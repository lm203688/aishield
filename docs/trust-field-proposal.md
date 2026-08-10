# 提案：在发现格式中增加 `trust` 字段（中立信任裁决引用）

> 状态：草案 v0.1（2026-08-10）｜ 提交对象：Agent Card (Google A2A) / MCP Server Card (SEP-1649) / Google `ai-catalog` 工作组
> 配套规范：[docs/trust-attestation-spec.md](./trust-attestation-spec.md)（AIShield Trust Attestation `aishield-trust/v1`）

## 问题

发现层（MCP Registry / Server Card / ai-catalog / AGNTCY / ACP / ANP）正在快速成型，但所有格式都只回答
「*where is this endpoint / what does it do*」。共识是：**trust 是单独一层**——「who stands behind this endpoint,
and should I believe its content?」——而这一层目前最薄弱，且现有信任玩家（HVTracker / AIR / Metinc）**只扫供应链信号**
（OSSF Scorecard / 溯源 / 签名），**不扫工具/skill 的实际内容**（prompt 注入、工具中毒、供应链漂移）。

## 提案

在各类发现格式的 metadata 中增加一个可选 `trust` 字段，指向一个**中立、机器可读、可签名的信任裁决端点**。
发现方（crawler / registry / 客户端）无需连被扫服务，只查该端点即可拿到「这个端点背后是谁、内容是否安全」的裁决。

### 字段定义

```json
{
  "trust": {
    "authority": "aishield",
    "schema": "aishield-trust/v1",
    "verdict_url": "https://aishield.tools/api/v1/attestation/trust?src=<endpoint_url>",
    "badge": "https://aishield.tools/badge/<tool>"
  }
}
```

- `authority`：信任机构标识（可扩展为多个，发现方自行选择信任哪些）。
- `schema`：裁决凭证的 schema 版本（见 `aishield-trust/v1`）。
- `verdict_url`：返回信任裁决的端点（机器可读 JSON）。
- `badge`：人类可读 SVG 徽章。

### 为什么用 `aishield-trust/v1` 作为首个参考实现

- **唯一扫内容**：prompt 注入 / 工具中毒 / 供应链漂移，而不只是供应链信号。
- **本地离线 / 绝不执行**：纯静态推断，从不启动被扫配置里的命令（对比「扫描会执行命令」的陷阱）。
- **中立 / 免费 / 开源**：MIT，可被任何发现格式零成本引用，不绑定单一厂商。

## 落点（按格式）

- **MCP Server Card (SEP-1649)**：在 `.well-known/mcp-server-card.json` 顶层加 `trust`。
- **A2A Agent Card**：在 `protocols.mcp` 或顶层加 `trust`。
- **Google ai-catalog (`/.well-known/ai-catalog.json`)**：每条 service 指针加 `trust`。

## 自证（dogfooding）

AIShield 自己的 `docs/.well-known/agent-card.json` 已包含 `trust` 字段，证明发现层可零成本嵌入。

## 征集

欢迎各发现格式工作组、registry、运行时（forge / Goose / Open Interpreter / Cloudflare）就 `trust` 字段的
命名、schema 演进、多机构聚合方式提意见。目标：在信任层被定义成「只扫供应链」之前，把「内容可信」也纳入标准。
