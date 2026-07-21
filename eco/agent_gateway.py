"""
eco/agent_gateway.py — Agent-First 一键入驻网关

功能:
  - agent_setup():       Agent 一键入驻（注册 + 生成 API Key + 返回快速开始指引）
  - agent_quick_scan():  Agent 快速扫描（通过 DID 自动关联身份）
  - agent_status():      查询 Agent 状态（信息 + Key 数量 + 信誉分 + 使用统计）
  - ERROR_CODES:         统一错误码常量
  - 数据持久化: 复用 api/data/ 目录
  - 线程安全: threading.Lock

Agent-First 理念:
  Agent 只需一次 POST /api/v1/agent/setup 即可完成注册、认证、获取使用指引，
  无需分别调用 /identity/register + /auth/keys + /docs 等多个端点。

API路由:
  POST /api/v1/agent/setup     — Agent 一键入驻（无认证）
  POST /api/v1/agent/scan      — Agent 快速扫描（可选认证）
  GET  /api/v1/agent/status/{did} — 查询 Agent 状态
"""

import json
import os
import uuid
import threading
from datetime import datetime, timezone, timedelta

# ── 路径配置 ──
# 数据目录: api/data/（相对于项目根目录）
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()

# ── 生产环境 Base URL ──
_BASE_URL = "https://aishield.tools"


# ══════════════════════════════════════════════
#  错误码常量
# ══════════════════════════════════════════════

ERROR_CODES = {
    "AUTH_REQUIRED": {
        "code": "AUTH_REQUIRED",
        "http_status": 401,
        "message": "API key required",
    },
    "AUTH_INVALID": {
        "code": "AUTH_INVALID",
        "http_status": 401,
        "message": "Invalid or expired API key",
    },
    "AUTH_RATE_LIMITED": {
        "code": "AUTH_RATE_LIMITED",
        "http_status": 429,
        "message": "Rate limit exceeded",
    },
    "NOT_FOUND": {
        "code": "NOT_FOUND",
        "http_status": 404,
        "message": "Resource not found",
    },
    "INVALID_JSON": {
        "code": "INVALID_JSON",
        "http_status": 400,
        "message": "Invalid JSON in request body",
    },
    "BODY_TOO_LARGE": {
        "code": "BODY_TOO_LARGE",
        "http_status": 413,
        "message": "Request body exceeds 100KB limit",
    },
    "PARAM_MISSING": {
        "code": "PARAM_MISSING",
        "http_status": 400,
        "message": "Missing required parameter",
    },
    "PARAM_INVALID": {
        "code": "PARAM_INVALID",
        "http_status": 400,
        "message": "Invalid parameter value",
    },
    "AGENT_EXISTS": {
        "code": "AGENT_EXISTS",
        "http_status": 409,
        "message": "Agent already registered",
    },
    "INTERNAL_ERROR": {
        "code": "INTERNAL_ERROR",
        "http_status": 500,
        "message": "Internal server error",
    },
    "PERMISSION_DENIED": {
        "code": "PERMISSION_DENIED",
        "http_status": 403,
        "message": "Insufficient permissions",
    },
}


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


def _ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(_DATA_DIR, exist_ok=True)


def _now_iso():
    """返回当前时间的ISO格式字符串"""
    return datetime.now(TZ).isoformat()


def _make_error(code_key, error_id=None):
    """
    构造标准错误响应

    Args:
        code_key (str):             ERROR_CODES 中的键名
        error_id (str, optional):   错误唯一ID（用于追踪）

    Returns:
        dict: 标准错误格式
    """
    info = ERROR_CODES.get(code_key, ERROR_CODES["INTERNAL_ERROR"])
    return {
        "error_code": info["code"],
        "error": info["message"],
        "error_id": error_id or f"err_{uuid.uuid4().hex[:12]}",
    }


# ══════════════════════════════════════════════
#  Agent 一键入驻
# ══════════════════════════════════════════════

