#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield · Rule Promotion Gate
==============================

Closes the last link of the Tech Radar loop:

    signal -> draft candidate -> [THIS GATE] -> live detection rule

`scripts/tech_radar.py` drafts candidates into `scanner/_proposed/*.json`.
Without a gate those drafts either rot in place or get hand-copied into
`scanner/rules.py` with no verification -- which is how a scanner acquires
false positives and loses the trust it sells.

This tool refuses to promote anything that fails:

  1. schema      -- required fields present, status == "ready"
  2. no TODOs    -- every placeholder actually filled in
  3. regex       -- each pattern compiles
  4. not-too-broad -- pattern must not match trivial/empty strings
  5. duplicate   -- pattern not already in the live rule set
  6. benign corpus -- ZERO matches against known-good samples
                      (a rule that fires on benign input is worse than no rule)

Promoted rules land in `data/radar_rules.json`, loaded by scanner/rules.py at
import time. Deliberately a separate file from `data/generated_rules.json`,
which `intel_to_rules.py` regenerates wholesale and would otherwise erase
radar-promoted rules on its next run.

Usage:
  python scripts/promote_rule.py --check                # validate all drafts
  python scripts/promote_rule.py --promote <file.json>  # promote one
  python scripts/promote_rule.py --promote-all          # promote every "ready"
  python scripts/promote_rule.py --list                 # show live radar rules
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROPOSED_DIR = os.path.join(ROOT, "scanner", "_proposed")
RADAR_RULES = os.path.join(ROOT, "data", "radar_rules.json")

VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}

