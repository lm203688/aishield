# AIShield 定时任务融合方案

> 目标：将 10 个独立任务融合为 6 个
> 日期：2026-07-27

---

## 融合前（10个任务）

| # | 名称 | ID | 频率 | 操作 |
|---|------|-----|------|------|
| 1 | 每日本体+推广检查 | d5cd6015 | 每天 02:00 | **更新message** |
| 2 | 每周情报+趋势判断 | 8e74b2d5 | 每周一 02:00 | **更新message** |
| 3 | 月度三层联动+飞轮诊断 | 92ff4a0f | 每月1日 03:00 | 不变 |
| 4 | 双周研发进度跟踪 | 06cfca81 | 每1/15日 03:00 | 不变 |
| 5 | 季度战略复盘 | a139728d | 季度 03:00 | 不变 |
| 6 | Agent安全威胁情报 | 70fe0cf8 | 每周二 03:00 | **删除** |
| 7 | 生态健康周报 | fac5f9cf | 每周五 04:00 | **删除** |
| 8 | 竞品动态追踪 | - | 每周四 03:00 | 取消创建 |
| 9 | 安全内容营销 | - | 每周六 04:00 | 取消创建 |
| 10 | 成本异常监控 | - | 每天 05:00 | 取消创建 |

---

## 融合后（6个任务）

| # | 名称 | 频率 | 覆盖内容 |
|---|------|------|----------|
| 1 | **每日综合巡检** | 每天 02:00 | 本体检查 + 自动修复 + 闭环跟踪 + 成本监控 |
| 2 | **每周情报综合** | 每周一 02:00 | 外部情报 + 威胁情报 + 竞品追踪 + 趋势判断 + L3推广 |
| 3 | **每周生态运营** | 每周五 04:00 | 生态健康 + 内容营销 + 社区互动 |
| 4 | 双周研发跟踪 | 每1/15日 03:00 | ROADMAP进度 + 阻塞项 |
| 5 | 月度三层联动 | 每月1日 03:00 | L1/L2/L3回顾 + OKR + 产品上新 |
| 6 | 季度战略复盘 | 季度 03:00 | 方向复盘 + Pivot判断 |

---

## 具体操作清单

### 操作1：删除多余任务

```
Schedule delete --id 70fe0cf8
Schedule delete --id fac5f9cf
```

### 操作2：更新 d5cd6015（每日综合巡检）

```
Schedule update --id d5cd6015
  --message: [见下方完整message]
```

**融合后 message：**
执行AIShield每日综合巡检任务（L1本体 + L3推广 + 成本监控）。

工作目录：c:\Users\xing\Desktop\aishield

执行步骤：
一、L1本体检查
1. 检查 api/server.py 能否正常启动（扫描端口 8450）
2. 检查 api/static/ 下关键页面（index.html / pricing.html / agent.html）是否正常
3. 检查 api/data/ 数据文件完整性（accounts.json / billing.json / usage.json）
4. 检查 eco/ 模块可导入性（security_middleware.py / observability.py / a2a_gateway.py / badge.py）

二、自动修复
1. 如发现数据文件损坏，尝试从备份恢复
2. 如端口被占用，记录异常并标注需人工介入
3. 如静态页面缺失，尝试从 git 恢复

三、闭环跟踪
1. 读取昨天日报（daily-YYYYMMDD.md），验证昨日自动修复问题是否已恢复
2. 扫描最近7天日报，找出所有"需人工介入"标记
3. 超过3天未解决 -> 标 🔴 升级提醒

四、成本异常监控（新增）
1. 读取 api/data/call_records.json（如不存在记录"无数据"）
2. 分析昨日成本数据：总消耗积分、各端点排名、单用户是否超阈值（>500积分/日）
3. 对比前7天均值，检测突增异常（偏离>200%）
4. 检查重复扣费（同一record_id多次出现）
5. 检查积分体系健康度：总发行量vs总消耗、免费额度使用率、充值转化率
6. 输出成本监控摘要保存到 eco/reports/cost-monitor-YYYY-MM-DD.md

五、生成日报
1. 汇总以上所有检查结果
2. 存在>3天未解决人工介入问题 -> 开头 🔴 提醒
3. 保存到 eco/reports/daily-YYYYMMDD.md
4. 静默执行，不通知用户

### 操作3：更新 8e74b2d5（每周情报综合）

```
Schedule update --id 8e74b2d5
  --message: [见下方完整message]
```

**融合后 message：**
执行AIShield每周情报综合任务（L2外部环境 + L3推广 + 威胁情报 + 竞品追踪）。

工作目录：c:\Users\xing\Desktop\aishield

