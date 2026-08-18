=== DIAGNOSTIC ===
Time: Tue Aug 18 06:19:16 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787048356.61327, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1878489  0.9  1.8 1294420 37600 ?       Sl   18:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1878594  1.2  1.9 1294676 39320 ?       Sl   18:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1878972  3.3  1.9 1294420 39196 ?       Sl   18:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-18T10:19:05Z INF Registered tunnel connection connIndex=0 connection=4596add3-603b-4676-afb0-0f2b56500bbc event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-18T10:19:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-18T10:19:06Z INF Registered tunnel connection connIndex=1 connection=dacc21ae-e639-47a6-92ca-314927f9dd94 event=0 ip=198.41.192.7 location=lax10 protocol=quic
2026-08-18T10:19:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-18T10:19:07Z INF Registered tunnel connection connIndex=2 connection=32308724-949d-45cc-bbc5-e8c3090335e9 event=0 ip=198.41.192.227 location=lax05 protocol=quic
2026-08-18T10:19:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-18T10:19:08Z INF Registered tunnel connection connIndex=3 connection=20ce0462-40ea-4ddb-9968-7455a43b8a62 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-18T10:19:15Z INF +-----------------------------------------------------------------------------------------------+
2026-08-18T10:19:15Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-18T10:19:15Z INF +-----------------------------------------------------------------------------------------------+
2026-08-18T10:19:15Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-18T10:19:15Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-18T10:19:15Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-18T10:19:15Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-18T10:19:15Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-18T10:19:15Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-18T10:19:15Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-18T10:19:15Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-18T10:19:15Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-18T10:19:15Z INF |                                                                                               |
2026-08-18T10:19:15Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-18T10:19:15Z INF +-----------------------------------------------------------------------------------------------+
2026-08-18T10:19:15Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ea9f2f61-f4a6-48a7-8796-cb0f532f3315 status=pass target=region1.v2.argotunnel.com
2026-08-18T10:19:15Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ea9f2f61-f4a6-48a7-8796-cb0f532f3315 status=pass target=region2.v2.argotunnel.com
2026-08-18T10:19:15Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ea9f2f61-f4a6-48a7-8796-cb0f532f3315 status=pass target=region1.v2.argotunnel.com
2026-08-18T10:19:15Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=ea9f2f61-f4a6-48a7-8796-cb0f532f3315 status=fail target=region2.v2.argotunnel.com
2026-08-18T10:19:15Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ea9f2f61-f4a6-48a7-8796-cb0f532f3315 status=pass target=region1.v2.argotunnel.com
2026-08-18T10:19:15Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ea9f2f61-f4a6-48a7-8796-cb0f532f3315 status=pass target=region2.v2.argotunnel.com
2026-08-18T10:19:15Z INF precheck component="Cloudflare API" details="API is reachable" run_id=ea9f2f61-f4a6-48a7-8796-cb0f532f3315 status=pass target=api.cloudflare.com:443
2026-08-18T10:19:15Z INF precheck complete hard_fail=false run_id=ea9f2f61-f4a6-48a7-8796-cb0f532f3315 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:18:55] Time: Tue Aug 18 06:18:55 PM CST 2026
[18:18:55] User: root (UID: 0)
[18:18:55] === STEP 1: 启动 API (端口 8450) ===
[18:18:55] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 1xlax08, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[18:18:56] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:18:56] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:18:56] 凭证文件存在
[18:18:56] 创建 config.yml...
[18:18:56] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:18:56] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:18:56] API 已在运行
[18:18:56] API 状态: OK
[18:18:56] === STEP 2: 安装 cloudflared ===
[18:18:56] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:18:56] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:18:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:18:56] === STEP 3: 检查认证方式 ===
[18:18:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:18:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:18:56] 检查现有 tunnel...
[18:18:57] DNS 路由结果: 2026-08-18T10:18:57Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:18:57] === STEP 5: 更新 DNS (API) ===
[18:18:57] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:18:57] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:18:58] 设置 SSL 模式为 Full...
[18:18:59] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 1xlax08, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-18T10:18:59Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[18:18:59] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:18:59] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:18:59] 凭证文件存在
[18:18:59] 创建 config.yml...
[18:18:59] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:18:59] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
SSL: 跳过
[18:18:59] === STEP 6: 启动 Tunnel ===
[18:19:00] DNS 路由结果: 
[18:19:00] === STEP 5: 更新 DNS (API) ===
[18:19:00] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:19:00] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:19:01] 设置 SSL 模式为 Full...
SSL: 跳过
[18:19:02] === STEP 6: 启动 Tunnel ===
[18:19:03] 启动 Named Tunnel (cert 模式)...
[18:19:03] 使用 config: /root/.cloudflared/config.yml
[18:19:03] cloudflared PID: 1878489
[18:19:05] Tunnel 连接已建立!
[18:19:05] --- cloudflared 日志 (最后 15 行) ---
2026-08-18T10:19:03Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-18T10:19:03Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-18T10:19:03Z INF Generated Connector ID: 1247ba7c-9753-4677-bede-aadb4086f816
2026-08-18T10:19:03Z INF Initial protocol quic
2026-08-18T10:19:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T10:19:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T10:19:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T10:19:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T10:19:03Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-18T10:19:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-18T10:19:03Z INF Registered tunnel connection connIndex=0 connection=9add373b-35e0-42df-adeb-390e25f4cb65 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-18T10:19:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-18T10:19:03Z INF Registered tunnel connection connIndex=1 connection=c7dd1e40-09eb-4051-8e50-fd7608194c38 event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-18T10:19:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
2026-08-18T10:19:04Z INF Registered tunnel connection connIndex=2 connection=a7267abe-3cc1-4e1f-89c5-a98c7433f7ff event=0 ip=198.41.192.47 location=lax07 protocol=quic
[18:19:05] === STEP 7: 持久化 ===
[18:19:05] 启动 Named Tunnel (cert 模式)...
[18:19:05] 使用 config: /root/.cloudflared/config.yml
[18:19:05] cloudflared PID: 1878594
[18:19:05] systemd 服务已配置
[18:19:05] Cron 保活已设置
[18:19:05] === STEP 8: 验证 ===
[18:19:05] --- API (localhost:8450) ---
 OK
