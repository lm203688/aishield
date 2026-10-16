# -*- coding: utf-8 -*-
"""
eco/runtime_observer.py — 运行时免疫层：用户态观测 + 连续证明集成（蓝图 Program C · RIL）v0.1
============================================================================================

蓝图定位（§3 Program C / §4 参考架构）
-------------------------------------
缺口 A：AIShield 只扫"代码/描述"，不观测"agent 真正调用工具时的行为"。
核心治理（决策网关 + kill switch + 哈希链审计 + 行为监控 + **连续证明流 Ed25519
签名**）已在 `eco/runtime_governance.py` 落地。本模块补上**缺失的那一层**：
把 agent 的真实工具调用送进治理网关，并与"执行"**解耦**——在 Windows 上用户态
可跑，无需 eBPF。

铁律（与 no_execute 不变量同源）
------------------------------
观测器 **绝不由自己执行** 被治理的工具调用 —— 它只：① 在 agent 行动前问网关
"允许吗"；② 记录决策 + 喂给行为监控；③（可选）在被拒时抑制执行（fail-closed）。
观测 ≠ 执行，这是隔离不变量 FVI 的运行时延伸。

Tetragon / eBPF 升级路径（蓝图 60 天 PoC）
----------------------------------------
本用户态观测器与 Tetragon sidecar 共享同一组不变量（no_execute / no_network /
single_writer）与同一决策端点（RuntimeGovernor.evaluate）。`tetragon_sidecar_spec()`
产出 eBPF 观测策略骨架（仅声明，不在本机执行），60 天 PoC 时由 sidecar 进程把
真实 exec/文件/网络事件转成同一格式的 observe() 调用即可无缝替换本用户态实现。

零第三方依赖；治理后端可注入，便于离线测试。
"""
from __future__ import annotations

import functools
import os
import sys
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eco import runtime_governance as rg  # noqa: E402


class RuntimeObserver:
    """用户态运行时观测器：把 agent 工具调用意图送进治理网关，与执行解耦。"""

    def __init__(self, governor=None, deny_suppresses: bool = True):
        # governor 可注入（测试注入假网关）；缺省用既有 RuntimeGovernor 单例
        self._gov = governor
        self.deny_suppresses = deny_suppresses

    def _governor(self):
        return self._gov or rg._default

    def observe(self, server: str, tool: str = "", context: Optional[dict] = None) -> Dict[str, Any]:
        """观测一次工具调用意图，返回治理决策。**绝不执行工具本身**。"""
        g = self._governor()
        try:
            result = g.evaluate(server, tool, context)
        except Exception:
            # 网关不可达 → fail-closed 默认拒绝（绝不因观测故障而放行）
            return {"decision": rg.DECISION_DENY, "allowed": False,
                    "server": server, "tool": tool,
                    "reason": "governor unavailable -> fail-closed deny",
                    "policy_hit": "fail_closed"}
        return result

    def maybe_invoke(self, server: str, tool: str = "", context: Optional[dict] = None,
                     action: Optional[Callable[[], Any]] = None) -> Dict[str, Any]:
        """观测并在允许时执行 action。被拒默认抑制执行（fail-closed）。

        action 是零参 callable；观测器**绝不会自己 spawn** 被治理的命令。
        返回决策，含 suppressed 标记（若因 deny 而未执行）。
        """
        res = self.observe(server, tool, context)
        if res.get("allowed"):
            if action is not None:
                action()
            return res
        if self.deny_suppresses and action is not None:
            res["suppressed"] = True
        return res


@contextmanager
def guard_tool_call(observer: RuntimeObserver, server: str, tool: str = "",
                   context: Optional[dict] = None):
    """进程内工具调用护栏（Windows 兼容，无 eBPF）。

    用法::
        with guard_tool_call(obs, "demo-server", "exec_shell") as guard:
            if guard["allowed"]:
                do_the_real_call()

    被拒时 guard["allowed"] 为 False，agent 代码据此跳过执行；护栏本身不执行任何事。
    """
    res = observer.observe(server, tool, context)
    try:
        yield res
    finally:
        # 观测器不持有任何需要清理的资源（与执行彻底解耦）
        pass


def tool_guard(observer: RuntimeObserver, server: str, tool: str = "",
               context: Optional[dict] = None):
    """装饰器工厂：把任意工具函数包进运行时护栏，被拒返回 (None, decision)。"""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            res = observer.observe(server, tool, context)
            if not res.get("allowed"):
                return None, res
            return fn(*args, **kwargs), res
        return wrapper
    return decorator


def tetragon_sidecar_spec() -> Dict[str, Any]:
    """Tetragon / eBPF sidecar 升级路径规格（声明式，不在本机执行）。

    60 天 PoC：sidecar 进程挂到 agent 进程上，把真实 exec/文件/网络事件转成
    与 RuntimeObserver.observe() 同一格式的调用，即可无缝替换本用户态实现。
    这里只描述"观测什么、交给谁决策、共享哪些不变量"，不执行任何 eBPF 操作。
    """
    return {
        "spec_version": "ril-sidecar-v0.1",
        "target": "agent-process (LangChain/CrewAI/AutoGPT)",
        "observe_events": ["exec", "file_write", "network_connect"],
        "observe_method": "eBPF (Tetragon LSM hook) — userland strace/Falco 起步",
        "decision_endpoint": "eco.runtime_governance.RuntimeGovernor.evaluate",
        "shared_invariants": ["no_execute", "no_network", "single_writer(E13)"],
        "fail_closed": True,
        "never_executes_observed_call": True,  # sidecar 只观测+决策，不替 agent 执行
        "continuous_attestation": True,         # 复用 AttestationStream（Ed25519 签名）
        "upgrade_note": "本用户态观测器与 sidecar 共用 observe()->decision 契约，"
                        "切换时下游 agent 代码零改动。",
    }


if __name__ == "__main__":
    obs = RuntimeObserver()
    print("sidecar spec:", tetragon_sidecar_spec()["spec_version"])
    print("default decision for unknown server:",
          obs.observe("unknown-agent", "read_file")["decision"])
