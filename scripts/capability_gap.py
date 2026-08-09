#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield · Capability Gap Analyser  (the "adopt" half of the Tech Radar)
========================================================================

The Tech Radar has two halves:

  defend  -- an ATTACK appears in the ecosystem  ->  draft a detection rule
             (implemented in scripts/tech_radar.py :: draft_rule_candidate)

  adopt   -- a DEFENCE appears in the ecosystem  ->  do we already have it?
             (implemented here)

Without the adopt half the radar only tells us what to be afraid of, never
what to build. Papers such as "DreamGuard: Runtime Guardrail for LLM Agents"
or "Zero-Trust MCP Enforcement Architecture" are not threats -- they are
capabilities our competitors will ship before we do unless we notice.

How it works
------------
1. CAPABILITY_CATALOG declares what AIShield already does, each entry tying a
   capability to the keywords that describe it AND to the file that implements
   it. The file-existence check is enforced by `verify_catalog()` so the
   catalog cannot silently rot as the codebase changes.
2. Every radar signal is matched against DEFENCE_PATTERNS to decide whether it
   describes a defensive capability at all.
3. A defensive signal is then matched against the catalog:
     - keyword overlap  -> COVERED  (we have it; note it for benchmarking)
     - no overlap       -> GAP      (adopt candidate, ranked by evidence)

Zero third-party dependencies -- stdlib only, matching the project rule.

Usage:
  python scripts/capability_gap.py                 # self-check the catalog
  python scripts/capability_gap.py --report        # print catalog as markdown
