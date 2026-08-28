=== DIAGNOSTIC ===
Time: Sat Aug 29 03:38:16 AM CST 2026
=== USER ===
root
=== GIT LOG ===
f2fb5c5a chore(radar): publish 2026-08-28 tech radar
152554ea chore(radar): publish 2026-08-28 tech radar
82df29bc auto: 部署验证状态回写 [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 215, "uptime": 1787945896.8989973, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3216961  0.1  1.6 1294676 33080 ?       Sl   02:09   0:07 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3217192  0.1  1.6 1294676 33240 ?       Sl   02:09   0:07 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T18:09:09Z INF Registered tunnel connection connIndex=0 connection=d21ce8be-c681-4235-bd49-f58908426544 event=0 ip=198.41.192.67 location=lax08 protocol=quic
2026-08-28T18:09:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-28T18:09:10Z INF Registered tunnel connection connIndex=1 connection=c530f529-5a89-4cd2-9bad-a9cb4cf48f43 event=0 ip=198.41.200.33 location=sjc08 protocol=quic
2026-08-28T18:09:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-08-28T18:09:11Z INF Registered tunnel connection connIndex=2 connection=ec336c95-6f14-4777-b54f-036c6dde361d event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-28T18:09:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.37
2026-08-28T18:09:12Z INF Registered tunnel connection connIndex=3 connection=b7fa2c9f-c17c-41fe-8f93-7ce3f530900c event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-08-28T18:09:12Z INF +-----------------------------------------------------------------------------------------------+
2026-08-28T18:09:12Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-28T18:09:12Z INF +-----------------------------------------------------------------------------------------------+
2026-08-28T18:09:12Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-28T18:09:12Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-28T18:09:12Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-28T18:09:12Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-28T18:09:12Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-28T18:09:12Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-28T18:09:12Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-28T18:09:12Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-28T18:09:12Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-28T18:09:12Z INF |                                                                                               |
2026-08-28T18:09:12Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-28T18:09:12Z INF +-----------------------------------------------------------------------------------------------+
2026-08-28T18:09:12Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=78ef14dd-5d60-44c4-a4d0-7d82699f38f5 status=pass target=region1.v2.argotunnel.com
2026-08-28T18:09:12Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=78ef14dd-5d60-44c4-a4d0-7d82699f38f5 status=pass target=region2.v2.argotunnel.com
2026-08-28T18:09:12Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=78ef14dd-5d60-44c4-a4d0-7d82699f38f5 status=pass target=region1.v2.argotunnel.com
2026-08-28T18:09:12Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=78ef14dd-5d60-44c4-a4d0-7d82699f38f5 status=fail target=region2.v2.argotunnel.com
2026-08-28T18:09:12Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=78ef14dd-5d60-44c4-a4d0-7d82699f38f5 status=pass target=region1.v2.argotunnel.com
2026-08-28T18:09:12Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=78ef14dd-5d60-44c4-a4d0-7d82699f38f5 status=pass target=region2.v2.argotunnel.com
2026-08-28T18:09:12Z INF precheck component="Cloudflare API" details="API is reachable" run_id=78ef14dd-5d60-44c4-a4d0-7d82699f38f5 status=pass target=api.cloudflare.com:443
2026-08-28T18:09:12Z INF precheck complete hard_fail=false run_id=78ef14dd-5d60-44c4-a4d0-7d82699f38f5 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:06:44] Time: Sat Aug 29 02:06:44 AM CST 2026
[02:06:44] User: root (UID: 0)
[02:06:44] === STEP 1: 启动 API (端口 8450) ===
[02:08:54] HEAD: f2fb5c5a -> f2fb5c5a
[02:08:55] server-card 版本: 磁盘=4.3.0 仓库=4.3.0
[02:08:55] 运行进程自报版本=4.3.0 / 磁盘代码版本=4.3.0
[02:08:55] 代码已是最新且 API 健康 -> 跳过重启
[02:08:55] API 状态: OK
[02:08:55] === STEP 2: 安装 cloudflared ===
[02:08:55] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:08:55] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:08:55] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:08:55] === STEP 3: 检查认证方式 ===
[02:08:55] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:08:55] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:08:55] 检查现有 tunnel...
[02:08:56] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                   
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax07, 2xlax12, 1xsjc05, 1xsjc07, 1xsjc08, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                               
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                               
[02:08:56] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:08:56] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:08:56] 凭证文件存在
[02:08:56] 创建 config.yml...
[02:08:56] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:08:56] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:08:57] DNS 路由结果: 2026-08-28T18:08:57Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:08:57] === STEP 5: 更新 DNS (API) ===
[02:08:57] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:08:58] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:08:58] 设置 SSL 模式为 Full...
SSL: 跳过
[02:08:59] === STEP 6: 启动 Tunnel ===
[02:09:02] 启动 Named Tunnel (cert 模式)...
[02:09:02] 使用 config: /root/.cloudflared/config.yml
[02:09:02] cloudflared PID: 3216961
[02:09:10] Tunnel 连接已建立!
[02:09:10] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T18:09:02Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T18:09:02Z INF Generated Connector ID: 79f8122c-5544-4aba-bb75-afffddd572f5
2026-08-28T18:09:02Z INF Initial protocol quic
2026-08-28T18:09:02Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T18:09:02Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T18:09:02Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T18:09:02Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T18:09:02Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T18:09:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.193
2026-08-28T18:09:07Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-28T18:09:07Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.193
2026-08-28T18:09:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-28T18:09:09Z INF Registered tunnel connection connIndex=0 connection=d21ce8be-c681-4235-bd49-f58908426544 event=0 ip=198.41.192.67 location=lax08 protocol=quic
2026-08-28T18:09:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-28T18:09:10Z INF Registered tunnel connection connIndex=1 connection=c530f529-5a89-4cd2-9bad-a9cb4cf48f43 event=0 ip=198.41.200.33 location=sjc08 protocol=quic
[02:09:10] === STEP 7: 持久化 ===
[02:09:11] systemd 服务已配置
[02:09:11] Cron 保活已设置
[02:09:11] === STEP 8: 验证 ===
[02:09:11] --- API (localhost:8450) ---
 OK
[02:09:11] --- cloudflared 进程 ---
root     3216961  1.1  1.9 1294420 39496 ?       Sl   02:09   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3217192  0.0  1.3 1292484 27392 ?       Rl   02:09   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:09:11] --- aishield.tools ---
 OK
[02:09:12] --- DNS CNAME ---
[02:09:12] --- DNS A ---
172.67.188.44
104.21.81.46
[02:09:12] === 部署汇总 ===
[02:09:12] Tunnel Mode: cert
[02:09:12] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:09:12] API: http://localhost:8450
[02:09:12] 域名: https://aishield.tools
[02:09:12] cloudflared: /usr/local/bin/cloudflared
[02:09:12] PID: 3216961
[02:09:12] Config: /root/.cloudflared/config.yml
[02:09:12] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:09:12] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-29 02:09:11 CST; 1h 29min ago
   Main PID: 3217184 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 16.2M
        CPU: 7.849s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3217184 /bin/bash /opt/start-tunnel.sh
             └─3217192 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3125577,fd=3))                                                    
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
Time: Fri Aug 28 19:38:17 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 215, "uptime": 1787945897.563888, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
