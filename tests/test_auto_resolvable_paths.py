# -*- coding: utf-8 -*-
"""并发 push 的「快照类」声明（.github/auto-resolvable-paths.txt）与 E13 门禁。

背景（2026-10-05 第三条同型事故）
--------------------------------
spine 端到端复验时，同一个生产者被并发实例化（手动 dispatch 与 spine 的
workflow_call 同时跑 —— 被调用 workflow 上写的 concurrency 实测不生效），
两个 run 各写一份快照 → push 时 rebase 撞 content 冲突 → git_push_safe.sh 按
「`data/state/` 之外一律是真实逻辑」判成需人工处理 → exit 3 → 当天闭环在
job 4 终止，其后 8 个 job 全部 skipped，并报一次假警。

根因不是那次重叠，而是**分类判据用了路径前缀这个代理**。因此本轮的修法是：
把判据从"路径长什么样"换成"写入者是否唯一"，并让声明受 E13 派生校验。

本文件锁死四件事
----------------
1. 派生器**按调用对象**解析写入者，而不是"文件里出现了该字面量且有写调用"。
   后者会把 scripts/rule_decay.py 误判成 data/generated_rules.json 的写入者
   （它确实读这个文件，但 json.dump 写的是 HITS_LOG / DECAY_STATE /
   RADAR_RULES）—— 一个爱误报的门禁很快会被整体无视。
2. 真正跑一次 git rebase 冲突（不是 mock）：快照类冲突必须自动解决并 push 成功，
   非快照类冲突必须 exit 3。
3. E10 必须守住**统一 push 入口**的退出码。原先 `if "git_push_safe" in s: continue`
   让入口整行免检，而门禁自己的报错信息又叫人改用这个入口 —— 「推荐了入口却不守
   入口」，与 E11/E12/E13 同型；刻意降级必须有 `allow-push-degrade: <理由>` 声明。
4. 带 `[skip ci]` 的自动提交若改写**对外声明面**，其推送必须经被验证的路径：
   `git_push_safe.sh` 在推送前跑声明面预检（`--declared-surface` 派生判据 +
   `rule_count_gate --check`），不一致即 **exit 4 拒绝推送**；E14 守住这条。
   实测事故：自动分发用写死的 133 覆盖了 feeds.xml 里刚修好的 264，全程零报警。
"""

import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import scripts.validate_workflows as V  # noqa: E402

DECL = ROOT / ".github" / "auto-resolvable-paths.txt"
PUSH_SH = ROOT / "scripts" / "git_push_safe.sh"


