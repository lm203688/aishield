# -*- coding: utf-8 -*-
"""
AIShield · Policy Packs 测试 — tests/test_policy_pack.py
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scanner.policy_pack import (
    DEFAULT_PACK,
    STRICT_PACK,
    MCP_ONLY_PACK,
    PERSONAL_AGENT_PACK,
    RED_TEAM_PACK,
    apply_pack,
    list_packs,
    load_pack,
    write_builtin_packs,
    _match_any,
    _severity_rank,
)


def _mk_findings():
    """构造覆盖所有 severity / category 的 findings。"""
    return {
        "findings": [
            {"type": "info_a", "severity": "info", "owasp_category": "MCP01", "file": "a.py"},
            {"type": "low_b", "severity": "low", "owasp_category": "MCP02", "file": "b.py"},
            {"type": "medium_c", "severity": "medium", "owasp_category": "MCP03", "file": "c.py"},
            {"type": "high_d", "severity": "high", "owasp_category": "MCP04", "file": "d.py"},
            {"type": "crit_e", "severity": "critical", "owasp_category": "ASI06", "file": "e.py"},
            {"type": "info_log", "severity": "info", "owasp_category": "MCP01", "file": "test.log"},
        ],
        "summary": {"total_findings": 6},
    }


class TestLoadPack(unittest.TestCase):
    def test_load_default(self):
        p = load_pack("default")
        self.assertEqual(p["name"], "default")
        self.assertIn("config", p)

    def test_load_all_builtins(self):
        for name in ["default", "strict", "mcp-only", "personal-agent", "red-team"]:
            p = load_pack(name)
            self.assertEqual(p["name"], name)

    def test_load_missing_raises(self):
        with self.assertRaises(KeyError):
            load_pack("nonexistent-pack")

    def test_list_packs_returns_all(self):
        names = list_packs()
        for n in ["default", "strict", "mcp-only", "personal-agent", "red-team"]:
            self.assertIn(n, names)


class TestSeverityRank(unittest.TestCase):
    def test_ordering(self):
        self.assertLess(_severity_rank("info"), _severity_rank("low"))
        self.assertLess(_severity_rank("low"), _severity_rank("medium"))
        self.assertLess(_severity_rank("medium"), _severity_rank("high"))
        self.assertLess(_severity_rank("high"), _severity_rank("critical"))

    def test_unknown_returns_negative(self):
        self.assertLess(_severity_rank("unknown_sev"), 0)


class TestApplyPackDefault(unittest.TestCase):
    def test_default_passes_only_if_no_critical(self):
        report = _mk_findings()
        result = apply_pack(report, DEFAULT_PACK)
        # 有 critical → 默认 fail
        self.assertFalse(result["pass"])

    def test_default_passes_with_no_critical(self):
        report = {
            "findings": [
                {"type": "a", "severity": "high", "owasp_category": "MCP01", "file": "a.py"},
                {"type": "b", "severity": "low", "owasp_category": "MCP02", "file": "b.py"},
            ],
        }
        result = apply_pack(report, DEFAULT_PACK)
        self.assertTrue(result["pass"])


class TestApplyPackStrict(unittest.TestCase):
    def test_strict_fails_on_medium(self):
        report = {
            "findings": [
                {"type": "a", "severity": "medium", "owasp_category": "MCP03", "file": "a.py"},
            ],
        }
        result = apply_pack(report, STRICT_PACK)
        self.assertFalse(result["pass"])
        self.assertEqual(result["summary"]["fail_on"], "medium")

    def test_strict_passes_when_all_low(self):
        report = {
            "findings": [
                {"type": "a", "severity": "low", "owasp_category": "MCP01", "file": "a.py"},
                {"type": "b", "severity": "info", "owasp_category": "MCP02", "file": "b.py"},
            ],
        }
        result = apply_pack(report, STRICT_PACK)
        self.assertTrue(result["pass"])

    def test_strict_filters_out_info(self):
        """strict severity_min=low → info 被过滤"""
        report = _mk_findings()
        result = apply_pack(report, STRICT_PACK)
        # info 的 2 条 (info_a, info_log) 被过滤
        self.assertEqual(result["summary"]["skipped_by_severity"], 2)


class TestApplyPackMcpOnly(unittest.TestCase):
    def test_mcp_only_filters_asi(self):
        report = _mk_findings()
        result = apply_pack(report, MCP_ONLY_PACK)
        # ASI06 应被过滤（不在 required 里）
        cats = {f["owasp_category"] for f in result["findings"]}
        self.assertNotIn("ASI06", cats)
        self.assertLess(len(result["findings"]), len(report["findings"]))


class TestApplyPackPersonalAgent(unittest.TestCase):
    def test_excludes_mcp04(self):
        report = _mk_findings()
        result = apply_pack(report, PERSONAL_AGENT_PACK)
        # MCP04 (high_d) 应被排除
        types = {f["type"] for f in result["findings"]}
        self.assertNotIn("high_d", types)

    def test_excludes_unlisted_categories(self):
        """required_categories 白名单：MCP08/MCP09/MCP10 不在 → 过滤"""
        report = {
            "findings": [
                {"type": "a", "severity": "high", "owasp_category": "MCP08", "file": "a.py"},
            ],
        }
        result = apply_pack(report, PERSONAL_AGENT_PACK)
        self.assertEqual(len(result["findings"]), 0)


class TestApplyPackRedTeam(unittest.TestCase):
    def test_red_team_never_fails(self):
        """red-team fail_on=impossible → 任何 findings 都 pass"""
        report = {
            "findings": [
                {"type": "a", "severity": "critical", "owasp_category": "MCP01", "file": "a.py"},
                {"type": "b", "severity": "high", "owasp_category": "MCP02", "file": "b.py"},
            ],
        }
        result = apply_pack(report, RED_TEAM_PACK)
        self.assertTrue(result["pass"])
        self.assertEqual(result["summary"]["triggered_findings"], 0)

    def test_red_team_keeps_all_findings(self):
        """severity_min=info + 无 category 过滤 → 保留全部"""
        report = _mk_findings()
        result = apply_pack(report, RED_TEAM_PACK)
        self.assertEqual(len(result["findings"]), len(report["findings"]))


class TestExcludedFiles(unittest.TestCase):
    def test_excludes_by_glob(self):
        pack = {
            "name": "test-excl",
            "config": {
                "severity_min": "info",
                "fail_on": "critical",
                "excluded_files": ["*.log", "test_*.py"],
            },
        }
        report = _mk_findings()
        result = apply_pack(report, pack)
        # test.log 被过滤
        files = {f["file"] for f in result["findings"]}
        self.assertNotIn("test.log", files)

    def test_no_exclusion_when_empty(self):
        pack = {
            "name": "test-empty",
            "config": {
                "severity_min": "info",
                "fail_on": "critical",
                "excluded_files": [],
            },
        }
        report = _mk_findings()
        result = apply_pack(report, pack)
        self.assertEqual(len(result["findings"]), len(report["findings"]))


class TestSummary(unittest.TestCase):
    def test_summary_fields_present(self):
        report = _mk_findings()
        result = apply_pack(report, DEFAULT_PACK)
        s = result["summary"]
        for k in ["original_findings", "filtered_findings", "pack", "fail_on",
                  "triggered_findings", "skipped_by_severity", "skipped_by_category",
                  "skipped_by_file"]:
            self.assertIn(k, s)

    def test_pack_name_in_result(self):
        report = _mk_findings()
        result = apply_pack(report, STRICT_PACK)
        self.assertEqual(result["pack"], "strict")


class TestMatchAny(unittest.TestCase):
    def test_basename_match(self):
        self.assertTrue(_match_any("foo/bar.log", ["*.log"]))

    def test_path_match(self):
        self.assertTrue(_match_any("tests/test_x.py", ["tests/*.py"]))

    def test_no_match(self):
        self.assertFalse(_match_any("foo/bar.py", ["*.log"]))

    def test_empty_filepath(self):
        self.assertFalse(_match_any("", ["*.log"]))


class TestWriteBuiltinPacks(unittest.TestCase):
    def test_idempotent(self):
        before = {n: load_pack(n) for n in list_packs()}
        write_builtin_packs()
        after = {n: load_pack(n) for n in list_packs()}
        self.assertEqual(sorted(before.keys()), sorted(after.keys()))

    def test_returns_all_paths(self):
        paths = write_builtin_packs()
        self.assertEqual(len(paths), 5)
        for p in paths:
            self.assertTrue(os.path.exists(p))


if __name__ == "__main__":
    unittest.main()
