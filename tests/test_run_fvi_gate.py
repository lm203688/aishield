# -*- coding: utf-8 -*-
"""
tests/test_run_fvi_gate.py — Program E（FVI）CI 门禁入口测试

钉死：
  1. 有界模型检查层对"正确模型零反例 + 两缺陷变异体必须被抓"返回 rc=0。
  2. 若把判别力自证去掉（检查器对变异体也放行），门禁必须失败而非假绿。
"""
import unittest

import scripts.run_fvi_gate as gate
import scripts.check_isolation_invariants as fvi


class TestFviGate(unittest.TestCase):
    def test_model_check_layer_passes(self):
        rc, summary = gate._run_model_check()
        self.assertEqual(rc, 0, summary)
        # 正确模型确实探索了非空状态空间（不是空跑）
        self.assertIn("[PASS] 正确模型", summary)

    def test_discriminative_power_enforced(self):
        """判别力：两个缺陷变异体都必须在 summary 里被记为 PASS。"""
        rc, summary = gate._run_model_check()
        self.assertEqual(rc, 0)
        self.assertIn("判别力：step_buggy_leak 被抓到", summary)
        self.assertIn("判别力：step_buggy_multiwriter 被抓到", summary)

    def test_gate_logic_fails_on_weak_checker(self):
        """防假绿：若检查器对变异体也放行，门禁必须非零。"""
        # 临时把变异体替换为"永远不违规"的恒真函数
        orig_leak = fvi.step_buggy_leak

        def _always_ok(s, a):
            ns = fvi.step_correct(s, a)
            return ns
        fvi.step_buggy_leak = _always_ok
        try:
            rc, summary = gate._run_model_check()
            self.assertNotEqual(rc, 0)
            self.assertIn("判别力缺失", summary)
        finally:
            fvi.step_buggy_leak = orig_leak


if __name__ == "__main__":
    unittest.main()
