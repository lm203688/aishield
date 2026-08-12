#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scanner/workspace_scan.py — Pre-flight workspace scan

针对 "给 agent 一台电脑"（forge / agent-forge / forgevm / Open Interpreter /
Goose / Claude Desktop / Cursor 等）平台的启动前安全扫描。

核心不变量（与 AIShield 全局一致）：
  1. **绝不 spawn** 配置中出现的任何命令/URL —— 只读 + 静态解析。
  2. **不联网抓取**（除非调用方显式 enable_osv）—— 不发起 SSRF。
  3. **复用现有引擎**（rules_analyze + dependency + secrets + poisoning +
     taint + identity_scan + network_scan + calculate_scores），不写重复逻辑，
     新增的 identity/network 模块为保守启发式，零新增误报面。

用法：
    from scanner.workspace_scan import preflight
    report = preflight("/path/to/agent/workspace")
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from .rules import analyze as rules_analyze
from .engine import (
    calculate_scores,
    dependency_analysis,
    generate_recommendations,
    secrets_detection,
    taint_analysis,
    tool_poisoning_detection,
)
from .identity_scan import identity_analysis
from .network_scan import network_analysis
from .agentcard_scan import agentcard_analysis
from .authentik_scan import authentik_analysis
from .slop_scan import slop_analysis
from .payment_scan import payment_analysis

TZ = timezone(timedelta(hours=8))
SCANNER_VERSION = "4.0-preflight.2"

# 安全护栏：避免误读巨型 workspace
MAX_FILE_BYTES = 512 * 1024          # 单文件 512KB 上限
MAX_FILES_PER_SCAN = 200            # 总文件数上限
MAX_WALK_DEPTH = 8                  # 递归深度上限
MAX_SKILL_FILES = 50                # skill 文件数上限
SKIP_DIR_NAMES = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", "target", ".next", ".cache", ".tox",
    ".mypy_cache", ".pytest_cache", ".ruff_cache",
}

# 平台识别标记（路径 -> 友好名）
PLATFORM_MARKERS = [
    # (path_glob_or_name, platform_id, display)
    (".mcp.json",                  "claude_desktop",  "Claude Desktop / 通用 MCP"),
    (".cursor/mcp.json",           "cursor",          "Cursor"),
    (".vscode/mcp.json",           "vscode",          "VS Code"),
    (".claude",                    "claude_code",     "Claude Code"),
    ("forge.yaml",                 "forge",           "forge (micha3lbrown)"),
    ("forge.yml",                  "forge",           "forge (micha3lbrown)"),
    (".openinterpreter",           "open_interpreter", "Open Interpreter"),
    (".goose",                     "goose",           "Goose (Block/LF)"),
    ("SKILL.md",                   "agent_skills",    "Agent Skills (通用)"),
]


# ============================================================================
# 平台检测
# ============================================================================

def detect_platforms(workspace_dir):
    """检测 workspace 里有哪几个 agent 平台的配置文件。

    Returns: { platform_id: { "display": str, "configs": [rel_path, ...] } }
    """
    root = Path(workspace_dir).resolve()
    if not root.exists() or not root.is_dir():
        return {}

    out = {}
    for marker, pid, display in PLATFORM_MARKERS:
        if marker.startswith(".") or marker.endswith(".md") or marker.endswith(".yaml") or marker.endswith(".yml") or marker.endswith(".json"):
            # 文件标记
            hits = []
            for p in root.rglob(marker):
                # 深度限制
                try:
                    rel = p.relative_to(root)
                    if len(rel.parts) > MAX_WALK_DEPTH:
                        continue
                    if any(part in SKIP_DIR_NAMES for part in rel.parts[:-1]):
                        continue
                except ValueError:
                    continue
                hits.append(str(p.relative_to(root)).replace("\\", "/"))
            if hits:
                out.setdefault(pid, {"display": display, "configs": []})
                out[pid]["configs"].extend(sorted(set(hits)))
        else:
            # 目录标记
            d = root / marker
            if d.exists() and d.is_dir():
                out.setdefault(pid, {"display": display, "configs": []})
                out[pid]["configs"].append(marker + "/")
    return out


# ============================================================================
# Config 解析器（不执行，纯文本解析）
# ============================================================================

