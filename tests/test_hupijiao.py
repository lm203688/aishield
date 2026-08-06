"""
tests/test_hupijiao.py — 虎皮椒人民币支付通道测试

全部离线：不发任何网络请求，用构造凭证验证协议与安全不变量。
重点是支付侧四类经典攻击面：伪造商户、伪造签名、篡改金额、重放回调。
"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eco import credentials  # noqa: E402
from eco import hupijiao as hp  # noqa: E402

TEST_APPID = "999900001111"
TEST_SECRET = "unit_test_secret_do_not_use"


def _gw(**kw):
    """构造一个不依赖本地 .secrets.json 的测试网关。"""
    params = dict(appid=TEST_APPID, app_secret=TEST_SECRET,
                  api_base="https://api.xunhupay.com",
                  notify_url="https://example.test/notify")
    params.update(kw)
    return hp.HupijiaoGateway(**params)


def _signed(params, secret=TEST_SECRET):
    p = dict(params)
    p["hash"] = hp.generate_hash(p, secret)
    return p


class TestSignature(unittest.TestCase):
    def test_hash_is_deterministic(self):
        p = {"appid": "a", "trade_order_id": "t1", "total_fee": "1.00"}
        self.assertEqual(hp.generate_hash(p, "s"), hp.generate_hash(p, "s"))

    def test_hash_independent_of_insertion_order(self):
        a = {"b": "2", "a": "1", "c": "3"}
        b = {"c": "3", "a": "1", "b": "2"}
        self.assertEqual(hp.generate_hash(a, "s"), hp.generate_hash(b, "s"))

    def test_empty_values_and_hash_key_excluded(self):
        base = {"a": "1", "b": "2"}
        withextra = {"a": "1", "b": "2", "c": "", "d": None, "hash": "deadbeef"}
        self.assertEqual(hp.generate_hash(base, "s"), hp.generate_hash(withextra, "s"))

    def test_secret_actually_affects_hash(self):
        p = {"a": "1"}
        self.assertNotEqual(hp.generate_hash(p, "s1"), hp.generate_hash(p, "s2"))

    def test_verify_hash_roundtrip(self):
        p = _signed({"appid": TEST_APPID, "total_fee": "9.90"})
        self.assertTrue(hp.verify_hash(p, TEST_SECRET))

    def test_verify_hash_rejects_tampered_and_missing(self):
        p = _signed({"appid": TEST_APPID, "total_fee": "9.90"})
        p["total_fee"] = "0.01"                      # 改金额
        self.assertFalse(hp.verify_hash(p, TEST_SECRET))
        self.assertFalse(hp.verify_hash({"a": "1"}, TEST_SECRET))   # 无 hash
        self.assertFalse(hp.verify_hash(p, ""))                     # 无密钥


class TestNotifySecurity(unittest.TestCase):
    """回调是唯一"钱已到账"的可信来源，四道校验逐条验证。"""

    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="aishield_hpj_")
        self._orig_file = hp.ORDERS_FILE
        hp.ORDERS_FILE = os.path.join(self._tmp, "orders.json")
        self.gw = _gw()
        self.base = {
            "appid": TEST_APPID,
            "trade_order_id": "order_abc",
            "total_fee": "19.00",
            "transaction_id": "tx_1",
            "open_order_id": "20300001",
            "status": "OD",
            "time": "1786000000",
            "nonce_str": "abcdef",
        }

    def tearDown(self):
        hp.ORDERS_FILE = self._orig_file

    def _seed_local_order(self, total_fee="19.00", status="pending_payment"):
        hp._save_orders({"orders": {"order_abc": {
            "trade_order_id": "order_abc", "total_fee": total_fee,
            "amount_cny": float(total_fee), "status": status,
        }}})

    def test_valid_notify_passes(self):
        self._seed_local_order()
        ok, reason = self.gw.verify_notify(_signed(self.base))
        self.assertTrue(ok, reason)
        self.assertEqual(reason, "ok")

    def test_rejects_foreign_appid(self):
        """他人用自己的商户号伪造回调 —— 必须被 appid 归属检查拦下。"""
        p = dict(self.base, appid="111100002222")
        ok, reason = self.gw.verify_notify(_signed(p))
        self.assertFalse(ok)
        self.assertEqual(reason, "appid_mismatch")

    def test_rejects_bad_signature(self):
        p = dict(self.base, hash="0" * 32)
        ok, reason = self.gw.verify_notify(p)
        self.assertFalse(ok)
        self.assertEqual(reason, "bad_signature")

    def test_rejects_unpaid_status(self):
        p = _signed(dict(self.base, status="WP"))
        ok, reason = self.gw.verify_notify(p)
        self.assertFalse(ok)
        self.assertIn("not_paid_status", reason)

    def test_rejects_amount_tampering(self):
        """签名合法但金额与本地下单不符（如 0.01 买 19 元认证）——必须拒。"""
        self._seed_local_order(total_fee="19.00")
        p = _signed(dict(self.base, total_fee="0.01"))
        ok, reason = self.gw.verify_notify(p)
        self.assertFalse(ok)
        self.assertEqual(reason, "amount_mismatch")

    def test_rejects_replay_after_settlement(self):
        self._seed_local_order(status="paid")
        ok, reason = self.gw.verify_notify(_signed(self.base))
        self.assertFalse(ok)
        self.assertEqual(reason, "already_settled")

    def test_rejects_when_gateway_unconfigured(self):
        # 隔离真实 .secrets.json：未配置时绝不能"放行"，否则任何人都能伪造到账
        with mock.patch.object(credentials, "get", return_value=""):
            gw = hp.HupijiaoGateway(appid="", app_secret="")
        ok, reason = gw.verify_notify(_signed(self.base))
        self.assertFalse(ok)
        self.assertEqual(reason, "gateway_not_configured")

    def test_rejects_empty_payload(self):
        ok, reason = self.gw.verify_notify({})
        self.assertFalse(ok)
        self.assertEqual(reason, "empty_payload")

    def test_handle_notify_is_idempotent(self):
        self._seed_local_order()
        from urllib.parse import urlencode
        body = urlencode(_signed(self.base))
        first = self.gw.handle_notify(body)
        self.assertTrue(first["ok"])
        self.assertEqual(first["order"]["status"], "paid")
        second = self.gw.handle_notify(body)          # 平台重推
        self.assertFalse(second["ok"])
        self.assertEqual(second["reason"], "already_settled")

    def test_parse_notify_handles_form_body(self):
        from urllib.parse import urlencode
        parsed = hp.HupijiaoGateway.parse_notify(urlencode(self.base))
        self.assertEqual(parsed["trade_order_id"], "order_abc")
        self.assertEqual(parsed["total_fee"], "19.00")

    def test_notify_secret_is_never_echoed(self):
        self._seed_local_order()
        from urllib.parse import urlencode
        res = self.gw.handle_notify(urlencode(_signed(self.base)))
        self.assertNotIn(TEST_SECRET, json.dumps(res, ensure_ascii=False))


class TestSSRFGuard(unittest.TestCase):
    def test_official_hosts_allowed(self):
        for base in ("https://api.xunhupay.com", "https://admin.xunhupay.com",
                     "https://anything.xunhupay.com"):
            self.assertTrue(hp.HupijiaoGateway._host_allowed(base), base)

    def test_foreign_hosts_blocked(self):
        for base in ("https://evil.com", "http://127.0.0.1:8080",
                     "http://169.254.169.254", "https://xunhupay.com.evil.net", ""):
            self.assertFalse(hp.HupijiaoGateway._host_allowed(base), base)

    def test_post_refuses_disallowed_host(self):
        gw = _gw(api_base="https://evil.com")
        data, err = gw._post("/payment/do.html", {"a": 1})
        self.assertIsNone(data)
        self.assertIn("白名单", err)


class TestCreatePaymentValidation(unittest.TestCase):
    """参数校验必须在发网络请求之前完成（下面用例都不应触网）。"""

    def test_unconfigured_degrades_gracefully(self):
        # 隔离真实 .secrets.json：未配置时优雅降级而非触网失败
        with mock.patch.object(credentials, "get", return_value=""):
            res = hp.HupijiaoGateway(appid="", app_secret="").create_payment(1.0)
        self.assertFalse(res["success"])
        self.assertIn("未配置", res["error"])

    def test_rejects_non_cny(self):
        res = _gw().create_payment(1.0, currency="USD")
        self.assertFalse(res["success"])

    def test_rejects_unknown_payment_method(self):
        res = _gw().create_payment(1.0, payment="paypal")
        self.assertFalse(res["success"])

    def test_rejects_bad_amounts(self):
        for bad in (0, -1, "abc", None):
            res = _gw().create_payment(bad)
            self.assertFalse(res["success"], bad)

    def test_query_requires_an_identifier(self):
        res = _gw().query_order()
        self.assertFalse(res["success"])


class TestHelpers(unittest.TestCase):
    def test_extract_open_order_id(self):
        url = "https://api.xunhupay.com/payments/wechat/index?id=20305381080&appid=x"
        self.assertEqual(hp._extract_open_order_id(url), "20305381080")
        self.assertEqual(hp._extract_open_order_id(""), "")
        self.assertEqual(hp._extract_open_order_id("not a url"), "")

    def test_amounts_equal_tolerance(self):
        self.assertTrue(hp._amounts_equal("19.00", 19))
        self.assertTrue(hp._amounts_equal(0.1 + 0.2, 0.3))
        self.assertFalse(hp._amounts_equal("19.00", "0.01"))
        self.assertFalse(hp._amounts_equal(None, "1.00"))
        self.assertFalse(hp._amounts_equal("abc", "1.00"))

    def test_status_never_leaks_plaintext_secret(self):
        st = _gw().status()
        blob = json.dumps(st, ensure_ascii=False)
        self.assertNotIn(TEST_SECRET, blob)
        self.assertNotIn(TEST_APPID, blob)
        self.assertTrue(st["configured"])
        self.assertTrue(st["api_base_allowed"])


class TestCredentials(unittest.TestCase):
    def test_env_takes_precedence(self):
        key = "AISHIELD_UNIT_TEST_CRED"
        os.environ[key] = "from_env"
        try:
            self.assertEqual(credentials.get(key), "from_env")
        finally:
            os.environ.pop(key, None)

    def test_missing_returns_default(self):
        self.assertEqual(credentials.get("AISHIELD_DEFINITELY_MISSING_KEY", "fallback"),
                         "fallback")

    def test_mask_hides_middle(self):
        self.assertEqual(credentials.mask("abcdefghij", keep=2), "ab******ij")
        self.assertEqual(credentials.mask("abc"), "***")
        self.assertEqual(credentials.mask(""), "")

    def test_fingerprint_is_stable_and_short(self):
        fp = credentials.fingerprint("secret")
        self.assertEqual(len(fp), 8)
        self.assertEqual(fp, credentials.fingerprint("secret"))
        self.assertNotEqual(fp, credentials.fingerprint("secret2"))

    def test_describe_never_returns_plaintext(self):
        key = "AISHIELD_UNIT_TEST_CRED2"
        os.environ[key] = "supersecretvalue"
        try:
            blob = json.dumps(credentials.describe(key))
            self.assertNotIn("supersecretvalue", blob)
            self.assertIn("fingerprint", blob)
        finally:
            os.environ.pop(key, None)


class TestCnyPricing(unittest.TestCase):
    def test_cny_price_tiers_present_and_ordered(self):
        from eco.monetization import PRICE_CNY_BY_LEVEL as p
        self.assertGreater(p["gold"], p["silver"])
        self.assertGreater(p["silver"], p["bronze"])
        self.assertEqual(p["none"], 0.0)

    def test_low_score_cannot_buy_certification(self):
        """付费不能绕过评分门槛——否则认证就成了卖徽章。"""
        from eco.monetization import request_cert_payment_cny
        res = request_cert_payment_cny("https://example.test/tool",
                                       {"overall_score": 20})
        self.assertFalse(res["success"])
        self.assertEqual(res.get("badge_level"), "none")


if __name__ == "__main__":
    unittest.main(verbosity=2)
