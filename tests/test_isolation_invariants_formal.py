"""FVI v0.1 — 隔离不变量形式化证明的回归门禁。

把 `scripts/check_isolation_invariants.py`（纯 Python 有界模型检查）接进测试套件，
使三条基石不变量的"机器可检验证明"成为**每次提交都重跑**的门禁，而非一次性脚本。

与 tests/test_isolation_invariants.py（B4 经验式：拦截 spawn，证"这一次 0 spawn"）
互补：那边证运行时实例，这边证**机制**——任意（含恶意）输入下都不可能
no_execute / no_network / single_writer(E13) 被违背。这对应蓝图 Program E
的 30 天第一步「把不变量写成接入 tests/ 的机器可检验证明」。

判别力自证：除了"正确模型无反例"，还断言两个变异体**必须被抓到** —— 若检查器
对错误关系也"通过"（恒真/假绿），本测试失败。
"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import scripts.check_isolation_invariants as fvi


class TestIsolationInvariantsFormal(unittest.TestCase):
    def test_correct_model_has_no_counterexample(self):
        explored, cex, violations = fvi.explore(fvi.step_correct)
        self.assertIsNone(cex, f"正确模型出现反例：{violations}")
        self.assertEqual(violations, [])
        # 状态空间非空且有界（保证真的探索了，不是空跑）
        self.assertGreater(explored, len(fvi.HOSTILE_CORPUS))

    def test_checker_catches_op_leak_mutant(self):
        """判别力：把被扫 op 泄漏成动作的缺陷必须被抓到（否则检查器恒真）。"""
        _, cex, violations = fvi.explore(fvi.step_buggy_leak)
        self.assertTrue(cex is not None or violations,
                        "变异体 step_buggy_leak 未被抓到 → 检查器恒真（假绿）")
        self.assertTrue(any("EXEC" in v or "NET" in v for v in violations))

    def test_checker_catches_multiwriter_mutant(self):
        """判别力：单一生产者(E13)违背必须被抓到。"""
        _, cex, violations = fvi.explore(fvi.step_buggy_multiwriter)
        self.assertTrue(cex is not None or violations,
                        "变异体 step_buggy_multiwriter 未被抓到 → 检查器恒真（假绿）")
        self.assertTrue(any("SINGLE_WRITER" in v for v in violations))

    def test_checker_catches_readonly_mutant(self):
        """判别力：INV-4 read_only_input 违背必须被抓到（M3）。"""
        _, _, violations = fvi.explore(fvi.step_buggy_writes_scanned)
        self.assertTrue(violations, "M3 未被抓到 → 检查器恒真")
        self.assertTrue(any("READ_ONLY" in v for v in violations))

    def test_checker_catches_completeness_mutant(self):
        """判别力：INV-5 完备性违背必须被抓到（M4）。"""
        corpus_names = frozenset(a.name for a in fvi.HOSTILE_CORPUS)
        tc = lambda ts: fvi.completeness_check(ts, corpus_names)
        _, _, violations = fvi.explore_with_report(
            fvi.step_buggy_skip, terminal_check=tc)
        self.assertTrue(violations, "M4 未被抓到 → 检查器恒真")
        self.assertTrue(any("COMPLETENESS" in v for v in violations))

    def test_completeness_argument_matches_actual(self):
        """完备性论证的结论必须与实测穷举结果一致。"""
        arg = fvi.completeness_argument()
        report, _, _ = fvi.explore_with_report(fvi.step_correct)
        self.assertEqual(report["termination"], "exhausted")
        self.assertEqual(report["explored"], arg["upper_bound"])
        self.assertEqual(report["explored"], 2 ** len(fvi.HOSTILE_CORPUS))

    def test_script_exit_code_zero(self):
        """端到端：脚本整体退出码 0（正确模型通过 + 4 变异体均被抓）。"""
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "check_isolation_invariants.py")],
            capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(r.returncode, 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}")
        self.assertIn("INV-1/2/3/4 全部成立", r.stdout)
        self.assertIn("INV-5 完备性", r.stdout)
        self.assertIn("termination=exhausted", r.stdout)
        for mid in ("M1", "M2", "M3", "M4"):
            self.assertIn(mid, r.stdout, f"{mid} 未在输出中")


if __name__ == "__main__":
    unittest.main()
