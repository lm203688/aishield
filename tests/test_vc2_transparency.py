"""FTM 契约测试（Program D）：W3C VC 2.0 自认证 + CT 式透明日志。

两条主线：
  1. VC 2.0 / VC-JWT —— 第三方**只拿 JWT 字符串**（无密钥环、无服务
     在线）就能从 did:key 解出公钥验签；篡改/过期/除销/非 did:key
     issuer 各有各的拒绝码。
  2. 透明日志 —— Merkle 包含证明在树尺寸 1..10 的**每个**索引上都
     必须自洽（这是 RFC 6962 实现最容易错的地方，用穷举钉死）；
     签名树头可验证；错误结构一律拒。
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
from eco import did_key
from eco import transparency_log as tl
from eco import verifiable_identity as vi


class _VC2Env(unittest.TestCase):
    """隔离的密钥环境：临时 KEY_FILE，保证 Ed25519 active。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.keyfile = os.path.join(self._td.name, "signing_keys.json")
        self._p = mock.patch.object(vi, "KEY_FILE", self.keyfile)
        self._p.start()
        self.ring = vi.SigningKeyRing(path=self.keyfile)
        self.ring.rotate_to_ed25519(persist=True)

    def tearDown(self):
        self._p.stop()
        self._td.cleanup()


class TestVC2IssueAndSelfCertifiedVerify(_VC2Env):
    def test_issue_and_verify_roundtrip_third_party(self):
        issued = vi.issue_vc2("did:key:z6MkSUBJECTexample000000000000000000000",
                              {"role": "scanner", "scope": ["read"]})
        vc = issued["credential"]
        self.assertEqual(vc["@context"], ["https://www.w3.org/ns/credentials/v2"])
        self.assertIn("VerifiableCredential", vc["type"])
        self.assertIn("aishieldAgentIdentityV2", vc["type"])
        self.assertTrue(did_key.is_did_key(vc["issuer"]))
        self.assertEqual(vc["credentialSubject"]["id"],
                         "did:key:z6MkSUBJECTexample000000000000000000000")
        self.assertIn("validFrom", vc)
        self.assertIn("validUntil", vc)
        self.assertIn("credentialStatus", vc)

        # 第三方视角：只有 JWT 字符串
        res = vi.verify_vc2(issued["jwt"])
        self.assertTrue(res["valid"], res)
        self.assertEqual(res["code"], "ok")
        self.assertIn("self-certified", res["verification"])

    def test_verify_via_dict_with_jwt(self):
        issued = vi.issue_vc2("did:key:z6Mkabc")
        res = vi.verify_vc2(issued)
        self.assertTrue(res["valid"])

    def test_tampered_jwt_rejected(self):
        issued = vi.issue_vc2("did:key:z6Mkabc")
        head, payload, sig = issued["jwt"].split(".")
        # 改 payload 不改签名 → 签名失败
        forged = json.loads(vi._b64u_dec(payload))
        forged["sub"] = "did:key:z6MkATTACKER"
        new_payload = vi._b64u(json.dumps(forged, ensure_ascii=False,
                                          sort_keys=True, separators=(",", ":"))
                               .encode("utf-8"))
        res = vi.verify_vc2(f"{head}.{new_payload}.{sig}")
        self.assertFalse(res["valid"])
        self.assertEqual(res["code"], "bad_signature")

    def test_expired_vc_rejected(self):
        issued = vi.issue_vc2("did:key:z6Mkabc", ttl=-10)
        res = vi.verify_vc2(issued["jwt"])
        self.assertFalse(res["valid"])
        self.assertEqual(res["code"], "expired")

    def test_revoked_vc_rejected(self):
        issued = vi.issue_vc2("did:key:z6Mkabc")
        vi.revoke(issued["credential_id"])
        res = vi.verify_vc2(issued["jwt"])
        self.assertFalse(res["valid"])
        self.assertEqual(res["code"], "revoked")

    def test_unsecured_bare_datamodel_rejected(self):
        vc = {"@context": ["https://www.w3.org/ns/credentials/v2"],
              "type": ["VerifiableCredential"]}
        res = vi.verify_vc2(vc)
        self.assertFalse(res["valid"])
        self.assertEqual(res["code"], "unsecured")

    def test_non_did_key_issuer_is_honest_not_fake_verified(self):
        # 旧 did:aishield 标签 issuer：不假装验过，明说无法自认证
        ring = vi.SigningKeyRing().load()
        alg, priv, pub = cs.generate_keypair()
        kid = vi._kid(pub)
        vc = {"@context": ["https://www.w3.org/ns/credentials/v2"],
              "type": ["VerifiableCredential"],
              "issuer": "did:aishield:" + kid,
              "credentialSubject": {"id": "did:key:z6Mkx"}}
        payload = {"iss": vc["issuer"], "sub": "did:key:z6Mkx",
                   "nbf": vi._now(), "exp": vi._now() + 3600,
                   "jti": "x1", "vc": vc}
        header = {"typ": "JWT", "alg": "EdDSA"}
        signing_input = (vi._b64u(json.dumps(header, sort_keys=True,
                                             separators=(",", ":")).encode())
                         + "." + vi._b64u(json.dumps(payload, sort_keys=True,
                                                     separators=(",", ":")).encode()))
        sig = cs.sign(signing_input.encode("ascii"), priv, cs.ALG_ED25519)
        jwt = signing_input + "." + vi._b64u(vi._b64u_dec(sig))
        res = vi.verify_vc2(jwt)
        self.assertFalse(res["valid"])
        self.assertEqual(res["code"], "non_self_certified_issuer")