"""
from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# What AIShield already does.
#   name      : human-readable capability
#   keywords  : terms that, if present in a signal, mean "this is that thing"
#   impl      : repo-relative file proving the capability exists
# ---------------------------------------------------------------------------
CAPABILITY_CATALOG = [
    {
        "name": "Static rule engine (MCP + Agentic dual axis)",
        "keywords": ["static analysis", "rule engine", "sast", "config scan",
                     "manifest scan", "detection rule"],
        "impl": "scanner/rules.py",
    },
    {
        "name": "Risk scoring & explainability",
        "keywords": ["risk score", "scoring", "explainab", "score breakdown",
                     "severity model"],
        "impl": "scanner/engine.py",
    },
    {
        "name": "SBOM generation (CycloneDX) + SARIF export",
        "keywords": ["sbom", "cyclonedx", "sarif", "bill of materials",
                     "provenance manifest"],
        "impl": "scanner/sbom.py",
    },
    {
        "name": "Known-CVE correlation (OSV.dev)",
        "keywords": ["cve", "vulnerability database", "osv", "known vulnerab"],
        "impl": "scanner/osv.py",
    },
    {
        "name": "Attack path analysis (minimal removal set)",
        "keywords": ["attack path", "attack graph", "kill chain",
                     "exploit chain", "reachability"],
        "impl": "scanner/attack_path.py",
    },
    {
        "name": "Policy-as-code gating",
        "keywords": ["policy as code", "policy engine", "opa", "admission control",
                     "policy enforcement"],
        "impl": "scanner/policy.py",
    },
    {
        "name": "Read-only live probe (never spawns scanned config)",
        "keywords": ["dynamic analysis", "live probe", "runtime inspection",
                     "sandbox execution", "dynamic scan"],
        "impl": "scanner/live_probe.py",
    },
    {
        "name": "Rug-pull / version drift detection",
        "keywords": ["rug pull", "version drift", "silent update", "tool mutation",
                     "post-approval change"],
        "impl": "scanner/rug_pull.py",
    },
    {
        "name": "Continuous monitoring of registered servers",
        "keywords": ["continuous monitoring", "drift detection", "watch",
                     "periodic rescan"],
        "impl": "scanner/monitor.py",
    },
    {
        "name": "Fleet-wide posture aggregation",
        "keywords": ["fleet", "multi-server", "posture dashboard", "estate",
                     "inventory"],
        "impl": "scanner/fleet.py",
    },
    {
        "name": "Registry / client discovery",
        "keywords": ["registry", "discovery", "catalog crawl", "server index"],
        "impl": "scanner/registry_discovery.py",
    },
    {
        "name": "Runtime governance kill switch + hash-chained audit log",
        "keywords": ["kill switch", "circuit breaker", "runtime guardrail",
                     "runtime enforcement", "tamper-evident", "audit log",
                     "hash chain", "append-only log", "runtime governance",
                     "zero-trust enforcement"],
        "impl": "eco/runtime_governance.py",
    },
    {
        "name": "Continuous attestation subscription (recurring re-verify)",
        "keywords": ["attestation", "continuous verification", "certification",
                     "re-certification", "trust decay", "revocation"],
        "impl": "eco/attestation.py",
    },
    {
        "name": "Trust badge / certification issuance",
        "keywords": ["badge", "trust mark", "certification authority",
                     "seal of approval", "verified publisher"],
        "impl": "eco/badge.py",
    },
    {
        "name": "Agent-to-agent payment rail (x402) + CNY rail",
        "keywords": ["x402", "agent payment", "machine payable", "micropayment",
                     "402 payment required"],
        "impl": "eco/x402.py",
    },
    {
        "name": "Spend cap (fail-closed budget enforcement)",
        "keywords": ["spend cap", "budget", "rate limit spend", "cost control",
                     "financial guardrail"],
        "impl": "eco/spend_cap.py",
    },
    {
        "name": "Agent identity & signing",
        "keywords": ["agent identity", "did", "signing", "signature verification",
                     "keystore", "provenance signature", "code signing"],
        "impl": "eco/identity.py",
    },
    {
        "name": "Sandboxed execution boundary",
        "keywords": ["sandbox", "isolation", "container escape", "seccomp",
                     "capability confinement"],
        "impl": "eco/sandbox.py",
    },
    {
        "name": "A2A protocol gateway",
        "keywords": ["a2a", "agent2agent", "agent card", "inter-agent protocol"],
        "impl": "eco/a2a_gateway.py",
    },
    {
        "name": "Observability / telemetry",
        "keywords": ["telemetry", "observability", "tracing", "otel", "metrics"],
        "impl": "scanner/telemetry.py",
    },
    {
        "name": "LLM-assisted semantic analysis (optional backend)",
        "keywords": ["llm judge", "semantic analysis", "model-based detection",
                     "llm-as-a-judge", "semantic audit"],
        "impl": "scanner/llm_analyzer.py",
    },
]


# ---------------------------------------------------------------------------
# Does a signal describe a DEFENSIVE capability (as opposed to an attack)?
# ---------------------------------------------------------------------------
# STRONG: unambiguously about defending/securing something. At least one of
# these must be present -- otherwise a finance benchmark that happens to say
# "audit" would be filed as a security capability we are missing.
DEFENCE_STRONG = [
    r"\bdefen[cs]e?\b", r"\bdefend\w*", r"\bguard(rail|ing)?\b", r"\bshield\w*",
    r"\bmitigat\w+", r"\bsafeguard\w*", r"\bsecurity\b", r"\bsecuring\b",
    r"\bcertif\w+", r"\battestation\b", r"\bsanitiz\w+", r"\bsandbox\w*",
    r"\bzero[- ]trust\b", r"\bprovenance\b", r"\bthreat\w*", r"\bvulnerab\w+",
    r"\bmalicious\b", r"\battack\w*", r"\bexploit\w*", r"\bpoison\w*",
    r"\binjection\b", r"\bjailbreak\w*", r"\bbackdoor\w*", r"\btrustworth\w+",
    r"\bred[- ]team\w*", r"\badversarial\b", r"\brisk\b", r"\bsafety\b",
    r"\benforcement\b", r"\baccess control\b", r"\bprivacy\b",
]
_DEFENCE_STRONG_RE = re.compile("|".join(DEFENCE_STRONG), re.I)

# WEAK: consistent with a capability but far too generic on their own.
DEFENCE_WEAK = [
    r"\bframework\b", r"\btoolkit\b", r"\bscanner\b", r"\baudit\w*",
    r"\bbenchmark\b", r"\bevaluat\w+", r"\bmonitor\w*", r"\bdetect\w+",
    r"\bverif\w+", r"\bisolat\w+", r"\bprotect\w+", r"\benforce\w*",
]
_DEFENCE_WEAK_RE = re.compile("|".join(DEFENCE_WEAK), re.I)

# Signals must also be about our domain, else every security paper matches.
DOMAIN_PATTERNS = [
    r"\bagent\w*", r"\bllm\b", r"\bmcp\b", r"model context protocol",
    r"\btool[- ]use\b", r"\bprompt\b", r"language model", r"\bskill\b",
]
_DOMAIN_RE = re.compile("|".join(DOMAIN_PATTERNS), re.I)

# Domains adjacent to ours but out of scope -- their "security" papers are not
# capabilities AIShield should adopt.
OUT_OF_SCOPE = [
    r"\bverilog\b", r"\bhardware design\b", r"\bchiplet\w*", r"\brtl\b",
    r"\bfinancial workflow\w*", r"\binvestment\b", r"\bportfolio\b",
    r"\bsocial inference\b", r"\bsurvey[- ]country\b", r"\bmedical imaging\b",
    r"\bautonomous driving\b", r"\bvision transformer\b", r"\bwireless\b",
    r"\bfederated learning\b", r"\brecommendation system\b",
]
_OUT_OF_SCOPE_RE = re.compile("|".join(OUT_OF_SCOPE), re.I)


def is_defensive(sig) -> bool:
    """True if the signal describes a defensive capability in our domain.

    Requires: (strong security term) AND (agent/LLM domain term) AND
    (not an out-of-scope vertical). The strong/weak split exists because words
    like "audit" and "benchmark" appear in papers that have nothing to do with
    agent security -- matching on those alone floods the adopt list with noise.
    """
    text = " ".join(str(v) for v in sig.values() if isinstance(v, str))
    if _OUT_OF_SCOPE_RE.search(text):
        return False
    if not _DOMAIN_RE.search(text):
        return False
    return bool(_DEFENCE_STRONG_RE.search(text))


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------
def match_capability(sig):
    """Return (capability_entry, matched_keywords) or (None, [])."""
    text = " ".join(str(v) for v in sig.values() if isinstance(v, str)).lower()
    best, best_hits = None, []
    for cap in CAPABILITY_CATALOG:
        hits = [k for k in cap["keywords"] if k in text]
        if len(hits) > len(best_hits):
            best, best_hits = cap, hits
    return (best, best_hits) if best_hits else (None, [])


def _gap_topic(sig):
    """Best-effort short label for what an uncovered signal is about."""
    title = (sig.get("title") or "").strip()
    # Papers usually read "NAME: the actual description"
    if ":" in title:
        head, tail = title.split(":", 1)
        if len(head) <= 24 and tail.strip():
            return tail.strip()[:110]
    return title[:110]


def analyse(signals):
    """Split signals into covered capabilities and adoption gaps.

    Returns {"covered": [...], "gaps": [...]}, each item a dict ready for
    report rendering. Gaps are ranked by evidence strength (stars / points
    first, then arXiv papers) so the top of the list is worth acting on.
    """
    covered, gaps = [], []
    seen_titles = set()

    for sig in signals:
        if "id" not in sig or not is_defensive(sig):
            continue
        title = (sig.get("title") or "").strip()
        key = title.lower()
        if not title or key in seen_titles:
            continue
        seen_titles.add(key)

        cap, hits = match_capability(sig)
        row = {
            "title": title,
            "url": sig.get("url", ""),
            "source": sig.get("_source", "?"),
            "weight": sig.get("stars") or sig.get("points") or sig.get("score") or 0,
        }
        if cap:
            row["capability"] = cap["name"]
            row["matched"] = hits
            covered.append(row)
        else:
            row["topic"] = _gap_topic(sig)
            gaps.append(row)

    covered.sort(key=lambda r: -r["weight"])
    gaps.sort(key=lambda r: -r["weight"])
    return {"covered": covered, "gaps": gaps}


# ---------------------------------------------------------------------------
# Report rendering (consumed by tech_radar.render_report)
# ---------------------------------------------------------------------------
def render_section(result, max_gaps=12, max_covered=8):
    covered, gaps = result["covered"], result["gaps"]
    if not covered and not gaps:
        return []

    lines = ["## 🚀 Adopt line — capability gap analysis", ""]
    lines.append(
        "Defensive techniques spotted in the ecosystem, checked against what "
        "AIShield already ships. **Gaps are candidate R&D items.**"
    )
    lines.append("")

    if gaps:
        lines.append(f"### ❗ Adoption gaps ({len(gaps)}) — not covered by any current capability")
        lines.append("")
        for g in gaps[:max_gaps]:
            w = f" · ⭐/▲ {g['weight']}" if g["weight"] else ""
            lines.append(f"- **{g['topic']}**  \n  [{g['title'][:90]}]({g['url']}) "
                         f"`{g['source']}`{w}")
        if len(gaps) > max_gaps:
            lines.append(f"- _...and {len(gaps) - max_gaps} more_")
        lines.append("")

    if covered:
        lines.append(f"### ✅ Already covered ({len(covered)}) — useful for benchmarking")
        lines.append("")
        for c in covered[:max_covered]:
            lines.append(f"- {c['capability']}  ←  [{c['title'][:70]}]({c['url']}) "
                         f"(matched: {', '.join(c['matched'][:3])})")
        if len(covered) > max_covered:
            lines.append(f"- _...and {len(covered) - max_covered} more_")
        lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Catalog self-check -- prevents the catalog from silently rotting
# ---------------------------------------------------------------------------
def verify_catalog():
    """Return list of problems. Empty list == catalog healthy."""
    problems = []
    seen_names = set()
    for cap in CAPABILITY_CATALOG:
        name = cap.get("name", "")
        if not name:
            problems.append("entry with empty name")
            continue
        if name in seen_names:
            problems.append(f"duplicate capability name: {name}")
        seen_names.add(name)
        if not cap.get("keywords"):
            problems.append(f"{name}: no keywords")
        impl = cap.get("impl", "")
        if not impl:
            problems.append(f"{name}: no impl file declared")
        elif not os.path.exists(os.path.join(ROOT, impl)):
            problems.append(f"{name}: impl file missing -> {impl}")
    return problems


def main():
    ap = argparse.ArgumentParser(description="AIShield capability gap analyser")
    ap.add_argument("--report", action="store_true",
                    help="Print the capability catalog as markdown")
    args = ap.parse_args()

    problems = verify_catalog()
    if problems:
        print("CATALOG PROBLEMS:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"catalog OK: {len(CAPABILITY_CATALOG)} capabilities, all impl files present")

    if args.report:
        print()
        print("| Capability | Implementation |")
        print("|---|---|")
        for cap in CAPABILITY_CATALOG:
            print(f"| {cap['name']} | `{cap['impl']}` |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
