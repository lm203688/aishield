# -*- coding: utf-8 -*-
"""
tests/test_self_reference.py — 自指误报允许清单

AIShield 扫自己的制品时，检测器词汇 / 演示载荷 / 只读 preflight 会被自己的规则
命中（自指误报）。允许清单用来消噪，但它本身是**放大风险面**的东西——用不好就
变成"掩盖真实漏洞的后门"。本文件钉死它的安全不变量：

  1. 清单可解析且每条都有 reason（无可评审理由的条目不得存在，也不得放行）
  2. 精确匹配 (source, file, type) —— 少一个维度都不算命中
  3. 安全底线：未登记的新发现（新路径 / 新类型）绝不被抑制
  4. 单调性：抑制只降不减真实信号——新类型发现必须留在 kept 里
  5. 损坏/缺失的清单 = 空清单 = 全部保留（fail-closed，绝不反向放行）
  6. 端到端：对真实仓库跑台账外自检，未登记阻断必须为 0，且清单无腐烂条目
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from scanner import self_reference as sr  # noqa: E402
import self_scan  # noqa: E402


class TestAllowlistParsing(unittest.TestCase):

    def test_shipped_allowlist_is_valid_json(self):
        with open(sr.ALLOWLIST_PATH, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["version"], 1)
        self.assertGreaterEqual(len(data["entries"]), 1)

    def test_every_entry_has_a_reviewable_reason(self):
        al = sr.load_allowlist()
        self.assertEqual(len(al["index"]), len(al["entries"]),
                         "所有条目都应进入索引（说明字段完整）")
        for e in al["entries"]:
            self.assertTrue(e["reason"].strip(),
                            f"条目缺理由，等于无声放行: {e}")

    def test_missing_file_yields_empty_not_permissive(self):
        al = sr.load_allowlist("/nonexistent/allowlist.json")
        self.assertEqual(al["index"], {})
        kept, sup = sr.split_findings("x", [{"file": "a", "type": "t"}], al)
        self.assertEqual(len(kept), 1)
        self.assertEqual(sup, [], "清单缺失时必须全部保留（fail-closed）")

    def test_corrupt_file_yields_empty(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as f:
            f.write("{ not json ]")
            bad = f.name
        self.addCleanup(os.unlink, bad)
        self.assertEqual(sr.load_allowlist(bad)["index"], {})


class TestMatching(unittest.TestCase):

    def setUp(self):
        self.al = sr.load_allowlist()

    def test_known_combo_matches(self):
        entry = sr.match("mcp-server/src",
                         {"file": "index.ts", "type": "dangerous_pattern"}, self.al)
        self.assertIsNotNone(entry)
        self.assertTrue(entry["reason"])

    def test_wrong_type_does_not_match(self):
        """同文件不同类型的发现不能蹭同一条目。"""
        self.assertIsNone(sr.match("mcp-server/src",
                                   {"file": "index.ts", "type": "secrets_hardcoded"}, self.al))

    def test_wrong_file_does_not_match(self):
        self.assertIsNone(sr.match("mcp-server/src",
                                   {"file": "other.ts", "type": "dangerous_pattern"}, self.al))

    def test_wrong_source_does_not_match(self):
        self.assertIsNone(sr.match("some/other/dir",
                                   {"file": "index.ts", "type": "dangerous_pattern"}, self.al))

    def test_known_findings_are_suppressed_with_reason(self):
        findings = [{"file": "index.ts", "type": "dangerous_pattern", "severity": "critical"}]
        kept, sup = sr.split_findings("mcp-server/src", findings, self.al)
        self.assertEqual(kept, [])
        self.assertEqual(len(sup), 1)
        self.assertIn("reason", sup[0]["self_reference"])

    def test_safety_floor_new_type_never_suppressed(self):
        """安全底线：同一文件上冒出的**新类型**发现必须照旧暴露。"""
        findings = [{"file": "index.ts", "type": "data_exfiltration_live",
                     "severity": "critical"}]
        kept, sup = sr.split_findings("mcp-server/src", findings, self.al)
        self.assertEqual(len(kept), 1, "未登记的新类型不得被抑制")
        self.assertEqual(sup, [])

    def test_safety_floor_new_path_never_suppressed(self):
        findings = [{"file": "brand_new_file.py", "type": "dangerous_pattern",
                     "severity": "high"}]
        kept, sup = sr.split_findings("mcp-server/src", findings, self.al)
        self.assertEqual(len(kept), 1)
        self.assertEqual(sup, [])

    def test_mixed_findings_split_correctly(self):
        findings = [
            {"file": "index.ts", "type": "dangerous_pattern"},
            {"file": "index.ts", "type": "secrets_hardcoded"},
        ]
        kept, sup = sr.split_findings("mcp-server/src", findings, self.al)
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]["type"], "secrets_hardcoded")
        self.assertEqual(len(sup), 1)

    def test_blocking_of_filters_severities(self):
        fs = [{"severity": "critical"}, {"severity": "high"},
              {"severity": "medium"}, {"severity": "low"}]
        self.assertEqual(len(sr.blocking_of(fs)), 2)


class TestSelfScanEndToEnd(unittest.TestCase):
    """对真实仓库跑一遍台账外自检（只读，不联网）。"""

    @classmethod
    def setUpClass(cls):
        cls.summary = self_scan.scan()

    def test_no_unregistered_blocking_findings(self):
        self.assertEqual(self.summary["totals"]["blocking_unsuppressed"], 0,
                         "存在未登记的自指误报之外的真实阻断项: %s" % self.summary)

    def test_allowlist_has_no_rot(self):
        """清单腐烂检测：每条都应仍匹配实际发现，否则提示清理。"""
        self.assertEqual(self.summary["stale_allowlist_entries"], [],
                         "允许清单有已失效条目，应清理以免误导: %s"
                         % self.summary["stale_allowlist_entries"])

    def test_noise_is_actually_suppressed(self):
        self.assertGreater(self.summary["totals"]["suppressed"], 0,
                           "清单未抑制任何命中，可能已失效")

    def test_overall_ok(self):
        self.assertTrue(self.summary["ok"])

    def test_invariants_declared(self):
        self.assertTrue(self.summary["invariants"]["no_execute"])
        self.assertTrue(self.summary["invariants"]["no_network"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
