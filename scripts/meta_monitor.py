#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 元监控 (Meta-Monitor)：监控自动化体系本身
==================================================
评估报告的第一性问题：**14 个 workflow，没有一个在监控这 14 个。**
于是 self-heal 的语法错误潜伏 48 天无人察觉，日报误报 4 天无人纠正，
台账写着"28 个任务运行中"而调度器里实际只有 1 条记录。

自动化体系一旦无人监督，就会从"帮你干活"退化成"假装在干活"，
而且退化过程完全静默 —— 这比彻底宕机更危险。

本模块的检查项：
  M1 语法有效性   —— 所有 workflow 能否被 Actions 正常解析（含 needs 依赖链）
  M2 运行活性     —— 定时任务是否真的在按 cron 执行（对比预期频率与实际记录）
  M3 静默失败     —— 各状态域归属的 workflow 是否按期成功执行（状态文件为 CI 运行时产物，不入库，故以运行活性为准）
  M4 台账一致性   —— 文档声称的任务数 vs 实际存在的 workflow 数
  M5 闭环完整性   —— 每个闭环 workflow 是否具备"检测→动作→验证→告警"四个环节
  M6 告警可达性   —— 通知总线是否具备至少一个可用出口

用法：
    python scripts/meta_monitor.py
    python scripts/meta_monitor.py --notify   # 发现问题时派单
退出码：0=健康，1=存在严重问题
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import http.client
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
WF_DIR = REPO_ROOT / ".github" / "workflows"

GH_OWNER = os.environ.get("GH_OWNER", "lm203688")
GH_REPO = os.environ.get("GH_REPO", "aishield")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gh(path: str):
    """带分块读取与重试的 GitHub API 调用。

    历史坑：/actions/runs?per_page=100 的响应体较大，某些运行环境里
    urllib 的 `resp.read()` 会抛出 http.client.IncompleteRead 而截断，
    导致本应返回运行记录的调用变成 None —— 监控器随之把 M2/M3 判成
    "无法获取运行记录"（ok=null）而静默放行，等于没监控。改用分块读取
    （循环 read(64k) 直到 EOF）并把瞬时网络错误重试 3 次，确保拿到完整
    JSON，让活性/新鲜度检查真正生效。
    """
    if not GH_TOKEN:
        return None
    url = f"https://api.github.com{path}"
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {GH_TOKEN}")
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("User-Agent", "aishield-meta-monitor")
            with urllib.request.urlopen(req, timeout=60) as r:
                chunks = []
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
                return json.loads(b"".join(chunks).decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(2 * (attempt + 1))
                last_err = e
                continue
            print(f"[meta] GitHub API HTTP 错误 {path}: {e.code}")
            return None
        except (http.client.IncompleteRead, ConnectionError, urllib.error.URLError,
                TimeoutError, OSError) as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
            continue
    print(f"[meta] GitHub API 多次失败 {path}: {last_err}")
    return None


# --------------------------------------------------------------------------
# M1 语法有效性
# --------------------------------------------------------------------------
def check_syntax() -> Dict[str, Any]:
    try:
        out = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "validate_workflows.py"), "--json"],
            capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT),
        )
        data = json.loads(out.stdout or "{}")
        errs = data.get("errors", 0)
        bad = [r["file"] for r in data.get("results", []) if r.get("errors")]
        return {
            "ok": errs == 0,
            "errors": errs,
            "warnings": data.get("warnings", 0),
            "bad_files": bad,
            "detail": "所有 workflow 依赖链合法" if errs == 0
                      else f"{errs} 个错误，涉及 {', '.join(bad)}（这类错误会让 workflow 静默地永不执行）",
        }
    except Exception as e:
        return {"ok": False, "detail": f"校验器执行失败: {e}"}


