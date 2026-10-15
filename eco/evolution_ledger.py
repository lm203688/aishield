"""
eco/evolution_ledger.py — 规则自进化账本（RSES 的不可变脊柱）
==============================================================

解决的问题
----------
`scanner/_proposed/` 的候选规则此前只有两个终态：被 `promote_rule.py` 晋升
（写 data/radar_rules.json + 一条无结构的 promotion_ledger.jsonl 事件），
或者烂在目录里。整条"情报 → 草稿 → 自测 → 晋升 → 回滚"的链上，**没有一个
地方回答"这次规则集变更是谁批准的"**：

  * promotion_ledger.jsonl 是纯事件流水，无哈希链、无准入门槛 —— 事后可被
    任何人改写而无痕；
  * 元 agent（本仓 RSES 的草拟侧）如果直接获得晋升权，一次被劫持的草稿
    （或一次 prompt injection 污染的草稿会话）就能把任意正则写进线上规则集。

本模块是这条链的账本层，三条硬不变量：

  1. **追加 only + 哈希链**：每条记录含 prev_hash 与自身 hash（对除 hash 外
     字段的规范化 JSON 取 sha256）。改任何历史字段、删任何一行、调换顺序，
     `verify_chain()` 都在第一个断点报告出来。
  2. **特权动作必须带批准人**：promote / demote / rollback（都会改线上规则集）
     缺 `approved_by` 即 `ValueError` —— 不允许匿名规则集变更。
  3. **元 agent 永不晋升**：actor 以 `meta:` 前缀标识草拟侧 agent，对特权
     动作一律拒绝（哪怕它拿到了 approved_by）。这是结构约束之外的第二道防线
     —— `eco/meta_agent.py` 压根没有 promote/demote/rollback 方法，双保险。

与 promotion_ledger.jsonl 的分工（刻意保留两个账本）
----------------------------------------------------
  * `data/state/promotion_ledger.jsonl`（promote_rule.py 自带）：信息性事件
    流水，写失败不阻断晋升（既有契约，tests 钉死）。
  * 本账本：**问责脊柱**。晋升前必须先解决批准人（缺拒），晋升后落链。
    存储失败会 raise —— 一次没有记录的规则集变更就是完整性事故，不是
    "打个 warning 就好"的小事。

存储与并发
----------
默认落在 `data/state/evolution_ledger.jsonl`（与 promotion_ledger 同目录）。
追加语义 + 单写者纪律（所有调用方都经本模块的 `record()`）。它由
rule-promoter workflow 提交进 git，`.gitattributes` 配 `merge=union`
（追加型日志的语义正确的合并驱动，见 .github/auto-resolvable-paths.txt
的说明）。注意它**不**声明为"快照类"自动解决路径 —— 那是快照语义，追加型
日志的冲突必须走 union，不能走"取一方"。

CLI（workflow 的安全阀回滚也走它记账）::

    python eco/evolution_ledger.py --verify          # 校验整条链
    python eco/evolution_ledger.py --summary
    python eco/evolution_ledger.py --list
    python eco/evolution_ledger.py --record --action rollback \\
        --target data/radar_rules.json --actor ci:rule-promoter \\
        --approved-by ci:rule-promoter --rationale "测试红灯安全阀回滚"

零第三方依赖；时间戳用 UTC（与它互补的 promotion_ledger 一致）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
from datetime import datetime, timezone

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_STATE = os.path.join(_BASE, "data", "state")

#: 默认账本路径。测试与脚本可把 `path=` 传进 record()/verify_chain() 等函数，
#: 或直接改这个模块级常量（与 eco/runtime_governance 的 AUDIT_LOG 同模式）。
LEDGER_FILE = os.path.join(DATA_STATE, "evolution_ledger.jsonl")

GENESIS_HASH = "0" * 64

#: 全部合法动作。draft/test/reflect 是草拟侧（元 agent 可发）；
#: promote/demote/rollback 是特权侧（必须带 approved_by，元 agent 禁入）。
ACTIONS = ("draft", "test", "promote", "demote", "reflect", "rollback")
PRIVILEGED_ACTIONS = frozenset({"promote", "demote", "rollback"})

#: 元 agent 的 actor 前缀。前缀即信任域：meta:* 只许起草，不许改规则集。
META_ACTOR_PREFIX = "meta:"

_lock = threading.RLock()


# ---------------------------------------------------------------------------
# 序列化 / 哈希
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical(entry: dict) -> str:
    """除 hash 外的全字段规范化 JSON —— 哈希的唯一口径。

    sort_keys + 紧凑分隔符：同一份内容在任何进程、任何字典插入顺序下都得到
    同一串字节，否则 verify_chain() 会把无害的字段重排误报成篡改。
    """
    payload = {k: v for k, v in entry.items() if k != "hash"}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def _entry_hash(entry: dict) -> str:
    return hashlib.sha256(_canonical(entry).encode("utf-8")).hexdigest()


def _read_entries(path: str):
    """读账本。返回 (entries, problems)。

    problems 是 [(lineno, reason), ...]：无法解析/不是对象的行。坏行不让
    read 抛异常中断调用方，但 verify_chain() 会把第一个坏行报成断点 ——
    审计账本里的静默跳行正是最危险的那类假绿。
    """
    entries, problems = [], []
    if not os.path.exists(path):
        return entries, problems
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError as e:
                problems.append((lineno, "not valid JSON (%s)" % e))
                continue
            if not isinstance(obj, dict):
                problems.append((lineno, "not a JSON object"))
                continue
            entries.append(obj)
    return entries, problems


# ---------------------------------------------------------------------------
# 写：唯一入口
# ---------------------------------------------------------------------------
def record(*, actor: str, action: str, target: str, rationale: str = "",
           evidence: dict | None = None, approved_by: str | None = None,
           path: str | None = None) -> dict:
    """追加一条进化事件，返回该条目（含 seq / hash）。

    准入门槛（缺一即 ValueError，fail-closed）：
      * action ∈ ACTIONS；
      * actor / target 为非空字符串；
      * 特权动作（promote/demote/rollback）必须带 approved_by，且 actor 不得
        是元 agent（`meta:` 前缀）。

    存储失败会向上抛（与 promotion_ledger 的"不阻断"刻意不同）：一次没有
    入账的规则集变更 = 完整性事故，调用方必须看见。
    """
    if action not in ACTIONS:
        raise ValueError("unknown action %r (expected one of %s)"
                         % (action, list(ACTIONS)))
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("actor must be a non-empty string")
    if not isinstance(target, str) or not target.strip():
        raise ValueError("target must be a non-empty string")
    if action in PRIVILEGED_ACTIONS:
        if not isinstance(approved_by, str) or not approved_by.strip():
            raise ValueError(
                "action %r is privileged: approved_by is required "
                "(no anonymous rule-set changes)" % action)
        if actor.startswith(META_ACTOR_PREFIX):
            raise ValueError(
                "meta-agent %r cannot perform privileged action %r -- "
                "drafting agents never promote" % (actor, action))
    if evidence is not None and not isinstance(evidence, dict):
        raise ValueError("evidence must be a dict or None")
    if rationale is None:
        rationale = ""

    sink = path or LEDGER_FILE
    with _lock:
        entries, _problems = _read_entries(sink)
        # 尾条 hash 字段本身被改坏也照样追加：检测不依赖"能否继续写"——
        # verify_chain() 对每个条目先查 linkage 再重算 hash，第一个断点永远
        # 指向第一现场（被改的那条），不会被续上的新条目掩盖。反过来，若因
        # 链已断就拒绝追加，攻击者改一个字节就能冻结整条晋升循环（DoS）。
        prev_hash = entries[-1].get("hash") if entries else GENESIS_HASH
        entry = {
            "seq": len(entries) + 1,
            "ts": _utc_now_iso(),
            "actor": actor,
            "action": action,
            "target": target,
            "rationale": rationale,
            "evidence": evidence or {},
            "approved_by": approved_by,
            "prev_hash": prev_hash,
        }
        entry["hash"] = _entry_hash(entry)
        parent = os.path.dirname(sink)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(sink, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry


# ---------------------------------------------------------------------------
# 读 / 验
# ---------------------------------------------------------------------------
def list_entries(path: str | None = None) -> list:
    """按追加顺序返回全部可解析条目。"""
    entries, _problems = _read_entries(path or LEDGER_FILE)
    return entries


def verify_chain(path: str | None = None) -> dict:
    """校验整条链。返回 {ok, entries, broken_at, reason, head}。

    检查顺序（报第一个断点即停）：
      1. 文件可解析（坏行 → broken_at = 行号）；
      2. prev_hash  linkage（删行/调序 → 第一现场指向断行）；
      3. hash  重算（改任何历史字段 → 该条 hash 不符）；
      4. seq   连续（与 2 互补：纯删行时 2 先报）。
    """
    sink = path or LEDGER_FILE
    entries, problems = _read_entries(sink)
    if problems:
        lineno, reason = problems[0]
        return {"ok": False, "entries": len(entries), "broken_at": lineno,
                "reason": "line %d: %s" % (lineno, reason), "head": None}
    prev = GENESIS_HASH
    for i, e in enumerate(entries):
        seq = e.get("seq")
        if e.get("prev_hash") != prev:
            return {"ok": False, "entries": len(entries),
                    "broken_at": seq if isinstance(seq, int) else i + 1,
                    "reason": "entry #%s prev_hash mismatch (expected %s, found %s)"
                              % (seq, prev[:12], str(e.get("prev_hash"))[:12]),
                    "head": None}
        if _entry_hash(e) != e.get("hash"):
            return {"ok": False, "entries": len(entries),
                    "broken_at": seq if isinstance(seq, int) else i + 1,
                    "reason": "entry #%s hash mismatch -- content was tampered"
                              % seq,
                    "head": None}
        if seq != i + 1:
            return {"ok": False, "entries": len(entries), "broken_at": seq,
                    "reason": "entry seq discontinuity at position %d (found %s)"
                              % (i + 1, seq),
                    "head": None}
        prev = e["hash"]
    return {"ok": True, "entries": len(entries), "broken_at": None,
            "reason": None,
            "head": entries[-1]["hash"] if entries else GENESIS_HASH}


def summary(path: str | None = None) -> dict:
    """按动作 / actor 聚合的概览（含链校验结果），供观测面消费。"""
    entries = list_entries(path)
    by_action: dict = {}
    by_actor: dict = {}
    for e in entries:
        by_action[e.get("action", "?")] = by_action.get(e.get("action", "?"), 0) + 1
        by_actor[e.get("actor", "?")] = by_actor.get(e.get("actor", "?"), 0) + 1
    return {"entries": len(entries), "by_action": by_action,
            "by_actor": by_actor,
            "head": entries[-1].get("hash") if entries else GENESIS_HASH,
            "verified": verify_chain(path)["ok"]}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AIShield evolution ledger")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--list", action="store_true", help="List entries (newest first)")
    g.add_argument("--verify", action="store_true", help="Verify the hash chain")
    g.add_argument("--summary", action="store_true", help="Aggregate counts")
    g.add_argument("--record", action="store_true", help="Append one entry")
    ap.add_argument("--action", choices=list(ACTIONS))
    ap.add_argument("--target")
    ap.add_argument("--actor")
    ap.add_argument("--approved-by", dest="approved_by")
    ap.add_argument("--rationale", default="")
    ap.add_argument("--evidence-json", dest="evidence_json", default=None,
                    help="JSON object string for the evidence field")
    ap.add_argument("--path", default=None, help="Ledger file (default: %s)"
                    % os.path.relpath(LEDGER_FILE, _BASE))
    args = ap.parse_args(argv)

    path = args.path or LEDGER_FILE

    if args.record:
        if not args.action or not args.target or not args.actor:
            print("--record requires --action, --target and --actor")
            return 2
        evidence = None
        if args.evidence_json:
            try:
                evidence = json.loads(args.evidence_json)
            except ValueError as e:
                print("--evidence-json is not valid JSON: %s" % e)
                return 2
        try:
            entry = record(actor=args.actor, action=args.action,
                           target=args.target, rationale=args.rationale,
                           evidence=evidence, approved_by=args.approved_by,
                           path=path)
        except ValueError as e:
            print("REFUSED: %s" % e)
            return 2
        print("recorded #%s %s by %s (approved_by=%s)"
              % (entry["seq"], entry["action"], entry["actor"],
                 entry["approved_by"]))
        return 0

    if args.list:
        entries = list_entries(path)
        if not entries:
            print("ledger is empty (%s)" % os.path.relpath(path, _BASE))
            return 0
        print("%d entry(ies) in %s:\n" % (len(entries),
                                          os.path.relpath(path, _BASE)))
        for e in reversed(entries):
            print("  #%-3s %s  %-8s %-22s %s"
                  % (e.get("seq"), e.get("ts"), e.get("action"),
                     e.get("actor"), e.get("target")))
            if e.get("approved_by"):
                print("        approved_by: %s" % e["approved_by"])
        return 0

    if args.verify:
        res = verify_chain(path)
        if res["ok"]:
            print("chain OK: %d entry(ies), head=%s"
                  % (res["entries"], (res["head"] or "")[:16]))
            return 0
        print("CHAIN BROKEN at %s: %s" % (res["broken_at"], res["reason"]))
        return 1

    # 默认：summary
    s = summary(path)
    print(json.dumps(s, ensure_ascii=False, indent=2))
    return 0 if s["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
