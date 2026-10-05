# -*- coding: utf-8 -*-
"""E11 / E12 测试前置门禁 —— 「同一件事多处各自实现」这一类的封堵验证。

背景（2026-10-05，**同日两次**同一类事故）
------------------------------------------
第一次：`python tests/run_all.py` 在 **6 个 workflow** 里各自实现，只有 ci.yml 装了
cryptography。另外 5 个在干净 runner 上跑 → `eco/crypto_sign.py` 静默降级
hmac-sha256 → L1 可移植身份 / L3 意图授权用例 fail-closed 成片报红 →
threat-intel-feed 的 verify job 失败 → spine 在 job 2 终止 → **后 8 个 job
全部 skipped**，整条闭环停摆。

修法不是「补那 5 处 pip install」：spine 是串行的，修好 job 2 之后 job 3
（rule-promoter，同样裸跑）当天就会以完全相同的方式失败。**逐个补 = 一天推进
一格**。所以真正要钉死的是「没有人可以绕过统一前置」—— E11。

第二次（E11 上线同一轮）：把前置收敛到 prepare-tests 之后，同一轮新增的 31 个
用例让测试套件多出一个第三方依赖 pyyaml，而前置只声明了 cryptography。干净
runner 上 Ran 1968 tests → failures=10 / errors=1 / skipped=29（本地 3 skip），
spine 再次停在 job 2。教训是**收敛到一处之后，那一处的内容必须是被派生出来的**：
于是有了 E12（从 import 图推导测试真实依赖，与 action 声明双向 diff）。

本组测试守四件事：
  1. 统一前置 action 本身存在、是 composite、且**真的断言** Ed25519 后端
     （只装包不断言，等于把「装上了」和「用上了」混为一谈）；
  2. 全仓每一个跑全量套件的 job 都引用了它（正向）；
  3. 门禁不是空转：漏引用必须报 E11，注释里提一句 run_all.py 不得误报（反向）；
  4. E12 的依赖推导必须**穿到本仓脚本里**（yaml 藏在 scripts/*.py），
     且用「回到事故当天只声明 cryptography」来验证它当时会响（反向）。
"""
from __future__ import annotations

import inspect
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import validate_workflows as V  # noqa: E402

WF_DIR = ROOT / ".github" / "workflows"
PREP_ACTION_PATH = ROOT / ".github" / "actions" / "prepare-tests" / "action.yml"

# 已知必须引用统一前置的 workflow（跑全量套件的全部入口）
SUITE_RUNNERS = (
    "ci.yml",
    "threat-intel-feed.yml",
    "rule-promoter.yml",
    "feature-closed-loop.yml",
    "publish-npm.yml",
    "self-heal-closed-loop.yml",
)

try:
    import yaml  # type: ignore
except ImportError:  # 见 _NeedsYaml：这里只记录缺失，不静默跳过
    yaml = None


class _NeedsYaml:
    """需要 PyYAML 才能做结构断言的测试基类。

    缺失时**失败**而不是跳过。跳过等于「这条门禁今天不存在」，而它恰恰是
    2026-10-05 一天内两次 CI 事故的同一形态：本地全绿、CI 红了一整天没人看见。
    环境不满足时要让信号响亮 —— 这正是 run_all.py 对 cryptography 采取 abort(2)
    的同一条理由，只是这里没有必要中止整套测试。
    """

    def setUp(self):
        super().setUp()
        if yaml is None:
            self.fail(
                "本测试需要 PyYAML；统一前置 .github/actions/prepare-tests 会安装它，"
                "本地请 `python -m pip install pyyaml`。**不做静默跳过** —— "
                "「测试是否运行取决于环境」正是 2026-10-05 两次事故的共同形态。"
            )



def _mk_probe(body: str) -> Path:
    """把一段 workflow 文本落到临时目录，返回路径。"""
    d = tempfile.mkdtemp(prefix="aishield_e11_")
    p = Path(d) / "probe.yml"
    p.write_text(body, encoding="utf-8")
    return p


_HEAD = "name: probe\non:\n  workflow_dispatch:\njobs:\n"
_CHECKOUT = "      - uses: actions/checkout@v4\n"


def _e11(errors):
    return [e for e in errors if e.startswith("E11")]


