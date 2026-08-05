"""
多客户端 MCP 配置自动发现与配置级威胁分析 — 测试

三类：
  A. 发现与解析（路径推导 / 多 schema 兼容 / fail-safe）
  B. 单服务器风险检测（提权/拉包/凭证/传输/项目信任）
  C. 跨服务器分析（命名空间遮蔽 / 毒性组合流）+ 误报控制
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scanner import client_discovery as cd


def _types(findings):
    return {f["type"] for f in findings}


# ---------------------------------------------------------------- A. 发现与解析

class TestDiscovery(unittest.TestCase):

    def test_windows_paths_include_appdata_clients(self):
        found = cd.discover_client_configs(
            home="C:/Users/t", appdata="C:/Users/t/AppData/Roaming",
            platform_name="win32", exists=lambda p: False,
        )
        paths = " ".join(f["path"] for f in found)
        self.assertIn("AppData/Roaming/Claude/claude_desktop_config.json", paths)
        self.assertIn(".cursor/mcp.json", paths)
        self.assertTrue(any(f["client"] == "Windsurf" for f in found))

    def test_macos_paths_use_application_support(self):
        found = cd.discover_client_configs(
            home="/Users/t", platform_name="darwin", exists=lambda p: False
        )
        paths = " ".join(f["path"] for f in found)
        self.assertIn("Library/Application Support/Claude", paths)

    def test_project_scope_only_when_project_root_given(self):
        without = cd.discover_client_configs(home="/h", exists=lambda p: False)
        self.assertFalse(any(f["scope"] == "project" for f in without))
        with_proj = cd.discover_client_configs(
            home="/h", project_root="/repo", exists=lambda p: False
        )
        self.assertTrue(any(f["scope"] == "project" for f in with_proj))
        self.assertTrue(any(f["path"].endswith("/repo/.mcp.json") for f in with_proj))

    def test_supports_at_least_eight_clients(self):
        clients = {p["client"] for p in cd.get_client_profiles()}
        self.assertGreaterEqual(len(clients), 8)

    def test_exists_flag_is_reported(self):
        found = cd.discover_client_configs(
            home="/h", platform_name="linux",
            exists=lambda p: p.endswith(".cursor/mcp.json"),
        )
        hits = [f for f in found if f["exists"]]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["client"], "Cursor")

    def test_no_duplicate_paths_per_client(self):
        found = cd.discover_client_configs(
            home="/h", platform_name="linux", project_root="/r", exists=lambda p: False
        )
        keys = [(f["client"], f["path"]) for f in found]
        self.assertEqual(len(keys), len(set(keys)))


class TestParsing(unittest.TestCase):

    def test_parses_mcpservers_schema(self):
        cfg = json.dumps({"mcpServers": {"fs": {"command": "node", "args": ["a.js"]}}})
        self.assertIn("fs", cd.parse_mcp_config(cfg))

    def test_parses_vscode_servers_schema(self):
        cfg = json.dumps({"servers": {"gh": {"command": "node"}}})
        self.assertIn("gh", cd.parse_mcp_config(cfg))

    def test_parses_zed_context_servers_and_nested_mcp(self):
        self.assertIn("z", cd.parse_mcp_config({"context_servers": {"z": {"command": "x"}}}))
        self.assertIn("n", cd.parse_mcp_config({"mcp": {"servers": {"n": {"command": "x"}}}}))

    def test_malformed_json_is_failsafe(self):
        self.assertEqual(cd.parse_mcp_config("{not json"), {})
        self.assertEqual(cd.parse_mcp_config(None), {})
        self.assertEqual(cd.parse_mcp_config("[]"), {})

    def test_non_dict_entries_are_skipped(self):
        cfg = {"mcpServers": {"good": {"command": "x"}, "bad": "oops"}}
        parsed = cd.parse_mcp_config(cfg)
        self.assertEqual(list(parsed), ["good"])


# ------------------------------------------------- B. 单服务器风险检测

class TestServerEntryRisks(unittest.TestCase):

    def test_detects_elevated_privilege_launch(self):
        f = cd.analyze_server_entry("root-fs", {"command": "sudo", "args": ["node", "s.js"]})
        self.assertIn("elevated_privilege_launch", _types(f))
        self.assertEqual(
            [x["severity"] for x in f if x["type"] == "elevated_privilege_launch"], ["critical"]
        )

    def test_detects_stdio_command_exposure(self):
        f = cd.analyze_server_entry("s", {"command": "node", "args": ["server.js"]})
        self.assertIn("stdio_command_execution_exposure", _types(f))

    def test_remote_server_has_no_stdio_exposure_finding(self):
        f = cd.analyze_server_entry("r", {"url": "https://api.example.com/mcp"})
        self.assertNotIn("stdio_command_execution_exposure", _types(f))

    def test_detects_unpinned_runtime_package_fetch(self):
        f = cd.analyze_server_entry(
            "weather", {"command": "npx", "args": ["-y", "weather-mcp"]}
        )
        hits = [x for x in f if x["type"] == "runtime_package_fetch"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["severity"], "high")

    def test_pinned_version_does_not_flag_runtime_fetch(self):
        f = cd.analyze_server_entry(
            "weather", {"command": "npx", "args": ["weather-mcp@1.2.3"]}
        )
        self.assertNotIn("runtime_package_fetch", _types(f))

    def test_latest_tag_is_flagged_even_without_auto_yes(self):
        f = cd.analyze_server_entry("w", {"command": "uvx", "args": ["some-mcp@latest"]})
        hits = [x for x in f if x["type"] == "runtime_package_fetch"]
        self.assertEqual(hits[0]["severity"], "high")

    def test_detects_shell_interpreter_launch(self):
        f = cd.analyze_server_entry("x", {"command": "bash", "args": ["-c", "node s.js"]})
        self.assertIn("shell_interpreter_launch", _types(f))

    def test_detects_untrusted_launch_source(self):
        f = cd.analyze_server_entry(
            "x", {"command": "node", "args": ["https://evil.example.com/payload.js"]}
        )
        self.assertIn("untrusted_launch_source", _types(f))

    def test_detects_plaintext_credentials(self):
        f = cd.analyze_server_entry("gh", {
            "command": "node",
            "env": {"GITHUB_TOKEN": "ghp_" + "a" * 30},
        })
        hits = [x for x in f if x["type"] == "credential_exposure_in_config"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["severity"], "critical")
        # 证据必须脱敏，绝不回显原始凭证
        self.assertNotIn("ghp_", hits[0]["evidence"])

    def test_placeholder_env_values_are_not_flagged(self):
        for val in ("${GITHUB_TOKEN}", "<your-token>", "your-api-key-here",
                    "changeme", "$GITHUB_TOKEN"):
            f = cd.analyze_server_entry("gh", {"command": "node", "env": {"TOKEN": val}})
            self.assertNotIn("credential_exposure_in_config", _types(f),
                             f"占位符被误报: {val}")

    def test_detects_db_connection_string_with_password(self):
        f = cd.analyze_server_entry("db", {
            "command": "node",
            "env": {"DATABASE_URL": "postgres://admin:s3cretpw@db.example.com:5432/app"},
        })
        self.assertIn("credential_exposure_in_config", _types(f))

    def test_detects_insecure_http_transport(self):
        f = cd.analyze_server_entry("r", {"url": "http://api.example.com/mcp"})
        self.assertIn("insecure_transport", _types(f))

    def test_localhost_http_is_not_insecure_transport(self):
        f = cd.analyze_server_entry("r", {"url": "http://127.0.0.1:8080/mcp"})
        self.assertNotIn("insecure_transport", _types(f))

    def test_detects_remote_server_without_auth(self):
        f = cd.analyze_server_entry("r", {"url": "https://api.example.com/mcp"})
        hits = [x for x in f if x["type"] == "remote_server_without_auth"]
        self.assertEqual(hits[0]["severity"], "high")

    def test_remote_with_auth_header_is_not_flagged(self):
        f = cd.analyze_server_entry("r", {
            "url": "https://api.example.com/mcp",
            "headers": {"Authorization": "Bearer ${TOKEN}"},
        })
        self.assertNotIn("remote_server_without_auth", _types(f))

    def test_private_host_without_auth_is_only_medium(self):
        f = cd.analyze_server_entry("r", {"url": "https://10.0.0.5/mcp"})
        hits = [x for x in f if x["type"] == "remote_server_without_auth"]
        self.assertEqual(hits[0]["severity"], "medium")

    def test_project_scope_raises_trust_risk(self):
        f = cd.analyze_server_entry("s", {"command": "node"}, source=".mcp.json",
                                    scope="project")
        self.assertIn("project_config_trust_risk", _types(f))
        f2 = cd.analyze_server_entry("s", {"command": "node"}, scope="user")
        self.assertNotIn("project_config_trust_risk", _types(f2))

    def test_findings_carry_owasp_and_remediation(self):
        f = cd.analyze_server_entry("x", {"command": "sudo", "args": ["node"]})
        for item in f:
            self.assertTrue(item.get("owasp_category"))
            self.assertTrue(item.get("remediation"))
            self.assertEqual(item.get("server"), "x")


# ------------------------------------------- C. 跨服务器分析与集成

class TestCapabilities(unittest.TestCase):

    def test_infers_filesystem_and_network(self):
        caps = cd.infer_capabilities("filesystem", {"command": "npx",
                                                    "args": ["@x/filesystem"]})
        self.assertIn("filesystem", caps)
        caps2 = cd.infer_capabilities("fetch", {"command": "npx", "args": ["mcp-fetch"]})
        self.assertIn("network_out", caps2)

    def test_remote_server_implies_network(self):
        self.assertIn("network_out", cd.infer_capabilities("x", {"url": "https://a/mcp"}))

    def test_inline_plaintext_credential_implies_secrets(self):
        caps = cd.infer_capabilities("x", {"command": "node",
                                           "env": {"GITHUB_TOKEN": "ghp_" + "c" * 30}})
        self.assertIn("secrets", caps)

    def test_env_reference_does_not_imply_secrets(self):
        """仅凭键名判定会让毒性流对几乎所有合法配置恒亮 —— 必须按值判定。"""
        for val in ("${GITHUB_TOKEN}", "<your-token>", "changeme"):
            caps = cd.infer_capabilities("x", {"command": "node",
                                               "env": {"API_TOKEN": val}})
            self.assertNotIn("secrets", caps, f"env 引用被误判为持有密钥: {val}")

    def test_secret_store_server_implies_secrets(self):
        self.assertIn("secrets",
                      cd.infer_capabilities("vault", {"command": "npx",
                                                      "args": ["vault-mcp@1.0.0"]}))

    def test_plain_server_has_no_capabilities(self):
        self.assertEqual(cd.infer_capabilities("calc", {"command": "node",
                                                        "args": ["calc.js"]}), set())


class TestCrossServer(unittest.TestCase):

    def test_detects_server_name_collision(self):
        inv = [
            {"name": "github", "client": "Cursor", "file": "a.json", "capabilities": set()},
            {"name": "GitHub", "client": "VS Code", "file": "b.json", "capabilities": set()},
        ]
        f = cd.analyze_cross_server(inv)
        self.assertIn("server_name_collision", _types(f))

    def test_unique_names_do_not_collide(self):
        inv = [
            {"name": "a", "client": "c", "file": "f", "capabilities": set()},
            {"name": "b", "client": "c", "file": "f", "capabilities": set()},
        ]
        self.assertNotIn("server_name_collision", _types(cd.analyze_cross_server(inv)))

    def test_detects_secrets_plus_network_toxic_flow(self):
        inv = [
            {"name": "vault", "client": "c", "file": "f", "capabilities": {"secrets"}},
            {"name": "fetch", "client": "c", "file": "f", "capabilities": {"network_out"}},
        ]
        f = cd.analyze_cross_server(inv)
        flows = [x for x in f if x["type"] == "cross_server_toxic_flow"]
        pair = [x for x in flows if x["capability_pair"] == ["secrets", "network_out"]]
        self.assertTrue(pair)
        # secrets 已按「内联明文凭证」判定，外泄链路具体存在 → 升 high
        self.assertEqual(pair[0]["severity"], "high")

    def test_no_toxic_flow_when_capability_missing(self):
        inv = [{"name": "fs", "client": "c", "file": "f", "capabilities": {"filesystem"}}]
        self.assertNotIn("cross_server_toxic_flow", _types(cd.analyze_cross_server(inv)))

    def test_empty_inventory_is_safe(self):
        self.assertEqual(cd.analyze_cross_server([]), [])


class TestScanIntegration(unittest.TestCase):

    def _cfg(self):
        return json.dumps({"mcpServers": {
            "filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"]},
            "fetch": {"command": "npx", "args": ["mcp-fetch@1.0.0"]},
            "gh": {"command": "node", "args": ["gh.js"],
                   "env": {"GITHUB_TOKEN": "ghp_" + "b" * 30}},
        }})

    def test_scan_returns_inventory_findings_summary(self):
        res = cd.scan_client_configs({"claude_desktop_config.json": self._cfg()})
        self.assertEqual(res["summary"]["servers_found"], 3)
        self.assertEqual(res["summary"]["files_parsed"], 1)
        self.assertGreater(res["summary"]["findings_total"], 0)
        self.assertIn("credential_exposure_in_config", _types(res["findings"]))

    def test_scan_result_is_json_serializable(self):
        res = cd.scan_client_configs({"a.json": self._cfg()})
        json.dumps(res)  # capabilities 必须已从 set 转为 list

    def test_config_score_drops_with_critical_findings(self):
        clean = cd.scan_client_configs({"a.json": json.dumps(
            {"mcpServers": {"calc": {"command": "/usr/local/bin/calc-mcp"}}}
        )})
        dirty = cd.scan_client_configs({"a.json": self._cfg()})
        self.assertGreater(clean["summary"]["config_score"],
                           dirty["summary"]["config_score"])

    def test_score_is_bounded(self):
        res = cd.scan_client_configs({"a.json": self._cfg()})
        self.assertGreaterEqual(res["summary"]["config_score"], 0)
        self.assertLessEqual(res["summary"]["config_score"], 100)

    def test_empty_input_is_safe(self):
        res = cd.scan_client_configs({})
        self.assertEqual(res["summary"]["servers_found"], 0)
        self.assertEqual(res["findings"], [])

    def test_discover_and_scan_never_executes_commands(self):
        """核心不变量：发现+扫描全程不得 spawn 任何子进程。"""
        import subprocess

        calls = []
        for attr in ("Popen", "run", "call", "check_output"):
            orig = getattr(subprocess, attr)
            setattr(subprocess, attr,
                    lambda *a, _n=attr, **k: calls.append(_n))
            self.addCleanup(setattr, subprocess, attr, orig)

        cfg = self._cfg()
        cd.discover_and_scan(
            home="/h", platform_name="linux",
            read=lambda p: cfg,
        )
        self.assertEqual(calls, [], "扫描过程中不得执行任何被扫命令")

    def test_discover_and_scan_reports_supported_clients(self):
        res = cd.discover_and_scan(home="/h", platform_name="linux",
                                   read=lambda p: "{}")
        self.assertGreaterEqual(res["summary"]["clients_supported"], 8)
        self.assertIn("discovered", res)

    def test_unreadable_file_is_skipped_not_fatal(self):
        def boom(path):
            raise IOError("permission denied")

        res = cd.discover_and_scan(home="/h", platform_name="linux", read=boom)
        self.assertEqual(res["summary"]["servers_found"], 0)


class TestScoringDiscrimination(unittest.TestCase):
    """评分器必须能区分好坏 —— 恒 0 或恒 100 的门禁等于没有门禁。"""

    def test_clean_config_scores_high(self):
        score, _ = cd.compute_config_score([])
        self.assertEqual(score, 100)

    def test_medium_penalty_is_capped_by_fleet_size(self):
        """20 台机器各 1 条 medium 不应把分数打到 0。"""
        many = [{"severity": "medium"} for _ in range(40)]
        score, _ = cd.compute_config_score(many)
        self.assertGreaterEqual(score, 75)

    def test_info_findings_cost_nothing(self):
        score, _ = cd.compute_config_score([{"severity": "info"} for _ in range(50)])
        self.assertEqual(score, 100)

    def test_criticals_drive_score_down_fast(self):
        score, _ = cd.compute_config_score([{"severity": "critical"} for _ in range(5)])
        self.assertEqual(score, 0)

    def test_benign_and_malicious_scores_are_separated(self):
        benign = [{"severity": "medium"}] * 15 + [{"severity": "info"}] * 20
        evil = [{"severity": "critical"}] * 3 + [{"severity": "high"}] * 4
        b, _ = cd.compute_config_score(benign)
        m, _ = cd.compute_config_score(evil)
        self.assertGreater(b - m, 50, "良性与恶意配置的分数必须显著分离")

    def test_stdio_exposure_is_info_not_noise(self):
        f = cd.analyze_server_entry("s", {"command": "node", "args": ["s.js"]})
        hits = [x for x in f if x["type"] == "stdio_command_execution_exposure"]
        self.assertEqual(hits[0]["severity"], "info")

    def test_toxic_flow_is_advisory_and_capped_at_medium(self):
        inv = [
            {"name": "fs", "client": "c", "file": "f", "capabilities": {"filesystem"}},
            {"name": "fetch", "client": "c", "file": "f", "capabilities": {"network_out"}},
        ]
        flows = [x for x in cd.analyze_cross_server(inv)
                 if x["type"] == "cross_server_toxic_flow"]
        self.assertTrue(flows)
        self.assertEqual(flows[0]["severity"], "medium")
        self.assertTrue(flows[0]["advisory"])

    def test_wildcard_bind_is_high(self):
        f = cd.analyze_server_entry("w", {"url": "http://0.0.0.0:9000/mcp"})
        hits = [x for x in f if x["type"] == "wildcard_bind"]
        self.assertEqual(hits[0]["severity"], "high")


class TestFalsePositiveControl(unittest.TestCase):
    """典型的良性真实配置不得产生 high/critical 噪声。"""

    BENIGN = {
        "pinned-local": {"command": "/usr/local/bin/my-mcp", "args": ["--stdio"]},
        "pinned-npx": {"command": "npx", "args": ["@scope/server-mcp@2.1.0"]},
        "env-ref": {"command": "node", "args": ["s.js"],
                    "env": {"API_KEY": "${MY_API_KEY}"}},
        "https-authed": {"url": "https://mcp.example.com/sse",
                         "headers": {"Authorization": "Bearer ${TOKEN}"}},
        "localhost": {"url": "http://localhost:3000/mcp",
                      "headers": {"X-Api-Key": "${K}"}},
    }

    def test_benign_configs_produce_no_high_or_critical(self):
        res = cd.scan_client_configs({"a.json": json.dumps({"mcpServers": self.BENIGN})})
        loud = [f for f in res["findings"] if f["severity"] in ("high", "critical")]
        self.assertEqual(loud, [], f"良性配置误报: {[f['type'] for f in loud]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
