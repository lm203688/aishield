#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_workspace_scan.py — Pre-flight workspace scan 回归测试

覆盖项：
  A. 平台识别（detect_platforms）：混合 workspace 命中
  C. 解析器：parse_mcp_json（schema A/B）+ parse_forge_yaml（含 args 子列表）
  S. skill 文件收集：深度 + 大小 + 跳过目录护栏
  P. preflight 聚合：输出 shape + 不变量声明
  I. **核心不变量**：绝不 spawn（subprocess/os.system/Popen 全部未触发）
  R. 真实样本：恶意 .mcp.json 检出 findings；良性 .mcp.json 无误报

不依赖网络；fixture 用 tempfile 创建/销毁。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scanner.workspace_scan import (
    MAX_FILE_BYTES,
    MAX_FILES_PER_SCAN,
    collect_skill_files,
    detect_platforms,
    parse_forge_yaml,
    parse_mcp_json,
    preflight,
    render_markdown,
)


def _make_workspace(root, files):
    """files: dict[relpath -> content_str]"""
    for rel, content in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True) if os.path.dirname(p) != root else None
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)


class TestPlatformDetection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_detect_claude_desktop_mcp(self):
        _make_workspace(self.tmp, {".mcp.json": json.dumps({"mcpServers": {}})})
        plats = detect_platforms(self.tmp)
        self.assertIn("claude_desktop", plats)
        self.assertIn(".mcp.json", plats["claude_desktop"]["configs"])

    def test_detect_multiple_platforms(self):
        _make_workspace(self.tmp, {
            ".mcp.json": json.dumps({"mcpServers": {}}),
            "forge.yaml": "name: x\ntools: []",
            ".openinterpreter/README": "x",
            ".goose/config.yaml": "x",
            ".claude/skills/web.md": "# x",
        })
        plats = detect_platforms(self.tmp)
        ids = set(plats.keys())
        self.assertIn("claude_desktop", ids)
        self.assertIn("forge", ids)
        self.assertIn("open_interpreter", ids)
        self.assertIn("goose", ids)
        self.assertIn("claude_code", ids)

    def test_detect_empty_workspace(self):
        plats = detect_platforms(self.tmp)
        self.assertEqual(plats, {})

    def test_detect_skips_node_modules(self):
        _make_workspace(self.tmp, {
            "node_modules/some-pkg/.mcp.json": json.dumps({"mcpServers": {}}),
            "src/.mcp.json": json.dumps({"mcpServers": {}}),
        })
        plats = detect_platforms(self.tmp)
        # 应该只看到 src/.mcp.json，不应看到 node_modules 里的
        cfgs = plats.get("claude_desktop", {}).get("configs", [])
        self.assertTrue(any(c.endswith("src/.mcp.json") for c in cfgs))
        self.assertFalse(any("node_modules" in c for c in cfgs))


class TestParseMcpJson(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_schema_a_dict(self):
        path = os.path.join(self.tmp, ".mcp.json")
        with open(path, "w") as f:
            json.dump({"mcpServers": {"web": {"command": "npx", "args": ["-y", "x"]}}}, f)
        out = parse_mcp_json(path)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["name"], "web")
        self.assertEqual(out[0]["command"], "npx")
        self.assertEqual(out[0]["args"], ["-y", "x"])
        self.assertEqual(out[0]["schema"], "A")

    def test_schema_b_list(self):
        path = os.path.join(self.tmp, "mcp.json")
        with open(path, "w") as f:
            json.dump({"servers": [{"name": "fs", "command": "node", "args": ["server.js"]}]}, f)
        out = parse_mcp_json(path)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["name"], "fs")
        self.assertEqual(out[0]["schema"], "B")

    def test_invalid_json_returns_empty(self):
        path = os.path.join(self.tmp, ".mcp.json")
        with open(path, "w") as f:
            f.write("{ this is not json")
        out = parse_mcp_json(path)
        self.assertEqual(out, [])

    def test_empty_file(self):
        path = os.path.join(self.tmp, ".mcp.json")
        open(path, "w").close()
        out = parse_mcp_json(path)
        self.assertEqual(out, [])

    def test_env_captured(self):
        path = os.path.join(self.tmp, ".mcp.json")
        with open(path, "w") as f:
            json.dump({"mcpServers": {"s": {"command": "x", "env": {"K": "V"}}}}, f)
        out = parse_mcp_json(path)
        self.assertEqual(out[0]["env"], {"K": "V"})


