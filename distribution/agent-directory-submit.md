# AIShield · agent 原生目录投稿强化清单（按 ROI 排序，本周可执行）

> 配套台账：`distribution/listings/SUBMIT.md`（各渠道完整 paste 文案与状态速查）。
> 本文件是"行动层"：挑最高 ROI 的渠道，给一次性可执行步骤 + 精简粘贴文本，便于一个 sitting 内做完。
> 铁律：所有动作需用户登录对应平台；AI 不代登录、不改任何外部平台状态。

## 优先级总览

| 序 | 渠道 | ROI | 资产状态 | 动作 |
|---|---|---|---|---|
| 1 | Smithery | 高 | ✅ `smithery.yaml` 就位 | 登录即发 |
| 2 | ClawHub | 高（抢命名空间） | ✅ `distribution/clawhub/SKILL.md` | `clawhub publish` |
| 3 | Official MCP Registry | 高 | ✅ `registry/server.json`(stdio-only) | 提 PR |
| 4 | MCP.so / PulseMCP / MCPfinder | 中/低 | ✅ 文案 | 表单 / dashboard |
| 5 | GitHub Marketplace | 中 | ✅ 独立仓库源码 | 建仓发布 |
| 6 | DSH | 高（先发窗口） | ✅ `distribution/deepseek-harness/` | 投稿 + npm |
| 7 | HuggingFace / A2A Registry | 低 | ✅ README / agent-card | 上传 / 注册 |

## 今日 30 分钟可做完的 3 件

1. **Smithery**：打开 `https://smithery.ai/new` → 连 GitHub 仓库 `lm203688/aishield` → 发布（stdio = self-hosted 也会被搜到）。仓库根 `smithery.yaml` 已就位，无需改文案。
2. **ClawHub**：`clawhub publish` 发布 `distribution/clawhub/SKILL.md`，抢 `aishield` 命名空间（当前被 `ai-shield-audit` squat，我们是正主）。
3. **Official MCP Registry**：fork `modelcontextprotocol/registry` → 在 `servers/` 下加 `io/github/lm203688/aishield.json`（内容同 `registry/server.json`，已改 stdio-only，去掉死端 remote）→ 提 PR。

## 通用精简粘贴文案（各表单复用）

- **标题 / Name**：`AIShield (local, open-source)`
- **短描述**：Local-first, open-source AI-tool security scanner for MCP servers, AI skills, GPTs and prompts. OWASP MCP Top 10 + Agentic ASI01–10. 227 MCP / 233 skill rules. Runs fully offline — your code never leaves your machine.
- **仓库**：https://github.com/lm203688/aishield
- **安装**：`npx -y aishield-mcp-server`
- **官网**：https://aishield.tools
- **标签**：`security` `mcp` `scanner` `owasp` `agent-security` `prompt-injection` `supply-chain` `local-first` `open-source`

## 完成后

- 在 `distribution/listings/SUBMIT.md`「发布状态速查」表更新对应渠道状态；
- 下次 `AIShield 多渠道分发缺口巡检` 自动化运行会自动复核对账。
