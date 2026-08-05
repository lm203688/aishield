"""
AIShield 攻击路径求解 (M4 / F4)

对多客户端 MCP 配置审计产出的「跨服务器毒性组合流」，计算：
  1) 最小移除集（hitting set 贪心）——删掉哪几个 server 即可打破所有毒性流；
  2) 攻击图 JSON（D3 可视化可直接消费）。

这是 mcp-audit 的攻击路径引擎的开源对标实现：不 spawn、纯图算法。
"""
from __future__ import annotations

from collections import defaultdict


def _capability_owners(inventory: list[dict]) -> dict[str, set[str]]:
    owners: dict[str, set[str]] = defaultdict(set)
    for item in inventory:
        name = str(item.get("name") or "?")
        for cap in item.get("capabilities") or ():
            owners[cap].add(name)
    return owners


def _flows_from(inventory: list[dict], toxic_findings: list[dict]):
    """把毒性流 findings 转成「涉及 server 集合」流列表。"""
    owners = _capability_owners(inventory)
    flows = []
    for f in toxic_findings:
        if f.get("type") != "cross_server_toxic_flow":
            continue
        pair = f.get("capability_pair") or []
        if len(pair) != 2:
            continue
        cap_a, cap_b = pair
        a = owners.get(cap_a, set())
        b = owners.get(cap_b, set())
        if not a or not b:
            continue
        if a == b and len(a) == 1:
            involved = set(a)  # 单 server 同时具备两种能力
        else:
            # 跨 server：每条 (a_owner, b_owner) 组合构成一条流
            involved = set()
            for x in a:
                for y in b:
                    if x != y:
                        involved.add(x)
                        involved.add(y)
            if not involved:
                involved = a | b
        flows.append({
            "servers": frozenset(involved),
            "capability_pair": [cap_a, cap_b],
            "severity": f.get("severity", "medium"),
        })
    return flows


def solve_minimal_removal(inventory: list[dict], toxic_findings: list[dict]) -> dict:
    """
    贪心 hitting set：每轮选「参与未覆盖流最多的 server」移除，直至无未覆盖流。

    Returns:
        {
          "removed_servers": [str, ...],   # 建议移除顺序
          "total_flows": int,
          "broken_flows": int,
          "remaining_flows": int,          # 0 表示全部打破
          "iterations": int,
          "note": str,
        }
    """
    flows = _flows_from(inventory, toxic_findings)
    if not flows:
        return {"removed_servers": [], "total_flows": 0, "broken_flows": 0,
                "remaining_flows": 0, "iterations": 0,
                "note": "未检测到跨服务器毒性流"}

    uncovered = list(flows)
    removed: list[str] = []
    iterations = 0
    while uncovered:
        # 统计每个 server 参与的未覆盖流数
        count: dict[str, int] = defaultdict(int)
        for fl in uncovered:
            for s in fl["servers"]:
                count[s] += 1
        if not count:
            break
        best = max(count.items(), key=lambda kv: kv[1])[0]
        removed.append(best)
        uncovered = [fl for fl in uncovered if best not in fl["servers"]]
        iterations += 1
        if iterations > len({s for fl in flows for s in fl["servers"]}) + 2:
            break  # 安全上限，避免异常输入死循环

    return {
        "removed_servers": removed,
        "total_flows": len(flows),
        "broken_flows": len(flows) - len(uncovered),
        "remaining_flows": len(uncovered),
        "iterations": iterations,
        "note": "已生成最小移除集（贪心近似，非全局最优）",
    }


def attack_graph_json(inventory: list[dict], toxic_findings: list[dict]) -> dict:
    """产出 D3 可视化用的节点/边数据。"""
    owners = _capability_owners(inventory)
    nodes = []
    seen = set()
    for item in inventory:
        name = str(item.get("name") or "?")
        if name in seen:
            continue
        seen.add(name)
        nodes.append({
            "id": name,
            "label": name,
            "client": item.get("client", "unknown"),
            "capabilities": sorted(item.get("capabilities") or ()),
        })
    links = []
    for fl in _flows_from(inventory, toxic_findings):
        servers = sorted(fl["servers"])
        if len(servers) == 2:
            links.append({
                "source": servers[0], "target": servers[1],
                "capability_pair": fl["capability_pair"],
                "severity": fl["severity"],
            })
        elif len(servers) == 1:
            links.append({
                "source": servers[0], "target": servers[0],
                "capability_pair": fl["capability_pair"],
                "severity": fl["severity"], "self": True,
            })
    return {"nodes": nodes, "links": links}
