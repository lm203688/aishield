# AIShield · Agent 生态分层补全路线图（开源市场扫描 + 自研）

> 状态：Phase 0（规划 + 开源清单），本轮回**不写扫描器代码**，仅产出路线图与开源参照。
> 数据源：2026-10-08 开源市场扫描（MCP 注册表格局、OWASP/ATLAS/MAESTRO 框架、agent 安全平台）
> 红线（来自 AGENTS.md）：零第三方依赖（标准库 only，测试用 `unittest`）；绝不 spawn 被扫配置里的命令；改写对外声明面前必须验证再推送；门禁不可绕过。

---

## 0. 目标与边界

- 把 AIShield 从「MCP / skill / prompt 扫描器」升级为覆盖 **agent 全栈各生态位**的支撑基础设施：每一层都能扫描/检测 + 提供支撑能力。
- 方法论：**① 开源市场扫描**（不重造轮子，优先集成/对齐已有开源与标准）；**② 自研**（填补开源空白层）。
- 框架锚点：OWASP LLM Top 10 + OWASP **Agentic AI Top 10（ASI01–ASI10，2025-12-09 发布）** + MITRE **ATLAS** + CSA **MAESTRO（7 层 L1–L7）**。

---

## 1. 分层覆盖地图（12 层）

| # | 生态层 | OWASP 映射 | 开源市场现状（2026-10 扫描） | AIShield 当前 | 差距 / 待补 |
|---|---|---|---|---|---|
| 1 | 模型 / 提示注入 | LLM01 | — | prompt scan 部分 | 不直接扫模型/训练数据 |
| 2 | 工具 / 函数 (MCP) | MCP Top 10 | Glama ≈94.6k / Smithery(被 Arcade.dev 收购) ≈24k / Official Registry ≈2k / PulseMCP ≈12k(暂停收录) / mcp.so ≈20k | **MCP 扫描 ✓ 核心** | 已较全 |
| 3 | 技能 (Skills) | LLM03 衍生 | Claude Skills / WorkBuddy skills / Glama skills | skill scan ✓ | 已覆盖 |
| 4 | 提示词 / GPTs | LLM01 | GPT Store | prompt + GPTs scan ✓ | 已覆盖 |
| 5 | 智能体编排 / A2A | **ASI07** | Google A2A 协议、agent card 兴起 | agent-card + agent-infra API 部分 | **缺 A2A 协议扫描、多智能体计划扫描** |
| 6 | 记忆 / RAG | **ASI06** | Lakera / NeuralTrust 偏运行时护栏 | 未扫记忆存储 | **缺记忆投毒 / 上下文污染检测（空白层）** |
| 7 | 身份 / 权限 | **ASI03** | — | L1/L3 ed25519 身份 ✓ `identity_ready` | 已覆盖 |
| 8 | 供应链 / AIBOM | **ASI04 / LLM03** | Cisco `mcp-scanner` / Snyk `agent-scan` / CycloneDX AIBOM | MCP provenance 部分 | **缺 AIBOM 生成、组件 SBOM** |
| 9 | 护栏 / 安全（自身） | 全 | — | scanner + 17 red-team probes + benchmark ✓ | 已覆盖 |
| 10 | 可观测 / 评测 | 横切 | `mcp-eval` / `mcpchecker`（CI 门禁） | red_team + benchmark ✓ | **缺运行时 guard 集成** |
| 11 | 分发 / 市场 | — | B1–B8 七+ 渠道 | ecosystem API + connectors + 台账 ✓ | 分发本身待你登录发布（#188 等） |
| 12 | 代码执行 / 沙箱 | **ASI05** | E2B / Modal / Docker / nsjail / gVisor | 未覆盖 | **缺沙箱边界 / 逃逸扫描** |

**待补 5 处缺口**：#5 A2A、#6 记忆/RAG、#8 AIBOM、#10 运行时 guard（横切）、#12 代码执行沙箱。

---

## 2. 五个缺口详述（自研范围 + 可集成开源）

### Gap 5 — 智能体编排 / A2A（ASI07 跨智能体通信）
- **开源现状**：Google **A2A（Agent2Agent）协议**、agent card（`/.well-known/agent.json` 信任声明）、agent-to-agent message。AIShield 已有 agent-card 解析 + `agent-infra` API。
- **自研范围**：扫描 agent card 的信任声明（身份锚点、能力声明、delegation 链）；检测 ASI07 spoofing / replay / unauthenticated；多智能体 **plan 静态扫描**（goal-hijack 链式）。
- **可集成**：A2A 规范（repo 待核实：`github.com/google/A2A`）、agent card schema。
- **验收**：新增 `scanner/a2a_scan.py` + 规则若干；`/api/v1/agent-infra/*` 扩展。

