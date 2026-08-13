#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield · AI Agent Ecosystem Tech Radar
========================================

Daily closed-loop task (registered as WorkBuddy automation at 02:00 Beijing).

Goal:
  Actively track the AI agent / MCP ecosystem for new open-source tech,
  new attack vectors, new protocols, and competitor capabilities.
  Produce a categorised daily report + auto-draft rule candidates +
  create GitHub issue for critical signals.

Design:
  - Zero third-party deps (stdlib only; network goes through a curl subprocess
    to bypass the local TLS-intercepting proxy that resets Python's urllib;
    urllib is kept as a fallback when curl is absent).
  - Each scan source is independent: failure of one source never aborts others.
  - Idempotent: safe to re-run; uses data/state/tech_radar.json as dedupe history.
  - Dry-run by default for first run; --live to enable issue creation.

Output:
  - docs/intel/YYYY-MM-DD-tech-radar.md   (human-readable daily report)
  - data/state/tech_radar.json             (machine-readable signal history)
  - scanner/rules/_proposed/*.py           (auto-drafted rule stubs)
  - GitHub issues                          (critical signals only, --live)

Usage:
  python scripts/tech_radar.py --dry-run            # local validation
  python scripts/tech_radar.py --once --dry-run     # single pass, no issues
  python scripts/tech_radar.py --once --live        # single pass + create issues
"""
from __future__ import annotations

import argparse
import base64
import datetime
import glob
import hashlib
import json
import tempfile
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capability_gap  # noqa: E402  (sibling module, adopt-line analysis)

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTEL_DIR = os.path.join(ROOT, "docs", "intel")
STATE_FILE = os.path.join(ROOT, "data", "state", "tech_radar.json")
PROPOSED_DIR = os.path.join(ROOT, "scanner", "_proposed")
REPO = "lm203688/aishield"

# Keywords used to filter GitHub repos and arXiv papers
TRACK_KEYWORDS = [
    "mcp-server", "mcp security", "mcp audit", "mcp-scan",
    "agent-security", "agent scanner", "agent guardrail",
    "prompt-injection", "jailbreak llm", "tool-use attack",
    "agentic ai", "agentic security", "agentic threat",
    "claude security", "claude-code security", "mcp poison",
    "skill injection", "agent card", "a2a protocol",
    "x402", "model context protocol security",
]

# Platforms the user explicitly wants tracked (even if adjacent).
USER_PLATFORMS = [
    # name, github_org (or None), check_tag
    ("hubport",          None,                    "mcp"),       # 呼波特
    ("anthropic claude", "anthropics",            "security"),
    ("microsoft mdash",  "microsoft",             "agent"),
    ("cisco antares",    "cisco",                 "ai"),
]

# Severity thresholds
CRITICAL_TAGS = {"new-cve", "protocol-vuln", "fundamental-bypass"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

def _today_str() -> str:
    return _now_utc().strftime("%Y-%m-%d")

def _fetch(url, headers=None, method="GET", data=None, timeout=20):
    """Transport: curl subprocess (TLS-intercepting-proxy workaround) with an
    urllib fallback when curl is unavailable. Returns (status, body_text).

    Why curl: this box sits behind a TLS-intercepting proxy that resets
    Python's `urllib` handshake (SSL UNEXPECTED_EOF); `curl` uses the OS trust
    store and succeeds. Mirrors the approach used by scripts/gh_push.py.
    """
    headers = dict(headers or {})
    headers.setdefault("User-Agent", "aishield-tech-radar/1.0")
    if shutil.which("curl") is None:
        return _fetch_urllib(url, headers, method, data, timeout)
    cmd = ["curl", "-sS", "--max-time", str(timeout), "-i", "-X", method.upper()]
    for k, v in headers.items():
        cmd += ["-H", f"{k}: {v}"]
    if data is not None:
        cmd += ["-d", data if isinstance(data, str) else json.dumps(data)]
    cmd.append(url)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              errors="replace", timeout=timeout + 5)
    except Exception as e:
        return -1, str(e)
    out = proc.stdout or ""
    if "\r\n\r\n" in out:
        head, _, body = out.partition("\r\n\r\n")
    elif "\n\n" in out:
        head, _, body = out.partition("\n\n")
    else:
        head, body = "", out
    status = -1
    for line in head.splitlines():
        if line.upper().startswith("HTTP/"):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    status = int(parts[1])
                except ValueError:
                    pass
            break
    return status, body


def _fetch_urllib(url, headers, method="GET", data=None, timeout=20):
    req = urllib.request.Request(url, method=method.upper())
    for k, v in headers.items():
        req.add_header(k, v)
    if data is not None:
        req.data = data.encode("utf-8") if isinstance(data, str) else data
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return -1, str(e)


def _http_json(url, headers=None, timeout=20):
    status, body = _fetch(url, headers=headers, timeout=timeout)
    try:
        return status, json.loads(body or "{}")
    except Exception:
        return status, {"_error": "json parse failed", "_raw": (body or "")[:200]}


def _http_text(url, headers=None, timeout=20):
    return _fetch(url, headers=headers, timeout=timeout)

def _pat():
    p = os.path.join(ROOT, ".workbuddy", "schedule-revert-pat.txt")
    if os.path.exists(p):
        return open(p, encoding="utf-8").read().strip()
    return os.environ.get("AISHIELD_PAT", "")

def _ensure_dirs():
    os.makedirs(INTEL_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    os.makedirs(PROPOSED_DIR, exist_ok=True)

def _load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.loads(open(STATE_FILE, encoding="utf-8").read())
        except Exception:
            pass
    return {"seen_ids": [], "last_run": None, "runs": 0}

def _save_state(state):
    # Merge onto whatever is on disk: mid-scan writers (e.g. the arXiv endpoint
    # hint) must not be clobbered by the stale copy main() loaded at startup.
    merged = _load_state()
    merged.update(state)
    merged["last_run"] = _now_utc().isoformat()
    merged["runs"] = merged.get("runs", 0) + 1
    open(STATE_FILE, "w", encoding="utf-8").write(
        json.dumps(merged, ensure_ascii=False, indent=2)
    )

def _save_endpoint_hint(state):
    """Persist state without touching run counters (used mid-scan)."""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        open(STATE_FILE, "w", encoding="utf-8").write(
            json.dumps(state, ensure_ascii=False, indent=2)
        )
    except Exception:
        pass

def _signal_id(sig):
    h = hashlib.sha1()
    h.update(json.dumps(sig, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()[:12]

def _within_days(date_str, days):
    """True if YYYY-MM-DD is within the look-back window (unparseable -> keep)."""
    try:
        dt = datetime.datetime.strptime((date_str or "")[:10], "%Y-%m-%d")
    except Exception:
        return True
    return (_now_utc() - dt).days <= days


# ---------------------------------------------------------------------------
# Source: GitHub trending repos matching agent/MCP/security keywords
# ---------------------------------------------------------------------------
def scan_github_trending(days=7, max_per_keyword=8):
    pat = _pat()
    headers = {"Accept": "application/vnd.github+json"}
    if pat:
        headers["Authorization"] = f"Bearer {pat}"

    cutoff = (_now_utc() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    signals = []
    seen_repos = set()

    for kw in TRACK_KEYWORDS:
        q = urllib.parse.quote(f"{kw} created:>{cutoff} stars:>5")
        url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={max_per_keyword}"
        status, data = _http_json(url, headers=headers)
        if status != 200:
            signals.append({
                "_source": "github-trending",
                "_kw": kw,
                "_error": data.get("_error", f"HTTP {status}"),
            })
            continue
        for repo in data.get("items", []):
            full = repo.get("full_name", "")
            if full in seen_repos:
                continue
            seen_repos.add(full)
            signals.append({
                "_source": "github-trending",
                "id": _signal_id({"repo": full, "url": repo.get("html_url", "")}),
                "title": repo.get("full_name", ""),
                "description": (repo.get("description") or "")[:300],
                "url": repo.get("html_url", ""),
                "stars": repo.get("stargazers_count", 0),
                "created": repo.get("created_at", "")[:10],
                "language": repo.get("language") or "?",
                "keyword": kw,
            })
        time.sleep(0.3)  # be polite
    return signals


# ---------------------------------------------------------------------------
# Source: arXiv recent papers on agent security / prompt injection
# ---------------------------------------------------------------------------
ARXIV_QUERIES = [
    'all:"prompt injection" AND all:"agent"',
    'all:"jailbreak" AND all:"tool"',
    'all:"mcp" AND all:"security"',
    'all:"agentic" AND all:"attack"',
    'all:"model context protocol"',
]

# Categories polled by the RSS / listing fallbacks. Keyword filtering is then
# applied locally, so we do not depend on the (often unreachable) search API.
ARXIV_CATEGORIES = ["cs.CR", "cs.AI", "cs.MA", "cs.SE"]

# Relevance filter applied to RSS/listing results (search API already filters).
ARXIV_RELEVANCE = [
    "agent", "agentic", "llm", "language model", "prompt", "injection",
    "jailbreak", "tool use", "tool-use", "mcp", "model context protocol",
    "multi-agent", "autonomous", "guardrail", "red team", "adversarial",
]


def _arxiv_relevant(text):
    t = (text or "").lower()
    return any(k in t for k in ARXIV_RELEVANCE)


def _arxiv_via_api(days, max_results):
    """Endpoint A: export.arxiv.org search API (most precise, often DNS-blocked)."""
    signals, seen = [], set()

    # Cheap probe first: skip the whole endpoint if unreachable rather than
    # burning ~100s on retries.
    probe_url = (
        "https://export.arxiv.org/api/query?"
        + urllib.parse.urlencode(
            {"search_query": ARXIV_QUERIES[0], "max_results": 1},
            quote_via=urllib.parse.quote,
        )
    )
    ps, _ = _http_text(probe_url, timeout=12)
    if ps != 200:
        raise RuntimeError(f"export.arxiv.org probe failed (HTTP {ps})")

    for q in ARXIV_QUERIES:
        url = (
            "https://export.arxiv.org/api/query?"
            + urllib.parse.urlencode({
                "search_query": q,
                "start": 0,
                "max_results": max_results,
                "sortBy": "submittedDate",
                "sortOrder": "desc",
            }, quote_via=urllib.parse.quote)  # arXiv rejects %2B; needs %20
        )
        status, body = _http_text(url, timeout=30)
        if status != 200 or not body:
            continue
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            continue
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("a:entry", ns):
            eid = entry.findtext("a:id", default="", namespaces=ns)
            if not eid or eid in seen:
                continue
            seen.add(eid)
            published = (entry.findtext("a:published", default="", namespaces=ns) or "")[:10]
            if not _within_days(published, days):
                continue
            signals.append({
                "_source": "arxiv",
                "_endpoint": "api",
                "id": _signal_id({"arxiv": eid}),
                "title": (entry.findtext("a:title", default="", namespaces=ns) or "").strip()[:200],
                "summary": (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()[:400],
                "url": eid,
                "published": published,
                "query": q,
            })
        time.sleep(1.0)  # arXiv asks for politeness
    return signals


def _arxiv_via_rss(days, max_results):
    """Endpoint B: rss.arxiv.org per-category feed (fast, weekdays only)."""
    signals, seen = [], set()
    reachable = False
    for cat in ARXIV_CATEGORIES:
        status, body = _http_text(f"https://rss.arxiv.org/rss/{cat}", timeout=20)
        if status != 200 or not body:
            continue
        reachable = True
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            continue
        for item in root.iter("item"):
            link = (item.findtext("link") or "").strip()
            title = (item.findtext("title") or "").strip()
            if not link or link in seen:
                continue
            seen.add(link)
            desc = (item.findtext("description") or "").strip()
            if not _arxiv_relevant(f"{title} {desc}"):
                continue
            signals.append({
                "_source": "arxiv",
                "_endpoint": "rss",
                "id": _signal_id({"arxiv": link}),
                "title": title[:200],
                "summary": re.sub(r"<[^>]+>", " ", desc)[:400],
                "url": link,
                "published": _today_str(),
                "query": f"cat:{cat}",
            })
        time.sleep(0.3)
    if not reachable:
        raise RuntimeError("rss.arxiv.org unreachable for all categories")
    # RSS is empty on weekends/holidays -- that is valid, not an error.
    return signals[: max_results * len(ARXIV_CATEGORIES)]


_LIST_ENTRY_RE = re.compile(
    r'<a href\s*="/abs/(?P<id>\d{4}\.\d{4,5})".*?'
    r"<div class='list-title mathjax'>\s*<span class='descriptor'>Title:</span>\s*"
    r"(?P<title>.*?)\s*</div>",
    re.S,
)


def _arxiv_via_listing(days, max_results):
    """Endpoint C: arxiv.org/list/<cat>/recent HTML (last-resort, always up)."""
    signals, seen = [], set()
    reachable = False
    for cat in ARXIV_CATEGORIES:
        status, html = _http_text(
            f"https://arxiv.org/list/{cat}/recent",
            headers={"User-Agent": "Mozilla/5.0 (compatible; aishield-tech-radar/1.0)"},
            timeout=30,
        )
        if status != 200 or not html:
            continue
        reachable = True
        for m in _LIST_ENTRY_RE.finditer(html):
            aid, title = m.group("id"), re.sub(r"\s+", " ", m.group("title")).strip()
            if aid in seen or not title:
                continue
            seen.add(aid)
            if not _arxiv_relevant(title):
                continue
            signals.append({
                "_source": "arxiv",
                "_endpoint": "listing",
                "id": _signal_id({"arxiv": f"https://arxiv.org/abs/{aid}"}),
                "title": title[:200],
                "summary": "",
                "url": f"https://arxiv.org/abs/{aid}",
                "published": _today_str(),
                "query": f"cat:{cat}",
            })
        time.sleep(0.5)
    if not reachable:
        raise RuntimeError("arxiv.org listing unreachable for all categories")
    return signals[: max_results * len(ARXIV_CATEGORIES)]


def scan_arxiv(days=7, max_results=10):
    """Scan arXiv via a three-tier endpoint chain.

    Root cause of past 0-yield days: `export.arxiv.org` fails DNS resolution
    from some networks (WinError 11002), which the old probe misreported as an
    "arXiv outage". `rss.arxiv.org` and `arxiv.org` remain reachable, so we now
    degrade to category feeds + local keyword filtering instead of giving up.
    """
    chain = [
        ("api",     _arxiv_via_api),
        ("rss",     _arxiv_via_rss),
        ("listing", _arxiv_via_listing),
    ]
    # Try last known-good endpoint first -- avoids re-probing a DNS-blocked
    # host every single run (saves ~15s/day on networks that block export.*).
    preferred = _load_state().get("arxiv_endpoint")
    if preferred:
        chain.sort(key=lambda item: 0 if item[0] == preferred else 1)

    attempts = []
    for name, fn in chain:
        try:
            out = fn(days, max_results)
        except Exception as e:  # endpoint unreachable -> try the next one
            attempts.append(f"{name}: {e}")
            continue
        if out:
            st = _load_state()
            if st.get("arxiv_endpoint") != name:
                st["arxiv_endpoint"] = name
                _save_endpoint_hint(st)
            return out
        # Endpoint worked but returned nothing (e.g. RSS on a weekend).
        attempts.append(f"{name}: reachable but 0 relevant items")
    return [{
        "_source": "arxiv",
        "_query": "endpoint-chain",
        "_error": "no arXiv endpoint yielded items -- " + " | ".join(attempts),
    }]


# ---------------------------------------------------------------------------
# Source: HackerNews (Algolia) -- high-signal agent/MCP stories
# ---------------------------------------------------------------------------
def scan_hackernews(days=7, min_points=10):
    queries = ["mcp server", "mcp security", "agent security", "prompt injection agent",
               "model context protocol", "agentic ai security", "claude code security"]
    cutoff_ts = int((_now_utc() - datetime.timedelta(days=days)).timestamp())
    signals = []
    seen_ids = set()

    for q in queries:
        url = (
            "https://hn.algolia.com/api/v1/search?"
            + urllib.parse.urlencode({
                "query": q,
                "tags": "story",
                "numericFilters": f"points>{min_points},created_at_i>{cutoff_ts}",
                "hitsPerPage": 10,
            })
        )
        status, data = _http_json(url)
        if status != 200:
            signals.append({"_source": "hn", "_query": q, "_error": f"HTTP {status}"})
            continue
        for hit in data.get("hits", []):
            oid = hit.get("objectID", "")
            if oid in seen_ids:
                continue
            seen_ids.add(oid)
            signals.append({
                "_source": "hn",
                "id": _signal_id({"hn": oid}),
                "title": hit.get("title", "")[:200],
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={oid}",
                "points": hit.get("points", 0),
                "comments": hit.get("num_comments", 0),
                "created": hit.get("created_at", "")[:10],
                "query": q,
            })
        time.sleep(0.3)
    return signals


# ---------------------------------------------------------------------------
# Source: Reddit r/LocalLLaMA + r/MCP (top of week)
# ---------------------------------------------------------------------------
def scan_reddit(days=7, limit_per_sub=20):
    subs = ["LocalLLaMA", "MCP", "ClaudeAI", "Anthropic"]
    signals = []
    headers = {"User-Agent": "aishield-tech-radar/1.0 (research)"}

    for sub in subs:
        # t=week -> top of past week
        url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit={limit_per_sub}"
        status, data = _http_json(url, headers=headers, timeout=20)
        if status != 200:
            signals.append({"_source": "reddit", "_sub": sub, "_error": f"HTTP {status}"})
            continue
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            score = d.get("score", 0)
            if score < 30:
                continue
            signals.append({
                "_source": "reddit",
                "id": _signal_id({"reddit": d.get("id", "")}),
                "title": (d.get("title") or "")[:200],
                "url": "https://reddit.com" + (d.get("permalink") or ""),
                "score": score,
                "comments": d.get("num_comments", 0),
                "sub": sub,
                "created": datetime.datetime.utcfromtimestamp(
                    d.get("created_utc", 0)
                ).strftime("%Y-%m-%d"),
            })
        time.sleep(1.0)  # Reddit is strict
    return signals


# ---------------------------------------------------------------------------
# Source: OWASP / standards orgs via their GitHub repos (recent activity)
# ---------------------------------------------------------------------------
def scan_standards_orgs(pat):
    headers = {"Accept": "application/vnd.github+json"}
    if pat:
        headers["Authorization"] = f"Bearer {pat}"
    orgs = [
        ("OWASP",         "OWASP"),
        ("AgenticAI",     "agentic-ai"),  # OWASP Agentic AI Top 10
        ("linuxfoundation", "linux-foundation"),
    ]
    signals = []
    for label, org in orgs:
        url = f"https://api.github.com/orgs/{org}/repos?sort=updated&per_page=8"
        status, data = _http_json(url, headers=headers)
        if status != 200:
            signals.append({"_source": "standards", "_org": org, "_error": f"HTTP {status}"})
            continue
        for repo in data if isinstance(data, list) else []:
            updated = (repo.get("updated_at") or "")[:10]
            try:
                upd_dt = datetime.datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ")
                if (_now_utc() - upd_dt).days > 14:
                    continue
            except Exception:
                continue
            signals.append({
                "_source": "standards",
                "id": _signal_id({"std": repo.get("full_name", "") + updated}),
                "title": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "description": (repo.get("description") or "")[:200],
                "updated": updated,
                "org": label,
            })
        time.sleep(0.4)
    return signals


# ---------------------------------------------------------------------------
# Source: user-specified platforms (intersect with MCP/agent keywords)
# ---------------------------------------------------------------------------
def scan_user_platforms(pat):
    headers = {"Accept": "application/vnd.github+json"}
    if pat:
        headers["Authorization"] = f"Bearer {pat}"
    signals = []
    for name, org, tag in USER_PLATFORMS:
        if not org:
            # No GitHub presence known -- record a note for human follow-up
            signals.append({
                "_source": "user-platform",
                "id": _signal_id({"up": name, "date": _today_str()}),
                "title": f"{name} (manual watch)",
                "url": "",
                "description": f"Track {name} releases/changelog for intersection with {tag}",
                "needs_manual_check": True,
            })
            continue
        # Look at recent repos from this org matching the tag
        url = (
            f"https://api.github.com/search/repositories?q=org:{org}+{tag}"
            f"+created:>{(_now_utc() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')}"
            "&sort=updated&per_page=5"
        )
        status, data = _http_json(url, headers=headers)
        if status != 200:
            signals.append({"_source": "user-platform", "_org": org, "_error": f"HTTP {status}"})
            continue
        for repo in data.get("items", []):
            signals.append({
                "_source": "user-platform",
                "id": _signal_id({"up": repo.get("full_name", "")}),
                "title": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "description": (repo.get("description") or "")[:200],
                "platform": name,
            })
        time.sleep(0.4)
    return signals


# ---------------------------------------------------------------------------
# Classification & criticality
# ---------------------------------------------------------------------------
# Ordered most-specific -> most-generic; first match wins.
# Each entry maps to an attack category that AIShield can (or should) detect.
ATTACK_PATTERNS = [
    # -- Skill / plugin surface (AIShield scans skills, so this is core) ------
    (r"(malicious|poison\w*|backdoor\w*)\s+skill",           "skill-poisoning"),
    (r"skill\s*(file|system)s?\b.*\b(risk|attack|malicious)", "skill-poisoning"),
    (r"skill\s*injection",                                    "skill-poisoning"),
    # -- Memory / trajectory / self-evolving state ---------------------------
    (r"trajectory\s*poison",                                  "trajectory-poisoning"),
    (r"memory\s*(poison|injection|corruption)",               "memory-poisoning"),
    (r"self[- ]evolving\s+agent",                             "trajectory-poisoning"),
    # -- Prompt / instruction layer -----------------------------------------
    (r"prompt\s*injection",                                   "prompt-injection"),
    (r"indirect\s+injection",                                 "prompt-injection"),
    (r"instruction\s*(backdoor|hijack)",                      "instruction-hijack"),
    (r"jailbreak",                                            "jailbreak"),
    # -- Tool / MCP layer ----------------------------------------------------
    (r"tool\s*(poison|injection|squatting)",                  "tool-poisoning"),
    (r"(mcp|model context protocol)\b.*\b(poison|vuln|exploit|attack|threat)",
                                                              "mcp-attack"),
    (r"rug\s*pull",                                           "rug-pull"),
    (r"confused\s+deputy",                                    "confused-deputy"),
    (r"excessive\s+agency",                                   "excessive-agency"),
    # -- Identity / trust ----------------------------------------------------
    (r"agent\s*(card\s*)?spoof",                              "agent-spoof"),
    (r"(impersonat\w+|identity\s+spoof)\s*.*agent",           "agent-spoof"),
    # -- Data / credentials --------------------------------------------------
    (r"credential\s*(exfil\w*|leak\w*|theft|steal\w*)",       "credential-theft"),
    (r"data\s*exfiltrat\w+",                                  "data-exfiltration"),
    # -- Supply chain --------------------------------------------------------
    (r"supply\s*chain",                                       "supply-chain"),
    (r"(dependency|package)\s*(confusion|typosquat\w*)",      "supply-chain"),
    # -- Generic agent attack (catch-all, keep last) -------------------------
    (r"backdoor\s*(attack|trigger)",                          "backdoor"),
    (r"(llm|agent|agentic)\s*.*\b(red[- ]team\w*|adversarial attack)\b",
                                                              "adversarial-agent"),
]

# Title cues that escalate severity.
_SEV_CRITICAL = ["bypass", "exploit", "rce", "remote code", "unauthenticated",
                 "zero-day", "0-day", "wormable", "privilege escalation"]
_SEV_HIGH = ["new attack", "first", "novel", "breaking", "automated attack",
             "practical attack", "real-world attack", "in the wild"]


def classify_signal(sig):
    """Return (category, severity) for a signal, or (None, None)."""
    text = " ".join(str(v) for v in sig.values() if isinstance(v, str)).lower()
    cat = next((c for pat, c in ATTACK_PATTERNS if re.search(pat, text)), None)
    if not cat:
        return None, None
    title = (sig.get("title") or "").lower()
    if any(k in title for k in _SEV_CRITICAL):
        return cat, "critical"
    if any(k in title for k in _SEV_HIGH):
        return cat, "high"
    # A defence/benchmark paper describes an attack but is not itself a threat.
    if any(k in title for k in ["defen", "guard", "mitigat", "survey", "benchmark",
                                "detect", "safeguard", "certification"]):
        return cat, "medium"
    return cat, "high"


def is_critical(sig):
    cat, sev = classify_signal(sig)
    return sev == "critical"


# ---------------------------------------------------------------------------
# Auto-draft rule candidates
# ---------------------------------------------------------------------------
def _slugify(text):
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return (s[:30] or "rule")


def draft_rule_candidate(sig):
    """Write a rule candidate for a high-severity signal. Return path or None.

    Candidates are JSON, matching how the scanner actually stores rules
    (`{pattern: (description, severity)}` -- see scanner/rules.py). An earlier
    version emitted Python stubs subclassing `Rule`/`RuleResult`; those classes
    do not exist in this project, so every stub was unusable by construction.
    """
    cat, sev = classify_signal(sig)
    if not cat:
        return None
    slug = _slugify(sig.get("title", "rule")) + "_" + sig.get("id", "x")[:6]
    date = _today_str()
    fname = f"PROPOSED_{date.replace('-', '')}_{slug}.json"
    fpath = os.path.join(PROPOSED_DIR, fname)

    candidate = {
        "status": "draft",
        "_instructions": [
            "1. Read the source signal URL and understand the attack.",
            "2. Fill in `rules`: each needs a real regex `pattern`, a Chinese "
            "`description` and a `severity` (critical|high|medium|low).",
            "3. Set `status` to `ready`.",
            "4. Run: python scripts/promote_rule.py --check   (validates every "
            "candidate: regex compiles, no false positives on benign corpus)",
            "5. Run: python scripts/promote_rule.py --promote <file>",
            "   Rejected? Fix or delete the file -- do not leave drafts to rot.",
        ],
        "drafted_at": date,
        "signal": {
            "id": sig.get("id", ""),
            "title": (sig.get("title") or "")[:200],
            "url": sig.get("url", ""),
            "source": sig.get("_source", "unknown"),
        },
        "attack_category": cat,
        "severity": sev,
        "rules": [
            {
                "pattern": "TODO: regex here",
                "description": f"TODO: 中文描述 ({cat})",
                "severity": sev,
            }
        ],
        "review_notes": "",
    }
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(candidate, f, ensure_ascii=False, indent=2)
    return fpath


# ---------------------------------------------------------------------------
# GitHub issue creation (critical signals only, --live)
# ---------------------------------------------------------------------------
def create_github_issue(pat, sig, cat, sev):
    if not pat:
        return None
    title = f"[Tech Radar] {cat} :: {(sig.get('title') or '')[:80]}"
    body = (
        f"**Auto-flagged by tech_radar.py on {_today_str()}**\n\n"
        f"- Source: `{sig.get('_source', '?')}`\n"
        f"- Severity: **{sev}**\n"
        f"- Attack category: `{cat}`\n"
        f"- Link: {sig.get('url', '')}\n\n"
        f"### Why flagged\n"
        f"This signal matches a known attack pattern (`{cat}`) with "
        f"critical severity per radar heuristics.\n\n"
        f"### Next steps\n"
        f"- [ ] Review the source\n"
        f"- [ ] Decide: add rule / ignore / monitor\n"
        f"- [ ] If add: see `scanner/rules/_proposed/` for auto-drafted stub\n"
    )
    payload = {
        "title": title,
        "body": body,
        "labels": ["tech-radar", f"severity:{sev}", f"category:{cat}"],
    }
    status, body = _fetch(
        f"https://api.github.com/repos/{REPO}/issues",
        headers={
            "Authorization": f"Bearer {pat}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method="POST",
        data=json.dumps(payload),
        timeout=30,
    )
    if status == 201:
        try:
            return json.loads(body or "{}").get("html_url")
        except Exception:
            return None
    print(f"  issue creation failed: HTTP {status}", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# GitHub publish -- auto-commit intel report + index to public main
# (closes the "occupation loop": a dated, continuous, machine-readable trail
#  that proves we have tracked the ecosystem since date X)
# ---------------------------------------------------------------------------
def _gh_get_file(rel_path, token):
    """Return (sha, base64_content) for a file on main, or (None, None)."""
    url = (f"https://api.github.com/repos/{REPO}/contents/"
           f"{rel_path.replace(os.sep, '/')}?ref=main")
    status, body = _fetch(
        url,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json"},
        method="GET", timeout=20)
    if status != 200:
        return None, None
    try:
        obj = json.loads(body or "{}")
        return obj.get("sha"), (obj.get("content") or "").replace("\n", "")
    except Exception:
        return None, None


def _gh_api_put(rel_path, content_str, message, token, sha=None):
    """PUT a file to the GitHub Contents API. Curl subprocess primary (TLS
    proxy workaround), urllib fallback when curl is absent. Writes payload to
    a temp file to dodge the Windows ~8k command-line limit."""
    url = (f"https://api.github.com/repos/{REPO}/contents/"
           f"{rel_path.replace(os.sep, '/')}")
    payload = {
        "message": message,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("ascii"),
        "branch": "main",
    }
    if sha:
        payload["sha"] = sha
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="ghpush_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        if shutil.which("curl") is not None:
            cmd = ["curl", "-sS", "--max-time", "30", "-X", "PUT", url,
                   "-H", f"Authorization: Bearer {token}",
                   "-H", "Accept: application/vnd.github+json",
                   "-H", "Content-Type: application/json",
                   "-d", f"@{tmp}"]
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  errors="replace", timeout=40)
            out = proc.stdout or ""
        else:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"), method="PUT")
            req.add_header("Authorization", f"Bearer {token}")
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("Content-Type", "application/json")
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    out = resp.read().decode("utf-8", "replace")
            except urllib.error.HTTPError as e:
                out = e.read().decode("utf-8", "replace")
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass
    try:
        data = json.loads(out or "{}")
    except Exception:
        return False, "no-json response"
    if "commit" in data:
        return True, data.get("commit", {}).get("sha", "")[:8]
    return False, data.get("message", "unknown error")[:160]


def _build_index():
    """Rolling index of all daily radar reports -> docs/intel/index.md."""
    files = sorted(glob.glob(os.path.join(INTEL_DIR, "*-tech-radar.md")),
                   reverse=True)
    lines = ["# AIShield Tech Radar — 索引 / Index", ""]
    lines.append("_滚动索引：每日自动生成并推送到 public `main`。"
                 "一条带日期的持续追踪记录，就是“这个方向我们从 X 月就在跟”的"
                 "不可伪造证据 —— 生态位提前卡位的实质。_")
    lines.append("")
    lines.append("| 日期 | 报告 |")
    lines.append("|---|---|")
    for f in files:
        base = os.path.basename(f)
        date = base.replace("-tech-radar.md", "")
        lines.append(f"| {date} | [{base}](./{base}) |")
    lines.append("")
    idx_path = os.path.join(INTEL_DIR, "index.md")
    with open(idx_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return os.path.relpath(idx_path, ROOT).replace(os.sep, "/")


def _publish(rel_paths, token, message):
    """Best-effort publish of local files to public main. Returns list of
    (rel_path, ok, info). Never raises -- publishing must not break the scan."""
    results = []
    for rel in rel_paths:
        abs_p = os.path.join(ROOT, rel)
        if not os.path.exists(abs_p):
            results.append((rel, False, "missing local file"))
            continue
        content = open(abs_p, encoding="utf-8").read()
        my_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
        sha, cur_b64 = _gh_get_file(rel, token)
        if sha and cur_b64 == my_b64:
            results.append((rel, True, "unchanged (skipped)"))
            continue
        ok, info = _gh_api_put(rel, content, message, token, sha)
        results.append((rel, ok, info))
    return results


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------
SECTION_HEADERS = {
    "github-trending": "🆕 New open-source repos (potential integration/defense)",
    "arxiv":           "📄 Recent arXiv papers (attack research)",
    "hn":              "🗞 HackerNews high-signal discussions",
    "reddit":          "💬 Reddit top discussions",
    "standards":       "📜 Standards orgs recent activity (OWASP / LF)",
    "user-platform":   "🏢 User-specified platforms",
}


def render_report(signals, drafted_rules, created_issues, errors):
    today = _today_str()
    lines = [f"# AI Agent Ecosystem Tech Radar — {today}", ""]
    lines.append(f"_Auto-generated by `scripts/tech_radar.py` at "
                 f"{_now_utc().strftime('%H:%M UTC')}._")
    lines.append("")

    # Stats
    by_src = {}
    for s in signals:
        src = s.get("_source", "?")
        by_src[src] = by_src.get(src, 0) + 1
    lines.append("## 📊 Signal volume")
    lines.append("")
    lines.append("| Source | Count |")
    lines.append("|---|---|")
    for src, n in sorted(by_src.items(), key=lambda x: -x[1]):
        lines.append(f"| {src} | {n} |")
    lines.append(f"| **errors** | **{len(errors)}** |")
    lines.append("")

    # Per-source sections
    grouped = {}
    for s in signals:
        if "_error" in s or "id" not in s:
            continue
        grouped.setdefault(s["_source"], []).append(s)

    for src, header in SECTION_HEADERS.items():
        items = grouped.get(src, [])
        if not items:
            continue
        lines.append(f"## {header}")
        lines.append("")
        # sort by relevance: stars/points/score desc, capped at 15
        items.sort(key=lambda x: -(x.get("stars") or x.get("points") or x.get("score") or 0))
        for it in items[:15]:
            title = it.get("title", "?")
            url = it.get("url", "")
            extra = []
            if "stars" in it:    extra.append(f"⭐ {it['stars']}")
            if "points" in it:   extra.append(f"▲ {it['points']} (💬 {it.get('comments', 0)})")
            if "score" in it:    extra.append(f"⬆ {it['score']} (💬 {it.get('comments', 0)})")
            if "language" in it: extra.append(f"`{it['language']}`")
            if "keyword" in it:  extra.append(f"kw:`{it['keyword']}`")
            line = f"- [{title}]({url})" if url else f"- {title}"
            if extra:
                line += "  " + " · ".join(extra)
            cat, sev = classify_signal(it)
            if cat:
                line += f"  → **{cat}** / {sev}"
            lines.append(line)
        lines.append("")

    # Errors
    if errors:
        lines.append("## ⚠️ Source errors (non-fatal)")
        lines.append("")
        for e in errors[:20]:
            lines.append(f"- `{e}`")
        lines.append("")

    # Auto-drafted rule candidates
    if drafted_rules:
        lines.append("## 🤖 Auto-drafted rule candidates")
        lines.append("")
        lines.append("These stubs were generated for high-severity signals. "
                     "Review and either move into `scanner/rules.py` or delete.")
        lines.append("")
        for p in drafted_rules:
            rel = os.path.relpath(p, ROOT)
            lines.append(f"- `{rel}`")
        lines.append("")

    # Adopt line -- capability gap analysis (defensive tech we may be missing)
    try:
        gap_result = capability_gap.analyse(signals)
        lines.extend(capability_gap.render_section(gap_result))
    except Exception as e:  # never let the adopt half break the report
        lines.append(f"_capability gap analysis failed: {e}_")
        lines.append("")

    # Created issues
    if created_issues:
        lines.append("## 🐙 GitHub issues auto-created")
        lines.append("")
        for u in created_issues:
            lines.append(f"- {u}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="AIShield Tech Radar")
    ap.add_argument("--live", action="store_true",
                    help="Create GitHub issues for critical signals (default: dry-run)")
    ap.add_argument("--once", action="store_true",
                    help="Single pass (default: full run)")
    ap.add_argument("--days", type=int, default=7,
                    help="Look-back window in days (default: 7)")
    ap.add_argument("--sources", nargs="*",
                    choices=["github", "arxiv", "hn", "reddit", "standards", "platforms", "all"],
                    default=["all"],
                    help="Which sources to scan")
    ap.add_argument("--publish", action="store_true",
                    help="Auto-commit intel report + index to public main via Contents API")
    args = ap.parse_args()

    dry_run = not args.live
    sources = set(args.sources) if "all" not in args.sources else {
        "github", "arxiv", "hn", "reddit", "standards", "platforms"}

    _ensure_dirs()
    state = _load_state()
    seen_ids = set(state.get("seen_ids", []))
    pat = _pat()

    print(f"[radar] {_today_str()}  dry_run={dry_run}  sources={sorted(sources)}  "
          f"pat_present={bool(pat)}")

    all_signals = []
    errors = []

    def run(name, fn):
        print(f"[scan] {name} ...", end=" ", flush=True)
        t0 = time.time()
        try:
            out = fn()
            print(f"OK ({len(out)} items, {time.time()-t0:.1f}s)")
            return out
        except Exception as e:
            print(f"ERROR ({e})")
            return []

    if "github" in sources:
        sigs = run("github-trending", lambda: scan_github_trending(days=args.days))
        all_signals.extend(sigs)
    if "arxiv" in sources:
        sigs = run("arxiv", lambda: scan_arxiv(days=args.days))
        all_signals.extend(sigs)
    if "hn" in sources:
        sigs = run("hackernews", lambda: scan_hackernews(days=args.days))
        all_signals.extend(sigs)
    if "reddit" in sources:
        sigs = run("reddit", lambda: scan_reddit(days=args.days))
        all_signals.extend(sigs)
    if "standards" in sources:
        sigs = run("standards", lambda: scan_standards_orgs(pat))
        all_signals.extend(sigs)
    if "platforms" in sources:
        sigs = run("user-platforms", lambda: scan_user_platforms(pat))
        all_signals.extend(sigs)

    # split errors from valid signals
    valid = [s for s in all_signals if "id" in s]
    errors = [f"{s.get('_source','?')} :: {s.get('_kw') or s.get('_query') or s.get('_sub') or s.get('_org','?')} :: {s.get('_error')}"
              for s in all_signals if "_error" in s]

    # dedupe vs previous runs
    new_signals = [s for s in valid if s["id"] not in seen_ids]
    seen_ids.update(s["id"] for s in valid)
    # cap history to last 5000 ids
    state["seen_ids"] = list(seen_ids)[-5000:]

    # auto-draft rule candidates for high-severity NEW signals
    drafted_rules = []
    if not dry_run or True:  # always draft in both modes; user reviews regardless
        for sig in new_signals:
            cat, sev = classify_signal(sig)
            if cat and sev in ("high", "critical"):
                path = draft_rule_candidate(sig)
                if path:
                    drafted_rules.append(path)
    print(f"[draft] {len(drafted_rules)} rule stub(s) generated")

    # auto-create issues for critical NEW signals (only in --live)
    created_issues = []
    if not dry_run:
        for sig in new_signals:
            cat, sev = classify_signal(sig)
            if cat and sev == "critical":
                url = create_github_issue(pat, sig, cat, sev)
                if url:
                    created_issues.append(url)
                time.sleep(1.0)
        print(f"[issues] {len(created_issues)} issue(s) created")
    else:
        print("[issues] DRY-RUN -- no issues created")

    # render report -- use TODAY's full scan (valid), not the cross-run dedup
    # delta, so the public daily trail is always a faithful snapshot of what
    # the radar saw that day (dedup only gates issues/drafts, not the report).
    report = render_report(valid, drafted_rules, created_issues, errors)
    report_path = os.path.join(INTEL_DIR, f"{_today_str()}-tech-radar.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[report] {report_path}")

    # persist state
    state["last_signals"] = len(new_signals)
    state["last_drafted"] = len(drafted_rules)
    state["last_issues"] = len(created_issues)
    state["last_errors"] = len(errors)
    _save_state(state)

    # ---- publish loop (occupation): push report + rolling index to main ----
    if args.publish:
        if not pat:
            print("[publish] SKIPPED -- no PAT configured")
        else:
            idx_rel = _build_index()
            report_rel = os.path.relpath(report_path, ROOT).replace(os.sep, "/")
            targets = [report_rel, idx_rel]
            print(f"[publish] pushing {len(targets)} file(s) to {REPO}@main ...")
            for rel, ok, info in _publish(
                    targets, pat, f"chore(radar): publish {_today_str()} tech radar"):
                print(f"  [{'OK ' if ok else 'ERR'}] {rel} -> {info}")

    print(f"[done] new={len(new_signals)} drafted={len(drafted_rules)} "
          f"issues={len(created_issues)} errors={len(errors)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())