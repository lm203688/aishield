#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 自动化台账生成器
========================
解决问题：automation/task-registry.md 长期由人手维护，声称"28 个定时任务在跑"，
实际本仓库只有 15 个 workflow，且其中 self-heal 已静默失效 48 天。台账一旦失真，
所有基于它的决策（"我们自动化程度很高"）都是错的，而且没人会去核对。

结构性对策：台账不再手写，改由本脚本从 .github/workflows/ 的真实内容派生。
台账 = 现实的投影，就不可能再失真。

派生内容：
  · 每个 workflow 的真实触发器（cron 译成人话 / push / issues / dispatch）
  · job 数、依赖链、是否具备闭环四环节
  · 引用的本地脚本（缺失会被标红）
  · 状态总线中该域的最近更新时间（有则显示）

用法：
  python scripts/gen_task_registry.py            # 写入 automation/task-registry.md
  python scripts/gen_task_registry.py --check    # 只校验是否过期（CI 用，过期退出码 1）
  python scripts/gen_task_registry.py --stdout   # 打印不写盘
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
WF_DIR = REPO_ROOT / ".github" / "workflows"
REGISTRY = REPO_ROOT / "automation" / "task-registry.md"
STATE_DIR = REPO_ROOT / "data" / "state"

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

WEEK = {"0": "周日", "1": "周一", "2": "周二", "3": "周三",
        "4": "周四", "5": "周五", "6": "周六", "7": "周日"}


def cron_to_cn(expr: str) -> str:
    """把 cron 表达式翻译成中文人话（UTC 时间，标注时区避免误读）。"""
    parts = str(expr).split()
    if len(parts) != 5:
        return f"cron `{expr}`（字段数异常）"
    minute, hour, dom, mon, dow = parts

    if hour.startswith("*/"):
        return f"每 {hour[2:]} 小时（第 {minute} 分）UTC"
    if hour == "*":
        return f"每小时第 {minute} 分 UTC"

    hhmm = f"{int(hour):02d}:{int(minute):02d}" if hour.isdigit() and minute.isdigit() else f"{hour}:{minute}"

    if dow != "*":
        days = "、".join(WEEK.get(d.strip(), d.strip()) for d in dow.split(","))
        return f"每{days} {hhmm} UTC"
    if dom != "*":
        return f"每月 {dom} 日 {hhmm} UTC"
    if mon != "*":
        return f"{mon} 月 {dom} 日 {hhmm} UTC"
    return f"每日 {hhmm} UTC"


def triggers_of(data: Dict[str, Any]) -> tuple[List[str], List[str]]:
    """返回 (定时触发描述列表, 事件触发描述列表)。"""
    on = data.get("on", data.get(True)) or {}
    crons: List[str] = []
    events: List[str] = []

    if isinstance(on, str):
        return crons, [on]
    if isinstance(on, list):
        return crons, [str(x) for x in on]

    for key, val in on.items():
        k = str(key)
        if k == "schedule":
            for s in (val or []):
                c = (s or {}).get("cron")
                if c:
                    crons.append(cron_to_cn(c))
        elif k == "workflow_dispatch":
            events.append("手动")
        elif k == "push":
            br = (val or {}).get("branches") if isinstance(val, dict) else None
            events.append(f"push({','.join(br)})" if br else "push")
        elif k == "pull_request":
            events.append("PR")
        elif k == "issues":
            events.append("Issue 事件")
        else:
            events.append(k)
    return crons, events


LOOP_STAGE_PATTERNS = {
    "检测": r"probe|health|scan|fetch|triage|collect|discover",
    "动作": r"deploy|publish|commit|repair|submit|adopt",
    "验证": r"verify|validate|test|assert",
    "告警": r"notify\.py|escalate",
}


def loop_stages(text: str) -> List[str]:
    return [name for name, pat in LOOP_STAGE_PATTERNS.items()
            if re.search(pat, text, re.I)]


