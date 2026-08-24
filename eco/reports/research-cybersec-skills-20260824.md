# 调研：anthropic-cybersecurity-skills 对 AIShield 扫描能力的借鉴价值

> 调研日期：2026-08-24 · 结论：**高价值，四个可落地借鉴点 + 一个现成集成件**

## 一、目标库是什么

`mukul975/Anthropic-Cybersecurity-Skills`（注意：社区项目，非 Anthropic 官方；30.7k stars，Apache 2.0）

| 维度 | 数据 |
|---|---|
| 规模 | 817 个技能（skills.sh 显示已至 833）· 29~34 安全域 |
| 标准 | agentskills.io：SKILL.md（YAML frontmatter + 结构化正文） |
| 框架映射 | ATT&CK×805 · NIST CSF 2.0×804 · D3FEND×139 · NIST AI RMF×97 · MITRE F3×94 · **MITRE ATLAS×93** |
| 加载成本 | 渐进式披露：frontmatter ~30 token 扫描，全文 500–2000 token |
| 结构 | SKILL.md（When to Use / Prerequisites / Workflow / Verification）+ references/standards.md + 可运行 scripts/ |

与 AIShield 最相关的三个域：
- **AI Security（12 技能）**：garak/PyRIT 红队、直接+间接提示注入、RAG 投毒、**MCP 工具投毒**、agentic 工具调用管控、运行时 guardrails —— 与本仓规则域完全重叠
- **Supply Chain Security（5 技能）**：SBOM、依赖混淆、恶意 npm 包甄别、typosquatting 检测 —— 呼应 acquisition/npm-self-heal 已覆盖面
- **Vulnerability Management（25 技能）**：扫描工作流、补丁优先级、CVSS

## 二、可借鉴点（按投入产出排序）

### 1. 给雷达规则加框架映射字段 ⭐ 最贴合定位
MITRE **ATLAS 2026.07** 新增了 agentic AI 攻击向量：AI agent 上下文投毒、工具调用滥用、**MCP server 入侵**、恶意 agent 部署——这正是 AIShield 的主战场。
- 动作：`radar_rules.json` schema 增加 `atlas_techniques` / `d3fend_techniques` / `nist_csf` 字段；`promote_rule.py` 六道闸门加一道"映射 ID 格式合法"校验
- 成本：低（schema 扩展 + 校验正则）；收益：产品可信度对标行业框架，营销物料直接可用

### 2. 规则文件渐进式披露结构
该库每条技能 frontmatter 即可检索。本仓 `scanner/rules/*.json` 已有元数据，但对齐方向：保证 id/severity/owasp_category/frameworks 全部前置在头部固定位置，便于外部 agent（含我们自己的 MCP server）低成本枚举规则。

### 3. 晋升闸门引入"验证面板"模式
Anthropic 官方 defending-code-reference-harness 的核心是 Researcher→独立 Verifier 面板压误报。对应到本仓：
- `promote_rule.py --promote-all` 目前六道静态闸门；可加第七道：候选规则先跑扩充版良性语料 + 对抗样本集（现有良性语料之外的负样本），通过才入库
- rule-promoter.yml 的测试回滚安全阀已是同思想的第一步，语料扩充是其自然延伸

### 4. 威胁模型驱动的扫描分域
harness 用 threat model 划分子系统再并行扫描以降误报。对应：scanner 按 target 类型（agent-card / tool-description / HTTP endpoint / skill manifest）给规则打适用域标签，避免跨域误报——与六道闸门中"不过宽"互补。

## 三、现成集成件（ROADMAP 缺口直填）

`anthropics/claude-code-security-review`：官方 GitHub Action，diff 感知 PR 扫描 + 误报过滤 + PR 行级评论。
- 直填 ROADMAP 未勾选项「支持 PR 评论自动标注安全风险」：ci.yml 或新 workflow 中 `uses: anthropics/claude-code-security-review@main`，需配 `CLAUDE_API_KEY`
- 注意：按 token 计费，建议只在 PR 事件触发（勿挂 hourly cron）

## 四、分发侧机会

agentskills.io 生态（skills.sh、awesome-agent-skills 等）正处于爆发期（该库 5 个月 30k stars）。AIShield 可把自己的 MCP 安全知识打包成兼容 skill 包发布（如 `scanning-mcp-servers-for-tool-poisoning`），复用既有生态卡位策略，零边际成本新增一条分发渠道。

## 五、不建议照搬

- 833 技能全量引入作依赖：体量过大且与本仓规则引擎形态不同；只借 schema 与流程思想
- ATT&CK v19 变更（2026-04-28 拆分 Defense Evasion 为 Stealth/Impair Defenses）：若做框架映射需按 v19.1 起，避免二次迁移

---
*调研来源：GitHub README/releases、skills.sh、anthropics/claude-code-security-review、anthropics/defending-code-reference-harness*
