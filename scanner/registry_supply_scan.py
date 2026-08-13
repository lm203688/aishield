# -*- coding: utf-8 -*-
"""
注册表层 typosquat + 出站意图 + 渐进式发现隐藏载荷检测（供应链）

背景：
- ClawHavoc（2026-02）：1,184 恶意 Skill，仿冒 Google Assistant Pro / YouTube Summarize Pro，
  双层投递（Markdown 窃取 SSH key + 嵌入 shell 部署 AMOS）。
- Zenity BlackHat 2026：skills.sh 仿冒 Paperclip / Browser Use，1.7M 安装，凭据窃取；
  恶意命令藏在 setup-installation.md 二级文档（渐进式发现），主文件保持良性。
- 腾讯 SRC 扫 5 万 Skill，74.6% 声明联网。

检测（纯本地）：仅对 skill/agent 风格文件（避免误判 MCP server config）：
- Skill/包名 typosquat：名与内置权威生态名近距（≤2）且非一致 → 仿冒。
- 出站意图 / 外传通道：声明 outbound POST/上传到外部 host，或 curl/wget/requests.post 到外域。
- 渐进式发现隐藏载荷：主文件指示读取二级文档（references/setup*.md），该文档含安装/克隆/执行命令。
"""

import re

_OWASP = "MCP04"

_BRAND = [
    "paperclip", "browseruse", "browser-use", "openclaw", "clawhub", "claude", "cursor",
    "github", "gitlab", "notion", "slack", "openai", "anthropic", "youtube", "googledocs",
    "google", "spotify", "figma", "tavily", "postman", "vercel", "supabase", "airtable",
]


def _norm(s):
    s = (s or "").lower()
    s = re.sub(r"[\s_\-\.]+", "", s)
    s = re.sub(r"(ai|pro|official|headless|app|plus|cloud|hq|dev|api|bot|helper|tool)$", "", s)
    return s


def _lev(a, b):
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


_NAME_RE = re.compile(r'(?:name|title)\s*[:=]\s*["\']?([A-Za-z0-9 _\-\.]{4,}?)["\']?\s*$', re.M)
_EGRESS = re.compile(
    r'(https?://[a-z0-9.\-]+\.[a-z]{2,}[^\s"\']*|'
    r'(curl|wget|requests\.post|fetch|http\.post|axios\.post)\s*\([^)]*https?://|'
    r'(send|upload|exfil|post|transmit|beacon)\s+(the\s+)?(data|file|key|secret|result|output)\s+(to|over))', re.I)
_PROGRESSIVE = re.compile(
    r'(read|open|see|refer\s+to|check\s+out)\s+[`"\']?([\w./\-]*?(setup|install|references?|installation)[\w./\-]*?\.(md|txt|yaml|yml|sh|ps1))[`"\']?', re.I)
_INSTALL_CMD = re.compile(
    r'(git\s+clone|npm\s+(install|i)\s+|pip\s+install|curl\s+.+\|\s*(sh|bash)|'
    r'wget\s+.+\|\s*(sh|bash)|npx\s+[^\s]+\s+install|pnpm\s+(add|install)|'
    r'bun\s+install|sh\s+[\w./\-]+\.sh)', re.I)


def registry_supply_analysis(files):
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
        # 仅对 skill/agent 风格文件检测（排除 MCP server config）
        if "<mcp-config>" in fp:
            continue
        is_skill = ("skill" in fp.lower()
                    or fp.lower().endswith((".md", ".txt", ".yaml", ".yml")))
        if not is_skill:
            continue

        # 1) 名 typosquat
        for m in _NAME_RE.finditer(content):
            nm = m.group(1).strip()
            nn = _norm(nm)
            if len(nn) < 4:
                continue
            for brand in _BRAND:
                if nn == brand:
                    continue
                d = _lev(nn, brand)
                if 1 <= d <= 2 and abs(len(nn) - len(brand)) <= 3:
                    add("skill_name_typosquat", "high",
                        f"Skill/包名 `{nm}` 与权威生态品牌 `{brand}` 编辑距离 {d}，疑似 typosquat 仿冒（ClawHavoc/Zenity 类）",
                        fp, nm)
                    break

        # 2) 出站意图 / 外传
        if _EGRESS.search(content):
            add("suspicious_egress", "medium",
                "检测到出站网络意图 / 外传通道（POST/上传到外部 host 或 curl/wget 到外域），skill 声明联网需复核是否越权外传",
                fp, content[:120])

        # 3) 渐进式发现隐藏载荷
        pm = _PROGRESSIVE.search(content)
        if pm:
            ref = pm.group(2)
            for fp2, c2 in files.items():
                if ref in fp2 and isinstance(c2, str) and _INSTALL_CMD.search(c2):
                    add("progressive_hidden_payload", "high",
                        f"主文件指示读取二级文档 `{ref}`，该文档含安装/克隆/执行命令（渐进式发现隐藏载荷，Zenity BlackHat 类）",
                        fp, ref)
                    break

    sev = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev[f["severity"]] = sev.get(f["severity"], 0) + 1
    summary = {"registry_supply_findings": len(findings), "severity_counts": sev,
               "files_scanned": len(files),
               "note": "注册表 typosquat + 出站意图 + 渐进式发现隐藏载荷"}
    return {"findings": findings, "summary": summary}
