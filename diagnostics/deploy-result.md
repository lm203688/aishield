=== DIAGNOSTIC ===
Time: Thu Aug 13 01:25:23 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786598723.2625694, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      614742  0.1  1.1 1294676 22788 ?       Sl   Aug12   1:19 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      614954  0.1  1.0 1294676 21912 ?       Sl   Aug12   1:20 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-12T15:16:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-12T15:16:39Z INF +-------------------------------------------------------------------------------------+
2026-08-12T15:16:39Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-12T15:16:39Z INF +-------------------------------------------------------------------------------------+
2026-08-12T15:16:39Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-12T15:16:39Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-12T15:16:39Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-12T15:16:39Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-12T15:16:39Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-12T15:16:39Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-12T15:16:39Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-12T15:16:39Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-12T15:16:39Z INF |                                                                                     |
2026-08-12T15:16:39Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-12T15:16:39Z INF +-------------------------------------------------------------------------------------+
2026-08-12T15:16:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region1.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region2.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region1.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region2.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region1.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region2.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="Cloudflare API" details="API is reachable" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=api.cloudflare.com:443
2026-08-12T15:16:39Z INF precheck complete hard_fail=false run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 suggested_protocol=quic
2026-08-12T15:16:39Z INF Registered tunnel connection connIndex=0 connection=a7b98d0d-6200-410c-8fbf-1d48d91d03b4 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-12T15:16:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-12T15:16:40Z INF Registered tunnel connection connIndex=1 connection=5a08a41d-e21f-42d6-a1c9-c1c7175c9748 event=0 ip=198.41.192.67 location=lax11 protocol=quic
2026-08-12T15:16:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-12T15:16:41Z INF Registered tunnel connection connIndex=2 connection=c031658e-6e98-4e1c-aa47-b3d49e18e924 event=0 ip=198.41.192.227 location=lax05 protocol=quic
2026-08-12T15:16:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-12T15:16:42Z INF Registered tunnel connection connIndex=3 connection=cb2bb108-e5a9-4597-842e-9c5cc814842c event=0 ip=198.41.200.233 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[13:25:13] Time: Thu Aug 13 01:25:13 PM CST 2026
[13:25:13] User: root (UID: 0)
[13:25:13] === STEP 1: 启动 API (端口 8450) ===
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-12 23:16:44 CST; 14h ago
   Main PID: 614950 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 20.6M
        CPU: 1min 20.772s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─614950 /bin/bash /opt/start-tunnel.sh
             └─614954 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 13 05:25:23 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786598723.9361343, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
