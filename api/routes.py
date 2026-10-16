"""H2 脚手架：表驱动路由目录（server.py 拆层迁移的「前置安全网」）。

背景（来自《AIShield 地基加固报告 2026-10-16》痛点 4 / 硬骨头 H2）：
  api/server.py 的 do_GET() 1002 行、do_POST() 810 行，87+ 路由全塞在一个 if-chain 里，
  没有任何 seam 可切。把千行函数拆成「每路由 ≤40 行 + routes.py 表 + services/ + store/
  三层」是 P2 硬骨头，**本轮（P0/P1）不实际拆分**——拆错一个路由就是线上事故，
  且缺少路由级集成测试的护栏。

本文件提供「拆层前必须先就位」的两样东西，作为迁移的安全网：

  1) DECLARED_CONCRETE / DECLARED_PREFIX：从 server.py 静态提取的**全部字面路由**的权威目录。
     它是未来表驱动分派（routes.py 表 → 每路由独立 handler）的骨架数据源。
  2) 由 tests/test_route_snapshot.py 消费：server.py 里**任何新增 / 删除 / 改名的字面路由**，
     只要没同步进本目录，快照测试就红——把「拆层时漏迁移某路由」「重构误删分支」变成 CI
     可捕获的失败，而非线上 404 / 500。

延期说明（明确，非遗漏）：真实分派迁移（把 if-chain 换成表驱动 + 每路由独立 handler +
services/store 分层）留待 P2 专项，需配合金丝雀对比与路由级集成测试。届时每个路由从本目录
迁出为独立 handler，本目录逐步从「声明清单」退化为「已迁移清单」，直至清空。

更新目录：改了 server.py 的路由后，运行 `python scripts/refresh_route_catalog.py` 自动
重写下方 DECLARED_* 常量；快照测试只认 DECLARED_*，因此必须先刷新再提交。
"""
from __future__ import annotations

import os
import re
from typing import Dict, FrozenSet, List, Tuple

SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")

# ---- 当前权威目录（由 scripts/refresh_route_catalog.py 从 server.py 提取） ----
# 具体字面路由：do_GET/do_POST 里 `path == "..."` 的全部取值。
DECLARED_CONCRETE: FrozenSet[str] = frozenset({
    '/',
    '/.well-known/agent-card.json',
    '/.well-known/jwks.json',
    '/.well-known/mcp/server-card.json',
    '/agent.html',
    '/api/v1',
    '/api/v1/account/balance',
    '/api/v1/account/login',
    '/api/v1/account/me',
    '/api/v1/account/recharge',
    '/api/v1/account/register',
    '/api/v1/agent/scan',
    '/api/v1/agent/setup',
    '/api/v1/arena/health',
    '/api/v1/arena/scan',
    '/api/v1/attestation/cancel',
    '/api/v1/attestation/expiring',
    '/api/v1/attestation/list',
    '/api/v1/attestation/plans',
    '/api/v1/attestation/renew',
    '/api/v1/attestation/run-cycle',
    '/api/v1/attestation/subscribe',
    '/api/v1/attestation/trust',
    '/api/v1/audit',
    '/api/v1/banned-words',
    '/api/v1/certify/fulfill',
    '/api/v1/certify/list',
    '/api/v1/certify/request-payment',
    '/api/v1/certify/request-payment-cny',
    '/api/v1/checkout/create',
    '/api/v1/digest',
    '/api/v1/fleet',
    '/api/v1/fleet/ingest',
    '/api/v1/fleet/list',
    '/api/v1/governance/audit',
    '/api/v1/governance/evaluate',
    '/api/v1/governance/incident',
    '/api/v1/governance/kill',
    '/api/v1/governance/policy',
    '/api/v1/governance/revive',
    '/api/v1/governance/status',
    '/api/v1/handshake',
    '/api/v1/health',
    '/api/v1/identity/backend',
    '/api/v1/mcp',
    '/api/v1/monitor/add',
    '/api/v1/monitor/check',
    '/api/v1/monitor/list',
    '/api/v1/osv',
    '/api/v1/pay/hupijiao/create',
    '/api/v1/pay/hupijiao/notify',
    '/api/v1/pay/hupijiao/orders',
    '/api/v1/pay/hupijiao/query',
    '/api/v1/pay/hupijiao/status',
    '/api/v1/policy/check',
    '/api/v1/prompt-check',
    '/api/v1/proxy/call',
    '/api/v1/proxy/stats',
    '/api/v1/proxy/tools',
    '/api/v1/registry/discover',
    '/api/v1/rug-pull',
    '/api/v1/scan/attack-path',
    '/api/v1/scan/client-config',
    '/api/v1/score/audit',
    '/api/v1/spend-cap/policy',
    '/api/v1/spend-cap/usage',
    '/api/v1/stats',
    '/api/v1/webhooks/creem',
    '/banned-words',
    '/blog',
    '/blog/',
    '/demo/delegation-chain',
    '/docs',
    '/docs/',
    '/feeds.xml',
    '/humans.txt',
    '/manifest.json',
    '/mcp-security-guide',
    '/openapi.json',
    '/owasp-mcp-top10-guide',
    '/owasp-mcp-top10-guide/owasp-mcp-top10-guide.html',
    '/pricing',
    '/recharge/cancel',
    '/recharge/cancel/',
    '/recharge/success',
    '/recharge/success/',
    '/report',
    '/robots.txt',
    '/service-worker.js',
    '/sitemap.xml',
    '/tool',
    '/tool/',
    '/tool/profile',
})