class TestWriterDerivation(unittest.TestCase):
    """写入者推导必须是"解析调用对象"，而不是"看见字面量"。"""

    @classmethod
    def setUpClass(cls):
        cls.generated = V._write_map(["generated_rules.json"])["generated_rules.json"]
        cls.intel = V._write_map(["threat_intel.json"])["threat_intel.json"]

    def test_generated_rules_has_exactly_one_writer(self):
        self.assertEqual(
            self.generated, ["scripts/intel_to_rules.py"],
            "data/generated_rules.json 的写入者必须唯一 —— "
            "「最后写入者胜」只在单一生产者下成立，多一个就要 E13")

    def test_threat_intel_has_exactly_one_writer(self):
        self.assertEqual(self.intel, ["scripts/fetch_vuln_feeds.py"])

    def test_read_only_mention_is_not_a_writer(self):
        """rule_decay.py 含该字面量、且文件里有 json.dump —— 但它不是写入者。

        若判据退化成 token 级「出现字面量 + 有写调用」，这条会立刻变红。
        这就是本轮把 object-resolution 写进推导器的原因。
        """
        self.assertNotIn("scripts/rule_decay.py", self.generated)
        self.assertIn("generated_rules.json",
                      (ROOT / "scripts" / "rule_decay.py").read_text(encoding="utf-8"))
        self.assertIn("json.dump",
                      (ROOT / "scripts" / "rule_decay.py").read_text(encoding="utf-8"))

    def test_two_producer_file_is_detected(self):
        """data/radar_rules.json 真有 2 个写入者 —— 它就该留在声明之外。"""
        writers = V._write_map(["radar_rules.json"])["radar_rules.json"]
        self.assertEqual(
            sorted(writers), ["scripts/promote_rule.py", "scripts/rule_decay.py"])
        self.assertNotIn(
            "data/radar_rules.json", V._declared_auto_paths(),
            "有 2 个生产者的文件被声明为快照类 = 并发时会静默丢掉一方的改动")

    def test_append_style_writer_is_detected(self):
        """open(path, 'w') 形式的写入点也要认（rule_decay 写 rule_hits.jsonl）。"""
        writers = V._write_map(["rule_hits.jsonl"])["rule_hits.jsonl"]
        self.assertEqual(writers, ["scripts/rule_decay.py"])

    def test_path_method_open_is_a_write_site(self):
        """`Path.open("a")` 这种方法形式也必须认。

        写第一版测试时发现的真实漏洞：只认内建 `open(path, mode)`，漏了
        `ALERT_LOG.open("a")`（scripts/notify.py:284）与 `open(LEDGER, "a")`。
        后者恰好是内建形式所以侥幸命中，前者则完全看不见。
        """
        writers = V._write_map(
            ["undelivered_alerts.jsonl", "promotion_ledger.jsonl"])
        self.assertEqual(writers["undelivered_alerts.jsonl"], ["scripts/notify.py"])
        self.assertEqual(writers["promotion_ledger.jsonl"],
                         ["scripts/promote_rule.py"])
        # 无参 / 只读的 Path.open 不得被当成写入点
        self.assertEqual(V._write_site_names(ast.parse("p.open()\n")), [])
        self.assertEqual(V._write_site_names(ast.parse("p.open('r')\n")), [])
        self.assertEqual(len(V._write_site_names(ast.parse("p.open('w')\n"))), 1)
        self.assertEqual(len(V._write_site_names(ast.parse("p.open(mode='a')\n"))), 1)

    def test_read_mode_open_is_not_a_writer(self):
        """只读打开不得算写入者（AST 层面：模式里必须含 w/a/x/+）。"""
        tree = ast.parse("open('x.json', encoding='utf-8')\n")
        self.assertEqual(V._write_site_names(tree), [])
        tree2 = ast.parse("open('x.json', 'w')\n")
        self.assertEqual(len(V._write_site_names(tree2)), 1)

    def _append_mode_writes(self, mod, basename):
        """该模块里有没有以**追加模式**写 basename 的写入点。"""
        tree = ast.parse((ROOT / mod).read_text(encoding="utf-8"))
        consts = {}
        for n in ast.walk(tree):
            if (isinstance(n, ast.Assign) and len(n.targets) == 1
                    and isinstance(n.targets[0], ast.Name)):
                consts.setdefault(n.targets[0].id, []).extend(
                    V._str_consts(n.value))
        hits = []
        for n in ast.walk(tree):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == "open" and len(n.args) >= 2):
                names = set(V._str_consts(n.args[0]))
                if isinstance(n.args[0], ast.Name):
                    names |= set(consts.get(n.args[0].id, []))
                if basename in names and any(
                        "a" in m for m in V._str_consts(n.args[1])):
                    hits.append(n.lineno)
        return hits

    def test_declared_writers_full_rewrite_each_run(self):
        """声明为快照类 ⇒ 写入者对它必须是整体重写，不能是追加。

        追加语义下"丢掉对方那一份"不再安全（会少一段数据），那时冲突就该
        按真冲突处理（exit 3）。这条把该前提钉在结构上。
        """
        for mod, base in (("scripts/intel_to_rules.py", "generated_rules.json"),
                          ("scripts/fetch_vuln_feeds.py", "threat_intel.json")):
            src = (ROOT / mod).read_text(encoding="utf-8")
            self.assertIn("write_text(", src, f"{mod} 应整体重写 {base}")
            self.assertEqual(self._append_mode_writes(mod, base), [],
                             f"{mod} 不得以追加模式写 {base}")
        # 反向确认这条检查真的能报：promote_rule.py 用追加模式写台账
        self.assertTrue(self._append_mode_writes("scripts/promote_rule.py",
                                                 "promotion_ledger.jsonl"))


