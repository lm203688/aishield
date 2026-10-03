"""身份锚点闭环测试：注册凭据 → 归属 → 注销 → 审计（硬骨头 #363）。

为什么单列一个文件：``POST /api/v1/identity/register`` 长期是**裸端点** ——
任何人都能往公开注册表写一个 DID，却没有对应手段把它取回来（`tests/test_linkages.py`
里那条"裸注册必须 401"的断言因此一直 skip 在服务器没起的状态）。本文件把闭环钉死：

    无凭据 → 401（注册根本不发生）
    越权注销 → 403（归属是硬边界）
    正常注销 → status=inactive + revoked_at + 可回放的审计事件

隔离说明：eco/identity.py 把身份数据落在 ``api/data/``，本用例一律备份字节并在
tearDown 里逐字节还原（探针/测试都不许在仓库留下别的 DID 残迹）。
"""

import json
import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eco import identity                                    # noqa: E402
from api import ecosystem_api                               # noqa: E402

_AGENTS = identity.AGENTS_FILE
_TOKENS = identity.TOKENS_FILE
_EVENTS = identity.EVENTS_FILE


def _snapshot():
    snap = {}
    for p in (_AGENTS, _TOKENS, _EVENTS):
        if os.path.exists(p):
            with open(p, "rb") as f:
                snap[p] = f.read()
    return snap


def _restore(snap):
    for p in (_AGENTS, _TOKENS, _EVENTS):
        if os.path.exists(p):
            os.remove(p)
    for p, blob in snap.items():
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        with open(p, "wb") as f:
            f.write(blob)


