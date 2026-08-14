=== DIAGNOSTIC ===
Time: Sat Aug 15 04:59:38 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786741178.143717, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2726755  1.6  1.9 1294676 38316 ?       Sl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2726781  1.0  1.9 1294676 38484 ?       Sl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2726983  1.8  1.8 1360284 37932 ?       Sl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
22026-08-14T20:59:30Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-14T20:59:30Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.193
2026-08-14T20:59:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-14T20:59:31Z INF Registered tunnel connection connIndex=0 connection=c5c646b3-e6d3-4695-b38c-574552cbbe3e event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-14T20:59:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
2026-08-14T20:59:32Z INF Registered tunnel connection connIndex=1 connection=2a43f0c2-324b-4a5e-b1c4-5366091f4a0d event=0 ip=198.41.192.227 location=lax11 protocol=quic
2026-08-14T20:59:32Z INF +-------------------------------------------------------------------------------------+
2026-08-14T20:59:32Z INF |                               CONNECTIVITY PRE-CHECKS          2026-08-14T20:59:37Z INF +-----------------------------------------------------------------------------------------------+
2026-08-14T20:59:37Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-14T20:59:37Z INF +-----------------------------------------------------------------------------------------------+
2026-08-14T20:59:37Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-14T20:59:37Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-14T20:59:37Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-14T20:59:37Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-14T20:59:37Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-14T20:59:37Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-14T20:59:37Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-14T20:59:37Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-14T20:59:37Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-14T20:59:37Z INF |                                                                                               |
2026-08-14T20:59:37Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-14T20:59:37Z INF +-----------------------------------------------------------------------------------------------+
2026-08-14T20:59:37Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7a9f209b-ec5f-49fd-bdd4-54cbe38fa101 status=pass target=region1.v2.argotunnel.com
2026-08-14T20:59:37Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7a9f209b-ec5f-49fd-bdd4-54cbe38fa101 status=pass target=region2.v2.argotunnel.com
2026-08-14T20:59:37Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=7a9f209b-ec5f-49fd-bdd4-54cbe38fa101 status=pass target=region1.v2.argotunnel.com
2026-08-14T20:59:37Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=7a9f209b-ec5f-49fd-bdd4-54cbe38fa101 status=fail target=region2.v2.argotunnel.com
2026-08-14T20:59:37Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7a9f209b-ec5f-49fd-bdd4-54cbe38fa101 status=pass target=region1.v2.argotunnel.com
2026-08-14T20:59:37Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7a9f209b-ec5f-49fd-bdd4-54cbe38fa101 status=pass target=region2.v2.argotunnel.com
2026-08-14T20:59:37Z INF precheck component="Cloudflare API" details="API is reachable" run_id=7a9f209b-ec5f-49fd-bdd4-54cbe38fa101 status=pass target=api.cloudflare.com:443
2026-08-14T20:59:37Z INF precheck complete hard_fail=false run_id=7a9f209b-ec5f-49fd-bdd4-54cbe38fa101 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[04:59:37] Time: Sat Aug 15 04:59:37 AM CST 2026
[04:59:37] User: root (UID: 0)
[04:59:37] === STEP 1: 启动 API (端口 8450) ===
DNS 更新: OK
[04:59:38] 设置 SSL 模式为 Full...
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-15 04:59:30 CST; 7s ago
   Main PID: 2726982 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 18.1M
        CPU: 154ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2726982 /bin/bash /opt/start-tunnel.sh
             └─2726983 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 20:59:38 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786741178.8334074, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
