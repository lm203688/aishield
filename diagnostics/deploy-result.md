=== DIAGNOSTIC ===
Time: Sat Aug 29 02:05:13 AM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 215, "uptime": 1787940313.4917376, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3213878  1.3  1.9 1360284 39532 ?       Sl   02:05   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3214009  1.6  1.9 1294676 39828 ?       Sl   02:05   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T18:05:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-28T18:05:03Z INF Registered tunnel connection connIndex=0 connection=c62e02f0-94b3-4328-90e8-8681c119c554 event=0 ip=198.41.192.37 location=lax12 protocol=quic
2026-08-28T18:05:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-28T18:05:04Z INF Registered tunnel connection connIndex=1 connection=580ba5a8-06c1-4091-b3b7-bdb8366482b6 event=0 ip=198.41.200.113 location=sjc05 protocol=quic
2026-08-28T18:05:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-28T18:05:05Z INF Registered tunnel connection connIndex=2 connection=be109021-2bd1-4b84-8c88-53c075b329ba event=0 ip=198.41.200.13 location=sjc07 protocol=quic
2026-08-28T18:05:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.77
2026-08-28T18:05:06Z INF Registered tunnel connection connIndex=3 connection=59a46a30-8341-4615-a2fd-9037aa66a5ea event=0 ip=198.41.192.77 location=lax12 protocol=quic
2026-08-28T18:05:10Z INF +-------------------------------------------------------------------------------------+
2026-08-28T18:05:10Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-28T18:05:10Z INF +-------------------------------------------------------------------------------------+
2026-08-28T18:05:10Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-28T18:05:10Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T18:05:10Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T18:05:10Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T18:05:10Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T18:05:10Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T18:05:10Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T18:05:10Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-28T18:05:10Z INF |                                                                                     |
2026-08-28T18:05:10Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-28T18:05:10Z INF +-------------------------------------------------------------------------------------+
2026-08-28T18:05:10Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cb43bc49-10df-4e9b-8522-97ffd60da85c status=pass target=region1.v2.argotunnel.com
2026-08-28T18:05:10Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cb43bc49-10df-4e9b-8522-97ffd60da85c status=pass target=region2.v2.argotunnel.com
2026-08-28T18:05:10Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cb43bc49-10df-4e9b-8522-97ffd60da85c status=pass target=region1.v2.argotunnel.com
2026-08-28T18:05:10Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cb43bc49-10df-4e9b-8522-97ffd60da85c status=pass target=region2.v2.argotunnel.com
2026-08-28T18:05:10Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cb43bc49-10df-4e9b-8522-97ffd60da85c status=pass target=region1.v2.argotunnel.com
2026-08-28T18:05:10Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cb43bc49-10df-4e9b-8522-97ffd60da85c status=pass target=region2.v2.argotunnel.com
2026-08-28T18:05:10Z INF precheck component="Cloudflare API" details="API is reachable" run_id=cb43bc49-10df-4e9b-8522-97ffd60da85c status=pass target=api.cloudflare.com:443
2026-08-28T18:05:10Z INF precheck complete hard_fail=false run_id=cb43bc49-10df-4e9b-8522-97ffd60da85c suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:04:03] Time: Sat Aug 29 02:04:03 AM CST 2026
[02:04:03] User: root (UID: 0)
[02:04:03] === STEP 1: 启动 API (端口 8450) ===
[02:04:35] HEAD: f2fb5c5a -> f2fb5c5a
[02:04:55] server-card 版本: 磁盘=4.3.0 仓库=unknown
[02:04:55] 运行进程自报版本=4.3.0 / 磁盘代码版本=4.3.0
[02:04:55] 代码已是最新且 API 健康 -> 跳过重启
[02:04:55] API 状态: OK
[02:04:55] === STEP 2: 安装 cloudflared ===
[02:04:55] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:56] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:56] === STEP 3: 检查认证方式 ===
[02:04:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:56] 检查现有 tunnel...
[02:04:57] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax08, 1xlax09, 1xlax10, 2xsjc05, 2xsjc07 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
2026-08-28T18:04:57Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:04:57] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:57] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:57] 凭证文件存在
[02:04:57] 创建 config.yml...
[02:04:57] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:57] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:57] DNS 路由结果: 2026-08-28T18:04:57Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:57] === STEP 5: 更新 DNS (API) ===
[02:04:58] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:58] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:04:59] 设置 SSL 模式为 Full...
SSL: 跳过
[02:05:00] === STEP 6: 启动 Tunnel ===
[02:05:03] 启动 Named Tunnel (cert 模式)...
[02:05:03] 使用 config: /root/.cloudflared/config.yml
[02:05:03] cloudflared PID: 3213878
[02:05:05] Tunnel 连接已建立!
[02:05:05] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T18:05:03Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-28T18:05:03Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T18:05:03Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T18:05:03Z INF Generated Connector ID: b80db81e-6a1c-45a6-b9f3-94e1716da296
2026-08-28T18:05:03Z INF Initial protocol quic
2026-08-28T18:05:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T18:05:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T18:05:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T18:05:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T18:05:03Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T18:05:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-28T18:05:03Z INF Registered tunnel connection connIndex=0 connection=c62e02f0-94b3-4328-90e8-8681c119c554 event=0 ip=198.41.192.37 location=lax12 protocol=quic
2026-08-28T18:05:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-28T18:05:04Z INF Registered tunnel connection connIndex=1 connection=580ba5a8-06c1-4091-b3b7-bdb8366482b6 event=0 ip=198.41.200.113 location=sjc05 protocol=quic
2026-08-28T18:05:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
[02:05:05] === STEP 7: 持久化 ===
[02:05:05] systemd 服务已配置
[02:05:05] Cron 保活已设置
[02:05:05] === STEP 8: 验证 ===
[02:05:05] --- API (localhost:8450) ---
 OK
[02:05:05] --- cloudflared 进程 ---
root     3213878  5.5  1.9 1360028 39328 ?       Sl   02:05   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3214009  0.0  1.3 1292740 27668 ?       Rl   02:05   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:05:05] --- aishield.tools ---
 OK
[02:05:07] --- DNS CNAME ---
[02:05:07] --- DNS A ---
104.21.81.46
172.67.188.44
[02:05:07] === 部署汇总 ===
[02:05:07] Tunnel Mode: cert
[02:05:07] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:05:07] API: http://localhost:8450
[02:05:07] 域名: https://aishield.tools
[02:05:07] cloudflared: /usr/local/bin/cloudflared
[02:05:07] PID: 3213878
[02:05:07] Config: /root/.cloudflared/config.yml
[02:05:07] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:05:07] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-29 02:05:05 CST; 7s ago
   Main PID: 3214008 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.8M
        CPU: 140ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3214008 /bin/bash /opt/start-tunnel.sh
             └─3214009 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 28 18:05:14 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 215, "uptime": 1787940314.7018247, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
