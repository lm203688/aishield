=== DIAGNOSTIC ===
Time: Tue Aug 18 02:19:27 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787033967.6215787, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1499901  0.1  1.1 1360284 23872 ?       Sl   08:34   0:30 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1500046  0.1  1.2 1294676 24880 ?       Sl   08:34   0:30 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-18T00:34:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
2026-08-18T00:34:37Z INF Registered tunnel connection connIndex=2 connection=7ab75be3-d21f-4a51-8803-936ccfb0077d event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-08-18T00:34:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
2026-08-18T00:34:42Z INF +-------------------------------------------------------------------------------------+
2026-08-18T00:34:42Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-18T00:34:42Z INF +-------------------------------------------------------------------------------------+
2026-08-18T00:34:42Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-18T00:34:42Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T00:34:42Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T00:34:42Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T00:34:42Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T00:34:42Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T00:34:42Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T00:34:42Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-18T00:34:42Z INF |                                                                                     |
2026-08-18T00:34:42Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-18T00:34:42Z INF +-------------------------------------------------------------------------------------+
2026-08-18T00:34:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=1120a15c-b950-4d28-ab4b-47e69203aa33 status=pass target=region1.v2.argotunnel.com
2026-08-18T00:34:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=1120a15c-b950-4d28-ab4b-47e69203aa33 status=pass target=region2.v2.argotunnel.com
2026-08-18T00:34:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=1120a15c-b950-4d28-ab4b-47e69203aa33 status=pass target=region1.v2.argotunnel.com
2026-08-18T00:34:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=1120a15c-b950-4d28-ab4b-47e69203aa33 status=pass target=region2.v2.argotunnel.com
2026-08-18T00:34:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=1120a15c-b950-4d28-ab4b-47e69203aa33 status=pass target=region1.v2.argotunnel.com
2026-08-18T00:34:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=1120a15c-b950-4d28-ab4b-47e69203aa33 status=pass target=region2.v2.argotunnel.com
2026-08-18T00:34:42Z INF precheck component="Cloudflare API" details="API is reachable" run_id=1120a15c-b950-4d28-ab4b-47e69203aa33 status=pass target=api.cloudflare.com:443
2026-08-18T00:34:42Z INF precheck complete hard_fail=false run_id=1120a15c-b950-4d28-ab4b-47e69203aa33 suggested_protocol=quic
2026-08-18T00:34:43Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-08-18T00:34:43Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.73
2026-08-18T00:34:45Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-18T00:34:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.53
2026-08-18T00:34:57Z INF Registered tunnel connection connIndex=3 connection=28ba0fb3-1ead-45e4-9c07-ea75d2108f46 event=0 ip=198.41.200.53 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:34:25] Time: Tue Aug 18 08:34:25 AM CST 2026
[08:34:25] User: root (UID: 0)
[08:34:25] === STEP 1: 启动 API (端口 8450) ===
[08:34:27] API 已在运行
[08:34:27] API 状态: OK
[08:34:27] === STEP 2: 安装 cloudflared ===
[08:34:27] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:34:27] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:34:27] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:34:27] === STEP 3: 检查认证方式 ===
[08:34:27] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:34:27] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:34:27] 检查现有 tunnel...
[08:34:28] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 1xlax08, 2xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[08:34:28] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:34:28] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:34:28] 凭证文件存在
[08:34:28] 创建 config.yml...
[08:34:28] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:34:28] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:34:30] DNS 路由结果: 2026-08-18T00:34:30Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:34:30] === STEP 5: 更新 DNS (API) ===
[08:34:30] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:34:31] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:34:32] 设置 SSL 模式为 Full...
SSL: 跳过
[08:34:32] === STEP 6: 启动 Tunnel ===
[08:34:35] 启动 Named Tunnel (cert 模式)...
[08:34:35] 使用 config: /root/.cloudflared/config.yml
[08:34:35] cloudflared PID: 1499901
[08:34:37] Tunnel 连接已建立!
[08:34:37] --- cloudflared 日志 (最后 15 行) ---
2026-08-18T00:34:35Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-18T00:34:35Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-18T00:34:35Z INF Generated Connector ID: 30378fac-817d-498c-9a58-cee068c3e8d7
2026-08-18T00:34:36Z INF Initial protocol quic
2026-08-18T00:34:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T00:34:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T00:34:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T00:34:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T00:34:36Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-18T00:34:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
2026-08-18T00:34:36Z INF Registered tunnel connection connIndex=0 connection=650b1375-7943-4375-adc1-e5f7d66dc8d3 event=0 ip=198.41.192.47 location=lax05 protocol=quic
2026-08-18T00:34:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-18T00:34:36Z INF Registered tunnel connection connIndex=1 connection=64a6558b-c5e7-44c3-8271-c4bb2b0a9cae event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-18T00:34:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
2026-08-18T00:34:37Z INF Registered tunnel connection connIndex=2 connection=7ab75be3-d21f-4a51-8803-936ccfb0077d event=0 ip=198.41.192.107 location=lax08 protocol=quic
[08:34:37] === STEP 7: 持久化 ===
[08:34:38] systemd 服务已配置
[08:34:38] Cron 保活已设置
[08:34:38] === STEP 8: 验证 ===
[08:34:38] --- API (localhost:8450) ---
 OK
[08:34:38] --- cloudflared 进程 ---
root     1499901  3.3  1.9 1360284 38960 ?       Sl   08:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1500046  0.0  1.3 1292484 27140 ?       Sl   08:34   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:34:38] --- aishield.tools ---
 OK
[08:34:39] --- DNS CNAME ---
[08:34:39] --- DNS A ---
172.67.188.44
104.21.81.46
[08:34:39] === 部署汇总 ===
[08:34:39] Tunnel Mode: cert
[08:34:39] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:34:39] API: http://localhost:8450
[08:34:39] 域名: https://aishield.tools
[08:34:39] cloudflared: /usr/local/bin/cloudflared
[08:34:39] PID: 1499901
[08:34:39] Config: /root/.cloudflared/config.yml
[08:34:39] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:34:39] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-18 08:34:38 CST; 5h 44min ago
   Main PID: 1500038 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.2M
        CPU: 30.919s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1500038 /bin/bash /opt/start-tunnel.sh
             └─1500046 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Tue Aug 18 06:19:28 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787033968.1407819, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
