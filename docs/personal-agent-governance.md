# 个人 Agent 治理层设计文档（Personal Agent Governance）

**版本**：v4.8.1
**日期**：2026-09-24
**触发事件**：Meta Muse 上线 13 天 250 万下载，2026-09-18 开放 Connector Platform（muse.ai/platform）

---

## 一、为什么现在做

### 市场拐点
2026-09-08 Meta 发布 Muse：
- 13 天 250 万下载，超越同期 ChatGPT / Claude / Grok 首发期表现
- 登顶美国 iOS 免费榜
- 上线 10 天开放 connector 开发者平台
- **首次实现"聊天→干活"规模化**（不再是 demo 而是消费级）

同期竞品跟进：ChatGPT-Agent、Claude-Agent、Gemini-Agent、Perplexity Assistant。

### 结构性缺口
**每个平台的个人 Agent 都是封闭体系**：
| 平台 | 身份 | 支付 | 治理 |
|---|---|---|---|
| Meta Muse | Meta 账号 | Stripe Link（一次性卡号） | Sentinel（内部监督） |
| ChatGPT-Agent | OpenAI 账号 | Stripe | 内部 |
| Claude-Agent | Anthropic 账号 | 无 | 内部 |
| 自建 Agent | 无 | 无 | 无 |

**结构性缺失的能力（无一家覆盖全）**：
1. 跨平台可验证的个人 Agent 身份
2. 累计预算守护（周 / 月粒度）+ 目标站风险评分
3. Connector 独立第二意见审核
4. 用户级 dispute 回执（可离线验证）

**结论**：这不是"某一家平台的插件"，而是"个人 Agent 生态的公共基础设施"。
AIShield 定位：**Personal Agent Governance Kernel**。

---

## 二、我们已有什么（v4.7.1 盘点）

**已有能力（企业/供应链向）**：
| 能力 | 文件 | 说明 |
|---|---|---|
| Signed Agent Card | `eco/agent_card.py` | Ed25519/HMAC，A2A v1.0 兼容 |
| KYA SD-JWT | `eco/kyad_compat.py` | 企业向 SD-JWT |
| ERC-8004 | `eco/kyad_compat.py` | 钱包 → Agent 身份 |
| Specialist Registry | `eco/specialist_registry.py` | 8 域专业注册（企业向） |
| Evidence Bundle | `eco/evidence_bundle.py` | SOC 向审计（OCSF/STIX/ATT&CK） |
| Ship Gate | `scripts/ship_gate.py` | 10 态发布门 |
| Spend Cap | `eco/spend_cap.py` | 支付层额度（reserve/commit） |
| Trust Score | `api/trust_api.py` / `eco/trust_protocol.py` | 扫描分+鉴证+信誉+责任链 4 维加权 |

**缺失（个人 Agent 场景必须补）**：
| Gap | 已有？ | 说明 |
|---|---|---|
| 消费级 KYA（个人 DID） | ❌ | KYA SD-JWT 是企业级 |
| 个人预算守护（周粒度 + 风险） | ⚠️ | `spend_cap.py` 有基础，无风险评分、无"周"粒度、无 quote-first |
| Connector 独立审核 | ⚠️ | 有 MCP manifest 扫描，无独立第二意见定位 |
| 用户级 dispute | ❌ | Evidence Bundle 是 SOC 向 |

---

## 三、本模块做什么

### 4 大能力（新增）

**1. PAI 身份（Personal Agent Identity）**
- 每个自然人一个 DID（`did:aishield:pa:<hash>`）
- 每个 DID 下多个 Agent 实例（Alice 的 Muse / ChatGPT-Agent / 自建）
- Capability Ticket：`用户对某实例的一次授权`（scope + TTL + HMAC 签名）
- 吊销实例 → 连带吊销其所有 tickets

**2. 个人预算守护**
- 4 粒度：per_tx / daily / **weekly** / monthly
- 8 因素风险评分：
  - 金额超历史 P90 → +30
  - 目标域名命中 HIGH_RISK_DOMAIN_HINTS → +20
  - 深夜 00-06 → +10
  - 币种漂移 → +15
  - 首次目标 → +10
  - 高危 action（purchase/refund/wire_transfer/crypto_transfer）→ +10
- 4 档 verdict：**allow / confirm / block / denied**
  - allow：预算内 & 风险 < 40
  - confirm：预算内 & 风险 40-70（quote-first）
  - block：预算内 & 风险 ≥ 70（可覆盖）
  - denied：预算超限（不可覆盖）

