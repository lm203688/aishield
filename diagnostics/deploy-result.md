=== DIAGNOSTIC ===
Time: Sat Aug 15 08:26:45 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786753605.9174905, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2867438  0.1  1.6 1294420 33744 ?       Sl   08:22   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2867658  0.1  1.6 1294676 34084 ?       Sl   08:22   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-15T00:22:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-15T00:22:07Z INF Registered tunnel connection connIndex=0 connection=9a2df466-868c-4bad-aa01-97bb98ae8e1d event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-15T00:22:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-08-15T00:22:07Z INF Registered tunnel connection connIndex=1 connection=8ae202b7-082e-4054-b4e8-7e19b535157a event=0 ip=198.41.192.57 location=lax05 protocol=quic
2026-08-15T00:22:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-15T00:22:08Z INF Registered tunnel connection connIndex=2 connection=05415d2f-7341-48cb-bee3-ce981d012b89 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-15T00:22:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-15T00:22:09Z INF Registered tunnel connection connIndex=3 connection=9680a975-2707-4ccb-a4d7-3c17d19e86f7 event=0 ip=198.41.192.47 location=lax07 protocol=quic
2026-08-15T00:22:13Z INF +-------------------------------------------------------------------------------------+
2026-08-15T00:22:13Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-15T00:22:13Z INF +-------------------------------------------------------------------------------------+
2026-08-15T00:22:13Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-15T00:22:13Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-15T00:22:13Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-15T00:22:13Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-15T00:22:13Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-15T00:22:13Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-15T00:22:13Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-15T00:22:13Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-15T00:22:13Z INF |                                                                                     |
2026-08-15T00:22:13Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-15T00:22:13Z INF +-------------------------------------------------------------------------------------+
2026-08-15T00:22:13Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=2b4a19c7-6893-4edd-b702-771c8a72f88d status=pass target=region1.v2.argotunnel.com
2026-08-15T00:22:13Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=2b4a19c7-6893-4edd-b702-771c8a72f88d status=pass target=region2.v2.argotunnel.com
2026-08-15T00:22:13Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=2b4a19c7-6893-4edd-b702-771c8a72f88d status=pass target=region1.v2.argotunnel.com
2026-08-15T00:22:13Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=2b4a19c7-6893-4edd-b702-771c8a72f88d status=pass target=region2.v2.argotunnel.com
2026-08-15T00:22:13Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=2b4a19c7-6893-4edd-b702-771c8a72f88d status=pass target=region1.v2.argotunnel.com
2026-08-15T00:22:13Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=2b4a19c7-6893-4edd-b702-771c8a72f88d status=pass target=region2.v2.argotunnel.com
2026-08-15T00:22:13Z INF precheck component="Cloudflare API" details="API is reachable" run_id=2b4a19c7-6893-4edd-b702-771c8a72f88d status=pass target=api.cloudflare.com:443
2026-08-15T00:22:13Z INF precheck complete hard_fail=false run_id=2b4a19c7-6893-4edd-b702-771c8a72f88d suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:21:58] Time: Sat Aug 15 08:21:58 AM CST 2026
[08:21:58] --- DNS A ---
[08:21:58] User: root (UID: 0)
[08:21:58] === STEP 1: 启动 API (端口 8450) ===
104.21.81.46
172.67.188.44
[08:21:58] === 部署汇总 ===
[08:21:58] Tunnel Mode: cert
[08:21:58] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:21:58] API: http://localhost:8450
[08:21:58] 域名: https://aishield.tools
[08:21:58] cloudflared: /usr/local/bin/cloudflared
[08:21:58] PID: 2866584
[08:21:58] Config: /root/.cloudflared/config.yml
[08:21:58] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:21:58] 状态: Named Tunnel (cert 模式) 已配置
[08:21:59] 启动 Named Tunnel (cert 模式)...
[08:21:59] 使用 config: /root/.cloudflared/config.yml
[08:21:59] cloudflared PID: 2866910
[08:21:59] API 已在运行
[08:21:59] API 状态: OK
[08:21:59] === STEP 2: 安装 cloudflared ===
[08:21:59] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:22:00] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:22:00] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:22:00] === STEP 3: 检查认证方式 ===
[08:22:00] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:22:00] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:22:00] 检查现有 tunnel...
[08:22:00] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xlax01, 1xlax10, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[08:22:00] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:22:00] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:22:00] 凭证文件存在
[08:22:00] 创建 config.yml...
[08:22:00] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:22:00] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:22:01] Tunnel 连接已建立!
[08:22:01] --- cloudflared 日志 (最后 15 行) ---
2026-08-15T00:21:59Z INF Generated Connector ID: efb40445-d483-4aed-8252-8086251b4039
2026-08-15T00:21:59Z INF Initial protocol quic
2026-08-15T00:21:59Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T00:21:59Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T00:21:59Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T00:21:59Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T00:21:59Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-15T00:21:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-15T00:21:59Z INF Registered tunnel connection connIndex=0 connection=c1e2c02f-f011-4428-ba2e-e8654341b7a2 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-15T00:21:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-15T00:22:00Z INF Registered tunnel connection connIndex=1 connection=90a48f99-e35c-4bb4-937e-ab84c1cb7397 event=0 ip=198.41.192.7 location=lax11 protocol=quic
2026-08-15T00:22:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      2026-08-15T00:22:01Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.73
2026-08-15T00:22:01Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.73
2026-08-15T00:22:01Z ERR Connection terminated connIndex=1
[08:22:01] === STEP 7: 持久化 ===
[08:22:01] DNS 路由结果: 2026-08-15T00:22:01Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:22:01] === STEP 5: 更新 DNS (API) ===
[08:22:01] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:22:02] systemd 服务已配置
[08:22:02] Cron 保活已设置
[08:22:02] === STEP 8: 验证 ===
[08:22:02] --- API (localhost:8450) ---
 OK
