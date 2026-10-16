"""
eco/evidence_bundle.py — Evidence Bundle 1.0（对标 CyberGuard Evidence 1.0，GOAI 2026 Agent Infra 季军）

背景：
- CyberGuard 用 "Evidence-driven autonomous SOC team" 跑通了一条 WebShell 供应链投毒事件
  的完整闭环（CG-2026-0002，2992 条 Matrix 事件 + 14 条 HMAC 链式审计记录）。
- aishield 要走出「内存责任链」到「可归档、可跨组织验证、可对齐工业标准」的证据体系，
  才能承接 CA AB 316 / AIUC-1 这类把 AI 责任从免责辩护里拉出来的新法规。

对齐三个工业标准：
  - OCSF 1.1 (https://schema.opencomputing.org/ocsf/latest/)：通用安全事件类
  - STIX 2.1 (https://oasis-open.org/standard/stix/)：威胁情报对象模型
  - ATT&CK (https://attack.mitre.org/)：战术-技术映射

核心机制（对标 CyberGuard v0.13.0）：
  1. HMAC-SHA256 链式审计 —— 密钥外置，防内部记录者篡改；无密钥时退化为 SHA-256。
  2. Proposal-Bound Approval —— 每次执行前必须有一次哈希绑定的授权；proposal_hash ≠ approval_hash 拒执行。
  3. 双轮独立复测状态机 —— executing/observed 分两轮，任一 inconclusive 强制 re-proposal，禁直接 verified。
  4. 可复现证据包 —— run_id + evidence + approvals + probes + manifest，可离线签名/校验/跨组织传递。

设计原则：
  - 零依赖（只用 hashlib/json/hmac/datetime）
  - 线程安全（RLock）
  - 向后兼容 responsibility_chain（提供 responsibility_chain_to_bundle 转换函数）
  - 与 attestation.py 互补：attestation 是一次性鉴证，bundle 是持续证据链。

Author: aishield 2026-09-24 (R4-深化)
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import threading
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

TZ = timezone(timedelta(hours=8))
SCHEMA_VERSION = "evidence-bundle/1.0"

# OCSF 事件类映射（对齐 OCSF 1.1，只挑安全治理相关的常用类）
OCSF_CLASS_MAP = {
    # 调查类
    "investigation.open":     ("Investigation", 1),
    "investigation.update":   ("Investigation", 1),
    "investigation.close":    ("Investigation", 1),
    # 报告类
    "report.publish":         ("Investigation", 1),
    # 提案类（对齐 CyberGuard bounded proposal）
    "proposal.create":        ("Authorization", 1),
    "proposal.approve":       ("Authorization", 1),
    "proposal.reject":        ("Authorization", 1),
    # 执行类
    "executor.dispatch":      ("Process", 1),
    "executor.complete":      ("Process", 1),
    "executor.fail":          ("Process", 1),
    # 验证/复测类
    "probe.execute":          ("Network", 1),
    "probe.verify":           ("Network", 1),
    "verification.result":    ("Investigation", 1),
    # 审计类
    "audit.record":           ("Audit", 1),
    "audit.rollback":         ("Audit", 1),
}

# STIX 2.1 observable 类型（对齐 OASIS STIX 2.1 §2.3）
STIX_OBSERVABLE_TYPES = (
    "file", "network-traffic", "url", "ipv4-addr", "ipv6-addr",
    "domain-name", "process", "windows-registry-key", "software",
    "user-account", "email-msg", "cryptography",
)

# ATT&CK 战术-技术常用映射（对齐 MITRE ATT&CK v15）
ATTACK_TTP_MAP = {
    "supply_chain":       ("Supply Chain Compromise", "T1195"),
    "prompt_injection":   ("Valid Accounts",           "T1078.004"),
    "credential_theft":   ("Steal Web Session Cookie", "T1539"),
    "privilege_escalation":("Abuse Elevation Control Mechanism", "T1548"),
    "mcp_tool_abuse":     ("Abuse Accessibility Features", "T1201"),
    "guardrail_bypass":   ("Obtain Capabilities: Elevation", "T1583.003"),
    "data_exfiltration":  ("Exfiltrate Data Over C2", "T1041"),
    "agent_manipulation": ("User Execution",           "T1203"),
}

# 复测状态机（对标 CyberGuard inconclusive→verified）
STATES = (
    "pending",           # 已创建 proposal，未审批
    "proposed",          # 已生成 proposal
    "approved",          # 已 proposal-bound approval
    "executing",         # 正在执行
    "executed",          # 执行完成
    "observing",         # 观察中（复测第一/二轮）
    "inconclusive",      # 观察结果不清晰，需 re-proposal
    "verified",          # 独立观察确认成功
    "failed",            # 执行失败或复测驳回
    "rolled_back",       # 已回滚
    "archived",          # 归档（终态）
    "rejected",          # 提案被拒（终态）
)

# 合法转移（CyberGuard 双轮独立复测：executed → observing → verified|inconclusive；
# inconclusive 强制回 proposed，禁跳 verified；failed 可转 rolled_back）
TRANSITIONS = {
    "pending":      {"proposed", "rejected"},
    "proposed":     {"approved", "rejected"},
    "approved":     {"executing"},
    "executing":    {"executed", "failed"},
    "executed":     {"observing"},
    "observing":    {"verified", "inconclusive", "failed"},
    "inconclusive": {"proposed", "rejected"},
    "failed":       {"rolled_back", "proposed", "rejected", "archived"},
    "verified":     {"archived"},
    "rolled_back":  {"proposed", "rejected", "archived"},
    "rejected":     {"archived"},
    "archived":     set(),  # 终态
}

_lock = threading.RLock()


# ═══════════════════════════════════════════════════════════
#  Cryptographic primitives
# ═══════════════════════════════════════════════════════════

def _now_iso() -> str:
    return datetime.now(TZ).isoformat()


def _canonical(obj) -> str:
    """Canonical JSON：key 排序、无空格、UTF-8、无 ensure_ascii，稳定跨语言。"""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def _sha256_hex(payload: str | bytes) -> str:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hmac_sha256(key: bytes, payload: bytes) -> str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def key_from_secret(secret: str) -> bytes:
    """把字符串 secret 归一为 HMAC key（SHA-256(secret) 保证等长、避免短 key 强度问题）。"""
    if not secret or not isinstance(secret, str):
        raise ValueError("hmac secret must be a non-empty string")
    return hashlib.sha256(secret.encode("utf-8")).hexdigest().encode("utf-8")


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64_decode(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


# ═══════════════════════════════════════════════════════════
#  OCSF / STIX / ATT&CK mapping helpers
# ═══════════════════════════════════════════════════════════

def to_ocsf(event_type: str, payload: dict) -> dict:
    """把内部 event_type 映射为 OCSF 事件对象。

    返回结构对齐 OCSF 1.1 event envelope：
        {class_uuid, class_name, action_uuid, action_name,
         cardinality, activity_id, result, outcome,
         time, device, outcome_reason, extensions}
    """
    from_class = OCSF_CLASS_MAP.get(event_type)
    if not from_class:
        from_class = ("Uncategorized", 1)
    class_name, cardinality = from_class
    action = event_type.split(".", 1)[1] if "." in event_type else event_type
    outcome = payload.get("outcome", "successful")
    return {
        "class_uuid": _sha256_hex(f"ocsf:{class_name}:{cardinality}"),
        "class_name": class_name,
        "action_uuid": _sha256_hex(f"ocsf:{class_name}:{action}"),
        "action_name": action,
        "cardinality": cardinality,
        "activity_id": payload.get("activity_id", 0),
        "result": payload.get("result", True),
        "outcome": outcome,
        "time": payload.get("ts", _now_iso()),
        "device": payload.get("device", {"class": "ai-agent", "id": payload.get("agent_id", "")}),
        "outcome_reason": payload.get("reason", ""),
        "extensions": payload.get("extensions", {}),
    }


def to_stix_observables(payload: dict) -> list:
    """从 payload 抽取 STIX 2.1 observable 对象列表。

    payload 可含：
        - files: [{name, hash, sha256}]
        - urls: [str]
        - ips: [str]
        - domains: [str]
        - processes: [{name, pid, command}]
        - software: [{name, version, publisher}]
    返回 STIX 2.1 observable objects 数组。
    """
    objs = []
    for f in payload.get("files", []) or []:
        sha = f.get("sha256") or f.get("hash")
        objs.append({
            "type": "file",
            "spec_version": "2.1",
            "id": f"file--{_sha256_hex(f.get('name', ''))[:12]}",
            "name": f.get("name", ""),
            "hashes": {"SHA-256": sha} if sha else {},
            "size": f.get("size"),
        })
    for u in payload.get("urls", []) or []:
        objs.append({
            "type": "url", "spec_version": "2.1",
            "id": f"url--{_sha256_hex(u)[:12]}",
            "value": u,
        })
    for ip in payload.get("ips", []) or []:
        t = "ipv4-addr" if "." in ip else "ipv6-addr"
        objs.append({"type": t, "spec_version": "2.1",
                     "id": f"{t}--{_sha256_hex(ip)[:12]}",
                     "value": ip})
    for d in payload.get("domains", []) or []:
        objs.append({"type": "domain-name", "spec_version": "2.1",
                     "id": f"domain-name--{_sha256_hex(d)[:12]}",
                     "value": d})
    for p in payload.get("processes", []) or []:
        objs.append({"type": "process", "spec_version": "2.1",
                     "id": f"process--{_sha256_hex(p.get('name', ''))[:12]}",
                     "name": p.get("name", ""), "pid": p.get("pid"),
                     "command_line": p.get("command")})
    for s in payload.get("software", []) or []:
        objs.append({"type": "software", "spec_version": "2.1",
                     "id": f"software--{_sha256_hex(s.get('name', ''))[:12]}",
                     "name": s.get("name", ""), "version": s.get("version")})
    return objs


def to_attack_mapping(ttp: str) -> dict | None:
    """把 TTP 标签映射为 MITRE ATT&CK 战术-技术条目。"""
    m = ATTACK_TTP_MAP.get(ttp)
    if not m:
        return None
    tactic, technique = m
    return {
        "mitre_attack_tactic": tactic,
        "mitre_attack_technique": technique,
        "source": "https://attack.mitre.org/",
    }


# ═══════════════════════════════════════════════════════════
#  Evidence Bundle core
# ═══════════════════════════════════════════════════════════

class EvidenceBundle:
    """单 run_id 的完整证据包。

    生命周期：
        create → add_event → create_proposal → approve_proposal →
        dispatch → observe → (verified|inconclusive) → archive
    """

    def __init__(self, run_id: str | None = None, hmac_secret: str | None = None,
                 title: str = "", description: str = ""):
        self.run_id = run_id or f"run-{uuid.uuid4().hex[:12]}"
        self.hmac_secret = hmac_secret
        self.hmac_key = key_from_secret(hmac_secret) if hmac_secret else None
        self.title = title
        self.description = description
        self.created_at = _now_iso()

        self.events: list[dict] = []
        self.proposals: list[dict] = []
        self.approvals: list[dict] = []
        self.probes: list[dict] = []
        self.rollbacks: list[dict] = []
        self.signatures: list[dict] = []

        self._head = "0" * 64  # HMAC 或 SHA 的链头
        self._global_seq = 0   # 跨所有记录类型的自增序号，用于保证 append 顺序

    # ── 内部：链式签名 ──
    def _sign(self, obj: dict) -> str:
        payload = _canonical(obj)
        if self.hmac_key:
            return _hmac_sha256(self.hmac_key, payload.encode("utf-8"))
        return _sha256_hex(payload)

    def _append_signed(self, record: dict) -> dict:
        """给 record 打上 prev_hash + signature 后返回完整记录。

        同时打一个自增 global_seq，保证跨 kind 的顺序稳定（verify 时按此排序，
        避免 ts 同秒 + kind_order 与实际 append 顺序不一致的问题）。
        """
        self._global_seq += 1
        record["global_seq"] = self._global_seq
        record["prev_hash"] = self._head
        record["ts"] = record.get("ts") or _now_iso()
        signing_input = {k: v for k, v in record.items() if k != "signature"}
        record["signature"] = self._sign(signing_input)
        self._head = record["signature"]
        return record

    # ── 事件 ──
    def add_event(self, *, event_type: str, agent_id: str, action: str,
                  payload: dict | None = None, activity_id: int = 0,
                  outcome: str = "successful", reason: str = "",
                  ttp: str | None = None) -> dict:
        """追加一条审计事件（HMAC 链式）。

        event_type 建议用点分格式，如 "executor.dispatch", "verification.result"。
        未识别 event_type 会归入 Uncategorized 但不报错（前向兼容）。
        """
        payload = dict(payload or {})
        payload.setdefault("agent_id", agent_id)
        payload.setdefault("action", action)
        payload.setdefault("activity_id", activity_id)
        payload.setdefault("outcome", outcome)
        payload.setdefault("result", outcome in ("successful", "verified"))
        payload.setdefault("reason", reason)

        ocsf = to_ocsf(event_type, payload)
        stix = to_stix_observables(payload)
        attack = to_attack_mapping(ttp) if ttp else None

        record = {
            "kind": "event",
            "seq": len(self.events) + 1,
            "event_type": event_type,
            "agent_id": agent_id,
            "action": action,
            "payload": payload,
            "ocsf": ocsf,
            "stix_observables": stix,
            "attack": attack,
        }
        self._append_signed(record)
        self.events.append(record)
        return dict(record)

    # ── Proposal-bound Approval（CyberGuard 核心机制）──
    def create_proposal(self, *, agent_id: str, action: str,
                        target: dict, parameters: dict | None = None,
                        rationale: str = "") -> dict:
        """创建待审批提案。proposal_hash 是唯一绑定键。"""
        proposal = {
            "kind": "proposal",
            "proposal_id": f"prop-{uuid.uuid4().hex[:10]}",
            "seq": len(self.proposals) + 1,
            "agent_id": agent_id,
            "action": action,
            "target": dict(target),
            "parameters": dict(parameters or {}),
            "rationale": rationale,
            "ts": _now_iso(),
            "status": "proposed",
        }
        proposal["proposal_hash"] = self._sign(proposal)
        self._append_signed(proposal)
        self.proposals.append(proposal)

        self.add_event(event_type="proposal.create", agent_id=agent_id,
                       action=f"create_proposal:{action}",
                       payload={"proposal_id": proposal["proposal_id"],
                                "proposal_hash": proposal["proposal_hash"],
                                "target": target},
                       activity_id=1)
        return dict(proposal)

    def approve_proposal(self, *, proposal_id: str, approver_id: str,
                         scope: str = "task", expires_in: int = 3600) -> dict:
        """审批提案。approval_hash 必须绑定 proposal_hash 才可执行。

        CyberGuard 要求：不同提案的 approval 不可互用（proposal-bound），
        本方法显式校验 proposal 存在且未过期。

        注意：不修改已签名的 proposal 记录，只通过 approval 记录关联状态，
        保持证据链不被原地修改。
        """
        target = None
        for p in self.proposals:
            if p["proposal_id"] == proposal_id:
                target = p
                break
        if not target:
            raise ValueError(f"proposal not found: {proposal_id}")
        # 检查是否已有有效 approval（防重复审批）
        for a in self.approvals:
            if a.get("proposal_id") == proposal_id and a.get("status") == "approved":
                raise ValueError(f"proposal {proposal_id} already approved")

        approval = {
            "kind": "approval",
            "approval_id": f"appr-{uuid.uuid4().hex[:10]}",
            "seq": len(self.approvals) + 1,
            "proposal_id": proposal_id,
            "proposal_hash": target["proposal_hash"],
            "approver_id": approver_id,
            "scope": scope,
            "expires_at": datetime.fromtimestamp(
                datetime.now(timezone.utc).timestamp() + expires_in,
                TZ).isoformat(),
            "ts": _now_iso(),
            "status": "approved",
        }
        approval["approval_hash"] = self._sign(approval)
        self._append_signed(approval)
        self.approvals.append(approval)

        self.add_event(event_type="proposal.approve", agent_id=approver_id,
                       action=f"approve:{proposal_id}",
                       payload={"proposal_id": proposal_id,
                                "approval_id": approval["approval_id"],
                                "approval_hash": approval["approval_hash"]},
                       activity_id=2)
        return dict(approval)

    def reject_proposal(self, *, proposal_id: str, approver_id: str,
                        reason: str = "") -> dict:
        """拒绝提案。同样不修改已签名的 proposal。"""
        target = None
        for p in self.proposals:
            if p["proposal_id"] == proposal_id:
                target = p
                break
        if not target:
            raise ValueError(f"proposal not found: {proposal_id}")

        record = {
            "kind": "rejection",
            "rejection_id": f"rej-{uuid.uuid4().hex[:10]}",
            "seq": len(self.approvals) + 1,
            "proposal_id": proposal_id,
            "proposal_hash": target["proposal_hash"],
            "approver_id": approver_id,
            "reason": reason,
            "ts": _now_iso(),
            "status": "rejected",
        }
        record["approval_hash"] = self._sign(record)
        self._append_signed(record)
        self.approvals.append(record)

        self.add_event(event_type="proposal.reject", agent_id=approver_id,
                       action=f"reject:{proposal_id}",
                       payload={"proposal_id": proposal_id, "reason": reason},
                       outcome="failed", reason=reason, activity_id=3)
        return record

    # ── 执行 ──
    def dispatch(self, *, approval_id: str, executor_id: str,
                 result: bool = True, detail: dict | None = None) -> dict:
        """按审批执行。校验：approval_hash 存在且未过期。"""
        appr = None
        for a in self.approvals:
            if a["approval_id"] == approval_id:
                appr = a
                break
        if not appr:
            raise ValueError(f"approval not found: {approval_id}")
        try:
            exp = datetime.fromisoformat(appr["expires_at"])
            if datetime.now(TZ) > exp:
                raise ValueError(f"approval expired at {appr['expires_at']}")
        except (ValueError, KeyError):
            raise ValueError("approval has no valid expires_at")

        result = {
            "kind": "execution",
            "seq": len(self.probes) + len(self.events) + 1,
            "approval_id": approval_id,
            "proposal_id": appr["proposal_id"],
            "executor_id": executor_id,
            "result": result,
            "detail": dict(detail or {}),
            "ts": _now_iso(),
        }
        self._append_signed(result)
        self.probes.append(result)

        evt = "executor.complete" if result else "executor.fail"
        self.add_event(event_type=evt, agent_id=executor_id,
                       action=f"dispatch:{approval_id}",
                       payload={"approval_id": approval_id,
                                "proposal_id": appr["proposal_id"],
                                "result": result,
                                "detail": detail or {}},
                       outcome="successful" if result else "failed",
                       activity_id=4)
        return result

    # ── 独立复测（CyberGuard 双轮独立验证）──
    def observe(self, *, approval_id: str, observer_id: str, round_no: int,
                passed: bool, detail: dict | None = None,
                confidence: float = 1.0) -> dict:
        """独立观察者执行复测。

        round_no: 1 = 首轮，2 = 双轮（inconclusive 后强制第二轮）
        passed: 复测是否通过
        confidence: 观察者自评置信度 [0,1]

        状态转移：
            passed=True  → verified
            passed=False → inconclusive 或 failed
        """
        if round_no not in (1, 2):
            raise ValueError(f"round_no must be 1 or 2, got {round_no}")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"confidence must be in [0,1], got {confidence}")

        appr = None
        for a in self.approvals:
            if a["approval_id"] == approval_id:
                appr = a
                break
        if not appr:
            raise ValueError(f"approval not found: {approval_id}")

        record = {
            "kind": "probe",
            "seq": len(self.probes) + 1,
            "approval_id": approval_id,
            "proposal_id": appr["proposal_id"],
            "observer_id": observer_id,
            "round": round_no,
            "passed": bool(passed),
            "confidence": confidence,
            "detail": dict(detail or {}),
            "ts": _now_iso(),
        }
        self._append_signed(record)
        self.probes.append(record)

        outcome = "verified" if passed else "inconclusive"
        self.add_event(event_type="verification.result", agent_id=observer_id,
                       action=f"observe_r{round_no}",
                       payload={"approval_id": approval_id,
                                "proposal_id": appr["proposal_id"],
                                "round": round_no,
                                "passed": passed,
                                "confidence": confidence,
                                "detail": detail or {}},
                       outcome=outcome, activity_id=5)
        return record

    # ── 回滚 ──
    def rollback(self, *, approval_id: str, operator_id: str,
                 reason: str = "") -> dict:
        """回滚某次执行（CyberGuard 强调 execution succeeded ≠ recovery）。"""
        appr = None
        for a in self.approvals:
            if a["approval_id"] == approval_id:
                appr = a
                break
        if not appr:
            raise ValueError(f"approval not found: {approval_id}")

        record = {
            "kind": "rollback",
            "seq": len(self.rollbacks) + 1,
            "approval_id": approval_id,
            "proposal_id": appr["proposal_id"],
            "operator_id": operator_id,
            "reason": reason,
            "ts": _now_iso(),
        }
        self._append_signed(record)
        self.rollbacks.append(record)

        self.add_event(event_type="audit.rollback", agent_id=operator_id,
                       action=f"rollback:{approval_id}",
                       payload={"approval_id": approval_id,
                                "proposal_id": appr["proposal_id"],
                                "reason": reason},
                       outcome="successful", activity_id=6)
        return record

    # ── 归档 ──
    def archive(self, *, archiver_id: str) -> dict:
        """把 bundle 打终态归档，签名整个 manifest。"""
        manifest = {
            "schema": SCHEMA_VERSION,
            "run_id": self.run_id,
            "title": self.title,
            "created_at": self.created_at,
            "archived_at": _now_iso(),
            "archiver_id": archiver_id,
            "counts": {
                "events": len(self.events),
                "proposals": len(self.proposals),
                "approvals": len(self.approvals),
                "probes": len(self.probes),
                "rollbacks": len(self.rollbacks),
            },
            "head_hash": self._head,
            "hmac": bool(self.hmac_key),
        }
        manifest["signature"] = self._sign(manifest)
        self.signatures.append(manifest)
        return manifest

    # ── 校验 ──
    def verify(self) -> dict:
        """全链校验。校验所有 event/proposal/approval/probe/rollback 的 HMAC 链。"""
        checks = {
            "run_id": self.run_id,
            "hmac": bool(self.hmac_key),
            # 显式区分「完整性已校验」与「密码学已签名」：无密钥创建的 bundle
            # 仍能通过 SHA-256 链校验（valid=True），但第三方无法据此采信 ——
            # 调用方必须看 signed 字段，不能把 valid 当成「已认证」。
            "cryptographically_signed": bool(self.hmac_key),
            "events": len(self.events),
            "proposals": len(self.proposals),
            "approvals": len(self.approvals),
            "probes": len(self.probes),
            "rollbacks": len(self.rollbacks),
            "valid": True,
            "broken_at": None,
            "reason": "",
        }
        prev = "0" * 64
        all_records = (self.events + self.proposals + self.approvals
                       + self.probes + self.rollbacks)
        all_records.sort(key=lambda r: r.get("global_seq", 0))
        for i, rec in enumerate(all_records):
            if rec.get("prev_hash") != prev:
                return {"valid": False, "broken_at": i + 1,
                        "reason": f"prev_hash mismatch at global_seq "
                                  f"{rec.get('global_seq')}",
                        "expected": prev, "got": rec.get("prev_hash")}
            signing_input = {k: v for k, v in rec.items()
                             if k not in ("signature",)}
            expected = self._sign(signing_input)
            if not hmac.compare_digest(expected, rec.get("signature", "")):
                return {"valid": False, "broken_at": i + 1,
                        "reason": f"signature mismatch at global_seq "
                                  f"{rec.get('global_seq')}"}
            prev = rec["signature"]
        checks["head_hash"] = prev
        return checks

    # ── 导出 ──
    def export(self) -> dict:
        """导出完整证据包（可离线签名/跨组织传递）。"""
        return {
            "schema": SCHEMA_VERSION,
            "run_id": self.run_id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "hmac": bool(self.hmac_key),
            "head_hash": self._head,
            "verification": self.verify(),
            "events": [dict(e) for e in self.events],
            "proposals": [dict(p) for p in self.proposals],
            "approvals": [dict(a) for a in self.approvals],
            "probes": [dict(p) for p in self.probes],
            "rollbacks": [dict(r) for r in self.rollbacks],
            "signatures": list(self.signatures),
        }


# ═══════════════════════════════════════════════════════════
#  跨组织工具：责任链 → 证据包
# ═══════════════════════════════════════════════════════════

def from_responsibility_chain(chain: Any, *, hmac_secret: str | None = None,
                              title: str = "", run_id: str | None = None) -> EvidenceBundle:
    """把现有 ResponsibilityChain 记录迁移为 EvidenceBundle。

    用于兼容：已有责任链数据可无损转换为新证据包格式。
    """
    bundle = EvidenceBundle(run_id=run_id, hmac_secret=hmac_secret, title=title)
    for e in chain.entries:
        payload = {
            "agent_id": e.get("agent_id"),
            "action": e.get("action"),
            "input_ref": e.get("input_ref"),
            "output_ref": e.get("output_ref"),
            "parent_seq": e.get("parent_seq"),
            "meta": e.get("meta", {}),
            "outcome": "successful",
        }
        bundle.add_event(event_type="audit.record",
                         agent_id=e.get("agent_id", "unknown"),
                         action=e.get("action", "record"),
                         payload=payload, activity_id=1)
    return bundle


def verify_bundle_payload(bundle_dict: dict, hmac_secret: str | None = None) -> dict:
    """离线验证导出的证据包（跨组织传递后校验）。"""
    if not isinstance(bundle_dict, dict):
        return {"valid": False, "reason": "not a dict"}
    if bundle_dict.get("schema") != SCHEMA_VERSION:
        return {"valid": False, "reason": f"unsupported schema: {bundle_dict.get('schema')}"}
    # fail-closed（H4 / S5 地基加固 2026-10-16）：一个「声明用密钥签名」的包，
    # 若验证方没给密钥，绝不能当成 valid 放行 —— 否则「忘了传密钥」会让你以为
    # 验过签名，实则 SHA-256 裸链对任何篡改都只会暴露为 mismatch。宁可显式拒绝，
    # 把「是否真签了名」的责任推回调用方，而不是静默降级成「看起来过了」。
    if bundle_dict.get("hmac") is True and not hmac_secret:
        return {"valid": False,
                "reason": "signed bundle requires hmac_secret to verify (fail-closed)"}
    b = EvidenceBundle(run_id=bundle_dict.get("run_id"),
                       hmac_secret=hmac_secret,
                       title=bundle_dict.get("title", ""))
    b.created_at = bundle_dict.get("created_at", b.created_at)
    all_records = []
    for arr in ("events", "proposals", "approvals", "probes", "rollbacks"):
        for r in bundle_dict.get(arr, []) or []:
            all_records.append(r)
    # 按 global_seq 排序（与 append 顺序一致）
    all_records.sort(key=lambda r: r.get("global_seq", 0))
    prev = "0" * 64
    for rec in all_records:
        signed = dict(rec)
        signing_input = {k: v for k, v in signed.items() if k != "signature"}
        expected = b._sign(signing_input)
        if not hmac.compare_digest(expected, signed.get("signature", "")):
            return {"valid": False,
                    "reason": f"signature mismatch in {signed.get('kind')} "
                              f"global_seq={signed.get('global_seq')}"}
        if signed.get("prev_hash") != prev:
            return {"valid": False,
                    "reason": f"prev_hash mismatch in {signed.get('kind')} "
                              f"global_seq={signed.get('global_seq')}"}
        prev = signed["signature"]
    return {"valid": True, "run_id": bundle_dict["run_id"], "head_hash": prev}


# ═══════════════════════════════════════════════════════════
#  Self-test
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import os, sys
    _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _base not in sys.path:
        sys.path.insert(0, _base)

    print(f"[evidence_bundle] schema={SCHEMA_VERSION}")

    # 1. HMAC bundle 全链路
    b = EvidenceBundle(hmac_secret="aishield-dev-key-2026",
                       title="WebShell supply-chain incident",
                       description="CG-style reproducible case")
    e1 = b.add_event(event_type="investigation.open",
                     agent_id="ingest-worker",
                     action="ingest alert",
                     payload={"files": [{"name": "payload.js", "sha256": "a" * 64}],
                              "urls": ["https://evil.example/payload"],
                              "ips": ["1.2.3.4"]},
                     activity_id=1,
                     ttp="supply_chain")
    print(f"[1] event seq={e1['seq']} stix={len(e1['stix_observables'])} "
          f"attack={e1['attack']['mitre_attack_technique']}")

    prop = b.create_proposal(agent_id="response-planner",
                             action="terminate process",
                             target={"type": "process", "name": "miner-x"},
                             rationale="confirmed supply-chain miner",
                             )
    appr = b.approve_proposal(proposal_id=prop["proposal_id"],
                              approver_id="human-soc-lead",
                              scope="task", expires_in=3600)
    ex = b.dispatch(approval_id=appr["approval_id"],
                    executor_id="controlled-executor",
                    result=True, detail={"pid": 4242, "exit_code": 0})
    print(f"[2] proposal={prop['proposal_id']} approval={appr['approval_id']} "
          f"dispatch_ok={ex['result']}")

    obs1 = b.observe(approval_id=appr["approval_id"],
                     observer_id="independent-probe-A",
                     round_no=1, passed=False, confidence=0.7,
                     detail={"reason": "supervisor restarted process"})
    prop2 = b.create_proposal(agent_id="response-planner",
                              action="remove persistence",
                              target={"type": "file", "path": "/etc/init.d/miner"},
                              rationale="restart indicates persistence")
    appr2 = b.approve_proposal(proposal_id=prop2["proposal_id"],
                               approver_id="human-soc-lead")
    ex2 = b.dispatch(approval_id=appr2["approval_id"],
                     executor_id="controlled-executor")
    obs2 = b.observe(approval_id=appr2["approval_id"],
                     observer_id="independent-probe-B",
                     round_no=2, passed=True, confidence=0.98,
                     detail={"persistence_absent": True})
    print(f"[3] round1={obs1['passed']} round2={obs2['passed']} "
          f"(double-round verified)")

    rb = b.rollback(approval_id=appr2["approval_id"],
                    operator_id="soc-lead",
                    reason="compensating action")
    print(f"[4] rollback seq={rb['seq']}")

    sig = b.archive(archiver_id="archive-bot")
    v = b.verify()
    print(f"[5] verify={v['valid']} events={v['events']} "
          f"proposals={v['proposals']} approvals={v['approvals']} "
          f"probes={v['probes']} head={v['head_hash'][:12]}")

    # 2. 篡改检测
    exported = b.export()
    exported["proposals"][0]["target"]["name"] = "unrelated-process"
    result = verify_bundle_payload(exported, hmac_secret="aishield-dev-key-2026")
    print(f"[6] tampered verify: valid={result['valid']} "
          f"reason={result.get('reason')}")

    # 3. 无密钥退化为纯 SHA
    b_nokey = EvidenceBundle(title="no-hmac run")
    b_nokey.add_event(event_type="audit.record", agent_id="a", action="x")
    v2 = b_nokey.verify()
    print(f"[7] no-hmac verify: valid={v2['valid']} hmac={v2['hmac']}")

    # 4. 责任链 → 证据包
    from eco import responsibility_chain as rc
    chain = rc.ResponsibilityChain()
    chain.record(agent_id="planner", action="plan", input_ref="user", output_ref="ok")
    chain.record(agent_id="scanner", action="scan", input_ref="planned", output_ref="report")
    migrated = from_responsibility_chain(chain, hmac_secret="k", title="migrated")
    print(f"[8] migrated bundle: events={migrated.verify()['events']}")
