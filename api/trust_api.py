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
import hashlib
import base64
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
ATTESTATIONS_FILE = os.path.join(DATA_DIR, "attestations.json")
SCHEMA_DIR = os.path.join(_ROOT, "schema")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()

TRUST_VERSION = "0.1"
ATTESTATION_VERSION = "1.0"
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
#  紧凑信任摘要 (aishield-digest/v1)
# ══════════════════════════════════════════════
#
# 为什么需要它：完整的裁决信封有一个 agent 真正需要的字段，也有二十个它不需要
# 的字段。agent 每一轮对话都要重新判断「这个东西我能不能信」，如果每次都拉
# 完整报告，token 花在重复传输同一份不变的内容上。
#
# 这是 Cache-to-Cache 那条观察的工程化落地：**一个紧凑但语义完整的载体，胜过
# 把整份文本重发一遍**。我们不碰模型的 KV-cache（那需要改模型内部），只做纯
# 工程压缩 —— 几百字节的摘要 + 一个内容指纹，让调用方按指纹缓存。
#
# 输入三种形态，覆盖 agent 的三种现实处境：
#   configs     — 手里有 MCP 客户端配置文本（本机发现到的、或用户粘贴的）
#   scan_result — 已经有扫描结果，只想压一压
#   src         — 只有一个远程 URL，要现成的信任裁决
#
# 对外承诺（可被下游依赖，不要悄悄改）：
#   · 不 spawn 被扫配置、不联网扫描 —— 见 no_spawn_guarantee / offline_scan
#   · 不出现凭证原文（top[] 只放 severity/type/owasp，永不回传 evidence）
#   · **risk 绝不比实际找到的最严重 finding 更轻** —— 报「安全」的门槛是
#     真的没有 critical/high/medium，而不是分数恰好越过了某一档。
#     这一条是本次实测抓到的假安心缺陷的修复（见 _SEVERITY_RISK_FLOOR）。

DIGEST_SCHEMA = "aishield-digest/v1"
_SEVERITY_ORDER = ("critical", "high", "medium", "low", "info")

# 由「实际存在的最严重 finding」推出的风险下限。
#
# 为什么必须有下限：分数的分档只看数字。两条 high 各扣 8 分 → 84 分 → 落在
# `>= 80` 这一档 → 摘要会把 `risk: "safe"` 和 `severity_counts: {"high": 2}`
# 并列发出去。agent 只读 risk 字段，于是拿到一个「安全」的配置，而它同时具有
# 明文 HTTP 远程传输和每次启动都拉未锁定版本的启动方式 —— 这是安全产品里最
# 危险的一类错误：**假安心**（plausible-but-wrong）。
#
# 所以 risk 取「分数档」与「最严重 finding 档」中更重的一方。分数仍然照原样
# 输出（它是既有的项目级约定，其它页面/审计都依赖它），只是不再允许它单独
# 决定风险标签。
# low / info 不设下限：姿态类噪音不该把一份干净配置抬成风险。
_SEVERITY_RISK_FLOOR = {"critical": "critical", "high": "high", "medium": "medium"}

# risk 值的严重程度排序，用于取二者之中更重的一方。
_RISK_RANK = {"unknown": 0, "safe": 0, "medium": 1, "high": 2, "critical": 3}


def _risk_floor(severity_counts):
    """返回 (下限 risk, 最严重 severity)；无实质 finding 时返回 (None, None)。"""
    counts = severity_counts or {}
    if not isinstance(counts, dict):
        return None, None
    for sev in _SEVERITY_ORDER:  # critical → high → medium → low → info
        if sev not in _SEVERITY_RISK_FLOOR:
            continue
        try:
            n = int(counts.get(sev, 0) or 0)
        except (TypeError, ValueError):
            n = 0
        if n > 0:
            return _SEVERITY_RISK_FLOOR[sev], sev
    return None, None


def _risk_from_score(score, severity_counts=None):
    """由分数定档，但**绝不低于实际找到的最严重 finding**。

    severity_counts 省略时行为与旧版一致（纯分数分档），因此既有调用方与
    契约测试不受影响；摘要路径传入 counts，避免「safe + high×2」自相矛盾。
    """
    if score is None:
        band = "unknown"
    elif score >= 80:
        band = "safe"
    elif score >= 60:
        band = "medium"
    elif score >= 40:
        band = "high"
    else:
        band = "critical"

    floor, _worst = _risk_floor(severity_counts)
    if floor and _RISK_RANK.get(floor, 0) > _RISK_RANK.get(band, 0):
        return floor
    return band


