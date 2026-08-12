=== DIAGNOSTIC ===
Time: Wed Aug 12 07:36:36 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786534596.7322042, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      303021  0.1  1.2 1294676 24556 ?       Sl   15:29   0:25 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      303117  0.1  1.1 1294676 22944 ?       Sl   15:29   0:25 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-12T11:03:47Z WRN failed to serve tunnel connection error="datagram manager encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.113
2026-08-12T11:03:47Z WRN Serve tunnel error error="datagram manager encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.113
2026-08-12T11:03:47Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.200.113
2026-08-12T11:03:48Z WRN Connection terminated error="datagram manager encountered a failure while serving" connIndex=3
2026-08-12T11:03:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.113
2026-08-12T11:04:03Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.113
2026-08-12T11:04:03Z INF Retrying connection in up to 4s connIndex=3 event=0 ip=198.41.200.113
2026-08-12T11:04:07Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-12T11:04:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.193
2026-08-12T11:04:18Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-12T11:04:18Z INF Retrying connection in up to 8s connIndex=3 event=0 ip=198.41.200.193
2026-08-12T11:04:26Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-12T11:04:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-12T11:04:28Z INF Registered tunnel connection connIndex=3 connection=0da2fe0f-730c-4cb6-a7a7-13de4eee69dc event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-12T11:04:50Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: Application error 0x0 (remote)" connIndex=2 event=0 ip=198.41.192.227
2026-08-12T11:04:50Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=2 event=0 ip=198.41.192.227
2026-08-12T11:04:50Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.227
2026-08-12T11:04:50Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.227
2026-08-12T11:04:50Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.192.227
2026-08-12T11:04:52Z WRN Connection terminated error="accept stream listener encountered a failure while serving" connIndex=2
2026-08-12T11:05:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-12T11:05:19Z INF Registered tunnel connection connIndex=2 connection=10a4d47a-af4b-4934-b4e6-ba23d8aa0db0 event=0 ip=198.41.192.227 location=lax10 protocol=quic
2026-08-12T11:06:29Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: Application error 0x0 (remote)" connIndex=1 event=0 ip=198.41.200.233
2026-08-12T11:06:29Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=1 event=0 ip=198.41.200.233
2026-08-12T11:06:29Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.233
2026-08-12T11:06:29Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.233
2026-08-12T11:06:29Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.233
2026-08-12T11:06:30Z WRN Connection terminated error="accept stream listener encountered a failure while serving" connIndex=1
2026-08-12T11:09:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-12T11:09:18Z INF Registered tunnel connection connIndex=1 connection=c746bebc-3332-4b75-9200-62c72aad87b9 event=0 ip=198.41.200.233 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[15:29:33] Time: Wed Aug 12 03:29:33 PM CST 2026
[15:29:33] User: root (UID: 0)
[15:29:33] === STEP 1: 启动 API (端口 8450) ===
[15:29:33] 启动 Named Tunnel (cert 模式)...
[15:29:33] 使用 config: /root/.cloudflared/config.yml
[15:29:33] cloudflared PID: 302437
[15:29:34] API 已在运行
[15:29:34] API 状态: OK
[15:29:34] === STEP 2: 安装 cloudflared ===
[15:29:34] cloudflared 安装路径: /usr/local/bin/cloudflared
[15:29:34] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[15:29:34] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[15:29:34] === STEP 3: 检查认证方式 ===
[15:29:34] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[15:29:34] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[15:29:34] 检查现有 tunnel...
[15:29:35] Tunnel 连接已建立!
[15:29:35] --- cloudflared 日志 (最后 15 行) ---
2026-08-12T07:29:33Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-12T07:29:33Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-12T07:29:33Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-12T07:29:33Z INF Generated Connector ID: 3bf1afca-1bf0-4ef0-88b7-0589c5476f67
2026-08-12T07:29:33Z INF Initial protocol quic
2026-08-12T07:29:33Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T07:29:33Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T07:29:33Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T07:29:33Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T07:29:33Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-12T07:29:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-12T07:29:34Z INF Registered tunnel connection connIndex=0 connection=c7eb6499-2cf5-40c0-957e-70c77755751b event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-12T07:29:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-12T07:29:34Z INF Registered tunnel connection connIndex=1 connection=f1a53d79-1817-4c40-bc75-6270c91cc752 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-12T07:29:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
[15:29:35] === STEP 7: 持久化 ===
[15:29:35] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax08, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[15:29:35] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[15:29:35] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[15:29:35] 凭证文件存在
[15:29:35] 创建 config.yml...
[15:29:35] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[15:29:35] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[15:29:36] systemd 服务已配置
[15:29:36] Cron 保活已设置
[15:29:36] === STEP 8: 验证 ===
[15:29:36] --- API (localhost:8450) ---
 OK
