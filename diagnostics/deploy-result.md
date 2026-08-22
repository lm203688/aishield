=== DIAGNOSTIC ===
Time: Sat Aug 22 08:32:10 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787358730.768415, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1063983  1.1  1.4 1294676 29348 ?       Sl   08:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1064169  2.1  1.6 1360028 32720 ?       Sl   08:32   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-22T00:31:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-22T00:31:59Z INF Registered tunnel connection connIndex=1 connection=1ded74c0-1905-4bfe-af98-73958641671c event=0 ip=198.41.200.43 location=sjc05 protocol=quic
2026-08-22T00:32:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-08-22T00:32:00Z INF +-------------------------------------------------------------------------------------+
2026-08-22T00:32:00Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-22T00:32:00Z INF +-------------------------------------------------------------------------------------+
2026-08-22T00:32:00Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-22T00:32:00Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-22T00:32:00Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-22T00:32:00Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-22T00:32:00Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-22T00:32:00Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-22T00:32:00Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-22T00:32:00Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-22T00:32:00Z INF |                                                                                     |
2026-08-22T00:32:00Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-22T00:32:00Z INF +-------------------------------------------------------------------------------------+
2026-08-22T00:32:00Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region1.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region2.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region1.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region2.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region1.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region2.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=api.cloudflare.com:443
2026-08-22T00:32:00Z INF precheck complete hard_fail=false run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 suggested_protocol=quic
2026-08-22T00:32:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.77
2026-08-22T00:32:01Z INF Registered tunnel connection connIndex=3 connection=8a5c5314-143c-455a-aac5-70e715b6c398 event=0 ip=198.41.192.77 location=sjc06 protocol=quic
2026-08-22T00:32:05Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.73
2026-08-22T00:32:05Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.73
2026-08-22T00:32:07Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:31:42] Time: Sat Aug 22 08:31:42 AM CST 2026
[08:31:42] User: root (UID: 0)
[08:31:42] === STEP 1: 启动 API (端口 8450) ===
[08:31:44] API 已在运行
[08:31:44] API 状态: OK
[08:31:44] === STEP 2: 安装 cloudflared ===
[08:31:44] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:31:45] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:31:45] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:31:45] === STEP 3: 检查认证方式 ===
[08:31:45] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:31:45] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:31:45] 检查现有 tunnel...
[08:31:46] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xsjc01, 3xsjc06, 1xsjc07, 1xsjc08, 2xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[08:31:46] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:31:46] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:31:46] 凭证文件存在
[08:31:46] 创建 config.yml...
[08:31:46] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:31:46] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:31:48] DNS 路由结果: 2026-08-22T00:31:48Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:31:48] === STEP 5: 更新 DNS (API) ===
[08:31:48] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:31:48] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:31:49] 设置 SSL 模式为 Full...
SSL: 跳过
[08:31:49] === STEP 6: 启动 Tunnel ===
[08:31:52] 启动 Named Tunnel (cert 模式)...
[08:31:52] 使用 config: /root/.cloudflared/config.yml
[08:31:52] cloudflared PID: 1063983
[08:32:01] Tunnel 连接已建立!
[08:32:01] --- cloudflared 日志 (最后 15 行) ---
2026-08-22T00:32:00Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-22T00:32:00Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-22T00:32:00Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-22T00:32:00Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-22T00:32:00Z INF |                                                                                     |
2026-08-22T00:32:00Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-22T00:32:00Z INF +-------------------------------------------------------------------------------------+
2026-08-22T00:32:00Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region1.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region2.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region1.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region2.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region1.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=region2.v2.argotunnel.com
2026-08-22T00:32:00Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 status=pass target=api.cloudflare.com:443
2026-08-22T00:32:00Z INF precheck complete hard_fail=false run_id=f3c55155-d21d-46d3-8d6a-48969ee8fe02 suggested_protocol=quic
[08:32:01] === STEP 7: 持久化 ===
[08:32:01] systemd 服务已配置
[08:32:01] Cron 保活已设置
[08:32:01] === STEP 8: 验证 ===
[08:32:01] --- API (localhost:8450) ---
 OK
[08:32:01] --- cloudflared 进程 ---
root     1063983  1.2  1.8 1294676 37784 ?       Sl   08:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1064169  0.0  1.2 1358092 24244 ?       Rl   08:32   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:32:01] --- aishield.tools ---
 OK
[08:32:03] --- DNS CNAME ---
[08:32:03] --- DNS A ---
172.67.188.44
104.21.81.46
[08:32:03] === 部署汇总 ===
[08:32:03] Tunnel Mode: cert
[08:32:03] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:32:03] API: http://localhost:8450
[08:32:03] 域名: https://aishield.tools
[08:32:03] cloudflared: /usr/local/bin/cloudflared
[08:32:03] PID: 1063983
[08:32:03] Config: /root/.cloudflared/config.yml
[08:32:03] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:32:03] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-22 08:32:01 CST; 9s ago
   Main PID: 1064161 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 24.9M
        CPU: 196ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1064161 /bin/bash /opt/start-tunnel.sh
             └─1064169 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sat Aug 22 00:32:12 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787358732.476002, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
