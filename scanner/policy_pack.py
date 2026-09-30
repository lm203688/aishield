# -*- coding: utf-8 -*-
"""
AIShield · Policy Packs
========================

参考 agentshield / Semgrep 的 policy pack 模式，为企业/团队/场景提供
预设安全策略。每个 pack 定义：

* severity_min     —— 报告的最小 severity（默认 "info"，即全部）
* fail_on          —— CI 中触发失败的最低 severity（默认 "critical"）
* excluded_categories —— 跳过的 OWASP 类别列表（默认空）
* excluded_files   —— 跳过扫描的文件 glob 模式列表（默认空）
* required_categories —— 只报告这些类别（默认空 = 全部）
* recommended_actions —— 附加操作建议（默认空）
* context          —— 给调用者的场景说明

使用方式：
    from scanner.policy_pack import load_pack, apply_pack
    pack = load_pack("strict")
    result = apply_pack(report, pack)   # result["pass"] == False → CI fail

设计纪律
--------
* 纯配置，不改扫描逻辑。apply_pack 只是对 findings 做过滤 + 判定，
  扫描引擎本身不动。
* 零依赖，标准库。
* 默认 pack（default）行为等价于"不做过滤"，保证向后兼容。
"""
import json
import os
import fnmatch
from typing import Dict, List, Any

_PACKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "policy_packs")

