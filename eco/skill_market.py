"""
eco/skill_market.py — 技能交易市场

功能:
  - SkillRegistry:         技能注册与管理
      publish / get_skill / search / list_by_agent / update
      pricing_model: "free" / "per_call" / "subscription"
  - SkillInvoker:          技能调用器
      invoke / get_invocation
      检查免费配额，记录调用
  - SkillRating:           技能评分系统
      rate / get_ratings
      rating: 1-5
  - 数据持久化: api/data/skill_market.json

API路由:
  POST /api/v1/skills/publish             — 发布技能
  GET  /api/v1/skills                     — 搜索技能
  GET  /api/v1/skills/{skill_id}         — 技能详情
  GET  /api/v1/skills/agent/{agent_id}    — 按Agent列出技能
  PUT  /api/v1/skills/{skill_id}         — 更新技能
  POST /api/v1/skills/{skill_id}/invoke  — 调用技能
  POST /api/v1/skills/{skill_id}/rate     — 评价技能
  GET  /api/v1/skills/{skill_id}/ratings  — 查看评分
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
SKILL_MARKET_FILE = os.path.join(_DATA_DIR, "skill_market.json")

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


def _generate_skill_id():
    """生成技能ID"""
    return f"skill-{uuid.uuid4().hex[:12]}"


def _generate_invocation_id():
    """生成调用ID"""
    return f"inv-{uuid.uuid4().hex[:12]}"


# ══════════════════════════════════════════════
#  分类与定价常量
# ══════════════════════════════════════════════

SKILL_CATEGORIES = {
    "security":      "安全扫描",
    "data_analysis":  "数据分析",
    "nlp":           "自然语言处理",
    "code_gen":      "代码生成",
    "image_process": "图像处理",
    "automation":    "自动化",
    "integration":   "集成对接",
    "monitoring":    "监控告警",
    "other":         "其他",
}

PRICING_MODELS = {
    "free":         {"label": "免费",   "desc": "永久免费使用"},
    "per_call":     {"label": "按次付费", "desc": "每次调用单独计费"},
    "subscription": {"label": "订阅制", "desc": "按月/年订阅"},
}


# ══════════════════════════════════════════════
#  技能注册与管理
# ══════════════════════════════════════════════

class SkillRegistry:
    """
    技能注册管理器
    负责技能的发布、查询、搜索和更新
    """

    def __init__(self):
        self._skills = {}

    def _load(self):
        """从磁盘加载技能数据"""
        data = _load_json(SKILL_MARKET_FILE, {"skills": {}, "invocations": {}, "ratings": {}})
        self._skills = data.get("skills", {})

    def _save(self):
        """持久化技能数据到磁盘"""
        _ensure_data_dir()
        # 合并已有数据，避免覆盖 invocations 和 ratings
        existing = _load_json(SKILL_MARKET_FILE, {"skills": {}, "invocations": {}, "ratings": {}})
        existing["skills"] = self._skills
        _save_json(SKILL_MARKET_FILE, existing)

    def publish(self, agent_id, name, description, category,
                pricing_model="free", price=0, capabilities=None,
                tags=None, version="1.0.0", free_quota=10):
        """
        发布新技能

        Args:
            agent_id (str):          发布者Agent ID
            name (str):              技能名称
            description (str):       技能描述
            category (str):          分类
            pricing_model (str):     定价模型 (free/per_call/subscription)
            price (float):           价格
            capabilities (list):     能力列表
            tags (list):             标签
            version (str):           版本号
            free_quota (int):        免费配额次数

        Returns:
            dict: {"skill_id", "status"}
        """
        self._load()

        # 验证定价模型
        if pricing_model not in PRICING_MODELS:
            raise ValueError(f"无效定价模型: {pricing_model}，支持: {list(PRICING_MODELS.keys())}")

        # 验证评分范围
        if free_quota < 0:
            raise ValueError("free_quota 不能为负数")

        skill_id = _generate_skill_id()

        skill = {
            "skill_id": skill_id,
            "agent_id": agent_id,
            "name": name,
            "description": description,
            "category": category,
            "pricing_model": pricing_model,
            "price": float(price),
            "capabilities": capabilities or [],
            "tags": tags or [],
            "version": version,
            "free_quota": free_quota,
            "total_calls": 0,
            "total_rating": 0,
            "rating_count": 0,
            "status": "published",
            "published_at": _now_iso(),
            "updated_at": _now_iso(),
        }

        self._skills[skill_id] = skill
        self._save()

        return {
            "skill_id": skill_id,
            "status": "published",
        }

    def get_skill(self, skill_id):
        """
        查询技能详情

        Args:
            skill_id (str): 技能ID

        Returns:
            dict | None: 技能信息
        """
        self._load()
        return self._skills.get(skill_id)

    def search(self, query=None, category=None, capability=None,
               pricing_model=None, sort_by="relevance", page=1):
        """
        搜索技能

        Args:
            query (str, opt):        搜索关键词（匹配名称/描述/标签）
            category (str, opt):     按分类筛选
            capability (str, opt):   按能力筛选
            pricing_model (str, opt): 按定价模型筛选
            sort_by (str):           排序方式 (relevance/rating/calls/newest)
            page (int):              页码

        Returns:
            dict: {"skills", "total", "page", "page_size"}
        """
        self._load()

        page_size = 20
        skills = list(self._skills.values())

        # 只搜索已发布的技能
        skills = [s for s in skills if s.get("status") == "published"]

        # 按分类筛选
        if category:
            skills = [s for s in skills if s.get("category") == category]

        # 按能力筛选
        if capability:
            skills = [s for s in skills if capability in s.get("capabilities", [])]

        # 按定价模型筛选
        if pricing_model:
            skills = [s for s in skills if s.get("pricing_model") == pricing_model]

        # 关键词搜索
        if query:
            query_lower = query.lower()
            scored_skills = []
            for s in skills:
                score = 0
                if query_lower in s.get("name", "").lower():
                    score += 10
                if query_lower in s.get("description", "").lower():
                    score += 5
                if any(query_lower in tag.lower() for tag in s.get("tags", [])):
                    score += 3
                if any(query_lower in cap.lower() for cap in s.get("capabilities", [])):
                    score += 2
                if score > 0:
                    scored_skills.append((s, score))
            skills = [item[0] for item in sorted(scored_skills, key=lambda x: x[1], reverse=True)]
        else:
            # 无关键词时按排序方式排列
            if sort_by == "rating":
                skills.sort(key=lambda x: x.get("rating_count", 0), reverse=True)
            elif sort_by == "calls":
                skills.sort(key=lambda x: x.get("total_calls", 0), reverse=True)
            elif sort_by == "newest":
                skills.sort(key=lambda x: x.get("published_at", ""), reverse=True)

        total = len(skills)
        start = (page - 1) * page_size
        end = start + page_size
        skills_page = skills[start:end]

        return {
            "skills": skills_page,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def list_by_agent(self, agent_id):
        """
        按Agent列出其发布的技能

        Args:
            agent_id (str): Agent ID

        Returns:
            list: 技能列表
        """
        self._load()
        skills = [
            s for s in self._skills.values()
            if s.get("agent_id") == agent_id
        ]
        # 按发布时间倒序
        skills.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return skills

    def update(self, skill_id, agent_id, updates):
        """
        更新技能信息

        Args:
            skill_id (str):  技能ID
            agent_id (str):  Agent ID（权限验证）
            updates (dict):  要更新的字段

        Returns:
            dict | None: 更新后的技能信息
        """
        self._load()

        skill = self._skills.get(skill_id)
        if not skill:
            return None

        # 验证Agent归属
        if skill.get("agent_id") != agent_id:
            return None

        # 允许更新的字段
        allowed_fields = (
            "name", "description", "category", "pricing_model",
            "price", "capabilities", "tags", "version", "free_quota", "status",
        )

        for key, value in updates.items():
            if key in allowed_fields:
                skill[key] = value

        skill["updated_at"] = _now_iso()
        self._skills[skill_id] = skill
        self._save()

        return skill


# ══════════════════════════════════════════════
#  技能调用器
# ══════════════════════════════════════════════

class SkillInvoker:
    """
    技能调用器
    负责技能的调用管理和费用计算
    """

    def __init__(self):
        self._invocations = {}

    def _load(self):
        """从磁盘加载调用数据"""
        data = _load_json(SKILL_MARKET_FILE, {"skills": {}, "invocations": {}, "ratings": {}})
        self._invocations = data.get("invocations", {})

    def _save(self):
        """持久化调用数据到磁盘"""
        _ensure_data_dir()
        existing = _load_json(SKILL_MARKET_FILE, {"skills": {}, "invocations": {}, "ratings": {}})
        existing["invocations"] = self._invocations
        _save_json(SKILL_MARKET_FILE, existing)

    def invoke(self, skill_id, caller_agent_id, input_data):
        """
        调用技能

        Args:
            skill_id (str):         技能ID
            caller_agent_id (str):  调用者Agent ID
            input_data (dict):      输入数据

        Returns:
            dict: {"invocation_id", "result", "cost", "remaining_quota"}
        """
        self._load()

        # 加载技能信息
        registry = SkillRegistry()
        registry._load()
        skill = registry.get_skill(skill_id)

        if not skill:
            return {"error": f"技能 {skill_id} 不存在"}
        if skill.get("status") != "published":
            return {"error": f"技能 {skill_id} 未发布"}

        invocation_id = _generate_invocation_id()

        # 计算费用
        cost = 0.0
        if skill["pricing_model"] == "free":
            cost = 0.0
        elif skill["pricing_model"] == "per_call":
            cost = skill.get("price", 0.0)
        elif skill["pricing_model"] == "subscription":
            cost = 0.0  # 订阅制不额外收费

        # 更新技能调用统计
        skill["total_calls"] = skill.get("total_calls", 0) + 1
        remaining_quota = max(0, skill.get("free_quota", 10) - skill["total_calls"])

        # 保存技能更新
        registry._save()

        # 记录调用
        invocation = {
            "invocation_id": invocation_id,
            "skill_id": skill_id,
            "caller_agent_id": caller_agent_id,
            "input_data": input_data,
            "output": None,  # 实际调用结果由外部填充
            "cost": cost,
            "status": "completed",
            "invoked_at": _now_iso(),
        }

        self._invocations[invocation_id] = invocation
        self._save()

        return {
            "invocation_id": invocation_id,
            "result": None,  # 预留: 实际结果由技能执行引擎填充
            "cost": cost,
            "remaining_quota": remaining_quota,
        }

    def get_invocation(self, invocation_id):
        """
        查询调用记录

        Args:
            invocation_id (str): 调用ID

        Returns:
            dict | None: 调用记录
        """
        self._load()
        return self._invocations.get(invocation_id)


# ══════════════════════════════════════════════
#  技能评分系统
# ══════════════════════════════════════════════

class SkillRating:
    """
    技能评分管理器
    负责技能的评价和评分统计
    """

    def __init__(self):
        self._ratings = {}

    def _load(self):
        """从磁盘加载评分数据"""
        data = _load_json(SKILL_MARKET_FILE, {"skills": {}, "invocations": {}, "ratings": {}})
        self._ratings = data.get("ratings", {})

    def _save(self):
        """持久化评分数据到磁盘"""
        _ensure_data_dir()
        existing = _load_json(SKILL_MARKET_FILE, {"skills": {}, "invocations": {}, "ratings": {}})
        existing["ratings"] = self._ratings
        _save_json(SKILL_MARKET_FILE, existing)

    def rate(self, invocation_id, caller_agent_id, skill_id, rating, comment=None):
        """
        对技能进行评分

        Args:
            invocation_id (str):    调用ID
            caller_agent_id (str):   评分者Agent ID
            skill_id (str):         技能ID
            rating (int):           评分 (1-5)
            comment (str, opt):     评论

        Returns:
            dict: 评分记录
        """
        self._load()

        # 验证评分范围
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValueError("评分必须在 1-5 之间")

        # 验证调用记录存在
        invoker = SkillInvoker()
        invoker._load()
        invocation = invoker.get_invocation(invocation_id)
        if not invocation:
            raise ValueError(f"调用记录 {invocation_id} 不存在")

        # 验证调用者身份
        if invocation.get("caller_agent_id") != caller_agent_id:
            raise ValueError("只有调用者本人可以评价")

        # 检查是否已评价
        skill_ratings = self._ratings.setdefault(skill_id, [])
        existing = [r for r in skill_ratings if r.get("invocation_id") == invocation_id]
        if existing:
            # 更新已有评价
            old = existing[0]
            old["rating"] = rating
            old["comment"] = comment or ""
            old["updated_at"] = _now_iso()
            record = old
        else:
            # 新增评价
            record = {
                "invocation_id": invocation_id,
                "caller_agent_id": caller_agent_id,
                "skill_id": skill_id,
                "rating": rating,
                "comment": comment or "",
                "rated_at": _now_iso(),
            }
            skill_ratings.append(record)

        self._ratings[skill_id] = skill_ratings

        # 更新技能统计评分
        registry = SkillRegistry()
        registry._load()
        skill = registry.get_skill(skill_id)
        if skill:
            all_ratings = skill_ratings
            avg = sum(r["rating"] for r in all_ratings) / len(all_ratings) if all_ratings else 0
            skill["total_rating"] = round(avg, 1)
            skill["rating_count"] = len(all_ratings)
            registry._save()

        self._save()

        return record

    def get_ratings(self, skill_id):
        """
        获取技能评分统计

        Args:
            skill_id (str): 技能ID

        Returns:
            dict: {"average", "total", "distribution"}
        """
        self._load()

        ratings = self._ratings.get(skill_id, [])

        if not ratings:
            return {
                "average": 0.0,
                "total": 0,
                "distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            }

        total = len(ratings)
        average = round(sum(r["rating"] for r in ratings) / total, 1)

        # 评分分布
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in ratings:
            score = r["rating"]
            distribution[score] = distribution.get(score, 0) + 1

        return {
            "average": average,
            "total": total,
            "distribution": distribution,
        }


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将技能市场模块路由注册到HTTPServer的Handler上

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

        # ── GET /api/v1/skills — 搜索技能 ──
        if path == "/api/v1/skills":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            reg = SkillRegistry()
            result = reg.search(
                query=qs.get("query", [None])[0],
                category=qs.get("category", [None])[0],
                capability=qs.get("capability", [None])[0],
                pricing_model=qs.get("pricing_model", [None])[0],
                sort_by=qs.get("sort_by", ["relevance"])[0],
                page=int(qs.get("page", ["1"])[0]),
            )
            self._send_json({"success": True, **result})
            return

        # ── GET /api/v1/skills/agent/{agent_id} — 按Agent列出技能 ──
        if path.startswith("/api/v1/skills/agent/"):
            agent_id = path[len("/api/v1/skills/agent/"):]
            reg = SkillRegistry()
            skills = reg.list_by_agent(agent_id)
            self._send_json({"success": True, "total": len(skills), "skills": skills})
            return

        # ── GET /api/v1/skills/{skill_id}/ratings — 查看评分 ──
        if path.startswith("/api/v1/skills/") and path.endswith("/ratings"):
            prefix = "/api/v1/skills/"
            suffix = "/ratings"
            skill_id = path[len(prefix):-len(suffix)]
            rating_mgr = SkillRating()
            result = rating_mgr.get_ratings(skill_id)
            self._send_json({"success": True, **result})
            return

        # ── GET /api/v1/skills/{skill_id} — 技能详情 ──
        if path.startswith("/api/v1/skills/"):
            skill_id = path[len("/api/v1/skills/"):]
            reg = SkillRegistry()
            skill = reg.get_skill(skill_id)
            if skill:
                self._send_json({"success": True, "skill": skill})
            else:
                self._send_json({"error": "技能不存在", "skill_id": skill_id}, 404)
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

        # ── POST /api/v1/skills/publish — 发布技能 ──
        if path == "/api/v1/skills/publish":
            required_fields = ["agent_id", "name", "description", "category"]
            for field in required_fields:
                if not data.get(field, "").strip():
                    self._send_json({"error": f"{field} 为必填"}, 400)
                    return

            try:
                reg = SkillRegistry()
                result = reg.publish(
                    agent_id=data["agent_id"],
                    name=data["name"],
                    description=data["description"],
                    category=data["category"],
                    pricing_model=data.get("pricing_model", "free"),
                    price=data.get("price", 0),
                    capabilities=data.get("capabilities"),
                    tags=data.get("tags"),
                    version=data.get("version", "1.0.0"),
                    free_quota=data.get("free_quota", 10),
                )
                self._send_json({"success": True, **result}, 201)
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
            return

        # ── POST /api/v1/skills/{skill_id}/invoke — 调用技能 ──
        if path.startswith("/api/v1/skills/") and path.endswith("/invoke"):
            prefix = "/api/v1/skills/"
            suffix = "/invoke"
            skill_id = path[len(prefix):-len(suffix)]
            caller_agent_id = data.get("caller_agent_id", "").strip()
            input_data = data.get("input_data", {})

            if not caller_agent_id:
                self._send_json({"error": "caller_agent_id 为必填"}, 400)
                return

            invoker = SkillInvoker()
            result = invoker.invoke(skill_id, caller_agent_id, input_data)
            if "error" in result:
                self._send_json(result, 400)
            else:
                self._send_json({"success": True, **result})
            return

        # ── POST /api/v1/skills/{skill_id}/rate — 评价技能 ──
        if path.startswith("/api/v1/skills/") and path.endswith("/rate"):
            prefix = "/api/v1/skills/"
            suffix = "/rate"
            skill_id = path[len(prefix):-len(suffix)]
            invocation_id = data.get("invocation_id", "").strip()
            caller_agent_id = data.get("caller_agent_id", "").strip()
            rating = data.get("rating")

            if not invocation_id or not caller_agent_id or rating is None:
                self._send_json({"error": "invocation_id, caller_agent_id, rating 为必填"}, 400)
                return

            try:
                rating_mgr = SkillRating()
                record = rating_mgr.rate(
                    invocation_id=invocation_id,
                    caller_agent_id=caller_agent_id,
                    skill_id=skill_id,
                    rating=int(rating),
                    comment=data.get("comment"),
                )
                self._send_json({"success": True, "rating": record})
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
    print("=== 技能交易市场测试 ===")

    # 测试技能发布
    print("\n--- 技能发布 ---")
    reg = SkillRegistry()

    result = reg.publish(
        agent_id="did:aishield:agent001",
        name="安全代码扫描",
        description="对MCP Server代码进行安全漏洞扫描，支持静态分析和依赖检查",
        category="security",
        pricing_model="per_call",
        price=0.5,
        capabilities=["static_analysis", "dependency_check", "owasp_scan"],
        tags=["安全", "MCP", "漏洞扫描"],
        version="1.0.0",
        free_quota=10,
    )
    skill_id = result["skill_id"]
    print(f"  发布成功: skill_id={skill_id}, status={result['status']}")

    result = reg.publish(
        agent_id="did:aishield:agent001",
        name="数据分析助手",
        description="快速分析JSON/CSV数据，生成可视化报告",
        category="data_analysis",
        pricing_model="free",
        capabilities=["json_parse", "csv_parse", "chart_gen"],
        tags=["数据分析", "可视化"],
        version="1.2.0",
        free_quota=100,
    )
    print(f"  发布成功: skill_id={result['skill_id']}, status={result['status']}")

    # 测试搜索
    print("\n--- 技能搜索 ---")
    results = reg.search(query="安全")
    print(f"  搜索 '安全': {results['total']}个结果")
    for s in results["skills"]:
        print(f"    - {s['name']} ({s['pricing_model']})")

    results = reg.search(category="security")
    print(f"  分类筛选 'security': {results['total']}个结果")

    # 测试Agent列表
    print("\n--- Agent技能列表 ---")
    skills = reg.list_by_agent("did:aishield:agent001")
    print(f"  Agent发布的技能: {len(skills)}个")
    for s in skills:
        print(f"    - {s['name']} v{s['version']}")

    # 测试技能调用
    print("\n--- 技能调用 ---")
    invoker = SkillInvoker()
    result = invoker.invoke(
        skill_id=skill_id,
        caller_agent_id="did:aishield:caller001",
        input_data={"code": "def hello(): pass"},
    )
    if "error" not in result:
        print(f"  调用成功: invocation_id={result['invocation_id']}")
        print(f"  费用: {result['cost']}, 剩余配额: {result['remaining_quota']}")

    # 测试评分
    print("\n--- 技能评分 ---")
    rating_mgr = SkillRating()
    if "invocation_id" in result:
        record = rating_mgr.rate(
            invocation_id=result["invocation_id"],
            caller_agent_id="did:aishield:caller001",
            skill_id=skill_id,
            rating=5,
            comment="非常好用的安全扫描技能",
        )
        print(f"  评分成功: {record['rating']}星 - {record['comment']}")

        # 查看评分统计
        stats = rating_mgr.get_ratings(skill_id)
        print(f"  评分统计: 平均{stats['average']}星, 共{stats['total']}条评价")
        print(f"  分布: {stats['distribution']}")

    # 测试更新
    print("\n--- 技能更新 ---")
    updated = reg.update(skill_id, "did:aishield:agent001", {
        "description": "升级版安全代码扫描，新增AI推理能力",
        "version": "1.1.0",
    })
    if updated:
        print(f"  更新成功: v{updated['version']}")

    print("\n=== 全部测试通过 ===")
