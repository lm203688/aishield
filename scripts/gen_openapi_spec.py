#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gen_openapi_spec.py —— 把**运行时真实路由**固化成契约清单。

背景（2026-10-03 一手实测）
────────────────────────────
进程内直调 ``api.server.AIShieldHandler.do_GET/do_POST``，逐个探 ``api/**`` 里
出现过的 ``/api/v1/...`` 字面量，探到命中的（不是 404 / "unknown ... endpoint"
那类措辞）就是**这条路由真的存在**。产物写进 ``api/openapi_runtime_paths.json``。

为什么要这么绕，不是直接手写
────────────────────────────
``api/openapi_spec.py`` 是手工 curated 的 10 条清单，而路由实现散在 server.py
的 if/startswith 长链 + 5 个 handler 模块里 —— 两边从来没有强制同步。实测差距：
运行时命中 110 条，契约只写 10 条，**103 条对智能体不可发现**，而且契约里还有
3 条（identity/agents、identity/register、billing/plans）压根没实现。

再手抄一遍 103 条是表面工作：写完第二天加第 104 条又回到原点。所以这里把运行时
事实**落成可入库的清单**，由 ``get_openapi_spec()`` 与 curated 部分合并 —— 契约
从此是实现的投影，而不是与之并列、需要人手对齐的第二份真相。

schema 从哪来
────────────
不手写、不臆造：取探针拿到的**真实响应样本**反推最小 JSON Schema（深度 3 截断）。
样本塞不进去（纯文本/HTML/超限）就只记 tag + summary + 状态，标
``sample_present: false`` —— 宁可少给一份 schema，也不给一份编出来的 schema。

hermetic
────────
探针会真的打到 ``/api/v1/fleet/ingest`` 这类**写状态**端点（已经污染过一次
``data/fleet.json`` 了）。所以整轮探针包在 ``hermetic_state()`` 里，退出时逐字节
还原并**删掉探针新建的文件**；产物里带 ``state_audit``，把污染自查结果一起留痕。

!!! 一条进程只跑一遍探针 !!!
──────────────────────────
探针会改状态（fleet ingest 会塞一条成员），还原只覆盖已有文件；同进程跑第二遍
看到的是被第一遍改过的数据，命中数会从 110 漂到 123。所以 CLI 一律走 ``--json``
或写文件，需要多条命令时分开进程跑。

用法
────
  python scripts/gen_openapi_spec.py                 # 生成（写 api/openapi_runtime_paths.json）
  python scripts/gen_openapi_spec.py --check         # 校验清单是否已过期（CI 用）
  python scripts/gen_openapi_spec.py --out <path>    # 指定输出
  python scripts/gen_openapi_spec.py --json          # 机器出口（不写文件）
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

sys.path.insert(0, os.path.join(REPO, "scripts"))

import openapi_contract as oc  # noqa: E402

MANIFEST = os.path.join(REPO, "api", "openapi_runtime_paths.json")

_SENSITIVE_KEYS = ("token", "secret", "password", "api_key", "apikey",
                   "authorization", "signature", "private_key")


def _redact(node: object, depth: int = 0) -> object:
    """清掉样本里的凭据类字段。

    样本来自真实响应，签名的订单/密钥返回值一旦原样进 spec 就是**把隐私写进
    公开文档**，所以这里必须过一道，而不是"反推 schema 应该原样存样本"。
    """
    if depth > 4:
        return "…"
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            lk = str(k).lower()
            if any(s in lk for s in _SENSITIVE_KEYS) and v not in (None, "", 0, [], {}):
                out[k] = "<redacted>"
            else:
                out[k] = _redact(v, depth + 1)
        return out
    if isinstance(node, list):
        return [_redact(v, depth + 1) for v in node[:8]]
    if isinstance(node, str) and len(node) > 120:
        return node[:120] + "…"
    return node


def build_manifest(do_probe: bool = True) -> dict:
    """探一轮运行时，产出清单 dict（未落盘）。"""
    records, errors, state_audit = oc.runtime_path_records(do_probe=do_probe)

    grouped: dict = {}
    for r in records:
        g = grouped.setdefault(r["path"], {
            "path": r["path"],
            "tag": r["tag"],
            "summary": r["summary"],
            "operations": [],
        })
        # 同一路径被多个前缀命中时 tag/summary 可能不同，保留先探到的那条即可；
        # 但 operations 要收全（GET 与 POST 都得进契约）。
        sample = _redact(r["sample"])
        g["operations"].append({
            "verb": r["verb"].lower(),
            "summary": r["summary"],
            "status": r["status"],
            "sample_present": r["sample"] is not None,
            "sample_truncated": r["sample_truncated"],
            "schema": oc.schema_from_sample(sample) if sample is not None else {},
            "x-aishield-generated": True,
            "x-aishield-probe-status": r["status"],
        })

    routes = []
    for path in sorted(grouped):
        g = grouped[path]
        ops = sorted(g["operations"], key=lambda d: d["verb"])
        seen = [o["verb"] for o in ops]
        if len(ops) != len(seen):
            # 同动词重复 = 探针把同一条路由记了两遍（候选超集重复），只留一次
            uniq = {}
            for o in ops:
                uniq[o["verb"]] = o
            ops = [uniq[k] for k in sorted(uniq)]
        g["operations"] = ops
        g["operation_ids"] = [f"{o['verb']}{_camel(path)}" for o in ops]
        routes.append(g)

    return {
        "note": "运行时路由清单：进程内直调 api.server.AIShieldHandler.do_GET/do_POST 探得，"
                "与 curated 规范合并后即线上 /openapi.json。",
        "source": "runtime probe (scripts/gen_openapi_spec.py)",
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "route_count": len(routes),
        "operation_count": sum(len(r["operations"]) for r in routes),
        "probe_errors": [{"path": p, "error": e} for _k, p, e in errors][:50],
        "state_audit": state_audit,
        "routes": routes,
    }


def _camel(path: str) -> str:
    segs = [s for s in path.strip("/").split("/") if s and not s.startswith("{")]
    out = ""
    for s in segs[2:] or segs:  # 跳过 api/v1
        out += s.replace("-", "_").title().replace("_", "")
    return out or "Root"


def load_manifest() -> dict:
    if not os.path.exists(MANIFEST):
        return {}
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def manifest_routes(manifest: dict) -> set:
    out = set()
    for r in (manifest or {}).get("routes", []):
        for o in r.get("operations", []):
            out.add((o["verb"], r["path"]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="从运行时探得的真实路由生成契约清单")
    ap.add_argument("--out", default=MANIFEST, help="输出路径")
    ap.add_argument("--check", action="store_true", help="校验清单是否过期（CI 用）")
    ap.add_argument("--no-probe", action="store_true", help="跳过探针（只静态）")
    ap.add_argument("--json", action="store_true", help="打印 JSON 而不落盘")
    args = ap.parse_args()

    m = build_manifest(do_probe=not args.no_probe)

    if args.json:
        print(json.dumps(m, ensure_ascii=False, indent=2))
        return 0

    if args.check:
        old = load_manifest()
        missing = sorted(manifest_routes(m) - manifest_routes(old))
        extra = sorted(manifest_routes(old) - manifest_routes(m))
        if missing or extra or m["probe_errors"]:
            print(f"FAIL：运行时路由清单过期（缺失 {len(missing)} / 待清理 {len(extra)} 条）")
            for k in missing[:20]:
                print("   新增未登记:", k)
            for k in extra[:20]:
                print("   清单有但已不存在:", k)
            for e in m["probe_errors"][:5]:
                print("   探针异常:", e["path"], e["error"][:80])
            return 1
        print(f"OK：运行时路由清单与实现一致（{m['route_count']} 路径 / "
              f"{m['operation_count']} 操作）")
        return 0

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
    sa = m["state_audit"] or {}
    print(f"运行时路由清单已写入：{args.out}")
    print(f"  路径 {m['route_count']} / 操作 {m['operation_count']} / "
          f"探针异常 {len(m['probe_errors'])}")
    print(f"  状态自查：新建 {len(sa.get('created', []))} / "
          f"还原 {len(sa.get('restored', []))} / 失败 {len(sa.get('failed', []))}")
    for p in sa.get("created", [])[:5]:
        print("    新建:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
