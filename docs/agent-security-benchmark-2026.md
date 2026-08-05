# AIShield Agent 安全基准报告 2026

> 版本: v4.2 · 发布: 2026-08-04 · 标准: OWASP MCP Top 10 (2025) + OWASP Agentic AI Top 10 (2025)
> 域名: https://aishield.tools · 授权: 开源 / 本地 / 零成本 / Agent 原生

---

## 1. 为什么需要这份基准

2026 年 Agent 安全市场从「单点 MCP 工具扫描」跃迁为「**Agentic 全生命周期安全 + 身份认证 + 能力交易 + 本地小模型**」四位一体。
AIShield 是少数同时覆盖 **MCP Top 10** 与 **Agentic AI Top 10** 双维、且以「本地 / 零成本 / 开源」为内核的扫描器。

本报告给出可验证的能力基线，供安全团队、Agent 市场、开发者对照采用。

---

## 2. 方法论

| 维度 | 能力 | 说明 |
|------|------|------|
| 静态规则 | **201 条正则检测规则** | 110 MCP 规则 + 60 Agentic(AIS) 规则 + 31 中文提示注入规则 |
| 语义分析 | LLM 可选后端 | Tool Poisoning 语义（可选远程 LLM）；规则引擎零依赖、全程本地 |
| 供应链 | SBOM + 依赖审计 | CycloneDX 1.5 SBOM 输出、危险包黑名单(OSV/NVD 情报驱动) |
| 幻觉包 | **离线 slopsquat 检测** | 编辑距离 typosquat + homoglyph + 品牌仿冒 + **复合式幻觉(非形近)** + 跨注册表混淆 + 依赖混淆；零网络、零包数据库 |
| 依赖卫生 | manifest 级检查 | 安装脚本投毒(critical)、非注册表来源(high)、未锁定版本(medium)、缺 lockfile(low) |
| 可集成 | SARIF 2.1.0 | 直接接入 GitHub Code Scanning / 任意 SARIF 工具链 |
| 信任层 | Trust API | 自动签发认证证书 + 0-100 信任评分，供服务交易市场调用 |

---

## 3. 覆盖范围矩阵

### 3.1 OWASP MCP Top 10（110 条规则）

| 编号 | 类别 | 规则数 |
|------|------|-------|
| MCP01 | Improper Token & Secret Management | 16 |
| MCP02 | Privilege Scope Creep | 12 |
| MCP03 | Tool Poisoning | 8 |
| MCP04 | Software Supply Chain Attack | 9 |
| MCP05 | Command Injection & Execution | 24 |
| MCP06 | Intent Flow Subversion / Prompt Injection | 14 |
| MCP07 | Insufficient Authentication & Authorization | 8 |
| MCP08 | Lack of Audit & Observability | 6 |
| MCP09 | Shadow MCP Servers | 6 |
| MCP10 | Context Injection & Over-Sharing | 7 |

### 3.2 OWASP Agentic AI Top 10（60 条规则，AIShield 新增）

| 编号 | 类别 | 规则数 |
|------|------|-------|
| ASI01 | Goal and Instruction Manipulation | 6 |
| ASI02 | Tool Misuse | 6 |
| ASI03 | Excessive Agency | 6 |
| ASI04 | Memory Manipulation (记忆投毒) | 6 |
| ASI05 | Agent Identity and Trust | 6 |
| ASI06 | Agent Communication & Supply Chain | 6 |
| ASI07 | Unbounded Resource Consumption | 6 |
| ASI08 | Observability and Monitoring Gaps | 6 |
| ASI09 | Cascading Failures & Multi-Agent Risks | 6 |
| ASI10 | Rogue Agent & Human-Autonomy Boundary | 6 |

> 竞品对照：mcp-audit(89 SAST 规则, 无 Agentic 维) · aishield.ai(4D 评分, 无 ASI) · mcp-scan(OWASP A-F, 无 ASI) · Claude Security(语义强但**上云**、闭源、按量计费)。**AIShield 唯一同时具备 MCP+Agentic 双维 + 本地零成本**。

---

## 4. 实测基准（样例 Agent 配置）

对一份含典型风险的 Agent 配置扫描，结果：

- 命中 **6/10 ASI** 类别：ASI01(目标操纵)、ASI03(过度代理)、ASI07(无限制资源)、ASI08(监控缺口)、ASI09(级联风险)、ASI10(流氓 Agent)
- 命中 **1/10 MCP**：MCP06(提示注入)
- 语义层额外捕获：记忆投毒(ASI04)需知识库语料，样例未含
- 输出附带 **CycloneDX SBOM** 与 **SARIF**，可直接进 CI

> 复现：`python -c "from scanner.rules import analyze; ..."` 或 `curl -XPOST /api/v1/audit`。

---

## 5. 差异化定位

