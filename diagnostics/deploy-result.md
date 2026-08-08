=== DIAGNOSTIC ===
Time: Sat Aug 8 07:17:01 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786187821.3127778, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     4045832  0.1  1.1 1294676 23604 ?       Sl   Aug07   2:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4045999  0.1  1.2 1294676 24600 ?       Sl   Aug07   2:04 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-07T13:10:39Z ERR Request failed error="stream 5 canceled by remote with error code 0" connIndex=0 dest=https://aishield.tools/ event=0 ip=198.41.192.27 type=http
2026-08-07T13:10:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-08-07T13:10:40Z INF Registered tunnel connection connIndex=3 connection=e803bf2c-8f1f-4ace-b17c-1741e09e4cef event=0 ip=198.41.192.57 location=lax10 protocol=quic
2026-08-07T13:10:43Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.73
2026-08-07T13:10:43Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.73
2026-08-07T13:10:43Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-07T13:10:44Z INF +-------------------------------------------------------------------------------------+
2026-08-07T13:10:44Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-07T13:10:44Z INF +-------------------------------------------------------------------------------------+
2026-08-07T13:10:44Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-07T13:10:44Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-07T13:10:44Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-07T13:10:44Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-07T13:10:44Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-07T13:10:44Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-07T13:10:44Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-07T13:10:44Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-07T13:10:44Z INF |                                                                                     |
2026-08-07T13:10:44Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-07T13:10:44Z INF +-------------------------------------------------------------------------------------+
2026-08-07T13:10:44Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=923a8e60-cea4-470b-9b22-34cddf779713 status=pass target=region1.v2.argotunnel.com
2026-08-07T13:10:44Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=923a8e60-cea4-470b-9b22-34cddf779713 status=pass target=region2.v2.argotunnel.com
2026-08-07T13:10:44Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=923a8e60-cea4-470b-9b22-34cddf779713 status=pass target=region1.v2.argotunnel.com
2026-08-07T13:10:44Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=923a8e60-cea4-470b-9b22-34cddf779713 status=pass target=region2.v2.argotunnel.com
2026-08-07T13:10:44Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=923a8e60-cea4-470b-9b22-34cddf779713 status=pass target=region1.v2.argotunnel.com
2026-08-07T13:10:44Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=923a8e60-cea4-470b-9b22-34cddf779713 status=pass target=region2.v2.argotunnel.com
2026-08-07T13:10:44Z INF precheck component="Cloudflare API" details="API is reachable" run_id=923a8e60-cea4-470b-9b22-34cddf779713 status=pass target=api.cloudflare.com:443
2026-08-07T13:10:44Z INF precheck complete hard_fail=false run_id=923a8e60-cea4-470b-9b22-34cddf779713 suggested_protocol=quic
2026-08-07T13:10:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-07T13:10:47Z INF Registered tunnel connection connIndex=1 connection=0e46b35d-608d-4e53-a37c-c94db44349b9 event=0 ip=198.41.200.43 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[21:05:45] Time: Fri Aug  7 09:05:45 PM CST 2026
[21:05:45] User: root (UID: 0)
[21:05:45] === STEP 1: 启动 API (端口 8450) ===
[21:07:15] API 已在运行
[21:07:15] API 状态: OK
[21:07:15] === STEP 2: 安装 cloudflared ===
[21:07:15] cloudflared 安装路径: /usr/local/bin/cloudflared
[21:07:15] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[21:07:15] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[21:07:15] === STEP 3: 检查认证方式 ===
[21:07:15] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[21:07:15] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[21:07:15] 检查现有 tunnel...
[21:07:16] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax08, 2xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[21:07:16] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[21:07:16] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[21:07:16] 凭证文件存在
[21:07:16] 创建 config.yml...
[21:07:16] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[21:07:16] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[21:07:18] DNS 路由结果: 2026-08-07T13:07:18Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[21:07:18] === STEP 5: 更新 DNS (API) ===
[21:07:18] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[21:07:19] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[21:07:19] 设置 SSL 模式为 Full...
SSL: 跳过
[21:07:20] === STEP 6: 启动 Tunnel ===
[21:07:23] 启动 Named Tunnel (cert 模式)...
[21:07:23] 使用 config: /root/.cloudflared/config.yml
[21:07:23] cloudflared PID: 4043063
[21:07:25] Tunnel 连接已建立!
[21:07:25] --- cloudflared 日志 (最后 15 行) ---
2026-08-07T13:07:23Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-07T13:07:23Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-07T13:07:23Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-07T13:07:23Z INF Generated Connector ID: 0af47f90-10b1-400f-9294-d2d0d59c5941
2026-08-07T13:07:23Z INF Initial protocol quic
2026-08-07T13:07:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T13:07:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T13:07:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T13:07:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T13:07:23Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-07T13:07:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-07T13:07:24Z INF Registered tunnel connection connIndex=0 connection=61e1e123-8bad-45cd-b37b-8cd64ad50a05 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-07T13:07:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-07T13:07:25Z INF Registered tunnel connection connIndex=1 connection=464ef52d-8f47-4290-8452-36d50d36a706 event=0 ip=198.41.192.67 location=lax05 protocol=quic
2026-08-07T13:07:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
[21:07:25] === STEP 7: 持久化 ===
[21:07:26] systemd 服务已配置
[21:07:26] Cron 保活已设置
[21:07:26] === STEP 8: 验证 ===
[21:07:26] --- API (localhost:8450) ---
 OK
