"""L2 策略贯通（scan pack → runtime PEP）的回归测试。

测的是一件事：**扫描期的策略包在运行时真的按同一口径生效**，
且**不因为贯通而误伤存量**。

防假绿要点（每条用例都必须能真的失败）：
  - 编译产物的 deny 集合必须与 pack 的 excluded_categories 同集合，不能多也不能少；
  - red-team 是「永不 fail」语义，编译后**绝不能**产生任何运行时拒绝能力；
  - 未知类别（pack 未覆盖的新类别）一律放行，否则生态一升级生产就炸；
  - 未绑 pack 的 server 运行时行为必须与贯通前逐字一致；
  - 扫描期严格度与运行时严格度必须**同向**（strict 在两边都比 default 严）。
"""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from eco import policy_bridge as pb
from eco import runtime_governance as rg

ASI10 = [f"ASI{i:02d}" for i in range(1, 11)]


class _HermeticRuntimeGovernance(unittest.TestCase):
    """把治理状态重定向到临时目录，绝不碰 api/data/ 下的真实文件。"""

    def setUp(self):
        self._orig_policy = rg.POLICY_FILE
        self._orig_audit = rg.AUDIT_LOG
        self._tmp = tempfile.mkdtemp(prefix="policybridge-")
        rg.POLICY_FILE = os.path.join(self._tmp, "governance.json")
        rg.AUDIT_LOG = os.path.join(self._tmp, "audit.jsonl")
        self.g = rg.RuntimeGovernor()

    def tearDown(self):
        rg.POLICY_FILE = self._orig_policy
        rg.AUDIT_LOG = self._orig_audit
        shutil.rmtree(self._tmp, ignore_errors=True)


class TestPackCompile(unittest.TestCase):
    """编译层：忠实映射，不编造、不放大。"""

    def test_all_builtin_packs_compile(self):
        for name in pb.pack_names():
            c = pb.compile_pack(name)
            self.assertEqual(c["source_pack"], name)
            self.assertTrue(c["rationale"], f"{name} 的 rationale 为空 = 不可解释")

    def test_mcp_only_deny_is_exactly_asi_family(self):
        rt = pb.compile_pack("mcp-only")["runtime"]
        self.assertEqual(rt["deny_categories"], ASI10)
        self.assertEqual(rt["allow_categories"],
                         ["MCP01", "MCP02", "MCP03", "MCP04", "MCP05",
                          "MCP06", "MCP07", "MCP08", "MCP09", "MCP10"])

    def test_personal_agent_deny_is_exactly_mcp04(self):
        rt = pb.compile_pack("personal-agent")["runtime"]
        self.assertEqual(rt["deny_categories"], ["MCP04"])
        self.assertEqual(rt["severity_floor"], "low")

    def test_red_team_never_produces_runtime_deny(self):
        """red-team 语义是「永不 fail」，编译后绝不能获得拒绝能力。"""
        rt = pb.compile_pack("red-team")["runtime"]
        self.assertEqual(rt["deny_categories"], [])
        self.assertFalse(rt["default_deny"])
        self.assertEqual(rt["strictness"], pb.STRICTNESS_OBSERVE)

    def test_default_pack_is_equivalent_to_no_pack(self):
        """default pack 没有类别约束 → 运行时不得产生任何额外拒绝。"""
        rt = pb.compile_pack("default")["runtime"]
        self.assertEqual(rt["deny_categories"], [])
        self.assertFalse(rt["default_deny"])
        self.assertEqual(rt["severity_floor"], "info")

    def test_severity_floor_follows_pack_min(self):
        self.assertEqual(pb.compile_pack("strict")["runtime"]["severity_floor"], "low")
        self.assertEqual(pb.compile_pack("default")["runtime"]["severity_floor"], "info")

    def test_unknown_pack_raises(self):
        with self.assertRaises(KeyError):
            pb.compile_pack("no-such-pack")

    def test_category_exact_enumeration_match(self):
        """pack 里是 ASI01..ASI10 全枚举 → 精确命中，不多不少。"""
        self.assertTrue(pb.category_matches("ASI03", ASI10))
        self.assertTrue(pb.category_matches("ASI10", ASI10))
        self.assertFalse(pb.category_matches("ASI11", ASI10))

    def test_category_glob_match(self):
        """pack 允许写 ASI* 这类族匹配（前缀），给策略作者留口子。"""
        self.assertTrue(pb.category_matches("ASI03", ["ASI"]))
        self.assertTrue(pb.category_matches("ASI03", ["ASI*"]))
        self.assertFalse(pb.category_matches("MCP07", ["ASI"]))
        self.assertFalse(pb.category_matches("", ["ASI03"]))
        self.assertFalse(pb.category_matches("ASI03", []))

    def test_strict_runtime_opt_in_pushes_default_deny(self):
        """只有运维显式同意，fail_on 才推成 default_deny（否则生产会全停）。"""
        self.assertFalse(pb.compile_pack("strict")["runtime"]["default_deny"])
        on = pb.compile_pack("strict", strict_runtime=True)["runtime"]
        self.assertTrue(on["default_deny"])
        self.assertEqual(on["strictness"], pb.STRICTNESS_ENFORCING)


