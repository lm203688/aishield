=== DIAGNOSTIC ===
Time: Fri Jul 31 08:36:24 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785458184.211422, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      467844  1.0  1.9 1294420 39360 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      467979  1.3  1.9 1294420 39660 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-07-31T00:36:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-07-31T00:36:14Z INF Registered tunnel connection connIndex=0 connection=17383240-dd06-4841-b327-9896ba6a35b8 event=0 ip=198.41.192.167 location=lax11 protocol=quic
2026-07-31T00:36:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-07-31T00:36:14Z INF Registered tunnel connection connIndex=1 connection=9f7e1b36-c096-4c94-836f-01812c049256 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-07-31T00:36:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-07-31T00:36:16Z INF Registered tunnel connection connIndex=2 connection=f08518c3-1ec5-4b2c-8b49-33e491088c18 event=0 ip=198.41.192.7 location=lax08 protocol=quic
2026-07-31T00:36:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-07-31T00:36:17Z INF Registered tunnel connection connIndex=3 connection=e00336eb-1420-459d-9b5b-3f9db9873778 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-07-31T00:36:20Z INF +-------------------------------------------------------------------------------------+
2026-07-31T00:36:20Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-07-31T00:36:20Z INF +-------------------------------------------------------------------------------------+
2026-07-31T00:36:20Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-07-31T00:36:20Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-07-31T00:36:20Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-07-31T00:36:20Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-07-31T00:36:20Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-07-31T00:36:20Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-07-31T00:36:20Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-07-31T00:36:20Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-07-31T00:36:20Z INF |                                                                                     |
2026-07-31T00:36:20Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-07-31T00:36:20Z INF +-------------------------------------------------------------------------------------+
2026-07-31T00:36:20Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=128aa9a2-68e3-46ac-b8d2-71f2e215767c status=pass target=region1.v2.argotunnel.com
2026-07-31T00:36:20Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=128aa9a2-68e3-46ac-b8d2-71f2e215767c status=pass target=region2.v2.argotunnel.com
2026-07-31T00:36:20Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=128aa9a2-68e3-46ac-b8d2-71f2e215767c status=pass target=region1.v2.argotunnel.com
2026-07-31T00:36:20Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=128aa9a2-68e3-46ac-b8d2-71f2e215767c status=pass target=region2.v2.argotunnel.com
2026-07-31T00:36:20Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=128aa9a2-68e3-46ac-b8d2-71f2e215767c status=pass target=region1.v2.argotunnel.com
2026-07-31T00:36:20Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=128aa9a2-68e3-46ac-b8d2-71f2e215767c status=pass target=region2.v2.argotunnel.com
2026-07-31T00:36:20Z INF precheck component="Cloudflare API" details="API is reachable" run_id=128aa9a2-68e3-46ac-b8d2-71f2e215767c status=pass target=api.cloudflare.com:443
2026-07-31T00:36:20Z INF precheck complete hard_fail=false run_id=128aa9a2-68e3-46ac-b8d2-71f2e215767c suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:35:57] Time: Fri Jul 31 08:35:57 AM CST 2026
[08:35:57] User: root (UID: 0)
[08:35:57] === STEP 1: 启动 API (端口 8450) ===
[08:36:00] API 已在运行
[08:36:00] API 状态: OK
[08:36:00] === STEP 2: 安装 cloudflared ===
[08:36:00] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:36:01] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:01] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:01] === STEP 3: 检查认证方式 ===
[08:36:01] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:36:01] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:36:01] 检查现有 tunnel...
[08:36:02] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax09, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[08:36:02] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:02] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:36:02] 凭证文件存在
[08:36:02] 创建 config.yml...
[08:36:02] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:36:02] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:06] DNS 路由结果: 2026-07-31T00:36:06Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:06] === STEP 5: 更新 DNS (API) ===
[08:36:06] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:08] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:36:09] 设置 SSL 模式为 Full...
SSL: 跳过
[08:36:10] === STEP 6: 启动 Tunnel ===
[08:36:13] 启动 Named Tunnel (cert 模式)...
[08:36:13] 使用 config: /root/.cloudflared/config.yml
[08:36:13] cloudflared PID: 467844
[08:36:15] Tunnel 连接已建立!
[08:36:15] --- cloudflared 日志 (最后 15 行) ---
2026-07-31T00:36:13Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-07-31T00:36:13Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-07-31T00:36:13Z INF cloudflared will not automatically update if installed by a package manager.
2026-07-31T00:36:13Z INF Generated Connector ID: 35968675-b9fe-44f6-bfe4-5c598005ece3
2026-07-31T00:36:13Z INF Initial protocol quic
2026-07-31T00:36:13Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-31T00:36:13Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-31T00:36:13Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-31T00:36:13Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-31T00:36:13Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-07-31T00:36:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-07-31T00:36:14Z INF Registered tunnel connection connIndex=0 connection=17383240-dd06-4841-b327-9896ba6a35b8 event=0 ip=198.41.192.167 location=lax11 protocol=quic
2026-07-31T00:36:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-07-31T00:36:14Z INF Registered tunnel connection connIndex=1 connection=9f7e1b36-c096-4c94-836f-01812c049256 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-07-31T00:36:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
[08:36:15] === STEP 7: 持久化 ===
[08:36:16] systemd 服务已配置
[08:36:16] Cron 保活已设置
[08:36:16] === STEP 8: 验证 ===
[08:36:16] --- API (localhost:8450) ---
 OK
[08:36:16] --- cloudflared 进程 ---
root      467844  3.6  1.9 1294420 39092 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      467979  0.0  1.3 1292740 27428 ?       Rl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:36:16] --- aishield.tools ---
 OK
[08:36:18] --- DNS CNAME ---
[08:36:18] --- DNS A ---
172.67.188.44
104.21.81.46
[08:36:18] === 部署汇总 ===
[08:36:18] Tunnel Mode: cert
[08:36:18] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:18] API: http://localhost:8450
[08:36:18] 域名: https://aishield.tools
[08:36:18] cloudflared: /usr/local/bin/cloudflared
[08:36:18] PID: 467844
[08:36:18] Config: /root/.cloudflared/config.yml
[08:36:18] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:18] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-07-31 08:36:16 CST; 7s ago
   Main PID: 467971 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.6M
        CPU: 125ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─467971 /bin/bash /opt/start-tunnel.sh
             └─467979 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Jul 31 00:36:24 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785458185.2547467, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
