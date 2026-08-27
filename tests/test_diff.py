"""测试：差分扫描模块"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from scanner.diff import diff_scans, diff_summary


class TestDiffScans(unittest.TestCase):

    def _mk_report(self, findings, score=50, version="4.2.2", scanned_at="2026-08-27 12:00:00"):
        return {
            "findings": findings,
            "overall_score": score,
            "scanner_version": version,
            "scanned_at": scanned_at,
        }

    def test_no_diff(self):
        findings = [{"type": "test", "description": "x", "file": "a.py"}]
        r = diff_scans(
            self._mk_report(findings, score=60),
            self._mk_report(findings, score=60),
        )
        self.assertEqual(r["new"], [])
        self.assertEqual(r["resolved"], [])
        self.assertEqual(r["changed"], [])
        self.assertEqual(r["score_delta"], 0)
        self.assertEqual(r["unchanged"], findings)

    def test_new_finding(self):
        prev = [{"type": "a", "description": "1", "file": "x"}]
        curr = prev + [{"type": "b", "description": "2", "file": "y"}]
        r = diff_scans(self._mk_report(prev), self._mk_report(curr))
        self.assertEqual(len(r["new"]), 1)
        self.assertEqual(r["new"][0]["type"], "b")
        self.assertEqual(len(r["resolved"]), 0)

    def test_resolved_finding(self):
        prev = [{"type": "a", "description": "1", "file": "x"}]
        r = diff_scans(self._mk_report(prev), self._mk_report([]))
        self.assertEqual(len(r["resolved"]), 1)
        self.assertEqual(len(r["new"]), 0)

    def test_severity_changed(self):
        prev = [{"type": "a", "description": "1", "file": "x", "severity": "low"}]
        curr = [{"type": "a", "description": "1", "file": "x", "severity": "high"}]
        r = diff_scans(self._mk_report(prev), self._mk_report(curr))
        self.assertEqual(len(r["changed"]), 1)
        self.assertEqual(r["changed"][0]["_prev_severity"], "low")
        self.assertEqual(r["changed"][0]["severity"], "high")
        self.assertEqual(len(r["unchanged"]), 0)

    def test_score_delta(self):
        r = diff_scans(
            self._mk_report([], score=40),
            self._mk_report([], score=70),
        )
        self.assertEqual(r["score_delta"], 30)
        self.assertIn("+30", r["summary"])

    def test_diff_summary_string(self):
        prev = [{"type": "a", "description": "x", "file": "f"}]
        curr = [{"type": "a", "description": "x", "file": "f"}]
        r = diff_scans(self._mk_report(prev, score=50), self._mk_report(curr, score=60))
        s = diff_summary(r)
        self.assertIn("差分扫描报告", s)
        self.assertIn("+10", s)

    def test_empty_reports(self):
        r = diff_scans(self._mk_report([]), self._mk_report([]))
        self.assertEqual(r["prev_total"], 0)
        self.assertEqual(r["curr_total"], 0)
        self.assertEqual(len(r["new"]), 0)
        self.assertEqual(len(r["resolved"]), 0)


class TestDiffSummaryFormat(unittest.TestCase):
    def _mk_report(self, findings, score=50, version="4.2.2", scanned_at="2026-08-27 12:00:00"):
        return {
            "findings": findings,
            "overall_score": score,
            "scanner_version": version,
            "scanned_at": scanned_at,
        }

    def test_new_and_resolved(self):
        prev = [{"type": "fixed", "description": "d", "file": "f"}]
        curr = [{"type": "new", "description": "e", "file": "g"}]
        r = diff_scans(self._mk_report(prev, score=50), self._mk_report(curr, score=65))
        s = diff_summary(r)
        self.assertIn("新增风险", s)
        self.assertIn("已修复", s)


if __name__ == "__main__":
    unittest.main()
