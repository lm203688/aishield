#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
release-facts.json 权威出口生成器
=================================

背景
----
2026-10-27 审计报告（§5 P0-1）指出：README 徽章显示 264 规则、正文已是 313；
ARTIFACT.md 仍把 237/264/291/40.6% 写成复现目标，与权威运行值 286/313/340/94.27%
不一致；mcp-server/README.md 同时残留 264 与新分类表。根因是"人工逐份改数字"，
每次规则晋升/版本升级都会漏改若干处。

本脚本是唯一修复：**所有对外聚合数字由一个权威命令派生**，写入
``release-facts.json``。README、ARTIFACT、徽章与发布说明只引用该文件的
生成结果，不手写副本。

权威来源（全部动态读取，无硬编码数字）
--------------------------------------
- version     : ``api.server.API_VERSION``（与 ``scripts/sync_version.py`` 同源）
- rules       : ``scanner.rules.get_rule_breakdown()`` + ``get_rule_count("skill")``
- benchmark   : ``benchmarks/corpus/external/scope_recall.json`` +
                ``benchmarks/corpus/external/manifest.json``
- protocol    : ``scanner.handshake.MCP_PROTOCOL_LATEST``、
                ``eco/guardrail_harness.py``、``eco/a2a_gateway.py``、
                ``mcp-server/package.json`` / ``package-lock.json``
- dependencies: ``setup.py``（install_requires + extras_require）、
                ``mcp-server/package.json``
- tests       : ``reports/audit-2026-10-27-tests.log``（诚实记录"未完成"，不冒充全绿）

用法
----
    python scripts/generate_release_facts.py             # 打印 computed JSON
    python scripts/generate_release_facts.py --write     # 写入 release-facts.json
    python scripts/generate_release_facts.py --check     # 与已提交文件比对，不一致 exit 1
    python scripts/generate_release_facts.py --validate-docs   # README/ARTIFACT/badge 对齐校验
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

FACTS_PATH = REPO / "release-facts.json"
SCHEMA_VERSION = 1


# ── 版本 ─────────────────────────────────────────────────────────────
def _version() -> str:
    from api.server import API_VERSION
    return API_VERSION


# ── 规则分解 ─────────────────────────────────────────────────────────
def _rules() -> Dict[str, Any]:
    from scanner.rules import get_rule_breakdown, get_rule_count
    b = get_rule_breakdown()
    return {
        "mcp": b["total"],
        "skill": get_rule_count("skill"),
        "static": b["static"],
        "generated": b["generated"],
        "radar": b["radar"],
        "breakdown_sums": b["static"] + b["generated"] + b["radar"] == b["total"],
    }


# ── 基准 ─────────────────────────────────────────────────────────────
def _benchmark() -> Optional[Dict[str, Any]]:
    sr = REPO / "benchmarks" / "corpus" / "external" / "scope_recall.json"
    mf = REPO / "benchmarks" / "corpus" / "external" / "manifest.json"
    if not sr.exists():
        return None
    data = json.loads(sr.read_text(encoding="utf-8"))
    s = data.get("summary", {})
    b = data.get("bootstrap", {})
    ext = data.get("external_summary", {})
    manifest = {}
    if mf.exists():
        m = json.loads(mf.read_text(encoding="utf-8"))
        manifest = {
            "benchmark": m.get("benchmark"),
            "collected_at": m.get("collected_at"),
            "schema_version": m.get("schema_version"),
            "family_count": m.get("family_count"),
            "cohen_kappa": m.get("cohen_kappa"),
            "label_basis": m.get("label_basis"),
            "r1_status": {"met": m.get("r1_status", {}).get("met")},
        }
    return {
        "corpus": manifest.get("benchmark", "aishield-external-corpus/v1"),
        "collected_at": manifest.get("collected_at"),
        "family_count": manifest.get("family_count") or ext.get("family_count"),
        "positives": s.get("positives") or ext.get("positives"),
        "negatives": s.get("negatives") or ext.get("negatives"),
        "detected": s.get("detected") or ext.get("detected"),
        "recall": s.get("recall") or ext.get("recall"),
        "recall_ci": {
            "low": b.get("recall_ci", {}).get("low"),
            "high": b.get("recall_ci", {}).get("high"),
            "method": b.get("recall_ci", {}).get("method", "percentile"),
            "seed": b.get("seed") or b.get("recall_ci", {}).get("seed"),
            "resamples": b.get("resamples") or b.get("recall_ci", {}).get("resamples"),
        },
        "false_positives": s.get("false_positives") or ext.get("false_positives"),
        "false_positive_rate": s.get("false_positive_rate") or ext.get("false_positive_rate"),
        "fpr_ci": {
            "low": b.get("false_positive_rate_ci", {}).get("low"),
            "high": b.get("false_positive_rate_ci", {}).get("high"),
        },
        "families_zero_detected": ext.get("families_zero_detected", []),
        "cohen_kappa": manifest.get("cohen_kappa"),
        "r1_status": manifest.get("r1_status"),
    }


