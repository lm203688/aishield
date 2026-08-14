=== DIAGNOSTIC ===
Time: Sat Aug 15 04:18:24 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786738704.5057366, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2610912  0.1  1.5 1294676 32004 ?       Sl   02:01   0:12 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2611012  0.1  1.6 1294676 32640 ?       Sl   02:01   0:13 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T18:01:11Z INF Registered tunnel connection connIndex=2 connection=26cd7a1f-8ada-4139-90bf-bca9a02b65de event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-14T18:01:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.67
2026-08-14T18:01:12Z INF Registered tunnel connection connIndex=3 connection=343ba16b-a942-4011-8b8e-bc4498a7e8fa event=0 ip=198.41.192.67 location=lax10 protocol=quic
2026-08-14T18:01:19Z INF +-----------------------------------------------------------------------------------------------+
2026-08-14T18:01:19Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-14T18:01:19Z INF +-----------------------------------------------------------------------------------------------+
2026-08-14T18:01:19Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-14T18:01:19Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-14T18:01:19Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-14T18:01:19Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-14T18:01:19Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-14T18:01:19Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-14T18:01:19Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-14T18:01:19Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-14T18:01:19Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-14T18:01:19Z INF |                                                                                               |
2026-08-14T18:01:19Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-14T18:01:19Z INF +-----------------------------------------------------------------------------------------------+
2026-08-14T18:01:19Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=350d5e9a-4cfc-49f6-9111-1bd2cb6ec267 status=pass target=region1.v2.argotunnel.com
2026-08-14T18:01:19Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=350d5e9a-4cfc-49f6-9111-1bd2cb6ec267 status=pass target=region2.v2.argotunnel.com
2026-08-14T18:01:19Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=350d5e9a-4cfc-49f6-9111-1bd2cb6ec267 status=pass target=region1.v2.argotunnel.com
2026-08-14T18:01:19Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=350d5e9a-4cfc-49f6-9111-1bd2cb6ec267 status=fail target=region2.v2.argotunnel.com
2026-08-14T18:01:19Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=350d5e9a-4cfc-49f6-9111-1bd2cb6ec267 status=pass target=region1.v2.argotunnel.com
2026-08-14T18:01:19Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=350d5e9a-4cfc-49f6-9111-1bd2cb6ec267 status=pass target=region2.v2.argotunnel.com
2026-08-14T18:01:19Z INF precheck component="Cloudflare API" details="API is reachable" run_id=350d5e9a-4cfc-49f6-9111-1bd2cb6ec267 status=pass target=api.cloudflare.com:443
2026-08-14T18:01:19Z INF precheck complete hard_fail=false run_id=350d5e9a-4cfc-49f6-9111-1bd2cb6ec267 suggested_protocol=http2
2026-08-14T18:01:37Z ERR  error="stream 9 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-14T18:01:37Z ERR Request failed error="stream 9 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.192.57 type=http
2026-08-14T19:51:41Z ERR  error="stream 25 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-14T19:51:41Z ERR Request failed error="stream 25 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.200.13 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[01:58:50] Time: Sat Aug 15 01:58:50 AM CST 2026
[01:58:50] User: root (UID: 0)
[01:58:50] === STEP 1: 启动 API (端口 8450) ===
[01:59:22] API 已在运行
[01:59:22] API 状态: OK
[01:59:22] === STEP 2: 安装 cloudflared ===
[01:59:22] cloudflared 安装路径: /usr/local/bin/cloudflared
[01:59:22] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[01:59:22] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[01:59:22] === STEP 3: 检查认证方式 ===
[01:59:22] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[01:59:22] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[01:59:22] 检查现有 tunnel...
[01:59:23] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax09, 2xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[01:59:23] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:23] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[01:59:23] 凭证文件存在
[01:59:23] 创建 config.yml...
[01:59:23] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[01:59:23] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:24] DNS 路由结果: 2026-08-14T17:59:24Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:24] === STEP 5: 更新 DNS (API) ===
[01:59:24] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:25] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[01:59:26] 设置 SSL 模式为 Full...
SSL: 跳过
[01:59:26] === STEP 6: 启动 Tunnel ===
[01:59:29] 启动 Named Tunnel (cert 模式)...
[01:59:29] 使用 config: /root/.cloudflared/config.yml
[01:59:29] cloudflared PID: 2608983
[01:59:31] Tunnel 连接已建立!
[01:59:31] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T17:59:29Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-14T17:59:29Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T17:59:29Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T17:59:29Z INF Generated Connector ID: b7dfc094-d0b6-4580-82f0-96e9b4a6c2e8
2026-08-14T17:59:29Z INF Initial protocol quic
2026-08-14T17:59:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T17:59:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T17:59:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T17:59:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T17:59:29Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-14T17:59:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.57
2026-08-14T17:59:30Z INF Registered tunnel connection connIndex=0 connection=d118a3cc-a375-44d4-8491-4929be1dcc4a event=0 ip=198.41.192.57 location=lax08 protocol=quic
2026-08-14T17:59:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-14T17:59:30Z INF Registered tunnel connection connIndex=1 connection=1ccb11bc-af63-4841-8b96-aa8aba0a124a event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-14T17:59:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[01:59:31] === STEP 7: 持久化 ===
[01:59:32] systemd 服务已配置
[01:59:32] Cron 保活已设置
[01:59:32] === STEP 8: 验证 ===
[01:59:32] --- API (localhost:8450) ---
 OK
