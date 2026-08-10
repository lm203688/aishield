#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对外发布物自检门禁（distribution gate）。

动机：AIShield 是安全扫描器，**自己投放出去的东西必须先过自己的扫描器**。
2026-08-10 Agensi 首个真实下载暴露的问题是「已发布但源没留底」——
外部世界拿到了一份仓库里无法复核的产物，这对一家做信任的项目是硬伤。

本脚本做三件事：
  1. 台账完整性：`distribution/published.json` 里每条 entry 的 source_dir
     必须真实存在且非空（source_status=missing 直接判失败）。
  2. 内容安全自检：复用 scanner 引擎（rules/dependency/secrets/poisoning/taint）
     扫每份发布源，命中 critical/high 即判失败，overall_score 低于阈值也失败。
  3. 出报告：Markdown / JSON 两种，供守夜与 CI 消费。

不变量（与主扫描器一致）：
  - 只读文件，**绝不执行**发布物里的任何命令
  - 不发起网络请求

用法：
    python scripts/verify_distribution.py            # 人读报告
    python scripts/verify_distribution.py --json     # 机器消费
    python scripts/verify_distribution.py --quiet    # 只出结论，靠 exit code
退出码：0 = 全部通过；1 = 有条目未通过；2 = 台账本身有问题。
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scanner.workspace_scan import _local_pipeline, _read_text  # noqa: E402

LEDGER_PATH = os.path.join(ROOT, "distribution", "published.json")

# 只扫文本类发布物；二进制/锁文件跳过
TEXT_EXT = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".js", ".ts",
            ".sh", ".toml", ".cfg", ".ini", ".html"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
MAX_FILES = 200

DEFAULT_POLICY = {
    "min_overall_score": 80,
    "block_severities": ["critical", "high"],
    "require_source_in_repo": True,
}


def load_ledger(path=LEDGER_PATH):
    """读台账。返回 (ledger, error)。"""
    if not os.path.exists(path):
        return None, f"台账不存在: {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as exc:
        return None, f"台账解析失败: {exc}"
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        return None, "台账结构非法：缺少 entries 数组"
    return data, None


