#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield Workflow 静态校验器
============================
解决问题：self-heal-closed-loop.yml 中 `escalate.needs: verify` 指向的是
step id 而非 job id，GitHub Actions 解析期直接报错，整个 workflow 48 天
从未运行，而本地无任何机制能发现——因为没人校验过这 14 个 workflow。

本校验器在 CI 与本地都能跑，专抓以下"沉默杀手"：
  E1 YAML 语法错误
  E2 needs 指向不存在的 job（当初的致命伤）
  E3 job 依赖成环
  E4 引用了不存在的本地脚本文件
  E5 定时任务缺少 workflow_dispatch（无法手动补跑）
  E6 非法顶层键（run 块续行落到第 0 列，命令被静默截断）
  E8 表达式含 shell 变量插值 / 注释里写坏表达式（workflow 无法加载）
  E9 CRLF(\\r) 行尾（破坏 heredoc 定界符导致 bash 语法错）/ 命令替换内嵌 heredoc（脆弱写法）
  E10 并发 push 假绿吞错（`git push` **或统一入口 `git_push_safe.sh`** 的失败被
      `|| echo`/`|| true` 吞）/ `git add data/state/` 整目录提交；刻意降级须写
      `allow-push-degrade: <理由>`
  E11 有第三方依赖的本仓入口却没引用统一前置 prepare-tests（派生判据，不写死名单）
  E12 统一前置没装齐测试套件**真正**依赖的第三方包（从 import 图推导，不用人工清单）
  E13 声明为"并发冲突可自动解决"的数据文件不是单一生产者（快照语义前提不成立）
  W1 关键步骤使用 continue-on-error（测试形同虚设）
  W2 workflow 无任何触发器
  W3 cron 表达式字段数不合法
  W6 统一前置装了测试套件已不再依赖的包（声明与依赖反向漂移）
  W7 声明为"可自动解决冲突"的数据文件已无人写入 / glob 已失效

退出码：0=全部通过，1=存在错误(E)
用法：
    python scripts/validate_workflows.py
    python scripts/validate_workflows.py --json
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

REPO_ROOT = Path(__file__).resolve().parent.parent
WF_DIR = REPO_ROOT / ".github" / "workflows"
# 本地 composite action。它们与 workflow 同属 CI 代码，且常被多个 job 共用
# （本仓 prepare-tests 被 6 个 job 引用）—— 出错会连锁失败，必须同样受检。
ACTION_DIR = REPO_ROOT / ".github" / "actions"

# ${{ ... }} 表达式提取（非贪婪，一行内可命中多个）
EXPRESSION_RE = re.compile(r"\$\{\{(.*?)\}\}")
# 表达式里的 shell 变量插值：$ 紧跟标识符。Actions 表达式不支持这个。
SHELL_VAR_IN_EXPR = re.compile(r"\$[A-Za-z_][A-Za-z0-9_.]*")

# ── E11：有第三方依赖的入口必须走统一前置（派生，不维护名单）────────────
# 起因（2026-10-05 事故）：`python tests/run_all.py` 在 6 个 workflow 里各自
# 实现，只有 ci.yml 装了 cryptography。另外 5 个在干净 runner 上跑 → 签名后端
# 降级 hmac-sha256 → L1/L3 用例 fail-closed 成片报红（实测 18F/9E）→
# threat-intel-feed 的 verify job 失败 → spine 在 job 2 终止 → 后 8 个 job 全跳过。
#
# 关键在于这是**递进式**的：spine 串行，修好 job 2 后 job 3（rule-promoter）
# 当天就会以同样方式失败。逐个补 = 一天推进一格，永远追不上。
#
# 判据不写死名单：**凡是运行本仓入口（脚本 / 全量套件）且其依赖闭包含第三方包的
# job，就必须引用统一前置**。这样第 7、第 8 个入口出现时会自动被拦下 —— 而
# 「同一件事多处各自实现」正是本轮事故的根因形态。
PREP_ACTION = "./.github/actions/prepare-tests"
PREP_ACTION_FILE = PREP_ACTION.removeprefix("./") + "/action.yml"
# 真在跑全量套件的命令行（允许 python / python3 / 带 -u 等开关）。
FULL_SUITE_RE = re.compile(r"\bpython[0-9.]*\b[^\n|;&]*\btests/run_all\.py\b")
# 命令行里**真的执行**本仓入口脚本（python 后跟 scripts/…、tests/… 等路径）。
# 前置的 (?<![\w./-]) 很关键：`docker run --entrypoint python aishield:test
# /app/api/server.py` 里的 `api/server.py` 只是容器内路径的子串，不是 host 上的入口。
RUN_REPO_PY_RE = re.compile(
    r"\bpython[0-9.]*\b[^\n|;&]*?(?<![\w./-])"
    r"((?:scripts|tests|api|scanner|eco|connectors|collector)/[\w./-]+\.py)\b")
# 这些命令行**不产生 host 侧依赖**，必须排除，否则门禁会满屏假红：
#   · py_compile —— 只编译不 import，第三方依赖根本不会被加载；
#   · docker …   —— 入口跑在容器里，host 装不装包与它无关。
_NO_HOST_DEP_MARKERS = ("py_compile", "docker")


# ── E12：统一前置必须装齐测试套件**真正**依赖的第三方包 ──────────────────
# 起因（2026-10-05 同日，E11 的第二次复现）：刚把「跑测试要装什么」收敛到
# prepare-tests 之后，同一轮里测试新增了 31 个用例（解析 YAML 结构 / 断言 action
# 的键），测试套件因此多出一个第三方依赖 pyyaml —— 而前置里只声明了 cryptography。
# 后果与上次同型：threat-intel-feed 的 verify job 在干净 runner 上
# Ran 1968 tests → failures=10 / errors=1 / skipped=29（本地 3 skip），spine 再停 job 2。
#
# 教训：**收敛到一处之后，那一处的内容必须是派生出来的，而不是靠人记得同步。**
# 否则收敛只是把「N 个漏点」换成「1 个漏点」。
#
# 所以本检查不维护任何清单：
#   左手：从 tests/ 出发沿**本仓** import 图做闭包，收集非 stdlib / 非本仓的顶层名；
#   右手：解析 prepare-tests 里 `pip install` 的包名；
#   双向 diff —— 漏装=E12(错误)，多装=W6(警告)。
#
# 边界（已知且刻意）：闭包只覆盖「测试套件可达」的模块。workflow 直接调用、
# 而测试又不碰的脚本（若有）不在此列 —— 那属于另一类入口，需要时另开检查。
TEST_DIR = REPO_ROOT / "tests"
PIP_INSTALL_RE = re.compile(r"\bpip\s+install\b(.*)")
# 发行名 → 导入名。默认同名（cryptography / requests 之类都不需要映射），
# 只列真实不一致的；不在此表内的按 lower + '-'→'_' 归一。
DIST_TO_IMPORT: Dict[str, str] = {
    "pyyaml": "yaml",
    "pillow": "PIL",
    "beautifulsoup4": "bs4",
    "python-dateutil": "dateutil",
    "pycryptodome": "Crypto",
    "msgpack-python": "msgpack",
}
# 反向表：报错时给用户的应当是**发行名**（pip install PyYAML），
# 而不是导入名 —— 本仓 self-check 实测过：写 `pip install yaml` 会去装 PyPI 上
# 另一个同名的历史遗留包，照着提示做反而装错。所以两个方向都要有。
IMPORT_TO_DIST: Dict[str, str] = {v: k for k, v in DIST_TO_IMPORT.items()}
# import 图遍历时要跳过的目录（第三方包 / 本机沙箱 / 打包产物，都不算「本仓模块」）
_GRAPH_SKIP = {".git", ".workbuddy", "node_modules", "__pycache__", ".venv",
               "venv", "site-packages", "build", "dist", "outputs", ".mypy_cache"}


