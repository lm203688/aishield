=== DIAGNOSTIC ===
Time: Sun Aug 16 08:37:08 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786840628.0410664, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3815621  1.0  1.9 1294676 40108 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3815645  1.0  1.9 1294420 39028 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3815835  1.5  1.9 1360284 39164 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-16T00:36:57Z INF Registered tunnel connection connIndex=0 connection=c4bd30e0-e7df-4162-93d5-943b320659ef event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-08-16T00:36:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-16T00:36:58Z INF Registered tunnel connection connIndex=1 connection=fb105f94-ba68-458c-9972-1f97e3437f11 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-16T00:36:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-16T00:36:59Z INF Registered tunnel connection connIndex=2 connection=017be372-4440-40f0-b2ff-ee9128936b50 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-16T00:36:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.227
2026-08-16T00:37:00Z INF Registered tunnel connection connIndex=3 connection=68678475-a71a-481a-a228-37c55746278a event=0 ip=198.41.192.227 location=lax10 protocol=quic
2026-08-16T00:37:03Z INF +-------------------------------------------------------------------------------------+
2026-08-16T00:37:03Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-16T00:37:03Z INF +-------------------------------------------------------------------------------------+
2026-08-16T00:37:03Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-16T00:37:03Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-16T00:37:03Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-16T00:37:03Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-16T00:37:03Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-16T00:37:03Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-16T00:37:03Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-16T00:37:03Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-16T00:37:03Z INF |                                                                                     |
2026-08-16T00:37:03Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-16T00:37:03Z INF +-------------------------------------------------------------------------------------+
2026-08-16T00:37:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e5250b8f-be9d-4f01-8a8c-ad821a669890 status=pass target=region1.v2.argotunnel.com
2026-08-16T00:37:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e5250b8f-be9d-4f01-8a8c-ad821a669890 status=pass target=region2.v2.argotunnel.com
2026-08-16T00:37:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e5250b8f-be9d-4f01-8a8c-ad821a669890 status=pass target=region1.v2.argotunnel.com
2026-08-16T00:37:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e5250b8f-be9d-4f01-8a8c-ad821a669890 status=pass target=region2.v2.argotunnel.com
2026-08-16T00:37:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e5250b8f-be9d-4f01-8a8c-ad821a669890 status=pass target=region1.v2.argotunnel.com
2026-08-16T00:37:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e5250b8f-be9d-4f01-8a8c-ad821a669890 status=pass target=region2.v2.argotunnel.com
2026-08-16T00:37:03Z INF precheck component="Cloudflare API" details="API is reachable" run_id=e5250b8f-be9d-4f01-8a8c-ad821a669890 status=pass target=api.cloudflare.com:443
2026-08-16T00:37:03Z INF precheck complete hard_fail=false run_id=e5250b8f-be9d-4f01-8a8c-ad821a669890 suggested_protocol=quic
c
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:36:47] Time: Sun Aug 16 08:36:47 AM CST 2026
[08:36:47] User: root (UID: 0)
[08:36:47] === STEP 1: 启动 API (端口 8450) ===
[08:36:49] API 已在运行
[08:36:49] API 状态: OK
[08:36:49] === STEP 2: 安装 cloudflared ===
[08:36:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:36:49] API 已在运行
[08:36:49] API 状态: OK
[08:36:49] === STEP 2: 安装 cloudflared ===
[08:36:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:36:49] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:49] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:49] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:49] === STEP 3: 检查认证方式 ===
[08:36:49] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:49] === STEP 3: 检查认证方式 ===
[08:36:49] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:36:49] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:36:49] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:36:49] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:36:49] 检查现有 tunnel...
[08:36:49] 检查现有 tunnel...
[08:36:50] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax07, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-16T00:36:50Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:36:50] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax07, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-16T00:36:50Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:36:50] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:50] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:36:50] 凭证文件存在
[08:36:50] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:50] 创建 config.yml...
[08:36:50] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:36:50] 凭证文件存在
[08:36:50] 创建 config.yml...
[08:36:50] config.yml 已创建:
[08:36:50] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:50] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:36:50] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:51] DNS 路由结果: 2026-08-16T00:36:51Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:51] === STEP 5: 更新 DNS (API) ===
[08:36:51] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:52] DNS 路由结果: 2026-08-16T00:36:52Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:52] === STEP 5: 更新 DNS (API) ===
[08:36:52] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:52] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[08:36:52] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:36:53] 设置 SSL 模式为 Full...
DNS 更新: OK
[08:36:53] 设置 SSL 模式为 Full...
SSL: 跳过
[08:36:53] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[08:36:54] === STEP 6: 启动 Tunnel ===
[08:36:56] 启动 Named Tunnel (cert 模式)...
[08:36:56] 使用 config: /root/.cloudflared/config.yml
[08:36:56] cloudflared PID: 3815621
[08:36:57] 启动 Named Tunnel (cert 模式)...
[08:36:57] 使用 config: /root/.cloudflared/config.yml
[08:36:57] cloudflared PID: 3815645
[08:36:58] Tunnel 连接已建立!
[08:36:58] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T00:36:57Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-16T00:36:57Z INF Generated Connector ID: ad5b7426-5a4b-4ab2-addd-ac558bd0a57c
2026-08-16T00:36:57Z INF Initial protocol quic
2026-08-16T00:36:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T00:36:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T00:36:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T00:36:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T00:36:57Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-16T00:36:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-16T00:36:57Z INF Registered tunnel connection connIndex=0 connection=c4bd30e0-e7df-4162-93d5-943b320659ef event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-08-16T00:36:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-16T00:36:58Z INF Registered tunnel connection connIndex=1 connection=fb105f94-ba68-458c-9972-1f97e3437f11 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-16T00:36:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23

