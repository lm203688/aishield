# -*- coding: utf-8 -*-
"""
tests/test_runtime_observer.py — Program C (RIL) 运行时免疫层门禁测试

钉死运行时铁律：
  1. 观测器绝不自行执行被治理的工具调用（maybe_invoke 在 deny 时抑制执行）。
  2. 网关不可达 / 异常 → fail-closed 默认拒绝（绝不因观测故障而放行）。
  3. 集成既有治理网关：default_deny 开启时未知 server 被拒；显式 allow 后放行。
  4. guard_tool_call / tool_guard 护栏在被拒时阻止执行（观测 ≠ 执行）。
"""
import os
import tempfile
import unittest

from eco import runtime_governance as rg
from eco.runtime_observer import (
    RuntimeObserver, guard_tool_call, tool_guard, tetragon_sidecar_spec,
)


class _FaultyGovernor:
    def evaluate(self, server, tool="", context=None):
        raise RuntimeError("governor down")


class TestRuntimeObserver(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ril_test_")
        self._orig_pf, self._orig_al = rg.POLICY_FILE, rg.AUDIT_LOG
        rg.POLICY_FILE = os.path.join(self.tmp, "governance.json")
        rg.AUDIT_LOG = os.path.join(self.tmp, "governance_audit.jsonl")
        self.addCleanup(setattr, rg, "POLICY_FILE", self._orig_pf)
        self.addCleanup(setattr, rg, "AUDIT_LOG", self._orig_al)
        # 默认策略：开启 fail-closed
        rg._default.set_default_deny(True)

    def test_never_executes_observed_call_on_deny(self):
        obs = RuntimeObserver()
        called = {"n": 0}
        res = obs.maybe_invoke("unknown-server", "exec_shell",
                               action=lambda: called.__setitem__("n", 1))
        self.assertFalse(res.get("allowed"))
        self.assertTrue(res.get("suppressed"))
        self.assertEqual(called["n"], 0, "被拒的工具调用绝不应被执行")

    def test_fail_closed_when_governor_unavailable(self):
        obs = RuntimeObserver(governor=_FaultyGovernor())
        res = obs.observe("any-server", "read_file")
        self.assertFalse(res.get("allowed"))
        self.assertEqual(res.get("policy_hit"), "fail_closed")

    def test_unknown_server_denied_under_fail_closed(self):
        obs = RuntimeObserver()
        res = obs.observe("brand-new-server", "read_file")
        self.assertFalse(res.get("allowed"))
        self.assertEqual(res.get("policy_hit"), "default_deny")

    def test_allowed_server_passes_and_invokes(self):
        rg._default.allow_tool("good-server", ["read_file"])
        obs = RuntimeObserver()
        called = {"n": 0}
        res = obs.maybe_invoke("good-server", "read_file",
                               action=lambda: called.__setitem__("n", 1))
        self.assertTrue(res.get("allowed"))
        self.assertEqual(called["n"], 1)

    def test_guard_tool_call_context_suppresses(self):
        obs = RuntimeObserver()
        executed = {"n": 0}
        with guard_tool_call(obs, "unknown-server", "exec_shell") as guard:
            if guard["allowed"]:
                executed["n"] += 1
        self.assertEqual(executed["n"], 0)

    def test_tool_guard_decorator_blocks_on_deny(self):
        obs = RuntimeObserver()

        @tool_guard(obs, "unknown-server", "exec_shell")
        def dangerous():
            return "ran"
        result, decision = dangerous()
        self.assertIsNone(result)
        self.assertFalse(decision.get("allowed"))

    def test_tetragon_sidecar_spec_well_formed(self):
        spec = tetragon_sidecar_spec()
        for key in ("spec_version", "observe_events", "decision_endpoint",
                    "shared_invariants", "fail_closed",
                    "never_executes_observed_call"):
            self.assertIn(key, spec)
        self.assertTrue(spec["never_executes_observed_call"])


if __name__ == "__main__":
    unittest.main()
