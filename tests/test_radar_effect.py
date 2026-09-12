# -*- coding: utf-8 -*-
"""
Radar 规则效果（promote -> effect）测试。

补的洞：规则晋升进 data/radar_rules.json 之后，既没人验证它真能命中攻击，
也没人复查它是否误伤良性输入。本文件钉死这两条判据与持久化语义。
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import radar_effect  # noqa: E402


class TestEffectEvaluation(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='aishield_effect_')
        self._orig_rules = radar_effect.RADAR_RULES
        self._orig_effect = radar_effect.EFFECT_FILE
        radar_effect.RADAR_RULES = os.path.join(self.tmp, 'radar_rules.json')
        radar_effect.EFFECT_FILE = os.path.join(self.tmp, 'radar_effect.json')

    def tearDown(self):
        radar_effect.RADAR_RULES = self._orig_rules
        radar_effect.EFFECT_FILE = self._orig_effect
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _seed_rules(self, rules, provenance=None):
        with open(radar_effect.RADAR_RULES, 'w', encoding='utf-8') as f:
            json.dump({'version': 1, 'rules': rules,
                       'provenance': provenance or {}}, f)

    def test_good_rule_catches_and_does_not_misfire(self):
        self._seed_rules({r'credential\s*(leak|theft)': ['d', 'high']})
        eff = radar_effect.evaluate()
        rec = eff['rules'][r'credential\s*(leak|theft)']
        self.assertTrue(rec['catch'], '规则必须能命中正样本，否则是死规则')
        self.assertFalse(rec['false_positive'])
        self.assertEqual(eff['summary']['promoted'], 1)
        self.assertEqual(eff['summary']['false_positives'], 0)

    def test_broad_rule_is_flagged_as_false_positive(self):
        """关键词型规则会命中良性安全文档 —— 必须被标红。"""
        self._seed_rules({r'prompt\s*injection': ['d', 'high']})
        eff = radar_effect.evaluate()
        self.assertTrue(eff['rules'][r'prompt\s*injection']['false_positive'])
        self.assertEqual(eff['summary']['false_positives'], 1)

    def test_dead_rule_has_no_catch(self):
        self._seed_rules({r'never\s*matches\s*zzz': ['d', 'high']})
        eff = radar_effect.evaluate()
        self.assertFalse(eff['rules'][r'never\s*matches\s*zzz']['catch'])
        self.assertEqual(eff['summary']['with_catch'], 0)

    def test_persists_and_reloads(self):
        self._seed_rules({r'backdoor\s*(attack|trigger)': ['d', 'high']})
        radar_effect.evaluate()
        again = radar_effect.load_effect()
        self.assertIn(r'backdoor\s*(attack|trigger)', again['rules'])
        self.assertIn('summary', again)

    def test_record_hits_increments_and_preserves_catch(self):
        self._seed_rules({r'credential\s*(leak|theft)': ['d', 'high']})
        radar_effect.evaluate()
        radar_effect.record_hits([r'credential\s*(leak|theft)'] * 3)
        rec = radar_effect.load_effect()['rules'][r'credential\s*(leak|theft)']
        self.assertEqual(rec['hits'], 3)
        self.assertTrue(rec['catch'], 'record_hits 不得抹掉已有的效果评估')
        # re-evaluate must preserve the accumulated hit count
        eff = radar_effect.evaluate()
        self.assertEqual(eff['rules'][r'credential\s*(leak|theft)']['hits'], 3)

    def test_stale_rule_entry_is_dropped(self):
        self._seed_rules({r'backdoor\s*(attack|trigger)': ['d', 'high']})
        radar_effect.evaluate()
        self._seed_rules({})          # rule removed from live set
        eff = radar_effect.evaluate()
        self.assertEqual(eff['rules'], {})
        self.assertEqual(eff['summary']['promoted'], 0)

    def test_no_rules_is_safe(self):
        self._seed_rules({})
        eff = radar_effect.evaluate()
        self.assertEqual(eff['summary']['promoted'], 0)
        self.assertIn('暂无', radar_effect.render(eff))


if __name__ == '__main__':
    unittest.main(verbosity=2)
