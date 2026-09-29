# AIShield 竞品扫描报告（2026-09-29）

> 扫描方法：WebSearch + GitHub 主页阅读 + npm/PyPI 元数据。事实锚定到具体日期/版本/star 数，非记忆推断。
> 结论层：AIShield 面临**4 个直接竞品同时挤压**，但**在 agent memory 安全扫描品类里仍有空白**。

---

## 一、4 个直接竞品实况（2026-06 至 2026-09）

| 项目 | 首版 | 规模 | 规则/探针 | 生态位差异 |
|---|---|---|---|---|
| **NVIDIA/SkillSpector** | 2026-05-11 | v2.3.7, 187 commits, Jun 28 latest | 68 patterns / 17 categories, YARA 签名, taint tracking | **大厂背书**：NVIDIA 出品；LangGraph + Pi extension；OSV.dev 实时 CVE |
| **getagentseal/agentseal** | ~2026-06 | 4 subcommands: `guard`/`scan`/`scan-mcp`/`shield` | 225 probes（82 extraction + 143 injection + 8 mutation）；MiniLM-L6-v2 语义 embedding | **红队 + 扫描双料**：能主动测 prompt 抵抗性；实时 shield 监控 agent 配置；6,600+ MCP 服务器信誉库 |
| **HeadyZhang/agent-audit** | ~2026-06 | 51→120+ rules，GT v2.2 | OWASP Agentic Top 10 全覆盖；LangChain/CrewAI/AutoGen/AgentScope 多框架；OpenClaw skill | **多框架覆盖** + baseline 增量扫描；框架-specific 检测 |
| **affaan-m/agentshield** | ~2026 早期 | 名字撞车（同名 SaaS 风险） | Claude Opus multi-agent 深度分析；policy packs（enterprise/regulated/ci-enforcement）；runtime monitor PreToolUse hook | **企业策略包** + runtime hook + Opus 分析——**企业级**路线 |

**共性**：全都是 2026 年新出现，都覆盖 OWASP Agentic Top 10，都有 SARIF/CI 门禁。AIShield 不再是唯一"覆盖 MCP+ASI01-10"的项目。

---

## 二、AIShield 的差异化优势（仍然在，但被稀释）

| 优势 | 竞品现状 | AIShield 状态 |
|---|---|---|
| **Local-first / no-spawn** | SkillSpector 需要 Docker / venv；agentseal 有实时 MCP 连接 | ✅ 优势仍显著——静态审计 + 14 client surfaces 自动发现 |
| **零依赖 offline** | 4 家都要 Docker 或 venv 或 cloud API key | ✅ 唯一零运行时依赖（urllib only） |
| **235 rules / 241 skill rules** | SkillSpector 68 / agent-audit 120+ / agentshield 无公开数 | ✅ 数量领先 |
| **Trust Standard + Certification L1-L3** | 无一家做中立认证 | ✅ 唯一做中性信任层的 |
| **aishield-trust/v1 内嵌规格** | 无对标 | ✅ 唯一可嵌 MCP Server Card / A2A Agent Card |
| **OWASP MCP Top 10 官方对齐** | 全都在做 | ⚠️ 不再有独占优势 |

---

## 三、Agent Memory 品类爆发（2026-06 至 2026-09）

**4 个新出现的 memory 层项目**：

| 项目 | 定位 | 规模 | 与 AIShield 的关系 |
|---|---|---|---|
| **instinct** (WRG-11) | Confidence-based self-learning，MCP server | 2 stars，PyPI + MCP Registry | 小，可协同 |
| **Innate** (Rust) | recall→record→evolve 飞轮，记忆+技能+直觉三层 | 2026 新，agents-report 报道 | 同类，可协同 |
| **Hermes Agent** (Nous Research) | Self-evolving agent，persistent memory + auto skill | **47,000 stars**，2026-02 首发，MIT，支持 MCP | **重量级**——个人 Agent OS 层 |
| **Hindsight** (sulhicmz/vectorize-io) | 仿生记忆：world/experiences/opinion/observation，LongMemEval SOTA | 学术界合作（Virginia Tech、Washington Post） | 记忆架构标杆 |

**加 self-learning-skills**：2026-06-28 上 trending，几天 897 stars，元技能+三条件晋升规则。

**结论**：memory 层是**新的攻击面**——这些项目存的"经验"、"技能"、"直觉"如果被投毒，agent 会**基于错误经验做后续决策**。AIShield 现在的 `memory_integrity_scan.py` 只覆盖 `ASI04`（memory poisoning）的通用规则，没有针对具体 memory 系统的深度扫描。

---

## 四、AIShield 面临的战略抉择

