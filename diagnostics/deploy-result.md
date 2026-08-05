=== DIAGNOSTIC ===
Time: Wed Aug 5 12:22:48 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785903768.694917, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1584203  1.0  1.9 1360284 39144 ?       Sl   12:22   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1584385  1.2  1.9 1294676 39528 ?       Sl   12:22   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-05T04:22:36Z INF Registered tunnel connection connIndex=0 connection=3b921603-075b-4db7-b98b-2f0de87c89e9 event=0 ip=198.41.192.107 location=lax05 protocol=quic
2026-08-05T04:22:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-05T04:22:37Z INF Registered tunnel connection connIndex=1 connection=18ee7789-3a46-4e30-b668-12637830ccf9 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-05T04:22:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-05T04:22:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.33
2026-08-05T04:22:39Z INF Registered tunnel connection connIndex=2 connection=e7082afe-2788-4605-bd12-4b7edd81adfa event=0 ip=198.41.192.227 location=lax08 protocol=quic
2026-08-05T04:22:39Z INF Registered tunnel connection connIndex=3 connection=0460a13a-7051-41ad-85f7-a24607af39b2 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-05T04:22:46Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T04:22:46Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-05T04:22:46Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T04:22:46Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-05T04:22:46Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-05T04:22:46Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-05T04:22:46Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-05T04:22:46Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-05T04:22:46Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-05T04:22:46Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-05T04:22:46Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-05T04:22:46Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-05T04:22:46Z INF |                                                                                               |
2026-08-05T04:22:46Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-05T04:22:46Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T04:22:46Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=95903685-51a8-4f58-b837-b774b617e806 status=pass target=region1.v2.argotunnel.com
2026-08-05T04:22:46Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=95903685-51a8-4f58-b837-b774b617e806 status=pass target=region2.v2.argotunnel.com
2026-08-05T04:22:46Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=95903685-51a8-4f58-b837-b774b617e806 status=pass target=region1.v2.argotunnel.com
2026-08-05T04:22:46Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=95903685-51a8-4f58-b837-b774b617e806 status=fail target=region2.v2.argotunnel.com
2026-08-05T04:22:46Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=95903685-51a8-4f58-b837-b774b617e806 status=pass target=region1.v2.argotunnel.com
2026-08-05T04:22:46Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=95903685-51a8-4f58-b837-b774b617e806 status=pass target=region2.v2.argotunnel.com
2026-08-05T04:22:46Z INF precheck component="Cloudflare API" details="API is reachable" run_id=95903685-51a8-4f58-b837-b774b617e806 status=pass target=api.cloudflare.com:443
2026-08-05T04:22:46Z INF precheck complete hard_fail=false run_id=95903685-51a8-4f58-b837-b774b617e806 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:22:24] Time: Wed Aug  5 12:22:24 PM CST 2026
[12:22:24] User: root (UID: 0)
[12:22:24] === STEP 1: 启动 API (端口 8450) ===
[12:22:26] API 已在运行
[12:22:26] API 状态: OK
[12:22:26] === STEP 2: 安装 cloudflared ===
[12:22:26] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:22:26] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:22:26] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:22:26] === STEP 3: 检查认证方式 ===
[12:22:26] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:22:26] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:22:26] 检查现有 tunnel...
[12:22:27] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[12:22:27] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:22:27] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:22:27] 凭证文件存在
[12:22:27] 创建 config.yml...
[12:22:27] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:22:27] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:22:29] DNS 路由结果: 2026-08-05T04:22:29Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:22:29] === STEP 5: 更新 DNS (API) ===
[12:22:29] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:22:30] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[12:22:32] 设置 SSL 模式为 Full...
SSL: 跳过
[12:22:33] === STEP 6: 启动 Tunnel ===
[12:22:36] 启动 Named Tunnel (cert 模式)...
[12:22:36] 使用 config: /root/.cloudflared/config.yml
[12:22:36] cloudflared PID: 1584203
[12:22:38] Tunnel 连接已建立!
[12:22:38] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T04:22:36Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-05T04:22:36Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-05T04:22:36Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T04:22:36Z INF Generated Connector ID: c627fc05-1024-4f4a-9082-d0b3165a7771
2026-08-05T04:22:36Z INF Initial protocol quic
2026-08-05T04:22:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:22:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:22:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:22:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:22:36Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-05T04:22:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-05T04:22:36Z INF Registered tunnel connection connIndex=0 connection=3b921603-075b-4db7-b98b-2f0de87c89e9 event=0 ip=198.41.192.107 location=lax05 protocol=quic
2026-08-05T04:22:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-05T04:22:37Z INF Registered tunnel connection connIndex=1 connection=18ee7789-3a46-4e30-b668-12637830ccf9 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-05T04:22:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
[12:22:38] === STEP 7: 持久化 ===
[12:22:38] systemd 服务已配置
[12:22:38] Cron 保活已设置
[12:22:38] === STEP 8: 验证 ===
[12:22:38] --- API (localhost:8450) ---
 OK
[12:22:38] --- cloudflared 进程 ---
root     1584203  4.5  1.9 1360028 39144 ?       Sl   12:22   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1584385  0.0  1.3 1292740 27268 ?       Rl   12:22   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:22:38] --- aishield.tools ---
 OK
[12:22:40] --- DNS CNAME ---
[12:22:40] --- DNS A ---
104.21.81.46
172.67.188.44
[12:22:40] === 部署汇总 ===
[12:22:40] Tunnel Mode: cert
[12:22:40] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:22:40] API: http://localhost:8450
[12:22:40] 域名: https://aishield.tools
[12:22:40] cloudflared: /usr/local/bin/cloudflared
[12:22:40] PID: 1584203
[12:22:40] Config: /root/.cloudflared/config.yml
[12:22:40] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:22:40] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 12:22:38 CST; 9s ago
   Main PID: 1584377 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.5M
        CPU: 129ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1584377 /bin/bash /opt/start-tunnel.sh
             └─1584385 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug  5 04:22:49 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785903769.6656473, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
