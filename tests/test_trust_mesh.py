# -*- coding: utf-8 -*-
"""
tests/test_trust_mesh.py — Program D (FTM) 联邦信任网格门禁测试

钉死联邦信任铁律：
  1. 签发的 W3C VC 2.0 凭证签名可被 did:key 公钥离线验真（真签名，非占位）。
  2. 凭证被篡改（任一字段）→ 验签失败。
  3. 透明日志哈希链防篡改：插入/改写任一 entry 即被 verify() 定位。
  4. 联邦安全聚合只接收哈希+计数，原始数据零出域（函数不触碰原始 payload）。
  5. 凭证 proof 不含私钥；Ed25519 后端 third_party_verifiable=True。
"""
import os
import json
import tempfile
import unittest

from eco import crypto_sign as cs
from eco import trust_mesh as tm


@unittest.skipIf(cs is None, "eco.crypto_sign 不可用")
class TestTrustMesh(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ftm_test_")
        self.kp = dict(zip(("alg", "private_key", "public_key"),
                           cs.generate_keypair()))
        self.subject = {
            "type": "mcp_server", "url": "https://github.com/example/demo",
            "name": "demo", "score": 92, "level": "gold", "risk": "safe",
            "no_spawn_guarantee": True, "offline_scan": True,
        }
        # 透明日志注入临时路径，避免写真实 api/data
        tm.TransparentLog.path = os.path.join(self.tmp, "trust_log.jsonl")

    def _issue(self):
        return tm.issue_credential(self.subject, keypair=self.kp)

    def test_vc_signature_verifies(self):
        vc = self._issue()
        res = tm.verify_credential(vc)
        self.assertTrue(res["valid"], res)
        # 公钥自认证：issuer 是 did:key，第三方无需信任服务即可验
        self.assertTrue(vc["issuer"].startswith("did:key:z"))

    def test_tampered_credential_fails_verification(self):
        vc = self._issue()
        vc["credentialSubject"]["score"] = 0  # 篡改
        res = tm.verify_credential(vc)
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["reason"])

    def test_proof_does_not_leak_private_key(self):
        vc = self._issue()
        blob = json.dumps(vc, ensure_ascii=False)
        self.assertNotIn(self.kp["private_key"], blob, "proof 不得含私钥")

    def test_third_party_verifiable_under_ed25519(self):
        # 仅当 cryptography 可用（Ed25519）时断言；否则诚实降级
        if cs.have_crypto():
            vc = self._issue()
            self.assertTrue(vc["proof"]["third_party_verifiable"])
            self.assertEqual(vc["proof"]["cryptosuite"], "ed25519-2020")

    def test_transparent_log_append_and_verify(self):
        log = tm.TransparentLog(path=os.path.join(self.tmp, "log.jsonl"))
        for _ in range(3):
            log.append(self._issue())
        v = log.verify()
        self.assertTrue(v["valid"], v)
        self.assertEqual(v["entries"], 3)

    def test_transparent_log_detects_tamper(self):
        log = tm.TransparentLog(path=os.path.join(self.tmp, "log2.jsonl"))
        for _ in range(2):
            log.append(self._issue())
        # 真正篡改第一条日志 entry 的内容（改 subject_sha256），打破其哈希
        with open(log.path, "r", encoding="utf-8") as f:
            entries = [json.loads(l) for l in f if l.strip()]
        entries[0]["subject_sha256"] = "0" * 64  # 内容篡改
        with open(log.path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        v = log.verify()
        self.assertFalse(v["valid"], v)

    def test_secure_aggregation_never_sees_raw_data(self):
        # 各节点只报哈希+计数；聚合结果不含任何原始 payload
        summaries = [
            {"node_id": "n1", "attack_vectors": [
                {"hash": "aaa", "count": 3}, {"hash": "bbb", "count": 1}]},
            {"node_id": "n2", "attack_vectors": [
                {"hash": "aaa", "count": 2}, {"hash": "ccc", "count": 5}]},
        ]
        agg = tm.secure_aggregate(summaries)
        self.assertEqual(agg["contributing_nodes"], 2)
        # 同一个攻击向量 aaa 跨 2 节点聚合
        self.assertEqual(agg["attack_vectors"]["aaa"], {"count": 5, "nodes": 2})
        self.assertEqual(agg["attack_vectors"]["ccc"], {"count": 5, "nodes": 1})
        agg_blob = json.dumps(agg)
        for raw in ("secret", "payload", "raw_data"):
            self.assertNotIn(raw, agg_blob)


if __name__ == "__main__":
    unittest.main()
