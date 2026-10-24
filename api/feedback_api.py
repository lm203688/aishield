"""
api/feedback_api.py — 交互式修复反馈闭环 API（P3-4）

提供误报反馈→抑制→修复建议→复扫的完整闭环：
- POST /api/v1/feedback/false-positive  — 报告误报（自动抑制该规则+文件）
- GET  /api/v1/feedback/suppressions    — 列出所有抑制规则
- POST /api/v1/feedback/suppressions    — 手动添加抑制
- DELETE /api/v1/feedback/suppressions/{id} — 移除抑制
- POST /api/v1/feedback/remediate       — 获取修复建议
- POST /api/v1/feedback/rescan          — 修复后复扫验证

设计纪律：
- 零第三方依赖，仅标准库
- 内存存储（不写磁盘），适合 CI 环境短生命周期
- 抑制规则是**临时白名单**，不是永久放行——每次扫描开始时重置
- 修复建议基于规则类型生成，不依赖外部 LLM
"""
from __future__ import annotations

import hashlib
import json
import time
from urllib.parse import parse_qs

# 路径：确保项目根在 sys.path
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

PREFIX = "/api/v1/feedback"

# ── 内存抑制存储 ──────────────────────────────────────────────────────────
# 结构：{ suppression_id: { rule_id, file_path, reason, created_at, source } }
_suppressions: dict = {}
_suppression_counter = 0


def _next_suppression_id() -> str:
    global _suppression_counter
    _suppression_counter += 1
    ts = int(time.time())
    return f"sup_{ts}_{_suppression_counter}"


def _make_suppression(rule_id: str, file_path: str, reason: str,
                      source: str) -> dict:
    sid = _next_suppression_id()
    entry = {
        "id": sid,
        "rule_id": rule_id,
        "file_path": file_path,
        "reason": reason,
        "source": source,  # "false_positive" | "manual" | "batch"
        "created_at": time.time(),
    }
    _suppressions[sid] = entry
    return entry


# ── 修复建议知识库 ────────────────────────────────────────────────────────
_REMEDIATION_DB = {
    "MCP01": {
        "title": "Tool Poisoning",
        "fix": "审查 MCP server 的 tools/list 返回值，移除嵌入的 prompt injection 载荷。"
               "确保工具描述不包含指令性文本（如 'ignore previous instructions'）。",
        "steps": [
            "1. 检查 tools/list 返回值中的 description 字段",
            "2. 移除任何指令性文本或角色扮演诱导",
            "3. 确保工具描述只说明功能，不包含行为指令",
        ],
    },
    "MCP02": {
        "title": "Tool Poisoning (Parameter)",
        "fix": "审查工具参数定义，确保 inputSchema 不包含 prompt injection 载荷。",
        "steps": [
            "1. 检查每个 tool 的 inputSchema",
            "2. 移除参数描述中的指令性文本",
            "3. 验证 schema 类型正确，不包含隐藏的指令字段",
        ],
    },
    "MCP03": {
        "title": "Tool Confusion",
        "fix": "确保工具命名唯一，避免与已知工具冲突。",
        "steps": [
            "1. 检查工具名称是否与内置工具或其他 server 冲突",
            "2. 使用唯一的命名空间前缀",
            "3. 避免使用通用名称（如 'search', 'run'）",
        ],
    },
    "MCP06": {
        "title": "Prompt Injection",
        "fix": "移除嵌入在工具描述、参数或返回值中的 prompt injection 载荷。",
        "steps": [
            "1. 扫描所有文本字段中的注入模式",
            "2. 使用转义或编码处理用户输入",
            "3. 在 agent 侧添加输入过滤层",
        ],
    },
    "MCP09": {
        "title": "Tool Poisoning (Rug Pull)",
        "fix": "固定依赖版本，使用 lockfile，定期验证工具内容未变。",
        "steps": [
            "1. 使用 package-lock.json 或 requirements.txt 固定版本",
            "2. 启用 npm/pip 的 integrity 校验",
            "3. 设置定期重扫策略检测内容变更",
        ],
    },
    "MCP10": {
        "title": "Unbounded Resource Consumption",
        "fix": "添加资源限制：请求超时、响应大小限制、速率限制。",
        "steps": [
            "1. 设置 HTTP 请求超时（建议 30s）",
            "2. 限制工具返回的响应大小",
            "3. 添加速率限制防止资源耗尽",
        ],
    },
    "SANDBOX": {
        "title": "Sandbox Hardening",
        "fix": "加固容器/沙箱配置，移除特权模式，限制网络和能力。",
        "steps": [
            "1. 移除 --privileged 和 cap_add: ALL",
            "2. 限制网络访问（使用 network: none 或白名单）",
            "3. 启用 seccomp/apparmor 默认配置",
            "4. 使用非 root 用户运行",
        ],
    },
}

