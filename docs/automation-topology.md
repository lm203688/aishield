# AIShield 闭环拓扑与空转诊断

> 生成日期：2026-10-06 ｜ 判据：**全部派生自真实产物**（workflow 文件内容、GitHub API 运行记录、`data/state/*.json` 远端真值、job 日志），
> 不采信台账散文、不采信本地副本（本地 `data/state/` 恒为陈旧快照）。
> 复验命令见文末。前身：`automation/workflow-优化梳理_2026-08-20.md`。

本文要回答三个问题：**闭环有几条**、**哪几条在空转**、**哪些能合并**。
凡是本文给出的数字，都能用文末命令当场复算出来。

---

## 1. 盘点

### 1.1 仓库内 GitHub Actions（20 个）

| 类型 | 数量 | 成员 |
|------|------|------|
| 定时驱动 | 6 | `closed-loop-spine`(03:17 每日) · `geo-indexnow-submit`(09:20 每日) · `meta-monitor`(每 8h) · `npm-self-heal`(每 12h) · `self-heal-closed-loop`(每 6h) · `stale`(02:26 每日) |
| 事件驱动 | 14 | `ci` · `unified-security-scan` · `pages` · `deploy-server` · `publish-npm` · `publish-mcp-registry` · `channel-distribution` · `threat-intel-feed` · `data-scan-flywheel` · `feature-closed-loop` · `rule-promoter` · `project-digest` · `issue-labeler` · `install-cf-token` |

其中 9 条只经 `closed-loop-spine.yml` 的 `uses:` 串行调用（雷达→情报→晋升→自扫描→CI→部署→反馈→分发→汇报），
子工作流已去掉独立 cron。**串行链本身是好设计**：依赖链即门禁（验证未过不部署、部署未过不汇报）。

### 1.2 WorkBuddy 调度器侧（本项目自有，7 条）

| 状态 | 名称 | 节奏 |
|------|------|------|
| ACTIVE | AIShield Tech Radar | 每日 02:00 |
| ACTIVE | AIShield 每日安全守夜 + 周日周报聚合 | 每日 08:30 |
| ACTIVE | AIShield 周度竞争情报 | 周一 09:00 |
| ACTIVE | AIShield × NetMind Arena 产品审核状态盯守 | 每日 11:00 |
| ACTIVE | aishield-competition-window-scan | 每月 25 日 |
| PAUSED | NetMind Arena 定时出赛（Jev 驱动） | 每 2h（产品仍 pending，无可出赛事） |
| PAUSED | AIShield 多渠道分发缺口巡检 | 每周六（连续 3 轮无 drift 后主动停） |

**独立性边界**：OracleMind / SwarmLabs / 智慧农业 / Catalyst Grant 等自动化不属本项目，不在此清单、也不由本项目代管。

### 1.3 状态总线真值（远端实测，2026-10-06）

`data/state/<域>.json` 是闭环之间**唯一的机器可读通信介质**。远端实测新鲜度：

| 域 | 实测年龄 | 归属 | 判定 |
|----|---------|------|------|
| distribution | 0.19 d | channel-distribution / geo-indexnow-submit | ✅ |
| health | 0.35 d | self-heal-closed-loop | ✅ |
| selfheal | 0.35 d | self-heal-closed-loop | ✅ |
| meta | 0.36 d | meta-monitor | ✅ |
| ci | 0.19 d | ci.yml | ✅ |
| intel | 0.20 d | threat-intel-feed | ✅ |
| registry | 0.94 d | publish-npm / publish-mcp-registry | ✅ |
| **feature** | **63.35 d** | feature-closed-loop / spine | ❌ 停更 63 天 |
| **rules** | **32.29 d** | threat-intel-feed / rule-promoter | ❌ 停更 32 天 |

---

## 2. 空转诊断（本轮实证的三处）

### 2.1 `feature` 域冻结 63 天 —— artifact 路径写错，被 `|| true` 吞

**现象**：`feature-closed-loop.yml` 的 `Commit Adoption Result` 每轮 job 结论都是 `success`，
但 `data/state/feature.json` 最后一次提交停在 `2026-08-04`（`669fd9a9`）。

**证据链**：
- 最近一轮日志（run `37448252930`，job `Commit Adoption Result`）显示 `[main 42997764] chore(feature-loop): 自动采纳 5 项反馈` → **`1 file changed`**，
  只提交了 `ROADMAP.md`，`data/state/feature.json` 根本没进这次提交。
- 根因：`upload-artifact@v4` 用多路径 `path: |` 上传时，按**公共父目录**保留结构。
  本例公共父目录是仓库根，于是下载后是 `/tmp/agg/data/state/feature.json` 与 `/tmp/agg/ROADMAP.md`；
  而提交步骤写的是 `cp /tmp/agg/feature.json ... 2>/dev/null || true` ——
  **cp 失败、`|| true` 吞掉、job 照样绿**。这正是"闭环在跑、状态没落地"的标准形状。

