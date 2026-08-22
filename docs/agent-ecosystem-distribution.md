# AIShield Agent 生态位分发版图（2026-08-15 实测）

> 本文件是「扫描所有开源平台 + 补齐 agent 生态位空白」的执行交付。所有「线上状态」均经 curl/WebFetch 实测，不靠推理。
> 维护：`aishield-ops` skill。配套台账：`api/data/mcp_submissions.json`、`distribution/published.json`。

## TL;DR（5 条关键结论）

1. ~~**官方 MCP Registry：AIShield 实际【未上架】。**~~ 🔴 **2026-08-22 二次纠正：此条本身是错的 —— AIShield 实际【已上架且 active】。** 之前用的 `GET /v0/servers/{name}` 是**不存在的 API 端点**（body 明写 `"Endpoint not found. See /docs"`），把「端点 404」误读成「条目 404」。正确查法 `GET /v0/servers?search=aishield` 返回在册条目：`io.github.lm203688/aishield`，version **4.2.2**，status **active**，`isLatest: true`，publishedAt 2026-08-07。**无需提 PR，勿重复提交。** 教训：404 必须先读 body 分清「端点不存在」vs「资源不存在」。
2. **品牌被同名云 SaaS 抢占。** 独立商业产品 **aishield.ai（owner `aishield-ai`）** 已上架 LobeHub（`aishield-ai/aishield`）、himcp.cn，带定价/API Key/「AI 语义分析」。agent 搜 "AIShield" 很可能先撞到它，而非我们的本地开源版。
3. **LobeHub 上的 "AIShield" 不是我们。** 那是上面的云 SaaS；我们的开源版在 LobeHub **缺位**。
4. **ClawHub 被第三方 squatting。** `clawhub/ai-shield-audit`（laurentaia，OpenClaw 审计，81/100，144K 安装）占了极易混淆的名字；我们**完全缺席** ClawHub。
5. ~~**我们真实已上架的只有 Glama + npm。**~~ 🔴 **2026-08-22 更正为：Glama + npm + Official MCP Registry（三处）。** Glama `lm203688/aishield`（id `gso85mvobx`）；npm `aishield-mcp-server` 4.2.2；Registry `io.github.lm203688/aishield` 4.2.2 active。「利用所有平台」仍未完成，但起点比此前记录的更好。

---

## 周报 2026-08-17（本周重大变化 · 经实测）

> 本周生态显著升温：**竞品把「本地/离线」做成标配并补上企业漏洞管理闭环**，而 **aishield.ai 开始蹭我们的「本地」叙事且其 npm 短名仍空闲**。

