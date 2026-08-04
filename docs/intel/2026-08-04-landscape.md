# AIShield 情报简报 — 2026-08-04（运营飞轮首轮）

> 由私有 skill `aishield-ops` 驱动，配合周度自动化 `automation-1785849857521`。

## 0. 本轮做了什么
1. 创建**私有**运营 skill：`~/.workbuddy/skills/aishield-ops`（不发布、不共享），封装「扫描 → 预测 → 竞品优势最大化 → 推广落地」标准循环，附 `references/competitive-landscape.md` 活竞争态势表。
2. 建立**周度自动化**（每周一）：`automation-1785849857521`「AIShield 周度竞争情报与推广」，持续扫描开源平台 + 媒体。
3. 执行首轮运营：实时扫描，更新 GEO / 基准 / 博客等推广资产。

## 1. 扫描信号（按类）

### 威胁 / 数据
- Palo Alto Unit 42：单 agent 连 5 个 MCP server 时 **78.3%** 独立攻击成功率。
- Cisco：分析 **31,000+** agent skills，**26%** 含 ≥1 漏洞。
- Dark Reading poll：48% 安全从业者视 agentic AI 为 2026 头号攻击向量。
- Cisco State of AI Security 2026：83% 计划部署 agentic AI，仅 29% 觉得准备好了。
- CVE-2025-54136：Cursor MCP「rug pull」信任绕过（2025-07）。

### 标准动量
- OWASP Agentic AI Top 10（ASI01–10）：2025-12 发布，已成新基线，100+ 专家，NIST/EC/Alan Turing 评估。
- NIST AI Agent Standards Initiative：2026-02。
- Five Eyes《Careful adoption of agentic AI》：2026-05。
- A2A 协议 v1.0.0（Linux 基金会，150+ 组织）；Agent Card 在 `/.well-known/agent-card.json`。
- x402 支付（Linux 基金会，100M+ 笔）：agent-to-agent USDC。

### 竞品 / 新进入者（mid-2026 品类已拥挤）
- **agent-security-scanner-mcp (sinewaveai)**：开源 MIT，1700+ AST/taint 规则（12 语言），A-F 评级，幻觉包检测（430 万+ 包），OpenClaw 集成，支持 Claude Code/Cursor/Windsurf/Cline/Gemini CLI。**最接近「4维评分+badge」概念的直接竞品**。
- **Palo Alto Prisma AIRS AI Gateway**：2026-07-16 GA，inline 检测 MCP tool call、agent-to-agent、prompt injection。企业级，非我车道。
- **Nightfall AI**：DLP 视角，宣称 95% 检测精度、实时 MCP 覆盖，SaaS。
- **Cyera AI Guardian / Teleport / ScanMCP.com / Equixly / MCP Guardian(EQTY Lab) / Cisco AI Defense**：各自切入（DSPM / 零信任 / 云扫描 / 治理 / 代理护栏）。
- 既有：Cisco mcp-scanner、Invariant mcp-scan、Snyk agent-scan、mcp-audit、aishield.ai、Akto。

### 生态结构
品类三派：**开源静态扫描**（多为 MCP-only）/ **云 SaaS**（上传代码或流量到云）/ **企业网关/平台**（运行时 inline 或代理）。AIShield 错位卡位在「本地 + 双维 + 中性信任机构」。

## 2. 预测性分析（未来 3–6 个月）
1. **MCP Top 10 成表桩，Agentic AI Top 10 成新基线**：仅 MCP-only 的工具会被视为过时。AIShield 已覆盖 ASI01–10 → 先发卡位「唯一双维 + 本地」。
2. **运行时/网关整合加速**：Palo Alto / Invariant proxy / Nightfall 抢运行时。AIShield 不硬刚，定位「CI 门禁 + 本地预检 + 信任背书」补充层。
3. **Agent 身份与信任 = 下一前沿**（ASI03/07/10）：A2A、Agent Card、独立身份、kill switch。中性信任注册中心仍是**空白** → AIShield Trust API + badge + x402 占此位。
4. **Supply chain（ASI04）升温**：幻觉包检测成标配（agent-security-scanner-mcp 已做）。AIShield 已有 CycloneDX SBOM，建议补「包名真实存在」钩子。
5. **本地/不上云 = 隐私护城河**：Five Eyes 谨慎采用 + 监管敏感 → 云 SaaS 受限。AIShield 零依赖本地扫描吃此红利。
6. **GEO / agent-native 发现成标配**：llms.txt / Agent Card / A2A。竞品几乎无 → AIShield 先发可见性优势。

## 3. 竞品优势最大化

### 可放大点（错位竞争，不硬刚）
- **本地零依赖、代码不上云** —— 压制所有云 SaaS（Nightfall/Akto/ScanMCP/aishield.ai）。
- **双维覆盖 MCP Top 10 + Agentic AI Top 10(ASI01–10)** —— 多数竞品仅 MCP-only。
- **中性信任机构（空白点）**：认证 L1–L3 + 0–100 信任分 + 可嵌入 badge + 机器可调用 Trust API + x402/USDC —— 全品类无人做中性信任注册中心。
- **CI 门禁 + SBOM + SARIF** —— 比仅运行时或仅扫描更可落地。
- **Agent-native & GEO**（llms.txt / Agent Card / MCP Server Card / A2A-ready）—— 竞品几乎无 agent 可发现存在。
- **开源免费** —— 对比付费（aishield.ai/Nightfall/Akto；agent-security-scanner-mcp 同为免费/MIT）。

### 薄弱点（诚实记录）
- 语义/深度代码分析弱于 agent-security-scanner-mcp（1700+ AST 规则）→ 错位竞争「生态扫描 + 信任认证」，不拼语义深度。
- 无运行时/网关能力 → 定位补充层，不越界。
- 社区声量 < 大厂 → 靠 GEO + 技术内容输出补。
- 缺「幻觉包检测」→ 建议在规则层补 supply-chain 包名校验钩子。

## 4. 本轮推广改动（已落地文件）
- `docs/llms.txt` / `docs/llms-full.txt`：规则数 **141 → 201**；刷新差异化话术；竞争定位表扩到 4 类对手；路线图改为「v4.2.0 已交付 + 下一步」。
- `docs/.well-known/agent-card.json`：风险类目 **141 → 201**。
- `docs/agent-security-benchmark-2026.md`：新增 §5.1「2026-08 生态快照：竞争全景」，含三派表、威胁数据、5 条可放大优势。
- `docs/blog/blog-agent-trust-gap-2026-08-04.md`：新文章《The agent trust gap》（英文，面向 HN/Reddit/Lobsters），角度 = 本地 + Agentic AI Top 10 + 中性信任机构。已入 `docs/blog/index.md`。
- 私有 skill `aishield-ops` + 周度自动化建立。

## 5. 待办 / 需用户手动
- [ ] **发布本轮内容到外部渠道**：HN / Reddit(r/LocalLLaMA, r/MCP) / Lobsters 发博客；X 线程草稿（我可生成）。
- [ ] 补「幻觉包检测」钩子（rules 层）以对标 agent-security-scanner-mcp。
- [ ] GitHub 手动三步仍未做：NPM_TOKEN / Pages 源选 GitHub Actions / `git tag v4.2.0 && git push` 触发发布链（见第七轮待办）。
- [ ] 下周自动化首跑（周一）将自动复扫并刷新本报告。

## 6. 一句话结论
品类已拥挤，但「本地不上云 + MCP+Agentic 双维 + 中性信任机构」的组合仍是**空白**，AIShield 先发卡位；本轮把已有能力如实露出并铺开 GEO/内容，下一步靠周度飞轮持续放大相对优势。
