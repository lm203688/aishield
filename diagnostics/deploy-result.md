=== DIAGNOSTIC ===
Time: Wed Aug 5 12:37:00 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785904620.3123543, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1591062  0.1  1.8 1294676 37272 ?       Sl   12:26   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1591166  0.1  1.8 1294676 38108 ?       Sl   12:27   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1599466  6.0  1.7 1293844 35020 ?       Sl   12:36   0:00 /usr/local/bin/cloudflared tunnel list
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-05T04:27:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
2026-08-05T04:27:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.77
2026-08-05T04:27:02Z INF Registered tunnel connection connIndex=3 connection=ac90b4ad-20c8-4662-b5e8-fa9fb9ae7e19 event=0 ip=198.41.192.77 location=lax11 protocol=quic
2026-08-05T04:27:05Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.193
2026-08-05T04:27:05Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.193
2026-08-05T04:27:05Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-05T04:27:05Z INF +-------------------------------------------------------------------------------------+
2026-08-05T04:27:05Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-05T04:27:05Z INF +-------------------------------------------------------------------------------------+
2026-08-05T04:27:05Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-05T04:27:05Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-05T04:27:05Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-05T04:27:05Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-05T04:27:05Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-05T04:27:05Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-05T04:27:05Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-05T04:27:05Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-05T04:27:05Z INF |                                                                                     |
2026-08-05T04:27:05Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-05T04:27:05Z INF +-------------------------------------------------------------------------------------+
2026-08-05T04:27:05Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8647ca77-4ceb-4024-b683-952e26d21f58 status=pass target=region1.v2.argotunnel.com
2026-08-05T04:27:05Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8647ca77-4ceb-4024-b683-952e26d21f58 status=pass target=region2.v2.argotunnel.com
2026-08-05T04:27:05Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8647ca77-4ceb-4024-b683-952e26d21f58 status=pass target=region1.v2.argotunnel.com
2026-08-05T04:27:05Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8647ca77-4ceb-4024-b683-952e26d21f58 status=pass target=region2.v2.argotunnel.com
2026-08-05T04:27:05Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8647ca77-4ceb-4024-b683-952e26d21f58 status=pass target=region1.v2.argotunnel.com
2026-08-05T04:27:05Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8647ca77-4ceb-4024-b683-952e26d21f58 status=pass target=region2.v2.argotunnel.com
2026-08-05T04:27:05Z INF precheck component="Cloudflare API" details="API is reachable" run_id=8647ca77-4ceb-4024-b683-952e26d21f58 status=pass target=api.cloudflare.com:443
2026-08-05T04:27:05Z INF precheck complete hard_fail=false run_id=8647ca77-4ceb-4024-b683-952e26d21f58 suggested_protocol=quic
2026-08-05T04:27:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-05T04:27:12Z INF Registered tunnel connection connIndex=2 connection=455998a9-1e55-4e3a-9f24-4ded8cf7d63f event=0 ip=198.41.200.113 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:36:59] Time: Wed Aug  5 12:36:59 PM CST 2026
[12:36:59] User: root (UID: 0)
[12:36:59] === STEP 1: 启动 API (端口 8450) ===
[12:37:00] DNS 路由结果: 2026-08-05T04:37:00Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:37:00] === STEP 5: 更新 DNS (API) ===
[12:37:00] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 12:27:00 CST; 9min ago
   Main PID: 1591158 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 15.7M
        CPU: 1.106s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1591158 /bin/bash /opt/start-tunnel.sh
             └─1591166 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug  5 04:37:00 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785904620.852078, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
