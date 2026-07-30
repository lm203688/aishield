=== DIAGNOSTIC ===
Time: Fri Jul 31 07:15:03 AM CST 2026
=== USER ===
root
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785453303.3880286, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      406253  0.4  1.9 1294676 39196 ?       Sl   07:14   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
root      406502  1.5  1.9 1294420 38844 ?       Sl   07:14   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
=== CLOUDFLARED LOG (last 30 lines) ===
2026-07-30T23:14:45Z INF Initial protocol quic
2026-07-30T23:14:45Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T23:14:45Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T23:14:45Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T23:14:45Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T23:14:45Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-07-30T23:14:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-07-30T23:14:45Z INF Registered tunnel connection connIndex=0 connection=c537264a-7da5-46db-9701-28f42425ecbf event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-07-30T23:14:51Z INF +-------------------------------------------------------------------------------------+
2026-07-30T23:14:51Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-07-30T23:14:51Z INF +-------------------------------------------------------------------------------------+
2026-07-30T23:14:51Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-07-30T23:14:51Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-07-30T23:14:51Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-07-30T23:14:51Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-07-30T23:14:51Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-07-30T23:14:51Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-07-30T23:14:51Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-07-30T23:14:51Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-07-30T23:14:51Z INF |                                                                                     |
2026-07-30T23:14:51Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-07-30T23:14:51Z INF +-------------------------------------------------------------------------------------+
2026-07-30T23:14:51Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=99b97377-f0f9-4577-a018-6777cf5bdb85 status=pass target=region1.v2.argotunnel.com
2026-07-30T23:14:51Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=99b97377-f0f9-4577-a018-6777cf5bdb85 status=pass target=region2.v2.argotunnel.com
2026-07-30T23:14:51Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=99b97377-f0f9-4577-a018-6777cf5bdb85 status=pass target=region1.v2.argotunnel.com
2026-07-30T23:14:51Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=99b97377-f0f9-4577-a018-6777cf5bdb85 status=pass target=region2.v2.argotunnel.com
2026-07-30T23:14:51Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=99b97377-f0f9-4577-a018-6777cf5bdb85 status=pass target=region1.v2.argotunnel.com
2026-07-30T23:14:51Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=99b97377-f0f9-4577-a018-6777cf5bdb85 status=pass target=region2.v2.argotunnel.com
2026-07-30T23:14:51Z INF precheck component="Cloudflare API" details="API is reachable" run_id=99b97377-f0f9-4577-a018-6777cf5bdb85 status=pass target=api.cloudflare.com:443
2026-07-30T23:14:51Z INF precheck complete hard_fail=false run_id=99b97377-f0f9-4577-a018-6777cf5bdb85 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[07:13:06] Time: Fri Jul 31 07:13:06 AM CST 2026
[07:13:06] User: root (UID: 0)
[07:13:06] === STEP 1: 启动 API (端口 8450) ===
[07:14:37] API 已在运行
[07:14:37] API 状态: OK
[07:14:37] === STEP 2: 安装 cloudflared ===
[07:14:37] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:14:37] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:14:37] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:14:37] === STEP 3: 获取 Account ID ===
[07:14:38] Account ID: 8162aa3b2241c132e43a81f526d7f758
[07:14:38] === STEP 4: 创建/获取 Named Tunnel ===
[07:14:38] 检查现有 tunnel: aishield-tunnel
[07:14:38] API 响应: []
[07:14:38] 创建新 Named Tunnel: aishield-tunnel
[07:14:39] Tunnel 创建失败!
[07:14:39] 错误: [{"code": 10000, "message": "Authentication error"}]
[07:14:39] 完整响应: {"success":false,"errors":[{"code":10000,"message":"Authentication error"}],"messages":[],"result":null}
[07:14:39] === STEP 7: 启动 Named Tunnel ===
[07:14:41] ERROR: 无法启动 Named Tunnel (缺少 token 或 cert)
[07:14:41] TUNNEL_ID: 空
[07:14:41] TUNNEL_TOKEN: 空
[07:14:41] cert.pem: 存在
[07:14:41] === FALLBACK: 启动 Quick Tunnel（临时方案）===
[07:14:41] Quick Tunnel PID: 406253
[07:14:56] Quick Tunnel URL: https://starter-itself-geometry-walking.trycloudflare.com
[07:14:56] 注意: Quick Tunnel URL 无法绑定到 aishield.tools (error 1014)
[07:14:56] 请使用此 URL 临时访问: https://starter-itself-geometry-walking.trycloudflare.com
[07:14:56] === STEP 8: 持久化 ===
[07:14:57] systemd 服务已配置
[07:14:57] Cron 保活已设置
[07:14:57] === STEP 9: 验证 ===
[07:14:57] --- API (localhost:8450) ---
 OK
[07:14:57] --- cloudflared 进程 ---
root      406253  0.6  1.9 1294676 39196 ?       Sl   07:14   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
root      406502  0.0  1.3 1292484 27192 ?       Rl   07:14   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
[07:14:57] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[07:14:57] --- DNS 解析 ---
172.67.188.44
104.21.81.46
[07:14:57] === 部署汇总 ===
[07:14:57] Tunnel ID: 未获取
[07:14:57] Tunnel Type: Named Tunnel
[07:14:57] CNAME: 未配置
[07:14:57] API: http://localhost:8450
[07:14:57] 域名: https://aishield.tools
[07:14:57] cloudflared: /usr/local/bin/cloudflared
[07:14:57] PID: 406253
[07:14:57] 状态: Named Tunnel 配置失败，使用 Quick Tunnel 临时方案
[07:14:57] 需要手动操作: 创建 API Token with Account:Cloudflare Tunnel:Edit 权限
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-07-31 07:14:57 CST; 6s ago
   Main PID: 406494 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 16.9M
        CPU: 103ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─406494 /bin/bash /opt/start-tunnel.sh
             └─406502 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                 
=== CRONTAB ===
*/5 * * * * flock -xn /tmp/stargate.lock -c '/usr/local/qcloud/stargate/admin/start.sh > /dev/null 2>&1 &'
* * * * * pgrep -f 'cloudflared tunnel' > /dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
=== START SCRIPT ===
#!/bin/bash
# AIShield Tunnel 启动脚本
TOKEN_FILE='/root/.cloudflared/tunnel-token'
CF_BIN='/usr/local/bin/cloudflared'

cleanup() { kill $CF_PID 2>/dev/null; exit 0; }
trap cleanup SIGTERM SIGINT

if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE")
    $CF_BIN tunnel run --token "$TOKEN" &
    CF_PID=$!
else
    $CF_BIN tunnel --url http://localhost:8450 &
    CF_PID=$!
fi

wait $CF_PID

=== HTTPS Test from Runner ===
Time: Thu Jul 30 23:15:03 UTC 2026

=== curl test (aishield.tools) ===
error code: 1014

=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
