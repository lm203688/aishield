# AIShield 待创建定时任务配置

> 前2个已创建成功，剩余3个待工具恢复后创建
> 创建日期：2026-07-27

---

## 已创建任务

| # | 名称 | Cron | 状态 | ID |
|---|------|------|------|----|
| 1 | AIShield Agent安全威胁情报 | `0 3 * * TUE` | ✅ 已创建 | 70fe0cf8 |
| 2 | AIShield 生态健康周报 | `0 4 * * FRI` | ✅ 已创建 | fac5f9cf |
| 3 | AIShield 竞品动态追踪 | `0 3 * * THU` | ❌ 待创建 | - |
| 4 | AIShield 安全内容营销 | `0 4 * * SAT` | ❌ 待创建 | - |
| 5 | AIShield 成本异常监控 | `0 5 * * *` | ❌ 待创建 | - |

---

## 任务3: AIShield 竞品动态追踪

| 字段 | 值 |
|------|-----|
| 名称 | AIShield 竞品动态追踪 |
| Cron | `0 3 * * THU`（每周四 03:00 北京时间）|
| 时区 | Asia/Shanghai |

**Message:**
```
执行AIShield竞品动态追踪任务。

工作目录：c:\Users\xing\Desktop\aishield

执行步骤：
1. 搜索以下竞品/生态项目的最新动态（最近7天）：
   - 'Model Context Protocol MCP ecosystem 2026'
   - 'A2A protocol Google agent-to-agent 2026'
   - 'agent security gateway startup 2026'
   - 'AI agent cost tracking observability 2026'
   - 'LLM guardrail prompt injection detection 2026'
2. 重点跟踪以下竞品：
   - ProtectAI（AI安全平台）
   - CalypsoAI（AI安全网关）
   - Langfuse（LLM可观测性）
   - Helicone（LLM成本追踪）
   - Smithery/Glama（MCP生态平台）
3. 分析每个竞品动态对AIShield三个优先级的影响
4. 输出竞品动态报告（中文），包含：竞品重要动态（Top 10）、竞争格局变化、差异化机会、产品调整建议
5. 保存到 c:\Users\xing\Desktop\aishield\eco\reports\competitor-track-YYYY-MM-DD.md
6. 静默执行，不通知用户
```

---

## 任务4: AIShield 安全内容营销

| 字段 | 值 |
|------|-----|
| 名称 | AIShield 安全内容营销 |
| Cron | `0 4 * * SAT`（每周六 04:00 北京时间）|
| 时区 | Asia/Shanghai |

**Message:**
```
执行AIShield安全领域内容营销任务。

工作目录：c:\Users\xing\Desktop\aishield

执行步骤：
1. 读取本周威胁情报报告（threat-intel-*.md）和竞品动态报告（competitor-track-*.md）
2. 读取 docs/agent-ecology-evolution-directions.md 确保内容与战略方向一致
3. 基于本周安全事件/竞品动态/AIShield能力，撰写1篇技术博客文章（中文，1500-2500字）：
   - 优先选题方向：
     a) Agent安全实战案例（如某MCP Server的Prompt注入攻击分析）
     b) Agent成本失控案例与解决方案
     c) A2A协议安全中间件设计思路
     d) Agent安全认证标准与实践
   - 文章必须自然提及AIShield的三个优先级能力
   - 文章结尾包含AIShield官网链接 https://aishield.tools
4. 保存文章到 c:\Users\xing\Desktop\aishield\content\blog\{topic-slug}-YYYY-MM-DD.md
5. 更新 api/static/feeds.xml（如存在）添加新文章条目
6. 静默执行，不通知用户
```

---

## 任务5: AIShield 成本异常监控

| 字段 | 值 |
|------|-----|
| 名称 | AIShield 成本异常监控 |
| Cron | `0 5 * * *`（每天 05:00 北京时间）|
| 时区 | Asia/Shanghai |

**Message:**
```
执行AIShield成本异常监控任务。

工作目录：c:\Users\xing\Desktop\aishield

执行步骤：
1. 读取 api/data/call_records.json（如不存在则跳过，记录"无数据"并结束）
2. 读取 api/data/cost_alerts.json（如不存在则跳过）
3. 读取 api/data/accounts.json 获取用户积分余额
4. 分析成本数据：
   a) 昨日总消耗积分与Token量
   b) 各端点消耗排名（Top 5）
   c) 单用户日消耗是否超过阈值（单日>500积分为异常）
   d) 对比前7天日均值，昨日消耗是否偏离>200%（突增异常）
   e) 检查是否存在重复扣费（同一record_id出现多次）
5. 检查积分体系健康度：
   a) 系统总积分发行量 vs 总消耗量
   b) 免费额度使用率
   c) 充值转化率
6. 如发现异常：
   a) 调用 eco/observability.py 的 ObservabilityService.get_cost_alerts() 生成告警
   b) 在日报中标注警告
7. 输出成本监控摘要（中文，简洁版，<500字），保存到 c:\Users\xing\Desktop\aishield\eco\reports\cost-monitor-YYYY-MM-DD.md
8. 静默执行，不通知用户。仅在发现严重异常时在报告开头明确标注
```
