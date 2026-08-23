=== DIAGNOSTIC ===
Time: Mon Aug 24 01:09:45 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787504985.0555978, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2525624  0.1  1.8 1294676 36924 ?       Sl   Aug23   0:17 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2525823  0.1  1.8 1294676 37324 ?       Sl   Aug23   0:18 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-23T14:01:20Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-23T14:01:20Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-23T14:01:20Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-23T14:01:20Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-23T14:01:20Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-23T14:01:20Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-23T14:01:20Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-23T14:01:20Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-23T14:01:20Z INF |                                                                                               |
2026-08-23T14:01:20Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-23T14:01:20Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T14:01:20Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=633caf78-9f8f-46f2-bdc5-418376a690ea status=pass target=region1.v2.argotunnel.com
2026-08-23T14:01:20Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=633caf78-9f8f-46f2-bdc5-418376a690ea status=pass target=region2.v2.argotunnel.com
2026-08-23T14:01:20Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=633caf78-9f8f-46f2-bdc5-418376a690ea status=pass target=region1.v2.argotunnel.com
2026-08-23T14:01:20Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=633caf78-9f8f-46f2-bdc5-418376a690ea status=fail target=region2.v2.argotunnel.com
2026-08-23T14:01:20Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=633caf78-9f8f-46f2-bdc5-418376a690ea status=pass target=region1.v2.argotunnel.com
2026-08-23T14:01:20Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=633caf78-9f8f-46f2-bdc5-418376a690ea status=pass target=region2.v2.argotunnel.com
2026-08-23T14:01:20Z INF precheck component="Cloudflare API" details="API is reachable" run_id=633caf78-9f8f-46f2-bdc5-418376a690ea status=pass target=api.cloudflare.com:443
2026-08-23T14:01:20Z INF precheck complete hard_fail=false run_id=633caf78-9f8f-46f2-bdc5-418376a690ea suggested_protocol=http2
2026-08-23T14:01:21Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.193
2026-08-23T14:01:21Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.193
2026-08-23T14:01:23Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-23T14:01:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
2026-08-23T14:01:43Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.73
2026-08-23T14:01:43Z INF Retrying connection in up to 4s connIndex=1 event=0 ip=198.41.200.73
2026-08-23T14:01:43Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-23T14:01:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-08-23T14:01:55Z INF Registered tunnel connection connIndex=1 connection=129cf6d2-ff8d-44a4-9b5f-2816370d5e1a event=0 ip=198.41.200.53 location=sjc05 protocol=quic
2026-08-23T15:26:40Z ERR  error="stream 33 canceled by remote with error code 0" connIndex=0 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-23T15:26:40Z ERR Request failed error="stream 33 canceled by remote with error code 0" connIndex=0 dest=https://aishield.tools/ event=0 ip=198.41.192.167 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[21:43:23] Time: Sun Aug 23 09:43:23 PM CST 2026
[21:43:23] User: root (UID: 0)
[21:43:23] === STEP 1: 启动 API (端口 8450) ===
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-23 22:01:21 CST; 3h 8min ago
   Main PID: 2525820 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 18.3M
        CPU: 18.053s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2525820 /bin/bash /opt/start-tunnel.sh
             └─2525823 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sun Aug 23 17:09:45 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787504985.6457832, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
