# -*- coding: utf-8 -*-
"""
内容溯源 / AI-slop 规避检测（内容可信层）

背景：soundshuman (176★) 代表 agent 文化层——让 agent 产出"去 AI 味"。这是风格层（互补，非竞品）。
但"去 AI 味"被武器化就成了规避检测：恶意 prompt/skill 用编码/角色扮演/翻译伪装绕过内容分类器。
AIShield 卡位（差异化）= 识别"为绕过检测器而设计的 prompt/skill"（内容溯源 / AI-slop 规避检测）。

本模块检测明显的注入/规避意图（高精确率，误报面小）：
  - 越权指令覆盖（ignore previous instructions / 忽略之前指令 / 覆盖系统提示）
  - 越狱角色扮演（DAN / developer mode / jailbreak / 假装你是）
  - 编码绕过（base64 / hex 包裹 "decode and run / execute"）
  - 翻译/混淆绕过（translate then execute / 把下面内容翻译后执行）
  - 反检测自指（do not mention you are an AI / 不要透露你是 AI / avoid detection）

设计原则：纯本地正则，不联网、不 spawn。仅命中高信号越狱/规避短语才报，避免把正常安全文档判毒。
命中后若内容呈"指令性"（system prompt / user: / 你必须为），升级为 high，否则 medium，降低把引用/讨论误判为攻击的噪声。
"""

import re

_OWASP = "MCP06"  # 意图流颠覆 / 上下文提示注入

_PATTERNS = [
    ("jailbreak_override_en", re.compile(
        r'(ignore\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?|'
        r'disregard\s+(your|the)\s+(previous|system|prior)\s+(prompt|instruction)|'
        r'override\s+(your|the)\s+system\s+prompt|forget\s+(everything|all)\s+(above|before))',
        re.I)),
    ("jailbreak_override_zh", re.compile(
        r'(忽略(之前|以上|前面|所有).{0,6}?(指令|提示|设定)|'
        r'覆盖(你的|系统).{0,4}?提示|无视(之前的|系统).{0,4}?(指令|提示))', re.I)),
    ("jailbreak_roleplay", re.compile(
        r'(\bDAN\b|developer\s*mode|jailbreak\s*(mode|prompt)?|'
        r'do\s+anything\s+now|pretend\s+(to\s+be|you\s+are)|假装(你|自己)是|扮演(一个|一名))',
        re.I)),
    ("evasion_encode", re.compile(
        r'(base64\s*[:-]?\s*(decode|解密)|decode\s+(this|the)\s+base64|'
        r'把(下面|以下|这段).{0,6}?(base64|编码|十六进制).{0,6}?(解密|解码|执行)|'
        r'hex\s*[:-]?\s*decode)', re.I)),
    ("evasion_translate", re.compile(
        r'(translate\s+(the\s+following|this)\s+(then\s+)?(and\s+)?(execute|run|respond)|'
        r'(把|将).{0,8}?(翻译|转写).{0,8}?(然后|再).{0,4}?(执行|运行|回答))', re.I)),
    ("evasion_self_ref", re.compile(
        r'(do\s+not\s+(mention|say|reveal|disclose)\s+(that\s+)?(you\s+are|you\'re)\s+an?\s+ai|'
        r'(不要|别|禁止).{0,8}?(透露|说|提|承认).{0,8}?(你是).{0,4}?(ai|人工智能|机器|模型)|'
        r'avoid\s+(being\s+)?detected|绕过.{0,4}?(检测|审查|过滤))', re.I)),
]

_INSTRUCT_CTX = re.compile(
    r'(system\s*prompt|user\s*:|assistant\s*:|instruction|prompt\s*:|'
    r'你(现在|必须|应该|要)|you\s+(must|should|will|are\s+required))', re.I)


def slop_analysis(files):
    """对 {filepath: content} 跑内容溯源 / AI-slop 规避检测。返回 {findings, summary}。"""
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
        matched = set()
        for ftype, pat in _PATTERNS:
            if pat.search(content):
                matched.add(ftype)
        if not matched:
            continue
        instruct_ctx = bool(_INSTRUCT_CTX.search(content))
        sev = "high" if instruct_ctx else "medium"
        add("ai_slop_evasion", sev,
            "检测到疑似提示注入 / 越狱 / 规避检测内容（" + ", ".join(sorted(matched)) +
            "），该 agent 内容可能专为绕过内容分类器而设计，需人工复核意图",
            filepath, content[:120])

    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1

    summary = {
        "slop_findings": len(findings),
        "severity_counts": sev_counts,
        "files_scanned": len(files),
        "note": "内容溯源/AI-slop 规避检测：越狱角色扮演、指令覆盖、编码/翻译绕过、反检测自指",
    }
    return {"findings": findings, "summary": summary}
