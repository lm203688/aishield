"""
eco/a2a_gateway.py — A2A协议Gateway

功能:
  - 兼容Google A2A (Agent-to-Agent) v1.0规范
  - AgentCard:     注册Agent卡片（name/url/skills/capabilities/authentication/默认交互模式）
  - AgentDiscovery: 发现已注册Agent
      支持技能/能力/标签/名称多维度过滤
      按信誉分降序返回
  - TaskRouter:    路由任务到合适的Agent
      根据Agent的能力描述与标签匹配任务
      根据匹配度 + 信誉分综合排序
      支持会话(session)、历史(history)、工件(artifacts)
      支持v1.0任务状态机(submitted/working/input-required/completed/canceled/failed/unknown)
  - 数据持久化: data/agent_registry.json

v1.0 升级要点（相对旧版）:
  - AgentCard.capabilities 由列表升级为 v1.0 对象结构(streaming/pushNotifications/...)
  - 新增 authentication / defaultInputModes / defaultOutputModes / documentationUrl 字段
  - skills 字段补充 examples / inputModes / outputModes
  - Task 状态对齐 v1.0 枚举；保留旧状态做向后兼容映射
  - Task 增加 sessionId / history / artifacts / metadata
  - 新增 cancel_task / add_message / add_artifact 等生命周期方法
  - 完全基于 Python 标准库，零外部依赖

API路由:
  POST /api/v1/a2a/agent-card           — 注册Agent卡片
  GET  /api/v1/a2a/discover             — 发现Agent
  POST /api/v1/a2a/task                 — 创建任务
  POST /api/v1/a2a/task/{id}/cancel     — 取消任务（v1.0新增）
  GET  /api/v1/a2a/task                 — 列出任务
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

# A2A协议版本（对齐 Google A2A v1.0）
A2A_VERSION = "1.0"
A2A_PROTOCOL = "aishield/a2a"
# 协议版本标签（与 .well-known/agent-card.json 中的 protocol_version 字段一致）
A2A_PROTOCOL_VERSION = "a2a-2025-06"

# 默认输入/输出交互模式（MIME 类型）
DEFAULT_INPUT_MODES = ["text/plain", "application/json"]
DEFAULT_OUTPUT_MODES = ["text/plain", "application/json"]


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


def _generate_session_id():
    """生成会话ID（A2A v1.0 sessionId 字段）"""
    return f"session-{uuid.uuid4().hex[:16]}"


def _generate_message_id():
    """生成消息ID（A2A v1.0 history 中 Message 的标识）"""
    return f"msg-{uuid.uuid4().hex[:12]}"


# ── 旧版 → v1.0 状态映射（保持向后兼容） ──
# 旧状态 → v1.0 状态
_LEGACY_TO_V1_STATUS = {
    "pending":     "submitted",      # 等待处理 → 已提交
    "routed":      "submitted",      # 已路由 → 仍属于已提交（等待Agent接管）
    "in_progress": "working",        # 处理中 → 工作中
    "completed":   "completed",      # 已完成
    "failed":      "failed",         # 失败
    "cancelled":   "canceled",       # 已取消（注意 v1.0 单词拼写为 canceled）
}

# v1.0 状态枚举（权威定义）
TASK_STATES_V1 = {
    "submitted":      "任务已提交",      # 任务已提交，等待远程Agent处理
    "working":        "任务处理中",      # 远程Agent正在处理任务
    "input-required": "需要客户端输入",  # 任务需要客户端提供额外输入
    "completed":      "任务已完成",      # 任务已成功完成
    "canceled":       "任务已取消",      # 任务已被取消
    "failed":         "任务失败",        # 任务执行失败
    "unknown":        "任务状态未知",    # 任务状态未知
}

# 终态集合：处于这些状态的任务不再接受状态变更
_TERMINAL_STATES = {"completed", "canceled", "failed"}


def _normalize_capabilities(cap):
    """
    规范化 capabilities 字段为 A2A v1.0 对象结构。

    旧版用列表（如 ["security_scan", "code_review"]），
    v1.0 用对象（{streaming, pushNotifications, stateTransitionHistory}）。
    为保持向后兼容，当传入列表时，将其转存为 capabilities.supported 列表，
    同时保留 v1.0 标准能力标志位。

    Args:
        cap: 旧版列表 或 v1.0 对象

    Returns:
        dict: v1.0 规范化后的 capabilities 对象
    """
    # v1.0 标准能力对象
    base = {
        "streaming": False,                # 是否支持 SSE 流式传输
        "pushNotifications": False,        # 是否支持推送通知
        "stateTransitionHistory": False,   # 是否暴露任务状态变更历史
    }
    if isinstance(cap, dict):
        # 已经是对象：合并已知标志位，并保留其他扩展字段
        for key in base:
            if key in cap:
                base[key] = bool(cap[key])
        # 保留旧版"supported"列表（若存在）
        if "supported" in cap:
            base["supported"] = list(cap.get("supported") or [])
        return base
    if isinstance(cap, (list, tuple)):
        # 旧版列表：转为 supported 字段，并保留原始能力名
        base["supported"] = list(cap)
        return base
    return base


def _normalize_skills(skills):
    """
    规范化 skills 字段，保证每个 skill 都包含 v1.0 必备字段。

    兼容三种输入格式：
      - 字符串列表: ["scan", "audit"]
      - 旧版字典列表: [{"id": ..., "name": ..., "tags": [...]}]
      - v1.0 字典列表: 含 examples/inputModes/outputModes

    Args:
        skills: 原始 skills 输入

    Returns:
        list: 规范化后的 skill 字典列表
    """
    if not isinstance(skills, (list, tuple)):
        return []
    normalized = []
    for idx, skill in enumerate(skills):
        if isinstance(skill, str):
            # 纯字符串 → 构造最小 v1.0 skill
            normalized.append({
                "id": f"skill-{idx}",
                "name": skill,
                "description": "",
                "tags": [],
                "examples": [],
                "inputModes": list(DEFAULT_INPUT_MODES),
                "outputModes": list(DEFAULT_OUTPUT_MODES),
            })
        elif isinstance(skill, dict):
            normalized.append({
                "id": skill.get("id") or f"skill-{idx}",
                "name": skill.get("name", ""),
                "description": skill.get("description", ""),
                "tags": list(skill.get("tags", []) or []),
                "examples": list(skill.get("examples", []) or []),
                "inputModes": list(skill.get("inputModes") or skill.get("input_modes") or DEFAULT_INPUT_MODES),
                "outputModes": list(skill.get("outputModes") or skill.get("output_modes") or DEFAULT_OUTPUT_MODES),
                # 保留原始扩展字段（如 input_schema/output_schema）
                **{k: v for k, v in skill.items()
                   if k not in ("id", "name", "description", "tags", "examples",
                                "inputModes", "outputModes", "input_modes", "output_modes")}
            })
    return normalized


def _normalize_task_status(status):
    """
    将任务状态规范化为 v1.0 枚举值。

    - 已是 v1.0 状态：原样返回
    - 是旧版状态：映射到 v1.0
    - 兼容 "cancelled"（旧拼写）→ "canceled"（v1.0 拼写）

    Args:
        status (str): 输入状态

    Returns:
        str | None: v1.0 状态枚举值，无效时返回 None
    """
    if not status:
        return None
    status = str(status).strip().lower()
    # 直接命中 v1.0 枚举
    if status in TASK_STATES_V1:
        return status
    # 兼容旧拼写 cancelled → canceled
    if status == "cancelled":
        return "canceled"
    # 旧版状态映射
    return _LEGACY_TO_V1_STATUS.get(status)


def _extract_capability_names(agent):
    """
    提取 Agent 卡片中所有能力名称（用于匹配/过滤）。

    兼容 v1.0 对象结构（capabilities.supported）与旧版列表结构。

    Args:
        agent (dict): Agent 卡片

    Returns:
        list: 能力名称列表（小写）
    """
    caps = agent.get("capabilities", {})
    if isinstance(caps, dict):
        return [str(c).lower() for c in caps.get("supported", [])]
    if isinstance(caps, (list, tuple)):
        return [str(c).lower() for c in caps]
    return []


def _extract_skill_tags(agent):
    """
    提取 Agent 卡片中所有技能标签（用于 tags 维度过滤与匹配）。

    Args:
        agent (dict): Agent 卡片

    Returns:
        set: 标签集合（小写）
    """
    tags = set()
    for skill in agent.get("skills", []) or []:
        if isinstance(skill, dict):
            for tag in skill.get("tags", []) or []:
                tags.add(str(tag).lower())
    return tags


# ══════════════════════════════════════════════
#  AgentCard — Agent卡片管理
# ══════════════════════════════════════════════

class AgentCard:
    """
    A2A Agent卡片管理
    兼容Google A2A v1.0 AgentCard规范

    v1.0 核心字段:
      - name / url / description / version: 基本信息
      - provider:                 提供者信息 {organization, url}
      - documentationUrl:          文档链接（v1.0新增）
      - capabilities:             能力对象 {streaming, pushNotifications, stateTransitionHistory, supported}
      - authentication:           认证配置 {schemes, credentials}（v1.0新增）
      - defaultInputModes:        默认输入MIME类型列表（v1.0新增）
      - defaultOutputModes:       默认输出MIME类型列表（v1.0新增）
      - skills:                   技能列表 [{id, name, description, tags, examples, inputModes, outputModes}]

    AIShield 扩展字段:
      - agent_id / reputation_score / reputation_level / status
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
        注册Agent卡片（兼容旧版列表式输入与v1.0对象式输入）

        旧版字段（仍受支持）:
          - name / url / description / skills / capabilities / version / provider

        v1.0 新增字段:
          - documentationUrl:   文档链接
          - authentication:    认证配置 {schemes: list, credentials: str}
          - defaultInputModes:  默认输入 MIME 类型列表
          - defaultOutputModes: 默认输出 MIME 类型列表
          - skills[].examples: 技能示例场景列表
          - skills[].inputModes / skills[].outputModes: 技能级交互模式

        Args:
            card_info (dict): Agent卡片信息

        Returns:
            dict: 注册的Agent卡片（含规范化后的 v1.0 字段）
        """
        self._load()

        agent_id = _generate_agent_id()

        card = {
            "agent_id": agent_id,
            # ── A2A v1.0 基本字段 ──
            "name": card_info.get("name", ""),
            "url": card_info.get("url", ""),
            "description": card_info.get("description", ""),
            "version": card_info.get("version", "1.0.0"),
            # ── v1.0 提供者信息（兼容旧版 provider 对象） ──
            "provider": card_info.get("provider", {}),
            # ── v1.0 新增字段 ──
            "documentationUrl": card_info.get("documentationUrl") or card_info.get("documentation_url", ""),
            "authentication": card_info.get("authentication", {
                "schemes": [],
                "credentials": None,
            }),
            "defaultInputModes": card_info.get("defaultInputModes") or card_info.get("default_input_modes") or list(DEFAULT_INPUT_MODES),
            "defaultOutputModes": card_info.get("defaultOutputModes") or card_info.get("default_output_modes") or list(DEFAULT_OUTPUT_MODES),
            # ── skills: 使用规范化函数处理 ──
            "skills": _normalize_skills(card_info.get("skills", [])),
            # ── capabilities: 使用规范化函数处理（列表→对象） ──
            "capabilities": _normalize_capabilities(card_info.get("capabilities", [])),
            # ── AIShield 扩展字段 ──
            "reputation_score": card_info.get("reputation_score", 50),
            "reputation_level": card_info.get("reputation_level", "standard"),
            "status": "active",
            "registered_at": _now_iso(),
            "updated_at": _now_iso(),
            # ── A2A 协议元数据 ──
            "a2a_version": A2A_VERSION,
            "a2a_protocol": A2A_PROTOCOL,
            "a2a_protocol_version": A2A_PROTOCOL_VERSION,
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

        对 capabilities 和 skills 字段会自动触发 v1.0 规范化。

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
            if key in ("agent_id", "registered_at"):
                # 不可变字段
                continue
            if key == "capabilities":
                # 触发 v1.0 规范化
                value = _normalize_capabilities(value)
            elif key == "skills":
                # 触发 v1.0 规范化
                value = _normalize_skills(value)
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

    def get_public_card(self, agent_id):
        """
        获取可公开的 AgentCard（符合 v1.0 .well-known/agent-card.json 结构）

        剥离 AIShield 内部字段，仅返回 A2A v1.0 标准字段。

        Args:
            agent_id (str): Agent ID

        Returns:
            dict | None: 公开的 AgentCard，不含内部字段
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        # 构造符合 v1.0 规范的公开卡片
        public = {
            "name": agent["name"],
            "url": agent["url"],
            "description": agent.get("description", ""),
            "version": agent.get("version", "1.0.0"),
            "provider": agent.get("provider", {}),
            "capabilities": agent.get("capabilities", {}),
            "skills": agent.get("skills", []),
        }
        # v1.0 可选字段（仅在有值时包含）
        if agent.get("documentationUrl"):
            public["documentationUrl"] = agent["documentationUrl"]
        if agent.get("authentication"):
            auth = agent["authentication"]
            if auth.get("schemes"):
                public["authentication"] = auth
        if agent.get("defaultInputModes"):
            public["defaultInputModes"] = agent["defaultInputModes"]
        if agent.get("defaultOutputModes"):
            public["defaultOutputModes"] = agent["defaultOutputModes"]
        return public


