#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 通知总线 (Notification Bus)
====================================
解决问题：此前所有告警的终点都是仓库里的 Markdown 文件，没人看 = 等于没告警。
本模块保证任何 P0/P1 事件都能**离开文件系统**，抵达人或机器人。

出口优先级（自动降级，任一成功即算送达）：
  1. GitHub Issue   —— Actions 内 GITHUB_TOKEN 自带，零配置零成本（默认主出口）
  2. Webhook        —— 飞书/企业微信/Slack/Discord 通用，配 NOTIFY_WEBHOOK 即启用
  3. 本地文件落盘   —— 兜底审计轨迹，永远执行

关键特性：
  * 去重冷却：同 fingerprint 事件在 cooldown 内不重复轰炸（默认 6 小时）
  * 自动恢复：故障恢复时调用 resolve()，自动关闭对应 Issue，形成告警闭环
  * 分级路由：P0 必达（全出口广播）；P1 主出口；P2 仅落盘

用法：
    python scripts/notify.py --level P0 --title "服务不可达" --body "详情..." --fingerprint health-down
    python scripts/notify.py --resolve --fingerprint health-down --title "服务已恢复"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
ALERT_LOG = REPO_ROOT / "data" / "state" / "alerts.jsonl"
COOLDOWN_FILE = REPO_ROOT / "data" / "state" / "alert_cooldown.json"

GH_OWNER = os.environ.get("GH_OWNER", "lm203688")
GH_REPO = os.environ.get("GH_REPO", "aishield")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
WEBHOOK = os.environ.get("NOTIFY_WEBHOOK", "")

