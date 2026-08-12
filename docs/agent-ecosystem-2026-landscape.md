# Agent 生态 2026 态势扫描与 AIShield 卡位布局

> 生成日期：2026-08-12 ｜ 基于 GitHub 用户反馈挖掘 + 开源市场新技术扫描
> 目的：把"agent 生态几个层次"框架对齐到 2026-08 的真实技术前沿，找出我们没跟上的节点，给出可执行的卡位与能力扩展。

---

## 0. 一句话结论

AIShield 最强的护城河仍是**安全层（214/220 规则）**，但我们之前漏看了 2026 年最热的两条线：
1. **Agent 身份层（Identity / NHI）**——A2A 仓库 top 5 issue 全是身份（💬655 / 235 / 143 / 103 / 94），Authentik 借 NHI 重新爆火，ANS/DNSid/Entra Agent ID 扎堆。这是 2026 年 agent 安全的"主战场"，我们**有 attestation 后端、却没有"扫描身份"的能力**。
2. **Agent 网络层（Mesh / 组网）**——Cloudflare Mesh 已把"agent 组网"做成基础设施，但官方自认**缺 per-agent 身份与策略**（"all agent traffic looks like from a Worker"）。这正好是 AIShield 内容可信 + 身份归因的补位点。

**窗口期约 2–3 个月**：A2A 的 trust.signals[] 规范正在起草（#1628，💬103），SDAP/AIP/Cedar 等信任补位流派刚冒头。我们必须把"信任层 = 扫内容 + 扫身份 + 扫组网"这个定义抢下来。

---

## 1. GitHub 用户反馈提炼的真实需求

### 1.1 自家仓库（lm203688/aishield）
- 50 个 open issue 全部是**自动化告警**（扫描发现安全问题 / 获客指标告警），没有真实用户功能请求——说明：**我们缺一条"用户提需求"的入口**，且对外声量还太小。
- 已关闭的历史 issue 暴露真实痛点：`#17 内容分发未落地`（💬40）、`#19/#18 MCP registry 上架失败`、`#42/#2 npm 发布失败`、`#69/#15 部署后验证失败`。
- **启示**：我们自己的"已发布但未留底/未上架"老问题已修（见 `distribution/published.json` + `verify_distribution.py`），但**对外分发渠道仍是短板**。

### 1.2 跨仓库高信号需求（按热度）
| 来源 | Issue | 热度 | 映射 AIShield 能力 |
|---|---|---|---|
| google/A2A | #1672 Agent Identity Verification for Agent Cards | 💬655 | **身份扫描**（我们的缺口） |
| google/A2A | #1786 Cryptographic Agent Identity extension | 💬235 | 身份签名校验 |
| google/A2A | #1829 Ed25519 + RFC 9421 signing | 💬143 | 身份签名校验 |
| google/A2A | #1628 trust.signals[] extension | 💬103 | **我们可成为 signal provider** |
| google/A2A | #1717 Governance metadata in Agent Cards | 💬94 | 治理/信任元数据 |
| anthropics/claude-code | #4476 Agent-Scoped MCP Config + Strict Isolation | 👍183 | 隔离（对手在做，我们互补） |
| anthropics/claude-code | #18653 Tool result transform hook for content sanitization | 👍17/💬24 | **内容可信平面**（我们的主场） |
| microsoft/vscode | #252496 Auto-approve terminal command in Agent Mode | 👍255 | 命令执行风险 |
| zed-industries/zed | #49057 Support for Agent Skills | 👍194 | skills 生态扩张 |
| 供应链（axios/litellm/greatsuspender） | 恶意维护者 / 依赖投毒 | 👍2268/1116/905 | **供应链审计**（我们已有 SBOM/OSV） |
| modelcontextprotocol/servers | #40/#64 MCP 在 Windows/npx/NVM 连不上 | 💬112/90 | 安装摩擦（影响我们 npm 包） |

