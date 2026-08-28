=== DIAGNOSTIC ===
Time: Fri Aug 28 12:34:57 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787891697.622563, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2671591  1.8  1.9 1294420 39008 ?       Sl   12:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2671758  3.0  1.8 1294676 38016 ?       Sl   12:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T04:34:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-08-28T04:34:51Z INF Registered tunnel connection connIndex=0 connection=4aa993df-00de-4fe4-84e8-877f867a2ff4 event=0 ip=198.41.200.53 location=sjc10 protocol=quic
2026-08-28T04:34:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-28T04:34:51Z INF Registered tunnel connection connIndex=1 connection=7ebc531d-a4ec-4657-8cc2-1e9b49347e08 event=0 ip=198.41.192.67 location=lax12 protocol=quic
2026-08-28T04:34:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-28T04:34:52Z INF Registered tunnel connection connIndex=2 connection=e3e161e7-d2c0-4c74-b835-4ade1d462e6d event=0 ip=198.41.192.77 location=lax09 protocol=quic
2026-08-28T04:34:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.23
2026-08-28T04:34:53Z INF Registered tunnel connection connIndex=3 connection=d82fa578-8614-4249-bd5b-1df5c340da4b event=0 ip=198.41.200.23 location=sjc05 protocol=quic
2026-08-28T04:34:57Z INF +-------------------------------------------------------------------------------------+
2026-08-28T04:34:57Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-28T04:34:57Z INF +-------------------------------------------------------------------------------------+
2026-08-28T04:34:57Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-28T04:34:57Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T04:34:57Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T04:34:57Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T04:34:57Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T04:34:57Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T04:34:57Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T04:34:57Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-28T04:34:57Z INF |                                                                                     |
2026-08-28T04:34:57Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-28T04:34:57Z INF +-------------------------------------------------------------------------------------+
2026-08-28T04:34:57Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=23e0e988-4b1e-4117-a393-c32f75ea4538 status=pass target=region1.v2.argotunnel.com
2026-08-28T04:34:57Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=23e0e988-4b1e-4117-a393-c32f75ea4538 status=pass target=region2.v2.argotunnel.com
2026-08-28T04:34:57Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=23e0e988-4b1e-4117-a393-c32f75ea4538 status=pass target=region1.v2.argotunnel.com
2026-08-28T04:34:57Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=23e0e988-4b1e-4117-a393-c32f75ea4538 status=pass target=region2.v2.argotunnel.com
2026-08-28T04:34:57Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=23e0e988-4b1e-4117-a393-c32f75ea4538 status=pass target=region1.v2.argotunnel.com
2026-08-28T04:34:57Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=23e0e988-4b1e-4117-a393-c32f75ea4538 status=pass target=region2.v2.argotunnel.com
2026-08-28T04:34:57Z INF precheck component="Cloudflare API" details="API is reachable" run_id=23e0e988-4b1e-4117-a393-c32f75ea4538 status=pass target=api.cloudflare.com:443
2026-08-28T04:34:57Z INF precheck complete hard_fail=false run_id=23e0e988-4b1e-4117-a393-c32f75ea4538 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:34:33] Time: Fri Aug 28 12:34:33 PM CST 2026
[12:34:33] User: root (UID: 0)
[12:34:33] === STEP 1: 启动 API (端口 8450) ===
[12:34:37] API 已在运行
[12:34:37] API 状态: OK
[12:34:37] === STEP 2: 安装 cloudflared ===
[12:34:37] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:34:37] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:34:37] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:34:37] === STEP 3: 检查认证方式 ===
[12:34:37] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:34:37] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:34:37] 检查现有 tunnel...
[12:34:38] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xlax08, 2xlax09, 2xsjc10, 2xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-28T04:34:38Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[12:34:38] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:34:38] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:34:38] 凭证文件存在
[12:34:38] 创建 config.yml...
[12:34:38] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:34:38] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:34:40] DNS 路由结果: 2026-08-28T04:34:40Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:34:40] === STEP 5: 更新 DNS (API) ===
[12:34:40] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:34:40] API 已在运行
[12:34:40] API 状态: OK
[12:34:40] === STEP 2: 安装 cloudflared ===
[12:34:40] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:34:40] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:34:40] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:34:40] === STEP 3: 检查认证方式 ===
[12:34:40] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:34:40] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:34:40] 检查现有 tunnel...
[12:34:40] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[12:34:41] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xlax08, 2xlax09, 2xsjc10, 2xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[12:34:41] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:34:41] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:34:41] 凭证文件存在
[12:34:41] 创建 config.yml...
[12:34:41] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:34:41] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[12:34:41] 设置 SSL 模式为 Full...
[12:34:42] DNS 路由结果: 2026-08-28T04:34:42Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:34:42] === STEP 5: 更新 DNS (API) ===
[12:34:42] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
SSL: 跳过
[12:34:43] === STEP 6: 启动 Tunnel ===
[12:34:46] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[12:34:46] 启动 Named Tunnel (cert 模式)...
[12:34:46] 使用 config: /root/.cloudflared/config.yml
[12:34:46] cloudflared PID: 2671291
DNS 更新: OK
[12:34:47] 设置 SSL 模式为 Full...
SSL: 跳过
[12:34:47] === STEP 6: 启动 Tunnel ===
[12:34:48] Tunnel 连接已建立!
[12:34:48] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T04:34:46Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T04:34:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-28T04:34:47Z INF Registered tunnel connection connIndex=0 connection=725bbf09-f307-4159-9c14-2666a993e140 event=0 ip=198.41.192.67 location=lax08 protocol=quic
2026-08-28T04:34:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-28T04:34:47Z INF Initiating graceful shutdown due to signal terminated ...
2026-08-28T04:34:47Z INF Registered tunnel connection connIndex=1 connection=c7817351-a5e9-44de-bda6-3f92baaf3d6a event=0 ip=198.41.200.233 location=sjc08 protocol=quic
2026-08-28T04:34:47Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=0 event=0 ip=198.41.192.67
2026-08-28T04:34:47Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.67
2026-08-28T04:34:47Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.67
2026-08-28T04:34:47Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.67
2026-08-28T04:34:47Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.200.233
2026-08-28T04:34:47Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.233
2026-08-28T04:34:47Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.233
2026-08-28T04:34:47Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.233
2026-08-28T04:34:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
[12:34:48] === STEP 7: 持久化 ===
[12:34:49] systemd 服务已配置
[12:34:49] Cron 保活已设置
[12:34:49] === STEP 8: 验证 ===
[12:34:49] --- API (localhost:8450) ---
 OK
