=== DIAGNOSTIC ===
Time: Tue Aug 25 09:38:33 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787621913.1656842, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3921031  0.8  1.8 1294420 37860 ?       Sl   09:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3921058  1.0  1.8 1294420 37036 ?       Sl   09:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3921081  1.0  1.8 1360284 37108 ?       Sl   09:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3921365  2.0  1.9 1360284 38904 ?       Sl   09:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3922299  0.0  1.5 1292740 30640 ?       Sl   09:38   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-25T01:38:22Z INF Registered tunnel connection connIndex=0 connection=758e1935-6ae1-433c-b3ff-3333aa3a367e event=0 ip=198.41.192.7 location=lax09 protocol=quic
2026-08-25T01:38:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-25T01:38:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-25T01:38:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.13
2026-08-25T01:38:24Z INF Registered tunnel connection connIndex=2 connection=e3c8bdea-db6a-400f-92af-3eb58bd13332 event=0 ip=198.41.192.77 location=lax10 protocol=quic
2026-08-25T01:38:24Z INF Registered tunnel connection connIndex=3 connection=64bc41ed-a0ed-4739-869f-59433fd21c6f event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-25T01:38:27Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.2002026-08-25T01:38:28Z INF +-------------------------------------------------------------------------------------+
2026-08-25T01:38:28Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-25T2026-08-25T01:38:29Z INF +-------------------------------------------------------------------------------------+
2026-08-25T01:38:29Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-25T01:38:29Z INF +-------------------------------------------------------------------------------------+
2026-08-25T01:38:29Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-25T01:38:29Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-25T01:38:29Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-25T01:38:29Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-25T01:38:29Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-25T01:38:29Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-25T01:38:29Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-25T01:38:29Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-25T01:38:29Z INF |                                                                                     |
2026-08-25T01:38:29Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-25T01:38:29Z INF +-------------------------------------------------------------------------------------+
2026-08-25T01:38:29Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=aea940c8-1aa9-409e-a33c-5770a5b16c94 status=pass target=region1.v2.argotunnel.com
2026-08-25T01:38:29Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=aea940c8-1aa9-409e-a33c-5770a5b16c94 status=pass target=region2.v2.argotunnel.com
2026-08-25T01:38:29Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=aea940c8-1aa9-409e-a33c-5770a5b16c94 status=pass target=region1.v2.argotunnel.com
2026-08-25T01:38:29Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=aea940c8-1aa9-409e-a33c-5770a5b16c94 status=pass target=region2.v2.argotunnel.com
2026-08-25T01:38:29Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=aea940c8-1aa9-409e-a33c-5770a5b16c94 status=pass target=region1.v2.argotunnel.com
2026-08-25T01:38:29Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=aea940c8-1aa9-409e-a33c-5770a5b16c94 status=pass target=region2.v2.argotunnel.com
2026-08-25T01:38:29Z INF precheck component="Cloudflare API" details="API is reachable" run_id=aea940c8-1aa9-409e-a33c-5770a5b16c94 status=pass target=api.cloudflare.com:443
2026-08-25T01:38:29Z INF precheck complete hard_fail=false run_id=aea940c8-1aa9-409e-a33c-5770a5b16c94 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[09:38:32] Time: Tue Aug 25 09:38:32 AM CST 2026
[09:38:32] User: root (UID: 0)
[09:38:32] === STEP 1: 启动 API (端口 8450) ===
[09:38:32] DNS 路由结果: 2026-08-25T01:38:32Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[09:38:32] === STEP 5: 更新 DNS (API) ===
[09:38:32] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:38:33] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 7xlax01, 2xlax08, 1xlax09, 2xlax10, 1xlax11, 2xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
2026-08-25T01:38:32Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[09:38:33] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:38:33] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[09:38:33] 凭证文件存在
[09:38:33] 创建 config.yml...
[09:38:33] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[09:38:33] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-25 09:38:25 CST; 7s ago
   Main PID: 3921364 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 19.6M
        CPU: 163ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3921364 /bin/bash /opt/start-tunnel.sh
             └─3921365 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Tue Aug 25 01:38:33 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787621913.7916627, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