def parse_mcp_json(path):
    """解析 .mcp.json / .cursor/mcp.json / .vscode/mcp.json。

    支持两种主流 schema：
      A) { "mcpServers": { "<name>": { "command":..., "args":[...], "env":{...}, "url":... } } }
      B) { "servers": [ { "name":..., "command":..., "args":[...] }, ... ] }
    """
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        if not raw.strip():
            return out
        data = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return out

    # Schema A
    servers = data.get("mcpServers") or data.get("mcp_servers") or data.get("servers")
    if isinstance(servers, dict):
        for name, cfg in servers.items():
            if not isinstance(cfg, dict):
                continue
            out.append({
                "name": str(name),
                "command": cfg.get("command", ""),
                "args": list(cfg.get("args", []) or []),
                "env": dict(cfg.get("env", {}) or {}),
                "url": cfg.get("url", ""),
                "transport": cfg.get("transport", "stdio" if cfg.get("command") else "http"),
                "source_file": str(path),
                "schema": "A",
            })
    # Schema B
    if isinstance(servers, list):
        for i, cfg in enumerate(servers):
            if not isinstance(cfg, dict):
                continue
            out.append({
                "name": str(cfg.get("name", f"server-{i}")),
                "command": cfg.get("command", ""),
                "args": list(cfg.get("args", []) or []),
                "env": dict(cfg.get("env", {}) or {}),
                "url": cfg.get("url", ""),
                "transport": cfg.get("transport", "stdio" if cfg.get("command") else "http"),
                "source_file": str(path),
                "schema": "B",
            })
    return out


def parse_forge_yaml(path):
    """容错的 forge.yaml 抽取器。

    不依赖 PyYAML（零依赖约束）。只关心风险信号：command / args / script / url。
    结构容差：top-level list、`tools:` list、`mcp_servers:` dict/list。
    """
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except OSError:
        return out

    # 找出每个条目：name + command + args + script + url
    # 容错策略：直接行级 regex 抽取 name/command/args/script/url，宽松归并。
    lines = raw.splitlines()
    item_re = re.compile(r"^\s*-\s*(.+)$")
    field_re = re.compile(r"^\s{4,}([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")

    name = ""
    command = ""
    args = []
    script = ""
    url = ""
    _in_args = False

    def flush():
        nonlocal name, command, args, script, url, _in_args
        if name or command or args or script or url:
            out.append({
                "name": name or "unnamed",
                "command": command,
                "args": args,
                "script": script,
                "url": url,
                "source_file": str(path),
            })
        name = ""
        command = ""
        args = []
        script = ""
        url = ""
        _in_args = False

    for line in lines:
        s = line.rstrip()
        if not s or s.lstrip().startswith("#"):
            continue
        # 新条目起点（顶层列表项）
        if item_re.match(s):
            # 仅当我们已经在某个顶层列表里
            indent = len(s) - len(s.lstrip())
            if indent == 2:  # "  - name: x" 形式
                flush()
                # 同行字段（field_re 要求 4 空格缩进，"  - key: val" 不会被它捕获，故在此手动处理）
                rest = s[4:]
                if ":" in rest:
                    k, _, v = rest.partition(":")
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k == "name":
                        name = v
                    elif k == "command":
                        command = v
                    elif k == "script":
                        script = v
                    elif k == "url":
                        url = v
                    elif k == "args":
                        _in_args = True
                continue   # 只对顶层条目 continue；子列表项 fall-through 到下面 args 分支
        # 字段行
        m = field_re.match(s)
        if m:
            k = m.group(1)
            v = m.group(2).strip()
            if k == "name":
                name = v.strip('"').strip("'")
            elif k == "command":
                command = v.strip('"').strip("'")
            elif k == "script":
                script = v.strip('"').strip("'")
            elif k == "url":
                url = v.strip('"').strip("'")
            elif k == "args":
                _in_args = True
                # 可能是 inline list 或后续多行
                if v.startswith("[") and v.endswith("]"):
                    inner = v[1:-1].strip()
                    if inner:
                        args = [a.strip().strip('"').strip("'") for a in inner.split(",")]
                # 否则留待下面 - 行处理
        elif _in_args and s.lstrip().startswith("- "):
            # args: 之下的列表项（只在确认进入 args 上下文后才追加）
            stripped_l = s.lstrip()
            args.append(stripped_l[2:].strip().strip('"').strip("'"))
    flush()
    return out


# ============================================================================
# Skill 文件收集（本地读取，不执行）
# ============================================================================

SKILL_FILE_GLOBS = ["SKILL.md", "skill.md", "skills/*.md", ".claude/skills/*.md"]
SKILL_FILE_MAX_DEPTH = 5