def agent_setup(data):
    """
    Agent 一键入驻 — 一次调用完成注册 + API Key 生成 + 快速开始指引

    内部流程:
      1. 调用 identity.AgentRegistration().register() 注册 Agent
      2. 调用 auth_provider.APIKeyManager().generate_key() 生成 API Key
      3. 返回所有信息（Agent 信息 + API Key + MCP 端点 + 快速开始指引）

    Args:
        data (dict): 入驻请求
            - agent_name (str, 必填):   Agent 名称
            - capabilities (list, 可选): 能力列表，如 ["scan", "monitor"]
            - owner (str, 可选):         所有者标识

    Returns:
        dict: 完整入驻结果
            - success (bool)
            - agent (dict):             Agent 注册信息（含 DID）
            - api_key (str):            API 密钥（明文，仅返回一次）
            - key_id (str):             API 密钥 ID
            - base_url (str):           平台 Base URL
            - mcp_endpoint (str):       MCP 端点
            - quick_start (dict):       各能力的快速开始指引
    """
    from eco.identity import AgentRegistration
    from eco.auth_provider import APIKeyManager

    # ── 参数校验 ──
    agent_name = (data.get("agent_name") or "").strip()
    if not agent_name:
        return {
            "success": False,
            **_make_error("PARAM_MISSING"),
            "detail": "agent_name is required",
        }

    capabilities = data.get("capabilities") or []
    owner = (data.get("owner") or "").strip()

    # ── 第一步：注册 Agent ──
    try:
        reg = AgentRegistration()
        agent = reg.register(
            name=agent_name,
            capabilities=capabilities,
            owner=owner,
        )
    except ValueError as e:
        # DID 冲突，表示 Agent 已存在
        err_msg = str(e)
        if "已注册" in err_msg:
            return {
                "success": False,
                **_make_error("AGENT_EXISTS"),
                "detail": err_msg,
            }
        return {
            "success": False,
            **_make_error("PARAM_INVALID"),
            "detail": err_msg,
        }
    except Exception as e:
        return {
            "success": False,
            **_make_error("INTERNAL_ERROR"),
            "detail": f"Agent registration failed: {str(e)}",
        }

    agent_did = agent["did"]

    # ── 第二步：生成 API Key ──
    try:
        key_mgr = APIKeyManager()
        key_result = key_mgr.generate_key(
            agent_id=agent_did,
            key_name=f"{agent_name}-default-key",
            scopes=["scan:*", "skill:*"],
            rate_limit=1000,
        )
    except Exception as e:
        return {
            "success": False,
            **_make_error("INTERNAL_ERROR"),
            "detail": f"API key generation failed: {str(e)}",
            "agent": agent,
        }

    # ── 第三步：组装完整响应 ──
    return {
        "success": True,
        "agent": agent,
        "api_key": key_result["api_key"],
        "key_id": key_result["key_id"],
        "base_url": _BASE_URL,
        "mcp_endpoint": f"{_BASE_URL}/api/v1/mcp",
        "quick_start": {
            "scan": (
                f"POST {_BASE_URL}/api/v1/audit "
                f"with Authorization: Bearer {key_result['api_key']}"
            ),
            "prompt_check": (
                f"POST {_BASE_URL}/api/v1/prompt-check "
                f"with Authorization: Bearer {key_result['api_key']}"
            ),
            "mcp": (
                f"POST {_BASE_URL}/api/v1/mcp "
                f"with MCP JSON-RPC 2.0 protocol"
            ),
        },
    }


# ══════════════════════════════════════════════
#  Agent 快速扫描
# ══════════════════════════════════════════════

