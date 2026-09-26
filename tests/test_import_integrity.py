"""
仓库内 import 完整性门禁 —— 防止"代码引用了仓库内一个不存在的模块/符号"。

2026-09-25 事故复盘：本地工作树有 api/trust_api.py 的 attestation 扩展
(generate_attestation 等 9 个函数)，但 main 分支上从未推送过那个文件。
结果是 `import api.server` 在 CI 的干净 checkout 上直接 ImportError，
unified-security-scan 连续 8 次红灯，而本机一切正常——因为本机有那份文件。

更隐蔽的一层：main 上还有 5 个被引用的模块根本不存在
(eco/crypto_sign.py、eco/platform.py、eco/protocol_bridge.py、
collector/audit_chain.py、scanner/sandbox.py)。它们没有炸，只是因为引用点要么
在 try/except 里、要么在函数体内的惰性 import 里、要么在 server.py 请求处理器
的惰性 import 里——CI 只跑 `import api.server`，永远触达不到。

本门禁做的事：
  1. 解析全仓库 *.py 里的 import / from ... import，挑出指向本仓库内部模块的
  2. 断言每个内部模块文件都存在
  3. 对 `from X import Y` 形式，进一步断言 Y 真的在 X 里定义了（除非是 try/except
     包裹的降级 import，那种按设计允许失败）

它把"引用存在性"从人工记得推送 变成 可执行断言。
"""

import ast
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "api"))
sys.path.insert(0, os.path.join(ROOT, "eco"))
sys.path.insert(0, os.path.join(ROOT, "collector"))

# 这些是仓库的顶层包/模块前缀。命中它们的 import 才算"仓库内部引用"。
# node_modules / dist / .workbuddy 里的东西不在门禁范围内。
INTERNAL_ROOTS = {
    "scanner", "eco", "connectors", "registry", "proxy", "collector",
    "tests", "scripts",
}
# api/ 下的模块（server.py / trust_api.py / openapi_spec.py / ecosystem_api.py ...）
# 既可作为 `import X`（因为 server.py 把 api/ 塞进了 sys.path），
# 也可作为 `from api import X`。两种形态都要覆盖。
API_MODULES = None      # 运行时计算
THIRD_PARTY = None      # 运行时计算
REPO_STEMS = None       # 运行时计算


def _api_module_names():
    """api/ 下的 .py 文件名（去掉扩展名）。

    api/ 既没有 __init__.py（namespace 包），又被 server.py 塞进 sys.path，
    所以 `import trust_api`、`import proxy`、`import ecosystem_api` 这些
    裸名字都能解析到 api/<name>.py —— 两种形态都要能查。
    """
    global API_MODULES
    if API_MODULES is not None:
        return API_MODULES
    d = os.path.join(ROOT, "api")
    API_MODULES = set()
    if os.path.isdir(d):
        for fn in os.listdir(d):
            if fn.endswith(".py"):
                API_MODULES.add(fn[:-3])
    return API_MODULES


def _third_party_names():
    """仓库声明的第三方依赖名集合（requirements*.txt 的 import 名形式）。

    用于区分「裸 import 指向仓库内部模块」和「裸 import 指向第三方包」。
    只认 requirements 文件里声明过的，避免把仓库内模块误当第三方放行。

    发行名与 import 名不一致时无法自动推导（PyYAML 的 import 名是 yaml、
    Pillow 是 PIL），故维护一张显式别名表；其余按「小写 + 连字符转下划线」
    以及「连字符前缀」（kafka-python 的 import 名是 kafka）两条规则归一。
    """
    global THIRD_PARTY
    if THIRD_PARTY is not None:
        return THIRD_PARTY
    THIRD_PARTY = set()
    aliases = {
        "pyyaml": "yaml",
        "pillow": "pil",
        "python-seccomp": "seccomp",
        "kafka-python": "kafka",
        "python-dateutil": "dateutil",
        "python-multipart": "multipart",
        "beautifulsoup4": "bs4",
        "scikit-learn": "sklearn",
        "opencv-python": "cv2",
        "flatbuffers": "flatbuffers",
    }
    for fn in os.listdir(ROOT):
        if not fn.startswith("requirements") or not fn.endswith(".txt"):
            continue
        try:
            with open(os.path.join(ROOT, fn), "r",
                      encoding="utf-8-sig") as f:
                for line in f:
                    line = line.split("#", 1)[0].strip()
                    if not line or line.startswith("-r ") or line.startswith("--"):
                        continue
                    dist = re.split(r"[<>=!~;\[ ]", line, maxsplit=1)[0].strip()
                    if not dist:
                        continue
                    low = dist.lower()
                    if low in aliases:
                        THIRD_PARTY.add(aliases[low])
                    THIRD_PARTY.add(low.replace("-", "_"))
                    if "-" in dist:
                        THIRD_PARTY.add(dist.split("-", 1)[0].lower())
        except OSError:
            continue
    return THIRD_PARTY


