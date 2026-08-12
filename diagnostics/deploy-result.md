=== DIAGNOSTIC ===
Time: Wed Aug 12 03:29:37 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786519777.8126516, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      302437  2.7  1.9 1294420 39532 ?       Sl   15:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      302608  4.0  1.6 1293844 33936 ?       Sl   15:29   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
root      302654 10.0  1.9 1294676 38928 ?       Sl   15:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-12T07:29:33Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-12T07:29:33Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
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
2026-08-12T07:29:35Z INF Registered tunnel connection connIndex=2 connection=4068101b-82d5-4190-ac94-1cfe10e21337 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-12T07:29:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-08-12T07:29:36Z INF Registered tunnel connection connIndex=3 connection=9553bec7-714f-49bb-8110-9205c82608a7 event=0 ip=198.41.192.57 location=lax11 protocol=quic
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
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-12 15:29:36 CST; 1s ago
   Main PID: 302646 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.0M
        CPU: 106ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─302646 /bin/bash /opt/start-tunnel.sh
             └─302654 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 12 07:29:38 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786519778.4664114, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
