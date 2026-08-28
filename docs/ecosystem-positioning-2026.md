# AIShield 生态位占位策划（2026-08-10）

> 依据《生态体系总纲》第四部分（4 层 + 数据层）框架，结合 2026-08-10 开源市场调研，盘点已介入层次、未布局关键节点，给出"尽快占据生态位"的差异化策略。
> 配套工件：`docs/trust-attestation-spec.md`（可被发现层引用的中立信任凭证 schema）。

## 一、框架回顾：agent 生态的几个层次

来自《生态体系总纲》4.1，也是本项目的最高结构依据：

| 层 | 总纲定义的核心交付物 |
|----|----------------------|
| **安全层** Security | MCP 扫描 / Prompt 防火墙 / OWASP 对齐 / Rug Pull / 供应链审计 |
| **信任层** Trust | 安全评分体系 / 认证徽章 / 信誉系统 / 持续监控 / Agent 身份 |
| **经济层** Economy | 支付网关 / 按次·订阅计费 / 平台抽成 / 结算 / 发票 |
| **协议层** Protocol | MCP Server / A2A Gateway / OAuth 2.0 / API Gateway |
| **数据层** Data | 安全数据库 / 审计日志 / 用户数据 / 市场交易数据 |

+ 2026-08-10 新定卡位：**Agent 计算机「内容安全平面」**（跨安全层，叠加在隔离层之上）。

## 二、我们已介入的层次（对齐当前仓库真实能力）

| 层 | 状态 | 证据 |
|----|------|------|
| **安全层** | ✅ 核心已建（最强） | 227 MCP / 233 Skill 规则；双维 OWASP MCP Top10 + Agentic ASI01-10；`workspace_scan` 启动前预扫；`SANDBOX_RULES` 沙箱硬化；taint / SBOM / OSV；CI gate（SARIF）+ `.md` 指令载荷盲点修复 |
| **协议层** | 🟡 部分已建 | `aishield-mcp-server` npm **4.3.0 已发布**；A2A `agent-card.json`；`api/server.py` 全离线；`llms.txt`；但 **GitHub Action 未上 Marketplace**、A2A Task 路由未做 |
| **信任层** | 🟡 后端已建，未"占位" | `eco/attestation.py`（订阅/鉴证/哈希链）、`/api/v1/trust/*`、`/api/v1/attestation/*`、`/badge/{tool}`、`eco/badge`、x402 + 虎皮椒支付脚手架**都已就绪**——但没作为"公开、可嵌入的中立信任机构"推出 |
| **经济层** | 🔴 弱（Phase 3） | 支付脚手架在（`eco/payment`、`eco/x402`、`eco/hupijiao`），但工具市场 / 调用网关 / escrow / 抽成未建 |
| **数据层** | 🟡 部分 | 安全库 / 审计日志 / telemetry 在；fleet/policy 引擎仅部分（mcpaudit 已有，我们弱） |

**结论**：安全层是我们的护城河；信任层技术基本就位却没"亮出来"——这是当前最大机会点。

## 三、还没布局的关键节点（gaps / 未占生态位）

1. **中立信任机构（公开、机器可读、可被发现层引用）**——总纲里最大的空白，现在 HVTracker / Orac / AIR 已经进场。**最高优先级。**
2. **GitHub Action → Marketplace（CI 节点）**——`action.yml` 已定义但未发布；AgentAuditKit 已占通用位，我们需差异化。
3. **跨注册中心发现层**——标准混战（MCP Registry / Server Card / ai-catalog / AGNTCY / ACP / ANP），**不应自建竞争注册表**，而应把"信任层"插进这些发现格式。
4. **运行时 guardrail 作为通用 harness 对外发布**——`eco/guardrail_harness.py` 已建，但没做成 forge / Goose / Open Interpreter 可装的 drop-in 拦截工具。
5. **Agent 计算机内容安全平面 GEO 放大 + 社区触达**——能力已建，缺对外叙事与社区渗透。

## 四、开源市场参考（2026-08-10 调研）

**发现层（标准战，不建议硬刚）**
- MCP Registry 预览（9652 条）、Server Card（SEP-1649，`.well-known` 暴露结构化 metadata）
- Google「Unified AI Card + AI Catalog」（`/.well-known/ai-catalog.json` 单一入口）
- AGNTCY Agent Directory Service（ADS，分布式目录）、ACP（Linux Foundation/BeeAI）、ANP（DID+JSON-LD）、W3C WoT、Eclipse LMOS
- **共识**：discovery ≠ trust。"A trust layer answers 'who stands behind this endpoint?'" ——信任层是单独一层，目前最薄弱

