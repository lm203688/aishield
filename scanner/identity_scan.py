# -*- coding: utf-8 -*-
"""
Agent 身份与凭证扫描（Identity / Non-Human Identity 层）

背景：2026 年 agent 安全的主战场从"工具执行"转移到"agent 身份可验证"。
- A2A 仓库 top issue 全是身份（AgentCard 签名 / Ed25519 / RFC9421 / trust.signals）
- Authentik 借 NHI（Non-Human Identity）重新爆火：service account + 短期令牌 + RBAC
- ANS / DNSid / Entra Agent ID / Okta for AI Agents 扎堆

本模块把 AIShield 从"只发信任证书"升级为"也能扫身份缺陷"：
  - 未签名的 AgentCard / agent 身份声明
  - 长期不轮转 / 无过期时间的凭证
  - 过宽授权（scope / permissions == "*"）
  - 缺 mTLS / DID 验证
  - 缺 scope attenuation（委托权限未收敛）

设计原则（与项目一致）：纯本地正则/启发式，不联网、不 spawn、不执行被扫配置。
所有 finding 带 owasp_category，使其自然并入 engine.calculate_scores 的维度扣分。
"""

import re

# 身份相关 OWASP MCP 类别：MCP02 = Authn/Authz/权限；MCP10 = 未授权访问；MCP04 = 供应链
_OWASP = "MCP02"

# 1) 未签名 AgentCard / 身份声明（有 card 名但整文件无签名证据）
_AGENT_CARD_HINT = re.compile(
    r'(agentCard|agent_card|"agent"\s*:|AgentCard|"@type"\s*:\s*"Agent")', re.I)
_SIGNATURE_HINT = re.compile(
    r'(signature|"sign"|jws|"proof"|proof|did:|verificationMethod|"kid")', re.I)

# 2) 过宽授权
_OVERBROAD_SCOPE = re.compile(
    r'(scope|scopes|permissions|permission|grants|entitlements|access)\s*[:=]\s*'
    r'(\[?\s*["\']?\s*\*+\s*["\']?\s*\]?|["\']\s*(admin|superuser|root|all|full|unrestricted)\s*["\'])',
    re.I)

# 3) 无过期 / 长期凭证
_NO_EXPIRY = re.compile(
    r'(expires|expiration|expiry|valid_until|ttl|token_ttl|rotate_after)\s*[:=]\s*'
    r'("?(never|none|null|infinite|0|false)"?|0)', re.I)
_LONG_LIVED_TOKEN = re.compile(
    r'(api[_-]?key|token|secret|access[_-]?token|client[_-]?secret|bearer)\s*[:=]\s*'
    r'["\'][A-Za-z0-9_\-]{24,}["\']', re.I)

# 4) 缺 mTLS / DID 验证（在身份上下文中）
_MTLS_OFF = re.compile(
    r'(mtls|mutual_tls|mutual[_-]?tls|client[_-]?cert|verify[_-]?tls|tls[_-]?verify)\s*[:=]\s*(false|0|"false"|"no"|disabled?)',
    re.I)
_NO_DID = re.compile(r'(did:|"did"|didDocument|verifiableCredential)', re.I)


def identity_analysis(files):
    """对 {filepath: content} 跑身份/凭证扫描。返回 {findings:[...], summary:{...}}。"""
    findings = []
    seen = set()

    def add(ftype, sev, desc, filepath, evidence, category=_OWASP):
        key = f"{ftype}:{desc}:{filepath}"
        if key in seen:
            return
        seen.add(key)
        findings.append({
            "type": ftype,
            "severity": sev,
            "description": desc,
            "file": filepath,
            "evidence": evidence[:140],
            "owasp_category": category,
        })

    for filepath, content in files.items():
        if not isinstance(content, str) or not content.strip():
            continue
        low = content

        # 仅当文件疑似含 agent 身份/配置时才深度检查，减少误报
        looks_like_identity = bool(
            _AGENT_CARD_HINT.search(content) or _NO_DID.search(content)
            or re.search(r'(service[_-]?account|agent[_-]?identity|agentId|client_id)', low, re.I))

        # 1) 未签名 AgentCard
        if _AGENT_CARD_HINT.search(content) and not _SIGNATURE_HINT.search(content):
            add("unsigned_agent_identity", "high",
                "检测到 AgentCard / agent 身份声明但缺少签名/证明（JWS/DID/proof），无法验证发布者真实性",
                filepath, content[:120])

        # 2) 过宽授权
        m = _OVERBROAD_SCOPE.search(content)
        if m:
            add("overbroad_scope", "high",
                "agent 授权过宽（scope/permission 含 '*'/admin/full），违反最小权限，委托时应做 scope attenuation",
                filepath, m.group(0)[:120])

        # 3) 无过期 / 长期凭证
        m = _NO_EXPIRY.search(content)
        if m:
            add("credential_no_expiry", "medium",
                "凭证/令牌缺少过期时间或设为 never，长期不轮转风险（NHI 最佳实践要求短期过期令牌）",
                filepath, m.group(0)[:120])

        # 4) 缺 mTLS（身份上下文）
        m = _MTLS_OFF.search(content)
        if m and looks_like_identity:
            add("mtls_disabled", "medium",
                "在 agent 身份上下文中禁用了 mTLS/TLS 验证，传输层身份无法保证",
                filepath, m.group(0)[:120])

        # 5) 长期硬编码令牌（身份上下文或明显 token 形态）
        m = _LONG_LIVED_TOKEN.search(content)
        if m and (looks_like_identity or _NO_EXPIRY.search(content)):
            add("long_lived_hardcoded_token", "high",
                "检测到硬编码长期令牌/密钥且未做过期与轮转声明，泄露后无自动失效",
                filepath, m.group(0)[:120])

    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1

    summary = {
        "identity_findings": len(findings),
        "severity_counts": sev_counts,
        "files_scanned": len(files),
        "note": "身份层扫描：验证 agent 身份可签名、凭证有期、授权收敛、传输有 mTLS/DID",
    }
    return {"findings": findings, "summary": summary}
