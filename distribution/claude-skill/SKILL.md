---
name: aishield-security-scan
description: 使用 AIShield 对 MCP 服务器 / Agent 配置 / AI Skill 做安全扫描，覆盖 OWASP MCP Top 10 与 Agentic AI Top 10（含记忆投毒、沙箱逃逸）。当用户要审计 AI 工具、检查 MCP 服务器安全、评估 Agent 风险、给 agent 工作区做启动前预扫、生成 SBOM/SARIF 时使用。
---

# AIShield Security Scan

你帮助用户评估 MCP 服务器、AI Skill 与 Agent 工作区的安全性。AIShield 是本地、开源、零成本的扫描器，覆盖 **OWASP MCP Top 10 + OWASP Agentic AI Top 10 + 沙箱硬化**，共 **214 条 MCP 规则 / 220 条 Skill 规则**，输出 CycloneDX SBOM 与 SARIF。

**核心不变量：扫描过程绝不执行被扫配置里的任何命令。** 很多同类工具为了读取 `tools/list` 会真实启动被扫服务——那等于先中招再体检。

## 何时使用

- 用户想审计一个 GitHub 上的 MCP 服务器或 Agent 仓库
- 用户担心工具投毒、提示注入、记忆投毒、过度代理、沙箱逃逸
- 用户要在 agent 沙箱启动前预扫工作区里的 MCP 配置与 skill
- 用户需要 SBOM / SARIF 接入 CI
- 用户想给自己的 Agent 申请 AIShield 安全认证证书

## 如何执行

先约定端点，不要在命令里写死内网地址：

```bash
# 自托管时指向你自己的实例；不设置则用官方托管端点
AISHIELD_API="${AISHIELD_API:-https://aishield.tools}"
```

### 方式 A：扫远程仓库

```bash
curl -X POST "$AISHIELD_API/api/v1/audit" \
  -H 'Content-Type: application/json' \
  -d '{"source_url":"https://github.com/owner/repo","tool_type":"mcp"}'
```

`tool_type` 取 `mcp`（MCP 服务器）或 `skill`（AI Skill / 提示词资产）。

### 方式 B：agent 工作区启动前预扫（纯本地，不联网）

```bash
python scripts/scan_workspace.py /path/to/workspace --md
```

解析工作区里的 `.mcp.json`、forge / Goose / Open Interpreter 配置与 skill 文件，
只读判定，产出可核对的风险表。适合在 sandbox 拉起 agent **之前**跑。

### 方式 C：导出 SARIF 接 Code Scanning

```bash
curl -X POST "$AISHIELD_API/api/v1/export/sarif" \
  -H 'Content-Type: application/json' \
  -d '{"scan_result": <上一步返回> }'
```

### 方式 D：查他人 Agent 的信任分

```bash
curl "$AISHIELD_API/api/v1/trust/score/agent-f864141ae08f"
curl "$AISHIELD_API/api/v1/registry"
```

## 输出解读

- `overall_score` / `risk_level`：整体安全评分与风险等级
- `owasp_coverage` / `agentic_coverage`：命中的 MCP / Agentic 类别
- `score_breakdown` / `top_deductions`：分数是怎么扣的，逐项可追
- `sbom`：CycloneDX 供应链清单；`sarif`：可进 CI 的发现项
- 评分 ≥80 自动签发认证证书（`certification` 字段）

## 注意事项

- **Markdown 不等于文档**：对 skill 类资产，`SKILL.md` 本身就是可执行载荷，AIShield 不会把其中的危险模式当"文档示例"降级处理。
- 语义分析为可选层：配置远程 LLM 需设置 `AISHIELD_LLM_URL` 与 `AISHIELD_LLM_KEY`；不设置则只跑规则引擎。
- 隔离与内容安全是两件事：容器 / 微 VM 沙箱管住"能做什么"，AIShield 管住"读进来的东西该不该信"。两者互补。
- 报告与基准见 https://aishield.tools 与 `docs/agent-security-benchmark-2026.md`。
