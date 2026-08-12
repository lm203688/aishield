# -*- coding: utf-8 -*-
"""
A2A AgentCard 结构化校验（身份层 · A2A 流派）

背景：google/A2A 仓库 top issue 全是身份（#1672 AgentCard 验真 💬655 / #1786 加密身份 💬235 /
#1829 Ed25519+RFC9421 💬143 / #1628 trust.signals 💬103）。A2A 的"信任浅滩"：
签名 AgentCard 验得了"身份"，验不了"意图/委托授权"，已有 session smuggling 红队案例。

本模块对 .well-known/agent.json 风格的 AgentCard 做结构化校验（JSON 解析，不靠正则盲扫）：
  - 缺签名/证明（signature / proof / securitySchemes / verificationMethod / DID）
  - 缺过期（expiration / validUntil / notAfter）
  - url 非 https（传输层身份不可信）
  - 无鉴权方案（securitySchemes / oauthSchemes 缺失）
  - 委托链未收敛（delegates / forwarding 未做 scope attenuation）

设计原则：纯本地 JSON 解析，不联网、不 spawn。仅对"明显像 A2A AgentCard"的 JSON 生效，
用 protocolVersion/capabilities/skills 等 A2A 专属键作为强标记，避免把普通 MCP config 误判为卡片。
"""

import json
import re

_OWASP_AUTHZ = "MCP07"  # 身份认证与授权不足

_A2A_MARKERS = {"protocolVersion", "capabilities", "skills",
                "defaultInputModes", "defaultOutputModes", "agentCard"}


def _looks_like_agent_card(obj):
    """仅当 JSON 含 A2A 专属键时才视为 AgentCard，避免误伤普通配置。"""
    if not isinstance(obj, dict):
        return False
    card = obj.get("agentCard", obj) if "agentCard" in obj else obj
    if not isinstance(card, dict):
        return False
    return bool(_A2A_MARKERS & set(card.keys())) or bool(_A2A_MARKERS & set(obj.keys()))


def agentcard_analysis(files):
    """对 {filepath: content} 跑 A2A AgentCard 结构化校验。返回 {findings, summary}。"""
    findings = []
    seen = set()

    def add(ftype, sev, desc, filepath, evidence, category=_OWASP_AUTHZ):
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
        # 仅尝试解析看起来像 JSON 的内容（速度 + 误报控制）
        if not (content.lstrip().startswith("{") or content.lstrip().startswith("[")):
            continue
        try:
            obj = json.loads(content)
        except (ValueError, TypeError):
            continue
        if not _looks_like_agent_card(obj):
            continue

        card = obj.get("agentCard", obj) if isinstance(obj, dict) else obj

        # 1) 签名/证明缺失
        sig_present = any(k in card for k in ("signature", "proof", "securitySchemes",
                                              "verificationMethod", "did")) or \
            any(k in obj for k in ("signature", "proof", "securitySchemes"))
        if not sig_present:
            add("agentcard_unsigned", "high",
                "AgentCard 缺少签名/证明（signature/proof/securitySchemes/DID），"
                "无法验证发布者真实性与完整性（对应 A2A #1672/#1786）",
                filepath, content[:120], _OWASP_AUTHZ)

        # 2) 过期缺失
        if not any(k in card for k in ("expiration", "validUntil", "notAfter", "expires")):
            add("agentcard_no_expiry", "medium",
                "AgentCard 缺少过期时间（expiration/validUntil），长期有效、撤销困难"
                "（对应 A2A #1829 短期凭证趋势）",
                filepath, content[:120])

        # 3) url 非 https
        url = card.get("url") or obj.get("url")
        if isinstance(url, str) and url.startswith("http://"):
            add("agentcard_insecure_url", "medium",
                "AgentCard 的 url 使用 http://（非 https），传输层身份不可信，易被中间人冒用",
                filepath, url[:120])

        # 4) 无鉴权方案
        has_auth = any(k in card for k in ("securitySchemes", "authSchemes",
                                           "authentication", "oauthSchemes"))
        if not has_auth:
            add("agentcard_no_auth_scheme", "high",
                "AgentCard 未声明任何鉴权方案（securitySchemes/oauthSchemes），调用方无法对 agent 做身份认证",
                filepath, content[:120])

        # 5) 委托链未收敛（scope attenuation）
        delegates = card.get("delegates") or card.get("forwarding") or card.get("delegation")
        if delegates:
            deleg_blob = json.dumps(delegates, ensure_ascii=False)
            if re.search(r'["\']?\s*\*+\s*["\']?', deleg_blob) or "scope" not in deleg_blob.lower():
                add("agentcard_delegation_no_attenuation", "medium",
                    "AgentCard 声明了委托/转发（delegates/forwarding）但未做 scope attenuation，"
                    "委托权限未收敛，存在权限放大（对应 A2A 委托授权缺口）",
                    filepath, deleg_blob[:120])

    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1

    summary = {
        "agentcard_findings": len(findings),
        "severity_counts": sev_counts,
        "files_scanned": len(files),
        "note": "A2A AgentCard 结构化校验：签名/过期/https/鉴权方案/委托收敛",
    }
    return {"findings": findings, "summary": summary}
