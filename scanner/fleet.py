"""
scanner/fleet.py — Fleet 中心化安全态势聚合 (F5)

把多 server / 多工具的扫描结果汇聚成一个"机队(fleet)"视图：
  - ingest(scan_result):   收纳一次扫描结果，按 identity(source_url/name) 去重
  - summary():             机队级聚合（通过率、平均分、严重度分布、OWASP 覆盖、最差成员）
  - list_members():        列出所有已收纳成员及其最新评分

数据落 data/fleet.json（本地优先，零出网）。

这是 mcp-audit 没有的"集中式 fleet 看板"能力——企业安全团队用一套 UI 看全部 MCP/Agent 资产。
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone, timedelta
from collections import defaultdict

TZ = timezone(timedelta(hours=8))
_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
FLEET_FILE = os.path.join(_DATA_DIR, "fleet.json")
_lock = threading.Lock()

_SEV_ORDER = ["critical", "high", "medium", "low", "info"]
_PASS_SCORE = 70  # 与 policies/default.json 的 min_overall_score 对齐


def _now_iso():
    return datetime.now(TZ).isoformat()


def _sev_hist(findings) -> dict:
    hist = {s: 0 for s in _SEV_ORDER}
    for f in findings or []:
        s = (f.get("severity") or "info").lower()
        hist[s] = hist.get(s, 0) + 1
    return hist


def _owasp_hist(findings) -> dict:
    hist: dict[str, int] = defaultdict(int)
    for f in findings or []:
        cat = f.get("owasp_category") or "UNMAPPED"
        hist[cat] += 1
    return dict(hist)


def _identity(scan_result: dict) -> str:
    """成员唯一键：优先 source_url，其次 name，最后 report 指纹。"""
    return (scan_result.get("source_url")
            or scan_result.get("name")
            or scan_result.get("target_name")
            or scan_result.get("report", {}).get("source_url")
            or f"anon-{_now_iso()}")


class FleetService:
    """机队聚合服务（线程安全，本地 JSON 持久化）。"""

    def __init__(self, path: str = FLEET_FILE):
        self.path = path

    # ── 持久化 ──
    def _load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"members": {}, "updated_at": ""}

    def _save(self, data: dict):
        with _lock:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            data["updated_at"] = _now_iso()
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    # ── 收纳 ──
    def ingest(self, scan_result: dict) -> dict:
        """收纳一次扫描结果，更新对应成员。

        scan_result 约定字段（与 engine.scan 返回兼容）：
          source_url, name, overall_score, badge_level, risk_level,
          total_findings, findings[{severity, owasp_category}], report
        """
        if not isinstance(scan_result, dict):
            return {"success": False, "error": "scan_result must be an object"}
        ident = _identity(scan_result)
        report = scan_result.get("report", scan_result)
        findings = report.get("findings") or scan_result.get("findings") or []

        member = {
            "identity": ident,
            "source_url": scan_result.get("source_url") or report.get("source_url", ""),
            "name": scan_result.get("name") or report.get("name") or ident,
            "overall_score": int(scan_result.get("overall_score")
                                 or report.get("overall_score", 0)),
            "badge_level": scan_result.get("badge_level")
                           or report.get("badge_level", "none"),
            "risk_level": scan_result.get("risk_level")
                         or report.get("risk_level", "unknown"),
            "total_findings": int(scan_result.get("total_findings")
                                  or report.get("total_findings")
                                  or len(findings)),
            "severity_hist": _sev_hist(findings),
            "owasp_hist": _owasp_hist(findings),
            "ingested_at": _now_iso(),
            "pass": (scan_result.get("overall_score")
                     or report.get("overall_score", 0)) >= _PASS_SCORE,
        }

        data = self._load()
        data.setdefault("members", {})[ident] = member
        self._save(data)
        return {"success": True, "member": member, "fleet_size": len(data["members"])}

    def list_members(self) -> list:
        data = self._load()
        return list(data.get("members", {}).values())

    def summary(self) -> dict:
        """机队级聚合视图。"""
        members = self.list_members()
        if not members:
            return {
                "total": 0, "pass": 0, "fail": 0,
                "avg_score": 0, "severity_hist": {s: 0 for s in _SEV_ORDER},
                "owasp_hist": {}, "score_buckets": {},
                "worst_offenders": [], "updated_at": "",
            }

        sev = {s: 0 for s in _SEV_ORDER}
        owasp: dict[str, int] = defaultdict(int)
        total_score = 0
        passed = 0
        buckets = {"0-49": 0, "50-69": 0, "70-89": 0, "90-100": 0}
        for m in members:
            total_score += m["overall_score"]
            if m["pass"]:
                passed += 1
            for s, c in (m.get("severity_hist") or {}).items():
                sev[s] = sev.get(s, 0) + c
            for cat, c in (m.get("owasp_hist") or {}).items():
                owasp[cat] += c
            sc = m["overall_score"]
            if sc < 50:
                buckets["0-49"] += 1
            elif sc < 70:
                buckets["50-69"] += 1
            elif sc < 90:
                buckets["70-89"] += 1
            else:
                buckets["90-100"] += 1

        worst = sorted(members, key=lambda x: x["overall_score"])[:5]

        return {
            "total": len(members),
            "pass": passed,
            "fail": len(members) - passed,
            "pass_rate": round(passed / len(members) * 100, 1),
            "avg_score": round(total_score / len(members), 1),
            "severity_hist": sev,
            "owasp_hist": dict(owasp),
            "score_buckets": buckets,
            "worst_offenders": [
                {"identity": w["identity"], "name": w["name"],
                 "overall_score": w["overall_score"], "risk_level": w["risk_level"]}
                for w in worst
            ],
            "updated_at": self._load().get("updated_at", ""),
        }

    def reset(self):
        self._save({"members": {}, "updated_at": _now_iso()})


# 便捷函数（与 scanner 包风格的模块级 API 对齐）
_default = FleetService()


def ingest(scan_result):
    return _default.ingest(scan_result)


def summary():
    return _default.summary()


def list_members():
    return _default.list_members()


def reset():
    _default.reset()


if __name__ == "__main__":
    svc = FleetService()
    svc.reset()
    svc.ingest({"source_url": "https://github.com/a/x", "overall_score": 92,
                "badge_level": "gold", "risk_level": "safe", "total_findings": 0,
                "findings": []})
    svc.ingest({"source_url": "https://github.com/a/y", "overall_score": 45,
                "badge_level": "none", "risk_level": "high", "total_findings": 3,
                "findings": [{"severity": "critical", "owasp_category": "MCP03"},
                             {"severity": "high", "owasp_category": "MCP03"},
                             {"severity": "medium", "owasp_category": "MCP08"}]})
    print(json.dumps(svc.summary(), ensure_ascii=False, indent=2))
