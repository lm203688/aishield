"""
tests/test_benchmark.py — 安全基准 v1 的契约测试

被测对象：scripts/benchmark.py（基准语料 + 参数化矩阵 + 计分）。

基准这种东西最容易退化成一页好看的数字。所以这里钉住的不是「能跑」，而是四件
让它保持可信的性质：

  1. **确定性** —— 同一份代码跑两次必须得到完全相同的 JSON。只要有人引入随机
     采样或时间戳，数字就不再可比，基准也就不再是基准。
  2. **口径不可悄悄放宽** —— 召回下限与误报上限被写死在测试里。想降低标准就得
     改测试，改测试就会出现在 diff 里，藏不住。
  3. **语料不可悄悄缩减** —— 正负样本数有下限。删掉几个难缠的样本能让数字变好看，
     这条测试专门堵住这条路。
  4. **对照组保持干净** —— 良性样本里不得出现 `npx -y` / `--privileged` /
     `bash -c` 这类**本身就有风险**的写法。2026-09-19 首轮就把这个坑踩了：把风险
     启动器照搬进对照组，3 例真实检出被当成扫描器的误报记了一笔。

另外做了一次**隔离不变量**的源码级断言：基准脚本不得引入 socket / urllib /
requests / subprocess。一个"基准"如果能联网或执行被测对象，它测的就不是扫描器。
"""

import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import benchmark as B  # noqa: E402


# 目标准入门槛（当前实测值：recall 0.90 / fp 0.0 / 规则覆盖 1.00）。
# 留出一点余量，但不留太多 —— 门禁的意义是"退步就红"，不是"随便怎样都绿"。
MIN_RECALL = 0.85
MAX_FALSE_POSITIVE_RATE = 0.0

# 2026-09-20：召回下限从 0.95 降到 0.85，不是放宽标准，而是**换口径**。
# 此前 `recall` 是「指令面 any-finding + 配置面 serious-only」的混合求和
# （0.96），两个平面用了不同的检出线，那个数字无法被任何单一标准解读。
# 现在两平面统一到 serious_only，90% 是同一个标准下的真值，5 条未达可处理
# 严重度的样本已公开列在「检出缺口」里。混合口径的 96% 不是更优成绩，
# 是不自洽的记账。
MIN_COVERAGE = 1.00

# 语料规模下限。删样本可以让任何指标变好看，这里堵住。
MIN_POSITIVES = 50
MIN_NEGATIVES = 30


class TestDeterminism(unittest.TestCase):
    def test_two_runs_produce_identical_json(self):
        a = json.dumps(B.run(), ensure_ascii=False, sort_keys=True)
        b = json.dumps(B.run(), ensure_ascii=False, sort_keys=True)
        self.assertEqual(a, b, '基准不确定 —— 数字不可比，基准失去意义')

    def test_corpus_builders_are_pure(self):
        """语料构造不能依赖全局状态：调两次结果必须一致。"""
        self.assertEqual(B.malicious_config_samples(), B.malicious_config_samples())
        self.assertEqual(B.benign_config_samples(), B.benign_config_samples())

    def test_result_declares_its_invariants(self):
        inv = B.run()["invariants"]
        self.assertFalse(inv["network_calls"])
        self.assertFalse(inv["executes_scanned_configs"])
        self.assertTrue(inv["deterministic"])


