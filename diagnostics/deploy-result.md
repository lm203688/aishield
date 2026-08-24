=== DIAGNOSTIC ===
Time: Mon Aug 24 05:51:34 PM CST 2026
=== USER ===
root
=== GIT LOG ===
dbcf3459 fix: download script from GitHub raw if git reset fails, add script version diagnostics
14ced6b0 chore: update deploy diagnostics [skip ci]
7b4068ba fix: force git reset on server to get latest deploy script
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787565094.1751444, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
NOT RUNNING
=== CLOUDFLARED LOG (last 30 lines) ===
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[17:50:40] Time: Mon Aug 24 05:50:40 PM CST 2026
[17:50:40] User: root (UID: 0)
[17:50:40] === STEP 1: 启动 API (端口 8450) ===
[17:50:40] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[17:50:41] 设置 SSL 模式为 Full...
[17:50:41] API 已在运行
[17:50:41] API 状态: OK
[17:50:41] === STEP 2: 安装 cloudflared ===
[17:50:41] cloudflared 安装路径: /usr/local/bin/cloudflared
[17:50:41] DNS 路由结果: 2026-08-24T09:50:41Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:50:41] === STEP 5: 更新 DNS (API) ===
[17:50:41] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:50:41] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:50:41] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:50:41] === STEP 3: 检查认证方式 ===
[17:50:41] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[17:50:41] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[17:50:41] 检查现有 tunnel...
SSL: 跳过
[17:50:41] === STEP 6: 启动 Tunnel ===
[17:50:41] 现有 tunnel 列表:

[17:50:41] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[17:50:41] 创建新 tunnel: aishield-tunnel
DNS 更新: OK
[17:50:42] 设置 SSL 模式为 Full...
[17:50:42] 创建输出: failed to create tunnel: Create Tunnel API call failed: tunnel with name already exists
[17:50:42] Tunnel 创建失败，尝试其他方法...
SSL: 跳过
[17:50:43] 使用第一个可用 tunnel: You
[17:50:43] 凭证文件: /root/.cloudflared/You.json
[17:50:43] === STEP 6: 启动 Tunnel ===
[17:50:43] 凭证文件不存在，列出 .cloudflared 目录内容:
total 24
drwxr-xr-x 2 root root 4096 Jul 31 07:21 .
drwx------ 9 root root 4096 Aug 10 08:42 ..
-r-------- 1 root root  175 Jul 31 07:21 0c39bcfb-0c96-4858-9025-d54131e062ec.json
-r-------- 1 root root  175 Jul 28 11:03 aa3f86b8-01f4-4ce0-83a8-5512219f9003.json
-rw------- 1 root root  282 Jul 28 11:02 cert.pem
-rw-r--r-- 1 root root  227 Aug 24 17:50 config.yml
[17:50:43] 创建 config.yml...
[17:50:43] config.yml 已创建:
tunnel: You
credentials-file: /root/.cloudflared/You.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[17:50:43] 路由 DNS: aishield.tools -> You.cfargotunnel.com
[17:50:44] DNS 路由结果: 2026-08-24T09:50:44Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:50:44] === STEP 5: 更新 DNS (API) ===
[17:50:44] CNAME: aishield.tools -> You.cfargotunnel.com
[17:50:44] 启动 Named Tunnel (cert 模式)...
[17:50:44] 使用 config: /root/.cloudflared/config.yml
[17:50:44] cloudflared PID: 3302214
[17:50:45] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[17:50:45] 设置 SSL 模式为 Full...
[17:50:46] 启动 Named Tunnel (cert 模式)...
[17:50:46] 使用 config: /root/.cloudflared/config.yml
[17:50:46] cloudflared PID: 3302269
SSL: 跳过
[17:50:46] === STEP 6: 启动 Tunnel ===
[17:50:49] 启动 Named Tunnel (cert 模式)...
[17:50:49] 使用 config: /root/.cloudflared/config.yml
[17:50:49] cloudflared PID: 3302342
[17:50:54] 等待 tunnel 连接... (10s)
[17:50:56] 等待 tunnel 连接... (10s)
[17:50:59] 等待 tunnel 连接... (10s)
[17:51:04] 等待 tunnel 连接... (20s)
[17:51:06] 等待 tunnel 连接... (20s)
[17:51:09] 等待 tunnel 连接... (20s)
[17:51:14] 等待 tunnel 连接... (30s)
[17:51:16] 等待 tunnel 连接... (30s)
[17:51:19] 等待 tunnel 连接... (30s)
[17:51:24] 等待 tunnel 连接... (40s)
[17:51:24] --- cloudflared 日志 (最后 15 行) ---
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
[17:51:24] === STEP 7: 持久化 ===
[17:51:25] systemd 服务已配置
[17:51:25] Cron 保活已设置
[17:51:25] === STEP 8: 验证 ===
[17:51:25] --- API (localhost:8450) ---
 OK
