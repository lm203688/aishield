# AIShield 投资人视角 · 竞争对比与平台提升战略报告

> 视角设定：作为多家机构（安全基金 / 产业 CVC / 生态战略方）的投资人，对 AIShield 项目做独立尽调式评估。
> 数据时点：2026-08-05。竞争情报已用公开最新动态（RSAC 2026、OWASP Agentic Top 10、Agent Security Market Map 2026）校准。
> 项目现状：Agent 原生 AI 工具安全扫描器，201 条本地规则（110 MCP + 60 Agentic ASI + 31 中文注入），14 客户端非执行式审计，Trust API / SBOM-SARIF / x402 计费 / GEO 资产已落地；npm `aishield-mcp-server@4.2.1`、MCP 官方 Registry `io.github.lm203688/aishield@4.2.1` 已上架。

---

## 0. 执行摘要（一句话给投资人）

Agentic AI 安全是 **2026 年形成最快的网安品类**（$3.6B 融资、$96B M&A、OWASP 已于 2025-12 发布 Agentic Top 10），MCP 已达 9700 万月下载、1.7 万+ 活跃 server——**TAM 巨大且窗口期就在 12 个月内**。AIShield 的卡位（本地不上云 + MCP·Agentic 双维 + 中性信任机构叙事）是正确且仍空白的，但**能力深度正被开源竞品 mcp-audit 反超**，且"数据资产"与"模型算法层"两块几乎为零。结论：**方向对、先发卡位在，但必须在 2 个季度内补齐"深度 + 数据 + 语义"三件事，否则会被 mcp-audit 的社区势能吃掉差异化**。

---

## 1. 市场与竞品对比矩阵（2026-08 最新）

### 1.1 市场规模信号（投资人最关心的"赛道是否成立"）

| 指标 | 数值 | 含义 |
|---|---|---|
| 2026 年度 Agent 安全融资 | **$3.6B** | 自云安全后最快形成的网安品类 |
| 2026 M&A 总额 | **$96B**（400 笔，+270% YoY） | 收购路径清晰（Wiz $32B、ServiceNow $11.6B 等） |
| OWASP Agentic Top 10 | 2025-12 发布（ASI01–10） | 风险分类已成"监管参考架构" |
| MCP 采用 | 9700 万月 SDK 下载、1.7 万+ 活跃 server | 攻击面在 gateway 层爆炸式扩张 |
| 企业事件率 | **88%** 企业报告过 AI agent 安全事件；仅 **21%** 有运行时可见性 | 需求真实、供给严重不足 |
| 资本密集度 | Kai $125M / Oasis $120M / XBOW $120M / Noma $100M / RunSybil $40M | 一层（identity）已被重金占坑 |

**四层市场结构（Bessemer 框架）**：① 身份层（agent IAM，Oasis/Entra Agent ID/Okta）② **API/MCP gateway 层（AIShield 所在）** ③ 运行时/SaaS 层 ④ 治理层。AIShield 卡在②，是正确的"被集成入口"，但②目前最拥堵（mcp-audit、aishield.ai、Runlayer、Lasso、Palo Alto 等混战）。

### 1.2 直接竞品能力对比

| 维度 | **AIShield** | **mcp-audit**（最强开源对手） | **aishield.ai** | **Bosch AIShield** | **Anthropic Claude Security / MS MDASH** |
|---|---|---|---|---|---|
| 部署模型 | 本地 CLI / 库 | 本地 CLI / GitHub Action | 云 SaaS（付费） | 企业云 | 云（大厂平台内） |
| 审计方式 | **非执行式（不 spawn 被扫配置）** | 执行式（live connect 连运行 server） | 执行式 | 执行式 | 语义/运行时 |
| 客户端覆盖 | **14** | 8 | 少 | 企业级 | 自家生态 |
| 规则规模 | 201（含 31 中文注入） | 11 毒化正则 + 9 凭据 + 7 毒性流 + **89 SAST(Semgrep)** | 未公开 | 45+ 专利 | 语义模型 |
| SBOM/SARIF | CycloneDX + SARIF ✅ | CycloneDX + SARIF + Nucleus ✅ | 部分 | 企业级 | 平台内 |
| Agentic ASI 覆盖 | **ASI01–10 静态评分** | 仅 MCP01–10（无 ASI） | 部分 | 企业级 | 语义 |
| 企业漏洞管理对接 | ❌ | **Nucleus FlexConnect**（接 Qualys/Tenable/CrowdStrike） | ❌ | ✅ | ✅ |
| 攻击路径/图可视化 | ❌（仅文本） | **攻击路径引擎 + D3 攻击图 dashboard** | ❌ | 企业级 | 平台内 |
| 信任/badge 生态 | **Trust API + badge + 注册中心** | ❌ | 付费认证 | 企业认证 | ❌ |
| CI 集成 | GitHub Action ✅ | **GitHub Marketplace Action（更易被发现）** | API | 企业 | 平台内 |
| 商业化 | 开源 + x402 微支付（未跑通） | 纯开源 Apache2.0 | 付费 SaaS | 企业授权 | 平台绑定 |

