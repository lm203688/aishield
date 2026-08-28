#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本一致性同步器
================

背景
----
项目在 9 个位置各自声明版本号，实测曾漂移出 3 个不同的值：

    mcp-server/package.json   4.1.0   ← npm 实际发布的版本
    mcp-server/mcp.json       4.2.0   ← 有人升了这里，忘了其它
    registry/coze_plugin.json 4.0.0   ← 更早的遗留
    registry/dify_openapi.yaml 4.1.0
    registry/dify_plugin.yaml  4.1.0
    setup.py                   4.1.0

版本漂移的危害不在于难看，而在于**下游分发渠道会各自宣称不同的版本**。
用户从 Coze 装到的是"4.0.0"，从 npm 装到的是"4.1.0"，出问题时无法定位
究竟跑的是哪份代码。

设计
----
不做"提醒人去改"，而是让一致性由机器保证：

    --check   任一处不一致就退出码 1（挂进 CI 门禁）
    --sync    全部对齐到基准版本
    --set X   显式设定版本并全量同步（发版时用）

基准版本取所有声明中的**最大 semver**，理由是：漂移通常源于
"升了一处忘了其它"，最大值即最新意图。

用法
----
    python scripts/sync_version.py            # 查看现状
    python scripts/sync_version.py --check    # CI 门禁
    python scripts/sync_version.py --sync     # 对齐
    python scripts/sync_version.py --set 4.3.0
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# 每个目标：(相对路径, 定位正则, 替换模板)
# 刻意使用锚定的精确正则，避免误伤 schema 里的 example / 无关字段。
TARGETS: List[Tuple[str, str, str]] = [
    ("mcp-server/package.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("mcp-server/mcp.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("registry/coze_plugin.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("registry/dify_openapi.yaml",
     r'(\n\s{2}version:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("registry/dify_plugin.yaml",
     r'(\nversion:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("setup.py",
     r'(version\s*=\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # 协议层自报版本：MCP 客户端握手时看到的就是这个字符串。
    # 它曾长期硬编码 '3.0.0'，而 npm 上的包已经发到 4.2.x —— 用户报障时
    # 说"我用的 3.0.0"，谁也对不上是哪份代码。这正是本脚本要消灭的漂移，
    # 只不过它藏在 TS 源码里而非配置文件，所以一直逃过了门禁。
    ("mcp-server/src/index.ts",
     r"(const SERVER_VERSION\s*=\s*')([^']+)(')",
     r"\g<1>{v}\g<3>"),
    # API 层自报版本：MCP 客户端在 negotiate 时看到的 serverInfo.version
    # 曾长期硬编码 4.2.0 而 setup.py 已到 4.2.2 —— 用户报障时版本对不上。
    ("api/server.py",
     r'("serverInfo": \{"name": "AIShield", "version": ")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # OpenAPI 规范里的 info.version
    ("api/openapi_spec.py",
     r'("title": "AIShield API",\s*\n\s*"version": ")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # dist 构建产物——每次 sync 必须同步，否则 npm 发布预检失败。
    # 见 2026-08-28 npm publish v4.3.0 preflight 因 dist 仍 4.2.2 而失败。
    ("mcp-server/dist/index.js",
     r"(const SERVER_VERSION\s*=\s*')([^']+)(')",
     r"\g<1>{v}\g<3>"),
]

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def _semver_key(v: str) -> Tuple[int, int, int]:
    m = SEMVER.match(v.strip())
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (0, 0, 0)


def read_all() -> List[Dict[str, Any]]:
    """读出每个目标当前声明的版本。"""
    out: List[Dict[str, Any]] = []
    for rel, pattern, _ in TARGETS:
        p = REPO_ROOT / rel
        item: Dict[str, Any] = {"path": rel, "exists": p.exists(), "version": None}
        if p.exists():
            # utf-8-sig：项目里部分 json 带 BOM
            text = p.read_text(encoding="utf-8-sig")
            m = re.search(pattern, text)
            item["version"] = m.group(2) if m else None
            if m is None:
                item["error"] = "未匹配到版本字段（文件结构可能已变）"
        else:
            item["error"] = "文件不存在"
        out.append(item)
    return out


def baseline(items: List[Dict[str, Any]]) -> str:
    versions = [i["version"] for i in items if i.get("version")]
    if not versions:
        return "0.0.0"
    return max(versions, key=_semver_key)


def apply_version(version: str, dry: bool = False) -> int:
    """把所有目标对齐到指定版本，返回实际改动的文件数。"""
    changed = 0
    for rel, pattern, template in TARGETS:
        p = REPO_ROOT / rel
        if not p.exists():
            print(f"   ⚠ 跳过（不存在）: {rel}")
            continue
        raw = p.read_bytes()
        has_bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        m = re.search(pattern, text)
        if not m:
            print(f"   ⚠ 跳过（未匹配）: {rel}")
            continue
        if m.group(2) == version:
            continue
        new_text = re.sub(pattern, template.format(v=version), text, count=1)
        if dry:
            print(f"   [dry-run] {rel}: {m.group(2)} → {version}")
        else:
            # 保留原有 BOM，避免把无关的编码差异混进 diff
            data = new_text.encode("utf-8")
            p.write_bytes((b"\xef\xbb\xbf" + data) if has_bom else data)
            print(f"   ✓ {rel}: {m.group(2)} → {version}")
        changed += 1
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description="版本一致性同步器")
    ap.add_argument("--check", action="store_true", help="不一致则退出码 1（CI 门禁）")
    ap.add_argument("--sync", action="store_true", help="全部对齐到基准版本")
    ap.add_argument("--set", dest="set_version", help="显式设定版本并全量同步")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    items = read_all()
    base = args.set_version or baseline(items)

    if args.json:
        print(json.dumps({"baseline": base, "targets": items},
                         ensure_ascii=False, indent=2))
        return 0

    distinct = sorted({i["version"] for i in items if i.get("version")},
                      key=_semver_key)
    broken = [i for i in items if i.get("error")]

    if args.set_version or args.sync:
        print(f"同步版本到 {base}")
        print("=" * 56)
        n = apply_version(base, dry=args.dry_run)
        print("=" * 56)
        print(f"改动 {n} 个文件" if n else "已全部一致，无需改动")
        return 0

    # 默认：报告现状
    print(f"版本一致性检查（基准 {base}）")
    print("=" * 56)
    for i in items:
        if i.get("error"):
            print(f"❌ {i['path']:<34} {i['error']}")
        elif i["version"] == base:
            print(f"✅ {i['path']:<34} {i['version']}")
        else:
            print(f"⚠️  {i['path']:<34} {i['version']}  ← 落后于 {base}")
    print("=" * 56)

    ok = len(distinct) <= 1 and not broken
    if ok:
        print(f"所有声明位一致：{base}")
    else:
        print(f"检出 {len(distinct)} 个不同版本：{', '.join(distinct)}")
        if broken:
            print(f"另有 {len(broken)} 处无法读取")
        print("修复：python scripts/sync_version.py --sync")

    if args.check and not ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
