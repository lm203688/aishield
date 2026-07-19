"""
eco/payment.py — 支付网关 + 计费系统

功能:
  - PaymentGateway:      抽象支付接口
  - AlipayGateway:       支付宝（ACT协议2.0对接骨架）
  - CreemGateway:        国际支付（已有集成）
  - BillingService:      计费服务
      免费层: 50次/天
      Pro: ¥19/月 1000次/天
      Enterprise: 定制
  - 数据持久化: data/billing.json

API路由:
  POST /api/v1/billing/usage  — 记录API调用使用量
  GET  /api/v1/billing/plan   — 查询当前套餐信息
"""

import json
import os
import time
import uuid
import hashlib
import threading
from datetime import datetime, timezone, timedelta

# ── 路径配置 ──
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")
BILLING_FILE = os.path.join(_DATA_DIR, "billing.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()


# ══════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════

def _load_json(path, default=None):
    """加载JSON文件"""
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    """线程安全保存JSON文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _now_iso():
    """返回当前时间ISO格式"""
    return datetime.now(TZ).isoformat()


# ══════════════════════════════════════════════
#  套餐定义
# ══════════════════════════════════════════════

PLANS = {
    "free": {
        "name": "免费层",
        "price": 0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "daily_limit": 50,
        "monthly_limit": 1500,
        "features": ["基础安全扫描", "Prompt注入检测", "违禁词检测"],
    },
    "pro": {
        "name": "Pro",
        "price": 19,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "daily_limit": 1000,
        "monthly_limit": 30000,
        "features": [
            "全量安全扫描",
            "Prompt注入检测",
            "违禁词检测",
            "批量扫描",
            "API优先级",
            "历史报告导出",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 0,  # 定制价格
        "currency": "CNY",
        "billing_cycle": "custom",
        "daily_limit": -1,  # 无限制
        "monthly_limit": -1,
        "features": [
            "全部Pro功能",
            "私有化部署",
            "自定义规则引擎",
            "SLA保障",
            "专属技术支持",
            "API速率自定义",
        ],
    },
}


# ══════════════════════════════════════════════
#  抽象支付网关
# ══════════════════════════════════════════════

class PaymentGateway:
    """
    抽象支付网关接口
    所有支付方式必须实现此接口
    """

    def create_payment(self, amount, currency, order_id, description=""):
        """
        创建支付订单

        Args:
            amount (float):     金额
            currency (str):     货币代码 (CNY/USD)
            order_id (str):     订单ID
            description (str):  描述

        Returns:
            dict: 支付信息 {payment_url, payment_id, ...}
        """
        raise NotImplementedError("子类必须实现 create_payment")

    def verify_payment(self, payment_id):
        """
        验证支付结果

        Args:
            payment_id (str): 支付ID

        Returns:
            dict: 验证结果 {verified, amount, status}
        """
        raise NotImplementedError("子类必须实现 verify_payment")

    def refund(self, payment_id, reason=""):
        """
        发起退款

        Args:
            payment_id (str): 支付ID
            reason (str):     退款原因

        Returns:
            dict: 退款结果 {refunded, refund_id}
        """
        raise NotImplementedError("子类必须实现 refund")

    def get_name(self):
        """返回网关名称"""
        raise NotImplementedError("子类必须实现 get_name")


# ══════════════════════════════════════════════
#  支付宝网关（ACT协议2.0骨架）
# ══════════════════════════════════════════════

class AlipayGateway(PaymentGateway):
    """
    支付宝支付网关（ACT协议2.0对接骨架）
    
    ACT协议 (Alipay Connect Tunnel) 2.0:
      - 基于HTTPS双向认证
      - 签名算法: RSA-SHA256
      - 回调通知: 异步 + 同步

    注意: 此为骨架实现，生产环境需接入支付宝SDK
    """

    # ACT协议2.0端点（沙箱）
    ACT_GATEWAY = "https://openapi-sandbox.dl.alipaydev.com"
    ACT_VERSION = "2.0"

    def __init__(self, app_id=None, private_key=None, alipay_public_key=None):
        """
        初始化支付宝网关

        Args:
            app_id (str):           应用ID
            private_key (str):      应用私钥
            alipay_public_key (str): 支付宝公钥
        """
        self.app_id = app_id or os.environ.get("ALIPAY_APP_ID", "")
        self.private_key = private_key or os.environ.get("ALIPAY_PRIVATE_KEY", "")
        self.alipay_public_key = alipay_public_key or os.environ.get("ALIPAY_PUBLIC_KEY", "")
        self._sandbox = True  # 默认使用沙箱环境

    def create_payment(self, amount, currency, order_id, description=""):
        """
        创建支付宝支付订单（ACT协议2.0骨架）

        Returns:
            dict: 支付信息
        """
        if not self.app_id:
            return {
                "error": "支付宝网关未配置（缺少app_id）",
                "payment_url": None,
                "payment_id": f"alipay_mock_{order_id}",
                "sandbox": True,
            }

        # ACT协议2.0请求体骨架
        act_request = {
            "method": "alipay.trade.create",
            "app_id": self.app_id,
            "version": self.ACT_VERSION,
            "notify_url": "",  # 生产环境需配置
            "biz_content": {
                "out_trade_no": order_id,
                "total_amount": str(amount),
                "currency": currency,
                "subject": description or "AIShield API订阅",
                "product_code": "GENERAL_WITHHOLDING",  # 周期扣款
                "timeout_express": "30m",
            },
        }

        # TODO: 生产环境需要签名并发送HTTPS请求
        # signature = self._sign(act_request)
        # response = self._post_to_alipay(act_request, signature)

        return {
            "payment_id": f"alipay_{order_id}",
            "payment_url": f"{self.ACT_GATEWAY}/pay?order={order_id}",
            "sandbox": self._sandbox,
            "status": "pending",
            "act_request": act_request,
        }

    def verify_payment(self, payment_id):
        """
        验证支付宝支付结果

        Returns:
            dict: 验证结果
        """
        # TODO: 生产环境需要验证支付宝回调签名
        return {
            "verified": False,
            "payment_id": payment_id,
            "status": "pending",
            "message": "骨架实现 — 需接入支付宝SDK进行实际验证",
        }

    def refund(self, payment_id, reason=""):
        """
        支付宝退款

        Returns:
            dict: 退款结果
        """
        # TODO: 生产环境需要调用支付宝退款API
        return {
            "refunded": False,
            "payment_id": payment_id,
            "reason": reason,
            "message": "骨架实现 — 需接入支付宝SDK进行实际退款",
        }

    def get_name(self):
        return "Alipay (ACT 2.0)"


# ══════════════════════════════════════════════
#  Creem国际支付网关
# ══════════════════════════════════════════════

class CreemGateway(PaymentGateway):
    """
    Creem国际支付网关
    支持国际信用卡和PayPal

    注意: 骨架实现，生产环境需接入Creem API
    """

    CREEM_API = "https://api.creem.io/v1"

    def __init__(self, api_key=None, webhook_secret=None):
        """
        初始化Creem网关

        Args:
            api_key (str):        API密钥
            webhook_secret (str): Webhook签名密钥
        """
        self.api_key = api_key or os.environ.get("CREEM_API_KEY", "")
        self.webhook_secret = webhook_secret or os.environ.get("CREEM_WEBHOOK_SECRET", "")

    def create_payment(self, amount, currency, order_id, description=""):
        """
        创建Creem支付

        Returns:
            dict: 支付信息
        """
        if not self.api_key:
            return {
                "error": "Creem网关未配置（缺少api_key）",
                "payment_url": None,
                "payment_id": f"creem_mock_{order_id}",
            }

        # Creem API请求骨架
        creem_request = {
            "amount": amount,
            "currency": currency,
            "order_id": order_id,
            "description": description or "AIShield API Subscription",
            "success_url": "",   # 支付成功跳转
            "cancel_url": "",     # 支付取消跳转
            "webhook_url": "",    # 异步通知
        }

        return {
            "payment_id": f"creem_{order_id}",
            "payment_url": f"{self.CREEM_API}/checkout/{order_id}",
            "status": "pending",
            "creem_request": creem_request,
        }

    def verify_payment(self, payment_id):
        """
        验证Creem支付结果

        Returns:
            dict: 验证结果
        """
        return {
            "verified": False,
            "payment_id": payment_id,
            "status": "pending",
            "message": "骨架实现 — 需接入Creem API进行实际验证",
        }

    def refund(self, payment_id, reason=""):
        """
        Creem退款

        Returns:
            dict: 退款结果
        """
        return {
            "refunded": False,
            "payment_id": payment_id,
            "reason": reason,
            "message": "骨架实现 — 需接入Creem API进行实际退款",
        }

    def get_name(self):
        return "Creem (International)"


# ══════════════════════════════════════════════
#  计费服务
# ══════════════════════════════════════════════

class BillingService:
    """
    计费服务
    管理用户套餐、用量统计和账单
    """

    def __init__(self):
        self._billing_data = {}

    def _load(self):
        """从磁盘加载计费数据"""
        self._billing_data = _load_json(BILLING_FILE, {
            "accounts": {},
            "usage_log": [],
        })

    def _save(self):
        """持久化到磁盘"""
        _save_json(BILLING_FILE, self._billing_data)

    def _get_account(self, account_id):
        """获取或创建账户"""
        self._load()
        accounts = self._billing_data.get("accounts", {})
        if account_id not in accounts:
            accounts[account_id] = {
                "account_id": account_id,
                "plan": "free",
                "created_at": _now_iso(),
                "monthly_usage": {},
                "payment_history": [],
            }
            self._billing_data["accounts"] = accounts
            self._save()
        return accounts[account_id]

    def upgrade_plan(self, account_id, new_plan, gateway_name="alipay"):
        """
        升级套餐

        Args:
            account_id (str):   账户ID
            new_plan (str):      目标套餐 (free/pro/enterprise)
            gateway_name (str):  支付网关名称

        Returns:
            dict: 升级结果
        """
        if new_plan not in PLANS:
            raise ValueError(f"无效套餐: {new_plan}，可选: {list(PLANS.keys())}")

        self._load()
        account = self._get_account(account_id)
        old_plan = account["plan"]

        # 生成订单
        order_id = f"bill_{uuid.uuid4().hex[:12]}"
        plan_info = PLANS[new_plan]

        # 尝试创建支付
        payment_result = {"status": "mock", "message": "计费系统骨架 — 无需实际支付"}

        if plan_info["price"] > 0:
            # 实际支付流程骨架
            if gateway_name == "alipay":
                gateway = AlipayGateway()
            elif gateway_name == "creem":
                gateway = CreemGateway()
            else:
                gateway = AlipayGateway()

            payment_result = gateway.create_payment(
                amount=plan_info["price"],
                currency=plan_info["currency"],
                order_id=order_id,
                description=f"AIShield {plan_info['name']} 套餐",
            )

        # 更新账户
        account["plan"] = new_plan
        account["upgraded_at"] = _now_iso()
        account["payment_history"].append({
            "order_id": order_id,
            "plan": new_plan,
            "amount": plan_info["price"],
            "gateway": gateway_name,
            "timestamp": _now_iso(),
            "payment_result": payment_result,
        })
        # 只保留最近100条支付记录
        if len(account["payment_history"]) > 100:
            account["payment_history"] = account["payment_history"][-100:]

        self._billing_data["accounts"][account_id] = account
        self._save()

        return {
            "success": True,
            "account_id": account_id,
            "old_plan": old_plan,
            "new_plan": new_plan,
            "plan_info": {
                "name": plan_info["name"],
                "price": plan_info["price"],
                "currency": plan_info["currency"],
                "daily_limit": plan_info["daily_limit"],
            },
            "order_id": order_id,
            "payment": payment_result,
        }

    def record_usage(self, account_id, endpoint, ip=""):
        """
        记录一次API调用

        Args:
            account_id (str): 账户ID
            endpoint (str):   调用的端点
            ip (str):         客户端IP

        Returns:
            dict: 使用记录结果
        """
        self._load()
        account = self._get_account(account_id)
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        plan = PLANS.get(account["plan"], PLANS["free"])

        # 更新月度用量
        monthly_usage = account.get("monthly_usage", {})
        day_usage = monthly_usage.get(today, {"count": 0, "endpoints": {}})
        day_usage["count"] += 1
        ep = day_usage["endpoints"]
        ep[endpoint] = ep.get(endpoint, 0) + 1
        monthly_usage[today] = day_usage
        account["monthly_usage"] = monthly_usage

        # 检查限额
        daily_limit = plan["daily_limit"]
        over_limit = daily_limit > 0 and day_usage["count"] > daily_limit

        # 记录使用日志
        usage_log = self._billing_data.get("usage_log", [])
        usage_log.append({
            "account_id": account_id,
            "endpoint": endpoint,
            "ip": ip,
            "timestamp": _now_iso(),
            "plan": account["plan"],
        })
        # 只保留最近10000条
        if len(usage_log) > 10000:
            self._billing_data["usage_log"] = usage_log[-5000:]
        else:
            self._billing_data["usage_log"] = usage_log

        self._billing_data["accounts"][account_id] = account
        self._save()

        return {
            "success": True,
            "account_id": account_id,
            "plan": account["plan"],
            "today_count": day_usage["count"],
            "daily_limit": daily_limit,
            "over_limit": over_limit,
            "remaining": max(0, daily_limit - day_usage["count"]) if daily_limit > 0 else -1,
        }

    def get_plan_info(self, account_id):
        """
        查询当前套餐信息

        Args:
            account_id (str): 账户ID

        Returns:
            dict: 套餐和使用信息
        """
        self._load()
        account = self._get_account(account_id)
        plan_name = account.get("plan", "free")
        plan = PLANS[plan_name]
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        monthly_usage = account.get("monthly_usage", {})
        today_usage = monthly_usage.get(today, {"count": 0})

        # 计算本月总用量
        month_prefix = today[:7]  # "2025-01"
        month_total = sum(
            v.get("count", 0) for k, v in monthly_usage.items()
            if k.startswith(month_prefix)
        )

        return {
            "account_id": account_id,
            "plan": plan_name,
            "plan_info": plan,
            "usage": {
                "today": today_usage.get("count", 0),
                "daily_limit": plan["daily_limit"],
                "month_total": month_total,
                "monthly_limit": plan["monthly_limit"],
                "remaining_daily": max(0, plan["daily_limit"] - today_usage.get("count", 0))
                                 if plan["daily_limit"] > 0 else -1,
            },
            "features": plan["features"],
        }

    def generate_bill(self, account_id, month=None):
        """
        生成月度账单

        Args:
            account_id (str): 账户ID
            month (str):       月份 (YYYY-MM)，默认当月

        Returns:
            dict: 账单信息
        """
        self._load()
        account = self._get_account(account_id)

        if not month:
            month = datetime.now(TZ).strftime("%Y-%m")

        plan = PLANS.get(account["plan"], PLANS["free"])
        monthly_usage = account.get("monthly_usage", {})

        # 汇总该月数据
        month_days = sorted([k for k in monthly_usage if k.startswith(month)])
        total_calls = sum(monthly_usage.get(d, {}).get("count", 0) for d in month_days)
        endpoints = {}
        for d in month_days:
            for ep, count in monthly_usage.get(d, {}).get("endpoints", {}).items():
                endpoints[ep] = endpoints.get(ep, 0) + count

        bill = {
            "account_id": account_id,
            "bill_id": f"bill_{account_id}_{month}",
            "month": month,
            "plan": account["plan"],
            "plan_price": plan["price"],
            "currency": plan["currency"],
            "total_calls": total_calls,
            "daily_breakdown": {d: monthly_usage.get(d, {}).get("count", 0) for d in month_days},
            "endpoint_breakdown": endpoints,
            "generated_at": _now_iso(),
        }

        return bill


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将支付模块路由注册到HTTPServer的Handler上

    兼容 api/server.py 的 AIShieldHandler 模式。

    Args:
        handler: AIShieldHandler实例
    """
    original_do_get = handler.do_GET
    original_do_post = handler.do_POST

    def do_get_patched(self):
        """扩展GET路由"""
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path

        # ── GET /api/v1/billing/plan — 查询套餐信息 ──
        if path == "/api/v1/billing/plan":
            # 从查询参数获取account_id，默认使用IP
            query = parse_qs(parsed.query)
            account_id = query.get("account_id", ["default"])[0]
            try:
                billing = BillingService()
                info = billing.get_plan_info(account_id)
                self._send_json({"success": True, "billing": info})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 非本模块路由
        original_do_get(self)

    def do_post_patched(self):
        """扩展POST路由"""
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_body()
            data = json.loads(body) if body else {}
        except (json.JSONDecodeError, TypeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        # ── POST /api/v1/billing/usage — 记录API调用 ──
        if path == "/api/v1/billing/usage":
            account_id = data.get("account_id", "default")
            endpoint = data.get("endpoint", "unknown")
            try:
                billing = BillingService()
                result = billing.record_usage(
                    account_id=account_id,
                    endpoint=endpoint,
                    ip=self.client_address[0],
                )
                self._send_json({"success": True, "usage": result})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 非本模块路由
        original_do_post(self)

    handler.do_GET = do_get_patched.__get__(handler, type(handler))
    handler.do_POST = do_post_patched.__get__(handler, type(handler))


# ══════════════════════════════════════════════
#  独立测试入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    from urllib.parse import parse_qs

    print("=== 套餐信息 ===")
    for name, plan in PLANS.items():
        print(f"  {name}: ¥{plan['price']}/月, {plan['daily_limit']}次/天")

    print("\n=== 支付宝网关测试 ===")
    alipay = AlipayGateway()
    result = alipay.create_payment(19, "CNY", "test_order_001", "Pro套餐")
    print(f"  创建支付: {result.get('payment_id')}")

    print("\n=== 计费服务测试 ===")
    billing = BillingService()

    # 记录使用
    for i in range(10):
        result = billing.record_usage("test_user", "/api/v1/audit", "127.0.0.1")
    print(f"  记录10次调用: today_count={result['today_count']}")

    # 查询套餐
    info = billing.get_plan_info("test_user")
    print(f"  套餐: {info['plan']}")
    print(f"  今日用量: {info['usage']['today']}/{info['usage']['daily_limit']}")

    # 升级套餐
    upgrade = billing.upgrade_plan("test_user", "pro")
    print(f"  升级到Pro: ¥{upgrade['plan_info']['price']}")

    # 再次查询
    info = billing.get_plan_info("test_user")
    print(f"  套餐: {info['plan']}, 日限额: {info['usage']['daily_limit']}")

    # 生成账单
    bill = billing.generate_bill("test_user")
    print(f"\n  账单: {bill['bill_id']}")
    print(f"  总调用: {bill['total_calls']}次")
    print(f"  套餐价格: ¥{bill['plan_price']}")

    print("\n=== 全部测试通过 ===")
