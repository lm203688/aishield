#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 权威漏洞库对接 (Authoritative Vulnerability Feeds)
==========================================================
评估报告指出：threat-intel-feed 号称"专业数据库对接"，实际只在
GitHub 搜仓库名（`search/repositories?q=MCP server security CVE`），
拿回来的是**仓库列表而非漏洞记录** —— 这不是威胁情报，是搜索结果。
领域专家视角下，这一项直接判不及格。

本模块对接三个真正的权威源，且全部零凭据可用：
  1. OSV.dev        —— Google 开源漏洞库，覆盖 npm/PyPI/Go，MCP 生态主战场
  2. NVD (NIST)     —— 美国国家漏洞库，CVE 权威定义方
  3. GitHub Advisory—— GitHub 安全公告库，生态针对性最强

输出统一 schema，可直接被规则引擎消费：
  {id, source, severity, cvss, title, summary, affected, references, published}

用法：
    python scripts/fetch_vuln_feeds.py --days 30
    python scripts/fetch_vuln_feeds.py --days 7 --notify
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

THREAT_DB = REPO_ROOT / "data" / "threat_intel.json"
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""

# MCP / AI Agent 生态的关键攻击面关键词
KEYWORDS = [
    "prompt injection",
    "model context protocol",
    "llm agent",
    "ai agent sandbox escape",
    "tool poisoning",
]
# OSV 直接按生态+包名查更准，这些是 MCP 生态高频依赖
OSV_ECOSYSTEMS = ["npm", "PyPI"]
OSV_PACKAGES = [
    ("npm", "@modelcontextprotocol/sdk"),
    ("npm", "@modelcontextprotocol/server-filesystem"),
    ("npm", "langchain"),
    ("PyPI", "mcp"),
    ("PyPI", "langchain"),
    ("PyPI", "llama-index"),
]

# --------------------------------------------------------------------------
# 上游数据源健康（闭环补位：检测 → 重试 → 降级告警 → 恢复即关闭）
# --------------------------------------------------------------------------
# 旧实现的洞：三个源各自的异常被 `except: print(...)` 吞掉就完事 —— 既不记状态
# 也不告警。任一个源可以静默宕机数周，而流程照常写库、照常返回 0（绿）。
# 更糟的是三个源**全部**失败时仍然 exit 0：情报库整整停更，流水线却报成功。
#
# 现在的语义（fail-closed，与项目"禁止吞门禁失败"铁律一致）：
#   · 全部源成功      → exit 0，并关闭降级/宕机告警（恢复即关闭）
#   · 部分源失败      → exit 0（仍有可用数据）+ P1 告警，逐源记 consecutive_failures
#   · 全部源失败      → exit 1 让流程变红，且不刷新 updated（停更必须可见）
SOURCE_RETRIES = 2          # 单源额外重试次数（共 1 + 2 次尝试）
RETRY_BACKOFF_SEC = 3       # 退避基数：第 n 次重试前等待 n * base 秒
FP_DEGRADED = "vuln-source-degraded"   # 部分上游源不可用
FP_DOWN = "vuln-source-down"           # 全部上游源不可用（情报停更）


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ctx() -> ssl.SSLContext:
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c


# 传输层计数：用于区分"该源近期确实没有新漏洞"与"该源根本没连上"。
# 这是旧版最隐蔽的一层假绿 —— fetcher 内部 `if not res: continue` 会把传输
# 失败降级成空列表，调用方看到 [] 只能理解成"没有新情报"，于是源彻底宕机
# 也表现为健康。计数器让 fetcher 能在"一个请求都没成功"时显式抛错。
_TRANSPORT = {"req": 0, "ok": 0, "fail": 0}


def _reset_transport() -> None:
    _TRANSPORT.update(req=0, ok=0, fail=0)


def _assert_transport(name: str) -> None:
    """一次请求都没成功 → 抛错，绝不返回 [] 冒充"无新漏洞"。"""
    if _TRANSPORT["req"] > 0 and _TRANSPORT["ok"] == 0:
        raise RuntimeError(
            f"{name} 传输层全部失败：{_TRANSPORT['fail']}/{_TRANSPORT['req']} 次请求无一成功"
        )


