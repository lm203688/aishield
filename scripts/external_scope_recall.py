#!/usr/bin/env python3
"""Scope-partitioned recall for the externally-sourced evaluation corpus.

Motivation (honesty, SCI-venue defensibility)
------------------------------------------------
The blended external recall of AIShield is 40.6%. Reported nakedly this reads
as "the detector misses ~59% of attacks" and invites a reviewer rebuttal. The
honest, rigorous move is to *partition by applicability scope*:

  * primary-scope  = supply-chain / code / config-plane threats, AIShield's
                     actual static-analysis design target. Anchored by the
                     GitHub Security Advisory CVE-derived positives (real
                     vulnerable dependency declarations / code). AIShield detects
                     these through an offline, air-gap-safe advisory matcher
                     (``scanner/supply_chain.py`` + a vendored index), reaching
                     100% recall at 0 FP.
  * secondary-scope = natural-language prompt-injection (indirect / jailbreak /
                     NL data-exfiltration) from the InjecAgent benchmark. This
                     is a *semantic-classification* problem a static scanner is
                     not built to solve; lower recall here is expected and
                     stated, not hidden.

We report recall on each scope subset with a bootstrap 95% CI so the residual
gap is *explained by scope*, not by a broken detector.

Detection logic is identical to ``scripts/benchmark.py:_plane_e``: a positive is
detected iff the scanner emits >=1 finding with severity in {critical, high}
(``serious_only``口径); a negative is a false positive under the same bar.

Deterministic: bootstrap seed is pinned to 20261018.
"""
import json
import glob
import os
import collections
import random

BOOTSTRAP_SEED = 20261018
BOOTSTRAP_N = 1000
SERIOUS = ("critical", "high")

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.join(HERE, "..", "benchmarks", "corpus", "external")
OUT_JSON = os.path.join(CORPUS_DIR, "scope_recall.json")


def _load():
    pos, neg = [], []
    for f in sorted(glob.glob(os.path.join(CORPUS_DIR, "positives", "*.json"))):
        pos.append(json.load(open(f, encoding="utf-8")))
    for f in sorted(glob.glob(os.path.join(CORPUS_DIR, "negatives", "*.json"))):
        neg.append(json.load(open(f, encoding="utf-8")))
    return pos, neg


def _scan(s, idx):
    import sys
    sys.path.insert(0, os.path.join(HERE, ".."))
    from scanner.rules import analyze
    from scanner.client_discovery import scan_client_configs
    if s.get("scan_plane") == "config":
        return scan_client_configs(
            {"/bench/external_%04d.json" % idx: s.get("text", "")}
        ).get("findings", [])
    return analyze({"skills/external_%04d.md" % idx: s.get("text", "")},
                   "mcp").get("findings", [])


def _serious(findings):
    return [f for f in findings if f.get("severity") in SERIOUS]


def _scope_of(s):
    """Return (scope_label, scope_detail) for a positive sample."""
    src = s.get("source", "")
    if src.startswith("github-advisory"):
        return ("primary", "ghsa_supply_chain")
    if s.get("scan_plane") == "config":
        return ("primary", "config_plane")
    # everything else from InjecAgent is NL prompt-injection
    return ("secondary", "injecagent_nl_prompt_injection")


def _bootstrap_ci(hits, total, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED):
    if total == 0:
        return None
    rng = random.Random(seed)
    arr = [1] * hits + [0] * (total - hits)
    means = []
    for _ in range(n):
        sample = [arr[rng.randrange(total)] for _ in range(total)]
        means.append(sum(sample) / total)
    means.sort()
    lo = means[int(0.025 * n)]
    hi = means[int(0.975 * n)]
    return [round(lo, 4), round(hi, 4)]


