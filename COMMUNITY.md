# COMMUNITY.md — 分发与社区渠道清单（B8）

> 借鉴 heyclicky 的增长飞轮：社区复刻 / 集成列表本身就是分发信号（distribution KPI）。
> 本文件把 AIShield 的「已上架 / 待上架 / 社区信号」集中登记，作为运营守夜的台账。

## 官方上架渠道

| 渠道 | 状态 | 链接 / 标识 | 备注 |
|---|---|---|---|
| **npm** | ✅ 已上架 | `aishield-mcp-server` v4.8.3 | 主分发通道；`npm i -g aishield-mcp-server` |
| **Glama** | ✅ 已上架 | `lm203688/aishield` (gso85mvobx, MIT) | MCP server 目录 |
| **Skills 市场** | ✅ 已上架 | `aishield-ops` skill（用户级） | 运营 / 竞品 / 推广资产 |
| **Official MCP Registry** | ⚠️ 待核实 | 推送由 `publish-mcp-registry.yml` 自动完成 | 实测 `registry.modelcontextprotocol.io` 曾返 404，需复验 |
| **GitHub Marketplace** | 🟡 待建仓 | 动作名 `aishield-security-scan` | 需独立仓 `lm203688/aishield-action` |
| **Glama Skills** | ✅ 同步 | 与 npm / GitHub 同源 | — |
| **Tencent TeamAI hub** | 🟡 资产就绪 | `distribution/teamai/`（README + `block-unscanned-skill` hook） | 腾讯开源 agent 框架，分发 11 种 agent（含 WorkBuddy）；缺「全量 skill/MCP 安全门禁」，我方补位 |
| **CocoLoop / CLS-Certify** | 🟡 草稿就绪 | `distribution/cocoloop/LISTING.md` | 国内最大 OpenClaw 技能商店（1.3万–4.7万 skills）；其安全扫描依赖大模型+外部 API，我方差异化＝本地零依赖 / 代码不上云 / 双维 / 秒级静态 |

## 社区信号（分发 KPI）

- **Awesome 列表 / 社区复刻**：被第三方收录或 fork 即视为有效分发信号，归到此处登记。
- **awesome-mcp-servers / awesome-agent-security**：定期提交收录 PR，状态登记于上表。
- **社区复刻（如 clickyX 之于 heyclicky）**：出现复刻仓时，评估是否吸收 upstream 修复。

## 竞品 / 渠道深度分析

- 14 个 agent 项目的逐项目评估（扫描目标 / 竞品 / 分发 / 威胁建模）见 `docs/agent-landscape-2026-09.md`。

## 分发缺口（运营待办）

1. 复验 Official MCP Registry 上架状态（避免「已发布」误判）。
2. 建 `lm203688/aishield-action` 独立仓，打通 GitHub Marketplace。
3. 每新增一个上架渠道，更新本表 + `distribution/published.json` 台账。
4. **CocoLoop 上架**：文案已就绪，**等用户注册账号**（手机/微信 OTP）后在「社区投稿」入口粘贴 `distribution/cocoloop/LISTING.md`。TeamAI 无需账号，`teamai.yaml` 已在册。
5. ✅ **规则数 drift 已 sweep（2026-09-15）**：基线 **235 MCP / 241 Skill**（含 2 条 RSI L5 规则）。37 个 live 面（README / `api/server.py` 元数据 / `api/static/*` 静态页 / `docs/*` GEO 资产 / registry / discovery 文件）已统一为 235/241，静态页版本号 4.2.2→4.3.0。带日期的历史报告（`eco/reports/`、`docs/intel/`、`_scan_*`、`docs/agent-ecosystem-distribution.md`、`raw_verify.md`）**刻意保留原值**，改之等于篡改史实。

> 渠道状态以一手复验为准（curl / RDAP / 页面实测），不凭记忆。
