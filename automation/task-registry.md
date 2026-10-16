# AIShield 自动化台账

> **本文件由 `scripts/gen_task_registry.py` 自动生成，请勿手工编辑。**
> 生成时间：2026-10-16 01:23 UTC

历史教训：本台账曾手工声称「二十八项定时任务在跑」，而仓库实际只有十四个 workflow，其中 self-heal 因 YAML 语法错静默失效 48 天。台账一旦脱离现实，就会把「看起来很自动化」的幻觉喂给每一次决策。现改为从 workflow 真实内容派生。

## 总览

| 指标 | 数值 |
|------|------|
| 本仓库 workflow 总数 | 21 个任务 |
| 其中定时驱动 | 7 个 |
| 其中事件驱动 | 14 个 |
| 存在断链/语法问题 | 0 个 |

## 定时任务

| Workflow | 名称 | 调度 | Jobs | 闭环环节 |
|----------|------|------|------|----------|
| `closed-loop-spine.yml` | AIShield Closed-Loop Spine (情报→修复→提升→迭代) | 每日 03:17 UTC | 9 | 检测✓动作✓验证✓ ⚠️缺告警 |
| `geo-indexnow-submit.yml` | AIShield GEO IndexNow Submit (收录加速) | 每日 09:20 UTC | 3 | 检测✓动作✓验证✓告警✓ |
| `meta-monitor.yml` | AIShield Meta-Monitor (监控自动化体系本身) | 每 8 小时（第 15 分）UTC | 2 | 检测✓动作✓验证✓告警✓ |
| `npm-self-heal.yml` | npm self-heal | 每 12 小时（第 12 分）UTC | 1 | 动作✓验证✓ ⚠️缺检测告警 |
| `self-heal-closed-loop.yml` | AIShield Auto Self-Heal Closed-Loop | 每 6 小时（第 23 分）UTC | 6 | 检测✓动作✓验证✓告警✓ |
| `stale.yml` | Stale Issues Manager | 每日 02:26 UTC | 1 | 验证✓ ⚠️缺检测动作告警 |
| `tech-radar.yml` | AIShield Tech Radar (技术雷达采集) | 每日 06:23 UTC | 1 | 检测✓动作✓验证✓ ⚠️缺告警 |

## 事件驱动任务

| Workflow | 名称 | 触发 | Jobs |
|----------|------|------|------|
| `channel-distribution.yml` | AIShield Channel Distribution (Content + Registry + Social) | workflow_call / 手动 | 7 |
| `ci.yml` | AIShield CI/CD | workflow_call / push(main,dev) / PR / 手动 | 10 |
| `data-scan-flywheel.yml` | AIShield Data Flywheel (Batch Scan to Self-Built Database) | workflow_call / 手动 | 2 |
| `deploy-server.yml` | Deploy to Production Server | workflow_call / 手动 | 2 |
| `feature-closed-loop.yml` | AIShield Intelligence-to-Feature Closed-Loop | workflow_call / Issue 事件 / 手动 | 5 |
| `install-cf-token.yml` | install CF token to VPS | 手动 | 1 |
| `issue-labeler.yml` | Auto Label Issues | Issue 事件 / 手动 | 1 |
| `pages.yml` | Pages Site (内容站构建与发布) | push(main) / workflow_run / 手动 | 4 |
| `project-digest.yml` | AIShield Project Digest (统一迭代汇报) | workflow_call / 手动 | 1 |
| `publish-mcp-registry.yml` | Publish to MCP Registry | workflow_run / 手动 | 2 |
| `publish-npm.yml` | Publish to npm | release / push / 手动 | 5 |
| `rule-promoter.yml` | AIShield Rule Auto-Promoter | workflow_call / 手动 | 2 |
| `threat-intel-feed.yml` | AIShield Threat-Intel Feed Update | workflow_call / 手动 | 6 |
| `unified-security-scan.yml` | AIShield Unified Security Scan | workflow_call / push(main) / PR / 手动 | 2 |

## 状态总线最近更新

> 机器可读状态存于 `data/state/<域>.json`，是闭环之间唯一的通信介质。

| 状态域 | 最近更新 |
|--------|----------|
| data | 2026-09-04 07:56:50 |
| deploy | 2026-10-15 07:24:56 |
| distribution | 2026-10-14 08:50:35 |
| feature | 2026-10-14 08:49:43 |
| flywheel | 2026-10-15 08:16:52 |
| health | 2026-10-15 17:11:28 |
| intel | 2026-10-15 08:19:32 |
| meta | 2026-10-15 13:23:27 |
| registry | 2026-10-14 08:50:23 |
| rules | 2026-10-15 08:18:05 |
| selfheal | 2026-10-15 17:11:41 |

## 健康问题

当前无语法错误、无脚本断链。

---

## 跨项目调度任务（外部，不计入本仓库统计）

HealthLens / GeneTech / RoboParts / SwarmLabs / OracleMind 等项目的定时任务由 WorkBuddy 调度器管理，不在本仓库内，**其运行状态无法从这里验证**，因此不并入上方计数。需核对时请直接查询调度器。

