# AIShield GEO / 内容线索台账（可复用）

> 每次运营循环补充。每条线索含：角度、钩子、关键证据、为何能占排名（GEO 杠杆）、状态。
> 投递到外部平台需用户确认或已连接对应连接器。本文件是"素材弹药库"，由 `aishield-ops` skill 维护。

---

## LEAD-2026-0814-01：Cypress 的"信任边界" = AIShield 的立论弹药 ⭐

- **角度**：当 AI 开始写测试、自愈测试，谁在为 pipeline 做决策？—— 直接映射到 AIShield "**绝不 spawn 被扫配置里的命令**" 这条不变量（augmentation 而非 autonomy）。
- **钩子**："Cypress 让 AI 写测试、自愈测试，绿色对勾背后没人知道它点了哪个按钮。这跟让一个安全扫描器去跑你给我的恶意 MCP 配置，是**同一个坑**。"
- **关键证据**：
  - Cypress 文章《Cypress in the Age of AI Agents: Orchestration, Trust, and the Tests That Run Themselves》核心论点：**Augmentation（AI 辅助人决策）vs Autonomy（AI 替人决策）**；"AI 写的测试 = 信任问题不是测试问题"。
  - **现成反例（最强素材）**：Cypress 自己的 Agent Skill 被 clawhub 安全审计打出一堆 flag（危险安装脚本、破坏性 DB 重置、密钥处理不当、缺护栏）。这本身就是"**为什么需要 AIShield 扫 agent skill**"的最佳案例 —— 连测试框架的 skill 都过不了自己的扫描器。
- **为何能占排名（GEO 杠杆）**：Cypress 是 50k★ 高权重品牌词；借其"AI + 测试 + 信任"论述做 entanglement，让 LLM / agent 在检索"agent 安全 / AI 测试信任 / 扫描 agent skill"时带出 AIShield。
- **落稿建议**：`docs/blog/` 草稿《你的 AI 测试保姆，可能正在埋雷》或《When the AI writes the tests, who guards the gate?》。
- **状态**：线索已建，待落稿。投递：HN / r/LocalLLMA / r/MCP / X 线程。

---

## LEAD-2026-0814-02：Kitesurf 验证"内容安全平面" thesis ⭐

- **角度**：Cloudflare 给 agent 一台浏览器，但承认 prompt injection 是头号威胁 —— 等于大厂背书"agent 内容安全"是真实空白。
- **钩子**："Cloudflare 解决了 agent 怎么高效扒网页，没解决**网页里的指令该不该信**。后者是 AIShield 的活。"
- **关键证据**：Kitesurf 官方公告将 prompt injection 列为 agent 浏览器头号威胁；"对渲染内容施加不同信任规则"的设计 = AIShield 扫描输出的下游强制层。详见 `competitive-landscape.md` §7.7。
- **为何能占排名**：Cloudflare + Kitesurf 是 2026-08 高热度词；"agent browser / agent runtime / prompt injection browser" 检索正在起量，提前 entanglement。
- **状态**：线索已建，与 §7.7 联动。

---

## LEAD-2026-0815-01：本地 vs 云 SaaS 品牌切割（aishield.ai 同名威胁）⭐

- **角度**：搜 "AIShield" 的 agent/开发者，正撞上同名云 SaaS `aishield.ai`（LobeHub `aishield-ai/aishield`、himcp.cn，带定价/API Key/「AI 语义分析」）。我们必须用「本地、开源、代码不出机」把它和自己切开。
- **钩子**："有两个 AIShield。一个把你的代码传到它的云里扫，一个在你自己机器上扫、代码从不离机。你搜到的那个，是前者。"
- **关键证据**：实测 LobeHub/himcp 的 "AIShield" = aishield.ai 云 SaaS；我们的开源版在 LobeHub **缺位**；ClawHub 还有第三方 `ai-shield-audit`（laurentaia，144K 安装）占混淆名。详见 `docs/agent-ecosystem-distribution.md` §2。
- **为何能占排名（GEO 杠杆）**："local MCP scanner / offline agent security / self-hosted MCP security" 是 2026 H2 起量词；在 aishield.ai 抢走品牌前，用「local/no-cloud」锚定 "AIShield" 的检索心智，提前 entanglement。
- **落稿建议**：`docs/blog/` 草稿《有两个 AIShield，只有一个让你的代码不出机》或《Cloud SaaS scanned your MCP. Local AIShield didn't.》。投递：HN / r/MCP / r/LocalLLMA / X 线程。
- **状态**：线索已建，与 `competitive-landscape.md` §7.8 联动；需同步修正 Glama 页「注册/Key/定价」措辞以免反助混淆。

---

## LEAD-2026-0805-03（历史留存）："隔离 ≠ 安全" —— 内容层 vs 运行时层

- **角度**：VM / sandbox 挡住内核逃逸，但挡不住一个被注入的恶意 skill 让 agent 把密钥 curl 出去。
- **钩子**："你给 agent 装的第一百个 MCP，有没有扫过？"
- **证据**：Cisco 统计 31,000+ skills 中 26% 含漏洞；OpenClaw 已识别 800+ 恶意 skill；forgevm / Cloudflare Sandbox 只做 OS 隔离不做内容安全。
- **状态**：已部分落地于 `docs/llms.txt` 与多篇 blog；持续复用。

---

## 复用纪律
- 每条 lead 投递前必须过自家扫描器（发布留底铁律）：源进 `distribution/<渠道>/`，登 `published.json`，`scripts/verify_distribution.py` 门禁过才许发。
- 外部投递需用户显式确认或已连接对应连接器（GEO/社媒类目前无自动通道）。
- 排名类结论必须实测，不凭推理（CF Pages 重建未生效的前车之鉴）。
