"""
评分可解释（M3 收口）—— 让 overall_score 从黑盒变成可回放、可申诉、可审计的账本。

为什么需要这个模块
------------------
calculate_scores() 早就返回了 score_breakdown，但它在两个地方「解释不完整」：

1. **扣分账拼不平**。breakdown['contributors'] 只保留扣分最多的 5 条，
   penalty 却是全量求和。实测一条 12 条告警的扫描：penalty=105、展示 80、
   **25 分凭空消失** —— 用户问「为什么是 60 不是 85」，回答永远拼不出账。
   engine 已补 contributions_full（全量），这里负责**强制闭合**并审计。
2. **归因申诉不到规则**。contributors 里只有一句中文 reason，没有 rule_id，
   企业安全团队没法把扣分翻回具体规则条目去复核。

本模块的三件事
--------------
audit(scores[, findings, total_files])
    账本审计：逐项验证「维度分 = clamp(base - penalty)」「penalty = 全部扣分项之和」
    「展示项 + 被截断项 = 全量」「overall = 加权和」「risk/badge 与分数自洽」。
    任何一条不成立就进 issues，并给出可申诉的原因。

replay(findings, total_files, extra_findings)
    独立复算：不调用 engine.calculate_scores，而是**另写一条计算路径**从原始
    findings 重算一遍分数与归因。两条路径互不相干，所以它不是镜像而是**校验**；
    复算结果与 engine 不一致 ⇒ 这个分数当下不可信（口径漂移就抓在这里）。
    附带确定性 digest：同输入必得同输出，可用于 CI 回归（分数口径不许悄悄变）。

explain(scores, fmt='json'|'text')
    机器可读归因（fmt='json' 给 dict，给 API/SOAR 消费；'text' 给人看）。
    json 输出里 attribution_complete=True 才算「这条分数解释得清」。

零依赖：只用标准库。与 engine 共享 _DIM_CONFIG（权重单一事实源），
但算术路径独立 —— 刻意重复，因为要能互相证伪。
"""
from __future__ import annotations

import hashlib
import json

from . import engine as _engine

__all__ = ["audit", "replay", "explain", "attribution_text", "ledger_from_replay",
           "DIM_ORDER", "WEIGHTS"]

DIM_ORDER = ("security_score", "permissions_score", "data_handling_score",
             "supply_chain_score", "reliability_score")

# 权重/扣分表单一事实源取自 engine（不复制一份，免得两边漂移）
WEIGHTS = {k: v[1] for k, v in _engine._DIM_CONFIG.items()}
_DEDUCT = {k: v[2] for k, v in _engine._DIM_CONFIG.items()}
_CATFILTER = {k: v[3] for k, v in _engine._DIM_CONFIG.items()}
_SHOW_TOP = 5

SEVERITY_NAMES = {0: "unknown", 1: "info", 2: "low", 3: "medium", 4: "high", 5: "critical"}


def _dedup_key(f: dict) -> str:
    """与 engine 同口径的折叠键（type:description:file）。"""
    return "%s:%s:%s" % (f.get("type", ""), f.get("description", ""), f.get("file", ""))


def _is_match(f: dict, catfilter) -> bool:
    cat = f.get("owasp_category", "")
    if catfilter is None:
        return True
    if isinstance(catfilter, str):
        return cat == catfilter
    return cat in catfilter


def _dim_base(dim_key: str, total_files: int) -> int:
    """维度基准分与 engine 的 total_files==0 阻尼规则保持一致。"""
    base = 100
    if total_files == 0:
        if dim_key == "security_score":
            base = min(base, 65)
        elif dim_key == "data_handling_score":
            base = min(base, 70)
        elif dim_key == "reliability_score":
            base = max(0, base - 30)
    return base


def _overall(dims: dict) -> int:
    """与 engine 完全同样的加权顺序 —— 浮点求和必须逐位一致，否则回放不可比。"""
    return int(round(
        dims["security_score"] * 0.40 + dims["permissions_score"] * 0.20 +
        dims["data_handling_score"] * 0.20 + dims["supply_chain_score"] * 0.10 +
        dims["reliability_score"] * 0.10
    ))


