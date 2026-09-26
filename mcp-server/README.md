# AIShield MCP Server

Security scanner for AI Agent tools, aligned with **OWASP MCP Top 10** and
**OWASP Agentic AI Top 10 (ASI)**. 201 local rules, 5-dimension scoring.

> `owasp_category` values `ASI01`–`ASI10` are AIShield's **internal** category IDs, not the
> official OWASP Top 10 for Agentic Applications (2026) identifiers. Only `ASI01`/`ASI02`/`ASI03`
> coincide; internal `ASI04` (memory poisoning) is official `ASI06`, and official `ASI04` is
> Agentic Supply Chain. Crosswalk: `internal_to_owasp_agentic` in the `compliance_summary`
> payload, source `scanner/compliance.py::INTERNAL_ASI_TO_OWASP`.

Scans never execute the code under review — AIShield reads configuration and
source statically, and never spawns commands from the config it is inspecting.

## Install

```bash
npx aishield-mcp-server
```

## Claude Desktop / Cursor / Windsurf

```json
{
  "mcpServers": {
    "aishield": {
      "command": "npx",
      "args": ["-y", "aishield-mcp-server"],
      "env": { "AISHIELD_API_KEY": "your-key" }
    }
  }
}
```

## Remote Mode (StreamableHTTP)

