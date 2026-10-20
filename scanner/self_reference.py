# -*- coding: utf-8 -*-
"""
scanner/self_reference.py — 自指误报允许清单

AIShield 是安全扫描器，也必须能安全地扫描**自己的已发布制品**。但自家制品里
天然含有检测器词汇（index.ts 的工具描述写了"越狱/零宽/exfil"）、演示载荷
（guardrail 示例里被拦截的恶意片段）、只读 preflight（GitHub Action 入口用
subprocess 仅 clone 待扫目标跑只读检查）——这些会被自己的规则命中，形成
"自指误报"，淹没真正的信号。

本模块提供 **(source, file, type) 三元组精确匹配**的允许清单，并支持两种
有界扩展：
  - 目录通配：条目 file 以 `/**` 结尾时，前缀匹配该目录下的任意子路径；
  - 包级匹配：条目带 `package` 字段时，按依赖包名（而非文件路径）判定。

不变量（安全底线）：
  - 命中清单的发现被标注为 self_reference（不再阻断），并保留理由供审计；
  - NEVER_SUPPRESS 中的类型（密钥/凭证/私钥/恶意依赖）**无论如何都不允许被
    抑制**——即便有人误加了对应条目，match() 也直接返回 None（fail-closed）；
  - 未登记的新发现（新路径 / 新类型）一律照旧暴露，绝不用宽泛白名单掩盖真实问题；
  - 清单是显式数据文件，可评审、可 diff、可留证；损坏/缺失即空清单（全部保留）。

本模块只做匹配与标注，不做任何执行、不发起网络请求。
"""
from __future__ import annotations

import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWLIST_PATH = os.path.join(REPO_ROOT, "distribution", "self_reference_allowlist.json")

# 允许清单条目的必需字段
_REQUIRED = ("source", "file", "type", "reason")

# 安全底线：这些类型代表真实高危信号（密钥/凭证/私钥/恶意依赖），
# 一旦被允许清单抑制即等于掩盖真实漏洞。match() 对它们永远返回 None。
NEVER_SUPPRESS = {
    "secret_exposure",
    "secrets_hardcoded",
    "credential_leak",
    "private_key_committed",
    "dangerous_dependency",
}


def _norm(p: str) -> str:
    """规范化路径：统一分隔符、去首尾空白。只剥离开头的 './'，不碰 '.github' 这类点目录。"""
    s = (p or "").replace("\\", "/").strip()
    while s.startswith("./"):
        s = s[2:]
    return s


def load_allowlist(path: str | None = None) -> dict:
    """读允许清单。文件缺失/损坏时返回空清单（绝不因为读不到就放行一切）。

    每条有效条目会被赋予稳定 `_id`（e{索引}），供消噪命中统计与腐烂检测使用。
    """
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
    kept = []
    for i, e in enumerate(data.get("entries", [])):
        if not isinstance(e, dict) or any(not e.get(k) for k in _REQUIRED):
            continue                       # 缺字段的条目直接忽略，不放行
        e = dict(e)
        e["_id"] = "e%d" % i
        index[e["_id"]] = e
        kept.append(e)
    data["entries"] = kept
    data["index"] = index
    return data


def match(source: str, finding: dict, allowlist: dict) -> dict | None:
    """返回命中的允许清单条目，未命中返回 None。

    匹配顺序：
      1. 安全底线：NEVER_SUPPRESS 类型一律不抑制（即便清单有对应条目）；
      2. 类型 + 源必须一致；
      3. 包级条目（带 package）按依赖包名匹配；
      4. 目录通配条目（file 以 /** 结尾）按路径前缀匹配；
      5. 否则按精确文件路径匹配。
    """
    ftype = str(finding.get("type", "")).strip()
    if ftype in NEVER_SUPPRESS:
        return None
    src = _norm(source)
    ffile = _norm(finding.get("file", ""))
    pkg = finding.get("package")
    for e in allowlist.get("entries", []):
        if not isinstance(e, dict):
            continue
        if str(e.get("type", "")).strip() != ftype:
            continue
        if _norm(e.get("source", "")) != src:
            continue
        # 包级匹配：按依赖包名判定（dangerous_dependency 等类型使用）
        epkg = e.get("package")
        if epkg:
            if pkg and _norm(str(pkg)) == _norm(str(epkg)):
                return e
            continue
        ef = _norm(e.get("file", ""))
        # 目录通配：file 以 /** 结尾时，前缀匹配该目录下的任意子路径
        if ef.endswith("/**"):
            prefix = ef[:-3].rstrip("/")
            if ffile == prefix or ffile.startswith(prefix + "/"):
                return e
            continue
        if ef == ffile:
            return e
    return None


def split_findings(source: str, findings, allowlist: dict, used_ids: set | None = None):
    """把发现拆成 (kept, suppressed)。

    kept       —— 未被允许清单覆盖的发现（真正的信号，仍需人工判断/阻断）
    suppressed —— 命中的自指误报，每条形如 {**finding, "self_reference": {...}}
    used_ids   —— 可选集合，写入本次被命中条目的 _id，供腐烂检测使用
    """
    kept, suppressed = [], []
    for f in findings or []:
        entry = match(source, f, allowlist)
        if entry:
            suppressed.append({**f, "self_reference": {
                "reason": entry.get("reason", ""),
                "allowlist_version": allowlist.get("version", 0),
                "entry_id": entry.get("_id"),
            }})
            if used_ids is not None:
                used_ids.add(entry.get("_id"))
        else:
            kept.append(f)
    return kept, suppressed


def blocking_of(findings, severities=("critical", "high")):
    """从发现里筛出阻断级（默认 critical/high）。"""
    s = set(severities)
    return [f for f in findings or [] if (f.get("severity") or "").lower() in s]