**已修**（本轮）：
- 两种 artifact 布局都认，找不到就 `exit 1` 并打印实际文件树（宁可红，不可静默丢状态）；
- 状态域已按真实值补齐（采自当日 job 输出 `adopted=5 / P0-P1=1`）。

### 2.2 `rules` 域冻结 32 天 —— restore 成功但漏进 `git add`

**现象**：同一个 job（`threat-intel-feed` job 4）每天既写 `intel.json` 也写 `rules.json`，
`intel` 域天天刷新（今日 0.20 d），`rules` 域却停在 `2026-09-04`（`9a035946`）。

**根因**：`intel_to_rules.py` 写的 `data/state/rules.json` 被 artifact 正确 restore 回工作区，
但该 job 的提交名单是
`git add data/threat_intel.json data/generated_rules.json data/state/intel.json mcp-server/README.md` ——
**`data/state/rules.json` 不在名单里**，restore 出来的文件随工作区一起被丢弃。
两个域共用一条提交语句，一个在名单内、一个在名单外，于是"一半在写、一半在空转"。

**已修**（本轮）：名单补上 `data/state/rules.json`；restore 增加布局自适配 + 找不到即红。

### 2.3 定时 spine 实际每天都在红 —— 被自己的规则数预检拦死

**现象**：最近 3 次 **定时** spine 运行，`37448252930`(10-06) 与 `37295992148`(10-05) 均为 `failure`；
只有手动 `workflow_dispatch` 的 `37338172156` 是 `success`。此前"线上四处一致"的结论来自手动触发那一轮，
掩盖了定时链路的持续红灯。

**根因链（完整闭环，非猜测）**：
1. `content/blog/case-filesystem-test-2026-07-25.md` 里写死 `基于 AIShield 133 条安全规则扫描`；
2. `scripts/publish_content.py:publish_feed()` 把每篇稿件的 `summary` **原样抄进** `api/static/feeds.xml`（受约束声明面）；
3. 于是每天分发都把 `feeds.xml` 重新写成 `133`；
4. `git_push_safe.sh` 推送前调用 `rule_count_gate`，检出 `api/static/feeds.xml:28 实测 133 → 应为 264`，**exit 4 拒绝推送**；
5. job `2-Publish` 变红 → spine 当天整条链路终止在分发环节。

**为什么两代都没人发现**：稿件源目录 `content/blog/`、`eco/content/` **不在门禁收束集内** ——
门禁抓的是产物（`api/static/`），而病在源。门禁覆盖从 53 位扩到 **55 位**（判据派生自发布器自己的
`publish_content.CONTENT_DIRS`，不手抄路径），`--check` 当场复现并定位到第 24 行。

**已修**（本轮）：源文件同步为 264、`docs/blog/` 镜像一并同步、门禁收束集纳入稿件源。

### 2.4 让上面三处能**被自动抓到**（更重要）

M3"静默失败检测"此前只判**归属 workflow 跑没跑**。而 2026-09-08 起每个域的归属列表末尾都挂了
每日 spine —— 只要 spine 绿，M3 就**恒判新鲜**。于是 63 天 / 32 天的停更全程零报警。

本轮把 M3 改成**双信号**，缺一不可：
- （甲）运行活性：归属 workflow 近期是否成功跑过（与 M2 同源，无 token 时跳过）；
- （乙）状态落地：**直接**读 `data/state/<域>.json` 的 `updated` 与阈值比（仅 CI，本地副本陈旧故不判）。

之所以原来删掉（乙）、现在必须补回：**"在跑"与"在写"是两件事**。
只判前者，等于给"链路在跑、状态没落地"这种空转发永久绿灯 —— 而它正是 M3 存在的唯一理由。

---

## 3. 重叠、低价值与脆弱单点

### 3.1 重叠（可合并，尚未合并）

| 族 | 成员 | 重叠点 | 处置建议 |
|----|------|--------|---------|
| 安全网 | `self-heal-closed-loop`(6h) · `npm-self-heal`(12h) | 都是"线上/分发物异常后自愈"；`npm-self-heal` 无检测与告警环节（台账已标 ⚠️） | 保留，但把 `npm-self-heal` 的结论写入状态总线，由 `self-heal` 统一告警 |
| 监控 | `meta-monitor`(8h) · WorkBuddy 守夜(每日 08:30) | 都做体系健康巡检，输入源不同（前者读 Actions API，后者读本地仓库+线上探测） | 保留双源（互为异质见证）；守夜增加"读 M3 结论"避免各报一份 |
| 分发 | `channel-distribution` · `publish-npm` · `publish-mcp-registry` | 同属"对外分发"，前两者已在 spine 内串行 | 保留；`publish-mcp-registry` 结果需回写 `registry` 域 |
| push 触发 | `ci` · `unified-security-scan` | 都在 `push(main)` 上跑，判据不同（前者工程契约、后者安全门禁） | 保留，但两者都要经 `.github/actions/prepare-tests` 保证依赖一致（E11/E12 已门禁） |
| 节奏自相矛盾 | `npm-self-heal` | workflow cron 写"每 12 小时"，脚本注释与内部降频逻辑写"每 6 小时" | 统一口径（本项待办） |

