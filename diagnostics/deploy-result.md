=== DIAGNOSTIC ===
Time: Sun Aug 23 02:04:59 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787421899.1546106, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1749495  1.0  1.9 1294676 39304 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1749600  1.3  1.9 1294420 40092 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-22T18:04:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-22T18:04:47Z INF Registered tunnel connection connIndex=0 connection=3a106b72-cd15-4fc6-ac93-d61a4212d8f3 event=0 ip=198.41.192.27 location=sjc06 protocol=quic
2026-08-22T18:04:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-22T18:04:47Z INF Registered tunnel connection connIndex=1 connection=f011c568-da2d-4bdb-95b4-ddf4ebffacc7 event=0 ip=198.41.200.113 location=sjc05 protocol=quic
2026-08-22T18:04:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-22T18:04:48Z INF Registered tunnel connection connIndex=2 connection=7d186fa6-6e07-4bc7-9227-2e4a9ca46b44 event=0 ip=198.41.192.167 location=sjc01 protocol=quic
2026-08-22T18:04:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-22T18:04:49Z INF Registered tunnel connection connIndex=3 connection=d9f8c50b-fc23-495b-8bfe-0bd65d7f8f37 event=0 ip=198.41.200.43 location=sjc10 protocol=quic
2026-08-22T18:04:53Z INF +-------------------------------------------------------------------------------------+
2026-08-22T18:04:53Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-22T18:04:53Z INF +-------------------------------------------------------------------------------------+
2026-08-22T18:04:53Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-22T18:04:53Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-22T18:04:53Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-22T18:04:53Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-22T18:04:53Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-22T18:04:53Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-22T18:04:53Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-22T18:04:53Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-22T18:04:53Z INF |                                                                                     |
2026-08-22T18:04:53Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-22T18:04:53Z INF +-------------------------------------------------------------------------------------+
2026-08-22T18:04:53Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b87d5b81-25d5-4b67-a3cf-83a1422c6be4 status=pass target=region1.v2.argotunnel.com
2026-08-22T18:04:53Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b87d5b81-25d5-4b67-a3cf-83a1422c6be4 status=pass target=region2.v2.argotunnel.com
2026-08-22T18:04:53Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b87d5b81-25d5-4b67-a3cf-83a1422c6be4 status=pass target=region1.v2.argotunnel.com
2026-08-22T18:04:53Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b87d5b81-25d5-4b67-a3cf-83a1422c6be4 status=pass target=region2.v2.argotunnel.com
2026-08-22T18:04:53Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b87d5b81-25d5-4b67-a3cf-83a1422c6be4 status=pass target=region1.v2.argotunnel.com
2026-08-22T18:04:53Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b87d5b81-25d5-4b67-a3cf-83a1422c6be4 status=pass target=region2.v2.argotunnel.com
2026-08-22T18:04:53Z INF precheck component="Cloudflare API" details="API is reachable" run_id=b87d5b81-25d5-4b67-a3cf-83a1422c6be4 status=pass target=api.cloudflare.com:443
2026-08-22T18:04:53Z INF precheck complete hard_fail=false run_id=b87d5b81-25d5-4b67-a3cf-83a1422c6be4 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:03:19] Time: Sun Aug 23 02:03:19 AM CST 2026
[02:03:19] User: root (UID: 0)
[02:03:19] === STEP 1: 启动 API (端口 8450) ===
[02:04:39] API 已在运行
[02:04:39] API 状态: OK
[02:04:39] === STEP 2: 安装 cloudflared ===
[02:04:39] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:39] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:39] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:39] === STEP 3: 检查认证方式 ===
[02:04:39] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:39] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:39] 检查现有 tunnel...
[02:04:40] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xsjc01, 1xsjc05, 1xsjc06, 1xsjc07, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
[02:04:40] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:40] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:40] 凭证文件存在
[02:04:40] 创建 config.yml...
[02:04:40] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:40] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:41] DNS 路由结果: 2026-08-22T18:04:41Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:41] === STEP 5: 更新 DNS (API) ===
[02:04:41] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:42] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:04:42] 设置 SSL 模式为 Full...
SSL: 跳过
[02:04:43] === STEP 6: 启动 Tunnel ===
[02:04:46] 启动 Named Tunnel (cert 模式)...
[02:04:46] 使用 config: /root/.cloudflared/config.yml
[02:04:46] cloudflared PID: 1749495
[02:04:48] Tunnel 连接已建立!
[02:04:48] --- cloudflared 日志 (最后 15 行) ---
2026-08-22T18:04:46Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-22T18:04:46Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-22T18:04:46Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-22T18:04:46Z INF Generated Connector ID: 5847da1a-7222-4524-a5c4-6f52ca5740c8
2026-08-22T18:04:46Z INF Initial protocol quic
2026-08-22T18:04:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-22T18:04:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-22T18:04:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-22T18:04:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-22T18:04:46Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-22T18:04:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-22T18:04:47Z INF Registered tunnel connection connIndex=0 connection=3a106b72-cd15-4fc6-ac93-d61a4212d8f3 event=0 ip=198.41.192.27 location=sjc06 protocol=quic
2026-08-22T18:04:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-22T18:04:47Z INF Registered tunnel connection connIndex=1 connection=f011c568-da2d-4bdb-95b4-ddf4ebffacc7 event=0 ip=198.41.200.113 location=sjc05 protocol=quic
2026-08-22T18:04:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
[02:04:48] === STEP 7: 持久化 ===
[02:04:49] systemd 服务已配置
[02:04:49] Cron 保活已设置
[02:04:49] === STEP 8: 验证 ===
[02:04:49] --- API (localhost:8450) ---
 OK
[02:04:49] --- cloudflared 进程 ---
root     1749495  3.3  1.8 1293844 38192 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1749600  0.0  1.3 1292484 27440 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:04:49] --- aishield.tools ---
 OK
[02:04:51] --- DNS CNAME ---
[02:04:51] --- DNS A ---
104.21.81.46
172.67.188.44
[02:04:51] === 部署汇总 ===
[02:04:51] Tunnel Mode: cert
[02:04:51] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:51] API: http://localhost:8450
[02:04:51] 域名: https://aishield.tools
[02:04:51] cloudflared: /usr/local/bin/cloudflared
[02:04:51] PID: 1749495
[02:04:51] Config: /root/.cloudflared/config.yml
[02:04:51] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:51] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-23 02:04:49 CST; 9s ago
   Main PID: 1749599 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.8M
        CPU: 148ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1749599 /bin/bash /opt/start-tunnel.sh
             └─1749600 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sat Aug 22 18:04:59 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787421899.9512916, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
