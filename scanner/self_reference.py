# -*- coding: utf-8 -*-
"""
scanner/self_reference.py — 自指误报允许清单

AIShield 是安全扫描器，也必须能安全地扫描**自己的已发布制品**。但自家制品里
天然含有检测器词汇（index.ts 的工具描述写了"越狱/零宽/exfil"）、演示载荷
（guardrail 示例里被拦截的恶意片段）、只读 preflight（GitHub Action 入口用
subprocess 仅 clone 待扫目标跑只读检查）——这些会被自己的规则命中，形成
"自指误报"，淹没真正的信号。

本模块提供 **(source, file, type) 三元组精确匹配**的允许清单：
  - 命中清单的发现被标注为 self_reference（不再阻断），并保留理由供审计；
  - 未登记的新发现一律照旧暴露 —— 绝不用宽泛的路径白名单掩盖真实问题；
  - 清单是显式数据文件，可评审、可 diff、可留证。

不变量：本模块只做匹配与标注，不做任何执行、不发起网络请求。
"""
from __future__ import annotations

import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWLIST_PATH = os.path.join(REPO_ROOT, "distribution", "self_reference_allowlist.json")

# 允许清单条目的必需字段
_REQUIRED = ("source", "file", "type", "reason")


def _norm(p: str) -> str:
    """规范化路径：统一分隔符、去首尾空白。只剥离开头的 './'，不碰 '.github' 这类点目录。"""
    s = (p or "").replace("\\", "/").strip()
    while s.startswith("./"):
        s = s[2:]
    return s


def load_allowlist(path: str | None = None) -> dict:
    """读允许清单。文件缺失/损坏时返回空清单（绝不因为读不到就放行一切）。"""
    path = path or ALLOWLIST_PATH
    empty = {"version": 0, "entries": [], "index": {}}
    if not os.path.exists(path):
        return empty
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return empty
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        return empty
    index = {}
    for e in data["entries"]:
        if not isinstance(e, dict) or any(not e.get(k) for k in _REQUIRED):
            continue                       # 缺字段的条目直接忽略，不放行
        index[(_norm(e["source"]), _norm(e["file"]), str(e["type"]).strip())] = e
    data["index"] = index
    return data


def match(source: str, finding: dict, allowlist: dict) -> dict | None:
    """返回命中的允许清单条目，未命中返回 None。"""
    key = (_norm(source), _norm(finding.get("file", "")),
           str(finding.get("type", "")).strip())
    return (allowlist.get("index") or {}).get(key)


def split_findings(source: str, findings, allowlist: dict):
    """把发现拆成 (kept, suppressed)。

    kept       —— 未被允许清单覆盖的发现（真正的信号，仍需人工判断/阻断）
    suppressed —— 命中的自指误报，每条形如 {**finding, "self_reference": {reason,...}}
    """
    kept, suppressed = [], []
    for f in findings or []:
        entry = match(source, f, allowlist)
        if entry:
            suppressed.append({**f, "self_reference": {
                "reason": entry.get("reason", ""),
                "allowlist_version": allowlist.get("version", 0)}})
        else:
            kept.append(f)
    return kept, suppressed


def blocking_of(findings, severities=("critical", "high")):
    """从发现里筛出阻断级（默认 critical/high）。"""
    s = set(severities)
    return [f for f in findings or [] if (f.get("severity") or "").lower() in s]