def _repo_module_stems():
    """仓库里所有 .py 模块的文件名（小写），不含 tests/ 与 _scratch/。

    一些脚本会 sys.path.insert 其它仓库子目录：scripts/arena/jev_player.py
    挂上 scripts/typesafe 后 `import jev_client`，
    scripts/typesafe/citation_adjudicator.py 挂上 scripts 后 `import benchmark`。
    这类引用的可达性取决于运行时 sys.path，静态推不出来（路径表达式是
    os.path.join(ROOT, "scripts", "typesafe") 这种动态拼装）。
    因此退一步：只要仓库内任意位置存在同名模块就算可达 —— 门禁要拦的是
    「文件根本不在仓库里」这一类（干净 checkout 必炸），而不是精确验证
    每个导入者的 sys.path 拼装是否完整（那是另一个量级的问题，误报远多于命中）。
    """
    global REPO_STEMS
    if REPO_STEMS is not None:
        return REPO_STEMS
    skip = {"__pycache__", "node_modules", ".workbuddy", "dist", ".cilog",
            "venv", ".venv", ".remotecheck", "_scratch", "tests"}
    REPO_STEMS = set()
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in skip]
        REPO_STEMS.update(f[:-3].lower() for f in fn if f.endswith(".py"))
    return REPO_STEMS


def _resolve_candidates(mod_path, base_dir=None):
    """把一个点分模块名展开成所有可能的落盘路径。

    只列「仓库根目录」和「api/」两个 sys.path 根。这两个是确定在 sys.path 上
    的（仓库根是 Python 对脚本入口的隐式根，api/ 由 server.py 显式插入），
    也是 CI 干净 checkout 上唯一能可靠解析的根。

    刻意不列「导入者所在目录」：scripts/、tests/、scripts/arena/ 等目录是靠
    tests/run_all.py 或各脚本自己 sys.path.insert 临时挂上去的，本地顺序与
    CI 顺序不同，用导入者目录做判定会把环境问题误判成代码缺陷（或反过来
    放过真缺陷）。scripts/harness_corpus.py 未推送时的漏检，正确修法就是让
    判定落在仓库根上，而不是顺着导入者目录找。
    """
    parts = mod_path.split(".")
    cands = []
    if parts[0] == "api":
        # `api` -> api/ 目录本身；`api.server` -> api/server.py
        if len(parts) == 1:
            cands.append(os.path.join(ROOT, "api"))
        else:
            cands.append(os.path.join(ROOT, "api", *parts[1:-1], parts[-1] + ".py"))
            cands.append(os.path.join(ROOT, "api", *parts[1:], "__init__.py"))
    else:
        cands.append(os.path.join(ROOT, *parts[:-1], parts[-1] + ".py"))
        cands.append(os.path.join(ROOT, *parts, "__init__.py"))
        cands.append(os.path.join(ROOT, *parts))          # namespace 包
        # 裸名字回落到 api/（api/ 在 sys.path 上）
        if len(parts) == 1:
            cands.append(os.path.join(ROOT, "api", parts[0] + ".py"))
            cands.append(os.path.join(ROOT, "api", parts[0], "__init__.py"))
    return cands


def _module_exists(mod_path, base_dir=None):
    """`a.b.c` 或裸 `trust_api` 形式的模块是否落盘。"""
    return any(os.path.exists(p) for p in _resolve_candidates(mod_path, base_dir))


def _top_is_internal(mod_path, base_dir=None, self_path=None):
    top = mod_path.split(".")[0]
    if mod_path == "api" or mod_path.startswith("api."):
        return True
    # tests/ 下的文件靠 tests/run_all.py 把 scripts/ 挂上 sys.path 后
    # `import self_scan` 这类跨目录取用，导入者目录既不是仓库根也不是 api/，
    # 用仓库根的判定规则会全是误报，故整体豁免。
    if base_dir and os.path.basename(os.path.normpath(base_dir)) == "tests":
        return False
    if top in INTERNAL_ROOTS:
        return True
    if top in _api_module_names():
        return True
    # 裸名字且不是标准库、也不是 requirements 里声明的第三方依赖
    # → 只能是仓库内部模块，必须落盘存在。
    #
    # 这个判定刻意**不**引用"目标文件是否存在"。早先的版本用
    # 「导入者所在目录里是否真有同名模块」来判内部引用，结果目标文件一缺失
    # 就判不成内部引用、整个 import 被静默跳过 —— scripts/harness_corpus.py
    # 未推送时正是这么漏掉的：tests/test_benchmark.py 的 15 个用例在干净
    # CI 上一律 ModuleNotFoundError，而门禁一路绿灯。
    # 大小写归一：Pillow 的 import 名是 PIL，sys.stdlib_module_names 全是小写。
    third = {n.lower() for n in _third_party_names()}
    if ("." not in mod_path
            and top.lower() not in getattr(sys, "stdlib_module_names", ())
            and top.lower() not in third):
        return True
    return False