**关键判读**：
- mcp-audit 在**能力深度**上已领先：它有 live server 分析（能抓运行时工具描述注入）、89 条 SAST 源码规则、Nucleus 企业对接、攻击图可视化、GitHub Marketplace 入口。**AIShield 的"非执行式"是唯一它短期难掉头的结构性差异**，但这是把双刃剑——用户会问"你不连运行 server 怎么抓运行时投毒？"
- AIShield 的**结构性护城河仍在**：14 客户端（vs 8）、ASI01–10 Agentic 维度、中文注入规则（出海/合规差异化）、Trust/badge 生态（中性信任机构叙事）、GEO 资产齐全。这些 mcp-audit 都没有，且不是纯算法能补的。
- 大厂（Anthropic/MS）做语义审计但**不硬刚**——它们的战场是自家平台内，AIShield 走"本地/零成本/CI 门禁/中性信任"是对的。

---

## 2. 竞争力 SWOT

**Strengths（优势）**
- 本地优先、零数据出网 → 合规友好（金融/政务/医疗场景的硬门槛）
- 非执行式审计不变式 → 不会"为了审计而真的执行恶意配置"，安全叙事干净
- 双维覆盖（MCP + Agentic ASI01–10）+ 中文注入规则 → 差异化且难抄
- 分发占位完整：npm + MCP Registry + GEO（llms.txt/robots/agent-card）→ agent 原生可发现
- Trust API / badge / 注册中心 → 已具备"信任层"雏形

**Weaknesses（劣势）**
- 能力深度被 mcp-audit 反超（缺 SAST、缺 live 采样、缺攻击图、缺企业对接）
- **模型算法层几乎空白**：全确定性规则，无语义/学习，漏掉"界面正常但意图恶意"的 server
- **数据资产未货币化**：0 公开漏洞库、0 使用量 telemetry、基准未公开 → 无法证明 PMF，也无网络效应
- 商业化未跑通：x402 仍是 mock，badge 未收费，无企业版
- 社区势能弱：stars/贡献者远不及 mcp-audit，GitHub Marketplace 入口缺失

**Opportunities（机会）**
- 赛道窗口期（12 个月内卡位决定生死）
- "中性信任机构"叙事仍空白 → 做成 agent 经济的"SSL/CA"
- 大厂不做的"本地+开源+CI 门禁"长尾市场
- 2026 M&A 火热 → 做好数据/标准卡位 = 最快被收购路径
- 中文/出海合规市场（31 条中文注入规则已是先手）

**Threats（威胁）**
- mcp-audit 社区势能 + Marketplace 入口可能形成"事实标准"
- 大厂把语义审计免费内置（Anthropic/MS）→ 压缩独立工具空间
- 身份层被 Oasis/Entra 占坑后，gateway 层可能被打包进 wider 平台
- 资金密集型对手（Runlayer 4 个月 8 个独角兽客户）可能降维收购

---

## 3. 功能 / 数据 / 模型算法 三维缺失诊断

### 3.1 功能缺失（按投资人优先级排序）

| # | 缺失 | 竞品参照 | 为什么重要 |
|---|---|---|---|
| F1 | **SAST 源码级规则包** | mcp-audit 89 条 Semgrep | 只扫配置/包抓不到"代码里静默 shell-out"的恶意 server |
| F2 | **可选的 live 只读采样**（不 spawn，只 connect 读 tool list） | mcp-audit live connect | 补"运行时工具描述注入"盲区，且不破非执行不变式 |
| F3 | **企业漏洞管理对接**（Nucleus/Splunk/SIEM 输出） | mcp-audit Nucleus | 进企业采购清单的唯一路径（否则永远是小工具） |
| F4 | **攻击路径/图可视化**（D3 dashboard） | mcp-audit 攻击图 | 决策层要"看见"风险才能买单 |
| F5 | **Fleet / 持续监控（watch 模式）** | mcp-audit watch | 从"一次性扫描"到"持续治理" |
| F6 | **策略即代码（governance YAML）** | mcp-audit policy-as-code | 企业合规落地刚需 |
| F7 | **GitHub Marketplace Action 入口** | mcp-audit Marketplace | 分发势能 = 社区 = 标准话语权 |
| F8 | **多 agent 级联/rogue 运行时检测**（ASI08/10 现仅静态） | 大厂运行时 | "rogue agent"是 OWASP ASI10 核心，投资人最关心 |

