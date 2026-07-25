# AIShield 开源合作策略

> 与开源 Agent 项目建立深度合作，构建 Agent 安全生态网络

## 核心逻辑

```
AIShield = Agent 安全连接器
├── 上游：Agent 框架（CrewAI, LangChain, AutoGen） → 需要 AIShield 保护他们的 Agent
├── 中游：MCP Server（10,000+） → 需要 AIShield 扫描验证
└── 下游：Agent 市场/目录（mcp-marketplace, Smithery） → 需要 AIShield 提供信任评分
```

**为什么这个逻辑成立：**
1. AIShield 本质是"连接器" — 连接 Agent 框架和安全能力
2. 框架项目没有安全能力 = AIShield 有明确的合作价值
3. MCP Server 作者需要安全验证 = AIShield 提供免费扫描服务
4. 市场平台需要信任数据 = AIShield 提供标准化安全评分
5. **反馈循环：** 合作方的用户使用 AIShield → 发现安全问题 → 反馈给 AIShield → 规则库提升 → 合作方受益更多

## Phase 1: 高影响低门槛（1-2 个月）

### 1.1 MCP 原生集成（覆盖面最广）

**目标**: 让任何 MCP 客户端都能直接调用 AIShield

**已实现**:
- `POST /api/v1/mcp` — StreamableHTTP MCP 端点
- 8 个 MCP 工具（aishield_scan, agent_register 等）
- Agent Card 自动发现

**推广**:
- 向 awesome-mcp-servers 提交 PR
- 发布到 Glama.ai 目录
- 在 Claude/Cursor 社区推荐

### 1.2 mcp-marketplace 安全评分集成

**目标项目**: [AI-Agent-Hub/mcp-marketplace](https://github.com/AI-Agent-Hub/mcp-marketplace)
**Stars**: 新兴项目，索引 5000+ MCP Server
**合作方式**:
1. 提交 PR：为每个 MCP Server 添加 AIShield 安全评分 badge
2. 提供 API：`GET /api/v1/badge/{server_name}` 返回 SVG badge
3. 价值：mcp-marketplace 的差异化功能，AIShield 的流量入口

**PR 方案**:
```
在 mcp-marketplace 的 MCP Server 详情页添加:
[![AIShield Security](https://aishield.tools/badge/{server_name}?score=85&level=A)](https://aishield.tools/tool/profile?name={server_name})
```

### 1.3 与 agentic_security 互补合作

**目标项目**: [msoedov/agentic_security](https://github.com/msoedov/agentic_security)
**Stars**: 1,899
**合作方式**:
- 互相推荐：agentic_security 做 prompt 层扫描，AIShield 做 MCP/工具层扫描
- 联合博客："Complete AI Agent Security Stack"
- shared issue tracker 标签

## Phase 2: 框架深度集成（2-4 个月）

### 2.1 CrewAI Tools Registry

**目标**: CrewAI (38.8k stars)
**合作方式**: 开发 `crewai-tools-aishield` 包

```python
# crewai_tools_aishield.py
from crewai.tools import BaseTool
from aishield import scan_tool

class AIShieldSecurityTool(BaseTool):
    name: str = "aishield_security_scan"
    description: str = "Scan an MCP tool for security risks before execution"
    
    def _run(self, tool_name: str, tool_description: str) -> str:
        result = scan_tool(tool_name, tool_description)
        return f"Security Score: {result['score']}/100, Risk: {result['risk_level']}"
```

**价值**: CrewAI Agent 在执行任何工具前可以先调用安全检查

### 2.2 OpenAI Agents SDK

**目标**: OpenAI Agents SDK (15.2k stars, 原生 MCP 支持)
**合作方式**: AIShield 已是 MCP Server，任何使用 OpenAI Agents SDK 的项目都可以直接集成

```python
# 在 OpenAI Agents SDK 配置中添加
mcp_servers = {
    "aishield": {
        "url": "https://aishield.tools/api/v1/mcp",
        "type": "streamable-http"
    }
}
```

### 2.3 LangChain Callback Handler

**目标**: LangChain (117k stars)
**合作方式**: 开发 `langchain-aishield` 包

```python
from langchain_aishield import AIShieldCallback

# 在 Agent 执行链中注入安全检查
callbacks=[AIShieldCallback(api_key="...")]
```

### 2.4 SuperAGI 插件

**目标**: SuperAGI（生产级 AutoGPT）
**合作方式**: 利用其原生 Plugin 系统开发安全扫描插件

## Phase 3: 生态影响力（4-6 个月）

### 3.1 向 MCP 官方提交安全最佳实践

- 在 modelcontextprotocol/servers 仓库中添加安全文档
- 参与 OWASP MCP Top 10 标准制定

### 3.2 n8n / Dify 工作流节点

- 开发 AIShield 安全扫描工作流节点
- 在 n8n/Dify 插件市场发布

### 3.3 向 Anthropic / Google 提交 A2A 安全扩展提案

- 在 A2A 协议中增加 `security_verification` 字段
- 在 Agent Card 中增加 `security_badge` 字段

## 合作项目优先级矩阵

| 项目 | Stars | MCP | 安全缺口 | 插件机制 | 接受PR概率 | 优先级 |
|------|-------|-----|---------|---------|-----------|-------|
| mcp-marketplace | 新 | 是 | 完全缺失 | API | 高 | P0 |
| agentic_security | 1.9k | 是 | 互补 | MCP | 高 | P0 |
| CrewAI | 38.8k | 是 | 无 | Tools Registry | 高 | P1 |
| OpenAI Agents SDK | 15.2k | 原生 | 无 | Tool | 中 | P1 |
| LangChain | 117k | 是 | 仅 Guardrails | Callback | 中 | P1 |
| SuperAGI | 高 | 部分 | 无 | Plugin | 极高 | P1 |
| Smolagents | 23.2k | 是 | 无 | Toolkit | 中高 | P2 |
| n8n | 65k+ | 否 | 无 | 节点 | 中 | P2 |
| Dify | 60k+ | 部分 | 无 | 插件市场 | 中 | P2 |

## 反馈收集机制

每个合作项目都会产生反馈循环：

```
合作方用户使用 AIShield 扫描
    ↓
发现新的安全风险 / 误报 / 漏报
    ↓
在 GitHub Issue 报告（或合作方 Issue 交叉引用）
    ↓
AIShield 团队修复 / 新增规则
    ↓
新版本自动部署（CI/CD）
    ↓
合作方用户受益 → 更多使用 → 更多反馈
```

## 联系合作方的话术模板

### Issue/PR 标题
```
[WIP] Add AIShield security scanning integration
```

### 描述模板
```
Hi {maintainer_name},

I'm building AIShield, an open-source AI Agent security scanner aligned with OWASP MCP Top 10 (133 rules, MIT license, zero dependencies).

I noticed {project_name} doesn't have built-in security scanning for {specific_gap}. I'd like to propose an integration that:

1. {具体的集成方案}
2. {对用户的价值}
3. {对项目的价值}

The integration is lightweight (pure stdlib, no new dependencies) and provides:
- {feature 1}
- {feature 2}

Would you be open to this? Happy to adjust the approach based on your preferences.

Links:
- Repo: https://github.com/lm203688/aishield
- Demo: https://aishield.tools
- MCP endpoint: https://aishield.tools/api/v1/mcp
```
