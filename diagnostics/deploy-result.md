=== DIAGNOSTIC ===
Time: Wed Aug 19 04:36:50 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787128610.331477, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2753777  0.7  1.8 1294676 37224 ?       Sl   16:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2753798  0.8  1.7 1294676 35132 ?       Sl   16:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2754042  0.9  1.8 1294676 37780 ?       Sl   16:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-19T08:36:36Z INF Registered tunnel connection connIndex=2 connection=97bbc4fa-1940-4b27-b41f-570688cdfaab event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-19T08:36:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.67
22026-08-19T08:36:42Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-19T08:36:42Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-08-19T08:36:43Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-19T08:36:43Z INF +-----------------------------------------------------------------------------------------------+
2026-08-19T08:36:43Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-19T08:36:43Z INF +-----------------------------------------------------------------------------------------------+
2026-08-19T08:36:43Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-19T08:36:43Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-19T08:36:43Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-19T08:36:43Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-19T08:36:43Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-19T08:36:43Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-19T08:36:43Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-19T08:36:43Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-19T08:36:43Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-19T08:36:43Z INF |                                                                                               |
2026-08-19T08:36:43Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-19T08:36:43Z INF +-----------------------------------------------------------------------------------------------+
2026-08-19T08:36:43Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c034d700-a1db-4d85-a8ef-aeb7b7382cdb status=pass target=region1.v2.argotunnel.com
2026-08-19T08:36:43Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c034d700-a1db-4d85-a8ef-aeb7b7382cdb status=pass target=region2.v2.argotunnel.com
2026-08-19T08:36:43Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c034d700-a1db-4d85-a8ef-aeb7b7382cdb status=pass target=region1.v2.argotunnel.com
2026-08-19T08:36:43Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=c034d700-a1db-4d85-a8ef-aeb7b7382cdb status=fail target=region2.v2.argotunnel.com
2026-08-19T08:36:43Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c034d700-a1db-4d85-a8ef-aeb7b7382cdb status=pass target=region1.v2.argotunnel.com
2026-08-19T08:36:43Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c034d700-a1db-4d85-a8ef-aeb7b7382cdb status=pass target=region2.v2.argotunnel.com
2026-08-19T08:36:43Z INF precheck component="Cloudflare API" details="API is reachable" run_id=c034d700-a1db-4d85-a8ef-aeb7b7382cdb status=pass target=api.cloudflare.com:443
2026-08-19T08:36:43Z INF precheck complete hard_fail=false run_id=c034d700-a1db-4d85-a8ef-aeb7b7382cdb suggested_protocol=http2
2026-08-19T08:36:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.33
2026-08-19T08:36:46Z INF Registered tunnel connection connIndex=3 connection=9150ff49-3a9e-421b-99fc-73a02446292f event=0 ip=198.41.200.33 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:36:21] Time: Wed Aug 19 04:36:21 PM CST 2026
[16:36:21] User: root (UID: 0)
[16:36:21] === STEP 1: 启动 API (端口 8450) ===
[16:36:25] API 已在运行
[16:36:25] API 状态: OK
[16:36:25] === STEP 2: 安装 cloudflared ===
[16:36:25] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:36:25] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:36:25] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:36:25] === STEP 3: 检查认证方式 ===
[16:36:25] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:36:25] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:36:25] 检查现有 tunnel...
[16:36:26] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax07, 1xlax08, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-19T08:36:26Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[16:36:26] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:36:26] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:36:26] 凭证文件存在
[16:36:26] 创建 config.yml...
[16:36:26] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:36:26] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:36:26] API 已在运行
[16:36:26] API 状态: OK
[16:36:26] === STEP 2: 安装 cloudflared ===
[16:36:26] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:36:26] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:36:26] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:36:26] === STEP 3: 检查认证方式 ===
[16:36:26] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:36:26] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:36:26] 检查现有 tunnel...
[16:36:27] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax07, 1xlax08, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[16:36:27] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:36:27] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:36:27] 凭证文件存在
[16:36:27] 创建 config.yml...
[16:36:27] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:36:27] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:36:27] DNS 路由结果: 2026-08-19T08:36:27Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:36:27] === STEP 5: 更新 DNS (API) ===
[16:36:27] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:36:28] DNS 路由结果: 2026-08-19T08:36:28Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:36:28] === STEP 5: 更新 DNS (API) ===
[16:36:28] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:36:28] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:36:29] 设置 SSL 模式为 Full...
SSL: 跳过
[16:36:30] === STEP 6: 启动 Tunnel ===
[16:36:30] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:36:31] 设置 SSL 模式为 Full...
SSL: 跳过
[16:36:31] === STEP 6: 启动 Tunnel ===
[16:36:33] 启动 Named Tunnel (cert 模式)...
[16:36:33] 使用 config: /root/.cloudflared/config.yml
[16:36:33] cloudflared PID: 2753777
[16:36:34] 启动 Named Tunnel (cert 模式)...
[16:36:34] 使用 config: /root/.cloudflared/config.yml
[16:36:34] cloudflared PID: 2753798
[16:36:35] Tunnel 连接已建立!
[16:36:35] --- cloudflared 日志 (最后 15 行) ---
2026-08-19T08:36:35Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-19T08:36:35Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-19T08:36:35Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-19T08:36:35Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-19T08:36:35Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-19T08:36:35Z INF Generated Connector ID: 2b3959cb-8bef-425f-a865-f7c782a37e54
2026-08-19T08:36:35Z INF Initial protocol quic
2026-08-19T08:36:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T08:36:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T08:36:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T08:36:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T08:36:35Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-19T08:36:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
 2026-08-19T08:36:35Z INF Registered tunnel connection connIndex=0 connection=3240bfd4-1680-4f54-b237-a5841fe58cd7 event=0 ip=198.41.192.167 location=lax10 protocol=quic
