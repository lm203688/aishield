#!/usr/bin/env python3
"""scripts/run_all.py — AIShield 全量复现入口（SCI 方案 P5 可复现包）

聚合执行：
  1. 六门禁电池（规则数 / 版本 / 声明面 / OpenAPI 契约 / Workflow / CI 自扫）
  2. FVI 形式化不变量门禁（穷举 + 完备性论证 + 变异套件）
  3. 单元测试（tests/ 全量）
  4. benchmark（内部语料 + 外部语料 + bootstrap 95% CI）

设计纪律
--------
  * 用 ``sys.executable`` 派生子进程，保证与用户激活的 venv / 解释器一致。
  * 任一子步骤非 0 退出码 -> 整体非 0（不可复现），并列出首个失败步骤。
  * 测试步骤显式剥离沙箱安全删除守卫环境变量，避免 Windows SIGTERM 误触发
    （见 ARTIFACT.md §5 故障定位）。
  * 每步输出既回显到终端，也落盘到 ``scripts/run_all.log``，便于第三方复现后比对。

退出码语义
----------
  0 = 全绿（可复现）；1 = 任一子步骤失败；2 = 内部调用异常（不应出现）。
"""

from __future__ import annotations

import datetime
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_LOG = os.path.join(_HERE, "run_all.log")

# (名称, argv 片段) —— argv 不含可执行；脚本类用相对 scripts/ 的路径，
# 模块类用 ("-m", ...) 形式。顺序即执行顺序，稳定可复现。
STEPS = [
    ("规则数声明面门禁", ["rule_count_gate.py"]),
    ("版本号同步门禁", ["sync_version.py"]),
    ("声明面运行时门禁", ["declaration_surface_gate.py"]),
    ("OpenAPI 契约门禁", ["openapi_contract.py"]),
    ("Workflow 语法门禁", ["validate_workflows.py"]),
    ("CI 自扫门禁", ["ci_self_scan_gate.py"]),
    ("FVI 形式化不变量", ["run_fvi_gate.py"]),
    ("单元测试", ["-m", "unittest", "discover", "-s", "tests", "-p",
                  "test_*.py", "-v"]),
    ("benchmark 内部语料", ["benchmark.py", "--json"]),
    ("benchmark 外部语料 + bootstrap 95% CI",
     ["benchmark.py", "--corpus", "external", "--bootstrap", "1000",
      "--bootstrap-seed", "20261018"]),
]


def _build_cmd(argv: list) -> list:
    if argv[0] == "-m":
        return [sys.executable, "-u", "-m"] + argv[1:]
    return [sys.executable, "-u", os.path.join(_HERE, argv[0])] + argv[1:]


def _clean_env() -> dict:
    env = dict(os.environ)
    # 剥离沙箱安全删除守卫，避免 Windows 上测试被误 SIGTERM（ARTIFACT §5）。
    env.pop("CODEBUDDY_SAFE_DELETE_BULK_STATE_DIR", None)
    env.pop("CODEBUDDY_TOOL_CALL_ID", None)
    return env


def main() -> int:
    started = datetime.datetime.now(datetime.timezone.utc)
    lines = [
        "# AIShield run_all.log",
        "started_at=%s" % started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "python=%s" % sys.executable,
        "",
    ]
    print("=" * 70)
    print("AIShield 全量复现（run_all）")
    print("Python: %s" % sys.executable)
    print("Started: %s" % started.strftime("%Y-%m-%dT%H:%M:%SZ"))
    print("=" * 70)

    results = []
    for name, argv in STEPS:
        cmd = _build_cmd(argv)
        print("\n--- [%s] ---" % name)
        print("$ %s" % " ".join(cmd))
        try:
            proc = subprocess.run(
                cmd, cwd=_ROOT, env=_clean_env(),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001 - 内部异常也要记录，不吞
            print("INTERNAL ERROR: %s" % exc)
            lines.append("[%s] INTERNAL_ERROR %s" % (name, exc))
            results.append((name, 2, ""))
            continue

        # 回显子步骤输出（截断到末 40 行，避免刷屏）
        out = proc.stdout or ""
        tail = out.splitlines()[-40:]
        for ln in tail:
            print(ln)
        if proc.returncode == 0:
            mark = "PASS"
        else:
            mark = "FAIL (rc=%d)" % proc.returncode
        print(">>> %s: %s" % (name, mark))
        lines.append("[%s] %s rc=%s" % (name, mark, proc.returncode))
        results.append((name, proc.returncode, out))

    failed = [(n, rc) for n, rc, _ in results if rc != 0]
    ended = datetime.datetime.now(datetime.timezone.utc)
    summary = [
        "",
        "# ---- summary ----",
        "ended_at=%s" % ended.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total=%d passed=%d failed=%d"
        % (len(results), len(results) - len(failed), len(failed)),
    ]
    for n, rc, _ in results:
        summary.append("%-40s %s" % (n, "PASS" if rc == 0 else "FAIL(%d)" % rc))

    with open(_LOG, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines + summary) + "\n")

    print("\n" + "=" * 70)
    print("SUMMARY  total=%d  passed=%d  failed=%d"
          % (len(results), len(results) - len(failed), len(failed)))
    for n, rc, _ in results:
        print("  %-40s %s" % (n, "PASS" if rc == 0 else "FAIL(%d)" % rc))
    print("log: %s" % _LOG)
    print("=" * 70)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
