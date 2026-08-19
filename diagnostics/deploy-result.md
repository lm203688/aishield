=== DIAGNOSTIC ===
Time: Wed Aug 19 10:09:24 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787105364.912193, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2441730  0.1  1.7 1294676 35132 ?       Sl   08:39   0:08 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2441889  0.1  1.7 1294676 34544 ?       Sl   08:39   0:08 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-19T01:27:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.227
2026-08-19T01:27:10Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.192.227
2026-08-19T01:27:10Z INF Retrying connection in up to 4s connIndex=3 event=0 ip=198.41.192.227
2026-08-19T01:27:12Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-19T01:27:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.7
2026-08-19T01:27:14Z INF Registered tunnel connection connIndex=3 connection=7d0be591-4d91-4f0a-be62-e2c138b2ae05 event=0 ip=198.41.192.7 location=lax07 protocol=quic
2026-08-19T02:03:07Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: Application error 0x0 (remote)" connIndex=1 event=0 ip=198.41.192.47
2026-08-19T02:03:07Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.192.47
2026-08-19T02:03:07Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.47
2026-08-19T02:03:07Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.47
2026-08-19T02:03:07Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.47
2026-08-19T02:03:07Z WRN Connection terminated error="accept stream listener encountered a failure while serving" connIndex=1
2026-08-19T02:03:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-19T02:03:21Z INF Registered tunnel connection connIndex=1 connection=4a210d3f-2e5d-4145-b0fe-985304f883e6 event=0 ip=198.41.192.47 location=lax08 protocol=quic
2026-08-19T02:08:39Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=2 event=0 ip=198.41.200.53
2026-08-19T02:08:39Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: Application error 0x0 (remote)" connIndex=2 event=0 ip=198.41.200.53
2026-08-19T02:08:39Z WRN failed to serve tunnel connection error="datagram manager encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.53
2026-08-19T02:08:39Z WRN Serve tunnel error error="datagram manager encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.53
2026-08-19T02:08:39Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.200.53
2026-08-19T02:08:40Z WRN Connection terminated error="datagram manager encountered a failure while serving" connIndex=2
2026-08-19T02:08:42Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-19T02:08:47Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.53
2026-08-19T02:08:47Z INF Retrying connection in up to 4s connIndex=2 event=0 ip=198.41.200.53
2026-08-19T02:08:51Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-19T02:08:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
2026-08-19T02:08:59Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.193
2026-08-19T02:08:59Z INF Retrying connection in up to 8s connIndex=2 event=0 ip=198.41.200.193
2026-08-19T02:09:02Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-19T02:09:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-19T02:09:17Z INF Registered tunnel connection connIndex=2 connection=80c75f62-934e-4b6c-83b5-0424a304d444 event=0 ip=198.41.200.53 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:32:39] Time: Wed Aug 19 08:32:39 AM CST 2026
[08:32:39] User: root (UID: 0)
[08:32:39] === STEP 1: 启动 API (端口 8450) ===
[08:36:11] API 已在运行
[08:36:11] API 状态: OK
[08:36:11] === STEP 2: 安装 cloudflared ===
[08:36:11] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:36:11] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:11] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:11] === STEP 3: 检查认证方式 ===
[08:36:11] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:36:11] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:36:11] 检查现有 tunnel...
[08:36:12] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax08, 1xlax09, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-19T00:36:12Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:36:12] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:12] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:36:12] 凭证文件存在
[08:36:12] 创建 config.yml...
[08:36:12] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:36:12] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:14] DNS 路由结果: 2026-08-19T00:36:14Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:14] === STEP 5: 更新 DNS (API) ===
[08:36:14] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:15] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:36:15] 设置 SSL 模式为 Full...
SSL: 跳过
[08:36:16] === STEP 6: 启动 Tunnel ===
[08:36:19] 启动 Named Tunnel (cert 模式)...
[08:36:19] 使用 config: /root/.cloudflared/config.yml
[08:36:19] cloudflared PID: 2439227
[08:36:21] Tunnel 连接已建立!
[08:36:21] --- cloudflared 日志 (最后 15 行) ---
2026-08-19T00:36:19Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-19T00:36:19Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-19T00:36:19Z INF Generated Connector ID: 7ab9a2a0-727c-4d48-8f89-d0cda6ab9146
2026-08-19T00:36:19Z INF Initial protocol quic
2026-08-19T00:36:19Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T00:36:19Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T00:36:19Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T00:36:19Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T00:36:19Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-19T00:36:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-19T00:36:20Z INF Registered tunnel connection connIndex=0 connection=6b4e95c9-f20d-4f37-aeac-ff3a6fb64373 event=0 ip=198.41.192.107 location=lax09 protocol=quic
2026-08-19T00:36:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-19T00:36:20Z INF Registered tunnel connection connIndex=1 connection=0ed08807-85c2-4b97-b88b-6403a9c05b3c event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-19T00:36:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-19T00:36:21Z INF Registered tunnel connection connIndex=2 connection=d863782d-b65b-42c7-b2df-f709a2effacb event=0 ip=198.41.192.77 location=lax08 protocol=quic
[08:36:21] === STEP 7: 持久化 ===
[08:36:22] systemd 服务已配置
[08:36:22] Cron 保活已设置
[08:36:22] === STEP 8: 验证 ===
[08:36:22] --- API (localhost:8450) ---
 OK
