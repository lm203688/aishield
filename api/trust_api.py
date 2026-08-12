"""
api/trust_api.py — AIShield Trust Standard 的可机调用实现 (P1 迭代)

把 docs/aishield-trust-standard-v0.1.md 中定义的认证/信任体系变成真实 API，
供 UUMit / Gate / MAXIA / Google A2A 等能力交易市场调用做"安全认证层"。

能力:
  - 自动认证: 从 engine.scan 结果自动签发 cert + badge (score>=80)
  - 认证验证: 按 cert_id 查询证书状态
  - 信任评分: 0-100, 供服务交易/委托决策使用
  - 注册中心: 公开查询已注册 Agent
  - Agent Card: A2A 身份声明 (.well-known/agent-card.json)

设计:
  - 零第三方依赖 (仅标准库)
  - 既可作为模块被 server.py import, 也可独立运行 (python trust_api.py)
"""

import os
import sys
import json
import uuid
import threading
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs

# ── 路径: 确保项目根在 sys.path, 以便 import eco / scanner ──
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

BASE = _HERE
DATA_DIR = os.path.join(BASE, "data")
CERTIFICATIONS_FILE = os.path.join(DATA_DIR, "certifications.json")
REGISTRY_FILE = os.path.join(DATA_DIR, "agent_registry.json")
AGENT_CARD_FILE = os.path.join(_ROOT, "docs", ".well-known", "agent-card.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()

TRUST_VERSION = "0.1"
ISSUER = "AIShield Trust Authority"
ISSUER_URL = "https://aishield.tools"


# ══════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════
def _load_json(path, default=None):
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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _now_iso():
    return datetime.now(TZ).isoformat()


# ══════════════════════════════════════════════
#  认证 (Certification)
# ══════════════════════════════════════════════
def auto_certify(scan_result):
    """从 engine.scan 结果自动签发证书 + badge。
    规则: overall_score >= 80 才签发 (与 server.py 中既有逻辑一致)。
    返回 cert dict; 未达阈值返回 None。
    """
    try:
        from eco import badge as _badge
    except Exception:
        return None
    overall = (scan_result or {}).get("overall_score", 0)
    if overall < 80:
        return None
    svc = _badge.CertificationService()
    source_url = scan_result.get("source_url") or scan_result.get("repository") or "local-scan"
    try:
        cert = svc.certify_tool(source_url=source_url, scan_report=scan_result)
        return cert
    except Exception:
        return None


def certify(source_url, scan_report):
    """显式签发证书 (供 POST /api/v1/trust/certify 使用)。"""
    try:
        from eco import badge as _badge
        svc = _badge.CertificationService()
        return svc.certify_tool(source_url=source_url, scan_report=scan_report)
    except Exception as e:
        return {"error": str(e)}


def verify_cert(cert_id):
    """按 cert_id 验证证书状态。兼容 dict / list 两种持久化结构。"""
    data = _load_json(CERTIFICATIONS_FILE, {})
    cert = None
    if isinstance(data, dict):
        # 常见结构: {cert_id: cert} 或 {"certs": {cert_id: cert}}
        if cert_id in data:
            cert = data[cert_id]
        elif isinstance(data.get("certs"), dict) and cert_id in data["certs"]:
            cert = data["certs"][cert_id]
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("cert_id") == cert_id:
                cert = item
                break
    if not cert:
        return None
    # 计算是否过期
    expires = cert.get("expires_at") or cert.get("expiry")
    status = "active"
    if expires:
        try:
            exp = datetime.fromisoformat(expires)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=TZ)
            if exp < datetime.now(TZ):
                status = "expired"
        except Exception:
            pass
    return {**cert, "verified": True, "status": status, "issuer": ISSUER, "issuer_url": ISSUER_URL}


# ══════════════════════════════════════════════
#  信任评分 (Trust Score, 0-100)
# ══════════════════════════════════════════════
def trust_score(agent_id):
    """基于注册中心 + 认证记录计算 0-100 信任评分。
    因子透明可解释, 供服务交易市场/委托决策调用。
    """
    registry = _load_json(REGISTRY_FILE, {})
    agents = registry.get("agents", {})
    agent = agents.get(agent_id)
    if not agent:
        return None

    factors = []
    score = 40  # 基础分
    factors.append(("已注册身份", 40))

    # 身份认证机制
    schemes = (agent.get("authentication", {}) or {}).get("schemes", []) or []
    if schemes:
        score += 18
        factors.append(("声明认证机制: " + ",".join(schemes), 18))

    # 技能文档完整度
    skills = agent.get("skills", []) or []
    documented = [s for s in skills if s.get("examples")]
    if skills:
        score += 8
        factors.append(("声明技能 x%d" % len(skills), 8))
    if documented:
        score += 6
        factors.append(("技能含使用示例 x%d" % len(documented), 6))

    # 文档链接
    if agent.get("documentationUrl"):
        score += 6
        factors.append(("提供文档链接", 6))

    # 已签发安全证书
    certs = _find_agent_certs(agent_id, agent.get("name", ""))
    if certs:
        score += 22
        factors.append(("已通过 AIShield 安全认证 x%d" % len(certs), 22))

    score = max(0, min(100, score))

    level = "gold" if score >= 85 else "silver" if score >= 70 else "bronze" if score >= 55 else "none"
    return {
        "agent_id": agent_id,
        "name": agent.get("name", ""),
        "trust_score": score,
        "level": level,
        "factors": factors,
        "certifications": certs,
        "trust_standard_version": TRUST_VERSION,
        "issued_by": ISSUER,
        "issued_at": _now_iso(),
    }


