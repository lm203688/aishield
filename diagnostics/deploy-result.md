=== DIAGNOSTIC ===
Time: Fri Aug 7 08:56:26 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786107386.4926884, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     4031846  0.8  1.7 1294420 36012 ?       Sl   20:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4031971  1.0  1.8 1360284 37044 ?       Sl   20:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-07T12:56:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-07T12:56:12Z INF Registered tunnel connection connIndex=1 connection=e18be8c8-8156-4067-9b5c-ee4788ad8512 event=0 ip=198.41.192.47 location=lax10 protocol=quic
2026-08-07T12:56:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
2026-08-07T12:56:13Z INF Registered tunnel connection connIndex=2 connection=36b59e84-adcb-4b24-9833-8e7a874d3cc4 event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-07T12:56:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
2026-08-07T12:56:17Z INF +-------------------------------------------------------------------------------------+
2026-08-07T12:56:17Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-07T12:56:17Z INF +-------------------------------------------------------------------------------------+
2026-08-07T12:56:17Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-07T12:56:17Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-07T12:56:17Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-07T12:56:17Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-07T12:56:17Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-07T12:56:17Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-07T12:56:17Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-07T12:56:17Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-07T12:56:17Z INF |                                                                                     |
2026-08-07T12:56:17Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-07T12:56:17Z INF +-------------------------------------------------------------------------------------+
2026-08-07T12:56:17Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f81a631f-0706-4840-a0f2-72a86f7b00aa status=pass target=region1.v2.argotunnel.com
2026-08-07T12:56:17Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f81a631f-0706-4840-a0f2-72a86f7b00aa status=pass target=region2.v2.argotunnel.com
2026-08-07T12:56:17Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f81a631f-0706-4840-a0f2-72a86f7b00aa status=pass target=region1.v2.argotunnel.com
2026-08-07T12:56:17Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f81a631f-0706-4840-a0f2-72a86f7b00aa status=pass target=region2.v2.argotunnel.com
2026-08-07T12:56:17Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f81a631f-0706-4840-a0f2-72a86f7b00aa status=pass target=region1.v2.argotunnel.com
2026-08-07T12:56:17Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f81a631f-0706-4840-a0f2-72a86f7b00aa status=pass target=region2.v2.argotunnel.com
2026-08-07T12:56:17Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f81a631f-0706-4840-a0f2-72a86f7b00aa status=pass target=api.cloudflare.com:443
2026-08-07T12:56:17Z INF precheck complete hard_fail=false run_id=f81a631f-0706-4840-a0f2-72a86f7b00aa suggested_protocol=quic
2026-08-07T12:56:18Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-08-07T12:56:18Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.73
2026-08-07T12:56:20Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[20:55:48] Time: Fri Aug  7 08:55:48 PM CST 2026
[20:55:48] User: root (UID: 0)
[20:55:48] === STEP 1: 启动 API (端口 8450) ===
[20:56:01] API 已在运行
[20:56:01] API 状态: OK
[20:56:01] === STEP 2: 安装 cloudflared ===
[20:56:01] cloudflared 安装路径: /usr/local/bin/cloudflared
[20:56:01] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[20:56:01] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[20:56:01] === STEP 3: 检查认证方式 ===
[20:56:01] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[20:56:01] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[20:56:01] 检查现有 tunnel...
[20:56:02] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xfra07, 1xfra12, 1xlax01, 1xlax05, 1xlax10, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
[20:56:02] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[20:56:02] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[20:56:02] 凭证文件存在
[20:56:02] 创建 config.yml...
[20:56:02] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[20:56:02] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[20:56:04] DNS 路由结果: 2026-08-07T12:56:04Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[20:56:04] === STEP 5: 更新 DNS (API) ===
[20:56:04] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[20:56:05] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[20:56:06] 设置 SSL 模式为 Full...
SSL: 跳过
[20:56:07] === STEP 6: 启动 Tunnel ===
[20:56:10] 启动 Named Tunnel (cert 模式)...
[20:56:10] 使用 config: /root/.cloudflared/config.yml
[20:56:10] cloudflared PID: 4031846
[20:56:12] Tunnel 连接已建立!
[20:56:12] --- cloudflared 日志 (最后 15 行) ---
2026-08-07T12:56:10Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-07T12:56:10Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-07T12:56:10Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-07T12:56:10Z INF Generated Connector ID: 1dab54d9-a5bd-4969-9f74-a56061c9da51
2026-08-07T12:56:10Z INF Initial protocol quic
2026-08-07T12:56:10Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T12:56:10Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T12:56:10Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T12:56:10Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T12:56:10Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-07T12:56:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-08-07T12:56:11Z INF Registered tunnel connection connIndex=0 connection=ae0cfeca-caf2-46e9-93b1-a6b492473615 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-07T12:56:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-07T12:56:12Z INF Registered tunnel connection connIndex=1 connection=e18be8c8-8156-4067-9b5c-ee4788ad8512 event=0 ip=198.41.192.47 location=lax10 protocol=quic
2026-08-07T12:56:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
[20:56:12] === STEP 7: 持久化 ===
[20:56:13] systemd 服务已配置
[20:56:13] Cron 保活已设置
[20:56:13] === STEP 8: 验证 ===
[20:56:13] --- API (localhost:8450) ---
 OK
[20:56:13] --- cloudflared 进程 ---
root     4031846  2.6  1.9 1294100 38336 ?       Sl   20:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4031971  0.0  1.3 1292740 27308 ?       Rl   20:56   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[20:56:13] --- aishield.tools ---
 OK
[20:56:16] --- DNS CNAME ---
[20:56:16] --- DNS A ---
172.67.188.44
104.21.81.46
[20:56:16] === 部署汇总 ===
[20:56:16] Tunnel Mode: cert
[20:56:16] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[20:56:16] API: http://localhost:8450
[20:56:16] 域名: https://aishield.tools
[20:56:16] cloudflared: /usr/local/bin/cloudflared
[20:56:16] PID: 4031846
[20:56:16] Config: /root/.cloudflared/config.yml
[20:56:16] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[20:56:16] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-07 20:56:13 CST; 13s ago
   Main PID: 4031967 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 19.9M
        CPU: 155ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─4031967 /bin/bash /opt/start-tunnel.sh
             └─4031971 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug  7 12:56:26 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786107387.1775303, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