class TestDeclarationAndGate(unittest.TestCase):
    """声明本身 + E13 的行为。"""

    def _gate(self, patterns, push_text=None):
        """用注入的声明条目前提跑 E13，返回其结果条目。"""
        real = V.AUTO_PATHS_FILE
        real_decl = V._declared_auto_paths
        real_push = V._push_script_text
        V.AUTO_PATHS_FILE = DECL           # 真实文件 → exists() 为真（早退分支不触发）
        V._declared_auto_paths = lambda: list(patterns)
        if push_text is not None:
            V._push_script_text = lambda: push_text
        try:
            res = []
            V._check_auto_resolvable_paths(res)
            self.assertEqual(len(res), 1)
            return res[0]
        finally:
            V.AUTO_PATHS_FILE = real
            V._declared_auto_paths = real_decl
            V._push_script_text = real_push

    def test_declaration_contains_snapshot_entries(self):
        pats = V._declared_auto_paths()
        self.assertIn("data/state/*", pats)
        self.assertIn("data/generated_rules.json", pats)
        self.assertIn("data/threat_intel.json", pats)

    def test_real_repo_gate_is_green(self):
        entry = self._gate(V._declared_auto_paths())
        self.assertEqual(entry["errors"], [])
        self.assertEqual(entry["warnings"], [])

    def test_gate_is_not_vacuous(self):
        """门禁必须有东西可查，否则"零告警"可能只是没跑。"""
        entry = self._gate(["data/generated_rules.json", "data/threat_intel.json"])
        self.assertEqual(entry["errors"], [])
        wmap = V._write_map(["generated_rules.json", "threat_intel.json"])
        self.assertTrue(all(wmap[k] for k in wmap),
                        "声明里的文件必须能推导出写入者 —— 否则本测试是空转")

    def test_second_writer_is_an_error(self):
        """把真实存在 2 个生产者的文件塞进声明 → 必须 E13 报错。"""
        entry = self._gate(["data/radar_rules.json"])
        self.assertTrue(entry["errors"], "2 个生产者必须报 E13")
        self.assertIn("radar_rules.json", entry["errors"][0])
        self.assertIn("E13", entry["errors"][0])
        self.assertIn("promote_rule.py", entry["errors"][0])

    def test_stale_literal_entry_warns(self):
        """字面量条目已无人写入 → W7（留着会让真冲突被当成快照覆盖）。"""
        entry = self._gate(["data/definitely_nobody_writes_this.json"])
        self.assertEqual(entry["errors"], [])
        self.assertTrue(any("W7" in w for w in entry["warnings"]))

    def test_dead_glob_warns(self):
        entry = self._gate(["data/state/*.no-such-ext"])
        self.assertEqual(entry["errors"], [])
        self.assertTrue(any("W7" in w for w in entry["warnings"]))

    def test_glob_members_without_static_writer_are_silent(self):
        """边界：通配符条目成员是动态命名的，静态推导看不见写入者 → 不该报 W7。

        data/state/* 的成员由 scripts/state_bus.py 用 f"{key}.json" 拼出来，
        基名不是字面量。对这种情况报"无人写入"是纯误报，而误报的门禁等于没有门禁。
        """
        entry = self._gate(["data/state/*"])
        self.assertEqual(entry["errors"], [])
        self.assertEqual([w for w in entry["warnings"] if "找不到任何" in w], [])

    def test_gate_detects_consumer_drift(self):
        """声明改了但消费方没读 → E13（"清单写了但不生效"是同型事故）。"""
        entry = self._gate(["data/generated_rules.json"], push_text="# 没有任何引用\n")
        self.assertTrue(any("git_push_safe.sh" in e for e in entry["errors"]))
        self.assertTrue(any("E13" in e for e in entry["errors"]))

    def test_push_script_reads_the_declaration(self):
        src = PUSH_SH.read_text(encoding="utf-8")
        self.assertIn(DECL.name, src,
                      "git_push_safe.sh 必须读这份声明，而不是硬编码前缀")
        # 旧判据（写死的 ^data/state/ grep 分区）必须已经不存在
        self.assertNotIn("grep -E '^data/state/'", src)


def _git_raw(cwd, *args, timeout=60):
    """执行 git；失败即抛（这些是夹具步骤，失败必须立刻可见）。"""
    p = subprocess.run(("git",) + args, cwd=str(cwd), check=False,
                       capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} 失败: {p.stderr}")
    return p


def _build_seed():
    """建一次"带种子提交的裸仓库"。

    每个用例只需 copytree 一份即可开跑 —— 本机实测 git 进程创建约 0.3s/次，
    "每个用例都从 init 开始"会白付 5 次调用；种子只为夹具服务，不该进被测语义。
    """
    seed = Path(tempfile.mkdtemp(prefix="aishield_gps_seed_"))
    bare = seed / "origin.git"
    _git_raw(seed, "init", "-q", "--bare", "--initial-branch=main", str(bare))
    work = seed / "work"
    _git_raw(seed, "clone", "-q", str(bare), str(work))
    _git_raw(work, "config", "user.email", "seed@t")
    _git_raw(work, "config", "user.name", "seed")
    (work / "data" / "state").mkdir(parents=True, exist_ok=True)
    for rel in ("data/state/intel.json", "data/state/ci.json"):
        (work / rel).write_text('{"v":0}\n', encoding="utf-8")
    (work / "scanner_rules.py").write_text("RULES=0\n", encoding="utf-8")
    _git_raw(work, "add", "-A")
    _git_raw(work, "commit", "-qm", "seed")
    _git_raw(work, "push", "-q", "origin", "main")
    return seed


@unittest.skipUnless(shutil.which("git") and shutil.which("bash"),
                     "需要 git 与 bash")
