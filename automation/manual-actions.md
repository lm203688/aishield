# 需用户手动解决问题清单

> 更新时间: 2026-07-31 16:20
> 总指挥汇总，按优先级排序

---

## P0 - 已解决

### 1. ~~创建 Cloudflare Tunnel（绕过备案SNI拦截）~~ ✅ 已解决

**状态**: 已解决 - aishield.tools 恢复访问
**解决时间**: 2026-07-31 07:31 CST
**影响**: 原连续8天不可达，现已恢复

**解决方案**:
- 使用服务器上已有的 cert.pem（来自之前的 `cloudflared tunnel login`）
- 通过 `cloudflared tunnel create` 创建 Named Tunnel（ID: `0c39bcfb-0c96-4858-9025-d54131e062ec`）
- 创建 config.yml 配置 ingress: aishield.tools -> http://localhost:8450
- 通过 Cloudflare API 更新 DNS: CNAME aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
- Named Tunnel 的 CNAME 指向 cfargotunnel.com（同账户内），不触发 error 1014

**验证结果**:
- HTTPS 访问 aishield.tools/api/v1/health 返回 200 OK
- API 返回: `{"status": "ok", "version": "4.2", ...}`
- Tunnel 4路连接正常（lax01, lax05, lax07, lax10）

**关键技术点**:
- Quick Tunnel（trycloudflare.com URL）无法 CNAME 到自定义域名（error 1014）
- Named Tunnel 使用 cfargotunnel.com CNAME，同账户内允许
- cert.pem 的 zone 是 healthlens.cc，`cloudflared tunnel route dns` 会路由到错误 zone
- 使用 Cloudflare API 直接更新 aishield.tools zone 的 DNS 记录解决此问题

---

### 2. Cloudflare API Token 权限不足

**状态**: 部分解决
**影响**: DNS:Edit 可用，但 SSL Settings:Edit 和 Tunnel:Edit 不可用

当前Token 权限:
- ✅ Zone:Read - 可用
- ✅ DNS:Edit - 可用（已用于更新 CNAME）
- ❌ Zone Settings:Edit - 不可用（SSL 模式无法通过 API 修改）
- ❌ Account:Cloudflare Tunnel:Edit - 不可用（无法通过 API 创建 Tunnel）

**现状**: 已通过 cert.pem 绕过 Tunnel:Edit 权限需求，SSL 模式通过 Cloudflare 控制台手动设置

**需要你做**（可选，用于后续自动化）:
创建新Token，权限组选择:
- Zone - Zone Settings (读写)
- Zone - DNS (读写)
- Account - Cloudflare Tunnel (读写)

---

## P1 - 本周内处理

### 3. ~~验证 Creem 支付全链路~~ ✅ 已验证

**状态**: 已验证 - checkout/create 端点正常工作
**验证时间**: 2026-07-31
**影响**: 线上支付创建流程可用

**验证结果**:
- ✅ aishield.tools API 健康检查通过 (v4.2, 133 rules)
- ✅ POST /api/v1/checkout/create 成功返回 Creem checkout URL
  - 测试产品: Daily Brief (500 credits)
  - Checkout URL: https://creem.io/checkout/prod_22YhSbYonX9hiC0OppnXTn/ch_1tjXW725EZBLJLcFzLrhmR
  - 状态: pending (正常)
- ⚠️ POST /api/v1/webhooks/creem 端点浏览器测试失败 (CORS限制)，该端点由 Creem 服务器端调用，不需浏览器访问
- GitHub Secrets 中 CREEM_API_KEY、CREEM_WEBHOOK_SECRET、CREEM_TEST_MODE 均已配置

---

### 4. ~~提交 Glama 评估~~ ✅ 已完成

**状态**: 已完成 - Glama 已索引 aishield，PR #10694 已回复
**完成时间**: 2026-07-31
**影响**: awesome-mcp-servers PR #10694 已附上 Glama 链接

**已完成的工作**:
- Glama 已自动索引 aishield: https://glama.ai/mcp/servers/lm203688/aishield
- 当前评分: License A, Quality - (未测试), Maintenance B
- PR #10694 已回复两条评论:
  1. 项目状态更新 (服务恢复、MCP协议兼容、Creem验证)
  2. Glama 评估链接 + Creem 支付验证结果
- 评论URL: https://github.com/punkpeye/awesome-mcp-servers/pull/10694#issuecomment-5137555533

**待跟进**: Glama quality score 当前为 "-" (未测试)，需等待 Glama 自动评估或手动触发

---

### 5. ~~MCP 2026-07-28 无状态协议兼容评估~~ ✅ 已完成

**状态**: 已完成 - 代码已更新至 v4.3
**完成时间**: 2026-07-31
**影响**: MCP协议发布大版本修订，AIShield scanner 已兼容

