#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 反馈聚合与迭代采纳 (Feedback Aggregator)
=================================================
评估报告指出 feature-closed-loop 的两个致命缺陷：
  1. **唯一输入源是 GitHub Issue，而仓库 0 个 issue** —— 闭环没有输入，空转。
  2. **update-roadmap 只 echo 追加一行标题，从不 commit** —— 采纳环节是假动作。

自动化闭环若只依赖"用户主动提反馈"，在冷启动期必然空转。
本模块把输入源从 1 路扩展到 4 路，其中 3 路是系统自己产生的客观事实，
不依赖任何外部用户行为 —— 这样即使 0 用户，迭代闭环依然有真实输入。

四路输入：
  S1 用户反馈   —— GitHub Issue（有用户时的主输入）
  S2 生态位待办 —— registry_tracker 探测到的未上架生态位（直接阻塞变现）
  S3 体系问题   —— meta_monitor 发现的自动化体系缺陷
  S4 情报驱动   —— 高危漏洞对应的检测能力缺口

输出：真实写入 ROADMAP.md + 为 P0/P1 项创建可跟踪 Issue + 状态回写

用法：
    python scripts/feedback_aggregator.py --adopt
    python scripts/feedback_aggregator.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ROADMAP = REPO_ROOT / "ROADMAP.md"
STATE_DIR = REPO_ROOT / "data" / "state"

GH_OWNER = os.environ.get("GH_OWNER", "lm203688")
GH_REPO = os.environ.get("GH_REPO", "aishield")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""

MARKER_START = "<!--AUTO_ADOPTED_START-->"
MARKER_END = "<!--AUTO_ADOPTED_END-->"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gh(method: str, path: str, payload: dict | None = None):
    if not GH_TOKEN:
        return None
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=json.dumps(payload).encode("utf-8") if payload else None,
        method=method,
    )
    req.add_header("Authorization", f"Bearer {GH_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "aishield-feedback")
    if payload:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            b = r.read().decode("utf-8")
            return json.loads(b) if b else {}
    except Exception as e:
        print(f"[feedback] API {method} {path}: {e}")
        return None


def _read_state(domain: str) -> Dict[str, Any]:
    p = STATE_DIR / f"{domain}.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("current") or {}
    except Exception:
        return {}


# --------------------------------------------------------------------------
# S1 用户反馈
# --------------------------------------------------------------------------
def source_user_issues() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    issues = _gh("GET", f"/repos/{GH_OWNER}/{GH_REPO}/issues?state=open&per_page=50") or []
    for i in issues:
        if i.get("pull_request"):
            continue
        labels = [l["name"] for l in i.get("labels", [])]
        # 自动告警类 Issue 不算用户需求，避免自我循环
        if "auto-alert" in labels or "blog" in labels:
            continue
        text = (i.get("title") or "") + (i.get("body") or "")
        if any(l in labels for l in ("enhancement", "feature", "bug")) or re.search(
            r"需求|建议|feature|enhancement|bug|支持", text, re.I
        ):
            items.append({
                "source": "S1 用户反馈",
                "title": i.get("title", "")[:150],
                "priority": "P1" if "bug" in labels else "P2",
                "ref": i.get("html_url", ""),
                "key": f"issue-{i.get('number')}",
            })
    return items


# --------------------------------------------------------------------------
# S2 生态位待办
# --------------------------------------------------------------------------
def source_registry_todos() -> List[Dict[str, Any]]:
    st = _read_state("registry")
    out = []
    for t in st.get("todos") or []:
        out.append({
            "source": "S2 生态位待办",
            "title": f"{t.get('niche')}：{t.get('action')}",
            "priority": t.get("priority", "P2"),
            "ref": "",
            "key": "registry-" + re.sub(r"\W+", "-", (t.get("niche") or ""))[:40].lower(),
        })
    return out


# --------------------------------------------------------------------------
# S3 体系问题
# --------------------------------------------------------------------------
def source_meta_problems() -> List[Dict[str, Any]]:
    st = _read_state("meta")
    out = []
    for p in st.get("problems") or []:
        code = p.split(":")[0].strip()
        out.append({
            "source": "S3 体系问题",
            "title": f"修复自动化体系缺陷 — {p[:140]}",
            "priority": "P1",
            "ref": "",
            "key": "meta-" + re.sub(r"\W+", "-", code)[:30].lower(),
        })
    return out


# --------------------------------------------------------------------------
# S4 情报驱动的能力缺口
# --------------------------------------------------------------------------
def source_intel_gaps() -> List[Dict[str, Any]]:
    st = _read_state("intel")
    rules_st = _read_state("rules")
    out = []
    high_new = int(st.get("high_new") or 0)
    if high_new > 0:
        out.append({
            "source": "S4 情报驱动",
            "title": f"评审本轮 {high_new} 条新增高危漏洞的检测覆盖情况",
            "priority": "P1",
            "ref": "",
            "key": "intel-high-review",
        })
    dist = rules_st.get("owasp_distribution") or {}
    all_cats = [f"LLM{i:02d}" for i in range(1, 11)]
    missing = [c for c in all_cats if c not in dist]
    if missing:
        out.append({
            "source": "S4 情报驱动",
            "title": f"补齐 OWASP LLM Top10 未覆盖类别的检测规则：{', '.join(missing)}",
            "priority": "P2",
            "ref": "",
            "key": "owasp-gap",
        })
    return out


# --------------------------------------------------------------------------
def adopt_to_roadmap(items: List[Dict[str, Any]], dry: bool = False) -> int:
    if not ROADMAP.exists():
        print("ROADMAP.md 不存在，跳过采纳")
        return 0
    text = ROADMAP.read_text(encoding="utf-8")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        MARKER_START,
        "",
        "## 自动采纳项（迭代闭环产出）",
        "",
        f"> 由 feedback_aggregator 于 {today} 自动聚合四路输入生成，"
        f"每轮覆盖更新。勾选即视为已处理。",
        "",
        "| 优先级 | 来源 | 事项 | 参考 |",
        "|--------|------|------|------|",
    ]
    order = {"P0": 0, "P1": 1, "P2": 2}
    for it in sorted(items, key=lambda x: order.get(x["priority"], 9)):
        ref = f"[链接]({it['ref']})" if it.get("ref") else "—"
        title = it["title"].replace("|", "\\|")
        lines.append(f"| {it['priority']} | {it['source']} | {title} | {ref} |")
    lines += ["", MARKER_END]
    block = "\n".join(lines)

    if MARKER_START in text and MARKER_END in text:
        new_text = re.sub(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), block, text, flags=re.S
        )
    else:
        new_text = text.rstrip() + "\n\n" + block + "\n"

    if dry:
        print(f"   [dry-run] 将写入 ROADMAP.md，共 {len(items)} 项")
        return len(items)
    if new_text != text:
        ROADMAP.write_text(new_text, encoding="utf-8")
        print(f"   ✓ ROADMAP.md 已更新，采纳 {len(items)} 项（真实写入，非空转）")
    else:
        print("   = ROADMAP.md 无变化")
    return len(items)


