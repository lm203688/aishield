=== DIAGNOSTIC ===
Time: Sun Aug 16 10:12:58 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786846378.9508047, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3838564  0.1  1.6 1294676 33824 ?       Sl   09:10   0:05 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3838761  0.1  1.6 1294676 32816 ?       Sl   09:10   0:05 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-16T01:10:44Z INF +-------------------------------------------------------------------------------------+
2026-08-16T01:10:44Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-16T01:10:44Z INF +-------------------------------------------------------------------------------------+
2026-08-16T01:10:44Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-16T01:10:44Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-16T01:10:44Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-16T01:10:44Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-16T01:10:44Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-16T01:10:44Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-16T01:10:44Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-16T01:10:44Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-16T01:10:44Z INF |                                                                                     |
2026-08-16T01:10:44Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-16T01:10:44Z INF +-------------------------------------------------------------------------------------+
2026-08-16T01:10:44Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region1.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region2.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region1.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region2.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region1.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region2.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=api.cloudflare.com:443
2026-08-16T01:10:44Z INF precheck complete hard_fail=false run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 suggested_protocol=quic
2026-08-16T01:10:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-16T01:10:45Z INF Registered tunnel connection connIndex=0 connection=dcb75696-653a-4ee0-bec9-b428e8f32121 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-16T01:10:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-16T01:10:45Z INF Registered tunnel connection connIndex=1 connection=6c246b78-6ab7-454c-bae3-4974b1d53f60 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-08-16T01:10:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
2026-08-16T01:10:46Z INF Registered tunnel connection connIndex=2 connection=7a681199-3a8a-42aa-b60a-86f93592e4e5 event=0 ip=198.41.192.27 location=lax07 protocol=quic
2026-08-16T01:10:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.13
2026-08-16T01:10:47Z INF Registered tunnel connection connIndex=3 connection=68cee26b-a867-40c2-9633-f2c28a984ecb event=0 ip=198.41.200.13 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[09:10:29] Time: Sun Aug 16 09:10:29 AM CST 2026
[09:10:29] User: root (UID: 0)
[09:10:29] === STEP 1: 启动 API (端口 8450) ===
[09:10:30] API 已在运行
[09:10:30] API 状态: OK
[09:10:30] === STEP 2: 安装 cloudflared ===
[09:10:30] cloudflared 安装路径: /usr/local/bin/cloudflared
[09:10:30] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:10:30] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:10:30] === STEP 3: 检查认证方式 ===
[09:10:30] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:10:30] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:10:30] 检查现有 tunnel...
[09:10:31] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax09, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-16T01:10:31Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[09:10:31] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:10:31] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[09:10:31] 凭证文件存在
[09:10:31] 创建 config.yml...
[09:10:31] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[09:10:31] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:10:32] DNS 路由结果: 2026-08-16T01:10:32Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[09:10:32] === STEP 5: 更新 DNS (API) ===
[09:10:32] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:10:33] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[09:10:34] 设置 SSL 模式为 Full...
SSL: 跳过
[09:10:34] === STEP 6: 启动 Tunnel ===
[09:10:37] 启动 Named Tunnel (cert 模式)...
[09:10:37] 使用 config: /root/.cloudflared/config.yml
[09:10:37] cloudflared PID: 3838564
[09:10:45] Tunnel 连接已建立!
[09:10:45] --- cloudflared 日志 (最后 15 行) ---
2026-08-16T01:10:44Z INF |                                                                                     |
2026-08-16T01:10:44Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-16T01:10:44Z INF +-------------------------------------------------------------------------------------+
2026-08-16T01:10:44Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region1.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region2.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region1.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region2.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region1.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=region2.v2.argotunnel.com
2026-08-16T01:10:44Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 status=pass target=api.cloudflare.com:443
2026-08-16T01:10:44Z INF precheck complete hard_fail=false run_id=f7dcc4dd-04a3-4594-9bd5-3e068622ef45 suggested_protocol=quic
2026-08-16T01:10:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-16T01:10:45Z INF Registered tunnel connection connIndex=0 connection=dcb75696-653a-4ee0-bec9-b428e8f32121 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-16T01:10:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-16T01:10:45Z INF Registered tunnel connection connIndex=1 connection=6c246b78-6ab7-454c-bae3-4974b1d53f60 event=0 ip=198.41.192.7 location=lax05 protocol=quic
[09:10:45] === STEP 7: 持久化 ===
[09:10:46] systemd 服务已配置
[09:10:46] Cron 保活已设置
[09:10:46] === STEP 8: 验证 ===
[09:10:46] --- API (localhost:8450) ---
 OK
[09:10:46] --- cloudflared 进程 ---
root     3838564  1.1  1.9 1294676 39236 ?       Sl   09:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3838761  0.0  1.3 1292740 27304 ?       Rl   09:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[09:10:46] --- aishield.tools ---
 OK
[09:10:47] --- DNS CNAME ---
[09:10:47] --- DNS A ---
104.21.81.46
172.67.188.44
[09:10:47] === 部署汇总 ===
[09:10:47] Tunnel Mode: cert
[09:10:47] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:10:47] API: http://localhost:8450
[09:10:47] 域名: https://aishield.tools
[09:10:47] cloudflared: /usr/local/bin/cloudflared
[09:10:47] PID: 3838564
[09:10:47] Config: /root/.cloudflared/config.yml
[09:10:47] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:10:47] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-16 09:10:46 CST; 1h 2min ago
   Main PID: 3838757 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 16.3M
        CPU: 5.922s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3838757 /bin/bash /opt/start-tunnel.sh
             └─3838761 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2342254,fd=3))                                                    
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
Time: Sun Aug 16 02:12:59 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786846379.6814268, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
