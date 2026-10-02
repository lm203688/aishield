# -*- coding: utf-8 -*-
"""
Agent Memory 深度扫描（2026-09-30 引入 · 竞品空白填补）

背景
----
2026 年 Agent Memory 品类爆发：Hermes (Nous Research, 47k stars, self-evolving)、
Hindsight (Virginia Tech + LongMemEval SOTA)、Innate (Rust recall→record→evolve)、
instinct (WRG-11, memory 驱动 agent 行为) 同时上线。这些框架把"记忆"从
被动存储升级为"可执行的策略源"——记忆条目本身可以是规则、策略、习惯、
甚至代码块。

本库既有的 memory 相关扫描器：
  * memory_scan.py           — 检测"注入行为"（有人正在写恶意指令进记忆）
  * memory_integrity_scan.py — 检测"结构缺陷"（无完整性校验 / 共享无分区）

二者都基于**代码模式静态分析**，覆盖了 ASI06 Memory & Context Poisoning 的
两个基础形态。但**新框架特化的攻击面**没有被覆盖：

1. **cross_session_accumulation**   —— 记忆条目缺少时间戳 / session 边界，
   攻击者可以在第 1 个 session 埋一条被时间衰减过滤的"良性"记录，累积到
   第 N 个 session 时才浮现成可执行的恶意指令。这是 Hermes self-evolving
   和 instinct confidence 累积机制共有的攻击面。

2. **memory_recall_injection**      —— 用户 prompt 直接拼进向量检索 query，
   检索结果又被直接拼进 system prompt。攻击者通过精心构造的检索 query
   把 memory 里的"合法历史记录"变成对当前 session 的指令覆盖。这是
   memory_RAG 架构的固有攻击面（Hindsight 的检索层尤其脆弱）。

3. **framework_specific_api**       —— Hermes / Hindsight / Innate / Letta /
   Mem0 / Zep 各自的 API 特化检测。同一代码库同时使用多个 memory 后端时
   容易漏掉隔离边界；本扫描器按 API 名分别报告，让人工审计能逐框架判断。

4. **persistent_goal_injection**    —— "从此刻起 / 永久 / always / never"
   等跨 session 语义的指令。既有的 memory_scan.py 已经覆盖了写入行为，
   但**读回时**这些条目会被当作普通记忆拼进 system prompt——检测"读回
   侧"缺少隔离。

判定纪律
--------
* 纯静态、零依赖、只读；不 spawn 任何命令、不联网。
* 命中判定必须基于**强信号**（框架 API 名 + 关键字段共现），避免
  "任何文件里出现 memory 就报"的通用噪音。
* severity 分级：critical（可直接跨 session 执行指令）/ high（架构缺陷
  需人工确认）/ medium（潜在风险，需结合上下文判断）。

对齐
----
* OWASP Agentic AI Top 10 (2025): ASI06 Memory & Context Poisoning
* OWASP MCP Top 10 (2025 v0.1): MCP06 Intent Flow Subversion
* 与 memory_integrity_scan 的边界：本模块关注**跨 session / 检索 /
  框架 API** 三个新维度；memory_integrity_scan 关注**存储完整性与分区**。
"""

import re

_OWASP = "ASI06"   # Memory & Context Poisoning

