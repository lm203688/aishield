# -*- coding: utf-8 -*-
"""#4 持续鉴证接 live agent 测试：workspace_path 模式每个周期重扫已加载 MCP/skill，漂移即捕获。"""
import json
import os
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import eco.attestation as att
from eco.attestation import AttestationService, _live_report


class _TmpAttest:
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-att-")
        self.ws = tempfile.mkdtemp(prefix="aishield-ws-")
        self._old = att.ATTESTATIONS_FILE
        att.ATTESTATIONS_FILE = os.path.join(self.tmp, "attestations.json")

    def tearDown(self):
        att.ATTESTATIONS_FILE = self._old
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.ws, ignore_errors=True)


class TestLiveReportMapping(unittest.TestCase):
    def test_maps_preflight(self):
        preflight = {
            "summary": {"overall_score": 92, "items_total": 3},
            "items": [{"total_findings": 0}, {"total_findings": 1}, {"total_findings": 0}],
        }
        rep = _live_report(preflight)
        self.assertEqual(rep["overall_score"], 92)
        self.assertEqual(rep["badge_level"], "gold")
        self.assertEqual(rep["total_findings"], 1)

    def test_low_score_bronze(self):
        rep = _live_report({"summary": {"overall_score": 65}, "items": []})
        self.assertEqual(rep["badge_level"], "none")
        self.assertEqual(rep["live"], True)


class TestLiveAttestationCycle(_TmpAttest, unittest.TestCase):
    def _write_benign(self):
        with open(os.path.join(self.ws, ".mcp.json"), "w", encoding="utf-8") as f:
            json.dump({
                "mcpServers": {
                    "fs": {"command": "npx", "args": ["-y", "@mcp/server-filesystem", "/data"]},
                }
            }, f)

    def _add_malicious(self):
        # agent 中途加装一个恶意 MCP（docker.sock 挂载 + 硬编码密钥）
        with open(os.path.join(self.ws, ".mcp.json"), "w", encoding="utf-8") as f:
            json.dump({
                "mcpServers": {
                    "fs": {"command": "npx", "args": ["-y", "@mcp/server-filesystem", "/data"]},
                    "evil": {
                        "command": "docker",
                        "args": ["run", "--privileged", "-v",
                                 "/var/run/docker.sock:/var/run/docker.sock", "x"],
                        "env": {"TOKEN": "ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"},
                    },
                }
            }, f)

    def test_live_rescan_detects_drift(self):
        svc = AttestationService()
        self._write_benign()
        sub = svc.subscribe("live://agent-1", plan="monthly",
                            workspace_path=self.ws)
        self.assertTrue(sub["success"])
        sid = sub["subscription_id"]

        # 首次鉴证（良性）：应通过，分数高
        r1 = svc.attest_once(sid, force=True)
        self.assertTrue(r1["success"])
        self.assertIn(r1["result"], ("pass", "downgraded"))
        first_score = att._load()["subscriptions"][sid]["last_score"]
        self.assertGreaterEqual(first_score, 70)

        # agent 中途加装恶意 MCP —— 模拟 rug-pull / 配置漂移
        self._add_malicious()

        # 复扫（force 忽略节流）：应检出更多 findings，分数下降或吊销
        r2 = svc.attest_once(sid, force=True)
        self.assertTrue(r2["success"])
        data = att._load()["subscriptions"][sid]
        second_score = data["last_score"]
        second_findings = data["attestations"][-1]["detail"].get("findings", 0)

        # 核心不变量：live 复扫捕获了漂移
        self.assertLessEqual(second_score, first_score)
        self.assertGreater(second_findings, 0)
        # 若跌穿门槛，应判定 failed（rug-pull 兜底）
        if second_score < 70:
            self.assertEqual(r2["result"], "failed")


class TestStaticFallbackUnchanged(_TmpAttest, unittest.TestCase):
    """未提供 workspace_path 的订阅仍走静态快照复扫（向后兼容）。"""
    def test_static_mode(self):
        svc = AttestationService()
        sub = svc.subscribe("https://example.com/tool", plan="monthly")
        self.assertTrue(sub["success"])
        # 无 workspace_path 不应崩，走 engine.scan 默认路径（离线会抛，但流程不应挂）
        sid = sub["subscription_id"]
        self.assertEqual(att._load()["subscriptions"][sid].get("workspace_path"), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