def create_tracking_issues(items: List[Dict[str, Any]], dry: bool = False) -> int:
    """为 P0/P1 项创建可跟踪 Issue，使迭代项有明确归属与状态。"""
    high = [i for i in items if i["priority"] in ("P0", "P1") and not i.get("ref")]
    if not high:
        return 0
    if dry:
        print(f"   [dry-run] 将为 {len(high)} 个 P0/P1 项创建跟踪 Issue")
        return len(high)
    if not GH_TOKEN:
        print("   ! 无 GITHUB_TOKEN，跳过 Issue 创建")
        return 0

    existing = _gh("GET", f"/repos/{GH_OWNER}/{GH_REPO}/issues?state=all&labels=auto-adopted&per_page=100") or []
    created = 0
    for it in high:
        marker = f"<!--adopt-key:{it['key']}-->"
        if any(marker in (e.get("body") or "") for e in existing):
            continue
        body = (
            f"{marker}\n"
            f"**来源：** {it['source']}\n"
            f"**优先级：** {it['priority']}\n"
            f"**采纳时间：** `{_now()}`\n\n"
            f"{it['title']}\n\n"
            f"---\n> 由迭代闭环自动采纳。完成后关闭本 Issue 即可，下轮不会重复创建。"
        )
        r = _gh("POST", f"/repos/{GH_OWNER}/{GH_REPO}/issues", {
            "title": f"[{it['priority']}] {it['title'][:120]}",
            "body": body,
            "labels": ["auto-adopted", "enhancement"],
        })
        if r:
            created += 1
            print(f"   ✓ 已创建跟踪 Issue #{r.get('number')}: {it['title'][:60]}")
    return created


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 反馈聚合与迭代采纳")
    ap.add_argument("--adopt", action="store_true", help="真实写入 ROADMAP 并创建 Issue")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run or not args.adopt

    print("聚合四路反馈输入\n" + "=" * 60)
    sources = [
        ("S1 用户反馈", source_user_issues),
        ("S2 生态位待办", source_registry_todos),
        ("S3 体系问题", source_meta_problems),
        ("S4 情报驱动", source_intel_gaps),
    ]
    items: List[Dict[str, Any]] = []
    for label, fn in sources:
        try:
            got = fn()
        except Exception as e:
            print(f"  {label}: 异常 {e}")
            got = []
        print(f"  {label}: {len(got)} 项")
        items.extend(got)

    # 去重
    seen = set()
    uniq = []
    for it in items:
        if it["key"] in seen:
            continue
        seen.add(it["key"])
        uniq.append(it)

    print("=" * 60)
    print(f"聚合后共 {len(uniq)} 项待办：")
    order = {"P0": 0, "P1": 1, "P2": 2}
    for it in sorted(uniq, key=lambda x: order.get(x["priority"], 9)):
        print(f"  [{it['priority']}] ({it['source']}) {it['title'][:80]}")

    if not uniq:
        print("\n无待办事项 —— 但请注意：0 输入本身可能意味着上游探测环节失效。")

    print("\n采纳到 ROADMAP：")
    adopt_to_roadmap(uniq, dry)
    print("\n创建跟踪 Issue：")
    n_issues = create_tracking_issues(uniq, dry)

    try:
        from scripts.state_bus import StateBus

        StateBus().set(
            "feature",
            {
                "adopted": len(uniq),
                "issues_created": n_issues,
                "by_source": {lbl: len([i for i in uniq if i["source"] == lbl])
                              for lbl, _ in sources},
                "p1_count": len([i for i in uniq if i["priority"] in ("P0", "P1")]),
                "last_run": _now(),
            },
            source="feedback_aggregator",
        )
    except Exception as e:
        print(f"[warn] 状态回写失败: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
