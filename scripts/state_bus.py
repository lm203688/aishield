#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 状态总线 (State Bus)
=============================
解决问题：此前各自动化环节之间用 Markdown 散文传递结论，机器无法读取，
导致"监测 -> 修复 -> 测试 -> 上线 -> 验证"链条在环节之间断裂。

设计原则：
  1. 机器间只传 JSON，人读的 Markdown 由 JSON 渲染而来，绝不反向解析。
  2. 每个状态文件是"事实快照 + 变更历史"，可被任何 workflow 读写。
  3. 所有写入带时间戳与来源，便于追溯是哪个任务写的。

状态文件位置：data/state/<domain>.json

用法（命令行）：
    python scripts/state_bus.py set health '{"http":200,"healthy":true}' --source self-heal
    python scripts/state_bus.py get health
    python scripts/state_bus.py get health --key healthy
    python scripts/state_bus.py history health --limit 5
    python scripts/state_bus.py summary

用法（模块）：
    from scripts.state_bus import StateBus
    bus = StateBus()
    bus.set("health", {"http": 200, "healthy": True}, source="self-heal")
    st = bus.get("health")
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = REPO_ROOT / "data" / "state"

# 已知状态域，用于 summary 与校验；未知域也允许写入（宽松策略）
KNOWN_DOMAINS = {
    "health": "线上服务健康事实（由三路探测写入）",
    "selfheal": "自愈闭环执行结果（修复/测试/部署/验证）",
    "distribution": "内容与生态分发执行结果",
    "intel": "威胁情报采集与转化结果",
    "rules": "扫描规则库版本与来源",
    "flywheel": "数据飞轮批量扫描进度",
    "feature": "功能迭代闭环采纳结果",
    "meta": "元监控：自动化体系自身的健康度",
    "registry": "MCP Registry / npm / Marketplace 上架状态",
    "ci": "CI 门禁运行结果（跨 workflow 复用的状态枢纽）",
    "deploy": "部署与上线验证结果（deploy-server 独占写入）",
}

MAX_HISTORY = 50


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateBus:
    """状态总线：跨 workflow 的机器可读事实存储。"""

    def __init__(self, state_dir: Path | str = STATE_DIR):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, domain: str) -> Path:
        safe = "".join(c for c in domain if c.isalnum() or c in "-_")
        return self.state_dir / f"{safe}.json"

    def get(self, domain: str) -> Dict[str, Any]:
        """读取某状态域的当前快照；不存在返回空壳。"""
        p = self._path(domain)
        if not p.exists():
            return {"domain": domain, "current": {}, "history": [], "updated": None}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            # 文件损坏时不阻断流水线，返回空壳并保留损坏文件备份
            try:
                p.rename(p.with_suffix(".json.corrupt"))
            except Exception:
                pass
            return {"domain": domain, "current": {}, "history": [], "updated": None}

    def set(
        self,
        domain: str,
        payload: Dict[str, Any],
        source: str = "unknown",
        merge: bool = True,
    ) -> Dict[str, Any]:
        """写入状态。merge=True 时与既有 current 合并，False 时整体替换。"""
        st = self.get(domain)
        prev = dict(st.get("current") or {})
        new_current = {**prev, **payload} if merge else dict(payload)
        new_current["_source"] = source
        new_current["_ts"] = _now()

        history: List[Dict[str, Any]] = st.get("history") or []
        # 只在实际发生变化时记历史，避免历史被无变化的心跳刷屏
        prev_cmp = {k: v for k, v in prev.items() if not k.startswith("_")}
        new_cmp = {k: v for k, v in new_current.items() if not k.startswith("_")}
        if prev_cmp != new_cmp:
            history.append({"ts": _now(), "source": source, "state": new_cmp})
            history = history[-MAX_HISTORY:]

        st.update(
            {
                "domain": domain,
                "desc": KNOWN_DOMAINS.get(domain, ""),
                "current": new_current,
                "history": history,
                "updated": _now(),
            }
        )
        self._path(domain).write_text(
            json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return st

    def value(self, domain: str, key: str, default: Any = None) -> Any:
        return (self.get(domain).get("current") or {}).get(key, default)

    def history(self, domain: str, limit: int = 10) -> List[Dict[str, Any]]:
        return (self.get(domain).get("history") or [])[-limit:]

    def _is_state_file(self, path: Path) -> bool:
        """只有带 domain/current 结构的文件才算状态域。
        published.json、alert_cooldown.json 等辅助文件不参与新鲜度判定，
        否则会把正常的数据文件误报成"环节停摆"。"""
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
            return isinstance(d, dict) and "domain" in d and "current" in d
        except Exception:
            return False

    def domains(self) -> List[str]:
        return sorted(f.stem for f in self.state_dir.glob("*.json") if self._is_state_file(f))

    def summary(self) -> Dict[str, Any]:
        """全域汇总，供元监控与日报使用。"""
        out: Dict[str, Any] = {"generated": _now(), "domains": {}}
        for d in self.domains():
            st = self.get(d)
            cur = st.get("current") or {}
            out["domains"][d] = {
                "updated": st.get("updated"),
                "source": cur.get("_source"),
                "keys": {k: v for k, v in cur.items() if not k.startswith("_")},
            }
        return out

    def stale_domains(self, max_age_hours: int = 48) -> List[str]:
        """返回超过 max_age_hours 未更新的状态域——静默失败的信号。"""
        stale = []
        now = datetime.now(timezone.utc)
        for d in self.domains():
            st = self.get(d)
            upd = st.get("updated")
            if not upd:
                stale.append(d)
                continue
            try:
                t = datetime.fromisoformat(upd)
                if (now - t).total_seconds() > max_age_hours * 3600:
                    stale.append(d)
            except Exception:
                stale.append(d)
        return sorted(stale)


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 状态总线")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_set = sub.add_parser("set", help="写入状态")
    p_set.add_argument("domain")
    p_set.add_argument("payload", help="JSON 字符串")
    p_set.add_argument("--source", default="cli")
    p_set.add_argument("--replace", action="store_true", help="整体替换而非合并")

    p_get = sub.add_parser("get", help="读取状态")
    p_get.add_argument("domain")
    p_get.add_argument("--key", help="只取某个字段")

    p_hist = sub.add_parser("history", help="查看变更历史")
    p_hist.add_argument("domain")
    p_hist.add_argument("--limit", type=int, default=10)

    sub.add_parser("summary", help="全域汇总")

    p_stale = sub.add_parser("stale", help="列出超时未更新的状态域")
    p_stale.add_argument("--hours", type=int, default=48)

    args = ap.parse_args()
    bus = StateBus()

    if args.cmd == "set":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError as e:
            print(f"payload 不是合法 JSON: {e}", file=sys.stderr)
            return 2
        st = bus.set(args.domain, payload, source=args.source, merge=not args.replace)
        print(json.dumps(st["current"], ensure_ascii=False, indent=2))
    elif args.cmd == "get":
        st = bus.get(args.domain)
        if args.key:
            v = (st.get("current") or {}).get(args.key)
            print("" if v is None else (v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)))
        else:
            print(json.dumps(st, ensure_ascii=False, indent=2))
    elif args.cmd == "history":
        print(json.dumps(bus.history(args.domain, args.limit), ensure_ascii=False, indent=2))
    elif args.cmd == "summary":
        print(json.dumps(bus.summary(), ensure_ascii=False, indent=2))
    elif args.cmd == "stale":
        print(json.dumps(bus.stale_domains(args.hours), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
