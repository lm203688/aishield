# -*- coding: utf-8 -*-
"""
合规映射模块测试 — tests/test_compliance.py

红线：
    - 映射是静态知识，必须确定性（同输入同输出，无随机/无网络）
    - 全 20 个 OWASP 类别（MCP01-10 + ASI01-10）都要有映射，漏类 = 报告盲区
    - 未知类别/空输入不崩溃，unmapped 计数如实
    - 不输出"合规分数/合规结论"（中性信任机构红线）
"""
import json
import os
import re
import unittest

from scanner.compliance import (
    CATEGORY_CONTROLS,
    INTERNAL_ASI_TO_OWASP,
    MAESTRO_LAYER_NAMES,
    MAESTRO_THREAT_CODES,
    OWASP_AGENTIC_2026,
    OWASP_AGENTIC_ASI_TO_THREATS,
    OWASP_AGENTIC_THREATS,
    OWASP_AGENTIC_UNCOVERED,
    _CATEGORY_MAESTRO,
    compliance_summary,
    controls_for_category,
    FRAMEWORKS,
)


class TestCategoryCoverage(unittest.TestCase):
    def test_all_20_categories_mapped(self):
        for i in range(1, 11):
            self.assertIn("MCP%02d" % i, CATEGORY_CONTROLS)
            self.assertIn("ASI%02d" % i, CATEGORY_CONTROLS)

    def test_every_category_has_all_frameworks(self):
        """FRAMEWORKS 目前是 4 个（NIST/ISO/PCI + MAESTRO），漏一个 = 报告盲区。"""
        self.assertEqual(FRAMEWORKS, ("nist_csf", "iso27001", "pci_dss", "maestro"))
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


