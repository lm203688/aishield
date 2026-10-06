#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gen_agent_api_index.py —— 从运行时契约派生「agent 照着能调通」的调用索引。

源（唯一真相源）
────────────────
``api.openapi_spec.get_openapi_spec()`` —— 它本身是 **curated + 运行时探得路由** 的
投影（当前 132 条 path）。所以本索引不需要任何手工清单，路由加一条、索引下一次
重算就带上，不存在"抄漏第 133 条"的问题。

产物
────
``docs/agent-api-index.md`` —— 线上可达：``https://aishield.tools/docs/agent-api-index.html``
（``api/server.py`` 的 ``/docs/`` 分支会把 ``.md`` 渲染成 HTML；已实测 200）。

分组按「agent 最需要」排序，而不是按字母或按模块
──────────────────────────────────────────────
外部 agent 的真实调用顺序是：先确认"我能不能被信"（身份/信任/鉴权），
再确认"这次动作合不合规"（准入/证据/意图），最后才是生态位与分发。
按字母排的索引看起来整齐，但对 agent 没用。

诚实边界（与 README 的 runner provenance 同一原则）
────────────────────────────────────────────────
**不给编出来的 schema。** 请求体在契约里没声明就照实标 `未声明`，
并把它计入文末的"缺口清单"——缺口是**可数的**，下一轮增量就是有界任务，
而不是一句"schema 待补"。宁可少给一份，也不给一份测试跑不出来的。

用法
────
    python scripts/gen_agent_api_index.py            # 重新生成索引
    python scripts/gen_agent_api_index.py --check    # CI：索引是否过期
    python scripts/gen_agent_api_index.py --json     # 机器可读（分组 + 缺口统计）
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Tuple

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BASE)

OUT_PATH = os.path.join(_BASE, "docs", "agent-api-index.md")

# 「agent 最需要」的分组表。值是路径第二段（/api/v1/<seg>/... 的 <seg>）。
GROUPS: List[Tuple[str, str, Tuple[str, ...]]] = [
    ("P0", "信任与身份（先回答“我能不能被信”）",
     ("trust", "attestations", "attestation", "identity", "agent-card", "digest", "registry")),
    ("P1", "准入与证据（这次动作合不合规）",
     ("ship-gate", "evidence", "intent", "protocol", "chain", "scan", "guard", "sandbox")),
    ("P2", "生态位与分发（让人找得到我）",
     ("ecosystem", "specialist", "leaderboard", "contributors", "connectors",
      "agent-infra", "eco-support", "billing", "pricing")),
    ("P3", "运营与自省（其余）", ()),
]

_METHOD_ORDER = ("get", "post", "put", "delete", "patch")


def _seg(path: str) -> str:
    parts = [p for p in path.strip("/").split("/") if p]
    return parts[2] if len(parts) > 2 else ""


def _group_of(path: str) -> str:
    seg = _seg(path)
    for key, _title, segs in GROUPS:
        if seg in segs:
            return key
    return "P3"


def _short_response(op: Dict[str, Any]) -> str:
    """取响应的**顶层**字段名（从 schema 里派生，不猜）。"""
    resp = (op.get("responses") or {})
    for code in ("200", "201", "202"):
        r = resp.get(code)
        if not isinstance(r, dict):
            continue
        sch = ((r.get("content") or {}).get("application/json") or {}).get("schema") or {}
        if "$ref" in sch:
            return f"$ref {sch['$ref'].split('/')[-1]}"
        props = list((sch.get("properties") or {}).keys())
        if props:
            head = ", ".join(f"`{p}`" for p in props[:6])
            more = "" if len(props) <= 6 else f" …（共 {len(props)}）"
            return head + more
        if sch.get("type"):
            return f"`{sch['type']}`"
    return "—"


def _clean_summary(raw: str) -> str:
    """去掉运行时探得的样板后缀，保留可读那一句。"""
    line = raw.strip().splitlines()[0] if raw.strip() else ""
    for junk in ("（运行时探得；schema 由真实响应推导）", "(runtime-probed)"):
        line = line.replace(junk, "")
    return line.strip()[:110]


def _observed_status(op: Dict[str, Any]) -> str:
    st = op.get("status")
    if isinstance(st, int):
        return str(st)
    for code in ("200", "201", "202", "401", "403"):
        if code in (op.get("responses") or {}):
            return code
    return "—"


def _has_body(op: Dict[str, Any]) -> bool:
    return bool(op.get("requestBody"))


def collect() -> Dict[str, Any]:
    """从契约派生索引数据。契约导入失败必须炸，不退化。"""
    from api.openapi_spec import get_openapi_spec

    spec = get_openapi_spec()
    schemas = ((spec.get("components") or {}).get("schemas") or {})
    rows: List[Dict[str, Any]] = []
    for path, item in sorted((spec.get("paths") or {}).items()):
        if not isinstance(item, dict):
            continue
        for verb in _METHOD_ORDER:
            op = item.get(verb)
            if not isinstance(op, dict):
                continue
            body_schema = ""
            rb = op.get("requestBody") or {}
            content = ((rb.get("content") or {}).get("application/json") or {})
            bsch = content.get("schema") or {}
            if "$ref" in bsch:
                body_schema = bsch["$ref"].split("/")[-1]
            elif bsch.get("properties"):
                body_schema = ", ".join(f"`{k}`" for k in list(bsch["properties"])[:8])
            rows.append({
                "group": _group_of(path),
                "method": verb.upper(),
                "path": path,
                "summary": _clean_summary(op.get("summary") or ""),
                # 没有 security 键 ≠ 不需要认证 —— 运行时探得的操作本身不带该键。
                # 缺键就照实写"未声明"，不替契约下"无需认证"的结论。
                "auth": ("需要" if op.get("security") else "无") if "security" in op else "未声明",
                "status": _observed_status(op),
                "response": _short_response(op),
                "body": body_schema or ("未声明" if not _has_body(op) else "(无字段说明)"),
                "has_body": _has_body(op),
            })
    total = len(rows)
    with_body = sum(1 for r in rows if r["has_body"])
    return {"rows": rows, "total": total, "with_body": with_body,
            "schemas": len(schemas), "openapi": spec.get("openapi", "")}


