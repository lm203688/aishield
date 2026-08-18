# AIShield 作为「智能体通路」的信任与内容安全层

> 日期：2026-08-18 | 触发：用户要求"分析 agent 之间的连接，让项目直接成为 agent 通路的环节"
> 定位结论：AIShield 不做 agent 的"大脑"也不做"算力"，而是嵌入 **agent 连接拓扑每一跳的信任/内容安全校验点** —— 成为 Internet of Agents 的"中立信任层 + 内容安全平面"。

---

## 1. 2026 的 agent 连接拓扑（Internet of Agents）

```
   [Tool / Data]  <—— MCP（纵向：agent↔工具） ——>  [Agent A]
                                                       │
                                       A2A（横向：agent↔agent）
                                                       │
   [Agent B] <—— A2A ——> [Agent C] ……（Agentic Mesh / dMCP：P2P 直接握手）
                                                       │
                          [AGNTCY Directory / OASF AI Card]  —— 发现 + 身份（Webex ACS 已落地）
                                                       │
                          [Agentic Gateway / Control Plane]  —— 枢纽：authz / rate-limit / observability
```

事实依据（2026-08-18 扫描）：
- **A2A**（Google，现 Linux Foundation）：Agent Card 在 `/.well-known/agent-card.json`，JSON-RPC 2.0，意图协商，Agent Trust Score 概念。
- **AGNTCY**（Cisco + LangChain + LlamaIndex + Galileo + Glean，Linux Foundation "Internet of Agents"）：三支柱 = 消息 schema + 发现（Agent Directory / OASF AI Cards）+ 身份（Agent Identity Service，徽章分 Cisco Official / Onboarded / Federated）。Webex 已集成进 Agent Central Service（ACS）。SLIM = 安全 agent-to-agent 消息协议。ARD = Agentic Resource Discovery 规范（联邦发现）。
- **Agentic Mesh / dMCP**：P2P agent 网络取代中心编排器；动态能力发现；"Agent Spoofing / 不可验证对等体" 成为头号威胁；安全靠 ephemeral 加密身份 + zero-trust。
- **Agentic Gateway / Control Plane**：坐在 MCP + A2A 前面的控制面，强制 authz / rate-limit / observability —— **安全治理实际落点**。

## 2. 每个连接点的「信任缺口」（AIShield 的插入依据）

| 连接点 | 现有方案做了什么 | 信任/内容缺口 | AIShield 插入 |
|--------|----------------|--------------|--------------|
| **发现（Discovery）** | AGNTCY/OASF AI Card 有签名；徽章是**厂商发**（Cisco Official/Onboarded/Federated） | 没人验证 card 背后 *agent/skill 实际做什么*（prompt injection / tool poisoning） | 中立第三方 **内容信任徽章**，叠加在厂商徽章之上 |
| **连接（Gateway）** | Agentic Gateway 管 authz / 限流 / 可观测 | **不验证工具调用/消息的内容信任**；SentinelMCP/cMCP 在此做网络代理 | Gateway 内的**内容平面模块**（本地、离线） |
| **A2A 消息** | 只签 AgentCard，不签消息*内容* | 消息可携带 prompt injection / goal hijack 跨 agent 传播（ASI01/ASI08） | 扫描 A2A 消息载荷（复用 `goal_hijack_scan` / `slop_scan`） |
| **Mesh 反欺诈** | 靠 ephemeral 加密身份 | 需要**可验证 + 可审计**的 agent 身份 | `attestation` 可验证身份 + 不可篡改哈希链日志（CoSAI 要求） |

核心判断：**缺口是"内容信任 + 中立可验证身份"，不是"连接能力"**。AGNTCY/Cisco 提供发现与厂商身份，但把"内容是否该被信任"留给各 agent 自己。这正是 AIShield 的卡位。

## 3. AIShield 成为通路环节的 4 个插入点

