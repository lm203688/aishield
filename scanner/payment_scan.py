# -*- coding: utf-8 -*-
"""
AP2 / x402 支付授权 scope 审计（经济层 · 支付授权）

背景：AP2 (Agent Payments Protocol) + A2A x402 稳定币微支付（Coinbase×Google）兴起。
支付授权存在"三授权"：意图(intent) / 购物车(cart) / 支付(payment)。
风险：支付授权过宽（maxAmount 缺失/无限、auto_approve、scope=*），agent 可被诱导超额付款。

本模块扫描 x402 / AP2 / 稳定币支付配置，识别支付授权缺口：
  - maxAmount 缺失 / 为 * / 为 0 或极大值（无上限）
  - auto_approve / autoApprove: true（支付免确认）
  - payTo / facilitator 指向硬编码未授信地址（缺可信白名单）
  - payment scope 过宽（scope: "*"）
  - 支付授权未绑定具体 intent（authorize/approve payment 但无 cartId/orderId/intent 关联）

设计原则：纯本地正则/启发式，不联网、不 spawn。仅在支付上下文（x402/payment/usdc 等标记）才检测，降误报。
"""

import re

_OWASP = "MCP02"  # 权限范围蔓延导致提权

_PAYMENT_HINT = re.compile(
    r'(x402|ap2|payment|payments|pay_to|payTo|facilitator|max_amount|maxAmount|'
    r'stablecoin|usdc|settle|invoice|checkout)', re.I)

_NO_CAP = re.compile(
    r'(max[_-]?amount|maxAmount|limit|spending[_-]?limit|cap)\s*[:=]\s*'
    r'("?(?:none|\*|unlimited|infinite|0|null|false)"?|0)', re.I)
_AUTO_APPROVE = re.compile(
    r'(auto[_-]?approve|autoApprove|auto[_-]?pay|skip[_-]?confirm)\s*[:=]\s*(true|1|"true"|"yes")', re.I)
_OVERBROAD_SCOPE = re.compile(
    r'(scope|scopes|permissions)\s*[:=]\s*'
    r'(\[?\s*["\']?\s*\*+\s*["\']?\s*\]?|["\']\s*(?:admin|superuser|root|all|full|unrestricted)\s*["\'])',
    re.I)
_HARDCODED_ADDR = re.compile(
    r'(payTo|pay_to|facilitator|recipient|to)\s*[:=]\s*["\']'
    r'(0x[a-fA-F0-9]{40}|[1-9A-HJ-NP-Za-km-z]{25,})["\']', re.I)
_GRANT_NO_INTENT = re.compile(
    r'(authoriz\w*\s*(payment|pay)|approve\w*\s*(payment|pay)|'
    r'payment\s*(authorization|approval|grant)|grant\w*\s*(payment|pay))', re.I)
_INTENT_BIND = re.compile(r'(cart[_-]?id|order[_-]?id|intent|invoice[_-]?id|reference)', re.I)


def payment_analysis(files):
    """对 {filepath: content} 跑 AP2/x402 支付授权 scope 审计。返回 {findings, summary}。"""
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
        if not _PAYMENT_HINT.search(content):
            continue  # 仅在支付上下文检测

        # 1) 无支付上限
        m = _NO_CAP.search(content)
        if m:
            add("payment_no_cap", "high",
                "x402/AP2 支付缺少金额上限（maxAmount/limit 为 none/*/0），agent 可被诱导无限额付款",
                filepath, m.group(0)[:120])

        # 2) 自动批准支付
        m = _AUTO_APPROVE.search(content)
        if m:
            add("payment_auto_approve", "high",
                "支付配置 auto_approve/skip_confirm=true，agent 付款免人工确认，易被诱导转账",
                filepath, m.group(0)[:120])

        # 3) 过宽支付 scope
        m = _OVERBROAD_SCOPE.search(content)
        if m:
            add("payment_overbroad_scope", "high",
                "支付授权 scope 过宽（'*'/admin/full），违反最小授权",
                filepath, m.group(0)[:120])

        # 4) 硬编码收款地址（顾问级，低扣分）
        m = _HARDCODED_ADDR.search(content)
        if m:
            add("payment_hardcoded_recipient", "low",
                "支付收款方/facilitator 为硬编码地址，缺可信白名单与校验，易被替换或固定为攻击者地址",
                filepath, m.group(0)[:120])

        # 5) 支付授权未绑定 intent（仅当显式 authorize/approve payment 时才报，降误报）
        if _GRANT_NO_INTENT.search(content) and not _INTENT_BIND.search(content):
            add("payment_no_intent_binding", "medium",
                "支付授权（authorize/approve payment）未绑定具体意图（缺 cartId/orderId/intent），"
                "agent 可能在无对应交易上下文下付款",
                filepath, content[:120])

    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1

    summary = {
        "payment_findings": len(findings),
        "severity_counts": sev_counts,
        "files_scanned": len(files),
        "note": "AP2/x402 支付授权 scope 审计：金额上限、auto_approve、scope 收敛、intent 绑定",
    }
    return {"findings": findings, "summary": summary}
