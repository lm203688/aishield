"""
eco/personal_agent.py — 个人 Agent 治理层（Personal Agent Governance Kernel）

触发场景（2026-09）：Meta Muse 上线 13 天 250 万下载、登顶美国 iOS 免费榜；
2026-09-18 开放 Connector Platform（muse.ai/platform）。ChatGPT agent / Claude agent
/ Gemini agent 也在跟进。个人 agent 从"能聊"进入"能办"时代，但每一款个人 agent
都是封闭体系，缺乏：

  1. 跨平台可验证的个人 Agent 身份（谁能证明"这个 Muse 实例是 Alice 的"？）
  2. 面向消费者的预算/风险守护（Stripe Link 只管单次卡号，不管决策质量）
  3. Connector / Skill 的独立第二意见（Meta 自己的审核之外，用户要中立评估）
  4. 行动 provenance（"我的 agent 是不是擅自订了酒店？"的可验证回执）

本模块把这四块建成一个零依赖的治理内核，任何个人 agent 都可以调用来
接入。定位与既有分工：
  - Enterprise 身份 → eco/kyad_compat.py (SD-JWT)
  - Agent Card 签名 → eco/agent_card.py (A2A v1.0 兼容)
  - 企业预算 → eco/spend_cap.py (reserve/commit/release 两阶段)
  - SOC 证据包 → eco/evidence_bundle.py (HMAC + OCSF/STIX/ATT&CK)
  - **个人 Agent 治理 → 本模块**（消费级、DID 面向自然人、可 dispute）

数据落 api/data/personal_agents.json（已被 .gitignore 覆盖）。
签名走 eco/crypto_sign（Ed25519 优先，HMAC 降级），零第三方依赖。
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import threading
import time
import uuid
from datetime import datetime, timezone, timedelta

try:
    from eco import crypto_sign as cs
except ImportError:
    import crypto_sign as cs

try:
    from eco import agent_card
except ImportError:  # 允许以脚本方式直接运行自测
    import agent_card

try:
    from eco import trust_protocol
except ImportError:  # 允许以脚本方式直接运行自测
    import trust_protocol

TZ = timezone(timedelta(hours=8))
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_BASE, "api", "data")
STORE_FILE = os.path.join(_DATA, "personal_agents.json")
HMAC_SECRET_FILE = os.path.join(_DATA, "personal_agent_hmac.json")

_lock = threading.RLock()

# 自然人身份 DID 方法：#441 起统一为自认证 did:key（公钥编码进 DID），
# 不再使用旧标签 did:aishield:pa:*。历史已存用户维持旧 DID（幂等返回）。


def get_pa_signer_did() -> str:
    """PAI 信任服务签名者 DID（#441：统一为自认证 did:key，密钥不可用回退旧标签）。"""
    try:
        return agent_card.get_signer_did()
    except Exception:
        return "did:aishield:trust-service"


# 兼容旧常量：模块级常量在导入时解析一次（密钥未生成则回退旧标签）。
PA_SIGNER_DID = get_pa_signer_did()

# 行动 provenance HMAC 链默认参数
CHUNK_TTL_DAYS = 90  # provenance 记录保留 90 天
MAX_TICKET_ACTIONS = 32

# ── 预算策略（消费级默认，比企业 spend_cap 保守） ──
PERSONAL_DEFAULT_LIMITS = {
    "CNY": {"per_tx": 200.0, "daily": 800.0, "weekly": 3000.0, "monthly": 8000.0},
    "USD": {"per_tx": 30.0,  "daily": 100.0, "weekly": 400.0,  "monthly": 1000.0},
}

# ── 高风险目标域名（触发 quote-first / 二次确认） ──
HIGH_RISK_DOMAIN_HINTS = (
    ".com/pay", ".payment", "checkout.", "billing.",
    "appleid.apple.com", "accounts.google.com", "id.microsoft.com",
    "bank.", "credit.", "wire.", "crypto.", "binance.", "coinbase.",
    "pay.", "stripe.", "paypal.",
)

# ── Connector 审核规则（复用 SKILL_EXTRA 的攻击面经验） ──
DANGEROUS_SCOPE_KEYWORDS = (
    "wallet", "payment", "spend", "finance", "x402", "stablecoin",
    "desktop", "screen", "mouse", "keyboard", "admin", "root", "sudo",
    "privileged", "system", "shell", "credential", "secret", "privatekey",
    "read_all", "write_all", "execute", "unrestricted",
)


# ══════════════════════════════════════════════════════════════
# Utils
# ══════════════════════════════════════════════════════════════

def _now():
    return datetime.now(TZ)


def _now_iso():
    return _now().isoformat()


def _short_id(prefix="id"):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _hash_hex(obj, secret=b""):
    """对 dict/list 做规范哈希，用于 HMAC 链和指纹。"""
    body = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if secret:
        return hmac.new(secret, body.encode("utf-8"), hashlib.sha256).hexdigest()
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _norm_user(user_id):
    u = (user_id or "").strip()
    if not u:
        raise ValueError("user_id 不能为空")
    # 允许 alphanumeric + _ - @ . / : —— 覆盖 email / did / agent instance id
    if re.fullmatch(r"[\w@.\-:/]+", u) is None:
        raise ValueError(f"user_id 含非法字符: {u!r}")
    return u


def _norm_currency(c):
    c = (c or "").strip().upper()
    if c == "USDC":
        return "USD"
    if c in ("RMB", "CNH"):
        return "CNY"
    return c


def _week_key(dt=None):
    # ISO 周（周一为一周起）
    d = dt or _now()
    iso_year, iso_week, _ = d.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _load_hmac_secret():
    """行动链的 HMAC 密钥（服务端持有，仅服务端可签名 action record）。"""
    if os.path.exists(HMAC_SECRET_FILE):
        try:
            with open(HMAC_SECRET_FILE, "r", encoding="utf-8") as f:
                return json.load(f)["secret"].encode("utf-8")
        except Exception:
            pass
    os.makedirs(_DATA, exist_ok=True)
    secret = uuid.uuid4().hex + uuid.uuid4().hex
    with open(HMAC_SECRET_FILE, "w", encoding="utf-8") as f:
        json.dump({"secret": secret, "created_at": _now_iso()}, f)
    return secret.encode("utf-8")


def _load():
    if os.path.exists(STORE_FILE):
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k in ("users", "agent_instances", "tickets", "consent_ledger",
                      "budget_ledger", "action_ledger", "connector_reviews",
                      "disputes"):
                data.setdefault(k, {})
            return data
        except Exception:
            pass
    return {"users": {}, "agent_instances": {}, "tickets": {},
            "consent_ledger": {}, "budget_ledger": {},
            "action_ledger": {}, "connector_reviews": {}, "disputes": {},
            "meta": {"created_at": _now_iso()}}


