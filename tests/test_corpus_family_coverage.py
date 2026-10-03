#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""攻击语料「攻击面族覆盖度」门禁（2026-10-03 建立）。

为什么需要这套断言
------------------
2026-10-03 体检：ATTACK_SAMPLES 只有 27 条、平均 56 字符的单行短句，攻击面
高度同质（curl|sh 2 条、越狱家族 0 条、工具投毒 0 条、skill 投毒 0 条）。
两个后果都跟"指标难看"无关：

1. benchmark 的 recall=1.0 是在那 27 条上量的。换个攻击面造句读数就塌——
   这是「假绿六层」里"窄样本不验真实路径"的具体形态，不是规则变强了。
2. scanner/_proposed 里 5 个候选（jailbreak / tool\\s*(poison|injection|squatting) /
   supply\\s*chain / (malicious|poison)\\s+skill / red-team 自述）在攻击语料上
   0 命中，看着像"候选是空壳正则"，实际是**语料里根本没有这些攻击面**。
   拿语料盲点当候选缺陷去改正则，只会让候选更贴合那 27 条，两边一起固化。

所以族覆盖度先于规则数成为门禁对象。三条口径：

* 每族至少 1 条样本 —— 防止族被整体删掉而门禁只看见"总数还够"。
* 每族至少 1 条能被现网引擎判出 serious —— 只数样本条数会让"族在但规则没
  覆盖"变成静默通过，那正是本次要抓的假绿；数字仍要报，但不允许 0 检出。
* KNOWN_GAP_SAMPLES 里每一条都必须**能被扫出来**（2026-10-03 口径翻转）。
  这个名字下原来记的是"尚未覆盖的攻击面"，断言方向是"保持未检出"。但那条
  断言允许无限地把新盲区登记进来而 CI 全绿——它把「记录」当成了「处置」，
  而 recall=1.0 会在这些盲区上继续虚高。现在方向反过来：
  **登记一个盲区的前提是它先能被检出**；真扫不出来的攻击面属于「不判定为
  攻击」那一类，走 DESCRIPTION_SAMPLES，不要往这里塞。
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from scanner.rules import analyze  # noqa: E402
import rule_corpus  # noqa: E402

MIN_PER_FAMILY = 1


def _serious(text):
    findings = analyze({"skills/payload_xx.md": text}, "mcp").get("findings", [])
    return [f for f in findings if f.get("severity") in ("critical", "high")]


class TestFamilyCorpusIntegrity(unittest.TestCase):
    """语料层自洽：族、列表、反查表三者不得各说各话。"""

    def test_every_family_sample_is_in_the_flat_list(self):
        flat = set(rule_corpus.ATTACK_SAMPLES)
        for name, samples in rule_corpus.ATTACK_FAMILIES.items():
            for s in samples:
                self.assertIn(s, flat,
                              f'{name} 的样本不在 ATTACK_SAMPLES 里：{s[:60]!r}')

    def test_every_attack_sample_has_a_family(self):
        for s in rule_corpus.ATTACK_SAMPLES:
            self.assertIn(s, rule_corpus.SAMPLE_FAMILY,
                          f'正样本没有族标签（基准会归到 unlabeled）：{s[:60]!r}')

    def test_family_names_do_not_shrink(self):
        """族数只增不减：删族必须显式改这里的名单，而不是悄悄掉下去。"""
        expected = {
            "injection_direct", "injection_indirect", "memory_poison",
            "multi_agent", "model_artifact", "lifecycle_hook",
            "device_primitive", "offensive_capability", "resource_exhaustion",
            "credential_exposure", "capability_selfdecl", "guardrail_tamper",
            "jailbreak_family", "tool_poison", "skill_poison",
            "supply_chain_exec", "evasion_variant",
        }
        self.assertEqual(expected, set(rule_corpus.ATTACK_FAMILIES))

    def test_index_grouped_families_are_still_aligned(self):
        """老族按 ATTACK_SAMPLES 定义序取索引，插样本会整族漂移。"""
        text = rule_corpus.ATTACK_SAMPLES
        self.assertIn("Ignore all previous instructions", text[0])
        self.assertIn("retrieved webpage says", text[7])
        self.assertIn("保存到记忆库", text[2])
        self.assertIn("append a rule to memory", text[3])
        self.assertIn("persist the instruction", text[5])
        self.assertIn("broadcast the task", text[6])
        self.assertIn("from_pretrained", text[9])
        self.assertIn("SessionStart hook", text[10])
        self.assertIn("adb shell", text[13])
        self.assertIn("fastboot flash", text[14])
        self.assertIn("exploit and shellcode", text[15])
        self.assertIn("token budget is exhausted", text[16])
        self.assertIn("Repeat the previous answer", text[18])
        self.assertIn("private_key=0x9f2c", text[20])
        self.assertIn("seed_phrase", text[21])
        self.assertIn("fuzzing across the fleet", text[22])
        self.assertIn("rewrites its own guardrail", text[23])
        self.assertIn("disable the verifier", text[25])
        self.assertIn("remove audit log entries", text[26])


