=== DIAGNOSTIC ===
Time: Thu Aug 20 04:11:21 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787170281.5284874, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3123299  0.1  1.7 1294676 35900 ?       Sl   02:05   0:11 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3123430  0.1  1.7 1294676 35788 ?       Sl   02:05   0:10 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-19T18:05:15Z INF Registered tunnel connection connIndex=3 connection=639e139a-4606-4de2-876c-6cd12b1d0f69 event=0 ip=198.41.192.67 location=lax09 protocol=quic
2026-08-19T18:05:18Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.73
2026-08-19T18:05:18Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.73
2026-08-19T18:05:18Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-19T18:05:19Z INF +-------------------------------------------------------------------------------------+
2026-08-19T18:05:19Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-19T18:05:19Z INF +-------------------------------------------------------------------------------------+
2026-08-19T18:05:19Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-19T18:05:19Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-19T18:05:19Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-19T18:05:19Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-19T18:05:19Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-19T18:05:19Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-19T18:05:19Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-19T18:05:19Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-19T18:05:19Z INF |                                                                                     |
2026-08-19T18:05:19Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-19T18:05:19Z INF +-------------------------------------------------------------------------------------+
2026-08-19T18:05:19Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=37127bf3-a802-4a60-a6dc-88113a146129 status=pass target=region1.v2.argotunnel.com
2026-08-19T18:05:19Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=37127bf3-a802-4a60-a6dc-88113a146129 status=pass target=region2.v2.argotunnel.com
2026-08-19T18:05:19Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=37127bf3-a802-4a60-a6dc-88113a146129 status=pass target=region1.v2.argotunnel.com
2026-08-19T18:05:19Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=37127bf3-a802-4a60-a6dc-88113a146129 status=pass target=region2.v2.argotunnel.com
2026-08-19T18:05:19Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=37127bf3-a802-4a60-a6dc-88113a146129 status=pass target=region1.v2.argotunnel.com
2026-08-19T18:05:19Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=37127bf3-a802-4a60-a6dc-88113a146129 status=pass target=region2.v2.argotunnel.com
2026-08-19T18:05:19Z INF precheck component="Cloudflare API" details="API is reachable" run_id=37127bf3-a802-4a60-a6dc-88113a146129 status=pass target=api.cloudflare.com:443
2026-08-19T18:05:19Z INF precheck complete hard_fail=false run_id=37127bf3-a802-4a60-a6dc-88113a146129 suggested_protocol=quic
2026-08-19T18:05:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-19T18:05:22Z INF Registered tunnel connection connIndex=1 connection=6063827b-fe0f-4baa-a480-cbaad222ad85 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-19T18:40:08Z ERR  error="stream 13 canceled by remote with error code 0" connIndex=0 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-19T18:40:08Z ERR Request failed error="stream 13 canceled by remote with error code 0" connIndex=0 dest=https://aishield.tools/ event=0 ip=198.41.192.167 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:03:37] Time: Thu Aug 20 02:03:37 AM CST 2026
[02:03:37] User: root (UID: 0)
[02:03:37] === STEP 1: 启动 API (端口 8450) ===
[02:04:10] API 已在运行
[02:04:10] API 状态: OK
[02:04:10] === STEP 2: 安装 cloudflared ===
[02:04:10] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:10] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:10] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:10] === STEP 3: 检查认证方式 ===
[02:04:10] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:10] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:10] 检查现有 tunnel...
[02:04:11] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax08, 1xlax10, 1xlax11, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-19T18:04:11Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:04:11] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:11] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:11] 凭证文件存在
[02:04:11] 创建 config.yml...
[02:04:11] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:11] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:12] DNS 路由结果: 2026-08-19T18:04:12Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:12] === STEP 5: 更新 DNS (API) ===
[02:04:12] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:13] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:04:13] 设置 SSL 模式为 Full...
SSL: 跳过
[02:04:14] === STEP 6: 启动 Tunnel ===
[02:04:17] 启动 Named Tunnel (cert 模式)...
[02:04:17] 使用 config: /root/.cloudflared/config.yml
[02:04:17] cloudflared PID: 3122276
[02:04:19] Tunnel 连接已建立!
[02:04:19] --- cloudflared 日志 (最后 15 行) ---
2026-08-19T18:04:17Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-19T18:04:17Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-19T18:04:17Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-19T18:04:17Z INF Generated Connector ID: 5fd2090b-d8e9-4af3-bba4-da237b543e35
2026-08-19T18:04:17Z INF Initial protocol quic
2026-08-19T18:04:17Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T18:04:17Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T18:04:17Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T18:04:17Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T18:04:17Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-19T18:04:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-19T18:04:18Z INF Registered tunnel connection connIndex=0 connection=7dbc5e66-84d4-4292-a28c-49954a034231 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-19T18:04:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-19T18:04:18Z INF Registered tunnel connection connIndex=1 connection=52aa9dda-9423-464a-bd26-c358e785e900 event=0 ip=198.41.192.27 location=lax09 protocol=quic
2026-08-19T18:04:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
[02:04:19] === STEP 7: 持久化 ===
[02:04:20] systemd 服务已配置
[02:04:20] Cron 保活已设置
[02:04:20] === STEP 8: 验证 ===
[02:04:20] --- API (localhost:8450) ---
 OK