# ── E13 / W7：并发 push 的「快照类」声明必须被**派生实测** ────────────────
# 起因（2026-10-05，第三条同型事故）：spine 端到端复验时同一个生产者被并发实例化
# （手动 dispatch 与 spine 的 workflow_call 同时跑 —— 被调用 workflow 上写的
# concurrency 实测不生效），两 run 各写一份快照 → push 时 rebase 撞 content 冲突
# → git_push_safe.sh 按「`data/state/` 之外一律是真实逻辑」判成需人工处理
# → exit 3 → 当天闭环在 job 4 终止，其后 8 个 job 全部 skipped，并报一次假警。
#
# 根因不是那一次重叠，而是**分类判据用了一个路径前缀代理**：
#   data/generated_rules.json 的 out 完全由 data/threat_intel.json 重算
#     （intel_to_rules.py 读旧文件只为打印一个 Δ 数字，不参与决策）；
#   data/threat_intel.json 由 fetch_vuln_feeds.py 单点整体重写
#     （旧副本只用于「全源失败时不刷新 updated」，让停更在时间戳上可见）。
#   两者与 data/state/* 完全同类 —— 「快照、最后写入者胜」是安全的。
#
# 与 E11/E12 同型：**清单式代理必然漏**。所以 E13 不采信声明的内容，
# 而是为每条 glob 实测：写入者必须存在且**唯一**（唯一生产者是 last-writer-wins
# 成立的前提）。0 个 → W7 警告（声明已失效）；≥2 个 → E13 错误（必须移出）。
AUTO_PATHS_FILE = REPO_ROOT / ".github" / "auto-resolvable-paths.txt"
# 派生写入者时扫描的本仓源码目录（刻意不含 tests/ —— 那里只读数据文件）
_WRITE_SCAN_DIRS = ("scripts", "api", "scanner", "eco", "connectors",
                    "collector", "distribution")
# 写入点解析出来的路径常量里，哪一段算"被写的数据文件名"
_DATA_FILE_RE = re.compile(r"[\w.-]+\.(?:json|jsonl|txt|csv|ya?ml)$")