[01:59:32] --- cloudflared 进程 ---
root     2608983  2.6  1.9 1294100 38464 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2609093  0.0  1.3 1292484 27552 ?       Rl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[01:59:32] --- aishield.tools ---
 OK
[01:59:34] --- DNS CNAME ---
[01:59:34] --- DNS A ---
104.21.81.46
172.67.188.44
[01:59:34] === 部署汇总 ===
[01:59:34] Tunnel Mode: cert
[01:59:34] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:34] API: http://localhost:8450
[01:59:34] 域名: https://aishield.tools
[01:59:34] cloudflared: /usr/local/bin/cloudflared
[01:59:34] PID: 2608983
[01:59:34] Config: /root/.cloudflared/config.yml
[01:59:34] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:34] 状态: Named Tunnel (cert 模式) 已配置
[02:01:01] API 已在运行
[02:01:01] API 状态: OK
[02:01:01] === STEP 2: 安装 cloudflared ===
[02:01:01] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:01:01] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:01:01] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:01:01] === STEP 3: 检查认证方式 ===
[02:01:01] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:01:01] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:01:01] 检查现有 tunnel...
[02:01:02] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax08, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-14T18:01:02Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:01:02] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:01:02] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:01:02] 凭证文件存在
[02:01:02] 创建 config.yml...
[02:01:02] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:01:02] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:01:04] DNS 路由结果: 2026-08-14T18:01:04Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:01:04] === STEP 5: 更新 DNS (API) ===
[02:01:04] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:01:05] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:01:05] 设置 SSL 模式为 Full...
SSL: 跳过
[02:01:06] === STEP 6: 启动 Tunnel ===
[02:01:09] 启动 Named Tunnel (cert 模式)...
[02:01:09] 使用 config: /root/.cloudflared/config.yml
[02:01:09] cloudflared PID: 2610912
[02:01:11] Tunnel 连接已建立!
[02:01:11] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T18:01:09Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T18:01:09Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T18:01:09Z INF Generated Connector ID: 3bf99e4e-b3cf-4313-94dc-245eaf48cb0a
2026-08-14T18:01:09Z INF Initial protocol quic
2026-08-14T18:01:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T18:01:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T18:01:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T18:01:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T18:01:09Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-14T18:01:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-14T18:01:10Z INF Registered tunnel connection connIndex=0 connection=cfe7e8dd-d280-4577-a875-b74f132b6696 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-14T18:01:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-08-14T18:01:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-14T18:01:11Z INF Registered tunnel connection connIndex=1 connection=f0a2ae82-4320-4bf7-a04f-ec22fbc337a8 event=0 ip=198.41.192.57 location=lax10 protocol=quic
2026-08-14T18:01:11Z INF Registered tunnel connection connIndex=2 connection=26cd7a1f-8ada-4139-90bf-bca9a02b65de event=0 ip=198.41.200.13 location=lax01 protocol=quic
[02:01:11] === STEP 7: 持久化 ===
[02:01:12] systemd 服务已配置
[02:01:12] Cron 保活已设置
[02:01:12] === STEP 8: 验证 ===
[02:01:12] --- API (localhost:8450) ---
 OK
[02:01:12] --- cloudflared 进程 ---
root     2610912  3.0  1.9 1294100 38456 ?       Sl   02:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2611012  0.0  1.3 1292740 27544 ?       Rl   02:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:01:12] --- aishield.tools ---
 OK
[02:01:13] --- DNS CNAME ---
[02:01:14] --- DNS A ---
172.67.188.44
104.21.81.46
[02:01:14] === 部署汇总 ===
[02:01:14] Tunnel Mode: cert
[02:01:14] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:01:14] API: http://localhost:8450
[02:01:14] 域名: https://aishield.tools
[02:01:14] cloudflared: /usr/local/bin/cloudflared
[02:01:14] PID: 2610912
[02:01:14] Config: /root/.cloudflared/config.yml
[02:01:14] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:01:14] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-15 02:01:12 CST; 2h 17min ago
   Main PID: 2611011 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 19.8M
        CPU: 13.198s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2611011 /bin/bash /opt/start-tunnel.sh
             └─2611012 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 20:18:24 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786738704.9439662, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
