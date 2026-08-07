"""
tests/test_governance.py — 支付上限 / 运行时治理 / 持续鉴证 三大模块测试

重点不是覆盖率数字，而是钉死安全不变量：
  - spend cap：超限必须拒绝、并发预留不能透支、已付款不能漏账、未知币种 fail-closed
  - governance：kill switch 优先级最高、fail-closed 默认拒绝、审计链篡改可检出
  - attestation：掉分必须吊销认证（rug-pull 兜底）、证据链完整、过期停止背书

所有用例使用临时数据文件，不触碰真实运行态账本。
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eco import spend_cap as sc              # noqa: E402
from eco import runtime_governance as rg     # noqa: E402
from eco import attestation as at            # noqa: E402


class _TempDataMixin:
    """把模块级数据文件重定向到临时目录，测试之间互不污染。"""

    def _isolate(self):
        self._tmp = tempfile.mkdtemp(prefix="aishield_test_")
        self.addCleanup(shutil.rmtree, self._tmp, True)
        return self._tmp


# ══════════════════════════════════════════
#  支付上限 spend cap
# ══════════════════════════════════════════

class TestSpendCap(_TempDataMixin, unittest.TestCase):

    def setUp(self):
        tmp = self._isolate()
        self._orig_file = sc.CAPS_FILE
        sc.CAPS_FILE = os.path.join(tmp, "spend_caps.json")
        self.addCleanup(setattr, sc, "CAPS_FILE", self._orig_file)
        os.environ["AISHIELD_SPEND_CAP"] = "1"
        self.svc = sc.SpendCapService()

    # ── 基本额度 ──
    def test_default_policy_present(self):
        pol = self.svc.get_policy("agent:a", "CNY")
        self.assertEqual(pol["limits"]["per_tx"], sc.DEFAULT_LIMITS["CNY"]["per_tx"])
        self.assertFalse(pol["custom"])

    def test_allows_within_limit(self):
        ok, reason, _ = self.svc.check("agent:a", 39.0, "CNY")
        self.assertTrue(ok)
        self.assertEqual(reason, "ok")

    def test_rejects_over_per_tx(self):
        ok, reason, detail = self.svc.check("agent:a", 99999, "CNY")
        self.assertFalse(ok)
        self.assertEqual(reason, "per_tx_exceeded")
        self.assertEqual(detail["limit"], sc.DEFAULT_LIMITS["CNY"]["per_tx"])

    def test_rejects_zero_and_negative(self):
        for bad in (0, -1, -0.01):
            ok, reason, _ = self.svc.check("agent:a", bad, "CNY")
            self.assertFalse(ok, f"{bad} 应被拒绝")
            self.assertEqual(reason, "invalid_amount")

    def test_rejects_non_numeric_amount(self):
        ok, reason, _ = self.svc.check("agent:a", "abc", "CNY")
        self.assertFalse(ok)
        self.assertEqual(reason, "invalid_amount")

    def test_unknown_currency_fails_closed(self):
        """未定义额度的币种必须拒绝——绝不能因为没配规则就放行。"""
        ok, reason, _ = self.svc.check("agent:a", 1.0, "JPY")
        self.assertFalse(ok)
        self.assertEqual(reason, "currency_not_allowed")

    def test_usdc_maps_to_usd_bucket(self):
        self.svc.set_policy("agent:a", "USD", per_tx=10)
        ok, reason, _ = self.svc.check("agent:a", 50, "USDC")
        self.assertFalse(ok)
        self.assertEqual(reason, "per_tx_exceeded")

    # ── 日/月累计 ──
    def test_daily_cap_accumulates(self):
        self.svc.set_policy("agent:b", "CNY", per_tx=100, daily=150, monthly=10000)
        r1 = self.svc.reserve("agent:b", 100, "CNY", order_id="o1")
        self.assertTrue(r1["success"])
        self.svc.commit(order_id="o1")
        ok, reason, _ = self.svc.check("agent:b", 100, "CNY")
        self.assertFalse(ok)
        self.assertEqual(reason, "daily_exceeded")

    def test_monthly_cap_enforced(self):
        self.svc.set_policy("agent:c", "CNY", per_tx=100, daily=100000, monthly=150)
        self.svc.reserve("agent:c", 100, "CNY", order_id="m1")
        self.svc.commit(order_id="m1")
        ok, reason, _ = self.svc.check("agent:c", 100, "CNY")
        self.assertFalse(ok)
        self.assertEqual(reason, "monthly_exceeded")

    # ── 预留 / 确认 / 释放 ──
    def test_reservation_blocks_double_spend(self):
        """未确认的预留也要占额度，否则并发下单可以透支。"""
        self.svc.set_policy("agent:d", "CNY", per_tx=100, daily=150, monthly=10000)
        self.svc.reserve("agent:d", 100, "CNY", order_id="r1")
        ok, reason, _ = self.svc.check("agent:d", 100, "CNY")
        self.assertFalse(ok)
        self.assertEqual(reason, "daily_exceeded")

    def test_release_returns_quota(self):
        self.svc.set_policy("agent:e", "CNY", per_tx=100, daily=150, monthly=10000)
        self.svc.reserve("agent:e", 100, "CNY", order_id="r2")
        self.svc.release(order_id="r2")
        ok, _, _ = self.svc.check("agent:e", 100, "CNY")
        self.assertTrue(ok, "释放后额度应恢复")

    def test_reserve_is_idempotent_per_order(self):
        a = self.svc.reserve("agent:f", 10, "CNY", order_id="same")
        b = self.svc.reserve("agent:f", 10, "CNY", order_id="same")
        self.assertTrue(b.get("idempotent"))
        self.assertEqual(a["reservation_id"], b["reservation_id"])
        self.assertEqual(self.svc.usage("agent:f", "CNY")["reserved"], 10.0)

    def test_commit_is_idempotent(self):
        self.svc.reserve("agent:g", 20, "CNY", order_id="c1")
        first = self.svc.commit(order_id="c1")
        second = self.svc.commit(order_id="c1")
        self.assertTrue(second.get("idempotent"))
        self.assertEqual(first["daily_total"], 20.0)
        self.assertEqual(self.svc.usage("agent:g", "CNY")["daily_spent"], 20.0)

    def test_late_commit_does_not_lose_the_charge(self):
        """预留过期后结算仍必须入账，否则限额可被"拖时间"绕过。"""
        res = self.svc.commit(order_id="late1", payer_id="agent:h",
                              amount=88.0, currency="CNY")
        self.assertTrue(res["success"])
        self.assertEqual(self.svc.usage("agent:h", "CNY")["daily_spent"], 88.0)

    def test_commit_without_reservation_or_params_fails(self):
        res = self.svc.commit(order_id="ghost")
        self.assertFalse(res["success"])

    def test_expired_reservation_is_pruned(self):
        self.svc.set_policy("agent:i", "CNY", per_tx=100, daily=100, monthly=10000)
        self.svc.reserve("agent:i", 100, "CNY", order_id="exp1")
        # 手动把预留改成已过期
        data = sc._load()
        for r in data["reservations"].values():
            r["expires_at"] = (datetime.now(sc.TZ) - timedelta(seconds=10)).isoformat()
        sc._save(data)
        ok, _, _ = self.svc.check("agent:i", 100, "CNY")
        self.assertTrue(ok, "过期预留应被回收，额度释放")

    def test_payers_are_isolated(self):
        self.svc.set_policy("agent:x", "CNY", per_tx=100, daily=100, monthly=10000)
        self.svc.reserve("agent:x", 100, "CNY", order_id="ix")
        self.svc.commit(order_id="ix")
        ok, _, _ = self.svc.check("agent:y", 100, "CNY")
        self.assertTrue(ok, "不同 payer 的额度必须互相独立")

    def test_set_policy_rejects_negative(self):
        res = self.svc.set_policy("agent:z", "CNY", per_tx=-1)
        self.assertFalse(res["success"])

    def test_set_policy_rejects_unknown_currency(self):
        res = self.svc.set_policy("agent:z", "XYZ", per_tx=10)
        self.assertFalse(res["success"])

    def test_anonymous_payer_normalized(self):
        self.assertEqual(self.svc.usage(None, "CNY")["payer_id"], "anonymous")
        self.assertEqual(self.svc.usage("  ", "CNY")["payer_id"], "anonymous")

    def test_disabled_switch_skips_enforcement(self):
        os.environ["AISHIELD_SPEND_CAP"] = "0"
        try:
            ok, reason, _ = self.svc.check("agent:a", 10 ** 9, "CNY")
            self.assertTrue(ok)
            self.assertEqual(reason, "cap_disabled")
        finally:
            os.environ["AISHIELD_SPEND_CAP"] = "1"

    def test_corrupt_ledger_does_not_crash(self):
        with open(sc.CAPS_FILE, "w", encoding="utf-8") as f:
            f.write("{ this is not json")
        ok, _, _ = self.svc.check("agent:a", 1.0, "CNY")
        self.assertTrue(isinstance(ok, bool))


# ══════════════════════════════════════════
#  运行时治理
# ══════════════════════════════════════════

class TestRuntimeGovernance(_TempDataMixin, unittest.TestCase):

    def setUp(self):
        tmp = self._isolate()
        self._orig_policy, self._orig_audit = rg.POLICY_FILE, rg.AUDIT_LOG
        rg.POLICY_FILE = os.path.join(tmp, "governance.json")
        rg.AUDIT_LOG = os.path.join(tmp, "governance_audit.jsonl")
        self.addCleanup(setattr, rg, "POLICY_FILE", self._orig_policy)
        self.addCleanup(setattr, rg, "AUDIT_LOG", self._orig_audit)
        self.g = rg.RuntimeGovernor()

    # ── 决策优先级 ──
    def test_default_allow_when_not_fail_closed(self):
        self.assertEqual(self.g.evaluate("s1", "read")["decision"], rg.DECISION_ALLOW)

    def test_fail_closed_denies_unknown(self):
        self.g.set_default_deny(True)
        res = self.g.evaluate("unknown-server", "any_tool")
        self.assertEqual(res["decision"], rg.DECISION_DENY)
        self.assertEqual(res["policy_hit"], "default_deny")

    def test_allowlist_is_tool_scoped(self):
        self.g.set_default_deny(True)
        self.g.allow_tool("s1", ["read_file"])
        self.assertTrue(self.g.evaluate("s1", "read_file")["allowed"])
        self.assertFalse(self.g.evaluate("s1", "exec_shell")["allowed"],
                         "未列入 allowlist 的工具必须拒绝")

    def test_deny_overrides_allow(self):
        self.g.allow_tool("s1", ["read_file"])
        self.g.deny_tool("s1", ["read_file"])
        res = self.g.evaluate("s1", "read_file")
        self.assertFalse(res["allowed"])
        self.assertEqual(res["policy_hit"], "deny_list")

    def test_kill_switch_beats_everything(self):
        self.g.allow_tool("s1", "*")
        self.g.kill("s1", reason="发现工具描述注入")
        res = self.g.evaluate("s1", "read_file")
        self.assertFalse(res["allowed"])
        self.assertEqual(res["policy_hit"], "kill_switch")

    def test_wildcard_allow(self):
        self.g.set_default_deny(True)
        self.g.allow_tool("s2", "*")
        self.assertTrue(self.g.evaluate("s2", "anything")["allowed"])

    def test_empty_server_denied(self):
        res = self.g.evaluate("", "tool")
        self.assertFalse(res["allowed"])
        self.assertEqual(res["policy_hit"], "invalid_request")

    def test_revive_restores_access(self):
        self.g.kill("s3")
        self.assertTrue(self.g.is_killed("s3"))
        self.assertTrue(self.g.revive("s3")["success"])
        self.assertFalse(self.g.is_killed("s3"))
        self.assertTrue(self.g.evaluate("s3", "read")["allowed"])

    def test_revive_unknown_server_fails(self):
        self.assertFalse(self.g.revive("never-killed")["success"])

    def test_kill_requires_server(self):
        self.assertFalse(self.g.kill("")["success"])

    # ── 事故熔断 ──
    def test_incidents_trigger_auto_kill(self):
        last = None
        for _ in range(rg.DEFAULT_INCIDENT_THRESHOLD):
            last = self.g.record_incident("s4", "high", {"rule": "ASI08"})
        self.assertTrue(last["auto_killed"])
        self.assertFalse(self.g.evaluate("s4", "x")["allowed"])

    def test_low_severity_does_not_trip_breaker(self):
        for _ in range(10):
            res = self.g.record_incident("s5", "low")
        self.assertFalse(res["auto_killed"])
        self.assertEqual(res["count"], 0)

    def test_revive_resets_incident_count(self):
        for _ in range(rg.DEFAULT_INCIDENT_THRESHOLD):
            self.g.record_incident("s6", "high")
        self.g.revive("s6")
        res = self.g.record_incident("s6", "high")
        self.assertEqual(res["count"], 1, "复活后事故计数应清零")
        self.assertFalse(res["auto_killed"])

    # ── 审计链 ──
    def test_audit_chain_valid_after_writes(self):
        for i in range(5):
            self.g.evaluate("s7", f"tool{i}")
        chain = rg.verify_chain()
        self.assertTrue(chain["valid"])
        self.assertGreaterEqual(chain["entries"], 5)

    def test_audit_chain_detects_tampering(self):
        """把审计里的"拒绝"改写成"放行"，必须能被检出。"""
        self.g.set_default_deny(True)
        for i in range(3):
            self.g.evaluate("s8", f"tool{i}")       # 全部会被 fail-closed 拒绝
        with open(rg.AUDIT_LOG, "r", encoding="utf-8") as f:
            lines = [l for l in f.read().splitlines() if l.strip()]
        entry = json.loads(lines[1])
        self.assertEqual(entry["detail"]["decision"], rg.DECISION_DENY)
        entry["detail"]["decision"] = rg.DECISION_ALLOW      # 篡改：抹掉一次拒绝
        lines[1] = json.dumps(entry, ensure_ascii=False)
        with open(rg.AUDIT_LOG, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        chain = rg.verify_chain()
        self.assertFalse(chain["valid"])
        self.assertEqual(chain["broken_at"], 2)

    def test_audit_chain_detects_deletion(self):
        for i in range(4):
            self.g.evaluate("s9", f"tool{i}")
        with open(rg.AUDIT_LOG, "r", encoding="utf-8") as f:
            lines = [l for l in f.read().splitlines() if l.strip()]
        del lines[1]                                 # 删掉一条
        with open(rg.AUDIT_LOG, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        self.assertFalse(rg.verify_chain()["valid"])

    def test_kill_is_audited(self):
        self.g.kill("s10", reason="演练")
        events = [e["event"] for e in rg.read_audit(limit=20)]
        self.assertIn("kill", events)

    def test_corrupt_policy_fails_closed(self):
        """策略文件坏了必须收紧到默认拒绝，而不是敞开。"""
        with open(rg.POLICY_FILE, "w", encoding="utf-8") as f:
            f.write("!!! not json !!!")
        res = self.g.evaluate("whatever", "tool")
        self.assertFalse(res["allowed"])
        self.assertTrue(res.get("policy_load_error"))

    def test_status_reports_chain_health(self):
        self.g.evaluate("s11", "t")
        st = self.g.status()
        self.assertTrue(st["audit_chain"]["valid"])
        self.assertIn("killed_count", st)


# ══════════════════════════════════════════
#  持续鉴证订阅
# ══════════════════════════════════════════

class _FakeCertService:
    """替身认证服务，避免测试写真实 certifications.json。"""

    def __init__(self):
        self.revoked = []
        self.renewed = []

    def revoke_certification(self, cert_id, reason=""):
        self.revoked.append((cert_id, reason))
        return True

    def renew_certification(self, cert_id, report):
        self.renewed.append((cert_id, report.get("overall_score")))
        return {"cert_id": cert_id, "status": "certified"}


class TestAttestation(_TempDataMixin, unittest.TestCase):

    def setUp(self):
        tmp = self._isolate()
        self._orig = at.ATTESTATIONS_FILE
        at.ATTESTATIONS_FILE = os.path.join(tmp, "attestations.json")
        self.addCleanup(setattr, at, "ATTESTATIONS_FILE", self._orig)
        self.svc = at.AttestationService()
        self.certs = _FakeCertService()
        self.good = lambda url: {"overall_score": 92, "badge_level": "gold",
                                 "total_findings": 0}
        self.mid = lambda url: {"overall_score": 75, "badge_level": "silver",
                                "total_findings": 3}
        self.bad = lambda url: {"overall_score": 41, "badge_level": "none",
                                "total_findings": 9}

    def _sub(self, url="https://github.com/x/y", **kw):
        res = self.svc.subscribe(url, cert_id="cert_test", **kw)
        self.assertTrue(res["success"], res)
        return res["subscription_id"]

    # ── 订阅生命周期 ──
    def test_subscribe_creates_active(self):
        res = self.svc.subscribe("https://github.com/a/b", "monthly")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], at.STATUS_ACTIVE)
        self.assertEqual(res["price_cny"], at.SUBSCRIPTION_PLANS["monthly"]["CNY"])

    def test_subscribe_requires_source_url(self):
        self.assertFalse(self.svc.subscribe("")["success"])

    def test_subscribe_rejects_unknown_plan(self):
        res = self.svc.subscribe("https://github.com/a/b", "lifetime")
        self.assertFalse(res["success"])
        self.assertIn("available", res)

    def test_duplicate_subscription_blocked(self):
        self.svc.subscribe("https://github.com/dup/x")
        res = self.svc.subscribe("https://github.com/dup/x")
        self.assertFalse(res["success"])
        self.assertTrue(res["existing"])

    def test_renew_extends_from_current_expiry(self):
        sid = self._sub()
        before = self.svc.get_subscription(sid)["expires_at"]
        res = self.svc.renew_subscription(sid, periods=2)
        self.assertTrue(res["success"])
        self.assertGreater(res["expires_at"], before)
        self.assertEqual(res["amount_cny"],
                         round(at.SUBSCRIPTION_PLANS["monthly"]["CNY"] * 2, 2))

    def test_renew_rejects_bad_periods(self):
        sid = self._sub()
        self.assertFalse(self.svc.renew_subscription(sid, 0)["success"])
        self.assertFalse(self.svc.renew_subscription(sid, -3)["success"])

    def test_cancel_then_no_attestation(self):
        sid = self._sub()
        self.assertTrue(self.svc.cancel(sid)["success"])
        res = self.svc.attest_once(sid, scan_fn=self.good, force=True)
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], at.STATUS_CANCELLED)

    def test_cancel_is_idempotent(self):
        sid = self._sub()
        self.svc.cancel(sid)
        self.assertTrue(self.svc.cancel(sid).get("idempotent"))

    def test_renew_cancelled_rejected(self):
        sid = self._sub()
        self.svc.cancel(sid)
        self.assertFalse(self.svc.renew_subscription(sid)["success"])

    # ── 鉴证判定 ──
    def test_pass_renews_certification(self):
        sid = self._sub()
        res = self.svc.attest_once(sid, scan_fn=self.good, force=True,
                                   cert_service=self.certs)
        self.assertEqual(res["result"], "pass")
        self.assertEqual(res["cert_action"], "renewed")
        self.assertEqual(len(self.certs.renewed), 1)

    def test_downgrade_detected(self):
        sid = self._sub()
        self.svc.attest_once(sid, scan_fn=self.good, force=True, cert_service=self.certs)
        res = self.svc.attest_once(sid, scan_fn=self.mid, force=True,
                                   cert_service=self.certs)
        self.assertEqual(res["result"], "downgraded")
        self.assertEqual(res["prev_level"], "gold")

    def test_score_drop_revokes_certification(self):
        """rug-pull 兜底：拿到徽章后改坏代码，复扫必须立刻吊销。"""
        sid = self._sub()
        self.svc.attest_once(sid, scan_fn=self.good, force=True, cert_service=self.certs)
        res = self.svc.attest_once(sid, scan_fn=self.bad, force=True,
                                   cert_service=self.certs)
        self.assertEqual(res["result"], "failed")
        self.assertEqual(res["cert_action"], "revoked")
        self.assertEqual(len(self.certs.revoked), 1)

    def test_throttled_until_due(self):
        sid = self._sub()
        self.svc.attest_once(sid, scan_fn=self.good, force=True, cert_service=self.certs)
        res = self.svc.attest_once(sid, scan_fn=self.good)
        self.assertTrue(res.get("skipped"))
        self.assertEqual(res["reason"], "not_due")

    def test_scan_failure_recorded_not_fatal(self):
        sid = self._sub()

        def boom(url):
            raise RuntimeError("network down")

        res = self.svc.attest_once(sid, scan_fn=boom, force=True, cert_service=self.certs)
        self.assertFalse(res["success"])
        self.assertEqual(res["result"], "error")
        self.assertEqual(len(self.certs.revoked), 0, "扫描失败不应误吊销认证")

    def test_lapsed_subscription_stops_attesting(self):
        sid = self._sub()
        data = at._load()
        past = datetime.now(at.TZ) - timedelta(days=400)
        data["subscriptions"][sid]["expires_at"] = past.isoformat()
        at._save(data)
        res = self.svc.attest_once(sid, scan_fn=self.good, force=True)
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], at.STATUS_LAPSED)

    def test_grace_period_still_attests(self):
        sid = self._sub()
        data = at._load()
        just_expired = datetime.now(at.TZ) - timedelta(days=1)
        data["subscriptions"][sid]["expires_at"] = just_expired.isoformat()
        at._save(data)
        res = self.svc.attest_once(sid, scan_fn=self.good, force=True,
                                   cert_service=self.certs)
        self.assertTrue(res["success"], "宽限期内仍应继续鉴证")

    # ── 证据链 ──
    def test_evidence_chain_valid(self):
        sid = self._sub()
        for fn in (self.good, self.mid, self.good):
            self.svc.attest_once(sid, scan_fn=fn, force=True, cert_service=self.certs)
        sub = self.svc.get_subscription(sid)
        self.assertTrue(sub["evidence_chain"]["valid"])
        self.assertEqual(sub["evidence_chain"]["entries"], 3)

    def test_evidence_chain_detects_tampering(self):
        sid = self._sub()
        self.svc.attest_once(sid, scan_fn=self.bad, force=True, cert_service=self.certs)
        self.svc.attest_once(sid, scan_fn=self.good, force=True, cert_service=self.certs)
        data = at._load()
        # 篡改：把"失败"改成"通过"
        data["subscriptions"][sid]["attestations"][0]["result"] = "pass"
        at._save(data)
        sub = self.svc.get_subscription(sid)
        self.assertFalse(sub["evidence_chain"]["valid"])

    # ── 对外信任状态 ──
    def test_trust_status_unsubscribed(self):
        st = self.svc.trust_status("https://github.com/never/subscribed")
        self.assertFalse(st["subscribed"])
        self.assertFalse(st["continuously_verified"])

    def test_trust_status_verified_after_pass(self):
        url = "https://github.com/ok/tool"
        self.svc.subscribe(url, cert_id="c1")
        sid = self.svc.list_subscriptions()[0]["subscription_id"]
        self.svc.attest_once(sid, scan_fn=self.good, force=True, cert_service=self.certs)
        st = self.svc.trust_status(url)
        self.assertTrue(st["continuously_verified"])
        self.assertEqual(st["last_result"], "pass")

    def test_trust_status_not_verified_after_failure(self):
        url = "https://github.com/bad/tool"
        self.svc.subscribe(url, cert_id="c2")
        sid = self.svc.list_subscriptions()[0]["subscription_id"]
        self.svc.attest_once(sid, scan_fn=self.bad, force=True, cert_service=self.certs)
        st = self.svc.trust_status(url)
        self.assertFalse(st["continuously_verified"],
                         "鉴证失败的工具绝不能显示为持续可信")

    # ── 批量与查询 ──
    def test_run_cycle_processes_due_subscriptions(self):
        self._sub("https://github.com/a/1")
        self._sub("https://github.com/a/2")
        summary = self.svc.run_cycle(scan_fn=self.good, force=True,
                                     cert_service=self.certs)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["attested"], 2)
        self.assertEqual(summary["failed"], 0)

    def test_run_cycle_counts_failures(self):
        self._sub("https://github.com/b/1")
        summary = self.svc.run_cycle(scan_fn=self.bad, force=True,
                                     cert_service=self.certs)
        self.assertEqual(summary["failed"], 1)

    def test_get_expiring_lists_soon_to_expire(self):
        sid = self._sub()
        data = at._load()
        soon = datetime.now(at.TZ) + timedelta(days=3)
        data["subscriptions"][sid]["expires_at"] = soon.isoformat()
        at._save(data)
        items = self.svc.get_expiring(days=7)
        self.assertEqual(len(items), 1)
        self.assertLessEqual(items[0]["remaining_days"], 3)

    def test_list_filters_by_payer(self):
        self.svc.subscribe("https://github.com/p/1", payer_id="agent:p1")
        self.svc.subscribe("https://github.com/p/2", payer_id="agent:p2")
        self.assertEqual(len(self.svc.list_subscriptions(payer_id="agent:p1")), 1)

    def test_plans_exposed(self):
        p = at.plans()
        self.assertIn("monthly", p)
        self.assertIn("annual", p)
        self.assertGreater(p["annual"]["CNY"], p["monthly"]["CNY"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
