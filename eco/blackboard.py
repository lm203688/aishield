"""
eco/blackboard.py — 跨任务共享上下文仓（本地化 SecondBrain）

GenSpark 6.0 的 SecondBrain 把「上下文可得性」当一等公民；本项目本地优先，
故实现为本地轻量共享黑板：agent 间可写入 / 读取带命名空间的共享状态，
消除来回同步。AIShield 安全闸命中事件也写入 security_events 命名空间，
使 AIShield 成为「既拦截又记录」的 agent 通路节点。

设计原则（与扫描器同源）：
  - 零第三方依赖、可完全离线、不外发数据。
  - 以「命名空间」隔离不同 agent / 任务的共享上下文，降低耦合。
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone, timedelta

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_BASE, "api", "data")
BLACKBOARD_FILE = os.path.join(_DATA, "blackboard.json")
TZ = timezone(timedelta(hours=8))
_lock = threading.RLock()


def _load():
    if not os.path.exists(BLACKBOARD_FILE):
        return {"namespaces": {}}
    try:
        with open(BLACKBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"namespaces": {}}


def _save(data):
    os.makedirs(os.path.dirname(BLACKBOARD_FILE), exist_ok=True)
    with _lock:
        with open(BLACKBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _now_iso():
    return datetime.now(TZ).isoformat()


class Blackboard:
    """
    共享上下文仓：按命名空间组织 agent 间可共享的键值状态与事件流。
    """

    def put(self, namespace, key, value, agent_id=None):
        """写入一条共享状态。"""
        with _lock:
            data = _load()
            ns = data["namespaces"].setdefault(namespace, {"entries": {}, "events": []})
            ns["entries"][key] = {
                "value": value,
                "agent_id": agent_id,
                "updated_at": _now_iso(),
            }
            _save(data)
            return {"namespace": namespace, "key": key, "status": "ok"}

    def get(self, namespace, key):
        """读取一条共享状态；不存在返回 None。"""
        data = _load()
        ns = data["namespaces"].get(namespace)
        if not ns or key not in ns.get("entries", {}):
            return None
        return ns["entries"][key]

    def query(self, namespace=None):
        """
        查询共享状态。
          - 指定 namespace：返回该空间下所有 {key: entry}
          - 不指定：返回 {namespace: [keys...]} 概览
        """
        data = _load()
        if namespace:
            ns = data["namespaces"].get(namespace)
            return ns.get("entries", {}) if ns else {}
        return {
            ns_name: list(ns.get("entries", {}).keys())
            for ns_name, ns in data["namespaces"].items()
        }

    def list_namespaces(self):
        """列出所有命名空间。"""
        data = _load()
        return list(data["namespaces"].keys())

    def append_event(self, namespace, event, agent_id=None):
        """向命名空间追加一条事件（如安全闸命中记录）。"""
        with _lock:
            data = _load()
            ns = data["namespaces"].setdefault(namespace, {"entries": {}, "events": []})
            ev = dict(event)
            ev.setdefault("event_id", f"evt-{uuid.uuid4().hex[:12]}")
            ev["agent_id"] = agent_id
            ev["ts"] = ev.get("ts") or _now_iso()
            ns["events"].append(ev)
            _save(data)
            return ev

    def query_events(self, namespace, limit=50):
        """读取命名空间的事件流（默认最近 limit 条）。"""
        data = _load()
        ns = data["namespaces"].get(namespace)
        if not ns:
            return []
        return ns.get("events", [])[-limit:]

    def delete(self, namespace, key):
        """删除一条共享状态。"""
        with _lock:
            data = _load()
            ns = data["namespaces"].get(namespace)
            if ns and key in ns.get("entries", {}):
                del ns["entries"][key]
                _save(data)
                return True
            return False


if __name__ == "__main__":
    print("=== Blackboard 自检 ===")
    bb = Blackboard()
    bb.put("demo", "goal", {"task": "scan"}, agent_id="a1")
    print("get:", bb.get("demo", "goal"))
    bb.append_event("security_events", {"kind": "test", "decision": "allow"})
    print("namespaces:", bb.list_namespaces())
    print("events:", len(bb.query_events("security_events")))
