# AGENTS.md — Agent 原生项目手册（AIShield）

> 本文件供 AI 编码 agent（Claude Code / Codex / Cursor / AIShield 自身）直接读取。
> 目标：让 agent 在 **不询问** 的情况下理解架构、不变量与贡献约定。
> 借鉴自 heyclicky（`farzaa/clicky`）的 `AGENTS.md` 增长飞轮——早期 MIT 开源 +
> agent 可读文档，3 周冲到 7.5k stars。

## 这是什么

AIShield 是 **Agent 原生 AI 工具安全扫描器**：扫描 MCP server / skill / GPTs /
prompt，对齐 **OWASP MCP Top 10 (2025)** 与 **OWASP Agentic AI Top 10 (ASI01–ASI10)**，
零第三方依赖、可 100% 离线运行。

- 仓库入口：`lm203688/aishield`（public）
- npm 包：`aishield-mcp-server`（v4.8.3，264 条规则 = 静态 237 + 情报 8 + 雷达 19）
- 线上站：`aishield.tools`（Cloudflare Named Tunnel → VPS `:8450` → `api/server.py`）
- 后端 API 前缀：`/api/v1`（注意：`/api/health` 会 404）

## 核心不变量（违背即 bug）

1. **绝不 spawn 被扫配置里的命令。** 扫描器把被扫内容当字符串读取、做正则/语义
   匹配，绝不 `exec` / `os.system` / `subprocess` 被扫配置中的任何指令。
   自证：`python scripts/prove_isolation.py`（拦截 subprocess/os.system，断言 0 次 spawn）。
2. **代码与配置绝不上传云端。** 本地优先、零依赖、可离线。
3. **绝不引用过期规则计数。** 真值以 `/api/v1/health` 的 `rules_breakdown` 为准；
   改规则数必须同步 `mcp-server/README.md` 逐类表 + 跑 `scripts/sync_readme_counts()`。
   勿引用 227/215/133/228 等历史数字。
4. **本地测试绿 ≠ CI 绿。** 推送走 `scripts/_push_batch.py`（Contents API，单提交），
   推完必须 API 复验。
5. **事件型告警必须能销案。** "本轮新增 N 条漏洞" 类告警不会自动恢复，零新增即 resolve；
   不要把它当健康型告警只在恢复时 `--resolve`。

## 架构速览

| 目录 / 文件 | 职责 |
|---|---|
| `api/server.py` | 后端 FastAPI 服务（`/api/v1/audit`、`/api/v1/handshake` 等） |
| `scanner/` | 扫描引擎（`engine.py` 主入口 `scan()`；`rules.py` 规则库；`baseline_scan.py` 基线漂移） |
| `mcp-server/src/index.ts` | MCP server（调后端 API，渲染结果给 agent） |
| `scripts/` | 运维脚本：`tech_radar.py`（雷达）、`promote_rule.py`（规则晋升）、`radar_effect.py`（效果度量）、`_push_batch.py`（推送） |
| `data/state/` | 运行时状态（`tech_radar.json`、`radar_effect.json`） |
| `.github/workflows/` | CI/CD + 守夜 spine（cron 03:17）+ 独立 cron（self-heal/meta-monitor/stale） |
| `tests/` | Python 测试套件（`tests/run_all.py` 统一入口） |

## 闭环四环节（落地必查）

检测 → 动作 → 验证 → 告警。任何新能力都要问：它在哪一步闭环？否则只是半成品。

## 一键启动（给 agent / 贡献者）

```
# 1. 克隆并准备
git clone https://github.com/lm203688/aishield.git && cd aishield
python -m venv .venv && source .venv/bin/activate && pip install pytest

# 2. 跑全量测试
python tests/run_all.py

# 3. 自证隔离不变量
python scripts/prove_isolation.py
```

> 把上面这段贴进 Claude Code / Codex 即可启动，无需额外讲解。

## 贡献约定（范围纪律 — B7）

- **不擅自加超出请求范围的功能或重构。** 大代码库里 churn 比 bug 更贵；先问再扩。
- 保持零外部依赖（标准库 only）。测试可用 `pytest`。
- 新增/修改 `scanner/rules/` 规则遵循 `MCPxx-xxx` 编号；雷达规则必须「结构性具体」
  （含 `|` 交替或有界间隔 `.{n,m}`，裸关键词留 draft），否则会误伤自家仓库。
- 改 `scanner/` 后跑对应测试；改 `.github/workflows/` 后跑
  `scripts/gen_task_registry.py --check` 校验台账一致。
- 多文件推送用 `scripts/_push_batch.py`（单提交，避免中间不一致态致 CI 假红）。

## 相关文档

- `COMMUNITY.md` — 分发 / 上架渠道清单（Glama / npm / Skills 市场 / GitHub Marketplace）
- `CONTRIBUTING.md` — 完整贡献流程
- `docs/` — 安全研究博客与架构文档
