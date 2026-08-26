=== DIAGNOSTIC ===
Time: Wed Aug 26 10:31:49 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787754709.3733876, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      635392  0.1  1.4 1294676 28400 ?       Sl   08:40   1:33 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      635500  0.1  1.3 1294676 27844 ?       Sl   08:40   1:34 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-26T13:29:19Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.63
2026-08-26T13:29:19Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.63
2026-08-26T13:29:19Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.200.63
2026-08-26T13:29:19Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.113
2026-08-26T13:29:19Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.113
2026-08-26T13:29:19Z WRN failed to serve tunnel connection error="datagram manager encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.113
2026-08-26T13:29:19Z WRN Serve tunnel error error="datagram manager encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.113
2026-08-26T13:29:19Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.113
2026-08-26T13:29:20Z WRN Connection terminated error="accept stream listener encountered a failure while serving" connIndex=2
2026-08-26T13:29:20Z WRN Connection terminated error="datagram manager encountered a failure while serving" connIndex=1
2026-08-26T13:29:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-26T13:29:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-26T13:29:42Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.113
2026-08-26T13:29:42Z INF Retrying connection in up to 4s connIndex=1 event=0 ip=198.41.200.113
2026-08-26T13:29:42Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.63
2026-08-26T13:29:42Z INF Retrying connection in up to 4s connIndex=2 event=0 ip=198.41.200.63
2026-08-26T13:29:45Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-26T13:29:45Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-26T13:29:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-26T13:29:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-26T13:29:54Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.13
2026-08-26T13:29:54Z INF Retrying connection in up to 8s connIndex=1 event=0 ip=198.41.200.13
2026-08-26T13:29:54Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.113
2026-08-26T13:29:54Z INF Retrying connection in up to 8s connIndex=2 event=0 ip=198.41.200.113
2026-08-26T13:30:00Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-26T13:30:01Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-26T13:30:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-26T13:30:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-26T13:30:50Z INF Registered tunnel connection connIndex=1 connection=8aa12de6-f5ba-4cf0-8d9b-ddcb3079b23f event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-26T13:30:51Z INF Registered tunnel connection connIndex=2 connection=fc6bfa5d-4bd7-4b65-99cd-82935d917fe7 event=0 ip=198.41.200.13 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:40:15] Time: Wed Aug 26 08:40:15 AM CST 2026
[08:40:15] User: root (UID: 0)
[08:40:15] === STEP 1: 启动 API (端口 8450) ===
[08:40:19] API 已在运行
[08:40:19] API 状态: OK
[08:40:19] === STEP 2: 安装 cloudflared ===
[08:40:19] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:40:19] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:40:19] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:40:19] === STEP 3: 检查认证方式 ===
[08:40:19] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:40:19] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:40:19] 检查现有 tunnel...
[08:40:20] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 5xlax01, 1xlax05, 2xlax09, 2xlax10, 1xlax12, 1xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
2026-08-26T00:40:20Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:40:20] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:40:20] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:40:20] 凭证文件存在
[08:40:20] 创建 config.yml...
[08:40:20] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:40:20] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:40:21] DNS 路由结果: 2026-08-26T00:40:21Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:40:21] === STEP 5: 更新 DNS (API) ===
[08:40:21] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:40:22] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:40:22] 设置 SSL 模式为 Full...
SSL: 跳过
[08:40:23] === STEP 6: 启动 Tunnel ===
[08:40:26] 启动 Named Tunnel (cert 模式)...
[08:40:26] 使用 config: /root/.cloudflared/config.yml
[08:40:26] cloudflared PID: 635392
[08:40:28] Tunnel 连接已建立!
[08:40:28] --- cloudflared 日志 (最后 15 行) ---
2026-08-26T00:40:26Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-26T00:40:26Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-26T00:40:26Z INF Generated Connector ID: 50dbb32c-5011-4133-b519-ed076d5e233f
2026-08-26T00:40:26Z INF Initial protocol quic
2026-08-26T00:40:26Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-26T00:40:26Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-26T00:40:26Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-26T00:40:26Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-26T00:40:26Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-26T00:40:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-26T00:40:27Z INF Registered tunnel connection connIndex=0 connection=eb5366cd-2b15-436a-ac64-79dab7a5d640 event=0 ip=198.41.192.227 location=lax10 protocol=quic
2026-08-26T00:40:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-26T00:40:27Z INF Registered tunnel connection connIndex=1 connection=4ee0d873-a502-4ed8-9cd9-a57d55a8f574 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-26T00:40:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-26T00:40:28Z INF Registered tunnel connection connIndex=2 connection=34cd1d8c-b611-4474-95c7-4e3bc5b48cce event=0 ip=198.41.200.63 location=lax01 protocol=quic
[08:40:28] === STEP 7: 持久化 ===
[08:40:29] systemd 服务已配置
[08:40:29] Cron 保活已设置
[08:40:29] === STEP 8: 验证 ===
[08:40:29] --- API (localhost:8450) ---
 OK
[08:40:29] --- cloudflared 进程 ---
root      635392  3.3  1.9 1294420 39328 ?       Sl   08:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      635500  0.0  1.3 1292484 27844 ?       Sl   08:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:40:29] --- aishield.tools ---
 OK
[08:40:31] --- DNS CNAME ---
[08:40:32] --- DNS A ---
172.67.188.44
104.21.81.46
[08:40:32] === 部署汇总 ===
[08:40:32] Tunnel Mode: cert
[08:40:32] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:40:32] API: http://localhost:8450
[08:40:32] 域名: https://aishield.tools
[08:40:32] cloudflared: /usr/local/bin/cloudflared
[08:40:32] PID: 635392
[08:40:32] Config: /root/.cloudflared/config.yml
[08:40:32] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:40:32] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-26 08:40:29 CST; 13h ago
   Main PID: 635499 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 21.4M
        CPU: 1min 34.057s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─635499 /bin/bash /opt/start-tunnel.sh
             └─635500 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug 26 14:31:49 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787754710.3228, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
