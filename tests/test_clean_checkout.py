"""干净 checkout 上身份闭环仍然可用（反假绿门禁）。

═════════════════════════════════════════════════════════════
  为什么必须有这个文件
═════════════════════════════════════════════════════════════
  2026-10-05 实测：CI 连红 4 次，根因是 ``tests/test_verifiable_identity.py`` 与
  ``tests/test_intent_mandate.py`` 的 setUp 把 ``os.path.exists`` 写在了 ``open()``
  **之后**。CI 里 ``api/data/*.json`` 一个都没有（``.gitignore`` line 80 全盖住、
  干净 checkout 也不带种子数据），于是 setUp 直接抛 FileNotFoundError，27 个 L1
  用例集体 error；而本地 ``api/data`` 有种子数据、那条分支永远走不到 ——
  **本地全绿、CI 连红**。

  光修 setUp 只是治病；这里加一条**机制级门禁**：把身份侧的文件路径全部重定向到
  一个**空目录**（等价干净 checkout），跑一遍真实的「发凭据 → 注册 → 签 VC →
  验 VC → 除销」闭环。任何一步因为「文件不存在」而崩，这里立刻红。

  这不是又一个冗余用例：它守的是一类**只在干净环境才会暴露**的失败，而 CI 是
  唯一稳定提供干净环境的跑法 —— 没有它，下一次同类 bug 又有 4 次机会藏起来。
"""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest


class TestCleanCheckoutIdentity(unittest.TestCase):
    """身份闭环必须在「一个字节种子数据都没有」的目录里跑得通。"""

    def setUp(self):
        from eco import crypto_sign
        from eco import identity
        from eco import intent_mandate as im
        from eco import verifiable_identity as vi

        self._mods = (crypto_sign, identity, im, vi)
        self._orig = {
            "KEY_FILE": vi.KEY_FILE,
            "LEGACY_KEY_FILE": vi.LEGACY_KEY_FILE,
            "AGENTS_FILE": identity.AGENTS_FILE,
            "TOKEN_FILE": getattr(identity, "TOKEN_FILE", None),
            "MANDATE_FILE": im.MANDATE_FILE,
        }
        self._tmp = tempfile.mkdtemp(prefix="clean-checkout-")
        vi.KEY_FILE = os.path.join(self._tmp, "signing_keys.json")
        vi.LEGACY_KEY_FILE = os.path.join(self._tmp, "nobody-legacy.json")
        identity.AGENTS_FILE = os.path.join(self._tmp, "agents.json")
        if self._orig["TOKEN_FILE"]:
            identity.TOKEN_FILE = os.path.join(self._tmp, "registration_tokens.json")
        im.MANDATE_FILE = os.path.join(self._tmp, "intent_mandates.json")
        self._tmp = self._tmp

    def tearDown(self):
        from eco import identity
        from eco import intent_mandate as im
        from eco import verifiable_identity as vi

        vi.KEY_FILE = self._orig["KEY_FILE"]
        vi.LEGACY_KEY_FILE = self._orig["LEGACY_KEY_FILE"]
        identity.AGENTS_FILE = self._orig["AGENTS_FILE"]
        if self._orig["TOKEN_FILE"]:
            identity.TOKEN_FILE = self._orig["TOKEN_FILE"]
        im.MANDATE_FILE = self._orig["MANDATE_FILE"]
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_identity_closed_loop_without_any_seed_file(self):
        """空目录 + 无种子：注册 → 签 VC → 离线凭 JWKS 验 → 除销，全程不能因为
        「文件不存在」崩掉 —— 这正是 CI 干净 checkout 的真实处境。"""
        from eco import identity
        from eco import verifiable_identity as vi

        tk = identity.RegistrationTokenAuthority().issue("clean-checkout-owner")
        agent = identity.AgentRegistration().register(
            name="clean-checkout-agent", owner="clean-checkout-owner",
            registration_token=tk["token"])
        did = agent["did"]
        self.assertTrue(did, "干净 checkout 下注册没拿到 DID")

        # 干净环境下必须先有一条可用密钥环：这是生产冷启动的真实状态
        ring = vi.SigningKeyRing()
        ring.load()
        if not ring.is_ed25519_ready():
            ring.rotate_to_ed25519()

        cred = ring.issue_credential(did, ttl=60)
        self.assertTrue(cred.get("token"), "干净 checkout 下签不出凭证")

        jw = ring.jwks()
        self.assertTrue(jw.get("ready"), f"干净 checkout 下 JWKS 不可发布：{jw.get('reason')}")
        self.assertEqual(len(jw.get("keys") or []), 1)

        ok = vi.verify(cred["token"], check_revocation=True)
        self.assertTrue(ok.get("verified") or ok.get("valid") or ok is True,
                        f"干净 checkout 下验不过自己签的凭证：{ok}")

        # 产物必须落在临时目录：一旦重定向没生效，闭环会写进仓库 api/data，
        # 把运行目录当成测试 playground —— 那个状态正是 2026-10-05 假绿的温床。
        # 注意这里**不能**反过来断言「仓库 api/data 里没文件」：本地与生产的
        # api/data 本来就有运行时数据，那是正常的，判红只会让门禁空转。
        self.assertEqual(os.path.dirname(identity.AGENTS_FILE), self._tmp,
                         "AGENTS_FILE 没指向临时目录 —— 闭环数据会写进仓库 api/data")
        self.assertTrue(os.path.exists(identity.AGENTS_FILE),
                        "身份闭环没产生注册表数据（重定向后应落在临时目录）")
        self.assertTrue(os.path.exists(vi.KEY_FILE),
                        "签名密钥环没落在临时目录，会污染仓库 api/data")


if __name__ == "__main__":
    unittest.main()