# AST 修复建议
_AST_REMEDIATION = {
    "AST01": "审查技能文件中的可执行代码，移除远程模块加载、编码载荷执行和反弹 shell 模式。",
    "AST02": "固定依赖版本，使用 lockfile 和 integrity 校验，验证发布者账号仍活跃。",
    "AST03": "遵循最小权限原则，移除通配符权限（*）和 admin/system scope 声明。",
    "AST04": "确保技能元数据诚实描述其能力，不冒充知名品牌，不虚假声称官方认证。",
    "AST05": "避免将执行逻辑外置到可变 URL，固定指令源或使用内联配置。",
    "AST06": "启用沙箱隔离，限制网络访问为 bridge/none 模式，避免 host 网络。",
    "AST07": "固定版本号（不使用 latest/master），添加 checksum/integrity 字段。",
    "AST08": "避免混淆代码（chr 拼接、hex escape、base64+exec），使用可读的源码。",
    "AST09": "添加责任人（author/owner）和审批状态（approved/reviewed）字段。",
    "AST10": "明确声明支持的平台列表，避免使用 all/universal 通配符。",
}


def _get_remediation(rule_id: str, description: str = "") -> dict:
    """根据规则 ID 生成修复建议。"""
    # 尝试精确匹配
    if rule_id in _REMEDIATION_DB:
        entry = _REMEDIATION_DB[rule_id].copy()
        entry["rule_id"] = rule_id
        entry["description"] = description
        return entry

    # 尝试 AST 前缀
    if rule_id.startswith("AST"):
        return {
            "rule_id": rule_id,
            "description": description,
            "title": f"{rule_id} Remediation",
            "fix": _AST_REMEDIATION.get(rule_id, "审查并修复该问题。"),
            "steps": [
                "1. 定位问题代码",
                "2. 应用修复",
                "3. 重新扫描验证",
            ],
        }

    # 通用建议
    return {
        "rule_id": rule_id,
        "description": description,
        "title": f"Fix for {rule_id}",
        "fix": "审查相关代码，应用适当的安全修复。",
        "steps": [
            "1. 定位问题代码",
            "2. 应用修复",
            "3. 重新扫描验证",
        ],
    }


# ── 复扫逻辑 ──────────────────────────────────────────────────────────────
def _rescan_content(content: str, file_path: str = "",
                    original_findings: list = None) -> dict:
    """复扫内容，返回新 findings 和对比结果。"""
    # 加载扫描引擎
    from scanner.engine import scan_content
    new_findings = scan_content(content, file_path=file_path or "inline")

    result = {
        "file_path": file_path or "inline",
        "content_hash": hashlib.sha256(
            content.encode("utf-8")).hexdigest()[:16],
        "new_findings_count": len(new_findings),
        "new_findings": [
            {
                "rule_id": f.get("rule_id"),
                "description": f.get("description"),
                "severity": f.get("severity"),
                "line": f.get("line"),
            }
            for f in new_findings
        ],
    }

    # 对比原始 findings
    if original_findings:
        original_ids = {f.get("rule_id") for f in original_findings}
        new_ids = {f.get("rule_id") for f in new_findings}
        result["fixed"] = sorted(original_ids - new_ids)
        result["remaining"] = sorted(new_ids)
        result["new_issues"] = sorted(new_ids - original_ids)
        result["all_fixed"] = len(new_findings) == 0
        result["improvement"] = (
            len(original_findings) - len(new_findings)
        )

    return result


# ── GET ────────────────────────────────────────────────────────────────────
def handle_get(path: str, query: str = ""):
    """返回 (payload_dict, status_code)。"""
    # 允许调用方把 ?query 直接拼在 path 里
    if "?" in path:
        path, embedded = path.split("?", 1)
        if not query:
            query = embedded
    sub = path[len(PREFIX):]

    if sub == "" or sub == "/":
        return {
            "service": "aishield-feedback",
            "version": "v1",
            "endpoints": {
                "GET  /api/v1/feedback/suppressions": "列出所有抑制规则",
                "POST /api/v1/feedback/false-positive": "报告误报（自动抑制）",
                "POST /api/v1/feedback/suppressions": "手动添加抑制",
                "DELETE /api/v1/feedback/suppressions/{id}": "移除抑制",
                "POST /api/v1/feedback/remediate": "获取修复建议",
                "POST /api/v1/feedback/rescan": "修复后复扫验证",
                "POST /api/v1/feedback/clear": "清空所有抑制",
            },
            "active_suppressions": len(_suppressions),
        }, 200

    if sub == "/suppressions":
        return {
            "count": len(_suppressions),
            "suppressions": list(_suppressions.values()),
        }, 200

    if sub.startswith("/suppressions/"):
        sid = sub[len("/suppressions/"):]
        if sid in _suppressions:
            return _suppressions[sid], 200
        return {"error": "suppression not found", "id": sid}, 404

    return {"error": "unknown feedback endpoint", "path": path,
            "hint": "GET %s/ for endpoint list" % PREFIX}, 404


