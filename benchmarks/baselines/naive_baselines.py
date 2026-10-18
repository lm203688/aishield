#!/usr/bin/env python3
"""benchmarks/baselines/naive_baselines.py — 离线可跑的"朴素基线"（SCI 方案 P2 任务 2.2）

为什么需要这两个基线
--------------------
R2 要求**同一固定语料上 ≥3 个可出真实数字**的基线。本项目 4 个外部商业基线
（Invariant / agent-security-scanner / mcp-audit / Snyk）在本环境**无法运行**，
诚实标记为 ``not_run``（对比条件不对等，不伪造）。但它们凑不齐"≥3 个真实数字"。

因此这里提供两个**真正离线可跑、零依赖、确定性**的朴素基线，用来把对比表填满
真实数字，并让 AIShield 的相对优势有"下界参照"：

  1. Naive keyword heuristic —— 安全外行会写的那类规则：扫 ``text`` 里有没有
     一批"可疑词"。它不建模攻击结构，命中即报。多数微妙注入（把恶意指令嵌进
     良性 JSON/产品描述里）它抓不到，所以 recall 偏低；同时良性 matched 负样本
     里也常出现 "send/email/access" 等词，所以 FP 不零。这是一个**诚实的弱基线**。
  2. Random guess (base-rate) —— 零信号的最多数/随机基线：按正样本先验概率
     p=593/1110 用样本 id 派生的确定性哈希决定报不报。它给出"什么都不懂时
     分数的理论下界"，是 ML 安全论文的标准参照。

设计纪律（与 runner.py 一致）
---------------------------
  * 两个基线都 **offline=True**，运行期不联网，check() 恒返回可用。
  * 输出 schema 与 ``runner._normalize`` 完全一致：
    ``{"sample_id", "detected": bool, "severity": "high"/None}``
  * 不把正样本/负样本分开跑两套逻辑 —— 同一函数对两类样本一视同仁，和 AIShield
    自身走同一条管道的原则一致。
  * 绝不 overfit：关键词表是通用安全词汇，不是"看了答案后写的"。
"""

from __future__ import annotations

import hashlib
import os
from typing import Any, Callable, Dict, List, Tuple

# 与 benchmarks/corpus/external/manifest.json 的 totals 保持一致（报告口径）。
# 用质数派生确定性决策，保证同一段代码重跑得到同一个数。
_BASE_RATE_POS = 593
_BASE_RATE_TOTAL = 1110

# 朴素关键词表：安全外行 / 初级正则会写的那类"可疑词"。
# 故意**不**穷尽——它要表现的是"没有攻击结构感知"的弱点。
KEYWORD_LIST = (
    "ignore previous", "disregard", "system prompt", "exfiltrate", "exfil",
    "bypass", "override", "jailbreak", "confidential", "password", "api key",
    "secret", "send to", "email them", "email this", "send this", "grant access",
    "permanent access", "execute", "run command", "curl ", "wget ", "base64",
    "reverse shell", "sudo", "privilege", "leak", "dump", "export all",
    "forward to", "transmit", "upload to", "post to", "credential",
)


def _naive_keyword_invoke(sample: Dict[str, Any]) -> Dict[str, Any]:
    """朴素关键词启发式：text 含任一可疑词即报 serious。"""
    sid = sample.get("id", "unknown")
    text = sample.get("text", "") or ""
    low = text.lower()
    hit = any(kw in low for kw in KEYWORD_LIST)
    if not hit:
        return {"sample_id": sid, "detected": False, "severity": None}
    # 朴素启发式不分严重度，统一按 high 计入 serious_only 口径。
    return {"sample_id": sid, "detected": True, "severity": "high"}


def _naive_random_invoke(sample: Dict[str, Any]) -> Dict[str, Any]:
    """零信号随机基线：按正样本先验概率 p 用确定性哈希决定是否报。"""
    sid = sample.get("id", "unknown")
    # 样本 id 是语料内稳定主键；用 SHA256(id) 派生 [0,1)，与运行顺序无关。
    digest = hashlib.sha256(("naive-random-v1:" + sid).encode("utf-8")).digest()
    frac = int.from_bytes(digest[:8], "big") / (2 ** 64)
    p = _BASE_RATE_POS / _BASE_RATE_TOTAL
    detected = frac < p
    if not detected:
        return {"sample_id": sid, "detected": False, "severity": None}
    return {"sample_id": sid, "detected": True, "severity": "high"}


def _always_available() -> Tuple[bool, str]:
    return True, "离线启发式，零依赖，恒可用"


def _reg_naive_keyword() -> Any:
    from runner import Baseline  # 延迟导入，避免模块级环形依赖
    return Baseline(
        name="Naive keyword heuristic", version="v1 (heuristic)", offline=True,
        command="python benchmarks/baselines/naive_baselines.py --keyword",
        check=_always_available, invoke=_naive_keyword_invoke, rule_count=0,
        source="本项目（朴素关键词基线，无攻击结构感知）")


def _reg_naive_random() -> Any:
    from runner import Baseline  # 延迟导入，避免模块级环形依赖
    return Baseline(
        name="Random guess (base-rate)", version="v1 (seed=sha256-id)",
        offline=True,
        command="python benchmarks/baselines/naive_baselines.py --random",
        check=_always_available, invoke=_naive_random_invoke, rule_count=0,
        source="本项目（零信号随机/最多数基线，p=593/1110）")


def naive_baselines() -> List[Any]:
    """朴素基线列表（确定性顺序）。"""
    return [_reg_naive_keyword(), _reg_naive_random()]


if __name__ == "__main__":
    # 仅作为自测：打印两个基线在全部样本上的命中数，便于人工 sanity check。
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import rule_corpus
    corpus = rule_corpus.load_external_corpus()
    pos = corpus.get("positives", ())
    neg = corpus.get("negatives", ())
    kw_hits = sum(1 for s in pos if _naive_keyword_invoke(s)["detected"])
    kw_fp = sum(1 for s in neg if _naive_keyword_invoke(s)["detected"])
    rd_hits = sum(1 for s in pos if _naive_random_invoke(s)["detected"])
    rd_fp = sum(1 for s in neg if _naive_random_invoke(s)["detected"])
    print("keyword  recall=%d/%d  fp=%d/%d" % (kw_hits, len(pos), kw_fp, len(neg)))
    print("random   recall=%d/%d  fp=%d/%d" % (rd_hits, len(pos), rd_fp, len(neg)))
