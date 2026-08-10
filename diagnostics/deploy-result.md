=== DIAGNOSTIC ===
Time: Mon Aug 10 06:51:24 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786359084.7827594, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
NOT RUNNING
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-10T10:51:21Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=bf1e8332-f0b8-4716-80ad-52505795f9ab status=fail target=region2.v2.argotunnel.com
2026-08-10T10:51:21Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bf1e8332-f0b8-4716-80ad-52505795f9ab status=pass target=region1.v2.argotunnel.com
2026-08-10T10:51:21Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bf1e8332-f0b8-4716-80ad-52505795f9ab status=pass target=region2.v2.argotunnel.com
2026-08-10T10:51:21Z INF precheck component="Cloudflare API" details="API is reachable" run_id=bf1e8332-f0b8-4716-80ad-52505795f9ab status=pass target=api.cloudflare.com:443
2026-08-10T10:51:21Z INF precheck complete hard_fail=false run_id=bf1e8332-f0b8-4716-80ad-52505795f9ab suggested_protocol=http2
2026-08-10T10:51:23Z INF Initiating graceful shutdown due to signal terminated ...
2026-08-10T10:51:23Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.192.57
2026-08-10T10:51:23Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.57
2026-08-10T10:51:23Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.57
2026-08-10T10:51:23Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.192.57
2026-08-10T10:51:23Z ERR Connection terminated connIndex=2
2026-08-10T10:51:23Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.192.227
2026-08-10T10:51:23Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.227
2026-08-10T10:51:23Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.227
2026-08-10T10:51:23Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.227
2026-08-10T10:51:23Z ERR Connection terminated connIndex=0
2026-08-10T10:51:23Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.200.33
2026-08-10T10:51:23Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.33
2026-08-10T10:51:23Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.33
2026-08-10T10:51:23Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.200.33
2026-08-10T10:51:23Z ERR Connection terminated connIndex=3
2026-08-10T10:51:23Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.200.43
2026-08-10T10:51:23Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.43
2026-08-10T10:51:23Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.43
2026-08-10T10:51:23Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.43
2026-08-10T10:51:23Z ERR Connection terminated connIndex=1
2026-08-10T10:51:23Z ERR no more connections active and exiting
2026-08-10T10:51:23Z INF Tunnel server stopped
2026-08-10T10:51:23Z ERR icmp router terminated error="context canceled"
2026-08-10T10:51:23Z INF Metrics server stopped
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:49:48] Time: Mon Aug 10 06:49:48 PM CST 2026
[18:49:48] User: root (UID: 0)
[18:49:48] === STEP 1: 启动 API (端口 8450) ===
[18:50:59] API 已在运行
[18:50:59] API 状态: OK
[18:50:59] === STEP 2: 安装 cloudflared ===
[18:50:59] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:50:59] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:50:59] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:50:59] === STEP 3: 检查认证方式 ===
[18:51:00] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:51:00] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:51:00] 检查现有 tunnel...
[18:51:01] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xlax01, 1xlax08, 2xlax10, 1xlax11, 1xsjc05 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[18:51:01] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:51:01] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:51:01] 凭证文件存在
[18:51:01] 创建 config.yml...
[18:51:01] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:51:01] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:51:03] DNS 路由结果: 2026-08-10T10:51:03Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:51:03] === STEP 5: 更新 DNS (API) ===
[18:51:03] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:51:05] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:51:07] 设置 SSL 模式为 Full...
SSL: 跳过
[18:51:08] === STEP 6: 启动 Tunnel ===
[18:51:11] 启动 Named Tunnel (cert 模式)...
[18:51:11] 使用 config: /root/.cloudflared/config.yml
[18:51:11] cloudflared PID: 2754500
[18:51:13] Tunnel 连接已建立!
[18:51:13] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T10:51:11Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T10:51:11Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T10:51:11Z INF Generated Connector ID: 06c8cef0-78b8-45ff-ac07-492399fd3449
2026-08-10T10:51:11Z INF Initial protocol quic
2026-08-10T10:51:11Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:51:11Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:51:11Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:51:11Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:51:11Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-10T10:51:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-10T10:51:11Z INF Registered tunnel connection connIndex=0 connection=77b21e6c-80dd-41ae-b971-3248ef5de0c9 event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-08-10T10:51:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-10T10:51:12Z INF Registered tunnel connection connIndex=1 connection=236ef82c-128a-496d-822c-7d6c7f773805 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-10T10:51:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
2026-08-10T10:51:13Z INF Registered tunnel connection connIndex=2 connection=c4fe81e1-a524-4aec-8aa5-bfb94652c598 event=0 ip=198.41.192.57 location=lax10 protocol=quic
[18:51:13] === STEP 7: 持久化 ===
[18:51:13] systemd 服务已配置
[18:51:13] Cron 保活已设置
[18:51:13] === STEP 8: 验证 ===
[18:51:13] --- API (localhost:8450) ---
 OK
[18:51:13] --- cloudflared 进程 ---
root     2754500  5.0  1.9 1294676 39236 ?       Sl   18:51   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2754593  0.0  1.3 1292740 27488 ?       Rl   18:51   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:51:13] --- aishield.tools ---
 OK
[18:51:17] --- DNS CNAME ---
[18:51:17] --- DNS A ---
104.21.81.46
172.67.188.44
[18:51:17] === 部署汇总 ===
[18:51:17] Tunnel Mode: cert
[18:51:17] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:51:17] API: http://localhost:8450
[18:51:17] 域名: https://aishield.tools
[18:51:17] cloudflared: /usr/local/bin/cloudflared
[18:51:17] PID: 2754500
[18:51:17] Config: /root/.cloudflared/config.yml
[18:51:17] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:51:17] 状态: Named Tunnel (cert 模式) 已配置
[18:51:18] API 已在运行
[18:51:18] API 状态: OK
[18:51:18] === STEP 2: 安装 cloudflared ===
[18:51:18] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:51:18] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:51:18] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:51:18] === STEP 3: 检查认证方式 ===
[18:51:18] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:51:18] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:51:18] 检查现有 tunnel...
[18:51:19] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xlax01, 1xlax07, 1xlax09, 2xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[18:51:19] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:51:19] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:51:19] 凭证文件存在
[18:51:19] 创建 config.yml...
[18:51:19] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:51:19] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:51:21] DNS 路由结果: 2026-08-10T10:51:21Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:51:21] === STEP 5: 更新 DNS (API) ===
[18:51:21] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:51:22] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:51:22] 设置 SSL 模式为 Full...
SSL: 跳过
[18:51:23] === STEP 6: 启动 Tunnel ===
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) since Mon 2026-08-10 18:51:23 CST; 1s ago
    Process: 2754592 ExecStart=/opt/start-tunnel.sh (code=exited, status=0/SUCCESS)
   Main PID: 2754592 (code=exited, status=0/SUCCESS)
        CPU: 253ms

Aug 10 18:51:23 VM-0-11-ubuntu systemd[1]: cloudflared-tunnel.service: Deactivated successfully.
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450      0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                    
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
Time: Mon Aug 10 10:51:25 UTC 2026

=== curl test (aishield.tools) ===
error code: 1033

=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
