# .well-known — 说明

本仓库的 **可服务** `.well-known/*` 资产在 [`api/static/.well-known/`](../api/static/.well-known/)。

Cloudflare Pages 从 `api/static/` 作为网站根部署（见 [`deploy.sh`](../deploy.sh) 与 `.github/workflows/pages.yml`），所以线上路径

- `https://aishield.tools/.well-known/agent-card.json`
- `https://aishield.tools/.well-known/agent.json`
- `https://aishield.tools/.well-known/mcp/server-card.json`
- `https://aishield.tools/.well-known/security.txt`

分别对应 `api/static/.well-known/` 下的同名文件。

**为什么仓库根不再复制一份**：曾出现"两个根"的历史遗留问题（`api/static/.well-known/agent.json` 和 `docs/.well-known/agent-card.json` 各有一份，前者是活副本、后者是死副本），规则数门禁被迫两边都覆盖，是"扫死副本、放行活副本"缺陷的根源。2026-10-17 起只保留 `api/static/.well-known/` 一处作为唯一真源；根 `.well-known/` 只留本 README 作解释，不再放内容。

## 服务资产清单（唯一真源 `api/static/.well-known/`）

| 文件 | 用途 |
|---|---|
| `agent-card.json` | A2A / agent discovery 卡 |
| `agent.json` | agents.well-known.dev v1 通用 agent 描述 |
| `ai-plugin.json` | Vercel AI SDK / ChatGPT plugin 描述 |
| `mcp/server-card.json` | MCP 官方 registry manifest |
| `security.txt` | 漏洞披露联系方式 |

规则数/版本一致性由 `scripts/rule_count_gate.py` + `scripts/sync_version.py` + `scripts/declaration_surface_gate.py` 联合强制（`api/static/.well-known/*` 在声明面白名单内）。
