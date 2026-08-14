=== DIAGNOSTIC ===
Time: Sat Aug 15 07:09:54 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786748994.7002087, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2790931  0.1  1.6 1294676 32472 ?       Sl   06:25   0:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2791049  0.1  1.6 1294676 33212 ?       Sl   06:25   0:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T22:25:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-14T22:25:49Z INF Registered tunnel connection connIndex=1 connection=cf8dbb5d-2f01-4079-839e-4ea56a1b4645 event=0 ip=198.41.192.67 location=lax05 protocol=quic
2026-08-14T22:25:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-14T22:25:50Z INF Registered tunnel connection connIndex=2 connection=d3e38142-3101-468d-a41a-9d3152ed311e event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-14T22:25:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.227
2026-08-14T22:25:51Z INF Registered tunnel connection connIndex=3 connection=ef51bf32-556e-477b-8b80-e0c536238c03 event=0 ip=198.41.192.227 location=lax05 protocol=quic
2026-08-14T22:25:55Z INF +-------------------------------------------------------------------------------------+
2026-08-14T22:25:55Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-14T22:25:55Z INF +-------------------------------------------------------------------------------------+
2026-08-14T22:25:55Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-14T22:25:55Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T22:25:55Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T22:25:55Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T22:25:55Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T22:25:55Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T22:25:55Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T22:25:55Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-14T22:25:55Z INF |                                                                                     |
2026-08-14T22:25:55Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-14T22:25:55Z INF +-------------------------------------------------------------------------------------+
2026-08-14T22:25:55Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=4c881541-0839-4f93-8070-fde8143e56e4 status=pass target=region1.v2.argotunnel.com
2026-08-14T22:25:55Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=4c881541-0839-4f93-8070-fde8143e56e4 status=pass target=region2.v2.argotunnel.com
2026-08-14T22:25:55Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=4c881541-0839-4f93-8070-fde8143e56e4 status=pass target=region1.v2.argotunnel.com
2026-08-14T22:25:55Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=4c881541-0839-4f93-8070-fde8143e56e4 status=pass target=region2.v2.argotunnel.com
2026-08-14T22:25:55Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4c881541-0839-4f93-8070-fde8143e56e4 status=pass target=region1.v2.argotunnel.com
2026-08-14T22:25:55Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4c881541-0839-4f93-8070-fde8143e56e4 status=pass target=region2.v2.argotunnel.com
2026-08-14T22:25:55Z INF precheck component="Cloudflare API" details="API is reachable" run_id=4c881541-0839-4f93-8070-fde8143e56e4 status=pass target=api.cloudflare.com:443
2026-08-14T22:25:55Z INF precheck complete hard_fail=false run_id=4c881541-0839-4f93-8070-fde8143e56e4 suggested_protocol=quic
2026-08-14T22:26:04Z ERR  error="stream 17 canceled by remote with error code 0" connIndex=0 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-14T22:26:04Z ERR Request failed error="stream 17 canceled by remote with error code 0" connIndex=0 dest=https://aishield.tools/ event=0 ip=198.41.200.113 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[06:25:40] Time: Sat Aug 15 06:25:40 AM CST 2026
[06:25:40] User: root (UID: 0)
[06:25:40] === STEP 1: 启动 API (端口 8450) ===
[06:25:42] API 已在运行
[06:25:42] API 状态: OK
[06:25:42] === STEP 2: 安装 cloudflared ===
[06:25:42] cloudflared 安装路径: /usr/local/bin/cloudflared
[06:25:42] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:25:42] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:25:42] === STEP 3: 检查认证方式 ===
[06:25:42] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[06:25:42] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[06:25:42] 检查现有 tunnel...
[06:25:42] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[06:25:42] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:25:42] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[06:25:42] 凭证文件存在
[06:25:42] 创建 config.yml...
[06:25:42] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[06:25:42] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:25:43] DNS 路由结果: 2026-08-14T22:25:43Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[06:25:43] === STEP 5: 更新 DNS (API) ===
[06:25:43] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:25:44] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[06:25:45] 设置 SSL 模式为 Full...
SSL: 跳过
[06:25:45] === STEP 6: 启动 Tunnel ===
[06:25:48] 启动 Named Tunnel (cert 模式)...
[06:25:48] 使用 config: /root/.cloudflared/config.yml
[06:25:48] cloudflared PID: 2790931
[06:25:50] Tunnel 连接已建立!
[06:25:50] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T22:25:48Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T22:25:48Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T22:25:48Z INF Generated Connector ID: 9339236c-2ba2-4a75-8852-7e06006575a9
2026-08-14T22:25:48Z INF Initial protocol quic
2026-08-14T22:25:48Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T22:25:48Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T22:25:48Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T22:25:48Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T22:25:48Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-14T22:25:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-14T22:25:49Z INF Registered tunnel connection connIndex=0 connection=147d592f-4563-458f-9c3b-5ad1cd7f459b event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-14T22:25:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-14T22:25:49Z INF Registered tunnel connection connIndex=1 connection=cf8dbb5d-2f01-4079-839e-4ea56a1b4645 event=0 ip=198.41.192.67 location=lax05 protocol=quic
2026-08-14T22:25:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-14T22:25:50Z INF Registered tunnel connection connIndex=2 connection=d3e38142-3101-468d-a41a-9d3152ed311e event=0 ip=198.41.200.23 location=lax01 protocol=quic
[06:25:50] === STEP 7: 持久化 ===
[06:25:51] systemd 服务已配置
[06:25:51] Cron 保活已设置
[06:25:51] === STEP 8: 验证 ===
[06:25:51] --- API (localhost:8450) ---
 OK
[06:25:51] --- cloudflared 进程 ---
root     2790931  3.0  1.9 1294676 39004 ?       Sl   06:25   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2791049  0.0  1.3 1292740 27496 ?       Sl   06:25   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[06:25:51] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[06:25:52] --- DNS CNAME ---
[06:25:52] --- DNS A ---
172.67.188.44
104.21.81.46
[06:25:52] === 部署汇总 ===
[06:25:52] Tunnel Mode: cert
[06:25:52] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:25:52] API: http://localhost:8450
[06:25:52] 域名: https://aishield.tools
[06:25:52] cloudflared: /usr/local/bin/cloudflared
[06:25:52] PID: 2790931
[06:25:52] Config: /root/.cloudflared/config.yml
[06:25:52] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:25:52] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-15 06:25:51 CST; 44min ago
   Main PID: 2791041 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 16.9M
        CPU: 3.744s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2791041 /bin/bash /opt/start-tunnel.sh
             └─2791049 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 23:09:55 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786748995.2575903, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
