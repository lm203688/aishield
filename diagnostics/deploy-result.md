=== DIAGNOSTIC ===
Time: Wed Aug 19 02:17:26 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787077046.4766467, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2183073  0.1  1.5 1294676 30428 ?       Sl   02:03   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2183181  0.1  1.4 1294676 28456 ?       Sl   02:03   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-18T18:03:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-18T18:03:57Z INF Registered tunnel connection connIndex=0 connection=e05d05f5-1c22-4290-9341-7f73ecdfc570 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-18T18:03:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-18T18:03:57Z INF Registered tunnel connection connIndex=1 connection=9b51b1fc-b3e9-4d9b-b3a2-cfd335e75b93 event=0 ip=198.41.192.107 location=lax11 protocol=quic
2026-08-18T18:03:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-18T18:03:58Z INF Registered tunnel connection connIndex=2 connection=019bf989-20ec-4f94-b629-6b40b04ffe4e event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-18T18:03:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.227
2026-08-18T18:03:59Z INF Registered tunnel connection connIndex=3 connection=c7b98b7e-f53b-475a-968a-84f34cb8ebd3 event=0 ip=198.41.192.227 location=lax09 protocol=quic
2026-08-18T18:04:03Z INF +-------------------------------------------------------------------------------------+
2026-08-18T18:04:03Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-18T18:04:03Z INF +-------------------------------------------------------------------------------------+
2026-08-18T18:04:03Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-18T18:04:03Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T18:04:03Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T18:04:03Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T18:04:03Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T18:04:03Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T18:04:03Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T18:04:03Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-18T18:04:03Z INF |                                                                                     |
2026-08-18T18:04:03Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-18T18:04:03Z INF +-------------------------------------------------------------------------------------+
2026-08-18T18:04:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b8e7ad94-276d-4c39-a8b9-db447604cfc4 status=pass target=region1.v2.argotunnel.com
2026-08-18T18:04:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b8e7ad94-276d-4c39-a8b9-db447604cfc4 status=pass target=region2.v2.argotunnel.com
2026-08-18T18:04:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b8e7ad94-276d-4c39-a8b9-db447604cfc4 status=pass target=region1.v2.argotunnel.com
2026-08-18T18:04:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b8e7ad94-276d-4c39-a8b9-db447604cfc4 status=pass target=region2.v2.argotunnel.com
2026-08-18T18:04:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b8e7ad94-276d-4c39-a8b9-db447604cfc4 status=pass target=region1.v2.argotunnel.com
2026-08-18T18:04:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b8e7ad94-276d-4c39-a8b9-db447604cfc4 status=pass target=region2.v2.argotunnel.com
2026-08-18T18:04:03Z INF precheck component="Cloudflare API" details="API is reachable" run_id=b8e7ad94-276d-4c39-a8b9-db447604cfc4 status=pass target=api.cloudflare.com:443
2026-08-18T18:04:03Z INF precheck complete hard_fail=false run_id=b8e7ad94-276d-4c39-a8b9-db447604cfc4 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:03:48] Time: Wed Aug 19 02:03:48 AM CST 2026
[02:03:48] User: root (UID: 0)
[02:03:48] === STEP 1: 启动 API (端口 8450) ===
[02:03:49] API 已在运行
[02:03:49] API 状态: OK
[02:03:49] === STEP 2: 安装 cloudflared ===
[02:03:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:03:50] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:03:50] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:03:50] === STEP 3: 检查认证方式 ===
[02:03:50] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:03:50] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:03:50] 检查现有 tunnel...
[02:03:50] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 1xlax05, 2xlax09, 1xlax11, 2xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[02:03:50] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:03:50] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:03:50] 凭证文件存在
[02:03:50] 创建 config.yml...
[02:03:50] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:03:50] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:03:51] DNS 路由结果: 2026-08-18T18:03:51Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:03:51] === STEP 5: 更新 DNS (API) ===
[02:03:51] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:03:52] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:03:53] 设置 SSL 模式为 Full...
SSL: 跳过
[02:03:53] === STEP 6: 启动 Tunnel ===
[02:03:57] 启动 Named Tunnel (cert 模式)...
[02:03:57] 使用 config: /root/.cloudflared/config.yml
[02:03:57] cloudflared PID: 2183073
[02:03:59] Tunnel 连接已建立!
[02:03:59] --- cloudflared 日志 (最后 15 行) ---
2026-08-18T18:03:57Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-18T18:03:57Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-18T18:03:57Z INF Generated Connector ID: 068cdc61-f3bc-4fb3-a0dc-596a49dcffe6
2026-08-18T18:03:57Z INF Initial protocol quic
2026-08-18T18:03:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T18:03:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T18:03:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T18:03:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T18:03:57Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-18T18:03:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-18T18:03:57Z INF Registered tunnel connection connIndex=0 connection=e05d05f5-1c22-4290-9341-7f73ecdfc570 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-18T18:03:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-18T18:03:57Z INF Registered tunnel connection connIndex=1 connection=9b51b1fc-b3e9-4d9b-b3a2-cfd335e75b93 event=0 ip=198.41.192.107 location=lax11 protocol=quic
2026-08-18T18:03:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-18T18:03:58Z INF Registered tunnel connection connIndex=2 connection=019bf989-20ec-4f94-b629-6b40b04ffe4e event=0 ip=198.41.200.13 location=lax01 protocol=quic
[02:03:59] === STEP 7: 持久化 ===
[02:03:59] systemd 服务已配置
[02:03:59] Cron 保活已设置
[02:03:59] === STEP 8: 验证 ===
[02:03:59] --- API (localhost:8450) ---
 OK
[02:03:59] --- cloudflared 进程 ---
root     2183073  4.0  1.9 1293844 38692 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2183181  0.0  1.3 1292484 26696 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:03:59] --- aishield.tools ---
 OK
[02:04:00] --- DNS CNAME ---
[02:04:01] --- DNS A ---
104.21.81.46
172.67.188.44
[02:04:01] === 部署汇总 ===
[02:04:01] Tunnel Mode: cert
[02:04:01] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:01] API: http://localhost:8450
[02:04:01] 域名: https://aishield.tools
[02:04:01] cloudflared: /usr/local/bin/cloudflared
[02:04:01] PID: 2183073
[02:04:01] Config: /root/.cloudflared/config.yml
[02:04:01] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:01] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-19 02:03:59 CST; 13min ago
   Main PID: 2183173 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 15.9M
        CPU: 1.405s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2183173 /bin/bash /opt/start-tunnel.sh
             └─2183181 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=1897042,fd=3))                                                    
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
Time: Tue Aug 18 18:17:26 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787077047.0680752, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
