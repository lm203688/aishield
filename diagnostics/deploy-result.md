=== DIAGNOSTIC ===
Time: Wed Aug 5 11:26:09 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785900369.9344385, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1537596  0.9  1.9 1360284 38960 ?       Sl   11:25   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1537760  1.1  1.9 1294740 39852 ?       Sl   11:25   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-05T03:25:59Z INF Registered tunnel connection connIndex=1 connection=014b0f5e-23fd-4c26-839c-e477c2b4915b event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-05T03:25:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-08-05T03:26:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.27
2026-08-05T03:26:01Z INF Registered tunnel connection connIndex=3 connection=b860ae32-55a0-4452-b4d3-f5321b934f85 event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-08-05T03:26:04Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.73
2026-08-05T03:26:04Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.73
2026-08-05T03:26:06Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-05T03:26:07Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T03:26:07Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-05T03:26:07Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T03:26:07Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-05T03:26:07Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-05T03:26:07Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-05T03:26:07Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-05T03:26:07Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-05T03:26:07Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-05T03:26:07Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-05T03:26:07Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-05T03:26:07Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-05T03:26:07Z INF |                                                                                               |
2026-08-05T03:26:07Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-05T03:26:07Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T03:26:07Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8bdc4659-b4e3-4525-bcfe-4640ed547114 status=pass target=region1.v2.argotunnel.com
2026-08-05T03:26:07Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8bdc4659-b4e3-4525-bcfe-4640ed547114 status=pass target=region2.v2.argotunnel.com
2026-08-05T03:26:07Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8bdc4659-b4e3-4525-bcfe-4640ed547114 status=pass target=region1.v2.argotunnel.com
2026-08-05T03:26:07Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=8bdc4659-b4e3-4525-bcfe-4640ed547114 status=fail target=region2.v2.argotunnel.com
2026-08-05T03:26:07Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8bdc4659-b4e3-4525-bcfe-4640ed547114 status=pass target=region1.v2.argotunnel.com
2026-08-05T03:26:07Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8bdc4659-b4e3-4525-bcfe-4640ed547114 status=pass target=region2.v2.argotunnel.com
2026-08-05T03:26:07Z INF precheck component="Cloudflare API" details="API is reachable" run_id=8bdc4659-b4e3-4525-bcfe-4640ed547114 status=pass target=api.cloudflare.com:443
2026-08-05T03:26:07Z INF precheck complete hard_fail=false run_id=8bdc4659-b4e3-4525-bcfe-4640ed547114 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[11:23:30] Time: Wed Aug  5 11:23:30 AM CST 2026
[11:23:30] User: root (UID: 0)
[11:23:30] === STEP 1: 启动 API (端口 8450) ===
DNS 更新: OK
[11:23:33] 设置 SSL 模式为 Full...
SSL: 跳过
[11:23:35] === STEP 6: 启动 Tunnel ===
[11:23:38] 启动 Named Tunnel (cert 模式)...
[11:23:38] 使用 config: /root/.cloudflared/config.yml
[11:23:38] cloudflared PID: 1535400
[11:23:46] Tunnel 连接已建立!
[11:23:46] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T03:23:38Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-05T03:23:38Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T03:23:38Z INF Generated Connector ID: 84fcb824-9c73-43d6-8680-473c089bbe00
2026-08-05T03:23:38Z INF Initial protocol quic
2026-08-05T03:23:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T03:23:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T03:23:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T03:23:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T03:23:38Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-05T03:23:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.73
2026-08-05T03:23:43Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.73
2026-08-05T03:23:43Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.73
2026-08-05T03:23:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-05T03:23:45Z INF Registered tunnel connection connIndex=0 connection=d2a65e0e-4c40-45fd-a738-6f527236388c event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-05T03:23:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
[11:23:46] === STEP 7: 持久化 ===
[11:23:47] systemd 服务已配置
[11:23:47] Cron 保活已设置
[11:23:47] === STEP 8: 验证 ===
[11:23:47] --- API (localhost:8450) ---
 OK
