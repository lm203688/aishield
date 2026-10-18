#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档断链门禁
============

问题
----
`docs/intel/index.md` 是滚动索引，条目**只加不删**（时间准确性即价值）。
但一旦某日 `tech_radar.py` 输出名与索引里的引用名不完全一致（日期格式变体
`2026-08-09-tech-radar.md` vs `2026-09-10-1803-tech-radar.md`），索引就会
静默积累断链 —— 用户/Agent 点进去是 404，而门禁从来不知道。

2026-10-17 实测：`docs/intel/index.md` 有 55 条引用，14 条断链。断链存在
半年无人发现，因为它不在任何门禁覆盖面里。

解决
----
本脚本扫 `docs/**/*.md`（跳过 `docs/blog`、`docs/eco`、`docs/intel/*.md`
—— 后者是"报告正文"，正文里的外链可能是外部 URL 而非仓库内相对路径）。

只检**仓库内相对链接**（`](./xxx.md)` / `](../xxx.md)`）。外链、锚点、
图片一律跳过。

用法
----
    python scripts/check_doc_links.py            # 报告现状
    python scripts/check_doc_links.py --check    # CI 门禁，有断链 exit 1

退出码
------
    0  无断链
    1  检出断链
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from typing import List, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 只扫这些目录下的 .md
SCAN_DIRS = ("docs",)

# 跳过这些子目录（正文类/博客类/情报正文类，不做相对链接门禁）
SKIP_DIR_PARTS = (
    "docs/blog",
    "docs/eco",
    "docs/intel",  # 情报正文本身不做断链门禁（外链多、正文引用规则不同）
    "docs/benchmark",
    "docs/competitions",
)

# 跳过这些具体文件（已知豁免）
SKIP_FILES = frozenset({
    "docs/intel/index.md",   # 由 scripts/tech_radar.py 维护，本门禁只校验内容存在
})

# 相对 md 链接：`](./foo.md)` 或 `](../foo.md)` 或 `](foo.md)`
# 排除 `](http...)` `](https...)` `](#anchor)` `](mailto...)` `](!)`
REL_MD_LINK = re.compile(r"\]\((?!\s*https?://)(?!\s*#)(?!\s*mailto:)([^)\s]+\.(?:md|markdown))\)")


def _scan_paths() -> List[str]:
    """列出所有受门禁约束的 md 文件（绝对路径）。"""
    out: List[str] = []
    for top in SCAN_DIRS:
        root = os.path.join(REPO, top)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # 剪枝：跳过 SKIP_DIR_PARTS
            rel_dir = os.path.relpath(dirpath, REPO).replace(os.sep, "/")
            if any(rel_dir.startswith(s) for s in SKIP_DIR_PARTS):
                dirnames[:] = []
                continue
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                rel = os.path.join(rel_dir, fn).replace(os.sep, "/")
                if rel in SKIP_FILES:
                    continue
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def _extract_links(abspath: str) -> List[Tuple[str, str]]:
    """提取所有相对 md 链接，返回 (源文件, 目标相对路径) 列表。"""
    with open(abspath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    src_dir = os.path.dirname(abspath)
    out: List[Tuple[str, str]] = []
    for m in REL_MD_LINK.finditer(content):
        target = m.group(1)
        # 排除锚点：`foo.md#anchor`
        if "#" in target:
            target = target.split("#", 1)[0]
        if not target:
            continue
        # 排除绝对路径
        if os.path.isabs(target) or target.startswith("//"):
            continue
        resolved = os.path.normpath(os.path.join(src_dir, target))
        rel = os.path.relpath(resolved, REPO).replace(os.sep, "/")
        out.append((os.path.relpath(abspath, REPO).replace(os.sep, "/"), rel))
    return out


def check() -> Tuple[int, List[str]]:
    """返回 (断链数, 断链详情)。"""
    files = _scan_paths()
    broken: List[str] = []
    for f in files:
        for src, target in _extract_links(f):
            if not os.path.exists(os.path.join(REPO, target)):
                broken.append(f"  {src} → {target}  (不存在)")
    return len(broken), broken


def main() -> int:
    ap = argparse.ArgumentParser(description="文档断链门禁")
    ap.add_argument("--check", action="store_true", help="CI 门禁：有断链 exit 1")
    args = ap.parse_args()

    broken_count, broken = check()

    print("=" * 60)
    print("文档断链检查")
    print("=" * 60)

    if broken_count == 0:
        print("✅ 无断链")
        print("=" * 60)
        return 0

    print(f"❌ 检出 {broken_count} 处断链：")
    for line in broken:
        print(line)
    print("=" * 60)
    if args.check:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
