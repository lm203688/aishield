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


def _append_event(event: str, did: str, actor: str = "", result: str = "ok",
                  reason: str = "") -> dict:
    """
    追加一条身份审计事件到 data/identity_events.jsonl。

    「注册 → 撤销」必须可回放，否则注销就只是把记录改了个 status，事后无从
    追究是谁在什么时候把哪个 DID 摘掉的。事件文件是 append-only：写不进也要
    不能让主流程挂掉，所以吞异常但绝不静默伪造成功。
    """
    rec = {"ts": _now_iso(), "event": event, "did": did,
           "actor": actor, "result": result, "reason": reason}
    try:
        _ensure_data_dir()
        os.makedirs(os.path.dirname(EVENTS_FILE) or ".", exist_ok=True)
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as exc:                      # pragma: no cover - 磁盘异常
        rec["result"] = "event_write_failed"
        rec["reason"] = f"{type(exc).__name__}: {exc}"
    return rec


# ══════════════════════════════════════════════
#  身份鉴权错误（语义化异常，HTTP 层按码映射）
# ══════════════════════════════════════════════

class IdentityAuthError(Exception):
    """注册凭据缺失 / 失效 → HTTP 401。"""


class IdentityForbidden(Exception):
    """凭据有效但不属于该 Agent 的归属方 → HTTP 403。"""


# ══════════════════════════════════════════════
#  注册凭据（Registration Token）
# ══════════════════════════════════════════════

TOKENS_FILE = os.path.join(_DATA_DIR, "registration_tokens.json")
EVENTS_FILE = os.path.join(_DATA_DIR, "identity_events.jsonl")
_TOKEN_TTL_SECONDS = 3600          # 默认 1 小时有效期
_REVOKE_TOKEN_BYTES = 16           # 撤销码熵度

_TOKEN_PREFIX = "rt_"
_IDENTITY_TOKEN_TTL_SECONDS = 3600  # 身份凭证签发令牌有效期（#367 L1）
_IDENTITY_TOKEN_PREFIX = "idt_"


def _hash_identity_token(token) -> str:
    return hashlib.sha256(str(token or "").encode()).hexdigest()


