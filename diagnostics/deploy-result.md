=== DIAGNOSTIC ===
Time: Thu Aug 27 02:31:31 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787769091.860338, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1318905  0.1  1.7 1294676 34936 ?       Sl   02:04   0:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1319042  0.1  1.6 1294676 34072 ?       Sl   02:04   0:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-26T18:04:43Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-08-26T18:04:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.107
2026-08-26T18:04:45Z INF Registered tunnel connection connIndex=3 connection=b8618478-6fcc-480a-9399-f9afc2f30da5 event=0 ip=198.41.192.107 location=lax10 protocol=quic
2026-08-26T18:04:48Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.73
2026-08-26T18:04:48Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.73
2026-08-26T18:04:48Z INF +-------------------------------------------------------------------------------------+
2026-08-26T18:04:48Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-26T18:04:48Z INF +-------------------------------------------------------------------------------------+
2026-08-26T18:04:48Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-26T18:04:48Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-26T18:04:48Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-26T18:04:48Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-26T18:04:48Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-26T18:04:48Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-26T18:04:48Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-26T18:04:48Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-26T18:04:48Z INF |                                                                                     |
2026-08-26T18:04:48Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-26T18:04:48Z INF +-------------------------------------------------------------------------------------+
2026-08-26T18:04:48Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=322949c6-0cd2-4d3c-8ce3-9fb2937aecee status=pass target=region1.v2.argotunnel.com
2026-08-26T18:04:48Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=322949c6-0cd2-4d3c-8ce3-9fb2937aecee status=pass target=region2.v2.argotunnel.com
2026-08-26T18:04:48Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=322949c6-0cd2-4d3c-8ce3-9fb2937aecee status=pass target=region1.v2.argotunnel.com
2026-08-26T18:04:48Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=322949c6-0cd2-4d3c-8ce3-9fb2937aecee status=pass target=region2.v2.argotunnel.com
2026-08-26T18:04:48Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=322949c6-0cd2-4d3c-8ce3-9fb2937aecee status=pass target=region1.v2.argotunnel.com
2026-08-26T18:04:48Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=322949c6-0cd2-4d3c-8ce3-9fb2937aecee status=pass target=region2.v2.argotunnel.com
2026-08-26T18:04:48Z INF precheck component="Cloudflare API" details="API is reachable" run_id=322949c6-0cd2-4d3c-8ce3-9fb2937aecee status=pass target=api.cloudflare.com:443
2026-08-26T18:04:48Z INF precheck complete hard_fail=false run_id=322949c6-0cd2-4d3c-8ce3-9fb2937aecee suggested_protocol=quic
2026-08-26T18:04:49Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-26T18:05:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-26T18:05:00Z INF Registered tunnel connection connIndex=2 connection=cfa9206a-4e80-41fb-abe1-2835a42e37f2 event=0 ip=198.41.200.53 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:04:32] Time: Thu Aug 27 02:04:32 AM CST 2026
[02:04:32] User: root (UID: 0)
[02:04:32] === STEP 1: 启动 API (端口 8450) ===
[02:04:33] API 已在运行
[02:04:33] API 状态: OK
[02:04:33] === STEP 2: 安装 cloudflared ===
[02:04:33] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:33] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:33] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:33] === STEP 3: 检查认证方式 ===
[02:04:33] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:33] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:33] 检查现有 tunnel...
[02:04:34] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xlax01, 2xlax08, 1xlax10, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-26T18:04:34Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:04:34] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:34] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:34] 凭证文件存在
[02:04:34] 创建 config.yml...
[02:04:34] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:34] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:35] DNS 路由结果: 2026-08-26T18:04:35Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:35] === STEP 5: 更新 DNS (API) ===
[02:04:35] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:36] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:04:38] 设置 SSL 模式为 Full...
SSL: 跳过
[02:04:39] === STEP 6: 启动 Tunnel ===
[02:04:42] 启动 Named Tunnel (cert 模式)...
[02:04:42] 使用 config: /root/.cloudflared/config.yml
[02:04:42] cloudflared PID: 1318905
[02:04:44] Tunnel 连接已建立!
[02:04:44] --- cloudflared 日志 (最后 15 行) ---
2026-08-26T18:04:42Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-26T18:04:42Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-26T18:04:42Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-26T18:04:42Z INF Generated Connector ID: ace8fd57-a737-461d-b710-55badbfbf7e7
2026-08-26T18:04:42Z INF Initial protocol quic
2026-08-26T18:04:42Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-26T18:04:42Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-26T18:04:42Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-26T18:04:42Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-26T18:04:42Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-26T18:04:42Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-26T18:04:42Z INF Registered tunnel connection connIndex=0 connection=3f8571db-997f-41c9-ae0a-68d3acbc5b7d event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-26T18:04:42Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.77
2026-08-26T18:04:43Z INF Registered tunnel connection connIndex=1 connection=43f6dbe4-4e59-49c4-8428-ca6ec4fe968d event=0 ip=198.41.192.77 location=lax09 protocol=quic
2026-08-26T18:04:43Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[02:04:44] === STEP 7: 持久化 ===
[02:04:44] systemd 服务已配置
[02:04:44] Cron 保活已设置
[02:04:44] === STEP 8: 验证 ===
[02:04:44] --- API (localhost:8450) ---
 OK
[02:04:44] --- cloudflared 进程 ---
root     1318905  5.5  1.9 1294100 38660 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1319042  0.0  1.3 1292740 27504 ?       Rl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:04:44] --- aishield.tools ---
 OK
[02:04:46] --- DNS CNAME ---
[02:04:46] --- DNS A ---
172.67.188.44
104.21.81.46
[02:04:46] === 部署汇总 ===
[02:04:46] Tunnel Mode: cert
[02:04:46] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:46] API: http://localhost:8450
[02:04:46] 域名: https://aishield.tools
[02:04:46] cloudflared: /usr/local/bin/cloudflared
[02:04:46] PID: 1318905
[02:04:46] Config: /root/.cloudflared/config.yml
[02:04:46] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:46] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-27 02:04:44 CST; 26min ago
   Main PID: 1319034 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.1M
        CPU: 3.095s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1319034 /bin/bash /opt/start-tunnel.sh
             └─1319042 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 26 18:31:32 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787769092.3458452, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