def collect_source_files(source_dir, max_files=MAX_FILES):
    """收集发布源里的文本文件 -> {relpath: content}。纯读取，不执行。"""
    files = {}
    abs_dir = source_dir if os.path.isabs(source_dir) else os.path.join(ROOT, source_dir)
    if not os.path.isdir(abs_dir):
        return files
    for cur, dirnames, filenames in os.walk(abs_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            ext = os.path.splitext(fn)[1].lower()
            if ext not in TEXT_EXT:
                continue
            full = os.path.join(cur, fn)
            rel = os.path.relpath(full, abs_dir).replace("\\", "/")
            files[rel] = _read_text(full)
            if len(files) >= max_files:
                return files
    return files


def _tool_type_for(entry):
    kind = (entry.get("kind") or "").lower()
    return "skill" if kind in ("skill", "prompt", "gpt") else "mcp"


def verify_entry(entry, policy):
    """校验单条发布物。返回结果字典。"""
    name = entry.get("name") or "<unnamed>"
    channel = entry.get("channel") or "<unknown>"
    source_dir = entry.get("source_dir") or ""
    status = (entry.get("source_status") or "").lower()

    result = {
        "channel": channel,
        "name": name,
        "version": entry.get("version"),
        "published_version": entry.get("published_version"),
        "source_dir": source_dir,
        "source_status": status,
        "passed": False,
        "reasons": [],
        "overall_score": None,
        "blocking_findings": [],
        "file_count": 0,
    }

    if not source_dir:
        result["reasons"].append("台账未声明 source_dir")
        return result

    if status == "missing":
        result["reasons"].append("源未留底（source_status=missing）——外部已拿到但仓库无法复核")
        if policy.get("require_source_in_repo", True):
            return result

    files = collect_source_files(source_dir)
    result["file_count"] = len(files)
    if not files:
        result["reasons"].append(f"源目录为空或不存在: {source_dir}")
        return result

    report = _local_pipeline(files, name, tool_type=_tool_type_for(entry))
    score = report.get("overall_score")
    result["overall_score"] = score

    block = set(policy.get("block_severities") or [])
    blocking = [
        {
            "severity": f.get("severity"),
            "type": f.get("type"),
            "description": f.get("description"),
            "file": f.get("file"),
        }
        for f in report.get("findings", [])
        if f.get("severity") in block
    ]
    result["blocking_findings"] = blocking
    result["total_findings"] = report.get("total_findings", 0)

    if blocking:
        result["reasons"].append(f"命中 {len(blocking)} 条阻断级发现（{'/'.join(sorted(block))}）")

    min_score = policy.get("min_overall_score", 80)
    if score is None or score < min_score:
        result["reasons"].append(f"评分 {score} 低于阈值 {min_score}")

    # published 了但版本对不上，只提示不阻断
    pv = entry.get("published_version")
    if pv and pv != entry.get("version"):
        result["reasons"].append(
            f"提示：线上版本 {pv} 与仓库源版本 {entry.get('version')} 不一致，下次更新需覆盖发布"
        )

    hard_fail = bool(blocking) or score is None or score < min_score
    if status == "missing" and policy.get("require_source_in_repo", True):
        hard_fail = True
    result["passed"] = not hard_fail
    return result


def verify_all(ledger=None):
    """跑全量校验。返回汇总字典。"""
    if ledger is None:
        ledger, err = load_ledger()
        if err:
            return {"ok": False, "error": err, "results": []}
    policy = dict(DEFAULT_POLICY)
    policy.update(ledger.get("policy") or {})

    results = [verify_entry(e, policy) for e in ledger.get("entries", [])]
    failed = [r for r in results if not r["passed"]]
    return {
        "ok": not failed,
        "policy": policy,
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "results": results,
        "invariants": {"no_execute": True, "no_network": True},
    }


def render_markdown(summary):
    lines = ["# 对外发布物自检报告", ""]
    if summary.get("error"):
        lines.append(f"**台账错误**：{summary['error']}")
        return "\n".join(lines)

    verdict = "全部通过" if summary["ok"] else f"{summary['failed']} 条未通过"
    lines.append(f"**结论**：{verdict}（共 {summary['total']} 条）")
    pol = summary["policy"]
    lines.append(
        f"**策略**：最低分 {pol['min_overall_score']}，"
        f"阻断等级 {'/'.join(pol['block_severities'])}，"
        f"要求源留底 {'是' if pol.get('require_source_in_repo', True) else '否'}"
    )
    lines.append("")
    lines.append("| 渠道 | 产物 | 源状态 | 文件数 | 评分 | 阻断项 | 结果 |")
    lines.append("|------|------|--------|--------|------|--------|------|")
    for r in summary["results"]:
        lines.append(
            "| {ch} | {nm} | {st} | {fc} | {sc} | {bl} | {res} |".format(
                ch=r["channel"], nm=r["name"], st=r["source_status"] or "-",
                fc=r["file_count"],
                sc="-" if r["overall_score"] is None else r["overall_score"],
                bl=len(r["blocking_findings"]),
                res="通过" if r["passed"] else "未通过",
            )
        )
    notes = [r for r in summary["results"] if r["reasons"]]
    if notes:
        lines.append("")
        lines.append("## 明细")
        for r in notes:
            lines.append(f"- **{r['channel']}/{r['name']}**")
            for reason in r["reasons"]:
                lines.append(f"  - {reason}")
            for f in r["blocking_findings"][:5]:
                lines.append(f"  - [{f['severity']}] {f['description']} ({f['file']})")
    lines.append("")
    lines.append("> 不变量：只读扫描，不执行发布物中的任何命令，不发起网络请求。")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="AIShield 对外发布物自检门禁")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--quiet", action="store_true", help="只输出一行结论")
    args = parser.parse_args(argv)

    ledger, err = load_ledger()
    if err:
        print(f"台账错误：{err}")
        return 2

    summary = verify_all(ledger)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif args.quiet:
        print(f"distribution gate: {summary['passed']}/{summary['total']} passed")
    else:
        print(render_markdown(summary))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
