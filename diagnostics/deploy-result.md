=== DIAGNOSTIC ===
Time: Tue Aug 4 11:09:17 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785856157.425799, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      995510  0.8  1.9 1294420 38448 ?       Sl   23:09   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      995602  1.0  1.9 1294676 38476 ?       Sl   23:09   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-04T15:09:03Z INF Registered tunnel connection connIndex=0 connection=8fe81d27-c5ab-4ca3-b803-969b85b175e0 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-04T15:09:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-04T15:09:04Z INF Registered tunnel connection connIndex=1 connection=55d6096f-1a7d-41cf-8e3f-ba3ddf15953f event=0 ip=198.41.192.107 location=lax11 protocol=quic
2026-08-04T15:09:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-04T15:09:05Z INF Registered tunnel connection connIndex=2 connection=74b4f1fc-64f7-4e42-a3d7-b3c89d5af7ef event=0 ip=198.41.192.167 location=lax08 protocol=quic
2026-08-04T15:09:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.13
2026-08-04T15:09:06Z INF Registered tunnel connection connIndex=3 connection=5be372cc-098b-4cca-97cb-c5bf5cf469d6 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-04T15:09:13Z INF +-----------------------------------------------------------------------------------------------+
2026-08-04T15:09:13Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-04T15:09:13Z INF +-----------------------------------------------------------------------------------------------+
2026-08-04T15:09:13Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-04T15:09:13Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-04T15:09:13Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-04T15:09:13Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-04T15:09:13Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-04T15:09:13Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-04T15:09:13Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-04T15:09:13Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-04T15:09:13Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-04T15:09:13Z INF |                                                                                               |
2026-08-04T15:09:13Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-04T15:09:13Z INF +-----------------------------------------------------------------------------------------------+
2026-08-04T15:09:13Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=1e825868-8725-43ba-9e4f-d9a5d2ea7657 status=pass target=region1.v2.argotunnel.com
2026-08-04T15:09:13Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=1e825868-8725-43ba-9e4f-d9a5d2ea7657 status=pass target=region2.v2.argotunnel.com
2026-08-04T15:09:13Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=1e825868-8725-43ba-9e4f-d9a5d2ea7657 status=pass target=region1.v2.argotunnel.com
2026-08-04T15:09:13Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=1e825868-8725-43ba-9e4f-d9a5d2ea7657 status=fail target=region2.v2.argotunnel.com
2026-08-04T15:09:13Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=1e825868-8725-43ba-9e4f-d9a5d2ea7657 status=pass target=region1.v2.argotunnel.com
2026-08-04T15:09:13Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=1e825868-8725-43ba-9e4f-d9a5d2ea7657 status=pass target=region2.v2.argotunnel.com
2026-08-04T15:09:13Z INF precheck component="Cloudflare API" details="API is reachable" run_id=1e825868-8725-43ba-9e4f-d9a5d2ea7657 status=pass target=api.cloudflare.com:443
2026-08-04T15:09:13Z INF precheck complete hard_fail=false run_id=1e825868-8725-43ba-9e4f-d9a5d2ea7657 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:08:51] Time: Tue Aug  4 11:08:51 PM CST 2026
[23:08:51] User: root (UID: 0)
[23:08:51] === STEP 1: 启动 API (端口 8450) ===
[23:08:53] API 已在运行
[23:08:53] API 状态: OK
[23:08:53] === STEP 2: 安装 cloudflared ===
[23:08:53] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:08:53] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:08:53] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:08:53] === STEP 3: 检查认证方式 ===
[23:08:53] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:08:53] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:08:53] 检查现有 tunnel...
[23:08:54] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax05, 1xlax07, 1xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[23:08:54] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:08:54] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:08:54] 凭证文件存在
[23:08:54] 创建 config.yml...
[23:08:54] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:08:54] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:08:55] DNS 路由结果: 2026-08-04T15:08:55Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:08:55] === STEP 5: 更新 DNS (API) ===
[23:08:55] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:08:57] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[23:08:58] 设置 SSL 模式为 Full...
SSL: 跳过
[23:09:00] === STEP 6: 启动 Tunnel ===
[23:09:03] 启动 Named Tunnel (cert 模式)...
[23:09:03] 使用 config: /root/.cloudflared/config.yml
[23:09:03] cloudflared PID: 995510
[23:09:05] Tunnel 连接已建立!
[23:09:05] --- cloudflared 日志 (最后 15 行) ---
2026-08-04T15:09:03Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-04T15:09:03Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-04T15:09:03Z INF Generated Connector ID: 2cf7b1fb-4cce-4265-9700-ed46591f3dc3
2026-08-04T15:09:03Z INF Initial protocol quic
2026-08-04T15:09:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-04T15:09:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-04T15:09:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-04T15:09:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-04T15:09:03Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-04T15:09:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-04T15:09:03Z INF Registered tunnel connection connIndex=0 connection=8fe81d27-c5ab-4ca3-b803-969b85b175e0 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-04T15:09:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-04T15:09:04Z INF Registered tunnel connection connIndex=1 connection=55d6096f-1a7d-41cf-8e3f-ba3ddf15953f event=0 ip=198.41.192.107 location=lax11 protocol=quic
2026-08-04T15:09:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-04T15:09:05Z INF Registered tunnel connection connIndex=2 connection=74b4f1fc-64f7-4e42-a3d7-b3c89d5af7ef event=0 ip=198.41.192.167 location=lax08 protocol=quic
[23:09:05] === STEP 7: 持久化 ===
[23:09:05] systemd 服务已配置
[23:09:05] Cron 保活已设置
[23:09:05] === STEP 8: 验证 ===
[23:09:05] --- API (localhost:8450) ---
 OK
[23:09:05] --- cloudflared 进程 ---
root      995510  4.5  1.9 1294420 39324 ?       Sl   23:09   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      995602  0.0  1.3 1292484 27316 ?       Sl   23:09   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[23:09:05] --- aishield.tools ---
 OK
[23:09:08] --- DNS CNAME ---
[23:09:08] --- DNS A ---
104.21.81.46
172.67.188.44
[23:09:08] === 部署汇总 ===
[23:09:08] Tunnel Mode: cert
[23:09:08] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:09:08] API: http://localhost:8450
[23:09:08] 域名: https://aishield.tools
[23:09:08] cloudflared: /usr/local/bin/cloudflared
[23:09:08] PID: 995510
[23:09:08] Config: /root/.cloudflared/config.yml
[23:09:08] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:09:08] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-04 23:09:05 CST; 11s ago
   Main PID: 995601 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.3M
        CPU: 142ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─995601 /bin/bash /opt/start-tunnel.sh
             └─995602 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Tue Aug  4 15:09:17 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785856158.187498, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
