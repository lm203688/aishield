=== DIAGNOSTIC ===
Time: Thu Aug 20 06:16:23 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787220983.6076963, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3693563  0.1  1.5 1294676 31560 ?       Sl   16:34   0:09 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3693668  0.1  1.5 1294676 31792 ?       Sl   16:34   0:09 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-20T08:34:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-20T08:34:10Z INF Registered tunnel connection connIndex=1 connection=87e73d80-eaa6-4571-9fc8-c4949b2b5ad1 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-20T08:34:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
2026-08-20T08:34:11Z INF Registered tunnel connection connIndex=2 connection=ae13ffaf-7798-403f-b2ed-c24ace937f6b event=0 ip=198.41.192.47 location=lax10 protocol=quic
2026-08-20T08:34:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.53
2026-08-20T08:34:12Z INF Registered tunnel connection connIndex=3 connection=9d6eee37-841f-458e-bcf4-844faee930bd event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-20T08:34:16Z INF +-------------------------------------------------------------------------------------+
2026-08-20T08:34:16Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-20T08:34:16Z INF +-------------------------------------------------------------------------------------+
2026-08-20T08:34:16Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-20T08:34:16Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-20T08:34:16Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-20T08:34:16Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-20T08:34:16Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-20T08:34:16Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-20T08:34:16Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-20T08:34:16Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-20T08:34:16Z INF |                                                                                     |
2026-08-20T08:34:16Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-20T08:34:16Z INF +-------------------------------------------------------------------------------------+
2026-08-20T08:34:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8e3058fd-8bc7-4358-92d3-72f395ff4b23 status=pass target=region1.v2.argotunnel.com
2026-08-20T08:34:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8e3058fd-8bc7-4358-92d3-72f395ff4b23 status=pass target=region2.v2.argotunnel.com
2026-08-20T08:34:16Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8e3058fd-8bc7-4358-92d3-72f395ff4b23 status=pass target=region1.v2.argotunnel.com
2026-08-20T08:34:16Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8e3058fd-8bc7-4358-92d3-72f395ff4b23 status=pass target=region2.v2.argotunnel.com
2026-08-20T08:34:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8e3058fd-8bc7-4358-92d3-72f395ff4b23 status=pass target=region1.v2.argotunnel.com
2026-08-20T08:34:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8e3058fd-8bc7-4358-92d3-72f395ff4b23 status=pass target=region2.v2.argotunnel.com
2026-08-20T08:34:16Z INF precheck component="Cloudflare API" details="API is reachable" run_id=8e3058fd-8bc7-4358-92d3-72f395ff4b23 status=pass target=api.cloudflare.com:443
2026-08-20T08:34:16Z INF precheck complete hard_fail=false run_id=8e3058fd-8bc7-4358-92d3-72f395ff4b23 suggested_protocol=quic
2026-08-20T09:38:37Z ERR  error="stream 37 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-20T09:38:37Z ERR Request failed error="stream 37 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.200.63 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:29:21] Time: Thu Aug 20 04:29:21 PM CST 2026
[16:29:21] User: root (UID: 0)
[16:29:21] === STEP 1: 启动 API (端口 8450) ===
[16:31:32] API 已在运行
[16:31:32] API 状态: OK
[16:31:32] === STEP 2: 安装 cloudflared ===
[16:31:32] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:31:32] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:31:32] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:31:32] === STEP 3: 检查认证方式 ===
[16:31:32] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:31:32] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:31:32] 检查现有 tunnel...
[16:31:33] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax09, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[16:31:33] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:31:33] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:31:33] 凭证文件存在
[16:31:33] 创建 config.yml...
[16:31:33] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:31:33] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:31:36] DNS 路由结果: 2026-08-20T08:31:36Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:31:36] === STEP 5: 更新 DNS (API) ===
[16:31:36] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:31:38] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:31:39] 设置 SSL 模式为 Full...
SSL: 跳过
[16:31:40] === STEP 6: 启动 Tunnel ===
[16:31:43] 启动 Named Tunnel (cert 模式)...
[16:31:43] 使用 config: /root/.cloudflared/config.yml
[16:31:43] cloudflared PID: 3691343
[16:31:45] Tunnel 连接已建立!
[16:31:45] --- cloudflared 日志 (最后 15 行) ---
2026-08-20T08:31:43Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-20T08:31:43Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-20T08:31:43Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-20T08:31:43Z INF Generated Connector ID: 4a9c9dea-2709-4ac5-9b88-8cdbf49dc806
2026-08-20T08:31:43Z INF Initial protocol quic
2026-08-20T08:31:43Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:31:43Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:31:43Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:31:43Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:31:43Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-20T08:31:43Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-20T08:31:44Z INF Registered tunnel connection connIndex=0 connection=aa67f417-7dc3-457d-bd45-3ec074ec0464 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-20T08:31:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
2026-08-20T08:31:44Z INF Registered tunnel connection connIndex=1 connection=a27836d8-487d-4a3c-b7bb-017104a0df15 event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-08-20T08:31:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
[16:31:45] === STEP 7: 持久化 ===
[16:31:45] systemd 服务已配置
[16:31:45] Cron 保活已设置
[16:31:45] === STEP 8: 验证 ===
[16:31:45] --- API (localhost:8450) ---
 OK
[16:31:45] --- cloudflared 进程 ---
root     3691343  4.5  1.9 1293836 38244 ?       Sl   16:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3691471  0.0  1.3 1292740 27328 ?       Rl   16:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:31:45] --- aishield.tools ---
 OK
[16:31:47] --- DNS CNAME ---
[16:31:47] --- DNS A ---
104.21.81.46
172.67.188.44
[16:31:47] === 部署汇总 ===
[16:31:47] Tunnel Mode: cert
[16:31:47] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:31:47] API: http://localhost:8450
[16:31:47] 域名: https://aishield.tools
[16:31:47] cloudflared: /usr/local/bin/cloudflared
[16:31:47] PID: 3691343
[16:31:47] Config: /root/.cloudflared/config.yml
[16:31:47] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:31:47] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-20 16:34:12 CST; 1h 42min ago
   Main PID: 3693660 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 16.1M
        CPU: 9.909s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3693660 /bin/bash /opt/start-tunnel.sh
             └─3693668 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 20 10:16:24 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787220984.2991967, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