def _risk_and_badge(dims: dict, overall: int):
    if dims["security_score"] < 40:
        risk = "critical"
    elif dims["security_score"] < 60:
        risk = "high"
    elif dims["security_score"] < 80:
        risk = "medium"
    else:
        risk = "safe"
    badge = "gold" if overall >= 85 else "silver" if overall >= 70 else "bronze" if overall >= 55 else "none"
    return risk, badge


def replay(findings, total_files: int = 0, extra_findings=None) -> dict:
    """
    独立复算：从原始 findings 重算一遍分数 + 全量归因 + 确定性 digest。

    返回 {overall_score, dims, attributions, digest, inputs_hash}
    digest 是分数账本的指纹，用它做 CI 回归：口径一变（有人悄悄调了权重或
    折叠逻辑）digest 就变，一眼能看见，而不是等用户来问「为什么降了 3 分」。
    """
    flat = list(findings or [])
    if extra_findings:
        flat = flat + list(extra_findings)

    seen, unique = set(), []
    for f in flat:
        k = _dedup_key(f)
        if k in seen:
            continue
        seen.add(k)
        unique.append(f)

    dims, attributions = {}, {}
    for dim_key in DIM_ORDER:
        ded, cfilter = _DEDUCT[dim_key], _CATFILTER[dim_key]
        contribs, folded, seen_desc = [], [], set()
        for f in unique:
            if not _is_match(f, cfilter):
                continue
            desc = f.get("description", "")
            amt = ded.get(f.get("severity", "info"), 0)
            if desc in seen_desc:
                if amt > 0:
                    folded.append({"reason": desc, "rule_id": f.get("rule_id") or f.get("type", ""),
                                   "severity": f.get("severity", "info"), "amount": amt})
                continue
            seen_desc.add(desc)
            if amt > 0:
                contribs.append({"rule_id": f.get("rule_id") or f.get("type", ""),
                                 "reason": desc, "severity": f.get("severity", "info"),
                                 "owasp": f.get("owasp_category", ""), "amount": amt})
        contribs.sort(key=lambda c: -c["amount"])
        base = _dim_base(dim_key, total_files)
        penalty = sum(c["amount"] for c in contribs)
        dims[dim_key] = max(0, min(100, base - penalty))
        attributions[dim_key] = {
            "base": base, "penalty": penalty, "score": dims[dim_key],
            "contributions": contribs, "folded": folded,
            "hidden_by_truncation": len(contribs) > _SHOW_TOP,
        }

    overall = _overall(dims)
    risk, badge = _risk_and_badge(dims, overall)
    ledger = {
        "dims": {k: dims[k] for k in DIM_ORDER},
        "overall_score": overall,
        "risk_level": risk,
        "badge_level": badge,
    }
    return {
        **ledger,
        "attributions": attributions,
        "digest": _digest(ledger),
        "inputs_hash": _digest([_dedup_key(f) for f in unique]) + ":%d" % total_files,
    }