**3. 行动溯源（HMAC 链）**
- 每 user 一条独立链
- 每 record 有 seq + prev_hash + hash（HMAC-SHA256）
- 90 天 TTL，最多 2000 条
- 离线可验证（`verify_action_chain`）
- 用户可发 dispute（`file_dispute`）

**4. Connector 独立审核**
- 8 项规则：危险 scope / 管道安装 / 明文 token / 签名 / 过期 / 权限过度 / quote-first / 描述一致性
- 返回 0-100 分数 + verdict（pass / pass_with_warnings / needs_review / reject）
- 定位：Meta 官方审核之外的**第二意见**

### 与 Muse 集成

- **主路径**：`connectors/muse/` 提交包 → muse.ai/platform
- **备选路径 A**：MCP 兼容（8 个 `aishield_personal_*` 工具，Muse 一旦支持 MCP 零迁移）
- **备选路径 B**：Web Bot Auth 头（GoDaddy+Cloudflare 2026-04 标准）
- **备选路径 C**：自建 Gateway（任何 agent 走 AIShield 才访问外部服务）

### 与 CyberGuard 对位

| 维度 | CyberGuard（GOAI 2026 Agent Infra 季军） | AIShield |
|---|---|---|
| 场景 | SOC / 企业应用 | 个人 Agent 治理 |
| 身份 | HMAC 审计 | 个人 DID + 企业 SD-JWT |
| 支付 | 无 | 消费级预算守护 |
| 证据 | OCSF/STIX/ATT&CK | SOC Evidence Bundle + 用户 dispute |
| Connector | 无 | 独立第二意见审核 |
| 关系 | 正交互补 | 非竞争，AIShield 可作 CyberGuard 上游身份层 |

---

## 四、文件清单

```
eco/
  personal_agent.py          ← 核心模块（~1200 行）
api/
  personal_agent_api.py      ← HTTP 端点（18 个）
mcp-server/
  src/index.ts               ← 8 个 aishield_personal_* 工具
  mcp.json                   ← manifest（48 工具总数）
  README.md                  ← 文档（新增 Personal Agent Governance 段）
connectors/
  muse/
    README.md                ← muse.ai/platform 提交材料
    openapi.yaml             ← OpenAPI 3.1 spec
docs/
  personal-agent-governance.md   ← 本文档
tests/
  test_personal_agent.py         ← 单元测试
```

---

## 五、技术选型

| 决策 | 选择 | 理由 |
|---|---|---|
| 签名算法 | Ed25519 优先 / HMAC-SHA256 降级 | 零依赖原则，与 agent_card 一致 |
| DID 方法 | `did:aishield:pa:<base32>` | 遵循 DWN 命名，独立于企业 DID 命名空间 |
| HMAC 链 | 每 user 独立 | 隐私隔离 + 独立验证 |
| 存储 | JSON 文件 | 零依赖、易迁移、易 export/delete（GDPR） |
| 风险评分 | 8 因素加权 | 消费级场景足够，避免复杂 ML |
| Connector 审核 | 关键词 + 启发式 | 快速独立第二意见，不追求完全自动化 |
| 支付 | 不处理支付，仅 pre-flight | 与 Stripe Link 正交 |

---

## 六、演进路线

**Phase 1（v4.8.0）+ Phase 1.1（v4.8.1，本文档）**：核心 + Muse/Grok Bot/Coze 提交包 + 12 MCP 工具 + 平台注册表 40+
**Phase 2（v4.9.0）**：
- SDK：Python / TypeScript 客户端
- Web 前端：个人 Agent 治理仪表盘
- Muse 审核反馈迭代
- ChatGPT-Agent / Claude-Agent 适配
**Phase 3（v5.0.0）**：
- 多语言 SDK（Go / Rust / Swift）
- 硬件钱包签名（硬件可信根）
- 与 ERC-8004 深集成（钱包作为个人 Agent 主权密钥）
- Agent 生态"个人 DID 互操作标准"提案（面向 W3C DID working group）

---

## 七、参考

- Meta Muse：https://www.jiemian.com/article/15131734.html
- Muse Connector Platform：https://muse.ai/platform
- CyberGuard：GOAI 2026 Agent Infra 季军
- OWASP MCP Top 10 (2025 v0.1)
- OWASP Agentic AI Top 10 (2026)
- Web Bot Auth（GoDaddy+Cloudflare 2026-04）
- ERC-8004（Ethereum 智能合约 Agent 身份）
- SD-JWT（RFC 9474）
