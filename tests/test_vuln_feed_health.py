# -*- coding: utf-8 -*-
"""
tests/test_vuln_feed_health.py — 上游情报源健康闭环

补的洞（Issue #656）：fetch_vuln_feeds 旧版把三个上游源的异常 `print` 掉就算了，
既不记状态也不告警。后果有两层，且都是静默的：

  1. 单个源可以连续宕机数周无人察觉（"部分降级"不可见）
  2. 三个源**全部**失败时脚本仍然 `return 0` → 流程全绿、状态照写，
     而情报库其实已经停更（"全量停更"被伪装成成功）

本文件钉死修复后的语义：

  · 单源带重试，失败必留痕（ok/error/attempts/consecutive_failures）
  · 非列表返回值不得冒充成功（空结果 ≠ 抓取成功）
  · 传输层全挂必须抛错：「源没有新漏洞」≠「源根本没连上」（第二层假绿）
  · 连续失败次数跨轮次累计，成功即归零（抖动 vs 长期宕机的分辨依据）
  · 部分失败 → exit 0 + P1 降级告警；**全量失败 → exit 1 且不刷新 updated**
  · 恢复即关闭：全通关两条，部分恢复只关"全部宕机"那条
  · 契约：workflow 必须 `set -o pipefail`，否则退出码会被 `| tail` 吞成假绿
  · M7：元监控能看见上游源停更，且无 token / 老数据时不得误判红
"""
import base64
import contextlib
import io
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_vuln_feeds as fv          # noqa: E402
import meta_monitor as mm              # noqa: E402

WF = ROOT / ".github" / "workflows" / "threat-intel-feed.yml"


class _FakeBus:
    """记录 notify / resolve 的假通知总线。"""

    def __init__(self):
        self.notified = []   # (level, title, fingerprint)
        self.resolved = []   # fingerprint

    def notify(self, level, title, body, fingerprint=None, cooldown_hours=6):
        self.notified.append((level, title, fingerprint))
        return True

    def resolve(self, fingerprint, title="", note=""):
        self.resolved.append(fingerprint)
        return True


class _FakeStateBus:
    def set(self, *a, **kw):
        return None


@contextlib.contextmanager
def _fakes(bus):
    """把 scripts.notify / scripts.state_bus 换成假件，避免真实副作用。"""
    notify_mod = types.ModuleType("scripts.notify")
    notify_mod.notify = bus.notify
    notify_mod.resolve = bus.resolve
    bus_mod = types.ModuleType("scripts.state_bus")
    bus_mod.StateBus = _FakeStateBus
    saved = {k: sys.modules.get(k) for k in ("scripts.notify", "scripts.state_bus")}
    sys.modules["scripts.notify"] = notify_mod
    sys.modules["scripts.state_bus"] = bus_mod
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


class TestFetchSourceRetry(unittest.TestCase):
    """单源抓取：重试、留痕、绝不假装成功。"""

    def test_success_first_attempt(self):
        items, h = fv.fetch_source("s", lambda d: [{"id": "A"}], 30, retries=2)
        self.assertTrue(h["ok"])
        self.assertEqual(h["attempts"], 1)
        self.assertEqual(h["items"], 1)
        self.assertIsNone(h["error"])
        self.assertEqual(len(items), 1)

    def test_retries_then_succeeds(self):
        calls = {"n": 0}

        def flaky(days):
            calls["n"] += 1
            if calls["n"] < 2:
                raise RuntimeError("boom")
            return [{"id": "B"}]

        with mock.patch.object(fv.time, "sleep", lambda *_: None):
            items, h = fv.fetch_source("s", flaky, 30, retries=2)
        self.assertTrue(h["ok"], "第 2 次尝试应成功")
        self.assertEqual(h["attempts"], 2)
        self.assertEqual(len(items), 1)

    def test_exhausted_retries_records_truth(self):
        def always_fail(days):
            raise RuntimeError("上游 503")

        with mock.patch.object(fv.time, "sleep", lambda *_: None):
            items, h = fv.fetch_source("nvd", always_fail, 30, retries=2)
        self.assertFalse(h["ok"])
        self.assertEqual(items, [], "失败源必须返回空列表，不得残留部分数据")
        self.assertEqual(h["attempts"], 3, "1 次原始 + 2 次重试")
        self.assertIn("503", h["error"])

    def test_non_list_return_is_not_a_success(self):
        """空结果 ≠ 抓取成功：返回 None 必须判失败，否则空源与好源无法区分。"""
        items, h = fv.fetch_source("s", lambda d: None, 30, retries=0)
        self.assertFalse(h["ok"])
        self.assertEqual(items, [])
        self.assertIn("非列表", h["error"])