def collect_skill_files(workspace_dir, max_files=MAX_SKILL_FILES):
    """收集 workspace 下的 skill 文件。带深度 + 数量上限，避免巨型树爆炸。"""
    root = Path(workspace_dir).resolve()
    if not root.exists() or not root.is_dir():
        return []

    found = []
    seen = set()
    for glob in SKILL_FILE_GLOBS:
        for p in root.rglob(glob):
            try:
                rel = p.relative_to(root)
                if len(rel.parts) > SKILL_FILE_MAX_DEPTH + 1:
                    continue
                if any(part in SKIP_DIR_NAMES for part in rel.parts[:-1]):
                    continue
            except ValueError:
                continue
            key = str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            try:
                if not p.is_file() or p.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            found.append(p)
            if len(found) >= max_files:
                return sorted(found)
    return sorted(found)


def _read_text(path, max_bytes=MAX_FILE_BYTES):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = f.read(max_bytes + 1)
        if len(data) > max_bytes:
            data = data[:max_bytes] + "\n... [truncated]\n"
        return data
    except OSError:
        return ""


# ============================================================================
# 镜像 engine.scan() 的本地版流水线（不抓 URL / 不 spawn）
# ============================================================================

def _local_pipeline(files, name, tool_type="mcp"):
    """对给定的 {filepath: content} 字典跑完整检测流水线。返回与 engine.scan() 同 shape 的报告子集。"""
    total_files = len(files)
    static = rules_analyze(files, tool_type)
    dependency = dependency_analysis(files)
    secrets = secrets_detection(files)
    poisoning = tool_poisoning_detection(files)
    taint = taint_analysis(files)
    identity = identity_analysis(files)
    network = network_analysis(files)
    agentcard = agentcard_analysis(files)
    authentik = authentik_analysis(files)
    slop = slop_analysis(files)
    payment = payment_analysis(files)
    extra_findings = (identity.get("findings", []) + network.get("findings", [])
                      + agentcard.get("findings", []) + authentik.get("findings", [])
                      + slop.get("findings", []) + payment.get("findings", []))
    scores = calculate_scores(static, dependency, secrets, poisoning, taint, total_files,
                              extra_findings=extra_findings)

    all_findings = []
    for f in static.get("findings", []):
        all_findings.append(f)
    for f in dependency.get("findings", []):
        all_findings.append(f)
    for f in secrets.get("findings", []):
        all_findings.append(f)
    for f in poisoning:
        all_findings.append(f)
    for f in taint:
        all_findings.append(f)
    for f in identity.get("findings", []):
        all_findings.append(f)
    for f in network.get("findings", []):
        all_findings.append(f)
    for f in agentcard.get("findings", []):
        all_findings.append(f)
    for f in authentik.get("findings", []):
        all_findings.append(f)
    for f in slop.get("findings", []):
        all_findings.append(f)
    for f in payment.get("findings", []):
        all_findings.append(f)

    seen = set()
    unique = []
    for f in all_findings:
        k = f"{f.get('type','')}:{f.get('description','')}:{f.get('file','')}"
        if k not in seen:
            seen.add(k)
            unique.append(f)

    recommendations = generate_recommendations(unique, scores)
    return {
        **scores,
        "name": name,
        "tool_type": tool_type,
        "findings": unique,
        "total_findings": len(unique),
        "static_analysis": static,
        "dependency_analysis": dependency,
        "secrets_detection": secrets,
        "tool_poisoning": poisoning,
        "identity_scan": identity,
        "network_scan": network,
        "agentcard_scan": agentcard,
        "authentik_scan": authentik,
        "slop_scan": slop,
        "payment_scan": payment,
        "recommendations": recommendations,
    }


# ============================================================================
# 主入口：preflight
# ============================================================================

def _risk_from_score(score):
    if score is None:
        return "unknown"
    if score >= 80:
        return "low"
    if score >= 60:
        return "medium"
    return "high"


def _overall_assessment(items):
    """基于所有 items 的整体判定。"""
    if not items:
        return "empty"
    high = sum(1 for it in items if it.get("risk_level") == "high")
    medium = sum(1 for it in items if it.get("risk_level") == "medium")
    if high > 0:
        return "danger"
    if medium > 0:
        return "review"
    return "safe"