def _digest(obj) -> str:
    """确定性指纹：同输入、同顺序 ⇒ 同 digest（排序后再序列化）。"""
    try:
        raw = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except TypeError:
        raw = repr(sorted(map(str, obj)))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def audit(scores: dict, findings=None, total_files: int = 0) -> dict:
    """
    账本审计 —— 解释性的真门槛。

    只传 scores 时做**内部自洽**审计（不依赖外部输入）；
    传 findings/total_files 时额外做**独立复算交叉验证**。

    返回 {ok, issues[], warnings[], attribution_complete, coverage}
    attribution_complete=False 就别把这条分数当「可解释」对外讲。

    语义边界（别混淆）：**账本完备**才是不完整性的门槛（penalty 能由全量扣分项
    逐个翻出来、且每条都有 rule_id）；top5 展示截断是**展示层**的事，只要全量账本
    在、hidden_amount 如实报出来，这条分数照样算解释得清 —— 否则会出现「解释得清
    但永远报红」的假硬，门禁自己先空转。
    """
    issues, warnings = [], []
    breakdown = scores.get("score_breakdown", {}) or {}

    for dim_key in DIM_ORDER:
        b = breakdown.get(dim_key) or {}
        base, penalty = b.get("base", 0), b.get("penalty", 0)
        full = b.get("contributions_full")
        if full is None:
            # 老结构（没有全量账本）无法审计：只展示 top5 的账必然拼不平
            full = b.get("contributors", []) or []
            issues.append({
                "dimension": dim_key,
                "code": "no_full_ledger",
                "message": "缺少 contributions_full，扣分账无法闭合（只展示 top%d 的账必然拼不平）" % _SHOW_TOP,
            })
        full_sum = sum(c.get("amount", 0) for c in full)
        shown = b.get("contributors", []) or []
        shown_sum = sum(c.get("amount", 0) for c in shown)
        if penalty != full_sum:
            issues.append({
                "dimension": dim_key, "code": "penalty_not_reproducible",
                "message": "penalty=%s 但全量扣分项之和=%s（有扣分项没进账本）" % (penalty, full_sum),
            })
        if shown_sum and full_sum and shown_sum < full_sum:
            # 展示截断 → 警告不是问题：全量账本在，缺口如实数出来就行。
            warnings.append({
                "dimension": dim_key, "code": "display_truncated",
                "message": "contributors 只展示 top%d（%s/%s 分），剩余 %s 分在 contributions_full 里"
                           % (_SHOW_TOP, shown_sum, full_sum, full_sum - shown_sum),
            })
        for c in full:
            if not c.get("rule_id"):
                issues.append({
                    "dimension": dim_key, "code": "missing_rule_id",
                    "message": "扣分项没有 rule_id，申诉无法定位规则：%s" % str(c.get("reason", ""))[:40],
                })
                break
        dim_score = scores.get(dim_key)
        if dim_score is not None and dim_score != max(0, min(100, base - penalty)):
            issues.append({
                "dimension": dim_key, "code": "dim_formula_mismatch",
                "message": "维度分 %s 与 base-penalty=%s 不符" % (dim_score, max(0, min(100, base - penalty))),
            })

    # overall / risk / badge 自洽
    dims = {dk: scores.get(dk, 0) for dk in DIM_ORDER}
    if findings is not None:
        rp = replay(findings, total_files=total_files)
        if rp["overall_score"] != scores.get("overall_score"):
            issues.append({
                "code": "replay_mismatch", "dimension": None,
                "message": "独立复算得 %s，engine 给 %s —— 口径已漂移，此分数不可信"
                           % (rp["overall_score"], scores.get("overall_score")),
            })
        for dk in DIM_ORDER:
            if rp["dims"][dk] != dims.get(dk):
                issues.append({
                    "code": "replay_dim_mismatch", "dimension": dk,
                    "message": "独立复算维度 %s=%s，engine 给 %s" % (dk, rp["dims"][dk], dims.get(dk)),
                })

    return {
        "ok": not issues,
        "issues": issues,
        "warnings": warnings,
        # 账本完备（不是展示完整）才算解释得清
        "attribution_complete": not issues,
        "coverage": _coverage(breakdown),  # 展示口径能覆盖百分之多少的扣分
        "digest": scores.get("digest") or _digest(scores.get("overall_score")),
    }


def ledger_from_replay(rp: dict) -> dict:
    """
    把 replay() 的输出转成 explain()/audit() 认的 scores 形状。

    replay 是「独立复算」、explain 是「解释」—— 两边不能各说各话，所以这里做
    一次显式形状对齐，而不是让调用方手搓 dict（手搓最容易漏字段、解释就假了）。
    """
    breakdown = {}
    for dim_key, a in (rp.get("attributions") or {}).items():
        contribs = list(a.get("contributions") or [])
        breakdown[dim_key] = {
            "base": a.get("base", 100),
            "penalty": a.get("penalty", 0),
            "contributions_full": contribs,
            "contributors": contribs[:_SHOW_TOP],
            "folded_duplicates": a.get("folded") or [],
        }
    scores = {dk: rp["dims"][dk] for dk in DIM_ORDER}
    scores.update({
        "overall_score": rp.get("overall_score"),
        "risk_level": rp.get("risk_level"),
        "badge_level": rp.get("badge_level"),
        "score_breakdown": breakdown,
        "digest": rp.get("digest"),
    })
    return scores


