# Trust Attestation 快速上手（Agent 自证凭据）

> 目标读者：要让自己的 agent / MCP server / 工具**可被第三方独立验证**的开发者。
> 读完之后你能做到：签出一枚跟扫描结果绑定的凭据，让别人只凭公钥离线验签，
> 且**不需要信任 AIShield 的在线服务**。

本文里的每个字段名都不是写来给人看的 —— 它们同时被
`api/ecosystem_request_bodies.py` 声明进 OpenAPI 契约，并由
`tests/test_ecosystem_request_contract.py` 逐字段回查 handler 源码。
字段对不上，测试会红。

---

## 0. 先分清三件事

| 你想要的 | 该调的端点 | 产物 |
| --- | --- | --- |
| 「我扫过了，这是我的结论」 | `POST /api/v1/attestations/from-scan` | 一枚与扫描结果绑定的 attestation |
| 「这枚凭据是真的吗」 | `POST /api/v1/attestations/verify` | 验签结果（离线可完成） |
| 「我不要了」 | `POST /api/v1/attestations/revoke` | 吊销记录（在线检查才会看到） |

**边界（请当作产品说明的一部分读）**：

- 凭据证明的是**「某个主体在某时刻、在某一套规则集下被扫描出的结论」**，
  不是「这个工具是安全的」。扫描规则集会变，结论有保质期。
- 凭证的信任根是**签发者公钥**。第三方不校验签发者身份时，凭据只能证明
  「有人签了它」。验证方必须自己决定信任哪个签发者 —— 这一步无法被服务代替。

---

## 1. 从扫描结果签一枚凭据（最常用）

```bash
curl -sS -X POST https://aishield.tools/api/v1/attestations/from-scan \
  -H 'Content-Type: application/json' \
  -d '{
    "scan_result": {"summary": {"overall_score": 92, "critical": 0, "high": 1}},
    "subject_url": "https://github.com/your-org/your-tool",
    "subject_type": "tool"
  }'
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `scan_result` | ✅ | 扫描器输出。**必须含 `summary.overall_score`** |
| `subject_url` | ✅ | 被证明的主体（仓库 / 工具主页） |
| `subject_type` | | `tool`（默认）/ `agent` / `server` |

> ⚠️ **`summary.overall_score` 缺失不会报错，会按 0 分算。**
> 于是你会拿到一枚 `risk = critical` 的凭据，还以为是成功的。这是本仓
> `api/trust_api.py` 的实际行为，不是本文的推测：
> `create_attestation_from_scan()` 取不到分数即回落 0。
> 所以 `scripts/integrate_trust_attestation.py` 在本地就 fail-closed —— 缺字段直接
> `return 2`，绝不把"设备问题"签成"产品很危险"。CI 里请照抄这个姿势。

成功返回 `201`，`attestation` 就是你之后要验证/吊销的那枚凭据。

---

## 2. 验证（离线可完成）

```bash
curl -sS -X POST https://aishield.tools/api/v1/attestations/verify \
  -H 'Content-Type: application/json' \
  -d '{"attestation_id": "att_xxxxxxxx", "online_verification": true}'
```

- `attestation_id` 必填；`online_verification` 默认 `true`。
- 关掉 `online_verification` 只做离线验签 —— **吊销状态就查不到了**。
  离线可完成是有代价的，别把它当成"更快"。

---

## 3. 吊销

```bash
curl -sS -X POST https://aishield.tools/api/v1/attestations/revoke \
  -H 'Content-Type: application/json' \
  -d '{"attestation_id": "att_xxxxxxxx", "reason": "superseded by v2"}'
```

`reason` 可选，只进审计记录。

---

## 4. 手工签发（不想走扫描时）

`POST /api/v1/attestations` 要求 `subject` / `verdict` / `coverage` / `attestation`
**四个字段缺一不可**，`issuer` 与 `expires_at` 可选。

```bash
curl -sS -X POST https://aishield.tools/api/v1/attestations \
  -H 'Content-Type: application/json' \
  -d '{
    "subject": {"type": "tool", "url": "https://github.com/your-org/your-tool"},
    "verdict": "pass",
    "coverage": {"scanner": "aishield", "profile": "default"},
    "attestation": {"score": 92},
    "expires_at": "2027-01-01T00:00:00Z"
  }'
