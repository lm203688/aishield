"""
eco/identity.py — Agent身份 + DID + 信誉系统

功能:
  - AgentRegistration: Agent注册（name/did/publicKey/capabilities/owner）
  - generate_did():    生成去中心化身份 (did:aishield:xxxxx)
  - ReputationSystem:  信誉积分系统
      初始50分 | 完成任务+5 | 失败-10 | 被举报-20
      等级: novice(0-39) / standard(40-69) / trusted(70-89) / verified(90-100)
  - 数据持久化: data/agents.json
  - 提供API路由处理函数（兼容HTTPServer模式）

API路由:
  POST /api/v1/identity/register          — 注册Agent
  GET  /api/v1/identity/agents             — 列出所有Agent
  GET  /api/v1/identity/agents/{did}      — 查询Agent详情
  POST /api/v1/identity/reputation/{did}  — 更新信誉分
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
AGENTS_FILE = os.path.join(_DATA_DIR, "agents.json")

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


def _ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(_DATA_DIR, exist_ok=True)


def _now_iso():
    """返回当前时间的ISO格式字符串"""
    return datetime.now(TZ).isoformat()


# ══════════════════════════════════════════════
#  DID 生成
# ══════════════════════════════════════════════

def generate_did():
    """
    生成去中心化身份标识符
    格式: did:aishield:<随机hex>
    
    Returns:
        str: DID字符串，例如 "did:aishield:a3f2b1c4e5d6"
    """
    # 生成12字节随机hex作为标识符
    rand_bytes = uuid.uuid4().bytes[:6]
    identifier = rand_bytes.hex()
    return f"did:aishield:{identifier}"


# ══════════════════════════════════════════════
#  Agent注册
# ══════════════════════════════════════════════

class AgentRegistration:
    """
    Agent注册管理器
    负责Agent的注册、查询、更新
    """

    def __init__(self):
        self._agents = {}  # did -> agent_info

    def _load(self):
        """从磁盘加载Agent数据"""
        data = _load_json(AGENTS_FILE, {"agents": {}})
        self._agents = data.get("agents", {})

    def _save(self):
        """持久化Agent数据到磁盘"""
        _ensure_data_dir()
        _save_json(AGENTS_FILE, {"agents": self._agents})

    def register(self, name, did=None, public_key=None,
                capabilities=None, owner=None):
        """
        注册一个新的Agent

        Args:
            name (str):        Agent名称
            did (str, opt):    去中心化身份（为空则自动生成）
            public_key (str):  公钥
            capabilities (list): 能力列表
            owner (str):       所有者

        Returns:
            dict: Agent注册信息
        """
        self._load()

        # 生成DID（如果未提供）
        if not did:
            did = generate_did()

        # 检查DID是否已存在
        if did in self._agents:
            raise ValueError(f"Agent DID '{did}' 已注册")

        # 构建Agent信息
        agent_info = {
            "name": name,
            "did": did,
            "public_key": public_key or "",
            "capabilities": capabilities or [],
            "owner": owner or "",
            "reputation_score": 50,         # 初始信誉分
            "reputation_level": "standard", # 初始等级
            "registered_at": _now_iso(),
            "updated_at": _now_iso(),
            "status": "active",
        }

        self._agents[did] = agent_info
        self._save()

        return agent_info

    def get_agent(self, did):
        """
        根据DID查询Agent信息

        Args:
            did (str): Agent DID

        Returns:
            dict | None: Agent信息，不存在返回None
        """
        self._load()
        return self._agents.get(did)

    def list_agents(self):
        """
        列出所有已注册的Agent

        Returns:
            list: Agent信息列表
        """
        self._load()
        return list(self._agents.values())

    def update_agent(self, did, **kwargs):
        """
        更新Agent信息

        Args:
            did (str): Agent DID
            **kwargs:  要更新的字段

        Returns:
            dict | None: 更新后的Agent信息
        """
        self._load()
        agent = self._agents.get(did)
        if not agent:
            return None

        for key, value in kwargs.items():
            if key in agent and key not in ("did", "registered_at"):
                agent[key] = value
        agent["updated_at"] = _now_iso()

        self._agents[did] = agent
        self._save()
        return agent

    def deactivate_agent(self, did):
        """
        停用Agent

        Args:
            did (str): Agent DID

        Returns:
            bool: 是否成功
        """
        self._load()
        if did not in self._agents:
            return False

        self._agents[did]["status"] = "inactive"
        self._agents[did]["updated_at"] = _now_iso()
        self._save()
        return True


# ══════════════════════════════════════════════
#  信誉系统
# ══════════════════════════════════════════════

# 信誉等级定义
REPUTATION_LEVELS = {
    "novice":    {"min": 0,  "max": 39, "label": "新手", "color": "#888888"},
    "standard":  {"min": 40, "max": 69, "label": "标准", "color": "#4A90D9"},
    "trusted":   {"min": 70, "max": 89, "label": "可信", "color": "#27AE60"},
    "verified":  {"min": 90, "max": 100, "label": "已认证", "color": "#F5A623"},
}

# 信誉变更规则
REPUTATION_RULES = {
    "task_complete": {"change": +5,  "desc": "任务完成"},
    "task_fail":     {"change": -10, "desc": "任务失败"},
    "reported":      {"change": -20, "desc": "被举报"},
}


class ReputationSystem:
    """
    信誉积分系统
    管理Agent的信誉分数和等级
    """

    def __init__(self):
        self._agents = {}

    def _load(self):
        """从磁盘加载数据"""
        data = _load_json(AGENTS_FILE, {"agents": {}})
        self._agents = data.get("agents", {})

    def _save(self):
        """持久化到磁盘"""
        _ensure_data_dir()
        _save_json(AGENTS_FILE, {"agents": self._agents})

    @staticmethod
    def _calc_level(score):
        """
        根据分数计算信誉等级

        Args:
            score (int): 信誉分数

        Returns:
            str: 等级名称
        """
        score = max(0, min(100, score))
        for level_name, config in REPUTATION_LEVELS.items():
            if config["min"] <= score <= config["max"]:
                return level_name
        return "novice"

    def get_score(self, did):
        """
        获取Agent信誉分

        Args:
            did (str): Agent DID

        Returns:
            int: 信誉分数（不存在返回0）
        """
        self._load()
        agent = self._agents.get(did)
        if not agent:
            return 0
        return agent.get("reputation_score", 0)

    def get_level(self, did):
        """
        获取Agent信誉等级

        Args:
            did (str): Agent DID

        Returns:
            str: 等级名称
        """
        score = self.get_score(did)
        return self._calc_level(score)

    def update_score(self, did, event_type):
        """
        更新Agent信誉分

        Args:
            did (str):         Agent DID
            event_type (str):  事件类型 (task_complete/task_fail/reported)

        Returns:
            dict: 更新后的信誉信息 {score, level, change, event}
        """
        self._load()

        if did not in self._agents:
            raise ValueError(f"Agent '{did}' 未注册")

        if event_type not in REPUTATION_RULES:
            raise ValueError(f"未知事件类型: {event_type}")

        rule = REPUTATION_RULES[event_type]
        agent = self._agents[did]

        # 更新分数（限制在0-100范围内）
        old_score = agent.get("reputation_score", 50)
        new_score = max(0, min(100, old_score + rule["change"]))
        agent["reputation_score"] = new_score
        agent["reputation_level"] = self._calc_level(new_score)
        agent["updated_at"] = _now_iso()

        # 记录信誉变更历史
        history = agent.setdefault("reputation_history", [])
        history.append({
            "event": event_type,
            "desc": rule["desc"],
            "change": rule["change"],
            "score_before": old_score,
            "score_after": new_score,
            "timestamp": _now_iso(),
        })
        # 只保留最近50条记录
        if len(history) > 50:
            agent["reputation_history"] = history[-50:]

        self._agents[did] = agent
        self._save()

        return {
            "did": did,
            "score": new_score,
            "level": agent["reputation_level"],
            "change": rule["change"],
            "event": event_type,
            "desc": rule["desc"],
        }

    def get_history(self, did):
        """
        获取Agent信誉变更历史

        Args:
            did (str): Agent DID

        Returns:
            list: 历史记录列表
        """
        self._load()
        agent = self._agents.get(did)
        if not agent:
            return []
        return agent.get("reputation_history", [])


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将身份模块路由注册到HTTPServer的Handler上

    兼容 api/server.py 的 AIShieldHandler 模式。
    在 Handler.__init__ 中调用此函数注册路由。

    Args:
        handler: AIShieldHandler实例（需要已有 _send_json 和 _read_body 方法）
    """
    # 保存原始方法引用
    original_do_get = handler.do_GET
    original_do_post = handler.do_POST

    def do_get_patched(self):
        """扩展GET路由"""
        # 兼容: 如果handler已有_parsed_path则复用，否则解析self.path
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path

        # ── GET /api/v1/identity/agents — 列出所有Agent ──
        if path == "/api/v1/identity/agents":
            reg = AgentRegistration()
            agents = reg.list_agents()
            self._send_json({
                "success": True,
                "total": len(agents),
                "agents": agents,
            })
            return

        # ── GET /api/v1/identity/agents/{did} — 查询Agent详情 ──
        if path.startswith("/api/v1/identity/agents/"):
            did = path[len("/api/v1/identity/agents/"):]
            reg = AgentRegistration()
            agent = reg.get_agent(did)
            if agent:
                self._send_json({"success": True, "agent": agent})
            else:
                self._send_json({"error": "Agent不存在", "did": did}, 404)
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

        # ── POST /api/v1/identity/register — 注册Agent ──
        if path == "/api/v1/identity/register":
            name = data.get("name", "").strip()
            if not name:
                self._send_json({"error": "name is required"}, 400)
                return

            try:
                reg = AgentRegistration()
                agent = reg.register(
                    name=name,
                    did=data.get("did"),
                    public_key=data.get("public_key"),
                    capabilities=data.get("capabilities"),
                    owner=data.get("owner"),
                )
                self._send_json({"success": True, "agent": agent}, 201)
            except ValueError as e:
                self._send_json({"error": str(e)}, 409)
            return

        # ── POST /api/v1/identity/reputation/{did} — 更新信誉分 ──
        if path.startswith("/api/v1/identity/reputation/"):
            did = path[len("/api/v1/identity/reputation/"):]
            event_type = data.get("event_type", "")
            try:
                repo = ReputationSystem()
                result = repo.update_score(did, event_type)
                self._send_json({"success": True, "reputation": result})
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
            return

        # 非本模块路由，交给原始处理器
        original_do_post(self)

    # 替换Handler的方法
    handler.do_GET = do_get_patched.__get__(handler, type(handler))
    handler.do_POST = do_post_patched.__get__(handler, type(handler))