# --------------------------------------------------------------------------
# M2 运行活性
# --------------------------------------------------------------------------
CRON_MAX_AGE_HOURS = {
    # workflow 文件名 -> 允许的最大静默小时数（约为 cron 周期的 2 倍）
    # 注意：自 2026-09 起，原独立调度的子工作流（data-scan-flywheel /
    # threat-intel-feed / channel-distribution / feature-closed-loop 等）已取消
    # 独立 cron，改为由 closed-loop-spine.yml 每日 03:17 经 uses: 串行编排。
    # 它们不再有"独立运行活性"，故此处只登记真正独立按 cron 运行的工作流，
    # 避免 M2 把"被 spine 吸收的子工作流"误报为静默失效。
    "self-heal-closed-loop.yml": 12,
    # deploy-server 由 closed-loop-spine 每日 03:17 触发（每次必部署），
    # 正常最大静默约 24h+，12h 阈值会造成每日误报；放宽到 30h。
    "deploy-server.yml": 30,
    "ci.yml": 48,
    "meta-monitor.yml": 48,
    "npm-self-heal.yml": 48,
    "stale.yml": 48,
    "closed-loop-spine.yml": 48,
}

# 状态域 -> 归属（写入该域的）workflow 列表。
# 用于 M3：判断"环节是否停摆"不是看本地状态文件是否新鲜
# （状态文件是 CI 运行时产物，从不入库，本地永远是陈旧副本），
# 而是看归属 workflow 近期是否真的成功跑过。
#
# 关键修正（2026-09-08）：自闭环合并进 closed-loop-spine.yml 后，下列子工作流
# 只经 spine 的 uses: 调用执行。GitHub 的 /actions/runs 全局列表**不会**把
# uses: 调用的可复用工作流作为独立条目返回（仅 ci/deploy-server/
# unified-security-scan 等仍留有独立触发，才会出现）。因此直接用子工作流
# 文件名判活性会恒定误报"stale"。修正方案：把被 spine 吸收的状态域，在归属
# 列表末尾补上 closed-loop-spine.yml 作为可靠归属——spine 自身确实出现在全局
# runs 列表里，且每日成功运行即代表这些环节都已跑通。
DOMAIN_OWNERS = {
    "health": ["self-heal-closed-loop.yml", "deploy-server.yml"],
    "selfheal": ["self-heal-closed-loop.yml", "deploy-server.yml"],
    "distribution": ["channel-distribution.yml", "closed-loop-spine.yml"],
    "intel": ["threat-intel-feed.yml", "closed-loop-spine.yml"],
    "rules": ["threat-intel-feed.yml", "rule-promoter.yml", "closed-loop-spine.yml"],
    "flywheel": ["data-scan-flywheel.yml", "closed-loop-spine.yml"],
    "feature": ["feature-closed-loop.yml", "closed-loop-spine.yml"],
    "meta": ["meta-monitor.yml"],
    "registry": ["publish-mcp-registry.yml", "publish-npm.yml"],
    "ci": ["ci.yml"],
}
# 状态域 -> 允许的最大静默小时数（取归属 workflow 中最严格的阈值）。
DOMAIN_MAX_AGE_HOURS = {
    "health": 12, "selfheal": 12, "distribution": 336, "intel": 96,
    "rules": 96, "flywheel": 96, "feature": 336, "meta": 48,
    # registry = 发布动作（publish-mcp-registry / publish-npm），发版事件驱动，
    # 非定时任务；两次发版间隔数周属正常，不应按 336h 判停摆。
    "registry": 1440, "ci": 48,
}

_LATEST_RUNS_CACHE: Dict[str, Dict[str, Any]] | None = None


def _monitored_workflows() -> List[str]:
    """M2/M3 需要判活的所有 workflow 文件名（去重）。"""
    names = set(CRON_MAX_AGE_HOURS)
    for owners in DOMAIN_OWNERS.values():
        names.update(owners)
    return sorted(n for n in names if (WF_DIR / n).exists())