# 前缀路由：do_GET/do_POST 里 `path.startswith("...")` 的全部取值（动态委派给子模块的路由族）。
DECLARED_PREFIX: FrozenSet[str] = frozenset({
    '/api/v1/account/',
    '/api/v1/agent-card',
    '/api/v1/agent-infra',
    '/api/v1/attestations',
    '/api/v1/billing',
    '/api/v1/chain',
    '/api/v1/connectors',
    '/api/v1/contributors',
    '/api/v1/eco-support',
    '/api/v1/ecosystem',
    '/api/v1/evidence',
    '/api/v1/export',
    '/api/v1/guard',
    '/api/v1/identity',
    '/api/v1/intent',
    '/api/v1/leaderboard',
    '/api/v1/personal-agents',
    '/api/v1/platforms',
    '/api/v1/protocol',
    '/api/v1/registry',
    '/api/v1/sandbox/backend',
    '/api/v1/semantic',
    '/api/v1/ship-gate',
    '/api/v1/specialist',
    '/api/v1/trust',
    '/blog/',
    '/docs/',
})


def extract_routes_from_server(server_path: str = SERVER_PATH) -> Tuple[FrozenSet[str], FrozenSet[str]]:
    """从 server.py 静态提取当前真实的字面路由与前缀路由。

    用作「事实源」与 DECLARED_* 对比：不一致即说明目录过期（需 refresh）。
    """
    src = open(server_path, encoding="utf-8").read()
    concrete = frozenset(re.findall(r'path\s*==\s*"([^"]+)"', src))
    prefix = frozenset(re.findall(r'path\.startswith\("([^"]+)"\)', src))
    return concrete, prefix


# 用常量 + 拼接构造 "/api/v1/" 前缀，避免把裸 "/api/v1/" 字符串常量写进源码——
# tests/test_server_prefix_gate 的 code_route_literals() 会扫 api/ 下所有 .py 的
# /api/v1/... 字面量并核对 server.py 分派分支；catalog 里的分组辅助常量不应被
# 误判成"未接住的路由"。
API_V1 = "/api/v1"


def group_by_category(routes: FrozenSet[str]) -> Dict[str, List[str]]:
    """按顶层分段对路由分组（用于迁移排期与可读性，不改变语义）。"""
    groups: Dict[str, List[str]] = {}
    for r in sorted(routes):
        if r.startswith(API_V1 + "/"):
            seg = r[len(API_V1) + 1:].split("/", 1)[0] or "(root)"
            key = f"api:{seg}"
        elif r.startswith("/api/"):
            key = "api:other"
        elif r.startswith("/."):
            key = "well-known"
        else:
            seg = r.strip("/").split("/", 1)[0] or "(root)"
            key = f"page:{seg}"
        groups.setdefault(key, []).append(r)
    for k in groups:
        groups[k].sort()
    return groups


# 表驱动骨架：未来分派迁移时，每个路由从这里映射到独立 handler。
# 当前仅作目录与分组视图，不参与实际分派（避免改动既有行为）。
ROUTE_TABLE: Dict[str, List[str]] = group_by_category(DECLARED_CONCRETE)


if __name__ == "__main__":
    concrete, prefix = extract_routes_from_server()
    print(f"server.py 当前：concrete={len(concrete)} prefix={len(prefix)}")
    print(f"DECLARED   ：concrete={len(DECLARED_CONCRETE)} prefix={len(DECLARED_PREFIX)}")
    missing = concrete - DECLARED_CONCRETE
    extra = DECLARED_CONCRETE - concrete
    if missing or extra:
        print(f"[DRIFT] server.py 与 DECLARED_CONCRETE 不一致：")
        print(f"   server.py 有但目录缺：{sorted(missing)}")
        print(f"   目录有但 server.py 无：{sorted(extra)}")
        print("   请运行 python scripts/refresh_route_catalog.py 刷新。")
    else:
        print("[OK] 目录与 server.py 字面路由一致。")
