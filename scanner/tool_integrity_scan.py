# -*- coding: utf-8 -*-
"""
工具名碰撞 / typosquat 检测 + Rug-pull / 版本漂移 / 工具定义突变检测（供应链 · 工具身份）

背景：
- CVE-2026-30856（腾讯 WeKnora）：恶意远程 MCP server 借 mcp_{service}_{tool} 歧义命名重写
  tavily_extract，劫持工具执行（CVSS 5.9）。工具名不是身份，是"任何人都能印的标签"。
- Cross-server shadowing（GitHub MCP 事件）：被毒 server 诱导 agent 在已授权 server 上调用工具。
- Rug-pull：Canopii 2026-06 审计 11,524 个 MCP server，184 个发布后偷偷改工具定义；MCP spec
  加 tools/list_changed 但客户端执行不一。专家公认"唯一能便宜彻底关掉的 stage =
  哈希锁定工具描述、每次调用复检"。

检测（纯本地、不联网、不 spawn）：
- 工具名近距碰撞：同 workspace 内两个 server 的 name 归一化后编辑距离≤2 → 混淆副手/影子。
- 已知良性生态名仿冒：工具名与内置权威名归一化编辑距离≤2 但非一致 → typosquat。
- Rug-pull 风险：远程 MCP config 未 pin 版本（缺 version/pinned）+ skill 含自更新/拉取最新/
  postinstall 管道执行指令 → 工具定义可被静默变更。
"""

import json
import re

_OWASP_COLLISION = "MCP02"   # 混淆副手 / 权限滥用
_OWASP_RUG = "MCP04"         # 供应链 / 后发布变更

_CANONICAL = [
    "github", "gitlab", "tavily", "openai", "anthropic", "claude", "cursor",
    "browseruse", "paperclip", "openclaw", "clawhub", "notion", "slack",
    "google", "youtube", "spotify", "figma", "postgres", "mysql", "redis",
    "filesystem", "fetch", "brave", "sqlite", "aws", "gcp", "azure",
]


def _norm(s):
    s = (s or "").lower()
    s = re.sub(r"[\s_\-\.]+", "", s)
    s = re.sub(r"(ai|pro|official|headless|app|plus|cloud|hq|dev|api|bot)$", "", s)
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


def _extract_names(files):
    names = []
    for fp, content in files.items():
        if not isinstance(content, str):
            continue
        if "<mcp-config>" in fp or fp.endswith(".json") or "mcp" in fp.lower():
            try:
                data = json.loads(content)
            except Exception:
                continue
            n = data.get("name") if isinstance(data, dict) else None
            if n:
                names.append((str(n), fp))
    return names


def tool_integrity_analysis(files):
    findings = []
    seen = set()

    def add(ftype, sev, desc, filepath, evidence, category):
        key = f"{ftype}:{desc}:{filepath}"
        if key in seen:
            return
        seen.add(key)
        findings.append({
            "type": ftype, "severity": sev, "description": desc,
            "file": filepath, "evidence": evidence[:140], "owasp_category": category,
        })

    names = _extract_names(files)

    # 近距碰撞（同 workspace 多 name）
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, fa = names[i]
            b, fb = names[j]
            na, nb = _norm(a), _norm(b)
            if not na or not nb or na == nb:
                continue
            d = _lev(na, nb)
            if d <= 2 and abs(len(na) - len(nb)) <= 3:
                add("tool_name_collision", "high",
                    f"工具名近距碰撞：`{a}` 与 `{b}` 归一化编辑距离 {d}，疑似混淆副手/影子工具（CVE-2026-30856 类）",
                    fa, f"{a} ~ {b}", _OWASP_COLLISION)

    # 已知良性名仿冒
    for nm, fp in names:
        nn = _norm(nm)
        if not nn:
            continue
        for canon in _CANONICAL:
            if nn == canon:
                continue
            d = _lev(nn, canon)
            if 1 <= d <= 2 and abs(len(nn) - len(canon)) <= 3:
                add("tool_name_typosquat", "high",
                    f"工具名 `{nm}` 与权威名 `{canon}` 编辑距离 {d}，疑似 typosquat 仿冒（CVE-2026-30856 类）",
                    fp, f"{nm} ~ {canon}", _OWASP_COLLISION)
                break

    # Rug-pull：远程未 pin 版本 + 自更新指令
    _NO_PIN = re.compile(r'"?(version|pinned|pin)"?\s*[:=]', re.I)
    _SELF_UPDATE = re.compile(
        r'(self[\-_ ]?update|fetch\s+(the\s+)?latest|pull\s+(the\s+)?latest|'
        r'update\s+(itself|automatically)|auto[\-_ ]?update|'
        r'postinstall|post_install|curl\s+[^"\n]*\|\s*(sh|bash)|'
        r'wget\s+[^"\n]*\|\s*(sh|bash))', re.I)
    _HAS_URL = re.compile(r'"url"\s*:\s*"https?://', re.I)
    for fp, content in files.items():
        if not isinstance(content, str) or not content.strip():
            continue
        is_cfg = ("<mcp-config>" in fp or fp.endswith(".json")
                  or fp.endswith(".yaml") or fp.endswith(".yml"))
        if is_cfg and _HAS_URL.search(content) and not _NO_PIN.search(content):
            add("mcp_no_version_pin", "medium",
                "远程 MCP server 配置未 pin 版本（缺 version/pinned 字段），工具定义可在后续连接中静默变更（rug-pull 风险）",
                fp, content[:120], _OWASP_RUG)
        if _SELF_UPDATE.search(content):
            add("skill_self_update", "high",
                "含自更新 / 拉取最新 / postinstall 管道执行指令，工具定义或载荷可在安装后静默变更（rug-pull 风险）",
                fp, content[:120], _OWASP_RUG)

    sev = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev[f["severity"]] = sev.get(f["severity"], 0) + 1
    summary = {"tool_integrity_findings": len(findings), "severity_counts": sev,
               "files_scanned": len(files),
               "note": "工具名碰撞/typosquat + rug-pull/版本漂移检测"}
    return {"findings": findings, "summary": summary}
