# AIShield 长期记忆（精简索引版）

> 全量历史见 `.workbuddy/memory/archive/MEMORY-full-2026-08-10.md`；活态势表见私有 skill `~/.workbuddy/skills/aishield-ops/references/competitive-landscape.md`。

## 定位
Agent 原生 AI 工具安全扫描器：扫 MCP server / AI skill / GPTs / prompt。规则底座 **214 MCP / 220 Skill**（含 11 条 SANDBOX 沙箱硬化 + 雷达晋升规则），对齐 OWASP MCP Top10 + Agentic AI Top10。**零第三方依赖（仅 urllib）**，本地规则引擎 + 可选远程 LLM 语义后端。
仓库 `lm203688/aishield`（public，Pages baseurl `/aishield`）；npm `aishield-mcp-server` **4.2.2**（已发布可用）。
**核心不变量：绝不 spawn 被扫配置里的命令**（竞品会真实执行）。基准 20 良性 0 误报 / 10 恶意 10/10。

## 卡位
空白位 =「本地不上云 + MCP+Agentic 双维 + 中性信任机构 + Fleet 看板 + 机器可结算付费认证 + **agent 计算机的内容安全平面**」。
最危险竞品 mcp-audit（89 SAST 规则、全离线）。forgevm / Cloudflare Sandbox / Open Interpreter / Goose 只做 OS 隔离，不做内容安全 → **互补非竞品**。
关键认知：**缺口是可见性不是能力**，杠杆在 GEO/agent 化露出。

## 能力索引（按文件找，不复述细节）
- `scanner/`：rules / engine（`_DIM_CONFIG` 驱动评分）/ sbom / osv / attack_path / policy / telemetry / live_probe / fleet / **workspace_scan（启动前预扫）**
- `eco/`：badge / payment / x402 / **hupijiao（CNY 轨）** / monetization / credentials / **spend_cap（fail-closed 三档）** / **runtime_governance（kill switch + 哈希链审计）** / **attestation（持续鉴证，支持 live workspace 复扫）** / **guardrail_harness（stdio JSON-RPC 准入）**
- `api/server.py`：eco 模块用 `register_routes(handler)` monkey-patch 链式包装；静态页全离线 0 CDN
- `scripts/`：gh_push / tech_radar / promote_rule / capability_gap / scan_workspace / sync_version / gen_task_registry
- 测试 `tests/run_all.py`：**404 通过 / 0 失败 / 9 skipped**（unittest，无 pytest）

## 工程铁律
- **推送**：本地 .git 损坏 + git 直连 github.com 不通 → 一律 `scripts/gh_push.py`（Contents API PUT 带 sha）。**推完必须 API 复验**。
- **PAT**（`.workbuddy/schedule-revert-pat.txt`，gitignored）：已具 repo + workflow + delete_repo。曾明文出现在对话，**建议轮换**。delete_repo 高危，删仓库须用户明确确认。
- **门禁教训**：恒定输出的门禁等于没门禁。`tests/test_ci_contract.py` 钉死「门禁读的键 API 必须提供」。改 workflow 后必跑 `gen_task_registry.py`，否则 CI 红。
- **环境**：Git Bash 无 `sleep`（用 Python）；别用 `timeout`（命中 Windows timeout.exe）；`rm` 用 Windows 绝对路径；npm 走 `C:/Users/xing/node/node.exe .../npm-cli.js`。
- **密钥红线**：仓库 public，真实密钥只进 gitignored 文件或环境变量。
- **自带洞最难堪**：对外发布物（npm 依赖、分发的 skill）必须先过自家扫描器，纳入守夜必检。
- **发布留底**：任何对外渠道（Agensi/Claude Skill/GPT Store/HF）发布的产物，源必须入 `distribution/` 留底。

## 巡检
日度守夜 `automation-1785826846646`（08:30，报告 `eco/reports/guard-*.md`）；周度竞争情报 `automation-1785849857521`（周一）；Tech Radar `automation-1786262658410`（daily 02:00）。
**带外巡检必查**：GitHub API 最近运行时间 + 各 workflow `state` 是否 active（仓库内自检看不到 Actions 被禁用）。最强存活信号 = 远端 `data/state/health.json` 的 `updated`（Contents API 读，本地副本不算数）。
调度加速期 HOURLY 至 2026-08-30，回滚由 `automation-1785890505506`（08-31）执行。

## 路线图（剩余）
1. 中立跨注册中心发现层（104k agents / 15 registries / 0 互操作）——挂起。
2. 运行时治理：补行为监控采集 + CI 门禁调 evaluate。
3. Fleet 接 monitor 版本流；x402 接真实 facilitator；enterprise 多租户。
4. Agent 计算机安全底座 #1–#4 已全闭环（预扫/沙箱硬化/harness 准入/持续鉴证）。
