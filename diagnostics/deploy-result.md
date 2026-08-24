=== DIAGNOSTIC ===
Time: Tue Aug 25 07:11:46 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787613106.1842716, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3624021  0.1  1.0 1294676 21888 ?       Sl   02:03   0:26 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3624040  0.1  1.1 1294676 22296 ?       Sl   02:03   0:25 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3624297  0.1  1.0 1294676 21536 ?       Sl   02:03   0:26 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-24T18:03:10Z WRN Connection terminated error="failed to 2026-08-24T18:03:11Z INF +-------------------------------------------------------------------------------------+
2026-08-24T18:03:11Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-24T18:03:11Z INF +-------------------------------------------------------------------------------------+
2026-08-24T18:03:11Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-24T18:03:11Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-24T18:03:11Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-24T18:03:11Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-24T18:03:11Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-24T18:03:11Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-24T18:03:11Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-24T18:03:11Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-24T18:03:11Z INF |                                                                                     |
2026-08-24T18:03:11Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-24T18:03:11Z INF +-------------------------------------------------------------------------------------+
2026-08-24T18:03:11Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9865180d-8eaf-4e3b-b95d-b2aea2b14c59 status=pass target=region1.v2.argotunnel.com
2026-08-24T18:03:11Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9865180d-8eaf-4e3b-b95d-b2aea2b14c59 status=pass target=region2.v2.argotunnel.com
2026-08-24T18:03:11Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=9865180d-8eaf-4e3b-b95d-b2aea2b14c59 status=pass target=region1.v2.argotunnel.com
2026-08-24T18:03:11Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=9865180d-8eaf-4e3b-b95d-b2aea2b14c59 status=pass target=region2.v2.argotunnel.com
2026-08-24T18:03:11Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9865180d-8eaf-4e3b-b95d-b2aea2b14c59 status=pass target=region1.v2.argotunnel.com
2026-08-24T18:03:11Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9865180d-8eaf-4e3b-b95d-b2aea2b14c59 status=pass target=region2.v2.argotunnel.com
2026-08-24T18:03:11Z INF precheck component="Cloudflare API" details="API is reachable" run_id=9865180d-8eaf-4e3b-b95d-b2aea2b14c59 status=pass target=api.cloudflare.com:443
2026-08-24T18:03:11Z INF precheck complete hard_fail=false run_id=9865180d-8eaf-4e3b-b95d-b2aea2b14c59 suggested_protocol=quic
2026-08-24T21:33:33Z ERR  error="stream 13 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-24T21:33:33Z ERR Request failed error="stream 13 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.192.7 type=http
=0 ip=198.41.200.193
2026-08-24T18:03:12Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-24T18:03:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-24T18:03:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.13
2026-08-24T18:03:20Z INF Registered tunnel connection connIndex=3 connection=0a87d12c-5457-4f76-bf52-3e0a4aad08c5 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-24T18:03:20Z INF Registered tunnel connection connIndex=1 connection=5cd22252-6959-4d2f-812e-20ee57018494 event=0 ip=198.41.200.113 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:02:56] Time: Tue Aug 25 02:02:56 AM CST 2026
[02:02:56] User: root (UID: 0)
[02:02:56] === STEP 1: 启动 API (端口 8450) ===
[02:02:57] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 1xlax10, 1xlax11, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-24T18:02:57Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:02:57] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:02:57] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:02:57] 凭证文件存在
[02:02:57] 创建 config.yml...
[02:02:57] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:02:57] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:02:57] API 已在运行
[02:02:57] API 状态: OK
[02:02:57] === STEP 2: 安装 cloudflared ===
[02:02:57] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:02:57] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:02:57] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:02:57] === STEP 3: 检查认证方式 ===
[02:02:57] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:02:57] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:02:57] 检查现有 tunnel...
[02:02:58] DNS 路由结果: 2026-08-24T18:02:58Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:02:58] === STEP 5: 更新 DNS (API) ===
[02:02:58] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:02:58] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 1xlax10, 1xlax11, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[02:02:58] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:02:58] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:02:58] 凭证文件存在
[02:02:58] 创建 config.yml...
[02:02:58] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:02:58] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:02:58] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[02:02:59] DNS 路由结果: 2026-08-24T18:02:59Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:02:59] === STEP 5: 更新 DNS (API) ===
[02:02:59] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[02:03:00] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[02:03:00] 设置 SSL 模式为 Full...
DNS 更新: OK
[02:03:01] 设置 SSL 模式为 Full...
SSL: 跳过
[02:03:01] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[02:03:02] === STEP 6: 启动 Tunnel ===
[02:03:04] 启动 Named Tunnel (cert 模式)...
[02:03:04] 使用 config: /root/.cloudflared/config.yml
[02:03:04] cloudflared PID: 3624021
[02:03:05] 启动 Named Tunnel (cert 模式)...
[02:03:05] 使用 config: /root/.cloudflared/config.yml
[02:03:05] cloudflared PID: 3624040
[02:03:06] Tunnel 连接已建立!
[02:03:06] --- cloudflared 日志 (最后 15 行) ---
2026-08-24T18:03:05Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-24T18:03:05Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-24T18:03:05Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-24T18:03:05Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-24T18:03:05Z INF Generated Connector ID: 74990ff8-0968-4e59-87f4-9b6d98e2836e
2026-08-24T18:03:05Z INF Initial protocol quic
2026-08-24T18:03:05Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T18:03:05Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T18:03:05Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T18:03:05Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T18:03:05Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-24T18:03:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-24T18:03:05Z INF Registered tunnel connection connIndex=0 connection=cfb12e02-a6e5-4d2e-af9b-fb16f931a18e event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-24T18:03:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-24T18:03:06Z INF Registered tunnel connection connIndex=1 connection=0259e32d-9d6d-4cff-85e8-fd119f8f3f10 event=0 ip=198.41.192.7 location=lax12 protocol=quic
[02:03:06] === STEP 7: 持久化 ===
[02:03:07] Tunnel 连接已建立!
[02:03:07] --- cloudflared 日志 (最后 15 行) ---
2026-08-24T18:03:05Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-24T18:03:05Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-24T18:03:05Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-24T18:03:05Z INF Generated Connector ID: 74990ff8-0968-4e59-87f4-9b6d98e2836e
2026-08-24T18:03:05Z INF Initial protocol quic
2026-08-24T18:03:05Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T18:03:05Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T18:03:05Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T18:03:05Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T18:03:05Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-24T18:03:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-24T18:03:05Z INF Registered tunnel connection connIndex=0 connection=cfb12e02-a6e5-4d2e-af9b-fb16f931a18e event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-24T18:03:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-24T18:03:06Z INF Registered tunnel connection connIndex=1 connection=0259e32d-9d6d-4cff-85e8-fd119f8f3f10 event=0 ip=198.41.192.7 locat2026-08-24T18:03:06Z INF2026-08-24T18:03:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
2026-08-24T18:03:07Z INF Registered tunnel connection connIndex=2 connection=ba03f220-89e1-4925-a8ca-16a26b06c912 event=0 ip=198.41.192.47 location=lax12 protocol=quic
[02:03:07] === STEP 7: 持久化 ===
[02:03:07] systemd 服务已配置
[02:03:07] Cron 保活已设置
[02:03:07] === STEP 8: 验证 ===
[02:03:07] --- API (localhost:8450) ---
 OK