[15:29:36] --- cloudflared 进程 ---
root      302437  3.3  1.9 1294420 38968 ?       Sl   15:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      302608  6.0  1.5 1292812 31656 ?       Rl   15:29   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
root      302654  0.0  1.3 1292740 27360 ?       Rl   15:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[15:29:36] --- aishield.tools ---
 OK
[15:29:37] --- DNS CNAME ---
[15:29:37] --- DNS A ---
104.21.81.46
172.67.188.44
[15:29:37] === 部署汇总 ===
[15:29:37] Tunnel Mode: cert
[15:29:37] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[15:29:37] API: http://localhost:8450
[15:29:37] 域名: https://aishield.tools
[15:29:37] cloudflared: /usr/local/bin/cloudflared
[15:29:37] PID: 302437
[15:29:37] Config: /root/.cloudflared/config.yml
[15:29:37] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[15:29:37] 状态: Named Tunnel (cert 模式) 已配置
[15:29:38] DNS 路由结果: 2026-08-12T07:29:38Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[15:29:38] === STEP 5: 更新 DNS (API) ===
[15:29:38] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[15:29:38] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[15:29:39] 设置 SSL 模式为 Full...
SSL: 跳过
[15:29:40] === STEP 6: 启动 Tunnel ===
[15:29:43] 启动 Named Tunnel (cert 模式)...
[15:29:43] 使用 config: /root/.cloudflared/config.yml
[15:29:43] cloudflared PID: 303021
[15:29:45] Tunnel 连接已建立!
[15:29:45] --- cloudflared 日志 (最后 15 行) ---
2026-08-12T07:29:44Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-12T07:29:44Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-12T07:29:44Z INF Generated Connector ID: fee787db-63df-41e5-8f5c-07a37f4b153a
2026-08-12T07:29:44Z INF Initial protocol quic
2026-08-12T07:29:44Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T07:29:44Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T07:29:44Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T07:29:44Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T07:29:44Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-12T07:29:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-12T07:29:44Z INF Registered tunnel connection connIndex=0 connection=ebb4e05a-f97c-4d5a-a925-80b27f5a86ad event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-08-12T07:29:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-12T07:29:45Z INF Registered tunnel connection connIndex=1 connection=7a5db37d-7a70-44b1-a03f-3f9645f7f311 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-12T07:29:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
2026-08-12T07:29:45Z INF Registered tunnel connection connIndex=2 connection=3f202b9b-baa4-4de4-b096-588a54070d8e event=0 ip=198.41.192.67 location=lax10 protocol=quic
[15:29:45] === STEP 7: 持久化 ===
[15:29:46] systemd 服务已配置
[15:29:46] Cron 保活已设置
[15:29:46] === STEP 8: 验证 ===
[15:29:46] --- API (localhost:8450) ---
 OK
[15:29:46] --- cloudflared 进程 ---
root      303021  4.0  1.9 1294420 38756 ?       Sl   15:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      303117  0.0  1.3 1292484 26676 ?       Rl   15:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[15:29:46] --- aishield.tools ---
 OK
[15:29:49] --- DNS CNAME ---
[15:29:49] --- DNS A ---
104.21.81.46
172.67.188.44
[15:29:49] === 部署汇总 ===
[15:29:49] Tunnel Mode: cert
[15:29:49] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[15:29:49] API: http://localhost:8450
[15:29:49] 域名: https://aishield.tools
[15:29:49] cloudflared: /usr/local/bin/cloudflared
[15:29:49] PID: 303021
[15:29:49] Config: /root/.cloudflared/config.yml
[15:29:49] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[15:29:49] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-12 15:29:46 CST; 4h 6min ago
   Main PID: 303109 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.6M
        CPU: 25.496s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─303109 /bin/bash /opt/start-tunnel.sh
             └─303117 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 12 11:36:37 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786534597.4666827, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
