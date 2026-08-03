# AIShield 周报 W31 (2026-07-27 ~ 2026-08-02)

> **生成日期**：2026-08-03
> **上游**：每日闭环 7/27~7/31 全部日报
> **下游**：下周每日闭环将根据本报告决策调整检测重点

---

## 一、本周关键标记

> **【🔴 服务中断第 8 天】aishield.tools 连续 8 天不可达**，从 Error 1033 → Error 525 → 腾讯云备案拦截，所有线上数据收集中断。
> **【🔴 推广全面阻塞】PR #10694 阻塞 8 天、Smithery 未部署 8 天、Glama 未提交 8 天、0 star / 0 fork / 0 issue。**
> **【🔴 威胁情报爆发】Agent 沙箱逃逸实战化（OpenAI→HuggingFace）、MCP 5 个 CVE、Prompt Injection 进化。**
> **【🟡 MCP 无状态大版本】7/28 发布，需评估兼容性，是本周技术响应重点。**

---

## 二、情报闭环（威胁 → 规则 → Agent → 验证）

### 2.1 威胁情报汇总

| 威胁类型 | 本周新发现 | 影响等级 | 现有规则覆盖 | 决策 |
|----------|-----------|----------|-------------|------|
| Agent 沙箱逃逸 | OpenAI→HuggingFace、Cursor/Codex/Gemini、Claude Cowork | 🔴 最高 | ❌ 无 | **立即采用** |
| MCP 凭证流转异常 | CVE-2026-16496（跨用户凭证继承） | 🔴 最高 | ❌ 无 | **立即采用** |
| MCP SSRF/DNS Rebinding | CVE-2026-14869、CVE-2026-35568 | 🔴 高 | ⚠️ 部分 | **立即采用** |
| Prompt Injection 进化 | GPT-Red 84% 成功率、IterInject | 🔴 高 | ⚠️ 静态覆盖 | **排期** |
| 渐进式提权 | 多轮对话诱导 Agent 突破权限 | 🟡 中 | ❌ 无 | **排期** |
| A2A v1.0 安全 | Agent Cards 暴露、跨组织委托 | 🟡 中 | ✅ 已覆盖 | **观察** |

### 2.2 规则更新执行

- **新增规则 1**：`sandbox_escape` — 检测路径遍历、/proc /sys 等敏感目录访问
- **新增规则 2**：`mcp_credential_flow` — 检测无状态请求中的异常 OAuth 凭证头
- **维持规则**：prompt_injection、banned_words、sensitive_data、pii_leak、hallucination
- **badge.py 阈值**：维持 Gold>=90, Silver>=70, Bronze>=50

### 2.3 Agent 安全统计

| 指标 | 数值 | 说明 |
|------|------|------|
| 本周安全检查数 | **0** | 服务不可达，无新流量 |
| 历史累计检查数 | **8** | 7/27 测试数据 |
| 安全通过数 | **5** | — |
| 拦截数 | **3** | sensitive_data(2)、pii_leak(3)、hallucination(1) |
| 拦截率 | **37.5%** | 测试数据，非生产 |

---

## 三、竞品闭环（动态 → 差距 → 决策 → 执行）

### 3.1 本周竞品重大事件

| 竞品 | 事件 | 影响 |
|------|------|------|
| F5 / CalypsoAI | F5 收购 CalypsoAI | 企业级 AI 安全竞争加剧 |
| Pipelock | 运行时 Agent 防火墙，48 DLP 模式 | AIShield 运行时防护差距大 |
| MCP Defender | Cursor/Claude 客户端插件 | 用户触点差距 |
| Snyk Agent Scan | ~1,800 stars，CI 集成 | 开发者工作流入口差距 |

### 3.2 差距与决策

| 差距 | 决策 | 排期 |
|------|------|------|
| 运行时 Proxy 防护弱 | 强化 proxy.py，参考 Pipelock DLP 模式 | 2 周内 |
| 无 CI/CD 集成 | 开发 GitHub Action `aishield-security-scan` | 1 个月内 |
| 无客户端插件 | 评估 VS Code/Cursor 插件可行性 | 1-2 个月 |
| 社区热度 0 | 本周发布 2 篇技术博客 + Reddit/HN 发帖 | 本周 |

---