def _get_latest_runs() -> Dict[str, Dict[str, Any]]:
    """获取各 workflow 最近一次运行记录（带缓存，M2/M3 共用，避免重复调 API）。

    两级查询（2026-09-08 修正）：先从全局 /actions/runs?per_page=100 提取；
    但该窗口在高频 push（状态总线每次提交都触发 CI）下只覆盖约 2 天，
    低频事件驱动型 workflow（如 publish-mcp-registry / publish-npm，
    仅发版时运行）会整体缺席，导致 M3 把"只是最近没发版"误判为"停摆"。
    故对全局列表里缺席的受监 workflow，逐个补查其专属
    /workflows/<file>/runs?per_page=1 端点（结论以该端点为准）。
    """
    global _LATEST_RUNS_CACHE
    if _LATEST_RUNS_CACHE is not None:
        return _LATEST_RUNS_CACHE
    runs = _gh(f"/repos/{GH_OWNER}/{GH_REPO}/actions/runs?per_page=100")
    latest: Dict[str, Dict[str, Any]] = {}
    if runs:
        for r in runs.get("workflow_runs", []):
            wf = (r.get("path") or "").split("/")[-1]
            if wf not in latest:
                latest[wf] = {"at": r.get("run_started_at"),
                              "conclusion": r.get("conclusion"),
                              "status": r.get("status")}
    # 二级补查：缺席的受监 workflow 用专属端点兜底
    for wf in _monitored_workflows():
        if wf in latest:
            continue
        data = _gh(f"/repos/{GH_OWNER}/{GH_REPO}/actions/workflows/{wf}/runs?per_page=1")
        wr = (data or {}).get("workflow_runs") or []
        if wr:
            latest[wf] = {"at": wr[0].get("run_started_at"),
                          "conclusion": wr[0].get("conclusion"),
                          "status": wr[0].get("status")}
        else:
            # 明确登记"从未运行"，与网络失败区分开
            latest[wf] = {"at": None, "conclusion": None, "status": None}
    _LATEST_RUNS_CACHE = latest
    return latest


def check_liveness() -> Dict[str, Any]:
    if not GH_TOKEN:
        return {"ok": None, "detail": "无 GITHUB_TOKEN，跳过运行活性检查"}
    latest = _get_latest_runs()
    if not latest:
        return {"ok": None, "detail": "无法获取运行记录"}

    now = datetime.now(timezone.utc)
    silent, failing = [], []
    for wf, max_age in CRON_MAX_AGE_HOURS.items():
        if not (WF_DIR / wf).exists():
            continue
        info = latest.get(wf)
        if not info or not info.get("at"):
            silent.append({"workflow": wf, "reason": "从未运行过（极可能解析失败）"})
            continue
        try:
            t = datetime.fromisoformat(info["at"].replace("Z", "+00:00"))
            age = (now - t).total_seconds() / 3600
            if age > max_age:
                silent.append({"workflow": wf, "reason": f"已静默 {age:.0f} 小时（阈值 {max_age}h）"})
        except Exception:
            pass
        if info.get("conclusion") == "failure":
            failing.append(wf)

    return {
        "ok": not silent and not failing,
        "silent": silent,
        "failing": failing,
        "detail": "所有定时任务按期执行且最近一次均成功" if not silent and not failing
                  else f"{len(silent)} 个任务超期未执行，{len(failing)} 个最近运行失败 —— 这是静默失效的典型信号",
    }