def render(data: Dict[str, Any]) -> str:
    rows: List[Dict[str, Any]] = data["rows"]
    L: List[str] = []
    A = L.append
    A("# AIShield Agent API 调用索引")
    A("")
    A("> **本文件由 `scripts/gen_agent_api_index.py` 从运行时契约自动生成，请勿手工编辑。**")
    A("> 契约本身是实现的投影（`get_openapi_spec()` = curated + 运行时探得路由），")
    A("> 因此新增一条路由，重算本文件即带上，不存在“抄漏”这一层。")
    A("")
    A("外部 agent 的正确调用顺序是：**先确认我能不能被信 → 再确认这次动作合不合规 → 最后才是生态位与分发**。")
    A("下表按这个顺序分组，不按字母、不按模块。")
    A("")
    A("## 索引健康度（每次重算实测）")
    A("")
    A("| 指标 | 值 |")
    A("|:---|:---|")
    A(f"| 契约版本 | `{data['openapi']}` |")
    A(f"| 可调用操作数 | **{data['total']}** |")
    A(f"| 已声明请求体 | {data['with_body']} |")
    A(f"| **请求体未声明** | **{data['total'] - data['with_body']}** |")
    A(f"| 组件 schema 数 | {data['schemas']} |")
    A("")
    A("`请求体未声明` 不是“参数无意义”，而是**契约还没把它写下来** —— "
      "外部 agent 只能靠猜字段名。缺口是**可数的**，见文末清单；`--check` 防止它悄悄变大。")
    A("")

    for key, title, _segs in GROUPS:
        grp = [r for r in rows if r["group"] == key]
        if not grp:
            continue
        A(f"## {key} · {title}")
        A("")
        A(f"共 {len(grp)} 条操作。")
        A("")
        A("| 方法 | 路径 | 认证 | 实测状态 | 摘要 | 响应顶层字段 | 请求体 |")
        A("|:---|:---|:---:|:---:|:---|:---|:---|")
        for r in grp:
            A(f"| `{r['method']}` | `{r['path']}` | {r['auth']} | {r['status']} | "
              f"{r['summary']} | {r['response']} | {r['body']} |")
        A("")

    A("## 缺口清单（请求体未声明，按分组）")
    A("")
    missing = [r for r in rows if not r["has_body"] and r["method"] == "POST"]
    A(f"其中 `POST` 且无请求体声明共 **{len(missing)}** 条 —— 这些是「agent 最难照着调」的部分，"
      "按 P0→P3 排，前 20 条是有界的下一轮增量：")
    A("")
    for key, title, _s in GROUPS:
        sub = [r for r in missing if r["group"] == key]
        if not sub:
            continue
        A(f"- **{key}**（{len(sub)}）：" + "、".join(f"`{r['path']}`" for r in sub[:12])
          + ("…" if len(sub) > 12 else ""))
    A("")

    A("## 复验方法（不要相信本文，相信命令）")
    A("")
    A("```bash")
    A("# 1) 索引是否与契约一致（CI 用）")
    A("python scripts/gen_agent_api_index.py --check")
    A("")
    A("# 2) 契约是否与实现一致（运行时路由双向 diff）")
    A("python scripts/openapi_contract.py --check")
    A("")
    A("# 3) 线上真实可调（挑任一条 P0 路由）")
    A("curl -s --ssl-no-revoke --tlsv1.3 -H 'User-Agent: Mozilla/5.0' \\")
    A("  https://aishield.tools/api/v1/digest | head -c 300")
    A("```")
    A("")
    A("线上索引页：<https://aishield.tools/docs/agent-api-index.html>")
    A("")
    return "\n".join(L)


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="从运行时契约派生 agent 调用索引")
    ap.add_argument("--check", action="store_true", help="校验索引是否过期（CI 用）")
    ap.add_argument("--json", action="store_true", help="打印 JSON，不落盘")
    args = ap.parse_args(argv)

    data = collect()
    if args.json:
        print(json.dumps({k: v for k, v in data.items() if k != "rows"},
                         ensure_ascii=False, indent=2))
        return 0

    text = render(data)
    if args.check:
        if not os.path.exists(OUT_PATH):
            print(f"❌ 索引不存在：{OUT_PATH}")
            print("修复：python scripts/gen_agent_api_index.py")
            return 1
        cur = open(OUT_PATH, encoding="utf-8").read()
        if cur != text:
            print("❌ docs/agent-api-index.md 与契约不一致（索引已过期）")
            print("修复：python scripts/gen_agent_api_index.py")
            return 1
        print(f"✅ 索引与契约一致（{data['total']} 条操作 / 请求体未声明 {data['total'] - data['with_body']} 条）")
        return 0

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"✅ 已生成 {os.path.relpath(OUT_PATH, _BASE)}"
          f"（{data['total']} 条操作，请求体未声明 {data['total'] - data['with_body']} 条）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
