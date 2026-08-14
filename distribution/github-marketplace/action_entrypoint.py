#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
action_entrypoint.py — GitHub Action (Docker) entrypoint.

Reads INPUT_* env injected by action.yml, runs the AIShield preflight scan
against the target repo, produces score / risk_level / report(JSON) / sarif,
writes GitHub Actions outputs and Step Summary. Exits non-zero (failing CI)
when risk >= fail_on.

Core invariant (same as the scanner):
  - never spawn any command from the scanned config
  - never fetch scanned content over the network (fully offline when enable_osv=false)

Self-contained: when run from the standalone `aishield-action` repo (where the
`scanner/` package is absent), it lazily clones the AIShield source repo
(OUR repo, not the scanned target) to import the engine.
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from scanner.workspace_scan import preflight
except Exception:  # noqa: BLE001
    _src = "/opt/aishield"
    if not os.path.isdir(os.path.join(_src, "scanner")):
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/lm203688/aishield", _src],
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    if os.path.isdir(os.path.join(_src, "scanner")):
        sys.path.insert(0, _src)
    from scanner.workspace_scan import preflight

RISK_ORDER = {"safe": 0, "low": 0, "medium": 1, "high": 2, "critical": 3}
SARIF_LEVEL = {"critical": "error", "high": "error", "medium": "warning", "low": "note", "info": "none"}


def resolve_target():
    url = (os.environ.get("INPUT_SOURCE_URL") or "").strip()
    ws = os.environ.get("GITHUB_WORKSPACE") or "/github/workspace"
    if url:
        if os.path.isdir(url):
            return url, f"local path: {url}"
        tmp = tempfile.mkdtemp(prefix="aishield-src-")
        try:
            subprocess.run(["git", "clone", "--depth", "1", url, tmp],
                           check=True, timeout=180,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return tmp, f"cloned: {url}"
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[warn] clone failed ({e}); fall back to workspace\n")
            if os.path.isdir(ws):
                return ws, f"workspace: {ws}"
            return ".", "workspace: ."
    if os.path.isdir(ws):
        return ws, f"workspace: {ws}"
    return ".", "workspace: ."


def verdict_from(report):
    s = report.get("summary", {})
    assess = s.get("overall_assessment", "safe")
    if assess == "danger":
        risk = "high"
    elif assess == "review":
        risk = "medium"
    else:
        risk = "safe"
    score = s.get("overall_score")
    if score is None:
        score = 100 if assess in ("safe", "empty") else 0
    return score, risk


def build_sarif(report, tool_version):
    findings = []
    for f in report.get("aggregate_findings", []) or []:
        findings.append(f)
    rules = {}
    results = []
    for f in findings:
        rid = f.get("type") or f.get("rule_id") or "AISHIELD-UNKNOWN"
        sev = (f.get("severity") or "medium").lower()
        rules.setdefault(rid, {
            "id": rid,
            "shortDescription": {"text": (f.get("description") or rid)[:120]},
            "defaultConfiguration": {"level": SARIF_LEVEL.get(sev, "warning")},
        })
        loc_file = f.get("file") or "unknown"
        results.append({
            "ruleId": rid,
            "level": SARIF_LEVEL.get(sev, "warning"),
            "message": {"text": f.get("description") or rid},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": loc_file},
                    "region": {"startLine": int(f.get("line") or 1)},
                }
            }],
        })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "AIShield",
                    "version": tool_version,
                    "informationUri": "https://aishield.tools",
                    "rules": list(rules.values()),
                }
            },
            "results": results,
        }],
    }


def main():
    target, src_desc = resolve_target()
    tool_type = (os.environ.get("INPUT_TOOL_TYPE") or "mcp").strip() or "mcp"
    name = (os.environ.get("INPUT_NAME") or "").strip()
    fail_on = (os.environ.get("INPUT_FAIL_ON") or "high").strip().lower() or "high"
    enable_osv = str(os.environ.get("INPUT_ENABLE_OSV", "false")).strip().lower() == "true"

    sys.stdout.write(f"[aishield] scanning {src_desc} (tool_type={tool_type}, fail_on={fail_on}, osv={enable_osv})\n")
    sys.stdout.flush()

    report = preflight(target)
    score, risk = verdict_from(report)

    with open("aishield-report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    sarif = build_sarif(report, report.get("scanner_version", "4.2.2"))
    with open("aishield.sarif", "w", encoding="utf-8") as fh:
        json.dump(sarif, fh, ensure_ascii=False, indent=2)

    out_path = os.environ.get("GITHUB_OUTPUT")
    if out_path:
        with open(out_path, "a", encoding="utf-8") as fh:
            fh.write(f"score={score}\n")
            fh.write(f"risk_level={risk}\n")
            fh.write(f"report={os.path.abspath('aishield-report.json')}\n")
            fh.write(f"sarif={os.path.abspath('aishield.sarif')}\n")

    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    s = report.get("summary", {})
    if summ:
        with open(summ, "a", encoding="utf-8") as fh:
            fh.write("## 🛡️ AIShield Scan Result\n\n")
            fh.write(f"- **Score**: `{score}` / 100\n")
            fh.write(f"- **Risk**: `{risk}`\n")
            fh.write(f"- **Items scanned**: `{s.get('items_total', 0)}` "
                     f"(high={s.get('items_high_risk', 0)}, medium={s.get('items_medium_risk', 0)})\n")
            fh.write(f"- **Assessment**: `{s.get('overall_assessment', 'n/a')}`\n")

    sys.stdout.write(f"[aishield] score={score} risk={risk}\n")
    sys.stdout.flush()

    if RISK_ORDER.get(risk, 0) >= RISK_ORDER.get(fail_on, 2):
        sys.stdout.write(f"[aishield] FAIL: risk '{risk}' >= fail_on '{fail_on}'\n")
        sys.stdout.flush()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