[11:23:47] --- cloudflared 进程 ---
root     1535400  1.2  1.9 1294676 39448 ?       Sl   11:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1535596  0.0  1.4 1292740 28736 ?       Sl   11:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[11:23:47] --- aishield.tools ---
 OK
[11:23:49] --- DNS CNAME ---
[11:23:49] --- DNS A ---
104.21.81.46
172.67.188.44
[11:23:49] === 部署汇总 ===
[11:23:49] Tunnel Mode: cert
[11:23:49] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:23:49] API: http://localhost:8450
[11:23:49] 域名: https://aishield.tools
[11:23:49] cloudflared: /usr/local/bin/cloudflared
[11:23:49] PID: 1535400
[11:23:49] Config: /root/.cloudflared/config.yml
[11:23:49] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:23:49] 状态: Named Tunnel (cert 模式) 已配置
[11:25:41] API 已在运行
[11:25:41] API 状态: OK
[11:25:41] === STEP 2: 安装 cloudflared ===
[11:25:41] cloudflared 安装路径: /usr/local/bin/cloudflared
[11:25:41] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:25:41] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:25:41] === STEP 3: 检查认证方式 ===
[11:25:41] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[11:25:41] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[11:25:41] 检查现有 tunnel...
[11:25:44] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax10, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[11:25:44] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:25:44] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[11:25:44] 凭证文件存在
[11:25:44] 创建 config.yml...
[11:25:44] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[11:25:44] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:25:46] DNS 路由结果: 2026-08-05T03:25:46Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[11:25:46] === STEP 5: 更新 DNS (API) ===
[11:25:46] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:25:49] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[11:25:51] 设置 SSL 模式为 Full...
SSL: 跳过
[11:25:54] === STEP 6: 启动 Tunnel ===
[11:25:57] 启动 Named Tunnel (cert 模式)...
[11:25:57] 使用 config: /root/.cloudflared/config.yml
[11:25:57] cloudflared PID: 1537596
[11:25:59] Tunnel 连接已建立!
[11:25:59] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T03:25:57Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-05T03:25:57Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-05T03:25:57Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T03:25:57Z INF Generated Connector ID: c281a3c0-fa92-465e-9d9b-530724e439ee
2026-08-05T03:25:57Z INF Initial protocol quic
2026-08-05T03:25:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T03:25:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T03:25:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T03:25:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T03:25:57Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-05T03:25:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-05T03:25:58Z INF Registered tunnel connection connIndex=0 connection=2bb6441a-a06f-433a-93b4-7703f521e1a5 event=0 ip=198.41.192.227 location=lax10 protocol=quic
2026-08-05T03:25:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-05T03:25:59Z INF Registered tunnel connection connIndex=1 connection=014b0f5e-23fd-4c26-839c-e477c2b4915b event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-05T03:25:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[11:25:59] === STEP 7: 持久化 ===
[11:26:00] systemd 服务已配置
[11:26:00] Cron 保活已设置
[11:26:00] === STEP 8: 验证 ===
[11:26:00] --- API (localhost:8450) ---
 OK
[11:26:00] --- cloudflared 进程 ---
root     1537596  3.0  1.9 1360028 38516 ?       Sl   11:25   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1537760  0.0  1.3 1292740 27592 ?       Sl   11:25   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[11:26:00] --- aishield.tools ---
 OK
[11:26:01] --- DNS CNAME ---
[11:26:02] --- DNS A ---
172.67.188.44
104.21.81.46
[11:26:02] === 部署汇总 ===
[11:26:02] Tunnel Mode: cert
[11:26:02] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:26:02] API: http://localhost:8450
[11:26:02] 域名: https://aishield.tools
[11:26:02] cloudflared: /usr/local/bin/cloudflared
[11:26:02] PID: 1537596
[11:26:02] Config: /root/.cloudflared/config.yml
[11:26:02] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:26:02] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 11:26:00 CST; 9s ago
   Main PID: 1537756 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.1M
        CPU: 120ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1537756 /bin/bash /opt/start-tunnel.sh
             └─1537760 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                 
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
Time: Wed Aug  5 03:26:10 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785900370.6361432, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
