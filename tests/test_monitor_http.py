"""监控端点（/api/v1/monitor/*）的 HTTP 契约测试。

来源与必要性
─────────────
这三个端点的功能断言**此前只存在于 tests/quick_test.py**（脚本式、unittest 之外）。
2026-10-16 清理遗留脚本时发现：quick_test.py 失败时只打印「Failed: N」而不
`sys.exit(1)`，退出码恒为 0 —— 它在 CI 里是**假绿**，等于没有测试。因此该文件被
删除前，必须先把它独有的覆盖搬进正式套件（否则是真实覆盖回退）。

覆盖点：add → list → check → remove 的完整链路，外加两处容易退化的契约：
  * 缺 source_url 必须 400（不能吞掉变成 200 空结果）
  * check 在零监控项时必须零网络往返（否则 CI 会因 GitHub API 抖动成红）

隔离方式
─────────
不启动真实 HTTP 服务器：直接以 object.__new__() 构造 handler，喂伪 rfile/wfile。
该模式在本仓已有先例（tests/test_declaration_surface.py 的 _post_json），好处是
不占端口、Windows 上可靠、也不受 ThreadingMixIn 的线程时序影响。

持久化必须重定向：scanner/monitor.py 把数据写进仓库根的 data/monitored_tools.json，
而**该文件是 git 跟踪的**。测试若真写进去，会留下一条只写不收的脏记录并让工作树
变脏 —— 正是本仓要治的那个病。故 setUp 把 MONITOR_FILE 指到临时目录，tearDown
还原并核验仓库里的原文件字节未被触碰。

网络必须打桩：check_version_change 会打真实 GitHub API。测试套件不该依赖外网
（外网抖动会让 CI 出现与本仓代码无关的红），且 monitor/check 在零监控项时应短路，
这一点单独断言，防止未来有人把网络调用挪到短路判断之前。
"""
from __future__ import annotations

import email.message
import io
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scanner.monitor as MON  # noqa: E402
import api.server as S        # noqa: E402
from api.server import AIShieldHandler  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TRACKED_FILE = _REPO_ROOT / "data" / "monitored_tools.json"

_TOOL = "https://github.com/modelcontextprotocol/servers"
_TOOL_NAME = "mcp-official-smoke"


class _Http(unittest.TestCase):
    """以伪 rfile/wfile 直接驱动 handler，不启动服务器。"""

    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="aishield_monitor_")
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)
        # 重定向持久化到临时目录：仓库里的 data/monitored_tools.json 是跟踪文件。
        self._orig_monitor_file = MON.MONITOR_FILE
        MON.MONITOR_FILE = os.path.join(self._tmp, "monitored_tools.json")
        # 记录原文件字节，收尾时断言未被污染。
        self._orig_bytes = (
            _TRACKED_FILE.read_bytes() if _TRACKED_FILE.exists() else None
        )

    def tearDown(self):
        MON.MONITOR_FILE = self._orig_monitor_file
        now = _TRACKED_FILE.read_bytes() if _TRACKED_FILE.exists() else None
        self.assertEqual(
            now, self._orig_bytes,
            "测试污染了 git 跟踪的 data/monitored_tools.json —— 请检查隔离是否失效",
        )

    # ── 驱动 ─────────────────────────────────────────────────────────
    def _call(self, method: str, path: str, body=None):
        """返回 (status, parsed_json_or_text)。"""
        body_bytes = (
            json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None
            else (b"" if method == "POST" else None)
        )
        h = object.__new__(AIShieldHandler)
        h.rfile = io.BytesIO(body_bytes or b"")
        h.wfile = io.BytesIO()
        h.client_address = ("127.0.0.1", 5555)
        h.command = method
        h.request_method = method
        h.path = path
        h.requestline = f"{method} {path} HTTP/1.1"
        h.request_version = "HTTP/1.1"
        h.server_version = "AIShield"
        h.system_version = ""
        h.protocol_version = "HTTP/1.1"
        msg = email.message.Message()
        msg["Host"] = "127.0.0.1"
        if body_bytes:
            msg["Content-Length"] = str(len(body_bytes))
            msg["Content-Type"] = "application/json"
        h.headers = msg
        if method == "POST":
            h.do_POST()
        else:
            h.do_GET()
        raw = h.wfile.getvalue().decode("utf-8", "replace")
        head, _, payload = raw.partition("\r\n\r\n")
        status = int(head.split(" ", 2)[1]) if " " in head else 0
        ctype = "application/json"
        for line in head.split("\r\n")[1:]:
            if line.lower().startswith("content-type:"):
                ctype = line.split(":", 1)[1].strip()
        if "json" in ctype.lower() or payload.lstrip().startswith(("{", "[")):
            try:
                return status, json.loads(payload)
            except ValueError:
                pass
        return status, payload