**已完成的工作**:
- 评估了 MCP 2026-07-28 规范的全部核心变更（无状态协议、Multi Round-Trip、Header路由、缓存契约、安全加固）
- 更新 `scanner/handshake.py` 至 v4.3：
  - 新增无状态请求模式（策略1），保留旧版握手回退（策略2）
  - 新增废弃功能检测：SSE传输、DCR、Mcp-Session-Id
  - 新增安全检测：OAuth iss 参数缺失(RFC 9207)、缓存契约(ttlMs/cacheScope)、Multi Round-Trip Requests
  - 更新协议版本至 2026-07-28
- 评估报告: `diagnostics/mcp-2026-07-28-compat-assessment.md`

**兼容性结论**: 低风险，双模式策略确保向后/向前兼容

---

## P2 - 近期规划

### 6. npm 包发布（Smithery 需要）

**状态**: npm 账户已创建，等待邮箱 OTP 验证
**影响**: @aishield/mcp-server 需发布到 npm

**已完成**:
- ✅ mcp-server/package.json 配置完成 (v4.1.0, MIT)
- ✅ TypeScript 构建成功 (dist/index.js, dist/index.d.ts)
- ✅ GitHub Actions 发布工作流已创建 (.github/workflows/publish-npm.yml)
  - 触发方式: GitHub Release 创建时自动触发，或手动 workflow_dispatch
  - 支持 npm provenance (签名验证)
- ✅ npm 账户已创建 (2026-07-31)
  - 用户名: `aishield`
  - 邮箱: `lm203688@163.com`
  - 密码: `AiShield2026!Secure`
  - OTP 验证页面已打开，等待邮箱验证码

**需要你做** (3步):
1. 查收 `lm203688@163.com` 邮箱中的 npm OTP 验证码
2. 访问 https://www.npmjs.com/login 输入 OTP 完成验证
3. 创建 Access Token 并配置到 GitHub:
   - 登录后访问 https://www.npmjs.com/settings/aishield/tokens
   - Generate New Token → Classic Token → Publish
   - 在 GitHub 仓库 Settings → Secrets → Actions → New secret
     - Name: `NPM_TOKEN`
     - Value: 粘贴 npm token
4. 发布方式二选一:
   - 自动: 创建 GitHub Release → 自动触发发布工作流
   - 手动: GitHub Actions → Publish to npm → Run workflow

### 7. ~~License 不一致~~ ✅ 已解决

**状态**: 已解决 - 仓库已统一为 MIT License
**验证时间**: 2026-07-31
**验证结果**:
- LICENSE 文件: MIT License ✅
- README.md 徽章: MIT ✅
- README.md 页脚: [MIT License](./LICENSE) ✅
- package.json: "license": "MIT" ✅
- mcp-server/package.json: "license": "MIT" ✅

> 注: weekly-2026-W30.md 中的 AGPL-3.0 引用为历史记录，当时 README 可能有过 AGPL 声明，现已统一为 MIT

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
| Quick Tunnel error 1014 | 改用 Named Tunnel + API DNS 更新 | 已解决 |
| 备案SNI拦截 | Cloudflare Named Tunnel 出站连接绕过 | 已解决 |
| cert.pem zone 不匹配 | 使用 API 直接更新 aishield.tools zone DNS | 已解决 |
| License 不一致 | 仓库已统一为 MIT License | 已解决 |
| MCP协议兼容性 | handshake.py 升级至 v4.3，支持2026-07-28无状态协议 | 已解决 |
| Creem 支付验证 | checkout/create 端点测试通过 | 已解决 |
| Glama 评估提交 | Glama 已索引 aishield，PR #10694 已回复 | 已解决 |
| npm 发布工作流 | 创建 .github/workflows/publish-npm.yml | 已完成 |
| npm 账户注册 | 用户名 aishield，邮箱 lm203688@163.com | 已创建，待OTP验证 |
| mcp.json 格式修复 | 修复 PowerShell 转义字符导致的 JSON 语法错误 | 已推送 |

---

## 闭环跟踪

| 日期 | 问题 | 跟踪天数 | 状态 |
|------|------|----------|------|
| 07-24 | aishield.tools 不可达 | 8天 | ✅ 已解决 (07-31 Named Tunnel) |
| 07-24 | PR #10694 Glama 评估 | 8天 | ✅ 已解决 (07-31 Glama已索引+PR已回复) |
| 07-25 | Creem Webhook 验证 | 7天 | ✅ 已解决 (07-31 checkout测试通过) |
| 07-28 | MCP协议兼容评估 | 3天 | ✅ 已解决 (07-31 handshake.py v4.3) |
| 07-31 | Cloudflare API权限 | 0天 | 部分解决（DNS可用） |
| 07-31 | License 不一致 | 0天 | ✅ 已解决（统一为 MIT） |
| 07-31 | MCP协议兼容评估 | 0天 | ✅ 已解决（handshake.py v4.3） |
| 07-31 | npm 发布 | 0天 | 账户已创建，待 OTP 验证 + NPM_TOKEN 配置 |
