"""
差分扫描模块 — 对比两次扫描结果，只报告新增/变化/已修复的风险

设计哲学:
    - 本地计算，零网络
    - 输入两份 scan() 的 dict 输出，输出差异报告
    - 不修改原始 scan() 签名，向后兼容

用法:
    from scanner.diff import diff_scans, diff_summary
    report1 = scanner.scan(url)
    report2 = scanner.scan(url)
    delta = diff_scans(report1, report2)
    summary = diff_summary(delta)
"""

from __future__ import annotations

from typing import Any, Dict, List

# finding 唯一键
_FKEY_FIELDS = ("type", "description", "file")


def _fkey(f: Dict[str, Any]) -> str:
    return "|".join(str(f.get(k, "")) for k in _FKEY_FIELDS)


def diff_scans(
    prev: Dict[str, Any],
    curr: Dict[str, Any],
    *,
    include_fixed: bool = True,
) -> Dict[str, Any]:
    """
    对比两份扫描报告，返回结构化差异。

    Args:
        prev: 上次的扫描报告（dict）
        curr: 本次的扫描报告（dict）
        include_fixed: 是否包含已修复（resolved）的 finding

    Returns:
        {
            "prev_version": str,
            "curr_version": str,
            "prev_scanned_at": str,
            "curr_scanned_at": str,
            "prev_total": int,
            "curr_total": int,
            "prev_score": float,
            "curr_score": float,
            "score_delta": float,
            "new": [finding...],              # 新增
            "resolved": [finding...],          # 已修复
            "unchanged": [finding...],         # 未变
            "changed": [finding...],           # 严重程度变化
            "summary": "..."
        }
    """
    prev_findings = prev.get("findings", [])
    curr_findings = curr.get("findings", [])

    prev_map: Dict[str, Dict[str, Any]] = {}
    for f in prev_findings:
        prev_map[_fkey(f)] = f

    curr_map: Dict[str, Dict[str, Any]] = {}
    for f in curr_findings:
        curr_map[_fkey(f)] = f

    prev_keys = set(prev_map.keys())
    curr_keys = set(curr_map.keys())

    new_findings = [curr_map[k] for k in sorted(curr_keys - prev_keys)]
    resolved_findings = [prev_map[k] for k in sorted(prev_keys - curr_keys)] if include_fixed else []
    common_keys = sorted(prev_keys & curr_keys)

    unchanged: List[Dict[str, Any]] = []
    changed: List[Dict[str, Any]] = []
    for k in common_keys:
        p = prev_map[k]
        c = curr_map[k]
        if p.get("severity") == c.get("severity") and p.get("owasp") == c.get("owasp"):
            unchanged.append(c)
        else:
            item = dict(c)
            item["_prev_severity"] = p.get("severity")
            changed.append(item)

    prev_score = prev.get("overall_score", 0)
    curr_score = curr.get("overall_score", 0)
    score_delta = round(curr_score - prev_score, 2)

    # 生成摘要
    parts = []
    if score_delta > 0:
        parts.append(f"安全分 +{score_delta}")
    elif score_delta < 0:
        parts.append(f"安全分 {score_delta}")
    else:
        parts.append("安全分无变化")

    if new_findings:
        parts.append(f"{len(new_findings)} 新增风险")
    if resolved_findings:
        parts.append(f"{len(resolved_findings)} 已修复")
    if changed:
        parts.append(f"{len(changed)} 严重程度变化")

    summary = "；".join(parts) if parts else "无差异"

    return {
        "prev_version": prev.get("scanner_version", ""),
        "curr_version": curr.get("scanner_version", ""),
        "prev_scanned_at": prev.get("scanned_at", ""),
        "curr_scanned_at": curr.get("scanned_at", ""),
        "prev_total": len(prev_findings),
        "curr_total": len(curr_findings),
        "prev_score": prev_score,
        "curr_score": curr_score,
        "score_delta": score_delta,
        "new": new_findings,
        "resolved": resolved_findings,
        "unchanged": unchanged,
        "changed": changed,
        "summary": summary,
    }


def diff_summary(delta: Dict[str, Any]) -> str:
    """生成人类可读的差分摘要"""
    lines = [
        "=== AIShield 差分扫描报告 ===",
        f"对比: {delta.get('prev_version', '?')}@{delta.get('prev_scanned_at', '?')}  →  "
        f"{delta.get('curr_version', '?')}@{delta.get('curr_scanned_at', '?')}",
        f"安全分: {delta.get('prev_score', 0)} → {delta.get('curr_score', 0)} ({delta.get('score_delta', 0):+.2f})",
        f"发现: {delta.get('prev_total', 0)} → {delta.get('curr_total', 0)}",
        "",
    ]

    if delta.get("new"):
        lines.append(f"🆕 新增风险 ({len(delta['new'])}):")
        for f in delta["new"][:5]:
            lines.append(f"   [{f.get('severity', '?')}] {f.get('type', '?')}: {f.get('description', '?')[:80]}")
        if len(delta["new"]) > 5:
            lines.append(f"   ... 还有 {len(delta['new'])-5} 条")

    if delta.get("resolved"):
        lines.append(f"\n✅ 已修复 ({len(delta['resolved'])}):")
        for f in delta["resolved"][:5]:
            lines.append(f"   {f.get('type', '?')}: {f.get('description', '?')[:80]}")

    if delta.get("changed"):
        lines.append(f"\n⚠️  严重程度变化 ({len(delta['changed'])}):")
        for f in delta["changed"][:5]:
            lines.append(f"   {f.get('type', '?')}: {f.get('_prev_severity', '?')} → {f.get('severity', '?')}")

    lines.append(f"\n📊 摘要: {delta.get('summary', '无差异')}")
    return "\n".join(lines)