**当前定位**（llms.txt 里写的）：Agent 生态的 content-trust 平面 + 中立信任层。
**风险**：4 家直接竞品都在做"agent security scanner"，AIShield 会被当成其中一个替代品，而不是不可替代的层。

**3 条候选路径**：

### 路径 A：横向扩规则，把数量做到 500+（防守）
- 跟进 agent-audit 的多框架检测（LangChain/CrewAI/AutoGen/AgentScope）
- 跟进 SkillSpector 的 YARA 签名 + taint tracking
- 跟进 agentseal 的红队 prompt injection 测试
- **成本**：中；**风险**：陷入规则数量竞赛，NVIDIA 有工程师资源，打不赢

### 路径 B：纵向做 agent memory 安全扫描（进攻）
- 新建 `scanner/memory_scanner_v2.py` 模块
- 深度扫描 instinct/Innate/Hermes/Hindsight 的记忆库（不只是通用 ASI04）
- 检测：经验投毒、技能覆盖、置信度伪造、直觉偏移
- **成本**：中；**风险**：需先与 memory 项目建生态关系，否则无数据来源

### 路径 C：中立信任层深耕（差异化）
- 让 4 家竞品（SkillSpector/agentseal/agent-audit/agentshield）都能引用 `aishield-trust/v1` 作为他们的 badge
- AIShield 定位为**元层**（meta layer）——所有 scanner 的公共信任凭证层
- 类似 CA 在 TLS 生态里的位置
- **成本**：低（写 spec + 联系 4 家团队）；**风险**：需要竞品接受，短期难

---

## 五、具体新提升方向（5 项候选，等用户拍板）

按 ROI 从低到高：

### 1. **规则晋升 confidence-based**（借鉴 instinct/self-learning-skills）
- 现状：`scanner/_proposed/` 纯人工审阅，17 条 outstanding authoring work 堆积
- 改动：同一攻击模式在语料里出现 N 次自动进 draft，5→mature / 10→rule
- 文件：新建 `scanner/rule_promotion.py`
- 成本：中；ROI：**高**（解堆积）

### 2. **规则 decay 机制**（借鉴 instinct）
- 现状：235 条规则只增不减
- 改动：90 天未在 benchmark 命中 → 置信度 -1 → 归零删除
- 文件：新增到 `scripts/rule_count_gate.py` 或独立 `scripts/rule_decay.py`
- 成本：低；ROI：**中**（防膨胀）

### 3. **Agent Memory 深度扫描模块**（进攻 agent memory 品类）
- 新建 `scanner/memory_scanner_v2.py`
- 支持扫描 instinct `.db`、Innate 目录、Hermes sessions、Hindsight banks
- 检测 memory poisoning 深度模式：经验投毒、技能覆盖、置信度伪造
- 成本：中；ROI：**高**（新品类空白）

### 4. **AI Agent 策略包预设**（借鉴 agentshield policy packs）
- 新建 `distribution/policies/{enterprise,regulated,ci-enforcement,oss,high-risk-hooks-mcp}.json`
- 每个策略包包含预配置的规则集 + 分数阈值 + runtime hook 建议
- 成本：低；ROI：**中**（企业级差异化）

### 5. **Red-team prompt injection 主动测试**（借鉴 agentseal scan）
- 新建 `scanner/redteam.py`
- 225 probes（或缩小到 50 关键探针），可测系统提示的抗注入能力
- 需要 LLM API 或本地 Ollama；AIShield 用户已有 Ollama 生态
- 成本：高；ROI：**中**（agentseal 已有先发）

---

## 六、优先级建议

**推荐组合：3 + 1 + 4**
- **3（Agent Memory 深度扫描）** = 进攻新品类，跟 memory 层 4 个新项目建立生态关系
- **1（规则晋升 confidence）** = 内部效率，直接解决堆积问题
- **4（策略包预设）** = 企业差异化，接 agentshield 的路线

**暂不做的**：
- 2（decay）—— 等规则超过 300 条再考虑
- 5（红队测试）—— agentseal 已有先发，追不上

**长期战略层**：走**路径 C**（中立信任层深耕），让 4 家竞品都引用 AIShield badge。但这是市场动作，非代码改动。

---

## 七、一句话总结

**AIShield 从"唯一"变成"之一"是既定事实**。要么横向规模战（打不赢 NVIDIA），要么纵向新品类（agent memory 是空白），要么横向变纵向——做所有 scanner 的元信任层。**推荐：agent memory 扫描模块 + 内部效率 + 策略包**，长期做元信任层。

---

*本报告为战略层文档，代码改动需用户单独拍板。所有 star 数、版本号、日期以 2026-09-29 WebSearch 结果为准。*
