"""
统一导出面（F3 收口）测试：目标端注册表 + 配置化 + 规格校验 + 脱敏。

要防的病：
  * 「导出器存在」≠「导出能用」：六个目标端必须**逐一实跑**并校验合规格，
    不是只看函数导得出来；
  * 目标端 headers 带 HEC token / API key，**绝不能进产物或日志**；
  * 校验函数不能是摆设 —— 用坏 builder 反向验证 validate 真的报错。

全部离线：导出不联网（投递是调用方的事）。
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scanner import export_registry as ex  # noqa: E402

FINDINGS = [
    {"rule_id": "ASI01-INJ-01", "type": "指令覆盖", "severity": "high",
     "description": "第1条指令被覆盖", "file": "a.py", "lines": "3", "col": "1",
     "owasp_category": "ASI01", "remediation": "改为白名单"},
    {"rule_id": "ASI04-01", "type": "越权", "severity": "critical",
     "description": "缺失鉴权", "file": "b.py", "lines": "9", "col": "2",
     "owasp_category": "ASI04", "remediation": "加鉴权", "cve": "CVE-2026-0001"},
]


class TestRegistry(unittest.TestCase):
    def test_expected_targets_registered(self):
        for name in ("nucleus", "splunk", "ocsf", "stix", "json", "csv"):
            self.assertIn(name, ex.TARGETS, "目标端 %s 没注册" % name)

    def test_every_target_exports_cleanly(self):
        """六个目标端逐一实跑 —— 只导函数不跑，等于没验。"""
        for name in sorted(ex.TARGETS):
            with self.subTest(target=name):
                r = ex.export_to(FINDINGS, name)
                self.assertTrue(r.ok, "%s 导出有问题: %s" % (name, r.issues))
                self.assertIsNotNone(r.payload)

    def test_unknown_target_rejected(self):
        with self.assertRaises(KeyError):
            ex.TargetConfig("x", "no-such-target")


class TestOcsfSpec(unittest.TestCase):
    def test_ocsf_fields_follow_spec(self):
        r = ex.export_to(FINDINGS, "ocsf")
        p = r.payload
        self.assertEqual(p["schema_version"], "1.1.0")
        self.assertEqual(p["class_uid"], 2001)
        self.assertEqual(p["class_name"], "Vulnerability Finding")
        self.assertEqual(p["count"], len(FINDINGS))
        self.assertIn("product", p["metadata"])

    def test_ocsf_severity_id_mapping(self):
        sev = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
        findings = [dict(FINDINGS[0], rule_id="R-%s" % s, severity=s, description="d-%s" % s)
                    for s in sev]
        p = ex.export_to(findings, "ocsf").payload
        got = {f["severity"]: f["severity_id"] for f in p["findings"]}
        for name, sid in sev.items():
            self.assertEqual(got[name.capitalize()], sid, "OCSF severity_id 映射错: %s" % name)

    def test_ocsf_warns_about_dropped_remediation(self):
        """规范装不下的字段要如实警告，别让用户以为丢了。"""
        r = ex.export_to(FINDINGS, "ocsf")
        self.assertTrue(any("remediation" in w for w in r.warnings),
                        "有 remediation 却没警告，用户会以为字段丢了")


class TestStixSpec(unittest.TestCase):
    def test_stix_bundle_shape(self):
        p = ex.export_to(FINDINGS, "stix").payload
        self.assertEqual(p["type"], "bundle")
        self.assertTrue(p["id"].startswith("bundle--"))
        kinds = [o["type"] for o in p["objects"]]
        self.assertEqual(kinds[0], "identity")
        self.assertEqual(kinds.count("vulnerability"), len(FINDINGS))

    def test_stix_ids_are_deterministic(self):
        """同一 rule_id 必须每次同一 STIX id —— SOAR 去重靠它。"""
        a = ex.export_to(FINDINGS, "stix").payload
        b = ex.export_to(FINDINGS, "stix").payload
        ids_a = [o["id"] for o in a["objects"] if o["type"] == "vulnerability"]
        ids_b = [o["id"] for o in b["objects"] if o["type"] == "vulnerability"]
        self.assertEqual(ids_a, ids_b, "STIX id 不稳定，SOAR 会重复建单")
        ext = [o["external_references"][0]["external_id"] for o in a["objects"]
               if o["type"] == "vulnerability"]
        self.assertEqual(ext, [f["rule_id"] for f in FINDINGS], "external_id 必须用稳定 rule_id")


class TestCsvAndJson(unittest.TestCase):
    def test_csv_header_and_rows(self):
        r = ex.export_to(FINDINGS, "csv")
        lines = r.payload.strip("\n").split("\n")
        self.assertEqual(len(lines), len(FINDINGS) + 1, "CSV 行数不符")
        self.assertIn("rule_id", lines[0])
        self.assertIn("ASI01-INJ-01", lines[1])

    def test_json_is_normalized(self):
        p = ex.export_to(FINDINGS, "json").payload
        self.assertEqual(p["count"], len(FINDINGS))
        self.assertEqual(p["findings"], FINDINGS)


class TestLegacyDelegation(unittest.TestCase):
    """nucleus/splunk 走 registry 后行为必须与旧实现一致（兼容红线）。"""

    def test_nucleus_keeps_rule_id_as_finding_number(self):
        p = ex.export_to(FINDINGS, "nucleus").payload
        self.assertEqual([f["finding_number"] for f in p["findings"]],
                         [f["rule_id"] for f in FINDINGS])

    def test_splunk_event_count(self):
        p = ex.export_to(FINDINGS, "splunk").payload
        self.assertEqual(p["event_count"], len(FINDINGS))
        self.assertEqual([e["rule_id"] for e in p["events"]], [f["rule_id"] for f in FINDINGS])


class TestTargetConfig(unittest.TestCase):
    def test_headers_are_redacted(self):
        cfg = ex.TargetConfig("siem", "splunk", endpoint="https://splunk:8088/services/collector",
                              headers={"Authorization": "Bearer sk-abcdef123456789",
                                       "X-Source": "aishield"})
        red = cfg.redact_headers()
        self.assertNotIn("sk-abcdef123456789", json.dumps(red), "明文凭据泄漏到 headers")
        self.assertTrue(red["Authorization"].startswith("***MASKED***"))
        self.assertEqual(red["X-Source"], "aishield", "非敏感头不该被乱改")

    def test_to_dict_never_exposes_raw_secret(self):
        cfg = ex.TargetConfig("siem", "splunk", headers={"X-Api-Key": "supersecretvalue12345"})
        self.assertNotIn("supersecretvalue12345", json.dumps(cfg.to_dict(), ensure_ascii=False))

    def test_secret_inside_finding_is_caught(self):
        """产物里带凭据形态的串必须报出来（弱探针，但比不查强）。"""
        bad = [dict(FINDINGS[0], description="curl -H 'Authorization: Bearer abcdef123456'")]
        r = ex.export_to(bad, "splunk")
        self.assertFalse(r.ok, "产物含 Bearer 凭据却没报")
        self.assertTrue(any("凭据" in i for i in r.issues))

    def test_mask_secret_keeps_only_tail(self):
        m = ex.mask_secret("sk-abcdef123456789")
        self.assertNotIn("abcdef", m.replace("***MASKED***", ""))
        self.assertTrue(m.endswith("6789"))

    def test_config_file_roundtrip_and_batch(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "targets.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump({"targets": [
                    {"name": "siem", "target": "splunk",
                     "endpoint": "https://splunk:8088/services/collector",
                     "headers": {"Authorization": "Bearer topsecret123456"}},
                    {"name": "off", "target": "json", "enabled": False},
                ]}, fh, ensure_ascii=False)
            cfgs = ex.load_config(p)
            self.assertEqual([c.name for c in cfgs], ["siem", "off"])
            self.assertFalse(cfgs[1].enabled)
            results = ex.batch_export(FINDINGS, cfgs)
            self.assertEqual([r.name for r in results], ["siem"], "disabled 目标端没被跳过")

    def test_disable_clean_csv(self):
        self.assertTrue(ex.export_to(FINDINGS, "csv").ok)
        self.assertTrue(ex.export_to(FINDINGS, "csv").payload.startswith("rule_id,"))


class TestValidationIsNotDecoration(unittest.TestCase):
    """反向用例：校验必须真能拦下坏产物，否则就是装饰。"""

    def test_missing_required_field_is_reported(self):
        ex.register_target("_bad_missing", lambda f, c: {"schema": "x"},
                           "Bad", "1", "json", required=("schema", "findings"))
        try:
            r = ex.export_to(FINDINGS, "_bad_missing")
            self.assertFalse(r.ok)
            self.assertTrue(any("findings" in i for i in r.issues))
        finally:
            ex.TARGETS.pop("_bad_missing", None)

    def test_build_exception_is_surfaced_not_swallowed(self):
        def boom(findings, cfg):
            raise RuntimeError("format blew up")

        ex.register_target("_boom", boom, "Boom", "1", "json", required=())
        try:
            r = ex.export_to(FINDINGS, "_boom")
            self.assertFalse(r.ok)
            self.assertIn("build_failed", r.issues)
            self.assertIsNone(r.payload, "构建失败不该给出半个 payload")
        finally:
            ex.TARGETS.pop("_boom", None)

    def test_text_target_validates_header_columns(self):
        ex.register_target("_bad_csv", lambda f, c: "a,b\n1,2\n", "BadCsv", "1", "text",
                           required=("rule_id",))
        try:
            r = ex.export_to(FINDINGS, "_bad_csv")
            self.assertFalse(r.ok)
            self.assertTrue(any("表头" in i for i in r.issues))
        finally:
            ex.TARGETS.pop("_bad_csv", None)


class TestCliScript(unittest.TestCase):
    def test_cli_lists_targets_and_audits(self):
        import subprocess
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script = os.path.join(repo, "scripts", "export_findings.py")
        out = subprocess.run([sys.executable, script, "--list"],
                             capture_output=True, text=True, cwd=repo)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("ocsf", out.stdout)
        with tempfile.TemporaryDirectory() as td:
            fp = os.path.join(td, "f.json")
            with open(fp, "w", encoding="utf-8") as fh:
                json.dump(FINDINGS, fh, ensure_ascii=False)
            r = subprocess.run([sys.executable, script, "--findings", fp,
                                "--target", "json", "--audit-score", "--total-files", "3"],
                               capture_output=True, text=True, cwd=repo)
            self.assertEqual(r.returncode, 0, "CLI 审计失败: %s%s" % (r.stdout, r.stderr))
            self.assertIn("扣分账本闭合", r.stdout)


if __name__ == "__main__":
    unittest.main()
