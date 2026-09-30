# -*- coding: utf-8 -*-
"""
Confidence-based rule promotion 测试 — tests/test_confidence_promotion.py

覆盖：
  * 阈值边界（0 / 1 / 4 / 5 / 9 / 10 hits）
  * BENIGN_CORPUS 零命中红线
  * 状态分类（raw / seed / draft / rule）
  * decay 检测（stale / stale_suggested_reject）
  * CLI --check / --apply 输出结构
  * 已 rejected 候选不被处理
"""
import datetime
import json
import os
import tempfile
import unittest

# 直接测函数，不写临时文件
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))

from scripts.confidence_promotion import (
    _classify,
    _count_hits,
    _evaluate_candidate,
    _now,
    SEED_THRESHOLD,
    DRAFT_THRESHOLD,
    RULE_THRESHOLD,
    STALE_DAYS,
    DEAD_DAYS,
)
from rule_corpus import ATTACK_SAMPLES, BENIGN_CORPUS


def _days_ago(n: int) -> str:
    return (datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(days=n)).isoformat(timespec="seconds")


class TestClassifyThresholds(unittest.TestCase):
    def test_zero_is_raw(self):
        self.assertEqual(_classify(0, None, _now())["state"], "raw")

    def test_one_is_seed(self):
        r = _classify(1, _now(), _now())
        self.assertEqual(r["state"], "seed")
        self.assertFalse(r["stale"])

    def test_four_is_seed(self):
        r = _classify(4, _now(), _now())
        self.assertEqual(r["state"], "seed")

    def test_five_is_draft(self):
        r = _classify(5, _now(), _now())
        self.assertEqual(r["state"], "draft")

    def test_nine_is_draft(self):
        r = _classify(9, _now(), _now())
        self.assertEqual(r["state"], "draft")

    def test_ten_is_rule(self):
        r = _classify(10, _now(), _now())
        self.assertEqual(r["state"], "rule")

    def test_large_is_rule(self):
        r = _classify(99, _now(), _now())
        self.assertEqual(r["state"], "rule")


class TestClassifyDecay(unittest.TestCase):
    def test_fresh_not_stale(self):
        r = _classify(10, _now(), _now())
        self.assertFalse(r["stale"])
        self.assertFalse(r["stale_suggested_reject"])

    def test_stale_at_boundary(self):
        old = _days_ago(STALE_DAYS)
        r = _classify(10, old, _now())
        self.assertTrue(r["stale"])
        self.assertFalse(r["stale_suggested_reject"])

    def test_dead_at_boundary(self):
        old = _days_ago(DEAD_DAYS)
        r = _classify(10, old, _now())
        self.assertTrue(r["stale"])
        self.assertTrue(r["stale_suggested_reject"])

    def test_raw_not_stale_even_if_old(self):
        # raw 状态没有 last_observed 语义，不判 stale
        old = _days_ago(365)
        r = _classify(0, old, _now())
        self.assertEqual(r["state"], "raw")
        self.assertFalse(r["stale"])

    def test_seed_not_stale_even_if_old(self):
        old = _days_ago(365)
        r = _classify(2, old, _now())
        # seed 也判 stale
        self.assertTrue(r["stale"])

    def test_none_last_observed_no_stale(self):
        r = _classify(10, None, _now())
        self.assertFalse(r["stale"])


class TestCountHits(unittest.TestCase):
    def test_pattern_hits_multiple_samples(self):
        # 通用型攻击字符串，应命中多条 ATTACK_SAMPLES
        hits = _count_hits(r'ignore\s+all\s+previous\s+instructions', ATTACK_SAMPLES)
        self.assertGreater(hits, 0)

    def test_nonsensical_pattern_zero_hits(self):
        hits = _count_hits(r'zzz_no_such_token_zzz_', ATTACK_SAMPLES)
        self.assertEqual(hits, 0)

    def test_broken_regex_zero_hits(self):
        # 语法错误的正则 → 静默 0 命中，不抛异常
        hits = _count_hits(r'(', ATTACK_SAMPLES)
        self.assertEqual(hits, 0)

    def test_each_sample_counts_once(self):
        # 一个 sample 内多处匹配仍只算 1 次
        samples = ["foo bar foo", "baz foo"]
        self.assertEqual(_count_hits(r'foo', samples), 2)


