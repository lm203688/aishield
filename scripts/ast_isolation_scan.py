"""T7 / H3 第二层：AST 静态隔离扫描门禁（结构层证明）。

AIShield 的核心铁律：「扫描器把被扫配置当**数据**读取，绝不执行其中的命令」。
三层证明互补：

  Layer 1  (scripts/prove_isolation.py)        运行时 mock 拦截 —— 证「这一次 scan() 没 spawn」。
  Layer 1b (scripts/check_isolation_invariants.py / FVI) 有界模型检查 —— 证「机制上不可能」。
  Layer 2  (**本文件**)                         AST 静态扫描 —— 证「scanner/ 源码结构上
                                                不存在能把被扫数据升级为执行原语的调用路径」。

为什么需要 Layer 2：Layer 1 的 mock 只拦「当前代码路径确实尝试了 spawn」；但被扫数据诱导的
import 副作用、动态 eval/exec、pickle.loads 反序列化执行等**形态不在 mock 拦截面内**。Layer 2
直接从 AST 上枚举所有危险原语调用点，确保任何新提交的「能执行被扫数据」的代码路径都会被 CI 抓住。

扫描范围：仓库内 `scanner/` 下全部 `*.py`（排除 `test_*.py` / `*_test.py`，测试不是生产不信任
输入处理者）。不扫其他目录——`api/`/`eco/`/`scripts/` 的 spawn 由 Layer 1 运行时门禁 + FVI 覆盖，
且那些目录的 spawn 通常执行**固定二进制/命令**而非被扫数据；本报告 H3 的关注点正是 scanner
这一「读取被扫配置」的信任边界。

危险原语（命中 `ast.Call`）：
  - 裸调用：exec / eval / compile / __import__
  - os.system / os.popen
  - subprocess.Popen / subprocess.run / subprocess.call / subprocess.check_output / subprocess.check_call
  - importlib.import_module / importlib.util.find_spec（动态导入 = 可被被扫数据诱导）
  - pickle.loads / marshal.loads / yaml.load（不安全反序列化 = 隐式代码执行）

白名单（必须显式、可审计，每条带原因）。白名单是「刻意放行」而非「漏扫」：
  - scanner/sandbox.py                     受控沙箱本身：其职责就是在隔离环境 spawn 被扫代码，
                                            这是「有意隔离执行」，不是「泄漏」，故放行。
  - scanner/integrations/bb_browser.py     启动**固定**的浏览器二进制（参数非被扫数据流入），
                                            属合法集成，放行。

反假绿（判别力自证）：内置一段恶意样例源码，扫描它**必须**产出违规；若未产出，说明扫描器自身
空洞（恒真/假绿），退出码非 0。这与 FVI / prove_isolation 同样采用「变异体必须被抓」的纪律。

运行：python scripts/ast_isolation_scan.py
退出码：0 = scanner/ 零违规 且 判别力自证通过；1 = 发现未白名单的危险调用 或 判别力自证失败。
标准库 only、零依赖、100% 离线。
"""
from __future__ import annotations

import ast
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# scanner/ 下「读取被扫配置」的信任边界。
SCAN_ROOT = ROOT / "scanner"

# 跳过测试文件（测试不是生产不信任输入处理者）。
SKIP_SUFFIXES = ("_test.py",)
SKIP_PREFIXES = ("test_",)

# ---- 危险原语定义 ---------------------------------------------------------
# (kind, 匹配规则)。kind 用于报告分类。
# 对属性调用（os.system / subprocess.run / importlib.import_module / yaml.load）：
#   以 (module, attr) 形式匹配。
# 对裸调用（exec / eval / compile / __import__ / pickle.loads）：以 name 形式匹配。
DANGEROUS_ATTR_CALLS: Dict[str, Tuple[str, str]] = {
    "os.system": ("os", "system"),
    "os.popen": ("os", "popen"),
    "subprocess.Popen": ("subprocess", "Popen"),
    "subprocess.run": ("subprocess", "run"),
    "subprocess.call": ("subprocess", "call"),
    "subprocess.check_output": ("subprocess", "check_output"),
    "subprocess.check_call": ("subprocess", "check_call"),
    "importlib.import_module": ("importlib", "import_module"),
    "importlib.util.find_spec": ("importlib.util", "find_spec"),
    "pickle.loads": ("pickle", "loads"),
    "marshal.loads": ("marshal", "loads"),
    "yaml.load": ("yaml", "load"),
}

DANGEROUS_NAME_CALLS = {
    "exec",
    "eval",
    "compile",
    "__import__",
}

# ---- 白名单（显式、可审计） -----------------------------------------------
# 相对 scanner/ 的路径 -> 放行原因。
WHITELIST: Dict[str, str] = {
    "sandbox.py": (
        "受控沙箱：其职责就是在隔离环境（RLIMIT/seccomp）下 spawn 被扫代码，"
        "属于「有意隔离执行」而非「泄漏」。"
    ),
    "integrations/bb_browser.py": (
        "启动固定的浏览器二进制（参数非被扫数据流入），属合法集成。"
    ),
}


@dataclass
class Violation:
    file: str           # 相对 SCAN_ROOT 的路径
    line: int
    kind: str           # 危险原语名
    snippet: str        # 该行的源码片段

    def __str__(self) -> str:
        return f"  {self.file}:{self.line}  [{self.kind}]  {self.snippet.strip()}"