def _synthesize_mcp_config_files(extracted_servers, skill_files):
    """把解析出来的 MCP server + skill 内容构造成 files 字典喂给引擎。"""
    files = {}
    # MCP server：把每个 server 的 config 序列化为合成文件，让规则引擎扫
    for srv in extracted_servers:
        # 用一个直观的合成文件名（与 AIShield "不执行" 不变量一致 —— 它只是个文本文件）
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", srv.get("name", "unnamed"))[:80]
        synthetic_path = f"<mcp-config>/{safe_name}.mcp.json"
        body = json.dumps({
            "name": srv.get("name"),
            "command": srv.get("command"),
            "args": srv.get("args"),
            "env": srv.get("env"),
            "url": srv.get("url"),
            "transport": srv.get("transport"),
            "source_file": srv.get("source_file"),
        }, ensure_ascii=False, indent=2)
        files[synthetic_path] = body

    # Skill 文件：直接读原文喂入
    for sf in skill_files:
        try:
            rel = sf.name if sf.parent == Path(sf.anchor) else str(sf)
        except Exception:
            rel = sf.name
        files[f"<skill>/{rel}"] = _read_text(sf)
    return files


def preflight(workspace_dir):
    """对给定 workspace 跑启动前安全扫描。

    Returns: dict (pre-flight report)
    """
    root = Path(workspace_dir).resolve()
    if not root.exists() or not root.is_dir():
        return {
            "error": f"workspace not found or not a directory: {workspace_dir}",
            "workspace": str(workspace_dir),
            "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "scanner_version": SCANNER_VERSION,
        }

    platforms = detect_platforms(root)
    skill_files = collect_skill_files(root)

    # 解析各平台 config
    extracted_servers = []
    config_parse_errors = []
    for pid, info in platforms.items():
        for cfg_rel in info.get("configs", []):
            cfg_path = root / cfg_rel
            if not cfg_path.exists():
                continue
            if pid in ("claude_desktop", "cursor", "vscode"):
                srvs = parse_mcp_json(cfg_path)
                for s in srvs:
                    s["platform"] = pid
                    extracted_servers.append(s)
            elif pid == "forge":
                srvs = parse_forge_yaml(cfg_path)
                for s in srvs:
                    s["platform"] = pid
                    extracted_servers.append(s)
            elif pid == "agent_skills":
                pass  # 仅检测，文件已由 collect_skill_files 收集
            else:
                # open_interpreter / goose / claude_code：v1 仅识别 + 收集目录下 SKILL.md
                pass

    # 构造 files 字典 → 跑引擎
    files = _synthesize_mcp_config_files(extracted_servers, skill_files)
    total_files = len(files)
    if total_files > MAX_FILES_PER_SCAN:
        files = dict(list(files.items())[:MAX_FILES_PER_SCAN])

    # 跑整个流水线（一次性，不逐项 split，保留聚合 + 单项详情两路）
    if files:
        full = _local_pipeline(files, name=f"workspace:{root.name}", tool_type="mcp")
    else:
        full = {
            "overall_score": None,
            "risk_level": "unknown",
            "findings": [],
            "total_findings": 0,
            "owasp_coverage": {},
            "agentic_coverage": {},
        }

    # 单项细粒度：把每个 MCP server 与每个 skill 文件分别跑一次（小项）
    per_item = []
    for srv in extracted_servers:
        item_files = {f"<mcp-config>/{re.sub(r'[^A-Za-z0-9_.-]', '_', srv.get('name','unnamed'))[:80]}.mcp.json":
                      files.get(f"<mcp-config>/{re.sub(r'[^A-Za-z0-9_.-]', '_', srv.get('name','unnamed'))[:80]}.mcp.json", "")}
        if not item_files or not list(item_files.values())[0]:
            continue
        rep = _local_pipeline(item_files, name=srv.get("name", "unnamed"), tool_type="mcp")
        per_item.append({
            "kind": "mcp_server",
            "platform": srv.get("platform"),
            "name": srv.get("name"),
            "command": srv.get("command"),
            "args": srv.get("args"),
            "url": srv.get("url"),
            "source_file": srv.get("source_file"),
            "overall_score": rep.get("overall_score"),
            "badge_level": rep.get("badge_level"),
            "risk_level": rep.get("risk_level") or _risk_from_score(rep.get("overall_score")),
            "total_findings": rep.get("total_findings", 0),
            "findings": rep.get("findings", [])[:10],  # 截断，避免巨型
        })

    for sf in skill_files:
        rel = sf.name
        content = _read_text(sf)
        rep = _local_pipeline({f"<skill>/{rel}": content}, name=rel, tool_type="skill")
        per_item.append({
            "kind": "skill",
            "platform": "agent_skills",
            "name": rel,
            "source_file": str(sf.relative_to(root)).replace("\\", "/"),
            "overall_score": rep.get("overall_score"),
            "badge_level": rep.get("badge_level"),
            "risk_level": rep.get("risk_level") or _risk_from_score(rep.get("overall_score")),
            "total_findings": rep.get("total_findings", 0),
            "findings": rep.get("findings", [])[:10],
        })

    items_high = sum(1 for it in per_item if it.get("risk_level") == "high")
    items_medium = sum(1 for it in per_item if it.get("risk_level") == "medium")
    items_low = sum(1 for it in per_item if it.get("risk_level") == "low")

    return {
        "workspace": str(root),
        "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "scanner_version": SCANNER_VERSION,
        "powered_by": "AIShield",
        "platforms_detected": [
            {"platform_id": pid, "display": info["display"], "configs": info["configs"]}
            for pid, info in platforms.items()
        ],
        "summary": {
            "items_total": len(per_item),
            "items_high_risk": items_high,
            "items_medium_risk": items_medium,
            "items_low_risk": items_low,
            "overall_score": full.get("overall_score"),
            "risk_level": full.get("risk_level"),
            "overall_assessment": _overall_assessment(per_item),
            "config_files_parsed": len(extracted_servers) + len(skill_files),
        },
        "items": per_item,
        "aggregate_findings": full.get("findings", [])[:50],
        "aggregate_recommendations": full.get("recommendations", []),
        "owasp_coverage": full.get("owasp_coverage", {}),
        "agentic_coverage": full.get("agentic_coverage", {}),
        # 不变量声明（供门禁测试断言）
        "_invariants": {
            "no_spawn": True,
            "no_remote_fetch": True,
            "engines_reused": ["rules_analyze", "dependency_analysis",
                               "secrets_detection", "tool_poisoning_detection",
                               "taint_analysis", "calculate_scores",
                               "identity_analysis", "network_analysis",
                               "agentcard_analysis", "authentik_analysis",
                               "slop_analysis", "payment_analysis"],
        },
    }


