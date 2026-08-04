---
title: AIShield Agent Security Benchmark 2026
emoji: 🛡️
colorFrom: blue
colorTo: purple
sdk: static
pinned: false
license: mit
---

# AIShield Agent Security Benchmark 2026

可复现的 **AI Agent / MCP 安全检测基准**。基于 OWASP MCP Top 10 (2025) 与 OWASP Agentic AI Top 10 (2025) 双维标准，提供 201 条静态检测规则 + LLM 语义分析 + CycloneDX SBOM/SARIF 输出。

## 这个库是什么
- **规则库**：`scanner/rules.py` — 110 条 MCP 规则 + 60 条 Agentic(AIS) 规则 + 31 条中文提示注入规则
- **语义分析**：`scanner/llm_analyzer.py` — Tool Poisoning 语义检测（可选，远程 LLM）
- **信任层**：`api/trust_api.py` — 自动认证证书 + 0-100 信任评分
- **报告**：[Agent 安全基准报告 2026](https://aishield.tools/agent-security-benchmark-2026)

## 快速复现
```bash
# 1) 安装并启动
pip install -r requirements.txt   # 零第三方依赖，仅需 Python 3.11+
python -m api.server

# 2) 扫描一个 MCP 仓库
curl -X POST http://localhost:8000/api/v1/audit \
  -H 'Content-Type: application/json' \
  -d '{"source_url":"https://github.com/owner/mcp-server","tool_type":"mcp"}'

# 3) 导出 SARIF 接入 Code Scanning
curl -X POST http://localhost:8000/api/v1/export/sarif \
  -H 'Content-Type: application/json' -d '{"scan_result":{...}}'
```

## 覆盖矩阵
- OWASP MCP Top 10：MCP01–MCP10（110 规则）
- OWASP Agentic AI Top 10：ASI01–ASI10（60 规则）

## 本地 / 零成本 / 隐私
规则引擎零依赖、可完全本地运行，代码与数据**不上云**；全部开源。

## 引用
```
AIShield. (2026). Agent Security Benchmark 2026. https://aishield.tools
```