# --------------------------------------------------------------------------
# M3 静默失败（状态总线陈旧）
# --------------------------------------------------------------------------
def check_state_freshness() -> Dict[str, Any]:
    """M3 静默失败检测。

    旧实现读 data/state/<domain>.json 的 updated 时间戳判新鲜度，但该文件是 CI
    运行时产物：workflow 写后 `git add data/state/ && git commit ... || echo skipped`，
    并发 push 冲突被 `|| echo` 吞掉，仓库里从未真正入库（git ls-files = 0），
    本地副本永远是 08-04 的陈旧快照 —— 据此判分会产生恒定的假 degraded。

    正确信号：状态域归属的 workflow 近期是否真的成功跑过（与 M2 同源的运行活性）。
    无 token（本地）时跳过，与 M2/M6 一致，避免本地永远亮红灯。
    """
    if not GH_TOKEN:
        return {"ok": None,
                "detail": "本地无 token；状态文件为 CI 运行时产物，新鲜度以 CI 内运行活性（M2）为准，本地不判红"}
    latest = _get_latest_runs()
    if not latest:
        return {"ok": None, "detail": "无法获取运行记录，跳过状态新鲜度检查"}

    now = datetime.now(timezone.utc)
    stale = []
    for domain, owners in DOMAIN_OWNERS.items():
        if not (WF_DIR / owners[0]).exists():
            continue
        fresh = False
        for wf in owners:
            info = latest.get(wf)
            if not info or not info.get("at"):
                continue
            try:
                t = datetime.fromisoformat(info["at"].replace("Z", "+00:00"))
                age = (now - t).total_seconds() / 3600
                # 近期运行且结论为成功（或尚未得出结论）才算新鲜；
                # 仅"最近跑过"但失败，仍视为该环节已停摆。
                if age <= DOMAIN_MAX_AGE_HOURS.get(domain, 336) and info.get("conclusion") in (None, "success"):
                    fresh = True
                    break
            except Exception:
                pass
        if not fresh:
            stale.append(domain)
    return {
        "ok": not stale,
        "stale": stale,
        "detail": "所有状态域的归属 workflow 均按期成功执行" if not stale
                  else f"状态域 {stale} 的归属 workflow 超过阈值未成功运行 —— 对应环节可能已停摆",
    }


# --------------------------------------------------------------------------
# M4 台账一致性
# --------------------------------------------------------------------------
def check_ledger() -> Dict[str, Any]:
    reg = REPO_ROOT / "automation" / "task-registry.md"
    actual = len(list(WF_DIR.glob("*.yml"))) + len(list(WF_DIR.glob("*.yaml")))
    if not reg.exists():
        return {"ok": True, "actual": actual, "detail": f"无台账文件，实际 workflow {actual} 个"}
    text = reg.read_text(encoding="utf-8", errors="replace")
    claims = [int(m) for m in re.findall(r"(\d+)\s*个(?:定时)?任务", text)]
    claimed = max(claims) if claims else None
    if claimed and abs(claimed - actual) > 3:
        return {
            "ok": False,
            "claimed": claimed,
            "actual": actual,
            "detail": f"台账声称 {claimed} 个任务，实际仅 {actual} 个 workflow —— 台账失真会误导所有后续决策",
        }
    return {"ok": True, "claimed": claimed, "actual": actual, "detail": "台账与实际基本一致"}


# --------------------------------------------------------------------------
# M5 闭环完整性
# --------------------------------------------------------------------------
LOOP_WORKFLOWS = [
    "self-heal-closed-loop.yml",
    "feature-closed-loop.yml",
    "channel-distribution.yml",
    "data-scan-flywheel.yml",
    "threat-intel-feed.yml",
]


def check_loop_integrity() -> Dict[str, Any]:
    incomplete = []
    for name in LOOP_WORKFLOWS:
        p = WF_DIR / name
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        has_detect = bool(re.search(r"probe|health|scan|fetch|triage|collect", text, re.I))
        has_action = bool(re.search(r"deploy|publish|commit|repair|submit", text, re.I))
        has_verify = bool(re.search(r"verify|validate|test|assert|health_probe", text, re.I))
        has_alert = bool(re.search(r"notify\.py|issues:\s*write|escalate", text, re.I))
        missing = [
            n for n, ok in [
                ("检测", has_detect), ("动作", has_action),
                ("验证", has_verify), ("告警", has_alert),
            ] if not ok
        ]
        if missing:
            incomplete.append({"workflow": name, "missing": missing})
    return {
        "ok": not incomplete,
        "incomplete": incomplete,
        "detail": "所有闭环具备 检测→动作→验证→告警 四环节" if not incomplete
                  else f"{len(incomplete)} 个闭环缺环节，链条会在缺口处断开",
    }


