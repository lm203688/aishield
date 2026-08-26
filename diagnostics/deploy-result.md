=== DIAGNOSTIC ===
Time: Wed Aug 26 08:28:03 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787704083.9144475, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      377927  0.1  1.3 1360348 26948 ?       Sl   02:04   0:37 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      377948  0.1  1.3 1360284 27724 ?       Sl   02:04   0:36 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      378237  0.1  1.4 1294676 28768 ?       Sl   02:04   0:36 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-25T21:33:32Z ERR failed to accept incoming stream requests error="failed to accep2026-08-25T21:33:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-25T21:33:32Z WRN Connection terminated error="datagram manager encountered a failure while serving" connIndex=3
2026-08-25T21:33:35Z INF Registered tunnel connection connIndex=0 connection=20638c45-9335-4dd3-ac1f-53307a991a94 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-25T21:33:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-25T21:33:37Z INF Registered tunnel connection connIndex=3 connection=744c2cee-4230-4b5a-a894-1ced2339195d event=0 ip=198.41.200.233 location=lax01 protocol=quic
1 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-25T21:33:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-25T21:33:40Z INF Registered tunnel connection connIndex=2 connection=4373f215-4a93-44f6-a553-8392fd822bf8 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-25T21:38:41Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.53
2026-08-25T21:38:41Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.53
2026-08-25T21:38:41Z WRN failed to serve tunnel connection error="datagram manager encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.53
2026-08-25T21:38:41Z WRN Serve tunnel error error="datagram manager encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.53
2026-08-25T21:38:41Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.200.53
2026-08-25T21:38:41Z WRN Connection terminated error="datagram manager encountered a failure while serving" connIndex=2
2026-08-25T21:38:42Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-25T21:38:43Z INF Registered tunnel connection connIndex=2 connection=68e38d4c-519d-460f-bff2-b460ddd47b0f event=0 ip=198.41.200.53 location=sjc10 protocol=quic
2026-08-25T23:05:23Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:05:23Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:05:23Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:05:23Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:05:23Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:05:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:05:27Z INF Registered tunnel connection connIndex=0 connection=0a4de281-5d36-4d24-aed1-f88975515786 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-25T23:06:26Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:06:26Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:06:26Z WRN failed to serve tunnel connection error="datagram manager encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:06:26Z WRN Serve tunnel error error="datagram manager encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:06:26Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:06:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-25T23:06:31Z INF Registered tunnel connection connIndex=0 connection=bdedb914-dcb8-445e-908e-a748068ed643 event=0 ip=198.41.200.113 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:04:09] Time: Wed Aug 26 02:04:09 AM CST 2026
[02:04:09] User: root (UID: 0)
[02:04:09] === STEP 1: 启动 API (端口 8450) ===
[02:04:13] API 已在运行
[02:04:13] API 状态: OK
[02:04:13] === STEP 2: 安装 cloudflared ===
[02:04:13] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:13] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:13] API 已在运行
[02:04:13] API 状态: OK
[02:04:13] === STEP 2: 安装 cloudflared ===
[02:04:13] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:13] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:13] === STEP 3: 检查认证方式 ===
[02:04:14] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:14] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:14] 检查现有 tunnel...
[02:04:14] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:14] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:14] === STEP 3: 检查认证方式 ===
[02:04:14] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:14] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:14] 检查现有 tunnel...
[02:04:14] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax09, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-25T18:04:14Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:04:14] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:14] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:14] 凭证文件存在
[02:04:14] 创建 config.yml...
[02:04:14] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:14] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:14] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax09, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-25T18:04:14Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:04:14] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:14] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:14] 凭证文件存在
[02:04:14] 创建 config.yml...
[02:04:14] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:14] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:16] DNS 路由结果: 2026-08-25T18:04:16Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:16] === STEP 5: 更新 DNS (API) ===
[02:04:16] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:17] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[02:04:17] DNS 路由结果: 2026-08-25T18:04:17Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:17] === STEP 5: 更新 DNS (API) ===
[02:04:17] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[02:04:17] 设置 SSL 模式为 Full...
[02:04:18] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
SSL: 跳过
[02:04:18] === STEP 6: 启动 Tunnel ===
DNS 更新: OK
[02:04:18] 设置 SSL 模式为 Full...
SSL: 跳过
[02:04:19] === STEP 6: 启动 Tunnel ===
[02:04:21] 启动 Named Tunnel (cert 模式)...
[02:04:21] 使用 config: /root/.cloudflared/config.yml
[02:04:21] cloudflared PID: 377927
[02:04:22] 启动 Named Tunnel (cert 模式)...
[02:04:22] 使用 config: /root/.cloudflared/config.yml
[02:04:22] cloudflared PID: 377948
[02:04:23] Tunnel 连接已建立!
[02:04:23] --- cloudflared 日志 (最后 15 行) ---
2026-08-25T18:04:22Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-25T18:04:22Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-25T18:04:22Z INF Generated Connector ID: 65947156-3fc2-4601-8819-6f40c67f014c
2026-08-25T18:04:22Z INF Initial protocol quic
2026-08-25T18:04:22Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-25T18:04:22Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-25T18:04:22Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-25T18:04:22Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-25T18:04:22Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-25T18:04:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-25T18:04:22Z INF Registered tunnel connection connIndex=0 connection=eb5e323a-e73a-480a-a76d-b80e45626793 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-25T18:04:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-25T18:04:23Z INF Registered tunnel connection connIndex=1 connection=be41b555-07dc-4fd3-8b18-2b86bc65456d event=0 ip=198.41.192.107 location=lax10 protocol=quic
-08-25T18:04:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-25T18:04:23Z INF Registered tunnel connection connIndex=2 connection=8df3c464-b6b6-4e5a-9175-967c69e3c3aa event=0 ip=198.41.192.227 location=lax05 protocol=quic
[02:04:23] === STEP 7: 持久化 ===
[02:04:24] systemd 服务已配置
[02:04:24] Cron 保活已设置
[02:04:24] === STEP 8: 验证 ===
[02:04:24] --- API (localhost:8450) ---
 OK
