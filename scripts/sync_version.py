#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本一致性同步器
================

背景
----
项目在 11 个配置位置各自声明版本号，实测曾漂移出 3 个不同的值：

    mcp-server/package.json   4.1.0   ← npm 实际发布的版本
    mcp-server/mcp.json       4.2.0   ← 有人升了这里，忘了其它
    registry/coze_plugin.json 4.0.0   ← 更早的遗留
    registry/dify_openapi.yaml 4.1.0
    registry/dify_plugin.yaml  4.1.0
    setup.py                   4.1.0

除配置外，还有一类**公开面自报版本**同样会漂移，且长期逃过门禁：
`api/static/*.html` 的 `softwareVersion`、`humans.txt`、`smithery.yaml`。
2026-09-15 规则数 sweep 时发现它们停在 4.2.2 而 npm 已是 4.3.0，
故一并纳入 TARGETS。凡"用户能读到的版本声明"都应受门禁约束。

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
    # API 层自报版本的**唯一声明位**。此前本文件散落 7 处独立字面量（/health、
    # /api/v1 根、三处 powered_by 水印、MCP-over-HTTP initialize 的 serverInfo、
    # server-card fallback），各自漂移——2026-09-25 实测同一进程 /health 报
    # "4.3.0" 而 mcp.json 已是 "4.8.3"，用户按 /health 查文档永远查旧版。
    # 已收敛为单一常量，故锚点由「匹配某个字面量」改为「匹配常量定义」。
    # 注意：不要改回锚定字面量的写法——那是漂移的根源。
    ("api/server.py",
     r'(API_VERSION\s*=\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # 扫描器对外自报版本：用户可读到的扫描版本声明，必须与全仓库版本一致。
    # 此前漏登记 → sync_version 对它失明，test_version_declare 钉为门禁缺口。
    ("scanner/engine.py",
     r'(SCANNER_VERSION\s*=\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # SARIF / SBOM 产物里对外自报的工具版本。会直接进入用户的 CI 产物，
    # 却从未在门禁内——曾长期停在 4.3.0 而 npm 已 4.8.3。
    ("scanner/sbom.py",
     r'(TOOL_VERSION\s*=\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # 仓库根目录的 SARIF 样例。必须锚定在 driver.name 之后，否则会先命中
    # 文件第 3 行的 SARIF 规范版本 "2.1.0"——那是 schema 决定的，不是产品版本。
    ("aishield.sarif",
     r'("name": "AIShield",\r?\n\s+"version": ")([^"]+)(")',
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
    # MCP Registry 提交清单：顶层 version。
    # 该文件曾有 10 个声明位被门禁覆盖，server.json 是第 11 个却漏在外面，
    # 于是它停在 4.2.2 而其余全是 4.3.0 —— validate_registry 每次都报
    # "npm 版本不一致"，把 ci.yml 的 workflow-lint 永久打成红灯。
    # 两个 version 字段必须用各自锚定的正则，count=1 只会替换首个命中。
    ("registry/server.json",
     r'("description": "[^"]+",\r?\n\s+"version": ")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("registry/server.json",
     r'("identifier": "aishield-mcp-server",\r?\n\s+"version": ")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # 2026-09-19：第 12 个声明位。`mcp-server/server.json` 是 npm 包 files 清单里
    # 会被**真实发布出去**的 MCP Registry 清单，但它并不在门禁内 —— 于是 registry/
    # 那份跟着升到 4.3.0，mcp-server/ 这份停在 4.2.2 无人察觉。用户解包看清单
    # 得到的是一个和包本身不符的版本号。同一个坑，换了个文件名又来一次。
    ("mcp-server/server.json",
     r'("description": "[^"]+",\r?\n\s+"version": ")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("mcp-server/server.json",
     r'("identifier": "aishield-mcp-server",\r?\n\s+"version": ")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # 公开静态面 / 生态清单自报版本 —— 此前不在门禁内，于是长期停在 4.2.2
    # 而 npm / registry 已是 4.3.0（2026-09-15 规则数 sweep 时才发现）。
    # 每个声明位锚点不同，同一文件多处需各自一条（count=1 只替换首个命中）。
    # 注意：只登记「仓库内真实存在」的文件。`aishield_home.html` 是根目录下一份
    # 未被引用的重复副本、不在仓库中——登记它会让 CI 因「文件不存在」而误判版本
    # 不一致（2026-09-15 实测：本地有、CI 无 → 本地绿而 CI 红）。
    ("api/static/index.html",
     r'("softwareVersion": ")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("api/static/index.html",
     r'(aishield-mcp-server@)([0-9.]+)',
     r"\g<1>{v}"),
    ("api/static/index.html",
     r'(<span>AIShield v)([0-9.]+)',
     r"\g<1>{v}"),
    ("api/static/agent.html",
     r'("softwareVersion": ")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("api/static/agent.html",
     r'(AIShield v)([0-9.]+)',
     r"\g<1>{v}"),
    ("api/static/mcp-security-guide.html",
     r'(AIShield v)([0-9.]+)',
     r"\g<1>{v}"),
    ("api/static/humans.txt",
     r'(Version:\s*)([0-9.]+)',
     r"\g<1>{v}"),
    # Agent 发现资产里的服务版本声明（2026-09-15 从 13 站知识库生态移植进来时
    # 一并纳入门禁）。`schema_version` 是 schema 版本号、不是产品版本，
    # 所以锚定用 `"version"` / `"service_version"` 精确匹配，不会误伤
    # `"schema_version": "1.0"` / `"schema_version": "v1"`。
    ("api/static/.well-known/ai-plugin.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("api/static/agent-discovery.json",
     r'("service_version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("api/static/.well-known/agent.json",
     r'("service_version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # Agent Card 与 MCP Server Card：A2A / MCP 客户端在握手时直接读取的自报版本，
    # 属于最靠前的对外面。此前两份文件完全不在门禁内，一直停在 4.3.0 而
    # mcp.json 已 4.8.3——线上 aishield.tools 报的就是这个错版本号。
    # 正则必须带前导引号锚定 `"version"`：否则 `protocol_version` /
    # `mcp_protocol_version` / `owasp_version` 都会被误判为产品版本。
    ("api/static/.well-known/agent-card.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("api/static/.well-known/mcp/server-card.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # ⚠ 关键区分：`/.well-known/agent-card.json` 这个线上端点实际由
    # api/trust_api.py 的 agent_card() 读 **docs/** 下的那份返回，
    # api/static/ 那份是死代码（server.py:410 的 trust_api 分支先命中）。
    # 2026-09-25 线上 curl 实测：docs 那份停在 4.3.0——A2A 发现协议里
    # AI agent 读到的就是错版本号。两份都得登记，别只修死的那份。
    ("docs/.well-known/agent-card.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("docs/.well-known/mcp/server-card.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # llms-full.txt 是给 LLM 读的全文索引，AI agent 会直接抓。
    # 锚定在 *Canonical* 那一行，避免误伤正文里出现的其它版本号。
    ("api/static/llms-full.txt",
     r'(?m)^(\*Canonical:.*?Version:\s*)(\d+\.\d+\.\d+)',
     r"\g<1>{v}"),
    # Anthropic 插件分发包：plugin.json 是插件市场读到的版本，
    # SKILL.md frontmatter 里的 version 是技能清单版本，两者必须一致。
    ("distribution/aishield-plugins/.claude-plugin/plugin.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # 插件市场提交表单的现成值，与 plugin.json 必须一致。
    ("distribution/aishield-plugins/FORM_VALUES.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # 各分发渠道的技能清单 / 插件包。这些是独立上架的产物，
    # 2026-09-25 实测分别停在 4.1.0 / 4.2.2 / 4.3.0 三个不同版本。
    ("registry/SKILL.md",
     r'(?m)^(\s*version:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("distribution/clawhub/SKILL.md",
     r'(?m)^(\s*version:\s*)(\d+\.\d+\.\d+)(\s*)',
     r"\g<1>{v}\g<3>"),
    ("distribution/deepseek-harness/dsh-plugin/package.json",
     r'("version"\s*:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("docs/llms-full.txt",
     r'(?m)^(\*Canonical:.*?Version:\s*)(\d+\.\d+\.\d+)',
     r"\g<1>{v}"),
    # 项目自身 SBOM 的应用组件版本。SBOM 里其余组件是内部源文件，
    # 版本号由 scripts/gen_project_sbom.py 从 setup.py 派生后统一盖章，
    # 所以只锚定 application 组件那一个声明位即可。
    ("docs/project-sbom.cyclonedx.json",
     r'("name": "aishield",\r?\n\s+"version": ")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    ("distribution/aishield-plugins/skills/aishield-security-scan/SKILL.md",
     r'(?m)^(\s*version:\s*")([^"]+)(")',
     r"\g<1>{v}\g<3>"),
    # README 里用户直接复制的安装命令，写死旧版本会误导升级路径。
    ("mcp-server/README.md",
     r'(aishield-mcp-server@)(\d+\.\d+\.\d+)',
     r"\g<1>{v}"),
    ("smithery.yaml",
     r'(\nversion:\s*")([^"]+)(")',
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