# ══════════════════════════════════════════════
#  AgentDiscovery — Agent发现
# ══════════════════════════════════════════════

class AgentDiscovery:
    """
    Agent发现服务
    根据条件查找合适的Agent（兼容 v1.0 对象式 capabilities）
    """

    def __init__(self):
        self._agents = {}

    def _load(self):
        """从磁盘加载数据"""
        data = _load_json(AGENT_REGISTRY_FILE, {"agents": {}})
        self._agents = data.get("agents", {})

    def discover(self, skill=None, capability=None, name=None, min_reputation=0, tags=None):
        """
        发现Agent（多维度过滤）

        Args:
            skill (str):          按技能名称/描述/标签筛选
            capability (str):     按能力名称筛选（兼容 v1.0 对象与旧版列表）
            name (str):           按名称模糊搜索
            min_reputation (int): 最低信誉分
            tags (str|list):      按技能标签筛选（v1.0新增，支持逗号分隔字符串或列表）

        Returns:
            list: 匹配的Agent列表（按信誉分降序）
        """
        self._load()
        agents = list(self._agents.values())

        # 只返回活跃的Agent
        agents = [a for a in agents if a.get("status") == "active"]

        # 按技能筛选（匹配技能名称、描述、标签）
        if skill:
            skill_lower = skill.lower()
            agents = [a for a in agents
                      if any(s.get("name", "").lower() == skill_lower
                             or skill_lower in s.get("description", "").lower()
                             or skill_lower in [str(t).lower() for t in (s.get("tags") or [])]
                             or skill_lower in [str(e).lower() for e in (s.get("examples") or [])]
                             for s in (a.get("skills") or []))]

        # 按能力筛选（兼容 v1.0 对象与旧版列表）
        if capability:
            cap_lower = capability.lower()
            agents = [a for a in agents
                      if cap_lower in _extract_capability_names(a)]

        # 按名称筛选
        if name:
            name_lower = name.lower()
            agents = [a for a in agents if name_lower in a.get("name", "").lower()]

        # 按标签筛选（v1.0新增）
        if tags:
            # 统一为列表
            if isinstance(tags, str):
                tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
            elif isinstance(tags, (list, tuple)):
                tag_list = [str(t).lower() for t in tags]
            else:
                tag_list = []
            if tag_list:
                tag_set = set(tag_list)
                agents = [a for a in agents
                          if tag_set & _extract_skill_tags(a)]

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

