=== DIAGNOSTIC ===
Time: Tue Aug 18 08:13:41 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787012021.5661263, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1482617  1.0  1.8 1294676 37540 ?       Sl   08:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1482719  1.7  1.9 1294676 39468 ?       Sl   08:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-18T00:13:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-18T00:13:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-08-18T00:13:32Z INF Registered tunnel connection connIndex=2 connection=576d7b96-8acb-44ef-afc7-13a9654590ac event=0 ip=198.41.192.7 location=lax10 protocol=quic
2026-08-18T00:13:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-18T00:13:33Z INF Registered tunnel connection connIndex=3 connection=50b20b87-08db-4f52-b217-ba1222bcffe0 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-18T00:13:36Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.193
2026-08-18T00:13:36Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.193
2026-08-18T00:13:36Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-18T00:13:37Z INF +-------------------------------------------------------------------------------------+
2026-08-18T00:13:37Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-18T00:13:37Z INF +-------------------------------------------------------------------------------------+
2026-08-18T00:13:37Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-18T00:13:37Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T00:13:37Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T00:13:37Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T00:13:37Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T00:13:37Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T00:13:37Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T00:13:37Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-18T00:13:37Z INF |                                                                                     |
2026-08-18T00:13:37Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-18T00:13:37Z INF +-------------------------------------------------------------------------------------+
2026-08-18T00:13:37Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=0b4ed4bd-1f66-4db5-a7f6-b0d94daaf7a6 status=pass target=region1.v2.argotunnel.com
2026-08-18T00:13:37Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=0b4ed4bd-1f66-4db5-a7f6-b0d94daaf7a6 status=pass target=region2.v2.argotunnel.com
2026-08-18T00:13:37Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=0b4ed4bd-1f66-4db5-a7f6-b0d94daaf7a6 status=pass target=region1.v2.argotunnel.com
2026-08-18T00:13:37Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=0b4ed4bd-1f66-4db5-a7f6-b0d94daaf7a6 status=pass target=region2.v2.argotunnel.com
2026-08-18T00:13:37Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=0b4ed4bd-1f66-4db5-a7f6-b0d94daaf7a6 status=pass target=region1.v2.argotunnel.com
2026-08-18T00:13:37Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=0b4ed4bd-1f66-4db5-a7f6-b0d94daaf7a6 status=pass target=region2.v2.argotunnel.com
2026-08-18T00:13:37Z INF precheck component="Cloudflare API" details="API is reachable" run_id=0b4ed4bd-1f66-4db5-a7f6-b0d94daaf7a6 status=pass target=api.cloudflare.com:443
2026-08-18T00:13:37Z INF precheck complete hard_fail=false run_id=0b4ed4bd-1f66-4db5-a7f6-b0d94daaf7a6 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:13:22] Time: Tue Aug 18 08:13:22 AM CST 2026
[08:13:22] User: root (UID: 0)
[08:13:22] === STEP 1: 启动 API (端口 8450) ===
[08:13:23] API 已在运行
[08:13:23] API 状态: OK
[08:13:23] === STEP 2: 安装 cloudflared ===
[08:13:23] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:13:24] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:13:24] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:13:24] === STEP 3: 检查认证方式 ===
[08:13:24] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:13:24] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:13:24] 检查现有 tunnel...
[08:13:25] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax07, 1xlax08, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-18T00:13:25Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:13:25] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:13:25] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:13:25] 凭证文件存在
[08:13:25] 创建 config.yml...
[08:13:25] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:13:25] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:13:25] DNS 路由结果: 2026-08-18T00:13:25Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:13:25] === STEP 5: 更新 DNS (API) ===
[08:13:25] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:13:26] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:13:27] 设置 SSL 模式为 Full...
SSL: 跳过
[08:13:27] === STEP 6: 启动 Tunnel ===
[08:13:30] 启动 Named Tunnel (cert 模式)...
[08:13:30] 使用 config: /root/.cloudflared/config.yml
[08:13:30] cloudflared PID: 1482617
[08:13:32] Tunnel 连接已建立!
[08:13:32] --- cloudflared 日志 (最后 15 行) ---
2026-08-18T00:13:30Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-18T00:13:30Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-18T00:13:30Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-18T00:13:30Z INF Generated Connector ID: c2807af4-039e-4704-8117-87db9a8220dc
2026-08-18T00:13:30Z INF Initial protocol quic
2026-08-18T00:13:30Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T00:13:30Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T00:13:30Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T00:13:30Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T00:13:30Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-18T00:13:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.57
2026-08-18T00:13:31Z INF Registered tunnel connection connIndex=0 connection=031e2f3a-7a70-4768-a81a-78df6dab1d8f event=0 ip=198.41.192.57 location=lax08 protocol=quic
2026-08-18T00:13:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-18T00:13:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-08-18T00:13:32Z INF Registered tunnel connection connIndex=2 connection=576d7b96-8acb-44ef-afc7-13a9654590ac event=0 ip=198.41.192.7 location=lax10 protocol=quic
[08:13:32] === STEP 7: 持久化 ===
[08:13:33] systemd 服务已配置
[08:13:33] Cron 保活已设置
[08:13:33] === STEP 8: 验证 ===
[08:13:33] --- API (localhost:8450) ---
 OK
[08:13:33] --- cloudflared 进程 ---
root     1482617  3.0  1.9 1294420 38520 ?       Sl   08:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1482719  0.0  1.3 1292484 27684 ?       Rl   08:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:13:33] --- aishield.tools ---
 OK
[08:13:34] --- DNS CNAME ---
[08:13:34] --- DNS A ---
104.21.81.46
172.67.188.44
[08:13:34] === 部署汇总 ===
[08:13:34] Tunnel Mode: cert
[08:13:34] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:13:34] API: http://localhost:8450
[08:13:34] 域名: https://aishield.tools
[08:13:34] cloudflared: /usr/local/bin/cloudflared
[08:13:34] PID: 1482617
[08:13:34] Config: /root/.cloudflared/config.yml
[08:13:34] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:13:34] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-18 08:13:33 CST; 8s ago
   Main PID: 1482718 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 20.2M
        CPU: 154ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1482718 /bin/bash /opt/start-tunnel.sh
             └─1482719 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Tue Aug 18 00:13:41 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787012022.2334936, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
