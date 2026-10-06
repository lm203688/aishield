# AIShield Agent API 调用索引

> **本文件由 `scripts/gen_agent_api_index.py` 从运行时契约自动生成，请勿手工编辑。**
> 契约本身是实现的投影（`get_openapi_spec()` = curated + 运行时探得路由），
> 因此新增一条路由，重算本文件即带上，不存在“抄漏”这一层。

外部 agent 的正确调用顺序是：**先确认我能不能被信 → 再确认这次动作合不合规 → 最后才是生态位与分发**。
下表按这个顺序分组，不按字母、不按模块。

## 索引健康度（每次重算实测）

| 指标 | 值 |
|:---|:---|
| 契约版本 | `3.0.3` |
| 可调用操作数 | **148** |
| 已声明请求体 | 28 |
| **请求体未声明** | **120** |
| 组件 schema 数 | 11 |

`请求体未声明` 不是“参数无意义”，而是**契约还没把它写下来** —— 外部 agent 只能靠猜字段名。缺口是**可数的**，见文末清单；`--check` 防止它悄悄变大。

## P0 · 信任与身份（先回答“我能不能被信”）

共 45 条操作。

| 方法 | 路径 | 认证 | 实测状态 | 摘要 | 响应顶层字段 | 请求体 |
|:---|:---|:---:|:---:|:---|:---|:---|
| `POST` | `/api/v1/agent-card/identity` | 未声明 | 200 | Agent 生态 API · identity | `agent_id`, `kya`, `kya_sd_jwt_compact`, `web_bot_auth`, `erc8004` | `card`, `trust_score` |
| `GET` | `/api/v1/agent-card/pubkey` | 未声明 | 200 | Agent 生态 API · pubkey | `signer_did`, `key_id`, `alg`, `public_key`, `endpoint` | 未声明 |
| `POST` | `/api/v1/agent-card/sign` | 未声明 | 200 | Agent 生态 API · sign | `aishield` | `card`, `trust_score` |
| `POST` | `/api/v1/agent-card/verify` | 未声明 | 200 | Agent 生态 API · verify | `valid`, `reason` | `card`, `public_key` |
| `POST` | `/api/v1/attestation/cancel` | 未声明 | 200 | POST /api/v1/attestation/cancel | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/attestation/expiring` | 未声明 | 200 | GET /api/v1/attestation/expiring | `success`, `total`, `subscriptions` | 未声明 |
| `GET` | `/api/v1/attestation/list` | 未声明 | 200 | GET /api/v1/attestation/list | `success`, `total`, `subscriptions` | 未声明 |
| `GET` | `/api/v1/attestation/plans` | 未声明 | 200 | GET /api/v1/attestation/plans | `success`, `plans` | 未声明 |
| `POST` | `/api/v1/attestation/renew` | 未声明 | 200 | POST /api/v1/attestation/renew | `success`, `error`, `subscription_id`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/attestation/run-cycle` | 未声明 | 200 | POST /api/v1/attestation/run-cycle | `success`, `total`, `attested`, `skipped`, `failed`, `errors` …（共 8） | 未声明 |
| `POST` | `/api/v1/attestation/subscribe` | 未声明 | 200 | POST /api/v1/attestation/subscribe | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/attestation/trust` | 未声明 | 200 | GET /api/v1/attestation/trust | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/attestations` | 未声明 | 200 | GET /api/v1/attestations | `count`, `attestations` | 未声明 |
| `POST` | `/api/v1/attestations` | 未声明 | 200 | POST /api/v1/attestations | `error`, `error_code`, `error_id` | `subject`, `verdict`, `coverage`, `attestation`, `issuer`, `expires_at` |
| `GET` | `/api/v1/attestations/from-scan` | 未声明 | 200 | GET /api/v1/attestations/from-scan | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/attestations/from-scan` | 未声明 | 200 | POST /api/v1/attestations/from-scan | `error`, `error_code`, `error_id` | `scan_result`, `subject_url`, `subject_type` |
| `GET` | `/api/v1/attestations/revoke` | 未声明 | 200 | GET /api/v1/attestations/revoke | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/attestations/revoke` | 未声明 | 200 | POST /api/v1/attestations/revoke | `error`, `error_code`, `error_id` | `attestation_id`, `reason` |
| `GET` | `/api/v1/attestations/schema` | 未声明 | 200 | GET /api/v1/attestations/schema | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/attestations/verify` | 未声明 | 200 | GET /api/v1/attestations/verify | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/attestations/verify` | 未声明 | 200 | POST /api/v1/attestations/verify | `error`, `error_code`, `error_id` | `attestation_id`, `online_verification` |
| `GET` | `/api/v1/digest` | 未声明 | 200 | GET /api/v1/digest | `error`, `hint`, `schema`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/identity/agents` | 未声明 | 200 | 列出所有已注册 Agent | `success`, `total`, `agents` | 未声明 |
| `POST` | `/api/v1/identity/credentials/issue` | 未声明 | 200 | Agent 生态 API · issue | `error`, `error_code`, `error_id` | `did`, `owner`, `identity_token`, `claims`, `ttl` |
| `POST` | `/api/v1/identity/credentials/revoke` | 未声明 | 200 | Agent 生态 API · revoke | `success`, `error`, `error_code`, `error_id` | `did`, `owner`, `credential_id` |
| `POST` | `/api/v1/identity/credentials/verify` | 未声明 | 200 | Agent 生态 API · verify | `success`, `error`, `error_code`, `error_id` | `token` |
| `POST` | `/api/v1/identity/erc8004/wrap` | 未声明 | 200 | Agent 生态 API · wrap | `error`, `error_code`, `error_id` | `wallet_address`, `chain_id` |
| `GET` | `/api/v1/identity/jwks` | 未声明 | 200 | Agent 生态 API · jwks | `keys`, `ready`, `algorithm`, `reason` | 未声明 |
| `POST` | `/api/v1/identity/kyad/export` | 未声明 | 200 | Agent 生态 API · export | `agent_id`, `kya`, `kya_sd_jwt_compact`, `web_bot_auth`, `erc8004` | `card`, `trust_score` |
| `POST` | `/api/v1/identity/register` | 需要 | 200 | 注册 Agent（需注册凭据） | `success`, `did`, `name`, `reputation_score`, `status`, `registered_at` | AgentRegisterRequest |
| `POST` | `/api/v1/identity/registration-token` | 未声明 | 200 | Agent 生态 API · registration-token | `error`, `error_code`, `error_id` | `owner`, `ttl_seconds` |
| `GET` | `/api/v1/identity/wallets` | 未声明 | 200 | Agent 生态 API · wallets | `docs` | 未声明 |
| `GET` | `/api/v1/registry` | 未声明 | 200 | Trust API 认证与信任评分 · registry | `count`, `agents` | 未声明 |
| `GET` | `/api/v1/registry/discover` | 未声明 | 200 | Trust API 认证与信任评分 · discover | `error`, `agent_id`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/registry/discover` | 未声明 | 200 | Trust API 认证与信任评分 · discover | `object` | 未声明 |
| `GET` | `/api/v1/trust` | 未声明 | 200 | Trust API 认证与信任评分 · trust | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/trust` | 未声明 | 200 | Trust API 认证与信任评分 · trust | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/trust/auto` | 未声明 | 200 | Trust API 认证与信任评分 · auto | `error`, `error_code`, `error_id` | `scan_result` |
| `GET` | `/api/v1/trust/cert` | 未声明 | 200 | Trust API 认证与信任评分 · cert | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/trust/certify` | 未声明 | 200 | Trust API 认证与信任评分 · certify | `error`, `error_code`, `error_id` | `source_url`, `scan_report` |
| `GET` | `/api/v1/trust/digest` | 未声明 | 200 | Trust API 认证与信任评分 · digest | `error`, `hint`, `schema`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/trust/digest` | 未声明 | 200 | Trust API 认证与信任评分 · digest | `error`, `hint`, `schema`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/trust/score` | 未声明 | 200 | Trust API 认证与信任评分 · score | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/trust/verify` | 未声明 | 200 | Trust API 认证与信任评分 · verify | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/trust/verify` | 未声明 | 200 | Trust API 认证与信任评分 · verify | `error`, `error_code`, `error_id` | `src`, `type` |

## P1 · 准入与证据（这次动作合不合规）

共 16 条操作。

| 方法 | 路径 | 认证 | 实测状态 | 摘要 | 响应顶层字段 | 请求体 |
|:---|:---|:---:|:---:|:---|:---|:---|
| `POST` | `/api/v1/chain` | 未声明 | 200 | Agent 生态 API · chain | `schema`, `chain_id`, `entries`, `head_hash`, `hmac`, `verified` …（共 7） | `chain_id` |
| `POST` | `/api/v1/evidence` | 未声明 | 200 | POST /api/v1/evidence | `run_id`, `hmac`, `created_at`, `title` | 未声明 |
| `GET` | `/api/v1/evidence/schemas` | 未声明 | 200 | GET /api/v1/evidence/schemas | `schema`, `ocsf_classes`, `stix_observable_types`, `attack_ttps`, `states`, `transitions` | 未声明 |
| `GET` | `/api/v1/evidence/verify-payload` | 未声明 | 200 | GET /api/v1/evidence/verify-payload | `schema`, `run_id`, `title`, `description`, `created_at`, `hmac` …（共 14） | 未声明 |
| `POST` | `/api/v1/evidence/verify-payload` | 未声明 | 200 | POST /api/v1/evidence/verify-payload | `verification` | 未声明 |
| `POST` | `/api/v1/intent/mandates` | 未声明 | 200 | POST /api/v1/intent/mandates | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/intent/mandates/evaluate` | 未声明 | 200 | POST /api/v1/intent/mandates/evaluate | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/intent/mandates/verify` | 未声明 | 200 | POST /api/v1/intent/mandates/verify | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/protocol/normalize` | 未声明 | 200 | Agent 生态 API · normalize | `error`, `error_code`, `error_id` | `protocol`, `payload` |
| `POST` | `/api/v1/protocol/translate` | 未声明 | 200 | Agent 生态 API · translate | `error`, `error_code`, `error_id` | `target`, `payload`, `from_protocol` |
| `GET` | `/api/v1/sandbox/backend/current` | 未声明 | 200 | Agent 生态 API · current | `recommended`, `system`, `python_version`, `backends`, `recommended_info` | 未声明 |
| `GET` | `/api/v1/sandbox/backend/matrix` | 未声明 | 200 | Agent 生态 API · matrix | `system`, `recommended`, `matrix` | 未声明 |
| `POST` | `/api/v1/scan/attack-path` | 未声明 | 200 | POST /api/v1/scan/attack-path | `recommendation`, `graph` | 未声明 |
| `POST` | `/api/v1/scan/client-config` | 未声明 | 200 | POST /api/v1/scan/client-config | `error`, `hint`, `clients_supported`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/ship-gate/run` | 未声明 | 200 | POST /api/v1/ship-gate/run | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/ship-gate/states` | 未声明 | 200 | GET /api/v1/ship-gate/states | `states`, `transitions`, `schema` | 未声明 |

