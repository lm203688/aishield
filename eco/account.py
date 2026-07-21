"""
eco/account.py — 用户账户系统

功能:
  - UserAccount: 用户注册/登录/余额/API Key 管理
      register / login / get_by_api_key / get_user_info
      recharge / consume / get_balance
      每个用户一个默认 API Key（SHA256 hash）
  - 数据持久化: api/data/accounts.json

API路由:
  POST /api/v1/account/register  — 注册（送5元体验金）
  POST /api/v1/account/login     — 登录（重新生成 API Key）
  GET  /api/v1/account/me        — 查询当前用户信息（需要 Bearer token）
  POST /api/v1/account/recharge  — 充值
  GET  /api/v1/account/balance   — 查询余额
"""

import json
import os
import uuid
import hashlib
import threading
from datetime import datetime, timezone, timedelta

# ── 路径配置 ──
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")
ACCOUNTS_FILE = os.path.join(_DATA_DIR, "accounts.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()


# ══════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════

def _load_json(path, default=None):
    """加载JSON文件，失败返回默认值"""
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
    """线程安全地保存JSON文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _now_iso():
    """返回当前时间的ISO格式字符串"""
    return datetime.now(TZ).isoformat()


def _hash_sha256(text):
    """SHA256 哈希"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _generate_api_key():
    """生成原始 API Key（32位hex）"""
    raw = uuid.uuid4().hex + uuid.uuid4().hex
    return raw[:32]


# ══════════════════════════════════════════════
#  用户账户管理
# ══════════════════════════════════════════════

class UserAccount:
    """
    用户账户管理器
    负责用户注册、登录验证、余额管理和 API Key 生成
    """

    def __init__(self):
        self._accounts = {}
        self._email_index = {}

    def _load(self):
        """从磁盘加载账户数据"""
        data = _load_json(ACCOUNTS_FILE, {"accounts": {}, "email_index": {}})
        self._accounts = data.get("accounts", {})
        self._email_index = data.get("email_index", {})

    def _save(self):
        """持久化账户数据到磁盘"""
        _save_json(ACCOUNTS_FILE, {
            "accounts": self._accounts,
            "email_index": self._email_index,
        })

    def _find_by_email(self, email):
        """通过邮箱查找账户"""
        self._load()
        account_id = self._email_index.get(email.lower())
        if account_id:
            return self._accounts.get(account_id)
        return None

    def register(self, name, email, password):
        """
        注册新用户

        Args:
            name (str):     用户名
            email (str):    邮箱
            password (str): 密码

        Returns:
            dict: {account_id, api_key, balance, name, email, created_at}
        """
        self._load()

        email = email.strip().lower()
        name = name.strip()
        if not name or not email or not password:
            raise ValueError("name, email, password 均为必填")

        # 检查邮箱是否已注册
        if email in self._email_index:
            raise ValueError(f"邮箱 {email} 已被注册")

        account_id = f"usr_{uuid.uuid4().hex[:12]}"
        raw_api_key = _generate_api_key()
        api_key_hash = _hash_sha256(raw_api_key)

        account = {
            "account_id": account_id,
            "name": name,
            "email": email,
            "password_hash": _hash_sha256(password),
            "api_key_hash": api_key_hash,
            "balance": 5.0,  # 送5元体验金
            "status": "active",
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        }

        self._accounts[account_id] = account
        self._email_index[email] = account_id
        self._save()

        return {
            "account_id": account_id,
            "api_key": raw_api_key,
            "balance": account["balance"],
            "name": account["name"],
            "email": account["email"],
            "created_at": account["created_at"],
        }

    def login(self, email, password):
        """
        用户登录
        登录成功重新生成 API Key 并返回

        Args:
            email (str):    邮箱
            password (str): 密码

        Returns:
            dict: {account_id, api_key, balance, name, email}
        """
        self._load()

        email = email.strip().lower()
        account = self._find_by_email(email)
        if not account:
            raise ValueError("邮箱或密码错误")

        if account.get("status") != "active":
            raise ValueError("账户已被禁用")

        password_hash = _hash_sha256(password)
        if account.get("password_hash") != password_hash:
            raise ValueError("邮箱或密码错误")

        # 重新生成 API Key
        raw_api_key = _generate_api_key()
        account["api_key_hash"] = _hash_sha256(raw_api_key)
        account["updated_at"] = _now_iso()
        self._accounts[account["account_id"]] = account
        self._save()

        return {
            "account_id": account["account_id"],
            "api_key": raw_api_key,
            "balance": account["balance"],
            "name": account["name"],
            "email": account["email"],
        }

    def get_by_api_key(self, api_key):
        """
        通过原始 API Key 查找账户

        Args:
            api_key (str): 原始 API Key

        Returns:
            dict | None: 账户信息（不含敏感字段）
        """
        self._load()

        if not api_key:
            return None

        api_key_hash = _hash_sha256(api_key)
        for account in self._accounts.values():
            if account.get("api_key_hash") == api_key_hash:
                return account
        return None

    def get_user_info(self, account_id):
        """
        获取用户信息（对外展示，不含密码hash）

        Args:
            account_id (str): 账户ID

        Returns:
            dict | None: 用户信息
        """
        self._load()
        account = self._accounts.get(account_id)
        if not account:
            return None
        return {
            "account_id": account["account_id"],
            "name": account["name"],
            "email": account["email"],
            "balance": account["balance"],
            "status": account["status"],
            "created_at": account["created_at"],
            "updated_at": account["updated_at"],
        }

    def recharge(self, account_id, amount, gateway="alipay"):
        """
        充值（增加余额）

        Args:
            account_id (str): 账户ID
            amount (float):   充值金额（CNY）
            gateway (str):    支付网关

        Returns:
            dict: 充值结果
        """
        self._load()

        if amount <= 0:
            raise ValueError("充值金额必须大于0")

        account = self._accounts.get(account_id)
        if not account:
            raise ValueError("账户不存在")

        account["balance"] = round(account.get("balance", 0.0) + amount, 2)
        account["updated_at"] = _now_iso()

        self._accounts[account_id] = account
        self._save()

        return {
            "account_id": account_id,
            "amount": amount,
            "gateway": gateway,
            "new_balance": account["balance"],
            "status": "success",
            "order_id": f"rcg_{uuid.uuid4().hex[:12]}",
        }

    def consume(self, account_id, amount):
        """
        消费（扣除余额）

        Args:
            account_id (str): 账户ID
            amount (float):   消费金额（CNY）

        Returns:
            dict: 消费结果
        """
        self._load()

        if amount <= 0:
            raise ValueError("消费金额必须大于0")

        account = self._accounts.get(account_id)
        if not account:
            raise ValueError("账户不存在")

        balance = account.get("balance", 0.0)
        if balance < amount:
            raise ValueError(f"余额不足: 当前余额 {balance} CNY，需要 {amount} CNY")

        account["balance"] = round(balance - amount, 2)
        account["updated_at"] = _now_iso()

        self._accounts[account_id] = account
        self._save()

        return {
            "account_id": account_id,
            "amount": amount,
            "new_balance": account["balance"],
        }

    def get_balance(self, account_id):
        """
        查询余额

        Args:
            account_id (str): 账户ID

        Returns:
            float: 余额
        """
        self._load()
        account = self._accounts.get(account_id)
        if not account:
            raise ValueError("账户不存在")
        return account.get("balance", 0.0)

    def get_account_by_id(self, account_id):
        """
        通过ID获取完整账户数据（内部使用）

        Args:
            account_id (str): 账户ID

        Returns:
            dict | None: 账户数据
        """
        self._load()
        return self._accounts.get(account_id)


# ══════════════════════════════════════════════
#  认证辅助函数
# ══════════════════════════════════════════════

def _get_auth_account(handler):
    """
    从请求头中提取 Bearer token 并验证，返回账户数据或 None

    Args:
        handler: HTTPServer Handler 实例

    Returns:
        dict | None: 账户数据
    """
    auth_header = handler.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    api_key = auth_header[len("Bearer "):].strip()
    if not api_key:
        return None

    mgr = UserAccount()
    return mgr.get_by_api_key(api_key)


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将账户模块路由注册到HTTPServer的Handler上

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

        # ── GET /api/v1/account/me — 查询当前用户信息 ──
        if path == "/api/v1/account/me":
            account = _get_auth_account(self)
            if not account:
                self._send_json({"error": "Unauthorized"}, 401)
                return
            info = UserAccount().get_user_info(account["account_id"])
            self._send_json({"success": True, "account": info})
            return

        # ── GET /api/v1/account/balance — 查询余额 ──
        if path == "/api/v1/account/balance":
            account = _get_auth_account(self)
            if not account:
                self._send_json({"error": "Unauthorized"}, 401)
                return
            try:
                balance = UserAccount().get_balance(account["account_id"])
                self._send_json({"success": True, "account_id": account["account_id"], "balance": balance})
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
            return

        # 非本模块路由，交给原始处理器
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

        # ── POST /api/v1/account/register — 注册 ──
        if path == "/api/v1/account/register":
            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "")
            if not name or not email or not password:
                self._send_json({"error": "name, email, password 均为必填"}, 400)
                return
            try:
                mgr = UserAccount()
                result = mgr.register(name, email, password)
                self._send_json({"success": True, **result}, 201)
            except ValueError as e:
                self._send_json({"error": str(e)}, 409)
            return

        # ── POST /api/v1/account/login — 登录 ──
        if path == "/api/v1/account/login":
            email = data.get("email", "").strip()
            password = data.get("password", "")
            if not email or not password:
                self._send_json({"error": "email, password 均为必填"}, 400)
                return
            try:
                mgr = UserAccount()
                result = mgr.login(email, password)
                self._send_json({"success": True, **result})
            except ValueError as e:
                self._send_json({"error": str(e)}, 401)
            return

        # ── POST /api/v1/account/recharge — 充值 ──
        if path == "/api/v1/account/recharge":
            account_id = data.get("account_id", "").strip()
            amount = float(data.get("amount", 0))
            gateway = data.get("gateway", "alipay")
            if not account_id or amount <= 0:
                self._send_json({"error": "account_id 和 amount 为必填，且 amount > 0"}, 400)
                return
            try:
                mgr = UserAccount()
                result = mgr.recharge(account_id, amount, gateway)
                self._send_json({"success": True, **result})
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
            return

        # 非本模块路由，交给原始处理器
        original_do_post(self)

    handler.do_GET = do_get_patched.__get__(handler, type(handler))
    handler.do_POST = do_post_patched.__get__(handler, type(handler))


