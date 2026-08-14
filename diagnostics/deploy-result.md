=== DIAGNOSTIC ===
Time: Fri Aug 14 09:29:32 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786670972.7616212, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1959744  1.2  1.9 1294676 38756 ?       Sl   09:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1959842  1.8  1.9 1294420 38836 ?       Sl   09:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T01:29:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-14T01:29:23Z INF Registered tunnel connection connIndex=0 connection=3da3d0b8-fd93-4911-b399-384a12d379b3 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-14T01:29:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-14T01:29:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-14T01:29:24Z INF Registered tunnel connection connIndex=1 connection=e59abaf7-38b1-4da9-8864-a00bf82e6288 event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-08-14T01:29:24Z INF Registered tunnel connection connIndex=2 connection=e648a62c-b7cd-48ff-96ae-20b2149e7bd5 event=0 ip=198.41.192.77 location=lax05 protocol=quic
2026-08-14T01:29:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.13
2026-08-14T01:29:26Z INF Registered tunnel connection connIndex=3 connection=fded521f-6cfc-4a12-8f2c-8d84548534b0 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-14T01:29:32Z INF +-------------------------------------------------------------------------------------+
2026-08-14T01:29:32Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-14T01:29:32Z INF +-------------------------------------------------------------------------------------+
2026-08-14T01:29:32Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-14T01:29:32Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T01:29:32Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T01:29:32Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T01:29:32Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T01:29:32Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T01:29:32Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T01:29:32Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-14T01:29:32Z INF |                                                                                     |
2026-08-14T01:29:32Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-14T01:29:32Z INF +-------------------------------------------------------------------------------------+
2026-08-14T01:29:32Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=12748357-ccd0-449a-9b47-a6a2c6b015dc status=pass target=region1.v2.argotunnel.com
2026-08-14T01:29:32Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=12748357-ccd0-449a-9b47-a6a2c6b015dc status=pass target=region2.v2.argotunnel.com
2026-08-14T01:29:32Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=12748357-ccd0-449a-9b47-a6a2c6b015dc status=pass target=region1.v2.argotunnel.com
2026-08-14T01:29:32Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=12748357-ccd0-449a-9b47-a6a2c6b015dc status=pass target=region2.v2.argotunnel.com
2026-08-14T01:29:32Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=12748357-ccd0-449a-9b47-a6a2c6b015dc status=pass target=region1.v2.argotunnel.com
2026-08-14T01:29:32Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=12748357-ccd0-449a-9b47-a6a2c6b015dc status=pass target=region2.v2.argotunnel.com
2026-08-14T01:29:32Z INF precheck component="Cloudflare API" details="API is reachable" run_id=12748357-ccd0-449a-9b47-a6a2c6b015dc status=pass target=api.cloudflare.com:443
2026-08-14T01:29:32Z INF precheck complete hard_fail=false run_id=12748357-ccd0-449a-9b47-a6a2c6b015dc suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[09:29:06] Time: Fri Aug 14 09:29:06 AM CST 2026
[09:29:06] User: root (UID: 0)
[09:29:06] === STEP 1: 启动 API (端口 8450) ===
[09:29:08] API 已在运行
[09:29:08] API 状态: OK
[09:29:08] === STEP 2: 安装 cloudflared ===
[09:29:08] cloudflared 安装路径: /usr/local/bin/cloudflared
[09:29:08] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:29:08] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:29:08] === STEP 3: 检查认证方式 ===
[09:29:08] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:29:08] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:29:08] 检查现有 tunnel...
[09:29:11] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax07, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[09:29:11] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:29:11] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[09:29:11] 凭证文件存在
[09:29:11] 创建 config.yml...
[09:29:11] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[09:29:11] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:29:12] DNS 路由结果: 2026-08-14T01:29:12Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[09:29:12] === STEP 5: 更新 DNS (API) ===
[09:29:12] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:29:15] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[09:29:16] 设置 SSL 模式为 Full...
SSL: 跳过
[09:29:19] === STEP 6: 启动 Tunnel ===
[09:29:22] 启动 Named Tunnel (cert 模式)...
[09:29:22] 使用 config: /root/.cloudflared/config.yml
[09:29:22] cloudflared PID: 1959744
[09:29:24] Tunnel 连接已建立!
[09:29:24] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T01:29:22Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-14T01:29:22Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-14T01:29:22Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T01:29:22Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T01:29:22Z INF Generated Connector ID: f68d610e-c1c7-458a-8588-904c30102cb4
2026-08-14T01:29:22Z INF Initial protocol quic
2026-08-14T01:29:22Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T01:29:22Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T01:29:22Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T01:29:22Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T01:29:22Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-14T01:29:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-14T01:29:23Z INF Registered tunnel connection connIndex=0 connection=3da3d0b8-fd93-4911-b399-384a12d379b3 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-14T01:29:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-14T01:29:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
[09:29:24] === STEP 7: 持久化 ===
[09:29:25] systemd 服务已配置
[09:29:25] Cron 保活已设置
[09:29:25] === STEP 8: 验证 ===
[09:29:25] --- API (localhost:8450) ---
 OK
[09:29:25] --- cloudflared 进程 ---
root     1959744  3.0  1.9 1293836 38556 ?       Sl   09:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1959842  0.0  1.3 1292484 27552 ?       Rl   09:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[09:29:25] --- aishield.tools ---
 OK
[09:29:26] --- DNS CNAME ---
[09:29:27] --- DNS A ---
104.21.81.46
172.67.188.44
[09:29:27] === 部署汇总 ===
[09:29:27] Tunnel Mode: cert
[09:29:27] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:29:27] API: http://localhost:8450
[09:29:27] 域名: https://aishield.tools
[09:29:27] cloudflared: /usr/local/bin/cloudflared
[09:29:27] PID: 1959744
[09:29:27] Config: /root/.cloudflared/config.yml
[09:29:27] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:29:27] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-14 09:29:25 CST; 7s ago
   Main PID: 1959838 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.1M
        CPU: 132ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1959838 /bin/bash /opt/start-tunnel.sh
             └─1959842 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 01:29:33 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786670973.7002993, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
