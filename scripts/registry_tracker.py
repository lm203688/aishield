#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 生态位上架追踪器 (Registry / Distribution Tracker)
==========================================================
评估报告的核心结论：AIShield 卡位的 4 个关键生态位（Agent CA、中国合规网关、
CI/CD 卡口、被调用的安全数据源）代码完成度均超 80%，**挡住变现的不是技术，
而是 npm publish / registry submit / Marketplace 上架这几个从未执行的发布动作。**

本模块把"是否已上架"从主观判断变成**可探测的客观事实**：
  - 真实请求各生态目录，确认 AIShield 是否可被检索到
  - 未上架项自动生成待办，并通过通知总线升级为可执行任务
  - 状态写入状态总线，供元监控与周报消费

追踪的生态位：
  1. npm registry      —— @aishield/mcp-scanner 是否已发布（Agent 可直接 npx 调用）
  2. MCP Registry      —— 官方 modelcontextprotocol registry 收录
  3. GitHub Topics     —— 仓库是否打上可被检索的 topic
  4. GitHub Pages      —— 内容站是否已上线
  5. API 可用性        —— 作为"被调用的安全数据源"，端点是否对外可用

用法：
    python scripts/registry_tracker.py --check
    python scripts/registry_tracker.py --check --notify
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

GH_OWNER = os.environ.get("GH_OWNER", "lm203688")
GH_REPO = os.environ.get("GH_REPO", "aishield")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""

PKG_JSON = REPO_ROOT / "mcp-server" / "package.json"


def _pkg_field(field: str, fallback: str) -> str:
    """从 package.json 读取字段。

    这里刻意不硬编码包名：曾经硬编码成 @aishield/mcp-scanner，
    而真实包名是 aishield-mcp-server —— 追踪器于是长期在
    查询一个根本不存在的包，「未发布」这条待办从一开始就查错了对象。
    单一事实来源 = package.json 本身。
    """
    try:
        raw = PKG_JSON.read_text(encoding="utf-8-sig")
        return json.loads(raw).get(field) or fallback
    except Exception:
        return fallback


NPM_PKG = os.environ.get("NPM_PKG") or _pkg_field("name", "aishield-mcp-server")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ctx() -> ssl.SSLContext:
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c


def _get(url: str, headers: Dict[str, str] | None = None, timeout: int = 20):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "aishield-tracker"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


# --------------------------------------------------------------------------
# 各生态位探测
# --------------------------------------------------------------------------
def check_npm() -> Dict[str, Any]:
    code, body = _get(f"https://registry.npmjs.org/{NPM_PKG.replace('/', '%2F')}")
    if code == 200:
        try:
            d = json.loads(body)
            latest = (d.get("dist-tags") or {}).get("latest", "?")
            return {
                "listed": True,
                "version": latest,
                "detail": f"已发布 v{latest}，Agent 可直接 npx 调用",
            }
        except Exception:
            return {"listed": True, "detail": "已发布（版本解析失败）"}
    return {
        "listed": False,
        "detail": f"{NPM_PKG} 未在 npm 发布（HTTP {code}）",
        "action": "执行 npm publish —— 这是 Agent 能'直接用上'AIShield 的最短路径",
        "priority": "P1",
    }


def check_mcp_registry() -> Dict[str, Any]:
    # 官方 registry 检索
    code, body = _get("https://registry.modelcontextprotocol.io/v0/servers?limit=100")
    if code == 200 and "aishield" in body.lower():
        return {"listed": True, "detail": "已被 MCP 官方 registry 收录"}
    if code == 200:
        return {
            "listed": False,
            "detail": "MCP 官方 registry 可访问，但未检索到 aishield",
            "action": "向 modelcontextprotocol/registry 提交 server.json —— 生态入口即用户入口",
            "priority": "P1",
        }
    return {
        "listed": False,
        "detail": f"registry 探测失败 (HTTP {code})",
        "action": "确认 registry 端点后重试提交",
        "priority": "P2",
    }


