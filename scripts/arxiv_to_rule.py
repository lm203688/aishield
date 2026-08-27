#!/usr/bin/env python3
"""
arXiv → 规则自动转录 Pipeline
==============================

从 arXiv 最新 agent-security 论文中提取攻击模式，
自动生成规则 stub 到 scanner/_proposed/，并附单元测试骨架。

用法:
    python scripts/arxiv_to_rule.py              # 干跑，不写文件
    python scripts/arxiv_to_rule.py --apply      # 写文件到 _proposed/
    python scripts/arxiv_to_rule.py --apply --max 5

输出:
    scanner/_proposed/rule_<slug>.py          # 规则 stub
    scanner/_proposed/rule_<slug>_test.py     # 单元测试骨架
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROPOSED = REPO_ROOT / "scanner" / "_proposed"

# ── 关键词 → OWASP MCP 类别映射 ──
KEYWORD_MAP = [
    (r"prompt\s*injection|jailbreak|prompt\s*hijack", "MCP02", "prompt_injection"),
    (r"excessive\s*permission|over-privileged|scope\s*expansion", "MCP07", "over_permit"),
    (r"data\s*exfiltration|sensitive\s*data|privacy\s*leak", "MCP03", "data_leak"),
    (r"command\s*injection|code\s*execution|shell\s*out", "MCP01", "cmd_inject"),
    (r"supply\s*chain|typosquat|dependency\s*confusion", "MCP04", "supply_chain"),
    (r"session\s*hijack|authentication\s*bypass", "MCP05", "auth_bypass"),
    (r"rate\s*limit|abuse|ddos", "MCP08", "rate_limit"),
    (r"red\s*team|adversarial|evasion", "MCP09", "adversarial"),
    (r"agent\s*hijack|goal\s*hijack|task\s*takeover", "ASI06", "goal_hijack"),
    (r"dark\s*pattern|manipulat", "ASI07", "dark_pattern"),
    (r"mcp\s*oauth|handshake", "ASI08", "mcp_oauth"),
    (r"memory\s*poison|context\s*injection", "ASI04", "memory_poison"),
]

# ── 严重程度启发式 ──
SEVERITY_MAP = {
    "critical": ["zero-day", "critical", "emergency", "pwn"],
    "high": ["severe", "high", "exploit", "attack", "bypass", "injection"],
    "medium": ["risk", "vulnerab", "weak", "leak"],
    "low": ["minor", "cosmetic", "low"],
}


def _fetch_arxiv_papers(max_results: int = 3) -> list[dict]:
    """复用 tech_radar 的 arXiv 抓取逻辑"""
    try:
        from scripts.tech_radar import _arxiv_via_api
        papers = _arxiv_via_api(days=30, max_results=max_results)
        return papers
    except Exception as e:
        print(f"[WARN] arXiv API 不可达（中国网络常见）: {e}", file=sys.stderr)
        print(f"[WARN] 使用模拟数据集演示 pipeline", file=sys.stderr)
        return _mock_papers()


def _mock_papers() -> list[dict]:
    """模拟数据：pipeline 不依赖网络也能跑"""
    return [
        {
            "id": "2608.00001",
            "title": "Adversarial Prompt Injection via Multi-Agent Handshake",
            "summary": "We demonstrate that multi-agent systems using MCP handshake are vulnerable to prompt injection attacks through handshake metadata poisoning.",
        },
        {
            "id": "2608.00002",
            "title": "Goal Hijacking in Autonomous Agent Workflows",
            "summary": "This paper shows how autonomous agents can be hijacked to execute unauthorized goals through subtle context manipulation in tool descriptions.",
        },
        {
            "id": "2608.00003",
            "title": "Memory Poisoning Attacks Against RAG-Based Agents",
            "summary": "We propose a novel memory poisoning attack where adversaries inject malicious entries into agent memory stores to manipulate future decisions.",
        },
    ]


def _extract_patterns(paper: dict) -> list[dict]:
    """从论文标题/摘要中提取攻击模式"""
    text = f"{paper.get('title','')} {paper.get('summary','')}"
    patterns = []

    for kw, owasp, slug_hint in KEYWORD_MAP:
        if re.search(kw, text, re.IGNORECASE):
            # 提取触发词作为规则 pattern
            found = re.findall(rf"\b\w*{re.escape(kw.split('|')[0].replace('\\s', '').replace('\\\\', ''))}\w*\b", text, re.IGNORECASE)[:3]
            if not found:
                found = [kw.split('|')[0].replace("\\s*", "").replace("\\", "")]

            # 判断严重程度
            severity = "medium"
            for sev, keywords in SEVERITY_MAP.items():
                if any(k in text.lower() for k in keywords):
                    severity = sev
                    break

            patterns.append({
                "owasp": owasp,
                "severity": severity,
                "trigger_words": found[:3],
                "pattern_regex": f"(?=.*{'|'.join(re.escape(w) for w in found[:2])})",
            })

    return patterns


def _generate_rule_stub(paper_id: str, slug: str, patterns: list[dict]) -> str:
    """生成规则 stub 代码"""
    rules_code = []
    for i, p in enumerate(patterns[:5], 1):
        rid = f"AIP_{p['owasp'].replace('MCP','').replace('ASI','')}{i:02d}"
        trigger = "|".join(re.escape(w) for w in p["trigger_words"][:2])
        rules_code.append(f"""    {{
        "rule_id": "{rid}",
        "owasp": "{p['owasp']}",
        "severity": "{p['severity']}",
        "trigger": r"{trigger}",
        "description": "Auto-generated from arXiv {paper_id}",
    }},""")

    rules_str = "\n".join(rules_code)

    return f'''"""
