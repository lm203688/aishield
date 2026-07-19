"""
eco/a2a_gateway.py — A2A协议Gateway

功能:
  - 兼容Google A2A (Agent-to-Agent) v1.0规范
  - AgentCard:     注册Agent卡片（name/url/skills/capabilities）
  - AgentDiscovery: 发现已注册Agent
  - TaskRouter:    路由任务到合适的Agent
      根据Agent的能力描述匹配任务
      根据信誉分排序
  - 数据持久化: data/agent_registry.json

API路由:
  POST /api/v1/a2a/agent-card  — 注册Agent卡片
  GET  /api/v1/a2a/discover   — 发现Agent
  POST /api/v1/a2a/task        — 创建任务
"""

import json
import os
import uuid
import threading
import re
from datetime import datetime, timezone, timedelta

# ── 路径配置 ──
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")
AGENT_REGISTRY_FILE = os.path.join(_DATA_DIR, "agent_registry.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()

# A2A协议版本
A2A_VERSION = "1.0"
A2A_PROTOCOL = "aishield/a2a"


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


def _generate_agent_id():
    """生成Agent ID"""
    return f"agent-{uuid.uuid4().hex[:12]}"


def _generate_task_id():
    """生成任务ID"""
    return f"task-{uuid.uuid4().hex[:12]}"


# ══════════════════════════════════════════════
#  AgentCard — Agent卡片管理
# ══════════════════════════════════════════════

class AgentCard:
    """
    A2A Agent卡片管理
    兼容Google A2A v1.0 AgentCard规范
    """

    def __init__(self):
        self._agents = {}

    def _load(self):
        """从磁盘加载注册数据"""
        data = _load_json(AGENT_REGISTRY_FILE, {
            "agents": {},
            "tasks": {},
        })
        self._agents = data.get("agents", {})

    def _save(self):
        """持久化到磁盘"""
        # 加载完整数据再合并（不覆盖tasks等其他数据）
        full_data = _load_json(AGENT_REGISTRY_FILE, {
            "agents": {},
            "tasks": {},
        })
        full_data["agents"] = self._agents
        _save_json(AGENT_REGISTRY_FILE, full_data)

    def register(self, card_info):
        """
        注册Agent卡片

        A2A v1.0 AgentCard字段:
          - name:        Agent名称
          - url:         Agent服务URL
          - description: 描述
          - skills:      技能列表 [{id, name, description, tags}]
          - capabilities: 能力列表
          - version:     Agent版本
          - provider:    提供者信息

        Args:
            card_info (dict): Agent卡片信息

        Returns:
            dict: 注册的Agent卡片
        """
        self._load()

        agent_id = _generate_agent_id()

        card = {
            "agent_id": agent_id,
            "name": card_info.get("name", ""),
            "url": card_info.get("url", ""),
            "description": card_info.get("description", ""),
            "skills": card_info.get("skills", []),
            "capabilities": card_info.get("capabilities", []),
            "version": card_info.get("version", "1.0.0"),
            "provider": card_info.get("provider", {}),
            # AIShield扩展字段
            "reputation_score": card_info.get("reputation_score", 50),
            "reputation_level": card_info.get("reputation_level", "standard"),
            "status": "active",
            "registered_at": _now_iso(),
            "updated_at": _now_iso(),
            # A2A协议元数据
            "a2a_version": A2A_VERSION,
            "a2a_protocol": A2A_PROTOCOL,
        }

        self._agents[agent_id] = card
        self._save()

        return card

    def get_agent(self, agent_id):
        """
        获取Agent卡片

        Args:
            agent_id (str): Agent ID

        Returns:
            dict | None: Agent卡片
        """
        self._load()
        return self._agents.get(agent_id)

    def list_agents(self):
        """
        列出所有注册的Agent

        Returns:
            list: Agent卡片列表
        """
        self._load()
        return list(self._agents.values())

    def update_agent(self, agent_id, updates):
        """
        更新Agent卡片

        Args:
            agent_id (str): Agent ID
            updates (dict): 更新字段

        Returns:
            dict | None: 更新后的卡片
        """
        self._load()
        agent = self._agents.get(agent_id)
        if not agent:
            return None

        for key, value in updates.items():
            if key in agent and key not in ("agent_id", "registered_at"):
                agent[key] = value
        agent["updated_at"] = _now_iso()

        self._agents[agent_id] = agent
        self._save()
        return agent

    def deactivate_agent(self, agent_id):
        """
        停用Agent

        Args:
            agent_id (str): Agent ID

        Returns:
            bool: 是否成功
        """
        self._load()
        if agent_id not in self._agents:
            return False
        self._agents[agent_id]["status"] = "inactive"
        self._agents[agent_id]["updated_at"] = _now_iso()
        self._save()
        return True


# ══════════════════════════════════════════════
#  AgentDiscovery — Agent发现
# ══════════════════════════════════════════════

class AgentDiscovery:
    """
    Agent发现服务
    根据条件查找合适的Agent
    """

    def __init__(self):
        self._agents = {}

    def _load(self):
        """从磁盘加载数据"""
        data = _load_json(AGENT_REGISTRY_FILE, {"agents": {}})
        self._agents = data.get("agents", {})

    def discover(self, skill=None, capability=None, name=None, min_reputation=0):
        """
        发现Agent

        Args:
            skill (str):         按技能筛选
            capability (str):    按能力筛选
            name (str):          按名称模糊搜索
            min_reputation (int): 最低信誉分

        Returns:
            list: 匹配的Agent列表（按信誉分降序）
        """
        self._load()
        agents = list(self._agents.values())

        # 只返回活跃的Agent
        agents = [a for a in agents if a.get("status") == "active"]

        # 按技能筛选
        if skill:
            agents = [a for a in agents
                      if any(s.get("name", "").lower() == skill.lower()
                             or skill.lower() in s.get("description", "").lower()
                             or skill.lower() in s.get("tags", [])
                             for s in a.get("skills", []))]

        # 按能力筛选
        if capability:
            agents = [a for a in agents
                      if capability.lower() in [c.lower() for c in a.get("capabilities", [])]]

        # 按名称筛选
        if name:
            agents = [a for a in agents if name.lower() in a.get("name", "").lower()]

        # 最低信誉分
        if min_reputation > 0:
            agents = [a for a in agents if a.get("reputation_score", 0) >= min_reputation]

        # 按信誉分降序排列
        agents.sort(key=lambda a: a.get("reputation_score", 0), reverse=True)

        return agents

    def get_agent_by_skill(self, skill):
        """
        获取最擅长某技能的Agent（信誉分最高）

        Args:
            skill (str): 技能名称

        Returns:
            dict | None: 最佳匹配Agent
        """
        agents = self.discover(skill=skill)
        return agents[0] if agents else None


# ══════════════════════════════════════════════
#  TaskRouter — 任务路由
# ══════════════════════════════════════════════

# 任务状态
TASK_STATUSES = {
    "pending":    "等待处理",
    "routed":     "已路由",
    "in_progress": "处理中",
    "completed":  "已完成",
    "failed":     "失败",
    "cancelled":  "已取消",
}


class TaskRouter:
    """
    任务路由器
    将任务路由到最合适的Agent
    """

    def __init__(self):
        self._tasks = {}
        self._agents = {}

    def _load(self):
        """从磁盘加载数据"""
        data = _load_json(AGENT_REGISTRY_FILE, {
            "agents": {},
            "tasks": {},
        })
        self._agents = data.get("agents", {})
        self._tasks = data.get("tasks", {})

    def _save(self):
        """持久化到磁盘"""
        _save_json(AGENT_REGISTRY_FILE, {
            "agents": self._agents,
            "tasks": self._tasks,
        })

    def _match_agent(self, task_description, required_skills=None):
        """
        根据任务描述和所需技能匹配最佳Agent

        匹配逻辑:
          1. 提取任务描述中的关键词
          2. 匹配Agent的技能标签和能力列表
          3. 按匹配度 + 信誉分综合排序

        Args:
            task_description (str):  任务描述
            required_skills (list): 所需技能列表

        Returns:
            list: 匹配的Agent列表（按综合评分排序）
        """
        # 提取任务关键词
        keywords = set(re.findall(r'\w+', task_description.lower()))

        # 只考虑活跃Agent
        active_agents = [a for a in self._agents.values()
                        if a.get("status") == "active"]

        scored_agents = []
        for agent in active_agents:
            match_score = 0

            # 1. 技能匹配（权重40%）
            agent_skills = agent.get("skills", [])
            for skill in agent_skills:
                # 兼容str和dict两种skill格式
                if isinstance(skill, str):
                    skill_text = skill
                elif isinstance(skill, dict):
                    skill_text = (
                        skill.get("name", "") + " " +
                        skill.get("description", "") + " " +
                        " ".join(skill.get("tags", []))
                    )
                else:
                    continue
                skill_words = set(re.findall(r'\w+', skill_text.lower()))
                overlap = len(keywords & skill_words)
                match_score += overlap * 2

            # 2. 能力匹配（权重30%）
            capabilities = agent.get("capabilities", [])
            for cap in capabilities:
                cap_words = set(re.findall(r'\w+', cap.lower()))
                overlap = len(keywords & cap_words)
                match_score += overlap * 1.5

            # 3. 名称匹配（权重10%）
            name_words = set(re.findall(r'\w+', agent.get("name", "").lower()))
            name_overlap = len(keywords & name_words)
            match_score += name_overlap

            # 4. 描述匹配（权重10%）
            desc_words = set(re.findall(r'\w+', agent.get("description", "").lower()))
            desc_overlap = len(keywords & desc_words)
            match_score += desc_overlap

            # 5. 必需技能检查（权重10%）
            if required_skills:
                agent_skill_names = [s.get("name", "") for s in agent_skills]
                agent_caps = agent.get("capabilities", [])
                for req in required_skills:
                    if (req.lower() in [n.lower() for n in agent_skill_names]
                            or req.lower() in [c.lower() for c in agent_caps]):
                        match_score += 3

            # 6. 信誉分加权（0-100映射为0-10）
            rep_bonus = agent.get("reputation_score", 50) / 10.0
            match_score += rep_bonus

            scored_agents.append({
                "agent": agent,
                "match_score": round(match_score, 2),
            })

        # 按匹配分排序
        scored_agents.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_agents

    def create_task(self, task_description, task_type="general",
                    required_skills=None, payload=None):
        """
        创建并路由任务

        Args:
            task_description (str):  任务描述
            task_type (str):        任务类型 (general/scan/audit/report)
            required_skills (list): 所需技能
            payload (dict):        任务负载数据

        Returns:
            dict: 任务信息（含路由结果）
        """
        self._load()

        task_id = _generate_task_id()

        # 匹配Agent
        matches = self._match_agent(task_description, required_skills)

        # 选择最佳Agent
        best_agent = matches[0] if matches else None
        routed_to = best_agent["agent"]["agent_id"] if best_agent else None
        routed_name = best_agent["agent"]["name"] if best_agent else None

        task = {
            "task_id": task_id,
            "task_type": task_type,
            "description": task_description,
            "required_skills": required_skills or [],
            "payload": payload or {},
            "routed_to": routed_to,
            "routed_name": routed_name,
            "match_score": best_agent["match_score"] if best_agent else 0,
            "status": "routed" if best_agent else "pending",
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "a2a_version": A2A_VERSION,
        }

        self._tasks[task_id] = task
        self._save()

        return {
            "task": task,
            "candidates": [
                {
                    "agent_id": m["agent"]["agent_id"],
                    "agent_name": m["agent"]["name"],
                    "match_score": m["match_score"],
                    "reputation": m["agent"].get("reputation_score", 0),
                }
                for m in matches[:5]  # 返回前5个候选
            ],
        }

    def get_task(self, task_id):
        """
        获取任务详情

        Args:
            task_id (str): 任务ID

        Returns:
            dict | None: 任务信息
        """
        self._load()
        return self._tasks.get(task_id)

    def update_task_status(self, task_id, status, result=None):
        """
        更新任务状态

        Args:
            task_id (str):  任务ID
            status (str):   新状态
            result (dict):   任务结果

        Returns:
            dict | None: 更新后的任务
        """
        self._load()
        task = self._tasks.get(task_id)
        if not task:
            return None

        if status not in TASK_STATUSES:
            raise ValueError(f"无效状态: {status}")

        task["status"] = status
        task["updated_at"] = _now_iso()
        if result:
            task["result"] = result

        self._tasks[task_id] = task
        self._save()
        return task

    def list_tasks(self, status=None, page=1, page_size=20):
        """
        列出任务

        Args:
            status (str):   过滤状态
            page (int):     页码
            page_size (int): 每页数量

        Returns:
            dict: 任务列表
        """
        self._load()
        tasks = list(self._tasks.values())

        if status:
            tasks = [t for t in tasks if t.get("status") == status]

        # 按时间倒序
        tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)

        total = len(tasks)
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "tasks": tasks[start:end],
        }


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将A2A Gateway模块路由注册到HTTPServer的Handler上

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

        # ── GET /api/v1/a2a/discover — 发现Agent ──
        if path == "/api/v1/a2a/discover":
            from urllib.parse import parse_qs
            query = parse_qs(parsed.query)
            skill = query.get("skill", [None])[0]
            capability = query.get("capability", [None])[0]
            name = query.get("name", [None])[0]
            try:
                min_rep = int(query.get("min_reputation", [0])[0])
            except (ValueError, IndexError):
                min_rep = 0

            try:
                discovery = AgentDiscovery()
                agents = discovery.discover(
                    skill=skill,
                    capability=capability,
                    name=name,
                    min_reputation=min_rep,
                )
                self._send_json({
                    "success": True,
                    "total": len(agents),
                    "agents": agents,
                    "a2a_version": A2A_VERSION,
                })
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

        # ── POST /api/v1/a2a/agent-card — 注册Agent卡片 ──
        if path == "/api/v1/a2a/agent-card":
            name = data.get("name", "").strip()
            if not name:
                self._send_json({"error": "name is required"}, 400)
                return

            try:
                card_mgr = AgentCard()
                card = card_mgr.register(data)
                self._send_json({
                    "success": True,
                    "agent_card": card,
                    "a2a_version": A2A_VERSION,
                }, 201)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── POST /api/v1/a2a/task — 创建任务 ──
        if path == "/api/v1/a2a/task":
            description = data.get("description", "").strip()
            if not description:
                self._send_json({"error": "description is required"}, 400)
                return

            try:
                router = TaskRouter()
                result = router.create_task(
                    task_description=description,
                    task_type=data.get("task_type", "general"),
                    required_skills=data.get("required_skills"),
                    payload=data.get("payload"),
                )
                self._send_json({
                    "success": True,
                    "a2a_version": A2A_VERSION,
                    **result,
                }, 201)
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
    print("=== A2A Gateway测试 ===")

    # 注册Agent
    print("\n--- 注册Agent卡片 ---")
    card_mgr = AgentCard()

    agent1 = card_mgr.register({
        "name": "SecurityScanner",
        "url": "https://agent.aishield.dev/scanner",
        "description": "OWASP MCP Top 10安全扫描Agent",
        "skills": [
            {"id": "scan", "name": "security_scan", "description": "安全扫描", "tags": ["scan", "security", "audit"]},
            {"id": "audit", "name": "code_audit", "description": "代码审计", "tags": ["audit", "code"]},
        ],
        "capabilities": ["security_scan", "prompt_check", "banned_words"],
        "version": "1.0.0",
        "provider": {"name": "AIShield"},
        "reputation_score": 85,
    })
    print(f"  Agent1: {agent1['agent_id']} — {agent1['name']}")

    agent2 = card_mgr.register({
        "name": "CodeReviewer",
        "url": "https://agent.aishield.dev/reviewer",
        "description": "AI代码审查Agent",
        "skills": [
            {"id": "review", "name": "code_review", "description": "代码审查", "tags": ["review", "code", "quality"]},
        ],
        "capabilities": ["code_review", "security_scan"],
        "version": "1.0.0",
        "provider": {"name": "AIShield"},
        "reputation_score": 72,
    })
    print(f"  Agent2: {agent2['agent_id']} — {agent2['name']}")

    # 发现Agent
    print("\n--- 发现Agent ---")
    discovery = AgentDiscovery()

    scan_agents = discovery.discover(skill="security_scan")
    print(f"  能做security_scan的Agent: {len(scan_agents)}个")
    for a in scan_agents:
        print(f"    {a['name']} (信誉: {a['reputation_score']})")

    # 任务路由
    print("\n--- 任务路由 ---")
    router = TaskRouter()

    result = router.create_task(
        task_description="请对这个MCP工具进行安全扫描，检查是否符合OWASP标准",
        task_type="scan",
        required_skills=["security_scan"],
    )
    task = result["task"]
    print(f"  任务ID: {task['task_id']}")
    print(f"  路由到: {task['routed_name']} (匹配分: {task['match_score']})")
    print(f"  候选数: {len(result['candidates'])}")
    for c in result["candidates"]:
        print(f"    {c['agent_name']}: 匹配{c['match_score']}, 信誉{c['reputation']}")

    print("\n=== 全部测试通过 ===")
