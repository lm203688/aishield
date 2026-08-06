"""
eco/monetization.py — 认证徽章 ↔ x402 收费闭环 (Phase 3)

把"中性信任机构"的认证能力接上真实金融轨道：
  - request_cert_payment(source_url, scan_report):
      按 badge 等级定价，返回 x402 402 支付要求（USDC / Base）。
      订单落 data/payments.json，状态 = pending_payment。
  - fulfill_cert(order_id, payment_header, scan_report?):
      结构校验客户端传回的 Payment 头；通过后标记订单已结算（离线降级为
      settled_offline——真实链上结算需钱包 + 在线 facilitator），并发出认证徽章。

这条链路对标 mcp-audit「开源免费」的差异化：AIShield 的认证可付费、可机器对机器结算，
是面向企业"SaaS 化信任背书"的最小可用闭环。
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
PAYMENTS_FILE = os.path.join(_DATA, "payments.json")
_lock = threading.Lock()

# 认证定价（USDC，Base 链 1:1 近似）。none 等级不可认证（score<50）。
PRICE_BY_LEVEL = {"gold": 0.05, "silver": 0.02, "bronze": 0.01, "none": 0.0}
DEFAULT_PAY_TO = os.environ.get("X402_PAY_TO", "0xAIShieldTreasuryPlaceholderAddress")

# 人民币定价（虎皮椒 · 微信/支付宝）。面向国内个人与小团队，x402 之外的第二条轨道。
PRICE_CNY_BY_LEVEL = {"gold": 39.00, "silver": 19.00, "bronze": 9.00, "none": 0.0}


def _now_iso():
    return datetime.now(TZ).isoformat()


def _load():
    if os.path.exists(PAYMENTS_FILE):
        try:
            with open(PAYMENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"orders": {}}


def _save(data):
    with _lock:
        os.makedirs(os.path.dirname(PAYMENTS_FILE), exist_ok=True)
        with open(PAYMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _level_from_report(scan_report):
    if not scan_report:
        return "none"
    lvl = scan_report.get("badge_level")
    if lvl and lvl in PRICE_BY_LEVEL:
        return lvl
    score = scan_report.get("overall_score", 0)
    if score >= 90:
        return "gold"
    if score >= 70:
        return "silver"
    if score >= 50:
        return "bronze"
    return "none"


class BadgeMonetization:
    """认证徽章 ↔ x402 收费闭环服务。"""

    def request_cert_payment(self, source_url, scan_report=None, amount_usd=None):
        """发起一次"付费认证"订单，返回 x402 402 支付要求。"""
        if not source_url:
            return {"success": False, "error": "source_url is required"}
        level = _level_from_report(scan_report)
        if level == "none":
            return {"success": False, "error": "score < 50，无认证资格",
                    "status": "rejected", "badge_level": "none"}
        price = amount_usd if amount_usd is not None else PRICE_BY_LEVEL[level]
        if not price or price <= 0:
            return {"success": False, "error": "定价无效", "badge_level": level}

        from eco.x402 import X402Gateway
        gw = X402Gateway(pay_to=DEFAULT_PAY_TO)
        order_id = f"cert_{uuid.uuid4().hex[:12]}"
        pay = gw.create_payment(amount=price, currency="USD", order_id=order_id,
                                description=f"AIShield {level} 认证 · {source_url}")

        order = {
            "order_id": order_id,
            "type": "cert",
            "source_url": source_url,
            "badge_level": level,
            "amount_usd": price,
            "status": "pending_payment",
            "scan_report": scan_report,
            "payment_requirements": pay.get("payment_requirements"),
            "facilitator": pay.get("facilitator"),
            "created_at": _now_iso(),
        }
        data = _load()
        data.setdefault("orders", {})[order_id] = order
        _save(data)

        return {
            "success": True,
            "status": "requires_payment",
            "order_id": order_id,
            "badge_level": level,
            "amount_usd": price,
            "currency": "USDC",
            "network": pay.get("network", "base"),
            "pay_to": DEFAULT_PAY_TO,
            "payment_requirements": pay.get("payment_requirements"),
            "note": "客户端用钱包对 paymentRequirements 签名后，通过 Payment 头回传 /api/v1/certify/fulfill",
        }

    def fulfill_cert(self, order_id, payment_header, scan_report=None):
        """校验支付头并签发认证。返回 {cert, order}。"""
        if not order_id or not payment_header:
            return {"success": False, "error": "order_id 与 payment_header 均为必填"}
        data = _load()
        order = data.get("orders", {}).get(order_id)
        if not order:
            return {"success": False, "error": "订单不存在", "order_id": order_id}
        if order.get("status") == "settled":
            return {"success": False, "error": "订单已结算", "order_id": order_id}

        from eco.x402 import decode_payment_header, validate_payment_payload
        payload = decode_payment_header(payment_header) if isinstance(payment_header, str) else payment_header
        ok, msg = validate_payment_payload(payload)
        if not ok:
            return {"success": False, "error": f"支付头校验失败: {msg}"}

        # 链上签名验证交给 facilitator；离线环境下降级为 settled_offline。
        settlement = "settled_offline"  # 真实结算需在线 facilitator（见 eco/x402.py）
        order["status"] = settlement
        order["settled_at"] = _now_iso()
        order["payment_header_valid"] = True
        _save(data)

        report = scan_report or order.get("scan_report") or {}
        from eco.badge import CertificationService
        cert = CertificationService().certify_tool(order["source_url"], report)
        return {
            "success": True,
            "order_id": order_id,
            "settlement": settlement,
            "certification": cert,
            "note": "认证已签发；链上 USDC 结算需钱包 + 在线 facilitator（当前为离线降级）",
        }

    # ══════════════════════════════════════════
    #  人民币轨道（虎皮椒 · 微信/支付宝）
    # ══════════════════════════════════════════

    def request_cert_payment_cny(self, source_url, scan_report=None,
                                 payment="wechat", amount_cny=None):
        """发起一次"人民币付费认证"订单，返回可扫码/可跳转的支付链接。

        与 x402 版本同构，区别只在结算轨道：这条给国内用户，那条给 agent。
        """
        if not source_url:
            return {"success": False, "error": "source_url is required"}
        level = _level_from_report(scan_report)
        if level == "none":
            return {"success": False, "error": "score < 50，无认证资格",
                    "status": "rejected", "badge_level": "none"}
        price = amount_cny if amount_cny is not None else PRICE_CNY_BY_LEVEL[level]
        if not price or price <= 0:
            return {"success": False, "error": "定价无效", "badge_level": level}

        from eco.hupijiao import HupijiaoGateway
        gw = HupijiaoGateway()
        if not gw.configured:
            return {"success": False, "error": "人民币通道未配置（虎皮椒凭证缺失）",
                    "gateway": "hupijiao"}

        order_id = f"cert{uuid.uuid4().hex[:12]}"
        res = gw.create_payment(
            amount=price,
            order_id=order_id,
            description=f"AIShield {level} 认证",
            payment=payment,
            attach=order_id,
            metadata={"type": "cert", "source_url": source_url,
                      "badge_level": level, "scan_report": scan_report},
        )
        if not res.get("success"):
            return {"success": False, "error": res.get("error", "下单失败"),
                    "gateway": "hupijiao", "order_id": order_id}

        # 同步登记到统一订单簿，使 /api/v1/certify/list 能同时看到两条轨道
        data = _load()
        data.setdefault("orders", {})[order_id] = {
            "order_id": order_id,
            "type": "cert",
            "gateway": "hupijiao",
            "source_url": source_url,
            "badge_level": level,
            "amount_cny": price,
            "currency": "CNY",
            "payment": payment,
            "status": "pending_payment",
            "scan_report": scan_report,
            "pay_url": res.get("pay_url"),
            "qrcode_url": res.get("qrcode_url"),
            "created_at": _now_iso(),
        }
        _save(data)

        return {
            "success": True,
            "status": "requires_payment",
            "gateway": "hupijiao",
            "order_id": order_id,
            "badge_level": level,
            "amount_cny": price,
            "currency": "CNY",
            "payment": payment,
            "pay_url": res.get("pay_url"),
            "qrcode_url": res.get("qrcode_url"),
            "note": "扫码或打开 pay_url 完成支付；支付成功后虎皮椒回调 /api/v1/pay/hupijiao/notify 自动签发认证。",
        }

    def settle_cny_order(self, trade_order_id, notify_params=None):
        """虎皮椒回调验签通过后调用：幂等地签发认证。

        只处理 metadata.type == "cert" 的订单；其它订单（充值等）原样跳过。
        """
        if not trade_order_id:
            return {"success": False, "error": "trade_order_id is required"}

        data = _load()
        order = data.get("orders", {}).get(trade_order_id)
        if not order:
            # 非认证类订单（如套餐充值），不属于本闭环
            return {"success": False, "error": "非认证订单或订单不存在",
                    "order_id": trade_order_id, "skipped": True}
        if order.get("status") in ("settled", "settled_offline", "paid"):
            # 幂等：重复回调直接返回既有认证，不重复签发
            return {"success": True, "order_id": trade_order_id, "idempotent": True,
                    "settlement": order.get("status"),
                    "certification": order.get("certification")}

        order["status"] = "paid"
        order["settled_at"] = _now_iso()
        order["settlement"] = "hupijiao_cny"
        if notify_params:
            order["transaction_id"] = notify_params.get("transaction_id", "")

        from eco.badge import CertificationService
        cert = CertificationService().certify_tool(
            order.get("source_url", ""), order.get("scan_report") or {})
        order["certification"] = cert
        _save(data)

        return {"success": True, "order_id": trade_order_id,
                "settlement": "hupijiao_cny", "certification": cert}

    def get_order(self, order_id):
        return _load().get("orders", {}).get(order_id)

    def list_orders(self, status=None):
        orders = list(_load().get("orders", {}).values())
        if status:
            orders = [o for o in orders if o.get("status") == status]
        return orders


# ── 通用 x402 要求助手（供其它付费服务复用）──
def x402_requirements(amount_usd, resource, description="AIShield service"):
    from eco.x402 import X402Gateway
    gw = X402Gateway(pay_to=DEFAULT_PAY_TO)
    pay = gw.create_payment(amount=amount_usd, currency="USD",
                            order_id=f"srv_{uuid.uuid4().hex[:12]}",
                            description=description)
    pay["payment_requirements"].setdefault("paymentRequirements", [{}])[0]["resource"] = resource
    return pay


# ── 模块级便捷 API ──
_default = BadgeMonetization()


def request_cert_payment(source_url, scan_report=None, amount_usd=None):
    return _default.request_cert_payment(source_url, scan_report, amount_usd)


def fulfill_cert(order_id, payment_header, scan_report=None):
    return _default.fulfill_cert(order_id, payment_header, scan_report)


def request_cert_payment_cny(source_url, scan_report=None, payment="wechat", amount_cny=None):
    return _default.request_cert_payment_cny(source_url, scan_report, payment, amount_cny)


def settle_cny_order(trade_order_id, notify_params=None):
    return _default.settle_cny_order(trade_order_id, notify_params)


def get_order(order_id):
    return _default.get_order(order_id)


def list_orders(status=None):
    return _default.list_orders(status)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(_BASE))
    from eco.x402 import build_payment_payload, encode_payment_header

    # 演示完整闭环：请求 → 模拟钱包签名 → 履约签发
    rep = {"overall_score": 92, "badge_level": "gold", "risk_level": "safe", "total_findings": 0}
    req = request_cert_payment("https://github.com/example/gold-tool", rep)
    print("请求:", req["status"], req["order_id"], f"${req['amount_usd']} USDC")

    # 模拟客户端钱包签名（真实环境由 viem/ethers 完成）
    signed = {"from": "0xClient", "to": DEFAULT_PAY_TO, "value": "50000",
              "validAfter": "0", "validBefore": "9999999999", "nonce": "0xabc", "signature": "0xdef"}
    header = encode_payment_header(build_payment_payload(signed))
    res = fulfill_cert(req["order_id"], header, rep)
    print("履约:", res["success"], "->", res["certification"]["status"], res["certification"]["cert_id"])
