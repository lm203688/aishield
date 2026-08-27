=== DIAGNOSTIC ===
Time: Fri Aug 28 06:37:46 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787870266.142819, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2435814  1.1  1.8 1294676 37496 ?       Sl   06:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2435952  1.5  1.9 1294676 38904 ?       Sl   06:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-27T22:37:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-27T22:37:35Z INF Registered tunnel connection connIndex=1 connection=f0c17d65-6df4-45a6-b61e-72cdd732e9b9 event=0 ip=198.41.192.7 location=lax08 protocol=quic
2026-08-27T22:37:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-08-27T22:37:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.37
2026-08-27T22:37:37Z INF Registered tunnel connection connIndex=3 connection=7a869088-d280-499b-813d-3ff2d5792e46 event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-27T22:37:41Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.73
2026-08-27T22:37:41Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.73
2026-08-27T22:37:41Z INF +-------------------------------------------------------------------------------------+
2026-08-27T22:37:41Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-27T22:37:41Z INF +-------------------------------------------------------------------------------------+
2026-08-27T22:37:41Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-27T22:37:41Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-27T22:37:41Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-27T22:37:41Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-27T22:37:41Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-27T22:37:41Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-27T22:37:41Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-27T22:37:41Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-27T22:37:41Z INF |                                                                                     |
2026-08-27T22:37:41Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-27T22:37:41Z INF +-------------------------------------------------------------------------------------+
2026-08-27T22:37:41Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=93e49bc6-3035-4fe3-8af4-54c6891f0afc status=pass target=region1.v2.argotunnel.com
2026-08-27T22:37:41Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=93e49bc6-3035-4fe3-8af4-54c6891f0afc status=pass target=region2.v2.argotunnel.com
2026-08-27T22:37:41Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=93e49bc6-3035-4fe3-8af4-54c6891f0afc status=pass target=region1.v2.argotunnel.com
2026-08-27T22:37:41Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=93e49bc6-3035-4fe3-8af4-54c6891f0afc status=pass target=region2.v2.argotunnel.com
2026-08-27T22:37:41Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=93e49bc6-3035-4fe3-8af4-54c6891f0afc status=pass target=region1.v2.argotunnel.com
2026-08-27T22:37:41Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=93e49bc6-3035-4fe3-8af4-54c6891f0afc status=pass target=region2.v2.argotunnel.com
2026-08-27T22:37:41Z INF precheck component="Cloudflare API" details="API is reachable" run_id=93e49bc6-3035-4fe3-8af4-54c6891f0afc status=pass target=api.cloudflare.com:443
2026-08-27T22:37:41Z INF precheck complete hard_fail=false run_id=93e49bc6-3035-4fe3-8af4-54c6891f0afc suggested_protocol=quic
2026-08-27T22:37:42Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[06:37:14] Time: Fri Aug 28 06:37:14 AM CST 2026
[06:37:14] User: root (UID: 0)
[06:37:14] === STEP 1: 启动 API (端口 8450) ===
[06:37:27] API 已在运行
[06:37:27] API 状态: OK
[06:37:27] === STEP 2: 安装 cloudflared ===
[06:37:27] cloudflared 安装路径: /usr/local/bin/cloudflared
[06:37:27] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:37:27] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:37:27] === STEP 3: 检查认证方式 ===
[06:37:27] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[06:37:27] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[06:37:27] 检查现有 tunnel...
[06:37:28] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xlax07, 2xlax09, 2xsjc05, 1xsjc07, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-27T22:37:28Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[06:37:28] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:37:28] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[06:37:28] 凭证文件存在
[06:37:28] 创建 config.yml...
[06:37:28] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[06:37:28] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:37:29] DNS 路由结果: 2026-08-27T22:37:29Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[06:37:29] === STEP 5: 更新 DNS (API) ===
[06:37:29] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:37:30] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[06:37:31] 设置 SSL 模式为 Full...
SSL: 跳过
[06:37:31] === STEP 6: 启动 Tunnel ===
[06:37:34] 启动 Named Tunnel (cert 模式)...
[06:37:34] 使用 config: /root/.cloudflared/config.yml
[06:37:34] cloudflared PID: 2435814
[06:37:36] Tunnel 连接已建立!
[06:37:36] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T22:37:34Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-27T22:37:34Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-27T22:37:34Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-27T22:37:34Z INF Generated Connector ID: 79f38ed0-9253-4fac-93a7-3d0ae807a4e9
2026-08-27T22:37:34Z INF Initial protocol quic
2026-08-27T22:37:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:37:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:37:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:37:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:37:35Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-27T22:37:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-27T22:37:35Z INF Registered tunnel connection connIndex=0 connection=fffbfd11-2acd-4310-b77c-e79a76f6c1eb event=0 ip=198.41.200.13 location=sjc05 protocol=quic
2026-08-27T22:37:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-27T22:37:35Z INF Registered tunnel connection connIndex=1 connection=f0c17d65-6df4-45a6-b61e-72cdd732e9b9 event=0 ip=198.41.192.7 location=lax08 protocol=quic
2026-08-27T22:37:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[06:37:36] === STEP 7: 持久化 ===
[06:37:37] systemd 服务已配置
[06:37:37] Cron 保活已设置
[06:37:37] === STEP 8: 验证 ===
[06:37:37] --- API (localhost:8450) ---
 OK
[06:37:37] --- cloudflared 进程 ---
root     2435814  3.6  1.9 1294092 38528 ?       Sl   06:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2435952  0.0  1.3 1292740 27468 ?       Sl   06:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[06:37:37] --- aishield.tools ---
 OK
[06:37:39] --- DNS CNAME ---
[06:37:39] --- DNS A ---
104.21.81.46
172.67.188.44
[06:37:39] === 部署汇总 ===
[06:37:39] Tunnel Mode: cert
[06:37:39] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:37:39] API: http://localhost:8450
[06:37:39] 域名: https://aishield.tools
[06:37:39] cloudflared: /usr/local/bin/cloudflared
[06:37:39] PID: 2435814
[06:37:39] Config: /root/.cloudflared/config.yml
[06:37:39] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:37:39] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 06:37:37 CST; 8s ago
   Main PID: 2435946 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 20.5M
        CPU: 159ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2435946 /bin/bash /opt/start-tunnel.sh
             └─2435952 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 27 22:37:46 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787870267.190726, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