[21:07:26] --- cloudflared 进程 ---
root     4043063  3.0  1.9 1359452 38588 ?       Sl   21:07   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4043155  0.0  1.3 1292740 26928 ?       Rl   21:07   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[21:07:26] --- aishield.tools ---
 OK
[21:07:28] --- DNS CNAME ---
[21:07:28] --- DNS A ---
104.21.81.46
172.67.188.44
[21:07:28] === 部署汇总 ===
[21:07:28] Tunnel Mode: cert
[21:07:28] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[21:07:28] API: http://localhost:8450
[21:07:28] 域名: https://aishield.tools
[21:07:28] cloudflared: /usr/local/bin/cloudflared
[21:07:28] PID: 4043063
[21:07:28] Config: /root/.cloudflared/config.yml
[21:07:28] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[21:07:28] 状态: Named Tunnel (cert 模式) 已配置
[21:10:25] API 已在运行
[21:10:25] API 状态: OK
[21:10:25] === STEP 2: 安装 cloudflared ===
[21:10:25] cloudflared 安装路径: /usr/local/bin/cloudflared
[21:10:25] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[21:10:26] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[21:10:26] === STEP 3: 检查认证方式 ===
[21:10:26] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[21:10:26] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[21:10:26] 检查现有 tunnel...
[21:10:27] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax07, 1xlax09, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[21:10:27] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[21:10:27] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[21:10:27] 凭证文件存在
[21:10:27] 创建 config.yml...
[21:10:27] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[21:10:27] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[21:10:29] DNS 路由结果: 2026-08-07T13:10:29Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[21:10:29] === STEP 5: 更新 DNS (API) ===
[21:10:29] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[21:10:31] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[21:10:31] 设置 SSL 模式为 Full...
SSL: 跳过
[21:10:34] === STEP 6: 启动 Tunnel ===
[21:10:37] 启动 Named Tunnel (cert 模式)...
[21:10:37] 使用 config: /root/.cloudflared/config.yml
[21:10:37] cloudflared PID: 4045832
[21:10:39] Tunnel 连接已建立!
[21:10:39] --- cloudflared 日志 (最后 15 行) ---
2026-08-07T13:10:37Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-07T13:10:37Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-07T13:10:37Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-07T13:10:37Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-07T13:10:37Z INF Generated Connector ID: d15c9cf8-08b1-4c7c-bc47-35fb0b1d9934
2026-08-07T13:10:37Z INF Initial protocol quic
2026-08-07T13:10:37Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T13:10:37Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T13:10:37Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T13:10:37Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T13:10:37Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-07T13:10:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-07T13:10:38Z INF Registered tunnel connection connIndex=0 connection=fb66bb9d-9099-4139-a905-6ab3fab521ac event=0 ip=198.41.192.27 location=lax09 protocol=quic
2026-08-07T13:10:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
2026-08-07T13:10:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
[21:10:39] === STEP 7: 持久化 ===
[21:10:39] systemd 服务已配置
[21:10:39] Cron 保活已设置
[21:10:39] === STEP 8: 验证 ===
[21:10:39] --- API (localhost:8450) ---
 OK
[21:10:39] --- cloudflared 进程 ---
root     4045832  5.0  1.9 1294676 39032 ?       Sl   21:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4045999  0.0  1.3 1292740 27812 ?       Rl   21:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[21:10:39] --- aishield.tools ---
 OK
[21:10:40] --- DNS CNAME ---
[21:10:41] --- DNS A ---
172.67.188.44
104.21.81.46
[21:10:41] === 部署汇总 ===
[21:10:41] Tunnel Mode: cert
[21:10:41] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[21:10:41] API: http://localhost:8450
[21:10:41] 域名: https://aishield.tools
[21:10:41] cloudflared: /usr/local/bin/cloudflared
[21:10:41] PID: 4045832
[21:10:41] Config: /root/.cloudflared/config.yml
[21:10:41] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[21:10:41] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-07 21:10:39 CST; 22h ago
   Main PID: 4045998 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 23.3M
        CPU: 2min 4.962s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─4045998 /bin/bash /opt/start-tunnel.sh
             └─4045999 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sat Aug  8 11:17:01 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786187821.730427, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
