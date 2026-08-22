=== DIAGNOSTIC ===
Time: Sat Aug 22 10:21:26 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787365286.2277257, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1136242  1.1  1.9 1360284 38996 ?       Sl   10:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1136374  1.2  1.9 1294420 39776 ?       Sl   10:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-22T02:21:15Z INF Registered tunnel connection connIndex=0 connection=bcf36abc-61c2-4834-888e-879aa020f94e event=0 ip=198.41.192.107 location=sjc06 protocol=quic
2026-08-22T02:21:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-22T02:21:16Z INF Registered tunnel connection connIndex=1 connection=452cc22e-3bea-459a-9e77-b67de42b6409 event=0 ip=198.41.200.33 location=sjc10 protocol=quic
2026-08-22T02:21:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-08-22T02:21:17Z INF Registered tunnel connection connIndex=2 connection=c35055c4-a21e-4068-87ed-9280a02ac93b event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-22T02:21:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-22T02:21:18Z INF Registered tunnel connection connIndex=3 connection=9dbeb2cc-5720-44cf-af2d-d133f6a54726 event=0 ip=198.41.192.47 location=sjc01 protocol=quic
2026-08-22T02:21:25Z INF +-----------------------------------------------------------------------------------------------+
2026-08-22T02:21:25Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-22T02:21:25Z INF +-----------------------------------------------------------------------------------------------+
2026-08-22T02:21:25Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-22T02:21:25Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-22T02:21:25Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-22T02:21:25Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-22T02:21:25Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-22T02:21:25Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-22T02:21:25Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-22T02:21:25Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-22T02:21:25Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-22T02:21:25Z INF |                                                                                               |
2026-08-22T02:21:25Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-22T02:21:25Z INF +-----------------------------------------------------------------------------------------------+
2026-08-22T02:21:25Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ae0d0c9f-407e-435b-a614-d7cf28986938 status=pass target=region1.v2.argotunnel.com
2026-08-22T02:21:25Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ae0d0c9f-407e-435b-a614-d7cf28986938 status=pass target=region2.v2.argotunnel.com
2026-08-22T02:21:25Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ae0d0c9f-407e-435b-a614-d7cf28986938 status=pass target=region1.v2.argotunnel.com
2026-08-22T02:21:25Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=ae0d0c9f-407e-435b-a614-d7cf28986938 status=fail target=region2.v2.argotunnel.com
2026-08-22T02:21:25Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ae0d0c9f-407e-435b-a614-d7cf28986938 status=pass target=region1.v2.argotunnel.com
2026-08-22T02:21:25Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ae0d0c9f-407e-435b-a614-d7cf28986938 status=pass target=region2.v2.argotunnel.com
2026-08-22T02:21:25Z INF precheck component="Cloudflare API" details="API is reachable" run_id=ae0d0c9f-407e-435b-a614-d7cf28986938 status=pass target=api.cloudflare.com:443
2026-08-22T02:21:25Z INF precheck complete hard_fail=false run_id=ae0d0c9f-407e-435b-a614-d7cf28986938 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[10:21:01] Time: Sat Aug 22 10:21:01 AM CST 2026
[10:21:02] User: root (UID: 0)
[10:21:02] === STEP 1: 启动 API (端口 8450) ===
[10:21:04] API 已在运行
[10:21:04] API 状态: OK
[10:21:04] === STEP 2: 安装 cloudflared ===
[10:21:04] cloudflared 安装路径: /usr/local/bin/cloudflared
[10:21:04] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:21:04] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:21:04] === STEP 3: 检查认证方式 ===
[10:21:04] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[10:21:04] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[10:21:04] 检查现有 tunnel...
[10:21:05] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xsjc01, 1xsjc06, 1xsjc08, 1xsjc10, 2xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[10:21:05] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:21:05] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[10:21:05] 凭证文件存在
[10:21:05] 创建 config.yml...
[10:21:05] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[10:21:05] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:21:08] DNS 路由结果: 2026-08-22T02:21:08Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[10:21:08] === STEP 5: 更新 DNS (API) ===
[10:21:08] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:21:09] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[10:21:10] 设置 SSL 模式为 Full...
SSL: 跳过
[10:21:11] === STEP 6: 启动 Tunnel ===
[10:21:14] 启动 Named Tunnel (cert 模式)...
[10:21:15] 使用 config: /root/.cloudflared/config.yml
[10:21:15] cloudflared PID: 1136242
[10:21:17] Tunnel 连接已建立!
[10:21:17] --- cloudflared 日志 (最后 15 行) ---
2026-08-22T02:21:15Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-22T02:21:15Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-22T02:21:15Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-22T02:21:15Z INF Generated Connector ID: 32cf62c3-0332-4c26-a93c-08c947465381
2026-08-22T02:21:15Z INF Initial protocol quic
2026-08-22T02:21:15Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-22T02:21:15Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-22T02:21:15Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-22T02:21:15Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-22T02:21:15Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-22T02:21:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-22T02:21:15Z INF Registered tunnel connection connIndex=0 connection=bcf36abc-61c2-4834-888e-879aa020f94e event=0 ip=198.41.192.107 location=sjc06 protocol=quic
2026-08-22T02:21:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-22T02:21:16Z INF Registered tunnel connection connIndex=1 connection=452cc22e-3bea-459a-9e77-b67de42b6409 event=0 ip=198.41.200.33 location=sjc10 protocol=quic
2026-08-22T02:21:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
[10:21:17] === STEP 7: 持久化 ===
[10:21:17] systemd 服务已配置
[10:21:17] Cron 保活已设置
[10:21:17] === STEP 8: 验证 ===
[10:21:17] --- API (localhost:8450) ---
 OK
[10:21:17] --- cloudflared 进程 ---
root     1136242  5.5  1.9 1360028 38996 ?       Sl   10:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1136374  0.0  1.0 1292484 21372 ?       Rl   10:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[10:21:17] --- aishield.tools ---
 OK
[10:21:19] --- DNS CNAME ---
[10:21:20] --- DNS A ---
172.67.188.44
104.21.81.46
[10:21:20] === 部署汇总 ===
[10:21:20] Tunnel Mode: cert
[10:21:20] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:21:20] API: http://localhost:8450
[10:21:20] 域名: https://aishield.tools
[10:21:20] cloudflared: /usr/local/bin/cloudflared
[10:21:20] PID: 1136242
[10:21:20] Config: /root/.cloudflared/config.yml
[10:21:20] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:21:20] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-22 10:21:17 CST; 8s ago
   Main PID: 1136366 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.0M
        CPU: 129ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1136366 /bin/bash /opt/start-tunnel.sh
             └─1136374 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sat Aug 22 02:21:26 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787365287.154759, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
