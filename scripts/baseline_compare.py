#!/usr/bin/env python3
"""scripts/baseline_compare.py — 基线对比表 + bootstrap 95% CI（SCI 方案 P2 任务 2.3 / R3）

用途
----
在同一固定语料（benchmarks/corpus/external/）上，对 AIShield 自身与全部已跑基线
算 precision / recall / F1，并给 recall 与 FP 率做 bootstrap 95% CI（默认 1000 次
重采样）。输出 Markdown 对比表，列：工具 / 版本 / recall(95%CI) / FP(95%CI) / F1 /
规则数 / 是否上云。

口径纪律（与 scripts/benchmark.py Plane E 完全一致）
----------------------------------------------------
  * detection_bar = serious_only：只有 critical/high finding 才算检出。
  * 正样本上 detected=1 记为召回；负样本上 detected=1 记为误报。
  * precision = TP / (TP + FP)，recall = TP / (TP + FN)。
  * F1 = 2PR / (P + R)；P 或 R 为 0 时 F1 定义退化为 0（不取极限）。

诚实纪律（不伪造）
------------------
  · 基线未跑（status=not_run）-> 对比表里该行列 N/A 并注 "条件不对等"。
  · 基线失败（status=failed）  -> 列 FAILED 并注原因，不填数字。
  · 只有 status=ok 且样本数与当前语料一致，数字才进入比较。
    样本数不一致意味着"基线跑的是另一份语料"，那是对比表里最危险的假对比。
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

sys.path.insert(0, os.path.join(_ROOT, "benchmarks", "baselines"))

from benchmark import _bootstrap_ci, BOOTSTRAP_SEED  # noqa: E402

SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# 指标
# ---------------------------------------------------------------------------
def _prf(tp: int, fp: int, fn: int) -> Dict[str, float]:
    """由混淆矩阵算 precision/recall/F1。0/0 记为 None（无定义）。"""
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    if precision is None or recall is None or (precision + recall) == 0:
        f1 = None
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
        "f1": round(f1, 4) if f1 is not None else None,
        "tp": tp, "fp": fp, "fn": fn,
    }


def _confusion(payload: Dict[str, Any], corpus: Dict[str, Any]) -> Dict[str, int]:
    """从归一化结果重建混淆矩阵。样本数不匹配则抛错（不静默对齐）。"""
    pos_ids = {s["id"] for s in corpus.get("positives", ())}
    neg_ids = {s["id"] for s in corpus.get("negatives", ())}
    results = payload.get("results") or {}
    got_ids = set(results.keys())

    missing = (pos_ids | neg_ids) - got_ids
    extra = got_ids - (pos_ids | neg_ids)
    if missing or extra:
        raise ValueError(
            "基线结果与当前语料不匹配：缺 %d 条（如 %s），多 %d 条 —— "
            "该基线跑的是另一份语料，不参与对比"
            % (len(missing), next(iter(missing), "?"), len(extra)))

    tp = fp = fn = 0
    for sid in pos_ids:
        if results[sid].get("detected"):
            tp += 1
        else:
            fn += 1
    for sid in neg_ids:
        if results[sid].get("detected"):
            fp += 1
    return {"tp": tp, "fp": fp, "fn": fn,
            "n_pos": len(pos_ids), "n_neg": len(neg_ids)}


def _outcomes_from_confusion(cm: Dict[str, int]) -> tuple:
    """把混淆矩阵还原成 0/1 序列，喂给 bootstrap。

    recall 的分母是正样本：1=检出，0=漏检。
    fp 率的分母是负样本：1=误报，0=正确放行。
    """
    recall_seq = [1] * cm["tp"] + [0] * cm["fn"]
    fp_seq = [1] * cm["fp"] + [0] * (cm["n_neg"] - cm["fp"])
    return recall_seq, fp_seq


# ---------------------------------------------------------------------------
# 汇总一行
# ---------------------------------------------------------------------------
def _row(name: str, version: str, offline: bool, rule_count: Optional[int],
         payload: Optional[Dict[str, Any]], corpus: Dict[str, Any],
         resamples: int, seed: int = BOOTSTRAP_SEED) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "name": name, "version": version, "offline": offline,
        "rule_count": rule_count,
    }
    if payload is None or payload.get("status") == "not_run":
        row["status"] = "not_run"
        row["reason"] = (payload or {}).get("reason", "未提供结果")
        row["recall"] = row["fp_rate"] = row["f1"] = None
        row["recall_ci"] = row["fp_ci"] = None
        return row
    if payload.get("status") == "failed":
        row["status"] = "failed"
        row["reason"] = payload.get("reason", "?")
        row["recall"] = row["fp_rate"] = row["f1"] = None
        row["recall_ci"] = row["fp_ci"] = None
        return row

    try:
        cm = _confusion(payload, corpus)
    except ValueError as exc:
        row["status"] = "inconsistent_corpus"
        row["reason"] = str(exc)
        row["recall"] = row["fp_rate"] = row["f1"] = None
        row["recall_ci"] = row["fp_ci"] = None
        return row

    m = _prf(cm["tp"], cm["fp"], cm["fn"])
    row["status"] = "ok"
    row["n_positives"] = cm["n_pos"]
    row["n_negatives"] = cm["n_neg"]
    row["tp"] = cm["tp"]
    row["fp"] = cm["fp"]
    row["fn"] = cm["fn"]
    row["precision"] = m["precision"]
    row["recall"] = m["recall"]
    row["f1"] = m["f1"]
    row["fp_rate"] = round(cm["fp"] / cm["n_neg"], 4) if cm["n_neg"] else None
    row["recall_ci"] = None
    row["fp_ci"] = None
    if resamples > 0:
        recall_seq, fp_seq = _outcomes_from_confusion(cm)
        row["recall_ci"] = _bootstrap_ci(recall_seq, resamples=resamples,
                                         seed=seed)
        row["fp_ci"] = _bootstrap_ci(fp_seq, resamples=resamples, seed=seed)
    return row


# ---------------------------------------------------------------------------
# 渲染
# ---------------------------------------------------------------------------
def _fmt(v: Optional[float], ci: Optional[Dict[str, Any]], digits: int = 1) -> str:
    if v is None:
        return "N/A"
    pct = lambda x: ("%." + str(digits) + "f%%") % (x * 100)  # noqa: E731
    if ci and ci.get("low") is not None:
        return "%s [%s, %s]" % (pct(v), pct(ci["low"]), pct(ci["high"]))
    return pct(v)


def render_markdown(rows: List[Dict[str, Any]], corpus: Dict[str, Any],
                    resamples: int) -> str:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# 基线对比（同一固定外部语料）",
        "",
        "> 由 `python scripts/baseline_compare.py --markdown` 生成，请勿手工编辑。",
        "> 生成时间：%s ｜ 语料：`benchmarks/corpus/external/` ｜ bootstrap 重采样：%d 次"
        % (now, resamples),
        "",
        "口径：serious_only（仅 critical/high 计为检出）。"
        "基线在**运行期不联网**探测可用性；须上云的基线标 `非离线`，其对比条件不对等。",
        "",
        "## 对比表",
        "",
        "| 工具 | 版本 | recall(95%CI) | FP(95%CI) | F1 | 规则数 | 上云 |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        rc = "N/A" if r.get("rule_count") is None else str(r["rule_count"])
        cloud = "否" if r.get("offline") else "是"
        if r.get("status") in ("not_run", "failed", "inconsistent_corpus"):
            tag = {"not_run": "N/A（条件不对等）",
                   "failed": "FAILED",
                   "inconsistent_corpus": "N/A（语料不一致）"}[r["status"]]
        else:
            tag = _fmt(r.get("recall"), r.get("recall_ci"))
        fptag = ("N/A" if r.get("status") != "ok"
                 else _fmt(r.get("fp_rate"), r.get("fp_ci")))
        f1 = ("N/A" if r.get("status") != "ok" or r.get("f1") is None
              else "%d%%" % round(r["f1"] * 100))
        lines.append("| %s | %s | %s | %s | %s | %s | %s |"
                     % (r["name"], r.get("version", "?"), tag, fptag, f1, rc, cloud))

    lines += [
        "",
        "## 诚实标注（不伪造）",
        "",
        "以下工具在本环境**未能运行**，因此不给出分数。留白比编造高分更诚实 ——",
        "它明确标注了哪些对比条件不对等，供论文局限性章节直接引用。",
        "",
    ]
    for r in rows:
        if r.get("status") != "ok":
            lines.append("- **%s** %s — %s"
                         % (r["name"], r.get("version", ""), r.get("reason", "?")))
    ok = [r for r in rows if r.get("status") == "ok"]
    if not ok:
        lines.append("- （无可用基线结果）")

    lines += [
        "",
        "## 不变量",
        "",
        "- 所有工具吃同一份固定语料（`benchmarks/corpus/external/`），无人工挑选",
        "- 口径统一为 serious_only，与 `scripts/benchmark.py` Plane E 完全一致",
        "- bootstrap 种子固定为 %d，同一段代码重跑得到同一个 CI" % BOOTSTRAP_SEED,
        "- 样本数与当前语料不一致的基线结果被拒绝对齐（视为跑了另一份语料）",
        "",
        "复现：`python scripts/baseline_compare.py --markdown`",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def build(corpus: Dict[str, Any], resamples: int = 1000,
          include_self: bool = True,
          seed: int = BOOTSTRAP_SEED) -> Dict[str, Any]:
    import runner
    rows: List[Dict[str, Any]] = []
    if include_self:
        self_payload = runner.load_result("AIShield")
        rows.append(_row("AIShield", "self", True, 264, self_payload, corpus,
                         resamples, seed=seed))
    for b in runner.registry():
        rows.append(_row(b.name, b.version, b.offline, b.rule_count,
                         runner.load_result(b.name), corpus, resamples,
                         seed=seed))
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "corpus": "benchmarks/corpus/external/",
        "detection_bar": "serious_only",
        "bootstrap": {"resamples": resamples, "seed": seed,
                      "alpha": 0.05, "method": "percentile"},
        "rows": rows,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="baseline_compare",
        description="基线对比表 + bootstrap 95%% CI（SCI 方案 P2 任务 2.3）")
    ap.add_argument("--json", action="store_true", help="输出确定性 JSON")
    ap.add_argument("--markdown", action="store_true", help="输出 Markdown 对比表")
    ap.add_argument("--bootstrap", type=int, default=1000,
                    help="bootstrap 重采样次数（默认 1000；0 则不出 CI）")
    ap.add_argument("--seed", type=int, default=BOOTSTRAP_SEED,
                    help="bootstrap 随机种子（默认 %d；换种子可做敏感性分析）"
                         % BOOTSTRAP_SEED)
    ap.add_argument("--no-self", action="store_true",
                    help="不把 AIShield 自身纳入对比表")
    ap.add_argument("--out", default=None, help="写入文件（默认 stdout）")
    ap.add_argument("--fail-under-recall", type=float, default=None,
                    help="AIShield recall 低于此值则退出码 1（CI 门禁）")
    args = ap.parse_args(argv)

    import rule_corpus
    corpus = rule_corpus.load_external_corpus()
    if not corpus.get("positives"):
        print("外部语料为空，无法对比：请先跑 scripts/corpus_collect.py")
        return 2

    result = build(corpus, resamples=args.bootstrap,
                   include_self=not args.no_self, seed=args.seed)

    if args.markdown:
        text = render_markdown(result["rows"], corpus, args.bootstrap)
    elif args.json:
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        lines = ["基线对比（corpus=external, bootstrap=%d）" % args.bootstrap, "-" * 60]
        for r in result["rows"]:
            if r.get("status") == "ok":
                lines.append("%-26s recall=%s  fp=%s  f1=%s"
                             % (r["name"], _fmt(r.get("recall"), r.get("recall_ci")),
                                _fmt(r.get("fp_rate"), r.get("fp_ci")),
                                "N/A" if r.get("f1") is None else "%d%%" % round(r["f1"] * 100)))
            else:
                lines.append("%-26s %s — %s"
                             % (r["name"], r.get("status"), r.get("reason", "")))
        text = "\n".join(lines)

    if args.out:
        parent = os.path.dirname(os.path.abspath(args.out))
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("wrote %s" % args.out)
    else:
        print(text)

    rc = 0
    self_row = next((r for r in result["rows"] if r["name"] == "AIShield"), None)
    if args.fail_under_recall is not None:
        if self_row is None or self_row.get("recall") is None:
            print("FAIL: AIShield 无可比 recall（未跑或语料不一致）")
            rc = 1
        elif self_row["recall"] < args.fail_under_recall:
            print("FAIL: AIShield recall %.4f < %.4f"
                  % (self_row["recall"], args.fail_under_recall))
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
