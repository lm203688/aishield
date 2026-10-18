"""
Agent 基础设施开源扫描管道（scan_pipeline.py, v4.8.2）

围绕 AIShield 核心目标，对 agent 基础设施类开源项目做多维度、多层次的构建：

  1. 平台开源扫描   — 复用 scanner.engine（OWASP MCP Top10 静态 + 依赖 + 密钥 + 评分）
  2. 封装           — 为目标生成 MCP 适配器骨架，把被扫项目快速接成 AIShield 可治理的 tool
  3. 二次研发       — 依据扫描 findings 生成「二次研发清单」（治理加固项）

输入三态（零依赖、可离线）：
  - repo_url       : GitHub 仓库地址 → 在线扫描（scanner.engine.scan）
  - local_path     : 本地目录       → 离线扫描（读取文件后走 engine 底层分析）
  - files          : 内存文件字典   → 离线扫描（测试/CI 友好，确定性）

registry 集成：传 platform_id 时从 eco.platform_registry 取 name / access_paths / family。
"""

import os
import json
import re
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))

# ── 已知 agent 基础设施目标（registry id → 默认 tool_type）──
# repo_url 由调用方显式传入，避免硬编码可能失效的地址。
KNOWN_AGENT_INFRA = {
    "laya": {"tool_type": "mcp", "note": "本地决策/护栏模型，可作治理护栏后端"},
    "nasiko": {"tool_type": "mcp", "note": "agent 基础设施"},
    "agent-desktop": {"tool_type": "mcp", "note": "桌面 agent 基础设施"},
    "nvidia-dev": {"tool_type": "native_sdk", "note": "NVIDIA 开发者平台 NGC/NIM/NeMo"},
}

_SCANNER_VERSION = "4.0"


def _safe_import_engine():
    """延迟导入 scanner.engine，避免耦合。"""
    import scanner.engine as engine
    return engine


def resolve_target(spec):
    """把多种形式的 spec 规整为统一 target 字典。

    spec 可为：
      {"platform_id": "laya"}
      {"name": "x", "repo_url": "https://github.com/o/r"}
      {"name": "x", "local_path": "/abs/path"}
      {"name": "x", "files": {"a.py": "..."}}
    返回 {name, tool_type, repo_url, local_path, files, platform_id, source_mode, family, access_paths, note}
    """
    if not isinstance(spec, dict):
        raise ValueError("spec must be a dict")

    platform_id = spec.get("platform_id")
    name = spec.get("name")
    repo_url = spec.get("repo_url")
    local_path = spec.get("local_path")
    files = spec.get("files")
    tool_type = spec.get("tool_type", "mcp")

    family = None
    access_paths = None
    note = None

    if platform_id:
        try:
            import eco.platform_registry as reg
            p = reg.get_platform(platform_id)
            if p:
                name = name or p.get("name")
                family = p.get("family")
                access_paths = p.get("access_paths")
                note = (KNOWN_AGENT_INFRA.get(platform_id) or {}).get("note")
                tool_type = tool_type if tool_type != "mcp" else (KNOWN_AGENT_INFRA.get(platform_id) or {}).get("tool_type", "mcp")
        except Exception:
            pass
        if not name:
            name = platform_id

    if repo_url:
        source_mode = "online"
    elif local_path or files:
        source_mode = "offline"
    elif platform_id and platform_id in KNOWN_AGENT_INFRA:
        # registry 目标但没给 url/path → 要求补一个
        raise ValueError(
            "platform_id=%s 已登记但缺少 repo_url/local_path/files，请补充其一" % platform_id
        )
    else:
        raise ValueError("spec 必须提供 repo_url / local_path / files 之一，或有效的 platform_id")

    return {
        "name": name or "unnamed-target",
        "tool_type": tool_type,
        "repo_url": repo_url,
        "local_path": local_path,
        "files": files,
        "platform_id": platform_id,
        "source_mode": source_mode,
        "family": family,
        "access_paths": access_paths,
        "note": note,
    }


