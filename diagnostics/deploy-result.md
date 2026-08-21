=== DIAGNOSTIC ===
Time: Sat Aug 22 05:11:37 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787346698.013917, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      816271  0.1  1.6 1360284 32404 ?       Sl   02:12   0:15 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      816364  0.1  1.5 1294676 32004 ?       Sl   02:12   0:15 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-21T18:12:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.77
2026-08-21T18:12:34Z INF Registered tunnel connection connIndex=1 connection=61ae4d8f-a503-499f-b82c-8a02f620f179 event=0 ip=198.41.192.77 location=sjc01 protocol=quic
2026-08-21T18:12:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-21T18:12:35Z INF Registered tunnel connection connIndex=2 connection=1dbe2fb9-53dd-492f-96bf-f6a8b4a90fb2 event=0 ip=198.41.200.33 location=sjc11 protocol=quic
2026-08-21T18:12:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.67
2026-08-21T18:12:36Z INF Registered tunnel connection connIndex=3 connection=e700422a-b910-4ee0-b427-499b7759b11a event=0 ip=198.41.192.67 location=sjc06 protocol=quic
2026-08-21T18:12:40Z INF +-------------------------------------------------------------------------------------+
2026-08-21T18:12:40Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-21T18:12:40Z INF +-------------------------------------------------------------------------------------+
2026-08-21T18:12:40Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-21T18:12:40Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-21T18:12:40Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-21T18:12:40Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-21T18:12:40Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-21T18:12:40Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-21T18:12:40Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-21T18:12:40Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-21T18:12:40Z INF |                                                                                     |
2026-08-21T18:12:40Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-21T18:12:40Z INF +-------------------------------------------------------------------------------------+
2026-08-21T18:12:40Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=54521214-e134-43dd-b143-f72fc0781dd6 status=pass target=region1.v2.argotunnel.com
2026-08-21T18:12:40Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=54521214-e134-43dd-b143-f72fc0781dd6 status=pass target=region2.v2.argotunnel.com
2026-08-21T18:12:40Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=54521214-e134-43dd-b143-f72fc0781dd6 status=pass target=region1.v2.argotunnel.com
2026-08-21T18:12:40Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=54521214-e134-43dd-b143-f72fc0781dd6 status=pass target=region2.v2.argotunnel.com
2026-08-21T18:12:40Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=54521214-e134-43dd-b143-f72fc0781dd6 status=pass target=region1.v2.argotunnel.com
2026-08-21T18:12:40Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=54521214-e134-43dd-b143-f72fc0781dd6 status=pass target=region2.v2.argotunnel.com
2026-08-21T18:12:40Z INF precheck component="Cloudflare API" details="API is reachable" run_id=54521214-e134-43dd-b143-f72fc0781dd6 status=pass target=api.cloudflare.com:443
2026-08-21T18:12:40Z INF precheck complete hard_fail=false run_id=54521214-e134-43dd-b143-f72fc0781dd6 suggested_protocol=quic
2026-08-21T18:41:38Z ERR  error="stream 13 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-21T18:41:38Z ERR Request failed error="stream 13 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.192.77 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:12:24] Time: Sat Aug 22 02:12:24 AM CST 2026
[02:12:24] User: root (UID: 0)
[02:12:24] === STEP 1: 启动 API (端口 8450) ===
[02:12:25] API 已在运行
[02:12:25] API 状态: OK
[02:12:25] === STEP 2: 安装 cloudflared ===
[02:12:25] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:12:26] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:12:26] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:12:26] === STEP 3: 检查认证方式 ===
[02:12:26] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:12:26] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:12:26] 检查现有 tunnel...
[02:12:26] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xsjc01, 1xsjc05, 2xsjc06, 2xsjc08, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[02:12:26] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:12:26] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:12:26] 凭证文件存在
[02:12:26] 创建 config.yml...
[02:12:26] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:12:26] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:12:28] DNS 路由结果: 2026-08-21T18:12:28Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:12:28] === STEP 5: 更新 DNS (API) ===
[02:12:28] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:12:28] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:12:29] 设置 SSL 模式为 Full...
SSL: 跳过
[02:12:30] === STEP 6: 启动 Tunnel ===
[02:12:33] 启动 Named Tunnel (cert 模式)...
[02:12:33] 使用 config: /root/.cloudflared/config.yml
[02:12:33] cloudflared PID: 816271
[02:12:35] Tunnel 连接已建立!
[02:12:35] --- cloudflared 日志 (最后 15 行) ---
2026-08-21T18:12:33Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-21T18:12:33Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-21T18:12:33Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-21T18:12:33Z INF Generated Connector ID: 5663ca01-7190-4716-b8b2-a664094388ea
2026-08-21T18:12:33Z INF Initial protocol quic
2026-08-21T18:12:33Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-21T18:12:33Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-21T18:12:33Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-21T18:12:33Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-21T18:12:33Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-21T18:12:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-21T18:12:33Z INF Registered tunnel connection connIndex=0 connection=1f737331-1204-48c9-b33d-0e7d36c40f42 event=0 ip=198.41.200.233 location=sjc08 protocol=quic
2026-08-21T18:12:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.77
2026-08-21T18:12:34Z INF Registered tunnel connection connIndex=1 connection=61ae4d8f-a503-499f-b82c-8a02f620f179 event=0 ip=198.41.192.77 location=sjc01 protocol=quic
2026-08-21T18:12:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
[02:12:35] === STEP 7: 持久化 ===
[02:12:35] systemd 服务已配置
[02:12:35] Cron 保活已设置
[02:12:35] === STEP 8: 验证 ===
[02:12:35] --- API (localhost:8450) ---
 OK
[02:12:35] --- cloudflared 进程 ---
root      816271  5.0  1.9 1360284 38760 ?       Sl   02:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      816364  0.0  1.3 1292484 27316 ?       Rl   02:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:12:35] --- aishield.tools ---
 OK
[02:12:37] --- DNS CNAME ---
[02:12:37] --- DNS A ---
104.21.81.46
172.67.188.44
[02:12:37] === 部署汇总 ===
[02:12:37] Tunnel Mode: cert
[02:12:37] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:12:37] API: http://localhost:8450
[02:12:37] 域名: https://aishield.tools
[02:12:37] cloudflared: /usr/local/bin/cloudflared
[02:12:37] PID: 816271
[02:12:37] Config: /root/.cloudflared/config.yml
[02:12:37] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:12:37] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-22 02:12:35 CST; 2h 59min ago
   Main PID: 816363 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.2M
        CPU: 15.220s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─816363 /bin/bash /opt/start-tunnel.sh
             └─816364 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 21 21:11:38 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787346698.6554556, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
