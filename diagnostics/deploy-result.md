=== DIAGNOSTIC ===
Time: Fri Aug 14 04:54:00 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786697640.8257823, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2184149  0.1  1.8 1294676 36868 ?       Sl   15:04   0:10 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2184251  0.1  1.8 1294676 37688 ?       Sl   15:04   0:10 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T07:04:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-14T07:04:57Z INF Registered tunnel connection connIndex=0 connection=55d2902f-1c29-488d-a771-e1c95c316ffa event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-14T07:04:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-14T07:04:58Z INF Registered tunnel connection connIndex=1 connection=3f27fcda-8c70-4ebc-ba81-752ee4f37fc3 event=0 ip=198.41.192.47 location=lax11 protocol=quic
2026-08-14T07:04:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-14T07:04:59Z INF Registered tunnel connection connIndex=2 connection=c751fad2-ba6c-4d70-96f4-d7b4f5e088e4 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-14T07:04:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.107
2026-08-14T07:05:00Z INF Registered tunnel connection connIndex=3 connection=eab2754c-6a55-4cd5-81e2-88ebdd746e3b event=0 ip=198.41.192.107 location=lax10 protocol=quic
2026-08-14T07:05:05Z INF +-------------------------------------------------------------------------------------+
2026-08-14T07:05:05Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-14T07:05:05Z INF +-------------------------------------------------------------------------------------+
2026-08-14T07:05:05Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-14T07:05:05Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T07:05:05Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T07:05:05Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T07:05:05Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T07:05:05Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T07:05:05Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T07:05:05Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-14T07:05:05Z INF |                                                                                     |
2026-08-14T07:05:05Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-14T07:05:05Z INF +-------------------------------------------------------------------------------------+
2026-08-14T07:05:05Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=bd291c1f-d1c1-4cab-a6de-5d97788ff922 status=pass target=region1.v2.argotunnel.com
2026-08-14T07:05:05Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=bd291c1f-d1c1-4cab-a6de-5d97788ff922 status=pass target=region2.v2.argotunnel.com
2026-08-14T07:05:05Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=bd291c1f-d1c1-4cab-a6de-5d97788ff922 status=pass target=region1.v2.argotunnel.com
2026-08-14T07:05:05Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=bd291c1f-d1c1-4cab-a6de-5d97788ff922 status=pass target=region2.v2.argotunnel.com
2026-08-14T07:05:05Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bd291c1f-d1c1-4cab-a6de-5d97788ff922 status=pass target=region1.v2.argotunnel.com
2026-08-14T07:05:05Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bd291c1f-d1c1-4cab-a6de-5d97788ff922 status=pass target=region2.v2.argotunnel.com
2026-08-14T07:05:05Z INF precheck component="Cloudflare API" details="API is reachable" run_id=bd291c1f-d1c1-4cab-a6de-5d97788ff922 status=pass target=api.cloudflare.com:443
2026-08-14T07:05:05Z INF precheck complete hard_fail=false run_id=bd291c1f-d1c1-4cab-a6de-5d97788ff922 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[15:04:45] Time: Fri Aug 14 03:04:45 PM CST 2026
[15:04:45] User: root (UID: 0)
[15:04:45] === STEP 1: 启动 API (端口 8450) ===
[15:04:47] API 已在运行
[15:04:47] API 状态: OK
[15:04:47] === STEP 2: 安装 cloudflared ===
[15:04:47] cloudflared 安装路径: /usr/local/bin/cloudflared
[15:04:47] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[15:04:47] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[15:04:47] === STEP 3: 检查认证方式 ===
[15:04:47] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[15:04:47] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[15:04:47] 检查现有 tunnel...
[15:04:48] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax07, 1xlax08, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-14T07:04:48Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.1
[15:04:48] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[15:04:48] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[15:04:48] 凭证文件存在
[15:04:48] 创建 config.yml...
[15:04:48] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[15:04:48] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[15:04:50] DNS 路由结果: 2026-08-14T07:04:50Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[15:04:50] === STEP 5: 更新 DNS (API) ===
[15:04:50] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[15:04:51] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[15:04:52] 设置 SSL 模式为 Full...
SSL: 跳过
[15:04:54] === STEP 6: 启动 Tunnel ===
[15:04:57] 启动 Named Tunnel (cert 模式)...
[15:04:57] 使用 config: /root/.cloudflared/config.yml
[15:04:57] cloudflared PID: 2184149
[15:04:59] Tunnel 连接已建立!
[15:04:59] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T07:04:57Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T07:04:57Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T07:04:57Z INF Generated Connector ID: 6d4983f7-200a-47ac-a74a-7cfea5cc8f53
2026-08-14T07:04:57Z INF Initial protocol quic
2026-08-14T07:04:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T07:04:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T07:04:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T07:04:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T07:04:57Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-14T07:04:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-14T07:04:57Z INF Registered tunnel connection connIndex=0 connection=55d2902f-1c29-488d-a771-e1c95c316ffa event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-14T07:04:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-14T07:04:58Z INF Registered tunnel connection connIndex=1 connection=3f27fcda-8c70-4ebc-ba81-752ee4f37fc3 event=0 ip=198.41.192.47 location=lax11 protocol=quic
2026-08-14T07:04:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-14T07:04:59Z INF Registered tunnel connection connIndex=2 connection=c751fad2-ba6c-4d70-96f4-d7b4f5e088e4 event=0 ip=198.41.200.63 location=lax01 protocol=quic
[15:04:59] === STEP 7: 持久化 ===
[15:04:59] systemd 服务已配置
[15:04:59] Cron 保活已设置
[15:04:59] === STEP 8: 验证 ===
[15:04:59] --- API (localhost:8450) ---
 OK
[15:04:59] --- cloudflared 进程 ---
root     2184149  4.5  1.9 1294420 38640 ?       Sl   15:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2184251  0.0  1.3 1292484 27452 ?       Sl   15:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[15:04:59] --- aishield.tools ---
 OK
[15:05:01] --- DNS CNAME ---
[15:05:01] --- DNS A ---
172.67.188.44
104.21.81.46
[15:05:02] === 部署汇总 ===
[15:05:02] Tunnel Mode: cert
[15:05:02] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[15:05:02] API: http://localhost:8450
[15:05:02] 域名: https://aishield.tools
[15:05:02] cloudflared: /usr/local/bin/cloudflared
[15:05:02] PID: 2184149
[15:05:02] Config: /root/.cloudflared/config.yml
[15:05:02] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[15:05:02] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-14 15:04:59 CST; 1h 49min ago
   Main PID: 2184247 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 15.6M
        CPU: 10.805s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2184247 /bin/bash /opt/start-tunnel.sh
             └─2184251 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 08:54:01 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786697641.3533108, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