class TestMaestroMapping(unittest.TestCase):
    """CSA MAESTRO 7 层（+ OWASP 表内单列的 Cross-Layer 第 8 层）映射锚定。

    这是 2026-09-17 从 OWASP GenAI Security Project「Multi-Agentic system
    Threat Modelling Guide」v1.0 采纳的第 4 个框架。它回答的问题与
    NIST/ISO/PCI 不同：不是"上哪条控制"，而是"这条风险落在哪一层信任边界"。
    """

    def test_layer_names_are_the_eight_layers(self):
        self.assertEqual(
            sorted(MAESTRO_LAYER_NAMES),
            ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"])
        self.assertEqual(MAESTRO_LAYER_NAMES["L1"], "Foundation Model")
        self.assertEqual(MAESTRO_LAYER_NAMES["L8"], "Cross-Layer (Emergent)")

    def test_every_category_maps_to_a_valid_layer(self):
        for cat, layers in _CATEGORY_MAESTRO.items():
            self.assertTrue(layers, f"{cat} 未映射 MAESTRO 层")
            for layer in layers:
                self.assertIn(layer, MAESTRO_LAYER_NAMES,
                              f"{cat} 的 {layer} 不在 MAESTRO_LAYER_NAMES")

    def test_every_category_has_threat_codes(self):
        """每类至少给一个官方威胁锚点；码必须是官方目录内的 T 编号。"""
        for cat, codes in MAESTRO_THREAT_CODES.items():
            self.assertTrue(codes, f"{cat} 缺 T-code")
            for c in codes:
                self.assertRegex(c, r"^T\d{1,2}$", msg=f"{cat} 的 {c} 格式异常")
                self.assertIn(c, OWASP_AGENTIC_THREATS,
                              f"{cat} 的 {c} 不在 OWASP 官方威胁目录")

    def test_all_owasp_threat_codes_reachable(self):
        """官方 T1–T17 每条都至少被一个类别引用 —— 否则 OWASP 有威胁我们无锚点。"""
        referenced = {c for codes in MAESTRO_THREAT_CODES.values() for c in codes}
        missing = set(OWASP_AGENTIC_THREATS) - referenced
        self.assertEqual(missing, set(),
                         f"OWASP 威胁未被任何类别覆盖: {sorted(missing)}")

    def test_category_keys_align_with_controls(self):
        """两张表必须覆盖同一批类别，否则单点查询会漏锚点。"""
        self.assertEqual(set(_CATEGORY_MAESTRO), set(MAESTRO_THREAT_CODES))

    def test_maestro_aggregates_into_summary(self):
        r = compliance_summary([{"owasp_category": "ASI04", "severity": "high"}])
        controls = r["frameworks"]["maestro"]["controls"]
        for layer in ("L2", "L8"):
            self.assertIn(layer, controls)
            self.assertEqual(controls[layer]["max_severity"], "high")

    def test_multi_layer_takes_highest_severity(self):
        findings = [
            {"owasp_category": "ASI04", "severity": "low"},     # L2, L8
            {"owasp_category": "ASI09", "severity": "critical"},  # L8, L7
        ]
        r = compliance_summary(findings)
        self.assertEqual(r["frameworks"]["maestro"]["controls"]["L8"]["max_severity"],
                         "critical")

    def test_cross_layer_is_distinct_from_ecosystem(self):
        """L7（生态）与 L8（跨层涌现）必须分开计数，否则多 agent 级联风险被埋掉。"""
        r = compliance_summary([{"owasp_category": "ASI09", "severity": "medium"}])
        controls = r["frameworks"]["maestro"]["controls"]
        self.assertIn("L7", controls)
        self.assertIn("L8", controls)

    def test_maestro_codes_are_layer_ids_only(self):
        """码只应是 L1–L8，不要把层名拼进去（与 NIST/ISO 的裸编号风格保持一致）。"""
        for m in CATEGORY_CONTROLS.values():
            for code in m["maestro"]:
                self.assertRegex(code, r"^L[1-8]$", msg=code)


class TestOwaspAgentic2026Catalog(unittest.TestCase):
    """OWASP 官方目录防漂移锚定。

    背景：本库对外宣称"对齐 OWASP ASI01–10"，但本库 ASI01–ASI10 是自建归纳，
    编号与官方 Top 10 for Agentic Applications 2026 并非同一套体系（只有 ASI01/
    ASI02 恰好一致）。若官方名称或交叉表被改坏，对外报告的措辞就会变成引用
    不存在的 OWASP 条目 —— 这里把官方事实钉死。
    """

    def test_official_catalog_has_exactly_ten_categories(self):
        self.assertEqual(len(OWASP_AGENTIC_2026), 10)
        self.assertEqual(sorted(OWASP_AGENTIC_2026), [f"ASI{i:02d}" for i in range(1, 11)])

    def test_official_names_pinned(self):
        """官方名称逐字锚定，改写 = 测试红。"""
        expected = {
            "ASI01": "Agent Goal Hijack",
            "ASI02": "Tool Misuse & Exploitation",
            "ASI03": "Identity & Privilege Abuse",
            "ASI04": "Agentic Supply Chain Vulnerabilities",
            "ASI05": "Unexpected Code Execution",
            "ASI06": "Memory & Context Poisoning",
            "ASI07": "Insecure Inter-Agent Communication",
            "ASI08": "Cascading Failures",
            "ASI09": "Human-Agent Trust Exploitation",
            "ASI10": "Rogue Agents",
        }
        self.assertEqual(OWASP_AGENTIC_2026, expected)

    def test_official_threat_catalog_is_t1_to_t17(self):
        """官方威胁条目是 T1–T17 共 17 条（不是 15 条：T16/T17 是后补条目）。"""
        self.assertEqual(len(OWASP_AGENTIC_THREATS), 17)
        self.assertEqual(sorted(OWASP_AGENTIC_THREATS, key=lambda t: int(t[1:])),
                         [f"T{i}" for i in range(1, 18)])

    def test_crosswalk_covers_every_internal_category(self):
        """本库每个内部 ASI 类别都必须在交叉表里有声明（含"官方无对应"的空列表）。"""
        self.assertEqual(sorted(INTERNAL_ASI_TO_OWASP),
                         [f"ASI{i:02d}" for i in range(1, 11)])

    def test_crosswalk_targets_are_real_owasp_categories(self):
        for internal, officials in INTERNAL_ASI_TO_OWASP.items():
            for ow in officials:
                self.assertIn(ow, OWASP_AGENTIC_2026,
                              f"{internal} 交叉到不存在的 {ow}")

    def test_memory_poisoning_maps_to_official_asi06(self):
        """本库 ASI04（记忆操纵与投毒）= 官方 ASI06，不是官方 ASI04（供应链）。"""
        self.assertEqual(INTERNAL_ASI_TO_OWASP["ASI04"], ["ASI06"])
        self.assertEqual(OWASP_AGENTIC_2026["ASI06"], "Memory & Context Poisoning")
        self.assertNotEqual(OWASP_AGENTIC_2026["ASI04"], "Memory & Context Poisoning")

    def test_most_internal_ids_do_not_coincide_with_official(self):
        """只有前 3 个恰好与官方同号；其余必须靠交叉表换算。

        ASI04（记忆投毒）是最容易踩的坑：官方 ASI04 是供应链，记忆投毒是官方 ASI06。
        """
        coincident = {k for k, v in INTERNAL_ASI_TO_OWASP.items() if v == [k]}
        self.assertEqual(coincident, {"ASI01", "ASI02", "ASI03"})

    def test_official_mapping_uses_only_real_threats(self):
        for asi, threats in OWASP_AGENTIC_ASI_TO_THREATS.items():
            self.assertIn(asi, OWASP_AGENTIC_2026)
            for t in threats:
                self.assertIn(t, OWASP_AGENTIC_THREATS, f"{asi} 的 {t} 不在官方威胁目录")

    def test_uncovered_list_is_valid(self):
        """未覆盖列表必须恰好等于「官方目录 − 交叉表覆盖」，不靠手写维护。"""
        for asi in OWASP_AGENTIC_UNCOVERED:
            self.assertIn(asi, OWASP_AGENTIC_2026)
        covered = {ow for v in INTERNAL_ASI_TO_OWASP.values() for ow in v}
        derived = sorted(set(OWASP_AGENTIC_2026) - covered)
        self.assertEqual(sorted(OWASP_AGENTIC_UNCOVERED), derived,
                         "OWASP_AGENTIC_UNCOVERED 应等于官方目录减去交叉表覆盖的类别，"
                         "避免手写列表与交叉表漂移")

    def test_uncovered_is_unexpected_code_execution(self):
        """官方 ASI05（Unexpected Code Execution）无独立内部类别 —— 事实锚定。

        本库对它的覆盖散落在 least_agency_scan（os.system/eval/pip|sh）与
        provenance_scan（未锁版本的安装来源），没有专门的 ASI 类别，
        因此必须显式声明为能力缺口，而不是假装已覆盖。
        """
        self.assertEqual(sorted(OWASP_AGENTIC_UNCOVERED), ["ASI05"])

    def test_summary_exposes_namespace_and_crosswalk(self):
        """摘要必须声明编号命名空间，否则消费方会把本库编号当 OWASP 官方引用。"""
        r = compliance_summary([{"owasp_category": "ASI04", "severity": "medium"}])
        self.assertEqual(r["category_id_namespace"], "aishield-internal")
        self.assertEqual(r["owasp_agentic_2026"], OWASP_AGENTIC_2026)
        self.assertEqual(r["internal_to_owasp_agentic"], INTERNAL_ASI_TO_OWASP)
        self.assertIn("ASI05", r["owasp_agentic_uncovered"])


class TestPublicNamespaceDisclosure(unittest.TestCase):
    """对外可见面的命名空间声明不得丢失。

    缺了这个声明，外部读者会把本库内部编号当 OWASP 官方引用 —— 这正是
    2026-09-17 修正的问题（本库 ASI04 被读成官方 ASI04 供应链）。
    """

    JSON_ASSETS = (
        "api/static/.well-known/agent.json",
        "api/static/.well-known/ai-plugin.json",
        "api/static/agent-discovery.json",
        "api/static/.well-known/agent-card.json",
        "docs/.well-known/agent-card.json",
        "mcp-server/mcp.json",
        "mcp-server/server.json",
    )

    def test_json_assets_carry_category_id_note(self):
        for rel in self.JSON_ASSETS:
            with self.subTest(asset=rel):
                self.assertTrue(os.path.exists(rel), f"{rel} 缺失")
                d = json.load(open(rel, encoding="utf-8"))
                self.assertIn("category_id_note", d, f"{rel} 缺 category_id_note")
                self.assertIn("INTERNAL", d["category_id_note"])
                self.assertIn("ASI06", d["category_id_note"])

    def test_llms_txt_carries_namespace_note(self):
        """断言用小写比较 —— 正文措辞允许改写，但声明不得丢失。"""
        p = "api/static/llms.txt"
        t = open(p, encoding="utf-8").read()
        low = t.lower()
        self.assertIn("namespace note", low)
        self.assertIn("internal category ids", low)
        self.assertIn("internal_to_owasp_agentic", t)
        self.assertIn("INTERNAL_ASI_TO_OWASP", t)

    def test_readme_carries_namespace_note(self):
        t = open("README.md", encoding="utf-8").read()
        self.assertIn("编号体系说明", t)
        self.assertIn("INTERNAL_ASI_TO_OWASP", t)

    def test_two_llms_txt_copies_are_byte_identical(self):
        """两份 llms.txt 历史上多次漂移，改动必须同步。"""
        # 用 with 读：Windows 上未关闭的句柄会拖住文件锁，后续用例改写该文件
        # （规则数同步、_push_batch 等）就可能撞上 PermissionError —— 那会被
        # 当成"产品回归"，而真因只是测试自己没关文件。
        with open("api/static/llms.txt", "rb") as fa:
            a = fa.read()
        with open("docs/llms.txt", "rb") as fb:
            b = fb.read()
        self.assertEqual(a, b)

    def test_alignment_doc_exists_and_records_divergence(self):
        p = "docs/owasp-agentic-taxonomy-alignment.md"
        self.assertTrue(os.path.exists(p), f"{p} 缺失")
        t = open(p, encoding="utf-8").read()
        for needle in ("Agent Goal Hijack", "Memory & Context Poisoning",
                       "Agentic Supply Chain Vulnerabilities",
                       "Unexpected Code Execution", "T1–T17"):
            self.assertIn(needle, t, f"{p} 缺 {needle}")


class TestEmittedCategoryNamespace(unittest.TestCase):
    """扫描器实发 owasp_category 的命名空间纪律。

    发现于 2026-09-17 的对外文档校对：11 个 Agentic 扫描器里 10 个发的其实是
    MCP0x（官方 OWASP MCP Top 10 编号），只有 memory_integrity_scan 发 ASI0x
    （本库内部编号）。报告字段因此混用两个命名空间，文档必须讲清楚，
    否则消费方按 ASI0x 过滤会漏掉绝大多数 Agentic 命中。
    """

    def test_every_module_emits_a_registered_category(self):
        """模块级 _OWASP 常量必须是 CATEGORY_CONTROLS 里真实存在的键。"""
        import glob
        bad = []
        for f in glob.glob("scanner/*_scan.py"):
            txt = open(f, encoding="utf-8", errors="replace").read()
            m = re.search(r'_OWASP\s*=\s*["\']([^"\']+)["\']', txt)
            if m and m.group(1) not in CATEGORY_CONTROLS:
                bad.append((f, m.group(1)))
        self.assertEqual(bad, [], "以下模块发出未注册的 owasp_category 码")

    def test_agentic_scanners_emit_mcp_namespace(self):
        """Agentic 扫描器发 MCP0x 是既定约定；ASI0x 的例外必须是显式登记的。

        例外登记在此而非散在文档里 —— 新增 ASI0x 发射者必须同时改这里，
        否则测试红，提醒维护者同步对外命名空间声明。
        """
        agentic = [
            "goal_hijack_scan", "least_agency_scan", "mcp_oauth_scan",
            "provenance_scan", "memory_scan", "memory_integrity_scan",
            "scope_composition_scan", "dark_pattern_scan", "antitamper_scan",
            "registry_supply_scan",
        ]
        asi_emitters = []
        for mod in agentic:
            f = "scanner/%s.py" % mod
            if not os.path.exists(f):
                continue
            txt = open(f, encoding="utf-8", errors="replace").read()
            m = re.search(r'_OWASP\s*=\s*["\']([^"\']+)["\']', txt)
            if m and m.group(1).startswith("ASI"):
                asi_emitters.append((mod, m.group(1)))
        self.assertEqual(
            {m for m, _ in asi_emitters}, {"memory_integrity_scan"},
            "发出 ASI0x 的 Agentic 扫描器必须是显式登记的例外，"
            "新增例外需同步 docs/owasp-agentic-taxonomy-alignment.md")
        for mod, code in asi_emitters:
            self.assertIn(code, CATEGORY_CONTROLS)


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
