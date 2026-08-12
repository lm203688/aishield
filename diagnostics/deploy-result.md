=== DIAGNOSTIC ===
Time: Wed Aug 12 10:31:03 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786545063.5802689, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      577232  0.8  1.8 1294092 36524 ?       Sl   22:30   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      577423  1.4  1.8 1294676 37580 ?       Sl   22:30   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-12T14:30:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-12T14:30:53Z INF Registered tunnel connection connIndex=1 connection=8ed98e58-6b4f-4cfb-9a1b-fcf22f88ab0d event=0 ip=198.41.192.47 location=lax05 protocol=quic
2026-08-12T14:30:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-12T14:30:54Z INF Registered tunnel connection connIndex=2 connection=3d5dbac8-e139-4177-95b3-f356810a4578 event=0 ip=198.41.192.77 location=lax09 protocol=quic
2026-08-12T14:30:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.193
2026-08-12T14:30:58Z INF +-------------------------------------------------------------------------------------+
2026-08-12T14:30:58Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-12T14:30:58Z INF +-------------------------------------------------------------------------------------+
2026-08-12T14:30:58Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-12T14:30:58Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-12T14:30:58Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-12T14:30:58Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-12T14:30:58Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-12T14:30:58Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-12T14:30:58Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-12T14:30:58Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-12T14:30:58Z INF |                                                                                     |
2026-08-12T14:30:58Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-12T14:30:58Z INF +-------------------------------------------------------------------------------------+
2026-08-12T14:30:58Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=078ca106-8367-4e89-86cb-66f75dbe4a8b status=pass target=region1.v2.argotunnel.com
2026-08-12T14:30:58Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=078ca106-8367-4e89-86cb-66f75dbe4a8b status=pass target=region2.v2.argotunnel.com
2026-08-12T14:30:58Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=078ca106-8367-4e89-86cb-66f75dbe4a8b status=pass target=region1.v2.argotunnel.com
2026-08-12T14:30:58Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=078ca106-8367-4e89-86cb-66f75dbe4a8b status=pass target=region2.v2.argotunnel.com
2026-08-12T14:30:58Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=078ca106-8367-4e89-86cb-66f75dbe4a8b status=pass target=region1.v2.argotunnel.com
2026-08-12T14:30:58Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=078ca106-8367-4e89-86cb-66f75dbe4a8b status=pass target=region2.v2.argotunnel.com
2026-08-12T14:30:58Z INF precheck component="Cloudflare API" details="API is reachable" run_id=078ca106-8367-4e89-86cb-66f75dbe4a8b status=pass target=api.cloudflare.com:443
2026-08-12T14:30:58Z INF precheck complete hard_fail=false run_id=078ca106-8367-4e89-86cb-66f75dbe4a8b suggested_protocol=quic
2026-08-12T14:30:59Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-12T14:30:59Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-08-12T14:31:01Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[22:30:52] Time: Wed Aug 12 10:30:52 PM CST 2026
[22:30:52] User: root (UID: 0)
[22:30:52] === STEP 1: 启动 API (端口 8450) ===
[22:30:53] Tunnel 连接已建立!
[22:30:53] --- cloudflared 日志 (最后 15 行) ---
2026-08-12T14:30:51Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-12T14:30:51Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-12T14:30:51Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-12T14:30:51Z INF Generated Connector ID: 4db3b7e6-a9e6-4eea-9482-d5445c377feb
2026-08-12T14:30:51Z INF Initial protocol quic
2026-08-12T14:30:51Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T14:30:51Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T14:30:51Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T14:30:51Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T14:30:51Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-12T14:30:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-12T14:30:52Z INF Registered tunnel connection connIndex=0 connection=a96e529e-d5ab-4608-b77a-2be4b071741a event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-12T14:30:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-12T14:30:53Z INF Registered tunnel connection connIndex=1 connection=8ed98e58-6b4f-4cfb-9a1b-fcf22f88ab0d event=0 ip=198.41.192.47 location=lax05 protocol=quic
2026-08-12T14:30:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
[22:30:53] === STEP 7: 持久化 ===
[22:30:54] systemd 服务已配置
[22:30:54] Cron 保活已设置
[22:30:54] === STEP 8: 验证 ===
[22:30:54] --- API (localhost:8450) ---
 OK
[22:30:54] --- cloudflared 进程 ---
root      577232  2.6  1.8 1293836 38100 ?       Sl   22:30   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      577423  0.0  1.3 1292484 27496 ?       Sl   22:30   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[22:30:54] --- aishield.tools ---
 OK
[22:30:56] --- DNS CNAME ---
[22:30:56] --- DNS A ---
104.21.81.46
172.67.188.44
[22:30:56] === 部署汇总 ===
[22:30:56] Tunnel Mode: cert
[22:30:56] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[22:30:56] API: http://localhost:8450
[22:30:56] 域名: https://aishield.tools
[22:30:56] cloudflared: /usr/local/bin/cloudflared
[22:30:56] PID: 577232
[22:30:56] Config: /root/.cloudflared/config.yml
[22:30:56] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:30:56] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-12 22:30:54 CST; 9s ago
   Main PID: 577422 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 18.4M
        CPU: 136ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─577422 /bin/bash /opt/start-tunnel.sh
             └─577423 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 12 14:31:03 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786545064.2239263, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
