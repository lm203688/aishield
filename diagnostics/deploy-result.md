=== DIAGNOSTIC ===
Time: Wed Aug 5 12:24:41 PM CST 2026
=== USER ===
root
=== GIT LOG ===
dbcf345 fix: download script from GitHub raw if git reset fails, add script version diagnostics
14ced6b chore: update deploy diagnostics [skip ci]
7b4068b fix: force git reset on server to get latest deploy script
=== SCRIPT CHECK ===
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785903881.7915251, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1586308  1.0  1.9 1294676 39044 ?       Sl   12:24   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1586326  0.9  1.9 1294676 38972 ?       Sl   12:24   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1586797  0.0  1.8 1359444 37520 ?       Sl   12:24   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-05T04:24:29Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-05T04:24:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-05T04:24:30Z INF Registered tunnel connection connIndex=0 connection=98c4a319-996b-428d-a15c-99f8d14851a9 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-05T04:24:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.10202026-08-05T04:24:31Z INF Registered tunnel connection connIndex=1 connection=5dcdf53a-0099-489c-ac80-a23a2d8d233f event=0 ip=198.41.192.107 location=lax11 protocol=quic
2026-08-05T04:24:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-05T04:24:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.27
2026-08-05T04:24:32Z INF Registered tunnel connection connIndex=2 connection=243d4db7-736a-41c5-a11d-d6dbdcbdab60 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-05T04:24:33Z INF Registered tunnel connection connIndex=3 connection=41902211-e0f6-4a69-854a-df662d45ce58 event=0 ip=198.41.192.27 location=lax10 protocol=quic
2026-08-05T04:24:36Z INF +-------------------------------------------------------------------------------------+
2026-08-05T04:24:36Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-05T04:24:36Z INF +-------------------------------------------------------------------------------------+
2026-08-05T04:24:36Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-05T04:24:36Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-05T04:24:36Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-05T04:24:36Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-05T04:24:36Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-05T04:24:36Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-05T04:24:36Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-05T04:24:36Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-05T04:24:36Z INF |                                                                                     |
2026-08-05T04:24:36Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-05T04:24:36Z INF +-------------------------------------------------------------------------------------+
2026-08-05T04:24:36Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f430c8ca-71a8-40be-9f61-c82440b3bef0 status=pass target=region1.v2.argotunnel.com
2026-08-05T04:24:36Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f430c8ca-71a8-40be-9f61-c82440b3bef0 status=pass target=region2.v2.argotunnel.com
2026-08-05T04:24:36Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f430c8ca-71a8-40be-9f61-c82440b3bef0 status=pass target=region1.v2.argotunnel.com
2026-08-05T04:24:36Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f430c8ca-71a8-40be-9f61-c82440b3bef0 status=pass target=region2.v2.argotunnel.com
2026-08-05T04:24:36Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f430c8ca-71a8-40be-9f61-c82440b3bef0 status=pass target=region1.v2.argotunnel.com
2026-08-05T04:24:36Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f430c8ca-71a8-40be-9f61-c82440b3bef0 status=pass target=region2.v2.argotunnel.com
2026-08-05T04:24:36Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f430c8ca-71a8-40be-9f61-c82440b3bef0 status=pass target=api.cloudflare.com:443
2026-08-05T04:24:36Z INF precheck complete hard_fail=false run_id=f430c8ca-71a8-40be-9f61-c82440b3bef0 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:24:18] Time: Wed Aug  5 12:24:18 PM CST 2026
[12:24:18] User: root (UID: 0)
[12:24:18] === STEP 1: 启动 API (端口 8450) ===
[12:24:18] API 已在运行
[12:24:18] API 状态: OK
[12:24:18] === STEP 2: 安装 cloudflared ===
[12:24:18] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:24:18] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:24:18] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:24:18] === STEP 3: 检查认证方式 ===
[12:24:18] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:24:18] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:24:18] 检查现有 tunnel...
[12:24:19] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax05, 2xlax08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[12:24:19] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:24:19] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:24:19] 凭证文件存在
[12:24:19] 创建 config.yml...
[12:24:19] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:24:19] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:24:20] API 已在运行
[12:24:20] API 状态: OK
[12:24:20] === STEP 2: 安装 cloudflared ===
[12:24:20] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:24:20] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:24:20] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:24:20] === STEP 3: 检查认证方式 ===
[12:24:20] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:24:20] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:24:21] 检查现有 tunnel...
[12:24:21] DNS 路由结果: 2026-08-05T04:24:21Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:24:21] === STEP 5: 更新 DNS (API) ===
[12:24:21] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:24:21] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[12:24:22] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax05, 2xlax08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[12:24:22] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:24:22] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:24:22] 凭证文件存在
[12:24:22] 创建 config.yml...
[12:24:22] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:24:22] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[12:24:23] 设置 SSL 模式为 Full...
[12:24:24] DNS 路由结果: 2026-08-05T04:24:24Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:24:24] === STEP 5: 更新 DNS (API) ===
[12:24:24] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:24:25] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
SSL: 跳过
[12:24:25] === STEP 6: 启动 Tunnel ===
DNS 更新: OK
[12:24:26] 设置 SSL 模式为 Full...
SSL: 跳过
[12:24:26] === STEP 6: 启动 Tunnel ===
[12:24:29] 启动 Named Tunnel (cert 模式)...
[12:24:29] 使用 config: /root/.cloudflared/config.yml
[12:24:29] cloudflared PID: 1586308
[12:24:29] 启动 Named Tunnel (cert 模式)...
[12:24:29] 使用 config: /root/.cloudflared/config.yml
[12:24:29] cloudflared PID: 1586326
[12:24:31] Tunnel 连接已建立!
[12:24:31] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T04:24:29Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-05T04:24:29Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-05T04:24:29Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-05T04:24:29Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T04:24:29Z INF Generated Connector ID: a8097f7d-3016-477c-8eee-be0ffb8d4243
2026-08-05T04:24:29Z INF Initial protocol quic
2026-08-05T04:24:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:24:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:24:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:24:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:24:29Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-05T04:24:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-05T04:24:30Z INF Registered tunnel connection connIndex=0 connection=98c4a319-996b-428d-a15c-99f8d14851a9 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-05T04:24:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.102026-08-05T04:24:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
2026-08-05T04:24:30Z INF Registered tunnel connection connIndex=1 connection=9562c09a-29b0-4979-9736-293663650844 event=0 ip=198.41.200.233 location=lax01 protocol=quic
[12:24:31] === STEP 7: 持久化 ===
[12:24:31] systemd 服务已配置
[12:24:31] Cron 保活已设置
[12:24:31] === STEP 8: 验证 ===
[12:24:31] --- API (localhost:8450) ---
 OK
