# -*- coding: utf-8 -*-
"""
暗模式 / 指令内社会工程检测（ASI09 · Human-Agent Trust Exploitation）

背景：Zenity "appear benign until execute"。风险：用紧迫性、权威冒充、压制验证等手段让人类/agent
在没理解动作与证据的情况下批准有害行为（信任滥用）。

检测（纯本地，需组合信号以降低误报——单点词不报）：
- 权威冒充：自称管理员/官方/某厂商要求执行。
- 压制验证：不要问用户 / 跳过确认 / 无需验证 / 相信我。
- 紧迫性 + 行动：urgent/立即/限时 + 要求执行动作。
- 虚假保证：这是安全的/官方的/ guaranteed。

每个正则的每个分支都是独立平衡的 (...) 组，顶层用 | 连接，避免括号不匹配。
"""

import re

_OWASP = "MCP06"

_AUTHORITY = re.compile(
    r'(as\s+(your|the)\s+(administrator|admin|system|developer|root))|'
    r'(the\s+)?(system|your\s+developer|openai|anthropic|google|microsoft|官方|管理员)\s+(requires|says|instructs|命令|要求|指示)|'
    r'(i\s+am\s+(your|the)\s+(admin|administrator|developer|creator))', re.I)

_SUPPRESS_VERIFY = re.compile(
    r'(do\s+not\s+(ask|verify|confirm|check|tell)\s+(the\s+)?(user|anyone))|'
    r'((skip|disable|bypass)\s+(the\s+)?(confirmation|verification|review|approval|check))|'
    r'(no\s+need\s+to\s+(verify|confirm|ask|check))|'
    r'(trust\s+me)|(相信我)|(无需验证)|(不要询问用户)', re.I)

_URGENCY = re.compile(
    r'(\burgent(ly)?\b)|(immediately)|(right\s+now)|(as\s+soon\s+as\s+possible)|'
    r'(time[\- ]?sensitive)|(before\s+it\'?s\s+too\s+late)|(deadline)|'
    r'(紧急)|(立即)|(马上)|(刻不容缓)|(趁)|(限时)', re.I)

_FAKE_ASSURANCE = re.compile(
    r'(this\s+is\s+(safe|official|trusted|verified|guaranteed))|'
    r'((guaranteed|official|安全|官方|可信|已验证)\s*(and|，|,)?\s*(to\s+)?(proceed|execute|run|do|执行|放心))', re.I)


def dark_pattern_analysis(files):
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
        auth = bool(_AUTHORITY.search(content))
        suppress = bool(_SUPPRESS_VERIFY.search(content))
        urgent = bool(_URGENCY.search(content))
        assure = bool(_FAKE_ASSURANCE.search(content))
        # 需≥2 个暗模式信号组合才报，单点词（如文档里的"立即"）不误报
        score = sum([auth, suppress, urgent, assure])
        if score < 2:
            continue
        tags = []
        if auth:
            tags.append("authority_impersonation")
        if suppress:
            tags.append("suppress_verification")
        if urgent:
            tags.append("urgency")
        if assure:
            tags.append("false_assurance")
        sev = "high" if (auth and suppress) else "medium"
        add("dark_pattern_trust_exploit", sev,
            "检测到指令内社会工程/暗模式（" + ", ".join(tags) +
            "）：利用信任滥用让人类/agent 在缺乏验证下批准行为（ASI09）",
            fp, content[:120])

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1
    summary = {"dark_pattern_findings": len(findings), "severity_counts": sev_c,
               "files_scanned": len(files), "note": "暗模式/指令内社会工程检测（ASI09）"}
    return {"findings": findings, "summary": summary}
