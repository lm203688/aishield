=== DIAGNOSTIC ===
Time: Wed Aug 5 01:36:02 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785908162.6488395, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
NOT RUNNING
=== CLOUDFLARED LOG (last 30 lines) ===
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[13:35:55] Time: Wed Aug  5 01:35:55 PM CST 2026
[13:35:55] User: root (UID: 0)
[13:35:55] === STEP 1: 启动 API (端口 8450) ===
DNS 更新: OK
[13:35:55] 设置 SSL 模式为 Full...
[13:35:56] API 已在运行
[13:35:56] API 状态: OK
[13:35:56] === STEP 2: 安装 cloudflared ===
[13:35:56] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:35:56] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:35:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:35:56] === STEP 3: 检查认证方式 ===
[13:35:56] API 已在运行
[13:35:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:35:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:35:56] API 状态: OK
[13:35:56] 检查现有 tunnel...
[13:35:56] === STEP 2: 安装 cloudflared ===
[13:35:56] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:35:56] 启动 Named Tunnel (cert 模式)...
[13:35:56] 使用 config: /root/.cloudflared/config.yml
[13:35:56] cloudflared PID: 1644334
[13:35:56] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:35:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:35:56] === STEP 3: 检查认证方式 ===
[13:35:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:35:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:35:56] 检查现有 tunnel...
SSL: 跳过
[13:35:57] === STEP 6: 启动 Tunnel ===
[13:35:57] 现有 tunnel 列表:
[13:35:57] 现有 tunnel 列表:


[13:35:57] 创建新 tunnel: aishield-tunnel
[13:35:57] 创建新 tunnel: aishield-tunnel
[13:35:57] 创建输出: failed to create tunnel: Create Tunnel API call failed: tunnel with name already exists
[13:35:57] Tunnel 创建失败，尝试其他方法...
[13:35:57] 创建输出: failed to create tunnel: Create Tunnel API call failed: tunnel with name already exists
[13:35:57] Tunnel 创建失败，尝试其他方法...
[13:35:58] Tunnel 连接已建立!
[13:35:58] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T05:35:56Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-05T05:35:56Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.57
2026-08-05T05:35:57Z INF Registered tunnel connection connIndex=0 connection=3e03e537-9665-4a27-a48d-2a95eca6f6bc event=0 ip=198.41.192.57 location=lax07 protocol=quic
2026-08-05T05:35:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-08-05T05:35:57Z INF Initiating graceful shutdown due to signal terminated ...
2026-08-05T05:35:57Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=0 event=0 ip=198.41.192.57
2026-08-05T05:35:57Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.57
2026-08-05T05:35:57Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.57
2026-08-05T05:35:57Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.57
2026-08-05T05:35:57Z INF Registered tunnel connection connIndex=1 connection=c90c43e5-4725-429e-a469-c8b4934af0ec event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-05T05:35:57Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.200.53
2026-08-05T05:35:57Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.53
2026-08-05T05:35:57Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.53
2026-08-05T05:35:57Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.53
2026-08-05T05:35:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.37
[13:35:58] === STEP 7: 持久化 ===
[13:35:59] 使用第一个可用 tunnel: You
[13:35:59] 凭证文件: /root/.cloudflared/You.json
[13:35:59] 凭证文件不存在，列出 .cloudflared 目录内容:
total 24
drwxr-xr-x 2 root root 4096 Jul 31 07:21 .
drwx------ 8 root root 4096 Jul 28 11:01 ..
-r-------- 1 root root  175 Jul 31 07:21 0c39bcfb-0c96-4858-9025-d54131e062ec.json
-r-------- 1 root root  175 Jul 28 11:03 aa3f86b8-01f4-4ce0-83a8-5512219f9003.json
-rw------- 1 root root  282 Jul 28 11:02 cert.pem
-rw-r--r-- 1 root root  227 Aug  5 13:35 config.yml
[13:35:59] 创建 config.yml...
[13:35:59] config.yml 已创建:
tunnel: You
credentials-file: /root/.cloudflared/You.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:35:59] 路由 DNS: aishield.tools -> You.cfargotunnel.com
[13:35:59] 使用第一个可用 tunnel: You
[13:35:59] 凭证文件: /root/.cloudflared/You.json
[13:35:59] 凭证文件不存在，列出 .cloudflared 目录内容:
total 24
drwxr-xr-x 2 root root 4096 Jul 31 07:21 .
drwx------ 8 root root 4096 Jul 28 11:01 ..
-r-------- 1 root root  175 Jul 31 07:21 0c39bcfb-0c96-4858-9025-d54131e062ec.json
-r-------- 1 root root  175 Jul 28 11:03 aa3f86b8-01f4-4ce0-83a8-5512219f9003.json
-rw------- 1 root root  282 Jul 28 11:02 cert.pem
-rw-r--r-- 1 root root  161 Aug  5 13:35 config.yml
[13:35:59] 创建 config.yml...
[13:35:59] config.yml 已创建:
tunnel: You
credentials-file: /root/.cloudflared/You.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:35:59] 路由 DNS: aishield.tools -> You.cfargotunnel.com
[13:35:59] systemd 服务已配置
[13:35:59] Cron 保活已设置
[13:35:59] === STEP 8: 验证 ===
[13:35:59] --- API (localhost:8450) ---
 OK
[13:35:59] --- cloudflared 进程 ---
root     1644334  3.6  1.9 1294676 39980 ?       Sl   13:35   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1644620  0.0  1.5 1358092 30948 ?       Sl   13:35   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
root     1644663  0.0  1.5 1292740 30744 ?       Sl   13:35   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
[13:35:59] --- aishield.tools ---
[13:36:00] 启动 Named Tunnel (cert 模式)...
[13:36:00] 使用 config: /root/.cloudflared/config.yml
[13:36:00] cloudflared PID: 1644720
 FAIL (DNS 传播中或配置错误)
[13:36:00] --- DNS CNAME ---
[13:36:00] --- DNS A ---
104.21.81.46
172.67.188.44
[13:36:00] === 部署汇总 ===
[13:36:00] Tunnel Mode: cert
[13:36:00] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:36:00] API: http://localhost:8450
[13:36:00] 域名: https://aishield.tools
[13:36:00] cloudflared: /usr/local/bin/cloudflared
[13:36:00] PID: 1644334
[13:36:00] Config: /root/.cloudflared/config.yml
[13:36:00] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:36:00] 状态: Named Tunnel (cert 模式) 已配置
[13:36:01] DNS 路由结果: 2026-08-05T05:36:01Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:36:01] === STEP 5: 更新 DNS (API) ===
[13:36:01] CNAME: aishield.tools -> You.cfargotunnel.com
[13:36:01] DNS 路由结果: 2026-08-05T05:36:01Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:36:01] === STEP 5: 更新 DNS (API) ===
[13:36:01] CNAME: aishield.tools -> You.cfargotunnel.com
[13:36:01] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) (Result: exit-code) since Wed 2026-08-05 13:36:00 CST; 2s ago
    Process: 1644669 ExecStart=/opt/start-tunnel.sh (code=exited, status=1/FAILURE)
   Main PID: 1644669 (code=exited, status=1/FAILURE)
        CPU: 81ms
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
Time: Wed Aug  5 05:36:02 UTC 2026

=== curl test (aishield.tools) ===
error code: 1033

=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
