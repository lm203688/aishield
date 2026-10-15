"""
api/governance_api.py — 运行时治理能力的可机调用 HTTP 门面（#422 治理通电）

把 eco/runtime_governance 这一「世界级但从未上线」的库接线成产品级 API：
fail-closed 准入网关、kill switch、不可篡改哈希链审计、参数护栏、多 agent
责任链、成本可观测，全都通过 /api/v1/guard/* 对外暴露。

默认 mode=observe（记录并放行、不拦截），对外诚实标注 enforced=False，
避免「以为护栏开着其实没拦」的能力误读；set_mode("enforce") 一键升级到
fail-closed 强制拦截。

设计：零第三方依赖，仅标准库；既可被 server.py import，也可独立运行。
"""
from __future__ import annotations

import json
from urllib.parse import parse_qs

# 路径：确保项目根在 sys.path，以便 import eco
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

PREFIX = "/api/v1/guard"


def _rg():
    from eco import runtime_governance as rg
    return rg


def _q(query: str, key: str, default=None):
    vals = parse_qs(query or "").get(key)
    return vals[0] if vals else default


# ── GET ────────────────────────────────────────────────────────────────────
def handle_get(path: str, query: str = ""):
    """返回 (payload_dict, status_code)。

    容错：允许调用方把 ?query 直接拼在 path 里（如单测直接传完整 URL），
    也允许按 server.py 的真实调用约定把 query 作为第二参数传入。两种都支持。
    """
    rg = _rg()
    # 若 path 里带了查询串，拆出来并入 query
    if "?" in path:
        path, embedded = path.split("?", 1)
        if not query:
            query = embedded
    sub = path[len(PREFIX):]  # 去掉前缀后的子路径

    if sub == "" or sub == "/":
        return {
            "service": "aishield-runtime-governance",
            "version": "v1",
            "default_mode": "observe",
            "endpoints": {
                "GET  /api/v1/guard/evaluate?server=&tool=": "判定一次工具调用是否放行",
                "GET  /api/v1/guard/policy": "当前策略 + 模式",
                "GET  /api/v1/guard/audit?limit=": "倒序读取不可篡改审计链",
                "GET  /api/v1/guard/status": "网关健康 + 审计链校验",
                "GET  /api/v1/guard/attest": "持续证明流：最新运行时快照 + 全链校验",
                "GET  /api/v1/guard/kill-switch?server=": "查询某 server 是否被熔断",
                "POST /api/v1/guard/evaluate": "判定（带 context）",
                "POST /api/v1/guard/kill": "熔断某 server",
                "POST /api/v1/guard/revive": "恢复某 server",
                "POST /api/v1/guard/policy": "切换 mode: observe|enforce",
                "POST /api/v1/guard/allow": "加放行规则",
                "POST /api/v1/guard/deny": "加拒绝规则",
                "POST /api/v1/guard/attest": "强制签一次运行时快照",
            },
        }, 200

    if sub == "/evaluate":
        server = _q(query, "server")
        tool = _q(query, "tool", "")
        if not server:
            return {"error": "server query param required"}, 400
        return rg.evaluate(server, tool, log=True), 200

    if sub == "/policy":
        policy, ok = rg._load_policy()
        mode = policy.get("mode") or ("enforce" if policy.get("default_deny") else "observe")
        return {
            "mode": mode,
            "enforced": bool(policy.get("default_deny")),
            "default_deny": policy.get("default_deny", False),
            "allow_rules": len(policy.get("allow", {})),
            "deny_rules": len(policy.get("deny", {})),
            "killed_count": len(policy.get("killed", {})),
            "policy_healthy": ok,
            "note": "mode=observe 记录并放行（不拦截）；set_mode('enforce') 升级到 fail-closed",
        }, 200

    if sub == "/audit":
        try:
            limit = int(_q(query, "limit", "100"))
        except (TypeError, ValueError):
            limit = 100
        rows = rg.read_audit(limit=limit)
        return {"count": len(rows), "entries": rows}, 200

    if sub == "/status":
        return rg.status(), 200

    if sub == "/kill-switch":
        server = _q(query, "server")
        if not server:
            return {"error": "server query param required"}, 400
        return {"server": server, "killed": rg.is_killed(server)}, 200

    if sub == "/attest":
        # 持续证明流（Program C）：最新运行时快照 + 全链校验。
        # 快照只含状态摘要（策略指纹/审计链头/行为健康），绝不含策略原文
        # 与任何密钥材料 —— 可安全对外。
        return {
            "stream": {
                "every_evaluations": rg.ATTEST_EVERY_EVALUATIONS,
                "note": "每 N 次准入判定签一次运行时快照；签名密钥与 JWKS 同一把，"
                        "第三方可离线验证",
            },
            "latest": rg.attest_status().get("latest"),
            "chain": rg.attest_status().get("chain"),
        }, 200

    return {"error": "unknown guard endpoint", "path": path,
            "hint": "GET %s/ for endpoint list" % PREFIX}, 404


# ── POST ───────────────────────────────────────────────────────────────────
def handle_post(path: str, data: dict):
    """返回 (payload_dict, status_code)。"""
    data = data or {}
    rg = _rg()
    sub = path[len(PREFIX):]

    if sub == "/evaluate":
        server = data.get("server")
        tool = data.get("tool", "")
        context = data.get("context")
        if not server:
            return {"error": "server required"}, 400
        return rg.evaluate(server, tool, context=context, log=True), 200

    if sub == "/kill":
        server = data.get("server")
        reason = data.get("reason", "manual kill switch")
        if not server:
            return {"error": "server required"}, 400
        return rg.kill(server, reason), 200

    if sub == "/revive":
        server = data.get("server")
        reason = data.get("reason", "manual revive")
        if not server:
            return {"error": "server required"}, 400
        return rg.revive(server, reason), 200

    if sub == "/policy":
        # 显式切换 observe / enforce；也可直接给 default_deny 布尔
        if "mode" in data:
            return rg.set_mode(data["mode"]), 200
        if "default_deny" in data:
            return rg.set_default_deny(bool(data["default_deny"])), 200
        return {"error": "mode (observe|enforce) or default_deny required"}, 400

    if sub == "/allow":
        server = data.get("server")
        tools = data.get("tools", "*")
        if not server:
            return {"error": "server required"}, 400
        return rg.allow_tool(server, tools), 200

    if sub == "/deny":
        server = data.get("server")
        tools = data.get("tools", "*")
        if not server:
            return {"error": "server required"}, 400
        return rg.deny_tool(server, tools), 200

    if sub == "/attest":
        # 强制签一次运行时快照（运维触发/测试用），返回快照本体。
        entry = rg.attest_now()
        if not entry:
            return {"error": "快照签发失败"}, 500
        return entry, 200

    return {"error": "unknown guard endpoint", "path": path}, 404


if __name__ == "__main__":
    import pprint
    pprint.pprint(handle_get(PREFIX + "/"))
