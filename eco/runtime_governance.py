"""
eco/runtime_governance.py — 运行时治理：fail-closed 决策网关 + kill switch + 不可篡改审计

补的是 AIShield 最大的能力缺口：扫描是"事前"，这里是"事中"。
对齐 OWASP Agentic AI ASI08（失控自主性）/ ASI10（治理缺失）与 CoSAI 对
"fail-closed 执行网关 + 不可变日志"的要求。

三件事，缺一不可：
  1. 决策网关 evaluate()  —— 每次工具调用前问一句"允许吗"，未知实体默认拒绝。
  2. kill switch          —— 出事时一键切断某个 server/tool，立刻生效，无需重启。
  3. 哈希链审计日志       —— append-only，每条含 prev_hash，事后可证明没被改过。

设计原则（与扫描器同源）：
  - 绝不 spawn 被治理的进程，本模块只做决策与记录。
  - 零第三方依赖、可完全离线运行、不外发任何数据。
  - fail-closed：策略损坏、实体未知、熔断触发 —— 一律 deny，不是 allow。
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_BASE, "api", "data")
POLICY_FILE = os.path.join(_DATA, "governance.json")
AUDIT_LOG = os.path.join(_DATA, "governance_audit.jsonl")

_lock = threading.RLock()

GENESIS_HASH = "0" * 64

# 连续高危事件达到此阈值自动熔断（kill）该 server
DEFAULT_INCIDENT_THRESHOLD = 3

DECISION_ALLOW = "allow"
DECISION_DENY = "deny"


def _now_iso():
    return datetime.now(TZ).isoformat()


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _default_policy():
    return {
        # default_deny=True → 未在 allowlist 中的实体一律拒绝（fail-closed 的核心开关）
        "default_deny": False,
        "killed": {},        # server -> {reason, killed_at}
        "allow": {},         # server -> {"tools": [...] | "*"}
        "deny": {},          # server -> {"tools": [...] | "*"}
        "incidents": {},     # server -> {"count": n, "last": iso, "events": [...]}
        "incident_threshold": DEFAULT_INCIDENT_THRESHOLD,
        "updated_at": _now_iso(),
    }


def _load_policy():
    """读策略。文件损坏时返回 fail-closed 策略（default_deny=True），绝不放行。"""
    if not os.path.exists(POLICY_FILE):
        return _default_policy(), True
    try:
        with open(POLICY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("policy root must be an object")
        base = _default_policy()
        base.update(data)
        return base, True
    except Exception:
        # 关键：策略读不出来时收紧而不是放开
        broken = _default_policy()
        broken["default_deny"] = True
        broken["_load_error"] = True
        return broken, False


def _save_policy(policy):
    os.makedirs(os.path.dirname(POLICY_FILE), exist_ok=True)
    policy["updated_at"] = _now_iso()
    tmp = POLICY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(policy, f, ensure_ascii=False, indent=2)
    os.replace(tmp, POLICY_FILE)


# ══════════════════════════════════════════
#  哈希链审计日志（append-only）
# ══════════════════════════════════════════

def _last_entry():
    """读日志末条。空日志返回 None。"""
    if not os.path.exists(AUDIT_LOG):
        return None
    last = None
    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last = line
    except Exception:
        return None
    if not last:
        return None
    try:
        return json.loads(last)
    except Exception:
        return None


def _entry_digest(entry):
    """对条目做规范化摘要——排除 hash 自身，键排序保证可复现。"""
    payload = {k: v for k, v in entry.items() if k != "hash"}
    return _sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def audit(event, detail=None):
    """追加一条审计记录，返回落盘后的条目（含 seq / prev_hash / hash）。"""
    with _lock:
        prev = _last_entry()
        seq = (prev.get("seq", 0) + 1) if prev else 1
        prev_hash = prev.get("hash", GENESIS_HASH) if prev else GENESIS_HASH
        entry = {
            "seq": seq,
            "ts": _now_iso(),
            "event": event,
            "detail": detail or {},
            "prev_hash": prev_hash,
        }
        entry["hash"] = _entry_digest(entry)
        os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry


def read_audit(limit=100, event=None):
    """按时间倒序读审计日志。"""
    if not os.path.exists(AUDIT_LOG):
        return []
    rows = []
    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    if event:
        rows = [r for r in rows if r.get("event") == event]
    rows.reverse()
    return rows[:limit]


def verify_chain():
    """校验整条哈希链。任何一条被改写/删除/插入都会被定位到。"""
    if not os.path.exists(AUDIT_LOG):
        return {"valid": True, "entries": 0, "note": "审计日志为空"}
    prev_hash = GENESIS_HASH
    expected_seq = 1
    count = 0
    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    return {"valid": False, "entries": count, "broken_at": lineno,
                            "reason": "JSON 解析失败"}
                count += 1
                if entry.get("seq") != expected_seq:
                    return {"valid": False, "entries": count, "broken_at": lineno,
                            "reason": f"序号断裂：期望 {expected_seq}，实际 {entry.get('seq')}"}
                if entry.get("prev_hash") != prev_hash:
                    return {"valid": False, "entries": count, "broken_at": lineno,
                            "reason": "prev_hash 不匹配（前序条目被篡改或删除）"}
                if _entry_digest(entry) != entry.get("hash"):
                    return {"valid": False, "entries": count, "broken_at": lineno,
                            "reason": "本条内容被篡改（hash 不符）"}
                prev_hash = entry["hash"]
                expected_seq += 1
    except Exception as exc:
        return {"valid": False, "entries": count, "reason": f"读取失败: {exc}"}
    return {"valid": True, "entries": count, "head_hash": prev_hash}


# ══════════════════════════════════════════
#  决策网关
# ══════════════════════════════════════════

def _matches(entry, tool):
    """entry 可以是 "*"、列表或 {"tools": [...]}。"""
    if entry in ("*", True):
        return True
    if isinstance(entry, dict):
        entry = entry.get("tools", [])
    if isinstance(entry, str):
        return entry == "*" or entry == tool
    if isinstance(entry, (list, tuple, set)):
        return "*" in entry or tool in entry
    return False


class RuntimeGovernor:
    """运行时治理网关。evaluate() 是唯一的准入判定入口。"""

    def evaluate(self, server, tool="", context=None, log=True):
        """判定一次工具调用是否放行。

        优先级（从高到低，任何一层命中即终止）：
            kill switch > deny 名单 > allow 名单 > default_deny 兜底
        """
        server = (server or "").strip()
        tool = (tool or "").strip()
        policy, ok = _load_policy()

        def _result(decision, reason, policy_hit):
            res = {"decision": decision, "allowed": decision == DECISION_ALLOW,
                   "server": server, "tool": tool, "reason": reason,
                   "policy_hit": policy_hit, "ts": _now_iso()}
            if not ok:
                res["policy_load_error"] = True
            if log:
                audit("decision", {"server": server, "tool": tool,
                                   "decision": decision, "reason": reason,
                                   "policy_hit": policy_hit,
                                   "context": (context or {})})
            return res

        if not server:
            return _result(DECISION_DENY, "server 标识缺失", "invalid_request")

        # 1) kill switch —— 最高优先级，立刻切断
        killed = policy.get("killed", {})
        if server in killed:
            return _result(DECISION_DENY,
                           f"该 server 已被熔断: {killed[server].get('reason', '未说明')}",
                           "kill_switch")

        # 2) 显式 deny
        deny = policy.get("deny", {})
        if server in deny and _matches(deny[server], tool):
            return _result(DECISION_DENY, "命中显式拒绝规则", "deny_list")

        # 3) 显式 allow
        allow = policy.get("allow", {})
        if server in allow and _matches(allow[server], tool):
            return _result(DECISION_ALLOW, "命中放行规则", "allow_list")

        # 4) 兜底：fail-closed 模式下未知实体一律拒绝
        if policy.get("default_deny"):
            return _result(DECISION_DENY, "未在放行名单内（fail-closed 默认拒绝）", "default_deny")
        return _result(DECISION_ALLOW, "默认放行（未开启 fail-closed）", "default_allow")

    # ── kill switch ──
    def kill(self, server, reason="manual kill switch"):
        server = (server or "").strip()
        if not server:
            return {"success": False, "error": "server 标识不能为空"}
        with _lock:
            policy, _ = _load_policy()
            policy.setdefault("killed", {})[server] = {
                "reason": reason, "killed_at": _now_iso()}
            _save_policy(policy)
        entry = audit("kill", {"server": server, "reason": reason})
        return {"success": True, "server": server, "reason": reason,
                "killed_at": entry["ts"], "audit_seq": entry["seq"]}

    def revive(self, server, reason="manual revive"):
        server = (server or "").strip()
        with _lock:
            policy, _ = _load_policy()
            if server not in policy.get("killed", {}):
                return {"success": False, "error": "该 server 未被熔断", "server": server}
            policy["killed"].pop(server, None)
            # 复活时清空事故计数，否则下一次事故立刻又被熔断
            policy.get("incidents", {}).pop(server, None)
            _save_policy(policy)
        entry = audit("revive", {"server": server, "reason": reason})
        return {"success": True, "server": server, "revived_at": entry["ts"],
                "audit_seq": entry["seq"]}

    def is_killed(self, server):
        policy, _ = _load_policy()
        return (server or "").strip() in policy.get("killed", {})

    # ── 策略管理 ──
    def set_default_deny(self, enabled):
        with _lock:
            policy, _ = _load_policy()
            policy["default_deny"] = bool(enabled)
            _save_policy(policy)
        audit("policy_change", {"default_deny": bool(enabled)})
        return {"success": True, "default_deny": bool(enabled)}

    def allow_tool(self, server, tools="*"):
        return self._set_list("allow", server, tools)

    def deny_tool(self, server, tools="*"):
        return self._set_list("deny", server, tools)

    def _set_list(self, bucket, server, tools):
        server = (server or "").strip()
        if not server:
            return {"success": False, "error": "server 标识不能为空"}
        if isinstance(tools, str):
            tools = [tools]
        with _lock:
            policy, _ = _load_policy()
            existing = policy.setdefault(bucket, {}).get(server)
            merged = set()
            if isinstance(existing, dict):
                merged |= set(existing.get("tools", []))
            elif isinstance(existing, (list, tuple, set)):
                merged |= set(existing)
            elif isinstance(existing, str):
                merged.add(existing)
            merged |= set(tools)
            policy[bucket][server] = {"tools": sorted(merged), "updated_at": _now_iso()}
            _save_policy(policy)
        audit("policy_change", {"bucket": bucket, "server": server, "tools": sorted(set(tools))})
        return {"success": True, "bucket": bucket, "server": server,
                "tools": policy[bucket][server]["tools"]}

    def clear_rule(self, bucket, server):
        if bucket not in ("allow", "deny"):
            return {"success": False, "error": "bucket 只能是 allow 或 deny"}
        with _lock:
            policy, _ = _load_policy()
            removed = policy.get(bucket, {}).pop((server or "").strip(), None)
            _save_policy(policy)
        audit("policy_change", {"bucket": bucket, "server": server, "cleared": bool(removed)})
        return {"success": True, "cleared": bool(removed), "bucket": bucket, "server": server}

    # ── 事故与自动熔断 ──
    def record_incident(self, server, severity="high", detail=None):
        """记录一次运行时事故。累计达阈值自动 kill（ASI08 失控自主性的刹车）。"""
        server = (server or "").strip()
        if not server:
            return {"success": False, "error": "server 标识不能为空"}
        with _lock:
            policy, _ = _load_policy()
            threshold = int(policy.get("incident_threshold", DEFAULT_INCIDENT_THRESHOLD))
            rec = policy.setdefault("incidents", {}).setdefault(
                server, {"count": 0, "events": []})
            # 只有 high/critical 计入熔断计数，低危不至于误伤
            counts = severity in ("high", "critical")
            if counts:
                rec["count"] = int(rec.get("count", 0)) + 1
            rec["last"] = _now_iso()
            rec.setdefault("events", []).append(
                {"ts": _now_iso(), "severity": severity, "detail": detail or {}})
            rec["events"] = rec["events"][-20:]     # 只留最近 20 条，避免无限膨胀
            auto_killed = False
            if counts and rec["count"] >= threshold and server not in policy.get("killed", {}):
                policy.setdefault("killed", {})[server] = {
                    "reason": f"自动熔断：连续 {rec['count']} 次 {severity} 事故",
                    "killed_at": _now_iso(), "auto": True}
                auto_killed = True
            _save_policy(policy)
        audit("incident", {"server": server, "severity": severity,
                           "count": rec["count"], "auto_killed": auto_killed,
                           "detail": detail or {}})
        if auto_killed:
            audit("kill", {"server": server, "reason": "auto: incident threshold reached",
                           "auto": True})
        return {"success": True, "server": server, "count": rec["count"],
                "threshold": threshold, "auto_killed": auto_killed}

    def status(self):
        policy, ok = _load_policy()
        chain = verify_chain()
        return {
            "default_deny": policy.get("default_deny", False),
            "killed": policy.get("killed", {}),
            "killed_count": len(policy.get("killed", {})),
            "allow_rules": len(policy.get("allow", {})),
            "deny_rules": len(policy.get("deny", {})),
            "incident_threshold": policy.get("incident_threshold", DEFAULT_INCIDENT_THRESHOLD),
            "incidents": {k: v.get("count", 0) for k, v in policy.get("incidents", {}).items()},
            "policy_healthy": ok,
            "audit_chain": chain,
            "updated_at": policy.get("updated_at"),
        }


# ── 模块级便捷 API ──
_default = RuntimeGovernor()


def evaluate(server, tool="", context=None, log=True):
    return _default.evaluate(server, tool, context, log)


def kill(server, reason="manual kill switch"):
    return _default.kill(server, reason)


def revive(server, reason="manual revive"):
    return _default.revive(server, reason)


def is_killed(server):
    return _default.is_killed(server)


def record_incident(server, severity="high", detail=None):
    return _default.record_incident(server, severity, detail)


def allow_tool(server, tools="*"):
    return _default.allow_tool(server, tools)


def deny_tool(server, tools="*"):
    return _default.deny_tool(server, tools)


def set_default_deny(enabled):
    return _default.set_default_deny(enabled)


def status():
    return _default.status()


if __name__ == "__main__":
    g = RuntimeGovernor()
    print("初始:", g.evaluate("demo-server", "read_file")["decision"])
    g.deny_tool("demo-server", ["exec_shell"])
    print("拒绝规则:", g.evaluate("demo-server", "exec_shell")["reason"])
    for i in range(3):
        r = g.record_incident("demo-server", "high", {"finding": f"prompt injection #{i+1}"})
    print("自动熔断:", r["auto_killed"])
    print("熔断后:", g.evaluate("demo-server", "read_file")["reason"])
    print("复活:", g.revive("demo-server")["success"])
    print("链校验:", verify_chain())
