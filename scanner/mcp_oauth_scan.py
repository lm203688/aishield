# -*- coding: utf-8 -*-
"""
MCP OAuth 姿态检查（ASI03 身份权限 · OAuth 专项）

背景：CVE-2026-32211（Azure MCP 缺认证 CVSS 9.1）；OAuth 2.1 采用率参差；RFC 9207 token
issuer 校验缺失导致 mix-up 攻击；长寿命 token 扩大泄露半径。
风险：agent 以无认证/弱认证/长寿命 token 访问 MCP server。

检测（纯本地，仅对 MCP server config）：
- 远程 server（url https）无认证（缺 authorization/oauth/token/apiKey/bearer）。
- 声明 oauth 但缺 issuer/token_endpoint（RFC 9207 issuer 校验缺失）。
- 长寿命 token：expires_in 极大（>3600）或 refresh_token 无轮换提示。
"""

import re
import json

_OWASP = "MCP02"

_HAS_URL = re.compile(r'"url"\s*:\s*"https?://', re.I)
_HAS_AUTH = re.compile(
    r'("?(authorization|oauth|oauth2|token|apikey|api_key|apiKey|bearer|'
    r'authorization_scheme|auth)"?\s*[:=])', re.I)
_HAS_ISSUER = re.compile(r'("?(issuer|token_endpoint|tokenEndpoint|authorization_server)"?\s*[:=])', re.I)
_LONG_TOKEN = re.compile(r'("?expires_in"?\s*[:=]\s*\d{5,})', re.I)
_REFRESH_NO_ROTATE = re.compile(
    r'("?refresh_token"?\s*[:=])', re.I)
# GPT Action 清单：认证通过顶层/action 级 "auth" 字段声明，无 auth = 合法公开行为
_IS_GPT_MANIFEST = re.compile(r'"actions"\s*:\s*\[', re.I)


def _looks_like_gpt_manifest(content):
    """粗略判定 JSON 是否为 GPT Action 清单（顶层 actions 数组）。"""
    if not _IS_GPT_MANIFEST.search(content):
        return False
    try:
        obj = json.loads(content)
    except Exception:
        return _IS_GPT_MANIFEST.search(content) is not None
    return isinstance(obj, dict) and isinstance(obj.get("actions"), list)


def mcp_oauth_analysis(files):
    findings = []
    seen = set()

    def add(ftype, sev, desc, filepath, evidence, category=_OWASP):
        key = f"{ftype}:{desc}:{filepath}"
        if key in seen:
            return
        seen.add(key)
        findings.append({"type": ftype, "severity": sev, "description": desc,
                         "file": filepath, "evidence": evidence[:140], "owasp_category": category})

    for fp, content in files.items():
        if not isinstance(content, str) or not content.strip():
            continue
        is_server = ("<mcp-config>" in fp or fp.endswith(".json")
                     or fp.endswith(".yaml") or fp.endswith(".yml"))
        if not is_server:
            continue
        if not _HAS_URL.search(content):
            continue  # 仅检查远程 server
        if _looks_like_gpt_manifest(content):
            # GPT Action 清单：无 auth 字段即公开 action（合法模式），不报 mcp_no_auth。
            # 仍对显式存在的 oauth/refresh/长效 token 块做专项检查。
            if _HAS_AUTH.search(content) and re.search(r'oauth', content, re.I) and not _HAS_ISSUER.search(content):
                add("mcp_oauth_no_issuer", "medium",
                    "GPT Action 声明 OAuth 但缺 issuer/token_endpoint，缺 RFC 9207 token issuer 校验，存在 mix-up 攻击风险",
                    fp, content[:120])
            if _LONG_TOKEN.search(content):
                add("mcp_long_lived_token", "medium",
                    "token expires_in 极大（>3600s），长寿命 token 扩大泄露半径，建议短寿命 + DPoP/CAEP",
                    fp, content[:120])
            elif _REFRESH_NO_ROTATE.search(content) and not re.search(r'(rotate|rotation|revoke)', content, re.I):
                add("mcp_refresh_no_rotation", "low",
                    "声明 refresh_token 但未见轮换/撤销机制，长寿命凭证风险",
                    fp, content[:120])
            continue
        if not _HAS_AUTH.search(content):
            add("mcp_no_auth", "high",
                "远程 MCP server 配置无认证字段（authorization/oauth/token/apiKey），端点可被未授权调用（CVE-2026-32211 类）",
                fp, content[:120])
        elif _HAS_AUTH.search(content) and re.search(r'oauth', content, re.I) and not _HAS_ISSUER.search(content):
            add("mcp_oauth_no_issuer", "medium",
                "MCP server 声明 OAuth 但缺 issuer/token_endpoint，缺 RFC 9207 token issuer 校验，存在 mix-up 攻击风险",
                fp, content[:120])
        if _LONG_TOKEN.search(content):
            add("mcp_long_lived_token", "medium",
                "token expires_in 极大（>3600s），长寿命 token 扩大泄露半径，建议短寿命 + DPoP/CAEP",
                fp, content[:120])
        elif _REFRESH_NO_ROTATE.search(content) and not re.search(r'(rotate|rotation|revoke)', content, re.I):
            add("mcp_refresh_no_rotation", "low",
                "声明 refresh_token 但未见轮换/撤销机制，长寿命凭证风险",
                fp, content[:120])

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1
    summary = {"mcp_oauth_findings": len(findings), "severity_counts": sev_c,
               "files_scanned": len(files), "note": "MCP OAuth 姿态检查（ASI03）"}
    return {"findings": findings, "summary": summary}
