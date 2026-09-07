# -*- coding: utf-8 -*-
"""
基线漂移扫描模块（Baseline / Definition Pinning）

借鉴来源（2026-09-07 开源扫描）:
    - HeadyZhang/agent-audit: --save-baseline / --baseline 增量扫描工作流
    - AgentAvow/mcp-security-scan (agentgraph.co): tool-definition pinning
      with drift detection —— 被审计过的定义事后被改 = rug-pull（CVE-2025-54136
      Cursor mcp.json rug-pull 类）
    - Snyk agent-scan + mcp-security-scan: Toxic Flow（致命三要素）
      = 私有数据访问 + 不可信内容 + 对外通信 三者齐聚同一工具
    - veloxlabsio/mcp-scan: fail-closed —— 解析失败产出 finding 而非空报告

设计哲学（与全库一致）:
    - 纯标准库（hashlib/json/re），零第三方依赖，零网络
    - 凭证一律脱敏：env 只记 键名，绝不记 值
    - 定义级钉扎与 rug_pull.py 的 commit-diff 分析互补：
      rug_pull 看仓库历史；baseline 看你审计那一刻的定义本身，
      对非 git 部署、跨机配置同样有效。

用法:
    from scanner.baseline_scan import build_baseline, check_drift, detect_toxic_flows

    # 第一次扫描: 钉扎
    baseline = build_baseline(files)
    # 之后每次: 比对
    result = check_drift(files, baseline)
    result["findings"]  # changed(critical) / added / removed
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List
BASELINE_VERSION = 1

# ---- 信号识别（脱敏：只看键名，不看值） ----
_SECRET_KEY_RE = re.compile(
    r"(API[_-]?KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)", re.I
)
_REMOTE_CONTENT_RE = re.compile(r"\b(fetch|browse|scrape|crawl|reader|web)\b", re.I)
_URL_IN_ARGS_RE = re.compile(r"https?://", re.I)
_URL_FIELDS = ("url", "endpoint", "server_url", "base_url", "host")
_PRIVATE_PATH_RE = re.compile(r"(~|\bhome\b|\bdocuments\b|\busers\b|\bdesktop\b|\.ssh|\.aws|\.git)", re.I)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def _canonical_definition(entry: Dict[str, Any]) -> str:
    """从 mcpServers 条目提取稳定定义（env 只取键名，值一律丢弃）。"""
    env = entry.get("env") or {}
    if not isinstance(env, dict):
        env = {}
    stable = {
        "command": entry.get("command"),
        "args": entry.get("args"),
        "type": entry.get("type"),
        "transport": entry.get("transport"),
        "url": entry.get("url") or entry.get("endpoint"),
        "env_keys": sorted(str(k) for k in env.keys()),
    }
    return json.dumps(stable, sort_keys=True, ensure_ascii=False)


def definition_fingerprints(files: Dict[str, str]) -> Dict[str, str]:
    """
    从扫描文件集合提取定义级指纹。

    覆盖:
      - 任何含 mcpServers 的 .json / .yml / .yaml  → 逐服务器指纹
      - SKILL.md / *.skill.md                      → 整文件指纹
      - agent-card.json / server-card.json         → 逐工具指纹

    Returns:
        {definition_key: sha256}
    """
    fps: Dict[str, str] = {}
    if not isinstance(files, dict):
        return fps

    for fname, content in files.items():
        if not isinstance(content, str) or not content.strip():
            continue
        lower = fname.lower()

        # 1) SKILL.md / 技能文件：整文件钉扎
        if lower.endswith("skill.md") or lower.endswith(".skill.md"):
            key = f"skill:{fname}"
            fps[key] = _sha256(content)
            continue

        # 2) JSON/YAML 配置：尝试解析 mcpServers / tools
        if lower.endswith((".json", ".yml", ".yaml")):
            parsed = None
            if lower.endswith(".json"):
                try:
                    parsed = json.loads(content)
                except Exception:
                    parsed = None

            servers = None
            if isinstance(parsed, dict):
                servers = parsed.get("mcpServers") or parsed.get("servers")

            if isinstance(servers, dict) and servers:
                for sname, entry in servers.items():
                    if not isinstance(entry, dict):
                        continue
                    key = f"mcp:{fname}:{sname}"
                    fps[key] = _sha256(_canonical_definition(entry))
                continue

            # agent-card / server-card 的 tools 数组
            tools = None
            if isinstance(parsed, dict):
                tools = parsed.get("tools")
            if isinstance(tools, list) and tools:
                for t in tools:
                    if isinstance(t, dict) and t.get("name"):
                        key = f"tool:{fname}:{t['name']}"
                        fps[key] = _sha256(
                            json.dumps(t, sort_keys=True, ensure_ascii=False)
                        )
                continue

            # 其他结构化配置文件：整文件钉扎（fail-closed 姿态：宁可多钉）
            if lower.endswith(".json"):
                fps[f"config:{fname}"] = _sha256(content)

    return fps


def _finding(ftype: str, severity: str, desc: str, file: str) -> Dict[str, Any]:
    return {"type": ftype, "severity": severity, "description": desc, "file": file}


def check_drift(
    files: Dict[str, str], baseline: Dict[str, Any]
) -> Dict[str, Any]:
    """
    比对当前定义指纹与基线，产出漂移 findings。

    语义（借鉴 agentgraph pinning）:
      - changed: 审计过的定义被改写 → critical（rug-pull 类）
      - added:   出现审计时不存在的新定义 → medium
      - removed: 定义消失 → medium
      - baseline 本身非法/为空 → fail-closed 产出 error finding
    """
    out: Dict[str, Any] = {
        "module": "baseline_scan",
        "findings": [],
        "baseline_valid": bool(
            isinstance(baseline, dict)
            and baseline.get("version") == BASELINE_VERSION
            and isinstance(baseline.get("definitions"), dict)
        ),
        "checked_at": _now_iso(),
    }
    if not out["baseline_valid"]:
        out["findings"].append(
            _finding(
                "baseline_invalid",
                "high",
                "基线文件缺失或格式非法 —— 无法判定定义是否被篡改（fail-closed，不默认通过）",
                "baseline",
            )
        )
        return out

    base_defs: Dict[str, str] = baseline["definitions"]
    current = definition_fingerprints(files)

    for key, old_hash in base_defs.items():
        if key not in current:
            out["findings"].append(
                _finding(
                    "baseline_removed",
                    "medium",
                    f"定义 '{key}' 在基线中存在但已从当前配置消失",
                    key,
                )
            )
        elif current[key] != old_hash:
            out["findings"].append(
                _finding(
                    "baseline_drift_changed",
                    "critical",
                    f"定义 '{key}' 与审计基线不一致 —— 已被修改"
                    "（rug-pull 特征：审计后篡改命令/参数/URL/env）",
                    key,
                )
            )
    for key in current.keys() - base_defs.keys():
        out["findings"].append(
            _finding(
                "baseline_added",
                "medium",
                f"出现基线之外的新定义 '{key}'（未经过审计）",
                key,
            )
        )
    return out


def build_baseline(files: Dict[str, str]) -> Dict[str, Any]:
    """钉扎当前定义集合，返回可持久化的基线（JSON 兼容）。"""
    return {
        "version": BASELINE_VERSION,
        "generated_at": _now_iso(),
        "tool": "aishield-baseline",
        "definitions": definition_fingerprints(files),
        "note": "审计通过后保存本文件；下次扫描用 check_drift(files, baseline) 比对",
    }


def detect_toxic_flows(files: Dict[str, str]) -> Dict[str, Any]:
    """
    致命三要素（lethal trifecta）组合检测 —— 配置级数据流启发式。

    三要素（同一 mcpServers 条目内）:
      PRIVATE    : env 中存在凭证键名 / args 指向用户私有路径
      UNTRUSTED  : 服务本身处理外部不可信内容（fetch/browse/scrape/crawl/web）
      OUTBOUND   : 存在对外通信面（url 字段 / args 含 URL / curl|wget）

    判定: 三者齐聚 = critical；任意两者 = medium；单个信号不报（告警稀缺性）。
    """
    findings: List[Dict[str, Any]] = []
    if not isinstance(files, dict):
        return {"module": "toxic_flow", "findings": findings}

    for fname, content in files.items():
        if not isinstance(content, str) or not content.strip():
            continue
        if not fname.lower().endswith((".json", ".yml", ".yaml")):
            continue
        try:
            parsed = json.loads(content) if fname.lower().endswith(".json") else None
        except Exception:
            parsed = None
        if not isinstance(parsed, dict):
            continue
        servers = parsed.get("mcpServers") or parsed.get("servers")
        if not isinstance(servers, dict):
            continue

        for sname, entry in servers.items():
            if not isinstance(entry, dict):
                continue
            command = str(entry.get("command") or "")
            args_list = entry.get("args") or []
            args_text = " ".join(str(a) for a in args_list) if isinstance(args_list, list) else str(args_list)
            env = entry.get("env") if isinstance(entry.get("env"), dict) else {}
            env_keys = [str(k) for k in env.keys()]

            private = bool(
                any(_SECRET_KEY_RE.search(k) for k in env_keys)
                or _PRIVATE_PATH_RE.search(args_text)
            )
            untrusted = bool(
                _REMOTE_CONTENT_RE.search(command)
                or _REMOTE_CONTENT_RE.search(sname)
                or _REMOTE_CONTENT_RE.search(args_text)
            )
            outbound = bool(
                entry.get("url")
                or entry.get("endpoint")
                or _URL_IN_ARGS_RE.search(args_text)
                or re.search(r"\b(curl|wget)\b", command)
            )

            signals = [s for s, on in (
                ("private-data", private),
                ("untrusted-content", untrusted),
                ("outbound-channel", outbound),
            ) if on]

            if len(signals) >= 3:
                findings.append(_finding(
                    "toxic_flow_trifecta",
                    "critical",
                    f"MCP 服务器 '{sname}' 齐聚致命三要素"
                    f"（{' + '.join(signals)}）—— 私有数据可被拉入处理上下文并外传"
                    "（GitLost 类数据外泄链），建议拆分或加出网白名单",
                    fname,
                ))
            elif len(signals) == 2:
                findings.append(_finding(
                    "toxic_flow_pair",
                    "medium",
                    f"MCP 服务器 '{sname}' 同时具备 {' + '.join(signals)}"
                    "（致命三要素缺一），请确认是否必要",
                    fname,
                ))
            # 单信号不报 —— 告警稀缺性红线

    return {"module": "toxic_flow", "findings": findings}


def baseline_scan(
    files: Dict[str, str], baseline: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    一站式入口：
      - baseline=None → 返回新基线（钉扎模式）
      - baseline 给定 → 返回漂移 findings（比对模式）
    另附 toxic flow 检测结果（无状态，每次都跑）。
    """
    toxic = detect_toxic_flows(files)
    if baseline is None:
        return {
            "mode": "pin",
            "baseline": build_baseline(files),
            "toxic_flow": toxic,
        }
    drift = check_drift(files, baseline)
    return {"mode": "check", "drift": drift, "toxic_flow": toxic}