class TestSnapshotConflictResolution(unittest.TestCase):
    """真跑一次 rebase 冲突，验证脚本的实际分区行为（不做任何 mock）。"""

    # 测试仓库的配置：`gc --auto` 在 gc.autoDetach=true（默认）下会 detached 到
    # 后台并继承管道；autoCRLF 会让"内容冲突"变成换行符噪音。全部经 `git clone -c`
    # 一次写入（本机 git 进程创建约 0.3s/次，逐条 config 太贵）。
    _CLONE_CFG = ("-c", "gc.auto=0", "-c", "maintenance.auto=false",
                  "-c", "core.autocrlf=false", "-c", "advice.detachedHead=false",
                  "-c", "core.fsmonitor=false")

    @classmethod
    def setUpClass(cls):
        cls._seed = _build_seed()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._seed, ignore_errors=True)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aishield_gps_"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _git(self, cwd, *args, check=True):
        p = subprocess.run(("git",) + args, cwd=str(cwd), check=False,
                           capture_output=True, text=True, timeout=60)
        if check and p.returncode != 0:
            self.fail(f"git {' '.join(args)} 失败: {p.stderr}")
        return p

    def _setup(self):
        """裸 origin（种子副本）+ 两个 clone（A=远端那一方，B=要 push 的本 run）。"""
        origin = self.tmp / "origin.git"
        shutil.copytree(self._seed / "origin.git", origin)
        for name in ("A", "B"):
            self._git(self.tmp, "clone", "-q", *self._CLONE_CFG,
                      "-c", f"user.email={name.lower()}@t",
                      "-c", f"user.name={name.lower()}",
                      str(origin), str(self.tmp / name))
        a, b = self.tmp / "A", self.tmp / "B"
        (a / ".github").mkdir(parents=True, exist_ok=True)
        (b / ".github").mkdir(parents=True, exist_ok=True)
        # 用**真实的**声明内容，连带验证默认相对路径能读到这里
        shutil.copyfile(DECL, b / ".github" / DECL.name)
        return a, b

    def _push_from_a(self, a, rel, content, msg):
        (a / rel).write_text(content, encoding="utf-8")
        self._git(a, "add", "-A")
        self._git(a, "commit", "-qm", msg)
        self._git(a, "push", "-q", "origin", "main")

    def _run_script(self, b):
        p = subprocess.run(["bash", str(PUSH_SH), "2", "1", "main"],
                           cwd=str(b), check=False, capture_output=True,
                           text=True, timeout=300)
        return p.returncode, (p.stdout or "") + (p.stderr or "")

    def test_snapshot_conflict_is_auto_resolved(self):
        """只在声明为快照类的文件上冲突 → 自动解决并 push 成功。"""
        a, b = self._setup()
        (b / "data" / "generated_rules.json").write_text('{"v":1,"who":"B"}\n',
                                                         encoding="utf-8")
        (b / "data" / "state" / "intel.json").write_text('{"v":1,"who":"B"}\n',
                                                         encoding="utf-8")
        self._git(b, "add", "-A")
        self._git(b, "commit", "-qm", "B local")
        # A 先推，制造与 B 的真实 content 冲突
        self._push_from_a(a, "data/generated_rules.json", '{"v":2,"who":"A"}\n', "A")
        self._push_from_a(a, "data/state/intel.json", '{"v":2,"who":"A"}\n', "A2")

        rc, out = self._run_script(b)
        self.assertEqual(rc, 0, f"快照类冲突应自动解决，实际 rc={rc}\n{out}")
        self.assertIn("快照文件冲突已自动解决", out)
        # --theirs 语义：被重放的本地快照胜出
        self._git(a, "fetch", "-q", "origin", "main")
        got = self._git(a, "show", "origin/main:data/generated_rules.json").stdout
        self.assertIn('"who":"B"', got)

    def test_non_snapshot_conflict_exits_3(self):
        """对照：冲突落在未声明的源码文件 → 必须 exit 3 交人工。"""
        a, b = self._setup()
        (b / "scanner_rules.py").write_text("RULES=B\n", encoding="utf-8")
        self._git(b, "add", "-A")
        self._git(b, "commit", "-qm", "B local")
        self._push_from_a(a, "scanner_rules.py", "RULES=A\n", "A")

        rc, out = self._run_script(b)
        self.assertEqual(rc, 3, f"未声明文件冲突必须 exit 3，实际 rc={rc}\n{out}")
        self.assertIn("非快照文件冲突", out)
        self.assertIn("scanner_rules.py", out)

    def test_missing_declaration_falls_back_to_old_prefix(self):
        """声明文件缺失时必须退回**旧的**前缀判据，不得静默扩大自动解决范围。

        这条是向后兼容的护栏：老 checkout / 复用本脚本的其他仓库拿不到声明，
        此时 `data/generated_rules.json` 不在 `data/state/` 前缀内 → 走 exit 3。
        若哪天有人把兜底写成"没声明就都自动解决"，这条会立刻红。
        """
        a, b = self._setup()
        (b / ".github" / DECL.name).unlink()      # 拿不到声明
        (b / "data" / "generated_rules.json").write_text('{"v":1,"who":"B"}\n',
                                                         encoding="utf-8")
        self._git(b, "add", "-A")
        self._git(b, "commit", "-qm", "B local")
        self._push_from_a(a, "data/generated_rules.json", '{"v":2,"who":"A"}\n', "A")

        rc, out = self._run_script(b)
        self.assertEqual(rc, 3, f"无声明时不得自动解决，实际 rc={rc}\n{out}")
        self.assertIn("generated_rules.json", out)


