# AIShield Agent 生态位分发版图（2026-08-15 实测）

> 本文件是「扫描所有开源平台 + 补齐 agent 生态位空白」的执行交付。所有「线上状态」均经 curl/WebFetch 实测，不靠推理。
> 维护：`aishield-ops` skill。配套台账：`api/data/mcp_submissions.json`、`distribution/published.json`。

## TL;DR（5 条关键结论）

1. **官方 MCP Registry：AIShield 实际【未上架】。** `GET /v0/servers/io.github.lm203688/aishield` 与 `/v0.1/...` 均 404，API 明确承认路径正确但条目不存在。此前「已 verified」的判断是**错误/过期的**，本次纠正。这是一个 HIGH 缺口，不是「无需操作」。
2. **品牌被同名云 SaaS 抢占。** 独立商业产品 **aishield.ai（owner `aishield-ai`）** 已上架 LobeHub（`aishield-ai/aishield`）、himcp.cn，带定价/API Key/「AI 语义分析」。agent 搜 "AIShield" 很可能先撞到它，而非我们的本地开源版。
3. **LobeHub 上的 "AIShield" 不是我们。** 那是上面的云 SaaS；我们的开源版在 LobeHub **缺位**。
4. **ClawHub 被第三方 squatting。** `clawhub/ai-shield-audit`（laurentaia，OpenClaw 审计，81/100，144K 安装）占了极易混淆的名字；我们**完全缺席** ClawHub。
5. **我们真实已上架的只有 Glama + npm。** Glama `lm203688/aishield`（id `gso85mvobx`）已确认是我们的；npm `aishield-mcp-server` 4.2.2 已发。「利用所有平台」离完成很远。

---

## §1 平台版图实测表（2026-08-15）

| 平台 | 我们的状态 | 提交方式 | 门槛 | 优先级 | 备注 / 证据 |
|---|---|---|---|---|---|
| **Official MCP Registry** | ❌ **未上架**（404 实测） | PR 到 `modelcontextprotocol/registry` 的 `servers/` | GitHub PR（用户） | **HIGH** | `registry/server.json` 已备；但含一个指向 `aishield.tools/api/v1/mcp` 的 streamable-http remote，而 aishield.tools 是纯静态站、无此后端 → 建议改 **stdio-only** 再提 |
| **Glama** | ✅ **已上架**（lm203688/aishield, gso85mvobx） | 从 GitHub repo 自动同步 | 无（已 live） | done | 页面丰富（227/233 规则、内容安全平面 thesis）；但描述偏「云 API（注册/Key/定价/8450 端口）」，**模糊了本地定位**——需修正以区隔 aishield.ai |
| **npm `aishield-mcp-server`** | ✅ 4.2.2 已发 | npm | done | done | 包名正确 |
| **LobeHub** | ⚠️ 被云 SaaS 占位；我们缺位 | 网页提交 | 账号 | **HIGH** | 搜 "AIShield" 命中 `aishield-ai/aishield`（云 SaaS）；我们的开源版未单独上架 |
| **Smithery** | ❌ 未发布 | 网页 dashboard（GitHub 登录，连 repo） | 账号 | **HIGH** | stdio-only → 走「self-hosted」列出（非 one-click）；需有人在 smithery.ai/new 发布。server-card.json 已就位可被扫 |
| **ClawHub** | ❌ 缺位 + 第三方 squat | `clawhub skill publish` | GitHub 登录（需够老账号） | **HIGH** | `ai-shield-audit`（laurentaia）已占混淆名；我们须以 `aishield` 认领命名空间 |
| **MCP.so** | ❌ 未找到 | 网页表单 / GitHub Issue | 账号 | MED | 搜索无命中 |
| **PulseMCP** | ❓ 未核实（大概率未上） | 网页 dashboard | 账号 | MED | 子代理报「auto-ingest」但实测搜索未证实；需有人手动发布 |
| **GitHub Marketplace (Action)** | ❌ 未发布 | release + 勾选 Publish | **独立干净仓库**（见下）+ 接受协议 | MED | 硬约束：动作仓库**不得含任何 workflow 文件**；主仓有 18 个 `.github/workflows` → 必须新建独立仓库 `lm203688/aishield-action` |
| **HuggingFace** | ❌ 源在仓未发 | 上传 dataset card | 账号 | LOW | `distribution/huggingface/` 源就绪 |
| **MCPfinder (mcpfind.org)** | ❌ 未做 | 提交 | 账号 | LOW | 索引 6700+ server，性价比高 |
| **A2A Registry / AgentSpace** | ❌ 未做 | 注册 Agent Card | 调研 | LOW | Agent Card 已备（`docs/.well-known/agent-card.json`） |
| **aishield.tools 本域发现文件** | ⚠️ **stale 4.2.0/133** | CF Pages 重建 | CF token（权限不足） | HIGH（已知） | 之前 15 文件修复未触达线上；3 个 `cfut_` token 权限都够不到该部署 |
| **DeepSeek Harness (DSH)** | ❌ 缺位（生态首日，security 类目真空） | ① DSH Plugins 目录投稿（deepbolt.xyz）② 原生 `dsh-aishield` 插件（npm+cordis.patch.yml）③ MCP 桥接：DSH 原生支持 MCP → AIShield MCP server 零适配 | 目录投稿需账号 / 插件需 npm 发布 | **HIGH（新渠道·先发窗口）** | 首日 34k–65k★、1000+ 插件；supply-chain 风险是官方头号隐患→AIShield 本职；**无安全插件**→先发占 security 类目。dev preview+breaking changes→走 MCP 桥接最稳 |