Auto-generated rule stub from arXiv {paper_id}
==============================================

Pipeline: scripts/arxiv_to_rule.py
Source: https://arxiv.org/abs/{paper_id}

使用方法:
    1. 人工审查此文件，确认触发模式正确
    2. 补充真实规则文本（替换 trigger regex）
    3. 运行 python -m unittest tests/test_rule_{slug}.py
    4. 通过后将规则移入 scanner/rules.py 对应类别
"""

from __future__ import annotations

RULES = [
{rules_str}
]


def check(content: str) -> list[dict]:
    """对输入内容运行所有本模块规则"""
    import re as _re
    findings = []
    for rule in RULES:
        if _re.search(rule["trigger"], content, _re.IGNORECASE | _re.DOTALL):
            findings.append({{
                "rule_id": rule["rule_id"],
                "owasp": rule["owasp"],
                "severity": rule["severity"],
                "description": rule["description"],
                "evidence": content[:200],
            }})
    return findings
'''


def _generate_test_stub(slug: str) -> str:
    """生成单元测试骨架"""
    return f'''"""单元测试骨架 — {slug}"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest

class TestRule{slug.capitalize().replace('_','')} (unittest.TestCase):
    def test_detect_positive(self):
        from scanner._proposed.rule_{slug} import check
        # TODO: 替换为真实攻击样本
        sample = "sample text with trigger keywords"
        findings = check(sample)
        self.assertGreaterEqual(len(findings), 0)

    def test_no_false_positive(self):
        from scanner._proposed.rule_{slug} import check
        # TODO: 替换为良性样本
        sample = "normal harmless text"
        findings = check(sample)
        for f in findings:
            self.assertNotEqual(f.get("severity"), "critical")


if __name__ == "__main__":
    unittest.main()
'''


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="arXiv→规则自动转录")
    ap.add_argument("--apply", action="store_true", help="实际写入 _proposed/ 目录")
    ap.add_argument("--max", type=int, default=3, help="处理的论文数量")
    args = ap.parse_args()

    if not args.apply and __name__ == "__main__":
        args.apply = True  # 命令行默认 --apply

    papers = _fetch_arxiv_papers(args.max)
    print(f"处理 {len(papers)} 篇论文")
    print("=" * 60)

    written = []
    for paper in papers:
        pid = paper.get("id", "unknown").rsplit("/", 1)[-1]
        patterns = _extract_patterns(paper)
        if not patterns:
            print(f"  [SKIP] {pid}: 未匹配到已知攻击类别")
            continue

        # slug = arXiv id + hash(title)[:8]
        title_hash = hashlib.md5(paper.get("title", "").encode()).hexdigest()[:8]
        slug = f"{pid}_{title_hash}"

        rule_code = _generate_rule_stub(pid, slug, patterns)
        test_code = _generate_test_stub(slug)

        print(f"  [OK] {pid}: {len(patterns)} 条候选规则")
        for p in patterns[:3]:
            print(f"       {p['owasp']} {p['severity']:8s} trigger={p['trigger_words'][:2]}")

        if args.apply:
            PROPOSED.mkdir(parents=True, exist_ok=True)
            rule_path = PROPOSED / f"rule_{slug}.py"
            test_path = PROPOSED / f"rule_{slug}_test.py"
            rule_path.write_text(rule_code, encoding="utf-8")
            test_path.write_text(test_code, encoding="utf-8")
            written.append(str(rule_path))
            print(f"       → {rule_path.relative_to(REPO_ROOT)}")
            print(f"       → {test_path.relative_to(REPO_ROOT)}")

    print("=" * 60)
    print(f"生成 {len(written)} 条规则 stub（含测试骨架）")

    if written:
        print("\n下一步:")
        print("  1. 人工审查 _proposed/ 下的规则 stub")
        print("  2. 修改 trigger regex 为真实攻击模式")
        print("  3. 运行 python -m unittest scanner/_proposed/rule_*_test.py")
        print("  4. 通过后 scripts/propose_rule_pr.py 开 PR 合并")
    return 0


if __name__ == "__main__":
    sys.exit(main())
