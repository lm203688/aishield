"""
AIShield 企业集成导出 (F3)

把统一 findings 结构转成企业漏洞管理平台可消费的格式：
  - Nucleus FlexConnect（对齐 Qualys / Tenable / CrowdStrike 摄入字段）
  - Splunk / 通用 SIEM JSON
  - 攻击图 JSON（交给前端 D3 渲染）

findings 元素约定字段：type, severity, description, file/evidence, owasp_category, package, cve
"""
from __future__ import annotations

from .attack_path import solve_minimal_removal, attack_graph_json

_SEV_TO_NUCLEUS = {
    "critical": "Critical", "high": "High", "medium": "Medium",
    "low": "Low", "info": "Informational",
}
_SEV_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def to_nucleus(findings: list[dict], asset_name: str = "aishield-scan",
               asset_type: str = "mcp-server") -> dict:
    """
    Nucleus FlexConnect 风格摄入结构。
    字段对齐标准摄入管道：asset_name / finding_number / finding_severity / ...
    """
    issues = []
    for i, f in enumerate(findings, 1):
        issues.append({
            "finding_number": f"AS-{i:04d}",
            "finding_severity": _SEV_TO_NUCLEUS.get(f.get("severity", "info"), "Informational"),
            "finding_name": f.get("type", "unknown"),
            "finding_description": f.get("description", ""),
            "owasp_category": f.get("owasp_category", ""),
            "cve": f.get("cve", ""),
            "affected_asset": f.get("file") or f.get("package") or "",
            "evidence": f.get("evidence", ""),
        })
    return {
        "schema": "nucleus-flexconnect/1.0",
        "asset_name": asset_name,
        "asset_type": asset_type,
        "scanner": "AIShield",
        "findings": issues,
    }


def to_splunk(findings: list[dict], source: str = "aishield") -> dict:
    """Splunk / 通用 SIEM HEC 风格 JSON（事件列表）。"""
    events = []
    for f in findings:
        events.append({
            "event": "aishield_finding",
            "source": source,
            "severity": f.get("severity", "info"),
            "category": f.get("type", "unknown"),
            "owasp": f.get("owasp_category", ""),
            "description": f.get("description", ""),
            "asset": f.get("file") or f.get("package") or "",
            "cve": f.get("cve", ""),
        })
    return {"event_count": len(events), "events": events}


def to_attack_graph(inventory: list[dict], toxic_findings: list[dict]) -> dict:
    """攻击图（D3 友好） + 最小移除集建议。"""
    return {
        "graph": attack_graph_json(inventory, toxic_findings),
        "recommendation": solve_minimal_removal(inventory, toxic_findings),
    }
