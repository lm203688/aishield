"""
api/ecosystem_request_bodies.py — 生态路由请求体声明表（agent 最需要的一批）

为什么需要这一层
────────────────
``api/openapi_spec.py`` 的契约有两条来源：

  1. curated —— 手工十来个端点，带完整 requestBody / 错误码 / 示例；
  2. runtime —— ``scripts/gen_openapi_spec.py`` 直调 handler 探出来的真实路由，
     schema **由真实响应反推**。

问题出在第 2 条上：探针只能拿到**响应**，拿不到**请求体**（它按空 body 探）。
于是 ``/api/v1/attestations/from-scan``、``/api/v1/agent-card/sign`` 这类
"智能体接入时最先要调"的端点，在 ``/openapi.json`` 与
``docs/agent-api-index.md`` 里都写着 **请求体未声明** —— 外部 agent 知道有这么
个端点，却不知道字段叫什么，照着调必然 400。

这里补的就是这块：**只给 requestBody，不动响应**。

它不是手抄，也不允许是编的
────────────────────────────
每条都带 ``source``（handler 所在文件）。``tests/test_ecosystem_request_contract.py``
会反过来验两件事：

  · 端点 + 动词必须真的在 ``api/openapi_runtime_paths.json`` 里（**不许有 phantom**）；
  · 每个字段名必须在该 ``source`` 文件里以 ``"字段名"`` 字面量出现
    （**不许有编出来的字段**）。

字段的 required / 默认值 / 枚举，逐条读自 handler 的 ``data.get(...)`` 与紧随其后
的校验分支；``note`` 里写明"为什么是这几个字段"，方便下一个人核对而不是信任。

维护约定
────────
新增路由时，如果它属于"agent 最需要的接入面"，在这里加一条即可 ——
``get_openapi_spec()`` 会把它并进契约，``docs/agent-api-index.md`` 的
"请求体未声明"计数会同步下降。忘记加不会导致测试红（这是**增量**声明表，
不是覆盖门禁）。
"""

from __future__ import annotations

# ── 通用片段 ──
_STR = {"type": "string"}
_URL = {"type": "string", "format": "uri"}
_OBJ = {"type": "object"}
_INT = {"type": "integer"}
_BOOL = {"type": "boolean"}