class TestPackRuntimeEnforcement(_HermeticRuntimeGovernance):
    """运行时层：pack 的 excluded_categories 产生真拒绝。"""

    def test_denied_category_is_blocked_at_runtime(self):
        rg.bind_pack("srv", "mcp-only")
        r = self.g.evaluate("srv", "tool", context={"category": "ASI03"})
        self.assertFalse(r["allowed"])
        self.assertEqual(r["reason"], "命中 policy pack「mcp-only」排除的类别 ASI03")
        self.assertEqual(r["policy_hit"], "pack_excluded_category")

    def test_allowed_category_passes(self):
        rg.bind_pack("srv", "mcp-only")
        self.assertTrue(self.g.evaluate("srv", "tool", context={"category": "MCP07"})["allowed"])

    def test_missing_category_is_not_penalized(self):
        """没给 category 的调用不能被 pack 拒 —— 否则存量调用全挂。"""
        rg.bind_pack("srv", "mcp-only")
        self.assertTrue(self.g.evaluate("srv", "tool")["allowed"])

    def test_unlisted_category_is_not_penalized(self):
        """未来新类别（如 MCP11）不在 pack 表里，必须放行，只打观察标记。"""
        rg.bind_pack("srv", "personal-agent")
        r = self.g.evaluate("srv", "tool", context={"category": "MCP11"})
        self.assertTrue(r["allowed"])
        self.assertTrue(r["pack"]["unlisted_category"])

    def test_below_floor_is_observation_only(self):
        rg.bind_pack("srv", "strict")  # severity_floor = low
        r = self.g.evaluate("srv", "tool", context={"category": "MCP01", "severity": "info"})
        self.assertTrue(r["allowed"])
        self.assertTrue(r["pack"]["below_severity_floor"])

    def test_above_floor_has_no_floor_flag(self):
        rg.bind_pack("srv", "strict")
        r = self.g.evaluate("srv", "tool", context={"category": "MCP01", "severity": "critical"})
        self.assertTrue(r["allowed"])
        self.assertNotIn("below_severity_floor", r["pack"])

    def test_red_team_bound_produces_no_deny(self):
        rg.bind_pack("srv", "red-team")
        self.assertTrue(self.g.evaluate("srv", "t", context={"category": "ASI09"})["allowed"])

    def test_kill_switch_still_wins_over_pack(self):
        rg.bind_pack("srv", "mcp-only")
        self.g.kill("srv", reason="test")
        r = self.g.evaluate("srv", "t", context={"category": "MCP07"})
        self.assertEqual(r["policy_hit"], "kill_switch")

    def test_explicit_deny_list_still_wins(self):
        rg.bind_pack("srv", "mcp-only")
        self.g.deny_tool("srv", "*")
        r = self.g.evaluate("srv", "t", context={"category": "MCP07"})
        self.assertFalse(r["allowed"])
        self.assertEqual(r["policy_hit"], "deny_list")
        self.g.clear_rule("deny", "srv")

    def test_unbind_restores_default_behavior(self):
        rg.bind_pack("srv", "mcp-only")
        self.assertFalse(self.g.evaluate("srv", "t", context={"category": "ASI03"})["allowed"])
        self.assertTrue(rg.unbind_pack("srv"))
        self.assertTrue(self.g.evaluate("srv", "t", context={"category": "ASI03"})["allowed"])

    def test_unbind_unknown_server_is_false(self):
        self.assertFalse(rg.unbind_pack("nobody"))

    def test_bound_pack_is_introspectable(self):
        rg.bind_pack("srv", "personal-agent")
        ent = rg.bound_pack("srv")
        self.assertEqual(ent["source_pack"], "personal-agent")
        self.assertEqual(ent["runtime"]["deny_categories"], ["MCP04"])
        self.assertTrue(ent["rationale"])
        self.assertIsNone(rg.bound_pack("nobody"))


