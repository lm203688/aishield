=== DIAGNOSTIC ===
Time: Wed Aug 5 12:50:21 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785905421.7429972, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1601132  0.1  1.7 1294676 35672 ?       Sl   12:37   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1601178  0.1  1.7 1294676 35924 ?       Sl   12:37   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1601392  0.1  1.8 1360284 36332 ?       Sl   12:37   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-05T04:37:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-05T04:37:26Z INF Registered tunnel connection connIndex=1 connection=cb089d99-7e3e-4dc0-9a7e-e98989a6dda9 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-05T04:37:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-05T04:37:26Z INF Registered tunnel connection connIndex=2 connection=c8ce5e95-5e14-42d1-bbea-f0a08507be4b event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-05T04:37:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.7
2026-08-05T04:37:28Z INF Registered tunnel connection connIndex=3 connection=f130b3bd-d3f1-4869-985e-d1ef6e57acda event=0 ip=198.41.192.7 location=lax09 protocol=quic
2026-08-05T04:37:35Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T04:37:35Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-05T04:37:35Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T04:37:35Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-05T04:37:35Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-05T04:37:35Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-05T04:37:35Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-05T04:37:35Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-05T04:37:35Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-05T04:37:35Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-05T04:37:35Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-05T04:37:35Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-05T04:37:35Z INF |                                                                                               |
2026-08-05T04:37:35Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-05T04:37:35Z INF +-----------------------------------------------------------------------------------------------+
2026-08-05T04:37:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=730d8c84-3b50-450d-8f80-c021fed142dd status=pass target=region1.v2.argotunnel.com
2026-08-05T04:37:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=730d8c84-3b50-450d-8f80-c021fed142dd status=pass target=region2.v2.argotunnel.com
2026-08-05T04:37:35Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=730d8c84-3b50-450d-8f80-c021fed142dd status=pass target=region1.v2.argotunnel.com
2026-08-05T04:37:35Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=730d8c84-3b50-450d-8f80-c021fed142dd status=fail target=region2.v2.argotunnel.com
2026-08-05T04:37:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=730d8c84-3b50-450d-8f80-c021fed142dd status=pass target=region1.v2.argotunnel.com
2026-08-05T04:37:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=730d8c84-3b50-450d-8f80-c021fed142dd status=pass target=region2.v2.argotunnel.com
2026-08-05T04:37:35Z INF precheck component="Cloudflare API" details="API is reachable" run_id=730d8c84-3b50-450d-8f80-c021fed142dd status=pass target=api.cloudflare.com:443
2026-08-05T04:37:35Z INF precheck complete hard_fail=false run_id=730d8c84-3b50-450d-8f80-c021fed142dd suggested_protocol=http2
8d796d43-70c3-4c7b-a5e5-5968d1af3fe0 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:37:11] Time: Wed Aug  5 12:37:11 PM CST 2026
[12:37:11] User: root (UID: 0)
[12:37:11] === STEP 1: 启动 API (端口 8450) ===
[12:37:12] API 已在运行
[12:37:12] API 状态: OK
[12:37:12] === STEP 2: 安装 cloudflared ===
[12:37:12] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:37:12] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:37:12] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:37:12] === STEP 3: 检查认证方式 ===
[12:37:12] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:37:12] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:37:12] 检查现有 tunnel...
[12:37:12] 启动 Named Tunnel (cert 模式)...
[12:37:12] 使用 config: /root/.cloudflared/config.yml
[12:37:12] cloudflared PID: 1600420
[12:37:12] API 已在运行
[12:37:12] API 状态: OK
[12:37:12] === STEP 2: 安装 cloudflared ===
[12:37:12] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:37:12] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:37:13] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:37:13] === STEP 3: 检查认证方式 ===
[12:37:13] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:37:13] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:37:13] 检查现有 tunnel...
[12:37:13] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax01     
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[12:37:13] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:37:13] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:37:13] 凭证文件存在
[12:37:13] 创建 config.yml...
[12:37:13] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:37:13] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:37:14] Tunnel 连接已建立!
[12:37:14] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T04:37:12Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:37:12Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-05T04:37:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-05T04:37:13Z INF Registered tunnel connection connIndex=0 connection=29517d59-9bed-4a9f-8723-cc796eb854f9 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-05T04:37:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
2026-08-05T04:37:13Z INF Registered tunnel connection connIndex=1 connection=71ec6d87-1db9-4537-b2b3-2ec0582fc4d8 event=0 ip=198.41.192.227 location=lax09 protocol=quic
2026-08-05T04:37:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              2026-08-05T04:37:14Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.73
2026-08-05T04:37:14Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.73
2026-08-05T04:37:14Z ERR Connection terminated connIndex=1
2026-08-05T04:37:14Z ERR no more connections active and exiting
2026-08-05T04:37:14Z INF Tunnel server stopped
2026-08-05T04:37:14Z INF Metrics server stopped
2026-08-05T04:37:14Z ERR icmp router terminated error="context canceled"
eled"
[12:37:14] === STEP 7: 持久化 ===
[12:37:14] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS      
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax01, 1xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                  
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                  
[12:37:14] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:37:14] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:37:14] 凭证文件存在
[12:37:14] 创建 config.yml...
[12:37:14] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:37:14] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:37:15] systemd 服务已配置
[12:37:15] Cron 保活已设置
[12:37:15] === STEP 8: 验证 ===
[12:37:15] --- API (localhost:8450) ---
 OK
