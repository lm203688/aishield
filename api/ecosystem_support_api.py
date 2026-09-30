# -*- coding: utf-8 -*-
"""
Agent 生态支持体系 API（2026-09-30 引入 · 战略转向落地）

背景
----
AIShield 从"agent 安全扫描器"演进到"agent 生态支持体系基础设施"。5 项
硬骨头模块（Agent Memory 深度扫描 / confidence 规则晋升 / 独立 rule decay /
Policy Pack / Red-team probe）此前只在 CLI / test 层暴露，本模块把它们
统一装进 REST API，供 MCP server 与外部消费者调用。

端点总览（前缀 /api/v1/eco-support）
-------------------------------------
GET  /policy-packs                       列出所有内置策略包
GET  /policy-packs/{name}                获取策略包详情
POST /policy-apply                       用策略包过滤一份扫描报告
GET  /red-team-probes                    列出所有 red-team 探针
POST /red-team-probe                     执行探针集（默认走 scanner.rules 引擎）
GET  /red-team-probe/coverage            OWASP 覆盖矩阵报告
POST /agent-memory-scan                  Agent Memory 深度扫描（8 框架 + 4 品类）
POST /confidence-promotion               规则 confidence 晋升检查
GET  /rule-decay                         规则衰减状态报告
POST /rule-decay/retire                  执行规则退役（改 radar_rules.json）

纪律
----
* 纯静态、零依赖、离线可跑；不 spawn、不联网。
* fail-closed：所有异常 → 500 + 明确 error 字段，绝不静默吞掉。
* 与 scanner/policy_pack.py 等模块解耦 —— 本层只做路由与形状转换，
  策略语义完全由底层模块承担。
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
from typing import Any, Dict, List, Tuple

# 项目根加入 sys.path，确保能 import scanner/scripts
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ── 内部依赖延迟 import（本文件被 server 惰性 import，避免影响启动）─────────

def _import_scanner():
    from scanner import agent_memory_scan, policy_pack, red_team_probe
    return agent_memory_scan, policy_pack, red_team_probe


def _import_scripts():
    from scripts import confidence_promotion, rule_decay
    return confidence_promotion, rule_decay


# ════════════════════════════════════════════════════════════════════════════
# 路由分发
# ════════════════════════════════════════════════════════════════════════════

def handle_get(path: str, query: dict) -> Tuple[Any, int]:
    """处理 GET /api/v1/eco-support/*。"""
    # 剥前缀
    prefix = "/api/v1/eco-support/"
    sub = path[len(prefix):] if path.startswith(prefix) else path.strip("/")

    try:
        if sub == "policy-packs":
            return _list_policy_packs(), 200
        if sub.startswith("policy-packs/"):
            name = urllib.parse.unquote(sub[len("policy-packs/"):])
            return _get_policy_pack(name)
        if sub == "red-team-probes":
            return _list_red_team_probes(), 200
        if sub == "red-team-probe/coverage":
            return _red_team_coverage(), 200
        if sub == "rule-decay":
            return _rule_decay_state(), 200
        if sub == "summary":
            return _overview(), 200
        return {"error": f"unknown endpoint: {path}"}, 404
    except KeyError as e:
        return {"error": f"not found: {e}"}, 404
    except Exception as e:
        return {"error": str(e), "trace": _safe_trace(e)}, 500


def handle_post(path: str, data: Dict[str, Any]) -> Tuple[Any, int]:
    """处理 POST /api/v1/eco-support/*。"""
    prefix = "/api/v1/eco-support/"
    sub = path[len(prefix):] if path.startswith(prefix) else path.strip("/")

    if not isinstance(data, dict):
        data = {}

    try:
        if sub == "agent-memory-scan":
            return _agent_memory_scan(data)
        if sub == "policy-apply":
            return _policy_apply(data)
        if sub in ("red-team-probe", "red-team-probe/run"):
            return _run_red_team_probes(data)
        if sub == "confidence-promotion":
            return _confidence_promotion(data)
        if sub == "rule-decay/retire":
            return _rule_decay_retire(data)
        if sub == "rule-decay/snapshot":
            return _rule_decay_snapshot(data)
        return {"error": f"unknown endpoint: {path}"}, 404
    except KeyError as e:
        return {"error": f"not found: {e}"}, 404
    except Exception as e:
        return {"error": str(e), "trace": _safe_trace(e)}, 500


# ════════════════════════════════════════════════════════════════════════════
# Handlers
# ════════════════════════════════════════════════════════════════════════════

def _overview() -> Dict[str, Any]:
    _, policy_pack, red_team_probe = _import_scanner()
    confidence_promotion, _ = _import_scripts()
    packs = policy_pack.list_packs()
    probes = red_team_probe.list_probes()
    return {
        "service": "AIShield Ecosystem Support",
        "version": "1.0.0",
        "description": (
            "Agent 生态支持体系基础设施 —— Agent Memory 深度扫描 / confidence 晋升 / "
            "rule decay / Policy Pack / Red-team probe 五模块统一 API"
        ),
        "capabilities": {
            "agent_memory_scan": {
                "frameworks": 8,
                "attack_categories": 4,
                "endpoint": "POST /api/v1/eco-support/agent-memory-scan",
            },
            "policy_packs": {
                "builtin_count": len(packs),
                "names": packs,
                "list_endpoint": "GET /api/v1/eco-support/policy-packs",
                "apply_endpoint": "POST /api/v1/eco-support/policy-apply",
            },
            "red_team_probes": {
                "probe_count": len(probes),
                "coverage": "OWASP MCP Top 10 + Agentic AI Top 10",
                "run_endpoint": "POST /api/v1/eco-support/red-team-probe",
                "coverage_endpoint": "GET /api/v1/eco-support/red-team-probe/coverage",
            },
            "confidence_promotion": {
                "thresholds": {
                    "seed": confidence_promotion.SEED_THRESHOLD,
                    "draft": confidence_promotion.DRAFT_THRESHOLD,
                    "rule": confidence_promotion.RULE_THRESHOLD,
                    "stale_days": confidence_promotion.STALE_DAYS,
                    "dead_days": confidence_promotion.DEAD_DAYS,
                },
                "endpoint": "POST /api/v1/eco-support/confidence-promotion",
            },
            "rule_decay": {
                "dormant_window_days": 14,
                "retire_window_days": 30,
                "state_endpoint": "GET /api/v1/eco-support/rule-decay",
                "retire_endpoint": "POST /api/v1/eco-support/rule-decay/retire",
            },
        },
        "principles": [
            "纯静态零依赖离线可跑",
            "不 spawn 任何命令、不联网",
            "fail-closed：异常明确返回，绝不静默",
            "OWASP MCP Top 10 + Agentic AI Top 10 双维对齐",
        ],
    }


def _list_policy_packs() -> Dict[str, Any]:
    _, policy_pack, _ = _import_scanner()
    names = policy_pack.list_packs()
    packs = {}
    for n in names:
        try:
            packs[n] = policy_pack.load_pack(n)
        except Exception as e:
            packs[n] = {"error": str(e)}
    return {"count": len(names), "packs": packs}


def _get_policy_pack(name: str) -> Tuple[Dict[str, Any], int]:
    _, policy_pack, _ = _import_scanner()
    pack = policy_pack.load_pack(name)
    return {"name": name, "pack": pack}, 200


def _policy_apply(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    _, policy_pack, _ = _import_scanner()
    pack_name = data.get("pack_name") or data.get("pack") or "default"
    report = data.get("report")
    if report is None:
        # 允许传 findings 数组作为简写
        findings = data.get("findings")
        if findings is not None:
            report = {"findings": findings, "overall_score": data.get("overall_score", 100)}
    if report is None:
        return {"error": "missing field: report (or findings)"}, 400
    try:
        pack = policy_pack.load_pack(pack_name)
    except Exception as e:
        return {"error": f"unknown pack {pack_name!r}: {e}"}, 404
    result = policy_pack.apply_pack(report, pack)
    return {"pack_name": pack_name, "result": result}, 200


def _agent_memory_scan(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    agent_memory_scan, _, _ = _import_scanner()
    files = data.get("files")
    if not isinstance(files, dict) or not files:
        return {"error": "missing field: files (dict of path -> content)"}, 400
    # 兼容传 base64：files 值可能带 {content: "..."} 包装
    normalized: Dict[str, str] = {}
    for k, v in files.items():
        if isinstance(v, dict):
            normalized[str(k)] = v.get("content", "") or ""
        elif isinstance(v, str):
            normalized[str(k)] = v
        else:
            normalized[str(k)] = ""
    framework_focus = data.get("framework_focus")
    result = agent_memory_scan.agent_memory_analysis(normalized)
    if framework_focus:
        focus = str(framework_focus).lower()
        result["findings"] = [
            f for f in result.get("findings", [])
            if focus in f.get("type", "").lower() or focus in f.get("description", "").lower()
        ]
        result["summary"] = result.get("summary", {})
        result["summary"]["framework_focus"] = focus
    return {
        "status": "ok",
        "files_scanned": len(normalized),
        "findings": result.get("findings", []),
        "summary": result.get("summary", {}),
    }, 200


def _list_red_team_probes() -> Dict[str, Any]:
    _, _, red_team_probe = _import_scanner()
    return {"count": len(red_team_probe.list_probes()), "probes": red_team_probe.list_probes()}


def _run_red_team_probes(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    _, _, red_team_probe = _import_scanner()
    include_failed = bool(data.get("include_failed", False))
    only_ids = data.get("probe_ids")
    # 默认走 scanner.rules 引擎
    try:
        from scanner import rules as scanner_rules
        rule_engine = scanner_rules.analyze
    except Exception:
        rule_engine = None
    result = red_team_probe.run_probes(rule_engine=rule_engine)
    probes = result.get("probes", [])
    if only_ids:
        want = set(only_ids)
        probes = [p for p in probes if p.get("id") in want]
    if not include_failed:
        probes = [p for p in probes if p.get("passed") is not False]
    result["probes"] = probes
    return {"status": "ok", "result": result}, 200


def _red_team_coverage() -> Dict[str, Any]:
    _, _, red_team_probe = _import_scanner()
    return red_team_probe.coverage_report()


def _confidence_promotion(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    confidence_promotion, _ = _import_scripts()
    write_back = bool(data.get("write_back", False))
    enforce = bool(data.get("enforce", False))
    result = confidence_promotion.run_check(write_back=write_back, enforce=enforce)
    return {"status": "ok", "result": result}, 200


def _rule_decay_state() -> Dict[str, Any]:
    _, rule_decay = _import_scripts()
    snapshots = rule_decay.read_snapshots()
    rules = rule_decay.load_radar_rules() + rule_decay.load_generated_pattern_rules()
    state = rule_decay.compute_state(snapshots, rules)
    return {
        "status": "ok",
        "history": {
            "snapshots_count": len(snapshots),
            "kept_recent": rule_decay.HIST_KEEP,
        },
        "state": state,
    }


def _rule_decay_snapshot(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    _, rule_decay = _import_scripts()
    snap = data.get("snapshot")
    if not isinstance(snap, dict):
        return {"error": "missing field: snapshot (dict)"}, 400
    # 允许传简写：{ts, hits: {rule_id: count}}；否则按 rule_decay 原生形状写
    if "hits" in snap and not ("rules" in snap or "snapshot" in snap):
        snap = {"timestamp": snap.get("ts", snap.get("timestamp", "")), **snap}
    rule_decay.append_snapshot(snap)
    return {"status": "ok", "appended": snap}, 200


def _rule_decay_retire(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    _, rule_decay = _import_scripts()
    snapshots = rule_decay.read_snapshots()
    rules = rule_decay.load_radar_rules() + rule_decay.load_generated_pattern_rules()
    state = rule_decay.compute_state(snapshots, rules)
    dry_run = bool(data.get("dry_run", True))
    if dry_run:
        return {"status": "ok", "dry_run": True, "state": state}, 200
    retired = rule_decay.retire_rules_from_source(state)
    return {"status": "ok", "dry_run": False, "retired_count": retired, "state": state}, 200


# ════════════════════════════════════════════════════════════════════════════
# 工具函数
# ════════════════════════════════════════════════════════════════════════════

def _safe_trace(err: Exception) -> str:
    """返回一个简短、可读的异常摘要，避免把栈打到响应体里撑爆客户端。"""
    import traceback
    lines = traceback.format_exception_only(type(err), err)
    return "".join(lines).strip()[:500]
