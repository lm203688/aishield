# -*- coding: utf-8 -*-
"""
A2A / 多智能体编排信任链扫描（ASI07 · 跨智能体通信）

背景与边界
----------
`agentcard_scan.py` 已覆盖 **AgentCard JSON 结构层**（签名/过期/https/鉴权方案/
委托收敛，映射 MCP07）。但 A2A 生态还有两面它够不到：

1. **运行时消息 / 委托 artifact 层**：A2A 协议在运行时交换的 `message`（role+parts）
   / `task`（contextId）/ `delegationChain` 等 JSON 工件。当一条消息自带 `sender`
   身份字段却无 `signature`/`nonce`，或委托链把 `scope:"*"` / `role:"admin"` 下发
   给子 agent，就是 ASI07 的 spoofing / privilege-escalation。卡片验得了"身份"，
   验不了"这条消息/这次委托"的意图与授权收敛。
2. **内容级编排计划层**：agent 的 system prompt / SKILL.md / orchestration plan /
   多智能体调度配置里，若存在"无条件信任对端消息""把凭证转发给另一个 agent"
   "冒充某 agent""以全权限委托子 agent"等指令，就是 plan 静态层面的 goal-hijack
   链式入口（MITRE ATLAS T0051 在 agent 间的横向移动）。

本模块补这两面，与 agentcard_scan 互补、不重叠：
- agentcard_scan  → 解析 `.well-known/agent.json` 这种**卡片**。
- 本模块          → 解析 A2A **message/task/delegation** 工件 + 扫描 prompt/plan 文本。

判据纪律（与 rag_corpus_poison_scan 同源，零误报优先）
---------------------------------------------------
* 纯静态、零依赖、只读；不 spawn 任何命令、不联网。
* 内容层命中必须是**强信号**（动词 + 对端/子 agent 目标 + 信任/凭证/提权语义共现），
  且不含否定前缀（"don't delegate with full perms" 是良性建议，不报）。
* 良性侧抑制：反引号代码段内的引用攻击短语（讲解手法）抑制；教学框架整词抑制。
* severity：critical（可直接横向移动/提权/外传）/ high（架构性信任缺口）/ medium（加固项）。

对齐
----
* OWASP Agentic AI Top 10 (2025): ASI07 Agentic Misuse / Unsafe Multi-Agent Orchestration
* MITRE ATLAS: T0051 LLM Prompt Injection（agent 间横向移动场景）
* Google A2A: AgentCard / message(parts) / task(contextId) / delegationChain
"""

import json
import re

_OWASP = "ASI07"  # Unsafe Multi-Agent Orchestration

# ── 0. 良性侧抑制（与 rag_corpus_poison_scan 同纪律）──────────────────────
_BENIGN_META = re.compile(
    r'(for\s+example|an?\s+example|this\s+is\s+(?:a|an)\s+(?:test|sample|demo|example)|'
    r'as\s+an?\s+example|example\s+of|'
    r'for\s+demonstrat|this\s+is\s+(?:a|an)\s+demonstrat|'
    r'in\s+this\s+(?:example|tutorial|guide)|as\s+an?\s+illustrat|'
    r'pretend\s+(?:this|the\s+user)|role[- ]?play|'
    r'prompt[- ]?inject)', re.I)


def _in_code_span(content, start, end):
    """命中短语是否被 markdown 反引号包成行内代码（如讲解 `` `delegate with full
    permissions` ``）。被引用的攻击短语是文档在**讲解**手法，不是会被 agent 照着
    执行的活指令 —— 自家安全文档大量这样写，必须抑制，否则自扫误报。"""
    pre = content[max(0, start - 2):start]
    post = content[end:end + 2]
    return "`" in pre and "`" in post


def _is_negated(content, start):
    """命中前的 32 字符内若是否定前缀（don't / do not / never / not to / avoid /
    should not），说明这是"不要这样做"的良性建议，抑制。避免把"never delegate with
    full permissions"当成真实投毒指令。"""
    pre = content[max(0, start - 32):start].lower()
    return bool(re.search(
        r"(don'?t|do\s+not|never|not\s+to|avoid|should\s+not|must\s+not)\s+$", pre))