### Gap 6 — 记忆 / RAG（ASI06 记忆与上下文投毒）★ 推荐 Phase 1
- **现状澄清（2026-10-08）**：本仓库**代码级** ASI06 已由 `scanner/agent_memory_scan.py`（#343）覆盖（8 框架、跨 session 累积、检索注入、持久化指令）。**真正空白的是内容级**——RAG 语料 / 持久化记忆**正文**里的投毒（间接注入残留、角色劫持、外传诱导），此前无人扫。
- **自研范围（本次落地）**：`scanner/rag_corpus_poison_scan.py` 对 {filepath: content} 做内容级扫描，六类：嵌入指令 / 角色劫持 / 外传诱导 / 紧急伪装 / 跨文档互证 / 编码载荷。已接入 `workspace_scan._local_pipeline`（与 agent_memory_scan 同款），11 单测覆盖正/负样本与集成。
- **可集成**：RAG 检索内容 screening 思路（Lakera）；**自研为主**。
- **数据飞轮**：与 swarmlabs 科研实体库可形成闭环（投毒样本 → 规则晋升）。
- **验收**：✅ 见 Phase 1 行；`scanner/` 在 rule_count_gate 排除目录，不增声明位。

### Gap 8 — 供应链 / AIBOM（ASI04）
- **开源现状**：Cisco `mcp-scanner`、Snyk `agent-scan`（组件 vetting）；OWASP **CycloneDX AIBOM** 标准。
- **自研范围**：MCP server 组件溯源 + 生成 **AIBOM / SBOM**（依赖、来源、签名）；对接 `ecosystem_support_api`。
- **可集成**：CycloneDX AIBOM schema；mcp-scanner 思路。
- **验收**：新增 `scanner/supply_chain.py` + AIBOM 生成器；`verify` 门禁扩展。

### Gap 10 — 可观测 / 评测（横切，运行时 guard 集成）
- **开源现状**：`mcp-eval`、`mcpchecker`（CI 门禁：schema validation、description quality、cross-client compat、behavioral test、security scan）。
- **自研范围**：把现有 17 red-team probes + benchmark 包装成可被 agent 平台**运行时调用**的 guard API（参考 Lakera Guard API 形态）；持续监控 + kill switch。
- **验收**：`/api/v1/guard/*` 运行时端点；与 `red_team_probe` 打通。

### Gap 12 — 代码执行 / 沙箱（ASI05 意外代码执行）
- **开源现状**：E2B / Modal / Docker / nsjail / gVisor（沙箱运行时）；supergateway（stdio→SSE 传输）。
- **自研范围**：扫描 MCP server 中「执行代码 / Shell」类工具（危险 tool 声明检测）；沙箱边界/逃逸风险标记。
- **可集成**：沙箱运行时（部署侧，非扫描侧）。
- **验收**：新增 `scanner/code_exec_scan.py`（危险 tool 模式匹配 + allow/deny 建议）。

---

## 3. 构建顺序与里程碑

| Phase | 内容 | 说明 |
|---|---|---|
| **Phase 0** | 规划 + 开源清单（本文档） | ✅ 本轮回完成 |
| **Phase 1** | Gap 6 记忆/RAG（内容级） | ✅ 2026-10-08 完成：`scanner/rag_corpus_poison_scan.py` + 接入 `workspace_scan` 流水线 + 11 单测；全量 2085 测试绿 |
| **Phase 2** | Gap 5 A2A | 延伸已有 agent-card 基础 |
| **Phase 3** | Gap 8 供应链/AIBOM | 对接 CycloneDX 标准 |
| **Phase 4** | Gap 12 代码执行沙箱 | 危险 tool 检测 |
| 横切 | Gap 10 运行时 guard | 贯穿各 phase，封装 red-team/benchmark 为运行时 API |

每阶段交付：扫描器模块（`scanner/*`）+ 规则（入 `rule_count_gate` 声明位）+ API 端点（若需）+ 测试（`unittest`）+ 推送前跑 `verify_distribution` / `sync_version --check` / `rule_count_gate --check` + 线上复验。

---

## 4. 分发层（#11）待你配合发布清单

> 完整步骤见 `registry/publish-guide.md`。下列为阻塞在「需你登录」的条目，逐步指引已在前序消息 B1–B3 给出。

