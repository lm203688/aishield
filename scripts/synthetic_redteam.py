# -*- coding: utf-8 -*-
"""
scripts/synthetic_redteam.py — 合成红队 harness（蓝图 Program F · 合成红队）v0.1
=================================================================================

蓝图定位（AIShield 下一阶段跃迁蓝图 §3 Program F）
--------------------------------------------------
"agent 对抗 agent"：用红队探针生成对抗样本，自动压测检测器（蓝方），
找出逃逸点（evasion），再把逃逸样本反哺成 NSE 训练集（Program A）。

本模块做三件事：
  1. **取种**：复用 scanner.red_team_probe 的 17 个真实攻击探针作种子。
  2. **变异**：对种子做确定性变形（base64 / hex / 零宽字符 / 同形字 /
     指令拆分 / markdown 包裹），保留原攻击类别（expected_types 不变）。
  3. **对抗 + 反哺**：把种子与变异体喂给"蓝方"检测器，统计逃逸率；
     把"应检出的正样本"结构化为 NSE corpus 记录（含归因类别）。

设计纪律
--------
* 零随机：所有变异是确定性的，可复现、可单测钉死。
* 不碰被跟踪数据：corpus 默认只打到 stdout；仅当显式 `--write` 才落盘，
  且落盘路径由调用方指定（默认 scanner/_proposed/，属未跟踪草稿区）。
* 防御器可注入：本地用 NSE / 既有规则集，CI 亦可挂接，不绑定具体实现。

红队伦理边界
------------
本模块只产出"对抗样本文本"用于自检，**不执行任何攻击**；变异体是静态字符串，
逃逸报告是"检测器缺口"而非"漏洞利用指南"。
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import sys
from typing import Any, Callable, Dict, List, Optional

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scanner import red_team_probe as rtp  # noqa: E402


# ── 确定性变异算子 ────────────────────────────────────────────────────────
def mut_base64(text: str) -> str:
    """把整段 payload 做 base64（模拟"编码绕过"类逃逸）。"""
    return "b64:" + base64.b64encode(text.encode("utf-8")).decode("ascii")


def mut_hex(text: str) -> str:
    """逐字符 hex 编码（模拟 hex 混淆）。"""
    return "hex:" + text.encode("utf-8").hex()


def mut_zero_width(text: str, every: int = 5) -> str:
    """每 N 个字符插入一个零宽空格（肉眼不可见，破坏字面匹配）。"""
    zw = "\u200b"
    out = []
    for i, ch in enumerate(text):
        out.append(ch)
        if i % every == every - 1 and ch not in ("\n", " "):
            out.append(zw)
    return "".join(out)


# 同形字映射（拉丁 → 视觉近似的 Unicode），模拟 homoglyph 混淆
_HOMOGLYPHS = {
    "a": "\u0430",  # 西里尔 a
    "e": "\u0435",  # 西里尔 e
    "o": "\u043e",  # 西里尔 o
    "c": "\u0441",  # 西里尔 c
    "i": "\u0456",  # 西里尔 i
    "l": "\u04cf",  # 西里尔 palindrome
    "s": "\u0455",  # 西里尔 s
}


def mut_homoglyph(text: str) -> str:
    return "".join(_HOMOGLYPHS.get(ch, ch) for ch in text)


def mut_split_instruction(text: str) -> str:
    """在关键祈使短语里插入零宽/空格，破坏连续字面匹配。"""
    target = "ignore all previous instructions"
    if target in text.lower():
        # 直接对原文做零宽插入（保持大小写）
        frag = text.lower()
        idx = frag.find(target)
        orig = text[idx: idx + len(target)]
        spaced = " ".join(orig)
        return text[:idx] + spaced + text[idx + len(target):]
    return text


def mut_markdown_wrap(text: str) -> str:
    """用代码块包裹，模拟"藏在 markdown 里"的注入。"""
    return "```\n" + text + "\n```"


_MUTATORS: Dict[str, Callable[[str], str]] = {
    "base64": mut_base64,
    "hex": mut_hex,
    "zero_width": mut_zero_width,
    "homoglyph": mut_homoglyph,
    "split_instruction": mut_split_instruction,
    "markdown_wrap": mut_markdown_wrap,
}


# ── 命中类别抽取（兼容 NSE / 规则集多种 finding 形态）────────────────────
def _collect_categories(findings: Any) -> set:
    """从检测器返回结构里抽出所有 OWASP/AIShield 类别前缀。"""
    cats: set = set()
    if findings is None:
        return cats
    items = findings
    if isinstance(findings, dict):
        # NSE 返回 {"confirmed":[...], "candidates":[...], "ratified":[...]}
        for key in ("confirmed", "candidates", "ratified", "findings"):
            if isinstance(findings.get(key), list):
                items = findings[key]
                break
    if not isinstance(items, list):
        items = [findings]
    for f in items:
        if not isinstance(f, dict):
            continue
        rid = f.get("rule_id") or f.get("id") or ""
        for token in (rid, f.get("owasp_category") or "",
                      f.get("category") or "", f.get("type") or "",
                      f.get("rule_type") or "", f.get("name") or ""):
            if not token:
                continue
            prefix = str(token).split("-")[0].split(":")[0]
            if prefix:
                cats.add(prefix)
    return cats


class SyntheticRedTeam:
    """合成红队主类：取种 → 变异 → 对抗 → 反哺。"""

    def __init__(self, mutators: Optional[List[str]] = None):
        self._mutator_names = mutators or list(_MUTATORS.keys())

    # ── 取种 ────────────────────────────────────────────────────────────
    def load_seeds(self) -> List[Dict[str, Any]]:
        """深拷贝 17 个真实探针作种子（expected_types 即应保持的攻击类别）。"""
        return rtp.get_all_probes()

    # ── 变异 ────────────────────────────────────────────────────────────
    def mutate_probe(self, probe: Dict[str, Any]) -> List[Dict[str, Any]]:
        """对单个种子的 payload 施加所有变异算子，保留攻击类别。"""
        variants: List[Dict[str, Any]] = []
        payload = probe.get("payload", "")
        for name in self._mutator_names:
            fn = _MUTATORS[name]
            try:
                variant_text = fn(payload)
            except (UnicodeError, binascii.Error):
                continue
            if variant_text == payload:
                # 算子无效果（如 split 没命中关键词）→ 跳过，避免噪声样本
                continue
            variants.append({
                "parent_probe": probe["id"],
                "parent_name": probe.get("name"),
                "mutation": name,
                "expected_types": list(probe.get("expected_types", [])),
                "severity": probe.get("severity"),
                "category": probe.get("category"),
                "text": variant_text,
            })
        return variants

    def build_dataset(self) -> List[Dict[str, Any]]:
        """种子 + 变异体，全部作为"应检出的正样本"。"""
        ds: List[Dict[str, Any]] = []
        for p in self.load_seeds():
            ds.append({
                "parent_probe": p["id"],
                "parent_name": p.get("name"),
                "mutation": "seed",
                "expected_types": list(p.get("expected_types", [])),
                "severity": p.get("severity"),
                "category": p.get("category"),
                "text": p.get("payload", ""),
            })
            ds.extend(self.mutate_probe(p))
        return ds

    # ── 对抗（agent vs agent）───────────────────────────────────────────
    def run(self, defender: Callable[[str], Any]) -> Dict[str, Any]:
        """
        defender(text) -> findings（检测器返回结构）。

        返回：
            {
              "total": N,
              "detected": N,
              "evaded": N,
              "evasion_rate": float,
              "evasions": [ {parent_probe, mutation, expected_types, text} ],
              "details": [ {parent_probe, mutation, expected, matched, detected} ],
            }
        """
        ds = self.build_dataset()
        evasions: List[Dict[str, Any]] = []
        details: List[Dict[str, Any]] = []
        detected = 0
        for rec in ds:
            expected = set(rec["expected_types"])
            try:
                findings = defender(rec["text"]) or []
            except Exception as e:  # 单条防御器异常不应中断整批
                findings = []
                rec_err = f"defender raised: {e}"
            else:
                rec_err = None
            matched = _collect_categories(findings)
            is_detected = bool(expected & matched) if expected else (
                len(matched) > 0)
            if is_detected:
                detected += 1
            else:
                evasions.append({
                    "parent_probe": rec["parent_probe"],
                    "mutation": rec["mutation"],
                    "expected_types": rec["expected_types"],
                    "text": rec["text"],
                })
            details.append({
                "parent_probe": rec["parent_probe"],
                "mutation": rec["mutation"],
                "expected": sorted(expected),
                "matched": sorted(matched),
                "detected": is_detected,
                "error": rec_err,
            })
        total = len(ds)
        return {
            "total": total,
            "detected": detected,
            "evaded": total - detected,
            "evasion_rate": round((total - detected) / total, 4) if total else 0.0,
            "evasions": evasions,
            "details": details,
        }

    # ── 反哺 NSE corpus ─────────────────────────────────────────────────
    def to_corpus_records(self) -> List[Dict[str, Any]]:
        """结构化为 NSE 正样本记录（含期望类别）。"""
        recs = []
        for rec in self.build_dataset():
            recs.append({
                "text": rec["text"],
                "expected_categories": rec["expected_types"],
                "parent_probe": rec["parent_probe"],
                "mutation": rec["mutation"],
                "severity": rec["severity"],
                "source": "synthetic_redteam",
            })
        return recs


# ── 命令行入口 ────────────────────────────────────────────────────────────
def _build_defender(name: str) -> Callable[[str], Any]:
    """构造一个防御器 callable。失败即诚实报错（不静默降级）。"""
    if name == "rules":
        from scanner import rules as rules_mod
        def _def(text: str) -> List[Dict[str, Any]]:
            out = []
            for pat, (rname, sev) in rules_mod.ALL_RULES.items():
                if re_search(pat, text):  # noqa: F821  (见下方补定义)
                    out.append({"rule_id": rname, "owasp_category": _cat_of_name(rname),
                                "severity": sev})
            return out
        return _def
    if name == "nse":
        from scanner.neuro_symbolic_probe import NeuroSymbolicProbe
        probe = NeuroSymbolicProbe()
        return lambda text: probe.scan(text)
    raise SystemExit(f"未知防御器: {name}（可选 rules / nse）")


def re_search(pat: str, text: str) -> bool:
    import re
    try:
        return re.search(pat, text) is not None
    except re.error:
        return False


def _cat_of_name(rname: str) -> str:
    # 规则名形如 "MCP01-001" / "ASI04-..." → 取前缀
    return rname.split("-")[0].split(":")[0]


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="AIShield 合成红队 harness")
    ap.add_argument("--defender", default=None,
                    help="对抗用的蓝方检测器：rules | nse（默认只列数据集）")
    ap.add_argument("--write", default=None,
                    help="把反哺 NSE 的 corpus 写入该 jsonl 路径")
    ap.add_argument("--evasion-report", action="store_true",
                    help="跑对抗并打印逃逸报告")
    ap.add_argument("--count-only", action="store_true",
                    help="只打印生成样本数")
    args = ap.parse_args(argv)

    srt = SyntheticRedTeam()
    if args.count_only:
        print(f"synthetic red-team dataset size: {len(srt.build_dataset())}")
        return 0

    if args.evasion_report:
        if not args.defender:
            print("需指定 --defender rules|nse 才能跑逃逸报告")
            return 2
        defender = _build_defender(args.defender)
        report = srt.run(defender)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.write:
        recs = srt.to_corpus_records()
        with open(args.write, "w", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"wrote {len(recs)} corpus records → {args.write}")
        return 0

    # 默认：打印数据集概览（不落盘、不跑防御器）
    ds = srt.build_dataset()
    by_mut: Dict[str, int] = {}
    for r in ds:
        by_mut[r["mutation"]] = by_mut.get(r["mutation"], 0) + 1
    print("Synthetic Red-Team Dataset")
    print("=" * 50)
    print(f"total samples: {len(ds)}")
    print(f"by mutation:   {json.dumps(by_mut, ensure_ascii=False)}")
    print("seed probes:   %d" % len(srt.load_seeds()))
    print("\n（用 --evasion-report --defender nse 跑 agent-vs-agent 压测；")
    print(" 用 --write <path>.jsonl 导出 NSE 训练集）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
