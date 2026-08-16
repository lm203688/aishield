=== DIAGNOSTIC ===
Time: Mon Aug 17 04:05:04 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786910704.2716944, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      303966  0.1  1.5 1294676 32116 ?       Sl   01:59   0:11 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      304165  0.1  1.5 1294676 31844 ?       Sl   01:59   0:11 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-16T17:59:43Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-16T17:59:43Z INF +-------------------------------------------------------------------------------------+
2026-08-16T17:59:43Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=43ad8732-a2e5-43eb-b6c0-87b560a50cbf status=pass target=region1.v2.argotunnel.com
2026-08-16T17:59:43Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=43ad8732-a2e5-43eb-b6c0-87b560a50cbf status=pass target=region2.v2.argotunnel.com
2026-08-16T17:59:43Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=43ad8732-a2e5-43eb-b6c0-87b560a50cbf status=pass target=region1.v2.argotunnel.com
2026-08-16T17:59:43Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=43ad8732-a2e5-43eb-b6c0-87b560a50cbf status=pass target=region2.v2.argotunnel.com
2026-08-16T17:59:43Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=43ad8732-a2e5-43eb-b6c0-87b560a50cbf status=pass target=region1.v2.argotunnel.com
2026-08-16T17:59:43Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=43ad8732-a2e5-43eb-b6c0-87b560a50cbf status=pass target=region2.v2.argotunnel.com
2026-08-16T17:59:43Z INF precheck component="Cloudflare API" details="API is reachable" run_id=43ad8732-a2e5-43eb-b6c0-87b560a50cbf status=pass target=api.cloudflare.com:443
2026-08-16T17:59:43Z INF precheck complete hard_fail=false run_id=43ad8732-a2e5-43eb-b6c0-87b560a50cbf suggested_protocol=quic
2026-08-16T17:59:43Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.37
2026-08-16T17:59:44Z INF Registered tunnel connection connIndex=2 connection=5233126e-7670-4469-b44e-64a7c426335f event=0 ip=198.41.192.37 location=lax09 protocol=quic
2026-08-16T17:59:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.193
2026-08-16T17:59:49Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-16T17:59:49Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-08-16T17:59:51Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-16T18:00:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
2026-08-16T18:00:13Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-08-16T18:00:13Z INF Retrying connection in up to 4s connIndex=3 event=0 ip=198.41.200.73
2026-08-16T18:00:13Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-16T18:00:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.193
2026-08-16T18:00:30Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-16T18:00:30Z INF Retrying connection in up to 8s connIndex=3 event=0 ip=198.41.200.193
2026-08-16T18:00:37Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-16T18:01:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
2026-08-16T18:01:14Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-08-16T18:01:14Z INF Retrying connection in up to 16s connIndex=3 event=0 ip=198.41.200.73
2026-08-16T18:01:21Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-16T18:03:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-16T18:03:54Z INF Registered tunnel connection connIndex=3 connection=f7320d2f-af66-4531-806c-d50be421b427 event=0 ip=198.41.200.233 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[01:59:28] Time: Mon Aug 17 01:59:28 AM CST 2026
[01:59:28] User: root (UID: 0)
[01:59:28] === STEP 1: 启动 API (端口 8450) ===
[01:59:29] API 已在运行
[01:59:29] API 状态: OK
[01:59:29] === STEP 2: 安装 cloudflared ===
[01:59:29] cloudflared 安装路径: /usr/local/bin/cloudflared
[01:59:29] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[01:59:29] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[01:59:29] === STEP 3: 检查认证方式 ===
[01:59:29] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[01:59:29] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[01:59:29] 检查现有 tunnel...
[01:59:29] Tunnel 连接已建立!
[01:59:29] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T17:59:27Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-16T17:59:27Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-16T17:59:27Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-16T17:59:27Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-16T17:59:27Z INF Generated Connector ID: f7c070e8-d39a-4ecd-bc45-3346956cf4a7
2026-08-16T17:59:27Z INF Initial protocol quic
2026-08-16T17:59:27Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T17:59:27Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T17:59:27Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T17:59:27Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T17:59:27Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-16T17:59:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-16T17:59:28Z INF Registered tunnel connection connIndex=0 connection=46aaf8cd-5f34-4edd-924f-3664c7790b5c event=0 ip=198.41.192.227 location=lax09 protocol=quic
2026-08-16T17:59:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
2026-08-16T17:59:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
[01:59:29] === STEP 7: 持久化 ===
[01:59:30] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS      
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax08, 1xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                  
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                  
[01:59:30] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:30] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[01:59:30] 凭证文件存在
[01:59:30] 创建 config.yml...
[01:59:30] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[01:59:30] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:30] systemd 服务已配置
[01:59:30] Cron 保活已设置
[01:59:30] === STEP 8: 验证 ===
[01:59:30] --- API (localhost:8450) ---
 OK
