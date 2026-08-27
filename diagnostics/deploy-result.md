=== DIAGNOSTIC ===
Time: Thu Aug 27 12:40:58 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787805658.6136806, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1732195  0.8  1.9 1294676 38968 ?       Sl   12:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1732214  1.0  1.9 1360284 39424 ?       Sl   12:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1732402  1.3  1.9 1294676 39072 ?       Sl   12:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-27T04:40:46Z INF Registered tunnel connection connIndex=0 connection=0aebb273-9331-4be1-b571-848760fd0235 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-08-27T04:40:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-27T04:40:47Z INF Registered tunnel connection connIndex=1 connection=6a0ac5b7-1a16-4f63-b277-28676884b7b5 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-27T04:40:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-27T04:40:48Z INF Registered tunnel connection connIndex=2 connection=7f6df67b-209a-4cd7-aa17-dae0f4108030 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-27T04:40:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.167
2026-08-27T04:40:49Z INF Registered tunnel connection connIndex=3 connection=369ba7c7-726f-4150-9e30-64a1317a8fc1 event=0 ip=198.41.192.167 location=lax07 protocol=quic
202026-08-27T04:40:54Z INF +-----------------------------------------------------------------------------------------------+
2026-08-27T04:40:54Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-27T04:40:54Z INF +-----------------------------------------------------------------------------------------------+
2026-08-27T04:40:54Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-27T04:40:54Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-27T04:40:54Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-27T04:40:54Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-27T04:40:54Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-27T04:40:54Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-27T04:40:54Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-27T04:40:54Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-27T04:40:54Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-27T04:40:54Z INF |                                                                                               |
2026-08-27T04:40:54Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-27T04:40:54Z INF +-----------------------------------------------------------------------------------------------+
2026-08-27T04:40:54Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7303a113-f14f-4786-b0b1-707215ed0956 status=pass target=region1.v2.argotunnel.com
2026-08-27T04:40:54Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7303a113-f14f-4786-b0b1-707215ed0956 status=pass target=region2.v2.argotunnel.com
2026-08-27T04:40:54Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=7303a113-f14f-4786-b0b1-707215ed0956 status=pass target=region1.v2.argotunnel.com
2026-08-27T04:40:54Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=7303a113-f14f-4786-b0b1-707215ed0956 status=fail target=region2.v2.argotunnel.com
2026-08-27T04:40:54Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7303a113-f14f-4786-b0b1-707215ed0956 status=pass target=region1.v2.argotunnel.com
2026-08-27T04:40:54Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7303a113-f14f-4786-b0b1-707215ed0956 status=pass target=region2.v2.argotunnel.com
2026-08-27T04:40:54Z INF precheck component="Cloudflare API" details="API is reachable" run_id=7303a113-f14f-4786-b0b1-707215ed0956 status=pass target=api.cloudflare.com:443
2026-08-27T04:40:54Z INF precheck complete hard_fail=false run_id=7303a113-f14f-4786-b0b1-707215ed0956 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:39:17] Time: Thu Aug 27 12:39:17 PM CST 2026
[12:39:17] User: root (UID: 0)
[12:39:17] === STEP 1: 启动 API (端口 8450) ===
[12:40:34] API 已在运行
[12:40:34] API 状态: OK
[12:40:34] === STEP 2: 安装 cloudflared ===
[12:40:34] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:40:34] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:40:34] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:40:34] === STEP 3: 检查认证方式 ===
[12:40:34] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:40:34] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:40:34] 检查现有 tunnel...
[12:40:35] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax09, 1xlax10, 2xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[12:40:35] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:40:35] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:40:35] 凭证文件存在
[12:40:35] 创建 config.yml...
[12:40:35] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:40:35] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:40:36] API 已在运行
[12:40:36] API 状态: OK
[12:40:36] === STEP 2: 安装 cloudflared ===
[12:40:36] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:40:37] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:40:37] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:40:37] === STEP 3: 检查认证方式 ===
[12:40:37] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:40:37] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:40:37] 检查现有 tunnel...
[12:40:37] DNS 路由结果: 2026-08-27T04:40:37Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:40:37] === STEP 5: 更新 DNS (API) ===
[12:40:37] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:40:37] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax09, 1xlax10, 2xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[12:40:37] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:40:37] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:40:37] 凭证文件存在
[12:40:37] 创建 config.yml...
[12:40:37] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:40:38] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:40:40] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[12:40:40] DNS 路由结果: 2026-08-27T04:40:40Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:40:40] === STEP 5: 更新 DNS (API) ===
[12:40:40] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[12:40:40] 设置 SSL 模式为 Full...
SSL: 跳过
[12:40:41] === STEP 6: 启动 Tunnel ===
[12:40:41] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[12:40:42] 设置 SSL 模式为 Full...
SSL: 跳过
[12:40:43] === STEP 6: 启动 Tunnel ===
[12:40:44] 启动 Named Tunnel (cert 模式)...
[12:40:44] 使用 config: /root/.cloudflared/config.yml
[12:40:44] cloudflared PID: 1732195
[12:40:46] 启动 Named Tunnel (cert 模式)...
[12:40:46] 使用 config: /root/.cloudflared/config.yml
[12:40:46] cloudflared PID: 1732214
[12:40:48] Tunnel 连接已建立!
[12:40:48] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T04:40:46Z INF Initial protocol quic
2026-08-27T04:40:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T04:40:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T04:40:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T04:40:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T04:40:46Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-27T04:40:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.7
2026-08-27T04:40:46Z INF Registered tunnel connection connIndex=0 connection=0aebb273-9331-4be1-b571-848760fd0235 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-08-27T04:40:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-27T04:40:47Z INF Registered tunnel connection connIndex=1 connection=6a0ac5b7-1a16-4f63-b277-28676884b7b5 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-27T04:40:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
.13
2026-08-27T04:40:46Z INF Registered tunnel connection connIndex=2 connection=9781b14f-be7d-4c77-9448-75ab71c78d79 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-27T04:40:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-08-27T04:40:47Z INF Registered tunnel connection connIndex=3 connection=1073cf40-019f-40d7-9ff7-bf9e724b2d05 event=0 ip=198.41.192.57 location=lax07 protocol=quic
[12:40:48] === STEP 7: 持久化 ===
[12:40:48] Tunnel 连接已建立!
[12:40:48] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T04:40:46Z INF Initial protocol quic
2026-08-27T04:40:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T04:40:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T04:40:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T04:40:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T04:40:46Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-27T04:40:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.7
2026-08-27T04:40:46Z INF Registered tunnel connection connIndex=0 connection=0aebb273-9331-4be1-b571-848760fd0235 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-08-27T04:40:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-27T04:40:47Z INF Registered tunnel connection connIndex=1 connection=6a0ac5b7-1a16-4f63-b277-28676884b7b5 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-27T04:40:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
.13
2026-08-27T04:40:46Z INF Registered tunnel connection connIndex=2 connection=9781b14f-be7d-4c77-9448-75ab71c78d79 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-27T04:40:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-08-27T04:40:47Z INF Registered tunnel connection connIndex=3 connection=1073cf40-019f-40d7-9ff7-bf9e724b2d05 event=0 ip=198.41.192.57 location=lax07 protocol=quic
[12:40:48] === STEP 7: 持久化 ===
[12:40:49] systemd 服务已配置
[12:40:49] systemd 服务已配置
[12:40:49] Cron 保活已设置
[12:40:49] === STEP 8: 验证 ===
[12:40:49] Cron 保活已设置
[12:40:49] --- API (localhost:8450) ---
[12:40:49] === STEP 8: 验证 ===
[12:40:49] --- API (localhost:8450) ---
 OK
 OK