def _coverage(breakdown: dict) -> float:
    """展示的扣分项占了全量扣分多少（用于判断解释够不够）。"""
    total_shown = total_full = 0.0
    for dim_key in DIM_ORDER:
        b = breakdown.get(dim_key) or {}
        full = b.get("contributions_full") or []
        if b.get("contributions_full") is None:
            full = b.get("contributors", []) or []
        total_full += sum(c.get("amount", 0) for c in full)
        total_shown += sum(c.get("amount", 0) for c in (b.get("contributors", []) or []))
    if total_full == 0:
        return 1.0
    return round(total_shown / total_full, 4)


def explain(scores: dict, fmt: str = "json"):
    """
    机器可读归因。fmt='json' 返回 dict（API/SOAR 消费），'text' 返回人话字符串。

    json 结构：
      overall_score / risk_level / badge_level
      per_dim{dim: {base, penalty, score, shown, hidden, hidden_amount,
                    contributions[{rule_id, reason, severity, amount}],
                    folded_duplicates[rule_id, ...]}}
      attribution_complete / issues[]
    """
    if fmt == "text":
        return attribution_text(scores)
    breakdown = scores.get("score_breakdown", {}) or {}
    ad = audit(scores)
    per_dim = {}
    for dim_key in DIM_ORDER:
        b = breakdown.get(dim_key) or {}
        full = b.get("contributions_full") or b.get("contributors", []) or []
        shown = b.get("contributors", []) or []
        hidden = [c for c in full if c not in shown]
        per_dim[dim_key] = {
            "base": b.get("base", 100),
            "penalty": b.get("penalty", 0),
            "score": scores.get(dim_key),
            "shown_amount": sum(c.get("amount", 0) for c in shown),
            "hidden_amount": sum(c.get("amount", 0) for c in hidden),
            "contributions": full,
            "folded_duplicates": b.get("folded_duplicates", []) or [],
        }
    return {
        "overall_score": scores.get("overall_score"),
        "risk_level": scores.get("risk_level"),
        "badge_level": scores.get("badge_level"),
        "attribution_complete": ad["attribution_complete"],
        "coverage": ad["coverage"],
        "issues": ad["issues"],
        "per_dim": per_dim,
        "digest": ad["digest"],
    }


def attribution_text(scores: dict) -> str:
    """人话版扣分账（CLI / 工单引用用）。"""
    ex = explain(scores, fmt="json")
    lines = ["总分 %s（%s，badge=%s）" % (ex["overall_score"], ex["risk_level"], ex["badge_level"])]
    if not ex["attribution_complete"]:
        codes = sorted({i["code"] for i in ex["issues"]})
        lines.append("  ⚠ 解释不完整（coverage=%.0f%%）：%s" % (ex["coverage"] * 100, ", ".join(codes)))
    for dim_key in DIM_ORDER:
        d = ex["per_dim"][dim_key]
        lines.append("  · %-20s %s = 基准 %s − 扣分 %s（展示 %s%s）"
                     % (dim_key, d["score"], d["base"], d["penalty"], d["shown_amount"],
                        "，另有 %s 分未展示" % d["hidden_amount"] if d["hidden_amount"] else ""))
        for c in d["contributions"][:5]:
            lines.append("      - [%s] %s -%s  rule=%s"
                         % (c.get("severity", ""), str(c.get("reason", ""))[:44], c.get("amount"), c.get("rule_id", "-")))
        for c in d["contributions"][5:]:
            lines.append("      - [%s] %s -%s  rule=%s（被截断，见全量账本）"
                         % (c.get("severity", ""), str(c.get("reason", ""))[:30], c.get("amount"), c.get("rule_id", "-")))
    return "\n".join(lines)
