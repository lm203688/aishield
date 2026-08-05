"""
投资人视角战略补齐项 — 单元测试 (D1/M3/M4/F2/F3/F6/D3/D4)

全部离线可跑：OSV 用 cache 注入，registry 接受离线返回 []，telemetry 测关闭路径。
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scanner import osv, attack_path, exporters, policy, telemetry, live_probe, registry_discovery
from scanner.engine import explain_score


class TestOSV(unittest.TestCase):
    def test_build_query(self):
        q = osv.build_osv_query("lodash", "npm", "4.17.20")
        self.assertEqual(q["package"]["name"], "lodash")
        self.assertEqual(q["package"]["ecosystem"], "npm")
        self.assertEqual(q["version"], "4.17.20")

    def test_offline_no_network(self):
        self.assertEqual(osv.check_osv([{"name": "lodash", "version": "4.17.20", "source": "npm"}],
                                        use_network=False), [])

    def test_cache_hit_returns_finding(self):
        query = osv.build_osv_query("lodash", "npm", "4.17.20")
        cache = {json.dumps(query, sort_keys=True): [
            {"id": "OSV-2024-999", "severity": [{"score": "CRITICAL"}], "summary": "test vuln"}]}
        findings = osv.check_osv([{"name": "lodash", "version": "4.17.20", "source": "npm"}],
                                 use_network=True, cache=cache)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["cve"], "OSV-2024-999")
        self.assertEqual(findings[0]["severity"], "critical")

    def test_unsupported_ecosystem_skipped(self):
        self.assertEqual(osv.check_osv([{"name": "x", "source": "cargo"}],
                                        use_network=False), [])


class TestAttackPath(unittest.TestCase):
    INV = [
        {"name": "file-reader", "client": "claude", "capabilities": ["file-read"]},
        {"name": "net-sender", "client": "claude", "capabilities": ["network"]},
        {"name": "shell-runner", "client": "cursor", "capabilities": ["shell-exec"]},
    ]
    TOX = [
        {"type": "cross_server_toxic_flow", "severity": "high",
         "capability_pair": ["file-read", "network"], "description": "x"},
        {"type": "cross_server_toxic_flow", "severity": "high",
         "capability_pair": ["shell-exec", "network"], "description": "y"},
    ]

    def test_minimal_removal_breaks_all(self):
        res = attack_path.solve_minimal_removal(self.INV, self.TOX)
        self.assertIn("net-sender", res["removed_servers"])
        self.assertEqual(res["remaining_flows"], 0)
        self.assertEqual(res["total_flows"], 2)

    def test_graph_shape(self):
        g = attack_path.attack_graph_json(self.INV, self.TOX)
        self.assertEqual(len(g["nodes"]), 3)
        self.assertEqual(len(g["links"]), 2)

    def test_no_flows(self):
        res = attack_path.solve_minimal_removal(self.INV, [])
        self.assertEqual(res["removed_servers"], [])


class TestExporters(unittest.TestCase):
    F = [{"type": "taint_flow", "severity": "critical", "description": "t",
          "owasp_category": "MCP05", "file": "a.js", "cve": ""}]

    def test_nucleus(self):
        nuc = exporters.to_nucleus(self.F)
        self.assertTrue(nuc["schema"].startswith("nucleus"))
        self.assertEqual(len(nuc["findings"]), 1)
        self.assertEqual(nuc["findings"][0]["finding_severity"], "Critical")

    def test_splunk(self):
        sp = exporters.to_splunk(self.F)
        self.assertEqual(sp["event_count"], 1)

    def test_attack_graph_export(self):
        ag = exporters.to_attack_graph(TestAttackPath.INV, TestAttackPath.TOX)
        self.assertIn("recommendation", ag)
        self.assertIn("graph", ag)


class TestPolicy(unittest.TestCase):
    def setUp(self):
        self.pol = policy.load_policy()

    def test_blocks_critical(self):
        bad = {"overall_score": 30, "security_score": 20, "findings": [
            {"severity": "critical", "owasp_category": "MCP03", "description": "x"}], "name": "x"}
        r = policy.evaluate_policy(bad, policy=self.pol)
        self.assertFalse(r["passed"])
        self.assertTrue(any(v["rule"] == "blocked_owasp_categories" for v in r["violations"]))

    def test_passes_clean(self):
        good = {"overall_score": 90, "security_score": 90, "permissions_score": 90,
                "data_handling_score": 90, "supply_chain_score": 90, "reliability_score": 90,
                "findings": [], "name": "y"}
        self.assertTrue(policy.evaluate_policy(good, policy=self.pol)["passed"])

    def test_min_score_violation(self):
        low = {"overall_score": 50, "security_score": 70, "findings": [], "name": "z"}
        r = policy.evaluate_policy(low, policy=self.pol)
        self.assertFalse(r["passed"])


class TestTelemetry(unittest.TestCase):
    def test_disabled_by_default(self):
        self.assertIsNone(telemetry.record_scan({"overall_score": 80}))

    def test_aggregates_shape(self):
        agg = telemetry.get_aggregates()
        self.assertIn("samples", agg)
        self.assertIn("score_distribution", agg)

    def test_bucket(self):
        self.assertEqual(telemetry._bucket_score(90), "85-100")
        self.assertEqual(telemetry._bucket_score(10), "0-39")


class TestLiveProbe(unittest.TestCase):
    def test_disabled_returns_skipped(self):
        self.assertFalse(live_probe.probe_server_metadata({"url": "http://x"}, enable=False)["probed"])

    def test_stdio_not_spawned(self):
        r = live_probe.probe_server_metadata({"command": "node x.js"}, enable=True)
        self.assertEqual(r["transport"], "stdio")
        self.assertFalse(r["probed"])

    def test_remote_off_by_default(self):
        self.assertFalse(live_probe.probe_server_metadata({"url": "http://x"})["probed"])


class TestRegistryDiscovery(unittest.TestCase):
    def test_normalize(self):
        sample = {"server": {"name": "a/b", "displayName": "B",
                             "packages": [{"version": "1.0", "url": "http://x"}], "isLatest": True}}
        n = registry_discovery._normalize_official(sample)
        self.assertEqual(n["name"], "a/b")
        self.assertEqual(n["version"], "1.0")

    def test_offline_search_returns_list(self):
        res = registry_discovery.search_registry("test")
        self.assertIsInstance(res, list)


class TestExplainScore(unittest.TestCase):
    def test_explain(self):
        scores = {
            "overall_score": 72, "risk_level": "medium", "badge_level": "silver",
            "security_score": 80,
            "score_breakdown": {"security_score": {"base": 100, "penalty": 20,
                "contributors": [{"reason": "x", "severity": "high", "amount": 10, "owasp": "MCP03"}]}},
            "top_deductions": [{"dimension": "security_score", "reason": "x",
                                "severity": "high", "amount": 10, "owasp": "MCP03"}],
        }
        txt = explain_score(scores)
        self.assertIn("72", txt)
        self.assertIn("x", txt)


if __name__ == "__main__":
    unittest.main()
