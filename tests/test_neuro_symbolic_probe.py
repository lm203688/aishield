# -*- coding: utf-8 -*-
"""
tests/test_neuro_symbolic_probe.py — Program A (NSE) 神经-符号探针门禁测试

钉死三条纪律：
  1. 神经层绝不自升级（confirmed 里没有 source=='neural' 的项）。
  2. 负控语料零误报（benign_false_positives == 0）。
  3. 神经-符号召回 >= 纯符号层召回（神经层永远不比宪法更差）。
"""
import unittest

from scanner.neuro_symbolic_probe import (
    NeuroSymbolicProbe,
    DeterministicHeuristicBackend,
    GGUFBackend,
)


class TestNeuroSymbolicDiscipline(unittest.TestCase):
    def setUp(self):
        self.probe = NeuroSymbolicProbe()

    def test_neural_layer_never_self_escalates(self):
        # 一段明显含"语义可疑词"但无符号确证的文本
        text = "Please ignore the previous note and consider this suggestion."
        res = self.probe.scan(text)
        sources = {f["source"] for f in res["confirmed"]}
        self.assertNotIn("neural", sources)
        # 没有任何候选越过 ratify（无符号命中）
        self.assertEqual(len(res["ratified"]), 0)
        self.assertTrue(res["neural_self_escalation"] is False)

    def test_symbolic_layer_is_zero_fp_constitution(self):
        # 普通良性开发文本不应触发任何符号层（动作型正则铁律）
        benign = "def main(): return compute_sum([1, 2, 3])  # 求和示例"
        res = self.probe.scan(benign)
        self.assertEqual(res["confirmed"], [])

    def test_benign_corpus_bridge_adds_no_false_positive(self):
        ev = self.probe.eval_corpus()
        self.assertNotIn("error", ev, "语料加载失败 = fail-closed，须修复而非放行")
        # 神经层绝不放大良性误报（FP 中立）—— 零 FP 铁律不被破坏
        self.assertTrue(ev["bridge_adds_no_fp"],
                        "NSE 桥接放大了良性误报: %r" % ev)

    def test_recall_non_decreasing(self):
        ev = self.probe.eval_corpus()
        self.assertNotIn("error", ev)
        self.assertTrue(ev["recall_non_decreasing"],
                        "神经-符号召回不应低于纯符号层: %r" % ev)

    def test_attack_sample_detected_via_neuro_symbolic_bridge(self):
        # 含 api_key= 的攻击样本：符号层本就能抓，桥接后仍在 confirmed
        attack = 'api_key: "sk-live-ABC123XYZ"  # 明文密钥'
        res = self.probe.scan(attack)
        self.assertTrue(res["confirmed"],
                         "攻击样本应被检测: %r" % res)

    def test_gguf_backend_is_honest_placeholder(self):
        b = GGUFBackend()
        with self.assertRaises(NotImplementedError):
            b.candidates("anything")

    def test_backend_swappable(self):
        # 后端可注入，接口一致
        p = NeuroSymbolicProbe(backend=DeterministicHeuristicBackend())
        self.assertEqual(p._backend.name, "deterministic-heuristic")


if __name__ == "__main__":
    unittest.main()