def _save(data):
    os.makedirs(_DATA, exist_ok=True)
    tmp = STORE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, STORE_FILE)


# ══════════════════════════════════════════════════════════════
# 1) Personal Agent Identity (PAI) —— 消费级 KYA
# ══════════════════════════════════════════════════════════════
#
# 与 kyad_compat (企业 SD-JWT) 的区别：
#   - DID 主体是自然人，不依赖企业 CA
#   - 每个自然人有多个 agent 实例（Muse / ChatGPT-agent / 自建），
#     每个实例有独立的 keypair，签自己发的 action
#   - Capability Ticket 是"用户对某个 agent 实例的一次授权"，
#     带 scope（域名白名单 / 金额上限 / 动作类型）+ TTL
# ══════════════════════════════════════════════════════════════

def create_personal_did(user_id, display_name=None, email=None):
    """为自然人创建 PAI 身份。幂等：已存在则返回现有。

    #441：自然人身份统一为自认证 ``did:key``。从 user_id 确定性派生 Ed25519
    密钥对（零依赖、纯标准库），DID = 公钥派生的 ``did:key:z...``——同一 user_id
    永远得到同一 DID（幂等 / 可复算），且密码学上自洽（可独立验签）。
    """
    user_id = _norm_user(user_id)
    with _lock:
        data = _load()
        existing = data["users"].get(user_id)
        if existing:
            return dict(existing, idempotent=True)
        # 稳定种子 → 确定性密钥对 → did:key
        seed = hashlib.sha256(
            ("aishield:pai:v1:" + user_id).encode("utf-8")).digest()
        did = trust_protocol.keypair_from_seed(seed).did
        rec = {
            "user_id": user_id,
            "did": did,
            "display_name": display_name or user_id,
            "email": email,
            "created_at": _now_iso(),
            "version": 1,
        }
        data["users"][user_id] = rec
        _save(data)
        return dict(rec)


def register_agent_instance(user_id, agent_name, provider, capabilities=None,
                            platform_hint=None, platform=None, platform_tier=None):
    """在用户 DID 下登记一个 agent 实例（如 Alice 的 Muse for iPhone）。

    platform (v4.8.1+): 结构化平台标识，与 eco.platform_registry 对齐。
        可以是：
          - str 形式（platform_id），如 "meta-muse" / "xai-grok-bot" / "bytedance-coze"
          - dict 形式，至少含 {"id": ..., "capabilities_needed": [...]}
        注册时会对 platform_id 做存在性检查（软失败：未知平台仍允许登记，
        但在返回值上标注 platform_known=False，便于上游告警）。
    platform_tier: 可选，标注该实例在此平台上的订阅等级（如 "free" /
        "super_grok_heavy" / "plus"），用于治理时的差异化策略。
    platform_hint: 保留旧字段做向后兼容，新代码应使用 platform。
    """
    user_id = _norm_user(user_id)
    if not agent_name or not provider:
        raise ValueError("agent_name 与 provider 均必填")
    # 结构化平台字段
    platform_rec = _resolve_platform_ref(platform, platform_hint)
    with _lock:
        data = _load()
        if user_id not in data["users"]:
            create_personal_did(user_id)
            data = _load()
        inst_id = _short_id("inst")
        did = data["users"][user_id]["did"]
        rec = {
            "instance_id": inst_id,
            "user_id": user_id,
            "parent_did": did,
            "agent_name": agent_name,
            "provider": provider,
            "platform_hint": platform_hint,  # 向后兼容
            "platform": platform_rec,        # v4.8.1+ 结构化
            "platform_tier": platform_tier,
            "capabilities": capabilities or [],
            "status": "active",
            "created_at": _now_iso(),
        }
        data["agent_instances"].setdefault(user_id, {})[inst_id] = rec
        _save(data)
        return dict(rec)


def _resolve_platform_ref(platform, platform_hint=None):
    """把 platform 参数（str/dict/None）解析成统一 dict。

    返回形如：
        {"id": "meta-muse", "known": True, "vendor": "Meta",
         "family": "consumer", "cny_accessible": "verified_blocked",
         "access_paths": ["connector_official", "mcp"],
         "capabilities_needed": [], "hint": "muse-ios"}
    """
    if not platform:
        # 仅用 hint，不查表
        return {"id": None, "known": False, "hint": platform_hint,
                "vendor": None, "family": None,
                "cny_accessible": None, "access_paths": []}
    # dict 输入
    if isinstance(platform, dict):
        pid = (platform.get("id") or "").strip().lower() or None
        rec = dict(platform)
        rec["id"] = pid
    elif isinstance(platform, str):
        pid = platform.strip().lower() or None
        rec = {"id": pid, "capabilities_needed": []}
    else:
        pid = None
        rec = {"id": None, "capabilities_needed": []}

    # 查表补齐
    known = False
    if pid:
        try:
            from eco import platform_registry as pr
        except Exception:
            pr = None
        if pr is not None:
            p = pr.get_platform(pid)
            if p:
                known = True
                rec["name"] = p.get("name")
                rec["vendor"] = p.get("vendor")
                rec["family"] = p.get("family")
                rec["cny_accessible"] = p.get("cny_accessible")
                rec["access_paths"] = p.get("access_paths", [])
                # 该平台内置治理能力（我们不必再补）
                rec["platform_governance"] = p.get("governance", [])
                # 该平台缺失、需要 AIShield 补的能力
                rec["governance_gaps"] = p.get("gaps", [])
            else:
                known = False
                rec["reason_unknown"] = "platform_id not in registry"
    rec["known"] = known
    rec["hint"] = platform_hint
    return rec


def get_platform_for_instance(user_id, instance_id):
    """反查某 agent 实例注册时的平台元信息（含治理缺口）。"""
    user_id = _norm_user(user_id)
    with _lock:
        data = _load()
        inst = data["agent_instances"].get(user_id, {}).get(instance_id)
        if not inst:
            return {"found": False, "error": "instance 不存在"}
        return {"found": True, "instance_id": instance_id,
                "agent_name": inst.get("agent_name"),
                "provider": inst.get("provider"),
                "platform": inst.get("platform"),
                "platform_tier": inst.get("platform_tier"),
                "platform_hint": inst.get("platform_hint"),
                "status": inst.get("status")}


