"""
eco/policy_bridge.py — L2 策略贯通：把扫描期 policy pack 编译为运行时 PEP 策略

═══════════════════════════════════════════════════════════════════
  为什么需要这一层（真缺口，不是包装）
═══════════════════════════════════════════════════════════════════
  AIShield 一直有两条互不相通的策略线：

    线 A（扫描期）  scanner/policy_pack.py  的 5 个 pack
                    —— 对「扫描报告」做六维过滤，决定 CI 过不过。
    线 B（运行期）  eco/runtime_governance.py 的 RuntimeGovernor
                    —— 对「每次工具调用」做准入判定，策略写死在 _default_policy()。

  后果是一个真实且隐蔽的缺陷：**同一个 agent，在扫描期按 strict pack 被评判
  「medium 及以上会 fail」，在运行期却按另一套写死的宽松策略被放行**。
  策略只在 CI 那一瞬生效，之后 agent 跑到生产里就没人管了。
  「一次声明、全程生效」做不到。

  本模块把线 A 编译成线 B 能消费的运行时策略，并让每一次运行时拒绝都能
  回溯到 pack 里的具体字段（可解释，不是黑盒）。

═══════════════════════════════════════════════════════════════════
  语义映射（每一条都忠实于 pack 字段，不编造、不放大）
═══════════════════════════════════════════════════════════════════
  运行时网关看到的粒度是 (server, tool)，pack 看到的粒度是
  (category, severity, file)。要贯通必须做语义投影，投影规则如下：

  ┌─ pack 字段 ─────────┬─ 运行时投影 ─────────────────────────────┐
  │ excluded_categories  │ deny_categories  → 运行时**真拒绝**       │
  │                      │ 「明确不关心的类别」= 不该拿到这个权限     │
  ├──────────────────────┼────────────────────────────────────────┤
  │ required_categories  │ allow_categories → 运行时**放行并观察**   │
  │                      │ （不能反过来当白名单硬拒：未来的 MCP11    │
  │                      │   等新类别不在表里，硬拒会误伤生态升级）   │
  ├──────────────────────┼────────────────────────────────────────┤
  │ severity_min         │ severity_floor   → 审计**记录阈值**       │
  │                      │ 低于此严重度的调用只在日志里，不升级告警   │
  ├──────────────────────┼────────────────────────────────────────┤
  │ fail_on              │ strictness       → 档位标签（见下）        │
  │                      │ 仅作可解释标注，**不直接翻成 default_deny**│
  └──────────────────────┴────────────────────────────────────────┘

  为什么 fail_on 不直接翻成 default_deny：
  default_deny=True 会拒绝**一切未知实体**，而 pack 的 fail_on 只是 CI 阈值。
  strict pack 的 excluded/required 都是空的 —— 它的语义是「medium 会 fail」，
  不是「拒绝一切」。直接翻成 default_deny 会让生产 agent 全停，属于典型的
  「表面贯通、实际炸掉」。这里保持 strictness 标注 + severity_floor 收紧，
  并在 ops 需要时由运维显式调用 strict_runtime=True 才会推默认拒绝。

  三档 strictness（运行时真实拒绝行为的旁证）：
      observe     fail_on == "impossible"  → 只观察，永不产生运行时拒绝
      balanced    有 deny_categories 但无默认拒绝
      enforcing   显式 strict_runtime=True 或 fail_on >= medium 且运维确认

═══════════════════════════════════════════════════════════════════
  设计原则（与扫描器同源）
═══════════════════════════════════════════════════════════════════
  - 零第三方依赖、可离线、不外发数据。
  - 编译产物每一项都带 rationale，回溯到 pack 的哪个字段，可审计。
  - 默认不误伤：未知类别（表里没有的）一律放行 + 观察，不猜、不硬拒。
  - 本模块**绝不 spawn 任何被治理的进程**，只做策略编译与记录。
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

__all__ = [
    "compile_pack",
    "pack_names",
    "category_matches",
    "runtime_predicate",
    "STRICTNESS_ENFORCING",
    "STRICTNESS_BALANCED",
    "STRICTNESS_OBSERVE",
]

# ── strictness 档位 ──────────────────────────────────────────────────────
STRICTNESS_ENFORCING = "enforcing"
STRICTNESS_BALANCED = "balanced"
STRICTNESS_OBSERVE = "observe"

_SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def _sev_rank(sev: str) -> int:
    return _SEVERITY_ORDER.get((sev or "").strip().lower(), -1)


def _str_set(value: Any) -> List[str]:
    """把 pack 里的类别字段规整成大写字符串列表。非列表值按空处理。"""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set)):
        return []
    out = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item.strip().upper())
    return sorted(set(out))


def pack_names() -> List[str]:
    """列出所有可用 policy pack 名（走 scanner.policy_pack，唯一事实源）。"""
    from scanner import policy_pack as _pp  # noqa: PLC0415（延迟导入，避免 eco→scanner 启动耦合）

    return list(_pp.list_packs())


def category_matches(category: Optional[str], patterns: List[str]) -> bool:
    """类别匹配：支持精确匹配与前缀（'ASI' 命中 'ASI01'、'ASI0' 命中 'ASI01'）。

    运行时调用方在 context 里给 category（如 MCP07 / ASI03）；pack 里写的是
    类别族（如 ASI01-ASI10）。前缀匹配让「排除整个 ASI 族」在运行时成立，
    同时精确类别优先。
    """
    cat = (category or "").strip().upper()
    if not cat:
        return False
    if not patterns:
        return False
    if cat in patterns:
        return True
    for p in patterns:
        if cat.startswith(p.rstrip("*")):
            return True
    return False


def compile_pack(
    pack_name: str,
    *,
    strict_runtime: bool = False,
) -> Dict[str, Any]:
    """把一个扫描期 policy pack 编译成运行时 PEP 可消费的策略片段。

    Args:
        pack_name:   pack 名（default / strict / mcp-only / personal-agent / red-team）
        strict_runtime:
            运维显式同意把 pack 严格度推成运行时默认拒绝。默认 False ——
            因为 pack 的 fail_on 是 CI 阈值语义，直接翻 default_deny 会拒掉
            一切未知实体（生产炸服）。要严必须显式开。

    Returns:
        {
          "source_pack", "name", "description", "config",
          "runtime": {"deny_categories", "allow_categories", "severity_floor",
                      "strictness", "default_deny"},
          "rationale": [{"runtime_rule", "from_pack_field", "value", "effect"}, ...],
        }

    Raises:
        KeyError: pack 不存在（与 scanner.policy_pack 同口径）。
    """
    from scanner import policy_pack as _pp  # noqa: PLC0415

    pack = _pp.load_pack(pack_name)
    config = pack.get("config") or {}
    excluded = _str_set(config.get("excluded_categories"))
    required = _str_set(config.get("required_categories"))
    severity_min = (config.get("severity_min") or "info").strip().lower()
    fail_on = (config.get("fail_on") or "info").strip().lower()

    runtime: Dict[str, Any] = {
        # excluded → 运行时真拒绝（唯一可信的拒绝信号）
        "deny_categories": excluded,
        # required → 运行时放行 + 观察；不硬拒未知类别（生态升级不炸）
        "allow_categories": required,
        # severity_min → 审计记录阈值
        "severity_floor": severity_min,
        # fail_on → 档位旁证（不直接驱动 default_deny）
        "strictness": STRICTNESS_OBSERVE if fail_on == "impossible" else STRICTNESS_BALANCED,
        # 仅在运维显式确认时才推默认拒绝
        "default_deny": bool(strict_runtime) and fail_on != "impossible",
    }

    # strictness 升级：有真拒绝规则 → balanced 之上；显式开 → enforcing
    if runtime["deny_categories"] and runtime["strictness"] == STRICTNESS_BALANCED:
        runtime["strictness"] = STRICTNESS_BALANCED
    if strict_runtime and fail_on not in ("impossible",):
        runtime["strictness"] = STRICTNESS_ENFORCING

    rationale: List[Dict[str, Any]] = []

    if excluded:
        rationale.append({
            "runtime_rule": "runtime.deny_categories",
            "from_pack_field": "config.excluded_categories",
            "value": excluded,
            "effect": "运行时拒绝声明了该类别的工具调用（真拦截，非仅 CI）",
        })
    if required:
        rationale.append({
            "runtime_rule": "runtime.allow_categories",
            "from_pack_field": "config.required_categories",
            "value": required,
            "effect": "运行时放行并观察这些类别；表外未知类别仍放行（不误伤生态升级）",
        })
    if severity_min:
        rationale.append({
            "runtime_rule": "runtime.severity_floor",
            "from_pack_field": "config.severity_min",
            "value": severity_min,
            "effect": f"低于 {severity_min} 的判定只写审计日志，不升级为告警",
        })
    if fail_on:
        rationale.append({
            "runtime_rule": "runtime.strictness",
            "from_pack_field": "config.fail_on",
            "value": fail_on,
            "effect": "CI 通过阈值在运行时只作档位标注，不直接驱动 default_deny（避免拒掉一切未知实体）",
        })
    if strict_runtime:
        rationale.append({
            "runtime_rule": "runtime.default_deny",
            "from_pack_field": "<operator explicit>",
            "value": True,
            "effect": "运维显式开启：未列入 allow_categories 的实体运行时拒绝",
        })
    if not rationale:
        rationale.append({
            "runtime_rule": "runtime",
            "from_pack_field": "<pack>",
            "value": pack_name,
            "effect": "该 pack 不含任何类别/严重度约束，运行时与默认行为等价（只做审计）",
        })

    return {
        "source_pack": pack.get("name") or pack_name,
        "name": pack.get("name") or pack_name,
        "description": pack.get("description") or "",
        "config": config,
        "runtime": runtime,
        "rationale": rationale,
    }


def runtime_predicate(pack_name: str, **kw) -> Dict[str, Any]:
    """一次编译的便利包装：直接拿运行时可消费的片段。"""
    return compile_pack(pack_name, **kw)["runtime"]


# ── 自检 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for _n in pack_names():
        _c = compile_pack(_n)
        print(f"{_n:<16} strictness={_c['runtime']['strictness']:<10} "
              f"deny={len(_c['runtime']['deny_categories'])} allow={len(_c['runtime']['allow_categories'])} "
              f"floor={_c['runtime']['severity_floor']}")
