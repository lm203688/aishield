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
2. **红线不可破，但红线要分两级**（2026-10-02 真实队列实证后改）：
   * 硬红线：命中的是 **祈使式执行**（真实攻击指令形态）→ 停止累积 confidence，
     绝不允许 promote。误报优先于召回。
   * 软红线：命中的只是 **话题提及**（防御自述、docs 讲概念）→ 不杀候选，但禁
     止自动 promote，只能人工审到 draft。旧实现一刀切"任何 benign 命中即拒绝"，
     结果红线只会误杀、从不拦真误报。
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

from rule_corpus import (  # noqa: E402
    ATTACK_SAMPLES,
    BENIGN_CORPUS,
    IMPERATIVE_BENIGN_SAMPLES,
)

# ── 阈值（对齐 instinct）──────────────────────────────────────────────────
SEED_THRESHOLD = 1          # 1-4 hits  = seed
DRAFT_THRESHOLD = 5         # 5-9 hits  = draft
RULE_THRESHOLD = 10         # 10+ hits  = rule (auto-promote eligible)

# decay
STALE_DAYS = 90             # 90 天未观察到 → stale
DEAD_DAYS = 180             # 180 天 → 建议 reject

# ── 良性命中分类（话题提及 vs 祈使式执行）───────────────────────────────────
# 原始红线写的是"任何 BENIGN_CORPUS 命中即拒绝累积"。真实队列跑一遍就露馅了：
# 被拦的那两条命中的全是 **话题提及**（防御工具自述"已缓解工具投毒"、docs 里
# "ignore all previous instructions 是 canonical 越狱短语"），不是可执行攻击。
# 一刀切的结果是——**红线只用来误杀，从不用来拦真误报**，而且它会顺手把 0 命中
# 的 raw 候选直接置成 rejected 永久销案。
#
# 这里把良性命中分成两类，判定口径与 `scripts/audit_rules.py` 的 citation 子类同源
# （话题提及 ≠ 祈使式执行），但补了中文标记：BENIGN_CORPUS[11]/[25] 是中文安全
# 公告，audit_rules 的 CITATION_MARKERS 纯英文，会把它们判成 general。
_TOPIC_MARKER = re.compile(
    r"(?i)(?:defens\w*|guardrail|mitigat\w*|detect\w*|catches?|blocks?|prevents?|"
    r"is\s+(?:a\s+)?(?:security|safe)|canonical|threat\s+model|such\s+as|"
    r"patterns\s+like|fixture|e\.g\.|docs?\s*[:=]|"
    r"安全|缓解|防御|检测|拦截|审计|防护|加固| scanning|scanner|hardening)"
)

# 祈使式：句首/冒号后的可执行指令词。命中即硬红线，不给宽免。
_IMPERATIVE_MARKER = re.compile(
    r"(?im)(?:^\W*|\b(?:step\s*[:：]\s*)?)(?:"
    r"run\b|execute\b|exec\b|perform\b|runbook|invok\w*\b|call\b|"
    r"执行|运行|调用|请执行|运行下面|务必|排障步骤|运维手册|自动化流水线)"
)

# 低特异性 pattern：与雷达规则同口径——没有 `|` 交替、也没有有界间隔 `.{n,m}`
# 的裸关键词，只允许到 seed，不能靠语料命中数堆到 draft/rule。
_LOW_SPEC_RE = re.compile(r"\||\{\d+,?\d*\}")

STATE_ORDER = ("raw", "seed", "draft", "rule")


def _classify_benign_hit(sample: str) -> str:
    """把一条良性命中归类为 `topic_mention` 或 `imperative`。

    **默认走 imperative（即阻断）**：无法归进话题提及的一律按祈使处理。红线
    的失败方向是"该拦没拦"，宁可误杀候选也不能放过会误报生产的 pattern。
    """
    if _IMPERATIVE_MARKER.search(sample):
        return "imperative"
    if _TOPIC_MARKER.search(sample):
        return "topic_mention"
    return "imperative"


