=== DIAGNOSTIC ===
Time: Sat Aug 29 10:29:05 AM CST 2026
=== USER ===
root
=== GIT LOG ===
f3b02739 chore(guard): 2026-08-29 守夜报告 · 三项全绿
05bb06e0 auto: distribution 状态域心跳 [skip ci]
1360a2e7 auto: 生态目录上架状态更新 [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 215, "uptime": 1787970545.9241047, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3468095  0.1  1.4 1294676 28628 ?       Sl   08:33   0:10 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3468190  0.1  1.3 1294676 28016 ?       Sl   08:33   0:10 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-29T00:33:10Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-29T00:33:10Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-29T00:33:10Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-29T00:33:10Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-29T00:33:10Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-29T00:33:10Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-29T00:33:10Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-29T00:33:10Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-29T00:33:10Z INF |                                                                                     |
2026-08-29T00:33:10Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-29T00:33:10Z INF +-------------------------------------------------------------------------------------+
2026-08-29T00:33:10Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=58177447-8742-4241-a43e-391646fcb40b status=pass target=region1.v2.argotunnel.com
2026-08-29T00:33:10Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=58177447-8742-4241-a43e-391646fcb40b status=pass target=region2.v2.argotunnel.com
2026-08-29T00:33:10Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=58177447-8742-4241-a43e-391646fcb40b status=pass target=region1.v2.argotunnel.com
2026-08-29T00:33:10Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=58177447-8742-4241-a43e-391646fcb40b status=pass target=region2.v2.argotunnel.com
2026-08-29T00:33:10Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=58177447-8742-4241-a43e-391646fcb40b status=pass target=region1.v2.argotunnel.com
2026-08-29T00:33:10Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=58177447-8742-4241-a43e-391646fcb40b status=pass target=region2.v2.argotunnel.com
2026-08-29T00:33:10Z INF precheck component="Cloudflare API" details="API is reachable" run_id=58177447-8742-4241-a43e-391646fcb40b status=pass target=api.cloudflare.com:443
2026-08-29T00:33:10Z INF precheck complete hard_fail=false run_id=58177447-8742-4241-a43e-391646fcb40b suggested_protocol=quic
2026-08-29T00:33:11Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-29T00:33:11Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-08-29T00:33:12Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-29T00:33:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
2026-08-29T00:33:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-29T00:33:27Z INF Registered tunnel connection connIndex=1 connection=3420acd7-dd26-48ab-9875-d3c76cb5b2c2 event=0 ip=198.41.200.33 location=sjc08 protocol=quic
2026-08-29T00:33:31Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-08-29T00:33:31Z INF Retrying connection in up to 4s connIndex=3 event=0 ip=198.41.200.73
2026-08-29T00:33:34Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-29T00:33:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.13
2026-08-29T00:33:54Z INF Registered tunnel connection connIndex=3 connection=c0a44a2f-b95d-4798-9b5f-7283272a65e7 event=0 ip=198.41.200.13 location=sjc10 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:32:34] Time: Sat Aug 29 08:32:34 AM CST 2026
[08:32:34] User: root (UID: 0)
[08:32:34] === STEP 1: 启动 API (端口 8450) ===
[08:32:35] HEAD: f3b02739 -> f3b02739
[08:32:55] server-card 版本: 磁盘=4.3.0 仓库=unknown
[08:32:55] 运行进程自报版本=4.3.0 / 磁盘代码版本=4.3.0
[08:32:55] 代码已是最新且 API 健康 -> 跳过重启
[08:32:55] API 状态: OK
[08:32:55] === STEP 2: 安装 cloudflared ===
[08:32:55] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:32:56] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:32:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:32:56] === STEP 3: 检查认证方式 ===
[08:32:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:32:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:32:56] 检查现有 tunnel...
[08:32:56] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax08, 2xlax09, 1xlax11, 1xsjc05, 1xsjc07, 2xsjc08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
2026-08-29T00:32:56Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:32:56] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:32:56] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:32:56] 凭证文件存在
[08:32:56] 创建 config.yml...
[08:32:56] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:32:56] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:32:58] DNS 路由结果: 2026-08-29T00:32:58Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:32:58] === STEP 5: 更新 DNS (API) ===
[08:32:58] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:32:59] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:32:59] 设置 SSL 模式为 Full...
SSL: 跳过
[08:33:00] === STEP 6: 启动 Tunnel ===
[08:33:03] 启动 Named Tunnel (cert 模式)...
[08:33:03] 使用 config: /root/.cloudflared/config.yml
[08:33:03] cloudflared PID: 3468095
[08:33:05] Tunnel 连接已建立!
[08:33:05] --- cloudflared 日志 (最后 15 行) ---
2026-08-29T00:33:03Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-29T00:33:03Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-29T00:33:03Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-29T00:33:03Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-29T00:33:03Z INF Generated Connector ID: a343d457-1441-49ee-96e2-84d7b633ac23
2026-08-29T00:33:03Z INF Initial protocol quic
2026-08-29T00:33:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-29T00:33:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-29T00:33:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-29T00:33:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-29T00:33:03Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-29T00:33:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-29T00:33:04Z INF Registered tunnel connection connIndex=0 connection=7759e044-78b3-44aa-b161-deea773bacfd event=0 ip=198.41.192.227 location=lax08 protocol=quic
2026-08-29T00:33:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
2026-08-29T00:33:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
[08:33:05] === STEP 7: 持久化 ===
[08:33:06] systemd 服务已配置
[08:33:06] Cron 保活已设置
[08:33:06] === STEP 8: 验证 ===
[08:33:06] --- API (localhost:8450) ---
 OK
[08:33:06] --- cloudflared 进程 ---
root     3468095  3.0  1.9 1293844 38204 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3468190  0.0  1.3 1292740 27520 ?       Rl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:33:06] --- aishield.tools ---
 OK
[08:33:07] --- DNS CNAME ---
[08:33:08] --- DNS A ---
172.67.188.44
104.21.81.46
[08:33:08] === 部署汇总 ===
[08:33:08] Tunnel Mode: cert
[08:33:08] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:33:08] API: http://localhost:8450
[08:33:08] 域名: https://aishield.tools
[08:33:08] cloudflared: /usr/local/bin/cloudflared
[08:33:08] PID: 3468095
[08:33:08] Config: /root/.cloudflared/config.yml
[08:33:08] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:33:08] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-29 08:33:06 CST; 1h 55min ago
   Main PID: 3468189 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 21.8M
        CPU: 10.429s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3468189 /bin/bash /opt/start-tunnel.sh
             └─3468190 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sat Aug 29 02:29:07 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 215, "uptime": 1787970547.335275, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
