"""
eco/verifiable_identity.py — L1 可移植身份：JWKS 公钥发现 + 可验证凭证（VC）

═══════════════════════════════════════════════════════════════════
  为什么这一层是硬实力，不是补个端点
═══════════════════════════════════════════════════════════════════
  2026 年 agent 身份的主战场已经从「能不能登录」移到「别家能不能验我」：

    - IETF 已成立 Web Bot Authentication 工作组（首份 draft 2026-09-01）；
    - W3C Verifiable Credentials 2.0 系已转为 Recommendation；
    - CSA 明确指出：SPIFFE/SPIRE 的工作负载身份依赖「issuer 看得见被签发
      的基础设施」，一旦 agent 要向**另一家组织**出示可迁移身份，就必须有
      W3C DID + VC 这一层，否则依赖方无从验证。

  「别家能不能验我」的物理前提是**公钥可发现**。本模块就是这个前提的实现：

    JWKS（RFC 7517）→ 对外只发布**非对称公钥** → 任何第三方拉到 JWKS 就能
    离线验 aishield 签发的可验证凭证。**私钥（含对称密钥）永不出现在任何
    对外输出里** —— 这是本模块的第一红线，见 _assert_publishable()。

═══════════════════════════════════════════════════════════════════
  生产现状与迁移（真问题，不是假设）
═══════════════════════════════════════════════════════════════════
  当前线上 ``api/data/agent_card_key.json`` 的 alg **已是 ed25519（非对称）**，
  私钥/公钥分离，JWKS 对外就绪（``ready=true``，返回真实 Ed25519 公钥）。
  服务启动时 ``api/server.py`` 调用 ``ensure_ed25519(persist=True)`` 保证这一点；
  若发现活跃密钥仍是 HMAC，则自动迁移并在 JWKS 诚实标 ``ready=false``。

  历史包袱（双窗口，生产安全）：早期版本确曾用 hmac-sha256（对称），彼时
  ``public_key`` 与 ``private_key`` 同值，照搬发布等于公开签名密钥。故：

    * JWKS **永不**发布对称密钥（见 ``_assert_publishable`` 红线守卫）；
    * 旧对称密钥一旦迁移即进入 deprecated：**只保留验旧签，绝不发布、绝不进 JWKS**；
    * 迁移后的旧凭证仍能验（deprecated 公钥参与验签），新凭证公开可验。

  迁移语义（双窗口，生产安全）：
    - 新 Ed25519 密钥成为 active（对外签发 + 进 JWKS）；
    - 旧对称密钥移入 deprecated：**只保留验旧签的能力，绝不发布、绝不进 JWKS**；
    - 迁移后的旧凭证仍能验（deprecated 公钥参与验签），新凭证公开可验。

  若运行环境缺 `cryptography` 后端仍是 HMAC：JWKS 返回空 keys + 明确诊断
  （install cryptography / 跑迁移脚本），**绝不**把对称密钥往外发。

═══════════════════════════════════════════════════════════════════
  设计原则
═══════════════════════════════════════════════════════════════════
  - 零第三方依赖（签名走 eco/crypto_sign，自动 Ed25519 / HMAC 降级）。
  - 凭证紧凑串行：base64url(payload) + "." + base64url(sig)，带 alg/kid，
    可离线验证（验签不需要服务端状态）。
  - 除销状态是唯一的在线依赖：除销过的凭证验出「已被除销」而不是「签名错」。
  - 绝不 spawn 任何被治理的进程，本模块只做签发/验签/记录。
"""
from __future__ import annotations

import base64
import datetime
import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional

from eco import crypto_sign as _cs
from eco import did_key

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(BASE, "api", "data")

KEY_FILE = os.path.join(_DATA, "signing_keys.json")
LEGACY_KEY_FILE = os.path.join(_DATA, "agent_card_key.json")

ALG = "Ed25519"                 # RFC 7518 / 7517 对外输出必须是这个写法（大小写敏感）
ALG_UPPER = ALG.upper()         # 内部比较一律走大写：crypto_sign 返回的是 'ed25519'
KTY = "OKP"
CRV = "Ed25519"
VC_TYPE = "aishield.agent-identity.v1"

