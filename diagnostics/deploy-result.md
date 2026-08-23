=== DIAGNOSTIC ===
Time: Sun Aug 23 09:58:30 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787493511.0478246, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2008847  0.1  1.0 1294676 21952 ?       Sl   08:43   1:14 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2009070  0.1  1.1 1294676 22320 ?       Sl   08:43   1:16 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-23T00:43:39Z INF Registered tunnel connection connIndex=1 connection=e7364ed7-0fca-4d1d-a71a-b582f683f36b event=0 ip=198.41.200.43 location=sjc10 protocol=quic
2026-08-23T00:43:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-23T00:43:40Z INF Registered tunnel connection connIndex=2 connection=0302ada6-d5e9-4b63-9cca-efd78b5b759c event=0 ip=198.41.200.13 location=sjc07 protocol=quic
2026-08-23T00:43:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-23T00:43:41Z INF Registered tunnel connection connIndex=3 connection=c3b6c663-0214-49d8-9201-47a166447aaf event=0 ip=198.41.192.47 location=sjc01 protocol=quic
2026-08-23T00:43:42Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T00:43:42Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-23T00:43:42Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T00:43:42Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-23T00:43:42Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-23T00:43:42Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-23T00:43:42Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-23T00:43:42Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-23T00:43:42Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-23T00:43:42Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-23T00:43:42Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-23T00:43:42Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-23T00:43:42Z INF |                                                                                               |
2026-08-23T00:43:42Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-23T00:43:42Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T00:43:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region1.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region2.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region1.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=fail target=region2.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region1.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region2.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="Cloudflare API" details="API is reachable" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=api.cloudflare.com:443
2026-08-23T00:43:42Z INF precheck complete hard_fail=false run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 suggested_protocol=http2
2026-08-23T07:13:32Z ERR  error="Incoming request ended abruptly: context canceled" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-23T07:13:32Z ERR Request failed error="Incoming request ended abruptly: context canceled" connIndex=2 dest=https://aishield.tools/api/v1/mcp event=0 ip=198.41.200.13 type=http
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
     Active: active (running) since Sun 2026-08-23 08:43:40 CST; 13h ago
   Main PID: 2009062 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.7M
        CPU: 1min 16.191s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2009062 /bin/bash /opt/start-tunnel.sh
             └─2009070 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3693189,fd=3))                                                    
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
Time: Sun Aug 23 13:58:31 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787493512.1790218, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