_NODE_HEAD = "\n".join([
    "name: probe",
    "on:",
    "  workflow_dispatch:",
    "permissions:",
    "  contents: write",
    "jobs:",
    "  a:",
    "    runs-on: ubuntu-latest",
    "    steps:",
    "      - name: p",
    "        run: |",
    "",
])


def _check_probe(body: str):
    """把一段 run 块塞进最小 workflow，跑真正的 check_file，返回 errors。

    必须 newline='' 写：Windows 上 write_text 会把 \\n 译成 \\r\\n，直接触发 E9，
    那样测的就不是 E10 了。
    """
    tmp = Path(tempfile.mkdtemp(prefix="aishield_wfprobe_"))
    try:
        p = tmp / "probe.yml"
        lines = "".join("          " + ln + "\n" for ln in body.splitlines())
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(_NODE_HEAD + lines)
        return V.check_file(p)["errors"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class TestPushSwallowGate(unittest.TestCase):
    """E10 对「统一 push 入口的退出码」的守护。

    为什么专门测它：门禁原先有一句 `if "git_push_safe" in s: continue` —— 只要行里
    出现统一入口就整行免检，而门禁**自己的报错信息**恰恰叫人改用这个入口。
    「推荐了入口却对入口免检」与 E11/E12/E13 同型，是本项目最容易反复出现的一类缺陷。
    """

    def setUp(self):
        self.assertIsNotNone(V.yaml, "本套件运行前已由 run_all.py 预检 pyyaml")

    def test_entry_swallow_without_declaration_is_an_error(self):
        errs = _check_probe('bash scripts/git_push_safe.sh || echo "skipped"')
        self.assertTrue(errs and "E10" in errs[0], errs)
        self.assertIn("git_push_safe.sh", errs[0])

    def test_literal_git_push_swallow_is_still_an_error(self):
        """老行为不能因为扩正则而丢。"""
        errs = _check_probe("git push origin main || echo skipped")
        self.assertTrue(errs and "E10" in errs[0], errs)

    def test_bare_entry_call_passes(self):
        self.assertEqual(_check_probe("bash scripts/git_push_safe.sh"), [])

    def test_comment_mentioning_entry_passes(self):
        """注释里提到入口 ≠ 吞码（引用场景不能误报）。"""
        self.assertEqual(
            _check_probe("# 参考 bash scripts/git_push_safe.sh 的用法"), [])

    def test_declared_degrade_with_reason_passes(self):
        body = ("# allow-push-degrade: 只回写展示字段，下一轮重算覆盖\n"
                'bash scripts/git_push_safe.sh || echo "x"')
        self.assertEqual(_check_probe(body), [])

    def test_declared_degrade_without_reason_is_an_error(self):
        """有声明但没理由 = 把门禁关掉，必须报。

        这条踩过坑：第一版把"理由"算在「注释块 + 命令行」的拼接串上，
        冒号后为空时会把后面的命令行当成理由，于是静默放过。
        """
        body = ('# allow-push-degrade:\n'
                'bash scripts/git_push_safe.sh || echo "x"')
        errs = _check_probe(body)
        self.assertTrue(errs and "理由" in errs[0], errs)

    def test_inline_degrade_marker_passes(self):
        body = ('bash scripts/git_push_safe.sh || echo "x"'
                '  # allow-push-degrade: 装饰性心跳')
        self.assertEqual(_check_probe(body), [])

    def test_declaration_must_be_adjacent(self):
        """声明与降级必须紧邻 —— 否则"远处的声明"会漂移成万能豁免。"""
        body = ("# allow-push-degrade: 太远了\n# x\n# y\n# z\n# w\n"
                'bash scripts/git_push_safe.sh || echo "x"')
        self.assertTrue(_check_probe(body), "隔着 5 行的声明不该被吸附")

    def test_real_repo_has_no_undeclared_swallow(self):
        r = V.check_file(ROOT / ".github" / "workflows"
                         / "geo-indexnow-submit.yml")
        self.assertEqual([e for e in r["errors"] if "E10" in e], [],
                         "真仓里唯一那处刻意的 push 降级必须带声明")

    def test_real_geo_indexnow_degrade_is_declared(self):
        """把生产里那个**唯一**的例外钉住：声明一旦被删掉，这条会立刻红。"""
        src = (ROOT / ".github" / "workflows"
               / "geo-indexnow-submit.yml").read_text(encoding="utf-8")
        self.assertIn("git_push_safe.sh || echo", src,
                      "该 workflow 的心跳降级是本仓唯一的 push 吞码例外")
        marker = re.search(r"allow-push-degrade\s*:\s*(\S.*)", src)
        self.assertIsNotNone(marker, "该例外必须带 allow-push-degrade 声明")
        self.assertTrue(marker.group(1).strip(), "声明必须写理由")


class TestSkipCiDeclaredSurface(unittest.TestCase):
    """E14：带 CI-skip 的自动提交若改写对外声明面，其推送必须经**被验证的**路径。

    实测事故（2026-10-06）：channel-distribution 的 publish job 会重写
    `api/static/feeds.xml` 与 `README.md`，提交信息带 `[skip ci]`（ci.yml 完全不跑），
    于是它用生成脚本里写死的 133 覆盖了当天刚修好的 264，全程零报警。
    闭环的写入者恰是唯一能绕过全部门禁的人 —— 所以这条必须单独钉住。
    """

    def _jobs(self, script):
        return {"a": {"runs-on": "ubuntu-latest",
                      "steps": [{"run": script}]}}

    def _errors(self, script, entry_ok=True):
        return V.skip_ci_declared_surface_errors(self._jobs(script), entry_ok)

    # ── 反向用例：门禁不是空转 ──────────────────────────────────────
    def test_declared_write_behind_skip_ci_without_verification_is_caught(self):
        errs = self._errors(
            "git add README.md\n"
            'git commit -m "auto: x [skip ci]"\n'
            "git push origin main\n")
        self.assertEqual(len(errs), 1, f"应当报错，实际 {errs}")
        self.assertIn("没有任何验证", errs[0][1])
        self.assertIn("README.md", errs[0][1])

    def test_real_channel_distribution_shape_is_caught(self):
        """拿**真实**的 workflow 结构做验证：把入口换掉就必须报。

        这条是"把测试写在自己想象的结构上"的解药 —— 上面那些是合成样例，
        这条喂的是仓库里真跑的那份（`channel-distribution.yml` 的 publish job，
        它 staged 了 `api/static/feeds.xml` + `README.md`）。
        """
        data, err = V._load(ROOT / ".github" / "workflows" / "channel-distribution.yml")
        self.assertEqual(err, "", f"读取真实 workflow 失败: {err}")
        publish = data["jobs"]["publish"]
        staged = set()
        for b in V._run_texts(publish):
            for m in V._GIT_ADD_RE.finditer(b):
                staged.update(m.group(1).split())
        self.assertIn("api/static/feeds.xml", staged,
                      "前提失效：该 job 不再暂存声明面，本用例已不代表真实结构")
        self.assertEqual(
            V.skip_ci_declared_surface_errors({"publish": publish}, True), [],
            "真实 job 走了统一入口且入口有预检，不该报")

        import copy
        broken = copy.deepcopy(publish)
        for step in broken["steps"]:
            if isinstance(step, dict) and "run" in step:
                step["run"] = step["run"].replace(
                    "bash scripts/git_push_safe.sh", "git push origin main")
        errs = V.skip_ci_declared_surface_errors({"publish": broken}, True)
        self.assertEqual(len(errs), 1,
                         "把统一入口换成裸 git push 后必须报 E14（真实结构）")

    def test_entry_script_losing_its_precheck_is_caught(self):
        """入口在、但预检被摘掉 → 报"收敛到一处在这一处失守"。"""
        errs = self._errors(
            "git add README.md\n"
            'git commit -m "auto: x [skip ci]"\n'
            "bash scripts/git_push_safe.sh\n", entry_ok=False)
        self.assertEqual(len(errs), 1)
        self.assertIn("预检被摘掉", errs[0][1])

    # ── 正向用例：不该被误伤 ────────────────────────────────────────
    def test_push_via_entry_with_precheck_passes(self):
        self.assertEqual(self._errors(
            "git add README.md\n"
            'git commit -m "auto: x [skip ci]"\n'
            "bash scripts/git_push_safe.sh\n"), [])

    def test_in_job_self_check_passes(self):
        """没走入口但在本 job 内自检 —— 也算验证发生过。"""
        self.assertEqual(self._errors(
            "git add api/static/feeds.xml\n"
            "python scripts/rule_count_gate.py --check\n"
            'git commit -m "auto: x [skip ci]"\n'
            "git push origin main\n"), [])

    def test_non_declared_staged_paths_are_ignored(self):
        self.assertEqual(self._errors(
            "git add data/state/x.json docs/blog/y.md\n"
            'git commit -m "auto: x [skip ci]"\n'
            "git push origin main\n"), [])

    def test_commit_without_skip_marker_is_ignored(self):
        """不带 CI-skip → ci.yml 会跑，不需要额外要求。"""
        self.assertEqual(self._errors(
            "git add README.md\n"
            'git commit -m "chore: x"\n'
            "git push origin main\n"), [])

    def test_real_repo_entry_has_the_precheck(self):
        self.assertIn("rule_count_gate", V._push_script_text(),
                      "git_push_safe.sh 里的声明面预检不见了 —— E14 的前提失效")

    def test_real_repo_workflows_are_clean(self):
        files = sorted(list(V.WF_DIR.glob("*.yml")) + list(V.WF_DIR.glob("*.yaml")))
        bad = []
        for f in files:
            data, err = V._load(f)
            if err or not isinstance(data, dict):
                continue
            for jname, msg in V.skip_ci_declared_surface_errors(
                    data.get("jobs") or {}, True):
                bad.append(f"{f.name}:{jname} {msg}")
        self.assertEqual(bad, [],
                         "真实 workflow 有未验证的对外声明面写入: " + " | ".join(bad))


class TestDeclaredSurfaceChanged(unittest.TestCase):
    """`rule_count_gate.declared_surface_changed()` —— push 前预检用的窄出口。

    判据必须**派生**（复用 `_is_declared_surface` + `EXCLUDE_FILES`），
    不在这里手抄路径前缀；否则两处白名单一扩缩就又分叉。
    """

    def setUp(self):
        import importlib
        self.rcg = importlib.import_module("scripts.rule_count_gate")

    def test_real_surfaces_are_recognized(self):
        got = set(self.rcg.declared_surface_changed(
            ["README.md", "api/static/llms.txt", "mcp-server/README.md",
             "registry/x.json", "docs/benchmark/a.md"]))
        for rel in ("README.md", "api/static/llms.txt", "mcp-server/README.md"):
            self.assertIn(rel, got, f"{rel} 是对外声明面，却被判成非声明面")

    def test_non_surfaces_are_excluded(self):
        got = self.rcg.declared_surface_changed(
            ["scripts/foo.py", "data/state/ci.json", "docs/old-doc.md",
             "docs/blog/x.md", "scanner/rules.py", "tests/test_x.py"])
        self.assertEqual(got, [], f"非声明面被误判为声明面: {got}")

    def test_exempt_files_are_not_surfaces(self):
        """豁免文件本就是"数字不该被同步"的资产 —— 不该触发推送前预检。"""
        self.assertEqual(
            self.rcg.declared_surface_changed(["api/static/llms-full.txt"]), [])

    def test_leading_dot_slash_is_normalized(self):
        self.assertEqual(self.rcg.declared_surface_changed(["./README.md"]),
                         ["README.md"])

    def test_blank_lines_are_ignored(self):
        self.assertEqual(
            self.rcg.declared_surface_changed(["", "   ", "\t"]), [])

    def test_cli_export_is_usable(self):
        """shell 侧靠 `--declared-surface` 读 stdin —— 出口必须真能跑。"""
        p = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "rule_count_gate.py"),
             "--declared-surface"],
            cwd=str(ROOT), input="README.md\nscripts/x.py\napi/static/llms.txt\n",
            capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, f"出口失败: {p.stderr}")
        self.assertEqual(p.stdout.split(), ["README.md", "api/static/llms.txt"])


