# -*- coding: utf-8 -*-
"""FVI ↔ 治理层贯通测试。

双向对账：
  ① 治理层 memory_threats 键集合 == FVI HOSTILE_CORPUS 工件名集合（6:6 同步）
  ② /api/v1/governance/policy 无 server 时返回全局视图含 memory_threats + fvi_integrated
  ③ POST action=memory_verdict 可覆写单条工件的治理决策
  ④ 篡改（增/删/改）任一侧都会让 verify_fvi_integration() 报 not ok

本测试的"验证 FVI 与治理层贯通"意图：若 HOSTILE_CORPUS 是 FVI 侧的
canonical 威胁面，治理层 memory_threats 必须与之 1:1 映射，任何单边变更
（例如 FVI 加了新工件、或治理层策略文件被人手改）都会被机器抓出，而不是
靠人眼 review 兜底。
"""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from eco import runtime_governance as rg
import scripts.check_isolation_invariants as fvi


class _TempDataMixin:
    """把模块级数据文件重定向到临时目录，测试之间互不污染。"""

    def _isolate(self):
        self._tmp = tempfile.mkdtemp(prefix="aishield_fvi_test_")
        self.addCleanup(shutil.rmtree, self._tmp, True)
        return self._tmp


class TestFviGovernanceIntegration(_TempDataMixin, unittest.TestCase):
    """FVI HOSTILE_CORPUS 与治理层 memory_threats 的双向对账。"""

    def setUp(self):
        tmp = self._isolate()
        self._orig_policy = rg.POLICY_FILE
        self._orig_audit = rg.AUDIT_LOG
        rg.POLICY_FILE = os.path.join(tmp, "governance.json")
        rg.AUDIT_LOG = os.path.join(tmp, "governance_audit.jsonl")
        self.addCleanup(setattr, rg, "POLICY_FILE", self._orig_policy)
        self.addCleanup(setattr, rg, "AUDIT_LOG", self._orig_audit)

    # ── ① 双向对账：FVI 6 工件 == 治理层 memory_threats 6 键 ──
    def test_fvi_and_policy_memory_threats_are_in_sync(self):
        """初始化策略里 memory_threats 应与 FVI HOSTILE_CORPUS 完全同步。"""
        res = rg.verify_fvi_integration()
        self.assertTrue(res["ok"],
                        f"初始策略与 FVI 不同步：缺 {res['missing_in_policy']} "
                        f"多 {res['extra_in_policy']}")
        self.assertEqual(len(res["fvi_artifacts"]), 6)
        self.assertEqual(len(res["policy_artifacts"]), 6)
        self.assertEqual(set(res["fvi_artifacts"]), set(res["policy_artifacts"]))

    def test_memory_threats_default_verdicts_match_rsi(self):
        """6 工件的默认 verdict 与 RSI 分级一致：L5 → deny，L1 良性 → observe。"""
        threats = rg.memory_threats()
        self.assertEqual(len(threats), 6)
        for name, meta in threats.items():
            if meta["has_adversary_requests"]:
                self.assertEqual(meta["rsi"], "L5", f"{name}: L5 应标 L5")
                self.assertEqual(meta["verdict"], "deny",
                                 f"{name}: 恶意工件默认 verdict 应为 deny")
            else:
                self.assertEqual(meta["rsi"], "L1", f"{name}: 良性对照应标 L1")
                self.assertEqual(meta["verdict"], "observe",
                                 f"{name}: 良性对照默认 verdict 应为 observe")

    def test_memory_threats_derived_from_fvi_canonical(self):
        """治理层 memory_threats 必须是 FVI HOSTILE_CORPUS 派生，不是手工复制。

        用 mock 把 HOSTILE_CORPUS 换成"多一个工件"的版本，重新派生应多出
        1 条；这证明是活派生（single source of truth），不是死拷贝。
        """
        orig = fvi.HOSTILE_CORPUS
        extra = orig + (fvi.Artifact("__synthetic__probe", frozenset({"exec"})),)
        fvi.HOSTILE_CORPUS = extra
        try:
            derived = rg._build_memory_threats()
            self.assertIn("__synthetic__probe", derived,
                          "新增工件未反映到派生结果 → 派生失效，是死拷贝")
            self.assertEqual(len(derived), 7)
        finally:
            fvi.HOSTILE_CORPUS = orig
        # 恢复后重新派生应回到 6
        self.assertEqual(len(rg._build_memory_threats()), 6)

    # ── ② POST action=memory_verdict 覆写决策 ──
    def test_set_memory_verdict_overwrites(self):
        """为某恶意工件覆写治理决策（例如运维确认要 allow 观察）。"""
        art = "package.json#postinstall"
        before = rg.memory_threats()[art]["verdict"]
        self.assertEqual(before, "deny")

        res = rg.set_memory_verdict(art, "observe")
        self.assertTrue(res["success"])
        after = rg.memory_threats()[art]["verdict"]
        self.assertEqual(after, "observe")

    def test_set_memory_verdict_rejects_unknown_artifact(self):
        """未知工件（不在 FVI HOSTILE_CORPUS 里）拒绝写入，不静默接受。"""
        res = rg.set_memory_verdict("__not_a_real_artifact__", "deny")
        self.assertFalse(res["success"])
        self.assertIn("unknown threat artifact", res["error"])
        # 未知工件不得污染策略
        self.assertNotIn("__not_a_real_artifact__", rg.memory_threats())

    def test_set_memory_verdict_rejects_bad_verdict(self):
        """非法 verdict 值（不在 deny/allow/observe 中）拒绝。"""
        res = rg.set_memory_verdict("package.json#postinstall", "banana")
        self.assertFalse(res["success"])
        self.assertIn("verdict", res["error"])

    # ── ③ 篡改：FVI 侧新增工件，治理层跟不上 → verify 抓出 ──
    def test_verify_catches_fvi_side_addition(self):
        """模拟 FVI 加了新工件、治理层策略未同步，verify 必须报 not ok。

        先把当前策略落盘（此时 FVI 与治理层一致 = 6 工件），然后 FVI 侧
        新增工件，此时治理层策略文件里的 memory_threats 仍是 6 个 —— 模拟
        "FVI 更新了威胁面、运维没同步刷策略文件" 的真实漂移场景。
        """
        # 先落盘一次：让治理层策略文件真实存在且含 6 工件
        policy, ok = rg._load_policy()
        self.assertTrue(ok)
        rg._save_policy(policy)

        # 然后 FVI 侧新增工件
        orig = fvi.HOSTILE_CORPUS
        fvi.HOSTILE_CORPUS = orig + (fvi.Artifact("__new_threat__", frozenset({"exec"})),)
        try:
            res = rg.verify_fvi_integration()
            self.assertFalse(res["ok"], "FVI 加工件后治理层未同步应被报出")
            self.assertIn("__new_threat__", res["missing_in_policy"])
        finally:
            fvi.HOSTILE_CORPUS = orig

    def test_verify_catches_policy_side_deletion(self):
        """模拟治理层策略文件被人手删了一个工件，verify 必须报出。"""
        # 手工删掉一个工件后保存
        policy, ok = rg._load_policy()
        self.assertTrue(ok)
        policy["memory_threats"].pop("benign_readme.md", None)
        rg._save_policy(policy)
        res = rg.verify_fvi_integration()
        self.assertFalse(res["ok"], "治理层策略缺工件应被 verify 报出")
        self.assertIn("benign_readme.md", res["missing_in_policy"])

    # ── ④ 策略损坏（fail-closed）下拒绝写入 memory_threats ──
    def test_set_memory_verdict_refuses_on_broken_policy(self):
        """策略文件损坏（fail-closed）时拒绝写入 verdict —— 不能静默降级。"""
        # 写一份损坏的策略文件
        with open(rg.POLICY_FILE, "w", encoding="utf-8") as f:
            f.write("{\"garbage\": 1}")  # 无可识别字段
        # 加载应返回 (policy_with_default_deny=True, ok=False)
        policy, ok = rg._load_policy()
        self.assertFalse(ok)
        self.assertTrue(policy.get("default_deny"))
        # 写 verdict 应抛 RuntimeError
        with self.assertRaises(RuntimeError):
            rg.set_memory_verdict("package.json#postinstall", "allow")

    # ── ⑤ 派生判表包含所有 FVI 工件的 adversary_ops ──
    def test_memory_threats_include_all_fvi_adversary_ops(self):
        """治理层 memory_threats 的 adversary_ops 必须完整反映 FVI 的 op 集合。"""
        threats = rg.memory_threats()
        for a in fvi.HOSTILE_CORPUS:
            self.assertIn(a.name, threats)
            self.assertEqual(sorted(threats[a.name]["adversary_ops"]),
                             sorted(a.adversary_requests),
                             f"{a.name}: adversary_ops 不匹配 FVI 定义")


if __name__ == "__main__":
    unittest.main()