```
   [Tool] ──MCP──> [AIShield 内容平面] ──> [Agent A]
                                          │ A2A
                                    [AIShield 消息注入扫描]
                                          │
   [Agent B] ──A2A──> [AIShield 消息注入扫描] ──> [Agent C]
                          │
            [AGNTCY/OASF AI Card] ← AIShield 中立内容信任徽章
                          │
            [Agentic Gateway] ← AIShield 内容平面模块（本地/离线）
```

1. **Discovery（卡验证）**：在 agent/skill 被登记进 AGNTCY Directory / MCP Registry 前，AIShield 扫其内容层，签发中立 `aishield-trust/v1` 徽章。厂商徽章说"谁发的"，AIShield 徽章说"内容是否安全"。
2. **Connection（Gateway 内容平面）**：`guardrail_harness` 已是 stdio JSON-RPC 准入闸门，可包装为 Agentic Gateway 的一个本地内容平面模块（不抢网关的 authz/限流活，只做内容信任）。
3. **Messaging（A2A 注入扫描）**：agent 间每跳消息过 `goal_hijack_scan` / `slop_scan`，阻断跨 agent 的 prompt injection / goal hijack 传播。
4. **Identity（可验证身份）**：`attestation` 发**可验证收据**（见 §5 借鉴 cMCP），给 mesh 提供 CoSAI 要求的"verifiable claims + immutable log"。

→ 一句话定位：**"Every agent-to-agent and agent-to-tool hop can be gated by AIShield."** AIShield 是 agent 通路的"信任中间人"，而非另一个 agent 或另一个网关。

## 4. 从新开源项目借鉴（adopt / defend）

2026-08-18 扫描发现 4 个高参考价值的新开源项目（均 2026 新发）：

### 4.1 SentinelMCP（technosiveuk-ui，Apache 2.0，v0.2.0 Alpha，Go）—— MCP 防火墙网关
- **可做（adopt）**：① **fail-closed 传输硬化**（拒绝明文/IP-literal upstream、upstream cert pinning、egress allowlist）；② **HITL 中断/恢复**（durable checkpoint + webhook 审批）；③ **OTel 审计导出**（SIEM 管线）。我们的 `guardrail_harness` 做 per-call 准入，但缺 fail-closed 传输 + HITL resume。
- **差异（defend）**：它是**网络代理 + DLP**（需坐在流量里），我们是**本地内容信任 + 信任分**（无需拦截流量）。定位 = "Gateway 里的内容平面"，互补非竞争。

### 4.2 cMCP / Confidential MCP Runtime（agentrust-io，dev preview 2026-06）—— TEE 硬件 attested 审计
- **可做（adopt）**：**签名 TRACE Claim / 可验证审计收据**。我们的 `attestation.py` 已有哈希链审计，可输出**第三方可验证的签名收据**（`aishield-trust/v1` 已定义 schema），加一个 verification endpoint。这正好对接 AGNTCY 的 "verifiable claims"。
- **差异（defend）**：cMCP 依赖 TEE 硬件；我们 software-only → 兼容性强、零硬件要求。可发"签名收据"而不绑定硬件。

### 4.3 CheckMCP（h129hj，MIT，2026-07）—— 扫描器 + 自托管网关 + canary 外泄检测
- **可做（adopt）**：**canary / 诱饵 token 外泄检测** —— 注入诱饵密钥并监控其是否被带出（callback-canary）。我们是*静态*外泄检测（规则层），缺**运行时 canary 确认**这一环（与 `spend_cap` / `runtime_governance` 互补）。
- **差异（defend）**：CheckMCP 有托管 SaaS（checkmcp.dev）；我们坚持本地/离线 → 差异化。
- 其 "live badges + continuous drift monitoring + governance policy API" = 我们 Continuous Attestation + badge + Trust API 的同构 → **强化而非借用**。

### 4.4 MCP Core Defense（amurlaniakea，AGPL-3.0）—— 7 阶段安全代理
- **可做（adopt，高价值）**：**DCI Checker（描述-代码一致性）** —— 验证 MCP tool 的*自然语言描述*是否与*代码实际行为*一致（Python/JS/TS AST）。我们扫描述里的投毒，但**不验证"描述↔代码"一致性**。这是结构性缺口，离线 AST 可实现，防守壁垒高。
- **差异（defend）**：AGPL + Python；我们 MIT + 零依赖。保持离线。

