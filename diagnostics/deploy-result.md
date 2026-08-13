=== DIAGNOSTIC ===
Time: Thu Aug 13 04:11:11 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786608671.5591402, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1278366  0.1  1.7 1294676 34236 ?       Sl   16:00   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1278486  0.1  1.6 1360284 33496 ?       Sl   16:00   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-13T08:00:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-13T08:00:31Z INF Registered tunnel connection connIndex=0 connection=26c0d854-3293-4e28-8b49-4270234d8221 event=0 ip=198.41.192.27 location=lax07 protocol=quic
2026-08-13T08:00:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-08-13T08:00:32Z INF Registered tunnel connection connIndex=1 connection=8791ad14-80f4-48aa-aa9f-682a12ad7431 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-13T08:00:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-13T08:00:33Z INF Registered tunnel connection connIndex=2 connection=e7d9acf7-9ee9-4582-aa63-93ec4a7fe41e event=0 ip=198.41.192.167 location=lax07 protocol=quic
2026-08-13T08:00:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.33
2026-08-13T08:00:34Z INF Registered tunnel connection connIndex=3 connection=e9dc625d-c624-4a47-a416-bd17f583ae61 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-13T08:00:39Z INF +-------------------------------------------------------------------------------------+
2026-08-13T08:00:39Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-13T08:00:39Z INF +-------------------------------------------------------------------------------------+
2026-08-13T08:00:39Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-13T08:00:39Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-13T08:00:39Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-13T08:00:39Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-13T08:00:39Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-13T08:00:39Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-13T08:00:39Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-13T08:00:39Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-13T08:00:39Z INF |                                                                                     |
2026-08-13T08:00:39Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-13T08:00:39Z INF +-------------------------------------------------------------------------------------+
2026-08-13T08:00:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=42a86517-0098-4fe0-9b85-7901e954dcf3 status=pass target=region1.v2.argotunnel.com
2026-08-13T08:00:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=42a86517-0098-4fe0-9b85-7901e954dcf3 status=pass target=region2.v2.argotunnel.com
2026-08-13T08:00:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=42a86517-0098-4fe0-9b85-7901e954dcf3 status=pass target=region1.v2.argotunnel.com
2026-08-13T08:00:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=42a86517-0098-4fe0-9b85-7901e954dcf3 status=pass target=region2.v2.argotunnel.com
2026-08-13T08:00:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=42a86517-0098-4fe0-9b85-7901e954dcf3 status=pass target=region1.v2.argotunnel.com
2026-08-13T08:00:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=42a86517-0098-4fe0-9b85-7901e954dcf3 status=pass target=region2.v2.argotunnel.com
2026-08-13T08:00:39Z INF precheck component="Cloudflare API" details="API is reachable" run_id=42a86517-0098-4fe0-9b85-7901e954dcf3 status=pass target=api.cloudflare.com:443
2026-08-13T08:00:39Z INF precheck complete hard_fail=false run_id=42a86517-0098-4fe0-9b85-7901e954dcf3 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:11:03] Time: Thu Aug 13 04:11:03 PM CST 2026
[16:11:03] User: root (UID: 0)
[16:11:03] === STEP 1: 启动 API (端口 8450) ===
[16:11:05] API 已在运行
[16:11:05] API 状态: OK
[16:11:05] === STEP 2: 安装 cloudflared ===
[16:11:05] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:11:05] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:11:05] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:11:05] === STEP 3: 检查认证方式 ===
[16:11:05] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:11:05] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:11:05] 检查现有 tunnel...
[16:11:06] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax07, 1xlax08, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[16:11:06] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:11:06] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:11:06] 凭证文件存在
[16:11:06] 创建 config.yml...
[16:11:06] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:11:06] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:11:10] DNS 路由结果: 2026-08-13T08:11:10Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:11:10] === STEP 5: 更新 DNS (API) ===
[16:11:10] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:11:11] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-13 16:00:33 CST; 10min ago
   Main PID: 1278485 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.0M
        CPU: 1.241s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1278485 /bin/bash /opt/start-tunnel.sh
             └─1278486 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2772386,fd=3))                                                    
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
Time: Thu Aug 13 08:11:11 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786608672.0391848, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
