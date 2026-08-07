"""
eco/spend_cap.py — 支付层消费上限（per-agent spend cap）

为什么在支付层而不是应用层做：
    agent 自主付费（x402 / 虎皮椒）意味着"程序可以自己花钱"。一旦提示注入
    或逻辑失控，应用层的 if 判断很容易被绕过。企业采购把"支付上限"当作
    硬门槛——额度必须由结算通道统一强制，且默认拒绝而非默认放行。

四个不变量：
    1. 单笔上限 per_tx      —— 挡住"一次性大额"
    2. 日累计 daily         —— 挡住"高频小额磨额度"
    3. 月累计 monthly       —— 挡住"跨日持续失控"
    4. fail-closed          —— 策略读不出来/币种未配额度 → 拒绝，不是放行

并发安全靠"预留-确认"两阶段：
    reserve(order_id) 先冻结额度 → 下单成功 commit() 落账 / 下单失败 release() 退回。
    预留带 TTL（默认 15 分钟），超时自动回收，避免额度被废单占死。

零第三方依赖，账本落 api/data/spend_caps.json（已被 .gitignore 覆盖）。
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_BASE, "api", "data")
CAPS_FILE = os.path.join(_DATA, "spend_caps.json")

_lock = threading.RLock()

# 预留有效期（秒）：下单流程走完通常 <60s，给 15 分钟冗余
RESERVATION_TTL_SEC = 900

# 默认额度（保守）。可用 set_policy 按 payer 覆盖，或用环境变量调全局默认。
DEFAULT_LIMITS = {
    "CNY": {
        "per_tx": float(os.environ.get("AISHIELD_CAP_CNY_PER_TX", "500")),
        "daily": float(os.environ.get("AISHIELD_CAP_CNY_DAILY", "2000")),
        "monthly": float(os.environ.get("AISHIELD_CAP_CNY_MONTHLY", "10000")),
    },
    "USD": {
        "per_tx": float(os.environ.get("AISHIELD_CAP_USD_PER_TX", "50")),
        "daily": float(os.environ.get("AISHIELD_CAP_USD_DAILY", "200")),
        "monthly": float(os.environ.get("AISHIELD_CAP_USD_MONTHLY", "1000")),
    },
}

# 总开关：设为 "0"/"false" 可停用（仅供本地调试，生产不建议）
def _enabled():
    return os.environ.get("AISHIELD_SPEND_CAP", "1").strip().lower() not in ("0", "false", "off", "no")


def _now():
    return datetime.now(TZ)


def _now_iso():
    return _now().isoformat()


def _day_key(dt=None):
    return (dt or _now()).strftime("%Y-%m-%d")


def _month_key(dt=None):
    return (dt or _now()).strftime("%Y-%m")


def _norm_currency(currency):
    c = (currency or "").strip().upper()
    if c == "USDC":       # x402 结算资产，额度与 USD 共用
        return "USD"
    if c in ("RMB", "CNH"):
        return "CNY"
    return c


def _norm_payer(payer_id):
    p = (payer_id or "").strip()
    return p if p else "anonymous"


def _load():
    if os.path.exists(CAPS_FILE):
        try:
            with open(CAPS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("policies", {})
                data.setdefault("ledger", {})
                data.setdefault("reservations", {})
                data.setdefault("committed", {})
                return data
        except Exception:
            # 账本损坏时不静默清零——返回空结构但由 fail-closed 逻辑兜底
            pass
    return {"policies": {}, "ledger": {}, "reservations": {}, "committed": {}}


def _save(data):
    os.makedirs(os.path.dirname(CAPS_FILE), exist_ok=True)
    tmp = CAPS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CAPS_FILE)


def _limits_for(data, payer_id, currency):
    """取该 payer 在该币种下的额度。未显式配置则用默认；币种完全未知返回 None（fail-closed）。"""
    pol = data.get("policies", {}).get(payer_id) or {}
    lim = (pol.get("limits") or {}).get(currency)
    if lim:
        merged = dict(DEFAULT_LIMITS.get(currency, {}))
        merged.update({k: v for k, v in lim.items() if isinstance(v, (int, float))})
        return merged
    return dict(DEFAULT_LIMITS[currency]) if currency in DEFAULT_LIMITS else None


def _prune_reservations(data):
    """回收过期预留，返回被回收的数量。"""
    now = _now()
    dropped = []
    for rid, r in list(data.get("reservations", {}).items()):
        try:
            exp = datetime.fromisoformat(r.get("expires_at", ""))
        except Exception:
            dropped.append(rid)
            continue
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=TZ)
        if now > exp:
            dropped.append(rid)
    for rid in dropped:
        data["reservations"].pop(rid, None)
    return len(dropped)


def _spent(data, payer_id, currency):
    """已确认消费：(日累计, 月累计)。"""
    book = data.get("ledger", {}).get(payer_id, {}).get(currency, {})
    d = float(book.get("daily", {}).get(_day_key(), 0.0))
    m = float(book.get("monthly", {}).get(_month_key(), 0.0))
    return d, m


def _reserved(data, payer_id, currency):
    """未确认但已冻结的额度合计（仅统计未过期的）。"""
    total = 0.0
    for r in data.get("reservations", {}).values():
        if r.get("payer_id") == payer_id and r.get("currency") == currency:
            total += float(r.get("amount", 0.0))
    return total


class SpendCapService:
    """支付上限服务。所有金额均为该币种的最小可读单位（元 / 美元），非分。"""

    # ── 策略管理 ──
    def set_policy(self, payer_id, currency, per_tx=None, daily=None, monthly=None, note=""):
        payer_id = _norm_payer(payer_id)
        currency = _norm_currency(currency)
        if currency not in DEFAULT_LIMITS:
            return {"success": False, "error": f"不支持的币种: {currency}"}
        with _lock:
            data = _load()
            pol = data.setdefault("policies", {}).setdefault(payer_id, {"limits": {}})
            lim = pol.setdefault("limits", {}).setdefault(currency, {})
            for key, val in (("per_tx", per_tx), ("daily", daily), ("monthly", monthly)):
                if val is not None:
                    if not isinstance(val, (int, float)) or val < 0:
                        return {"success": False, "error": f"{key} 必须是非负数"}
                    lim[key] = float(val)
            pol["updated_at"] = _now_iso()
            if note:
                pol["note"] = note
            _save(data)
            return {"success": True, "payer_id": payer_id, "currency": currency,
                    "limits": _limits_for(data, payer_id, currency)}

    def get_policy(self, payer_id, currency="CNY"):
        payer_id = _norm_payer(payer_id)
        currency = _norm_currency(currency)
        data = _load()
        return {"payer_id": payer_id, "currency": currency,
                "limits": _limits_for(data, payer_id, currency),
                "custom": bool(data.get("policies", {}).get(payer_id))}

    # ── 额度检查 ──
    def check(self, payer_id, amount, currency="CNY"):
        """只读检查，不冻结额度。返回 (ok, reason, detail)。"""
        payer_id = _norm_payer(payer_id)
        currency = _norm_currency(currency)

        if not _enabled():
            return True, "cap_disabled", {"enabled": False}

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, "invalid_amount", {"amount": amount}
        if amount <= 0:
            return False, "invalid_amount", {"amount": amount}

        with _lock:
            data = _load()
            _prune_reservations(data)
            limits = _limits_for(data, payer_id, currency)
            # fail-closed：币种没有任何额度定义 → 拒绝
            if not limits:
                return False, "currency_not_allowed", {"currency": currency}

            if amount > limits["per_tx"]:
                return False, "per_tx_exceeded", {
                    "amount": amount, "limit": limits["per_tx"], "currency": currency}

            day_spent, month_spent = _spent(data, payer_id, currency)
            held = _reserved(data, payer_id, currency)

            if day_spent + held + amount > limits["daily"]:
                return False, "daily_exceeded", {
                    "amount": amount, "spent": day_spent, "reserved": held,
                    "limit": limits["daily"], "currency": currency}

            if month_spent + held + amount > limits["monthly"]:
                return False, "monthly_exceeded", {
                    "amount": amount, "spent": month_spent, "reserved": held,
                    "limit": limits["monthly"], "currency": currency}

            return True, "ok", {
                "amount": amount, "currency": currency,
                "daily_remaining": round(limits["daily"] - day_spent - held - amount, 6),
                "monthly_remaining": round(limits["monthly"] - month_spent - held - amount, 6),
            }

    # ── 两阶段：预留 → 确认 / 释放 ──
    def reserve(self, payer_id, amount, currency="CNY", order_id=""):
        """冻结额度。成功返回 {"success": True, "reservation_id": ...}。"""
        payer_id = _norm_payer(payer_id)
        currency = _norm_currency(currency)

        if not _enabled():
            return {"success": True, "reservation_id": "", "skipped": True, "reason": "cap_disabled"}

        ok, reason, detail = self.check(payer_id, amount, currency)
        if not ok:
            return {"success": False, "error": reason, "reason": reason, "detail": detail}

        with _lock:
            data = _load()
            _prune_reservations(data)
            # 幂等：同一 order_id 已有活跃预留则直接复用，避免重复冻结
            for rid, r in data.get("reservations", {}).items():
                if order_id and r.get("order_id") == order_id:
                    return {"success": True, "reservation_id": rid, "idempotent": True,
                            "amount": r.get("amount"), "currency": r.get("currency")}
            rid = f"rsv_{uuid.uuid4().hex[:12]}"
            data.setdefault("reservations", {})[rid] = {
                "reservation_id": rid,
                "payer_id": payer_id,
                "order_id": order_id or rid,
                "amount": float(amount),
                "currency": currency,
                "created_at": _now_iso(),
                "expires_at": (_now() + timedelta(seconds=RESERVATION_TTL_SEC)).isoformat(),
            }
            _save(data)
            return {"success": True, "reservation_id": rid, "amount": float(amount),
                    "currency": currency, "expires_in": RESERVATION_TTL_SEC}

    def commit(self, reservation_id=None, order_id=None,
               payer_id=None, amount=None, currency=None):
        """把预留额度落到已消费账本。幂等：同一 order_id 只计一次。

        钱已经付了，记账就必须成功。若预留已 TTL 过期（结算比下单晚很多是常态），
        允许用 payer_id/amount/currency 直接补记——账本宁可超限也不能漏账，
        否则限额会被"拖时间"绕过。
        """
        if not _enabled():
            return {"success": True, "skipped": True, "reason": "cap_disabled"}
        if not reservation_id and not order_id:
            return {"success": False, "error": "reservation_id 或 order_id 至少提供一个"}

        with _lock:
            data = _load()
            _prune_reservations(data)

            # 幂等闸门：该订单已入账则直接返回
            if order_id and order_id in data.get("committed", {}):
                return {"success": True, "idempotent": True, "order_id": order_id,
                        "committed_at": data["committed"][order_id].get("committed_at")}

            res = None
            rid = None
            if reservation_id and reservation_id in data.get("reservations", {}):
                rid, res = reservation_id, data["reservations"][reservation_id]
            elif order_id:
                for k, r in data.get("reservations", {}).items():
                    if r.get("order_id") == order_id:
                        rid, res = k, r
                        break
            if not res:
                # 预留已过期 → 用显式参数补记，绝不静默漏账
                if payer_id and amount is not None and currency:
                    res = {"payer_id": _norm_payer(payer_id), "amount": float(amount),
                           "currency": _norm_currency(currency),
                           "order_id": order_id or f"late_{uuid.uuid4().hex[:8]}"}
                    rid = None
                else:
                    return {"success": False, "error": "预留不存在或已过期",
                            "reservation_id": reservation_id, "order_id": order_id}

            payer_id, currency = res["payer_id"], res["currency"]
            amount = float(res["amount"])
            book = (data.setdefault("ledger", {})
                        .setdefault(payer_id, {})
                        .setdefault(currency, {"daily": {}, "monthly": {}}))
            dk, mk = _day_key(), _month_key()
            book.setdefault("daily", {})[dk] = round(float(book.get("daily", {}).get(dk, 0.0)) + amount, 6)
            book.setdefault("monthly", {})[mk] = round(float(book.get("monthly", {}).get(mk, 0.0)) + amount, 6)

            data["reservations"].pop(rid, None)
            data.setdefault("committed", {})[res["order_id"]] = {
                "payer_id": payer_id, "amount": amount, "currency": currency,
                "committed_at": _now_iso(),
            }
            _save(data)
            return {"success": True, "order_id": res["order_id"], "payer_id": payer_id,
                    "amount": amount, "currency": currency,
                    "daily_total": book["daily"][dk], "monthly_total": book["monthly"][mk]}

    def release(self, reservation_id=None, order_id=None):
        """下单失败时退回冻结额度。"""
        if not _enabled():
            return {"success": True, "skipped": True, "reason": "cap_disabled"}
        with _lock:
            data = _load()
            target = None
            if reservation_id and reservation_id in data.get("reservations", {}):
                target = reservation_id
            elif order_id:
                for k, r in data.get("reservations", {}).items():
                    if r.get("order_id") == order_id:
                        target = k
                        break
            if not target:
                return {"success": False, "error": "预留不存在", "released": False}
            r = data["reservations"].pop(target)
            _save(data)
            return {"success": True, "released": True, "reservation_id": target,
                    "amount": r.get("amount"), "currency": r.get("currency")}

    # ── 观测 ──
    def usage(self, payer_id, currency="CNY"):
        payer_id = _norm_payer(payer_id)
        currency = _norm_currency(currency)
        with _lock:
            data = _load()
            _prune_reservations(data)
            limits = _limits_for(data, payer_id, currency) or {}
            day_spent, month_spent = _spent(data, payer_id, currency)
            held = _reserved(data, payer_id, currency)
            return {
                "payer_id": payer_id, "currency": currency, "enabled": _enabled(),
                "limits": limits,
                "daily_spent": day_spent, "monthly_spent": month_spent, "reserved": held,
                "daily_remaining": round(limits.get("daily", 0) - day_spent - held, 6) if limits else 0,
                "monthly_remaining": round(limits.get("monthly", 0) - month_spent - held, 6) if limits else 0,
                "day": _day_key(), "month": _month_key(),
            }

    def list_reservations(self, payer_id=None):
        with _lock:
            data = _load()
            _prune_reservations(data)
            items = list(data.get("reservations", {}).values())
            if payer_id:
                pid = _norm_payer(payer_id)
                items = [r for r in items if r.get("payer_id") == pid]
            return items


# ── 模块级便捷 API ──
_default = SpendCapService()


def check(payer_id, amount, currency="CNY"):
    return _default.check(payer_id, amount, currency)


def reserve(payer_id, amount, currency="CNY", order_id=""):
    return _default.reserve(payer_id, amount, currency, order_id)


def commit(reservation_id=None, order_id=None, payer_id=None, amount=None, currency=None):
    return _default.commit(reservation_id, order_id, payer_id, amount, currency)


def release(reservation_id=None, order_id=None):
    return _default.release(reservation_id, order_id)


def usage(payer_id, currency="CNY"):
    return _default.usage(payer_id, currency)


def set_policy(payer_id, currency, per_tx=None, daily=None, monthly=None, note=""):
    return _default.set_policy(payer_id, currency, per_tx, daily, monthly, note)


def get_policy(payer_id, currency="CNY"):
    return _default.get_policy(payer_id, currency)


if __name__ == "__main__":
    svc = SpendCapService()
    print("默认策略:", svc.get_policy("agent:demo", "CNY"))
    r = svc.reserve("agent:demo", 39.0, "CNY", order_id="demo_order_1")
    print("预留:", r)
    print("确认:", svc.commit(order_id="demo_order_1"))
    print("用量:", svc.usage("agent:demo", "CNY"))
    print("超单笔:", svc.check("agent:demo", 99999, "CNY"))
