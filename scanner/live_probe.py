"""
AIShield 可选 live 只读探针 (F2)

补「运行时工具描述注入」盲区，且**不破坏非执行式不变量**：
  - 仅对已运行（remote / SSE / HTTP）的 server 发起元数据 GET；
  - 绝不 spawn 被扫配置里的任何命令（stdio command 直接跳过）；
  - 默认关闭，需 enable_live_probe=True 才执行；
  - 只读取 tool manifest 文本，不调用任何工具、不传参、不触发副作用。

这让我们能在「不执行」前提下，抓到 server 运行后才暴露的工具描述投毒。
"""
from __future__ import annotations

import json
import urllib.request
from urllib.error import URLError, HTTPError

from .engine import urlopen  # SSRF 防护复用


def _manifest_urls(entry: dict) -> list[str]:
    url = entry.get("url") or entry.get("host") or ""
    if not url:
        return []
    base = url.rstrip("/")
    return [base, f"{base}/tools", f"{base}/.well-known/mcp/tool-list", f"{base}/mcp"]


def probe_server_metadata(entry: dict, *, enable: bool = False,
                         timeout: int = 8) -> dict:
    """
    只读探测一个已运行 server 的工具清单。

    Args:
        entry: client_discovery 解析出的 server 条目（含 url / command）
        enable: 显式开关（默认 False 即跳过，保护非执行不变量）
    Returns:
        {probed, reachable, transport, tools:[{name, description}], note}
    """
    if not enable:
        return {"probed": False, "reachable": False, "transport": "skipped",
                "tools": [], "note": "live probe 默认关闭（非执行式不变量）"}

    # 关键：stdio server 需要 spawn 才能起来 → 直接跳过，绝不执行命令
    if entry.get("command") and not entry.get("url"):
        return {"probed": False, "reachable": False, "transport": "stdio",
                "tools": [], "note": "stdio server 需 spawn 才运行，已跳过（不变量）"}

    url = entry.get("url")
    if not url:
        return {"probed": False, "reachable": False, "transport": "none",
                "tools": [], "note": "无远程地址，无法只读探测"}

    tools: list[dict] = []
    reachable = False
    last_err = ""
    for u in _manifest_urls(entry):
        body = urlopen(u, timeout=timeout)
        if body is None:
            last_err = "unreachable/blocked"
            continue
        reachable = True
        try:
            text = body.decode("utf-8", errors="replace")
        except Exception:
            continue
        parsed = _extract_tools(text)
        if parsed:
            tools.extend(parsed)
            break
        last_err = "no tool manifest found"

    return {
        "probed": True,
        "reachable": reachable,
        "transport": "remote",
        "tools": tools,
        "note": "只读元数据，未执行任何工具" if reachable else (last_err or "unreachable"),
    }


def _extract_tools(text: str) -> list[dict]:
    """尽力从 JSON / JSON 片段中抽取工具名与描述。"""
    tools: list[dict] = []
    try:
        data = json.loads(text)
    except Exception:
        # 尝试抓第一个 { ... } 片段
        import re
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return tools
        try:
            data = json.loads(m.group())
        except Exception:
            return tools

    items = data
    if isinstance(data, dict):
        items = data.get("tools") or data.get("toolList") or data.get("result", {}).get("tools") or []
    if not isinstance(items, list):
        return tools
    for t in items:
        if isinstance(t, dict) and t.get("name"):
            tools.append({"name": t.get("name"), "description": (t.get("description") or "")[:300]})
    return tools