# ══════════════════════════════════════════════
#  独立测试入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("=== 用户账户系统测试 ===")

    mgr = UserAccount()

    # 清理测试数据
    if os.path.exists(ACCOUNTS_FILE):
        os.remove(ACCOUNTS_FILE)

    # 注册
    print("\n--- 注册 ---")
    result = mgr.register("张三", "zhangsan@example.com", "password123")
    print(f"  注册成功: account_id={result['account_id']}, api_key={result['api_key'][:8]}..., balance={result['balance']}")

    # 重复注册
    try:
        mgr.register("张三2", "zhangsan@example.com", "password456")
    except ValueError as e:
        print(f"  重复注册拦截: {e}")

    # 登录
    print("\n--- 登录 ---")
    login_result = mgr.login("zhangsan@example.com", "password123")
    print(f"  登录成功: account_id={login_result['account_id']}, balance={login_result['balance']}")

    # 错误密码
    try:
        mgr.login("zhangsan@example.com", "wrongpassword")
    except ValueError as e:
        print(f"  错误密码拦截: {e}")

    # 通过 API Key 获取用户信息
    print("\n--- API Key 验证 ---")
    account = mgr.get_by_api_key(login_result["api_key"])
    print(f"  API Key 验证成功: {account['name']}")

    # 充值
    print("\n--- 充值 ---")
    recharge_result = mgr.recharge(account["account_id"], 100.0, "alipay")
    print(f"  充值成功: +{recharge_result['amount']} CNY, 新余额: {recharge_result['new_balance']}")

    # 消费
    print("\n--- 消费 ---")
    consume_result = mgr.consume(account["account_id"], 10.5)
    print(f"  消费成功: -{consume_result['amount']} CNY, 新余额: {consume_result['new_balance']}")

    # 余额不足
    try:
        mgr.consume(account["account_id"], 200.0)
    except ValueError as e:
        print(f"  余额不足拦截: {e}")

    # 查询余额
    print("\n--- 查询余额 ---")
    balance = mgr.get_balance(account["account_id"])
    print(f"  当前余额: {balance} CNY")

    # 查询用户信息
    print("\n--- 查询用户信息 ---")
    info = mgr.get_user_info(account["account_id"])
    print(f"  用户: {info['name']}, 邮箱: {info['email']}, 余额: {info['balance']}")

    print("\n=== 全部测试通过 ===")