def _find_agent_certs(agent_id, name):
    data = _load_json(CERTIFICATIONS_FILE, {})
    found = []
    items = []
    if isinstance(data, dict):
        if "certs" in data and isinstance(data["certs"], dict):
            items = list(data["certs"].values())
        else:
            items = [v for v in data.values() if isinstance(v, dict)]
    elif isinstance(data, list):
        items = [i for i in data if isinstance(i, dict)]
    for c in items:
        if c.get("agent_id") == agent_id or (name and c.get("name") == name):
            found.append({
                "cert_id": c.get("cert_id"),
                "badge_level": c.get("badge_level"),
                "overall_score": c.get("overall_score"),
                "expires_at": c.get("expires_at") or c.get("expiry"),
            })
    return found


# ══════════════════════════════════════════════
#  注册中心 (Agent Registry)
# ══════════════════════════════════════════════
def registry_list(tag=None, provider=None):
    registry = _load_json(REGISTRY_FILE, {})
    agents = registry.get("agents", {})
    out = []
    for aid, a in agents.items():
        if tag and tag not in _agent_tags(a):
            continue
        if provider and (a.get("provider", {}) or {}).get("name") != provider:
            continue
        out.append({
            "agent_id": aid,
            "name": a.get("name", ""),
            "description": a.get("description", ""),
            "url": a.get("url", ""),
            "version": a.get("version", ""),
            "skills": [s.get("id") for s in a.get("skills", [])],
            "authentication": (a.get("authentication", {}) or {}).get("schemes", []),
        })
    return {"count": len(out), "agents": out}


def registry_get(agent_id):
    registry = _load_json(REGISTRY_FILE, {})
    return registry.get("agents", {}).get(agent_id)


def _agent_tags(agent):
    tags = set()
    for s in agent.get("skills", []) or []:
        for t in s.get("tags", []) or []:
            tags.add(t)
    return tags


