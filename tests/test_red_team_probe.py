# -*- coding: utf-8 -*-
"""
AIShield · Red-team Probe 测试 — tests/test_red_team_probe.py
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scanner.red_team_probe import (
    _PROBES,
    _extract_hit_ids,
    coverage_report,
    get_all_probes,
    get_probe,
    list_probes,
    run_probes,
    summarize_probes,
)


class TestProbeCatalog(unittest.TestCase):
    def test_probes_have_required_fields(self):
        for p in _PROBES:
            for k in ("id", "name", "category", "severity", "payload",
                      "expected_types", "notes"):
                self.assertIn(k, p, f"probe {p.get('id')} missing {k}")
            self.assertTrue(p["id"])
            self.assertTrue(p["name"])
            self.assertTrue(p["payload"])
            self.assertIsInstance(p["expected_types"], set)

    def test_probe_ids_unique(self):
        ids = [p["id"] for p in _PROBES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_ids_follow_naming_convention(self):
        """probe id 应形如 MCP01-1 / ASI04-1。"""
        import re
        pattern = re.compile(r"^(MCP|MCP0?\d|ASI)\d?-\d+$|^(MCP|ASI)\d{2}-\d+$")
        for pid in [p["id"] for p in _PROBES]:
            self.assertTrue(
                re.match(r"^(MCP|ASI)\d{2}-\d+$", pid),
                f"probe id {pid!r} doesn't match MCP/ASI NN-N convention",
            )

    def test_severities_valid(self):
        valid = {"info", "low", "medium", "high", "critical"}
        for p in _PROBES:
            self.assertIn(p["severity"], valid)

    def test_categories_are_owasp(self):
        for p in _PROBES:
            self.assertTrue(
                p["category"].startswith(("MCP", "ASI")),
                f"probe {p['id']} category {p['category']!r} not OWASP",
            )

    def test_expected_types_are_owasp_categories(self):
        """expected_types 应是 OWASP 类别（MCP01-10, ASI01-10）。"""
        for p in _PROBES:
            for t in p["expected_types"]:
                self.assertTrue(
                    t.startswith(("MCP", "ASI")),
                    f"probe {p['id']} expected_type {t!r} not OWASP category",
                )


class TestListAndGet(unittest.TestCase):
    def test_list_probes(self):
        ids = list_probes()
        self.assertGreater(len(ids), 10)
        self.assertIn("MCP01-1", ids)

    def test_get_probe_by_id(self):
        p = get_probe("MCP01-1")
        self.assertIsNotNone(p)
        self.assertEqual(p["id"], "MCP01-1")

    def test_get_probe_missing(self):
        self.assertIsNone(get_probe("MCP99-99"))

    def test_get_all_probes_returns_copy(self):
        a = get_all_probes()
        b = get_all_probes()
        self.assertIsNot(a, b)
        # 修改一个副本不影响另一个
        a[0]["name"] = "MODIFIED"
        self.assertNotEqual(a[0]["name"], b[0]["name"])


class TestSummarize(unittest.TestCase):
    def test_total_matches_probes(self):
        s = summarize_probes()
        self.assertEqual(s["total"], len(_PROBES))

    def test_by_category_sums_correct(self):
        s = summarize_probes()
        total = sum(s["by_category"].values())
        self.assertEqual(total, s["total"])

    def test_by_severity_sums_correct(self):
        s = summarize_probes()
        total = sum(s["by_severity"].values())
        self.assertEqual(total, s["total"])

    def test_coverage_report_alias(self):
        """coverage_report 是 summarize_probes 的别名。"""
        self.assertEqual(coverage_report(), summarize_probes())


class TestExtractHitIds(unittest.TestCase):
    def test_extracts_rule_id_prefix(self):
        findings = [{"rule_id": "MCP01-001"}]
        hits = _extract_hit_ids(findings)
        self.assertIn("MCP01", hits)

    def test_extracts_owasp_category(self):
        findings = [{"owasp_category": "MCP06"}]
        hits = _extract_hit_ids(findings)
        self.assertIn("MCP06", hits)

    def test_extracts_type_field(self):
        findings = [{"type": "dangerous_pattern"}]
        hits = _extract_hit_ids(findings)
        self.assertIn("dangerous_pattern", hits)

    def test_empty_findings(self):
        self.assertEqual(_extract_hit_ids([]), set())

    def test_multiple_findings_dedup(self):
        findings = [
            {"rule_id": "MCP01-001"},
            {"rule_id": "MCP01-002"},
            {"owasp_category": "MCP06"},
        ]
        hits = _extract_hit_ids(findings)
        self.assertIn("MCP01", hits)
        self.assertIn("MCP06", hits)


class TestRunProbesNoEngine(unittest.TestCase):
    def test_returns_all_probes(self):
        r = run_probes(None)
        self.assertEqual(r["total"], len(_PROBES))
        self.assertEqual(r["engine_used"], False)
        # 每个 probe 都有结果
        self.assertEqual(len(r["results"]), len(_PROBES))

    def test_passed_is_none_when_no_engine(self):
        r = run_probes(None)
        for pid, res in r["results"].items():
            self.assertIsNone(res["passed"])


class TestRunProbesWithEngine(unittest.TestCase):
    def _make_engine(self, hits):
        """构造一个 mock engine，返回固定的 findings。"""
        def engine(payload):
            return [{"rule_id": f"{h}-001", "owasp_category": h}
                    for h in hits]
        return engine

    def test_engine_with_matching_hit(self):
        r = run_probes(self._make_engine({"MCP06"}))
        # MCP01-1 (expected MCP06) should pass
        self.assertTrue(r["results"]["MCP01-1"]["passed"])

    def test_engine_with_no_matching_hit(self):
        r = run_probes(self._make_engine({"ASI09"}))
        # MCP01-1 (expected MCP06) should fail
        self.assertFalse(r["results"]["MCP01-1"]["passed"])

    def test_engine_raises_handled_gracefully(self):
        def bad_engine(payload):
            raise ValueError("boom")
        r = run_probes(bad_engine)
        # 所有 probe 都 fail，但都有 error 字段
        for pid, res in r["results"].items():
            self.assertFalse(res["passed"])
            self.assertIn("error", res)
        self.assertEqual(r["failed"], len(_PROBES))

    def test_engine_returns_none(self):
        def empty_engine(payload):
            return None
        r = run_probes(empty_engine)
        # 所有 expected 非空 → fail
        for pid, res in r["results"].items():
            self.assertFalse(res["passed"])


class TestCoverageReport(unittest.TestCase):
    def test_report_structure(self):
        r = coverage_report()
        for k in ("total", "by_category", "by_severity"):
            self.assertIn(k, r)

    def test_categories_are_owasp(self):
        r = coverage_report()
        for cat in r["by_category"]:
            self.assertTrue(cat.startswith(("MCP", "ASI")))


if __name__ == "__main__":
    unittest.main()
