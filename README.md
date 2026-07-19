<h1 align="center">
  <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMzOEIyRUYiIHN0cm9rZS13aWR0aD0iMiI+PHBhdGggZD0iTTEyIDIyYzUuNTIzIDAgMTAtNC40NzcgMTAtMTBTMTcuNTIzIDIgMTIgMiAyIDYuNDc3IDIgMTJzNC40NzcgMTAgMTAgMTB6Ii8+PHBhdGggZD0iTTEyIDh2NCIvPjxwYXRoIGQ9Ik0xMiAxNmguMDEiLz48L3N2Zz4=" alt="AIShield" width="28" valign="middle"/>
  AIShield
</h1>

<p align="center">
  <strong>OWASP MCP Top 10 对齐的 AI Agent 安全扫描与信任生态平台</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"/>
  <img src="https://img.shields.io/badge/Python-3.10%2B-green.svg" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/Rules-133-orange.svg" alt="133 Rules"/>
  <img src="https://img.shields.io/badge/API-22%20Endpoints-9cf.svg" alt="22 API Endpoints"/>
</p>

---

## 简介

AIShield 是一个面向 AI Agent 生态的全链路安全平台，覆盖从 Prompt 注入、工具滥用到 MCP 协议攻击等核心威胁面。平台内置 133 条与 OWASP MCP Top 10 对齐的安全检测规则，支持中文 Prompt 注入检测等本土化场景，并提供 Agent 身份认证（DID）、信誉评分与安全徽章等信任生态模块，帮助开发者构建可信、可审计的 AI Agent 应用。

---

## 特性亮点

| 安全层 (Security Layer) | 生态层 (Ecosystem Layer) |
|:---|:---|
| 133 条 OWASP MCP Top 10 对齐检测规则 | Agent DID 去中心化身份体系 |
| 5 维安全评分（注入 / 越权 / 数据 / 协议 / 供应链） | 多级信誉系统 (Reputation System) |
| 中文 Prompt 注入检测（支持拼音、谐音、拆字变体） | 安全徽章体系 (金 / 银 / 铜) |
| Rug Pull 智能合约 / Agent 行为检测 | 工具市场 (Tool Marketplace) |
| MCP 握手验证与协议合规检查 | A2A (Agent-to-Agent) 协议网关 |
| 零宽字符 / 隐写术 / 不可见负载检测 | 按量计费与配额管理系统 |

---

## 快速开始

### pip 安装

```bash
pip install aishield
aishield init
aishield scan --target ./my-agent
```

### Docker

```bash
docker pull ghcr.io/aishield/aishield:latest
docker run -p 8000:8000 ghcr.io/aishield/aishield:latest
```

### MCP Server (npx)

```json
{
  "mcpServers": {
    "aishield": {
      "command": "npx",
      "args": ["-y", "aishield-mcp-server"]
    }
  }
}
```

---

## API 端点

| 方法 | 路径 | 描述 |
|:---|:---|:---|
| `POST` | `/api/v1/scan` | 提交 Agent 安全扫描任务 |
| `GET`  | `/api/v1/scan/{task_id}` | 查询扫描任务状态与结果 |
| `GET`  | `/api/v1/scan/{task_id}/report` | 获取扫描报告（JSON / PDF） |
| `POST` | `/api/v1/scan/batch` | 批量提交扫描任务 |
| `GET`  | `/api/v1/scan/batch/{batch_id}` | 查询批量扫描进度 |
| `GET`  | `/api/v1/rules` | 获取全部检测规则列表 |
| `GET`  | `/api/v1/rules/{rule_id}` | 获取单条规则详情 |
| `POST` | `/api/v1/rules/custom` | 创建自定义检测规则 |
| `PUT`  | `/api/v1/rules/custom/{rule_id}` | 更新自定义规则 |
| `DELETE`| `/api/v1/rules/custom/{rule_id}` | 删除自定义规则 |
| `GET`  | `/api/v1/agent/did/{agent_id}` | 查询 Agent DID 身份信息 |
| `POST` | `/api/v1/agent/did/register` | 注册 Agent DID 身份 |
| `GET`  | `/api/v1/agent/reputation/{agent_id}` | 查询 Agent 信誉评分 |
| `POST` | `/api/v1/agent/badge/issue` | 签发安全徽章 |
| `GET`  | `/api/v1/agent/badge/{agent_id}` | 查看 Agent 徽章列表 |
| `GET`  | `/api/v1/mcp/verify` | MCP 握手协议验证 |
| `POST` | `/api/v1/mcp/audit` | MCP 交互日志审计 |
| `GET`  | `/api/v1/marketplace/tools` | 工具市场 - 工具列表 |
| `GET`  | `/api/v1/marketplace/tools/{tool_id}` | 工具市场 - 工具详情 |
| `POST` | `/api/v1/marketplace/tools/publish` | 工具市场 - 发布工具 |
| `GET`  | `/api/v1/billing/usage` | 查询用量与计费明细 |
| `POST` | `/api/v1/a2a/gateway/forward` | A2A 协议网关转发 |

