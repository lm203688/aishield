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
  - Zero third-party deps (stdlib + urllib only) -- matches the project.
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
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

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

def _http_json(url, headers=None, timeout=20):
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", "aishield-tech-radar/1.0")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return -1, {"_error": str(e)}

def _http_text(url, headers=None, timeout=20):
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", "aishield-tech-radar/1.0")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return -1, str(e)

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
    state["last_run"] = _now_utc().isoformat()
    state["runs"] = state.get("runs", 0) + 1
    open(STATE_FILE, "w", encoding="utf-8").write(
        json.dumps(state, ensure_ascii=False, indent=2)
    )

def _signal_id(sig):
    h = hashlib.sha1()
    h.update(json.dumps(sig, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()[:12]


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
def scan_arxiv(days=7, max_results=10):
    queries = [
        'all:"prompt injection" AND all:"agent"',
        'all:"jailbreak" AND all:"tool"',
        'all:"mcp" AND all:"security"',
        'all:"agentic" AND all:"attack"',
        'all:"model context protocol"',
    ]
    signals = []
    seen_ids = set()
    headers = {}

    # Cheap probe first: if arXiv is broadly broken today, skip the whole
    # source instead of burning ~100s on retries. arXiv has flaky days.
    probe_q = queries[0]
    probe_url = (
        "http://export.arxiv.org/api/query?"
        + urllib.parse.urlencode({
            "search_query": probe_q,
            "max_results": 1,
        }, quote_via=urllib.parse.quote)
    )
    ps, _ = _http_text(probe_url, headers=headers, timeout=15)
    if ps != 200:
        return [{
            "_source": "arxiv",
            "_query": "probe",
            "_error": f"arXiv probe failed HTTP {ps} -- skipping source (likely transient outage)",
        }]

    for q in queries:
        url = (
            "http://export.arxiv.org/api/query?"
            + urllib.parse.urlencode({
                "search_query": q,
                "start": 0,
                "max_results": max_results,
                "sortBy": "submittedDate",
                "sortOrder": "desc",
            }, quote_via=urllib.parse.quote)  # arXiv rejects %2B; need %20 for spaces
        )
        # arXiv is intermittently flaky -- retry on 5xx/timeout
        body = ""
        status = -1
        for attempt in range(2):
            status, body = _http_text(url, headers=headers, timeout=30)
            if status == 200:
                break
            time.sleep(2 * (attempt + 1))
        if status != 200 or not body:
            signals.append({"_source": "arxiv", "_query": q, "_error": f"HTTP {status}"})
            continue
        try:
            root = ET.fromstring(body)
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("a:entry", ns):
                eid = entry.findtext("a:id", default="", namespaces=ns)
                if eid in seen_ids:
                    continue
                seen_ids.add(eid)
                title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
                summary = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
                published = entry.findtext("a:published", default="", namespaces=ns)[:10]
                # filter: only include last 7 days
                try:
                    pub_dt = datetime.datetime.strptime(published, "%Y-%m-%d")
                    if (_now_utc() - pub_dt).days > days:
                        continue
                except Exception:
                    pass
                signals.append({
                    "_source": "arxiv",
                    "id": _signal_id({"arxiv": eid}),
                    "title": title[:200],
                    "summary": summary[:400],
                    "url": eid,
                    "published": published,
                    "query": q,
                })
        except ET.ParseError as e:
            signals.append({"_source": "arxiv", "_query": q, "_error": f"parse: {e}"})
        time.sleep(1.0)  # arXiv asks for politeness
    return signals


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
ATTACK_PATTERNS = [
    (r"prompt\s*injection",                "prompt-injection"),
    (r"tool\s*(poison|injection|use)",     "tool-poisoning"),
    (r"jailbreak",                         "jailbreak"),
    (r"rug\s*pull",                        "rug-pull"),
    (r"mcp\s*(poison|vuln|exploit)",       "mcp-attack"),
    (r"agent\s*(card\s*)?spoof",           "agent-spoof"),
    (r"credential\s*(exfil|leak|theft)",   "credential-theft"),
    (r"supply\s*chain",                    "supply-chain"),
]

def classify_signal(sig):
    """Return (category, severity) for a signal, or (None, None)."""
    text = " ".join(str(v) for v in sig.values() if isinstance(v, str)).lower()
    cats = [c for pat, c in ATTACK_PATTERNS if re.search(pat, text)]
    if not cats:
        return None, None
    # Heuristic: papers with "bypass" or "exploit" in title -> critical
    title = (sig.get("title") or "").lower()
    if any(k in title for k in ["bypass", "exploit", "rce", "remote code", "unauthenticated"]):
        return cats[0], "critical"
    if any(k in title for k in ["new attack", "first", "novel", "breaking"]):
        return cats[0], "high"
    return cats[0], "medium"


def is_critical(sig):
    cat, sev = classify_signal(sig)
    return sev == "critical"


# ---------------------------------------------------------------------------
# Auto-draft rule candidates
# ---------------------------------------------------------------------------
RULE_TEMPLATE = '''# -*- coding: utf-8 -*-
"""
Auto-drafted rule candidate -- PROPOSED, NOT ACTIVE.
====================================================

Generated by scripts/tech_radar.py on {date}
Source signal: {source_url}
Attack pattern: {attack_category}
Severity:       {severity}

Review instructions:
  1. Read the source signal (URL above) to understand the attack.
  2. Implement the `check()` method below with detection logic.
  3. Test against {source_kind} samples -- real positive AND real negative.
  4. If valid: move this file into scanner/rules.py and assign a permanent id.
     If false positive or out of scope: delete this file.

Original signal title:
  {signal_title}
"""
from __future__ import annotations
from scanner.rules import Rule, RuleResult


class ProposedRule_{slug}(Rule):
    id = "PROPOSED-{date_slug}-{slug}"
    description = "Detects {attack_category} per radar signal {signal_id}"
    severity = "{severity}"
    category = "{attack_category}"

    def check(self, manifest, content=""):
        # TODO(operator): implement detection logic based on source signal.
        # Suggested fields to inspect in `manifest`:
        #   - manifest.tools        (list of tool defs)
        #   - manifest.prompts      (list of prompt strings)
        #   - manifest.resources    (list of resource URIs)
        #   - manifest.config       (raw config dict)
        #   - content               (raw file content as string)
        # Return RuleResult(fired=True, reason="...") when detected.
        return RuleResult(fired=False, reason="draft -- implement check()")
'''


def _slugify(text):
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return (s[:30] or "rule")


def draft_rule_candidate(sig):
    """Generate a rule stub file for a high-severity signal. Return path or None."""
    cat, sev = classify_signal(sig)
    if not cat:
        return None
    slug = _slugify(sig.get("title", "rule")) + "_" + sig.get("id", "x")[:6]
    date = _today_str()
    date_slug = date.replace("-", "")
    fname = f"PROPOSED_{date_slug}_{slug}.py"
    fpath = os.path.join(PROPOSED_DIR, fname)
    body = RULE_TEMPLATE.format(
        date=date,
        date_slug=date_slug,
        slug=slug,
        source_url=sig.get("url", ""),
        source_kind=sig.get("_source", "unknown"),
        signal_id=sig.get("id", ""),
        signal_title=(sig.get("title") or "")[:120],
        attack_category=cat,
        severity=sev,
    )
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(body)
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
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/issues",
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
    )
    req.add_header("Authorization", f"Bearer {pat}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "aishield-tech-radar/1.0")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8") or "{}")
            return data.get("html_url")
    except Exception as e:
        print(f"  issue creation failed: {e}", file=sys.stderr)
        return None


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

    # Created issues
    if created_issues:
        lines.append("## 🐙 GitHub issues auto-created")
        lines.append("")
        for u in created_issues:
            lines.append(f"- {u}")
        lines.append("")

    # Actionable proposals (filled in by caller)
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

    # render report
    report = render_report(new_signals, drafted_rules, created_issues, errors)
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

    print(f"[done] new={len(new_signals)} drafted={len(drafted_rules)} "
          f"issues={len(created_issues)} errors={len(errors)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())