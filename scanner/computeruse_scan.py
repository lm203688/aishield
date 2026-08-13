# -*- coding: utf-8 -*-
"""
Computer-use / 浏览器不可逆动作风险检测（agent 计算机内容安全平面 · 差异化空白位）

背景：Operator / Claude Computer Use 兴起，agent 直接操作 UI/OS。不可逆 UI 动作（下载运行/
点击放行/关安全）无确认即执行，是"agent 计算机内容安全平面"的核心风险面。
风险：指示 agent 执行不可逆、无确认、削弱本机的动作。

检测（纯本地，强信号）：
- 下载并运行 / 执行下载的文件。
- 关闭/绕过安全机制（防火墙/杀软/警告/权限弹窗）。
- 高危 OS 动作：以管理员运行 / 修改注册表 / 删除系统文件 / 提权。
- 浏览器提交：填表并提交 / 接受 cookie 继续 / 自动授权。

每个正则的每个分支都是独立平衡的 (...) 组，顶层用 | 连接，避免括号不匹配。
"""

import re

_OWASP = "MCP05"   # 非预期动作 / 越权执行

_DOWNLOAD_RUN = re.compile(
    r'(download\s+(and|then)\s+(run|execute|install))|'
    r'((run|execute|launch)\s+(the\s+)?(downloaded|installer|setup)\s+(file|package))|'
    r'((下载|执行)\s*(并|后)?\s*(运行|安装)\s*(下载的|安装包|文件))', re.I)

_DISABLE_SEC = re.compile(
    r'((disable|turn\s+off|turn\s+of|deactivate|bypass)\s+(the\s+)?'
    r'(firewall|antivirus|security\s+(software|feature|warning)|protection|defender|uac|gatekeeper|sip))|'
    r'((关闭|禁用|绕过)\s*(防火墙|杀毒|杀软|安全(软件|警告|防护|机制)))', re.I)

_DISMISS_WARN = re.compile(
    r'((dismiss|ignore|bypass|skip)\s+(the\s+)?(security\s+)?(warning|alert|prompt|dialog))|'
    r'((忽略|绕过|跳过)\s*(安全)?(警告|弹窗|提示|确认))', re.I)

_OS_DANGER = re.compile(
    r'(run\s+as\s+administrator)|(run\s+with\s+admin)|(sudo\s+)|'
    r'((modify|edit|delete)\s+(the\s+)?(registry|system\s+file))|'
    r'((grant|give)\s+(yourself|full|all)\s+(permissions|access))|'
    r'(以管理员)|(提权)|(修改注册表)|(删除系统文件)|(授予全部权限)', re.I)

_BROWSER_SUBMIT = re.compile(
    r'((fill\s+(the\s+)?(form|fields?)\s+and\s+(submit|send)))|'
    r'((accept|click)\s+(the\s+)?(cookie|consent|allow\s+access|grant\s+permission))|'
    r'((填(写|表)\s*(并)?\s*(提交|发送))|((接受|点击)\s*(cookie|授权|允许访问)))', re.I)


def computeruse_analysis(files):
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
        if _DOWNLOAD_RUN.search(content):
            hits.append("download_and_run")
        if _DISABLE_SEC.search(content):
            hits.append("disable_security")
        if _DISMISS_WARN.search(content):
            hits.append("dismiss_security_warning")
        if _OS_DANGER.search(content):
            hits.append("os_privileged_action")
        if _BROWSER_SUBMIT.search(content):
            hits.append("browser_submit")
        if not hits:
            continue
        # 削弱安全/下载运行/提权 升级 high
        sev = "high" if any(h in hits for h in ("download_and_run", "disable_security", "os_privileged_action")) else "medium"
        add("computer_use_irreversible_action", sev,
            "检测到不可逆/削弱本机的 computer-use 动作指令（" + ", ".join(hits) +
            "）：agent 计算机内容安全平面风险，需确认闸门",
            fp, content[:120])

    sev_c = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_c[f["severity"]] = sev_c.get(f["severity"], 0) + 1
    summary = {"computeruse_findings": len(findings), "severity_counts": sev_c,
               "files_scanned": len(files), "note": "computer-use 不可逆动作风险（内容安全平面）"}
    return {"findings": findings, "summary": summary}
