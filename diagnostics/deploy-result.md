=== DIAGNOSTIC ===
Time: Thu Aug 13 01:46:46 AM CST 2026
=== USER ===
root
=== GIT LOG ===
dbcf345 fix: download script from GitHub raw if git reset fails, add script version diagnostics
14ced6b chore: update deploy diagnostics [skip ci]
7b4068b fix: force git reset on server to get latest deploy script
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786556806.9863782, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      614742  0.1  1.6 1294676 32236 ?       Sl   Aug12   0:14 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      614954  0.1  1.6 1294676 32324 ?       Sl   Aug12   0:15 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-12T15:16:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-12T15:16:39Z INF +-------------------------------------------------------------------------------------+
2026-08-12T15:16:39Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-12T15:16:39Z INF +-------------------------------------------------------------------------------------+
2026-08-12T15:16:39Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-12T15:16:39Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-12T15:16:39Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-12T15:16:39Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-12T15:16:39Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-12T15:16:39Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-12T15:16:39Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-12T15:16:39Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-12T15:16:39Z INF |                                                                                     |
2026-08-12T15:16:39Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-12T15:16:39Z INF +-------------------------------------------------------------------------------------+
2026-08-12T15:16:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region1.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region2.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region1.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region2.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region1.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region2.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="Cloudflare API" details="API is reachable" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=api.cloudflare.com:443
2026-08-12T15:16:39Z INF precheck complete hard_fail=false run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 suggested_protocol=quic
2026-08-12T15:16:39Z INF Registered tunnel connection connIndex=0 connection=a7b98d0d-6200-410c-8fbf-1d48d91d03b4 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-12T15:16:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-12T15:16:40Z INF Registered tunnel connection connIndex=1 connection=5a08a41d-e21f-42d6-a1c9-c1c7175c9748 event=0 ip=198.41.192.67 location=lax11 protocol=quic
2026-08-12T15:16:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-12T15:16:41Z INF Registered tunnel connection connIndex=2 connection=c031658e-6e98-4e1c-aa47-b3d49e18e924 event=0 ip=198.41.192.227 location=lax05 protocol=quic
2026-08-12T15:16:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-12T15:16:42Z INF Registered tunnel connection connIndex=3 connection=cb2bb108-e5a9-4597-842e-9c5cc814842c event=0 ip=198.41.200.233 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:16:21] Time: Wed Aug 12 11:16:21 PM CST 2026
[23:16:21] User: root (UID: 0)
[23:16:21] === STEP 1: 启动 API (端口 8450) ===
[23:16:22] API 已在运行
[23:16:22] API 状态: OK
[23:16:22] === STEP 2: 安装 cloudflared ===
[23:16:22] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:16:22] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:16:22] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:16:22] === STEP 3: 检查认证方式 ===
[23:16:22] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:16:22] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:16:22] 检查现有 tunnel...
[23:16:23] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax07, 1xlax09, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[23:16:23] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:16:23] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:16:23] 凭证文件存在
[23:16:23] 创建 config.yml...
[23:16:23] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:16:23] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:16:25] DNS 路由结果: 2026-08-12T15:16:25Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:16:25] === STEP 5: 更新 DNS (API) ===
[23:16:25] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:16:27] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[23:16:29] 设置 SSL 模式为 Full...
SSL: 跳过
[23:16:30] === STEP 6: 启动 Tunnel ===
[23:16:33] 启动 Named Tunnel (cert 模式)...
[23:16:33] 使用 config: /root/.cloudflared/config.yml
[23:16:33] cloudflared PID: 614742
[23:16:41] Tunnel 连接已建立!
[23:16:41] --- cloudflared 日志 (最后 15 行) ---
2026-08-12T15:16:39Z INF |                                                                                     |
2026-08-12T15:16:39Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-12T15:16:39Z INF +-------------------------------------------------------------------------------------+
2026-08-12T15:16:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region1.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region2.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region1.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region2.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region1.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=region2.v2.argotunnel.com
2026-08-12T15:16:39Z INF precheck component="Cloudflare API" details="API is reachable" run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 status=pass target=api.cloudflare.com:443
2026-08-12T15:16:39Z INF precheck complete hard_fail=false run_id=c81cdae0-02fe-4d44-b91c-366b8d421218 suggested_protocol=quic
2026-08-12T15:16:39Z INF Registered tunnel connection connIndex=0 connection=a7b98d0d-6200-410c-8fbf-1d48d91d03b4 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-12T15:16:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-12T15:16:40Z INF Registered tunnel connection connIndex=1 connection=5a08a41d-e21f-42d6-a1c9-c1c7175c9748 event=0 ip=198.41.192.67 location=lax11 protocol=quic
2026-08-12T15:16:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
[23:16:41] === STEP 7: 持久化 ===
[23:16:44] systemd 服务已配置
[23:16:44] Cron 保活已设置
[23:16:44] === STEP 8: 验证 ===
[23:16:44] --- API (localhost:8450) ---
 OK
[23:16:44] --- cloudflared 进程 ---
root      614742  1.0  1.9 1294676 39356 ?       Sl   23:16   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      614954  0.0  1.3 1292740 27100 ?       Rl   23:16   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[23:16:44] --- aishield.tools ---
 OK
[23:16:45] --- DNS CNAME ---
[23:16:45] --- DNS A ---
104.21.81.46
172.67.188.44
[23:16:45] === 部署汇总 ===
[23:16:45] Tunnel Mode: cert
[23:16:45] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:16:45] API: http://localhost:8450
[23:16:45] 域名: https://aishield.tools
[23:16:45] cloudflared: /usr/local/bin/cloudflared
[23:16:45] PID: 614742
[23:16:45] Config: /root/.cloudflared/config.yml
[23:16:45] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:16:45] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-12 23:16:44 CST; 2h 30min ago
   Main PID: 614950 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.6M
        CPU: 15.070s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─614950 /bin/bash /opt/start-tunnel.sh
             └─614954 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2772386,fd=3))                                                    
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
Time: Wed Aug 12 17:46:47 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786556807.6285603, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
