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
  M7 上游情报源   —— OSV / NVD / GitHub Advisory 是否真的可用（情报库有无停更）
  M8 雷达情报源   —— Tech Radar 的 github/arxiv/hn/reddit/standards/platforms 是否可用
  M9 雷达规则效果 —— 已晋升的雷达规则是否真的命中攻击、是否误伤良性输入
  M10 监控覆盖面  —— 有独立 cron 的 workflow 是否都在受监清单内（元监控自检）

用法：
    python scripts/meta_monitor.py
    python scripts/meta_monitor.py --notify   # 发现问题时派单
退出码：0=健康，1=存在严重问题
"""

from __future__ import annotations

import argparse
import base64
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
    # deploy-server.yml 不在本清单：它已无独立 cron，仅由 spine 经
    # `uses: ./.github/workflows/deploy-server.yml` 调用（见 spine 第 64 行）。
    # GitHub **不会**把 uses: 调用登记进被调 workflow 自己的 runs 列表（实测
    # deploy-server 自身最后一次 schedule 停在 08-31），因此用它的运行记录判活
    # 必然误报"静默"。部署环节的活性正确判据 = spine 本次运行成功（spine 已登记，
    # 且其 deploy job 失败会使 spine 整体 conclusion=failure → 仍能捕获真实故障）。
    "ci.yml": 48,
    "meta-monitor.yml": 48,
    "npm-self-heal.yml": 48,
    "stale.yml": 48,
    "closed-loop-spine.yml": 48,
    # 【2026-10-05 补】它每天 09:20 UTC 独立运行（另含 push 触发），却一直不在
    # 任何受监清单里 —— 每天在跑、坏了没人知道。之所以长期没被发现，是因为它
    # 既不在 CRON_MAX_AGE_HOURS，也不在 spine 的编排里，两边都以为对方在管。
    # 现在由 M10「监控覆盖面」把这类遗漏变成显式红灯，不再靠人记得。
    "geo-indexnow-submit.yml": 48,
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
    # distribution 域有**两个**写入者：channel-distribution（分发动作）与
    # geo-indexnow-submit（收录提交，见其 state_bus.py set distribution）。
    # 原先只登记了前者，于是收录链路的活性从来没被真正判过。
    "distribution": ["channel-distribution.yml", "closed-loop-spine.yml",
                     "geo-indexnow-submit.yml"],
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
                  else f"{len(silent)} 个任务超期未执行，{len(failing)} 个最近运行失败"
                       + (f"（{'、'.join(failing)}）" if failing else "")
                       + " —— 这是静默失效的典型信号",
    }


# --------------------------------------------------------------------------
# M3 静默失败（状态总线陈旧）
# --------------------------------------------------------------------------
def _common_failed_owner(stale: List[str], latest: Dict[str, Dict[str, Any]]):
    """在被判 stale 的域里找**共同的失败归属** workflow —— 把「N 个故障」收敛成「1 个根因」。

    【2026-10-05 事故】spine 的 job 2 失败时，体检报
    「状态域 ['distribution','intel','rules','flywheel','feature'] 停摆」——
    读起来是 5 个环节各自出了问题，实际这 5 个域的归属列表里都含
    closed-loop-spine.yml，真正要修的只有 1 处（打开 spine 看它在哪个 job 断的）。

    面板的职责不只是「报出异常」，还要把异常归到**可操作的最小根因**上：
    报 5 个故障会让人去逐个排查 5 个子系统，归因粒度错了，诊断成本放大一个量级。

    只在某个失败归属覆盖 >= 2 个 stale 域时才点出（单域的情况 detail 已说清）。
    """
    hits: Dict[str, List[str]] = {}
    for domain in stale:
        for wf in DOMAIN_OWNERS.get(domain, []):
            info = latest.get(wf) or {}
            if not info.get("at"):
                continue
            if info.get("conclusion") == "failure":
                hits.setdefault(wf, []).append(domain)
    if not hits:
        return None
    wf, domains = max(hits.items(), key=lambda kv: len(kv[1]))
    if len(domains) < 2:
        return None
    return wf, domains


def check_state_freshness() -> Dict[str, Any]:
    """M3 静默失败检测。

    旧实现读 data/state/<domain>.json 的 updated 时间戳判新鲜度，但该文件是 CI
    运行时产物：workflow 写后 `git add data/state/ && git commit ... || echo skipped`，
    并发 push 冲突被 `|| echo` 吞掉，仓库里从未真正入库（git ls-files = 0），
    本地副本永远是 08-04 的陈旧快照 —— 据此判分会产生恒定的假 degraded。

    现改为**双信号**，缺一不可：

    （甲）运行活性：状态域归属的 workflow 近期是否真的成功跑过（与 M2 同源）。
          无 token（本地）时跳过，与 M2/M6 一致，避免本地永远亮红灯。
    （乙）状态落地：**直接**读 data/state/<domain>.json 的 updated 与阈值比。

    为什么必须补回（乙）：2026-09-08 把(甲)改成"归属列表末尾挂 spine"之后，
    每个域的归属里都有每日 spine，于是只要 spine 绿，(甲)就**恒判新鲜** ——
    2026-10-06 实测 spine 每轮 success，而 feature 状态域冻结 63 天、
    rules 冻结 32 天（一个 artifact 路径写错被 `|| true` 吞、一个漏进 git add）。
    只判(甲)等于给"链路在跑、状态没落地"这种空转发永久绿灯，而它正是本函数
    存在的唯一理由。两种失效形状不同，必须分别判。
    无 token（本地）时(乙)不读文件：本地副本恒陈旧，读了只有固定假红。
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

    # ── 第二信号：状态文件**自己的** updated 时间戳 ──────────────────
    # 上面那段判的是"归属 workflow 跑没跑"。但每个域的归属列表末尾都挂了
    # 每日 spine，于是只要 spine 绿，M3 就**恒判新鲜** —— 2026-10-06 实测：
    # spine 每轮 success，而 data/state/feature.json 已冻结 63 天、
    # data/state/rules.json 冻结 32 天。两个都是真缺陷，机制却相反：
    #   ① feature：artifact 多路径上传按仓库相对结构落盘，
    #      `cp /tmp/agg/feature.json ... || true` 天天失败被吞，只提交了 ROADMAP.md；
    #   ② rules：restore 成功，但 job 的 `git add` 名单里漏了 data/state/rules.json。
    # "在跑"与"在写"是两件事，必须分别判；只判前者就是给空转发绿灯。
    # 只在 CI（有 token、checkout 即最新）里读文件：本地副本恒是陈旧快照，
    # 读了只会产生固定假红（见本函数 docstring 的历史教训）。
    stale_files: List[str] = []
    state_dir = REPO_ROOT / "data" / "state"
    for domain in DOMAIN_OWNERS:
        p = state_dir / f"{domain}.json"
        if not p.exists():
            continue  # 未落盘的域（如 flywheel）由上面的运行活性那一路覆盖
        try:
            ts = (json.loads(p.read_text(encoding="utf-8")) or {}).get("updated")
            if not ts:
                continue
            t_file = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            if t_file.tzinfo is None:
                t_file = t_file.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        hrs = (now - t_file).total_seconds() / 3600
        if hrs > DOMAIN_MAX_AGE_HOURS.get(domain, 336):
            stale_files.append(f"{domain}({hrs / 24:.0f}d)")

    detail = ("所有状态域的归属 workflow 均按期成功执行" if not stale
              else f"状态域 {stale} 的归属 workflow 超过阈值未成功运行 —— 对应环节可能已停摆")
    if stale_files:
        detail += (f"；且状态文件自身超期未刷新：{'、'.join(stale_files)}"
                   f" —— 链路在跑但状态没落地（artifact 路径/git add 名单是首要嫌疑）")
    root = _common_failed_owner(stale, latest)
    if root:
        wf, domains = root
        detail += (f"；共同根因：{wf} 最近一次运行失败，{len(domains)} 个域共用该归属"
                   f"（{'、'.join(domains)}）—— 先修这一处，不必逐个排查各子系统")
    return {
        "ok": not stale and not stale_files,
        "stale": stale,
        "stale_files": stale_files,
        "root_cause": (root[0] if root else None),
        "detail": detail,
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


# --------------------------------------------------------------------------
# M7 上游情报源健康
# --------------------------------------------------------------------------
INTEL_DB_PATH = "data/threat_intel.json"
INTEL_MAX_SILENT_HOURS = 72     # 情报库超过 3 天未成功更新 → 视为停更
SOURCE_FAIL_THRESHOLD = 2       # 单源连续失败 >= 2 次才判 degraded（放过单次抖动）


def check_intel_sources() -> Dict[str, Any]:
    """M7 上游数据源健康（OSV / NVD / GitHub Advisory）。

    补的洞：fetch_vuln_feeds 旧版把每源异常 print 掉就完事，既不记状态也不
    告警，更糟的是三个源全挂仍 exit 0 —— 情报库停更而流程全绿。现在采集端
    已逐源留痕（source_health），本检查负责把它纳入体系体检。

    为什么必须读**远端**副本：data/threat_intel.json 由 CI 提交，本地工作区
    是 08-04 的陈旧快照（与 M3 同一个坑），据本地文件判分会产生恒定假 degraded。

    判据（本地无 token 时跳过，与 M2/M3/M6 一致）：
      · 任一源连续失败 >= 2 次           → 上游长期不可用
      · 情报库 last_success 超过 72h     → 情报停更
    升级前的老数据（无 source_health 字段）不判红，避免误伤。
    """
    if not GH_TOKEN:
        return {"ok": None,
                "detail": "本地无 token；上游源健康以 CI 内采集结果为准，本地不判红"}
    meta = _gh(f"/repos/{GH_OWNER}/{GH_REPO}/contents/{INTEL_DB_PATH}?ref=main")
    if not isinstance(meta, dict) or not meta.get("content"):
        return {"ok": None, "detail": "无法读取远端情报库，跳过上游源健康检查"}
    try:
        db = json.loads(base64.b64decode(meta["content"]).decode("utf-8"))
    except Exception as e:
        return {"ok": None, "detail": f"远端情报库解析失败，跳过检查: {e}"}

    block = db.get("source_health")
    if not isinstance(block, dict):
        return {"ok": None, "detail": "情报库尚无 source_health 字段（升级前数据），跳过"}

    now = datetime.now(timezone.utc)
    bad: List[str] = []
    srcs = block.get("sources") if isinstance(block.get("sources"), dict) else {}
    for name, h in srcs.items():
        if not isinstance(h, dict):
            continue
        try:
            n = int(h.get("consecutive_failures") or 0)
        except Exception:
            n = 0
        if h.get("ok") is False and n >= SOURCE_FAIL_THRESHOLD:
            bad.append(f"{name} 连续 {n} 次失败")

    stale_hours = None
    ls = block.get("last_success")
    if ls:
        try:
            t = datetime.fromisoformat(str(ls).replace("Z", "+00:00"))
            stale_hours = (now - t).total_seconds() / 3600
        except Exception:
            stale_hours = None
    if stale_hours is not None and stale_hours > INTEL_MAX_SILENT_HOURS:
        bad.append(f"情报库已 {stale_hours:.0f}h 未成功更新")

    if bad:
        return {"ok": False, "detail": "上游情报源异常：" + "；".join(bad)}

    ok_n = sum(1 for h in srcs.values() if isinstance(h, dict) and h.get("ok"))
    fresh = f"{stale_hours:.0f}h 前更新" if stale_hours is not None else "更新时间未知"
    return {"ok": True, "detail": f"上游情报源健康（{ok_n}/{len(srcs)} 正常），情报库 {fresh}"}


# --------------------------------------------------------------------------
# M8 雷达情报源健康
# --------------------------------------------------------------------------
RADAR_STATE_PATH = "data/state/tech_radar.json"
RADAR_FAIL_THRESHOLD = 3       # 单源连续失败 >= 3 次（约 3 天）才判 degraded


def check_radar_sources() -> Dict[str, Any]:
    """M8 雷达情报源健康（github / arxiv / hn / reddit / standards / platforms）。

    对称的洞：M7 只覆盖 fetch_vuln_feeds 的 OSV/NVD/GitHub Advisory，而 Tech
    Radar 的 6 个源（尤其 Reddit）此前没有任何健康监控。实测 Reddit 连续 12 天
    HTTP -1（本机出口不可达），却因聚合 errors=4 < 阈值而 Permanent 绿——典型
    的"源挂了但流程全绿"。tech_radar 现已逐源留痕 source_health（并随
    --publish 推到远端），本检查把它纳入体系体检，与 M7 同构。

    判据（无 token / 远端无 state / 无 source_health 时跳过，与 M7 一致）：
      · 任一源连续失败 >= 3 次（约 3 天）→ 该源长期不可用
    """
    if not GH_TOKEN:
        return {"ok": None,
                "detail": "本地无 token；雷达源健康以 CI 内采集结果为准，本地不判红"}
    meta = _gh(f"/repos/{GH_OWNER}/{GH_REPO}/contents/{RADAR_STATE_PATH}?ref=main")
    if not isinstance(meta, dict) or not meta.get("content"):
        return {"ok": None, "detail": "无法读取远端雷达状态，跳过雷达源健康检查"}
    try:
        st = json.loads(base64.b64decode(meta["content"]).decode("utf-8"))
    except Exception as e:
        return {"ok": None, "detail": f"远端雷达状态解析失败，跳过检查: {e}"}

    health = st.get("source_health")
    if not isinstance(health, dict):
        return {"ok": None, "detail": "雷达状态尚无 source_health 字段，跳过"}

    bad: List[str] = []
    blocked: List[str] = []
    for name, h in health.items():
        if not isinstance(h, dict):
            continue
        try:
            n = int(h.get("consecutive_failures") or 0)
        except Exception:
            n = 0
        if n < RADAR_FAIL_THRESHOLD:
            continue
        if h.get("known_blocked"):
            # 结构性不可达（如 reddit 在本机出口）——仍计数但不升级，与
            # tech_radar._degraded_sources 同一判据，避免每天重复报同一个
            # 救不了的故障（噪声淹没真信号）。
            blocked.append(f"{name} 已知不可达 {n} 次")
        else:
            bad.append(f"{name} 连续 {n} 次失败")

    if bad:
        return {"ok": False, "detail": "雷达情报源异常：" + "；".join(bad)}

    ok_n = sum(1 for h in health.values()
               if isinstance(h, dict)
               and int(h.get("consecutive_failures", 0) or 0) == 0)
    tail = ("；已知不可达（不升级）：" + "；".join(blocked)) if blocked else ""
    return {"ok": True,
            "detail": f"雷达情报源健康（{ok_n}/{len(health)} 正常）{tail}"}


# --------------------------------------------------------------------------
# M9 雷达规则效果
# --------------------------------------------------------------------------
RADAR_EFFECT_PATH = "data/state/radar_effect.json"


def check_radar_effect() -> Dict[str, Any]:
    """M9 雷达规则效果（晋升的规则是否真的有效 / 是否误报）。

    补的洞：promote->effect 的最后一环此前完全缺失 —— 晋升进 data/radar_rules.json
    的规则，既没人验证它真能命中攻击文本，也没人复查它是否误伤良性输入。一条在良性
    语料上误报的规则比没有规则更糟（见 promote_rule.py 的注释）。radar_effect 现在
    逐条衡量 catch（正样本命中）与 false_positive（良性误报），rule-promoter 晋升后
    刷新并提交该状态；本检查把它纳入体系体检。

    判据（无 token / 远端无状态 / 无已晋升规则时跳过，与 M7/M8 一致）：
      · 任一已晋升规则在良性语料上误报 → 规则本身是缺陷，判红
      （"零命中"只作信息展示：正样本语料有限，缺命中不等于规则无效，不判红。）
    """
    if not GH_TOKEN:
        return {"ok": None,
                "detail": "本地无 token；雷达规则效果以 CI 内评估为准，本地不判红"}
    meta = _gh(f"/repos/{GH_OWNER}/{GH_REPO}/contents/{RADAR_EFFECT_PATH}?ref=main")
    if not isinstance(meta, dict) or not meta.get("content"):
        return {"ok": None, "detail": "无法读取远端雷达效果状态，跳过规则效果检查"}
    try:
        eff = json.loads(base64.b64decode(meta["content"]).decode("utf-8"))
    except Exception as e:
        return {"ok": None, "detail": f"远端雷达效果状态解析失败，跳过检查: {e}"}

    rules = eff.get("rules") if isinstance(eff.get("rules"), dict) else {}
    if not rules:
        return {"ok": None, "detail": "尚无已晋升雷达规则，跳过效果检查"}

    fp = [p for p, r in rules.items() if isinstance(r, dict) and r.get("false_positive")]
    if fp:
        return {"ok": False,
                "detail": "已晋升雷达规则在良性语料上误报：" +
                          "；".join(f"{p} -> {(rules[p].get('fp_sample') or '')[:40]}" for p in fp[:3])}

    catch_n = sum(1 for r in rules.values() if isinstance(r, dict) and r.get("catch"))
    return {"ok": True,
            "detail": f"雷达规则效果正常（{len(rules)} 条，{catch_n} 条命中正样本，零误报）"}


# --------------------------------------------------------------------------
# M10 监控覆盖面（元监控自检：我有没有漏监控）
# --------------------------------------------------------------------------
def check_monitor_coverage() -> Dict[str, Any]:
    """M10 监控覆盖面：有独立 cron 的 workflow 必须全部被本模块判活。

    补的洞（2026-10-05 实测）：geo-indexnow-submit.yml 每天 09:20 独立运行，
    却既不在 CRON_MAX_AGE_HOURS / DOMAIN_OWNERS 里，也不在 spine 的编排里 ——
    **每天在跑，坏了没人知道**。

    这是静默失效的最深处：M2~M9 的前提都是「这个环节已被纳入监控」，而这里的
    问题是「这个环节根本不在监控范围内」—— 连「有东西坏了」这个信号本身都不存在。
    上面所有检查做得再好，也照不到监控范围之外的空白。

    同时校验归属清单里的**文件名真实存在**：写错一个文件名会被
    _monitored_workflows 的存在性过滤静默丢掉，于是某个域的活性判据悄悄少一个
    来源 —— 判据变弱却毫无提示。判据弱化本身也是一种静默失效。
    """
    declared = set(CRON_MAX_AGE_HOURS)
    for owners in DOMAIN_OWNERS.values():
        declared.update(owners)

    missing_files = sorted(n for n in declared if not (WF_DIR / n).exists())
    if missing_files:
        return {
            "ok": False,
            "missing_files": missing_files,
            "detail": f"受监清单引用了不存在的 workflow：{missing_files} —— 该归属会被"
                      f"静默过滤掉，对应环节的判活依据会悄悄少一个来源",
        }

    if yaml is None:
        return {"ok": None, "detail": "无 PyYAML，跳过监控覆盖面检查"}

    scheduled: List[str] = []
    for p in sorted(WF_DIR.glob("*.yml")):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        on = data.get("on", data.get(True))
        if isinstance(on, dict) and on.get("schedule"):
            scheduled.append(p.name)

    uncovered = sorted(n for n in scheduled if n not in declared)
    if uncovered:
        return {
            "ok": False,
            "uncovered": uncovered,
            "detail": f"{uncovered} 有独立 cron 却不在受监清单里 —— 每天在跑但坏了"
                      f"没人知道（两边都以为对方在管）",
        }
    return {"ok": True,
            "detail": f"所有独立调度的 workflow（{len(scheduled)} 个）均已被监控覆盖"}


CHECKS = [
    ("M1 语法有效性", check_syntax),
    ("M2 运行活性", check_liveness),
    ("M3 状态新鲜度", check_state_freshness),
    ("M4 台账一致性", check_ledger),
    ("M5 闭环完整性", check_loop_integrity),
    ("M6 告警可达性", check_alert_reachability),
    ("M7 上游情报源", check_intel_sources),
    ("M8 雷达情报源", check_radar_sources),
    ("M9 雷达规则效果", check_radar_effect),
    ("M10 监控覆盖面", check_monitor_coverage),
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
