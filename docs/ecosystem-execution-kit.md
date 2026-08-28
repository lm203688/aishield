# AIShield 生态卡位 · 外部动作执行套件（2026-08-12）

> 本文件把「需要你账号/登录」的外部卡位动作，整理成**可直接复制粘贴/照做**的材料。
> 代码侧能力（身份/网络/Authentik/A2A/AI-slop/x402 六模块）已在仓库内落地并通过测试；
> 下面是「占位动作」——它们让 AIShield 真正成为发现层引用的**中立信任机构**。
>
> 优先级：P0 立即（低成本高杠杆）> P1 本月（渠道/标准）> P2 文化层（差异化叙事）。

---

## P0-1 · 在 A2A 仓库提 `trust.signal` 提案（#1628）

**链接**：https://github.com/google/A2A/issues/1628
**动作**：登录 GitHub → 打开 issue → 在底部评论框粘贴下面的内容 → Comment。

```markdown
## Proposal: register AIShield attestation as a `trust.signal` provider

A2A's signed AgentCard solves *identity* but leaves the "trust shallow" open
(session smuggling, delegated-authorization abuse). We propose a concrete
`trust.signal` entry that points at an external, machine-readable attestation
rather than re-implementing scoring inside the protocol.

```json
{
  "trust": {
    "standard": "aishield-trust/v1",
    "attestation_url": "https://aishield.tools/.well-known/agent-card.json",
    "verify": "GET https://aishield.tools/api/v1/trust?src=<agent-card-url>",
    "signal": {
      "verdict": "trusted | unverified | unknown",
      "content_scan": "pass | fail",
      "identity_attestation": "signed | unsigned",
      "score": 0-100
    }
  }
}
```

Why AIShield:
- **Scans content**, not just supply-chain signals (prompt injection / tool
  poisoning / rug-pull) — the gap HVTracker/AIR/OSSF Scorecard don't cover.
- **Local / offline**, no code sent to cloud; **never spawns** the scanned config.
- Already implements `identity_scan` (signed AgentCard, scope attenuation) and
  `agentcard_scan` (structured validation of the exact fields A2A issues discuss).

We'd love A2A WG feedback on the `trust.signal` envelope shape. Happy to align
the schema with whatever the WG standardizes.
```

**注意**：把上面的外层 ` ```markdown ` / 内层 ` ```json ` 在 GitHub 里嵌套会转义，
实际粘贴时只用一层代码块（json 块即可，外层去掉）。保留 JSON 示例。

---

## P0-2 · 认领 Glama 未认领 listing

**链接**：https://glama.ai/mcp/servers/lm203688/aishield （或搜索 `aishield`）
**动作**：
1. 登录 glama.ai（用 GitHub 账号）。
2. 搜 `aishield` / `lm203688/aishield` → 仓库被索引但显示 **Unclaimed**。
3. 点 **Claim** → 验证你是维护者（GitHub 仓库写权限即过）。
4. 填定位（建议文案）：
   - **Tagline**: `Local-first, offline AI Agent security scanner & neutral trust authority for MCP / A2A`
   - **Category**: Security / Dev Tools
   - **Description**: `227 MCP + 233 Skill OWASP-aligned rules; scans content (prompt injection, tool poisoning), agent identity, network/Mesh reachability, Authentik NHI, A2A AgentCard, AI-slop evasion and x402 payment scope. Never spawns the scanned config.`
5. 保存 → listing 变为 Claimed，出现在 Glama 发现流。

---

## P0-3 · Cloudflare Mesh 社区补位叙事

**场景**：Cloudflare Mesh 公告 / Agents Week 讨论 / Mesh 仓库 issue。
**动作**：发下面这段（可作为评论或独立 post）：

```text
Cloudflare Mesh nails "can the agent reach it" (reachability). The acknowledged
gap is per-agent identity + policy. AIShield sits on top of Mesh as the
content-trust + identity-attribution layer:

- Mesh decides reachability; AIShield decides "should this agent be believed,
  and what did it do" — pre-flight workspace scan before the sandbox boots,
  sandbox-hardening rules, per-tool-call admission with a hash-chained audit log,
  and continuous attestation that revokes certs on rug-pull.
- We already scan the exact Mesh pitfalls: account-wide network bindings with no
  per-agent policy, unauthenticated agent endpoints, private resources exposed
  public. Run both planes together.

Not competing with Mesh — complementary. Mesh = blast radius, AIShield = content trust.
```

---

## P1-1 · awesome-mcp-servers / Cursor / MCP Registry 上架复核

**材料**（文案见 `docs/listing-copy.md`，已备）：
- awesome-mcp-servers：找对应 PR #2 状态，若 stalled 补一版差异点说明（本地离线 + 不执行 + 扫内容）。
- Cursor / MCP Registry：确认 `npx @aishield/mcp-server` 在 Registry 可被索引（server-card 已在
  `api/static/.well-known/mcp/server-card.json` 暴露）。

---

## P1-2 · 向 ANS / ai-catalog 工作组提 `trust` 字段

**复用 P0-1 的 `trust` 信封**，提交到：
- Linux Foundation ANS（Agent Name Service）讨论
- Google `ai-catalog` `.well-known/ai-catalog.json` 扩展提案

核心一句话：**discovery ≠ trust；每个发现格式只需加一个 `trust` 字段指向 AIShield 的
`aishield-trust/v1` 即可零成本获得"内容是否可信"裁决。**

---

## P2-1 · soundshuman / de-AI 社区桥接定位文

**场景**：soundshuman / de-AI 相关讨论（"agent 产出要去 AI 味"）。
**动作**：发下面这段，明确分工、避免被误认为竞品：

```text
soundshuman 解决"风格层"：让 agent 输出更像人写、去 AI 味。
AIShield 解决"安全/可信层"：这个 agent 的内容有没有毒、有没有在规避检测。

两者互补，不是竞品：
- 去 AI 味被武器化 = 规避检测。AIShield 的 ai_slop_scan 专门识别"为绕过内容分类器
  而设计的 prompt/skill"（指令覆盖 / DAN 角色扮演 / base64·翻译混淆 / 反检测自指）。
- 风格自然 ≠ 内容安全。一个"像人写"的 skill 照样可能含 prompt 注入。

建议：de-AI 工具负责文风，AIShield 负责在 load 之前对 skill 做安全 attestation。
```

---

## 状态看板

| 动作 | 状态 | 谁做 | 备注 |
|---|---|---|---|
| A2A #1628 提案 | ⏳ 待发 | 用户 | 文案已备 |
| Glama 认领 | ⏳ 待认领 | 用户 | 文案已备 |
| Cloudflare Mesh 叙事 | ⏳ 待发 | 用户 | 文案已备 |
| awesome/Cursor/Registry 复核 | ⏳ 待复核 | 用户 | listing-copy.md 已备 |
| ANS/ai-catalog trust 字段 | ⏳ 待提 | 用户 | 复用 P0-1 信封 |
| soundshuman 桥接 | ⏳ 待发 | 用户 | 文案已备 |
| GitHub Action Marketplace 最终 Publish | ⏳ 待用户点 Publish | 用户 | action.yml v4.3.0 已强移 tag |

> 代码侧已闭环（6 个扫描模块 + 测试 483 通过）。外部动作只需账号登录，Agent 无法代点。
