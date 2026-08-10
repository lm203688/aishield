# AIShield 项目长期记忆

## 定位
Agent 原生 AI 工具安全扫描器：扫 MCP server / AI skills / GPTs / prompts，4 维评分 + 认证 badge + Guardrail MCP 拦截。规则底座 **214 条 MCP / 220 条 Skill**（110 MCP + 60 Agentic ASI + 31 中文注入 + 11 SANDBOX 沙箱硬化 + 2 雷达晋升规则），对齐 OWASP MCP Top10 + Agentic AI Top10 + **SANDBOX 沙箱逃逸类**。**零第三方依赖（仅 urllib）**，本地规则引擎 + 可选远程 LLM 语义后端（本地 Ollama 已按用户要求移除）。
仓库 `lm203688/aishield`（**public**，Pages baseurl `/aishield`）；npm 包 `aishield-mcp-server` v4.2.2。

## 品牌与竞争
- 名字被 Bosch AIShield / aishield.ai 占用，**改名已取消**（用户保留，持有 aishield.tools）。叙事区隔：vs Claude Security = 本地不上云；vs aishield.ai = 开源免费；vs Bosch = 轻量聚焦 MCP·Agent。
- 最危险竞品 **mcp-audit**（Apache2.0、89 SAST 规则、SARIF+CycloneDX、全离线）。大厂做语义审计（Anthropic/Microsoft MDASH/Cisco Antares）——不硬刚。
- 空白卡位 =「本地不上云 + MCP+Agentic 双维 + 中性信任机构 + Fleet 看板 + 机器可结算付费认证」。快照 `docs/intel/2026-08-04-landscape.md`，活态势表在私有 skill `~/.workbuddy/skills/aishield-ops/references/competitive-landscape.md`。
- **关键认知：缺口是可见性，不是能力**。信任体系早已 spec+data 化，杠杆是露出既有体系 + GEO/agent 化。

