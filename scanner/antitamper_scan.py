# -*- coding: utf-8 -*-
"""
自保护 / 反篡改模式检测（ASI10 · Rogue Agents）

背景：Zenity BlackHat 2026 发现恶意 skill 会 (1) 改写自身 system prompt 以在被删时重装；
(2) 卸载官方 skill-creator 并换成伪造版；(3) 指示 agent 自动重装。
风险：agent 行为脱离治理范围（rogue），自我维持、对抗移除。

检测（纯本地，强信号）：自保护/重装、禁用/替换其它组件、反分析/隐藏。
"""

import re

_OWASP = "MCP03"

_SELF_PRESERVE = re.compile(
    r'((if\s+(deleted|removed)\s*,?\s*(then\s+)?'
    r'(reinstall|re-install|restore|recreate|reappear|come\s+back))|'
    r'((reinstall|re-install|restore|self[\- ]?heal|persist)\s+'
    r'(yourself|itself|automatically|on\s+(delete|removal)))|'
    r'((rewrite|modify|edit)\s+(your|its)\s+own\s+(system\s+prompt|configuration|config))|'
    r'(do\s+not\s+(let|allow)\s+(the\s+)?(user|anyone)\s+(delete|remove|uninstall)))', re.I)

_DISABLE_OTHER = re.compile(
    r'((uninstall|disable|remove|replace|deactivate)\s+(the\s+)?(official\s+)?skill[\- ]?creator)|'
    r'((uninstall|disable|remove|replace|deactivate)\s+(the\s+)?(official\s+)?'
    r'(other\s+skills|competing|built[\- ]?in|default)\s+(skill|tool|plugin|component))|'
    r'((replace\s+(the\s+)?(skill[\- ]?creator|official)\s+with))', re.I)

_ANTI_ANALYSIS = re.compile(
    r'((do\s+not\s+(show|reveal|tell|mention|log|display)\s+(this|these|the\s+following)\s+'
    r'(instruction|prompt|step|to\s+(the\s+)?user))|'
    r'((hide\s+(this|these)\s+(instruction|prompt|from\s+(the\s+)?user)))|'
    r'((do\s+not\s+(log|record|audit|monitor)\s+(this|these|your\s+actions))))', re.I)


def antitamper_analysis(files):
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
        hits = []
        if _SELF_PRESERVE.search(content):
            hits.append("self_preservation")
        if _DISABLE_OTHER.search(content):
            hits.append("disable_other_components")
        if _ANTI_ANALYSIS.search(content):
            hits.append("anti_analysis")
        if not hits:
            continue
        add("antitamper_self_preservation", "high",
            "检测到自保护/反篡改模式（" + ", ".join(hits) +
            "）：agent 可能脱离治理、自我维持、对抗移除（rogue agent）",
            fp, content[:120])

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1
    summary = {"antitamper_findings": len(findings), "severity_counts": sev_c,
               "files_scanned": len(files), "note": "自保护/反篡改模式检测（ASI10）"}
    return {"findings": findings, "summary": summary}