2026-08-16T00:36:58Z INF Registered tunnel connection connIndex=2 connection=0a28082d-714f-4225-a216-7996c6f28342 event=0 ip=198.41.192.227 location=lax07 protocol=quic
[08:36:58] === STEP 7: 持久化 ===
[08:36:59] Tunnel 连接已建立!
[08:36:59] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T00:36:57Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-16T00:36:57Z INF Generated Connector ID: ad5b7426-5a4b-4ab2-addd-ac558bd0a57c
2026-08-16T00:36:57Z INF Initial protocol quic
2026-08-16T00:36:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T00:36:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T00:36:57Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-16T00:36:57Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-16T00:36:57Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-16T00:36:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-16T00:36:57Z INF Registered tunnel connection connIndex=0 connection=c4bd30e0-e7df-4162-93d5-943b320659ef event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-08-16T00:36:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-16T00:36:58Z INF Registered tunnel connection connIndex=1 connection=fb105f94-ba68-458c-9972-1f97e3437f11 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-16T00:36:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23

2026-08-16T00:36:58Z INF Registered tunnel connection connIndex=2 connection=0a28082d-714f-4225-a216-7996c6f28342 event=0 ip=198.41.192.227 location=lax07 protocol=quic
[08:36:59] === STEP 7: 持久化 ===
[08:37:00] systemd 服务已配置
[08:37:00] systemd 服务已配置
[08:37:00] Cron 保活已设置
[08:37:00] Cron 保活已设置
[08:37:00] === STEP 8: 验证 ===
[08:37:00] === STEP 8: 验证 ===
[08:37:00] --- API (localhost:8450) ---
[08:37:00] --- API (localhost:8450) ---
 OK
 OK
[08:37:00] --- cloudflared 进程 ---
[08:37:00] --- cloudflared 进程 ---
root     3815621  2.2  1.9 1294100 38880 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3815645  3.0  1.9 1294420 38764 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3815835  0.0  1.3 1358092 27132 ?       Rl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3815621  2.2  1.9 1294100 38880 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3815645  3.0  1.9 1294420 38764 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3815835  0.0  1.3 1358092 27132 ?       Rl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:37:00] --- aishield.tools ---
[08:37:00] --- aishield.tools ---
 OK
[08:37:01] --- DNS CNAME ---
 OK
[08:37:01] --- DNS CNAME ---
[08:37:01] --- DNS A ---
[08:37:01] --- DNS A ---
172.67.188.44
104.21.81.46
[08:37:01] === 部署汇总 ===
[08:37:01] Tunnel Mode: cert
172.67.188.44
104.21.81.46
[08:37:01] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:37:01] === 部署汇总 ===
[08:37:01] API: http://localhost:8450
[08:37:01] 域名: https://aishield.tools
[08:37:01] Tunnel Mode: cert
[08:37:01] cloudflared: /usr/local/bin/cloudflared
[08:37:01] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:37:01] PID: 3815645
[08:37:01] API: http://localhost:8450
[08:37:01] Config: /root/.cloudflared/config.yml
[08:37:01] 域名: https://aishield.tools
[08:37:01] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:37:01] cloudflared: /usr/local/bin/cloudflared
[08:37:01] 状态: Named Tunnel (cert 模式) 已配置
[08:37:01] PID: 3815621
[08:37:01] Config: /root/.cloudflared/config.yml
[08:37:01] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:37:01] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-16 08:37:00 CST; 7s ago
   Main PID: 3815821 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.4M
        CPU: 132ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3815821 /bin/bash /opt/start-tunnel.sh
             └─3815835 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sun Aug 16 00:37:08 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786840628.8205738, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
