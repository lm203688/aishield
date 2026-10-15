"""AIShield — 个人 Agent 平台注册表与能力矩阵 (v4.8.1).

目的：让个人 Agent 治理层（PAI / 预算 / 行动溯源）**平台中立**，
不再绑死某个具体平台（Muse / Grok Bot 都只是接入方之一）。

背景 (2026-09-24 一手事实)：
- Meta Muse：muse.ai 大陆连接超时；大陆用户无法直接访问。
- xAI Grok Bot：api.x.ai / x.com 大陆连接超时；SuperGrok 订阅 $30 起。
- OpenAI：OpenAI Operator / ChatGPT Agent 大陆同样不通。
- 字节 Coze / 豆包 / 腾讯元宝 / 百度文心 / 阿里通义：大陆可达。

接入路径 5 类（platform_registry 里每个平台都标注）：
1. **mcp** —— MCP 协议（Microsoft/Anthropic 2024 标准），我们已就绪
2. **openai_compat** —— OpenAI 兼容 API（xAI / DeepSeek / 智谱 / Kimi / Groq 等）
3. **connector_official** —— 平台官方 connector 平台（Muse / ChatGPT / Grok Bot）
4. **native_sdk** —— 平台私有 SDK（Coze / 元宝 / 豆包等）
5. **browser_agent** —— 无 API 浏览器操作（Grok Bot / OpenAI Operator / 类 Claude Computer Use）

治理缺口矩阵：每个平台内置了哪些治理能力，缺哪些由我们补齐。
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from typing import Any

_LOCK = threading.RLock()

# ══════════════════════════════════════════════════════════════
# 平台注册表 (2026-09-24 快照，40+ 平台)
# ══════════════════════════════════════════════════════════════
# 字段说明：
#   id              —— 平台唯一标识
#   name            —— 展示名
#   vendor          —— 厂商
#   family          —— consumer(消费级) / developer(开发者) / enterprise(企业级)
#   cny_accessible  —— 大陆直连可达性 (verified_blocked / reachable / regional_only)
#   access_paths    —— 可用接入路径（数组，见 docstring 5 类）
#   pricing         —— 订阅/计费摘要（USD/CNY）
#   governance      —— 平台内置治理能力（数组）
#   gaps            —— 缺失、需要 AIShield 补齐的能力
#   launched        —— 上线/开放日期
#   notes           —— 备注
# ══════════════════════════════════════════════════════════════

PLATFORMS: dict[str, dict[str, Any]] = {
    # ─────────────────────────────────────────────────────
    # 海外消费级 agent（大陆不可达，但海外用户 / 双栈需要）
    # ─────────────────────────────────────────────────────
    "meta-muse": {
        "id": "meta-muse",
        "name": "Meta Muse",
        "vendor": "Meta",
        "family": "consumer",
        "cny_accessible": "verified_blocked",  # 2026-09-24 curl timeout 确认
        "access_paths": ["connector_official", "mcp"],
        "platform_url": "https://muse.ai",
        "developer_url": "https://muse.ai/platform",
        "launched": "2026-09-08",
        "connector_opened": "2026-09-18",
        "pricing": "免费 (iOS 免费榜 #1, 13 天 250 万下载)",
        "payment": "Stripe Link (一次性卡号)",
        "governance": [
            "secure_vm_isolation", "sentinel_supervisor",
            "stripe_link_payment", "sensitive_action_confirm",
            "internal_audit_trail",
        ],
        "gaps": [
            "portable_personal_identity",   # Meta 账号体系封闭
            "cumulative_budget_governance",  # Stripe Link 只管单次
            "target_site_risk_scoring",
            "connector_independent_review",
            "user_level_dispute_receipt",
        ],
        "notes": "大陆用户通过官方 connector 平台接入无解；MCP 通道备用。",
    },

    "xai-grok-bot": {
        "id": "xai-grok-bot",
        "name": "Grok Bot",
        "vendor": "xAI",
        "family": "consumer",
        "cny_accessible": "verified_blocked",  # x.com / api.x.ai 都超时
        "access_paths": ["openai_compat", "connector_official", "browser_agent"],
        "platform_url": "https://x.com",
        "developer_url": "https://docs.x.ai",
        "api_base": "https://api.x.ai/v1",
        "launched": "2026-08-11",
        "connector_opened": "2026-08-29",  # X connector
        "enterprise_opened": "2026-09-03",
        "pricing": "SuperGrok $30/mo, Plus $100, Heavy $300；Cursor 系列含",
        "api_pricing": "fast $0.20/1M in；4.3 $1.25/1M；4.6 $2/1M in $6/1M out",
        "payment": "xAI 订阅 + X API credits (付费用户免费额度)",
        "governance": [
            "cloud_computer_isolation", "persistent_agent_state",
            "approval_before_action", "enterprise_audit_controls",
        ],
        "gaps": [
            "portable_personal_identity",
            "personal_budget_governance",
            "third_party_action_dispute",
            "off_platform_audit_trail",
        ],
        "notes": (
            "Grok Bot 是 standing agents（登录你已有的工具，含无 API 场景）。"
            "xAI API 走 OpenAI 兼容模式，我们最容易通过 openai_compat 通道接入。"
        ),
    },

    "xai-grok-api": {
        "id": "xai-grok-api",
        "name": "Grok API (xAI)",
        "vendor": "xAI",
        "family": "developer",
        "cny_accessible": "verified_blocked",
        "access_paths": ["openai_compat"],
        "platform_url": "https://api.x.ai/v1",
        "developer_url": "https://docs.x.ai",
        "launched": "2025-07-08",  # Grok 4.5
        "pricing": "grok-4.1-fast $0.20/1M in；grok-4.3 $1.25；grok-4.6 $2/1M in $6/1M out",
        "payment": "按量计费",
        "governance": ["api_key_auth", "data_retention_policy"],
        "gaps": [
            "agent_level_governance", "tool_call_audit",
            "user_personal_identity",
        ],
        "notes": "纯开发者 API；Grok Build（终端 coding agent）通过 API 走。",
    },

    # ───────────────────────────────────────────────────────────────
    # 2026-09-24 v4.8.2：agent 基础设施开源生态（laya / nasiko / agent-desktop）
    # + NVIDIA 开发者平台 —— 围绕核心目标的多维接入底座
    # ───────────────────────────────────────────────────────────────
    "nvidia-dev": {
        "id": "nvidia-dev",
        "name": "NVIDIA Developer Platform (NGC / NIM / NeMo)",
        "vendor": "NVIDIA",
        "family": "developer",
        # NGC Catalog / NIM / NeMo Microservices 多需海外或代理；部分镜像国内可下
        "cny_accessible": "regional_only",
        "access_paths": ["native_sdk", "connector_official", "mcp"],
        "platform_url": "https://developer.nvidia.com",
        "developer_url": "https://docs.nvidia.com",
        # NIM / NeMo 推理与编排 API（OpenAI 兼容风格）
        "api_base": "https://integrate.api.nvidia.com/v1",
        "launched": "2024-01-01",
        "pricing": "NGC 免费层 + NIM 按量；DGX / AI Factory 企业",
        "payment": "按量 + 企业合约",
        "governance": [
            "enterprise_sso", "model_card_publish", "artifact_signing",
        ],
        "gaps": [
            "portable_personal_identity",
            "cumulative_budget_governance",
            "user_level_dispute_receipt",
            "target_site_risk_scoring",
            "connector_independent_review",
        ],
        "notes": (
            "NVIDIA 开发者平台（NGC Catalog / NIM 微服务 / NeMo / AI Blueprint）"
            "是 agent 基础设施的核心算力与模型底座。AIShield 可经 native_sdk "
            "封装其推理/编排 API，或经 MCP 把 NIM 微服务当工具暴露；大陆需代理访问。"
        ),
    },

    "laya": {
        "id": "laya",
        "name": "Laya (本地决策/护栏模型)",
        "vendor": "OSS",
        "family": "infrastructure",
        "cny_accessible": "reachable",  # 开源，本地可跑
        "access_paths": ["mcp", "native_sdk"],
        "platform_url": "https://github.com/lm203688/laya",
        "developer_url": "https://github.com/lm203688/laya",
        "launched": "2026-09-22",
        "pricing": "开源 (MIT)",
        "payment": "免费",
        "governance": ["local_inference", "zero_cost_guardrail"],
        "gaps": [
            "portable_personal_identity",
            "cumulative_budget_governance",
            "user_level_dispute_receipt",
            "connector_independent_review",
        ],
        "notes": (
            "Laya 是本地零成本决策/护栏模型（ModernBERT + 决策头），已以 MCP "
            "server 形式接入 AIShield 作本地初筛层。属 agent 基础设施类项目，"
            "AIShield 通过开源扫描 + 封装双层接入生态。"
        ),
    },

    "nasiko": {
        "id": "nasiko",
        "name": "Nasiko (agent 基础设施)",
        "vendor": "OSS",
        "family": "infrastructure",
        "cny_accessible": "reachable",
        "access_paths": ["mcp", "connector_official"],
        "platform_url": "https://github.com/search?q=nasiko+agent+infrastructure",
        "developer_url": "https://github.com/search?q=nasiko+agent+infrastructure",
        "launched": "2026-01-01",
        "pricing": "开源",
        "payment": "免费",
        "governance": ["agent_runtime"],
        "gaps": [
            "portable_personal_identity",
            "cumulative_budget_governance",
            "user_level_dispute_receipt",
            "target_site_risk_scoring",
            "connector_independent_review",
        ],
        "notes": (
            "Nasiko 是 agent 基础设施类开源项目。AIShield 将其纳入 agent 基础设施 "
            "开源扫描目标，通过封装（MCP 适配器）与二次研发接入生态。"
        ),
    },

    "agent-desktop": {
        "id": "agent-desktop",
        "name": "Agent Desktop (桌面 agent 基础设施)",
        "vendor": "OSS",
        "family": "infrastructure",
        "cny_accessible": "reachable",
        "access_paths": ["mcp", "native_sdk"],
        "platform_url": "https://github.com/search?q=agent-desktop+infrastructure",
        "developer_url": "https://github.com/search?q=agent-desktop+infrastructure",
        "launched": "2026-01-01",
        "pricing": "开源",
        "payment": "免费",
        "governance": ["desktop_agent_runtime"],
        "gaps": [
            "portable_personal_identity",
            "cumulative_budget_governance",
            "user_level_dispute_receipt",
            "target_site_risk_scoring",
            "connector_independent_review",
        ],
        "notes": (
            "Agent Desktop 是桌面端 agent 基础设施开源项目。AIShield 将其纳入 "
            "agent 基础设施开源扫描目标，通过封装与二次研发接入生态。"
        ),
    },

    "openai-chatgpt-agent": {
        "id": "openai-chatgpt-agent",
        "name": "ChatGPT Agent",
        "vendor": "OpenAI",
        "family": "consumer",
        "cny_accessible": "verified_blocked",
        "access_paths": ["openai_compat", "connector_official"],
        "platform_url": "https://chatgpt.com",
        "developer_url": "https://platform.openai.com",
        "launched": "2025-07",
        "pricing": "Plus $20 / Pro $200 / Enterprise",
        "payment": "Stripe",
        "governance": ["account_login", "action_confirm", "gpt_app_connectors"],
        "gaps": [
            "portable_personal_identity",
            "cross_platform_budget",
            "user_dispute_receipt",
        ],
        "notes": "GPT Apps 平台已开放第三方 connector。",
    },

    "openai-operator": {
        "id": "openai-operator",
        "name": "OpenAI Operator",
        "vendor": "OpenAI",
        "family": "consumer",
        "cny_accessible": "verified_blocked",
        "access_paths": ["openai_compat", "browser_agent"],
        "launched": "2025-01-23",
        "pricing": "Plus 可用 / Pro 无限",
        "payment": "Stripe",
        "governance": ["account_login", "safe_mode_confirm", "no_credit_card_save"],
        "gaps": [
            "personal_identity", "cumulative_budget",
            "action_dispute_receipt",
        ],
        "notes": "浏览器代操 agent；credit card save 是显式拒绝的。",
    },

    "anthropic-claude-agent": {
        "id": "anthropic-claude-agent",
        "name": "Claude (Anthropic)",
        "vendor": "Anthropic",
        "family": "consumer",
        "cny_accessible": "verified_blocked",
        "access_paths": ["openai_compat", "connector_official", "browser_agent"],
        "launched": "2024-03",
        "pricing": "Pro $20 / Max $100-200",
        "payment": "Stripe",
        "governance": ["account_login", "computer_use_preview", "project_context"],
        "gaps": [
            "personal_identity", "budget_governance", "dispute_receipt",
        ],
        "notes": "Computer Use 是浏览器 agent 模式。",
    },

    "google-gemini": {
        "id": "google-gemini",
        "name": "Gemini",
        "vendor": "Google",
        "family": "consumer",
        "cny_accessible": "verified_blocked",
        "access_paths": ["openai_compat", "connector_official"],
        "launched": "2023-02",
        "pricing": "Free / Plus $19.99 / Pro $249.99",
        "payment": "Google Play / Web",
        "governance": ["google_account", "gmail_integration"],
        "gaps": [
            "personal_identity", "cross_platform_budget", "action_dispute",
        ],
        "notes": "大陆 Google 全线不通。",
    },

    # ─────────────────────────────────────────────────────
    # 海外开发者 API（大陆可能通过代理，取决于 API 主机）
    # ─────────────────────────────────────────────────────
    "xai-api-vertex": {
        "id": "xai-api-vertex",
        "name": "Grok on Google Vertex AI",
        "vendor": "Google Cloud / xAI",
        "family": "developer",
        "cny_accessible": "regional_only",  # 国内云可访问，但 Vertex 需海外账号
        "access_paths": ["openai_compat"],
        "launched": "2026-08-21",
        "pricing": "按 Vertex 定价",
        "notes": "Grok 通过 Vertex Model Garden 部署；ZDR 可选。",
    },

    "groq": {
        "id": "groq",
        "name": "Groq API",
        "vendor": "Groq",
        "family": "developer",
        "cny_accessible": "regional_only",
        "access_paths": ["openai_compat"],
        "launched": "2024-06",
        "pricing": "免费层 + 付费",
        "notes": "开源模型推理；Llama / Mixtral。",
    },

    "cerebras": {
        "id": "cerebras",
        "name": "Cerebras Cloud",
        "vendor": "Cerebras",
        "family": "developer",
        "cny_accessible": "regional_only",
        "access_paths": ["openai_compat"],
        "launched": "2024-10",
        "notes": "Llama 系。",
    },

    "fireworks": {
        "id": "fireworks",
        "name": "Fireworks AI",
        "vendor": "Fireworks",
        "family": "developer",
        "cny_accessible": "regional_only",
        "access_paths": ["openai_compat"],
        "launched": "2023-05",
        "notes": "开源模型托管。",
    },

    "together": {
        "id": "together",
        "name": "Together AI",
        "vendor": "Together",
        "family": "developer",
        "cny_accessible": "regional_only",
        "access_paths": ["openai_compat"],
        "launched": "2022-04",
        "notes": "开源模型托管。",
    },

    # ─────────────────────────────────────────────────────
    # 国内消费级 agent（大陆可达，重点接入方向）
    # ─────────────────────────────────────────────────────
    "bytedance-coze": {
        "id": "bytedance-coze",
        "name": "Coze (字节扣子)",
        "vendor": "字节跳动",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["native_sdk", "openai_compat", "connector_official", "mcp"],
        "platform_url": "https://www.coze.cn",
        "developer_url": "https://www.coze.cn/docs",
        "launched": "2023-07",
        "pricing": "开发者免费层 / 企业付费",
        "payment": "支付宝 / 微信 / 虎皮椒",
        "governance": [
            "workspace_isolation", "bot_publisher_review",
            "knowledge_base", "workflow_builder",
        ],
        "gaps": [
            "portable_personal_identity",
            "user_level_action_dispute",
            "connector_independent_review",
        ],
        "notes": "大陆唯一有官方 MCP 支持的 agent 平台（coze.cn/mcp）；接入优先级最高。",
    },

    "bytedance-doubao": {
        "id": "bytedance-doubao",
        "name": "豆包 (Doubao)",
        "vendor": "字节跳动",
        "family": "consumer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat", "native_sdk"],
        "platform_url": "https://www.doubao.com",
        "developer_url": "https://www.volcengine.com",
        "launched": "2023-11",
        "pricing": "免费 / 企业 API 按量",
        "payment": "支付宝 / 微信",
        "governance": ["volc_account", "workspace_context"],
        "gaps": [
            "personal_agent_identity", "agent_level_budget",
            "action_dispute",
        ],
        "notes": "字节 API 走 volcengine 平台。",
    },

    "bytedance-seedream": {
        "id": "bytedance-seedream",
        "name": "即梦 (Seedream)",
        "vendor": "字节跳动",
        "family": "consumer",
        "cny_accessible": "reachable",
        "access_paths": ["native_sdk"],
        "platform_url": "https://jimeng.jianying.com",
        "notes": "图像/视频生成 agent。",
    },

    "tencent-yuanbao": {
        "id": "tencent-yuanbao",
        "name": "腾讯元宝",
        "vendor": "腾讯",
        "family": "consumer",
        "cny_accessible": "reachable",
        "access_paths": ["native_sdk"],
        "platform_url": "https://yuanbao.tencent.com",
        "developer_url": "https://cloud.tencent.com/product/hunyuan",
        "launched": "2024-05",
        "pricing": "免费 / 企业 API",
        "payment": "微信支付",
        "governance": ["qq_wechat_account", "hunyuan_workspace"],
        "gaps": [
            "portable_personal_identity", "agent_budget_governance",
        ],
        "notes": "接入走混元 API + 微信登录。",
    },

    "baidu-ernie": {
        "id": "baidu-ernie",
        "name": "文心一言",
        "vendor": "百度",
        "family": "consumer",
        "cny_accessible": "reachable",
        "access_paths": ["native_sdk", "openai_compat"],
        "platform_url": "https://yiyan.baidu.com",
        "developer_url": "https://qianfan.bj.baidubce.com",
        "launched": "2023-03",
        "pricing": "免费 / 企业 API",
        "payment": "百度智能云计费",
        "governance": ["baidu_account", "qianfan_workspace"],
        "gaps": ["personal_identity", "cross_platform_budget"],
        "notes": "百智能云千帆。",
    },

    "baidu-duanwu": {
        "id": "baidu-duanwu",
        "name": "百度文心智能体平台",
        "vendor": "百度",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["native_sdk", "connector_official"],
        "launched": "2024-05",
        "notes": "百度智能体市场。",
    },

    "aliyun-tongyi": {
        "id": "aliyun-tongyi",
        "name": "通义千问 (Tongyi)",
        "vendor": "阿里巴巴",
        "family": "consumer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat", "native_sdk", "connector_official"],
        "platform_url": "https://tongyi.aliyun.com",
        "developer_url": "https://dashscope.aliyun.com",
        "launched": "2023-04",
        "pricing": "免费 / DashScope API 按量",
        "payment": "支付宝 / 云计费",
        "governance": ["aliyun_account", "dashscope_workspace"],
        "gaps": ["portable_personal_identity", "personal_budget"],
        "notes": "DashScope 走 OpenAI 兼容协议；百炼智能体市场。",
    },

    "kuaishou-kling": {
        "id": "kuaishou-kling",
        "name": "可灵 (Kling)",
        "vendor": "快手",
        "family": "consumer",
        "cny_accessible": "reachable",
        "access_paths": ["native_sdk"],
        "platform_url": "https://klingai.com",
        "notes": "视频生成 agent。",
    },

    "minimax": {
        "id": "minimax",
        "name": "MiniMax (海螺)",
        "vendor": "MiniMax",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat", "native_sdk"],
        "platform_url": "https://hailuo.cn",
        "developer_url": "https://platform.minimaxi.com",
        "launched": "2023-12",
        "notes": "Abab / 海螺 API。",
    },

    "moonshot-kimi": {
        "id": "moonshot-kimi",
        "name": "Kimi",
        "vendor": "月之暗面",
        "family": "consumer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat", "native_sdk"],
        "platform_url": "https://kimi.moonshot.cn",
        "developer_url": "https://platform.moonshot.cn",
        "launched": "2023-10",
        "notes": "长上下文；OpenAI 兼容。",
    },

    "zhipu-glm": {
        "id": "zhipu-glm",
        "name": "智谱 GLM",
        "vendor": "智谱 AI",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat", "native_sdk"],
        "platform_url": "https://chatglm.cn",
        "developer_url": "https://open.bigmodel.cn",
        "launched": "2023-08",
        "notes": "GLM-4 / 大模型开放平台。",
    },

    "deepseek": {
        "id": "deepseek",
        "name": "DeepSeek",
        "vendor": "深度求索",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat"],
        "platform_url": "https://chat.deepseek.com",
        "developer_url": "https://api.deepseek.com",
        "launched": "2024-05",
        "pricing": "V3 $0.27/1M in, R1 $0.55",
        "notes": "OpenAI 兼容；性价比最高的国内开发者 API。",
    },

    "stepfun": {
        "id": "stepfun",
        "name": "StepFun (阶跃星辰)",
        "vendor": "阶跃星辰",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat", "native_sdk"],
        "platform_url": "https://xiongchi.chat",
        "developer_url": "https://platform.stepfun.com",
        "notes": "通用 + 多模态。",
    },

    "baichuan": {
        "id": "baichuan",
        "name": "百川",
        "vendor": "百川智能",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat"],
        "platform_url": "https://baichuan-ai.com",
        "developer_url": "https://platform.baichuan-ai.com",
        "notes": "医疗 / 金融垂类。",
    },

    "01-ai": {
        "id": "01-ai",
        "name": "Yi (零一万物)",
        "vendor": "零一万物",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat", "native_sdk"],
        "platform_url": "https://yi.yiig.ai",
        "developer_url": "https://platform.lingyiwanwu.com",
        "notes": "Yi-Lightning。",
    },

    # ─────────────────────────────────────────────────────
    # Agent 平台（开发者建 agent、上架给 C 端）
    # ─────────────────────────────────────────────────────
    "dify": {
        "id": "dify",
        "name": "Dify",
        "vendor": "LangGenius",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat", "connector_official", "mcp"],
        "platform_url": "https://dify.ai",
        "launched": "2023-05",
        "notes": "开源 LLMOps 平台。",
    },

    "fastgpt": {
        "id": "fastgpt",
        "name": "FastGPT",
        "vendor": "labring",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["openai_compat", "native_sdk"],
        "platform_url": "https://fastgpt.io",
        "notes": "开源 LLMOps。",
    },

    "n8n": {
        "id": "n8n",
        "name": "n8n (工作流)",
        "vendor": "n8n GmbH",
        "family": "developer",
        "cny_accessible": "reachable",
        "access_paths": ["native_sdk", "mcp"],
        "platform_url": "https://n8n.io",
        "notes": "低代码工作流 + AI 节点。",
    },

    # ─────────────────────────────────────────────────────
    # Agent / 支付标准（不是平台，但常被提及）
    # ─────────────────────────────────────────────────────
    "aisa-agentpay": {
        "id": "aisa-agentpay",
        "name": "AIsa AgentPay Guard",
        "vendor": "AIsa",
        "family": "infrastructure",
        "cny_accessible": "regional_only",
        "access_paths": ["native_sdk"],
        "launched": "2026-09-10",
        "notes": (
            "Agent 支付 guard：quote-first / per-request / per-task / per-time 三层限额；"
            "已吸收进 AIShield SKILL_EXTRA 5 条支付/预算规则。"
        ),
    },

    "x402": {
        "id": "x402",
        "name": "x402 Protocol",
        "vendor": "Coinbase",
        "family": "infrastructure",
        "cny_accessible": "regional_only",
        "access_paths": ["openai_compat"],  # 走 HTTP 402 协议
        "launched": "2025",
        "notes": "HTTP 402 + USDC 支付标准。",
    },
}

PLATFORM_BY_ID: dict[str, dict[str, Any]] = {p["id"]: p for p in PLATFORMS.values()}

# 补齐所有平台必填字段（governance / gaps / access_paths / cny_accessible / family）
# 缺字段的开发者平台默认：governance=[], gaps=[], access_paths=[]（不推荐主动接入）
for _pid, _p in list(PLATFORMS.items()):
    _p.setdefault("governance", [])
    _p.setdefault("gaps", [])
    _p.setdefault("access_paths", [])
    _p.setdefault("cny_accessible", "unknown")
    _p.setdefault("family", "developer")
    _p.setdefault("launched", "unknown")
    _p.setdefault("notes", "")

# ══════════════════════════════════════════════════════════════
# AIShield 治理项（每个平台 gaps 里的 key 映射到具体能力）
# ══════════════════════════════════════════════════════════════

GOVERNANCE_PROVISIONS: dict[str, dict[str, str]] = {
    "portable_personal_identity":
        "PAI DID (did:key，自认证) —— 跨平台可验证个人 Agent 身份",
    "cumulative_budget_governance":
        "个人预算守护（per_tx / daily / weekly / monthly 4 粒度）",
    "target_site_risk_scoring":
        "8 因素风险评分（amount_over_p90 / off_hours / currency_shift / new_target 等）",
    "connector_independent_review":
        "Connector 独立 8 规则审核（危险 scope / 管道安装 / 明文 token 等）",
    "user_level_dispute_receipt":
        "HMAC-SHA256 行动链 + 用户级 dispute 回执（90 天离线可验证）",
    "personal_identity":
        "PAI DID（同 portable_personal_identity）",
    "agent_budget_governance":
        "预算守护（同 cumulative_budget_governance）",
    "personal_budget_governance":
        "预算守护（同 cumulative_budget_governance）",
    "budget_governance":
        "预算守护（同 cumulative_budget_governance）",
    "cumulative_budget":
        "累计预算守护（同 cumulative_budget_governance）",
    "personal_budget":
        "个人预算守护（同 cumulative_budget_governance）",
    "cross_platform_budget":
        "跨平台累计预算（per-user 单点治理，任意平台实例都记账）",
    "agent_level_budget":
        "agent 实例级预算（Ticket 层 scope）",
    "user_level_action_dispute":
        "HMAC-SHA256 行动链 + 用户级 dispute 回执（90 天离线可验证）",
    "agent_level_governance":
        "Capability Ticket（用户对某实例的白名单 + TTL 授权）",
    "tool_call_audit":
        "HMAC 行动溯源链（工具调用 + 参数 + verdict）",
    "user_personal_identity":
        "PAI DID（企业开发者 API 也支持）",
    "personal_agent_identity":
        "PAI DID + 实例注册（agent_name + provider + platform）",
    "third_party_action_dispute":
        "dispute 回执（用户可挑战任一历史行动）",
    "off_platform_audit_trail":
        "HMAC 链跨平台可验证（不依赖平台内部日志）",
    "action_dispute_receipt":
        "同 user_level_dispute_receipt",
    "action_dispute":
        "同 user_level_dispute_receipt",
    "user_dispute_receipt":
        "用户级 dispute 回执（同 user_level_dispute_receipt）",
    "dispute_receipt":
        "同 user_level_dispute_receipt",
    "agent_audit":
        "HMAC 行动溯源链（覆盖工具调用 + 参数 + 状态变迁）",
}

# ══════════════════════════════════════════════════════════════
# 接入路径定义
# ══════════════════════════════════════════════════════════════

ACCESS_PATHS: dict[str, dict[str, Any]] = {
    "mcp": {
        "name": "MCP 协议",
        "description": "Model Context Protocol（Microsoft/Anthropic 2024 标准）。AIShield 已提供 48+ MCP 工具，平台只要支持 MCP 即可零迁移接入。",
        "isolation_level": "high",
        "requires_platform_change": False,
        "aisshield_status": "ready",
    },
    "openai_compat": {
        "name": "OpenAI 兼容 API",
        "description": "平台提供 OpenAI 兼容 /v1/chat/completions 接口，AIShield 可作为上游 guardrail 或工具调用被路由。",
        "isolation_level": "medium",
        "requires_platform_change": True,
        "aisshield_status": "ready",
    },
    "connector_official": {
        "name": "平台官方 connector",
        "description": "平台开放 connector 平台（Muse / ChatGPT / Coze / 元宝），提交表单 → 平台审核 → 上架。",
        "isolation_level": "low",
        "requires_platform_change": True,
        "aisshield_status": "requires_submission",
    },
    "native_sdk": {
        "name": "平台私有 SDK",
        "description": "平台不开放 MCP / OpenAI 兼容模式，需按平台私有 SDK 集成。",
        "isolation_level": "low",
        "requires_platform_change": True,
        "aisshield_status": "requires_adaptor",
    },
    "browser_agent": {
        "name": "浏览器代操",
        "description": "Grok Bot / OpenAI Operator / Claude Computer Use 等，通过浏览器层操作网页，无 API 也可用。AIShield 走 MCP 作为其内部工具。",
        "isolation_level": "high",
        "requires_platform_change": False,
        "aisshield_status": "ready",
    },
}

# ══════════════════════════════════════════════════════════════
# 查询函数
# ══════════════════════════════════════════════════════════════

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_platform(platform_id: str) -> dict[str, Any] | None:
    """按 id 取平台信息；不存在返回 None。"""
    return PLATFORM_BY_ID.get((platform_id or "").strip().lower())


def list_platforms(
    *,
    family: str | None = None,
    cny_accessible: str | None = None,
    access_path: str | None = None,
    includes_gaps: bool = False,
) -> list[dict[str, Any]]:
    """列出所有平台。

    family: consumer / developer / enterprise / infrastructure
    cny_accessible: reachable / verified_blocked / regional_only
    access_path: mcp / openai_compat / connector_official / native_sdk / browser_agent
    includes_gaps: True 时返回 gaps 已解析的 governance_provision 映射
    """
    out: list[dict[str, Any]] = []
    for p in PLATFORMS.values():
        if family and p.get("family") != family:
            continue
        if cny_accessible and p.get("cny_accessible") != cny_accessible:
            continue
        if access_path and access_path not in (p.get("access_paths") or []):
            continue
        q = dict(p)
        if not includes_gaps:
            q.pop("gaps", None)
            q.pop("governance", None)
        out.append(q)
    return out


def recommend_platforms(
    *,
    user_country: str = "CN",
    capabilities_needed: list[str] | None = None,
    budget: str = "free",
    developer_level: str = "beginner",
    prefer_mcp: bool = True,
) -> list[dict[str, Any]]:
    """推荐接入平台。

    user_country: "CN" 时排除 verified_blocked
    capabilities_needed: 例如 ["personal_identity", "budget_governance"]
        —— 过滤掉不覆盖这些治理项的平台
    budget: "free" / "paid"
    developer_level: "beginner" / "intermediate" / "expert"
    prefer_mcp: True 时优先 MCP 通道的平台
    """
    if capabilities_needed is None:
        capabilities_needed = []
    scored: list[tuple[float, dict[str, Any]]] = []

    for p in PLATFORMS.values():
        pid = p["id"]

        # 大陆过滤
        if user_country.upper() == "CN" and p.get("cny_accessible") == "verified_blocked":
            continue

        # 治理项匹配
        gaps = set(p.get("gaps") or [])
        missing = gaps - set(capabilities_needed)
        if capabilities_needed and not set(capabilities_needed) & gaps:
            # 用户要的治理能力这个平台都不缺 —— 不需要接入
            continue

        score = 0.0

        # 治理缺口越全，越需要接入
        score += len(missing) * 0.1

        # 优先 MCP 通道
        if prefer_mcp and "mcp" in (p.get("access_paths") or []):
            score += 1.0

        # 可达性
        if p.get("cny_accessible") == "reachable":
            score += 0.5

        # developer family 更适合二次开发
        if p.get("family") == "developer" and developer_level in ("intermediate", "expert"):
            score += 0.3

        # 优先有 developer_url
        if p.get("developer_url"):
            score += 0.2

        # 优先新上线（更活跃）
        launched = p.get("launched")
        if launched:
            try:
                ym = datetime.strptime(launched, "%Y-%m-%d")
                age = (datetime(2026, 9, 24) - ym).days
                # 越近越高，1 年 365 天封顶
                score += max(0.0, 0.3 - age / 365 * 0.3)
            except Exception:
                pass

        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])

    out: list[dict[str, Any]] = []
    for sc, p in scored[:10]:
        q = dict(p)
        q["_score"] = round(sc, 3)
        q["_reason"] = _recommend_reason(p, capabilities_needed, user_country)
        out.append(q)
    return out


def _recommend_reason(p: dict[str, Any],
                      capabilities_needed: list[str],
                      user_country: str) -> str:
    parts: list[str] = []
    gaps = set(p.get("gaps") or [])
    matched = gaps & set(capabilities_needed or [])
    if matched:
        parts.append(f"补齐 {len(matched)} 项治理缺口")
    if user_country.upper() == "CN" and p.get("cny_accessible") == "reachable":
        parts.append("大陆可达")
    if "mcp" in (p.get("access_paths") or []):
        parts.append("支持 MCP")
    if p.get("developer_url"):
        parts.append("有开发者入口")
    if not parts:
        parts.append("生态接入候选")
    return "；".join(parts)


def governance_gap_matrix() -> dict[str, dict[str, Any]]:
    """返回治理缺口矩阵：{platform_id: {covered, gaps, provision_map}}。"""
    out: dict[str, dict[str, Any]] = {}
    for p in PLATFORMS.values():
        covered = p.get("governance") or []
        gaps = p.get("gaps") or []
        provision_map = {
            g: GOVERNANCE_PROVISIONS.get(g, f"(无映射) {g}") for g in gaps
        }
        out[p["id"]] = {
            "platform_id": p["id"],
            "name": p["name"],
            "vendor": p.get("vendor"),
            "cny_accessible": p.get("cny_accessible"),
            "covered": covered,
            "gaps": gaps,
            "gaps_with_provisions": provision_map,
        }
    return out


def stats() -> dict[str, Any]:
    """平台注册表统计。"""
    by_family: dict[str, int] = {}
    by_access: dict[str, int] = {}
    by_cny: dict[str, int] = {}
    for p in PLATFORMS.values():
        by_family[p.get("family", "unknown")] = \
            by_family.get(p.get("family", "unknown"), 0) + 1
        by_cny[p.get("cny_accessible", "unknown")] = \
            by_cny.get(p.get("cny_accessible", "unknown"), 0) + 1
        for ap in (p.get("access_paths") or []):
            by_access[ap] = by_access.get(ap, 0) + 1
    return {
        "total_platforms": len(PLATFORMS),
        "by_family": by_family,
        "by_cny_accessible": by_cny,
        "by_access_path": by_access,
        "governance_provisions_count": len(GOVERNANCE_PROVISIONS),
        "access_paths_defined": list(ACCESS_PATHS.keys()),
        "snapshot_at": _now_iso(),
    }


# ══════════════════════════════════════════════════════════════
# 平台注册（允许运行时扩展）
# ══════════════════════════════════════════════════════════════

def register_platform(platform_id: str, **fields: Any) -> dict[str, Any]:
    """运行时注册新平台（用于 CI/CD 增量扩展）。"""
    pid = (platform_id or "").strip().lower()
    if not pid:
        raise ValueError("platform_id 不能为空")
    if not any(c.isalpha() for c in pid):
        raise ValueError("platform_id 必须含字母")
    if pid in PLATFORM_BY_ID:
        # 更新模式
        for k, v in fields.items():
            PLATFORM_BY_ID[pid][k] = v
        return dict(PLATFORM_BY_ID[pid])
    rec = dict(fields)
    rec["id"] = pid
    rec.setdefault("launched", "unknown")
    rec.setdefault("gaps", [])
    rec.setdefault("governance", [])
    rec.setdefault("access_paths", [])
    rec.setdefault("cny_accessible", "unknown")
    PLATFORMS[pid] = rec
    PLATFORM_BY_ID[pid] = rec
    return dict(rec)


# ══════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("AIShield Platform Registry — self test")
    print("=" * 60)

    print(f"\nTotal platforms: {stats()['total_platforms']}")
    print(f"By family: {stats()['by_family']}")
    print(f"By CNY accessibility: {stats()['by_cny_accessible']}")
    print(f"By access path: {stats()['by_access_path']}")

    # 1. 大陆可达平台
    reachable = list_platforms(cny_accessible="reachable")
    print(f"\n大陆可达平台 ({len(reachable)}):")
    for p in reachable:
        print(f"  · {p['id']:30s} family={p['family']:12s} "
              f"paths={','.join(p['access_paths'] or [])}")

    # 2. 已验证大陆不通
    blocked = list_platforms(cny_accessible="verified_blocked")
    print(f"\n大陆验证不通 ({len(blocked)}):")
    for p in blocked:
        print(f"  · {p['id']:30s} {p.get('developer_url', 'n/a')}")

    # 3. 推荐
    print("\n--- 大陆用户 + MCP 优先 + 需要 personal_identity 推荐 ---")
    recs = recommend_platforms(
        user_country="CN",
        capabilities_needed=["portable_personal_identity",
                             "cumulative_budget_governance"],
        prefer_mcp=True,
    )
    for r in recs:
        print(f"  · score={r['_score']:.3f} {r['id']:30s} {r['_reason']}")

    # 4. 治理矩阵
    print("\n--- 治理矩阵示例 (meta-muse) ---")
    matrix = governance_gap_matrix()
    for k in ("meta-muse", "xai-grok-bot", "bytedance-coze"):
        if k in matrix:
            m = matrix[k]
            print(f"\n{k} ({m['name']}):")
            print(f"  covered: {len(m['covered'])} | gaps: {len(m['gaps'])}")
            for g, prov in m["gaps_with_provisions"].items():
                print(f"    GAP: {g} → {prov}")

    # 5. 注册新平台
    print("\n--- 运行时注册测试 ---")
    new_p = register_platform("test-fake", name="TestFake",
                               vendor="Test", family="developer",
                               cny_accessible="reachable",
                               access_paths=["mcp"])
    print(f"  registered: {new_p['id']}")
    assert "test-fake" in PLATFORM_BY_ID
    print(f"  total now: {len(PLATFORMS)}")

    print("\n✅ self-test passed")