def _read_local_files(local_path):
    """递归读取本地目录下的源文件为 {rel_path: content}。"""
    files = {}
    skip_dirs = {"node_modules", ".git", "dist", "__pycache__", ".venv", "venv",
                 "vendor", "build", ".next", "target", ".idea", ".tox"}
    exts = (".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml", ".yml",
            ".toml", ".md", ".txt", ".sh", ".env.example", ".cfg", ".ini")
    for root, dirs, fnames in os.walk(local_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fn in fnames:
            if not fn.endswith(exts):
                continue
            full = os.path.join(root, fn)
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as fh:
                    rel = os.path.relpath(full, local_path)
                    files[rel] = fh.read()
            except Exception:
                continue
    return files


def offline_scan(files, tool_type="mcp"):
    """离线扫描：直接用 engine 底层分析函数，避免任何网络依赖。"""
    engine = _safe_import_engine()
    static = engine.rules_analyze(files, tool_type)
    dependency = engine.dependency_analysis(files)
    secrets = engine.secrets_detection(files)
    total_files = len(files)
    scores = engine.calculate_scores(static, dependency, secrets, [], [], total_files)
    findings = []
    for src in (static.get("findings", []), dependency.get("findings", []), secrets.get("findings", [])):
        findings.extend(src)
    recommendations = engine.generate_recommendations(findings, scores)
    return {
        "findings": findings,
        "total_findings": len(findings),
        "scores": scores,
        "recommendations": recommendations,
        "total_files": total_files,
        "dependency_count": dependency.get("total_dependencies", len(dependency.get("dependencies", []))),
    }


def _normalize_engine_report(raw, target):
    """把 engine.scan 的返回规整成统一 report 形状。"""
    findings = raw.get("findings", [])
    # engine.scan 有时把 findings 放在报告顶层或其他键；做一次兜底合并
    for k in ("static_findings", "dependency_findings", "secret_findings"):
        if isinstance(raw.get(k), list):
            findings.extend(raw[k])
    return {
        "findings": findings,
        "total_findings": raw.get("total_findings", len(findings)),
        "scores": raw.get("scores") or raw.get("score_breakdown") or {},
        "recommendations": raw.get("recommendations", []),
        "total_files": raw.get("total_files", 0),
        "dependency_count": raw.get("total_dependencies", raw.get("dependency_count", 0)),
        "overall_score": raw.get("overall_score"),
        "risk_level": raw.get("risk_level"),
        "badge_level": raw.get("badge_level"),
    }


def scan_target(spec, http_post_mock=None):
    """扫描单个 agent-infra 目标，返回统一 report。

    http_post_mock 仅在线模式（engine.scan 内部 fetch）可能用到，这里透传给 engine。
    返回 dict: {target, mode, report, scanned_at, scanner_version, error}
    """
    target = resolve_target(spec)
    scanned_at = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

    try:
        if target["source_mode"] == "online":
            engine = _safe_import_engine()
            kwargs = {"tool_type": target["tool_type"], "name": target["name"]}
            # engine.scan 走网络；本环境 api.github.com 可达，但允许 mock 注入
            raw = engine.scan(target["repo_url"], **kwargs)
            if raw.get("error"):
                return {
                    "target": target, "mode": "online", "error": raw["error"],
                    "scanned_at": scanned_at, "scanner_version": _SCANNER_VERSION,
                    "report": None,
                }
            report = _normalize_engine_report(raw, target)
        else:
            files = target["files"]
            if files is None and target["local_path"]:
                files = _read_local_files(target["local_path"])
            if not files:
                return {
                    "target": target, "mode": "offline", "error": "no files to scan",
                    "scanned_at": scanned_at, "scanner_version": _SCANNER_VERSION, "report": None,
                }
            report = offline_scan(files, target["tool_type"])
    except Exception as e:  # 网络/解析异常降级
        return {
            "target": target, "mode": target["source_mode"],
            "error": "scan failed: %s" % e,
            "scanned_at": scanned_at, "scanner_version": _SCANNER_VERSION, "report": None,
        }

    return {
        "target": target,
        "mode": target["source_mode"],
        "report": report,
        "scanned_at": scanned_at,
        "scanner_version": _SCANNER_VERSION,
        "error": None,
    }


# ────────────────────────────────────────────────────────────
# 封装：MCP 适配器骨架生成
# ────────────────────────────────────────────────────────────

_MCP_ADAPTER_TPL = '''\
"""
AIShield 封装适配器 — <<NAME>>
由 agent_infra.scan_pipeline 自动生成（v<<VERSION>>）。

被扫项目：<<REPO>>
扫描结果：<<TOTAL>> findings / 综合评分 <<SCORE>>（<<RISK>>）
接入路径：<<PATHS>>

本适配器把「<<NAME>>」接成 AIShield 可治理的 MCP tool：
  - 所有动作先经 AIShield 个人 Agent 治理层做预算/风险 preflight
  - 敏感操作触发 block（需人工 override）
  - 行动上链（HMAC 行动账本）供离线审计
"""

import sys
import os

# 走 AIShield 治理层（零依赖）：
#   from connectors.base import preflight_and_record  # 见 personal_agent 集成
#   import eco.personal_agent as pa

SERVER_NAME = "<<SAFE_NAME>>"


def handle(tool_name, arguments, *, user_id, agent_instance_id):
    """统一入口：先治理 preflight，再转发到 <<NAME>> 原生能力。

    模板说明：本函数是 MCP 适配器骨架的占位实现，
    由 build_mcp_adapter_skeleton() 生成时替换 SERVER_NAME 和工具清单。
    实际集成时需：
      1. 调用 AIShield 治理层 preflight（见 eco/personal_agent.py）
      2. 调用目标 MCP server 的原生 API / SDK
    参考实现：connectors/agent_infra/personal_agent.py
    """
    # Step 1: 治理 preflight（owner: @lm203688）
    #   from eco import personal_agent as pa
    #   pf = pa.check_budget_and_risk(
    #       user_id=user_id,
    #       action="mcp.%s" % tool_name,
    #       agent_instance_id=agent_instance_id,
    #   )
    #   if pf.get("verdict") == "block":
    #       return {"ok": False, "blocked": True, "reason": pf.get("reason")}
    #
    # Step 2: 转发到目标 MCP server（owner: 集成方）
    #   在此调用 <<NAME>> 原生 API / SDK，传入 tool_name 和 arguments
    raise NotImplementedError(
        "Implement forwarding to %s. "
        "See docstring for integration steps." % SERVER_NAME)


# 暴露给 AIShield 64-tool MCP server 的工具清单（示例）
TOOLS = [
<<TOOLS>>
]
'''


def build_mcp_adapter_skeleton(result, result_index=0):
    """根据扫描结果生成 MCP 适配器骨架字符串。"""
    target = result.get("target", {})
    report = result.get("report") or {}
    name = target.get("name", "unnamed")
    safe_name = re.sub(r"[^A-Za-z0-9_]", "_", name).strip("_") or "target"
    scores = report.get("scores", {}) or {}
    score = scores.get("overall_score") if isinstance(scores, dict) else None
    risk_level = report.get("risk_level") or _score_to_risk(score)
    access_paths = ", ".join(target.get("access_paths") or ["mcp"])
    repo = target.get("repo_url") or target.get("local_path") or "in-memory files"
    total = report.get("total_findings", 0)

    # 依据 findings 推导候选 tool（封装层暴露的原子能力）
    tools_block = _derive_tools_from_findings(report.get("findings", []))

    return (_MCP_ADAPTER_TPL
            .replace("<<NAME>>", name)
            .replace("<<VERSION>>", _SCANNER_VERSION)
            .replace("<<REPO>>", repo)
            .replace("<<TOTAL>>", str(total))
            .replace("<<SCORE>>", str(score) if score is not None else "n/a")
            .replace("<<RISK>>", risk_level)
            .replace("<<PATHS>>", access_paths)
            .replace("<<SAFE_NAME>>", safe_name)
            .replace("<<TOOLS>>", tools_block))


def _derive_tools_from_findings(findings):
    """从扫描 findings 推导建议暴露的 MCP tool（封装层原子能力）。"""
    if not findings:
        return "    # 暂无 findings；建议先补全被扫项目的 manifest 后再生成 tool 清单"
    cats = {}
    for f in findings:
        c = f.get("type") or f.get("category") or f.get("owasp") or "unknown"
        cats[c] = cats.get(c, 0) + 1
    lines = []
    for i, (c, n) in enumerate(sorted(cats.items(), key=lambda kv: -kv[1]), 1):
        lines.append('    {"name": "%s_guard_%d", "description": "%s 类风险治理 (%d findings)"},'
                     % (re.sub(r"[^A-Za-z0-9_]", "_", str(c)), i, c, n))
    return "\n".join(lines) if lines else "    # 暂无 findings；建议先补全被扫项目的 manifest 后再生成 tool 清单"


def _score_to_risk(score):
    if score is None:
        return "unknown"
    if score >= 85:
        return "low"
    if score >= 70:
        return "medium"
    if score >= 50:
        return "high"
    return "critical"


# ────────────────────────────────────────────────────────────
# 二次研发清单
# ────────────────────────────────────────────────────────────

def build_secondary_rd_checklist(result):
    """依据 findings 生成「二次研发清单」——把每个风险点转成可执行的治理加固项。"""
    report = result.get("report") or {}
    findings = report.get("findings", []) or []
    target = result.get("target", {})
    name = target.get("name", "target")

    checklist = []
    # 1) 按严重度分组，给出加固项
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    for f in sorted(findings, key=lambda x: sev_order.get((x.get("severity") or "info").lower(), 9)):
        sev = (f.get("severity") or "info").lower()
        desc = f.get("description") or f.get("type") or "风险项"
        file_hint = f.get("file") or f.get("location") or "—"
        action = _remediation_for(f)
        checklist.append({
            "severity": sev,
            "title": "加固：%s" % desc,
            "evidence": file_hint,
            "action": action,
            "source": "scan_finding",
        })
    # 2) 治理接入项（与 AIShield 集成必做）
    checklist.append({
        "severity": "governance",
        "title": "为 %s 接入 AIShield 个人 Agent 治理层（预算/风险/HMAC 行动账本）" % name,
        "evidence": "connectors/agent_infra 封装层",
        "action": "在生成适配器的 handle() 内调用 pa.check_budget_and_risk 做 preflight；block 级动作需 override；动作经 record_action 上链。",
        "source": "aishield_integration",
    })
    checklist.append({
        "severity": "governance",
        "title": "把 %s 封装为 AIShield 64-tool MCP server 的一个受治理 tool" % name,
        "evidence": "mcp-server/src/index.ts",
        "action": "在 manifest 注册 aishield_connector_* 类工具，复用 connectors/base.py 的 OAuth/store/secret 机制。",
        "source": "aishield_integration",
    })
    return checklist


def _remediation_for(finding):
    t = (finding.get("type") or finding.get("category") or "").lower()
    desc = finding.get("description") or ""
    if "secret" in t or "token" in t or "credential" in desc.lower():
        return "移除硬编码密钥，改为环境变量 / 密钥管理服务；加入 secret scanning 到 CI。"
    if "injection" in t or "prompt" in t:
        return "对外部输入做结构化校验与沙箱；在治理层对敏感指令触发 block。"
    if "dependency" in t or "package" in t:
        return "固定依赖版本并启用 lockfile；对危险包做替换或隔离。"
    if "auth" in t or "permission" in t:
        return "收紧最小权限；敏感操作要求显式授权与审计。"
    if "ssrf" in t or "url" in t:
        return "对出站 URL 做 SSRF 防护（拒绝内网/私有地址）。"
    return "按 OWASP MCP Top10 对应项加固，并记录到治理行动账本。"


# ────────────────────────────────────────────────────────────
# 组合：组合多个目标成 portfolio 报告
# ────────────────────────────────────────────────────────────

def scan_portfolio(specs, http_post_mock=None):
    """批量扫描多个 agent-infra 目标，聚合为 portfolio 报告。"""
    results = []
    errors = []
    for spec in specs:
        try:
            r = scan_target(spec, http_post_mock=http_post_mock)
            results.append(r)
            if r.get("error"):
                errors.append({"target": spec.get("name") or spec.get("platform_id"), "error": r["error"]})
        except Exception as e:
            errors.append({"target": spec.get("name") or spec.get("platform_id"), "error": str(e)})

    total_findings = sum((r.get("report") or {}).get("total_findings", 0) for r in results)
    scored = [(r.get("report") or {}).get("scores", {}) or {} for r in results]
    avg = None
    valid = [s.get("overall_score") for s in scored if isinstance(s, dict) and isinstance(s.get("overall_score"), (int, float))]
    if valid:
        avg = round(sum(valid) / len(valid), 1)

    return {
        "targets": len(results),
        "results": results,
        "total_findings": total_findings,
        "average_score": avg,
        "errors": errors,
        "generated_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "scanner_version": _SCANNER_VERSION,
    }


def export_portfolio(portfolio, out_path):
    """把 portfolio 报告落盘（JSON）。"""
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(portfolio, fh, ensure_ascii=False, indent=2, default=str)
    return out_path
