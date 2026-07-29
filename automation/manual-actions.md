# 需用户手动解决问题清单

> 更新时间: 2026-07-30
> 总指挥汇总，按优先级排序

---

## P0 - 立即处理

### 1. 确认 Cloudflare SSL 模式为 "Full"

**状态**: 待确认
**影响**: aishield.tools 连续7天不可达，支付系统全链路中断

**已自动处理**:
- 部署脚本已更新，添加 443 端口 + 自签 SSL 证书配置
- Nginx 配置已更新，监听 443 端口
- 提交代码后会自动部署

**需要你做**:
登录 Cloudflare 控制台 → aishield.tools → SSL/TLS → Overview
确认模式为 **Full**（不是 Flexible，也不是 Full Strict）
- Flexible = Cloudflare 通过80端口连接源站 → 被备案拦截
- Full = Cloudflare 通过443端口连接源站 → 绕过备案拦截 ✅
- Full Strict = 需要有效证书 → 自签证书会被拒绝

**为什么是备案问题不是SSL问题**:
服务器IP 150.158.119.19 是腾讯云中国大陆服务器，aishield.tools 未在腾讯云完成ICP备案。腾讯云拦截80端口的HTTP请求。通过443端口（HTTPS）可以绕过此限制。

---

### 2. Cloudflare API Token 权限不足

**状态**: 已确认
**影响**: 无法通过API自动修改SSL设置

当前 Token (cfut_Moh...) 虽然在 Zone 列表显示有 `#zone_settings:read/edit` 权限，但实际调用 SSL 设置 API 返回 403 错误 (code 9109)。

**需要你做**（二选一）:
- **方案A**: 在 Cloudflare 控制台手动确认 SSL 模式（推荐，最快）
- **方案B**: 创建新 Token，权限组选择 "Zone - Zone Settings"（注意不是 "SSL and Certificates"）

---

### 3. MCP 2026-07-28 无状态协议兼容评估

**状态**: 跟踪中（第2天）
**影响**: MCP协议发布大版本修订，可能影响扫描器

MCP协议07-28发布无状态化架构：
- 移除 initialize 握手和 Mcp-Session-Id
- Tasks 扩展破坏性变更
- MCP Apps 沙箱 iframe 是新攻击面

**需要你做**:
用 Beta SDK 测试 scanner/handshake.py 兼容性，产出兼容性报告
或授权我进行评估

---

## P1 - 本周内处理

### 4. 提交 Glama 评估（阻塞7天）

**状态**: 阻塞中
**影响**: awesome-mcp-servers PR #10694 无法合并

**需要你做**:
1. 前往 https://glama.ai/mcp/servers
2. 提交 lm203688/aishield
3. 获取 quality score
4. 回 PR #10694 评论附上 Glama 链接

---

### 5. 服务恢复后验证 Creem 支付全链路

**状态**: 等待服务恢复
**影响**: 无法确认线上支付是否正常

**自动处理**: 部署成功后我会自动验证
**需要你做**: 如果自动验证失败，需手动触发测试支付

---

## P2 - 近期规划

### 6. npm 包发布（Smithery 需要）

**状态**: 未开始
**影响**: Smithery 目录无法配置生效

**需要你做**: 发布 @aishield/mcp-server 到 npm

---

### 7. License 不一致

**状态**: 发现
**影响**: 企业采用信心

README 写 AGPL-3.0，仓库元数据显示 MIT。需统一。

---

## 已自动处理的问题

| 问题 | 处理方式 | 状态 |
|------|----------|------|
| Nginx 只监听80端口 | 添加443端口+SSL配置 | 已更新，待部署 |
| 自签SSL证书缺失 | 部署脚本自动生成 | 已更新，待部署 |
| 端口80/443被Docker占用 | 部署脚本自动释放 | 已更新，待部署 |
| 部署脚本容错性不足 | 添加Docker+Host双方案 | 已更新 |

---

## 闭环跟踪

| 日期 | 问题 | 跟踪天数 | 状态 |
|------|------|----------|------|
| 07-24 | aishield.tools 不可达 | 7天 | 部署脚本已更新，待部署验证 |
| 07-24 | PR #10694 Glama 评估 | 7天 | 需手动操作 |
| 07-25 | Creem Webhook 验证 | 6天 | 等待服务恢复 |
| 07-28 | MCP协议兼容评估 | 2天 | 需手动评估 |
| 07-30 | Cloudflare API权限 | 0天 | 需手动确认或新建Token |
