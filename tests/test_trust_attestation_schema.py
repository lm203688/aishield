# -*- coding: utf-8 -*-
"""Trust Attestation 签发链路的契约测试。

**为什么必须有这个测试**（2026-10-06 实锤）
────────────────────────────────────────
线上 `POST /api/v1/attestations` 与 `/api/v1/attestations/from-scan` 长期返回
`{"error": "Schema validation failed: Schema not found"}`，而本地测试全绿。

根因：`api/trust_api.py:_load_attestation_schema()` 读的是
`schema/trust-attestation-v1.json`，该文件**在本地存在、在 main 上不存在**
（远端 404，也没被 .gitignore 排除 —— 就是某次提交时没带上）。
部署 tarball 来自 git checkout，于是服务器上永远少这一个文件：
**信任鉴证这根支柱在线上根本签不出凭证**，而"本地跑得好好的"。

教训与 feeds.xml 那次同形：**产物受测、它依赖的输入不在门禁里**。
所以这里钉的不是"函数能不能跑"，而是"签发所需的文件是否真的随仓库发布"。
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SCHEMA_PATH = os.path.join(ROOT, "schema", "trust-attestation-v1.json")


class TestAttestationSchemaShips(unittest.TestCase):
    """schema 文件必须随仓库发布 —— 缺了它线上签发全挂。"""

    def test_schema_file_exists(self):
        self.assertTrue(
            os.path.exists(SCHEMA_PATH),
            "schema/trust-attestation-v1.json 不存在：线上所有 attestation 签发端点"
            "都会返回 'Schema not found'（部署产物来自 git checkout，本地有、远端没有 "
            "＝ 线上一直签不出凭证）。",
        )

    def test_schema_is_valid_json_with_required(self):
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            sch = json.load(f)
        self.assertIn("required", sch)
        # _validate_attestation_schema() 逐字校验这六个字段，schema 必须覆盖它们，
        # 否则会出现"文件在、校验仍失败"的第二种断链。
        for field in ("schema", "issuer", "subject", "verdict", "coverage", "attestation"):
            self.assertIn(field, sch["required"], f"schema 未要求字段 {field}")

    def test_loader_returns_schema(self):
        import api.trust_api as T
        self.assertIsNotNone(
            T._load_attestation_schema(),
            "_load_attestation_schema() 返回 None —— 与线上 'Schema not found' 同因",
        )


class TestIssuanceEndToEnd(unittest.TestCase):
    """签发链路必须真的产出凭证，而不是返回一句错误。"""

    _SUBJECT = {"type": "agent", "url": "https://github.com/example/demo", "name": "demo"}
    _VERDICT = {"score": 88, "level": "silver", "risk": "safe",
                "no_spawn_guarantee": True, "offline_scan": True}
    _COVERAGE = {"owasp_mcp_top10": "10/10", "owasp_asi_top10": "10/10",
                 "dimensions": ["security", "supply_chain"]}
    _META = {"method": "automated", "scan_id": "scan_unit_1", "findings_count": 2,
             "severity_counts": {"medium": 2}, "evidence_count": 2,
             "generated_at": "2026-10-06T00:00:00+00:00"}

    def test_generate_attestation_succeeds(self):
        import api.trust_api as T
        res, err = T.generate_attestation(self._SUBJECT, self._VERDICT,
                                         self._COVERAGE, self._META)
        self.assertIsNone(err, f"签发失败：{err}")
        self.assertTrue(res.get("id"))
        self.assertIn("issued_at", res)
        self.assertEqual(res.get("schema"), "trust-attestation/v1")

    def test_create_from_scan_succeeds(self):
        """集成工具 scripts/integrate_trust_attestation.py 走的就是这条路径。"""
        import api.trust_api as T
        scan = {
            "source_url": "https://github.com/example/demo",
            "scan_id": "scan_unit_1",
            "summary": {"overall_score": 88, "findings_total": 2,
                        "severity_counts": {"medium": 2}},
            "findings": [{"severity": "medium", "rule": "demo.rule"}],
        }
        res, err = T.create_attestation_from_scan(
            scan, "https://github.com/example/demo", "agent")
        self.assertIsNone(err, f"from-scan 签发失败：{err}")
        self.assertTrue(res.get("id"))

    def test_from_scan_requires_score(self):
        """缺 summary.overall_score 时必须走 0 分口径 —— 记录这个语义，
        防止有人"顺手"改成默认满分，把无依据的凭证签出去。"""
        import api.trust_api as T
        scan = {"source_url": "https://github.com/example/demo", "findings": []}
        res, err = T.create_attestation_from_scan(
            scan, "https://github.com/example/demo", "agent")
        self.assertIsNone(err)
        self.assertEqual(res["verdict"]["score"], 0)
        self.assertEqual(res["verdict"]["risk"], "critical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
