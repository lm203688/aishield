=== DIAGNOSTIC ===
Time: Mon Aug 24 05:33:14 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787563994.9306595, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2960777  0.1  1.2 1360284 24664 ?       Sl   09:10   0:50 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2960898  0.1  1.1 1294676 23808 ?       Sl   09:10   0:48 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-24T01:10:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-08-24T01:10:12Z INF Registered tunnel connection connIndex=0 connection=397cafc6-f5fd-49cd-a597-af6fee6c2ba9 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-24T01:10:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-24T01:10:13Z INF Registered tunnel connection connIndex=1 connection=b7285ffe-e2ab-4a8b-97ea-f6145c534584 event=0 ip=198.41.192.167 location=lax12 protocol=quic
2026-08-24T01:10:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
2026-08-24T01:10:14Z INF Registered tunnel connection connIndex=2 connection=d7de1149-e1bd-4187-98bd-d3423b29fcf3 event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-24T01:10:14Z INF +-------------------------------------------------------------------------------------+
2026-08-24T01:10:14Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-24T01:10:14Z INF +-------------------------------------------------------------------------------------+
2026-08-24T01:10:14Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-24T01:10:14Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-24T01:10:14Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-24T01:10:14Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-24T01:10:14Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-24T01:10:14Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-24T01:10:14Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-24T01:10:14Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-24T01:10:14Z INF |                                                                                     |
2026-08-24T01:10:14Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-24T01:10:14Z INF +-------------------------------------------------------------------------------------+
2026-08-24T01:10:14Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b280bfae-28e1-4bc3-a825-4bef679baffe status=pass target=region1.v2.argotunnel.com
2026-08-24T01:10:14Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b280bfae-28e1-4bc3-a825-4bef679baffe status=pass target=region2.v2.argotunnel.com
2026-08-24T01:10:14Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b280bfae-28e1-4bc3-a825-4bef679baffe status=pass target=region1.v2.argotunnel.com
2026-08-24T01:10:14Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b280bfae-28e1-4bc3-a825-4bef679baffe status=pass target=region2.v2.argotunnel.com
2026-08-24T01:10:14Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b280bfae-28e1-4bc3-a825-4bef679baffe status=pass target=region1.v2.argotunnel.com
2026-08-24T01:10:14Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b280bfae-28e1-4bc3-a825-4bef679baffe status=pass target=region2.v2.argotunnel.com
2026-08-24T01:10:14Z INF precheck component="Cloudflare API" details="API is reachable" run_id=b280bfae-28e1-4bc3-a825-4bef679baffe status=pass target=api.cloudflare.com:443
2026-08-24T01:10:14Z INF precheck complete hard_fail=false run_id=b280bfae-28e1-4bc3-a825-4bef679baffe suggested_protocol=quic
2026-08-24T01:10:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-08-24T01:10:15Z INF Registered tunnel connection connIndex=3 connection=4da29ba6-e856-4b44-9468-7b15c68b1343 event=0 ip=198.41.200.63 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[09:08:28] Time: Mon Aug 24 09:08:28 AM CST 2026
[09:08:28] User: root (UID: 0)
[09:08:28] === STEP 1: 启动 API (端口 8450) ===
[09:09:58] API 已在运行
[09:09:58] API 状态: OK
[09:09:58] === STEP 2: 安装 cloudflared ===
[09:09:58] cloudflared 安装路径: /usr/local/bin/cloudflared
[09:09:58] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:09:58] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:09:58] === STEP 3: 检查认证方式 ===
[09:09:58] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:09:58] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:09:58] 检查现有 tunnel...
[09:09:59] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 2xlax11, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[09:09:59] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:09:59] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[09:09:59] 凭证文件存在
[09:09:59] 创建 config.yml...
[09:09:59] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[09:09:59] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:10:00] DNS 路由结果: 2026-08-24T01:10:00Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[09:10:00] === STEP 5: 更新 DNS (API) ===
[09:10:00] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:10:02] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[09:10:03] 设置 SSL 模式为 Full...
SSL: 跳过
[09:10:04] === STEP 6: 启动 Tunnel ===
[09:10:07] 启动 Named Tunnel (cert 模式)...
[09:10:07] 使用 config: /root/.cloudflared/config.yml
[09:10:07] cloudflared PID: 2960777
[09:10:13] Tunnel 连接已建立!
[09:10:13] --- cloudflared 日志 (最后 15 行) ---
2026-08-24T01:10:07Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-24T01:10:07Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-24T01:10:07Z INF Generated Connector ID: 4a76ae38-b124-44ce-88de-0279c8db6199
2026-08-24T01:10:07Z INF Initial protocol quic
2026-08-24T01:10:07Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T01:10:07Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T01:10:07Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T01:10:07Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T01:10:07Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-24T01:10:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.193
2026-08-24T01:10:12Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-24T01:10:12Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.193
2026-08-24T01:10:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-08-24T01:10:12Z INF Registered tunnel connection connIndex=0 connection=397cafc6-f5fd-49cd-a597-af6fee6c2ba9 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-24T01:10:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
[09:10:13] === STEP 7: 持久化 ===
[09:10:13] systemd 服务已配置
[09:10:13] Cron 保活已设置
[09:10:13] === STEP 8: 验证 ===
[09:10:13] --- API (localhost:8450) ---
 OK
[09:10:13] --- cloudflared 进程 ---
root     2960777  1.6  1.9 1294676 39192 ?       Sl   09:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2960898  0.0  1.3 1292740 27428 ?       Rl   09:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[09:10:13] --- aishield.tools ---
 OK
[09:10:15] --- DNS CNAME ---
[09:10:15] --- DNS A ---
104.21.81.46
172.67.188.44
[09:10:15] === 部署汇总 ===
[09:10:15] Tunnel Mode: cert
[09:10:15] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:10:15] API: http://localhost:8450
[09:10:15] 域名: https://aishield.tools
[09:10:15] cloudflared: /usr/local/bin/cloudflared
[09:10:15] PID: 2960777
[09:10:15] Config: /root/.cloudflared/config.yml
[09:10:15] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:10:15] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-24 09:10:13 CST; 8h ago
   Main PID: 2960897 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 21.5M
        CPU: 48.858s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2960897 /bin/bash /opt/start-tunnel.sh
             └─2960898 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 24 09:33:15 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787563995.5650365, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