# ── 1. 框架特化 API ───────────────────────────────────────────────────────
# 每个框架一个 dict：api_pattern（API 调用特征） + risk_signal（该 API 的
# 特有风险信号）。风险信号为正则，命中即认为该 API 存在特化风险。
_FRAMEWORKS = {
    "hermes": {
        # Hermes (Nous Research)：self-evolving agent，API 名 recall/record/evolve/reflect
        "api": re.compile(
            r'\b(HermesAgent|hermes\.record|hermes\.recall|hermes\.evolve|'
            r'hermes\.reflect|hermes\.consolidat|from\s+hermes[\s\.]|'
            r'import\s+hermes\b)', re.I),
        # 特化风险：evolve / consolidate 调用（self-evolving 无版本 pin / 无审计）
        "risk": re.compile(
            r'(evolve\s*\(|consolidat\w*\s*\()', re.I),
        # 安全约束关键词（文件级；命中即视为已有约束，抑制告警）
        "guards": re.compile(
            r'(version\s*=|pin(?:ned|_to)?\s*=|rollback\s*=|'
            r'signature\s*=|audit(?:_?log)?\s*=)', re.I),
    },
    "hindsight": {
        # Hindsight：仿生记忆，LongMemEval SOTA。API: recall / remember / forget
        "api": re.compile(
            r'\b(Hindsight|HindsightMemory|hindsight\.recall|hindsight\.remember|'
            r'hindsight\.forget|from\s+hindsight[\s\.]|import\s+hindsight\b)', re.I),
        "risk": re.compile(r'(recall\s*\()', re.I),
        "guards": re.compile(
            r'(scope\s*=|namespace\s*=|tenant\s*=|filter\s*=)', re.I),
    },
    "innate": {
        # Innate (Rust)：recall → record → evolve 三阶段。
        "api": re.compile(
            r'\b(innate_memory|InnateMemory|innate::|InnateClient|'
            r'innate\.recall|innate\.record|innate\.evolve)', re.I),
        "risk": re.compile(r'(innate\.evolve\s*\(|innate::evolve)', re.I),
        "guards": re.compile(r'(version|rollback|signature|audit)', re.I),
    },
    "letta": {
        # Letta：server-side memory，API: memory.add / memory.update / memory.delete
        "api": re.compile(
            r'\b(LettaClient|letta_agent|letta\.Client|letta_memory|'
            r'memory\.update\s*\(|memory\.delete\s*\(|'
            r'from\s+letta[\s\.]|import\s+letta\b)', re.I),
        "risk": re.compile(
            r'(letta[\w\.]*\s*\.\s*memory[\w\.]*\s*\.\s*(update|set|replace)\s*\()',
            re.I),
        "guards": re.compile(
            r'(signature\s*=|audit|rollback|verified\s*=)', re.I),
    },
    "mem0": {
        # Mem0：memory.add / memory.search / memory.get / memory.delete
        "api": re.compile(
            r'\b(mem0\.Memory|Mem0Client|from\s+mem0[\s\.]|import\s+mem0\b|'
            r'mem0\.(add|search|get|delete|update)\s*\()', re.I),
        "risk": re.compile(r'(mem0\.(add|update)\s*\()', re.I),
        "guards": re.compile(
            r'(user_id\s*=|agent_id\s*=|session_id\s*=)', re.I),
    },
    "zep": {
        # Zep：Zep memory store，API: zep.add / zep.search / zep.get
        "api": re.compile(
            r'\b(ZepClient|zep\.Client|from\s+zep[\s\.]|import\s+zep\b|'
            r'zep\.(add|search|get)\s*\()', re.I),
        "risk": re.compile(r'(zep\.add\s*\()', re.I),
        "guards": re.compile(
            r'(session_id\s*=|user_id\s*=|namespace\s*=)', re.I),
    },
    "memobase": {
        # Memobase：agent memory 服务器
        "api": re.compile(
            r'\b(MemobaseClient|memobase\.)', re.I),
        "risk": re.compile(r'memobase\.\w*\s*\('),
        "guards": re.compile(r'(session_id|user_id|scope)', re.I),
    },
    "cognee": {
        # Cognee：knowledge graph 记忆
        "api": re.compile(r'\bfrom\s+cognee|import\s+cognee\b'),
        "risk": re.compile(r'cognee\.(\w+)\s*\('),
        "guards": re.compile(r'(namespace|scope|tenant)', re.I),
    },
}

# ── 2. 跨 session 累积污染 ──────────────────────────────────────────────
# 记忆条目必须有至少一个时间/边界锚点，否则无法区分"合法历史"与"跨 session
# 累积的注入"。检测：memory 写入调用但整行/邻近无时间戳 / session_id /
# trace_id 等锚点。
_SESSION_ANCHOR = re.compile(
    r'(timestamp|created_at|updated_at|inserted_at|session_?id|trace_?id|'
    r'request_?id|turn_?id|msg_?id|message_?id|turn\s*=|'
    r'datetime\(\)|time\.time|time\.now|utcnow|isoformat|strftime|'
    r'\bepoch\b|\bnow\(\))', re.I)

