=== DIAGNOSTIC ===
Time: Fri Aug 14 02:55:02 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786690502.2532713, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2172443  2.4  1.8 1294676 38080 ?       Sl   14:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2172472  2.7  1.9 1294420 38372 ?       Sl   14:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2172930 10.0  1.7 1294100 36044 ?       Sl   14:55   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T06:54:58Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-14T06:54:58Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-14T06:54:58Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-14T06:54:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T06:54:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T06:54:58Z INF Generated Connector ID: 37e77b88-b673-46c7-a036-8c66692b0870
2026-08-14T06:54:58Z INF Initial protocol quic
2026-08-14T06:54:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T06:54:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T06:54:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T06:54:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T06:54:58Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-14T06:54:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.10722026-08-14T06:54:59Z INF Registered tunnel connection connIndex=0 connection=69cceefa-0df6-4958-a448-40a6e2184461 event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-14T06:54:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.22022026-08-14T06:54:59Z INF Registered tunnel connection connIndex=1 connection=cd9bb41d-19b6-489d-b2be-0404588923c5 event=0 ip=198.41.200.233 location=lax01 protocol=q20262026-08-14T06:55:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.2002026-08-14T06:55:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.167
2026-08-14T06:55:01Z INF Registered tunnel connection connIndex=3 connection=c5ef76fb-416a-4de1-bf26-9f2cd9384e81 event=0 ip=198.41.192.167 location=lax10 protocol=quic
27
2026-08-14T06:55:02Z INF Registered tunnel connection connIndex=3 connection=c4d35bea-3e3c-403c-9bd0-aac4e0f9ead4 event=0 ip=198.41.192.227 location=lax10 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[14:54:52] Time: Fri Aug 14 02:54:52 PM CST 2026
[14:54:52] User: root (UID: 0)
[14:54:52] === STEP 1: 启动 API (端口 8450) ===
DNS 更新: OK
[14:54:53] 设置 SSL 模式为 Full...
[14:54:53] DNS 路由结果: 2026-08-14T06:54:53Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[14:54:53] === STEP 5: 更新 DNS (API) ===
[14:54:53] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:54:54] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[14:54:54] 设置 SSL 模式为 Full...
SSL: 跳过
[14:54:54] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[14:54:55] === STEP 6: 启动 Tunnel ===
[14:54:55] API 已在运行
[14:54:55] API 状态: OK
[14:54:55] === STEP 2: 安装 cloudflared ===
[14:54:55] cloudflared 安装路径: /usr/local/bin/cloudflared
[14:54:55] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:54:55] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:54:55] === STEP 3: 检查认证方式 ===
[14:54:55] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[14:54:55] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[14:54:55] 检查现有 tunnel...
[14:54:57] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
2026-08-14T06:54:57Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.1
[14:54:57] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:54:57] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[14:54:57] 凭证文件存在
[14:54:57] 创建 config.yml...
[14:54:57] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[14:54:57] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:54:57] 启动 Named Tunnel (cert 模式)...
[14:54:57] 使用 config: /root/.cloudflared/config.yml
[14:54:57] cloudflared PID: 2172443
[14:54:58] 启动 Named Tunnel (cert 模式)...
[14:54:58] 使用 config: /root/.cloudflared/config.yml
[14:54:58] cloudflared PID: 2172472
[14:54:59] Tunnel 连接已建立!
[14:54:59] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T06:54:58Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-14T06:54:58Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-14T06:54:58Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-14T06:54:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T06:54:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T06:54:58Z INF Generated Connector ID: 37e77b88-b673-46c7-a036-8c66692b0870
2026-08-14T06:54:58Z INF Initial protocol quic
2026-08-14T06:54:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T06:54:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T06:54:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T06:54:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T06:54:58Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-14T06:54:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.10722026-08-14T06:54:59Z INF Registered tunnel connection connIndex=0 connection=69cceefa-0df6-4958-a448-40a6e2184461 event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-14T06:54:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.22022026-08-14T06:54:59Z INF Registered tunnel connection connIndex=1 connection=cd9bb41d-19b6-489d-b2be-0404588923c5 event=0 ip=198.41.200.233 location=lax01 protocol=q2026-08-14T06:54:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[14:54:59] === STEP 7: 持久化 ===
[14:55:00] DNS 路由结果: 2026-08-14T06:55:00Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[14:55:00] === STEP 5: 更新 DNS (API) ===
[14:55:00] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:55:00] Tunnel 连接已建立!
[14:55:00] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T06:54:58Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-14T06:54:58Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-14T06:54:58Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-14T06:54:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T06:54:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T06:54:58Z INF Generated Connector ID: 37e77b88-b673-46c7-a036-8c66692b0870
2026-08-14T06:54:58Z INF Initial protocol quic
2026-08-14T06:54:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T06:54:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T06:54:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T06:54:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T06:54:58Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-14T06:54:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.10722026-08-14T06:54:59Z INF Registered tunnel connection connIndex=0 connection=69cceefa-0df6-4958-a448-40a6e2184461 event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-14T06:54:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.22022026-08-14T06:54:59Z INF Registered tunnel connection connIndex=1 connection=cd9bb41d-19b6-489d-b2be-0404588923c5 event=0 ip=198.41.200.233 location=lax01 protocol=q20262026-08-14T06:55:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-14T06:55:00Z INF Registered tunnel connection connIndex=2 connection=e47de46f-4894-45ce-b855-932ae927cd32 event=0 ip=198.41.200.33 location=lax01 protocol=quic
[14:55:00] === STEP 7: 持久化 ===
[14:55:00] systemd 服务已配置
[14:55:00] Cron 保活已设置
[14:55:00] === STEP 8: 验证 ===
[14:55:00] --- API (localhost:8450) ---
 OK
[14:55:01] --- cloudflared 进程 ---
[14:55:01] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
root     2172443  3.0  1.9 1294676 38752 ?       Rl   14:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2172472  3.3  1.9 1294420 38352 ?       Sl   14:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2172631 10.0  1.7 1293844 35596 ?       Sl   14:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[14:55:01] --- aishield.tools ---
[14:55:01] systemd 服务已配置
[14:55:01] Cron 保活已设置
[14:55:01] === STEP 8: 验证 ===
[14:55:01] --- API (localhost:8450) ---
 OK
[14:55:01] --- cloudflared 进程 ---
root     2172443  3.0  1.9 1294676 38208 ?       Sl   14:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2172472  3.6  1.9 1294420 38260 ?       Sl   14:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2172930  0.0  1.3 1292740 26824 ?       Dl   14:55   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[14:55:01] --- aishield.tools ---
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-14 14:55:01 CST; 449ms ago
   Main PID: 2172926 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 18.0M
        CPU: 113ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2172926 /bin/bash /opt/start-tunnel.sh
             └─2172930 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 06:55:02 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786690503.445131, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
