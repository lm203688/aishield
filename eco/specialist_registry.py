"""
eco/specialist_registry.py — 专业 agent 注册表（支柱 L2：小 agent 生态）

理念：百花齐放时代，最有活力的是**垂直/专业 agent**，而不是又一个通用平台。
本注册表按 8 大专业域组织 agent，让注册者一次声明域/能力/证书，
消费方（编排器、LLM 路由、审计）可以按域查询。

8 大专业域（对齐 OWASP AIUC-1 场景 + 2026 生态主流赛道）：
  legal      法律 / 合规
  medical    医疗 / 生物
  finance    金融 / 支付
  education  教育 / 培训
  engineering代码 / 系统运维
  design     内容 / 设计
  research   科研 / 数据分析
  civic      政务 / 民生

每条注册记录强制包含：
  - agent_id / name / domain
  - capabilities（本域内的具体能力清单）
  - certifications（持有的证书/徽章/attestation 引用）
  - signed_at / publisher_did（谁签发的）

状态：注册即可上线，被吊销或超时未续期则降级。

零依赖；数据文件在 api/data/specialist_registry.json。
线程安全。
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone, timedelta

try:
    from eco import agent_card
except ImportError:  # 允许以脚本方式直接运行自测
    import agent_card

TZ = timezone(timedelta(hours=8))
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE, "api", "data")
_REGISTRY_FILE = os.path.join(_DATA_DIR, "specialist_registry.json")

_lock = threading.RLock()

# 8 大专业域：定义 + 每域典型能力标签
DOMAINS = {
    "legal":       {"label": "法律 / 合规",      "tags": ["contract", "compliance", "dispute", "review"]},
    "medical":     {"label": "医疗 / 生物",      "tags": ["diagnosis", "drug", "imaging", "genomics"]},
    "finance":     {"label": "金融 / 支付",      "tags": ["risk", "trading", "audit", "payment"]},
    "education":   {"label": "教育 / 培训",      "tags": ["tutor", "assessment", "curriculum", "mentor"]},
    "engineering": {"label": "代码 / 系统运维",   "tags": ["coding", "devops", "debugging", "architecture"]},
    "design":      {"label": "内容 / 设计",      "tags": ["writing", "art", "video", "branding"]},
    "research":    {"label": "科研 / 数据分析",   "tags": ["analysis", "literature", "simulation", "visualization"]},
    "civic":       {"label": "政务 / 民生",      "tags": ["public-service", "social-welfare", "urban", "tax"]},
}

# 证书状态
STATE_ACTIVE = "active"
STATE_REVOKED = "revoked"
STATE_LAPSED = "lapsed"

DEFAULT_TTL_DAYS = 90   # 注册后 90 天需 renew


def _now_iso():
    return datetime.now(TZ).isoformat()


def _load() -> dict:
    if not os.path.exists(_REGISTRY_FILE):
        return {"version": 1, "agents": {}}
    try:
        with open(_REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": 1, "agents": {}}


def _save(doc: dict):
    os.makedirs(_DATA_DIR, exist_ok=True)
    tmp = _REGISTRY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _REGISTRY_FILE)


def _fingerprint(agent_id: str, domain: str, capabilities: list, certs: list) -> str:
    payload = json.dumps(
        {"id": agent_id, "d": domain, "c": sorted(capabilities or []), "certs": sorted(certs or [])},
        ensure_ascii=False, sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# ── 注册 / 更新 ──
def register_agent(
    *, agent_id: str, name: str, domain: str,
    capabilities: list, certs: list = None,
    url: str = "", provider: str = "", description: str = "",
    publisher_did: str | None = None,
    extra: dict = None,
) -> dict:
    """注册（或覆盖更新）一个专业 agent。返回完整记录。"""
    # #441：publisher_did 缺省时统一为信任服务自认证 did:key（密钥不可用回退旧标签）。
    if not publisher_did:
        publisher_did = agent_card.get_signer_did()
    if domain not in DOMAINS:
        raise ValueError(f"unknown domain: {domain}; must be one of {list(DOMAINS)}")
    if not agent_id or not name:
        raise ValueError("agent_id and name are required")
    if not capabilities:
        raise ValueError("capabilities list cannot be empty")
    now = _now_iso()
    expires_ts = time.time() + DEFAULT_TTL_DAYS * 86400
    with _lock:
        doc = _load()
        record = {
            "agent_id": agent_id,
            "name": name,
            "domain": domain,
            "capabilities": list(capabilities),
            "certs": list(certs or []),
            "url": url,
            "provider": provider,
            "description": description,
            "publisher_did": publisher_did,
            "registered_at": now,
            "updated_at": now,
            "expires_at": now,
            "expires_ts": expires_ts,
            "state": STATE_ACTIVE,
            "fingerprint": _fingerprint(agent_id, domain, capabilities, certs or []),
            "extra": extra or {},
        }
        doc["agents"][agent_id] = record
        _save(doc)
        return dict(record)


def renew(agent_id: str) -> dict | None:
    """续期：把 expires_ts 向后推 DEFAULT_TTL_DAYS 天。"""
    with _lock:
        doc = _load()
        rec = doc["agents"].get(agent_id)
        if not rec:
            return None
        now = _now_iso()
        rec["expires_at"] = now
        rec["expires_ts"] = time.time() + DEFAULT_TTL_DAYS * 86400
        rec["updated_at"] = now
        rec["state"] = STATE_ACTIVE
        _save(doc)
        return dict(rec)


def revoke(agent_id: str, reason: str = "") -> dict | None:
    """吊销注册。"""
    with _lock:
        doc = _load()
        rec = doc["agents"].get(agent_id)
        if not rec:
            return None
        rec["state"] = STATE_REVOKED
        rec["revoked_at"] = _now_iso()
        rec["revoke_reason"] = reason
        _save(doc)
        return dict(rec)


def get(agent_id: str) -> dict | None:
    with _lock:
        return _load()["agents"].get(agent_id)


def list_agents(domain: str | None = None, include_lapsed: bool = False) -> list:
    """按域列出 agent；include_lapsed=True 时把过期但未吊销的也算。"""
    with _lock:
        doc = _load()
        result = []
        now_ts = time.time()
        for rec in doc["agents"].values():
            if domain and rec.get("domain") != domain:
                continue
            state = rec.get("state", STATE_ACTIVE)
            if state == STATE_REVOKED:
                continue
            if state == STATE_ACTIVE and rec.get("expires_ts", 0) < now_ts:
                if not include_lapsed:
                    continue
                rec = dict(rec)
                rec["state"] = STATE_LAPSED
            result.append(rec)
        return result


def list_by_domain() -> dict:
    """聚合视图：每个域下多少 agent。"""
    with _lock:
        doc = _load()
        now_ts = time.time()
        counts = {d: {"active": 0, "lapsed": 0, "revoked": 0} for d in DOMAINS}
        for rec in doc["agents"].values():
            d = rec.get("domain")
            if d not in counts:
                continue
            state = rec.get("state", STATE_ACTIVE)
            if state == STATE_REVOKED:
                counts[d]["revoked"] += 1
            elif state == STATE_ACTIVE and rec.get("expires_ts", 0) < now_ts:
                counts[d]["lapsed"] += 1
            else:
                counts[d]["active"] += 1
        return counts


def domains_catalog() -> list:
    """返回 8 域目录（供 API 消费）。"""
    counts = list_by_domain()
    return [
        {"id": d, "label": info["label"], "tags": info["tags"], **counts[d]}
        for d, info in DOMAINS.items()
    ]


# 内置种子（首次运行填充，方便消费方看到"生态有活"）
_SEED = [
    ("aishield-scanner", "AIShield Security Scanner", "engineering",
     ["security-scan", "compliance-check", "mcp-audit"], [],
     "https://aishield.tools", "AIShield",
     "OWASP MCP Top10 + ASI01-10 安全扫描，235+ 规则，零依赖"),
    ("aishield-prober", "AIShield Live Probe", "engineering",
     ["live-probe", "regression-scan"], [],
     "https://aishield.tools", "AIShield",
     "对已上线 agent / MCP 做持续复扫，检测 rug-pull"),
]


def seed_if_empty(force: bool = False) -> int:
    """注册示例 agent（幂等）。force=True 时清空重建。"""
    with _lock:
        if force:
            with open(_REGISTRY_FILE, "w", encoding="utf-8") as f:
                json.dump({"version": 1, "agents": {}}, f)
        doc = _load()
        added = 0
        for aid, name, dom, caps, certs, url, prov, desc in _SEED:
            if aid in doc["agents"]:
                continue
            register_agent(agent_id=aid, name=name, domain=dom, capabilities=caps,
                           certs=certs, url=url, provider=prov, description=desc)
            added += 1
        return added


if __name__ == "__main__":
    seed_if_empty(force=True)
    print("域目录：")
    for d in domains_catalog():
        print(f"  {d['id']:>12}  {d['label']}  active={d['active']}  lapsed={d['lapsed']}")
    print("\nengineering 域列表：")
    for rec in list_agents(domain="engineering"):
        print(f"  - {rec['agent_id']:>24}  caps={rec['capabilities']}")
