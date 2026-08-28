# AIShield 发布操作手册

> 三步完成发布，每步 5 分钟以内

---

## 任务一：提交 awesome-mcp-servers PR（最优先）

### 为什么重要
punkpeye/awesome-mcp-servers 是 MCP 生态最大的发现入口，2,600+ PR、9,000+ commits。被收录后所有 MCP 用户都能看到 AIShield。

### 操作步骤

**Step 1: 生成 GitHub Token**
1. 打开 https://github.com/settings/tokens?type=beta
2. 点击 "Generate new token"
3. Token name: `aishield-pr`
4. Repository access: `All repositories`（或选 `Only select repositories` > 选 `punkpeye/awesome-mcp-servers`）
5. Permissions > Repository permissions > Contents: `Read and write`
6. 点击 "Generate token"，复制 Token（只显示一次）

**Step 2: Fork 仓库**
1. 打开 https://github.com/punkpeye/awesome-mcp-servers
2. 点击右上角 "Fork"
3. 等待 Fork 完成

**Step 3: 编辑文件**
1. 在你 Fork 的仓库中，打开 `README.md`
2. 找到 `## Security` 分类（如果没有，找最接近的分类或创建）
3. 在该分类下添加以下内容：

```markdown
- [AIShield](https://aishield.tools) - AI Agent security & trust infrastructure. OWASP MCP Top 10 aligned scanner with 227 rules, MCP native, Agent-First one-click onboarding, A2A trust scoring. Zero dependencies, pure Python. ([Open Source](https://github.com/lm203688/aishield))
```

**Step 4: 提交 PR**
1. 点击 "Contribute" > "Open pull request"
2. Title: `Add AIShield - AI Agent security scanner`
3. Description:

```markdown
## Summary

Adding AIShield, an open-source AI Agent security scanner aligned with OWASP MCP Top 10.

## Key Features

- **227 security rules** covering all 10 OWASP MCP Top 10 risk categories
- **MCP native**: StreamableHTTP endpoint, 8 tools available
- **Agent-First**: One-call onboarding (register + API key + quick start)
- **Zero dependencies**: Pure Python stdlib
- **A2A Agent Card**: Auto-discovery with trust scoring
- **OpenAPI 3.0.3**: Machine-readable API spec

## Installation as MCP Server

```json
{
  "mcpServers": {
    "aishield": {
      "url": "https://aishield.tools/api/v1/mcp"
    }
  }
}
```

## Links

- Website: https://aishield.tools
- Repository: https://github.com/lm203688/aishield
- License: MIT
- OpenAPI: https://aishield.tools/openapi.json
- Agent Card: https://aishield.tools/.well-known/agent-card.json

## Category

`security`, `developer-tools`
```

4. 点击 "Create pull request"

---

## 任务二：发布 Reddit 帖子

### 最佳发布时间
- **北京时间**: 周二或周三 21:00-23:00（美东上午 9-11 点）
- **目标子版块**: r/LocalLLaMA（最活跃的 AI Agent 社区）

### 操作步骤

**Step 1: 准备账号**
1. 打开 https://www.reddit.com
2. 注册/登录
3. r/LocalLLaMA 需要邮箱验证 + 一定 karma 才能发帖（如果受限，先在 r/MCP 或 r/ChatGPTCoding 评论积累 karma）

**Step 2: 发布帖子**
1. 打开 https://www.reddit.com/r/LocalLLaMA/new/
2. Post type: `Link`
3. URL: `https://github.com/lm203688/aishield`
4. Title:

```
AIShield: Open-source AI Agent security scanner (OWASP MCP Top 10, 227 rules, MCP native, zero deps)
```

5. 帖子内容（ flair 选 `Show & Tell` 或 `Tool`）:

```markdown
I built AIShield, an open-source AI Agent security & trust infrastructure platform. It scans MCP servers and AI Agent tools against 227 security rules aligned with OWASP MCP Top 10.

**The problem**: The MCP ecosystem has 10,000+ servers and 97M monthly SDK downloads, but zero built-in security scanning. When an AI agent calls a MCP tool, it gets the same permissions as the user — no sandboxing, no trust verification, no prompt injection protection.

**What it does**:
- Scans MCP tool descriptions, schemas, and configs for 227 security risks
- Detects prompt injection, secret leakage, excessive permissions, tool abuse, schema poisoning
- Provides an MCP Server endpoint — Claude, Cursor, VS Code can call security scans directly
- Agent-First: register + get DID + API key in ONE API call
- Built-in trust ecosystem: DID identity, reputation, skill marketplace

**MCP integration**:
```json
{
  "mcpServers": {
    "aishield": { "url": "https://aishield.tools/api/v1/mcp" }
  }
}
```

**Tech**: Pure Python stdlib (zero dependencies), 227 rules, MIT license.

**Links**:
- Demo: https://aishield.tools
- Code: https://github.com/lm203688/aishield
- OpenAPI: https://aishield.tools/openapi.json

Feedback welcome — especially from MCP server authors who want to verify their tools are safe.
```

**Step 3: 交叉发布到其他版块**（48 小时后）
- r/MCP — 标题改为聚焦 MCP 安全
- r/ChatGPTCoding — 标题改为 AI 安全工具
- r/Python — 标题改为零依赖安全工具

---

## 任务三：发布 Hacker News 帖子

### 最佳发布时间
- **北京时间**: 周三或周四 6:00-8:00（美东下午 6-8 点，HN 黄金时段）

### 操作步骤

**Step 1: 提交**
1. 打开 https://news.ycombinator.com/submit
2. Title:

```
AIShield: Open-source AI Agent security scanner (OWASP MCP Top 10)
```

3. URL: `https://github.com/lm203688/aishield`

**Step 2: 首条评论**（提交后立即发）

```text
Author here. AIShield scans MCP servers and AI Agent tools against 227 security rules aligned with OWASP MCP Top 10.

Key differentiator vs existing tools (Guardrails AI, agentic_security, MEDUSA):
- AIShield is a trust INFRASTRUCTURE, not just a scanner — DID identity, reputation system, skill marketplace, payment
- MCP native — works as MCP Server, callable from Claude/Cursor/VS Code
- Agent-First — one-call onboarding returns DID + API key + quick start guide
- Zero external dependencies — pure Python stdlib

MCP ecosystem has 10,000+ servers but zero security scanning. AIShield fills that gap.

I wrote a Chinese guide on OWASP MCP Top 10: https://aishield.tools/owasp-mcp-top10-guide/owasp-mcp-top10-guide.html
```

---

## 任务四：提交 Glama.ai 目录

### 操作步骤

1. 打开 https://glama.ai/mcp/servers/submit（或搜索提交入口）
2. 填写信息：
   - Name: `AIShield Security Scanner`
   - URL: `https://aishield.tools/api/v1/mcp`
   - Description: `AI Agent security scanner aligned with OWASP MCP Top 10. 227 rules, prompt injection detection, secret leakage, tool abuse, MCP handshake verification.`
   - Categories: `security`, `developer-tools`
   - Repository: `https://github.com/lm203688/aishield`
   - License: `MIT`

---

## 任务五：提交 mcp-marketplace 安全评分 PR

### 操作步骤

1. 打开 https://github.com/AI-Agent-Hub/mcp-marketplace
2. Fork 仓库
3. 找到 MCP Server 详情页的渲染代码
4. 添加 AIShield 安全评分 badge：

```html
<a href="https://aishield.tools/badge/{server_name}"">
  <img src="https://aishield.tools/badge/{server_name}" alt="AIShield Security Score" />
</a>
```

5. 提交 PR，标题：`Add AIShield security score badge for MCP servers`

---

## 发布后跟进

| 时间 | 动作 |
|------|------|
| 发布后 1 小时 | 回复所有评论（即使是简短感谢） |
| 发布后 24 小时 | 记录数据（views, upvotes, comments, stars, traffic） |
| 发布后 1 周 | 在 GitHub Discussions 分享发布数据 |