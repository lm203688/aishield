#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield · Confidence-based Rule Promotion
==========================================

借鉴 WRG-11/instinct 项目的核心机制（raw→mature→rule 三态 + 90 天 decay），
把 `scanner/_proposed/*.json` 从"纯人工审阅"升级为"语料驱动的自动晋升"。

解决的问题
----------
当前 `_proposed/` 有 20 条 outstanding 候选堆积：
    - 每条带一个 pattern（正则表达式）
    - 需要人工审阅：正则写得对不对？误报率多少？
    - 结果是堆积不动（instinct 项目也踩过这个坑）

本脚本用 **ATTACK_SAMPLES + BENIGN_CORPUS**（单一真源在
`scripts/rule_corpus.py`）作为判据：

  * confidence = pattern 在 ATTACK_SAMPLES 上的命中条数
  * 准入红线 = 在 BENIGN_CORPUS 上零命中（任何 benign 命中立即拒绝累积）

状态机（对齐 instinct）
-----------------------
    raw (0 hits)     →  候选刚起草，无证据
    seed  (1-4)      →  有观察但证据不足
    draft (5-9)      →  证据充分，建议人工审阅后可 promote
    rule  (10+)      →  可自动 promote（配合 --enforce）

decay（对齐 instinct 的 90 天机制）
-----------------------------------
每次扫描更新 `last_observed` 时间戳。若 90 天未再观察到新的命中：
  * draft / rule → 标记 `stale: true`，但不主动降 confidence
  * 若连续 180 天未命中，标记 `stale_suggested_reject: true`

设计纪律
--------
1. **只读 + 可选写**：默认 `--check` 只报告，`--apply` 才写回 JSON。
2. **红线不可破**：任何在 BENIGN_CORPUS 上的命中都会阻止 confidence 累积，
   无论 ATTACK_SAMPLES 命中多少。误报优先于召回。
3. **零依赖**：只用标准库 + 本仓 `scripts/rule_corpus.py`。
4. **不重复劳动**：不修改 `promote_rule.py` 的 gate；本脚本产出的是
   `status_hint` 字段，`promote_rule.py` 可选择尊重或不尊重它。

Usage
-----
  python scripts/confidence_promotion.py                     # 默认 --check
  python scripts/confidence_promotion.py --check             # 只报告
  python scripts/confidence_promotion.py --apply             # 写回 JSON
  python scripts/confidence_promotion.py --report-json       # 机器可读输出
  python scripts/confidence_promotion.py --enforce           # 自动 promote ≥10 的
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import sys
from typing import Tuple, List, Dict, Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

PROPOSED_DIR = os.path.join(ROOT, "scanner", "_proposed")
RADAR_RULES = os.path.join(ROOT, "data", "radar_rules.json")

from rule_corpus import ATTACK_SAMPLES, BENIGN_CORPUS  # noqa: E402

# ── 阈值（对齐 instinct）──────────────────────────────────────────────────
SEED_THRESHOLD = 1          # 1-4 hits  = seed
DRAFT_THRESHOLD = 5         # 5-9 hits  = draft
RULE_THRESHOLD = 10         # 10+ hits  = rule (auto-promote eligible)

# decay
STALE_DAYS = 90             # 90 天未观察到 → stale
DEAD_DAYS = 180             # 180 天 → 建议 reject


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _classify(confidence: int, last_observed: str | None, now: str) -> Dict[str, Any]:
    """根据 confidence + last_observed 判定状态。"""
    if confidence == 0:
        base = "raw"
    elif confidence < DRAFT_THRESHOLD:
        base = "seed"
    elif confidence < RULE_THRESHOLD:
        base = "draft"
    else:
        base = "rule"

    stale = False
    stale_suggested_reject = False
    if last_observed and base in ("draft", "rule", "seed"):
        try:
            last = datetime.datetime.fromisoformat(last_observed)
            delta = datetime.datetime.now(datetime.timezone.utc) - last
            if delta.days >= STALE_DAYS:
                stale = True
            if delta.days >= DEAD_DAYS:
                stale_suggested_reject = True
        except (ValueError, TypeError):
            pass

    return {
        "confidence": confidence,
        "state": base,
        "stale": stale,
        "stale_suggested_reject": stale_suggested_reject,
    }


