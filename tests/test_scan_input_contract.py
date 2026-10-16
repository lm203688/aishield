"""
扫描器输入契约测试 —— S4 信号纯度（error / risk 分型）

背景（2026-10-16 地基加固，S4）:
  scanner/engine.py 的 scan() 在输入校验失败（缺 source_url / 超长 /
  非 GitHub URL / 类型错误）时，曾统一把 risk_level 标成 "critical"。
  这会污染下游信号：一个打错 URL 的用户请求，和一条真正命中的高危发现，
  在 risk_level 维度上无法区分 —— 调度方 / 告警方按 critical 一刀切，
  既制造噪声，又稀释了真实 critical 的权重。

修复：输入错误属于「请求不合法」，不是「发现高危」，risk_level 应降级为
"unknown"，与真正的发现档（safe/low/medium/high/critical）在语义上分离。
error 字段仍保留原始原因，调用方据此区分「输入错误」与「扫描发现」。

本测试钉死这条分型：任何输入校验失败路径，risk_level 必须是 "unknown"。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scanner.engine import scan  # noqa: E402


class TestScanInputContract(unittest.TestCase):
    def test_missing_source_url_risk_unknown(self):
        rep = scan("")
        self.assertIn("error", rep)
        self.assertEqual(rep["risk_level"], "unknown")

    def test_none_source_url_risk_unknown(self):
        rep = scan(None)
        self.assertIn("error", rep)
        self.assertEqual(rep["risk_level"], "unknown")

    def test_non_string_source_url_risk_unknown(self):
        rep = scan(12345)
        self.assertIn("error", rep)
        self.assertEqual(rep["risk_level"], "unknown")

    def test_too_long_source_url_risk_unknown(self):
        rep = scan("https://github.com/a/b" + "x" * 600)
        self.assertIn("error", rep)
        self.assertEqual(rep["risk_level"], "unknown")

    def test_non_http_url_risk_unknown(self):
        # 引擎只把「非 http(s) 的 URL」当作输入错误（"Only GitHub URLs" 分支）；
        # 非 GitHub 的 http(s) URL 会落入正常扫描分支（与 S4 范围无关，属潜在 gap）。
        # 这里验证输入校验分支的 risk_level 分型：ftp:// 既非 http(s) 也非 GitHub。
        rep = scan("ftp://example.com/foo/bar")
        self.assertIn("error", rep)
        self.assertEqual(rep["risk_level"], "unknown")


if __name__ == "__main__":
    unittest.main(verbosity=2)
