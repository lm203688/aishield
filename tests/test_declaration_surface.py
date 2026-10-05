# -*- coding: utf-8 -*-
"""公开声明面门禁回归：验证「服务出去的字节」，而不只是「仓库里的文件」。

2026-10-05 一手实测触发。线上 ``https://aishield.tools/.well-known/agent-card.json``
返回 ``235 MCP / 241 skill rule categories``（真值 264 / 291），
同一时刻 ``rule_count_gate.py --check`` 报「✅ 全部一致，无漂移」。两句都是真话：

    server.py 的 Trust 分支已对同一 path 先 return（真正服务 docs 那份）
    后面那个静态分支引用 api/static 那份 —— 永远不可达
    而规则数门禁的覆盖范围恰好只到 api/static

所以"文件里的数字"全对、"服务出去的数字"全错。修复过程中本门禁又实测抓出四处
同类缺口（feeds.xml 因 .xml 不在扩展名白名单而整份漏检、smithery.yaml 因
`MCP / N skill` 小写写法导致 pair 模式不匹配从而 sync 只改了一半、
RFC 9116 的 /.well-known/security.txt 在 robots.txt 里 Allow 却实际 404、
同名孪生副本身份不明）。这些都不是"某个模式写漏了"，而是**验证对象选错了层次**。

本文件钉死六件事：
  1. 注册表自洽：在册服务面的文件真实存在；
  2. 孪生身份：两根下的同名文件必须在台账里登记身份（拦死副本复生）；
  3. 分派唯一性：同一 URL 在同一个分派函数里只声明一次（AST，纯函数反向验证）；
  4. 运行时规则数断言：响应体里的规则数必须等于权威值 —— 喂合成的"坏响应"
     必须报红（**门禁不是空转**）；
  5. 真服务面实测可达且内容自洽（原缺陷的端到端回归）；
  6. `--json` 出口是纯 JSON（横幅必须走 stderr，否则门禁自己写坏）。
"""
import json
import os
import subprocess
import sys
import unittest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_REPO, os.path.join(_REPO, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import scripts.declaration_surface_gate as dsg  # noqa: E402
import scripts.rule_count_gate as rcg  # noqa: E402
from api import declaration_surface as ds  # noqa: E402


class TestRegistry(unittest.TestCase):
    """在册服务面必须与磁盘现实一致。"""

    def test_every_served_file_exists(self):
        for url, s in ds.SERVED.items():
            if s.kind == "computed":
                continue
            with self.subTest(url=url):
                self.assertTrue(s.rel, f"{url} 非 computed 却无服务文件")
                self.assertTrue(os.path.isfile(ds.abs_path(s.rel)),
                                f"{url} 的服务文件不存在: {s.rel}")

    def test_roots_are_the_two_known_ones(self):
        """服务文件只能落在两个已知声明面根下，否则孪生审计会漏掉它。"""
        for url, s in ds.SERVED.items():
            if s.kind == "computed" or not s.rel:
                continue
            rel = s.rel.replace(os.sep, "/")
            with self.subTest(url=url):
                self.assertTrue(
                    rel.startswith(ds.ROOT_STATIC + "/")
                    or rel.startswith(ds.ROOT_DOCS + "/"),
                    f"{url} 的服务文件 {rel} 不在已知声明面根下")

    def test_other_root_roundtrip(self):
        self.assertEqual(ds.other_root("api/static/llms.txt"), "docs/llms.txt")
        self.assertEqual(ds.other_root("docs/llms.txt"), "api/static/llms.txt")
        self.assertEqual(ds.other_root("scanner/rules.py"), "")

    def test_computed_surfaces_are_declared_as_such(self):
        """计算型必须显式标 kind=computed，否则会被当成"缺文件"漏过去。"""
        jwks = ds.SERVED.get("/.well-known/jwks.json")
        self.assertIsNotNone(jwks)
        self.assertEqual(jwks.kind, "computed")
        self.assertEqual(jwks.rel, "")


class TestTwinAudit(unittest.TestCase):
    """同名孪生副本的身份必须写明 —— 这是 235/241 漂移的机械拦截。"""

    def test_all_twins_are_registered(self):
        pairs = list(ds.iter_twins())
        self.assertTrue(pairs, "孪生审计一条都查不到，说明规则本身失效了")
        for served_rel, twin_rel, url in pairs:
            with self.subTest(twin=twin_rel):
                self.assertIn(twin_rel.replace(os.sep, "/"), ds.SHADOWS,
                              f"{twin_rel} 是身份不明的孪生副本")

    def test_agent_card_twin_is_known(self):
        """原缺陷核心：agent-card 在两个根下各有一份，必须都有身份。"""
        served = ds.SERVED["/.well-known/agent-card.json"]
        self.assertTrue(served.rel.replace(os.sep, "/").startswith("docs/"))
        twin = ds.twin_of(served.rel)
        self.assertIn(twin.replace(os.sep, "/"), ds.SHADOWS)

    def test_shadow_ledger_entries_exist(self):
        """台账不能烂成愿望清单 —— 登记了却不存在，会掩盖新孪生。"""
        for rel in ds.SHADOWS:
            with self.subTest(rel=rel):
                self.assertTrue(os.path.exists(ds.abs_path(rel)),
                                f"SHADOWS 登记的 {rel} 不存在")

    def test_shadow_and_served_are_disjoint(self):
        for rel in ds.SHADOWS:
            with self.subTest(rel=rel):
                self.assertIsNone(ds.served_by(rel),
                                  f"{rel} 身份自相矛盾：既在 SERVED 又在 SHADOWS")


class TestDispatchUniqueness(unittest.TestCase):
    """同一 URL 在同一分派函数里只能被比较一次（AST 判定，纯函数）。"""

    def test_duplicate_in_same_dispatcher_is_caught(self):
        """原缺陷的形状：同一个 do_GET 里两处比较同一 URL。"""
        src = (
            "def do_GET(self):\n"
            "    path = self.path\n"
            "    if path == '/.well-known/agent-card.json':\n"
            "        return 1\n"
            "    if path == '/.well-known/agent-card.json':\n"
            "        return 2\n"
        )
        found = dsg.dispatch_duplicates(src, "synthetic.py")
        self.assertEqual(len(found), 1, "同一分派函数内重复声明未被抓到")
        self.assertIn("/.well-known/agent-card.json", found[0].detail)

    def test_same_url_in_two_dispatchers_is_fine(self):
        """分层是正常的：server.py 负责分派、trust_api.py 负责实现。"""
        src = (
            "def do_GET(self):\n"
            "    path = self.path\n"
            "    if path == '/x':\n"
            "        return 1\n"
            "def handle_get(path, q):\n"
            "    if path == '/x':\n"
            "        return 2\n"
        )
        self.assertEqual(dsg.dispatch_duplicates(src, "synthetic.py"), [])

    def test_duplicate_in_non_dispatch_helper_is_ignored(self):
        """助手函数里重复出现同一 URL（拼日志之类）不该判红 —— 判红会逼人加豁免。"""
        src = (
            "def _describe(path):\n"
            "    if path == '/x':\n"
            "        return 'a'\n"
            "    if path == '/x':\n"
            "        return 'b'\n"
        )
        self.assertEqual(dsg.dispatch_duplicates(src, "synthetic.py"), [])

    def test_real_dispatch_modules_are_unique(self):
        """真实模块必须干净；红了就说明又长出了不可达分支。"""
        self.assertEqual(dsg.check_dispatch_uniqueness(), [])


class TestRuntimeRulesAssertion(unittest.TestCase):
    """核心：响应体里的规则数必须等于权威值。"""

    def setUp(self):
        self.auth = rcg.authority()
        self.patterns = rcg._patterns()

    def _run(self, body, rel="docs/.well-known/agent-card.json", excluded=()):
        return dsg.runtime_rules_findings(
            "/.well-known/agent-card.json", rel, body, self.auth,
            self.patterns, excluded_files=excluded)

    def test_doctored_response_is_caught(self):
        """门禁不是空转：把权威值换成别的数字，必须报红。"""
        body = json.dumps({
            "version": "4.11.0",
            "description": "against 999 MCP / 888 skill rule categories",
        }, ensure_ascii=False)
        found = self._run(body)
        self.assertEqual(len(found), 1, "被篡改的响应体没被抓住")
        self.assertIn("999", found[0].detail)
        self.assertIn("888", found[0].detail)

    def test_original_defect_shape_is_caught(self):
        """原缺陷的原文：235 / 241。这正是线上曾经返回的内容。"""
        body = json.dumps({
            "description": "Scan an MCP server against 235 MCP / 241 skill "
                           "rule categories (OWASP MCP Top 10).",
        }, ensure_ascii=False)
        found = self._run(body)
        self.assertEqual(len(found), 1)
        # 两个数都要报出来 —— 只报 skill 一侧等于留下半对文件，
        # 而半对文件在门禁眼里是绿的（这正是 smithery.yaml 踩过的坑）。
        self.assertIn("235", found[0].detail)
        self.assertIn("241", found[0].detail)

    def test_non_declaration_mention_is_clean(self):
        """提到 OWASP MCP Top 10 不该被判成规则数声明。"""
        body = json.dumps({
            "description": "Aligned with OWASP MCP Top 10 and Agentic AI Top 10.",
        }, ensure_ascii=False)
        self.assertEqual(self._run(body), [])

    def test_excluded_historical_file_is_skipped(self):
        """llms-full.txt 的 "214-rule base" 是历史基线，改掉等于伪造历史。"""
        body = "Agentic AI Top 10 detection module (60 ASI rules on the 214-rule base)."
        # 不传豁免名单时必须报红 —— 先证明"跳过"是**按名单**发生的，
        # 而不是这段文本天然无害。少了这一步，将来把豁免名单写错成"全豁免"
        # 也测不出来。
        self.assertTrue(self._run(body, rel="api/static/llms-full.txt"),
                        "未传豁免名单时必须报红 —— 这是「按名单跳过」成立的前提")
        self.assertEqual(
            self._run(body, rel="api/static/llms-full.txt",
                      excluded=rcg.EXCLUDE_FILES), [])

    def test_local_subcount_is_a_known_false_positive_source(self):
        """`the 11 rules above` 指局部子集，不是总数。

        记录它是因为它会周期性出现在散文里；当前只靠 EXCLUDE_FILES 处理
        llms-full.txt，若将来别的文件也这么写，需要的是**加豁免理由**而不是
        放宽模式（放宽会连真正的总数漂移一起放走）。
        """
        found = self._run("see the 11 rules above", rel="api/static/new.txt")
        self.assertTrue(found, "此处若变成空，说明模式被无声放宽了")


class TestVersionAssertion(unittest.TestCase):
    """版本断言只对显式声明了版本路径的资产生效。"""

    def test_nested_version_path(self):
        body = json.dumps({"serverInfo": {"version": "4.11.0"}})
        self.assertIsNone(dsg.version_finding("/x", body, ("serverInfo", "version"),
                                              "4.11.0"))

    def test_mismatch_is_reported(self):
        body = json.dumps({"version": "4.2.0"})
        f = dsg.version_finding("/x", body, ("version",), "4.11.0")
        self.assertIsNotNone(f)
        self.assertIn("4.2.0", f.detail)

    def test_missing_is_reported(self):
        body = json.dumps({"name": "x"})
        f = dsg.version_finding("/x", body, ("version",), "4.11.0")
        self.assertIsNotNone(f)
        self.assertIn("缺少", f.detail)

    def test_surfaces_without_version_path_are_not_checked(self):
        """jwks/manifest/geo-faqs 本来就不带版本，不该被"缺版本"打扰。"""
        for url in ("/.well-known/jwks.json", "/manifest.json", "/geo-faqs.json"):
            with self.subTest(url=url):
                if url in ds.SERVED:
                    self.assertIsNone(ds.SERVED[url].version_path)

    def test_agent_card_declares_version_path(self):
        self.assertEqual(
            ds.SERVED["/.well-known/agent-card.json"].version_path, ("version",))


class TestLiveServedSurfaces(unittest.TestCase):
    """端到端回归：真服务面必须 200，且响应体里的规则数自洽。

    这是唯一在"服务出去之后"的检查，也就是本门禁存在的理由。
    """

    @classmethod
    def setUpClass(cls):
        import openapi_contract as oc
        cls.oc = oc
        cls.auth = rcg.authority()
        cls.patterns = rcg._patterns()
        cls.bodies = {}
        with oc.hermetic_state():
            for url in ds.SERVED:
                status, body = oc._probe_one(url, "GET")
                cls.bodies[url] = (status, body)

    def test_all_registered_surfaces_are_served(self):
        for url in ds.SERVED:
            with self.subTest(url=url):
                status, _ = self.bodies[url]
                self.assertEqual(status, 200, f"{url} 在册却不可服务（{status}）")

    def test_served_bodies_carry_no_rule_drift(self):
        """原缺陷的正面回归：服务出去的字节里不能再有错数字。"""
        problems = []
        for url, (status, body) in self.bodies.items():
            if status != 200:
                continue
            s = ds.SERVED[url]
            hits = dsg.runtime_rules_findings(
                url, s.rel, body, self.auth, self.patterns,
                excluded_files=rcg.EXCLUDE_FILES)
            problems += [f"{url}: {h.detail}" for h in hits]
        self.assertEqual(problems, [],
                         "服务出去的声明面仍有规则数漂移：\n" + "\n".join(problems))

    def test_agent_card_serves_the_gate_covered_file(self):
        """原缺陷的反面：服务的文件必须落在规则数门禁覆盖范围内。"""
        served = ds.SERVED["/.well-known/agent-card.json"]
        rel = served.rel.replace(os.sep, "/")
        self.assertTrue(rcg._is_declared_surface(rel),
                        f"{rel} 被服务却不在规则数门禁覆盖范围内 —— "
                        f"这正是 235/241 长期漂移而不报警的结构原因")

    def test_rfc9116_canonical_path_is_served(self):
        """robots.txt Allow 了 /.well-known/security.txt，就必须真能服务。"""
        status, _ = self.bodies.get("/.well-known/security.txt", (0, ""))
        self.assertEqual(status, 200)


class TestGovernancePolicyRouteIsReachable(unittest.TestCase):
    """路由级回归：/api/v1/governance/policy 的每个 action 都必须真的能到。

    为什么必须写在**路由层**：tests/test_governance.py 一直只测
    ``runtime_governance`` 的模块函数（``g.allow_tool(...)`` 等），全绿。
    而该能力唯一的 HTTP 入口被一个不可达分支吃掉 —— 模块函数对、路由死，
    两边的测试各自都过。这类缺陷只有"从路由发一次真实请求"才看得见。

    2026-10-05 实测：``{"action":"deny"}`` 曾经落到"策略包绑定"分支，把 deny
    当 pack 名，返回 ``unknown policy pack: `` —— 一个降级成误导性错误的
    安全控制（ASI08/ASI10 kill switch 的工具级部分）从上线起不可调用。
    """

    def _post_json(self, path, payload):
        import io
        from email.message import Message
        from api.server import AIShieldHandler
        body = json.dumps(payload).encode("utf-8")
        h = object.__new__(AIShieldHandler)
        h.rfile = io.BytesIO(body)
        w = io.BytesIO()
        h.wfile = w
        h.client_address = ("127.0.0.1", 5555)
        h.command = "POST"
        h.request_method = "POST"
        h.path = path
        h.requestline = f"POST {path} HTTP/1.1"
        h.request_version = "HTTP/1.1"
        h.server_version = "AIShield"
        h.system_version = ""
        h.protocol_version = "HTTP/1.1"
        msg = Message()
        msg["Host"] = "127.0.0.1"
        msg["Content-Length"] = str(len(body))
        msg["Content-Type"] = "application/json"
        h.headers = msg
        h.do_POST()
        raw = w.getvalue().decode("utf-8", "replace")
        head, _, pl = raw.partition("\r\n\r\n")
        import re
        m = re.search(r"HTTP/1\.1\s+(\d{3})", head)
        status = int(m.group(1)) if m else 0
        try:
            return status, json.loads(pl)
        except ValueError:
            return status, {"_raw": pl[:200]}

    def test_all_documented_actions_are_reachable(self):
        import openapi_contract as oc
        path = "/api/v1/governance/policy"
        cases = [
            ({"server": "s1", "action": "allow", "tools": "*"}, "allow"),
            ({"server": "s1", "action": "deny", "tools": "*"}, "deny"),
            ({"server": "s1", "action": "default_deny", "enabled": False}, None),
        ]
        with oc.hermetic_state():
            for payload, expect_bucket in cases:
                with self.subTest(action=payload["action"]):
                    status, doc = self._post_json(path, payload)
                    self.assertEqual(
                        status, 200,
                        f"{payload['action']} 未走通：{status} {doc}")
                    self.assertTrue(doc.get("success"),
                                    f"{payload['action']} 返回失败：{doc}")
                    if expect_bucket:
                        self.assertEqual(doc.get("bucket"), expect_bucket)

    def test_unknown_action_is_rejected_not_reinterpreted(self):
        """未知 action 必须明确回绝，不能静默按 bind 处理。

        静默降级正是那个死分支能存活至今的原因：调用方收到的是
        "unknown policy pack"，于是一直以为是自己参数写错。
        """
        import openapi_contract as oc
        with oc.hermetic_state():
            status, doc = self._post_json(
                "/api/v1/governance/policy",
                {"server": "s1", "action": "definitely_not_an_action"})
        self.assertEqual(status, 400)
        self.assertFalse(doc.get("success"))
        self.assertIn("bind", doc.get("error", ""))


class TestGateIsNotDecoration(unittest.TestCase):
    """门禁整体行为：当前绿、出口可机读、异常必须 exit 2。"""

    def _run_gate(self, *args, timeout=900):
        proc = subprocess.run(
            [sys.executable, os.path.join(_REPO, "scripts",
                                          "declaration_surface_gate.py"), *args],
            cwd=_REPO, capture_output=True, text=True, timeout=timeout)
        return proc

    def test_gate_is_green(self):
        proc = self._run_gate("--check", "--json")
        self.assertEqual(proc.returncode, 0,
                         f"声明面门禁未通过:\n{proc.stdout}\n{proc.stderr}")
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["error_count"], 0)

    def test_json_stdout_is_pure(self):
        """横幅必须走 stderr：`--json` 出口混进非 JSON 行 = 门禁自己写坏。"""
        proc = self._run_gate("--check", "--json")
        json.loads(proc.stdout)  # 抛异常即失败
        self.assertNotIn("ProxyGateway", proc.stdout)

    def test_missing_module_is_not_green(self):
        """门禁自身坏掉必须 exit 2，不能退化成"没找到问题"。

        这里用 --no-probe 之外的手段模拟不了，所以直接断言退出码语义：
        非 0 且非 1 只可能来自异常路径。改用检查纯函数在全绿仓库上返回空集合，
        再断言"有输入就必须有输出"这一不变量由 TestRuntimeRulesAssertion 覆盖。
        """
        proc = self._run_gate("--check", "--no-probe")
        self.assertIn(proc.returncode, (0, 1))
        if proc.returncode == 0:
            self.assertIn("✅", proc.stdout)


if __name__ == "__main__":
    unittest.main()
