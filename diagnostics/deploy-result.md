=== DIAGNOSTIC ===
Time: Tue Aug 25 08:32:01 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787617921.2990756, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3877252  1.2  1.8 1294676 37792 ?       Sl   08:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3877345  1.8  1.8 1294420 37340 ?       Sl   08:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-25T00:31:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-25T00:31:51Z INF Registered tunnel connection connIndex=1 connection=1cbe5951-df75-466a-a293-824b8aaeca73 event=0 ip=198.41.192.67 location=lax10 protocol=quic
2026-08-25T00:31:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-08-25T00:31:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.227
2026-08-25T00:31:54Z INF Registered tunnel connection connIndex=3 connection=67194d77-2bc4-4343-a5e6-93d0ab694d74 event=0 ip=198.41.192.227 location=lax08 protocol=quic
2026-08-25T00:31:57Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.73
2026-08-25T00:31:57Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.73
2026-08-25T00:31:57Z INF +-------------------------------------------------------------------------------------+
2026-08-25T00:31:57Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-25T00:31:57Z INF +-------------------------------------------------------------------------------------+
2026-08-25T00:31:57Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-25T00:31:57Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-25T00:31:57Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-25T00:31:57Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-25T00:31:57Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-25T00:31:57Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-25T00:31:57Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-25T00:31:57Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-25T00:31:57Z INF |                                                                                     |
2026-08-25T00:31:57Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-25T00:31:57Z INF +-------------------------------------------------------------------------------------+
2026-08-25T00:31:57Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=72571e94-83f2-4708-992a-174f39f14256 status=pass target=region1.v2.argotunnel.com
2026-08-25T00:31:57Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=72571e94-83f2-4708-992a-174f39f14256 status=pass target=region2.v2.argotunnel.com
2026-08-25T00:31:57Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=72571e94-83f2-4708-992a-174f39f14256 status=pass target=region1.v2.argotunnel.com
2026-08-25T00:31:57Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=72571e94-83f2-4708-992a-174f39f14256 status=pass target=region2.v2.argotunnel.com
2026-08-25T00:31:57Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=72571e94-83f2-4708-992a-174f39f14256 status=pass target=region1.v2.argotunnel.com
2026-08-25T00:31:57Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=72571e94-83f2-4708-992a-174f39f14256 status=pass target=region2.v2.argotunnel.com
2026-08-25T00:31:57Z INF precheck component="Cloudflare API" details="API is reachable" run_id=72571e94-83f2-4708-992a-174f39f14256 status=pass target=api.cloudflare.com:443
2026-08-25T00:31:57Z INF precheck complete hard_fail=false run_id=72571e94-83f2-4708-992a-174f39f14256 suggested_protocol=quic
2026-08-25T00:31:58Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:31:41] Time: Tue Aug 25 08:31:41 AM CST 2026
[08:31:41] User: root (UID: 0)
[08:31:41] === STEP 1: 启动 API (端口 8450) ===
[08:31:43] API 已在运行
[08:31:43] API 状态: OK
[08:31:43] === STEP 2: 安装 cloudflared ===
[08:31:43] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:31:44] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:31:44] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:31:44] === STEP 3: 检查认证方式 ===
[08:31:44] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:31:44] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:31:44] 检查现有 tunnel...
[08:31:44] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 1xlax07, 1xlax09, 1xlax10, 1xlax11, 2xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
[08:31:44] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:31:44] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:31:44] 凭证文件存在
[08:31:44] 创建 config.yml...
[08:31:44] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:31:44] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:31:45] DNS 路由结果: 2026-08-25T00:31:45Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:31:45] === STEP 5: 更新 DNS (API) ===
[08:31:45] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:31:46] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:31:47] 设置 SSL 模式为 Full...
SSL: 跳过
[08:31:47] === STEP 6: 启动 Tunnel ===
[08:31:51] 启动 Named Tunnel (cert 模式)...
[08:31:51] 使用 config: /root/.cloudflared/config.yml
[08:31:51] cloudflared PID: 3877252
[08:31:53] Tunnel 连接已建立!
[08:31:53] --- cloudflared 日志 (最后 15 行) ---
2026-08-25T00:31:51Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-25T00:31:51Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-25T00:31:51Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-25T00:31:51Z INF Generated Connector ID: 5f91bc3e-8431-42ad-a643-0071e3e5d0ed
2026-08-25T00:31:51Z INF Initial protocol quic
2026-08-25T00:31:51Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-25T00:31:51Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-25T00:31:51Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-25T00:31:51Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-25T00:31:51Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-25T00:31:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-25T00:31:51Z INF Registered tunnel connection connIndex=0 connection=b7e0380c-2309-4ab6-8ded-1d6acfcf696f event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-25T00:31:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-25T00:31:51Z INF Registered tunnel connection connIndex=1 connection=1cbe5951-df75-466a-a293-824b8aaeca73 event=0 ip=198.41.192.67 location=lax10 protocol=quic
2026-08-25T00:31:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[08:31:53] === STEP 7: 持久化 ===
[08:31:53] systemd 服务已配置
[08:31:53] Cron 保活已设置
[08:31:53] === STEP 8: 验证 ===
[08:31:53] --- API (localhost:8450) ---
 OK
[08:31:53] --- cloudflared 进程 ---
root     3877252  5.0  1.9 1294676 39332 ?       Sl   08:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3877345  0.0  1.3 1292484 27916 ?       Rl   08:31   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:31:53] --- aishield.tools ---
 OK
[08:31:55] --- DNS CNAME ---
[08:31:55] --- DNS A ---
104.21.81.46
172.67.188.44
[08:31:55] === 部署汇总 ===
[08:31:55] Tunnel Mode: cert
[08:31:55] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:31:55] API: http://localhost:8450
[08:31:55] 域名: https://aishield.tools
[08:31:55] cloudflared: /usr/local/bin/cloudflared
[08:31:55] PID: 3877252
[08:31:55] Config: /root/.cloudflared/config.yml
[08:31:55] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:31:55] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-25 08:31:53 CST; 7s ago
   Main PID: 3877344 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.6M
        CPU: 164ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3877344 /bin/bash /opt/start-tunnel.sh
             └─3877345 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Tue Aug 25 00:32:01 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787617921.7952878, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