[12:40:49] --- cloudflared 进程 ---
[12:40:49] --- cloudflared 进程 ---
root     1732195  2.2  1.9 1294676 39312 ?       Sl   12:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1732214  3.3  1.9 1360284 39532 ?       Sl   12:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1732402  0.0  1.3 1292484 27376 ?       Rl   12:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:40:49] --- aishield.tools ---
root     1732195  2.2  1.9 1294676 39312 ?       Sl   12:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1732214  3.3  1.9 1360284 39532 ?       Sl   12:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1732402  0.0  1.3 1292484 27376 ?       Rl   12:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:40:49] --- aishield.tools ---
 OK
[12:40:50] --- DNS CNAME ---
[12:40:50] --- DNS A ---
104.21.81.46
172.67.188.44
[12:40:50] === 部署汇总 ===
[12:40:50] Tunnel Mode: cert
[12:40:50] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:40:50] API: http://localhost:8450
[12:40:50] 域名: https://aishield.tools
[12:40:50] cloudflared: /usr/local/bin/cloudflared
[12:40:50] PID: 1732195
[12:40:50] Config: /root/.cloudflared/config.yml
[12:40:50] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:40:50] 状态: Named Tunnel (cert 模式) 已配置
 OK
[12:40:51] --- DNS CNAME ---
[12:40:51] --- DNS A ---
172.67.188.44
104.21.81.46
[12:40:51] === 部署汇总 ===
[12:40:51] Tunnel Mode: cert
[12:40:51] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:40:51] API: http://localhost:8450
[12:40:51] 域名: https://aishield.tools
[12:40:51] cloudflared: /usr/local/bin/cloudflared
[12:40:51] PID: 1732214
[12:40:51] Config: /root/.cloudflared/config.yml
[12:40:51] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:40:51] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-27 12:40:49 CST; 9s ago
   Main PID: 1732395 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.4M
        CPU: 138ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1732395 /bin/bash /opt/start-tunnel.sh
             └─1732402 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 27 04:40:59 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787805659.4848263, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
