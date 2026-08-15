=== DIAGNOSTIC ===
Time: Sat Aug 15 06:09:14 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786788554.2413852, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2981966  0.1  1.5 1294676 32100 ?       Sl   11:17   0:39 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2982142  0.1  1.6 1294676 33000 ?       Sl   11:17   0:40 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-15T03:17:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
2026-08-15T03:17:29Z INF Registered tunnel connection connIndex=1 connection=4939dded-107e-4f94-ab21-12c431a7a6dd event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-08-15T03:17:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-08-15T03:17:30Z INF Registered tunnel connection connIndex=2 connection=631efbea-d7f7-43ab-873a-15bacce28933 event=0 ip=198.41.192.7 location=lax09 protocol=quic
2026-08-15T03:17:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-15T03:17:31Z INF Registered tunnel connection connIndex=3 connection=154cf85a-d0e8-4d3c-93b9-af75845476f3 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-15T03:17:35Z INF +-------------------------------------------------------------------------------------+
2026-08-15T03:17:35Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-15T03:17:35Z INF +-------------------------------------------------------------------------------------+
2026-08-15T03:17:35Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-15T03:17:35Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-15T03:17:35Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-15T03:17:35Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-15T03:17:35Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-15T03:17:35Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-15T03:17:35Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-15T03:17:35Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-15T03:17:35Z INF |                                                                                     |
2026-08-15T03:17:35Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-15T03:17:35Z INF +-------------------------------------------------------------------------------------+
2026-08-15T03:17:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=51cb8b70-c39b-4230-820f-a3b0b013f3d0 status=pass target=region1.v2.argotunnel.com
2026-08-15T03:17:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=51cb8b70-c39b-4230-820f-a3b0b013f3d0 status=pass target=region2.v2.argotunnel.com
2026-08-15T03:17:35Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=51cb8b70-c39b-4230-820f-a3b0b013f3d0 status=pass target=region1.v2.argotunnel.com
2026-08-15T03:17:35Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=51cb8b70-c39b-4230-820f-a3b0b013f3d0 status=pass target=region2.v2.argotunnel.com
2026-08-15T03:17:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=51cb8b70-c39b-4230-820f-a3b0b013f3d0 status=pass target=region1.v2.argotunnel.com
2026-08-15T03:17:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=51cb8b70-c39b-4230-820f-a3b0b013f3d0 status=pass target=region2.v2.argotunnel.com
2026-08-15T03:17:35Z INF precheck component="Cloudflare API" details="API is reachable" run_id=51cb8b70-c39b-4230-820f-a3b0b013f3d0 status=pass target=api.cloudflare.com:443
2026-08-15T03:17:35Z INF precheck complete hard_fail=false run_id=51cb8b70-c39b-4230-820f-a3b0b013f3d0 suggested_protocol=quic
2026-08-15T03:17:52Z ERR  error="stream 9 canceled by remote with error code 0" connIndex=0 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-15T03:17:52Z ERR Request failed error="stream 9 canceled by remote with error code 0" connIndex=0 dest=https://aishield.tools/ event=0 ip=198.41.200.63 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[11:17:19] Time: Sat Aug 15 11:17:19 AM CST 2026
[11:17:19] User: root (UID: 0)
[11:17:19] === STEP 1: 启动 API (端口 8450) ===
[11:17:20] API 已在运行
[11:17:20] API 状态: OK
[11:17:20] === STEP 2: 安装 cloudflared ===
[11:17:20] cloudflared 安装路径: /usr/local/bin/cloudflared
[11:17:20] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:17:21] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:17:21] === STEP 3: 检查认证方式 ===
[11:17:21] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[11:17:21] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[11:17:21] 检查现有 tunnel...
[11:17:21] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax05, 1xlax08, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-15T03:17:21Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[11:17:21] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:17:21] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[11:17:21] 凭证文件存在
[11:17:21] 创建 config.yml...
[11:17:21] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[11:17:21] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:17:23] DNS 路由结果: 2026-08-15T03:17:23Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[11:17:23] === STEP 5: 更新 DNS (API) ===
[11:17:23] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:17:23] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[11:17:24] 设置 SSL 模式为 Full...
SSL: 跳过
[11:17:25] === STEP 6: 启动 Tunnel ===
[11:17:28] 启动 Named Tunnel (cert 模式)...
[11:17:28] 使用 config: /root/.cloudflared/config.yml
[11:17:28] cloudflared PID: 2981966
[11:17:30] Tunnel 连接已建立!
[11:17:30] --- cloudflared 日志 (最后 15 行) ---
2026-08-15T03:17:28Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-15T03:17:28Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-15T03:17:28Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-15T03:17:28Z INF Generated Connector ID: 1249af4f-f865-471d-9eed-91ecfe4b6f3f
2026-08-15T03:17:28Z INF Initial protocol quic
2026-08-15T03:17:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T03:17:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T03:17:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T03:17:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T03:17:28Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-15T03:17:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-15T03:17:29Z INF Registered tunnel connection connIndex=0 connection=079bed34-958a-48cb-ae68-049a9be320dc event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-15T03:17:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
2026-08-15T03:17:29Z INF Registered tunnel connection connIndex=1 connection=4939dded-107e-4f94-ab21-12c431a7a6dd event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-08-15T03:17:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
[11:17:30] === STEP 7: 持久化 ===
[11:17:31] systemd 服务已配置
[11:17:31] Cron 保活已设置
[11:17:31] === STEP 8: 验证 ===
[11:17:31] --- API (localhost:8450) ---
 OK
[11:17:31] --- cloudflared 进程 ---
root     2981966  3.0  1.9 1294420 39012 ?       Sl   11:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2982142  0.0  1.3 1292740 27356 ?       Rl   11:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[11:17:31] --- aishield.tools ---
 OK
[11:17:32] --- DNS CNAME ---
[11:17:32] --- DNS A ---
172.67.188.44
104.21.81.46
[11:17:32] === 部署汇总 ===
[11:17:32] Tunnel Mode: cert
[11:17:32] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:17:32] API: http://localhost:8450
[11:17:32] 域名: https://aishield.tools
[11:17:32] cloudflared: /usr/local/bin/cloudflared
[11:17:32] PID: 2981966
[11:17:32] Config: /root/.cloudflared/config.yml
[11:17:32] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:17:32] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-15 11:17:31 CST; 6h ago
   Main PID: 2982134 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 18.6M
        CPU: 40.978s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2982134 /bin/bash /opt/start-tunnel.sh
             └─2982142 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sat Aug 15 10:09:14 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786788554.7759497, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