class TestPrepareTestsAction(_NeedsYaml, unittest.TestCase):
    """统一前置 action 自身的质量。"""

    def test_action_file_exists(self):
        self.assertTrue(
            PREP_ACTION_PATH.exists(),
            "统一测试前置 action 缺失 —— 6 个 workflow 的引用会全部失效",
        )

    def test_action_is_composite(self):
        text = PREP_ACTION_PATH.read_text(encoding="utf-8")
        self.assertIn("using: composite", text)

    def test_action_installs_cryptography(self):
        text = PREP_ACTION_PATH.read_text(encoding="utf-8")
        self.assertIn("cryptography", text)
        self.assertIn("pip install", text)

    def test_action_installs_pyyaml(self):
        """pyyaml 的位置与 cryptography 同等重要。

        2026-10-05 第二次事故就是漏了它：新用例解析 YAML，缺包时**静默跳过**
        （本地 3 skip / CI 29 skip），于是没人看见它其实没在跑。E12 现在会把
        「测试依赖但前置没装」变成硬错误，这里再加一道直接断言。
        """
        declared = V.declared_pip_deps(PREP_ACTION_PATH.read_text(encoding="utf-8"))
        self.assertIn("yaml", declared, f"前置未声明 pyyaml：{declared}")

    def test_action_asserts_backend_not_just_installs(self):
        """装上了 ≠ 用上了。

        `eco/crypto_sign.py` 在 **import 时**按 cryptography 是否可用来定后端。
        只装包不断言，就可能出现「装到了别的解释器 / 被 PYTHONPATH 遮蔽」——
        包在、后端没启用，测试仍然在错误前提下跑。
        """
        text = PREP_ACTION_PATH.read_text(encoding="utf-8")
        self.assertIn("backend()", text)
        self.assertIn("ALG_ED25519", text)
        self.assertIn("sys.exit(1)", text, "断言失败必须 fail-closed，不能只打印")

    def test_action_asserts_yaml_importable(self):
        """yaml 同样要断言：只写进 pip install 不等于当前进程真的能 import 到。"""
        text = PREP_ACTION_PATH.read_text(encoding="utf-8")
        self.assertIn("import yaml", text)

    def test_action_never_degrades_to_skip(self):
        """降级成 skip 就是假绿：L1/L3 是产品核心能力，不是可选增强。"""
        text = PREP_ACTION_PATH.read_text(encoding="utf-8")
        self.assertNotIn("continue-on-error: true", text)

    def test_node_deps_default_on(self):
        """node 依赖默认**开**。

        跑全量套件就包含 stdio 端到端测试；默认关会让它在每个引用方那里悄悄
        跳过 —— 「跳过」正是本 action 要消灭的假绿形态。默认值应当是最严格的那个，
        需要省时间的调用方自己显式关掉（如 publish-npm 已自行 npm ci）。
        """
        d = yaml.safe_load(PREP_ACTION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(str(d["inputs"]["install-node-deps"]["default"]), "true")


class TestEverySuiteRunnerHasPrereq(_NeedsYaml, unittest.TestCase):
    """正向：全仓每一个跑全量套件的 job 都必须引用统一前置。"""

    def test_all_workflows_pass_e11(self):
        offenders = []
        for p in sorted(WF_DIR.glob("*.yml")):
            for e in _e11(V.check_file(p).get("errors", [])):
                offenders.append(f"{p.name}: {e}")
        self.assertEqual(
            offenders, [],
            "存在跑全量测试却未引用统一前置的 job（缺前置会让签名后端降级，"
            "用例成片报假回归）：\n" + "\n".join(offenders),
        )

    def test_expected_runners_reference_the_action(self):
        for name in SUITE_RUNNERS:
            text = (WF_DIR / name).read_text(encoding="utf-8")
            self.assertIn(
                V.PREP_ACTION, text,
                f"{name} 未引用统一测试前置 {V.PREP_ACTION}",
            )

    def test_registry_matches_reality(self):
        """SUITE_RUNNERS 不能只是硬编码名单 —— 必须与仓库现状一致。

        否则新增一个跑套件的 workflow 后，上面的循环会「因为不在名单里」
        而静默放过，测试反倒成了盲区。
        """
        actual = set()
        for p in WF_DIR.glob("*.yml"):
            text = p.read_text(encoding="utf-8")
            if any(V.FULL_SUITE_RE.search(ln) for ln in V._command_lines(text)):
                actual.add(p.name)
        missing = actual - set(SUITE_RUNNERS)
        self.assertEqual(
            missing, set(),
            f"以下 workflow 跑全量套件但不在 SUITE_RUNNERS 名单里：{sorted(missing)}；"
            f"请补进名单，否则测试会漏掉它们",
        )


class TestGateCatchesMissingPrereq(_NeedsYaml, unittest.TestCase):
    """反向：一个永远不报错的门禁和没有门禁是一样的。"""

    def test_missing_prereq_is_flagged(self):
        body = (_HEAD + "  bad:\n    runs-on: ubuntu-latest\n    steps:\n"
                + _CHECKOUT
                + "      - name: Run tests\n        run: python tests/run_all.py\n")
        p = _mk_probe(body)
        self.addCleanup(shutil.rmtree, p.parent, ignore_errors=True)
        errs = _e11(V.check_file(p).get("errors", []))
        self.assertEqual(len(errs), 1, f"漏引用必须报 E11，实际 {errs}")
        self.assertIn("bad", errs[0])

    def test_prereq_present_is_clean(self):
        body = (_HEAD + "  good:\n    runs-on: ubuntu-latest\n    steps:\n"
                + _CHECKOUT
                + f"      - uses: {V.PREP_ACTION}\n"
                + "      - name: Run tests\n        run: python tests/run_all.py\n")
        p = _mk_probe(body)
        self.addCleanup(shutil.rmtree, p.parent, ignore_errors=True)
        self.assertEqual(_e11(V.check_file(p).get("errors", [])), [])

    def test_comment_mention_is_not_flagged(self):
        """注释里提一句 run_all.py 不算「这个 job 在跑测试」。

        本仓 workflow 里有大量解释性注释专门讨论测试（例如 ci.yml 里就写着
        "这一步原先只是裸 python tests/run_all.py"）。误报会让门禁迅速失去信誉，
        最后被人整体无视。
        """
        body = (_HEAD + "  doc:\n    runs-on: ubuntu-latest\n    steps:\n"
                + _CHECKOUT
                + "      - name: Just echo\n        run: |\n"
                + "          # 本 job 不跑 python tests/run_all.py，只是解释\n"
                + "          echo hello\n")
        p = _mk_probe(body)
        self.addCleanup(shutil.rmtree, p.parent, ignore_errors=True)
        self.assertEqual(
            _e11(V.check_file(p).get("errors", [])), [],
            "注释里提到 run_all.py 被误判成真的在跑测试",
        )

    def test_python3_and_flags_still_detected(self):
        """python3 / -u 之类的写法不能成为绕过门禁的后门。"""
        for cmd in ("python3 tests/run_all.py",
                    "python -u tests/run_all.py",
                    "python3.13 tests/run_all.py"):
            body = (_HEAD + "  bad:\n    runs-on: ubuntu-latest\n    steps:\n"
                    + _CHECKOUT
                    + f"      - name: Run tests\n        run: {cmd}\n")
            p = _mk_probe(body)
            self.addCleanup(shutil.rmtree, p.parent, ignore_errors=True)
            self.assertEqual(
                len(_e11(V.check_file(p).get("errors", []))), 1,
                f"命令写法 '{cmd}' 绕过了 E11 —— 门禁有后门",
            )

    def test_script_entry_with_deps_requires_prereq(self):
        """跑本仓**脚本**（其依赖闭包含第三方包）同样必须走统一前置。

        判据是派生的，不是「盯着 run_all.py」：本仓实测另有 3 个 job 属于同一类
        漏洞而全都不叫 run_all —— ci.yml 的 workflow-lint、meta-monitor 的
        inspect（各自 `pip install pyyaml`），以及 unified-security-scan 的
        self-scan（干脆什么都不装，YAML 策略与签名后端双双静默降级）。
        写死名单的检查永远追不上下一个入口。
        """
        body = (_HEAD + "  lint:\n    runs-on: ubuntu-latest\n    steps:\n"
                + _CHECKOUT
                + "      - name: Gate\n        run: python scripts/validate_workflows.py\n")
        p = _mk_probe(body)
        self.addCleanup(shutil.rmtree, p.parent, ignore_errors=True)
        errs = _e11(V.check_file(p).get("errors", []))
        self.assertEqual(len(errs), 1, f"跑有依赖的脚本却没前置，应报 E11：{errs}")
        self.assertIn("lint", errs[0])

    def test_script_entry_without_deps_is_not_flagged(self):
        """没有第三方依赖的脚本不该被要求装前置 —— 噪音会淹掉真信号。"""
        body = (_HEAD + "  ver:\n    runs-on: ubuntu-latest\n    steps:\n"
                + _CHECKOUT
                + "      - name: Sync\n        run: python scripts/sync_version.py --check\n")
        p = _mk_probe(body)
        self.addCleanup(shutil.rmtree, p.parent, ignore_errors=True)
        self.assertEqual(_e11(V.check_file(p).get("errors", [])), [])

    def test_py_compile_and_docker_are_not_host_entries(self):
        """py_compile 只编译不 import；docker 入口跑在容器里 —— 都不需要 host 装包。

        两条都是实测踩出来的误报：不排除的话 ci.yml 的 docker-test（`docker run
        --entrypoint python aishield:test /app/api/server.py`）与 self-heal 的
        repair（`python -m py_compile api/server.py`）都会被判缺前置。
        一个爱误报的门禁，很快会被整体无视。
        """
        for cmd in ("python -m py_compile api/server.py",
                    "docker run --entrypoint python aishield:test /app/api/server.py"):
            body = (_HEAD + "  j:\n    runs-on: ubuntu-latest\n    steps:\n"
                    + _CHECKOUT
                    + f"      - name: X\n        run: {cmd}\n")
            p = _mk_probe(body)
            self.addCleanup(shutil.rmtree, p.parent, ignore_errors=True)
            self.assertEqual(
                _e11(V.check_file(p).get("errors", [])), [],
                f"'{cmd}' 被误判为需要 host 侧依赖",
            )

    def test_nonexistent_local_action_is_flagged(self):
        body = (_HEAD + "  x:\n    runs-on: ubuntu-latest\n    steps:\n"
                + "      - uses: ./.github/actions/does-not-exist\n")
        p = _mk_probe(body)
        self.addCleanup(shutil.rmtree, p.parent, ignore_errors=True)
        errs = [e for e in V.check_file(p).get("errors", [])
                if e.startswith("E4") and "action" in e]
        self.assertEqual(len(errs), 1, f"本地 action 路径打错必须报 E4，实际 {errs}")


class TestCompositeActionIsValidated(_NeedsYaml, unittest.TestCase):
    """composite action 必须和 workflow 一样受检。

    把前置集中到一处之后，那一处就成了 **6 个 job 的单点依赖**：它本身若 CRLF
    污染 / heredoc 定界符损坏 / 表达式写错，6 个 job 会**一起**失败 —— 正是本轮
    要消灭的连锁停摆形态，只是换了个位置。所以校验器必须覆盖它，且不能因为
    action 没有 on/jobs 结构就产出成片误报（误报会淹掉真信号）。
    """

    _GOOD = (
        "name: Probe action\n"
        "description: probe\n"
        "inputs:\n"
        "  flag:\n"
        "    description: f\n"
        "    required: false\n"
        "    default: 'false'\n"
        "runs:\n"
        "  using: composite\n"
        "  steps:\n"
        "    - name: Say hi\n"
        "      shell: bash\n"
        "      run: |\n"
        "        echo hi\n"
    )

    def _write(self, body, newline=""):
        d = tempfile.mkdtemp(prefix="aishield_action_")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        p = Path(d) / "action.yml"
        with open(p, "w", encoding="utf-8", newline=newline) as fh:
            fh.write(body)
        return p

    def test_valid_action_has_no_workflow_specific_false_positives(self):
        """没有 on/jobs 不是错误 —— 不能因此报 E5（缺 dispatch）/W2/E1。"""
        r = V.check_file(self._write(self._GOOD))
        self.assertEqual(r.get("kind"), "action")
        noise = [e for e in r["errors"]
                 if e.startswith(("E5", "E6")) or "未定义任何 job" in e]
        self.assertEqual(noise, [], f"合法 composite action 被误报：{noise}")
        self.assertEqual(
            [w for w in r["warnings"] if w.startswith("W2")], [],
            "合法 composite action 被判为「无触发器」",
        )

    def test_crlf_in_action_is_caught(self):
        """CRLF 会破坏 heredoc 定界符 —— action 里的 heredoc 同样致命。"""
        r = V.check_file(self._write(self._GOOD, newline="\r\n"))
        self.assertEqual(len([e for e in r["errors"] if e.startswith("E9")]), 1)

    def test_missing_script_ref_in_action_is_caught(self):
        body = self._GOOD.replace("        echo hi\n",
                                  "        python scripts/nope_missing.py\n")
        r = V.check_file(self._write(body))
        self.assertEqual(len([e for e in r["errors"] if e.startswith("E4")]), 1)

    def test_bad_top_level_key_in_action_is_caught(self):
        """run 块续行落到第 0 列 → 命令被截断，对 action 同样是沉默杀手。"""
        r = V.check_file(self._write(self._GOOD + "stray_key: oops\n"))
        self.assertEqual(len([e for e in r["errors"] if e.startswith("E6")]), 1)

    def test_heredoc_inside_substitution_in_action_is_flagged(self):
        body = self._GOOD.replace(
            "        echo hi\n",
            "        V=$(python - <<'EOF'\n        print(1)\n        EOF\n        )\n",
        )
        r = V.check_file(self._write(body))
        self.assertEqual(len([w for w in r["warnings"] if w.startswith("E9")]), 1)

    def test_real_prepare_tests_action_is_clean(self):
        """本仓真实 action 文件必须零错误零警告。"""
        r = V.check_file(PREP_ACTION_PATH)
        self.assertEqual(r["errors"], [], f"prepare-tests action 有错误：{r['errors']}")
        self.assertEqual(r["warnings"], [], f"prepare-tests action 有警告：{r['warnings']}")

    def test_validator_cli_actually_scans_actions(self):
        """端到端：CLI 的 --json 输出里必须出现 action.yml。

        上面几条都在直接调 check_file —— 就算 main() 忘了把它加进扫描列表，
        它们也照样全绿。这条专门盯住「真的被扫到了」，否则整套检查是空转。
        """
        out = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_workflows.py"), "--json"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=180,
        )
        self.assertEqual(out.returncode, 0, f"校验器非零退出：{out.stdout[-400:]}")
        data = json.loads(out.stdout)
        names = [r["file"] for r in data["results"]]
        self.assertIn("action.yml", names, "CLI 没有扫描 .github/actions/ 下的 action.yml")


