# -*- coding: utf-8 -*-
"""
来源 / SLSA / 签名 / 完整性校验检测（供应链 · 来源可信）

背景：92% MCP 包无任何组织验证信号（Island 报告）；供应链攻击靠"来源不可验证"。
检测（纯本地，排除 MCP server config 的命令字段以避免误报）：
- 未 pin 版本安装：npx <pkg> / pip install <pkg> 无 ==version / @version（在 skill/脚本上下文）。
- 从 git URL 安装无 commit pin：git+https://... 无 @<sha>。
- 锁定文件缺 integrity：package-lock/requirements 等含包但无 sha/integrity。
- SBOM 引用但无签名/attestation 标记。
"""

import re

_OWASP = "MCP04"

_NPX_NOPIN = re.compile(r'\bnpx\s+([@A-Za-z0-9/_-]+)([\s`"\.\):]|$)', re.I)
_PIP_NOPIN = re.compile(r'\bpip\s+install\s+([A-Za-z0-9._-]+)([\s`"\.\):]|$)', re.I)
_GIT_NOPIN = re.compile(r'git\+https?://[^\s"\']+?(?!@[\da-f]{7,})', re.I)
_INTEGRITY_OK = re.compile(r'(integrity|sha256|sha512|"integrity"|\bsha\d+\s*[:=])', re.I)


def provenance_analysis(files):
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
        low = fp.lower()
        # MCP server config 的命令字段不是"安装来源"语义，跳过 pin 检查以免误报
        if "<mcp-config>" in fp:
            continue
        is_install_ctx = ("skill" in low or low.endswith((".md", ".txt", ".sh", ".ps1", ".yaml", ".yml")))
        is_lock = any(k in low for k in ("package-lock", "requirements", "poetry.lock",
                                        "pipfile.lock", "yarn.lock", "pnpm-lock"))

        if is_lock:
            if re.search(r'(npm|pip|package|"version"|name\s*:)', content) and not _INTEGRITY_OK.search(content):
                add("lockfile_no_integrity", "medium",
                    "依赖锁定文件缺少完整性校验（integrity/sha），无法验证包未被篡改（SLSA 来源可信缺口）",
                    fp, content[:120])

        if is_install_ctx:
            for m in _NPX_NOPIN.finditer(content):
                pkg = m.group(1)
                if "@" not in pkg and "/" not in pkg.replace("@", "", 1):
                    add("npx_no_version_pin", "low",
                        f"`npx {pkg}` 未指定版本，可能拉取被劫持的最新版本（来源不可验证）",
                        fp, m.group(0)[:120])
            for m in _PIP_NOPIN.finditer(content):
                pkg = m.group(1)
                if "==" not in pkg and "[" not in pkg and "@" not in pkg:
                    add("pip_no_version_pin", "low",
                        f"`pip install {pkg}` 未 pin 版本，来源不可验证",
                        fp, m.group(0)[:120])
            if _GIT_NOPIN.search(content):
                add("git_install_no_commit_pin", "medium",
                    "从 git URL 安装依赖但未 pin commit SHA，仓库被篡改将影响下游（来源不可验证）",
                    fp, content[:120])

        if re.search(r'(sbom|software\s*bill)', content, re.I) and not re.search(
                r'(signature|signed|attest|cosign|in-toto)', content, re.I):
            add("sbom_unsigned", "low",
                "SBOM 引用但未见签名/attestation 标记，无法验证物料清单完整性",
                fp, content[:120])

    sev = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev[f["severity"]] = sev.get(f["severity"], 0) + 1
    summary = {"provenance_findings": len(findings), "severity_counts": sev,
               "files_scanned": len(files), "note": "来源/SLSA/签名/完整性校验"}
    return {"findings": findings, "summary": summary}
