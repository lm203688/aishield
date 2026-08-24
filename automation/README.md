# AIShield 定时任务管理中枢

> 作为项目总指挥的统一任务管理入口。所有定时任务的注册、状态、结果汇总于此。

## 目录结构

```
automation/
├── README.md           - 本文件（任务管理中枢说明）
├── task-registry.md    - 任务注册表（由 scripts/gen_task_registry.py 从 .github/workflows/ 自动派生，勿手编）
├── manual-actions.md   - 需要用户手动解决的问题清单
├── daily-summary.md    - 每日任务执行汇总（自动更新）
└── status/             - 各任务执行状态快照
```

> 台账即代码：`.github/workflows/*.yml` 是唯一事实源，`task-registry.md` 是派生产物。
> 增删定时任务后运行 `python scripts/gen_task_registry.py`（CI 里自动跑），一致性用 `--check` 校验。

## 任务分类

| 项目 | 任务数 | 频率 | 状态 |
|------|--------|------|------|
| AIShield（本仓） | 18 workflow（13 个定时调度） | 15 分钟~季度 | 运行中 |
| HealthLens | 见各项目仓 | 日/周/月/季 | 运行中 |
| GeneTech | 见各项目仓 | 日/周/月 | 运行中 |
| RoboParts | 见各项目仓 | 日/周/月 | 运行中 |
| SwarmLabs | 见各项目仓 | 日 | 运行中 |
| OracleMind | 见各项目仓 | 日/周/月 | 运行中 |
| 获客基础设施 | WorkBuddy 守护（5 个带外任务） | 日/周 | 运行中 |

> 注：除 AIShield 外的项目台账在各自仓库维护；本目录的 task-registry.md 只派生本仓 workflow。
> WorkBuddy 守护（守夜巡检、周度竞争情报、Tech Radar、分发缺口、周日 digest）不在 GitHub Actions 内，
> 由本机计划任务驱动，产物直接推 main。

## 闭环原则

所有任务遵循闭环工作流：
```
信息收集 → 分析 → 决策 → 开发/执行 → 测试/验证 → 部署/反馈
```

## 报告路径

各项目报告产出路径：
- AIShield: `eco/reports/daily-YYYYMMDD.md`、`eco/reports/weekly-YYYY-WNN.md`
- 其他项目: 各自项目目录下的 `ops/` 文件夹

## 需人工介入处理流程

1. 定时任务发现需人工介入的问题 → 写入 `manual-actions.md`
2. 总指挥汇总 → 统一通知用户
3. 用户处理后 → 标记为已解决
4. 下次任务执行时验证修复效果

## 告警分级约定（scripts/notify.py）

| 级别 | 行为 | 适用 |
|------|------|------|
| P0 | 立即建 Issue + webhook | 服务宕机、部署验证失败等硬故障 |
| P1 | 建 Issue（冷却 6h 去重）+ webhook | 流水线红、晋升被回滚 |
| P2 | 仅落盘 + webhook，不建 Issue | 业务指标波动（如获客阈值）→ 归入周日 digest |

> 教训（2026-08-24）：告警指纹必须稳定（勿把 runId 拼进标题），否则去重失效会灌屏。