class TestQualityGates(unittest.TestCase):
    """把当前的质量水平锁住：退步就红。"""

    def setUp(self):
        self.result = B.run()
        self.summary = self.result["summary"]

    def test_recall_does_not_regress(self):
        self.assertGreaterEqual(
            self.summary["recall"], MIN_RECALL,
            '召回退化到 %.4f（下限 %.2f）' % (self.summary["recall"], MIN_RECALL))

    def test_false_positive_rate_does_not_regress(self):
        self.assertLessEqual(
            self.summary["false_positive_rate"], MAX_FALSE_POSITIVE_RATE,
            '误报率上升到 %.4f —— 误报比漏报更伤信任' % self.summary["false_positive_rate"])

    def test_memory_plane_is_not_a_figurehead(self):
        """Plane D（Agent Memory）必须真跑、真被断言。

        这一面走的是 `agent_memory_analysis()` 另一条引擎（框架 API + 跨
        session 语义），不在 rules.analyze 的统计里。它只在单测中跑过、基准
        里没有，等于**宣称支持 8 个记忆框架但拿不出检出证据** —— 2026-10-02
        建这一面时立刻戳出真缺口：mem0 的官方写法 `client = mem0.MemoryClient();
        client.add(...)` 全类漏检（扫描器当时只认 `mem0.add(` 模块直调）。
        所以这里不只要它在，还要守住 recall=1.0 / fp=0，否则它会悄悄退化成
        一个永远绿的空壳。
        """
        planes = [p for p in self.result["planes"] if p.get("name") == "memory_plane"]
        self.assertEqual(len(planes), 1,
                         '基准里没有 memory_plane —— Agent Memory 面没有证据')
        m = planes[0]
        self.assertEqual(m["recall"], 1.0,
                         'Agent Memory 面漏检 %d/%d：%s'
                         % (len(m["missed"]), m["positives"], m["missed"]))
        self.assertEqual(m["false_positive_rate"], 0.0,
                         'Agent Memory 面误报：%s' % m["false_positive_ids"])
        # 四个攻击面必须有各自的检出记录，不能靠一条样本刷满
        self.assertEqual(len(m["by_axis"]) >= 4, True,
                         'Agent Memory 面的攻击面分轴不足，样本可能同质：%s' % sorted(m["by_axis"]))

    def test_no_serious_finding_fires_on_any_negative(self):
        """逐条点名：任何负样本上的 critical/high 都是缺陷，不是"统计噪声"。"""
        offenders = []
        for p in self.result["planes"]:
            offenders.extend(p.get("false_positive_ids") or [])
            offenders.extend("instruction_sample_#%d" % i
                             for i in p.get("false_positive_indices") or [])
        self.assertEqual(offenders, [], '负样本被误判：%s' % offenders)

    def test_corpus_has_not_been_shrunk(self):
        # 2026-10-02：DESCRIPTION_SAMPLES（讨论性描述，描述攻击而非攻击本身）
        # 从 positive 分母剔出。重分类**不计入缩水**，但必须**留痕** ——
        # 把 description_samples_excluded 加回分母，等价于「总语料量不得减少」：
        # 想抵消这条，只能老老实实往 DESCRIPTION_SAMPLES 里放样本，而那条
        # 样本随后还要过 description_serious_hits 的误报检查。偷偷删一条正样本
        # 不留痕的写法，在这个断言下会直接掉到下限以下。
        excluded = 0
        for p in self.result["planes"]:
            excluded += p.get("description_samples_excluded") or 0
        self.assertGreaterEqual(self.summary["positives"] + excluded, MIN_POSITIVES,
                                '正样本被删到 %d 条且未留痕（下限 %d，含剔除 %d）'
                                % (self.summary["positives"], MIN_POSITIVES, excluded))
        self.assertGreaterEqual(self.summary["negatives"], MIN_NEGATIVES,
                                '负样本被删到 %d 条（下限 %d）' % (self.summary["negatives"], MIN_NEGATIVES))

    def test_coverage_does_not_regress(self):
        """规则覆盖率不达标意味着规则层开始认不得攻击意图了。"""
        self.assertGreaterEqual(
            self.summary["recall_any"], MIN_COVERAGE,
            '规则覆盖率退化到 %.4f（下限 %.2f）' % (self.summary["recall_any"], MIN_COVERAGE))

    def test_coverage_not_below_recall(self):
        """覆盖率不可能低于召回率 —— 达到可处理严重度必然先有 finding。

        两者倒挂只可能是口径又分裂了（比如召回按 any-finding、覆盖按
        serious-only）。这条断言把顺序钉死，不依赖具体数字。
        """
        self.assertGreaterEqual(self.summary["recall_any"], self.summary["recall"],
                                '规则覆盖率 %.4f 低于召回率 %.4f —— 口径可能又分裂了'
                                % (self.summary["recall_any"], self.summary["recall"]))