2026-08-19T08:36:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
[16:36:35] === STEP 7: 持久化 ===
[16:36:36] systemd 服务已配置
[16:36:36] Cron 保活已设置
[16:36:36] === STEP 8: 验证 ===
[16:36:36] --- API (localhost:8450) ---
 OK
[16:36:36] --- cloudflared 进程 ---
root     2753777  2.6  1.8 1294100 37532 ?       Sl   16:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2753798  4.5  1.8 1294676 37992 ?       Sl   16:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2753917  0.0  1.3 1292740 27084 ?       Rl   16:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:36:36] --- aishield.tools ---
[16:36:36] Tunnel 连接已建立!
[16:36:36] --- cloudflared 日志 (最后 15 行) ---
2026-08-19T08:36:35Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-19T08:36:35Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-19T08:36:35Z INF Generated Connector ID: 2b3959cb-8bef-425f-a865-f7c782a37e54
2026-08-19T08:36:35Z INF Initial protocol quic
2026-08-19T08:36:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T08:36:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T08:36:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T08:36:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T08:36:35Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-19T08:36:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-08-19T08:36:35Z INF Registered tunnel connection connIndex=0 connection=5eddf11b-498b-4c60-bdf7-c8fc1dadc930 event=0 ip=198.41.192.77 location=lax10 protocol=quic
2026-08-19T08:36:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
22026-08-19T08:36:35Z INF Registered tunnel connection connIndex=1 connection=253b211b-09f6-40c2-9dca-ae177adec440 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-19T08:36:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-19T08:36:36Z INF Registered tunnel connection connIndex=2 connection=97bbc4fa-1940-4b27-b41f-570688cdfaab event=0 ip=198.41.200.13 location=lax01 protocol=quic
[16:36:37] === STEP 7: 持久化 ===
[16:36:37] systemd 服务已配置
[16:36:37] Cron 保活已设置
[16:36:37] === STEP 8: 验证 ===
[16:36:37] --- API (localhost:8450) ---
 OK
[16:36:37] --- cloudflared 进程 ---
root     2753777  2.5  1.8 1294676 37948 ?       Sl   16:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2753798  3.3  1.8 1294676 37372 ?       Sl   16:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2754042  0.0  1.3 1292740 27456 ?       Rl   16:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:36:37] --- aishield.tools ---
 OK
 FAIL (DNS 传播中或配置错误)
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-19 16:36:37 CST; 12s ago
   Main PID: 2754038 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 21.1M
        CPU: 136ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2754038 /bin/bash /opt/start-tunnel.sh
             └─2754042 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 19 08:36:50 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787128611.007623, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
