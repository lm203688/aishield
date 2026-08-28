=== DIAGNOSTIC ===
Time: Fri Aug 28 05:23:57 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787909037.62421, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2867334  1.0  1.8 1294676 38144 ?       Sl   17:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2867463  1.1  1.8 1294676 38036 ?       Sl   17:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T09:23:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-28T09:23:44Z INF Registered tunnel connection connIndex=0 connection=9ab1fc89-0ce7-4435-8e8d-507a92b7c827 event=0 ip=198.41.200.233 location=sjc10 protocol=quic
2026-08-28T09:23:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-28T09:23:45Z INF Registered tunnel connection connIndex=1 connection=44636c5d-ac7c-4e16-a3b6-215c4a6449d0 event=0 ip=198.41.192.107 location=lax11 protocol=quic
2026-08-28T09:23:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-28T09:23:46Z INF Registered tunnel connection connIndex=2 connection=4aaf8852-2366-4363-964c-db3f2f3c0e0e event=0 ip=198.41.200.33 location=sjc08 protocol=quic
2026-08-28T09:23:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.227
2026-08-28T09:23:47Z INF Registered tunnel connection connIndex=3 connection=b6db8f42-3ee4-446e-9035-1889c639f287 event=0 ip=198.41.192.227 location=lax08 protocol=quic
2026-08-28T09:23:52Z INF +-------------------------------------------------------------------------------------+
2026-08-28T09:23:52Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-28T09:23:52Z INF +-------------------------------------------------------------------------------------+
2026-08-28T09:23:52Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-28T09:23:52Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T09:23:52Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T09:23:52Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T09:23:52Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T09:23:52Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T09:23:52Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T09:23:52Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-28T09:23:52Z INF |                                                                                     |
2026-08-28T09:23:52Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-28T09:23:52Z INF +-------------------------------------------------------------------------------------+
2026-08-28T09:23:52Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=564cc790-9396-401f-a0e6-0083a31742ff status=pass target=region1.v2.argotunnel.com
2026-08-28T09:23:52Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=564cc790-9396-401f-a0e6-0083a31742ff status=pass target=region2.v2.argotunnel.com
2026-08-28T09:23:52Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=564cc790-9396-401f-a0e6-0083a31742ff status=pass target=region1.v2.argotunnel.com
2026-08-28T09:23:52Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=564cc790-9396-401f-a0e6-0083a31742ff status=pass target=region2.v2.argotunnel.com
2026-08-28T09:23:52Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=564cc790-9396-401f-a0e6-0083a31742ff status=pass target=region1.v2.argotunnel.com
2026-08-28T09:23:52Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=564cc790-9396-401f-a0e6-0083a31742ff status=pass target=region2.v2.argotunnel.com
2026-08-28T09:23:52Z INF precheck component="Cloudflare API" details="API is reachable" run_id=564cc790-9396-401f-a0e6-0083a31742ff status=pass target=api.cloudflare.com:443
2026-08-28T09:23:52Z INF precheck complete hard_fail=false run_id=564cc790-9396-401f-a0e6-0083a31742ff suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[17:23:33] Time: Fri Aug 28 05:23:33 PM CST 2026
[17:23:33] User: root (UID: 0)
[17:23:33] === STEP 1: 启动 API (端口 8450) ===
[17:23:35] API 已在运行
[17:23:35] API 状态: OK
[17:23:35] === STEP 2: 安装 cloudflared ===
[17:23:35] cloudflared 安装路径: /usr/local/bin/cloudflared
[17:23:35] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:23:35] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:23:35] === STEP 3: 检查认证方式 ===
[17:23:35] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[17:23:35] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[17:23:35] 检查现有 tunnel...
[17:23:36] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax08, 2xlax12, 2xsjc05, 2xsjc08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[17:23:36] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:23:36] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[17:23:36] 凭证文件存在
[17:23:36] 创建 config.yml...
[17:23:36] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[17:23:36] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:23:38] DNS 路由结果: 2026-08-28T09:23:38Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:23:38] === STEP 5: 更新 DNS (API) ===
[17:23:38] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:23:39] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[17:23:39] 设置 SSL 模式为 Full...
SSL: 跳过
[17:23:41] === STEP 6: 启动 Tunnel ===
[17:23:44] 启动 Named Tunnel (cert 模式)...
[17:23:44] 使用 config: /root/.cloudflared/config.yml
[17:23:44] cloudflared PID: 2867334
[17:23:46] Tunnel 连接已建立!
[17:23:46] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T09:23:44Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-28T09:23:44Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T09:23:44Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T09:23:44Z INF Generated Connector ID: 9a062db4-dacc-4f22-96e4-520aca9a76c1
2026-08-28T09:23:44Z INF Initial protocol quic
2026-08-28T09:23:44Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T09:23:44Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T09:23:44Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T09:23:44Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T09:23:44Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T09:23:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-28T09:23:44Z INF Registered tunnel connection connIndex=0 connection=9ab1fc89-0ce7-4435-8e8d-507a92b7c827 event=0 ip=198.41.200.233 location=sjc10 protocol=quic
2026-08-28T09:23:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-28T09:23:45Z INF Registered tunnel connection connIndex=1 connection=44636c5d-ac7c-4e16-a3b6-215c4a6449d0 event=0 ip=198.41.192.107 location=lax11 protocol=quic
2026-08-28T09:23:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
[17:23:46] === STEP 7: 持久化 ===
[17:23:46] systemd 服务已配置
[17:23:46] Cron 保活已设置
[17:23:46] === STEP 8: 验证 ===
[17:23:46] --- API (localhost:8450) ---
 OK
[17:23:47] --- cloudflared 进程 ---
root     2867334  3.6  1.9 1294676 39380 ?       Sl   17:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2867463  2.0  1.3 1292484 27548 ?       Sl   17:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[17:23:47] --- aishield.tools ---
 OK
[17:23:48] --- DNS CNAME ---
[17:23:49] --- DNS A ---
104.21.81.46
172.67.188.44
[17:23:49] === 部署汇总 ===
[17:23:49] Tunnel Mode: cert
[17:23:49] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:23:49] API: http://localhost:8450
[17:23:49] 域名: https://aishield.tools
[17:23:49] cloudflared: /usr/local/bin/cloudflared
[17:23:49] PID: 2867334
[17:23:49] Config: /root/.cloudflared/config.yml
[17:23:49] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:23:49] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 17:23:46 CST; 10s ago
   Main PID: 2867459 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.3M
        CPU: 145ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2867459 /bin/bash /opt/start-tunnel.sh
             └─2867463 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 28 09:23:58 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787909038.4227407, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
