"""
AIShield 跨注册中心发现 (D3)

填补「104k agents / 15 registries / 0 互操作」的空白：聚合多个 MCP registry 的
server 条目为统一结构，供信任注册中心规模化与生态发现使用。
  - 官方 registry.modelcontextprotocol.io（v0）
  - 可扩展加入社区/企业 registry（在 REGISTRIES 注册）
"""
from __future__ import annotations

import json
import urllib.request
from urllib.parse import quote
from urllib.error import URLError, HTTPError

OFFICIAL = "https://registry.modelcontextprotocol.io/v0/servers"
REGISTRIES = {
    "official": OFFICIAL,
}

_SESSION = {"ua": "AIShield/4.2"}


def _get_json(url: str, timeout: int = 10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _SESSION["ua"], "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, HTTPError, OSError, ValueError):
        return None


def _normalize_official(entry: dict) -> dict:
    srv = entry.get("server", entry)
    name = srv.get("name") or entry.get("name") or "unknown"
    pkgs = srv.get("packages", [])
    version = (pkgs[0].get("version") if pkgs else None) or srv.get("version")
    return {
        "name": name,
        "display_name": srv.get("displayName") or name,
        "version": version,
        "description": (srv.get("description") or "")[:300],
        "registry": "official",
        "source_url": (pkgs[0].get("url") if pkgs else None) or srv.get("repository", {}).get("url"),
        "is_latest": srv.get("isLatest"),
    }


def search_registry(query: str, registry: str = "official", limit: int = 20,
                    timeout: int = 10) -> list[dict]:
    """在单个 registry 搜索 server。"""
    base = REGISTRIES.get(registry, OFFICIAL)
    url = f"{base}?search={quote(query)}&limit={limit}"
    data = _get_json(url, timeout)
    if not data:
        return []
    servers = data.get("servers", [])
    out = []
    for e in servers:
        out.append(_normalize_official(e))
    return out


def discover_across_registries(query: str, registries: list[str] | None = None,
                               limit: int = 20) -> dict:
    """
    跨多个注册中心发现并去重聚合。

    Returns:
        {query, registries_searched, total, servers:[...去重], by_registry:{reg:[...]}}
    """
    regs = registries or list(REGISTRIES.keys())
    by_registry: dict[str, list[dict]] = {}
    merged: dict[str, dict] = {}
    for reg in regs:
        found = search_registry(query, reg, limit)
        by_registry[reg] = found
        for s in found:
            key = s["name"]
            if key not in merged:
                merged[key] = s
                merged[key]["seen_in"] = [reg]
            else:
                merged[key]["seen_in"].append(reg)
    return {
        "query": query,
        "registries_searched": regs,
        "total": len(merged),
        "servers": list(merged.values()),
        "by_registry": by_registry,
    }
