# -*- coding: utf-8 -*-
"""
Rule decay 测试 — tests/test_rule_decay.py

覆盖：
  * _pattern_hash 稳定性（同 pattern → 同 hash）
  * _count_hits 计数正确
  * compute_state：无历史 → active
  * compute_state：全部命中 → active
  * compute_state：14 次快照 0 命中 → dormant
  * compute_state：30 次快照 0 命中 → retire_suggested
  * append_snapshot + read_snapshots 往返
  * HIST_KEEP 截断旧快照
  * load_external_hits 合并
  * retire_rules_from_source 从 JSON 移除规则
"""
import datetime
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from scripts.rule_decay import (
    _pattern_hash,
    _count_hits,
    _now,
    compute_state,
    append_snapshot,
    read_snapshots,
    evaluate_all,
    load_external_hits,
    retire_rules_from_source,
    HITS_LOG,
    DECAY_STATE,
    HIST_KEEP,
    DORMANT_WINDOW,
    RETIRE_WINDOW,
)
from rule_corpus import ATTACK_SAMPLES, BENIGN_CORPUS


class TestPatternHash(unittest.TestCase):
    def test_stable(self):
        h1 = _pattern_hash(r"foo\s+bar")
        h2 = _pattern_hash(r"foo\s+bar")
        self.assertEqual(h1, h2)

    def test_different(self):
        h1 = _pattern_hash(r"foo\s+bar")
        h2 = _pattern_hash(r"bar\s+foo")
        self.assertNotEqual(h1, h2)

    def test_length_12(self):
        h = _pattern_hash("any pattern")
        self.assertEqual(len(h), 12)


class TestCountHits(unittest.TestCase):
    def test_basic(self):
        samples = ["ignore all previous instructions", "hello world"]
        self.assertEqual(_count_hits(r"ignore", samples), 1)

    def test_zero(self):
        self.assertEqual(_count_hits(r"zzz_nope_zzz", ATTACK_SAMPLES), 0)

    def test_broken_regex(self):
        # 语法错误静默 0
        self.assertEqual(_count_hits(r"(", ATTACK_SAMPLES), 0)


class TestComputeStateEmptyHistory(unittest.TestCase):
    def _rules(self):
        return [("hash1", {"pattern": "foo", "meta": ["d", "high"]})]

    def test_no_snapshots_all_active(self):
        state = compute_state([], self._rules())
        self.assertEqual(state["summary"]["active"], 1)
        self.assertEqual(state["summary"]["dormant"], 0)
        self.assertEqual(state["summary"]["retire_suggested"], 0)


class TestComputeStateAllHit(unittest.TestCase):
    def test_all_hit_stays_active(self):
        """历史里每次都有命中 → active。"""
        rules = [("h1", {"pattern": "p", "meta": []})]
        snaps = []
        for i in range(RETIRE_WINDOW + 5):
            snaps.append({
                "ts": f"2026-09-{(i % 28) + 1:02d}T10:00:00Z",
                "rules": {"h1": {"attack_hits": 3, "benign_hits": 0}},
            })
        state = compute_state(snaps, rules)
        self.assertEqual(state["rules"]["h1"]["status"], "active")


class TestComputeStateDormant(unittest.TestCase):
    def test_14_zero_hits_becomes_dormant(self):
        """最近 14 次 0 命中 → dormant（未到 30 次阈值）。"""
        rules = [("h1", {"pattern": "p", "meta": []})]
        snaps = []
        # 先给 30 次命中，再给 14 次 0 命中
        for _ in range(RETIRE_WINDOW - DORMANT_WINDOW):
            snaps.append({"ts": "T", "rules": {"h1": {"attack_hits": 5}}})
        for _ in range(DORMANT_WINDOW):
            snaps.append({"ts": "T", "rules": {"h1": {"attack_hits": 0}}})
        state = compute_state(snaps, rules)
        self.assertEqual(state["rules"]["h1"]["status"], "dormant")


class TestComputeStateRetire(unittest.TestCase):
    def test_30_zero_hits_becomes_retire(self):
        """连续 30 次 0 命中 → retire_suggested。"""
        rules = [("h1", {"pattern": "p", "meta": []})]
        snaps = []
        for _ in range(RETIRE_WINDOW):
            snaps.append({"ts": "T", "rules": {"h1": {"attack_hits": 0}}})
        state = compute_state(snaps, rules)
        self.assertEqual(state["rules"]["h1"]["status"], "retire_suggested")
        self.assertGreater(state["summary"]["retire_suggested"], 0)

    def test_recovery_after_retire_window(self):
        """30 次 0 命中后被一次命中救回 → 不 retire。"""
        rules = [("h1", {"pattern": "p", "meta": []})]
        snaps = []
        for _ in range(RETIRE_WINDOW):
            snaps.append({"ts": "T", "rules": {"h1": {"attack_hits": 0}}})
        # 最后一次命中
        snaps.append({"ts": "T", "rules": {"h1": {"attack_hits": 3}}})
        # 最近 30 次窗口内已经有 1 次命中，不再是 0 命中
        state = compute_state(snaps, rules)
        self.assertNotEqual(
            state["rules"]["h1"]["status"],
            "retire_suggested",
        )


