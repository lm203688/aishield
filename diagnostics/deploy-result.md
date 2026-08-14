=== DIAGNOSTIC ===
Time: Fri Aug 14 11:17:00 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786677420.7643466, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1963575  0.1  1.7 1294676 35336 ?       Sl   09:34   0:09 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1963594  0.1  1.7 1294676 35276 ?       Sl   09:34   0:09 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1963822  0.1  1.7 1294676 34984 ?       Sl   09:34   0:09 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T01:34:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-14T01:34:31Z INF Registered tunnel connection connIndex=2 connection=7517fd38-6b2b-4c19-92e6-fb16f61ebf15 event=0 ip=198.41.192.67 location=lax09 protocol=quic
22026-08-14T01:34:32Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.22026-08-14T01:34:34Z INF +-------------------------------------------------------------------------------------+
2026-08-14T01:34:34Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-14T01:34:34Z INF +-------------------------------------------------------------------------------------+
2026-08-14T01:34:34Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-14T01:34:34Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T01:34:34Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T01:34:34Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T01:34:34Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T01:34:34Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T01:34:34Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T01:34:34Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-14T01:34:34Z INF |                                                                                     |
2026-08-14T01:34:34Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-14T01:34:34Z INF +-------------------------------------------------------------------------------------+
2026-08-14T01:34:34Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cd278c71-6c53-4e27-9393-f25d8ae69fe0 status=pass target=region1.v2.argotunnel.com
2026-08-14T01:34:34Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cd278c71-6c53-4e27-9393-f25d8ae69fe0 status=pass target=region2.v2.argotunnel.com
2026-08-14T01:34:34Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cd278c71-6c53-4e27-9393-f25d8ae69fe0 status=pass target=region1.v2.argotunnel.com
2026-08-14T01:34:34Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cd278c71-6c53-4e27-9393-f25d8ae69fe0 status=pass target=region2.v2.argotunnel.com
2026-08-14T01:34:34Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cd278c71-6c53-4e27-9393-f25d8ae69fe0 status=pass target=region1.v2.argotunnel.com
2026-08-14T01:34:34Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cd278c71-6c53-4e27-9393-f25d8ae69fe0 status=pass target=region2.v2.argotunnel.com
2026-08-14T01:34:34Z INF precheck component="Cloudflare API" details="API is reachable" run_id=cd278c71-6c53-4e27-9393-f25d8ae69fe0 status=pass target=api.cloudflare.com:443
2026-08-14T01:34:34Z INF precheck complete hard_fail=false run_id=cd278c71-6c53-4e27-9393-f25d8ae69fe0 suggested_protocol=quic
etails="API is reachable" run_id=8886e271-8072-43be-bdd8-2467ace93b0f status=pass target=api.cloudflare.com:443
2026-08-14T01:34:34Z INF precheck complete hard_fail=false run_id=8886e271-8072-43be-bdd8-2467ace93b0f suggested_protocol=quic
2026-08-14T01:34:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-14T01:34:41Z INF Registered tunnel connection connIndex=2 connection=94488371-fdae-4c34-9aca-14f8eac70e55 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-14T01:34:51Z ERR  error="stream 5 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-14T01:34:51Z ERR Request failed error="stream 5 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.192.227 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[09:34:12] Time: Fri Aug 14 09:34:12 AM CST 2026
[09:34:12] User: root (UID: 0)
[09:34:12] === STEP 1: 启动 API (端口 8450) ===
[09:34:13] API 已在运行
[09:34:13] API 状态: OK
[09:34:13] === STEP 2: 安装 cloudflared ===
[09:34:13] cloudflared 安装路径: /usr/local/bin/cloudflared
[09:34:13] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:34:13] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:34:13] === STEP 3: 检查认证方式 ===
[09:34:13] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:34:13] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:34:13] 检查现有 tunnel...
[09:34:13] API 已在运行
[09:34:13] API 状态: OK
[09:34:13] === STEP 2: 安装 cloudflared ===
[09:34:13] cloudflared 安装路径: /usr/local/bin/cloudflared
[09:34:13] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:34:13] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:34:13] === STEP 3: 检查认证方式 ===
[09:34:13] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:34:13] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:34:13] 检查现有 tunnel...
[09:34:15] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax05, 1xlax07, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[09:34:15] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:34:15] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[09:34:15] 凭证文件存在
[09:34:15] 创建 config.yml...
[09:34:15] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[09:34:15] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:34:17] DNS 路由结果: 2026-08-14T01:34:17Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[09:34:17] === STEP 5: 更新 DNS (API) ===
[09:34:17] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:34:17] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax05, 1xlax07, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[09:34:17] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:34:17] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[09:34:17] 凭证文件存在
[09:34:17] 创建 config.yml...
[09:34:17] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[09:34:17] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:34:20] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[09:34:20] DNS 路由结果: 2026-08-14T01:34:20Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[09:34:20] === STEP 5: 更新 DNS (API) ===
[09:34:20] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:34:20] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[09:34:21] 设置 SSL 模式为 Full...
DNS 更新: OK
[09:34:22] 设置 SSL 模式为 Full...
SSL: 跳过
[09:34:22] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[09:34:23] === STEP 6: 启动 Tunnel ===
[09:34:25] 启动 Named Tunnel (cert 模式)...
[09:34:25] 使用 config: /root/.cloudflared/config.yml
[09:34:25] cloudflared PID: 1963575
[09:34:26] 启动 Named Tunnel (cert 模式)...
[09:34:26] 使用 config: /root/.cloudflared/config.yml
[09:34:26] cloudflared PID: 1963594
[09:34:27] Tunnel 连接已建立!
[09:34:27] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T01:34:26Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-14T01:34:26Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-14T01:34:26Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-14T01:34:26Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T01:34:26Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T01:34:26Z INF Generated Connector ID: daf7a9e3-43f6-44ba-b68c-fcb87656fb57
2026-08-14T01:34:26Z INF Initial protocol quic
2026-08-14T01:34:26Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T01:34:26Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T01:34:26Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T01:34:26Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T01:34:26Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-14T01:34:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
                                                                                                                                                                                                                                                                                                                    2026-08-14T01:34:27Z INF Registered tunnel connection connIndex=1 connection=9342fb1e-7fe2-43fa-8311-3b51f0e13be0 event=0 ip=198.41.192.77 location=lax07 protocol=quic