def list_instances_by_platform(user_id, platform_id=None,
                                include_revoked=False):
    """列出某用户的所有实例，可过滤 platform。"""
    user_id = _norm_user(user_id)
    with _lock:
        data = _load()
        insts = data["agent_instances"].get(user_id, {})
    out = []
    for iid, inst in insts.items():
        if not include_revoked and inst.get("status") != "active":
            continue
        pid = ((inst.get("platform") or {}).get("id") or "")
        if platform_id and pid != platform_id.lower():
            continue
        out.append({"instance_id": iid, "agent_name": inst.get("agent_name"),
                    "provider": inst.get("provider"),
                    "platform": inst.get("platform"),
                    "status": inst.get("status")})
    return out


def revoke_agent_instance(user_id, instance_id, reason=""):
    """吊销 agent 实例（用户主动 or 平台侧安全事件）。"""
    user_id = _norm_user(user_id)
    with _lock:
        data = _load()
        insts = data["agent_instances"].get(user_id, {})
        inst = insts.get(instance_id)
        if not inst:
            return {"success": False, "reason": "instance 不存在"}
        inst["status"] = "revoked"
        revoked_at = _now_iso()
        inst["revoked_at"] = revoked_at
        inst["revoke_reason"] = reason
        # 连带吊销该实例的所有 ticket
        revoked_tickets = 0
        for tid, t in data["tickets"].get(user_id, {}).items():
            if t.get("instance_id") == instance_id and t.get("status") == "active":
                t["status"] = "revoked"
                t["revoked_at"] = revoked_at
                t["revoke_reason"] = f"instance revoked: {reason}"
                revoked_tickets += 1
        _save(data)
        return {"success": True, "instance_id": instance_id,
                "revoked_tickets": revoked_tickets}


# ── Capability Ticket ──
def create_capability_ticket(user_id, instance_id, actions, scope=None,
                             expires_in=3600, reason="", max_uses=None):
    """为 (user, instance) 签发一张授权票据。

    actions: 白名单动作，例如 ["send_email", "purchase"]
    scope:   可选边界，例如 {"to_domain": "mail.google.com",
                             "max_amount": 500, "currency": "CNY",
                             "allowed_categories": ["utilities"]}
    expires_in: 秒；默认 1h，最长 24h
    max_uses:   可选，最多消耗次数；None=无次数限制（仅 TTL 限制）
    返回的 ticket 可被 agent 侧出示、由 verifier 独立验证。
    """
    user_id = _norm_user(user_id)
    if not actions or not isinstance(actions, list):
        raise ValueError("actions 必须是非空列表")
    if len(actions) > MAX_TICKET_ACTIONS:
        raise ValueError(f"actions 数量超过 {MAX_TICKET_ACTIONS}")
    expires_in = max(60, min(int(expires_in), 24 * 3600))
    if max_uses is not None and (not isinstance(max_uses, int) or max_uses < 1):
        raise ValueError("max_uses 必须是 >=1 的整数或 None")
    with _lock:
        data = _load()
        inst = data["agent_instances"].get(user_id, {}).get(instance_id)
        if not inst:
            raise ValueError("instance 未登记，请先 register_agent_instance")
        if inst.get("status") != "active":
            raise ValueError(f"instance 状态异常: {inst.get('status')}")
        now = _now()
        rec = {
            "ticket_id": _short_id("ct"),
            "user_id": user_id,
            "instance_id": instance_id,
            "parent_did": data["users"][user_id]["did"],
            "actions": list(actions),
            "scope": scope or {},
            "reason": reason,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=expires_in)).isoformat(),
            "status": "active",
            "consumed": 0,
            "max_uses": max_uses,  # None = 无次数限制（TTL 内）
        }
        # 用服务端 HMAC secret 签，verifier 独立验证（同 evidence_bundle 模式）
        body = {k: v for k, v in rec.items() if k not in ("signature",)}
        rec["signature"] = _hash_hex(body, _load_hmac_secret())
        data["tickets"].setdefault(user_id, {})[rec["ticket_id"]] = rec
        _save(data)
        return dict(rec)


def verify_capability_ticket(ticket, allow_consumed=False):
    """验证 ticket 的完整性、时效、scope。

    不消耗 ticket（那是 check_and_consume 的事），仅做只读校验。
    """
    if not isinstance(ticket, dict) or "ticket_id" not in ticket:
        return {"valid": False, "reason": "not_a_ticket"}
    sig = ticket.pop("signature", None)
    if not sig:
        return {"valid": False, "reason": "unsigned"}
    body = dict(ticket)
    body.pop("signature", None)
    recalc = _hash_hex(body, _load_hmac_secret())
    if not hmac.compare_digest(recalc, sig):
        # 把 signature 塞回去
        ticket["signature"] = sig
        return {"valid": False, "reason": "signature_mismatch", "ticket": ticket}
    # 塞回
    ticket["signature"] = sig
    # 时效
    try:
        exp = datetime.fromisoformat(ticket.get("expires_at", ""))
    except Exception:
        return {"valid": False, "reason": "bad_expires_at", "ticket": ticket}
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=TZ)
    if _now() > exp:
        return {"valid": False, "reason": "expired", "expires_at": ticket["expires_at"]}
    if ticket.get("status") != "active":
        return {"valid": False, "reason": f"status={ticket.get('status')}",
                "ticket": ticket}
    max_uses = ticket.get("max_uses")
    if (not allow_consumed and max_uses is not None
            and ticket.get("consumed", 0) >= int(max_uses)):
        return {"valid": False, "reason": "exhausted",
                "consumed": ticket.get("consumed", 0),
                "max_uses": max_uses}
    return {"valid": True, "ticket_id": ticket["ticket_id"],
            "actions": ticket.get("actions"), "scope": ticket.get("scope"),
            "instance_id": ticket.get("instance_id")}