**核心需求信号**：① agent 身份可验证（最大声量）；② 内容/工具结果净化（我们的内容可信平面）；③ 隔离与最小权限；④ 供应链可审计；⑤ 安装零摩擦。

---

## 2. 新技术扫描（用户点名 + 衍生）

### 2.1 Cloudflare Mesh（用户点名）
- 2026-04-14 Agents Week 发布：把 human/devices/cloud VPC/agents 组进一个加密私有组网，Workers VPC binding 让 agent 免暴露访问内网，免费 50 节点。
- 配套 **Enterprise MCP Reference Architecture**：Mesh 管"可达性"，MCP auth 管"工具执行权限"，明确分工。
- **官方自认的缺口**：*"Per-agent identity and policy evaluation are listed as future development items"*——Mesh 把所有 agent 流量当成"来自一个 Worker"，**无法区分是哪个 agent 调的、按 agent 写策略**。
- **AIShield 卡位**：我们是 Mesh 的**内容可信 + 身份归因补位层**——Mesh 管"能不能连"，AIShield 管"这个 agent 该不该信、它干了什么"。

### 2.2 Authentik（用户点名）
- goauthentik/authentik（22k★，开源 IdP，OAuth/OIDC/SAML/LDAP/RADIUS/SCIM）。2026 因 **NHI（Non-Human Identity）** 重新爆火。
- 官方发文《A note to AI agents about authentik》：把 agent 当 service account，发**短期过期令牌 + RBAC**，令牌到期自动轮换。
- **AIShield 卡位**：扫描 agent 服务账号配置——长期不轮转令牌、scope 过宽、缺过期时间、缺 mTLS——这是"身份层"的具体检测项。

### 2.3 soundshuman（用户点名，代表 agent 文化层）
- aashaexo/soundshuman（176★）：去 AI 写作痕迹，41 类模式，已上 claudepluginhub 成 skill。
- 它代表一个**文化信号**：agent 产出要"像人写的"，去 AI 味工具开始集成进 agent 工作流。
- **AIShield 卡位（差异化）**：soundshuman 是"风格层"（让 agent 不说 agent 话），我们是"安全/可信层"（这个 agent 内容有没有毒、有没有在规避检测）。二者互补——**我们可新增"内容溯源 / AI-slop 规避检测"子能力**，识别专门设计来绕过检测器的恶意 prompt/skill（详见 §4 路线图）。

### 2.4 A2A / AP2 / x402（agent 协议与支付）
- A2A：22k★，150+ 组织生产使用，Linux 基金会。AP2（Agent Payments Protocol）+ A2A x402 稳定币微支付（Coinbase×Google）。
- **A2A 的"信任浅滩"**：Signed AgentCard 验得了"身份"，验不了"意图/委托授权"；已有 **session smuggling** 红队案例。
- 信任补位流派：SDAP（DID + mTLS + scope attenuation + Merkle 审计链）、AIP（IBCTs 调用绑定令牌 + 权限只收不放）、AWS Cedar + A2A。
- **AIShield 卡位**：内容可信 + 身份归因 + 委托权限衰减检测，直接对应"信任浅滩"。

### 2.5 ANS / DNSid / AID（agent 身份寻址）
- Linux 基金会 ANS（Agent Name Service）：把 agent 身份绑 DNS，ACME 证明域名控制后发证书，状态写只追加日志。
- Identity Digital 的 DNSid、社区极简 AID 草案、微软 Entra Agent ID、Okta for AI Agents 均已上线。
- **AIShield 卡位**：扫描 agent 身份是否走 DNS/DID 可验证、证书是否过期/自签、是否缺撤销机制。

---

## 3. 映射到 AIShield 4 层框架的能力缺口

