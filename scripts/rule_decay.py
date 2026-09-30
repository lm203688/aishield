#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield · Rule Decay
=====================

配套 confidence_promotion.py：晋升是入口，衰减是出口。一个规则集如果只
进不出，90 天就会膨胀成一堆"话题提及型"高误报规则，扫描器信誉随之崩塌。

核心机制（对齐 instinct 项目）
------------------------------
1. 每次运行记录一次"评估快照"到 `data/state/rule_hits.jsonl`（追加，不覆盖）。
2. 每条 live 规则在快照里有：命中数 / 语料规模 / 时间戳。
3. **dormant**：最近 N 次快照命中数 ≤ 阈值 M → 标记 dormant（不删，但降权）。
4. **retire**：连续 K 次快照 0 命中 → 标记 retire_suggested（建议人工确认删除）。
5. **recovery**： dormant/retire_suggested 的规则如果又命中了 → 恢复 active。

数据来源
--------
* 固定基准：`scripts/rule_corpus.py` 的 ATTACK_SAMPLES / BENIGN_CORPUS
* 可选外部：`--hits-file <path>` 从外部扫描日志追加（JSONL 格式：
  `{"ts": "...", "pattern_hash": "...", "hits": N}`）

设计纪律
--------
* 只写 state，不改 radar_rules.json 本身（人工审查后手动删）。
* 与 confidence_promotion 共享 `--apply` 语义（默认 dry-run）。
* 零外部依赖。

Usage
-----
  python scripts/rule_decay.py                    # dry-run 报告
  python scripts/rule_decay.py --apply             # 追加快照 + 更新 state
  python scripts/rule_decay.py --report-json        # 机器可读输出
  python scripts/rule_decay.py --hits-file X.jsonl  # 追加外部命中记录
  python scripts/rule_decay.py --retire             # 从 radar_rules.json 移除
                                                          # retire_suggested 规则
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
from typing import Dict, Any, List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

RADAR_RULES = os.path.join(ROOT, "data", "radar_rules.json")
GENERATED_RULES = os.path.join(ROOT, "data", "generated_rules.json")
HITS_LOG = os.path.join(ROOT, "data", "state", "rule_hits.jsonl")
DECAY_STATE = os.path.join(ROOT, "data", "state", "rule_decay.json")

from rule_corpus import ATTACK_SAMPLES, BENIGN_CORPUS  # noqa: E402

# ── 阈值（对齐 instinct）──────────────────────────────────────────────────
HIST_KEEP = 90            # 保留最多 90 次快照
DORMANT_WINDOW = 14       # 最近 14 次快照
DORMANT_HIT_MAX = 0       # 14 次窗口内命中 ≤ 0 次 → dormant
RETIRE_WINDOW = 30        # 最近 30 次快照
RETIRE_HIT_MAX = 0        # 30 次窗口内命中 ≤ 0 次 → retire_suggested


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _pattern_hash(pattern: str) -> str:
    """stable hash for cross-run identity."""
    return hashlib.sha1(pattern.encode("utf-8")).hexdigest()[:12]


def _count_hits(pattern: str, samples: List[str]) -> int:
    try:
        rx = re.compile(pattern, re.I | re.S)
    except re.error:
        return 0
    return sum(1 for s in samples if rx.search(s))


def load_radar_rules() -> List[Tuple[str, Dict[str, Any]]]:
    """加载 radar_rules.json 里的所有 rule，返回 [(hash, meta), ...]。"""
    if not os.path.exists(RADAR_RULES):
        return []
    with open(RADAR_RULES, encoding="utf-8") as f:
        d = json.load(f)
    rules = d.get("rules", {})
    out = []
    for pattern, meta in rules.items():
        out.append((
            _pattern_hash(pattern),
            {"pattern": pattern, "meta": meta},
        ))
    return out


def load_generated_pattern_rules() -> List[Tuple[str, Dict[str, Any]]]:
    """加载 generated_rules.json 里的 pattern_rules。"""
    if not os.path.exists(GENERATED_RULES):
        return []
    with open(GENERATED_RULES, encoding="utf-8") as f:
        d = json.load(f)
    out = []
    for pattern, meta in (d.get("pattern_rules") or {}).items():
        out.append((
            _pattern_hash(pattern),
            {"pattern": pattern, "meta": meta},
        ))
    return out