def _module_file(mod_path, base_dir=None):
    """`a.b.c` 或裸 `trust_api` 形式的模块对应的 .py 路径；找不到返回 None。"""
    for p in _resolve_candidates(mod_path, base_dir):
        if p.endswith(".py") and os.path.isfile(p):
            return p
    return None


def _assign_targets(node):
    """从 Assign / AnnAssign 节点取出绑定的名字。"""
    out = set()
    if isinstance(node, ast.Assign):
        for tg in node.targets:
            if isinstance(tg, ast.Name):
                out.add(tg.id)
            elif isinstance(tg, (ast.Tuple, ast.List)):
                for e in tg.elts:
                    if isinstance(e, ast.Name):
                        out.add(e.id)
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        out.add(node.target.id)
    return out


def _names_from_stmts(stmts):
    """从一组语句里收集它们绑定的名字（不进入函数/类体）。"""
    names = set()
    for stmt in stmts:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(stmt.name)
        elif isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            names.update(_assign_targets(stmt))
        elif isinstance(stmt, ast.Import):
            for alias in stmt.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(stmt, ast.ImportFrom):
            if any(a.name == "*" for a in stmt.names):
                names.add("*")
            for alias in stmt.names:
                if alias.name != "*":
                    names.add(alias.asname or alias.name)
        elif isinstance(stmt, ast.Try):
            # 模块级 try/except 是常见写法：
            #   try:
            #       from scanner.rules import get_rule_count
            #       SCANNER_AVAILABLE = True
            #   except Exception:
            #       SCANNER_AVAILABLE = False
            # 名字在 if-else 两侧都可能出现，body/handlers/orelse/finalbody 都要收。
            names.update(_names_from_stmts(stmt.body))
            for h in stmt.handlers:
                names.update(_names_from_stmts(h.body))
            names.update(_names_from_stmts(stmt.orelse))
            names.update(_names_from_stmts(stmt.finalbody))
        elif isinstance(stmt, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            names.update(_names_from_stmts(stmt.body))
            names.update(_names_from_stmts(stmt.orelse))
        elif isinstance(stmt, (ast.With, ast.AsyncWith)):
            names.update(_names_from_stmts(stmt.body))
    return names


def _defined_names(path):
    """AST 解析一个模块文件，返回它顶层定义的名字集合。

    纯静态分析、绝不 import —— 这是有意的。用 importlib 去逐个导入 200 多个
    模块会让门禁依赖本机装了哪些第三方包（browser-use / neo4j / kafka-python
    都是可选依赖），并且执行这些模块的顶层副作用会污染后续测试。在干净 checkout
    上「某模块缺可选依赖而导入失败」会被误判成「门禁不过」，把环境噪音当缺陷报。

    返回集合里含 "*" 表示该模块有 `from x import *`，此时任何名字都放行。

    两处实测踩过的坑：
      1. 必须用 utf-8-sig 读 —— eco/a2a_gateway.py 带 UTF-8 BOM，用 utf-8 读会让
         ast.parse 抛 `SyntaxError: invalid non-printable character U+FEFF`，于是
         这个模块所有类名都被误报成"未定义"。
      2. 名字不只出现在 tree.body 的直接子节点上 —— api/arena_core.py 的
         SCANNER_AVAILABLE / _get_rule_count 定义在模块级 try/except 里，
         只看 tree.body 会把 Try 节点整体当"不绑定任何名字"。
    """
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            tree = ast.parse(f.read())
    except (SyntaxError, OSError):
        return set()
    return _names_from_stmts(tree.body)


class TestInternalImportTargetsExist(unittest.TestCase):
    """每个指向仓库内部的 import 都必须能落盘解析到真实文件。"""

    def _iter_files(self):
        """yield (相对路径, 已解析的 AST)。跳过生成物与第三方目录。"""
        skip = {"__pycache__", "node_modules", ".workbuddy", "dist", ".cilog",
                "_scratch", "venv", ".venv", ".remotecheck"}
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in skip]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
                try:
                    with open(path, "rb") as fh:
                        # utf-8-sig：eco/a2a_gateway.py 带 BOM，用 utf-8 读会
                        # 让 ast.parse 抛 SyntaxError，整个文件静默漏检。
                        tree = ast.parse(fh.read().decode("utf-8-sig"))
                except (SyntaxError, OSError, UnicodeDecodeError):
                    continue
                yield rel, tree

    def _iter_imports(self):
        """yield (file, module_path, names, exempt)

        names 为 None 表示 `import X`。exempt=True 表示该 import 被
        try/except ImportError 包裹且兜底分支里有真实的降级实现。

        两种被包裹的 import 必须区别对待：

          try:
              from eco import crypto_sign as cs   # 没有降级实现
          except ImportError:
              import crypto_sign as cs            # 只是换写法再 import 一次
          —— 两条路径指向同一个缺失文件，目标不存在时照样 ImportError。

          try:
              from scanner.prompt_checker import check_prompt_injection
          except ImportError:
              def check_prompt_injection(prompt):  # 真实的降级实现
                  return {"detected": False, ...}
          —— 按设计允许目标缺失，模块文档也明确写了"可选依赖"。
        """
        skip = {"__pycache__", "node_modules", ".workbuddy", "dist", ".cilog",
                "_scratch",
                "venv", ".venv", ".remotecheck"}
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in skip]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
                try:
                    # utf-8-sig：eco/a2a_gateway.py 带 BOM，用 utf-8 读会让该文件
                    # 静默解析失败，它里面的 import 就全部逃过检查。
                    with open(path, "r", encoding="utf-8-sig") as f:
                        tree = ast.parse(f.read())
                except (SyntaxError, OSError):
                    continue
                fallback = {}
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Try):
                        continue
                    for h in node.handlers:
                        t = h.type
                        is_import_err = (
                            (isinstance(t, ast.Name) and t.id == "ImportError")
                            or (isinstance(t, ast.Tuple)
                                and any(isinstance(e, ast.Name) and e.id == "ImportError"
                                        for e in t.elts)))
                        if not is_import_err:
                            continue
                        span = range(node.lineno,
                                     getattr(node, "end_lineno", node.lineno) + 1)
                        provided = set()
                        for stmt in h.body:
                            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef,
                                                  ast.ClassDef)):
                                provided.add(stmt.name)
                            elif isinstance(stmt, ast.Assign):
                                for tg in stmt.targets:
                                    if isinstance(tg, ast.Name):
                                        provided.add(tg.id)
                                    elif isinstance(tg, ast.Tuple):
                                        for e in tg.elts:
                                            if isinstance(e, ast.Name):
                                                provided.add(e.id)
                            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                                provided.add(stmt.target.id)
                        for n2 in span:
                            fallback.setdefault(n2, set()).update(provided)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if not _top_is_internal(alias.name, dirpath, path):
                                continue
                            bound = alias.asname or alias.name.split(".")[0]
                            ex = bool(fallback.get(node.lineno, set()) & {bound})
                            yield rel, alias.name, None, ex, dirpath
                    elif isinstance(node, ast.ImportFrom):
                        if node.module is None or node.level:
                            continue
                        if not _top_is_internal(node.module, dirpath, path):
                            continue
                        names = [a.name for a in node.names]
                        provided = fallback.get(node.lineno, set())
                        ex = bool(provided and any(a.name in provided for a in node.names))
                        yield rel, node.module, names, ex, dirpath

    def _resolvable_via_dynamic_path(self, mod, base_dir):
        """裸名字能否经由「运行时才挂上 sys.path 的目录」解析到。

        兜底路径有两条：导入者所在目录（scripts/arena/jev_player.py 挂 HERE
        后 `import arena_client`），以及仓库内任意位置存在同名模块
        （citation_adjudicator.py 挂 scripts/ 后 `import benchmark`）。

        这只作为「已判定为内部引用之后」的解析路径，不参与 _top_is_internal
        的判定 —— 后者一旦引用存在性，目标文件缺失时就判不成内部引用而
        静默跳过，那正是漏检的根因。
        """
        if "." in mod:
            return False
        if base_dir and (os.path.isfile(os.path.join(base_dir, mod + ".py"))
                         or os.path.isdir(os.path.join(base_dir, mod))):
            return True
        return mod.lower() in _repo_module_stems()

    def test_all_internal_module_targets_exist(self):
        """每个指向仓库内部的 import 都必须落盘解析到真实文件。

        唯一豁免：try/except ImportError 且兜底分支里有真实的降级实现。
        只换个写法再 import 一次不算降级（`from eco import crypto_sign` /
        `import crypto_sign` 两条路径都指向同一个缺失文件，照样 ImportError）。

        覆盖三种裸名字形态：api/ 下的（`import trust_api`）、
        同目录兄弟模块（scripts/ 里的 `import harness_corpus`）。
        后者此前完全漏检 —— scripts/harness_corpus.py 未推送时，
        tests/test_benchmark.py 的 15 个用例在干净 CI 上一律
        ModuleNotFoundError，而门禁一路绿灯。
        """
        missing = []
        for rel, mod, names, exempt, base_dir in self._iter_imports():
            if exempt or _module_exists(mod, base_dir) \
                    or self._resolvable_via_dynamic_path(mod, base_dir):
                continue
            missing.append("  %s -> %s" % (rel, mod))
        self.assertEqual(
            missing, [],
            msg="以下 import 指向的仓库内模块文件不存在——干净 checkout 上会 ImportError：\n"
                + "\n".join(sorted(set(missing))))

    def test_imported_names_are_defined(self):
        """`from X import Y` 里的 Y 必须是 X 的子模块或 X 里已定义的名字。

        `from eco import agent_gateway` 导入的是 eco/agent_gateway.py 这个子模块，
        而不是 eco/__init__.py 上的属性 —— 两种解析路径都要接受。
        """
        problems = []
        cache = {}
        for rel, mod, names, exempt, base_dir in self._iter_imports():
            if not names or exempt or not _module_exists(mod, base_dir):
                continue
            key = (mod, base_dir)
            if key not in cache:
                src = _module_file(mod, base_dir)
                cache[key] = _defined_names(src) if src else set()
            defined = cache[key]
            if "*" in defined:
                continue
            for name in names:
                if name == "*":
                    continue
                if _module_exists(mod + "." + name, base_dir):
                    continue
                if name in defined:
                    continue
                problems.append("  %s -> %s.%s 未定义" % (rel, mod, name))
        self.assertEqual(
            problems, [],
            msg="以下 from-import 的符号既不是子模块也不是目标模块里已定义的名字：\n"
                + "\n".join(sorted(set(problems))))

    def test_bare_import_does_not_shadow_stdlib(self):
        """裸 `import M` 不得命中与标准库同名的仓库模块。

        eco/sandbox_backend.py 里写 `import platform` 要的是标准库，
        但 eco/ 挂在 sys.path 上且有 eco/platform.py，于是解析结果取决于
        导入顺序：标准库 platform 若已被别的依赖先加载就没事，一旦是首次
        加载就落到 eco/platform.py，platform.system() 抛
        AttributeError: module 'platform' has no attribute 'system'。
        本地因为 sys.modules 里恰好已有标准库 platform 而长期未炸，
        干净 CI runner 上必炸。

        判定依据：模块名在 sys.stdlib_module_names 里（Python 3.10+ 权威清单），
        且仓库里存在同名 .py 落盘 —— 两者同时成立即为遮蔽风险。

        注意这里**不**复用 _iter_imports：那个迭代器只产出 _top_is_internal
        判为内部引用的 import，而本测试要找的恰恰是标准库名字，
        已经被 _top_is_internal 的 `top not in stdlib` 条件排除了。
        """
        shadows = []
        stdlib = getattr(sys, "stdlib_module_names", frozenset())
        # 一次性收集仓库内所有 .py 的文件名，避免每个 import 都全树扫。
        flat = set()
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames
                           if d not in {"__pycache__", "node_modules",
                                        ".workbuddy", "dist", ".cilog",
                                        "venv", ".venv", ".remotecheck",
                                        "_scratch"}]
            flat.update(fn[:-3] for fn in filenames if fn.endswith(".py"))
        for rel, tree in self._iter_files():
            for node in ast.walk(tree):
                if not isinstance(node, ast.Import):
                    continue
                for alias in node.names:
                    mod = alias.name
                    if "." in mod or mod not in stdlib or mod not in flat:
                        continue
                    shadows.append("  %s:%d -> import %s（遮蔽标准库）"
                                   % (rel, node.lineno, mod))
        self.assertEqual(
            shadows, [],
            msg="以下裸 import 会按导入顺序在标准库与仓库同名模块之间摇摆，"
                "应改用显式标准库加载或给仓库模块改名：\n"
                + "\n".join(sorted(set(shadows))))


if __name__ == "__main__":
    unittest.main()
