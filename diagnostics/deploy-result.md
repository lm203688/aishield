=== DIAGNOSTIC ===
Time: Sat Aug 15 11:13:38 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786763618.5205865, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2978898  1.0  1.9 1294676 38468 ?       Sl   11:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2979021  1.2  1.9 1294420 39756 ?       Sl   11:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-15T03:13:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-08-15T03:13:26Z INF Registered tunnel connection connIndex=0 connection=6ee3df32-d86a-4b55-89b4-ab9e9ca4dfb4 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-15T03:13:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-15T03:13:26Z INF Registered tunnel connection connIndex=1 connection=f34be312-ffda-47e2-95ff-d17f715be616 event=0 ip=198.41.192.167 location=lax05 protocol=quic
2026-08-15T03:13:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-15T03:13:27Z INF Registered tunnel connection connIndex=2 connection=191ee6cb-c394-46e7-beb7-6bda97df1dca event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-15T03:13:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.77
2026-08-15T03:13:28Z INF Registered tunnel connection connIndex=3 connection=db8b7ae2-8b33-4844-9dd9-327d0b04046e event=0 ip=198.41.192.77 location=lax11 protocol=quic
2026-08-15T03:13:32Z INF +-------------------------------------------------------------------------------------+
2026-08-15T03:13:32Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-15T03:13:32Z INF +-------------------------------------------------------------------------------------+
2026-08-15T03:13:32Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-15T03:13:32Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-15T03:13:32Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-15T03:13:32Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-15T03:13:32Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-15T03:13:32Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-15T03:13:32Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-15T03:13:32Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-15T03:13:32Z INF |                                                                                     |
2026-08-15T03:13:32Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-15T03:13:32Z INF +-------------------------------------------------------------------------------------+
2026-08-15T03:13:32Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=02650bc8-590e-43a0-9f89-d4df7e20180b status=pass target=region1.v2.argotunnel.com
2026-08-15T03:13:32Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=02650bc8-590e-43a0-9f89-d4df7e20180b status=pass target=region2.v2.argotunnel.com
2026-08-15T03:13:32Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=02650bc8-590e-43a0-9f89-d4df7e20180b status=pass target=region1.v2.argotunnel.com
2026-08-15T03:13:32Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=02650bc8-590e-43a0-9f89-d4df7e20180b status=pass target=region2.v2.argotunnel.com
2026-08-15T03:13:32Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=02650bc8-590e-43a0-9f89-d4df7e20180b status=pass target=region1.v2.argotunnel.com
2026-08-15T03:13:32Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=02650bc8-590e-43a0-9f89-d4df7e20180b status=pass target=region2.v2.argotunnel.com
2026-08-15T03:13:32Z INF precheck component="Cloudflare API" details="API is reachable" run_id=02650bc8-590e-43a0-9f89-d4df7e20180b status=pass target=api.cloudflare.com:443
2026-08-15T03:13:32Z INF precheck complete hard_fail=false run_id=02650bc8-590e-43a0-9f89-d4df7e20180b suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[11:13:15] Time: Sat Aug 15 11:13:15 AM CST 2026
[11:13:15] User: root (UID: 0)
[11:13:15] === STEP 1: 启动 API (端口 8450) ===
[11:13:17] API 已在运行
[11:13:17] API 状态: OK
[11:13:17] === STEP 2: 安装 cloudflared ===
[11:13:17] cloudflared 安装路径: /usr/local/bin/cloudflared
[11:13:17] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:13:17] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:13:17] === STEP 3: 检查认证方式 ===
[11:13:17] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[11:13:17] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[11:13:17] 检查现有 tunnel...
[11:13:18] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax05, 2xlax07 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[11:13:18] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:13:18] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[11:13:18] 凭证文件存在
[11:13:18] 创建 config.yml...
[11:13:18] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[11:13:18] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:13:19] DNS 路由结果: 2026-08-15T03:13:19Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[11:13:19] === STEP 5: 更新 DNS (API) ===
[11:13:19] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:13:20] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[11:13:21] 设置 SSL 模式为 Full...
SSL: 跳过
[11:13:22] === STEP 6: 启动 Tunnel ===
[11:13:25] 启动 Named Tunnel (cert 模式)...
[11:13:25] 使用 config: /root/.cloudflared/config.yml
[11:13:25] cloudflared PID: 2978898
[11:13:27] Tunnel 连接已建立!
[11:13:27] --- cloudflared 日志 (最后 15 行) ---
2026-08-15T03:13:25Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-15T03:13:25Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-15T03:13:25Z INF Generated Connector ID: 573adb5f-60c9-423b-85a7-300c9e164cec
2026-08-15T03:13:25Z INF Initial protocol quic
2026-08-15T03:13:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T03:13:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T03:13:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T03:13:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T03:13:25Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-15T03:13:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-08-15T03:13:26Z INF Registered tunnel connection connIndex=0 connection=6ee3df32-d86a-4b55-89b4-ab9e9ca4dfb4 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-15T03:13:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-15T03:13:26Z INF Registered tunnel connection connIndex=1 connection=f34be312-ffda-47e2-95ff-d17f715be616 event=0 ip=198.41.192.167 location=lax05 protocol=quic
2026-08-15T03:13:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-15T03:13:27Z INF Registered tunnel connection connIndex=2 connection=191ee6cb-c394-46e7-beb7-6bda97df1dca event=0 ip=198.41.200.13 location=lax01 protocol=quic
[11:13:27] === STEP 7: 持久化 ===
[11:13:28] systemd 服务已配置
[11:13:28] Cron 保活已设置
[11:13:28] === STEP 8: 验证 ===
[11:13:28] --- API (localhost:8450) ---
 OK
[11:13:28] --- cloudflared 进程 ---
root     2978898  3.0  1.9 1294676 39328 ?       Sl   11:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2979021  0.0  1.3 1292740 27664 ?       Rl   11:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[11:13:28] --- aishield.tools ---
 OK
[11:13:29] --- DNS CNAME ---
[11:13:29] --- DNS A ---
104.21.81.46
172.67.188.44
[11:13:29] === 部署汇总 ===
[11:13:29] Tunnel Mode: cert
[11:13:29] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:13:29] API: http://localhost:8450
[11:13:29] 域名: https://aishield.tools
[11:13:29] cloudflared: /usr/local/bin/cloudflared
[11:13:29] PID: 2978898
[11:13:29] Config: /root/.cloudflared/config.yml
[11:13:29] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:13:29] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-15 11:13:28 CST; 10s ago
   Main PID: 2979019 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.9M
        CPU: 134ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2979019 /bin/bash /opt/start-tunnel.sh
             └─2979021 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sat Aug 15 03:13:38 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786763619.2713058, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
