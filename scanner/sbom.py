"""
scanner/sbom.py — CycloneDX SBOM + SARIF 输出 (P2 迭代)

补齐与 mcp-audit 的能力差: 让扫描结果可被 CI / 安全工具链直接消费。
  - CycloneDX 1.5 SBOM (bomFormat/specVersion/metadata/components/vulnerabilities)
  - SARIF 2.1.0 (runs[].tool.driver.rules + results)

零第三方依赖 (仅标准库)。输入为 engine.scan 返回的 scan_result dict。
"""

import json
import uuid
import re
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
TOOL_NAME = "AIShield"
TOOL_VERSION = "4.2.0"

_SEV_TO_SARIF = {
    "critical": "error", "high": "error",
    "medium": "warning", "low": "note", "info": "note", "none": "none",
}
_SEV_TO_CDX = {
    "critical": "critical", "high": "high", "medium": "medium",
    "low": "low", "info": "info", "none": "none",
}


def _now_iso():
    return datetime.now(TZ).isoformat()


def _severity_to_score(sev):
    return {
        "critical": 9.8, "high": 7.5, "medium": 5.0,
        "low": 2.5, "info": 0.5, "none": 0.0,
    }.get(sev, 5.0)


def cyclonedx_sbom(scan_result, target_name="unknown", target_version="0.0.0"):
    """从扫描结果生成 CycloneDX 1.5 SBOM。"""
    findings = scan_result.get("findings", []) if isinstance(scan_result, dict) else []
    components = []
    seen = set()
    for f in findings:
        fpath = f.get("file", "")
        if fpath and fpath not in seen:
            seen.add(fpath)
            components.append({
                "type": "file",
                "name": fpath,
                "bom-ref": "comp-" + str(len(components) + 1),
            })

    vulnerabilities = []
    for i, f in enumerate(findings):
        sev = f.get("severity", "medium")
        vulnerabilities.append({
            "bom-ref": "vuln-" + str(i + 1),
            "id": f.get("owasp_category", "RULE") + "-" + str(i + 1),
            "source": {"name": "AIShield", "url": "https://aishield.tools"},
            "ratings": [{
                "severity": _SEV_TO_CDX.get(sev, "medium"),
                "score": _severity_to_score(sev),
                "method": "static-analysis",
            }],
            "description": f.get("description", ""),
            "recommendation": "Review and remediate per OWASP guidance.",
            "affects": [{"ref": "comp-" + str(list(seen).index(f.get("file", "")) + 1)}]
            if f.get("file") in seen else [],
        })

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": "urn:uuid:" + str(uuid.uuid4()),
        "version": 1,
        "metadata": {
            "timestamp": _now_iso(),
            "authors": [{"name": "AIShield"}],
            "component": {
                "type": "application",
                "name": target_name,
                "version": target_version,
            },
            "tools": [{"vendor": "AIShield", "name": TOOL_NAME, "version": TOOL_VERSION}],
        },
        "components": components,
        "vulnerabilities": vulnerabilities,
    }


def sarif_from_scan(scan_result, target_name="unknown"):
    """从扫描结果生成 SARIF 2.1.0 报告。"""
    findings = scan_result.get("findings", []) if isinstance(scan_result, dict) else []
    rules = {}
    results = []
    for f in findings:
        cat = f.get("owasp_category") or "GENERIC"
        rule_id = cat
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": cat,
                "shortDescription": {"text": f.get("description", "")[:120]},
                "helpUri": "https://aishield.tools/owasp",
            }
        try:
            line = int(str(f.get("lines", "1")).split(",")[0])
        except Exception:
            line = 1
        results.append({
            "ruleId": rule_id,
            "level": _SEV_TO_SARIF.get(f.get("severity", "medium"), "warning"),
            "message": {"text": f.get("description", "")},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f.get("file", "unknown")},
                    "region": {"startLine": line},
                }
            }],
        })

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": TOOL_NAME,
                    "version": TOOL_VERSION,
                    "informationUri": "https://aishield.tools",
                    "rules": list(rules.values()),
                }
            },
            "originalUriBaseIds": {"SRC": {"uri": "./"}},
            "results": results,
            "properties": {
                "target": target_name,
                "generated_at": _now_iso(),
            },
        }],
    }


def attach_sbom_sarif(scan_result, target_name="unknown", target_version="0.0.0"):
    """就地给 scan_result 增加 sbom / sarif 字段 (供 API 响应与报告)。"""
    if not isinstance(scan_result, dict):
        return scan_result
    scan_result["sbom"] = cyclonedx_sbom(scan_result, target_name, target_version)
    scan_result["sarif"] = sarif_from_scan(scan_result, target_name)
    return scan_result


def export(scan_result, target_name="unknown", target_version="0.0.0", fmt="both"):
    """单入口: 返回 dict {sbom:..., sarif:...} 供脚本/路由调用。"""
    out = {}
    if fmt in ("both", "sbom"):
        out["sbom"] = cyclonedx_sbom(scan_result, target_name, target_version)
    if fmt in ("both", "sarif"):
        out["sarif"] = sarif_from_scan(scan_result, target_name)
    return out


if __name__ == "__main__":
    # 自测: 用假数据生成两种格式
    sample = {
        "findings": [
            {"file": "server.py", "lines": "12", "severity": "critical",
             "description": "硬编码API密钥", "owasp_category": "MCP01"},
            {"file": "agent.py", "lines": "30", "severity": "high",
             "description": "关闭人类确认环", "owasp_category": "ASI03"},
        ]
    }
    print(json.dumps(export(sample, "demo", "1.0.0"), ensure_ascii=False, indent=2))