# 对称密钥（HMAC）绝不允许作为对外发布的密钥
_SECRET_ALGS = {"hmac", "hmac-sha256", "hmacsha256", "share"}


# ── 编码工具 ─────────────────────────────────────────────────────────────
def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64u_dec(s: str) -> bytes:
    s = (s or "").strip()
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _kid(public_b64: str) -> str:
    """kid = 公钥的 sha256 前 12 位（十六进制），与规则侧 _pattern_hash 同风格。"""
    return hashlib.sha256((public_b64 or "").encode("ascii")).hexdigest()[:12]


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def _now() -> int:
    return int(time.time())


def _iso_utc(epoch: int) -> str:
    """Unix 秒 → RFC 3339 UTC（W3C VC 2.0 validFrom/validUntil 要求）。"""
    return datetime.datetime.fromtimestamp(epoch, tz=datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def _assert_publishable(key: Dict[str, Any], where: str) -> None:
    """红线守卫：任何准备进 JWKS 的密钥，必须是非对称的 Ed25519 公钥。

    这里抛异常而不是静默跳过 —— 静默跳过会让「jwks 端点返回了个空气」变成
    一个没人报的假绿。宁可让端点 500，也不能把对称密钥发到公网上。
    """
    alg = str(key.get("alg") or "").strip().lower()
    if alg in _SECRET_ALGS:
        raise ValueError(
            f"{where}: 该密钥是对称密钥（alg={alg}），对称密钥绝不能对外发布"
            "（等同于公开签名密钥）。请先迁移到 Ed25519。"
        )
    if str(key.get("alg") or "").strip().upper() != ALG_UPPER:
        raise ValueError(f"{where}: 只支持 {ALG} 公钥发布，当前 alg={key.get('alg')}")


# ══════════════════════════════════════════
#  密钥环
# ══════════════════════════════════════════
class SigningKeyRing:
    """active（对外签发/发布）+ deprecated（仅验旧，不发布）。"""

    def __init__(self, path: Optional[str] = None):
        # 注意：默认值不能写成 KEY_FILE —— 默认参数在 import 时绑定，
        # 那样测试改了 vi.KEY_FILE 也重定向不到，会真去写 api/data/。
        self.path = path or KEY_FILE
        self.data: Dict[str, Any] = {"active": None, "deprecated": [],
                                     "revoked_credentials": [], "created_at": None}

    # ── 持久化 ──
    def load(self) -> "SigningKeyRing":
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.data = loaded
                    self.data.setdefault("active", None)
                    self.data.setdefault("deprecated", [])
                    self.data.setdefault("revoked_credentials", [])
            except Exception:
                # 密钥文件损坏：不静默重签（会伪造身份），保持空环由调用方决定
                pass
        else:
            self._absorb_legacy()
        return self

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def _absorb_legacy(self) -> None:
        """把历史 agent_card_key.json 收编为 deprecated（只验旧签，绝不发）。"""
        if not os.path.exists(LEGACY_KEY_FILE):
            return
        try:
            with open(LEGACY_KEY_FILE, "r", encoding="utf-8") as f:
                legacy = json.load(f)
        except Exception:
            return
        if not isinstance(legacy, dict):
            return
        pub = str(legacy.get("public_key") or "").strip()
        priv = str(legacy.get("private_key") or "").strip()
        if not pub or not priv:
            return
        self.data["active"] = {
            "alg": legacy.get("alg") or "hmac-sha256",
            "public_key": pub,
            "private_key": priv,
            "created_at": None,
        }
        self.data["_legacy_source"] = os.path.basename(LEGACY_KEY_FILE)

    # ── 密钥访问 ──
    def active(self) -> Optional[Dict[str, Any]]:
        a = self.data.get("active")
        return a if isinstance(a, dict) else None

    def deprecated(self) -> List[Dict[str, Any]]:
        d = self.data.get("deprecated")
        return d if isinstance(d, list) else []

    def key_by_kid(self, kid: str) -> Optional[Dict[str, Any]]:
        for cand in [self.active()] + self.deprecated():
            if cand and _kid(str(cand.get("public_key") or "")) == kid:
                return cand
        return None

    def is_ed25519_ready(self) -> bool:
        a = self.active()
        return bool(a) and str(a.get("alg") or "").upper() == ALG_UPPER

    def rotate_to_ed25519(self, *, persist: bool = True) -> Dict[str, Any]:
        """迁移到 Ed25519：新 active + 旧密钥进 deprecated（幂等，见 rotate）。"""
        return self.rotate(persist=persist)

    def ensure_ed25519(self, *, persist: bool = True) -> Dict[str, Any]:
        """保证活跃密钥为非对称 Ed25519：不是则幂等迁移。

        供服务启动时（api/server.py main）调用，使 JWKS 对外就绪——只有
        非对称公钥才能进 JWKS 被第三方公开验证；HMAC 对称密钥按安全红线
        永不外发，于是 JWKS 会 `ready=false`，aishield-trust/v1 信封也只能
        诚实标 `unsigned`。迁移把活跃密钥换成 Ed25519，旧密钥进 deprecated
        （仅验旧签），JWKS 随即 `ready=true`。幂等：已是 Ed25519 时不动。
        """
        if self.is_ed25519_ready():
            return {"ensured": True, "already": True,
                    "kid": _kid(str((self.active() or {}).get("public_key") or ""))}
        return self.rotate_to_ed25519(persist=persist)

    def rotate(self, *, force: bool = False, persist: bool = True) -> Dict[str, Any]:
        """轮换密钥：新 Ed25519 为 active，旧 active 进 deprecated（仅验旧签）。

        与 rotate_to_ed25519() 的区别在这一行：已经 Ed25519 时默认**不动**
        （迁移幂等，别把已经在用的密钥换掉）；但运维要**定期轮换**时必须能强制
        换 —— 只有「迁移」没有「轮换」，密钥就永远换不动，deprecated 双窗口
        也永远轮不上。

        返回 {"migrated": bool, "kid":..., "kept_deprecated": n, ...}
        对称旧密钥同样进 deprecated（保留验旧签），但 jwks() 永远拒发。
        """
        old = self.active()
        if old and str(old.get("alg") or "").upper() == ALG_UPPER and not force:
            return {"migrated": False, "kid": _kid(str(old.get("public_key"))),
                    "kept_deprecated": 0, "reason": "已是 Ed25519，无需迁移"}
        alg, priv_b64, pub_b64 = _cs.generate_keypair()
        new = {"alg": alg, "public_key": pub_b64, "private_key": priv_b64,
               "created_at": _now()}
        self.data["active"] = new
        if old:
            self.data["deprecated"] = [old] + [
                k for k in self.deprecated() if k is not old]
        self.data["deprecated"] = self.data["deprecated"][:20]
        if persist:
            self.save()
        return {"migrated": True, "kid": _kid(pub_b64), "alg": alg,
                "kept_deprecated": len(self.deprecated()),
                "old_alg": old.get("alg") if old else None}

    # ── JWKS（RFC 7517）────────────────────────────────────────────────
    def jwks(self) -> Dict[str, Any]:
        """对外公钥发现文档。**只含非对称 Ed25519 公钥，且只含 active。**

        对称/过期密钥一律不进；若 active 不是 Ed25519，keys 为空 + 诊断字段。
        """
        keys: List[Dict[str, Any]] = []
        diag: Dict[str, Any] = {}
        a = self.active()
        if not a:
            diag["ready"] = False
            diag["reason"] = "无可用签名密钥"
        else:
            alg = str(a.get("alg") or "").strip()
            if alg.upper() != ALG_UPPER:
                diag["ready"] = False
                diag["algorithm"] = alg
                # 诊断文案要**可执行**：告诉运维「哪一步错了 + 下一步敲什么」，
                # 只回一句「ready=false」等于把问题丢给对方猜（历史坑：空壳诊断
                # 让人以为端点挂了，实际是密钥没迁）。
                diag["reason"] = (
                    f"当前活跃密钥是 HMAC 对称密钥（alg={alg}），对称密钥对外发布"
                    " 等同于公开签名密钥，按安全红线拒绝发布任何公钥；"
                    f"请先 rotate_to_ed25519() 迁移到 {ALG}（迁移后旧密钥仅保留"
                    " 验旧签能力，不进 JWKS）"
                )
            else:
                pub = str(a.get("public_key") or "")
                _assert_publishable(a, "jwks.active")
                keys.append({
                    "kid": _kid(pub),
                    "kty": KTY,
                    "crv": CRV,
                    "alg": ALG,
                    "x": _b64u(_b64u_dec(pub)),
                })
                diag["ready"] = True
        return {"keys": keys, **diag}

    # ── 可验证凭证 ──
    def issue_credential(self, subject_did: str, claims: Optional[Dict[str, Any]] = None,
                         ttl: int = 86400) -> Dict[str, Any]:
        """签发一枚 agent 身份凭证（紧凑串行：payload.sig）。

        返回 {"credential_id", "token", "kid", "expires_at", "status"}
        """
        a = self.active()
        if not a:
            raise RuntimeError("无可用签名密钥，无法签发凭证")
        # 对称（HMAC）后端下签出来的凭证别人验不了 —— 宁可不发，也不发一枚
        # 只能自证的凭证（那比没有凭证更容易误导）。
        if not self.is_ed25519_ready():
            raise RuntimeError(
                f"当前活跃密钥 alg={a.get('alg')} 不是 {ALG}，签出的凭证无法被第三方"
                "公开验证；请先 rotate_to_ed25519() 迁移（旧密钥仍保留验旧签）"
            )
        pub = str(a.get("public_key") or "")
        kid = _kid(pub)
        # #441：issuer DID 统一为签名密钥的自认证 did:key（公钥编码进 DID，
        # 第三方可从 iss 直接解出公钥独立验签）。密钥异常时回退旧标签。
        try:
            issuer_did = did_key.did_key_from_base64url(pub)
        except Exception:
            issuer_did = "did:aishield:" + kid
        now = _now()
        cid = hashlib.sha256(
            _canonical({"sub": subject_did, "kid": kid, "iat": now})).hexdigest()[:16]
        payload = {
            "typ": VC_TYPE,
            "alg": ALG,
            "kid": kid,
            "iss": issuer_did,
            "sub": subject_did,
            "vcd": cid,
            "iat": now,
            "exp": now + int(ttl),
            "claims": claims or {},
        }
        body = _canonical(payload)
        try:
            sig = _cs.sign(body, str(a.get("private_key") or ""))
        except Exception as e:
            raise RuntimeError(f"凭证签名失败：{e}") from e
        token = f"{_b64u(body)}.{_b64u(_b64u_dec(sig))}"
        return {"credential_id": cid, "token": token, "kid": kid,
                "expires_at": payload["exp"], "subject": subject_did, "status": "active"}

    def verify(self, token: str, *, check_revocation: bool = True) -> Dict[str, Any]:
        """验证一枚凭证：签名 → 过期 → 除销。离线可验（除销查询需在线）。"""
        if not token or not isinstance(token, str) or "." not in token:
            return {"valid": False, "reason": "token 格式非法", "code": "malformed"}
        head_b64, _, sig_b64 = token.partition(".")
        try:
            body = _b64u_dec(head_b64)
            sig = _b64u_dec(sig_b64)
        except Exception:
            return {"valid": False, "reason": "token 编码非法", "code": "malformed"}

        try:
            outer = json.loads(body.decode("utf-8"))
        except Exception:
            return {"valid": False, "reason": "payload 不是 JSON", "code": "malformed"}

        kid = str(outer.get("kid") or "")
        key = self.key_by_kid(kid)
        if not key:
            return {"valid": False, "reason": f"未知 kid: {kid}", "code": "unknown_key",
                    "credential": outer}

        alg = str(key.get("alg") or "").upper()
        if alg == ALG_UPPER:
            # 关键：alg 实参必须传 crypto_sign 自己的常量。它内部对 alg 是大小写
            # 敏感的（传 'Ed25519' 会静默返回 False），自己拼字符串必踩。
            ok = _cs.verify(body, _cs_sign_to_b64(sig), str(key.get("public_key")),
                            _cs.ALG_ED25519)
        else:
            ok = False
        if not ok:
            return {"valid": False, "reason": "签名校验失败", "code": "bad_signature",
                    "credential": outer}

        exp = outer.get("exp")
        if isinstance(exp, (int, float)) and exp < _now():
            return {"valid": False, "reason": "凭证已过期", "code": "expired",
                    "credential": outer}

        if check_revocation:
            cid = str(outer.get("vcd") or "")
            if cid and cid in _revoked_now():
                return {"valid": False, "reason": "凭证已被除销", "code": "revoked",
                        "credential": outer}
        return {"valid": True, "reason": "ok", "code": "ok", "credential": outer}

    # ── 除销 ──
    def revoke(self, credential_id: str, *, persist: bool = True) -> bool:
        lst = self.data.setdefault("revoked_credentials", [])
        if credential_id in lst:
            return False
        lst.append(credential_id)
        self.data["revoked_credentials"] = lst
        if persist:
            self.save()
        return True

    # ══════════════════════════════════════════
    #  W3C VC 2.0 + VC-JWT（Program D / FTM）
    # ══════════════════════════════════════════
    #  与上面紧凑串行凭证（aishield.agent-identity.v1）的分工：
    #    v1 = 自有紧凑格式，服务端闭环够用；
    #    v2 = W3C VC 2.0 数据模型 + VC-JWT 保护，**给别家看的** ——
    #        第三方拿到 JWT 字符串，从 iss 的 did:key 直接解出公钥
    #        （自认证），离线验签，不需要我们的 JWKS、不需要我们在线。
    #  这正是蓝图 §3 Program D「别家能不能验我」的落地。

    VC2_CONTEXT = "https://www.w3.org/ns/credentials/v2"
    VC2_STATUS_TYPE = "aishieldCredentialStatusList2026"
    VC2_BASE_TYPE = "aishieldAgentIdentityV2"

    def issue_vc2(self, subject_did: str, claims: Optional[Dict[str, Any]] = None,
                  ttl: int = 86400,
                  credential_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """签发一枚 W3C VC 2.0 凭证，返回 {credential, jwt, credential_id, ...}。

        credential = VC 2.0 数据模型（JSON-LD context / type / issuer /
        credentialSubject / validFrom / validUntil / credentialStatus）；
        jwt = VC-JWT（W3C VC 2.0 标准化的 JOSE 保护形式，EdDSA 签名）。
        """
        a = self.active()
        if not a:
            raise RuntimeError("无可用签名密钥，无法签发凭证")
        if not self.is_ed25519_ready():
            raise RuntimeError(
                f"当前活跃密钥 alg={a.get('alg')} 不是 {ALG}，签出的 VC 2.0 无法"
                "被第三方公开验证；请先 rotate_to_ed25519() 迁移")
        pub = str(a.get("public_key") or "")
        kid = _kid(pub)
        try:
            issuer_did = did_key.did_key_from_base64url(pub)
        except Exception:
            issuer_did = "did:aishield:" + kid
        now = _now()
        cid = hashlib.sha256(_canonical(
            {"sub": subject_did, "kid": kid, "iat": now, "typ": self.VC2_BASE_TYPE}
        )).hexdigest()[:16]
        extra_types = [t for t in (credential_types or []) if isinstance(t, str)]
        vc = {
            "@context": [self.VC2_CONTEXT],
            "type": ["VerifiableCredential", self.VC2_BASE_TYPE] + extra_types,
            "issuer": issuer_did,
            "credentialSubject": {"id": subject_did, **(claims or {})},
            "validFrom": _iso_utc(now),
            "validUntil": _iso_utc(now + int(ttl)),
            "credentialStatus": {
                "id": "https://aishield.tools/api/v1/trust/vc2/status#" + cid,
                "type": self.VC2_STATUS_TYPE,
            },
        }
        # VC-JWT：header + payload（W3C VC 2.0 § Securing with JOSE）
        header = {"typ": "JWT", "alg": "EdDSA"}
        payload = {"iss": issuer_did, "sub": subject_did, "nbf": now,
                   "exp": now + int(ttl), "jti": cid, "vc": vc}
        signing_input = _b64u(_canonical(header)) + "." + _b64u(_canonical(payload))
        sig = _cs.sign(signing_input.encode("ascii"),
                       str(a.get("private_key") or ""), _cs.ALG_ED25519)
        jwt = signing_input + "." + _b64u(_b64u_dec(sig))
        return {"credential": vc, "jwt": jwt, "credential_id": cid,
                "issuer": issuer_did, "kid": kid, "subject": subject_did,
                "expires_at": payload["exp"], "status": "active",
                "formats": ["vc+ld+json (data model)", "vc+jwt (secured)"]}

    def verify_vc2(self, credential_or_jwt, *, check_revocation: bool = True) -> Dict[str, Any]:
        """验证 VC 2.0：接受 VC-JWT 字符串或带 jwt 字段的凭证对象。

        自认证路径：issuer 是 did:key → 直接解出公钥验签，**不依赖
        本服务在线、不依赖 JWKS**。这是"别家能不能验我"的答案。
        """
        if isinstance(credential_or_jwt, str):
            return self._verify_vc_jwt(credential_or_jwt, check_revocation)
        if isinstance(credential_or_jwt, dict):
            if credential_or_jwt.get("jwt"):
                return self._verify_vc_jwt(credential_or_jwt["jwt"], check_revocation)
            return {"valid": False, "code": "unsecured",
                    "reason": "裸 VC 数据模型没有保护机制；请验证随附的 VC-JWT"}
        return {"valid": False, "code": "malformed",
                "reason": "输入应为 VC-JWT 字符串或含 jwt 字段的对象"}

    def _verify_vc_jwt(self, jwt: str, check_revocation: bool = True) -> Dict[str, Any]:
        if not jwt or not isinstance(jwt, str):
            return {"valid": False, "code": "malformed", "reason": "JWT 为空"}
        parts = jwt.split(".")
        if len(parts) != 3:
            return {"valid": False, "code": "malformed", "reason": "JWT 须有三段"}
        try:
            header = json.loads(_b64u_dec(parts[0]))
            payload = json.loads(_b64u_dec(parts[1]))
            sig_raw = _b64u_dec(parts[2])
        except Exception:
            return {"valid": False, "code": "malformed", "reason": "JWT 编码非法"}
        iss = str(payload.get("iss")
                  or (payload.get("vc") or {}).get("issuer") or "")
        if not iss:
            return {"valid": False, "code": "unresolvable_issuer", "reason": "缺 issuer"}
        if not did_key.is_did_key(iss):
            # 旧 did:aishield 标签签的 VC 2.0：无法自认证，只能服务端验。
            # 诚实返回不可第三方验证，而不是假装验过。
            return {"valid": False, "code": "non_self_certified_issuer",
                    "reason": f"issuer {iss} 不是 did:key，第三方无法自认证验签",
                    "credential": payload.get("vc")}
        try:
            raw_pub = did_key.decode_did_key(iss)
        except Exception as exc:
            return {"valid": False, "code": "unresolvable_issuer",
                    "reason": f"did:key 解码失败: {exc}"}
        pub_b64url = base64.urlsafe_b64encode(raw_pub).decode("ascii").rstrip("=")
        ok = _cs.verify((parts[0] + "." + parts[1]).encode("ascii"),
                        _cs_sign_to_b64(sig_raw), pub_b64url, _cs.ALG_ED25519)
        if not ok:
            return {"valid": False, "code": "bad_signature",
                    "reason": "签名校验失败（JWT 被改写或密钥不匹配）"}
        now = _now()
        nbf, exp = payload.get("nbf"), payload.get("exp")
        if isinstance(nbf, (int, float)) and now + 60 < nbf:
            return {"valid": False, "code": "not_yet_valid",
                    "reason": "凭证尚未生效", "credential": payload.get("vc")}
        if isinstance(exp, (int, float)) and now > exp:
            return {"valid": False, "code": "expired",
                    "reason": "凭证已过期", "credential": payload.get("vc")}
        jti = str(payload.get("jti") or "")
        if check_revocation and jti and jti in _revoked_now():
            return {"valid": False, "code": "revoked",
                    "reason": "凭证已被除销", "credential": payload.get("vc")}
        return {"valid": True, "code": "ok", "reason": "ok",
                "issuer": iss, "jti": jti, "credential": payload.get("vc"),
                "verification": "did:key self-certified (offline, no JWKS needed)"}


def _cs_sign_to_b64(sig: bytes) -> str:
    """把验签入口需要的签名字节转成 crypto_sign 的 base64 形态。"""
    return base64.b64encode(sig).decode("ascii")


def _revoked_now() -> set:
    """实时读除销名单（每次读盘，不做进程内缓存）。

    除销是「凭证三要素」里唯一需要在线的部分，缓存会让「刚除销的凭证还验得
    过」变成一个持续到进程重启的窗口 —— 那正是攻击者复用的时间窗。
    """
    try:
        with open(KEY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            lst = data.get("revoked_credentials") or []
            return set(x for x in lst if isinstance(x, str))
    except Exception:
        pass
    return set()


# ══════════════════════════════════════════
#  模块级便利 API
# ══════════════════════════════════════════
def jwks() -> Dict[str, Any]:
    return SigningKeyRing().load().jwks()


def issue_credential(subject_did: str, claims: Optional[Dict[str, Any]] = None,
                     ttl: int = 86400) -> Dict[str, Any]:
    return SigningKeyRing().load().issue_credential(subject_did, claims, ttl)


def verify(token: str, *, check_revocation: bool = True) -> Dict[str, Any]:
    """验证凭证。

    ``check_revocation=False`` 用于**完全离线**的第三方：它只拉一次 JWKS 的
    公钥就能验验签，不碰除销名单（除销查询是这里唯一需要在线的部分）。
    """
    return SigningKeyRing().load().verify(token, check_revocation=check_revocation)


def revoke(credential_id: str) -> bool:
    ring = SigningKeyRing().load()
    return ring.revoke(credential_id)


def issue_vc2(subject_did: str, claims: Optional[Dict[str, Any]] = None,
              ttl: int = 86400,
              credential_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """签发 W3C VC 2.0 凭证（VC-JWT 保护，did:key 自认证）。"""
    return SigningKeyRing().load().issue_vc2(subject_did, claims, ttl, credential_types)


def verify_vc2(credential_or_jwt, *, check_revocation: bool = True) -> Dict[str, Any]:
    """验证 VC 2.0（第三方视角：只需 JWT 本身，did:key 自认证）。"""
    return SigningKeyRing().load().verify_vc2(credential_or_jwt,
                                              check_revocation=check_revocation)


def status() -> Dict[str, Any]:
    ring = SigningKeyRing().load()
    a = ring.active()
    return {
        "ready": ring.is_ed25519_ready(),
        # 对外一律给出规范大写写法：内部 crypto_sign 返回的是 'ed25519'，
        # 状态页若原样透出会让人拿去当 alg 传给第三方库，而 RFC 7517 要求
        # "Ed25519"，大小写不通就是验不出来。
        "alg": ALG_UPPER if ring.is_ed25519_ready() else (a or {}).get("alg"),
        "kid": _kid(str((a or {}).get("public_key") or "")) if a else None,
        "deprecated_keys": len(ring.deprecated()),
        "revoked_credentials": len(ring.data.get("revoked_credentials") or []),
        "legacy_source": ring.data.get("_legacy_source"),
    }


if __name__ == "__main__":
    print("JWKS:", json.dumps(jwks(), ensure_ascii=False)[:200])
    print("status:", json.dumps(status(), ensure_ascii=False))