[02:03:07] --- cloudflared 进程 ---
root     3624021  3.0  1.8 1293844 36476 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3624040  5.0  1.8 1294676 37412 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3624190  0.0  1.7 1293844 34796 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:03:07] --- aishield.tools ---
[02:03:07] systemd 服务已配置
[02:03:07] Cron 保活已设置
[02:03:07] === STEP 8: 验证 ===
[02:03:07] --- API (localhost:8450) ---
 OK
[02:03:07] --- cloudflared 进程 ---
root     3624021  3.3  1.8 1294420 37828 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3624040  5.0  1.8 1294676 37296 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3624297  0.0  1.3 1292484 26544 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:03:07] --- aishield.tools ---
 OK
[02:03:09] --- DNS CNAME ---
 OK
[02:03:09] --- DNS CNAME ---
[02:03:09] --- DNS A ---
[02:03:09] --- DNS A ---
104.21.81.46
172.67.188.44
172.67.188.44
104.21.81.46
[02:03:09] === 部署汇总 ===
[02:03:09] === 部署汇总 ===
[02:03:09] Tunnel Mode: cert
[02:03:09] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:03:09] Tunnel Mode: cert
[02:03:09] API: http://localhost:8450
[02:03:09] 域名: https://aishield.tools
[02:03:09] cloudflared: /usr/local/bin/cloudflared
[02:03:09] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:03:09] PID: 3624040
[02:03:09] Config: /root/.cloudflared/config.yml
[02:03:09] API: http://localhost:8450
[02:03:09] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:03:09] 域名: https://aishield.tools
[02:03:09] 状态: Named Tunnel (cert 模式) 已配置
[02:03:09] cloudflared: /usr/local/bin/cloudflared
[02:03:09] PID: 3624021
[02:03:09] Config: /root/.cloudflared/config.yml
[02:03:09] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:03:09] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-25 02:03:07 CST; 5h 8min ago
   Main PID: 3624293 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 18.0M
        CPU: 27.006s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3624293 /bin/bash /opt/start-tunnel.sh
             └─3624297 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2525069,fd=3))                                                    
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
Time: Mon Aug 24 23:11:47 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787613107.7361498, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
