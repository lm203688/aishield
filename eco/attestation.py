"""
eco/attestation.py — 持续鉴证订阅（Continuous Attestation）

把"一次性认证"升级成"持续信任"。

为什么必须做：
    一次性认证的致命缺陷是 rug-pull——工具在拿到徽章后再改坏代码，徽章却还挂着。
    对手（Scribe / Codenotary）卖的正是"持续鉴证订阅"：SBOM + SDLC 治理 + 不可变存证。
    对 AIShield 而言这同时解决两件事：安全上堵住认证过期窗口，商业上把一次性收入
    变成 recurring。

机制：
    订阅 → 周期性自动复扫 → 分数达标自动续期 / 掉分自动降级或吊销 → 每次留哈希链存证。

状态机：
    active   订阅有效，按 attest_interval_days 持续复扫
    grace    订阅已到期，进入宽限期（默认 7 天），仍复扫但提示续费
    lapsed   宽限期结束仍未续费 → 停止复扫，关联认证不再被"持续"背书
    cancelled 用户主动取消

复扫结果对认证的影响（阈值与 badge.py 保持一致：70 分）：
    >= 70 且不低于原等级   → 续期，attestation=pass
    >= 70 但等级下降       → 续期但降级，attestation=downgraded
    <  70                  → 吊销认证，attestation=failed（这是 rug-pull 的兜底）

零第三方依赖；复扫函数可注入（scan_fn），便于离线测试与自定义扫描后端。
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_BASE, "api", "data")
ATTESTATIONS_FILE = os.path.join(_DATA, "attestations.json")

_lock = threading.RLock()

GENESIS_HASH = "0" * 64

# 认证分数门槛，与 eco/badge.py 的 certify_tool 保持一致
CERT_SCORE_THRESHOLD = 70

# 徽章等级排序，用于判断"是否降级"
_LEVEL_RANK = {"none": 0, "bronze": 1, "silver": 2, "gold": 3}

# 订阅套餐：周期天数 + 双轨定价
SUBSCRIPTION_PLANS = {
    "monthly":   {"days": 30,  "CNY": 29.0,  "USD": 4.0,  "label": "月度持续鉴证"},
    "quarterly": {"days": 90,  "CNY": 79.0,  "USD": 11.0, "label": "季度持续鉴证"},
    "annual":    {"days": 365, "CNY": 269.0, "USD": 38.0, "label": "年度持续鉴证"},
}

DEFAULT_ATTEST_INTERVAL_DAYS = 7   # 每 7 天复扫一次
DEFAULT_GRACE_DAYS = 7             # 到期后宽限 7 天

STATUS_ACTIVE = "active"
STATUS_GRACE = "grace"
STATUS_LAPSED = "lapsed"
STATUS_CANCELLED = "cancelled"


def _now():
    return datetime.now(TZ)


def _now_iso():
    return _now().isoformat()


def _parse_iso(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except Exception:
        return None
    return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load():
    if os.path.exists(ATTESTATIONS_FILE):
        try:
            with open(ATTESTATIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("subscriptions", {})
                return data
        except Exception:
            pass
    return {"subscriptions": {}}


def _save(data):
    os.makedirs(os.path.dirname(ATTESTATIONS_FILE), exist_ok=True)
    tmp = ATTESTATIONS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, ATTESTATIONS_FILE)


def _record_digest(record):
    payload = {k: v for k, v in record.items() if k != "hash"}
    return _sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _append_evidence(sub, result, score, badge_level, detail=None):
    """把一次鉴证结果追加到该订阅的证据链。"""
    chain = sub.setdefault("attestations", [])
    prev_hash = chain[-1]["hash"] if chain else GENESIS_HASH
    record = {
        "seq": len(chain) + 1,
        "ts": _now_iso(),
        "result": result,
        "score": score,
        "badge_level": badge_level,
        "detail": detail or {},
        "prev_hash": prev_hash,
    }
    record["hash"] = _record_digest(record)
    chain.append(record)
    sub["attestations"] = chain[-100:]     # 保留最近 100 次，防止无限膨胀
    return record


def verify_evidence_chain(sub):
    """校验单个订阅的证据链完整性。"""
    chain = (sub or {}).get("attestations", [])
    if not chain:
        return {"valid": True, "entries": 0}
    prev_hash = chain[0].get("prev_hash", GENESIS_HASH)
    # 允许因保留窗口裁剪而不从创世哈希起算，只校验链内连续性
    for idx, rec in enumerate(chain):
        if rec.get("prev_hash") != prev_hash:
            return {"valid": False, "entries": len(chain), "broken_at": idx + 1,
                    "reason": "prev_hash 不匹配"}
        if _record_digest(rec) != rec.get("hash"):
            return {"valid": False, "entries": len(chain), "broken_at": idx + 1,
                    "reason": "记录被篡改"}
        prev_hash = rec["hash"]
    return {"valid": True, "entries": len(chain), "head_hash": prev_hash}


def _effective_status(sub, now=None):
    """根据当前时间推导订阅状态（不落盘）。"""
    now = now or _now()
    if sub.get("status") == STATUS_CANCELLED:
        return STATUS_CANCELLED
    expires = _parse_iso(sub.get("expires_at"))
    if not expires:
        return STATUS_LAPSED
    if now <= expires:
        return STATUS_ACTIVE
    grace_days = int(sub.get("grace_days", DEFAULT_GRACE_DAYS))
    if now <= expires + timedelta(days=grace_days):
        return STATUS_GRACE
    return STATUS_LAPSED


def _live_report(preflight_report):
    """把 scanner.workspace_scan.preflight() 的输出映射成 attest_once 期望的报告形状。

    preflight 的 summary 已含 overall_score / risk_level，这里补全 total_findings
    与 badge_level，使 live agent 复扫与静态快照复扫走同一套分数→结论逻辑。
    """
    summary = (preflight_report or {}).get("summary", {}) or {}
    score = summary.get("overall_score") or 0
    items = (preflight_report or {}).get("items", []) or []
    total_findings = sum(int(it.get("total_findings", 0) or 0) for it in items)
    if not total_findings:
        total_findings = len((preflight_report or {}).get("aggregate_findings", []) or [])
    if score >= 90:
        badge_level = "gold"
    elif score >= 80:
        badge_level = "silver"
    elif score >= 70:
        badge_level = "bronze"
    else:
        badge_level = "none"
    return {
        "overall_score": score,
        "badge_level": badge_level,
        "total_findings": total_findings,
        "live": True,
        "items_total": summary.get("items_total", len(items)),
    }


class AttestationService:
    """持续鉴证订阅服务。"""

    # ── 订阅生命周期 ──
    def subscribe(self, source_url, plan="monthly", payer_id=None, cert_id=None,
                  attest_interval_days=DEFAULT_ATTEST_INTERVAL_DAYS,
                  workspace_path=None):
        """订阅持续鉴证。

        workspace_path（可选）：live agent 的工作区目录。若提供，每次复扫将直接
        对该目录跑 scanner.workspace_scan.preflight()（重新评估已加载的 MCP/skill
        配置），从而把"持续鉴证"接到真实运行的 agent 上——这正是 rug-pull 兜底
        的关键：agent 中途加装恶意 MCP，下次复扫即被捕获并吊销认证。
        不提供则回退为对 source_url 跑 scanner.engine.scan()（静态快照）。
        """
        if not source_url:
            return {"success": False, "error": "source_url is required"}
        if plan not in SUBSCRIPTION_PLANS:
            return {"success": False, "error": f"未知套餐: {plan}",
                    "available": list(SUBSCRIPTION_PLANS)}
        try:
            interval = int(attest_interval_days)
        except (TypeError, ValueError):
            return {"success": False, "error": "attest_interval_days 必须是整数"}
        if interval < 1:
            return {"success": False, "error": "复扫间隔至少 1 天"}

        spec = SUBSCRIPTION_PLANS[plan]
        with _lock:
            data = _load()
            # 同一 source_url 已有未取消订阅 → 不重复创建，引导走续费
            for sid, sub in data.get("subscriptions", {}).items():
                if sub.get("source_url") == source_url and sub.get("status") != STATUS_CANCELLED:
                    return {"success": False, "error": "该来源已有订阅，请续费而非重复订阅",
                            "subscription_id": sid, "existing": True}
            sub_id = f"sub_{uuid.uuid4().hex[:12]}"
            now = _now()
            sub = {
                "subscription_id": sub_id,
                "source_url": source_url,
                "workspace_path": workspace_path or "",
                "plan": plan,
                "plan_label": spec["label"],
                "payer_id": payer_id or "anonymous",
                "cert_id": cert_id or "",
                "status": STATUS_ACTIVE,
                "price_cny": spec["CNY"],
                "price_usd": spec["USD"],
                "attest_interval_days": interval,
                "grace_days": DEFAULT_GRACE_DAYS,
                "created_at": now.isoformat(),
                "started_at": now.isoformat(),
                "expires_at": (now + timedelta(days=spec["days"])).isoformat(),
                "next_attest_at": now.isoformat(),   # 立即可做首次鉴证
                "last_attest_at": "",
                "attestations": [],
                "renewals": 0,
            }
            data.setdefault("subscriptions", {})[sub_id] = sub
            _save(data)
        return {"success": True, "subscription_id": sub_id, "plan": plan,
                "status": STATUS_ACTIVE, "expires_at": sub["expires_at"],
                "price_cny": spec["CNY"], "price_usd": spec["USD"],
                "attest_interval_days": interval,
                "note": "订阅已创建；调用 run_cycle() 或等待定时任务执行首次持续鉴证。"}

    def renew_subscription(self, subscription_id, periods=1, plan=None):
        """续费。从当前到期日顺延（未过期不损失剩余时长），已 lapsed 则从现在起算。"""
        try:
            periods = int(periods)
        except (TypeError, ValueError):
            return {"success": False, "error": "periods 必须是整数"}
        if periods < 1:
            return {"success": False, "error": "periods 至少为 1"}
        with _lock:
            data = _load()
            sub = data.get("subscriptions", {}).get(subscription_id)
            if not sub:
                return {"success": False, "error": "订阅不存在", "subscription_id": subscription_id}
            if sub.get("status") == STATUS_CANCELLED:
                return {"success": False, "error": "订阅已取消，请重新订阅"}
            use_plan = plan or sub.get("plan")
            if use_plan not in SUBSCRIPTION_PLANS:
                return {"success": False, "error": f"未知套餐: {use_plan}"}
            spec = SUBSCRIPTION_PLANS[use_plan]
            now = _now()
            base = _parse_iso(sub.get("expires_at")) or now
            if base < now:
                base = now      # 已过期：从现在起算，不倒补
            new_expiry = base + timedelta(days=spec["days"] * periods)
            sub["plan"] = use_plan
            sub["plan_label"] = spec["label"]
            sub["price_cny"] = spec["CNY"]
            sub["price_usd"] = spec["USD"]
            sub["expires_at"] = new_expiry.isoformat()
            sub["status"] = STATUS_ACTIVE
            sub["renewals"] = int(sub.get("renewals", 0)) + periods
            sub["renewed_at"] = now.isoformat()
            _append_evidence(sub, "renewed", sub.get("last_score", 0),
                             sub.get("last_badge_level", "none"),
                             {"plan": use_plan, "periods": periods,
                              "expires_at": sub["expires_at"]})
            _save(data)
        return {"success": True, "subscription_id": subscription_id, "plan": use_plan,
                "status": STATUS_ACTIVE, "expires_at": sub["expires_at"],
                "renewals": sub["renewals"],
                "amount_cny": round(spec["CNY"] * periods, 2),
                "amount_usd": round(spec["USD"] * periods, 2)}

    def cancel(self, subscription_id, reason=""):
        with _lock:
            data = _load()
            sub = data.get("subscriptions", {}).get(subscription_id)
            if not sub:
                return {"success": False, "error": "订阅不存在"}
            if sub.get("status") == STATUS_CANCELLED:
                return {"success": False, "error": "订阅已是取消状态", "idempotent": True}
            sub["status"] = STATUS_CANCELLED
            sub["cancelled_at"] = _now_iso()
            sub["cancel_reason"] = reason
            _append_evidence(sub, "cancelled", sub.get("last_score", 0),
                             sub.get("last_badge_level", "none"), {"reason": reason})
            _save(data)
        return {"success": True, "subscription_id": subscription_id, "status": STATUS_CANCELLED}

    # ── 持续鉴证核心 ──
    def attest_once(self, subscription_id, scan_fn=None, force=False, cert_service=None):
        """对单个订阅执行一次鉴证复扫。

        scan_fn(source_url) -> scan_report；缺省用 scanner.engine.scan。
        force=True 忽略 next_attest_at 的节流。
        """
        with _lock:
            data = _load()
            sub = data.get("subscriptions", {}).get(subscription_id)
            if not sub:
                return {"success": False, "error": "订阅不存在"}

            status = _effective_status(sub)
            sub["status"] = status
            if status in (STATUS_CANCELLED, STATUS_LAPSED):
                _save(data)
                return {"success": False, "error": f"订阅状态为 {status}，已停止持续鉴证",
                        "subscription_id": subscription_id, "status": status}

            if not force:
                nxt = _parse_iso(sub.get("next_attest_at"))
                if nxt and _now() < nxt:
                    _save(data)
                    return {"success": True, "skipped": True, "reason": "not_due",
                            "subscription_id": subscription_id,
                            "next_attest_at": sub.get("next_attest_at")}
            source_url = sub.get("source_url", "")

        # 复扫放在锁外——扫描可能耗时，不能阻塞其它订阅
        if scan_fn is None:
            ws_path = sub.get("workspace_path", "")
            if ws_path and os.path.isdir(ws_path):
                # live agent 模式：每个周期直接重扫其工作区（已加载的 MCP/skill）
                def scan_fn(_url, _path=ws_path):
                    from scanner.workspace_scan import preflight
                    return _live_report(preflight(_path))
            else:
                def scan_fn(url):
                    from scanner.engine import scan as _scan
                    return _scan(url)
        try:
            report = scan_fn(source_url) or {}
        except Exception as exc:
            with _lock:
                data = _load()
                sub = data["subscriptions"][subscription_id]
                _append_evidence(sub, "error", sub.get("last_score", 0),
                                 sub.get("last_badge_level", "none"),
                                 {"error": f"{type(exc).__name__}: {exc}"})
                # 扫描失败不改变认证状态，但要重排下次，避免卡死
                sub["next_attest_at"] = (_now() + timedelta(days=1)).isoformat()
                _save(data)
            return {"success": False, "error": f"复扫失败: {exc}",
                    "subscription_id": subscription_id, "result": "error"}

        score = report.get("overall_score", report.get("score", 0)) or 0
        badge_level = report.get("badge_level", "none")
        prev_level = sub.get("last_badge_level") or badge_level

        # 判定鉴证结论
        if score < CERT_SCORE_THRESHOLD:
            result = "failed"
        elif _LEVEL_RANK.get(badge_level, 0) < _LEVEL_RANK.get(prev_level, 0):
            result = "downgraded"
        else:
            result = "pass"

        cert_action = "none"
        cert_svc = cert_service
        if cert_svc is None:
            try:
                from eco.badge import CertificationService
                cert_svc = CertificationService()
            except Exception:
                cert_svc = None

        with _lock:
            data = _load()
            sub = data["subscriptions"][subscription_id]
            cert_id = sub.get("cert_id") or ""

            if cert_svc and cert_id:
                try:
                    if result == "failed":
                        # rug-pull 兜底：分数掉破门槛立刻吊销，不等到期
                        ok = cert_svc.revoke_certification(
                            cert_id, reason=f"持续鉴证失败：score={score} < {CERT_SCORE_THRESHOLD}")
                        cert_action = "revoked" if ok else "revoke_failed"
                    else:
                        renewed = cert_svc.renew_certification(cert_id, report)
                        cert_action = "renewed" if renewed else "renew_failed"
                except Exception as exc:
                    cert_action = f"error: {type(exc).__name__}"

            sub["last_score"] = score
            sub["last_badge_level"] = badge_level
            sub["last_result"] = result
            sub["last_attest_at"] = _now_iso()
            interval = int(sub.get("attest_interval_days", DEFAULT_ATTEST_INTERVAL_DAYS))
            sub["next_attest_at"] = (_now() + timedelta(days=interval)).isoformat()
            record = _append_evidence(sub, result, score, badge_level,
                                      {"cert_action": cert_action,
                                       "prev_level": prev_level,
                                       "findings": report.get("total_findings", 0)})
            _save(data)

        return {"success": True, "subscription_id": subscription_id, "result": result,
                "score": score, "badge_level": badge_level, "prev_level": prev_level,
                "cert_action": cert_action, "evidence_seq": record["seq"],
                "evidence_hash": record["hash"],
                "next_attest_at": sub["next_attest_at"]}

    def run_cycle(self, scan_fn=None, force=False, cert_service=None):
        """批量执行到期的持续鉴证。定时任务的入口。"""
        data = _load()
        sub_ids = list(data.get("subscriptions", {}).keys())
        summary = {"total": len(sub_ids), "attested": 0, "skipped": 0,
                   "failed": 0, "errors": 0, "results": []}
        for sid in sub_ids:
            res = self.attest_once(sid, scan_fn=scan_fn, force=force, cert_service=cert_service)
            if res.get("skipped"):
                summary["skipped"] += 1
            elif not res.get("success"):
                # 状态不可鉴证（lapsed/cancelled）也计入 skipped，真正的扫描错误才算 error
                if res.get("result") == "error":
                    summary["errors"] += 1
                else:
                    summary["skipped"] += 1
            else:
                summary["attested"] += 1
                if res.get("result") == "failed":
                    summary["failed"] += 1
            summary["results"].append(res)
        summary["ran_at"] = _now_iso()
        return summary

    # ── 查询 ──
    def get_subscription(self, subscription_id):
        sub = _load().get("subscriptions", {}).get(subscription_id)
        if not sub:
            return None
        enriched = dict(sub)
        enriched["effective_status"] = _effective_status(sub)
        enriched["evidence_chain"] = verify_evidence_chain(sub)
        return enriched

    def list_subscriptions(self, status=None, payer_id=None):
        subs = []
        for sub in _load().get("subscriptions", {}).values():
            item = dict(sub)
            item["effective_status"] = _effective_status(sub)
            if status and item["effective_status"] != status:
                continue
            if payer_id and item.get("payer_id") != payer_id:
                continue
            item.pop("attestations", None)      # 列表视图不返回完整证据链
            subs.append(item)
        subs.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        return subs

    def get_expiring(self, days=7):
        """N 天内到期、需要提醒续费的订阅。"""
        now = _now()
        deadline = now + timedelta(days=days)
        out = []
        for sub in _load().get("subscriptions", {}).values():
            if _effective_status(sub) not in (STATUS_ACTIVE, STATUS_GRACE):
                continue
            exp = _parse_iso(sub.get("expires_at"))
            if exp and now <= exp <= deadline:
                item = dict(sub)
                item.pop("attestations", None)
                item["remaining_days"] = (exp - now).days
                out.append(item)
        out.sort(key=lambda s: s.get("expires_at", ""))
        return out

    def trust_status(self, source_url):
        """对外的"这个工具现在还可信吗"查询——Trust API 用。"""
        for sub in _load().get("subscriptions", {}).values():
            if sub.get("source_url") != source_url:
                continue
            eff = _effective_status(sub)
            chain = sub.get("attestations", [])
            last = chain[-1] if chain else None
            continuously_verified = (
                eff in (STATUS_ACTIVE, STATUS_GRACE)
                and bool(last) and last.get("result") in ("pass", "downgraded", "renewed")
            )
            return {
                "source_url": source_url,
                "subscribed": True,
                "subscription_id": sub.get("subscription_id"),
                "status": eff,
                "continuously_verified": continuously_verified,
                "last_result": last.get("result") if last else None,
                "last_score": sub.get("last_score"),
                "badge_level": sub.get("last_badge_level"),
                "last_attest_at": sub.get("last_attest_at"),
                "next_attest_at": sub.get("next_attest_at"),
                "expires_at": sub.get("expires_at"),
                "evidence_entries": len(chain),
                "evidence_chain": verify_evidence_chain(sub),
            }
        return {"source_url": source_url, "subscribed": False,
                "continuously_verified": False,
                "note": "该来源未订阅持续鉴证，徽章仅代表签发时点的快照。"}


# ── 模块级便捷 API ──
_default = AttestationService()


def subscribe(source_url, plan="monthly", payer_id=None, cert_id=None,
              attest_interval_days=DEFAULT_ATTEST_INTERVAL_DAYS):
    return _default.subscribe(source_url, plan, payer_id, cert_id, attest_interval_days)


def renew_subscription(subscription_id, periods=1, plan=None):
    return _default.renew_subscription(subscription_id, periods, plan)


def cancel(subscription_id, reason=""):
    return _default.cancel(subscription_id, reason)


def attest_once(subscription_id, scan_fn=None, force=False, cert_service=None):
    return _default.attest_once(subscription_id, scan_fn, force, cert_service)


def run_cycle(scan_fn=None, force=False, cert_service=None):
    return _default.run_cycle(scan_fn, force, cert_service)


def get_subscription(subscription_id):
    return _default.get_subscription(subscription_id)


def list_subscriptions(status=None, payer_id=None):
    return _default.list_subscriptions(status, payer_id)


def get_expiring(days=7):
    return _default.get_expiring(days)


def trust_status(source_url):
    return _default.trust_status(source_url)


def plans():
    return {k: dict(v) for k, v in SUBSCRIPTION_PLANS.items()}


if __name__ == "__main__":
    svc = AttestationService()
    print("套餐:", json.dumps(plans(), ensure_ascii=False))
    r = svc.subscribe("https://github.com/example/demo", "monthly", payer_id="agent:demo")
    print("订阅:", r.get("subscription_id"), r.get("status"))
    if r.get("success"):
        sid = r["subscription_id"]
        good = lambda url: {"overall_score": 92, "badge_level": "gold", "total_findings": 0}
        print("首次鉴证:", svc.attest_once(sid, scan_fn=good, force=True)["result"])
        bad = lambda url: {"overall_score": 41, "badge_level": "none", "total_findings": 9}
        print("掉分鉴证:", svc.attest_once(sid, scan_fn=bad, force=True)["result"])
        print("信任状态:", svc.trust_status("https://github.com/example/demo")["continuously_verified"])