def referenced_scripts(text: str) -> List[str]:
    """抽取 run 里引用的本地脚本，用于标记断链。"""
    hits = set(re.findall(r"(?:python\s+(?:-m\s+)?)([\w./-]+\.py)", text))
    hits |= set(re.findall(r"(?:bash\s+)([\w./-]+\.sh)", text))
    return sorted(hits)


def state_freshness() -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not STATE_DIR.exists():
        return out
    for p in STATE_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(d, dict) and "domain" in d and "current" in d:
                out[d["domain"]] = str(d.get("updated", ""))[:19].replace("T", " ")
        except Exception:
            continue
    return out


def collect() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    files = sorted(list(WF_DIR.glob("*.yml")) + list(WF_DIR.glob("*.yaml")))
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        data: Dict[str, Any] = {}
        parse_err = ""
        if yaml is not None:
            try:
                loaded = yaml.safe_load(text)
                data = loaded if isinstance(loaded, dict) else {}
            except Exception as e:
                parse_err = str(e).split("\n")[0][:60]

        crons, events = triggers_of(data)
        jobs = list((data.get("jobs") or {}).keys())
        scripts = referenced_scripts(text)
        missing = [s for s in scripts if not (REPO_ROOT / s).exists()
                   and not s.startswith(("scanner.", "tests."))]

        rows.append({
            "file": p.name,
            "name": data.get("name") or p.stem,
            "crons": crons,
            "events": events,
            "jobs": jobs,
            "stages": loop_stages(text),
            "missing": missing,
            "parse_err": parse_err,
        })
    return rows


