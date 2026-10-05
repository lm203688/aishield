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
   **统一 push 入口的退出码必须被尊重**：`bash scripts/git_push_safe.sh` 的失败
   （exit 1 重试耗尽 / exit 3 真冲突）不许用 `|| echo` / `|| true` 吞掉 —— 吞掉后
   并发冲突与产物丢失都不会被发现。确属装饰性回写、失败也确实安全时，
   必须在**紧邻上方注释**里写 `allow-push-degrade: <理由>`（理由必须非空）。
   由 `scripts/validate_workflows.py` 的 **E10** 强制 —— 它原先只盯字面量 `git push`，
   而报错信息又叫大家改用这个入口，等于"推荐了入口却对入口免检"，
   2026-10-05 与其他三条一起被归为同一类缺陷。
5. **事件型告警必须能销案。** "本轮新增 N 条漏洞" 类告警不会自动恢复，零新增即 resolve；
   不要把它当健康型告警只在恢复时 `--resolve`。
6. **跑测试/门禁的前提只能来自一处，且那一处必须是被派生校验的。**
   凡运行本仓入口（`tests/run_all.py` 或任何依赖闭包含第三方包的 `scripts/*.py`）
   的 job，都必须先引用 `.github/actions/prepare-tests` —— 由
   `scripts/validate_workflows.py` 的 **E11** 强制；该 action 里 `pip install`
   声明的包是否覆盖测试真实依赖，由 **E12** 双向 diff 强制（依赖从 import 图推导，
   不是人工清单）。
   历史事故（2026-10-05，**同一天两次**）：第一次是同一件事在 6 个 workflow 里各自
   实现、5 个漏装签名后端依赖 → 干净 runner 上 L1/L3 用例成片报假回归 → spine 在
   job 2 终止、其后 8 个 job 全 skipped；第二次是**刚收敛完**、新用例引入 pyyaml 而
   前置漏装 → 同型再挂一次（另外还有 3 个 job 属于同一类：各自 `pip install pyyaml`
   或什么都不装，其中自扫描 job 一直在降级环境下跑）。
   两个教训：① 这是**递进式**的，逐个补没用，只能靠统一入口 + 门禁；
   ② 收敛到一处之后，那一处的内容必须**派生**出来 —— 否则只是把「N 个漏点」换成
   「1 个漏点」，漏的形式从"改 6 个文件"变成"改 1 个文件但没人提醒你"。
7. **并发 push 时"哪些文件可自动解决冲突"的判据只能是"写入者唯一"，不能是路径前缀。**
   名单在 `.github/auto-resolvable-paths.txt`（`scripts/git_push_safe.sh` 读它），
   内容由 `scripts/validate_workflows.py` 的 **E13** 派生实测：每条 glob 的
   写入者必须存在且**唯一**（唯一生产者 = "最后写入者胜"成立的前提），
   0 个 → W7、≥2 个 → E13。
   历史事故（2026-10-05，第三条同型）：同一次复验里同一生产者被并发实例化，
   两份快照撞在 `data/generated_rules.json` 上，而判据是前缀 `data/state/` ——
   该文件被误判为"真实逻辑冲突"→ exit 3 → 当天闭环在 job 4 终止、其后 8 个 job
   全 skipped，还报了一次假警。前缀只是"这类文件长什么样"的代理，不是判据。
   加新条目：先确认该文件**只有一个** Python 写入者且是整体重写（可跑
   `python -c "import scripts.validate_workflows as V; print(V._write_map(['<文件名>']))"`），
   再把 glob 加进声明；门禁会替你复核。