# ── 协议支持 ─────────────────────────────────────────────────────────
def _grep_const(pattern: str, rel: str) -> Optional[str]:
    p = REPO / rel
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(pattern, line)
        if m:
            return m.group(1) if m.groups() else line.strip()
    return None


def _protocol() -> Dict[str, Any]:
    # MCP 最新协议版本（handshake 的权威常量）
    mcp_latest = _grep_const(r'MCP_PROTOCOL_LATEST\s*=\s*"([^"]+)"', "scanner/handshake.py")
    # Guardrail harness 返回的 protocolVersion
    guardrail = _grep_const(r'"protocolVersion"\s*:\s*"([^"]+)"', "eco/guardrail_harness.py")
    # A2A gateway
    a2a = _grep_const(r'A2A_PROTOCOL_VERSION\s*=\s*"([^"]+)"', "eco/a2a_gateway.py")
    # MCP SDK 声明与锁定
    sdk_declared = _grep_const(r'"@modelcontextprotocol/sdk"\s*:\s*"([^"]+)"',
                               "mcp-server/package.json")
    sdk_locked = None
    lock = REPO / "mcp-server" / "package-lock.json"
    if lock.exists():
        lk = json.loads(lock.read_text(encoding="utf-8"))
        try:
            sdk_locked = lk["packages"]["node_modules/@modelcontextprotocol/sdk"]["version"]
        except KeyError:
            pass
    return {
        "mcp_latest": mcp_latest,
        "guardrail_protocol": guardrail,
        "a2a_protocol": a2a,
        "mcp_sdk_declared": sdk_declared,
        "mcp_sdk_locked": sdk_locked,
    }


# ── 依赖边界 ─────────────────────────────────────────────────────────
def _dependencies() -> Dict[str, Any]:
    # Python：从 setup.py 解析 install_requires / extras_require
    setup_text = (REPO / "setup.py").read_text(encoding="utf-8")
    install_requires: List[str] = []
    m = re.search(r"install_requires\s*=\s*\[(.*?)\]", setup_text, re.S)
    if m:
        install_requires = re.findall(r'"([^"]+)"', m.group(1))
    extras: Dict[str, List[str]] = {}
    m = re.search(r"extras_require\s*=\s*\{(.*?)\n\s*\}", setup_text, re.S)
    if m:
        # 逐 extra 键拆分
        for seg in re.findall(r'"([^"]+)"\s*:\s*\[(.*?)\]', m.group(1), re.S):
            extras[seg[0]] = re.findall(r'"([^"]+)"', seg[1])
    # Node
    node_deps: Dict[str, str] = {}
    pkg = REPO / "mcp-server" / "package.json"
    if pkg.exists():
        node_deps = json.loads(pkg.read_text(encoding="utf-8")).get("dependencies", {})
    return {
        "python": {
            "install_requires": install_requires,
            "extras_require": extras,
        },
        "node": {"dependencies": node_deps},
    }


# ── 测试结果（诚实） ─────────────────────────────────────────────────
def _tests() -> Dict[str, Any]:
    log = REPO / "reports" / "audit-2026-10-27-tests.log"
    if not log.exists():
        return {"status": "unknown", "note": "未找到审计测试日志"}
    text = log.read_text(encoding="utf-8", errors="replace")
    # 审计在 300s 时限内未结束、无最终汇总 —— 必须诚实记录，不冒充全绿
    has_final = bool(re.search(r"^(Ran |OK|FAILED)", text, re.M))
    last_seen = None
    for m in re.finditer(r"^(test_\w+) ", text, re.M):
        last_seen = m.group(1)
    return {
        "status": "verified" if has_final else "incomplete",
        "note": ("全量 Python 测试在 300 秒审计时限内未结束，无最终汇总；"
                 "已执行部分未见失败，但不能据此声称全量通过。" if not has_final
                 else "审计日志含最终汇总"),
        "last_test_seen": last_seen,
        "log": "reports/audit-2026-10-27-tests.log",
    }


# ── git ──────────────────────────────────────────────────────────────
def _git() -> Dict[str, Any]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO),
            capture_output=True, text=True, check=False).stdout.strip()
    except Exception:
        commit = None
    return {"commit": commit}