# 记忆写入调用（比 memory_integrity_scan 的 EXPLICIT 更严，只匹配明确的
# "持久化写入"调用，不是"读/查"）
_WRITE_CALL = re.compile(
    r'(memory\.(add|save|set|append|update|write|put|store|insert|commit)\s*\(|'
    r'(hermes|hindsight|letta|mem0|zep|innate|memobase|cognee)\s*\.\s*'
    r'(add|record|remember|store|set|save|insert|commit|evolve)\s*\(|'
    r'INSERT\s+INTO\s+[`"\']?(memories?|memory|history|session|context|traces)[`"\']?\s*\()',
    re.I)

# 「客户端变量持有」写入形态（2026-10-02 补）
#
# 实证来源：给 Agent Memory 面建基准语料时，mem0 的一条标准写法
#     client = mem0.MemoryClient(...); client.add(messages, user_id="alice")
# 全类零命中 —— 各框架的 risk 正则只写死 `mem0.add(` / `zep.add(` 这种
# **模块直调**形态，而这三个框架的官方示例恰恰都是「先建 client 再
# client.add」。结果是扫描器号称支持 8 个框架，实际对其中 3 个的主流
# 用法是瞎的。
#
# 判定纪律：客户端变量只放宽**写操作**语义（add/update/record/save/...），
# 不放宽读操作；良性侧靠各框架 guards（user_id= / session_id= / audit 等）
# 与邻近锚点（timestamp / session_id）抑制，负样本见 _diag_mem 及其保留版。
_CLIENT_VAR_WRITE = re.compile(
    r'\b(?:mem|mem0|zep|store|client|memory|memory_store)\s*\.\s*'
    r'(add|update|record|save|set|append|replace|store|write|put)\s*\(', re.I)

# ── 3. Memory recall injection ─────────────────────────────────────────
# 用户输入直接拼进向量检索 query，检索结果直接拼进 system prompt。
# 特征：query 字符串包含 f-string 或 .format / % 拼接用户输入；
# 或者直接把检索结果拼进 system prompt 而没有清洗。
_QUERY_CONCAT = re.compile(
    r'(recall|search|query|retrieve|find|lookup)\s*\(\s*'
    r'(?:f\s*["\']|f["\']|" ?\+ ?\w+|" %\s*\(|'
    r'"\s*\.format\s*\(|\bformat\s*\(|\bf\s*|'
    r'user(?:_?input|_?query|_?message|_?prompt|_?text)\b|'
    r'input\(|stdin|message\.content)', re.I)

_SYSTEM_PROMPT_INJECT = [
    # 顺序 A：system prompt 先出现，随后（200 字符内）出现 recall/search 调用
    re.compile(
        r'(system[_\s]?prompt|system_?msg|sys_?prompt|context\s*=|'
        r'<system>\s*|#?\s*System\s*[:：])'
        r'.{0,200}'
        r'(recall|search|retrieve|find|lookup|memory\.)', re.I | re.S),
    # 顺序 B：recall/search 先出现，随后（300 字符内）被赋给 system prompt
    re.compile(
        r'(recall|search|retrieve|find|lookup|memory\.)\s*\(.*?\)'
        r'.{0,300}'
        r'(system[_\s]?prompt|system_?msg|sys_?prompt|<system>|'
        r'#?\s*System\s*[:：])', re.I | re.S),
]

# ── 4. Persistent goal injection（读回侧）───────────────────────────────
# 记忆条目中包含"跨 session 语义"的动词短语。检测读取侧（recall / get /
# query / find）返回的内容被直接拼进 system prompt。
_PERSIST_VERB = re.compile(
    r'\b(from\s+now\s+on|going\s+forward|'
    r'permanent(?:ly)?|persist(?:ence|ent)?|'
    r'always|never|'
    r'from\s+this\s+point|'
    r'每次|始终|从今以后|从现在起|永远|'
    r'永久|'
    r'今后|'
    r'以后)\b', re.I)


