=== DIAGNOSTIC ===
Time: Fri Aug 28 03:09:38 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787900978.2650893, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2684311  0.1  1.5 1360284 30448 ?       Sl   12:47   0:15 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2684462  0.1  1.5 1294676 32044 ?       Sl   12:47   0:16 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T04:47:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-28T04:47:18Z INF Registered tunnel connection connIndex=0 connection=155aeedf-b216-40fd-aee7-b43489f4f4ad event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-08-28T04:47:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-28T04:47:19Z INF Registered tunnel connection connIndex=1 connection=71e1449a-5094-4656-9ae6-d164daa7da2c event=0 ip=198.41.200.43 location=sjc08 protocol=quic
2026-08-28T04:47:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-28T04:47:19Z INF Registered tunnel connection connIndex=2 connection=7fa619e3-62f6-4f9c-8895-e887c120ec5c event=0 ip=198.41.192.227 location=lax05 protocol=quic
2026-08-28T04:47:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.23
2026-08-28T04:47:21Z INF Registered tunnel connection connIndex=3 connection=3e88ab7a-570f-4420-bc7d-eda2b53a5bf1 event=0 ip=198.41.200.23 location=sjc05 protocol=quic
2026-08-28T04:47:25Z INF +-------------------------------------------------------------------------------------+
2026-08-28T04:47:25Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-28T04:47:25Z INF +-------------------------------------------------------------------------------------+
2026-08-28T04:47:25Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-28T04:47:25Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T04:47:25Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T04:47:25Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T04:47:25Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T04:47:25Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T04:47:25Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T04:47:25Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-28T04:47:25Z INF |                                                                                     |
2026-08-28T04:47:25Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-28T04:47:25Z INF +-------------------------------------------------------------------------------------+
2026-08-28T04:47:25Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e4404a99-5564-4355-a12c-a9aec8786b16 status=pass target=region1.v2.argotunnel.com
2026-08-28T04:47:25Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e4404a99-5564-4355-a12c-a9aec8786b16 status=pass target=region2.v2.argotunnel.com
2026-08-28T04:47:25Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e4404a99-5564-4355-a12c-a9aec8786b16 status=pass target=region1.v2.argotunnel.com
2026-08-28T04:47:25Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e4404a99-5564-4355-a12c-a9aec8786b16 status=pass target=region2.v2.argotunnel.com
2026-08-28T04:47:25Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e4404a99-5564-4355-a12c-a9aec8786b16 status=pass target=region1.v2.argotunnel.com
2026-08-28T04:47:25Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e4404a99-5564-4355-a12c-a9aec8786b16 status=pass target=region2.v2.argotunnel.com
2026-08-28T04:47:25Z INF precheck component="Cloudflare API" details="API is reachable" run_id=e4404a99-5564-4355-a12c-a9aec8786b16 status=pass target=api.cloudflare.com:443
2026-08-28T04:47:25Z INF precheck complete hard_fail=false run_id=e4404a99-5564-4355-a12c-a9aec8786b16 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:44:56] Time: Fri Aug 28 12:44:56 PM CST 2026
[12:44:56] User: root (UID: 0)
[12:44:56] === STEP 1: 启动 API (端口 8450) ===
[12:47:07] API 已在运行
[12:47:07] API 状态: OK
[12:47:07] === STEP 2: 安装 cloudflared ===
[12:47:07] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:47:07] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:47:07] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:47:07] === STEP 3: 检查认证方式 ===
[12:47:07] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:47:07] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:47:07] 检查现有 tunnel...
[12:47:07] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax08, 1xlax11, 1xlax12, 3xsjc05, 1xsjc07 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
[12:47:07] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:47:07] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:47:07] 凭证文件存在
[12:47:07] 创建 config.yml...
[12:47:07] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:47:07] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:47:11] DNS 路由结果: 2026-08-28T04:47:11Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:47:11] === STEP 5: 更新 DNS (API) ===
[12:47:11] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:47:12] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[12:47:13] 设置 SSL 模式为 Full...
SSL: 跳过
[12:47:14] === STEP 6: 启动 Tunnel ===
[12:47:17] 启动 Named Tunnel (cert 模式)...
[12:47:17] 使用 config: /root/.cloudflared/config.yml
[12:47:17] cloudflared PID: 2684311
[12:47:19] Tunnel 连接已建立!
[12:47:19] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T04:47:17Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-28T04:47:17Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T04:47:17Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T04:47:17Z INF Generated Connector ID: 4d819de3-2cad-415b-bf19-5acc6350cd02
2026-08-28T04:47:17Z INF Initial protocol quic
2026-08-28T04:47:17Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T04:47:17Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T04:47:18Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T04:47:18Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T04:47:18Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T04:47:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-28T04:47:18Z INF Registered tunnel connection connIndex=0 connection=155aeedf-b216-40fd-aee7-b43489f4f4ad event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-08-28T04:47:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-28T04:47:19Z INF Registered tunnel connection connIndex=1 connection=71e1449a-5094-4656-9ae6-d164daa7da2c event=0 ip=198.41.200.43 location=sjc08 protocol=quic
2026-08-28T04:47:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
[12:47:19] === STEP 7: 持久化 ===
[12:47:20] systemd 服务已配置
[12:47:20] Cron 保活已设置
[12:47:20] === STEP 8: 验证 ===
[12:47:20] --- API (localhost:8450) ---
 OK
[12:47:20] --- cloudflared 进程 ---
root     2684311  3.3  1.9 1360284 38824 ?       Sl   12:47   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2684462  0.0  1.3 1292484 27772 ?       Sl   12:47   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:47:20] --- aishield.tools ---
 OK
[12:47:22] --- DNS CNAME ---
[12:47:22] --- DNS A ---
172.67.188.44
104.21.81.46
[12:47:22] === 部署汇总 ===
[12:47:22] Tunnel Mode: cert
[12:47:22] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:47:22] API: http://localhost:8450
[12:47:22] 域名: https://aishield.tools
[12:47:22] cloudflared: /usr/local/bin/cloudflared
[12:47:22] PID: 2684311
[12:47:22] Config: /root/.cloudflared/config.yml
[12:47:22] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:47:22] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 12:47:20 CST; 2h 22min ago
   Main PID: 2684461 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 20.1M
        CPU: 16.337s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2684461 /bin/bash /opt/start-tunnel.sh
             └─2684462 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 28 07:09:38 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787900978.8316393, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
