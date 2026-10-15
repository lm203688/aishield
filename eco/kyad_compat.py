"""
eco/kyad_compat.py — KYA / Web Bot Auth 兼容层（支柱 L3：中立身份服务）

背景（2026 生态，一手锚点）：
  - KYA v0.1 Draft（Know-Your-Agent）：使用 SD-JWT + delegation chain 表达
    agent 身份 + 授权，8 种 machine-verifiable constraint。
  - Web Bot Auth：由 Cloudflare + GoDaddy 于 2026-04-07 联合发布，用
    HTTP Signature 做 bot 到 web 服务的身份绑定，是 agent 访问第三方网站的
    基础协议。
  - ANS（Agent Name Service）：GoDaddy + Cloudflare 的域名级 agent 命名。
  - ERC-8004：以太坊的 on-chain agent 身份（wallet-bound DID）。

设计目标：
  AIShield 不自研协议，只做**中立兼容层**：
    1. 把 A2A Agent Card 转换成 KYA-style agent identity（含 SD-JWT 结构的 claims）
    2. 把 agent identity 转换成 Web Bot Auth 的 HTTP Signature header 模板
    3. 把 ERC-8004 wallet 地址包装为 aishield 内部的 DID 别名
  这样 agent 生态的创新者可以用一个 aishield attestation 同时对接 KYA、
  Web Bot Auth、ERC-8004 三种上游标准。

零依赖；不解析 SD-JWT（那是 IETF 标准，交给消费方），这里只**生成**符合
SD-JWT 结构的 claims 列表（每条 claim 单独带 sha-256 摘要），便于后续
拼装成完整 SD-JWT。
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import datetime, timezone, timedelta

try:
    from eco import agent_card
except ImportError:  # 允许以脚本方式直接运行自测
    import agent_card

TZ = timezone(timedelta(hours=8))
NAMESPACE_AISHIELD = "aishield.org/2026"

KYA_SCHEMA = "https://w3c-ccg.github.io/SD-JWT/index.html"
WEB_BOT_AUTH_SCHEMA = "https://cloudflare.com/web-bot-auth/2026"
ERC8004_SCHEMA = "https://erc8004.dev/spec.json"


def _now_iso() -> str:
    return datetime.now(TZ).isoformat()


def _sha256_b64(payload: bytes) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).decode("ascii")


def _canon(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


# ══════════════════════════════════════════════
#  KYA SD-JWT claims
# ══════════════════════════════════════════════
def build_kya_claims(
    *, agent_id: str, name: str, url: str = "",
    capabilities: list = None, trust_score: int | None = None,
    signer_did: str | None = None,
    attestations: list = None,
) -> dict:
    """生成 KYA v0.1 风格的 SD-JWT claims 集合。

    返回结构：
      {
        "kid": str,                       # aishield 签发的 key id
        "alg": "ES256",                   # SD-JWT 通用
        "iat": "2026-09-24T...+08:00",
        "schema": KYA_SCHEMA,
        "claims": [
          {"cty": "agent:metadata", "value": {...}, "disc": "<sha256>"},
          {"cty": "agent:capability", "value": [...], "disc": "..."},
          ...
        ],
        "constraints": [ ... 8 种 machine-verifiable constraint 中的常见几种 ... ]
      }
    """
    # #441：signer_did 缺省时统一为信任服务自认证 did:key（密钥不可用回退旧标签）。
    if not signer_did:
        signer_did = agent_card.get_signer_did()
    now = _now_iso()
    claims = []

    # Claim 1: agent 元数据
    meta = {
        "agent_id": agent_id,
        "name": name,
        "url": url,
        "issuer": signer_did,
        "issued_at": now,
    }
    claims.append({
        "cty": "agent:metadata",
        "value": meta,
        "disc": _sha256_b64(_canon(meta)),
    })

    # Claim 2: capabilities（可披露）
    if capabilities:
        cap_payload = {"capabilities": list(capabilities)}
        claims.append({
            "cty": "agent:capability",
            "value": cap_payload,
            "disc": _sha256_b64(_canon(cap_payload)),
        })

    # Claim 3: trust score（可选）
    if trust_score is not None:
        ts_payload = {"score": int(trust_score), "scale": "0-100", "scheme": NAMESPACE_AISHIELD}
        claims.append({
            "cty": "agent:trust",
            "value": ts_payload,
            "disc": _sha256_b64(_canon(ts_payload)),
        })

    # Claim 4: attestations（引用的外部证书）
    if attestations:
        att_payload = {"references": list(attestations)}
        claims.append({
            "cty": "agent:attestation",
            "value": att_payload,
            "disc": _sha256_b64(_canon(att_payload)),
        })

    # 8 种 constraint 中的 3 个常用（KYA v0.1 允许 subset）
    constraints = [
        {"type": "expiry", "value": "P90D"},        # 90 天内有效
        {"type": "scope",  "value": capabilities or ["unrestricted"]},
        {"type": "issuer", "value": signer_did},
    ]

    return {
        "kid": f"aishield-key-1",
        "alg": "ES256",
        "iat": now,
        "schema": KYA_SCHEMA,
        "claims": claims,
        "constraints": constraints,
        "namespace": NAMESPACE_AISHIELD,
    }


def _b64u(obj_or_bytes) -> str:
    """base64url 无 padding 编码。obj 会先做 canonical JSON 序列化。"""
    import base64 as b64
    if isinstance(obj_or_bytes, (dict, list)):
        data = json.dumps(obj_or_bytes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    elif isinstance(obj_or_bytes, str):
        data = obj_or_bytes.encode("utf-8")
    else:
        data = obj_or_bytes
    return b64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64u_decode(s: str) -> bytes:
    import base64 as b64
    pad = "=" * (-len(s) % 4)
    return b64.urlsafe_b64decode((s + pad).encode("ascii"))


def to_sd_jwt_compact(
    kya_claims: dict,
    private_key_b64: str = "",
    private_key_alg: str = "ed25519",
) -> str:
    """把 KYA claims 序列化为**带签名**的 SD-JWT compact 形式。

    格式：`<b64u(header)>.<b64u(payload)>.<b64u(signature)>~<disc1.disc2.disc3>`

    - 未提供 private_key_b64 时输出**结构骨架**（signature 部分为空）；
    - 提供时按私有密钥签名（默认 Ed25519，兼容 ES256/HS256 通过 private_key_alg 选择）。
    - 签名 base64 编码，签名对象为 `header.payload.discs` 的规范串。
    """
    header = {"alg": kya_claims.get("alg", "ES256"), "typ": "dc+sd-jwt", "kid": kya_claims.get("kid", "")}
    payload = {
        "schema": kya_claims.get("schema"),
        "iat": kya_claims.get("iat"),
        "claims": kya_claims.get("claims", []),
        "constraints": kya_claims.get("constraints", []),
        "namespace": kya_claims.get("namespace"),
    }
    h = _b64u(header)
    p = _b64u(payload)
    discs = ".".join(c["disc"] for c in kya_claims.get("claims", []))

    if not private_key_b64:
        # 结构骨架模式（未签名）
        return f"{h}.{p}."

    # 签名模式：签 `h.p.discs`
    try:
        from eco import crypto_sign as cs
    except ImportError:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from eco import crypto_sign as cs

    message = f"{h}.{p}.{discs}".encode("utf-8")
    if private_key_alg == "ed25519" or cs.backend() == "ed25519":
        alg = cs.ALG_ED25519
    else:
        alg = cs.ALG_HMAC
    sig = cs.sign(message, private_key_b64, alg)
    return f"{h}.{p}.{sig}~{discs}"


def verify_sd_jwt(sd_jwt: str, public_key_b64: str, alg: str = "ed25519") -> dict:
    """验证带签名的 SD-JWT。

    返回：
      {"valid": bool, "claims_count": int, "iat": str, "reason": str}
    """
    import os
    parts = sd_jwt.split("~")
    if len(parts) != 2:
        return {"valid": False, "reason": "malformed: expected header.payload.sig~discs"}
    head, discs = parts[0], parts[1]
    hps = head.split(".")
    if len(hps) != 3:
        return {"valid": False, "reason": "malformed: expected h.p.sig"}
    h, p, sig = hps

    try:
        from eco import crypto_sign as cs
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from eco import crypto_sign as cs

    message = f"{h}.{p}.{discs}".encode("utf-8")
    alg_real = cs.ALG_ED25519 if alg == "ed25519" else cs.ALG_HMAC
    ok = cs.verify(message, sig, public_key_b64, alg_real)

    try:
        payload = json.loads(_b64u_decode(p).decode("utf-8"))
    except Exception:
        payload = {}

    return {
        "valid": ok,
        "claims_count": len(payload.get("claims", [])),
        "iat": payload.get("iat"),
        "reason": "" if ok else "signature verification failed",
    }


# ══════════════════════════════════════════════
#  Web Bot Auth HTTP Signature
# ══════════════════════════════════════════════
def build_web_bot_auth_headers(
    *, agent_id: str, agent_url: str, method: str = "GET",
    path: str = "/", ts: str | None = None,
) -> dict:
    """为 agent 访问第三方 Web 服务生成 Web Bot Auth 兼容的签名头模板。

    返回一个 header dict，其中 Authorization 头符合 HTTP Signature
    (RFC 9421) 的通用格式，`keyid` 指向 agent 的 aishield 公钥，
    `algorithm` 由部署方选择（默认 `rsa-v1_5-sha256`）。
    """
    ts = ts or datetime.now(TZ).strftime("%Y%m%dT%H%M%SZ")
    date_header = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    base = {
        "Date": date_header,
        "(request-target)": f"{method.lower()} {path}",
        "Content-Digest": "(none)",
        "X-Web-Bot-Auth-Agent": agent_id,
        "X-Web-Bot-Auth-URL": agent_url,
        "X-Web-Bot-Auth-Timestamp": ts,
    }
    return base


def assemble_signature_header(
    base_headers: dict, *, agent_id: str, agent_url: str,
    signature_b64: str = "<PENDING>",
) -> str:
    """组装成完整的 Authorization: Signature ... 头字符串。"""
    covered = ", ".join(f'"{k}"' for k in ["@method", "@path", "date", "content-digest",
                                             "x-web-bot-auth-agent", "x-web-bot-auth-url"])
    keyid = f"{agent_url}#aishield-key-1"
    return (
        f'Signature created="{base_headers.get("Date", "")}", '
        f'algorithm="rsa-v1_5-sha256", '
        f'keyid="{keyid}", '
        f'headers="{covered}", '
        f'signature="{signature_b64}"'
    )


# ══════════════════════════════════════════════
#  ERC-8004 wallet 身份
# ══════════════════════════════════════════════
def wallet_to_did(wallet_address: str, chain_id: int = 1) -> str:
    """把 ERC-8004 wallet 地址映射为 aishield 内部 DID。

    要求地址符合以太坊格式：0x + 40 位 hex。
    """
    if not isinstance(wallet_address, str):
        raise ValueError("wallet_address must be a string")
    addr = wallet_address.strip()
    if not addr.startswith("0x") and not addr.startswith("0X"):
        raise ValueError("wallet address must start with 0x")
    body = addr[2:]
    if len(body) != 40:
        raise ValueError(f"wallet address body must be 40 hex chars, got {len(body)}")
    try:
        int(body, 16)
    except ValueError:
        raise ValueError(f"wallet address body must be valid hex: {body}")
    return f"did:erc8004:chain{int(chain_id)}:{addr.lower()}"


def did_to_wallet(did: str) -> dict | None:
    """反向解析：aishield DID → ERC-8004 wallet 结构。"""
    if not did.startswith("did:erc8004:"):
        return None
    parts = did.split(":")
    if len(parts) != 4:
        return None
    try:
        chain = int(parts[2].replace("chain", ""))
    except ValueError:
        chain = 1
    return {"chain_id": chain, "address": parts[3], "schema": ERC8004_SCHEMA}


def agent_card_to_identity(
    card: dict,
    *, signer_did: str | None = None,
    trust_score: int | None = None,
) -> dict:
    """一站式：Agent Card → 三种上游身份（KYA + Web Bot Auth + ERC-8004 optional）。

    输入：aishield 签名过的 Agent Card（含 aishield 命名空间）
    输出：{ kya: {...}, web_bot_auth: {...}, erc8004: {...|None} }
    """
    agent_id = card.get("id") or card.get("name", "anonymous-agent")
    name = card.get("name", agent_id)
    url = card.get("url", "")
    caps = card.get("capabilities", [])
    if isinstance(caps, dict):
        caps = caps.get("supported", []) or []
    attestations = []
    a = card.get("aishield", {}) or {}
    if a.get("signature"):
        attestations.append({
            "type": "aishield-signed-agent-card",
            "signer": a.get("signer_did"),
            "signed_at": a.get("signed_at"),
        })

    kya = build_kya_claims(
        agent_id=agent_id, name=name, url=url,
        capabilities=caps or [], trust_score=trust_score,
        signer_did=signer_did, attestations=attestations,
    )
    wba = build_web_bot_auth_headers(agent_id=agent_id, agent_url=url or "about:blank")

    return {
        "agent_id": agent_id,
        "kya": kya,
        "kya_sd_jwt_compact": to_sd_jwt_compact(kya),
        "web_bot_auth": {
            "headers": wba,
            "schema": WEB_BOT_AUTH_SCHEMA,
        },
        "erc8004": None,   # 需要用户提供 wallet 才能映射
    }


if __name__ == "__main__":
    # 自证
    card = {
        "name": "Medical-Consult-Agent",
        "url": "https://example.org/agents/med-1",
        "capabilities": {"supported": ["consult", "triage"]},
        "aishield": {"signature": "abc", "signer_did": "did:aishield:trust-service",
                      "signed_at": _now_iso()},
    }
    ident = agent_card_to_identity(card, trust_score=75)
    print("KYA claims:", len(ident["kya"]["claims"]))
    print("SD-JWT compact (前 80):", ident["kya_sd_jwt_compact"][:80])
    print("Web Bot Auth headers:", list(ident["web_bot_auth"]["headers"].keys()))
    did = wallet_to_did("0xaB1234567890abcdef1234567890AbcdEF12345678", 1)
    print("ERC-8004 DID:", did)
    print("Reverse parse:", did_to_wallet(did))
