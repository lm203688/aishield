=== DIAGNOSTIC ===
Time: Wed Aug 12 11:13:55 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786547635.4002612, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      609700  2.0  1.9 1294420 39560 ?       Sl   23:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      609901  2.6  1.8 1293844 36688 ?       Sl   23:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-12T15:13:50Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-12T15:13:50Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-12T15:13:50Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-12T15:13:50Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-12T15:13:50Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-12T15:13:50Z INF Generated Connector ID: 48fa088c-b777-4bc7-9afb-8c87e882682d
2026-08-12T15:13:50Z INF Initial protocol quic
2026-08-12T15:13:50Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T15:13:50Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T15:13:50Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T15:13:50Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T15:13:50Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-12T15:13:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-12T15:13:50Z INF Registered tunnel connection connIndex=0 connection=80963ced-14e5-47dd-9239-bd6cbd8906fa event=0 ip=198.41.192.67 location=lax11 protocol=quic
2026-08-12T15:13:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-12T15:13:50Z INF Registered tunnel connection connIndex=1 connection=687c1aa5-f400-43dc-9c28-b14619f44708 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-12T15:13:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-08-12T15:13:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-08-12T15:13:53Z INF Registered tunnel connection connIndex=3 connection=84eb2f9f-9082-4091-86ef-c460e42a09ef event=0 ip=198.41.192.57 location=lax05 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:13:49] Time: Wed Aug 12 11:13:49 PM CST 2026
[23:13:49] User: root (UID: 0)
[23:13:49] === STEP 1: 启动 API (端口 8450) ===
[23:13:50] 启动 Named Tunnel (cert 模式)...
[23:13:50] 使用 config: /root/.cloudflared/config.yml
[23:13:50] cloudflared PID: 609700
[23:13:51] API 已在运行
[23:13:51] API 状态: OK
[23:13:51] === STEP 2: 安装 cloudflared ===
[23:13:51] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:13:51] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:13:51] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:13:51] === STEP 3: 检查认证方式 ===
[23:13:51] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:13:51] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:13:51] 检查现有 tunnel...
[23:13:52] Tunnel 连接已建立!
[23:13:52] --- cloudflared 日志 (最后 15 行) ---
2026-08-12T15:13:50Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-12T15:13:50Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-12T15:13:50Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-12T15:13:50Z INF Generated Connector ID: 48fa088c-b777-4bc7-9afb-8c87e882682d
2026-08-12T15:13:50Z INF Initial protocol quic
2026-08-12T15:13:50Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T15:13:50Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T15:13:50Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-12T15:13:50Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-12T15:13:50Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-12T15:13:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-12T15:13:50Z INF Registered tunnel connection connIndex=0 connection=80963ced-14e5-47dd-9239-bd6cbd8906fa event=0 ip=198.41.192.67 location=lax11 protocol=quic
2026-08-12T15:13:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-12T15:13:50Z INF Registered tunnel connection connIndex=1 connection=687c1aa5-f400-43dc-9c28-b14619f44708 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-12T15:13:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[23:13:52] === STEP 7: 持久化 ===
[23:13:52] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS      
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax01, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                  
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                  
[23:13:52] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:13:52] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:13:52] 凭证文件存在
[23:13:52] 创建 config.yml...
[23:13:52] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:13:52] systemd 服务已配置
[23:13:52] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:13:52] Cron 保活已设置
[23:13:52] === STEP 8: 验证 ===
[23:13:52] --- API (localhost:8450) ---
 OK
[23:13:52] --- cloudflared 进程 ---
root      609700  4.0  1.9 1294100 38580 ?       Sl   23:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      609901  0.0  1.3 1292740 27648 ?       Rl   23:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      609919  0.0  1.4 1292740 30064 ?       Sl   23:13   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
[23:13:52] --- aishield.tools ---
 OK
[23:13:54] --- DNS CNAME ---
[23:13:54] DNS 路由结果: 2026-08-12T15:13:54Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:13:54] === STEP 5: 更新 DNS (API) ===
[23:13:54] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:13:54] --- DNS A ---
172.67.188.44
104.21.81.46
[23:13:54] === 部署汇总 ===
[23:13:54] Tunnel Mode: cert
[23:13:54] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:13:54] API: http://localhost:8450
[23:13:54] 域名: https://aishield.tools
[23:13:54] cloudflared: /usr/local/bin/cloudflared
[23:13:54] PID: 609700
[23:13:54] Config: /root/.cloudflared/config.yml
[23:13:54] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:13:54] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-12 23:13:52 CST; 2s ago
   Main PID: 609891 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 16.2M
        CPU: 95ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─609891 /bin/bash /opt/start-tunnel.sh
             └─609901 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 12 15:13:55 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786547635.935015, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
