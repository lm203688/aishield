# -*- coding: utf-8 -*-
"""
RAG 语料 / 持久化记忆内容 投毒扫描（ASI06 · 内容级）

背景与边界
----------
`agent_memory_scan.py` 已覆盖 **代码级** ASI06：它静态分析源码里对
Hermes / Hindsight / Mem0 / Zep … 等记忆框架的调用，检测跨 session 累积污染、
检索注入、持久化指令四类**代码模式**。

但 agent 生态还有一面它够不到 —— **RAG 语料本身 / 持久化记忆的内容**。
当一条被注入的"指令"已经躺在知识库文档、vector store 导出、memory dump、
或个人知识库 markdown 里，它不再表现为"代码调用"，而是表现为"被检索后
拼进 prompt 的普通文本"。这一面的投毒检测，本库此前是空白。

本模块就补这一面：对 {filepath: content} 里的**文档正文**做内容级扫描，
识别嵌入在语料中的指令注入 / 角色劫持 / 外传诱导 / 跨文档互证加固 / 编码载荷。

判据纪律（与 agent_memory_scan 同源，零误报优先）
------------------------------------------------
* 纯静态、零依赖、只读；不 spawn 任何命令、不联网。
* 命中必须是**强信号**（祈使式指令 + 角色/外传/执行语义共现），而非
  普通文档里的 "note:" / "please see" 之类良性表述。
* 良性侧抑制：安全/教育类文档解释"什么是 prompt injection"时通常带
  "example / for demonstration / this is a test" 等元标记，命中邻近这些
  标记的不报（避免把教学样例当真实投毒）。
* severity：critical（可直接改写 agent 行为 / 外传）/ high（架构性诱导
  需人工确认）。

对齐
----
* OWASP Agentic AI Top 10 (2025): ASI06 Memory & Context Poisoning
* MITRE ATLAS: T0051 LLM Prompt Injection（间接注入残留场景）
* 与 agent_memory_scan 的边界：本模块扫描**内容文本**；agent_memory_scan
  扫描**调用代码**。二者互补，不重叠。
"""

import re

_OWASP = "ASI06"  # Memory & Context Poisoning

# ── 0. 良性侧抑制（文档是"讲解/示例"而非"投毒"）──────────────────────
# 命中行若同时带这些**教学框架**元标记，大概率是教学样例，抑制告警。
# 关键：必须用整词教学框架（for example / this is an example / example of /
# as an example / for demonstration / role-play / prompt injection ...），
# 绝不能用裸 "example" 子串 —— 攻击域名 evil-example.com 里的 "example"
# 会被裸子串误判为教学标记，把真实外传样本静默抑制（已实测踩坑）。
_BENIGN_META = re.compile(
    r'(for\s+example|an?\s+example|this\s+is\s+(?:a|an)\s+(?:test|sample|demo|example)|'
    r'as\s+an?\s+example|example\s+of|'
    r'for\s+demonstrat|this\s+is\s+(?:a|an)\s+demonstrat|'
    r'in\s+this\s+(?:example|tutorial|guide)|as\s+an?\s+illustrat|'
    r'pretend\s+(?:this|the\s+user)|role[- ]?play|'
    r'prompt[- ]?inject)', re.I)

# ── 1. 嵌入指令：要求忽略既有指令 / 覆盖上下文 ───────────────────────────
_EMBEDDED_DIRECTIVE = [
    # ignore / disregard / forget 既有指令
    re.compile(
        r'(?:ignore|disregard|forget|override|skip|neglect)\s+'
        r'(?:all\s+|any\s+|the\s+|your\s+)?'
        r'(?:previous|prior|above|earlier|preceding|existing|prior)\s+'
        r'(?:instructions?|prompts?|context|messages?|system\s*(?:prompt|message))',
        re.I),
    # 直接给"系统"下指令的伪装
    re.compile(
        r'(?:^|\n)\s*(?:system|assistant|model|ai)\s*:\s*'
        r'(?:you\s+(?:must|should|are|will|need)|ignore|from\s+now|'
        r'always|never|disregard|act\s+as|pretend)', re.I),
]

# ── 2. 角色 / 身份劫持 ─────────────────────────────────────────────────
_PERSONA_HIJACK = [
    re.compile(
        r'(?:you\s+are\s+now|you\'?re\s+now|from\s+now\s+on,?\s+you|'
        r'your\s+new\s+(?:name|role|identity|purpose|persona|objective|goal|'
        r'function|directive)\s+(?:is|will\s+be|should\s+be|becomes)|'
        r'your\s+(?:real|true|actual|secret)\s+(?:identity|purpose|goal|'
        r'objective|name)\s+(?:is|should\s+be))', re.I),
    re.compile(
        r'(?:pretend\s+to\s+be|act\s+as\s+if\s+you|'
        r'role[- ]?play\s+(?:as\s+)?(?:a|an|the)|'
        r'your\s+persona\s+(?:is|changes?\s+to)|'
        r'adopt\s+the\s+(?:role|identity|persona)\s+of)', re.I),
]

