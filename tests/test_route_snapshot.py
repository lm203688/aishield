"""H2 脚手架的路由快照测试（server.py 拆层迁移护栏）。

保证：
  1) api/routes.py 的 DECLARED_CONCRETE / DECLARED_PREFIX 与 server.py 实际字面路由
     完全一致——server.py 新增/删除/改名任一字面路由却没刷新目录，本测试红。
     这把「拆层时漏迁移某路由」「重构误删分支」变成 CI 可捕获的失败，而非线上 404。
  2) DECLARED_CONCRETE 内无重复、非空（目录确实在维护，而非空壳）。
  3) 每类路由可按 ROUTE_TABLE 分组（表驱动骨架可用）。

注意：本测试**只**钉死「字面路由集合」，不钉行为；行为由 test_openapi_contract
（server 路由 vs openapi spec 双向 diff）与 test_server_prefix_gate（前缀门禁）覆盖。
实际分派迁移（if-chain → 表驱动 + 每路由独立 handler）属于 P2 专项，延期见 api/routes.py。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api import routes as routes_mod


def test_declared_concrete_not_empty_and_unique():
    assert len(routes_mod.DECLARED_CONCRETE) > 0
    # frozenset 本身去重；这里确认数量与去重后一致（防重复录入）。
    assert len(routes_mod.DECLARED_CONCRETE) == len(set(routes_mod.DECLARED_CONCRETE))


def test_declared_matches_server_literals():
    concrete, prefix = routes_mod.extract_routes_from_server()
    missing = concrete - routes_mod.DECLARED_CONCRETE
    extra = routes_mod.DECLARED_CONCRETE - concrete
    assert not missing, (
        f"server.py 有但 api/routes.py 目录缺失的字面路由：{sorted(missing)}\n"
        f"请运行 python scripts/refresh_route_catalog.py 刷新目录后再提交。"
    )
    assert not extra, (
        f"api/routes.py 目录有但 server.py 已不存在的字面路由：{sorted(extra)}\n"
        f"这些是无主声明，请运行 refresh_route_catalog.py 清理。"
    )


def test_declared_prefix_matches_server():
    _, prefix = routes_mod.extract_routes_from_server()
    missing = prefix - routes_mod.DECLARED_PREFIX
    extra = routes_mod.DECLARED_PREFIX - prefix
    assert not missing, (
        f"server.py 新增但未登记的前缀路由：{sorted(missing)}\n"
        f"请运行 python scripts/refresh_route_catalog.py 刷新目录。"
    )
    assert not extra, (
        f"api/routes.py 目录有但 server.py 已不存在的前缀路由：{sorted(extra)}\n"
        f"请运行 refresh_route_catalog.py 清理。"
    )


def test_route_table_grouped():
    # 表驱动骨架可用：能按功能分组，且覆盖全部声明的具体路由。
    table = routes_mod.ROUTE_TABLE
    flat = [r for v in table.values() for r in v]
    assert set(flat) == routes_mod.DECLARED_CONCRETE
    # 至少应识别出 api / well-known / page 几大类。
    assert any(k.startswith("api:") for k in table)
