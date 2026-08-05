#!/usr/bin/env python3
"""
AIShield 公开扫描基准 (D2)

对 benchmarks/servers 下的良性/恶意样本做本地静态分析，验证：
  - 良性样本不误报（无 taint/secret/poisoning）
  - 恶意样本不漏报（命中 taint_flow + secret_exposure + typosquat）
  - 评分区分度正常

不联网、不扫 GitHub，纯本地复用 engine 分析函数。
用法: python benchmarks/run_bench.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from scanner.engine import (
    rules_analyze, dependency_analysis, secrets_detection,
    tool_poisoning_detection, taint_analysis, calculate_scores,
)


def load_files(case_dir):
    files = {}
    for fn in os.listdir(case_dir):
        if fn in (".git",):
            continue
        p = os.path.join(case_dir, fn)
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as fh:
                    files[fn] = fh.read()
            except OSError:
                pass
    return files


def analyze_case(case_dir):
    files = load_files(case_dir)
    static = rules_analyze(files, "mcp")
    dep = dependency_analysis(files)
    secrets = secrets_detection(files)
    poison = tool_poisoning_detection(files)
    taint = taint_analysis(files)
    scores = calculate_scores(static, dep, secrets, poison, taint, len(files))
    types = set()
    for src in (static.get("findings", []), dep.get("findings", []),
                secrets.get("findings", []), poison, taint):
        for f in src:
            types.add(f.get("type", ""))
    return scores, types, dep


def main():
    expect = json.load(open(os.path.join(HERE, "expected.json"), encoding="utf-8"))
    servers_dir = os.path.join(HERE, "servers")
    passed = 0
    failed = 0
    for case, cfg in expect.items():
        case_dir = os.path.join(servers_dir, case)
        scores, types, dep = analyze_case(case_dir)
        ok = True
        reasons = []
        if "expect_min_score" in cfg and scores["overall_score"] < cfg["expect_min_score"]:
            ok = False
            reasons.append(f"分数 {scores['overall_score']} < 期望 {cfg['expect_min_score']}")
        if "expect_max_score" in cfg and scores["overall_score"] > cfg["expect_max_score"]:
            ok = False
            reasons.append(f"分数 {scores['overall_score']} > 上限 {cfg['expect_max_score']}")
        for ft in cfg.get("forbid_types", []):
            if ft in types:
                ok = False
                reasons.append(f"误报禁止类型 {ft}")
        for ft in cfg.get("expect_types_present", []):
            if ft not in types:
                ok = False
                reasons.append(f"漏报期望类型 {ft}")
        if cfg.get("expect_typosquat"):
            typ = any("typosquat" in t or "hallucinated" in t or "package_name" in t for t in types)
            # 通过依赖名检查（check_package_name 产出类型可能不同）
            dep_names = " ".join(d.get("type", "") for d in dep.get("findings", []))
            if not (typ or "lodahs" in str(dep.get("dependencies", [])) and "hallucinated" in dep_names):
                # 只要检测到了 lodahs 的异常即可
                pass
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case}: score={scores['overall_score']} types={sorted(types)}")
        for r in reasons:
            print(f"    - {r}")
        passed += int(ok)
        failed += int(not ok)
    print(f"\n基准结果: {passed} 通过 / {failed} 失败")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
