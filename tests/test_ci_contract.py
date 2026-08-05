"""
CI 门禁契约测试 — 锁定「门禁能读到分数」这条链路

背景（真实事故，2026-08-05）:
  security-scan.yml 用 `d.get('score', 0)` 读 /api/v1/audit 响应，
  但当时响应只有 `report.overall_score`，顶层无 score →
  门禁恒得 0 分 → 连红 17 次 / 48h，而被守护对象其实是健康的。

教训: 门禁连红时先怀疑门禁自己。
不变量: 门禁读取的每一个分数键，API 都必须真实提供。

本文件为纯静态契约测试，不依赖运行中的服务器、不依赖网络。
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_PY = os.path.join(ROOT, 'api', 'server.py')
WORKFLOW = os.path.join(ROOT, '.github', 'workflows', 'security-scan.yml')

# API 承诺提供的分数取值路径（顶层键 / 嵌套容器键）
API_SCORE_KEYS = {'score', 'report', 'overall_score', 'badge_level', 'risk_level'}


def _read(path):
    with open(path, 'r', encoding='utf-8') as fh:
        return fh.read()


class TestAuditResponseContract(unittest.TestCase):
    """/api/v1/audit 响应形状契约"""

    def setUp(self):
        self.src = _read(SERVER_PY)

    def test_audit_response_exposes_top_level_score(self):
        """顶层 score 字段存在且取自 overall_score —— CI 门禁的直接依赖"""
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


class TestSecurityGateReadsRealKeys(unittest.TestCase):
    """门禁读取的键必须被 API 真实提供（跨文件一致性）"""

    def setUp(self):
        if not os.path.exists(WORKFLOW):
            self.skipTest('security-scan.yml 不存在')
        self.wf = _read(WORKFLOW)

    def _score_keys(self):
        """抽取门禁从 JSON 报告中读取的所有键名"""
        keys = set(re.findall(r"get\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]", self.wf))
        keys |= set(re.findall(r"d\.([A-Za-z_][A-Za-z0-9_]*)\s*\?\?", self.wf))
        return keys

    def test_every_key_the_gate_reads_is_served_by_api(self):
        """门禁读的键不能是 API 里不存在的幻觉字段（历史事故根因）"""
        unknown = self._score_keys() - API_SCORE_KEYS
        self.assertEqual(
            unknown, set(),
            f"门禁读取了 API 未提供的键 {sorted(unknown)} —— 会静默取到默认值",
        )

    def test_gate_reads_at_least_one_score_key(self):
        """门禁必须真的读分数，而不是空跑"""
        self.assertTrue(
            self._score_keys() & {'score', 'overall_score'},
            '门禁未引用任何分数字段',
        )

    def test_gate_threshold_is_explicit(self):
        """阈值必须写死在门禁里，便于审计"""
        self.assertRegex(self.wf, r'-lt\s+\d+|<\s*\d+|>=\s*\d+',
                         '门禁缺少显式分数阈值')


if __name__ == '__main__':
    unittest.main(verbosity=2)
