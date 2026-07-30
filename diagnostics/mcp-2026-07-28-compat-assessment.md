# MCP 2026-07-28 协议兼容性评估报告

> 评估时间: 2026-07-31
> 评估对象: AIShield scanner/handshake.py (v4.0 → v4.3)
> 协议版本: MCP 2026-07-28 (第5版规范)
> 评估状态: ✅ 已完成，代码已更新

---

## 1. MCP 2026-07-28 核心变更

### 1.1 无状态协议核心
- **移除 handshake**: 不再需要 `initialize` → `initialized` 握手流程
- **移除 session ID**: `Mcp-Session-Id` header 废弃，每个请求自包含协议版本和身份
- **影响**: MCP 服务器可运行在 serverless/edge 基础设施上，无需共享会话存储

### 1.2 Multi Round-Trip Requests
- 替代旧版服务器端发起的回调
- 工具可返回 `resultType: "input_required"`，客户端通过 `inputResponses` 重试
- 跨独立无状态请求实现多轮交互

### 1.3 Header 路由
- 新增 `Mcp-Method` 和 `Mcp-Name` HTTP headers
- 网关/WAF 可基于 header 做路由和授权决策，无需解析 JSON body

### 1.4 缓存契约
- 工具/提示/资源列表响应新增 `ttlMs` 和 `cacheScope` 字段
- 服务器声明自身新鲜度窗口，客户端据此缓存

### 1.5 安全加固
- OAuth 授权服务器必须返回 `iss` 参数 (RFC 9207)
- 客户端凭据绑定到特定授权服务器
- Dynamic Client Registration (DCR) 废弃，替换为 Client ID Metadata Documents

### 1.6 废弃功能 (12个月过渡期)
- HTTP+SSE 传输
- Roots, Sampling, Logging
- Dynamic Client Registration (DCR)

### 1.7 扩展框架
- Tasks 进入正式扩展: `io.modelcontextprotocol/tasks`
- MCP Apps 和 Enterprise Managed Authorization 作为扩展

---

## 2. AIShield handshake.py 兼容性评估

### 2.1 评估前状态 (v4.0)

| 检测项 | 旧版状态 | 风险等级 |
|--------|----------|----------|
| 协议版本 | `2025-03-26` (旧版) | 中 |
| 握手方式 | 有状态 `initialize` 握手 | 中 |
| SSE 传输 | 使用 `text/event-stream` Accept | 低 (12个月过渡) |
| Header 路由 | 未使用 `Mcp-Method`/`Mcp-Name` | 低 |
| 缓存契约 | 未检测 `ttlMs`/`cacheScope` | 低 |
| Multi Round-Trip | 未检测 `input_required` | 低 |
| OAuth iss | 未检测 RFC 9207 合规 | 中 |
| DCR 废弃 | 未检测 | 低 |

### 2.2 评估后状态 (v4.3)

| 检测项 | 新版状态 | 改进说明 |
|--------|----------|----------|
| 协议版本 | `2026-07-28` (最新) | ✅ 更新协议版本常量 |
| 握手方式 | 双模式: 无状态优先 + 旧版回退 | ✅ 策略1无状态 `tools/list`，策略2回退 `initialize` |
| SSE 传输 | 检测并标记为废弃 | ✅ 新增 `deprecated_sse_transport` 检测 |
| Header 路由 | 使用 `Mcp-Method`/`Mcp-Protocol-Version` | ✅ 无状态请求包含路由 headers |
| 缓存契约 | 检测 `ttlMs`/`cacheScope` | ✅ 新增 `_check_cache_contract()` |
| Multi Round-Trip | 检测 `input_required` | ✅ 新增 `_check_input_required()` |
| OAuth iss | 检测 RFC 9207 合规 | ✅ 新增 `missing_oauth_iss` 检测 |
| DCR 废弃 | 检测 DCR 使用 | ✅ 新增 `deprecated_dcr` 检测 |
| Session ID | 检测有状态会话 | ✅ 新增 `stateful_session`/`deprecated_session_id` 检测 |
| 旧版协议 | 检测并建议升级 | ✅ 新增 `legacy_protocol` 检测 |

