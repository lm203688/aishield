"""
eco/auth_provider.py — 增强身份认证

功能:
  - APIKeyManager: API密钥管理
      generate_key / verify_key / revoke_key / list_keys / check_rate_limit
      key格式: ask_live_32位hex
      存储SHA256哈希，明文只返回一次
  - ScopeManager: 权限作用域管理
      validate_scopes / check_access
      支持通配符 (scan:*)
  - AuditLogger: 审计日志
      log_event / query_events
  - 数据持久化: api/data/auth_api_keys.json
                 api/data/auth_audit.json
  - 线程安全: threading.Lock
  - OAuth部分暂留TODO

API路由:
  POST /api/v1/auth/keys                  — 生成API Key
  POST /api/v1/auth/keys/verify           — 验证API Key
  POST /api/v1/auth/keys/{key_id}/revoke  — 撤销API Key
  GET  /api/v1/auth/keys                  — 列出API Key
  POST /api/v1/auth/keys/check-rate       — 检查速率限制
  POST /api/v1/auth/scopes/validate       — 验证作用域
  POST /api/v1/auth/scopes/check          — 检查访问权限
  POST /api/v1/auth/audit/log             — 记录审计事件
  GET  /api/v1/auth/audit/query           — 查询审计日志
"""

import json
import os
import time
import uuid
import hashlib
import threading
from datetime import datetime, timezone, timedelta

# ── 路径配置 ──
# 数据目录: api/data/（相对于项目根目录）
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")
API_KEYS_FILE = os.path.join(_DATA_DIR, "auth_api_keys.json")
OAUTH_FILE = os.path.join(_DATA_DIR, "auth_oauth.json")
AUDIT_FILE = os.path.join(_DATA_DIR, "auth_audit.json")

TZ = timezone(timedelta(hours=8))


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
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(_DATA_DIR, exist_ok=True)


def _now_iso():
    """返回当前时间的ISO格式字符串"""
    return datetime.now(TZ).isoformat()


# ══════════════════════════════════════════════
#  ScopeManager — 权限作用域管理
# ══════════════════════════════════════════════

# 预定义权限作用域
SCOPES = {
    # 扫描相关
    "scan:read":       "读取扫描配置和结果",
    "scan:execute":    "执行安全扫描",
    "scan:admin":      "管理扫描配置",
    # 协作相关
    "collab:publish":  "发布协作消息",
    "collab:subscribe": "订阅协作频道",
    "collab:admin":    "管理协作配置",
    # 技能相关
    "skill:invoke":    "调用技能",
    "skill:register":  "注册技能",
    "skill:admin":     "管理技能",
    # 沙箱相关
    "sandbox:execute": "执行沙箱命令",
    "sandbox:admin":   "管理沙箱",
    # 计费相关
    "billing:read":    "查看账单",
    "billing:write":   "修改账单/充值",
    # 认证相关
    "auth:admin":      "管理认证配置",
    "auth:keys":       "管理API密钥",
    # 身份相关
    "identity:read":   "读取身份信息",
    "identity:write":  "修改身份信息",
}


class ScopeManager:
    """
    权限作用域管理器
    验证和检查API访问权限
    """

    def validate_scopes(self, requested):
        """
        验证请求的作用域是否合法

        Args:
            requested (list): 请求的作用域列表

        Returns:
            tuple: (valid, valid_list, invalid_list)
                valid (bool):       是否全部合法
                valid_list (list):  合法的作用域
                invalid_list (list): 不合法的作用域
        """
        valid_list = []
        invalid_list = []

        for scope in requested:
            if self._is_valid_scope(scope):
                valid_list.append(scope)
            else:
                invalid_list.append(scope)

        return (len(invalid_list) == 0, valid_list, invalid_list)

    def check_access(self, token_scopes, required):
        """
        检查令牌是否具有所需权限

        支持通配符匹配，例如 token_scopes 包含 "scan:*" 则匹配所有 scan: 前缀的权限

        Args:
            token_scopes (list): 令牌持有的作用域列表
            required (str):      所需的作用域

        Returns:
            bool: 是否有权限
        """
        if required in token_scopes:
            return True

        # 通配符匹配
        required_prefix = required.split(":")[0] + ":*"
        if required_prefix in token_scopes:
            return True

        # 检查required是否是某个通配符的子集
        for ts in token_scopes:
            if ts.endswith(":*"):
                prefix = ts.split(":")[0] + ":"
                if required.startswith(prefix):
                    return True

        return False

    @staticmethod
    def _is_valid_scope(scope):
        """
        检查单个作用域是否在预定义列表中

        Args:
            scope (str): 作用域名称

        Returns:
            bool: 是否合法
        """
        if scope in SCOPES:
            return True
        # 通配符形式: resource:*
        if scope.endswith(":*"):
            prefix = scope.split(":")[0] + ":"
            for s in SCOPES:
                if s.startswith(prefix):
                    return True
        return False