# ============================================================================
# CLI 友好的人类可读输出
# ============================================================================

def render_markdown(report):
    """把 preflight 报告渲染为 markdown（给 CLI 用）。"""
    lines = []
    lines.append(f"# AIShield Pre-flight Report — `{report.get('workspace','?')}`")
    lines.append("")
    lines.append(f"- 扫描时间: `{report.get('scanned_at','')}`")
    lines.append(f"- 引擎版本: `{report.get('scanner_version','')}`")
    s = report.get("summary", {})
    lines.append(f"- 检出平台: **{len(report.get('platforms_detected',[]))}**")
    lines.append(f"- 扫描项总数: **{s.get('items_total',0)}** （高风险 {s.get('items_high_risk',0)} / 中 {s.get('items_medium_risk',0)} / 低 {s.get('items_low_risk',0)}）")
    lines.append(f"- 整体评分: **{s.get('overall_score','N/A')}** / 风险: **{s.get('risk_level','?')}** / 判定: **{s.get('overall_assessment','?')}**")
    lines.append("")
    if report.get("platforms_detected"):
        lines.append("## 检出的平台")
        for p in report["platforms_detected"]:
            lines.append(f"- **{p['display']}** (`{p['platform_id']}`): {', '.join(p['configs'])}")
        lines.append("")
    if report.get("items"):
        lines.append("## 单项明细")
        for it in report["items"]:
            lines.append(f"### {it.get('kind','?')} · `{it.get('name','?')}` — 评分 {it.get('overall_score','N/A')} / {it.get('risk_level','?')}")
            if it.get("command"):
                lines.append(f"- command: `{it.get('command')}`")
            if it.get("args"):
                lines.append(f"- args: {it.get('args')}")
            if it.get("url"):
                lines.append(f"- url: `{it.get('url')}`")
            lines.append(f"- source: `{it.get('source_file','?')}`")
            lines.append(f"- findings: {it.get('total_findings',0)}")
            for f in it.get("findings", [])[:5]:
                lines.append(f"  - `{f.get('severity','?')}` {f.get('type','?')}: {f.get('description','')[:120]}")
            lines.append("")
    if report.get("aggregate_recommendations"):
        lines.append("## 聚合建议")
        for r in report["aggregate_recommendations"][:10]:
            lines.append(f"- {r}")
    inv = report.get("_invariants", {})
    if inv:
        lines.append("")
        lines.append("---")
        lines.append(f"**不变量**：no_spawn={inv.get('no_spawn')} · no_remote_fetch={inv.get('no_remote_fetch')} · 复用引擎={', '.join(inv.get('engines_reused',[]))}")
    return "\n".join(lines) + "\n"