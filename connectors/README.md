# AIShield 个人 Agent 平台接入层（v4.8.3）

**核心结论**：任何个人 Agent 平台的用户，都可以通过 AIShield 加装独立的
个人身份（PAI DID）、预算守护、行动溯源、Connector 独立审核层。
平台不需要官方上架，MCP / OpenAI 兼容 API 即可零迁移接入。

## 大陆访问状态（2026-09-24 一手核实）

| 状态 | 数量 | 平台 |
|---|---|---|
| **verified_blocked** | 7 | Meta Muse、Grok Bot、Grok API、ChatGPT Agent、OpenAI Operator、Claude、Gemini |
| **reachable** | 20 | Coze、豆包、元宝、文心、通义、Kimi、DeepSeek、GLM、Yi、Minimax 等 |
| **regional_only** | 5 | Vertex / Groq / Cerebras / Fireworks / Together（海外云） |

**关键洞察**：海外头部消费级 agent（Muse / Grok Bot / ChatGPT Agent /
OpenAI Operator）大陆全部不通。AIShield 的定位不是"上架某平台"，而是
**"跨平台中立治理层"** —— 平台只是接入方之一。

## 接入路径分层（5 类）

| 路径 | 隔离度 | 平台需要改动 | AIShield 状态 | 典型场景 |
|---|---|---|---|---|
| **mcp** | 高 | 否 | ready | 平台支持 MCP 即可（Coze / Dify / n8n / ChatGPT MCP） |
| **openai_compat** | 中 | 是 | ready | 平台提供 OpenAI 兼容 API，AIShield 作为上游 guardrail 或工具路由 |
| **browser_agent** | 高 | 否 | ready | Grok Bot / OpenAI Operator 通过浏览器层调用 AIShield 工具 |
| **connector_official** | 低 | 是 | requires_submission | 平台官方 connector 平台（Muse / ChatGPT / Coze / 元宝） |
| **native_sdk** | 低 | 是 | requires_adaptor | 平台私有 SDK（豆包 / 元宝 / 可灵） |

**优先级建议**：MCP > browser_agent > openai_compat > connector_official > native_sdk

理由：MCP 与浏览器代操不需要平台配合，AIShield 侧就能开工；
connector 官方通道依赖平台审核节奏，是**兜底方案**不是主路径。

## 已建接入包（海外个人 Agent + 开发者平台，全部真实实现）

| 平台 | 接入包 | 大陆可达 | 主接入路径 | 集成形态 | 鉴权 |
|---|---|---|---|---|---|
| **Meta Muse** | [`connectors/muse/`](./muse/) | ❌ | connector_official / MCP | 开发者身份 + MCP 桥 | OAuth 2.0 |
| **Grok Bot (xAI)** | [`connectors/grok_bot/`](./grok_bot/) | ❌ | openai_compat / browser_agent / MCP | 开发者身份 + MCP 桥 | OAuth 2.0 + PAT |
| **NVIDIA Developer Platform** | [`connectors/nvidia/`](./nvidia/) | ⚠️ 需代理 | native_sdk / connector_official / MCP | NGC Catalog + NIM 推理 + NeMo 编排 | NGC API Key |

> 注：Coze 等**国内**平台按需求**不建接入包**，仅保留注册表参考条目。

三个接入包共用一套骨架（`connectors/base.py` + `connectors/dispatcher.py`）：
OAuth/PAT 换取 → token 存储与刷新 → 登记为 PAI 实例 → **preflight 治理前置**
（预算 + 8 因素风险 + 敏感词升级 → 4-tier verdict）→ 真实 API 调用 → HMAC 行动链。

## 双形态对接（同一平台的两条路径）

同一平台可以**同时**走两条形态，治理层是共用的，身份（PAI DID）也是共用的：

### 形态 ①：开发者身份（OAuth / PAT / API Key）

平台官方开发者身份，AIShield 持有密钥、代理所有敏感动作。