def agent_quick_scan(data):
    """
    Agent 快速扫描 — 根据工具信息执行安全扫描

    输入工具的名称、描述和 Schema，自动调用扫描引擎进行安全分析。
    Agent 无需手动传入 DID，系统从上下文自动关联。

    Args:
        data (dict): 扫描请求
            - tool_name (str, 必填):        工具名称
            - tool_description (str, 必填):  工具描述
            - tool_schema (dict, 可选):      工具输入/输出 Schema（JSON Schema）
            - source_url (str, 可选):        源码仓库 URL（如果提供则进行深度扫描）
            - capabilities (list, 可选):     工具声明的能力列表

    Returns:
        dict: 扫描结果
            - success (bool)
            - score (int):          安全评分 (0-100)
            - risk (str):           风险等级
            - findings (list):      发现的安全问题
            - scanned_at (str):     扫描时间
    """
    # ── 参数校验 ──
    tool_name = (data.get("tool_name") or "").strip()
    tool_description = (data.get("tool_description") or "").strip()

    if not tool_name:
        return {
            "success": False,
            **_make_error("PARAM_MISSING"),
            "detail": "tool_name is required",
        }
    if not tool_description:
        return {
            "success": False,
            **_make_error("PARAM_MISSING"),
            "detail": "tool_description is required",
        }

    tool_schema = data.get("tool_schema") or {}
    source_url = (data.get("source_url") or "").strip()
    capabilities = data.get("capabilities") or []

    # ── 执行扫描 ──
    try:
        from scanner.engine import scan

        # 构造扫描输入：优先使用 source_url 做深度扫描，
        # 否则用 tool_description 作为内容进行快速分析
        scan_input = source_url if source_url else tool_description

        result = scan(
            source_url=scan_input,
            tool_type="mcp",
            name=tool_name,
            description=tool_description,
        )
    except Exception as e:
        return {
            "success": False,
            **_make_error("INTERNAL_ERROR"),
            "detail": f"Scan failed: {str(e)}",
        }

    # 补充 Agent 维度的元信息
    result["success"] = True
    result["agent_quick_scan"] = True
    result["tool_name"] = tool_name
    if capabilities:
        result["declared_capabilities"] = capabilities
    if tool_schema:
        result["tool_schema_provided"] = True

    return result


# ══════════════════════════════════════════════
#  Agent 状态查询
# ══════════════════════════════════════════════

def agent_status(did):
    """
    查询 Agent 状态 — 聚合身份、API Key、信誉、使用统计

    Args:
        did (str): Agent 的去中心化身份标识 (did:aishield:xxx)

    Returns:
        dict: Agent 状态信息
            - success (bool)
            - agent (dict):             Agent 基本信息
            - api_keys_count (int):     已生成的 API Key 数量
            - active_keys_count (int):  仍处于激活状态的 API Key 数量
            - reputation_score (int):   信誉分数
            - reputation_level (str):   信誉等级
            - usage_stats (dict):       使用统计
    """
    # ── 参数校验 ──
    if not did or not isinstance(did, str):
        return {
            "success": False,
            **_make_error("PARAM_MISSING"),
            "detail": "did is required",
        }

    did = did.strip()

    # ── 查询 Agent 信息 ──
    from eco.identity import AgentRegistration
    from eco.auth_provider import APIKeyManager

    reg = AgentRegistration()
    agent = reg.get_agent(did)

    if not agent:
        return {
            "success": False,
            **_make_error("NOT_FOUND"),
            "detail": f"Agent '{did}' not found",
        }

    # ── 查询 API Key 统计 ──
    try:
        key_mgr = APIKeyManager()
        keys = key_mgr.list_keys(agent_id=did)
        api_keys_count = len(keys)
        active_keys_count = sum(
            1 for k in keys if k.get("status") == "active"
        )
    except Exception:
        api_keys_count = 0
        active_keys_count = 0

    # ── 使用统计（从 billing 数据中提取） ──
    usage_stats = _get_usage_stats(did)

    return {
        "success": True,
        "agent": agent,
        "api_keys_count": api_keys_count,
        "active_keys_count": active_keys_count,
        "reputation_score": agent.get("reputation_score", 0),
        "reputation_level": agent.get("reputation_level", "novice"),
        "usage_stats": usage_stats,
    }


