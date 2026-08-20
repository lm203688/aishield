=== DIAGNOSTIC ===
Time: Thu Aug 20 04:21:08 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787214068.8500319, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3678578  0.1  1.8 1294676 37268 ?       Sl   16:15   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3678725  0.2  1.8 1294676 37468 ?       Sl   16:15   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3682752  2.5  1.5 1292740 31296 ?       Sl   16:21   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-20T08:15:37Z INF Registered tunnel connection connIndex=2 connection=6e4a0b98-b444-45b4-8a50-7f6d959f09d6 event=0 ip=198.41.192.37 location=lax07 protocol=quic
2026-08-20T08:15:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
2026-08-20T08:15:43Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-08-20T08:15:43Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.73
2026-08-20T08:15:44Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-20T08:15:45Z INF +-----------------------------------------------------------------------------------------------+
2026-08-20T08:15:45Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-20T08:15:45Z INF +-----------------------------------------------------------------------------------------------+
2026-08-20T08:15:45Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-20T08:15:45Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-20T08:15:45Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-20T08:15:45Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-20T08:15:45Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-20T08:15:45Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-20T08:15:45Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-20T08:15:45Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-20T08:15:45Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-20T08:15:45Z INF |                                                                                               |
2026-08-20T08:15:45Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-20T08:15:45Z INF +-----------------------------------------------------------------------------------------------+
2026-08-20T08:15:45Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=6a5707bc-7471-49e8-adb0-1e6187ebdcf2 status=pass target=region1.v2.argotunnel.com
2026-08-20T08:15:45Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=6a5707bc-7471-49e8-adb0-1e6187ebdcf2 status=pass target=region2.v2.argotunnel.com
2026-08-20T08:15:45Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=6a5707bc-7471-49e8-adb0-1e6187ebdcf2 status=pass target=region1.v2.argotunnel.com
2026-08-20T08:15:45Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=6a5707bc-7471-49e8-adb0-1e6187ebdcf2 status=fail target=region2.v2.argotunnel.com
2026-08-20T08:15:45Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=6a5707bc-7471-49e8-adb0-1e6187ebdcf2 status=pass target=region1.v2.argotunnel.com
2026-08-20T08:15:45Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=6a5707bc-7471-49e8-adb0-1e6187ebdcf2 status=pass target=region2.v2.argotunnel.com
2026-08-20T08:15:45Z INF precheck component="Cloudflare API" details="API is reachable" run_id=6a5707bc-7471-49e8-adb0-1e6187ebdcf2 status=pass target=api.cloudflare.com:443
2026-08-20T08:15:45Z INF precheck complete hard_fail=false run_id=6a5707bc-7471-49e8-adb0-1e6187ebdcf2 suggested_protocol=http2
2026-08-20T08:16:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-20T08:16:02Z INF Registered tunnel connection connIndex=3 connection=42017e3e-5f81-408f-8d26-7971256222ed event=0 ip=198.41.200.233 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:18:55] Time: Thu Aug 20 04:18:55 PM CST 2026
[16:18:55] User: root (UID: 0)
[16:18:55] === STEP 1: 启动 API (端口 8450) ===
[16:21:05] API 已在运行
[16:21:05] API 状态: OK
[16:21:05] === STEP 2: 安装 cloudflared ===
[16:21:05] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:21:06] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:21:06] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:21:06] === STEP 3: 检查认证方式 ===
[16:21:06] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:21:06] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:21:06] 检查现有 tunnel...
[16:21:06] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax07, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[16:21:06] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:21:06] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:21:06] 凭证文件存在
[16:21:06] 创建 config.yml...
[16:21:06] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:21:06] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-20 16:15:38 CST; 5min ago
   Main PID: 3678717 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 15.9M
        CPU: 715ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3678717 /bin/bash /opt/start-tunnel.sh
             └─3678725 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=1897042,fd=3))                                                    
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
Time: Thu Aug 20 08:21:09 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787214069.383982, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
