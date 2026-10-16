# -*- coding: utf-8 -*-
"""
tests/test_rses_cycle.py — Program B (RSES) 安全自进化闭环门禁测试

钉死闭环不变量：
  1. 草拟元 agent 结构上不含任何晋升/降级/回滚特权方法（FORBIDDEN_METHODS 全缺）。
  2. 进化账本哈希链通过 verify_chain()（append-only + 不可篡改）。
  3. `meta:` 前缀 actor 从未在账本中执行过特权动作（双保险）。
  4. 闭环能起草→自测→（ready 则）提交晋升审议；坏草稿被安全拒绝。
"""
import os
import tempfile
import unittest

from eco.meta_agent import DraftingMetaAgent
from eco import evolution_ledger as ledger
from scripts.rses_cycle import RSSESCycle


class TestRSESLoop(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rses_test_")
        self.prop_dir = os.path.join(self.tmp, "proposed")
        self.lg_path = os.path.join(self.tmp, "evolution_ledger.jsonl")
        os.makedirs(self.prop_dir, exist_ok=True)
        self.cycle = RSSESCycle(proposals_dir=self.prop_dir,
                                ledger_path=self.lg_path)

    def test_forbidden_methods_absent_on_agent(self):
        cls = type(self.cycle.agent)
        for m in cls.FORBIDDEN_METHODS:
            self.assertFalse(hasattr(cls, m),
                             "草拟元 agent 不得含特权方法 %r" % m)

    def test_meta_agent_cannot_promote(self):
        self.assertFalse(hasattr(type(self.cycle.agent), "promote"))
        self.assertFalse(hasattr(type(self.cycle.agent), "promote_rule"))

    def test_ledger_chain_verified_after_cycle(self):
        sig = {
            "signal_id": "intel-test-1",
            "signal_title": "Demo injection via alt text",
            "signal_url": "https://example.com/INTEL-TEST-1",
            "pattern": r'!\[[^\]]*\]\([^)]*\)',
            "description": "Markdown 图片 alt 文本间接注入（演示）",
            "severity": "low", "attack_category": "MCP06",
        }
        self.cycle.run([sig])
        audit = self.cycle.self_audit()
        self.assertTrue(audit["ok"], "闭环不变量自检失败: %r" % audit)

    def test_self_audit_passes_on_clean_ledger(self):
        audit = self.cycle.self_audit()
        self.assertTrue(audit["ledger_chain_verified"])
        self.assertEqual(audit["meta_agent_privileged_violations"], [])

    def test_meta_actor_privileged_action_rejected_by_ledger(self):
        # 即便有人试图用 meta: actor 调 ledger.record 晋升，也必须被拒
        with self.assertRaises(ValueError):
            ledger.record(actor="meta:rogue", action="promote",
                          target="data/radar_rules.json",
                          approved_by="someone",
                          path=self.lg_path)
        # 正常 human 晋升则允许（对照）
        e = ledger.record(actor="human:reviewer", action="promote",
                          target="data/radar_rules.json",
                          approved_by="human:reviewer", path=self.lg_path)
        self.assertEqual(e["action"], "promote")

    def test_bad_draft_is_safely_rejected(self):
        # 过短模式 → 起草期 ValueError，闭环计入 rejected，不污染账本为 ready
        bad = {
            "signal_id": "intel-bad-1", "signal_title": "Bad",
            "signal_url": "https://example.com/bad",
            "pattern": "x", "description": "too short", "severity": "low",
        }
        res = self.cycle.run([bad])
        self.assertEqual(res["rejected"], 1)
        self.assertEqual(res["submitted"], 0)


if __name__ == "__main__":
    unittest.main()
