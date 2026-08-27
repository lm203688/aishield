"""测试：Fuzzing 模块"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from scanner.fuzzing import fuzz, FuzzReport, FuzzVector


class TestFuzz(unittest.TestCase):

    def test_fuzz_returns_report(self):
        sample = '{"token": "secret123", "password": "admin"}'
        report = fuzz(sample, max_mutations=20, seed=42)
        self.assertIsInstance(report, FuzzReport)
        self.assertGreater(report.total_mutations, 0)

    def test_fuzz_detection_runs(self):
        sample = '{"password": "secret", "token": "api_key"}'
        report = fuzz(sample, max_mutations=30, seed=123)
        # 检测+漏网总数等于变异数
        self.assertEqual(report.detected_count + report.undetected_count, report.total_mutations)

    def test_fuzz_coverage_field(self):
        sample = '{"token": "abc"}'
        report = fuzz(sample, max_mutations=10, seed=99)
        self.assertIsInstance(report.coverage_pct, float)
        self.assertGreaterEqual(report.coverage_pct, 0.0)
        self.assertLessEqual(report.coverage_pct, 100.0)

    def test_fuzz_summary(self):
        sample = '{"eval": "code"}'
        report = fuzz(sample, max_mutations=15, seed=7)
        self.assertIn("变异", report.summary)
        self.assertIn("%", report.summary)

    def test_fuzz_new_vectors_type(self):
        sample = '{"secret": "data"}'
        report = fuzz(sample, max_mutations=20, seed=55)
        self.assertIsInstance(report.new_vectors, list)

    def test_fuzz_to_dict(self):
        sample = '{"token": "x"}'
        report = fuzz(sample, max_mutations=10, seed=1)
        d = report.to_dict()
        self.assertIn("new_vector_count", d)
        self.assertIn("new_vector_categories", d)
        self.assertIn("coverage_pct", d)

    def test_fuzz_reproducibility(self):
        sample = '{"password": "abc"}'
        r1 = fuzz(sample, max_mutations=10, seed=42)
        r2 = fuzz(sample, max_mutations=10, seed=42)
        self.assertEqual(r1.total_mutations, r2.total_mutations)
        self.assertEqual(r1.detected_count, r2.detected_count)

    def test_fuzz_empty_input(self):
        report = fuzz("", max_mutations=5, seed=1)
        self.assertEqual(report.total_mutations, 0)

    def test_fuzz_vector_structure(self):
        sample = '{"password": "abc"}'
        report = fuzz(sample, max_mutations=20, seed=1)
        for v in report.new_vectors:
            self.assertIsInstance(v, FuzzVector)
            self.assertIn(v.category, ("encoding", "structure", "semantic"))
            self.assertIsInstance(v.vector_id, str)
            self.assertIsInstance(v.input_variant, str)


class TestSynonymMap(unittest.TestCase):
    def test_synonym_keys(self):
        from scanner.fuzzing import SYNONYM_MAP
        self.assertIn("eval", SYNONYM_MAP)
        self.assertIn("password", SYNONYM_MAP)
        self.assertGreater(len(SYNONYM_MAP), 5)


if __name__ == "__main__":
    unittest.main()
