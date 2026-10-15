"""RIL 持续证明流契约测试（Program C — Runtime Immune Layer）。

钉死四条：
  1. 快照内容纪律 —— 只含状态摘要（策略**指纹**而非原文、审计链头、
     行为健康、熔断数），无任何密钥材料；
  2. 链完整 + 篡改可定位 —— 任一字节被改，verify() 指出行号与原因；
  3. 签名可第三方验证 —— Ed25519 快照能用 JWKS 同一把公钥验过；
  4. 节流纪律 —— 默认每 N 次判定才签一次；强制触发不经节流。
"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from eco import crypto_sign as cs
from eco import runtime_governance as rg


def _fake_ed25519_key():
    alg, priv, pub = cs.generate_keypair()
    return {"alg": alg, "public_key": pub, "private_key": priv, "created_at": 0}


class AttestationStreamTestBase(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        td = self._td.name
        self.pol = os.path.join(td, "governance.json")
        self.aud = os.path.join(td, "governance_audit.jsonl")
        self.att = os.path.join(td, "runtime_attestations.jsonl")
        self.key = _fake_ed25519_key()
        self._patches = [
            mock.patch.object(rg, "POLICY_FILE", self.pol),
            mock.patch.object(rg, "AUDIT_LOG", self.aud),
            mock.patch.object(rg, "_default_attest", rg.AttestationStream(path=self.att, every=3)),
        ]
        for p in self._patches:
            p.start()
        rg._default_attest._signer = lambda: self.key
        rg._default_attest.key_resolver = (
            lambda kid: self.key if kid == rg._kid_of(self.key) else None)

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self._td.cleanup()


class TestSnapshotContent(AttestationStreamTestBase):
    def test_snapshot_has_no_secret_material(self):
        rg.allow_tool("srv", ["a"])
        entry = rg.attest_now()
        self.assertIsNotNone(entry)
        blob = json.dumps(entry)
        # 只允许出现指纹，不允许出现策略原文/私钥
        self.assertNotIn(self.key["private_key"], blob)
        self.assertNotIn("allow", blob)          # 策略结构不进快照
        self.assertIn("policy_digest", entry)
        self.assertEqual(len(entry["policy_digest"]), 64)   # sha256 hex
        self.assertIn("audit_head_hash", entry)
        self.assertIn("behavior_healthy", entry)

    def test_snapshot_signed_and_third_party_verifiable(self):
        entry = rg.attest_now()
        self.assertTrue(entry.get("third_party_verifiable"))
        self.assertEqual(entry.get("signature_alg"), "ed25519")
        body = {k: v for k, v in entry.items()
                if k not in ("hash", "signature", "signature_alg", "signer_kid",
                             "third_party_verifiable", "unsigned_reason")}
        raw = json.dumps(body, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
        # 第三方视角：只拿 JWKS 里的公钥，不碰本服务
        self.assertTrue(cs.verify(raw, entry["signature"],
                                  self.key["public_key"], cs.ALG_ED25519))

    def test_hmac_degradation_is_honest(self):
        alg, priv, pub = cs.generate_keypair()
        # 造一个 HMAC 对称密钥（生产上来自未迁移环境）
        hmac_key = {"alg": "hmac-sha256", "public_key": priv, "private_key": priv}
        rg._default_attest._signer = lambda: hmac_key
        entry = rg.attest_now()
        self.assertFalse(entry.get("third_party_verifiable"),
                         "HMAC 对称密钥签的快照必须诚实标注不可第三方验证")

    def test_no_key_means_unsigned_not_fabricated(self):
        rg._default_attest._signer = lambda: None
        entry = rg.attest_now()
        self.assertIsNone(entry.get("signature"))
        self.assertIn("unsigned_reason", entry)


class TestChainIntegrity(AttestationStreamTestBase):
    def test_chain_valid_then_tamper_detected(self):
        rg.attest_now()
        rg.attest_now()
        ok = rg._default_attest.verify()
        self.assertTrue(ok["valid"], ok)
        self.assertEqual(ok["entries"], 2)

        with open(self.att, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().split("\n") if ln.strip()]
        obj = json.loads(lines[0])
        obj["killed_count"] = 999          # 篡改第一条的状态
        lines[0] = json.dumps(obj, ensure_ascii=False)
        with open(self.att, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        bad = rg._default_attest.verify()
        self.assertFalse(bad["valid"])
        self.assertEqual(bad.get("broken_at"), 1)

    def test_signature_tamper_detected(self):
        rg.attest_now()
        with open(self.att, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().split("\n") if ln.strip()]
        obj = json.loads(lines[0])
        # 改内容 + 同步重算 hash（排除字段与 verify() 口径一致）→ hash 检查
        # 过、签名检查必须抓 —— 这条专门证明"改了还能骗过 hash"的场景
        # 由签名兜底。
        sig_fields = ("hash", "signature", "signature_alg", "signer_kid",
                      "third_party_verifiable", "unsigned_reason")
        obj["policy_digest"] = "0" * 64
        obj["hash"] = rg._sha256(json.dumps(
            {k: v for k, v in obj.items() if k not in sig_fields},
            ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        lines[0] = json.dumps(obj, ensure_ascii=False)
        with open(self.att, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        bad = rg._default_attest.verify()
        self.assertFalse(bad["valid"])
        self.assertIn("签名", bad.get("reason", ""))


class TestThrottle(AttestationStreamTestBase):
    def test_every_n_evaluations(self):
        # every=3：第 1、2 次不签，第 3 次签
        for _ in range(2):
            self.assertIsNone(rg._default_attest.snapshot())
        entry = rg._default_attest.snapshot()
        self.assertIsNotNone(entry)
        self.assertEqual(entry["evaluations"], 3)

    def test_evaluate_integration_writes_stream(self):
        # 走真实 evaluate() 路径（log=True），证明流自动被喂
        rg._default_attest = rg.AttestationStream(path=self.att, every=2)
        rg._default_attest._signer = lambda: self.key
        rg._default_attest.key_resolver = (
            lambda kid: self.key if kid == rg._kid_of(self.key) else None)
        rg.evaluate("srv-a", "tool", log=True)
        rg.evaluate("srv-a", "tool", log=True)
        latest = rg._default_attest.latest()
        self.assertIsNotNone(latest)
        self.assertGreaterEqual(latest["evaluations"], 2)

    def test_attestation_failure_never_blocks_decision(self):
        def _boom():
            raise RuntimeError("stream broken")
        rg._default_attest = mock.Mock(side_effect=None)
        rg._default_attest.snapshot.side_effect = RuntimeError("stream broken")
        res = rg.evaluate("srv-a", "tool", log=True)
        self.assertIn(res["decision"], ("allow", "deny"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
