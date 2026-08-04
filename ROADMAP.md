# AIShield 路线图

> 基于竞品生态扫描和 Agent 营销体系研究制定的迭代计划

## Phase 1: 基础设施完善（已完成）

- [x] OWASP MCP Top 10 对齐的 133 条安全规则
- [x] MCP StreamableHTTP 端点（JSON-RPC 2.0）
- [x] A2A Agent Card 自动发现
- [x] Agent-First 一键入驻（注册 + API Key + 快速指引）
- [x] OpenAPI 3.0.3 规范（`/openapi.json`）
- [x] 结构化错误码（`error_code` + `error_id`）
- [x] 账户系统（注册/登录/余额/充值）
- [x] DID + 信誉系统
- [x] 技能市场 + 沙箱
- [x] GEO 优化（sitemap, robots, agent-card, feeds）
- [x] CI/CD 流水线
- [x] GitHub Issue 模板 + 自动标签 + Stale Bot
- [x] CONTRIBUTING.md

## Phase 2: 原生分发与生态卡位（0-3 个月）

### MCP 生态
- [x] 向 awesome-mcp-servers 提交 PR 上架（PR #2，等待合并）
- [x] 发布 MCP Server 到 Smithery.ai 目录（lm203688/aishield）
- [x] 提交 Cursor Directory（等待安全扫描）
- [x] 配置 Glama.ai Topics（等待爬虫索引）
- [ ] 发布 `aishield-mcp-server` npm 包（本地 stdio wrapper）
- [ ] 申请 Claude Desktop 官方推荐
- [ ] 申请 VS Code Copilot MCP 集成

### GitHub 生态
- [ ] 发布 GitHub Action（`aishield-security-scan`）到 Marketplace
- [ ] 支持 PR 评论自动标注安全风险
- [ ] 支持 SARIF 格式输出（与 GitHub Advanced Security 兼容）
- [ ] 申请 GitHub Sponsors

### A2A 生态
- [ ] 完善 A2A Agent Card（增加更多技能描述）
- [ ] 实现 A2A Task 路由（`POST /api/v1/a2a/task`）
- [ ] 接入 Google A2A 测试套件

### 内容营销
- [ ] 建立博客（aishield.tools/blog）
- [ ] 每周发布 1 篇 AI Agent 安全分析文章
- [ ] 发布《OWASP MCP Top 10 中文解读》系列
- [ ] 在 Reddit r/LocalLLaMA、Hacker News 发布产品

## Phase 3: 社区飞轮（3-6 个月）

### 社区建设
- [ ] 建立 Discord 社区
- [ ] 建立 GitHub Discussions
- [ ] 每月社区更新（This Month in AIShield）
- [ ] 开源维护者计划（免费 Pro 套餐）
- [ ] 安全规则贡献者署名机制

### 数据驱动迭代
- [ ] 集成 Sentry（错误监控）
- [ ] 集成 Plausible（网站分析）
- [ ] 设计 Telemetry 方案（分级控制、透明化、匿名化）
- [ ] 建立功能使用频率看板

### 规则库增长
- [ ] 开放规则贡献接口
- [ ] 建立规则评审流程
- [ ] 目标：规则库从 133 条增长到 500 条
- [ ] 引入社区 CVE 案例库

## Phase 4: 商业化与信任层（6-12 个月）

### 企业功能
- [ ] 私有化部署方案
- [ ] SSO / SAML 集成
- [ ] 审计日志与合规报告
- [ ] SLA 保障

### 信任基础设施
- [ ] Agent 信誉评分公开查询 API
- [ ] Agent 间交易担保（escrow）
- [ ] 链上信誉存证（可选）
- [ ] 与主流 Agent 框架（LangChain, AutoGPT, CrewAI）深度集成

### 国际化
- [ ] 英文文档完善
- [ ] 日文、韩文社区拓展
- [ ] 参加国际安全会议（Black Hat, DEF CON, OWASP）

## 自动迭代体系（已部署运行）

基于三层闭环 × 情报矩阵 × 业务飞轮，让项目在无人干预下持续进化。