class TestFamilyCoverageFloor(unittest.TestCase):
    """覆盖度下限：族在、样本在、规则也认。"""

    def test_no_family_is_under_populated(self):
        stat, gaps = rule_corpus.family_coverage(MIN_PER_FAMILY)
        self.assertEqual([], gaps,
                         "以下攻击面样本数低于 %d，基准读数在该面上无意义：%s"
                         % (MIN_PER_FAMILY, gaps))

    def test_every_family_has_at_least_one_serious_detection(self):
        """族级召回下限。规则掉了或样本被改弱，这里必须红而不是被 recall 摊平。"""
        dead = []
        for name, samples in rule_corpus.ATTACK_FAMILIES.items():
            covered = [s for s in samples if _serious(s)]
            if not covered:
                dead.append(name)
        self.assertEqual([], dead,
                         "以下攻击面整族 0 检出（规则库盲区或样本变质）：%s" % dead)

    def test_known_gap_samples_are_actually_covered_now(self):
        """缺口已补口径（2026-10-03 翻转）。

        这些样本是「曾经整族 0 检出」的攻击面，留在这里当回归见证人：规则库
        一旦被改弱、或样本被改写，这里立刻红。
        """
        gap_missed = [s for s in rule_corpus.KNOWN_GAP_SAMPLES if not _serious(s)]
        self.assertEqual([], gap_missed,
                         "以下已登记攻击面现在扫不出来了（规则被改弱或样本变质）：%r"
                         % [s[:50] for s in gap_missed])

    def test_known_gap_register_is_not_a_trash_can(self):
        """防「登记盲区」这扇门：新增登记项若扫不出，测试必须红。

        方向要紧——把断言写成「允许未检出」，就等于给自己发了一张「随时可
        以记录新盲区、CI 永不吱声」的通行证，而这正是本模块存在的目的。
        """
        src = open(os.path.join(ROOT, "scripts", "benchmark.py"),
                   encoding="utf-8").read()
        self.assertIn("known_gap_missed", src,
                      "benchmark 必须把未检出的已知盲区吐出来，否则这条口径无消费者")


class TestFamilyReportWiring(unittest.TestCase):
    """benchmark 必须把族级读数吐出来，否则这套语料组织没有消费者。"""

    def test_benchmark_reports_family_coverage(self):
        with open(os.path.join(ROOT, "scripts", "benchmark.py"),
                  encoding="utf-8") as f:
            src = f.read()
        self.assertIn("family_coverage", src)
        self.assertIn("family_gaps", src)

    def test_family_gaps_is_derived_from_zero_detected_families(self):
        with open(os.path.join(ROOT, "scripts", "benchmark.py"),
                  encoding="utf-8") as f:
            src = f.read()
        self.assertIn('if v["detected"] == 0', src,
                      "family_gaps 必须来自「整族 0 检出」，不能是硬编码白名单")


if __name__ == "__main__":
    unittest.main()