**信任层（白空间正被抢，必须快）**
- **HVTracker**（hvtracker.net）：522 个开源 agent 的信任分，基于 OSSF Scorecard / 溯源 / 签名提交 —— **但不扫内容（prompt 注入 / 工具中毒）**
- **Orac Agent Trust**（github.com/Orac-G/agent-trust）：信任分 + **x402 微支付** + prompt 注入筛查，Cloudflare Workers 上线，AEI 1100+ agent
- **AIR**（agentidentityregistry.org）：W3C DID + 五维信任分（溯源/行为/透明/安全/同行背书）0-1000
- **Crucible**：链上（Mantle ERC-8004）验证+信誉
- **Metinc**：240+ 评估，4 维（最接近的商业模式竞品，但不做扫描引擎）

**CI 节点（已被占，需差异化）**
- **AgentAuditKit**：271 规则 / 12 框架 / **GitHub Marketplace Action 已上线** / SARIF / CVE→规则账本 / 1100+ 测试 / 离线确定性 —— 我们未占节点的最强竞品

**Agent 计算机（互补非竞品）**
- forge / forgevm / Open Interpreter / Goose / 腾讯云 Cube / Cloudflare `@cloudflare/computer`——只做 OS 级隔离，不做 MCP/skill/prompt 内容安全

## 五、占位策略（差异化 + 快）

**核心 thesis**：AIShield = agent 生态的「**信任层 / 内容安全平面**」。不做发现层注册表、不做运行时不隔离、不做通用经济市场。

具体占位动作（按杠杆排序）：

1. **【白空间·最高杠杆】把已有 trust_api/attestation/badge 包装成"公开可嵌入的中立信任机构"**
   - 定义 **AIShield Trust Attestation** schema（见 `trust-attestation-spec.md`），让 MCP Server Card / Agent Card / ai-catalog 用 `trust` 字段引用我们。
   - **差异化锚点**：唯一"**扫内容**"（prompt 注入 / 工具中毒 / 供应链漂移）+ 离线 + 中立 + 免费。抢在 HVTracker/Orac 把"信任层"定义成"只扫供应链信号"之前定型。
2. **【CI 节点】发布 GitHub Action 到 Marketplace**
   - 差异化：默认 **no-spawn（不执行被扫配置）** + 内容/prompt 注入 + **中文合规（违禁词）**。AgentAuditKit 占通用位，我们占"中国合规 + 不执行"位。
3. **【Agent 计算机平面】GEO 放大 + 社区触达**
   - 扩"Cloudflare Sandbox + AIShield"联合叙事；把 `guardrail_harness` 做成 forge/Goose/Open Interpreter 的 drop-in 拦截工具；触达这些社区。
4. **【经济层·暂缓】x402 + 虎皮椒已就绪**，等信任层有流量后接"按结果付费"结算（参考 Orac 的 x402 信任分模式），不抢先烧资源。

## 六、执行清单（优先级）

**P0（本周，in-repo，我可直接动手）**
- [ ] 写 AIShield Trust Attestation schema + 在 `agent-card.json` / `llms.txt` 引用（让发现层能嵌我们）
- [ ] 校验 `action.yml` + `Dockerfile`，准备 Marketplace 上架材料（README 片段、差异点说明）
- [ ] GEO：把"内容安全平面 / 中立信任机构"扩写到 README / llms / agent-card
- [ ] 把 `guardrail_harness` 包装成 forge/Goose 可用的 drop-in 配置示例

**P1（需你确认后外部发布）**
- [ ] 发布 GitHub Action 到 Marketplace
- [ ] 复核 MCP Registry / awesome-mcp-servers(PR #2) / Cursor / Glama 上架状态
- [ ] 向 Agent Card / ai-catalog / MCP Server Card 工作组提交"trust 字段"提案
- [ ] 触达 forge / Goose / Open Interpreter / Cloudflare 社区

**P2（Phase 3）**：经济层工具市场 / 抽成 / escrow

## 七、风险与判断（诚实）

- **不做**发现层注册表（打不过标准战 + 已被 AGNTCY 等占）；**不做**运行时不隔离（打不过 forgevm/Cube）。
- 信任层是**窗口期**：HVTracker/Orac 已进场，3 个月内不定型就被动——这是当前唯一要抢的时间窗。
- 测试量级劣势（AgentAuditKit 1100+ vs 我们 428）不改主打"测试数"，改主打"**扫内容 + 中立信任 + 离线不执行**"。
- 经济层在信任层有流量前不重投入（避免重蹈总纲 1.1「零收入零用户」陷阱）。