# ══════════════════════════════════════════════
#  声明表
#  键 = (path, verb)；值 = {required, properties, example, source, note}
# ══════════════════════════════════════════════
ECO_REQUEST_BODIES: dict[tuple[str, str], dict] = {

    # ── Trust Attestation：从扫描结果签凭证（agent 自证的主路径）──
    ("/api/v1/attestations/from-scan", "post"): {
        "source": "api/trust_api.py",
        "note": "三字段里 scan_result + subject_url 缺失即 400；subject_type 有默认值 'tool'。",
        "required": ["scan_result", "subject_url"],
        "properties": {
            "scan_result": {**_OBJ, "description": "扫描器输出（须含 summary.overall_score，否则按 0 分签出 critical 凭证）"},
            "subject_url": {**_URL, "description": "被证明主体的 URL（仓库 / 工具主页）"},
            "subject_type": {
                **_STR, "default": "tool",
                "enum": ["tool", "agent", "server"],
                "description": "主体类型",
            },
        },
        "example": {
            "scan_result": {"summary": {"overall_score": 92, "critical": 0, "high": 0}},
            "subject_url": "https://github.com/example/tool",
            "subject_type": "tool",
        },
    },

    # ── Trust Attestation：验证 ──
    ("/api/v1/attestations/verify", "post"): {
        "source": "api/trust_api.py",
        "note": "attestation_id 缺失即 400；online_verification 默认 True（关掉则只做离线验签）。",
        "required": ["attestation_id"],
        "properties": {
            "attestation_id": {**_STR, "description": "凭证 ID"},
            "online_verification": {**_BOOL, "default": True, "description": "是否做在线吊销检查"},
        },
        "example": {"attestation_id": "att_xxxxxxxx", "online_verification": True},
    },

    # ── Trust Attestation：撤销 ──
    ("/api/v1/attestations/revoke", "post"): {
        "source": "api/trust_api.py",
        "note": "attestation_id 必需；reason 可选，只进审计。",
        "required": ["attestation_id"],
        "properties": {
            "attestation_id": {**_STR, "description": "凭证 ID"},
            "reason": {**_STR, "description": "撤销原因（可选）"},
        },
        "example": {"attestation_id": "att_xxxxxxxx", "reason": "superseded by v2"},
    },

    # ── Trust Attestation：手工签发（四字段全必填）──
    ("/api/v1/attestations", "post"): {
        "source": "api/trust_api.py",
        "note": "subject / verdict / coverage / attestation 四者缺一即 400；issuer 与 expires_at 可选。",
        "required": ["subject", "verdict", "coverage", "attestation"],
        "properties": {
            "subject": {**_OBJ, "description": "主体描述"},
            "verdict": {**_STR, "description": "结论（如 pass / fail）"},
            "coverage": {**_OBJ, "description": "覆盖范围"},
            "attestation": {**_OBJ, "description": "证据体"},
            "issuer": {**_STR, "description": "签发方（可选）"},
            "expires_at": {"type": "string", "format": "date-time", "description": "过期时间（可选）"},
        },
        "example": {
            "subject": {"type": "tool", "url": "https://github.com/example/tool"},
            "verdict": "pass",
            "coverage": {"rules": 264},
            "attestation": {"score": 92},
        },
    },

    # ── Trust：自动签发（分数不够则 200 且不签发）──
    ("/api/v1/trust/auto", "post"): {
        "source": "api/trust_api.py",
        "note": "scan_result 也可写作 scan_report；命中即自动评分，≥80 才签（否则 200 + success=false）。",
        "required": ["scan_result"],
        "properties": {
            "scan_result": {**_OBJ, "description": "扫描结果（别名 scan_report）"},
        },
        "example": {"scan_result": {"summary": {"overall_score": 92}}},
    },

    # ── Trust：手工认证 ──
    ("/api/v1/trust/certify", "post"): {
        "source": "api/trust_api.py",
        "note": "source_url 可由 repository 顶替，scan_report 可由 scan_result 顶替；两者都缺即 400。",
        "required": ["source_url", "scan_report"],
        "properties": {
            "source_url": {**_URL, "description": "来源 URL（别名 repository）"},
            "scan_report": {**_OBJ, "description": "扫描报告（别名 scan_result）"},
        },
        "example": {
            "source_url": "https://github.com/example/tool",
            "scan_report": {"summary": {"overall_score": 92}},
        },
    },

    # ── Trust：验证信封（三选一的入参）──
    ("/api/v1/trust/verify", "post"): {
        "source": "api/trust_api.py",
        "note": "src / source_url / tool 任一即可（handler 内部按此优先级取）；type 可选。",
        "required": ["src"],
        "properties": {
            "src": {**_STR, "description": "被验证对象（别名 source_url / tool）"},
            "type": {**_STR, "description": "信封类型（可选）"},
        },
        "example": {"src": "https://github.com/example/tool"},
    },

    # ── Agent Card：签名 ──
    ("/api/v1/agent-card/sign", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "card 可为空对象（handler 用 `or {}` 兜底）；trust_score 可选，写进签名体。",
        "required": [],
        "properties": {
            "card": {**_OBJ, "description": "agent card 主体（可空）"},
            "trust_score": {"type": "number", "description": "信任评分（可选）"},
        },
        "example": {
            "card": {"name": "DemoAgent", "url": "https://demo.example/agent",
                     "capabilities": {"supported": ["scan"]}},
            "trust_score": 88,
        },
    },

    # ── Agent Card：验签 ──
    ("/api/v1/agent-card/verify", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "card 可空；public_key 不传则回落到 card 内嵌公钥。",
        "required": [],
        "properties": {
            "card": {**_OBJ, "description": "已签名的 agent card"},
            "public_key": {**_STR, "description": "验签公钥（可选）"},
        },
        "example": {"card": {"name": "DemoAgent", "aishield": {"sig": "..."}}},
    },

    # ── Agent Card：导出身份 ──
    ("/api/v1/agent-card/identity", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "与 sign 同形：card 可空，trust_score 可选。",
        "required": [],
        "properties": {
            "card": {**_OBJ, "description": "agent card"},
            "trust_score": {"type": "number", "description": "信任评分（可选）"},
        },
        "example": {"card": {"name": "DemoAgent"}, "trust_score": 88},
    },

    # ── 责任链：开链 ──
    ("/api/v1/chain", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "chain_id 可选，不传由服务端生成。",
        "required": [],
        "properties": {
            "chain_id": {**_STR, "description": "责任链 ID（可选）"},
        },
        "example": {"chain_id": "chain_2026_10_06"},
    },

    # ── 协议桥：归一化 ──
    ("/api/v1/protocol/normalize", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "protocol 是归一化的输入协议名；payload 可空，handler 用 `or {}` 兜底。",
        "required": ["protocol"],
        "properties": {
            "protocol": {**_STR, "description": "源协议名（如 mcp / a2a / openai）"},
            "payload": {**_OBJ, "description": "待归一化载荷（可选）"},
        },
        "example": {"protocol": "mcp", "payload": {"jsonrpc": "2.0", "method": "tools/list"}},
    },

    # ── 协议桥：翻译 ──
    ("/api/v1/protocol/translate", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "target 目标协议必需；from_protocol 也可写作 source；payload 可空。",
        "required": ["target"],
        "properties": {
            "target": {**_STR, "description": "目标协议名"},
            "payload": {**_OBJ, "description": "待翻译载荷（可选）"},
            "from_protocol": {**_STR, "description": "源协议（别名 source，可选）"},
        },
        "example": {"target": "a2a", "from_protocol": "mcp", "payload": {}},
    },

    # ── 身份：领注册凭据（必须绑定 owner）──
    ("/api/v1/identity/registration-token", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "owner 也可写作 agent_id；缺失即 400。凭据明文只在响应里出现一次，服务端只存 sha256。",
        "required": ["owner"],
        "properties": {
            "owner": {**_STR, "description": "凭据归属方（别名 agent_id）"},
            "ttl_seconds": {**_INT, "description": "有效期秒数（可选，非整数即 400）"},
        },
        "example": {"owner": "team-acme", "ttl_seconds": 3600},
    },

    # ── 身份：注册（必须带一次性凭据）──
    ("/api/v1/identity/register", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "name / owner / registration_token 三者缺一即 401 或 400；registration_token 注册时即消费，一次性。",
        "required": ["name", "owner", "registration_token"],
        "properties": {
            "name": {**_STR, "description": "Agent 名称"},
            "owner": {**_STR, "description": "所有者标识（必须与凭据签发的 owner 一致，别名 agent_id）"},
            "registration_token": {**_STR, "description": "一次性注册凭据（别名 token）"},
            "did": {**_STR, "description": "指定 DID（可选，非字符串即 400）"},
            "public_key": {**_STR, "description": "Agent 公钥（可选）"},
            "capabilities": {
                "type": "array", "items": {"type": "string"},
                "description": "能力列表（可选，默认空数组）",
            },
        },
        "example": {
            "name": "MySecurityAgent", "owner": "team-acme",
            "registration_token": "rt_xxxxxxxx", "capabilities": ["scan"],
        },
    },

    # ── 身份凭证：签发 ──
    ("/api/v1/identity/credentials/issue", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "did / owner / identity_token 三者缺一即 400。注意不是 registration_token —— 它在 register() 里已被消费，拿它换 VC 必然 401。",
        "required": ["did", "owner", "identity_token"],
        "properties": {
            "did": {**_STR, "description": "Agent DID"},
            "owner": {**_STR, "description": "所有者标识（须与注册记录一致，否则 403）"},
            "identity_token": {**_STR, "description": "身份凭证签发令牌（注册成功时一次性返回）"},
            "claims": {**_OBJ, "description": "自定义声明（可选）"},
            "ttl": {**_INT, "default": 86400, "description": "有效期秒数（可选）"},
        },
        "example": {"did": "did:aishield:abc123", "owner": "team-acme",
                    "identity_token": "it_xxxxxxxx"},
    },

    # ── 身份凭证：验证（公开，离线可完成）──
    ("/api/v1/identity/credentials/verify", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "只需 token；验签离线可完成，吊销检查是唯一在线依赖。",
        "required": ["token"],
        "properties": {
            "token": {**_STR, "description": "待验证的凭证 token"},
        },
        "example": {"token": "vc_payload.signature"},
    },

    # ── 身份凭证：除销（仅属主）──
    ("/api/v1/identity/credentials/revoke", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "did / owner / credential_id 三者缺一即 400；owner 不匹配即 403。",
        "required": ["did", "owner", "credential_id"],
        "properties": {
            "did": {**_STR, "description": "Agent DID"},
            "owner": {**_STR, "description": "所有者标识"},
            "credential_id": {**_STR, "description": "凭证 ID"},
        },
        "example": {"did": "did:aishield:abc123", "owner": "team-acme",
                    "credential_id": "vc_xxxxxxxx"},
    },

    # ── ERC-8004 包装 ──
    ("/api/v1/identity/erc8004/wrap", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "wallet_address 也可写作 address，缺失即 400；chain_id 默认 1，非整数即 400。",
        "required": ["wallet_address"],
        "properties": {
            "wallet_address": {**_STR, "description": "钱包地址（别名 address）"},
            "chain_id": {**_INT, "default": 1, "description": "链 ID"},
        },
        "example": {"wallet_address": "0x0000000000000000000000000000000000000000", "chain_id": 1},
    },

    # ── KYA 导出 ──
    ("/api/v1/identity/kyad/export", "post"): {
        "source": "api/ecosystem_api.py",
        "note": "与 agent-card/sign 同形：card 可空，trust_score 可选。",
        "required": [],
        "properties": {
            "card": {**_OBJ, "description": "agent card"},
            "trust_score": {"type": "number", "description": "信任评分（可选）"},
        },
        "example": {"card": {"name": "DemoAgent"}, "trust_score": 88},
    },

    # ── Agent 基础设施开源扫描：单目标 ──
    ("/api/v1/agent-infra/scan", "post"): {
        "source": "api/connectors_api.py",
        "note": "六字段白名单，只取非 None 的；全空即 400。定位方式三选一：repo_url / local_path / files。",
        "required": [],
        "properties": {
            "name": {**_STR, "description": "目标名称"},
            "repo_url": {**_URL, "description": "仓库 URL（三选一）"},
            "local_path": {**_STR, "description": "本地路径（三选一）"},
            "files": {"type": "array", "items": {**_STR}, "description": "文件列表（三选一）"},
            "platform_id": {**_STR, "description": "归属平台 ID（可选）"},
            "tool_type": {**_STR, "description": "工具类型（可选）"},
        },
        "example": {"name": "example-mcp", "repo_url": "https://github.com/example/mcp"},
    },

    # ── Agent 基础设施开源扫描：组合 ──
    ("/api/v1/agent-infra/scan-portfolio", "post"): {
        "source": "api/connectors_api.py",
        "note": "specs 必须是非空列表（元素形状同 /agent-infra/scan），否则 400。",
        "required": ["specs"],
        "properties": {
            "specs": {
                "type": "array",
                "items": {**_OBJ},
                "description": "扫描目标列表，每项形状同 /api/v1/agent-infra/scan",
            },
        },
        "example": {"specs": [{"name": "example-mcp",
                               "repo_url": "https://github.com/example/mcp"}]},
    },
}


def as_openapi_request_bodies() -> dict[str, dict]:
    """转成 {path: {verb: requestBody}}，供 openapi_spec 注入。"""
    out: dict[str, dict] = {}
    for (path, verb), spec in ECO_REQUEST_BODIES.items():
        rb = {
            "required": bool(spec.get("required")),
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": spec["properties"],
                    },
                },
            },
            "x-aishield-declared-by": "api/ecosystem_request_bodies.py",
        }
        req = spec.get("required") or []
        if req:
            rb["content"]["application/json"]["schema"]["required"] = list(req)
        if spec.get("example"):
            rb["content"]["application/json"]["example"] = spec["example"]
        out.setdefault(path, {})[verb] = rb
    return out


if __name__ == "__main__":  # 自证：不依赖任何第三方，打印条目数
    n = len(ECO_REQUEST_BODIES)
    files = sorted({v["source"] for v in ECO_REQUEST_BODIES.values()})
    print(f"生态请求体声明 {n} 条，来自 {len(files)} 个 handler：")
    for f in files:
        print("  -", f)