def _str_consts(node: ast.AST) -> List[str]:
    """收集节点子树里的所有字符串常量。"""
    return [n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _declared_auto_paths() -> List[str]:
    """读并发冲突可自动解决的 glob 声明（`#` 起注释，空行忽略）。"""
    if not AUTO_PATHS_FILE.exists():
        return []
    pats: List[str] = []
    for line in AUTO_PATHS_FILE.read_text(encoding="utf-8").splitlines():
        pat = line.split("#", 1)[0].strip()
        if pat:
            pats.append(pat)
    return pats


def _open_modes(node: ast.Call, pos: int) -> List[str]:
    """取出 open 调用的模式常量（第 pos 个位置参数优先，其次 `mode=` 关键字）。"""
    if len(node.args) > pos:
        return _str_consts(node.args[pos])
    for kw in node.keywords:
        if kw.arg == "mode":
            return _str_consts(kw.value)
    return []


def _is_write_mode(modes: List[str]) -> bool:
    return any(any(c in m for c in "wax+") for m in modes)


def _write_site_names(tree: ast.AST) -> List[set]:
    """取出每个写入点的**目标标识常量集合**（解析写入对象，不做 token 级判断）。

    覆盖三种真实写法：
      · `X.write_text(...)` / `X.write_bytes(...)`；
      · 内建 `open(path, "w"/"a"/"x"/"+")`  —— 模式在第 1 个位置参数；
      · `Path.open("w"/"a")`（方法形式）    —— 模式在第 0 个位置参数。
    只读打开一律不算 —— 这正是 scripts/rule_decay.py 不该被判成
    generated_rules.json 写入者的原因（它读该文件，但写的是 HITS_LOG 等）。
    """
    consts: Dict[str, set] = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            consts.setdefault(node.targets[0].id, set()).update(
                _str_consts(node.value))
    out: List[set] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        target: ast.AST | None = None
        if isinstance(fn, ast.Attribute) and fn.attr in ("write_text", "write_bytes"):
            target = fn.value
        elif isinstance(fn, ast.Attribute) and fn.attr == "open":
            if not _is_write_mode(_open_modes(node, 0)):   # Path.open(mode, ...)
                continue
            target = fn.value
        elif isinstance(fn, ast.Name) and fn.id == "open":
            if not _is_write_mode(_open_modes(node, 1)):   # open(path, mode, ...)
                continue
            target = node.args[0] if node.args else None
        if target is None:
            continue
        names = set(_str_consts(target))
        if isinstance(target, ast.Name):
            names |= consts.get(target.id, set())
        out.append(names)
    return out


def _repo_py_files() -> List[Path]:
    files: List[Path] = []
    for d in _WRITE_SCAN_DIRS:
        base = REPO_ROOT / d
        if base.is_dir():
            files.extend(p for p in sorted(base.rglob("*.py"))
                         if not any(part in _GRAPH_SKIP for part in p.parts))
    return files


def _write_map(basenames: Iterable[str]) -> Dict[str, List[str]]:
    """basename -> 写它的本仓 Python 模块（派生，不维护清单）。

    先用原文子串做**超集**预筛（写入者必然含该字面量），只对命中的文件做 AST
    解析 —— 门禁一慢就会被绕过，这一步把绝大多数文件挡在解析之外。
    """
    want = set(basenames)
    found: Dict[str, set] = {b: set() for b in want}
    for py in _repo_py_files():
        try:
            text = py.read_text(encoding="utf-8-sig")
        except OSError:
            continue
        if not any(b in text for b in want):
            continue
        try:
            tree = ast.parse(text)
        except (SyntaxError, ValueError):
            continue
        for names in _write_site_names(tree):
            for n in names:
                m = _DATA_FILE_RE.search(n)
                if m and Path(m.group(0)).name in want:
                    found[Path(m.group(0)).name].add(_rel(py))
    return {k: sorted(v) for k, v in found.items()}


def _has_glob(pat: str) -> bool:
    """条目是否含通配符（含通配符的条目成员是动态命名的，见 E13 边界说明）。"""
    return any(c in pat for c in "*?[")


def _push_script_text() -> str:
    """消费方脚本的原文（抽成函数是为了让测试能注入"分叉"的场景）。"""
    p = REPO_ROOT / "scripts" / "git_push_safe.sh"
    try:
        return p.read_text(encoding="utf-8") if p.exists() else ""
    except OSError:
        return ""


def _check_auto_resolvable_paths(results: List[Dict[str, Any]]) -> None:
    """E13 / W7：可自动解决冲突的声明，必须每条都实测出**唯一**生产者。

    声明本身（.github/auto-resolvable-paths.txt）是给人读的策略说明，不是判据；
    判据是下面这两条实测：
      · 写入者必须唯一  —— 否则 E13（两个生产者 = 两处在改真实内容，
        静默取一方会丢改动，「最后写入者胜」的前提不成立）；
      · 字面量条目的写入者必须存在 —— 否则 W7（声明已失效，删除它，
        留着会让真冲突被当成快照静默覆盖）。
    另加一条消费者一致性：脚本必须真的读这个声明，否则声明与判据分叉
    —— 「清单改了但不生效」正是本轮事故的同型形态。

    边界（已知且刻意，为了不制造永久误报）：含**通配符**的条目（如
    data/state/*）成员是运行期按 key 动态拼出来的（scripts/state_bus.py 的
    STATE_DIR / f"{domain}.json"），基名不以字面量出现，静态推导必然看不见写入者。
    对这类条目只检查「glob 还能匹配到文件」，其成员中**能被静态看到**的写入者
    仍照常做唯一性检查。误报会让门禁被整体无视，比漏报更糟，所以这里宁可留白。
    """
    if not AUTO_PATHS_FILE.exists():
        return  # 由测试兜底；不存在时 git_push_safe.sh 退回内置前缀，行为不变

    entry: Dict[str, Any] = {"file": AUTO_PATHS_FILE.name, "kind": "policy",
                             "errors": [], "warnings": [], "jobs": []}
    patterns = _declared_auto_paths()
    matched_all: List[Path] = []
    for pat in patterns:
        matched_all.extend(p for p in REPO_ROOT.glob(pat) if p.is_file())
    wmap = _write_map(p.name for p in matched_all)

    for pat in patterns:
        matched = [p for p in REPO_ROOT.glob(pat) if p.is_file()]
        if not matched:
            entry["warnings"].append(
                f"W7 声明 '{pat}' 匹配不到任何文件 —— 该条已失效，请从 "
                f"{_rel(AUTO_PATHS_FILE)} 删除（留着会让真冲突被当成快照覆盖）")
            continue
        for f in sorted(matched):
            writers = wmap.get(f.name, [])
            if len(writers) > 1:
                entry["errors"].append(
                    f"E13 '{_rel(f)}' 有 {len(writers)} 个写入者"
                    f"（{', '.join(writers)}）—— 「最后写入者胜」只在**单一生产者**"
                    f"下成立；两个生产者说明两处都在改真实内容，并发时静默取一方"
                    f"会丢改动。请把它从 {_rel(AUTO_PATHS_FILE)} 移出，"
                    f"让冲突按真冲突处理（exit 3 交人工）")
            elif not writers and not _has_glob(pat):
                entry["warnings"].append(
                    f"W7 '{_rel(f)}' 被声明为并发冲突可自动解决，但找不到任何"
                    f"本仓 Python 写入者 —— 声明已失效（写入者也可能不在 "
                    f"{'/'.join(_WRITE_SCAN_DIRS)} 内）")

    push_sh_text = _push_script_text()
    if push_sh_text and AUTO_PATHS_FILE.name not in push_sh_text:
        entry["errors"].append(
            f"E13 scripts/git_push_safe.sh 没有读取 {AUTO_PATHS_FILE.name} —— "
            f"声明与消费者已分叉：策略写在声明里，实际判据却仍在脚本里硬编码")
    results.append(entry)


def _command_lines(script: str):
    """只产出真正的命令行，跳过整行注释。

    注释里提一句 run_all.py 不该被当成"这个 job 在跑测试"：本仓库的 workflow
    里有大量解释性注释专门讨论测试，误报会让门禁很快失去信誉。
    """
    for line in (script or "").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        yield line

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


def _load(path: Path) -> tuple[Dict[str, Any] | None, str]:
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        return None, "PyYAML 未安装，跳过深度解析"
    try:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            return None, "顶层不是映射结构"
        return data, ""
    except Exception as e:
        return None, f"YAML 解析失败: {e}"


def _detect_cycle(deps: Dict[str, List[str]]) -> List[str]:
    """返回成环的 job 名列表（空表示无环）。"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in deps}
    cycle: List[str] = []

    def dfs(node: str, stack: List[str]) -> bool:
        color[node] = GRAY
        stack.append(node)
        for nxt in deps.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == GRAY:
                cycle.extend(stack[stack.index(nxt):] + [nxt])
                return True
            if color[nxt] == WHITE and dfs(nxt, stack):
                return True
        stack.pop()
        color[node] = BLACK
        return False

    for n in list(deps):
        if color[n] == WHITE and dfs(n, []):
            break
    return cycle


def _is_composite_action(data: Dict[str, Any]) -> bool:
    """是否是一个 composite action 定义（.github/actions/**/action.yml）。

    action.yml 与 workflow 同属「CI 代码」，但它没有 on / jobs 结构，适用的
    检查集不同（没有触发器、没有 job 依赖），故必须先区分再分流。

    为什么必须校验它：本仓的 .github/actions/prepare-tests 是 **6 个 job 的
    单点依赖** —— 它一旦 CRLF 污染 / heredoc 定界符损坏 / 表达式写错，那 6 个
    job 会**一起**失败。而这恰好就是本轮要消灭的「连锁停摆」形态：
    把命脉集中到一处之后，那一处必须被更严格地守住，否则等于把风险换了个位置。
    """
    runs = data.get("runs")
    return isinstance(runs, dict) and runs.get("using") == "composite"


def _check_local_refs(text: str, res: Dict[str, Any]) -> None:
    """E4：引用的本地脚本 / 本地 action 必须真实存在。

    workflow 与 action 共用本检查，所以抽成函数而不是复制两份 —— 复制出来的
    两份迟早会漂移，而「同一件事多处各自实现」正是本轮事故的根因形态。
    """
    for m in re.finditer(r"python\s+(scripts/[\w./-]+\.py|tests/[\w./-]+\.py)", text):
        rel = m.group(1)
        if not (REPO_ROOT / rel).exists():
            res["errors"].append(f"E4 引用了不存在的脚本: {rel}")
    for m in re.finditer(r"bash\s+(scripts/[\w./-]+\.sh)", text):
        rel = m.group(1)
        if not (REPO_ROOT / rel).exists():
            res["warnings"].append(f"W5 引用了本仓库不存在的 shell 脚本: {rel}（可能在服务器侧）")
    for m in re.finditer(r"uses:\s*\./?\.github/[\w./-]+", text):
        rel = m.group(0).split(":", 1)[1].strip()
        if rel.startswith("./"):
            rel = rel[2:]
        if not (REPO_ROOT / rel).exists():
            res["errors"].append(f"E4 引用了不存在的本地 action: {rel}")


def import_name_to_dist(name: str) -> str:
    """导入名 → pip 用的发行名（yaml→PyYAML、PIL→pillow…）。"""
    return IMPORT_TO_DIST.get(name, name)


def declared_pip_deps(text: str) -> List[str]:
    """从（action 的）原始文本里取出 `pip install` 声明的包，返回**导入名**列表。

    只在本仓 action 上调用，所以不需要处理 requirements 文件 / 约束文件：
    出现 `-r/-c` 这类参数说明有人把声明搬到了别处，那本身就该被 review 拦下。
    """
    deps: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = PIP_INSTALL_RE.search(s)
        if not m:
            continue
        try:
            tokens = shlex.split(m.group(1))
        except ValueError:
            tokens = m.group(1).split()
        for tok in tokens:
            if tok.startswith("-"):
                continue
            name = re.split(r"[<>=!~\[;@ ]", tok, maxsplit=1)[0].strip()
            if not name:
                continue
            low = name.lower()
            deps.add(DIST_TO_IMPORT.get(low, low.replace("-", "_")))
    return sorted(deps)


_ROOTS_CACHE: List[Path] | None = None


def _module_roots() -> List[Path]:
    """候选解析根：仓库根 + 仓库内所有目录（进程内缓存）。

    为什么要全给：本仓测试靠 `sys.path.insert` 直接引 scripts/api/scanner 等目录，
    甚至 scripts/arena 这种二级目录（`import jev_player`）。把根给全，解析就只需要
    看「这个 dotted 路径能不能落在某个根下」，无需复刻每个测试的 sys.path 拼装逻辑。
    """
    global _ROOTS_CACHE
    if _ROOTS_CACHE is None:
        roots = [REPO_ROOT]
        for d in REPO_ROOT.rglob("*"):
            if not d.is_dir():
                continue
            if set(d.relative_to(REPO_ROOT).parts) & _GRAPH_SKIP:
                continue
            roots.append(d)
        _ROOTS_CACHE = roots
    return _ROOTS_CACHE


def _rel(path: Path) -> str:
    """尽量给相对路径；探针文件可能在仓库外（单测会这么用）。"""
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_module(dotted: str, roots: List[Path]) -> Path | None:
    """dotted 模块路径 → 文件或目录（取最浅的一个）。解析不到 = 第三方包。"""
    rel = Path(*dotted.split("."))
    files: List[Path] = []
    dirs: List[Path] = []
    for r in roots:
        pkg = r / rel
        for cand in (r / (dotted.replace(".", "/") + ".py"), pkg / "__init__.py"):
            if cand.is_file():
                files.append(cand)
        if pkg.is_dir():
            dirs.append(pkg)
    pool = files or dirs          # 同名文件优先于同名目录
    return min(pool, key=lambda x: len(x.parts)) if pool else None


_RESOLVE_CACHE: Dict[str, Path | None] = {}


def third_party_imports(entry_files: Iterable[Path]) -> Dict[str, List[str]]:
    """从入口文件出发沿**本仓** import 图做闭包，返回 {第三方顶层名: [引用它的文件]}。

    为什么不能只扫 tests/ 表层 import：测试通过 `from scripts import meta_monitor`
    之类引用本仓脚本，而 yaml 这类依赖**藏在那些脚本里** —— 只扫表层就会漏掉真正的
    漏装（本次事故正是如此：yaml 在 scripts/validate_workflows.py 与
    scripts/meta_monitor.py 里）。

    为什么要按 dotted 路径**精确到文件**、而不是把命中的目录整体递归扫掉：
    scanner/integrations/、scripts/arena/ 里有大量**可选**集成依赖
    （neo4j / kafka / langchain / seccomp …），它们是 try/except 守卫的可选路径，
    一旦被当成"测试必需"就会逼着统一前置安装十几个包 —— 门禁会因此变成笑话。
    所以：包目录只走它的 __init__.py，其余按实际 import 到的子模块逐个跟进。
    """
    std = set(sys.stdlib_module_names)
    roots = _module_roots()
    seen: set[Path] = set()
    third: Dict[str, List[str]] = {}

    def _resolve_cached(dotted: str) -> Path | None:
        # 进程级缓存：一次校验里解析会被问上千次（每个 job 各跑一遍闭包），
        # 不缓存的话整个门禁要多花十秒以上 —— 门禁一慢就会被绕过。
        if dotted not in _RESOLVE_CACHE:
            _RESOLVE_CACHE[dotted] = _resolve_module(dotted, roots)
        return _RESOLVE_CACHE[dotted]

    def walk(path: Path, depth: int) -> None:
        if depth > 12 or path in seen:
            return
        seen.add(path)
        if path.is_dir():                       # 命名空间包：只跟进 __init__.py
            init = path / "__init__.py"
            if init.is_file():
                walk(init, depth + 1)
            return
        try:
            # utf-8-sig：本仓有文件带 BOM（tests/test_geo.py 实测），
            # 直接 utf-8 读进来 ast.parse 会报 non-printable character。
            text = path.read_text(encoding="utf-8-sig")
        except OSError:
            return
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return
        where = _rel(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                targets = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level or not node.module:
                    continue
                # `from m import a, b` 既可能依赖 m，也可能真的依赖 m.a / m.b
                targets = [node.module] + [f"{node.module}.{a.name}"
                                           for a in node.names if a.name != "*"]
            else:
                continue
            for t in targets:
                top = t.split(".")[0]
                if top in std:
                    continue
                hit = _resolve_cached(t)
                if hit is not None:
                    walk(hit, depth + 1)
                    continue
                # 子模块路径没解析出来，但顶层是本仓模块 → 不算第三方
                if _resolve_cached(top) is not None:
                    continue
                third.setdefault(top, []).append(where)

    for f in entry_files:
        walk(f, 0)
    return third


def _test_suite_entry_files() -> List[Path]:
    """全量套件的入口集合 = tests/*.py（run_all.py 就是逐个加载它们的）。"""
    return sorted(p for p in TEST_DIR.glob("*.py") if p.name != "__init__.py")


def _job_entry_files(job_body: Dict[str, Any]) -> List[Path]:
    """一个 job 实际运行的**本仓入口**文件（供 E11 派生依赖闭包）。

    跑全量套件展开成整套 tests/*.py —— 只看 run_all.py 自己的 import 会漏掉
    测试间接引入的依赖（yaml 就是这么漏掉的）。
    """
    files: List[Path] = []
    for st in (job_body.get("steps") or []):
        if not isinstance(st, dict):
            continue
        for line in _command_lines(st.get("run") or ""):
            if any(mk in line for mk in _NO_HOST_DEP_MARKERS):
                continue
            if FULL_SUITE_RE.search(line):
                files.extend(_test_suite_entry_files())
                continue
            for m in RUN_REPO_PY_RE.finditer(line):
                p = REPO_ROOT / m.group(1)
                if p.is_file():
                    files.append(p)
    return files


_DEP_CACHE: Dict[tuple, Dict[str, List[str]]] = {}


def _third_party_of(entries: Iterable[Path]) -> Dict[str, List[str]]:
    """带缓存的依赖闭包（同一份入口集合在一次运行里会被问多次）。"""
    key = tuple(sorted(str(p) for p in entries))
    if key not in _DEP_CACHE:
        _DEP_CACHE[key] = third_party_imports(entries)
    return _DEP_CACHE[key]


def check_file(path: Path) -> Dict[str, Any]:
    res: Dict[str, Any] = {"file": path.name, "errors": [], "warnings": [], "jobs": []}
    data, err = _load(path)
    if err and data is None:
        res["errors"].append(f"E1 {err}")
        return res
    if data is None:
        return res

    text = path.read_text(encoding="utf-8")

    # E9a CRLF 行尾检查（致命但本地极难发现）
    #
    # 背景：本仓库 workflow 多经 Windows 环境推送，历史上是 CRLF 行尾。CRLF 对 bash
    # 是隐形炸弹——heredoc 定界符行变成 'PYCI\r'，bash 比对永远不等，于是报
    # "unterminated here-document" 继而 "syntax error near ')'"，整个 workflow 静默失败。
    # threat-intel-feed 因此连续 3 次失败（2026-08-28~31）。读原始字节，含 \r 即报错，
    # 杜绝该类回归（涉及变量插值时 GitHub 不会在本地给出任何提示）。
    raw = path.read_bytes()
    if b"\r" in raw:
        res["errors"].append(
            "E9 文件含 CRLF(\\r) 行尾 —— 会破坏 heredoc 定界符导致 bash 语法错，须统一转为 LF"
        )

    # E9b 命令替换内嵌 heredoc（脆弱写法）：$( ... <<'EOF' ... )
    #   该写法在 CRLF / 定界符带尾随空白 / 结束符缩进时彻底崩，且极难调试。
    #   建议把脚本落盘成文件再调用，而非塞进 $( ) 里。warning 级别，不阻断推送。
    HEREDOC_IN_SUBST = re.compile(r"\$\(\s*[^)]*<<")

    def _walk_runs(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "run" and isinstance(v, str):
                    # 逐行跳过注释，避免说明性注释里的字面量（如解释某 bug 时的示例代码）误报
                    for line in v.splitlines():
                        if line.strip().startswith("#"):
                            continue
                        if HEREDOC_IN_SUBST.search(line):
                            yield v
                            break
                else:
                    yield from _walk_runs(v)
        elif isinstance(node, list):
            for i in node:
                yield from _walk_runs(i)

    # 遍历整份 data（而非 data["jobs"]）：composite action 的 run 位于
    # runs.steps[].run，不在 jobs 下 —— 只传 jobs 会让 action 完全逃过检查。
    for _ in _walk_runs(data):
        res["warnings"].append(
            "E9 检测到命令替换内嵌 heredoc ($( ... <<'EOF' ...))，"
            "该写法在 CRLF/定界符带尾随空白时会致 bash 语法错，建议改为调用落盘脚本"
        )
        break

    # E10 并发 push 假绿吞错 / 整目录状态提交（2026-09-05 审计 spine 三次失败）
    #
    # 背景：closed-loop-spine 每日主干里多个 workflow 先后 push 同一个 main。
    #   (a) `git push ... || echo "push skipped"` —— job 永远绿灯，但产物永久丢失。
    #       feature-closed-loop 因此连挂 09-01 / 09-02 两天，迭代汇报被 skip；
    #       规则晋升产物靠人工补 13 条才入库（数据飞轮"只进不出"同型根因）。
    #   (b) `git add data/state/` —— 把别的 workflow 刚 push 的状态文件一并提交，
    #       rebase 时产生内容冲突（重试无法解决），必须精确到本 workflow 自己的域文件。
    # 统一要求走 scripts/git_push_safe.sh（带重试，耗尽才真 exit 1 触发 alert job）。
    #
    # 【2026-10-05 补】原先这里有一句 `if "git_push_safe" in s: continue` —— 只要行里
    # 出现统一入口就整行免检。于是 `bash scripts/git_push_safe.sh || echo "..."` 优雅地
    # 绕过门禁：**门禁的报错信息叫人改用这个入口，却对入口的退出码免检**。
    # 这与 E11/E12/E13 同型（收敛到一处却没守住那一处），所以现在入口一并受检，
    # 同时给"确实是装饰性回写、失败也不该红"的场景一个**声明式**出口：
    # 同一行或上一行写 `allow-push-degrade: <理由>`（理由必须非空，否则报错）。
    PUSHSWALLOW = re.compile(
        r"(?:git\s+push|git_push_safe\.sh)\b[^\n|;&]*\|\|\s*(?:echo\b|true\b|\d\s*$|\{)"
    )
    DEGRADE_MARKER = re.compile(r"allow-push-degrade\s*:")
    PULL_NO_RETRY = re.compile(r"git\s+pull\s+--rebase\b[^\n]*\|\|\s*true")
    # 目录引用 = 同一行存在 `git add`，且 `data/state/` 之后紧跟空白或行尾。
    # 反例（不报）：`git add ROADMAP.md data/state/feature.json` —— 精确文件，合法。
    # 反例（不报）：`python -c "...p='data/state/published.json'..."` —— 行内无 git add，
    #              纯字符串引用。上一版正则漏了 `git add` 前缀，导致这类行被误报。
    ADD_STATE_DIR = re.compile(r"git\s+add\b[^\n]*\bdata/state/(?=\s|$)")

    def _run_lines(node):
        """产出 (紧邻上方的注释块, 当前行)。

        当前行跳过整行注释，但**把紧邻的注释块一起带出来** —— 降级声明
        `allow-push-degrade:` 是写在注释里的，丢掉它就没法区分"刻意降级"与
        "顺手吞掉"。只取紧邻的 4 行，避免把远处的声明误吸附过来。
        """
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "run" and isinstance(v, str):
                    comments: List[str] = []
                    for line in v.splitlines():
                        if line.strip().startswith("#"):
                            comments.append(line)
                            continue
                        yield "\n".join(comments[-4:]), line
                        comments = []
                else:
                    yield from _run_lines(v)
        elif isinstance(node, list):
            for i in node:
                yield from _run_lines(i)

    def _degrade_marker(above: str, line: str):
        """(是否声明降级, 理由)。

        理由**只能取自注释**：上一版把理由算在"注释块 + 命令行"的拼接串上，
        `# allow-push-degrade:`（冒号后为空）会把后面的命令行当成理由，
        于是"声明了但没写理由"被静默放过 —— 探针实测抓到，已修。
        """
        m = DEGRADE_MARKER.search(above or "")
        if m:
            return True, above[m.end():].replace("\n", " ").strip()
        inline = line.split("#", 1)[1] if "#" in line else ""
        m = DEGRADE_MARKER.search(inline)
        if m:
            return True, inline[m.end():].strip()
        return False, ""

    for above, line in _run_lines(data):
        s = line.strip()
        if PUSHSWALLOW.search(s):
            declared, reason = _degrade_marker(above, line)
            if declared and reason:
                continue  # 显式声明且写了理由：接受（例如装饰性心跳回写）
            if declared:
                res["errors"].append(
                    f"E10 `allow-push-degrade:` 必须写明理由（{s[:60]}）—— "
                    "没有理由的例外等于把门禁关掉"
                )
            else:
                res["errors"].append(
                    f"E10 统一 push 入口 `git_push_safe.sh` 的失败被 `|| echo`/`|| true` "
                    f"吞成假绿（{s[:70]}）—— 脚本报错信息让调用方改用这个入口，"
                    "入口的退出码就必须被尊重：吞掉后并发冲突 / 重试耗尽都不会被发现，"
                    "产物永久丢失。确属装饰性回写（失败也确实安全）请在紧邻上方注释里写 "
                    "`allow-push-degrade: <理由>`"
                )
        elif PULL_NO_RETRY.search(s):
            res["errors"].append(
                f"E10 `git pull --rebase ... || true` 吞掉 rebase 失败且无重试（{s[:70]}）；"
                "改用 `bash scripts/git_push_safe.sh`"
            )
        if ADD_STATE_DIR.search(s):
            res["errors"].append(
                f"E10 `git add data/state/` 提交整个状态目录（{s[:70]}）"
                "—— 会把其他 workflow 刚 push 的文件一并提交并引发 rebase 内容冲突；"
                "请只 add 本 workflow 自己拥有的 data/state/<domain>.json"
            )

    # E6 顶层键污染检查

    # 场景：run 块里的多行字符串未缩进，续行落到第 0 列后被 YAML 当成新的顶层键。
    # 这类错误语法上合法、GitHub 不报错，但 run 命令已被截断 —— 比语法错更隐蔽。
    if _is_composite_action(data):
        # composite action 的合法顶层键是另一套；沿用 workflow 的白名单会全量误报
        ALLOWED_TOP = {"name", "description", "author", "inputs", "outputs",
                       "runs", "branding"}
    else:
        ALLOWED_TOP = {
            "name", "on", "jobs", "permissions", "env", "defaults",
            "concurrency", "run-name", True,  # PyYAML 把 on: 解析成布尔 True
        }
    for key in data.keys():
        if key not in ALLOWED_TOP:
            res["errors"].append(
                f"E6 非法顶层键 '{key}' —— 多半是 run 块内多行字符串未缩进导致命令被截断"
            )

    # E8 表达式合法性检查（抓「workflow 无法加载」这类沉默杀手）
    #
    # 背景：GitHub Actions 的表达式在 workflow 加载时就静态求值，而且
    # **连 YAML 注释里的 ${{ }} 也照样求值**。所以任何写在注释里的坏表达式，
    # 都会让整个 workflow 无法加载——而 PyYAML 与 E1 的语法检查都完全正常，
    # 这个错只在 GitHub 侧出现，本地门禁永远发现不了。
    #
    # 三种已实测的致命写法：
    #   1) 表达式里嵌 shell 变量：needs.$job.result
    #      -> (Line 247, Col 14) Unexpected symbol: '$job'
    #   2) 注释里写下坏表达式的字面量当作文档说明
    #      -> 同一个解析错误被「注释」重新引入（已实测复现）
    #   3) 注释里打一个空的表达式标记占位（本来说明「注释也会被求值」时
    #      顺手打的例子）-> An expression was expected（已实测复现）
    #
    # 命中后的表现极具误导：run 名退化为 .github/workflows/ci.yml、
    # 零 job、秒红，看起来像「CI 全红」，实际是「CI 从来没跑过」。
    # 曾连续 17 次全因此失败，而门禁脚本本地全绿，极难发现。
    #
    # 这里只做可疑模式的静态拦截，不是完整表达式解析器——
    # 宁可多报也不放过，人工 5 秒即可确认。
    for lineno, line in enumerate(text.splitlines(), start=1):
        for expr in EXPRESSION_RE.findall(line):
            body = expr.strip()
            if not body:
                # 空表达式标记：GitHub 报 "An expression was expected"。
                # 极易在注释里踩到——写「表达式标记」来解释这个规则时，
                # 顺手打个占位空标记，就会让整个 workflow 无法加载。
                res["errors"].append(
                    f"E8 第 {lineno} 行存在空表达式标记 —— GitHub 报 "
                    f"'An expression was expected'，整个 workflow 无法加载。"
                    f"注释里要举例就用文字描述，不要打标记的字面量。"
                )
                continue
            if SHELL_VAR_IN_EXPR.search(body):
                res["errors"].append(
                    f"E8 第 {lineno} 行表达式含 shell 变量插值: ${{{{ {body} }}}}"
                    f" —— Actions 表达式不支持，整个 workflow 将无法加载"
                )

    # ── composite action：通用检查已跑完，在此分流 ───────────────────────
    # 下面的触发器 / job / needs 检查都建立在 workflow 结构上（on / jobs）。
    # action.yml 没有这些结构，继续往下走只会产出成片误报（E5 无 dispatch、
    # W2 无触发器、E1 未定义 job），把真信号淹掉。
    if _is_composite_action(data):
        res["kind"] = "action"
        res["crons"] = []
        res["workflow_run_refs"] = []
        # 记录相对路径（同名 action.yml 会有多个）与**声明的 pip 依赖**，
        # 供 cross_check 的 E12 做双向 diff —— 声明处只有这一处，所以这里读到的
        # 就是「本仓声称跑测试要装什么」的唯一事实源。
        res["path"] = _rel(path)
        res["pip_deps"] = declared_pip_deps(text)
        _check_local_refs(text, res)
        return res

    # 触发器检查（PyYAML 会把 on: 解析成 True 键，需两边都看）
    on = data.get("on", data.get(True))
    if not on:
        res["warnings"].append("W2 未定义任何触发器，此 workflow 永不执行")

    # 记录本文件的 workflow 名与 workflow_run 引用，供跨文件检查（E7）使用
    res["name"] = data.get("name")
    res["workflow_run_refs"] = []
    if isinstance(on, dict):
        wr = on.get("workflow_run") or {}
        refs = wr.get("workflows") if isinstance(wr, dict) else None
        if isinstance(refs, str):
            refs = [refs]
        res["workflow_run_refs"] = [str(x) for x in (refs or [])]

    has_dispatch = False
    res["crons"] = []
    if isinstance(on, dict):
        has_dispatch = "workflow_dispatch" in on
        sched = on.get("schedule")
        if sched:
            if not has_dispatch:
                res["errors"].append("E5 存在 schedule 但缺少 workflow_dispatch，故障时无法手动补跑")
            if isinstance(sched, list):
                for s in sched:
                    cron = (s or {}).get("cron", "")
                    if cron:
                        res["crons"].append(str(cron))
                    if cron and len(str(cron).split()) != 5:
                        res["errors"].append(f"W3 cron 表达式字段数非 5: '{cron}'")
    elif isinstance(on, list):
        has_dispatch = "workflow_dispatch" in on

    # Job 依赖检查 —— 当初的致命伤就在这里
    jobs = data.get("jobs") or {}
    if not isinstance(jobs, dict) or not jobs:
        res["errors"].append("E1 未定义任何 job")
        return res

    job_names = set(jobs.keys())
    res["jobs"] = sorted(job_names)
    dep_map: Dict[str, List[str]] = {}

    for jname, jbody in jobs.items():
        if not isinstance(jbody, dict):
            continue
        needs = jbody.get("needs")
        deps: List[str] = []
        if isinstance(needs, str):
            deps = [needs]
        elif isinstance(needs, list):
            deps = [str(n) for n in needs]
        dep_map[jname] = deps

        for d in deps:
            if d not in job_names:
                # 判断是不是误把 step id 当 job（历史事故的确切形态）
                step_ids = set()
                for jb in jobs.values():
                    if isinstance(jb, dict):
                        for st in jb.get("steps") or []:
                            if isinstance(st, dict) and st.get("id"):
                                step_ids.add(st["id"])
                hint = "（该名称是某个 step 的 id，不是 job）" if d in step_ids else ""
                res["errors"].append(
                    f"E2 job '{jname}' 的 needs 指向不存在的 job '{d}'{hint}"
                )

        # needs.<job>.outputs 引用校验
        for m in re.finditer(r"needs\.([A-Za-z0-9_-]+)\.", json.dumps(jbody, ensure_ascii=False)):
            ref = m.group(1)
            if ref not in job_names:
                res["errors"].append(f"E2 job '{jname}' 引用了不存在的 needs.{ref}")
            elif ref not in deps:
                res["warnings"].append(
                    f"W4 job '{jname}' 引用 needs.{ref} 但未在 needs 中声明依赖"
                )

    cycle = _detect_cycle(dep_map)
    if cycle:
        res["errors"].append(f"E3 job 依赖成环: {' -> '.join(cycle)}")

    # 引用的本地脚本 / 本地 action 是否存在（与 action 分支共用同一实现）
    _check_local_refs(text, res)

    # 测试步骤被 continue-on-error 架空
    for jname, jbody in jobs.items():
        if not isinstance(jbody, dict):
            continue
        for st in jbody.get("steps") or []:
            if not isinstance(st, dict):
                continue
            name = (st.get("name") or "").lower()
            run = st.get("run") or ""
            # 只认"真的在跑测试套件"的步骤。诊断/探活步骤名里也常带 test，
            # 但它们本就该 continue-on-error（属可观测性，不是门禁），不应误报。
            TEST_CMDS = ("run_all.py", "quick_test.py", "pytest",
                         "npm test", "npm run test", "py_compile",
                         "validate_workflows.py")
            is_test = any(c in run for c in TEST_CMDS)
            if is_test and st.get("continue-on-error") is True:
                res["warnings"].append(
                    f"W1 job '{jname}' 步骤 '{st.get('name') or run[:30]}' "
                    f"跑了测试却设 continue-on-error，测试无法阻断发布"
                )

    # ── E11 有第三方依赖的入口必须引用统一前置（派生判据）────────────────
    # 判据：job 内出现真正的命令行（注释不算）——
    #   · 跑全量套件（python tests/run_all.py）→ 入口 = 整套 tests/*.py；
    #   · 跑本仓脚本（python scripts/xxx.py）→ 入口 = 该脚本；
    # 沿这些入口做第三方依赖闭包，非空却没用统一前置 → 报错。
    #
    # 为什么是派生的而不是「盯着 run_all.py」：本仓曾有三处**同类**漏洞，
    # 全都不是 run_all.py —— ci.yml 的 workflow-lint 与 meta-monitor 的 inspect
    # 各自 `pip install pyyaml`（同一件事的第二、第三处实现），
    # unified-security-scan 的 self-scan 则干脆什么都没装（YAML 策略静默退回
    # 极简解析器、签名后端退回 hmac）。写死名单的检查永远追不上下一个入口。
    for jname, jbody in jobs.items():
        if not isinstance(jbody, dict):
            continue
        steps = [st for st in (jbody.get("steps") or []) if isinstance(st, dict)]
        entries = _job_entry_files(jbody)
        if not entries:
            continue
        deps = sorted(_third_party_of(entries))
        if not deps:
            continue
        has_prep = any((st.get("uses") or "").strip().startswith(PREP_ACTION)
                       for st in steps)
        if has_prep:
            continue
        shown = sorted({_rel(p) for p in entries})
        res["errors"].append(
            f"E11 job '{jname}' 运行了本仓入口 {shown[:3]}{' 等' if len(shown) > 3 else ''}，"
            f"其依赖闭包含第三方包 {deps}，却没有引用 {PREP_ACTION} —— "
            f"缺包时轻则用例成片报红（看起来像产品回归），重则**静默降级**："
            f"签名后端退回 hmac-sha256、YAML 策略退回极简解析器。"
            f"请改用该 action 统一安装（不需要 node 依赖就传 install-node-deps: 'false'）"
        )
    return res


def _check_prereq_covers_suite_deps(results: List[Dict[str, Any]]) -> None:
    """E12 / W6：统一前置声明的依赖必须与测试套件的真实依赖一致（双向 diff）。

    这条检查的价值不在于"抓到这一次" —— 而在于它**不需要人来维护清单**：
    依赖是从代码里推导出来的，前置是从 action 里解析出来的，任何一侧变了，
    下一次运行就会报出来。这正是"收敛到一处之后必须更严格地守住那一处"。
    """
    if yaml is None:
        # 没有 PyYAML 时连 action 都解析不了（E1 会报出来），不必再叠加噪音
        return
    prep = next((r for r in results
                 if r.get("path") == PREP_ACTION_FILE), None)
    if prep is None:
        return  # action 不存在 / 未被扫描 —— 由 E4 与测试兜底，这里不重复报

    derived = _third_party_of(_test_suite_entry_files())
    declared = set(prep.get("pip_deps") or ())

    for name in sorted(set(derived) - declared):
        users = sorted(set(derived[name]))[:3]
        prep["errors"].append(
            f"E12 测试套件依赖第三方包 '{name}'（{', '.join(users)}），"
            f"但 {PREP_ACTION_FILE} 没有安装它 —— 干净 runner 上这些用例会以"
            f"「ImportError / 静默跳过」的形式失败，看起来像产品回归"
            f"（2026-10-05 因此让 spine 连停两天）。请在该 action 的 pip install 行补上"
        )
    for name in sorted(declared - set(derived)):
        prep["warnings"].append(
            f"W6 统一前置安装了 '{name}'，但测试套件已不再依赖它 —— "
            f"要么删掉这行声明，要么在注释里说明它是给调用方脚本用的"
        )


def cross_check(results: List[Dict[str, Any]]) -> None:
    """跨文件检查 E7：workflow_run 引用了不存在的 workflow 名。

    GitHub 对写错的 workflow 名**不会报任何错**，该触发器只是永不生效。
    这与当初 self-heal 静默死亡 48 天是同一类故障：
    配置看起来完全正常，实际从未生效，且没有任何信号告诉你。
    """
    _check_prereq_covers_suite_deps(results)
    _check_auto_resolvable_paths(results)

    known = {r["name"] for r in results if r.get("name")}
    for r in results:
        for ref in r.get("workflow_run_refs", []):
            if ref not in known:
                near = [n for n in known if n and (
                    ref.lower() in n.lower() or n.lower() in ref.lower())]
                hint = f"，最接近的是 '{near[0]}'" if near else ""
                r["errors"].append(
                    f"E7 workflow_run 引用了不存在的 workflow 名 '{ref}'"
                    f" —— 该触发器永不生效{hint}"
                )

    # W4/W5 调度拥塞检查
    #
    # GitHub 官方明确说明：schedule 事件在高负载时段会被延迟，甚至直接丢弃，
    # 而「每小时的开始」正是高负载时段。整点排任务 = 主动把自己排进最可能
    # 被丢弃的时间格。多个 workflow 共用同一表达式则会进一步加剧竞争。
    slots: Dict[str, List[str]] = {}
    for r in results:
        for cron in r.get("crons", []):
            slots.setdefault(cron, []).append(r["file"])

    for cron, files in slots.items():
        parts = str(cron).split()
        if len(parts) == 5 and parts[0] == "0":
            for f in files:
                for r in results:
                    if r["file"] == f:
                        r["warnings"].append(
                            f"W4 cron '{cron}' 排在整点，GitHub 高负载时段易被延迟或丢弃"
                            f" —— 建议错开到非整点分钟"
                        )
        if len(files) > 1:
            for f in files:
                for r in results:
                    if r["file"] == f:
                        others = [x for x in files if x != f]
                        r["warnings"].append(
                            f"W5 cron '{cron}' 与 {', '.join(others)} 完全撞车，互相争抢配额"
                        )


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield Workflow 校验器")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not WF_DIR.exists():
        print("未找到 .github/workflows 目录")
        return 0

    files = sorted(list(WF_DIR.glob("*.yml")) + list(WF_DIR.glob("*.yaml")))
    action_files = (sorted(ACTION_DIR.glob("*/action.yml")) if ACTION_DIR.exists() else [])
    files = files + action_files
    results = [check_file(f) for f in files]
    cross_check(results)
    n_err = sum(len(r["errors"]) for r in results)
    n_warn = sum(len(r["warnings"]) for r in results)

    if args.json:
        print(json.dumps(
            {"total": len(files), "errors": n_err, "warnings": n_warn, "results": results},
            ensure_ascii=False, indent=2))
    else:
        n_actions = len(action_files)
        print(f"校验 {len(files)} 个文件（{len(files) - n_actions} workflow + "
              f"{n_actions} local action）\n" + "=" * 62)
        for r in results:
            if r["errors"] or r["warnings"]:
                icon = "❌" if r["errors"] else "⚠️ "
                kind = ("composite action" if r.get("kind") == "action"
                        else "policy declaration" if r.get("kind") == "policy"
                        else f"jobs: {', '.join(r['jobs']) or '-'}")
                print(f"\n{icon} {r['file']}  ({kind})")
                for e in r["errors"]:
                    print(f"     ERROR  {e}")
                for w in r["warnings"]:
                    print(f"     WARN   {w}")
            else:
                print(f"✅ {r['file']}")
        print("\n" + "=" * 62)
        print(f"结果：{n_err} 个错误，{n_warn} 个警告")
        if n_err == 0:
            print("所有 workflow 依赖链合法，可被 GitHub Actions 正常解析。")
    return 1 if n_err else 0


if __name__ == "__main__":
    raise SystemExit(main())