class TestPrereqCoversSuiteDeps(_NeedsYaml, unittest.TestCase):
    """E12：统一前置声明的依赖必须与测试套件**真实**依赖一致。

    E11 保证「所有入口都走同一个前置」，E12 保证「那个前置里装的东西是对的」——
    两者缺一不可。少了 E12，E11 只是把「N 个漏点」收敛成「1 个漏点」：
    2026-10-05 当天就是这么在收敛之后立刻又挂了一次（漏 pyyaml）。
    """

    def test_real_repo_is_consistent(self):
        """正向：本仓**从前置推导出的集合**与**从 action 读出的声明**必须完全相等。"""
        derived = set(V.third_party_imports(V._test_suite_entry_files()))
        declared = set(V.declared_pip_deps(
            PREP_ACTION_PATH.read_text(encoding="utf-8")))
        self.assertEqual(
            derived, declared,
            f"前置声明 {sorted(declared)} 与测试真实依赖 {sorted(derived)} 不一致 —— "
            f"漏装会让用例静默跳过（假绿），多装是死声明",
        )
        self.assertIn("cryptography", derived)
        self.assertIn("yaml", derived)

    def test_gate_reports_missing_dep(self):
        """反向：测试依赖里出现前置没装的包 → 必须报 E12。"""
        res = self._run_gate([self._entry("import totally_missing_pkg_xyz\n")])
        e12 = [e for e in res["errors"] if e.startswith("E12")]
        self.assertEqual(len(e12), 1, f"漏装必须报 E12，实际 {res['errors']}")
        self.assertIn("totally_missing_pkg_xyz", e12[0])

    def test_gate_reports_unused_declaration(self):
        """反向：前置装了但测试已不依赖 → W6（声明与依赖的反向漂移）。"""
        res = self._run_gate([self._entry("import json\nimport os\n")])
        self.assertEqual([e for e in res["errors"] if e.startswith("E12")], [])
        w6 = [w for w in res["warnings"] if w.startswith("W6")]
        self.assertEqual(len(w6), 2, f"两个声明都该被判为未使用，实际 {res['warnings']}")

    def test_would_have_caught_the_real_incident(self):
        """回到事故当天：前置只声明 cryptography → E12 必须当场报 yaml。

        这条防的是「门禁看起来在跑，但这个场景它不报」。
        """
        orig = V.declared_pip_deps
        V.declared_pip_deps = lambda text: ["cryptography"]  # type: ignore[assignment]
        try:
            res = V.check_file(PREP_ACTION_PATH)
            V._check_prereq_covers_suite_deps([res])
        finally:
            V.declared_pip_deps = orig
        e12 = [e for e in res["errors"] if e.startswith("E12")]
        self.assertEqual(len(e12), 1, f"事故当天该报 E12，实际 {res['errors']}")
        self.assertIn("'yaml'", e12[0])

    def test_derivation_follows_into_repo_scripts(self):
        """推导必须**穿到本仓脚本里** —— yaml 就藏在 scripts/*.py。

        只扫 tests/ 表层 import 的实现会漏掉它（本文件虽然自己 import yaml，
        但 meta_monitor / policy 不是），故用一个「自己不 import yaml」的入口
        来验证闭包真的跟进去了。
        """
        entry = ROOT / "tests" / "test_vuln_feed_health.py"
        self.assertNotIn("import yaml", entry.read_text(encoding="utf-8"),
                         "样本选错了：该入口自己就 import yaml，证明不了传递性")
        derived = V.third_party_imports([entry])
        self.assertIn("yaml", derived)
        self.assertTrue(
            any(p.startswith("scripts/") for p in derived["yaml"]),
            f"yaml 应当由 scripts/*.py 引入，实际来源 {derived['yaml']}",
        )

    def test_stdlib_only_entry_has_no_third_party(self):
        probe = self._entry("import json\nimport os\nimport sys\n"
                            "from pathlib import Path\n")
        self.assertEqual(V.third_party_imports([probe]), {})

    def test_namespace_packages_count_as_local(self):
        """api / scripts / distribution 都没有 __init__.py，但它们**是本仓模块**。

        漏判会把它们报成第三方包 → E12 一上线就满屏假红 → 门禁失去信誉被无视
        （这正是首版实现的真实缺陷，故立此回归）。
        """
        roots = V._module_roots()
        for name in ("api", "scripts", "distribution", "scanner", "eco", "tests"):
            self.assertIsNotNone(
                V._resolve_module(name, roots), f"{name} 未被识别为本仓模块")
        self.assertIsNone(V._resolve_module("totally_missing_pkg_xyz", roots))

    def test_pip_specs_are_normalised_to_import_names(self):
        """发行名 → 导入名的归一：PyYAML→yaml、带版本号/环境标记都要能解析。"""
        self.assertEqual(V.declared_pip_deps("run: pip install PyYAML==6.0"), ["yaml"])
        self.assertEqual(V.declared_pip_deps("run: pip install 'requests>=2.0'"),
                         ["requests"])
        self.assertEqual(
            V.declared_pip_deps("run: python -m pip install --quiet cryptography"),
            ["cryptography"])
        self.assertEqual(V.declared_pip_deps("# pip install nowhere"), [])

    # ── 辅助 ─────────────────────────────────────────────────────────
    def _entry(self, body: str) -> Path:
        d = tempfile.mkdtemp(prefix="aishield_e12_")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        p = Path(d) / "entry_probe.py"
        p.write_text(body, encoding="utf-8")
        return p

    def _run_gate(self, entries) -> dict:
        """用给定的入口集合跑一次 E12 比对（只替换入口，其余保持真实）。"""
        orig = V._test_suite_entry_files
        V._test_suite_entry_files = lambda: list(entries)  # type: ignore[assignment]
        try:
            res = V.check_file(PREP_ACTION_PATH)
            V._check_prereq_covers_suite_deps([res])
        finally:
            V._test_suite_entry_files = orig
        return res