# --------------------------------------------------------------------------
# M6 告警可达性
# --------------------------------------------------------------------------
def check_alert_reachability() -> Dict[str, Any]:
    outlets = []
    if GH_TOKEN:
        outlets.append("github-issue")
    if os.environ.get("NOTIFY_WEBHOOK"):
        outlets.append("webhook")

    in_ci = os.environ.get("GITHUB_ACTIONS") == "true"

    if outlets:
        return {"ok": True, "outlets": outlets,
                "detail": f"可用告警出口: {', '.join(outlets)}"}

    if not in_ci:
        # 本地跑不带 GITHUB_TOKEN 是常态，CI 内由 Actions 自动注入。
        # 这里若判红，会变成一条永远亮着的假警报，久而久之整个面板就没人看了。
        return {"ok": None, "outlets": [],
                "detail": "本地环境无 token（属正常）；告警出口的有效性以 CI 内检查为准"}

    return {"ok": False, "outlets": [],
            "detail": "CI 中无任何可用告警出口 —— 告警将只能落盘，等同于没有告警"}


CHECKS = [
    ("M1 语法有效性", check_syntax),
    ("M2 运行活性", check_liveness),
    ("M3 状态新鲜度", check_state_freshness),
    ("M4 台账一致性", check_ledger),
    ("M5 闭环完整性", check_loop_integrity),
    ("M6 告警可达性", check_alert_reachability),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 元监控")
    ap.add_argument("--notify", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results: Dict[str, Any] = {}
    problems: List[str] = []

    for label, fn in CHECKS:
        try:
            r = fn()
        except Exception as e:
            r = {"ok": False, "detail": f"检查异常: {e}"}
        results[label] = r
        if r.get("ok") is False:
            problems.append(f"{label}: {r.get('detail')}")

    checked = [r for r in results.values() if r.get("ok") is not None]
    passed = sum(1 for r in checked if r.get("ok"))
    score = round(passed / len(checked) * 100) if checked else 0
    level = ("healthy" if score >= 90 else
             "degraded" if score >= 60 else
             "critical" if score >= 30 else "down")

    if args.json:
        print(json.dumps({"score": score, "level": level, "results": results,
                          "problems": problems}, ensure_ascii=False, indent=2))
    else:
        print(f"自动化体系自检得分：{passed}/{len(checked)}（{score}% / {level}）")
        print("=" * 64)
        for label, r in results.items():
            mark = "✅" if r.get("ok") else ("❌" if r.get("ok") is False else "➖")
            print(f"{mark} {label}")
            print(f"     {r.get('detail', '')}")
        if problems:
            print("\n" + "=" * 64)
            print("需处理问题：")
            for p in problems:
                print(f"  · {p}")

    try:
        from scripts.state_bus import StateBus

        StateBus().set(
            "meta",
            {"score": score, "level": level, "passed": passed, "total": len(checked),
             "problems": problems, "checked_at": _now()},
            source="meta_monitor",
        )
    except Exception as e:
        print(f"[warn] 状态回写失败: {e}")

    if args.notify:
        try:
            from scripts.notify import notify, resolve

            if problems:
                body = f"自动化体系自检得分 **{score}%**（{passed}/{len(checked)}）\n\n发现以下问题：\n\n"
                for p in problems:
                    body += f"- {p}\n"
                body += "\n> 元监控的价值：自动化失效往往是静默的，不主动检查就永远不会发现。"
                notify("P1", f"元监控发现 {len(problems)} 项自动化体系问题", body,
                       "meta-monitor-issues", cooldown_hours=24)
            else:
                resolve("meta-monitor-issues", "自动化体系恢复健康",
                        f"元监控全部 {len(checked)} 项检查通过。")
        except Exception as e:
            print(f"[warn] 通知失败: {e}")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
