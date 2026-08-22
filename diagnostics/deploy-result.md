=== DIAGNOSTIC ===
Time: Sat Aug 22 08:12:18 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787400738.4318168, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1140971  0.1  1.2 1294676 24304 ?       Sl   10:27   0:54 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1141074  0.1  1.2 1294676 24508 ?       Sl   10:27   0:55 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-22T02:27:08Z INF Registered tunnel connection connIndex=0 connection=5afa733b-2dfc-4468-9035-ca89c51a02cb event=0 ip=198.41.200.233 location=sjc10 protocol=quic
2026-08-22T02:27:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-22T02:27:09Z INF Registered tunnel connection connIndex=1 connection=0e552d98-0410-4fa5-8ea2-299a4235e4e7 event=0 ip=198.41.192.67 location=sjc01 protocol=quic
2026-08-22T02:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-22T02:27:10Z INF Registered tunnel connection connIndex=2 connection=1d970ea9-d3dc-4bf0-8c2b-9fbb89d5c6f9 event=0 ip=198.41.200.113 location=sjc07 protocol=quic
2026-08-22T02:27:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-22T02:27:11Z INF Registered tunnel connection connIndex=3 connection=d2b85ae4-d3ae-4339-a01b-912260b31855 event=0 ip=198.41.192.47 location=sjc06 protocol=quic
2026-08-22T02:27:17Z INF +-----------------------------------------------------------------------------------------------+
2026-08-22T02:27:17Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-22T02:27:17Z INF +-----------------------------------------------------------------------------------------------+
2026-08-22T02:27:17Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-22T02:27:17Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-22T02:27:17Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-22T02:27:17Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-22T02:27:17Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-22T02:27:17Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-22T02:27:17Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-22T02:27:17Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-22T02:27:17Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-22T02:27:17Z INF |                                                                                               |
2026-08-22T02:27:17Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-22T02:27:17Z INF +-----------------------------------------------------------------------------------------------+
2026-08-22T02:27:17Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c3bcdb0d-87e0-4d91-8d40-53cb8a3d456f status=pass target=region1.v2.argotunnel.com
2026-08-22T02:27:17Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c3bcdb0d-87e0-4d91-8d40-53cb8a3d456f status=pass target=region2.v2.argotunnel.com
2026-08-22T02:27:17Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c3bcdb0d-87e0-4d91-8d40-53cb8a3d456f status=pass target=region1.v2.argotunnel.com
2026-08-22T02:27:17Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=c3bcdb0d-87e0-4d91-8d40-53cb8a3d456f status=fail target=region2.v2.argotunnel.com
2026-08-22T02:27:17Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c3bcdb0d-87e0-4d91-8d40-53cb8a3d456f status=pass target=region1.v2.argotunnel.com
2026-08-22T02:27:17Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c3bcdb0d-87e0-4d91-8d40-53cb8a3d456f status=pass target=region2.v2.argotunnel.com
2026-08-22T02:27:17Z INF precheck component="Cloudflare API" details="API is reachable" run_id=c3bcdb0d-87e0-4d91-8d40-53cb8a3d456f status=pass target=api.cloudflare.com:443
2026-08-22T02:27:17Z INF precheck complete hard_fail=false run_id=c3bcdb0d-87e0-4d91-8d40-53cb8a3d456f suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[10:25:30] Time: Sat Aug 22 10:25:30 AM CST 2026
[10:25:30] User: root (UID: 0)
[10:25:30] === STEP 1: 启动 API (端口 8450) ===
[10:27:00] API 已在运行
[10:27:00] API 状态: OK
[10:27:00] === STEP 2: 安装 cloudflared ===
[10:27:00] cloudflared 安装路径: /usr/local/bin/cloudflared
[10:27:00] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:27:00] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:27:00] === STEP 3: 检查认证方式 ===
[10:27:00] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[10:27:00] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[10:27:00] 检查现有 tunnel...
[10:27:01] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xsjc01, 2xsjc06, 1xsjc07, 1xsjc08, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
[10:27:01] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:27:01] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[10:27:01] 凭证文件存在
[10:27:01] 创建 config.yml...
[10:27:01] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[10:27:01] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:27:02] DNS 路由结果: 2026-08-22T02:27:02Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[10:27:02] === STEP 5: 更新 DNS (API) ===
[10:27:02] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:27:03] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[10:27:04] 设置 SSL 模式为 Full...
SSL: 跳过
[10:27:04] === STEP 6: 启动 Tunnel ===
[10:27:07] 启动 Named Tunnel (cert 模式)...
[10:27:07] 使用 config: /root/.cloudflared/config.yml
[10:27:07] cloudflared PID: 1140971
[10:27:09] Tunnel 连接已建立!
[10:27:09] --- cloudflared 日志 (最后 15 行) ---
2026-08-22T02:27:07Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-22T02:27:07Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-22T02:27:07Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-22T02:27:07Z INF Generated Connector ID: 6027d041-1ad8-42cd-9b39-0c9337e1910b
2026-08-22T02:27:07Z INF Initial protocol quic
2026-08-22T02:27:07Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-22T02:27:07Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-22T02:27:07Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-22T02:27:07Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-22T02:27:07Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-22T02:27:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-22T02:27:08Z INF Registered tunnel connection connIndex=0 connection=5afa733b-2dfc-4468-9035-ca89c51a02cb event=0 ip=198.41.200.233 location=sjc10 protocol=quic
2026-08-22T02:27:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-22T02:27:09Z INF Registered tunnel connection connIndex=1 connection=0e552d98-0410-4fa5-8ea2-299a4235e4e7 event=0 ip=198.41.192.67 location=sjc01 protocol=quic
2026-08-22T02:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
[10:27:09] === STEP 7: 持久化 ===
[10:27:10] systemd 服务已配置
[10:27:10] Cron 保活已设置
[10:27:10] === STEP 8: 验证 ===
[10:27:10] --- API (localhost:8450) ---
 OK
[10:27:10] --- cloudflared 进程 ---
root     1140971  3.0  1.9 1294420 38772 ?       Sl   10:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1141074  0.0  1.3 1292484 27332 ?       Sl   10:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[10:27:10] --- aishield.tools ---
 OK
[10:27:12] --- DNS CNAME ---
[10:27:12] --- DNS A ---
104.21.81.46
172.67.188.44
[10:27:12] === 部署汇总 ===
[10:27:12] Tunnel Mode: cert
[10:27:12] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:27:12] API: http://localhost:8450
[10:27:12] 域名: https://aishield.tools
[10:27:12] cloudflared: /usr/local/bin/cloudflared
[10:27:12] PID: 1140971
[10:27:12] Config: /root/.cloudflared/config.yml
[10:27:12] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:27:12] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-22 10:27:10 CST; 9h ago
   Main PID: 1141073 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.6M
        CPU: 55.349s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1141073 /bin/bash /opt/start-tunnel.sh
             └─1141074 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3693189,fd=3))                                                    
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
Time: Sat Aug 22 12:12:19 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787400739.4672303, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
