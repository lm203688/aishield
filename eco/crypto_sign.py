"""
eco/crypto_sign.py — 统一签名原语（零依赖，可选升级）

解决硬骨头 #2（伪造 Agent Card）：为 agent 生态资产提供密码学签名能力。

两种后端，自动选择：
  - "ed25519"    : 当 `cryptography` 可用时使用，真正的非对称签名，可离线公开验证
  - "hmac-sha256": 缺库时降级，对称密钥，仅服务端可验证（调用 /api/v1/agent-card/verify）

设计原则：
  - 默认零依赖可运行；`pip install cryptography` 后自动升级为 Ed25519，无需改任何业务代码
  - 签名统一 base64 编码，附带 `alg` 字段，验证方据此选择算法
  - 密钥以 bytes 存储，外部一律用 base64 字符串传递
  - canonical_bytes() 用确定性 JSON 序列化，避免字段顺序差异导致签名不一致

本模块是 R1「签名 Agent Card」与 R5「中立身份服务」的密码学底座。
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives import serialization
    _HAVE_CRYPTO = True
except Exception:  # pragma: no cover - 取决于运行环境
    _HAVE_CRYPTO = False

ALG_ED25519 = "ed25519"
ALG_HMAC = "hmac-sha256"


def backend() -> str:
    """当前生效的签名算法。"""
    return ALG_ED25519 if _HAVE_CRYPTO else ALG_HMAC


def have_crypto() -> bool:
    return _HAVE_CRYPTO


def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    """解码 base64url，**容忍缺 padding**（JWT / JWKS 的惯例是不写 '='）。

    严格 base64 要求长度是 4 的倍数；而 compact token 的每一段都是把 padding
    去掉之后发出去的。校验端若笨到要求 padding，等于把别人按 RFC 7515 解出来的
    签名字节直接判成「验不过」——协议层写着能验，实际谁也验不了。
    """
    s = (s or "").strip()
    if not s:
        raise ValueError("empty base64 payload")
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.encode("ascii") + pad.encode("ascii"))


def generate_keypair():
    """返回 (alg, private_b64, public_b64)。

    - ed25519: private = 32 字节种子, public = 32 字节（非对称，可公开 public）
    - hmac:    private == public == 32 字节随机密钥（对称，secret 不能公开）
    """
    if _HAVE_CRYPTO:
        sk = Ed25519PrivateKey.generate()
        pk = sk.public_key()
        priv = sk.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub = pk.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return ALG_ED25519, _b64e(priv), _b64e(pub)
    # HMAC 对称：生成随机密钥
    key = os.urandom(32)
    return ALG_HMAC, _b64e(key), _b64e(key)


def sign(message: bytes, private_b64: str, alg: str | None = None) -> str:
    """对 message 签名，返回 base64 签名串。"""
    alg = alg or backend()
    key = _b64d(private_b64)
    if alg == ALG_ED25519:
        if not _HAVE_CRYPTO:
            raise RuntimeError("cryptography 不可用，无法使用 ed25519")
        sk = Ed25519PrivateKey.from_private_bytes(key)
        return _b64e(sk.sign(message))
    # HMAC
    return _b64e(hmac.new(key, message, hashlib.sha256).digest())


def verify(message: bytes, signature_b64: str, public_b64: str, alg: str) -> bool:
    """验证签名。ed25519 用 public 公钥；hmac 用对称密钥（即 secret）。"""
    try:
        key = _b64d(public_b64)
        sig = _b64d(signature_b64)
    except Exception:
        return False
    if alg == ALG_ED25519:
        if not _HAVE_CRYPTO:
            return False
        try:
            Ed25519PublicKey.from_public_bytes(key).verify(sig, message)
            return True
        except Exception:
            return False
    # HMAC：对称，public 即密钥
    expected = hmac.new(key, message, hashlib.sha256).digest()
    return hmac.compare_digest(expected, sig)


def canonical_bytes(obj) -> bytes:
    """确定性 JSON 序列化（字段排序、无空格），用于签名与指纹。"""
    return json.dumps(
        obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def fingerprint(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


if __name__ == "__main__":
    print("backend:", backend(), "| cryptography:", _HAVE_CRYPTO)
    alg, priv, pub = generate_keypair()
    msg = canonical_bytes({"name": "demo", "skills": ["scan"]})
    sig = sign(msg, priv, alg)
    print("alg:", alg)
    print("verify ok:", verify(msg, sig, pub, alg))
    print("verify tampered:", verify(canonical_bytes({"name": "evil"}), sig, pub, alg))
