---
name: aishield-security-scan
description: 使用 AIShield 对 MCP 服务器 / Agent 配置做安全扫描，覆盖 OWASP MCP Top 10 与 Agentic AI Top 10（含记忆投毒）。当用户要审计 AI 工具、检查 MCP 服务器安全、评估 Agent 风险、生成 SBOM/SARIF 时使用。
---

# AIShield Security Scan

你帮助用户评估 MCP 服务器与 AI Agent 的安全性。AIShield 是本地、开源、零成本的扫描器，覆盖 **OWASP MCP Top 10（110 条规则）+ OWASP Agentic AI Top 10（60 条规则）** 双维检测，并输出 CycloneDX SBOM 与 SARIF。

## 何时使用
- 用户想审计一个 GitHub 上的 MCP 服务器或 Agent 仓库
- 用户担心工具投毒、提示注入、记忆投毒、过度代理
- 用户需要 SBOM / SARIF 接入 CI
- 用户想给自己的 Agent 申请 AIShield 安全认证证书

## 如何执行

### 方式 A：本地扫描（推荐，隐私/零成本）
```bash
# 扫描远程仓库
python -m api.server &   # 启动后调用
curl -X POST http://localhost:8000/api/v1/audit \
  -H 'Content-Type: application/json' \
  -d '{"source_url":"https://github.com/owner/repo","tool_type":"mcp"}'

# 获取 SARIF 接入 Code Scanning
curl -X POST http://localhost:8000/api/v1/export/sarif \
  -H 'Content-Type: application/json' \
  -d '{"scan_result": <上一步返回> }'
```

### 方式 B：调用 AIShield Trust API（给他人 Agent 出安全证书）
```bash
# 查询某 Agent 的信任评分
curl https://aishield.tools/api/v1/trust/score/agent-f864141ae08f

# 列出已注册 Agent
curl https://aishield.tools/api/v1/registry
```

## 输出解读
- `overall_score` / `risk_level`：整体安全评分与风险等级
- `owasp_coverage` / `agentic_coverage`：命中的 MCP / Agentic 类别
- `sbom`：CycloneDX 供应链清单；`sarif`：可进 CI 的发现项
- 评分 ≥80 自动签发认证证书（`certification` 字段）

## 注意事项
- 语义分析（可选）：配置远程 LLM 需设置 `AISHIELD_LLM_URL` 与 `AISHIELD_LLM_KEY`；不设置则跳过语义层，仅规则引擎运行。
- 报告与基准见 https://aishield.tools 与 docs/agent-security-benchmark-2026.md。