[17:51:25] --- cloudflared 进程 ---
root     3303001  0.0  1.1 1292484 22800 ?       Rl   17:51   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[17:51:25] --- aishield.tools ---
[17:51:26] 等待 tunnel 连接... (40s)
[17:51:26] --- cloudflared 日志 (最后 15 行) ---
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
[17:51:26] === STEP 7: 持久化 ===
[17:51:26] systemd 服务已配置
[17:51:26] Cron 保活已设置
[17:51:26] === STEP 8: 验证 ===
[17:51:26] --- API (localhost:8450) ---
 OK
[17:51:26] --- cloudflared 进程 ---
root     3303122  0.0  1.3 1292484 27424 ?       Rl   17:51   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[17:51:26] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[17:51:27] --- DNS CNAME ---
 FAIL (DNS 传播中或配置错误)
[17:51:27] --- DNS CNAME ---
[17:51:27] --- DNS A ---
[17:51:27] --- DNS A ---
104.21.81.46
172.67.188.44
[17:51:27] === 部署汇总 ===
[17:51:27] Tunnel Mode: cert
[17:51:27] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
172.67.188.44
104.21.81.46
[17:51:27] API: http://localhost:8450
[17:51:27] === 部署汇总 ===
[17:51:27] 域名: https://aishield.tools
[17:51:27] Tunnel Mode: cert
[17:51:27] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:51:27] cloudflared: /usr/local/bin/cloudflared
[17:51:27] PID: 3302269
[17:51:27] API: http://localhost:8450
[17:51:27] 域名: https://aishield.tools
[17:51:27] cloudflared: /usr/local/bin/cloudflared
[17:51:27] Config: /root/.cloudflared/config.yml
[17:51:27] PID: 3302214
[17:51:27] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:51:27] 状态: Named Tunnel (cert 模式) 已配置
[17:51:27] Config: /root/.cloudflared/config.yml
[17:51:27] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:51:27] 状态: Named Tunnel (cert 模式) 已配置
[17:51:29] 等待 tunnel 连接... (40s)
[17:51:29] --- cloudflared 日志 (最后 15 行) ---
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
[17:51:29] === STEP 7: 持久化 ===
[17:51:30] systemd 服务已配置
[17:51:30] Cron 保活已设置
[17:51:30] === STEP 8: 验证 ===
[17:51:30] --- API (localhost:8450) ---
 OK
[17:51:30] --- cloudflared 进程 ---
root     3303377  0.0  1.3 1292484 27720 ?       Sl   17:51   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[17:51:30] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[17:51:30] --- DNS CNAME ---
[17:51:31] --- DNS A ---
104.21.81.46
172.67.188.44
[17:51:31] === 部署汇总 ===
[17:51:31] Tunnel Mode: cert
[17:51:31] Tunnel ID: You
[17:51:31] API: http://localhost:8450
[17:51:31] 域名: https://aishield.tools
[17:51:31] cloudflared: /usr/local/bin/cloudflared
[17:51:31] PID: 3302342
[17:51:31] Config: /root/.cloudflared/config.yml
[17:51:31] CNAME: You.cfargotunnel.com
[17:51:31] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) (Result: exit-code) since Mon 2026-08-24 17:51:30 CST; 3s ago
    Process: 3303371 ExecStart=/opt/start-tunnel.sh (code=exited, status=1/FAILURE)
   Main PID: 3303371 (code=exited, status=1/FAILURE)
        CPU: 88ms
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450      0.0.0.0:*    users:(("python3",pid=2525069,fd=3))                                                    
=== CRONTAB ===
*/5 * * * * flock -xn /tmp/stargate.lock -c '/usr/local/qcloud/stargate/admin/start.sh > /dev/null 2>&1 &'
* * * * * pgrep -f 'cloudflared tunnel' > /dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
=== START SCRIPT ===
#!/bin/bash
# AIShield Tunnel 启动脚本
CF_BIN='/usr/local/bin/cloudflared'
CONFIG_FILE='/root/.cloudflared/config.yml'
TOKEN_FILE='/root/.cloudflared/tunnel-token'

cleanup() { kill $CF_PID 2>/dev/null; exit 0; }
trap cleanup SIGTERM SIGINT

if [ -f "$CONFIG_FILE" ]; then
    $CF_BIN tunnel --config "$CONFIG_FILE" run &
    CF_PID=$!
elif [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE")
    $CF_BIN tunnel run --token "$TOKEN" &
    CF_PID=$!
else
    $CF_BIN tunnel --url http://localhost:8450 &
    CF_PID=$!
fi

wait $CF_PID

=== HTTPS Test from Runner ===
Time: Mon Aug 24 09:51:34 UTC 2026

=== curl test (aishield.tools) ===
error code: 1033

=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