DEFAULT_COOLDOWN_HOURS = 6
LEVEL_EMOJI = {"P0": "🔴", "P1": "🟠", "P2": "🟡"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fingerprint(title: str, fp: Optional[str]) -> str:
    if fp:
        return fp
    return hashlib.sha1(title.encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------
# 出口 1：GitHub Issue
# --------------------------------------------------------------------------
def _gh_api(method: str, path: str, payload: Optional[dict] = None) -> Optional[Any]:
    if not GH_TOKEN:
        return None
    url = f"https://api.github.com{path}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {GH_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "aishield-notify")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print(f"[notify] GitHub API {method} {path} -> HTTP {e.code}: {e.read()[:200]}")
    except Exception as e:
        print(f"[notify] GitHub API 调用失败: {e}")
    return None


def _find_issue(fingerprint: str) -> Optional[dict]:
    """按 fingerprint 标记查找已开启的告警 Issue。"""
    issues = _gh_api("GET", f"/repos/{GH_OWNER}/{GH_REPO}/issues?state=open&per_page=100")
    if not issues:
        return None
    marker = f"<!--aishield-fp:{fingerprint}-->"
    for i in issues:
        if marker in (i.get("body") or ""):
            return i
    return None


def send_github_issue(level: str, title: str, body: str, fingerprint: str) -> bool:
    if not GH_TOKEN:
        print("[notify] 未提供 GITHUB_TOKEN，跳过 Issue 出口")
        return False
    marker = f"<!--aishield-fp:{fingerprint}-->"
    full_body = (
        f"{marker}\n"
        f"**级别：** {LEVEL_EMOJI.get(level, '')} {level}\n"
        f"**首次触发：** `{_now()}`\n"
        f"**指纹：** `{fingerprint}`\n\n"
        f"---\n\n{body}\n\n"
        f"---\n"
        f"> 本 Issue 由 AIShield 通知总线自动创建。故障恢复后会自动关闭，无需人工处理。"
    )
    existing = _find_issue(fingerprint)
    if existing:
        num = existing["number"]
        _gh_api(
            "POST",
            f"/repos/{GH_OWNER}/{GH_REPO}/issues/{num}/comments",
            {"body": f"🔁 **再次触发** `{_now()}`\n\n{body}"},
        )
        print(f"[notify] 已在既有 Issue #{num} 追加记录")
        return True
    labels = ["auto-alert", f"severity:{level.lower()}"]
    created = _gh_api(
        "POST",
        f"/repos/{GH_OWNER}/{GH_REPO}/issues",
        {
            "title": f"{LEVEL_EMOJI.get(level, '')} [{level}] {title}",
            "body": full_body,
            "labels": labels,
        },
    )
    if created:
        print(f"[notify] 已创建 Issue #{created.get('number')}")
        return True
    return False


def resolve_github_issue(fingerprint: str, note: str = "") -> bool:
    if not GH_TOKEN:
        return False
    existing = _find_issue(fingerprint)
    if not existing:
        print(f"[notify] 无对应开启中的 Issue（fp={fingerprint}），无需关闭")
        return False
    num = existing["number"]
    _gh_api(
        "POST",
        f"/repos/{GH_OWNER}/{GH_REPO}/issues/{num}/comments",
        {"body": f"✅ **已恢复** `{_now()}`\n\n{note or '自动化闭环确认故障消除，自动关闭。'}"},
    )
    _gh_api(
        "PATCH",
        f"/repos/{GH_OWNER}/{GH_REPO}/issues/{num}",
        {"state": "closed", "state_reason": "completed"},
    )
    print(f"[notify] 已自动关闭 Issue #{num}")
    return True


# --------------------------------------------------------------------------
# 出口 2：Webhook（飞书 / 企业微信 / Slack / Discord 自适应）
# --------------------------------------------------------------------------
def send_webhook(level: str, title: str, body: str) -> bool:
    if not WEBHOOK:
        return False
    text = f"{LEVEL_EMOJI.get(level, '')} [{level}] {title}\n\n{body[:1500]}"
    if "feishu" in WEBHOOK or "larksuite" in WEBHOOK:
        payload = {"msg_type": "text", "content": {"text": text}}
    elif "weixin" in WEBHOOK or "qyapi" in WEBHOOK:
        payload = {"msgtype": "text", "text": {"content": text}}
    elif "discord" in WEBHOOK:
        payload = {"content": text[:1900]}
    else:  # Slack 及通用
        payload = {"text": text}
    try:
        req = urllib.request.Request(
            WEBHOOK,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "aishield-notify"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"[notify] Webhook 送达 HTTP {r.status}")
            return 200 <= r.status < 300
    except Exception as e:
        print(f"[notify] Webhook 发送失败: {e}")
        return False


# --------------------------------------------------------------------------
# 出口 3：本地落盘（永远执行，审计轨迹）
# --------------------------------------------------------------------------
def append_log(record: Dict[str, Any]) -> None:
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ALERT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------
# 冷却控制
# --------------------------------------------------------------------------
def _load_cooldown() -> Dict[str, str]:
    if COOLDOWN_FILE.exists():
        try:
            return json.loads(COOLDOWN_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_cooldown(d: Dict[str, str]) -> None:
    COOLDOWN_FILE.parent.mkdir(parents=True, exist_ok=True)
    COOLDOWN_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def _in_cooldown(fp: str, hours: int) -> bool:
    d = _load_cooldown()
    last = d.get(fp)
    if not last:
        return False
    try:
        t = datetime.fromisoformat(last)
        return (datetime.now(timezone.utc) - t).total_seconds() < hours * 3600
    except Exception:
        return False


# --------------------------------------------------------------------------
# 主入口
# --------------------------------------------------------------------------
def notify(
    level: str,
    title: str,
    body: str,
    fingerprint: Optional[str] = None,
    cooldown_hours: int = DEFAULT_COOLDOWN_HOURS,
    force: bool = False,
) -> bool:
    fp = _fingerprint(title, fingerprint)
    record = {
        "ts": _now(),
        "level": level,
        "title": title,
        "body": body[:2000],
        "fingerprint": fp,
        "channels": [],
    }

    if not force and level != "P0" and _in_cooldown(fp, cooldown_hours):
        record["skipped"] = "cooldown"
        append_log(record)
        print(f"[notify] fp={fp} 处于冷却期，跳过外发（仍已落盘）")
        return False

    delivered = False
    if level in ("P0", "P1"):
        if send_github_issue(level, title, body, fp):
            record["channels"].append("github-issue")
            delivered = True
    if level == "P0" or not delivered:
        if send_webhook(level, title, body):
            record["channels"].append("webhook")
            delivered = True

    record["delivered"] = delivered
    append_log(record)

    cd = _load_cooldown()
    cd[fp] = _now()
    _save_cooldown(cd)

    if not delivered and level in ("P0", "P1"):
        print(f"[notify] ⚠️ {level} 告警未能外发！仅落盘。请配置 NOTIFY_WEBHOOK 或确保 GITHUB_TOKEN 可用。")
    return delivered


def resolve(fingerprint: str, title: str = "", note: str = "") -> bool:
    ok = resolve_github_issue(fingerprint, note)
    if WEBHOOK:
        send_webhook("P2", f"✅ 已恢复：{title or fingerprint}", note or "自动化闭环确认故障消除。")
    append_log(
        {"ts": _now(), "level": "RESOLVED", "title": title, "fingerprint": fingerprint, "note": note}
    )
    cd = _load_cooldown()
    cd.pop(fingerprint, None)
    _save_cooldown(cd)
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 通知总线")
    ap.add_argument("--level", default="P1", choices=["P0", "P1", "P2"])
    ap.add_argument("--title", default="")
    ap.add_argument("--body", default="")
    ap.add_argument("--fingerprint", default=None)
    ap.add_argument("--cooldown", type=int, default=DEFAULT_COOLDOWN_HOURS)
    ap.add_argument("--force", action="store_true", help="忽略冷却期强制发送")
    ap.add_argument("--resolve", action="store_true", help="标记恢复并关闭对应 Issue")
    args = ap.parse_args()

    if args.resolve:
        if not args.fingerprint:
            print("--resolve 必须提供 --fingerprint", file=sys.stderr)
            return 2
        resolve(args.fingerprint, args.title, args.body)
        return 0

    if not args.title:
        print("--title 不能为空", file=sys.stderr)
        return 2
    notify(args.level, args.title, args.body, args.fingerprint, args.cooldown, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
