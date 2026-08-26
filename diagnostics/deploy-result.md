=== DIAGNOSTIC ===
Time: Thu Aug 27 02:04:30 AM CST 2026
=== USER ===
root
=== GIT LOG ===
dbcf3459 fix: download script from GitHub raw if git reset fails, add script version diagnostics
14ced6b0 chore: update deploy diagnostics [skip ci]
7b4068ba fix: force git reset on server to get latest deploy script
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787767470.0580957, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1318135  1.0  1.8 1294676 37068 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1318260  1.5  1.9 1360028 38428 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-26T18:04:19Z INF Registered tunnel connection connIndex=1 connection=bbb1a370-7303-435d-9c3e-9a02a1380712 event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-26T18:04:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-08-26T18:04:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-08-26T18:04:21Z INF Registered tunnel connection connIndex=3 connection=2a9ccf52-3922-40b4-bd27-502cee8decb8 event=0 ip=198.41.192.57 location=lax12 protocol=quic
2026-08-26T18:04:25Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.73
2026-08-26T18:04:25Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.73
2026-08-26T18:04:25Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-26T18:04:28Z INF +-----------------------------------------------------------------------------------------------+
2026-08-26T18:04:28Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-26T18:04:28Z INF +-----------------------------------------------------------------------------------------------+
2026-08-26T18:04:28Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-26T18:04:28Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-26T18:04:28Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-26T18:04:28Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-26T18:04:28Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-26T18:04:28Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-26T18:04:28Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-26T18:04:28Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-26T18:04:28Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-26T18:04:28Z INF |                                                                                               |
2026-08-26T18:04:28Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-26T18:04:28Z INF +-----------------------------------------------------------------------------------------------+
2026-08-26T18:04:28Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7cc1c5e2-2fb4-4d81-b823-3e7eed8cb87f status=pass target=region1.v2.argotunnel.com
2026-08-26T18:04:28Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7cc1c5e2-2fb4-4d81-b823-3e7eed8cb87f status=pass target=region2.v2.argotunnel.com
2026-08-26T18:04:28Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=7cc1c5e2-2fb4-4d81-b823-3e7eed8cb87f status=pass target=region1.v2.argotunnel.com
2026-08-26T18:04:28Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=7cc1c5e2-2fb4-4d81-b823-3e7eed8cb87f status=fail target=region2.v2.argotunnel.com
2026-08-26T18:04:28Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7cc1c5e2-2fb4-4d81-b823-3e7eed8cb87f status=pass target=region1.v2.argotunnel.com
2026-08-26T18:04:28Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7cc1c5e2-2fb4-4d81-b823-3e7eed8cb87f status=pass target=region2.v2.argotunnel.com
2026-08-26T18:04:28Z INF precheck component="Cloudflare API" details="API is reachable" run_id=7cc1c5e2-2fb4-4d81-b823-3e7eed8cb87f status=pass target=api.cloudflare.com:443
2026-08-26T18:04:28Z INF precheck complete hard_fail=false run_id=7cc1c5e2-2fb4-4d81-b823-3e7eed8cb87f suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:04:07] Time: Thu Aug 27 02:04:07 AM CST 2026
[02:04:07] User: root (UID: 0)
[02:04:07] === STEP 1: 启动 API (端口 8450) ===
[02:04:10] API 已在运行
[02:04:10] API 状态: OK
[02:04:10] === STEP 2: 安装 cloudflared ===
[02:04:10] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:10] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:10] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:10] === STEP 3: 检查认证方式 ===
[02:04:10] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:10] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:10] 检查现有 tunnel...
[02:04:11] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax10, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
2026-08-26T18:04:11Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:04:11] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:11] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:11] 凭证文件存在
[02:04:11] 创建 config.yml...
[02:04:11] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:11] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:12] DNS 路由结果: 2026-08-26T18:04:12Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:12] === STEP 5: 更新 DNS (API) ===
[02:04:12] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:13] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:04:14] 设置 SSL 模式为 Full...
SSL: 跳过
[02:04:15] === STEP 6: 启动 Tunnel ===
[02:04:18] 启动 Named Tunnel (cert 模式)...
[02:04:18] 使用 config: /root/.cloudflared/config.yml
[02:04:18] cloudflared PID: 1318135
[02:04:20] Tunnel 连接已建立!
[02:04:20] --- cloudflared 日志 (最后 15 行) ---
2026-08-26T18:04:18Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-26T18:04:18Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-26T18:04:18Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-26T18:04:18Z INF Generated Connector ID: cbb6791e-dc96-46a4-9d17-caa3a31dee62
2026-08-26T18:04:18Z INF Initial protocol quic
2026-08-26T18:04:18Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-26T18:04:18Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-26T18:04:18Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-26T18:04:18Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-26T18:04:18Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-26T18:04:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-26T18:04:19Z INF Registered tunnel connection connIndex=0 connection=e06c574a-e229-4025-b576-c6ff99818778 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-26T18:04:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-26T18:04:19Z INF Registered tunnel connection connIndex=1 connection=bbb1a370-7303-435d-9c3e-9a02a1380712 event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-26T18:04:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[02:04:20] === STEP 7: 持久化 ===
[02:04:21] systemd 服务已配置
[02:04:21] Cron 保活已设置
[02:04:21] === STEP 8: 验证 ===
[02:04:21] --- API (localhost:8450) ---
 OK
[02:04:21] --- cloudflared 进程 ---
root     1318135  3.0  1.8 1294100 37916 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1318260  0.0  1.3 1292484 27252 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:04:21] --- aishield.tools ---
 OK
[02:04:23] --- DNS CNAME ---
[02:04:23] --- DNS A ---
104.21.81.46
172.67.188.44
[02:04:23] === 部署汇总 ===
[02:04:23] Tunnel Mode: cert
[02:04:23] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:23] API: http://localhost:8450
[02:04:23] 域名: https://aishield.tools
[02:04:23] cloudflared: /usr/local/bin/cloudflared
[02:04:23] PID: 1318135
[02:04:23] Config: /root/.cloudflared/config.yml
[02:04:23] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:23] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-27 02:04:20 CST; 9s ago
   Main PID: 1318258 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 19.1M
        CPU: 150ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1318258 /bin/bash /opt/start-tunnel.sh
             └─1318260 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2525069,fd=3))                                                    
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
Time: Wed Aug 26 18:04:30 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787767471.3237238, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
