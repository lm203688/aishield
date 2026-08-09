=== DIAGNOSTIC ===
Time: Sun Aug 9 04:54:08 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786265648.9729564, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1736801  1.0  1.9 1294420 40184 ?       Sl   16:53   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1736900  1.1  1.9 1294420 39864 ?       Sl   16:53   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-09T08:53:57Z INF Registered tunnel connection connIndex=0 connection=61b37722-2bc6-4e8b-bb98-4914a012d68b event=0 ip=198.41.192.7 location=lax07 protocol=quic
2026-08-09T08:53:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-09T08:53:57Z INF Registered tunnel connection connIndex=1 connection=d0f6606b-3159-4b99-9003-5c1d4bad1db0 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-09T08:53:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-09T08:53:58Z INF Registered tunnel connection connIndex=2 connection=dab7147f-d00f-42b5-8ea4-4e93718bebd2 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-09T08:53:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-09T08:53:59Z INF Registered tunnel connection connIndex=3 connection=a1a5033f-1ee7-4b6e-b0df-9505d45d02ed event=0 ip=198.41.192.47 location=lax08 protocol=quic
2026-08-09T08:54:05Z INF +-----------------------------------------------------------------------------------------------+
2026-08-09T08:54:05Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-09T08:54:05Z INF +-----------------------------------------------------------------------------------------------+
2026-08-09T08:54:05Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-09T08:54:05Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-09T08:54:05Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-09T08:54:05Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-09T08:54:05Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-09T08:54:05Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-09T08:54:05Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-09T08:54:05Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-09T08:54:05Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-09T08:54:05Z INF |                                                                                               |
2026-08-09T08:54:05Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-09T08:54:05Z INF +-----------------------------------------------------------------------------------------------+
2026-08-09T08:54:05Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=2321fb3f-f15c-4287-a036-b1f1ac6eeb4a status=pass target=region1.v2.argotunnel.com
2026-08-09T08:54:05Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=2321fb3f-f15c-4287-a036-b1f1ac6eeb4a status=pass target=region2.v2.argotunnel.com
2026-08-09T08:54:05Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=2321fb3f-f15c-4287-a036-b1f1ac6eeb4a status=pass target=region1.v2.argotunnel.com
2026-08-09T08:54:05Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=2321fb3f-f15c-4287-a036-b1f1ac6eeb4a status=fail target=region2.v2.argotunnel.com
2026-08-09T08:54:05Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=2321fb3f-f15c-4287-a036-b1f1ac6eeb4a status=pass target=region1.v2.argotunnel.com
2026-08-09T08:54:05Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=2321fb3f-f15c-4287-a036-b1f1ac6eeb4a status=pass target=region2.v2.argotunnel.com
2026-08-09T08:54:05Z INF precheck component="Cloudflare API" details="API is reachable" run_id=2321fb3f-f15c-4287-a036-b1f1ac6eeb4a status=pass target=api.cloudflare.com:443
2026-08-09T08:54:05Z INF precheck complete hard_fail=false run_id=2321fb3f-f15c-4287-a036-b1f1ac6eeb4a suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:52:59] Time: Sun Aug  9 04:52:59 PM CST 2026
[16:52:59] User: root (UID: 0)
[16:52:59] === STEP 1: 启动 API (端口 8450) ===
[16:53:47] API 已在运行
[16:53:47] API 状态: OK
[16:53:47] === STEP 2: 安装 cloudflared ===
[16:53:47] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:53:47] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:53:47] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:53:47] === STEP 3: 检查认证方式 ===
[16:53:47] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:53:47] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:53:47] 检查现有 tunnel...
[16:53:48] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 1xlax05, 3xlax07, 2xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[16:53:48] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:53:48] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:53:48] 凭证文件存在
[16:53:48] 创建 config.yml...
[16:53:48] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:53:48] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:53:50] DNS 路由结果: 2026-08-09T08:53:50Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:53:50] === STEP 5: 更新 DNS (API) ===
[16:53:50] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:53:50] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:53:51] 设置 SSL 模式为 Full...
SSL: 跳过
[16:53:52] === STEP 6: 启动 Tunnel ===
[16:53:55] 启动 Named Tunnel (cert 模式)...
[16:53:55] 使用 config: /root/.cloudflared/config.yml
[16:53:55] cloudflared PID: 1736801
[16:53:57] Tunnel 连接已建立!
[16:53:57] --- cloudflared 日志 (最后 15 行) ---
2026-08-09T08:53:55Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-09T08:53:55Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-09T08:53:55Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-09T08:53:55Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-09T08:53:55Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-09T08:53:55Z INF Generated Connector ID: af29d95e-ecb7-4429-b5ce-5eba2e0a52b9
2026-08-09T08:53:55Z INF Initial protocol quic
2026-08-09T08:53:55Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T08:53:55Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T08:53:55Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T08:53:55Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T08:53:55Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-09T08:53:55Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.7
2026-08-09T08:53:57Z INF Registered tunnel connection connIndex=0 connection=61b37722-2bc6-4e8b-bb98-4914a012d68b event=0 ip=198.41.192.7 location=lax07 protocol=quic
2026-08-09T08:53:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
[16:53:57] === STEP 7: 持久化 ===
[16:53:57] systemd 服务已配置
[16:53:57] Cron 保活已设置
[16:53:57] === STEP 8: 验证 ===
[16:53:57] --- API (localhost:8450) ---
 OK
[16:53:57] --- cloudflared 进程 ---
root     1736801  4.5  1.9 1294092 38404 ?       Sl   16:53   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1736900  0.0  1.3 1292740 27284 ?       Sl   16:53   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:53:58] --- aishield.tools ---
 OK
[16:54:00] --- DNS CNAME ---
[16:54:00] --- DNS A ---
104.21.81.46
172.67.188.44
[16:54:00] === 部署汇总 ===
[16:54:00] Tunnel Mode: cert
[16:54:00] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:54:00] API: http://localhost:8450
[16:54:00] 域名: https://aishield.tools
[16:54:00] cloudflared: /usr/local/bin/cloudflared
[16:54:00] PID: 1736801
[16:54:00] Config: /root/.cloudflared/config.yml
[16:54:00] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:54:00] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-09 16:53:57 CST; 11s ago
   Main PID: 1736896 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.3M
        CPU: 143ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1736896 /bin/bash /opt/start-tunnel.sh
             └─1736900 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sun Aug  9 08:54:09 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786265650.1100996, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