---

## §2 品牌碰撞威胁（最被低估的风险）

### 2.1 aishield.ai 同名云 SaaS
- 独立公司产品，**同名 "AIShield"**，owner `aishield-ai`，已上 LobeHub + himcp.cn。
- 卖点：定价阶梯（Free/Pro ¥29/Enterprise ¥199）、API Key、注册送积分、「AI 语义分析」、30+ 正则。
- **威胁**：agent / 开发者搜 "AIShield" → 先见云 SaaS → 我们的「本地、开源、代码不出机」差异化被淹没。
- **我们的错位武器**：不是功能多少，是**部署模型**。Glama/llms.txt/README 的文案必须把「local / no-cloud / your code never leaves your machine」打到最前，把云 Trust API 降为「可选」。否则我们自己 Glama 页（写着注册/Key/定价）也在帮 aishield.ai 混淆认知。

### 2.2 ClawHub `ai-shield-audit` squatting
- `clawhub/ai-shield-audit`（laurentaia）OpenClaw 安全审计，81/100、社区验证、144K 安装。
- 名字与 "AIShield" 高度混淆，且做的是**同一件事（审计 agent 配置）**——是直接的认知劫持。
- **动作**：尽快以 `aishield` 名义在 ClawHub 发布我们的 skill（见 §4），抢回命名空间。

---

## §3 R&D 参考：竞品如何被 agent 发现 / 衔接（可迁移模式）

| 参考项目 | 分发/衔接模式 | 可迁移到 AIShield |
|---|---|---|
| **agent-security-scanner-mcp** (sinewaveai) | **一引擎三态**：MCP Registry 条目 + OpenClaw 插件 + 技能目录同步发布 | 我们也应「一套引擎、多表面」：Registry + ClawHub skill + GitHub Action + npm 一次铺齐，不依赖单一渠道 |
| **mcp-audit** (Adam Dudley) | **多形态**：CLI + 编辑器扩展 + 独立二进制 + 库，多入口触达开发者 | 在开发者「出现的地方」铺：Action（CI）、skill（agent 运行时）、npm（脚本）、ClawHub（agent 应用商店） |
| **Smithery** | streamable-http = one-click 安装；stdio = self-hosted 列出（仍可被搜到） | AIShield 是 stdio，走 self-hosted 列出即可——**发现价值不依赖 one-click** |
| **ClawHub** | skill = 文件夹 + `SKILL.md`（frontmatter 含 name/description/version/requires）；`clawhub skill publish` 发布；命名空间竞争激烈 | 证明命名空间是资产；我们必须抢 `aishield`。frontmatter 的 description 要带「local / offline / 不执行被扫配置」关键词以利 agent 检索 |
| **Glama** | 从 GitHub repo 的 README/llms.txt **自动同步**；描述即门面 | 保持 repo 内 llms.txt / README / server-card 的「本地优先」措辞一致，Glama 页才会准确区隔云 SaaS |
| **Official MCP Registry** | PR 到 `modelcontextprotocol/registry`，人工复核（数工作日）；`server.json` 即产物 | 我们 `registry/server.json` 已备；修正为 stdio-only 后提 PR 即可（用户操作） |
| **aishield.ai（云 SaaS）** | 4D 评分 + badge + Guardrail MCP + API——**UX 表面和我们几乎一样** | 印证「功能集雷同，差异在部署模型」。我们的 listing 文案须靠「local/no-cloud」切割，而非堆功能 |