| 渠道 | 名称 | 状态 | 你的动作 |
|---|---|---|---|
| `agensi` | chinese-seo-compliance | ⚠️ 漂移（源 1.1.0 等覆盖发布） | 登录 agensi.io → 覆盖发布 → 版本 1.1.0 → 回写台账（B1） |
| `claude-skills` | aishield-security-scan | 未发布 | Claude 账号登录提交（A2） |
| `gpt-store` | aishield-gpt | 未发布 | ChatGPT Plus/Pro 建 GPT + Actions（A3） |
| `huggingface` | aishield-agent-security-benchmark | 未发布 | HF 登录建 dataset（A4） |
| `clawhub` | aishield | 未发布 | 较老 GitHub 账号认领命名空间（A5） |
| `glama` / `smithery` / `mcp.so` / `pulsemcp` / Official / npm / Docker / PyPI | aishield-mcp-server | 多未主动提交 | GitHub/npm/Docker/PyPI token 登录提交（B1–B8） |

**硬阻塞两项**（需你生成凭证后给我，我不 echo）：
- **Agensi 登录**（B1）—— #188。
- **GitHub PAT（`workflow` scope）**（B2）—— Tech Radar 闭环 dispatch 硬阻塞。

---

## 5. 开源参照汇总表

| 类别 | 项目 / 协议 | 用途 | 链接 / 状态 |
|---|---|---|---|
| MCP 注册表 | Glama | 最大目录、自动评级 A–F | https://glama.ai/mcp/servers |
| MCP 注册表 | Smithery（Arcade.dev） | 托管 + CLI 发布 | https://smithery.ai |
| MCP 注册表 | Official MCP Registry | 权威根、命名空间验证 | https://github.com/modelcontextprotocol/registry |
| MCP 注册表 | PulseMCP | 人工策展（暂停收录） | https://pulsemcp.com |
| MCP 注册表 | mcp.so | 按调用量排名 | https://mcp.so |
| 参考 server | modelcontextprotocol/servers | Anthropic 7 参考实现 | https://github.com/modelcontextprotocol/servers |
| 框架 | OWASP LLM Top 10 | 模型层风险 | owasp.org LLM Top 10 |
| 框架 | OWASP Agentic AI Top 10 | ASI01–ASI10 | owasp.org AI Security Project |
| 框架 | MITRE ATLAS | 攻击技术 taxonomy | https://atlas.mitre.org |
| 框架 | CSA MAESTRO | 7 层架构加固 | CSA 发布 |
| 协议 | Google A2A | 跨智能体通信 | github.com/google/A2A（待核实） |
| 护栏 | Lakera | 运行时 guard / 框架映射 | https://www.lakera.ai |
| 护栏 | NeuralTrust | 运行时护栏 + ASI 解析 | https://neuraltrust.ai |
| 供应链 | Cisco mcp-scanner | MCP server 安全扫描 | 链接待核实 |
| 供应链 | Snyk agent-scan | agent 组件 vetting | https://snyk.io |
| 标准 | CycloneDX AIBOM | AI BOM 生成标准 | https://cyclonedx.org/capabilities/ai-bom/ |
| 评测 | mcp-eval / mcpchecker | CI 门禁 | GitHub（链接待核实） |
| 沙箱 | E2B / Modal / Docker / nsjail / gVisor | 代码执行隔离 | 部署侧集成 |

> 注：标注「待核实」的链接来自市场扫描的间接引用，落地对应 phase 时请先 `WebFetch` 确认确切地址后再写入文档/代码注释。

---

## 6. 约束与门禁（每阶段必跑）

- **零依赖**：扫描器只用标准库；测试 `unittest`（禁 `pytest`，否则 `validate_workflows` E12 红）。
- **隔离不变量**：绝不 `exec`/`subprocess` 被扫配置中的指令（`scripts/prove_isolation.py` 自证）。
- **版本/规则门禁**：`scripts/sync_version.py --check`（47 版本位）、`scripts/rule_count_gate.py --check`（55 声明位）、`scripts/verify_distribution.py`（分发台账）。
- **推送**：统一走 `scripts/_push_batch.py` / `git_push_safe.sh`，推送前取 `declared_surface_changed()`，非空则 `--check` 拦截（E14）。
- **workflow 改动**：改 `.github/workflows/` 后跑 `scripts/gen_task_registry.py --check`；PAT 需 `Workflows:write`（当前缺失，见 §4）。
