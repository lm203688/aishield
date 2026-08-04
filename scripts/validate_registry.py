#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 官方 Registry 提交文件校验器
================================

为什么需要它
------------
向 registry.modelcontextprotocol.io 提交 server.json 时，服务端校验失败
只会回一句笼统的 400。而这份文件有若干**不看 schema 根本猜不到**的硬约束：

  · description 上限 **100 字符** —— 项目原有描述 130+ 字，必被拒
  · name 必须是反向 DNS 且**有且仅有一个斜杠**：io.github.<owner>/<server>
  · packages[].registryType / identifier / transport 三项缺一不可
  · version 不接受范围写法（^1.2.3 会被拒）

与其提交后靠报错试错，不如提交前就地校验。

实现说明
--------
刻意不引入 jsonschema 依赖（项目有零依赖门禁），而是从官方地址拉取真实
schema，再对本项目实际用到的约束做定向校验。schema 拉不到时降级为离线
基础校验，并明确告知已降级 —— 不假装校验通过。

用法
----
    python scripts/validate_registry.py
    python scripts/validate_registry.py --check     # CI 门禁，失败退出 1
    python scripts/validate_registry.py --sync      # 版本对齐 package.json
"""
from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVER_JSON = REPO_ROOT / "registry" / "server.json"
PKG_JSON = REPO_ROOT / "mcp-server" / "package.json"

SCHEMA_URL_DEFAULT = (
    "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
)

# 离线降级时使用的基础约束（与 2025-12-11 schema 一致）
FALLBACK = {
    "required": ["name", "description", "version"],
    "name_pattern": r"^[a-zA-Z0-9.-]+/[a-zA-Z0-9._-]+$",
    "name_max": 200,
    "description_max": 100,
    "title_max": 100,
    "package_required": ["registryType", "identifier", "transport"],
    "repository_required": ["url", "source"],
}

VERSION_RANGE = re.compile(r"[\^~><=\s*x]")


def _ctx() -> ssl.SSLContext:
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c


def fetch_schema(url: str) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "aishield-registry-validator"})
        with urllib.request.urlopen(req, timeout=20, context=_ctx()) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def constraints_from_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """从真实 schema 中提取本校验器关心的约束。"""
    c = dict(FALLBACK)
    try:
        defs = schema.get("definitions") or schema.get("$defs") or {}
        sd = defs.get("ServerDetail") or {}
        props = sd.get("properties") or {}
        if sd.get("required"):
            c["required"] = sd["required"]
        if props.get("name", {}).get("pattern"):
            c["name_pattern"] = props["name"]["pattern"]
        for key, prop in (("name_max", "name"), ("description_max", "description"),
                          ("title_max", "title")):
            m = (props.get(prop) or {}).get("maxLength")
            if m:
                c[key] = m
        pk = defs.get("Package") or {}
        if pk.get("required"):
            c["package_required"] = pk["required"]
        repo = defs.get("Repository") or {}
        if repo.get("required"):
            c["repository_required"] = repo["required"]
    except Exception:
        pass
    return c


def validate(doc: Dict[str, Any], c: Dict[str, Any]) -> List[str]:
    errs: List[str] = []

    for f in c["required"]:
        if not doc.get(f):
            errs.append(f"缺少必填字段 '{f}'")

    name = doc.get("name") or ""
    if name:
        if not re.match(c["name_pattern"], name):
            errs.append(f"name '{name}' 不符合反向 DNS 格式（须形如 io.github.owner/server）")
        if name.count("/") != 1:
            errs.append(f"name '{name}' 必须有且仅有一个斜杠，当前有 {name.count('/')} 个")
        if len(name) > c["name_max"]:
            errs.append(f"name 超长 {len(name)}/{c['name_max']}")

    desc = doc.get("description") or ""
    if len(desc) > c["description_max"]:
        errs.append(
            f"description 超长 {len(desc)}/{c['description_max']} 字符 —— "
            f"这是最容易踩的一条，提交会被直接拒"
        )

    title = doc.get("title") or ""
    if title and len(title) > c["title_max"]:
        errs.append(f"title 超长 {len(title)}/{c['title_max']}")

    ver = str(doc.get("version") or "")
    if ver and VERSION_RANGE.search(ver):
        errs.append(f"version '{ver}' 含范围/通配符，registry 只接受确定版本")

    repo = doc.get("repository")
    if repo is not None:
        if not isinstance(repo, dict):
            errs.append("repository 必须是对象")
        else:
            for f in c["repository_required"]:
                if not repo.get(f):
                    errs.append(f"repository 缺少必填字段 '{f}'")

    for i, p in enumerate(doc.get("packages") or []):
        if not isinstance(p, dict):
            errs.append(f"packages[{i}] 必须是对象")
            continue
        for f in c["package_required"]:
            if not p.get(f):
                errs.append(f"packages[{i}] 缺少必填字段 '{f}'")
        tr = p.get("transport")
        if isinstance(tr, dict) and not tr.get("type"):
            errs.append(f"packages[{i}].transport 缺少 type")
        pv = str(p.get("version") or "")
        if pv and VERSION_RANGE.search(pv):
            errs.append(f"packages[{i}].version '{pv}' 含范围写法")

    for i, r in enumerate(doc.get("remotes") or []):
        if not isinstance(r, dict):
            errs.append(f"remotes[{i}] 必须是对象")
            continue
        if not r.get("type"):
            errs.append(f"remotes[{i}] 缺少 type")
        if not r.get("url"):
            errs.append(f"remotes[{i}] 缺少 url")

    return errs


def cross_check_package(doc: Dict[str, Any]) -> List[str]:
    """server.json 与 package.json 的一致性 —— 二者漂移会导致 registry 指向不存在的包。"""
    warns: List[str] = []
    try:
        pkg = json.loads(PKG_JSON.read_text(encoding="utf-8-sig"))
    except Exception:
        return ["无法读取 mcp-server/package.json，跳过一致性检查"]

    for p in doc.get("packages") or []:
        if p.get("registryType") != "npm":
            continue
        if p.get("identifier") != pkg.get("name"):
            warns.append(
                f"npm 包名不一致：server.json='{p.get('identifier')}' "
                f"vs package.json='{pkg.get('name')}'"
            )
        if p.get("version") != pkg.get("version"):
            warns.append(
                f"npm 版本不一致：server.json='{p.get('version')}' "
                f"vs package.json='{pkg.get('version')}'"
            )
    if doc.get("version") != pkg.get("version"):
        warns.append(
            f"server 版本不一致：server.json='{doc.get('version')}' "
            f"vs package.json='{pkg.get('version')}'"
        )
    return warns


def sync_from_package(doc: Dict[str, Any]) -> bool:
    """把 server.json 的版本与包名对齐到 package.json。"""
    try:
        pkg = json.loads(PKG_JSON.read_text(encoding="utf-8-sig"))
    except Exception:
        print("无法读取 package.json，同步中止")
        return False
    changed = False
    if doc.get("version") != pkg.get("version"):
        doc["version"] = pkg.get("version")
        changed = True
    for p in doc.get("packages") or []:
        if p.get("registryType") == "npm":
            if p.get("identifier") != pkg.get("name"):
                p["identifier"] = pkg.get("name")
                changed = True
            if p.get("version") != pkg.get("version"):
                p["version"] = pkg.get("version")
                changed = True
    if changed:
        SERVER_JSON.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description="MCP Registry server.json 校验器")
    ap.add_argument("--check", action="store_true", help="有错误则退出 1")
    ap.add_argument("--sync", action="store_true", help="版本/包名对齐 package.json")
    ap.add_argument("--offline", action="store_true", help="不拉取远程 schema")
    args = ap.parse_args()

    if not SERVER_JSON.exists():
        print(f"未找到 {SERVER_JSON.relative_to(REPO_ROOT)}")
        return 1

    try:
        doc = json.loads(SERVER_JSON.read_text(encoding="utf-8-sig"))
    except Exception as e:
        print(f"❌ server.json 不是合法 JSON: {e}")
        return 1

    if args.sync:
        print("已同步版本与包名" if sync_from_package(doc) else "已一致，无需同步")
        doc = json.loads(SERVER_JSON.read_text(encoding="utf-8-sig"))

    schema_url = doc.get("$schema") or SCHEMA_URL_DEFAULT
    schema = None if args.offline else fetch_schema(schema_url)
    c = constraints_from_schema(schema) if schema else dict(FALLBACK)

    print("MCP Registry 提交文件校验")
    print("=" * 62)
    print(f"文件      : registry/server.json")
    print(f"server 名 : {doc.get('name')}")
    print(f"版本      : {doc.get('version')}")
    print(f"约束来源  : {'官方 schema（已拉取）' if schema else '内置基础约束（远程不可达，已降级）'}")
    print("-" * 62)

    errs = validate(doc, c)
    warns = cross_check_package(doc)

    if errs:
        for e in errs:
            print(f"❌ {e}")
    if warns:
        for w in warns:
            print(f"⚠️  {w}")
    if not errs and not warns:
        print("✅ 全部约束通过，可提交至 MCP 官方 registry")
        print(f"   description 长度 {len(doc.get('description') or '')}/{c['description_max']}")

    print("=" * 62)
    if errs:
        print(f"{len(errs)} 个错误，提交会被拒绝")
    if args.check and (errs or warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
