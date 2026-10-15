# AIShield for Grok Bot 接入包（v4.8.1）

**平台**：xAI Grok Bot
**产品上线**：2026-08-11（SuperGrok Heavy 起）
**X connector 上线**：2026-08-29
**企业版上线**：2026-09-03

## 大陆访问状态

- `api.x.ai` — **连接超时**（2026-09-24 curl 实测）
- `x.com` — **连接超时**
- `docs.x.ai` — 需要海外网络

**结论**：大陆用户不能直接使用 Grok Bot；本包主要供：
1. **海外用户**（能访问 xAI）—— 加装个人 Agent 治理层
2. **企业版**通过 xAI 云 API 在海外部署 —— 治理层可放任意可访问的
   边缘节点
3. **MCP 备用** —— Grok Bot 支持 MCP 后零迁移接入

## 为什么 Grok Bot 需要 AIShield

xAI 官方 Grok Bot 已经内置：
- Cloud computer 隔离（每 agent 独立环境）
- Persistent state（跨会话保留）
- Approval before action（敏感操作二次确认）
- Enterprise audit controls（企业管理员、网络、审计）

**但缺失（AIShield 补齐）**：

| Gap | xAI 覆盖？ | AIShield 补齐 |
|---|---|---|
| 可携带的个人 Agent 身份（跨平台） | ❌（xAI 账号体系） | ✅ PAI DID `did:key` |
| 个人累计预算守护 | ⚠️（订阅制，但 agent 内消费无边界） | ✅ 4 粒度 + 8 因素风险评分 |
| 用户级行动 dispute 回执 | ❌（xAI 内部日志） | ✅ HMAC 链 + 90 天离线可验证 |
| 跨平台审计链 | ❌（每平台各自） | ✅ 单点治理，任意平台实例都记账 |

## 接入路径（3 条，按优先级）

### 路径 A：MCP（推荐，零平台改动）

Grok Bot 支持通过浏览器/终端层调用任意 MCP 工具。AIShield 已提供
48+ MCP 工具。

```json
// 用户 Grok Bot 环境里注册 AIShield MCP server
{
  "mcpServers": {
    "aishield": {
      "command": "npx",
      "args": ["-y", "aishield-mcp-server"],
      "env": {
        "AISHIELD_API_BASE": "https://api.aishield.tools"
      }
    }
  }
}
```

**能力**：Grok Bot 在执行敏感操作（发邮件、下单、装 connector）前，
自动调用 `aishield_personal_budget_check` / `aishield_personal_ticket_create` /
`aishield_personal_action_record`。

### 路径 B：OpenAI 兼容 API（开发者模式）

xAI API 走 OpenAI 兼容协议。AIShield 可作为上游 guardrail 层：

```python
from openai import OpenAI
import requests

# 用户 Grok API 客户端
xai = OpenAI(
    api_key="xai-your-key-here",
    base_url="https://api.x.ai/v1",
)

# 每次调用前走 AIShield 治理检查
def guard(tool_call):
    r = requests.post(
        "https://api.aishield.tools/api/v1/personal-agents/budget/check",
        json={
            "user_id": "alice@x.com",
            "action": tool_call.name,
            "amount": tool_call.get("amount", 0),
            "currency": "USD",
            "target_url": tool_call.get("target"),
        },
    )
    verdict = r.json().get("verdict")
    if verdict == "denied":
        raise Exception("预算超限")
    if verdict == "block":
        raise Exception("高风险，需二次确认")
    return True  # 允许继续

# 敏感 tool call 前
if call_type in ("purchase", "send_email", "install_connector"):
    guard(tool_call)

response = xai.responses.create(
    model="grok-4.6",
    input=user_message,
    tools=[...],
)
```

### 路径 C：SuperGrok Custom Skills

Grok Bot 支持用户自建 "Custom Skills"（2026-05 上线）。AIShield
可作为 Custom Skill 的**前置守卫**：用户建的每个 Skill 里第一步
调用 `aishield_personal_did_create` / `aishield_personal_connector_vet`。

## AIShield 补齐的治理能力

### 1. 可携带个人身份
```
did:key:z6Mk...（由 user_id 确定性派生的自认证 DID）
```
跨 Grok Bot / Coze / ChatGPT Agent 都可识别，用户拥有，xAI 无法单方面吊销。

### 2. 个人预算守护（4 档 verdict）
- **allow** — 低风险，自动通过
- **confirm** — 中风险，quote-first（用户二次确认）
- **block** — 高风险，建议阻止（可覆盖）
- **denied** — 预算超限，不可覆盖

8 因素风险评分：`amount_over_p90 / target_high_risk / off_hours /
currency_shift / new_target / high_risk_action / quote_first_gap / amount_surge`

### 3. HMAC 行动链
每次 Grok Bot 执行敏感操作，追加一条记录到用户独立链：
```
[seq] HMAC-SHA256(prev_hash || action || payload || verdict)
```
90 天离线可验证，用户可发 dispute。

### 4. Connector 独立审核
用户为 Grok Bot 装第三方 Skill / connector 时，AIShield 做 8 规则审核
（比 xAI 审核更中立）。

## 部署路径

| 用户类型 | 部署方式 | 治理层位置 |
|---|---|---|
| 海外个人 SuperGrok 用户 | MCP client 直连 AIShield | AIShield SaaS 或自托管 |
| 海外开发者 | API 前置调用 | AIShield SaaS |
| 企业版 | 私有化部署 | 客户自有云 |
| 大陆用户（代理访问 xAI） | 同海外用户 | AIShield 大陆节点 |

## 快速验证

```bash
# 注册 Grok Bot 实例（标记 platform）
curl -X POST https://api.aishield.tools/api/v1/personal-agents/users/alice@x.com/agent-instances \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "Alice-GrokBot",
    "provider": "xAI",
    "platform": "xai-grok-bot",
    "platform_tier": "super_grok_heavy"
  }'

# 预算检查（Grok Bot 敏感操作前）
curl -X POST https://api.aishield.tools/api/v1/personal-agents/budget/check \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice@x.com",
    "action": "purchase",
    "amount": 150,
    "currency": "USD",
    "target_url": "https://checkout.example.com",
    "category": "groceries"
  }'

# 记录行动到 HMAC 链
curl -X POST https://api.aishield.tools/api/v1/personal-agents/users/alice@x.com/actions \
  -H "Content-Type: application/json" \
  -d '{
    "action": "purchase",
    "payload": {"amount": 150, "currency": "USD", "target_url": "https://checkout.example.com"},
    "verdict": "allow"
  }'
```

## 定位与竞争

- **不替代** xAI 内部治理（cloud isolation / approval）
- **补齐**：可携带身份 + 跨平台预算 + 用户级 dispute
- **与 CyberGuard 正交互补**：CyberGuard 做 SOC 应用，本层做个人治理

## 版本

- AIShield v4.8.1+
- 与 `eco/personal_agent.py` 完全对齐
- 参见 [`docs/personal-agent-platform-matrix.md`](../../docs/personal-agent-platform-matrix.md)
