=== DIAGNOSTIC ===
Time: Fri Aug 14 07:33:49 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786707229.677801, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2342686  0.1  1.7 1294676 35656 ?       Sl   19:08   0:02 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2342822  0.1  1.7 1294676 35776 ?       Sl   19:08   0:02 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T11:08:34Z INF Registered tunnel connection connIndex=0 connection=c2ea9322-f795-4b60-a45e-beef5a150ef3 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-14T11:08:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-14T11:08:34Z INF Registered tunnel connection connIndex=1 connection=ae738cb6-d50f-4185-b15d-e3ff1615ff49 event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-14T11:08:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
2026-08-14T11:08:35Z INF Registered tunnel connection connIndex=2 connection=ae151c6c-2994-4b22-bdbf-2da404db26a6 event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-08-14T11:08:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-08-14T11:08:37Z INF Registered tunnel connection connIndex=3 connection=79eba7fe-e72b-41be-9be6-ee49c3381951 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-14T11:08:43Z INF +-----------------------------------------------------------------------------------------------+
2026-08-14T11:08:43Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-14T11:08:43Z INF +-----------------------------------------------------------------------------------------------+
2026-08-14T11:08:43Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-14T11:08:43Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-14T11:08:43Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-14T11:08:43Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-14T11:08:43Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-14T11:08:43Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-14T11:08:43Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-14T11:08:43Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-14T11:08:43Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-14T11:08:43Z INF |                                                                                               |
2026-08-14T11:08:43Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-14T11:08:43Z INF +-----------------------------------------------------------------------------------------------+
2026-08-14T11:08:43Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=32d34c8b-881a-4952-8c3c-abb9632e85de status=pass target=region1.v2.argotunnel.com
2026-08-14T11:08:43Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=32d34c8b-881a-4952-8c3c-abb9632e85de status=pass target=region2.v2.argotunnel.com
2026-08-14T11:08:43Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=32d34c8b-881a-4952-8c3c-abb9632e85de status=pass target=region1.v2.argotunnel.com
2026-08-14T11:08:43Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=32d34c8b-881a-4952-8c3c-abb9632e85de status=fail target=region2.v2.argotunnel.com
2026-08-14T11:08:43Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=32d34c8b-881a-4952-8c3c-abb9632e85de status=pass target=region1.v2.argotunnel.com
2026-08-14T11:08:43Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=32d34c8b-881a-4952-8c3c-abb9632e85de status=pass target=region2.v2.argotunnel.com
2026-08-14T11:08:43Z INF precheck component="Cloudflare API" details="API is reachable" run_id=32d34c8b-881a-4952-8c3c-abb9632e85de status=pass target=api.cloudflare.com:443
2026-08-14T11:08:43Z INF precheck complete hard_fail=false run_id=32d34c8b-881a-4952-8c3c-abb9632e85de suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:50:32] Time: Fri Aug 14 06:50:32 PM CST 2026
[18:50:32] User: root (UID: 0)
[18:50:32] === STEP 1: 启动 API (端口 8450) ===
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-14 19:08:36 CST; 25min ago
   Main PID: 2342814 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 19.9M
        CPU: 2.654s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2342814 /bin/bash /opt/start-tunnel.sh
             └─2342822 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 11:33:50 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786707230.4305656, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