def _digest_fingerprint(payload):
    import hashlib

    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


# ══════════════════════════════════════════════
#  Trust Attestation 生成和验证
# ══════════════════════════════════════════════

def _load_attestation_schema():
    """加载Trust Attestation JSON Schema"""
    schema_path = os.path.join(SCHEMA_DIR, "trust-attestation-v1.json")
    if not os.path.exists(schema_path):
        return None
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _validate_attestation_schema(attestation):
    """验证attestation是否符合JSON Schema"""
    schema = _load_attestation_schema()
    if not schema:
        return False, "Schema not found"
    
    # 简单验证 - 在实际应用中可以使用jsonschema库
    required_fields = ["schema", "issuer", "subject", "verdict", "coverage", "attestation"]
    for field in required_fields:
        if field not in attestation:
            return False, f"Missing required field: {field}"
    
    # 验证schema版本
    if not attestation["schema"].startswith("trust-attestation/"):
        return False, "Invalid schema format"
    
    # 验证时间戳格式
    timestamp_fields = ["issued_at", "expires_at"]
    for field in timestamp_fields:
        if field in attestation and attestation[field]:
            try:
                datetime.fromisoformat(attestation[field].replace("Z", "+00:00"))
            except ValueError:
                return False, f"Invalid timestamp format in {field}"
    
    return True, "Valid"


def _generate_attestation_id():
    """生成唯一的attestation ID"""
    return str(uuid.uuid4())