def _count_hits(pattern: str, samples: List[str]) -> int:
    """pattern 在 samples 上的命中条数（每 sample 至多计 1 次）。"""
    try:
        rx = re.compile(pattern, re.I | re.S)
    except re.error:
        return 0
    hits = 0
    for s in samples:
        if rx.search(s):
            hits += 1
    return hits


def _evaluate_candidate(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """评估单个候选，返回 confidence 统计。"""
    attack_hits = 0
    benign_hits = 0
    patterns = []
    for rule in data.get("rules", []):
        pat = rule.get("pattern", "")
        if not pat:
            continue
        patterns.append(pat)
        attack_hits += _count_hits(pat, ATTACK_SAMPLES)
        benign_hits += _count_hits(pat, BENIGN_CORPUS)

    # 红线：任何 benign 命中 → confidence = 0（且标记 false_positive）
    if benign_hits > 0:
        return {
            "attack_hits": attack_hits,
            "benign_hits": benign_hits,
            "false_positive": True,
            "patterns": patterns,
            "note": f"{benign_hits} benign 命中 —— 违反零误报红线，不累积 confidence",
        }

    return {
        "attack_hits": attack_hits,
        "benign_hits": 0,
        "false_positive": False,
        "patterns": patterns,
    }


def load_candidates() -> List[Tuple[str, Dict[str, Any]]]:
    cands = []
    for path in sorted(glob.glob(os.path.join(PROPOSED_DIR, "PROPOSED_*.json"))):
        try:
            with open(path, encoding="utf-8") as f:
                cands.append((path, json.load(f)))
        except (json.JSONDecodeError, OSError) as e:
            print(f"  skip {path}: {e}", file=sys.stderr)
    return cands


def run_check(write_back: bool = False, enforce: bool = False) -> Dict[str, Any]:
    """主入口。返回结构化报告。"""
    cands = load_candidates()
    now = _now()
    report = {
        "now": now,
        "total_candidates": len(cands),
        "attack_corpus_size": len(ATTACK_SAMPLES),
        "benign_corpus_size": len(BENIGN_CORPUS),
        "thresholds": {
            "seed": SEED_THRESHOLD,
            "draft": DRAFT_THRESHOLD,
            "rule": RULE_THRESHOLD,
            "stale_days": STALE_DAYS,
            "dead_days": DEAD_DAYS,
        },
        "buckets": {
            "ready_to_promote": [],     # confidence >= 10, no FP
            "draft": [],                # 5 <= confidence < 10
            "seed": [],                 # 1 <= confidence < 5
            "raw": [],                  # 0 hits
            "false_positive": [],       # benign 命中
            "already_rejected": [],
            "stale": [],
        },
        "details": [],
        "promoted_this_run": [],
    }

    for path, data in cands:
        fname = os.path.basename(path)
        if data.get("status") == "rejected":
            report["buckets"]["already_rejected"].append(fname)
            continue

        result = _evaluate_candidate(path, data)
        confidence = 0 if result["false_positive"] else result["attack_hits"]
        last_observed = data.get("last_observed")
        cls = _classify(confidence, last_observed, now)

        entry = {
            "file": fname,
            "signal_id": (data.get("signal") or {}).get("id", "?"),
            "title": (data.get("signal") or {}).get("title", "?")[:80],
            "attack_category": data.get("attack_category", "?"),
            "attack_hits": result["attack_hits"],
            "benign_hits": result["benign_hits"],
            "confidence": confidence,
            "state": cls["state"],
            "last_observed": last_observed,
            "stale": cls["stale"],
            "stale_suggested_reject": cls["stale_suggested_reject"],
        }
        report["details"].append(entry)

        if result["false_positive"]:
            entry["note"] = result["note"]
            report["buckets"]["false_positive"].append(fname)
        elif confidence >= RULE_THRESHOLD:
            report["buckets"]["ready_to_promote"].append(fname)
        elif confidence >= DRAFT_THRESHOLD:
            report["buckets"]["draft"].append(fname)
        elif confidence >= SEED_THRESHOLD:
            report["buckets"]["seed"].append(fname)
        else:
            report["buckets"]["raw"].append(fname)

        if cls["stale"]:
            report["buckets"]["stale"].append(fname)

        # 写回 JSON（可选）
        if write_back:
            data["confidence"] = confidence
            data["last_observed"] = (
                now if confidence > (data.get("confidence") or 0) else last_observed
            )
            data["attack_hits_last_scan"] = result["attack_hits"]
            data["benign_hits_last_scan"] = result["benign_hits"]
            data["state"] = cls["state"]
            data["stale"] = cls["stale"]
            if result["false_positive"]:
                data["false_positive_blocked"] = result["note"]
                data["status"] = "rejected"
                data["_rejected_reason"] = (
                    f"confidence promotion rejected: {result['note']}"
                )
            elif cls["stale_suggested_reject"]:
                data["stale_suggested_reject"] = True

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        # enforce：自动 promote confidence >= 10 且零 benign 命中的
        if enforce and confidence >= RULE_THRESHOLD and not result["false_positive"]:
            report["promoted_this_run"].append(fname)

    return report


def _print_report(report: Dict[str, Any]) -> None:
    b = report["buckets"]
    print(f"AIShield · Confidence Promotion")
    print(f"  corpus: attack={report['attack_corpus_size']}  "
          f"benign={report['benign_corpus_size']}")
    print(f"  candidates: {report['total_candidates']}")
    print()
    print(f"  ready_to_promote (confidence >= {RULE_THRESHOLD}): "
          f"{len(b['ready_to_promote'])}")
    for f in b["ready_to_promote"]:
        print(f"    + {f}")
    print()
    print(f"  draft ({DRAFT_THRESHOLD}-{RULE_THRESHOLD-1}): "
          f"{len(b['draft'])}")
    for f in b["draft"]:
        print(f"    ~ {f}")
    print()
    print(f"  seed ({SEED_THRESHOLD}-{DRAFT_THRESHOLD-1}): "
          f"{len(b['seed'])}")
    for f in b["seed"]:
        print(f"    . {f}")
    print()
    print(f"  raw (0 hits): {len(b['raw'])}")
    for f in b["raw"]:
        print(f"    - {f}")
    print()
    if b["false_positive"]:
        print(f"  FALSE POSITIVE BLOCKED ({len(b['false_positive'])}):")
        for f in b["false_positive"]:
            print(f"    ! {f}")
    if b["stale"]:
        print()
        print(f"  STALE (>= {STALE_DAYS} days without new observation): "
              f"{len(b['stale'])}")
        for f in b["stale"]:
            print(f"    $ {f}")
    if b["already_rejected"]:
        print()
        print(f"  already rejected: {len(b['already_rejected'])}")

    print()
    print(f"  thresholds: seed={SEED_THRESHOLD} draft={DRAFT_THRESHOLD} "
          f"rule={RULE_THRESHOLD} stale_days={STALE_DAYS}")

    if report["promoted_this_run"]:
        print()
        print(f"  PROMOTED (enforce): {len(report['promoted_this_run'])}")
        for f in report["promoted_this_run"]:
            print(f"    >> {f}")


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="AIShield confidence-based rule promotion")
    p.add_argument("--check", action="store_true",
                   help="仅报告，不写回 JSON（默认行为）")
    p.add_argument("--apply", action="store_true",
                   help="写回 JSON：confidence / state / last_observed")
    p.add_argument("--report-json", action="store_true",
                   help="以 JSON 输出结构化报告（机器可读）")
    p.add_argument("--enforce", action="store_true",
                   help="自动 promote confidence >= 10 的候选（需配合 --apply）")
    args = p.parse_args(argv)

    write_back = args.apply or args.enforce
    report = run_check(write_back=write_back, enforce=args.enforce)

    if args.report_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_report(report)

    # 退出码：有 false_positive 或 raw 候选 → 非零，便于 CI 触发关注
    has_problem = (
        len(report["buckets"]["false_positive"]) > 0
        or len(report["buckets"]["raw"]) > 0
    )
    return 1 if has_problem else 0


if __name__ == "__main__":
    sys.exit(main())
