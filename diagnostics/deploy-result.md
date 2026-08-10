=== DIAGNOSTIC ===
Time: Mon Aug 10 06:53:29 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786359209.8736515, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2755072  0.2  1.9 1294676 38352 ?       Sl   18:51   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2755198  0.3  1.9 1294676 40120 ?       Sl   18:51   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-10T10:51:26Z INF Registered tunnel connection connIndex=0 connection=9e760cce-46c1-4309-bb9d-f0d2ae9e7d3c event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-08-10T10:51:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-10T10:51:27Z INF Registered tunnel connection connIndex=1 connection=acf61ce8-a025-42a5-aa01-6565bf16945d event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-10T10:51:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-08-10T10:51:28Z INF Registered tunnel connection connIndex=2 connection=4d075dec-f46a-42e0-8bda-9ff1c3042815 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-10T10:51:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-10T10:51:29Z INF Registered tunnel connection connIndex=3 connection=1a1d12a9-0bbd-4e8a-ac77-ebb5a59a38a4 event=0 ip=198.41.192.47 location=lax08 protocol=quic
2026-08-10T10:51:36Z INF +-----------------------------------------------------------------------------------------------+
2026-08-10T10:51:36Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-10T10:51:36Z INF +-----------------------------------------------------------------------------------------------+
2026-08-10T10:51:36Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-10T10:51:36Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-10T10:51:36Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-10T10:51:36Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-10T10:51:36Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-10T10:51:36Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-10T10:51:36Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-10T10:51:36Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-10T10:51:36Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-10T10:51:36Z INF |                                                                                               |
2026-08-10T10:51:36Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-10T10:51:36Z INF +-----------------------------------------------------------------------------------------------+
2026-08-10T10:51:36Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e9c8f6ca-b0f3-4019-bbc0-e47647d5eaff status=pass target=region1.v2.argotunnel.com
2026-08-10T10:51:36Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e9c8f6ca-b0f3-4019-bbc0-e47647d5eaff status=pass target=region2.v2.argotunnel.com
2026-08-10T10:51:36Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e9c8f6ca-b0f3-4019-bbc0-e47647d5eaff status=pass target=region1.v2.argotunnel.com
2026-08-10T10:51:36Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=e9c8f6ca-b0f3-4019-bbc0-e47647d5eaff status=fail target=region2.v2.argotunnel.com
2026-08-10T10:51:36Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e9c8f6ca-b0f3-4019-bbc0-e47647d5eaff status=pass target=region1.v2.argotunnel.com
2026-08-10T10:51:36Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e9c8f6ca-b0f3-4019-bbc0-e47647d5eaff status=pass target=region2.v2.argotunnel.com
2026-08-10T10:51:36Z INF precheck component="Cloudflare API" details="API is reachable" run_id=e9c8f6ca-b0f3-4019-bbc0-e47647d5eaff status=pass target=api.cloudflare.com:443
2026-08-10T10:51:36Z INF precheck complete hard_fail=false run_id=e9c8f6ca-b0f3-4019-bbc0-e47647d5eaff suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:53:01] Time: Mon Aug 10 06:53:01 PM CST 2026
[18:53:01] User: root (UID: 0)
[18:53:01] === STEP 1: 启动 API (端口 8450) ===
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-10 18:51:29 CST; 2min 0s ago
   Main PID: 2755190 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.0M
        CPU: 376ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2755190 /bin/bash /opt/start-tunnel.sh
             └─2755198 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 10 10:53:30 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786359210.4095383, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