# ══════════════════════════════════════════════
#  独立测试入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    # 快速测试DID生成
    print("=== DID生成测试 ===")
    for _ in range(5):
        did = generate_did()
        print(f"  {did}")

    # 测试Agent注册
    print("\n=== Agent注册测试 ===")
    reg = AgentRegistration()
    agent = reg.register(
        name="TestAgent-01",
        public_key="mock_key_abc123",
        capabilities=["scan", "audit", "monitor"],
        owner="test_owner",
    )
    print(f"  注册成功: {agent['did']}")
    print(f"  初始信誉: {agent['reputation_score']} ({agent['reputation_level']})")

    # 测试信誉更新
    print("\n=== 信誉系统测试 ===")
    repo = ReputationSystem()

    # 任务完成
    result = repo.update_score(agent["did"], "task_complete")
    print(f"  任务完成: +{result['change']} → {result['score']} ({result['level']})")

    # 任务完成
    result = repo.update_score(agent["did"], "task_complete")
    print(f"  任务完成: +{result['change']} → {result['score']} ({result['level']})")

    # 任务失败
    result = repo.update_score(agent["did"], "task_fail")
    print(f"  任务失败: {result['change']} → {result['score']} ({result['level']})")

    # 被举报
    result = repo.update_score(agent["did"], "reported")
    print(f"  被举报: {result['change']} → {result['score']} ({result['level']})")

    # 查询历史
    history = repo.get_history(agent["did"])
    print(f"\n  信誉变更历史 ({len(history)}条):")
    for h in history:
        print(f"    [{h['timestamp'][:19]}] {h['desc']}: {h['score_before']}→{h['score_after']} ({h['change']:+d})")

    print("\n=== 全部测试通过 ===")