class TestRunAllPrereqMessage(unittest.TestCase):
    """预检提示必须跨平台可用。

    初版提示写死了 ``C:\\Python314\\python.exe`` —— 在本机是对的，在 Linux runner
    上是一句**错指引**：照着做没有任何作用，还会让人以为要去装某个 Windows 解释器。
    这次事故恰恰发生在 CI 上，所以提示必须是通用可执行的。
    """

    @classmethod
    def setUpClass(cls):
        cls._src = ""
        cls._main_src = ""
        cls._RA = None
        try:
            from tests import run_all as RA  # noqa: WPS433
            cls._RA = RA
            cls._src = inspect.getsource(RA._crypto_backend_guard)
            cls._main_src = inspect.getsource(RA.main)
        except Exception:  # pragma: no cover - 仅在导入失败时走到
            pass

    def setUp(self):
        if not self._src:
            self.skipTest("无法导入 tests.run_all")

    def test_no_hardcoded_windows_interpreter(self):
        self.assertNotIn("Python314", self._src, "预检提示不应硬编码本机解释器路径")
        self.assertNotIn("C:\\", self._src, "预检提示不应出现 Windows 绝对路径")

    def test_gives_actionable_fix(self):
        self.assertIn("pip install cryptography", self._src)

    def test_points_at_ci_prereq(self):
        """提示里要指明 CI 侧由统一前置保证 —— 否则运维会去逐个改 workflow。"""
        self.assertIn("prepare-tests", self._src)

    def test_still_aborts_without_optin(self):
        """没有显式 AISHIELD_ALLOW_DEGRADED_CRYPTO=1 时必须 abort（而非静默降级）。"""
        self.assertIn("return 'abort'", self._src)
        self.assertIn("AISHIELD_ALLOW_DEGRADED_CRYPTO", self._src)

    def test_abort_exit_code_is_two(self):
        """abort 必须返回 2（门禁自身异常），与「测试失败 = 1」区分开。

        把「环境不满足」和「产品有缺陷」混成同一个退出码，是假绿的第一层：
        下游只看非零，于是无法区分**该改代码**还是**该装包**。
        run_all.py 末尾是 ``sys.exit(main())``，所以 return 2 → 进程退出码 2。
        """
        self.assertIn("crypto_state == 'abort'", self._main_src)
        self.assertIn("return 2", self._main_src)

    def test_preflight_reads_deps_from_the_single_declaration(self):
        """预检必须**按统一前置的声明**自查，而不是在 run_all 里再列一份清单。

        再列一份就是「同一件事的第二处实现」—— 本仓为此已出过两次事故。
        """
        src = inspect.getsource(self._RA._declared_missing_deps)
        self.assertIn("declared_pip_deps", src)
        self.assertIn("prepare-tests", src)
        # 当前解释器装了声明里的全部依赖 → 不该报缺失
        self.assertEqual(self._RA._declared_missing_deps(), [])

    def test_missing_non_crypto_dep_is_reported(self):
        """缺 pyyaml 这类依赖要被点名（cryptography 另走降级语义，不重复报）。"""
        orig = V.declared_pip_deps
        V.declared_pip_deps = lambda text: ["cryptography", "totally_missing_pkg_xyz"]
        try:
            missing = self._RA._declared_missing_deps()
        finally:
            V.declared_pip_deps = orig
        self.assertEqual(missing, ["totally_missing_pkg_xyz"])

    def test_missing_dep_hint_uses_distribution_name(self):
        """提示里的 `pip install X` 必须写**发行名**（= action 里声明的那串）。

        实测踩过：写导入名 yaml 会让人 `pip install yaml` —— PyPI 上那是另一个
        历史遗留包，照着做反而装错。发行名是 pyyaml（pip 对大小写不敏感）。
        """
        self.assertEqual(V.import_name_to_dist("yaml"), "pyyaml")
        self.assertEqual(V.import_name_to_dist("PIL"), "pillow")
        self.assertEqual(V.import_name_to_dist("requests"), "requests")
        # 报告路径必须真的走这层换算（只测映射函数会漏掉「没接上去」的情况）
        src = inspect.getsource(self._RA._declared_missing_deps)
        self.assertIn("import_name_to_dist", src)

    def test_main_aborts_on_missing_non_crypto_dep(self):
        """缺非加密依赖同样必须退 2（环境不满足），不能混成「测试失败 = 1」。"""
        self.assertIn("_declared_missing_deps()", self._main_src)
        self.assertIn("missing_deps", self._main_src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
