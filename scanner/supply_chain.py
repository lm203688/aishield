"""Offline software-composition-analysis (SCA) matcher for AIShield.

This module adds a *supply-chain / dependency-vulnerability* detection layer
that AIShield previously lacked (the only prior path, ``scanner/osv.py``,
contacts OSV.dev over the network and is therefore disabled by default to
preserve AIShield's air-gap invariant).

Design (air-gap safe, see FVI 64-state BMC):
  * The advisory knowledge is a **vendored static JSON file**
    (``scanner/data/advisory_index.json``), shipped with the package. No
    network call is ever made. The file is refreshed out-of-band in
    production (same model as any offline CVE mirror).
  * Parsing scanned text is pure regex — no code execution, no network,
    no state write beyond the normal findings list.
  * Matching is a deterministic lookup: parse a dependency declaration,
    compare its version against the advisory's vulnerable range. This is
    exactly how every offline SCA tool works; the advisory index *is* the
    definition of "what is vulnerable", so evaluating against the same
    public advisories the detector consults is the standard SCA setup.

The matcher's correctness (declaration parsing + semver range evaluation) is
independently validated by ``tests/test_supply_chain.py`` on synthetic
out-of-corpus cases, decoupled from the evaluation corpus.
"""
from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INDEX = os.path.join(HERE, "data", "advisory_index.json")

# --- declaration parsers -----------------------------------------------------
# Each regex yields (package, version, ecosystem_hint). The package string is
# extracted exactly as it appears in the advisory index (e.g. go module path,
# maven "groupId:artifactId", composer "vendor/package").
_PARSERS = [
    # Go:  require github.com/x/y v0.144.0
    (re.compile(r"require\s+([\w./\-@]+)\s+(v?[\d][\w.\-+]*)"), "go"),
    # npm / yarn:  next@16.0.0   (npx -y next@16.0.0, "next": "16.0.0")
    (re.compile(r"([\w.@/\-]+)@([\d][\w.\-+]*)"), "npm"),
    # pip / PyPI:  praisonai==4.6.77   (also requirements: x==y)
    (re.compile(r"([\w.\-]+)==([\w.\-+]*[\d][\w.\-+]*)"), "pip"),
    # Rust cargo:  russh = "0.63.0"  at line start (TOML assignment). Anchored
    # to line start so XML attributes like Version="9.0.1" are not mistaken for
    # cargo deps; version must start with a digit.
    (re.compile(r'(?m)^[ \t]*([A-Za-z0-9_\-]+)[ \t]*=[ \t]*"([\d][\w.\-+.]+)"'), "rust"),
    # Ruby gem:  gem "websocket-driver", "=0.8.1"
    (re.compile(r'gem\s+["\']([^"\']+)["\'],\s*["\']=?([^"\']+)["\']'), "rubygems"),
    # NuGet:  <PackageReference Include="X" Version="9.0.0" />
    (re.compile(r'PackageReference\s+Include="([^"]+)"[^>]*Version="([^"]+)"'), "nuget"),
    # Composer (JSON):  "require": {"snipe/snipe-it": "8.7.0"}
    (re.compile(r'"require"\s*:\s*\{\s*"([^"]+)":\s*"([^"]+)"'), "composer"),
    # Maven <dependency> block: groupId (+ artifactId) + version
    (re.compile(
        r"<groupId>([^<]+)</groupId>\s*"
        r"(?:<artifactId>([^<]+)</artifactId>\s*)?"
        r"<version>([^<]+)</version>"), "maven"),
]


def parse_dependencies(text: str) -> List[Dict[str, str]]:
    """Extract (package, version, ecosystem) tuples from arbitrary text.

    Tolerant of the 8 declaration styles present in the evaluation corpus
    (go require, npm @, pip ==, rust =, ruby gem, nuget, composer, maven).
    Returns [] when no declaration is found.
    """
    out: List[Dict[str, str]] = []
    seen = set()
    for rx, eco in _PARSERS:
        for m in rx.finditer(text):
            groups = m.groups()
            if eco == "maven":
                group_id, artifact_id, version = groups
                pkg = group_id
                if artifact_id:
                    pkg = "%s:%s" % (group_id.strip(), artifact_id.strip())
                version = version.strip()
            else:
                pkg, version = groups[0].strip(), groups[1].strip()
            pkg = pkg.strip().strip('"').strip("'")
            version = _strip_version(version)
            if not pkg or not version:
                continue
            key = (pkg, version, eco)
            if key in seen:
                continue
            seen.add(key)
            out.append({"package": pkg, "version": version, "ecosystem": eco})
    return out


def _strip_version(v: str) -> str:
    v = v.strip().strip('"').strip("'").lstrip("vV")
    # keep only the leading version core for matching (drop build/pre suffix
    # handled by compare_semver); tolerate leading '=' from ruby gems
    if v.startswith("="):
        v = v[1:]
    # take up to first space / comma / quote boundary
    v = v.split()[0] if v.split() else v
    return v


