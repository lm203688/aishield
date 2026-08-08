#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 零凭据内容发布器 (Zero-Credential Publisher)
=====================================================
解决问题：channel-distribution 的社交发布被 token 门控挡住，
`if [ -n "$TWITTER_BEARER_TOKEN" ]` 永远为假，于是永远走 else 分支。
结果：eco/content/ 里躺着一堆博客，从未抵达任何读者 —— 这是 0 star / 0 用户的直接原因。

本模块的原则：**不依赖任何需要付费或人工申请的凭据也必须能发出去。**

零凭据发布渠道（GITHUB_TOKEN 在 Actions 内自动注入，无需任何配置）：
  1. GitHub Issue（label: blog）—— 可被搜索引擎索引，可评论，天然社区入口
  2. GitHub Pages 静态站 —— 输出到 docs/blog/，配合 Jekyll 自动成站
  3. RSS/Atom Feed —— api/static/feeds.xml，供聚合器与 Agent 抓取
  4. README 最新文章区 —— 仓库首页即流量入口
  5. GitHub Release —— 里程碑内容自动成为发布说明

可选凭据渠道（配了才走，没配不影响主流程）：
  6. Webhook 推送到飞书/企业微信群

用法：
    python scripts/publish_content.py --all
    python scripts/publish_content.py --source eco/content --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

CONTENT_DIRS = [REPO_ROOT / "eco" / "content", REPO_ROOT / "content" / "blog"]
PAGES_DIR = REPO_ROOT / "docs" / "blog"
FEED_PATH = REPO_ROOT / "api" / "static" / "feeds.xml"
LEDGER = REPO_ROOT / "data" / "state" / "published.json"

