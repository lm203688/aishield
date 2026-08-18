"""
tests/test_trust_protocol.py — agent-trust-protocol 融合层闭环测试。

覆盖:
  - Ed25519 did:key 身份生成 / 序列化 / 反序列化
  - sign_data / verify_signature / verify_signature_by_did 签名验签（含篡改拒绝）
  - compute_trust_score 4 维加权评分 + 置信分级
  - EWMA 时间衰减一致性
  - TrustRegistry 事件记录 / 持久化 / 评分 / 验签

不依赖网络；TrustRegistry 写入临时文件，避免污染仓库 data/。
"""

import json
import os
import tempfile
import unittest

from eco import trust_protocol as tp


class IdentityTest(unittest.TestCase):
    def test_generate_keypair_did_format(self):
        kp = tp.generate_keypair()
        self.assertTrue(kp.did.startswith("did:key:z"))
        self.assertEqual(len(kp.private_key), 32)
        self.assertEqual(len(kp.public_key), 32)

    def test_did_roundtrip(self):
        kp = tp.generate_keypair()
        pk = tp.did_to_public_key(kp.did)
        self.assertEqual(pk, kp.public_key)
        self.assertEqual(tp.public_key_to_did(pk), kp.did)

    def test_sign_verify_roundtrip(self):
        kp = tp.generate_keypair()
        msg = "aishield-trust-protocol"
        sig = tp.sign_data(msg, kp.private_key)
        self.assertEqual(len(sig), 128)
        self.assertTrue(tp.verify_signature(msg, sig, kp.public_key))
        self.assertTrue(tp.verify_signature_by_did(msg, sig, kp.did))

    def test_verify_rejects_tampered(self):
        kp = tp.generate_keypair()
        sig = tp.sign_data("hello", kp.private_key)
        self.assertFalse(tp.verify_signature("hello-tampered", sig, kp.public_key))
        self.assertFalse(tp.verify_signature_by_did("hello-tampered", sig, kp.did))
        # 不同 DID 验签应失败
        other = tp.generate_keypair()
        self.assertFalse(tp.verify_signature_by_did("hello", sig, other.did))

    def test_identity_file_persist(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "identity.json")
            kp1 = tp.load_or_create_identity(path)
            self.assertTrue(os.path.exists(path))
            kp2 = tp.load_or_create_identity(path)  # 应加载而非新建
            self.assertEqual(kp1.did, kp2.did)
            self.assertEqual(kp1.private_key, kp2.private_key)

    def test_invalid_did_raises(self):
        with self.assertRaises(ValueError):
            tp.did_to_public_key("did:web:example.com")


class ScoringTest(unittest.TestCase):
    def _rec(self, status, rt=500, when="2026-08-18T00:00:00+00:00"):
        return tp.TransactionRecord(
            provider_did="did:key:zA",
            protocol="mcp",
            status=status,
            response_time_ms=rt,
            created_at=when,
        )

    def test_empty_records_insufficient(self):
        s = tp.compute_trust_score("did:key:zGhost", [])
        self.assertEqual(s.overall_score, 0)
        self.assertEqual(s.confidence_tier, "insufficient_data")
        self.assertEqual(s.grade, "F")

    def test_all_success_full_score(self):
        recs = [self._rec("success", rt=400) for _ in range(120)]
        s = tp.compute_trust_score("did:key:zA", recs)
        self.assertAlmostEqual(s.dimensions.completion_rate, 100.0, places=2)
        self.assertAlmostEqual(s.dimensions.reliability_score, 100.0, places=2)
        self.assertEqual(s.confidence_tier, "high")
        # 全部成功 + 最快响应 → 总分应接近满分
        self.assertGreaterEqual(s.overall_score, 95.0)
        self.assertIn(s.grade, ("A", "B"))

    def test_weighted_math_deterministic(self):
        # 50% 成功、无争议、响应 400ms（响应维度=100）、一致性先验=70
        recs = [self._rec("success", rt=400) for _ in range(5)] + \
               [self._rec("failure", rt=400) for _ in range(5)]
        s = tp.compute_trust_score("did:key:zA", recs)
        # completion_rate = 50, reliability = 100 (0 disputes), response=100, consistency≈70(先验主导)
        self.assertAlmostEqual(s.dimensions.completion_rate, 50.0, places=2)
        self.assertAlmostEqual(s.dimensions.reliability_score, 100.0, places=2)
        self.assertAlmostEqual(s.dimensions.response_time, 100.0, places=2)
        expected = 50 * 0.35 + 100 * 0.30 + s.dimensions.consistency_score * 0.20 + 100 * 0.15
        self.assertAlmostEqual(s.overall_score, round(expected, 2), places=2)
        self.assertEqual(s.confidence_tier, "low")  # 10 records

    def test_ewma_dispute_pulls_down(self):
        fresh = [self._rec("success", when="2026-08-18T00:00:00+00:00") for _ in range(40)]
        s_fresh = tp.compute_trust_score("did:key:zA", fresh)
        disputed = fresh + [self._rec("disputed", when="2026-08-18T00:00:00+00:00") for _ in range(10)]
        s_disputed = tp.compute_trust_score("did:key:zA", disputed)
        self.assertLess(s_disputed.dimensions.reliability_score, s_fresh.dimensions.reliability_score)
        self.assertLess(s_disputed.overall_score, s_fresh.overall_score)


class TrustRegistryTest(unittest.TestCase):
    def test_record_and_score(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "trust_registry.json")
            reg = tp.TrustRegistry(path=path)
            did = "did:key:zProvider"
            for _ in range(30):
                reg.record_event(did, "success", protocol="mcp", response_time_ms=300)
            for _ in range(2):
                reg.record_event(did, "failure", protocol="mcp", response_time_ms=300)
            sd = reg.score_dict(did)
            self.assertEqual(sd["transaction_count"], 32)
            self.assertGreater(sd["overall_score"], 0)
            self.assertLess(sd["overall_score"], 100)
            self.assertEqual(sd["confidence_tier"], "medium")

    def test_registry_persists(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "trust_registry.json")
            reg1 = tp.TrustRegistry(path=path)
            reg1.record_event("did:key:zP", "success", protocol="a2a")
            # 新实例从磁盘加载
            reg2 = tp.TrustRegistry(path=path)
            self.assertEqual(len(reg2.events_for("did:key:zP")), 1)
            self.assertEqual(reg2.score("did:key:zP").transaction_count, 1)

    def test_registry_verify_identity(self):
        kp = tp.generate_keypair()
        reg = tp.TrustRegistry(path=os.path.join(tempfile.mkdtemp(), "t.json"))
        sig = tp.sign_data("trusted-payload", kp.private_key)
        self.assertTrue(reg.verify_identity("trusted-payload", sig, kp.did))
        self.assertFalse(reg.verify_identity("other", sig, kp.did))

    def test_empty_registry_score(self):
        reg = tp.TrustRegistry(path=os.path.join(tempfile.mkdtemp(), "empty.json"))
        s = reg.score("did:key:zNobody")
        self.assertEqual(s.confidence_tier, "insufficient_data")
        self.assertEqual(s.overall_score, 0)


if __name__ == "__main__":
    unittest.main()
