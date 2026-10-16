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
import base64
import hashlib
import hmac
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
ALERT_LOG = REPO_ROOT / "data" / "state" / "alerts.jsonl"
COOLDOWN_FILE = REPO_ROOT / "data" / "state" / "alert_cooldown.json"
# 未送达台账：P0/P1 告警发出失败时追加到这里。
# 它的存在本身就是可观测信号 —— 「告警链路自己挂了」这件事不再靠人工翻日志，
# 任何健康检查读这个文件就能知道。空文件/不存在 = 链路健康。
UNDELIVERED_LOG = REPO_ROOT / "data" / "state" / "undelivered_alerts.jsonl"

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
# 出站脱敏（redaction）—— 告警正文会离开本机，进入 GitHub Issue 和第三方
# IM 机器人（飞书/企微/Slack/Discord）。告警正文里常常粘着扫描 finding 原文，
# 而 finding 的 evidence 字段就是「触发规则的那一行源代码」—— 硬编码 API key
# 那条规则的 evidence 字面上就是一个 API key。不脱敏等于把凭据主动群发出去。
#
# 脱敏必须在**所有**出口生效（Issue body 和 webhook payload），不能只挡一个。
# 顺序敏感：先抹掉具体凭据形状，再抹掉泛化的 key=value，最后抹邮箱/IP。
# --------------------------------------------------------------------------
REDACT_REPLACEMENT = "[REDACTED]"

REDACT_PATTERNS: List[tuple] = [
    # 1) 高置信具体形状：整值抹掉
    (re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"), REDACT_REPLACEMENT),          # GitHub token
    (re.compile(r"glpat-[A-Za-z0-9\-]{20,}"), REDACT_REPLACEMENT),             # GitLab PAT
    (re.compile(r"sk_live_[A-Za-z0-9_\-]{8,}|sk_test_[A-Za-z0-9_\-]{8,}"), REDACT_REPLACEMENT),
    (re.compile(r"sk-[A-Za-z0-9_\-]{16,}"), REDACT_REPLACEMENT),                  # OpenAI / 通用 sk-
    (re.compile(r"xox[bpras]-[A-Za-z0-9\-]{10,}"), REDACT_REPLACEMENT),        # Slack token
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,}"), REDACT_REPLACEMENT),  # JWT
    (re.compile(r"AKIA[0-9A-Z]{16}"), REDACT_REPLACEMENT),                     # AWS access key
    (re.compile(r"Bearer\s+[A-Za-z0-9._\-]{16,}"), "Bearer " + REDACT_REPLACEMENT),
    # 2) 泛化 key=value / "key": "value"
    #    值字符集必须排除方括号 —— 否则 [REDACTED] 本身会被当成新的值再次匹配，
    #    导致脱敏不幂等（同一段文本跑两遍会多出一个 ] ）。
    (re.compile(
        r"(?i)\b(api[_-]?key|apikey|access[_-]?token|refresh[_-]?token|auth[_-]?token"
        r"|secret|client_secret|password|passwd|pwd|token)\b"
        r"(\s*[=:]\s*)(\"[^\"]{4,}\"|'[^']{4,}'|[^\s,;{}\[\]]{4,})"
    ), lambda m: "%s%s%s" % (m.group(1), m.group(2), REDACT_REPLACEMENT)),
    # 3) 连接串里的 user:pass@
    (re.compile(r"(?i)\b([a-z][a-z0-9+]*://)[^\s:]+:([^\s@]+)@"), r"\1[REDACTED]:[REDACTED]@"),
    # 4) 邮箱
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), REDACT_REPLACEMENT),
]


def redact(text: str) -> str:
    """抹掉出站文本里的凭据。幂等：脱敏后的文本再跑一遍不变。

    绝不 raise —— 脱敏失败不能把告警一起丢掉，但返回原文时必须能被测试发现，
    所以调用方对"疑似仍含凭据"的情况走单独的校验。
    """
    if not text:
        return text
    out = text
    for pattern, repl in REDACT_PATTERNS:
        out = pattern.sub(repl, out)
    return out


def looks_redacted(text: str) -> bool:
    """自否证用：文本里还残留高置信凭据形状吗？

    脱敏是正则近似，不是完备证明。这个函数给调用方一个"我尽力了"的显式信号，
    而不是假装绝对安全。
    """
    if not text:
        return True
    for pattern, _repl in REDACT_PATTERNS[:8]:
        if pattern.search(text):
            return False
    return True


# 出站 webhook 签名：设置 NOTIFY_WEBHOOK_SIGNING_SECRET 后，给飞书/企微/Slack/Discord
# 的自定义中转（不是平台原生 webhook）一个可验证来源的凭据。平台原生 webhook
# 会忽略未知头，所以加头是无损的。
SIGNING_SECRET = os.environ.get("NOTIFY_WEBHOOK_SIGNING_SECRET", "")


