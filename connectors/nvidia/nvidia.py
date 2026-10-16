"""
connectors/nvidia/nvidia.py — NVIDIA 开发者平台接入（NGC / NIM / NeMo）
================================================================

**平台**：NVIDIA Developer Platform (https://developer.nvidia.com)
**接入底座**：NGC Catalog API / NIM 推理微服务（OpenAI 兼容）/ NeMo 训练编排
**认证**：NGC API Key（个人开发者身份），经 AIShield 治理层托管

**大陆访问状态（2026-09-24 实测）**：需 HTTPS_PROXY 走海外代理；self_check 会报告。

**治理模型**（与 eco/personal_agent.py 强绑定）：
  - PAI DID / Capability Ticket / 4-tier verdict / 8 因素风险 / HMAC 行动链
  - 所有 NVIDIA 调用前先做 preflight；敏感动作触发 block（需 override）
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import eco.personal_agent as pa
from connectors.base import (
    HTTPPost,
    detect_sensitive_triggers,
    extract_amount,
    http_post,
    load_state,
    prompt_fingerprint,
    proxy_env_summary,
    save_state,
)

# ============================================================
# NVIDIA 端点
# ============================================================

PLATFORM_ID = "nvidia-dev"
PROVIDER = "nvidia"

NGC_BASE = os.environ.get("AISHIELD_NVIDIA_NGC_BASE", "https://api.ngc.nvidia.com/v2")
NIM_BASE = os.environ.get("AISHIELD_NVIDIA_NIM_BASE", "https://ai.api.nvidia.com/v1")
NEMO_BASE = os.environ.get("AISHIELD_NVIDIA_NEMO_BASE", "https://api.nvidia.com/v1")

DEFAULT_REDIRECT_URI = os.environ.get(
    "AISHIELD_NVIDIA_REDIRECT_URI", "https://aishield.local/callback/nvidia"
)

# Action → 风险权重（影响 preflight 评分）
_ACTION_RISK_HINT = {
    "nim_chat": 0.1,
    "ngc_catalog": 0.0,
    "nemo_job": 0.4,
}


# ============================================================
# API Key 托管（个人开发者身份）
# ============================================================

def store_api_key(agent_instance_id: str, api_key: str) -> Dict[str, Any]:
    """存储 NGC API Key（fail-closed：空值拒绝）。"""
    if not api_key:
        return {"ok": False, "error": "api_key required"}
    data = load_state(PLATFORM_ID)
    inst = data.setdefault("instances", {}).setdefault(
        agent_instance_id, {"agent_instance_id": agent_instance_id}
    )
    inst["api_key"] = api_key
    inst["key_set_at"] = datetime.now(timezone.utc).isoformat()
    save_state(PLATFORM_ID, data)
    return {"ok": True, "agent_instance_id": agent_instance_id, "key_set": True}


def get_api_key(agent_instance_id: str) -> Dict[str, Any]:
    """取 NGC API Key（fail-closed：无则报错，不返回空密钥）。"""
    data = load_state(PLATFORM_ID)
    inst = data.get("instances", {}).get(agent_instance_id)
    if not inst or not inst.get("api_key"):
        return {"ok": False, "error": "no api key stored; call store_api_key first"}
    return {"ok": True, "api_key": inst["api_key"]}


def register_nvidia_agent(
    user_id: str,
    agent_name: str,
    agent_instance_id: str,
    platform_agent_id: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """登记一个 NVIDIA agent 实例到 AIShield（复用个人 Agent 治理层）。

    api_key 可选：一并传入则立即落库（NGC API Key 形态），
    也可稍后用 store_api_key() 单独设置。
    """
    if not (user_id and agent_name and agent_instance_id):
        return {"ok": False, "error": "user_id, agent_name, agent_instance_id required"}
    r = pa.register_agent_instance(
        user_id=user_id,
        agent_name=agent_name,
        provider=PROVIDER,
        platform=PLATFORM_ID,
        platform_hint=platform_agent_id or agent_instance_id,
    )
    out = {"ok": True, "agent_instance_id": agent_instance_id,
           "parent_did": r.get("parent_did"), "detail": r}
    if api_key:
        kr = store_api_key(agent_instance_id, api_key)
        out["api_key_stored"] = bool(kr.get("ok"))
    return out


# ============================================================
# Preflight（预算 / 风险）
# ============================================================

def preflight(
    agent_instance_id: str,
    user_id: str,
    prompt: str,
    action: str = "nim_chat",
    currency: str = "USD",
    amount: Optional[float] = None,
    http_post_mock: HTTPPost = None,
) -> Dict[str, Any]:
    if not (agent_instance_id and user_id):
        return {"ok": False, "error": "agent_instance_id and user_id required"}

    amount_detected = amount if amount is not None else extract_amount(prompt)
    triggers = detect_sensitive_triggers(prompt)
    payload = {
        "action": action,
        "prompt_fingerprint": prompt_fingerprint(prompt),
        "prompt_preview": (prompt or "")[:120],
        "target_url": NIM_BASE,
        "sensitive_triggers": triggers,
    }

    verdict_r = pa.check_budget_and_risk(
        user_id=user_id,
        action=f"nvidia.{action}",
        amount=amount_detected if amount_detected > 0 else None,
        currency=currency,
        target_url=NIM_BASE,
        category="inference" if action in ("nim_chat", "nemo_job") else "catalog",
        payload=payload,
    )
    if not verdict_r.get("success") and "verdict" not in verdict_r:
        return {"ok": False, "error": "preflight failed", "detail": verdict_r}

    raw_verdict = verdict_r.get("verdict") or "allow"
    raw_reason = verdict_r.get("verdict_reason") or verdict_r.get("reason") or ""
    risk = verdict_r.get("risk") or {}
    budget_info = verdict_r.get("budget") or {}

    final = raw_verdict
    final_reason = ""
    if raw_verdict == "denied" and raw_reason == "invalid_amount" and amount_detected <= 0:
        final = "allow"
        final_reason = "no_amount_inference_action"
    if raw_verdict in ("allow", "confirm", "denied") and triggers:
        final = "block"
        final_reason = "sensitive_triggers"
    elif raw_verdict == "denied" and raw_reason != "invalid_amount":
        final = "denied"
        final_reason = raw_reason

    verdict_out = {
        "verdict": final,
        "nvidia_action": action,
        "nvidia_sensitive_triggers": triggers,
        "final_reason": final_reason,
        "raw_verdict": raw_verdict,
        "raw_reason": raw_reason,
    }
    return {
        "ok": True,
        "verdict": verdict_out,
        "risk": risk,
        "budget": budget_info,
        "amount_detected": amount_detected,
        "currency": currency,
        "target_domain": "ai.api.nvidia.com",
        "agent_instance_id": agent_instance_id,
        "user_id": user_id,
        "prompt_fingerprint": prompt_fingerprint(prompt),
        "sensitive_triggers": triggers,
        "reason": raw_reason,
        "raw_verdict": verdict_r,
    }


# ============================================================
# 执行动作（NIM / NGC / NeMo）
# ============================================================

def run_agent_action(
    agent_instance_id: str,
    user_id: str,
    prompt: str,
    action: str = "nim_chat",
    model: str = "meta/llama-3.1-8b-instruct",
    currency: str = "USD",
    amount: Optional[float] = None,
    override: bool = False,
    http_post_mock: HTTPPost = None,
) -> Dict[str, Any]:
    """NVIDIA 全流程：preflight → API Key → 真实 API → record_action。"""
    pf = preflight(
        agent_instance_id=agent_instance_id, user_id=user_id, prompt=prompt,
        action=action, currency=currency, amount=amount, http_post_mock=http_post_mock,
    )
    if not pf.get("ok"):
        return pf

    verdict = pf["verdict"].get("verdict")
    verdict_data = pf["verdict"]

    if verdict == "denied":
        reason = pf.get("reason") or "budget_exceeded"
        if reason == "invalid_amount" and pf.get("amount_detected", 0) <= 0:
            verdict = "allow"
            verdict_data = {**verdict_data, "verdict": "allow", "reason": "no_amount_inference_action"}
        else:
            return {"ok": False, "error": f"budget hard-cap exceeded: {reason}",
                    "verdict": verdict_data, "risk": pf.get("risk"),
                    "note": "hard cap, override NOT allowed"}
    if verdict == "block" and not override:
        return {"ok": False, "error": "risk block; use override=true",
                "verdict": verdict_data, "risk": pf.get("risk"),
                "sensitive_triggers": pf.get("sensitive_triggers", [])}
    if verdict == "confirm" and not override:
        return {"ok": False, "error": "requires user confirmation",
                "verdict": verdict_data, "risk": pf.get("risk"),
                "action": "confirm_and_retry"}

    k = get_api_key(agent_instance_id)
    if not k.get("ok"):
        return {"ok": False, "error": k.get("error"), "verdict": verdict_data,
                "risk": pf.get("risk")}

    if action == "nim_chat":
        result = _call_nim_chat(k["api_key"], model, prompt, http_post_mock)
    elif action == "ngc_catalog":
        result = _call_ngc_catalog(k["api_key"], prompt, http_post_mock)
    elif action == "nemo_job":
        result = _call_nemo_job(k["api_key"], model, prompt, http_post_mock)
    else:
        return {"ok": False, "error": "unknown action",
                "supported": list(_ACTION_RISK_HINT.keys())}

    # 行动链记录（HMAC 上链；跨平台可离线验证）
    target = NGC_BASE if action == "ngc_catalog" else NIM_BASE
    action_payload = {
        "model": model,
        "target_url": target,
        "prompt_fingerprint": prompt_fingerprint(prompt),
        "result_ok": result.get("ok", False),
        "sensitive_triggers": pf.get("sensitive_triggers", []),
    }
    try:
        pa.record_action(
            user_id=user_id,
            action=f"nvidia.{action}",
            instance_id=agent_instance_id,
            verdict=verdict,
            payload=action_payload,
            note=json.dumps({
                "action": action, "model": model, "target": target,
                "override_used": bool(override),
            }, ensure_ascii=False),
        )
    except Exception:
        pass

    return {
        "ok": result.get("ok", False),
        "action": action,
        "verdict": verdict_data,
        "risk": pf.get("risk"),
        "result": result,
        "agent_instance_id": agent_instance_id,
        "user_id": user_id,
        "prompt_fingerprint": prompt_fingerprint(prompt),
    }


def _call_nim_chat(api_key: str, model: str, prompt: str, http_post_mock=None) -> Dict[str, Any]:
    url = NIM_BASE + "/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
    }
    sc, resp = http_post(url, body, token=api_key, http_post_mock=http_post_mock)
    if sc != 200:
        return {"ok": False, "status": sc, "error": resp}
    try:
        data = json.loads(resp) if isinstance(resp, str) else resp
        content = data["choices"][0]["message"]["content"]
    except Exception as e:
        return {"ok": False, "error": f"parse failed: {e}", "raw": resp}
    return {"ok": True, "content": content, "model": model}


def _call_ngc_catalog(api_key: str, query: str, http_post_mock=None) -> Dict[str, Any]:
    url = NGC_BASE + "/models"
    body = {"query": query, "pageSize": 20}
    sc, resp = http_post(url, body, token=api_key, http_post_mock=http_post_mock)
    if sc != 200:
        return {"ok": False, "status": sc, "error": resp}
    try:
        data = json.loads(resp) if isinstance(resp, str) else resp
        items = data.get("models", data.get("items", []))
        models = [m.get("name") for m in items][:20]
    except Exception as e:
        return {"ok": False, "error": f"parse failed: {e}", "raw": resp}
    return {"ok": True, "models": models, "query": query}


def _call_nemo_job(api_key: str, model: str, spec: str, http_post_mock=None) -> Dict[str, Any]:
    url = NEMO_BASE + "/nemo/jobs"
    body = {"model": model, "spec": spec, "kind": "training-orchestration"}
    sc, resp = http_post(url, body, token=api_key, http_post_mock=http_post_mock)
    if sc not in (200, 201, 202):
        return {"ok": False, "status": sc, "error": resp}
    try:
        data = json.loads(resp) if isinstance(resp, str) else resp
        job_id = data.get("jobId") or data.get("id")
    except Exception:
        job_id = None
    return {"ok": True, "job_id": job_id, "model": model}


# ============================================================
# 自检
# ============================================================

def self_check() -> Dict[str, Any]:
    """NVIDIA 接入就绪自检。"""
    data = load_state(PLATFORM_ID)
    instances = data.get("instances", {})
    n_with_key = sum(1 for v in instances.values() if v.get("api_key"))
    proxy = proxy_env_summary()
    return {
        "platform": PLATFORM_ID,
        "provider": PROVIDER,
        "reachable_from_cn": "regional_only (needs HTTPS_PROXY)",
        "instances": len(instances),
        "instances_with_key": n_with_key,
        "proxy": proxy,
        "endpoints": {"ngc": NGC_BASE, "nim": NIM_BASE, "nemo": NEMO_BASE},
        "actions": list(_ACTION_RISK_HINT.keys()),
        "self_check": "ok",
    }


def user_nvidia_state(user_id: str) -> Dict[str, Any]:
    """用户在 NVIDIA 平台上的所有注册 agent + API Key 状态。"""
    if not user_id:
        return {"ok": False, "error": "user_id required"}
    instances = pa.list_instances_by_platform(user_id=user_id, platform_id=PLATFORM_ID)
    state = load_state(PLATFORM_ID)
    key_info = []
    for inst in instances:
        iid = inst.get("instance_id")
        entry = state.get("instances", {}).get(iid)
        if entry:
            key_info.append({
                "agent_instance_id": iid,
                "agent_name": inst.get("agent_name"),
                "has_api_key": bool(entry.get("api_key")),
                "key_set_at": entry.get("key_set_at"),
            })
    return {
        "ok": True,
        "user_id": user_id,
        "platform": PLATFORM_ID,
        "platform_reachable": False,  # 大陆默认需代理
        "agents": instances,
        "api_keys": key_info,
        "proxy_env": proxy_env_summary(),
        "note": "需要 HTTPS_PROXY 走海外代理才能直连 ai.api.nvidia.com",
    }