def _hash_content(content):
    """生成内容哈希"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


def generate_attestation(subject, verdict, coverage, attestation, issuer=None, expires_at=None):
    """生成Trust Attestation凭证"""
    try:
        # 验证输入参数
        if not subject or not verdict or not coverage or not attestation:
            return None, "Missing required parameters"
        
        # 验证schema
        test_attestation = {
            "schema": "trust-attestation/v1",
            "issuer": issuer or ISSUER,
            "subject": subject,
            "verdict": verdict,
            "coverage": coverage,
            "attestation": attestation
        }
        is_valid, message = _validate_attestation_schema(test_attestation)
        if not is_valid:
            return None, f"Schema validation failed: {message}"
        
        # 生成完整的attestation
        attestation_obj = {
            "schema": "trust-attestation/v1",
            "id": _generate_attestation_id(),
            "issuer": issuer or ISSUER,
            "issued_at": datetime.now(TZ).isoformat(),
            "subject": subject,
            "verdict": verdict,
            "coverage": coverage,
            "attestation": attestation
        }
        
        if expires_at:
            attestation_obj["expires_at"] = expires_at
        
        # 计算内容指纹
        content_hash = _hash_content(json.dumps(attestation_obj, sort_keys=True))
        attestation_obj["fingerprint"] = f"sha256:{content_hash}"
        
        # 保存attestation
        attestations = _load_json(ATTESTATIONS_FILE, {})
        if not isinstance(attestations, dict):
            attestations = {}
        
        attestations[attestation_obj["id"]] = attestation_obj
        _save_json(ATTESTATIONS_FILE, attestations)
        
        return attestation_obj, None
        
    except Exception as e:
        return None, f"Failed to generate attestation: {str(e)}"


def verify_attestation(attestation_id, online_verification=True):
    """验证Trust Attestation凭证"""
    try:
        attestations = _load_json(ATTESTATIONS_FILE, {})
        if not isinstance(attestations, dict):
            return None, "Attestations not found"
        
        attestation = attestations.get(attestation_id)
        if not attestation:
            return None, "Attestation not found"
        
        # 验证schema
        is_valid, message = _validate_attestation_schema(attestation)
        if not is_valid:
            return None, f"Schema validation failed: {message}"
        
        # 检查过期时间
        if "expires_at" in attestation:
            try:
                expires = datetime.fromisoformat(attestation["expires_at"].replace("Z", "+00:00"))
                if expires < datetime.now(TZ):
                    return None, "Attestation expired"
            except ValueError:
                return None, "Invalid expiration date"
        
        # 验证指纹
        if "fingerprint" in attestation:
            content = json.dumps(attestation, sort_keys=True, ensure_ascii=False)
            expected_hash = attestation["fingerprint"]
            actual_hash = f"sha256:{_hash_content(content)}"
            if expected_hash != actual_hash:
                return None, "Fingerprint mismatch"
        
        # 在线验证
        if online_verification:
            try:
                # 这里可以添加对issuer API的在线验证
                # 例如验证badge URL是否可访问
                if "badge" in attestation:
                    badge_url = attestation["badge"]
                    # 简单的HTTP检查（在实际应用中应该使用更robust的方法）
                    import urllib.request
                    try:
                        urllib.request.urlopen(badge_url, timeout=5)
                    except Exception:
                        return None, "Badge URL not accessible"
            except Exception:
                # 在线验证失败不应该阻止整个验证过程
                pass
        
        # 添加验证状态
        verified_attestation = attestation.copy()
        verified_attestation["verified"] = True
        verified_attestation["verified_at"] = datetime.now(TZ).isoformat()
        
        return verified_attestation, None
        
    except Exception as e:
        return None, f"Verification failed: {str(e)}"


def list_attestations(subject=None, issuer=None, status=None):
    """列出attestations"""
    try:
        attestations = _load_json(ATTESTATIONS_FILE, {})
        if not isinstance(attestations, dict):
            return {"count": 0, "attestations": []}
        
        results = []
        for attestation_id, attestation in attestations.items():
            # 过滤条件
            if subject and attestation.get("subject", {}).get("url") != subject:
                continue
            if issuer and attestation.get("issuer") != issuer:
                continue
            
            # 检查状态
            current_status = "active"
            if "expires_at" in attestation:
                try:
                    expires = datetime.fromisoformat(attestation["expires_at"].replace("Z", "+00:00"))
                    if expires < datetime.now(TZ):
                        current_status = "expired"
                except ValueError:
                    current_status = "invalid"
            
            if status and current_status != status:
                continue
            
            # 添加状态信息
            result = attestation.copy()
            result["status"] = current_status
            results.append(result)
        
        return {"count": len(results), "attestations": results}
        
    except Exception as e:
        return {"error": f"Failed to list attestations: {str(e)}", "count": 0, "attestations": []}


def revoke_attestation(attestation_id, reason=None):
    """撤销attestation"""
    try:
        attestations = _load_json(ATTESTATIONS_FILE, {})
        if not isinstance(attestations, dict):
            return False, "Attestations not found"
        
        if attestation_id not in attestations:
            return False, "Attestation not found"
        
        # 标记为已撤销
        attestations[attestation_id]["revoked"] = True
        attestations[attestation_id]["revoked_at"] = datetime.now(TZ).isoformat()
        if reason:
            attestations[attestation_id]["revoked_reason"] = reason
        
        _save_json(ATTESTATIONS_FILE, attestations)
        return True, None
        
    except Exception as e:
        return False, f"Failed to revoke attestation: {str(e)}"


def create_attestation_from_scan(scan_result, subject_url, subject_type="tool"):
    """从扫描结果创建Trust Attestation"""
    try:
        # 提取扫描结果的关键信息
        summary = scan_result.get("summary", {})
        overall_score = summary.get("overall_score", 0)
        severity_counts = summary.get("severity_counts", {})
        
        # 构建subject
        subject = {
            "type": subject_type,
            "url": subject_url,
            "name": scan_result.get("source_url", subject_url)
        }
        
        # 构建verdict
        risk = "safe" if overall_score >= 80 else "medium" if overall_score >= 60 else "high" if overall_score >= 40 else "critical"
        verdict = {
            "score": overall_score,
            "level": "gold" if overall_score >= 85 else "silver" if overall_score >= 70 else "bronze" if overall_score >= 55 else "none",
            "risk": risk,
            "no_spawn_guarantee": True,
            "offline_scan": True
        }
        
        # 构建coverage
        coverage = {
            "owasp_mcp_top10": "10/10",
            "owasp_asi_top10": "10/10",
            "dimensions": ["security", "permissions", "data_handling", "supply_chain", "reliability"]
        }
        
        # 构建attestation
        attestation = {
            "method": "automated",
            "scan_id": scan_result.get("scan_id"),
            "findings_count": summary.get("findings_total", 0),
            "severity_counts": severity_counts,
            "evidence_count": len(scan_result.get("findings", [])),
            "generated_at": datetime.now(TZ).isoformat()
        }
        
        # 生成attestation
        result, error = generate_attestation(subject, verdict, coverage, attestation)
        if error:
            return None, error
        
        return result, None
        
    except Exception as e:
        return None, f"Failed to create attestation from scan: {str(e)}"


def _digest_envelope(envelope, max_findings=3):
    """把一个 aishield-trust/v1 信封压成摘要。

    信封里没有 findings 明细（它描述的是订阅状态，不是一次扫描），所以
    severity 分布为空、top 为空 —— 这是诚实的「没有更多信息」，而不是
    把缺失当成零。
    """
    verdict = (envelope or {}).get("verdict", {}) or {}
    subject = (envelope or {}).get("subject", {}) or {}
    score = verdict.get("score")
    counts = {}
    _floor, worst = _risk_floor(counts)
    core = {
        "subject": subject.get("url") or subject.get("name"),
        "score": score,
        "risk": verdict.get("risk") or _risk_from_score(score, counts),
        "worst_severity": worst,
        "level": verdict.get("level"),
        "severity_counts": {},
        "findings_total": None,
        "top": [],
    }
    out = {
        "schema": DIGEST_SCHEMA,
        "ready": score is not None,
        "issuer": ISSUER_URL,
        "no_spawn_guarantee": True,
        "offline_scan": True,
    }
    out.update(core)
    out["fingerprint"] = _digest_fingerprint(core)
    return out


def _digest_scan_result(result, max_findings=3, subject=None, include_collector=False):
    """把一次扫描结果压成摘要（走 collector 的同一套投影，不另造轮子）。

    默认**不**嵌套 collector 的 digest —— 两者字段高度重叠，嵌进去等于把同一份
    信息发两遍，正好背离做这个摘要的初衷。需要完整投影时用 include_collector。
    """
    from collector.aishield_collector import summarize, fingerprint

    summary = (result or {}).get("summary", {}) or {}
    findings = list((result or {}).get("findings", []) or [])

    def _sev_key(f):
        try:
            return _SEVERITY_ORDER.index(str(f.get("severity", "info")).lower())
        except ValueError:
            return len(_SEVERITY_ORDER)

    findings.sort(key=_sev_key)
    top = []
    for f in findings[: max(0, int(max_findings))]:
        top.append(
            {
                "severity": f.get("severity"),
                "type": f.get("type"),
                "owasp": f.get("owasp_category"),
            }
        )
    score = summary.get("config_score")
    if score is None:
        score = summary.get("overall_score")
    counts = summary.get("severity_counts", {}) or {}
    _floor, worst = _risk_floor(counts)
    out = {
        "schema": DIGEST_SCHEMA,
        "ready": True,
        "issuer": ISSUER_URL,
        "no_spawn_guarantee": True,
        "offline_scan": True,
        "subject": subject,
        "score": score,
        # risk 取「分数档」与「最严重 finding」中更重的一方：84 分配置带着 2 条
        # high 时不能报 safe，否则摘要自相矛盾且给出假安心。
        "risk": _risk_from_score(score, counts),
        "worst_severity": worst,
        "severity_counts": counts,
        "findings_total": summary.get("findings_total"),
        "servers_found": summary.get("servers_found"),
        "top": top,
        # collector 的指纹覆盖 summary+规范化 findings，同一份配置恒定不变，
        # 调用方据此判断「我缓存的那份还有效吗」。
        "fingerprint": fingerprint(result or {}),
    }
    if include_collector:
        out["collector_digest"] = summarize(result or {}, max_findings=max_findings)
    return out


def trust_digest(data=None, src=None, max_findings=3, include_collector=False):
    """紧凑信任摘要的统一入口。返回 (payload, status)。"""
    data = data or {}

    if data.get("configs"):
        from scanner.client_discovery import scan_client_configs

        try:
            result = scan_client_configs(data["configs"])
        except Exception as e:
            return {"error": "scan failed: %s" % e}, 400
        return _digest_scan_result(
            result, max_findings=max_findings, include_collector=include_collector
        ), 200

    if data.get("scan_result") or data.get("scan_report"):
        result = data.get("scan_result") or data.get("scan_report")
        return _digest_scan_result(
            result,
            max_findings=max_findings,
            subject=data.get("subject"),
            include_collector=include_collector,
        ), 200

    target = src or data.get("src") or data.get("source_url") or data.get("tool")
    if target:
        envelope = _verify_envelope(target, data.get("type"))
        return _digest_envelope(envelope, max_findings=max_findings), 200

    return {
        "error": "one of configs / scan_result / src required",
        "hint": "POST {configs:{path:content}} 或 {scan_result:{...}}，或 GET ?src=<repo url>",
        "schema": DIGEST_SCHEMA,
    }, 400


# ══════════════════════════════════════════════
#  HTTP 路由 (供 server.py 与独立 server 共用)
# ══════════════════════════════════════════════
def handle_get(path, query=""):
    """返回 (payload_dict, status_code)。"""
    q = parse_qs(query) if query else {}

    # Trust Attestation 端点
    if path == "/api/v1/attestations":
        # 列出attestations
        subject = q.get("subject", [None])[0]
        issuer = q.get("issuer", [None])[0]
        status = q.get("status", [None])[0]
        result = list_attestations(subject=subject, issuer=issuer, status=status)
        return result, 200

    m = __import__("re").match(r"^/api/v1/attestations/([^/]+)$", path)
    if m:
        # 获取单个attestation
        attestation_id = m.group(1)
        online = q.get("online", ["false"])[0].lower() == "true"
        result, error = verify_attestation(attestation_id, online_verification=online)
        if error:
            return {"error": error}, 404
        return result, 200

    if path == "/api/v1/attestations/schema":
        # 获取attestation schema
        schema = _load_attestation_schema()
        if schema:
            return schema, 200
        return {"error": "Schema not found"}, 404

    # 原有的Trust API端点
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

    if path == "/api/v1/trust/digest" or path == "/api/v1/digest":
        src = (q.get("src", [None])[0] or q.get("source_url", [None])[0]
               or q.get("tool", [None])[0])
        try:
            k = int(q.get("max_findings", [3])[0])
        except (TypeError, ValueError):
            k = 3
        return trust_digest(src=src, max_findings=k)

    if path == "/api/v1/trust" or path == "/api/v1/trust/verify":
        src = (q.get("src", [None])[0] or q.get("source_url", [None])[0]
               or q.get("tool", [None])[0])
        if not src:
            return {"error": "src (or source_url/tool) query param required"}, 400
        subject_type = q.get("type", [None])[0]
        return _verify_envelope(src, subject_type), 200

    if path == "/api/v1/trust/score" or path == "/api/v1/trust/cert":
        return {"error": "agent_id / cert_id required in path"}, 400

    # ── FTM（Program D）：W3C VC 2.0 + CT 式透明日志 ──
    if path == "/api/v1/trust/tlog/sth":
        # 当前签名树头：第三方验证"服务方日志此刻的状态"
        from eco import transparency_log as tlog
        return tlog.sth(), 200

    if path == "/api/v1/trust/tlog/entries":
        from eco import transparency_log as tlog
        try:
            limit = int(q.get("limit", ["20"])[0])
        except (TypeError, ValueError):
            limit = 20
        return {"entries": tlog.get_log().entries(limit=min(limit, 100)),
                "tree_size": tlog.get_log().size(),
                "root_hash": tlog.get_log().root()}, 200

    m = __import__("re").match(r"^/api/v1/trust/tlog/proof/(\d+)$", path)
    if m:
        # 包含证明：leaf_index（0-based）
        from eco import transparency_log as tlog
        return tlog.get_log().inclusion_proof(int(m.group(1))), 200

    if path == "/.well-known/agent-card.json":
        return agent_card(), 200

    return {"error": "unknown trust endpoint", "path": path}, 404


def handle_post(path, data):
    """返回 (payload_dict, status_code)。"""
    data = data or {}

    # ── FTM（Program D）：VC 2.0 签发（签发即进透明日志）──
    if path == "/api/v1/trust/vc2":
        subject_did = data.get("subject_did") or data.get("subject")
        if not subject_did or not isinstance(subject_did, str):
            return {"error": "subject_did required"}, 400
        claims = data.get("claims") or {}
        if not isinstance(claims, dict):
            return {"error": "claims must be an object"}, 400
        try:
            ttl = int(data.get("ttl", 86400))
        except (TypeError, ValueError):
            return {"error": "ttl must be an integer"}, 400
        try:
            from eco import verifiable_identity as vi
            issued = vi.issue_vc2(subject_did, claims, ttl,
                                  data.get("credential_types"))
        except RuntimeError as exc:
            return {"error": str(exc)}, 503
        # 透明签发：凭证摘要（不含 claims 原文）进 CT 式日志
        try:
            from eco import transparency_log as tlog
            tlog.append({
                "type": "vc2_issuance",
                "credential_id": issued["credential_id"],
                "issuer": issued["issuer"],
                "subject": subject_did,
                "expires_at": issued["expires_at"],
            })
        except Exception:
            pass        # 日志故障不阻断签发，但响应里如实标注
            issued["transparency_logged"] = False
        else:
            issued["transparency_logged"] = True
        return issued, 201

    if path == "/api/v1/trust/vc2/verify":
        token = data.get("jwt") or data.get("credential")
        if not token:
            return {"error": "jwt (VC-JWT string) or credential (object with jwt) required"}, 400
        from eco import verifiable_identity as vi
        return vi.verify_vc2(token), 200

    if path == "/api/v1/trust/vc2/revoke":
        credential_id = data.get("credential_id")
        if not credential_id:
            return {"error": "credential_id required"}, 400
        from eco import verifiable_identity as vi
        ok = vi.revoke(credential_id)
        return {"success": ok, "credential_id": credential_id,
                "note": "除销后 verify_vc2 返回 code=revoked"}, 200

    # Trust Attestation 端点
    if path == "/api/v1/attestations":
        # 创建新的attestation
        subject = data.get("subject")
        verdict = data.get("verdict")
        coverage = data.get("coverage")
        attestation = data.get("attestation")
        issuer = data.get("issuer")
        expires_at = data.get("expires_at")
        
        if not subject or not verdict or not coverage or not attestation:
            return {"error": "subject, verdict, coverage, and attestation required"}, 400
        
        result, error = generate_attestation(subject, verdict, coverage, attestation, issuer, expires_at)
        if error:
            return {"error": error}, 400
        
        return {"success": True, "attestation": result}, 201

    if path == "/api/v1/attestations/verify":
        # 验证attestation
        attestation_id = data.get("attestation_id")
        online = data.get("online_verification", True)
        
        if not attestation_id:
            return {"error": "attestation_id required"}, 400
        
        result, error = verify_attestation(attestation_id, online_verification=online)
        if error:
            return {"error": error}, 404
        
        return {"success": True, "attestation": result}, 200

    if path == "/api/v1/attestations/from-scan":
        # 从扫描结果创建attestation
        scan_result = data.get("scan_result")
        subject_url = data.get("subject_url")
        subject_type = data.get("subject_type", "tool")
        
        if not scan_result or not subject_url:
            return {"error": "scan_result and subject_url required"}, 400
        
        result, error = create_attestation_from_scan(scan_result, subject_url, subject_type)
        if error:
            return {"error": error}, 400
        
        return {"success": True, "attestation": result}, 201

    if path == "/api/v1/attestations/revoke":
        # 撤销attestation
        attestation_id = data.get("attestation_id")
        reason = data.get("reason")
        
        if not attestation_id:
            return {"error": "attestation_id required"}, 400
        
        success, error = revoke_attestation(attestation_id, reason)
        if error:
            return {"error": error}, 400
        
        return {"success": True, "message": "Attestation revoked"}, 200

    # 原有的Trust API端点
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

    if path == "/api/v1/trust/digest" or path == "/api/v1/digest":
        try:
            k = int(data.get("max_findings", 3))
        except (TypeError, ValueError):
            k = 3
        return trust_digest(data=data, max_findings=k)

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