# ── 3. 外传诱导：把密钥/上下文发到外部 ──────────────────────────────────
# 设计：verb（send/exfiltrate/...）→ 秘密词（api_key/secret/...）→
# 目的地（https://.../外部），三段用有限窗口桥接，允许 "and the X" 连词。
# 窗口受限（各 100 字符、可跨换行）以压制"文档两节各提一次"的巧合误报。
# 动词只用强信号：return/include/print/echo/leak/dump 在普通文档里太常见
# （"return the value" / "leaking data" 描述风险），会成片误报自家文档，故剔除。
_EXFILTRATION = [
    re.compile(
        r'(?:send|exfiltrate|forward|transmit|post|upload|reveal|disclose)\b'
        r'[\s\S]{0,100}?'
        r'(?:api[-_]?key|secret|password|passwd|token|credential|'
        r'private[-_]?key|system[-_]?prompt|env(?:ironment)?\s*vars?|'
        r'\.env|config(?:uration)?|cookies?|session[-_]?token)'
        r'[\s\S]{0,100}?'
        r'(?:to|via|over|at|into|toward|through|back\s+to)\s+'
        r'(?:https?://|http|ftp|the\s+attacker|'
        r'[a-z0-9.-]+\.(?:com|net|io|org|xyz|ru|cn)|'
        r'(?:me|us|them|external|remote|third[- ]?party))', re.I),
    re.compile(
        r'(?:exfiltrate|send\s+outside|escape\s+the\s+(?:sandbox|context)|'
        r'bypass\s+(?:the\s+)?(?:safety|security|guardrail)|'
        r'disable\s+(?:the\s+)?(?:safety|security|filter|guardrail|moderation))',
        re.I),
]

# ── 4. 紧急性伪装：IMPORTANT/URGENT 后跟指令 ───────────────────────────
_URGENT_DIRECTIVE = re.compile(
    r'(?:IMPORTANT|URGENT|CRITICAL|MANDATORY|NOTE\s*\(required\))\s*'
    r'[::\-\u2013\u2014]?\s*'
    r'(?:you\s+(?:must|should|are|will|need)|ignore|disregard|from\s+now|'
    r'always|never|do\s+not|stop|reveal|send|exfiltrate|act\s+as|pretend)',
    re.I)

# ── 5. 跨文档互证加固：引用另一文档来"证明"自己这条指令 ─────────────────
_CROSS_REF_REINFORCE = re.compile(
    r'(?:as\s+(?:stated|mentioned|noted|required|documented|defined|'
    r'specified|confirmed)\s+(?:in|by|within|according\s+to)\s+'
    r'[`"\'`]?[\w./\-]+\.(?:md|txt|json|docx?|pdf|yaml|yml|csv)'
    r'[`"\']?\s*,?\s*(?:you|the\s+agent|the\s+assistant|always|must)\s+'
    r'(?:must|should|will|are|is\s+to|need\s+to))', re.I)

# ── 6. 编码载荷 + 执行上下文：base64/hex 块被要求解码执行 ───────────────
# 仅当"解码/执行"指令与可疑长编码串共现时命中，避免把普通哈希/UUID当载荷。
# 窗口可跨换行（re.S），但受限 120 字符，避免把"文末签名块"误连到开头的指令。
_ENCODED_PAYLOAD = re.compile(
    r'(?:base64\s*decode|decode\s*(?:and|then)?\s*(?:run|execute|eval)|'
    r'eval\s*\(\s*(?:b?[\'"])?[A-Za-z0-9+/]{24,}|'
    r'execute\s+(?:the\s+)?(?:following\s+)?(?:base64|decoded|payload)|'
    r'run\s+(?:this|the\s+following)\s+(?:after\s+)?decod)'
    r'[\s\S]{0,120}?'
    r'([A-Za-z0-9+/]{32,}={0,2})', re.I | re.S)


def _in_code_span(content, start, end):
    """命中短语是否被 markdown 反引号包成行内代码（如 `` `ignore all previous
    instructions` ``）。被引用的攻击短语是文档在**讲解**手法，不是会被 agent
    照着执行的活指令 —— 自家安全 skill 的 SKILL.md 大量这样写，必须抑制，
    否则自扫会把自家文档判成投毒（已实测：docs/SKILL.md 因此误报）。"""
    pre = content[max(0, start - 2):start]
    post = content[end:end + 2]
    return "`" in pre and "`" in post


def _safe_suppress(content, start, end):
    """命中若落在反引号代码段内，或邻近良性元标记（教学样例/讲解框架），
    则抑制。返回 True 表示不报。"""
    if _in_code_span(content, start, end):
        return True
    window = content[max(0, start - 200): min(len(content), end + 200)]
    return bool(_BENIGN_META.search(window))