```json
{
  "mcpServers": {
    "aishield": {
      "url": "https://api.aishield.tools/mcp"
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `aishield_scan` | Full security scan — OWASP MCP Top 10 + Agentic AI Top 10, 235 rules, 5-dimension scoring |
| `aishield_guardrail` | Pre-install safety check — pass/block verdict with score |
| `aishield_prompt_check` | Prompt injection detection — Chinese + English |
| `aishield_banned_words` | Chinese content compliance — 6 platform rules |
| `aishield_rug_pull` | Rug pull detection — security code removed or new exfil paths across commits |
| `aishield_handshake` | MCP config review — `npx -y` risk, sensitive env vars, over-long tool descriptions |
| `aishield_digest` | Compact trust digest — a few hundred bytes + a content fingerprint, so an agent can answer "can I trust this?" every turn without re-pulling the full report. Its `risk` is never lighter than the worst finding present (high findings are never reported as "safe") and plaintext credentials are never echoed back |
| `aishield_laya_precheck` | Local Laya 421M decision-model pre-filter — calibrated probabilities for jailbreak / injection / sensitive-data / topic-classification. Non-generative, ~500 ms per call, zero cost, data never leaves the machine. Complement to the remote aishield scan: cheap inline guardrail before a scan, batch offline pre-filter. Fails soft (returns a startup hint) when the Laya HTTP service is down. English checkpoint has high false-positive rate on Chinese text — use `checkpoint=ml` for Chinese. |

### Trust Attestation (credential issue / verify / revoke)

| Tool | Description |
|------|-------------|
| `aishield_generate_attestation` | Issue a Trust Attestation credential aligned with `trust-attestation-v1` schema. |
| `aishield_verify_attestation` | Verify an attestation offline — schema + HMAC + expiry + revoke + issuer trust list. |
| `aishield_list_attestations` | List issued attestations with status filter. |
| `aishield_revoke_attestation` | Revoke an issued attestation with reason and operator. |

### Agent Card + Identity (Ed25519 / KYA SD-JWT / ERC-8004)

| Tool | Description |
|------|-------------|
| `aishield_sign_agent_card` | Sign an Agent Card with Ed25519 or HMAC-SHA256 fallback. |
| `aishield_verify_agent_card` | Verify Agent Card signature; detects post-signature tampering. |
| `aishield_export_identity` | Export agent identity as Ed25519 card + KYA SD-JWT + Web Bot Auth header. |
| `aishield_wrap_erc8004` | Wrap an Ethereum wallet address into ERC-8004 agent identity. |

### Specialist Registry (8 domains × 90-day TTL)

| Tool | Description |
|------|-------------|
| `aishield_register_specialist` | Register a specialist agent in one of 8 domains (legal/medical/finance/education/engineering/design/research/civic). |
| `aishield_list_specialist_domains` | List specialist domains with counts, top agents, and optional lapsed filter. |

### Responsibility Chain (HMAC-SHA256 chained audit)

| Tool | Description |
|------|-------------|
| `aishield_chain_create` | Create a new responsibility chain. |
| `aishield_chain_append` | Append a record; each entry HMAC-links to the previous one. |
| `aishield_chain_trace` | Trace backwards from an `output_ref` to the full responsibility path. |
| `aishield_chain_migrate_to_bundle` | Migrate a chain into an Evidence Bundle for R4-compliant audit. |

### Protocol Bridge (MCP / A2A / ACP / AP2)

| Tool | Description |
|------|-------------|
| `aishield_protocol_translate` | Translate a payload between MCP, A2A, ACP, and AP2 protocol formats. |

### Sandbox Backend (5-backend capability matrix)

| Tool | Description |
|------|-------------|
| `aishield_sandbox_backend_current` | Return the currently selected sandbox backend and its capability summary. |
| `aishield_sandbox_backend_matrix` | Full 5-backend capability matrix (OpenShell / mcpguard / meclaw / CF-isolate / python-subprocess). |
| `aishield_sandbox_evaluate` | Environment self-check returning per-backend availability. |

### Leaderboard + Contributor Incentives

| Tool | Description |
|------|-------------|
| `aishield_leaderboard_top` | Top-N agents by trust_score, optionally filtered by domain. |
| `aishield_leaderboard_query` | 4-dimension leaderboard snapshot (score/domain/provider/badge). |
| `aishield_leaderboard_snapshot` | Full leaderboard snapshot across all dimensions. |
| `aishield_contributors_leaderboard` | Contributor leaderboard across the 4-tier incentive system. |
| `aishield_contributor_register` | Register a contributor; enter the Contributor → Reviewer → Maintainer → Trustee ladder. |
| `aishield_contributor_add_event` | Add a weighted contribution event (review/rule_patch/bug_report/attestation/doc/ship_gate). |

### Evidence Bundle (R4-深化, CyberGuard v0.13.0 aligned)

HMAC-SHA256 chained audit + OCSF 1.1 event classes + STIX 2.1 observables + ATT&CK v15 TTP mapping + Proposal-Bound Approval + dual-round independent testing.

| Tool | Description |
|------|-------------|
| `aishield_evidence_create` | Create an Evidence Bundle instance (optionally HMAC-sealed). |
| `aishield_evidence_add_event` | Append an OCSF 1.1 event with optional ATT&CK TTP tag. |
| `aishield_evidence_create_proposal` | Create a Proposal-Bound proposal awaiting explicit approval. |
| `aishield_evidence_proposal` | Alias of `aishield_evidence_create_proposal`. |
| `aishield_evidence_approve_proposal` | Approve a proposal; binds approval_hash ↔ proposal_hash bidirectionally. |
| `aishield_evidence_approve` | Alias of `aishield_evidence_approve_proposal`. |
| `aishield_evidence_dispatch` | Dispatch an approved proposal to an executor agent. |
| `aishield_evidence_observe` | Run the dual-round independent observer against an executed proposal. |
| `aishield_evidence_rollback` | Roll back a dispatched action, emitting a rollback event into the HMAC chain. |
| `aishield_evidence_archive` | Archive a bundle into a portable manifest for offline transfer. |
| `aishield_evidence_verify` | Query live bundle verify state and HMAC chain integrity. |
| `aishield_evidence_verify_payload` | Offline verify a bundle payload with its HMAC secret. |
| `aishield_verify_evidence_bundle` | Alias of `aishield_evidence_verify_payload`. |

### Personal Agent Governance (v4.8.0, 2026-09-24)

面向个人 Agent（Meta Muse / ChatGPT-Agent / Claude-Agent / 自建 agent）的治理层。
覆盖消费级身份、预算守护、行动溯源、Connector 独立审核 —— 补齐个人 Agent 相比
企业 Agent 缺失的能力（Stripe Link 只处理单次卡号，无累计预算；每个平台
都有一套封闭的 Agent 账号体系，缺跨平台可验证的身份）。

| Tool | Description |
|------|-------------|
| `aishield_personal_did_create` | Create or fetch a Personal Agent Identity (PAI DID, `did:aishield:pa:*`). Idempotent. |
| `aishield_personal_instance_register` | Register a personal agent instance (e.g. "Alice's Muse on iOS") under her PAI DID. Revoke per-instance independently. |
| `aishield_personal_ticket_create` | Sign a capability ticket (action allowlist + scope + TTL) for one instance. Server HMAC-sealed, independently verifiable. |
| `aishield_personal_budget_check` | Pre-flight budget + risk check. Returns `allow` / `confirm` (quote-first) / `block` / `denied` verdict. |
| `aishield_personal_budget_reserve` | Reserve a personal budget before an order (freeze with 15 min TTL, idempotent by order_id). |
| `aishield_personal_action_record` | Append an action record to the user's HMAC chain — immutable provenance. |
| `aishield_personal_dispute_file` | File a dispute against a recorded action ("I didn't authorize this"). |
| `aishield_personal_connector_vet` | Independent second-opinion connector vetting (Meta review aside): dangerous scopes, piped-shell installs, plaintext tokens, quote-first, permission-description consistency. |

### Platform Registry (v4.8.1, 2026-09-24)

平台中立接入层：40+ 主流个人 Agent 平台的接入矩阵与治理缺口映射。
帮助使用者在 Muse / Grok Bot / ChatGPT Agent / Coze / DeepSeek 等
平台之间做选择，或让平台方（如 Muse 开发者）快速了解 AIShield 能补什么。

`aishield_personal_instance_register` 从 v4.8.1 起接受 `platform` 结构化字段
（如 `"meta-muse"` / `"xai-grok-bot"` / `"bytedance-coze"`），实例注册时自动
附带平台治理缺口。

| Tool | Description |
|------|-------------|
| `aishield_platform_catalog` | List the platform registry (40+ entries). Filter by `family` / `cny_accessible` / `access_path`. |
| `aishield_platform_detail` | Get full details for one platform ID (governance covered / gaps / AIShield provisions). |
| `aishield_platform_recommend` | Score-ranked recommendation given user_country, capabilities_needed, budget, developer_level. |
| `aishield_platform_gap_matrix` | Cross-platform governance gap matrix — one dict per platform with covered/gaps/provision_map. |

### Connectors — 海外平台真实接入 (v4.8.2, 2026-09-24)

Meta Muse、xAI Grok Bot 与 NVIDIA Developer Platform 的真实 REST 接入，前置 AIShield 治理层。
大陆需 `HTTPS_PROXY`；PAT / OAuth / NGC API Key 三通道；4-tier verdict；HMAC 行动链。

| Tool | Description |
|---|---|
| `aishield_connector_catalog` | List supported platforms (meta-muse, xai-grok-bot, nvidia-dev). |
| `aishield_connector_self_check` | Diagnostic: reachability, secret config, stored credentials, proxy summary. |
| `aishield_connector_authorize` | Build OAuth authorize URL (user opens browser; redirect_uri gets `?code=...`). Muse / Grok Bot only — nvidia-dev uses an NGC API Key. |
| `aishield_connector_exchange_code` | Exchange auth code for access_token + refresh_token. |
| `aishield_connector_register_agent` | Register a personal agent instance (PAT / OAuth / NGC API Key); ties it to a PAI DID. Pass `agent_instance_id` + `api_key` for nvidia-dev. |
| `aishield_connector_run` | Execute an agent action (chat / run_task / tool_call / nim_chat / ngc_catalog / nemo_job). Preflight budget + sensitive-keyword + risk; 4-tier verdict (allow / confirm / block / denied); override for block/confirm only; HMAC action chain record. |

### Agent Infra Scan — 开源基础设施扫描 (v4.8.3, 2026-09-25)

把 agent 基础设施类开源项目纳入生态：开源扫描 → 封装（MCP 适配器骨架）→
二次研发清单，三层交付物一次产出。

| Tool | Description |
|---|---|
| `aishield_agent_infra_targets` | List all agent-infrastructure / developer-platform scan targets (`family=infrastructure|developer`: nvidia-dev, laya, nasiko, agent-desktop, …). |
| `aishield_agent_infra_scan` | Scan one project and return `report` + `mcp_adapter_skeleton` + `secondary_rd_checklist`. Input is one of `repo_url` / `local_path` / `files` (in-memory dict, fully offline and deterministic). |

### Ship Gate (10-state release lifecycle)

| Tool | Description |
|------|-------------|
| `aishield_ship_gate_run` | Run the 10-state release gate: ANALYZE → BLIND_TEST → CHALLENGE → GATE → PREPARE → RELEASE → OBSERVE → ARCHIVE (+ ROLLBACK / REJECT). Emits an Evidence Bundle when `emit_bundle=true`. |

## Scoring Dimensions

1. **Security** (40%) — OWASP MCP Top 10 coverage
2. **Permissions** (20%) — Least privilege compliance
3. **Data Handling** (20%) — No secrets/exfiltration
4. **Supply Chain** (10%) — Dependency safety
5. **Reliability** (10%) — Auth/logging/observability

## OWASP MCP Top 10 Coverage

| Category | Rules | Description |
|----------|-------|-------------|
| MCP01 | 16 | Improper Token & Secret Management |
| MCP02 | 12 | Privilege Scope Creep |
| MCP03 | 8 | Tool Poisoning |
| MCP04 | 12 | Supply Chain Attack & Dependency Tampering |
| MCP05 | 24 | Command Injection & Execution |
| MCP06 | 13 | Intent Flow Subversion / Prompt Injection |
| MCP07 | 8 | Insufficient Authentication & Authorization |
| MCP08 | 6 | Lack of Audit & Observability |
| MCP09 | 6 | Shadow MCP Servers |
| MCP10 | 8 | Context Injection & Over-Sharing |

Subtotal: **235 rules**

## OWASP Agentic AI Top 10 (ASI) Coverage

| Category | Rules | Description |
|----------|-------|-------------|
| ASI01 | 6 | Goal and Instruction Manipulation |
| ASI02 | 6 | Tool Misuse |
| ASI03 | 8 | Excessive Agency |
| ASI04 | 6 | Memory Manipulation |
| ASI05 | 6 | Agent Identity and Trust |
| ASI06 | 6 | Agent Communication and Supply Chain |
| ASI07 | 6 | Unbounded Resource Consumption |
| ASI08 | 6 | Observability and Monitoring Gaps |
| ASI09 | 6 | Cascading Failures & Multi-Agent Risks |
| ASI10 | 6 | Rogue Agent & Human-Autonomy Boundary |

Subtotal: **235 rules**

## Other rule sets

| Source | Rules | Where it comes from |
|--------|------:|---------------------|
| Sandbox / host-escape heuristics | 11 | static, shipped in `scanner/rules.py` |
| Chinese-language prompt injection | 22 | static, shipped in `scanner/rules.py` |
| Threat-intel generated | 8 | `data/generated_rules.json` — regenerated by the intel workflow |
| Tech-Radar promoted | 19 | `data/radar_rules.json` — promoted after the rule-promotion gate |

Static baseline: **235 rules** (113 MCP + 62 ASI + 11 sandbox + 22 Chinese)

**Total: 235 rules** (MCP type) / **262 rules** (Skill type)

The Skill total adds 27 skill-specific rules on top of the MCP set.

> The two dynamic sets are loaded at startup from JSON files in `data/`. If a
> deployment has an older copy of those files, `GET /api/v1/health` reports the
> exact split as `rules_breakdown: {static, generated, radar, total}` — compare
> it against the numbers above instead of guessing which side is stale.

## Provenance & verification

Registry publication alone does not establish an audit. Installing a package
from npm or the MCP registry tells you nothing about whether anyone reviewed the
code inside it — so here is what is actually verifiable, and what is not.

**What the npm provenance attestation does cover.** Every release is built by
`.github/workflows/publish-npm.yml` with `id-token: write` and published using
`npm publish --provenance`. That attestation binds the tarball to a specific
commit of `github.com/lm203688/aishield` that ran on GitHub Actions, and is
signed by sigstore. Verify it rather than trusting the version number:

```bash
npm install aishield-mcp-server@4.8.3
npm audit signatures          # npm >= 9.5
```

The signature check tells you the tarball is the one Actions built at that
commit. Then confirm the commit is one you recognize:

```bash
git clone https://github.com/lm203688/aishield
cd aishield && git checkout <commit> && npm run build   # rebuild and diff dist/
```

**What it does not cover.**

- It is not a security review. A malicious maintainer with a compromised token
  can produce a valid provenance attestation for code they wrote.
- It is not a guarantee about the version number on the page above. `dist/` is
  built in CI, not hand-edited, but nothing stops a bad release from being
  published with a valid signature.
- **The build has a fallback path.** If provenance signing fails, the workflow
  retries without `--provenance` and only emits a `::warning::` in the log.
  A version can therefore be published *without* an attestation and still look
  normal. That is why the check above is the `npm audit signatures` step, not
  "check the version string". If a version has no signature, treat it as
  unverified and pin the commit instead.

**Record what you rely on.** For anything you depend on, write down the release
you selected, the source commit you reviewed, and the package integrity check
you ran. The registry page is not that record — it can change.

## License

MIT