def check_and_consume_ticket(ticket, action, payload):
    """检查 ticket 是否授权该 action + payload 是否在 scope 内，通过后消耗一次。"""
    v = verify_capability_ticket(ticket)
    if not v["valid"]:
        return {"allowed": False, **v}
    if action not in v["actions"]:
        return {"allowed": False, "reason": "action_not_in_ticket",
                "action": action, "ticket_actions": v["actions"]}
    scope = v["scope"] or {}
    # scope 检查（子集匹配）
    if scope.get("max_amount") is not None and "amount" in payload:
        try:
            if float(payload["amount"]) > float(scope["max_amount"]):
                return {"allowed": False, "reason": "amount_over_scope",
                        "amount": payload["amount"], "max": scope["max_amount"]}
        except (TypeError, ValueError):
            return {"allowed": False, "reason": "bad_amount_in_payload"}
    if scope.get("to_domain") and payload.get("target_url"):
        try:
            from urllib.parse import urlparse
            host = urlparse(payload["target_url"]).hostname or ""
        except Exception:
            host = ""
        if host and host != scope["to_domain"] and not host.endswith("." + scope["to_domain"]):
            return {"allowed": False, "reason": "target_out_of_scope",
                    "target": host, "allowed_domain": scope["to_domain"]}
    if scope.get("allowed_categories") and payload.get("category"):
        if payload["category"] not in scope["allowed_categories"]:
            return {"allowed": False, "reason": "category_not_allowed",
                    "category": payload["category"],
                    "allowed": scope["allowed_categories"]}
    # 通过 → 消耗一次
    with _lock:
        data = _load()
        tk = data["tickets"].get(_norm_user(ticket.get("user_id")), {}).get(
            ticket["ticket_id"])
        if not tk:
            return {"allowed": False, "reason": "ticket_not_found"}
        tk["consumed"] = int(tk.get("consumed", 0)) + 1
        # 达到 max_uses 就自动过期
        if tk.get("max_uses") and tk["consumed"] >= tk["max_uses"]:
            tk["status"] = "exhausted"
        # 消耗后重签：consumed 是签名体的一部分，改了就重签，
        # 保证 ticket 每次消耗后仍能离线独立验证。
        body = {k: v for k, v in tk.items() if k != "signature"}
        tk["signature"] = _hash_hex(body, _load_hmac_secret())
        _save(data)
    return {"allowed": True, "ticket_id": ticket["ticket_id"],
            "consumed": tk["consumed"], "action": action}


# ══════════════════════════════════════════════════════════════
# 2) Personal Budget Guard —— 面向消费者的预算 + 风险守护
# ══════════════════════════════════════════════════════════════
#
# 与 spend_cap.py 的区别：
#   - spend_cap 管"支付层总额度"（企业采购，reserve/commit/release）
#   - 本模块管"个人消费者"（默认更严，加"周"粒度、加 target 站风险评分）
#   - 本模块不替代支付，只做 pre-flight check（quote-first 前置）
# ══════════════════════════════════════════════════════════════

def set_budget_policy(user_id, currency="CNY", per_tx=None, daily=None,
                      weekly=None, monthly=None, note=""):
    """设置个人预算策略。未显式设置的字段沿用默认。"""
    user_id = _norm_user(user_id)
    currency = _norm_currency(currency)
    if currency not in PERSONAL_DEFAULT_LIMITS:
        return {"success": False, "error": f"不支持的币种: {currency}"}
    with _lock:
        data = _load()
        entry = _load_budget_entry(data, user_id, currency)
        pol = entry.setdefault("policy", {})
        for key, val in (("per_tx", per_tx), ("daily", daily),
                         ("weekly", weekly), ("monthly", monthly)):
            if val is not None:
                if not isinstance(val, (int, float)) or val < 0:
                    return {"success": False, "error": f"{key} 必须是非负数"}
                pol[key] = float(val)
        pol["updated_at"] = _now_iso()
        if note:
            pol["note"] = note
        _save(data)
        return {"success": True, "user_id": user_id, "currency": currency,
                "limits": _limits_for(data, user_id, currency)}


def get_budget_policy(user_id, currency="CNY"):
    user_id = _norm_user(user_id)
    currency = _norm_currency(currency)
    with _lock:
        data = _load()
        entry = _load_budget_entry(data, user_id, currency)
    pol = entry.get("policy", {}) or {}
    custom = any(v not in PERSONAL_DEFAULT_LIMITS.get(currency, {})
                 for k, v in pol.items() if isinstance(v, (int, float)))
    return {"user_id": user_id, "currency": currency,
            "limits": _limits_for(data, user_id, currency),
            "custom": custom,
            "note": pol.get("note", ""),
            "updated_at": pol.get("updated_at")}


# 预算存储结构（每个 user × currency 一个 dict）：
# {
#   "policy":      {"per_tx": 200.0, "daily": 800.0, "weekly": 3000.0,
#                   "monthly": 8000.0, "note": "", "updated_at": ""},
#   "spent_daily":  {"YYYY-MM-DD": 12.5, ...},
#   "spent_weekly": {"YYYY-WNN": 34.0, ...},
#   "spent_monthly":{"YYYY-MM": 123.0, ...},
#   "reservations": {"rsv_xxx": {...}}
# }

def _default_budget_entry(currency):
    return {
        "policy": dict(PERSONAL_DEFAULT_LIMITS.get(currency, {})),
        "spent_daily": {}, "spent_weekly": {}, "spent_monthly": {},
        "reservations": {},
    }


def _load_budget_entry(data, user_id, currency):
    """拿 (user, currency) 的预算账本；不存在则初始化。"""
    return data["budget_ledger"].setdefault(user_id, {}).setdefault(
        currency, _default_budget_entry(currency))


def _limits_for(data, user_id, currency):
    entry = _load_budget_entry(data, user_id, currency)
    pol = entry.get("policy", {}) or {}
    merged = dict(PERSONAL_DEFAULT_LIMITS.get(currency, {}))
    merged.update({k: float(v) for k, v in pol.items()
                   if isinstance(v, (int, float))})
    return merged


def _spent_and_held(data, user_id, currency):
    entry = _load_budget_entry(data, user_id, currency)
    dk, wk, mk = (_now().strftime("%Y-%m-%d"), _week_key(), _now().strftime("%Y-%m"))
    daily = float(entry.get("spent_daily", {}).get(dk, 0.0))
    weekly = float(entry.get("spent_weekly", {}).get(wk, 0.0))
    monthly = float(entry.get("spent_monthly", {}).get(mk, 0.0))
    held = sum(float(r.get("amount", 0)) for r in
               entry.get("reservations", {}).values())
    return daily, weekly, monthly, held, dk, wk, mk


