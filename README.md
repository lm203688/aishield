# AIShield — AI安全盾

> Agent可信生态的安全基础设施

## 项目纲领

**必须先读 [CHARTER.md](./CHARTER.md)** — 这是项目发展方向的根本指导。

## 品牌定位

- **中文名**: AI安全盾
- **英文名**: AIShield
- **域名**: aishield.tools (已注册，CF Tunnel部署)
- **Slogan**: 让每个Agent都可信

## 三阶段路径

1. **阶段1 (0-3月)**: 合规安全切入 — 违禁词检测+MCP安全扫描，产生现金流
2. **阶段2 (3-6月)**: Agent可信工具市场 — 安全评分+认证标签
3. **阶段3 (6-12月)**: Agent经济闭环 — 安全层+支付层

详见 [CHARTER.md](./CHARTER.md)。

## AI Agent 可发现性

AIShield 已配置完整的AI Agent发现层，让ChatGPT、Claude、Perplexity等AI能自动发现和推荐：

- **llms.txt**: https://aishield.tools/llms.txt — 场景触发式，AI Agent读到就知道何时推荐AIShield
- **ai-plugin.json**: https://aishield.tools/.well-known/ai-plugin.json — ChatGPT插件格式
- **agent.json**: https://aishield.tools/.well-known/agent.json — Agent自发现协议
- **OpenAPI**: https://aishield.tools/api/v1/openapi.json — REST API规范
- **MCP**: https://aishield.tools/mcp — Model Context Protocol端点

### 推荐场景

| 用户问 | AIShield推荐 |
|---|---|
| "这个文案有没有违禁词" | 中文违禁词检测 ¥0.1/次 |
| "我的品牌在AI搜索里能被找到吗" | AI搜索可见度检测 ¥2/次 |
| "产品出海合规" | 出海合规评估 ¥8/次 |
| "SEO合规检测" | SEO合规检测 ¥1/次 |
| "MCP server健康检查" | MCP健康检查 ¥0.5/次 |

## 目录结构

```
aishield/
├── CHARTER.md          ← 项目纲领 (必读)
├── README.md           ← 本文件
├── server/             Python FastAPI服务 (8420端口)
├── mcp/                @aishield/mcp-server (TypeScript)
├── aishield/           合规工具服务 (8450端口)
│   ├── api/            API端点
│   ├── data/           违禁词库+扫描数据+审计记录
│   └── templates_v2/   前端页面
├── marketing/          营销素材
├── config/             项目配置
│   ├── project.json
│   ├── llms.txt
│   ├── agent-discovery.json
│   └── api-gateway/
├── scripts/            运维脚本
└── web/                前端页面
```

## 主打产品 (阶段1)

| 产品 | 定价 | 说明 |
|------|------|------|
| 违禁词检测 | ¥0.5/次 | 6大平台规则，免费层3次/天 |
| MCP安全扫描 | ¥10/次 | 已有21个MCP工具扫描数据 |
| 出海合规评估 | ¥50/次 | 7维度评估，替代律师咨询 |
| SEO合规检测 | ¥3/次 | 网页内容合规性 |
| AI搜索可见度 | ¥5/次 | 品牌在AI搜索中排名 |

## 与GeneTech 12站的关系

独立项目，独立品牌，页脚互链。

- 12站 = Agent的数据源 (数据层)
- AIShield = Agent的安全+工具层 (安全层+经济层)

## 部署

```bash
# API服务
cd aishield/server && python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8420

# AIShield合规服务
cd aishield/aishield && bash aishield.sh start

# MCP Server
cd aishield/mcp && npm install && npm run build
```

## 支付

- Creem Store ID: sto_7gBcCekvUKTpsaAFyf (与12站共用)
- 虎皮椒(支付宝): 已配置