# Strings a correct rule must never fire on. Kept deliberately mundane: these
# are the shapes of real MCP configs and ordinary source files.
BENIGN_CORPUS = [
    '{"mcpServers": {"filesystem": {"command": "npx", "args": ["-y", '
    '"@modelcontextprotocol/server-filesystem", "/tmp"]}}}',
    '{"name": "weather", "description": "Get the current weather for a city.", '
    '"inputSchema": {"type": "object", "properties": {"city": {"type": "string"}}}}',
    "def add(a: int, b: int) -> int:\n    \"\"\"Return the sum of two numbers.\"\"\"\n    return a + b\n",
    "# README\n\nThis MCP server exposes read-only access to a SQLite database.\n"
    "Install with `npm install` and run `npm start`.\n",
    "import os\nimport json\n\nCONFIG = os.environ.get('CONFIG_PATH', './config.json')\n",
    "这是一个用于查询天气的工具，输入城市名称即可返回当前温度和湿度。",
    "本服务器提供只读的文件列表能力，不会修改或删除任何文件。",
    '{"tools": [{"name": "search", "description": "搜索知识库中的文档"}]}',
    "const server = new Server({name: 'demo', version: '1.0.0'});\nserver.start();\n",
    "logger.info('request completed in %d ms', elapsed)\n",
]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_candidates():
    out = []
    for p in sorted(glob.glob(os.path.join(PROPOSED_DIR, "PROPOSED_*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                out.append((p, json.load(f)))
        except Exception as e:
            out.append((p, {"_parse_error": str(e)}))
    return out


def load_radar_rules():
    if not os.path.exists(RADAR_RULES):
        return {"version": 1, "rules": {}, "provenance": {}}
    try:
        with open(RADAR_RULES, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": 1, "rules": {}, "provenance": {}}


def live_patterns():
    """Every pattern already active, so we never promote a duplicate."""
    pats = set(load_radar_rules().get("rules", {}))
    try:
        sys.path.insert(0, ROOT)
        from scanner import rules as scanner_rules  # noqa: WPS433
        pats |= set(getattr(scanner_rules, "ALL_RULES", {}))
    except Exception:
        pass  # validation still works without the live set
    return pats


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate(path, data, known_patterns=None):
    """Return (ok: bool, problems: list[str])."""
    problems = []
    name = os.path.basename(path)

    if "_parse_error" in data:
        return False, [f"{name}: invalid JSON -- {data['_parse_error']}"]

    status = data.get("status")
    if status != "ready":
        return False, [f"{name}: status is '{status}', expected 'ready' "
                       f"(fill in the rules, then flip the flag)"]

    for field in ("signal", "attack_category", "rules"):
        if not data.get(field):
            problems.append(f"{name}: missing required field '{field}'")
    if problems:
        return False, problems

    rules = data.get("rules") or []
    if not isinstance(rules, list) or not rules:
        return False, [f"{name}: 'rules' must be a non-empty list"]

    known = known_patterns if known_patterns is not None else live_patterns()

    for i, r in enumerate(rules):
        tag = f"{name}[{i}]"
        pattern = (r.get("pattern") or "").strip()
        desc = (r.get("description") or "").strip()
        sev = (r.get("severity") or "").strip().lower()

        if not pattern or pattern.upper().startswith("TODO"):
            problems.append(f"{tag}: pattern still a TODO placeholder")
            continue
        if not desc or desc.upper().startswith("TODO"):
            problems.append(f"{tag}: description still a TODO placeholder")
        if sev not in VALID_SEVERITIES:
            problems.append(f"{tag}: severity '{sev}' not in {sorted(VALID_SEVERITIES)}")

        try:
            compiled = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            problems.append(f"{tag}: regex does not compile -- {e}")
            continue

        # Guard against catastrophically broad patterns.
        if compiled.search("") or compiled.search("a"):
            problems.append(f"{tag}: pattern matches empty/trivial input -- too broad")
            continue
        if len(pattern) < 6:
            problems.append(f"{tag}: pattern suspiciously short ({len(pattern)} chars)")

        if pattern in known:
            problems.append(f"{tag}: duplicate -- pattern already active")

        # The decisive test: must not fire on known-good input.
        for j, sample in enumerate(BENIGN_CORPUS):
            if compiled.search(sample):
                problems.append(
                    f"{tag}: FALSE POSITIVE on benign sample #{j} -- "
                    f"matched {compiled.search(sample).group()[:60]!r}"
                )
                break

    return (not problems), problems


# ---------------------------------------------------------------------------
# Promotion
# ---------------------------------------------------------------------------
def promote(path, data):
    store = load_radar_rules()
    store.setdefault("rules", {})
    store.setdefault("provenance", {})

    added = 0
    for r in data["rules"]:
        pattern = r["pattern"].strip()
        store["rules"][pattern] = [
            r["description"].strip(),
            r["severity"].strip().lower(),
        ]
        store["provenance"][pattern] = {
            "signal_title": (data.get("signal") or {}).get("title", ""),
            "signal_url": (data.get("signal") or {}).get("url", ""),
            "source": (data.get("signal") or {}).get("source", ""),
            "attack_category": data.get("attack_category", ""),
            "promoted_from": os.path.basename(path),
            "drafted_at": data.get("drafted_at", ""),
        }
        added += 1

    os.makedirs(os.path.dirname(RADAR_RULES), exist_ok=True)
    with open(RADAR_RULES, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

    # Archive the candidate so the queue reflects only outstanding work.
    done_dir = os.path.join(PROPOSED_DIR, "promoted")
    os.makedirs(done_dir, exist_ok=True)
    os.replace(path, os.path.join(done_dir, os.path.basename(path)))

    sync_readme_counts()
    return added


# ---------------------------------------------------------------------------
# Keep published docs honest
# ---------------------------------------------------------------------------
def sync_readme_counts():
    """Rewrite the rule totals in mcp-server/README.md to the live values.

    That README is the npmjs.com package page -- the first thing a user reads.
    `tests/test_mcp_contract.py` binds its numbers to the engine, so promoting
    a rule without updating it turns CI red. Doing it here means the docs can
    never drift behind a promotion.
    """
    readme = os.path.join(ROOT, "mcp-server", "README.md")
    if not os.path.exists(readme):
        return False
    try:
        sys.path.insert(0, ROOT)
        from scanner import rules as scanner_rules
        mcp_n = scanner_rules.get_rule_count("mcp")
        skill_n = scanner_rules.get_rule_count("skill")
    except Exception as e:
        print(f"  warning: could not read live rule counts ({e}); "
              f"update mcp-server/README.md by hand")
        return False

    with open(readme, encoding="utf-8") as f:
        text = f.read()

    new_text, n = re.subn(
        r"\*\*Total:\s*\d+\s*rules\*\*\s*\(MCP type\)\s*/\s*\*\*\d+\s*rules\*\*\s*\(Skill type\)",
        f"**Total: {mcp_n} rules** (MCP type) / **{skill_n} rules** (Skill type)",
        text,
    )
    if n and new_text != text:
        with open(readme, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"  synced mcp-server/README.md -> {mcp_n} MCP / {skill_n} Skill rules")
        return True
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def cmd_check():
    cands = load_candidates()
    if not cands:
        print("no candidates in scanner/_proposed/")
        return 0

    known = live_patterns()
    ready, blocked, drafts = [], [], []
    for path, data in cands:
        ok, problems = validate(path, data, known)
        if ok:
            ready.append(path)
        elif len(problems) == 1 and "expected 'ready'" in problems[0]:
            drafts.append(path)
        else:
            blocked.append((path, problems))

    print(f"candidates: {len(cands)}  |  ready: {len(ready)}  "
          f"blocked: {len(blocked)}  awaiting-authoring: {len(drafts)}")

    if ready:
        print("\nREADY to promote:")
        for p in ready:
            print(f"  + {os.path.basename(p)}")
    if blocked:
        print("\nBLOCKED:")
        for p, probs in blocked:
            for msg in probs:
                print(f"  - {msg}")
    if drafts:
        print("\nAwaiting authoring (status != ready):")
        for p in drafts:
            print(f"  . {os.path.basename(p)}")

    return 1 if blocked else 0


def cmd_promote(target):
    path = target if os.path.isabs(target) else os.path.join(PROPOSED_DIR, target)
    if not os.path.exists(path):
        print(f"not found: {path}")
        return 1
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    ok, problems = validate(path, data)
    if not ok:
        print("REFUSED -- candidate failed validation:")
        for msg in problems:
            print(f"  - {msg}")
        return 1
    n = promote(path, data)
    print(f"promoted {n} rule(s) from {os.path.basename(path)} -> data/radar_rules.json")
    return 0


def cmd_promote_all():
    known = live_patterns()
    promoted = 0
    for path, data in load_candidates():
        ok, _ = validate(path, data, known)
        if ok:
            promoted += promote(path, data)
            known |= {r["pattern"].strip() for r in data["rules"]}
    print(f"promoted {promoted} rule(s)")
    return 0


def cmd_list():
    store = load_radar_rules()
    rules = store.get("rules", {})
    if not rules:
        print("no radar-promoted rules yet")
        return 0
    print(f"{len(rules)} radar-promoted rule(s) in data/radar_rules.json:\n")
    for pattern, (desc, sev) in rules.items():
        prov = store.get("provenance", {}).get(pattern, {})
        print(f"  [{sev:8s}] {desc}")
        print(f"             pattern: {pattern}")
        if prov.get("signal_url"):
            print(f"             source:  {prov['signal_url']}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="AIShield rule promotion gate")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="Validate all candidates")
    g.add_argument("--promote", metavar="FILE", help="Promote one candidate")
    g.add_argument("--promote-all", action="store_true",
                   help="Promote every candidate that passes validation")
    g.add_argument("--list", action="store_true", help="List promoted radar rules")
    args = ap.parse_args()

    if args.check:
        return cmd_check()
    if args.promote:
        return cmd_promote(args.promote)
    if args.promote_all:
        return cmd_promote_all()
    if args.list:
        return cmd_list()
    return 0


if __name__ == "__main__":
    sys.exit(main())
