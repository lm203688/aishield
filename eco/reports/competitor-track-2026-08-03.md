# AIShield 竞品动态跟踪 2026-08-03

> **覆盖周期**：最近7天（2026-07-27 ~ 2026-08-02）
> **生成时间**：2026-08-03

---

## 一、本周竞品重大事件

### 1. F5 收购 CalypsoAI（2026-07-14）

- **收购方**：F5（NASDAQ: FFIV），全球应用交付和 API 安全领导者
- **被收购方**：CalypsoAI，企业 AI 安全先锋，自适应 AI 推理安全
- **战略意义**：F5 将提供"端到端 AI 运行时保护"，不受模型或云环境限制
- **对 AIShield 影响**：🔴 **竞争加剧** — F5 + CalypsoAI 将形成企业级 AI 安全的完整闭环，AIShield 需强化"开源/开发者优先"差异化

---

### 2. MCP 安全赛道持续升温

| 竞品 | Stars/热度 | 定位 | 本周动态 |
|------|-----------|------|----------|
| Snyk Agent Scan | ~1,800 | scan+proxy 双模式 | 开源免费，需本地部署 |
| Cisco MCP Scanner | ~830 | YARA+LLM+API 三引擎 | 高级功能依赖 Cisco 云 |
| Docker MCP Gateway | ~1,300 | 容器化 MCP server | 基础设施级方案 |
| Pipelock | ~342 | 运行时 agent 防火墙 | 48 个 DLP 模式 |
| MCP Defender | HN 64 pts | Cursor/Claude 防火墙 | 客户端插件 |
| MCPShark | HN 35 pts | MCP 流量检测器 | 流量检测 |
| MCPSafe | 独立站 | 漏洞扫描+信任验证 | 信任评分 |

**关键洞察**：
- HackerNews 上 MCP 安全话题活跃，AIShield **完全缺席**
- 竞品从"部署前扫描"转向"运行时强制执行"，AIShield 仅有扫描层，**运行时防护（Proxy）是差距**

---

### 3. LLM 可观测性市场

| 平台 | 2026 状态 | 与 AIShield 关系 |
|------|----------|------------------|
| Langfuse | 基于 OpenTelemetry，仍是开源 LLM Observability 首选 | 互补 — AIShield 专注安全，Langfuse 专注观测 |
| Helicone | 企业级 LLM Ops 平台 | 互补 |
| Arize Phoenix | 模型可观测性 | 互补 |

**趋势**：可观测性与安全正在融合，但 AIShield 当前无 tracing/observability 功能，**是潜在扩展方向**。

---

### 4. MCP 生态平台

| 平台 | 规模 | AIShield 状态 |
|------|------|--------------|
| Smithery | ~7,000+ servers | ❌ 未上传（npm 包未发布） |
| Glama | ~37,000 servers | ❌ 未提交（PR #10694 阻塞 8 天） |
| mcp.so | ~13,000 servers | ❌ 未提交 |
| 腾讯云 MCP 广场 | 国内 | ❌ 未提交 |
| GitHub MCP Registry | 官方新推出 | ⏳ 待跟进 |

---

## 二、竞品差距分析

| 维度 | AIShield | 竞品 | 差距等级 |
|------|----------|------|----------|
| 运行时防护（Proxy） | 2次测试拦截 | Pipelock 48 DLP 模式 | 🔴 大 |
| CI/CD 集成 | ❌ 无 | Snyk/Cisco 均有 | 🔴 大 |
| 客户端插件 | ❌ 无 | MCP Defender（Cursor/Claude） | 🟡 中 |
| 社区热度 | 0 star | Snyk 1,800 stars | 🔴 大 |
| 企业背书 | 无 | F5/Cisco/Snyk | 🔴 大 |
| 协议覆盖 | MCP + A2A | 多数仅 MCP | ✅ 优势 |
| 积分制商业 | 已上线 | 多数开源/订阅 | ✅ 差异化 |
| Agent 信誉 | 已上线 | MCPSafe 类似 | ✅ 持平 |

---

## 三、可借鉴机会

1. **Pipelock 的 DLP 模式**：48 个数据泄露防护模式可启发 AIShield 规则库扩展
2. **MCP Defender 的客户端策略**：Cursor/Claude Desktop 插件是用户触点，AIShield 可考虑 VS Code 插件
3. **Snyk 的 CI 集成**：GitHub Action 是开发者工作流核心入口，ROADMAP 已规划但尚未执行
4. **MCPSafe 的信任评分**：与 AIShield 的 Agent 信誉系统思路一致，可强化差异化

---

*报告生成时间：2026-08-03*
