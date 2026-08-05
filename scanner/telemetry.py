"""
AIShield 匿名遥测 (D4) — 隐私优先的数据飞轮起点

设计红线：
  - 默认关闭。必须显式 AISHIELD_TELEMETRY=1 才记录。
  - 零 PII：绝不记录 source_url、server 名、依赖名、代码片段、IP。
  - 仅记录聚合信号：分数桶、规则覆盖、findings 计数、能力类型、时间桶。
  - 本地落盘于 data/telemetry.jsonl（追加），不上云；可由用户随时清空。
"""
from __future__ import annotations

import os
import json
import time
import math

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
TELEMETRY_FILE = os.path.join(DATA_DIR, "telemetry.jsonl")

ENABLED = os.environ.get("AISHIELD_TELEMETRY") == "1"


def _bucket_score(score: int) -> str:
    if score >= 85:
        return "85-100"
    if score >= 70:
        return "70-84"
    if score >= 55:
        return "55-69"
    if score >= 40:
        return "40-54"
    return "0-39"


def record_scan(report: dict, source: str = "cli") -> dict | None:
    """
    记录一次扫描的聚合信号。返回写入的记录（关闭时返回 None）。

    Args:
        report: engine.scan() 输出（仅读取聚合字段，不读 PII）
        source: 调用来源（cli / api / mcp）
    """
    if not ENABLED:
        return None

    findings = report.get("findings", []) or []
    sev_counts: dict[str, int] = {}
    cap_hits: dict[str, int] = {}
    for f in findings:
        sev = f.get("severity", "info")
        sev_counts[sev] = sev_counts.get(sev, 0) + 1
        cat = f.get("owasp_category")
        if cat:
            cap_hits[cat] = cap_hits.get(cat, 0) + 1

    # 时间桶（按小时，避免精确时间戳）
    hour_bucket = time.strftime("%Y-%m-%dT%H", time.gmtime())

    record = {
        "v": 1,
        "hour": hour_bucket,
        "source": source,
        "score_bucket": _bucket_score(report.get("overall_score", 0)),
        "overall_score": report.get("overall_score", 0),
        "dimensions": {
            "security": report.get("security_score"),
            "permissions": report.get("permissions_score"),
            "data": report.get("data_handling_score"),
            "supply": report.get("supply_chain_score"),
            "reliability": report.get("reliability_score"),
        },
        "sev_counts": sev_counts,
        "owasp_coverage": report.get("owasp_coverage", {}),
        "agentic_coverage": report.get("agentic_coverage", {}),
        "total_findings": len(findings),
        "rules_count": report.get("rules_count"),
        "tool_type": report.get("tool_type"),
    }

    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(TELEMETRY_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        return None
    return record


def get_aggregates() -> dict:
    """读取本地遥测并聚合（无数据时返回空聚合）。"""
    if not os.path.exists(TELEMETRY_FILE):
        return {"enabled": ENABLED, "samples": 0, "score_distribution": {},
                "total_findings": 0, "sev_distribution": {}, "owasp_hits": {}}
    score_dist: dict[str, int] = {}
    sev_dist: dict[str, int] = {}
    owasp: dict[str, int] = {}
    total_findings = 0
    samples = 0
    try:
        with open(TELEMETRY_FILE, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                samples += 1
                score_dist[r.get("score_bucket", "?")] = score_dist.get(r.get("score_bucket", "?"), 0) + 1
                total_findings += r.get("total_findings", 0)
                for s, c in (r.get("sev_counts") or {}).items():
                    sev_dist[s] = sev_dist.get(s, 0) + c
                for o, c in (r.get("owasp_coverage") or {}).items():
                    if c:
                        owasp[o] = owasp.get(o, 0) + 1
    except OSError:
        pass
    return {"enabled": ENABLED, "samples": samples, "score_distribution": score_dist,
            "total_findings": total_findings, "sev_distribution": sev_dist,
            "owasp_hits": owasp}


def reset() -> int:
    """清空本地遥测，返回删除的行数。"""
    if not os.path.exists(TELEMETRY_FILE):
        return 0
    try:
        with open(TELEMETRY_FILE, "r", encoding="utf-8") as fh:
            n = sum(1 for _ in fh)
        os.remove(TELEMETRY_FILE)
        return n
    except OSError:
        return 0