[12:37:15] --- cloudflared 进程 ---
root     1600420  3.6  1.8 1293836 37772 ?       Sl   12:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1600535  3.0  1.4 1292740 29336 ?       Sl   12:37   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
root     1600668  0.0  1.4 1292740 29608 ?       Sl   12:37   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
[12:37:15] --- aishield.tools ---
 OK
[12:37:16] --- DNS CNAME ---
[12:37:16] --- DNS A ---
172.67.188.44
104.21.81.46
[12:37:16] === 部署汇总 ===
[12:37:16] Tunnel Mode: cert
[12:37:16] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:37:16] API: http://localhost:8450
[12:37:16] 域名: https://aishield.tools
[12:37:16] cloudflared: /usr/local/bin/cloudflared
[12:37:16] PID: 1600420
[12:37:16] DNS 路由结果: 2026-08-05T04:37:16Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:37:16] Config: /root/.cloudflared/config.yml
[12:37:16] === STEP 5: 更新 DNS (API) ===
[12:37:16] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:37:16] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:37:16] 状态: Named Tunnel (cert 模式) 已配置
[12:37:16] DNS 路由结果: 2026-08-05T04:37:16Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:37:16] === STEP 5: 更新 DNS (API) ===
[12:37:16] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:37:17] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[12:37:18] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[12:37:19] 设置 SSL 模式为 Full...
SSL: 跳过
[12:37:20] === STEP 6: 启动 Tunnel ===
DNS 更新: OK
[12:37:21] 设置 SSL 模式为 Full...
SSL: 跳过
[12:37:22] === STEP 6: 启动 Tunnel ===
[12:37:23] 启动 Named Tunnel (cert 模式)...
[12:37:23] 使用 config: /root/.cloudflared/config.yml
[12:37:23] cloudflared PID: 1601132
[12:37:25] 启动 Named Tunnel (cert 模式)...
[12:37:25] 使用 config: /root/.cloudflared/config.yml
[12:37:25] cloudflared PID: 1601178
[12:37:27] Tunnel 连接已建立!
[12:37:27] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T04:37:25Z INF Generated Connector ID: ecb8dccb-a48d-4bb2-ae0a-8f417792b170
2026-08-05T04:37:25Z INF Initial protocol quic
2026-08-05T04:37:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:37:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:37:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:37:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:37:25Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-05T04:37:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-05T04:37:25Z INF Registered tunnel connection connIndex=0 connection=1073306d-7850-41b6-816c-49282f64eefc event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-05T04:37:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-05T04:37:26Z INF Registered tunnel connection connIndex=1 connection=cb089d99-7e3e-4dc0-9a7e-e98989a6dda9 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-05T04:37:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-05T04:37:26Z INF Registered tunnel connection connIndex=2 connection=c8ce5e95-5e14-42d1-bbea-f0a08507be4b event=0 ip=198.41.200.33 location=lax01 protocol=quic
26-08-05T04:37:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.53
2026-08-05T04:37:26Z INF Registered tunnel connection connIndex=3 connection=3143c47c-21c4-4abc-93be-7a39bc9f473a event=0 ip=198.41.200.53 location=lax01 protocol=quic
[12:37:27] === STEP 7: 持久化 ===
[12:37:27] Tunnel 连接已建立!
[12:37:27] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T04:37:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:37:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:37:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T04:37:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T04:37:25Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-05T04:37:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-05T04:37:25Z INF Registered tunnel connection connIndex=0 connection=1073306d-7850-41b6-816c-49282f64eefc event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-05T04:37:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-05T04:37:26Z INF Registered tunnel connection connIndex=1 connection=cb089d99-7e3e-4dc0-9a7e-e98989a6dda9 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-05T04:37:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-05T04:37:26Z INF Registered tunnel connection connIndex=2 connection=c8ce5e95-5e14-42d1-bbea-f0a08507be4b event=0 ip=198.41.200.33 location=lax01 protocol=quic
26-08-05T04:37:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.53
2026-08-05T04:37:26Z INF Registered tunnel connection connIndex=3 connection=3143c47c-21c4-4abc-93be-7a39bc9f473a event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-05T04:37:27Z ERR  error="stream 5 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-05T04:37:27Z ERR Request failed error="stream 5 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.200.113 type=http
[12:37:27] === STEP 7: 持久化 ===
[12:37:28] systemd 服务已配置
[12:37:28] systemd 服务已配置
[12:37:28] Cron 保活已设置
[12:37:28] Cron 保活已设置
[12:37:28] === STEP 8: 验证 ===
[12:37:28] --- API (localhost:8450) ---
[12:37:28] === STEP 8: 验证 ===
[12:37:28] --- API (localhost:8450) ---
 OK
