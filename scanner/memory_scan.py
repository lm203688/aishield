# -*- coding: utf-8 -*-
"""
记忆 / 持久上下文投毒检测（ASI06 · Memory & Context Poisoning）

背景：OWASP Agentic ASI06；Agent 记忆无标准协议（CSDN 分析指出"三个空白格"之一）。
风险：攻击者让 agent 把恶意指令写入记忆/持久上下文，跨 session 偏置未来推理与工具调用。

检测（纯本地，仅命中强信号指令，避免把正常"记住这个任务"误判）：
- 指示把指令（非数据）写入记忆 / 长期记忆 / 上下文存储。
- 持久化目标："从现在起始终 X" / "把这条加入你的系统提示" / "永久记住"。
- 写入记忆文件路径（.memory / memory.json / context store）。
"""

import re

_OWASP = "MCP03"   # 上下文/工具投毒（持久化指令偏置）

_WRITE_MEM = re.compile(
    r'(save\s+(this|the\s+following|these)\s+(instruction|directive|rule|prompt)\s+to\s+(your\s+)?(memory|long[\- ]?term\s+memory|context)|'
    r'(write|store|persist|remember)\s+(this|the\s+following|these)\s+(instruction|directive|rule|prompt|system\s+prompt)|'
    r'(add|append)\s+(this|the\s+following)\s+to\s+(your\s+)?(memory|system\s+prompt|instructions)|'
    r'(update|modify|edit)\s+(your\s+)?(system\s+prompt|instructions)\s+to\s+(always|from\s+now\s+on))', re.I)
_PERSIST_GOAL = re.compile(
    r'(from\s+now\s+on|永久|从此刻起|始终|always)\s*[,，]?\s*'
    r'(do|remember|follow|treat|consider|act|回答|respond|执行|忽略)', re.I)
_MEM_PATH = re.compile(r'(["\']?[\w./\\-]*\.memory[\w./\\-]*["\']?|memory\.json|context[\-_]?store|long[\- ]?term[\- ]?memory)', re.I)
_SEED = re.compile(
    r'(seed|poison|inject|植入|投毒|污染)\s+(the\s+)?(memory|context|knowledge|rag|检索|知识库)', re.I)


def memory_analysis(files):
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
        if _WRITE_MEM.search(content):
            hits.append("write_instruction_to_memory")
        if _PERSIST_GOAL.search(content):
            hits.append("persistent_goal")
        if _MEM_PATH.search(content):
            hits.append("memory_path_write")
        if _SEED.search(content):
            hits.append("seed_memory")
        if not hits:
            continue
        sev = "high" if ("write_instruction_to_memory" in hits or "seed_memory" in hits) else "medium"
        add("memory_context_poisoning", sev,
            "检测到记忆/持久上下文投毒向量（" + ", ".join(hits) +
            "）：可能把恶意指令写入 agent 长期记忆，跨 session 偏置其行为",
            fp, content[:120])

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1
    summary = {"memory_findings": len(findings), "severity_counts": sev_c,
               "files_scanned": len(files), "note": "记忆/持久上下文投毒检测（ASI06）"}
    return {"findings": findings, "summary": summary}