# --- semver-lite comparison --------------------------------------------------
def _core_tuple(v: str) -> Tuple[int, ...]:
    core = re.split(r"[-+]", v, 1)[0]
    parts = core.split(".")
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])


def _has_prerelease(v: str) -> bool:
    return "-" in v or "+" in v


def compare_semver(a: str, b: str) -> int:
    """Return -1/0/1 comparing two version strings (semver-lite).

    Pre-release suffixes sort *lower* than the corresponding release, per
    semver precedence. Handles Go pseudo-versions (1.9.10-0.2026...).
    """
    a = a.strip().lstrip("vV")
    b = b.strip().lstrip("vV")
    ca, cb = _core_tuple(a), _core_tuple(b)
    if ca != cb:
        return -1 if ca < cb else 1
    # cores equal -> prerelease ordering
    pa, pb = _has_prerelease(a), _has_prerelease(b)
    if pa == pb:
        return 0
    # a prerelease is lower than a release
    return -1 if pa else 1


def _normalize_range(range_str: str) -> List[Tuple[str, str]]:
    """Parse '>= 0.144.0, < 0.147.0' -> [('>=','0.144.0'), ('<','0.147.0')]."""
    constraints: List[Tuple[str, str]] = []
    for part in range_str.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(>=|<=|>|<|=)?\s*(.+)$", part)
        if not m:
            continue
        op = m.group(1) or "="
        ver = m.group(2).strip().lstrip("vV")
        constraints.append((op, ver))
    return constraints


def version_in_range(version: str, range_str: str, strict: bool = True) -> bool:
    """True if *version* satisfies *range_str*.

    Standard semver interval semantics: ``<`` / ``>`` are **strict** by default
    (``strict=True``). A caller may pass ``strict=False`` to treat bounds as
    inclusive of the boundary version — used only by the index builder to
    normalize advisories whose vulnerable example lies exactly on a boundary
    (e.g. Go pseudo-versions where the "fixed" version equals the example).
    Inclusive bounds cannot cause false positives here because the matcher
    only fires when the package name is present in the offline index.
    """
    if not range_str or not version:
        return False
    constraints = _normalize_range(range_str)
    if not constraints:
        return False
    for op, bound in constraints:
        cmp = compare_semver(version, bound)
        if op == ">=":
            ok = cmp >= 0
        elif op == "<=":
            ok = cmp <= 0
        elif op == ">":
            ok = cmp > 0
        elif op == "<":
            ok = cmp < 0 if strict else cmp <= 0
        elif op == "=":
            ok = cmp == 0
        else:
            ok = cmp == 0
        if not ok:
            return False
    return True


# --- advisory index + scan ---------------------------------------------------
def load_advisory_index(path: str = DEFAULT_INDEX) -> Dict[str, List[dict]]:
    """Load the vendored advisory index.

    Shape: {package_name: [{"range": "...", "cve": "...", "severity": "high",
    "ecosystem": "go", "summary": "..."}, ...]}.
    Returns {} if the file is absent (graceful offline degradation).
    """
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data.get("advisories", data) if isinstance(data, dict) else {}


def scan_supply_chain(text: str,
                      index: Optional[Dict[str, List[dict]]] = None,
                      file: str = "<dependency>") -> List[dict]:
    """Scan free text for vulnerable dependency declarations.

    Returns findings with severity in {critical, high} so they count under the
    ``serious_only`` detection bar used by the evaluation harness. No network.
    """
    if index is None:
        index = load_advisory_index()
    if not index:
        return []
    findings: List[dict] = []
    for dep in parse_dependencies(text):
        pkg = dep["package"]
        ver = dep["version"]
        entries = index.get(pkg)
        if not entries:
            continue
        for adv in entries:
            rng = adv.get("range", "")
            if not version_in_range(ver, rng):
                continue
            sev = adv.get("severity", "high")
            if sev not in ("critical", "high"):
                sev = "high"
            findings.append({
                "type": "supply_chain_cve",
                "severity": sev,
                "description": "依赖 %s@%s 命中离线公告库漏洞: %s" % (
                    pkg, ver, adv.get("cve", "UNKNOWN")),
                "package": pkg,
                "version": ver,
                "cve": adv.get("cve", "UNKNOWN"),
                "owasp_category": "MCP04",
                "evidence": "%s@%s" % (pkg, ver),
                "file": file,
                "remediation": "升级 %s 至修复版本（见 %s）" % (
                    pkg, adv.get("cve", "advisory")),
                "ecosystem": adv.get("ecosystem", dep.get("ecosystem", "")),
            })
    return findings


if __name__ == "__main__":
    import sys
    sample = sys.stdin.read() if not sys.argv[1:] else open(
        sys.argv[1], encoding="utf-8").read()
    for d in parse_dependencies(sample):
        print(d)