## 能力全景（截至 2026-08-06）
- **扫描引擎**：`scanner/rules.py`（ASI01–10 各 6 条）、`engine.py`（`calculate_scores` 由 `_DIM_CONFIG` 驱动 + `score_breakdown`/`top_deductions`，`explain_score()`）、`sbom.py`（CycloneDX/SARIF）、`osv.py`（OSV.dev CVE，默认离线）、`attack_path.py`（hitting-set 最小移除集 + D3 图数据）、`policy.py`（策略即代码 + `policies/default.json`）、`telemetry.py`（`AISHIELD_TELEMETRY=1` 匿名聚合）、`live_probe.py`（只读探针，**不 spawn**）、`registry_discovery.py`、`exporters.py`（Nucleus/Splunk）、`fleet.py`（FleetService 多 server 聚合）、`client_discovery.py`。
- **核心不变量：绝不 spawn 被扫配置中的命令**（竞品为读 `tools/list` 会真实执行）。代价：不覆盖运行时工具描述注入，已在文档明写。基准 20 良性 0 误报 / 10 恶意 10/10。
- **API**：`api/server.py`（BaseHTTPRequestHandler，eco 模块用 `register_routes(handler)` monkey-patch 链式包装 do_GET/do_POST）、`trust_api.py`。前端 `api/static/{attack-graph,fleet,enterprise}.html`（全部离线自包含，0 CDN）。
- **商业化（双轨付费认证闭环已闭环）**：`eco/{badge,payment,x402,monetization,credentials,hupijiao,account,spend_cap,attestation,runtime_governance}.py`。`BadgeMonetization` = x402 402 支付要求(USDC, agent→agent) + **虎皮椒 CNY 轨道**(微信/支付宝, 国内个人) → 统一订单簿 `data/payments.json` → 回调/notify 履约签发认证。虎皮椒四道安全不变量(商户归属/签名/金额防篡改/重放幂等) + SSRF 白名单 + 密钥零泄露(`credentials.py` 装载, 代码无明文)。`enterprise.html` 已加双入口。
- **支付层 spend cap（fail-closed 硬门槛）**：`eco/spend_cap.py`。per_tx/daily/monthly 三档；两阶段 reserve→commit/release 防并发透支；未知币种默认拒绝（不放大）；USDC→USD/RMB→CNY 归一；预留 TTL 过期显式补记不漏账；x402/虎皮椒双轨共用同一策略引擎（monetization 下单前 reserve、履约 commit、异常 release）。
- **运行时治理 kill switch（对齐 ASI08/10）**：`eco/runtime_governance.py`。决策优先级 kill_switch > deny_list > allow_list > default_deny；一键熔断 + 连续 high/critical 事故达阈值(默认 3)自动熔断；**哈希链审计日志**(append-only, 每条 prev_hash, 整链 verify_chain 篡改/删除/插入可定位)；策略损坏收紧为 default_deny。
- **持续鉴证订阅（Continuous Attestation，recurring + rug-pull 兜底）**：`eco/attestation.py`。active/grace/lapsed/cancelled 状态机；周期复扫(默认 7d)；分数<70 即吊销认证；降级检测；证据链哈希自校验；双轨定价(CNY/USD)；`trust_status()` 暴露「现在是否持续可信」。复用 `badge.CertificationService`(revoke/renew) 而非重写。
- **API 治理路由**：`api/server.py` 含 `/api/v1/governance/*`(status/audit/evaluate/kill/revive/incident/policy)、`/api/v1/spend-cap/*`(usage/policy)、`/api/v1/attestation/*`(plans/list/expiring/trust/subscribe/renew/cancel/run-cycle)；既有 `certify/request-payment[-cny]` 被 spend cap 拦下返回 **429**（区分「付不起」vs「参数错」）。
- **GEO/分发**：`docs/robots.txt`、`llms.txt`、`.well-known/agent-card.json`、`api/openapi.yaml`、`distribution/`（Claude Skill / GPT Store / HF）、`registry/server.json`、`action.yml`（GitHub Marketplace）、`benchmarks/run_bench.py`。
- **生态雷达（v2 双线闭环）**：`scripts/tech_radar.py`（每日 02:00 cron，6 类源 → `docs/intel/YYYY-MM-DD-tech-radar.md`）。**defend 线**：高严重度信号起草规则候选（JSON，格式对齐 `scanner/rules.py` 的 `{pattern:(desc,sev)}`，**杜绝原 `class X(Rule)` 虚构 API 的坏模板**）→ `scanner/_proposed/PROPOSED_*.json` → 经 `promote_rule.py` 闸门晋升 → `data/radar_rules.json`（独立库，不被 `generated_rules.json` 情报刷新抹掉）→ `scanner/rules.py::_load_radar_rules()` 载入 `ALL_RULES`（现 203）。**adopt 线**：`scripts/capability_gap.py` 对照 `CAPABILITY_CATALOG`（21 条现能力，强词+领域词+OUT_OF_SCOPE 过滤相邻领域噪音）产出「该造什么」Gap 列表，呼应「参考这些自己研发技术给项目」。
  - **arXiv 三级端点降级（根因修复）**：原 `export.arxiv.org` 长期 0 产出根因是 **DNS 解析失败（WinError 11002）非 API 宕机**；改为 `export.arxiv.org`(API) → `rss.arxiv.org`(分类 RSS) → `arxiv.org/list/<cat>/recent`(HTML) 逐层降级，全挂才返回带三段 `attempts` 的错误而非静默空列表。修复后产出 0→40，命中轨迹投毒/恶意技能/零信任 MCP 等靶心论文。
  - **晋升闸门 `promote_rule.py`**：六项校验（schema / 无 TODO / 正则可编译 / 不过宽 / 去重 / **良性语料 10 条零误报**）+ 写入 `radar_rules.json` + 归档 `scanner/_proposed/promoted/` + `sync_readme_counts()` 改写 README 保持 `test_mcp_contract.py` 契约绿。CLI：`--check`/`--promote`/`--promote-all`/`--list`。
  - **首条真实规则端到端跑通**："Trajectory Poisoning in Self-Evolving Agent Skill Systems" 论文 → 起草 → 填 2 条轨迹投毒规则 → 闸门放行 → 合入 ALL_RULES 203 → 真实样本检出 2 命中，良性零误报。
  - **测试**：`tests/test_tech_radar.py`（35 项，覆盖 arXiv 三级降级 / 分类器命中率不回归 / 采纳线弱词·越界过滤 / 闸门 5 拦 1 放 / 晋升真实生效+良性零误报 / README 同步幂等 / 草稿 JSON 格式须对齐引擎结构）。
  - hubport（呼波特）已在 USER_PLATFORMS 跟踪。WorkBuddy 自动化 `automation-1786262658410`（daily 02:00 北京）。
- **投资人 30/60/90 天建议与报告 14 项缺口已全部落地**（`docs/investor-strategy-2026-08.md` §8）。测试 `tests/run_all.py` 全量 **404 通过 / 0 失败 / 9 skipped**（unittest，无 pytest），含 `test_hupijiao.py` 35 项 + `test_governance.py` 67 项（spend cap/governance/attestation）+ `test_tech_radar.py` 35 项（雷达链路各环不得静默失效）+ `test_workspace_scan.py` 25 项（Agent 计算机预扫）+ `test_sandbox_rules.py` 9 项 + `test_guardrail_harness.py` 13 项 + `test_attestation_live.py` 4 项。