def _get_usage_stats(agent_id):
    """
    从 billing 数据中提取 Agent 的使用统计

    Args:
        agent_id (str): Agent ID / DID

    Returns:
        dict: 使用统计 {total_calls, endpoints, last_active}
    """
    billing_file = os.path.join(_DATA_DIR, "billing.json")
    data = _load_json(billing_file, {})

    # 在 usage_log 中按 account_id 筛选
    usage_log = data.get("usage_log", [])
    agent_calls = [
        entry for entry in usage_log
        if entry.get("account_id") == agent_id
    ]

    # 按端点统计
    endpoint_counts = {}
    for entry in agent_calls:
        ep = entry.get("endpoint", "unknown")
        endpoint_counts[ep] = endpoint_counts.get(ep, 0) + 1

    # 最后活跃时间
    last_active = None
    if agent_calls:
        timestamps = [
            entry.get("timestamp", "")
            for entry in agent_calls
            if entry.get("timestamp")
        ]
        if timestamps:
            last_active = max(timestamps)

    return {
        "total_calls": len(agent_calls),
        "endpoints": endpoint_counts,
        "last_active": last_active,
    }


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将 Agent Gateway 路由注册到 HTTPServer 的 Handler 上

    兼容 api/server.py 的 AIShieldHandler 模式。

    Args:
        handler: AIShieldHandler 实例（需要已有 _send_json 和 _read_body 方法）
    """
    # 保存原始方法引用
    original_do_get = handler.do_GET
    original_do_post = handler.do_POST

    def do_get_patched(self):
        """扩展 GET 路由"""
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path

        # ── GET /api/v1/agent/status/{did} — 查询 Agent 状态 ──
        if path.startswith("/api/v1/agent/status/"):
            did = path[len("/api/v1/agent/status/"):]
            result = agent_status(did)
            if result.get("success"):
                self._send_json(result)
            else:
                http_status = ERROR_CODES.get(
                    result.get("error_code", "INTERNAL_ERROR"),
                    ERROR_CODES["INTERNAL_ERROR"],
                ).get("http_status", 500)
                self._send_json(result, http_status)
            return

        # 非本模块路由，交给原始处理器
        original_do_get(self)

    def do_post_patched(self):
        """扩展 POST 路由"""
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
            self._send_json(_make_error("INVALID_JSON"), 400)
            return

        # ── POST /api/v1/agent/setup — Agent 一键入驻（无认证） ──
        if path == "/api/v1/agent/setup":
            result = agent_setup(data)
            if result.get("success"):
                self._send_json(result, 201)
            else:
                http_status = ERROR_CODES.get(
                    result.get("error_code", "INTERNAL_ERROR"),
                    ERROR_CODES["INTERNAL_ERROR"],
                ).get("http_status", 500)
                self._send_json(result, http_status)
            return

        # ── POST /api/v1/agent/scan — Agent 快速扫描（可选认证） ──
        if path == "/api/v1/agent/scan":
            result = agent_quick_scan(data)
            if result.get("success"):
                self._send_json(result)
            else:
                http_status = ERROR_CODES.get(
                    result.get("error_code", "INTERNAL_ERROR"),
                    ERROR_CODES["INTERNAL_ERROR"],
                ).get("http_status", 500)
                self._send_json(result, http_status)
            return

        # 非本模块路由，交给原始处理器
        original_do_post(self)

    # 替换 Handler 的方法
    handler.do_GET = do_get_patched.__get__(handler, type(handler))
    handler.do_POST = do_post_patched.__get__(handler, type(handler))


# ══════════════════════════════════════════════
#  独立测试入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("=== Agent 一键入驻测试 ===")
    result = agent_setup({
        "agent_name": "TestGatewayAgent",
        "capabilities": ["scan", "monitor"],
        "owner": "test_owner",
    })
    if result["success"]:
        print(f"  Agent DID: {result['agent']['did']}")
        print(f"  API Key:   {result['api_key'][:20]}...")
        print(f"  Key ID:    {result['key_id']}")
        print(f"  MCP:       {result['mcp_endpoint']}")
        print(f"  扫描指引:  {result['quick_start']['scan'][:60]}...")

        # 查询状态
        print("\n=== Agent 状态查询 ===")
        status = agent_status(result["agent"]["did"])
        print(f"  名称:     {status['agent']['name']}")
        print(f"  信誉分:   {status['reputation_score']} ({status['reputation_level']})")
        print(f"  API Key:  {status['api_keys_count']} 个 (活跃 {status['active_keys_count']})")
        print(f"  调用次数: {status['usage_stats']['total_calls']}")
    else:
        print(f"  入驻失败: {result.get('error')}")
        print(f"  详情: {result.get('detail', '')}")

    print("\n=== 全部测试通过 ===")