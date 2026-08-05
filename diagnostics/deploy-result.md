=== DIAGNOSTIC ===
Time: Wed Aug 5 11:05:20 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785942320.8440804, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1858935  0.1  1.7 1294676 36016 ?       Sl   18:16   0:27 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1859040  0.1  1.8 1294676 36320 ?       Sl   18:16   0:27 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-05T10:16:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-05T10:16:30Z INF Registered tunnel connection connIndex=0 connection=1a3755d6-2b10-43af-a994-53b93d167d15 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-05T10:16:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-05T10:16:30Z INF Registered tunnel connection connIndex=1 connection=8d999c6b-95ff-4f34-b4c2-0298059b4bd5 event=0 ip=198.41.192.37 location=lax09 protocol=quic
2026-08-05T10:16:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-08-05T10:16:31Z INF Registered tunnel connection connIndex=2 connection=41023622-c730-44de-810b-63083c2e31c3 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-05T10:16:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.7
2026-08-05T10:16:32Z INF Registered tunnel connection connIndex=3 connection=56614f60-2c4d-404e-b562-0f90c9c82755 event=0 ip=198.41.192.7 location=lax09 protocol=quic
2026-08-05T10:16:37Z INF +-------------------------------------------------------------------------------------+
2026-08-05T10:16:37Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-05T10:16:37Z INF +-------------------------------------------------------------------------------------+
2026-08-05T10:16:37Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-05T10:16:37Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-05T10:16:37Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-05T10:16:37Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-05T10:16:37Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-05T10:16:37Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-05T10:16:37Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-05T10:16:37Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-05T10:16:37Z INF |                                                                                     |
2026-08-05T10:16:37Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-05T10:16:37Z INF +-------------------------------------------------------------------------------------+
2026-08-05T10:16:37Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=0572e84b-716c-4816-b6fc-f6c2123892ce status=pass target=region1.v2.argotunnel.com
2026-08-05T10:16:37Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=0572e84b-716c-4816-b6fc-f6c2123892ce status=pass target=region2.v2.argotunnel.com
2026-08-05T10:16:37Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=0572e84b-716c-4816-b6fc-f6c2123892ce status=pass target=region1.v2.argotunnel.com
2026-08-05T10:16:37Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=0572e84b-716c-4816-b6fc-f6c2123892ce status=pass target=region2.v2.argotunnel.com
2026-08-05T10:16:37Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=0572e84b-716c-4816-b6fc-f6c2123892ce status=pass target=region1.v2.argotunnel.com
2026-08-05T10:16:37Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=0572e84b-716c-4816-b6fc-f6c2123892ce status=pass target=region2.v2.argotunnel.com
2026-08-05T10:16:37Z INF precheck component="Cloudflare API" details="API is reachable" run_id=0572e84b-716c-4816-b6fc-f6c2123892ce status=pass target=api.cloudflare.com:443
2026-08-05T10:16:37Z INF precheck complete hard_fail=false run_id=0572e84b-716c-4816-b6fc-f6c2123892ce suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:14:49] Time: Wed Aug  5 06:14:49 PM CST 2026
[18:14:49] User: root (UID: 0)
[18:14:49] === STEP 1: 启动 API (端口 8450) ===
[18:16:19] API 已在运行
[18:16:19] API 状态: OK
[18:16:19] === STEP 2: 安装 cloudflared ===
[18:16:19] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:16:19] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:16:19] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:16:19] === STEP 3: 检查认证方式 ===
[18:16:19] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:16:19] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:16:19] 检查现有 tunnel...
[18:16:20] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax08, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[18:16:20] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:16:20] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:16:20] 凭证文件存在
[18:16:20] 创建 config.yml...
[18:16:20] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:16:20] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:16:24] DNS 路由结果: 2026-08-05T10:16:24Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:16:24] === STEP 5: 更新 DNS (API) ===
[18:16:24] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:16:24] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:16:25] 设置 SSL 模式为 Full...
SSL: 跳过
[18:16:26] === STEP 6: 启动 Tunnel ===
[18:16:29] 启动 Named Tunnel (cert 模式)...
[18:16:29] 使用 config: /root/.cloudflared/config.yml
[18:16:29] cloudflared PID: 1858935
[18:16:31] Tunnel 连接已建立!
[18:16:31] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T10:16:29Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-05T10:16:29Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T10:16:29Z INF Generated Connector ID: e7dadb20-341a-49a3-aafe-026cbda3c1d6
2026-08-05T10:16:29Z INF Initial protocol quic
2026-08-05T10:16:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T10:16:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T10:16:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T10:16:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T10:16:29Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-05T10:16:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-05T10:16:30Z INF Registered tunnel connection connIndex=0 connection=1a3755d6-2b10-43af-a994-53b93d167d15 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-05T10:16:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-05T10:16:30Z INF Registered tunnel connection connIndex=1 connection=8d999c6b-95ff-4f34-b4c2-0298059b4bd5 event=0 ip=198.41.192.37 location=lax09 protocol=quic
2026-08-05T10:16:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-08-05T10:16:31Z INF Registered tunnel connection connIndex=2 connection=41023622-c730-44de-810b-63083c2e31c3 event=0 ip=198.41.200.43 location=lax01 protocol=quic
[18:16:31] === STEP 7: 持久化 ===
[18:16:32] systemd 服务已配置
[18:16:32] Cron 保活已设置
[18:16:32] === STEP 8: 验证 ===
[18:16:32] --- API (localhost:8450) ---
 OK
[18:16:32] --- cloudflared 进程 ---
root     1858935  3.0  1.9 1294420 39232 ?       Sl   18:16   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1859040  0.0  1.3 1292740 27164 ?       Rl   18:16   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:16:32] --- aishield.tools ---
 OK
[18:16:33] --- DNS CNAME ---
[18:16:34] --- DNS A ---
172.67.188.44
104.21.81.46
[18:16:34] === 部署汇总 ===
[18:16:34] Tunnel Mode: cert
[18:16:34] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:16:34] API: http://localhost:8450
[18:16:34] 域名: https://aishield.tools
[18:16:34] cloudflared: /usr/local/bin/cloudflared
[18:16:34] PID: 1858935
[18:16:34] Config: /root/.cloudflared/config.yml
[18:16:34] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:16:34] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 18:16:32 CST; 4h 48min ago
   Main PID: 1859039 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 16.9M
        CPU: 27.813s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1859039 /bin/bash /opt/start-tunnel.sh
             └─1859040 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                 
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
Time: Wed Aug  5 15:05:21 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785942321.4459734, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
