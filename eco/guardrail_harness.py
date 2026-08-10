"""
eco/guardrail_harness.py — Guardrail-as-harness 适配器（#3）

把 AIShield 暴露成"拦截每一次工具调用"的安全 harness —— 即 Cloudflare
Agents Week 反复强调的「大脑(agent 循环) / 双手(代码执行) 分离」里的
**双手治理层**。

三类平台（forge / forgevm / Cloudflare Sandbox / Goose / Open Interpreter）
只给 agent 一台隔离的"电脑"，却从不审查这台电脑**加载了哪些 MCP / skill /
prompt**。AIShield 卡的就是这层内容安全：在工具真正执行前问一句"准吗"。

三种使用形态：
  1. 编程调用：harness.intercept(server, tool, arguments, context) -> decision
     复用 runtime_governance.RuntimeGovernor.evaluate() 做 fail-closed 准入，
     并额外对「调用参数」跑规则引擎，命中 critical 模式直接拒绝（内容层护栏）。
  2. stdio JSON-RPC 适配器：以 MCP 风格 JSON-RPC over stdio 暴露 intercept，
     让任意 agent harness 把 AIShield 注册为"拦截工具"（零第三方依赖，纯 stdio）。
  3. 不 spawn 被治理进程、可完全离线、不外发任何数据 —— 与扫描器同源铁律。

对齐 OWASP MCP02（权限外溢）/ MCP07（认证授权）/ ASI08（失控自主性）。
"""
from __future__ import annotations

import json
import re
import sys

from eco.runtime_governance import RuntimeGovernor, DECISION_ALLOW, DECISION_DENY

# 参数内容扫描只拦 critical 级规则（密钥/私钥/沙箱逃逸/命令注入等），
# 避免对合法参数误伤。良性参数几乎不可能命中 critical 模式。
from scanner.rules import ALL_RULES


class GuardrailHarness:
    """in-loop 安全 harness：每次工具调用前的准入 + 内容护栏。"""

    def __init__(self, governor: RuntimeGovernor | None = None):
        self.gov = governor or RuntimeGovernor()

    # ── 核心：拦截一次工具调用 ──
    def intercept(self, server, tool="", arguments=None, context=None):
        """判定一次工具调用是否放行。

        两级闸门，任一拒绝即终止：
          1) 运行时治理准入（kill switch > deny > allow > default_deny）
          2) 调用参数内容扫描（critical 模式命中即拒）
        """
        server = (server or "").strip()
        tool = (tool or "").strip()

        # 第一级：运行时治理准入
        gov = self.gov.evaluate(server, tool, context=context, log=True)
        if gov["decision"] == DECISION_DENY:
            gov["stage"] = "governance"
            return gov

        # 第二级：参数内容扫描
        if arguments is not None:
            arg_text = arguments if isinstance(arguments, str) else json.dumps(arguments, ensure_ascii=False)
            blocked = self._scan_arguments(arg_text)
            if blocked:
                return {
                    "decision": DECISION_DENY,
                    "allowed": False,
                    "server": server,
                    "tool": tool,
                    "stage": "content_scan",
                    "reason": f"调用参数命中高危模式: {blocked}",
                    "policy_hit": "argument_blocked",
                    "ts": gov.get("ts"),
                }
        return {
            "decision": DECISION_ALLOW,
            "allowed": True,
            "server": server,
            "tool": tool,
            "stage": "pass",
            "reason": gov.get("reason", "准入"),
            "policy_hit": gov.get("policy_hit"),
            "ts": gov.get("ts"),
        }

    def _scan_arguments(self, text):
        """返回命中的首个 critical 规则描述，否则空串。"""
        for pat, (desc, sev) in ALL_RULES.items():
            if sev != "critical":
                continue
            try:
                if re.search(pat, text, re.I):
                    return desc
            except Exception:
                continue
        return ""


# ── stdio JSON-RPC 适配器（MCP 风格，零依赖） ──
_HARNESS = GuardrailHarness()


def _handle_request(req: dict, harness=None) -> dict | None:
    """把一条 JSON-RPC 请求转成响应对象（无需响应的返回 None）。

    harness 可注入，便于测试；缺省用模块级单例 _HARNESS。
    """
    h = harness or _HARNESS
    method = req.get("method")
    rid = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"guardrail": {"intercept": True}},
                "serverInfo": {"name": "aishield-guardrail", "version": "4.2"},
            },
        }
    if method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {"tools": [
                {"name": "intercept",
                 "description": "在工具执行前做 fail-closed 准入 + 参数内容护栏",
                 "inputSchema": {
                     "type": "object",
                     "properties": {
                         "server": {"type": "string"},
                         "tool": {"type": "string"},
                         "arguments": {"type": "object"},
                         "context": {"type": "object"},
                     },
                     "required": ["server"],
                 }},
            ]},
        }
    if method == "tools/call":
        params = req.get("params", {}) or {}
        name = params.get("name") or params.get("tool") or ""
        if name != "intercept":
            return {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32601, "message": f"unknown tool: {name}"}}
        decision = h.intercept(
            params.get("server", ""),
            params.get("tool", ""),
            params.get("arguments"),
            params.get("context"),
        )
        return {"jsonrpc": "2.0", "id": rid, "result": decision}
    # 未识别方法
    if rid is not None:
        return {"jsonrpc": "2.0", "id": rid,
                "error": {"code": -32601, "message": f"method not found: {method}"}}
    return None


def run_stdio(in_stream=None, out_stream=None):
    """从 stdin 逐行读 JSON-RPC，向 stdout 写响应。可被测试用 StringIO 注入。"""
    in_stream = in_stream or sys.stdin
    out_stream = out_stream or sys.stdout
    for line in in_stream:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        if not isinstance(req, dict):
            continue
        resp = _handle_request(req)
        if resp is not None:
            out_stream.write(json.dumps(resp, ensure_ascii=False) + "\n")
            out_stream.flush()


if __name__ == "__main__":
    run_stdio()
