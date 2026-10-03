# -*- coding: utf-8 -*-
"""API 契约一致性门禁回归（漂移式：只拦基线之外的新增）。

2026-10-03 一手实测触发：进程内直调 ``do_GET/do_POST`` 逐个探运行时路由，
与服务器自己发布的 /openapi.json 做双向 diff，结果是
**110 条运行时路由 vs 10 条契约路径**，且契约里还留着 3 条跑不通的
（``/api/v1/identity/agents`` ``/api/v1/identity/register`` ``/api/v1/billing/plans``）。
``api/openapi_spec.py`` 是手工维护的 curated 清单，加路由没人会想起改它 ——
所以这里要的是"不许再漂移"，不是一次性把 100+ 条手写完（那是表面工作）。

本文件钉死五件事：
  1. 门禁在当前仓库上是**绿的**（零 phantom、零 unknown、清单与实现一致）；
  2. 门禁**不是空转**：往契约里塞一条不存在的路由，它必须报 phantom；再加一条
     运行时有、清单里没有的路由，它必须报 manifest_missing；
  3. 路由分类逻辑对"未命中措辞"零误判（状态行里的 404 Not Found 曾把 128 条
     真路由全判成未实现 —— 假红和假绿一样要堵）；
  4. **门禁与生成器共用一套判定**（``_is_hit``）：曾经各写一份，生成器排除所有
     404、门禁算 404 命中，于是 4 条"路由存在但资源不存在"的端点被来回误判；
  5. 探针 hermetic：写状态端点被探到也要还原，``state_created`` 必须为空。
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

    # 这两个用例注入固定的命中集：diff(probe=False) 时 implemented 是空的，差集
    # 自然算不出来（第一版就这么写，结果是"断言永远拿不到东西还假装测过"）。
    _FAKE_HITS = [("GET", "/api/v1/health"), ("POST", "/api/v1/prompt-check")]

    def _diff_with_manifest(self, manifest: set):
        real_routes, real_manifest = oc.runtime_routes, oc.manifest_routes
        oc.runtime_routes = lambda probe=True: (
            list(self._FAKE_HITS), [], [], [])
        oc.manifest_routes = lambda: manifest
        try:
            return oc.diff(probe=False)
        finally:
            oc.runtime_routes, oc.manifest_routes = real_routes, real_manifest

    def test_manifest_drift_is_caught(self):
        """加了一条路由却没重跑生成器 —— 运行时有、清单没有，门禁必须红。"""
        d = self._diff_with_manifest({("GET", "/api/v1/health")})
        self.assertEqual(
            d["manifest_missing"], [("POST", "/api/v1/prompt-check")],
            "运行时有、清单没有，门禁却没报 —— 清单过期会一路漏到契约里",
        )

    def test_manifest_extra_is_caught(self):
        """路由删了但清单还留着 —— 相反方向的漂移。"""
        d = self._diff_with_manifest(
            {("GET", "/api/v1/health"), ("GET", "/api/v1/route-gone")})
        self.assertEqual(d["manifest_extra"], [("GET", "/api/v1/route-gone")])

    def test_manifest_and_runtime_agree_in_repo(self):
        """仓库当前状态：运行时命中的每一条都得在清单里（生成器跑过了就该是 0）。"""
        d = gate_json()
        self.assertEqual(d["manifest_missing"], [],
                         f"清单比实现少这些：{d['manifest_missing'][:5]}")
        self.assertEqual(d["manifest_extra"], [])
        self.assertEqual(d["phantom"], [], "契约里还有跑不通的路由")


class TestHitClassification(unittest.TestCase):
    """``_is_hit`` 是门禁与生成器共用的唯一判定，必须把三类 404 分开。"""

    def test_resource_not_found_is_a_hit(self):
        """路由匹配、资源不存在：``{"error": "platform 不存在", ...}`` 恰恰证明
        路由是真的（2026-10-03 因生成器把 404 一律排除而漏登记了 4 条）。"""
        self.assertTrue(oc._is_hit(404, '{"error": "platform 不存在", "error_code": "NOT_FOUND"}'))
        self.assertTrue(oc._is_hit(404, '{"success": false, "reason": "unsigned"}'))

    def test_route_not_found_is_not_a_hit(self):
        for body in ('{"error": "unknown ecosystem endpoint"}',
                     '{"error": "Not found"}',
                     '未知路由'):
            with self.subTest(body=body[:30]):
                self.assertFalse(oc._is_hit(404, body))

    def test_method_not_allowed_is_not_a_hit(self):
        """405/501 是方法选错，不是路径不存在 —— 别把路径一起抹掉。"""
        self.assertFalse(oc._is_hit(405, ""))
        self.assertFalse(oc._is_hit(501, ""))


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
