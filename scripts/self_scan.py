#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""台账外自检（off-ledger self-scan）+ 自指误报消噪。

背景：`verify_distribution.py` 只看 `distribution/published.json` 台账内的 5 条，
但仓库里还有一批**已发布/待发布但不在台账射程**的制品（npm 源 mcp-server/src、
DSH 骨架、guardrail-harness、github-marketplace Action、listings 等）。守夜会补扫
这些目录，结果里混着 13 条"扫描器自指误报"（检测器词汇 / 演示载荷 / 只读
preflight），长期淹没真实信号。

本脚本是那一步的**单一、可复用入口**：
  1. 扫台账内外全部源；
  2. 用 `distribution/self_reference_allowlist.json` 把自指误报标注为
     self_reference（不再阻断）并保留理由；
  3. 输出"未登记的阻断级发现"——**这才是真实信号**，非零即 exit 1；
  4. 反向校验 allowlist 是否腐烂（条目已不匹配任何实际发现 → stale，提示清理）。

不变量：只读文件，绝不执行发布物里的任何命令，不发起网络请求。
用法：
    python scripts/self_scan.py            # 人读报告
    python scripts/self_scan.py --json     # 机器消费
    python scripts/self_scan.py --quiet    # 一行结论 + exit code
退出码：0 = 无未登记的阻断级发现；1 = 存在真实信号；2 = 清单本身有问题。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from scanner.self_reference import load_allowlist, split_findings, blocking_of  # noqa: E402
from scanner.workspace_scan import _local_pipeline  # noqa: E402
from verify_distribution import collect_source_files, _tool_type_for  # noqa: E402

LEDGER_PATH = os.path.join(ROOT, "distribution", "published.json")

# 台账射程之外、但确实对外发布/随仓库分发的源（与守夜补扫目录对齐）
OFF_LEDGER_SOURCES = [
    "mcp-server/src",
    "distribution/deepseek-harness",
    "distribution/guardrail-harness",
    "distribution/github-marketplace",
    "distribution/listings",
    "distribution/claude-skill",
    "distribution/gpt-store",
    "distribution/huggingface",
    "distribution/clawhub",
    "action_entrypoint.py",
]


def _scan_sources():
    """返回去重后的 (source, is_dir) 列表：台账 source_dir + 台账外源。"""
    sources = []
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, "r", encoding="utf-8") as f:
                ledger = json.load(f)
            for e in ledger.get("entries", []):
                sd = e.get("source_dir")
                if sd:
                    sources.append(sd)
        except (OSError, ValueError):
            pass
    sources.extend(OFF_LEDGER_SOURCES)
    seen, out = set(), []
    for s in sources:
        key = s.replace("\\", "/").rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def scan(allowlist=None):
    allowlist = allowlist or load_allowlist()
    results, used_keys = [], set()
    totals = {"findings": 0, "suppressed": 0, "blocking_unsuppressed": 0}

    for source in _scan_sources():
        abs_p = os.path.join(ROOT, source)
        if not (os.path.isdir(abs_p) or os.path.isfile(abs_p)):
            continue
        if os.path.isfile(abs_p):
            from scanner.workspace_scan import _read_text
            files = {os.path.basename(abs_p): _read_text(abs_p)}
            tool_type = "skill"
        else:
            files = collect_source_files(source)
            tool_type = _tool_type_for({"kind": "mcp" if "mcp" in source else "skill"})
        if not files:
            continue

        report = _local_pipeline(files, os.path.basename(source.rstrip("/")) or source,
                                 tool_type=tool_type)
        kept, suppressed = split_findings(source, report.get("findings", []), allowlist)
        for f in suppressed:
            used_keys.add((source.replace("\\", "/"), (f.get("file") or "").replace("\\", "/"),
                           f.get("type")))
        blocking = blocking_of(kept)

        results.append({
            "source": source,
            "files": len(files),
            "overall_score": report.get("overall_score"),
            "findings": report.get("total_findings", len(report.get("findings", []))),
            "suppressed": len(suppressed),
            "blocking_unsuppressed": blocking,
        })
        totals["findings"] += report.get("total_findings", 0)
        totals["suppressed"] += len(suppressed)
        totals["blocking_unsuppressed"] += len(blocking)

    # allowlist 腐烂检测：条目已不匹配任何实际发现
    stale = [k for k in (allowlist.get("index") or {}) if k not in used_keys]

    return {
        "sources": results,
        "totals": totals,
        "stale_allowlist_entries": sorted("/".join(k) for k in stale),
        "allowlist_version": allowlist.get("version", 0),
        "ok": totals["blocking_unsuppressed"] == 0,
        "invariants": {"no_execute": True, "no_network": True},
    }


def render_markdown(summary):
    t = summary["totals"]
    lines = ["# 台账外自检报告（自指误报已消噪）", ""]
    lines.append(f"**结论**：{'通过' if summary['ok'] else '存在未登记的阻断级发现'} — "
                 f"发现 {t['findings']} / 自指误报 {t['suppressed']} / "
                 f"未登记阻断 {t['blocking_unsuppressed']}")
    lines.append("")
    lines.append("| 源 | 文件 | 评分 | 发现 | 自指误报 | 未登记阻断 |")
    lines.append("|----|------|------|------|----------|------------|")
    for r in summary["sources"]:
        lines.append("| {s} | {f} | {sc} | {n} | {sup} | {b} |".format(
            s=r["source"], f=r["files"],
            sc="-" if r["overall_score"] is None else r["overall_score"],
            n=r["findings"], sup=r["suppressed"],
            b=len(r["blocking_unsuppressed"])))
    if summary["stale_allowlist_entries"]:
        lines.append("")
        lines.append("## ⚠️ 允许清单腐烂（条目已不匹配任何发现，建议清理）")
        for k in summary["stale_allowlist_entries"]:
            lines.append(f"- `{k}`")
    real = [(r["source"], f) for r in summary["sources"] for f in r["blocking_unsuppressed"]]
    if real:
        lines.append("")
        lines.append("## 🚨 未登记的阻断级发现（真实信号，必须处理）")
        for src, f in real:
            lines.append(f"- **{src}** [{f.get('severity')}] {f.get('type')} "
                         f"{f.get('file')} — {f.get('description')}")
    lines.append("")
    lines.append("> 不变量：只读扫描，不执行发布物中的任何命令，不发起网络请求。")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="台账外自检 + 自指误报消噪")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    summary = scan()
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif args.quiet:
        print(f"off-ledger self-scan: blocking_unsuppressed="
              f"{summary['totals']['blocking_unsuppressed']} "
              f"suppressed={summary['totals']['suppressed']} "
              f"stale_allowlist={len(summary['stale_allowlist_entries'])}")
    else:
        print(render_markdown(summary))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
