=== DIAGNOSTIC ===
Time: Sat Aug 15 01:42:00 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786729320.1444898, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2342686  0.1  1.7 1294676 35824 ?       Sl   Aug14   0:38 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2342822  0.1  1.7 1294676 35476 ?       Sl   Aug14   0:39 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T16:55:49Z WRN Serve tunnel error error="datagram manager encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.63
2026-08-14T16:55:49Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.200.63
2026-08-14T16:55:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-14T16:55:50Z WRN Connection terminated error="datagram manager encountered a failure while serving" connIndex=3
2026-08-14T16:55:55Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.13
2026-08-14T16:55:55Z INF Retrying connection in up to 4s connIndex=0 event=0 ip=198.41.200.13
2026-08-14T16:55:56Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-14T16:55:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-08-14T16:56:01Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.23
2026-08-14T16:56:01Z INF Retrying connection in up to 8s connIndex=0 event=0 ip=198.41.200.23
2026-08-14T16:56:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-14T16:56:04Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.63
2026-08-14T16:56:04Z INF Retrying connection in up to 4s connIndex=3 event=0 ip=198.41.200.63
2026-08-14T16:56:07Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.113
2026-08-14T16:56:07Z INF Retrying connection in up to 16s connIndex=0 event=0 ip=198.41.200.113
2026-08-14T16:56:08Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-14T16:56:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.193
2026-08-14T16:56:23Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-14T16:56:23Z INF Retrying connection in up to 32s connIndex=0 event=0 ip=198.41.200.193
2026-08-14T16:56:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.33
2026-08-14T16:56:28Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.33
2026-08-14T16:56:28Z INF Retrying connection in up to 8s connIndex=3 event=0 ip=198.41.200.33
2026-08-14T16:56:33Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-14T16:56:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-14T16:56:46Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.23
2026-08-14T16:56:46Z INF Retrying connection in up to 1m4s connIndex=0 event=0 ip=198.41.200.23
2026-08-14T16:57:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-14T16:57:18Z INF Registered tunnel connection connIndex=0 connection=9fa22156-4661-44c6-901b-6b10b74401b0 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-14T16:57:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.53
2026-08-14T16:57:32Z INF Registered tunnel connection connIndex=3 connection=a214dde5-961f-4fe5-8d89-50393590c8b6 event=0 ip=198.41.200.53 location=lax01 protocol=quic
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
     Active: active (running) since Fri 2026-08-14 19:08:36 CST; 6h ago
   Main PID: 2342814 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.1M
        CPU: 39.664s
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
Time: Fri Aug 14 17:42:00 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786729320.9309433, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
