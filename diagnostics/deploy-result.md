=== DIAGNOSTIC ===
Time: Wed Aug 5 09:43:56 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785894236.2493188, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1458989  1.4  1.7 1360284 35644 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1459009  2.1  1.7 1360028 36000 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1459024  1.5  1.7 1293844 34760 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
root     1459129  1.5  1.7 1294100 35832 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
root     1459815  6.0  1.4 1292740 30088 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1460062  5.0  1.4 1292740 29512 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel list
root     1460122  0.0  1.5 1292740 30712 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel list
=== CLOUDFLARED LOG (last 30 lines) ===
error parsing tunnel ID: You is neither the ID nor the name of any of your tunnels
a Cloudflare account, is a quick way to experiment and try it out. However, be aware that these account-less Tunnels have no uptime guarantee, are subject to the Cloudflare Online Services Terms of Use (https://www.cloudflare.com/website-terms/), and Cloudflare reserves the right to investigate your use of Tunnels for violations of such terms. If you intend to use Tunnels in production you should use a pre-created named tunnel by following: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps
2026-08-05T01:43:50Z INF Requesting new quick Tunnel on trycloudflare.com...
2026-08-05T01:43:55Z INF +--------------------------------------------------------------------------------------------+
2026-08-05T01:43:55Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2026-08-05T01:43:55Z INF |  https://til-excerpt-measurement-indicator.trycloudflare.com                               |
2026-08-05T01:43:55Z INF +--------------------------------------------------------------------------------------------+
2026-08-05T01:43:55Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-05T01:43:55Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-05T01:43:55Z INF Settings: map[cred-file:/root/.cloudflared/You.json credentials-file:/root/.cloudflared/You.json ha-connections:1 protocol:quic url:http://localhost:8450]
2026-08-05T01:43:55Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T01:43:55Z INF Generated Connector ID: 5fbc2b7b-011f-401e-a812-0a3a87ef8ad9
2026-08-05T01:43:55Z INF Initial protocol quic
2026-08-05T01:43:55Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T01:43:55Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T01:43:55Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T01:43:55Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T01:43:55Z INF Starting metrics server on 127.0.0.1:20244/metrics
2026-08-05T01:43:55Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
68 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-08-05T01:43:56Z INF Registered tunnel connection connIndex=0 connection=02d1beef-81c2-400b-abf3-b6af5262c801 event=0 ip=198.41.192.77 location=lax07 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[09:43:54] Time: Wed Aug  5 09:43:54 AM CST 2026
[09:43:54] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[09:43:54] User: root (UID: 0)
[09:43:54] === STEP 1: 启动 API (端口 8450) ===
[09:43:55] systemd 服务已配置
[09:43:55] systemd 服务已配置
[09:43:55] systemd 服务已配置
[09:43:55] Cron 保活已设置
[09:43:55] Cron 保活已设置
[09:43:55] === STEP 8: 验证 ===
[09:43:55] Cron 保活已设置
[09:43:55] === STEP 8: 验证 ===
[09:43:55] --- API (localhost:8450) ---
[09:43:55] --- API (localhost:8450) ---
[09:43:55] === STEP 8: 验证 ===
[09:43:55] --- API (localhost:8450) ---
[09:43:55] API 已在运行
 OK
 OK
[09:43:55] --- cloudflared 进程 ---
[09:43:55] --- cloudflared 进程 ---
 OK
[09:43:55] API 状态: OK
[09:43:55] --- cloudflared 进程 ---
[09:43:55] === STEP 2: 安装 cloudflared ===
root     1458989  1.6  1.8 1360284 37360 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1459009  2.6  1.8 1360028 37264 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1459024  1.8  1.7 1293844 34756 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
root     1458989  1.6  1.8 1360284 37360 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1459009  2.6  1.8 1360028 37264 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1459024  1.8  1.7 1293844 34756 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
[09:43:55] cloudflared 安装路径: /usr/local/bin/cloudflared
root     1458989  1.6  1.8 1360284 37360 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1459009  2.6  1.8 1360028 37264 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1459024  1.8  1.7 1293844 34756 ?       Sl   09:43   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
[09:43:55] --- aishield.tools ---
[09:43:55] --- aishield.tools ---
[09:43:55] --- aishield.tools ---
[09:43:55] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:43:55] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:43:55] === STEP 3: 检查认证方式 ===
[09:43:55] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:43:55] API 已在运行
[09:43:55] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:43:55] 检查现有 tunnel...
[09:43:55] API 状态: OK
[09:43:55] === STEP 2: 安装 cloudflared ===
[09:43:55] cloudflared 安装路径: /usr/local/bin/cloudflared
[09:43:55] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:43:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:43:56] === STEP 3: 检查认证方式 ===
[09:43:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:43:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:43:56] 检查现有 tunnel...
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 09:43:55 CST; 973ms ago
   Main PID: 1459813 (start-tunnel.sh)
      Tasks: 6 (limit: 2216)
     Memory: 13.9M
        CPU: 80ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1459813 /bin/bash /opt/start-tunnel.sh
             └─1459815 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug  5 01:43:56 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785894237.5397456, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===

=== HTTPS Test from Runner ===
Time: Wed Aug  5 01:43:55 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785894235.6678276, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