class TestInstructionPlaneFeedsAgentInstructions(unittest.TestCase):
    """指令面必须按「agent 指令」而非「人类文档」喂样。

    2026-09-20 从 `sample.md` 改过来。`sample.md` 会命中 analyze() 的 is_doc
    文档降级，让每条攻击样本的 critical 被压成 low，serious-only 召回因此是
    0/28 —— 那个 0 不是扫描器看不见注入，是基准把攻击标注成了文档。
    与 ATTACK_SAMPLES[2]（叙述体被标成正样本）是同一类标注错误。

    三条依据写在 benchmark._plane_a 的注释里：样本是 agent 指令攻击；生产路径
    check_prompt_injection 不施加文档降级；良性侧早已用 skills/ 喂样。
    """

    def src(self):
        return open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'benchmark.py'),
                    encoding='utf-8').read()

    def test_uses_agent_instruction_path(self):
        src = self.src()
        self.assertIn('skills/%s_%02d.md', src,
                      '指令面未使用 skills/ 路径喂样 —— is_doc 降级会把召回压回 0/28')
        self.assertNotIn('analyze({"sample.md"', src,
                         '指令面退回 sample.md 喂样 —— 攻击被当成文档，serious 召回会归零')

    def test_injection_sample_reaches_serious_severity(self):
        """行为级断言：旗舰注入样本必须给到可处理的严重度。

        不依赖具体路径写法 —— 只要基准算出来的 serious 召回还是 0/28 就红。
        """
        p = self.result = B.run()["planes"][0]
        self.assertGreaterEqual(
            p["recall"], 0.5,
            '指令面 serious 召回 %.4f —— is_doc 降级可能又被吃进基准了' % p["recall"])

    def test_benign_side_uses_same_path_convention(self):
        """正负两侧必须同一类路径，否则严重度口径不可比。"""
        src = self.src()
        self.assertIn('_path(i, "payload")', src)
        self.assertIn('_path(i, "skill")', src)


class TestBarsAreUnifiable(unittest.TestCase):
    """两平面的检出线必须一致，否则总分不可比。

    2026-09-20 修的正是这个：指令面用 any_finding、配置面用 serious_only，
    相加得到的「召回率」不是任何单一标准下的数字，容易被读成严肃告警下的
    召回。总分是两平面之和，这个前提必须先成立。
    """

    def setUp(self):
        self.result = B.run()

    def test_all_planes_share_one_detection_bar(self):
        """Plane A/B 的检出线必须一致（Plane C 无此概念，跳过）。"""
        bars = set(p.get("detection_bar") for p in self.result["planes"]
                   if p.get("name") != "harness_plane")
        self.assertEqual(bars, {"serious_only"},
                         '平面检出线不统一：%s —— 总分成了混合口径求sum' % sorted(bars))

    def test_all_planes_share_one_coverage_bar(self):
        """Plane A/B 的覆盖线必须一致（Plane C 无此概念，跳过）。"""
        bars = set(p.get("coverage_bar") for p in self.result["planes"]
                   if p.get("name") != "harness_plane")
        self.assertEqual(bars, {"any_finding"},
                         '平面覆盖线不统一：%s' % sorted(bars))

    def test_summary_declares_its_bars(self):
        """总分必须自己声明口径，不能让读者去猜。"""
        s = self.result["summary"]
        self.assertEqual(s["detection_bar"], "serious_only")
        self.assertEqual(s["coverage_bar"], "any_finding")

    def test_no_coverage_false_positive_rate(self):
        """副口径不得配误报率。

        良性配置/文档上的 low/info 命中是信息性标注（「该配置使用运行时拉包」），
        不是误报。给它算 fp 会得到 40%+ 这种既不可操作也无法治理的数字 ——
        那个数字会诱导人去「优化」规则，把真正需要报的也一起压掉。
        """
        for p in self.result["planes"]:
            self.assertNotIn("false_positive_rate_any", p,
                             '%s 给副口径配了误报率' % p["name"])
        self.assertNotIn("false_positive_rate_any", self.result["summary"],
                         '总分给副口径配了误报率')


