=== DIAGNOSTIC ===
Time: Mon Aug 10 05:47:54 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786355274.4053183, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2710718  0.6  1.9 1360028 39868 ?       Sl   17:47   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2710927  1.2  1.9 1294420 39592 ?       Sl   17:47   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-10T09:47:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-08-10T09:47:42Z INF Registered tunnel connection connIndex=0 connection=d5d78e48-c8f0-497a-a616-f006351c0f66 event=0 ip=198.41.192.77 location=lax11 protocol=quic
2026-08-10T09:47:42Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-10T09:47:42Z INF +-------------------------------------------------------------------------------------+
2026-08-10T09:47:42Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-10T09:47:42Z INF +-------------------------------------------------------------------------------------+
2026-08-10T09:47:42Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-10T09:47:42Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-10T09:47:42Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-10T09:47:42Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-10T09:47:42Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-10T09:47:42Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-10T09:47:42Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-10T09:47:42Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-10T09:47:42Z INF |                                                                                     |
2026-08-10T09:47:42Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-10T09:47:42Z INF +-------------------------------------------------------------------------------------+
2026-08-10T09:47:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region1.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region2.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region1.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region2.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region1.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region2.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="Cloudflare API" details="API is reachable" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=api.cloudflare.com:443
2026-08-10T09:47:42Z INF precheck complete hard_fail=false run_id=a6b36368-6af4-4c92-b086-3bf008639311 suggested_protocol=quic
2026-08-10T09:47:42Z INF Registered tunnel connection connIndex=1 connection=c5520fe9-1bdc-40a2-b187-75276145246f event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-10T09:47:43Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
2026-08-10T09:47:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.113
2026-08-10T09:47:44Z INF Registered tunnel connection connIndex=2 connection=4f88b1fe-6415-4c07-9909-3313ccff6f39 event=0 ip=198.41.192.67 location=lax05 protocol=quic
2026-08-10T09:47:44Z INF Registered tunnel connection connIndex=3 connection=4a73cb09-c7d2-47de-b062-c6c3f65ff75d event=0 ip=198.41.200.113 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[17:47:24] Time: Mon Aug 10 05:47:24 PM CST 2026
[17:47:24] User: root (UID: 0)
[17:47:24] === STEP 1: 启动 API (端口 8450) ===
[17:47:27] API 已在运行
[17:47:27] API 状态: OK
[17:47:27] === STEP 2: 安装 cloudflared ===
[17:47:27] cloudflared 安装路径: /usr/local/bin/cloudflared
[17:47:27] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:47:27] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:47:27] === STEP 3: 检查认证方式 ===
[17:47:27] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[17:47:27] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[17:47:27] 检查现有 tunnel...
[17:47:29] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                    
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 12xlax01, 4xlax05, 1xlax07, 2xlax08, 1xlax09, 1xlax10, 3xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                                
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                                
[17:47:29] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:47:29] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[17:47:29] 凭证文件存在
[17:47:29] 创建 config.yml...
[17:47:29] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[17:47:29] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:47:30] DNS 路由结果: 2026-08-10T09:47:30Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:47:30] === STEP 5: 更新 DNS (API) ===
[17:47:30] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:47:31] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[17:47:31] 设置 SSL 模式为 Full...
SSL: 跳过
[17:47:32] === STEP 6: 启动 Tunnel ===
[17:47:35] 启动 Named Tunnel (cert 模式)...
[17:47:35] 使用 config: /root/.cloudflared/config.yml
[17:47:35] cloudflared PID: 2710718
[17:47:43] Tunnel 连接已建立!
[17:47:43] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T09:47:42Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-10T09:47:42Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-10T09:47:42Z INF |                                                                                     |
2026-08-10T09:47:42Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-10T09:47:42Z INF +-------------------------------------------------------------------------------------+
2026-08-10T09:47:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region1.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region2.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region1.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region2.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region1.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=region2.v2.argotunnel.com
2026-08-10T09:47:42Z INF precheck component="Cloudflare API" details="API is reachable" run_id=a6b36368-6af4-4c92-b086-3bf008639311 status=pass target=api.cloudflare.com:443
2026-08-10T09:47:42Z INF precheck complete hard_fail=false run_id=a6b36368-6af4-4c92-b086-3bf008639311 suggested_protocol=quic
2026-08-10T09:47:42Z INF Registered tunnel connection connIndex=1 connection=c5520fe9-1bdc-40a2-b187-75276145246f event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-10T09:47:43Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
[17:47:43] === STEP 7: 持久化 ===
[17:47:44] systemd 服务已配置
[17:47:44] Cron 保活已设置
[17:47:44] === STEP 8: 验证 ===
[17:47:44] --- API (localhost:8450) ---
 OK
[17:47:44] --- cloudflared 进程 ---
root     2710718  1.1  1.9 1360028 39868 ?       Sl   17:47   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2710927  0.0  1.3 1292740 27528 ?       Rl   17:47   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[17:47:44] --- aishield.tools ---
 OK
[17:47:46] --- DNS CNAME ---
[17:47:46] --- DNS A ---
172.67.188.44
104.21.81.46
[17:47:46] === 部署汇总 ===
[17:47:46] Tunnel Mode: cert
[17:47:46] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:47:46] API: http://localhost:8450
[17:47:46] 域名: https://aishield.tools
[17:47:46] cloudflared: /usr/local/bin/cloudflared
[17:47:46] PID: 2710718
[17:47:46] Config: /root/.cloudflared/config.yml
[17:47:46] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:47:46] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-10 17:47:44 CST; 10s ago
   Main PID: 2710920 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.8M
        CPU: 135ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2710920 /bin/bash /opt/start-tunnel.sh
             └─2710927 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 10 09:47:54 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786355275.3860202, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