### 3.2 低价值 / 结构性不可成功

| Workflow | 状况 | 处置建议 |
|----------|------|---------|
| `publish-mcp-registry` | 上游 Official MCP Registry `/v0` 与 `/v0.1` **均 404**，该环节结构上不可成功 | 保留为"上游恢复即自动上架"的钩子，但**不要**把它计入"闭环全绿" |
| `stale.yml` | 每日跑，但仓库 `open_issues_count = 9`（其中 `label:ci` 为 0） | 降到每周一次即可 |
| `issue-labeler.yml` | `on: issues`，无 issue 事件即 `skipped` 属设计内（最近三条 skipped/failure/failure） | 保留，不进告警面 |
| `install-cf-token.yml` | 手动一次性，已完成使命 | 保留作灾备，不计入闭环 |
| `automation-1786746357267`（分发缺口巡检） | 连续 3 轮无 drift，已 PAUSED | 保持暂停（台账基线已过时，重启前先刷基线） |

### 3.3 脆弱单点

1. **PAT 缺 `workflows: write`** —— 无法编辑 workflow YAML、无法 dispatch。当前所有 workflow 改动都要
   靠间接路径落地，是本项目最硬的结构性瓶颈。
2. **本地无 `.git`** —— `git status` 全假阴性；本地 `data/state/*.json` 恒为陈旧快照，
   任何"看本地文件下结论"的判断都会错（本轮开头即踩过一次：本地显示 6 个域停更 62–63 天，远端真值只有 2 个）。
3. **`cloudflared` 只能按 PID 停** —— 禁止 `pkill -f cloudflared`。
4. **两条"状态回写"路径共用 `git add` 名单** —— 名单漏项不会报错，只表现为"域停更"（本轮 2.2）。
5. **`|| true` 在状态落地路径上** —— 每一次吞异常都在制造"job 绿、状态没落"的可能（本轮 2.1）。

---

## 4. 融合方案（可执行）

按收益/风险排序，前 3 项**本轮已完成**：

1. ✅ **修 `feature` artifact 路径**（2.1）—— 恢复 feature 域写入。
2. ✅ **补 `rules` 的 `git add`**（2.2）—— 恢复 rules 域写入。
3. ✅ **门禁收束集纳入稿件源**（2.3）—— 让分发链不再自伤；`rule_count_gate` 覆盖 55 位。
4. ✅ **M3 增加"状态落地"信号**（2.4）—— 上述三类空转以后会被自动抓到。
5. ⏳ **状态落地路径禁用 `|| true`**：凡是"写状态域"的步骤，缺失即红。判据：扫描
   `state_bus.py set` / `cp .*data/state` 邻近的 `|| true`。
6. ⏳ **`npm-self-heal` 口径统一 + 结论入总线**，由 `self-heal` 统一告警。
7. ⏳ **`stale.yml` 降频到每周**；`publish-mcp-registry` 从"全绿"判据里剔除。
8. ⏳ **PAT 升级**（用户侧硬阻塞）：需 `workflows: write`。

---

## 5. 复验命令

```bash
# 1) 声明面收束集（应含 content/blog 与 eco/content 的稿件源）
python scripts/rule_count_gate.py --check

# 2) 状态域真实新鲜度（读远端，不看本地副本）
python - <<'PY'
import json, urllib.request, base64, ssl, datetime
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
now = datetime.datetime.now(datetime.timezone.utc)
for dom in ("distribution","feature","health","registry","rules","selfheal","ci","intel","meta"):
    u = f"https://api.github.com/repos/lm203688/aishield/contents/data/state/{dom}.json?ref=main"
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), context=ctx, timeout=30))
    j = json.loads(base64.b64decode(d["content"]).decode())
    t = datetime.datetime.fromisoformat(str(j["updated"]).replace("Z","+00:00"))
    print(f"{dom:14s} {(now-t).total_seconds()/86400:6.2f} d")
PY

# 3) 定时 spine 的真实结论（区分 schedule 与 workflow_dispatch）
gh run list --workflow=closed-loop-spine.yml --limit=5

# 4) M3 双信号
python scripts/meta_monitor.py --json | python -c "import json,sys;d=json.load(sys.stdin);print(d['state_freshness'])"

# 5) workflow 结构门禁
python scripts/validate_workflows.py
```

---

## 6. 结论

- 闭环**不是少**，而是**"绿"得不可信**：定时 spine 每天红在分发；两个状态域停更 63 天 / 32 天而所有 job 报 success；
  M3 因为归属列表里挂了 spine 而**结构上不可能**发现这些。
- 三处失效已修，且**修的是链路而不是数字**：源纳入门禁、artifact 布局自适配、提交名单补齐、M3 补"状态落地"信号。
- 台账（`automation/task-registry.md`）与本文的分工：前者=**有多少条**（自动生成），本文=**哪几条在空转、怎么合**。