class TestParameterization(unittest.TestCase):
    """参数化是这一版基准的核心借鉴定：一个意图 × 多种表面写法。"""

    def test_all_four_axes_are_exercised(self):
        axes = set()
        for s in B.malicious_config_samples():
            axes.update(k for k in s if k.startswith("axis_"))
        self.assertIn("axis_launcher", axes)
        self.assertIn("axis_credential", axes)
        self.assertIn("axis_transport", axes)
        self.assertIn("axis_risky_form", axes)

    def test_every_axis_bucket_has_at_least_two_variants(self):
        """每个轴至少两种写法 —— 只有一种写法的"轴"等于没测。

        `axis_risky_form` 是有意每种写法只放一条（它回答的是"仅凭写法够不够判"），
        所以单独豁免。
        """
        buckets = {}
        for s in B.malicious_config_samples():
            for k, v in s.items():
                if k.startswith("axis_"):
                    buckets.setdefault(k, set()).add(v)
        for axis, values in buckets.items():
            if axis == "axis_risky_form":
                continue
            self.assertGreaterEqual(len(values), 2,
                                    '%s 只有一种写法：%s' % (axis, values))

    def test_parameterization_is_not_cosmetic(self):
        """不同写法必须产生不同字节内容，否则"变体"只是标签。"""
        contents = [s["content"] for s in B.malicious_config_samples()]
        self.assertEqual(len(contents), len(set(contents)), '存在内容重复的"变体"')


class TestBenignControlsAreActuallyBenign(unittest.TestCase):
    """对照组必须干净，否则误报统计是假的。

    2026-09-19 首轮把 `npx -y` / `bash -c` / 无鉴权远程 URL 照搬进良性组，扫描器
    正确地报了 high，却被记成 3 例误报。差别不在扫描器，在对照组。
    """

    RISKY_MARKERS = ("npx -y", "-y ", "--privileged", "bash -c", "sh -c")

    def test_benign_configs_avoid_risky_launch_forms(self):
        offenders = []
        for s in B.benign_config_samples():
            low = s["content"].lower()
            for marker in self.RISKY_MARKERS:
                if marker in low:
                    offenders.append('%s 含风险写法 %r' % (s["id"], marker))
        self.assertEqual(offenders, [], '\n'.join(offenders))

    def test_benign_configs_do_not_carry_inline_credentials(self):
        """良性配置里放明文凭证就不是良性配置了 —— 那会制造记账混乱。"""
        for s in B.benign_config_samples():
            low = s["content"].lower()
            self.assertNotIn("ghp_", low, s["id"])
            self.assertNotIn("akia", low, s["id"])

    def test_defense_text_samples_are_present(self):
        """防御工具自述是误报重灾区，必须留在负样本里而不是被"优化"掉。"""
        self.assertGreaterEqual(len(B.DEFENSE_TEXT_SAMPLES), 5)
        joined = " ".join(B.DEFENSE_TEXT_SAMPLES).lower()
        self.assertIn("prompt injection", joined)


class TestBenchmarkIsolation(unittest.TestCase):
    """基准脚本不得联网、不得执行任何东西 —— 否则它测的不是扫描器。"""

    def setUp(self):
        self.src = open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'benchmark.py'),
                        encoding='utf-8').read()

    def test_no_network_or_subprocess_imports(self):
        for bad in ('import socket', 'import urllib', 'import requests',
                    'import subprocess', 'from socket', 'import http.client'):
            self.assertNotIn(bad, self.src, '基准脚本引入了 %r' % bad)

    def test_marks_itself_as_a_benchmark_not_a_scanner(self):
        self.assertIn('aishield-security-benchmark/v1', self.src)


class TestCliGates(unittest.TestCase):
    def test_fail_flags_are_wired(self):
        """CI 门禁要能真的让退出码变红，不能只是打印。"""
        self.assertIn('--fail-under-recall', self.src_of_main())
        self.assertIn('rc = 1', self.src_of_main())

    def src_of_main(self):
        return open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'benchmark.py'),
                    encoding='utf-8').read()

    def test_gate_returns_nonzero_on_impossible_threshold(self):
        rc = B.main(['--fail-under-recall', '1.5'])
        self.assertEqual(rc, 1, '不可能达到的阈值也必须让退出码变红')

    def test_gate_returns_zero_when_thresholds_are_satisfied(self):
        rc = B.main(['--fail-under-recall', '0.0', '--fail-over-fp', '1.0'])
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