---

## 3. 代码变更明细

### 3.1 新增常量
- `MCP_PROTOCOL_LATEST = "2026-07-28"`
- `MCP_PROTOCOL_LEGACY = "2025-03-26"`
- `USER_AGENT` 更新为 `AIShield-Handshake/4.3`

### 3.2 `_try_http_handshake()` 重构
- **策略1 (新增)**: 无状态 `tools/list` 请求，携带 `Mcp-Method`/`Mcp-Protocol-Version` headers
- **策略2 (保留)**: 旧版 `initialize` 握手回退，检测 `Mcp-Session-Id` 和协议版本
- **新增检测**: SSE 废弃传输、缓存契约、Multi Round-Trip Requests

### 3.3 新增辅助函数
- `_check_cache_contract()`: 检查 `ttlMs`/`cacheScope` 缓存契约
- `_check_input_required()`: 检查 `input_required` 结果类型

### 3.4 `verify_handshake()` 增强
- **检查5 (新增)**: 废弃功能检测
  - DCR (Dynamic Client Registration) 使用检测
  - HTTP+SSE 传输代码检测
  - Mcp-Session-Id 使用检测
  - OAuth iss 参数缺失检测
- **输出增强**: 新增 `protocol_version` 字段

---

## 4. 安全检测能力对照

### OWASP MCP Top 10 映射

| OWASP 类别 | 检测能力 | 状态 |
|------------|----------|------|
| MCP01 (敏感信息) | 敏感环境变量检测 | ✅ 保留 |
| MCP02 (认证授权) | OAuth iss 缺失检测、DCR 废弃检测 | ✅ 新增 |
| MCP03 (注入) | 工具描述异常长度检测 | ✅ 保留 |
| MCP04 (供应链) | npx -y 自动安装检测 | ✅ 保留 |
| MCP05 (传输安全) | SSE 废弃传输检测 | ✅ 新增 |
| MCP09 (URL安全) | 不安全远程URL检测 | ✅ 保留 |

---

## 5. 兼容性结论

### 5.1 向后兼容性
- ✅ 旧版 `initialize` 握手仍作为回退策略保留
- ✅ 12个月过渡期内 SSE 传输仍可工作
- ✅ DCR 在过渡期内仍可工作

### 5.2 前向兼容性
- ✅ 支持 2026-07-28 无状态请求模式
- ✅ 检测新协议特性 (缓存契约、Multi Round-Trip)
- ✅ 检测废弃功能并给出迁移建议

### 5.3 风险评估
- **低风险**: 核心安全检测能力（供应链、敏感信息、注入）不受协议变更影响
- **低风险**: 双模式策略确保对旧版和新版服务器的兼容性
- **信息级**: 废弃功能检测为信息性提示，不影响扫描结果评级

### 5.4 建议
1. 服务器端 API (`api/server.py`) 如作为 MCP Server 运行，建议后续评估是否需要支持无状态模式
2. 关注 Tier 1 SDK (Python/TypeScript) 的 2026-07-28 兼容版本发布
3. 12个月过渡期结束前（2027-07-28）完成所有废弃功能的迁移

---

## 6. 参考资料

- [MCP 2026-07-28 Specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [MCP Goes Stateless: What the 2026-07-28 Spec Actually Changes](https://www.scien.cx/2026/07/30/mcp-goes-stateless-what-the-2026-07-28-spec-actually-changes/)
- [AWS: MCP 2026-07-28 Specification Analysis](https://aws.amazon.com/it/blogs/machine-learning/category/learning-levels/intermediate-200/)
- [IT之家: MCP 2026-07-28 规范发布](https://www.ithome.com/0/983/102.htm)