[12:24:31] --- cloudflared 进程 ---
root     1586308  4.5  1.9 1294676 39044 ?       Sl   12:24   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1586326  4.5  1.9 1294420 38704 ?       Sl   12:24   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1586435  0.0  1.3 1292484 27448 ?       Rl   12:24   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:24:31] --- aishield.tools ---
[12:24:31] Tunnel 连接已建立!
[12:24:31] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T04:24:29Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-05T04:24:29Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T04:24:29Z INF Generated Connector ID: a8097f7d-3016-477c-8eee-be0ffb8d4243
2026-08-05T04:24:29Z INF Initial protocol quic
2026-08-05T04:24:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:24:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:24:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:24:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:24:29Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-05T04:24:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-05T04:24:30Z INF Registered tunnel connection connIndex=0 connection=98c4a319-996b-428d-a15c-99f8d14851a9 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-05T04:24:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.10202026-08-05T04:24:31Z INF Registered tunnel connection connIndex=1 connection=5dcdf53a-0099-489c-ac80-a23a2d8d233f event=0 ip=198.41.192.107 location=lax11 protocol=quic
2026-08-05T04:24:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
026-08-05T04:24:31Z INF Registered tunnel connection connIndex=2 connection=24ddfbfd-eee1-4553-87e4-542ac9cc8446 event=0 ip=198.41.192.107 location=lax05 protocol=quic
2026-08-05T04:24:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.33
[12:24:31] === STEP 7: 持久化 ===
 OK
[12:24:33] --- DNS CNAME ---
[12:24:33] --- DNS A ---
172.67.188.44
104.21.81.46
[12:24:33] === 部署汇总 ===
[12:24:33] Tunnel Mode: cert
[12:24:33] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:24:33] API: http://localhost:8450
[12:24:33] 域名: https://aishield.tools
[12:24:33] cloudflared: /usr/local/bin/cloudflared
[12:24:33] PID: 1586308
[12:24:33] Config: /root/.cloudflared/config.yml
[12:24:33] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:24:33] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 12:24:41 CST; 806ms ago
   Main PID: 1586791 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 16.2M
        CPU: 90ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1586791 /bin/bash /opt/start-tunnel.sh
             └─1586797 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug  5 04:24:42 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785903882.9492407, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