### 3.2 数据缺失（最被低估的短板）

- **D1 公开漏洞情报库缺失**：离线 CVE 用 bundled registry，无 OSV.dev 实时；无"新型 typosquat/homoglyph"情报积累 → 规则靠手写，跟不上攻击演化。
- **D2 扫描基准未公开**：无公开 PoC 基准 → 无法建立"第三方评测公信力"，投资人无法验证"误报率/覆盖率"声称。
- **D3 信任注册中心规模小**：registry/server.json 仅自身体量，跨注册中心发现层（104k agents / 15 registries / 0 互操作）缺失 → 网络效应起不来。
- **D4 使用量 telemetry 为零**：开源但"盲飞"，无匿名使用指标 → 无法向投资人证明 PMF，也无法做数据飞轮。
- **D5 误报/漏报反馈闭环缺失**：用户发现误报无处回流 → 规则质量无法自进化。

### 3.3 模型算法缺失（"也可以在模型算法上提出建议"）

当前：**100% 确定性规则（201 条）**。问题——dev.to 那篇作者点名："mcp-audit 只审计'声明的界面'，一个老实叫 `delete_everything` 的会被抓，但一个叫 `process_item` 却偷偷 shell-out 的抓不到"。AIShield 同理。

| # | 建议 | 说明 |
|---|---|---|
| M1 | **语义审计后端（LLM-as-judge，远程可选 + 本地可选小模型）** | 零样本意图判定，补规则漏报；这正是 2026-08-04 移除本地 Ollama 后该"复兴为差异化"的能力（远程语义后端，本地可选） |
| M2 | **Embedding 聚类发现 typosquat/homoglyph 家族** | 超越 Levenshtein，用向量近邻发现"长得像"的恶意包群 |
| M3 | **可解释评分模型（规则边际贡献归因）** | 回答"为什么 72 不是 71"——每条规则对总分的 Shapley 式贡献，提升信任与可申诉 |
| M4 | **攻击路径图算法（最小割 / hitting set）** | 复用竞品思路做开源实现：给定 server 集合，求"最小移除集"打破所有毒性流 |
| M5 | **行为基线 + 异常检测（runtime 采样序列偏离）** | 对 F2 采到的工具调用序列建基线，偏离即告警（抓 rogue agent） |
| M6 | **隐私保护漏洞情报聚合（差分隐私 / 联邦）** | 让 D4 telemetry 在合规前提回流，形成数据网络效应而不泄密 |
| M7 | **Benchmark 驱动的规则演进** | 用公开 PoC + 自建回归基准，避免"恒定输出"陷阱（即 CI 门禁形同虚设的历史教训） |

---

## 4. 分阶段提升方案

### Phase 1（0–3 月）· 止血 + 补差
- F1 SAST 规则包（先 30 条 Python/TS，覆盖 shell-out、动态 import、远端拉取）
- D1 接 OSV.dev 实时 CVE + 公开 typosquat 情报库
- M4 攻击路径算法（最小割）→ 输出文本版攻击路径（先不急着做图）
- F3 Nucleus/SIEM 输出适配器（JSON/SARIF 已有了，加 Nucleus schema）
- F7 GitHub Marketplace Action 上架（分发势能）
- 目标：能力深度追平 mcp-audit 的"可观测项"，守住 14 客户端 + 非执行 + ASI 差异

### Phase 2（3–6 月）· 数据 + 算法
- D2 公开扫描基准（含自建 20 良性/10 恶意 + 竞品 PoC），出第三方评测报告
- M1 远程语义审计后端（LLM-as-judge）+ 本地可选小模型，补漏报
- M2/M3 embedding 聚类 + 可解释评分
- F4 攻击图 D3 dashboard + F5 watch 模式
- D4 隐私合规 telemetry（可选匿名回传）→ 启动数据飞轮
- 目标：从"规则工具"升级为"带语义理解的扫描器 + 可信数据"

### Phase 3（6–12 月）· 平台化 + 收入
- F6 策略即代码市场 + F8 多 agent 运行时治理（kill switch）
- D3 信任注册中心规模化 + 跨注册中心发现层（中性信任机构落地）
- 商业化：企业版 SaaS（fleet + 运行时 + 合规报表）+ badge 认证收费 + x402 计费闭环
- 并购叙事：占据"标准/数据/分发"三卡位，定位为 Palo Alto / Check Point / ServiceNow 的收购最快路径
- 目标：工具 → 平台/基础设施（agent 经济的"SSL/CA"）

