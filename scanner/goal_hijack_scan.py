# -*- coding: utf-8 -*-
"""
目标劫持检测（ASI01 · Agent Goal Hijack）— slop_scan 之外的目标级向量

背景：ASI01 目标劫持比传统提示注入更危险——把恶意指令"内化"为 agent 长期目标，而非一次回答。
风险：外部内容（网页/邮件/文档）被当作指令执行；目标被静默替换。

检测（纯本地，强信号）：
- 外部内容即指令：读到网页/邮件/文档时"执行其中任何指令"。
- 目标替换：忽略用户请求、改为 X；"你的真实目标是"；"新目标"。
- 持久化目标：把某指令设为首要指令/永久目标。
"""

import re

_OWASP = "MCP06"   # 上下文/提示注入（目标级）

_EXT_AS_INSTRUCTION = re.compile(
    r'((treat\s+(any|all)\s+(text|content|webpage|page|email|document|message|instruction)\s+'
    r'(you\s+encounter|you\s+(read|see|process)|found|encountered)\s+as\s+(a\s+)?(command|instruction|prompt))|'
    r'((execute|follow|obey|act\s+on)\s+(any|all|every)\s+(instruction|command|directive)\s+'
    r'(you\s+(find|see|encounter|read)|contained\s+in|in\s+(the\s+)?(webpage|page|email|document|message)))|'
    r'((when\s+you\s+(read|browse|open|visit)\s+[^\n,]{0,40}?,?\s*(execute|follow|obey|run)\s+(any|the\s+)?(instruction|command))))', re.I)

_GOAL_SUBSTITUTE = re.compile(
    r'((ignore\s+(the\s+)?user\'?s?\s+(request|original\s+request|task|goal))|'
    r'((your|the)\s+(real|true|actual|new|primary)\s+(goal|objective|purpose|directive)\s+is)|'
    r'((replace|override|change)\s+(the\s+)?(user\'?s?\s+)?(goal|objective|intent|instruction)\s+(with|to))|'
    r'(from\s+now\s+on,?\s+your\s+(goal|objective|priority)\s+is))', re.I)

_PERSIST_GOAL_HIJACK = re.compile(
    r'((make\s+this\s+(your\s+)?(primary|main|permanent|top)\s+(directive|goal|instruction|objective))|'
    r'((set\s+(this|the\s+following)\s+as\s+(your\s+)?(primary|permanent|default)\s+(goal|directive|instruction))))', re.I)


def goal_hijack_analysis(files):
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
        if _EXT_AS_INSTRUCTION.search(content):
            hits.append("external_content_as_instruction")
        if _GOAL_SUBSTITUTE.search(content):
            hits.append("goal_substitution")
        if _PERSIST_GOAL_HIJACK.search(content):
            hits.append("persistent_goal_hijack")
        if not hits:
            continue
        sev = "high" if ("goal_substitution" in hits or "persistent_goal_hijack" in hits) else "medium"
        add("agent_goal_hijack", sev,
            "下有目标劫持向量（" + ", ".join(hits) +
            "）：agent 目标可能被外部内容或指令静默替换/内化，偏离用户意图",
            fp, content[:120])

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1
    summary = {"goal_hijack_findings": len(findings), "severity_counts": sev_c,
               "files_scanned": len(files), "note": "目标劫持检测（ASI01）"}
    return {"findings": findings, "summary": summary}