# ══════════════════════════════════════════════
#  APIKeyManager — API密钥管理
# ══════════════════════════════════════════════

class APIKeyManager:
    """
    API密钥管理器
    支持密钥生成、验证、撤销和速率限制
    密钥格式: ask_live_<32位hex>
    存储SHA256哈希，明文只在生成时返回一次
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._scope_manager = ScopeManager()

    def _load(self):
        """从磁盘加载密钥数据"""
        raw = _load_json(API_KEYS_FILE, {"keys": {}})
        self._keys = raw.get("keys", {})

    def _save(self):
        """持久化数据到磁盘"""
        _ensure_data_dir()
        _save_json(API_KEYS_FILE, {"keys": self._keys})

    @staticmethod
    def _hash_key(api_key):
        """
        计算API密钥的SHA256哈希

        Args:
            api_key (str): 原始API密钥

        Returns:
            str: SHA256哈希值
        """
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    def generate_key(self, agent_id, key_name, scopes=None,
                     rate_limit=1000, expires_in_days=None):
        """
        生成新的API密钥

        Args:
            agent_id (str):         所属Agent ID
            key_name (str):         密钥名称
            scopes (list, opt):     权限作用域列表
            rate_limit (int):       速率限制（次/分钟）
            expires_in_days (int, opt): 过期天数

        Returns:
            dict: {"key_id", "api_key", "name", "scopes"}
        """
        self._load()

        # 验证作用域
        if scopes:
            valid, valid_list, invalid_list = self._scope_manager.validate_scopes(scopes)
            if not valid:
                raise ValueError(f"无效的作用域: {invalid_list}")
            scopes = valid_list

        key_id = f"ask_{uuid.uuid4().hex[:12]}"
        raw_key = f"ask_live_{uuid.uuid4().hex}"
        key_hash = self._hash_key(raw_key)

        now = datetime.now(TZ)
        expires_at = None
        if expires_in_days:
            expires_at = (now + timedelta(days=expires_in_days)).isoformat()

        key_info = {
            "key_id": key_id,
            "agent_id": agent_id,
            "name": key_name,
            "key_hash": key_hash,
            "scopes": scopes or [],
            "rate_limit": rate_limit,
            "rate_counter": 0,
            "rate_window_start": _now_iso(),
            "status": "active",
            "expires_at": expires_at,
            "created_at": _now_iso(),
            "last_used_at": None,
        }

        self._keys[key_id] = key_info
        self._save()

        return {
            "key_id": key_id,
            "api_key": raw_key,
            "name": key_name,
            "scopes": scopes or [],
            "expires_at": expires_at,
        }

    def verify_key(self, api_key):
        """
        验证API密钥

        Args:
            api_key (str): 待验证的API密钥

        Returns:
            dict | None: {"key_id", "agent_id", "name", "scopes"} 验证失败返回None
        """
        self._load()

        key_hash = self._hash_key(api_key)

        for key_id, key_info in self._keys.items():
            if key_info["key_hash"] == key_hash:
                # 检查状态
                if key_info["status"] != "active":
                    return None
                # 检查过期
                if key_info.get("expires_at"):
                    expires = datetime.fromisoformat(key_info["expires_at"])
                    if datetime.now(TZ) > expires:
                        return None
                # 更新最后使用时间
                key_info["last_used_at"] = _now_iso()
                self._save()

                return {
                    "key_id": key_id,
                    "agent_id": key_info["agent_id"],
                    "name": key_info["name"],
                    "scopes": key_info["scopes"],
                }

        return None

    def revoke_key(self, key_id, agent_id):
        """
        撤销API密钥

        Args:
            key_id (str):    密钥ID
            agent_id (str):  所属Agent ID

        Returns:
            bool: 是否撤销成功
        """
        self._load()

        key_info = self._keys.get(key_id)
        if not key_info:
            return False
        if key_info["agent_id"] != agent_id:
            return False
        if key_info["status"] != "active":
            return False

        key_info["status"] = "revoked"
        key_info["revoked_at"] = _now_iso()

        self._save()
        return True

    def list_keys(self, agent_id):
        """
        列出Agent的所有API密钥（不含明文key）

        Args:
            agent_id (str): Agent ID

        Returns:
            list: 密钥信息列表
        """
        self._load()

        result = []
        for key_info in self._keys.values():
            if key_info["agent_id"] == agent_id:
                # 返回时排除 key_hash
                info = {k: v for k, v in key_info.items() if k != "key_hash"}
                result.append(info)

        return result

    def check_rate_limit(self, key_id):
        """
        检查速率限制

        Args:
            key_id (str): 密钥ID

        Returns:
            tuple: (allowed, remaining)
                allowed (bool):   是否允许
                remaining (int):  剩余可用次数
        """
        self._load()

        key_info = self._keys.get(key_id)
        if not key_info or key_info["status"] != "active":
            return (False, 0)

        rate_limit = key_info.get("rate_limit", 1000)
        counter = key_info.get("rate_counter", 0)
        window_start = key_info.get("rate_window_start", _now_iso())

        # 检查窗口是否已过期（1分钟窗口）
        window_time = datetime.fromisoformat(window_start)
        now = datetime.now(TZ)
        if (now - window_time).total_seconds() > 60:
            # 重置窗口
            key_info["rate_counter"] = 1
            key_info["rate_window_start"] = _now_iso()
            self._save()
            return (True, rate_limit - 1)

        # 检查是否超限
        if counter >= rate_limit:
            return (False, 0)

        # 递增计数
        key_info["rate_counter"] = counter + 1
        remaining = rate_limit - key_info["rate_counter"]
        self._save()

        return (True, remaining)


# ══════════════════════════════════════════════
#  AuditLogger — 审计日志
# ══════════════════════════════════════════════

class AuditLogger:
    """
    审计日志记录器
    记录和查询认证相关事件
    """

    def __init__(self):
        self._lock = threading.Lock()

    def _load(self):
        """从磁盘加载审计日志"""
        raw = _load_json(AUDIT_FILE, {"events": []})
        self._events = raw.get("events", [])

    def _save(self):
        """持久化数据到磁盘"""
        _ensure_data_dir()
        _save_json(AUDIT_FILE, {"events": self._events})

    def log_event(self, event_type, agent_id, details=None, ip=None):
        """
        记录审计事件

        Args:
            event_type (str):       事件类型 (login/logout/key_generate/key_revoke/...)
            agent_id (str):         关联Agent ID
            details (dict, opt):    事件详情
            ip (str, opt):          客户端IP
        """
        self._load()

        event = {
            "event_id": f"aud_{uuid.uuid4().hex[:16]}",
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details or {},
            "ip": ip,
            "created_at": _now_iso(),
        }

        self._events.append(event)

        # 保留最近10000条记录，防止文件过大
        if len(self._events) > 10000:
            self._events = self._events[-10000:]

        self._save()

    def query_events(self, agent_id=None, event_type=None, limit=100):
        """
        查询审计事件

        Args:
            agent_id (str, opt):    按Agent ID筛选
            event_type (str, opt):  按事件类型筛选
            limit (int):            最大返回条数

        Returns:
            list: 事件列表（按时间倒序）
        """
        self._load()

        result = self._events.copy()

        if agent_id:
            result = [e for e in result if e.get("agent_id") == agent_id]
        if event_type:
            result = [e for e in result if e.get("event_type") == event_type]

        # 按时间倒序
        result.reverse()

        return result[:limit]


# ══════════════════════════════════════════════
#  OAuth（TODO: 待实现）
# ══════════════════════════════════════════════

# TODO: OAuth2.0 授权码流程
#   - authorize_url(client_id, redirect_uri, scope, state) → str
#   - exchange_code(code, client_id, client_secret) → {"access_token", "refresh_token", "expires_in"}
#   - refresh_token(refresh_token, client_id, client_secret) → {"access_token", "expires_in"}
#   - revoke_token(token) → bool
# 数据文件: auth_oauth.json
# 参考标准: RFC 6749 (OAuth 2.0)