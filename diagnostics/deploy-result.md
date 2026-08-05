=== DIAGNOSTIC ===
Time: Wed Aug 5 06:11:40 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785924700.7285833, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
NOT RUNNING
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-05T10:11:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-05T10:11:34Z INF Registered tunnel connection connIndex=2 connection=54e9671f-d7f3-443b-b9d7-08fe3f8b3165 event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-05T10:11:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.6322026-08-05T10:11:35Z INF Registered tunnel connection connIndex=3 connection=ae754053-4728-46db-9ca8-3503edec338d event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-05T10:11:38Z INF Initiating graceful shutdown due to signal terminated ...
2026-08-05T10:11:38Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.200.43
2026-08-05T10:11:38Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.43
2026-08-05T10:11:38Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.43
2026-08-05T10:11:38Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.43
2026-08-05T10:11:382026-08-05T10:11:38Z ERR failed to run t2026-08-05T10:11:38Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.200.63
2026-08-05T10:11:38Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.63
2026-08-05T10:11:38Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.63
2026-08-05T10:11:38Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.200.63
2026-08-05T10:11:382026-08-05T10:11:38Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.192.7
2026-08-05T10:11:38Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.7
2026-08-05T10:11:38Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.7
2026-08-05T10:11:38Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.7
2026-08-05T10:11:38Z ERR Connection terminated connIndex=0
2026-08-05T10:11:38Z ERR failed to run the datag2026-08-05T10:11:38Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.192.7
2026-08-05T10:11:38Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.7
2026-08-05T10:11:38Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.7
2026-08-05T10:11:38Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.7
2026-08-05T10:12026-08-05T10:11:39Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.200.43
2026-08-05T10:11:39Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.43
2026-08-05T10:11:39Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.43
2026-08-05T10:11:39Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.43
2026-08-05T10:11:39Z ERR Connection terminated connIndex=1
2026-08-05T10:11:39Z ERR no more connections active and exiting
2026-08-05T10:11:39Z INF Tunnel server stopped
2026-08-05T10:11:39Z INF Metrics server stopped
2026-08-05T10:11:39Z ERR icmp router terminated error="context canceled"
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:11:31] Time: Wed Aug  5 06:11:31 PM CST 2026
[18:11:31] User: root (UID: 0)
[18:11:31] === STEP 1: 启动 API (端口 8450) ===
[18:11:31] Tunnel 连接已建立!
[18:11:31] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T10:11:29Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-05T10:11:29Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-05T10:11:29Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-05T10:11:29Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T10:11:29Z INF Generated Connector ID: e677667a-2ba8-4f74-8e71-bd337cd336e8
2026-08-05T10:11:29Z INF Initial protocol quic
2026-08-05T10:11:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T10:11:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T10:11:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T10:11:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T10:11:29Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-05T10:11:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.7
2026-08-05T10:11:30Z INF Registered tunnel connection connIndex=0 connection=bada96b3-705a-448b-85e8-daa99c3cbcba event=0 ip=198.41.192.7 location=lax10 protocol=quic
2026-08-05T10:11:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-05T10:11:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
[18:11:31] === STEP 7: 持久化 ===
[18:11:32] API 已在运行
[18:11:32] API 状态: OK
[18:11:32] === STEP 2: 安装 cloudflared ===
[18:11:32] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:11:32] 启动 Named Tunnel (cert 模式)...
[18:11:32] 使用 config: /root/.cloudflared/config.yml
[18:11:32] cloudflared PID: 1852097
[18:11:32] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:11:32] systemd 服务已配置
[18:11:32] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:11:32] === STEP 3: 检查认证方式 ===
[18:11:32] Cron 保活已设置
[18:11:32] === STEP 8: 验证 ===
[18:11:32] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:11:32] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:11:32] --- API (localhost:8450) ---
[18:11:32] 检查现有 tunnel...
 OK