[01:59:30] --- cloudflared 进程 ---
root      303480  3.3  1.9 1294420 38960 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      303718  0.0  1.5 1292740 30428 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
root      303724  0.0  1.3 1292740 26808 ?       Rl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[01:59:30] --- aishield.tools ---
[01:59:31] DNS 路由结果: 2026-08-16T17:59:31Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:31] === STEP 5: 更新 DNS (API) ===
[01:59:31] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
 OK
[01:59:32] --- DNS CNAME ---
[01:59:32] --- DNS A ---
172.67.188.44
104.21.81.46
[01:59:32] === 部署汇总 ===
[01:59:32] Tunnel Mode: cert
[01:59:32] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:32] API: http://localhost:8450
[01:59:32] 域名: https://aishield.tools
[01:59:32] cloudflared: /usr/local/bin/cloudflared
[01:59:32] PID: 303480
[01:59:32] Config: /root/.cloudflared/config.yml
[01:59:32] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:32] 状态: Named Tunnel (cert 模式) 已配置
[01:59:32] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[01:59:33] 设置 SSL 模式为 Full...
SSL: 跳过
[01:59:33] === STEP 6: 启动 Tunnel ===
[01:59:36] 启动 Named Tunnel (cert 模式)...
[01:59:36] 使用 config: /root/.cloudflared/config.yml
[01:59:36] cloudflared PID: 303966
[01:59:42] Tunnel 连接已建立!
[01:59:42] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T17:59:37Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-16T17:59:37Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-16T17:59:37Z INF Generated Connector ID: cbb8ef3e-95c6-4ab7-b521-b94c2245618d
2026-08-16T17:59:37Z INF Initial protocol quic
2026-08-16T17:59:37Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T17:59:37Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T17:59:37Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T17:59:37Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T17:59:37Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-16T17:59:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.193
2026-08-16T17:59:42Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-16T17:59:42Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.193
2026-08-16T17:59:42Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-16T17:59:42Z INF Registered tunnel connection connIndex=0 connection=547e60d8-5746-4004-ac90-6478fc21f874 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-16T17:59:42Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
[01:59:42] === STEP 7: 持久化 ===
[01:59:43] systemd 服务已配置
[01:59:43] Cron 保活已设置
[01:59:43] === STEP 8: 验证 ===
[01:59:43] --- API (localhost:8450) ---
 OK
[01:59:43] --- cloudflared 进程 ---
root      303966  1.5  1.9 1294100 38688 ?       Sl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      304165  0.0  1.3 1292484 27228 ?       Rl   01:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[01:59:43] --- aishield.tools ---
 OK
[01:59:44] --- DNS CNAME ---
[01:59:45] --- DNS A ---
104.21.81.46
172.67.188.44
[01:59:45] === 部署汇总 ===
[01:59:45] Tunnel Mode: cert
[01:59:45] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:59:45] API: http://localhost:8450
[01:59:45] 域名: https://aishield.tools
[01:59:45] cloudflared: /usr/local/bin/cloudflared
[01:59:45] PID: 303966
[01:59:45] Config: /root/.cloudflared/config.yml
[01:59:45] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:59:45] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-17 01:59:43 CST; 2h 5min ago
   Main PID: 304157 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.4M
        CPU: 11.678s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─304157 /bin/bash /opt/start-tunnel.sh
             └─304165 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sun Aug 16 20:05:04 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786910704.786099, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
