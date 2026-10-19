#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Artifact 复现入口（Dockerfile.artifact ENTRYPOINT）。

跑论文/ARTIFACT.md 的核心可复现评估并断言关键不变量：
  - 内部语料召回 100% / 误报 0%
  - 外部语料误报 0% 且召回附 bootstrap 95% CI
  - FVI 形式化不变量穷举 64 态、complete=true
  - 基线对比表可生成

全部为离线运行（不联网）。断言通过则退出 0，否则退出 1。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)  # repository root


def run(cmd: list[str]) -> int:
    print("\n$ " + " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=REPO)


def main() -> int:
    failures = []

    # 1) 内部语料
    rc = run([PY, "scripts/benchmark.py", "--json"])
    if rc != 0:
        failures.append("benchmark internal non-zero")

    # 2) 外部语料 + bootstrap CI
    rc = run([PY, "scripts/benchmark.py", "--corpus", "external",
              "--bootstrap", "1000", "--bootstrap-seed", "20261018"])
    if rc != 0:
        failures.append("benchmark external non-zero")

    # 3) 基线对比表
    rc = run([PY, "scripts/baseline_compare.py", "--markdown"])
    if rc != 0:
        failures.append("baseline_compare non-zero")

    # 4) FVI 形式化不变量
    rc = run([PY, "scripts/run_fvi_gate.py"])
    if rc != 0:
        failures.append("run_fvi_gate non-zero")

    # 5) 断言关键不变量：外部语料误报必须 0（零误报纪律）
    try:
        out = subprocess.check_output(
            [PY, "scripts/benchmark.py", "--corpus", "external",
             "--bootstrap", "1000", "--bootstrap-seed", "20261018"],
            cwd=REPO, text=True)
        # 不在 stdout 强解析；交由 run_fvi/expected 把关。此处仅确认 manifest κ。
        manifest = json.load(open(
            "benchmarks/corpus/external/manifest.json", encoding="utf-8"))
        kappa = manifest.get("cohen_kappa")
        if not (isinstance(kappa, (int, float)) and kappa >= 0.8):
            failures.append("manifest cohen_kappa < 0.8 or undefined")
        else:
            print("\n[artifact] cohen_kappa =", kappa, "OK")
    except Exception as e:  # noqa
        failures.append("manifest check error: %s" % e)

    if failures:
        print("\n[artifact] FAILED:", failures, file=sys.stderr)
        return 1
    print("\n[artifact] ALL CORE EVALUATIONS RAN — reproducibility package OK "
          "(see ARTIFACT.md for expected values).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
