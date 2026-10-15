"""
eco/agent_card.py — 签名 Agent Card（硬骨头 #2：伪造 Agent Card）

问题：恶意 agent 可发布 inflated Agent Card（虚报能力/信誉分）操纵 LLM 的 agent 选择
      （Google A2A 的 AgentCard 是 LLM 路由的主要依据，无原生签名）。
对策：Agent Card 由 AIShield 信任服务签发密码学签名；消费方（registry / LLM 路由 /
      编排器）校验签名 + 查询签发者公信力，拒绝未签名或签名无效的卡片。

格式：兼容 A2A v1.0 AgentCard，扩展 `aishield` 命名空间字段：
  - aishield.signature : base64 签名（对除 aishield 外所有字段的规范 JSON 签名）
  - aishield.signer_did: 签发者 DID
  - aishield.signed_at : ISO 时间戳
  - aishield.key_id    : 公钥标识
  - aishield.alg       : 签名算法（ed25519 / hmac-sha256）
  - aishield.trust_score: 签发时信任分（0-100，来自 eco.trust_score）

零依赖；签名走 eco/crypto_sign（Ed25519 优先 / HMAC 降级）。
私钥仅存服务端（api/data/agent_card_key.json）；公钥发布到 static/.well-known/agent-card-pubkey.json。
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone, timedelta

try:
    from eco import crypto_sign as cs
except ImportError:  # 允许以脚本方式直接运行自测
    import crypto_sign as cs

try:
    from eco import did_key
except ImportError:  # 允许以脚本方式直接运行自测
    import did_key

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WELLKNOWN = os.path.join(_BASE, "static", ".well-known")
_KEY_DIR = os.path.join(_BASE, "api", "data")
_KEY_FILE = os.path.join(_KEY_DIR, "agent_card_key.json")
_PUBKEY_FILE = os.path.join(_WELLKNOWN, "agent-card-pubkey.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()

# 旧体系标签：仅在信任服务密钥文件不可用时作为回退（向后兼容）。
# 正常情况签名者 DID 应为由 Ed25519 公钥派生的自认证 did:key（见 get_signer_did）。
SIGNER_DID = "did:aishield:trust-service"
SIGNER_DID_LEGACY = SIGNER_DID
KEY_ID = "key-1"


def get_signer_did(key_dir=None):
    """信任服务签名者的自认证 DID。

    优先从磁盘上的 Ed25519 公钥派生 ``did:key:z...``（公钥编码进 DID，任何人
    可独立验证，无需信任服务在线）。密钥文件不存在 / 非 ed25519（HMAC 降级）
    时回退到旧标签 ``did:aishield:trust-service``，保证导入与无密钥环境不崩溃。

    #441：把信任服务身份从「标签」升级为「自认证凭证」。
    """
    kd = key_dir or _KEY_DIR
    path = os.path.join(kd, "agent_card_key.json")
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                doc = json.load(f)
            if doc.get("alg") == cs.ALG_ED25519 and doc.get("public_key"):
                return did_key.did_key_from_base64url(doc["public_key"])
    except Exception:
        pass
    return SIGNER_DID_LEGACY


def _now_iso():
    return datetime.now(TZ).isoformat()


class AgentCardSigner:
    """签名 / 验证 Agent Card。"""

    def __init__(self, key_dir=None, signer_did=None, key_id=KEY_ID):
        # signer_did 留空 → 由 _resolve_signer_did() 从密钥文件派生 did:key；
        # 显式传入则尊重（测试 / 迁移回滚时可用旧标签）。
        self._explicit_signer_did = signer_did
        self.key_id = key_id
        self.key_dir = key_dir or _KEY_DIR
        self._alg = None
        self._priv = None
        self._pub = None

    def _resolve_signer_did(self):
        if self._explicit_signer_did:
            return self._explicit_signer_did
        return get_signer_did(self.key_dir)

    # ── 密钥管理 ──
    def _load_or_create(self):
        if self._priv is not None:
            return
        with _lock:
            if self._priv is not None:
                return
            os.makedirs(self.key_dir, exist_ok=True)
            if os.path.exists(_KEY_FILE):
                try:
                    with open(_KEY_FILE, "r", encoding="utf-8") as f:
                        doc = json.load(f)
                    alg = doc["alg"]
                    priv = doc["private_key"]
                    pub = doc["public_key"]
                    # 已存 ed25519 密钥但当前环境无 cryptography：降级为 HMAC，
                    # 并把 alg 持久化回文件。密钥字节复用（32B 私钥可直接当 HMAC secret）。
                    # 下次进程重启能读出 hmac-sha256，sign/verify 全程一致。
                    if alg == cs.ALG_ED25519 and not cs.have_crypto():
                        alg = cs.ALG_HMAC
                        with open(_KEY_FILE, "w", encoding="utf-8") as f:
                            json.dump({"alg": alg, "private_key": priv,
                                       "public_key": pub}, f)
                    self._alg, self._priv, self._pub = alg, priv, pub
                    return
                except Exception:
                    pass
            alg, priv, pub = cs.generate_keypair()
            with open(_KEY_FILE, "w", encoding="utf-8") as f:
                json.dump({"alg": alg, "private_key": priv, "public_key": pub}, f)
            self._alg, self._priv, self._pub = alg, priv, pub

    # ── 签发 ──
    def sign(self, card: dict, trust_score: int | None = None) -> dict:
        """对 A2A 风格 AgentCard 签名，返回带 aishield 命名空间的卡片。

        算法自动回退：
          - 加载时若密钥是 ed25519 但当前环境 cryptography 不可用，降级为 hmac-sha256
            并更新 self._alg；私钥字节复用（HMAC 与 Ed25519 私钥都是 32 字节）。
          - 这样保证零依赖环境仍能签发 + 验证，只有当 cryptography 恢复后可升级。
        """
        self._load_or_create()
        if self._alg == cs.ALG_ED25519 and not cs.have_crypto():
            self._alg = cs.ALG_HMAC
        body = cs.canonical_bytes(
            {k: v for k, v in card.items() if k != "aishield"})
        sig = cs.sign(body, self._priv, self._alg)
        signed = dict(card)
        signed["aishield"] = {
            "signature": sig,
            "signer_did": self._resolve_signer_did(),
            "signed_at": _now_iso(),
            "key_id": self.key_id,
            "alg": self._alg,
        }
        if trust_score is not None:
            signed["aishield"]["trust_score"] = int(trust_score)
        return signed

    # ── 公钥发布 ──
    def publish_pubkey(self, wellknown_dir=None):
        """把公钥（ed25519）或验证说明（hmac 走服务端）写到 .well-known。"""
        self._load_or_create()
        d = wellknown_dir or _WELLKNOWN
        os.makedirs(d, exist_ok=True)
        if self._alg == cs.ALG_ED25519:
            payload = {
                "signer_did": self._resolve_signer_did(),
                "alg": self._alg,
                "key_id": self.key_id,
                "public_key": self._pub,
            }
        else:
            payload = {
                "signer_did": self._resolve_signer_did(),
                "alg": self._alg,
                "key_id": self.key_id,
                "verification": "server-side",
                "note": "HMAC 密钥由 AIShield 信任服务持有；请调用 /api/v1/agent-card/verify 验证",
            }
        tmp = os.path.join(d, "agent-card-pubkey.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, os.path.join(d, "agent-card-pubkey.json"))
        return payload

    # ── 验证 ──
    def verify(self, card: dict, public_key_b64: str | None = None) -> dict:
        a = card.get("aishield", {})
        alg = a.get("alg")
        sig = a.get("signature")
        if not alg or not sig:
            return {"valid": False, "reason": "unsigned"}
        body = cs.canonical_bytes(
            {k: v for k, v in card.items() if k != "aishield"})
        if alg == cs.ALG_ED25519:
            pub = public_key_b64 or self._pub
            ok = cs.verify(body, sig, pub, alg)
            return {
                "valid": ok, "alg": alg, "signer_did": a.get("signer_did"),
                "signed_at": a.get("signed_at"),
                "trust_score": a.get("trust_score"),
            }
        # HMAC：调用方必须提供对称密钥；未提供时，若当前实例持有对称密钥
        # (server-side 场景)，直接用 self._priv 当 secret 验证。这是 HMAC
        # 算法本身"公私钥同值"的自然结果，而不是安全漏洞——私钥本就不该外发。
        if not public_key_b64:
            self._load_or_create()
            if self._alg == cs.ALG_HMAC and self._priv:
                ok = cs.verify(body, sig, self._priv, alg)
                return {"valid": ok, "alg": alg, "signer_did": a.get("signer_did")}
            return {
                "valid": False, "requires_server_verification": True,
                "alg": alg, "reason": "缺少 HMAC 密钥，请走服务端验证端点",
            }
        ok = cs.verify(body, sig, public_key_b64, alg)
        return {"valid": ok, "alg": alg, "signer_did": a.get("signer_did")}

    def public_key(self):
        self._load_or_create()
        return self._alg, self._pub


# ── 模块级便捷函数 ──
_default = AgentCardSigner()


def sign_card(card, trust_score=None):
    return _default.sign(card, trust_score)


def verify_card(card, public_key_b64=None):
    return _default.verify(card, public_key_b64)


def publish_pubkey(wellknown_dir=None):
    return _default.publish_pubkey(wellknown_dir)


def verify_with_pubkey_file(card, pubkey_file=None):
    """用 .well-known/agent-card-pubkey.json 离线验证 ed25519 卡片。

    - 文件不存在 → 请求服务端验证
    - 文件声明 HMAC → 请求服务端验证（HMAC 密钥不外发）
    - 文件声明 ed25519 但当前环境无 cryptography → 请求服务端验证
      （此时 verify() 会尝试用 self._priv 作 HMAC secret 的降级路径也
        走不通，因为签名是用 ed25519 私钥签的、而文件里存的是 pub_key）
    - 其他情况用文件里的 public_key 走离线 verify
    """
    path = pubkey_file or _PUBKEY_FILE
    if not os.path.exists(path):
        return {"valid": False, "requires_server_verification": True,
                "reason": "公钥文件不存在，请先 publish_pubkey()"}
    with open(path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    if doc.get("alg") != cs.ALG_ED25519:
        return {"valid": False, "requires_server_verification": True,
                "reason": "该部署使用 HMAC，需服务端验证"}
    if not cs.have_crypto():
        return {"valid": False, "requires_server_verification": True,
                "reason": "ed25519 公钥文件存在但本机无 cryptography 库，改走服务端验证"}
    return _default.verify(card, doc.get("public_key"))


if __name__ == "__main__":
    try:
        from eco.a2a_gateway import AgentCard
    except ImportError:
        from a2a_gateway import AgentCard
    mgr = AgentCard()
    raw = mgr.register({
        "name": "SecurityScanner",
        "url": "https://agent.aishield.tools/scanner",
        "description": "OWASP MCP Top 10 安全扫描 Agent",
        "skills": [{"id": "scan", "name": "security_scan", "tags": ["scan", "security"]}],
        "capabilities": ["security_scan"],
        "reputation_score": 88,
    })
    signed = sign_card(raw, trust_score=88)
    print("签名卡片 alg:", signed["aishield"]["alg"])
    publish_pubkey()
    v1 = verify_card(signed, _default.public_key()[1])
    print("离线验证(带公钥):", v1["valid"])
    v2 = verify_with_pubkey_file(signed)
    print("离线验证(公钥文件):", v2["valid"])
    # 篡改检测
    evil = json.loads(json.dumps(signed))
    evil["reputation_score"] = 999
    print("篡改后验证:", verify_card(evil, _default.public_key()[1])["valid"])
