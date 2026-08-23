# AIShield 自动化闭环修复交付报告

> 执行日期：2026-08-04
> 依据：《AIShield_全面评估与自动化闭环补位方案.md》
> 目标：把「看起来在自动运行」变成「真的在自动运行」

---

## 一、修复前 vs 修复后

| 维度 | 修复前 | 修复后 | 验证方式 |
|------|--------|--------|----------|
| 工作流语法/依赖链 | self-heal 因 `needs` 指向 step id 而非 job id，**48 天从未运行** | 15 个工作流 **0 错误 0 警告** | `validate_workflows.py` |
| 体系六维体检 | 无此机制 | **4/4 通过（healthy）** | `meta_monitor.py` |
| 闭环四环节齐备率 | 5 条闭环中 4 条缺环节 | **5 条全部齐备**（检测→动作→验证→告警） | M5 检查 |
| 台账真实性 | 手写声称「28 个定时任务」，实际 14 个 | **自动派生，15 个任务，永不漂移** | `gen_task_registry.py --check` |
| 线上服务状态 | 报告称「11 天不可达」 | **实测 4/4 healthy，HTTP 200** | `health_probe.py` |
| 情报→规则转化 | 情报只入库不产出规则 | 93 条真实漏洞 → **19 条检测规则已装载** | 扫描器规则数 133 → **141** |
| 内容分发 | token 门控恒假，**每次静默空转** | 零凭据四渠道必发 + 落地断言 | `publish_content.py` |
| 调度器守护任务 | AIShield **0 个** | **3 个已注册** | 调度器列表 |
| 回归测试 | 99 通过 | **99 通过（0 失败）** | `tests/run_all.py` |

---

## 二、三个致命缺陷的处置

### 缺陷 1：自愈闭环 48 天从未执行

**根因**：`escalate` 作业的 `needs: verify` 指向的是一个 step id，而非 job id。GitHub Actions 在解析期直接拒绝整个文件——**它从来没有失败过，因为它从来没有开始过**。本地没有任何机制能发现，因为从没有人校验过这些 YAML。

**处置**：
- 重写为 6 个真实作业：`probe → repair → test → verify → escalate → settle`
- `test` 移除 `continue-on-error`，测试失败**必须**阻断
- 新建 `validate_workflows.py`，静态检查 6 类沉默杀手（E1 语法、E2 needs 断链、E3 成环、E4 脚本缺失、E5 缺手动触发、E6 顶层键污染）
- 挂进 CI 门禁：语法错误**在合并前**就被拦下

> 修复过程中，这个校验器抓到了我自己写 `meta-monitor.yml` 时犯的**同一类错误**——多行字符串未缩进导致 YAML 解析失败。这是它存在价值的最好证明。

### 缺陷 2：内容分发静默空转

**根因**：发布步骤被 `if [ -n "$TWITTER_BEARER_TOKEN" ] && [ -n "$REDDIT_CLIENT_ID" ]` 包裹。这两个 secret 从未配置，条件恒假，**每次都走 else 分支打印一行日志**。内容持续生产、从未抵达任何读者——这是 0 star / 0 注册的直接成因。

**处置**：
- 新建 `publish_content.py`：Issue / GitHub Pages / RSS / README **四个零凭据渠道**，`GITHUB_TOKEN` 由 Actions 自动注入，恒可用
- 社交渠道降级为**可选放大**，缺凭据不影响主流程
- 新增 `discover` 作业（发布前探明待发数与历史台账）与 `verify` 作业，关键断言：**有待发内容却台账零增长 = 静默空转**，直接 P1 告警

### 缺陷 3：台账与现实脱节

**根因**：台账由人手维护。一旦失真，「我们自动化程度很高」的幻觉会被喂给每一次决策，而没人会去核对。

**处置**：新建 `gen_task_registry.py`，台账**从工作流真实内容派生**——是现实的投影，就不可能再失真。CI 门禁校验其时效性；同时剔除状态时间戳参与比对，避免门禁天天误红（**一个天天报警的门禁等于没有门禁**）。

---

## 三、新增能力清单

### 11 个脚本（全部零第三方依赖，仅用标准库）