def _safe_suppress(content, start, end):
    """命中若落在反引号代码段内，或邻近良性元标记（教学样例/讲解框架），或带否定
    前缀（良性建议），则抑制。返回 True 表示不报。"""
    if _in_code_span(content, start, end):
        return True
    window = content[max(0, start - 200): min(len(content), end + 200)]
    if _BENIGN_META.search(window):
        return True
    if _is_negated(content, start):
        return True
    return False


# ── 1. 内容层：对端信任 / 凭证 / 冒充 / 委托提权（强信号正则）──────────────
# 1a. 把凭证/密钥转发给另一个 agent / 对端（横向外传）
_CREDENTIAL_FORWARD_PEER = re.compile(
    r'(?:send|forward|pass|share|give|provide|transmit|hand\s+over|leak)\b'
    r'[\s\S]{0,90}?'
    r'(?:your\s+|the\s+)?(?:api[-_]?key|secret|token|password|passwd|credential|'
    r'private[-_]?key|system[-_]?prompt|session[-_]?token|auth\s*(?:token|header))'
    r'[\s\S]{0,90}?'
    r'(?:to|with|onto|into|over\s+to)\s+'
    r'(?:the\s+)?(?:agent|peer|sub[- ]?agent|another\s+agent|the\s+other\s+agent|'
    r'upstream\s+agent|downstream\s+agent|collaborator)', re.I)

# 1b. 无条件信任对端消息（盲信，无验证）
_BLIND_TRUST_PEER = re.compile(
    r'(?:trust|believe|accept|obey|act\s+on|execute|follow|comply\s+with)\b'
    r'[\s\S]{0,50}?'
    r'(?:any|every|all|whatever|each)\b'
    r'[\s\S]{0,40}?'
    r'(?:message|instruction|request|command|order|task|directive|prompt)\b'
    r'[\s\S]{0,30}?'
    r'(?:from|by|sent\s+by|of|issued\s+by)\s+'
    r'(?:the\s+)?(?:peer|agent|sub[- ]?agent|another\s+agent|the\s+other\s+agent|'
    r'upstream|collaborator)', re.I)

# 1c. 以全/提权委托子 agent（plan 级 goal-hijack 入口）
_DELEGATION_ESCALATION = re.compile(
    r'(?:delegate|hand\s+(?:off|over)|forward\s+to|route\s+to|assign\s+to|'
    r'pass\s+to|escalate\s+to|grant\s+(?:to|the))\b'
    r'[\s\S]{0,60}?'
    r'(?:agent|sub[- ]?agent|peer|the\s+other\s+agent|another\s+agent|'
    r'upstream|worker|tool\s+agent)\b'
    r'[\s\S]{0,90}?'
    r'(?:with\s+(?:full|elevated|admin|root|superuser|unrestricted|maximum|'
    r'all|higher)\s+(?:permissions?|access|privileges?|rights?|control|scope|agency|'
    r'authority)|full\s+(?:agency|authority|control)|bypass(?:ing)?\s+(?:the\s+)?'
    r'(?:scope|permission|boundary))', re.I)

# 1d. 冒充 / 接受对端声称的身份（spoofing）
_IDENTITY_SPOOF = re.compile(
    r'(?:pretend\s+to\s+be|impersonate|act\s+as\s+if\s+you\s+are|'
    r'claim\s+(?:to\s+be|you\s+are)|masquerade\s+as)\b'
    r'[\s\S]{0,60}?'
    r'(?:agent|another\s+agent|the\s+other\s+agent|peer|sub[- ]?agent|'
    r'upstream\s+agent|the\s+orchestrator|the\s+root\s+agent)|'
    r'(?:accept|trust|believe)\b[\s\S]{0,40}?\b'
    r"(?:peer'?s?|agent'?s?|the\s+other\s+agent'?s?)\s+(?:claimed|asserted|"
    r'stated|declared|self[- ]?reported)\s+(?:identity|name|role|capability)', re.I)


# ── 2. 结构层：A2A 消息 / 委托 artifact（JSON 解析，不靠正则盲扫）──────────
_A2A_MESSAGE_MARKERS = {"parts", "task", "contextId", "messageId",
                        "delegationChain", "delegations", "messages"}