## 发布链阻塞（待用户）
- ✅ GitHub Pages 已部署。✅ **npm 已发布**：`aishield-mcp-server` 在 npm 上 `latest=4.2.2`（4.2.0/4.2.1 于 2026-08-05、4.2.2 于 2026-08-07 成功发布，均经核验）。`publish-npm.yml` run #11（ref v4.2.2）success，verify 步骤 `npm install` + registry 轮询通过。早期的「NPM_TOKEN 只读 / E403」为发布前陈旧记录，已作废。
- **变更发布流程**：`publish-npm.yml` 触发方式 = release:created / push tag `v*` / workflow_dispatch（dry_run 开关）。门禁钉死六处版本一致 + tag 匹配 + 版本未重复；`npm-self-heal.yml` 每小时探测，未发布且 `NPM_TOKEN` 有效则自动 dispatch 发布。
- **若未来某次发布再报 403**：根因是仓库 Secret `NPM_TOKEN` 失效/只读，唯一修复 = 用户在 npmjs.com 重新生成 **Automation token**（或 Granular 勾 Packages:Read+Write）并更新仓库 Settings → Secrets → Actions → `NPM_TOKEN`。更新后 self-heal 每小时自动续跑，或手动 dispatch `publish-npm.yml`。

## 待办路线图
1. 中立跨注册中心发现层（104k agents / 15 registries / 0 互操作）——仍挂起。
2. ✅ 运行时治理 kill switch（ASI08/10）已落地（`eco/runtime_governance.py` + 哈希链审计 + 自动熔断）；剩余 = 行为监控采集接入 + CI 门禁调用 evaluate。
3. Fleet 接 `monitor.py` 版本变更流做持续态势；x402 接真实 facilitator 完成链上结算；enterprise 多租户账户层。
4. **Agent 计算机安全底座（2026-08-10 新增战略方向）**：forge/agent-forge/forgevm/Open Interpreter/Goose/Cloudflare Sandbox 只做 OS 级隔离、不做工具/skill 内容安全 → AIShield 卡位"agent 计算机的内容安全平面"。**backlog ①~④ 已全部完成（2026-08-10）**：① ✅ 启动前 workspace 预扫(`scanner/workspace_scan.py`+`scripts/scan_workspace.py`，25 项测试) ② ✅ 沙箱硬化规则包(`scanner/rules.py` 新增 `SANDBOX_RULES` 11 条 + `tests/test_sandbox_rules.py`，恶意全检出/良性零误报) ③ ✅ Guardrail-as-harness 适配器(`eco/guardrail_harness.py`：intercept 复用 runtime_governance + 参数 critical 护栏 + MCP 风格 stdio JSON-RPC，13 项测试) ④ ✅ 持续鉴证接 live agent(`eco/attestation.py` 支持 `workspace_path` → 每周期 `preflight()` 重扫、漂移吊销 + `tests/test_attestation_live.py`，4 项测试)。Cloudflare `@cloudflare/computer` 评估见态势表 7.6：互补非竞品，验证"隔离≠安全"、其"大脑/双手分离"==我们的 harness 架构。详见 `aishield-ops/references/competitive-landscape.md` 第七节。

## 自动化与巡检
- 日度 `automation-1785826846646` 体系守夜（带外巡检）08:30，报告写 `eco/reports/guard-YYYYMMDD.md`；周度 `automation-1785849857521` 竞争情报（周一）。
- **带外巡检核心价值**：仓库内自检看不到「Actions 被禁用/配额耗尽/整体静默」。必查 = GitHub API 最近运行时间 + 各 workflow `state` 是否 `active`。历史教训：self-heal 曾因 YAML 错静默失效 48 天。
- **最强存活信号 = 远端 `data/state/health.json` 的 `updated`**（Contents API 读）。本地同名文件会被巡检自身刷新，不可作为 CI 存活证据。

## 调度加速期（2026-08-05 → 08-30，08-31 回滚）
- 用户定调：**扁平 HOURLY**（原提「每 20 分钟」后改口"频率太高"）。13 个工作流 cron = `0 * * * *`；4 个 WorkBuddy 自动化 FREQ=HOURLY + validUntil=2026-08-30（系统不支持 MINUTELY）。
- 原始 cron 快照 `automation/schedule-snapshot-2026-08-05.json`；回滚由一次性自动化 `automation-1785890505506`（08-31 09:00）经 Contents API 还原并建 issue 提问。