# ── 推送前声明面预检：真跑 git，验证脚本**真的会拒绝推送** ────────────────
# 夹具里的 scripts/rule_count_gate.py 是**替身**：它的 `--declared-surface`
# 委派给真模块（保证判据仍是派生的），`--check` 的退出码由 FAKE_GATE_RC 控制。
# 这样既能构造"声明不一致"，又不用把整个仓库搬进临时目录。
_FAKE_GATE = '''\
import importlib.util, os, sys
_spec = importlib.util.spec_from_file_location("rcg_real", os.environ["AISHIELD_REAL_GATE"])
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)
if "--declared-surface" in sys.argv:
    for p in _m.declared_surface_changed(sys.stdin.read().splitlines()):
        print(p)
    sys.exit(0)
sys.exit(int(os.environ.get("FAKE_GATE_RC", "0")))
'''


def _build_surface_seed():
    """裸 origin + 一份带 README/状态文件/替身门禁的种子提交。"""
    seed = Path(tempfile.mkdtemp(prefix="aishield_surface_seed_"))
    bare = seed / "origin.git"
    _git_raw(seed, "init", "-q", "--bare", "--initial-branch=main", str(bare))
    work = seed / "work"
    _git_raw(seed, "clone", "-q", str(bare), str(work))
    _git_raw(work, "config", "user.email", "seed@t")
    _git_raw(work, "config", "user.name", "seed")
    (work / "scripts").mkdir(parents=True, exist_ok=True)
    (work / "data" / "state").mkdir(parents=True, exist_ok=True)
    (work / "scripts" / "rule_count_gate.py").write_text(_FAKE_GATE, encoding="utf-8")
    (work / "README.md").write_text("# seed\n", encoding="utf-8")
    (work / "data" / "state" / "x.json").write_text('{"v":0}\n', encoding="utf-8")
    _git_raw(work, "add", "-A")
    _git_raw(work, "commit", "-qm", "seed")
    _git_raw(work, "push", "-q", "origin", "main")
    return seed