| 层 | 现状 | 新技术暴露的缺口 | 本次扩展 |
|---|---|---|---|
| 安全层 | ✅ 214/220 规则 | 供应链/命令执行/内容净化 | 已强；补"工具结果净化"建议项 |
| **身份层（新）** | 🟡 只"发"不"扫" | A2A 身份💬655、Authentik NHI、ANS/DNSid | **新增 `identity_scan`：扫 AgentCard 签名/过期/scope/mTLS** |
| **网络层（新）** | 🔴 无 | Cloudflare Mesh 缺 per-agent 身份、过宽可达性 | **新增 `network_scan`：扫组网/Mesh 配置过宽暴露** |
| 信任层 | 🟡 后端已建未亮 | trust.signals[] 规范起草中 | 已落地 `/api/v1/trust` + 提案（见 `trust-field-proposal.md`） |
| 内容可信 | 🟡 有 poisoning/taint | soundshuman 文化层、AI-slop 规避 | 路线图：内容溯源/规避检测子能力 |
| 经济层 | 🔴 弱 | AP2/x402 支付授权过宽 | 路线图：支付授权 scope 审计 |
| 协议层 | 🟡 部分 | A2A card / ai-catalog | 已 dogfood `trust` 字段；待提提案 |

---

## 4. 生态位卡位布局（按优先级，附链接）

### P0 — 立即卡位（规范起草期，低成本高杠杆）
1. **A2A trust.signals[] signal provider**（`google/A2A` #1628，💬103，正在设计）
   - 提案：把 AIShield 的 attestation 结果作为 `trust.signal` 之一。我们已定义 `aishield-trust/v1`，直接对齐。
   - 材料：`docs/trust-field-proposal.md` 已备。
2. **认领 Glama 未认领 listing**（`lm203688/aishield` 被索引但 Unclaimed）
   - 登录 glama.ai → claim → 填信任/安全定位。
3. **Cloudflare Mesh 社区补位叙事**
   - 在 Mesh 公告/社区发"AIShield 作为 Mesh 的内容可信 + per-agent 身份补位层"。

### P1 — 本月卡位（渠道/标准）
4. **awesome-mcp-servers / Cursor / MCP Registry 上架复核**（文案见 `docs/listing-copy.md`）。
5. **向 ANS / ai-catalog 工作组提 `trust` 字段**（复用同一提案）。
6. **Authentik 集成**：把 `identity_scan` 做成可扫 Authentik service-account 导出的模块，发到 Authentik 社区。

### P2 — 内容/文化层（差异化叙事）
7. **soundshuman / de-AI 社区桥接**：明确分工——他们是风格层，我们是安全/可信层；可做一篇"agent 内容安全 vs 去 AI 味"的定位文，避免被误认为竞品。
8. **内容溯源 / AI-slop 规避检测**（路线图模块）：识别专门绕过检测器的恶意 prompt/skill。

---

## 5. 能力边界扩展路线图

### 本次落地（已实做）
- **`scanner/identity_scan.py`** — Agent 身份与凭证扫描：未签名 AgentCard、过期/无过期 service account、scope 过宽（`"*"`）、缺 mTLS/DID、缺 scope attenuation。
- **`scanner/network_scan.py`** — Agent 网络/Mesh 配置扫描：整账户 Mesh 绑定（`remote: true` 无 per-agent 策略）、`0.0.0.0` 暴露、agent 端点 `auth: none`、私有资源公网暴露。

### 下一步（路线图，待排期）
- **内容溯源 / AI-slop 规避检测**：识别"为绕过检测器而设计的 prompt/skill"。
- **支付授权 scope 审计**：扫描 AP2/x402 支付授权是否过宽（意图/购物车/支付三授权是否收敛）。
- **Authentik 导出扫描器**：直接吃 Authentik service-account 导出 JSON。
- **A2A AgentCard 校验器**：吃 `.well-known/agent.json`，校验签名/过期/委托链。

---

## 6. 待用户拍板的外部动作（公开动作，需你确认）
1. 在 A2A 仓库 #1628 提 `trust.signal` 提案（文案已备）。
2. 认领 Glama listing。
3. 复核 awesome-mcp-servers / Cursor / MCP Registry 上架。
4. 在 Cloudflare Mesh / Authentik / soundshuman 社区发补位/桥接叙事。
