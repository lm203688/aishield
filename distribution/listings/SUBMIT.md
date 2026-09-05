# AIShield 多渠道投稿台账（一键复制）

> 用途：把各平台的「去哪提交 / 贴什么」固化成可直接复制的文本，降低手动发布摩擦。
> 维护节奏：由自动化 `AIShield 多渠道分发缺口巡检` 每周核对状态并刷新本文件。
> 最后人工核对：2026-08-15（curl/WebFetch 实测）。
> 最后自动巡检：**2026-09-05**（curl 实测；本域 drift 已随 4.3.0 发版消除，详见表内 aishield.tools 两行）。

---

## ⚠️ 核验方法铁律（2026-08-22 血的教训，务必遵守）

历史上本台账把 Official MCP Registry 记成「未上架」长达两周，根因是**用了不存在的 API 路径**，把「端点 404」误读成「条目 404」：

| ❌ 错误做法 | ✅ 正确做法 |
|---|---|
| `GET /v0/servers/io.github.lm203688/aishield` → 返回 `{"detail":"Endpoint not found. See /docs..."}` 404。**这是端点不存在，不是我们没上架！** | `GET /v0/servers?search=aishield&limit=10` → 返回 servers 数组，看 `_meta["io.modelcontextprotocol.registry/official"].isLatest` 为 true 的那条 |
| `GET /api/health`、`/api/rules/stats` → 404，据此判定 aishield.tools「无后端」 | 真实后端在 **`/api/v1/*`**：`GET /api/v1/health` → 200；`POST /api/v1/mcp` (JSON-RPC `tools/list`) → 200 且返回 8 个工具 |
| `curl -sL https://lm203688.github.io/aishield/...` 判定 GitHub Pages 内容 | github.io **301 跳到 aishield.tools**（CNAME 所致），加 `-L` 等于在测 CF Pages。要测 GH Pages 自身内容**已不可能**——它是死端表面 |

**通用铁律**：404 要先分清「端点不存在」还是「资源不存在」——读 response body，不要只看 status code。任何「未上架 / 无后端 / 已失效」结论必须附可复现的 curl 命令 + body 片段。

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

## 1. Official MCP Registry（✅ 已上架 — 2026-08-22 纠正）

- **状态**：✅ **已上架且 active**。此前「未上架/404」是**核验方法错误**导致的误判，本次纠正。
- **实测证据（2026-08-22）**：
  ```
  curl -sS --ssl-no-revoke --tlsv1.3 \
    "https://registry.modelcontextprotocol.io/v0/servers?search=aishield&limit=10"
  ```
  返回 2 条同名条目，最新那条：

  | 字段 | 值 |
  |---|---|
  | name | `io.github.lm203688/aishield` |
  | title | AIShield Security Scanner |
  | version | **4.2.2** ✅ 与基线一致 |
  | status | **active** |
  | isLatest | **true** |
  | publishedAt | 2026-08-07T12:54:18Z |
  | packages | `aishield-mcp-server` 4.2.2 · transport **stdio** ✅ |
  | remotes | `streamable-http` → `https://aishield.tools/api/v1/mcp` |

- **无需提 PR**：条目已在册（推测由 `.github/workflows/publish-mcp-registry.yml` 发布）。此前「fork + 提 PR」的指引**作废**，勿重复提交造成重复条目。
- **⚠️ 唯一遗留缺陷**：在册条目的 `remotes` 指向 `aishield.tools/api/v1/mcp`。该端点**并未失效**（POST JSON-RPC 实测 200，返回 8 个工具、工具名正确为 `aishield_*`），但**其自报版本/规则数陈旧**（`/api/v1/health` 返回 `version: "4.2"`、`rules_count: 133`，基线应为 4.2.2 / 227）。即 agent 若走 remote 通道可用，但会读到过时元数据。
- **⚠️ 本地 `registry/server.json` 与在册条目不一致**：本地版本已被删掉 `remotes` 段（当时误判其为死端）。既然实测 remote 活着，**是否要在下次发版时移除 remote 变成 stdio-only，是一个待用户拍板的决策**（移除 = 少一个可发现表面；保留 = 需先修后端 stale 元数据）。
- **更新方式**：发新版本时由 `publish-mcp-registry.yml` 推送，不走 PR。

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

> 状态截止 **2026-09-05** 自动巡检（全部经 curl 实测）。

| 渠道 | 状态 | 资产就绪 | 需用户手动 |
|---|---|---|---|
| Official MCP Registry | ✅ **已上架 active 4.2.2**（2026-08-22 纠正误判） | ✅ 在册 | 无（remote 元数据 stale 待决策） |
| Glama | ✅ 已上架（2026-08-22 复测 200） | ✅ README/llms.txt 已去云化(2026-08-15) | 后台短描述待用户登录改 |
| npm | ✅ 4.2.2（2026-08-22 复测 latest=4.2.2） | — | — |
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
| aishield.tools 静态发现文件 | ✅ **已修复 4.3.0**（2026-09-05 复测：227 MCP/233 skill、6 工具名正确） | ✅ main 已是 4.3.0 正确 | 无（drift 随 4.3.0 发版消除，CF Pages Retry 不再需要） |
| aishield.tools `/api/v1` 后端 | ✅ **已修复 4.3.0/228**（2026-09-05 复测；commit 93fcd10c，deployed 2026-09-01） | — | 无（随 4.3.0 发版部署，元数据已新鲜） |
| GitHub Pages（github.io） | ⛔ **死端表面**：301→aishield.tools，内容不可达 | — | 无（勿再修，见下） |

### 表面拓扑（2026-08-22 实测厘清）

```
main 分支 (✅ 4.2.2 / 227 / aishield_*  ← 唯一正确的真相源)
  │
  ├── GitHub Pages ── pages.yml 构建成功 ──► github.io ──301(CNAME)──► aishield.tools
  │                                                                    （自身内容永不可达 = 死端）
  ├── Cloudflare Pages ──► aishield.tools 静态页 + .well-known/*  ⚠️ stale 4.2.0/133
  └── 某后端 origin ─────► aishield.tools/api/v1/*                ⚠️ stale 4.2/133（但工具名对）
```

**结论**：main 是对的，两个线上表面都是旧的。`pages.yml` 修不修都不影响 aishield.tools —— 唯一解是**重建 CF Pages + 重新部署后端**。

**⚠️ 附带发现（待用户拍板，本自动化未擅自改动）**：`pages.yml` 的 `3-Verify Reachable` 用 `curl -sL .../github.io/aishield/blog/` 探测，因 301 实际测的是 **CF Pages**，只要 aishield.tools 返回 200 就判绿 —— 即便内容 stale 也永远 success（78 次运行全绿）。这是一处**假绿门禁**（"恒定输出的门禁等于没门禁"）。建议改为断言内容新鲜度（抓 `.well-known/mcp/server-card.json` 断言 `version == 4.2.2`），这样 drift 会真实报红。此项属 workflow 改动，超出本自动化「只更新台账」职责，需用户授权。
