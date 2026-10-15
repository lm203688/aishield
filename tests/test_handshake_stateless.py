# -*- coding: utf-8 -*-
"""
tests/test_handshake_stateless.py — MCP 2026-07-28 无状态化风险面

背景：2026-07-28 版协议移除了 initialize 握手与 Mcp-Session-Id，改无状态核心。
这带来一个**新出现的信任假设**：

    旧版有状态协议下，Session-Id 隐式绑定了主体；移除握手后，server 在
    `_meta` 里自报的身份/能力成为**唯一线索**。协议明确要求：`_meta` 中的
    身份与能力声明是**不可信输入**，必须与令牌确立的主体核对，不一致
    fail-closed。若客户端只信 `_meta`，任何 server 都能冒充他人。

另一处新面是 MCP Apps（服务端渲染 HTML）—— 必须按不可信内容处理。

本文件钉死这两条检测，尤其钉住"取值路径"这一具体失效形态：
若从result 内读token 主体（实际在传输层/result 之外），该 critical 检测
会静默永不触发 —— 看起来实现了、实际是死代码，比没写更危险。
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scanner.handshake import (  # noqa: E402
    _check_meta_identity_consistency,
    _check_mcp_apps_untrusted,
)


def _types(findings):
    return [f["type"] for f in findings]


def _sev(findings, t):
    for f in findings:
        if f["type"] == t:
            return f["severity"]
    return None


class TestMetaIdentityConsistency(unittest.TestCase):

    def test_subject_mismatch_is_critical(self):
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"subject": "attacker"}}}, f,
            transport_subject="real-client")
        self.assertIn("meta_subject_mismatch", _types(f))
        self.assertEqual(_sev(f, "meta_subject_mismatch"), "critical")

    def test_matching_subject_silent(self):
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"subject": "real-client"}}}, f,
            transport_subject="real-client")
        self.assertEqual(f, [])

    def test_token_subject_read_outside_result(self):
        """回归钉死：token 主体**只**认传输层传入的 transport_subject。

        伪造服务端若在 response 内自填 token_subject 企图令比对相等，必须被
        忽略；只有调用方从传输层传入的基准才作数。早期实现从 result 里读
        token_subject，导致这条 critical 永不触发（"看起来实现了、实际是死代码"）。
        """
        f = []
        # 服务端自报 subject="a"，并恶意在 result 内伪造 token_subject="a" 企图匹配；
        # 但传输层确立的主体是 "real"（被扫 URL 所确立），二者不等 → 必须报 critical。
        _check_meta_identity_consistency(
            {"result": {"_meta": {"subject": "a"}}, "token_subject": "a"}, f,
            transport_subject="real")
        self.assertIn("meta_subject_mismatch", _types(f))

    def test_result_token_subject_is_ignored(self):
        """显式钉死：result 内的 token_subject / granted_scopes 一律不读。

        若实现错误地回退去读 result 内字段，下面这个「自填相等」的样本会漏报，
        测试随之失败——这是本修复要杜绝的回归。
        """
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"subject": "evil"},
                        "token_subject": "evil"}}, f,
            transport_subject="trusted-real")
        self.assertIn("meta_subject_mismatch", _types(f))

        g = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"scopes": ["admin"]},
                        "granted_scopes": ["admin"]}}, g,
            transport_granted_scopes=["read"])
        self.assertIn("meta_scope_overclaim", _types(g))

    def test_principal_alias_detected(self):
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"principal": "x"}}}, f,
            transport_subject="y")
        self.assertIn("meta_subject_mismatch", _types(f))

    def test_client_id_alias_detected(self):
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"client_id": "x"}}}, f,
            transport_subject="y")
        self.assertIn("meta_subject_mismatch", _types(f))

    def test_no_meta_is_silent(self):
        f = []
        _check_meta_identity_consistency({"result": {}}, f,
                                         transport_subject="u")
        self.assertEqual(f, [])

    def test_meta_none_is_silent(self):
        f = []
        _check_meta_identity_consistency({"result": {"_meta": None}}, f,
                                         transport_subject="u")
        self.assertEqual(f, [])

    def test_no_token_subject_cannot_judge(self):
        """只有自报、无传输层基准时**不报**—— 不能凭空指控。"""
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"subject": "anyone"}}}, f)
        self.assertEqual(f, [])

    def test_meta_not_object_is_flagged(self):
        f = []
        _check_meta_identity_consistency({"result": {"_meta": "string"}}, f,
                                         transport_subject="u")
        self.assertIn("meta_not_object", _types(f))
        self.assertEqual(_sev(f, "meta_not_object"), "medium")

    def test_meta_not_object_list(self):
        f = []
        _check_meta_identity_consistency({"result": {"_meta": [1, 2]}}, f,
                                         transport_subject="u")
        self.assertIn("meta_not_object", _types(f))

    def test_non_dict_result_silent(self):
        f = []
        _check_meta_identity_consistency({"result": "text"}, f,
                                         transport_subject="u")
        self.assertEqual(f, [])

    def test_missing_result_silent(self):
        f = []
        _check_meta_identity_consistency({}, f, transport_subject="u")
        self.assertEqual(f, [])

    def test_scope_overclaim_is_high(self):
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"scopes": ["read", "admin"]}}}, f,
            transport_granted_scopes=["read"])
        self.assertIn("meta_scope_overclaim", _types(f))
        self.assertEqual(_sev(f, "meta_scope_overclaim"), "high")

    def test_scope_within_grant_silent(self):
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"scopes": ["read"]}}}, f,
            transport_granted_scopes=["read", "write"])
        self.assertEqual(f, [])

    def test_roles_alias_treated_as_scopes(self):
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"roles": ["admin"]}}}, f,
            transport_granted_scopes=["user"])
        self.assertIn("meta_scope_overclaim", _types(f))

    def test_no_granted_baseline_no_overclaim(self):
        """没有授予基准时不报越权 —— 不凭空指控。"""
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"scopes": ["admin"]}}}, f)
        self.assertEqual(f, [])

    def test_granted_not_list_no_overclaim(self):
        f = []
        _check_meta_identity_consistency(
            {"result": {"_meta": {"scopes": ["admin"]}}}, f,
            transport_granted_scopes="admin")
        self.assertEqual(f, [])


class TestMcpAppsUntrusted(unittest.TestCase):

    def test_explicit_no_sandbox_is_high(self):
        f = []
        _check_mcp_apps_untrusted(
            {"result": {"apps": [{"uri": "https://x/app",
                                  "sandboxed": False}]}}, f)
        self.assertIn("mcp_app_untrusted_content", _types(f))
        self.assertEqual(_sev(f, "mcp_app_untrusted_content"), "high")

    def test_sandbox_false_alias_is_high(self):
        f = []
        _check_mcp_apps_untrusted(
            {"result": {"apps": [{"uri": "https://x/a", "sandbox": False}]}}, f)
        self.assertIn("mcp_app_untrusted_content", _types(f))

    def test_html_resource_flagged_info(self):
        f = []
        _check_mcp_apps_untrusted(
            {"result": {"apps": [{"uri": "https://x/a.html"}]}}, f)
        self.assertIn("mcp_app_html_resource", _types(f))
        self.assertEqual(_sev(f, "mcp_app_html_resource"), "info")

    def test_sandboxed_app_silent(self):
        f = []
        _check_mcp_apps_untrusted(
            {"result": {"apps": [{"uri": "https://x/a",
                                  "sandboxed": True}]}}, f)
        self.assertEqual(f, [])

    def test_ui_alias_supported(self):
        f = []
        _check_mcp_apps_untrusted(
            {"result": {"ui": [{"uri": "https://x/a.html"}]}}, f)
        self.assertIn("mcp_app_html_resource", _types(f))

    def test_no_apps_silent(self):
        f = []
        _check_mcp_apps_untrusted({"result": {}}, f)
        self.assertEqual(f, [])

    def test_apps_not_list_silent(self):
        f = []
        _check_mcp_apps_untrusted({"result": {"apps": "x"}}, f)
        self.assertEqual(f, [])

    def test_app_without_uri_silent(self):
        f = []
        _check_mcp_apps_untrusted({"result": {"apps": [{}]}}, f)
        self.assertEqual(f, [])

    def test_non_dict_app_skipped(self):
        f = []
        _check_mcp_apps_untrusted({"result": {"apps": ["str", None]}}, f)
        self.assertEqual(f, [])

    def test_non_dict_result_silent(self):
        f = []
        _check_mcp_apps_untrusted({"result": []}, f)
        self.assertEqual(f, [])


if __name__ == "__main__":
    unittest.main()
