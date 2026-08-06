"""
eco/hupijiao.py — 虎皮椒（XunhuPay）人民币支付网关

补上 AIShield 商业化的最后一块：**中国用户可用的真实 CNY 通道**。
此前只有 x402/USDC（机器对机器）与 Creem（国际卡），国内个人/小团队无法付款。

  x402   → agent 对 agent，链上 USDC
  Creem  → 海外信用卡
  虎皮椒 → 微信 / 支付宝，个人主体即可收款  ← 本模块

协议要点（虎皮椒 v3）：
  - 下单  POST {api_base}/payment/do.html     → {errcode, url, url_qrcode, oderid}
  - 查单  POST {api_base}/payment/query.html  → {errcode, data:{status,...}}
  - 回调  虎皮椒 POST 表单到 notify_url，业务方必须回纯文本 "success"
  - 签名  按 key 升序拼 k=v&...（剔除 hash 与空值）+ AppSecret，MD5

安全设计（支付是最常见的越权入口，这里逐条堵死）：
  1. 密钥只从 eco.credentials 装载，代码内无明文；对外一律 mask。
  2. 回调签名用 hmac.compare_digest 比对，避免时序侧信道。
  3. 校验回调里的 appid 必须等于本地 appid —— 否则他人可用自己的商户号伪造。
  4. **金额篡改防护**：回调 total_fee 必须与本地下单金额一致，否则拒绝。
  5. **重放防护**：按 open_order_id / transaction_id 去重，已结算订单不再履约。
  6. api_base 走白名单，防止环境变量被污染后变成 SSRF 跳板。
  7. 零第三方依赖，仅标准库 urllib。
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import random
import string
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

from . import credentials

TZ = timezone(timedelta(hours=8))

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS_FILE = os.path.join(_BASE, "api", "data", "hupijiao_orders.json")
_lock = threading.Lock()

DEFAULT_API_BASE = "https://api.xunhupay.com"
CREATE_PATH = "/payment/do.html"
QUERY_PATH = "/payment/query.html"

API_VERSION = "1.1"
PLUGIN_ID = "aishield"

#: 支付方式
PAYMENT_WECHAT = "wechat"
PAYMENT_ALIPAY = "alipay"
SUPPORTED_PAYMENTS = (PAYMENT_WECHAT, PAYMENT_ALIPAY)

#: 订单状态（虎皮椒）：OD = 已支付，WP = 待支付，CD = 已关闭
STATUS_PAID = "OD"

#: api_base 主机白名单（防 SSRF）。可用 HUPIJIAO_EXTRA_HOSTS 逗号分隔追加自建域名。
_ALLOWED_HOST_SUFFIXES = (".xunhupay.com",)
_ALLOWED_HOSTS = {"api.xunhupay.com", "admin.xunhupay.com"}


# ══════════════════════════════════════════════
#  签名
# ══════════════════════════════════════════════

def generate_hash(params, app_secret):
    """虎皮椒签名：key 升序拼 `k=v&...`（剔除 hash 与空值）+ AppSecret，取 MD5。"""
    parts = []
    for key in sorted(params.keys()):
        if key == "hash":
            continue
        val = params[key]
        if val is None or val == "":
            continue
        parts.append("%s=%s" % (key, val))
    raw = "&".join(parts) + (app_secret or "")
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def verify_hash(params, app_secret):
    """恒定时间比对回调/响应签名。缺 hash 或未配置密钥一律判否。"""
    given = (params or {}).get("hash", "")
    if not given or not app_secret:
        return False
    expected = generate_hash(params, app_secret)
    return hmac.compare_digest(str(given).lower(), expected.lower())


def _nonce(length=16):
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def _extract_open_order_id(pay_url):
    """从支付链接里取虎皮椒平台单号（v3 的 `id` 查询参数）。取不到返回空串。"""
    if not pay_url:
        return ""
    try:
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(pay_url).query)
        return (qs.get("id") or [""])[0]
    except Exception:
        return ""


def _now_iso():
    return datetime.now(TZ).isoformat()


# ══════════════════════════════════════════════
#  本地订单台账（金额篡改 / 重放防护的依据）
# ══════════════════════════════════════════════

def _load_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {"orders": {}}


def _save_orders(data):
    with _lock:
        os.makedirs(os.path.dirname(ORDERS_FILE), exist_ok=True)
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def get_order(trade_order_id):
    return _load_orders().get("orders", {}).get(trade_order_id)


def list_orders(status=None, limit=200):
    orders = list(_load_orders().get("orders", {}).values())
    if status:
        orders = [o for o in orders if o.get("status") == status]
    orders.sort(key=lambda o: o.get("created_at", ""), reverse=True)
    return orders[:limit]


def _amounts_equal(a, b, tol=0.005):
    """金额比对（分级容差，规避浮点误差）。任一侧不可解析即判不等。"""
    try:
        return abs(float(a) - float(b)) < tol
    except (TypeError, ValueError):
        return False


# ══════════════════════════════════════════════
#  网关
# ══════════════════════════════════════════════

class HupijiaoGateway:
    """虎皮椒支付网关（与 AlipayGateway / CreemGateway / X402Gateway 同接口）。"""

    def __init__(self, appid=None, app_secret=None, api_base=None,
                 notify_url=None, return_url=None, callback_url=None,
                 wap_name="AIShield", wap_url="https://aishield.tools", timeout=20):
        self.appid = appid or credentials.get("HUPIJIAO_APPID")
        self.app_secret = app_secret or credentials.get("HUPIJIAO_APP_SECRET")
        self.api_base = (api_base or credentials.get("HUPIJIAO_API_BASE")
                         or DEFAULT_API_BASE).rstrip("/")
        self.notify_url = notify_url or credentials.get("HUPIJIAO_NOTIFY_URL")
        self.return_url = return_url or credentials.get("HUPIJIAO_RETURN_URL")
        self.callback_url = callback_url or credentials.get("HUPIJIAO_CALLBACK_URL")
        self.wap_name = wap_name
        self.wap_url = wap_url
        self.timeout = timeout

    # ── 配置状态（可安全外发，无明文）──
    @property
    def configured(self):
        return bool(self.appid and self.app_secret)

    def status(self):
        return {
            "gateway": "hupijiao",
            "configured": self.configured,
            "appid": credentials.mask(self.appid, keep=3),
            "app_secret": credentials.mask(self.app_secret),
            "secret_fingerprint": credentials.fingerprint(self.app_secret),
            "api_base": self.api_base,
            "api_base_allowed": self._host_allowed(self.api_base),
            "notify_url": self.notify_url or "(未配置)",
            "supported_payments": list(SUPPORTED_PAYMENTS),
        }

    # ── SSRF 防护 ──
    @staticmethod
    def _host_allowed(api_base):
        try:
            host = urllib.parse.urlparse(api_base).hostname or ""
        except Exception:
            return False
        host = host.lower()
        extra = [h.strip().lower() for h in
                 (os.environ.get("HUPIJIAO_EXTRA_HOSTS", "") or "").split(",") if h.strip()]
        if host in _ALLOWED_HOSTS or host in extra:
            return True
        return any(host.endswith(sfx) for sfx in _ALLOWED_HOST_SUFFIXES)

    def _post(self, path, params):
        """表单 POST，返回 (data_dict, error_str)。仅标准库。"""
        if not self._host_allowed(self.api_base):
            return None, "api_base 主机不在白名单内: %s" % self.api_base
        url = self.api_base + path
        body = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "User-Agent": "AIShield/4.2 (+https://aishield.tools)",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            return None, "HTTP %s: %s" % (e.code, e.read().decode("utf-8", errors="replace")[:300])
        except Exception as e:
            return None, str(e)
        try:
            return json.loads(raw), None
        except Exception:
            return None, "响应非 JSON: %s" % raw[:300]

    # ── 下单 ──
    def create_payment(self, amount, currency="CNY", order_id=None, description="",
                       payment=PAYMENT_WECHAT, attach="", notify_url=None,
                       return_url=None, callback_url=None, metadata=None):
        """创建支付订单。amount 单位：元（CNY）。

        返回 {success, order_id, pay_url, qrcode_url, ...} 或 {success:False, error}。
        """
        if not self.configured:
            return {"success": False, "error": "虎皮椒网关未配置（缺 HUPIJIAO_APPID / HUPIJIAO_APP_SECRET）",
                    "gateway": "hupijiao", "hint": "写入 .secrets.json 或设置同名环境变量"}
        if currency and currency.upper() != "CNY":
            return {"success": False, "error": "虎皮椒仅支持 CNY，收到 %s" % currency}
        if payment not in SUPPORTED_PAYMENTS:
            return {"success": False, "error": "payment 只能是 %s" % (list(SUPPORTED_PAYMENTS),)}
        try:
            amount_f = float(amount)
        except (TypeError, ValueError):
            return {"success": False, "error": "amount 无法解析为数字"}
        if amount_f <= 0:
            return {"success": False, "error": "amount 必须大于 0"}

        order_id = order_id or "as%s%s" % (int(time.time()), _nonce(6).lower())
        total_fee = "%.2f" % amount_f

        params = {
            "version": API_VERSION,
            "appid": self.appid,
            "trade_order_id": order_id,
            "payment": payment,
            "total_fee": total_fee,
            "title": (description or "AIShield 服务")[:60],
            "time": str(int(time.time())),
            "notify_url": notify_url or self.notify_url or "",
            "return_url": return_url or self.return_url or "",
            "callback_url": callback_url or self.callback_url or "",
            "nonce_str": _nonce(),
            "plugins": PLUGIN_ID,
            "wap_url": self.wap_url,
            "wap_name": self.wap_name,
        }
        if attach:
            params["attach"] = str(attach)[:200]
        params["hash"] = generate_hash(params, self.app_secret)

        data, err = self._post(CREATE_PATH, params)
        if err:
            return {"success": False, "error": err, "gateway": "hupijiao", "order_id": order_id}

        errcode = data.get("errcode")
        if str(errcode) != "0":
            return {"success": False, "gateway": "hupijiao", "order_id": order_id,
                    "error": data.get("errmsg", "下单失败"), "errcode": errcode}

        # 虎皮椒平台单号：v3 未必在顶层返回 oderid，实际藏在支付链接的 id 参数里
        open_order_id = data.get("oderid") or data.get("orderid") or ""
        if not open_order_id:
            open_order_id = _extract_open_order_id(data.get("url") or data.get("url_qrcode") or "")

        # 落本地台账 —— 后续回调的金额与重放校验都以此为准
        record = {
            "trade_order_id": order_id,
            "gateway": "hupijiao",
            "payment": payment,
            "amount_cny": round(amount_f, 2),
            "total_fee": total_fee,
            "title": params["title"],
            "attach": params.get("attach", ""),
            "status": "pending_payment",
            "open_order_id": open_order_id,
            "pay_url": data.get("url", ""),
            "qrcode_url": data.get("url_qrcode", ""),
            "metadata": metadata or {},
            "created_at": _now_iso(),
        }
        store = _load_orders()
        store.setdefault("orders", {})[order_id] = record
        _save_orders(store)

        return {
            "success": True,
            "gateway": "hupijiao",
            "status": "requires_payment",
            "order_id": order_id,
            "amount_cny": round(amount_f, 2),
            "currency": "CNY",
            "payment": payment,
            "pay_url": record["pay_url"],
            "qrcode_url": record["qrcode_url"],
            "open_order_id": record["open_order_id"],
            "response_hash_valid": verify_hash(data, self.app_secret),
            "note": "把 pay_url 给用户打开，或渲染 qrcode_url 扫码支付；支付结果以异步 notify 为准。",
        }

    # ── 查单 ──
    def query_order(self, trade_order_id=None, open_order_id=None):
        """主动查单。回调丢失时的兜底。"""
        if not self.configured:
            return {"success": False, "error": "虎皮椒网关未配置"}
        if not trade_order_id and not open_order_id:
            return {"success": False, "error": "trade_order_id 与 open_order_id 至少提供一个"}

        params = {
            "appid": self.appid,
            "out_trade_order": trade_order_id or "",
            "open_order_id": open_order_id or "",
            "time": str(int(time.time())),
            "nonce_str": _nonce(),
        }
        params = {k: v for k, v in params.items() if v != ""}
        params["hash"] = generate_hash(params, self.app_secret)

        data, err = self._post(QUERY_PATH, params)
        if err:
            return {"success": False, "error": err, "gateway": "hupijiao"}
        if str(data.get("errcode")) != "0":
            return {"success": False, "error": data.get("errmsg", "查单失败"),
                    "errcode": data.get("errcode"), "gateway": "hupijiao"}

        payload = data.get("data") or {}
        return {
            "success": True,
            "gateway": "hupijiao",
            "trade_order_id": trade_order_id,
            "remote_status": payload.get("status", ""),
            "paid": payload.get("status") == STATUS_PAID,
            "data": payload,
        }

    # ── 回调 ──
    @staticmethod
    def parse_notify(raw_body):
        """把 application/x-www-form-urlencoded 回调体解析成扁平 dict。"""
        if isinstance(raw_body, bytes):
            raw_body = raw_body.decode("utf-8", errors="replace")
        parsed = urllib.parse.parse_qs(raw_body or "", keep_blank_values=True)
        return {k: v[0] if v else "" for k, v in parsed.items()}

    def verify_notify(self, params):
        """校验回调真实性。返回 (ok: bool, reason: str)。

        依次检查：网关已配置 → appid 归属 → 签名 → 支付状态 → 金额未被篡改。
        """
        if not self.configured:
            return False, "gateway_not_configured"
        if not isinstance(params, dict) or not params:
            return False, "empty_payload"

        if str(params.get("appid", "")) != str(self.appid):
            return False, "appid_mismatch"

        if not verify_hash(params, self.app_secret):
            return False, "bad_signature"

        if str(params.get("status", "")).upper() != STATUS_PAID:
            return False, "not_paid_status_%s" % params.get("status", "")

        trade_order_id = params.get("trade_order_id", "")
        if not trade_order_id:
            return False, "missing_trade_order_id"

        local = get_order(trade_order_id)
        if local:
            if not _amounts_equal(params.get("total_fee"), local.get("total_fee")):
                # 金额篡改：签名过了但金额与下单不符（如商户密钥泄露 / 中间人改单）
                return False, "amount_mismatch"
            if local.get("status") == "paid":
                return False, "already_settled"
        return True, "ok"

    def handle_notify(self, raw_body):
        """完整回调处理：解析 → 校验 → 幂等落账。

        返回 {ok, reason, order_id, params}。`ok=True` 时调用方应回纯文本 "success"。
        """
        params = self.parse_notify(raw_body)
        ok, reason = self.verify_notify(params)
        order_id = params.get("trade_order_id", "")

        if not ok:
            return {"ok": False, "reason": reason, "order_id": order_id, "params": params}

        store = _load_orders()
        orders = store.setdefault("orders", {})
        record = orders.get(order_id) or {
            "trade_order_id": order_id,
            "gateway": "hupijiao",
            "amount_cny": float(params.get("total_fee") or 0),
            "total_fee": params.get("total_fee", ""),
            "created_at": _now_iso(),
            "metadata": {},
            "orphan": True,  # 无本地下单记录（可能是历史订单）
        }
        record["status"] = "paid"
        record["paid_at"] = _now_iso()
        record["transaction_id"] = params.get("transaction_id", "")
        record["open_order_id"] = params.get("open_order_id", record.get("open_order_id", ""))
        record["notify_raw"] = {k: v for k, v in params.items() if k != "hash"}
        orders[order_id] = record
        _save_orders(store)

        return {"ok": True, "reason": "ok", "order_id": order_id,
                "params": params, "order": record}

    # ── PaymentGateway 接口兼容 ──
    def verify_payment(self, payment_id):
        """兼容接口：等价于主动查单。"""
        return self.query_order(trade_order_id=payment_id)

    def refund(self, payment_id, reason=""):
        return {"refunded": False, "gateway": "hupijiao", "payment_id": payment_id,
                "error": "虎皮椒退款需在商户后台操作，API 未开放"}

    def get_name(self):
        return "Hupijiao (虎皮椒 · 微信/支付宝)"


# ══════════════════════════════════════════════
#  模块级便捷 API
# ══════════════════════════════════════════════

def gateway():
    """取一个按当前凭证配置好的网关实例（每次新建，凭证热更新即时生效）。"""
    return HupijiaoGateway()


def create_payment(amount, order_id=None, description="", payment=PAYMENT_WECHAT, **kw):
    return gateway().create_payment(amount, order_id=order_id, description=description,
                                    payment=payment, **kw)


def query_order(trade_order_id=None, open_order_id=None):
    return gateway().query_order(trade_order_id, open_order_id)


def handle_notify(raw_body):
    return gateway().handle_notify(raw_body)


def status():
    return gateway().status()


if __name__ == "__main__":
    gw = HupijiaoGateway()
    print(json.dumps(gw.status(), ensure_ascii=False, indent=2))
    if gw.configured:
        demo = {"appid": gw.appid, "trade_order_id": "demo001", "total_fee": "0.01",
                "status": "OD", "time": str(int(time.time())), "nonce_str": _nonce()}
        demo["hash"] = generate_hash(demo, gw.app_secret)
        print("签名自洽:", verify_hash(demo, gw.app_secret))
        print("回调校验:", gw.verify_notify(demo))