class TestTransparencyLogMerkle(unittest.TestCase):
    """Merkle 证明的穷举正确性：树尺寸 1..10 × 每个索引。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.log = tl.TransparencyLog(path=os.path.join(self._td.name, "tlog.jsonl"))

    def tearDown(self):
        self._td.cleanup()

    def test_inclusion_proof_all_sizes_all_indices(self):
        for size in range(1, 11):
            log = tl.TransparencyLog(path=os.path.join(
                self._td.name, f"tlog_{size}.jsonl"))
            leaves = []
            for i in range(size):
                r = log.append({"i": i, "blob": f"entry-{i}-{'x' * (i % 7)}"})
                leaves.append(r["leaf_hash"])
            # 根与层叠构造一致
            self.assertEqual(log.root(), tl._merkle_root(leaves))
            for idx in range(size):
                proof = log.inclusion_proof(idx)
                self.assertTrue(
                    log.verify_inclusion(leaves[idx], proof),
                    f"size={size} idx={idx} 的包含证明验证失败")
            # 错误的 leaf_hash 必须拒
            bad = tl._leaf_hash({"i": 999})
            proof = log.inclusion_proof(0)
            self.assertFalse(log.verify_inclusion(bad, proof))
            # 错误的索引必须拒
            proof_wrong_idx = log.inclusion_proof(0)
            if size > 1:
                self.assertFalse(
                    log.verify_inclusion(leaves[1], proof_wrong_idx))
            # 越界索引
            self.assertIn("error", log.inclusion_proof(size))

    def test_root_changes_monotonically_with_appends(self):
        roots = []
        for i in range(5):
            self.log.append({"i": i})
            roots.append(self.log.root())
        self.assertEqual(len(set(roots)), 5)   # 每次追加根都变
        self.assertEqual(self.log.size(), 5)


class TestTransparencyLogSTH(unittest.TestCase):
    """签名树头：真签名可验、篡改可检、结构不符拒。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.log = tl.TransparencyLog(path=os.path.join(self._td.name, "tlog.jsonl"))
        alg, priv, pub = cs.generate_keypair()
        self.key = {"alg": alg, "public_key": pub, "private_key": priv}
        self.kid = tl._kid_of(self.key)
        self.log._signer = lambda: self.key
        self.log.key_resolver = lambda kid: self.key if kid == self.kid else None

    def tearDown(self):
        self._td.cleanup()

    def test_sth_signed_and_verifiable(self):
        r = self.log.append({"demo": 1})
        sth = r["sth"]
        self.assertTrue(sth.get("third_party_verifiable"))
        res = self.log.verify_sth(sth)
        self.assertTrue(res["valid"], res)
        self.assertTrue(res["root_matches_current_tree"])

    def test_tampered_sth_rejected(self):
        r = self.log.append({"demo": 1})
        sth = dict(r["sth"])
        sth["tree_size"] = 99
        res = self.log.verify_sth(sth)
        self.assertFalse(res["valid"])

    def test_sth_for_different_tree_marked_mismatch(self):
        r1 = self.log.append({"demo": 1})
        sth1 = r1["sth"]
        self.log.append({"demo": 2})
        res = self.log.verify_sth(sth1)
        self.assertTrue(res["valid"])                 # 签名本身仍有效
        self.assertFalse(res["root_matches_current_tree"])  # 但根已过期

    def test_unsigned_sth_honest(self):
        self.log._signer = lambda: None
        sth = self.log.sth()
        self.assertIsNone(sth.get("signature"))
        self.assertFalse(sth.get("third_party_verifiable"))
        res = self.log.verify_sth(sth)
        self.assertFalse(res["valid"])

    def test_malformed_proof_rejected(self):
        r = self.log.append({"demo": 1})
        for bad in [
            {"leaf_index": "x", "audit_path": [], "root_hash": "0" * 64, "tree_size": 1},
            {"leaf_index": 0, "audit_path": ["zz"], "root_hash": "0" * 64, "tree_size": 1},
            {"leaf_index": 0, "audit_path": [], "root_hash": "0" * 64, "tree_size": 2},
        ]:
            self.assertFalse(self.log.verify_inclusion(r["leaf_hash"], bad))


if __name__ == "__main__":
    unittest.main(verbosity=2)
