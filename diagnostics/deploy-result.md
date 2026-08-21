=== DIAGNOSTIC ===
Time: Sat Aug 22 01:16:57 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787332617.2752352, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      693415  0.1  1.8 1294676 36780 ?       Sl   Aug21   0:11 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      693523  0.1  1.8 1294676 37072 ?       Sl   Aug21   0:11 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-21T15:15:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-08-21T15:15:39Z INF Registered tunnel connection connIndex=0 connection=461742a4-05bb-44db-8739-9d276aef2c4d event=0 ip=198.41.192.77 location=sjc06 protocol=quic
2026-08-21T15:15:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-21T15:15:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-21T15:15:41Z INF Registered tunnel connection connIndex=1 connection=75c9324e-bbc8-4fcf-ad63-6e845233f38f event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-21T15:15:41Z INF Registered tunnel connection connIndex=2 connection=ceed1a15-ab44-4bbd-969e-e0b3db6efbba event=0 ip=198.41.200.63 location=sjc08 protocol=quic
2026-08-21T15:15:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.107
2026-08-21T15:15:42Z INF Registered tunnel connection connIndex=3 connection=50ad5117-a68b-4db8-bf71-191996abc46c event=0 ip=198.41.192.107 location=sjc01 protocol=quic
2026-08-21T15:15:48Z INF +-------------------------------------------------------------------------------------+
2026-08-21T15:15:48Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-21T15:15:48Z INF +-------------------------------------------------------------------------------------+
2026-08-21T15:15:48Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-21T15:15:48Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-21T15:15:48Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-21T15:15:48Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-21T15:15:48Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-21T15:15:48Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-21T15:15:48Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-21T15:15:48Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-21T15:15:48Z INF |                                                                                     |
2026-08-21T15:15:48Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-21T15:15:48Z INF +-------------------------------------------------------------------------------------+
2026-08-21T15:15:48Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f1fa92a8-b335-495c-937e-260d8cb897e9 status=pass target=region1.v2.argotunnel.com
2026-08-21T15:15:48Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f1fa92a8-b335-495c-937e-260d8cb897e9 status=pass target=region2.v2.argotunnel.com
2026-08-21T15:15:48Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f1fa92a8-b335-495c-937e-260d8cb897e9 status=pass target=region1.v2.argotunnel.com
2026-08-21T15:15:48Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f1fa92a8-b335-495c-937e-260d8cb897e9 status=pass target=region2.v2.argotunnel.com
2026-08-21T15:15:48Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f1fa92a8-b335-495c-937e-260d8cb897e9 status=pass target=region1.v2.argotunnel.com
2026-08-21T15:15:48Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f1fa92a8-b335-495c-937e-260d8cb897e9 status=pass target=region2.v2.argotunnel.com
2026-08-21T15:15:48Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f1fa92a8-b335-495c-937e-260d8cb897e9 status=pass target=api.cloudflare.com:443
2026-08-21T15:15:48Z INF precheck complete hard_fail=false run_id=f1fa92a8-b335-495c-937e-260d8cb897e9 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:13:59] Time: Fri Aug 21 11:13:59 PM CST 2026
[23:13:59] User: root (UID: 0)
[23:13:59] === STEP 1: 启动 API (端口 8450) ===
[23:15:30] API 已在运行
[23:15:30] API 状态: OK
[23:15:30] === STEP 2: 安装 cloudflared ===
[23:15:30] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:15:30] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:15:30] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:15:30] === STEP 3: 检查认证方式 ===
[23:15:30] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:15:30] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:15:30] 检查现有 tunnel...
[23:15:31] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xsjc01, 1xsjc05, 3xsjc06, 1xsjc07, 2xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[23:15:31] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:15:31] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:15:31] 凭证文件存在
[23:15:31] 创建 config.yml...
[23:15:31] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:15:31] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:15:33] DNS 路由结果: 2026-08-21T15:15:33Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:15:33] === STEP 5: 更新 DNS (API) ===
[23:15:33] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:15:34] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[23:15:35] 设置 SSL 模式为 Full...
SSL: 跳过
[23:15:36] === STEP 6: 启动 Tunnel ===
[23:15:39] 启动 Named Tunnel (cert 模式)...
[23:15:39] 使用 config: /root/.cloudflared/config.yml
[23:15:39] cloudflared PID: 693415
[23:15:41] Tunnel 连接已建立!
[23:15:41] --- cloudflared 日志 (最后 15 行) ---
2026-08-21T15:15:39Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-21T15:15:39Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-21T15:15:39Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-21T15:15:39Z INF Generated Connector ID: 19aea563-336e-4b1f-8b17-623c25afd058
2026-08-21T15:15:39Z INF Initial protocol quic
2026-08-21T15:15:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-21T15:15:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-21T15:15:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-21T15:15:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-21T15:15:39Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-21T15:15:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-08-21T15:15:39Z INF Registered tunnel connection connIndex=0 connection=461742a4-05bb-44db-8739-9d276aef2c4d event=0 ip=198.41.192.77 location=sjc06 protocol=quic
2026-08-21T15:15:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-21T15:15:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-21T15:15:41Z INF Registered tunnel connection connIndex=1 connection=75c9324e-bbc8-4fcf-ad63-6e845233f38f event=0 ip=198.41.200.233 location=sjc07 protocol=quic
[23:15:41] === STEP 7: 持久化 ===
[23:15:42] systemd 服务已配置
[23:15:42] Cron 保活已设置
[23:15:42] === STEP 8: 验证 ===
[23:15:42] --- API (localhost:8450) ---
 OK
[23:15:42] --- cloudflared 进程 ---
root      693415  3.3  1.9 1294676 38996 ?       Sl   23:15   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      693523  0.0  1.3 1292484 27372 ?       Rl   23:15   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[23:15:42] --- aishield.tools ---
 OK
[23:15:44] --- DNS CNAME ---
[23:15:44] --- DNS A ---
172.67.188.44
104.21.81.46
[23:15:44] === 部署汇总 ===
[23:15:44] Tunnel Mode: cert
[23:15:44] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:15:44] API: http://localhost:8450
[23:15:44] 域名: https://aishield.tools
[23:15:44] cloudflared: /usr/local/bin/cloudflared
[23:15:44] PID: 693415
[23:15:44] Config: /root/.cloudflared/config.yml
[23:15:44] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:15:44] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-21 23:15:42 CST; 2h 1min ago
   Main PID: 693519 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 17.9M
        CPU: 11.840s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─693519 /bin/bash /opt/start-tunnel.sh
             └─693523 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 21 17:16:57 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787332617.7859883, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