def render(rows: List[Dict[str, Any]]) -> str:
    fresh = state_freshness()
    scheduled = [r for r in rows if r["crons"]]
    evented = [r for r in rows if not r["crons"]]
    broken = [r for r in rows if r["parse_err"] or r["missing"]]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    L: List[str] = []
    L.append("# AIShield 自动化台账")
    L.append("")
    L.append("> **本文件由 `scripts/gen_task_registry.py` 自动生成，请勿手工编辑。**")
    L.append(f"> 生成时间：{now}")
    L.append("")
    L.append("历史教训：本台账曾手工声称「二十八项定时任务在跑」，而仓库实际只有十四个 "
             "workflow，其中 self-heal 因 YAML 语法错静默失效 48 天。台账一旦脱离现实，"
             "就会把「看起来很自动化」的幻觉喂给每一次决策。现改为从 workflow 真实内容派生。")
    L.append("")
    L.append("## 总览")
    L.append("")
    L.append("| 指标 | 数值 |")
    L.append("|------|------|")
    L.append(f"| 本仓库 workflow 总数 | {len(rows)} 个任务 |")
    L.append(f"| 其中定时驱动 | {len(scheduled)} 个 |")
    L.append(f"| 其中事件驱动 | {len(evented)} 个 |")
    L.append(f"| 存在断链/语法问题 | {len(broken)} 个 |")
    L.append("")

    L.append("## 定时任务")
    L.append("")
    L.append("| Workflow | 名称 | 调度 | Jobs | 闭环环节 |")
    L.append("|----------|------|------|------|----------|")
    for r in scheduled:
        stages = "".join(
            f"{s}✓" for s in ["检测", "动作", "验证", "告警"] if s in r["stages"]
        ) or "—"
        miss = [s for s in ["检测", "动作", "验证", "告警"] if s not in r["stages"]]
        if miss:
            stages += f" ⚠️缺{''.join(miss)}"
        L.append(f"| `{r['file']}` | {r['name']} | {' / '.join(r['crons'])} | "
                 f"{len(r['jobs'])} | {stages} |")
    L.append("")

    L.append("## 事件驱动任务")
    L.append("")
    L.append("| Workflow | 名称 | 触发 | Jobs |")
    L.append("|----------|------|------|------|")
    for r in evented:
        L.append(f"| `{r['file']}` | {r['name']} | {' / '.join(r['events']) or '—'} | "
                 f"{len(r['jobs'])} |")
    L.append("")

    if fresh:
        L.append("## 状态总线最近更新")
        L.append("")
        L.append("> 机器可读状态存于 `data/state/<域>.json`，是闭环之间唯一的通信介质。")
        L.append("")
        L.append("| 状态域 | 最近更新 |")
        L.append("|--------|----------|")
        for k in sorted(fresh):
            L.append(f"| {k} | {fresh[k] or '—'} |")
        L.append("")

    L.append("## 健康问题")
    L.append("")
    if not broken:
        L.append("当前无语法错误、无脚本断链。")
    else:
        for r in broken:
            if r["parse_err"]:
                L.append(f"- `{r['file']}`：YAML 解析失败 —— {r['parse_err']}")
            for m in r["missing"]:
                L.append(f"- `{r['file']}`：引用了不存在的脚本 `{m}`")
    L.append("")

    L.append("---")
    L.append("")
    L.append("## 跨项目调度任务（外部，不计入本仓库统计）")
    L.append("")
    L.append("HealthLens / GeneTech / RoboParts / SwarmLabs / OracleMind 等项目的定时任务"
             "由 WorkBuddy 调度器管理，不在本仓库内，**其运行状态无法从这里验证**，"
             "因此不并入上方计数。需核对时请直接查询调度器。")
    L.append("")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 自动化台账生成器")
    ap.add_argument("--check", action="store_true", help="仅校验台账是否过期")
    ap.add_argument("--stdout", action="store_true", help="打印不写盘")
    args = ap.parse_args()

    if yaml is None:
        print("[warn] PyYAML 未安装，触发器解析会退化")

    rows = collect()
    content = render(rows)

    if args.stdout:
        print(content)
        return 0

    if args.check:
        old = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""

        def normalize(t: str) -> str:
            """剔除随时间/平台自然变动的部分，只比对结构性内容。

            否则每跑一次探活、状态时间戳一变，台账就"过期"，
            CI 门禁会天天误红 —— 一个天天报警的门禁等于没有门禁。
            """
            # 行尾统一：CRLF 与 LF 只差一个 CR，但会让「全文件 137 行」都算差异，
            # 把真正的 1 行语义变化淹没掉。先归一化再比。
            t = t.replace("\r\n", "\n").replace("\r", "\n")
            t = re.sub(r"> 生成时间：.*", "", t)
            # 状态总线时间戳区段随时变，不参与结构比对
            t = re.sub(r"## 状态总线最近更新.*?(?=\n## |\n---)", "", t, flags=re.S)
            return t.strip()

        if normalize(old) != normalize(content):
            print("台账已过期，与实际 workflow 不符。请运行：")
            print("  python scripts/gen_task_registry.py")
            return 1
        print("台账与实际一致")
        return 0

    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" 是刻意的：不指定时 Python 会把 \n 转成 os.linesep，
    # Windows 上是 \r\n、Linux 上是 \n。于是同一个文件在本地生成是 CRLF、
    # 在 CI(Linux) 重新生成是 LF，git diff 会显示「137 行全变」——
    # 实际语义差异可能只有 1 行，但那满屏的红绿会让人误判成整份台账重写。
    # 固定 LF 后，本地与 CI 产出完全一致。
    REGISTRY.write_text(content, encoding="utf-8", newline="\n")
    scheduled = sum(1 for r in rows if r["crons"])
    print(f"已生成 {REGISTRY.relative_to(REPO_ROOT)}")
    print(f"  workflow 总数 {len(rows)} 个 / 定时 {scheduled} 个 / "
          f"事件驱动 {len(rows) - scheduled} 个")
    broken = [r for r in rows if r["parse_err"] or r["missing"]]
    if broken:
        print(f"  发现 {len(broken)} 个存在问题的 workflow")
    return 0


if __name__ == "__main__":
    sys.exit(main())
