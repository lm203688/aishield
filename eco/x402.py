"""
eco/x402.py — x402 / USDC 机器对机器支付网关 (P2 迭代)

x402 是 agent-to-agent 经济的事实标准支付协议 (2026 已进入 Linux 基金会,
累计 100M+ 笔支付; Coinbase Agent.market + Cloudflare/AWS/Google/Visa/Stripe/Shopify 全部接入)。

本模块让 AIShield 的"服务交易"赛道具备真实的金融轨道:
  - build_payment_requirements(): 生成 402 响应体 (x402Version / paymentRequirements)
  - X402Gateway: 与 AlipayGateway/CreemGateway 同接口的支付网关
  - FacilitatorClient: 调用 facilitator 验证/结算 (可降级)
  - 真实签名由钱包侧 (viem/ethers/Coinbase CDP) 完成, 本模块提供协议结构与校验

注意: 零第三方依赖, 仅标准库。链上签名需外部钱包, 这里提供协议骨架与校验。
"""

import json
import base64
import uuid
import threading
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))

X402_VERSION = 1
DEFAULT_NETWORK = "base"                       # USDC 主战场
DEFAULT_ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # Base USDC
DEFAULT_FACILITATOR = "https://x402.org/facilitator"
SUPPORTED_SCHEMES = ["exact"]                  # EIP-3009 transferWithAuthorization

_lock = threading.Lock()


# ══════════════════════════════════════════════
#  协议结构
# ══════════════════════════════════════════════
def build_payment_requirements(pay_to, amount_usd, asset=DEFAULT_ASSET,
                               network=DEFAULT_NETWORK, resource="",
                               description="AIShield service payment",
                               max_timeout_seconds=60, facilitator=DEFAULT_FACILITATOR):
    """生成 x402 402 响应体 (paymentRequirements)。

    amount_usd:  以 USD 计价的金额 (USDC 1:1 近似)
    pay_to:      收款地址 (AIShield 钱包)
    """
    usdc_amount = str(round(float(amount_usd), 6))
    return {
        "x402Version": X402_VERSION,
        "facilitator": facilitator,
        "paymentRequirements": [
            {
                "scheme": "exact",
                "network": network,
                "maxAmountRequired": usdc_amount,
                "asset": asset,
                "payTo": pay_to,
                "maxTimeoutSeconds": max_timeout_seconds,
                "resource": resource,
                "description": description,
            }
        ],
    }


def build_payment_payload(signed_transfer, network=DEFAULT_NETWORK):
    """组装 PaymentPayload (客户端钱包签名后调用)。

    signed_transfer: 钱包侧用 EIP-3009 transferWithAuthorization 签出的 authorization dict,
                     形如 {from, to, value, validAfter, validBefore, nonce, signature}
    """
    return {
        "x402Version": X402_VERSION,
        "scheme": "exact",
        "network": network,
        "payload": {
            "signature": signed_transfer.get("signature", ""),
            "authorization": {
                "from": signed_transfer.get("from", ""),
                "to": signed_transfer.get("to", ""),
                "value": str(signed_transfer.get("value", "0")),
                "validAfter": signed_transfer.get("validAfter", "0"),
                "validBefore": signed_transfer.get("validBefore", "0"),
                "nonce": signed_transfer.get("nonce", ""),
            },
        },
    }


def encode_payment_header(payload):
    """将 PaymentPayload 编码为 x402 `Payment` 请求头值 (base64 JSON)。"""
    raw = json.dumps(payload, separators=(",", ":"))
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")


def decode_payment_header(header_value):
    """解码 `Payment` 头 → PaymentPayload。"""
    try:
        raw = base64.b64decode(header_value.encode("ascii"))
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def validate_payment_payload(payload):
    """结构级校验 (不含链上签名验证, 链上验证交给 facilitator)。"""
    if not isinstance(payload, dict):
        return False, "payload must be object"
    if payload.get("x402Version") != X402_VERSION:
        return False, "unsupported x402Version"
    if payload.get("scheme") not in SUPPORTED_SCHEMES:
        return False, "unsupported scheme"
    auth = (payload.get("payload") or {}).get("authorization") or {}
    for field in ("from", "to", "value", "validAfter", "validBefore", "nonce"):
        if not auth.get(field):
            return False, f"missing authorization.{field}"
    if not (payload.get("payload") or {}).get("signature"):
        return False, "missing signature"
    return True, "ok"


