=== DIAGNOSTIC ===
Time: Mon Aug 24 08:34:10 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787531650.1436245, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2936676  0.4  1.9 1294420 38908 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2936984  0.9  1.9 1294676 39856 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-24T00:33:51Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-24T00:33:51Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-24T00:33:51Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-24T00:33:51Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-24T00:33:51Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-24T00:33:51Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-24T00:33:51Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-24T00:33:51Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-24T00:33:51Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-24T00:33:51Z INF |                                                                                               |
2026-08-24T00:33:51Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-24T00:33:51Z INF +-----------------------------------------------------------------------------------------------+
2026-08-24T00:33:51Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=region1.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=region2.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=region1.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=fail target=region2.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=region1.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=region2.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="Cloudflare API" details="API is reachable" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=api.cloudflare.com:443
2026-08-24T00:33:51Z INF precheck complete hard_fail=false run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe suggested_protocol=http2
2026-08-24T00:33:53Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-24T00:33:53Z INF Retrying connection in up to 4s connIndex=0 event=0 ip=198.41.200.193
2026-08-24T00:33:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-24T00:33:54Z INF Registered tunnel connection connIndex=0 connection=45604b9c-d1f0-4f93-82a7-15b6bac86d47 event=0 ip=198.41.192.67 location=lax11 protocol=quic
2026-08-24T00:33:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-24T00:33:54Z INF Registered tunnel connection connIndex=1 connection=69e30cf7-6e85-483a-a7c8-9e3f5c4912ee event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-24T00:33:55Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
2026-08-24T00:33:55Z INF Registered tunnel connection connIndex=2 connection=0a20b9e4-66e8-48f4-9c1a-3adfe01c420e event=0 ip=198.41.192.57 location=lax11 protocol=quic
2026-08-24T00:33:56Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.23
2026-08-24T00:33:56Z INF Registered tunnel connection connIndex=3 connection=a18ac27e-f393-4666-b901-2459f6b2ab0a event=0 ip=198.41.200.23 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:32:03] Time: Mon Aug 24 08:32:03 AM CST 2026
[08:32:03] User: root (UID: 0)
[08:32:03] === STEP 1: 启动 API (端口 8450) ===
[08:33:34] API 已在运行
[08:33:34] API 状态: OK
[08:33:34] === STEP 2: 安装 cloudflared ===
[08:33:34] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:33:34] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:33:34] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:33:34] === STEP 3: 检查认证方式 ===
[08:33:34] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:33:34] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:33:34] 检查现有 tunnel...
[08:33:35] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xsjc01, 3xsjc06, 1xsjc07, 3xsjc08, 2xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[08:33:35] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:33:35] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:33:35] 凭证文件存在
[08:33:35] 创建 config.yml...
[08:33:35] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:33:35] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:33:36] DNS 路由结果: 2026-08-24T00:33:36Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:33:36] === STEP 5: 更新 DNS (API) ===
[08:33:36] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:33:37] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:33:38] 设置 SSL 模式为 Full...
SSL: 跳过
[08:33:38] === STEP 6: 启动 Tunnel ===
[08:33:41] 启动 Named Tunnel (cert 模式)...
[08:33:41] 使用 config: /root/.cloudflared/config.yml
[08:33:41] cloudflared PID: 2936676
[08:33:51] 等待 tunnel 连接... (10s)
[08:33:55] Tunnel 连接已建立!
[08:33:55] --- cloudflared 日志 (最后 15 行) ---
2026-08-24T00:33:51Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=region2.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=region1.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=fail target=region2.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=region1.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=region2.v2.argotunnel.com
2026-08-24T00:33:51Z INF precheck component="Cloudflare API" details="API is reachable" run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe status=pass target=api.cloudflare.com:443
2026-08-24T00:33:51Z INF precheck complete hard_fail=false run_id=4b729bbe-5a54-48d4-a400-a87afc19cebe suggested_protocol=http2
2026-08-24T00:33:53Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-24T00:33:53Z INF Retrying connection in up to 4s connIndex=0 event=0 ip=198.41.200.193
2026-08-24T00:33:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-24T00:33:54Z INF Registered tunnel connection connIndex=0 connection=45604b9c-d1f0-4f93-82a7-15b6bac86d47 event=0 ip=198.41.192.67 location=lax11 protocol=quic
2026-08-24T00:33:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-24T00:33:54Z INF Registered tunnel connection connIndex=1 connection=69e30cf7-6e85-483a-a7c8-9e3f5c4912ee event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-24T00:33:55Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
2026-08-24T00:33:55Z INF Registered tunnel connection connIndex=2 connection=0a20b9e4-66e8-48f4-9c1a-3adfe01c420e event=0 ip=198.41.192.57 location=lax11 protocol=quic
[08:33:55] === STEP 7: 持久化 ===
[08:33:56] systemd 服务已配置
[08:33:56] Cron 保活已设置
[08:33:56] === STEP 8: 验证 ===
[08:33:56] --- API (localhost:8450) ---
 OK
[08:33:56] --- cloudflared 进程 ---
root     2936676  0.7  1.9 1294420 38908 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2936984  0.0  1.3 1292740 27180 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:33:56] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[08:34:02] --- DNS CNAME ---
[08:34:02] --- DNS A ---
104.21.81.46
172.67.188.44
[08:34:03] === 部署汇总 ===
[08:34:03] Tunnel Mode: cert
[08:34:03] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:34:03] API: http://localhost:8450
[08:34:03] 域名: https://aishield.tools
[08:34:03] cloudflared: /usr/local/bin/cloudflared
[08:34:03] PID: 2936676
[08:34:03] Config: /root/.cloudflared/config.yml
[08:34:03] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:34:03] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-24 08:33:56 CST; 13s ago
   Main PID: 2936976 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.0M
        CPU: 138ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2936976 /bin/bash /opt/start-tunnel.sh
             └─2936984 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 24 00:34:10 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787531650.7229586, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