def check_github_topics() -> Dict[str, Any]:
    if not GH_TOKEN:
        return {"listed": None, "detail": "无 token，跳过 topics 检查"}
    code, body = _get(
        f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/topics",
        {
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "aishield-tracker",
        },
    )
    if code == 200:
        try:
            names = json.loads(body).get("names", [])
        except Exception:
            names = []
        wanted = {"mcp", "ai-agent", "security", "mcp-server", "ai-security"}
        missing = sorted(wanted - set(names))
        if not missing:
            return {"listed": True, "detail": f"topics 完备: {', '.join(names)}"}
        return {
            "listed": False,
            "detail": f"当前 topics: {names or '无'}；缺少 {missing}",
            "action": f"补齐 GitHub topics: {', '.join(missing)} —— 零成本获取平台内检索流量",
            "priority": "P2",
        }
    return {"listed": None, "detail": f"topics 查询失败 HTTP {code}"}


def check_pages() -> Dict[str, Any]:
    url = f"https://{GH_OWNER}.github.io/{GH_REPO}/blog/"
    code, _ = _get(url)
    if code == 200:
        return {"listed": True, "detail": f"内容站已上线 {url}"}
    return {
        "listed": False,
        "detail": f"内容站不可达 (HTTP {code}) {url}",
        "action": "在仓库 Settings → Pages 开启 GitHub Pages（Source: main /docs）",
        "priority": "P1",
    }


def check_api_datasource() -> Dict[str, Any]:
    code, body = _get("https://aishield.tools/api/v1/health")
    if code == 200:
        return {"listed": True, "detail": "安全数据源 API 对外可用"}
    return {
        "listed": False,
        "detail": f"API 不可达 (HTTP {code})",
        "action": "触发自愈闭环恢复服务",
        "priority": "P0",
    }


CHECKS = {
    "npm": ("npm 包分发（Agent 直接调用入口）", check_npm),
    "mcp_registry": ("MCP 官方 Registry 收录", check_mcp_registry),
    "github_topics": ("GitHub Topics 检索曝光", check_github_topics),
    "pages": ("内容站 GitHub Pages", check_pages),
    "api": ("被调用的安全数据源 API", check_api_datasource),
}


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 生态位上架追踪器")
    ap.add_argument("--check", action="store_true", default=True)
    ap.add_argument("--notify", action="store_true", help="有未上架项时通过通知总线派单")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results: Dict[str, Any] = {}
    todos: List[Dict[str, str]] = []

    for key, (label, fn) in CHECKS.items():
        try:
            r = fn()
        except Exception as e:
            r = {"listed": None, "detail": f"探测异常: {e}"}
        r["label"] = label
        results[key] = r
        if r.get("listed") is False and r.get("action"):
            todos.append(
                {
                    "niche": label,
                    "action": r["action"],
                    "priority": r.get("priority", "P2"),
                }
            )

    listed = sum(1 for r in results.values() if r.get("listed") is True)
    total = sum(1 for r in results.values() if r.get("listed") is not None)
    coverage = round(listed / total * 100) if total else 0

    if args.json:
        print(json.dumps({"coverage": coverage, "results": results, "todos": todos},
                         ensure_ascii=False, indent=2))
    else:
        print(f"生态位上架覆盖率：{listed}/{total}（{coverage}%）")
        print("=" * 60)
        for key, r in results.items():
            mark = "✅" if r.get("listed") is True else ("❌" if r.get("listed") is False else "➖")
            print(f"{mark} {r['label']}")
            print(f"     {r.get('detail', '')}")
            if r.get("action"):
                print(f"     → 待办[{r.get('priority')}]: {r['action']}")
        if todos:
            print("\n" + "=" * 60)
            print(f"共 {len(todos)} 个生态位待上架 —— 这些是变现路径上的实际阻塞点。")

    # 状态回写
    try:
        from scripts.state_bus import StateBus

        StateBus().set(
            "registry",
            {
                "coverage_pct": coverage,
                "listed": listed,
                "total": total,
                "todos": todos,
                "checked_at": _now(),
            },
            source="registry_tracker",
        )
    except Exception as e:
        print(f"[warn] 状态回写失败: {e}")

    if args.notify and todos:
        try:
            from scripts.notify import notify

            body = f"生态位上架覆盖率 **{coverage}%**（{listed}/{total}）。以下生态位尚未打通，直接阻塞变现：\n\n"
            for t in todos:
                body += f"- **[{t['priority']}] {t['niche']}**\n  {t['action']}\n"
            body += "\n> 评估结论：这些生态位的代码完成度均超 80%，缺的只是发布动作本身。"
            notify("P1", f"生态位上架待办 {len(todos)} 项", body, "registry-todos", cooldown_hours=72)
        except Exception as e:
            print(f"[warn] 通知失败: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
