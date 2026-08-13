=== DIAGNOSTIC ===
Time: Fri Aug 14 07:28:14 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786663694.0963197, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1670991  0.1  1.2 1294676 25820 ?       Sl   02:04   0:29 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1671191  0.1  1.3 1294676 27248 ?       Sl   02:04   0:29 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-13T18:04:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-13T18:04:32Z INF Registered tunnel connection connIndex=0 connection=fb4e486a-73cd-404f-bcef-7ed96da6d41d event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-13T18:04:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-13T18:04:32Z INF Registered tunnel connection connIndex=1 connection=ec3f3396-769f-4249-8027-3f0f123ac37f event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-13T18:04:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-08-13T18:04:34Z INF Registered tunnel connection connIndex=2 connection=eeb89dc4-7832-415b-aea5-26591c4fdcfb event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-08-13T18:04:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.13
2026-08-13T18:04:34Z INF +-------------------------------------------------------------------------------------+
2026-08-13T18:04:34Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-13T18:04:34Z INF +-------------------------------------------------------------------------------------+
2026-08-13T18:04:34Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-13T18:04:34Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-13T18:04:34Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-13T18:04:34Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-13T18:04:34Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-13T18:04:34Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-13T18:04:34Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-13T18:04:34Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-13T18:04:34Z INF |                                                                                     |
2026-08-13T18:04:34Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-13T18:04:34Z INF +-------------------------------------------------------------------------------------+
2026-08-13T18:04:34Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=bca322c9-e9a4-4377-bd83-60d1751879cb status=pass target=region1.v2.argotunnel.com
2026-08-13T18:04:34Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=bca322c9-e9a4-4377-bd83-60d1751879cb status=pass target=region2.v2.argotunnel.com
2026-08-13T18:04:34Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=bca322c9-e9a4-4377-bd83-60d1751879cb status=pass target=region1.v2.argotunnel.com
2026-08-13T18:04:34Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=bca322c9-e9a4-4377-bd83-60d1751879cb status=pass target=region2.v2.argotunnel.com
2026-08-13T18:04:34Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bca322c9-e9a4-4377-bd83-60d1751879cb status=pass target=region1.v2.argotunnel.com
2026-08-13T18:04:34Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bca322c9-e9a4-4377-bd83-60d1751879cb status=pass target=region2.v2.argotunnel.com
2026-08-13T18:04:34Z INF precheck component="Cloudflare API" details="API is reachable" run_id=bca322c9-e9a4-4377-bd83-60d1751879cb status=pass target=api.cloudflare.com:443
2026-08-13T18:04:34Z INF precheck complete hard_fail=false run_id=bca322c9-e9a4-4377-bd83-60d1751879cb suggested_protocol=quic
2026-08-13T18:04:34Z INF Registered tunnel connection connIndex=3 connection=10fdc923-5b2f-4baf-a394-0163566f9775 event=0 ip=198.41.200.13 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:04:13] Time: Fri Aug 14 02:04:13 AM CST 2026
[02:04:13] User: root (UID: 0)
[02:04:13] === STEP 1: 启动 API (端口 8450) ===
[02:04:16] API 已在运行
[02:04:16] API 状态: OK
[02:04:16] === STEP 2: 安装 cloudflared ===
[02:04:16] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:17] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:17] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:17] === STEP 3: 检查认证方式 ===
[02:04:17] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:17] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:17] 检查现有 tunnel...
[02:04:17] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax07, 2xlax08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[02:04:17] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:17] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:17] 凭证文件存在
[02:04:17] 创建 config.yml...
[02:04:17] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:17] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:19] DNS 路由结果: 2026-08-13T18:04:19Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:19] === STEP 5: 更新 DNS (API) ===
[02:04:19] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:20] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:04:21] 设置 SSL 模式为 Full...
SSL: 跳过
[02:04:22] === STEP 6: 启动 Tunnel ===
[02:04:25] 启动 Named Tunnel (cert 模式)...
[02:04:25] 使用 config: /root/.cloudflared/config.yml
[02:04:25] cloudflared PID: 1670991
[02:04:33] Tunnel 连接已建立!
[02:04:33] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T18:04:25Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T18:04:25Z INF Generated Connector ID: 9f0d273e-e7ed-4aea-b063-9f1284a64c23
2026-08-13T18:04:25Z INF Initial protocol quic
2026-08-13T18:04:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T18:04:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T18:04:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T18:04:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T18:04:25Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T18:04:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.193
2026-08-13T18:04:30Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-13T18:04:30Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.193
2026-08-13T18:04:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-13T18:04:32Z INF Registered tunnel connection connIndex=0 connection=fb4e486a-73cd-404f-bcef-7ed96da6d41d event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-13T18:04:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-13T18:04:32Z INF Registered tunnel connection connIndex=1 connection=ec3f3396-769f-4249-8027-3f0f123ac37f event=0 ip=198.41.200.43 location=lax01 protocol=quic
[02:04:33] === STEP 7: 持久化 ===
[02:04:36] systemd 服务已配置
[02:04:36] Cron 保活已设置
[02:04:36] === STEP 8: 验证 ===
[02:04:36] --- API (localhost:8450) ---
 OK
[02:04:36] --- cloudflared 进程 ---
root     1670991  1.0  1.8 1294676 37688 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1671191  0.0  1.3 1292484 27248 ?       Rl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:04:36] --- aishield.tools ---
 OK
[02:04:37] --- DNS CNAME ---
[02:04:37] --- DNS A ---
172.67.188.44
104.21.81.46
[02:04:38] === 部署汇总 ===
[02:04:38] Tunnel Mode: cert
[02:04:38] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:38] API: http://localhost:8450
[02:04:38] 域名: https://aishield.tools
[02:04:38] cloudflared: /usr/local/bin/cloudflared
[02:04:38] PID: 1670991
[02:04:38] Config: /root/.cloudflared/config.yml
[02:04:38] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:38] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-14 02:04:36 CST; 5h 23min ago
   Main PID: 1671183 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 18.2M
        CPU: 29.207s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1671183 /bin/bash /opt/start-tunnel.sh
             └─1671191 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 13 23:28:14 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786663694.6426954, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