[12:37:28] --- cloudflared 进程 ---
 OK
[12:37:28] --- cloudflared 进程 ---
root     1601132  2.4  1.9 1294676 39900 ?       Sl   12:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1601178  3.3  1.9 1294420 39372 ?       Sl   12:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1601392  0.0  1.3 1292740 27552 ?       Dl   12:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:37:28] --- aishield.tools ---
root     1601132  2.4  1.9 1294676 39900 ?       Sl   12:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1601178  3.3  1.9 1294420 39372 ?       Sl   12:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1601392  0.0  1.3 1292740 27552 ?       Dl   12:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:37:28] --- aishield.tools ---
 OK
[12:37:29] --- DNS CNAME ---
[12:37:29] --- DNS A ---
104.21.81.46
172.67.188.44
[12:37:29] === 部署汇总 ===
[12:37:29] Tunnel Mode: cert
[12:37:29] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:37:29] API: http://localhost:8450
[12:37:29] 域名: https://aishield.tools
[12:37:29] cloudflared: /usr/local/bin/cloudflared
[12:37:29] PID: 1601178
[12:37:29] Config: /root/.cloudflared/config.yml
[12:37:29] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:37:29] 状态: Named Tunnel (cert 模式) 已配置
 OK
[12:37:30] --- DNS CNAME ---
[12:37:30] --- DNS A ---
172.67.188.44
104.21.81.46
[12:37:30] === 部署汇总 ===
[12:37:30] Tunnel Mode: cert
[12:37:30] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:37:30] API: http://localhost:8450
[12:37:30] 域名: https://aishield.tools
[12:37:30] cloudflared: /usr/local/bin/cloudflared
[12:37:30] PID: 1601132
[12:37:30] Config: /root/.cloudflared/config.yml
[12:37:30] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:37:30] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 12:37:28 CST; 12min ago
   Main PID: 1601387 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.0M
        CPU: 1.233s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1601387 /bin/bash /opt/start-tunnel.sh
             └─1601392 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug  5 04:50:22 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785905422.2389212, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
