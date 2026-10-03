# -*- coding: utf-8 -*-
"""API 契约一致性门禁回归（漂移式：只拦基线之外的新增）。

2026-10-03 一手实测触发：进程内直调 ``do_GET/do_POST`` 逐个探运行时路由，
与服务器自己发布的 /openapi.json 做双向 diff，结果是
**110 条运行时路由 vs 10 条契约路径**，且契约里还留着 3 条跑不通的
（``/api/v1/identity/agents`` ``/api/v1/identity/register`` ``/api/v1/billing/plans``）。
``api/openapi_spec.py`` 是手工维护的 curated 清单，加路由没人会想起改它 ——
所以这里要的是"不许再漂移"，不是一次性把 100+ 条手写完（那是表面工作）。

本文件钉死四件事：
  1. 门禁在当前仓库上是**绿的**（存量缺口都在基线里）；
  2. 门禁**不是空转**：往契约里塞一条不存在的路由，它必须报 phantom_new；
  3. 路由分类逻辑对"未命中措辞"零误判（状态行里的 404 Not Found 曾把 128 条
     真路由全判成未实现 —— 假红和假绿一样要堵）；
  4. 探针 hermetic：写状态端点被探到也要还原，``state_created`` 必须为空。
"""
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import scripts.openapi_contract as oc  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def gate_json(timeout=900):
    """跑一次门禁 EOF 出口（子进程）。

    **必须一进程一次**：探针会打到写状态端点，同一个进程里跑第二遍 diff，
    implemented 会从 110 漂到 123（第二次看到的是被第一次探针改过的数据）。
    门禁判的是"路由有没有命中"，不该被仓库数据态影响 —— 用子进程把状态冻结在
    干净起点，才保证 green 是真 green。
    """
    proc = subprocess.run(
        [sys.executable, os.path.join("scripts", "openapi_contract.py"), "--json"],
        cwd=REPO, capture_output=True, timeout=timeout,
    )
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")[-1500:]
    return json.loads(proc.stdout.decode("utf-8", "replace"))


class TestMissClassification(unittest.TestCase):
    """探针分类：必须分清"路由不存在"和"真的跑进处理分支了"。"""

    def test_not_found_status_line_is_not_a_miss(self):
        """2026-10-03 真踩过的坑：body 没剥头部时 "404 Not Found" 会被当成
        "not found" 的命中项，128 条真路由一夜之间全变"未实现"。"""
        status, body = 404, '{"error": "Not found", "error_code": "NOT_FOUND"}'
        self.assertTrue(oc._is_miss(status, body), "兜底 404 必须判为未命中")

    def test_unknown_endpoint_wording_is_a_miss(self):
        for body in (
            '{"error": "unknown ecosystem endpoint", "path": "/api/v1/x"}',
            '{"error": "unknown endpoint: /api/v1/x"}',
            '{"error": "unknown GET route: /api/v1/x", "ok": false}',
            '{"error": "unknown trust endpoint", "path": "/api/v1/trust/score"}',
        ):
            with self.subTest(body=body[:40]):
                self.assertTrue(oc._is_miss(404, body))

    def test_business_errors_are_not_misses(self):
        for body in (
            '{"error": "Rate limit exceeded (60 req/hour per IP)"}',
            '{"error": "Unauthorized"}',
            '{"error": "source_url is required"}',
            '{"valid": false, "reason": "unsigned"}',
        ):
            with self.subTest(body=body[:40]):
                self.assertFalse(oc._is_miss(429, body))
                self.assertFalse(oc._is_miss(401, body))

    def test_real_hits_are_not_misses(self):
        self.assertFalse(oc._is_miss(200, '{"count": 5, "packs": {}}'))
        self.assertFalse(oc._is_miss(400, '{"error": "Invalid JSON"}'))


class TestContractParsing(unittest.TestCase):
    """OpenAPI 方法键是小写（get/post），按大写匹配会把契约数成 0。"""

    def test_lowercase_methods_are_normalised(self):
        routes = oc.contract_routes()
        self.assertGreater(len(routes), 0, "契约解析出 0 条 —— 多半是大小写问题")
        self.assertTrue(
            all(v in ("GET", "POST") for v, _ in routes),
            f"方法键没归一化：{sorted({v for v, _ in routes})[:5]}",
        )
        self.assertIn(("GET", "/api/v1/health"), routes)


class TestGateNotVacuous(unittest.TestCase):
    """门禁必须能真的报出新漂移，否则它就是个永远绿的摆设。"""

    def test_new_phantom_is_caught(self):
        real = oc.contract_routes

        def fake():
            return real() | {("GET", "/api/v1/this-route-never-existed")}

        oc.contract_routes = fake
        try:
            d = oc.diff(probe=False)   # 纯契约侧构造，不需要探针
        finally:
            oc.contract_routes = real
        self.assertIn(
            ("GET", "/api/v1/this-route-never-existed"),
            d["phantom_new"],
            "往契约里塞一条不存在的路由，门禁却没报 —— 说明它是空转",
        )

    def test_baseline_holds_currently(self):
        d = gate_json()
        self.assertEqual(d["unknown_new"], [], f"出现新增未登记路由：{d['unknown_new']}")
        self.assertEqual(d["phantom_new"], [], f"契约里出现跑不通的路由：{d['phantom_new']}")
        self.assertEqual(d["probe_errors"], [], "探针自身报错，结论不可信")
        self.assertGreater(d["implemented_count"], 50)


class TestProbeHermetic(unittest.TestCase):
    """探针会打到 /api/v1/fleet/ingest 这类写状态端点，必须能自证清白。"""

    def test_probe_creates_no_state_files(self):
        d = gate_json()
        self.assertEqual(d["state_created"], [], f"探针新建了状态文件：{d['state_created']}")

    def test_known_write_endpoints_were_restored(self):
        d = gate_json()
        # 这两条是实测被探针写脏、又被还原掉的文件（fleet ingest 会塞 anon 成员）
        touched = {os.path.basename(p) for p in d["state_restored"]}
        self.assertTrue(touched <= {"fleet.json", "monitored_tools.json"}, f"意外触碰：{touched}")

    def test_fleet_file_has_no_probe_artifact(self):
        p = os.path.join(REPO, "data", "fleet.json")
        if not os.path.exists(p):
            self.skipTest("data/fleet.json 不存在")
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        bad = [k for k in (data.get("members") or {}) if k.startswith("anon-2026-")]
        self.assertEqual(bad, [], f"探针残留污染：{bad}")


class TestJsonExportIsMachineReadable(unittest.TestCase):
    """``--json`` 出口必须能被机器解析 —— 网关横幅不能混进 stdout。"""

    def test_stdout_is_pure_json(self):
        env = dict(os.environ)
        proc = subprocess.run(
            [sys.executable, os.path.join("scripts", "openapi_contract.py"), "--json"],
            cwd=REPO, capture_output=True, timeout=600, env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace")[-800:])
        try:
            d = json.loads(proc.stdout.decode("utf-8", "replace"))
        except json.JSONDecodeError as e:
            self.fail(f"--json 出口不是合法 JSON（被库级横幅污染？）：{e}\n"
                      f"stdout 开头：{proc.stdout[:120]!r}")
        for k in ("implemented_count", "contract_count", "unknown_new", "phantom_new",
                  "probe_errors", "state_created", "state_restored"):
            self.assertIn(k, d)


if __name__ == "__main__":
    unittest.main(verbosity=2)
