=== DIAGNOSTIC ===
Time: Mon Aug 24 11:26:18 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787585178.9758668, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3311502  0.1  1.1 1360284 24116 ?       Sl   18:02   0:36 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3311623  0.1  1.1 1294932 23628 ?       Sl   18:02   0:38 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-24T10:02:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-24T10:02:17Z INF Registered tunnel connection connIndex=1 connection=ff8fc61a-4142-400f-a5de-96197e3b2b18 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-24T10:02:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.37
2026-08-24T10:02:18Z INF Registered tunnel connection connIndex=2 connection=acbacf8a-e309-4488-930f-8514ebc1b889 event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-24T10:02:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-24T10:02:19Z INF Registered tunnel connection connIndex=3 connection=5ca1b114-2cf2-4257-a7c0-214bb56037f9 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-24T10:02:22Z INF +-------------------------------------------------------------------------------------+
2026-08-24T10:02:22Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-24T10:02:22Z INF +-------------------------------------------------------------------------------------+
2026-08-24T10:02:22Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-24T10:02:22Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-24T10:02:22Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-24T10:02:22Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-24T10:02:22Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-24T10:02:22Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-24T10:02:22Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-24T10:02:22Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-24T10:02:22Z INF |                                                                                     |
2026-08-24T10:02:22Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-24T10:02:22Z INF +-------------------------------------------------------------------------------------+
2026-08-24T10:02:22Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=0aa46dde-1351-4968-b2e0-a21be6c59fee status=pass target=region1.v2.argotunnel.com
2026-08-24T10:02:22Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=0aa46dde-1351-4968-b2e0-a21be6c59fee status=pass target=region2.v2.argotunnel.com
2026-08-24T10:02:22Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=0aa46dde-1351-4968-b2e0-a21be6c59fee status=pass target=region1.v2.argotunnel.com
2026-08-24T10:02:22Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=0aa46dde-1351-4968-b2e0-a21be6c59fee status=pass target=region2.v2.argotunnel.com
2026-08-24T10:02:22Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=0aa46dde-1351-4968-b2e0-a21be6c59fee status=pass target=region1.v2.argotunnel.com
2026-08-24T10:02:22Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=0aa46dde-1351-4968-b2e0-a21be6c59fee status=pass target=region2.v2.argotunnel.com
2026-08-24T10:02:22Z INF precheck component="Cloudflare API" details="API is reachable" run_id=0aa46dde-1351-4968-b2e0-a21be6c59fee status=pass target=api.cloudflare.com:443
2026-08-24T10:02:22Z INF precheck complete hard_fail=false run_id=0aa46dde-1351-4968-b2e0-a21be6c59fee suggested_protocol=quic
2026-08-24T12:57:31Z ERR  error="stream 477 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-24T12:57:31Z ERR Request failed error="stream 477 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.192.37 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:02:06] Time: Mon Aug 24 06:02:06 PM CST 2026
[18:02:06] User: root (UID: 0)
[18:02:06] === STEP 1: 启动 API (端口 8450) ===
[18:02:08] API 已在运行
[18:02:08] API 状态: OK
[18:02:08] === STEP 2: 安装 cloudflared ===
[18:02:08] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:02:08] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:02:08] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:02:08] === STEP 3: 检查认证方式 ===
[18:02:08] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:02:08] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:02:08] 检查现有 tunnel...
[18:02:09] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 3xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[18:02:09] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:02:09] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:02:09] 凭证文件存在
[18:02:09] 创建 config.yml...
[18:02:09] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:02:09] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:02:10] DNS 路由结果: 2026-08-24T10:02:10Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:02:10] === STEP 5: 更新 DNS (API) ===
[18:02:10] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:02:11] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:02:12] 设置 SSL 模式为 Full...
SSL: 跳过
[18:02:13] === STEP 6: 启动 Tunnel ===
[18:02:16] 启动 Named Tunnel (cert 模式)...
[18:02:16] 使用 config: /root/.cloudflared/config.yml
[18:02:16] cloudflared PID: 3311502
[18:02:18] Tunnel 连接已建立!
[18:02:18] --- cloudflared 日志 (最后 15 行) ---
2026-08-24T10:02:16Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-24T10:02:16Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-24T10:02:16Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-24T10:02:16Z INF Generated Connector ID: cf6e671a-e3ec-4395-83e8-4fb20fd9ba25
2026-08-24T10:02:16Z INF Initial protocol quic
2026-08-24T10:02:16Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T10:02:16Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T10:02:16Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T10:02:16Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T10:02:16Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-24T10:02:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-24T10:02:16Z INF Registered tunnel connection connIndex=0 connection=ae8b94e3-537c-4f92-be8c-4cf6a39cf96a event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-08-24T10:02:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-24T10:02:17Z INF Registered tunnel connection connIndex=1 connection=ff8fc61a-4142-400f-a5de-96197e3b2b18 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-24T10:02:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.37
[18:02:18] === STEP 7: 持久化 ===
[18:02:18] systemd 服务已配置
[18:02:18] Cron 保活已设置
[18:02:18] === STEP 8: 验证 ===
[18:02:18] --- API (localhost:8450) ---
 OK
[18:02:18] --- cloudflared 进程 ---
root     3311502  4.0  1.9 1359708 39016 ?       Sl   18:02   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3311623  0.0  1.3 1292484 26960 ?       Sl   18:02   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:02:18] --- aishield.tools ---
 OK
[18:02:20] --- DNS CNAME ---
[18:02:20] --- DNS A ---
104.21.81.46
172.67.188.44
[18:02:20] === 部署汇总 ===
[18:02:20] Tunnel Mode: cert
[18:02:20] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:02:20] API: http://localhost:8450
[18:02:20] 域名: https://aishield.tools
[18:02:20] cloudflared: /usr/local/bin/cloudflared
[18:02:20] PID: 3311502
[18:02:20] Config: /root/.cloudflared/config.yml
[18:02:20] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:02:20] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-24 18:02:18 CST; 5h 24min ago
   Main PID: 3311622 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 18.1M
        CPU: 38.702s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3311622 /bin/bash /opt/start-tunnel.sh
             └─3311623 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 24 15:26:19 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787585179.404738, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