def _looks_like_a2a_artifact(obj):
    """仅当 JSON 含 A2A **运行时工件**专属键时才视为扫描目标，避免误伤 AgentCard
    （卡片用 protocolVersion/capabilities/skills，由 agentcard_scan 处理）或普通
    MCP config。要求 message/task/delegation 这类运行期结构。"""
    if isinstance(obj, list):
        obj = obj[0] if obj and isinstance(obj[0], dict) else None
    if not isinstance(obj, dict):
        return False
    keys = set(obj.keys())
    if {"role", "parts"} <= keys:          # A2A message
        return True
    if "task" in keys and ("contextId" in keys or "artifacts" in keys):  # A2A task
        return True
    if "messages" in keys:                 # 消息数组
        return True
    if "delegationChain" in keys or "delegations" in keys:  # 委托链
        return True
    return False


def _collect_message_objects(obj):
    """从 artifact 中抽取需要校验的 message / delegation 子对象。"""
    out = []
    if isinstance(obj, list):
        obj = obj[0] if obj and isinstance(obj[0], dict) else None
    if not isinstance(obj, dict):
        return out
    if {"role", "parts"} <= set(obj.keys()):
        out.append(obj)
    if isinstance(obj.get("messages"), list):
        for m in obj["messages"]:
            if isinstance(m, dict):
                out.append(m)
    for key in ("delegationChain", "delegations"):
        val = obj.get(key)
        if isinstance(val, list):
            for d in val:
                if isinstance(d, dict):
                    out.append(d)
        elif isinstance(val, dict):
            out.append(val)
    if isinstance(obj.get("task"), dict):
        out.append(obj["task"])
    return out


_IDENTITY_KEYS = {"sender", "from", "agent", "author", "issuer", "origin", "source"}
_PROOF_KEYS = {"signature", "sig", "signed", "proof", "nonce", "timestamp",
               "verified", "hmac", "token", "mac", "sign"}


def _a2a_structural_checks(blob):
    """返回结构层命中列表：[(ftype, sev, desc, evidence)]。"""
    hits = []
    try:
        obj = json.loads(blob)
    except (ValueError, TypeError):
        return hits
    if not _looks_like_a2a_artifact(obj):
        return hits

    objs = _collect_message_objects(obj)
    escalated = False
    unverified = False
    no_replay = False

    for o in objs:
        keys = set(o.keys())
        # 委托提权：scope:"*" / role:admin / permissions:full 等
        sub = json.dumps(o, ensure_ascii=False)
        if (re.search(r'"scope"\s*:\s*"\*"', sub) or
                re.search(r'"role"\s*:\s*"(admin|root|superuser|owner)"', sub, re.I) or
                re.search(r'"(?:permissions?|access|privilege)"\s*:\s*'
                          r'"(full|elevated|unrestricted|all|admin)"', sub, re.I)):
            escalated = True
        # 未验证发送方：自带身份字段却无证明
        if (_IDENTITY_KEYS & keys) and not (_PROOF_KEYS & keys):
            unverified = True
        # 重放保护缺失：消息数组无 id/nonce/timestamp
        if "messages" in set(obj.keys()) and isinstance(obj.get("messages"), list):
            if not any(k in _PROOF_KEYS for o2 in obj["messages"]
                       if isinstance(o2, dict) for k in o2.keys()):
                no_replay = True

    if escalated:
        hits.append((
            "a2a_delegation_escalation", "critical",
            "A2A 委托链/消息把 scope:\"*\" 或 role:admin/full 等提权授权下发给子 "
            "agent——委托未做 scope attenuation，子 agent 可越权执行父 agent 无权"
            "做的动作（ASI07 privilege escalation，MITRE ATLAS 横向移动）",
            blob[:120]))
    if unverified:
        hits.append((
            "a2a_unverified_sender", "high",
            "A2A message/task 自带 sender/from/agent 身份字段，但同一工件内无 "
            "signature/nonce/timestamp 等证明——接收方无法验真发送方，可被 spoofing"
            "（对应 A2A #1672/#1786 身份验真缺口）",
            blob[:120]))
    if no_replay:
        hits.append((
            "a2a_replay_no_protection", "medium",
            "A2A messages 数组内每条消息均无 nonce/timestamp/id 等重放保护字段，"
            "攻击者可截获并重放消息诱导子 agent 重复执行（ASI07 replay）",
            blob[:120]))
    return hits