@unittest.skipUnless(shutil.which("git") and shutil.which("bash"),
                     "需要 git 与 bash")
class TestPushSurfacePrecheck(unittest.TestCase):
    """`git_push_safe.sh` 在推送前必须挡住"改写了对外声明面但数字不一致"的提交。

    实测事故：自动分发的 `[skip ci]` 提交把 feeds.xml 的 264 覆盖回 133。
    `[skip ci]` 让 ci.yml 完全不跑，所以唯一的补救时机就是**推送之前**。
    """

    _CLONE_CFG = ("-c", "gc.auto=0", "-c", "maintenance.auto=false",
                  "-c", "core.autocrlf=false", "-c", "advice.detachedHead=false",
                  "-c", "core.fsmonitor=false")

    @classmethod
    def setUpClass(cls):
        cls._seed = _build_surface_seed()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._seed, ignore_errors=True)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aishield_surface_"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _git(self, cwd, *args):
        p = subprocess.run(("git",) + args, cwd=str(cwd), check=False,
                           capture_output=True, text=True, timeout=60)
        return p

    def _clone_b(self):
        origin = self.tmp / "origin.git"
        shutil.copytree(self._seed / "origin.git", origin)
        b = self.tmp / "B"
        self._git(self.tmp, "clone", "-q", *self._CLONE_CFG,
                  "-c", "user.email=b@t", "-c", "user.name=b",
                  str(origin), str(b))
        return b

    def _commit(self, repo, rel, content, msg="local"):
        (repo / rel).write_text(content, encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", msg)

    def _remote_head(self, repo):
        p = self._git(repo, "ls-remote", "origin", "main")
        return p.stdout.split()[0] if p.stdout.strip() else ""

    def _run_script(self, repo, **env_extra):
        env = dict(os.environ)
        env["AISHIELD_REAL_GATE"] = str(ROOT / "scripts" / "rule_count_gate.py")
        env.update({k: str(v) for k, v in env_extra.items()})
        p = subprocess.run(["bash", str(PUSH_SH), "1", "1", "main"],
                           cwd=str(repo), check=False, capture_output=True,
                           text=True, timeout=300, env=env)
        return p.returncode, (p.stdout or "") + (p.stderr or "")

    # ── 核心反向用例 ─────────────────────────────────────────────────
    def test_declared_surface_with_inconsistent_rules_is_refused(self):
        b = self._clone_b()
        before = self._remote_head(b)
        self._commit(b, "README.md", "# changed\n")
        rc, out = self._run_script(b, FAKE_GATE_RC=1)
        self.assertEqual(rc, 4, f"必须拒绝推送（exit 4），实际 rc={rc}\n{out}")
        self.assertIn("拒绝推送", out)
        self.assertIn("README.md", out)
        self.assertEqual(self._remote_head(b), before,
                         "被拒绝的提交不得出现在远端")

    def test_declared_surface_with_consistent_rules_pushes(self):
        b = self._clone_b()
        before = self._remote_head(b)
        self._commit(b, "README.md", "# changed\n")
        rc, out = self._run_script(b, FAKE_GATE_RC=0)
        self.assertEqual(rc, 0, f"数字一致就该放行，实际 rc={rc}\n{out}")
        self.assertIn("声明面预检通过", out)
        self.assertNotEqual(self._remote_head(b), before, "远端应已前进")

    def test_non_surface_change_never_runs_the_gate(self):
        """没碰声明面就不该多跑一次门禁 —— 用 rc=99 证明它确实没被调用。"""
        b = self._clone_b()
        self._commit(b, "data/state/x.json", '{"v":1}\n')
        rc, out = self._run_script(b, FAKE_GATE_RC=99)
        self.assertEqual(rc, 0, f"非声明面改动不该被拦，实际 rc={rc}\n{out}")
        self.assertNotIn("声明面预检", out)

    def test_repo_without_the_gate_is_unaffected(self):
        """复用本脚本的其他仓库（没有 scripts/rule_count_gate.py）行为不变。"""
        b = self._clone_b()
        (b / "scripts" / "rule_count_gate.py").unlink()
        self._commit(b, "README.md", "# changed\n")
        rc, out = self._run_script(b)
        self.assertEqual(rc, 0, f"非本仓不该受影响，实际 rc={rc}\n{out}")

    def test_lookalike_paths_are_not_treated_as_surface(self):
        """路径判定不是"名字像不像" —— 故意起个 api_static_probe.txt 来钉住。"""
        b = self._clone_b()
        self._commit(b, "api_static_probe.txt", "x\n")
        rc, out = self._run_script(b, FAKE_GATE_RC=1)
        self.assertEqual(rc, 0,
                         f"api_static_probe.txt 不是声明面，不该被拦，实际 rc={rc}\n{out}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