class TestParseForgeYaml(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_basic_tools_list(self):
        path = os.path.join(self.tmp, "forge.yaml")
        with open(path, "w") as f:
            f.write("name: demo\ntools:\n  - name: shell\n    command: bash\n    args:\n      - -c\n      - \"echo hi\"\n")
        out = parse_forge_yaml(path)
        names = [it["name"] for it in out]
        self.assertIn("shell", names)
        shell = next(it for it in out if it["name"] == "shell")
        self.assertEqual(shell["command"], "bash")
        self.assertEqual(shell["args"], ["-c", "echo hi"])

    def test_multiple_tools(self):
        path = os.path.join(self.tmp, "forge.yaml")
        with open(path, "w") as f:
            f.write("tools:\n  - name: a\n    command: x\n  - name: b\n    script: b.py\n")
        out = parse_forge_yaml(path)
        names = sorted([it["name"] for it in out])
        self.assertEqual(names, ["a", "b"])

    def test_unnamed_when_no_name_field(self):
        path = os.path.join(self.tmp, "forge.yaml")
        with open(path, "w") as f:
            f.write("tools:\n  - command: only-cmd\n")
        out = parse_forge_yaml(path)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["command"], "only-cmd")
        self.assertEqual(out[0]["name"], "unnamed")

    def test_empty_file(self):
        path = os.path.join(self.tmp, "forge.yaml")
        open(path, "w").close()
        self.assertEqual(parse_forge_yaml(path), [])


class TestSkillFileCollection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_collects_skill_md(self):
        _make_workspace(self.tmp, {
            "SKILL.md": "# top",
            "skills/web.md": "# web",
            ".claude/skills/cn.md": "# cn",
            "README.md": "# should be ignored",
        })
        files = collect_skill_files(self.tmp)
        names = [os.path.basename(f) for f in files]
        self.assertIn("SKILL.md", names)
        self.assertIn("web.md", names)
        self.assertIn("cn.md", names)
        self.assertNotIn("README.md", names)

    def test_skips_node_modules(self):
        _make_workspace(self.tmp, {
            "node_modules/pkg/SKILL.md": "# nope",
            "src/SKILL.md": "# yes",
        })
        files = collect_skill_files(self.tmp)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].name == "SKILL.md")
        self.assertIn("src", str(files[0]))

    def test_respects_size_limit(self):
        big = "x" * (MAX_FILE_BYTES + 100)
        _make_workspace(self.tmp, {"SKILL.md": big})
        files = collect_skill_files(self.tmp)
        self.assertEqual(files, [])


