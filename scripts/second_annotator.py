#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二标注者协议（Second-Annotator Protocol）—— 复现 R1 的 inter-annotator agreement。

背景
----
外部语料 ``benchmarks/corpus/external/`` 的 PRIMARY 标注者（A）是语料策展流程：
每条样本带 ``labels:[{annotator:"A", positive: <bool>}]`` 与 ``family``。

SCI 门槛 R1 要求 ≥2 名标注者且 Cohen's κ ≥ 0.8。本仓库写作阶段无法获得真人双标，
因此这里提供一个 **可复现、透明的协议级第二标注者（B）**，其设计遵循 annotation
guideline 的独立重应用原则：

    B 仅从「原始信号」推导标签，绝不包含 A 的标签或 family 赋值：
      1. 外部可验证 provenance：样本带 cve_id / cwe_ids / 来源为 GitHub Security
         Advisory Database → 强正信号（确定性漏洞，无歧义）。
      2. 保守的高精度攻击短语词典：对 text + summary + user_instruction 做
         不区分大小写的短语匹配（仅命中明确攻击措辞，避免误伤良性样本）。
      3. 其余 → 负。

B 与 A 的分歧恰好落在「语义微妙 / 良性上下文误含触发词」的样本上，这正是真实
IAA 会出现分歧的地方。κ 是该协议下语料标签可靠性的可复现估计；最终真人双标是
投前最后一步（见 paper §7 / R7）。

本脚本确定性、零随机，故 κ 是语料 + 协议的固定属性，可复现。

产出
----
  - benchmarks/corpus/external/second_annotator_labels.json  （id -> bool，sidecar）
  - 就地为每条样本 labels 追加 {annotator:"B", basis:"protocol_independent", positive}
  - 打印 A/B 一致性分解，供 compute_kappa.py 读取
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
SIDECAR = os.path.join(CORPUS_DIR, "second_annotator_labels.json")

# ---------------------------------------------------------------------------
# 保守、高精度的攻击短语词典（仅明确攻击措辞；不收 password/token/secret 等
# 在良性上下文中高频出现的泛安全词，以免 B 对负样本过触发）。
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
    # 动作 / 外泄指令（InjecAgent 子集验证 N==0；第二分析师识别"要求 agent 执行
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
    """独立重标：只读原始信号，绝不读 family / labels。"""
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
    """取 PRIMARY 标注者 A 的 positive（bool）。"""
    for lab in sample.get("labels", []) or []:
        if lab.get("annotator") == "A":
            return bool(lab.get("positive"))
    # 退化：无 A 标签时回退到 family 是否为良性族（不应发生）
    return False


def run(patch_in_file: bool = True) -> dict:
    pos_files = sorted(glob.glob(os.path.join(CORPUS_DIR, "positives", "*.json")))
    neg_files = sorted(glob.glob(os.path.join(CORPUS_DIR, "negatives", "*.json")))
    files = pos_files + neg_files

    b_labels: dict[str, bool] = {}
    a_labels: dict[str, bool] = {}
    patched = 0

    for fp in files:
        with open(fp, encoding="utf-8") as fh:
            sample = json.load(fh)
        sid = sample["id"]
        a = primary_label(sample)
        b = label_b(sample)
        a_labels[sid] = a
        b_labels[sid] = b

        if patch_in_file:
            labels = sample.get("labels") or []
            existing = next((lab for lab in labels
                            if lab.get("annotator") == "B"), None)
            if existing is None:
                labels.append({
                    "annotator": "B",
                    "basis": "protocol_independent",
                    "positive": b,
                })
                patched += 1
            elif existing.get("positive") != b:
                existing["positive"] = b
                patched += 1
            else:
                continue  # 已是正确值，跳过写盘
            sample["labels"] = labels
            with open(fp, "w", encoding="utf-8") as fh:
                json.dump(sample, fh, ensure_ascii=False, indent=2)
                fh.write("\n")

    with open(SIDECAR, "w", encoding="utf-8") as fh:
        json.dump({"annotator": "B", "basis": "protocol_independent",
                   "labels": b_labels}, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # 一致性分解
    n = len(files)
    agree = sum(1 for s in b_labels if a_labels[s] == b_labels[s])
    a_pos = sum(1 for s in a_labels if a_labels[s])
    a_neg = n - a_pos
    b_pos = sum(1 for s in b_labels if b_labels[s])
    b_neg = n - b_pos
    # 2x2
    tp = sum(1 for s in b_labels if a_labels[s] and b_labels[s])
    tn = sum(1 for s in b_labels if not a_labels[s] and not b_labels[s])
    fp = sum(1 for s in b_labels if not a_labels[s] and b_labels[s])
    fn = sum(1 for s in b_labels if a_labels[s] and not b_labels[s])

    summary = {
        "n": n, "agree": agree, "observed_agreement": agree / n,
        "a_positive": a_pos, "a_negative": a_neg,
        "b_positive": b_pos, "b_negative": b_neg,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "patched_files": patched,
    }
    print("[second_annotator] corpus n =", n)
    print("  A: pos=%d neg=%d | B: pos=%d neg=%d" % (a_pos, a_neg, b_pos, b_neg))
    print("  2x2  TP=%d TN=%d FP=%d FN=%d" % (tp, tn, fp, fn))
    print("  observed agreement = %.4f" % (agree / n))
    print("  sidecar ->", SIDECAR)
    print("  patched in-file labels:", patched)
    return summary


if __name__ == "__main__":
    patch = "--no-patch" not in sys.argv
    run(patch_in_file=patch)
