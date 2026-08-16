=== DIAGNOSTIC ===
Time: Sun Aug 16 09:10:11 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786842611.3165243, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3837685  1.2  1.9 1294676 39884 ?       Sl   09:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3837823  1.8  1.9 1294676 39316 ?       Sl   09:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-16T01:10:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-16T01:10:02Z INF Registered tunnel connection connIndex=0 connection=a87a97c8-bbcc-458e-ac52-e677b3f338c8 event=0 ip=198.41.192.37 location=lax05 protocol=quic
2026-08-16T01:10:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-16T01:10:02Z INF Registered tunnel connection connIndex=1 connection=8f320444-67f4-48b2-80b8-8c75a4715c56 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-16T01:10:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-08-16T01:10:03Z INF Registered tunnel connection connIndex=2 connection=3dcba9a4-72fa-4658-b2f9-43c64e618317 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-16T01:10:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.67
2026-08-16T01:10:04Z INF Registered tunnel connection connIndex=3 connection=034ebdc4-6ee8-4341-bde5-f79e409f436e event=0 ip=198.41.192.67 location=lax10 protocol=quic
2026-08-16T01:10:08Z INF +-------------------------------------------------------------------------------------+
2026-08-16T01:10:08Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-16T01:10:08Z INF +-------------------------------------------------------------------------------------+
2026-08-16T01:10:08Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-16T01:10:08Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-16T01:10:08Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-16T01:10:08Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-16T01:10:08Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-16T01:10:08Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-16T01:10:08Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-16T01:10:08Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-16T01:10:08Z INF |                                                                                     |
2026-08-16T01:10:08Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-16T01:10:08Z INF +-------------------------------------------------------------------------------------+
2026-08-16T01:10:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ca935bdf-6dea-4134-9865-e3068c397ed1 status=pass target=region1.v2.argotunnel.com
2026-08-16T01:10:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ca935bdf-6dea-4134-9865-e3068c397ed1 status=pass target=region2.v2.argotunnel.com
2026-08-16T01:10:08Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ca935bdf-6dea-4134-9865-e3068c397ed1 status=pass target=region1.v2.argotunnel.com
2026-08-16T01:10:08Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ca935bdf-6dea-4134-9865-e3068c397ed1 status=pass target=region2.v2.argotunnel.com
2026-08-16T01:10:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ca935bdf-6dea-4134-9865-e3068c397ed1 status=pass target=region1.v2.argotunnel.com
2026-08-16T01:10:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ca935bdf-6dea-4134-9865-e3068c397ed1 status=pass target=region2.v2.argotunnel.com
2026-08-16T01:10:08Z INF precheck component="Cloudflare API" details="API is reachable" run_id=ca935bdf-6dea-4134-9865-e3068c397ed1 status=pass target=api.cloudflare.com:443
2026-08-16T01:10:08Z INF precheck complete hard_fail=false run_id=ca935bdf-6dea-4134-9865-e3068c397ed1 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[09:09:47] Time: Sun Aug 16 09:09:47 AM CST 2026
[09:09:47] User: root (UID: 0)
[09:09:47] === STEP 1: 启动 API (端口 8450) ===
[09:09:54] API 已在运行
[09:09:54] API 状态: OK
[09:09:54] === STEP 2: 安装 cloudflared ===
[09:09:54] cloudflared 安装路径: /usr/local/bin/cloudflared
[09:09:54] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:09:54] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:09:54] === STEP 3: 检查认证方式 ===
[09:09:54] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:09:54] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:09:54] 检查现有 tunnel...
[09:09:55] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 2xlax05, 1xlax07, 2xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-16T01:09:55Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[09:09:55] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:09:55] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[09:09:55] 凭证文件存在
[09:09:55] 创建 config.yml...
[09:09:55] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[09:09:55] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:09:56] DNS 路由结果: 2026-08-16T01:09:56Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[09:09:56] === STEP 5: 更新 DNS (API) ===
[09:09:56] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:09:57] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[09:09:58] 设置 SSL 模式为 Full...
SSL: 跳过
[09:09:58] === STEP 6: 启动 Tunnel ===
[09:10:01] 启动 Named Tunnel (cert 模式)...
[09:10:01] 使用 config: /root/.cloudflared/config.yml
[09:10:01] cloudflared PID: 3837685
[09:10:03] Tunnel 连接已建立!
[09:10:03] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T01:10:01Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-16T01:10:01Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-16T01:10:01Z INF Generated Connector ID: 42883e2c-e9cc-45ac-8bad-4d3a69a31860
2026-08-16T01:10:01Z INF Initial protocol quic
2026-08-16T01:10:01Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T01:10:01Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T01:10:01Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T01:10:01Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T01:10:01Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-16T01:10:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-16T01:10:02Z INF Registered tunnel connection connIndex=0 connection=a87a97c8-bbcc-458e-ac52-e677b3f338c8 event=0 ip=198.41.192.37 location=lax05 protocol=quic
2026-08-16T01:10:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-16T01:10:02Z INF Registered tunnel connection connIndex=1 connection=8f320444-67f4-48b2-80b8-8c75a4715c56 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-16T01:10:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-08-16T01:10:03Z INF Registered tunnel connection connIndex=2 connection=3dcba9a4-72fa-4658-b2f9-43c64e618317 event=0 ip=198.41.200.43 location=lax01 protocol=quic
[09:10:03] === STEP 7: 持久化 ===
[09:10:04] systemd 服务已配置
[09:10:04] Cron 保活已设置
[09:10:04] === STEP 8: 验证 ===
[09:10:04] --- API (localhost:8450) ---
 OK
[09:10:04] --- cloudflared 进程 ---
root     3837685  3.3  1.9 1294676 39440 ?       Sl   09:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3837823  0.0  1.2 1292484 24404 ?       Rl   09:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[09:10:04] --- aishield.tools ---
 OK
[09:10:06] --- DNS CNAME ---
[09:10:06] --- DNS A ---
104.21.81.46
172.67.188.44
[09:10:06] === 部署汇总 ===
[09:10:06] Tunnel Mode: cert
[09:10:06] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:10:06] API: http://localhost:8450
[09:10:06] 域名: https://aishield.tools
[09:10:06] cloudflared: /usr/local/bin/cloudflared
[09:10:06] PID: 3837685
[09:10:06] Config: /root/.cloudflared/config.yml
[09:10:06] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:10:06] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-16 09:10:04 CST; 6s ago
   Main PID: 3837819 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.5M
        CPU: 140ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3837819 /bin/bash /opt/start-tunnel.sh
             └─3837823 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2342254,fd=3))                                                    
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
Time: Sun Aug 16 01:10:11 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786842611.9357495, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