class TestNoRegressionOnUnbound(_HermeticRuntimeGovernance):
    """未绑 pack 的 server，行为必须与贯通前逐字一致。"""

    def test_unbound_server_behavior_unchanged(self):
        r = self.g.evaluate("srv", "tool")
        self.assertTrue(r["allowed"])
        self.assertEqual(r["policy_hit"], "default_allow")

    def test_unbound_server_still_honors_default_deny(self):
        self.g.set_default_deny(True)
        r = self.g.evaluate("srv", "tool")
        self.assertFalse(r["allowed"])
        self.assertEqual(r["policy_hit"], "default_deny")

    def test_unbound_server_has_no_pack_key(self):
        r = self.g.evaluate("srv", "tool")
        self.assertEqual(r["pack"], {})


class TestBrokenPolicyIsRefused(_HermeticRuntimeGovernance):
    """策略损坏时拒绝绑定，而不是在 fail-closed 状态下写入归属。"""

    def test_bind_on_corrupt_policy_raises(self):
        with open(rg.POLICY_FILE, "w", encoding="utf-8") as f:
            f.write("{ this is not json")
        with self.assertRaises(RuntimeError):
            rg.bind_pack("srv", "mcp-only")
        # 损坏状态下更不能把 pack 写进去
        self.assertIsNone(rg.bound_pack("srv"))


class TestConsistencyBetweenScanAndRuntime(unittest.TestCase):
    """贯通的核心断言：同一 pack 在扫描期与运行期的严格度必须同向。"""

    def test_strict_is_not_looser_than_default_in_runtime(self):
        from scanner import policy_pack as _pp

        strict = pb.compile_pack("strict")
        default = pb.compile_pack("default")

        # 扫描期：strict 的 fail_on 严格度 >= default
        # 注意方向：fail_on 是「什么严重度以上会 fail」，值越大越**宽松**
        # （critical 才 fail < high < medium < low < info 都 fail），
        # impossible = 永不 fail = 最宽。越严则 rank 越大。
        cfg_s = _pp.load_pack("strict")["config"]["fail_on"]
        cfg_d = _pp.load_pack("default")["config"]["fail_on"]
        rank = {"impossible": 0, "critical": 1, "high": 2, "medium": 3,
                "low": 4, "info": 5}
        self.assertGreaterEqual(rank[cfg_s], rank[cfg_d],
                                "strict 的 fail_on 必须不比 default 宽松")

        # 运行时：strict 的 severity_floor 严格度 >= default
        floor_rank = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        self.assertGreaterEqual(
            floor_rank[strict["runtime"]["severity_floor"]],
            floor_rank[default["runtime"]["severity_floor"]],
        )

    def test_mcp_only_runtime_deny_matches_scan_exclusion(self):
        """扫描期排除的类别，运行时必须正好拒绝 —— 多一个少一个都算错。"""
        cfg = __import__("scanner.policy_pack", fromlist=["x"]).load_pack("mcp-only")["config"]
        excluded = set(cfg["excluded_categories"])
        denied = set(pb.compile_pack("mcp-only")["runtime"]["deny_categories"])
        self.assertEqual(denied, excluded)


if __name__ == "__main__":
    unittest.main(verbosity=2)
