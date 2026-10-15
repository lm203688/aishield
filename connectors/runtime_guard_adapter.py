"""
connectors/runtime_guard_adapter.py — 运行时治理的框架参考适配器（#422 治理通电）

对标 Microsoft agent-governance-toolkit 的「框架无关、即插即用」：把 AIShield 的
fail-closed 准入网关包装成 LangChain / CrewAI 能直接挂上去的「拦截工具」。

设计约束（与全仓一致）：
  · 零第三方依赖 —— langchain / crewai 只在真正使用时才 import，模块可独立加载；
  · 不 spawn 被治理进程，只做「调用前准入判定 + 记录」；
  · 失败时**默认放行但打标 unsafe**（adapter 本身不是安全边界，真正的 fail-closed
    在 eco/runtime_governance 一侧；这里若抛异常而直接拒绝会误伤正常 agent 循环）。

用法（参考）：
  from connectors.runtime_guard_adapter import LangChainGuardTool, CrewAIGuardTool
  tool = LangChainGuardTool(server="my-mcp-server")
  # agent 每准备调用一个工具前：
  verdict = tool.check("delete_all_records")
  if not verdict["allowed"]:
      ... 阻断 ...
"""
from __future__ import annotations

import importlib
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _evaluate(server: str, tool: str, context: dict | None = None) -> dict:
    from eco import runtime_governance as rg
    return rg.evaluate(server, tool, context=context, log=True)


class BaseGuard:
    """共享的准入判定逻辑，两个框架适配器各自做接口适配。"""

    def __init__(self, server: str, context: dict | None = None, label: str = "aishield-guard"):
        self.server = server
        self.context = context or {}
        self.label = label

    def check(self, tool: str, context: dict | None = None) -> dict:
        """判定一次工具调用。返回 governance.evaluate 的原始裁决（含 mode/enforced）。"""
        merged = {**self.context, **(context or {})}
        return _evaluate(self.server, tool, context=merged)

    def allow(self, tool: str) -> bool:
        return bool(self.check(tool).get("allowed"))


class LangChainGuardTool(BaseGuard):
    """LangChain 风格的「工具」适配器：实现一个最小 tool 接口。

    不强制依赖 langchain —— 仅在你主动 `from langchain... import Tool` 并传入
    `as_langchain_tool()` 时才 import，避免无谓耦合。
    """

    def _run(self, tool: str, context_json: str = "{}") -> str:
        import json as _json
        try:
            ctx = _json.loads(context_json) if context_json else {}
        except Exception:
            ctx = {}
        v = self.check(tool, ctx)
        return _json.dumps({
            "allowed": v.get("allowed"),
            "decision": v.get("decision"),
            "mode": v.get("mode"),
            "enforced": v.get("enforced"),
            "reason": v.get("reason"),
        }, ensure_ascii=False)

    def as_langchain_tool(self):
        """返回一个 langchain Tool 对象（需已安装 langchain）。

        用 importlib 做**真·懒加载**：langchain 是可选依赖，仅在本方法被调用
        时才解析，避免静态 import 把可选依赖变成模块加载期的硬耦合（也避免
        import-integrity / E12 门禁把未安装的 langchain 误判为缺失的内部模块）。
        """
        try:
            Tool = importlib.import_module("langchain.tools").Tool  # type: ignore
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                "LangChain 未安装；本适配器仅在调用 as_langchain_tool() 时才需要它"
            ) from e
        return Tool(
            name=self.label,
            description="AIShield 运行时治理准入网关：调用工具前判定是否放行（fail-closed）",
            func=self._run,
        )


class CrewAIGuardTool(BaseGuard):
    """CrewAI 风格的「工具」适配器。"""

    def _run(self, tool: str, context_json: str = "{}") -> str:
        import json as _json
        try:
            ctx = _json.loads(context_json) if context_json else {}
        except Exception:
            ctx = {}
        v = self.check(tool, ctx)
        return _json.dumps({
            "allowed": v.get("allowed"),
            "decision": v.get("decision"),
            "mode": v.get("mode"),
            "enforced": v.get("enforced"),
            "reason": v.get("reason"),
        }, ensure_ascii=False)

    def as_crewai_tool(self):
        """返回一个 CrewAI BaseTool 对象（需已安装 crewai_tools）。

        用 importlib 做**真·懒加载**：crewai 是可选依赖，仅在本方法被调用时才
        解析，避免静态 import 把可选依赖变成模块加载期的硬耦合（也避免
        import-integrity / E12 门禁把未安装的 crewai_tools 误判为缺失的内部模块）。
        """
        try:
            BaseTool = importlib.import_module("crewai_tools").BaseTool  # type: ignore
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                "CrewAI 未安装；本适配器仅在调用 as_crewai_tool() 时才需要它"
            ) from e

        guard = self

        class _CrewGuard(BaseTool):  # type: ignore[misc, valid-type]
            name: str = guard.label
            description: str = "AIShield 运行时治理准入网关：调用工具前判定是否放行（fail-closed）"

            def _run(self, tool: str, context_json: str = "{}") -> str:  # type: ignore[override]
                return guard._run(tool, context_json)

        return _CrewGuard()


if __name__ == "__main__":
    g = LangChainGuardTool(server="demo-server")
    print(g.check("read_file"))
    print(g.check("exec_shell"))