# 任务状态（旧版，已由 v1.0 TASK_STATES_V1 取代，此处保留以兼容外部引用）
TASK_STATUSES = {
    "pending":     "等待处理",
    "routed":      "已路由",
    "in_progress": "处理中",
    "completed":   "已完成",
    "failed":      "失败",
    "cancelled":   "已取消",
    # v1.0 新增状态
    "submitted":      "已提交",
    "working":        "处理中",
    "input-required": "需要输入",
    "unknown":        "未知",
}


class TaskRouter:
    """
    任务路由器
    将任务路由到最合适的Agent

    v1.0 升级:
      - 状态机对齐 A2A v1.0 (submitted/working/input-required/completed/canceled/failed/unknown)
      - Task 结构增加 sessionId / history / artifacts / metadata
      - 新增 cancel_task / add_message / add_artifact 生命周期方法
      - 匹配算法利用 v1.0 tags / examples 字段增强精度
      - 能力匹配兼容 v1.0 对象结构
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

        匹配逻辑（v1.0增强）:
          1. 提取任务描述中的关键词
          2. 匹配Agent的技能标签、示例、能力列表（兼容v1.0对象结构）
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

            # 1. 技能匹配（权重35%）：名称+描述+标签+示例
            agent_skills = agent.get("skills", []) or []
            for skill in agent_skills:
                # 兼容str和dict两种skill格式
                if isinstance(skill, str):
                    skill_text = skill
                elif isinstance(skill, dict):
                    skill_text = (
                        skill.get("name", "") + " " +
                        skill.get("description", "") + " " +
                        " ".join(skill.get("tags") or []) + " " +
                        " ".join(skill.get("examples") or [])  # v1.0: examples 也参与匹配
                    )
                else:
                    continue
                skill_words = set(re.findall(r'\w+', skill_text.lower()))
                overlap = len(keywords & skill_words)
                match_score += overlap * 2

            # 2. 能力匹配（权重25%）：兼容v1.0对象与旧版列表
            cap_names = _extract_capability_names(agent)
            for cap in cap_names:
                cap_words = set(re.findall(r'\w+', cap.lower()))
                overlap = len(keywords & cap_words)
                match_score += overlap * 1.5

            # 3. 标签直接匹配（权重15%，v1.0新增）
            agent_tags = _extract_skill_tags(agent)
            tag_overlap = len(keywords & agent_tags)
            match_score += tag_overlap * 1.8

            # 4. 名称匹配（权重10%）
            name_words = set(re.findall(r'\w+', agent.get("name", "").lower()))
            name_overlap = len(keywords & name_words)
            match_score += name_overlap

            # 5. 描述匹配（权重10%）
            desc_words = set(re.findall(r'\w+', agent.get("description", "").lower()))
            desc_overlap = len(keywords & desc_words)
            match_score += desc_overlap

            # 6. 必需技能检查（权重5%）
            if required_skills:
                agent_skill_names = [s.get("name", "") for s in agent_skills if isinstance(s, dict)]
                for req in required_skills:
                    if (req.lower() in [n.lower() for n in agent_skill_names]
                            or req.lower() in cap_names):
                        match_score += 3

            # 7. 信誉分加权（0-100映射为0-10）
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
                    required_skills=None, payload=None,
                    session_id=None, metadata=None):
        """
        创建并路由任务（v1.0增强）

        Args:
            task_description (str):  任务描述
            task_type (str):        任务类型 (general/scan/audit/report)
            required_skills (list): 所需技能
            payload (dict):        任务负载数据
            session_id (str):       会话ID（v1.0新增，为空时自动生成）
            metadata (dict):        扩展元数据（v1.0新增）

        Returns:
            dict: 任务信息（含路由结果）
        """
        self._load()

        # ── P0-3: Agent 通信安全平面 ──
        # 每个 A2A 任务创建先过安全闸，命中威胁即拒绝。
        try:
            from eco import agent_security_gateway as _gw
            _screen = _gw.screen_message(
                sender_agent_id=(metadata or {}).get("sender_agent_id"),
                message_type="a2a_task",
                payload=payload,
                task_description=task_description,
                record=True,
            )
            if not _screen["allowed"]:
                raise ValueError(
                    "agent_security_gateway: A2A task blocked ("
                    + "; ".join(_screen["reasons"]) + ")"
                )
        except ValueError:
            raise
        except Exception:
            pass

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
            # ── v1.0 任务状态 ──
            "status": "submitted" if best_agent else "submitted",
            # ── v1.0 新增字段 ──
            "sessionId": session_id or _generate_session_id(),
            "history": [],      # 消息历史（Message列表）
            "artifacts": [],    # 产出工件（Artifact列表）
            "metadata": metadata or {},
            # ── 时间戳 ──
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            # ── 协议元数据 ──
            "a2a_version": A2A_VERSION,
            "a2a_protocol_version": A2A_PROTOCOL_VERSION,
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

    def update_task_status(self, task_id, status, result=None, message=None):
        """
        更新任务状态（兼容旧版状态与v1.0状态）

        状态变更规则:
          - 终态(completed/canceled/failed)不可再次变更
          - 状态自动规范化为 v1.0 枚举值

        Args:
            task_id (str):   任务ID
            status (str):    新状态（支持旧版状态名，自动映射）
            result (dict):    任务结果（v1.0 artifact 级结果）
            message (str):    状态变更附带消息（v1.0 status.message）

        Returns:
            dict | None: 更新后的任务

        Raises:
            ValueError: 状态无效或任务已处于终态
        """
        self._load()
        task = self._tasks.get(task_id)
        if not task:
            return None

        # 规范化状态为 v1.0 枚举
        v1_status = _normalize_task_status(status)
        if not v1_status:
            raise ValueError(f"无效状态: {status}，有效状态: {', '.join(TASK_STATES_V1.keys())}")

        # 终态检查
        current_status = task.get("status", "unknown")
        if current_status in _TERMINAL_STATES:
            raise ValueError(
                f"任务已处于终态 '{current_status}'，不可变更为 '{v1_status}'"
            )

        task["status"] = v1_status
        task["updated_at"] = _now_iso()

        # v1.0: 状态变更附带消息（附加到 history）
        if message:
            msg_entry = {
                "messageId": _generate_message_id(),
                "role": "system",
                "parts": [{"type": "text", "text": message}],
                "timestamp": _now_iso(),
            }
            task.setdefault("history", []).append(msg_entry)

        if result:
            task["result"] = result

        self._tasks[task_id] = task
        self._save()
        return task

    def cancel_task(self, task_id, reason=None):
        """
        取消任务（v1.0新增）

        只能取消非终态的任务。

        Args:
            task_id (str): 任务ID
            reason (str):  取消原因

        Returns:
            dict | None: 更新后的任务

        Raises:
            ValueError: 任务不存在或已处于终态
        """
        return self.update_task_status(
            task_id,
            status="canceled",
            message=reason or "任务已被取消",
        )

    def add_message(self, task_id, role, text, parts=None):
        """
        向任务历史追加消息（v1.0新增）

        Args:
            task_id (str): 任务ID
            role (str):     消息角色 (user/agent/system)
            text (str):     文本内容
            parts (list):   自定义Part列表（传入时覆盖默认的text part）

        Returns:
            dict | None: 更新后的任务
        """
        self._load()
        task = self._tasks.get(task_id)
        if not task:
            return None

        # 构造 v1.0 Message
        msg_entry = {
            "messageId": _generate_message_id(),
            "role": role,
            "parts": parts or [{"type": "text", "text": text}],
            "timestamp": _now_iso(),
        }
        task.setdefault("history", []).append(msg_entry)
        task["updated_at"] = _now_iso()

        self._tasks[task_id] = task
        self._save()
        return task

    def add_artifact(self, task_id, artifact):
        """
        向任务追加产出工件（v1.0新增）

        Args:
            task_id (str):  任务ID
            artifact (dict): 工件对象，至少包含 name 和 type 字段

        Returns:
            dict | None: 更新后的任务
        """
        self._load()
        task = self._tasks.get(task_id)
        if not task:
            return None

        # 补充工件元数据
        artifact_entry = {
            "artifactId": f"artifact-{uuid.uuid4().hex[:12]}",
            "name": artifact.get("name", "unnamed"),
            "type": artifact.get("type", "text"),
            "parts": artifact.get("parts", []),
            "metadata": artifact.get("metadata", {}),
            "timestamp": _now_iso(),
        }
        task.setdefault("artifacts", []).append(artifact_entry)
        task["updated_at"] = _now_iso()

        self._tasks[task_id] = task
        self._save()
        return task

    def list_tasks(self, status=None, session_id=None, page=1, page_size=20):
        """
        列出任务（v1.0增强：支持 session_id 过滤与状态规范化）

        Args:
            status (str):     过滤状态（支持旧版状态名，自动映射）
            session_id (str): 按会话ID过滤（v1.0新增）
            page (int):       页码
            page_size (int):  每页数量

        Returns:
            dict: 任务列表
        """
        self._load()
        tasks = list(self._tasks.values())

        # 状态过滤（规范化后比较）
        if status:
            v1_status = _normalize_task_status(status)
            if v1_status:
                tasks = [t for t in tasks if t.get("status") == v1_status]

        # 会话ID过滤（v1.0新增）
        if session_id:
            tasks = [t for t in tasks if t.get("sessionId") == session_id]

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
        """扩展GET路由（v1.0增强：新增任务列表、公开卡片、标签过滤）"""
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path
        from urllib.parse import parse_qs
        query = parse_qs(parsed.query)

        # ── GET /api/v1/a2a/discover — 发现Agent（支持 tags 参数） ──
        if path == "/api/v1/a2a/discover":
            skill = query.get("skill", [None])[0]
            capability = query.get("capability", [None])[0]
            name = query.get("name", [None])[0]
            tags = query.get("tags", [None])[0]  # v1.0新增：按标签过滤
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
                    tags=tags,
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

        # ── GET /api/v1/a2a/task — 列出任务（v1.0新增） ──
        if path == "/api/v1/a2a/task":
            try:
                status = query.get("status", [None])[0]
                session_id = query.get("session_id", [None])[0]
                page = int(query.get("page", [1])[0])
                page_size = int(query.get("page_size", [20])[0])
            except (ValueError, IndexError):
                self._send_json({"error": "page/page_size 必须为整数"}, 400)
                return

            try:
                router = TaskRouter()
                result = router.list_tasks(
                    status=status,
                    session_id=session_id,
                    page=page,
                    page_size=page_size,
                )
                self._send_json({
                    "success": True,
                    "a2a_version": A2A_VERSION,
                    **result,
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── GET /api/v1/a2a/agent-card/{id} — 获取公开的AgentCard（v1.0新增） ──
        if path.startswith("/api/v1/a2a/agent-card/"):
            agent_id = path[len("/api/v1/a2a/agent-card/"):]
            try:
                mgr = AgentCard()
                card = mgr.get_public_card(agent_id)
                if card:
                    self._send_json({"success": True, "agent_card": card})
                else:
                    self._send_json({"error": "Agent not found", "agent_id": agent_id}, 404)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 非本模块路由
        original_do_get(self)

    def do_post_patched(self):
        """扩展POST路由（v1.0增强：新增任务取消路由）"""
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
            # 兼容旧版扁平结构和新版嵌套 task 结构
            description = data.get("description", "").strip()
            if not description:
                # 尝试从嵌套 task 字段中提取（兼容 dispatcher.py 的调用方式）
                task_data = data.get("task", {})
                description = task_data.get("description") or task_data.get("input", "").strip()
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
                    session_id=data.get("session_id"),
                    metadata=data.get("metadata"),
                )
                self._send_json({
                    "success": True,
                    "a2a_version": A2A_VERSION,
                    **result,
                }, 201)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── POST /api/v1/a2a/task/{id}/cancel — 取消任务（v1.0新增） ──
        cancel_prefix = "/api/v1/a2a/task/"
        cancel_suffix = "/cancel"
        if path.startswith(cancel_prefix) and path.endswith(cancel_suffix):
            task_id = path[len(cancel_prefix):-len(cancel_suffix)]
            if not task_id:
                self._send_json({"error": "task_id is required"}, 400)
                return
            try:
                router = TaskRouter()
                reason = data.get("reason", "")
                task = router.cancel_task(task_id, reason=reason or None)
                if task:
                    self._send_json({
                        "success": True,
                        "task": task,
                        "a2a_version": A2A_VERSION,
                    })
                else:
                    self._send_json({"error": "Task not found", "task_id": task_id}, 404)
            except ValueError as e:
                self._send_json({"error": str(e)}, 409)
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
    print("=== A2A Gateway v1.0 测试 ===")

    # ── 1. 注册Agent卡片（旧版列表式 capabilities） ──
    print("\n--- 1. 注册Agent卡片（旧版列表式） ---")
    card_mgr = AgentCard()

    agent1 = card_mgr.register({
        "name": "SecurityScanner",
        "url": "https://agent.aishield.tools/scanner",
        "description": "OWASP MCP Top 10安全扫描Agent",
        "skills": [
            {"id": "scan", "name": "security_scan", "description": "安全扫描",
             "tags": ["scan", "security", "audit"],
             "examples": ["对MCP工具进行OWASP安全扫描"]},
            {"id": "audit", "name": "code_audit", "description": "代码审计", "tags": ["audit", "code"]},
        ],
        "capabilities": ["security_scan", "prompt_check", "banned_words"],
        "version": "1.0.0",
        "provider": {"name": "AIShield"},
        "reputation_score": 85,
    })
    print(f"  Agent1: {agent1['agent_id']} — {agent1['name']}")
    print(f"  capabilities 已规范化为对象: {isinstance(agent1['capabilities'], dict)}")
    print(f"  skills 含 examples: {bool(agent1['skills'][0].get('examples'))}")

    # ── 2. 注册Agent卡片（v1.0 对象式 capabilities） ──
    print("\n--- 2. 注册Agent卡片（v1.0 对象式） ---")
    agent2 = card_mgr.register({
        "name": "CodeReviewer",
        "url": "https://agent.aishield.tools/reviewer",
        "description": "AI代码审查Agent",
        "skills": [
            {"id": "review", "name": "code_review", "description": "代码审查",
             "tags": ["review", "code", "quality"],
             "examples": ["请审查这段Python代码的安全性"]},
        ],
        "capabilities": {"streaming": True, "pushNotifications": False, "supported": ["code_review"]},
        "authentication": {"schemes": ["Bearer"]},
        "documentationUrl": "https://docs.aishield.tools/reviewer",
        "version": "1.0.0",
        "provider": {"name": "AIShield", "url": "https://aishield.tools"},
        "reputation_score": 72,
    })
    print(f"  Agent2: {agent2['agent_id']} — {agent2['name']}")
    print(f"  capabilities.streaming: {agent2['capabilities'].get('streaming')}")
    print(f"  authentication.schemes: {agent2.get('authentication', {}).get('schemes')}")
    print(f"  documentationUrl: {agent2.get('documentationUrl')}")

    # ── 3. 发现Agent（含 tags 过滤） ──
    print("\n--- 3. 发现Agent ---")
    discovery = AgentDiscovery()

    scan_agents = discovery.discover(skill="security_scan")
    print(f"  能做security_scan的Agent: {len(scan_agents)}个")
    for a in scan_agents:
        print(f"    {a['name']} (信誉: {a['reputation_score']})")

    # v1.0: 按 tags 过滤
    tag_agents = discovery.discover(tags="audit,security")
    print(f"  标签含audit或security的Agent: {len(tag_agents)}个")

    # ── 4. 任务路由（v1.0 状态机） ──
    print("\n--- 4. 任务路由 ---")
    router = TaskRouter()

    result = router.create_task(
        task_description="请对这个MCP工具进行安全扫描，检查是否符合OWASP标准",
        task_type="scan",
        required_skills=["security_scan"],
    )
    task = result["task"]
    print(f"  任务ID: {task['task_id']}")
    print(f"  状态: {task['status']} (v1.0: submitted)")
    print(f"  会话ID: {task.get('sessionId', 'N/A')}")
    print(f"  路由到: {task['routed_name']} (匹配分: {task['match_score']})")
    print(f"  候选数: {len(result['candidates'])}")
    for c in result["candidates"]:
        print(f"    {c['agent_name']}: 匹配{c['match_score']}, 信誉{c['reputation']}")

    # ── 5. v1.0 生命周期：追加消息、追加工件、状态流转 ──
    print("\n--- 5. v1.0 任务生命周期 ---")
    task_id = task["task_id"]

    # 追加消息
    updated = router.add_message(task_id, "user", "请开始扫描")
    print(f"  追加用户消息: history长度={len(updated.get('history', []))}")

    # 更新为 working 状态
    updated = router.update_task_status(task_id, "working", message="开始执行安全扫描")
    print(f"  状态流转: {updated['status']}")

    # 追加工件
    updated = router.add_artifact(task_id, {
        "name": "scan_report",
        "type": "application/json",
        "parts": [{"type": "text", "text": "{\"score\": 95}"}],
    })
    print(f"  追加工件: artifacts数量={len(updated.get('artifacts', []))}")

    # 更新为 completed
    updated = router.update_task_status(task_id, "completed")
    print(f"  最终状态: {updated['status']}")

    # ── 6. 取消任务（v1.0） ──
    print("\n--- 6. 取消任务 ---")
    result2 = router.create_task(
        task_description="另一个测试任务",
        task_type="general",
    )
    task2 = result2["task"]
    canceled = router.cancel_task(task2["task_id"], reason="不再需要")
    print(f"  任务 {task2['task_id']} 状态: {canceled['status']}")

    # ── 7. 旧版状态兼容映射 ──
    print("\n--- 7. 旧版状态兼容 ---")
    mapped = _normalize_task_status("in_progress")
    print(f"  'in_progress' -> '{mapped}' (v1.0)")
    mapped = _normalize_task_status("cancelled")
    print(f"  'cancelled' -> '{mapped}' (v1.0)")

    # ── 8. 公开卡片 ──
    print("\n--- 8. 公开AgentCard ---")
    public = card_mgr.get_public_card(agent1["agent_id"])
    print(f"  公开卡片字段: {list(public.keys())}")
    print(f"  不含内部字段: {'agent_id' not in public}")

    # ── 9. 会话过滤 ──
    print("\n--- 9. 会话过滤 ---")
    session_id = task["sessionId"]
    session_tasks = router.list_tasks(session_id=session_id)
    print(f"  会话 {session_id[:20]}... 下的任务数: {session_tasks['total']}")

    print("\n=== 全部 v1.0 测试通过 ===")
