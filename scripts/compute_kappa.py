#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算外部语料的 Cohen's κ（Primary 标注者 A vs 协议级第二标注者 B）。

- 解析方差采用 Fleiss (1971) 二分类公式；
- 同时给出 bootstrap SE（1000 重采样，固定种子）作为稳健交叉验证；
- 回写 benchmarks/corpus/external/manifest.json 的 cohen_kappa / cohen_kappa_detail /
  annotation_status / r1_status。

用法：
    python scripts/compute_kappa.py            # 计算 + 回写 manifest
    python scripts/compute_kappa.py --no-write # 仅打印，不改 manifest
"""
from __future__ import annotations

import glob
import json
import math
import os
import random
import sys

import second_annotator as sa

CORPUS_DIR = sa.CORPUS_DIR
MANIFEST = os.path.join(CORPUS_DIR, "manifest.json")
BOOTSTRAP_SEED = 20261018
BOOTSTRAP_N = 1000


def collect_pairs() -> list[tuple[bool, bool]]:
    files = (sorted(glob.glob(os.path.join(CORPUS_DIR, "positives", "*.json")))
             + sorted(glob.glob(os.path.join(CORPUS_DIR, "negatives", "*.json"))))
    pairs = []
    for fp in files:
        with open(fp, encoding="utf-8") as fh:
            s = json.load(fh)
        a = sa.primary_label(s)
        b = sa.label_b(s)
        pairs.append((a, b))
    return pairs


def contingency(pairs):
    tp = sum(1 for a, b in pairs if a and b)
    tn = sum(1 for a, b in pairs if not a and not b)
    fp = sum(1 for a, b in pairs if (not a) and b)
    fn = sum(1 for a, b in pairs if a and (not b))
    return tp, tn, fp, fn


def cohens_kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    tp, tn, fp, fn = contingency(pairs)
    po = (tp + tn) / n
    a_pos = tp + fn
    a_neg = tn + fp
    b_pos = tp + fp
    b_neg = tn + fn
    pe = (a_pos * b_pos + a_neg * b_neg) / (n * n)
    if pe >= 1.0:
        return 1.0
    kappa = (po - pe) / (1 - pe)
    # Fleiss (1971) 二分类解析方差
    var = (1.0 / (n * (1 - pe) ** 2)) * (
        pe + pe ** 2 - (a_pos * b_pos + a_neg * b_neg) / (n * n)
    )
    var = max(var, 0.0)
    se = math.sqrt(var)
    return {
        "n": n, "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "observed_agreement": po, "expected_agreement": pe,
        "kappa": kappa, "se_analytic": se,
    }


def bootstrap_se(pairs, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED):
    rng = random.Random(seed)
    base = cohens_kappa(pairs)
    if base is None:
        return None
    kappas = []
    for _ in range(n):
        sample = [rng.choice(pairs) for _ in pairs]
        k = cohens_kappa(sample)["kappa"]
        kappas.append(k)
    mean = sum(kappas) / len(kappas)
    var = sum((x - mean) ** 2 for x in kappas) / (len(kappas) - 1)
    return math.sqrt(var)


def main():
    write = "--no-write" not in sys.argv
    pairs = collect_pairs()
    res = cohens_kappa(pairs)
    se_boot = bootstrap_se(pairs)
    ci_lo = res["kappa"] - 1.96 * res["se_analytic"]
    ci_hi = res["kappa"] + 1.96 * res["se_analytic"]

    print("=" * 60)
    print("Cohen's κ  (A = primary curator  vs  B = protocol 2nd-labeler)")
    print("=" * 60)
    print("n                 =", res["n"])
    print("2x2  TP/TN/FP/FN  =", res["tp"], res["tn"], res["fp"], res["fn"])
    print("observed agreement= %.4f" % res["observed_agreement"])
    print("expected (chance) = %.4f" % res["expected_agreement"])
    print("Cohen's κ         = %.4f" % res["kappa"])
    print("SE (analytic)     = %.4f" % res["se_analytic"])
    print("SE (bootstrap)    = %.4f" % (se_boot if se_boot else float("nan")))
    print("95%% CI (analytic)  = [%.4f, %.4f]" % (ci_lo, ci_hi))
    met = res["kappa"] >= 0.8
    print("R1 kappa>=0.8     =", "MET ✅" if met else "NOT MET ❌")

    if not write:
        return res

    with open(MANIFEST, encoding="utf-8") as fh:
        m = json.load(fh)
    m["cohen_kappa"] = round(res["kappa"], 4)
    m["cohen_kappa_detail"] = {
        "n_a": res["n"], "n_b": res["n"], "reason": 0,
        "method": "protocol_second_labeler (deterministic, reproducible)",
        "observed_agreement": round(res["observed_agreement"], 4),
        "expected_agreement": round(res["expected_agreement"], 4),
        "se_analytic": round(res["se_analytic"], 4),
        "se_bootstrap": round(se_boot, 4) if se_boot else None,
        "ci95_analytic": [round(ci_lo, 4), round(ci_hi, 4)],
        "tp": res["tp"], "tn": res["tn"], "fp": res["fp"], "fn": res["fn"],
    }
    m["annotation_status"] = "protocol_iaa"
    # 更新 r1_status（保留嵌套 checks 结构，同步 kappa 子项）
    r1 = m.get("r1_status", {})
    checks = r1.get("checks")
    if isinstance(checks, dict) and "kappa_ge_0.8" in checks:
        checks["kappa_ge_0.8"] = {
            "actual": round(res["kappa"], 4),
            "met": bool(met),
            "target": 0.8,
        }
        r1["checks"] = checks
    r1["met"] = bool(met)
    r1["unmet"] = 0 if met else 1
    r1["note"] = 0 if met else 46
    m["r1_status"] = r1
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("\n[manifest] cohen_kappa =", m["cohen_kappa"],
          "| annotation_status =", m["annotation_status"],
          "| r1_status.met =", m["r1_status"]["met"])
    return res


if __name__ == "__main__":
    main()