[18:11:32] --- cloudflared 进程 ---
root     1851915  3.0  1.9 1294420 38760 ?       Sl   18:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1852097  0.0  1.7 1294100 35612 ?       Sl   18:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1852129  0.0  1.6 1293580 33740 ?       Sl   18:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:11:32] --- aishield.tools ---
[18:11:33] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xlax01, 1xlax07, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[18:11:33] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:11:33] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:11:33] 凭证文件存在
[18:11:33] 创建 config.yml...
[18:11:33] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:11:33] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
 OK
[18:11:34] --- DNS CNAME ---
[18:11:34] Tunnel 连接已建立!
[18:11:34] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T10:11:32Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T10:11:32Z INF Generated Connector ID: 354cabf9-3dc1-444f-8bb0-b1f1d21119d0
2026-08-05T10:11:32Z INF Initial protocol quic
2026-08-05T10:11:32Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T10:11:32Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T10:11:32Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T10:11:32Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T10:11:32Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-05T10:11:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-05T10:11:33Z INF Registered tunnel connection connIndex=0 connection=b1291950-46be-48f5-92a3-c145574c5e7b event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-05T10:11:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-05T10:11:33Z INF Registered tunnel connection connIndex=1 connection=f1d4da05-1e40-443b-b3da-ec50d0d33ae9 event=0 ip=198.41.192.7 location=lax10 protocol=quic
2026-08-05T10:11:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
gistered tunnel connection connIndex=3 connection=1ccc6693-58f9-495e-9f32-f9f9046897c6 event=0 ip=198.41.192.37 location=lax07 protocol=quic
2026-08-05T10:11:32Z INF Registered tunnel connection connIndex=2 connection=89c49188-7e21-4b1f-b713-012ea1eb3c88 event=0 ip=198.41.200.33 location=lax01 protocol=quic
[18:11:34] === STEP 7: 持久化 ===
[18:11:34] --- DNS A ---
104.21.81.46
172.67.188.44
[18:11:34] === 部署汇总 ===
[18:11:34] Tunnel Mode: cert
[18:11:34] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:11:34] API: http://localhost:8450
[18:11:34] 域名: https://aishield.tools
[18:11:34] cloudflared: /usr/local/bin/cloudflared
[18:11:34] PID: 1851915
[18:11:34] Config: /root/.cloudflared/config.yml
[18:11:34] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:11:34] 状态: Named Tunnel (cert 模式) 已配置
[18:11:35] DNS 路由结果: 2026-08-05T10:11:35Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:11:35] === STEP 5: 更新 DNS (API) ===
[18:11:35] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:11:35] systemd 服务已配置
[18:11:35] Cron 保活已设置
[18:11:35] === STEP 8: 验证 ===
[18:11:35] --- API (localhost:8450) ---
 OK
[18:11:35] --- cloudflared 进程 ---
root     1851915  1.6  1.9 1294420 38760 ?       Sl   18:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1852097  3.3  1.9 1294100 38520 ?       Sl   18:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1852412  0.0  1.3 1292484 27432 ?       Rl   18:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:11:35] --- aishield.tools ---
[18:11:35] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:11:36] 设置 SSL 模式为 Full...
 OK
[18:11:37] --- DNS CNAME ---
[18:11:37] --- DNS A ---
104.21.81.46
172.67.188.44
[18:11:37] === 部署汇总 ===
[18:11:37] Tunnel Mode: cert
[18:11:37] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:11:37] API: http://localhost:8450
[18:11:37] 域名: https://aishield.tools
[18:11:37] cloudflared: /usr/local/bin/cloudflared
[18:11:37] PID: 1852097
[18:11:37] Config: /root/.cloudflared/config.yml
[18:11:37] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:11:37] 状态: Named Tunnel (cert 模式) 已配置
SSL: 跳过
[18:11:38] === STEP 6: 启动 Tunnel ===
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) since Wed 2026-08-05 18:11:40 CST; 159ms ago
    Process: 1852410 ExecStart=/opt/start-tunnel.sh (code=exited, status=0/SUCCESS)
   Main PID: 1852410 (code=exited, status=0/SUCCESS)
        CPU: 1.876s
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
Time: Wed Aug  5 10:11:41 UTC 2026

=== curl test (aishield.tools) ===
error code: 1033

=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