| 维度 | AIShield | Claude Security | aishield.ai | mcp-audit | mcpaudit(PyPI) | agent-security-scanner-mcp |
|------|----------|----------------|-------------|-----------|----------------|----------------------------|
| MCP Top 10 | ✅ 110 规则 | 语义(云) | ✅ | ✅ 89 | ✅ 72+ | ✅ |
| Agentic AI Top 10 | ✅ 60 规则 | 部分 | ❌ | ❌ | ⚠️ 宣称覆盖 | 部分 |
| 本地/零依赖 | ✅ 规则引擎本地零依赖 | ❌ 上云 | ❓ | ✅ | ✅ | ⚠️ 需 430 万包库 |
| 零成本 | ✅ 开源 | ❌ 计费 | ❌ 付费 | ✅ | ✅ | ✅ |
| SBOM/SARIF | ✅ | ⚠️ | ❌ | ✅ SBOM | ✅ SARIF | ✅ CycloneDX |
| 信任/认证 API | ✅ L1–L3 + 0–100 分 | ❌ | ⚠️ | ❌ | ⚠️ 仅 Trust Score | ⚠️ 仅 A–F 评级 |
| 幻觉包检测 | ✅ **含非形近幻觉（离线）** | ❌ | ❌ | ⚠️ 仅 typosquat | ❌ | ✅ 大库比对 |
| 跨注册表混淆 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 依赖卫生（安装脚本/锁文件） | ✅ | ⚠️ | ❌ | ⚠️ | ❌ | ✅ |
| 中文提示注入 | ✅ 31 条 | ⚠️ | ❌ | ❌ | ❌ | ❌ |

> **诚实标注**：测试规模上 AIShield（127）低于 mcp-audit（2,484）与 mcpaudit（6,430+）；深度 AST/taint 分析弱于 agent-security-scanner-mcp（1,000+ 规则、12 语言）。AIShield 的差异化不在"规则条数"，而在**双维覆盖 + 中性信任层 + 全离线幻觉包检测**这三项组合。

### 5.1 2026-08 生态快照：竞争全景（运营情报更新）

mid-2026 的 MCP/Agent 安全品类已显著拥挤，分三派：

| 派系 | 代表 | 形态 | 与 AIShield 关系 |
|------|------|------|------------------|
| 开源静态扫描 | Cisco mcp-scanner、Invariant mcp-scan、Snyk agent-scan、**agent-security-scanner-mcp(sinewaveai)**、mcp-audit | CLI/规则 | 直接竞品（多为 MCP-only） |
| 云 SaaS | Akto、Nightfall AI、ScanMCP.com、Equixly、**aishield.ai** | 上传代码/流量到云 | 被「本地不上云」差异化压制 |
| 企业网关/平台 | Palo Alto Prisma AIRS AI Gateway(GA 2026-07-16)、Cyera AI Guardian、Teleport、MCP Guardian(EQTY Lab)、Cisco AI Defense | 运行时 inline/代理 | 定位不同（运行时 vs 扫描+信任） |

**关键威胁数据（论证紧迫性）：** Palo Alto Unit 42 测得单 agent 连 5 个 MCP server 时 **78.3%** 独立攻击成功率；Cisco 分析 **31,000+** agent skills 中 **26%** 含 ≥1 漏洞；Dark Reading poll 显示 48% 安全从业者视 agentic AI 为 2026 头号攻击向量。

**供应链专项（2026-08 更新）：** USENIX Security 2025 测 16 个模型 / 57.6 万代码样本，**19.7%** 的模型推荐包不存在，产生 **205,474** 个唯一虚构包名，**43–58%** 可复现（开源模型 21.7% vs 商业 5.2%；2026 复现研究收敛至 4.62%–6.10%，未归零）。其中**约 50% 的幻觉名与任何真实包都不形近**，相似度/编辑距离检测结构性失效；另有 **8.7%** 的 Python 幻觉名在 npm 上真实存在，构成跨注册表攻击面。真实案例：`react-codeshift`（2026-01）经 **AI 生成的 skill 文件** 在 **237 个仓库** 间 agent→agent 扩散。**AIShield v4.2.0+ 已针对这两类盲区补齐纯离线检测。**

**AIShield 可放大优势（错位竞争，不硬刚）：**
1. **本地零依赖、代码不上云** —— 压制所有云 SaaS（Nightfall/Akto/ScanMCP/aishield.ai）。
2. **双维覆盖 MCP Top 10 + Agentic AI Top 10(ASI01–10)** —— 多数竞品仅 MCP-only。
3. **中性信任机构（空白点）**：认证 L1–L3 + 0–100 信任分 + 可嵌入 badge + Trust API + x402 —— 全品类无人做中性信任注册中心，AIShield 先发卡位。
4. **CI 门禁 + SBOM + SARIF** —— 比仅运行时或仅扫描更可落地。
5. **Agent-native & GEO**（llms.txt / Agent Card / MCP Server Card / A2A-ready）—— 竞品几乎无 agent 可发现存在。
6. **供应链幻觉包检测（已落地）**：离线 typosquat / 形近字符(homoglyph) / 厂商仿冒检测（Levenshtein 编辑距离 + 归一化 + 熵启发式），纯本地零依赖、不联网，覆盖 package.json / requirements.txt / pyproject.toml —— 直接补齐与 agent-security-scanner-mcp「幻觉包检测」的差距，且无需上传代码。

> 直接竞品 agent-security-scanner-mcp（1700+ AST 规则、A-F 评级、幻觉包检测）概念最接近「4维评分+badge」；AIShield 以「生态扫描(MCP/skill/agent)+认证信任+x402 市场+本地幻觉包检测」错位竞争，不拼语义深度。

---

## 6. 采用方式

1. **开发者**：`npx aishield-mcp-server scan <repo>` 或自托管 `python api/server.py`
2. **Agent 市场**：调用 Trust API (`/api/v1/trust/score/{agent_id}`) 对挂牌 agent 出安全证书
3. **CI**：消费 `/api/v1/export/sarif` 接入 GitHub Code Scanning
4. **安全团队**：订阅 CycloneDX SBOM 做供应链持续监控

---

*本报告由 AIShield 自动化情报飞轮生成，规则库随 OSV/NVD/GitHub Advisory 情报持续更新。*
