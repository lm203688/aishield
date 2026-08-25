=== DIAGNOSTIC ===
Time: Tue Aug 25 03:33:15 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787643195.1693254, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3954240  0.1  1.8 1294676 36344 ?       Sl   10:17   0:34 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3954338  0.1  1.7 1360028 35716 ?       Sl   10:17   0:34 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-25T02:17:08Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e6ffc666-173d-4dd8-89af-e95e4d9a88d3 status=pass target=region1.v2.argotunnel.com
2026-08-25T02:17:08Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e6ffc666-173d-4dd8-89af-e95e4d9a88d3 status=pass target=region2.v2.argotunnel.com
2026-08-25T02:17:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e6ffc666-173d-4dd8-89af-e95e4d9a88d3 status=pass target=region1.v2.argotunnel.com
2026-08-25T02:17:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e6ffc666-173d-4dd8-89af-e95e4d9a88d3 status=pass target=region2.v2.argotunnel.com
2026-08-25T02:17:08Z INF precheck component="Cloudflare API" details="API is reachable" run_id=e6ffc666-173d-4dd8-89af-e95e4d9a88d3 status=pass target=api.cloudflare.com:443
2026-08-25T02:17:08Z INF precheck complete hard_fail=false run_id=e6ffc666-173d-4dd8-89af-e95e4d9a88d3 suggested_protocol=quic
2026-08-25T02:17:09Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-25T02:17:09Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-08-25T02:17:10Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-25T02:17:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
2026-08-25T02:17:30Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-08-25T02:17:30Z INF Retrying connection in up to 4s connIndex=3 event=0 ip=198.41.200.73
2026-08-25T02:17:31Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-25T02:18:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-25T02:18:02Z INF Registered tunnel connection connIndex=3 connection=a00337b1-92f9-417c-bf67-0e0dc3ed69cf event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-25T05:02:24Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.63
2026-08-25T05:02:24Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.200.63
2026-08-25T05:02:24Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.63
2026-08-25T05:02:24Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.63
2026-08-25T05:02:24Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.63
2026-08-25T05:02:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-25T05:02:26Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.43
2026-08-25T05:02:26Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.43
2026-08-25T05:02:26Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.43
2026-08-25T05:02:26Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.43
2026-08-25T05:02:26Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.200.43
2026-08-25T05:02:26Z INF Registered tunnel connection connIndex=0 connection=6a933bfb-223e-4b6e-96fc-e9d37cb13d3a event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-25T05:02:26Z WRN Connection terminated error="accept stream listener encountered a failure while serving" connIndex=3
2026-08-25T05:02:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-25T05:02:29Z INF Registered tunnel connection connIndex=3 connection=2813080d-f116-4d02-9fdc-a3323a3ee86f event=0 ip=198.41.200.43 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[10:16:52] Time: Tue Aug 25 10:16:52 AM CST 2026
[10:16:52] User: root (UID: 0)
[10:16:52] === STEP 1: 启动 API (端口 8450) ===
[10:16:54] API 已在运行
[10:16:54] API 状态: OK
[10:16:54] === STEP 2: 安装 cloudflared ===
[10:16:54] cloudflared 安装路径: /usr/local/bin/cloudflared
[10:16:54] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:16:54] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:16:54] === STEP 3: 检查认证方式 ===
[10:16:54] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[10:16:54] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[10:16:54] 检查现有 tunnel...
[10:16:55] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[10:16:55] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:16:55] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[10:16:55] 凭证文件存在
[10:16:55] 创建 config.yml...
[10:16:55] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[10:16:55] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:16:56] DNS 路由结果: 2026-08-25T02:16:56Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[10:16:56] === STEP 5: 更新 DNS (API) ===
[10:16:56] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:16:57] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[10:16:58] 设置 SSL 模式为 Full...
SSL: 跳过
[10:16:58] === STEP 6: 启动 Tunnel ===
[10:17:01] 启动 Named Tunnel (cert 模式)...
[10:17:01] 使用 config: /root/.cloudflared/config.yml
[10:17:01] cloudflared PID: 3954240
[10:17:03] Tunnel 连接已建立!
[10:17:03] --- cloudflared 日志 (最后 15 行) ---
2026-08-25T02:17:02Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-25T02:17:02Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-25T02:17:02Z INF Generated Connector ID: f0052ab3-f056-492d-8008-e3fd563f4cf2
2026-08-25T02:17:02Z INF Initial protocol quic
2026-08-25T02:17:02Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-25T02:17:02Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-25T02:17:02Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-25T02:17:02Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-25T02:17:02Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-25T02:17:02Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-25T02:17:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-25T02:17:02Z INF Registered tunnel connection connIndex=0 connection=0e06142e-78e5-492c-b1cf-48ad9953ffb3 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-25T02:17:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-25T02:17:02Z INF Registered tunnel connection connIndex=1 connection=faad0115-a68f-4edd-9e5b-8e2fbfe9f409 event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-08-25T02:17:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
[10:17:04] === STEP 7: 持久化 ===
[10:17:04] systemd 服务已配置
[10:17:04] Cron 保活已设置
[10:17:04] === STEP 8: 验证 ===
[10:17:04] --- API (localhost:8450) ---
 OK
[10:17:04] --- cloudflared 进程 ---
root     3954240  4.0  1.9 1294420 39644 ?       Sl   10:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3954338  0.0  1.3 1292484 27424 ?       Rl   10:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[10:17:04] --- aishield.tools ---
 OK
[10:17:06] --- DNS CNAME ---
[10:17:06] --- DNS A ---
172.67.188.44
104.21.81.46
[10:17:06] === 部署汇总 ===
[10:17:06] Tunnel Mode: cert
[10:17:06] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:17:06] API: http://localhost:8450
[10:17:06] 域名: https://aishield.tools
[10:17:06] cloudflared: /usr/local/bin/cloudflared
[10:17:06] PID: 3954240
[10:17:06] Config: /root/.cloudflared/config.yml
[10:17:06] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:17:06] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-25 10:17:04 CST; 5h 16min ago
   Main PID: 3954332 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 18.1M
        CPU: 34.692s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3954332 /bin/bash /opt/start-tunnel.sh
             └─3954338 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2525069,fd=3))                                                    
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
Time: Tue Aug 25 07:33:15 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787643195.7509022, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