```bash
# Meta Muse：OAuth 全流程
curl -X POST https://api.aishield.tools/api/v1/connectors/meta-muse/oauth/authorize \
  -H "Content-Type: application/json" \
  -d '{"client_id":"your_muse_client_id","redirect_uri":"https://…","scopes":["agent:chat"]}'
# → 返回 authorize_url，用户浏览器打开授权，回调拿 code
curl -X POST https://api.aishield.tools/api/v1/connectors/meta-muse/oauth/token \
  -H "Content-Type: application/json" \
  -d '{"code":"<回调code>","client_id":"your_muse_client_id"}'

# Grok Bot：PAT 直连（官方推荐）
curl -X POST https://api.aishield.tools/api/v1/connectors/xai-grok-bot/agents/register \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u_alice","agent_name":"Alice 的 Grok","platform_agent_id":"grok_bot_x",
       "auth":"pat","credentials":{"pat":"xai…e"} }'

# NVIDIA：NGC API Key
curl -X POST https://api.aishield.tools/api/v1/connectors/nvidia-dev/agents/register \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u_alice","agent_name":"Alice 的 NIM","agent_instance_id":"agent_nv_1",
       "api_key":"NAPI_key…"}'

# 三平台通用的受治理动作执行（denied 硬拒 / block 需 override / allow 放行）
curl -X POST https://api.aishield.tools/api/v1/connectors/xai-grok-bot/actions/run \
  -H "Content-Type: application/json" \
  -d '{"agent_instance_id":"grok_inst_1","user_id":"u_alice","prompt":"帮我总结","action":"chat"}'
```

### 形态 ②：MCP 桥（零迁移）

AIShield 的 MCP server 本身就是桥——任何支持 MCP 的宿主（Claude Desktop /
Cursor / 自建 agent）装上 `aishield-mcp-server` 即获得全部治理能力，
**不需要平台侧任何改动**。海外平台只需用户在宿主里配置 `HTTPS_PROXY`。

```bash
npx aishield-mcp-server
```

MCP 工具（v4.8.3 共 66 个）：

| 工具 | 用途 |
|---|---|
| `aishield_connector_catalog` | 列出已实现接入的平台 |
| `aishield_connector_self_check` | 诊断可达性 / 密钥 / proxy 状态 |
| `aishield_connector_authorize` | 生成 OAuth 授权 URL |
| `aishield_connector_exchange_code` | 授权码换 token |
| `aishield_connector_register_agent` | 登记 PAI 实例（含 nvidia-dev 的 api_key） |
| `aishield_connector_run` | 受治理执行动作（MCP 形态 = 开发者身份形态同一入口） |
| `aishield_agent_infra_targets` | 列出 agent 基础设施 / 开发者平台扫描靶 |
| `aishield_agent_infra_scan` | 扫描 → 封装骨架 → 二次研发清单 |

大陆用户提示：`self_check` 返回的 `proxy` 字段会报告当前
`HTTPS_PROXY` 配置状态；无代理时可达性为 false，但治理层（预算 / 风险 /
行动链）仍可本地运行，等平台可达时直接复用已登记的实例。

## Agent 基础设施开源生态（封装 + 二次研发）

围绕核心目标，把 **agent 基础设施类开源项目** 纳入生态，通过「开源扫描 →
封装（MCP 适配器）→ 二次研发」多维度多层级构建：

| 目标 | 类别 | 大陆可达 | 接入路径 | 定位 |
|---|---|---|---|---|
| **NVIDIA Developer Platform**（NGC / NIM / NeMo / AI Blueprint） | developer 算力底座 | ⚠️ regional（需代理） | native_sdk / connector_official / MCP | 推理与编排 API 封装、NIM 微服务当工具暴露 |
| **Laya**（本地决策/护栏模型，已 MCP 接入） | infrastructure | ✅ | MCP（已接） | 本地零成本初筛层 |
| **Nasiko**（agent 基础设施） | infrastructure | ✅ | MCP / 封装 | 开源扫描目标，封装适配 |
| **Agent Desktop**（桌面 agent 基础设施） | infrastructure | ✅ | MCP / native_sdk | 开源扫描目标，封装适配 |

