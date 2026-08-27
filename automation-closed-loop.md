# AIShield 自动化闭环体系架构

> 设计目标：18 个 workflow 不是 18 个孤岛，而是一个 **Sense→Decide→Act→Verify→Report** 的五层闭环。任何一层输出都是下一层的输入，任何故障都被下一层捕获并自愈。

---

## 一、五层闭环总图

```
┌─────────────────────────────────────────────────────────────────┐
│                    ⑤ Report（报告层）                            │
│  Project Digest  ·  Agent Mail  ·  Meta Monitor  ·  Issue Labeler│
│                         ↑                                      │
│  ④ Verify（验证层）       ↑                                      │
│  Pages 3-Verify · CI verify · Meta Monitor · Distribution Gate   │
│                         ↑                                      │
│  ③ Act（执行层）          ↑                                      │
│  Self-Heal · Rule Promoter · CI Publish · Channel Distribution  │
│  Publish to npm / MCP Registry · Pages Deploy                   │
│                         ↑                                      │
│  ② Decide（决策层）        ↑                                      │
│  State Bus (data/state/*.json) · Feature Closed-Loop            │
│                         ↑                                      │
│  ① Sense（感知层）        ↑                                      │
│  Threat Intel Feed · Unified Security Scan · Data Flywheel      │
│  npm Self-Heal · Meta Monitor                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、18 个 workflow 按层归类

### ① Sense（感知层）— 数据采集

| Workflow | 触发 | 产出状态域 | 频率 | 健康度 |
|----------|------|-----------|------|--------|
| `threat-intel-feed.yml` | schedule | `intel.json` | 每 2h | ✅ success |
| `unified-security-scan.yml` | schedule/push | 扫描报告 | 每 2h | ✅ success |
| `data-scan-flywheel.yml` | schedule | `flywheel.json` | 每 3h | ✅ success |
| `npm-self-heal.yml` | schedule | npm 状态 | 每 2h | ✅ success |
| `meta-monitor.yml` | schedule | `meta.json` | 每 2h | ✅ success |

**Sense 层核心原则**：不写代码、不发版、不告警——只采集事实并写入 state bus。

### ② Decide（决策层）— 状态汇聚与路由

| Workflow | 输入 | 产出 | 决策逻辑 | 健康度 |
|----------|------|------|---------|--------|
| `feature-closed-loop.yml` | `feature.json` + Issues | `feature.json` + `ROADMAP.md` | 多源反馈→定级→采纳→落库 | ✅ 修复中（Python 3.11→3.13） |
| `rule-promoter.yml` | `_proposed/` + `rules.json` | `rules.json` | 候选规则→测试通过→晋升正式 | ✅ success |

**Decide 层核心原则**：只写 JSON 事实，不写散文。所有决策可追溯（source + timestamp）。

### ③ Act（执行层）— 修复/发布

| Workflow | 触发 | 操作 | 健康度 |
|----------|------|------|--------|
| `self-heal-closed-loop.yml` | schedule | 检测故障→执行修复→测试→部署 | ✅ success |
| `ci.yml` | push/schedule/manual | 7 个门禁 job + 写 `ci.json` | ✅ success |
| `publish-npm.yml` | release/tag/manual | npm publish | ⏸ 等待 v4.3.0 触发 |
| `publish-mcp-registry.yml` | npm publish 完成 | 提交 MCP Registry | ⏸ 链在 npm 后 |
| `pages.yml` | push | 部署内容站 | ✅ success |
| `channel-distribution.yml` | schedule | 多渠道内容分发 | ✅ success |

**Act 层核心原则**：任何写操作必须经过 CI 门禁（`ci.json.overall == "success"`）。

### ④ Verify（验证层）— 闭环确认

| 验证环节 | 位置 | 方法 | 失败动作 |
|----------|------|------|---------|
| 内容站版本复验 | `pages.yml` Step 3-Verify | `curl aishield.tools/api/v1/health` 对版本 | 失败→重部署 |
| CI 门禁 | `ci.yml` 7 jobs | py_compile + 590 tests + Docker | 失败→notify-on-failure |
| 分发门禁 | `ci.yml` distribution-gate | `verify_distribution.py` 5/5 | 失败→阻断合并 |
| 自动化体系自检 | `meta-monitor.yml` | 检查所有 workflow 活性 | 失败→自 heal |

### ⑤ Report（报告层）— 人机可读

| Workflow | 产出 | 受众 |
|----------|------|------|
| `project-digest.yml` | 周日迭代周报 | 用户（你） |
| `issue-labeler.yml` | 自动打标签 | 贡献者 |
| `stale.yml` | 自动关闭过期 issue | 维护者 |

---

## 三、状态总线（State Bus）— 闭环的数据骨干

`data/state/*.json` 是五层之间传递事实的唯一管道。

```
 Sense 写入 ──→  Decide 读取 + 更新 ──→  Act 读取 + 写入 ──→  Verify 读取确认
      ↑                                                           │
      └────────────────  Report 渲染 ────────────────────────────┘
```

### 各状态域

| 域 | 写入者 | 读取者 | 用途 |
|----|--------|--------|------|
| `health.json` | self-heal (三路探测) | meta-monitor, project-digest | 线上站存活状态 |
| `ci.json` | ci.yml | feature-closed-loop | CI 通过状态（跨 workflow 复用） |
| `feature.json` | feature-closed-loop | project-digest, meta-monitor | 功能迭代进度 |
| `rules.json` | rule-promoter | meta-monitor | 规则库版本 |
| `intel.json` | threat-intel-feed | project-digest | 威胁情报 |
| `flywheel.json` | data-scan-flywheel | meta-monitor | 数据飞轮进度 |
| `meta.json` | meta-monitor | project-digest | 自动化体系健康度 |
| `registry.json` | channel-distribution | meta-monitor | 上架状态 |
| `distribution.json` | channel-distribution | meta-monitor | 内容分发状态 |
| `selfheal.json` | self-heal | meta-monitor | 自愈执行记录 |

---

## 四、已修复的断点

### 断点 1：feature-closed-loop verify 步骤崩溃

**根因**：`ci.json` 不存在 → verify 走 Python 3.11 全量测试 → 3.11 与 3.13 不兼容 → 失败 → settle 被跳过 → 采纳结果无法落库。

**修复**（3 处）：
1. `ci.yml` 新增 `ci-state` job → CI 完成后写入 `data/state/ci.json`
2. `feature-closed-loop.yml` verify 步骤改为 Python 3.13（与 ci.yml 一致）
3. `feature-closed-loop.yml` ci.json 读取兼容新旧格式（`overall` + `current.last_status` + `last_status`）

### 断点 2：issue-labeler 持续失败

**根因**：`github/issue-labeler@v3.4` 已 deprecated，API 已下线。

**修复**：替换为 `peter-evans/issue-labeler@v3`，`repo-token` 改用 `${{ github.token }}`（更安全的标准写法）。

### 断点 3：publish-npm / publish-mcp-registry 零运行

**根因**：这两个 workflow 设计为"release 触发"和"链式触发"，仓库从未发过新 release（v4.2.2 之后）。

**解法**：发 v4.3.0 → `publish-npm.yml` 自动跑 → `publish-mcp-registry.yml` 连锁跑。

---

## 五、自动化运行完整性检查清单

| 检查项 | 方法 | 预期 |
|--------|------|------|
| 18 个 workflow 全部 active | GitHub API `/actions/workflows` | 18/18 active |
| 所有 Sense 层 24h 内有运行 | `/runs?created=>=24h-ago` | 每 workflow ≥1 run |
| `ci.json` 存在且 overall=success | `cat data/state/ci.json` | overall=success |
| feature-closed-loop 不再失败 | 下次 schedule run | success |
| issue-labeler 不再失败 | 开一个测试 issue | success |
| 542 个自产 issue 已清理 | GitHub issue 数 | ≤15 |

---

## 六、Agent 生态层架构

```
┌─────────────────────────────────────────────────────────────┐
│                     应用层 (Application)                     │
│  MCP Server · npm Package · GitHub Action · VS Code Ext    │
├─────────────────────────────────────────────────────────────┤
│                     能力层 (Capability)                      │
│  227 MCP Rules · 233 Skill Rules · 11 Agentic Modules      │
│  差分扫描 · Fuzzing · 攻击回放 · 垂直风险 · Trust API       │
├─────────────────────────────────────────────────────────────┤
│                     引擎层 (Engine)                          │
│  Scanner Engine · Policy Engine · Attestation · Spend Cap  │
├─────────────────────────────────────────────────────────────┤
│                     数据层 (Data)                            │
│  State Bus · Tech Radar DB · Attack Path Graph             │
├─────────────────────────────────────────────────────────────┤
│                     基础设施层 (Infra)                       │
│  Zero-dep Python · Ollama LLM · Docker · Cloudflare Pages  │
└─────────────────────────────────────────────────────────────┘
```

AIShield 作为 **agent 间的信任通路节点**：

```
   Agent A ──→ AIShield (扫描+鉴证) ──→ Agent B
                         │
                         ↓
                   Trust API (Ed25519)
                         │
                         ↓
              attestation → badge → payment
```

---

## 七、后续加固项

| 项 | 优先级 | 说明 |
|----|--------|------|
| 所有 workflow Python 版本统一 3.13 | P0 | 已完成 ci.yml + feature-closed-loop.yml |
| state bus 写入加 `updated` 字段强制 | P1 | 已有 state_bus.py 但部分 workflow 未遵守 |
| cross-workflow 依赖可视化 | P2 | 用 Mermaid 生成 DAG 图 |
| meta-monitor 增加"ci.json 新鲜度"检查 | P2 | 超 6h 未更新则告警 |