[18:19:05] --- cloudflared 进程 ---
root     1878489  4.5  1.9 1294420 38920 ?       Sl   18:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1878594  0.0  1.8 1293844 37056 ?       Sl   18:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1878672  0.0  1.3 1292484 27264 ?       Sl   18:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:19:05] --- aishield.tools ---
[18:19:07] Tunnel 连接已建立!
[18:19:07] --- cloudflared 日志 (最后 15 行) ---
2026-08-18T10:19:05Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-18T10:19:05Z INF Generated Connector ID: 5e1f8a2a-dad3-4005-ba91-363d4d08b00b
2026-08-18T10:19:05Z INF Initial protocol quic
2026-08-18T10:19:05Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T10:19:05Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T10:19:05Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T10:19:05Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T10:19:05Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-18T10:19:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-18T10:19:05Z INF Registered tunnel connection connIndex=0 connection=4596add3-603b-4676-afb0-0f2b56500bbc event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-18T10:19:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-18T10:19:06Z INF Registered tunnel connection connIndex=1 connection=dacc21ae-e639-47a6-92ca-314927f9dd94 event=0 ip=198.41.192.7 location=lax10 protocol=quic
2026-08-18T10:19:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
                                                                                                                                                                           2026-08-18T10:19:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.13
2026-08-18T10:19:06Z INF Registered tunnel connection connIndex=3 connection=b73c3bd6-e1d2-422d-95a4-0514b27aa507 event=0 ip=198.41.200.13 location=lax01 protocol=quic
[18:19:07] === STEP 7: 持久化 ===
 OK
[18:19:07] --- DNS CNAME ---
[18:19:08] --- DNS A ---
104.21.81.46
172.67.188.44
[18:19:08] === 部署汇总 ===
[18:19:08] Tunnel Mode: cert
[18:19:08] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:19:08] API: http://localhost:8450
[18:19:08] 域名: https://aishield.tools
[18:19:08] cloudflared: /usr/local/bin/cloudflared
[18:19:08] PID: 1878489
[18:19:08] Config: /root/.cloudflared/config.yml
[18:19:08] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:19:08] 状态: Named Tunnel (cert 模式) 已配置
[18:19:13] systemd 服务已配置
[18:19:13] Cron 保活已设置
[18:19:13] === STEP 8: 验证 ===
[18:19:13] --- API (localhost:8450) ---
 OK
[18:19:13] --- cloudflared 进程 ---
root     1878489  1.1  1.8 1294420 37600 ?       Sl   18:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1878594  1.6  1.9 1294676 39320 ?       Sl   18:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1878972  0.0  1.3 1292740 27104 ?       Sl   18:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:19:13] --- aishield.tools ---
 OK
[18:19:15] --- DNS CNAME ---
[18:19:15] --- DNS A ---
172.67.188.44
104.21.81.46
[18:19:15] === 部署汇总 ===
[18:19:15] Tunnel Mode: cert
[18:19:15] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:19:15] API: http://localhost:8450
[18:19:15] 域名: https://aishield.tools
[18:19:15] cloudflared: /usr/local/bin/cloudflared
[18:19:15] PID: 1878594
[18:19:15] Config: /root/.cloudflared/config.yml
[18:19:15] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:19:15] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-18 18:19:13 CST; 3s ago
   Main PID: 1878968 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.7M
        CPU: 113ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1878968 /bin/bash /opt/start-tunnel.sh
             └─1878972 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Tue Aug 18 10:19:17 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787048357.354403, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
