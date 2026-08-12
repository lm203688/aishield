# -*- coding: utf-8 -*-
"""
Authentik / NHI service-account 导出扫描（身份层 · Authentik 流派）

背景：Authentik (goauthentik/authentik, 22k★) 2026 因 NHI（Non-Human Identity）重新爆火。
官方《A note to AI agents about authentik》建议把 agent 当 service account，
发短期过期令牌 + RBAC，令牌到期自动轮换。

本模块扫描 Authentik 风格的 service-account / provider 导出（JSON / YAML / .env），
识别 NHI 最佳实践缺口：
  - skip_authorization: true（provider 跳过授权/同意，任何 agent 可静默拿令牌）
  - token_ttl: 0 / never（令牌永不过期，泄露无自动失效）
  - access_type: offline 但无过期（长期刷新令牌）
  - 硬编码 client_secret / api_key 且无轮转声明
  - scope 过宽（"*" / admin / full）—— 委托时应 scope attenuation

设计原则（与项目一致）：纯本地正则/启发式，不联网、不 spawn、不执行被扫配置。
仅在 Authentik/NHI 上下文（命中 service_account / client_secret / token_ttl 等标记）才深度检测，降误报。
"""

import re

_OWASP = "MCP07"  # 身份认证与授权不足

_AUTHENTIK_HINT = re.compile(
    r'(authentik|service[_-]?account|client[_-]?secret|client_id|skip_authorization|'
    r'token_ttl|application\s*[:=]|provider\s*[:=])', re.I)

# 1) skip_authorization（Authentik provider 跳同意）
_SKIP_AUTHZ = re.compile(
    r'(skip_authorization|skip_authorization_flow|skip_consent)\s*[:=]\s*(true|1|"true"|"yes")', re.I)

# 2) token 永不过期
_TOKEN_NO_EXPIRY = re.compile(
    r'(token_ttl|token_validity|expires|expiration|expiry|ttl|rotate_after)\s*[:=]\s*'
    r'("?(?:never|none|null|infinite|0|false)"?|0)', re.I)

# 3) offline 刷新令牌但无过期
_OFFLINE_NO_EXPIRY = re.compile(r'access_type\s*[:=]\s*["\']?offline', re.I)

# 4) 硬编码 client_secret / api_key
_HARDCODED_SECRET = re.compile(
    r'(client_secret|api[_-]?key|access[_-]?token|bearer)\s*[:=]\s*["\'][A-Za-z0-9_\-]{24,}["\']', re.I)

# 5) 过宽 scope（Authentik 上下文）
_OVERBROAD_SCOPE = re.compile(
    r'(scope|scopes|permissions|entitlements)\s*[:=]\s*'
    r'(\[?\s*["\']?\s*\*+\s*["\']?\s*\]?|["\']\s*(?:admin|superuser|root|all|full|unrestricted)\s*["\'])',
    re.I)


def authentik_analysis(files):
    """对 {filepath: content} 跑 Authentik/NHI service-account 扫描。返回 {findings, summary}。"""
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
        if not _AUTHENTIK_HINT.search(content):
            continue  # 仅在 Authentik/NHI 上下文检测，降低误报

        # 1) skip_authorization
        m = _SKIP_AUTHZ.search(content)
        if m:
            add("authentik_skip_authorization", "high",
                "Authentik provider 设置了 skip_authorization/skip_consent=true，"
                "agent 可在无用户/代理同意下静默获取令牌，违背最小授权",
                filepath, m.group(0)[:120])

        # 2) token 永不过期
        m = _TOKEN_NO_EXPIRY.search(content)
        if m:
            add("nh_i_token_no_expiry", "high",
                "NHI service-account 令牌缺少过期时间或设为 never/0（token_ttl/expires），"
                "泄露后无自动失效，违反 Authentik NHI 短期令牌最佳实践",
                filepath, m.group(0)[:120])

        # 3) offline 刷新令牌但无过期
        if _OFFLINE_NO_EXPIRY.search(content) and not re.search(
                r'(token_ttl|expires|expiration|expiry|ttl|rotate_after)\s*[:=]', content):
            add("nh_i_offline_token_no_expiry", "medium",
                "service-account 使用 access_type=offline（长期刷新令牌）但未声明过期/轮转，刷新令牌长期有效",
                filepath, content[:120])

        # 4) 硬编码密钥
        m = _HARDCODED_SECRET.search(content)
        if m:
            add("nh_i_hardcoded_secret", "high",
                "检测到硬编码 client_secret/api_key 且未做过期与轮转声明，泄露即长期可用",
                filepath, m.group(0)[:120])

        # 5) 过宽 scope
        m = _OVERBROAD_SCOPE.search(content)
        if m:
            add("nh_i_overbroad_scope", "high",
                "agent service-account 授权过宽（scope/permissions 含 '*'/admin/full），委托时应做 scope attenuation",
                filepath, m.group(0)[:120])

    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1

    summary = {
        "authentik_findings": len(findings),
        "severity_counts": sev_counts,
        "files_scanned": len(files),
        "note": "Authentik/NHI 身份层扫描：service-account 令牌短期过期、skip_authorization、scope 收敛",
    }
    return {"findings": findings, "summary": summary}