def rag_corpus_poison_analysis(files):
    """返回 {"findings": [...], "summary": {...}}，与同目录其他扫描器同形。

    files: {filepath: text_content}。text_content 是 RAG 语料 / 记忆导出 /
    知识库文档的正文。
    """
    findings = []
    seen = set()
    counts = {
        "rag_embedded_directive": 0,
        "rag_persona_hijack": 0,
        "rag_exfiltration_instruction": 0,
        "rag_urgent_directive": 0,
        "rag_cross_ref_reinforcement": 0,
        "rag_encoded_payload": 0,
    }

    def add(ftype, sev, desc, filepath, evidence):
        key = f"{ftype}:{filepath}:{evidence[:60]}"
        if key in seen:
            return
        seen.add(key)
        findings.append({
            "type": ftype,
            "severity": sev,
            "description": desc,
            "file": filepath,
            "evidence": evidence[:140],
            "owasp_category": _OWASP,
        })
        counts[ftype] = counts.get(ftype, 0) + 1

    n_files = 0
    for fp, content in files.items():
        if not isinstance(content, str) or not content.strip():
            continue
        n_files += 1

        # 1. 嵌入指令
        for pat in _EMBEDDED_DIRECTIVE:
            for m in pat.finditer(content):
                if _safe_suppress(content, m.start(), m.end()):
                    continue
                add(
                    "rag_embedded_directive",
                    "critical",
                    "RAG 语料中含『忽略既有指令/覆盖上下文』式嵌入指令——检索拼回"
                    "prompt 后可直接改写 agent 行为（间接注入残留，MITRE ATLAS "
                    "T0051 场景）",
                    fp, content[max(0, m.start() - 40): m.end() + 40],
                )

        # 2. 角色/身份劫持
        for pat in _PERSONA_HIJACK:
            for m in pat.finditer(content):
                if _safe_suppress(content, m.start(), m.end()):
                    continue
                add(
                    "rag_persona_hijack",
                    "critical",
                    "RAG 语料中含角色/身份劫持指令（'you are now' / 'your new "
                    "identity is' / 'act as'）——检索内容读回时被 LLM 当作可执行"
                    "角色定义而非普通文本，单次投毒即可持久化改写 agent 人格",
                    fp, content[max(0, m.start() - 40): m.end() + 40],
                )

        # 3. 外传诱导
        for pat in _EXFILTRATION:
            for m in pat.finditer(content):
                if _safe_suppress(content, m.start(), m.end()):
                    continue
                add(
                    "rag_exfiltration_instruction",
                    "critical",
                    "RAG 语料中含外传诱导（要求把 api_key/secret/system_prompt "
                    "发送到外部 URL/第三方）——检索命中后可能触发数据外泄",
                    fp, content[max(0, m.start() - 40): m.end() + 40],
                )

        # 4. 紧急性伪装指令
        for m in _URGENT_DIRECTIVE.finditer(content):
            if _safe_suppress(content, m.start(), m.end()):
                continue
            add(
                "rag_urgent_directive",
                "high",
                "RAG 语料用 IMPORTANT/URGENT 等紧急前缀包裹指令——典型社会工程"
                "加固手法，诱导 agent 优先执行被检索到的这条指令",
                fp, content[max(0, m.start() - 40): m.end() + 40],
            )

        # 5. 跨文档互证加固
        for m in _CROSS_REF_REINFORCE.finditer(content):
            if _safe_suppress(content, m.start(), m.end()):
                continue
            add(
                "rag_cross_ref_reinforcement",
                "high",
                "RAG 语料通过引用其他文档来『证明』自己这条指令（as stated in "
                "doc-X, you must...）——多文档互证可绕过单文档人工审查，是检索"
                "污染的常见加固手法",
                fp, content[max(0, m.start() - 40): m.end() + 40],
            )

        # 6. 编码载荷 + 执行上下文
        for m in _ENCODED_PAYLOAD.finditer(content):
            add(
                "rag_encoded_payload",
                "high",
                "RAG 语料含『解码后执行』式编码载荷（base64/hex 块被要求 eval/"
                "execute）——隐藏指令的常见载体，检索命中后可能触发代码执行",
                fp, content[max(0, m.start() - 40): m.end() + 40],
            )

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1

    summary = {
        "rag_corpus_poison_findings": len(findings),
        "severity_counts": sev_c,
        "files_scanned": n_files,
        "categories": {k: v for k, v in counts.items() if v > 0},
        "note": (
            "RAG 语料/持久化记忆内容投毒扫描（内容级，与 agent_memory_scan 代码级"
            "互补）：嵌入指令 / 角色劫持 / 外传诱导 / 紧急伪装 / 跨文档互证 / "
            "编码载荷 六类。命中为启发式强信号，建议人工复核后处置。"
        ),
    }
    return {"findings": findings, "summary": summary}
