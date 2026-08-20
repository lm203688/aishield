=== DIAGNOSTIC ===
Time: Fri Aug 21 07:13:11 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787267591.3929393, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     4066841  0.1  1.2 1294676 25104 ?       Sl   02:10   0:26 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4067077  0.1  1.3 1294676 26292 ?       Sl   02:10   0:27 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-20T18:10:22Z INF Registered tunnel connection connIndex=2 connection=90066aa7-e129-4584-8eec-6ba073e68b17 event=0 ip=198.41.192.167 location=lax10 protocol=quic
2026-08-20T18:10:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.53
2026-08-20T18:10:23Z INF Registered tunnel connection connIndex=3 connection=9c9808ce-1891-4746-869c-17c35e2d61e0 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-20T18:10:30Z INF +-----------------------------------------------------------------------------------------------+
2026-08-20T18:10:30Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-20T18:10:30Z INF +-----------------------------------------------------------------------------------------------+
2026-08-20T18:10:30Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-20T18:10:30Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-20T18:10:30Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-20T18:10:30Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-20T18:10:30Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-20T18:10:30Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-20T18:10:30Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-20T18:10:30Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-20T18:10:30Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-20T18:10:30Z INF |                                                                                               |
2026-08-20T18:10:30Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-20T18:10:30Z INF +-----------------------------------------------------------------------------------------------+
2026-08-20T18:10:30Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=79a743df-50b8-4268-877f-65a626392f12 status=pass target=region1.v2.argotunnel.com
2026-08-20T18:10:30Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=79a743df-50b8-4268-877f-65a626392f12 status=pass target=region2.v2.argotunnel.com
2026-08-20T18:10:30Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=79a743df-50b8-4268-877f-65a626392f12 status=pass target=region1.v2.argotunnel.com
2026-08-20T18:10:30Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=79a743df-50b8-4268-877f-65a626392f12 status=fail target=region2.v2.argotunnel.com
2026-08-20T18:10:30Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=79a743df-50b8-4268-877f-65a626392f12 status=pass target=region1.v2.argotunnel.com
2026-08-20T18:10:30Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=79a743df-50b8-4268-877f-65a626392f12 status=pass target=region2.v2.argotunnel.com
2026-08-20T18:10:30Z INF precheck component="Cloudflare API" details="API is reachable" run_id=79a743df-50b8-4268-877f-65a626392f12 status=pass target=api.cloudflare.com:443
2026-08-20T18:10:30Z INF precheck complete hard_fail=false run_id=79a743df-50b8-4268-877f-65a626392f12 suggested_protocol=http2
2026-08-20T18:45:22Z ERR  error="stream 77 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-20T18:45:22Z ERR Request failed error="stream 77 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.192.167 type=http
2026-08-20T22:31:22Z ERR  error="stream 57 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-20T22:31:22Z ERR Request failed error="stream 57 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.192.27 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:03:36] Time: Fri Aug 21 02:03:36 AM CST 2026
[02:03:36] User: root (UID: 0)
[02:03:36] === STEP 1: 启动 API (端口 8450) ===
[02:10:06] API 已在运行
[02:10:06] API 状态: OK
[02:10:06] === STEP 2: 安装 cloudflared ===
[02:10:06] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:10:06] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:10:06] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:10:06] === STEP 3: 检查认证方式 ===
[02:10:06] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:10:06] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:10:06] 检查现有 tunnel...
[02:10:07] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax09, 1xlax10, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-20T18:10:07Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:10:07] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:10:07] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:10:07] 凭证文件存在
[02:10:07] 创建 config.yml...
[02:10:07] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:10:07] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:10:09] DNS 路由结果: 2026-08-20T18:10:09Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:10:09] === STEP 5: 更新 DNS (API) ===
[02:10:09] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:10:09] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:10:10] 设置 SSL 模式为 Full...
SSL: 跳过
[02:10:11] === STEP 6: 启动 Tunnel ===
[02:10:12] API 已在运行
[02:10:12] API 状态: OK
[02:10:12] === STEP 2: 安装 cloudflared ===
[02:10:12] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:10:12] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:10:12] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:10:12] === STEP 3: 检查认证方式 ===
[02:10:12] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:10:12] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:10:12] 检查现有 tunnel...
[02:10:13] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[02:10:13] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:10:13] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:10:13] 凭证文件存在
[02:10:13] 创建 config.yml...
[02:10:13] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:10:13] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:10:14] 启动 Named Tunnel (cert 模式)...
[02:10:14] 使用 config: /root/.cloudflared/config.yml
[02:10:14] cloudflared PID: 4066267
[02:10:14] DNS 路由结果: 2026-08-20T18:10:14Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:10:14] === STEP 5: 更新 DNS (API) ===
[02:10:14] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:10:15] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[02:10:16] Tunnel 连接已建立!
[02:10:16] --- cloudflared 日志 (最后 15 行) ---
2026-08-20T18:10:14Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-20T18:10:14Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-20T18:10:14Z INF Generated Connector ID: 61056d2c-4db5-4d1c-aeca-c50fbe8838ed
2026-08-20T18:10:14Z INF Initial protocol quic
2026-08-20T18:10:14Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T18:10:14Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T18:10:14Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T18:10:14Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T18:10:14Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-20T18:10:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-20T18:10:14Z INF Registered tunnel connection connIndex=0 connection=beb3b294-a197-4da1-88cc-54e8af3c8fd8 event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-08-20T18:10:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-20T18:10:15Z INF Registered tunnel connection connIndex=1 connection=ce40fa06-fd95-4d6b-98c6-7a93a0e86d74 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-20T18:10:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-08-20T18:10:16Z INF Registered tunnel connection connIndex=2 connection=8b4723b8-1584-4fc9-b840-c85f91546c44 event=0 ip=198.41.192.7 location=lax09 protocol=quic
[02:10:16] === STEP 7: 持久化 ===
DNS 更新: OK
[02:10:16] 设置 SSL 模式为 Full...
SSL: 跳过
[02:10:16] === STEP 6: 启动 Tunnel ===
[02:10:17] systemd 服务已配置
[02:10:17] Cron 保活已设置
[02:10:17] === STEP 8: 验证 ===
[02:10:17] --- API (localhost:8450) ---
 OK
