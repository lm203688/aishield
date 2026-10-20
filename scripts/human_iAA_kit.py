#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人类双标工具包（Human Inter-Annotator Agreement Kit）。

为什么需要它
------------
`scripts/compute_lca.py` 产出的 κ = 0.867 是 **自动化标签一致性审计（LCA）**：
独立重推 vs 来源真值，衡量的是可复现性 / 自洽性，**不代表人类标注者间一致性**。
若投稿方要求 R1 风格的"≥2 名独立人类标注者、Cohen's κ≥0.8"，则本工具包是投前
必须执行的一步：它产出分层抽样样本、可供两名分析师独立标注的模板，并在标注回填后
计算**真实的**人类双标 κ，写回 manifest。

用法
----
  # 1) 生成待标注模板（分层抽样 ~110 条，确定性）
  python scripts/human_iAA_kit.py sample --out human_iAA_template.csv --n 110

  # 2) 两名独立分析师打开 CSV，在 annotator1 / annotator2 列各填
  #    true / false（或 1 / 0 / yes / no）。分歧处可填 adjudicated 列仲裁。
  #    （不依赖网络，纯本地。）

  # 3) 回填后重算真实人类 κ，写回 manifest
  python scripts/human_iAA_kit.py recompute --in human_iAA_template.csv

诚实约定
--------
- 本工具绝不自动"代填"人类标注；annotator 列留空即不参与 κ 计算。
- recompute 只接受人类回填的 CSV；未回填的行被跳过（不会伪造 100% 一致）。
- 真实人类 κ 才是 R1 的"标注者间一致性"证据；LCA κ 仍保留为自动化一致性补充。
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import random
import sys

CORPUS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "benchmarks", "corpus", "external",
)
MANIFEST = os.path.join(CORPUS_DIR, "manifest.json")
DEFAULT_N = 110
SEED = 20261018

_TRUTHY = {"true", "1", "yes", "y", "t", "positive", "pos"}
_FALSY = {"false", "0", "no", "n", "f", "negative", "neg"}


def _load_samples() -> list[dict]:
    out = []
    for side, d in (("positive", "positives"), ("negative", "negatives")):
        for fp in sorted(glob.glob(os.path.join(CORPUS_DIR, d, "*.json"))):
            with open(fp, encoding="utf-8") as fh:
                s = json.load(fh)
            out.append(s)
    return out


def _snippet(text: str, n: int = 200) -> str:
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)
    return " ".join(text.split())[:n]


def stratified_sample(n: int = DEFAULT_N, seed: int = SEED) -> list[dict]:
    """按 (side, family) 分层比例抽样，保证覆盖稀有族，确定性。"""
    samples = _load_samples()
    buckets: dict[tuple[str, str], list[dict]] = {}
    for s in samples:
        side = "positive" if (s.get("labels") and
                              any(l.get("annotator") == "A" and l.get("positive")
                                  for l in s.get("labels", []))) else "negative"
        fam = s.get("family", "?")
        buckets.setdefault((side, fam), []).append(s)

    rng = random.Random(seed)
    total = len(samples)
    chosen: list[dict] = []
    # 每族至少 1 条（若总数允许），其余按占比分配
    guaranteed = 0
    for key, items in buckets.items():
        if guaranteed >= n:
            break
        pick = items[0]
        chosen.append(pick)
        buckets[key] = [x for x in items if x is not pick]
        guaranteed += 1
    remaining = n - len(chosen)
    # 按剩余规模比例在未被保底抽走的池子里抽
    pool = [x for items in buckets.values() for x in items]
    if pool and remaining > 0:
        # 用分层权重：按原始占比加权随机
        weights = []
        for x in pool:
            side = "positive" if (x.get("labels") and
                                  any(l.get("annotator") == "A" and l.get("positive")
                                      for l in x.get("labels", []))) else "negative"
            fam = x.get("family", "?")
            # 权重 = 该 (side,fam) 桶在全集中的占比的倒数较小者，简单按 1/桶大小
            sz = max(1, len(buckets.get((side, fam), [x])))
            weights.append(1.0 / sz)
        extra = rng.choices(pool, weights=weights, k=min(remaining, len(pool)))
        # 去重（choices 可能重复）
        seen = {id(c) for c in chosen}
        for x in extra:
            if id(x) not in seen:
                chosen.append(x)
                seen.add(id(x))
    # 兜底：若仍不足 n，从全集补
    if len(chosen) < n:
        for s in samples:
            if s not in chosen:
                chosen.append(s)
                if len(chosen) >= n:
                    break
    rng.shuffle(chosen)
    return chosen[:n]


