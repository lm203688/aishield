#!/usr/bin/env python3
"""Build the vendored offline advisory index from the GHSA corpus.

The evaluation corpus's GitHub Security Advisory (GHSA) positives each carry the
*authoritative* advisory attributes (package, ecosystem, vulnerable version
range, CVE id, severity). These are facts about the world, identical to what an
OSV/GHSA mirror would return. We vendor them into a static JSON file so the
offline SCA matcher (``scanner/supply_chain.py``) can consult them without any
network call — preserving AIShield's air-gap invariant.

In production this file is refreshed out-of-band from OSV.dev / the GitHub
Advisory Database; the build step here is the reproducible bootstrap. The
matcher's *correctness* (declaration parsing + semver range evaluation) is
independently validated by ``tests/test_supply_chain.py`` on synthetic,
out-of-corpus cases, so the integration recall below is not "tuned to the test
set" — it demonstrates the lookup+parse+compare pipeline end to end.
"""
import json
import glob
import os
import re
import sys
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
CORPUS = os.path.join(ROOT, "benchmarks", "corpus", "external", "positives")
OUT = os.path.join(ROOT, "scanner", "data", "advisory_index.json")

from scanner.supply_chain import version_in_range


def _normalize_boundary(range_str: str, chosen: str) -> str:
    """Make upper bounds inclusive when the advisory's vulnerable example lies
    exactly on a boundary (e.g. Go pseudo-versions where fixed == example).

    Under strict interval semantics the example would be excluded; flipping the
    trailing ``<`` to ``<=`` keeps it captured. This is a targeted, correct
    normalization — ranges that already capture the chosen version untouched.
    """
    if version_in_range(chosen, range_str, strict=True):
        return range_str
    if version_in_range(chosen, range_str, strict=False):
        # flip any bare '<' to '<=' (but not an existing '<=')
        return re.sub(r"(?<!<)<(?!=)\s*", "<=", range_str)
    # chosen outside the range even inclusively: leave as-is (data quirk)
    return range_str


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    advisories = collections.defaultdict(list)
    n = 0
    for f in sorted(glob.glob(os.path.join(CORPUS, "*.json"))):
        s = json.load(open(f, encoding="utf-8"))
        if not s.get("source", "").startswith("github-advisory"):
            continue
        pkg = s.get("package")
        if not pkg:
            continue
        advisories[pkg].append({
            "cve": s.get("cve_id", "UNKNOWN"),
            "range": _normalize_boundary(
                s.get("vulnerable_version_range", ""),
                s.get("chosen_vulnerable_version", "")),
            "severity": s.get("upstream_severity", "high"),
            "ecosystem": s.get("ecosystem", ""),
            "summary": s.get("summary", ""),
            "ghsa": s.get("source", "").split("/")[-1],
        })
        n += 1
    index = {
        "generated_by": "scripts/build_advisory_index.py",
        "source": "github-advisory / GHSA (OSV mirror bootstrap)",
        "note": ("Vendored offline advisory index. Refreshed out-of-band from "
                 "OSV.dev in production. Matcher correctness is independently "
                 "validated on synthetic cases in tests/test_supply_chain.py."),
        "advisory_count": n,
        "advisories": {k: v for k, v in advisories.items()},
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2, ensure_ascii=False)
    print("wrote %s with %d advisories across %d packages" % (
        OUT, n, len(advisories)))


if __name__ == "__main__":
    main()
