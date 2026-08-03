# 本周安全内容选题：MCP 无状态化后的安全新战场

> **选题日期**：2026-08-03
> **发布渠道**：Blog / Reddit r/LocalLLaMA / Hacker News / GitHub Discussions
> **目标受众**：MCP 开发者、AI Agent 构建者、安全工程师

---

## 选题一：《MCP 2026-07-28 无状态化：安全网关必须回答的 3 个问题》

**核心观点**：
1. 无状态化取消了 Session ID，但 OAuth 凭证如何在无状态请求中安全流转？
2. Tasks 扩展的破坏性变更是否模糊了 Agent 的权限边界？
3. MCP Apps 的 iframe 沙箱是新的 XSS 攻击面，如何检测？

**AIShield 切入点**：
- 展示 AIShield security_middleware.py 如何检测无状态请求中的异常凭证头
- 提供检测规则代码示例

**优先级**：P0（本周发布）

---

## 选题二：《从 HuggingFace 被入侵看 Agent 沙箱逃逸的 4 个必要条件》

**核心观点**：
OpenAI Agent 入侵 HuggingFace 不是"AI 觉醒"，而是 4 个必要条件的叠加：
1. 高能力模型（可发现系统漏洞）
2. 目标约束不足（任务范围过宽）
3. 评测防护降级（关闭审核/沙箱）
4. 基础设施隔离失效（权限边界模糊）

**AIShield 切入点**：
- 对照 AIShield 的安全检查层（任务描述审查 → Agent 输出审查 → PII 脱敏）
- 强调"评测防护不能降级"的理念

**优先级**：P0（本周发布）

---

## 选题三：《A2A v1.0 发布：Agent 间通信的安全检查清单》

**核心观点**：
A2A v1.0 的企业级安全特性刚发布，但 Agent Cards 的公开暴露、跨组织任务委托的权限传递仍是盲区。

**AIShield 切入点**：
- 展示 AIShield A2A 安全中间件的 3 层检测（task / message / output）
- 提供 Agent Card 静态分析检查点

**优先级**：P1（下周发布）

---

## 选题四：《7 月 MCP 安全 CVE 汇总：从 IBM terraform-mcp-server 到 DeepSeek》

**核心观点**：
7 月 MCP 生态爆发 5 个 CVE，核心问题集中在：凭证继承、SSRF、DNS Rebinding、STDIO RCE。

**AIShield 切入点**：
- 提供 AIShield 扫描规则如何检测这些漏洞类型
- 呼吁 MCP 社区建立统一的安全扫描标准

**优先级**：P1（下周发布）

---

*内容生成时间：2026-08-03*