## P2 · 生态位与分发（让人找得到我）

共 18 条操作。

| 方法 | 路径 | 认证 | 实测状态 | 摘要 | 响应顶层字段 | 请求体 |
|:---|:---|:---:|:---:|:---|:---|:---|
| `POST` | `/api/v1/agent-infra/scan` | 未声明 | 200 | 海外平台接入与 Agent 基础设施扫描 · scan | `ok`, `error`, `error_code`, `error_id` | `name`, `repo_url`, `local_path`, `files`, `platform_id`, `tool_type` |
| `POST` | `/api/v1/agent-infra/scan-portfolio` | 未声明 | 200 | 海外平台接入与 Agent 基础设施扫描 · scan-portfolio | `ok`, `error`, `error_code`, `error_id` | `specs` |
| `GET` | `/api/v1/agent-infra/targets` | 未声明 | 200 | 海外平台接入与 Agent 基础设施扫描 · targets | `object` | 未声明 |
| `GET` | `/api/v1/billing/plans` | 未声明 | 200 | 查询计费套餐 | `success`, `plans` | 未声明 |
| `GET` | `/api/v1/connectors` | 未声明 | 200 | 海外平台接入与 Agent 基础设施扫描 · connectors | `ok`, `platforms`, `count` | 未声明 |
| `POST` | `/api/v1/connectors` | 未声明 | 200 | 海外平台接入与 Agent 基础设施扫描 · connectors | `ok`, `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/connectors/{plat}/self-check` | 未声明 | 200 | 海外平台接入与 Agent 基础设施扫描 · self-check | `ok`, `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/connectors/{plat}/state` | 未声明 | 200 | 海外平台接入与 Agent 基础设施扫描 · state | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/contributors` | 未声明 | 200 | Agent 生态 API · contributors | `count`, `contributors` | 未声明 |
| `POST` | `/api/v1/contributors` | 未声明 | 200 | Agent 生态 API · contributors | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/contributors/leaderboard` | 未声明 | 200 | Agent 生态 API · leaderboard | `leaderboard` | 未声明 |
| `GET` | `/api/v1/contributors/tiers` | 未声明 | 200 | Agent 生态 API · tiers | `tiers` | 未声明 |
| `GET` | `/api/v1/leaderboard/providers` | 未声明 | 200 | Agent 生态 API · providers | `providers` | 未声明 |
| `GET` | `/api/v1/leaderboard/snapshot` | 未声明 | 200 | Agent 生态 API · snapshot | `schema`, `generated_at`, `totals`, `top_by_score`, `top_by_badge`, `top_by_domain` …（共 7） | 未声明 |
| `GET` | `/api/v1/leaderboard/top` | 未声明 | 200 | Agent 生态 API · top | `schema`, `top` | 未声明 |
| `GET` | `/api/v1/specialist/agents` | 未声明 | 200 | Agent 生态 API · agents | `count`, `items` | 未声明 |
| `POST` | `/api/v1/specialist/agents` | 未声明 | 200 | Agent 生态 API · agents | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/specialist/domains` | 未声明 | 200 | Agent 生态 API · domains | `array` | 未声明 |

## P3 · 运营与自省（其余）

共 69 条操作。

| 方法 | 路径 | 认证 | 实测状态 | 摘要 | 响应顶层字段 | 请求体 |
|:---|:---|:---:|:---:|:---|:---|:---|
| `GET` | `/api/v1/account/balance` | 未声明 | 200 | GET /api/v1/account/balance | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/account/login` | 未声明 | 200 | POST /api/v1/account/login | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/account/me` | 未声明 | 200 | GET /api/v1/account/me | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/account/recharge` | 未声明 | 200 | POST /api/v1/account/recharge | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/account/register` | 未声明 | 200 | POST /api/v1/account/register | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/agent/scan` | 未声明 | 200 | POST /api/v1/agent/scan | `success`, `error_code`, `error`, `error_id`, `detail` | 未声明 |
| `POST` | `/api/v1/agent/setup` | 无 | 201 | Agent 一键入驻 | $ref AgentSetupResponse | AgentSetupRequest |
| `GET` | `/api/v1/arena/health` | 未声明 | 200 | GET /api/v1/arena/health | `ok`, `version`, `scanner_available`, `mcp_rules`, `skill_rules`, `timestamp` | 未声明 |
| `POST` | `/api/v1/arena/scan` | 未声明 | 200 | POST /api/v1/arena/scan | `scan_id`, `timestamp`, `verdict`, `fingerprint`, `rule_counts`, `findings` …（共 8） | 未声明 |
| `POST` | `/api/v1/audit` | 无 | 200 | 执行安全扫描 | $ref AuditResponse | AuditRequest |
| `POST` | `/api/v1/banned-words` | 无 | 200 | 违禁词检测 | `safe`, `hits`, `total_hits` | BannedWordsRequest |
| `POST` | `/api/v1/certify/fulfill` | 未声明 | 200 | POST /api/v1/certify/fulfill | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/certify/list` | 未声明 | 200 | GET /api/v1/certify/list | `success`, `certifications` | 未声明 |
| `POST` | `/api/v1/certify/request-payment` | 未声明 | 200 | POST /api/v1/certify/request-payment | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/certify/request-payment-cny` | 未声明 | 200 | POST /api/v1/certify/request-payment-cny | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/checkout/create` | 未声明 | 200 | POST /api/v1/checkout/create | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/export` | 未声明 | 200 | POST /api/v1/export | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/export/sarif` | 未声明 | 200 | POST /api/v1/export/sarif | `$schema`, `version`, `runs` | 未声明 |
| `POST` | `/api/v1/export/sbom` | 未声明 | 200 | POST /api/v1/export/sbom | `bomFormat`, `specVersion`, `serialNumber`, `version`, `metadata`, `components` …（共 7） | 未声明 |
| `GET` | `/api/v1/fleet` | 未声明 | 200 | GET /api/v1/fleet | `success`, `total`, `pass`, `fail`, `pass_rate`, `avg_score` …（共 11） | 未声明 |
| `POST` | `/api/v1/fleet/ingest` | 未声明 | 200 | POST /api/v1/fleet/ingest | `success`, `member`, `fleet_size` | 未声明 |
| `GET` | `/api/v1/fleet/list` | 未声明 | 200 | GET /api/v1/fleet/list | `success`, `members` | 未声明 |
| `GET` | `/api/v1/governance/audit` | 未声明 | 200 | GET /api/v1/governance/audit | `success`, `total`, `chain`, `entries` | 未声明 |
| `POST` | `/api/v1/governance/evaluate` | 未声明 | 200 | POST /api/v1/governance/evaluate | `success`, `decision`, `allowed`, `server`, `tool`, `reason` …（共 9） | 未声明 |
| `POST` | `/api/v1/governance/incident` | 未声明 | 200 | POST /api/v1/governance/incident | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/governance/kill` | 未声明 | 200 | POST /api/v1/governance/kill | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/governance/policy` | 未声明 | 200 | GET /api/v1/governance/policy | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/governance/policy` | 未声明 | 200 | POST /api/v1/governance/policy | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/governance/revive` | 未声明 | 200 | POST /api/v1/governance/revive | `success`, `error`, `server`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/governance/status` | 未声明 | 200 | GET /api/v1/governance/status | `success`, `default_deny`, `killed`, `killed_count`, `allow_rules`, `deny_rules` …（共 11） | 未声明 |
| `POST` | `/api/v1/handshake` | 无 | 200 | MCP 握手 | `success`, `session_id`, `server_info` | HandshakeRequest |
| `GET` | `/api/v1/health` | 无 | 200 | 健康检查 | $ref HealthResponse | 未声明 |
| `POST` | `/api/v1/mcp` | 无 | 200 | MCP JSON-RPC 2.0 端点 | `jsonrpc`, `id`, `result`, `error` | MCPRequest |
| `POST` | `/api/v1/monitor/add` | 未声明 | 200 | POST /api/v1/monitor/add | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/monitor/check` | 未声明 | 200 | POST /api/v1/monitor/check | `success`, `results`, `total` | 未声明 |
| `GET` | `/api/v1/monitor/list` | 未声明 | 200 | GET /api/v1/monitor/list | `success`, `total`, `tools` | 未声明 |
| `POST` | `/api/v1/osv` | 未声明 | 200 | POST /api/v1/osv | `findings` | 未声明 |
| `POST` | `/api/v1/pay/hupijiao/create` | 未声明 | 200 | POST /api/v1/pay/hupijiao/create | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/pay/hupijiao/notify` | 未声明 | 200 | POST /api/v1/pay/hupijiao/notify | `object` | 未声明 |
| `GET` | `/api/v1/pay/hupijiao/orders` | 未声明 | 200 | GET /api/v1/pay/hupijiao/orders | `success`, `total`, `orders` | 未声明 |
| `GET` | `/api/v1/pay/hupijiao/query` | 未声明 | 200 | GET /api/v1/pay/hupijiao/query | `success`, `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/pay/hupijiao/status` | 未声明 | 200 | GET /api/v1/pay/hupijiao/status | `success`, `gateway`, `configured`, `appid`, `app_secret`, `secret_fingerprint` …（共 10） | 未声明 |
| `POST` | `/api/v1/personal-agents/budget/check` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · check | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/personal-agents/budget/commit` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · commit | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/personal-agents/budget/release` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · release | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/personal-agents/budget/reserve` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · reserve | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/personal-agents/stats` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · stats | `users_total`, `agent_instances_total`, `active_tickets_total`, `actions_total`, `open_disputes_total` | 未声明 |
| `POST` | `/api/v1/personal-agents/tickets/consume` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · consume | `allowed`, `valid`, `reason` | 未声明 |
| `POST` | `/api/v1/personal-agents/tickets/verify` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · verify | `valid`, `reason` | 未声明 |
| `GET` | `/api/v1/personal-agents/users` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · users | `users` | 未声明 |
| `POST` | `/api/v1/personal-agents/users` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · users | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/platforms` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · platforms | `object` | 未声明 |
| `GET` | `/api/v1/platforms/gap-matrix` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · gap-matrix | `object` | 未声明 |
| `GET` | `/api/v1/platforms/recommend` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · recommend | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/platforms/recommend` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · recommend | `object` | 未声明 |
| `GET` | `/api/v1/platforms/register` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · register | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/platforms/register` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · register | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/platforms/stats` | 未声明 | 200 | 个人 Agent 治理层与平台注册表 · stats | `total_platforms`, `by_family`, `by_cny_accessible`, `by_access_path`, `governance_provisions_count`, `access_paths_defined` …（共 7） | 未声明 |
| `POST` | `/api/v1/policy/check` | 未声明 | 200 | POST /api/v1/policy/check | `passed`, `score`, `violations`, `policy_name` | 未声明 |
| `POST` | `/api/v1/prompt-check` | 无 | 200 | Prompt 注入检测 | `safe`, `risk_level`, `matches` | PromptCheckRequest |
| `POST` | `/api/v1/proxy/call` | 未声明 | 200 | POST /api/v1/proxy/call | `error`, `error_code`, `error_id` | 未声明 |
| `GET` | `/api/v1/proxy/stats` | 未声明 | 200 | GET /api/v1/proxy/stats | `total_calls`, `success_calls`, `blocked_calls`, `error_calls`, `by_tool`, `by_agent` …（共 7） | 未声明 |
| `GET` | `/api/v1/proxy/tools` | 未声明 | 200 | GET /api/v1/proxy/tools | `total`, `tools` | 未声明 |
| `POST` | `/api/v1/rug-pull` | 未声明 | 200 | POST /api/v1/rug-pull | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/score/audit` | 未声明 | 200 | POST /api/v1/score/audit | `error`, `error_code`, `error_id` | 未声明 |
| `POST` | `/api/v1/spend-cap/policy` | 未声明 | 200 | POST /api/v1/spend-cap/policy | `success`, `payer_id`, `currency`, `limits` | 未声明 |
| `GET` | `/api/v1/spend-cap/usage` | 未声明 | 200 | GET /api/v1/spend-cap/usage | `success`, `payer_id`, `currency`, `enabled`, `limits`, `daily_spent` …（共 12） | 未声明 |
| `GET` | `/api/v1/stats` | 未声明 | 200 | GET /api/v1/stats | `total_scans`, `total_api_calls`, `today`, `owasp_categories`, `rules_count` | 未声明 |
| `POST` | `/api/v1/webhooks/creem` | 未声明 | 200 | POST /api/v1/webhooks/creem | `error`, `error_code`, `error_id` | 未声明 |

## 缺口清单（请求体未声明，按分组）

其中 `POST` 且无请求体声明共 **56** 条 —— 这些是「agent 最难照着调」的部分，按 P0→P3 排，前 20 条是有界的下一轮增量：

- **P0**（7）：`/api/v1/attestation/cancel`、`/api/v1/attestation/renew`、`/api/v1/attestation/run-cycle`、`/api/v1/attestation/subscribe`、`/api/v1/registry/discover`、`/api/v1/trust`、`/api/v1/trust/digest`
- **P1**（8）：`/api/v1/evidence`、`/api/v1/evidence/verify-payload`、`/api/v1/intent/mandates`、`/api/v1/intent/mandates/evaluate`、`/api/v1/intent/mandates/verify`、`/api/v1/scan/attack-path`、`/api/v1/scan/client-config`、`/api/v1/ship-gate/run`
- **P2**（3）：`/api/v1/connectors`、`/api/v1/contributors`、`/api/v1/specialist/agents`
- **P3**（38）：`/api/v1/account/login`、`/api/v1/account/recharge`、`/api/v1/account/register`、`/api/v1/agent/scan`、`/api/v1/arena/scan`、`/api/v1/certify/fulfill`、`/api/v1/certify/request-payment`、`/api/v1/certify/request-payment-cny`、`/api/v1/checkout/create`、`/api/v1/export`、`/api/v1/export/sarif`、`/api/v1/export/sbom`…

## 复验方法（不要相信本文，相信命令）

```bash
# 1) 索引是否与契约一致（CI 用）
python scripts/gen_agent_api_index.py --check

# 2) 契约是否与实现一致（运行时路由双向 diff）
python scripts/openapi_contract.py --check

# 3) 线上真实可调（挑任一条 P0 路由）
curl -s --ssl-no-revoke --tlsv1.3 -H 'User-Agent: Mozilla/5.0' \
  https://aishield.tools/api/v1/digest | head -c 300
```

线上索引页：<https://aishield.tools/docs/agent-api-index.html>