- 🔴 **[品牌·aishield.ai 升级威胁]** LobeHub 条目 `aishield-ai/aishield` 现被标为 **「Local Service / 仅在客户端本地设备运行」**，公然蹭我们的「本地优先」叙事；其 LobeHub + himcp 安装指令写 `npx aishield-mcp`、`npx aishield-guardrail`、`pip install aishield`，但**实测 npm `aishield-mcp` 与 `aishield-guardrail` 均 404（不存在）**、PyPI `aishield` 存在 → 其安装指令失效，且 `aishield-mcp` 短名**仍空闲，是防御性抢注机会**（见 §1 新增行）。另：直接访问 `aishield.ai` 首页已变「Premium Domain For Sale」页，品牌或处于出售/动荡期，但其 marketplace 列表仍指向在线 API（`aishield.ai/api/v1`），需持续监控。
- 🔴 **[竞品 #1·mcp-audit]** `mcp-audit-scanner` 0.14.0（仍全离线）新增 **89 条 Semgrep SAST 规则、CVE 打标（CVE-2026-30615）、Nucleus FlexConnect 企业漏洞管理对接、Sigstore 签名校验、fleet 部署、governance policy-as-code、`watch` 实时监控**。已补上我们缺失的「企业漏洞管理闭环」，是同类最强直接竞品。注意空间内现出现 3 个同名/近名 mcp-audit（danush-aries / saagpatel / appsecsanta），用户易混淆。
- 🔴 **[竞品 #2·Sunglasses 新晋强敌]** `sunglasses-dev/sunglasses`：MIT、**100% 本地、无云依赖、无遥测**，1049 模式 / 7653 关键词 / 17 归一化 / 23 语言、0.261ms/输入，覆盖 prompt injection + MCP 工具投毒 + 跨 agent 注入 + 凭证外泄 + 「Proof Before Action」一次性容器。直接对冲我们的「本地/不出机」楔子。
- 🟠 **[竞品 #3·Snyk Agent Scan]** 原 MCP-Scan（2026-04 被 Snyk 收购）v0.5.12，自动发现 10+ agent 的 skill + MCP 配置；凭 Snyk 企业渠道分发。同周 `owasp-agentic-mcp` 1.0.9（OWASP Agentic AI Top10，上 Smithery）、`mcp-security-auditor` 1.0.0（MIT、SIEM 对接）也在补覆盖。LobeHub 上本地优先安全代理/防火墙集群（mcp-firewall / Steiner / Palizade / MCPVet / mcpguard / Sentinel Warden / op-injection-scanner）持续膨胀，类别噪音增大但验证「本地」是主流方向。
- 🟠 ~~**[渠道·Registry]** 本周实测 Official MCP Registry 仍 404（/v0 与 /v0.1 均 404），我们仍未上架——HIGH 缺口不变。~~ ⛔ **此条已被 2026-08-22 推翻**：404 来自查了**不存在的端点** `/v0/servers/{name}`，实际条目一直在册（4.2.2 active）。见「周报 2026-08-22」。
- 🟡 **[ClawHub]** `ai-shield-audit`（laurentaia）squatting 仍在，并扩展至 ClawBox 硬件（€549，4.7★）；ClawHub 曾曝排名操纵漏洞（2026-03 披露，已修）。命名空间高风险但认领价值仍在。

**行动建议（用户侧，AI 不代发/不代提）**：① 防御性抢注 npm `aishield-mcp`（空闲，阻断恶意占用，与 `aishield-mcp-server` 形成家族）；② 若 aishield.ai 域名确在出售，评估低成本回收品牌域名；③ 竞品已把「本地」做成标配并补企业漏洞管理，我们的差异化须上移到 **「内容安全平面 + 主动治理（kill switch / 持续鉴证）+ 机器可结算认证」**，而非仅「本地扫描」。

---

## 周报 2026-08-22（自动巡检 · 两处长期误判被纠正）

> 本周没有新渠道变化，但**发现台账自身有两处硬错误**，都是「404 读错含义」造成的。纠正后我们的实际分发面比记录的更好，但线上 drift 比记录的更严重。

- 🟢 **[纠正 1 · Registry 其实已上架]** Official MCP Registry 条目 `io.github.lm203688/aishield` **version 4.2.2 / status active / isLatest true / publishedAt 2026-08-07**。此前两周记的「404 未上架 · HIGH 缺口」是查了**不存在的端点** `/v0/servers/{name}`（body 明写 `Endpoint not found. See /docs`）。正确查法：`/v0/servers?search=aishield`。**「提 PR」动作作废**，重复提交会造成重复条目。
- 🔴 **[纠正 2 · aishield.tools 有活后端，且后端也 stale]** 旧判断「aishield.tools 是纯静态站、无后端、registry remote 指向死端」错误。实测 `GET /api/v1/health` → 200 `{"version":"4.2","rules_count":133}`；`POST /api/v1/mcp` (`tools/list`) → 200 返回 **8 个工具**，工具名**正确**（`aishield_*` 6 个 + `agent_register`/`agent_quick_scan`）但描述仍写 133 rules。旧探测查的 `/api/health`、`/api/rules/stats` 确实 404 —— **路径前缀记错**（真实前缀是 `/api/v1`）。→ drift 面从「1 处静态文件」扩大为「静态文件 + 后端」**2 处**。
- 🔴 **[新发现 · pages.yml 假绿门禁]** `github.io/aishield/...` **301 跳 aishield.tools**（CNAME 所致），而 `pages.yml` 的 `3-Verify Reachable` 用 `curl -sL` 探测 → 实际在测 CF Pages，只要 aishield.tools 返 200 就判绿。**78 次运行全 success，却从未验证过 GitHub Pages 自己的产物，更未发现内容 stale。** GitHub Pages 是死端表面，修它不影响线上域名；建议把 verify 改为断言 `.well-known/mcp/server-card.json` 的 `version == 4.2.2`，让 drift 真实报红（属 workflow 改动，待用户授权）。
- 🟢 **[无变化]** npm `aishield-mcp-server` latest = **4.2.2**（modified 2026-08-07）；Glama `lm203688/aishield` 复测 **200** 仍 live；`get_rule_count()` = **227** 基线确认。
- ⚠️ **[drift 连续第 3 周未修]** aishield.tools 静态 `.well-known/mcp/server-card.json` + `agent-card.json` 仍 **4.2.0 / 133 rules / 错工具名**，而 main 分支 raw 实测已是 **4.2.2 / `aishield_*`**。唯一解仍是 **CF Pages 重建（用户 dashboard Retry）**。

---

## §1 平台版图实测表（2026-08-15，2026-08-17 复核，**2026-08-22 重大纠正**）

| 平台 | 我们的状态 | 提交方式 | 门槛 | 优先级 | 备注 / 证据 |
|---|---|---|---|---|---|
| **Official MCP Registry** | ✅ **已上架 active**（2026-08-22 纠正） | 已在册，由 `publish-mcp-registry.yml` 发版推送 | 无 | done | **2026-08-22 实测 `GET /v0/servers?search=aishield`：`io.github.lm203688/aishield` version 4.2.2 / status active / isLatest true / publishedAt 2026-08-07 / npm pkg stdio ✅。** 此前「404 未上架」是查了不存在的 `/v0/servers/{name}` 端点所致的误判，已作废「提 PR」指引。遗留：在册 `remotes` 指向 `aishield.tools/api/v1/mcp`，该端点**实测活着**（POST JSON-RPC 200，8 工具，工具名正确）但自报 `4.2/133` 元数据陈旧 |
| **Glama** | ✅ **已上架**（lm203688/aishield, gso85mvobx） | 从 GitHub repo 自动同步 | 无（已 live） | done | 页面丰富（227/233 规则、内容安全平面 thesis）；但描述偏「云 API（注册/Key/定价/8450 端口）」，**模糊了本地定位**——需修正以区隔 aishield.ai。**2026-08-17 复测 200，仍 live。** |
| **npm `aishield-mcp-server`** | ✅ 4.2.2 已发（2026-08-07 最后发布） | npm | done | done | 包名正确；2026-08-17 复测 200，latest=4.2.2 |
| **npm `aishield-mcp`（防御性短名）** | ⚠️ **空闲（404）· 建议抢注** | npm | 账号（用户） | **HIGH** | aishield.ai 的 LobeHub/himcp 安装指令写 `npx aishield-mcp`，但该包**实测不存在（404）**；短名仍空闲，恶意方可能抢注劫持。建议以我们名义发布 `aishield-mcp` 作为 `aishield-mcp-server` 的别名入口（AI 不代发，需用户登录） |
| **PyPI `aishield`（aishield.ai 占用）** | ⚠️ 被 aishield.ai 占用 | PyPI | — | LOW | aishield.ai 指令 `pip install aishield` 指向的包存在；我们无 PyPI 同名资产，暂不构成直接劫持但增加混淆 |
| **LobeHub** | ⚠️ 被云 SaaS 占位；我们缺位 | 网页提交 | 账号 | **HIGH** | 搜 "AIShield" 命中 `aishield-ai/aishield`（云 SaaS）；**2026-08-17 新发现：该条目被标为「Local Service / 仅在客户端本地设备运行」，公然蹭「本地」叙事**，而其安装指令 `npx aishield-mcp` 指向的包实际不存在（404）。我们的开源版未单独上架 → 品牌认知被持续稀释 |
| **Smithery** | ❌ 未发布 | 网页 dashboard（GitHub 登录，连 repo） | 账号 | **HIGH** | stdio-only → 走「self-hosted」列出（非 one-click）；需有人在 smithery.ai/new 发布。server-card.json 已就位可被扫 |
| **ClawHub** | ❌ 缺位 + 第三方 squat | `clawhub skill publish` | GitHub 登录（需够老账号） | **HIGH** | `ai-shield-audit`（laurentaia）已占混淆名；我们须以 `aishield` 认领命名空间 |
| **MCP.so** | ❌ 未找到 | 网页表单 / GitHub Issue | 账号 | MED | 搜索无命中 |
| **PulseMCP** | ❓ 未核实（大概率未上） | 网页 dashboard | 账号 | MED | 子代理报「auto-ingest」但实测搜索未证实；需有人手动发布 |
| **GitHub Marketplace (Action)** | ❌ 未发布 | release + 勾选 Publish | **独立干净仓库**（见下）+ 接受协议 | MED | 硬约束：动作仓库**不得含任何 workflow 文件**；主仓有 18 个 `.github/workflows` → 必须新建独立仓库 `lm203688/aishield-action` |
| **HuggingFace** | ❌ 源在仓未发 | 上传 dataset card | 账号 | LOW | `distribution/huggingface/` 源就绪 |
| **MCPfinder (mcpfind.org)** | ❌ 未做 | 提交 | 账号 | LOW | 索引 6700+ server，性价比高 |
| **A2A Registry / AgentSpace** | ❌ 未做 | 注册 Agent Card | 调研 | LOW | Agent Card 已备（`docs/.well-known/agent-card.json`） |
| **aishield.tools 静态发现文件** | ⚠️ **stale 4.2.0/133/错工具名**（2026-08-22 连续第 3 周未变） | CF Pages 重建 | CF token（权限不足） | HIGH（已知） | main 分支实测已是 4.2.2 + `aishield_*` 正确（raw.githubusercontent 复验），线上未跟进；3 个 `cfut_` token 权限都够不到该部署 |
| **aishield.tools `/api/v1` 后端** | ⚠️ **活着但 stale** | 后端重新部署 | 需定位 origin | HIGH（新发现） | **2026-08-22 纠正「aishield.tools 无后端」旧判断**：`GET /api/v1/health` → 200 `{"version":"4.2","rules_count":133}`；`POST /api/v1/mcp` tools/list → 200，返回 **8 个工具**且工具名正确（`aishield_scan`/`aishield_guardrail`/`aishield_prompt_check`/`aishield_banned_words`/`aishield_rug_pull`/`aishield_handshake` + `agent_register`/`agent_quick_scan`），但描述仍写「133 rules」。旧探测查的是 `/api/health`、`/api/rules/stats`（这两个确实 404）→ 路径前缀记错导致误判 |
| **GitHub Pages（github.io）** | ⛔ **死端表面** | — | 无（勿再修） | — | `github.io/aishield/...` **301 跳到 aishield.tools**（CNAME），GH Pages 自身内容不可达。`pages.yml` 78 次运行全 success 但 `3-Verify` 用 `curl -sL` 实际在测 CF Pages → **假绿门禁**，内容 stale 也判绿。修 GH Pages 不影响线上域名 |
| **DeepSeek Harness (DSH)** | ❌ 缺位（生态首日，security 类目真空） | ① DSH Plugins 目录投稿（deepbolt.xyz）② 原生 `dsh-aishield` 插件（npm+cordis.patch.yml）③ MCP 桥接：DSH 原生支持 MCP → AIShield MCP server 零适配 | 目录投稿需账号 / 插件需 npm 发布 | **HIGH（新渠道·先发窗口）** | 首日 34k–65k★、1000+ 插件；supply-chain 风险是官方头号隐患→AIShield 本职；**无安全插件**→先发占 security 类目。dev preview+breaking changes→走 MCP 桥接最稳 |

---

## §2 品牌碰撞威胁（最被低估的风险）

### 2.1 aishield.ai 同名云 SaaS
- 独立公司产品，**同名 "AIShield"**，owner `aishield-ai`，已上 LobeHub + himcp.cn。
- 卖点：定价阶梯（Free/Pro ¥29/Enterprise ¥199）、API Key、注册送积分、「AI 语义分析」、30+ 正则。
- **威胁**：agent / 开发者搜 "AIShield" → 先见云 SaaS → 我们的「本地、开源、代码不出机」差异化被淹没。
- **我们的错位武器**：不是功能多少，是**部署模型**。Glama/llms.txt/README 的文案必须把「local / no-cloud / your code never leaves your machine」打到最前，把云 Trust API 降为「可选」。否则我们自己 Glama 页（写着注册/Key/定价）也在帮 aishield.ai 混淆认知。
- 🔴 **2026-08-17 升级**：aishield.ai 在 LobeHub 把其 MCP server 标为 **「Local Service / 仅在客户端本地设备运行」**，直接蹭我们的「本地优先」叙事（其实后端语义分析仍走 `aishield.ai/api/v1` 云调用）。其 LobeHub/himcp 安装指令写 `npx aishield-mcp` / `npx aishield-guardrail` / `pip install aishield`，但**实测 npm `aishield-mcp`、`aishield-guardrail` 均 404 不存在**、仅 PyPI `aishield` 存在 → 安装指令失效，且 `aishield-mcp` 短名**仍空闲**（防御性抢注机会，见 §1）。
- 🔴 **2026-08-17 新信号**：直接访问 `aishield.ai` 首页返回「Premium Domain For Sale」（Atom 域名出售页）。品牌或处于出售/动荡期；但其 marketplace 列表仍指向在线 API，产品应仍在运行。若域名确在出售，**回收 `aishield.ai` 品牌域名是低成本消除同名混淆的潜在杠杆**——需用户评估（AI 不代购）。

### 2.2 ClawHub `ai-shield-audit` squatting
- `clawhub/ai-shield-audit`（laurentaia）OpenClaw 安全审计，81/100、社区验证、144K 安装。
- 名字与 "AIShield" 高度混淆，且做的是**同一件事（审计 agent 配置）**——是直接的认知劫持。
- **动作**：尽快以 `aishield` 名义在 ClawHub 发布我们的 skill（见 §4），抢回命名空间。
- 🟡 **2026-08-17 跟踪**：该 squatting 条目已扩展至 ClawBox 硬件商店（€549 设备，4.7★，标榜「private, fast, no cloud」），认知劫持从软件蔓延到硬件。ClawHub 平台本身 2026-03 曾被曝**排名操纵漏洞**（攻击者可将恶意 skill 推到类目 #1，6 天 3900 次执行，已负责任披露并修复）——命名空间高风险但认领价值仍在；发布前须走 VirusTotal 扫描 + 老账号。

### 2.3 竞品功能升级威胁（内容安全平面被追平）
> 本周最大结构性风险：直接竞品把「本地/离线」做成标配，并补上我们缺失的**企业漏洞管理闭环**，我们的「本地扫描」单点差异化正在被抹平。

- 🔴 **mcp-audit (mcp-audit-scanner) 0.14.0** — 仍全离线（契合我们楔子），但已加 **89 条 Semgrep SAST 规则 + CVE 打标（CVE-2026-30615）+ Nucleus FlexConnect 企业漏洞管理对接 + Sigstore 签名校验 + fleet 部署 + governance policy-as-code + `watch` 实时监控**。这是**已补企业闭环的最强直接竞品**。空间内现同时存在 3 个同名/近名 mcp-audit（danush-aries / saagpatel / appsecsanta），用户易混淆，反而凸显「aishield」品牌需要更干净的认知锚点。
- 🔴 **Sunglasses (sunglasses-dev)** — 新晋强敌：MIT、**100% 本地、无云、无遥测**，1049 模式 / 7653 关键词 / 17 归一化 / 23 语言、0.261ms/输入，覆盖 prompt injection + MCP 工具投毒 + 跨 agent 注入 + 凭证外泄 + 「Proof Before Action」一次性容器。直接对冲「本地/不出机」楔子，且性能/覆盖数字更唬人。
- 🟠 **Snyk Agent Scan（原 MCP-Scan，2026-04 被 Snyk 收购）** v0.5.12 — 自动发现 10+ agent 的 skill + MCP 配置，凭 Snyk 企业渠道分发，是「主流化」威胁。
- 🟠 **owasp-agentic-mcp 1.0.9**（OWASP Agentic AI Top10，上 Smithery）、**mcp-security-auditor 1.0.0**（MIT、SIEM 对接 CEF/LEEF/Splunk）——补 OWASP Agentic / 企业 SIEM 覆盖，与我们 Agentic 11 模块正面重叠。
- **启示**：我们的护城河必须从「本地扫描」上移到 **内容安全平面 + 主动治理（kill switch / 持续鉴证 attestation）+ 机器可结算认证（x402/支付）** 这三件竞品没做或没做透的事上。详见周报 2026-08-17 行动建议。

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
1. ~~**Official MCP Registry 提 PR**~~ ❌ **作废（2026-08-22）**：已实测在册且 active（4.2.2 / isLatest）。**切勿再提 PR**，会造成重复条目。改为待决策项：在册条目的 `remotes`（`aishield.tools/api/v1/mcp`）实测活着但元数据陈旧 → 选 (a) 修后端元数据后保留 remote，或 (b) 下次发版移为 stdio-only（本地 `registry/server.json` 已是此形态）。需用户拍板。
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

### C. 本轮（2026-08-15 第二批）已补齐的可发布资产
- ✅ **Smithery 清单** `smithery.yaml`（仓库根）：`npx -y aishield-mcp-server` stdio 启动；登录 smithery.ai/new 连 repo 即发布。
- ✅ **GitHub Marketplace Action 源码** `distribution/github-marketplace/`（action.yml + 自包含 action_entrypoint.py + Dockerfile + README）：已抽离 root，明确「独立仓库 `lm203688/aishield-action`、不得含 workflow」约束；`action_entrypoint.py` 加惰性克隆兜底，独立仓库可自包含运行。
- ✅ **一站式投稿台账** `distribution/listings/SUBMIT.md`：6 个 web 表单渠道（Registry PR / LobeHub / MCP.so / PulseMCP / MCPfinder / A2A）+ 通用「本地优先」文案（区隔 aishield.ai）+ 发布状态速查表。用户登录即可复制粘贴。
- ✅ **分发缺口周期巡检自动化**：新增 weekly 自动化，实测 aishield.tools 发现文件 drift、刷新 SUBMIT.md 状态、提醒手动发布渠道。
- 📌 仍 100% 需用户手动的硬阻塞：Registry PR、LobeHub/Smithery/MCP.so/PulseMCP/MCPfinder 登录发布、ClawHub publish、DSH 目录投稿+npm、GitHub Marketplace 建独立仓库、aishield.tools CF Pages Retry（3 个 `cfut_` token 权限不足）。AI 已把这部分降到「复制粘贴 + 点一下」的最小摩擦。

---

## §5 本轮回测证据（可复现）
- `curl .../v0/servers/io.github.lm203688/aishield` → 404（API 提示正确路径但条目不存在）
- `curl .../v0.1/servers/io.github.lm203688/aishield` → 404
- `WebFetch glama.ai/mcp/servers/lm203688/aishield` → 确认是我们的（227/233 规则、内容安全平面）
- `WebSearch "aishield" site:mcp.so` → 无命中
- `WebSearch clawhub ai-shield-audit` → laurentaia 版 144K 安装、81/100
- `WebFetch lobehub.com/en/mcp/aishield-ai-aishield` → 云 SaaS（aishield.ai，定价/Key）

### §5.1 本轮回测证据（2026-08-17，可复现）
- ~~`curl registry.modelcontextprotocol.io/v0/servers/io.github.lm203688/aishield` → **404**（仍未上架）~~ ⛔ **无效证据**：该端点不存在（body = `Endpoint not found`），404 与上架状态无关。
- ~~`curl registry.modelcontextprotocol.io/v0.1/servers/io.github.lm203688/aishield` → **404**~~ ⛔ **同上，无效证据**。正确查法见 §5.2。
- `curl glama.ai/mcp/servers/lm203688/aishield` → **200**（Glama 仍 live，我们的条目）
- `curl registry.npmjs.org/aishield-mcp-server` → **200**，latest=**4.2.2**（2026-08-07 发布）
- `curl registry.npmjs.org/aishield-mcp` → **404**（aishield.ai 指令所引包不存在，短名空闲）
- `curl registry.npmjs.org/aishield-guardrail` → **404**（aishield.ai guardrail 包不存在）
- `curl pypi.org/pypi/aishield/json` → **200**（PyPI `aishield` 被 aishield.ai 占用）
- `WebFetch aishield.ai` → 「Premium Domain For Sale」页（品牌或动荡；marketplace 列表仍指在线 API）
- `WebFetch lobehub.com/zh-TW/mcp/aishield-ai-aishield` → 标「Local Service / 仅本地运行」，安装指令 `npx aishield-mcp`（包不存在）
- `WebSearch mcp-audit` → mcp-audit-scanner 0.14.0（89 SAST 规则 / Nucleus FlexConnect / Sigstore / fleet）；并现 3 个同名 fork
- `WebSearch agent security scanner` → Sunglasses（本地优先 1049 模式）、Snyk Agent Scan v0.5.12、owasp-agentic-mcp 1.0.9、mcp-security-auditor 1.0.0
- `WebSearch ClawHub ai-shield` → `ai-shield-audit`（laurentaia）仍在 + ClawBox 硬件；ClawHub 排名操纵漏洞（2026-03 披露已修）

### §5.2 本轮回测证据（2026-08-22 自动巡检，全部可复现）

> 前置：所有 curl 必带 `--ssl-no-revoke --tlsv1.3`（本机 TLS 拦截代理只放行 TLS1.3）。
> ⚠️ curl `-o` **不能写 `/tmp`**（Git Bash 映射，报 `client returned ERROR on write`，表现为 HTTP=200 但 size=0）→ 写工作区相对路径。

| 探测 | 结果 |
|---|---|
| `GET /v0/servers/io.github.lm203688/aishield` | 404 + body `{"detail":"Endpoint not found. See /docs..."}` → **端点不存在，非条目不存在** |
| `GET /v0/servers?search=aishield&limit=10` | **200**，2 条同名条目；`isLatest:true` 那条 = **4.2.2 / active / publishedAt 2026-08-07 / npm stdio** ✅ 已上架 |
| `GET aishield.tools/.well-known/mcp/server-card.json` | 200，**4.2.0 / 133 rules / `security_scan` 等错工具名** ⚠️ drift |
| `GET aishield.tools/.well-known/agent-card.json` | 200，**4.2.0 / 133 条** ⚠️ drift |
| `GET raw.githubusercontent.com/.../main/docs/.well-known/mcp/server-card.json` | 200，**4.2.2 / `aishield_*` 6 工具** ✅ main 正确 |
| `GET raw.../main/api/static/.well-known/mcp/server-card.json` | 200，**4.2.2 / `aishield_*`** ✅ main 正确 |
| `GET aishield.tools/api/health`、`/api/rules/stats` | 404（**路径前缀记错才导致「无后端」误判**） |
| `GET aishield.tools/api/v1/health` | **200** `{"status":"ok","version":"4.2","rules_count":133}` → 后端活着但 stale |
| `POST aishield.tools/api/v1/mcp` (`tools/list`) | **200**，返回 **8 工具**：`aishield_scan`/`aishield_guardrail`/`aishield_prompt_check`/`aishield_banned_words`/`aishield_rug_pull`/`aishield_handshake` + `agent_register`/`agent_quick_scan`（名对，描述仍写 133 rules） |
| `GET lm203688.github.io/aishield/.well-known/mcp/server-card.json` | **301** → 跟随后 `url_effective = aishield.tools/...` → **GH Pages 内容不可达（死端）** |
| `GET api.github.com/.../workflows/pages.yml/runs` | total **78**，最近 5 次全 `success`（→ 假绿门禁：verify 用 `-sL` 实际在测 CF Pages） |
| `GET registry.npmjs.org/aishield-mcp-server` | 200，`dist-tags.latest = 4.2.2`，modified 2026-08-07 ✅ |
| `GET glama.ai/mcp/servers/lm203688/aishield` | **200** ✅ 仍 live |
| 本地 `scanner.rules.get_rule_count()` | **227** ✅ 基线确认 |
