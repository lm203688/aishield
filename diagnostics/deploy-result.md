=== DIAGNOSTIC ===
Time: Sat Aug 22 02:10:35 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787335835.347687, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      814312  0.9  1.9 1294676 39792 ?       Sl   02:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      814423  1.2  1.9 1294676 39704 ?       Sl   02:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-21T18:10:23Z INF Registered tunnel connection connIndex=0 connection=675eec0e-88dc-45ae-9dff-fe88004db57d event=0 ip=198.41.200.13 location=sjc08 protocol=quic
2026-08-21T18:10:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-21T18:10:24Z INF Registered tunnel connection connIndex=1 connection=7f9628d7-d2ef-419a-9ffd-6dfb71a2bcc5 event=0 ip=198.41.192.47 location=sjc01 protocol=quic
2026-08-21T18:10:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-21T18:10:25Z INF Registered tunnel connection connIndex=2 connection=8fd0963f-37bf-4232-92f0-a3114dfa20de event=0 ip=198.41.200.63 location=sjc08 protocol=quic
2026-08-21T18:10:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-08-21T18:10:26Z INF Registered tunnel connection connIndex=3 connection=fbf125fe-b34c-458a-bced-1810981cd0b1 event=0 ip=198.41.192.57 location=sjc06 protocol=quic
2026-08-21T18:10:33Z INF +-----------------------------------------------------------------------------------------------+
2026-08-21T18:10:33Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-21T18:10:33Z INF +-----------------------------------------------------------------------------------------------+
2026-08-21T18:10:33Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-21T18:10:33Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-21T18:10:33Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-21T18:10:33Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-21T18:10:33Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-21T18:10:33Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-21T18:10:33Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-21T18:10:33Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-21T18:10:33Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-21T18:10:33Z INF |                                                                                               |
2026-08-21T18:10:33Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-21T18:10:33Z INF +-----------------------------------------------------------------------------------------------+
2026-08-21T18:10:33Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=bffbface-b667-4582-9a7d-796c5f38e3c2 status=pass target=region1.v2.argotunnel.com
2026-08-21T18:10:33Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=bffbface-b667-4582-9a7d-796c5f38e3c2 status=pass target=region2.v2.argotunnel.com
2026-08-21T18:10:33Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=bffbface-b667-4582-9a7d-796c5f38e3c2 status=pass target=region1.v2.argotunnel.com
2026-08-21T18:10:33Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=bffbface-b667-4582-9a7d-796c5f38e3c2 status=fail target=region2.v2.argotunnel.com
2026-08-21T18:10:33Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bffbface-b667-4582-9a7d-796c5f38e3c2 status=pass target=region1.v2.argotunnel.com
2026-08-21T18:10:33Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bffbface-b667-4582-9a7d-796c5f38e3c2 status=pass target=region2.v2.argotunnel.com
2026-08-21T18:10:33Z INF precheck component="Cloudflare API" details="API is reachable" run_id=bffbface-b667-4582-9a7d-796c5f38e3c2 status=pass target=api.cloudflare.com:443
2026-08-21T18:10:33Z INF precheck complete hard_fail=false run_id=bffbface-b667-4582-9a7d-796c5f38e3c2 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:10:12] Time: Sat Aug 22 02:10:12 AM CST 2026
[02:10:12] User: root (UID: 0)
[02:10:12] === STEP 1: 启动 API (端口 8450) ===
[02:10:15] API 已在运行
[02:10:15] API 状态: OK
[02:10:15] === STEP 2: 安装 cloudflared ===
[02:10:15] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:10:15] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:10:15] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:10:15] === STEP 3: 检查认证方式 ===
[02:10:15] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:10:15] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:10:15] 检查现有 tunnel...
[02:10:16] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xsjc01, 1xsjc05, 3xsjc06, 1xsjc07, 2xsjc08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[02:10:16] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:10:16] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:10:16] 凭证文件存在
[02:10:16] 创建 config.yml...
[02:10:16] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:10:16] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:10:18] DNS 路由结果: 2026-08-21T18:10:18Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:10:18] === STEP 5: 更新 DNS (API) ===
[02:10:18] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:10:18] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:10:19] 设置 SSL 模式为 Full...
SSL: 跳过
[02:10:20] === STEP 6: 启动 Tunnel ===
[02:10:23] 启动 Named Tunnel (cert 模式)...
[02:10:23] 使用 config: /root/.cloudflared/config.yml
[02:10:23] cloudflared PID: 814312
[02:10:25] Tunnel 连接已建立!
[02:10:25] --- cloudflared 日志 (最后 15 行) ---
2026-08-21T18:10:23Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-21T18:10:23Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-21T18:10:23Z INF Generated Connector ID: 0024ecb2-2c96-4ad3-aa08-3ca1aeddfd53
2026-08-21T18:10:23Z INF Initial protocol quic
2026-08-21T18:10:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-21T18:10:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-21T18:10:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-21T18:10:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-21T18:10:23Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-21T18:10:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-21T18:10:23Z INF Registered tunnel connection connIndex=0 connection=675eec0e-88dc-45ae-9dff-fe88004db57d event=0 ip=198.41.200.13 location=sjc08 protocol=quic
2026-08-21T18:10:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-21T18:10:24Z INF Registered tunnel connection connIndex=1 connection=7f9628d7-d2ef-419a-9ffd-6dfb71a2bcc5 event=0 ip=198.41.192.47 location=sjc01 protocol=quic
2026-08-21T18:10:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-21T18:10:25Z INF Registered tunnel connection connIndex=2 connection=8fd0963f-37bf-4232-92f0-a3114dfa20de event=0 ip=198.41.200.63 location=sjc08 protocol=quic
[02:10:25] === STEP 7: 持久化 ===
[02:10:25] systemd 服务已配置
[02:10:25] Cron 保活已设置
[02:10:25] === STEP 8: 验证 ===
[02:10:25] --- API (localhost:8450) ---
 OK
[02:10:25] --- cloudflared 进程 ---
root      814312  4.5  1.9 1294676 39576 ?       Sl   02:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      814423  0.0  1.3 1292740 27284 ?       Rl   02:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:10:25] --- aishield.tools ---
 OK
[02:10:27] --- DNS CNAME ---
[02:10:28] --- DNS A ---
104.21.81.46
172.67.188.44
[02:10:28] === 部署汇总 ===
[02:10:28] Tunnel Mode: cert
[02:10:28] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:10:28] API: http://localhost:8450
[02:10:28] 域名: https://aishield.tools
[02:10:28] cloudflared: /usr/local/bin/cloudflared
[02:10:28] PID: 814312
[02:10:28] Config: /root/.cloudflared/config.yml
[02:10:28] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:10:28] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-22 02:10:25 CST; 9s ago
   Main PID: 814422 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.0M
        CPU: 125ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─814422 /bin/bash /opt/start-tunnel.sh
             └─814423 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 21 18:10:35 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787335836.2944515, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
