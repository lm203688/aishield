# -*- coding: utf-8 -*-
"""shadow / enforce 双模式 + 雷达规则加载期字段契约的测试（2026-09-18 新增）。

补的洞：

1. promote_rule.py 原先只有"干"或"不干"两种结果，闸门在 CI 里无法**观测**。
   `--check` 只跑 schema / 良性语料，是否能在攻击语料上命中（catch）要等
   `--promote-all` 落库之后才由 radar_effect 事后报告，而后者是非阻断告警。
   结果：一条零命中的死规则会直接进线上，之后才被当成"带刺的铃铛"报告出来。
   现在 `--shadow` 能在**不写任何文件**的前提下给出 promote / warn / refuse
   三档判定，可以挂进 CI 当观测门。
2. scanner/rules.py 的雷达加载器原先对坏条目 `except: continue` 静默丢弃，
   severity 完全不校验、正则也完全不在加载期编译。两条后果：一条坏正则会等
   到扫描时才 re.error，把整次扫描打崩；一条被吞的规则等于一条不存在的规则，
   而报告里看不出任何差异（假绿）。现在字段契约在加载期执行，拒收条目进隔离
   区，可通过 get_radar_load_warnings() 读到。
"""

import copy
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import promote_rule  # noqa: E402
import radar_effect  # noqa: E402
import rule_corpus  # noqa: E402

# 三条候选规则，各覆盖一个判定档。
CATCH_PATTERN = "credential theft"       # 命中 ATTACK_SAMPLES[1]，不误报良性语料
CATCH_PATTERN2 = r"evil\.sh"             # 命中 ATTACK_SAMPLES[10,11]，同样零误报
DEAD_PATTERN = "backdoor\\s*(trigger|hook)"  # 结构上合法，但攻击语料里不存在
FP_PATTERN = "npm install"               # 命中良性语料里的 README 安装说明


def _read_text(path):
    """读整份文件；不存在时返回 None，便于做 before/after 断言。"""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def _candidate(tmp, name, pattern, status="ready", description="d", severity="high"):
    path = os.path.join(tmp, "PROPOSED_%s.json" % name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "status": status,
            "signal": {"title": "t", "url": "https://example.com/x", "source": "s"},
            "attack_category": "test-cat",
            "rules": [{"pattern": pattern, "description": description,
                       "severity": severity}],
        }, f)
    return path


