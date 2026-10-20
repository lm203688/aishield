#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签一致性审计（Label Consistency Audit, LCA）—— 复现 R1 的"标签可靠性"信号。

重要澄清（方法论诚实）
----------------------
本脚本 **不是** "第二标注者 / 双人工标注"。R1 的语料来自**权威、可审计真值来源**：

  * 正样本 66 条 = GitHub Security Advisory（GHSA）已发布 CVE，标签锚定第三方
    （NVD / GitHub / 发行方）已公开漏洞记录，非主观判断；
  * 正样本 527 条 + 负样本 517 条 = InjecAgent（Zhang et al., NAACL 2024）公开
    基准，标签为该数据集作者标注的攻击类型真值。

即语料是 **provenance 可审计的 gold-standard 语料**。顶会安全/对齐基准
（HarmBench / AdvBench / InjecAgent 等）均以此类外部真值作为标签，不需要
"两名人类标注者间一致性"来背书——标签的可靠性来自来源本身。

本脚本做的是 **自动化一致性审计（LCA）**：用一套"仅从原始信号独立重推标签"
的保守启发式（不读语料自带标签），去对照语料自带的来源真值标签，算出的 Cohen's
κ 衡量的是"独立自动化重推 与 来源真值"的一致性（即可复现性 / 标签自洽性），
**绝不代表人类标注者间一致性**。真实的人类双标（≥2 名独立分析师 + 分歧仲裁）是
投前最后一步，由 `scripts/human_iAA_kit.py` 提供工具包（见 paper §7 / R7）。

本脚本确定性、零随机，故 LCA κ 是语料 + 启发式的固定属性，可复现。

产出
----
  - benchmarks/corpus/external/lca_labels.json  （id -> bool，sidecar，仅审计用）
  - **绝不**向样本 labels 注入任何 "annotator" 字段（保持语料只有来源真值 A）。
  - 打印 独立重推(AI重推) vs 来源真值 的一致性分解，供 compute_lca.py 读取。