def agent_memory_analysis(files):
    """返回 {"findings": [...], "summary": {...}}，与同目录其他扫描器同形。"""
    findings = []
    seen = set()

    def add(ftype, sev, desc, filepath, evidence):
        key = f"{ftype}:{filepath}"
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

    n_files = 0
    framework_hits = {name: 0 for name in _FRAMEWORKS}

    for fp, content in files.items():
        if not isinstance(content, str) or not content.strip():
            continue
        n_files += 1
        lines = content.splitlines()

        # ── 检测 1：框架特化 API + 风险信号 ─────────────────────────────
        for fw_name, fw in _FRAMEWORKS.items():
            if not fw["api"].search(content):
                continue
            framework_hits[fw_name] += 1
            # 框架 risk 优先；未命中时再试「客户端变量持有」形态
            # （client.add(...)）。guards 抑制对两条路径同时生效 ——
            # 有 version= / user_id= / audit_log= 的写法不算缺约束。
            if ((fw["risk"].search(content) or _CLIENT_VAR_WRITE.search(content))
                    and not fw["guards"].search(content)):
                add(
                    f"memory_framework_{fw_name}_risky_api",
                    "high",
                    f"使用 {fw_name} 记忆 API 但同文件未见该框架特化的安全约束"
                    f"（version pin / scope / session_id / audit log 之一）——"
                    f"{fw_name} 的记忆 API 默认信任调用者写入，缺约束即等于"
                    f"跨 session 记忆污染通道",
                    fp,
                    content[:140],
                )

        # ── 检测 2：跨 session 累积污染（写入侧）────────────────────────
        # 记忆写入调用但邻近 3 行内无时间/边界锚点
        for i, line in enumerate(lines):
            if not _WRITE_CALL.search(line):
                continue
            # 邻近 3 行（±2）找锚点
            window_start = max(0, i - 2)
            window_end = min(len(lines), i + 3)
            window = "\n".join(lines[window_start:window_end])
            if _SESSION_ANCHOR.search(window):
                continue
            # 整文件也可能有全局时间戳（如 DB migration），检查
            if _SESSION_ANCHOR.search(content):
                continue
            add(
                "cross_session_accumulation",
                "high",
                "记忆写入调用未见时间戳/session_id/trace_id 等边界锚点：跨 session "
                "累积污染无法检测（攻击者可先埋'良性'记录，多个 session 后再浮现"
                "为可执行指令）",
                fp,
                line.strip()[:140],
            )

        # ── 检测 3：Memory recall injection ────────────────────────────
        # 特征 A：query 字符串拼接用户输入
        _sysprompt_hit = any(p.search(content) for p in _SYSTEM_PROMPT_INJECT)
        if _QUERY_CONCAT.search(content) and _sysprompt_hit:
            add(
                "memory_recall_injection",
                "critical",
                "检索 query 拼接用户输入且结果直接拼进 system prompt——攻击者"
                "可通过精心构造的检索 query 把 memory 里的'合法历史记录'变成"
                "对当前 session 的指令覆盖（Hindsight 检索层、Hermes recall 的"
                "典型脆弱点）",
                fp,
                content[:140],
            )

        # ── 检测 4：Persistent goal injection（读回侧）──────────────────
        # 记忆读取路径 + 跨 session 语义动词 + 无隔离/清洗
        if _PERSIST_VERB.search(content) and _WRITE_CALL.search(content):
            # 检查是否有隔离：过滤 / 清洗 / 边界检测
            if not re.search(
                r'(sanitize|cleanse|filter|strip|escape|html\.escape|'
                r'disallow|block(?:list|ed)|deny(?:list|ed)|'
                r'remove_?tags|<ignore>|</ignore>|'
                r'delimit(?:er|ing)|separator)',
                content, re.I,
            ):
                add(
                    "persistent_goal_injection",
                    "critical",
                    "记忆条目包含跨 session 语义动词（'from now on' / 'always' /"
                    " '从此刻起' / '永久' 等）且读回侧未见清洗/过滤/边界隔离——"
                    "记忆条目读回时会被 LLM 当作可执行指令而非历史事实，"
                    "单次注入即可跨 session 持久化（CVE-2025-55549 类模式）",
                    fp,
                    content[:140],
                )

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1

    summary = {
        "agent_memory_findings": len(findings),
        "severity_counts": sev_c,
        "files_scanned": n_files,
        "framework_hits": {k: v for k, v in framework_hits.items() if v > 0},
        "note": (
            "Agent Memory 深度扫描：跨 session 累积污染 / 检索注入 / "
            "框架特化 API / 持久化指令。覆盖 Hermes / Hindsight / Innate / "
            "Letta / Mem0 / Zep / Memobase / Cognee 八个框架。"
        ),
    }
    return {"findings": findings, "summary": summary}
