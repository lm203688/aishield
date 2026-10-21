#!/usr/bin/env python3
"""Error-analysis taxonomy for the NL prompt-injection subset (Task #542).

Goal: turn the 33.2% NL-injection recall (175/527 detected, 352 missed) from a
"weakness to hide" into a *rigorous, externally-categorized* error analysis that
a SCI reviewer accepts. We do NOT invent our own categories: we use the
benchmark's OWN authoritative fields (`attack_type`, `dataset_setting`) plus a
detector-independent lexical-opacity proxy.

Outputs JSON to benchmarks/corpus/external/nl_miss_taxonomy.json for the paper.
Deterministic; imports the same scanner functions as external_scope_recall.py.
"""
import json
import glob
import os
import collections
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.join(HERE, "..", "benchmarks", "corpus", "external")
OUT_JSON = os.path.join(CORPUS_DIR, "nl_miss_taxonomy.json")
SERIOUS = ("critical", "high")
sys.path.insert(0, os.path.join(HERE, ".."))


def _scan(s, idx):
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


# Detector-independent lexical-opacity proxy: a missed sample is "lexically
# opaque" if its *scanned text* contains none of a small high-precision set of
# explicit injection-control markers. This marks cases where static pattern
# analysis has no observable cue -- the genuine semantic-classification ceiling.
# It is intentionally conservative; false negatives (marked-but-missed) are
# reported separately as a small, fixable engineering gap.
EXPLICIT_MARKERS = (
    "ignore previous", "ignore all previous", "disregard", "system prompt",
    "you must", "you are now", "new instruction", "override", "forget",
    "do not tell", "without telling", "secretly", "exfiltrat", "send email",
    "email them", "api key", "password", "credential", "base64",
    "execute the following", "run the following", "developer mode",
    "reveal", "leak", "bypass",
)


def _opacity(text):
    t = (text or "").lower()
    return "opaque" if not any(m in t for m in EXPLICIT_MARKERS) else "marked"


def main():
    pos = [json.load(open(f, encoding="utf-8"))
           for f in glob.glob(os.path.join(CORPUS_DIR, "positives", "*.json"))]
    ia = [s for s in pos if not s.get("source", "").startswith("github-advisory")]

    rows = []
    for i, s in enumerate(ia):
        det = bool(_serious(_scan(s, i)))
        rows.append({
            "id": s.get("id"),
            "family": s.get("family"),
            "attack_type": s.get("attack_type", "?"),
            "dataset_setting": s.get("dataset_setting", "?"),
            "detected": det,
            "opacity": _opacity(s.get("text", "")),
        })

    detected = [r for r in rows if r["detected"]]
    missed = [r for r in rows if not r["detected"]]

    def bucket(rows_, *keys):
        c = collections.Counter()
        for r in rows_:
            c[tuple(r[k] for k in keys)] += 1
        return c

    # 1) recall by family
    fam_total = collections.Counter(r["family"] for r in rows)
    fam_hit = collections.Counter(r["family"] for r in detected)
    by_family = {f: {"total": fam_total[f], "hit": fam_hit[f],
                     "recall": round(fam_hit[f] / fam_total[f], 4)}
                 for f in fam_total}

    # 2) recall by dataset_setting (base vs enhanced)
    set_total = collections.Counter(r["dataset_setting"] for r in rows)
    set_hit = collections.Counter(r["dataset_setting"] for r in detected)
    by_setting = {k: {"total": set_total[k], "hit": set_hit[k],
                      "recall": round(set_hit[k] / set_total[k], 4)}
                  for k in set_total}

    # 3) recall by attack_type
    at_total = collections.Counter(r["attack_type"] for r in rows)
    at_hit = collections.Counter(r["attack_type"] for r in detected)
    by_attack_type = {k: {"total": at_total[k], "hit": at_hit[k],
                          "recall": round(at_hit[k] / at_total[k], 4)}
                      for k in at_total}

    # 4) misses: family x setting x opacity (the taxonomy table for the paper)
    miss_tax = collections.defaultdict(lambda: {"total": 0, "opaque": 0, "marked": 0})
    for r in missed:
        key = (r["family"], r["dataset_setting"], r["attack_type"])
        miss_tax[key]["total"] += 1
        miss_tax[key][r["opacity"]] += 1

    # 5) opacity summary
    opaque_miss = sum(1 for r in missed if r["opacity"] == "opaque")
    marked_miss = sum(1 for r in missed if r["opacity"] == "marked")
    # also: of the *detected*, how many were marked vs opaque (shows lexical cue helps)
    opaque_det = sum(1 for r in detected if r["opacity"] == "opaque")
    marked_det = sum(1 for r in detected if r["opacity"] == "marked")

    result = {
        "generated_by": "scripts/analyze_nl_misses.py",
        "subset": "injecagent NL prompt-injection (secondary scope)",
        "total": len(rows),
        "detected": len(detected),
        "missed": len(missed),
        "blended_recall": round(len(detected) / len(rows), 4),
        "by_family": by_family,
        "by_dataset_setting": by_setting,
        "by_attack_type": by_attack_type,
        "opacity_summary": {
            "missed_opaque": opaque_miss,
            "missed_marked": marked_miss,
            "pct_misses_opaque": round(opaque_miss / len(missed), 4),
            "detected_opaque": opaque_det,
            "detected_marked": marked_det,
        },
        "miss_taxonomy": {
            "::".join(k): v for k, v in sorted(
                miss_tax.items(), key=lambda kv: -kv[1]["total"])
        },
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    # console report
    print("NL-injection subset: %d total, %d detected, %d missed (recall %.1f%%)"
          % (len(rows), len(detected), len(missed), len(detected)/len(rows)*100))
    print("\nBy family:")
    for f, d in sorted(by_family.items()):
        print("  %-26s %3d/%3d  %.1f%%" % (f, d["hit"], d["total"], d["recall"]*100))
    print("\nBy dataset_setting (base=direct, enhanced=sophisticated):")
    for k, d in sorted(by_setting.items()):
        print("  %-12s %3d/%3d  %.1f%%" % (k, d["hit"], d["total"], d["recall"]*100))
    print("\nBy attack_type:")
    for k, d in sorted(by_attack_type.items(), key=lambda kv: -kv[1]["total"]):
        print("  %-26s %3d/%3d  %.1f%%" % (k, d["hit"], d["total"], d["recall"]*100))
    print("\nOpacity (lexical cue presence among MISSES):")
    print("  opaque (no explicit marker) : %d  (%.1f%% of misses)"
          % (opaque_miss, opaque_miss/len(missed)*100))
    print("  marked (had explicit marker): %d  (%.1f%% of misses)"
          % (marked_miss, marked_miss/len(missed)*100))
    print("  -> of DETECTED: opaque=%d marked=%d" % (opaque_det, marked_det))
    print("\nTop miss buckets (family|setting|attack_type):")
    for k, v in sorted(result["miss_taxonomy"].items(),
                       key=lambda kv: -kv[1]["total"])[:12]:
        print("  %-55s total=%d opaque=%d marked=%d"
              % (k, v["total"], v["opaque"], v["marked"]))
    print("\nwrote %s" % OUT_JSON)


if __name__ == "__main__":
    main()