[08:36:22] --- cloudflared 进程 ---
root     2439227  3.0  1.9 1294676 39524 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2439351  0.0  1.3 1292484 27332 ?       Rl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:36:22] --- aishield.tools ---
 OK
[08:36:23] --- DNS CNAME ---
[08:36:23] --- DNS A ---
104.21.81.46
172.67.188.44
[08:36:23] === 部署汇总 ===
[08:36:23] Tunnel Mode: cert
[08:36:24] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:24] API: http://localhost:8450
[08:36:24] 域名: https://aishield.tools
[08:36:24] cloudflared: /usr/local/bin/cloudflared
[08:36:24] PID: 2439227
[08:36:24] Config: /root/.cloudflared/config.yml
[08:36:24] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:24] 状态: Named Tunnel (cert 模式) 已配置
[08:39:25] API 已在运行
[08:39:25] API 状态: OK
[08:39:25] === STEP 2: 安装 cloudflared ===
[08:39:25] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:39:25] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:39:26] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:39:26] === STEP 3: 检查认证方式 ===
[08:39:26] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:39:26] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:39:26] 检查现有 tunnel...
[08:39:26] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax08, 2xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[08:39:26] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:39:26] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:39:26] 凭证文件存在
[08:39:26] 创建 config.yml...
[08:39:26] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:39:26] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:39:29] DNS 路由结果: 2026-08-19T00:39:29Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:39:29] === STEP 5: 更新 DNS (API) ===
[08:39:29] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:39:30] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:39:31] 设置 SSL 模式为 Full...
SSL: 跳过
[08:39:32] === STEP 6: 启动 Tunnel ===
[08:39:35] 启动 Named Tunnel (cert 模式)...
[08:39:35] 使用 config: /root/.cloudflared/config.yml
[08:39:35] cloudflared PID: 2441730
[08:39:41] Tunnel 连接已建立!
[08:39:41] --- cloudflared 日志 (最后 15 行) ---
2026-08-19T00:39:35Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-19T00:39:35Z INF Generated Connector ID: 0ed3c5a3-6583-4efa-94d6-f2af76d71a1d
2026-08-19T00:39:35Z INF Initial protocol quic
2026-08-19T00:39:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T00:39:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T00:39:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-19T00:39:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-19T00:39:35Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-19T00:39:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.193
2026-08-19T00:39:40Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-19T00:39:40Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.193
2026-08-19T00:39:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-19T00:39:41Z INF Registered tunnel connection connIndex=0 connection=9d337dbd-f35d-4062-a76a-36b440ccdca0 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-19T00:39:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-19T00:39:41Z INF Registered tunnel connection connIndex=1 connection=c1c3037d-7a5e-4d45-8cda-3be9c692e716 event=0 ip=198.41.192.47 location=lax08 protocol=quic
[08:39:41] === STEP 7: 持久化 ===
[08:39:42] systemd 服务已配置
[08:39:42] Cron 保活已设置
[08:39:42] === STEP 8: 验证 ===
[08:39:42] --- API (localhost:8450) ---
 OK
[08:39:42] --- cloudflared 进程 ---
root     2441730  1.4  1.8 1294676 38180 ?       Sl   08:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2441889  0.0  1.3 1292740 27296 ?       Rl   08:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:39:42] --- aishield.tools ---
 OK
[08:39:44] --- DNS CNAME ---
[08:39:44] --- DNS A ---
104.21.81.46
172.67.188.44
[08:39:44] === 部署汇总 ===
[08:39:44] Tunnel Mode: cert
[08:39:44] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:39:44] API: http://localhost:8450
[08:39:44] 域名: https://aishield.tools
[08:39:44] cloudflared: /usr/local/bin/cloudflared
[08:39:44] PID: 2441730
[08:39:44] Config: /root/.cloudflared/config.yml
[08:39:44] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:39:44] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-19 08:39:42 CST; 1h 29min ago
   Main PID: 2441888 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.4M
        CPU: 8.743s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2441888 /bin/bash /opt/start-tunnel.sh
             └─2441889 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 19 02:09:25 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787105365.327826, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