```

---

## 5. 身份锚点：先拿凭据，再注册

注册**不再是裸端点**。没带一次性注册凭据的请求会直接 `401` —— 这是刻意的：
否则注册表只有写入没有回收，会留下一堆谁也删不掉的脏 DID。

```bash
# ① 领注册凭据（绑定 owner，明文只在这一次响应里出现）
curl -sS -X POST https://aishield.tools/api/v1/identity/registration-token \
  -H 'Content-Type: application/json' \
  -d '{"owner": "team-acme", "ttl_seconds": 3600}'

# ② 用它注册（凭据在 register() 里被一次性消费）
curl -sS -X POST https://aishield.tools/api/v1/identity/register \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "MySecurityAgent",
    "owner": "team-acme",
    "registration_token": "rt_xxxxxxxx",
    "capabilities": ["scan"]
  }'
```

注册成功会**一并返回一枚身份凭证签发令牌（identity token，一次性、绑定 did+owner）**。

⚠️ 别拿 `registration_token` 去换身份凭证 —— 它在注册时就被消费了，必然 `401`
（这不是猜测，是本仓 #367 第一版实测复现的坑）。两条路径各有各的凭据：

```bash
# ③ 签发可验证身份凭证
curl -sS -X POST https://aishield.tools/api/v1/identity/credentials/issue \
  -H 'Content-Type: application/json' \
  -d '{"did": "did:aishield:abc123", "owner": "team-acme",
       "identity_token": "it_xxxxxxxx", "ttl": 86400}'

# ④ 公开验证（验签离线可完成）
curl -sS -X POST https://aishield.tools/api/v1/identity/credentials/verify \
  -H 'Content-Type: application/json' \
  -d '{"token": "vc_payload.signature"}'

# ⑤ 除销（仅属主；owner 不匹配即 403）
curl -sS -X POST https://aishield.tools/api/v1/identity/credentials/revoke \
  -H 'Content-Type: application/json' \
  -d '{"did": "did:aishield:abc123", "owner": "team-acme",
       "credential_id": "vc_xxxxxxxx"}'
```

---

## 6. 接进你的仓库（一条命令）

本仓自带检测 + 签发 + CI 片段生成的工具，零第三方依赖：

```bash
# 看看你的项目属于哪类框架、配置面长什么样（不会改任何文件）
python scripts/integrate_trust_attestation.py detect .

# 真去签一枚（缺 summary.overall_score 或 --subject-url 直接退出码 2，不签）
python scripts/integrate_trust_attestation.py attest . \
  --scan-result scan.json --subject-url https://github.com/your-org/your-tool

# 打印一段可直接贴进 .github/workflows/ 的步骤（含 expires_at 过期即红的断言）
python scripts/integrate_trust_attestation.py emit-action . \
  --subject-url https://github.com/your-org/your-tool
```

`detect` 的框架指纹是**逐行锚定 import 语句**得出的，不是全文子串匹配 ——
否则一个只在文档里提到 CrewAI 的仓库会把自己误判成 CrewAI 使用者。

---

## 7. 验证你自己的集成

```bash
# 契约里这些端点的请求体必须已声明（0 = 契约滞后）
python scripts/gen_agent_api_index.py --check

# 我声明的字段必须都能在 handler 源码里找到（防"编出来的 schema"）
python -m unittest tests.test_ecosystem_request_contract -v

# 签发链路必须真的能跑（钉死"schema 文件随仓库发布"）
python -m unittest tests.test_trust_attestation_schema -v
```

---

## 8. 权威值与索引（别抄数字）

- 当前规则数、工具数等**权威值**：`GET /api/v1/health` （见 `rules_breakdown`）。
- 全部端点的可读索引：`docs/agent-api-index.md` → 线上 `/docs/agent-api-index.html`。
  该索引列出每条操作的**请求体字段**；"请求体未声明"计数是真缺口，不是修辞。
- 机器可读契约：`/openapi.json`。

> 本文刻意不写死规则数。写死的数字会过期，而读者往往不会去看它过期了没有 ——
> 这正是本仓 `rule_count_gate` 存在的原因。
