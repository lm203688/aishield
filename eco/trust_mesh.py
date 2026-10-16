# -*- coding: utf-8 -*-
"""
eco/trust_mesh.py — 联邦信任网格（蓝图 Program D · FTM）v0.1
============================================================

蓝图定位（§3 Program D）
-----------------------
缺口 C：信任是"自证"（badge 零采纳），不是"互证"；单点信任无法对抗 agent 经济
的规模化攻击。本模块把 `aishield-trust/v1` 凭证从"自签占位"升级为
**W3C VC 2.0 + did:key 真签名 + CT 式透明日志**，并给出联邦协议 v0.1 骨架
（安全聚合，零数据出域）。

交付内容
--------
  1. `issue_credential()` —— 签发 W3C VC 2.0 凭证：用 did:key (Ed25519) 对凭证
     做 Data-Integrity 式签名（proof）。公钥自认证，第三方离线可验。
  2. `verify_credential()` —— 从 issuer 的 did:key 解出公钥，校验签名；防篡改。
  3. `TransparentLog` —— CT 式 append-only 哈希链，记录每次签发的凭证 ID；
     任何节点可验证"某凭证确实被公开登记过"，杜绝私下签发。
  4. `secure_aggregate()` —— 联邦 v0.1：各节点只上报**信号摘要（计数 + 哈希）**，
     不上传原始数据，全局聚合新型攻击特征向量——既 collective defense 又零数据出域。

零第三方依赖（Ed25519 走既有 eco.crypto_sign；did:key 走 eco.did_key）。
cryptography 不可用时降级 HMAC 并诚实标注 third_party_verifiable=False。
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_BASE, "api", "data")

try:
    from eco import crypto_sign as cs  # noqa: E402
    from eco import did_key as dk  # noqa: E402
except Exception:  # pragma: no cover
    cs = None
    dk = None

GENESIS_HASH = "0" * 64
_lock = threading.RLock()

VC_CONTEXTS = [
    "https://www.w3.org/ns/credentials/v2",
    "https://aishield.tools/ns/trust/v1",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ───────────────────────────────────────────────────────────────────────────
# 凭证签发 / 验证
# ───────────────────────────────────────────────────────────────────────────
def issue_credential(subject: Dict[str, Any], *, keypair: Optional[Dict[str, str]] = None,
                     cred_id: Optional[str] = None,
                     issuer_url: str = "https://aishield.tools") -> Dict[str, Any]:
    """签发一张 W3C VC 2.0 信任凭证，附 did:key (Ed25519) 数据完整性签名。

    subject 即被认证资产的信任声明（score/level/risk/no_spawn_guarantee …）。
    keypair = {"alg","private_key","public_key"}（缺省现场生成；生产注入长期密钥环）。
    返回完整可验证凭证（含 proof）。
    """
    if cs is None or dk is None:
        raise RuntimeError("eco.crypto_sign / eco.did_key 不可用")
    kp = keypair or dict(zip(("alg", "private_key", "public_key"),
                             cs.generate_keypair()))
    alg = kp.get("alg") or cs.backend()
    pub_raw_b64 = kp.get("public_key")
    issuer_did = dk.did_key_from_base64url(pub_raw_b64)

    # subject 副本，附签发实例 URL（与 issuer DID 互补；随凭证一起被签名）
    subject_signed = dict(subject)
    subject_signed["issuerUrl"] = issuer_url

    credential = {
        "@context": VC_CONTEXTS,
        "type": ["VerifiableCredential", "AIShieldTrustCredential"],
        "id": cred_id or ("urn:aishield:vc:" + _sha256_hex(json.dumps(subject_signed, sort_keys=True))[:16]),
        "issuer": issuer_did,
        "issuanceDate": _utc_now_iso(),
        "credentialSubject": subject_signed,
    }
    body = cs.canonical_bytes({k: v for k, v in credential.items() if k != "proof"})
    sig = cs.sign(body, kp.get("private_key"), alg)
    is_ed25519 = (alg == cs.ALG_ED25519)
    credential["proof"] = {
        "type": "Ed25519Signature2020" if is_ed25519 else "HmacSha256Integrity",
        "cryptosuite": "ed25519-2020" if is_ed25519 else "hmac-sha256",
        "verificationMethod": issuer_did + "#keys-1",
        "proofPurpose": "assertionMethod",
        "created": _utc_now_iso(),
        "proofValue": sig,
        "third_party_verifiable": is_ed25519,
    }
    return credential


def verify_credential(credential: Dict[str, Any]) -> Dict[str, Any]:
    """验证凭证签名：从 issuer did:key 解公钥，校验 Data-Integrity 签名。

    返回 {valid, reason, third_party_verifiable}。篡改任一字段（proof 除外）或
    改签名都会被拒。
    """
    issuer = credential.get("issuer")
    proof = credential.get("proof") or {}
    if not dk or not dk.is_did_key(issuer):
        return {"valid": False, "reason": "issuer 不是 did:key，无法离线解公钥",
                "third_party_verifiable": False}
    try:
        pub_raw = dk.decode_did_key(issuer)
    except Exception as e:
        return {"valid": False, "reason": "did:key 解码失败: %s" % e,
                "third_party_verifiable": False}
    pub_b64 = cs._b64e(pub_raw)
    body = cs.canonical_bytes({k: v for k, v in credential.items() if k != "proof"})
    # cryptosuite（"ed25519-2020"）映射到 cs.verify 需要的 alg（"ed25519"）
    suite = proof.get("cryptosuite", "")
    alg = cs.ALG_ED25519 if suite.startswith("ed25519") else cs.ALG_HMAC
    ok = cs.verify(body, proof.get("proofValue", ""), pub_b64, alg)
    return {
        "valid": ok,
        "reason": None if ok else "签名校验失败（凭证被篡改或密钥不匹配）",
        "third_party_verifiable": bool(proof.get("third_party_verifiable")),
    }


# ───────────────────────────────────────────────────────────────────────────
# CT 式透明日志（append-only 哈希链）
# ───────────────────────────────────────────────────────────────────────────
class TransparentLog:
    """凭证签发透明日志：每次签发登记一条 entry，哈希链防篡改、可公开审计。"""

    def __init__(self, path: Optional[str] = None):
        self.path = path or os.path.join(_DATA, "trust_log.jsonl")

    def _entry_digest(self, entry: Dict[str, Any]) -> str:
        payload = {k: v for k, v in entry.items() if k != "hash"}
        return _sha256_hex(json.dumps(payload, ensure_ascii=False,
                                      sort_keys=True, separators=(",", ":")))

    def _last(self) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return None
        last = None
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        last = line
        except Exception:
            return None
        return json.loads(last) if last else None

    def append(self, credential: Dict[str, Any]) -> Dict[str, Any]:
        prev = self._last()
        seq = (prev.get("seq", 0) + 1) if prev else 1
        prev_hash = prev.get("hash", GENESIS_HASH) if prev else GENESIS_HASH
        entry = {
            "seq": seq,
            "ts": _utc_now_iso(),
            "credential_id": credential.get("id"),
            "issuer": credential.get("issuer"),
            "subject_sha256": _sha256_hex(
                json.dumps(credential.get("credentialSubject", {}),
                           sort_keys=True, ensure_ascii=False)),
            "prev_hash": prev_hash,
        }
        entry["hash"] = self._entry_digest(entry)
        with _lock:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def verify(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {"valid": True, "entries": 0, "note": "透明日志为空"}
        prev_hash = GENESIS_HASH
        expected_seq = 1
        count = 0
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e = json.loads(line)
                    except Exception:
                        return {"valid": False, "entries": count, "broken_at": lineno,
                                "reason": "JSON 解析失败"}
                    count += 1
                    if e.get("seq") != expected_seq:
                        return {"valid": False, "entries": count, "broken_at": lineno,
                                "reason": "序号断裂"}
                    if e.get("prev_hash") != prev_hash:
                        return {"valid": False, "entries": count, "broken_at": lineno,
                                "reason": "prev_hash 不匹配（日志被篡改或删除）"}
                    if self._entry_digest(e) != e.get("hash"):
                        return {"valid": False, "entries": count, "broken_at": lineno,
                                "reason": "entry 内容被篡改"}
                    prev_hash = e["hash"]
                    expected_seq += 1
        except Exception as exc:
            return {"valid": False, "entries": count, "reason": "读取失败: %s" % exc}
        return {"valid": True, "entries": count, "head_hash": prev_hash}


# ───────────────────────────────────────────────────────────────────────────
# 联邦协议 v0.1：安全聚合（零数据出域）
# ───────────────────────────────────────────────────────────────────────────
def secure_aggregate(node_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """联邦安全聚合：各节点只上报信号摘要（attack_vector_hash + count），不上传
    原始数据。全局聚合"新型攻击特征向量"出现频次与覆盖节点数。

    返回 {attack_vectors, total_signals, contributing_nodes}。

    零数据出域纪律：本函数只接收哈希 + 计数，原始 payload 永远留在各节点本地。
    """
    vectors: Dict[str, Dict[str, Any]] = {}
    nodes = set()
    for node in node_summaries:
        nid = node.get("node_id", "anon")
        nodes.add(nid)
        for v in node.get("attack_vectors", []):
            h = v.get("hash")
            c = int(v.get("count", 0) or 0)
            if not h:
                continue
            agg = vectors.setdefault(h, {"count": 0, "node_set": set()})
            agg["count"] += c
            agg["node_set"].add(nid)
    return {
        "attack_vectors": {
            h: {"count": a["count"], "nodes": len(a["node_set"])}
            for h, a in vectors.items()
        },
        "total_signals": sum(a["count"] for a in vectors.values()),
        "contributing_nodes": len(nodes),
    }


if __name__ == "__main__":
    kp = dict(zip(("alg", "private_key", "public_key"), cs.generate_keypair()))
    subj = {"type": "mcp_server", "url": "https://github.com/example/demo",
            "name": "demo", "score": 92, "level": "gold", "risk": "safe",
            "no_spawn_guarantee": True, "offline_scan": True}
    vc = issue_credential(subj, keypair=kp)
    print("VC id:", vc["id"])
    print("issuer:", vc["issuer"])
    print("verify:", verify_credential(vc))
    log = TransparentLog(path=os.path.join(_DATA, "trust_log_demo.jsonl"))
    log.append(vc)
    print("log verify:", log.verify())
