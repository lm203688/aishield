"""T7 / H3 Layer 2 AST 静态隔离扫描门禁的回归测试。

确保：
  1) scanner/ 真实源码零未白名单危险执行原语（隔离不变量在结构层成立）。
  2) 扫描器非恒真：内置/合成恶意样例必须被抓住（防假绿）。
  3) 安全样例不产生误报（防过严导致合法代码无法提交）。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.ast_isolation_scan import (
    SCAN_ROOT,
    analyze_source,
    scan_directory,
    self_test_discriminator,
)


def test_scanner_directory_clean():
    violations = scan_directory(SCAN_ROOT)
    assert violations == [], (
        f"scanner/ 发现 {len(violations)} 处未白名单危险执行原语：\n"
        + "\n".join(str(v) for v in violations)
    )


def test_discriminator_catches_hostile_sample():
    # 与脚本内置判别力自证一致：扫描器自身必须能抓住恶意样例。
    assert self_test_discriminator() is True


def test_analyzer_flags_hostile_source():
    hostile = (
        "import os\n"
        "import subprocess\n"
        "def f(x):\n"
        "    os.system(x)\n"
        "    subprocess.Popen(x, shell=True)\n"
        "    return eval(x)\n"
    )
    findings = analyze_source(hostile, filename="<hostile>")
    kinds = {k for _, k in findings}
    assert {"os.system", "subprocess.Popen", "eval"}.issubset(kinds)


def test_analyzer_ignores_detection_signatures():
    # 扫描引擎用字符串/正则「检测」这些原语，不应被误报为真实调用。
    safe = (
        "PATTERNS = [r'os\\.system\\s*\\(', r'eval\\(', 'subprocess']\n"
        "def analyze(text):\n"
        "    return [p for p in PATTERNS if p in text]\n"
    )
    findings = analyze_source(safe, filename="<safe>")
    assert findings == [], f"检测签名被误报：{findings}"


def test_analyzer_whitelist_sandbox():
    # sandbox.py 即使含 subprocess.Popen 也应被白名单放行（在 scan_directory 层面）。
    from scripts.ast_isolation_scan import _is_whitelisted
    assert _is_whitelisted("sandbox.py") is not None
    assert _is_whitelisted("integrations/bb_browser.py") is not None
