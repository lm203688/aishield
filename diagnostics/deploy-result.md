=== DIAGNOSTIC ===
Time: Fri Aug 7 12:15:54 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786076154.5971842, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3649198  0.1  1.8 1360284 37764 ?       Sl   12:01   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3649358  0.1  1.8 1294676 37712 ?       Sl   12:01   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-07T04:01:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.77
2026-08-07T04:01:19Z INF Registered tunnel connection connIndex=1 connection=ea58a1d2-8198-4d0b-9e5f-abda338cc99a event=0 ip=198.41.192.77 location=lax11 protocol=quic
2026-08-07T04:01:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
2026-08-07T04:01:20Z INF Registered tunnel connection connIndex=2 connection=aee943da-8604-446a-85f8-c92bcf73ee2d event=0 ip=198.41.192.67 location=lax05 protocol=quic
2026-08-07T04:01:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-07T04:01:21Z INF Registered tunnel connection connIndex=3 connection=4bf92e00-dc75-40d0-a1ab-b96ed08bb00b event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-07T04:01:24Z INF +-------------------------------------------------------------------------------------+
2026-08-07T04:01:24Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-07T04:01:24Z INF +-------------------------------------------------------------------------------------+
2026-08-07T04:01:24Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-07T04:01:24Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-07T04:01:24Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-07T04:01:24Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-07T04:01:24Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-07T04:01:24Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-07T04:01:24Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-07T04:01:24Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-07T04:01:24Z INF |                                                                                     |
2026-08-07T04:01:24Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-07T04:01:24Z INF +-------------------------------------------------------------------------------------+
2026-08-07T04:01:24Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ca35c38f-e007-4a69-84d8-b8eb3cd3a884 status=pass target=region1.v2.argotunnel.com
2026-08-07T04:01:24Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ca35c38f-e007-4a69-84d8-b8eb3cd3a884 status=pass target=region2.v2.argotunnel.com
2026-08-07T04:01:24Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ca35c38f-e007-4a69-84d8-b8eb3cd3a884 status=pass target=region1.v2.argotunnel.com
2026-08-07T04:01:24Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ca35c38f-e007-4a69-84d8-b8eb3cd3a884 status=pass target=region2.v2.argotunnel.com
2026-08-07T04:01:24Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ca35c38f-e007-4a69-84d8-b8eb3cd3a884 status=pass target=region1.v2.argotunnel.com
2026-08-07T04:01:24Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ca35c38f-e007-4a69-84d8-b8eb3cd3a884 status=pass target=region2.v2.argotunnel.com
2026-08-07T04:01:24Z INF precheck component="Cloudflare API" details="API is reachable" run_id=ca35c38f-e007-4a69-84d8-b8eb3cd3a884 status=pass target=api.cloudflare.com:443
2026-08-07T04:01:24Z INF precheck complete hard_fail=false run_id=ca35c38f-e007-4a69-84d8-b8eb3cd3a884 suggested_protocol=quic
2026-08-07T04:01:26Z ERR  error="stream 9 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-07T04:01:26Z ERR Request failed error="stream 9 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.200.43 type=http
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
[12:01:11] DNS 路由结果: 2026-08-07T04:01:11Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:01:11] === STEP 5: 更新 DNS (API) ===
[12:01:12] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:01:12] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[12:01:13] 设置 SSL 模式为 Full...
SSL: 跳过
[12:01:15] === STEP 6: 启动 Tunnel ===
[12:01:18] 启动 Named Tunnel (cert 模式)...
[12:01:18] 使用 config: /root/.cloudflared/config.yml
[12:01:18] cloudflared PID: 3649198
[12:01:20] Tunnel 连接已建立!
[12:01:20] --- cloudflared 日志 (最后 15 行) ---
2026-08-07T04:01:18Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-07T04:01:18Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-07T04:01:18Z INF Generated Connector ID: ca284b79-3168-41d3-b2db-347fadc00839
2026-08-07T04:01:18Z INF Initial protocol quic
2026-08-07T04:01:18Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T04:01:18Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T04:01:18Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-07T04:01:18Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-07T04:01:18Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-07T04:01:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-07T04:01:18Z INF Registered tunnel connection connIndex=0 connection=bef49d0e-eb13-4b4a-a171-7fba933bcaf2 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-07T04:01:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.77
2026-08-07T04:01:19Z INF Registered tunnel connection connIndex=1 connection=ea58a1d2-8198-4d0b-9e5f-abda338cc99a event=0 ip=198.41.192.77 location=lax11 protocol=quic
2026-08-07T04:01:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
2026-08-07T04:01:20Z INF Registered tunnel connection connIndex=2 connection=aee943da-8604-446a-85f8-c92bcf73ee2d event=0 ip=198.41.192.67 location=lax05 protocol=quic
[12:01:20] === STEP 7: 持久化 ===
[12:01:20] systemd 服务已配置
[12:01:20] Cron 保活已设置
[12:01:20] === STEP 8: 验证 ===
[12:01:20] --- API (localhost:8450) ---
 OK
[12:01:20] --- cloudflared 进程 ---
root     3649198  4.5  1.9 1360284 39160 ?       Sl   12:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3649358  0.0  1.3 1292740 27388 ?       Sl   12:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:01:20] --- aishield.tools ---
 OK
[12:01:22] --- DNS CNAME ---
[12:01:22] --- DNS A ---
172.67.188.44
104.21.81.46
[12:01:23] === 部署汇总 ===
[12:01:23] Tunnel Mode: cert
[12:01:23] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:01:23] API: http://localhost:8450
[12:01:23] 域名: https://aishield.tools
[12:01:23] cloudflared: /usr/local/bin/cloudflared
[12:01:23] PID: 3649198
[12:01:23] Config: /root/.cloudflared/config.yml
[12:01:23] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:01:23] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-07 12:01:20 CST; 14min ago
   Main PID: 3649356 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 15.9M
        CPU: 1.550s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3649356 /bin/bash /opt/start-tunnel.sh
             └─3649358 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug  7 04:15:54 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786076155.3932233, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