## 工程铁律（踩过的坑）
- **推送姿势**：本地 `.git` 损坏 + git 协议到 github.com 不通 → 一律走 `scripts/gh_push.py`（Contents API PUT 带 sha）。推完必须 dispatch + 轮询复验，别只推不验。
- **当前 PAT 边界**（`.workbuddy/schedule-revert-pat.txt`，gitignored）：✅ 普通文件读写 / Actions 读 / dispatch（实测 `workflow_dispatch` 返回 204）/ workflow **disable·enable** / ✅ **写 `.github/workflows/*`（已获 `workflow` scope，PUT 200）** / ✅ **删仓库（已加 `delete_repo`，2026-08-10 增补）**。注：该 token 曾明文贴在对话里，建议干完本轮活后去 GitHub 撤销并重生成（轮换）。⚠️ `delete_repo` 属高危不可逆权限，程序化删仓库须用户明确确认后才执行。
  - 停用僵尸 workflow 用 `PUT /actions/workflows/{id}/disable`（只需 actions:write，绕开 workflow scope）。`Deploy to Railway` 已 disable（上游 action 仓库已删，17+ 连红；真实部署由 `deploy-server.yml` 承担）。
  - ⚠️ 12 个低风险仓库此前删除全部 403；PAT 现已加 `delete_repo`，可程序化删除，但属不可逆高风险操作，须用户明确确认后才执行。
- **门禁教训**：Security Scan 曾长期形同虚设，三段根因 = ① 缺 `source_url`(400) ② workflow 读顶层 `d['score']` 而响应只有 `report.overall_score`（恒 0）③ 远端热修被每小时 cron 的本地 stale 副本回退。**最终解法：改被守护对象而非门禁**——`/api/v1/audit` 顶层附加 `score`/`badge_level`/`risk_level`。**恒定输出的门禁等价于没有门禁**；已用 `tests/test_ci_contract.py` 钉死「门禁读的每个键 API 必须提供」。
  - audit 响应形状：`{success, score, badge_level, risk_level, report:{overall_score, security_score, ...}, powered_by, credits}`；必须带 `source_url`，本地约 110s。
- **台账漂移会红 CI**：`ci.yml` 有 `Assert task registry is up to date`；增删 workflow 后必跑 `scripts/gen_task_registry.py`。
- **环境**：Git Bash **无 `sleep`**（用 Python `time.sleep`）；**别用 `timeout`**（命中 Windows `timeout.exe`）。`rm` 需 Windows 风格绝对路径。npm 调用：`"C:/Users/xing/node/node.exe" "C:/Users/xing/node/node_modules/npm/bin/npm-cli.js" <cmd>`。
- **自带洞最难堪**：2026-08-05 `mcp-server` 自查 5 漏洞（2 high，含 SDK SSRF/路径穿越），`npm audit fix --package-lock-only` 归零。纳入每轮守夜必检。
- **密钥红线**：仓库 public，任何真实密钥（支付/PAT/token）只进 gitignored 本地文件或环境变量，**绝不进代码与提交历史**。

## 闭环 workflow 健康（2026-08-08 修复）
三个 hourly 失败闭环（Channel Distribution / Acquisition Automation / Data Flywheel）根因已钉死并修复，均在 main：
- **Channel Distribution**：`publish_content.py::discover()` 改为只返回**未发布**内容（比对 `data/state/published.json`），新增 `discover_all()` 供归档；消除 verify 把"已发布"误判"待发"的静默空转误报。
- **Acquisition Automation**：原 YAML 无 `permissions:` 声明 → 只读 token 致 `git push`/建 issue 403。修复 = repo 默认 `workflow_permissions=write`（API PATCH 200）。**若仍失败，用户须在 GitHub UI 复核 repo Settings → Actions → General → Workflow permissions = Read and write。**
- **Data Flywheel**：`.gitignore` 取消忽略 `data/batch_scans.json`（飞轮自建库必须入库），并忽略 `data/state/health.json`（guard 经 Contents API 直写 main，不受 gitignore 影响；flywheel 不再提交它，消除 push 冲突）。
- **约束（已解除）**：原 PAT 无 `Workflows:write` → 不能编辑 `.github/workflows/*.yml`、不能 `workflow_dispatch`（均 422/404）。2026-08-10 用户生成了带 `workflow` scope 的 classic PAT 存入 `.workbuddy/schedule-revert-pat.txt`，实测 `workflow_dispatch` 返回 204、可写 workflow YAML。同日又增补 `delete_repo`，现 PAT 已具备 repo / workflow / delete_repo 全能力。