def _risk_score_payload(action, payload, history):
    """对一个待执行 action 做轻量风险打分（0-100，越低越安全）。

    评分因素：
      - 金额超过个人历史 P90 → +30
      - 目标域名命中高风险线索 → +20
      - 深夜时段（00-06）→ +10
      - 币种异常（用户平时 CNY，突然 USD）→ +15
      - 目标域名首次出现 → +10
      - action 类型高危（purchase/refund/wire_transfer）→ +10
    """
    score = 0
    reasons = []
    hist = history or {"amounts": [], "currencies": set(), "targets": set(),
                       "actions": set()}
    amounts = [float(x) for x in hist.get("amounts", []) if x is not None]
    p90 = 0
    if amounts:
        s = sorted(amounts)
        idx = max(0, min(len(s) - 1, int(len(s) * 0.9)))
        p90 = s[idx]
    amount = float(payload.get("amount") or 0)
    if amount > 0 and p90 > 0 and amount > p90:
        score += 30
        reasons.append(f"amount_{amount:.2f}_over_p90_{p90:.2f}")
    target = payload.get("target_url") or payload.get("target_domain") or ""
    if target and any(h in target.lower() for h in HIGH_RISK_DOMAIN_HINTS):
        score += 20
        reasons.append("target_high_risk_hint")
    hour = _now().hour
    if hour < 6:
        score += 10
        reasons.append("off_hours_00_06")
    primary = sorted(hist.get("currencies") or {"CNY"})[0] if hist.get("currencies") else "CNY"
    cur = _norm_currency(payload.get("currency") or "CNY")
    if cur != primary:
        score += 15
        reasons.append(f"currency_shift_{primary}_to_{cur}")
    if target and hist.get("targets") and target not in hist["targets"]:
        score += 10
        reasons.append("new_target")
    if action in ("purchase", "refund", "wire_transfer", "crypto_transfer"):
        score += 10
        reasons.append(f"high_risk_action_{action}")
    return min(score, 100), reasons


def check_budget_and_risk(user_id, action, amount, currency="CNY",
                          target_url=None, category=None, payload=None):
    """pre-flight：检查预算 + 计算风险 + 返回建议（allow / confirm / block）。

    verdict 语义：
      - allow    : 预算内 & 风险 < 40 → 直接放行
      - confirm  : 预算内 & 风险 40-70 → 用户二次确认（quote-first）
      - block    : 预算内 & 风险 >= 70 → 建议阻止（可覆盖）
      - denied   : 预算超限（不可覆盖）
    """
    user_id = _norm_user(user_id)
    currency = _norm_currency(currency)
    payload = dict(payload or {})
    if target_url:
        payload.setdefault("target_url", target_url)
    if category:
        payload.setdefault("category", category)
    if amount is not None:
        payload.setdefault("amount", amount)

    with _lock:
        data = _load()
        limits = _limits_for(data, user_id, currency)
        entry = _load_budget_entry(data, user_id, currency)
        day_spent, week_spent, month_spent, held, day_k, week_k, month_k = (
            _spent_and_held(data, user_id, currency))
        # 历史（从 action_ledger 汇总）
        action_ledger = data["action_ledger"].get(user_id, {}).get("records", [])
        history = {
            "amounts": [r.get("payload", {}).get("amount")
                        for r in action_ledger
                        if isinstance(r.get("payload", {}).get("amount"),
                                     (int, float))],
            "currencies": {r.get("payload", {}).get("currency")
                           for r in action_ledger
                           if r.get("payload", {}).get("currency")},
            "targets": {r.get("payload", {}).get("target_url")
                        for r in action_ledger
                        if r.get("payload", {}).get("target_url")},
            "actions": {r.get("action") for r in action_ledger if r.get("action")},
        }
    amount_f = float(amount or 0)

    # 预算检查（fail-closed）
    if not limits:
        return {"verdict": "denied", "reason": "no_limits_configured",
                "currency": currency, "limits": limits}
    if amount_f <= 0:
        return {"verdict": "denied", "reason": "invalid_amount",
                "amount": amount}
    if amount_f > limits.get("per_tx", 0):
        return {"verdict": "denied", "reason": "per_tx_exceeded",
                "amount": amount_f, "limit": limits["per_tx"]}
    if day_spent + held + amount_f > limits.get("daily", 0):
        return {"verdict": "denied", "reason": "daily_exceeded",
                "spent": day_spent, "reserved": held,
                "limit": limits["daily"]}
    if week_spent + held + amount_f > limits.get("weekly", 0):
        return {"verdict": "denied", "reason": "weekly_exceeded",
                "spent": week_spent, "reserved": held,
                "limit": limits["weekly"]}
    if month_spent + held + amount_f > limits.get("monthly", 0):
        return {"verdict": "denied", "reason": "monthly_exceeded",
                "spent": month_spent, "reserved": held,
                "limit": limits["monthly"]}

    # 风险评分
    risk, reasons = _risk_score_payload(action, payload, history)

    if risk >= 70:
        verdict, verdict_reason = "block", "high_risk_needs_override"
    elif risk >= 40:
        verdict, verdict_reason = "confirm", "medium_risk_quote_first"
    else:
        verdict, verdict_reason = "allow", "low_risk"

    return {
        "verdict": verdict, "verdict_reason": verdict_reason,
        "action": action, "amount": amount_f, "currency": currency,
        "risk_score": risk, "risk_reasons": reasons,
        "limits": limits,
        "day_spent": day_spent, "week_spent": week_spent,
        "month_spent": month_spent, "reserved": held,
        "day_remaining": round(limits.get("daily", 0) - day_spent - held, 6),
        "week_remaining": round(limits.get("weekly", 0) - week_spent - held, 6),
        "month_remaining": round(limits.get("monthly", 0) - month_spent - held, 6),
    }


def reserve_budget(user_id, order_id, amount, currency="CNY",
                   target=None, note=""):
    """预留一笔个人预算（下单前先冻结）。幂等：同 order_id 复用。"""
    user_id = _norm_user(user_id)
    currency = _norm_currency(currency)
    amount_f = float(amount)
    rid = _short_id("rsv")
    with _lock:
        data = _load()
        entry = _load_budget_entry(data, user_id, currency)
        # 幂等
        for r in entry.get("reservations", {}).values():
            if r.get("order_id") == order_id:
                return {"success": True, "reservation_id": r["reservation_id"],
                        "idempotent": True, "amount": r["amount"],
                        "currency": r["currency"]}
        res = {
            "reservation_id": rid, "order_id": order_id,
            "user_id": user_id, "amount": amount_f, "currency": currency,
            "target": target, "note": note,
            "created_at": _now_iso(),
            "expires_at": (_now() + timedelta(minutes=15)).isoformat(),
        }
        entry.setdefault("reservations", {})[rid] = res
        _save(data)
    return {"success": True, "reservation_id": rid, "amount": amount_f,
            "currency": currency, "expires_in": 900}


def _find_reservation(data, reservation_id, order_id):
    """跨 user/currency 查找预留，返回 (uid, currency, rid, reservation_dict)。"""
    for uid, cur_map in data.get("budget_ledger", {}).items():
        for cur, entry in cur_map.items():
            rsvs = entry.get("reservations", {}) or {}
            if reservation_id and reservation_id in rsvs:
                return uid, cur, reservation_id, rsvs[reservation_id]
            for rid, r in rsvs.items():
                if order_id and r.get("order_id") == order_id:
                    return uid, cur, rid, r
    return None, None, None, None