2026-08-14T01:34:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
[09:34:27] === STEP 7: 持久化 ===
[09:34:28] systemd 服务已配置
[09:34:28] Cron 保活已设置
[09:34:28] === STEP 8: 验证 ===
[09:34:28] --- API (localhost:8450) ---
 OK
[09:34:28] --- cloudflared 进程 ---
root     1963575  3.0  1.9 1294676 38700 ?       Sl   09:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1963594  3.5  1.8 1294100 36920 ?       Sl   09:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1963699  0.0  1.3 1292740 27084 ?       Rl   09:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[09:34:28] --- aishield.tools ---
[09:34:28] Tunnel 连接已建立!
[09:34:28] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T01:34:26Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-14T01:34:26Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-14T01:34:26Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T01:34:26Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T01:34:26Z INF Generated Connector ID: daf7a9e3-43f6-44ba-b68c-fcb87656fb57
2026-08-14T01:34:26Z INF Initial protocol quic
2026-08-14T01:34:26Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T01:34:26Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T01:34:26Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T01:34:26Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T01:34:26Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-14T01:34:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
                                                                                                                                                                                                                                                                                                                    2026-08-14T01:34:27Z INF Registered tunnel connection connIndex=1 connection=9342fb1e-7fe2-43fa-8311-3b51f0e13be0 event=0 ip=198.41.192.77 location=lax07 protocol=quic
2026-08-14T01:34:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
2026-08-14T01:34:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.227
[09:34:28] === STEP 7: 持久化 ===
[09:34:29] systemd 服务已配置
[09:34:29] Cron 保活已设置
[09:34:29] === STEP 8: 验证 ===
[09:34:29] --- API (localhost:8450) ---
 OK
[09:34:29] --- cloudflared 进程 ---
root     1963575  2.5  1.9 1294676 38716 ?       Sl   09:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1963594  2.6  1.8 1294100 36968 ?       Sl   09:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1963822  0.0  1.3 1292740 27120 ?       Rl   09:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[09:34:29] --- aishield.tools ---
 OK
[09:34:29] --- DNS CNAME ---
[09:34:30] --- DNS A ---
104.21.81.46
172.67.188.44
[09:34:30] === 部署汇总 ===
[09:34:30] Tunnel Mode: cert
[09:34:30] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:34:30] API: http://localhost:8450
[09:34:30] 域名: https://aishield.tools
[09:34:30] cloudflared: /usr/local/bin/cloudflared
[09:34:30] PID: 1963575
[09:34:30] Config: /root/.cloudflared/config.yml
[09:34:30] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:34:30] 状态: Named Tunnel (cert 模式) 已配置
 FAIL (DNS 传播中或配置错误)
[09:34:34] --- DNS CNAME ---
[09:34:34] --- DNS A ---
104.21.81.46
172.67.188.44
[09:34:34] === 部署汇总 ===
[09:34:34] Tunnel Mode: cert
[09:34:34] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:34:34] API: http://localhost:8450
[09:34:34] 域名: https://aishield.tools
[09:34:34] cloudflared: /usr/local/bin/cloudflared
[09:34:34] PID: 1963594
[09:34:34] Config: /root/.cloudflared/config.yml
[09:34:34] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:34:34] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-14 09:34:29 CST; 1h 42min ago
   Main PID: 1963818 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 16.6M
        CPU: 9.699s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1963818 /bin/bash /opt/start-tunnel.sh
             └─1963822 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 03:17:01 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786677421.4463265, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
