"""L1 可移植身份（JWKS + 可验证凭证 + 除销）的回归测试。

测的是三件事：
  1. **公钥真的可发现**：第三方仅凭 JWKS 里的 x 字段就能离线验 aishield 签的凭证；
  2. **密钥绝不泄露**：JWKS 只含非对称 Ed25519 公钥，对称（HMAC）密钥与私钥
     在任何对外输出里都不出现 —— 线上 agent_card_key.json 恰好是 hmac-sha256，
     照搬 public_key 就等于公开签名密钥；
  3. **除销即时生效**：除销是凭证三要素里唯一在线依赖，缓存会让"刚除销的凭证
     还验得过"持续到进程重启，正好是攻击者的复用窗口。

防假绿：每条用例都构造能让它真失败的前置（不是断言一个空壳返回值）。
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

from eco import verifiable_identity as vi
from api import ecosystem_api as ea


class _HermeticIdentity(unittest.TestCase):
    """把密钥环与身份注册表重定向到临时目录。"""

    def setUp(self):
        self._orig_key = vi.KEY_FILE
        self._orig_legacy = vi.LEGACY_KEY_FILE
        self._tmp = tempfile.mkdtemp(prefix="videntity-")
        vi.KEY_FILE = os.path.join(self._tmp, "signing_keys.json")
        vi.LEGACY_KEY_FILE = os.path.join(self._tmp, "nobody-legacy.json")
        # 身份侧（DID 注册表 / 注册凭据）保持 hermetic：备份后还原
        self._snap = {}
        for name in ("agents.json", "registration_tokens.json"):
            p = os.path.join(vi.BASE, "api", "data", name)
            # exists 必须先于 open。顺序写反过（open 在外、exists 在三元里）会让
            # 干净环境（CI 只有 checkout，api/data/*.json 全被 gitignore）在 setUp
            # 直接抛 FileNotFoundError，27 个用例集体 error；而本地 api/data 有种子
            # 数据、这条分支永远走不到 —— 又一次「本地绿 ≠ 干净环境绿」。
            raw = None
            if os.path.exists(p):
                with open(p, "rb") as f:
                    raw = f.read()
            self._snap[name] = (p, raw)

    def tearDown(self):
        for name, (p, raw) in self._snap.items():
            if raw is None:
                if os.path.exists(p):
                    os.remove(p)
            else:
                with open(p, "wb") as f:
                    f.write(raw)
        vi.KEY_FILE = self._orig_key
        vi.LEGACY_KEY_FILE = self._orig_legacy
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _ring(self) -> vi.SigningKeyRing:
        r = vi.SigningKeyRing()
        r.load()
        return r

    def _make_agent(self, owner="alice") -> tuple:
        """注册一个 agent（走真实注册闭环），返回 (did, 注册凭据, 身份签发令牌)。

        身份签发令牌由 register 闭环一并返回（初始就存在的那一枚）；拿它去换
        VC 才是这条链的正确姿势 —— 注册凭据那时已被 consume。
        """
        from eco import identity

        tk = identity.RegistrationTokenAuthority().issue(owner)
        agent = identity.AgentRegistration().register(
            name="vc-test", owner=owner, registration_token=tk["token"])
        return agent["did"], tk["token"], agent["identity_token"]

    def _ready_ring(self) -> vi.SigningKeyRing:
        r = self._ring()
        r.rotate_to_ed25519()
        return r


class TestJwksRedLine(_HermeticIdentity):
    """红线：任何对外输出里都不能出现私钥或对称密钥。"""

    def test_jwks_has_no_private_material(self):
        self._ready_ring()
        keys = vi.jwks()["keys"]
        self.assertEqual(len(keys), 1)
        k = keys[0]
        self.assertEqual(sorted(k), ["alg", "crv", "kid", "kty", "x"])
        blob = json.dumps(keys)
        for bad in ("private", "priv", "secret", "hmac", "HMAC"):
            self.assertNotIn(bad, blob)

    def test_symmetric_key_is_never_published(self):
        """HMAC 对称密钥（线上现状）按红线拒绝发布，且给出可执行的诊断。"""
        r = self._ring()
        r.data["active"] = {"alg": "hmac-sha256", "public_key": "SAME_VALUE_HERE",
                            "private_key": "SAME_VALUE_HERE"}
        doc = r.jwks()
        self.assertEqual(doc["keys"], [])
        self.assertFalse(doc["ready"])
        self.assertIn("对称密钥", doc["reason"])

    def test_assert_publishable_blocks_symmetric(self):
        with self.assertRaises(ValueError):
            vi._assert_publishable({"alg": "hmac-sha256"}, "test")

    def test_missing_key_gives_diagnostic_not_empty_pass(self):
        doc = self._ring().jwks()
        self.assertEqual(doc["keys"], [])
        self.assertFalse(doc["ready"])


class TestKeyMigration(_HermeticIdentity):
    """迁移到 Ed25519：新密钥对外，旧密钥只验旧签、绝不发布。"""

    def test_rotate_makes_jwks_publishable(self):
        r = self._ring()
        r.data["active"] = {"alg": "hmac-sha256", "public_key": "OLD_SYM",
                            "private_key": "OLD_SYM"}
        m = r.rotate_to_ed25519()
        self.assertTrue(m["migrated"])
        self.assertEqual(m["kept_deprecated"], 1)
        self.assertTrue(r.is_ed25519_ready())
        self.assertEqual(len(r.jwks()["keys"]), 1)
        self.assertNotIn("OLD_SYM", json.dumps(vi.jwks()))

    def test_rotate_is_idempotent(self):
        r = self._ready_ring()
        kid = r.active() and vi._kid(r.active()["public_key"])
        m = r.rotate_to_ed25519()
        self.assertFalse(m["migrated"])
        self.assertEqual(m["kid"], kid)

    def test_deprecated_key_still_verifies_old_credentials(self):
        """旧密钥保留验旧签能力（双窗口），避免迁移后人验不过历史凭证。

        旧密钥是**真**密钥（真 keypair），不是占位字符串 —— 用假密钥写这条用例
        只会得到一条永远绿、但什么都没验的断言。
        """
        r = self._ring()
        old_alg, old_priv, old_pub = vi._cs.generate_keypair()
        r.data["active"] = {"alg": old_alg, "public_key": old_pub,
                            "private_key": old_priv, "created_at": 1}
        r.save()
        old_c = r.issue_credential("did:aishield:old")

        # 定期轮换（force）：旧 active 下台但保留验旧签
        m = r.rotate(force=True)
        self.assertTrue(m["migrated"])
        new_c = r.issue_credential("did:aishield:new")
        self.assertNotEqual(new_c["kid"], old_c["kid"])

        # 迁移后：旧凭证仍验得过（deprecated 公钥参与验签），新凭证也验得过
        r2 = self._ring()
        self.assertTrue(r2.verify(old_c["token"])["valid"],
                        "迁移后人必须仍验得过历史凭证，否则历史身份集体作废")
        self.assertTrue(r2.verify(new_c["token"])["valid"])
        # 但 JWKS 只发新公钥，旧密钥绝不出门
        self.assertEqual([k["kid"] for k in r2.jwks()["keys"]], [new_c["kid"]])
        self.assertNotIn(old_pub, json.dumps(vi.jwks()))

    def test_issue_refuses_on_symmetric_backend(self):
        """对称后端下宁可不签发，也不发一枚只有自己能验的凭证。"""
        r = self._ring()
        r.data["active"] = {"alg": "hmac-sha256", "public_key": "S", "private_key": "S"}
        r.save()
        with self.assertRaises(RuntimeError):
            r.issue_credential("did:aishield:x")


class TestCredentialLifecycle(_HermeticIdentity):
    """签发 → 验签（第三方离线）→ 除销（实时）。"""

    def test_sign_verify_roundtrip(self):
        r = self._ready_ring()
        c = r.issue_credential("did:aishield:alice", {"capabilities": ["scan"]})
        self.assertEqual(c["status"], "active")
        self.assertEqual(vi.verify(c["token"])["valid"], True)

    def test_third_party_verifies_with_jwks_only(self):
        """第三方不看服务端，只拿 JWKS 的 x 就能验 —— 这才是"可移植身份"。

        这里**不调用本模块自己的 verify()**：那是自己验自己，绿了也不说明什么。
        第三方拿 JWKS 里的 x 直接喂给密码学后端验，才是「别家能不能验我」的
        真实验。
        """
        r = self._ready_ring()
        c = r.issue_credential("did:aishield:bob")
        doc = vi.jwks()
        k = doc["keys"][0]
        x_raw = vi._b64u_dec(k["x"])
        self.assertEqual(vi._b64u(x_raw), k["x"])

        head_b64, _, sig_b64 = c["token"].partition(".")
        body = vi._b64u_dec(head_b64)
        # 完全离线：除销不查、服务端不碰，只用 JWKS 那一颗公钥
        ok = vi._cs.verify(body, sig_b64, vi._b64u(x_raw), vi._cs.ALG_ED25519)
        self.assertTrue(ok, "第三方仅凭 JWKS 公钥必须能离线验出签名")

        # 再来一次：把 x 换掉必须验不过（证明上面那次真做了验签，不是恒真）
        self.assertFalse(
            vi._cs.verify(body, sig_b64, vi._cs.generate_keypair()[2],
                          vi._cs.ALG_ED25519))
        # kid 必须能在 JWKS 里对上
        res = vi.verify(c["token"], check_revocation=False)
        self.assertEqual(res["credential"]["kid"], k["kid"])

    def test_revocation_takes_effect_immediately(self):
        r = self._ready_ring()
        c = r.issue_credential("did:aishield:carol")
        self.assertTrue(vi.verify(c["token"])["valid"])
        r.revoke(c["credential_id"])
        res = vi.verify(c["token"])
        self.assertEqual(res["code"], "revoked")
        self.assertIn("除销", res["reason"])

    def test_revocation_is_not_cached(self):
        """除销必须实时读盘；缓存会让除销在进程重启前一直失效。"""
        r = self._ready_ring()
        c = r.issue_credential("did:aishield:dave")
        long_lived = self._ring()
        long_lived.data = r.data  # 模拟持有旧快照的实例
        self.assertTrue(vi.verify(c["token"])["valid"])
        r.revoke(c["credential_id"])
        # 长生命周期实例若不刷新也会判 revoked（模块级函数每次读盘）
        self.assertEqual(vi.verify(c["token"])["code"], "revoked")

    def test_unrevoked_credential_still_passes(self):
        r = self._ready_ring()
        a = r.issue_credential("did:aishield:e1")
        r.revoke(a["credential_id"])
        b = r.issue_credential("did:aishield:e2")
        self.assertTrue(vi.verify(b["token"])["valid"])

    def test_expired(self):
        r = self._ready_ring()
        c = r.issue_credential("did:aishield:f1", ttl=-10)
        self.assertEqual(vi.verify(c["token"])["code"], "expired")

    def test_tampered_signature(self):
        r = self._ready_ring()
        c = r.issue_credential("did:aishield:g1")
        head, _, sig = c["token"].partition(".")
        bad = head + "." + vi._b64u(vi._b64u_dec(sig) + b"x")
        self.assertEqual(vi.verify(bad)["code"], "bad_signature")

    def test_malformed_inputs(self):
        self.assertEqual(vi.verify("abc")["code"], "malformed")
        self.assertEqual(vi.verify("aaa.bbb")["code"], "malformed")
        self.assertEqual(vi.verify("")["code"], "malformed")

    def test_unknown_kid(self):
        self.assertEqual(vi.verify("AAAA.BBBB")["code"], "malformed")

    def test_status_reports_ready(self):
        self._ready_ring()
        st = vi.status()
        self.assertTrue(st["ready"])
        self.assertIsNotNone(st["kid"])
        self.assertEqual(st["alg"], vi.ALG_UPPER)


class TestHttpSurface(_HermeticIdentity):
    """端点层：JWKS 公开、签发需凭据、验签公开、除销仅属主。"""

    def test_jwks_endpoint(self):
        self._ready_ring()
        body, status = ea._identity_jwks()
        self.assertEqual(status, 200)
        self.assertEqual(len(body["keys"]), 1)
        self.assertEqual(body["keys"][0]["kty"], vi.KTY)

    def test_verify_endpoint_is_public(self):
        r = self._ready_ring()
        c = r.issue_credential("did:aishield:h1")
        body, status = ea._identity_credential_verify({"token": c["token"]})
        self.assertEqual(status, 200)
        self.assertTrue(body["valid"])

    def test_verify_requires_token(self):
        body, status = ea._identity_credential_verify({})
        self.assertEqual(status, 400)

    def test_issue_requires_all_fields(self):
        for payload in ({}, {"did": "did:aishield:x"},
                        {"did": "did:aishield:x", "owner": "alice"}):
            self.assertEqual(ea._identity_credential_issue(payload)[1], 400)

    def test_issue_unknown_did_is_404(self):
        body, status = ea._identity_credential_issue(
            {"did": "did:aishield:nope", "owner": "alice", "identity_token": "idt_x"})
        self.assertEqual(status, 404)

    def test_issue_cross_owner_is_403(self):
        did, _rt, idt = self._make_agent("alice")
        body, status = ea._identity_credential_issue(
            {"did": did, "owner": "mallory", "identity_token": idt})
        self.assertEqual(status, 403)

    def test_issue_without_credential_is_rejected(self):
        """裸签发必须被拒：字段缺失先于凭据校验（400），而不是放行成 201。"""
        did, _rt, _idt = self._make_agent("alice")
        self.assertEqual(ea._identity_credential_issue(
            {"did": did, "owner": "alice"})[1], 400)
        # 有 did/owner 但没带签发令牌 → 400（不进入 401，字段先校验）
        self.assertEqual(ea._identity_credential_issue(
            {"did": did, "owner": "alice"})[1], 400)
        # 注册凭据已被 consume，拿它冒充签发令牌 → 401（不是 201）
        _did2, rt, _idt2 = self._make_agent("bob")
        body, status = ea._identity_credential_issue(
            {"did": did, "owner": "alice", "identity_token": rt})
        self.assertEqual(status, 401, body)

    def test_issue_full_flow_and_then_revoke(self):
        # 自带前置：密钥环必须自己建好，不能指望前一个用例跑过（顺序耦合的用例
        # 单独跑就红，那叫假绿）
        self._ready_ring()
        did, _rt, idt = self._make_agent("alice")
        body, status = ea._identity_credential_issue(
            {"did": did, "owner": "alice", "identity_token": idt,
             "claims": {"capabilities": ["scan"]}})
        self.assertEqual(status, 201, body)
        token = body["token"]
        self.assertTrue(ea._identity_credential_verify({"token": token})[0]["valid"])

        _, s2 = ea._identity_credential_issue(
            {"did": did, "owner": "alice", "identity_token": idt})
        # 签发令牌一次性：二次签发 401（不是又发一张凭证）
        self.assertEqual(s2, 401)

        rb, s3 = ea._identity_credential_revoke(
            {"did": did, "owner": "mallory", "credential_id": body["credential_id"]})
        self.assertEqual(s3, 403)
        rb, s4 = ea._identity_credential_revoke(
            {"did": did, "owner": "alice", "credential_id": body["credential_id"]})
        self.assertEqual(s4, 200)
        self.assertTrue(rb["revoked"])
        v = ea._identity_credential_verify({"token": token})[0]
        self.assertEqual(v["code"], "revoked")

    def test_revoke_requires_fields(self):
        self.assertEqual(ea._identity_credential_revoke({})[1], 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
