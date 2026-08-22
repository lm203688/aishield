=== DIAGNOSTIC ===
Time: Sat Aug 22 10:06:51 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787364412.1027632, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1118138  0.1  1.6 1294676 33700 ?       Sl   09:54   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1118243  0.1  1.7 1294676 34708 ?       Sl   09:54   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-22T01:54:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-22T01:54:15Z INF Registered tunnel connection connIndex=0 connection=90c33f70-60e2-458a-8d18-7c3f313136e4 event=0 ip=198.41.200.233 location=sjc11 protocol=quic
2026-08-22T01:54:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-22T01:54:15Z INF Registered tunnel connection connIndex=1 connection=1d70cc10-d1b0-445d-9664-314b637b3fa2 event=0 ip=198.41.192.167 location=sjc01 protocol=quic
2026-08-22T01:54:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-22T01:54:16Z INF Registered tunnel connection connIndex=2 connection=62a1db81-9be7-4a47-8273-a32da8c9fa37 event=0 ip=198.41.200.23 location=sjc10 protocol=quic
2026-08-22T01:54:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.77
2026-08-22T01:54:17Z INF Registered tunnel connection connIndex=3 connection=d7f03c58-c74d-4d6f-9853-7e0e0a0c66bf event=0 ip=198.41.192.77 location=sjc01 protocol=quic
2026-08-22T01:54:21Z INF +-------------------------------------------------------------------------------------+
2026-08-22T01:54:21Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-22T01:54:21Z INF +-------------------------------------------------------------------------------------+
2026-08-22T01:54:21Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-22T01:54:21Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-22T01:54:21Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-22T01:54:21Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-22T01:54:21Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-22T01:54:21Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-22T01:54:21Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-22T01:54:21Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-22T01:54:21Z INF |                                                                                     |
2026-08-22T01:54:21Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-22T01:54:21Z INF +-------------------------------------------------------------------------------------+
2026-08-22T01:54:21Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=3c730ea5-9bf4-45cd-9ed4-42bcd72ddcc4 status=pass target=region1.v2.argotunnel.com
2026-08-22T01:54:21Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=3c730ea5-9bf4-45cd-9ed4-42bcd72ddcc4 status=pass target=region2.v2.argotunnel.com
2026-08-22T01:54:21Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=3c730ea5-9bf4-45cd-9ed4-42bcd72ddcc4 status=pass target=region1.v2.argotunnel.com
2026-08-22T01:54:21Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=3c730ea5-9bf4-45cd-9ed4-42bcd72ddcc4 status=pass target=region2.v2.argotunnel.com
2026-08-22T01:54:21Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=3c730ea5-9bf4-45cd-9ed4-42bcd72ddcc4 status=pass target=region1.v2.argotunnel.com
2026-08-22T01:54:21Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=3c730ea5-9bf4-45cd-9ed4-42bcd72ddcc4 status=pass target=region2.v2.argotunnel.com
2026-08-22T01:54:21Z INF precheck component="Cloudflare API" details="API is reachable" run_id=3c730ea5-9bf4-45cd-9ed4-42bcd72ddcc4 status=pass target=api.cloudflare.com:443
2026-08-22T01:54:21Z INF precheck complete hard_fail=false run_id=3c730ea5-9bf4-45cd-9ed4-42bcd72ddcc4 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[09:52:35] Time: Sat Aug 22 09:52:35 AM CST 2026
[09:52:35] User: root (UID: 0)
[09:52:35] === STEP 1: 启动 API (端口 8450) ===
[09:54:06] API 已在运行
[09:54:06] API 状态: OK
[09:54:06] === STEP 2: 安装 cloudflared ===
[09:54:06] cloudflared 安装路径: /usr/local/bin/cloudflared
[09:54:06] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:54:06] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:54:06] === STEP 3: 检查认证方式 ===
[09:54:06] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:54:06] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:54:06] 检查现有 tunnel...
[09:54:08] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xsjc01, 1xsjc05, 1xsjc06, 2xsjc07, 1xsjc08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-22T01:54:08Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[09:54:08] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:54:08] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[09:54:08] 凭证文件存在
[09:54:08] 创建 config.yml...
[09:54:08] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[09:54:08] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:54:09] DNS 路由结果: 2026-08-22T01:54:09Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[09:54:09] === STEP 5: 更新 DNS (API) ===
[09:54:09] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:54:10] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[09:54:11] 设置 SSL 模式为 Full...
SSL: 跳过
[09:54:12] === STEP 6: 启动 Tunnel ===
[09:54:15] 启动 Named Tunnel (cert 模式)...
[09:54:15] 使用 config: /root/.cloudflared/config.yml
[09:54:15] cloudflared PID: 1118138
[09:54:17] Tunnel 连接已建立!
[09:54:17] --- cloudflared 日志 (最后 15 行) ---
2026-08-22T01:54:15Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-22T01:54:15Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-22T01:54:15Z INF Generated Connector ID: 42f65ad1-8d4f-44b6-bced-c4b2554430a4
2026-08-22T01:54:15Z INF Initial protocol quic
2026-08-22T01:54:15Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-22T01:54:15Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-22T01:54:15Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-22T01:54:15Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-22T01:54:15Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-22T01:54:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-22T01:54:15Z INF Registered tunnel connection connIndex=0 connection=90c33f70-60e2-458a-8d18-7c3f313136e4 event=0 ip=198.41.200.233 location=sjc11 protocol=quic
2026-08-22T01:54:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-22T01:54:15Z INF Registered tunnel connection connIndex=1 connection=1d70cc10-d1b0-445d-9664-314b637b3fa2 event=0 ip=198.41.192.167 location=sjc01 protocol=quic
2026-08-22T01:54:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-22T01:54:16Z INF Registered tunnel connection connIndex=2 connection=62a1db81-9be7-4a47-8273-a32da8c9fa37 event=0 ip=198.41.200.23 location=sjc10 protocol=quic
[09:54:17] === STEP 7: 持久化 ===
[09:54:17] systemd 服务已配置
[09:54:17] Cron 保活已设置
[09:54:17] === STEP 8: 验证 ===
[09:54:17] --- API (localhost:8450) ---
 OK
[09:54:17] --- cloudflared 进程 ---
root     1118138  6.0  1.9 1294420 39192 ?       Sl   09:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1118243  0.0  1.3 1292740 27260 ?       Rl   09:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[09:54:17] --- aishield.tools ---
 OK
[09:54:19] --- DNS CNAME ---
[09:54:19] --- DNS A ---
172.67.188.44
104.21.81.46
[09:54:19] === 部署汇总 ===
[09:54:19] Tunnel Mode: cert
[09:54:19] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:54:19] API: http://localhost:8450
[09:54:19] 域名: https://aishield.tools
[09:54:19] cloudflared: /usr/local/bin/cloudflared
[09:54:19] PID: 1118138
[09:54:19] Config: /root/.cloudflared/config.yml
[09:54:19] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:54:19] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-22 09:54:17 CST; 12min ago
   Main PID: 1118235 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.6M
        CPU: 1.369s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1118235 /bin/bash /opt/start-tunnel.sh
             └─1118243 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sat Aug 22 02:06:52 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787364412.9945462, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
