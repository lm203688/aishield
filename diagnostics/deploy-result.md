=== DIAGNOSTIC ===
Time: Wed Aug 5 05:45:48 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785923148.6965766, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
NOT RUNNING
=== CLOUDFLARED LOG (last 30 lines) ===
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[17:45:39] Time: Wed Aug  5 05:45:39 PM CST 2026
[17:45:39] User: root (UID: 0)
[17:45:39] === STEP 1: 启动 API (端口 8450) ===
[17:45:39] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[17:45:39] 设置 SSL 模式为 Full...
DNS 更新: OK
[17:45:40] 设置 SSL 模式为 Full...
[17:45:40] API 已在运行
[17:45:40] API 状态: OK
[17:45:40] === STEP 2: 安装 cloudflared ===
[17:45:40] cloudflared 安装路径: /usr/local/bin/cloudflared
[17:45:40] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:45:40] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:45:40] === STEP 3: 检查认证方式 ===
[17:45:40] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[17:45:40] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[17:45:40] 检查现有 tunnel...
[17:45:41] 启动 Named Tunnel (cert 模式)...
[17:45:41] 使用 config: /root/.cloudflared/config.yml
[17:45:41] cloudflared PID: 1825295
SSL: 跳过
[17:45:41] === STEP 6: 启动 Tunnel ===
[17:45:41] 现有 tunnel 列表:

[17:45:41] 创建新 tunnel: aishield-tunnel
SSL: 跳过
[17:45:41] === STEP 6: 启动 Tunnel ===
[17:45:41] 创建输出: 
[17:45:41] Tunnel 创建失败，尝试其他方法...
[17:45:42] 使用第一个可用 tunnel: You
[17:45:42] 凭证文件: /root/.cloudflared/You.json
[17:45:42] 凭证文件不存在，列出 .cloudflared 目录内容:
total 24
drwxr-xr-x 2 root root 4096 Jul 31 07:21 .
drwx------ 8 root root 4096 Jul 28 11:01 ..
-r-------- 1 root root  175 Jul 31 07:21 0c39bcfb-0c96-4858-9025-d54131e062ec.json
-r-------- 1 root root  175 Jul 28 11:03 aa3f86b8-01f4-4ce0-83a8-5512219f9003.json
-rw------- 1 root root  282 Jul 28 11:02 cert.pem
-rw-r--r-- 1 root root  227 Aug  5 17:45 config.yml
[17:45:42] 创建 config.yml...
[17:45:42] config.yml 已创建:
tunnel: You
credentials-file: /root/.cloudflared/You.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[17:45:42] 路由 DNS: aishield.tools -> You.cfargotunnel.com
[17:45:44] 启动 Named Tunnel (cert 模式)...
[17:45:44] 使用 config: /root/.cloudflared/config.yml
[17:45:44] cloudflared PID: 1825433
[17:45:44] 启动 Named Tunnel (cert 模式)...
[17:45:44] 使用 config: /root/.cloudflared/config.yml
[17:45:44] cloudflared PID: 1825450
[17:45:44] DNS 路由结果: 2026-08-05T09:45:44Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:45:44] === STEP 5: 更新 DNS (API) ===
[17:45:44] CNAME: aishield.tools -> You.cfargotunnel.com
[17:45:45] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[17:45:48] 设置 SSL 模式为 Full...
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) (Result: exit-code) since Wed 2026-08-05 17:45:45 CST; 2s ago
    Process: 1825418 ExecStart=/opt/start-tunnel.sh (code=exited, status=1/FAILURE)
   Main PID: 1825418 (code=exited, status=1/FAILURE)
        CPU: 77ms
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
Time: Wed Aug  5 09:45:49 UTC 2026

=== curl test (aishield.tools) ===
error code: 1033

=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
