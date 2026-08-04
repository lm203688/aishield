=== DIAGNOSTIC ===
Time: Wed Aug 5 07:01:07 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785884467.478009, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1333488  1.1  1.6 1360284 32532 ?       Sl   07:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1333598  1.8  1.7 1294676 34196 ?       Sl   07:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-04T23:00:56Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-04T23:00:57Z INF Registered tunnel connection connIndex=0 connection=5c2a1bc5-7be2-438b-8b36-61a383e02b1c event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-04T23:00:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-04T23:00:57Z INF Registered tunnel connection connIndex=1 connection=bafbcb8f-4992-4cd9-a323-1e426512ebeb event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-04T23:00:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-04T23:00:58Z INF Registered tunnel connection connIndex=2 connection=86caaf2b-6a53-42fb-9a55-7d4e90f4363e event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-08-04T23:00:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.53
2026-08-04T23:00:59Z INF Registered tunnel connection connIndex=3 connection=3f0f2de3-c153-4357-8dd1-e5bdf9060eaa event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-04T23:01:03Z INF +-------------------------------------------------------------------------------------+
2026-08-04T23:01:03Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-04T23:01:03Z INF +-------------------------------------------------------------------------------------+
2026-08-04T23:01:03Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-04T23:01:03Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-04T23:01:03Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-04T23:01:03Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-04T23:01:03Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-04T23:01:03Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-04T23:01:03Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-04T23:01:03Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-04T23:01:03Z INF |                                                                                     |
2026-08-04T23:01:03Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-04T23:01:03Z INF +-------------------------------------------------------------------------------------+
2026-08-04T23:01:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=484579ab-616c-43c7-821d-d48534c99d84 status=pass target=region1.v2.argotunnel.com
2026-08-04T23:01:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=484579ab-616c-43c7-821d-d48534c99d84 status=pass target=region2.v2.argotunnel.com
2026-08-04T23:01:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=484579ab-616c-43c7-821d-d48534c99d84 status=pass target=region1.v2.argotunnel.com
2026-08-04T23:01:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=484579ab-616c-43c7-821d-d48534c99d84 status=pass target=region2.v2.argotunnel.com
2026-08-04T23:01:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=484579ab-616c-43c7-821d-d48534c99d84 status=pass target=region1.v2.argotunnel.com
2026-08-04T23:01:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=484579ab-616c-43c7-821d-d48534c99d84 status=pass target=region2.v2.argotunnel.com
2026-08-04T23:01:03Z INF precheck component="Cloudflare API" details="API is reachable" run_id=484579ab-616c-43c7-821d-d48534c99d84 status=pass target=api.cloudflare.com:443
2026-08-04T23:01:03Z INF precheck complete hard_fail=false run_id=484579ab-616c-43c7-821d-d48534c99d84 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[06:59:18] Time: Wed Aug  5 06:59:18 AM CST 2026
[06:59:18] User: root (UID: 0)
[06:59:18] === STEP 1: 启动 API (端口 8450) ===
[07:00:49] API 已在运行
[07:00:49] API 状态: OK
[07:00:49] === STEP 2: 安装 cloudflared ===
[07:00:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:00:49] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:00:49] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:00:49] === STEP 3: 检查认证方式 ===
[07:00:49] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[07:00:49] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[07:00:49] 检查现有 tunnel...
[07:00:50] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax08, 1xlax09, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[07:00:50] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:00:50] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[07:00:50] 凭证文件存在
[07:00:50] 创建 config.yml...
[07:00:50] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[07:00:50] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:00:51] DNS 路由结果: 2026-08-04T23:00:51Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[07:00:51] === STEP 5: 更新 DNS (API) ===
[07:00:51] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:00:52] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[07:00:52] 设置 SSL 模式为 Full...
SSL: 跳过
[07:00:53] === STEP 6: 启动 Tunnel ===
[07:00:56] 启动 Named Tunnel (cert 模式)...
[07:00:56] 使用 config: /root/.cloudflared/config.yml
[07:00:56] cloudflared PID: 1333488
[07:00:58] Tunnel 连接已建立!
[07:00:58] --- cloudflared 日志 (最后 15 行) ---
2026-08-04T23:00:56Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-04T23:00:56Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-04T23:00:56Z INF Generated Connector ID: 754333ac-b209-419d-9b81-cfb3e3d29750
2026-08-04T23:00:56Z INF Initial protocol quic
2026-08-04T23:00:56Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-04T23:00:56Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-04T23:00:56Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-04T23:00:56Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-04T23:00:56Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-04T23:00:56Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-04T23:00:57Z INF Registered tunnel connection connIndex=0 connection=5c2a1bc5-7be2-438b-8b36-61a383e02b1c event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-04T23:00:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-04T23:00:57Z INF Registered tunnel connection connIndex=1 connection=bafbcb8f-4992-4cd9-a323-1e426512ebeb event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-04T23:00:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-04T23:00:58Z INF Registered tunnel connection connIndex=2 connection=86caaf2b-6a53-42fb-9a55-7d4e90f4363e event=0 ip=198.41.192.227 location=lax07 protocol=quic
[07:00:58] === STEP 7: 持久化 ===
[07:00:59] systemd 服务已配置
[07:00:59] Cron 保活已设置
[07:00:59] === STEP 8: 验证 ===
[07:00:59] --- API (localhost:8450) ---
 OK
[07:00:59] --- cloudflared 进程 ---
root     1333488  3.0  1.9 1359444 38760 ?       Sl   07:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1333598  0.0  1.3 1292484 27372 ?       Sl   07:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[07:00:59] --- aishield.tools ---
 OK
[07:01:00] --- DNS CNAME ---
[07:01:01] --- DNS A ---
172.67.188.44
104.21.81.46
[07:01:01] === 部署汇总 ===
[07:01:01] Tunnel Mode: cert
[07:01:01] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:01:01] API: http://localhost:8450
[07:01:01] 域名: https://aishield.tools
[07:01:01] cloudflared: /usr/local/bin/cloudflared
[07:01:01] PID: 1333488
[07:01:01] Config: /root/.cloudflared/config.yml
[07:01:01] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:01:01] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 07:00:59 CST; 8s ago
   Main PID: 1333594 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 24.2M
        CPU: 163ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1333594 /bin/bash /opt/start-tunnel.sh
             └─1333598 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Tue Aug  4 23:01:07 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785884468.0690997, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
