# -*- coding: utf-8 -*-
"""
Agent 网络 / Mesh 配置扫描（Network 层）

背景：Cloudflare Mesh（2026-04 Agents Week）把 agent 组网做成基础设施，但官方自认
"Per-agent identity and policy evaluation are future work" —— 所有 agent 流量被当成
"来自一个 Worker"，无法区分是哪个 agent、按 agent 写策略。A2A 也有 session smuggling
（复用合法会话令牌冒充合作方）。

本模块补 AIShield 的"网络层"能力，扫描 agent 组网 / 私网暴露 / 端点鉴权缺陷：
  - 整账户 Mesh 绑定（binding 整个 cf1:network / MESH 且 remote:true，无 per-agent 策略）
  - 0.0.0.0 / 全网卡监听暴露
  - agent 端点 auth: none / authentication: false / public: true
  - 私有资源（internal/private/vpc）被公网暴露

设计原则（与项目一致）：纯本地正则/启发式，不联网、不 spawn、不执行被扫配置。
"""

import re

# 1) 整账户 Mesh / VPC 网络绑定（账户级 network 且无 per-agent 约束）
_ACCOUNT_NETWORK_BINDING = re.compile(
    r'(vpc[_-]?networks|network[_-]?bindings|networks|bindings)\s*[:=]\s*\[[^\]]*'
    r'(cf1:network|"MESH"|"network_id"\s*:\s*"cf1:network"|account[_-]?wide|remote\s*:\s*true)',
    re.I)
# 更宽松：出现 cf1:network 或 remote:true 的 network 绑定
_MESH_HINT = re.compile(r'(cf1:network|"binding"\s*:\s*"MESH"|remote\s*:\s*true)', re.I)

# 2) 全网卡暴露
_BIND_ALL = re.compile(r'(bind|listen|host|address|interface)\s*[:=]\s*["\']?(0\.0\.0\.0|\[::\]|"")', re.I)
_PUBLIC_EXPOSE = re.compile(r'(public|expose|exposed|internet[_-]?facing)\s*[:=]\s*(true|1|"yes"|"true")', re.I)

# 3) 端点无鉴权
_NO_AUTH = re.compile(
    r'(auth|authentication|authn|authorization|require[_-]?auth|secured|protected)\s*[:=]\s*'
    r'(none|false|0|"no"|"false"|disabled?|anonymous)', re.I)
_AGENT_ENDPOINT = re.compile(r'(agent[_-]?endpoint|agent[_-]?url|mcp[_-]?endpoint|server[_-]?url|endpoint)', re.I)

# 4) 私有资源公网暴露
_PRIVATE_RES = re.compile(r'(internal|private|intranet|vpc|corp|staging|secret)', re.I)
_PUBLIC_FLAG = re.compile(r'public\s*[:=]\s*(true|1|"true"|"yes")', re.I)


def network_analysis(files):
    """对 {filepath: content} 跑网络/Mesh 配置扫描。返回 {findings:[...], summary:{...}}。"""
    findings = []
    seen = set()

    def add(ftype, sev, desc, filepath, evidence, category="MCP10"):
        key = f"{ftype}:{desc}:{filepath}"
        if key in seen:
            return
        seen.add(key)
        findings.append({
            "type": ftype,
            "severity": sev,
            "description": desc,
            "file": filepath,
            "evidence": evidence[:140],
            "owasp_category": category,
        })

    for filepath, content in files.items():
        if not isinstance(content, str) or not content.strip():
            continue

        # 1) 整账户 Mesh / VPC 绑定（无 per-agent 策略）
        if _MESH_HINT.search(content):
            add("account_wide_network_binding", "high",
                "检测到账户级网络/Mesh 绑定（cf1:network / binding MESH / remote:true），"
                "缺少 per-agent 身份与策略（Cloudflare 自认的缺口），任何 agent 可达整网",
                filepath, content[:120])

        # 2) 全网卡暴露
        m = _BIND_ALL.search(content)
        if m:
            add("bind_all_interfaces", "high",
                "服务绑定到 0.0.0.0/::（全网卡），agent 端点可能对外暴露",
                filepath, m.group(0)[:120])

        # 3) 端点无鉴权（agent 端点上下文）
        m = _NO_AUTH.search(content)
        if m and _AGENT_ENDPOINT.search(content):
            add("agent_endpoint_no_auth", "high",
                "检测到 agent/MCP 端点但鉴权被关闭（auth: none / anonymous），任何调用方可无认证使用",
                filepath, m.group(0)[:120])

        # 4) 私有资源公网暴露
        if _PRIVATE_RES.search(content) and _PUBLIC_FLAG.search(content):
            add("private_resource_public", "critical",
                "私有/内网资源（internal/private/vpc/corp/staging）被标记为 public=true，存在公网暴露风险",
                filepath, content[:120])

    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1

    summary = {
        "network_findings": len(findings),
        "severity_counts": sev_counts,
        "files_scanned": len(files),
        "note": "网络层扫描：agent 组网/Mesh 可达性过宽、端点无鉴权、私网公网暴露",
    }
    return {"findings": findings, "summary": summary}