class TestConsecutiveFailureHistory(unittest.TestCase):
    """连续失败次数：抖动与长期宕机的分辨依据。"""

    def test_increments_across_runs(self):
        cur = {"osv": {"ok": False}}
        fv._apply_history(cur, {})
        self.assertEqual(cur["osv"]["consecutive_failures"], 1)
        self.assertIsNotNone(cur["osv"]["degraded_since"])

        # 第二轮：把上一轮结果当历史
        cur2 = {"osv": {"ok": False}}
        fv._apply_history(cur2, cur)
        self.assertEqual(cur2["osv"]["consecutive_failures"], 2)

    def test_success_resets_counter(self):
        cur = {"osv": {"ok": True}}
        fv._apply_history(cur, {"osv": {"ok": False, "consecutive_failures": 5}})
        self.assertEqual(cur["osv"]["consecutive_failures"], 0)
        self.assertIsNone(cur["osv"]["degraded_since"])

    def test_degraded_since_is_sticky(self):
        first = {"osv": {"ok": False, "checked_at": "2026-01-01T00:00:00+00:00"}}
        fv._apply_history(first, {})
        started = first["osv"]["degraded_since"]

        second = {"osv": {"ok": False, "checked_at": "2026-01-05T00:00:00+00:00"}}
        fv._apply_history(second, first)
        self.assertEqual(second["osv"]["degraded_since"], started,
                         "宕机起点应保持首次失败时间，不被后续轮次刷新")

    def test_prev_health_tolerates_legacy_db(self):
        self.assertEqual(fv._prev_health({}), {})
        self.assertEqual(fv._prev_health({"source_health": None}), {})
        self.assertEqual(fv._prev_health({"source_health": {"sources": "bad"}}), {})
        self.assertEqual(
            fv._prev_health({"source_health": {"sources": {"osv": {"ok": True}}}}),
            {"osv": {"ok": True}})