def sign_payload(secret: str, body: bytes) -> str:
    """HMAC-SHA256，格式 `sha256=<hex>`，与 GitHub/Slack 事件签名约定一致。"""
    return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


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
    # 脱敏必须覆盖 Issue 出口 —— Issue 在公开仓库，且可能被第三方索引。
    # 历史上这里漏过一次：只脱敏了 webhook，Issue body 里的 evidence 原文照发。
    body = redact(body)
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
    # 先脱敏再截断：反过来的话截断可能把脱敏边界切掉，留下半条凭据。
    text = f"{LEVEL_EMOJI.get(level, '')} [{level}] {title}\n\n{redact(body)[:1500]}"
    if "feishu" in WEBHOOK or "larksuite" in WEBHOOK:
        payload = {"msg_type": "text", "content": {"text": text}}
    elif "weixin" in WEBHOOK or "qyapi" in WEBHOOK:
        payload = {"msgtype": "text", "text": {"content": text}}
    elif "discord" in WEBHOOK:
        payload = {"content": text[:1900]}
    else:  # Slack 及通用
        payload = {"text": text}
    raw = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "aishield-notify"}
    if SIGNING_SECRET:
        headers["X-AIShield-Signature"] = sign_payload(SIGNING_SECRET, raw)
    try:
        req = urllib.request.Request(
            WEBHOOK,
            data=raw,
            headers=headers,
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
# 未送达台账 —— 告警链路的「自身故障」必须可观测
#
# 此前 P0/P1 外发失败只 print 一句警告，然后 return False，而 main() 恒 return 0。
# 这就是「打印结论 ≠ 传出结论」：告警链路本身挂了，CI 显示绿色，没人知道。
# 台账把这个静默失败变成一行可读的磁盘状态，健康检查直接 count 即可。
# --------------------------------------------------------------------------
def _rewrite_undelivered(items: List[Dict[str, Any]]) -> None:
    UNDELIVERED_LOG.parent.mkdir(parents=True, exist_ok=True)
    UNDELIVERED_LOG.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items),
        encoding="utf-8",
    )


def record_undelivered(record: Dict[str, Any]) -> None:
    """按 fingerprint 去重写入（upsert）—— 台账是「待处理集合」，不是事件日志。

    重复追加有两个实害：
      1. 台账无限膨胀，重试失败一项就多一行，越堆越大；
      2. `retry_undelivered` 的「全部成功才清空」判断失真 —— 重试时 notify()
         又会写一条，len 永远对不上，台账永远清不掉。

    事件级的追加轨迹由 append_log 负责（alerts.jsonl），这里只维护当前待处理项。
    重复触发时累加 `attempts`，健康检查能看到「这条告警已经重试过几次」。
    """
    fp = record.get("fingerprint")
    existing = undelivered_records()
    for i, rec in enumerate(existing):
        if fp and rec.get("fingerprint") == fp:
            existing[i] = {
                **rec,
                "ts": record.get("ts") or rec.get("ts"),
                "attempts": int(rec.get("attempts", 0)) + 1,
            }
            _rewrite_undelivered(existing)
            return
    existing.append(record)
    _rewrite_undelivered(existing)


def undelivered_records() -> List[Dict[str, Any]]:
    if not UNDELIVERED_LOG.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in UNDELIVERED_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def clear_undelivered() -> int:
    """清空台账，返回清掉几条。仅由重试成功后调用。"""
    if not UNDELIVERED_LOG.exists():
        return 0
    n = len(undelivered_records())
    UNDELIVERED_LOG.write_text("", encoding="utf-8")
    return n


def retry_undelivered(level: str = "P0") -> int:
    """重放台账里的未送达告警（强制绕过冷却），全部成功后清空台账。

    形成闭环：告警丢失 -> 落台账 -> 有人或 cron 调 retry -> 清台账。
    没有这一步，台账只积累不消费，最终变成又一处死重。
    返回：成功重放条数。
    """
    items = undelivered_records()
    if not items:
        print("[notify] 无未送达告警待重试")
        return 0
    succeeded = 0
    for rec in items:
        title = rec.get("title") or rec.get("fingerprint") or "未命名告警"
        body = rec.get("body") or ""
        fp = rec.get("fingerprint") or None
        if notify(level, title, body, fp, force=True):
            succeeded += 1
            print(f"[notify] 重放成功: {title}")
        else:
            print(f"[notify] 重放仍失败: {title}（保留在台账）")
    if succeeded == len(items):
        clear_undelivered()
    return succeeded


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
        record["undelivered"] = True
        record_undelivered(record)
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
    ap.add_argument("--retry-undelivered", action="store_true",
                    help="重放未送达台账中的历史告警，全部成功后清空台账")
    ap.add_argument("--fail-on-undelivered", action="store_true",
                    help="P0/P1 未送达时返回非零退出码（fail-closed）。"
                         "默认关闭以保持既有 workflow 行为不变")
    args = ap.parse_args()

    if args.resolve:
        if not args.fingerprint:
            print("--resolve 必须提供 --fingerprint", file=sys.stderr)
            return 2
        resolve(args.fingerprint, args.title, args.body)
        return 0

    if args.retry_undelivered:
        items = undelivered_records()
        if not items:
            print("[notify] 未送达台账为空，无需重试")
            return 0
        succeeded = retry_undelivered(args.level)
        if succeeded == len(items):
            return 0
        print(f"[notify] {len(items) - succeeded}/{len(items)} 条重放仍失败，保留在台账",
              file=sys.stderr)
        return 4

    if not args.title:
        print("--title 不能为空", file=sys.stderr)
        return 2

    delivered = notify(args.level, args.title, args.body, args.fingerprint,
                       args.cooldown, args.force)
    if not delivered and args.level in ("P0", "P1"):
        if args.fail_on_undelivered:
            print("[notify] --fail-on-undelivered: P0/P1 未送达，返回非零退出码",
                  file=sys.stderr)
            return 3
        # 不 fail-closed 也必须把状态显式说出来 —— 静默 return 0 就是本次要修的假绿。
        print("[notify] ⚠️ 告警未送达（已记入未送达台账）。"
              "加 --fail-on-undelivered 可让 CI 变红；用 --retry-undelivered 可重放。",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
