"""
eco/did_key.py — 零依赖 did:key 编解码（Ed25519）

为什么需要它（#441 身份层统一）：
  旧体系用 ``did:aishield:<随机hex>`` 作 Agent / 个人身份 DID，但它只是个
  **标签** —— 真实安全来自独立于 DID 字符串的 Ed25519 签名。问题在于：
  拿到一个 ``did:aishield:xxx``，你无法从中恢复出任何可用于验证的公钥，
  必须另走一条带外通道（信任服务 / 注册表）才能拿到 key。这违背了
  "去中心化身份" 的自认证初衷。

  ``did:key`` 把公钥**编码进 DID 本身**（公钥 → multicodec 前缀 → base58btc），
  任何人拿到 DID 就能解出公钥独立验证，无需信任服务在线。这正是把
  AIShield 身份层从"标签"升级为"自认证凭证"的关键一步。

规范（W3C did:key + multicodec）：
  - Ed25519 公钥 (32 字节 raw) → 前缀 0xed 0x01 (multicodec ed25519-pub) →
    base58btc（无 padding、Bitcoin 字母表）→ ``did:key:z<base58>``
  - 解码逆过程；``decode_did_key`` 会校验 0xed01 前缀，非 Ed25519 一律拒绝

零第三方依赖：base58btc 与 urlsafe-base64 均为纯实现。
"""
from __future__ import annotations

import base64

# Bitcoin / base58btc 字母表
_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# multicodec: ed25519-pub = varint(0xed 0x01)
MULTICODEC_ED25519_PUB = b"\xed\x01"

DID_KEY_PREFIX = "did:key:z"


# ───────────────────────────────────────────────────────────
# base58btc（纯实现，不依赖任何第三方库）
# ───────────────────────────────────────────────────────────

def _b58encode(data: bytes) -> str:
    """bytes → base58btc 字符串。"""
    if not data:
        return ""
    n = int.from_bytes(data, "big")
    out = ""
    while n > 0:
        n, rem = divmod(n, 58)
        out = _B58_ALPHABET[rem] + out
    # 前导零字节 → 前导 '1'
    pad = 0
    for b in data:
        if b == 0:
            pad += 1
        else:
            break
    return _B58_ALPHABET[0] * pad + out


def _b58decode(s: str) -> bytes:
    """base58btc 字符串 → bytes。非法字符抛 ValueError。"""
    if not s:
        return b""
    n = 0
    for ch in s:
        idx = _B58_ALPHABET.find(ch)
        if idx < 0:
            raise ValueError(f"非法 base58 字符: {ch!r}")
        n = n * 58 + idx
    # 前导 '1' → 前导零字节
    pad = 0
    for ch in s:
        if ch == _B58_ALPHABET[0]:
            pad += 1
        else:
            break
    out = n.to_bytes((n.bit_length() + 7) // 8, "big") if n > 0 else b""
    return b"\x00" * pad + out


# ───────────────────────────────────────────────────────────
# urlsafe-base64（兼容 crypto_sign 的 _b64e 输出）
# ───────────────────────────────────────────────────────────

def _b64url_decode(s: str) -> bytes:
    """解码 urlsafe-base64，**容忍缺 padding**（JWT/JWKS 惯例不写 '='）。"""
    s = (s or "").strip()
    if not s:
        raise ValueError("empty base64 payload")
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.encode("ascii") + pad.encode("ascii"))


# ───────────────────────────────────────────────────────────
# 编解码主入口
# ───────────────────────────────────────────────────────────

def encode_ed25519_pubkey(pubkey_raw: bytes) -> str:
    """Ed25519 原始公钥 (32 字节) → ``did:key:z...``。"""
    if not isinstance(pubkey_raw, (bytes, bytearray)):
        raise TypeError("pubkey 必须是 bytes")
    if len(pubkey_raw) != 32:
        raise ValueError(
            f"Ed25519 公钥必须是 32 字节，收到 {len(pubkey_raw)} 字节")
    payload = MULTICODEC_ED25519_PUB + bytes(pubkey_raw)
    return DID_KEY_PREFIX + _b58encode(payload)


