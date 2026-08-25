"""scanner/vertical_risk.py — 垂直场景风险审查测试"""
import sys, os
import unittest

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from scanner import vertical_risk


class VerticalRiskTest(unittest.TestCase):
    def test_finance_hits_multiple_terms(self):
        r = vertical_risk.scan_vertical_risk("这个庄家拉升的币稳赚不赔，代客理财保本保息")
        self.assertEqual(r["domain"], "finance")
        self.assertFalse(r["safe"])
        self.assertEqual(r["risk_level"], "high")
        self.assertGreaterEqual(r["found_count"], 3)
        self.assertTrue(any(f["term"] == "稳赚不赔" for f in r["found"]))

    def test_finance_no_hit(self):
        r = vertical_risk.scan_vertical_risk("今天学习 Python 语法")
        self.assertTrue(r["safe"])
        self.assertEqual(r["risk_level"], "none")
        self.assertEqual(r["found_count"], 0)

    def test_medical_high_risk(self):
        t = "祖传秘方包治百病，根治癌症不用吃药，百分百治愈"
        r = vertical_risk.scan_vertical_risk(t, "medical")
        self.assertEqual(r["domain"], "medical")
        self.assertFalse(r["safe"])
        self.assertEqual(r["risk_level"], "high")
        self.assertGreaterEqual(r["found_count"], 3)

    def test_medical_low_risk(self):
        r = vertical_risk.scan_vertical_risk("偏方可以根治癌症", "medical")
        self.assertFalse(r["safe"])
        self.assertEqual(r["risk_level"], "low")

    def test_gov_medium_risk(self):
        t = "内部文件泄露，涉及涉密资料"
        r = vertical_risk.scan_vertical_risk(t, "gov")
        self.assertFalse(r["safe"])
        self.assertEqual(r["risk_level"], "medium")

    def test_scan_all_domains_clean(self):
        r = vertical_risk.scan_all_domains("今天天气很好")
        self.assertTrue(r["safe"])
        self.assertEqual(r["blocking_domains"], [])
        self.assertEqual(set(r["per_domain"]), {"finance", "medical", "gov"})

    def test_scan_all_domains_mixed(self):
        t = "庄家拉升稳赚不赔，且这是祖传秘方"
        r = vertical_risk.scan_all_domains(t)
        self.assertFalse(r["safe"])
        self.assertIn("finance", r["blocking_domains"])
        self.assertIn("medical", r["blocking_domains"])

    def test_invalid_domain_returns_error(self):
        r = vertical_risk.scan_vertical_risk("x", "nonexistent")
        self.assertIn("error", r)
        self.assertIn("available", r)

    def test_position_and_context_are_valid(self):
        r = vertical_risk.scan_vertical_risk("prefix稳赚不赔suffix", "finance")
        hit = r["found"][0]
        self.assertGreater(hit["position"], 0)
        self.assertTrue(hit["context"])

    def test_empty_text_is_safe(self):
        self.assertTrue(vertical_risk.scan_vertical_risk("", "finance")["safe"])


if __name__ == "__main__":
    unittest.main()