def _is_low_specificity(pattern: str) -> bool:
    """裸关键词（无 `|`、无有界间隔）→ True。裸关键词只允许到 seed 状态。"""
    if not pattern:
        return True
    return _LOW_SPEC_RE.search(pattern) is None


def _cap_state(state: str, cap: str) -> str:
    """把状态压到 cap 及以下（二者取更靠前的一档）。"""
    try:
        i, j = STATE_ORDER.index(state), STATE_ORDER.index(cap)
    except ValueError:
        return state
    return STATE_ORDER[min(i, j)]


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
    """评估单个候选，返回 confidence 统计。

    红线分两级（2026-10-02 真实队列实证后改）：

    * **硬红线**（`false_positive=True`）：pattern 命中 BENIGN_CORPUS 里的
      **祈使式执行**样本。这类命中意味着规则真的会打在"正在执行的攻击指令"上，
      必须拒绝累积。
    * **软红线**（`promotable=False`）：pattern 只命中 **话题提及**（防御自述、
      docs 讲概念）。不能因此杀候选——那会让红线退化成"只用来误杀"。但必须
      禁止自动 promote：这类 pattern 的命中主要来自散文，证据强度不足以支持
      直接进生产规则集，交给人工审阅到 draft 为止。

    另：attack_hits == 0 的 raw 候选**不受红线影响**（不得改写 status），
    否则一次 `--apply` 就能把没证据的候选永久销案。
    """
    attack_hits = 0
    topic_hits = 0
    imperative_hits = 0
    patterns = []
    for rule in data.get("rules", []):
        pat = rule.get("pattern", "")
        if not pat:
            continue
        patterns.append(pat)
        attack_hits += _count_hits(pat, ATTACK_SAMPLES)
        for sample in BENIGN_CORPUS:
            if _count_hits(pat, [sample]):
                if _classify_benign_hit(sample) == "topic_mention":
                    topic_hits += 1
                else:
                    imperative_hits += 1
        # IMPERATIVE_BENIGN_SAMPLES 是红线专用的"长得像攻击指令的良性运维步骤"。
        # 它们在 BENIGN_CORPUS 之外单独成组：红线的判据必须是"会不会打在真实攻击
        # 指令形态上"，光看提及类样本测不出这个。设计上这组一律按祈使式处理。
        for sample in IMPERATIVE_BENIGN_SAMPLES:
            if _count_hits(pat, [sample]):
                imperative_hits += 1

    low_spec = any(_is_low_specificity(p) for p in patterns)

    return {
        "attack_hits": attack_hits,
        "benign_hits": topic_hits + imperative_hits,
        "topic_hits": topic_hits,
        "imperative_hits": imperative_hits,
        "false_positive": imperative_hits > 0,
        "promotable": imperative_hits == 0,
        "low_specificity": low_spec,
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
            "false_positive": [],       # 祈使式 benign 命中（硬红线）
            "topic_mention": [],        # 话题提及命中（软红线，禁自动 promote）
            "low_specificity": [],      # 裸关键词 pattern，压到 seed
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

        # 低特异性（裸关键词）与话题提及命中都压到 seed 及以下，
        # 与雷达规则"裸关键词留 draft"的口径一致。
        cap = "seed" if (result["low_specificity"] or result["topic_hits"]) else "rule"
        state = _cap_state(cls["state"], cap)

        entry = {
            "file": fname,
            "signal_id": (data.get("signal") or {}).get("id", "?"),
            "title": (data.get("signal") or {}).get("title", "?")[:80],
            "attack_category": data.get("attack_category", "?"),
            "attack_hits": result["attack_hits"],
            "benign_hits": result["benign_hits"],
            "topic_hits": result["topic_hits"],
            "imperative_hits": result["imperative_hits"],
            "low_specificity": result["low_specificity"],
            "confidence": confidence,
            "state": state,
            "promotable": result["promotable"] and state in ("draft", "rule"),
            "last_observed": last_observed,
            "stale": cls["stale"],
            "stale_suggested_reject": cls["stale_suggested_reject"],
        }
        report["details"].append(entry)

        if result["false_positive"]:
            entry["note"] = (
                f"{result['imperative_hits']} 条祈使式 benign 命中（话题提及另计"
                f"{result['topic_hits']} 条）—— 硬红线，禁止累积 confidence"
            )
            report["buckets"]["false_positive"].append(fname)
        elif confidence >= RULE_THRESHOLD:
            report["buckets"]["ready_to_promote"].append(fname)
        elif confidence >= DRAFT_THRESHOLD:
            report["buckets"]["draft"].append(fname)
        elif confidence >= SEED_THRESHOLD:
            report["buckets"]["seed"].append(fname)
        else:
            report["buckets"]["raw"].append(fname)

        if entry["low_specificity"]:
            report["buckets"]["low_specificity"].append(fname)
        if result["topic_hits"] and not result["false_positive"]:
            report["buckets"]["topic_mention"].append(fname)
        if cls["stale"]:
            report["buckets"]["stale"].append(fname)

        # 写回 JSON（可选）
        if write_back:
            data["confidence"] = confidence
            data["last_observed"] = (
                now if confidence > (data.get("confidence") or 0) else last_observed
            )
            data["attack_hits_last_scan"] = result["attack_hits"]
            data["topic_hits_last_scan"] = result["topic_hits"]
            data["imperative_hits_last_scan"] = result["imperative_hits"]
            data["state"] = state
            data["stale"] = cls["stale"]
            if result["low_specificity"]:
                data["low_specificity"] = True
            if result["topic_hits"]:
                # 只标记"需人工审阅"，**不改 status**——候选必须留在队列里可复议。
                data["topic_mention_hit"] = (
                    f"{result['topic_hits']} 条良性样本命中属于话题提及（非祈使式执行），"
                    f"不阻断累积，但禁止自动 promote，需人工审阅"
                )
            if result["false_positive"]:
                # 硬红线只写 blocked 字段，不覆写 status。
                # 旧实现在这里把 status 直接改成 "rejected"，意味着**跑一次
                # --apply 就永久销毁一条候选**（无法复议、语料扩了也救不回来）。
                data["blocked_by"] = entry["note"]

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        # enforce：自动 promote confidence >= 10 且 promotable 的
        if enforce and confidence >= RULE_THRESHOLD and result["promotable"]:
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
        print(f"  FALSE POSITIVE BLOCKED (祈使式 benign 命中，硬红线): "
              f"{len(b['false_positive'])}")
        for f in b["false_positive"]:
            print(f"    ! {f}")
    if b["topic_mention"]:
        print(f"  TOPIC-MENTION ONLY (话题提及，不阻断但禁自动 promote): "
              f"{len(b['topic_mention'])}")
        for f in b["topic_mention"]:
            print(f"    ~ {f}")
    if b["low_specificity"]:
        print(f"  LOW SPECIFICITY (裸关键词，压到 seed): "
              f"{len(b['low_specificity'])}")
        for f in b["low_specificity"]:
            print(f"    ~ {f}")
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

    return _exit_code(report)


def _exit_code(report: Dict[str, Any]) -> int:
    """细粒度退出码。

    旧实现是 `false_positive>0 or raw>0`，用真实队列一跑就恒为 1（队列里必然
    有 raw 候选），接进 CI 就是永久红，真正的处置只有两种：长期红着，或者被人
    `|| true` 掉 —— 两种都堵死了硬红线的信号。

    0 = 干净，无需人工介入
    1 = 有硬红线命中（祈使式 benign 命中），需要人工决策
    2 = 有 >=180 天无新观察的候选，需要清理
    """
    if report["buckets"]["false_positive"]:
        return 1
    if report["details"] and all(
        d.get("stale_suggested_reject") for d in report["details"]
    ):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