def commit_budget(reservation_id=None, order_id=None, user_id=None,
                  amount=None, currency=None):
    """把预留落到账本（下单成功）。预留过期时可用显式参数补记（fail-late）。"""
    if not reservation_id and not order_id:
        return {"success": False, "error": "需 reservation_id 或 order_id"}
    with _lock:
        data = _load()
        uid, cur, rid, res_hit = _find_reservation(data, reservation_id, order_id)
        if not res_hit:
            if user_id and amount is not None and currency:
                user_id = _norm_user(user_id)
                currency = _norm_currency(currency)
                uid, cur = user_id, currency
                res_hit = {
                    "user_id": user_id, "amount": float(amount),
                    "currency": currency,
                    "order_id": order_id or f"late_{uuid.uuid4().hex[:8]}",
                }
            else:
                return {"success": False, "error": "预留不存在或已过期"}
        entry = _load_budget_entry(data, uid, cur)
        amount_f = float(res_hit["amount"])
        dk, wk, mk = (_now().strftime("%Y-%m-%d"), _week_key(), _now().strftime("%Y-%m"))
        entry.setdefault("spent_daily", {})[dk] = round(
            float(entry.get("spent_daily", {}).get(dk, 0.0)) + amount_f, 6)
        entry.setdefault("spent_weekly", {})[wk] = round(
            float(entry.get("spent_weekly", {}).get(wk, 0.0)) + amount_f, 6)
        entry.setdefault("spent_monthly", {})[mk] = round(
            float(entry.get("spent_monthly", {}).get(mk, 0.0)) + amount_f, 6)
        # 清理预留
        if rid and rid in entry.get("reservations", {}):
            entry["reservations"].pop(rid, None)
        _save(data)
    return {"success": True, "order_id": res_hit["order_id"],
            "user_id": uid, "amount": amount_f, "currency": cur,
            "daily_total": entry["spent_daily"][dk],
            "monthly_total": entry["spent_monthly"][mk]}


def release_budget(reservation_id=None, order_id=None):
    """下单失败释放预留。"""
    with _lock:
        data = _load()
        uid, cur, rid, res_hit = _find_reservation(data, reservation_id, order_id)
        if not res_hit:
            return {"success": False, "error": "预留不存在"}
        entry = _load_budget_entry(data, uid, cur)
        popped = entry["reservations"].pop(rid, None)
        _save(data)
        return {"success": True, "released": True, "reservation_id": rid,
                "amount": popped.get("amount") if popped else res_hit.get("amount"),
                "currency": popped.get("currency") if popped else res_hit.get("currency")}


def budget_usage(user_id, currency="CNY"):
    user_id = _norm_user(user_id)
    currency = _norm_currency(currency)
    with _lock:
        data = _load()
        limits = _limits_for(data, user_id, currency)
        daily_spent, week_spent, month_spent, reserved, dk, wk, mk = (
            _spent_and_held(data, user_id, currency))
    return {
        "user_id": user_id, "currency": currency,
        "limits": limits,
        "daily_spent": daily_spent, "weekly_spent": week_spent,
        "monthly_spent": month_spent, "reserved": reserved,
        "daily_remaining": round(limits.get("daily", 0) - daily_spent - reserved, 6),
        "weekly_remaining": round(limits.get("weekly", 0) - week_spent - reserved, 6),
        "monthly_remaining": round(limits.get("monthly", 0) - month_spent - reserved, 6),
        "day": dk, "week": wk, "month": mk,
    }


# ══════════════════════════════════════════════════════════════
# 3) Action Provenance Ledger —— 行动溯源（HMAC 链）
# ══════════════════════════════════════════════════════════════
#
# 每个 user 有一条独立 HMAC 链；每条 record 由 (user_id, action, payload,
# agent_instance, ticket) 构成，链头 prev_hash 串起。可离线验证"这条记录
# 是服务端签的、没被改过、顺序连续"。
# ══════════════════════════════════════════════════════════════

def record_action(user_id, action, payload=None, instance_id=None,
                  ticket_id=None, verdict="allow", actor_did=None,
                  note=""):
    """向用户 HMAC 链追加一条 action record。

    参数：
      user_id     : 自然人（必须已建 DID）
      action      : 动作类型，如 "purchase", "send_email", "connect_connector"
      payload     : 动作负载（金额/目标 URL/内容 hash 等）
      instance_id : 是哪个 agent 实例（可选，用于跨 agent 追溯）
      ticket_id   : 使用的授权票据（可选）
      verdict     : 该动作当时的 check_budget_and_risk 结果
      actor_did   : agent 实例自签名 DID（可选，未提供则用 parent_did）
      note        : 用户/agent 附加备注
    """
    user_id = _norm_user(user_id)
    if not action:
        raise ValueError("action 必填")
    with _lock:
        data = _load()
        if user_id not in data["users"]:
            create_personal_did(user_id)
            data = _load()
        ledger = data["action_ledger"].setdefault(user_id, {
            "records": [], "head_hash": "", "seq": 0,
        })
        prev_hash = ledger.get("head_hash", "")
        seq = int(ledger.get("seq", 0)) + 1
        rec_body = {
            "seq": seq,
            "user_id": user_id,
            "action": action,
            "payload": payload or {},
            "instance_id": instance_id,
            "ticket_id": ticket_id,
            "verdict": verdict,
            "actor_did": actor_did or data["users"][user_id]["did"],
            "parent_did": data["users"][user_id]["did"],
            "note": note,
            "prev_hash": prev_hash,
            "at": _now_iso(),
        }
        rec_hash = _hash_hex(rec_body, _load_hmac_secret())
        rec = dict(rec_body)
        rec["hash"] = rec_hash
        ledger["records"].append(rec)
        ledger["head_hash"] = rec_hash
        ledger["seq"] = seq
        # 清理老数据（超过 90 天）
        cutoff = (_now() - timedelta(days=CHUNK_TTL_DAYS)).isoformat()
        ledger["records"] = [r for r in ledger["records"]
                             if r.get("at", "0") >= cutoff][:2000]
        _save(data)
    return {"success": True, "seq": seq, "hash": rec_hash,
            "prev_hash": prev_hash, "at": rec["at"]}


def get_action_receipt(user_id, seq):
    """生成一条 action 的可验证回执（消费级 dispute 用）。"""
    user_id = _norm_user(user_id)
    with _lock:
        data = _load()
        ledger = data["action_ledger"].get(user_id, {})
        for r in ledger.get("records", []):
            if r.get("seq") == int(seq):
                return dict(r)
    return {"found": False, "seq": seq}


