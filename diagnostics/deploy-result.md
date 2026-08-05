=== DIAGNOSTIC ===
Time: Wed Aug 5 11:20:27 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785900027.8354628, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1532141  0.9  1.9 1294676 39216 ?       Sl   11:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1532239  1.0  1.9 1294676 39172 ?       Sl   11:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-05T03:20:14Z INF Registered tunnel connection connIndex=0 connection=feded4ec-2488-4c31-a627-e1f37908c834 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-05T03:20:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-05T03:20:15Z INF Registered tunnel connection connIndex=1 connection=a6da2c07-450b-4ef4-9cd1-8428ddd6e10b event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-08-05T03:20:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
2026-08-05T03:20:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.23
2026-08-05T03:20:17Z INF Registered tunnel connection connIndex=3 connection=e26f3a05-ff16-4145-93f1-e90a6e4314a6 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-05T03:20:17Z INF Registered tunnel connection connIndex=2 connection=c5e2e471-df67-4dcd-a185-5dcbbf7e88c5 event=0 ip=198.41.192.27 location=lax11 protocol=quic
2026-08-05T03:20:23Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T03:20:23Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-05T03:20:23Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T03:20:23Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-05T03:20:23Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-05T03:20:23Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-05T03:20:23Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-05T03:20:23Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-05T03:20:23Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-05T03:20:23Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-05T03:20:23Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-05T03:20:23Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-05T03:20:23Z INF |                                                                                               |
2026-08-05T03:20:23Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-05T03:20:23Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T03:20:23Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ec9a4551-b036-4748-bd40-a2d99779954a status=pass target=region1.v2.argotunnel.com
2026-08-05T03:20:23Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ec9a4551-b036-4748-bd40-a2d99779954a status=pass target=region2.v2.argotunnel.com
2026-08-05T03:20:23Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ec9a4551-b036-4748-bd40-a2d99779954a status=pass target=region1.v2.argotunnel.com
2026-08-05T03:20:23Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=ec9a4551-b036-4748-bd40-a2d99779954a status=fail target=region2.v2.argotunnel.com
2026-08-05T03:20:23Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ec9a4551-b036-4748-bd40-a2d99779954a status=pass target=region1.v2.argotunnel.com
2026-08-05T03:20:23Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ec9a4551-b036-4748-bd40-a2d99779954a status=pass target=region2.v2.argotunnel.com
2026-08-05T03:20:23Z INF precheck component="Cloudflare API" details="API is reachable" run_id=ec9a4551-b036-4748-bd40-a2d99779954a status=pass target=api.cloudflare.com:443
2026-08-05T03:20:23Z INF precheck complete hard_fail=false run_id=ec9a4551-b036-4748-bd40-a2d99779954a suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[11:19:36] Time: Wed Aug  5 11:19:36 AM CST 2026
[11:19:36] User: root (UID: 0)
[11:19:36] === STEP 1: 启动 API (端口 8450) ===
[11:19:59] API 已在运行
[11:19:59] API 状态: OK
[11:19:59] === STEP 2: 安装 cloudflared ===
[11:19:59] cloudflared 安装路径: /usr/local/bin/cloudflared
[11:19:59] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:19:59] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:19:59] === STEP 3: 检查认证方式 ===
[11:19:59] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[11:19:59] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[11:19:59] 检查现有 tunnel...
[11:20:00] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 3xlax05, 1xlax09, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[11:20:00] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:20:00] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[11:20:00] 凭证文件存在
[11:20:00] 创建 config.yml...
[11:20:00] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[11:20:00] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:20:03] DNS 路由结果: 2026-08-05T03:20:03Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[11:20:03] === STEP 5: 更新 DNS (API) ===
[11:20:03] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:20:04] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[11:20:07] 设置 SSL 模式为 Full...
SSL: 跳过
[11:20:10] === STEP 6: 启动 Tunnel ===
[11:20:13] 启动 Named Tunnel (cert 模式)...
[11:20:13] 使用 config: /root/.cloudflared/config.yml
[11:20:13] cloudflared PID: 1532141
[11:20:15] Tunnel 连接已建立!
[11:20:15] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T03:20:13Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-05T03:20:13Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-05T03:20:13Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T03:20:13Z INF Generated Connector ID: bc5de50b-4a77-4b64-b261-104e4a0d871c
2026-08-05T03:20:13Z INF Initial protocol quic
2026-08-05T03:20:13Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T03:20:13Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T03:20:13Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T03:20:13Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T03:20:13Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-05T03:20:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-05T03:20:14Z INF Registered tunnel connection connIndex=0 connection=feded4ec-2488-4c31-a627-e1f37908c834 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-05T03:20:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-05T03:20:15Z INF Registered tunnel connection connIndex=1 connection=a6da2c07-450b-4ef4-9cd1-8428ddd6e10b event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-08-05T03:20:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
[11:20:15] === STEP 7: 持久化 ===
[11:20:16] systemd 服务已配置
[11:20:16] Cron 保活已设置
[11:20:16] === STEP 8: 验证 ===
[11:20:16] --- API (localhost:8450) ---
 OK
[11:20:16] --- cloudflared 进程 ---
root     1532141  3.0  1.9 1294676 38948 ?       Sl   11:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1532239  0.0  1.3 1292484 27304 ?       Rl   11:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[11:20:16] --- aishield.tools ---
 OK
[11:20:18] --- DNS CNAME ---
[11:20:18] --- DNS A ---
104.21.81.46
172.67.188.44
[11:20:18] === 部署汇总 ===
[11:20:18] Tunnel Mode: cert
[11:20:18] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:20:18] API: http://localhost:8450
[11:20:18] 域名: https://aishield.tools
[11:20:18] cloudflared: /usr/local/bin/cloudflared
[11:20:18] PID: 1532141
[11:20:18] Config: /root/.cloudflared/config.yml
[11:20:18] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:20:18] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 11:20:16 CST; 11s ago
   Main PID: 1532231 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.9M
        CPU: 131ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1532231 /bin/bash /opt/start-tunnel.sh
             └─1532239 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug  5 03:20:28 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785900028.665799, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