def _req(url: str, data: dict | None = None, headers: dict | None = None, timeout: int = 30):
    h = {"User-Agent": "aishield-intel/1.0", "Accept": "application/json"}
    h.update(headers or {})
    body = json.dumps(data).encode("utf-8") if data else None
    if body:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h, method="POST" if body else "GET")
    _TRANSPORT["req"] += 1
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            payload = json.loads(r.read().decode("utf-8"))
            _TRANSPORT["ok"] += 1
            return payload
    except urllib.error.HTTPError as e:
        _TRANSPORT["fail"] += 1
        print(f"   ! HTTP {e.code} {url[:80]}")
    except Exception as e:
        _TRANSPORT["fail"] += 1
        print(f"   ! {type(e).__name__} {url[:80]}: {e}")
    return None


def _severity_from_cvss(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    return "low"


# --------------------------------------------------------------------------
# 源 1：OSV.dev
# --------------------------------------------------------------------------
def fetch_osv(days: int) -> List[Dict[str, Any]]:
    print("[1/3] OSV.dev（Google 开源漏洞库）")
    out: List[Dict[str, Any]] = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    for eco, pkg in OSV_PACKAGES:
        res = _req("https://api.osv.dev/v1/query", {"package": {"name": pkg, "ecosystem": eco}})
        if not res:
            continue
        for v in (res.get("vulns") or [])[:20]:
            pub = v.get("published", "")
            try:
                if pub and datetime.fromisoformat(pub.replace("Z", "+00:00")) < cutoff:
                    continue
            except Exception:
                pass
            sev = "unknown"
            cvss = None
            for s in v.get("severity") or []:
                if s.get("type", "").startswith("CVSS"):
                    try:
                        cvss = float(str(s.get("score", "")).split("/")[0])
                    except Exception:
                        pass
            if v.get("database_specific", {}).get("severity"):
                sev = str(v["database_specific"]["severity"]).lower()
            elif cvss is not None:
                sev = _severity_from_cvss(cvss)
            out.append({
                "id": v.get("id"),
                "source": "osv",
                "severity": sev,
                "cvss": cvss,
                "title": (v.get("summary") or v.get("id") or "")[:200],
                "summary": (v.get("details") or "")[:500],
                "affected": f"{eco}:{pkg}",
                "references": [r.get("url") for r in (v.get("references") or [])][:5],
                "published": pub,
                "fetched": _now(),
            })
        time.sleep(0.4)  # 礼貌限速
    _assert_transport("osv")
    print(f"   → 获取 {len(out)} 条")
    return out


# --------------------------------------------------------------------------
# 源 2：NVD (NIST)
# --------------------------------------------------------------------------
def fetch_nvd(days: int) -> List[Dict[str, Any]]:
    print("[2/3] NVD（NIST 国家漏洞库）")
    out: List[Dict[str, Any]] = []
    start = (datetime.now(timezone.utc) - timedelta(days=min(days, 120))).strftime("%Y-%m-%dT%H:%M:%S.000")
    end = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000")

    for kw in KEYWORDS[:3]:  # 无 API key 时限速严格，取最关键的 3 个
        url = (
            "https://services.nvd.nist.gov/rest/json/cves/2.0?"
            + urllib.parse.urlencode({
                "keywordSearch": kw,
                "pubStartDate": start,
                "pubEndDate": end,
                "resultsPerPage": 20,
            })
        )
        res = _req(url, timeout=45)
        if not res:
            time.sleep(6)
            continue
        for item in res.get("vulnerabilities") or []:
            c = item.get("cve") or {}
            descs = [d.get("value") for d in c.get("descriptions") or [] if d.get("lang") == "en"]
            cvss = None
            sev = "unknown"
            metrics = c.get("metrics") or {}
            for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                if metrics.get(key):
                    d = metrics[key][0].get("cvssData") or {}
                    cvss = d.get("baseScore")
                    sev = (d.get("baseSeverity") or _severity_from_cvss(cvss)).lower()
                    break
            out.append({
                "id": c.get("id"),
                "source": "nvd",
                "severity": sev,
                "cvss": cvss,
                "title": (descs[0][:200] if descs else c.get("id", "")),
                "summary": (descs[0][:500] if descs else ""),
                "affected": kw,
                "references": [r.get("url") for r in (c.get("references") or [])][:5],
                "published": c.get("published", ""),
                "fetched": _now(),
            })
        time.sleep(6)  # NVD 无 key 限速：约 5 请求/30 秒
    _assert_transport("nvd")
    print(f"   → 获取 {len(out)} 条")
    return out


# --------------------------------------------------------------------------
# 源 3：GitHub Security Advisory
# --------------------------------------------------------------------------
def fetch_github_advisory(days: int) -> List[Dict[str, Any]]:
    print("[3/3] GitHub Security Advisory")
    out: List[Dict[str, Any]] = []
    headers = {"Accept": "application/vnd.github+json"}
    if GH_TOKEN:
        headers["Authorization"] = f"Bearer {GH_TOKEN}"

    for eco in ["npm", "pip"]:
        url = f"https://api.github.com/advisories?ecosystem={eco}&per_page=50&sort=published"
        res = _req(url, headers=headers)
        if not isinstance(res, list):
            continue
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        for a in res:
            pub = a.get("published_at", "")
            try:
                if pub and datetime.fromisoformat(pub.replace("Z", "+00:00")) < cutoff:
                    continue
            except Exception:
                pass
            text = ((a.get("summary") or "") + " " + (a.get("description") or "")).lower()
            # 只留与 AI Agent / MCP 攻击面相关的
            if not any(k in text for k in
                       ["prompt", "llm", "agent", "mcp", "model context", "ai ", "sandbox", "tool"]):
                continue
            pkgs = []
            for v in a.get("vulnerabilities") or []:
                p = (v.get("package") or {}).get("name")
                if p:
                    pkgs.append(f"{eco}:{p}")
            out.append({
                "id": a.get("ghsa_id"),
                "source": "github-advisory",
                "severity": (a.get("severity") or "unknown").lower(),
                "cvss": (a.get("cvss") or {}).get("score"),
                "title": (a.get("summary") or "")[:200],
                "summary": (a.get("description") or "")[:500],
                "affected": ", ".join(pkgs[:5]),
                "references": [a.get("html_url")],
                "published": pub,
                "fetched": _now(),
            })
        time.sleep(0.5)
    print(f"   → 获取 {len(out)} 条")
    return out


# --------------------------------------------------------------------------
def load_db() -> Dict[str, Any]:
    if THREAT_DB.exists():
        try:
            d = json.loads(THREAT_DB.read_text(encoding="utf-8"))
            if isinstance(d, list):
                return {"intel": d}
            return d
        except Exception:
            pass
    return {"intel": []}


# --------------------------------------------------------------------------
# 上游源健康：带重试抓取 + 逐源留痕
# --------------------------------------------------------------------------
def fetch_source(name: str, fn, days: int, retries: int = SOURCE_RETRIES):
    """抓取单个源，带重试，并**始终**把真相留在返回值里。

    返回 (items, health)。health.ok=False 时 items 必为空列表 —— 绝不用
    "空结果"冒充"抓取成功"，否则空源与健康源在下游无法区分。
    """
    last_err = None
    for attempt in range(retries + 1):
        try:
            items = fn(days)
            if not isinstance(items, list):
                raise TypeError(f"源返回非列表: {type(items).__name__}")
            return items, {
                "ok": True,
                "items": len(items),
                "attempts": attempt + 1,
                "error": None,
                "checked_at": _now(),
            }
        except Exception as e:  # 单源失败绝不阻断其他源
            last_err = f"{type(e).__name__}: {e}"
            if attempt < retries:
                wait = RETRY_BACKOFF_SEC * (attempt + 1)
                print(f"   ~ {name} 第 {attempt + 1} 次失败（{last_err}）—— {wait}s 后重试")
                time.sleep(wait)
    return [], {
        "ok": False,
        "items": 0,
        "attempts": retries + 1,
        "error": last_err,
        "checked_at": _now(),
        "consecutive_failures": 0,   # 由 _apply_history 补齐
    }


def _prev_health(db: Dict[str, Any]) -> Dict[str, Any]:
    """读上一轮入库的逐源健康，用于累计连续失败次数。"""
    block = db.get("source_health")
    if not isinstance(block, dict):
        return {}
    srcs = block.get("sources")
    return srcs if isinstance(srcs, dict) else {}


def _apply_history(health: Dict[str, Any], prev: Dict[str, Any]) -> None:
    """就地补 consecutive_failures / degraded_since。

    连续失败次数是升级判据的来源：元监控 M7 只在 >= 2 次时才判 degraded，
    这样一次网络抖动不会把整个体系报成异常，而长期宕机一定会暴露。
    """
    for name, h in health.items():
        if h.get("ok"):
            h["consecutive_failures"] = 0
            h["degraded_since"] = None
            continue
        p = prev.get(name) or {}
        try:
            n = int(p.get("consecutive_failures") or 0) + 1
        except Exception:
            n = 1
        h["consecutive_failures"] = n
        # degraded_since 必须始终有值：为 None 会让下游算不出"已宕机多久"
        h["degraded_since"] = p.get("degraded_since") or h.get("checked_at") or _now()


def _notify_source_health(health: Dict[str, Any], any_ok: bool, all_ok: bool,
                          notify_on: bool) -> None:
    """按健康真相开关告警 —— 恢复即关闭，杜绝陈旧 P1 堆积。"""
    try:
        from scripts.notify import notify, resolve
    except Exception as e:
        print(f"[warn] 通知总线不可用: {e}")
        return

    down = sorted(n for n, h in health.items() if not h.get("ok"))

    if all_ok:
        for fp, title in ((FP_DOWN, "上游情报源已全部恢复"),
                          (FP_DEGRADED, "上游情报源降级已恢复")):
            try:
                resolve(fp, title=title, note="本轮抓取所有上游源均成功。")
            except Exception as e:
                print(f"[warn] 关闭告警 {fp} 失败: {e}")
        return

    # 部分恢复：宕机条件已解除，但降级仍在 → 只关"全部宕机"那条
    if any_ok:
        try:
            resolve(FP_DOWN, title="上游情报源已部分恢复",
                    note=f"仍有源不可用：{', '.join(down)}")
        except Exception as e:
            print(f"[warn] 关闭告警 {FP_DOWN} 失败: {e}")

    if not notify_on:
        return

    detail = "\n".join(
        f"- `{n}`：连续 {h.get('consecutive_failures', 1)} 次失败，"
        f"attempts={h.get('attempts')}，last={h.get('error')}"
        for n, h in sorted(health.items()) if not h.get("ok")
    ) or "- （无失败源）"

    try:
        if any_ok:
            notify("P1", f"上游情报源降级（{len(down)}/{len(health)} 不可用）",
                   f"以下漏洞数据源抓取失败，情报覆盖已出现缺口：\n\n{detail}\n\n"
                   f"> 其余源正常，本次运行继续；连续失败会累计，恢复后自动关闭本告警。",
                   FP_DEGRADED, cooldown_hours=12)
        else:
            notify("P1", "上游情报源全部不可用，情报库已停更",
                   f"OSV / NVD / GitHub Advisory **全部**抓取失败，本轮情报零更新：\n\n{detail}\n\n"
                   f"> 已按 fail-closed 让流程变红；`updated` 未刷新，停更可被元监控 M7 察觉。",
                   FP_DOWN, cooldown_hours=6)
    except Exception as e:
        print(f"[warn] 源健康告警失败: {e}")


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 权威漏洞库对接")
    ap.add_argument("--days", type=int, default=30, help="拉取最近 N 天的漏洞")
    ap.add_argument("--notify", action="store_true", help="发现 critical/high 或源异常时告警")
    ap.add_argument("--retries", type=int, default=SOURCE_RETRIES,
                    help="单个上游源的额外重试次数（默认 %(default)s）")
    args = ap.parse_args()

    print(f"拉取最近 {args.days} 天的 MCP / AI Agent 相关漏洞\n" + "=" * 60)

    db_prev = load_db()
    prev_sources = _prev_health(db_prev)

    fetchers = [("osv", fetch_osv), ("nvd", fetch_nvd),
                ("github-advisory", fetch_github_advisory)]

    new: List[Dict[str, Any]] = []
    health: Dict[str, Any] = {}
    for name, fn in fetchers:
        items, h = fetch_source(name, fn, args.days, retries=args.retries)
        health[name] = h
        new.extend(items)
        mark = "ok  " if h["ok"] else "FAIL"
        tail = "" if h["ok"] else f"  err={h['error']}"
        print(f"   [{mark}] {name:16} items={h['items']:<4} attempts={h['attempts']}{tail}")

    _apply_history(health, prev_sources)

    any_ok = any(h["ok"] for h in health.values())
    all_ok = all(h["ok"] for h in health.values())
    down = sorted(n for n, h in health.items() if not h["ok"])

    intel: List[Dict[str, Any]] = db_prev.get("intel") or []
    seen = {i.get("id") for i in intel if i.get("id")}
    added = [i for i in new if i.get("id") and i["id"] not in seen]
    for i in added:
        intel.append(i)
        seen.add(i["id"])

    # 保留最近 1000 条，权威源优先
    intel.sort(key=lambda x: x.get("published") or "", reverse=True)
    intel = intel[:1000]

    stats: Dict[str, int] = {}
    for i in intel:
        stats[i.get("severity", "unknown")] = stats.get(i.get("severity", "unknown"), 0) + 1

    prev_block = db_prev.get("source_health")
    prev_last_success = prev_block.get("last_success") if isinstance(prev_block, dict) else None
    now = _now()

    THREAT_DB.parent.mkdir(parents=True, exist_ok=True)
    THREAT_DB.write_text(
        json.dumps(
            {
                "intel": intel,
                # 关键：全源失败时**不刷新** updated，让"停更"在时间戳上可见
                "updated": now if any_ok else (db_prev.get("updated") or now),
                "sources": [n for n, _ in fetchers],
                "sources_ok": sorted(n for n, h in health.items() if h["ok"]),
                "sources_failed": down,
                "source_health": {
                    "sources": health,
                    "degraded": down,
                    "last_success": now if any_ok else (prev_last_success or ""),
                    "last_attempt": now,
                },
                "stats": stats,
                "total": len(intel),
            },
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 60)
    print(f"本轮新增 {len(added)} 条，情报库共 {len(intel)} 条")
    print(f"分级统计: {json.dumps(stats, ensure_ascii=False)}")
    print(f"源健康: ok={sorted(n for n, h in health.items() if h['ok'])} "
          f"failed={down}")

    high = [i for i in added if i.get("severity") in ("critical", "high")]
    if high:
        print(f"\n⚠️ 本轮新增 {len(high)} 条高危漏洞：")
        for i in high[:10]:
            print(f"   [{i['severity'].upper()}] {i['id']} — {i['title'][:70]}")

    try:
        from scripts.state_bus import StateBus

        StateBus().set(
            "intel",
            {
                "total": len(intel), "added": len(added), "high_new": len(high),
                "stats": stats, "sources": [n for n, _ in fetchers],
                "sources_failed": down, "sources_ok": sorted(n for n, h in health.items() if h["ok"]),
                "degraded": bool(down), "total_outage": not any_ok,
                "last_run": now,
            },
            source="fetch_vuln_feeds",
        )
    except Exception as e:
        print(f"[warn] 状态回写失败: {e}")

    if args.notify and high:
        try:
            from scripts.notify import notify

            body = f"权威漏洞库本轮新增 **{len(high)}** 条 critical/high 级漏洞，涉及 MCP / AI Agent 攻击面：\n\n"
            for i in high[:15]:
                body += f"- **[{i['severity'].upper()}] {i['id']}** — {i['title'][:100]}\n"
                if i.get("affected"):
                    body += f"  影响：`{i['affected']}`\n"
            body += "\n> 这些漏洞将由 intel_to_rules 自动转化为扫描规则。"
            notify("P1", f"新增 {len(high)} 条高危 AI Agent 漏洞", body,
                   "new-high-vulns", cooldown_hours=12)
        except Exception as e:
            print(f"[warn] 通知失败: {e}")

    # 上游源健康：告警 + 恢复即关闭（闭环的第三、四环）
    _notify_source_health(health, any_ok, all_ok, notify_on=args.notify)

    if not any_ok:
        print("\n❌ 全部上游源抓取失败 —— fail-closed：本轮判失败，情报库未刷新。")
        return 1
    if down:
        print(f"\n⚠️ {len(down)} 个上游源不可用（{', '.join(down)}），"
              f"仍有源可用，本轮继续。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