> **adopt 优先级**：① DCI 描述-代码一致性（MCP Core Defense，最独特、最贴合"内容信任"） → ② 可验证签名收据（cMCP，对接 AGNTCY verifiable claims） → ③ canary 外泄检测（CheckMCP，运行时闭环） → ④ fail-closed 传输 + HITL（SentinelMCP，网关集成时再上）。

## 5. 与 AGNTCY / A2A 的互补而非竞争定位

话术（可写入 llms.txt / agent-card.json / 博客）：
> "AGNTCY 让 agent 找到彼此并验明厂商身份；A2A 让它们谈判任务；Agentic Gateway 管权限与限流。但**没人告诉一个 agent：它刚连上的那个 agent/skill 的内容，到底该不该信**。AIShield 是 agent 通路的**中立信任层 + 内容安全平面** —— 在发现时验证内容、在连接时做内容准入、在消息里扫注入、在 mesh 中提供可验证身份。本地、离线、不绑厂商。"

关键：我们**不**做发现协议（AGNTCY 的活）、**不**做网关路由（网关的活）、**不**做 TEE（cMCP 的活）。我们只在每一跳做"内容是否该被信任"这一件事，且中立、本地、离线。

## 6. GitHub 反馈参考（lm203688/aishield）

仓库当前 30 个 open issue **全部为 bot 自动创建，无人类反馈** —— 这本身是一个信号：社区互动/可发现性仍低（印证"缺口是可见性"）。但有两条高价值自动反馈：

- **#418 🟠 [P1] 内容站发布失败（读者侧入口不可达）**：`build=success deploy=failure verify=skipped`。Issue 自带修复指引："若 deploy 报 'Pages site not found' 或 404，说明仓库尚未启用 Actions 部署：Settings → Pages → Build and deployment → Source 选 'GitHub Actions'。" 结合 2026-08-17 发现（3 个 `cfut_` token 均无法访问 aishield.tools 所属账户），**根因是 aishield.tools 的 CF Pages 部署链路失效 / token 无权**。→ **用户动作 #1**：在 CF dashboard 用有权 token Retry，或在 GitHub repo Settings → Pages 确认 Actions 部署已启用。**这是 GEO/agent 露出的最大硬阻塞**。
- **#429 AIShield 扫描发现严重安全问题**：自扫在 run 32079403107 发现 **4× SSRF（内网/元数据地址访问）**。说明：① 我们的扫描闭环对自身依赖有效；② 需人工复核这 4 个 SSRF 是真漏洞还是误报（若是真，先修自家依赖；若是误报，补规则降噪）。→ 可作为"扫描器自证"案例写进对外材料。

## 7. 落地 backlog（建议）

| 优先级 | 项 | 复用 | 新增 | 验证标准 |
|--------|----|------|------|---------|
| P0 | DCI 描述-代码一致性扫描器 | `scanner/engine.py` 评分框架 | `scanner/dci_scan.py`（tree-sitter AST，离线） | 良性 0 误报 / 恶意（描述谎称只读实则写文件）全检出 |
| P1 | 可验证签名收据 | `eco/attestation.py` 哈希链 | 加 Ed25519 签名 + `/api/v1/attestation/verify` | 第三方持公钥可验收据未被篡改 |
| P1 | Agentic Gateway 内容平面适配器 | `eco/guardrail_harness.py` | 包装为网关可挂载模块（文档 + 示例） | forge/Goose/网关可注册并拦截 |
| P2 | canary 外泄检测 | `eco/runtime_governance.py` | 诱饵 token 注入 + 出口监控 | 诱饵离开即告警 |
| P2 | 修复 #418 内容站部署 | — | 用户动作：CF token / GitHub Pages 设置 | aishield.tools 各 clean URL 返回 200 |

> 完整威胁数据、竞品矩阵更新见 `references/competitive-landscape.md`；生态演进总纲见 `docs/agent-ecology-evolution-directions.md`（方向三）。
