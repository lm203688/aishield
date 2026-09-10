# -*- coding: utf-8 -*-
"""
tests/test_runtime_behavior.py — 运行时治理的行为监控层

决策网关是"点"（这次调用允许吗），行为监控是"线"（这个 agent 最近的调用模式
正常吗）。本文件钉死行为监控的安全不变量：

  1. 速率异常   —— 窗口内调用数超限判 rate_burst
  2. 拒绝探测   —— 窗口内被拒数达阈值判 denial_probe
  3. 窗口去重   —— 同一窗口每种异常只报一次，绝不刷屏
  4. 窗口过期   —— 超出 window_sec 的旧调用必须被剪掉，不能永久累积
  5. 隔离       —— 不同 server 的窗口互相独立
  6. 可审计     —— 每个异常都进哈希链审计
  7. 不误伤     —— 监控自身故障绝不能影响放行判定（evaluate 必须照常返回）
  8. 动作可挂   —— escalate 钩子能把异常升级为事故；默认关闭（保守）

所有用例重定向数据文件到临时目录，不触碰真实运行态账本。
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eco import runtime_governance as rg  # noqa: E402


class _Iso(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="aishield_behavior_")
        self.addCleanup(shutil.rmtree, self._tmp, True)
        self._orig_policy, self._orig_audit = rg.POLICY_FILE, rg.AUDIT_LOG
        rg.POLICY_FILE = os.path.join(self._tmp, "governance.json")
        rg.AUDIT_LOG = os.path.join(self._tmp, "governance_audit.jsonl")
        self.addCleanup(setattr, rg, "POLICY_FILE", self._orig_policy)
        self.addCleanup(setattr, rg, "AUDIT_LOG", self._orig_audit)
        self.addCleanup(self._restore_default)

    def _restore_default(self):
        rg.reset_behavior()
        rg._default_behavior.escalate = None


# ══════════════════════════════════════════
#  行为监控（类级）
# ══════════════════════════════════════════

class TestBehaviorMonitor(_Iso):

    def _monitor(self, **kw):
        kw.setdefault("rate_max", 5)
        kw.setdefault("denial_max", 3)
        return rg.BehaviorMonitor(path=os.path.join(self._tmp, "behavior.json"), **kw)

    def test_empty_is_healthy(self):
        st = self._monitor().status()
        self.assertTrue(st["healthy"])
        self.assertEqual(st["anomaly_count"], 0)

    def test_rate_burst_detected_on_threshold_crossing(self):
        m = self._monitor(rate_max=5)
        anomalies = []
        for i in range(6):
            anomalies = m.observe("s1", f"tool{i}")
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["type"], rg.ANOMALY_RATE_BURST)
        self.assertEqual(anomalies[0]["count"], 6)

    def test_rate_burst_is_deduplicated_within_window(self):
        """同一窗口内不能每次调用都报一次异常。"""
        m = self._monitor(rate_max=5)
        fired = 0
        for i in range(20):
            if m.observe("s1", "t"):
                fired += 1
        self.assertEqual(fired, 1, "同一窗口的 rate_burst 只能报一次")

    def test_denial_probe_detected(self):
        m = self._monitor(denial_max=3)
        seen = []
        for _ in range(3):
            seen = m.observe("s2", "exec", rg.DECISION_DENY)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0]["type"], rg.ANOMALY_DENIAL_PROBE)
        self.assertEqual(seen[0]["severity"], "high")

    def test_allow_does_not_trigger_denial_probe(self):
        # rate_max 调高，隔离出"拒绝探测"这一条路径单独验证
        m = self._monitor(denial_max=3, rate_max=99)
        for _ in range(10):
            self.assertEqual(m.observe("s3", "read", rg.DECISION_ALLOW), [])

    def test_old_entries_are_pruned(self):
        """窗口过期后必须剪掉旧调用，否则速率检测会永久误报。"""
        m = self._monitor(rate_max=3, window_sec=60)
        base = datetime.now(rg.TZ)
        for i in range(3):
            m.observe("s4", "t", ts=base - timedelta(seconds=300 + i))
        # 旧调用被剪掉后再来一次不应触发
        self.assertEqual(m.observe("s4", "t", ts=base), [])
        self.assertEqual(m.status()["servers"]["s4"]["calls"], 1)

    def test_servers_are_isolated(self):
        m = self._monitor(rate_max=3)
        for i in range(3):
            m.observe("a", "t")
        self.assertEqual(m.observe("b", "t"), [], "不同 server 的窗口必须独立")

    def test_anomaly_is_audited(self):
        m = self._monitor(rate_max=2)
        for i in range(3):
            m.observe("s5", "t")
        events = [e["event"] for e in rg.read_audit(limit=50)]
        self.assertIn("behavior_anomaly", events)

    def test_escalate_hook_is_called(self):
        calls = []
        m = self._monitor(rate_max=2, escalate=lambda s, sev, d: calls.append((s, sev, d)))
        for i in range(3):
            m.observe("s6", "t")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "s6")
        self.assertEqual(calls[0][2]["anomaly"], rg.ANOMALY_RATE_BURST)

    def test_no_escalate_by_default(self):
        m = self._monitor(rate_max=2)
        for i in range(3):
            m.observe("s7", "t")
        self.assertIsNone(m.escalate)

    def test_empty_server_is_ignored(self):
        self.assertEqual(self._monitor().observe("", "t"), [])

    def test_status_reports_denials_and_tools(self):
        m = self._monitor(denial_max=99, rate_max=99)
        m.observe("s8", "read_file", rg.DECISION_ALLOW)
        m.observe("s8", "exec_shell", rg.DECISION_DENY)
        st = m.status()["servers"]["s8"]
        self.assertEqual(st["calls"], 2)
        self.assertEqual(st["denials"], 1)
        self.assertEqual(st["tools"], ["exec_shell", "read_file"])


# ══════════════════════════════════════════
#  与决策网关的集成
# ══════════════════════════════════════════

class TestBehaviorIntegration(_Iso):

    def test_evaluate_feeds_behavior_monitor(self):
        rg.reset_behavior()
        rg.configure_behavior(rate_max=3, denial_max=99, escalate=None)
        for i in range(5):
            rg.evaluate("srv", f"tool{i}")
        st = rg.behavior_status()
        self.assertEqual(st["servers"]["srv"]["calls"], 5)
        self.assertEqual(st["anomaly_count"], 1, "超限应产生 1 条速率异常")

    def test_behavior_can_be_disabled_per_call(self):
        rg.reset_behavior()
        rg.configure_behavior(rate_max=3, denial_max=99, escalate=None)
        for i in range(5):
            rg.evaluate("srv2", f"tool{i}", behavior=False)
        self.assertEqual(rg.behavior_status()["anomaly_count"], 0)

    def test_monitor_failure_never_blocks_decision(self):
        """行为监控坏了也绝不能影响放行判定——监控不能成为新的故障点。"""
        rg.reset_behavior()
        good = rg._default_behavior
        try:
            class _Boom:
                def observe(self, *a, **k):
                    raise RuntimeError("behavior backend down")
            rg._default_behavior = _Boom()
            res = rg.evaluate("srv3", "read_file")
            self.assertEqual(res["decision"], rg.DECISION_ALLOW)
        finally:
            rg._default_behavior = good

    def test_escalation_wires_into_incident_chain(self):
        """开启升级后，行为异常应变成事故，进而可触发既有自动熔断。"""
        rg.reset_behavior()
        rg.configure_behavior(rate_max=2, denial_max=99)
        rg.enable_behavior_escalation(True)
        for i in range(3):
            rg.evaluate("srv4", f"tool{i}")
        self.assertGreaterEqual(len(rg._default_behavior._load()["anomalies"]), 1)
        policy, _ = rg._load_policy()
        self.assertIn("srv4", policy.get("incidents", {}),
                      "升级后应产生事故记录")
        rg.enable_behavior_escalation(False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