| 脚本 | 作用 | 实测结果 |
|------|------|----------|
| `state_bus.py` | 机器可读状态总线，替代 Markdown 散文做闭环间通信 | 6 个状态域 |
| `notify.py` | 通知总线：Issue + Webhook + 落盘兜底，指纹去重、自动销警 | 6h 冷却 |
| `health_probe.py` | 三路探测（HTTP/TCP/DNS）多数表决，消除误报 | 4/4 healthy |
| `validate_workflows.py` | 工作流静态校验，6 类错误 + 3 类警告 | 0 错 0 警 |
| `meta_monitor.py` | 元监控 M1–M6：**谁来监控监控者** | 4/4 healthy |
| `gen_task_registry.py` | 台账自动派生 | 15 任务 |
| `publish_content.py` | 零凭据四渠道发布 | 3 篇博客 |
| `registry_tracker.py` | 生态位追踪 | 覆盖率 25% |
| `fetch_vuln_feeds.py` | OSV / NVD / GitHub Advisory 权威源 | **93 条真实漏洞** |
| `intel_to_rules.py` | 情报→检测规则转化引擎 | 19 条规则 |
| `feedback_aggregator.py` | 四源反馈聚合 → 真实写入 ROADMAP | 8 项待采纳 |

### 关键设计取舍

**为什么坚持零第三方依赖**：项目自带 `dependency-check` 门禁，禁止 `requirements.txt` 和 `import requests`。所有新脚本一律使用 `urllib` + 标准库，因此工作流里那些 `pip install requests` 我全部删掉了——**装了也没用，还拖慢每次运行**。

**为什么元监控的 M6 要区分环境**：`GITHUB_TOKEN` 只在 CI 里自动注入，本地跑必然没有。如果一律判红，就会变成一条永远亮着的假警报，久而久之整个面板就没人看了。现在本地跳过、CI 内严格判定。

---

## 四、调度器守护任务（已注册 3 个）

GitHub Actions 内部的自检**无法发现 Actions 本身被禁用、配额耗尽、仓库整体静默**这类故障。因此在本机调度器注册了带外守护——这是唯一能从仓库外部交叉验证的视角。

| 任务 | 频率 | 核心判断 |
|------|------|----------|
| AIShield 体系守夜（带外巡检） | 每日 08:30 | health 域 >12h 未更新 或 meta 域 >48h 未更新 → **P0：Actions 整体没在跑** |
| AIShield 周度生态位与增长复盘 | 每周一 09:00 | 「这一周，项目在外部世界的存在感有没有真的增加」 |
| AIShield 月度战略与闭环有效性审计 | 每月 1 日 10:00 | 审「有没有产生真实价值」，判定每条闭环：有效 / 空转 / 停转 |

刻意**没有**注册更多——本地任务不该重复 GitHub Actions 已经做的事，它的价值只在带外视角。

---

## 五、仍然存在的短板（不回避）

| 短板 | 现状 | 建议 |
|------|------|------|
| 生态位覆盖率仅 25% | npm 未发布、MCP registry 未收录、Pages 404 | 投入产出比最高的是 **npm 发布**，一次操作长期获客 |
| 用户反馈源为空 | 四源聚合中 S1（用户 Issue）为 0 项 | 无真实用户是根本问题，不是自动化能解决的 |
| `NOTIFY_WEBHOOK` 未配置 | 告警只能走 GitHub Issue | 配一个企微/飞书机器人 webhook，5 分钟的事 |
| 首次运行验证 | 所有工作流已本地静态验证，但**尚未在 GitHub 上真实跑过一轮** | 建议手动触发 `meta-monitor.yml` 与 `self-heal-closed-loop.yml` 各一次 |

**最后一项最重要**：静态校验能保证「能被解析」，不能保证「能跑通」。合并后请手动触发一次，看真实结果。

---

## 六、验收命令

```bash
PY=C:/Users/xing/.workbuddy/binaries/python/versions/3.13.12/python.exe

$PY scripts/validate_workflows.py        # 期望：0 错误 0 警告
$PY scripts/meta_monitor.py              # 期望：4/4 healthy
$PY scripts/gen_task_registry.py --check # 期望：台账与实际一致
$PY scripts/health_probe.py              # 期望：4/4 healthy
$PY tests/run_all.py                     # 期望：99 passed, 0 failed
```
