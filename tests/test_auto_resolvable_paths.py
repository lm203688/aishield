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

本文件锁死两件事
----------------
1. 派生器**按调用对象**解析写入者，而不是"文件里出现了该字面量且有写调用"。
   后者会把 scripts/rule_decay.py 误判成 data/generated_rules.json 的写入者
   （它确实读这个文件，但 json.dump 写的是 HITS_LOG / DECAY_STATE /
   RADAR_RULES）—— 一个爱误报的门禁很快会被整体无视。
2. 真正跑一次 git rebase 冲突（不是 mock）：快照类冲突必须自动解决并 push 成功，
   非快照类冲突必须 exit 3。
"""

import ast
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
