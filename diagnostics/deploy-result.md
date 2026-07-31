=== DIAGNOSTIC ===
Time: Fri Jul 31 08:13:08 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785456788.2030265, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      450907  1.0  1.9 1294676 39420 ?       Sl   08:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      451035  1.3  1.9 1360284 39556 ?       Sl   08:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-07-31T00:12:58Z INF Registered tunnel connection connIndex=0 connection=0ceb0bdf-d0db-4c5c-b57d-11ea847cfa1e event=0 ip=198.41.192.27 location=lax11 protocol=quic
2026-07-31T00:12:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-07-31T00:12:58Z INF Registered tunnel connection connIndex=1 connection=fd369fbe-817c-4ee5-aa9a-3c4717005662 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-07-31T00:12:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-07-31T00:12:59Z INF Registered tunnel connection connIndex=2 connection=690cf1f3-b784-47c9-8135-a1119aae1b49 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-07-31T00:13:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.77
2026-07-31T00:13:00Z INF Registered tunnel connection connIndex=3 connection=43ea2137-a503-4c40-8cf2-80288397e0ea event=0 ip=198.41.192.77 location=lax09 protocol=quic
2026-07-31T00:13:07Z INF +-----------------------------------------------------------------------------------------------+
2026-07-31T00:13:07Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-07-31T00:13:07Z INF +-----------------------------------------------------------------------------------------------+
2026-07-31T00:13:07Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-07-31T00:13:07Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-07-31T00:13:07Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-07-31T00:13:07Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-07-31T00:13:07Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-07-31T00:13:07Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-07-31T00:13:07Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-07-31T00:13:07Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-07-31T00:13:07Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-07-31T00:13:07Z INF |                                                                                               |
2026-07-31T00:13:07Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-07-31T00:13:07Z INF +-----------------------------------------------------------------------------------------------+
2026-07-31T00:13:07Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=af1d509e-03a5-490e-8064-cd1a0040d0d4 status=pass target=region1.v2.argotunnel.com
2026-07-31T00:13:07Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=af1d509e-03a5-490e-8064-cd1a0040d0d4 status=pass target=region2.v2.argotunnel.com
2026-07-31T00:13:07Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=af1d509e-03a5-490e-8064-cd1a0040d0d4 status=pass target=region1.v2.argotunnel.com
2026-07-31T00:13:07Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=af1d509e-03a5-490e-8064-cd1a0040d0d4 status=fail target=region2.v2.argotunnel.com
2026-07-31T00:13:07Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=af1d509e-03a5-490e-8064-cd1a0040d0d4 status=pass target=region1.v2.argotunnel.com
2026-07-31T00:13:07Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=af1d509e-03a5-490e-8064-cd1a0040d0d4 status=pass target=region2.v2.argotunnel.com
2026-07-31T00:13:07Z INF precheck component="Cloudflare API" details="API is reachable" run_id=af1d509e-03a5-490e-8064-cd1a0040d0d4 status=pass target=api.cloudflare.com:443
2026-07-31T00:13:07Z INF precheck complete hard_fail=false run_id=af1d509e-03a5-490e-8064-cd1a0040d0d4 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:12:16] Time: Fri Jul 31 08:12:16 AM CST 2026
[08:12:16] User: root (UID: 0)
[08:12:16] === STEP 1: 启动 API (端口 8450) ===
[08:12:49] API 已在运行
[08:12:49] API 状态: OK
[08:12:49] === STEP 2: 安装 cloudflared ===
[08:12:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:12:49] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:12:49] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:12:49] === STEP 3: 检查认证方式 ===
[08:12:49] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:12:49] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:12:49] 检查现有 tunnel...
[08:12:50] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax08, 2xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[08:12:50] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:12:50] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:12:50] 凭证文件存在
[08:12:50] 创建 config.yml...
[08:12:50] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:12:50] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:12:52] DNS 路由结果: 2026-07-31T00:12:52Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:12:52] === STEP 5: 更新 DNS (API) ===
[08:12:52] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:12:52] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:12:53] 设置 SSL 模式为 Full...
SSL: 跳过
[08:12:54] === STEP 6: 启动 Tunnel ===
[08:12:57] 启动 Named Tunnel (cert 模式)...
[08:12:57] 使用 config: /root/.cloudflared/config.yml
[08:12:57] cloudflared PID: 450907
[08:12:59] Tunnel 连接已建立!
[08:12:59] --- cloudflared 日志 (最后 15 行) ---
2026-07-31T00:12:57Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-07-31T00:12:57Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-07-31T00:12:57Z INF cloudflared will not automatically update if installed by a package manager.
2026-07-31T00:12:57Z INF Generated Connector ID: ad9057f8-1a2a-4c8f-b971-bccb19beb2b5
2026-07-31T00:12:57Z INF Initial protocol quic
2026-07-31T00:12:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-31T00:12:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-31T00:12:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-31T00:12:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-31T00:12:57Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-07-31T00:12:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-07-31T00:12:58Z INF Registered tunnel connection connIndex=0 connection=0ceb0bdf-d0db-4c5c-b57d-11ea847cfa1e event=0 ip=198.41.192.27 location=lax11 protocol=quic
2026-07-31T00:12:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-07-31T00:12:58Z INF Registered tunnel connection connIndex=1 connection=fd369fbe-817c-4ee5-aa9a-3c4717005662 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-07-31T00:12:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
[08:12:59] === STEP 7: 持久化 ===
[08:12:59] systemd 服务已配置
[08:12:59] Cron 保活已设置
[08:12:59] === STEP 8: 验证 ===
[08:12:59] --- API (localhost:8450) ---
 OK
[08:12:59] --- cloudflared 进程 ---
root      450907  4.5  1.9 1294420 38640 ?       Sl   08:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      451035  0.0  1.3 1292740 27616 ?       Sl   08:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:12:59] --- aishield.tools ---
 OK
[08:13:01] --- DNS CNAME ---
[08:13:01] --- DNS A ---
104.21.81.46
172.67.188.44
[08:13:01] === 部署汇总 ===
[08:13:01] Tunnel Mode: cert
[08:13:01] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:13:01] API: http://localhost:8450
[08:13:01] 域名: https://aishield.tools
[08:13:01] cloudflared: /usr/local/bin/cloudflared
[08:13:01] PID: 450907
[08:13:01] Config: /root/.cloudflared/config.yml
[08:13:01] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:13:01] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-07-31 08:12:59 CST; 8s ago
   Main PID: 451029 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.9M
        CPU: 125ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─451029 /bin/bash /opt/start-tunnel.sh
             └─451035 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Jul 31 00:13:08 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785456788.9679754, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