def did_key_from_base64url(pub_b64url: str) -> str:
    """urlsafe-base64 编码的 Ed25519 公钥（同 crypto_sign._b64e 输出）→ did:key。"""
    return encode_ed25519_pubkey(_b64url_decode(pub_b64url))


def decode_did_key(did: str) -> bytes:
    """``did:key:z...`` → Ed25519 原始公钥 (32 字节)。

    校验 ``z`` 前缀与 0xed01 multicodec；非 Ed25519 或非 did:key 抛 ValueError。
    """
    if not is_did_key(did):
        raise ValueError(f"不是 did:key: {did!r}")
    body = did[len(DID_KEY_PREFIX):]
    raw = _b58decode(body)
    if not raw.startswith(MULTICODEC_ED25519_PUB):
        raise ValueError(
            "did:key 的多 codec 前缀不是 Ed25519 (0xed01)，不支持")
    pub = raw[len(MULTICODEC_ED25519_PUB):]
    if len(pub) != 32:
        raise ValueError(f"Ed25519 公钥长度异常: {len(pub)} 字节")
    return pub


# ───────────────────────────────────────────────────────────
# 判定 / 解析辅助
# ───────────────────────────────────────────────────────────

def is_did_key(did) -> bool:
    """是否形如 did:key:z...。"""
    return isinstance(did, str) and did.startswith(DID_KEY_PREFIX) and \
        did[len(DID_KEY_PREFIX):].rstrip("=") != ""


def did_method(did) -> str | None:
    """返回 DID 方法名：``key`` / ``aishield`` / ``aishield:pa`` / None。"""
    if not isinstance(did, str) or not did.startswith("did:"):
        return None
    rest = did[len("did:"):]
    method = rest.split(":", 1)[0]
    if method == "key":
        return "key"
    if method == "aishield":
        # 区分个人身份子方法 did:aishield:pa:*
        if rest.startswith("aishield:pa:"):
            return "aishield:pa"
        return "aishield"
    return method  # 其它方法原样返回（如 did:web / did:example）


def is_aishield_did(did) -> bool:
    """是否旧体系 did:aishield / did:aishield:pa（向后兼容判定）。"""
    m = did_method(did)
    return m in ("aishield", "aishield:pa")


def split_did(did: str):
    """拆分 DID 为 (method, method_specific_id)。非法返回 (None, None)。"""
    if not isinstance(did, str) or not did.startswith("did:"):
        return None, None
    rest = did[len("did:"):]
    parts = rest.split(":", 1)
    if len(parts) != 2:
        return None, None
    return parts[0], parts[1]


if __name__ == "__main__":
    # 自测：固定 32 字节公钥 → 编解码 round-trip + 前缀校验
    sample = bytes(range(32))  # 0x00..0x1f
    dk = encode_ed25519_pubkey(sample)
    print("encoded:", dk)
    assert dk.startswith("did:key:z"), "did:key 必须以 did:key:z 开头"
    assert decode_did_key(dk) == sample, "round-trip 失败"
    # 随机密钥
    import os
    for _ in range(3):
        pk = os.urandom(32)
        assert decode_did_key(encode_ed25519_pubkey(pk)) == pk
    # 判定辅助
    assert is_did_key(dk)
    assert not is_did_key("did:aishield:abc")
    assert did_method(dk) == "key"
    assert did_method("did:aishield:pa:xyz") == "aishield:pa"
    assert did_method("did:aishield:trust-service") == "aishield"
    assert is_aishield_did("did:aishield:pa:xyz")
    assert not is_aishield_did(dk)
    # 异常路径
    try:
        decode_did_key("did:aishield:trust-service")
        raise AssertionError("应当拒绝非 did:key")
    except ValueError:
        pass
    try:
        encode_ed25519_pubkey(b"short")
        raise AssertionError("应当拒绝非 32 字节公钥")
    except ValueError:
        pass
    print("did_key self-test OK")