[02:10:17] --- cloudflared 进程 ---
root     4066267  3.3  1.9 1294676 39224 ?       Sl   02:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4066450  0.0  1.3 1292740 27236 ?       Sl   02:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:10:17] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[02:10:18] --- DNS CNAME ---
[02:10:18] --- DNS A ---
104.21.81.46
172.67.188.44
[02:10:18] === 部署汇总 ===
[02:10:18] Tunnel Mode: cert
[02:10:18] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:10:18] API: http://localhost:8450
[02:10:18] 域名: https://aishield.tools
[02:10:18] cloudflared: /usr/local/bin/cloudflared
[02:10:18] PID: 4066267
[02:10:18] Config: /root/.cloudflared/config.yml
[02:10:18] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:10:18] 状态: Named Tunnel (cert 模式) 已配置
[02:10:19] 启动 Named Tunnel (cert 模式)...
[02:10:19] 使用 config: /root/.cloudflared/config.yml
[02:10:19] cloudflared PID: 4066841
[02:10:21] Tunnel 连接已建立!
[02:10:21] --- cloudflared 日志 (最后 15 行) ---
2026-08-20T18:10:20Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-20T18:10:20Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-20T18:10:20Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-20T18:10:20Z INF Generated Connector ID: 61928122-f0fe-45ff-a8da-816186f65ebc
2026-08-20T18:10:20Z INF Initial protocol quic
2026-08-20T18:10:20Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T18:10:20Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T18:10:20Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T18:10:20Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T18:10:20Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-20T18:10:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-20T18:10:20Z INF Registered tunnel connection connIndex=0 connection=f12a2e24-0d82-49c4-90f6-606dc74f1c2d event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-20T18:10:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-20T18:10:21Z INF Registered tunnel connection connIndex=1 connection=0922f251-b51f-411b-83a4-b8f9df0e1069 event=0 ip=198.41.192.27 location=lax12 protocol=quic
2026-08-20T18:10:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
[02:10:21] === STEP 7: 持久化 ===
[02:10:22] systemd 服务已配置
[02:10:22] Cron 保活已设置
[02:10:22] === STEP 8: 验证 ===
[02:10:22] --- API (localhost:8450) ---
 OK
[02:10:22] --- cloudflared 进程 ---
root     4066841  4.0  1.8 1293836 37312 ?       Sl   02:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4067077  0.0  1.3 1292484 27428 ?       Dl   02:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:10:22] --- aishield.tools ---
 OK
[02:10:24] --- DNS CNAME ---
[02:10:24] --- DNS A ---
172.67.188.44
104.21.81.46
[02:10:24] === 部署汇总 ===
[02:10:24] Tunnel Mode: cert
[02:10:24] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:10:24] API: http://localhost:8450
[02:10:24] 域名: https://aishield.tools
[02:10:24] cloudflared: /usr/local/bin/cloudflared
[02:10:24] PID: 4066841
[02:10:24] Config: /root/.cloudflared/config.yml
[02:10:24] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:10:24] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-21 02:10:22 CST; 5h 2min ago
   Main PID: 4067073 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 20.7M
        CPU: 27.875s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─4067073 /bin/bash /opt/start-tunnel.sh
             └─4067077 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 20 23:13:12 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787267592.44168, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
