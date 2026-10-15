# -*- coding: utf-8 -*-
"""
规则晋升的快照 / 回滚 / 台账测试（2026-09-16 新增）。

补的洞：promote() 原先直接覆盖写 data/radar_rules.json，且 _evaluate_effect()
是**事后** best-effort 告警（其 docstring 明写 "effect measurement must never
break promotion"）——一条误报规则会先落库成为线上规则，然后才被报告为误报，
届时已无任何回滚手段。借鉴 PenguinHarness 的 snapshot+rollback 闭环。

同一批改动还修了语料漂移：BENIGN_CORPUS 曾在 promote_rule.py 与 radar_effect.py
各存一份互为镜像，一边扩宽另一边看不见。现统一收口到 scripts/rule_corpus.py，
本文件用对象同一性钉死，防止重新分叉。
"""

import json
import os
import shutil
import sys
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import promote_rule  # noqa: E402
import radar_effect  # noqa: E402
import rule_corpus  # noqa: E402

GOOD = {"pattern": "backdoor\\s*(trigger|hook)", "description": "d", "severity": "high"}


def _candidate(tmp):
    path = os.path.join(tmp, 'PROPOSED_20260916_test_candidate.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({
            "status": "ready",
            "signal": {"title": "t", "url": "https://example.com/x", "source": "s"},
            "attack_category": "test-cat",
            "rules": [dict(GOOD)],
        }, f)
    return path


def _write_rules(path, rules):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'version': 1, 'rules': rules, 'provenance': {}}, f)


