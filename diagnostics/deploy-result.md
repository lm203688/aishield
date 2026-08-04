=== DIAGNOSTIC ===
Time: Tue Aug 4 10:42:52 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785854572.5854328, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      954779  0.1  1.7 1360028 35668 ?       Sl   22:12   0:02 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      954917  0.1  1.7 1360284 35848 ?       Sl   22:13   0:02 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-04T14:12:59Z INF Registered tunnel connection connIndex=0 connection=1d07e7a0-90b5-4e7e-abb4-930e92902d22 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-04T14:12:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-04T14:12:59Z INF Registered tunnel connection connIndex=1 connection=793cf79e-4ecb-48a5-a688-a0131afb4565 event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-04T14:13:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
2026-08-04T14:13:00Z INF Registered tunnel connection connIndex=2 connection=d0238f72-4f70-4aed-ba65-e91017071225 event=0 ip=198.41.192.57 location=lax05 protocol=quic
2026-08-04T14:13:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-04T14:13:02Z INF Registered tunnel connection connIndex=3 connection=b9ca2464-b7e5-4b74-91a2-54fcf81065c3 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-04T14:13:08Z INF +-----------------------------------------------------------------------------------------------+
2026-08-04T14:13:08Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-04T14:13:08Z INF +-----------------------------------------------------------------------------------------------+
2026-08-04T14:13:08Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-04T14:13:08Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-04T14:13:08Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-04T14:13:08Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-04T14:13:08Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-04T14:13:08Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-04T14:13:08Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-04T14:13:08Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-04T14:13:08Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-04T14:13:08Z INF |                                                                                               |
2026-08-04T14:13:08Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-04T14:13:08Z INF +-----------------------------------------------------------------------------------------------+
2026-08-04T14:13:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ceda8fd6-5928-4d96-b032-9148280f0b90 status=pass target=region1.v2.argotunnel.com
2026-08-04T14:13:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ceda8fd6-5928-4d96-b032-9148280f0b90 status=pass target=region2.v2.argotunnel.com
2026-08-04T14:13:08Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ceda8fd6-5928-4d96-b032-9148280f0b90 status=pass target=region1.v2.argotunnel.com
2026-08-04T14:13:08Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=ceda8fd6-5928-4d96-b032-9148280f0b90 status=fail target=region2.v2.argotunnel.com
2026-08-04T14:13:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ceda8fd6-5928-4d96-b032-9148280f0b90 status=pass target=region1.v2.argotunnel.com
2026-08-04T14:13:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ceda8fd6-5928-4d96-b032-9148280f0b90 status=pass target=region2.v2.argotunnel.com
2026-08-04T14:13:08Z INF precheck component="Cloudflare API" details="API is reachable" run_id=ceda8fd6-5928-4d96-b032-9148280f0b90 status=pass target=api.cloudflare.com:443
2026-08-04T14:13:08Z INF precheck complete hard_fail=false run_id=ceda8fd6-5928-4d96-b032-9148280f0b90 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[22:12:40] Time: Tue Aug  4 10:12:40 PM CST 2026
[22:12:40] User: root (UID: 0)
[22:12:40] === STEP 1: 启动 API (端口 8450) ===
[22:12:49] API 已在运行
[22:12:49] API 状态: OK
[22:12:49] === STEP 2: 安装 cloudflared ===
[22:12:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[22:12:50] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:12:50] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:12:50] === STEP 3: 检查认证方式 ===
[22:12:50] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[22:12:50] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[22:12:50] 检查现有 tunnel...
[22:12:51] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax09, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[22:12:51] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[22:12:51] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[22:12:51] 凭证文件存在
[22:12:51] 创建 config.yml...
[22:12:51] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[22:12:51] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:12:52] DNS 路由结果: 2026-08-04T14:12:52Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[22:12:52] === STEP 5: 更新 DNS (API) ===
[22:12:52] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:12:53] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[22:12:54] 设置 SSL 模式为 Full...
SSL: 跳过
[22:12:55] === STEP 6: 启动 Tunnel ===
[22:12:58] 启动 Named Tunnel (cert 模式)...
[22:12:58] 使用 config: /root/.cloudflared/config.yml
[22:12:58] cloudflared PID: 954779
[22:13:00] Tunnel 连接已建立!
[22:13:00] --- cloudflared 日志 (最后 15 行) ---
2026-08-04T14:12:58Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-04T14:12:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-04T14:12:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-04T14:12:58Z INF Generated Connector ID: 0eccb2b7-bbb6-4572-8047-074400bdb24a
2026-08-04T14:12:58Z INF Initial protocol quic
2026-08-04T14:12:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-04T14:12:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-04T14:12:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-04T14:12:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-04T14:12:58Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-04T14:12:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-08-04T14:12:59Z INF Registered tunnel connection connIndex=0 connection=1d07e7a0-90b5-4e7e-abb4-930e92902d22 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-04T14:12:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-04T14:12:59Z INF Registered tunnel connection connIndex=1 connection=793cf79e-4ecb-48a5-a688-a0131afb4565 event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-04T14:13:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
[22:13:00] === STEP 7: 持久化 ===
[22:13:01] systemd 服务已配置
[22:13:01] Cron 保活已设置
[22:13:01] === STEP 8: 验证 ===
[22:13:01] --- API (localhost:8450) ---
 OK
[22:13:01] --- cloudflared 进程 ---
root      954779  3.0  1.9 1360028 39176 ?       Sl   22:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      954917  0.0  1.3 1358348 27412 ?       Rl   22:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[22:13:01] --- aishield.tools ---
 OK
[22:13:03] --- DNS CNAME ---
[22:13:03] --- DNS A ---
104.21.81.46
172.67.188.44
[22:13:03] === 部署汇总 ===
[22:13:03] Tunnel Mode: cert
[22:13:03] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[22:13:03] API: http://localhost:8450
[22:13:03] 域名: https://aishield.tools
[22:13:03] cloudflared: /usr/local/bin/cloudflared
[22:13:03] PID: 954779
[22:13:03] Config: /root/.cloudflared/config.yml
[22:13:03] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:13:03] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-04 22:13:01 CST; 29min ago
   Main PID: 954915 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.1M
        CPU: 2.988s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─954915 /bin/bash /opt/start-tunnel.sh
             └─954917 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Tue Aug  4 14:42:52 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785854573.0570452, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