## 四、积分运营仪表盘

### 4.1 本周积分数据（7/27 ~ 8/2）

| 指标 | 本周数值 | 累计数值 | 状态 |
|------|----------|----------|------|
| 新增账户 | **0** | 1 | ❌ 服务不可达 |
| 充值笔数 | **0** | 2 | — |
| 充值积分 | **0** | 2,500 | — |
| 消费笔数 | **0** | 0 | — |
| 消费积分 | **0** | 0 | — |
| 总余额 | — | 2,600 | — |
| 活跃账户（近7天消费） | **0** | 0 | — |

### 4.2 历史 API 调用

| 日期 | 总请求 | 错误 | 说明 |
|------|--------|------|------|
| 07-21 | 42 | 0 | 最后一波正常流量 |
| 07-24 | 2 | 0 | 测试流量 |
| 07-25 | 24 | 1 | Creem 支付测试 |
| 07-26~08-02 | **0** | 0 | 服务不可达 |
| **本周合计** | **0** | **0** | — |

### 4.3 积分消耗率

- 总充值：2,500 积分
- 总消费：0 积分
- 消耗率：**0%**（低于 10% 阈值，但无可消费流量）

---

## 五、需求闭环（Issues → 提取 → 候选池 → 优先级）

### 5.1 GitHub Issues 状态

- **Open Issues**：0
- **Closed Issues**：0
- **本周新 Issues**：0

### 5.2 基于竞品/情报的推测需求候选池

| 需求 ID | 标题 | 来源 | 优先级 | 与 ROADMAP 匹配 |
|---------|------|------|--------|----------------|
| DEMAND-001 | MCP 服务器实时扫描 CLI/CI 集成 | 竞品差距 | P0 | Phase 2 GitHub Action |
| DEMAND-002 | 运行时 MCP 流量代理/拦截模式 | 竞品差距 | P0 | proxy.py 强化 |
| DEMAND-003 | Cursor/Claude Desktop 插件 | 竞品差距 | P1 | Phase 2 |
| DEMAND-004 | MCP 2026-07-28 无状态协议兼容 | 协议更新 | P0 | 核心技术基线 |

---

## 六、推广闭环（发现 → 选题 → 创作 → 发布 → 验证）

### 6.1 本周选题

| 选题 | 优先级 | 形式 | 目标渠道 |
|------|--------|------|----------|
| MCP 无状态化后的安全新战场 | P0 | 技术博客 | Blog + HN + Reddit |
| HuggingFace 被入侵的 4 个必要条件 | P0 | 案例分析 | Blog + Reddit |
| A2A v1.0 安全检查清单 | P1 | 技术博客 | Blog |
| 7 月 MCP 安全 CVE 汇总 | P1 | 汇总文章 | Blog |

### 6.2 推广渠道状态

| 渠道 | 状态 | 说明 |
|------|------|------|
| GitHub Stars | **0** | 无变化 |
| awesome-mcp-servers PR | 🔴 阻塞 8 天 | 需 Glama 提交 |
| Glama | ❌ 未提交 | ~37,000 servers |
| Smithery | ❌ 未上传 | ~7,000 servers |
| mcp.so | ❌ 未提交 | ~13,000 servers |
| Reddit/HN | ❌ 未发帖 | — |

---

## 七、生态闭环（检查 → 修复 → 验证）

### 7.1 已注册 Agent 健康检查

| Agent | URL | 状态 | skills | 信誉 | 可用性 |
|-------|-----|------|--------|------|--------|
| SecurityScanner | https://agent.aishield.tools/scanner | active | 2 | 85 | ❌ 域名不可达 |
| CodeReviewer | https://agent.aishield.tools/reviewer | active | 1 | 72 | ❌ 域名不可达 |
| test-compat | http://test | active | 1 | 50 | ❌ 无效 URL |
| TestAgent-01 | — | active | 3 | 30(novice) | ⚠️ 测试 |
| test-agent-e2e (x4) | — | active | 1 | 50 | ⚠️ 测试 |
| test-agent | — | active | 0 | 50 | ⚠️ 测试 |
| MCPTestAgent (x3) | — | active | 1 | 50 | ⚠️ 测试 |
| TestAgent_v42 | — | active | 2 | 50 | ⚠️ 测试 |
| E2E_Agent | — | active | 2 | 50 | ⚠️ 测试 |
| E2ETestAgent | — | active | 3 | 50 | ⚠️ 测试 |