class _Isolated(unittest.TestCase):
    """把脚本模块的数据路径全部重定向到临时目录，绝不碰仓库真实数据。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='aishield_promote_')
        self._pr = {}
        for mod in (promote_rule,):
            for attr in ('RADAR_RULES', 'SNAPSHOT_DIR', 'LEDGER', 'PROPOSED_DIR',
                     'EVOLUTION_LEDGER'):
                self._pr[(mod, attr)] = getattr(mod, attr)
        promote_rule.RADAR_RULES = os.path.join(self.tmp, 'data', 'radar_rules.json')
        promote_rule.SNAPSHOT_DIR = os.path.join(self.tmp, 'data', 'snapshots')
        promote_rule.LEDGER = os.path.join(self.tmp, 'data', 'state', 'ledger.jsonl')
        promote_rule.PROPOSED_DIR = self.tmp
        promote_rule.EVOLUTION_LEDGER = os.path.join(
            self.tmp, 'data', 'state', 'evolution_ledger.jsonl')
        # promote() 会连带改写 mcp-server/README.md —— 测试里禁用
        self._pr[('sync_readme_counts',)] = promote_rule.sync_readme_counts
        promote_rule.sync_readme_counts = lambda: False

    def tearDown(self):
        for key, val in self._pr.items():
            if isinstance(key, tuple) and len(key) == 2:
                setattr(key[0], key[1], val)
            else:
                setattr(promote_rule, key[0], val)
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestSnapshotBeforePromotion(_Isolated):

    def test_promote_writes_a_snapshot_of_the_pre_state(self):
        before = {r'first\s*rule': ['d', 'high']}
        _write_rules(promote_rule.RADAR_RULES, before)

        path = _candidate(self.tmp)
        n = promote_rule.promote(path, json.load(open(path, encoding='utf-8')),
                                approved_by='test-approver')

        self.assertEqual(n, 1)
        snaps = promote_rule.list_snapshots()
        self.assertEqual(len(snaps), 1, '晋升前必须留下一个回滚点')
        with open(snaps[0][0], encoding='utf-8') as f:
            self.assertEqual(json.load(f)['rules'], before,
                             '快照内容必须等于晋升前状态')
        # 线上状态确实变了
        self.assertIn(GOOD['pattern'], promote_rule.load_radar_rules()['rules'])

    def test_promote_without_existing_file_skips_snapshot(self):
        """首次晋升没有旧状态可留 —— 不得报错、不得造出空快照。"""
        path = _candidate(self.tmp)
        n = promote_rule.promote(path, json.load(open(path, encoding='utf-8')),
                                approved_by='test-approver')
        self.assertEqual(n, 1)
        self.assertEqual(promote_rule.list_snapshots(), [])

    def test_snapshots_are_never_overwritten_within_one_second(self):
        """连续两次晋升（同一秒内）不得让第一个回滚点消失。"""
        _write_rules(promote_rule.RADAR_RULES, {r'first\s*rule': ['d', 'high']})
        for i in range(2):
            path = os.path.join(self.tmp, 'PROPOSED_20260916_c%d.json' % i)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({
                    "status": "ready",
                    "signal": {"title": "t", "url": "u", "source": "s"},
                    "attack_category": "c",
                    "rules": [{"pattern": "evil%d\\s*payload" % i,
                               "description": "d", "severity": "high"}],
                }, f)
            promote_rule.promote(path, json.load(open(path, encoding='utf-8')),
                                approved_by='test-approver')
        self.assertEqual(len(promote_rule.list_snapshots()), 2,
                         '快照名必须唯一，否则回滚点被覆盖')


class TestRollback(_Isolated):

    def _promote_one(self, i=0):
        path = os.path.join(self.tmp, 'PROPOSED_20260916_r%d.json' % i)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "status": "ready",
                "signal": {"title": "t", "url": "u", "source": "s"},
                "attack_category": "c",
                "rules": [{"pattern": "rollback%d\\s*exploit" % i,
                           "description": "d", "severity": "high"}],
            }, f)
        promote_rule.promote(path, json.load(open(path, encoding='utf-8')),
                                approved_by='test-approver')

    def test_rollback_restores_the_exact_pre_state(self):
        before = {r'original\s*rule': ['d', 'high']}
        _write_rules(promote_rule.RADAR_RULES, before)
        self._promote_one()
        promoted_state = json.load(open(promote_rule.RADAR_RULES, encoding='utf-8'))['rules']
        self.assertIn('rollback0\\s*exploit', promoted_state)

        code, target = promote_rule.rollback(approved_by='test-approver')
        self.assertEqual(code, 0, '回滚必须成功: %s' % target)
        after = json.load(open(promote_rule.RADAR_RULES, encoding='utf-8'))['rules']
        self.assertEqual(after, before, '回滚后必须逐字恢复晋升前状态')

    def test_rollback_saves_the_current_state_first(self):
        """回滚本身也可能回错方向 —— 回滚前必须先留一个回滚点。"""
        _write_rules(promote_rule.RADAR_RULES, {r'base\s*rule': ['d', 'high']})
        self._promote_one()
        before_n = len(promote_rule.list_snapshots())

        promote_rule.rollback(approved_by='test-approver')

        self.assertEqual(len(promote_rule.list_snapshots()), before_n + 1,
                         '回滚未先快照当前状态，回错了无法撤销')

    def test_rollback_without_snapshots_fails_loudly(self):
        code, msg = promote_rule.rollback(approved_by='test-approver')
        self.assertEqual(code, 2, '无快照必须非 0 退出')
        self.assertIn('没有可用快照', msg)

    def test_rollback_to_missing_snapshot_fails_loudly(self):
        code, msg = promote_rule.rollback('no_such_snapshot.json',
                                  approved_by='test-approver')
        self.assertEqual(code, 2)
        self.assertIn('快照不存在', msg)

    def test_rollback_accepts_bare_filename(self):
        _write_rules(promote_rule.RADAR_RULES, {r'base\s*rule': ['d', 'high']})
        self._promote_one()
        name = os.path.basename(promote_rule.list_snapshots()[0][0])
        code, _ = promote_rule.rollback(name, approved_by='test-approver')
        self.assertEqual(code, 0, '应支持只传快照文件名')


class TestPromotionLedger(_Isolated):

    def test_promote_and_rollback_are_both_recorded(self):
        _write_rules(promote_rule.RADAR_RULES, {r'base\s*rule': ['d', 'high']})
        path = _candidate(self.tmp)
        promote_rule.promote(path, json.load(open(path, encoding='utf-8')),
                                approved_by='test-approver')
        promote_rule.rollback(approved_by='test-approver')

        entries = promote_rule.load_ledger()
        events = [e['event'] for e in entries]
        self.assertIn('promote', events)
        self.assertIn('rollback', events)
        self.assertLess(events.index('promote'), events.index('rollback'),
                        '事件顺序必须与实际操作一致')
        for e in entries:
            self.assertIn('ts', e)
        promoted = entries[events.index('promote')]
        self.assertEqual(promoted['patterns'], [GOOD['pattern']])
        self.assertTrue(promoted['snapshot'], '台账须记下对应的回滚点')

    def test_ledger_is_append_only_jsonl(self):
        """一行一条、追加写 —— 不得被后续事件覆盖。"""
        _write_rules(promote_rule.RADAR_RULES, {r'base\s*rule': ['d', 'high']})
        path = _candidate(self.tmp)
        promote_rule.promote(path, json.load(open(path, encoding='utf-8')),
                                approved_by='test-approver')
        with open(promote_rule.LEDGER, encoding='utf-8') as f:
            lines = [l for l in f.read().splitlines() if l.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIsInstance(json.loads(lines[0]), dict)

    def test_ledger_failure_does_not_block_promotion(self):
        """台账写不进（例如磁盘满）不得让晋升失败。"""
        promote_rule.LEDGER = os.path.join(self.tmp, 'no_such_dir',
                                            'ledger.jsonl')
        path = _candidate(self.tmp)
        n = promote_rule.promote(path, json.load(open(path, encoding='utf-8')),
                                approved_by='test-approver')
        self.assertEqual(n, 1, '台账故障不应阻断晋升')


class TestSnapshotPruning(_Isolated):

    def _make_snapshots(self, n):
        os.makedirs(promote_rule.SNAPSHOT_DIR, exist_ok=True)
        made = []
        for i in range(n):
            p = os.path.join(promote_rule.SNAPSHOT_DIR,
                             'radar_rules.20260916T%06d00Z.json' % i)
            with open(p, 'w', encoding='utf-8') as f:
                json.dump({'rules': {'r%d' % i: ['d', 'high']}}, f)
            os.utime(p, (time.time() - (n - i) * 60,
                         time.time() - (n - i) * 60))
            made.append(p)
        return made

    def test_keeps_only_the_newest_and_moves_the_rest(self):
        made = self._make_snapshots(promote_rule.KEEP_SNAPSHOTS + 5)
        moved = promote_rule.prune_snapshots()
        self.assertEqual(len(promote_rule.list_snapshots()),
                         promote_rule.KEEP_SNAPSHOTS)
        self.assertEqual(len(moved), 5, '超出保留份数的必须被处理掉')
        pruned_dir = os.path.join(promote_rule.SNAPSHOT_DIR, '.pruned')
        self.assertTrue(os.path.isdir(pruned_dir), '应移到 .pruned/ 而非删除')
        self.assertEqual(len(os.listdir(pruned_dir)), 5)
        # 内容仍在，可人工恢复
        for p in made:
            self.assertTrue(
                os.path.exists(p) or os.path.basename(p) in
                os.listdir(pruned_dir),
                '被裁掉的快照不得真的丢内容')

    def test_prune_is_a_noop_when_under_limit(self):
        self._make_snapshots(2)
        self.assertEqual(promote_rule.prune_snapshots(), [])
        self.assertEqual(len(promote_rule.list_snapshots()), 2)


class TestCorpusSingleSource(unittest.TestCase):
    """语料必须只有一个真源 —— 镜像常量一定会漂移。"""

    def test_benign_corpus_is_the_same_object_everywhere(self):
        self.assertIs(promote_rule.BENIGN_CORPUS, rule_corpus.BENIGN_CORPUS)
        self.assertIs(radar_effect.BENIGN_CORPUS, rule_corpus.BENIGN_CORPUS)

    def test_attack_samples_is_the_same_object(self):
        self.assertIs(radar_effect.ATTACK_SAMPLES, rule_corpus.ATTACK_SAMPLES)

    def test_no_duplicated_literal_list_in_consumers(self):
        """两个消费方不得再各自内联一份语料字面量。"""
        for rel in ('scripts/promote_rule.py', 'scripts/radar_effect.py'):
            src = open(os.path.join(ROOT, rel), encoding='utf-8').read()
            self.assertNotIn('BENIGN_CORPUS = [', src,
                             '%s 仍内联 BENIGN_CORPUS 字面量（会与真源漂移）' % rel)
        self.assertNotIn('ATTACK_SAMPLES = [',
                         open(os.path.join(ROOT, 'scripts/radar_effect.py'),
                              encoding='utf-8').read())


class TestCliWiring(unittest.TestCase):
    """新子命令必须真的接进 main()，否则只是死代码。"""

    def test_cli_exposes_rollback_and_snapshots(self):
        src = open(os.path.join(ROOT, 'scripts', 'promote_rule.py'),
                   encoding='utf-8').read()
        for token in ('--list-snapshots', '--rollback', '--ledger',
                      'def cmd_rollback', 'def cmd_list_snapshots',
                      'def cmd_ledger'):
            self.assertIn(token, src, 'main() 缺少 %s' % token)
        self.assertNotIn('os.remove', src,
                         '裁剪快照不应使用删除类 API（沙箱会被守卫吞掉）')

    def test_promote_takes_a_snapshot_before_writing(self):
        src = open(os.path.join(ROOT, 'scripts', 'promote_rule.py'),
                   encoding='utf-8').read()
        fn = src[src.index('def promote(path, data, approved_by=None):'):]
        fn = fn[:fn.index('\ndef ', 1)]
        approver_i = fn.index('if not approved_by')
        snap_i = fn.index('snapshot_current()')
        write_i = fn.index('open(RADAR_RULES')
        self.assertLess(approver_i, snap_i,
                        '批准人校验必须先于任何数据变动（无批准人 = 拒绝晋升）')
        self.assertLess(snap_i, write_i, '快照必须在覆盖写之前，否则回滚点已丢')


if __name__ == '__main__':
    unittest.main(verbosity=2)
