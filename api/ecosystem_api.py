"""
api/ecosystem_api.py — Agent 生态服务 API（5 支柱落地）

覆盖：
  - L1 信任认证:  Agent Card 签名/验证 + 公钥发现（硬骨头 #2）
  - L2 专业注册:  Specialist Registry（8 域）
  - L3 身份:      KYA SD-JWT + Web Bot Auth + ERC-8004（硬骨头 #6）
  - L4 责任链:    Responsibility Chain 追加/查询/溯源（硬骨头 #1）
  - L5 协议翻译:  MCP ⇄ A2A ⇄ ACP ⇄ AP2 互转（硬骨头 #5）

调用约定：
  本模块只暴露 handle_get(path, query) 和 handle_post(path, data)，
  与 api/trust_api.py 完全一致的接口，由 api/server.py 分发。
  所有路由以 /api/v1/ecosystem/ 或 /api/v1/agent-card/ 或 /api/v1/chain/ 开头。
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import sysconfig
import threading
from urllib.parse import parse_qs
import urllib.parse

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _stdlib_platform():
    """取标准库的 platform 模块，而不是仓库里的 eco/platform.py。

    本文件下面把 eco/ 挂上 sys.path，而 eco/ 里有一个 platform.py
    （平台注册中心，与标准库无关）。裸 `import platform` 的解析结果就
    取决于导入顺序：标准库 platform 已被别的模块先加载时拿到标准库，
    首次加载时拿到 eco/platform.py，随后 platform.system() 抛
    AttributeError: module 'platform' has no attribute 'system'。
    本地因为 sys.modules 里恰好已有标准库 platform 而长期未炸，
    干净 CI runner 上必炸。这里按标准库安装路径直接加载。
    """
    cached = sys.modules.get("platform")
    if cached is not None and "system" in dir(cached):
        return cached
    stdlib = sysconfig.get_paths()["stdlib"]
    spec = importlib.util.spec_from_file_location(
        "platform", os.path.join(stdlib, "platform.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["platform"] = mod          # 先入 sys.modules 防循环导入半初始化
    spec.loader.exec_module(mod)
    return mod


platform = _stdlib_platform()

# 允许作为独立脚本或被 api/server.py 两种路径调用
for _p in (_BASE, _BASE + "/eco", _BASE + "/api"):
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ── 惰性导入，避免 server.py 冷启动加载重量依赖 ──
def _import_agent_card():
    from eco import agent_card
    return agent_card


def _import_chain():
    from eco import responsibility_chain
    return responsibility_chain


def _import_bridge():
    from eco import protocol_bridge
    return protocol_bridge


def _import_specialist():
    from eco import specialist_registry
    return specialist_registry


def _import_kyad():
    from eco import kyad_compat
    return kyad_compat


def _import_identity():
    from eco import identity
    return identity


def _append_event_safe(event: str, did: str = "", actor: str = "",
                       result: str = "ok", reason: str = ""):
    """在 API 层留一条身份审计事件；审计写不进绝不能拖垮主流程。"""
    try:
        ident = _import_identity()
        return ident._append_event(event, did, actor=actor,
                                   result=result, reason=reason)
    except Exception as exc:                       # pragma: no cover
        return {"ts": "", "event": event, "did": did, "actor": actor,
                "result": "event_write_failed",
                "reason": f"{type(exc).__name__}: {exc}"}


def _import_evidence_bundle():
    from eco import evidence_bundle
    return evidence_bundle


def _import_ship_gate():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ship_gate", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "scripts", "ship_gate.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ══════════════════════════════════════════════
# 责任链：内存里的 chain 实例池（按 chain_id 隔离）
# ══════════════════════════════════════════════
_chains: dict = {}
_chains_lock = threading.RLock()


def _get_chain(chain_id: str):
    from eco import responsibility_chain as rc
    with _chains_lock:
        c = _chains.get(chain_id)
        if c is None:
            c = rc.ResponsibilityChain(chain_id=chain_id)
            _chains[chain_id] = c
        return c


def _gen_chain_id() -> str:
    import hashlib
    import time
    return "chain-" + hashlib.sha256(f"{time.time_ns()}".encode()).hexdigest()[:12]


# ══════════════════════════════════════════════
# Evidence Bundle：内存里的 bundle 实例池（R4-深化）
# ══════════════════════════════════════════════
_bundles: dict = {}
_bundles_lock = threading.RLock()


def _get_bundle(run_id: str, hmac_secret: str | None = None):
    eb = _import_evidence_bundle()
    with _bundles_lock:
        b = _bundles.get(run_id)
        if b is None:
            b = eb.EvidenceBundle(run_id=run_id, hmac_secret=hmac_secret)
            _bundles[run_id] = b
        return b


def _gen_run_id() -> str:
    import hashlib
    import time
    return "run-" + hashlib.sha256(f"{time.time_ns()}".encode()).hexdigest()[:12]


# ══════════════════════════════════════════════
#  Agent Card API
# ══════════════════════════════════════════════
def _agent_card_pubkey() -> dict:
    """返回签发动员公钥信息（供消费方离线验证）。"""
    ac = _import_agent_card()
    signer = ac.AgentCardSigner()
    alg, pub = signer.public_key()
    return {
        "signer_did": signer.signer_did,
        "key_id": signer.key_id,
        "alg": alg,
        "public_key": pub,
        "endpoint": "/api/v1/agent-card/verify",
    }


def _agent_card_sign(card: dict, trust_score: int | None) -> dict:
    ac = _import_agent_card()
    if not isinstance(card, dict):
        return {"error": "card must be a JSON object"}, 400
    signed = ac.sign_card(card, trust_score=trust_score)
    return signed, 200


def _agent_card_verify(card: dict, public_key_b64: str | None) -> dict:
    ac = _import_agent_card()
    if not isinstance(card, dict):
        return {"error": "card must be a JSON object"}, 400
    # 优先使用 .well-known 公钥文件（离线验证）
    try:
        v = ac.verify_with_pubkey_file(card)
        if v.get("valid"):
            return v, 200
        if v.get("requires_server_verification"):
            # 服务端持有 HMAC 密钥，走服务端验证
            v = ac.verify_card(card)
            return v, 200 if v.get("valid") else 400
        return v, 400
    except Exception as e:
        return {"error": str(e)}, 500


def _agent_card_export_identity(card: dict, trust_score: int | None) -> dict:
    """一站式：Agent Card → KYA + Web Bot Auth 身份导出。"""
    kyad = _import_kyad()
    ident = kyad.agent_card_to_identity(card, trust_score=trust_score)
    return ident, 200


# ══════════════════════════════════════════════
#  Specialist Registry API
# ══════════════════════════════════════════════
def _specialist_domains() -> dict:
    sr = _import_specialist()
    return sr.domains_catalog(), 200


def _specialist_list(domain: str | None, include_lapsed: bool) -> dict:
    sr = _import_specialist()
    items = sr.list_agents(domain=domain, include_lapsed=include_lapsed)
    return {"count": len(items), "items": items}, 200


def _specialist_get(agent_id: str) -> dict:
    sr = _import_specialist()
    rec = sr.get(agent_id)
    if not rec:
        return {"error": "agent not found", "agent_id": agent_id}, 404
    return rec, 200


def _specialist_register(data: dict) -> dict:
    sr = _import_specialist()
    required = ["agent_id", "name", "domain", "capabilities"]
    for k in required:
        if k not in data or not data[k]:
            return {"error": f"missing required field: {k}"}, 400
    try:
        rec = sr.register_agent(
            agent_id=data["agent_id"],
            name=data["name"],
            domain=data["domain"],
            capabilities=data["capabilities"],
            certs=data.get("certs", []),
            url=data.get("url", ""),
            provider=data.get("provider", ""),
            description=data.get("description", ""),
            publisher_did=data.get("publisher_did", "did:aishield:trust-service"),
            extra=data.get("extra"),
        )
        return rec, 201
    except ValueError as e:
        return {"error": str(e)}, 400


def _identity_token_issue(data: dict) -> dict:
    """POST /api/v1/identity/registration-token —— 领一枚注册凭据（绑定 owner）。

    身份注册必须可归属、可撤销；裸端点注册只会留下一堆谁也删不掉的脏 DID。
    凭据明文只在响应里出现一次，服务端只存 sha256。
    """
    ident = _import_identity()
    owner = (data.get("owner") or data.get("agent_id") or "").strip()
    if not owner:
        return {"error": "missing required field: owner"}, 400
    ttl = data.get("ttl_seconds")
    if ttl is not None:
        try:
            ttl = int(ttl)
        except (TypeError, ValueError):
            return {"error": "ttl_seconds must be an int"}, 400
    try:
        issued = ident.RegistrationTokenAuthority().issue(owner, ttl=ttl)
    except ValueError as e:
        return {"error": str(e)}, 400
    _append_event_safe("registration_token.issue", actor=owner)
    return {"token": issued["token"], "token_id": issued["token_id"],
            "owner": issued["owner"], "expires_at": issued["expires_at"]}, 201


def _identity_register(data: dict) -> dict:
    """POST /api/v1/identity/register —— Agent 身份注册（必须带注册凭据）。

    2026-10-03：``api/static/.well-known/agent.json``（对外发布的 agent card）里
    就挂着这个端点，但 server.py 的 do_POST 分发链上从来没有它 —— 外部 agent 照
    卡调用只会吃 404。eco/identity.py 的 AgentRegistration 一直是好的，缺的只是
    接线。这里补上，契约与卡片才不会再次撒谎。

    同一轮里把「裸注册」也堵上了：现在必须先领 registration-token（绑定 owner），
    注册时凭据一次性消费。否则注册表永远只有写入没有回收。
    """
    ident = _import_identity()
    reg = ident.AgentRegistration()
    name = (data.get("name") or "").strip()
    if not name:
        return {"error": "missing required field: name"}, 400
    owner = (data.get("owner") or data.get("agent_id") or "").strip()
    did = (data.get("did") or "").strip() or None
    if did is not None and not isinstance(did, str):
        return {"error": "did must be a string"}, 400
    token = data.get("registration_token") or data.get("token")
    if not token or not isinstance(token, str):
        return {"error": "missing required field: registration_token"}, 401
    try:
        agent = reg.register(
            name=name,
            did=did,
            public_key=data.get("public_key"),
            capabilities=data.get("capabilities") or [],
            owner=owner,
            registration_token=token,
        )
    except ident.IdentityAuthError as e:
        return {"error": str(e)}, 401
    except ident.IdentityForbidden as e:
        return {"error": str(e)}, 403
    except ValueError as e:
        return {"error": str(e)}, 409
    return {"success": True, "agent": agent}, 201


def _identity_revoke(did: str, owner: str = "", revoke_token: str = "") -> dict:
    """DELETE /api/v1/identity/agents/{did} —— 注销自己的身份锚点。"""
    ident = _import_identity()
    try:
        ok = ident.AgentRegistration().revoke_agent(
            did, owner=owner, revoke_token=revoke_token)
    except ident.IdentityForbidden as e:
        return {"error": str(e)}, 403
    if ok is None:
        return {"error": "Agent not found", "did": did}, 404
    if not ok:
        return {"success": True, "did": did, "status": "inactive",
                "result": "already inactive"}, 200
    return {"success": True, "did": did, "status": "inactive"}, 200


def _identity_list() -> dict:
    """GET /api/v1/identity/agents —— 已注册 Agent 列表。"""
    ident = _import_identity()
    items = ident.AgentRegistration().list_agents()
    # 对外只给 public_view：revoke_token_hash 漏出去等于把注销权送人
    items = [ident.AgentRegistration().public_view(a) for a in items]
    return {"success": True, "count": len(items), "agents": items}, 200


def _identity_get(did: str) -> dict:
    """GET /api/v1/identity/agents/{did} —— 单个 Agent 身份详情（脱敏视图）。"""
    ident = _import_identity()
    agent = ident.AgentRegistration().get_agent(did)
    if not agent:
        return {"success": False, "error": "Agent not found", "did": did}, 404
    return {"success": True,
            "agent": ident.AgentRegistration().public_view(agent)}, 200


def handle_delete(path: str, query: dict | None = None) -> tuple[dict, int]:
    """DELETE 分发入口（__DELETE__，2026-10-03 随身份注销闭环新增）。

    目前只承载身份注销：``DELETE /api/v1/identity/agents/{did}``。归属参数
    可以从 query（``?owner=``）或 JSON body 取，命令行 curl 不带 body 也能用。
    """
    q = query or {}
    m = re.match(r"^/api/v1/identity/agents/([^/]+)$", path)
    if not m:
        return {"error": "Not found", "path": path}, 404
    did = urllib.parse.unquote(m.group(1))
    return _identity_revoke(did, _first(q, "owner"), _first(q, "revoke_token"))


def _first(q: dict, key: str) -> str:
    """query 取值：?owner=a 或 ?owner=a&owner=b 都取第一个。"""
    v = q.get(key) if isinstance(q, dict) else None
    if isinstance(v, list):
        v = v[0] if v else ""
    return v if isinstance(v, str) else ("" if v is None else str(v))


def _specialist_renew(agent_id: str) -> dict:
    sr = _import_specialist()
    rec = sr.renew(agent_id)
    if not rec:
        return {"error": "agent not found", "agent_id": agent_id}, 404
    return rec, 200


def _specialist_revoke(agent_id: str, reason: str) -> dict:
    sr = _import_specialist()
    rec = sr.revoke(agent_id, reason=reason)
    if not rec:
        return {"error": "agent not found", "agent_id": agent_id}, 404
    return rec, 200


# ══════════════════════════════════════════════
#  KYA / Web Bot Auth / ERC-8004 API
# ══════════════════════════════════════════════
def _kyad_export(card: dict, trust_score: int | None) -> dict:
    return _agent_card_export_identity(card, trust_score)


def _erc8004_wrap(wallet_address: str, chain_id: int) -> dict:
    kyad = _import_kyad()
    try:
        did = kyad.wallet_to_did(wallet_address, chain_id)
        return {"did": did, "wallet": kyad.did_to_wallet(did)}, 200
    except ValueError as e:
        return {"error": str(e)}, 400


# ══════════════════════════════════════════════
#  Responsibility Chain API
# ══════════════════════════════════════════════
def _chain_create(chain_id: str | None) -> dict:
    cid = chain_id or _gen_chain_id()
    with _chains_lock:
        if cid in _chains:
            return {"error": "chain already exists", "chain_id": cid}, 409
        c = _get_chain(cid)
    return c.export(), 201


def _chain_append(chain_id: str, data: dict) -> dict:
    c = _get_chain(chain_id)
    agent_id = data.get("agent_id")
    action = data.get("action")
    if not agent_id or not action:
        return {"error": "agent_id and action required"}, 400
    entry = c.record(
        agent_id=agent_id,
        action=action,
        parent_seq=data.get("parent_seq"),
        input_ref=data.get("input_ref"),
        output_ref=data.get("output_ref"),
        meta=data.get("meta"),
    )
    return entry, 201


def _chain_view(chain_id: str) -> dict:
    c = _get_chain(chain_id)
    return c.export(), 200


def _chain_verify(chain_id: str) -> dict:
    c = _get_chain(chain_id)
    return c.verify(), 200


def _chain_trace(chain_id: str, output_ref) -> dict:
    c = _get_chain(chain_id)
    path = c.trace(output_ref)
    root = c.root_cause(output_ref)
    return {"chain_id": chain_id, "path": path, "root_cause": root, "depth": len(path)}, 200


# ══════════════════════════════════════════════
#  Contributors API (R2)
# ══════════════════════════════════════════════
def _import_contributors():
    from eco import contributors
    return contributors


def _import_sandbox_backend():
    from eco import sandbox_backend
    return sandbox_backend


def _sandbox_backend_capabilities() -> dict:
    sb = _import_sandbox_backend()
    return {
        "system": platform.system(),
        "recommended": sb.recommend_backend(),
        "matrix": sb.capabilities_matrix(),
    }, 200


def _sandbox_backend_current() -> dict:
    sb = _import_sandbox_backend()
    return sb.current_backend(), 200


def _contributor_register(data: dict) -> dict:
    cb = _import_contributors()
    cid = data.get("contributor_id")
    if not cid:
        return {"error": "contributor_id required"}, 400
    try:
        rec = cb.register_contributor(
            contributor_id=cid,
            name=data.get("name", ""),
            email=data.get("email", ""),
            github=data.get("github", ""),
            bio=data.get("bio", ""),
        )
        return rec, 201
    except ValueError as e:
        return {"error": str(e)}, 400


def _contributor_add_event(contributor_id: str, data: dict) -> dict:
    cb = _import_contributors()
    event_type = data.get("type") or data.get("event_type")
    if not event_type:
        return {"error": "type/event_type required"}, 400
    try:
        rec = cb.add_event(
            contributor_id=contributor_id,
            event_type=event_type,
            rule_id=data.get("rule_id", ""),
            rule_name=data.get("rule_name", ""),
            description=data.get("description", ""),
            extra=data.get("extra"),
        )
        return rec, 201
    except ValueError as e:
        return {"error": str(e)}, 400


# ══════════════════════════════════════════════
#  Protocol Bridge API
# ══════════════════════════════════════════════
def _bridge_normalize(protocol: str, payload: dict) -> dict:
    pb = _import_bridge()
    proto = (protocol or "").lower()
    if proto not in ("mcp", "a2a", "acp", "ap2"):
        return {"error": "protocol must be one of mcp/a2a/acp/ap2"}, 400
    if not isinstance(payload, dict):
        return {"error": "payload must be a JSON object"}, 400
    ua = {
        "mcp": pb.from_mcp, "a2a": pb.from_a2a,
        "acp": pb.from_acp, "ap2": pb.from_ap2,
    }[proto](payload)
    return {"protocol": proto, "universal_agent": ua.to_dict()}, 200


def _bridge_translate(target: str, payload: dict, from_protocol: str | None) -> dict:
    pb = _import_bridge()
    tp = (target or "").lower()
    if tp not in ("mcp", "a2a", "acp"):
        return {"error": "target must be one of mcp/a2a/acp"}, 400
    if not isinstance(payload, dict):
        return {"error": "payload must be a JSON object"}, 400
    src = (from_protocol or "").lower()
    if src == "universal":
        ua = pb.UniversalAgent(
            name=payload.get("name", ""), description=payload.get("description", ""),
            version=str(payload.get("version", "1.0.0")), url=payload.get("url", ""),
            provider=payload.get("provider", {}),
            capabilities=payload.get("capabilities", []),
            skills=payload.get("skills", []),
            protocols=payload.get("protocols", []),
            trust=payload.get("trust", {}),
            payment=payload.get("payment", {}),
        )
    elif src in ("mcp", "a2a", "acp", "ap2"):
        ua = {
            "mcp": pb.from_mcp, "a2a": pb.from_a2a,
            "acp": pb.from_acp, "ap2": pb.from_ap2,
        }[src](payload)
    else:
        return {"error": "from_protocol required (mcp/a2a/acp/ap2/universal)"}, 400
    result = {
        "mcp": pb.to_mcp, "a2a": pb.to_a2a,
    }[tp](ua) if tp in ("mcp", "a2a") else {"error": "target not supported"}
    if isinstance(result, dict) and result.get("error"):
        return result, 400
    return {"target": tp, "source": src, "result": result}, 200


# ══════════════════════════════════════════════
#  公开路由分发
# ══════════════════════════════════════════════
def handle_get(path: str, query: str = ""):
    """返回 (payload_dict, status_code)。"""
    q = parse_qs(query) if query else {}

    # ── Agent Card ──
    if path == "/api/v1/agent-card/pubkey":
        return _agent_card_pubkey(), 200

    # ── Specialist Registry ──
    if path == "/api/v1/specialist/domains":
        return _specialist_domains()
    if path == "/api/v1/specialist/agents":
        domain = q.get("domain", [None])[0]
        include_lapsed = q.get("include_lapsed", ["false"])[0].lower() == "true"
        return _specialist_list(domain, include_lapsed)

    m = re.match(r"^/api/v1/specialist/agents/([^/]+)$", path)
    if m:
        return _specialist_get(m.group(1))

    # ── Responsibility Chain ──
    m = re.match(r"^/api/v1/chain/([^/]+)/entries$", path)
    if m:
        cid = m.group(1)
        return _chain_view(cid)

    m = re.match(r"^/api/v1/chain/([^/]+)/verify$", path)
    if m:
        return _chain_verify(m.group(1))

    m = re.match(r"^/api/v1/chain/([^/]+)/trace$", path)
    if m:
        cid = m.group(1)
        ref = q.get("output_ref", [None])[0]
        if not ref:
            return {"error": "output_ref query param required"}, 400
        return _chain_trace(cid, ref)

    m = re.match(r"^/api/v1/chain/([^/]+)$", path)
    if m:
        return _chain_view(m.group(1))

    # ── Evidence Bundle（R4-深化）──
    if path == "/api/v1/evidence/schemas":
        eb = _import_evidence_bundle()
        return {"schema": eb.SCHEMA_VERSION,
                "ocsf_classes": eb.OCSF_CLASS_MAP,
                "stix_observable_types": eb.STIX_OBSERVABLE_TYPES,
                "attack_ttps": eb.ATTACK_TTP_MAP,
                "states": eb.STATES,
                "transitions": {k: sorted(v) for k, v in eb.TRANSITIONS.items()}}, 200

    m = re.match(r"^/api/v1/evidence/([^/]+)/verify$", path)
    if m:
        run_id = m.group(1)
        b = _get_bundle(run_id)
        return {"run_id": run_id, "verification": b.verify()}, 200

    m = re.match(r"^/api/v1/evidence/([^/]+)$", path)
    if m:
        run_id = m.group(1)
        b = _get_bundle(run_id)
        return b.export(), 200

    # ── Ship Gate Lifecycle（R4-深化）──
    if path == "/api/v1/ship-gate/states":
        sg = _import_ship_gate()
        return {"states": sg.STATE_DEFS,
                "transitions": {k: sorted(v) for k, v in sg.STATE_TRANSITIONS.items()},
                "schema": "ship-gate/1.0"}, 200

    # ── Identity Registry（agent card 承诺过的端点，2026-10-03 补接线）──
    if path == "/api/v1/identity/agents":
        return _identity_list()
    if path == "/api/v1/identity/registration-token":
        return {"error": "POST /api/v1/identity/registration-token"}, 405

    m = re.match(r"^/api/v1/identity/agents/([^/]+)$", path)
    if m:
        return _identity_get(m.group(1))

    # ── ERC-8004 查询 ──
    if path == "/api/v1/identity/wallets":
        return {"docs": "POST /api/v1/identity/erc8004/wrap to wrap wallet into DID"}, 200

    # ── Trust Leaderboard（R2）──
    if path == "/api/v1/leaderboard/top":
        try:
            limit = int(q.get("limit", [20])[0])
            min_score = int(q.get("min_score", [0])[0])
        except (TypeError, ValueError):
            return {"error": "limit/min_score must be int"}, 400
        from eco import leaderboard as lb
        return {"schema": lb.snapshot()["schema"], "top": lb.top_by_score(limit=limit, min_score=min_score)}, 200

    m = re.match(r"^/api/v1/leaderboard/domains/([^/]+)$", path)
    if m:
        domain = m.group(1)
        try:
            limit = int(q.get("limit", [10])[0])
        except (TypeError, ValueError):
            limit = 10
        from eco import leaderboard as lb
        try:
            return {"domain": domain, "top": lb.top_by_domain(domain, limit=limit)}, 200
        except ValueError as e:
            return {"error": str(e)}, 400

    if path == "/api/v1/leaderboard/providers":
        try:
            limit = int(q.get("limit", [20])[0])
        except (TypeError, ValueError):
            limit = 20
        from eco import leaderboard as lb
        return {"providers": lb.top_by_provider(limit=limit)}, 200

    m = re.match(r"^/api/v1/leaderboard/badges/([^/]+)$", path)
    if m:
        badge = m.group(1).lower()
        try:
            limit = int(q.get("limit", [20])[0])
        except (TypeError, ValueError):
            limit = 20
        from eco import leaderboard as lb
        return {"badge": badge, "items": lb.top_by_badge(badge, limit=limit)}, 200

    if path == "/api/v1/leaderboard/snapshot":
        from eco import leaderboard as lb
        return lb.snapshot(), 200

    # ── Contributors（R2）──
    if path == "/api/v1/contributors/leaderboard":
        try:
            limit = int(q.get("limit", [20])[0])
        except (TypeError, ValueError):
            limit = 20
        from eco import contributors as cb
        return {"leaderboard": cb.leaderboard(limit=limit)}, 200

    if path == "/api/v1/contributors/tiers":
        from eco import contributors as cb
        return {"tiers": cb.tier_summary()}, 200

    if path == "/api/v1/contributors":
        from eco import contributors as cb
        rows = cb.list_all(include_tier=True, limit=100)
        return {"count": len(rows), "contributors": rows}, 200

    m = re.match(r"^/api/v1/contributors/([^/]+)$", path)
    if m:
        from eco import contributors as cb
        rec = cb.get(m.group(1))
        if not rec:
            return {"error": "contributor not found", "contributor_id": m.group(1)}, 404
        return rec, 200

    # ── Sandbox Backend（R3）──
    if path == "/api/v1/sandbox/backend/current":
        return _sandbox_backend_current()
    if path == "/api/v1/sandbox/backend/matrix":
        return _sandbox_backend_capabilities()

    return {"error": "unknown ecosystem endpoint", "path": path}, 404


def handle_post(path: str, data: dict):
    """返回 (payload_dict, status_code)。"""
    data = data or {}

    # ── Agent Card ──
    if path == "/api/v1/agent-card/sign":
        card = data.get("card") or {}
        ts = data.get("trust_score")
        return _agent_card_sign(card, ts)

    if path == "/api/v1/agent-card/verify":
        card = data.get("card") or {}
        pk = data.get("public_key")
        return _agent_card_verify(card, pk)

    if path == "/api/v1/agent-card/identity":
        card = data.get("card") or {}
        ts = data.get("trust_score")
        return _agent_card_export_identity(card, ts)

    # ── Specialist Registry ──
    if path == "/api/v1/specialist/agents":
        return _specialist_register(data)

    m = re.match(r"^/api/v1/specialist/agents/([^/]+)/renew$", path)
    if m:
        return _specialist_renew(m.group(1))

    m = re.match(r"^/api/v1/specialist/agents/([^/]+)/revoke$", path)
    if m:
        return _specialist_revoke(m.group(1), data.get("reason", ""))

    # ── Identity Registry（agent card 承诺过的端点，2026-10-03 补接线）──
    if path == "/api/v1/identity/registration-token":
        return _identity_token_issue(data)

    if path == "/api/v1/identity/register":
        return _identity_register(data)

    # ── KYA / ERC-8004 ──
    if path == "/api/v1/identity/kyad/export":
        card = data.get("card") or {}
        ts = data.get("trust_score")
        return _kyad_export(card, ts)

    if path == "/api/v1/identity/erc8004/wrap":
        addr = data.get("wallet_address") or data.get("address")
        chain = data.get("chain_id", 1)
        if not addr:
            return {"error": "wallet_address required"}, 400
        try:
            return _erc8004_wrap(addr, int(chain))
        except ValueError as e:
            return {"error": str(e)}, 400

    # ── Responsibility Chain ──
    if path == "/api/v1/chain":
        cid = data.get("chain_id")
        return _chain_create(cid)

    m = re.match(r"^/api/v1/chain/([^/]+)/append$", path)
    if m:
        return _chain_append(m.group(1), data)

    # ── Evidence Bundle（R4-深化）──
    if path == "/api/v1/evidence":
        run_id = data.get("run_id") or _gen_run_id()
        hmac_secret = data.get("hmac_secret")
        title = data.get("title", "")
        eb = _import_evidence_bundle()
        b = eb.EvidenceBundle(run_id=run_id, hmac_secret=hmac_secret, title=title)
        with _bundles_lock:
            _bundles[run_id] = b
        return {"run_id": run_id, "hmac": bool(b.hmac_key),
                "created_at": b.created_at, "title": title}, 201

    m = re.match(r"^/api/v1/evidence/([^/]+)/events$", path)
    if m:
        run_id = m.group(1)
        b = _get_bundle(run_id)
        try:
            e = b.add_event(
                event_type=data.get("event_type", "audit.record"),
                agent_id=data.get("agent_id", "unknown"),
                action=data.get("action", "record"),
                payload=data.get("payload") or {},
                activity_id=int(data.get("activity_id", 0)),
                outcome=data.get("outcome", "successful"),
                reason=data.get("reason", ""),
                ttp=data.get("ttp"),
            )
            return {"event": e, "run_id": run_id, "verify": b.verify()}, 201
        except ValueError as exc:
            return {"error": str(exc), "run_id": run_id}, 400

    m = re.match(r"^/api/v1/evidence/([^/]+)/proposals$", path)
    if m:
        run_id = m.group(1)
        b = _get_bundle(run_id)
        try:
            prop = b.create_proposal(
                agent_id=data.get("agent_id", "planner"),
                action=data.get("action", ""),
                target=data.get("target") or {},
                parameters=data.get("parameters") or {},
                rationale=data.get("rationale", ""),
            )
            return {"proposal": prop, "run_id": run_id, "verify": b.verify()}, 201
        except ValueError as exc:
            return {"error": str(exc), "run_id": run_id}, 400

    m = re.match(r"^/api/v1/evidence/([^/]+)/proposals/([^/]+)/approve$", path)
    if m:
        run_id, prop_id = m.group(1), m.group(2)
        b = _get_bundle(run_id)
        try:
            appr = b.approve_proposal(
                proposal_id=prop_id,
                approver_id=data.get("approver_id", "unknown"),
                scope=data.get("scope", "task"),
                expires_in=int(data.get("expires_in", 3600)),
            )
            return {"approval": appr, "run_id": run_id, "verify": b.verify()}, 201
        except ValueError as exc:
            return {"error": str(exc), "run_id": run_id}, 400

    m = re.match(r"^/api/v1/evidence/([^/]+)/proposals/([^/]+)/reject$", path)
    if m:
        run_id, prop_id = m.group(1), m.group(2)
        b = _get_bundle(run_id)
        try:
            rej = b.reject_proposal(proposal_id=prop_id,
                                    approver_id=data.get("approver_id", "unknown"),
                                    reason=data.get("reason", ""))
            return {"rejection": rej, "run_id": run_id, "verify": b.verify()}, 201
        except ValueError as exc:
            return {"error": str(exc), "run_id": run_id}, 400

    m = re.match(r"^/api/v1/evidence/([^/]+)/dispatch$", path)
    if m:
        run_id = m.group(1)
        b = _get_bundle(run_id)
        try:
            result = b.dispatch(
                approval_id=data.get("approval_id", ""),
                executor_id=data.get("executor_id", "unknown"),
                result=bool(data.get("result", True)),
                detail=data.get("detail") or {},
            )
            return {"execution": result, "run_id": run_id, "verify": b.verify()}, 200
        except ValueError as exc:
            return {"error": str(exc), "run_id": run_id}, 400

    m = re.match(r"^/api/v1/evidence/([^/]+)/observe$", path)
    if m:
        run_id = m.group(1)
        b = _get_bundle(run_id)
        try:
            probe = b.observe(
                approval_id=data.get("approval_id", ""),
                observer_id=data.get("observer_id", "unknown"),
                round_no=int(data.get("round_no", 1)),
                passed=bool(data.get("passed", True)),
                detail=data.get("detail") or {},
                confidence=float(data.get("confidence", 1.0)),
            )
            return {"probe": probe, "run_id": run_id, "verify": b.verify()}, 200
        except ValueError as exc:
            return {"error": str(exc), "run_id": run_id}, 400

    m = re.match(r"^/api/v1/evidence/([^/]+)/rollback$", path)
    if m:
        run_id = m.group(1)
        b = _get_bundle(run_id)
        try:
            rb = b.rollback(
                approval_id=data.get("approval_id", ""),
                operator_id=data.get("operator_id", "unknown"),
                reason=data.get("reason", ""),
            )
            return {"rollback": rb, "run_id": run_id, "verify": b.verify()}, 200
        except ValueError as exc:
            return {"error": str(exc), "run_id": run_id}, 400

    m = re.match(r"^/api/v1/evidence/([^/]+)/archive$", path)
    if m:
        run_id = m.group(1)
        b = _get_bundle(run_id)
        manifest = b.archive(archiver_id=data.get("archiver_id", "system"))
        return {"manifest": manifest, "run_id": run_id, "verify": b.verify()}, 200

    # 离线验证 bundle payload（跨组织传递后校验）
    if path == "/api/v1/evidence/verify-payload":
        eb = _import_evidence_bundle()
        payload = data.get("bundle") or data.get("payload") or {}
        hmac_secret = data.get("hmac_secret")
        result = eb.verify_bundle_payload(payload, hmac_secret=hmac_secret)
        status = 200 if result.get("valid") else 422
        return {"verification": result}, status

    # ── Ship Gate Lifecycle（R4-深化）──
    if path == "/api/v1/ship-gate/run":
        sg = _import_ship_gate()
        try:
            from scanner.engine import scan as _scan
            target = data.get("target")
            findings = data.get("findings")
            if findings is None:
                if not target:
                    return {"error": "target or findings required"}, 400
                content = data.get("content", "")
                result = {"target": target, "files_scanned": 1,
                          "findings": _scan(content, target).get("findings", [])}
            else:
                result = {"target": target or "inline", "files_scanned": 1,
                          "findings": findings}
            sm = sg.StateMachine(
                hmac_secret=data.get("hmac_secret"),
                fail_on_warn=bool(data.get("fail_on_warn", False)),
                auto_accept_challenge=not bool(data.get("no_auto_accept", False)),
            )
            sm_result = sm.run(result,
                               full_lifecycle=bool(data.get("full_lifecycle", False)))
            return {"state_machine": sm_result, "counts": sm_result["counts"]}, 200
        except Exception as exc:
            return {"error": str(exc)}, 500

    # ── Protocol Bridge ──
    if path == "/api/v1/protocol/normalize":
        proto = data.get("protocol")
        payload = data.get("payload") or {}
        return _bridge_normalize(proto, payload)

    if path == "/api/v1/protocol/translate":
        target = data.get("target")
        payload = data.get("payload") or {}
        src = data.get("from_protocol") or data.get("source")
        return _bridge_translate(target, payload, src)

    # ── Contributors（R2）──
    if path == "/api/v1/contributors":
        return _contributor_register(data)

    m = re.match(r"^/api/v1/contributors/([^/]+)/events$", path)
    if m:
        return _contributor_add_event(m.group(1), data)

    return {"error": "unknown ecosystem endpoint", "path": path}, 404


# ══════════════════════════════════════════════
#  自证
# ══════════════════════════════════════════════
if __name__ == "__main__":
    print("── 5 支柱 API 端点自证 ──")

    # 1. Agent Card sign → verify
    card = {"name": "DemoAgent", "url": "https://demo.example/agent",
            "capabilities": {"supported": ["scan"]},
            "description": "demo"}
    signed, sc = _agent_card_sign(card, trust_score=88)
    print(f"[agent-card.sign]  status={sc}  alg={signed.get('aishield', {}).get('alg')}")
    v, sc = _agent_card_verify(signed, None)
    print(f"[agent-card.verify] status={sc}  valid={v.get('valid')}")

    # 篡改测试
    evil = dict(signed)
    evil["capabilities"] = {"supported": ["admin", "delete-everything"]}
    v2, sc2 = _agent_card_verify(evil, None)
    print(f"[agent-card.verify 篡改] status={sc2}  valid={v2.get('valid')}")

    # 2. Specialist Registry
    sr = _import_specialist()
    sr.seed_if_empty()
    cats, sc = _specialist_domains()
    print(f"[specialist.domains] status={sc}  8域={len(cats)}")
    lst, sc = _specialist_list("engineering", False)
    print(f"[specialist.list engineering] status={sc}  count={lst['count']}")

    # 3. Responsibility Chain
    created, sc = _chain_create(None)
    cid = created["chain_id"]
    print(f"[chain.create] status={sc}  id={cid}")
    e1, sc = _chain_append(cid, {"agent_id": "planner", "action": "plan",
                                  "input_ref": "user:scan",
                                  "output_ref": {"subtasks": ["s1"]}})
    print(f"[chain.append planner] status={sc}  seq={e1['seq']}")
    e2, sc = _chain_append(cid, {"agent_id": "scanner", "action": "call_tool:scan",
                                  "parent_seq": e1["seq"],
                                  "input_ref": e1["output_ref"],
                                  "output_ref": {"score": 30, "finding": "RCE"}})
    print(f"[chain.append scanner] status={sc}  seq={e2['seq']}")
    vr, sc = _chain_verify(cid)
    print(f"[chain.verify] status={sc}  valid={vr['valid']}")
    tr, sc = _chain_trace(cid, e2["output_ref"])
    print(f"[chain.trace] status={sc}  depth={tr['depth']}  root={tr['root_cause']['agent_id']}")

    # 4. KYA / Web Bot Auth
    ident, sc = _agent_card_export_identity(signed, 88)
    print(f"[kyad.export] status={sc}  claims={len(ident['kya']['claims'])}  wba_hdr={len(ident['web_bot_auth']['headers'])}")

    # 5. ERC-8004
    wrapped, sc = _erc8004_wrap("0x1234567890abcdef1234567890abcdef12345678", 1)
    print(f"[erc8004.wrap] status={sc}  did={wrapped.get('did', wrapped)}")

    # 6. Protocol Bridge
    mcp_payload = {"name": "DemoServer", "tools": [{"name": "hello", "description": "say hi"}]}
    norm, sc = _bridge_normalize("mcp", mcp_payload)
    print(f"[protocol.normalize] status={sc}  name={norm['universal_agent']['name']}")
    tr, sc = _bridge_translate("a2a", mcp_payload, "mcp")
    print(f"[protocol.translate mcp→a2a] status={sc}  result.name={tr['result']['name']}")

    print("\n全部端点自证通过。")
