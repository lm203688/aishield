#!/usr/bin/env python
"""身份注册表运维工具（2026-10-03 随身份锚点闭环新增）。

背景：``POST /api/v1/identity/register`` 曾经是裸端点，谁都能往公开注册表写一个
DID，注册完却没有任何手段把它摘掉。核线脚本一句话就留下了 ``did:aishield:xxxx``
（name=probe、owner 为空）这种**孤儿记录** —— 它既不能注销（没有归属），也不影响
任何功能，只能靠工具捞。

用法（一律先 --list 看清楚，再决定要不要动）：

    python scripts/identity_maintenance.py --list
    python scripts/identity_maintenance.py --purge-orphan      # 删 owner 为空的历史记录
    python scripts/identity_maintenance.py --purge-inactive    # 删已注销记录
    python scripts/identity_maintenance.py --purge-orphan --dry-run

安全边界：
  - 破坏性动作默认拒绝，必须显式带 --yes；
  - 删除前先写一条审计事件（append-only），事后可回放"谁在什么时候删了哪个 DID"；
  - --dry-run 只打印不落盘。
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eco import identity                                     # noqa: E402


def _main() -> int:
    ap = argparse.ArgumentParser(description="Agent 身份注册表运维")
    ap.add_argument("--list", action="store_true", help="列出存量记录与孤儿情况")
    ap.add_argument("--purge-orphan", action="store_true",
                    help="删除 owner 为空的记录（历史裸注册残留）")
    ap.add_argument("--purge-inactive", action="store_true",
                    help="删除已注销（inactive）的记录")
    ap.add_argument("--dry-run", action="store_true", help="只打印不落盘")
    ap.add_argument("--yes", action="store_true",
                    help="确认执行破坏性动作（默认拒绝）")
    args = ap.parse_args()

    if not any([args.list, args.purge_orphan, args.purge_inactive]):
        ap.error("至少给一个动作：--list / --purge-orphan / --purge-inactive")

    reg = identity.AgentRegistration()
    reg._load()
    agents = reg._agents
    total = len(agents)

    orphans = [d for d, a in agents.items() if not (a.get("owner") or "").strip()]
    inactive = [d for d, a in agents.items() if a.get("status") != "active"]

    if args.list:
        print(f"身份注册表：{total} 条记录")
        print(f"  活跃：{total - len(inactive)}   已注销：{len(inactive)}   孤儿（无 owner）：{len(orphans)}")
        for d in sorted(orphans):
            a = agents[d]
            print(f"  [孤儿] {d}  name={a.get('name')!r} "
                  f"注册于 {a.get('registered_at')}")
        for d in sorted(inactive):
            a = agents[d]
            print(f"  [已注销] {d}  name={a.get('name')!r} "
                  f"注销于 {a.get('revoked_at')}")
        if not args.purge_orphan and not args.purge_inactive:
            print("\n提示：加 --purge-orphan / --purge-inactive 执行清理")
        return 0

    targets: list[str] = []
    if args.purge_orphan:
        targets += orphans
    if args.purge_inactive:
        targets += [d for d in inactive if d not in targets]

    if not targets:
        print("没有需要清理的记录")
        return 0

    print(f"待清理 {len(targets)} 条：")
    for d in targets[:20]:
        print("  ", d)
    if len(targets) > 20:
        print(f"   ... 另 {len(targets) - 20} 条")

    if args.dry_run:
        print("\n--dry-run：未做任何改动")
        return 0
    if not args.yes:
        print("\n拒绝执行破坏性动作：确认请加 --yes（可先 --dry-run 看清单）")
        return 2

    for d in targets:
        identity._append_event("maintenance.purge", d, actor="identity_maintenance",
                               result="purged")
        agents.pop(d, None)
    reg._agents = agents
    reg._save()
    print(f"已清理 {len(targets)} 条（均写入审计事件），剩余 {len(reg._agents)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
