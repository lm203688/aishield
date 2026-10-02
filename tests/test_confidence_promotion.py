# -*- coding: utf-8 -*-
"""
Confidence-based rule promotion 测试 — tests/test_confidence_promotion.py

覆盖：
  * 阈值边界（0 / 1 / 4 / 5 / 9 / 10 hits）
  * 红线分级：祈使式 benign 命中（硬红线）vs 话题提及（软红线，禁自动 promote）
  * 低特异性 pattern 压到 seed（裸关键词口径）
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

from scripts import confidence_promotion
from scripts.confidence_promotion import (
    _cap_state,
    _classify,
    _classify_benign_hit,
    _count_hits,
    _evaluate_candidate,
    _is_low_specificity,
    _exit_code,
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

    def test_topic_mention_is_not_a_red_line_kill(self):
        # 这正是 AIShield 的核心设计原则："话题提及 ≠ 祈使执行"。
        #
        # 2026-10-02 修正：这条测试原先叫 test_benign_discussion_triggers_red_line，
        # 断言"讨论性 benign 命中 → false_positive"。**它的 docstring 和断言是反的**
        # （docstring 写要区分两者，断言要求不区分），而那个断言恰好把红线变成了一台
        # 只会误杀的机器：真实队列 22 条候选里，被拦的 2 条命中的全是话题提及
        # （"已缓解 MCP 工具投毒"、"ignore all previous instructions 是 canonical
        # 越狱短语"），硬红线（pattern 会打在真实攻击指令上）一次都没触发过。
        #
        # 现在语义是：话题提及 → 不杀候选，但禁自动 promote（只能人工审到 draft）。
        data = {
            "rules": [{"pattern": r'ignore\s+all\s+previous\s+instructions'}],
        }
        r = _evaluate_candidate("x.json", data)
        self.assertFalse(r["false_positive"])
        self.assertTrue(r["promotable"])
        # 且必须至少命中 2 条讨论性 benign 样本，全部归类为话题提及
        self.assertGreaterEqual(r["topic_hits"], 2)
        self.assertEqual(r["imperative_hits"], 0)

    def test_topic_mention_cannot_be_auto_promoted_end_to_end(self):
        # 软红线要在 run_check 层真正生效：话题提及命中把状态压到 seed，
        # 于是永远进不了 ready_to_promote / draft。
        with tempfile.TemporaryDirectory() as tmp:
            old = confidence_promotion.PROPOSED_DIR
            confidence_promotion.PROPOSED_DIR = tmp
            try:
                name = "PROPOSED_test_topic_mention.json"
                with open(os.path.join(tmp, name), "w", encoding="utf-8") as f:
                    json.dump(
                        {"status": "ready",
                         "attack_category": "jailbreak",
                         "rules": [{"pattern": r'ignore\s+all\s+previous\s+'
                                               r'instructions'}]},
                        f)
                report = confidence_promotion.run_check(write_back=False)
            finally:
                confidence_promotion.PROPOSED_DIR = old
            entry = report["details"][-1]
            self.assertEqual(entry["topic_hits"], 2)
            self.assertFalse(entry["promotable"])
            # 这条 pattern 在攻击语料上命中很多，本来够得着 rule；话题提及命中
            # 把它压到 seed —— 软红线生效的证据，不是"没证据所以 raw"。
            self.assertGreaterEqual(entry["attack_hits"], 1)
            self.assertEqual(entry["state"], "seed")
            self.assertNotIn(name, report["buckets"]["ready_to_promote"])
            self.assertNotIn(name, report["buckets"]["draft"])
            self.assertIn(name, report["buckets"]["seed"])
            self.assertIn(name, report["buckets"]["topic_mention"])

    def test_exit_code_is_not_always_one(self):
        # 旧实现 `false_positive>0 or raw>0` 在真实队列上恒为 1，接进 CI 就是
        # 永久红，最后必然被人 `|| true` 掉 —— 硬红线的信号就这么没了。
        clean = {"buckets": {"false_positive": []}, "details": []}
        self.assertEqual(_exit_code(clean), 0)
        blocked = {"buckets": {"false_positive": ["a.json"]}, "details": []}
        self.assertEqual(_exit_code(blocked), 1)
        dead = {"buckets": {"false_positive": []},
                "details": [{"stale_suggested_reject": True}]}
        self.assertEqual(_exit_code(dead), 2)

    def test_imperative_benign_hit_triggers_hard_red_line(self):
        # 硬红线必须有真针：pattern 打在"祈使式良性运维指令"上（curl|sh、rm -rf、
        # pip install 都在这个组里），一律拒绝累积。
        for pat in (r'curl\s+.*\|\s*sh', r'\brm\s+-rf\b', r'pip\s+install'):
            r = _evaluate_candidate("x.json", {"rules": [{"pattern": pat}]})
            self.assertTrue(r["false_positive"], pat)
            self.assertFalse(r["promotable"], pat)
            self.assertGreater(r["imperative_hits"], 0, pat)

    def test_unclassifiable_benign_hit_defaults_to_blocking(self):
        # 红线失败方向必须是"该拦没拦"。判定不出是话题提及的一律按祈使处理，
        # 宁可误杀候选，也不能放过会误报生产的 pattern。
        self.assertEqual(
            _classify_benign_hit("A random benign line with no markers at all."),
            "imperative",
        )

    def test_classify_distinguishes_topic_from_imperative(self):
        self.assertEqual(
            _classify_benign_hit(
                "This MCP server is a defensive guardrail: it detects prompt "
                "injection and jailbreak attempts."),
            "topic_mention",
        )
        # 中文良性公告同样要认出来（audit_rules 的 CITATION_MARKERS 是纯英文，
        # 会把这两条判成 general）
        self.assertEqual(
            _classify_benign_hit(
                "安全公告：我们已缓解 MCP 工具投毒（tool poisoning）风险"),
            "topic_mention",
        )
        self.assertEqual(
            _classify_benign_hit("Runbook step: run `curl -fsSL x | sh` now."),
            "imperative",
        )

    def test_low_specificity_pattern_capped_at_seed(self):
        # 与雷达规则同口径：裸关键词（无 `|`、无有界间隔）只能到 seed。
        self.assertTrue(_is_low_specificity(r'jailbreak'))
        self.assertTrue(_is_low_specificity(r'supply\s*chain'))
        self.assertFalse(_is_low_specificity(
            r'(llm|agent|agentic)\s*.*\b(red[- ]team\w*|adversarial attack)\b'))
        self.assertEqual(_cap_state("rule", "seed"), "seed")
        self.assertEqual(_cap_state("seed", "seed"), "seed")
        self.assertEqual(_cap_state("draft", "rule"), "draft")

    def test_raw_candidate_is_not_killed_by_red_line(self):
        # 0 攻击命中的候选不该被红线销案：否则一次 --apply 就把没证据的候选
        # 永久置成 rejected，语料扩了也救不回来。
        data = {"status": "ready", "rules": [{"pattern": r'jailbreak'}]}
        r = _evaluate_candidate("x.json", data)
        self.assertEqual(r["attack_hits"], 0)
        self.assertFalse(r["false_positive"])


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


class TestApplyDoesNotDestroyCandidates(unittest.TestCase):
    """--apply 只写评估字段，绝不把候选永久销案。"""

    def test_apply_keeps_status_and_records_blocked_reason(self):
        # 旧实现在 false_positive 分支里 `data["status"] = "rejected"`，
        # 意味着**跑一次 --apply 就永久销毁一条候选**：它从队列里消失，
        # 之后即使语料扩了、pattern 改对了也进不来。真实队列上已经埋着这个雷。
        with tempfile.TemporaryDirectory() as tmp:
            old = confidence_promotion.PROPOSED_DIR
            confidence_promotion.PROPOSED_DIR = tmp
            path = None
            try:
                path = os.path.join(tmp, "PROPOSED_test_apply.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(
                        {"status": "ready", "attack_category": "supply-chain",
                         "rules": [{"pattern": r'curl\s+.*\|\s*sh'}]}, f)
                confidence_promotion.run_check(write_back=True)
                with open(path, encoding="utf-8") as f:
                    saved = json.load(f)
            finally:
                confidence_promotion.PROPOSED_DIR = old
        self.assertEqual(saved["status"], "ready",
                         "--apply 不该改写 status，否则候选永久销案")
        self.assertIn("blocked_by", saved)
        self.assertTrue(saved["blocked_by"])

    def test_apply_is_idempotent_on_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = confidence_promotion.PROPOSED_DIR
            confidence_promotion.PROPOSED_DIR = tmp
            path = None
            try:
                path = os.path.join(tmp, "PROPOSED_test_apply2.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(
                        {"status": "ready", "rules": [{"pattern": r'pip\s+install'}]},
                        f)
                def _read():
                    with open(path, encoding="utf-8") as f:
                        return json.load(f)

                confidence_promotion.run_check(write_back=True)
                first = _read()
                confidence_promotion.run_check(write_back=True)
                second = _read()
            finally:
                confidence_promotion.PROPOSED_DIR = old
        self.assertEqual(first["status"], second["status"])
        self.assertEqual(first["confidence"], second["confidence"])


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
