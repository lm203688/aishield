# awesome-mcp-servers 上架 PR 模板

> 当向 [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) 提交 PR 时使用此模板

---

## PR 内容

```markdown
## AIShield Security Scanner

- **Website**: https://aishield.tools
- **Repository**: https://github.com/lm203688/aishield
- **License**: MIT

AIShield 是 AI Agent 安全与信任基础设施，为 MCP Server 和 AI Agent 工具提供 OWASP MCP Top 10 对齐的安全扫描。支持提示注入检测、密钥泄露检测、工具滥用检测、MCP 握手验证等 227 条安全规则。

**特点：**
- Agent-First 一键入驻（注册 Agent + 获取 API Key + 快速开始，一步完成）
- MCP StreamableHTTP 原生集成，可直接被 Claude/Cursor/VS Code 调用
- A2A Agent Card 自动发现，支持 Agent 间信任评分
- 开源、零外部依赖、227 条安全规则
- OpenAPI 3.0.3 规范，支持 Agent 自动发现 API

**安装方式：**
```json
{
  "mcpServers": {
    "aishield": {
      "url": "https://aishield.tools/api/v1/mcp"
    }
  }
}
```

**分类**: `security`, `developer-tools`
```

---

## 提交前检查清单

- [x] 项目使用 MIT 开源协议
- [x] 提供英文 README
- [x] 有明确的安装和使用说明
- [x] 项目活跃维护（最近 30 天有提交）
- [x] 无恶意代码或安全风险