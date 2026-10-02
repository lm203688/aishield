"""
tests/test_hermetic_guard.py — 测试套件自身的「脏数据」守卫，以及它的正向对照

背景（2026-09-19 实测）
----------------------
跑一次 `python tests/run_all.py`，会把被跟踪的 `data/fleet.json` 改写掉。
根因是 `tests/test_commercialization.py` 里写的是 `FleetService()` —— 没传
`path`，于是落到默认的真实文件，setUp 里的 `reset()` 把生产数据清了。

危害不在这一份文件，而在这个**失败模式**：套件全绿、数据已脏，改动混进下一次
`git add -A` 当成人工变更提交上线。它不报错，所以没人会去查。

因此 run_all.py 里加了一道守卫（快照 → 运行 → 核对 → 还原 → 非 0 退出）。
但守卫本身也可能变成假绿：一个永远不报错的守卫和没有守卫是一样的。所以这个
文件的核心是 **test_guard_actually_detects_and_restores_a_write** —— 它故意
制造一次污染，断言守卫抓到了、并且还原了。
"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.run_all as run_all  # noqa: E402


class TestGuardIsWiredIn(unittest.TestCase):
    """守卫必须真的挂在套件主流程上，不能只是一段没人调用的代码。"""

    def setUp(self):
        self.src = open(os.path.join(os.path.dirname(__file__), 'run_all.py'),
                        encoding='utf-8').read()

    def test_guard_wraps_the_runner(self):
        self.assertIn('with _DataGuard() as guard:', self.src,
                      '守卫没有包住 runner.run(suite)，等于没接线')

    def test_guard_leak_forces_nonzero_exit(self):
        """污染必须让整次运行失败 —— 只打印警告的话，CI 仍然是绿的。"""
        self.assertIn('result.wasSuccessful() and not guard.leaked', self.src,
                      '退出码没有把 guard.leaked 计入')

    def test_protected_surface_covers_the_known_leak(self):
        """今天踩过的那个文件必须在受保护清单里，否则守卫抓不到同类问题。"""
        self.assertIn('data/fleet.json', self.src)


class TestGuardDetectsRealWrites(unittest.TestCase):
    """正向对照：故意写一次，断言守卫抓到并还原。"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='aishield_guard_test_')
        os.makedirs(os.path.join(self.root, 'data'), exist_ok=True)
        self.rel = os.path.join('data', 'fake_production.json')
        self.abs_p = os.path.join(self.root, self.rel)
        with open(self.abs_p, 'w', encoding='utf-8') as fh:
            fh.write('{"original": true}')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_clean_run_reports_no_leak(self):
        with run_all._DataGuard(root=self.root, paths=[self.rel]) as guard:
            pass  # 什么都不写
        self.assertEqual(guard.leaked, [])

    def test_guard_actually_detects_and_restores_a_write(self):
        """这条测试是守卫的守卫：它红了，说明守卫本身坏了。"""
        with run_all._DataGuard(root=self.root, paths=[self.rel]) as guard:
            with open(self.abs_p, 'w', encoding='utf-8') as fh:
                fh.write('{"corrupted": true}')

        self.assertEqual(len(guard.leaked), 1, '守卫没有抓到这次写入')
        self.assertEqual(guard.leaked[0], (self.rel, 'MODIFIED'))
        with open(self.abs_p, encoding='utf-8') as fh:
            self.assertEqual(fh.read(), '{"original": true}',
                             '守卫报出了污染却没有还原，等于放任数据留在脏状态')

    def test_guard_detects_deletion(self):
        with run_all._DataGuard(root=self.root, paths=[self.rel]) as guard:
            os.remove(self.abs_p)
        self.assertEqual(guard.leaked, [(self.rel, 'DELETED')])

    def test_guard_does_not_flag_untouched_siblings(self):
        other = os.path.join('data', 'other.json')
        with open(os.path.join(self.root, other), 'w', encoding='utf-8') as fh:
            fh.write('{"x": 1}')
        with run_all._DataGuard(root=self.root, paths=[self.rel, other]) as guard:
            with open(self.abs_p, 'w', encoding='utf-8') as fh:
                fh.write('{"corrupted": true}')
        self.assertEqual([k for k, _ in guard.leaked], [self.rel])


