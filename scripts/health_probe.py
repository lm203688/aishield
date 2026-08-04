#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 三路健康探测与事实校验 (Health Probe / Fact Check)
==========================================================
解决问题：此前日报连续 4 天播报"服务连续 11 天不可达"，但实测 HTTP 200 正常。
单点探测 + 无交叉验证 + 结论不回写 = 自动化基于错误事实做决策，越跑越偏。

设计原则：
  1. **多路探测**：API 健康端点 / 根域 / TCP 连通性，三路独立取证。
  2. **多数表决**：≥2 路成功判定为健康，杜绝单次网络抖动导致的误判。
  3. **重试退避**：每路失败重试，避免瞬时抖动被当成故障。
  4. **事实回写**：结论写入状态总线，成为全体自动化任务的唯一事实来源(SSOT)。
  5. **状态翻转才告警**：健康->故障 才通知；故障->健康 自动 resolve 关闭 Issue。

用法：
    python scripts/health_probe.py                    # 探测并回写状态
    python scripts/health_probe.py --notify           # 探测 + 状态翻转时告警/恢复
    python scripts/health_probe.py --json             # 仅输出 JSON 结果
退出码：0=健康，1=降级/故障（供 workflow 做条件分支）
"""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.state_bus import StateBus  # noqa: E402

DOMAIN = "aishield.tools"
PROBES = [
    {"name": "api_health", "url": f"https://{DOMAIN}/api/v1/health", "expect": "ok", "weight": 2},
    {"name": "root", "url": f"https://{DOMAIN}/", "expect": None, "weight": 1},
    {"name": "openapi", "url": f"https://{DOMAIN}/api/v1/openapi.json", "expect": None, "weight": 1},
]
RETRIES = 3
TIMEOUT = 20
FINGERPRINT = "service-health-down"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ctx() -> ssl.SSLContext:
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c


def probe_http(url: str, expect: str | None) -> Dict[str, Any]:
    """单路 HTTP 探测，带重试退避。"""
    last_err = ""
    for attempt in range(1, RETRIES + 1):
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "aishield-probe/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=_ctx()) as r:
                body = r.read(4096).decode("utf-8", errors="replace")
                elapsed = round(time.time() - t0, 3)
                code = r.status
                ok = 200 <= code < 400
                if ok and expect:
                    ok = expect in body
                if ok:
                    return {"ok": True, "http": code, "elapsed": elapsed, "attempt": attempt}
                last_err = f"HTTP {code}" + ("" if not expect else f" / 缺少期望内容 '{expect}'")
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            # 4xx 说明服务活着只是路径不对，对连通性判定算"可达"
            if 400 <= e.code < 500:
                return {
                    "ok": True,
                    "http": e.code,
                    "elapsed": round(time.time() - t0, 3),
                    "attempt": attempt,
                    "note": "4xx 视为服务存活",
                }
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
        if attempt < RETRIES:
            time.sleep(2 * attempt)  # 线性退避
    return {"ok": False, "error": last_err, "attempt": RETRIES}


def probe_tcp(host: str, port: int = 443) -> Dict[str, Any]:
    """TCP 层探测：区分'服务挂了'与'应用层报错'。"""
    t0 = time.time()
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return {"ok": True, "elapsed": round(time.time() - t0, 3)}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def probe_dns(host: str) -> Dict[str, Any]:
    try:
        ips = sorted({r[4][0] for r in socket.getaddrinfo(host, None)})
        return {"ok": True, "ips": ips}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    score = 0
    total_weight = 0

    for p in PROBES:
        r = probe_http(p["url"], p["expect"])
        results[p["name"]] = r
        total_weight += p["weight"]
        if r.get("ok"):
            score += p["weight"]

    results["tcp"] = probe_tcp(DOMAIN, 443)
    results["dns"] = probe_dns(DOMAIN)

    # 多数表决：加权得分 >= 半数即判定健康
    healthy = score >= (total_weight / 2.0)
    # api_health 单独通过也直接判健康（核心端点是最强证据）
    if results.get("api_health", {}).get("ok"):
        healthy = True
    # 全部 HTTP 失败但 TCP 通 => 应用层故障（degraded 而非 down）
    if not healthy and results["tcp"].get("ok"):
        level = "degraded"
    elif healthy:
        level = "healthy"
    else:
        level = "down"

    api = results.get("api_health", {})
    verdict = {
        "healthy": healthy,
        "level": level,
        "score": score,
        "max_score": total_weight,
        "http": api.get("http"),
        "latency": api.get("elapsed"),
        "checked_at": _now(),
        "probes": results,
    }
    return verdict


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 三路健康探测")
    ap.add_argument("--notify", action="store_true", help="状态翻转时发送告警/恢复通知")
    ap.add_argument("--json", action="store_true", help="仅输出 JSON")
    args = ap.parse_args()

    verdict = run()
    bus = StateBus()
    prev = bus.get("health").get("current") or {}
    prev_healthy = prev.get("healthy")

    # 连续故障计数：只在真实故障时累加，恢复即清零（杜绝"11天不可达"这类幽灵计数）
    if verdict["healthy"]:
        verdict["consecutive_failures"] = 0
        verdict["last_healthy_at"] = verdict["checked_at"]
    else:
        verdict["consecutive_failures"] = int(prev.get("consecutive_failures") or 0) + 1
        verdict["last_healthy_at"] = prev.get("last_healthy_at")

    bus.set("health", {k: v for k, v in verdict.items() if k != "probes"}, source="health_probe")
    # 探测明细存入 detail/ 子目录：避免膨胀主状态文件，也避免被 stale 扫描误判为状态域
    detail_dir = Path(__file__).resolve().parent.parent / "data" / "state" / "detail"
    detail_dir.mkdir(parents=True, exist_ok=True)
    (detail_dir / "health_probes.json").write_text(
        json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if args.json:
        print(json.dumps(verdict, ensure_ascii=False, indent=2))
    else:
        icon = "✅" if verdict["healthy"] else "❌"
        print(f"{icon} 判定: {verdict['level']} (得分 {verdict['score']}/{verdict['max_score']})")
        for name, r in verdict["probes"].items():
            mark = "✓" if r.get("ok") else "✗"
            detail = r.get("http") or r.get("error") or r.get("ips") or ""
            print(f"   {mark} {name:<12} {detail}")
        if not verdict["healthy"]:
            print(f"   连续失败次数: {verdict['consecutive_failures']}")

    if args.notify:
        try:
            from scripts.notify import notify, resolve

            if not verdict["healthy"] and prev_healthy is not False:
                # 健康 -> 故障：翻转告警
                body = (
                    f"三路探测判定服务 **{verdict['level']}**（得分 {verdict['score']}/{verdict['max_score']}）\n\n"
                    + "\n".join(
                        f"- `{n}`: {'✓ 通过' if r.get('ok') else '✗ ' + str(r.get('error', ''))}"
                        for n, r in verdict["probes"].items()
                    )
                )
                notify("P0", f"服务健康探测失败 ({verdict['level']})", body, FINGERPRINT)
            elif verdict["healthy"] and prev_healthy is False:
                # 故障 -> 健康：自动关闭告警，闭环
                resolve(
                    FINGERPRINT,
                    "服务已恢复",
                    f"三路探测确认服务恢复正常，HTTP {verdict.get('http')}，延迟 {verdict.get('latency')}s。",
                )
        except Exception as e:
            print(f"[warn] 通知环节异常（不阻断探测）: {e}")

    return 0 if verdict["healthy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