class TestMonitorAdd(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.h = _Http()
        self.h.setUp()
        self._call = self.h._call

    def tearDown(self):
        self.h.tearDown()
        super().tearDown()

    def test_add_then_list_round_trip(self):
        """add 之后 list 必须能看到该工具（写读一致）。"""
        st, body = self._call("POST", "/api/v1/monitor/add",
                              {"source_url": _TOOL, "name": _TOOL_NAME})
        self.assertEqual(st, 200)
        self.assertTrue(body.get("success"), f"add 应成功：{body}")

        st, listed = self._call("GET", "/api/v1/monitor/list")
        self.assertEqual(st, 200)
        tools = listed.get("tools")
        self.assertIsInstance(tools, (list, dict))
        flat = json.dumps(tools, ensure_ascii=False)
        self.assertIn(_TOOL_NAME, flat, f"list 应包含刚加入的工具：{tools}")

    def test_add_without_source_url_is_400(self):
        """缺 source_url 必须 400，不能吞成 200 空结果（假绿入口）。"""
        st, body = self._call("POST", "/api/v1/monitor/add", {"name": _TOOL_NAME})
        self.assertEqual(st, 400)
        self.assertIn("error", body)

    def test_add_twice_is_idempotent_update(self):
        """重复 add 同一条目应更新名称而不是重复登记。"""
        for name in (_TOOL_NAME, "renamed-tool"):
            st, body = self._call("POST", "/api/v1/monitor/add",
                                  {"source_url": _TOOL, "name": name})
            self.assertEqual(st, 200, body)
        st, listed = self._call("GET", "/api/v1/monitor/list")
        flat = json.dumps(listed.get("tools"), ensure_ascii=False)
        self.assertIn("renamed-tool", flat)
        self.assertNotIn(_TOOL_NAME, flat)

    def test_remove_then_list_empty(self):
        """remove 必须真把条目清掉（只写不收 = 本仓要治的病）。"""
        self._call("POST", "/api/v1/monitor/add",
                   {"source_url": _TOOL, "name": _TOOL_NAME})
        st, body = self._call("POST", "/api/v1/monitor/remove",
                              {"source_url": _TOOL})
        self.assertEqual(st, 200, body)
        self.assertTrue(body.get("success"), body)
        st, listed = self._call("GET", "/api/v1/monitor/list")
        self.assertEqual(st, 200)
        self.assertNotIn(_TOOL_NAME,
                         json.dumps(listed.get("tools"), ensure_ascii=False))


class TestMonitorCheck(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.h = _Http()
        self.h.setUp()
        self._call = self.h._call

    def tearDown(self):
        self.h.tearDown()
        super().tearDown()

    def test_check_all_on_empty_list_makes_no_network_call(self):
        """零监控项时必须短路：不打 GitHub API。

        若未来把网络调用挪到短路判断之前，CI 会因外网抖动出现与本仓代码
        无关的红 —— 这类红最伤信誉，故固定下来。
        """
        with mock.patch.object(S, "check_version_change") as cv, \
             mock.patch.object(S, "check_all_monitored",
                               return_value=[]) as cam:
            st, body = self._call("POST", "/api/v1/monitor/check", {})
            self.assertEqual(st, 200, body)
            self.assertTrue(body.get("success"))
            self.assertEqual(body.get("results"), [])
            self.assertEqual(body.get("total"), 0)
            self.assertEqual(cv.call_count, 0, "零监控项却打了单仓库检查")
            self.assertEqual(cam.call_count, 1)

    def test_check_single_tool_calls_version_check(self):
        """带 source_url 时应走单仓库检查，且返回其结果（此处打桩，不联网）。"""
        stub = {"success": True, "tool": _TOOL, "has_changes": False}
        with mock.patch.object(S, "check_version_change", return_value=stub) as cv:
            st, body = self._call("POST", "/api/v1/monitor/check",
                                  {"source_url": _TOOL})
            self.assertEqual(st, 200, body)
            self.assertFalse(body.get("has_changes"))
            cv.assert_called_once_with(_TOOL)

    def test_check_batch_returns_total(self):
        """批量检查必须回报 total，且与 results 长度一致。"""
        stub = [{"tool": "a", "has_changes": True}, {"tool": "b", "has_changes": False}]
        with mock.patch.object(S, "check_all_monitored", return_value=stub):
            st, body = self._call("POST", "/api/v1/monitor/check", {})
            self.assertEqual(st, 200, body)
            self.assertEqual(len(body.get("results", [])), 2)
            self.assertEqual(body.get("total"), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
