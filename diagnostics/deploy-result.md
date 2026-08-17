=== DIAGNOSTIC ===
Time: Tue Aug 18 03:18:30 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786994310.7906423, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1237795  0.1  1.6 1294676 32708 ?       Sl   01:59   0:06 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1237947  0.1  1.6 1294676 33948 ?       Sl   01:59   0:06 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1238277  0.1  1.7 1294676 34460 ?       Sl   01:59   0:07 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-17T17:59:29Z INF Registered tunnel connection connIndex=0 connection=d9b7da50-bbf4-453a-ba3b-b9c6cd785139 event=0 ip=198.41.192.47 location=lax09 protocol=quic
2026-08-17T17:59:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-17T17:59:29Z INF Registered tunnel connection connIndex=1 connection=b9d0cea5-1e82-4d18-b483-a56aa74a90e0 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-17T17:59:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-08-17T17:59:30Z INF Registered tunnel connection connIndex=2 connection=12891a60-88a3-4704-a6bf-66fff90655b5 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-17T17:59:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.7
2026-08-17T17:59:31Z INF Registered tunnel connection connIndex=3 connection=0fc6738d-0ca2-43b2-9e01-f2a1538a94b4 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-08-17T17:59:35Z INF +-------------------------------------------------------------------------------------+
2026-08-17T17:59:35Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-17T17:59:35Z INF +-------------------------------------------------------------------------------------+
2026-08-17T17:59:35Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-17T17:59:35Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-17T17:59:35Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-17T17:59:35Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-17T17:59:35Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-17T17:59:35Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-17T17:59:35Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-17T17:59:35Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-17T17:59:35Z INF |                                                                                     |
2026-08-17T17:59:35Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-17T17:59:35Z INF +-------------------------------------------------------------------------------------+
2026-08-17T17:59:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region1.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region2.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region1.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region2.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region1.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region2.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="Cloudflare API" details="API is reachable" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=api.cloudflare.com:443
2026-08-17T17:59:35Z INF precheck complete hard_fail=false run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 suggested_protocol=quic
uic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[01:59:20] Time: Tue Aug 18 01:59:20 AM CST 2026
[01:59:20] User: root (UID: 0)
[01:59:20] === STEP 1: 启动 API (端口 8450) ===
[01:59:21] API 已在运行
[01:59:21] API 状态: OK
[01:59:21] === STEP 2: 安装 cloudflared ===
[01:59:21] cloudflared 安装路径: /usr/local/bin/cloudflared
[01:59:21] DNS 路由结果: 2026-08-17T17:59:21Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:21] === STEP 5: 更新 DNS (API) ===
[01:59:21] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:21] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[01:59:21] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[01:59:21] === STEP 3: 检查认证方式 ===
[01:59:21] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[01:59:21] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[01:59:21] 检查现有 tunnel...
[01:59:22] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[01:59:22] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[01:59:22] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:22] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[01:59:22] 凭证文件存在
[01:59:22] 创建 config.yml...
[01:59:22] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[01:59:22] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[01:59:23] 设置 SSL 模式为 Full...
[01:59:23] DNS 路由结果: 2026-08-17T17:59:23Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:23] === STEP 5: 更新 DNS (API) ===
[01:59:23] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
SSL: 跳过
[01:59:23] === STEP 6: 启动 Tunnel ===
[01:59:24] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[01:59:25] 设置 SSL 模式为 Full...
[01:59:25] 等待 tunnel 连接... (10s)
SSL: 跳过
[01:59:25] === STEP 6: 启动 Tunnel ===
[01:59:26] 启动 Named Tunnel (cert 模式)...
[01:59:26] 使用 config: /root/.cloudflared/config.yml
[01:59:26] cloudflared PID: 1237795
[01:59:27] Tunnel 连接已建立!
[01:59:27] --- cloudflared 日志 (最后 15 行) ---
2026-08-17T17:59:26Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-17T17:59:26Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-17T17:59:26Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-17T17:59:26Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-17T17:59:26Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-17T17:59:26Z INF Generated Connector ID: 08f0ec45-5854-4370-b836-684c187e1cf2
2026-08-17T17:59:26Z INF Initial protocol quic
2026-08-17T17:59:26Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-17T17:59:26Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-17T17:59:26Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-17T17:59:26Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-17T17:59:26Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-17T17:59:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-17T17:59:27Z INF Registered tunnel connection connIndex=0 connection=3db65848-b902-4ca9-98ca-82f64a66c10e event=0 ip=198.41.192.167 location=lax10 protocol=quic
2026-08-17T17:59:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
[01:59:27] === STEP 7: 持久化 ===
[01:59:28] systemd 服务已配置
[01:59:28] Cron 保活已设置
[01:59:28] === STEP 8: 验证 ===
[01:59:28] --- API (localhost:8450) ---
 OK