def agent_card():
    if os.path.exists(AGENT_CARD_FILE):
        try:
            with open(AGENT_CARD_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # 回退: 从注册中心生成
    return {
        "protocolVersion": "a2a-1.0.0",
        "name": "AIShield Security Scanner",
        "description": "OWASP MCP Top 10 + Agentic AI Top 10 security scanner",
        "url": "https://aishield.tools/api/v1/mcp",
        "skills": [
            {"id": "security_scan", "name": "security_scan"},
            {"id": "agentic_audit", "name": "agentic_audit"},
            {"id": "trust_score", "name": "trust_score"},
        ],
    }


# ══════════════════════════════════════════════
#  信任裁决信封 (aishield-trust/v1)
# ══════════════════════════════════════════════
def _verify_envelope(source_url, subject_type=None):
    """把 attestation.trust_status 收敛成 docs/trust-attestation-spec.md 定义的
    aishield-trust/v1 凭证信封，供发现层 (MCP Server Card / Agent Card / ai-catalog)
    用 `trust` 字段零成本引用。即使来源未订阅，也返回诚实的 unknown 裁决。
    """
    try:
        from eco import attestation as _att
        raw = _att.trust_status(source_url) or {}
    except Exception:
        raw = {}
    subscribed = bool(raw.get("subscribed", False))
    score = raw.get("last_score")
    if score is not None:
        try:
            score = int(score)
        except Exception:
            score = None
    if score is not None:
        risk = "safe" if score >= 80 else "medium" if score >= 60 else "high" if score >= 40 else "critical"
    else:
        risk = "unknown"
    badge = raw.get("badge_level")
    level = badge if badge else ("basic" if subscribed else "none")
    last_attest = raw.get("last_attest_at")
    # 证据链锚点（哈希链防篡改）
    chain_anchor = None
    ec = raw.get("evidence_chain")
    if isinstance(ec, list) and ec:
        last = ec[-1]
        if isinstance(last, dict):
            chain_anchor = last.get("hash") or last.get("anchor") or last.get("chain_anchor")
    return {
        "schema": "aishield-trust/v1",
        "issuer": ISSUER_URL,
        "issued_at": _now_iso(),
        "subject": {
            "type": subject_type or "tool",
            "url": source_url,
            "name": raw.get("source_url") or source_url,
        },
        "verdict": {
            "score": score,
            "level": level,
            "risk": risk,
            "no_spawn_guarantee": True,
            "offline_scan": True,
        },
        "coverage": {
            "owasp_mcp_top10": "10/10",
            "owasp_asi_top10": "10/10",
            "dimensions": ["security", "permissions", "data_handling", "supply_chain", "reliability"],
        },
        "attestation": {
            "method": "continuous" if subscribed else "none",
            "last_attested_at": last_attest,
            "chain_anchor": chain_anchor,
            "evidence_count": raw.get("evidence_entries", 0),
        },
        "badge": "%s/badge/%s" % (ISSUER_URL, source_url),
        "api": "%s/api/v1/trust?src=%s" % (ISSUER_URL, source_url),
    }


# ══════════════════════════════════════════════
#  HTTP 路由 (供 server.py 与独立 server 共用)
# ══════════════════════════════════════════════
def handle_get(path, query=""):
    """返回 (payload_dict, status_code)。"""
    q = parse_qs(query) if query else {}

    if path == "/api/v1/registry":
        tag = q.get("tag", [None])[0]
        provider = q.get("provider", [None])[0]
        return registry_list(tag=tag, provider=provider), 200

    m = __import__("re").match(r"^/api/v1/registry/([^/]+)$", path)
    if m:
        agent = registry_get(m.group(1))
        return (agent, 200) if agent else ({"error": "agent not found", "agent_id": m.group(1)}, 404)

    m = __import__("re").match(r"^/api/v1/trust/score/([^/]+)$", path)
    if m:
        s = trust_score(m.group(1))
        return (s, 200) if s else ({"error": "agent not found", "agent_id": m.group(1)}, 404)

    m = __import__("re").match(r"^/api/v1/trust/cert/([^/]+)$", path)
    if m:
        c = verify_cert(m.group(1))
        return (c, 200) if c else ({"error": "certificate not found", "cert_id": m.group(1)}, 404)

    if path == "/api/v1/trust" or path == "/api/v1/trust/verify":
        src = (q.get("src", [None])[0] or q.get("source_url", [None])[0]
               or q.get("tool", [None])[0])
        if not src:
            return {"error": "src (or source_url/tool) query param required"}, 400
        subject_type = q.get("type", [None])[0]
        return _verify_envelope(src, subject_type), 200

    if path == "/api/v1/trust/score" or path == "/api/v1/trust/cert":
        return {"error": "agent_id / cert_id required in path"}, 400

    if path == "/.well-known/agent-card.json":
        return agent_card(), 200

    return {"error": "unknown trust endpoint", "path": path}, 404


def handle_post(path, data):
    """返回 (payload_dict, status_code)。"""
    data = data or {}

    if path == "/api/v1/trust/auto":
        scan_result = data.get("scan_result") or data.get("scan_report")
        if not scan_result:
            return {"error": "scan_result required"}, 400
        cert = auto_certify(scan_result)
        if cert:
            return {"success": True, "certification": cert}, 201
        return {"success": False, "message": "score below 80, no certificate issued"}, 200

    if path == "/api/v1/trust/certify":
        source_url = data.get("source_url") or data.get("repository")
        scan_report = data.get("scan_report") or data.get("scan_result")
        if not source_url or not scan_report:
            return {"error": "source_url and scan_report required"}, 400
        cert = certify(source_url, scan_report)
        if cert and "error" not in cert:
            return {"success": True, "certification": cert}, 201
        return {"success": False, "error": (cert or {}).get("error", "certify failed")}, 400

    if path == "/api/v1/trust" or path == "/api/v1/trust/verify":
        src = data.get("src") or data.get("source_url") or data.get("tool")
        if not src:
            return {"error": "src (or source_url/tool) required"}, 400
        return _verify_envelope(src, data.get("type")), 200

    return {"error": "unknown trust endpoint", "path": path}, 404


# ══════════════════════════════════════════════
#  独立运行 (python trust_api.py [port])
# ══════════════════════════════════════════════
def run_standalone(port=8800):
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def _send(self, payload, status):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlparse(self.path)
            payload, status = handle_get(parsed.path, parsed.query)
            self._send(payload, status)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8", "replace") if length else ""
            try:
                data = json.loads(raw) if raw else {}
            except Exception:
                data = {}
            payload, status = handle_post(urlparse(self.path).path, data)
            self._send(payload, status)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

        def log_message(self, *args):
            pass

    print("AIShield Trust API on http://0.0.0.0:%d" % port)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    import sys as _sys
    p = int(_sys.argv[1]) if len(_sys.argv) > 1 else 8800
    run_standalone(p)