**核心结论**：agent 生态位的占领 = **多表面铺货 + 命名空间认领 + 一致的「本地」叙事**。没有哪个单渠道能闭环，但 Registry（agent 客户端原生发现）+ ClawHub（agent 应用商店）+ Glama（web 发现）是覆盖率最高的三件套，目前我们只占了 Glama。

---

## §4 行动 backlog（用户动作 vs AI 可准备）

### A. 需用户手动（账号/登录硬阻塞）
1. **Official MCP Registry 提 PR**：以 `registry/server.json`（改 stdio-only，去掉死 remote）向 `modelcontextprotocol/registry` 提 PR。→ 用户 fork/PR 或授权我代提（需该仓写权限 PAT）。
2. **Smithery 发布**：登录 smithery.ai/new → 连 GitHub repo `lm203688/aishield` → 发布（self-hosted）。
3. **LobeHub 认领/发布**：登录 LobeHub → 发布我们的开源 AIShield（与云 SaaS `aishield-ai` 区分，description 标 local）。
4. **ClawHub 发布**：`clawhub login`（需够老 GitHub 账号）→ `clawhub skill publish distribution/clawhub`（本文件已备骨架）。
5. **MCP.so / PulseMCP / MCPfinder**：网页表单提交（描述同上，强调 local）。
6. **GitHub Marketplace**：新建独立仓库 `lm203688/aishield-action`（不含 workflow），把 `action.yml`+`action_entrypoint.py` 移入，打 release 勾选 Publish + 接受 Marketplace 协议。
7. **aishield.tools CF Pages 重建**：在 CF dashboard（61960005 账户）→ 真实托管前端的 Pages 项目 → Deployments → Retry（3 个 `cfut_` token 权限不足，无法 API 触发）。
8. **HuggingFace**：上传 `distribution/huggingface/`。
9. **DeepSeek Harness (DSH)**：① 在 deepbolt.xyz DSH Plugins 提交我们的 listing（草稿 `distribution/deepseek-harness/DSH-PLUGINS-LISTING.md`）；② `npm publish dsh-aishield`（需登录 npm，且等 DSH Cordis API 稳定再补 `index.js` 注册体）；③ 对外文档写清 MCP 桥接方式（DSH 原生支持 MCP，AIShield server 零适配接入）。

### B. 本轮 AI 已准备 / 可直接执行
- ✅ 实测全平台状态，纠正「Registry 已 verified」误判（本报告）。
- ✅ 台账 `mcp_submissions.json` 已按真相更新（Registry→not_listed，Glama→listed，新增 LobeHub/ClawHub/Smithery/MCP.so/GitHub Marketplace 缺口 + 品牌碰撞标记）。
- ✅ 竞争态势 `competitive-landscape.md` 新增 §8（分发版图 + aishield.ai 同名威胁）。
- ✅ GEO 线索 `geo-content-leads.md` 新增「本地 vs 云 SaaS 品牌切割」lead。
- ✅ 准备 ClawHub skill 骨架 `distribution/clawhub/SKILL.md`（待用户登录发布）。
- ✅ 准备 DeepSeek Harness 认领资产 `distribution/deepseek-harness/`（`dsh-aishield` 插件骨架 package.json/cordis.patch.yml/index.js + DSH Plugins 目录投稿草稿 + 匹配策略 README）。
- ⏳ （建议）将 `registry/server.json` 改为 stdio-only 并提 PR——若用户给该仓写权限 PAT，我可代提。

---

## §5 本轮回测证据（可复现）
- `curl .../v0/servers/io.github.lm203688/aishield` → 404（API 提示正确路径但条目不存在）
- `curl .../v0.1/servers/io.github.lm203688/aishield` → 404
- `WebFetch glama.ai/mcp/servers/lm203688/aishield` → 确认是我们的（227/233 规则、内容安全平面）
- `WebSearch "aishield" site:mcp.so` → 无命中
- `WebSearch clawhub ai-shield-audit` → laurentaia 版 144K 安装、81/100
- `WebFetch lobehub.com/en/mcp/aishield-ai-aishield` → 云 SaaS（aishield.ai，定价/Key）