def compute() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git": _git(),
        "version": _version(),
        "rules": _rules(),
        "benchmark": _benchmark(),
        "protocol": _protocol(),
        "dependencies": _dependencies(),
        "tests": _tests(),
    }


# ── 文档对齐校验（README / ARTIFACT / badge / mcp-server README） ────
_DOC_PATTERNS = [
    # (相对路径, 正则, 期望值提取函数名)
    ("README.md", r'Rules-(\d+)-blue\.svg', "rules_badge"),
    ("ARTIFACT.md", r'^\| 静态规则数 \| (\d+) \|', "rules_static"),
    ("ARTIFACT.md", r'^\| 规则总数 \| (\d+) \|', "rules_mcp"),
    ("ARTIFACT.md", r'^\| Skill 规则数 \| (\d+) \|', "rules_skill"),
    ("ARTIFACT.md", r'^\| external corpus 召回 \| ([\d.]+)%', "recall_pct"),
    ("ARTIFACT.md", r'^\| external corpus 误报 \| ([\d.]+)%', "fpr_pct"),
    ("mcp-server/README.md", r'^\*\*Total: (\d+) rules\*\* \(MCP type\) / (\d+) rules', "mcp_total"),
]


def _expected_value(kind: str, facts: Dict[str, Any]) -> str:
    if kind == "rules_badge":
        return str(facts["rules"]["mcp"])
    if kind == "rules_static":
        return str(facts["rules"]["static"])
    if kind == "rules_mcp":
        return str(facts["rules"]["mcp"])
    if kind == "rules_skill":
        return str(facts["rules"]["skill"])
    if kind == "recall_pct":
        return f"{facts['benchmark']['recall'] * 100:.1f}"
    if kind == "fpr_pct":
        return f"{facts['benchmark']['false_positive_rate'] * 100:.1f}"
    if kind == "mcp_total":
        return f"{facts['rules']['mcp']}/{facts['rules']['skill']}"
    return ""


def validate_docs(facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """返回文档数字与 release-facts 不一致的条目。"""
    problems = []
    for rel, pattern, kind in _DOC_PATTERNS:
        p = REPO / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(pattern, text, re.M)
        if not m:
            continue
        got = "/".join(m.groups()) if m.groups() else m.group(1)
        want = _expected_value(kind, facts)
        if got != want:
            problems.append({
                "file": rel, "kind": kind,
                "got": got, "want": want, "match": m.group(0)[:60],
            })
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="release-facts.json 权威出口生成器")
    ap.add_argument("--write", action="store_true", help="写入 release-facts.json")
    ap.add_argument("--check", action="store_true",
                    help="与已提交文件比对，不一致则 exit 1（CI 门禁）")
    ap.add_argument("--validate-docs", action="store_true",
                    help="校验 README/ARTIFACT/badge 与 release-facts 对齐")
    args = ap.parse_args()

    facts = compute()

    if args.check:
        if not FACTS_PATH.exists():
            print(f"❌ {FACTS_PATH} 不存在 —— 先运行 --write 并提交")
            return 1
        committed = json.loads(FACTS_PATH.read_text(encoding="utf-8"))
        # 排除 generated_at / git 之外，比对语义核心
        for key in ("version", "rules", "protocol", "dependencies"):
            if committed.get(key) != facts.get(key):
                print(f"❌ release-facts.json 的 {key} 已过期（未再生成）")
                print(f"   committed: {json.dumps(committed.get(key), ensure_ascii=False)}")
                print(f"   computed : {json.dumps(facts.get(key), ensure_ascii=False)}")
                return 1
        if committed.get("benchmark") != facts.get("benchmark"):
            print("❌ release-facts.json 的 benchmark 已过期（未再生成）")
            return 1
        print("✅ release-facts.json 与权威源一致")
        return 0

    if args.validate_docs:
        problems = validate_docs(facts)
        if problems:
            for p in problems:
                print(f"❌ {p['file']} [{p['kind']}]: 文档写 {p['got']}，应 {p['want']}"
                      f"  〔{p['match']}〕")
            return 1
        print("✅ README / ARTIFACT / badge / mcp-server README 与 release-facts 对齐")
        return 0

    if args.write:
        FACTS_PATH.write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
        print(f"✅ 已写入 {FACTS_PATH}")
        print(f"   version={facts['version']} rules={facts['rules']['mcp']}"
              f" (static {facts['rules']['static']} + generated {facts['rules']['generated']}"
              f" + radar {facts['rules']['radar']}) skill={facts['rules']['skill']}"
              f" recall={facts['benchmark']['recall']}")
        return 0

    print(json.dumps(facts, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
