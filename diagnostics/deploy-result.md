=== DIAGNOSTIC ===
Time: Thu Aug 13 10:11:49 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786630309.152347, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1293677  0.1  1.3 1294676 27048 ?       Sl   16:21   0:34 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1293804  0.1  1.3 1294676 26332 ?       Sl   16:21   0:35 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-13T08:21:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-13T08:21:36Z INF Registered tunnel connection connIndex=0 connection=83ecdb62-e4fb-410c-98cc-c96d814f2954 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-13T08:21:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-13T08:21:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-13T08:21:37Z INF Registered tunnel connection connIndex=2 connection=94607c2f-adab-46f5-a468-fd70a67bbdb2 event=0 ip=198.41.192.77 location=lax08 protocol=quic
2026-08-13T08:21:38Z INF Registered tunnel connection connIndex=1 connection=a49e3805-b755-495c-a5d4-5c1bff0f0399 event=0 ip=198.41.192.27 location=lax08 protocol=quic
2026-08-13T08:21:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.23
2026-08-13T08:21:38Z INF Registered tunnel connection connIndex=3 connection=e3b928d2-5f00-4c53-b6c3-785e47500c46 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-13T08:21:42Z INF +-------------------------------------------------------------------------------------+
2026-08-13T08:21:42Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-13T08:21:42Z INF +-------------------------------------------------------------------------------------+
2026-08-13T08:21:42Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-13T08:21:42Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-13T08:21:42Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-13T08:21:42Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-13T08:21:42Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-13T08:21:42Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-13T08:21:42Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-13T08:21:42Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-13T08:21:42Z INF |                                                                                     |
2026-08-13T08:21:42Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-13T08:21:42Z INF +-------------------------------------------------------------------------------------+
2026-08-13T08:21:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=4dcbe9f4-acfd-4f92-b8a5-4a0c5cfd4c34 status=pass target=region1.v2.argotunnel.com
2026-08-13T08:21:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=4dcbe9f4-acfd-4f92-b8a5-4a0c5cfd4c34 status=pass target=region2.v2.argotunnel.com
2026-08-13T08:21:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=4dcbe9f4-acfd-4f92-b8a5-4a0c5cfd4c34 status=pass target=region1.v2.argotunnel.com
2026-08-13T08:21:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=4dcbe9f4-acfd-4f92-b8a5-4a0c5cfd4c34 status=pass target=region2.v2.argotunnel.com
2026-08-13T08:21:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4dcbe9f4-acfd-4f92-b8a5-4a0c5cfd4c34 status=pass target=region1.v2.argotunnel.com
2026-08-13T08:21:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4dcbe9f4-acfd-4f92-b8a5-4a0c5cfd4c34 status=pass target=region2.v2.argotunnel.com
2026-08-13T08:21:42Z INF precheck component="Cloudflare API" details="API is reachable" run_id=4dcbe9f4-acfd-4f92-b8a5-4a0c5cfd4c34 status=pass target=api.cloudflare.com:443
2026-08-13T08:21:42Z INF precheck complete hard_fail=false run_id=4dcbe9f4-acfd-4f92-b8a5-4a0c5cfd4c34 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:16:27] Time: Thu Aug 13 04:16:27 PM CST 2026
[16:16:27] User: root (UID: 0)
[16:16:27] === STEP 1: 启动 API (端口 8450) ===
[16:17:06] API 已在运行
[16:17:06] API 状态: OK
[16:17:06] === STEP 2: 安装 cloudflared ===
[16:17:06] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:17:06] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:17:06] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:17:06] === STEP 3: 检查认证方式 ===
[16:17:06] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:17:06] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:17:06] 检查现有 tunnel...
[16:17:08] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax07, 1xlax08, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[16:17:08] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:17:08] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:17:08] 凭证文件存在
[16:17:08] 创建 config.yml...
[16:17:08] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:17:08] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:17:10] DNS 路由结果: 2026-08-13T08:17:10Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:17:10] === STEP 5: 更新 DNS (API) ===
[16:17:10] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:17:11] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:17:12] 设置 SSL 模式为 Full...
SSL: 跳过
[16:17:12] === STEP 6: 启动 Tunnel ===
[16:17:15] 启动 Named Tunnel (cert 模式)...
[16:17:15] 使用 config: /root/.cloudflared/config.yml
[16:17:15] cloudflared PID: 1290472
[16:17:17] Tunnel 连接已建立!
[16:17:17] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T08:17:15Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T08:17:15Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T08:17:15Z INF Generated Connector ID: 220df0e8-3a97-4375-8357-0c61c5001290
2026-08-13T08:17:15Z INF Initial protocol quic
2026-08-13T08:17:15Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T08:17:15Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T08:17:15Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T08:17:15Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T08:17:15Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T08:17:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-13T08:17:16Z INF Registered tunnel connection connIndex=0 connection=acd29fa2-c837-4c43-8680-44b5995e83dd event=0 ip=198.41.192.227 location=lax11 protocol=quic
2026-08-13T08:17:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-13T08:17:17Z INF Registered tunnel connection connIndex=1 connection=2d72926b-8161-4e44-afbe-5ff0e49ac468 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-13T08:17:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
2026-08-13T08:17:17Z INF Registered tunnel connection connIndex=2 connection=244c775f-d313-4d9a-9456-49a0566e5884 event=0 ip=198.41.192.67 location=lax08 protocol=quic
[16:17:17] === STEP 7: 持久化 ===
[16:17:18] systemd 服务已配置
[16:17:18] Cron 保活已设置
[16:17:18] === STEP 8: 验证 ===
[16:17:18] --- API (localhost:8450) ---
 OK