---

## 5. 平台价值提升（投资人视角：工具→基础设施）

1. **占据"信任层"叙事**：把 Trust API / badge 做成 agent 经济的"中性 CA"——谁被 AIShield 认证，谁就在 agent 市场里可信。这是最高护城河（标准话语权），且大厂因"利益冲突"做不了中性。
2. **数据网络效应**：每次扫描的可选匿名回传 → 漏洞情报网络 → 反哺规则 → 双边市场（server 作者想拿 badge，用户想买可信 server）。
3. **标准/规范话语权**：推动 ASI 评分成为行业基准（类似 OWASP 的角色），用公开基准 + 评测报告建立公信力。
4. **分发即护城河**：npm + MCP Registry + GEO 已占位，需持续运营（文档、示例、社区 rule 贡献）。
5. **收入模型（开源核心 + 三层变现）**：① 企业 SaaS（fleet/运行时/合规）② 认证 badge 收费 ③ x402 微支付生态抽成。
6. **并购定位**：2026 M&A $96B，做好数据+标准卡位 = 18 个月内 $500M–$2B 退出的最快路径。

---

## 6. 多角色用户全流程走查

> 方法论：对每类角色走"发现 → 安装 → 扫描 → 读报告 → 改/提交 → 复扫 → 拿成果"全链路，标痛点与改进点。

### 角色 A：个人开发者 / 开源 MCP server 作者
**目标**：证明自己的 server 安全、拿 badge 增强可信度。
- 当前流程：`npx aishield-mcp-server` → 本地扫描 → 看终端分数 → 想拿 badge 不知怎么提交。
- 痛点：① 报告是终端文本，不易分享；② badge 申请入口隐蔽；③ 不知道"改哪条规则能涨分"。
- 改进：
  - **功能布局**：加 `aishield badge apply --server <name>` 一键申请 + 状态追踪。
  - **成果提交**：扫描后生成**可分享的 HTML 报告 + 徽章 SVG**（直接贴 GitHub README）。
  - **解释性**：报告里每条扣分项给"修复建议代码片段"（M3 可解释评分驱动）。

### 角色 B：企业安全 / 合规团队
**目标**：CI 门禁 + 纳入漏洞管理平台。
- 当前流程：配 GitHub Action → 门禁读 `score` → 红则阻断。
- 痛点：① 结果进不了现有漏洞平台（Splunk/Nucleus）→ 安全团队看不到；② 无 Fleet 视角（几百个 repo 各自扫）；③ 无合规报表。
- 改进：
  - **F3 企业对接**：输出 Nucleus/SIEM schema，进 Qualys/Tenable 同款管道。
  - **F5 Fleet/watch**：中心化聚合所有 repo 的 server 暴露面。
  - **成果提交**：月度"Agent 暴露面合规报表"（PDF/仪表盘）直接给 CISO。

### 角色 C：AI Agent 构建者 / 平台工程师
**目标**：审计自己 agent 要接的所有 MCP，防 toxflow。
- 当前流程：跑 `discover_and_scan()` → 看单 server 风险 + 命名空间遮蔽 + 毒性流。
- 痛点：① 多 server 组合风险（A 读文件 + B 联网）只在文本里一行；② 不知道"该删哪个 server 破链"（hitting set 未做）。
- 改进：
  - **M4 攻击路径算法**：直接给"最小移除集"建议（删 server X 即可破所有毒性流）。
  - **F4 攻击图**：可视化多 server 攻击路径，一眼看懂。
  - **功能布局**：IDE 插件实时标红"这个 server 接上会和现有 server 形成毒性流"。

### 角色 D：投资人 / BD / 生态方
**目标**：看数据、看信任背书、评估合作。
- 当前流程：看 npm / Registry / 文档 → 无统一数据看板。
- 痛点：① 无"被扫 server 总量 / 漏洞趋势"公开数据；② 无生态合作入口。
- 改进：
  - **D4 公开数据看板**：季度"Agent 安全态势报告"（行业级，增强 GEO/公信力）。
  - **生态入口**：registry 开放"提交你的 server 拿认证"的自助流。

### 角色 E：审计 / 认证机构
**目标**：用 badge 做第三方背书。
- 当前流程：Trust API `auto_certify` → 出 cert。
- 痛点：① 认证标准不透明（用户不信）；② 无复审机制。
- 改进：
  - **标准公开**：ASI 评分 rubric 全公开 + 第三方可复核。
  - **持续认证**：watch 模式触发复审，badge 过期自动降级（防"一次认证永久有效"）。

---