[12:34:49] --- cloudflared 进程 ---
root     2671291  3.0  1.9 1294420 39132 ?       Sl   12:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2671491  0.0  1.3 1292484 27544 ?       Sl   12:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:34:49] --- aishield.tools ---
[12:34:50] 启动 Named Tunnel (cert 模式)...
[12:34:50] 使用 config: /root/.cloudflared/config.yml
[12:34:50] cloudflared PID: 2671591
 OK
[12:34:51] --- DNS CNAME ---
[12:34:51] --- DNS A ---
104.21.81.46
172.67.188.44
[12:34:51] === 部署汇总 ===
[12:34:51] Tunnel Mode: cert
[12:34:51] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:34:51] API: http://localhost:8450
[12:34:51] 域名: https://aishield.tools
[12:34:51] cloudflared: /usr/local/bin/cloudflared
[12:34:51] PID: 2671291
[12:34:51] Config: /root/.cloudflared/config.yml
[12:34:51] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:34:51] 状态: Named Tunnel (cert 模式) 已配置
[12:34:52] Tunnel 连接已建立!
[12:34:52] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T04:34:50Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T04:34:50Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T04:34:50Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-28T04:34:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-08-28T04:34:51Z INF Registered tunnel connection connIndex=0 connection=4aa993df-00de-4fe4-84e8-877f867a2ff4 event=0 ip=198.41.200.53 location=sjc10 protocol=quic
2026-08-28T04:34:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-28T04:34:51Z INF Registered tunnel connection connIndex=1 connection=7ebc531d-a4ec-4657-8cc2-1e9b49347e08 event=0 ip=198.41.192.67 location=lax12 protocol=quic
2026-08-28T04:34:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-28T04:34:52Z INF Registered tunnel connection connIndex=2 connection=e3e161e7-d2c0-4c74-b835-4ade1d462e6d event=0 ip=198.41.192.77 location=lax09 protocol=quic
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 2026-08-28T04:34:50Z INF Registered tunnel connection connIndex=3 connection=f6f096cd-f1db-4cb8-b084-00ac0be800cb event=0 ip=198.41.192.57 location=lax10 protocol=quic
2026-08-28T04:34:51Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.192.57
2026-08-28T04:34:51Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.57
2026-08-28T04:34:51Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.57
2026-08-28T04:34:51Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.192.57
2026-08-28T04:34:51Z ERR Connection terminated connIndex=3
[12:34:52] === STEP 7: 持久化 ===
[12:34:53] systemd 服务已配置
[12:34:53] Cron 保活已设置
[12:34:53] === STEP 8: 验证 ===
[12:34:53] --- API (localhost:8450) ---
 OK
[12:34:53] --- cloudflared 进程 ---
root     2671591  3.6  1.9 1294100 38612 ?       Sl   12:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2671758  0.0  1.3 1292740 27520 ?       Rl   12:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:34:53] --- aishield.tools ---
 OK
[12:34:54] --- DNS CNAME ---
[12:34:55] --- DNS A ---
104.21.81.46
172.67.188.44
[12:34:55] === 部署汇总 ===
[12:34:55] Tunnel Mode: cert
[12:34:55] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:34:55] API: http://localhost:8450
[12:34:55] 域名: https://aishield.tools
[12:34:55] cloudflared: /usr/local/bin/cloudflared
[12:34:55] PID: 2671591
[12:34:55] Config: /root/.cloudflared/config.yml
[12:34:55] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:34:55] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 12:34:53 CST; 4s ago
   Main PID: 2671754 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.1M
        CPU: 125ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2671754 /bin/bash /opt/start-tunnel.sh
             └─2671758 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 28 04:34:59 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787891699.4291372, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
