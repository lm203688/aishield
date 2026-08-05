"""
CI 门禁契约测试 — 锁定「门禁能读到分数」这条链路

背景（真实事故，2026-08-05）:
  security-scan.yml 用 `d.get('score', 0)` 读 /api/v1/audit 响应，
  但响应只有 `report.overall_score`，顶层无 score →
  门禁恒得 0 分 → 连红 17 次 / 48h，而被守护对象其实是健康的。

教训: 门禁连红时先怀疑门禁自己。
防线: 
  1) API 响应必须同时提供顶层 score（便捷字段，与 report.overall_score 恒等）
  2) 任何 CI 取值路径都不允许「解析失败静默降级为 0」

本文件为纯静态契约测试，不依赖运行中的服务器。
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_PY = os.path.join(ROOT, 'api', 'server.py')
WORKFLOW = os.path.join(ROOT, '.github', 'workflows', 'security-scan.yml')


def _read(path):
    with open(path, 'r', encoding='utf-8') as fh:
        return fh.read()


class TestAuditResponseContract(unittest.TestCase):
    """/api/v1/audit 响应必须暴露顶层 score"""

    def setUp(self):
        self.src = _read(SERVER_PY)

    def test_audit_response_exposes_top_level_score(self):
        """顶层 score 字段存在且取自 overall_score"""
        self.assertRegex(
            self.src,
            r'"score":\s*result\.get\(\s*"overall_score"',
            "audit 响应缺少顶层 score 字段 —— CI 门禁将恒得 0 分",
        )

    def test_audit_response_keeps_nested_report(self):
        """report 嵌套结构不得被移除（既有消费方依赖）"""
        self.assertIn('"report": result,', self.src)

    def test_top_level_convenience_fields_present(self):
        """badge_level / risk_level 同步提升到顶层，便于 Agent 直读"""
        for key in ('"badge_level"', '"risk_level"'):
            self.assertIn(f'{key}: result.get(', self.src,
                          f'顶层缺少便捷字段 {key}')


class TestSecurityGateWorkflow(unittest.TestCase):
    """security-scan.yml 门禁本身的健壮性"""

    def setUp(self):
        if not os.path.exists(WORKFLOW):
            self.skipTest('security-scan.yml 不存在')
        self.wf = _read(WORKFLOW)

    def test_gate_has_issues_write_permission(self):
        """告警步骤要建 issue，必须声明 issues: write，否则 403"""
        self.assertRegex(self.wf, r'issues:\s*write',
                         '缺少 issues: write —— 告警步骤会 403')

    def test_gate_does_not_silently_default_to_zero(self):
        """禁止 `.get('score', 0)` 这类静默降级：解析不到必须显式失败"""
        bad = re.findall(r"get\(\s*['\"]score['\"]\s*,\s*0\s*\)", self.wf)
        self.assertEqual(
            bad, [],
            "门禁不得把解析失败降级为 0 分，应显式报错退出（历史事故根因）",
        )

    def test_gate_reads_authoritative_score_path(self):
        """门禁必须读得到权威分数（顶层 score 或 report.overall_score）"""
        self.assertTrue(
            'overall_score' in self.wf or "'score'" in self.wf or '"score"' in self.wf,
            '门禁未引用任何分数字段',
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