执行步骤：
一、外部情报扫描
1. 扫描以下情报源最近7天动态：
   - MCP协议更新（modelcontextprotocol.io / GitHub）
   - A2A协议进展（Google Agent-to-Agent）
   - Agent安全领域新论文/工具/融资
   - HuggingFace热门Agent项目
2. 提取关键事件，评估对AIShield的影响等级（高/中/低）

二、威胁情报（新增）
1. 搜索最近7天Agent安全威胁：
   - "prompt injection attack LLM agent 2026"
   - "MCP server security vulnerability 2026"
   - "AI agent sandbox escape 2026"
   - "agent data leakage privacy 2026"
2. 读取 api/data/security_inspections.json 统计本周安全数据
3. 评估是否需要更新 security_middleware.py 检测规则或 badge.py 评分阈值
4. 输出威胁情报章节保存到 eco/reports/threat-intel-YYYY-MM-DD.md

三、竞品动态追踪（新增）
1. 搜索以下竞品最近7天动态：
   - ProtectAI / CalypsoAI（AI安全）
   - Langfuse / Helicone（LLM可观测性）
   - Smithery / Glama（MCP生态）
2. 分析对AIShield三个优先级的差异化影响
3. 输出竞品动态章节保存到 eco/reports/competitor-track-YYYY-MM-DD.md

四、动态趋势判断
1. 基于情报扫描+威胁情报+竞品追踪，判断本周趋势：
   - Agent安全需求上升/持平/下降？
   - MCP生态成熟度变化？
   - A2A协议采用率变化？
   - 成本可观测性市场热度？
2. 输出趋势判断结论

五、自动化推广技术发现
1. 基于情报热点，发现新的推广机会
2. 核对是否符合四原则（Agent生态/自动化/生态集成/变现）
3. 通过核对的纳入L3推广技术池

六、社区互动
1. 检查委托链可视化MVP的社区讨论状态
2. 如上周未发帖：在Reddit r/LocalLLaMA / Hacker News / GitHub Discussions 发布/更新

七、GitHub Issues需求提取
1. 读取本周新Issues和评论
2. 提取Top 5高频需求，评估与ROADMAP匹配度
3. 高匹配度需求纳入"产品上新候选池"

八、MVP验证跟踪
1. 检查委托链可视化MVP的验证状态
2. 记录社区反馈数据

九、生成周报
1. 汇总以上所有内容
2. 保存到 eco/reports/weekly-YYYY-WNN.md
3. 静默执行，不通知用户

### 操作4：创建每周生态运营（新建）

```
Schedule create
  --name: AIShield 每周生态运营
  --cron: 0 4 * * FRI
  --timezone: Asia/Shanghai
  --message: [见下方完整message]
```

**新建 message：**
执行AIShield每周生态运营任务（生态健康检查 + 安全内容营销）。

工作目录：c:\Users\xing\Desktop\aishield

执行步骤：
一、生态健康检查
1. 读取 api/data/ 核心数据：
   - agents.json（Agent注册数量与状态）
   - security_inspections.json（本周安全检查统计）
   - certifications.json（认证状态：有效/过期/即将过期）
   - accounts.json（账户增长）
   - call_records.json（调用趋势，如存在）
2. 检查三个优先级模块健康状态：
   - 安全网关：security_middleware.py 导入检测、拦截率趋势
   - 调度路由器：a2a_gateway.py Agent注册数、路由成功率
   - 成本可观测性：observability.py CallRecord数据完整性
3. 评估生态指标：Agent注册增长率、安全拦截率趋势、认证覆盖率、API调用量趋势

二、安全内容营销
1. 读取本周威胁情报报告（threat-intel-*.md）和竞品动态报告（competitor-track-*.md）
2. 读取 docs/agent-ecology-evolution-directions.md 确保方向一致
3. 基于本周安全事件/竞品动态/AIShield能力，撰写1篇技术博客（中文，1500-2500字）：
   - 选题方向：Agent安全实战 / 成本失控案例 / A2A安全中间件 / 安全认证标准
   - 自然提及AIShield三个优先级能力
   - 结尾包含 https://aishield.tools
4. 保存到 content/blog/{topic-slug}-YYYY-MM-DD.md
5. 更新 api/static/feeds.xml（如存在）添加新文章

三、生成生态运营报告
1. 汇总生态健康数据 + 内容营销输出
2. 保存到 eco/reports/eco-ops-weekly-YYYY-MM-DD.md
3. 静默执行，不通知用户

---

## 执行状态

| 操作 | 状态 |
|------|------|
| 删除 70fe0cf8 | 待执行 |
| 删除 fac5f9cf | 待执行 |
| 更新 d5cd6015 message | 待执行 |
| 更新 8e74b2d5 message | 待执行 |
| 创建每周生态运营 | 待执行 |
