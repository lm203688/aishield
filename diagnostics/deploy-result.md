=== DIAGNOSTIC ===
Time: Sun Aug 9 01:38:01 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786253881.7988136, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      935278  0.1  1.6 1294676 33544 ?       Sl   Aug08   1:24 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      935385  0.1  1.6 1294676 33712 ?       Sl   Aug08   1:24 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-08T14:20:54Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-08T14:20:54Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-08T14:20:54Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-08T14:20:54Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-08T14:20:54Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-08T14:20:54Z INF |                                                                                     |
2026-08-08T14:20:54Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-08T14:20:54Z INF +-------------------------------------------------------------------------------------+
2026-08-08T14:20:54Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=3e9faaec-0c17-46a8-abfc-f57ac5f79acb status=pass target=region1.v2.argotunnel.com
2026-08-08T14:20:54Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=3e9faaec-0c17-46a8-abfc-f57ac5f79acb status=pass target=region2.v2.argotunnel.com
2026-08-08T14:20:54Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=3e9faaec-0c17-46a8-abfc-f57ac5f79acb status=pass target=region1.v2.argotunnel.com
2026-08-08T14:20:54Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=3e9faaec-0c17-46a8-abfc-f57ac5f79acb status=pass target=region2.v2.argotunnel.com
2026-08-08T14:20:54Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=3e9faaec-0c17-46a8-abfc-f57ac5f79acb status=pass target=region1.v2.argotunnel.com
2026-08-08T14:20:54Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=3e9faaec-0c17-46a8-abfc-f57ac5f79acb status=pass target=region2.v2.argotunnel.com
2026-08-08T14:20:54Z INF precheck component="Cloudflare API" details="API is reachable" run_id=3e9faaec-0c17-46a8-abfc-f57ac5f79acb status=pass target=api.cloudflare.com:443
2026-08-08T14:20:54Z INF precheck complete hard_fail=false run_id=3e9faaec-0c17-46a8-abfc-f57ac5f79acb suggested_protocol=quic
2026-08-08T14:20:54Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-08T14:20:54Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-08-08T14:20:55Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-08T14:20:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-08T14:20:59Z INF Registered tunnel connection connIndex=3 connection=1176f3c4-7e72-4a17-8ea5-fd2e9703c153 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-08T15:15:54Z ERR  error="stream 157 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-08T15:15:54Z ERR Request failed error="stream 157 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.192.107 type=http
2026-08-08T17:23:43Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.192.67
2026-08-08T17:23:43Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=0 event=0 ip=198.41.192.67
2026-08-08T17:23:43Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.67
2026-08-08T17:23:43Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.67
2026-08-08T17:23:43Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.67
2026-08-08T17:23:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-08T17:23:44Z INF Registered tunnel connection connIndex=0 connection=4e47bcca-304b-449f-ae1a-d7a038755db9 event=0 ip=198.41.192.67 location=lax09 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[22:20:36] Time: Sat Aug  8 10:20:36 PM CST 2026
[22:20:36] User: root (UID: 0)
[22:20:36] === STEP 1: 启动 API (端口 8450) ===
[22:20:38] API 已在运行
[22:20:38] API 状态: OK
[22:20:38] === STEP 2: 安装 cloudflared ===
[22:20:38] cloudflared 安装路径: /usr/local/bin/cloudflared
[22:20:38] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:20:38] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:20:38] === STEP 3: 检查认证方式 ===
[22:20:38] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[22:20:38] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[22:20:38] 检查现有 tunnel...
[22:20:39] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[22:20:39] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[22:20:39] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[22:20:39] 凭证文件存在
[22:20:39] 创建 config.yml...
[22:20:39] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[22:20:39] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:20:40] DNS 路由结果: 2026-08-08T14:20:40Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[22:20:40] === STEP 5: 更新 DNS (API) ===
[22:20:40] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:20:41] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[22:20:42] 设置 SSL 模式为 Full...
SSL: 跳过
[22:20:44] === STEP 6: 启动 Tunnel ===
[22:20:47] 启动 Named Tunnel (cert 模式)...
[22:20:47] 使用 config: /root/.cloudflared/config.yml
[22:20:47] cloudflared PID: 935278
[22:20:49] Tunnel 连接已建立!
[22:20:49] --- cloudflared 日志 (最后 15 行) ---
2026-08-08T14:20:47Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-08T14:20:47Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-08T14:20:47Z INF Generated Connector ID: 9067f26d-23ce-49de-aa9a-07207b3a2601
2026-08-08T14:20:47Z INF Initial protocol quic
2026-08-08T14:20:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-08T14:20:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-08T14:20:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-08T14:20:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-08T14:20:47Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-08T14:20:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-08T14:20:47Z INF Registered tunnel connection connIndex=0 connection=d069752b-2b09-446a-8424-70f22eef45c5 event=0 ip=198.41.192.67 location=lax09 protocol=quic
2026-08-08T14:20:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-08-08T14:20:48Z INF Registered tunnel connection connIndex=1 connection=b4ea5fc4-43f7-4ee0-867f-15172582b4cc event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-08T14:20:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
2026-08-08T14:20:49Z INF Registered tunnel connection connIndex=2 connection=4b4a3dd2-28eb-4eee-ae18-1a295967a63b event=0 ip=198.41.192.107 location=lax10 protocol=quic
[22:20:49] === STEP 7: 持久化 ===
[22:20:50] systemd 服务已配置
[22:20:50] Cron 保活已设置
[22:20:50] === STEP 8: 验证 ===
[22:20:50] --- API (localhost:8450) ---
 OK
[22:20:50] --- cloudflared 进程 ---
root      935278  3.3  1.9 1294676 39344 ?       Sl   22:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      935385  0.0  1.3 1292484 27356 ?       Rl   22:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[22:20:50] --- aishield.tools ---
 OK
[22:20:54] --- DNS CNAME ---
[22:20:54] --- DNS A ---
104.21.81.46
172.67.188.44
[22:20:54] === 部署汇总 ===
[22:20:54] Tunnel Mode: cert
[22:20:54] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[22:20:54] API: http://localhost:8450
[22:20:54] 域名: https://aishield.tools
[22:20:54] cloudflared: /usr/local/bin/cloudflared
[22:20:54] PID: 935278
[22:20:54] Config: /root/.cloudflared/config.yml
[22:20:54] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:20:54] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-08 22:20:50 CST; 15h ago
   Main PID: 935379 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.2M
        CPU: 1min 24.036s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─935379 /bin/bash /opt/start-tunnel.sh
             └─935385 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sun Aug  9 05:38:02 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786253882.2816448, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