# ══════════════════════════════════════════════
#  Facilitator 客户端 (可降级)
# ══════════════════════════════════════════════
class FacilitatorClient:
    """调用 x402 facilitator 验证并结算支付。无网络时返回未验证。"""

    def __init__(self, facilitator_url=DEFAULT_FACILITATOR, timeout=15):
        self.url = facilitator_url
        self.timeout = timeout

    def verify_and_settle(self, payment_payload):
        """请求 facilitator 验证签名并结算。返回 {verified, tx_hash?, error?}。"""
        try:
            from urllib import request as _req
            req = _req.Request(
                self.url.rstrip("/") + "/verify",
                data=json.dumps(payment_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with _req.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return {"verified": bool(data.get("isValid")), "raw": data}
        except Exception as e:
            return {"verified": False, "error": str(e), "offline": True}


# ══════════════════════════════════════════════
#  支付网关 (与 Alipay/Creem 同接口)
# ══════════════════════════════════════════════
class X402Gateway:
    """x402 / USDC 机器对机器支付网关。

    与 PaymentGateway 接口兼容 (create_payment / verify_payment / refund / get_name)。
    """

    def __init__(self, pay_to="", facilitator=DEFAULT_FACILITATOR, network=DEFAULT_NETWORK):
        # 收款地址: 优先参数, 其次环境变量, 否则占位 (部署时配置)
        self.pay_to = pay_to or os_environ("X402_PAY_TO", "")
        self.facilitator = facilitator
        self.network = network

    def create_payment(self, amount, currency="USD", order_id=None, description=""):
        """生成 x402 支付要求 (402 响应体)。amount 以 USD 计价。"""
        order_id = order_id or f"x402_{uuid.uuid4().hex[:12]}"
        requirements = build_payment_requirements(
            pay_to=self.pay_to,
            amount_usd=amount,
            network=self.network,
            resource=f"order:{order_id}",
            description=description or "AIShield x402 payment",
            facilitator=self.facilitator,
        )
        return {
            "status": "requires_payment",
            "gateway": "x402",
            "order_id": order_id,
            "amount_usd": amount,
            "asset": "USDC",
            "network": self.network,
            "pay_to": self.pay_to,
            "facilitator": self.facilitator,
            "payment_requirements": requirements,
            "note": "客户端用钱包对 paymentRequirements 签名后, 通过 Payment 头回传。",
        }

    def verify_payment(self, payment_header, facilitator_client=None):
        """验证客户端回传的 `Payment` 头。"""
        payload = decode_payment_header(payment_header) if isinstance(payment_header, str) else payment_header
        if not payload:
            return {"verified": False, "error": "invalid payment header"}
        ok, msg = validate_payment_payload(payload)
        if not ok:
            return {"verified": False, "error": msg}
        # 链上签名验证交给 facilitator
        client = facilitator_client or FacilitatorClient(self.facilitator)
        res = client.verify_and_settle(payload)
        return {"verified": res.get("verified", False), **res}

    def refund(self, payment_id, reason=""):
        """x402 为结算型支付, 退款需链上反向转账, 本网关不直接支持。"""
        return {"refunded": False, "error": "x402 settlement-based; refund via on-chain reverse transfer", "gateway": "x402"}

    def get_name(self):
        return "x402"


def os_environ(key, default=""):
    import os
    return os.environ.get(key, default)


# ══════════════════════════════════════════════
#  市场集成助手
# ══════════════════════════════════════════════
def x402_requirements_for_listing(listing, pay_to=""):
    """为市场挂牌项附加 x402 支付要求, 使其可被 agent 直接付费调用。"""
    price = listing.get("price_usd", 0)
    return {
        **listing,
        "payment": {
            "method": "x402",
            "currency": "USDC",
            "amount_usd": price,
            "network": DEFAULT_NETWORK,
            "requirements": build_payment_requirements(
                pay_to=pay_to, amount_usd=price, resource=listing.get("id", "")
            ),
        },
    }


if __name__ == "__main__":
    req = build_payment_requirements("0xAIShieldWalletAddress", 0.05, network="base")
    print(json.dumps(req, indent=2))
    sample_signed = {
        "from": "0xClient", "to": "0xAIShieldWalletAddress", "value": "50000",
        "validAfter": "0", "validBefore": "9999999999", "nonce": "0xabc",
        "signature": "0xdef",
    }
    payload = build_payment_payload(sample_signed)
    header = encode_payment_header(payload)
    print("Payment header:", header[:40], "...")
    print("validate:", validate_payment_payload(payload))
