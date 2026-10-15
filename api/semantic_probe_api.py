"""
api/semantic_probe_api.py — NSE 语义探针的可机调用 HTTP 门面（Program A 通电）

把 scanner/semantic_probe 的双轨探针接线成产品级 API。核心诚实声明：

  · 本 API **不出结论**。probe 只返回候选（candidates），每个候选带
    requires_ratification=True；未经符号层 ratify 的候选不影响任何评分。
  · ratify 端点把候选与调用方提供的符号层 finding 对照，只升级有佐证的。
  · 零依赖、可完全离线运行（默认后端不发起任何外部调用）。

端点：
  GET  /api/v1/semantic/          服务信息 + 纪律声明
  GET  /api/v1/semantic/status     当前后端（是否配置 LLM、模型名、无密钥）
  POST /api/v1/semantic/probe      {text, context?} → 候选（无结论）
  POST /api/v1/semantic/ratify     {candidates, symbolic_findings?} → 分级
"""
from __future__ import annotations

import json
import os
import sys
from urllib.parse import parse_qs

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

PREFIX = "/api/v1/semantic"


def _probe():
    from scanner import semantic_probe as sp
    return sp


def _q(query: str, key: str, default=None):
    vals = parse_qs(query or "").get(key)
    return vals[0] if vals else default


# ── GET ────────────────────────────────────────────────────────────────────
def handle_get(path: str, query: str = ""):
    """返回 (payload_dict, status_code)。兼容 query 拼在 path 里的调用方式。"""
    if "?" in path:
        path, embedded = path.split("?", 1)
        if not query:
            query = embedded
    sub = path[len(PREFIX):]
    sp = _probe()

    if sub in ("", "/"):
        return {
            "service": "aishield-nse-semantic-probe",
            "version": "v1",
            "discipline": (
                "双轨：语义探针只产候选，结论必经符号层 ratify。"
                "本服务任何响应都不含 verdict/score/risk 字段 —— 零 FP 铁律"
                "不被语义层破坏。"
            ),
            "endpoints": {
                "GET  /api/v1/semantic/status": "当前后端与配置（无密钥外泄）",
                "POST /api/v1/semantic/probe": "{text} → 候选列表（不是结论）",
                "POST /api/v1/semantic/ratify": "{candidates, symbolic_findings} → ratified/unratified",
            },
            "candidate_kinds": list(sp.CANDIDATE_KINDS),
        }, 200

    if sub == "/status":
        probe = sp.get_probe()
        return {"backend": probe.backend_status(),
                "default_offline": probe.backend_status().get("backend") == "offline-lexical",
                "note": "LLM 后端需 AISHIELD_SEMANTIC_LLM_MODEL 等环境变量显式开启；"
                        "未配置时绝不发起外部调用。"}, 200

    return {"error": "unknown semantic endpoint", "path": path,
            "hint": "GET %s/ for endpoint list" % PREFIX}, 404


# ── POST ───────────────────────────────────────────────────────────────────
def handle_post(path: str, data: dict):
    """返回 (payload_dict, status_code)。"""
    data = data or {}
    if "?" in path:
        path = path.split("?", 1)[0]
    sub = path[len(PREFIX):]
    sp = _probe()

    if sub == "/probe":
        text = data.get("text") or data.get("content") or ""
        if not isinstance(text, str) or len(text.strip()) < 3:
            return {"error": "text (str, >=3 chars) required"}, 400
        if len(text) > 100_000:
            return {"error": "text too long (max 100KB)"}, 400
        result = sp.probe_text(text, data.get("context"))
        # 结构上再保证一次：万一将来有人给 probe 加了 verdict 字段，
        # 这里当场剥掉并把事实写进响应，而不是把结论透出去。
        leaked = sp.verdict_free_keys(result)
        if leaked:
            result.pop("_leaked", None)
            for k in list(leaked):
                result.pop(k, None)
            result["warning"] = (
                "探针输出曾含结论类字段 %s，已按双轨纪律剥除" % sorted(leaked))
        return result, 200

    if sub == "/ratify":
        candidates = data.get("candidates")
        if not isinstance(candidates, list):
            return {"error": "candidates (list) required"}, 400
        findings = data.get("symbolic_findings") or []
        if not isinstance(findings, list):
            return {"error": "symbolic_findings must be a list"}, 400
        return sp.SemanticProbe.ratify(candidates, findings), 200

    return {"error": "unknown semantic endpoint", "path": path}, 404


if __name__ == "__main__":
    import pprint
    pprint.pprint(handle_get(PREFIX + "/"))