| 层级 | 频率 | 说明 | 状态 |
|------|------|------|------|
| L1 本体现状 + L3 推广 | 每日 02:00 | API 健康、star 数、PR 状态、平台收录 | ✅ 运行中 |
| L2 外部情报 + 趋势判断 | 每周一 02:00 | HuggingFace、竞品、博主、arXiv、6 维动态发现 | ✅ 运行中 |
| 三层联动 + 飞轮诊断 + 产品上新 | 每月 1 日 03:00 | 飞轮 ROI、原则符合性核对、研发建议 | ✅ 运行中 |
| 战略复盘 | 每季度首日 03:00 | 方向校准、Pivot 判断、OKR 制定 | ✅ 运行中 |

**核心原则**：构建 Agent 生态（核心目标）| 自动化 | 生态化 | 盈利化

## 竞品监控清单

| 竞品 | 监控重点 | 频率 |
|---|---|---|
| Guardrails AI | Hub 新验证器、企业客户案例 | 每周 |
| MEDUSA | 新增规则类型、Star 增长 | 每周 |
| Agentic Security | 模糊测试新能力、CI 集成 | 每月 |
| Palo Alto AIRS | 产品更新、定价策略 | 每月 |
| Anthropic MCP | 协议更新、安全指南 | 实时 |

## 成功指标

| 指标 | 3 个月目标 | 6 个月目标 | 12 个月目标 |
|---|---|---|---|
| GitHub Stars | 500 | 2,000 | 10,000 |
| MCP Server 调用量 | 1,000/月 | 10,000/月 | 100,000/月 |
| 注册 Agent 数 | 100 | 1,000 | 10,000 |
| 安全规则数 | 200 | 500 | 1,000 |
| 博客文章数 | 12 | 24 | 50 |
| 社区成员数 | 50 | 200 | 1,000 |

---

**最后更新**: 2026-07-23
**下次评审**: 2026-08-23（首月自动迭代运行后复盘）

<!--AUTO_ADOPTED_START-->

## 自动采纳项（迭代闭环产出）

> 由 feedback_aggregator 于 2026-08-04 自动聚合四路输入生成，每轮覆盖更新。勾选即视为已处理。

| 优先级 | 来源 | 事项 | 参考 |
|--------|------|------|------|
| P1 | S2 生态位待办 | npm 包分发（Agent 直接调用入口）：执行 npm publish —— 这是 Agent 能'直接用上'AIShield 的最短路径 | — |
| P1 | S2 生态位待办 | MCP 官方 Registry 收录：向 modelcontextprotocol/registry 提交 server.json —— 生态入口即用户入口 | — |
| P1 | S4 情报驱动 | 评审本轮 52 条新增高危漏洞的检测覆盖情况 | — |
| P2 | S1 用户反馈 | [P1] 评审本轮 52 条新增高危漏洞的检测覆盖情况 | [链接](https://github.com/lm203688/aishield/issues/7) |
| P2 | S1 用户反馈 | [P1] 修复自动化体系缺陷 — M2 运行活性: 2 个任务超期未执行 —— 这是静默失效的典型信号 | [链接](https://github.com/lm203688/aishield/issues/6) |
| P2 | S1 用户反馈 | [P1] 内容站 GitHub Pages：在仓库 Settings → Pages 开启 GitHub Pages（Source: main /docs） | [链接](https://github.com/lm203688/aishield/issues/5) |
| P2 | S1 用户反馈 | [P1] MCP 官方 Registry 收录：向 modelcontextprotocol/registry 提交 server.json —— 生态入口即用户入口 | [链接](https://github.com/lm203688/aishield/issues/4) |
| P2 | S1 用户反馈 | [P1] npm 包分发（Agent 直接调用入口）：执行 npm publish —— 这是 Agent 能'直接用上'AIShield 的最短路径 | [链接](https://github.com/lm203688/aishield/issues/3) |
| P2 | S2 生态位待办 | GitHub Topics 检索曝光：补齐 GitHub topics: ai-security —— 零成本获取平台内检索流量 | — |
| P2 | S4 情报驱动 | 补齐 OWASP LLM Top10 未覆盖类别的检测规则：LLM02, LLM03, LLM04, LLM08, LLM09, LLM10 | — |

<!--AUTO_ADOPTED_END-->