---

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        AIShield Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Scanner Engine (核心层)                 │   │
│  │                                                         │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐            │   │
│  │  │ Prompt    │ │ MCP       │ │ Supply    │            │   │
│  │  │ Injection │ │ Protocol  │ │ Chain     │            │   │
│  │  │ Detector  │ │ Validator │ │ Analyzer  │            │   │
│  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘            │   │
│  │        │             │             │                   │   │
│  │  ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐            │   │
│  │  │ Rug Pull  │ │ Zero-Width│ │ Custom    │            │   │
│  │  │ Detector  │ │ Detector  │ │ Rules     │            │   │
│  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘            │   │
│  │        └─────────────┼─────────────┘                   │   │
│  │                      ▼                                 │   │
│  │            ┌──────────────────┐                         │   │
│  │            │  5-Dim Scorer    │                         │   │
│  │            │  评分引擎 (133条) │                         │   │
│  │            └────────┬─────────┘                         │   │
│  └─────────────────────┼───────────────────────────────────┘   │
│                        ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  API Server (接口层)                     │   │
│  │                                                         │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐            │   │
│  │  │ Scan API  │ │ Rules API │ │ MCP API   │            │   │
│  │  │ (6端点)   │ │ (5端点)   │ │ (2端点)   │            │   │
│  │  └───────────┘ └───────────┘ └───────────┘            │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐            │   │
│  │  │ Agent API │ │ Market API│ │ Billing   │            │   │
│  │  │ (5端点)   │ │ (3端点)   │ │ API (1)   │            │   │
│  │  └───────────┘ └───────────┘ └───────────┘            │   │
│  └─────────────────────┬───────────────────────────────────┘   │
│                        ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                Eco Modules (生态层)                      │   │
│  │                                                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Agent DID│ │ 信誉系统  │ │ 安全徽章  │ │ 工具市场 │  │   │
│  │  │ 身份注册  │ │ 评分追踪  │ │ 金/银/铜  │ │ 审核发布 │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  │  ┌──────────┐ ┌──────────┐                            │   │
│  │  │A2A网关   │ │ 计费系统  │                            │   │
│  │  │ 协议转发  │ │ 用量配额  │                            │   │
│  │  └──────────┘ └──────────┘                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 对比

| 维度 | AIShield | Snyk Agent Scan | AgentAuditKit |
|:---|::---:|:---:|:---:|
| OWASP MCP Top 10 对齐规则 | **133** | ~40 | ~60 |
| 中文 Prompt 注入检测 | **支持** | 不支持 | 不支持 |
| 5 维安全评分体系 | **支持** | 单一评分 | 3 维 |
| MCP 协议验证 | **支持** | 不支持 | 基础支持 |
| Rug Pull 检测 | **支持** | 不支持 | 不支持 |
| 零宽字符检测 | **支持** | 不支持 | 不支持 |
| Agent DID 身份 | **支持** | 不支持 | 不支持 |
| 信誉系统 & 安全徽章 | **支持** | 不支持 | 不支持 |
| 工具市场 | **支持** | 不支持 | 不支持 |
| A2A 协议网关 | **支持** | 不支持 | 不支持 |
| 计费系统 | **支持** | 企业版 | 不支持 |
| 自定义规则 | **支持** | 有限 | 支持 |
| MCP Server 模式 | **支持** | 不支持 | 支持 |
| 开源协议 | **MIT** | 商业 | Apache 2.0 |

---

## 路线图

### Phase 1 -- 基础安全扫描 (当前)

- [x] 133 条 OWASP MCP Top 10 对齐检测规则
- [x] 5 维安全评分引擎
- [x] 中文 Prompt 注入检测
- [x] MCP 握手验证
- [x] 零宽字符 / Rug Pull 检测
- [x] 22 个 REST API 端点
- [x] MCP Server 模式 (npx)

### Phase 2 -- 信任生态

- [ ] Agent DID 身份注册与验证
- [ ] 多级信誉系统上线
- [ ] 安全徽章 (金 / 银 / 铜) 签发
- [ ] 工具市场 Beta 上线
- [ ] A2A 协议网关
- [ ] 计费与配额系统

### Phase 3 -- 规模化与治理

- [ ] 多租户支持与企业 SSO
- [ ] SLA 监控与告警
- [ ] 社区贡献规则市场
- [ ] AI 驱动的规则自动生成
- [ ] 国际化 (i18n) 多语言支持
- [ ] Web Dashboard 可视化管理

---

## 贡献指南

我们欢迎所有形式的贡献！请遵循以下步骤：

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 提交变更：`git commit -m 'feat: 添加 xxx 功能'`
4. 推送分支：`git push origin feature/your-feature-name`
5. 提交 **Pull Request**

### 提交规范

请使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档变更
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建 / 工具链变更

### 新增规则

如需贡献新的检测规则，请在 `rules/` 目录下创建 JSON 文件，并确保规则与 OWASP MCP Top 10 分类对齐。提交 PR 前请运行完整测试套件：

```bash
pytest tests/ -v
```

---

## License

本项目基于 [MIT License](./LICENSE) 开源。

Copyright (c) 2025 AIShield Contributors

---

<p align="center">
  <sub>Built with care by the AIShield community</sub>
</p>