[16:17:18] --- cloudflared 进程 ---
root     1290472  3.3  1.9 1294676 39124 ?       Sl   16:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1290578  0.0  1.3 1292484 27400 ?       Rl   16:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:17:18] --- aishield.tools ---
 OK
[16:17:19] --- DNS CNAME ---
[16:17:20] --- DNS A ---
104.21.81.46
172.67.188.44
[16:17:20] === 部署汇总 ===
[16:17:20] Tunnel Mode: cert
[16:17:20] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:17:20] API: http://localhost:8450
[16:17:20] 域名: https://aishield.tools
[16:17:20] cloudflared: /usr/local/bin/cloudflared
[16:17:20] PID: 1290472
[16:17:20] Config: /root/.cloudflared/config.yml
[16:17:20] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:17:20] 状态: Named Tunnel (cert 模式) 已配置
[16:21:27] API 已在运行
[16:21:27] API 状态: OK
[16:21:27] === STEP 2: 安装 cloudflared ===
[16:21:27] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:21:27] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:21:27] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:21:27] === STEP 3: 检查认证方式 ===
[16:21:27] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:21:27] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:21:27] 检查现有 tunnel...
[16:21:28] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax08, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[16:21:28] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:21:28] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:21:28] 凭证文件存在
[16:21:28] 创建 config.yml...
[16:21:28] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:21:28] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:21:30] DNS 路由结果: 2026-08-13T08:21:30Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:21:30] === STEP 5: 更新 DNS (API) ===
[16:21:30] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:21:31] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:21:32] 设置 SSL 模式为 Full...
SSL: 跳过
[16:21:32] === STEP 6: 启动 Tunnel ===
[16:21:35] 启动 Named Tunnel (cert 模式)...
[16:21:35] 使用 config: /root/.cloudflared/config.yml
[16:21:35] cloudflared PID: 1293677
[16:21:37] Tunnel 连接已建立!
[16:21:37] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T08:21:36Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T08:21:36Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T08:21:36Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T08:21:36Z INF Generated Connector ID: e554e150-e92b-4266-bb69-ddf28cd11b3c
2026-08-13T08:21:36Z INF Initial protocol quic
2026-08-13T08:21:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T08:21:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T08:21:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T08:21:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T08:21:36Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T08:21:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-13T08:21:36Z INF Registered tunnel connection connIndex=0 connection=83ecdb62-e4fb-410c-98cc-c96d814f2954 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-13T08:21:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-13T08:21:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-13T08:21:37Z INF Registered tunnel connection connIndex=2 connection=94607c2f-adab-46f5-a468-fd70a67bbdb2 event=0 ip=198.41.192.77 location=lax08 protocol=quic
[16:21:38] === STEP 7: 持久化 ===
[16:21:38] systemd 服务已配置
[16:21:38] Cron 保活已设置
[16:21:38] === STEP 8: 验证 ===
[16:21:38] --- API (localhost:8450) ---
 OK
[16:21:38] --- cloudflared 进程 ---
root     1293677  3.0  1.9 1293836 38500 ?       Sl   16:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1293804  0.0  1.3 1292484 27208 ?       Rl   16:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:21:38] --- aishield.tools ---
 OK
[16:21:39] --- DNS CNAME ---
[16:21:40] --- DNS A ---
172.67.188.44
104.21.81.46
[16:21:40] === 部署汇总 ===
[16:21:40] Tunnel Mode: cert
[16:21:40] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:21:40] API: http://localhost:8450
[16:21:40] 域名: https://aishield.tools
[16:21:40] cloudflared: /usr/local/bin/cloudflared
[16:21:40] PID: 1293677
[16:21:40] Config: /root/.cloudflared/config.yml
[16:21:40] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:21:40] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-13 16:21:38 CST; 5h 50min ago
   Main PID: 1293798 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 20.5M
        CPU: 35.397s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1293798 /bin/bash /opt/start-tunnel.sh
             └─1293804 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2772386,fd=3))                                                    
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
Time: Thu Aug 13 14:11:49 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786630309.720677, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