def emit_template(out_path: str, n: int = DEFAULT_N) -> int:
    samples = stratified_sample(n=n)
    cols = ["id", "source", "dataset", "family", "side",
            "text_snippet", "source_truth_A", "annotator1", "annotator2",
            "adjudicated", "notes"]
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for s in samples:
            side = "positive" if (s.get("labels") and
                                  any(l.get("annotator") == "A" and l.get("positive")
                                      for l in s.get("labels", []))) else "negative"
            truth = "true" if side == "positive" else "false"
            w.writerow([
                s.get("id", ""),
                s.get("source", ""),
                s.get("dataset", ""),
                s.get("family", ""),
                side,
                _snippet(s.get("text", "")),
                truth,
                "",  # annotator1 —— 人类填
                "",  # annotator2 —— 人类填
                "",  # adjudicated —— 分歧仲裁（可选）
                "",
            ])
    print("[human_iAA] wrote %d review rows -> %s" % (len(samples), out_path))
    print("[human_iAA] 两名独立分析师请在 annotator1 / annotator2 列各填 "
          "true/false；分歧可在 adjudicated 列仲裁。")
    return len(samples)


def _parse_cell(v: str):
    if v is None:
        return None
    v = str(v).strip().lower()
    if v in _TRUTHY:
        return True
    if v in _FALSY:
        return False
    return None


def recompute(in_path: str) -> dict:
    pairs = []
    skipped = 0
    with open(in_path, encoding="utf-8", newline="") as fh:
        r = csv.DictReader(fh)
        for row in r:
            a1 = _parse_cell(row.get("annotator1"))
            a2 = _parse_cell(row.get("annotator2"))
            if a1 is None or a2 is None:
                skipped += 1
                continue
            pairs.append((a1, a2))
    if not pairs:
        print("[human_iAA] ERROR: 没有可计算的 (annotator1, annotator2) 对；"
              "请先由人类回填。", file=sys.stderr)
        return {}
    n = len(pairs)
    tp = sum(1 for a, b in pairs if a and b)
    tn = sum(1 for a, b in pairs if not a and not b)
    fp = sum(1 for a, b in pairs if (not a) and b)
    fn = sum(1 for a, b in pairs if a and (not b))
    po = (tp + tn) / n
    a_pos, a_neg = tp + fn, tn + fp
    b_pos, b_neg = tp + fp, tn + fn
    pe = (a_pos * b_pos + a_neg * b_neg) / (n * n)
    kappa = 1.0 if pe >= 1.0 else (po - pe) / (1 - pe)
    agree = (tp + tn) / n
    print("=" * 60)
    print("HUMAN Inter-Annotator Agreement (true dual annotation)")
    print("=" * 60)
    print("n (dual-filled rows) =", n, "| skipped (unfilled) =", skipped)
    print("2x2 TP/TN/FP/FN =", tp, tn, fp, fn)
    print("observed agreement = %.4f" % agree)
    print("Cohen's κ (human) = %.4f" % kappa)
    met = kappa >= 0.8
    print("human κ>=0.8 =", "MET ✅" if met else "NOT MET ❌")

    with open(MANIFEST, encoding="utf-8") as fh:
        m = json.load(fh)
    m["human_iAA_status"] = "done" if met else "done_below_threshold"
    m["human_iAA_kappa"] = round(kappa, 4)
    m["human_iAA_detail"] = {
        "n_dual_filled": n, "n_skipped_unfilled": skipped,
        "observed_agreement": round(agree, 4),
        "expected_agreement": round(pe, 4),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "method": "two independent human annotators + optional adjudication",
    }
    r1 = m.get("r1_status", {})
    checks = r1.get("checks") or {}
    checks["human_iaa_ge_0.8"] = {
        "actual": round(kappa, 4),
        "met": bool(met),
        "target": 0.8,
        "status": "done",
        "note": "genuine human inter-annotator agreement (two independent annotators)",
    }
    # 整体 R1：LCA + 人类双标 都达标才算完全闭环
    lca_ok = bool((checks.get("kappa_ge_0.8") or {}).get("met", False))
    r1["checks"] = checks
    r1["met"] = bool(lca_ok and met)
    r1["unmet"] = 0 if (lca_ok and met) else 1
    r1["note"] = 0 if (lca_ok and met) else 47
    m["r1_status"] = r1
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("\n[manifest] human_iAA_status =", m["human_iAA_status"],
          "| human_iAA_kappa =", m["human_iAA_kappa"],
          "| r1_status.met =", m["r1_status"]["met"])
    return {"kappa": kappa, "n": n, "met": met}


def main():
    ap = argparse.ArgumentParser(description="Human IAA kit")
    sub = ap.add_subparsers(dest="cmd")

    s = sub.add_parser("sample", help="生成分层抽样待标注模板 CSV")
    s.add_argument("--out", default="human_iAA_template.csv")
    s.add_argument("--n", type=int, default=DEFAULT_N)

    r = sub.add_parser("recompute", help="回填后重算真实人类 κ 并写回 manifest")
    r.add_argument("--in", dest="in_path", default="human_iAA_template.csv")

    args = ap.parse_args()
    if args.cmd == "sample":
        emit_template(args.out, n=args.n)
    elif args.cmd == "recompute":
        recompute(args.in_path)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
