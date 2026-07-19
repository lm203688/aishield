"""
MCP工具调用代理网关
功能：
  1. 接收Agent对MCP工具的调用请求
  2. 检查目标工具是否在已认证列表中
  3. 记录调用审计日志
  4. 转发请求到目标MCP Server（stdio或HTTP模式）
  5. 返回结果 + 计费记录
"""

import json
import os
import time
import threading
from datetime import datetime, timezone, timedelta
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError

# ── 路径 ──
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

MARKETPLACE_FILE = os.path.join(DATA_DIR, "marketplace.json")
PROXY_AUDIT_FILE = os.path.join(DATA_DIR, "proxy_audit.json")
PROXY_STATS_FILE = os.path.join(DATA_DIR, "proxy_stats.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()


def _load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def _save_json(path, data):
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class ProxyGateway:
    """MCP工具调用代理网关 — 认证工具通过AIShield代理调用，自动计费+审计"""

    def __init__(self):
        self._certified_tools = {}
        self._load_certified_tools()

    def _load_certified_tools(self):
        """加载已认证工具列表（marketplace.json中status=active的工具）"""
        marketplace = _load_json(MARKETPLACE_FILE, {"tools": {}})
        tools = marketplace.get("tools", {})
        active_tools = {}
        for tool_id, tool_info in tools.items():
            if tool_info.get("status") == "active":
                active_tools[tool_info.get("source_url", tool_id)] = {
                    "tool_id": tool_id,
                    "name": tool_info.get("name", ""),
                    "source_url": tool_info.get("source_url", ""),
                    "category": tool_info.get("category", "mcp"),
                    "description": tool_info.get("description", ""),
                    "overall_score": tool_info.get("overall_score", 0),
                    "badge_level": tool_info.get("badge_level", "none"),
                    "capabilities": tool_info.get("capabilities", []),
                }
        self._certified_tools = active_tools
        print(f"[ProxyGateway] 已加载 {len(active_tools)} 个已认证工具")

    def _reload_if_needed(self):
        """重新加载已认证工具列表（每次调用前检查，或可设为定时刷新）"""
        self._load_certified_tools()

    def _record_proxy_audit(self, record):
        """记录代理调用审计日志"""
        audits = _load_json(PROXY_AUDIT_FILE, {"calls": []})
        audits["calls"].append(record)
        # 只保留最近2000条
        if len(audits["calls"]) > 2000:
            audits["calls"] = audits["calls"][-1500:]
        _save_json(PROXY_AUDIT_FILE, audits)

    def _update_stats(self, stats_update):
        """更新代理调用统计"""
        stats = _load_json(PROXY_STATS_FILE, {
            "total_calls": 0,
            "success_calls": 0,
            "blocked_calls": 0,
            "error_calls": 0,
            "by_tool": {},
            "by_agent": {},
            "daily": {},
        })

        stats["total_calls"] += 1

        if stats_update.get("status") == "success":
            stats["success_calls"] += 1
        elif stats_update.get("status") == "blocked":
            stats["blocked_calls"] += 1
        else:
            stats["error_calls"] += 1

        # 按工具统计
        tool_name = stats_update.get("tool_name", "unknown")
        by_tool = stats.setdefault("by_tool", {})
        by_tool[tool_name] = by_tool.get(tool_name, 0) + 1

        # 按Agent统计
        agent_did = stats_update.get("agent_did", "anonymous")
        by_agent = stats.setdefault("by_agent", {})
        by_agent[agent_did] = by_agent.get(agent_did, 0) + 1

        # 按日统计
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        daily = stats.setdefault("daily", {})
        if today not in daily:
            daily[today] = {"total": 0, "success": 0, "blocked": 0, "error": 0}
        daily[today]["total"] += 1
        if stats_update.get("status") == "success":
            daily[today]["success"] += 1
        elif stats_update.get("status") == "blocked":
            daily[today]["blocked"] += 1
        else:
            daily[today]["error"] += 1

        # 只保留最近30天
        daily_keys = sorted(daily.keys())
        if len(daily_keys) > 30:
            for k in daily_keys[:-30]:
                del daily[k]

        _save_json(PROXY_STATS_FILE, stats)

    def call_tool(self, target_url, tool_name, arguments, agent_did=None):
        """
        核心方法：代理调用MCP工具

        Args:
            target_url: 目标MCP Server的URL
            tool_name: 要调用的工具名称
            arguments: 工具参数（dict）
            agent_did: 调用方的Agent DID（可选）

        Returns:
            dict: 包含调用结果或错误信息
        """
        call_time = datetime.now(TZ)
        call_ts = call_time.strftime("%Y-%m-%d %H:%M:%S")
        start_ms = time.time()

        # 1. 检查目标工具是否在已认证列表中
        self._reload_if_needed()
        certified = self._certified_tools.get(target_url)

        if not certified:
            # 工具未认证，阻断调用
            result = {
                "error": "Tool not certified",
                "blocked": True,
                "target_url": target_url,
                "tool_name": tool_name,
                "proxy_metadata": {
                    "call_time": call_ts,
                    "proxy_status": "blocked",
                    "reason": "target_url not in certified tools list (marketplace status != active)",
                    "latency_ms": int((time.time() - start_ms) * 1000),
                },
            }
            # 记录审计
            self._record_proxy_audit({
                "target_url": target_url,
                "tool_name": tool_name,
                "agent_did": agent_did,
                "status": "blocked",
                "call_time": call_ts,
                "latency_ms": result["proxy_metadata"]["latency_ms"],
            })
            self._update_stats({
                "status": "blocked",
                "tool_name": tool_name,
                "agent_did": agent_did,
            })
            return result

        # 2. 转发请求到目标MCP Server（JSON-RPC tools/call）
        rpc_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
        }

        try:
            # 构造目标端点：target_url/api/v1/mcp
            if target_url.endswith("/"):
                endpoint = target_url.rstrip("/") + "/api/v1/mcp"
            else:
                endpoint = target_url + "/api/v1/mcp"

            payload = json.dumps(rpc_request, ensure_ascii=False).encode("utf-8")
            req = urllib_request.Request(
                endpoint,
                data=payload,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json",
                    "User-Agent": "AIShield-ProxyGateway/4.1",
                },
                method="POST",
            )
            timeout = 30
            with urllib_request.urlopen(req, timeout=timeout) as resp:
                resp_body = resp.read().decode("utf-8", errors="replace")
                upstream_result = json.loads(resp_body)

            latency_ms = int((time.time() - start_ms) * 1000)

            result = {
                "result": upstream_result.get("result", upstream_result),
                "proxy_metadata": {
                    "call_time": call_ts,
                    "proxy_status": "success",
                    "certified_tool": certified.get("name", ""),
                    "certified_badge": certified.get("badge_level", "none"),
                    "target_endpoint": endpoint,
                    "latency_ms": latency_ms,
                    "agent_did": agent_did,
                },
            }

            # 3. 记录审计日志
            self._record_proxy_audit({
                "target_url": target_url,
                "tool_name": tool_name,
                "arguments_keys": list((arguments or {}).keys()),
                "agent_did": agent_did,
                "status": "success",
                "call_time": call_ts,
                "latency_ms": latency_ms,
                "certified_tool": certified.get("name", ""),
            })

            # 4. 更新统计
            self._update_stats({
                "status": "success",
                "tool_name": tool_name,
                "agent_did": agent_did,
            })

            return result

        except (URLError, HTTPError) as e:
            latency_ms = int((time.time() - start_ms) * 1000)
            error_msg = f"Upstream MCP server error: {e}"

            result = {
                "error": error_msg,
                "blocked": False,
                "target_url": target_url,
                "tool_name": tool_name,
                "proxy_metadata": {
                    "call_time": call_ts,
                    "proxy_status": "upstream_error",
                    "latency_ms": latency_ms,
                },
            }

            self._record_proxy_audit({
                "target_url": target_url,
                "tool_name": tool_name,
                "agent_did": agent_did,
                "status": "error",
                "call_time": call_ts,
                "latency_ms": latency_ms,
                "error": error_msg,
            })

            self._update_stats({
                "status": "error",
                "tool_name": tool_name,
                "agent_did": agent_did,
            })

            return result

        except Exception as e:
            latency_ms = int((time.time() - start_ms) * 1000)
            error_msg = f"Proxy internal error: {e}"

            result = {
                "error": error_msg,
                "blocked": False,
                "target_url": target_url,
                "tool_name": tool_name,
                "proxy_metadata": {
                    "call_time": call_ts,
                    "proxy_status": "proxy_error",
                    "latency_ms": latency_ms,
                },
            }

            self._record_proxy_audit({
                "target_url": target_url,
                "tool_name": tool_name,
                "agent_did": agent_did,
                "status": "error",
                "call_time": call_ts,
                "latency_ms": latency_ms,
                "error": error_msg,
            })

            self._update_stats({
                "status": "error",
                "tool_name": tool_name,
                "agent_did": agent_did,
            })

            return result

    def list_certified_tools(self):
        """
        返回可代理调用的已认证工具列表

        Returns:
            dict: {tools: [...], total: int}
        """
        self._reload_if_needed()
        tools_list = list(self._certified_tools.values())
        return {
            "total": len(tools_list),
            "tools": tools_list,
        }

    def get_call_stats(self):
        """
        返回代理调用统计

        Returns:
            dict: 统计数据
        """
        stats = _load_json(PROXY_STATS_FILE, {
            "total_calls": 0,
            "success_calls": 0,
            "blocked_calls": 0,
            "error_calls": 0,
            "by_tool": {},
            "by_agent": {},
            "daily": {},
        })
        return stats


# ── 全局实例 ──
gateway = ProxyGateway()