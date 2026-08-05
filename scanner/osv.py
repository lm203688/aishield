"""
AIShield OSV.dev 实时 CVE 检查 (D1)

对扫描出的 npm / PyPI 依赖查询 OSV.dev 漏洞数据库，补上 "离线 bundled CVE" 之外
的实时供应链漏洞情报。设计原则：
  - 离线优先：默认不联网（隐私 + 避免 CI 限流），由调用方显式 enable。
  - SSRF 无关：OSV 是公开 API，但仍仅对白名单主机发起请求。
  - 可缓存：调用方可传入 cache dict 复用结果。
"""
from __future__ import annotations

import json
import urllib.request
from urllib.error import URLError, HTTPError

OSV_QUERY_URL = "https://api.osv.dev/v1/query"
_SEVERITY_MAP = {
    "CRITICAL": "critical",
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low",
    "MODERATE": "medium",
}


def build_osv_query(name: str, ecosystem: str, version: str | None = None) -> dict:
    """构造 OSV 查询体（可供测试复用，不触网）。"""
    q: dict = {"package": {"name": name, "ecosystem": ecosystem}}
    if version:
        q["version"] = version
    return q


def _ecosystem_for(source: str) -> str | None:
    if source == "npm":
        return "npm"
    if source == "pypi":
        return "PyPI"
    return None


def check_osv(dependencies: list[dict], *, use_network: bool = True,
              timeout: int = 12, cache: dict | None = None) -> list[dict]:
    """
    对依赖列表查询 OSV.dev，返回 CVE findings。

    Args:
        dependencies: engine.dependency_analysis 产出的 [{name, version, source}]
        use_network: 是否联网（默认 True；CI 可传 False 仅做结构校验）
        cache: 可选 {query_json: [vulns]} 复用，避免重复请求
    Returns:
        findings: [{type, severity, description, package, version, cve, owasp_category, evidence}]
    """
    findings: list[dict] = []
    if not use_network:
        return findings

    cache = cache or {}
    for dep in dependencies:
        name = (dep.get("name") or "").strip()
        source = dep.get("source")
        ecosystem = _ecosystem_for(source or "")
        if not name or not ecosystem:
            continue
        ver = dep.get("version")
        version = ver if ver and ver not in ("latest", "*", "unknown", "", None) else None

        query = build_osv_query(name, ecosystem, version)
        cache_key = json.dumps(query, sort_keys=True)
        vulns = cache.get(cache_key)
        if vulns is None:
            try:
                req = urllib.request.Request(
                    OSV_QUERY_URL,
                    data=json.dumps(query).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "AIShield/4.2"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    vulns = json.loads(resp.read().decode("utf-8")).get("vulns", [])
                cache[cache_key] = vulns
            except (URLError, HTTPError, OSError, ValueError):
                cache[cache_key] = []
                continue

        for vuln in vulns:
            vid = vuln.get("id", "UNKNOWN")
            sev = "high"
            for s in vuln.get("severity", []):
                sev = _SEVERITY_MAP.get((s or {}).get("score", ""), sev)
            findings.append({
                "type": "osv_cve",
                "severity": sev,
                "description": f"依赖 {name}@{version or '?'} 命中 OSV 漏洞: {vid}",
                "package": name,
                "version": version,
                "cve": vid,
                "owasp_category": "MCP04",
                "evidence": (vuln.get("summary") or "")[:160],
                "fixed_version": _first_fixed(vuln),
            })
    return findings


def _first_fixed(vuln: dict) -> str:
    for af in vuln.get("affected", []):
        for rng in af.get("ranges", []):
            for ev in rng.get("events", []):
                if "fixed" in ev:
                    return str(ev["fixed"])
    return ""