[02:04:20] --- cloudflared 进程 ---
root     3122276  3.3  1.9 1294676 38968 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3122433  0.0  1.1 1292484 22748 ?       Rl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:04:20] --- aishield.tools ---
 OK
[02:04:21] --- DNS CNAME ---
[02:04:22] --- DNS A ---
104.21.81.46
172.67.188.44
[02:04:22] === 部署汇总 ===
[02:04:22] Tunnel Mode: cert
[02:04:22] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:22] API: http://localhost:8450
[02:04:22] 域名: https://aishield.tools
[02:04:22] cloudflared: /usr/local/bin/cloudflared
[02:04:22] PID: 3122276
[02:04:22] Config: /root/.cloudflared/config.yml
[02:04:22] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:22] 状态: Named Tunnel (cert 模式) 已配置
[02:05:05] API 已在运行
[02:05:05] API 状态: OK
[02:05:05] === STEP 2: 安装 cloudflared ===
[02:05:05] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:05:05] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:05:05] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:05:05] === STEP 3: 检查认证方式 ===
[02:05:05] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:05:05] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:05:05] 检查现有 tunnel...
[02:05:06] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax07, 2xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-19T18:05:06Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:05:06] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:05:06] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:05:06] 凭证文件存在
[02:05:06] 创建 config.yml...
[02:05:06] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:05:06] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:05:07] DNS 路由结果: 2026-08-19T18:05:07Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:05:07] === STEP 5: 更新 DNS (API) ===
[02:05:07] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:05:08] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:05:08] 设置 SSL 模式为 Full...
SSL: 跳过
[02:05:09] === STEP 6: 启动 Tunnel ===
[02:05:12] 启动 Named Tunnel (cert 模式)...
[02:05:12] 使用 config: /root/.cloudflared/config.yml
[02:05:12] cloudflared PID: 3123299
[02:05:14] Tunnel 连接已建立!
[02:05:14] --- cloudflared 日志 (最后 15 行) ---
2026-08-19T18:05:12Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-19T18:05:12Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-19T18:05:12Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-19T18:05:12Z INF Generated Connector ID: b34304b7-0b36-4870-8a1b-6e3e42339006
2026-08-19T18:05:12Z INF Initial protocol quic
2026-08-19T18:05:12Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T18:05:12Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T18:05:12Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T18:05:12Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T18:05:12Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-19T18:05:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-19T18:05:13Z INF Registered tunnel connection connIndex=0 connection=ba4af035-f2b1-4025-8c70-4ff2e29da682 event=0 ip=198.41.192.167 location=lax07 protocol=quic
2026-08-19T18:05:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
2026-08-19T18:05:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-08-19T18:05:14Z INF Registered tunnel connection connIndex=2 connection=3c7243fb-3b08-4f37-9f29-5d8ac7ca19c4 event=0 ip=198.41.200.233 location=lax01 protocol=quic
[02:05:14] === STEP 7: 持久化 ===
[02:05:15] systemd 服务已配置
[02:05:15] Cron 保活已设置
[02:05:15] === STEP 8: 验证 ===
[02:05:15] --- API (localhost:8450) ---
 OK
[02:05:15] --- cloudflared 进程 ---
root     3123299  2.6  1.9 1294092 38668 ?       Sl   02:05   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3123430  0.0  1.3 1292484 27392 ?       Rl   02:05   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:05:15] --- aishield.tools ---
 OK
[02:05:16] --- DNS CNAME ---
[02:05:16] --- DNS A ---
172.67.188.44
104.21.81.46
[02:05:16] === 部署汇总 ===
[02:05:16] Tunnel Mode: cert
[02:05:16] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:05:16] API: http://localhost:8450
[02:05:16] 域名: https://aishield.tools
[02:05:16] cloudflared: /usr/local/bin/cloudflared
[02:05:16] PID: 3123299
[02:05:16] Config: /root/.cloudflared/config.yml
[02:05:16] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:05:16] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-20 02:05:15 CST; 2h 6min ago
   Main PID: 3123425 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.4M
        CPU: 10.955s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3123425 /bin/bash /opt/start-tunnel.sh
             └─3123430 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 19 20:11:21 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787170282.1574278, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