[01:59:28] --- cloudflared 进程 ---
root     1237795  4.0  1.8 1294420 38200 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1237899  0.0  1.2 1292484 26128 ?       Rl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[01:59:28] --- aishield.tools ---
[01:59:28] 启动 Named Tunnel (cert 模式)...
[01:59:28] 使用 config: /root/.cloudflared/config.yml
[01:59:28] cloudflared PID: 1237947
[01:59:28] Tunnel 连接已建立!
[01:59:28] --- cloudflared 日志 (最后 15 行) ---
2026-08-17T17:59:28Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-17T17:59:28Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-17T17:59:28Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-17T17:59:28Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-17T17:59:28Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-17T17:59:28Z INF Generated Connector ID: a995f397-f2db-4d99-be17-cf8bfb57ca1b
2026-08-17T17:59:28Z INF Initial protocol quic
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     2026-08-17T17:59:28Z INF Registered tunnel connection connIndex=2 connection=62c1edff-b013-400b-9dc1-aac03bd0f72d event=0 ip=198.41.192.37 location=lax11 protocol=quic
[01:59:28] === STEP 7: 持久化 ===
 OK
[01:59:29] --- DNS CNAME ---
[01:59:29] --- DNS A ---
172.67.188.44
104.21.81.46
[01:59:29] === 部署汇总 ===
[01:59:29] Tunnel Mode: cert
[01:59:29] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:29] API: http://localhost:8450
[01:59:29] 域名: https://aishield.tools
[01:59:29] cloudflared: /usr/local/bin/cloudflared
[01:59:29] PID: 1237270
[01:59:29] Config: /root/.cloudflared/config.yml
[01:59:29] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:29] 状态: Named Tunnel (cert 模式) 已配置
[01:59:30] Tunnel 连接已建立!
[01:59:30] --- cloudflared 日志 (最后 15 行) ---
2026-08-17T17:59:28Z INF Initial protocol quic
2026-08-17T17:59:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-17T17:59:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-17T17:59:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-17T17:59:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-17T17:59:28Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-17T17:59:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
2026-08-17T17:59:29Z INF Registered tunnel connection connIndex=0 connection=d9b7da50-bbf4-453a-ba3b-b9c6cd785139 event=0 ip=198.41.192.47 location=lax09 protocol=quic
2026-08-17T17:59:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-17T17:59:29Z INF Registered tunnel connection connIndex=1 connection=b9d0cea5-1e82-4d18-b483-a56aa74a90e0 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-17T17:59:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-08-17T17:59:30Z INF Registered tunnel connection connIndex=2 connection=12891a60-88a3-4704-a6bf-66fff90655b5 event=0 ip=198.41.200.233 location=lax01 protocol=quic
c
2026-08-17T17:59:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.53
2026-08-17T17:59:29Z INF Registered tunnel connection connIndex=3 connection=719010a9-2c18-437d-b26c-35c26d032c52 event=0 ip=198.41.200.53 location=lax01 protocol=quic
[01:59:30] === STEP 7: 持久化 ===
[01:59:33] systemd 服务已配置
[01:59:33] systemd 服务已配置
[01:59:33] Cron 保活已设置
[01:59:33] Cron 保活已设置
[01:59:33] === STEP 8: 验证 ===
[01:59:33] --- API (localhost:8450) ---
[01:59:33] === STEP 8: 验证 ===
[01:59:33] --- API (localhost:8450) ---
 OK
 OK
[01:59:33] --- cloudflared 进程 ---
[01:59:33] --- cloudflared 进程 ---
root     1237795  1.5  1.7 1294676 35056 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1237947  2.8  1.8 1294676 37132 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1238277  0.0  1.3 1292740 27216 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[01:59:33] --- aishield.tools ---
root     1237795  1.5  1.7 1294676 35056 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1237947  2.8  1.8 1294676 37132 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1238277  0.0  1.3 1292740 27216 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[01:59:33] --- aishield.tools ---
 OK
[01:59:34] --- DNS CNAME ---
 OK
[01:59:35] --- DNS CNAME ---
[01:59:35] --- DNS A ---
[01:59:35] --- DNS A ---
172.67.188.44
104.21.81.46
[01:59:35] === 部署汇总 ===
[01:59:35] Tunnel Mode: cert
104.21.81.46
172.67.188.44
[01:59:35] === 部署汇总 ===
[01:59:35] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:35] Tunnel Mode: cert
[01:59:35] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:35] API: http://localhost:8450
[01:59:35] API: http://localhost:8450
[01:59:35] 域名: https://aishield.tools
[01:59:35] 域名: https://aishield.tools
[01:59:35] cloudflared: /usr/local/bin/cloudflared
[01:59:35] PID: 1237795
[01:59:35] cloudflared: /usr/local/bin/cloudflared
[01:59:35] PID: 1237947
[01:59:35] Config: /root/.cloudflared/config.yml
[01:59:35] Config: /root/.cloudflared/config.yml
[01:59:35] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:35] 状态: Named Tunnel (cert 模式) 已配置
[01:59:35] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:35] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-18 01:59:33 CST; 1h 18min ago
   Main PID: 1238270 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 24.7M
        CPU: 7.041s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1238270 /bin/bash /opt/start-tunnel.sh
             └─1238277 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 17 19:18:31 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786994311.4468179, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
