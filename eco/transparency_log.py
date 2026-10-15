"""
eco/transparency_log.py — CT 式透明日志（Program D / FTM）

把"信任"从产品功能升级为**可审计的基础设施**：每一次凭证签发、每一份
运行时快照的摘要，都追加进一条公开可验证的追加式日志。

设计对齐 Certificate Transparency（RFC 6962）：

  · 条目 = 任意 JSON；leaf_hash = sha256(0x00 || canonical(entry))
  · Merkle 树：interior = sha256(0x01 || left || right)，奇数节点向上提升
  · STH（signed tree head）= {tree_size, root_hash, ts} 的 did:key
    Ed25519 签名 —— 服务方无法悄悄改写历史而不被 STH 校验发现
  · 包含证明（inclusion proof）：任一方可离线验证"某条目确实在
    root 里"，无需信任服务方

零第三方依赖；签名密钥与 verifiable_identity 的 active Ed25519 同一把
（JWKS 对外发布，did:key 自认证）——缺 cryptography 时降级 HMAC 并
诚实标注 third_party_verifiable=False。

这不是区块链：不需要共识、不需要代币、不需要全网节点。它解决一个
具体问题——**"服务方说了算"的日志不可信，签名树头让它可验**。
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

TZ = timezone(timedelta(hours=8))
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_PATH = os.path.join(_BASE, "api", "data", "transparency_log.jsonl")

GENESIS = "0" * 64


def _now_iso():
    return datetime.now(TZ).isoformat()


def _canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _leaf_hash(entry) -> str:
    return hashlib.sha256(b"\x00" + _canonical(entry)).hexdigest()


def _node_hash(left: str, right: str) -> str:
    return hashlib.sha256(
        b"\x01" + bytes.fromhex(left) + bytes.fromhex(right)).hexdigest()


def _merkle_root(leaves: List[str]) -> str:
    """RFC 6962：自底向上，奇数节点提升。空树返回创世哈希。"""
    if not leaves:
        return GENESIS
    level = list(leaves)
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level) - 1, 2):
            nxt.append(_node_hash(level[i], level[i + 1]))
        if len(level) % 2 == 1:
            nxt.append(level[-1])       # 奇数提升
        level = nxt
    return level[0]


def _largest_pow2_below(n: int) -> int:
    """小于 n 的最大 2 的幂（RFC 6962 的 k）。n>=2 时结果 >=1。"""
    k = 1
    while k * 2 < n:
        k *= 2
    return k


def _audit_path(leaves: List[str], index: int) -> List[str]:
    """RFC 6962 递归定义：PATH(m, D[n])。

    m < k：path = 左子树内 path : [右子树根]
    m >= k：path = 右子树内 path : [左子树根]
    """
    n = len(leaves)
    if n <= 1:
        return []
    if not (0 <= index < n):
        raise IndexError("leaf index out of range")
    k = _largest_pow2_below(n)
    if index < k:
        return _audit_path(leaves[:k], index) + [_merkle_root(leaves[k:])]
    return _audit_path(leaves[k:], index - k) + [_merkle_root(leaves[:k])]


def _root_from_path(index: int, leaf_hash: str, path: List[str], n: int) -> Optional[str]:
    """_audit_path 的逆运算：从 leaf + path 重算根。任何结构不符返回 None。"""
    if n <= 0:
        return None
    if n == 1:
        return leaf_hash if not path else None
    if len(path) < 1:
        return None
    k = _largest_pow2_below(n)
    head, last = path[:-1], path[-1]
    if index < k:
        left = _root_from_path(index, leaf_hash, head, k)
        return _node_hash(left, last) if left else None
    right = _root_from_path(index - k, leaf_hash, head, n - k)
    return _node_hash(last, right) if right else None


class TransparencyLog:
    """追加式透明日志（JSONL 落盘， Merkle 树内存重建）。"""

    def __init__(self, path: Optional[str] = None, signer=None, key_resolver=None):
        self.path = path or _DEFAULT_PATH
        self._signer = signer            # () -> key dict | None
        self.key_resolver = key_resolver  # (kid) -> key dict | None
        self._leaves: List[str] = []
        self._load()

    # ── 持久化 ──
    def _load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    lh = rec.get("leaf_hash")
                    if lh:
                        self._leaves.append(lh)
        except Exception:
            # 日志损坏：保留已读到的部分，从可继续处追加（不静默重签历史）
            pass

    def _append_line(self, rec: dict):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ── 签名 ──
    def _sign_sth(self, sth_body: dict) -> dict:
        key = self._signer() if self._signer else None
        if not key:
            sth_body["signature"] = None
            sth_body["unsigned_reason"] = "no active signing key"
            sth_body["third_party_verifiable"] = False
            return sth_body
        alg = str(key.get("alg") or "")
        try:
            from eco import crypto_sign as cs
            sig = cs.sign(_canonical(sth_body), str(key.get("private_key") or ""),
                          alg or None)
            sth_body["signature"] = sig
            sth_body["signature_alg"] = alg
            sth_body["signer_kid"] = _kid_of(key)
            sth_body["third_party_verifiable"] = bool(alg.lower() == "ed25519")
        except Exception as exc:
            sth_body["signature"] = None
            sth_body["unsigned_reason"] = f"sign failed: {type(exc).__name__}"
            sth_body["third_party_verifiable"] = False
        return sth_body

    # ── 追加 ──
    def append(self, entry: dict) -> Dict[str, Any]:
        """追加一个条目，返回 {seq, leaf_hash, root_hash, sth}。"""
        if not isinstance(entry, dict):
            raise ValueError("entry must be a dict")
        leaf = _leaf_hash(entry)
        self._leaves.append(leaf)
        seq = len(self._leaves)
        root = _merkle_root(self._leaves)
        self._append_line({
            "seq": seq, "ts": _now_iso(), "entry": entry, "leaf_hash": leaf,
        })
        sth = self._sign_sth({
            "tree_size": seq, "root_hash": root, "ts": _now_iso(),
        })
        return {"seq": seq, "leaf_hash": leaf, "root_hash": root, "sth": sth}

    # ── 查询 ──
    def sth(self) -> Dict[str, Any]:
        root = _merkle_root(self._leaves)
        return self._sign_sth({"tree_size": len(self._leaves),
                               "root_hash": root, "ts": _now_iso()})

    def root(self) -> str:
        return _merkle_root(self._leaves)

    def size(self) -> int:
        return len(self._leaves)

    def entries(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        rows = []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        rows.append(json.loads(line))
        except Exception:
            return []
        rows.reverse()
        return rows[:limit]

    # ── 包含证明与验证 ──
    def inclusion_proof(self, leaf_index: int) -> Dict[str, Any]:
        """0-based leaf_index → 包含证明（audit path + root）。"""
        if leaf_index < 0 or leaf_index >= len(self._leaves):
            return {"error": f"leaf_index 越界（0..{len(self._leaves) - 1}）"}
        return {
            "leaf_index": leaf_index,
            "leaf_hash": self._leaves[leaf_index],
            "tree_size": len(self._leaves),
            "audit_path": _audit_path(self._leaves, leaf_index),
            "root_hash": self.root(),
        }

    def verify_inclusion(self, leaf_hash: str, proof: Dict[str, Any]) -> bool:
        """第三方验证：给定 leaf_hash 与 audit_path，重算根并比对。

        结构不符（树大小、索引、路径长度对不上）一律 False —— 宁可
        拒掉真证明，也不放行一个"碰巧对上"的假证明。
        """
        try:
            idx = int(proof["leaf_index"])
            path = [str(h) for h in proof["audit_path"]]
            claimed_root = str(proof["root_hash"])
            size = int(proof["tree_size"])
        except Exception:
            return False
        if size != len(self._leaves) or not (0 <= idx < size):
            return False
        computed = _root_from_path(idx, leaf_hash, path, size)
        return computed is not None and computed == claimed_root

    def verify_sth(self, sth: Dict[str, Any]) -> Dict[str, Any]:
        """验证签名树头：签名有效 + root 与当前树一致（或明确不一致）。"""
        sig = sth.get("signature")
        if not sig:
            return {"valid": False, "reason": "STH 未签名",
                    "third_party_verifiable": False}
        body = {k: v for k, v in sth.items()
                if k not in ("signature", "signature_alg", "signer_kid",
                             "third_party_verifiable", "unsigned_reason")}
        key = self._resolve_key(sth.get("signer_kid"))
        if not key:
            return {"valid": False, "reason": f"签名者 kid 不在密钥环: {sth.get('signer_kid')}"}
        from eco import crypto_sign as cs
        ok = cs.verify(_canonical(body), sig, str(key.get("public_key") or ""),
                       str(key.get("alg") or ""))
        current = self.root()
        return {
            "valid": bool(ok),
            "reason": "ok" if ok else "签名校验失败",
            "root_matches_current_tree": sth.get("root_hash") == current,
            "current_root": current,
        }

    def _resolve_key(self, kid):
        if self.key_resolver is not None:
            return self.key_resolver(kid)
        try:
            from eco import verifiable_identity as vi
            ring = vi.SigningKeyRing().load()
            for cand in [ring.active()] + ring.deprecated():
                if cand and _kid_of(cand) == kid:
                    return cand
        except Exception:
            pass
        return None

    def status(self) -> Dict[str, Any]:
        return {"entries": len(self._leaves), "root_hash": self.root(),
                "path": os.path.basename(self.path)}


def _kid_of(key: dict) -> str:
    import hashlib as _hl
    return _hl.sha256(str(key.get("public_key") or "").encode("ascii")).hexdigest()[:12]


# ── 模块级便捷 API ──
_default: Optional[TransparencyLog] = None


def get_log() -> TransparencyLog:
    global _default
    if _default is None:
        _default = TransparencyLog()
    return _default


def append(entry: dict) -> Dict[str, Any]:
    return get_log().append(entry)


def sth() -> Dict[str, Any]:
    return get_log().sth()


if __name__ == "__main__":
    log = TransparencyLog(path=os.path.join(
        os.environ.get("TEMP", "."), "tlog_demo.jsonl"))
    r = log.append({"demo": "entry-1"})
    print("append:", r["seq"], r["leaf_hash"][:16])
    print("root:", log.root()[:16])
    proof = log.inclusion_proof(0)
    print("verify inclusion:", log.verify_inclusion(r["leaf_hash"], proof))
    print("sth:", json.dumps(log.sth(), ensure_ascii=False)[:200])
