=== DIAGNOSTIC ===
Time: Fri Aug 28 11:29:01 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787930941.7256374, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3108478  0.9  1.9 1294676 39916 ?       Sl   23:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3108591  1.1  2.0 1294676 40456 ?       Sl   23:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T15:28:46Z INF Registered tunnel connection connIndex=0 connection=e383cf22-1732-499c-966b-f2699520a73c event=0 ip=198.41.192.167 location=lax11 protocol=quic
2026-08-28T15:28:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-08-28T15:28:47Z INF Registered tunnel connection connIndex=1 connection=52b1d253-7c2a-471d-8dfe-162dfb7cca43 event=0 ip=198.41.200.53 location=sjc08 protocol=quic
2026-08-28T15:28:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-28T15:28:48Z INF Registered tunnel connection connIndex=2 connection=fc58e98d-2097-476a-805a-d9eefa3dc188 event=0 ip=198.41.192.77 location=lax12 protocol=quic
2026-08-28T15:28:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-28T15:28:49Z INF Registered tunnel connection connIndex=3 connection=4d1b156d-ce49-4f49-a4c0-86a5768b3b9e event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-28T15:28:56Z INF +-----------------------------------------------------------------------------------------------+
2026-08-28T15:28:56Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-28T15:28:56Z INF +-----------------------------------------------------------------------------------------------+
2026-08-28T15:28:56Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-28T15:28:56Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-28T15:28:56Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-28T15:28:56Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-28T15:28:56Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-28T15:28:56Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-28T15:28:56Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-28T15:28:56Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-28T15:28:56Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-28T15:28:56Z INF |                                                                                               |
2026-08-28T15:28:56Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-28T15:28:56Z INF +-----------------------------------------------------------------------------------------------+
2026-08-28T15:28:56Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=a2c70e71-b711-4e26-9d57-b5d99b3fd5fa status=pass target=region1.v2.argotunnel.com
2026-08-28T15:28:56Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=a2c70e71-b711-4e26-9d57-b5d99b3fd5fa status=pass target=region2.v2.argotunnel.com
2026-08-28T15:28:56Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=a2c70e71-b711-4e26-9d57-b5d99b3fd5fa status=pass target=region1.v2.argotunnel.com
2026-08-28T15:28:56Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=a2c70e71-b711-4e26-9d57-b5d99b3fd5fa status=fail target=region2.v2.argotunnel.com
2026-08-28T15:28:56Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=a2c70e71-b711-4e26-9d57-b5d99b3fd5fa status=pass target=region1.v2.argotunnel.com
2026-08-28T15:28:56Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=a2c70e71-b711-4e26-9d57-b5d99b3fd5fa status=pass target=region2.v2.argotunnel.com
2026-08-28T15:28:56Z INF precheck component="Cloudflare API" details="API is reachable" run_id=a2c70e71-b711-4e26-9d57-b5d99b3fd5fa status=pass target=api.cloudflare.com:443
2026-08-28T15:28:56Z INF precheck complete hard_fail=false run_id=a2c70e71-b711-4e26-9d57-b5d99b3fd5fa suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:28:25] Time: Fri Aug 28 11:28:25 PM CST 2026
[23:28:25] User: root (UID: 0)
[23:28:25] === STEP 1: 启动 API (端口 8450) ===
[23:28:28] API 已在运行
[23:28:28] API 状态: OK
[23:28:28] === STEP 2: 安装 cloudflared ===
[23:28:28] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:28:28] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:28:28] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:28:28] === STEP 3: 检查认证方式 ===
[23:28:28] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:28:28] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:28:28] 检查现有 tunnel...
[23:28:30] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                   
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax07, 1xlax08, 1xlax11, 1xlax12, 1xsjc07, 2xsjc08, 1xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                               
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                               
[23:28:30] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:28:30] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:28:30] 凭证文件存在
[23:28:30] 创建 config.yml...
[23:28:30] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:28:30] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:28:40] DNS 路由结果: 2026-08-28T15:28:40Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:28:40] === STEP 5: 更新 DNS (API) ===
[23:28:40] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:28:41] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[23:28:42] 设置 SSL 模式为 Full...
SSL: 跳过
[23:28:42] === STEP 6: 启动 Tunnel ===
[23:28:45] 启动 Named Tunnel (cert 模式)...
[23:28:45] 使用 config: /root/.cloudflared/config.yml
[23:28:45] cloudflared PID: 3108478
[23:28:47] Tunnel 连接已建立!
[23:28:47] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T15:28:45Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-28T15:28:45Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T15:28:45Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T15:28:45Z INF Generated Connector ID: bccc0981-6e77-49c6-a0bf-0384ae1ca3e5
2026-08-28T15:28:45Z INF Initial protocol quic
2026-08-28T15:28:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:28:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:28:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:28:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:28:46Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T15:28:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-28T15:28:46Z INF Registered tunnel connection connIndex=0 connection=e383cf22-1732-499c-966b-f2699520a73c event=0 ip=198.41.192.167 location=lax11 protocol=quic
2026-08-28T15:28:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-08-28T15:28:47Z INF Registered tunnel connection connIndex=1 connection=52b1d253-7c2a-471d-8dfe-162dfb7cca43 event=0 ip=198.41.200.53 location=sjc08 protocol=quic
2026-08-28T15:28:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
[23:28:47] === STEP 7: 持久化 ===
[23:28:48] systemd 服务已配置
[23:28:48] Cron 保活已设置
[23:28:48] === STEP 8: 验证 ===
[23:28:48] --- API (localhost:8450) ---
 OK
[23:28:48] --- cloudflared 进程 ---
root     3108478  4.0  1.9 1294676 39340 ?       Sl   23:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3108591  0.0  1.3 1292484 27324 ?       Rl   23:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[23:28:48] --- aishield.tools ---
 OK
[23:28:50] --- DNS CNAME ---
[23:28:50] --- DNS A ---
104.21.81.46
172.67.188.44
[23:28:50] === 部署汇总 ===
[23:28:50] Tunnel Mode: cert
[23:28:50] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:28:50] API: http://localhost:8450
[23:28:50] 域名: https://aishield.tools
[23:28:50] cloudflared: /usr/local/bin/cloudflared
[23:28:50] PID: 3108478
[23:28:50] Config: /root/.cloudflared/config.yml
[23:28:50] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:28:50] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 23:28:48 CST; 13s ago
   Main PID: 3108583 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.4M
        CPU: 154ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3108583 /bin/bash /opt/start-tunnel.sh
             └─3108591 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 28 15:29:02 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787930942.7465997, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