def evaluate_all(rules: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """对每条规则算一次 ATTACK_SAMPLES / BENIGN_CORPUS 命中。"""
    snap = {
        "ts": _now(),
        "attack_corpus_size": len(ATTACK_SAMPLES),
        "benign_corpus_size": len(BENIGN_CORPUS),
        "rules": {},
    }
    for h, meta in rules:
        pat = meta["pattern"]
        snap["rules"][h] = {
            "pattern": pat[:200],
            "attack_hits": _count_hits(pat, ATTACK_SAMPLES),
            "benign_hits": _count_hits(pat, BENIGN_CORPUS),
            "hash": h,
        }
    return snap


def append_snapshot(snap: Dict[str, Any]) -> None:
    """追加快照到 JSONL（保留最近 HIST_KEEP 条）。"""
    os.makedirs(os.path.dirname(HITS_LOG), exist_ok=True)
    lines = []
    if os.path.exists(HITS_LOG):
        with open(HITS_LOG, encoding="utf-8") as f:
            lines = f.readlines()
    lines.append(json.dumps(snap, ensure_ascii=False) + "\n")
    # 保留最近 HIST_KEEP 条
    lines = lines[-HIST_KEEP:]
    with open(HITS_LOG, "w", encoding="utf-8") as f:
        f.writelines(lines)


def read_snapshots() -> List[Dict[str, Any]]:
    if not os.path.exists(HITS_LOG):
        return []
    snaps = []
    with open(HITS_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                snaps.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return snaps


def compute_state(snapshots: List[Dict[str, Any]],
                  rules: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """根据快照历史计算每条规则的状态。"""
    state = {
        "evaluated_at": _now(),
        "total_snapshots": len(snapshots),
        "thresholds": {
            "dormant_window": DORMANT_WINDOW,
            "dormant_hit_max": DORMANT_HIT_MAX,
            "retire_window": RETIRE_WINDOW,
            "retire_hit_max": RETIRE_HIT_MAX,
        },
        "rules": {},
        "summary": {
            "active": 0,
            "dormant": 0,
            "retire_suggested": 0,
            "total": len(rules),
        },
    }

    for h, meta in rules:
        # 收集该 hash 在所有快照中的命中数
        history = []
        for snap in snapshots:
            entry = snap.get("rules", {}).get(h)
            if entry is not None:
                history.append(entry.get("attack_hits", 0))

        total_hits = sum(history)
        last_hit_index = -1
        for i, hits in enumerate(history):
            if hits > 0:
                last_hit_index = i

        # 状态判定
        recent_dormant_window = history[-DORMANT_WINDOW:] if history else []
        recent_retire_window = history[-RETIRE_WINDOW:] if history else []

        dormant = (
            len(recent_dormant_window) >= DORMANT_WINDOW
            and sum(recent_dormant_window) <= DORMANT_HIT_MAX
        )
        retire = (
            len(recent_retire_window) >= RETIRE_WINDOW
            and sum(recent_retire_window) <= RETIRE_HIT_MAX
        )

        if retire:
            status = "retire_suggested"
        elif dormant:
            status = "dormant"
        else:
            status = "active"

        # 首次观察时间（如果有）
        first_seen = snapshots[0].get("ts") if snapshots else None
        last_seen = snapshots[-1].get("ts") if snapshots else None

        state["rules"][h] = {
            "pattern_prefix": meta["pattern"][:100],
            "status": status,
            "total_snapshots": len(history),
            "total_hits": total_hits,
            "last_hit_index": last_hit_index,
            "first_seen": first_seen,
            "last_seen": last_seen,
        }
        state["summary"][status] += 1

    return state


def load_external_hits(path: str) -> List[Dict[str, Any]]:
    """从外部 JSONL 文件读取命中记录。每行格式：
       {"ts": "...", "pattern_hash": "...", "hits": N}
    """
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def merge_external_into_snapshots(snapshots: List[Dict[str, Any]],
                                   external: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """把外部命中记录合并到最近一次快照的对应 hash 上。"""
    if not external or not snapshots:
        return snapshots
    # 找最新快照
    latest = snapshots[-1]
    for rec in external:
        h = rec.get("pattern_hash")
        hits = rec.get("hits", 0)
        if h and h in latest.get("rules", {}):
            latest["rules"][h]["attack_hits"] = hits
    return snapshots


def _print_report(state: Dict[str, Any]) -> None:
    s = state["summary"]
    print(f"AIShield · Rule Decay")
    print(f"  snapshots: {state['total_snapshots']}")
    print(f"  total rules: {s['total']}")
    print()
    print(f"  active:           {s['active']}")
    print(f"  dormant:          {s['dormant']}")
    print(f"  retire_suggested: {s['retire_suggested']}")

    t = state["thresholds"]
    print()
    print(f"  thresholds: dormant_window={t['dormant_window']}  "
          f"retire_window={t['retire_window']}  "
          f"dormant_hit_max={t['dormant_hit_max']}  "
          f"retire_hit_max={t['retire_hit_max']}")

    retire = [h for h, r in state["rules"].items()
              if r["status"] == "retire_suggested"]
    if retire:
        print()
        print(f"  RETIRE_SUGGESTED ({len(retire)}) — 30 次快照内 0 命中：")
        for h in retire:
            r = state["rules"][h]
            print(f"    ! {h}  hits={r['total_hits']}  {r['pattern_prefix'][:60]}")

    dormant = [h for h, r in state["rules"].items()
               if r["status"] == "dormant"]
    if dormant:
        print()
        print(f"  DORMANT ({len(dormant)}) — 14 次快照内 0 命中：")
        for h in dormant[:20]:
            r = state["rules"][h]
            print(f"    $ {h}  hits={r['total_hits']}  {r['pattern_prefix'][:60]}")


def _write_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(DECAY_STATE), exist_ok=True)
    with open(DECAY_STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def retire_rules_from_source(state: Dict[str, Any]) -> int:
    """从 radar_rules.json 移除所有 retire_suggested 的规则。"""
    retire_hashes = [h for h, r in state["rules"].items()
                     if r["status"] == "retire_suggested"]
    if not retire_hashes:
        return 0
    if not os.path.exists(RADAR_RULES):
        return 0
    with open(RADAR_RULES, encoding="utf-8") as f:
        d = json.load(f)
    rules = d.get("rules", {})
    removed = 0
    for h in retire_hashes:
        # 反查 pattern
        for pat, meta in list(rules.items()):
            if _pattern_hash(pat) == h:
                del rules[pat]
                removed += 1
                break
    if removed:
        with open(RADAR_RULES, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
    return removed


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="AIShield rule decay engine")
    p.add_argument("--apply", action="store_true",
                   help="追加快照 + 更新 decay state")
    p.add_argument("--report-json", action="store_true")
    p.add_argument("--hits-file", default=None,
                   help="从外部 JSONL 追加命中记录到最新快照")
    p.add_argument("--retire", action="store_true",
                   help="从 radar_rules.json 移除所有 retire_suggested 规则（危险）")
    args = p.parse_args(argv)

    # 1. 加载规则
    radar = load_radar_rules()
    generated = load_generated_pattern_rules()
    all_rules = radar + generated

    # 2. 生成新快照
    snap = evaluate_all(radar)  # 只统计 radar rules（generated 用不到）

    # 3. 合并外部命中（如有）
    external = load_external_hits(args.hits_file) if args.hits_file else []

    # 4. 读历史快照
    snapshots = read_snapshots()

    if args.apply or args.retire:
        append_snapshot(snap)
        snapshots = read_snapshots()  # 重新读
        if external:
            snapshots = merge_external_into_snapshots(snapshots, external)

    # 5. 计算状态
    state = compute_state(snapshots, radar)

    # 6. 输出
    if args.report_json:
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        _print_report(state)

    if args.apply or args.retire:
        _write_state(state)

    # 7. 执行 retire
    if args.retire:
        removed = retire_rules_from_source(state)
        print(f"\nretired {removed} rules from {os.path.relpath(RADAR_RULES, ROOT)}")

    # 退出码
    return 1 if state["summary"]["retire_suggested"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