def verify_action_chain(user_id, verify_from_seq=1):
    """从头验证用户 HMAC 链：连续性 + 签名。"""
    user_id = _norm_user(user_id)
    with _lock:
        data = _load()
        ledger = data["action_ledger"].get(user_id, {})
    secret = _load_hmac_secret()
    prev = ""
    for r in ledger.get("records", []):
        if r.get("seq", 0) < verify_from_seq:
            continue
        if r.get("prev_hash") != prev:
            return {"valid": False, "reason": "prev_hash_mismatch",
                    "at_seq": r.get("seq")}
        body = {k: v for k, v in r.items() if k != "hash"}
        if not hmac.compare_digest(_hash_hex(body, secret), r.get("hash", "")):
            return {"valid": False, "reason": "hash_mismatch",
                    "at_seq": r.get("seq")}
        prev = r["hash"]
    return {"valid": True, "records": len(ledger.get("records", [])),
            "head_hash": ledger.get("head_hash")}


def file_dispute(user_id, seq, reason, description=""):
    """用户对某条 action 提出 dispute（"这个操作我不知情"）。"""
    user_id = _norm_user(user_id)
    receipt = get_action_receipt(user_id, seq)
    if not receipt.get("found", True) and "seq" not in receipt:
        return {"success": False, "reason": "record_not_found"}
    dispute_id = _short_id("dis")
    with _lock:
        data = _load()
        rec = {
            "dispute_id": dispute_id,
            "user_id": user_id,
            "seq": int(seq),
            "action_hash": receipt.get("hash"),
            "reason": reason,
            "description": description,
            "created_at": _now_iso(),
            "status": "open",
        }
        data["disputes"].setdefault(user_id, []).append(rec)
        _save(data)
    return {"success": True, "dispute_id": dispute_id, "status": "open",
            "action_hash": receipt.get("hash")}


def get_disputes(user_id, status=None):
    user_id = _norm_user(user_id)
    with _lock:
        data = _load()
        items = data["disputes"].get(user_id, [])
    if status:
        items = [d for d in items if d.get("status") == status]
    return items


# ══════════════════════════════════════════════════════════════
# 4) Connector Vetting —— 独立第二意见审核
# ══════════════════════════════════════════════════════════════
#
# Meta 官方 connector 有审；但用户还需要中立评估（不是 Meta 的视角）。
# 本模块吃一个"connector 描述"字典（未来 muse.ai/platform 提交材料
# 就是这种结构），返回 findings + 建议。
# ══════════════════════════════════════════════════════════════

def vet_connector(user_id, connector):
    """对一个 connector 做独立安全评估。

    connector 结构（示例）：
      {
        "name": "Notion",
        "publisher": "Notion Labs",
        "url": "https://notion.so",
        "capabilities": ["read_docs", "write_docs", "search"],
        "scopes": ["docs.read", "docs.write"],
        "install_commands": ["curl -sL https://notion.so/mcp | sh"],
        "signature": "ed25519-signature-base64",   // 可选
        "expires_at": "2027-01-01",                 // 可选
        "requires_payments": false
      }
    返回：{verdict, score, findings[], recommended_actions[]}
    """
    user_id = _norm_user(user_id)
    findings = []
    score = 100

    name = connector.get("name", "<unknown>")
    caps = connector.get("capabilities", []) or []
    scopes = connector.get("scopes", []) or []
    scopes_blob = " ".join(str(s).lower() for s in scopes)
    caps_blob = " ".join(str(c).lower() for c in caps)
    combined = scopes_blob + " " + caps_blob
    desc = json.dumps(connector, ensure_ascii=False).lower()

    # ── 危险 scope 关键词 ──
    hit_danger = []
    for kw in DANGEROUS_SCOPE_KEYWORDS:
        if kw in scopes_blob or kw in caps_blob:
            hit_danger.append(kw)
    if hit_danger:
        score -= 25
        findings.append({
            "id": "C1", "severity": "high",
            "title": "Dangerous scope/capability keywords",
            "detail": f"命中关键词: {hit_danger}",
            "remediation": "要求 publisher 明确列出每个 scope 的实际用途，"
                           "或降级为最小权限版本",
        })

    # ── install_commands 供应链 ──
    install_cmds = connector.get("install_commands", []) or []
    for cmd in install_cmds:
        if "curl" in cmd and "sh" in cmd:
            score -= 20
            findings.append({
                "id": "C2", "severity": "high",
                "title": "Piped shell install command",
                "detail": f"`curl ... | sh` 类安装命令: {cmd!r}",
                "remediation": "改为发布可校验的 binary + 校验和",
            })
            break

    # ── 明文 token/secret 扫描 ──
    _token_re = re.compile(
        r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{12,}"
        r"|xox[baprs]-[A-Za-z0-9-]{20,}|Bearer\s+[A-Za-z0-9._\-]{20,})",
        re.IGNORECASE,
    )
    for m in _token_re.finditer(desc):
        score -= 30
        findings.append({
            "id": "C3", "severity": "critical",
            "title": "Credential-like string in connector manifest",
            "detail": f"命中凭据模式: {m.group(0)[:20]}...",
            "remediation": "移除 manifest 里的明文凭据，改用 OAuth flow 或用户自填",
        })
        break

    # ── 签名/过期声明 ──
    if not connector.get("signature"):
        score -= 15
        findings.append({
            "id": "C4", "severity": "medium",
            "title": "Connector manifest not signed",
            "detail": "缺 signature 字段；无法离线验证 manifest 未被篡改",
            "remediation": "用 publisher 私钥签名 manifest（推荐 ed25519）",
        })
    if not connector.get("expires_at") and not connector.get("version"):
        score -= 5
        findings.append({
            "id": "C5", "severity": "low",
            "title": "No version or expiry declared",
            "detail": "manifest 无 version 或 expires_at，无法管理更新节奏",
            "remediation": "补充 SemVer + expires_at",
        })

    # ── 过度代理判定（scope 数量） ──
    if len(scopes) > 15 or len(caps) > 20:
        score -= 10
        findings.append({
            "id": "C6", "severity": "medium",
            "title": "Excessive scope count",
            "detail": f"scopes={len(scopes)} caps={len(caps)}，超出最小权限实践",
            "remediation": "拆分为按场景的最小权限版本",
        })

    # ── 支付相关 ──
    if connector.get("requires_payments") and not connector.get("quote_first_supported"):
        score -= 15
        findings.append({
            "id": "C7", "severity": "high",
            "title": "Payment-capable connector without quote-first support",
            "detail": "connector 支持支付但未声明 quote-first（用户看不到最终价就直接下单）",
            "remediation": "实现 quote-first：向用户展示 final price + destination 后再执行",
        })

    # ── 描述 vs 权限一致性 ──
    # 简易启发：description 里没提的关键词不能出现在 scopes 里（反之亦然）
    desc_body = (connector.get("description") or "").lower()
    unmentioned = [kw for kw in DANGEROUS_SCOPE_KEYWORDS
                   if kw in scopes_blob and kw not in desc_body]
    if unmentioned:
        score -= 10
        findings.append({
            "id": "C8", "severity": "medium",
            "title": "Scope not disclosed in description",
            "detail": f"权限里出现但描述未提及的关键词: {unmentioned}",
            "remediation": "在 description 里明确列出这些用途",
        })

    score = max(0, score)
    if score >= 80:
        verdict = "pass"
    elif score >= 55:
        verdict = "pass_with_warnings"
    elif score >= 30:
        verdict = "needs_review"
    else:
        verdict = "reject"

    rec = {
        "verdict": verdict, "score": score, "findings": findings,
        "connector": {"name": name, "publisher": connector.get("publisher"),
                      "url": connector.get("url")},
        "recommended_actions": [
            "让用户看到所有 scope 后再决定是否授权" if verdict == "pass" else
            "要求 publisher 修订 manifest 后重审" if verdict == "needs_review" else
            "阻断安装，等待 publisher 修复 critical/high findings",
        ],
    }
    with _lock:
        data = _load()
        data["connector_reviews"].setdefault(user_id, []).append({
            "reviewed_at": _now_iso(),
            "connector_name": name,
            "verdict": verdict,
            "score": score,
            "findings_count": len(findings),
        })
        _save(data)
    return rec