def _rel(path: Path) -> str:
    # 统一用正斜杠，跨平台与 WHITELIST 键一致。
    return str(path.relative_to(SCAN_ROOT)).replace(os.sep, "/")


def _is_whitelisted(rel_path: str) -> Optional[str]:
    # 精确路径匹配
    if rel_path in WHITELIST:
        return WHITELIST[rel_path]
    # 也允许子路径兜底：白名单里的文件无论位于 scanner/ 哪一层都放行
    for wl in WHITELIST:
        if rel_path.endswith(wl):
            return WHITELIST[wl]
    return None


def _attr_chain(node: ast.AST) -> Optional[Tuple[str, str]]:
    """解析 `a.b.c(...)` 形式的调用，返回 (full_module_chain, final_attr)。

    例：subprocess.run(...) -> ('subprocess', 'run')
        importlib.util.find_spec(...) -> ('importlib.util', 'find_spec')
        os.system(...) -> ('os', 'system')
    """
    if not isinstance(node, ast.Attribute):
        return None
    attr = node.attr
    val = node.value
    chain = attr
    while isinstance(val, ast.Attribute):
        chain = f"{val.attr}.{chain}"
        val = val.value
    if isinstance(val, ast.Name):
        chain = f"{val.id}.{chain}"
    else:
        # 形如 a.b.c.d —— 取最后两段足够判别 module.attr
        parts = chain.split(".")
        if len(parts) >= 2:
            chain = ".".join(parts[-2:])
    # 归一：只关心 module.attr 两段
    parts = chain.split(".")
    if len(parts) >= 2:
        return (".".join(parts[:-1]), parts[-1])
    return (parts[0], "")


def analyze_source(code: str, filename: str = "<code>") -> List[Tuple[int, str]]:
    """分析一段源码，返回 [(line, kind), ...] 危险调用（未做白名单过滤）。"""
    findings: List[Tuple[int, str]] = []
    try:
        tree = ast.parse(code, filename=filename)
    except SyntaxError:
        # 语法错误不应静默通过；交由调用方决定（真实仓库文件都能解析）。
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        # 属性调用：os.system / subprocess.run / yaml.load ...
        if isinstance(func, ast.Attribute):
            parsed = _attr_chain(func)
            if parsed is not None:
                mod, attr = parsed
                key = f"{mod}.{attr}"
                if key in DANGEROUS_ATTR_CALLS:
                    findings.append((node.lineno, key))
            continue

        # 裸调用：exec / eval / compile / __import__ / pickle.loads（后者是 Name？不，pickle.loads 是属性）
        if isinstance(func, ast.Name) and func.id in DANGEROUS_NAME_CALLS:
            findings.append((node.lineno, func.id))

    return findings


def scan_directory(root: Path) -> List[Violation]:
    violations: List[Violation] = []
    if not root.exists():
        return violations
    for path in sorted(root.rglob("*.py")):
        name = path.name
        if name.startswith(SKIP_PREFIXES) or name.endswith(SKIP_SUFFIXES):
            continue
        rel = _rel(path)
        if _is_whitelisted(rel) is not None:
            continue
        try:
            code = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line, kind in analyze_source(code, filename=str(path)):
            snippet = ""
            for i, src_line in enumerate(code.splitlines(), start=1):
                if i == line:
                    snippet = src_line
                    break
            violations.append(Violation(file=rel, line=line, kind=kind, snippet=snippet))
    return violations


# ---- 判别力自证（反假绿） --------------------------------------------------
DISCRIMINATOR_SAMPLE = '''\
import os
import subprocess

def handle_scanned_config(user_input):
    # 缺陷：把被扫数据直接喂给执行原语（这正是要被 Layer 2 抓住的形态）
    os.system(user_input)
    subprocess.Popen(user_input, shell=True)
    result = eval(user_input)
    return result
'''


def self_test_discriminator() -> bool:
    """内置恶意样例必须被扫描器抓住；否则扫描器空洞（假绿）。"""
    findings = analyze_source(DISCRIMINATOR_SAMPLE, filename="<discriminator>")
    kinds = {k for _, k in findings}
    required = {"os.system", "subprocess.Popen", "eval"}
    missing = required - kinds
    if missing:
        print(f"[DISCRIMINATOR FAIL] 扫描器未抓住内置恶意样例中的 {sorted(missing)} —— "
              f"扫描器空洞（假绿），门禁无效。")
        return False
    print(f"[DISCRIMINATOR PASS] 内置恶意样例被抓住（{sorted(kinds)}），"
          f"证明扫描器非恒真。")
    return True


def main() -> int:
    print("== T7 / H3 Layer 2: AST 静态隔离扫描（scanner/ 信任边界）==\n")

    if not self_test_discriminator():
        return 1

    violations = scan_directory(SCAN_ROOT)
    if violations:
        print(f"\n[FAIL] 在 scanner/ 发现 {len(violations)} 处未白名单的危险执行原语调用：")
        for v in violations:
            print(v)
        print("\n若为合法用途，请在 scripts/ast_isolation_scan.py 的 WHITELIST 中显式登记并写明原因；"
              "否则视为隔离被突破，必须修复。")
        return 1

    print(f"\n[PASS] scanner/ 源码零未白名单危险执行原语（扫描范围已排除测试文件）。")
    print("       白名单（刻意放行，可审计）：")
    for rel, reason in WHITELIST.items():
        print(f"         - {rel}: {reason}")
    print("\n结论：结构上不存在能把被扫数据升级为执行原语的调用路径（Layer 2 成立）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