# severity 顺序（越大越严重）
_SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def load_pack(name: str) -> Dict[str, Any]:
    """按名称加载策略包。未找到抛 KeyError。"""
    path = os.path.join(_PACKS_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise KeyError(f"policy pack not found: {name} (looked in {_PACKS_DIR})")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_packs() -> List[str]:
    """列出所有可用 pack 名。"""
    return sorted(
        os.path.splitext(fn)[0]
        for fn in os.listdir(_PACKS_DIR)
        if fn.endswith(".json")
    )


def _severity_rank(sev: str) -> int:
    return _SEVERITY_ORDER.get(sev, -1)


def apply_pack(report: Dict[str, Any], pack: Dict[str, Any]) -> Dict[str, Any]:
    """对扫描报告应用策略包，返回过滤后的报告 + 是否通过。

    输入 report 结构：
        {
            "findings": [{"type": ..., "severity": ..., "owasp_category": ..., "file": ...}],
            ...其他字段保留
        }

    返回结构（新增字段）：
        {
            "findings": [过滤后],          # 只保留通过 severity_min 和类别过滤的
            "pack": pack["name"],           # 用的哪个 pack
            "pass": bool,                   # CI 判定：True 表示通过
            "summary": {...}                # 过滤统计
        }
    """
    config = pack.get("config", {})
    severity_min = config.get("severity_min", "info")
    fail_on = config.get("fail_on", "critical")
    excluded_cats = set(config.get("excluded_categories", []))
    required_cats = set(config.get("required_categories", []))
    excluded_files = config.get("excluded_files", [])

    original_findings = report.get("findings", [])
    filtered = []
    skipped_severity = 0
    skipped_category = 0
    skipped_file = 0

    for f in original_findings:
        sev = f.get("severity", "info")
        cat = f.get("owasp_category", "")
        fp = f.get("file", "")

        if _severity_rank(sev) < _severity_rank(severity_min):
            skipped_severity += 1
            continue
        if excluded_cats and cat in excluded_cats:
            skipped_category += 1
            continue
        if required_cats and cat not in required_cats:
            skipped_category += 1
            continue
        if excluded_files and _match_any(fp, excluded_files):
            skipped_file += 1
            continue

        filtered.append(f)

    # CI 判定：任何 severity >= fail_on 的 finding 都触发 fail
    # fail_on="off"/"impossible" 表示永不 fail（红队模式）
    if fail_on in ("off", "impossible"):
        triggered = []
        passed = True
    else:
        fail_rank = _severity_rank(fail_on)
        if fail_rank < 0:
            # 未知 severity，保守视作永不 fail
            triggered = []
            passed = True
        else:
            triggered = [
                f for f in filtered
                if _severity_rank(f.get("severity", "info")) >= fail_rank
            ]
            passed = len(triggered) == 0

    result = dict(report)
    result["findings"] = filtered
    result["pack"] = pack.get("name", "?")
    result["pass"] = passed
    result["summary"] = {
        **report.get("summary", {}),
        "pack": pack.get("name", "?"),
        "original_findings": len(original_findings),
        "filtered_findings": len(filtered),
        "skipped_by_severity": skipped_severity,
        "skipped_by_category": skipped_category,
        "skipped_by_file": skipped_file,
        "fail_on": fail_on,
        "triggered_findings": len(triggered),
    }
    return result


def _match_any(filepath: str, patterns: List[str]) -> bool:
    """filepath 是否匹配任一 glob 模式（简单实现：无通配的 basename 匹配）。"""
    if not filepath:
        return False
    basename = os.path.basename(filepath)
    for pat in patterns:
        if fnmatch.fnmatch(basename, pat) or fnmatch.fnmatch(filepath, pat):
            return True
    return False


# ── 内置 pack 定义（同步到 scanner/policy_packs/*.json）────────────────────

DEFAULT_PACK = {
    "name": "default",
    "description": "平衡策略：报告全部 severity，CI 只对 critical 触发失败。",
    "context": "AIShield 默认策略。适合绝大多数场景。",
    "config": {
        "severity_min": "info",
        "fail_on": "critical",
        "excluded_categories": [],
        "required_categories": [],
        "excluded_files": [],
    },
}

STRICT_PACK = {
    "name": "strict",
    "description": "严格策略：任何 medium 及以上都触发 CI 失败。适合生产 MCP 部署前审查。",
    "context": "生产部署前必须用。宁严勿松。",
    "config": {
        "severity_min": "low",
        "fail_on": "medium",
        "excluded_categories": [],
        "required_categories": [],
        "excluded_files": [],
    },
}

MCP_ONLY_PACK = {
    "name": "mcp-only",
    "description": "MCP 服务专用：只关心 MCP01-MCP10，忽略 agent 生态特有的类别。",
    "context": "扫描 MCP 服务器配置和代码。",
    "config": {
        "severity_min": "info",
        "fail_on": "high",
        "excluded_categories": [
            "ASI01", "ASI02", "ASI03", "ASI04", "ASI05",
            "ASI06", "ASI07", "ASI08", "ASI09", "ASI10",
        ],
        "required_categories": [
            "MCP01", "MCP02", "MCP03", "MCP04", "MCP05",
            "MCP06", "MCP07", "MCP08", "MCP09", "MCP10",
        ],
        "excluded_files": [],
    },
}

PERSONAL_AGENT_PACK = {
    "name": "personal-agent",
    "description": "个人 Agent 治理层：关注身份/工具/记忆，忽略供应链（个人用户不装第三方包）。",
    "context": "AIShield 个人 Agent 治理层预设，用于 eco/personal_agent.py 相关扫描。",
    "config": {
        "severity_min": "low",
        "fail_on": "high",
        "excluded_categories": ["MCP04"],
        "required_categories": [
            "MCP01", "MCP02", "MCP03", "MCP05", "MCP06", "MCP07",
            "ASI01", "ASI04", "ASI05", "ASI06", "ASI07",
        ],
        "excluded_files": [],
    },
}

RED_TEAM_PACK = {
    "name": "red-team",
    "description": "红队模式：不阻塞任何 finding，只报告全部作为观察。",
    "context": "红队扫描不应 fail，所有结果都是观察信号。",
    "config": {
        "severity_min": "info",
        "fail_on": "impossible",  # 永不成真
        "excluded_categories": [],
        "required_categories": [],
        "excluded_files": [],
    },
}


# ── 写入 pack JSON 文件（幂等）────────────────────────────────────────────
def write_builtin_packs() -> List[str]:
    """把内置 pack 写到 _PACKS_DIR（幂等）。返回写入的文件名列表。"""
    os.makedirs(_PACKS_DIR, exist_ok=True)
    written = []
    for pack in [DEFAULT_PACK, STRICT_PACK, MCP_ONLY_PACK,
                 PERSONAL_AGENT_PACK, RED_TEAM_PACK]:
        path = os.path.join(_PACKS_DIR, f"{pack['name']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(pack, f, indent=2, ensure_ascii=False)
        written.append(path)
    return written


# 首次导入时自动写出内置 pack（幂等）
if os.path.isdir(_PACKS_DIR) and not os.listdir(_PACKS_DIR):
    write_builtin_packs()

__all__ = [
    "load_pack",
    "list_packs",
    "apply_pack",
    "write_builtin_packs",
    "DEFAULT_PACK",
    "STRICT_PACK",
    "MCP_ONLY_PACK",
    "PERSONAL_AGENT_PACK",
    "RED_TEAM_PACK",
]