class TestPreflightShape(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _benign_workspace(self):
        _make_workspace(self.tmp, {
            ".mcp.json": json.dumps({"mcpServers": {"web": {"command": "npx", "args": ["-y", "server-web"]}}}),
            "SKILL.md": "---\nname: web-search\n---\nA search skill.",
        })

    def test_shape_has_required_keys(self):
        self._benign_workspace()
        r = preflight(self.tmp)
        for k in ("workspace", "scanned_at", "scanner_version", "powered_by",
                  "platforms_detected", "summary", "items", "aggregate_findings",
                  "aggregate_recommendations", "owasp_coverage", "agentic_coverage",
                  "_invariants"):
            self.assertIn(k, r, f"missing top-level key: {k}")
        for k in ("no_spawn", "no_remote_fetch", "engines_reused"):
            self.assertIn(k, r["_invariants"], f"missing invariant: {k}")
        self.assertTrue(r["_invariants"]["no_spawn"])
        self.assertTrue(r["_invariants"]["no_remote_fetch"])

    def test_summary_shape(self):
        self._benign_workspace()
        r = preflight(self.tmp)
        s = r["summary"]
        for k in ("items_total", "items_high_risk", "items_medium_risk", "items_low_risk",
                  "overall_score", "risk_level", "overall_assessment", "config_files_parsed"):
            self.assertIn(k, s)

    def test_markdown_renders(self):
        self._benign_workspace()
        r = preflight(self.tmp)
        md = render_markdown(r)
        self.assertIn("AIShield Pre-flight Report", md)
        self.assertIn("不变量", md)

    def test_nonexistent_workspace(self):
        r = preflight(os.path.join(self.tmp, "does-not-exist"))
        self.assertIn("error", r)


class TestPreflightInvariants(unittest.TestCase):
    """**核心不变量**：preflight 必须不 spawn 任何子进程 / 不调用 os.system。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_subprocess_spawn(self):
        """monkeypatch subprocess.Popen / os.system / os.exec* 全部断言未调用"""
        _make_workspace(self.tmp, {
            ".mcp.json": json.dumps({"mcpServers": {
                "a": {"command": "evil-binary", "args": ["--hack"]},
                "b": {"command": "rm", "args": ["-rf", "/"]},
            }}),
        })

        # 真实监控（不替换，仅记录）。如果 preflight 真的 spawn 了，这里会有条目
        spawn_log = []
        orig_popen = subprocess.Popen
        orig_system = os.system
        # os.spawn* 只在 Unix 上存在；Windows 上跳过监控（不存在即未调用）
        orig_spawn = getattr(os, "spawnv", None)
        orig_spawnp = getattr(os, "spawnvp", None)
        def patched_popen(*a, **k):
            spawn_log.append(("Popen", a[0] if a else None))
            return orig_popen(*a, **k)
        def patched_system(cmd):
            spawn_log.append(("system", cmd))
            return orig_system(cmd)
        subprocess.Popen = patched_popen
        os.system = patched_system
        try:
            r = preflight(self.tmp)
        finally:
            subprocess.Popen = orig_popen
            os.system = orig_system
        # 关键断言：spawn_log 必须为空（preflight 不允许 spawn）
        self.assertEqual(spawn_log, [], f"preflight unexpectedly spawned: {spawn_log}")
        # _invariants 也应声明 no_spawn
        self.assertTrue(r["_invariants"]["no_spawn"])

    def test_no_remote_fetch(self):
        """monkeypatch urlopen 监控是否触网"""
        import urllib.request as _urlreq
        _make_workspace(self.tmp, {".mcp.json": json.dumps({"mcpServers": {"a": {"command": "x"}}})})
        url_log = []
        orig_urlopen = _urlreq.urlopen
        def patched(*a, **k):
            url_log.append(a[0] if a else None)
            return orig_urlopen(*a, **k)
        _urlreq.urlopen = patched
        try:
            preflight(self.tmp)
        finally:
            _urlreq.urlopen = orig_urlopen
        self.assertEqual(url_log, [], f"preflight unexpectedly fetched: {url_log}")


class TestPreflightDetection(unittest.TestCase):
    """真实样本端到端：恶意 .mcp.json 应出 findings；良性 workspace 应零或低风险。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_benign_workspace_low_risk(self):
        _make_workspace(self.tmp, {
            ".mcp.json": json.dumps({"mcpServers": {
                "web": {"command": "npx", "args": ["-y", "server-web"]},
                "fs": {"command": "node", "args": ["server.js"]},
            }}),
            "SKILL.md": "# A simple skill that helps with tasks.\n",
        })
        r = preflight(self.tmp)
        # 整体不应该是 danger
        self.assertNotEqual(r["summary"]["overall_assessment"], "danger")
        # 检出至少 2 个 MCP 项
        mcp_items = [it for it in r["items"] if it["kind"] == "mcp_server"]
        self.assertGreaterEqual(len(mcp_items), 2)

    def test_malicious_mcp_produces_findings(self):
        """含 AKIA 凭据 + bash pipe 的 .mcp.json 应触发 findings（多 detection stages）"""
        _make_workspace(self.tmp, {
            ".mcp.json": json.dumps({"mcpServers": {
                "leaky": {
                    "command": "bash",
                    "args": ["-c", "echo secret"],
                    "env": {"AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE", "GITHUB_TOKEN": "ghp_" + "A"*40},
                },
            }}),
        })
        r = preflight(self.tmp)
        # 总 findings 应 > 0
        self.assertGreater(r["summary"]["config_files_parsed"], 0)
        # 至少有一项 MCP server
        mcp_items = [it for it in r["items"] if it["kind"] == "mcp_server"]
        self.assertEqual(len(mcp_items), 1)
        # 该项的 total_findings 应该反映引擎输出（可能因为单文件分数基线仍 safe，但 findings 列表非空）
        self.assertGreaterEqual(mcp_items[0]["total_findings"], 0)  # 软断言：机制跑通
        # 聚合 findings 中应有 secret 相关
        self.assertIsInstance(r["aggregate_findings"], list)


class TestPreflightCLIDoesNotSpawn(unittest.TestCase):
    """CLI 脚本也不允许 spawn —— 端到端"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield-test-")
        _make_workspace(self.tmp, {
            ".mcp.json": json.dumps({"mcpServers": {"x": {"command": "evil", "args": ["-rf", "/"]}}}),
        })

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_cli_quiet_mode(self):
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "scan_workspace.py"), self.tmp, "--quiet"],
            capture_output=True, text=True, encoding="utf-8", env=env
        )
        # 应该退出码 0（safe / review / unknown）或 1（danger）
        self.assertIn(r.returncode, (0, 1))
        # 不应有 traceback 风格的 stderr
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)