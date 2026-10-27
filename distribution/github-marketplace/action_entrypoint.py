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

⚠️ 同步纪律：本文件是主仓 `action_entrypoint.py` 的「独立 marketplace 发布副本」，
主逻辑必须与根版本一致（坏配置 exit 2 / 最高档 risk / output_format /
trust_attestation）。仅懒克隆加载逻辑是独立仓库专属，允许不同。
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

# 风险档权重（与根版本一致：info/safe=1，low=1，medium=2，high=3，critical=4）
RISK_ORDER = {"info": 1, "safe": 1, "low": 1, "medium": 2, "high": 3, "critical": 4}
ASSESSMENT_FALLBACK = {"danger": "high", "review": "medium"}
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


def _max_risk(*candidates):
    """取候选风险档中的最高档；空串/未知值按最低档处理。"""
    rank = {"": 0, "info": 1, "safe": 1, "low": 1, "medium": 2, "high": 3, "critical": 4}
    best, best_r = "safe", 1
    for c in candidates:
        c = (c or "").strip().lower()
        if rank.get(c, 0) > best_r:
            best, best_r = c, rank[c]
    return best


def verdict_from(report):
    s = report.get("summary", {})
    assess = (s.get("overall_assessment") or "safe").lower()
    # 风险档 = 引擎整体档 ∪ 逐条 finding 最高档 ∪ assessment 兜底，取最高者。
    # 旧实现只从三档 assessment 反推，risk 永远到不了 critical（fail_on: critical 永不触发）。
    risk = _max_risk(
        s.get("risk_level"),
        *((f.get("severity") or "") for f in (report.get("aggregate_findings") or [])),
        ASSESSMENT_FALLBACK.get(assess, "safe"),
    )
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


def _write_trust_attestation(report, score, risk):
    """生成带完整性锚点的扫描裁决（不是可独立验签的凭证）。

    审计 P0-6：哈希链能证明「记录后来没被悄悄改」，但不能单独证明「扫描结论
    真实」或「第三方能验证签发者」。故对外只称「带完整性锚点的扫描裁决」。
    """
    import hashlib
    s = report.get("summary", {}) or {}
    payload = {
        "schema": "https://aishield.tools/schemas/scan-adjudication-v1.json",
        "kind": "scan-adjudication",
        "score": score,
        "risk_level": risk,
        "assessment": s.get("overall_assessment", "n/a"),
        "items_total": s.get("items_total", 0),
        "items_high_risk": s.get("items_high_risk", 0),
        "items_medium_risk": s.get("items_medium_risk", 0),
        "scanner_version": report.get("scanner_version"),
        "scanned_at": report.get("scanned_at"),
        "findings_digest": hashlib.sha256(
            json.dumps(report.get("aggregate_findings") or [], ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()[:32],
    }
    payload["integrity_anchor"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    path = "aishield-trust-attestation.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path


def main():
    target, src_desc = resolve_target()
    tool_type = (os.environ.get("INPUT_TOOL_TYPE") or "mcp").strip() or "mcp"
    name = (os.environ.get("INPUT_NAME") or "").strip()
    fail_on = (os.environ.get("INPUT_FAIL_ON") or "high").strip().lower() or "high"
    enable_osv = str(os.environ.get("INPUT_ENABLE_OSV", "false")).strip().lower() == "true"
    output_format = (os.environ.get("INPUT_OUTPUT_FORMAT") or "sarif").strip().lower() or "sarif"
    include_attest = str(os.environ.get("INPUT_INCLUDE_TRUST_ATTESTATION", "false")).strip().lower() == "true"

    # 坏配置必须产生明确错误（exit 2），不能静默按默认值处理（审计 P0-2 判据）。
    valid_risk = sorted(set(RISK_ORDER) - {"safe"})
    if fail_on not in RISK_ORDER:
        sys.stderr.write(f"[error] fail_on='{fail_on}' 不是合法风险档（{valid_risk}）\n")
        return 2
    if output_format not in ("json", "sarif", "text"):
        sys.stderr.write(f"[error] output_format='{output_format}' 不是合法输出格式（json/sarif/text）\n")
        return 2

    sys.stdout.write(f"[aishield] scanning {src_desc} (tool_type={tool_type}, fail_on={fail_on}, "
                     f"osv={enable_osv}, format={output_format})\n")
    sys.stdout.flush()

    report = preflight(target)
    score, risk = verdict_from(report)

    with open("aishield-report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    sarif = build_sarif(report, report.get("scanner_version", "4.11.0"))
    with open("aishield.sarif", "w", encoding="utf-8") as fh:
        json.dump(sarif, fh, ensure_ascii=False, indent=2)

    trust_path = ""
    if include_attest:
        try:
            trust_path = _write_trust_attestation(report, score, risk)
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[warn] trust attestation 生成失败（{e}），继续发布扫描结果\n")

    out_path = os.environ.get("GITHUB_OUTPUT")
    if out_path:
        with open(out_path, "a", encoding="utf-8") as fh:
            fh.write(f"score={score}\n")
            fh.write(f"risk_level={risk}\n")
            fh.write(f"report={os.path.abspath('aishield-report.json')}\n")
            if output_format in ("sarif", "json"):
                fh.write(f"sarif={os.path.abspath('aishield.sarif')}\n")
            if trust_path:
                fh.write(f"trust_attestation={os.path.abspath(trust_path)}\n")

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