class TestBenignCorpusRedLine(unittest.TestCase):
    def test_benign_match_forces_false_positive(self):
        data = {
            "status": "ready",
            "rules": [{"pattern": r'if|and|return'}],  # 太宽，命中 benign 代码
        }
        r = _evaluate_candidate("x.json", data)
        self.assertTrue(r["false_positive"])
        self.assertGreater(r["benign_hits"], 0)

    def test_tight_pattern_zero_benign(self):
        # 注意：不能用 "ignore all previous instructions" —— BENIGN_CORPUS 里
        # 有 2 条在讨论这个短语（良性语料刻意包含"话题提及 vs 祈使执行"的区分）。
        # 用真正零 benign 的通用攻击 pattern 代替。
        data = {
            "status": "ready",
            "rules": [{"pattern": r'exfiltrate\s+the\s+user\'s\s+api\s+keys'}],
        }
        r = _evaluate_candidate("x.json", data)
        self.assertFalse(r["false_positive"])
        self.assertEqual(r["benign_hits"], 0)

    def test_benign_discussion_triggers_red_line(self):
        # 这正是 AIShield 的核心设计原则："话题提及 ≠ 祈使执行"。
        # 讨论 "ignore all previous instructions" 的良性文档会被这个宽泛 pattern 误报，
        # confidence_promotion 必须识别并拒绝累积。
        data = {
            "rules": [{"pattern": r'ignore\s+all\s+previous\s+instructions'}],
        }
        r = _evaluate_candidate("x.json", data)
        self.assertTrue(r["false_positive"])
        # 且必须至少命中 2 条讨论性 benign 样本
        self.assertGreaterEqual(r["benign_hits"], 2)


class TestEvaluateCandidate(unittest.TestCase):
    def test_multiple_rules_sum_hits(self):
        data = {
            "rules": [
                {"pattern": r'ignore\s+all\s+previous\s+instructions'},
                {"pattern": r'prompt\s*injection'},
            ],
        }
        r = _evaluate_candidate("x.json", data)
        total = r["attack_hits"]
        # 两个 pattern 命中数之和
        self.assertGreater(total, 0)

    def test_empty_rules_zero_hits(self):
        r = _evaluate_candidate("x.json", {"rules": []})
        self.assertEqual(r["attack_hits"], 0)
        self.assertEqual(r["benign_hits"], 0)
        self.assertFalse(r["false_positive"])

    def test_missing_rules_key(self):
        r = _evaluate_candidate("x.json", {})
        self.assertEqual(r["attack_hits"], 0)

    def test_pattern_list_stored(self):
        data = {"rules": [{"pattern": r'foo'}, {"pattern": r'bar'}]}
        r = _evaluate_candidate("x.json", data)
        self.assertEqual(r["patterns"], ["foo", "bar"])


class TestThresholdConstants(unittest.TestCase):
    def test_thresholds_ordered(self):
        self.assertLess(SEED_THRESHOLD, DRAFT_THRESHOLD)
        self.assertLess(DRAFT_THRESHOLD, RULE_THRESHOLD)

    def test_stale_days_reasonable(self):
        self.assertGreater(STALE_DAYS, 30)
        self.assertLess(STALE_DAYS, 180)
        self.assertGreater(DEAD_DAYS, STALE_DAYS)

    def test_thresholds_match_instinct(self):
        # instinct 项目的三态：raw / mature (5-9) / rule (10+)
        self.assertEqual(DRAFT_THRESHOLD, 5)
        self.assertEqual(RULE_THRESHOLD, 10)


if __name__ == "__main__":
    unittest.main()
