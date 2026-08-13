# -*- coding: utf-8 -*-
"""
最小代理 / 能力过度声明审计（ASI02 工具滥用 · ASI10 rogue）

背景：OWASP "Least-Agency"（最小代理扩展最小权限）。风险：低权限意图的 skill 却声明/使用
高危能力（shell 执行、删文件、读凭证、联网发送、代码执行），违背最小代理原则。

检测（纯本地，仅命中显式危险原语，良性 skill 不会含）：
- 管道执行：`curl ... | sh` / `wget ... | bash`
- 危险原语：rm -rf / sudo <危险命令> / chmod 777 / os.system / eval( / subprocess
- 凭证读取：cat ~/.aws/credentials / id_rsa / ssh key / 读取 secrets 文件
- 码执行：python -c / node -e / exec( 直接执行动态内容
"""

import re

_OWASP = "MCP02"   # 权限范围 / 最小代理

_PRIMITIVES = [
    ("pipe_exec", re.compile(r'(curl|wget)\s+[^"\n]*\|\s*(sh|bash)', re.I)),
    ("rm_rf", re.compile(r'\brm\s+-rf?\b|\brm\s+.*-r\s+-f', re.I)),
    ("sudo_danger", re.compile(r'\bsudo\s+(rm|delete|chmod|mv|cp|sh|bash|python|node|dd)\b', re.I)),
    ("chmod_777", re.compile(r'\bchmod\s+777\b', re.I)),
    ("os_system", re.compile(r'\bos\.system\s*\(|subprocess\.(call|Popen|run)\s*\(', re.I)),
    ("eval_exec", re.compile(r'\beval\s*\(|\bexec\s*\(|\bnode\s+-e\b|\bpython\s+-c\b', re.I)),
    ("cred_read", re.compile(
        r'(cat|read|type|more)\s+[^"\n]*(~/\.aws/credentials|\.ssh/id_rsa|id_rsa|'
        r'\.env|secrets?\.(json|yml|yaml|env)|credentials\.(json|yml|yaml))', re.I)),
    ("ssh_key", re.compile(r'(ssh[\- ]?key|private\s+key|id_ed25519|id_rsa|id_ecdsa)', re.I)),
]


def least_agency_analysis(files):
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
        for label, pat in _PRIMITIVES:
            if pat.search(content):
                hits.append(label)
        if not hits:
            continue
        # 高危原语组合（管道执行/凭证读取/rm -rf）升级 high，其余 medium
        sev = "high" if any(h in hits for h in ("pipe_exec", "cred_read", "rm_rf", "os_system", "eval_exec")) else "medium"
        add("capability_overclaim", sev,
            "检测到高危能力原语（" + ", ".join(hits) +
            "）超出普通 agent 任务所需，违背最小代理/最小权限原则，需人工复核意图",
            fp, content[:120])

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1
    summary = {"least_agency_findings": len(findings), "severity_counts": sev_c,
               "files_scanned": len(files), "note": "最小代理/能力过度声明审计（ASI02/ASI10）"}
    return {"findings": findings, "summary": summary}
