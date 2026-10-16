"""H2 脚手架配套：刷新 api/routes.py 的 DECLARED_* 常量。

当 server.py 的路由（do_GET/do_POST 里的 `path == "..."` / `path.startswith("...")`）
新增 / 删除 / 改名后，先跑本脚本重写 api/routes.py 的 DECLARED_CONCRETE /
DECLARED_PREFIX，再提交。tests/test_route_snapshot.py 只认 DECLARED_*，
因此必须先刷新再提交，否则快照测试红。

运行：python scripts/refresh_route_catalog.py
标准库 only。
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "api", "server.py")
ROUTES = os.path.join(ROOT, "api", "routes.py")


def main() -> int:
    src = open(SERVER, encoding="utf-8").read()
    concrete = sorted(set(re.findall(r'path\s*==\s*"([^"]+)"', src)))
    prefix = sorted(set(re.findall(r'path\.startswith\("([^"]+)"\)', src)))

    routes_src = open(ROUTES, encoding="utf-8").read()

    def _fmt_block(items, indent=8):
        return ",\n".join(f'{" " * indent}{i!r}' for i in items)

    concrete_block = "frozenset({\n" + _fmt_block(concrete) + ",\n})"
    prefix_block = "frozenset({\n" + _fmt_block(prefix) + ",\n})"

    new = re.sub(
        r"DECLARED_CONCRETE: FrozenSet\[str\] = frozenset\(\{.*?\}\),",
        f"DECLARED_CONCRETE: FrozenSet[str] = {concrete_block},",
        routes_src, flags=re.S,
    )
    if new == routes_src:
        print("[FAIL] 未能替换 DECLARED_CONCRETE（routes.py 结构可能变动）。")
        return 1
    new = re.sub(
        r"DECLARED_PREFIX: FrozenSet\[str\] = frozenset\(\{.*?\}\),",
        f"DECLARED_PREFIX: FrozenSet[str] = {prefix_block},",
        new, flags=re.S,
    )
    if new == routes_src:
        print("[FAIL] 未能替换 DECLARED_PREFIX（routes.py 结构可能变动）。")
        return 1

    open(ROUTES, "w", encoding="utf-8").write(new)
    print(f"[OK] 已刷新 api/routes.py：concrete={len(concrete)} prefix={len(prefix)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
