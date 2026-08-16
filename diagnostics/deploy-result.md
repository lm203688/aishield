=== DIAGNOSTIC ===
Time: Sun Aug 16 10:57:09 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786849029.8599548, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3908423  1.0  1.9 1294420 39420 ?       Sl   10:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3908522  1.3  1.9 1294420 39544 ?       Sl   10:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3908775  2.0  1.9 1294676 39412 ?       Sl   10:57   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-16T02:57:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-16T02:57:01Z INF Registered tunnel connection connIndex=1 connection=14a58dbc-5f96-4b48-b312-6515ced4fc77 event=0 ip=198.41.192.47 location=lax05 protocol=quic
2026-08-16T02:57:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-16T02:57:02Z INF Registered tunnel connection connIndex=2 connection=eccc271c-6f25-4d9d-a7d7-0d91ab2a030f event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-16T02:57:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.7
2026-08-16T02:57:05Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.22026-08-16T02:57:07Z INF +-------------------------------------------------------------------------------------+
2026-08-16T02:57:07Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-16T022026-08-16T02:57:08Z INF +-----------------------------------------------------------------------------------------------+
2026-08-16T02:57:08Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-16T02:57:08Z INF +-----------------------------------------------------------------------------------------------+
2026-08-16T02:57:08Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-16T02:57:08Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-16T02:57:08Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-16T02:57:08Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-16T02:57:08Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-16T02:57:08Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-16T02:57:08Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-16T02:57:08Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-16T02:57:08Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-16T02:57:08Z INF |                                                                                               |
2026-08-16T02:57:08Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-16T02:57:08Z INF +-----------------------------------------------------------------------------------------------+
2026-08-16T02:57:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ca369301-938f-473d-8178-b8ff97c9ee9a status=pass target=region1.v2.argotunnel.com
2026-08-16T02:57:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ca369301-938f-473d-8178-b8ff97c9ee9a status=pass target=region2.v2.argotunnel.com
2026-08-16T02:57:08Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ca369301-938f-473d-8178-b8ff97c9ee9a status=pass target=region1.v2.argotunnel.com
2026-08-16T02:57:08Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=ca369301-938f-473d-8178-b8ff97c9ee9a status=fail target=region2.v2.argotunnel.com
2026-08-16T02:57:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ca369301-938f-473d-8178-b8ff97c9ee9a status=pass target=region1.v2.argotunnel.com
2026-08-16T02:57:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ca369301-938f-473d-8178-b8ff97c9ee9a status=pass target=region2.v2.argotunnel.com
2026-08-16T02:57:08Z INF precheck component="Cloudflare API" details="API is reachable" run_id=ca369301-938f-473d-8178-b8ff97c9ee9a status=pass target=api.cloudflare.com:443
2026-08-16T02:57:08Z INF precheck complete hard_fail=false run_id=ca369301-938f-473d-8178-b8ff97c9ee9a suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[10:56:52] Time: Sun Aug 16 10:56:52 AM CST 2026
[10:56:52] User: root (UID: 0)
[10:56:52] === STEP 1: 启动 API (端口 8450) ===
[10:56:53] DNS 路由结果: 2026-08-16T02:56:53Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[10:56:53] === STEP 5: 更新 DNS (API) ===
[10:56:53] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:56:53] API 已在运行
[10:56:53] API 状态: OK
[10:56:53] === STEP 2: 安装 cloudflared ===
[10:56:53] cloudflared 安装路径: /usr/local/bin/cloudflared
[10:56:53] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:56:53] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:56:53] === STEP 3: 检查认证方式 ===
[10:56:53] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[10:56:53] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[10:56:53] 检查现有 tunnel...
[10:56:54] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[10:56:54] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax07, 1xlax08, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-16T02:56:54Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[10:56:54] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:56:54] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[10:56:54] 凭证文件存在
[10:56:54] 创建 config.yml...
[10:56:54] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[10:56:54] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[10:56:54] 设置 SSL 模式为 Full...
SSL: 跳过
[10:56:55] === STEP 6: 启动 Tunnel ===
[10:56:55] DNS 路由结果: 
[10:56:55] === STEP 5: 更新 DNS (API) ===
[10:56:55] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:56:56] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[10:56:57] 设置 SSL 模式为 Full...
SSL: 跳过
[10:56:57] === STEP 6: 启动 Tunnel ===
[10:56:58] 启动 Named Tunnel (cert 模式)...
[10:56:58] 使用 config: /root/.cloudflared/config.yml
[10:56:58] cloudflared PID: 3908423
[10:57:00] Tunnel 连接已建立!
[10:57:00] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T02:56:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-16T02:56:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-16T02:56:58Z INF Generated Connector ID: 9505a26c-eca6-44a3-82c2-4e2a662736cf
2026-08-16T02:56:58Z INF Initial protocol quic
2026-08-16T02:56:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T02:56:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T02:56:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T02:56:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T02:56:58Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-16T02:56:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-16T02:56:58Z INF Registered tunnel connection connIndex=0 connection=5d13d3ba-565d-44dc-8a6c-f1f4ddb4d3e5 event=0 ip=198.41.192.27 location=lax11 protocol=quic
2026-08-16T02:56:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-16T02:56:59Z INF Registered tunnel connection connIndex=1 connection=164b44db-bb32-4271-a9c6-a264bea49683 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-16T02:56:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-08-16T02:57:00Z INF Registered tunnel connection connIndex=2 connection=cadbcb4b-1249-4e77-8797-f3d43f63de28 event=0 ip=198.41.192.7 location=lax07 protocol=quic
[10:57:00] === STEP 7: 持久化 ===
[10:57:00] 启动 Named Tunnel (cert 模式)...
[10:57:00] 使用 config: /root/.cloudflared/config.yml
[10:57:00] cloudflared PID: 3908522
[10:57:01] systemd 服务已配置
[10:57:01] Cron 保活已设置
[10:57:01] === STEP 8: 验证 ===
[10:57:01] --- API (localhost:8450) ---
 OK
