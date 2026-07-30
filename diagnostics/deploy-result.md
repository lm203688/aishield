=== DIAGNOSTIC ===
Time: Fri Jul 31 07:41:10 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785454870.0669055, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      427216  1.1  1.9 1294676 39288 ?       Sl   07:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      427359  1.2  1.9 1294676 39564 ?       Sl   07:41   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-07-30T23:41:00Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-07-30T23:41:00Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-07-30T23:41:00Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-07-30T23:41:00Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-07-30T23:41:00Z INF cloudflared will not automatically update if installed by a package manager.
2026-07-30T23:41:00Z INF Generated Connector ID: 8ed01a75-ded4-4854-83c6-1c36d725618d
2026-07-30T23:41:00Z INF Initial protocol quic
2026-07-30T23:41:00Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T23:41:00Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T23:41:00Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T23:41:00Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T23:41:00Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-07-30T23:41:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.57
2026-07-30T23:41:00Z INF Registered tunnel connection connIndex=0 connection=3211c6ba-02c4-4973-be35-69181a744d92 event=0 ip=198.41.192.57 location=lax09 protocol=quic
2026-07-30T23:41:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-07-30T23:41:00Z INF Registered tunnel connection connIndex=1 connection=2f16b6d5-8d67-4aef-9960-3eb0e082abca event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-07-30T23:41:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-07-30T23:41:01Z INF Registered tunnel connection connIndex=2 connection=5ae599e6-d75a-490b-9066-814b50e6cf53 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-07-30T23:41:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-07-30T23:41:02Z INF Registered tunnel connection connIndex=3 connection=2b092621-51a1-4a0c-b7c0-299a6491460d event=0 ip=198.41.192.47 location=lax08 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[07:40:51] Time: Fri Jul 31 07:40:51 AM CST 2026
[07:40:51] User: root (UID: 0)
[07:40:51] === STEP 1: 启动 API (端口 8450) ===
[07:40:52] API 已在运行
[07:40:52] API 状态: OK
[07:40:52] === STEP 2: 安装 cloudflared ===
[07:40:52] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:40:52] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:40:53] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:40:53] === STEP 3: 检查认证方式 ===
[07:40:53] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[07:40:53] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[07:40:53] 检查现有 tunnel...
[07:40:53] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax07, 2xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[07:40:53] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:40:53] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[07:40:53] 凭证文件存在
[07:40:53] 创建 config.yml...
[07:40:53] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[07:40:53] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:40:55] DNS 路由结果: 2026-07-30T23:40:55Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[07:40:55] === STEP 5: 更新 DNS (API) ===
[07:40:55] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:40:55] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[07:40:56] 设置 SSL 模式为 Full...
SSL: 跳过
[07:40:57] === STEP 6: 启动 Tunnel ===
[07:41:00] 启动 Named Tunnel (cert 模式)...
[07:41:00] 使用 config: /root/.cloudflared/config.yml
[07:41:00] cloudflared PID: 427216
[07:41:02] Tunnel 连接已建立!
[07:41:02] --- cloudflared 日志 (最后 15 行) ---
2026-07-30T23:41:00Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-07-30T23:41:00Z INF cloudflared will not automatically update if installed by a package manager.
2026-07-30T23:41:00Z INF Generated Connector ID: 8ed01a75-ded4-4854-83c6-1c36d725618d
2026-07-30T23:41:00Z INF Initial protocol quic
2026-07-30T23:41:00Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T23:41:00Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T23:41:00Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T23:41:00Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T23:41:00Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-07-30T23:41:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.57
2026-07-30T23:41:00Z INF Registered tunnel connection connIndex=0 connection=3211c6ba-02c4-4973-be35-69181a744d92 event=0 ip=198.41.192.57 location=lax09 protocol=quic
2026-07-30T23:41:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-07-30T23:41:00Z INF Registered tunnel connection connIndex=1 connection=2f16b6d5-8d67-4aef-9960-3eb0e082abca event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-07-30T23:41:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-07-30T23:41:01Z INF Registered tunnel connection connIndex=2 connection=5ae599e6-d75a-490b-9066-814b50e6cf53 event=0 ip=198.41.200.233 location=lax01 protocol=quic
[07:41:02] === STEP 7: 持久化 ===
[07:41:02] systemd 服务已配置
[07:41:02] Cron 保活已设置
[07:41:02] === STEP 8: 验证 ===
[07:41:02] --- API (localhost:8450) ---
 OK
[07:41:02] --- cloudflared 进程 ---
root      427216  4.5  1.9 1294420 38580 ?       Sl   07:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      427359  0.0  1.3 1292740 27264 ?       Rl   07:41   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[07:41:02] --- aishield.tools ---
 OK
[07:41:04] --- DNS CNAME ---
[07:41:04] --- DNS A ---
104.21.81.46
172.67.188.44
[07:41:04] === 部署汇总 ===
[07:41:04] Tunnel Mode: cert
[07:41:04] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:41:04] API: http://localhost:8450
[07:41:04] 域名: https://aishield.tools
[07:41:04] cloudflared: /usr/local/bin/cloudflared
[07:41:04] PID: 427216
[07:41:04] Config: /root/.cloudflared/config.yml
[07:41:04] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:41:04] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-07-31 07:41:02 CST; 7s ago
   Main PID: 427355 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 18.1M
        CPU: 120ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─427355 /bin/bash /opt/start-tunnel.sh
             └─427359 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Jul 30 23:41:10 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785454870.8745759, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
