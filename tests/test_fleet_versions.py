# -*- coding: utf-8 -*-
"""
tests/test_fleet_versions.py — Fleet 版本流（版本漂移检测）

F5 Fleet 原本只有"健康聚合"，没有版本维度：一支机队里各成员跑在哪些版本、
谁掉队、是否出现未授权版本，全都看不见。本文件钉死版本流的不变量：

  1. ingest 必须采集 version（顶层 / report 两层都要认）
  2. 基准版本 = 多数成员采用者（配置漂移语义），并列时取更高版本
  3. unknown 版本不得被选为基准（无法验证的版本不配当标杆），且自身算漂移
  4. 全部同版本 → ok=True 无漂移；任一成员版本不同 → 计入 drifted
  5. 确定性：同一输入多次计算结果一致

所有用例使用临时数据文件，不触碰真实 data/fleet.json。
"""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanner.fleet import FleetService  # noqa: E402


class TestFleetVersionStream(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="aishield_fleet_")
        self.addCleanup(shutil.rmtree, self._tmp, True)
        self.svc = FleetService(path=os.path.join(self._tmp, "fleet.json"))

    def _ingest(self, url, version=None, **kw):
        payload = {"source_url": url, "overall_score": 90,
                   "badge_level": "gold", "risk_level": "safe"}
        if version is not None:
            payload["version"] = version
        payload.update(kw)
        return self.svc.ingest(payload)

    # ── 采集 ──
    def test_version_captured_from_top_level(self):
        self._ingest("https://github.com/a/x", version="1.2.3")
        m = self.svc.list_members()[0]
        self.assertEqual(m["version"], "1.2.3")

    def test_version_captured_from_report(self):
        self.svc.ingest({"source_url": "https://github.com/a/y",
                         "report": {"version": "2.0.0", "overall_score": 80}})
        self.assertEqual(self.svc.list_members()[0]["version"], "2.0.0")

    def test_missing_version_is_unknown_not_crash(self):
        self._ingest("https://github.com/a/z")
        self.assertEqual(self.svc.list_members()[0]["version"], "unknown")

    # ── 基准与漂移 ──
    def test_empty_fleet_is_ok(self):
        vs = self.svc.version_stream()
        self.assertEqual(vs["total"], 0)
        self.assertIsNone(vs["canonical"])
        self.assertTrue(vs["ok"])

    def test_uniform_version_has_no_drift(self):
        for i in range(3):
            self._ingest(f"https://github.com/a/{i}", version="1.0.0")
        vs = self.svc.version_stream()
        self.assertEqual(vs["canonical"], "1.0.0")
        self.assertEqual(vs["drifted"], [])
        self.assertTrue(vs["ok"])

    def test_majority_version_is_canonical(self):
        """基准取多数派（配置漂移语义）：2 票 1.0.0 胜过 1 票 2.0.0。"""
        self._ingest("https://github.com/a/1", version="1.0.0")
        self._ingest("https://github.com/a/2", version="1.0.0")
        self._ingest("https://github.com/a/3", version="2.0.0")
        vs = self.svc.version_stream()
        self.assertEqual(vs["canonical"], "1.0.0")
        self.assertEqual(len(vs["drifted"]), 1)
        self.assertEqual(vs["drifted"][0]["version"], "2.0.0")
        self.assertFalse(vs["ok"])

    def test_tie_break_prefers_higher_version(self):
        self._ingest("https://github.com/b/1", version="1.0.0")
        self._ingest("https://github.com/b/2", version="1.2.0")
        vs = self.svc.version_stream()
        self.assertEqual(vs["canonical"], "1.2.0", "并列时应选更高版本作基准")

    def test_unknown_never_becomes_canonical(self):
        """无法验证的版本不能当标杆。"""
        self._ingest("https://github.com/c/1", version="unknown")
        self._ingest("https://github.com/c/2", version="3.1.0")
        vs = self.svc.version_stream()
        self.assertEqual(vs["canonical"], "3.1.0")
        self.assertEqual(vs["unknown"], 1)
        self.assertEqual(len(vs["drifted"]), 1)
        self.assertEqual(vs["drifted"][0]["version"], "unknown")

    def test_all_unknown_is_tolerated(self):
        self._ingest("https://github.com/d/1")
        self._ingest("https://github.com/d/2")
        vs = self.svc.version_stream()
        self.assertEqual(vs["canonical"], "unknown")
        self.assertTrue(vs["ok"], "全是未知版本时不产生漂移噪声")
        self.assertEqual(vs["unknown"], 2)

    def test_versions_buckets_list_identities(self):
        self._ingest("https://github.com/e/1", version="1.0.0")
        self._ingest("https://github.com/e/2", version="2.0.0")
        vs = self.svc.version_stream()
        self.assertEqual(sorted(vs["versions"].keys()), ["1.0.0", "2.0.0"])
        self.assertEqual(vs["versions"]["1.0.0"], ["https://github.com/e/1"])

    def test_deterministic(self):
        self._ingest("https://github.com/f/1", version="1.0.0")
        self._ingest("https://github.com/f/2", version="2.0.0")
        a = self.svc.version_stream()
        b = self.svc.version_stream()
        self.assertEqual(a, b, "同一输入多次计算结果必须一致")

    def test_reingest_updates_version(self):
        """成员升级后，版本流必须随之更新，不能停留在旧版本。"""
        self._ingest("https://github.com/g/1", version="1.0.0")
        self._ingest("https://github.com/g/1", version="2.0.0")
        vs = self.svc.version_stream()
        self.assertEqual(vs["canonical"], "2.0.0")
        self.assertEqual(vs["total"], 1)

    def test_ver_tuple_orders_numerically_not_lexically(self):
        from scanner.fleet import _ver_tuple
        self.assertGreater(_ver_tuple("1.10.0"), _ver_tuple("1.9.0"),
                           "版本比较必须按数字段，不能按字符串字典序")
        self.assertEqual(_ver_tuple(""), (0,))


if __name__ == "__main__":
    unittest.main(verbosity=2)
