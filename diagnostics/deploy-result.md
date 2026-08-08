=== DIAGNOSTIC ===
Time: Sat Aug 8 10:14:47 PM CST 2026
=== USER ===
root
=== GIT LOG ===
dbcf345 fix: download script from GitHub raw if git reset fails, add script version diagnostics
14ced6b chore: update deploy diagnostics [skip ci]
7b4068b fix: force git reset on server to get latest deploy script
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786198487.9372847, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
NOT RUNNING
=== CLOUDFLARED LOG (last 30 lines) ===
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[22:13:34] Time: Sat Aug  8 10:13:34 PM CST 2026
[22:13:34] User: root (UID: 0)
[22:13:34] === STEP 1: 启动 API (端口 8450) ===
[22:13:42] API 已在运行
[22:13:42] API 状态: OK
[22:13:42] === STEP 2: 安装 cloudflared ===
[22:13:42] cloudflared 安装路径: /usr/local/bin/cloudflared
[22:13:42] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:13:42] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:13:42] === STEP 3: 检查认证方式 ===
[22:13:42] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[22:13:42] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[22:13:42] 检查现有 tunnel...
[22:13:43] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax09, 2xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[22:13:43] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[22:13:43] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[22:13:43] 凭证文件存在
[22:13:43] 创建 config.yml...
[22:13:43] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[22:13:43] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:13:46] DNS 路由结果: 2026-08-08T14:13:46Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[22:13:46] === STEP 5: 更新 DNS (API) ===
[22:13:46] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:13:48] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[22:13:49] API 已在运行
[22:13:49] API 状态: OK
[22:13:49] === STEP 2: 安装 cloudflared ===
[22:13:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[22:13:49] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:13:49] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:13:49] === STEP 3: 检查认证方式 ===
[22:13:49] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[22:13:49] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[22:13:49] 检查现有 tunnel...
DNS 更新: OK
[22:13:51] 设置 SSL 模式为 Full...
SSL: 跳过
[22:13:52] === STEP 6: 启动 Tunnel ===
[22:13:52] 现有 tunnel 列表:

[22:13:52] 创建新 tunnel: aishield-tunnel
[22:13:54] 创建输出: failed to create tunnel: Create Tunnel API call failed: tunnel with name already exists
[22:13:54] Tunnel 创建失败，尝试其他方法...
[22:13:55] 使用第一个可用 tunnel: You
[22:13:55] 凭证文件: /root/.cloudflared/You.json
[22:13:55] 凭证文件不存在，列出 .cloudflared 目录内容:
total 24
drwxr-xr-x 2 root root 4096 Jul 31 07:21 .
drwx------ 8 root root 4096 Jul 28 11:01 ..
-r-------- 1 root root  175 Jul 31 07:21 0c39bcfb-0c96-4858-9025-d54131e062ec.json
-r-------- 1 root root  175 Jul 28 11:03 aa3f86b8-01f4-4ce0-83a8-5512219f9003.json
-rw------- 1 root root  282 Jul 28 11:02 cert.pem
-rw-r--r-- 1 root root  227 Aug  8 22:13 config.yml
[22:13:55] 创建 config.yml...
[22:13:55] config.yml 已创建:
tunnel: You
credentials-file: /root/.cloudflared/You.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[22:13:55] 路由 DNS: aishield.tools -> You.cfargotunnel.com
[22:13:55] 启动 Named Tunnel (cert 模式)...
[22:13:55] 使用 config: /root/.cloudflared/config.yml
[22:13:55] cloudflared PID: 929196
[22:13:57] DNS 路由结果: 2026-08-08T14:13:57Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[22:13:57] === STEP 5: 更新 DNS (API) ===
[22:13:57] CNAME: aishield.tools -> You.cfargotunnel.com
[22:13:58] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[22:13:59] 设置 SSL 模式为 Full...
SSL: 跳过
[22:14:00] === STEP 6: 启动 Tunnel ===
[22:14:03] 启动 Named Tunnel (cert 模式)...
[22:14:03] 使用 config: /root/.cloudflared/config.yml
[22:14:03] cloudflared PID: 929348
[22:14:05] 等待 tunnel 连接... (10s)
[22:14:13] 等待 tunnel 连接... (10s)
[22:14:15] 等待 tunnel 连接... (20s)
[22:14:23] 等待 tunnel 连接... (20s)
[22:14:25] 等待 tunnel 连接... (30s)
[22:14:33] 等待 tunnel 连接... (30s)
[22:14:35] 等待 tunnel 连接... (40s)
[22:14:35] --- cloudflared 日志 (最后 15 行) ---
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
[22:14:35] === STEP 7: 持久化 ===
[22:14:36] systemd 服务已配置
[22:14:36] Cron 保活已设置
[22:14:36] === STEP 8: 验证 ===
[22:14:36] --- API (localhost:8450) ---
 OK
[22:14:36] --- cloudflared 进程 ---
root      929872  0.0  1.3 1292740 27192 ?       Rl   22:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[22:14:36] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[22:14:37] --- DNS CNAME ---
[22:14:38] --- DNS A ---
104.21.81.46
172.67.188.44
[22:14:38] === 部署汇总 ===
[22:14:38] Tunnel Mode: cert
[22:14:38] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[22:14:38] API: http://localhost:8450
[22:14:38] 域名: https://aishield.tools
[22:14:38] cloudflared: /usr/local/bin/cloudflared
[22:14:38] PID: 929196
[22:14:38] Config: /root/.cloudflared/config.yml
[22:14:38] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:14:38] 状态: Named Tunnel (cert 模式) 已配置
[22:14:43] 等待 tunnel 连接... (40s)
[22:14:43] --- cloudflared 日志 (最后 15 行) ---
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
[22:14:43] === STEP 7: 持久化 ===
[22:14:44] systemd 服务已配置
[22:14:44] Cron 保活已设置
[22:14:44] === STEP 8: 验证 ===
[22:14:44] --- API (localhost:8450) ---
 OK
[22:14:44] --- cloudflared 进程 ---
root      930172  0.0  1.3 1292484 27704 ?       Sl   22:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[22:14:44] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[22:14:45] --- DNS CNAME ---
[22:14:45] --- DNS A ---
172.67.188.44
104.21.81.46
[22:14:45] === 部署汇总 ===
[22:14:45] Tunnel Mode: cert
[22:14:45] Tunnel ID: You
[22:14:45] API: http://localhost:8450
[22:14:45] 域名: https://aishield.tools
[22:14:45] cloudflared: /usr/local/bin/cloudflared
[22:14:45] PID: 929348
[22:14:45] Config: /root/.cloudflared/config.yml
[22:14:45] CNAME: You.cfargotunnel.com
[22:14:45] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) (Result: exit-code) since Sat 2026-08-08 22:14:45 CST; 2s ago
    Process: 930168 ExecStart=/opt/start-tunnel.sh (code=exited, status=1/FAILURE)
   Main PID: 930168 (code=exited, status=1/FAILURE)
        CPU: 110ms
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450      0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                 
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
Time: Sat Aug  8 14:14:48 UTC 2026

=== curl test (aishield.tools) ===
error code: 1033

=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
