"""
AIShield — trust_protocol

Agent 信誉协议层（融合自 lm203688/agent-trust-protocol，Apache-2.0，并入 AIShield MIT）。

提供两块零依赖能力（仅用 Python 标准库）：
  1. 身份（Identity）：Ed25519 密钥对 + did:key:z6Mk... 生成 / 签名 / 验签。
     —— 纯标准库实现 Curve25519 / RFC 8032，无需任何第三方加密库。
  2. 信誉（Scoring）：4 维加权信誉分（完成率 / 响应速度 / 可靠性 / 一致性），
     含 30 天半衰期的 EWMA 时间衰减一致性，输出 0–100 分 + 置信分级 + 等级。

与现有 api/trust_api.py（高层注册表 / 证书系统）互补：
  trust_api 是「注册表 + 证书」业务层；本模块是「密码学身份 + 信誉评分引擎」底层原语。
  TrustRegistry 可将 blackboard 交易事件 / 直接事件聚合成 DID 信誉分。

用法:
    from eco.trust_protocol import generate_keypair, sign_data, verify_signature_by_did, compute_trust_score, TrustRegistry
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import secrets
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

# ─────────────────────────────────────────────────────────────────────────────
# 身份层：Ed25519 + did:key（纯标准库实现，RFC 8032 / Curve25519）
# ─────────────────────────────────────────────────────────────────────────────

ED25519_MULTICODEC_PREFIX = bytes([0xed, 0x01])
BASE58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _base58_encode(data: bytes) -> str:
    # 仅统计「前导」零字节（标准 base58 语义）
    zeros = 0
    for b in data:
        if b == 0:
            zeros += 1
        else:
            break
    n = int.from_bytes(data, "big")
    chars = []
    while n > 0:
        n, r = divmod(n, 58)
        chars.append(BASE58_ALPHABET[r:r + 1])
    return ("1" * zeros) + b"".join(reversed(chars)).decode()


def _base58_decode(s: str) -> bytes:
    # 仅统计「前导」'1' 字符为前导零字节
    zeros = 0
    for c in s:
        if c == "1":
            zeros += 1
        else:
            break
    n = 0
    for c in s.encode():
        n = n * 58 + BASE58_ALPHABET.index(c)
    out = []
    while n > 0:
        n, r = divmod(n, 256)
        out.append(r)
    out.reverse()
    return b"\x00" * zeros + bytes(out)


P = 2**255 - 19
D = 37095705934669439343138083508754565189542113879843219016388785533085940283555
Q = 2**252 + 27742317777372353535851937790883648493
I = pow(2, (P - 1) // 4, P)


def _inv(x: int) -> int:
    return pow(x, P - 2, P)


def _recover_x(y: int, sign: int) -> int:
    y2 = y * y % P
    x2 = (y2 - 1) * _inv(D * y2 + 1) % P
    if x2 == 0:
        if sign:
            raise ValueError("Invalid point")
        return 0
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P != 0:
        x = x * I % P
    if (x * x - x2) % P != 0:
        raise ValueError("Invalid point")
    if x & 1 != sign:
        x = P - x
    return x


_G: Optional[tuple] = None


def _get_G() -> tuple:
    global _G
    if _G is None:
        y = 4 * _inv(5) % P
        x = _recover_x(y, 0)
        _G = (x, y, 1, x * y % P)
    return _G


def _point_add(P1: tuple, P2: tuple) -> tuple:
    X1, Y1, Z1, T1 = P1
    X2, Y2, Z2, T2 = P2
    a = (Y1 - X1) * (Y2 - X2) % P
    b = (Y1 + X1) * (Y2 + X2) % P
    c = T1 * 2 * D * T2 % P
    d = Z1 * 2 * Z2 % P
    e = b - a
    f = d - c
    g = d + c
    h = b + a
    return (e * f % P, g * h % P, f * g % P, e * h % P)


def _point_mul(s: int, point: tuple) -> tuple:
    result = (0, 1, 1, 0)
    current = point
    while s > 0:
        if s & 1:
            result = _point_add(result, current)
        current = _point_add(current, current)
        s >>= 1
    return result


def _compress(point: tuple) -> bytes:
    X, Y, Z = point[:3]
    zi = _inv(Z)
    x = X * zi % P
    y = Y * zi % P
    b = y.to_bytes(32, "little")
    if x & 1:
        b = b[:-1] + bytes([b[-1] | 0x80])
    return b


def _sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def _clamp(k: bytes) -> int:
    c = bytearray(k)
    c[0] &= 248
    c[31] &= 127
    c[31] |= 64
    return int.from_bytes(c, "little")


def _ed_sign(message: bytes, private_key: bytes) -> bytes:
    h = _sha512(private_key)
    a = _clamp(h[:32])
    prefix = h[32:]
    G = _get_G()
    A = _compress(_point_mul(a, G))
    r_hash = _sha512(prefix + message)
    r = int.from_bytes(r_hash, "little") % Q
    R = _compress(_point_mul(r, G))
    k_hash = _sha512(R + A + message)
    k = int.from_bytes(k_hash, "little") % Q
    S = ((r + k * a) % Q).to_bytes(32, "little")
    return R + S


def _ed_verify(message: bytes, signature: bytes, public_key: bytes) -> bool:
    if len(signature) != 64:
        return False
    try:
        R_bytes = signature[:32]
        S = int.from_bytes(signature[32:], "little")
        pk_y = int.from_bytes(public_key, "little") & ((1 << 255) - 1)
        pk_sign = public_key[31] >> 7
        pk_x = _recover_x(pk_y, pk_sign)
        A = (pk_x, pk_y, 1, pk_x * pk_y % P)
        ry = int.from_bytes(R_bytes, "little") & ((1 << 255) - 1)
        rs = R_bytes[31] >> 7
        rx = _recover_x(ry, rs)
        R_pt = (rx, ry, 1, rx * ry % P)
        G = _get_G()
        k_hash = _sha512(R_bytes + public_key + message)
        k = int.from_bytes(k_hash, "little") % Q
        lhs = _compress(_point_mul(S, G))
        rhs = _compress(_point_add(R_pt, _point_mul(k, A)))
        return lhs == rhs
    except Exception:
        return False


def _public_key_from_private(private_key: bytes) -> bytes:
    h = _sha512(private_key)
    a = _clamp(h[:32])
    G = _get_G()
    return _compress(_point_mul(a, G))


@dataclass
class AgentKeypair:
    """Ed25519 密钥对 + 派生的 did:key 身份。"""
    private_key: bytes   # 32 bytes
    public_key: bytes    # 32 bytes
    did: str             # did:key:z6Mk...


def generate_keypair() -> AgentKeypair:
    """生成新 Ed25519 密钥对并派生 did:key:z6Mk... DID。"""
    private_key = secrets.token_bytes(32)
    public_key = _public_key_from_private(private_key)
    multicodec = ED25519_MULTICODEC_PREFIX + public_key
    did = f"did:key:z{_base58_encode(multicodec)}"
    return AgentKeypair(private_key=private_key, public_key=public_key, did=did)


def public_key_to_did(public_key: bytes) -> str:
    """从 32 字节 Ed25519 公钥派生 did:key:z6Mk... DID。"""
    multicodec = ED25519_MULTICODEC_PREFIX + public_key
    return f"did:key:z{_base58_encode(multicodec)}"


def did_to_public_key(did: str) -> bytes:
    """从 did:key:z6Mk... DID 提取 32 字节原始公钥。"""
    if not did.startswith("did:key:"):
        raise ValueError("Not a did:key DID")
    mb = did[len("did:key:"):]
    if not mb.startswith("z"):
        raise ValueError("Expected multibase base58btc (prefix 'z')")
    decoded = _base58_decode(mb[1:])
    if decoded[:2] != ED25519_MULTICODEC_PREFIX:
        raise ValueError("DID is not an Ed25519 did:key (expected multicodec prefix 0xed01)")
    return decoded[2:]


def sign_data(data: str | bytes, private_key: bytes) -> str:
    """用私钥签名，返回 128 字符 hex 串（64 字节签名）。"""
    if isinstance(data, str):
        data = data.encode()
    return _ed_sign(data, private_key).hex()


def verify_signature(data: str | bytes, signature_hex: str, public_key: bytes) -> bool:
    """验签（配合 sign_data 使用）。"""
    if isinstance(data, str):
        data = data.encode()
    try:
        return _ed_verify(data, bytes.fromhex(signature_hex), public_key)
    except Exception:
        return False


def verify_signature_by_did(data: str | bytes, signature_hex: str, did: str) -> bool:
    """用 did:key DID 验签（无需原始公钥）。"""
    return verify_signature(data, signature_hex, did_to_public_key(did))


@dataclass
class IdentityFile:
    """序列化密钥对（默认存于 .aishield/identity.json，避免与上游 .agent-trust.json 冲突）。"""
    did: str
    public_key: str   # hex
    private_key: str  # hex  ← 保密
    created_at: str
    version: str = "1.0.0"

    def to_dict(self) -> dict:
        return {
            "did": self.did,
            "publicKey": self.public_key,
            "privateKey": self.private_key,
            "createdAt": self.created_at,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "IdentityFile":
        return cls(
            did=d["did"],
            public_key=d["publicKey"],
            private_key=d["privateKey"],
            created_at=d["createdAt"],
            version=d.get("version", "1.0.0"),
        )

    def to_keypair(self) -> AgentKeypair:
        return AgentKeypair(
            private_key=bytes.fromhex(self.private_key),
            public_key=bytes.fromhex(self.public_key),
            did=self.did,
        )


def load_or_create_identity(path: str = ".aishield/identity.json") -> AgentKeypair:
    """加载 .aishield/identity.json 身份，不存在则生成新身份并持久化。"""
    p = Path(path)
    if p.exists():
        with open(p) as f:
            return IdentityFile.from_dict(json.load(f)).to_keypair()
    p.parent.mkdir(parents=True, exist_ok=True)
    kp = generate_keypair()
    identity_file = IdentityFile(
        did=kp.did,
        public_key=kp.public_key.hex(),
        private_key=kp.private_key.hex(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    with open(p, "w") as f:
        json.dump(identity_file.to_dict(), f, indent=2)
    return kp


# ─────────────────────────────────────────────────────────────────────────────
# 信誉层：4 维加权评分 + EWMA 时间衰减一致性
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ScoreDimensions:
    completion_rate: float = 0.0
    response_time: float = 0.0
    reliability_score: float = 0.0
    consistency_score: float = 0.0


@dataclass
class TransactionRecord:
    provider_did: str
    protocol: Literal["x402", "mcp", "a2a", "other"]
    status: Literal["success", "failure", "disputed"]
    response_time_ms: float
    amount_usd: float = 0.0
    consumer_did: Optional[str] = None
    id: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class TrustScore:
    did: str
    overall_score: float
    dimensions: ScoreDimensions
    transaction_count: int
    computed_at: str
    confidence_tier: Literal["insufficient_data", "low", "medium", "high"]

    @property
    def grade(self) -> str:
        if self.overall_score >= 90:
            return "A"
        if self.overall_score >= 75:
            return "B"
        if self.overall_score >= 60:
            return "C"
        if self.overall_score >= 40:
            return "D"
        return "F"


WEIGHTS = dict(
    completion_rate=0.35,
    reliability_score=0.30,
    consistency_score=0.20,
    response_time=0.15,
)

MIN_FOR_LOW = 5
MIN_FOR_MEDIUM = 25
MIN_FOR_HIGH = 100

EWMA_HALF_LIFE_DAYS = 30
EWMA_PRIOR_N = 10
EWMA_PRIOR_SCORE = 70


def _normalise_response_time(avg_ms: float) -> float:
    FAST, SLOW = 500, 10_000
    if avg_ms <= FAST:
        return 100.0
    if avg_ms >= SLOW:
        return 0.0
    return 100 * (1 - (avg_ms - FAST) / (SLOW - FAST))


def _ewma_consistency(records: list[TransactionRecord]) -> float:
    """EWMA 时间衰减一致性分（30 天半衰期）。"""
    if not records:
        return float(EWMA_PRIOR_SCORE)

    half_life_ms = EWMA_HALF_LIFE_DAYS * 24 * 3600 * 1000
    decay = math.log(2) / half_life_ms
    now_ms = datetime.now(timezone.utc).timestamp() * 1000

    prior_weight = EWMA_PRIOR_N * math.exp(-decay * half_life_ms)
    weighted_sum = prior_weight * EWMA_PRIOR_SCORE
    total_weight = prior_weight

    for r in records:
        try:
            ts = datetime.fromisoformat(r.created_at.replace("Z", "+00:00")).timestamp() * 1000
        except Exception:
            ts = now_ms
        age = max(0, now_ms - ts)
        w = math.exp(-decay * age)
        value = 100 if r.status == "success" else (0 if r.status == "disputed" else 30)
        weighted_sum += w * value
        total_weight += w

    return round(weighted_sum / total_weight, 2)


def compute_trust_score(did: str, records: list[TransactionRecord]) -> TrustScore:
    """
    基于交易记录计算给定 DID 的 AgentTrust 信誉分（纯 Python 实现，
    对应 agent-trust-protocol packages/core/src/scoring.ts）。
    """
    now = datetime.now(timezone.utc).isoformat()

    if not records:
        return TrustScore(
            did=did,
            overall_score=0,
            dimensions=ScoreDimensions(),
            transaction_count=0,
            computed_at=now,
            confidence_tier="insufficient_data",
        )

    n = len(records)
    success_count = sum(1 for r in records if r.status == "success")
    dispute_count = sum(1 for r in records if r.status == "disputed")
    avg_ms = sum(r.response_time_ms for r in records) / n

    dims = ScoreDimensions(
        completion_rate=round(success_count / n * 100, 2),
        response_time=round(_normalise_response_time(avg_ms), 2),
        reliability_score=round(max(0, 100 - (dispute_count / n) * 200), 2),
        consistency_score=_ewma_consistency(records),
    )

    overall = round(
        dims.completion_rate * WEIGHTS["completion_rate"]
        + dims.reliability_score * WEIGHTS["reliability_score"]
        + dims.consistency_score * WEIGHTS["consistency_score"]
        + dims.response_time * WEIGHTS["response_time"],
        2,
    )

    tier: Literal["insufficient_data", "low", "medium", "high"] = (
        "insufficient_data" if n < MIN_FOR_LOW
        else "low" if n < MIN_FOR_MEDIUM
        else "medium" if n < MIN_FOR_HIGH
        else "high"
    )

    return TrustScore(
        did=did,
        overall_score=overall,
        dimensions=dims,
        transaction_count=n,
        computed_at=now,
        confidence_tier=tier,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 注册表：持久化 DID → 交易事件 → 信誉分（可摄入 blackboard 事件）
# ─────────────────────────────────────────────────────────────────────────────

class TrustRegistry:
    """维护 DID 交易事件并产出信誉分。默认持久化到 api/data/trust_registry.json。"""

    def __init__(self, path: str = "api/data/trust_registry.json"):
        self.path = path
        self._lock = threading.Lock()
        self._data: dict = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"events": []}
        return {"events": []}

    def _save(self) -> None:
        # 调用方（record_event）已持有 self._lock，此处不再加锁，避免重入死锁
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def record_event(
        self,
        provider_did: str,
        status: Literal["success", "failure", "disputed"],
        protocol: Literal["x402", "mcp", "a2a", "other"] = "other",
        response_time_ms: float = 0.0,
        amount_usd: float = 0.0,
        consumer_did: Optional[str] = None,
    ) -> TransactionRecord:
        """记录一笔交易事件并持久化。"""
        rec = TransactionRecord(
            provider_did=provider_did,
            protocol=protocol,
            status=status,
            response_time_ms=response_time_ms,
            amount_usd=amount_usd,
            consumer_did=consumer_did,
        )
        with self._lock:
            self._data.setdefault("events", []).append({
                "id": rec.id,
                "provider_did": rec.provider_did,
                "consumer_did": rec.consumer_did,
                "protocol": rec.protocol,
                "status": rec.status,
                "response_time_ms": rec.response_time_ms,
                "amount_usd": rec.amount_usd,
                "created_at": rec.created_at,
            })
            self._save()
        return rec

    def events_for(self, did: str) -> list[TransactionRecord]:
        """返回某 DID 作为 provider 的全部交易记录。"""
        out = []
        for e in self._data.get("events", []):
            if e.get("provider_did") == did:
                out.append(TransactionRecord(
                    provider_did=e["provider_did"],
                    protocol=e.get("protocol", "other"),
                    status=e.get("status", "success"),
                    response_time_ms=e.get("response_time_ms", 0.0),
                    amount_usd=e.get("amount_usd", 0.0),
                    consumer_did=e.get("consumer_did"),
                    id=e.get("id"),
                    created_at=e.get("created_at"),
                ))
        return out

    def score(self, did: str) -> TrustScore:
        """计算某 DID 的信誉分。"""
        return compute_trust_score(did, self.events_for(did))

    def score_dict(self, did: str) -> dict:
        """分数 → 可序列化字典。"""
        s = self.score(did)
        return {
            "did": s.did,
            "overall_score": s.overall_score,
            "grade": s.grade,
            "confidence_tier": s.confidence_tier,
            "transaction_count": s.transaction_count,
            "dimensions": {
                "completion_rate": s.dimensions.completion_rate,
                "response_time": s.dimensions.response_time,
                "reliability_score": s.dimensions.reliability_score,
                "consistency_score": s.dimensions.consistency_score,
            },
            "computed_at": s.computed_at,
        }

    def verify_identity(self, data: str | bytes, signature_hex: str, did: str) -> bool:
        """用登记 DID 验签（便捷封装）。"""
        return verify_signature_by_did(data, signature_hex, did)