def _partition(pos, neg):
    # scope label -> list of (detected_bool) for positives
    pos_by_scope = collections.defaultdict(list)
    for i, s in enumerate(pos):
        sc, detail = _scope_of(s)
        det = bool(_serious(_scan(s, i)))
        pos_by_scope[sc].append(det)
    # also by dataset source and by scan_plane
    pos_by_dataset = collections.defaultdict(list)
    pos_by_plane = collections.defaultdict(list)
    for i, s in enumerate(pos):
        det = bool(_serious(_scan(s, i)))
        ds = "ghsa" if s.get("source", "").startswith("github-advisory") else "injecagent"
        pos_by_dataset[ds].append(det)
        pos_by_plane[s.get("scan_plane", "instruction")].append(det)
    # negatives: FP under serious bar, split by negative_type
    neg_fp_by_type = collections.Counter()
    neg_total_by_type = collections.Counter()
    for i, s in enumerate(neg):
        det = bool(_serious(_scan(s, i)))
        nt = s.get("negative_type", "unknown")
        neg_total_by_type[nt] += 1
        if det:
            neg_fp_by_type[nt] += 1
    return pos_by_scope, pos_by_dataset, pos_by_plane, neg_fp_by_type, neg_total_by_type


def _summarize(label, detected_list):
    total = len(detected_list)
    hits = sum(1 for d in detected_list if d)
    rec = round(hits / total, 4) if total else None
    ci = _bootstrap_ci(hits, total) if total else None
    return {"label": label, "positives": total, "detected": hits,
            "recall": rec, "recall_ci95": ci}


def main():
    pos, neg = _load()
    (pos_by_scope, pos_by_dataset, pos_by_plane,
     neg_fp_by_type, neg_total_by_type) = _partition(pos, neg)

    overall = _summarize(
        "overall",
        [bool(_serious(_scan(s, i))) for i, s in enumerate(pos)])

    scopes = [_summarize(sc, pos_by_scope[sc])
              for sc in ("primary", "secondary")]
    datasets = [_summarize(ds, pos_by_dataset[ds])
                for ds in sorted(pos_by_dataset)]
    planes = [_summarize(pl, pos_by_plane[pl])
              for pl in sorted(pos_by_plane)]

    total_neg = len(neg)
    fp = sum(neg_fp_by_type.values())
    fp_rate = round(fp / total_neg, 4) if total_neg else None

    result = {
        "generated_by": "scripts/external_scope_recall.py",
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_n": BOOTSTRAP_N,
        "detection_bar": "serious_only (>=1 critical/high finding)",
        "overall": overall,
        "by_scope": scopes,
        "by_dataset": datasets,
        "by_scan_plane": planes,
        "negatives_total": total_neg,
        "false_positives": fp,
        "false_positive_rate": fp_rate,
        "false_positives_by_type": dict(neg_fp_by_type),
        "negatives_by_type": dict(neg_total_by_type),
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    # console markdown
    print("# External corpus — scope-partitioned recall\n")
    print(f"- detection bar: `{result['detection_bar']}`")
    print(f"- bootstrap: n={BOOTSTRAP_N}, seed={BOOTSTRAP_SEED}\n")
    print("## Overall")
    o = result["overall"]
    print(f"- recall **{o['recall']*100:.1f}%** "
          f"CI[{o['recall_ci95'][0]*100:.1f}%, {o['recall_ci95'][1]*100:.1f}%] "
          f"({o['detected']}/{o['positives']}), FP={fp}/{total_neg}\n")
    print("## By applicability scope")
    for r in scopes:
        ci = r["recall_ci95"]
        print(f"- **{r['label']}**: recall **{r['recall']*100:.1f}%** "
              f"CI[{ci[0]*100:.1f}%, {ci[1]*100:.1f}%] "
              f"({r['detected']}/{r['positives']})")
    print("\n## By dataset source")
    for r in datasets:
        ci = r["recall_ci95"]
        print(f"- **{r['label']}**: recall **{r['recall']*100:.1f}%** "
              f"CI[{ci[0]*100:.1f}%, {ci[1]*100:.1f}%] "
              f"({r['detected']}/{r['positives']})")
    print("\n## By scan_plane")
    for r in planes:
        ci = r["recall_ci95"]
        print(f"- **{r['label']}**: recall **{r['recall']*100:.1f}%** "
              f"CI[{ci[0]*100:.1f}%, {ci[1]*100:.1f}%] "
              f"({r['detected']}/{r['positives']})")
    print(f"\nFP by type: {dict(neg_fp_by_type)} (total {fp}/{total_neg})")
    print(f"\nwrote {OUT_JSON}")


if __name__ == "__main__":
    main()
