=== DIAGNOSTIC ===
Time: Wed Aug 19 05:20:06 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787131206.2685685, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2758537  0.1  1.7 1294676 36188 ?       Sl   16:42   0:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2758637  0.1  1.8 1294676 36648 ?       Sl   16:42   0:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-19T08:42:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-19T08:42:19Z INF Registered tunnel connection connIndex=0 connection=157edc2a-1658-47c0-9bae-143d7cfe9790 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-19T08:42:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-19T08:42:20Z INF Registered tunnel connection connIndex=1 connection=2c8c3ca9-0c33-4e32-8f60-445256d9c39a event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-19T08:42:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-08-19T08:42:21Z INF Registered tunnel connection connIndex=2 connection=f089a471-dd1d-4a20-9db5-5b6616d890f0 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-19T08:42:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-19T08:42:22Z INF Registered tunnel connection connIndex=3 connection=320a0304-e89d-4182-8729-eb1636b22cfe event=0 ip=198.41.192.47 location=lax10 protocol=quic
2026-08-19T08:42:26Z INF +-------------------------------------------------------------------------------------+
2026-08-19T08:42:26Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-19T08:42:26Z INF +-------------------------------------------------------------------------------------+
2026-08-19T08:42:26Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-19T08:42:26Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-19T08:42:26Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-19T08:42:26Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-19T08:42:26Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-19T08:42:26Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-19T08:42:26Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-19T08:42:26Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-19T08:42:26Z INF |                                                                                     |
2026-08-19T08:42:26Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-19T08:42:26Z INF +-------------------------------------------------------------------------------------+
2026-08-19T08:42:26Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=94bebb9b-6c42-4980-b241-9a7d596b723d status=pass target=region1.v2.argotunnel.com
2026-08-19T08:42:26Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=94bebb9b-6c42-4980-b241-9a7d596b723d status=pass target=region2.v2.argotunnel.com
2026-08-19T08:42:26Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=94bebb9b-6c42-4980-b241-9a7d596b723d status=pass target=region1.v2.argotunnel.com
2026-08-19T08:42:26Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=94bebb9b-6c42-4980-b241-9a7d596b723d status=pass target=region2.v2.argotunnel.com
2026-08-19T08:42:26Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=94bebb9b-6c42-4980-b241-9a7d596b723d status=pass target=region1.v2.argotunnel.com
2026-08-19T08:42:26Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=94bebb9b-6c42-4980-b241-9a7d596b723d status=pass target=region2.v2.argotunnel.com
2026-08-19T08:42:26Z INF precheck component="Cloudflare API" details="API is reachable" run_id=94bebb9b-6c42-4980-b241-9a7d596b723d status=pass target=api.cloudflare.com:443
2026-08-19T08:42:26Z INF precheck complete hard_fail=false run_id=94bebb9b-6c42-4980-b241-9a7d596b723d suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:40:38] Time: Wed Aug 19 04:40:38 PM CST 2026
[16:40:38] User: root (UID: 0)
[16:40:38] === STEP 1: 启动 API (端口 8450) ===
[16:42:09] API 已在运行
[16:42:09] API 状态: OK
[16:42:09] === STEP 2: 安装 cloudflared ===
[16:42:09] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:42:09] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:42:09] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:42:09] === STEP 3: 检查认证方式 ===
[16:42:09] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:42:09] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:42:09] 检查现有 tunnel...
[16:42:10] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 1xlax08, 1xlax09, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-19T08:42:10Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[16:42:10] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:42:10] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:42:10] 凭证文件存在
[16:42:10] 创建 config.yml...
[16:42:10] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:42:10] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:42:13] DNS 路由结果: 2026-08-19T08:42:13Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:42:13] === STEP 5: 更新 DNS (API) ===
[16:42:13] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:42:13] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:42:14] 设置 SSL 模式为 Full...
SSL: 跳过
[16:42:16] === STEP 6: 启动 Tunnel ===
[16:42:19] 启动 Named Tunnel (cert 模式)...
[16:42:19] 使用 config: /root/.cloudflared/config.yml
[16:42:19] cloudflared PID: 2758537
[16:42:21] Tunnel 连接已建立!
[16:42:21] --- cloudflared 日志 (最后 15 行) ---
2026-08-19T08:42:19Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-19T08:42:19Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-19T08:42:19Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-19T08:42:19Z INF Generated Connector ID: be87f55e-92b1-41c4-9897-00d80c697781
2026-08-19T08:42:19Z INF Initial protocol quic
2026-08-19T08:42:19Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T08:42:19Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T08:42:19Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T08:42:19Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T08:42:19Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-19T08:42:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-19T08:42:19Z INF Registered tunnel connection connIndex=0 connection=157edc2a-1658-47c0-9bae-143d7cfe9790 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-19T08:42:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-19T08:42:20Z INF Registered tunnel connection connIndex=1 connection=2c8c3ca9-0c33-4e32-8f60-445256d9c39a event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-19T08:42:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
[16:42:21] === STEP 7: 持久化 ===
[16:42:21] systemd 服务已配置
[16:42:21] Cron 保活已设置
[16:42:21] === STEP 8: 验证 ===
[16:42:21] --- API (localhost:8450) ---
 OK
[16:42:21] --- cloudflared 进程 ---
root     2758537  4.5  1.9 1294100 38920 ?       Sl   16:42   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2758637  0.0  1.3 1292740 26608 ?       Rl   16:42   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:42:21] --- aishield.tools ---
 OK
[16:42:23] --- DNS CNAME ---
[16:42:23] --- DNS A ---
172.67.188.44
104.21.81.46
[16:42:23] === 部署汇总 ===
[16:42:23] Tunnel Mode: cert
[16:42:23] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:42:23] API: http://localhost:8450
[16:42:23] 域名: https://aishield.tools
[16:42:23] cloudflared: /usr/local/bin/cloudflared
[16:42:23] PID: 2758537
[16:42:23] Config: /root/.cloudflared/config.yml
[16:42:23] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:42:23] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-19 16:42:21 CST; 37min ago
   Main PID: 2758633 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.0M
        CPU: 3.827s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2758633 /bin/bash /opt/start-tunnel.sh
             └─2758637 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 19 09:20:06 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787131206.7835102, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