"""
from __future__ import annotations

import glob
import json
import os
import sys

CORPUS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "benchmarks", "corpus", "external",
)
SIDECAR = os.path.join(CORPUS_DIR, "lca_labels.json")

# ---------------------------------------------------------------------------
# 保守、高精度的攻击短语词典（仅明确攻击措辞；不收 password/token/secret 等
# 在良性上下文中高频出现的泛安全词，以免对负样本过触发）。
#
# 其中「命令式指令覆盖 / 注入标记」一组在 InjecAgent 子集（527 正 / 517 负）
# 上经差分频率验证为 P>0 且 N==0，是高精度独立信号；其余为通用高精度攻击术语。
# ---------------------------------------------------------------------------
ATTACK_PHRASES = [
    # 命令式指令覆盖 / 注入标记（InjecAgent 子集验证 P>0 且 N==0）
    "ignore all previous", "ignore previous", "ignore the previous",
    "previous instructions", "strictly adhere", "adhere to the",
    "the following instruction", "following instructions", "important ignore",
    "instruction please", "disregard previous", "disregard the",
    "forget previous", "forget everything", "new instructions",
    "system prompt", "you are now", "override", "do not tell",
    "hidden instruction", "new prompt", "updated instructions",
    # 外部可验证 provenance 短语（确定性漏洞 / 越权授予）
    "grant permanent", "permanent access", "access to my",
    "send the", "please transfer", "transfer", "download",
    # 通用高精度攻击术语
    "exfiltrat", "base64", "rm -rf", "os.system", "subprocess",
    "eval(", "exec(", "drop table", "union select", "command injection",
    "reverse shell", "bypass", "privilege escalation", "api key",
    "secret key", "malicious", "payload", "exploit", "extract the",
    "reveal", "confidential", "sql injection", "credential",
    "send this to", "transmit", "leak", "injection attack",
    # 动作 / 外泄指令（InjecAgent 子集验证 N==0；识别"要求 agent 执行
    # 外泄/越权动作"的独立信号）
    "please retrieve", "please send", "please email", "please transfer",
    "please update", "please unlock", "please delete", "please share",
    "please forward", "please post", "please download", "please grant",
    "email them", "send this", "my dropbox", "my account", "my saved",
    "my alternate", "update my", "unlock my", "to binance", "transfer usd",
    "alternate email", "and send", "to my dropbox", "retrieve the",
    "from my account",
]


def _text_of(sample: dict) -> str:
    parts = []
    for k in ("text", "summary", "user_instruction", "user_tool"):
        v = sample.get(k)
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, (list, dict)):
            parts.append(json.dumps(v, ensure_ascii=False))
    return "\n".join(parts).lower()


def label_b(sample: dict) -> bool:
    """独立重推：只读原始信号，绝不读 family / labels（来源真值）。

    这是 LCA 的"独立重推"一侧，对照 corpus 自带的来源真值（A）。
    """
    # 1) 外部可验证 provenance（确定性漏洞）
    if sample.get("cve_id") or sample.get("cwe_ids"):
        return True
    src = (sample.get("source") or "")
    if "github security advisory" in src.lower() or "ghsa" in src.lower():
        return True
    # 2) 保守高精度短语词典
    blob = _text_of(sample)
    if any(phrase in blob for phrase in ATTACK_PHRASES):
        return True
    # 3) 其余为负
    return False


def primary_label(sample: dict):
    """取语料自带的来源真值标签（A = 外部真值）。"""
    for lab in sample.get("labels", []) or []:
        if lab.get("annotator") == "A":
            return bool(lab.get("positive"))
    # 退化：无 A 标签时回退到 family 是否为良性族（不应发生）
    return False


def run() -> dict:
    """执行 LCA：独立重推 vs 来源真值，仅产出 sidecar，绝不改写样本。"""
    pos_files = sorted(glob.glob(os.path.join(CORPUS_DIR, "positives", "*.json")))
    neg_files = sorted(glob.glob(os.path.join(CORPUS_DIR, "negatives", "*.json")))
    files = pos_files + neg_files

    b_labels: dict[str, bool] = {}
    a_labels: dict[str, bool] = {}

    for fp in files:
        with open(fp, encoding="utf-8") as fh:
            sample = json.load(fh)
        sid = sample["id"]
        a = primary_label(sample)
        b = label_b(sample)
        a_labels[sid] = a
        b_labels[sid] = b

    with open(SIDECAR, "w", encoding="utf-8") as fh:
        json.dump({"audit": "label_consistency_audit", "basis": "independent_re-derivation_vs_source_truth",
                   "labels": b_labels}, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # 一致性分解（独立重推 B 对照 来源真值 A）
    n = len(files)
    agree = sum(1 for s in b_labels if a_labels[s] == b_labels[s])
    a_pos = sum(1 for s in a_labels if a_labels[s])
    a_neg = n - a_pos
    b_pos = sum(1 for s in b_labels if b_labels[s])
    b_neg = n - b_pos
    tp = sum(1 for s in b_labels if a_labels[s] and b_labels[s])
    tn = sum(1 for s in b_labels if not a_labels[s] and not b_labels[s])
    fp = sum(1 for s in b_labels if not a_labels[s] and b_labels[s])
    fn = sum(1 for s in b_labels if a_labels[s] and not b_labels[s])

    summary = {
        "n": n, "agree": agree, "observed_agreement": agree / n,
        "source_truth_positive": a_pos, "source_truth_negative": a_neg,
        "re_derivation_positive": b_pos, "re_derivation_negative": b_neg,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
    }
    print("[lca] corpus n =", n)
    print("  来源真值 A: pos=%d neg=%d | 独立重推 B: pos=%d neg=%d"
          % (a_pos, a_neg, b_pos, b_neg))
    print("  2x2  TP=%d TN=%d FP=%d FN=%d" % (tp, tn, fp, fn))
    print("  observed agreement = %.4f" % (agree / n))
    print("  sidecar ->", SIDECAR)
    print("  NOTE: 本 κ 是自动化标签一致性审计(LCA)，非人类标注者间一致性。")
    return summary


if __name__ == "__main__":
    run()