- 接入底座见 [`eco/platform_registry.py`](../eco/platform_registry.py)（family=infrastructure / developer）。
- 查询：`GET /api/v1/platforms?family=infrastructure` 或 `python eco/platform_registry.py`。
- 英伟达开发者平台 + 海外个人 Agent（Muse / Grok Bot）通过 **MCP** 或
  **开发者身份** 双形态接入，构成 AIShield 的「国外个人 Agent + agent 基础设施
  开源生态」双轮。

### Agent 基础设施开源扫描管道（`connectors/agent_infra/`）

三层构建：**开源扫描 → 封装（MCP 适配器骨架）→ 二次研发清单**。

```bash
# 列出扫描靶（family=infrastructure | developer，共 23 个）
curl https://api.aishield.tools/api/v1/agent-infra/targets

# 在线扫描（走 api.github.com）
curl -X POST https://api.aishield.tools/api/v1/agent-infra/scan \
  -H "Content-Type: application/json" \
  -d '{"name":"laya","repo_url":"https://github.com/…/laya","platform_id":"laya","tool_type":"mcp"}'

# 离线扫描（内存文件，完全零依赖、确定性）
curl -X POST https://api.aishield.tools/api/v1/agent-infra/scan \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","files":{"config.py":"API_KEY=***"}}'

# 批量扫描 + 组合评分
curl -X POST https://api.aishield.tools/api/v1/agent-infra/scan-portfolio \
  -H "Content-Type: application/json" \
  -d '{"specs":[{"name":"a","files":{…}},{"name":"b","files":{…}}]}'
```

返回三层交付物：
- `report` — 复用 AIShield scanner（findings / 综合评分 / 建议）
- `mcp_adapter_skeleton` — 自动生成 Python MCP 适配器骨架，含治理 preflight 接入点
- `secondary_rd_checklist` — 按风险类别派生的二次研发工作项

代码：[`connectors/agent_infra/scan_pipeline.py`](./agent_infra/scan_pipeline.py)
测试：[`tests/test_agent_infra_scan.py`](../tests/test_agent_infra_scan.py)

其他 30+ 平台见 [`eco/platform_registry.py`](../eco/platform_registry.py)，
`docs/personal-agent-platform-matrix.md` 有完整矩阵。

## 定位

与 **CyberGuard**（GOAI 2026 Agent Infra 季军）正交互补：
- CyberGuard：SOC 应用层，管企业 SOC 事件
- AIShield 个人治理层：管**个人 Agent 用户**的身份、预算、行动
- 二者可在同一平台（如 Muse）形成"上层应用 + 底层身份"栈

## 治理缺口覆盖

| 平台治理缺口 | AIShield 补齐 |
|---|---|
| `portable_personal_identity` | PAI DID (`did:key`)，跨平台可验证 |
| `cumulative_budget_governance` | 4 粒度预算守护（per_tx / daily / weekly / monthly） |
| `target_site_risk_scoring` | 8 因素风险评分 |
| `connector_independent_review` | 8 规则独立审核 |
| `user_level_dispute_receipt` | HMAC-SHA256 行动链 + 用户 dispute 回执 |
| `cross_platform_budget` | 单点治理，任意平台实例都记账 |
| `agent_level_governance` | Capability Ticket（用户对实例的白名单 + TTL） |
| `off_platform_audit_trail` | HMAC 链跨平台可验证，不依赖平台内部日志 |

## 快速验证

```bash
# 平台注册表统计
python eco/platform_registry.py

# 获取大陆用户推荐接入平台
curl -X POST https://api.aishield.tools/api/v1/platforms/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_country": "CN", "capabilities_needed": ["portable_personal_identity"]}'

# 反查某实例的平台治理缺口
curl https://api.aishield.tools/api/v1/personal-agents/users/alice@example.com/agent-instances/inst_xxx
```
