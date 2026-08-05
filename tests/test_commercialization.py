"""
商业化层补齐 (F4/F5/Phase3) — 单元测试

覆盖:
  - F5  FleetService 聚合（收纳 / 汇总 / 列表 / 重置）
  - Phase3 BadgeMonetization x402 闭环（请求支付 / 结构校验履约 / 拒绝无效头 / none 等级拦截）
  - F4  to_attack_graph 数据形状（节点/边/最小移除集）
全部离线可跑。
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scanner import fleet as fleet_mod
from scanner.exporters import to_attack_graph
from eco import monetization as mon
from eco.x402 import build_payment_payload, encode_payment_header


SAMPLE_MEMBERS = [
    {"source_url": "https://github.com/acme/a", "overall_score": 93, "badge_level": "gold",
     "risk_level": "safe", "total_findings": 0, "findings": []},
    {"source_url": "https://github.com/acme/b", "overall_score": 78, "badge_level": "silver",
     "risk_level": "low", "total_findings": 2,
     "findings": [{"severity": "low", "owasp_category": "MCP03"}, {"severity": "low", "owasp_category": "MCP05"}]},
    {"source_url": "https://github.com/acme/c", "overall_score": 41, "badge_level": "none",
     "risk_level": "high", "total_findings": 4,
     "findings": [{"severity": "critical", "owasp_category": "MCP08"},
                  {"severity": "high", "owasp_category": "MCP08"},
                  {"severity": "medium", "owasp_category": "MCP03"},
                  {"severity": "low", "owasp_category": "MCP01"}]},
]


class TestFleet(unittest.TestCase):
    def setUp(self):
        self.svc = fleet_mod.FleetService()
        self.svc.reset()

    def test_ingest_and_summary(self):
        for m in SAMPLE_MEMBERS:
            self.svc.ingest(m)
        s = self.svc.summary()
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["pass"], 2)        # a(93) + b(78)；c(41) 不达标
        self.assertEqual(s["fail"], 1)
        self.assertAlmostEqual(s["avg_score"], (93 + 78 + 41) / 3, places=1)
        self.assertAlmostEqual(s["pass_rate"], 66.7, places=1)
        # 严重度累计：1 critical / 1 high / 2 medium / 4 low
        self.assertEqual(s["severity_hist"]["critical"], 1)
        self.assertEqual(s["severity_hist"]["high"], 1)
        self.assertEqual(s["severity_hist"]["low"], 3)
        # OWASP 覆盖
        self.assertEqual(s["owasp_hist"].get("MCP08"), 2)

    def test_worst_offenders_sorted(self):
        for m in SAMPLE_MEMBERS:
            self.svc.ingest(m)
        worst = self.svc.summary()["worst_offenders"]
        self.assertEqual(worst[0]["identity"], "https://github.com/acme/c")
        self.assertEqual(len(worst), 3)

    def test_dedup_by_identity(self):
        self.svc.ingest(SAMPLE_MEMBERS[0])
        self.svc.ingest(SAMPLE_MEMBERS[0])   # 同 source_url 覆盖，不新增
        self.assertEqual(self.svc.summary()["total"], 1)

    def test_list_members(self):
        self.svc.ingest(SAMPLE_MEMBERS[1])
        members = self.svc.list_members()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]["name"], "https://github.com/acme/b")


class TestMonetization(unittest.TestCase):
    def setUp(self):
        self.svc = mon.BadgeMonetization()
        # 清空订单，避免跨测试污染
        data = mon._load()
        data["orders"] = {}
        mon._save(data)

    def _valid_header(self, pay_to="0xPayTo", value="50000"):
        signed = {"from": "0xClient", "to": pay_to, "value": value,
                  "validAfter": "0", "validBefore": "9999999999", "nonce": "0xabc", "signature": "0xdef"}
        return encode_payment_header(build_payment_payload(signed))

    def test_request_payment_gold(self):
        rep = {"overall_score": 92, "badge_level": "gold", "risk_level": "safe", "total_findings": 0}
        r = self.svc.request_cert_payment("https://github.com/acme/gold", rep)
        self.assertTrue(r["success"])
        self.assertEqual(r["status"], "requires_payment")
        self.assertEqual(r["badge_level"], "gold")
        self.assertAlmostEqual(r["amount_usd"], 0.05)
        self.assertIn("payment_requirements", r)
        # 订单已落库
        self.assertIsNotNone(self.svc.get_order(r["order_id"]))

    def test_reject_none_level(self):
        rep = {"overall_score": 40, "badge_level": "none"}
        r = self.svc.request_cert_payment("https://github.com/acme/low", rep)
        self.assertFalse(r["success"])
        self.assertEqual(r["status"], "rejected")

    def test_fulfill_with_valid_header(self):
        rep = {"overall_score": 92, "badge_level": "gold", "risk_level": "safe", "total_findings": 0}
        req = self.svc.request_cert_payment("https://github.com/acme/gold2", rep)
        header = self._valid_header(pay_to=req["pay_to"])
        res = self.svc.fulfill_cert(req["order_id"], header, rep)
        self.assertTrue(res["success"])
        self.assertEqual(res["certification"]["status"], "certified")
        self.assertEqual(res["certification"]["badge_level"], "gold")
        # 订单标记结算
        self.assertEqual(self.svc.get_order(req["order_id"])["status"], "settled_offline")

    def test_fulfill_rejects_invalid_header(self):
        rep = {"overall_score": 80, "badge_level": "silver", "risk_level": "low"}
        req = self.svc.request_cert_payment("https://github.com/acme/silver", rep)
        res = self.svc.fulfill_cert(req["order_id"], "not-a-valid-header", rep)
        self.assertFalse(res["success"])

    def test_fulfill_unknown_order(self):
        res = self.svc.fulfill_cert("order_does_not_exist", self._valid_header())
        self.assertFalse(res["success"])


class TestAttackGraphData(unittest.TestCase):
    def test_to_attack_graph_shape(self):
        inv = [
            {"name": "file-reader", "client": "claude", "capabilities": ["file-read"]},
            {"name": "net-sender", "client": "claude", "capabilities": ["network"]},
        ]
        tox = [{"type": "cross_server_toxic_flow", "severity": "high",
                "capability_pair": ["file-read", "network"]}]
        g = to_attack_graph(inv, tox)
        self.assertIn("graph", g)
        self.assertIn("recommendation", g)
        self.assertEqual(len(g["graph"]["nodes"]), 2)
        self.assertEqual(len(g["graph"]["links"]), 1)
        # 单条毒性流：移除任一侧即可打破（贪心取首个命中）
        self.assertTrue(set(g["recommendation"]["removed_servers"]) <= {"file-reader", "net-sender"})
        self.assertEqual(g["recommendation"]["broken_flows"], 1)
        self.assertEqual(g["recommendation"]["remaining_flows"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