[02:04:24] --- cloudflared 进程 ---
[02:04:24] Tunnel 连接已建立!
[02:04:24] --- cloudflared 日志 (最后 15 行) ---
root      377927  3.3  1.8 1360092 38100 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      377948  4.5  1.9 1359708 38220 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      378046  0.0  1.3 1292484 27160 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
2026-08-25T18:04:22Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-25T18:04:22Z INF Generated Connector ID: 65947156-3fc2-4601-8819-6f40c67f014c
2026-08-25T18:04:22Z INF Initial protocol quic
2026-08-25T18:04:22Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-25T18:04:22Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-25T18:04:22Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-25T18:04:22Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-25T18:04:22Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-25T18:04:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-25T18:04:22Z INF Registered tunnel connection connIndex=0 connection=eb5e323a-e73a-480a-a76d-b80e45626793 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-25T18:04:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-25T18:04:23Z INF Registered tunnel connection connIndex=1 connection=be41b555-07dc-4fd3-8b18-2b86bc65456d event=0 ip=198.41.192.107 location=lax10 protocol=quic
2026-08-25T18:04:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-25T18:04:24Z INF Registered tunnel connection connIndex=2 connection=f3b2fa95-6ba4-4ceb-b8c4-c088e51961b5 event=0 ip=198.41.200.53 location=lax01 protocol=quic
26-08-25T18:04:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
[02:04:24] --- aishield.tools ---
[02:04:24] === STEP 7: 持久化 ===
[02:04:25] systemd 服务已配置
[02:04:25] Cron 保活已设置
[02:04:25] === STEP 8: 验证 ===
[02:04:25] --- API (localhost:8450) ---
 OK
[02:04:25] --- cloudflared 进程 ---
root      377927  2.5  1.8 1360348 37016 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      377948  3.0  1.8 1359708 36808 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      378237  0.0  1.3 1292484 27468 ?       Rl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:04:25] --- aishield.tools ---
 OK
[02:04:26] --- DNS CNAME ---
[02:04:26] --- DNS A ---
104.21.81.46
172.67.188.44
[02:04:26] === 部署汇总 ===
[02:04:26] Tunnel Mode: cert
[02:04:26] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:26] API: http://localhost:8450
[02:04:26] 域名: https://aishield.tools
[02:04:26] cloudflared: /usr/local/bin/cloudflared
[02:04:26] PID: 377927
[02:04:26] Config: /root/.cloudflared/config.yml
[02:04:26] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:26] 状态: Named Tunnel (cert 模式) 已配置
 OK
[02:04:26] --- DNS CNAME ---
[02:04:26] --- DNS A ---
104.21.81.46
172.67.188.44
[02:04:26] === 部署汇总 ===
[02:04:26] Tunnel Mode: cert
[02:04:26] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:26] API: http://localhost:8450
[02:04:26] 域名: https://aishield.tools
[02:04:26] cloudflared: /usr/local/bin/cloudflared
[02:04:26] PID: 377948
[02:04:26] Config: /root/.cloudflared/config.yml
[02:04:26] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:26] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-26 02:04:25 CST; 6h ago
   Main PID: 378229 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 19.0M
        CPU: 36.629s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─378229 /bin/bash /opt/start-tunnel.sh
             └─378237 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 26 00:28:04 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787704084.5868483, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