def a2a_orchestration_analysis(files):
    """返回 {"findings": [...], "summary": {...}}，与同目录其他扫描器同形。

    files: {filepath: text_content}。覆盖两类：
      - 内容文本（prompt / SKILL.md / orchestration plan / 调度配置）：盲信对端、
        凭证转发对端、身份冒充、委托提权。
      - A2A 运行时工件 JSON（message/parts、task/contextId、delegationChain）：
        委托提权、未验证发送方、重放保护缺失。
    """
    findings = []
    seen = set()
    counts = {
        "a2a_credential_forward_peer": 0,
        "a2a_blind_trust_peer": 0,
        "a2a_delegation_escalation": 0,
        "a2a_identity_spoof": 0,
        "a2a_unverified_sender": 0,
        "a2a_replay_no_protection": 0,
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
        low = content.lower()

        # ── 内容层 ──
        # 1a 凭证转发对端
        for m in _CREDENTIAL_FORWARD_PEER.finditer(content):
            if _safe_suppress(content, m.start(), m.end()):
                continue
            add(
                "a2a_credential_forward_peer", "critical",
                "编排计划/提示词要求把 api_key/secret/token 等凭证转发给另一个 agent/"
                "对端——横向凭证外传，子 agent 或攻陷的对端可借此冒充本 agent 调用"
                "上游服务（ASI07 + MITRE ATLAS T0051 横向移动）",
                fp, content[max(0, m.start() - 40): m.end() + 40],
            )

        # 1b 盲信对端
        for m in _BLIND_TRUST_PEER.finditer(content):
            if _safe_suppress(content, m.start(), m.end()):
                continue
            add(
                "a2a_blind_trust_peer", "high",
                "编排计划/提示词要求无条件信任来自对端 agent 的任意消息/指令——缺发送方"
                "验真时，被 spoof 的对端可借此劫持本 agent 的目标（ASI07 blind trust，"
                "goal-hijack 链式入口）",
                fp, content[max(0, m.start() - 40): m.end() + 40],
            )

        # 1c 委托提权
        for m in _DELEGATION_ESCALATION.finditer(content):
            if _safe_suppress(content, m.start(), m.end()):
                continue
            add(
                "a2a_delegation_escalation", "critical",
                "编排计划/提示词要求以全权限/提权委托子 agent（delegate ... with full "
                "permissions）——子 agent 获得超出父 agent 的授权，构成权限放大与 goal-"
                "hijack 入口（ASI07 privilege escalation）",
                fp, content[max(0, m.start() - 40): m.end() + 40],
            )

        # 1d 身份冒充
        for m in _IDENTITY_SPOOF.finditer(content):
            if _safe_suppress(content, m.start(), m.end()):
                continue
            add(
                "a2a_identity_spoof", "high",
                "编排计划/提示词要求冒充另一 agent 或接受对端自报身份——spoofing 面，"
                "可被用于伪造来源诱导下游 agent（ASI07 identity spoofing）",
                fp, content[max(0, m.start() - 40): m.end() + 40],
            )

        # ── 结构层（仅对看起来像 JSON 的内容尝试解析）──
        if low.lstrip().startswith("{") or low.lstrip().startswith("["):
            try:
                json.loads(content)
            except (ValueError, TypeError):
                continue
            for ftype, sev, desc, ev in _a2a_structural_checks(content):
                add(ftype, sev, desc, fp, ev)

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1

    summary = {
        "a2a_orchestration_findings": len(findings),
        "severity_counts": sev_c,
        "files_scanned": n_files,
        "categories": {k: v for k, v in counts.items() if v > 0},
        "note": (
            "A2A/多智能体编排信任链扫描（ASI07，与 agentcard_scan 互补）：内容层 "
            "（盲信对端 / 凭证转发对端 / 身份冒充 / 委托提权）+ 结构层（委托提权 / "
            "未验证发送方 / 重放保护缺失）。命中为启发式强信号，建议人工复核后处置。"
        ),
    }
    return {"findings": findings, "summary": summary}
