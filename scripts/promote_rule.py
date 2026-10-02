#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield · Rule Promotion Gate
==============================

Closes the last link of the Tech Radar loop:

    signal -> draft candidate -> [THIS GATE] -> live detection rule

`scripts/tech_radar.py` drafts candidates into `scanner/_proposed/*.json`.
Without a gate those drafts either rot in place or get hand-copied into
`scanner/rules.py` with no verification -- which is how a scanner acquires
false positives and loses the trust it sells.

This tool refuses to promote anything that fails:

  1. schema      -- required fields present, status == "ready"
  2. no TODOs    -- every placeholder actually filled in
  3. regex       -- each pattern compiles
  4. not-too-broad -- pattern must not match trivial/empty strings
  5. duplicate   -- pattern not already in the live rule set
  6. benign corpus -- ZERO matches against known-good samples
                      (a rule that fires on benign input is worse than no rule)

Promoted rules land in `data/radar_rules.json`, loaded by scanner/rules.py at
import time. Deliberately a separate file from `data/generated_rules.json`,
which `intel_to_rules.py` regenerates wholesale and would otherwise erase
radar-promoted rules on its next run.

Usage:
  python scripts/promote_rule.py --check                # validate all drafts
  python scripts/promote_rule.py --shadow               # DRY RUN: full verdict, writes nothing
  python scripts/promote_rule.py --promote <file.json>  # promote one (enforce)
  python scripts/promote_rule.py --promote-all          # promote every "ready"
  python scripts/promote_rule.py --promote-all --strict # ...but refuse dead rules
  python scripts/promote_rule.py --list                 # show live radar rules
  python scripts/promote_rule.py --list-snapshots       # show rollback points
  python scripts/promote_rule.py --rollback             # roll back to newest
  python scripts/promote_rule.py --rollback <snap.json> # roll back to one
  python scripts/promote_rule.py --ledger               # show promote/rollback log

Shadow vs enforce (see the module docstring of the shadow section below):
  shadow   -- observe only. Runs validation + effect measurement against a
              simulated store, writes nothing, exits 1 if anything is wrong.
              Wire this into CI so the gate is observable without committing.
  enforce  -- --promote / --promote-all. Refuses on validation failure or a
              benign-corpus false positive (always). A zero-catch ("dead")
              rule is refused only under --strict; otherwise it is promoted
              with a loud warning, because a brand-new attack type will not
              appear in the fixed ATTACK_SAMPLES corpus.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

PROPOSED_DIR = os.path.join(ROOT, "scanner", "_proposed")
RADAR_RULES = os.path.join(ROOT, "data", "radar_rules.json")
SNAPSHOT_DIR = os.path.join(ROOT, "data", "snapshots")
LEDGER = os.path.join(ROOT, "data", "state", "promotion_ledger.jsonl")
KEEP_SNAPSHOTS = 20

VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}

# 良性语料单一真源在 scripts/rule_corpus.py（此前与 radar_effect.py 各存一份
# 互为镜像，扩宽时互相看不见 —— 见该模块 docstring）。
from rule_corpus import BENIGN_CORPUS  # noqa: E402


