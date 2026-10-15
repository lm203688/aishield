# AIShield — Meta Muse Connector 提交包

**提交平台**：https://muse.ai/platform (Submit a connector 表单)
**提交日期**：2026-09-24
**目标**：让 Muse agent 在执行敏感操作前调用 AIShield 做身份核验 + 预算守护 + 行动溯源。

## 一句话产品描述

> **AIShield for Muse**：给 Meta Muse 个人 Agent 加装独立的安全治理层——
> 在 Muse 执行支付 / 邮件 / 表单 / 授权等敏感操作之前，让用户拿到一份可验证的
> 「授权凭证 + 预算回执 + 行动溯源链」，Meta 官方审核之外的第二意见。

## 为什么 Muse 需要 AIShield

Meta 官方 Muse 已经内置：
- Secure VM 隔离 + Sentinel 监督 agent
- Stripe Link 支付（一次性卡号，无凭据接触）
- 敏感操作二次确认
- 独立 audit trail

**但缺失的（AIShield 补齐）**：

| Gap | Stripe Link / Meta Sentinel 覆盖？ | AIShield 补齐 |
|---|---|---|
| 跨平台可验证的个人 Agent 身份（"这个 Muse 是 Alice 的"） | ❌（Meta 账号体系封闭） | ✅ PAI DID (`did:key`) |
| 累计预算 + 周 / 月上限 | ❌（Stripe Link 只管单次卡号） | ✅ 个人预算守护（4 粒度） |
| 目标站风险评分 + quote-first 决策 | ⚠️（Stripe 有 3D Secure，但不做决策层） | ✅ 8 因素风险评分 + allow/confirm/block/denied |
| Connector 独立第二意见 | ❌（Meta 自审） | ✅ 8 维度独立评估 |
| 用户级 dispute 回执（"我的 agent 擅自订了酒店？"） | ❌（Meta 内部日志） | ✅ HMAC 链 + 离线可验证 |

**定位与 Muse 的关系**：
- **不替代** Stripe Link（支付通道）
- **不替代** Sentinel（授权监督）
- **补齐** 治理层：身份、预算决策、独立审核、消费级证据

## 提交表单内容（muse.ai/platform）

### Step 1: Describe your product

**产品名称**：AIShield — Personal Agent Governance for Muse

**一句话**：给 Muse agent 加装独立的个人身份 + 预算守护 + 行动溯源层。

**详细描述**（复制到表单）：

> AIShield is an open-source personal agent governance kernel (MIT, github.com/lm203688/aishield). It plugs into Muse before the agent executes sensitive actions — payment, email, form-fill, connector install — and gives the user three things Meta's stack does not provide:
>
> 1. **A portable personal identity** (PAI DID, `did:key`) that works across Muse, ChatGPT-Agent, Claude-Agent, and any self-built agent. Users own it; no platform can revoke it unilaterally.
> 2. **Personal budget governance with cumulative weekly and monthly limits** — beyond what Stripe Link's per-transaction card number can express. Includes 8-factor risk scoring (target-site reputation, amount vs. personal history P90, off-hours, currency shift, first-seen target, high-risk action type, quote-first gap) and a four-tier verdict: allow / confirm / block / denied.
> 3. **Immutable action provenance** — every sensitive action Muse performs is appended to an HMAC-SHA256 chained ledger, verifiable offline for 90 days. Users can file disputes against any action with cryptographic receipts.
>
> Additionally, AIShield provides **independent second-opinion connector vetting** — for the connectors Meta already reviews, users can request a neutral assessment outside Meta's stack.

### Step 2: Submit for review

**功能端点**（Muse agent 通过 HTTPS 调用）：