[08:22:02] --- cloudflared 进程 ---
root     2866910  3.6  1.9 1294420 38488 ?       Sl   08:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2867203  0.0  1.3 1292484 27368 ?       Sl   08:22   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:22:02] --- aishield.tools ---
[08:22:02] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:22:03] 设置 SSL 模式为 Full...
 OK
[08:22:03] --- DNS CNAME ---
[08:22:03] --- DNS A ---
104.21.81.46
172.67.188.44
[08:22:03] === 部署汇总 ===
[08:22:03] Tunnel Mode: cert
[08:22:03] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:22:03] API: http://localhost:8450
[08:22:03] 域名: https://aishield.tools
[08:22:03] cloudflared: /usr/local/bin/cloudflared
[08:22:03] PID: 2866910
[08:22:03] Config: /root/.cloudflared/config.yml
[08:22:03] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:22:03] 状态: Named Tunnel (cert 模式) 已配置
SSL: 跳过
[08:22:04] === STEP 6: 启动 Tunnel ===
[08:22:07] 启动 Named Tunnel (cert 模式)...
[08:22:07] 使用 config: /root/.cloudflared/config.yml
[08:22:07] cloudflared PID: 2867438
[08:22:09] Tunnel 连接已建立!
[08:22:09] --- cloudflared 日志 (最后 15 行) ---
2026-08-15T00:22:07Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-15T00:22:07Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-15T00:22:07Z INF Generated Connector ID: 69d994a6-d5bc-484d-a3c0-473be645a084
2026-08-15T00:22:07Z INF Initial protocol quic
2026-08-15T00:22:07Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T00:22:07Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T00:22:07Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T00:22:07Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T00:22:07Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-15T00:22:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-15T00:22:07Z INF Registered tunnel connection connIndex=0 connection=9a2df466-868c-4bad-aa01-97bb98ae8e1d event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-15T00:22:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-08-15T00:22:07Z INF Registered tunnel connection connIndex=1 connection=8ae202b7-082e-4054-b4e8-7e19b535157a event=0 ip=198.41.192.57 location=lax05 protocol=quic
2026-08-15T00:22:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-15T00:22:08Z INF Registered tunnel connection connIndex=2 connection=05415d2f-7341-48cb-bee3-ce981d012b89 event=0 ip=198.41.200.23 location=lax01 protocol=quic
[08:22:09] === STEP 7: 持久化 ===
[08:22:09] systemd 服务已配置
[08:22:09] Cron 保活已设置
[08:22:09] === STEP 8: 验证 ===
[08:22:09] --- API (localhost:8450) ---
 OK
[08:22:09] --- cloudflared 进程 ---
root     2867438  5.0  1.9 1294420 38704 ?       Sl   08:22   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2867658  0.0  1.4 1292740 28292 ?       Sl   08:22   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:22:09] --- aishield.tools ---
 OK
[08:22:11] --- DNS CNAME ---
[08:22:11] --- DNS A ---
104.21.81.46
172.67.188.44
[08:22:11] === 部署汇总 ===
[08:22:11] Tunnel Mode: cert
[08:22:11] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:22:11] API: http://localhost:8450
[08:22:11] 域名: https://aishield.tools
[08:22:11] cloudflared: /usr/local/bin/cloudflared
[08:22:11] PID: 2867438
[08:22:11] Config: /root/.cloudflared/config.yml
[08:22:11] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:22:11] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-15 08:22:09 CST; 4min 36s ago
   Main PID: 2867655 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 17.0M
        CPU: 539ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2867655 /bin/bash /opt/start-tunnel.sh
             └─2867658 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sat Aug 15 00:26:46 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786753606.3591857, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