**结论**：
- 生产级 Agent（SecurityScanner、CodeReviewer）URL 不可达，因 aishield.tools 服务中断
- 其余均为测试 Agent，无需维护
- **无新 Agent 满足注册条件（skills>=3）**
- **无新 Agent 满足认证条件（score>=70）**

### 7.2 生态修复决策

| 问题 | 修复决策 | 验证方式 |
|------|----------|----------|
| aishield.tools 不可达 | 需人工修复 SSL/备案 | Health API 200 |
| Agent URL 不可达 | 服务恢复后自动恢复 | curl Agent URL |

---

## 八、决策摘要（供每日闭环引用）

### 8.1 已采用决策

1. **安全规则**：新增 `sandbox_escape` + `mcp_credential_flow` 检测（P0，立即采用）
2. **推广内容**：确定 2 个 P0 选题（MCP 无状态安全、HuggingFace 入侵分析）
3. **需求入库**：4 个需求进入候选池（DEMAND-001~004）

### 8.2 排期决策

1. **多轮注入检测**：需 LLM-as-a-Judge，排期 2-4 周
2. **iframe 沙箱逃逸**：研究阶段，排期 1 个月
3. **渐进式提权检测**：行为模式检测，排期 2 周

### 8.3 观察决策

1. **A2A v1.0 安全**：已有 A2A 中间件覆盖，暂不扩展

---

## 九、闭环状态检查

### 9.1 断点清单

| 断点 | 影响 | 状态 |
|------|------|------|
| 服务不可达（SSL/备案） | 所有线上数据、推广、用户获取中断 | 🔴 连续 8 天 |
| 无新 Agent 注册 | 生态停滞 | 🟡 连续 8 天 |
| 无 GitHub Issues | 用户需求渠道为空 | 🟡 仓库创建至今 |
| 无真实用户流量 | 积分制、安全规则无法验证生产效果 | 🔴 连续 8 天 |

### 9.2 闭环率统计

| 指标 | 数值 |
|------|------|
| 本周可执行闭环 | **2/6**（威胁情报分析完成、内容选题确定） |
| 阻塞闭环 | **4/6**（规则部署、Agent注册、内容发布、需求验证均依赖服务恢复） |
| 根本原因 | **服务不可用** |

---

## 十、下周验证清单

1. [ ] 验证新增 `sandbox_escape` 检测规则是否正确导入并拦截测试用例
2. [ ] 验证新增 `mcp_credential_flow` 检测规则测试用例
3. [ ] 检查 MCP 2026-07-28 Beta SDK 兼容性测试结果
4. [ ] 验证本周推广内容发布后的链接可访问性和 SEO 结构化数据
5. [ ] 检查 aishield.tools SSL/备案状态是否恢复
6. [ ] 验证 PR #10694 / Glama 提交进展
7. [ ] 检查是否有新 Agent 注册或认证请求

---

## 附录：数据快照

```
accounts.json:
  账户数: 1 (usr_b20686a8dd25 / IdempTest)
  总余额: 2,600 积分
  充值历史: 2 笔（2,000 + 500 积分，Creem 网关）
  消费历史: 无

usage.json (本周 W31):
  07-27~08-02: 0 次（服务不可达）
  历史总计: 68 次

security_inspections.json:
  总检查: 8 | 安全: 5 | 拦截: 3
  风险分布: sensitive_data(2), pii_leak(3), hallucination(1)

agents.json:
  已注册 Agent: 11（全部测试）
  信誉分布: novice(1), standard(10)

agent_registry.json:
  已注册 Agent: 5（2 个生产级 URL 不可达）

certifications.json:
  总认证: 14 | certified: 7 | revoked: 2 | rejected: 1

GitHub (lm203688/aishield):
  Stars: 0 | Forks: 0 | Issues: 0 | Open Issues: 0
  最近推送: 2026-07-22
```

---

*报告生成时间：2026-08-03*
*数据来源：本地 JSON 数据文件、GitHub API、arXiv、NVD、IBM Security、腾讯云、Aviatrix、OWASP*
*下一期报告：2026-W32（2026-08-10 生成）*