class TestSnapshotRoundtrip(unittest.TestCase):
    """读写快照文件。用 tempfile 避免污染真实 state。"""

    def setUp(self):
        self._orig_HITS_LOG = os.environ.get("RULE_DECAY_HITS_LOG")
        # monkeypatch 模块常量
        global HITS_LOG_TEST
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "hits.jsonl")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_append_and_read(self):
        import scripts.rule_decay as mod
        original = mod.HITS_LOG
        mod.HITS_LOG = self.path
        try:
            snap = {"ts": "2026-09-30T00:00:00Z", "rules": {}}
            append_snapshot(snap)
            snaps = read_snapshots()
            self.assertEqual(len(snaps), 1)
            self.assertEqual(snaps[0]["ts"], "2026-09-30T00:00:00Z")
        finally:
            mod.HITS_LOG = original

    def test_hist_keep_truncation(self):
        """超过 HIST_KEEP 的旧快照被截断。"""
        import scripts.rule_decay as mod
        original = mod.HITS_LOG
        mod.HITS_LOG = self.path
        try:
            for i in range(HIST_KEEP + 5):
                append_snapshot({"ts": f"T{i}", "rules": {}})
            snaps = read_snapshots()
            self.assertLessEqual(len(snaps), HIST_KEEP)
            # 最新保留的是最后 HIST_KEEP 条
            self.assertEqual(snaps[-1]["ts"], f"T{HIST_KEEP + 4}")
        finally:
            mod.HITS_LOG = original

    def test_read_nonexistent_returns_empty(self):
        import scripts.rule_decay as mod
        original = mod.HITS_LOG
        mod.HITS_LOG = os.path.join(self.tmpdir, "nonexistent.jsonl")
        try:
            snaps = read_snapshots()
            self.assertEqual(snaps, [])
        finally:
            mod.HITS_LOG = original


class TestExternalHits(unittest.TestCase):
    def test_load_valid_jsonl(self):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        for i in range(3):
            tmp.write(json.dumps({"pattern_hash": f"h{i}", "hits": i + 1}) + "\n")
        tmp.close()
        try:
            recs = load_external_hits(tmp.name)
            self.assertEqual(len(recs), 3)
            self.assertEqual(recs[0]["hits"], 1)
        finally:
            os.unlink(tmp.name)

    def test_load_nonexistent_returns_empty(self):
        self.assertEqual(load_external_hits("/tmp/nonexistent_hits.jsonl"), [])

    def test_load_skips_malformed(self):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        tmp.write(json.dumps({"pattern_hash": "h0", "hits": 1}) + "\n")
        tmp.write("not json\n")
        tmp.write(json.dumps({"pattern_hash": "h1", "hits": 2}) + "\n")
        tmp.close()
        try:
            recs = load_external_hits(tmp.name)
            self.assertEqual(len(recs), 2)
        finally:
            os.unlink(tmp.name)


class TestEvaluateAll(unittest.TestCase):
    def test_evaluates_radar_rules(self):
        rules = [
            (_pattern_hash("ignore all previous instructions"),
             {"pattern": "ignore all previous instructions", "meta": []}),
        ]
        snap = evaluate_all(rules)
        self.assertIn("rules", snap)
        self.assertIn("ts", snap)
        self.assertGreater(len(snap["rules"]), 0)
        entry = list(snap["rules"].values())[0]
        self.assertIn("attack_hits", entry)
        self.assertIn("benign_hits", entry)
        self.assertIn("hash", entry)


class TestRetireRulesFromSource(unittest.TestCase):
    """从 radar_rules.json 移除 retire_suggested 规则。"""

    def setUp(self):
        import scripts.rule_decay as mod
        self._orig = mod.RADAR_RULES
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "radar_rules.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        import scripts.rule_decay as mod
        mod.RADAR_RULES = self._orig

    def test_removes_retire_suggested(self):
        import scripts.rule_decay as mod
        mod.RADAR_RULES = self.path
        # 准备一个 radar_rules.json
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "rules": {
                "pat_keep": ["desc", "high"],
                "pat_retire": ["desc", "medium"],
            }}, f)
        # 构造一个 decay state
        state = {
            "rules": {
                _pattern_hash("pat_retire"): {
                    "status": "retire_suggested",
                    "pattern_prefix": "pat_retire",
                },
                _pattern_hash("pat_keep"): {
                    "status": "active",
                    "pattern_prefix": "pat_keep",
                },
            },
        }
        removed = retire_rules_from_source(state)
        self.assertEqual(removed, 1)
        with open(self.path, encoding="utf-8") as f:
            d = json.load(f)
        self.assertIn("pat_keep", d["rules"])
        self.assertNotIn("pat_retire", d["rules"])

    def test_no_retire_no_change(self):
        import scripts.rule_decay as mod
        mod.RADAR_RULES = self.path
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "rules": {
                "pat_a": ["d", "high"],
            }}, f)
        state = {"rules": {}}
        removed = retire_rules_from_source(state)
        self.assertEqual(removed, 0)


class TestThresholds(unittest.TestCase):
    def test_dormant_before_retire(self):
        self.assertLess(DORMANT_WINDOW, RETIRE_WINDOW)

    def test_hist_keep_sufficient(self):
        self.assertGreaterEqual(HIST_KEEP, RETIRE_WINDOW)


if __name__ == "__main__":
    unittest.main()