GH_OWNER = os.environ.get("GH_OWNER", "lm203688")
GH_REPO = os.environ.get("GH_REPO", "aishield")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
SITE_BASE = os.environ.get("SITE_BASE", "https://aishield.tools")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gh(method: str, path: str, payload: Optional[dict] = None) -> Optional[Any]:
    if not GH_TOKEN:
        return None
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=json.dumps(payload).encode("utf-8") if payload else None,
        method=method,
    )
    req.add_header("Authorization", f"Bearer {GH_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "aishield-publisher")
    if payload:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            b = r.read().decode("utf-8")
            return json.loads(b) if b else {}
    except urllib.error.HTTPError as e:
        print(f"[publish] GitHub API {method} {path} -> {e.code}: {e.read()[:200]}")
    except Exception as e:
        print(f"[publish] GitHub API 异常: {e}")
    return None


# --------------------------------------------------------------------------
# 内容发现与解析
# --------------------------------------------------------------------------
# 内部稿件前缀：规划稿与社交短文案不作为独立文章对外发布
INTERNAL_PREFIXES = ("content-plan", "social-", "draft-")


def discover_all() -> List[Path]:
    """返回全部可发布内容（含已发布），用于生成完整归档（Pages/RSS/README）。"""
    out: List[Path] = []
    for d in CONTENT_DIRS:
        if d.exists():
            out.extend(sorted(d.glob("*.md")))
    return [p for p in out if not p.name.startswith(INTERNAL_PREFIXES)]


def discover() -> List[Path]:
    """返回尚未发布的内容（真正的待发队列）。

    此前 discover() 返回全部内容，导致稳态下 verify 步骤把已发布内容
    误判为 '待发'（PENDING 恒 > 0 且台账零增长），触发静默空转误报。
    现改为只返回不在发布台账中的内容；稳态下返回 0，verify 不再误报。
    """
    ledger = load_ledger()
    published_ids = set(ledger.keys())
    return [p for p in discover_all() if parse_article(p)["id"] not in published_ids]


# 摘要提取时需要跳过的行：这些都不是「正文第一句」
_SKIP_PREFIX = ("#", ">", "|", "!", "*", "-", "+", "`", "<", "=", "_", "[")
_HR = re.compile(r"^\s*([-*_=])\1{2,}\s*$")          # --- *** ___ ===
_META_LINE = re.compile(r"^\s*(发布日期|标签|来源|作者|日期|Tags?|Date|Author)\s*[:：]")


def _extract_summary(text: str, limit: int = 200) -> str:
    """抽取一段真正能当摘要用的正文。

    早期实现只跳过 # > |，结果把紧跟标题的水平分隔线 `---` 当成了摘要，
    于是 RSS 每条 description 都是「---」、Pages 每页 description 也是「---」。
    对聚合器和搜索引擎而言，这等同于没有摘要 —— 内容发出去了，
    但在任何抓取方眼里都是一条空记录。
    """
    lines = text.splitlines()

    # 跳过 YAML front-matter
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i + 1:]
                break

    buf: List[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            if buf:                     # 段落结束
                break
            continue
        if _HR.match(s) or _META_LINE.match(s) or s.startswith(_SKIP_PREFIX):
            if buf:
                break
            continue
        buf.append(s)
        if sum(len(x) for x in buf) >= limit:
            break

    summary = " ".join(buf).strip()
    if len(summary) > limit:
        summary = summary[:limit].rstrip() + "…"
    return summary


def parse_article(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    title = path.stem
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        title = m.group(1).strip()
    body = text
    summary = _extract_summary(text)
    date_m = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    date = date_m.group(1) if date_m else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "id": hashlib.sha1(path.name.encode()).hexdigest()[:12],
        "file": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "slug": path.stem,
        "title": title,
        "summary": summary,
        "body": body,
        "date": date,
    }


def load_ledger() -> Dict[str, Any]:
    if LEDGER.exists():
        try:
            return json.loads(LEDGER.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_ledger(d: Dict[str, Any]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------
# 渠道 1：GitHub Issue（零凭据、可索引、可讨论）
# --------------------------------------------------------------------------
def publish_issue(a: Dict[str, Any], dry: bool = False) -> Optional[str]:
    marker = f"<!--aishield-post:{a['id']}-->"
    if dry:
        print(f"   [dry-run] 将发布 Issue: {a['title']}")
        return None
    if not GH_TOKEN:
        print("   ! 无 GITHUB_TOKEN，跳过 Issue 渠道")
        return None
    existing = _gh("GET", f"/repos/{GH_OWNER}/{GH_REPO}/issues?state=all&labels=blog&per_page=100") or []
    for i in existing:
        if marker in (i.get("body") or ""):
            print(f"   = 已发布过，跳过 (Issue #{i['number']})")
            return i.get("html_url")
    body = (
        f"{marker}\n"
        f"> 📅 {a['date']} ｜ 来源：AIShield 自动内容流水线\n\n"
        f"{a['body']}\n\n"
        f"---\n"
        f"🛡️ **AIShield** — MCP / AI Agent 安全扫描与信任基础设施\n"
        f"- 在线扫描：{SITE_BASE}\n"
        f"- 开源仓库：https://github.com/{GH_OWNER}/{GH_REPO}\n"
        f"- 欢迎在本 Issue 下讨论，或提交你希望我们扫描的 MCP 工具。"
    )
    created = _gh(
        "POST",
        f"/repos/{GH_OWNER}/{GH_REPO}/issues",
        {"title": a["title"], "body": body, "labels": ["blog", "content"]},
    )
    if created:
        url = created.get("html_url")
        print(f"   ✓ Issue 已发布 #{created.get('number')} {url}")
        return url
    return None


# --------------------------------------------------------------------------
# 渠道 2：GitHub Pages 静态站
# --------------------------------------------------------------------------
def publish_pages(articles: List[Dict[str, Any]], dry: bool = False) -> int:
    if dry:
        print(f"   [dry-run] 将写出 {len(articles)} 篇到 docs/blog/")
        return 0
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    for a in articles:
        fm = (
            "---\n"
            f"layout: default\n"
            f"title: \"{a['title'].replace(chr(34), chr(39))}\"\n"
            f"date: {a['date']}\n"
            f"description: \"{a['summary'].replace(chr(34), chr(39))[:150]}\"\n"
            "---\n\n"
        )
        (PAGES_DIR / f"{a['slug']}.md").write_text(fm + a["body"], encoding="utf-8")
        n += 1
    # 索引页
    idx = ["---", "layout: default", "title: AIShield 安全洞察", "---", "", "# AIShield 安全洞察", ""]
    idx.append("MCP / AI Agent 安全领域的持续观察，由 AIShield 自动化情报流水线产出。\n")
    for a in sorted(articles, key=lambda x: x["date"], reverse=True):
        idx.append(f"- **[{a['title']}]({a['slug']}.html)** — `{a['date']}`  \n  {a['summary'][:120]}")
    (PAGES_DIR / "index.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"   ✓ Pages 已生成 {n} 篇 + 索引页 docs/blog/index.md")
    return n


# --------------------------------------------------------------------------
# 渠道 3：RSS Feed（供 Agent / 聚合器抓取）
# --------------------------------------------------------------------------
def publish_feed(articles: List[Dict[str, Any]], dry: bool = False) -> None:
    if dry:
        print(f"   [dry-run] 将生成 RSS，共 {len(articles)} 条")
        return
    FEED_PATH.parent.mkdir(parents=True, exist_ok=True)

    def esc(s: str) -> str:
        return (
            s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    items = []
    for a in sorted(articles, key=lambda x: x["date"], reverse=True)[:30]:
        try:
            dt = datetime.strptime(a["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)
        link = f"https://{GH_OWNER}.github.io/{GH_REPO}/blog/{a['slug']}.html"
        items.append(
            "    <item>\n"
            f"      <title>{esc(a['title'])}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid isPermaLink=\"false\">aishield-{a['id']}</guid>\n"
            f"      <pubDate>{format_datetime(dt)}</pubDate>\n"
            f"      <description>{esc(a['summary'])}</description>\n"
            "    </item>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n  <channel>\n'
        "    <title>AIShield 安全洞察</title>\n"
        f"    <link>{SITE_BASE}</link>\n"
        "    <description>MCP / AI Agent 安全扫描与威胁情报</description>\n"
        "    <language>zh-CN</language>\n"
        f"    <lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )
    FEED_PATH.write_text(xml, encoding="utf-8")
    print(f"   ✓ RSS 已生成 {FEED_PATH.relative_to(REPO_ROOT)}（{len(items)} 条）")


# --------------------------------------------------------------------------
# 渠道 4：README 最新文章区
# --------------------------------------------------------------------------
def update_readme(articles: List[Dict[str, Any]], dry: bool = False) -> None:
    readme = REPO_ROOT / "README.md"
    if not readme.exists() or dry:
        if dry:
            print("   [dry-run] 将更新 README 最新文章区")
        return
    text = readme.read_text(encoding="utf-8")
    start, end = "<!--LATEST_POSTS_START-->", "<!--LATEST_POSTS_END-->"
    lines = ["", "### 📰 最新安全洞察", ""]
    for a in sorted(articles, key=lambda x: x["date"], reverse=True)[:5]:
        link = f"https://{GH_OWNER}.github.io/{GH_REPO}/blog/{a['slug']}.html"
        lines.append(f"- [{a['title']}]({link}) `{a['date']}`")
    lines.append("")
    block = start + "\n" + "\n".join(lines) + "\n" + end
    if start in text and end in text:
        text = re.sub(re.escape(start) + r".*?" + re.escape(end), block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    readme.write_text(text, encoding="utf-8")
    print("   ✓ README 最新文章区已更新")


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 零凭据内容发布器")
    ap.add_argument("--all", action="store_true", help="发布全部渠道")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    all_articles = [parse_article(p) for p in discover_all()]
    pending_articles = [parse_article(p) for p in discover()]
    if not all_articles:
        print("未发现任何可发布内容")
        return 0

    print(f"内容库共 {len(all_articles)} 篇，其中待发布 {len(pending_articles)} 篇：")
    for a in pending_articles:
        print(f"  - {a['title']}  ({a['file']})")
    if not pending_articles:
        print("  （本轮无新增待发布内容，仅刷新归档渠道 Pages/RSS/README）")

    ledger = load_ledger()
    print("\n渠道 1/4 GitHub Issue（可索引社区入口）")
    for a in pending_articles:
        url = publish_issue(a, args.dry_run)
        if url:
            ledger[a["id"]] = {"title": a["title"], "issue": url, "at": _now()}

    print("\n渠道 2/4 GitHub Pages 静态站")
    publish_pages(all_articles, args.dry_run)

    print("\n渠道 3/4 RSS Feed")
    publish_feed(all_articles, args.dry_run)

    print("\n渠道 4/4 README 首页导流")
    update_readme(all_articles, args.dry_run)

    if not args.dry_run:
        save_ledger(ledger)
        try:
            from scripts.state_bus import StateBus

            StateBus().set(
                "distribution",
                {
                    "articles": len(articles),
                    "published_issues": len(ledger),
                    "channels": ["github-issue", "pages", "rss", "readme"],
                    "last_run": _now(),
                },
                source="publish_content",
            )
        except Exception as e:
            print(f"[warn] 状态回写失败: {e}")

    print(f"\n完成：{len(articles)} 篇内容已进入 4 个零凭据分发渠道。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