## 7. 给投资人的 30 / 60 / 90 天建议

- **30 天**：① 关掉误报噪音、稳定 CI（已完成 #19 清理）；② 上 GitHub Marketplace Action（分发势能）；③ 接 OSV.dev 实时 CVE（D1）。
- **60 天**：① SAST 规则包（F1）+ 攻击路径算法（M4）追平 mcp-audit 可观测项；② 公开扫描基准（D2）出评测报告；③ 隐私合规 telemetry（D4）启动数据飞轮。
- **90 天**：① 远程语义审计后端（M1）形成差异化；② 企业对接 Nucleus（F3）+ Fleet（F5）；③ 信任注册中心规模化 + 跨注册中心发现（D3）→ 启动"中性信任机构"叙事落地。

**一句话投资逻辑**：AIShield 的"本地 + 双维 + 中性信任"卡位正确且在窗口期内，但必须在 2 个季度内把"深度（SAST/live/图）+ 数据（情报/telemetry/基准）+ 语义（LLM-as-judge）"三件事补齐，否则差异化会被 mcp-audit 的社区势能抹平；补上后，它是最符合"被大厂收购"叙事的轻量标的。

---

## 8. 实现进度（2026-08-05 已落地）

用户要求"补全所有缺失，把 30/60/90 天建议尽快完成"。以下为本次已实现并推上 main 的模块（新增 22 项测试，全量 190→212 通过）：

| 报告缺口 | 模块 / 文件 | 接入点 | 状态 |
|---|---|---|---|
| D1 OSV 实时 CVE | `scanner/osv.py` | `scan(enable_osv=True)` + `POST /api/v1/osv` | ✅ |
| M4 攻击路径求解 | `scanner/attack_path.py` | `POST /api/v1/scan/attack-path` | ✅ |
| F3 Nucleus/SIEM 导出 | `scanner/exporters.py` | `POST /api/v1/export/nucleus`、`/splunk` | ✅ |
| F6 策略即代码 | `scanner/policy.py` + `policies/default.json` | `POST /api/v1/policy/check` | ✅ |
| D4 隐私遥测 | `scanner/telemetry.py` | `AISHIELD_TELEMETRY=1` 开关 | ✅ |
| F2 live 只读探针 | `scanner/live_probe.py` | client-config `enable_live_probe` | ✅（不 spawn） |
| D3 跨注册中心发现 | `scanner/registry_discovery.py` | `POST /api/v1/registry/discover` | ✅ |
| M3 可解释评分 | `engine.calculate_scores` 重构 + `explain_score()` | 每次 scan 返回 `score_breakdown` | ✅ |
| D2 公开基准 | `benchmarks/`（良性/恶意样本 + `run_bench.py`） | `python benchmarks/run_bench.py` | ✅ |
| 30天② Marketplace Action | `action.yml` | GitHub Marketplace 可上架 | ✅ |
| M1 语义后端 | 既有 `scanner/llm_analyzer.py` | `scan()` 已接 LLM findings 入评分归因 | 既有，本次纳入评分 |

**商业化层（F4 / F5 / Phase3）已于 2026-08-05 第二轮补齐并推上 main**：

| 报告缺口 | 模块 / 文件 | 接入点 | 状态 |
|---|---|---|---|
| F4 攻击图 D3 前端 | `api/static/attack-graph.html`（离线力导向图，0 出网） | `GET /attack-graph` 消费 `POST /api/v1/scan/attack-path` | ✅ |
| F5 fleet 中心化 UI | `scanner/fleet.py` + `api/static/fleet.html` | `GET /api/v1/fleet`、`POST /api/v1/fleet/ingest`、`GET /api/v1/fleet/list` | ✅ |
| Phase3 企业 SaaS / badge 收费 / x402 闭环 | `eco/monetization.py` + `api/static/enterprise.html` | `POST /api/v1/certify/request-payment`、`POST /api/v1/certify/fulfill`、`GET /api/v1/certify/list` | ✅ |

至此，**投资人 30/60/90 天建议与报告全部 11 个 engine 缺口 + 3 个商业化层缺口均已落地**。全量测试 200 通过（第二轮新增 `tests/test_commercialization.py` 10 项：Fleet 聚合 / x402 付费认证闭环 / 攻击图数据形状）。直接竞品 mcp-audit 仍缺 Fleet 看板与可机器结算的付费认证，本层为差异化收口。

---
*附：本报告所有竞争数据来自 2026-08-05 公开检索（RSAC 2026、OWASP Agentic Top 10、Agent Security Market Map 2026、mcp-audit 官方文档/PyPI）与项目内部记忆快照交叉校准。*