# ══════════════════════════════════════════════════════════════
# 5) 聚合视图
# ══════════════════════════════════════════════════════════════

def get_user_state(user_id):
    user_id = _norm_user(user_id)
    with _lock:
        data = _load()
    user = data["users"].get(user_id)
    if not user:
        return {"found": False, "user_id": user_id}
    insts = list(data["agent_instances"].get(user_id, {}).values())
    tix = list(data["tickets"].get(user_id, {}).values())
    active_tickets = [t for t in tix if t.get("status") == "active"]
    actions = data["action_ledger"].get(user_id, {}).get("records", [])
    disputes = data["disputes"].get(user_id, [])
    budgets = data["budget_ledger"].get(user_id, {})
    budget_summary = {}
    for cur, entry in budgets.items():
        pol = entry.get("policy", {}) or {}
        merged = dict(PERSONAL_DEFAULT_LIMITS.get(cur, {}))
        merged.update({k: float(v) for k, v in pol.items()
                       if isinstance(v, (int, float))})
        limits = {k: v for k, v in merged.items() if isinstance(v, (int, float))}
        day_k = _now().strftime("%Y-%m-%d")
        week_k = _week_key()
        month_k = _now().strftime("%Y-%m")
        budget_summary[cur] = {
            "limits": limits,
            "daily_spent": float((entry.get("spent_daily", {}) or {}).get(day_k, 0.0)),
            "weekly_spent": float((entry.get("spent_weekly", {}) or {}).get(week_k, 0.0)),
            "monthly_spent": float((entry.get("spent_monthly", {}) or {}).get(month_k, 0.0)),
        }
    return {
        "user_id": user_id,
        "did": user["did"],
        "display_name": user.get("display_name"),
        "created_at": user["created_at"],
        "agent_instances": [
            {"instance_id": i["instance_id"], "agent_name": i["agent_name"],
             "provider": i["provider"], "status": i.get("status"),
             "platform_hint": i.get("platform_hint")}
            for i in insts
        ],
        "active_tickets": len(active_tickets),
        "tickets_total": len(tix),
        "actions_recorded": len(actions),
        "chain_valid": verify_action_chain(user_id)["valid"],
        "open_disputes": len([d for d in disputes if d.get("status") == "open"]),
        "budget_summary": budget_summary,
        "connector_reviews": data["connector_reviews"].get(user_id, [])[-5:],
    }


def list_users():
    with _lock:
        data = _load()
    return list(data["users"].keys())


def _export_public_state():
    """给 /api/v1/personal-agents/stats 用。"""
    with _lock:
        data = _load()
    return {
        "users_total": len(data["users"]),
        "agent_instances_total": sum(
            len(v) for v in data["agent_instances"].values()),
        "active_tickets_total": sum(
            1 for u in data["tickets"].values()
            for t in u.values() if t.get("status") == "active"),
        "actions_total": sum(
            len(v.get("records", [])) for v in data["action_ledger"].values()),
        "open_disputes_total": sum(
            len([d for d in v if d.get("status") == "open"])
            for v in data["disputes"].values()),
    }


if __name__ == "__main__":
    print("=== Personal Agent Governance Kernel ===")
    print("PAI DID:", create_personal_did("alice@example.com", "Alice", "alice@example.com"))
    inst = register_agent_instance("alice@example.com", "Muse", "Meta",
                                   platform_hint="muse-ios")
    print("Instance:", inst["instance_id"], inst["agent_name"], inst["provider"])
    tk = create_capability_ticket("alice@example.com", inst["instance_id"],
                                  ["purchase"], scope={"max_amount": 200},
                                  expires_in=600, reason="buy groceries")
    print("Ticket:", tk["ticket_id"])
    v = verify_capability_ticket(tk)
    print("Verify ticket:", v)
    chk = check_budget_and_risk("alice@example.com", "purchase", 180, "CNY",
                                target_url="https://checkout.example.com",
                                category="groceries")
    print("Budget+risk check:", {k: v for k, v in chk.items() if k != "limits"})
    rec = record_action("alice@example.com", "purchase",
                        payload={"amount": 180, "currency": "CNY",
                                 "target_url": "https://checkout.example.com"},
                        instance_id=inst["instance_id"], ticket_id=tk["ticket_id"],
                        verdict=chk["verdict"])
    print("Recorded:", rec["seq"], rec["hash"][:12])
    chain = verify_action_chain("alice@example.com")
    print("Chain valid:", chain)
    vet = vet_connector("alice@example.com", {
        "name": "ExampleShop", "publisher": "Example Inc",
        "url": "https://example.com",
        "capabilities": ["search_products", "checkout"],
        "scopes": ["products.read", "payment.spend"],
        "install_commands": ["curl -sL https://example.com/install.sh | sh"],
        "requires_payments": True,
    })
    print("Vet:", vet["verdict"], "score=", vet["score"],
          "findings=", len(vet["findings"]))
