=== DIAGNOSTIC ===
Time: Sun Aug 16 10:10:03 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786889403.681151, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3922494  0.1  1.2 1294676 25032 ?       Sl   11:11   1:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3922584  0.1  1.3 1360284 26712 ?       Sl   11:11   1:05 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-16T03:11:59Z ERR Request failed error="stream 5 canceled by remote with error code 0" connIndex=0 dest=https://aishield.tools/ event=0 ip=198.41.200.13 type=http
2026-08-16T03:12:04Z INF +-----------------------------------------------------------------------------------------------+
2026-08-16T03:12:04Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-16T03:12:04Z INF +-----------------------------------------------------------------------------------------------+
2026-08-16T03:12:04Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-16T03:12:04Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-16T03:12:04Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-16T03:12:04Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-16T03:12:04Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-16T03:12:04Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-16T03:12:04Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-16T03:12:04Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-16T03:12:04Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-16T03:12:04Z INF |                                                                                               |
2026-08-16T03:12:04Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-16T03:12:04Z INF +-----------------------------------------------------------------------------------------------+
2026-08-16T03:12:04Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7ebb6261-95e4-4620-89c4-a463f87ed6d4 status=pass target=region1.v2.argotunnel.com
2026-08-16T03:12:04Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7ebb6261-95e4-4620-89c4-a463f87ed6d4 status=pass target=region2.v2.argotunnel.com
2026-08-16T03:12:04Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=7ebb6261-95e4-4620-89c4-a463f87ed6d4 status=pass target=region1.v2.argotunnel.com
2026-08-16T03:12:04Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=7ebb6261-95e4-4620-89c4-a463f87ed6d4 status=fail target=region2.v2.argotunnel.com
2026-08-16T03:12:04Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7ebb6261-95e4-4620-89c4-a463f87ed6d4 status=pass target=region1.v2.argotunnel.com
2026-08-16T03:12:04Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7ebb6261-95e4-4620-89c4-a463f87ed6d4 status=pass target=region2.v2.argotunnel.com
2026-08-16T03:12:04Z INF precheck component="Cloudflare API" details="API is reachable" run_id=7ebb6261-95e4-4620-89c4-a463f87ed6d4 status=pass target=api.cloudflare.com:443
2026-08-16T03:12:04Z INF precheck complete hard_fail=false run_id=7ebb6261-95e4-4620-89c4-a463f87ed6d4 suggested_protocol=http2
2026-08-16T05:16:46Z ERR  error="stream 53 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-16T05:16:46Z ERR Request failed error="stream 53 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.192.47 type=http
2026-08-16T05:31:45Z ERR  error="stream 73 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-16T05:31:45Z ERR Request failed error="stream 73 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.200.63 type=http
2026-08-16T13:34:07Z ERR  error="stream 185 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-16T13:34:07Z ERR Request failed error="stream 185 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.192.47 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[11:05:08] Time: Sun Aug 16 11:05:08 AM CST 2026
[11:05:08] User: root (UID: 0)
[11:05:08] === STEP 1: 启动 API (端口 8450) ===
[11:11:18] API 已在运行
[11:11:18] API 状态: OK
[11:11:18] === STEP 2: 安装 cloudflared ===
[11:11:18] cloudflared 安装路径: /usr/local/bin/cloudflared
[11:11:18] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:11:18] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:11:18] === STEP 3: 检查认证方式 ===
[11:11:18] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[11:11:18] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[11:11:18] 检查现有 tunnel...
[11:11:19] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax07, 1xlax08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[11:11:19] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:11:19] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[11:11:19] 凭证文件存在
[11:11:19] 创建 config.yml...
[11:11:19] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[11:11:19] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:11:20] DNS 路由结果: 2026-08-16T03:11:20Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[11:11:20] === STEP 5: 更新 DNS (API) ===
[11:11:20] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:11:21] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[11:11:22] 设置 SSL 模式为 Full...
SSL: 跳过
[11:11:22] === STEP 6: 启动 Tunnel ===
[11:11:25] 启动 Named Tunnel (cert 模式)...
[11:11:25] 使用 config: /root/.cloudflared/config.yml
[11:11:25] cloudflared PID: 3921784
[11:11:27] Tunnel 连接已建立!
[11:11:27] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T03:11:25Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-16T03:11:25Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-16T03:11:25Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-16T03:11:25Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-16T03:11:25Z INF Generated Connector ID: 052176cd-ae01-44b9-8389-267a08a3e9de
2026-08-16T03:11:25Z INF Initial protocol quic
2026-08-16T03:11:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T03:11:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T03:11:26Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T03:11:26Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T03:11:26Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-16T03:11:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-16T03:11:26Z INF Registered tunnel connection connIndex=0 connection=a6b4a999-9c2e-45c9-86bc-f178900d8c1a event=0 ip=198.41.192.227 location=lax05 protocol=quic
2026-08-16T03:11:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-16T03:11:27Z INF Registered tunnel connection connIndex=1 connection=9ad2ca69-044b-475a-9d36-87190659631c event=0 ip=198.41.200.13 location=lax01 protocol=quic
[11:11:27] === STEP 7: 持久化 ===
[11:11:28] systemd 服务已配置
[11:11:28] Cron 保活已设置
[11:11:28] === STEP 8: 验证 ===
[11:11:28] --- API (localhost:8450) ---
 OK