8. **门禁的"覆盖面"本身也必须是派生的，不能是两处白名单里手抄的一半。**
   规则数门禁的覆盖面 = `TEXT_EXT`（后缀）∧ `_is_declared_surface`（路径）
   的**合取**。`scripts/declaration_surface_gate.py` 的「4. 门禁覆盖闭合」必须
   **直接问 `rule_count_gate.collect_files()` 要集合**，不得就地重算这两个条件；
   由 `test_gate_asks_the_authoritative_collector` 用源码级断言钉死。
   **豁免**（`rule_count_gate.EXCLUDE_FILES`）是特权：必须是 `路径 → 非空理由`
   的字典，无理由 = error、文件不存在 = 死豁免 = warn，由第 5 项
   `check_exempt_ledger()` 强制 —— 能悄悄变大的豁免表等于把门禁关掉一半。
   历史事故（2026-10-06，同型第 5 处）：旧实现只抄了路径白名单、漏了后缀白名单，
   `api/static/feeds.xml` 因此**在门禁外躺了两代**（门禁注释自承"仅仅因为 `.xml`
   不在元组里"），最后靠运行时探针才发现。补一个 `.xml` 只是治标：只要还有人
   手抄一半条件，下一个 `.css` / `.js` 会以同样的方式漏。
9. **跨模块可变状态必须经统一出口取模块对象。**
   `scripts.rule_count_gate`（按包名 import）与 `rule_count_gate`（按模块名 import，
   因为它既要能当脚本跑又要能被 import）是**同一份源码的两个模块实例**。
   改前者而门禁读后者 → 改动对门禁不可见；断言恰好是"应当为空"时就会得到**假绿**。
   凡需要注入/观察的模块级状态，一律走已抽出的访问器（如
   `declaration_surface_gate._rule_gate()`），并用 `is` 断言同一对象。
10. **改写对外声明面的自动提交，必须先验证再推送。**
    `[skip ci]` 本身不是缺陷（本仓 13 处都合法），缺陷是"**改写对外资产却没验证**"。
    判据：`scripts/git_push_safe.sh` 在推送前取「本次提交改动的文件 ∩ 声明面」
    （`rule_count_gate.declared_surface_changed()`，派生判据），非空则跑
    `rule_count_gate.py --check`，不一致 **exit 4 拒绝推送**；人/agent 侧由
    `scripts/_push_batch.py` 的 `_surface_precheck()` 对称守卫，**刻意不给逃生开关**。
    `validate_workflows.py` 的 **E14** 钉住这条：带 CI-skip 提交 + 暂存声明面路径 ⇒
    必须走统一入口（且入口**仍含**预检，防"预检被摘掉"）或在本 job 内自检。
    历史事故（2026-10-06，同型第 6 处，最要命的一处）：`channel-distribution` 的
    publish job 带 `[skip ci]` 重写 `api/static/feeds.xml`，用生成脚本里写死的 133
    覆盖了当天刚修好的 264，**全程零报警**；线上当时仍是 264（部署早于该提交），
    下一次部署才会把 133 发出去。闭环的写入者恰是唯一能绕过全部门禁的人。
11. **E10 与 E14 分工**：E10 管"失败不许被吞"，E14 管"**验证根本没发生**"。
    后者更隐蔽 —— jobs 全绿、文件确实推上去了，只是推上去的内容把门禁的结论推翻了。


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
python -m venv .venv && source .venv/bin/activate
pip install pytest cryptography pyyaml   # cryptography / pyyaml 都是**必需**的，不是可选增强

# 2. 跑全量测试
python tests/run_all.py

# 3. 自证隔离不变量
python scripts/prove_isolation.py
```

> `cryptography` 为什么必需：L1 可移植身份（JWKS 只发非对称公钥、第三方凭公钥离线验签）
> 与 L3 意图授权（AP2 Intent Mandate）建立在 Ed25519 上。缺它时 `eco/crypto_sign.py`
> 会静默降级成 hmac-sha256，那两组用例 fail-closed 成片报红，**看起来像产品回归**。
> `tests/run_all.py` 会在开跑前预检并中止（退出码 2），让你不必对着一屏误导性红找根因。
> `pyyaml` 为什么必需：`scripts/validate_workflows.py` 与 `scripts/meta_monitor.py`
> 靠它解析 workflow / 体检配置；缺它时校验器会报 `E1 PyYAML 未安装`，而依赖 YAML 的
> 用例会**静默跳过** —— 跳过即假绿（2026-10-05 第二次事故正是如此：本地 3 skip、
> CI 29 skip，没人发现那 31 个用例其实没在跑）。
> 这两个包由 `E12` 从 import 图**推导**校验，不是靠人记得同步。
> CI 侧由 `.github/actions/prepare-tests` 统一保证，本地无需对应 workflow 做任何事。

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
