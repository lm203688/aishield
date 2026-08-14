# AIShield 多渠道投稿台账（一键复制）

> 用途：把各平台的「去哪提交 / 贴什么」固化成可直接复制的文本，降低手动发布摩擦。
> 维护节奏：由自动化 `AIShield 多渠道分发缺口巡检` 每周核对状态并刷新本文件。
> 最后人工核对：2026-08-15（curl/WebFetch 实测）。

---

## 通用「本地优先」投稿文案（所有平台复用，用于区隔同名云 SaaS aishield.ai）

**标题/Name**：`AIShield (local, open-source)`

**一句话描述（Short）**：
> Local-first, open-source AI-tool security scanner for MCP servers, AI skills, GPTs and prompts. OWASP MCP Top 10 + Agentic ASI01–10. 227 MCP / 233 skill rules. Runs fully offline — your code never leaves your machine.

**长描述（Long）**：
> AIShield is a **local-first, open-source** security scanner for the agent ecosystem. It scans MCP servers, AI skills, GPTs and prompts for tool poisoning, prompt injection and supply-chain risks, aligned to OWASP MCP Top 10 + Agentic AI Top 10 (ASI01–ASI10). The rule base covers 227 MCP + 233 skill rules, with zero third-party runtime dependencies (urllib only) and an optional remote LLM semantic backend.
>
> **Why local-first matters:** AIShield runs entirely on your machine. It never uploads your code or config, never spawns commands found inside the artifact being scanned, and can run 100% offline. This is the open-source edition — distinct from the cloud SaaS `aishield.ai`.

**关键标签**：`security` `mcp` `scanner` `owasp` `agent-security` `prompt-injection` `supply-chain` `local-first` `open-source`

**仓库 / 安装**：
- Repo: `https://github.com/lm203688/aishield`
- MCP server: `npx -y aishield-mcp-server`
- 官网: `https://aishield.tools`

---

## 1. Official MCP Registry（HIGH · 需向 modelcontextprotocol/registry 提 PR）

- **状态**：❌ 未上架（实测 404）。`registry/server.json` 已备且 **stdio-only**（已去掉指向死端 `aishield.tools/api/v1/mcp` 的 remote）。
- **去哪**：fork `https://github.com/modelcontextprotocol/registry` → 在 `servers/` 下加 `io/github/lm203688/aishield.json`（内容同 `registry/server.json`）→ 提 PR。
- **粘贴内容**：直接复制仓库根 `registry/server.json` 全文。
- **注意**：人工复核数工作日；描述已本地优先，勿改成云 API 口吻。

## 2. LobeHub（HIGH · 被同名云 SaaS 占位，须以开源版区隔）

- **状态**：⚠️ LobeHub 现有 `aishield-ai/aishield` = 云 SaaS（aishield.ai），**非我们**。我们的开源版缺位。
- **去哪**：登录 LobeHub → Publish / Submit MCP → 填我们的开源版。
- **粘贴内容**：用上方「通用本地优先文案」，并在描述首句加：**“Open-source local edition — not the aishield.ai cloud SaaS.”**
- **MCP 端点**：`npx -y aishield-mcp-server`（stdio）。

## 3. MCP.so（MED · 网页表单）

- **状态**：❌ 未找到（搜索无命中）。
- **去哪**：`https://mcp.so` → Add MCP Server / Submit。
- **粘贴内容**：上方「通用本地优先文案」。

## 4. PulseMCP（MED · dashboard 提交）

- **状态**：❓ 未核实（子代理报 auto-ingest 但实测搜索未证实）。
- **去哪**：`https://www.pulsemcp.com` → 登录 → Submit a server → 连 `lm203688/aishield`。
- **粘贴内容**：上方「通用本地优先文案」。

## 5. MCPfinder / mcpfind.org（LOW · 高性价比索引）

- **状态**：❌ 未做（索引 6700+ server）。
- **去哪**：`https://mcpfind.org` → Submit。
- **粘贴内容**：上方「通用本地优先文案」。

## 6. A2A Registry / Google AgentSpace（LOW · Agent Card 注册）

- **状态**：❌ 未做。Agent Card 已备（`docs/.well-known/agent-card.json`）。
- **去哪**：A2A Registry（`a2aregistry.org`）或 Google AgentSpace → 注册 Agent Card。
- **粘贴内容**：上传/引用 `docs/.well-known/agent-card.json`（已含 `authentication` 字段与 227 规则数）。

---

## 7. GitHub Marketplace Action（MED · 独立仓库）

- **状态**：✅ 源码就绪于 `distribution/github-marketplace/`（action.yml + 自包含 action_entrypoint.py + Dockerfile + README）。
- **去哪**：新建独立仓库 `lm203688/aishield-action`（**不得含任何 workflow 文件**）→ 推入本目录内容 → 打 Release 勾选 Publish to Marketplace。
- **详见**：`distribution/github-marketplace/README.md`。

## 8. Smithery（HIGH · 仓库根清单已就位）

- **状态**：✅ `smithery.yaml` 已放仓库根；登录 smithery.ai/new 连 `lm203688/aishield` 即可发布（stdio = self-hosted 列出，仍可被搜到）。
- **去哪**：`https://smithery.ai/new` → 连 GitHub repo。

## 9. DeepSeek Harness / DSH（HIGH · 先发窗口）

- **状态**：✅ 认领资产就绪 `distribution/deepseek-harness/`。
- **去哪**：① deepbolt.xyz DSH Plugins 投我们的 listing（草稿 `DSH-PLUGINS-LISTING.md`）；② `npm publish dsh-aishield`（等 DSH Cordis API 稳再补 `index.js` 注册体）。

---

## 发布状态速查（每周由自动化刷新）

| 渠道 | 状态 | 资产就绪 | 需用户手动 |
|---|---|---|---|
| Official MCP Registry | ❌ 未上架 | ✅ server.json | PR |
| Glama | ✅ 已上架 | — | 修正描述去云化 |
| npm | ✅ 4.2.2 | — | — |
| LobeHub | ⚠️ 被 SaaS 占位 | ✅ 文案 | 登录发布开源版 |
| Smithery | ❌ 未发布 | ✅ smithery.yaml | 登录发布 |
| ClawHub | ❌ 缺位+squat | ✅ SKILL.md | clawhub publish |
| MCP.so | ❌ | ✅ 文案 | 表单 |
| PulseMCP | ❓ | ✅ 文案 | dashboard |
| MCPfinder | ❌ | ✅ 文案 | 表单 |
| GitHub Marketplace | ❌ | ✅ 源码 | 建独立仓库发布 |
| HuggingFace | ❌ | ✅ README | 上传 |
| A2A Registry | ❌ | ✅ agent-card | 注册 |
| DSH | ❌ | ✅ 全套 | 投稿+npm |
| aishield.tools 本域 | ⚠️ stale 4.2.0/133 | ✅ 源码已修 | CF Retry |
