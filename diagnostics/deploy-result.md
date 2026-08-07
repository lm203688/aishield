=== DIAGNOSTIC ===
Time: Fri Aug 7 12:01:09 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786075269.8834038, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3648275  2.2  1.9 1360284 39580 ?       Sl   12:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3648449  3.6  1.9 1294092 38656 ?       Sl   12:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3648460  2.3  1.6 1293836 33420 ?       Sl   12:01   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
root     3648668  6.0  1.7 1293844 34196 ?       Sl   12:01   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-07T04:01:06Z INF Thank you for trying Cloudflare Tunnel. Doing so, without a Cloudflare account, is a quick way to experiment and try it out. However, be aware that these account-less Tunnels have no uptime guarantee, are subject to the Cloudflare Online Services Terms of Use (https://www.cloudflare.com/website-terms/), and Cloudflare reserves the right to investigate your use of Tunnels for violations of such terms. If you intend to use Tunnels in production you should use a pre-created named tunnel by following: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps
2026-08-07T04:01:06Z INF Requesting new quick Tunnel on trycloudflare.com...
84ea61a7f8ae
2026-08-07T04:01:06Z INF Initial protocol quic
2026-08-07T04:01:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T04:01:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T04:01:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T04:01:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T04:01:06Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-07T04:01:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-07T04:01:07Z INF Registered tunnel connection connIndex=0 connection=e289a636-8f18-4438-b063-80a0b52c0269 event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-07T04:01:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-07T04:01:07Z INF Registered tunnel connection connIndex=1 connection=2ef0f9be-828b-47e8-b4fb-c0c10b36b696 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-07T04:01:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-08-07T04:01:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.37
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:01:07] Time: Fri Aug  7 12:01:07 PM CST 2026
[12:01:07] User: root (UID: 0)
[12:01:07] === STEP 1: 启动 API (端口 8450) ===
[12:01:08] API 已在运行
[12:01:08] API 状态: OK
[12:01:08] === STEP 2: 安装 cloudflared ===
[12:01:08] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:01:08] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:01:08] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:01:08] === STEP 3: 检查认证方式 ===
[12:01:08] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:01:08] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:01:08] 检查现有 tunnel...
[12:01:08] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xlax01, 1xlax07, 1xlax09, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[12:01:08] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:01:08] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:01:08] 凭证文件存在
[12:01:08] 创建 config.yml...
[12:01:08] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:01:08] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-07 12:01:04 CST; 5s ago
   Main PID: 3648274 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.5M
        CPU: 119ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3648274 /bin/bash /opt/start-tunnel.sh
             └─3648275 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug  7 04:01:10 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786075270.638427, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