```
GET  https://aishield.tools/api/v1/personal-agents/stats
POST https://aishield.tools/api/v1/personal-agents/users
GET  https://aishield.tools/api/v1/personal-agents/users/{user_id}
POST https://aishield.tools/api/v1/personal-agents/users/{user_id}/agent-instances
POST https://aishield.tools/api/v1/personal-agents/users/{user_id}/tickets
POST https://aishield.tools/api/v1/personal-agents/budget/check
POST https://aishield.tools/api/v1/personal-agents/budget/reserve
POST https://aishield.tools/api/v1/personal-agents/budget/commit
POST https://aishield.tools/api/v1/personal-agents/budget/release
POST https://aishield.tools/api/v1/personal-agents/users/{user_id}/actions
GET  https://aishield.tools/api/v1/personal-agents/users/{user_id}/actions/{seq}
GET  https://aishield.tools/api/v1/personal-agents/users/{user_id}/actions/verify
POST https://aishield.tools/api/v1/personal-agents/users/{user_id}/disputes
POST https://aishield.tools/api/v1/personal-agents/users/{user_id}/connectors/vet
POST https://aishield.tools/api/v1/personal-agents/tickets/verify
POST https://aishield.tools/api/v1/personal-agents/tickets/consume
```

**认证**：`Authorization: Bearer <AISHIELD_API_KEY>`（用户自注册获取；无强绑定 Meta 账号）

**OpenAPI 3.1**：见附件 `openapi.yaml`

**MCP 备选**：本 connector 同时作为 MCP 工具发布（8 个 `aishield_personal_*` 工具，npm `aishield-mcp-server` v4.8.1）—— 未来 Meta 若支持 MCP，零迁移接入。

### Step 3: Security & compliance statement

**功能要求**：
- 只读/写 API；不主动扫描用户邮箱、日历、支付账户
- 所有数据存储在服务端 `api/data/personal_agents.json`（本地 JSON，无第三方 SaaS）
- 用户随时可 export / delete；提供 `POST /api/v1/personal-agents/users/{uid}/reset` 全量删除端点（生产环境）
- HMAC-SHA256 链保证行动记录不可篡改；用户可离线验证

**安全要求**：
- OWASP MCP Top 10 + Agentic AI Top 10 对齐（235+262 规则）
- 所有 API 参数校验 + fail-closed（预算超限直接 denied，不是"放行"）
- 签名走 Ed25519 优先 / HMAC-SHA256 降级（零依赖）
- MIT 开源，任何人可审计

**法务要求**：
- MIT License
- 数据存储位置：`aishield.tools`（Cloudflare Workers，见隐私政策）
- 不收集 PII 用于训练任何模型
- GDPR 合规：用户可通过 API 请求导出 / 删除其个人 DID 及关联全部数据
- 支付：AIShield 不处理支付，仅做 pre-flight 决策；实际支付仍走 Stripe Link

## 隐私政策摘要

**收集**：user_id（用户提供）、display_name、email（可选）、Agent 实例元数据、预算策略、行动记录 payload（用户主动提交）
**用途**：仅用于用户自己的治理查询（预算查询、行动溯源、dispute 回执）
**存储**：JSON 文件，90 天 TTL，用户可 export / delete
**共享**：不向任何第三方共享（包括 Meta、Stripe）
**删除**：`POST /api/v1/personal-agents/users/{uid}/reset` 立即删除全部数据

## 提交步骤

1. 访问 https://muse.ai/platform
2. 点击 "Submit a connector"
3. 用上面的内容填写各字段
4. 上传 `openapi.yaml` 作为 API 规格附件
5. 附加仓库链接 `github.com/lm203688/aishield`（MIT 开源，代码可审计）
6. 提交后等待 Meta 审核（功能、安全、法务、端到端测试）

## 若 Meta 拒绝或不通过

**降级方案 A：MCP 通道**
- 发布 `aishield-mcp-server@4.8.1` 到 npm（已就绪）
- Muse 一旦支持 MCP 即零迁移接入（Meta 尚未宣布 MCP 支持，但生态必然跟进）

**降级方案 B：Web Bot Auth 侧边车**
- 用 `eco/kyad_compat.py` 的 Web Bot Auth 头（GoDaddy+Cloudflare 2026-04 标准）
- 让 Muse agent 在发起敏感操作前请求一个短期 bot token
- AIShield 提供 token 验证服务

**降级方案 C：自建 Gateway**
- 类似 ATEX / OpenRouter 的 agent 转发层
- 任何 agent 通过 AIShield Gateway 才能访问外部服务
- 用户主动切换代理，AIShield 做全流量治理

## 联系人

- Repo：https://github.com/lm203688/aishield
- npm：https://www.npmjs.com/package/aishield-mcp-server
- 邮件：security@aishield.tools
- 官网：https://aishield.tools
