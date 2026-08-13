# -*- coding: utf-8 -*-
"""
跨 server scope 组合 / 爆炸半径 / 混淆副手分析（ASI08 级联失败 · ASI07 跨 agent）

背景：agentmelt "blast radius = union of every connected server's scope"。单个 server 看似安全，
组合后形成高危链路（如一个能读凭证 + 另一个有出站 → 外传）；混淆副手（confused deputy）
让 agent 用自己的权限转发请求到其它 server。

检测（纯本地，单文件内组合信号 + 跨文件委托）：
- 凭证读取 + 出站：同文件含敏感凭证读取且含外传/POST。
- 文件读取 + 出站：读敏感文件且发往外部。
- 委托转发：指示 agent 用自己的凭据调用/转发到另一 server/agent（混淆副手）。
"""

import re

_OWASP = "MCP02"

_CRED_READ = re.compile(
    r'(~/\.aws/credentials|\.ssh/id_rsa|id_rsa|\.env\b|secrets?\.(json|yml|yaml)|'
    r'credentials\.(json|yml|yaml)|read\s+(the\s+)?(api[_-]?key|token|password|secret))', re.I)
_SENS_FILE = re.compile(r'(/etc/passwd|/etc/shadow|\.ssh/|credentials|secrets?\.|\.env\b)', re.I)
_EGRESS = re.compile(
    r'(https?://[a-z0-9.\-]+\.[a-z]{2,}|curl\s+[^"\n]*https?://|wget\s+[^"\n]*https?://|'
    r'(send|upload|post|transmit|exfil|beacon)\s+(the\s+)?(data|file|key|secret|result)\s+(to|over))', re.I)
_DELEGATE = re.compile(
    r'(forward|relay|proxy|pass\s+(through|along)|delegate)\b[^\n]*?'
    r'(using|with|via)\s+(your|the\s+agent\'?s|its)\s+(credentials|token|session|privileges|api\s+key|auth)', re.I)


def scope_composition_analysis(files):
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
        has_cred = bool(_CRED_READ.search(content)) or bool(_SENS_FILE.search(content))
        has_egress = bool(_EGRESS.search(content))
        has_delegate = bool(_DELEGATE.search(content))
        if has_cred and has_egress:
            add("exfil_combo", "high",
                "同文件同时具备敏感凭证/文件读取与外传通道，构成凭证外泄链路（爆炸半径/级联失败）",
                fp, content[:120])
        elif has_cred and not has_egress:
            # 仅读凭证也算高危能力，但无外传则不升级为组合告警
            pass
        if has_delegate:
            add("confused_deputy_forward", "high",
                "指示 agent 用自己的凭据/会话转发请求到其它 server/agent，构成混淆副手（confused deputy）",
                fp, content[:120])

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1
    summary = {"scope_composition_findings": len(findings), "severity_counts": sev_c,
               "files_scanned": len(files), "note": "跨 server scope 组合/爆炸半径/混淆副手（ASI08/ASI07）"}
    return {"findings": findings, "summary": summary}