# ── POST ───────────────────────────────────────────────────────────────────
def handle_post(path: str, data: dict):
    """返回 (payload_dict, status_code)。"""
    data = data or {}
    sub = path[len(PREFIX):]

    # ── 报告误报 → 自动抑制 ──
    if sub == "/false-positive":
        rule_id = data.get("rule_id")
        file_path = data.get("file_path")
        if not rule_id or not file_path:
            return {"error": "rule_id and file_path required"}, 400
        reason = data.get("reason", "Reported as false positive")
        entry = _make_suppression(rule_id, file_path, reason, "false_positive")
        return {
            "success": True,
            "suppression_id": entry["id"],
            "message": (
                f"Suppressed {rule_id} for {file_path}. "
                "This finding will be hidden on subsequent scans."
            ),
            "suppression": entry,
        }, 201

    # ── 手动添加抑制 ──
    if sub == "/suppressions":
        rule_id = data.get("rule_id")
        file_path = data.get("file_path")
        if not rule_id or not file_path:
            return {"error": "rule_id and file_path required"}, 400
        reason = data.get("reason", "Manual suppression")
        entry = _make_suppression(rule_id, file_path, reason, "manual")
        return {
            "success": True,
            "suppression_id": entry["id"],
            "suppression": entry,
        }, 201

    # ── 批量添加抑制 ──
    if sub == "/suppressions/batch":
        entries = data.get("suppressions", [])
        if not entries:
            return {"error": "suppressions array required"}, 400
        created = []
        for e in entries:
            if e.get("rule_id") and e.get("file_path"):
                entry = _make_suppression(
                    e["rule_id"], e["file_path"],
                    e.get("reason", "Batch suppression"),
                    "batch"
                )
                created.append(entry)
        return {
            "success": True,
            "created": len(created),
            "suppressions": created,
        }, 201

    # ── 清空所有抑制 ──
    if sub == "/clear":
        count = len(_suppressions)
        _suppressions.clear()
        return {
            "success": True,
            "cleared": count,
        }, 200

    # ── 获取修复建议 ──
    if sub == "/remediate":
        rule_id = data.get("rule_id")
        if not rule_id:
            return {"error": "rule_id required"}, 400
        description = data.get("description", "")
        suggestion = _get_remediation(rule_id, description)

        # 如果提供了 findings，为每个 finding 生成建议
        findings = data.get("findings")
        if findings:
            suggestions = []
            for f in findings:
                rid = f.get("rule_id", rule_id)
                desc = f.get("description", "")
                suggestions.append(_get_remediation(rid, desc))
            suggestion["findings"] = suggestions
            suggestion["total_findings"] = len(suggestions)

        return {
            "rule_id": rule_id,
            "remediation": suggestion,
        }, 200

    # ── 修复后复扫 ──
    if sub == "/rescan":
        content = data.get("content")
        if not content:
            return {"error": "content required (the fixed file content)"}, 400
        file_path = data.get("file_path", "")
        original_findings = data.get("original_findings")
        result = _rescan_content(content, file_path, original_findings)
        return result, 200

    return {"error": "unknown feedback endpoint", "path": path}, 404


# ── DELETE ─────────────────────────────────────────────────────────────────
def handle_delete(path: str):
    """返回 (payload_dict, status_code)。"""
    sub = path[len(PREFIX):]

    if sub.startswith("/suppressions/"):
        sid = sub[len("/suppressions/"):]
        if sid in _suppressions:
            removed = _suppressions.pop(sid)
            return {
                "success": True,
                "removed": removed,
            }, 200
        return {"error": "suppression not found", "id": sid}, 404

    return {"error": "unknown feedback endpoint", "path": path}, 404


if __name__ == "__main__":
    import pprint
    pprint.pprint(handle_get(PREFIX + "/"))
