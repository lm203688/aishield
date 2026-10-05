"""
评分可解释（M3 收口）测试。

这条测试要防的病：**分数解释得"看起来"很详细，但账其实拼不平**。
2026-10-05 实测坐实两个真缺口：
  * penalty=105，breakdown['contributors'] 只展示 80 → 25 分扣分在解释里蒸发，
    用户问「为什么 60 不是 85」永远拼不出账；
  * 扣分项只有中文 reason，没有 rule_id → 申诉定位不到具体规则。

所以这里的重点不是「函数能跑」，而是：
  1. 扣分账 **100% 闭合**（penalty == 全量扣分项之和）；
  2. 归因**每条**都能落到 rule_id；
  3. 展示截断**如实报出**（hidden_amount），不许闷着；
  4. 有**独立复算**且必须与 engine 一致（不一致 ⇒ 分数不可信）；
  5. 反向用例：掐掉全量账本 / 篡改 penalty / 去掉 rule_id / 改 overall，
     审计**必须**报出来 —— 否则这条门禁就是空转。
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scanner.engine import calculate_scores  # noqa: E402
from scanner.score_explain import (  # noqa: E402
    DIM_ORDER, audit, explain, replay, attribution_text, ledger_from_replay,
)


def _mk(n, sev_cycle=("critical", "high", "medium", "low"), cat="ASI01", desc_prefix="问题"):
    return [{"type": cat, "rule_id": "%s-R%02d" % (cat, i + 1),
             "description": "%s%d" % (desc_prefix, i + 1), "file": "%d.py" % i,
             "lines": str(i), "col": "1", "severity": sev_cycle[i % len(sev_cycle)],
             "owasp_category": cat} for i in range(n)]


def _engine_scores(findings, total_files=5):
    return calculate_scores({"findings": findings, "patterns_checked": 20},
                            {"findings": []}, {"findings": []}, [], [], total_files)


class TestLedgerCloses(unittest.TestCase):
    """扣分账必须闭合 —— 这是「可解释」的最低门槛。"""

    def setUp(self):
        self.findings = _mk(12)
        self.scores = _engine_scores(self.findings)

    def test_penalty_equals_sum_of_full_contributions(self):
        for dim in DIM_ORDER:
            b = self.scores["score_breakdown"][dim]
            full = b["contributions_full"]
            self.assertEqual(b["penalty"], sum(c["amount"] for c in full),
                             "%s 的 penalty 与全量扣分项之和不符，账拼不平" % dim)

    def test_truncation_is_real_and_visible(self):
        """12 条告警必然超过 top5 展示位 —— 截断必须发生且被如实标出。"""
        b = self.scores["score_breakdown"]["security_score"]
        self.assertTrue(b["truncated"], "样本应触发展示截断")
        self.assertGreater(len(b["contributions_full"]), len(b["contributors"]))
        ex = explain(self.scores, fmt="json")
        d = ex["per_dim"]["security_score"]
        self.assertGreater(d["hidden_amount"], 0, "被截断的扣分必须报出金额，不能闷着")
        self.assertEqual(d["shown_amount"] + d["hidden_amount"], d["penalty"],
                         "展示 + 隐藏 必须等于 total penalty")

    def test_every_deduction_carries_rule_id(self):
        for dim in DIM_ORDER:
            for c in self.scores["score_breakdown"][dim]["contributions_full"]:
                self.assertTrue(c.get("rule_id"), "%s 有扣分项缺 rule_id，申诉无法定位" % dim)

    def test_audit_ok_on_engine_output(self):
        aud = audit(self.scores, findings=self.findings, total_files=5)
        self.assertTrue(aud["ok"], "审计不该在正常 engine 输出上报错: %s" % aud["issues"])
        self.assertTrue(aud["attribution_complete"])

    def test_dim_score_equals_base_minus_penalty(self):
        for dim in DIM_ORDER:
            b = self.scores["score_breakdown"][dim]
            self.assertEqual(self.scores[dim], max(0, min(100, b["base"] - b["penalty"])))


class TestFoldedDuplicates(unittest.TestCase):
    """同描述跨文件折叠是口径，不是 bug —— 但必须可见。"""

    def test_same_rule_hitting_many_files_is_surfaced(self):
        findings = [{"type": "SECRET", "rule_id": "SEC-01", "description": "硬编码凭据",
                     "file": "%s.py" % f, "severity": "high", "owasp_category": "MCP04"}
                    for f in ("a", "b", "c")]
        scores = _engine_scores(findings, total_files=3)
        b = scores["score_breakdown"]["supply_chain_score"]
        self.assertEqual(b["penalty"], 15, "3 个文件同描述只扣一次")
        self.assertEqual(len(b["folded_duplicates"]), 2, "被折叠的 2 条必须记录")
        for f in b["folded_duplicates"]:
            self.assertEqual(f["rule_id"], "SEC-01", "折叠项也要能查到是哪条规则")
        ex = explain(scores, fmt="json")
        self.assertEqual(len(ex["per_dim"]["supply_chain_score"]["folded_duplicates"]), 2)


class TestReplay(unittest.TestCase):
    """独立复算：路径独立、结果必须一致、digest 可回归。"""

    def test_replay_matches_engine(self):
        findings = _mk(12)
        rp = replay(findings, total_files=5)
        scores = _engine_scores(findings)
        self.assertEqual(rp["overall_score"], scores["overall_score"],
                         "独立复算与 engine 不一致，此分数不可信")
        for dim in DIM_ORDER:
            self.assertEqual(rp["dims"][dim], scores[dim], "维度 %s 复算不一致" % dim)

    def test_replay_is_deterministic(self):
        findings = _mk(8)
        a = replay(findings, total_files=4)
        b = replay(findings, total_files=4)
        self.assertEqual(a["digest"], b["digest"], "同输入必须同 digest（口径回归靠它）")

    def test_digest_changes_when_score_changes(self):
        """反空转：digest 不能是常量。"""
        d1 = replay(_mk(4), total_files=4)["digest"]
        d2 = replay(_mk(4, sev_cycle=("critical",)), total_files=4)["digest"]
        self.assertNotEqual(d1, d2, "严重度变了 digest 却没变 —— digest 是假的")

    def test_ledger_from_replay_feedable_to_explain(self):
        rp = replay(_mk(6), total_files=3)
        scores = ledger_from_replay(rp)
        self.assertEqual(scores["overall_score"], rp["overall_score"])
        ex = explain(scores, fmt="json")
        self.assertTrue(ex["attribution_complete"])
        self.assertEqual(ex["overall_score"], rp["overall_score"])


class TestAuditCatchesFakes(unittest.TestCase):
    """反向用例：这四条不红，审计就是空转的门禁。"""

    def setUp(self):
        self.findings = _mk(12)
        self.scores = _engine_scores(self.findings)

    def _codes(self, aud):
        return {i["code"] for i in aud["issues"]}

    def test_missing_full_ledger_is_flagged(self):
        import copy
        s = copy.deepcopy(self.scores)
        for dim in DIM_ORDER:
            # 模拟「只有 top5 的老结构」
            s["score_breakdown"][dim].pop("contributions_full", None)
        aud = audit(s)
        self.assertIn("no_full_ledger", self._codes(aud))
        self.assertFalse(aud["ok"])

    def test_penalty_mismatch_is_flagged(self):
        import copy
        s = copy.deepcopy(self.scores)
        s["score_breakdown"]["security_score"]["penalty"] += 7
        aud = audit(s)
        self.assertIn("penalty_not_reproducible", self._codes(aud))

    def test_missing_rule_id_is_flagged(self):
        import copy
        s = copy.deepcopy(self.scores)
        for c in s["score_breakdown"]["security_score"]["contributions_full"]:
            c["rule_id"] = ""
        aud = audit(s)
        self.assertIn("missing_rule_id", self._codes(aud))

    def test_tampered_overall_is_flagged_by_replay(self):
        import copy
        s = copy.deepcopy(self.scores)
        s["overall_score"] = s["overall_score"] + 3
        aud = audit(s, findings=self.findings, total_files=5)
        self.assertIn("replay_mismatch", self._codes(aud),
                      "分数被改过而独立复算没发现 —— 复算形同虚设")

    def test_dim_formula_mismatch_is_flagged(self):
        import copy
        s = copy.deepcopy(self.scores)
        s["security_score"] = 99
        aud = audit(s)
        self.assertIn("dim_formula_mismatch", self._codes(aud))


class TestTextRender(unittest.TestCase):
    def test_text_shows_truncated_items_explicitly(self):
        findings = _mk(12)
        txt = attribution_text(_engine_scores(findings))
        self.assertIn("被截断", txt, "文本版必须明说还有扣分项没展开")
        self.assertIn("rule=", txt, "文本版必须能看出扣分对应的规则")

    def test_text_flags_incomplete_accounting(self):
        import copy
        s = copy.deepcopy(_engine_scores(_mk(12)))
        for dim in DIM_ORDER:
            b = s["score_breakdown"][dim]
            if b.get("contributions_full"):
                b["penalty"] = b["penalty"] + 5
                break
        txt = attribution_text(s)
        self.assertIn("解释不完整", txt)


if __name__ == "__main__":
    unittest.main()
