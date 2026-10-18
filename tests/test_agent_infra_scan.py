"""Agent 基础设施开源扫描管道测试（v4.8.2）。

全程离线（内存 files / 本地临时目录），不触发任何网络调用，确定性。
"""
import os
import sys
import tempfile
import shutil
import unittest

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from connectors.agent_infra import scan_pipeline as sp


RISKY_FILES = {
    "package.json": '{"name":"x","dependencies":{"express":"4.18.0","eval-fork-bomb":"1.0.0"}}',
    "config.py": 'API_KEY = "sk_live_abcdef1234567890abcdef"\nTOKEN = "ghp_1234567890abcdef"',
    "agent.py": 'def run(prompt):\n    exec(prompt)\n    return "ok"',
}

CLEAN_FILES = {
    "main.py": "def main():\n    print('hello agent infra')\n    return 0\n",
}


class TestResolveTarget(unittest.TestCase):
    def test_platform_id_without_url_raises(self):
        with self.assertRaises(ValueError):
            sp.resolve_target({"platform_id": "laya"})

    def test_repo_url_online_mode(self):
        t = sp.resolve_target({"name": "x", "repo_url": "https://github.com/o/r"})
        self.assertEqual(t["source_mode"], "online")
        self.assertEqual(t["repo_url"], "https://github.com/o/r")

    def test_files_offline_mode(self):
        t = sp.resolve_target({"name": "x", "files": RISKY_FILES})
        self.assertEqual(t["source_mode"], "offline")
        self.assertEqual(t["files"], RISKY_FILES)

    def test_platform_id_pulls_registry_meta(self):
        t = sp.resolve_target({"platform_id": "nasiko", "repo_url": "https://github.com/o/nasiko"})
        self.assertEqual(t["name"], "Nasiko (agent 基础设施)")
        self.assertIn("mcp", t["access_paths"])
        self.assertEqual(t["family"], "infrastructure")

    def test_missing_source_raises(self):
        with self.assertRaises(ValueError):
            sp.resolve_target({"name": "x"})


class TestOfflineScan(unittest.TestCase):
    def test_risky_files_produce_findings(self):
        res = sp.scan_target({"name": "risky", "files": RISKY_FILES})
        self.assertIsNone(res["error"])
        rep = res["report"]
        self.assertGreater(rep["total_findings"], 0)
        self.assertIn("scores", rep)
        self.assertIsNotNone((rep["scores"] or {}).get("overall_score"))
        # 至少应包含 critical 级密钥类风险
        sevs = [f.get("severity", "").lower() for f in rep["findings"]]
        descs = " ".join((f.get("description") or "") for f in rep["findings"])
        self.assertIn("critical", sevs)
        self.assertTrue(("密钥" in descs) or ("依赖" in descs))

    def test_clean_files_no_high_severity(self):
        res = sp.scan_target({"name": "clean", "files": CLEAN_FILES})
        self.assertIsNone(res["error"])
        sevs = [f.get("severity", "").lower() for f in res["report"]["findings"]]
        self.assertNotIn("critical", sevs)
        self.assertNotIn("high", sevs)

    def test_local_path_scan(self):
        d = tempfile.mkdtemp(prefix="ai_scan_")
        try:
            for fn, content in RISKY_FILES.items():
                with open(os.path.join(d, fn), "w", encoding="utf-8") as fh:
                    fh.write(content)
            res = sp.scan_target({"name": "local", "local_path": d})
            self.assertIsNone(res["error"])
            self.assertGreater(res["report"]["total_findings"], 0)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestMcpAdapterSkeleton(unittest.TestCase):
    def test_skeleton_contains_handle_and_todos(self):
        res = sp.scan_target({"name": "risky", "files": RISKY_FILES})
        skel = sp.build_mcp_adapter_skeleton(res)
        self.assertIn("def handle(", skel)
        # 2026-10-17：占位符改为「Step N + owner」形式（见 scan_pipeline.py 模板说明段），
        # 不再用 TODO(二次研发) 裸标签——owner 可追溯比 TODO 可搜索更重要。
        self.assertIn("owner:", skel)
        self.assertIn("Step 1: 治理 preflight", skel)
        self.assertIn("risky", skel)
        # 代码花括号未被 .format 误伤
        self.assertIn("raise NotImplementedError", skel)

    def test_skeleton_no_findings_still_valid(self):
        res = sp.scan_target({"name": "clean", "files": CLEAN_FILES})
        skel = sp.build_mcp_adapter_skeleton(res)
        self.assertIn("def handle(", skel)


class TestSecondaryRdChecklist(unittest.TestCase):
    def test_checklist_has_governance_items(self):
        res = sp.scan_target({"name": "risky", "files": RISKY_FILES})
        cl = sp.build_secondary_rd_checklist(res)
        self.assertGreaterEqual(len(cl), 3)
        sources = {c["source"] for c in cl}
        self.assertIn("aishield_integration", sources)
        titles = " ".join(c["title"] for c in cl)
        self.assertIn("AIShield", titles)


class TestPortfolio(unittest.TestCase):
    def test_scan_portfolio_aggregates(self):
        pf = sp.scan_portfolio([
            {"name": "a", "files": RISKY_FILES},
            {"name": "b", "files": CLEAN_FILES},
        ])
        self.assertEqual(pf["targets"], 2)
        self.assertIsNotNone(pf["average_score"])
        self.assertGreaterEqual(pf["total_findings"], 1)
        self.assertEqual(len(pf["results"]), 2)

    def test_export_portfolio(self):
        pf = sp.scan_portfolio([{"name": "a", "files": RISKY_FILES}])
        d = tempfile.mkdtemp(prefix="ai_pf_")
        try:
            out = os.path.join(d, "pf.json")
            sp.export_portfolio(pf, out)
            self.assertTrue(os.path.exists(out))
            with open(out, encoding="utf-8") as fh:
                import json
                data = json.load(fh)
            self.assertEqual(data["targets"], 1)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestScanErrors(unittest.TestCase):
    def test_empty_local_dir_returns_error(self):
        d = tempfile.mkdtemp(prefix="ai_empty_")
        try:
            # 目录存在但无任何可扫文件 → offline 分支读到空 files → 返回 error
            res = sp.scan_target({"name": "x", "local_path": d})
            self.assertIsNotNone(res.get("error"))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_invalid_spec_raises(self):
        with self.assertRaises(ValueError):
            sp.scan_target({"name": "x", "files": {}})


if __name__ == "__main__":
    unittest.main(verbosity=2)
