# AIShield Trust Attestation —— 可嵌入发现层的中立信任凭证

> 状态：提案 v0.1（2026-08-10）｜ 用途：让 MCP Server Card / A2A Agent Card / ai-catalog 等**发现格式**用统一 `trust` 字段引用 AIShield 的扫描型信任裁决，使 AIShield 成为 agent 生态的「信任层」节点。
> 后端现状：`api/server.py` 已提供 `/api/v1/trust/*`、`/api/v1/attestation/trust`、`/badge/{tool}`；`eco/attestation.py` 提供订阅/鉴证/哈希链。本规范把这些能力收敛成一个**机器可读、可签名、可嵌入**的凭证。

## 1. 为什么需要它（占位逻辑）

调研结论（2026-08-10）：发现层是标准战（MCP Registry / Server Card / ai-catalog / AGNTCY / ACP / ANP），但所有发现格式都共识一点——**"trust layer answers who stands behind this endpoint"**，而这一层目前最薄弱。现有信任玩家：
- HVTracker / AIR / Metinc：**只扫供应链信号**（OSSF Scorecard / 溯源 / 签名），**不扫工具/skill 的实际内容**（prompt 注入、工具中毒）。
- Orac：信任分 + x402，但依赖付费 API 做注入筛查。

**AIShield 的差异化锚点**：唯一**本地离线、扫内容（prompt 注入 / 工具中毒 / 供应链漂移）、绝不执行被扫配置**的信任裁决。本规范把它变成可被发现层零成本引用的凭证，抢在对手把"信任层"定义成"只扫供应链"之前定型。

## 2. 凭证 schema（`aishield-trust.json`）

```json
{
  "schema": "aishield-trust/v1",
  "issuer": "https://aishield.tools",
  "issued_at": "2026-08-10T12:00:00Z",
  "subject": {
    "type": "mcp_server | skill | agent | prompt",
    "url": "https://github.com/owner/repo",
    "name": "example-server"
  },
  "verdict": {
    "score": 92,
    "level": "gold | silver | bronze | basic",
    "risk": "safe | medium | high | critical",
    "no_spawn_guarantee": true,
    "offline_scan": true
  },
  "coverage": {
    "owasp_mcp_top10": "10/10",
    "owasp_asi_top10": "10/10",
    "dimensions": ["security", "permissions", "data_handling", "supply_chain", "reliability"]
  },
  "attestation": {
    "method": "continuous | once",
    "last_attested_at": "2026-08-10T12:00:00Z",
    "chain_anchor": "sha256:abc123...",
    "evidence_count": 7
  },
  "badge": "https://aishield.tools/badge/example-server",
  "api": "https://aishield.tools/api/v1/trust?src=https://github.com/owner/repo"
}
```

字段说明：
- `no_spawn_guarantee: true` —— **结构性卖点**：声明该信任裁决基于纯静态推断，从不启动被扫配置里的命令（对比 Snyk「扫描会执行命令」的陷阱）。
- `attestation.chain_anchor` —— 复用 `eco/attestation.py` 的哈希链，使裁决可审计、防篡改。
- `badge` / `api` —— 机器可直接拉取/展示，人类可读 SVG 徽章。

## 3. 如何嵌入发现格式（三种即插即用）

**A. MCP Server Card（SEP-1649）** — 在 `.well-known/mcp-server-card.json` 增加：
```json
{ "trust": { "authority": "aishield", "url": "https://aishield.tools/api/v1/trust?src=<server_url>" } }
```

**B. A2A Agent Card（`/.well-known/agent-card.json`）** — 在 `protocols.mcp` 或顶层增加：
```json
{ "trust": { "authority": "aishield", "verdict_url": "https://aishield.tools/api/v1/attestation/trust?src=<agent_url>" } }
```

**C. Google ai-catalog（`/.well-known/ai-catalog.json`）** — 每条 service 指针增加 `trust` 字段同上。

发现方（crawler / registry / 客户端）无需连被扫服务，只查 AIShield 端点即可拿到"这个端点背后是谁、内容是否安全"的裁决——正好补上发现层缺的信任层。

## 4. 公开端点（已存在，需对外标定）

| 端点 | 用途 |
|------|------|
| `GET /api/v1/trust?src=<url>` | 返回上述 `aishield-trust.json` 裁决 |
| `GET /api/v1/attestation/trust?src=<url>` | 持续鉴证状态 |
| `GET /badge/{tool}` | 公开 SVG 徽章（可嵌 README / 注册表页） |
| `GET /api/v1/attestation/plans` | 订阅计划（x402 / 虎皮椒可结算） |

## 5. 占位动作（配套 `ecosystem-positioning-2026.md` P0）

1. 本规范 v0.1 定稿后，在 AIShield 自有 `agent-card.json` / `llms.txt` 内**狗粮式引用**自己的 `trust` 字段（证明可用）。
2. 向 Agent Card / MCP Server Card / ai-catalog 工作组提交"trust 字段"提案（P1 外部）。
3. 在 README / GEO 资产中把"中立信任机构"作为头号定位叙事。