class RegistrationTokenAuthority:
    """
    注册凭据签发 / 校验 / 撤销。

    为什么需要它（2026-10-03 身份锚点闭环）：
    ``POST /api/v1/identity/register`` 原来是**裸端点** —— 任何人都能往公开注册表里
    写一个 DID，却没有办法把它取回来或注销掉。核线脚本一句话就留下了
    ``did:aishield:f3a4f5cec744``（name=probe）这种谁也删不掉的脏记录。
    这里引入「注册凭据 → 归属 → 撤销码」三段式：

        issue(owner)  → 一次性凭据，绑定 owner（明文只出现这一次，只存 sha256）
        consume(tok)  → 注册时消费，token 立即失效；owner 必须与 body 的 owner 一致
        revoke(owner) → 凭据可提前作废

    凭据不存明文，owner 不匹配一律 403，过期/已用一律 401。

    持久化: data/registration_tokens.json（该文件在 .gitignore 内，不进仓库）
    """

    def __init__(self, ttl: int = _TOKEN_TTL_SECONDS):
        self.ttl = ttl

    # ── 存储 ──
    def _load(self):
        return _load_json(TOKENS_FILE, {"tokens": {}}) or {"tokens": {}}

    def _save(self, data):
        _ensure_data_dir()
        _save_json(TOKENS_FILE, data)

    # ── 对外 API ──
    def issue(self, owner: str, ttl: int | None = None) -> dict:
        """签发一枚注册凭据。明文 token 只在这一次返回里出现。"""
        owner = (owner or "").strip()
        if not owner:
            raise ValueError("owner is required to issue a registration token")
        ttl = self.ttl if ttl is None else ttl
        token_id = uuid.uuid4().hex[:16]
        raw = _TOKEN_PREFIX + uuid.uuid4().hex
        expires = datetime.now(TZ) + timedelta(seconds=max(1, int(ttl)))
        record = {
            "token_id": token_id,
            "token_hash": hashlib.sha256(raw.encode()).hexdigest(),
            "owner": owner,
            "issued_at": _now_iso(),
            "expires_at": expires.isoformat(),
            "consumed_at": None,
            "revoked_at": None,
        }
        data = self._load()
        data.setdefault("tokens", {})[token_id] = record
        self._save(data)
        return {
            "token": raw,
            "token_id": token_id,
            "owner": owner,
            "expires_at": record["expires_at"],
        }

    def _live(self, record: dict) -> bool:
        if record.get("revoked_at"):
            return False
        if record.get("consumed_at"):
            return False
        exp = record.get("expires_at", "")
        if exp:
            try:
                return datetime.fromisoformat(exp) > datetime.now(TZ)
            except ValueError:
                return False
        return True

    def consume(self, token: str, owner: str | None = None) -> str:
        """
        校验并消费一枚注册凭据，返回被消费的 ``token_id``。

        失败抛 IdentityAuthError（401 语义）；owner 对不上抛 IdentityForbidden（403）。
        """
        if not token or not isinstance(token, str):
            raise IdentityAuthError("registration_token required")
        digest = hashlib.sha256(token.encode()).hexdigest()
        data = self._load()
        found = None
        token_id = None
        for tid, rec in data.get("tokens", {}).items():
            if rec.get("token_hash") == digest:
                found = rec
                token_id = tid
                break
        if found is None:
            raise IdentityAuthError("registration_token is not valid")
        if not self._live(found):
            reason = "already used" if found.get("consumed_at") else (
                "revoked" if found.get("revoked_at") else "expired")
            raise IdentityAuthError(f"registration_token is {reason}")
        if owner is not None and (owner or "").strip() != found.get("owner"):
            raise IdentityForbidden(
                "registration_token does not belong to this owner")
        found["consumed_at"] = _now_iso()
        self._save(data)
        return token_id

    def revoke(self, token_id: str, owner: str | None = None) -> bool:
        """提前作废一枚凭据（owner 可选校验，对不上返回 False）。"""
        data = self._load()
        rec = data.get("tokens", {}).get(token_id)
        if not rec:
            return False
        if owner is not None and (owner or "").strip() != rec.get("owner"):
            return False
        if rec.get("revoked_at") or rec.get("consumed_at"):
            return False
        rec["revoked_at"] = _now_iso()
        self._save(data)
        return True


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
                capabilities=None, owner=None, registration_token=None):
        """
        注册一个新的Agent

        Args:
            name (str):            Agent名称
            did (str, opt):        去中心化身份（为空则自动生成）
            public_key (str):      公钥
            capabilities (list):    能力列表
            owner (str):            所有者（必须与注册凭据的 owner 一致）
            registration_token (str): 一次性注册凭据，见 RegistrationTokenAuthority

        无注册凭据 → IdentityAuthError（401）。凭据过期/已用/不属于该 owner
        → IdentityAuthError / IdentityForbidden。DID 重复仍是 ValueError（409）。

        Returns:
            dict: Agent注册信息（含明文 ``revoke_token``，仅此一次；
                  内部只落它的 sha256）
        """
        self._load()

        owner = (owner or "").strip()

        # ── 归属校验：裸端点注册是不允许的（test_linkages 长期期望 401）──
        if not owner:
            raise IdentityAuthError("owner is required")
        authority = RegistrationTokenAuthority()
        if not registration_token:
            raise IdentityAuthError("registration_token required")
        token_id = authority.consume(registration_token, owner=owner)

        # 校验通过才生成 DID，避免「凭据失效但 DID 已被占用」的脏半状态
        if not did:
            did = generate_did()

        # 检查DID是否已存在
        if did in self._agents:
            raise ValueError(f"Agent DID '{did}' 已注册")

        # 撤销码 + 身份凭证签发令牌：明文只在返回值里出现一次，库里只留 hash
        revoke_plain = uuid.uuid4().hex[:_REVOKE_TOKEN_BYTES * 2]
        # 注册「不直接」签发可验证凭证：注册凭据是一次性的、注册时已消费，
        # 拿它去换 VC 必然 401（#367 第一版就栽在这）。所以注册成功时顺带签一枚
        # **身份凭证签发令牌**，把「注册 → 签发 VC」两步分开且各自一次性。
        idt_plain = _IDENTITY_TOKEN_PREFIX + uuid.uuid4().hex
        idt_expires = datetime.now(TZ) + timedelta(
            seconds=_IDENTITY_TOKEN_TTL_SECONDS)

        # 构建Agent信息
        agent_info = {
            "name": name,
            "did": did,
            "public_key": public_key or "",
            "capabilities": capabilities or [],
            "owner": owner,
            "reputation_score": 50,         # 初始信誉分
            "reputation_level": "standard", # 初始等级
            "registered_at": _now_iso(),
            "updated_at": _now_iso(),
            "status": "active",
            "revoked_at": None,
            "revoke_token_hash": hashlib.sha256(revoke_plain.encode()).hexdigest(),
            "registration_token_id": token_id,
            "identity_token_id": uuid.uuid4().hex[:16],
            "identity_token_hash": hashlib.sha256(idt_plain.encode()).hexdigest(),
            "identity_token_expires": idt_expires.isoformat(),
            "identity_token_consumed_at": None,
        }

        self._agents[did] = agent_info
        self._save()
        _append_event("register", did, actor=owner, result="ok")

        return dict(agent_info, revoke_token=revoke_plain,
                    identity_token=idt_plain)

    # ── 身份凭证签发令牌（#367 L1 可移植身份）──────────────────────
    def issue_identity_token(self, did: str, owner: str | None = None,
                             ttl: int | None = None) -> dict:
        """为已注册的 agent 签一枚**身份凭证签发令牌**（一次性，绑定 did+owner）。

        这是「注册凭据 → 归属 → 签发可验证凭证」链条的第三环。它不能复用
        registration_token：那个凭据在 register() 里已经被 consume 掉了，再拿
        来换 VC 一定 401；语义上两件事也不该共用一枚凭据（共用 = 一枚凭据打通
        两个动作，任何一步的重放都会同时贯通两步）。

        返回 {"token", "token_id", "did", "owner", "expires_at"}；明文只出现在
        这一次，库里只留 sha256。
        """
        self._load()
        agent = self._agents.get(did)
        if not isinstance(agent, dict):
            raise ValueError(f"Agent DID '{did}' 未注册")
        if owner is not None and (owner or "").strip() != (agent.get("owner") or ""):
            raise IdentityForbidden("identity token does not belong to this owner")
        ttl = _IDENTITY_TOKEN_TTL_SECONDS if ttl is None else ttl
        plain = _IDENTITY_TOKEN_PREFIX + uuid.uuid4().hex
        expires = datetime.now(TZ) + timedelta(seconds=max(1, int(ttl)))
        agent["identity_token_id"] = uuid.uuid4().hex[:16]
        agent["identity_token_hash"] = hashlib.sha256(plain.encode()).hexdigest()
        agent["identity_token_expires"] = expires.isoformat()
        agent["identity_token_consumed_at"] = None
        self._save()
        _append_event("identity_token", did, actor=owner or agent.get("owner"),
                      result="ok")
        return {"token": plain, "token_id": agent["identity_token_id"],
                "did": did, "owner": agent.get("owner"),
                "expires_at": expires.isoformat()}

    def consume_identity_token(self, did: str, token,
                              owner: str | None = None) -> str:
        """校验并消费一枚身份凭证签发令牌，返回 token_id。

        无效/已用/过期抛 IdentityAuthError（401 语义），归属不符抛
        IdentityForbidden（403）。
        """
        self._load()
        agent = self._agents.get(did)
        if not isinstance(agent, dict):
            raise IdentityAuthError("agent not found")
        if owner is not None and (owner or "").strip() != (agent.get("owner") or ""):
            raise IdentityForbidden("identity token does not belong to this owner")
        if _hash_identity_token(token) != agent.get("identity_token_hash"):
            raise IdentityAuthError("identity_token is not valid")
        if agent.get("identity_token_consumed_at"):
            raise IdentityAuthError("identity_token is already used")
        exp = agent.get("identity_token_expires") or ""
        if exp:
            try:
                if datetime.fromisoformat(exp) <= datetime.now(TZ):
                    raise IdentityAuthError("identity_token is expired")
            except ValueError:
                raise IdentityAuthError("identity_token expiry is malformed")
        agent["identity_token_consumed_at"] = _now_iso()
        self._save()
        return agent["identity_token_id"]

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
        停用Agent（内部使用，不带归属校验；对外请走 revoke_agent）

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

    @staticmethod
    def public_view(agent: dict) -> dict:
        """
        对外可见视图：剥掉所有「能当凭据复用」的字段。

        ``revoke_token_hash`` / ``registration_token_id`` 一旦漏出去，注册表
        就被别人拿去越权注销了；``identity_token_hash`` / ``identity_token_id``
        漏出去则等于把「替这个 agent 签身份凭证」的能力送人 —— 同样是致命伤。
        """
        if not isinstance(agent, dict):
            return {}
        return {k: v for k, v in agent.items()
                if k not in ("revoke_token_hash", "registration_token_id",
                             "identity_token_hash", "identity_token_id")}

    def purge_inactive(self, keep_active: bool = False) -> int:
        """
        运维清理：删除已 inactive / 已 revoked 的记录，返回删除条数。

        给脚本用（``scripts/identity_maintenance.py``），不是 HTTP 端点 ——
        身份注册表有删除能力就等于有破坏能力，不该裸奔在公网。
        """
        self._load()
        before = len(self._agents)
        if keep_active:
            self._agents = {d: a for d, a in self._agents.items()
                            if a.get("status") == "active"}
        else:
            self._agents = {}
        removed = before - len(self._agents)
        if removed:
            self._save()
        return removed

    def revoke_agent(self, did, owner=None, revoke_token=None):
        """
        注销（撤销）一个 Agent —— 身份锚点闭环的收口动作。

        三档结果：
          不存在            → None                      （HTTP 404）
          归属/撤销码不匹配   → IdentityForbidden          （HTTP 403，越权必拦）
          已是 inactive      → False                     （幂等，不再写审计）
          成功              → True                      （status=inactive + revoked_at + 事件）

        匹配判定：``owner`` 与记录的 owner 相等，或 ``revoke_token`` 的 sha256
        与记录的 ``revoke_token_hash`` 相等（两者任一即可，满足不同调用形态）。
        """
        self._load()
        agent = self._agents.get(did)
        if agent is None:
            return None

        owner = (owner or "").strip()
        matched = False
        if owner and owner == (agent.get("owner") or ""):
            matched = True
        elif revoke_token and agent.get("revoke_token_hash") == \
                hashlib.sha256(str(revoke_token).encode()).hexdigest():
            matched = True

        if not matched:
            raise IdentityForbidden(
                "not the owner of this agent; provide owner or revoke_token")

        if agent.get("status") == "inactive":
            _append_event("revoke", did, actor=owner or "revoke_token",
                          result="noop", reason="already inactive")
            return False

        agent["status"] = "inactive"
        agent["revoked_at"] = _now_iso()
        agent["updated_at"] = _now_iso()
        self._agents[did] = agent
        self._save()
        _append_event("revoke", did, actor=owner or "revoke_token",
                      result="ok")
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

        # ── POST /api/v1/identity/register — 注册Agent（须带注册凭据）──
        if path == "/api/v1/identity/register":
            name = data.get("name", "").strip()
            if not name:
                self._send_json({"error": "name is required"}, 400)
                return
            token = data.get("registration_token") or data.get("token")
            if not token:
                self._send_json(
                    {"error": "missing required field: registration_token"}, 401)
                return

            try:
                reg = AgentRegistration()
                agent = reg.register(
                    name=name,
                    did=data.get("did"),
                    public_key=data.get("public_key"),
                    capabilities=data.get("capabilities"),
                    owner=data.get("owner"),
                    registration_token=token,
                )
                self._send_json({"success": True, "agent": agent}, 201)
            except IdentityAuthError as e:
                self._send_json({"error": str(e)}, 401)
                return
            except IdentityForbidden as e:
                self._send_json({"error": str(e)}, 403)
                return
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
