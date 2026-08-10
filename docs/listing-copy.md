# 上架文案 / Listing Copy（对外分发用）

> 用途：提交到各 registry / 目录 / Marketplace 的文案副本。复制即用，按平台字数限制自行裁剪。
> 配套：docs/ecosystem-positioning-2026.md（占位策略）、docs/trust-attestation-spec.md（信任凭证）。

---

## 1. GitHub Marketplace — AIShield MCP/Agent Security Scan (Action)

**Name**: AIShield MCP/Agent Security Scan
**Short description**:
> Local-first, zero-egress security gate for MCP servers, agent skills & prompts. OWASP MCP Top 10 + Agentic ASI01–10, SARIF output, neutral trust badge.

**Full (≤ 65000 chars, 这里给要点)**:
- 本地优先、零出网：代码不出机器，无需上传 SaaS。
- 双维对齐：OWASP MCP Top 10 (2025) + OWASP Agentic AI Top 10 (ASI01–10)，214 MCP / 220 Skill 规则。
- 内容安全平面：唯一扫 prompt 注入 / 工具中毒 / 供应链漂移的扫描器。
- **绝不执行被扫配置**（no-spawn）：纯静态推断，扫恶意配置也不会中招（竞品会真实执行）。
- 中文合规：6 大平台违禁词覆盖。
- 输出 SARIF 2.1.0 → 直接进 GitHub Security；可嵌入信任徽章（金/银/铜）。
- `uses: lm203688/aishield@v4.2.2`

**Category**: Security / Testing
**Differentiator**: 占「中国合规 + 不执行」位，与 AgentAuditKit 通用位互补。

---

## 2. awesome-mcp-servers（PR #2 复核）

**Title**: AIShield — open-source MCP/Agent security scanner & neutral trust authority
**Blurb**:
> AIShield scans MCP servers, skills and prompts for tool poisoning, prompt injection, secret leakage and supply-chain risk — fully offline, 214/220 OWASP-aligned rules, never executes the scanned config. Also acts as a neutral trust authority: embeddable `aishield-trust/v1` attestation for Server Card / Agent Card / ai-catalog.

---

## 3. Cursor / Glama 目录

**One-liner**:
> AIShield — 本地离线、不执行被扫配置的下一代 agent 安全扫描器与中立信任机构。214/220 OWASP 规则，扫内容（prompt 注入/工具中毒），可嵌入信任凭证。

**Tags**: security, mcp, agent, trust, offline, owasp, prompt-injection

---

## 4. 社区触达（forge / Goose / Open Interpreter / Cloudflare）

**Angle**: 你们给 agent 一台隔离的电脑（爆炸半径），AIShield 补上内容可信（该不该信加载的 skill/工具）。
drop-in harness 示例见 `distribution/guardrail-harness/`。

**Post hook**:
> 沙箱只管「碰不到」，内容层管「信不过」。只上隔离层，一个加载了中毒 skill 的沙箱 agent 照样从容器内用你授予的凭据外泄数据。AIShield 的 guardrail harness 可作为 forge/Goose 的 pre-tool-call 拦截层，零依赖、离线、fail-closed。
