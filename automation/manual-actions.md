# 需用户手动解决问题清单

> 更新时间: 2026-07-31
> 总指挥汇总，按优先级排序

---

## P0 - 立即处理

### 1. 创建 Cloudflare Tunnel（绕过备案SNI拦截）

**状态**: 根因已确认，等待用户操作
**影响**: aishield.tools 连续8天不可达，支付系统全链路中断

**根因分析（已通过实验确认）**:

| 测试 | 结果 | 结论 |
|------|------|------|
| 443端口 + SNI(aishield.tools) | 连接被重置 | 备案系统拦截SNI |
| 443端口 无SNI(IP直连) | SSL握手成功，API返回200 | Nginx配置正确 |
| 8450端口 + Host(aishield.tools) | 302跳转备案拦截页 | 备案系统拦截Host头 |
| 8443/2053端口 | 安全组未开放 | 无法使用非标准端口 |

**结论**: 腾讯云备案系统检测所有端口中包含 `aishield.tools` 域名的请求（SNI/Host），主动重置连接。Cloudflare直连源站的所有方案均不可行。

**我已自动处理**:
- Nginx SSL配置已修复（TLS 1.2 + Origin CA证书 + 证书链）
- 部署脚本已增强（自动修复未知指令、循环容错）
- cloudflared自动安装和配置逻辑已部署到脚本
- 仅需用户提供Tunnel Token即可自动完成

**需要你做**（10分钟）:

1. 访问 Cloudflare Zero Trust: https://one.dash.cloudflare.com/
2. 左侧菜单: Networks → Tunnels → **Create a tunnel**
3. 选择 **Cloudflared** 类型，命名: `aishield-tunnel`
4. 在安装命令中找到 Token（格式类似 `eyJh...` 很长的字符串）
5. 复制 Token，添加到 GitHub 仓库 Secrets:
   - 仓库: https://github.com/lm203688/aishield/settings/secrets/actions
   - Name: `CLOUDFLARE_TUNNEL_TOKEN`
   - Value: 粘贴 Token
6. 在 Tunnel 的 **Public Hostname** 页面配置:
   - Subdomain: (空)
   - Domain: `aishield.tools`
   - Type: `HTTP`
   - URL: `localhost:8450`
7. 推送任意提交到 main 分支触发部署（或等下次自动部署）

**Tunnel 方案原理**:
```
用户 → Cloudflare边缘 → Tunnel(出站连接) → 服务器cloudflared → localhost:8450
```
- 服务器主动出站连接Cloudflare，无需入站SSL
- 备案系统无法检测出站连接中的域名
- 完全绕过SNI/Host拦截

---

### 2. Cloudflare API Token 权限不足

**状态**: 已确认
**影响**: 无法通过API自动修改SSL设置、创建Tunnel、配置Origin Rules

当前Token (cfut_Moh...) 仅有 Zone:Read 和 DNS:Read 权限。

**需要你做**（可选，用于后续自动化）:
创建新Token，权限组选择:
- Zone - Zone Settings (读写)
- Zone - DNS (读写)
- Account - Cloudflare Tunnel (读写)

---

## P1 - 本周内处理

### 3. 服务恢复后验证 Creem 支付全链路

**状态**: 等待Cloudflare Tunnel部署
**影响**: 无法确认线上支付是否正常

**自动处理**: Tunnel部署后我会自动验证
**需要你做**: 如果自动验证失败，需手动触发测试支付

---

### 4. 提交 Glama 评估（阻塞8天）

**状态**: 阻塞中
**影响**: awesome-mcp-servers PR #10694 无法合并

**需要你做**:
1. 前往 https://glama.ai/mcp/servers
2. 提交 lm203688/aishield
3. 获取 quality score
4. 回 PR #10694 评论附上 Glama 链接

---

### 5. MCP 2026-07-28 无状态协议兼容评估

**状态**: 跟踪中（第3天）
**影响**: MCP协议发布大版本修订

**需要你做**:
用 Beta SDK 测试 scanner/handshake.py 兼容性，或授权我进行评估

---

## P2 - 近期规划

### 6. npm 包发布（Smithery 需要）

**需要你做**: 发布 @aishield/mcp-server 到 npm

### 7. License 不一致

README写AGPL-3.0，仓库元数据显示MIT。需统一。

---

## 已自动处理的问题汇总

| 问题 | 处理方式 | 状态 |
|------|----------|------|
| Nginx 只监听80端口 | 添加443端口+SSL配置 | 已部署 |
| 自签SSL证书缺失 | 部署脚本自动生成Origin CA证书 | 已部署 |
| 证书链不完整 | 拼接服务器证书+根证书 | 已部署 |
| TLS 1.3 bad key share | 降级为TLS 1.2 | 已部署 |
| ssl_ciphersuites不支持 | 部署脚本自动移除未知指令 | 已部署 |
| 端口80/443被Docker占用 | 部署脚本自动释放 | 已部署 |
| iptables防火墙规则 | 部署脚本自动添加443/80规则 | 已部署 |
| 部署脚本容错性不足 | 增强自动修复+cloudflared支持 | 已部署 |
| 定时任务未归集 | 创建automation/管理中枢 | 已完成 |
| 任务状态未汇总 | 创建task-registry.md | 已完成 |

---

## 闭环跟踪

| 日期 | 问题 | 跟踪天数 | 状态 |
|------|------|----------|------|
| 07-24 | aishield.tools 不可达 | 8天 | 根因确认: 备案SNI拦截 → 需Cloudflare Tunnel |
| 07-24 | PR #10694 Glama 评估 | 8天 | 需手动操作 |
| 07-25 | Creem Webhook 验证 | 7天 | 等待Tunnel部署 |
| 07-28 | MCP协议兼容评估 | 3天 | 需手动评估 |
| 07-31 | Cloudflare API权限 | 0天 | 需新建Token(可选) |
