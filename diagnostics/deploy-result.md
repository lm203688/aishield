=== DIAGNOSTIC ===
Time: Tue Aug 18 08:25:07 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787012707.982948, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1490363  0.1  1.7 1294676 36064 ?       Sl   08:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1490489  0.1  1.7 1294420 35856 ?       Sl   08:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-18T00:20:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.193
2026-08-18T00:20:54Z INF +-------------------------------------------------------------------------------------+
2026-08-18T00:20:54Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-18T00:20:54Z INF +-------------------------------------------------------------------------------------+
2026-08-18T00:20:54Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-18T00:20:54Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T00:20:54Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T00:20:54Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T00:20:54Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T00:20:54Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T00:20:54Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T00:20:54Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-18T00:20:54Z INF |                                                                                     |
2026-08-18T00:20:54Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-18T00:20:54Z INF +-------------------------------------------------------------------------------------+
2026-08-18T00:20:54Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8fb15c39-ad80-4669-abb5-a7dbfafd9343 status=pass target=region1.v2.argotunnel.com
2026-08-18T00:20:54Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8fb15c39-ad80-4669-abb5-a7dbfafd9343 status=pass target=region2.v2.argotunnel.com
2026-08-18T00:20:54Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8fb15c39-ad80-4669-abb5-a7dbfafd9343 status=pass target=region1.v2.argotunnel.com
2026-08-18T00:20:54Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8fb15c39-ad80-4669-abb5-a7dbfafd9343 status=pass target=region2.v2.argotunnel.com
2026-08-18T00:20:54Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8fb15c39-ad80-4669-abb5-a7dbfafd9343 status=pass target=region1.v2.argotunnel.com
2026-08-18T00:20:54Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8fb15c39-ad80-4669-abb5-a7dbfafd9343 status=pass target=region2.v2.argotunnel.com
2026-08-18T00:20:54Z INF precheck component="Cloudflare API" details="API is reachable" run_id=8fb15c39-ad80-4669-abb5-a7dbfafd9343 status=pass target=api.cloudflare.com:443
2026-08-18T00:20:54Z INF precheck complete hard_fail=false run_id=8fb15c39-ad80-4669-abb5-a7dbfafd9343 suggested_protocol=quic
2026-08-18T00:20:54Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-18T00:20:54Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-08-18T00:20:56Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-18T00:21:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-08-18T00:21:04Z INF Registered tunnel connection connIndex=3 connection=938d79ec-5c22-4181-83f4-969aa95f5e4b event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-18T00:21:09Z ERR  error="stream 9 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-18T00:21:09Z ERR Request failed error="stream 9 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.200.113 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:20:39] Time: Tue Aug 18 08:20:39 AM CST 2026
[08:20:39] User: root (UID: 0)
[08:20:39] === STEP 1: 启动 API (端口 8450) ===
[08:20:40] API 已在运行
[08:20:40] API 状态: OK
[08:20:40] === STEP 2: 安装 cloudflared ===
[08:20:40] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:20:40] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:20:40] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:20:40] === STEP 3: 检查认证方式 ===
[08:20:40] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:20:40] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:20:40] 检查现有 tunnel...
[08:20:41] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax08, 3xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
2026-08-18T00:20:41Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:20:41] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:20:41] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:20:41] 凭证文件存在
[08:20:41] 创建 config.yml...
[08:20:41] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:20:41] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:20:42] DNS 路由结果: 2026-08-18T00:20:42Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:20:42] === STEP 5: 更新 DNS (API) ===
[08:20:42] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:20:43] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:20:43] 设置 SSL 模式为 Full...
SSL: 跳过
[08:20:44] === STEP 6: 启动 Tunnel ===
[08:20:47] 启动 Named Tunnel (cert 模式)...
[08:20:47] 使用 config: /root/.cloudflared/config.yml
[08:20:47] cloudflared PID: 1490363
[08:20:49] Tunnel 连接已建立!
[08:20:49] --- cloudflared 日志 (最后 15 行) ---
2026-08-18T00:20:47Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-18T00:20:47Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-18T00:20:47Z INF Generated Connector ID: 366bb100-06b5-4d16-900a-141af65fc40f
2026-08-18T00:20:47Z INF Initial protocol quic
2026-08-18T00:20:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T00:20:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T00:20:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T00:20:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T00:20:47Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-18T00:20:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-18T00:20:47Z INF Registered tunnel connection connIndex=0 connection=3bfd1b60-8364-47ad-a2e7-50086587dbb2 event=0 ip=198.41.192.167 location=lax10 protocol=quic
2026-08-18T00:20:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-18T00:20:48Z INF Registered tunnel connection connIndex=1 connection=9d786f23-d80b-4b39-b440-a8beb54137e3 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-18T00:20:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-08-18T00:20:49Z INF Registered tunnel connection connIndex=2 connection=d286a33e-6129-4c25-8222-26d6a56d6b45 event=0 ip=198.41.192.7 location=lax07 protocol=quic
[08:20:49] === STEP 7: 持久化 ===
[08:20:50] systemd 服务已配置
[08:20:50] Cron 保活已设置
[08:20:50] === STEP 8: 验证 ===
[08:20:50] --- API (localhost:8450) ---
 OK
[08:20:50] --- cloudflared 进程 ---
root     1490363  3.0  1.9 1294676 39272 ?       Sl   08:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1490489  0.0  1.3 1292740 27136 ?       Rl   08:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:20:50] --- aishield.tools ---
 OK
[08:20:51] --- DNS CNAME ---
[08:20:51] --- DNS A ---
172.67.188.44
104.21.81.46
[08:20:51] === 部署汇总 ===
[08:20:51] Tunnel Mode: cert
[08:20:51] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:20:51] API: http://localhost:8450
[08:20:51] 域名: https://aishield.tools
[08:20:51] cloudflared: /usr/local/bin/cloudflared
[08:20:51] PID: 1490363
[08:20:51] Config: /root/.cloudflared/config.yml
[08:20:51] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:20:51] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-18 08:20:50 CST; 4min 17s ago
   Main PID: 1490481 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 15.4M
        CPU: 499ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1490481 /bin/bash /opt/start-tunnel.sh
             └─1490489 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2342254,fd=3))                                                    
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
Time: Tue Aug 18 00:25:08 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787012708.5908122, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
