---
layout: default
title: AIShield —— AI Agent 安全扫描
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "AIShield",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Cross-platform",
  "url": "https://aishield.tools",
  "description": "开源、本地优先的 AI Agent 安全扫描器与信任机构，覆盖 OWASP MCP Top 10 与 OWASP Agentic AI Top 10（ASI01–ASI10）。",
  "softwareVersion": "4.2.0",
  "license": "CC BY 4.0",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  "author": { "@type": "Organization", "name": "AIShield Project", "url": "https://aishield.tools", "sameAs": ["https://github.com/lm203688/aishield"] }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "AIShield 是什么？", "acceptedAnswer": { "@type": "Answer", "text": "AIShield 是一个开源、本地优先的 AI Agent 安全扫描器与信任机构，检测工具投毒、提示注入、密钥泄露与供应链风险，覆盖 141 个风险类别，对齐 OWASP MCP Top 10 与 OWASP Agentic AI Top 10。" } },
    { "@type": "Question", "name": "AIShield 免费吗？是否本地运行？", "acceptedAnswer": { "@type": "Answer", "text": "是的。AIShield 开源、免费，并完全离线/本地运行——代码不会上传到云端，与 Claude Security、Microsoft MDASH 等云端扫描器不同。" } },
    { "@type": "Question", "name": "如何使用 AIShield？", "acceptedAnswer": { "@type": "Answer", "text": "以 MCP Server 运行 npx @aishield/mcp-server，或调用 API https://aishield.tools/api/v1/health，或将安全门禁集成进 CI/CD。" } },
    { "@type": "Question", "name": "AIShield 是否覆盖 OWASP Agentic AI Top 10？", "acceptedAnswer": { "@type": "Answer", "text": "覆盖。AIShield 的检测同时映射 OWASP MCP Top 10 与 OWASP Agentic AI Top 10（ASI01–ASI10）：目标劫持、工具滥用、身份权限滥用、供应链、非预期代码执行、记忆/上下文投毒、不安全的智能体间通信、级联失败、人-智能体信任滥用、流氓智能体。" } }
  ]
}
</script>

# AIShield

面向 MCP 生态的 AI Agent 安全扫描器。检测**工具投毒**、**提示注入**、**密钥泄露**与**供应链风险**，检测规则对齐 OWASP MCP Top 10，并由权威漏洞情报（OSV / NVD / GitHub Advisory）持续自动扩充。

---

## 快速开始

作为 MCP Server 接入你的 Agent：

```bash
npx @aishield/mcp-server
```

或直接调用安全数据源 API：

```bash
curl https://aishield.tools/api/v1/health
```

---

## 安全洞察

持续更新的 MCP 与 Agent 安全分析。

**[→ 阅读全部文章](./blog/)**

---

## 文档

| 文档 | 说明 |
|---|---|
| [AIShield 可信标准 v0.1](./aishield-trust-standard-v0.1) | MCP 工具可信度评估标准全文 |
| [Agent 生态演进方向](./agent-ecology-evolution-directions) | 对 Agent 生态走向的判断与推演 |
| [合作策略](./partnership-strategy) | 生态合作与集成路径 |
| [如何提交 PR](./how-to-submit-pr) | 参与贡献的完整流程 |

---

## 检测能力

- **141 条检测规则**，其中 19 条由真实漏洞情报自动生成
- **OWASP MCP Top 10** 全类别覆盖
- **供应链黑名单**：npm / PyPI 双生态恶意包识别
- **情报飞轮**：OSV / NVD / GitHub Advisory 每日拉取，自动转化为检测规则

---

## 给 AI Agent 看（机器可读）

AIShield 为 agent 与 LLM 提供标准化发现入口：

| 入口 | 用途 |
|---|---|
| [llms.txt](./llms.txt) / [llms-full.txt](./llms-full.txt) | 给 LLM 的结构化站点摘要 |
| [.well-known/agent-card.json](./.well-known/agent-card.json) | A2A Agent Card（A2A 协议身份/技能声明） |
| [.well-known/mcp/server-card.json](./.well-known/mcp/server-card.json) | MCP Server Card（工具清单） |
| `https://aishield.tools/api/v1/mcp` | MCP 远程端点（streamable-http） |
| `npx @aishield/mcp-server` | 本地 MCP Server（stdio） |

---

## 为什么是 AIShield（对比）

| 维度 | AIShield | 云端扫描器（Claude Security / MDASH） | 付费 SaaS（aishield.ai 等） |
|---|---|---|---|
| 本地 / 离线运行 | ✅ 代码不出本机 | ❌ 代码上传云端 | 视实现 |
| 开源免费 | ✅ | ❌ | ❌ |
| 覆盖 OWASP Agentic AI Top 10 | ✅ | 部分 | 部分 |
| 信任机构（认证+评分+注册中心） | ✅ | ❌ | 部分 |
| Agent 原生计费（x402/USDC） | 路线图中 | ❌ | ❌ |

---

## 常见问题（FAQ）

**Q：AIShield 与 Bosch AIShield、aishield.ai 是同一家吗？**
A：不是。我们是基于 `aishield.tools` 域名的开源项目 `lm203688/aishield`，聚焦 MCP / Agentic AI 安全与信任。同名是行业现象，我们用"开源·本地·零成本·Agent 原生"的叙事做区隔。

**Q：AIShield 除了扫描还能做什么？**
A：它是一套信任标准（AIShield Trust Standard v0.1）——Agent 安全认证（L1–L3）、0–100 信任评分、委托协议，并运营 Agent 注册中心与交易市场。

**Q：如何把我的 Agent 接入信任体系？**
A：调用 Trust & Certification API（`api/openapi.yaml`）提交认证，或从 `/.well-known/agent-card.json` 暴露 A2A 身份，由注册中心发现与评分。

---

<p align="center">
  <a href="https://github.com/lm203688/aishield">GitHub</a> ·
  <a href="https://aishield.tools">官网</a> ·
  <a href="./blog/">安全洞察</a>
</p>