class _Isolated(unittest.TestCase):
    """把脚本模块的数据路径全部重定向到临时目录，绝不碰仓库真实数据。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="aishield_shadow_")
        self._saved = {}
        for attr in ("RADAR_RULES", "SNAPSHOT_DIR", "LEDGER", "PROPOSED_DIR"):
            self._saved[attr] = getattr(promote_rule, attr)
        promote_rule.RADAR_RULES = os.path.join(self.tmp, "data", "radar_rules.json")
        promote_rule.SNAPSHOT_DIR = os.path.join(self.tmp, "data", "snapshots")
        promote_rule.LEDGER = os.path.join(self.tmp, "data", "state", "ledger.jsonl")
        promote_rule.PROPOSED_DIR = self.tmp
        self._saved["sync_readme_counts"] = promote_rule.sync_readme_counts
        promote_rule.sync_readme_counts = lambda: False
        self._saved["_evaluate_effect"] = promote_rule._evaluate_effect
        promote_rule._evaluate_effect = lambda: None
        # 效果台账与规则文件都要隔离：shadow 传了 save=False，但 enforce 路径
        # 可能写它；radar_effect.RADAR_RULES 必须一起重定向，否则默认参数会
        # 读回仓库真实文件（test_evaluate_default_* 就是被这个坑到）
        self._saved["EFFECT_FILE"] = radar_effect.EFFECT_FILE
        radar_effect.EFFECT_FILE = os.path.join(self.tmp, "data", "state",
                                                 "radar_effect.json")
        self._saved["EFFECT_RADAR_RULES"] = radar_effect.RADAR_RULES
        radar_effect.RADAR_RULES = os.path.join(self.tmp, "data",
                                                 "radar_rules.json")

    def tearDown(self):
        for attr, val in self._saved.items():
            if attr.startswith("EFFECT_"):
                setattr(radar_effect, attr[len("EFFECT_"):], val)
            else:
                setattr(promote_rule, attr, val)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_rules(self, rules):
        path = promote_rule.RADAR_RULES
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "rules": rules, "provenance": {}}, f)

    def _data(self, path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)


class TestShadowVerdicts(_Isolated):

    def test_promote_when_validation_passes_and_catch_is_nonzero(self):
        path = _candidate(self.tmp, "catch", CATCH_PATTERN)
        v = promote_rule.shadow(path, self._data(path), known_patterns=set())
        self.assertEqual(v["verdict"], "promote", v["problems"])
        self.assertEqual(v["zero_catch"], 0)
        self.assertEqual(v["false_positives"], 0)
        self.assertTrue(v["rules"][0]["catch"])

    def test_warn_when_the_rule_catches_nothing(self):
        path = _candidate(self.tmp, "dead", DEAD_PATTERN)
        v = promote_rule.shadow(path, self._data(path), known_patterns=set())
        self.assertEqual(v["verdict"], "warn")
        self.assertEqual(v["zero_catch"], 1)
        self.assertEqual(v["problems"], [])

    def test_refuse_when_the_rule_false_positives_on_benign_input(self):
        path = _candidate(self.tmp, "fp", FP_PATTERN)
        v = promote_rule.shadow(path, self._data(path), known_patterns=set())
        self.assertEqual(v["verdict"], "refuse")
        self.assertTrue(v["rules"][0]["false_positive"])
        # 良性样本片段要一起报出来，否则无从判断为什么被拒
        self.assertTrue(v["problems"], "误报必须有可读的原因说明")

    def test_refuse_when_schema_validation_fails(self):
        path = _candidate(self.tmp, "draft", CATCH_PATTERN, status="draft")
        v = promote_rule.shadow(path, self._data(path), known_patterns=set())
        self.assertEqual(v["verdict"], "refuse")
        self.assertTrue(any("expected 'ready'" in p for p in v["problems"]))

    def test_shadow_all_exit_code_is_one_when_anything_is_wrong(self):
        _candidate(self.tmp, "catch", CATCH_PATTERN)
        _candidate(self.tmp, "dead", DEAD_PATTERN)
        verdicts, code = promote_rule.shadow_all()
        self.assertEqual(len(verdicts), 2)
        self.assertEqual(code, 1, "存在 warn 候选时必须非零退出，才能当 CI 门用")

    def test_catch_patterns_really_catch(self):
        """前置条件自检：两个"干净候选"必须真的命中攻击语料。

        这条前置断言是被一次真实失败逼出来的：clean 用例原来给第二条候选
        写的是 `jailbreak\\s+prompt`，而它**在攻击语料里一条都打不中** ——
        shadow 按定义把它判成 warn（零命中 = 死规则），于是"全干净应当
        exit 0"这个断言就挂了。挂的原因是数据、不是逻辑，但在没这条
        前置断言时，症状看起来完全像"shadow 的退出码算错了"。
        """
        for pattern in (CATCH_PATTERN, CATCH_PATTERN2):
            hits = [s for s in rule_corpus.ATTACK_SAMPLES
                    if re.search(pattern, s, re.I)]
            self.assertTrue(hits, f'候选模式在攻击语料里零命中：{pattern}')

    def test_shadow_all_exit_code_zero_when_everything_is_clean(self):
        _candidate(self.tmp, "catch", CATCH_PATTERN)
        _candidate(self.tmp, "catch2", CATCH_PATTERN2)
        verdicts, code = promote_rule.shadow_all()
        self.assertEqual(code, 0, verdicts)
        self.assertEqual(len(verdicts), 2)

    def test_rejected_candidates_are_ignored_by_shadow_all(self):
        _candidate(self.tmp, "ok", CATCH_PATTERN)
        _candidate(self.tmp, "bad", CATCH_PATTERN, status="rejected")
        verdicts, _ = promote_rule.shadow_all()
        self.assertEqual(len(verdicts), 1)


class TestShadowWritesNothing(_Isolated):
    """shadow 的契约就是"一个字都不写"。任何写入都会让它可以被并发误触发。"""

    def test_shadow_mutates_no_file_on_disk(self):
        self._write_rules({r"existing\s*rule": ["d", "high"]})
        path = _candidate(self.tmp, "catch", CATCH_PATTERN)
        with open(path, "rb") as f:
            original_bytes = f.read()

        v = promote_rule.shadow(path, self._data(path), known_patterns=set())
        self.assertEqual(v["wrote"], [], "verdict 必须声明自己没写任何东西")

        self.assertEqual(v["verdict"], "promote")
        # 线上规则没被碰
        self.assertNotIn(CATCH_PATTERN, promote_rule.load_radar_rules()["rules"])
        # 候选文件没被归档
        self.assertTrue(os.path.exists(path))
        with open(path, "rb") as f:
            self.assertEqual(f.read(), original_bytes)
        # 台账 / 快照 / 效果台账都没被创建
        self.assertFalse(os.path.exists(promote_rule.LEDGER))
        self.assertFalse(os.path.exists(radar_effect.EFFECT_FILE))
        self.assertEqual(promote_rule.list_snapshots(), [])

    def test_shadow_runs_repeatably_with_identical_output(self):
        """shadow 没有副作用 → 重复运行结果必须逐字一致。"""
        self._write_rules({r"existing\s*rule": ["d", "high"]})
        path = _candidate(self.tmp, "catch", CATCH_PATTERN)
        a = promote_rule.shadow(path, self._data(path), known_patterns=set())
        b = promote_rule.shadow(path, self._data(path), known_patterns=set())
        for key in ("verdict", "problems", "would_add", "rules",
                    "zero_catch", "false_positives", "radar_rules_before",
                    "radar_rules_after"):
            self.assertEqual(a[key], b[key], key)


class TestEnforceConsultsShadow(_Isolated):

    def test_dead_rule_is_promoted_with_a_warning_by_default(self):
        """默认保持历史行为：死规则会进线上，但必须大声告警。

        不能把零命中当硬拒绝——雷达规则来自新信号，ATTACK_SAMPLES 是固定语料，
        全新攻击类型天然不在其中；硬拒会让整个晋升循环停摆。
        """
        path = _candidate(self.tmp, "dead", DEAD_PATTERN)
        n = promote_rule.promote(path, self._data(path))
        self.assertEqual(n, 1)
        self.assertIn(DEAD_PATTERN, promote_rule.load_radar_rules()["rules"])

    def test_strict_refuses_a_dead_rule(self):
        path = _candidate(self.tmp, "dead", DEAD_PATTERN)
        did, code, _note = promote_rule._try_promote_one(
            path, self._data(path), known=set(), strict=True)
        self.assertFalse(did)
        self.assertEqual(code, 3)
        self.assertNotIn(DEAD_PATTERN, promote_rule.load_radar_rules()["rules"])

    def test_strict_allows_a_rule_that_catches(self):
        path = _candidate(self.tmp, "catch", CATCH_PATTERN)
        did, code, _note = promote_rule._try_promote_one(
            path, self._data(path), known=set(), strict=True)
        self.assertTrue(did, code)
        self.assertEqual(code, 0)

    def test_cmd_promote_all_strict_skips_dead_rules_and_exits_nonzero(self):
        _candidate(self.tmp, "catch", CATCH_PATTERN)
        _candidate(self.tmp, "dead", DEAD_PATTERN)
        code = promote_rule.cmd_promote_all(strict=True)
        self.assertEqual(code, 1, "strict 下跳过死规则必须让 CI 看见")
        rules = promote_rule.load_radar_rules()["rules"]
        self.assertIn(CATCH_PATTERN, rules)
        self.assertNotIn(DEAD_PATTERN, rules)

    def test_cmd_promote_all_default_exits_zero(self):
        _candidate(self.tmp, "catch", CATCH_PATTERN)
        _candidate(self.tmp, "dead", DEAD_PATTERN)
        self.assertEqual(promote_rule.cmd_promote_all(strict=False), 0,
                         "默认行为必须保持向后兼容（rule-promoter.yml 依赖它）")


class TestSimulateAndInMemoryEffect(_Isolated):

    def test_simulate_does_not_mutate_the_input_store(self):
        store = {"version": 1,
                 "rules": {r"existing\s*rule": ["d", "high"]},
                 "provenance": {r"existing\s*rule": {"signal_url": "u"}}}
        before = copy.deepcopy(store)
        path = _candidate(self.tmp, "catch", CATCH_PATTERN)
        sim = promote_rule.simulate(store, self._data(path))
        self.assertEqual(store, before, "simulate 必须只改副本")
        self.assertIn(CATCH_PATTERN, sim["rules"])
        self.assertEqual(len(sim["rules"]), 2)
        self.assertNotIn(CATCH_PATTERN, store["rules"])

    def test_evaluate_with_a_store_does_not_write_the_live_file(self):
        self._write_rules({r"existing\s*rule": ["d", "high"]})
        effect_before = _read_text(radar_effect.EFFECT_FILE)

        sim = {"rules": {DEAD_PATTERN: ["d", "high"]}, "provenance": {}}
        store = radar_effect.evaluate(store=sim, save=False)

        self.assertIn(DEAD_PATTERN, store["rules"])
        self.assertFalse(store["rules"][DEAD_PATTERN]["catch"])
        self.assertEqual(
            _read_text(radar_effect.EFFECT_FILE),
            effect_before, "save=False 不得改写效果台账")
        # 线上规则文件也不得被碰
        self.assertEqual(promote_rule.load_radar_rules()["rules"],
                         {r"existing\s*rule": ["d", "high"]})

    def test_evaluate_default_still_reads_the_live_file(self):
        self._write_rules({DEAD_PATTERN: ["d", "high"]})
        store = radar_effect.evaluate(save=False)
        self.assertIn(DEAD_PATTERN, store.get("rules", {}),
                      "不带 store 时必须是历史行为：读线上文件")


class TestRadarLoadContract(unittest.TestCase):
    """雷达规则的加载期字段契约：拒收必须可见，import 绝不能崩。"""

    def setUp(self):
        import scanner.rules as scanner_rules
        self.rules = scanner_rules
        self.tmp = tempfile.mkdtemp(prefix="aishield_contract_")
        os.makedirs(os.path.join(self.tmp, "data"), exist_ok=True)
        self.path = os.path.join(self.tmp, "data", "radar_rules.json")
        self._file = scanner_rules.__file__
        # _load_radar_rules() 从 __file__ 推导数据路径；重定向它即可隔离。
        scanner_rules.__file__ = os.path.join(self.tmp, "scanner", "rules.py")

    def tearDown(self):
        self.rules.__file__ = self._file
        self.rules._load_radar_rules()  # 恢复真实仓库状态
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, rules):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "rules": rules, "provenance": {}}, f)

    def _reload(self):
        # 清空再载入，让计数类断言确定（_load_radar_rules 是累加的）。
        self.rules.RADAR_RULES = {}
        self.rules._load_radar_rules()
        return self.rules.get_radar_load_warnings()

    def test_valid_entry_loads_with_no_warnings(self):
        self._write({CATCH_PATTERN: ["凭证窃取", "high"]})
        self.assertEqual(self._reload(), {})
        self.assertIn(CATCH_PATTERN, self.rules.RADAR_RULES)
        self.assertEqual(self.rules.RADAR_RULES[CATCH_PATTERN][1], "high")

    def test_bad_severity_is_quarantined_not_silently_dropped(self):
        """拒收要可见：pattern 必须以键的形式出现在隔离区，理由要可读。"""
        self._write({CATCH_PATTERN: ["凭证窃取", "catastrophic"]})
        w = self._reload()
        self.assertEqual(len(w), 1)
        self.assertIn(CATCH_PATTERN, w, "被拒条目必须能被点名，不能无声消失")
        self.assertNotIn(CATCH_PATTERN, self.rules.RADAR_RULES)
        self.assertTrue(any("severity" in m for m in w[CATCH_PATTERN]), w)

    def test_todo_description_is_quarantined(self):
        self._write({CATCH_PATTERN: ["TODO fill this in", "high"]})
        w = self._reload()
        self.assertEqual(len(w), 1)
        self.assertTrue(any("TODO" in m for m in w[list(w)[0]]), w)

    def test_non_string_description_is_quarantined(self):
        self._write({CATCH_PATTERN: [None, "high"]})
        self.assertEqual(len(self._reload()), 1)

    def test_wrong_shape_value_is_quarantined(self):
        self._write({CATCH_PATTERN: ["只有描述没有严重级别"]})
        w = self._reload()
        self.assertEqual(len(w), 1)
        self.assertTrue(any("长度为 2" in m for m in w[CATCH_PATTERN]), w)

    def test_regex_that_does_not_compile_is_quarantined(self):
        """加载期编译正则 = 一条坏正则在加载期就被拦住，而不是炸掉整次扫描。"""
        self._write({"(unclosed": ["坏正则", "high"]})
        w = self._reload()
        self.assertEqual(len(w), 1)
        self.assertTrue(any("无法编译" in m for m in w["(unclosed"]), w)

    def test_over_broad_regex_is_quarantined(self):
        self._write({"(?:a)*": ["过宽", "high"]})
        w = self._reload()
        self.assertEqual(len(w), 1)
        self.assertTrue(any("过宽" in m for m in w["(?:a)*"]), w)

    def test_non_string_pattern_key_is_rejected_by_the_validator(self):
        """直接测校验器：json.dump 会把 int 键转成字符串，走 JSON 路径到不了。

        校验器仍必须拒绝它——它可能被非 JSON 的调用方复用（从内存 dict 重建、
        从其它格式导入），空键 / 非字符串键在任何来源下都该被拒收，否则
        get_radar_load_warnings() 里会出现无法用 pattern 名定位的条目。
        """
        problems = self.rules._validate_radar_entry(123, ["d", "high"])
        self.assertTrue(any("pattern key" in m for m in problems), problems)
        self.assertEqual(
            self.rules._validate_radar_entry("", ["d", "high"]),
            ["pattern key 为空或非字符串"])

    def test_one_bad_entry_does_not_prevent_good_ones_from_loading(self):
        """隔离必须是条目级的：一条坏条目不能拖走同文件里的其它规则。"""
        self._write({
            CATCH_PATTERN: ["好规则", "high"],
            r"existing\s*rule": ["好规则二", "medium"],
            "(unclosed": ["坏规则", "high"],
        })
        w = self._reload()
        self.assertEqual(len(w), 1)
        self.assertIn(CATCH_PATTERN, self.rules.RADAR_RULES)
        self.assertIn(r"existing\s*rule", self.rules.RADAR_RULES)

    def test_missing_file_still_degrades_silently(self):
        """文件缺失 = 首次晋升前的状态，静默降级是设计意图。"""
        if os.path.exists(self.path):
            os.remove(self.path)
        self.assertEqual(self._reload(), {})

    def test_whole_file_corrupt_still_degrades_silently(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{ this is not json")
        self.assertEqual(self._reload(), {},
                         "整体损坏走原有的静默降级路径（基础规则不受影响）")

    def test_quarantine_count_is_exposed_via_meta(self):
        self._write({CATCH_PATTERN: ["好", "high"], "(unclosed": ["坏", "high"]})
        self._reload()
        meta = self.rules.get_radar_rules_meta()
        self.assertEqual(meta["quarantined"], 1)
        self.assertEqual(meta["total_rules"], 1)


if __name__ == "__main__":
    unittest.main()