[11:11:28] --- cloudflared 进程 ---
root     3921784  3.3  1.8 1293844 37412 ?       Sl   11:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3921928  0.0  1.3 1292740 27264 ?       Rl   11:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[11:11:28] --- aishield.tools ---
 OK
[11:11:31] --- DNS CNAME ---
[11:11:31] --- DNS A ---
104.21.81.46
172.67.188.44
[11:11:31] === 部署汇总 ===
[11:11:31] Tunnel Mode: cert
[11:11:31] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:11:31] API: http://localhost:8450
[11:11:31] 域名: https://aishield.tools
[11:11:31] cloudflared: /usr/local/bin/cloudflared
[11:11:31] PID: 3921784
[11:11:31] Config: /root/.cloudflared/config.yml
[11:11:31] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:11:31] 状态: Named Tunnel (cert 模式) 已配置
[11:11:45] API 已在运行
[11:11:45] API 状态: OK
[11:11:45] === STEP 2: 安装 cloudflared ===
[11:11:45] cloudflared 安装路径: /usr/local/bin/cloudflared
[11:11:45] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:11:45] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:11:45] === STEP 3: 检查认证方式 ===
[11:11:45] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[11:11:45] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[11:11:45] 检查现有 tunnel...
[11:11:45] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax07, 1xlax08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[11:11:45] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:11:45] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[11:11:45] 凭证文件存在
[11:11:45] 创建 config.yml...
[11:11:45] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[11:11:45] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:11:47] DNS 路由结果: 2026-08-16T03:11:47Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[11:11:47] === STEP 5: 更新 DNS (API) ===
[11:11:47] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:11:48] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[11:11:50] 设置 SSL 模式为 Full...
SSL: 跳过
[11:11:51] === STEP 6: 启动 Tunnel ===
[11:11:54] 启动 Named Tunnel (cert 模式)...
[11:11:54] 使用 config: /root/.cloudflared/config.yml
[11:11:54] cloudflared PID: 3922494
[11:11:56] Tunnel 连接已建立!
[11:11:56] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T03:11:54Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-16T03:11:54Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-16T03:11:54Z INF Generated Connector ID: 06d44673-ef96-43c6-b742-8ea2deb3685d
2026-08-16T03:11:54Z INF Initial protocol quic
2026-08-16T03:11:54Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T03:11:54Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T03:11:54Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T03:11:54Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T03:11:54Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-16T03:11:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-16T03:11:54Z INF Registered tunnel connection connIndex=0 connection=5152aa0c-1e88-41b2-b2a1-5bba4f24b2f3 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-16T03:11:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-16T03:11:54Z INF Registered tunnel connection connIndex=1 connection=7f9348cb-6433-4b9f-8fe7-5ea360c758bd event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-08-16T03:11:55Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
2026-08-16T03:11:55Z INF Registered tunnel connection connIndex=2 connection=d015f477-d901-45ab-a7da-c09b438bb563 event=0 ip=198.41.192.47 location=lax11 protocol=quic
[11:11:56] === STEP 7: 持久化 ===
[11:11:56] systemd 服务已配置
[11:11:56] Cron 保活已设置
[11:11:56] === STEP 8: 验证 ===
[11:11:56] --- API (localhost:8450) ---
 OK
[11:11:56] --- cloudflared 进程 ---
root     3922494  4.5  1.9 1294100 38408 ?       Sl   11:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3922584  0.0  1.3 1292740 28060 ?       Sl   11:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[11:11:56] --- aishield.tools ---
 OK
[11:11:58] --- DNS CNAME ---
[11:11:58] --- DNS A ---
172.67.188.44
104.21.81.46
[11:11:58] === 部署汇总 ===
[11:11:58] Tunnel Mode: cert
[11:11:58] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:11:58] API: http://localhost:8450
[11:11:58] 域名: https://aishield.tools
[11:11:58] cloudflared: /usr/local/bin/cloudflared
[11:11:58] PID: 3922494
[11:11:58] Config: /root/.cloudflared/config.yml
[11:11:58] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:11:58] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-16 11:11:56 CST; 10h ago
   Main PID: 3922581 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 21.8M
        CPU: 1min 5.066s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3922581 /bin/bash /opt/start-tunnel.sh
             └─3922584 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sun Aug 16 14:10:04 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786889404.4358141, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
