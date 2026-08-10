=== DIAGNOSTIC ===
Time: Mon Aug 10 12:31:37 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786336297.2339869, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2495137  8.0  1.8 1294100 37488 ?       Sl   12:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-10T04:31:36Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-10T04:31:36Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-10T04:31:36Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T04:31:36Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T04:31:36Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T04:31:36Z INF Generated Connector ID: c5dddb8e-bf49-4803-b4a3-2f0467a585b7
2026-08-10T04:31:36Z INF Initial protocol quic
2026-08-10T04:31:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T04:31:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T04:31:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T04:31:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T04:31:36Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-10T04:31:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-10T04:31:36Z INF Registered tunnel connection connIndex=0 connection=871fc740-1422-4212-94eb-28183a04bc27 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-10T04:31:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:29:55] Time: Mon Aug 10 12:29:55 PM CST 2026
[12:29:55] User: root (UID: 0)
[12:29:55] === STEP 1: 启动 API (端口 8450) ===
[12:31:17] API 已在运行
[12:31:17] API 状态: OK
[12:31:17] === STEP 2: 安装 cloudflared ===
[12:31:17] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:31:17] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:31:17] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:31:17] === STEP 3: 检查认证方式 ===
[12:31:17] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:31:17] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:31:17] 检查现有 tunnel...
[12:31:19] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 1xlax10, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[12:31:19] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:31:19] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:31:19] 凭证文件存在
[12:31:19] 创建 config.yml...
[12:31:19] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:31:19] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:31:21] DNS 路由结果: 2026-08-10T04:31:21Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:31:21] === STEP 5: 更新 DNS (API) ===
[12:31:21] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:31:22] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[12:31:23] 设置 SSL 模式为 Full...
SSL: 跳过
[12:31:24] === STEP 6: 启动 Tunnel ===
[12:31:26] API 已在运行
[12:31:26] API 状态: OK
[12:31:26] === STEP 2: 安装 cloudflared ===
[12:31:26] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:31:26] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:31:26] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:31:26] === STEP 3: 检查认证方式 ===
[12:31:26] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:31:26] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:31:26] 检查现有 tunnel...
[12:31:27] 启动 Named Tunnel (cert 模式)...
[12:31:27] 使用 config: /root/.cloudflared/config.yml
[12:31:27] cloudflared PID: 2494719
[12:31:27] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax10     
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[12:31:27] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:31:27] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:31:27] 凭证文件存在
[12:31:27] 创建 config.yml...
[12:31:27] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:31:27] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:31:29] Tunnel 连接已建立!
[12:31:29] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T04:31:27Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T04:31:27Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T04:31:27Z INF Generated Connector ID: 4747e716-7de0-4540-98de-ba99267dcae2
2026-08-10T04:31:27Z INF Initial protocol quic
2026-08-10T04:31:27Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T04:31:27Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T04:31:27Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T04:31:27Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T04:31:27Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-10T04:31:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-10T04:31:27Z INF Registered tunnel connection connIndex=0 connection=396d81f9-7321-4274-9fb0-89280efafe0e event=0 ip=198.41.192.27 location=lax10 protocol=quic
2026-08-10T04:31:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-10T04:31:28Z INF Registered tunnel connection connIndex=1 connection=6d14f5a6-10fc-4791-8558-7bcaa84d6b32 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-10T04:31:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-10T04:31:29Z INF Registered tunnel connection connIndex=2 connection=26a30c69-c1aa-4e6c-a835-48da151c5ed6 event=0 ip=198.41.192.167 location=lax11 protocol=quic
[12:31:29] === STEP 7: 持久化 ===
[12:31:29] DNS 路由结果: 2026-08-10T04:31:29Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:31:29] === STEP 5: 更新 DNS (API) ===
[12:31:29] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:31:29] systemd 服务已配置
[12:31:29] Cron 保活已设置
[12:31:29] === STEP 8: 验证 ===
[12:31:29] --- API (localhost:8450) ---
 OK
[12:31:29] --- cloudflared 进程 ---
root     2494719  5.0  1.9 1294420 38932 ?       Sl   12:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2494878  0.0  1.3 1292484 27652 ?       Sl   12:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:31:29] --- aishield.tools ---
[12:31:30] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
 OK
[12:31:31] --- DNS CNAME ---
[12:31:32] --- DNS A ---
172.67.188.44
104.21.81.46
[12:31:32] === 部署汇总 ===
[12:31:32] Tunnel Mode: cert
[12:31:32] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:31:32] API: http://localhost:8450
[12:31:32] 域名: https://aishield.tools
[12:31:32] cloudflared: /usr/local/bin/cloudflared
[12:31:32] PID: 2494719
[12:31:32] Config: /root/.cloudflared/config.yml
[12:31:32] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:31:32] 状态: Named Tunnel (cert 模式) 已配置
DNS 更新: OK
[12:31:32] 设置 SSL 模式为 Full...
SSL: 跳过
[12:31:33] === STEP 6: 启动 Tunnel ===
[12:31:36] 启动 Named Tunnel (cert 模式)...
[12:31:36] 使用 config: /root/.cloudflared/config.yml
[12:31:36] cloudflared PID: 2495137
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) since Mon 2026-08-10 12:31:33 CST; 3s ago
    Process: 2494870 ExecStart=/opt/start-tunnel.sh (code=exited, status=0/SUCCESS)
   Main PID: 2494870 (code=exited, status=0/SUCCESS)
        CPU: 137ms

Aug 10 12:31:33 VM-0-11-ubuntu systemd[1]: cloudflared-tunnel.service: Deactivated successfully.
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                   
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
Time: Mon Aug 10 04:31:37 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786336297.8863122, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
