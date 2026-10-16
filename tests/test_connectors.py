"""
tests/test_connectors.py — 海外平台接入（Muse + Grok Bot）测试

覆盖：
  - connectors/base.py — OAuth 通用 + token 存储 + proxy 支持
  - connectors/muse/muse.py — Muse Agent 全流程
  - connectors/grok_bot/grok.py — Grok Bot 全流程（PAT + OAuth）
  - connectors/dispatcher.py — 平台分发

大陆环境网络不可达 → 所有真实 API 调用通过 http_post_mock 注入 mock 验证治理逻辑。
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_BASE,):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_TMP = tempfile.mkdtemp(prefix="aishield_conn_test_")
os.environ["AISHIELD_DATA_DIR"] = _TMP
os.environ["AISHIELD_MUSE_STORE"] = str(Path(_TMP) / "muse_state.json")
os.environ["AISHIELD_MUSE_SECRET"] = str(Path(_TMP) / "muse_secret.txt")
os.environ["AISHIELD_MUSE_SECRET_KEY"] = "muse-test-secret"
os.environ["AISHIELD_GROK_STORE"] = str(Path(_TMP) / "grok_state.json")
os.environ["AISHIELD_GROK_SECRET"] = str(Path(_TMP) / "grok_secret.txt")
os.environ["AISHIELD_GROK_SECRET_KEY"] = "xai-test-secret"

import connectors.base as base
import connectors.dispatcher as dispatcher
import connectors.grok_bot.grok as grok
import connectors.muse.muse as muse
import eco.personal_agent as pa


def _iso(days_from_now=0):
    return (datetime.now(timezone.utc) + timedelta(days=days_from_now)).isoformat()


def _clean_all():
    if pa.STORE_FILE:
        Path(pa.STORE_FILE).unlink(missing_ok=True)
    for key in ("AISHIELD_MUSE_STORE", "AISHIELD_MUSE_SECRET", "AISHIELD_GROK_STORE", "AISHIELD_GROK_SECRET"):
        p = os.environ.get(key)
        if p:
            Path(p).unlink(missing_ok=True)


# ============================================================
# base.py 测试
# ============================================================


class TestBaseOAuth(unittest.TestCase):
    def setUp(self):
        _clean_all()

    def test_build_authorize_url(self):
        r = base.build_authorize_url(
            authorize_endpoint="https://auth.example.com/oauth",
            client_id="cid_123",
            redirect_uri="https://example.com/cb",
            scopes=["read", "write"],
        )
        self.assertTrue(r["ok"])
        self.assertIn("client_id=cid_123", r["authorize_url"])
        self.assertIn("response_type=code", r["authorize_url"])
        self.assertIn("redirect_uri=", r["authorize_url"])
        self.assertIn("scope=read", r["authorize_url"])

    def test_exchange_code_for_token_success(self):
        def mock(url, payload):
            self.assertEqual(payload["grant_type"], "authorization_code")
            self.assertEqual(payload["code"], "auth_code_x")
            return 200, {"access_token": "at_1", "refresh_token": "rt_1",
                         "expires_in": 7200, "refresh_expires_in": 2592000}
        r = base.exchange_code_for_token(
            "https://auth.example.com/token", "auth_code_x", "cid", "secret", "https://cb",
            http_post_mock=mock,
        )
        self.assertTrue(r["ok"])
        self.assertEqual(r["tokens"]["access_token"], "at_1")
        self.assertGreater(r["tokens"]["expires_at"], int(time.time()))

    def test_exchange_code_requires_all_params(self):
        r = base.exchange_code_for_token(
            "https://t", "", "cid", "secret", "https://cb",
        )
        self.assertFalse(r["ok"])
        self.assertIn("required", r["error"])

    def test_store_and_get_access_token(self):
        tokens = {
            "access_token": "at_x", "refresh_token": "rt_x",
            "expires_at": int(time.time()) + 3600,
            "refresh_expires_at": int(time.time()) + 2592000,
            "scope": "read",
            "fetched_at": _iso(),
        }
        r = base.store_access_token("test_plat", "agent_1", "cid", tokens)
        self.assertTrue(r["ok"])
        tk = base.get_access_token("test_plat", "agent_1")
        self.assertTrue(tk["ok"])
        self.assertEqual(tk["access_token"], "at_x")

    def test_get_access_token_fail_closed_when_no_entry(self):
        tk = base.get_access_token("test_plat", "agent_missing")
        self.assertFalse(tk["ok"])
        self.assertIn("no token", tk["error"])

    def test_get_access_token_triggers_refresh(self):
        tokens = {
            "access_token": "at_old", "refresh_token": "rt_1",
            "expires_at": int(time.time()) + 30,  # 30s 内过期
            "refresh_expires_at": int(time.time()) + 2592000,
            "scope": "", "fetched_at": _iso(),
        }
        base.register_token_endpoint("test_plat", "https://t/token")
        # 存 client_secret
        sp = base.secret_path("test_plat")
        sp.parent.mkdir(parents=True, exist_ok=True)
        sp.write_text("test-secret", encoding="utf-8")
        base.store_access_token("test_plat", "agent_1", "cid", tokens)

        def mock(url, payload):
            self.assertEqual(payload["grant_type"], "refresh_token")
            return 200, {"access_token": "at_new", "refresh_token": "rt_new",
                         "expires_in": 7200}
        tk = base.get_access_token("test_plat", "agent_1", http_post_mock=mock)
        self.assertTrue(tk["ok"])
        self.assertEqual(tk["access_token"], "at_new")

    def test_get_access_token_fail_closed_refresh_fails(self):
        tokens = {
            "access_token": "at_old", "refresh_token": "rt_bad",
            "expires_at": int(time.time()) - 100,
            "refresh_expires_at": int(time.time()) + 2592000,
            "scope": "", "fetched_at": _iso(),
        }
        base.register_token_endpoint("test_plat2", "https://t/token")
        sp = base.secret_path("test_plat2")
        sp.parent.mkdir(parents=True, exist_ok=True)
        sp.write_text("test-secret", encoding="utf-8")
        base.store_access_token("test_plat2", "agent_1", "cid", tokens)

        def mock(url, payload):
            return 400, {"error": "invalid refresh token"}

        tk = base.get_access_token("test_plat2", "agent_1", http_post_mock=mock)
        self.assertFalse(tk["ok"])
        self.assertEqual(tk.get("action"), "re_authorize")


class TestBaseSensitive(unittest.TestCase):
    def setUp(self):
        _clean_all()

    def test_detect_sensitive_triggers_chinese(self):
        self.assertIn("转账", base.detect_sensitive_triggers("帮我转账 ¥100"))
        self.assertIn("群发", base.detect_sensitive_triggers("这份报告群发到全网"))

    def test_detect_sensitive_triggers_english(self):
        self.assertIn("delete all", base.detect_sensitive_triggers("please delete all files"))
        self.assertIn("withdraw", base.detect_sensitive_triggers("withdraw $50 from card"))

    def test_detect_sensitive_empty(self):
        self.assertEqual(base.detect_sensitive_triggers(None), [])
        self.assertEqual(base.detect_sensitive_triggers(""), [])

    def test_extract_amount_chinese(self):
        self.assertEqual(base.extract_amount("¥500"), 500)
        self.assertEqual(base.extract_amount("花 200元 买"), 200)

    def test_extract_amount_usd(self):
        self.assertEqual(base.extract_amount("$30 USD"), 30)

    def test_extract_amount_multiple_takes_max(self):
        self.assertEqual(base.extract_amount("¥50 + ¥500"), 500)

    def test_prompt_fingerprint_stable(self):
        fp1 = base.prompt_fingerprint("hello world")
        fp2 = base.prompt_fingerprint("hello world")
        self.assertEqual(fp1, fp2)
        self.assertNotEqual(fp1, base.prompt_fingerprint("different"))


# ============================================================
# Muse 集成测试
# ============================================================


class TestMuseOAuth(unittest.TestCase):
    def setUp(self):
        _clean_all()

    def test_build_authorize_url_muse(self):
        r = muse.build_authorize_url_muse(client_id="muse_app_123")
        self.assertTrue(r["ok"])
        self.assertIn("auth.muse.ai", r["authorize_url"])
        self.assertIn("client_id=muse_app_123", r["authorize_url"])

    def test_exchange_muse_code_success(self):
        def mock(url, payload):
            self.assertIn("auth.muse.ai", url)
            self.assertEqual(payload["grant_type"], "authorization_code")
            return 200, {"access_token": "at_muse", "refresh_token": "rt_muse",
                         "expires_in": 7200, "scope": "agent:chat"}
        r = muse.exchange_muse_code(code="code_x", client_id="muse_app", http_post_mock=mock)
        self.assertTrue(r["ok"])
        self.assertEqual(r["tokens"]["access_token"], "at_muse")

    def test_exchange_muse_requires_client_id(self):
        r = muse.exchange_muse_code(code="c", client_id="")
        self.assertFalse(r["ok"])


class TestMuseAgent(unittest.TestCase):
    def setUp(self):
        _clean_all()

    def _setup_ok(self, agent_id="agent_muse_1"):
        tokens = {
            "access_token": "at_muse_valid",
            "refresh_token": "rt_muse_valid",
            "expires_at": int(time.time()) + 3600,
            "refresh_expires_at": int(time.time()) + 2592000,
            "scope": "agent:chat",
            "fetched_at": _iso(),
        }
        r = muse.register_muse_agent(
            user_id="u_alice",
            agent_name="Alice's Muse",
            platform_agent_id="muse_agent_abc",
            client_id="muse_app_1",
            tokens=tokens,
        )
        self.assertTrue(r["ok"])
        self.assertEqual(r["platform"], "meta-muse")
        return r

    def test_register_muse_agent_persists_platform_meta(self):
        r = self._setup_ok()
        insts = pa.list_instances_by_platform(user_id="u_alice", platform_id="meta-muse")
        self.assertEqual(len(insts), 1)
        self.assertEqual(insts[0]["instance_id"], r["agent_instance_id"])

    def test_register_requires_all_fields(self):
        r = muse.register_muse_agent(user_id="", agent_name="X", platform_agent_id="Y", client_id="Z")
        self.assertFalse(r["ok"])

    def test_run_chat_success_allows_and_records(self):
        r_reg = self._setup_ok()
        calls = []

        def mock(url, payload):
            calls.append((url, payload))
            self.assertIn("/agents/", url)
            self.assertEqual(payload["content"], "总结一下今天的技术动态")
            return 200, {"data": {"id": "msg_1", "session_id": "sess_1", "content": "ok"}}

        r = muse.run_agent_action(
            agent_instance_id=r_reg["agent_instance_id"],
            user_id="u_alice",
            prompt="总结一下今天的技术动态",
            action="chat",
            bot_id="muse_agent_abc",
            http_post_mock=mock,
        )
        self.assertTrue(r["ok"])
        self.assertEqual(r["verdict"], "allow")
        self.assertEqual(r["message_id"], "msg_1")
        self.assertTrue(r["recorded_action"].get("success") or r["recorded_action"].get("ok"))
        self.assertEqual(len(calls), 1)

    def test_run_task_budget_denied(self):
        r_reg = self._setup_ok()
        pa.set_budget_policy(
            user_id="u_alice", currency="CNY",
            per_tx=10, daily=10, weekly=10, monthly=10,
        )

        def mock(url, payload):
            raise AssertionError("should not call API when denied")

        r = muse.run_agent_action(
            agent_instance_id=r_reg["agent_instance_id"],
            user_id="u_alice",
            prompt="帮我花 ¥500 买服务器",
            action="run_task",
            bot_id="muse_agent_abc",
            http_post_mock=mock,
        )
        self.assertFalse(r["ok"])
        self.assertEqual(r["verdict"]["verdict"], "denied")

    def test_run_chat_sensitive_block_without_override(self):
        r_reg = self._setup_ok()

        def mock(url, payload):
            raise AssertionError("should not call API when block")

        r = muse.run_agent_action(
            agent_instance_id=r_reg["agent_instance_id"],
            user_id="u_alice",
            prompt="帮我把这份报告群发到全网",
            action="chat",
            bot_id="muse_agent_abc",
            http_post_mock=mock,
        )
        self.assertFalse(r["ok"])
        self.assertEqual(r["verdict"]["verdict"], "block")
        self.assertIn("群发", r["verdict"].get("muse_sensitive_triggers", []))

    def test_run_chat_sensitive_block_with_override(self):
        r_reg = self._setup_ok()
        r = muse.run_agent_action(
            agent_instance_id=r_reg["agent_instance_id"],
            user_id="u_alice",
            prompt="帮我把这份报告群发到全网",
            action="chat",
            bot_id="muse_agent_abc",
            override=True,
            http_post_mock=lambda u, p: (200, {"data": {
                "id": "msg_99", "session_id": "sess_99", "content": "ok"}}),
        )
        self.assertTrue(r["ok"])
        self.assertTrue(r["override_used"])

    def test_run_chat_no_token(self):
        r = muse.run_agent_action(
            agent_instance_id="agent_missing",
            user_id="u_alice",
            prompt="hello",
            action="chat",
        )
        self.assertFalse(r["ok"])
        self.assertEqual(r.get("action"), "re_authorize")

    def test_run_chat_unknown_action(self):
        reg = self._setup_ok()
        r = muse.run_agent_action(
            agent_instance_id=reg["agent_instance_id"],
            user_id="u_alice",
            prompt="hello",
            action="unknown_op",
        )
        self.assertFalse(r["ok"])
        self.assertIn("unknown action", r["error"])

    def test_amount_detection_usd(self):
        pf = muse.preflight(
            agent_instance_id="agent_x",
            user_id="u_alice",
            prompt="spend $30 on API",
            currency="USD",
        )
        self.assertTrue(pf["ok"])
        self.assertEqual(pf["amount_detected"], 30)

    def test_user_muse_state_after_register(self):
        self._setup_ok()
        r = muse.user_muse_state("u_alice")
        self.assertTrue(r["ok"])
        self.assertEqual(r["platform"], "meta-muse")
        self.assertEqual(len(r["agents"]), 1)
        self.assertEqual(len(r["tokens"]), 1)
        self.assertEqual(r["platform_reachable"], False)

    def test_user_muse_state_reports_proxy_env(self):
        r = muse.user_muse_state("u_alice")
        self.assertIn("proxy_env", r)

    def test_self_check(self):
        r = muse.self_check()
        self.assertIn("ok", r)
        self.assertIn("checks", r)
        self.assertIn("muse_reachable", r["checks"])
        self.assertIn("client_secret_configured", r["checks"])


# ============================================================
# Grok Bot 集成测试
# ============================================================


class TestGrokAuth(unittest.TestCase):
    def setUp(self):
        _clean_all()

    def test_store_pat_and_get(self):
        r = grok.store_pat("agent_grok_1", "xai-pat-xxx")
        self.assertTrue(r["ok"])
        tk = grok.get_pat_or_token("agent_grok_1")
        self.assertTrue(tk["ok"])
        self.assertEqual(tk["access_token"], "xai-pat-xxx")
        self.assertEqual(tk["auth_type"], "pat")

    def test_pat_no_refresh_needed(self):
        grok.store_pat("agent_grok_2", "xai-pat-yyy")
        # PAT 不过期 → get_pat_or_token 直接返回
        tk = grok.get_pat_or_token("agent_grok_2")
        self.assertTrue(tk["ok"])

    def test_get_no_credentials(self):
        tk = grok.get_pat_or_token("agent_missing")
        self.assertFalse(tk["ok"])

    def test_build_authorize_url_xai(self):
        r = grok.build_authorize_url_xai(client_id="xai_app")
        self.assertTrue(r["ok"])
        self.assertIn("console.x.ai", r["authorize_url"])

    def test_exchange_xai_code_success(self):
        def mock(url, payload):
            self.assertIn("console.x.ai", url)
            return 200, {"access_token": "at_xai", "refresh_token": "rt_xai",
                         "expires_in": 7200}
        r = grok.exchange_xai_code(code="code_x", client_id="xai_app", http_post_mock=mock)
        self.assertTrue(r["ok"])
        self.assertEqual(r["tokens"]["access_token"], "at_xai")


class TestGrokAgent(unittest.TestCase):
    def setUp(self):
        _clean_all()

    def _setup_ok_pat(self, agent_id="agent_grok_1"):
        r = grok.register_grok_agent(
            user_id="u_alice",
            agent_name="Alice's Grok",
            platform_agent_id="grok_bot_x",
            auth="pat",
            credentials={"pat": "***"},
        )
        self.assertTrue(r["ok"])
        return r

    def test_register_grok_pat(self):
        r = self._setup_ok_pat()
        self.assertEqual(r["platform"], "xai-grok-bot")
        insts = pa.list_instances_by_platform(user_id="u_alice", platform_id="xai-grok-bot")
        self.assertEqual(len(insts), 1)

    def test_register_requires_valid_auth(self):
        r = grok.register_grok_agent(
            user_id="u_alice", agent_name="X", platform_agent_id="Y",
            auth="invalid",
        )
        self.assertFalse(r["ok"])
        self.assertIn("auth", r["error"])

    def test_run_chat_openai_compatible(self):
        r_reg = self._setup_ok_pat()
        calls = []

        def mock(url, payload):
            calls.append((url, payload))
            self.assertIn("api.x.ai/v1/chat/completions", url)
            self.assertEqual(payload["model"], "grok-3")
            self.assertEqual(payload["messages"][0]["content"], "hello grok")
            return 200, {
                "id": "cmpl_123",
                "choices": [{"message": {"content": "hi from grok"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
            }

        r = grok.run_agent_action(
            agent_instance_id=r_reg["agent_instance_id"],
            user_id="u_alice",
            prompt="hello grok",
            action="chat",
            model="grok-3",
            http_post_mock=mock,
        )
        self.assertTrue(r["ok"])
        self.assertEqual(r["verdict"], "allow")
        self.assertEqual(r["completion_id"], "cmpl_123")
        self.assertEqual(r["answer"], "hi from grok")
        self.assertEqual(r["usage"]["prompt_tokens"], 5)

    def test_run_chat_default_currency_usd(self):
        pf = grok.preflight(
            agent_instance_id="x", user_id="u_alice",
            prompt="hello",
        )
        self.assertEqual(pf["currency"], "USD")

    def test_run_chat_sensitive_block(self):
        r_reg = self._setup_ok_pat()

        def mock(url, payload):
            raise AssertionError("should not call API")

        r = grok.run_agent_action(
            agent_instance_id=r_reg["agent_instance_id"],
            user_id="u_alice",
            prompt="withdraw $50 from my card",
            action="chat",
            http_post_mock=mock,
        )
        self.assertFalse(r["ok"])
        self.assertEqual(r["verdict"]["verdict"], "block")
        self.assertIn("withdraw", r["verdict"].get("grok_sensitive_triggers", []))

    def test_run_chat_budget_denied(self):
        r_reg = self._setup_ok_pat()
        pa.set_budget_policy(
            user_id="u_alice", currency="USD",
            per_tx=5, daily=5, weekly=5, monthly=5,
        )

        def mock(url, payload):
            raise AssertionError("should not call API")

        r = grok.run_agent_action(
            agent_instance_id=r_reg["agent_instance_id"],
            user_id="u_alice",
            prompt="spend $50 on API",
            action="chat",
            http_post_mock=mock,
        )
        self.assertFalse(r["ok"])
        self.assertEqual(r["verdict"]["verdict"], "denied")

    def test_run_chat_with_override_proceeds(self):
        r_reg = self._setup_ok_pat()
        r = grok.run_agent_action(
            agent_instance_id=r_reg["agent_instance_id"],
            user_id="u_alice",
            prompt="please delete all my files",
            action="chat",
            override=True,
            http_post_mock=lambda u, p: (200, {
                "id": "cmpl_ok",
                "choices": [{"message": {"content": "ok"}}],
                "usage": {},
            }),
        )
        self.assertTrue(r["ok"])
        self.assertTrue(r["override_used"])

    def test_run_chat_no_credentials(self):
        r = grok.run_agent_action(
            agent_instance_id="agent_missing",
            user_id="u_alice",
            prompt="hello",
        )
        self.assertFalse(r["ok"])
        self.assertEqual(r.get("action"), "re_authorize")

    def test_run_chat_api_failure(self):
        r_reg = self._setup_ok_pat()
        r = grok.run_agent_action(
            agent_instance_id=r_reg["agent_instance_id"],
            user_id="u_alice",
            prompt="hello",
            http_post_mock=lambda u, p: (401, {"error": "invalid api key"}),
        )
        self.assertFalse(r["ok"])
        self.assertIn("xai api failed", r["error"])

    def test_user_grok_state(self):
        self._setup_ok_pat()
        r = grok.user_grok_state("u_alice")
        self.assertTrue(r["ok"])
        self.assertEqual(r["platform"], "xai-grok-bot")
        self.assertEqual(len(r["agents"]), 1)
        self.assertEqual(len(r["tokens"]), 1)
        self.assertEqual(r["tokens"][0]["auth_type"], "pat")

    def test_self_check(self):
        r = grok.self_check()
        self.assertIn("xai_reachable", r["checks"])
        self.assertIn("client_secret_configured", r["checks"])


# ============================================================
# 分发器 + 集成流
# ============================================================


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        _clean_all()

    def test_supported_platforms(self):
        plats = dispatcher.supported_platforms()
        self.assertIn("meta-muse", plats)
        self.assertIn("xai-grok-bot", plats)

    def test_unknown_platform(self):
        r = dispatcher.register_agent(platform="unknown")
        self.assertFalse(r["ok"])
        self.assertIn("unsupported", r["error"])

    def test_full_flow_muse(self):
        # 1. 授权
        auth = muse.build_authorize_url_muse(client_id="muse_app")
        self.assertTrue(auth["ok"])
        # 2. 换 token
        tokens_r = muse.exchange_muse_code(
            code="code_1", client_id="muse_app",
            http_post_mock=lambda u, p: (200, {"access_token": "at_full", "refresh_token": "rt_full", "expires_in": 7200, "scope": "agent:chat"}),
        )
        self.assertTrue(tokens_r["ok"])
        # 3. 注册 agent
        reg = muse.register_muse_agent(
            user_id="u_alice", agent_name="Alice's Muse",
            platform_agent_id="muse_x", client_id="muse_app",
            tokens=tokens_r["tokens"],
        )
        self.assertTrue(reg["ok"])
        # 4. chat
        r = muse.run_agent_action(
            agent_instance_id=reg["agent_instance_id"],
            user_id="u_alice",
            prompt="帮我写封邮件",
            action="chat",
            bot_id="muse_x",
            http_post_mock=lambda u, p: (200, {"data": {
                "id": "m1", "session_id": "s1", "content": "ok"}}),
        )
        self.assertTrue(r["ok"])
        # 5. 状态
        st = muse.user_muse_state("u_alice")
        self.assertEqual(len(st["agents"]), 1)

    def test_full_flow_grok_pat(self):
        reg = grok.register_grok_agent(
            user_id="u_bob", agent_name="Bob's Grok",
            platform_agent_id="grok_bot_y",
            auth="pat", credentials={"pat": "***"},
        )
        self.assertTrue(reg["ok"])
        r = grok.run_agent_action(
            agent_instance_id=reg["agent_instance_id"],
            user_id="u_bob",
            prompt="hello grok",
            action="chat",
            http_post_mock=lambda u, p: (200, {
                "id": "c1", "choices": [{"message": {"content": "hi"}}], "usage": {},
            }),
        )
        self.assertTrue(r["ok"])
        st = grok.user_grok_state("u_bob")
        self.assertEqual(len(st["agents"]), 1)


class TestCrossPlatformNeutral(unittest.TestCase):
    """平台中立：同一 DID 在 Muse 和 Grok 共存。"""
    def setUp(self):
        _clean_all()

    def test_same_did_multi_platform(self):
        did_r = pa.create_personal_did(user_id="u_alice", display_name="Alice")
        self.assertTrue(did_r.get("did"))
        did = did_r["did"]

        r_muse = muse.register_muse_agent(
            user_id="u_alice", agent_name="Alice's Muse",
            platform_agent_id="muse_a", client_id="muse_app",
        )
        r_grok = grok.register_grok_agent(
            user_id="u_alice", agent_name="Alice's Grok",
            platform_agent_id="grok_a", auth="pat",
            credentials={"pat": "***"},
        )
        self.assertTrue(r_muse["ok"] and r_grok["ok"])

        # 同一用户两个实例，共享 parent_did
        st = pa.get_user_state("u_alice")
        self.assertEqual(len(st.get("agent_instances", [])), 2)
        self.assertEqual(st.get("did"), did)

        # 分别看
        muse_agents = pa.list_instances_by_platform(user_id="u_alice", platform_id="meta-muse")
        grok_agents = pa.list_instances_by_platform(user_id="u_alice", platform_id="xai-grok-bot")
        self.assertEqual(len(muse_agents), 1)
        self.assertEqual(len(grok_agents), 1)


class TestBudgetGovernance(unittest.TestCase):
    """预算治理对 Muse/Grok 都一致生效。"""
    def setUp(self):
        _clean_all()

    def test_muse_currency_cny_denied(self):
        pa.set_budget_policy(
            user_id="u_alice", currency="CNY",
            per_tx=50, daily=200, weekly=500, monthly=1000,
        )
        pf = muse.preflight(
            agent_instance_id="a", user_id="u_alice",
            prompt="帮我花 ¥500 买云",
        )
        self.assertEqual(pf["verdict"]["verdict"], "denied")

    def test_grok_currency_usd_denied(self):
        pa.set_budget_policy(
            user_id="u_alice", currency="USD",
            per_tx=5, daily=20, weekly=50, monthly=100,
        )
        pf = grok.preflight(
            agent_instance_id="a", user_id="u_alice",
            prompt="spend $50 on API",
            currency="USD",
        )
        self.assertEqual(pf["verdict"]["verdict"], "denied")


if __name__ == "__main__":
    unittest.main()