def _events():
    if not os.path.exists(_EVENTS):
        return []
    out = []
    with open(_EVENTS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    return out


class IdentityRevocationTestCase(unittest.TestCase):
    def setUp(self):
        self._snap = _snapshot()
        for p in (_AGENTS, _TOKENS, _EVENTS):
            if os.path.exists(p):
                os.remove(p)

    def tearDown(self):
        _restore(self._snap)

    # ── 辅助 ──
    def _issue(self, owner="alice"):
        return identity.RegistrationTokenAuthority().issue(owner)

    def _register(self, owner="alice", token=None, name="probe-agent"):
        tk = self._issue(owner) if token is None else token
        reg = identity.AgentRegistration()
        return reg.register(name=name, owner=owner,
                            registration_token=tk["token"])


class TestRegistrationCredential(IdentityRevocationTestCase):
    """注册凭据的签发 / 一次性 / 归属一致性。"""

    def test_bare_registration_is_rejected(self):
        """裸注册不许成 —— 这是 test_linkages 长期期望但从未真跑过的那条。"""
        with self.assertRaises(identity.IdentityAuthError):
            identity.AgentRegistration().register(name="ghost", owner="mallory")

    def test_owner_is_mandatory_with_token(self):
        """有凭据没 owner 也不许注册：归属是后续所有鉴权的锚。"""
        with self.assertRaises(identity.IdentityAuthError):
            identity.AgentRegistration().register(name="ghost", owner="",
                                                  registration_token="rt_zz")

    def test_token_is_single_use(self):
        tk = {"token": identity.RegistrationTokenAuthority().issue("alice")["token"]}
        self._register(token=tk)
        with self.assertRaises(identity.IdentityAuthError):
            self._register(token=tk)

    def test_token_revoked_before_use(self):
        issued = identity.RegistrationTokenAuthority().issue("alice")
        identity.RegistrationTokenAuthority().revoke(issued["token_id"], owner="alice")
        with self.assertRaises(identity.IdentityAuthError):
            self._register(token={"token": issued["token"]})

    def test_issue_requires_owner(self):
        with self.assertRaises(ValueError):
            identity.RegistrationTokenAuthority().issue("  ")


class TestRevocationLoop(unittest.TestCase):
    """注销闭环 + 越权拦截 + 审计可回放。"""

    def setUp(self):
        self._snap = _snapshot()
        for p in (_AGENTS, _TOKENS, _EVENTS):
            if os.path.exists(p):
                os.remove(p)

    def tearDown(self):
        _restore(self._snap)

    def _register(self, owner="alice"):
        tk = identity.RegistrationTokenAuthority().issue(owner)
        reg = identity.AgentRegistration()
        return reg.register(name="probe-agent", owner=owner,
                            registration_token=tk["token"])

    def test_revoke_by_owner(self):
        a = self._register("alice")
        reg = identity.AgentRegistration()
        self.assertTrue(reg.revoke_agent(a["did"], owner="alice"))
        after = reg.get_agent(a["did"])
        self.assertEqual(after["status"], "inactive")
        self.assertTrue(after.get("revoked_at"))

    def test_revoke_by_revoke_token(self):
        a = self._register("alice")
        reg = identity.AgentRegistration()
        self.assertTrue(reg.revoke_agent(a["did"], revoke_token=a["revoke_token"]))
        self.assertEqual(reg.get_agent(a["did"])["status"], "inactive")

    def test_cross_owner_revoke_is_forbidden(self):
        """越权必须 403：注销权一旦可借出，注册表就是任人摘除的公共牌。"""
        a = self._register("alice")
        with self.assertRaises(identity.IdentityForbidden):
            identity.AgentRegistration().revoke_agent(a["did"], owner="mallory")
        self.assertEqual(identity.AgentRegistration().get_agent(a["did"])["status"],
                         "active")

    def test_wrong_revoke_token_is_forbidden(self):
        a = self._register("alice")
        with self.assertRaises(identity.IdentityForbidden):
            identity.AgentRegistration().revoke_agent(a["did"], revoke_token="guess")

    def test_revoke_missing_did_returns_none(self):
        self.assertIsNone(identity.AgentRegistration().revoke_agent("did:aishield:nope"))

    def test_revoke_is_idempotent(self):
        a = self._register("alice")
        reg = identity.AgentRegistration()
        self.assertTrue(reg.revoke_agent(a["did"], owner="alice"))
        self.assertFalse(reg.revoke_agent(a["did"], owner="alice"))

    def test_public_view_strips_secrets(self):
        a = self._register("alice")
        view = identity.AgentRegistration().public_view(a)
        self.assertNotIn("revoke_token_hash", view)
        self.assertNotIn("registration_token_id", view)

    def test_revoke_token_never_persisted_in_plain(self):
        a = self._register("alice")
        with open(_AGENTS, encoding="utf-8") as f:
            raw = f.read()
        self.assertIn(a["revoke_token_hash"], raw)
        self.assertNotIn(a["revoke_token"], raw)

    def test_audit_events_are_replayable(self):
        a = self._register("alice")
        identity.AgentRegistration().revoke_agent(a["did"], owner="alice")
        events = _events()
        kinds = [(e["event"], e["result"]) for e in events]
        self.assertIn(("register", "ok"), kinds)
        self.assertIn(("revoke", "ok"), kinds)
        self.assertEqual(events[0]["did"], a["did"])


class TestIdentityApiSurface(unittest.TestCase):
    """API 层的状态码映射（401 / 403 / 404 / 200）。"""

    def setUp(self):
        self._snap = _snapshot()
        for p in (_AGENTS, _TOKENS, _EVENTS):
            if os.path.exists(p):
                os.remove(p)

    def tearDown(self):
        _restore(self._snap)

    def test_register_without_token_is_401(self):
        payload, status = ecosystem_api._identity_register(
            {"name": "ghost", "owner": "mallory"})
        self.assertEqual(status, 401)
        self.assertIn("registration_token", payload["error"])

    def test_register_with_bad_token_is_401(self):
        payload, status = ecosystem_api._identity_register(
            {"name": "ghost", "owner": "mallory", "registration_token": "rt_bogus"})
        self.assertEqual(status, 401)

    def test_token_issue_requires_owner(self):
        payload, status = ecosystem_api._identity_token_issue({})
        self.assertEqual(status, 400)

    def test_full_loop_through_api_handlers(self):
        """领凭据 → 注册 → 越权 403 → 正常注销 200。"""
        # 领取凭据（明文只在响应里出现这一次）
        issued, s_issue = ecosystem_api._identity_token_issue({"owner": "alice"})
        self.assertEqual(s_issue, 201)
        self.assertTrue(issued["token"].startswith(identity._TOKEN_PREFIX))

        body, status = ecosystem_api._identity_register(
            {"name": "api-agent", "owner": "alice",
             "registration_token": issued["token"]})
        self.assertEqual(status, 201)
        did = body["agent"]["did"]
        self.assertIn("revoke_token", body["agent"])

        reg = identity.AgentRegistration()
        bad, s_bad = ecosystem_api._identity_revoke(did, owner="mallory")
        self.assertEqual(s_bad, 403)
        self.assertEqual(reg.get_agent(did)["status"], "active")

        ok, s_ok = ecosystem_api._identity_revoke(did, owner="alice")
        self.assertEqual(s_ok, 200)
        self.assertEqual(ok["status"], "inactive")

        missing, s_missing = ecosystem_api._identity_revoke("did:aishield:nope",
                                                           owner="alice")
        self.assertEqual(s_missing, 404)

    def test_delete_handler_rejects_unknown_path(self):
        payload, status = ecosystem_api.handle_delete("/api/v1/nope/deep")
        self.assertEqual(status, 404)
        self.assertIn("Not found", payload["error"])

    def test_delete_handler_revokes_owner_from_query(self):
        issued, _ = ecosystem_api._identity_token_issue({"owner": "alice"})
        body, _status = ecosystem_api._identity_register(
            {"name": "del-agent", "owner": "alice",
             "registration_token": issued["token"]})
        did = body["agent"]["did"]
        # 走 query 形态（curl -X DELETE 不带 body 也能注销）
        payload, status = ecosystem_api.handle_delete(
            f"/api/v1/identity/agents/{did}", {"owner": ["alice"]})
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "inactive")


if __name__ == "__main__":
    unittest.main()
