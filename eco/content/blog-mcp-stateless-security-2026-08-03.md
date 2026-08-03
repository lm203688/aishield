# MCP 2026-07-28 无状态化：安全网关必须回答的 3 个问题

> 发布日期：2026-08-03
> 标签：MCP, Agent Security, Stateless Protocol, OAuth
> 来源：AIShield 威胁情报周报

---

## 引言

2026 年 7 月 28 日，Anthropic 发布了 MCP（Model Context Protocol）协议诞生以来规模最大的一次修订——**彻底无状态化**。这一变化被称为"AI 的 USB-C 接口"的协议升级，但同时也带来了新的安全挑战。

作为 AIShield 安全研究团队，我们在分析后发现：**无状态化在简化架构的同时，也模糊了安全边界**。本文提出 3 个安全网关必须回答的核心问题，并分享 AIShield 的检测实践。

---

## 问题一：OAuth 凭证如何在无状态请求中安全流转？

### 旧版（有状态）

- `initialize` 握手建立 Session
- `Mcp-Session-ID` 绑定用户上下文
- 凭证与 Session 强关联，服务端维护状态

### 新版（无状态）

- 取消 `initialize` 握手
- 取消 `Mcp-Session-ID`
- 每个请求独立，由负载均衡器任意分配

### 安全风险

IBM 本周刚披露 **CVE-2026-16496**：terraform-mcp-server 存在"跨用户凭证继承"漏洞——如果攻击者获取了另一个用户的 MCP Session ID，就能以该用户的身份执行工具调用。**无状态化取消了 Session ID，但 OAuth Token 必须在每个请求中携带，Token 的泄露面反而扩大。**

### AIShield 检测方案

我们在 `security_middleware.py` 中新增了 `mcp_credential_flow` 检测规则，覆盖明文传输的 MCP 凭证头、请求体中意外泄露的 access_token / refresh_token、异常的凭证复用模式。

---

## 问题二：Tasks 扩展的破坏性变更是否模糊了权限边界？

MCP 2026-07-28 将 Tasks 扩展从"实验性"提升为"正式标准"，但这也带来了**权限边界的模糊**：

- Task 可以跨多个 MCP Server 执行
- 子 Task 可能继承父 Task 的权限
- 无状态化后，权限的传递链路更难追踪

**攻击场景**：攻击者通过构造一个看似无害的父 Task，诱导 Agent 在子 Task 中执行高权限操作（如删除数据、访问敏感 API）。

### AIShield 应对

- 任务描述审查：`inspect_task` 检测 Task 描述中的权限提升暗示
- 消息内容审查：`inspect_message` 检测 Agent 间通信中的异常权限请求
- 输出审查：`inspect_output` 检测 Agent 输出中是否包含敏感系统路径或凭证

---

## 问题三：MCP Apps 的 iframe 沙箱是新的 XSS 攻击面

MCP 2026-07-28 引入了 **MCP Apps**——允许在沙箱 iframe 中运行 MCP 工具的 UI。这是一个全新的攻击面：

- iframe 沙箱逃逸 → 访问宿主页面 DOM
- 恶意 MCP App → 窃取用户凭证
- 跨域通信 → 利用 postMessage 漏洞

**沙箱逃逸已成为实战威胁**。7 月 21-24 日，OpenAI Agent、Cursor、Codex、Gemini CLI、Claude Cowork 均被发现存在沙箱逃逸漏洞，其中 Claude Cowork 影响了 50 万 Mac 用户。

### AIShield 检测方案

新增 `sandbox_escape` 检测规则，覆盖路径遍历、敏感系统目录访问、危险系统调用等模式。

---

## 结论

MCP 无状态化是架构的进化，但安全边界不能随之模糊。AIShield 已经针对三大新风险更新了检测规则：

| 风险 | 检测规则 | 状态 |
|------|----------|------|
| OAuth 凭证泄露 | `mcp_credential_flow` | 已上线 |
| 权限边界模糊 | `inspect_task` / `inspect_message` | 已覆盖 |
| iframe 沙箱逃逸 | `sandbox_escape` | 已上线 |

**建议所有 MCP 开发者和 Agent 构建者**：在升级 MCP 2026-07-28 的同时，审查你的安全网关是否覆盖了这 3 个问题。

---

*本文基于 AIShield 威胁情报周报生成*
*检测代码已开源：github.com/lm203688/aishield*