import re


def _strip_comments_and_strings(src):
    """剥掉注释与字符串字面量，只留可执行代码。

    不剥就会踩已知的坑：这个仓库里解释「为什么不要写 FleetService()」的注释和
    文档字符串本身就会被模式匹配到，于是守卫对着自己的说明文字报警 —— 一条
    永远在叫的测试等于没有测试。
    """
    src = re.sub(r'""".*?"""', ' ', src, flags=re.S)
    src = re.sub(r"'''.*?'''", ' ', src, flags=re.S)
    src = re.sub(r'"[^"\n]*"', ' ', src)
    src = re.sub(r"'[^'\n]*'", ' ', src)
    src = re.sub(r'#[^\n]*', ' ', src)
    return src


class TestNoTestWritesProductionData(unittest.TestCase):
    """静态契约：测试里不得构造「默认落到生产路径」的数据服务。

    这条是根因防线。守卫只能在事后兜住，这里尽量在事前拦住 —— 只要有人再写
    `FleetService()`（不传 path），这条测试就会红。
    """

    def test_fleet_service_is_always_given_an_explicit_path(self):
        tests_dir = os.path.dirname(__file__)
        offenders = []
        for name in sorted(os.listdir(tests_dir)):
            if not name.startswith('test_') or not name.endswith('.py'):
                continue
            raw = open(os.path.join(tests_dir, name), encoding='utf-8', errors='replace').read()
            code = _strip_comments_and_strings(raw)
            for m in re.finditer(r'FleetService\s*\(([^)]*)\)', code):
                if 'path' not in m.group(1):
                    line = code[:m.start()].count('\n') + 1
                    offenders.append('%s:~%d FleetService(%s)'
                                     % (name, line, m.group(1).strip()))

        self.assertEqual(
            offenders, [],
            '测试用 FleetService() 未指定 path，会写真实的 data/fleet.json：\n  '
            + '\n  '.join(offenders))

    def test_sync_readme_counts_is_never_called_on_the_real_readme(self):
        """静态契约：`promote_rule.sync_readme_counts()` 会改写 npm 页面 README。

        这条是 2026-10-02 实测出来的泄漏 —— 一个测试直接调它，跑一次套件就改一次
        `mcp-server/README.md`，被守卫在事后兜住（受保护清单里有这个文件）。
        事后兜住仍要修数据，这里改成事前拦住：只要有人再写无参调用就红。

        该函数的正确用法是**传副本路径**：`sync_readme_counts(tmp/README.md)`。
        """
        tests_dir = os.path.dirname(__file__)
        offenders = []
        for name in sorted(os.listdir(tests_dir)):
            if not name.startswith('test_') or not name.endswith('.py'):
                continue
            raw = open(os.path.join(tests_dir, name), encoding='utf-8',
                       errors='replace').read()
            code = _strip_comments_and_strings(raw)
            for m in re.finditer(r'sync_readme_counts\s*\(\s*\)', code):
                line = code[:m.start()].count('\n') + 1
                offenders.append('%s:~%d' % (name, line))

        self.assertEqual(
            offenders, [],
            '测试无参调用 sync_readme_counts()，会改写真实的 mcp-server/README.md：\n  '
            + '\n  '.join(offenders))

    def test_the_stripper_itself_does_not_swallow_real_code(self):
        """剥注释的辅助函数不能把真代码也剥掉，否则上面那条测试是空转。"""
        sample = (
            'x = 1  # FleetService()\n'
            'note = "FleetService()"\n'
            'svc = FleetService()\n'
        )
        stripped = _strip_comments_and_strings(sample)
        # 字符串内容与注释都被剥掉（引号本身也不该剩下）
        self.assertNotIn('"', stripped)
        self.assertNotIn('#', stripped)
        # 唯一幸存的那次 FleetService() 是真实调用，不是注释/字面量里的说明文字
        self.assertEqual(len(re.findall(r'FleetService\s*\(\)', stripped)), 1,
                         '剥注释剥过头了：真实调用被吞掉，契约测试会变成假绿')


if __name__ == '__main__':
    unittest.main(verbosity=2)