class TestMainFailClosed(unittest.TestCase):
    """端到端：全量失败必须红，部分失败必须告警，恢复必须销案。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "threat_intel.json"
        self._saved_db = fv.THREAT_DB
        fv.THREAT_DB = self.db

    def tearDown(self):
        fv.THREAT_DB = self._saved_db
        self.tmp.cleanup()

    def _run(self, osv, nvd, gh, seed=None, argv=None):
        if seed is not None:
            self.db.write_text(json.dumps(seed, ensure_ascii=False), encoding="utf-8")
        bus = _FakeBus()
        argv = argv or ["fetch_vuln_feeds.py", "--notify"]
        with mock.patch.object(fv.time, "sleep", lambda *_: None), \
             mock.patch.object(fv, "fetch_osv", osv), \
             mock.patch.object(fv, "fetch_nvd", nvd), \
             mock.patch.object(fv, "fetch_github_advisory", gh), \
             mock.patch.object(sys, "argv", argv), \
             _fakes(bus):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = fv.main()
        db = json.loads(self.db.read_text(encoding="utf-8"))
        return rc, db, bus, buf.getvalue()

    def test_all_sources_ok_is_green_and_resolves(self):
        item = lambda d: [{"id": "OSV-1", "severity": "high",
                           "title": "t", "published": "2026-01-01"}]
        rc, db, bus, _ = self._run(item, item, item)
        self.assertEqual(rc, 0)
        self.assertEqual(db["sources_failed"], [])
        self.assertEqual(len(db["sources_ok"]), 3)
        self.assertTrue(db["source_health"]["last_success"])
        self.assertIn(fv.FP_DEGRADED, bus.resolved)
        self.assertIn(fv.FP_DOWN, bus.resolved)

    def test_partial_failure_stays_green_but_alerts(self):
        """1/3 源挂：仍有可用数据 → 不阻断，但必须留下降级告警。"""
        ok = lambda d: [{"id": "OSV-1", "severity": "low",
                         "title": "t", "published": "2026-01-01"}]

        def bad(d):
            raise RuntimeError("NVD 超时")

        rc, db, bus, _ = self._run(ok, bad, ok)
        self.assertEqual(rc, 0, "部分源可用时不应让流程变红")
        self.assertEqual(db["sources_failed"], ["nvd"])
        self.assertTrue(db["source_health"]["sources"]["nvd"]["consecutive_failures"] >= 1)
        fprints = [f for _, _, f in bus.notified]
        self.assertIn(fv.FP_DEGRADED, fprints)
        self.assertNotIn(fv.FP_DOWN, fprints, "还有源可用，不该报'全部不可用'")
        self.assertTrue(db["updated"], "有源成功 → updated 应刷新")

    def test_total_outage_fails_run_and_freezes_updated(self):
        """全量失败：exit 1（fail-closed）且 updated 不刷新，让停更可见。"""
        def bad(d):
            raise RuntimeError("上游全挂")

        old = "2026-01-01T00:00:00+00:00"
        seed = {"intel": [{"id": "OLD"}], "updated": old, "total": 1}
        rc, db, bus, out = self._run(bad, bad, bad, seed=seed)
        self.assertEqual(rc, 1, "三个源全挂必须判失败，否则情报停更被伪装成成功")
        self.assertEqual(db["updated"], old, "停更时 updated 不得刷新")
        self.assertEqual(db["sources_ok"], [])
        self.assertEqual(sorted(db["sources_failed"]), ["github-advisory", "nvd", "osv"])
        self.assertEqual(db["total"], 1, "全量失败不得清空既有情报")
        self.assertEqual(db["source_health"]["last_success"], "")
        fprints = [f for _, _, f in bus.notified]
        self.assertIn(fv.FP_DOWN, fprints)
        self.assertIn("fail-closed", out)

    def test_partial_recovery_closes_only_down_alert(self):
        """2/3 恢复：'全部宕机'条件解除 → 关 FP_DOWN；降级仍在 → 保留 FP_DEGRADED。"""
        ok = lambda d: []
        def bad(d):
            raise RuntimeError("still down")
        rc, db, bus, _ = self._run(ok, ok, bad)
        self.assertEqual(rc, 0)
        self.assertIn(fv.FP_DOWN, bus.resolved)
        self.assertNotIn(fv.FP_DEGRADED, bus.resolved,
                         "仍有源不可用，降级告警不应被关闭")

    def test_updated_bumps_only_when_a_source_succeeded(self):
        ok = lambda d: []
        rc, db, _, _ = self._run(ok, ok, ok, seed={"intel": [], "updated": "2020-01-01T00:00:00+00:00"})
        self.assertEqual(rc, 0)
        self.assertNotEqual(db["updated"], "2020-01-01T00:00:00+00:00")


class TestTransportLayerTruthfulness(unittest.TestCase):
    """更隐蔽的一层：'源没有新漏洞'与'源根本没连上'必须可区分。

    fetcher 内部是 `res = _req(...); if not res: continue` 的写法，而 _req 失败
    时只 print 并返回 None —— 于是"传输全挂"会退化成"返回 []"，调用方看到空
    列表只能理解为"该源近期无新情报"，源彻底宕机照样判健康。
    这一层比"三个源全挂仍 exit 0"更难发现：连告警机会都没有。
    """

    def setUp(self):
        fv._reset_transport()

    def tearDown(self):
        fv._reset_transport()

    def _patch_req(self, per_call):
        """替换 _req：按 per_call(url) 的返回/抛错驱动，并同步维护计数。"""
        def fake(url, data=None, headers=None, timeout=30):
            fv._TRANSPORT["req"] += 1
            try:
                payload = per_call(url)
            except Exception:
                fv._TRANSPORT["fail"] += 1
                return None
            fv._TRANSPORT["ok"] += 1
            return payload
        return fake

    def test_connected_but_no_data_is_success(self):
        """连得上但确实没有新漏洞 → 返回 []，不得当成故障。"""
        with mock.patch.object(fv, "_req", self._patch_req(lambda u: {})):
            self.assertEqual(fv.fetch_osv(7), [])
        self.assertEqual(fv._TRANSPORT["ok"], len(fv.OSV_PACKAGES))

    def test_all_requests_failed_raises(self):
        def boom(url):
            raise OSError("连接被重置")
        with mock.patch.object(fv, "_req", self._patch_req(boom)):
            with self.assertRaises(RuntimeError) as cm:
                fv.fetch_osv(7)
        self.assertIn("传输层", str(cm.exception))

    def test_partial_transport_failure_is_tolerated(self):
        """部分请求成功、部分失败 → 不抛错（有数据就继续，避免过度敏感）。"""
        state = {"n": 0}

        def flaky(url):
            state["n"] += 1
            if state["n"] == 1:
                raise OSError("首次失败")
            return {}

        with mock.patch.object(fv, "_req", self._patch_req(flaky)):
            self.assertEqual(fv.fetch_osv(7), [])

    def test_assert_transport_noop_when_no_request_made(self):
        fv._assert_transport("x")   # 不应抛错

    def test_wrapper_reports_fetcher_outage_as_failed(self):
        """端到端：源内部传输全挂 → fetch_source 必须 ok=False，而不是"0 条"。"""

        def boom(url):
            raise OSError("源不可达")

        with mock.patch.object(fv, "_req", self._patch_req(boom)), \
             mock.patch.object(fv.time, "sleep", lambda *_: None):
            items, h = fv.fetch_source("osv", fv.fetch_osv, 7, retries=0)
        self.assertFalse(h["ok"], "源内部传输全挂必须判失败")
        self.assertEqual(items, [])
        self.assertIn("传输层", h["error"])


class TestWorkflowPipefailContract(unittest.TestCase):
    """契约：退出码必须能真正传出去，否则 fail-closed 形同虚设。"""

    def test_pipefail_precedes_fetch(self):
        text = WF.read_text(encoding="utf-8")
        self.assertIn("set -o pipefail", text,
                      "缺少 pipefail：`| tail` 会把 fetch 的退出码吞成 0（假绿）")
        idx_pf = text.index("set -o pipefail")
        idx_run = text.index("fetch_vuln_feeds.py")
        self.assertLess(idx_pf, idx_run, "pipefail 必须出现在调用之前")

    def test_failed_output_is_declared(self):
        text = WF.read_text(encoding="utf-8")
        self.assertIn("failed: ${{ steps.fetch.outputs.failed }}", text)
        self.assertIn("failed=$failed", text)

    def test_no_bare_pipe_without_pipefail(self):
        """回归护栏：不得把 fetch 调用改回裸管道。"""
        for line in WF.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("python scripts/fetch_vuln_feeds.py") and "|" in s:
                self.assertTrue(
                    "set -o pipefail" in WF.read_text(encoding="utf-8"),
                    "裸管道 + 无 pipefail = 失败被吞")


class TestMetaMonitorM7(unittest.TestCase):
    """M7：体系体检必须能看见上游情报源停更，且不得误判红。"""

    def test_registered_in_checks(self):
        labels = [lbl for lbl, _ in mm.CHECKS]
        self.assertIn("M7 上游情报源", labels)

    def test_skips_without_token(self):
        with mock.patch.object(mm, "GH_TOKEN", ""):
            r = mm.check_intel_sources()
        self.assertIsNone(r["ok"], "本地无 token 应跳过而非判红")

    def _remote(self, db):
        payload = base64.b64encode(json.dumps(db, ensure_ascii=False).encode("utf-8")).decode()
        return {"content": payload}

    def _check_with(self, db):
        with mock.patch.object(mm, "GH_TOKEN", "x"), \
             mock.patch.object(mm, "_gh", lambda p: self._remote(db)):
            return mm.check_intel_sources()

    def test_flags_persistent_source_failure(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        r = self._check_with({"source_health": {
            "sources": {"nvd": {"ok": False, "consecutive_failures": 3}},
            "last_success": now}})
        self.assertFalse(r["ok"])
        self.assertIn("nvd", r["detail"])

    def test_tolerates_single_transient_failure(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        r = self._check_with({"source_health": {
            "sources": {"nvd": {"ok": False, "consecutive_failures": 1},
                        "osv": {"ok": True}},
            "last_success": now}})
        self.assertTrue(r["ok"], "单次抖动不该把体系判成 degraded")

    def test_flags_stale_intel(self):
        r = self._check_with({"source_health": {
            "sources": {"osv": {"ok": True}},
            "last_success": "2020-01-01T00:00:00+00:00"}})
        self.assertFalse(r["ok"])
        self.assertIn("未成功更新", r["detail"])

    def test_skips_legacy_db_without_health_block(self):
        r = self._check_with({"intel": [], "updated": "2026-01-01T00:00:00+00:00"})
        self.assertIsNone(r["ok"], "升级前老数据不应判红")

    def test_healthy_when_all_sources_fresh(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        r = self._check_with({"source_health": {
            "sources": {"osv": {"ok": True}, "nvd": {"ok": True},
                        "github-advisory": {"ok": True}},
            "last_success": now}})
        self.assertTrue(r["ok"])
        self.assertIn("3/3", r["detail"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
