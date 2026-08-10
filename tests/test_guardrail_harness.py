# -*- coding: utf-8 -*-
"""#3 Guardrail-as-harness 适配器测试：governance 准入 + 参数内容护栏 + stdio JSON-RPC。"""
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import eco.runtime_governance as rg
from eco.guardrail_harness import GuardrailHarness, _handle_request


class _TmpPolicy:
    """把治理模块的持久化文件重定向到临时目录，避免污染真实策略。"""
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-gh-")
        self._old_pf = rg.POLICY_FILE
        self._old_al = rg.AUDIT_LOG
        rg.POLICY_FILE = os.path.join(self.tmp, "governance.json")
        rg.AUDIT_LOG = os.path.join(self.tmp, "audit.jsonl")

    def tearDown(self):
        rg.POLICY_FILE = self._old_pf
        rg.AUDIT_LOG = self._old_al
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestInterceptGovernance(_TmpPolicy, unittest.TestCase):
    def test_default_allow(self):
        h = GuardrailHarness()
        d = h.intercept("benign-server", "read_file")
        self.assertEqual(d["decision"], "allow")
        self.assertEqual(d["stage"], "pass")

    def test_fail_closed_default_deny(self):
        gov = rg.RuntimeGovernor()
        gov.set_default_deny(True)
        h = GuardrailHarness(gov)
        d = h.intercept("unknown-server", "any_tool")
        self.assertEqual(d["decision"], "deny")
        self.assertEqual(d["stage"], "governance")
        self.assertEqual(d["policy_hit"], "default_deny")
        gov.set_default_deny(False)

    def test_kill_switch_blocks(self):
        gov = rg.RuntimeGovernor()
        gov.kill("evil-srv", "测试熔断")
        h = GuardrailHarness(gov)
        d = h.intercept("evil-srv", "exfil")
        self.assertEqual(d["decision"], "deny")
        self.assertEqual(d["policy_hit"], "kill_switch")
        gov.revive("evil-srv")

    def test_explicit_allowlist(self):
        gov = rg.RuntimeGovernor()
        gov.allow_tool("trusted", "*")
        h = GuardrailHarness(gov)
        d = h.intercept("trusted", "do_thing")
        self.assertEqual(d["decision"], "allow")
        gov.clear_rule("allow", "trusted")


class TestInterceptContentScan(_TmpPolicy, unittest.TestCase):
    def test_argument_secret_blocked(self):
        h = GuardrailHarness()
        # 参数里含 GitHub PAT（critical 模式）应被内容护栏拦截
        args = {"cmd": "git push https://ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA@github.com/x/y"}
        d = h.intercept("srv", "exec", arguments=args)
        self.assertEqual(d["decision"], "deny")
        self.assertEqual(d["stage"], "content_scan")
        self.assertIn("高危", d["reason"])

    def test_argument_privileged_blocked(self):
        h = GuardrailHarness()
        args = {"command": "docker run --privileged --rm pwn"}
        d = h.intercept("srv", "exec", arguments=args)
        self.assertEqual(d["decision"], "deny")
        self.assertEqual(d["stage"], "content_scan")

    def test_clean_argument_passes(self):
        h = GuardrailHarness()
        d = h.intercept("srv", "read", arguments={"path": "/data/report.md"})
        self.assertEqual(d["decision"], "allow")
        self.assertEqual(d["stage"], "pass")


class TestStdioJsonRpc(_TmpPolicy, unittest.TestCase):
    def _harness(self):
        return GuardrailHarness()

    def test_initialize(self):
        resp = _handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"},
                               harness=self._harness())
        self.assertEqual(resp["result"]["serverInfo"]["name"], "aishield-guardrail")

    def test_tools_list(self):
        resp = _handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                               harness=self._harness())
        names = [t["name"] for t in resp["result"]["tools"]]
        self.assertIn("intercept", names)

    def test_tools_call_allow(self):
        resp = _handle_request({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "intercept", "server": "srv", "tool": "read"},
        }, harness=self._harness())
        self.assertEqual(resp["result"]["decision"], "allow")

    def test_tools_call_blocked_by_content(self):
        resp = _handle_request({
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "intercept", "server": "srv", "tool": "exec",
                       "arguments": {"cmd": "echo -----BEGIN PRIVATE KEY-----"}},
        }, harness=self._harness())
        self.assertEqual(resp["result"]["decision"], "deny")

    def test_unknown_method_errors(self):
        resp = _handle_request({"jsonrpc": "2.0", "id": 5, "method": "bogus"},
                               harness=self._harness())
        self.assertIn("error", resp)

    def test_run_stdio_loop(self):
        h = self._harness()
        in_buf = io.StringIO(
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}) + "\n"
            + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                          "params": {"name": "intercept", "server": "s",
                                     "tool": "read"}}) + "\n"
        )
        out_buf = io.StringIO()
        from eco.guardrail_harness import run_stdio
        run_stdio(in_stream=in_buf, out_stream=out_buf)
        lines = [l for l in out_buf.getvalue().splitlines() if l.strip()]
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[1])["result"]["decision"], "allow")


if __name__ == "__main__":
    unittest.main(verbosity=2)