[10:57:01] --- cloudflared 进程 ---
root     3908423  3.3  1.9 1294420 39256 ?       Sl   10:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3908522  8.0  1.8 1294100 37416 ?       Sl   10:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3908544  0.0  1.3 1292484 27268 ?       Sl   10:57   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[10:57:01] --- aishield.tools ---
[10:57:02] Tunnel 连接已建立!
[10:57:02] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T02:57:00Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-16T02:57:00Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-16T02:57:00Z INF Generated Connector ID: cabcf289-c67e-47fd-a7d6-ebb6fce59ef9
2026-08-16T02:57:00Z INF Initial protocol quic
2026-08-16T02:57:00Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T02:57:00Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T02:57:00Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T02:57:00Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T02:57:00Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-16T02:57:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-08-16T02:57:01Z INF Registered tunnel connection connIndex=0 connection=c13b301b-371d-490f-b913-52fba94ca230 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-16T02:57:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-16T02:57:01Z INF Registered tunnel connection connIndex=1 connection=14a58dbc-5f96-4b48-b312-6515ced4fc77 event=0 ip=198.41.192.47 location=lax05 protocol=quic
2026-08-16T02:57:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-16T02:57:02Z INF Registered tunnel connection connIndex=2 connection=eccc271c-6f25-4d9d-a7d7-0d91ab2a030f event=0 ip=198.41.200.113 location=lax01 protocol=quic
[10:57:02] === STEP 7: 持久化 ===
 OK
[10:57:02] --- DNS CNAME ---
[10:57:03] --- DNS A ---
104.21.81.46
172.67.188.44
[10:57:03] === 部署汇总 ===
[10:57:03] Tunnel Mode: cert
[10:57:03] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:57:03] API: http://localhost:8450
[10:57:03] 域名: https://aishield.tools
[10:57:03] cloudflared: /usr/local/bin/cloudflared
[10:57:03] PID: 3908423
[10:57:03] Config: /root/.cloudflared/config.yml
[10:57:03] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:57:03] 状态: Named Tunnel (cert 模式) 已配置
[10:57:03] systemd 服务已配置
[10:57:03] Cron 保活已设置
[10:57:03] === STEP 8: 验证 ===
[10:57:03] --- API (localhost:8450) ---
 OK
[10:57:03] --- cloudflared 进程 ---
root     3908423  2.0  1.9 1294420 39544 ?       Sl   10:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3908522  3.3  1.9 1294100 38512 ?       Sl   10:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3908775  0.0  1.3 1292740 27160 ?       Rl   10:57   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[10:57:03] --- aishield.tools ---
 OK
[10:57:05] --- DNS CNAME ---
[10:57:05] --- DNS A ---
104.21.81.46
172.67.188.44
[10:57:05] === 部署汇总 ===
[10:57:05] Tunnel Mode: cert
[10:57:05] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:57:05] API: http://localhost:8450
[10:57:05] 域名: https://aishield.tools
[10:57:05] cloudflared: /usr/local/bin/cloudflared
[10:57:05] PID: 3908522
[10:57:05] Config: /root/.cloudflared/config.yml
[10:57:05] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:57:05] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-16 10:57:03 CST; 6s ago
   Main PID: 3908768 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.3M
        CPU: 127ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3908768 /bin/bash /opt/start-tunnel.sh
             └─3908775 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2342254,fd=3))                                                    
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
Time: Sun Aug 16 02:57:10 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786849030.4197376, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
