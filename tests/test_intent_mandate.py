"""L3 意图授权（Intent Mandate，对齐 AP2 / Verifiable Intent）的回归测试。

测的是 agent 商业化里最缺的一环：**行动之前先签字**。

  1. **意图不可抵赖**：mandate 由 agent 的 Ed25519 密钥签出，第三方仅凭 JWKS
     的 x 就能离线验 —— 不是"服务端说签过就算"；
  2. **边界真的拦得住**：过期、超上限、越动作、换 DID、重放，五种都必须拒；
  3. **账本损坏 fail-closed**：重放账本读不出来时，宁可拒放行也不能当空名单把
     已用过的 mandate 复活 —— 这是唯一一处"放行"依赖在线状态的判断。

防假绿：每条用例都构造能让它真失败的前置（篡改签名、伪造时间、损坏账本），
而不是断言一个空壳的 {"valid": True}。
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import tempfile
import unittest

from eco import verifiable_identity as vi
from eco import intent_mandate as im
from api import ecosystem_api as ea


class _HermeticMandate(unittest.TestCase):
    """把密钥环、重放账本与身份注册表一起重定向到临时目录。"""

    def setUp(self):
        self._orig_key = vi.KEY_FILE
        self._orig_mandate = im.MANDATE_FILE
        self._tmp = tempfile.mkdtemp(prefix="imandate-")
        vi.KEY_FILE = os.path.join(self._tmp, "signing_keys.json")
        im.MANDATE_FILE = os.path.join(self._tmp, "intent_mandates.json")
        # 身份侧（DID 注册表 / 注册凭据）保持 hermetic：备份后逐字节还原
        self._snap = {}
        for name in ("agents.json", "registration_tokens.json"):
            p = os.path.join(vi.BASE, "api", "data", name)
            self._snap[name] = (p, open(p, "rb").read() if os.path.exists(p) else None)

    def tearDown(self):
        for name, (p, raw) in self._snap.items():
            if raw is None:
                if os.path.exists(p):
                    os.remove(p)
            else:
                with open(p, "wb") as f:
                    f.write(raw)
        vi.KEY_FILE = self._orig_key
        im.MANDATE_FILE = self._orig_mandate
        shutil.rmtree(self._tmp, ignore_errors=True)

    # ── 工具 ──
    def _ring(self) -> vi.SigningKeyRing:
        r = vi.SigningKeyRing()
        r.load()
        return r

    def _ready_ring(self) -> vi.SigningKeyRing:
        r = self._ring()
        r.rotate_to_ed25519()
        return r

    def _make_agent(self, owner="alice") -> str:
        """注册一个 agent（走真实注册闭环），返回它的 DID。"""
        from eco import identity

        tk = identity.RegistrationTokenAuthority().issue(owner)
        agent = identity.AgentRegistration().register(
            name="intent-test", owner=owner, registration_token=tk["token"])
        return agent["did"]

    def _issue_via_api(self, owner="alice", action="purchase", **kw):
        did = self._make_agent(owner)
        body = {"agent_did": did, "owner": owner, "action": action}
        body.update(kw)
        return ea._intent_mandate_issue(body)


class TestIssueSurface(_HermeticMandate):
    """签发端点的鉴权与参数边界。"""

    def test_issue_with_symmetric_key_is_503_not_fake_ok(self):
        """生产默认还是 hmac 对称密钥 —— 此时绝不能"签发成功"。"""
        r = self._ring()
        r.data["active"] = {"alg": "hmac-sha256", "public_key": "SAME",
                            "private_key": "SAME"}
        r.save()
        # DID 必须真实存在，否则先撞 404，测不到密钥这一层
        did = self._make_agent("alice")
        body, status = ea._intent_mandate_issue(
            {"agent_did": did, "owner": "alice", "action": "purchase"})
        self.assertEqual(status, 503, "对称密钥下签出的券只能自证，必须显式报错")
        self.assertFalse(body.get("success"))

    def test_issue_unknown_did_is_404(self):
        self._ready_ring()
        body, status = ea._intent_mandate_issue(
            {"agent_did": "did:aishield:nope", "owner": "alice", "action": "purchase"})
        self.assertEqual(status, 404)

    def test_issue_cross_owner_is_403(self):
        self._ready_ring()
        did = self._make_agent("alice")
        body, status = ea._intent_mandate_issue(
            {"agent_did": did, "owner": "mallory", "action": "purchase"})
        self.assertEqual(status, 403)

    def test_issue_requires_fields(self):
        self._ready_ring()
        for bad in ({}, {"agent_did": "did:a", "owner": "o"},
                    {"agent_did": "did:a", "owner": "o", "action": ""}):
            self.assertEqual(ea._intent_mandate_issue(bad)[1], 400)

    def test_ttl_out_of_range_is_400(self):
        self._ready_ring()
        did = self._make_agent("alice")
        for bad_ttl in (0, -5, 999999):
            body, status = ea._intent_mandate_issue(
                {"agent_did": did, "owner": "alice", "action": "purchase", "ttl": bad_ttl})
            self.assertEqual(status, 400, f"ttl={bad_ttl} 应当被拒")

    def test_constraints_must_be_object(self):
        self._ready_ring()
        did = self._make_agent("alice")
        body, status = ea._intent_mandate_issue(
            {"agent_did": did, "owner": "alice", "action": "purchase",
             "constraints": "not-an-object"})
        self.assertEqual(status, 400)

    def test_issue_returns_verifiable_mandate(self):
        self._ready_ring()
        body, status = self._issue_via_api(
            constraints={"max_amount": 100, "currency": "USD", "allowed_actions": ["purchase"]})
        self.assertEqual(status, 201, body)
        for k in ("mandate_id", "token", "kid", "subject", "action", "expires_at"):
            self.assertIn(k, body)
        self.assertTrue(body["token"].count(".") == 1)
        # kid 必须能在 JWKS 里找到，否则第三方无从验签
        kids = [k["kid"] for k in vi.jwks()["keys"]]
        self.assertIn(body["kid"], kids)


class TestOfflineVerifiability(_HermeticMandate):
    """第三方凭 JWKS 离线验 —— 这才是"意图可携带"。"""

    def setUp(self):
        super().setUp()
        self._ready_ring()   # 用例自带前置，不依赖别的用例先跑

    def test_third_party_verifies_without_server(self):
        body, _ = self._issue_via_api(action="purchase")
        token = body["token"]
        # 模拟完全离线的一方：只读 JWKS 拿 x，自己拼验签
        doc = vi.jwks()
        k = [x for x in doc["keys"] if x["kid"] == body["kid"]][0]
        x_raw = base64.urlsafe_b64decode(k["x"] + "=" * (-len(k["x"]) % 4))
        self.assertEqual(vi._b64u(x_raw), k["x"])
        head_b64, _, _sig = token.partition(".")
        payload = json.loads(vi._b64u_dec(head_b64))
        self.assertEqual(payload["sub"], body["subject"])
        self.assertEqual(payload["action"], "purchase")
        self.assertGreater(payload["exp"], payload["iat"])

        res = im.IntentMandate().verify(token, check_replay=False)
        self.assertTrue(res["valid"], "第三方必须能离线验过这张券")

    def test_tampered_token_is_rejected(self):
        body, _ = self._issue_via_api()
        head, sig = body["token"].split(".", 1)
        # 改一个字节再重编（保持合法 base64 与 JSON 结构）
        payload = json.loads(vi._b64u_dec(head))
        payload["action"] = "transfer_all_funds_to_mallory"
        forged = f"{vi._b64u(im._canonical(payload))}.{sig}"
        res = im.IntentMandate().verify(forged, check_replay=False)
        self.assertFalse(res["valid"])
        self.assertEqual(res["code"], im.CODE_BAD_SIGNATURE)

    def test_garbage_token_is_malformed(self):
        for bad in ("", "abc", "a.b.c"):
            res = im.IntentMandate().verify(bad, check_replay=False)
            self.assertFalse(res["valid"], repr(bad))
            self.assertEqual(res["code"], im.CODE_MALFORMED)


class TestEvaluationGates(_HermeticMandate):
    """执行侧真正该调的 evaluate：五道闸门全过才放行。"""

    def setUp(self):
        super().setUp()
        self._ready_ring()
        self.agent_did = self._make_agent("alice")

    def _issue(self, **kw):
        body, status = ea._intent_mandate_issue(
            {"agent_did": self.agent_did, "owner": "alice", "action": "purchase",
             "constraints": {"max_amount": 100, "currency": "USD"},
             "request": {"amount": 10, "currency": "USD", "resource": "sku:1"}})
        self.assertEqual(status, 201, body)
        return body["token"]

    def test_evaluate_ok(self):
        token = self._issue()
        res, status = ea._intent_mandate_evaluate(
            {"token": token, "request": {"amount": 10, "currency": "USD"}})
        self.assertEqual(status, 200)
        self.assertTrue(res["valid"], res)
        self.assertEqual(res["code"], im.CODE_OK)

    def test_replay_is_rejected(self):
        token = self._issue()
        req = {"amount": 10, "currency": "USD"}
        self.assertTrue(ea._intent_mandate_evaluate(
            {"token": token, "request": req})[0]["valid"])
        res, status = ea._intent_mandate_evaluate({"token": token, "request": req})
        self.assertEqual(status, 403)
        self.assertEqual(res["code"], im.CODE_REPLAYED)

    def test_amount_over_limit_is_rejected(self):
        token = self._issue()
        res, status = ea._intent_mandate_evaluate(
            {"token": token, "request": {"amount": 99999, "currency": "USD"}})
        self.assertEqual(status, 403)
        self.assertEqual(res["code"], im.CODE_LIMIT_EXCEEDED)

    def test_missing_amount_is_rejected(self):
        """没带 amount 就不算证明没超上限 —— 不能因为字段缺失就放行。"""
        token = self._issue()
        res, status = ea._intent_mandate_evaluate({"token": token, "request": {}})
        self.assertEqual(status, 403)
        self.assertEqual(res["code"], im.CODE_LIMIT_EXCEEDED)

    def test_currency_mismatch_is_rejected(self):
        token = self._issue()
        res, _ = ea._intent_mandate_evaluate(
            {"token": token, "request": {"amount": 10, "currency": "CNY"}})
        self.assertFalse(res["valid"])
        self.assertEqual(res["code"], im.CODE_SCOPE_VIOLATION)

    def test_scope_violation_on_another_agent(self):
        token = self._issue()
        res, status = ea._intent_mandate_evaluate(
            {"token": token, "request": {"amount": 1, "agent_did": "did:aishield:mallory"}})
        self.assertEqual(status, 403)
        self.assertEqual(res["code"], im.CODE_SCOPE_VIOLATION)

    def test_action_not_in_whitelist_is_rejected(self):
        body, _ = ea._intent_mandate_issue(
            {"agent_did": self.agent_did, "owner": "alice", "action": "purchase",
             "constraints": {"allowed_actions": ["read"], "allowed_resources": ["repo:.*"]}})
        res, status = ea._intent_mandate_evaluate(
            {"token": body["token"], "request": {"action": "purchase"}})
        self.assertEqual(status, 403)
        self.assertEqual(res["code"], im.CODE_SCOPE_VIOLATION)

    def test_resource_out_of_scope_is_rejected(self):
        body, _ = ea._intent_mandate_issue(
            {"agent_did": self.agent_did, "owner": "alice", "action": "purchase",
             "constraints": {"allowed_actions": ["purchase"],
                             "allowed_resources": ["repo:frontend"]}})
        res, status = ea._intent_mandate_evaluate(
            {"token": body["token"], "request": {"action": "purchase",
                                                 "resource": "repo:payment-bot"}})
        self.assertEqual(status, 403)
        self.assertEqual(res["code"], im.CODE_SCOPE_VIOLATION)

    def test_expired_mandate_is_rejected(self):
        """把时间推到授权窗口之外 —— 券本身还签得好好的。"""
        token = self._issue()
        orig = im._now
        im._now = lambda: 10 ** 12
        try:
            res, status = ea._intent_mandate_evaluate({"token": token, "request": {}})
        finally:
            im._now = orig
        self.assertEqual(status, 403)
        self.assertEqual(res["code"], im.CODE_EXPIRED)

    def test_deadline_past_business_gate_is_rejected(self):
        body, _ = ea._intent_mandate_issue(
            {"agent_did": self.agent_did, "owner": "alice", "action": "purchase",
             "ttl": 600,
             "constraints": {"deadline": im._now() + 60}})
        base = im._now()
        orig = im._now
        im._now = lambda: base + 10 ** 6
        try:
            res, _ = ea._intent_mandate_evaluate({"token": body["token"], "request": {}})
        finally:
            im._now = orig
        self.assertFalse(res["valid"])
        self.assertEqual(res["code"], im.CODE_EXPIRED)


class TestLedgerFailClosed(_HermeticMandate):
    """重放账本损坏时，唯一的"在线放行"判断必须 fail-closed。"""

    def test_corrupted_ledger_refuses_to_pass(self):
        self._ready_ring()
        did = self._make_agent("alice")
        body, _ = ea._intent_mandate_issue(
            {"agent_did": did, "owner": "alice", "action": "purchase"})
        # 第一次用掉（写账本）
        self.assertTrue(ea._intent_mandate_evaluate(
            {"token": body["token"], "request": {}})[0]["valid"])
        # 账本损坏：不能把"读不出来"当成"没用过"而放行重放
        with open(im.MANDATE_FILE, "w", encoding="utf-8") as f:
            f.write("{ this is not json")
        body, status = ea._intent_mandate_evaluate(
            {"token": body["token"], "request": {}})
        self.assertEqual(status, 503)
        self.assertFalse(body.get("success"))

    def test_verify_still_judges_signature_when_ledger_broken(self):
        """验签不依赖账本 —— 账本坏了仍应给出**签名层面**的判定。"""
        self._ready_ring()
        did = self._make_agent("alice")
        body, _ = ea._intent_mandate_issue(
            {"agent_did": did, "owner": "alice", "action": "purchase"})
        head, sig = body["token"].split(".", 1)
        forged = f"{head}.{'A' * 10}"     # 签名段换掉，账本内容不动
        with open(im.MANDATE_FILE, "w", encoding="utf-8") as f:
            f.write("{ broken")
        res, status = ea._intent_mandate_verify({"token": forged})
        self.assertEqual(status, 200)
        self.assertFalse(res["valid"])
        self.assertEqual(res["code"], im.CODE_BAD_SIGNATURE,
                         "签名判定不能被账本损坏挪用成别的结果")

    def test_evaluate_requires_token(self):
        self._ready_ring()
        self.assertEqual(ea._intent_mandate_evaluate({})[1], 400)
        self.assertEqual(ea._intent_mandate_verify({})[1], 400)


def status_of(res):
    return res[1]


if __name__ == "__main__":
    unittest.main(verbosity=2)
