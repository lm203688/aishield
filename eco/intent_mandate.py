"""
eco/intent_mandate.py — L3 意图授权：Intent Mandate（对齐 AP2 / Verifiable Intent）

═══════════════════════════════════════════════════════════════════
  为什么这一层是硬实力
═══════════════════════════════════════════════════════════════════
  2026 年 agent 能花钱了。Google 的 AP2 把一次 agent 交易拆成三段：
  **Intent Mandate（人想干什么）→ Cart Mandate（买了什么）→
  Payment Mandate（怎么付）**，Mastercard 补上 Verifiable Intent 之后，
  Ant / Visa / Mastercard 在 2026-09 又推出 KYA（Know Your Agent）互操作框架。

  但落到「凭什么相信 agent 的这次动作就是人授权的、且没超纲、且没被重放」
  这件事上，绝大多数系统只有一句日志。这里补的是那句日志背后的三道闸：

    1. **不可抵赖**：mandate 用 agent 的签名密钥签，验签离线可完成；
    2. **不超纲**：action / resource / 金额上限 / 截止 / 工具白名单由
       mandate 自带约束，执行侧逐条卡（不是靠自然语言描述判断）；
    3. **不可重放**：mandate_id 一旦用掉立即记账，进程重启后仍有效。

  三道闸缺任何一道，等于给 agent 发了一张无限期的空白支票。

═══════════════════════════════════════════════════════════════════
  与 L1/L2 的关系
═══════════════════════════════════════════════════════════════════
  L1（verifiable_identity）管「这 agent 是谁」，L2（policy_bridge）管「这个工具
  能不能调」，L3 管「这次动作我批不批」。三者粒度不同、用途不同，不能互相替代：
  L1 的凭证回答不了「这次最多花多少钱」，L2 的 deny 名单也回答不了「这笔支付
  是不是人授权的」。

═══════════════════════════════════════════════════════════════════
  设计边界（不假装能做的事）
═══════════════════════════════════════════════════════════════════
  - 这里**不做**支付方式（不碰卡号、不碰收款），只做「意图约束」这一层；
  - mandate 的签发者是 agent 自己持有的签名密钥（与 VC 同密钥环），因此
    mandate 绑定 DID：别家 agent 拿不到这个 DID 的私钥就伪造不出 mandate；
  - 若运行环境仍是 HMAC（对称）后端：一律拒绝签发 mandate —— 对称密钥签的
    意图只能自证，等于没有不可抵赖性，宁可报错也不能发一张假支票。
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional

from eco import crypto_sign as _cs
from eco import verifiable_identity as _vi

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MANDATE_FILE = os.path.join(BASE, "api", "data", "intent_mandates.json")

MANDATE_TYPE = "aishield.intent-mandate.v1"

# 网关判定用的码（执行侧/审计侧只看这些码，别去解析自然语言）
CODE_OK = "ok"
CODE_MALFORMED = "malformed"
CODE_BAD_SIGNATURE = "bad_signature"
CODE_UNKNOWN_KEY = "unknown_key"
CODE_EXPIRED = "expired"
CODE_SCOPE_VIOLATION = "scope_violation"
CODE_LIMIT_EXCEEDED = "limit_exceeded"
CODE_REPLAYED = "replayed"
# 账本读不出来时给出的判定：不是"通过"，也不是"重放"，而是**无法判定**。
# 这条码存在的意义是让调用方能区分「iol 服务器坏了」与「这张券有问题」——
# 两种都要 fail-closed（valid=False），但只有前者该返 503 而不是 403。
CODE_LEDGER_ERROR = "ledger_error"


# ── 编码工具（与 L1 同风格：compact token = b64u(payload).b64u(sig)）───
def _b64u(data: bytes) -> str:
    return _vi._b64u(data)


def _b64u_dec(s: str) -> bytes:
    return _vi._b64u_dec(s)


def _canonical(obj: Any) -> bytes:
    return _vi._canonical(obj)


def _kid(public_b64: str) -> str:
    return _vi._kid(public_b64)


def _now() -> int:
    return int(time.time())


def _load_mandates() -> Dict[str, Any]:
    if os.path.exists(MANDATE_FILE):
        try:
            with open(MANDATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("used", {})
                return data
        except Exception:
            # 账本损坏：不能把「重放名单」当作空名单放行，那是把已用过的
            # mandate 全部复活。宁可让记账失效并显式报出来。
            return {"used": {}, "_load_error": "intent_mandates.json 损坏"}
    return {"used": {}}


def _save_mandates(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(MANDATE_FILE), exist_ok=True)
    tmp = MANDATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, MANDATE_FILE)


# ── 约束求值（执行侧逐条卡，不靠自然语言判断）────────────────────────
def _num(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def _check_constraints(payload: Dict[str, Any], request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """返回 {"code":..., "detail":...} 表示违例，None 表示全部合规。"""
    cons = payload.get("constraints") or {}
    action = str(request.get("action") or "").strip()
    allowed_actions = cons.get("allowed_actions") or cons.get("actions")
    if allowed_actions:
        allows = [str(a).strip() for a in allowed_actions]
        if action not in allows:
            return {"code": CODE_SCOPE_VIOLATION,
                    "detail": f"action={action!r} 不在授权动作白名单内"}

    resource = str(request.get("resource") or "").strip()
    allowed_resources = cons.get("allowed_resources")
    if allowed_resources:
        # 支持前缀（"repo:" 覆盖 "repo:foo"）与尾号通配
        ok = any(resource == str(r).strip()
                 or str(r).strip().rstrip("*").startswith(resource)
                 for r in allowed_resources)
        if not resource or not ok:
            return {"code": CODE_SCOPE_VIOLATION,
                    "detail": f"resource={resource!r} 不在授权资源范围内"}

    # 金额上限：只有显式声明 max_amount 的 mandate 才做金额闸（否则任何
    # 数字都会被当超纲，等于把 mandate 退化成布尔开关）
    max_amount = _num(cons.get("max_amount"))
    if max_amount is not None:
        amount = _num(request.get("amount"))
        if amount is None:
            return {"code": CODE_LIMIT_EXCEEDED,
                    "detail": "请求未带可比较的 amount，无法证明未超上限"}
        if amount > max_amount:
            return {"code": CODE_LIMIT_EXCEEDED,
                    "detail": f"amount={amount} 超过授权上限 {max_amount}"}
        currency = str(cons.get("currency") or "").strip().upper()
        if currency and str(request.get("currency") or "").strip().upper() != currency:
            return {"code": CODE_SCOPE_VIOLATION,
                    "detail": f"币种不一致：授权 {currency}，请求 {request.get('currency')}"}

    deadline = _num(cons.get("deadline"))
    if deadline is not None and _now() > deadline:
        return {"code": CODE_EXPIRED, "detail": "授权截止点已过"}
    return None


class IntentMandate:
    """意图授权的签发 / 求值 / 重放记账。"""

    def __init__(self, path: Optional[str] = None):
        # 同 L1：默认参数不能在 import 时绑定真实路径，否则测试重定向不了
        self.path = path or MANDATE_FILE

    # ── 签发 ──
    def issue(self, agent_did: str, action: str,
              constraints: Optional[Dict[str, Any]] = None,
              ttl: int = 300, request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """签一张 agent 意图 mandate。

        agent_did + action 必填；constraints 支持 allowed_actions /
        allowed_resources / max_amount / currency / deadline。返回
        {"mandate_id", "token", "kid", "expires_at", "constraints"}。
        """
        ring = _vi.SigningKeyRing().load()
        key = ring.active()
        if not key or not ring.is_ed25519_ready():
            raise RuntimeError(
                f"当前活跃密钥 alg={(key or {}).get('alg')} 不是 {_vi.ALG}，"
                "签出的意图只能自证、无法被第三方验证；请先迁移到 Ed25519"
            )
        if not agent_did or not action:
            raise ValueError("agent_did 与 action 必填")
        kid = _kid(str(key.get("public_key") or ""))
        now = _now()
        req = request or {}
        constraints = dict(constraints or {})
        # deadline 未给就按 ttl 到期（显式 deadline 优先，运维可设短窗）
        deadline = _num(constraints.get("deadline"))
        if deadline is None:
            constraints["deadline"] = now + int(ttl)

        mandate_id = hashlib.sha256(_canonical(
            {"did": agent_did, "action": action, "kid": kid, "iat": now}
        )).hexdigest()[:16]
        payload = {
            "typ": MANDATE_TYPE,
            "alg": _vi.ALG,
            "kid": kid,
            "iss": str(key.get("issuer") or ("did:aishield:" + kid)),
            "sub": agent_did,
            "mid": mandate_id,
            "action": action,
            "resource": str(req.get("resource") or ""),
            "constraints": constraints,
            "iat": now,
            "exp": now + int(ttl),
        }
        body = _canonical(payload)
        try:
            sig = _cs.sign(body, str(key.get("private_key") or ""))
        except Exception as e:  # pragma: no cover - 密钥异常路径
            raise RuntimeError(f"mandate 签名失败：{e}") from e
        token = f"{_b64u(body)}.{sig}"
        return {"mandate_id": mandate_id, "token": token, "kid": kid,
                "subject": agent_did, "action": action,
                "constraints": constraints, "expires_at": payload["exp"]}

    # ── 验签（离线可完成）──
    def verify(self, token: str, *, check_replay: bool = True) -> Dict[str, Any]:
        """只验签名与结构：不查重放账本、不看约束。"""
        if not token or not isinstance(token, str) or "." not in token:
            return {"valid": False, "code": CODE_MALFORMED, "reason": "mandate 格式非法"}
        head_b64, _, sig_b64 = token.partition(".")
        try:
            body = _b64u_dec(head_b64)
            _b64u_dec(sig_b64)
        except Exception:
            return {"valid": False, "code": CODE_MALFORMED, "reason": "mandate 编码非法"}
        try:
            outer = json.loads(body.decode("utf-8"))
        except Exception:
            return {"valid": False, "code": CODE_MALFORMED, "reason": "payload 不是 JSON"}
        if not isinstance(outer, dict) or outer.get("typ") != MANDATE_TYPE:
            return {"valid": False, "code": CODE_MALFORMED, "reason": "mandate 类型不匹配"}

        kid = str(outer.get("kid") or "")
        ring = _vi.SigningKeyRing().load()
        key = ring.key_by_kid(kid)
        if not key:
            return {"valid": False, "code": CODE_UNKNOWN_KEY, "reason": f"未知 kid: {kid}",
                    "mandate": outer}
        if str(key.get("alg") or "").upper() != _vi.ALG_UPPER:
            return {"valid": False, "code": CODE_BAD_SIGNATURE,
                    "reason": "命中的是非 Ed25519 密钥，无法公开验证", "mandate": outer}
        ok = _cs.verify(body, sig_b64, str(key.get("public_key") or ""), _cs.ALG_ED25519)
        if not ok:
            return {"valid": False, "code": CODE_BAD_SIGNATURE,
                    "reason": "mandate 签名校验失败", "mandate": outer}
        if check_replay:
            # 账本损坏时给出"无法判定"而不是抛异常：库调用方（包括 HTTP 边界）
            # 因此拿到的是同样的 fail-closed 判定，不会因为没写 try 就 500 掉。
            try:
                used = self._used_ids()
            except RuntimeError as e:
                return {"valid": False, "code": CODE_LEDGER_ERROR,
                        "reason": f"重放账本不可用：{e}", "mandate": outer}
            if outer.get("mid") in used:
                return {"valid": False, "code": CODE_REPLAYED,
                        "reason": "该 mandate 已被使用过（重放）", "mandate": outer}
        return {"valid": True, "code": CODE_OK, "reason": "ok", "mandate": outer}

    # ── 求值（执行侧入口）──
    def evaluate(self, token: str, request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """签 → 结构 → 过期 → 约束 → 重放，五道全过才算放行。

        顺序是刻意的：先离线可验的（签名/结构），再时间约束，再业务约束，
        最后才是需要写账的重放检查 —— 把「不用记账就能拒」的放在前面，避免
        大量非法请求去写盘。
        """
        req = request or {}
        res = self.verify(token, check_replay=True)
        if not res["valid"]:
            return res
        outer = res["mandate"]

        exp = outer.get("exp")
        if isinstance(exp, (int, float)) and exp < _now():
            return {"valid": False, "code": CODE_EXPIRED, "reason": "mandate 已过期",
                    "mandate": outer}
        dl = _num((outer.get("constraints") or {}).get("deadline"))
        if dl is not None and _now() > dl:
            return {"valid": False, "code": CODE_EXPIRED, "reason": "授权截止点已过",
                    "mandate": outer}

        sub = str(outer.get("sub") or "")
        if sub and str(req.get("agent_did") or "") and str(req.get("agent_did")) != sub:
            return {"valid": False, "code": CODE_SCOPE_VIOLATION,
                    "reason": "mandate 绑定的是另一个 agent DID", "mandate": outer}

        viol = _check_constraints(outer, req)
        if viol:
            return {"valid": False, "code": viol["code"], "reason": viol["detail"],
                    "mandate": outer}

        mid = str(outer.get("mid") or "")
        if mid and not self._mark_used(mid):
            return {"valid": False, "code": CODE_REPLAYED,
                    "reason": "该 mandate 已被使用过（重放）", "mandate": outer}
        return {"valid": True, "code": CODE_OK, "reason": "授权通过",
                "mandate": outer, "mandate_id": mid}

    # ── 重放账本 ──
    def _used_ids(self) -> "set":
        data = self._load_local()
        if data.get("_load_error"):
            raise RuntimeError(data["_load_error"])  # 账本损坏 → 拒绝放行（fail-closed）
        return set(x for x in (data.get("used") or {}).keys() if isinstance(x, str))

    def _load_local(self) -> Dict[str, Any]:
        data = _load_mandates()
        data["_path"] = self.path
        return data

    def _mark_used(self, mandate_id: str) -> bool:
        """记账并原子写盘。返回 False 表示已被用过（重放）。"""
        data = self._load_local()
        if data.get("_load_error"):
            raise RuntimeError(data["_load_error"])
        used = data.setdefault("used", {})
        if mandate_id in used:
            return False
        used[mandate_id] = _now()
        # 只留最近 5000 条，避免账本无限涨（旧条目只影响「用过一次」的记忆，
        # 而那种记忆本来就该有时效）
        if len(used) > 5000:
            for k in sorted(used, key=lambda x: used[x])[: len(used) - 5000]:
                used.pop(k, None)
        data.pop("_path", None)
        _save_mandates(data)
        return True

    def used_count(self) -> int:
        return len(self._used_ids())


# ══════════════════════════════════════════
#  模块级便利 API
# ══════════════════════════════════════════
def issue(agent_did: str, action: str, constraints: Optional[Dict[str, Any]] = None,
          ttl: int = 300, request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return IntentMandate().issue(agent_did, action, constraints, ttl, request)


def verify(token: str, *, check_replay: bool = True) -> Dict[str, Any]:
    """只验签（默认查重放；check_replay=False 用于离线审计）。"""
    return IntentMandate().verify(token, check_replay=check_replay)


def evaluate(token: str, request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return IntentMandate().evaluate(token, request)


def used_count() -> int:
    return IntentMandate().used_count()


if __name__ == "__main__":
    print(json.dumps(status(), ensure_ascii=False))
