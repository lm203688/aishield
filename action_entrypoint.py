#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
action_entrypoint.py — GitHub Action (Docker) 入口

读取 action.yml 注入的 INPUT_* 环境变量，对目标仓库跑 AIShield 预扫，
产出 score / risk_level / report(JSON) / sarif，并写 GitHub Actions 输出与
Step Summary。达到 fail_on 阈值则非零退出，使 CI 失败。

核心不变量（与扫描器同源）：
  - 绝不 spawn 被扫配置里的任何命令
  - 绝不联网抓取被扫内容（enable_osv=false 时完全离线）
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scanner.workspace_scan import preflight, SCANNER_VERSION

# 风险档权重，用于 fail_on 阈值比较。
RISK_ORDER = {"info": 1, "safe": 1, "low": 1, "medium": 2, "high": 3, "critical": 4}
# 三档 assessment 只能作兜底反推，不得作为唯一来源（见 verdict_from）。
ASSESSMENT_FALLBACK = {"danger": "high", "review": "medium"}
SARIF_LEVEL = {"critical": "error", "high": "error", "medium": "warning", "low": "note", "info": "none"}


def resolve_target():
    url = (os.environ.get("INPUT_SOURCE_URL") or "").strip()
    ws = os.environ.get("GITHUB_WORKSPACE") or "/github/workspace"
    if url:
        if os.path.isdir(url):
            return url, f"local path: {url}"
        # 视为 git URL，尝试浅克隆（离线场景会失败，则回退到挂载工作区）
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
    #
    # 旧实现只从三档 assessment 反推（danger->high / review->medium / 其余->safe），
    # 于是 risk 永远到不了 critical —— 用户写 `fail_on: critical` 期望拿到更宽松的门禁，
    # 实际拿到的是一个永不触发的门禁（RISK_ORDER[high] < RISK_ORDER[critical]，
    # 而 risk 恒为 safe/medium/high）。取最高档后单调只升不降，既修好 critical 档，
    # 又保留「有 danger 就至少 high」的原有语义。
    risk = _max_risk(
        s.get("risk_level"),
        *( (f.get("severity") or "") for f in (report.get("aggregate_findings") or []) ),
        ASSESSMENT_FALLBACK.get(assess, "safe"),
    )

    score = s.get("overall_score")
    if score is None:
        score = 100 if assess in ("safe", "empty") else 0
    return score, risk


def build_sarif(report, tool_version):
    findings = []
    for grp in ("aggregate_findings",):
        for f in report.get(grp, []) or []:
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
    sarif = {
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
    return sarif


def _write_trust_attestation(report, score, risk):
    """生成带完整性锚点的扫描裁决（不是可独立验签的凭证）。

    审计 P0-6 明确：哈希链能证明「记录后来没被悄悄改」，但不能单独证明
    「扫描结论真实」或「第三方能验证签发者」。故对外只能称「带完整性锚点的
    扫描裁决」，直到实现独立验签/密钥轮换/撤销/时间语义后才改称「可验证凭证」。
    本函数用扫描报告自身的规范化摘要作为锚点，不声称任何签名。
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

    # 坏配置必须产生明确错误（退出码 2），不能静默按默认值处理 ——
    # 否则用户以为在收紧门禁（fail_on: critical），实际拿到的仍是 high。
    # 审计 P0「坏配置产生明确错误」判据。
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

    try:
        report = preflight(target)
    except Exception as e:  # noqa: BLE001
        # 审计 P0-3 fail-closed：preflight 抛异常 = 扫描不完整（exit 3），
        # 绝不写成 0 findings / safe。
        sys.stderr.write(f"[error] preflight 失败：{e}\n")
        with open("aishield-report.json", "w", encoding="utf-8") as fh:
            json.dump({"error": f"preflight failed: {e}", "risk_level": "unknown",
                       "overall_score": 0, "total_findings": 0,
                       "scanner_version": SCANNER_VERSION}, fh, ensure_ascii=False, indent=2)
        return 3
    score, risk = verdict_from(report)

    # 写 JSON 报告（sarif/text 也写 JSON，JSON 是事实源；text 只省 SARIF）
    with open("aishield-report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    # 写 SARIF —— 版本取自引擎自身常量，不用硬编码兜底串。
    # 旧代码把兜底版本号写死在调用点里，而报告里的 scanner_version 实际是
    # 4.0-preflight.3、包版本是 4.3.0：SARIF 会盖上一个不存在的版本号，
    # 正是版本门禁要防的那类漂移。
    sarif = build_sarif(report, report.get("scanner_version") or SCANNER_VERSION)
    with open("aishield.sarif", "w", encoding="utf-8") as fh:
        json.dump(sarif, fh, ensure_ascii=False, indent=2)

    # 带完整性锚点的扫描裁决（用户显式开启才生成；未生成时不写 GITHUB_OUTPUT 键）
    trust_path = ""
    if include_attest:
        try:
            trust_path = _write_trust_attestation(report, score, risk)
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[warn] trust attestation 生成失败（{e}），继续发布扫描结果\n")

    # GitHub Actions 输出
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

    # Step Summary
    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    s = report.get("summary", {})
    if summ:
        with open(summ, "a", encoding="utf-8") as fh:
            fh.write(f"## 🛡️ AIShield Scan Result\n\n")
            fh.write(f"- **Score**: `{score}` / 100\n")
            fh.write(f"- **Risk**: `{risk}`\n")
            fh.write(f"- **Items scanned**: `{s.get('items_total', 0)}` "
                     f"(high={s.get('items_high_risk', 0)}, medium={s.get('items_medium_risk', 0)})\n")
            fh.write(f"- **Assessment**: `{s.get('overall_assessment', 'n/a')}`\n")

    sys.stdout.write(f"[aishield] score={score} risk={risk}\n")
    sys.stdout.flush()

    # 审计 P0-3 统一退出码：关键分析器失败（analyzer_status 含 failed）→ 3（不完整），
    # 即使分数显示 safe 也不能把「没能分析」伪装成「没有发现风险」。
    # preflight 报告通常走 workspace_scan 流水线，不一定带 analyzer_status；
    # 若带且有关键失败，按 exit 3 处理。
    try:
        from scanner.engine import analyzer_failures
        ast = report.get("analyzer_status") or {}
        if analyzer_failures(ast):
            sys.stdout.write(f"[aishield] INCOMPLETE: 关键分析器失败 {analyzer_failures(ast)}\n")
            sys.stdout.flush()
            return 3
    except Exception:  # noqa: BLE001  # 兼容：无 analyzer_status 时走阈值
        pass

    if RISK_ORDER.get(risk, 0) >= RISK_ORDER.get(fail_on, 2):
        sys.stdout.write(f"[aishield] FAIL: risk '{risk}' >= fail_on '{fail_on}'\n")
        sys.stdout.flush()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
