=== DIAGNOSTIC ===
Time: Fri Aug 28 08:35:34 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787877334.4217649, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2514918  0.8  1.2 1294676 25400 ?       Sl   08:35   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2515093  1.6  1.2 1360284 26008 ?       Sl   08:35   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T00:35:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-28T00:35:25Z INF +-------------------------------------------------------------------------------------+
2026-08-28T00:35:25Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-28T00:35:25Z INF +-------------------------------------------------------------------------------------+
2026-08-28T00:35:25Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-28T00:35:25Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T00:35:25Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T00:35:25Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T00:35:25Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T00:35:25Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T00:35:25Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T00:35:25Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-28T00:35:25Z INF |                                                                                     |
2026-08-28T00:35:25Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-28T00:35:25Z INF +-------------------------------------------------------------------------------------+
2026-08-28T00:35:25Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=97101069-891c-4258-a91a-946f8b8a201a status=pass target=region1.v2.argotunnel.com
2026-08-28T00:35:25Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=97101069-891c-4258-a91a-946f8b8a201a status=pass target=region2.v2.argotunnel.com
2026-08-28T00:35:25Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=97101069-891c-4258-a91a-946f8b8a201a status=pass target=region1.v2.argotunnel.com
2026-08-28T00:35:25Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=97101069-891c-4258-a91a-946f8b8a201a status=pass target=region2.v2.argotunnel.com
2026-08-28T00:35:25Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=97101069-891c-4258-a91a-946f8b8a201a status=pass target=region1.v2.argotunnel.com
2026-08-28T00:35:25Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=97101069-891c-4258-a91a-946f8b8a201a status=pass target=region2.v2.argotunnel.com
2026-08-28T00:35:25Z INF precheck component="Cloudflare API" details="API is reachable" run_id=97101069-891c-4258-a91a-946f8b8a201a status=pass target=api.cloudflare.com:443
2026-08-28T00:35:25Z INF precheck complete hard_fail=false run_id=97101069-891c-4258-a91a-946f8b8a201a suggested_protocol=quic
2026-08-28T00:35:26Z INF Registered tunnel connection connIndex=2 connection=da7b09ff-1d17-4d2e-9145-cb6e11626ec7 event=0 ip=198.41.192.77 location=lax08 protocol=quic
2026-08-28T00:35:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.113
2026-08-28T00:35:27Z INF Registered tunnel connection connIndex=3 connection=7c8a2aa7-bb74-4bcb-b411-0508164d1d43 event=0 ip=198.41.200.113 location=sjc10 protocol=quic
2026-08-28T00:35:29Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.73
2026-08-28T00:35:29Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.73
2026-08-28T00:35:30Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-28T00:35:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:33:40] Time: Fri Aug 28 08:33:40 AM CST 2026
[08:33:40] User: root (UID: 0)
[08:33:40] === STEP 1: 启动 API (端口 8450) ===
[08:35:11] API 已在运行
[08:35:11] API 状态: OK
[08:35:11] === STEP 2: 安装 cloudflared ===
[08:35:11] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:35:11] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:35:11] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:35:11] === STEP 3: 检查认证方式 ===
[08:35:11] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:35:11] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:35:11] 检查现有 tunnel...
[08:35:12] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax07, 1xlax10, 2xlax12, 3xsjc07, 1xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-28T00:35:12Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:35:12] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:35:12] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:35:12] 凭证文件存在
[08:35:12] 创建 config.yml...
[08:35:12] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:35:12] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:35:13] DNS 路由结果: 2026-08-28T00:35:13Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:35:13] === STEP 5: 更新 DNS (API) ===
[08:35:13] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:35:14] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:35:15] 设置 SSL 模式为 Full...
SSL: 跳过
[08:35:16] === STEP 6: 启动 Tunnel ===
[08:35:19] 启动 Named Tunnel (cert 模式)...
[08:35:19] 使用 config: /root/.cloudflared/config.yml
[08:35:19] cloudflared PID: 2514918
[08:35:25] Tunnel 连接已建立!
[08:35:25] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T00:35:19Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T00:35:19Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T00:35:19Z INF Generated Connector ID: 6926b307-c907-4ad6-b93d-cac837bdf572
2026-08-28T00:35:19Z INF Initial protocol quic
2026-08-28T00:35:19Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T00:35:19Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T00:35:19Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T00:35:19Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T00:35:19Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T00:35:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.193
2026-08-28T00:35:24Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-28T00:35:24Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.193
2026-08-28T00:35:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-28T00:35:24Z INF Registered tunnel connection connIndex=0 connection=cf0001b9-90e6-48c6-a7bf-1034fb8965f5 event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-28T00:35:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
[08:35:25] === STEP 7: 持久化 ===
[08:35:25] systemd 服务已配置
[08:35:25] Cron 保活已设置
[08:35:25] === STEP 8: 验证 ===
[08:35:25] --- API (localhost:8450) ---
 OK
[08:35:25] --- cloudflared 进程 ---
root     2514918  1.5  1.9 1294676 38400 ?       Sl   08:35   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2515093  0.0  1.3 1358348 27224 ?       Rl   08:35   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:35:25] --- aishield.tools ---
 OK
[08:35:27] --- DNS CNAME ---
[08:35:27] --- DNS A ---
172.67.188.44
104.21.81.46
[08:35:27] === 部署汇总 ===
[08:35:27] Tunnel Mode: cert
[08:35:27] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:35:27] API: http://localhost:8450
[08:35:27] 域名: https://aishield.tools
[08:35:27] cloudflared: /usr/local/bin/cloudflared
[08:35:27] PID: 2514918
[08:35:27] Config: /root/.cloudflared/config.yml
[08:35:27] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:35:27] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 08:35:25 CST; 8s ago
   Main PID: 2515092 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 22.0M
        CPU: 161ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2515092 /bin/bash /opt/start-tunnel.sh
             └─2515093 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 28 00:35:35 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787877336.2714734, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
