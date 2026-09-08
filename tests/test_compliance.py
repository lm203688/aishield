# -*- coding: utf-8 -*-
"""
合规映射模块测试 — tests/test_compliance.py

红线：
    - 映射是静态知识，必须确定性（同输入同输出，无随机/无网络）
    - 全 20 个 OWASP 类别（MCP01-10 + ASI01-10）都要有映射，漏类 = 报告盲区
    - 未知类别/空输入不崩溃，unmapped 计数如实
    - 不输出"合规分数/合规结论"（中性信任机构红线）
"""
import unittest

from scanner.compliance import (
    CATEGORY_CONTROLS,
    compliance_summary,
    controls_for_category,
    FRAMEWORKS,
)


class TestCategoryCoverage(unittest.TestCase):
    def test_all_20_categories_mapped(self):
        for i in range(1, 11):
            self.assertIn("MCP%02d" % i, CATEGORY_CONTROLS)
            self.assertIn("ASI%02d" % i, CATEGORY_CONTROLS)

    def test_every_category_has_all_three_frameworks(self):
        for cat, m in CATEGORY_CONTROLS.items():
            for fw in FRAMEWORKS:
                self.assertTrue(m.get(fw), f"{cat} 缺 {fw} 映射")

    def test_control_codes_look_sane(self):
        """锚定检查：防止手滑写出错误体系的控制项编号。"""
        for m in CATEGORY_CONTROLS.values():
            for code in m["iso27001"]:
                self.assertTrue(code.startswith("A."), f"ISO 控制项格式异常: {code}")
            for code in m["nist_csf"]:
                self.assertRegex(code, r"^[A-Z]{2}\.[A-Z]{2}-\d+$", msg=code)


class TestSummary(unittest.TestCase):
    def test_deterministic(self):
        findings = [{"owasp_category": "MCP01", "severity": "high"},
                    {"owasp_category": "MCP01", "severity": "critical"}]
        a = compliance_summary(list(findings))
        b = compliance_summary(list(reversed(findings)))
        # 聚合语义（计数/最高严重度）与顺序无关
        self.assertEqual(a["frameworks"], b["frameworks"])

    def test_counts_and_max_severity(self):
        findings = [
            {"owasp_category": "MCP05", "severity": "critical"},
            {"owasp_category": "MCP05", "severity": "medium"},
            {"owasp_category": "MCP04", "severity": "high"},
        ]
        r = compliance_summary(findings)
        self.assertEqual(r["categories_mapped"], 2)
        pci = r["frameworks"]["pci_dss"]["controls"]
        self.assertEqual(pci["6.2.4"]["findings_count"], 2)
        self.assertEqual(pci["6.2.4"]["max_severity"], "critical")

    def test_unmapped_counted_not_crash(self):
        findings = [{"type": "x"}, {"owasp_category": "MCP99", "severity": "low"}]
        r = compliance_summary(findings)
        self.assertEqual(r["findings_unmapped"], 2)
        self.assertEqual(r["categories_mapped"], 0)

    def test_empty_input(self):
        r = compliance_summary([])
        self.assertEqual(r["categories_mapped"], 0)
        self.assertEqual(r["findings_unmapped"], 0)
        for fw in FRAMEWORKS:
            self.assertEqual(r["frameworks"][fw]["controls_hit"], 0)

    def test_none_finding_items_tolerated(self):
        r = compliance_summary([None, "junk", {"owasp_category": "MCP08"}])
        self.assertEqual(r["categories_mapped"], 1)

    def test_no_compliance_verdict(self):
        """中性红线：输出里不得出现合规分数/通过结论。"""
        import json
        r = compliance_summary([{"owasp_category": "MCP01", "severity": "low"}])
        text = json.dumps(r, ensure_ascii=False)
        for banned in ("compliant", "score", "passed", "合规分数"):
            self.assertNotIn(banned, text.lower() if banned.isascii() else text)


class TestSingleQuery(unittest.TestCase):
    def test_known(self):
        m = controls_for_category("ASI03")
        self.assertIn("PR.AA-05", m["nist_csf"])

    def test_unknown_returns_empty(self):
        m = controls_for_category("MCP99")
        self.assertEqual(m, {fw: [] for fw in FRAMEWORKS})


if __name__ == "__main__":
    unittest.main()
