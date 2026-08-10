#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/scan_workspace.py — Pre-flight workspace scan CLI

给 agent 计算机（forge / Goose / Open Interpreter / Claude Desktop …）做
启动前安全扫描：识别平台、解析 MCP/skill 配置、复用 AIShield 引擎出报告。

核心不变量：**绝不 spawn** 配置中的任何命令、**绝不联网抓取**。

用法：
    python scripts/scan_workspace.py <workspace_dir>
    python scripts/scan_workspace.py <workspace_dir> --json
    python scripts/scan_workspace.py <workspace_dir> --md report.md
    python scripts/scan_workspace.py <workspace_dir> --quiet   # 只输出 overall 判定
"""
import argparse
import json as json_mod
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scanner.workspace_scan import preflight, render_markdown


def main():
    p = argparse.ArgumentParser(
        prog="aishield-scan-workspace",
        description="Pre-flight workspace scan for agent runtimes (forge / Goose / Open Interpreter / Claude Desktop …)",
    )
    p.add_argument("workspace", help="要扫描的 workspace 目录路径")
    p.add_argument("--json", action="store_true", help="输出 JSON 到 stdout")
    p.add_argument("--md", metavar="PATH", help="输出 Markdown 报告到指定文件")
    p.add_argument("--quiet", action="store_true", help="只打印整体判定行（适合 CI）")
    args = p.parse_args()

    report = preflight(args.workspace)

    if args.json:
        json_mod.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0 if (report.get("summary", {}).get("overall_assessment") != "danger") else 1

    md = render_markdown(report)

    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
        if not args.quiet:
            print(f"Markdown 报告已写入: {args.md}")
    else:
        sys.stdout.write(md)

    if args.quiet:
        s = report.get("summary", {})
        verdict = s.get("overall_assessment", "unknown")
        print(f"[aishield] {verdict.upper()} — score={s.get('overall_score')} items={s.get('items_total')} high={s.get('items_high_risk')}")
        return 0 if verdict != "danger" else 1

    s = report.get("summary", {})
    return 0 if s.get("overall_assessment") != "danger" else 1


if __name__ == "__main__":
    sys.exit(main())