def _import_radar_effect():
    """Late import: radar_effect pulls in the corpus too; keep the chain lazy."""
    if SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, SCRIPTS_DIR)
    import radar_effect
    return radar_effect


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_candidates():
    out = []
    for p in sorted(glob.glob(os.path.join(PROPOSED_DIR, "PROPOSED_*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                out.append((p, json.load(f)))
        except Exception as e:
            out.append((p, {"_parse_error": str(e)}))
    return out


def load_radar_rules():
    if not os.path.exists(RADAR_RULES):
        return {"version": 1, "rules": {}, "provenance": {}}
    try:
        with open(RADAR_RULES, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": 1, "rules": {}, "provenance": {}}


def live_patterns():
    """Every pattern already active, so we never promote a duplicate."""
    pats = set(load_radar_rules().get("rules", {}))
    try:
        sys.path.insert(0, ROOT)
        from scanner import rules as scanner_rules  # noqa: WPS433
        pats |= set(getattr(scanner_rules, "ALL_RULES", {}))
    except Exception:
        pass  # validation still works without the live set
    return pats


# ---------------------------------------------------------------------------
# Snapshot / ledger / rollback
# ---------------------------------------------------------------------------
# 2026-09-16 补：promote() 原先直接 open("w") 覆盖 data/radar_rules.json，
# 且 _evaluate_effect() 是**事后**best-effort 告警（docstring 明写
# "effect measurement must never break promotion"）。也就是说一条误报规则会
# 先落库成为线上规则，然后才被报告为误报 —— 而此时已经没有任何回滚手段，
# 只能手改 JSON 或 git revert。这是 PenguinHarness 的 snapshot+rollback 想解决的
# 同一个问题：优化循环里每一次改动都必须可撤销。
def _utc_stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _iso_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _unique_snapshot_path():
    """同一秒内多次晋升/回滚不得互相覆盖。"""
    base = os.path.join(SNAPSHOT_DIR, "radar_rules.%s.json" % _utc_stamp())
    n = 1
    while os.path.exists(base):
        base = os.path.join(SNAPSHOT_DIR, "radar_rules.%s.%d.json" % (_utc_stamp(), n))
        n += 1
    return base


def snapshot_current():
    """把当前 radar_rules.json 快照下来。文件不存在则跳过（首次晋升）。"""
    if not os.path.exists(RADAR_RULES):
        return None
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    dest = _unique_snapshot_path()
    shutil.copyfile(RADAR_RULES, dest)
    return dest


def list_snapshots():
    """按时间倒序返回 [(path, size, mtime_iso)]，最新在前。"""
    if not os.path.isdir(SNAPSHOT_DIR):
        return []
    out = []
    for p in glob.glob(os.path.join(SNAPSHOT_DIR, "radar_rules.*.json")):
        try:
            st = os.stat(p)
        except OSError:
            continue
        out.append((p, st.st_size,
                    datetime.datetime.fromtimestamp(st.st_mtime,
                                                    datetime.timezone.utc)
                    .strftime("%Y-%m-%dT%H:%M:%SZ")))
    return sorted(out, key=lambda t: t[2], reverse=True)


def prune_snapshots(keep=KEEP_SNAPSHOTS):
    """只保留最近 keep 份。用 os.replace 移入 .pruned/ 而非删除：
    删除类 API 在沙箱里可能被守卫吞掉，移动不受限且可人工恢复。"""
    stale = list_snapshots()[keep:]
    if not stale:
        return []
    pruned = os.path.join(SNAPSHOT_DIR, ".pruned")
    os.makedirs(pruned, exist_ok=True)
    moved = []
    for p, _sz, _ts in stale:
        dest = os.path.join(pruned, os.path.basename(p))
        n = 1
        while os.path.exists(dest):
            dest = os.path.join(pruned, "%s.%d" % (os.path.basename(p), n))
            n += 1
        os.replace(p, dest)
        moved.append(dest)
    return moved


def ledger_append(event, **fields):
    """追加一条不可变事件记录。失败不得阻断晋升本身。"""
    entry = {"ts": _iso_now(), "event": event}
    entry.update({k: v for k, v in fields.items() if v not in (None, "", [])})
    try:
        os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print("  warning: could not append promotion ledger (%s)" % e)
    return entry


def load_ledger():
    out = []
    if not os.path.exists(LEDGER):
        return out
    try:
        with open(LEDGER, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    except Exception:
        pass
    return out


def rollback(target=None):
    """回滚到某份快照（默认最新）。先快照当前状态，防止回滚方向搞反。

    返回 (exit_code, message)。
    """
    snaps = list_snapshots()
    if target is None:
        if not snaps:
            return 2, "没有可用快照，无法回滚"
        target = snaps[0][0]
    elif not os.path.isabs(target):
        target = os.path.join(SNAPSHOT_DIR, target)
    if not os.path.exists(target):
        return 2, "快照不存在: %s" % target

    before = snapshot_current()
    shutil.copyfile(target, RADAR_RULES)
    ledger_append("rollback", restored_from=os.path.basename(target),
                  previous_snapshot=os.path.basename(before) if before else None,
                  timestamp=os.path.basename(target))
    print("rolled back to %s (previous state kept at %s)"
          % (os.path.basename(target),
             os.path.basename(before) if before else "n/a"))
    return 0, target


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate(path, data, known_patterns=None):
    """Return (ok: bool, problems: list[str])."""
    problems = []
    name = os.path.basename(path)

    if "_parse_error" in data:
        return False, [f"{name}: invalid JSON -- {data['_parse_error']}"]

    status = data.get("status")
    if status != "ready":
        return False, [f"{name}: status is '{status}', expected 'ready' "
                       f"(fill in the rules, then flip the flag)"]

    for field in ("signal", "attack_category", "rules"):
        if not data.get(field):
            problems.append(f"{name}: missing required field '{field}'")
    if problems:
        return False, problems

    rules = data.get("rules") or []
    if not isinstance(rules, list) or not rules:
        return False, [f"{name}: 'rules' must be a non-empty list"]

    known = known_patterns if known_patterns is not None else live_patterns()

    for i, r in enumerate(rules):
        tag = f"{name}[{i}]"
        pattern = (r.get("pattern") or "").strip()
        desc = (r.get("description") or "").strip()
        sev = (r.get("severity") or "").strip().lower()

        if not pattern or pattern.upper().startswith("TODO"):
            problems.append(f"{tag}: pattern still a TODO placeholder")
            continue
        if not desc or desc.upper().startswith("TODO"):
            problems.append(f"{tag}: description still a TODO placeholder")
        if sev not in VALID_SEVERITIES:
            problems.append(f"{tag}: severity '{sev}' not in {sorted(VALID_SEVERITIES)}")

        try:
            compiled = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            problems.append(f"{tag}: regex does not compile -- {e}")
            continue

        # Guard against catastrophically broad patterns.
        if compiled.search("") or compiled.search("a"):
            problems.append(f"{tag}: pattern matches empty/trivial input -- too broad")
            continue
        if len(pattern) < 6:
            problems.append(f"{tag}: pattern suspiciously short ({len(pattern)} chars)")

        if pattern in known:
            problems.append(f"{tag}: duplicate -- pattern already active")

        # The decisive test: must not fire on known-good input.
        for j, sample in enumerate(BENIGN_CORPUS):
            if compiled.search(sample):
                problems.append(
                    f"{tag}: FALSE POSITIVE on benign sample #{j} -- "
                    f"matched {compiled.search(sample).group()[:60]!r}"
                )
                break

    return (not problems), problems


# ---------------------------------------------------------------------------
# Shadow / enforce dual mode
# ---------------------------------------------------------------------------
# 借鉴 TypeSafe pi-jev 的 shadow / enforce 双模式：闸门可以"只观测、不改变"地
# 连续运行（shadow），也可以真正生效（enforce）。
#
# 只借这个**模式区分**，明确不借它的默认值——pi-jev 的所有错误路径都 fail-OPEN
# （缺 key / 超时 / 429 全部放行工具调用）。本工具的品牌就是 fail-closed，
# 任何不确定一律拒，所以 shadow 只用于观测，判定失败不会降级成放行。
#
# 三种判定，按严格度递增：
#   promote -- 校验通过且能在攻击语料上命中
#   warn    -- 校验通过但零命中（catch=false）：规则是死重，不是安全问题
#   refuse  -- 校验失败或误报良性语料：绝不落库
#
# 为什么 warn 不直接等于 refuse：雷达规则来自**新**信号，ATTACK_SAMPLES 是固定
# 语料，全新攻击类型天然不在其中。把 catch=false 当硬拒绝会让循环彻底停摆
# （假阴性陷阱）；把它当安全问题又是过度收紧。所以 warn 走"默认放行 + 大声
# 告警 + --strict 显式收紧"，而不是二元。

SHADOW_ARCHIVE_SUBDIR = "shadow-refused"


def _live_counts():
    """Current rule counts from the live engine; None if unreadable.

    Deliberately never raises — a shadow run must be observable even when the
    scanner package cannot be imported in the current environment.
    """
    try:
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        import importlib
        import scanner.rules as scanner_rules
        importlib.reload(scanner_rules)
        return scanner_rules.get_rule_count("mcp"), scanner_rules.get_rule_count("skill")
    except Exception:
        return None


def _provenance_entry(data, promoted_from):
    """构造一条 provenance 记录。

    2026-09-19 增补 `trigger` / `intended_effect`（借鉴 PrimeIntellect prime-agent 的
    Continual Harness：每一次对 rules / prompts / memories 的写入都带 trigger 与
    intended effect，且可回滚）。原来的 provenance 只回答「它从哪来」，回答不了
    「当初为什么觉得该加它、期望它改变什么」—— 半年后要判断一条规则是否还该留着，
    缺的正是后者。

    向后兼容：老记录没有这两个字段，加载器视为 legacy、不报错（契约测试覆盖）。
    候选文件可以自带 `trigger` / `intended_effect`；没带就**从已有的真实字段派生**
    （来源情报标题 / 攻击类别），不编造内容。
    """
    signal = data.get("signal") or {}
    category = data.get("attack_category", "") or ""
    trigger = (data.get("trigger") or "").strip()
    if not trigger:
        title = (signal.get("title") or "").strip()
        url = (signal.get("url") or "").strip()
        if title or url:
            trigger = "signal: %s%s" % (title, " (%s)" % url if url else "")
        else:
            trigger = "promotion candidate: %s" % promoted_from
    intended = (data.get("intended_effect") or "").strip()
    if not intended:
        intended = (
            "detect %s payloads that previously went undetected; "
            "verified zero false positive on BENIGN_CORPUS"
            % (category or "the target attack class")
        )
    return {
        "signal_title": signal.get("title", ""),
        "signal_url": signal.get("url", ""),
        "source": signal.get("source", ""),
        "attack_category": category,
        "promoted_from": promoted_from,
        "drafted_at": data.get("drafted_at", ""),
        "trigger": trigger,
        "intended_effect": intended,
    }


def simulate(store, data):
    """Apply a candidate's rules onto a COPY of `store`. Writes nothing."""
    import copy
    sim = copy.deepcopy(store)
    sim.setdefault("rules", {})
    sim.setdefault("provenance", {})
    for r in data["rules"]:
        pattern = r["pattern"].strip()
        sim["rules"][pattern] = [
            r["description"].strip(),
            r["severity"].strip().lower(),
        ]
        sim["provenance"][pattern] = _provenance_entry(
            data, os.path.basename(data.get("promoted_from_path", "")) or ""
        )
    return sim


def shadow(path, data, known_patterns=None):
    """Dry-run a promotion and return a verdict. Mutates nothing on disk.

    The preview runs the *same* three axes the live loop checks afterwards
    (schema / benign false-positive / attack catch), just against a simulated
    store — so CI can observe "would this rule have been worth promoting"
    before the transaction commits. ``radar_effect.evaluate()`` is called with
    ``save=False``; nothing is written to radar_rules.json, radar_effect.json,
    the ledger, or the proposal queue.
    """
    store = load_radar_rules()
    ok, problems = validate(path, data, known_patterns)
    sim = simulate(store, data)
    # save=False: effect measurement is read-only in shadow mode.
    eff = _import_radar_effect().evaluate(store=sim, save=False)
    erules = eff.get("rules", {}) or {}

    per_rule = []
    zero_catch = 0
    false_positives = 0
    for r in data["rules"]:
        pat = r["pattern"].strip()
        rec = erules.get(pat, {})
        catch = bool(rec.get("catch"))
        fp = bool(rec.get("false_positive"))
        zero_catch += 0 if catch else 1
        false_positives += 0 if not fp else 1
        per_rule.append({
            "pattern": pat,
            "description": r["description"].strip(),
            "severity": r["severity"].strip().lower(),
            "catch": catch,
            "catch_samples": int(rec.get("catch_samples", 0) or 0),
            "false_positive": fp,
            "fp_sample": rec.get("fp_sample"),
        })

    if problems:
        verdict = "refuse"
    elif false_positives:
        verdict = "refuse"
    elif zero_catch:
        verdict = "warn"
    else:
        verdict = "promote"

    counts = _live_counts()
    return {
        "mode": "shadow",
        "candidate": os.path.basename(path),
        "verdict": verdict,
        "problems": problems,
        "would_add": [r["pattern"].strip() for r in data["rules"]],
        "rules": per_rule,
        "zero_catch": zero_catch,
        "false_positives": false_positives,
        "radar_rules_before": len(store.get("rules", {})),
        "radar_rules_after": len(sim.get("rules", {})),
        "live_counts_before": {"mcp": counts[0], "skill": counts[1]} if counts else None,
        "effect_summary": eff.get("summary", {}),
        "wrote": [],  # empty by construction; asserted by the tests
    }


def shadow_all(known_patterns=None):
    """Shadow-evaluate every outstanding candidate. Returns (list, exit_code).

    Exit code 1 if ANY candidate is refused or would promote a dead rule, so
    this can sit in CI as a non-mutating gate.
    """
    out = []
    known = known_patterns if known_patterns is not None else live_patterns()
    for path, data in load_candidates():
        if data.get("status") == "rejected":
            continue
        out.append(shadow(path, data, known))
    bad = [v for v in out if v["verdict"] != "promote"]
    return out, (1 if bad else 0)


def render_shadow(verdicts):
    if not verdicts:
        return "shadow: no outstanding candidates in scanner/_proposed/"
    lines = []
    counts = {}
    for v in verdicts:
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    lines.append("shadow verdicts: %s  (would add %d rule(s); writes nothing)"
                 % (", ".join("%s=%d" % (k, counts[k])
                              for k in sorted(counts)),
                    sum(len(v["would_add"]) for v in verdicts)))
    for v in verdicts:
        lines.append("\n  [%-7s] %s" % (v["verdict"].upper(), v["candidate"]))
        if v["problems"]:
            for p in v["problems"]:
                lines.append("    - %s" % p)
        for r in v["rules"]:
            flags = []
            flags.append("catch=%d" % r["catch_samples"])
            if r["false_positive"]:
                flags.append("FALSE POSITIVE: %r" % (r["fp_sample"] or ""))
            lines.append("    [%-6s] %-22s %s" % (r["severity"], " ".join(flags),
                                                  r["pattern"]))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Promotion
# ---------------------------------------------------------------------------
def promote(path, data):
    store = load_radar_rules()
    store.setdefault("rules", {})
    store.setdefault("provenance", {})

    added = 0
    for r in data["rules"]:
        pattern = r["pattern"].strip()
        store["rules"][pattern] = [
            r["description"].strip(),
            r["severity"].strip().lower(),
        ]
        store["provenance"][pattern] = _provenance_entry(data, os.path.basename(path))
        added += 1

    # 先快照：一次误晋升必须可撤销（见 snapshot_current 上方注释）。
    before = snapshot_current()
    patterns = [r["pattern"].strip() for r in data["rules"]]

    os.makedirs(os.path.dirname(RADAR_RULES), exist_ok=True)
    with open(RADAR_RULES, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

    # Archive the candidate so the queue reflects only outstanding work.
    done_dir = os.path.join(PROPOSED_DIR, "promoted")
    os.makedirs(done_dir, exist_ok=True)
    os.replace(path, os.path.join(done_dir, os.path.basename(path)))

    ledger_append("promote",
                  from_file=os.path.basename(path),
                  patterns=patterns,
                  attack_category=data.get("attack_category", ""),
                  snapshot=os.path.basename(before) if before else None,
                  rule_count=len(store.get("rules", {})))
    prune_snapshots()

    sync_readme_counts()
    return added


# ---------------------------------------------------------------------------
# Keep published docs honest
# ---------------------------------------------------------------------------
def sync_readme_counts(readme=None):
    """Rewrite the rule totals in mcp-server/README.md to the live values.

    That README is the npmjs.com package page -- the first thing a user reads.
    `tests/test_mcp_contract.py` binds its numbers to the engine, so promoting
    a rule without updating it turns CI red. Doing it here means the docs can
    never drift behind a promotion.

    `readme` 可指定任意路径（默认真实 npm 页面）。测试必须传副本：直接跑真实
    README 会被 `tests/run_all.py` 的 hermetic guard 判为脏数据写入
    （`mcp-server/README.md` 在其受保护清单里）。
    """
    readme = readme or os.path.join(ROOT, "mcp-server", "README.md")
    if not os.path.exists(readme):
        return False
    try:
        sys.path.insert(0, ROOT)
        import importlib
        import scanner.rules as scanner_rules
        # scanner.rules 在 import 时把 RADAR_RULES 缓存进模块级变量；本进程里
        # 模块已在 radar_rules.json 写入前被 import（validate 阶段），缓存滞后。
        # 重新加载以读取刚写入的文件，否则 README 永远停在晋升前的旧计数。
        importlib.reload(scanner_rules)
        mcp_n = scanner_rules.get_rule_count("mcp")
        skill_n = scanner_rules.get_rule_count("skill")
    except Exception as e:
        print(f"  warning: could not read live rule counts ({e}); "
              f"update mcp-server/README.md by hand")
        return False

    with open(readme, encoding="utf-8") as f:
        text = f.read()

    new_text, n = re.subn(
        r"\*\*Total:\s*\d+\s*rules\*\*\s*\(MCP type\)\s*/\s*\*\*\d+\s*rules\*\*\s*\(Skill type\)",
        f"**Total: {mcp_n} rules** (MCP type) / **{skill_n} rules** (Skill type)",
        text,
    )
    if n and new_text != text:
        with open(readme, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"  synced {os.path.basename(readme)} ({readme}) "
              f"-> {mcp_n} MCP / {skill_n} Skill rules")
        return True
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def cmd_check():
    cands = load_candidates()
    if not cands:
        print("no candidates in scanner/_proposed/")
        return 0

    known = live_patterns()
    ready, blocked, drafts, rejected = [], [], [], []
    for path, data in cands:
        if data.get("status") == "rejected":
            rejected.append(path)
            continue
        ok, problems = validate(path, data, known)
        if ok:
            ready.append(path)
        elif len(problems) == 1 and "expected 'ready'" in problems[0]:
            drafts.append(path)
        else:
            blocked.append((path, problems))

    print(f"candidates: {len(cands)}  |  ready: {len(ready)}  "
          f"blocked: {len(blocked)}  awaiting-authoring: {len(drafts)}  "
          f"rejected: {len(rejected)}")

    if ready:
        print("\nREADY to promote:")
        for p in ready:
            print(f"  + {os.path.basename(p)}")
    if blocked:
        print("\nBLOCKED:")
        for p, probs in blocked:
            for msg in probs:
                print(f"  - {msg}")
    if drafts:
        print("\nAwaiting authoring (status != ready):")
        for p in drafts:
            print(f"  . {os.path.basename(p)}")
    if rejected:
        print("\nRejected (radar could not auto-derive a safe pattern; see _rejected_reason):")
        for p in rejected:
            print(f"  x {os.path.basename(p)}")

    return 1 if blocked else 0


def _evaluate_effect():
    """Re-measure catch/false-positive for the live radar rules after a change.

    Best-effort: effect measurement must never break promotion. A promoted rule
    that somehow false-positives is surfaced loudly (the promotion gate should
    have caught it, so this is a belt-and-braces alarm).
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import radar_effect  # noqa: WPS433
        store = radar_effect.evaluate()
        s = store.get("summary", {})
        print(f"  effect: promoted={s.get('promoted', 0)} "
              f"with_catch={s.get('with_catch', 0)} "
              f"false_positives={s.get('false_positives', 0)}")
        for pat, r in store.get("rules", {}).items():
            if r.get("false_positive"):
                print(f"  !! WARNING: promoted rule false-positives on benign "
                      f"input: {pat} -> {r.get('fp_sample')}")
    except Exception as e:
        print(f"  warning: effect evaluation skipped ({e})")


def _try_promote_one(path, data, known, strict):
    """Enforce-mode decision for a single candidate.

    Returns (promoted: bool, code: int, note: str).
      code 0  -- promoted
      code 2  -- refused by a hard gate (validation or benign false positive)
      code 3  -- skipped as a dead rule (zero catch) under --strict
    """
    verdict = shadow(path, data, known)
    if verdict["verdict"] == "refuse":
        print("REFUSED -- candidate failed validation:")
        for msg in verdict["problems"]:
            print("  - %s" % msg)
        return False, 2, verdict["candidate"]
    if verdict["verdict"] == "warn":
        msg = ("%d of %d rule(s) catch nothing on the attack corpus (dead weight)"
               % (verdict["zero_catch"], len(verdict["rules"])))
        if strict:
            print("SKIPPED --strict: %s -- %s" % (verdict["candidate"], msg))
            return False, 3, verdict["candidate"]
        print("WARNING: promoting anyway -- %s -- %s" % (verdict["candidate"], msg))
    n = promote(path, data)
    print("promoted %d rule(s) from %s -> data/radar_rules.json"
          % (n, os.path.basename(path)))
    return True, 0, verdict["candidate"]


def cmd_shadow():
    verdicts, code = shadow_all()
    print(render_shadow(verdicts))
    print("\nshadow mode: no files were written")
    return code


def cmd_promote(target, strict=False):
    path = target if os.path.isabs(target) else os.path.join(PROPOSED_DIR, target)
    if not os.path.exists(path):
        print("not found: %s" % path)
        return 1
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    ok, problems = validate(path, data)
    if not ok:
        print("REFUSED -- candidate failed validation:")
        for msg in problems:
            print("  - %s" % msg)
        return 1
    _ok, code, _note = _try_promote_one(path, data, live_patterns(), strict)
    _evaluate_effect()
    return 0 if code == 0 else code


def cmd_promote_all(strict=False):
    known = live_patterns()
    promoted = refused = skipped = 0
    for path, data in load_candidates():
        ok, _ = validate(path, data, known)
        if not ok:
            continue  # cmd_check already reports these; enforce never writes them
        did, code, _note = _try_promote_one(path, data, known, strict)
        if did:
            promoted += 1
            known |= {r["pattern"].strip() for r in data["rules"]}
        elif code == 2:
            refused += 1
        elif code == 3:
            skipped += 1
    print("promoted %d candidate(s) | refused %d | skipped as dead %d"
          % (promoted, refused, skipped))
    _evaluate_effect()
    return 1 if (refused or skipped) else 0


def cmd_list():
    store = load_radar_rules()
    rules = store.get("rules", {})
    if not rules:
        print("no radar-promoted rules yet")
        return 0
    print(f"{len(rules)} radar-promoted rule(s) in data/radar_rules.json:\n")
    for pattern, (desc, sev) in rules.items():
        prov = store.get("provenance", {}).get(pattern, {})
        print(f"  [{sev:8s}] {desc}")
        print(f"             pattern: {pattern}")
        if prov.get("signal_url"):
            print(f"             source:  {prov['signal_url']}")
    return 0


def cmd_list_snapshots():
    snaps = list_snapshots()
    if not snaps:
        print("no snapshots yet")
        return 0
    print("rollback points (newest first) in %s:\n" % os.path.relpath(SNAPSHOT_DIR, ROOT))
    for p, size, ts in snaps:
        marker = "  <-- newest" if p == snaps[0][0] else ""
        print("  %s  %7d B  %s%s" % (os.path.basename(p), size, ts, marker))
    pruned = glob.glob(os.path.join(SNAPSHOT_DIR, ".pruned", "radar_rules.*"))
    if pruned:
        print("\n  (%d pruned older snapshot(s) kept under %s/.pruned/)"
              % (len(pruned), os.path.relpath(SNAPSHOT_DIR, ROOT)))
    return 0


def cmd_rollback(target):
    code, msg = rollback(target)
    print(msg)
    return code


def cmd_ledger():
    entries = load_ledger()
    if not entries:
        print("promotion ledger is empty (%s)" % os.path.relpath(LEDGER, ROOT))
        return 0
    print("%d ledger event(s):\n" % len(entries))
    for e in reversed(entries):
        pats = e.get("patterns") or []
        print("  %s %-10s %s" % (e.get("ts", "?"), e.get("event", "?"),
                                 os.path.basename(e.get("restored_from") or
                                                  e.get("from_file") or "-")))
        if pats:
            print("           +%d rule(s): %s" % (len(pats),
                                                  ", ".join(pats[:3])))
    return 0


def main():
    ap = argparse.ArgumentParser(description="AIShield rule promotion gate")
    ap.add_argument("--strict", action="store_true",
                    help="Refuse zero-catch (dead) rules instead of promoting "
                         "them with a warning")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="Validate all candidates")
    g.add_argument("--shadow", action="store_true",
                   help="Dry run: full verdict for every candidate, writes nothing")
    g.add_argument("--promote", metavar="FILE", help="Promote one candidate")
    g.add_argument("--promote-all", action="store_true",
                   help="Promote every candidate that passes validation")
    g.add_argument("--list", action="store_true", help="List promoted radar rules")
    g.add_argument("--list-snapshots", action="store_true",
                   help="List rollback points")
    g.add_argument("--rollback", nargs="?", const="", default=None,
                   metavar="SNAP", help="Roll back to a snapshot (default: newest)")
    g.add_argument("--ledger", action="store_true", help="Show promote/rollback log")
    args = ap.parse_args()

    if args.check:
        return cmd_check()
    if args.shadow:
        return cmd_shadow()
    if args.promote:
        return cmd_promote(args.promote, strict=args.strict)
    if args.promote_all:
        return cmd_promote_all(strict=args.strict)
    if args.list:
        return cmd_list()
    if args.list_snapshots:
        return cmd_list_snapshots()
    if args.rollback is not None:
        return cmd_rollback(args.rollback or None)
    if args.ledger:
        return cmd_ledger()
    return 0


if __name__ == "__main__":
    sys.exit(main())
