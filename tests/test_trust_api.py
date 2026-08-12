"""tests/test_trust_api.py — 信任层 (aishield-trust/v1) 后端闭环测试。

覆盖: registry 查询 / trust_score / cert 验证 / 新增 /api/v1/trust?src= 信封。
不依赖真实扫描器或网络：数据文件指向临时路径，attestation.trust_status 用 mock。
"""
import os
import json
import tempfile
import unittest
from unittest import mock

from api import trust_api


class TrustApiTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        # 让 trust_api 读写临时数据文件，避免污染仓库 data/
        self._cert = os.path.join(self._tmp, "certifications.json")
        self._reg = os.path.join(self._tmp, "agent_registry.json")
        trust_api.CERTIFICATIONS_FILE = self._cert
        trust_api.REGISTRY_FILE = self._reg
        # 一个已注册 agent
        reg = {"agents": {
            "agent:demo": {
                "name": "Demo Agent",
                "description": "demo",
                "url": "https://example.com/demo",
                "authentication": {"schemes": ["oauth2"]},
                "skills": [{"id": "s1", "examples": ["do x"]}],
                "documentationUrl": "https://example.com/docs",
            }
        }}
        with open(self._reg, "w", encoding="utf-8") as f:
            json.dump(reg, f)

    def tearDown(self):
        for p in (self._cert, self._reg):
            if os.path.exists(p):
                os.remove(p)

    # ── registry ──
    def test_registry_list_returns_agent(self):
        out = trust_api.registry_list()
        self.assertEqual(out["count"], 1)
        self.assertEqual(out["agents"][0]["name"], "Demo Agent")

    def test_registry_get(self):
        a = trust_api.registry_get("agent:demo")
        self.assertIsNotNone(a)
        self.assertIsNone(trust_api.registry_get("agent:ghost"))

    # ── trust_score ──
    def test_trust_score_registered(self):
        s = trust_api.trust_score("agent:demo")
        self.assertIsNotNone(s)
        # 已注册 + 认证机制 + 技能 + 文档 = 78 (silver)，无证书时不加 22 分
        self.assertGreaterEqual(s["trust_score"], 70)
        self.assertIn(s["level"], ("silver", "gold"))
        self.assertTrue(any("认证" in str(f) for f in s["factors"]))

    def test_trust_score_with_cert_reaches_gold(self):
        cert = {"cert_id": "C9", "name": "Demo Agent", "overall_score": 95,
                "badge_level": "gold", "expires_at": "2099-01-01T00:00:00+08:00"}
        with open(self._cert, "w", encoding="utf-8") as f:
            json.dump({"certs": {"C9": cert}}, f)
        s = trust_api.trust_score("agent:demo")
        self.assertGreaterEqual(s["trust_score"], 85)  # 78 + 22 证书 = 100
        self.assertEqual(s["level"], "gold")

    def test_trust_score_unknown(self):
        self.assertIsNone(trust_api.trust_score("agent:ghost"))

    # ── cert verify ──
    def test_verify_cert_found(self):
        cert = {"cert_id": "C1", "name": "Demo", "overall_score": 90,
                "badge_level": "gold", "expires_at": "2099-01-01T00:00:00+08:00"}
        with open(self._cert, "w", encoding="utf-8") as f:
            json.dump({"certs": {"C1": cert}}, f)
        out = trust_api.verify_cert("C1")
        self.assertIsNotNone(out)
        self.assertTrue(out["verified"])
        self.assertEqual(out["status"], "active")

    def test_verify_cert_missing(self):
        self.assertIsNone(trust_api.verify_cert("nope"))

    # ── /api/v1/trust?src= 信封 (aishield-trust/v1) ──
    def test_verify_endpoint_unsubscribed_is_honest(self):
        # 未订阅来源：返回 unknown 裁决，不谎报
        payload, status = trust_api.handle_get("/api/v1/trust", "src=https://github.com/x/y")
        self.assertEqual(status, 200)
        self.assertEqual(payload["schema"], "aishield-trust/v1")
        self.assertEqual(payload["subject"]["url"], "https://github.com/x/y")
        self.assertEqual(payload["verdict"]["risk"], "unknown")
        self.assertIsNone(payload["verdict"]["score"])
        self.assertTrue(payload["verdict"]["no_spawn_guarantee"])
        self.assertTrue(payload["verdict"]["offline_scan"])

    def test_verify_endpoint_subscribed_maps_score(self):
        fake = {
            "subscribed": True,
            "continuously_verified": True,
            "last_score": 92,
            "badge_level": "gold",
            "last_attest_at": "2026-08-12T00:00:00+08:00",
            "evidence_entries": 7,
            "evidence_chain": [{"hash": "sha256:abc"}],
        }
        with mock.patch("eco.attestation.trust_status", return_value=fake):
            payload, status = trust_api.handle_get("/api/v1/trust", "src=https://github.com/x/y&type=skill")
        self.assertEqual(status, 200)
        self.assertEqual(payload["verdict"]["score"], 92)
        self.assertEqual(payload["verdict"]["risk"], "safe")
        self.assertEqual(payload["verdict"]["level"], "gold")
        self.assertEqual(payload["subject"]["type"], "skill")
        self.assertEqual(payload["attestation"]["method"], "continuous")
        self.assertEqual(payload["attestation"]["chain_anchor"], "sha256:abc")

    def test_verify_endpoint_requires_src(self):
        payload, status = trust_api.handle_get("/api/v1/trust", "")
        self.assertEqual(status, 400)
        self.assertIn("src", payload["error"])

    def test_verify_alias_route(self):
        fake = {"subscribed": False, "continuously_verified": False}
        with mock.patch("eco.attestation.trust_status", return_value=fake):
            payload, status = trust_api.handle_get("/api/v1/trust/verify", "src=https://github.com/x/y")
        self.assertEqual(status, 200)
        self.assertEqual(payload["schema"], "aishield-trust/v1")

    # ── handle_post ──
    def test_post_trust_auto_graceful(self):
        # eco.badge 在测试环境可能不可 import，auto_certify 应优雅返回而非崩溃
        payload, status = trust_api.handle_post(
            "/api/v1/trust/auto", {"scan_result": {"overall_score": 95}})
        self.assertIn("success", payload)

    def test_post_verify_route(self):
        fake = {"subscribed": True, "continuously_verified": True,
                "last_score": 70, "badge_level": "silver"}
        with mock.patch("eco.attestation.trust_status", return_value=fake):
            payload, status = trust_api.handle_post(
                "/api/v1/trust", {"src": "https://github.com/x/y"})
        self.assertEqual(status, 200)
        self.assertEqual(payload["verdict"]["score"], 70)
        self.assertEqual(payload["verdict"]["level"], "silver")


if __name__ == "__main__":
    unittest.main()
