=== DIAGNOSTIC ===
Time: Mon Aug 10 01:13:15 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786338795.0865734, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2525180  0.2  1.9 1294676 38688 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2525333  0.2  1.9 1294676 38216 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-10T05:10:40Z INF Registered tunnel connection connIndex=2 connection=a6515c65-e502-4254-9b1e-b6f980427824 event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-08-10T05:10:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-10T05:10:41Z INF Registered tunnel connection connIndex=3 connection=5f9c9be3-d00f-45a9-bbfa-8d458424718e event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-10T05:10:45Z ERR  error="stream 5 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-10T05:10:45Z ERR Request failed error="stream 5 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.192.37 type=http
2026-08-10T05:10:47Z INF +-----------------------------------------------------------------------------------------------+
2026-08-10T05:10:47Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-10T05:10:47Z INF +-----------------------------------------------------------------------------------------------+
2026-08-10T05:10:47Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-10T05:10:47Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-10T05:10:47Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-10T05:10:47Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-10T05:10:47Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-10T05:10:47Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-10T05:10:47Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-10T05:10:47Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-10T05:10:47Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-10T05:10:47Z INF |                                                                                               |
2026-08-10T05:10:47Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-10T05:10:47Z INF +-----------------------------------------------------------------------------------------------+
2026-08-10T05:10:47Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ae124137-8ba0-4f16-8434-b5d5bcb3b6aa status=pass target=region1.v2.argotunnel.com
2026-08-10T05:10:47Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ae124137-8ba0-4f16-8434-b5d5bcb3b6aa status=pass target=region2.v2.argotunnel.com
2026-08-10T05:10:47Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ae124137-8ba0-4f16-8434-b5d5bcb3b6aa status=pass target=region1.v2.argotunnel.com
2026-08-10T05:10:47Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=ae124137-8ba0-4f16-8434-b5d5bcb3b6aa status=fail target=region2.v2.argotunnel.com
2026-08-10T05:10:47Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ae124137-8ba0-4f16-8434-b5d5bcb3b6aa status=pass target=region1.v2.argotunnel.com
2026-08-10T05:10:47Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ae124137-8ba0-4f16-8434-b5d5bcb3b6aa status=pass target=region2.v2.argotunnel.com
2026-08-10T05:10:47Z INF precheck component="Cloudflare API" details="API is reachable" run_id=ae124137-8ba0-4f16-8434-b5d5bcb3b6aa status=pass target=api.cloudflare.com:443
2026-08-10T05:10:47Z INF precheck complete hard_fail=false run_id=ae124137-8ba0-4f16-8434-b5d5bcb3b6aa suggested_protocol=http2
2026-08-10T05:10:53Z ERR  error="stream 5 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-10T05:10:53Z ERR Request failed error="stream 5 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.200.233 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[13:10:23] Time: Mon Aug 10 01:10:23 PM CST 2026
[13:10:23] User: root (UID: 0)
[13:10:23] 启动 Named Tunnel (cert 模式)...
[13:10:23] === STEP 1: 启动 API (端口 8450) ===
104.21.81.46
172.67.188.44
[13:10:23] 使用 config: /root/.cloudflared/config.yml
[13:10:23] === 部署汇总 ===
[13:10:23] Tunnel Mode: cert
[13:10:23] cloudflared PID: 2523823
[13:10:23] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:10:23] API: http://localhost:8450
[13:10:23] 域名: https://aishield.tools
[13:10:23] cloudflared: /usr/local/bin/cloudflared
[13:10:23] PID: 2522749
[13:10:23] Config: /root/.cloudflared/config.yml
[13:10:23] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:10:23] 状态: Named Tunnel (cert 模式) 已配置
[13:10:23] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[13:10:24] API 已在运行
[13:10:24] API 状态: OK
[13:10:24] === STEP 2: 安装 cloudflared ===
[13:10:24] cloudflared 安装路径: /usr/local/bin/cloudflared
SSL: 跳过
[13:10:24] === STEP 6: 启动 Tunnel ===
[13:10:24] 下载 cloudflared...
 FAIL (DNS 传播中或配置错误)
[13:10:24] 尝试下载: https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
[13:10:24] --- DNS CNAME ---
DNS 更新: OK
[13:10:24] 设置 SSL 模式为 Full...
[13:10:24] --- DNS A ---
172.67.188.44
104.21.81.46
[13:10:24] === 部署汇总 ===
[13:10:24] Tunnel Mode: cert
[13:10:24] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:10:24] API: http://localhost:8450
[13:10:24] 域名: https://aishield.tools
[13:10:24] cloudflared: /usr/local/bin/cloudflared
[13:10:24] PID: 2523316
[13:10:24] Config: /root/.cloudflared/config.yml
[13:10:24] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:10:24] 状态: Named Tunnel (cert 模式) 已配置
[13:10:25] Tunnel 连接已建立!
[13:10:25] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T05:10:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T05:10:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T05:10:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T05:10:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T05:10:23Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-10T05:10:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-10T05:10:23Z INF Registered tunnel connection connIndex=0 connection=38cf2e18-8f01-466f-9230-15afbe12a90c event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-10T05:10:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.77
2026-08-10T05:10:24Z INF Initiating graceful shutdown due to signal terminated ...
2026-08-10T05:10:24Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.200.13
2026-08-10T05:10:24Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.13
2026-08-10T05:10:24Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.13
2026-08-10T05:10:24Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.13
2026-08-10T05:10:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
2026-08-10T05:10:25Z INF Registered tunnel connection connIndex=2 connection=544aa7fb-b7cd-4566-b06a-65437eb7811a event=0 ip=198.41.192.57 location=lax11 protocol=quic
[13:10:25] === STEP 7: 持久化 ===
SSL: 跳过
[13:10:25] === STEP 6: 启动 Tunnel ===
[13:10:25] 下载成功!
[13:10:26] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:10:26] === STEP 3: 检查认证方式 ===
[13:10:26] systemd 服务已配置
[13:10:26] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:10:26] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:10:26] 检查现有 tunnel...
[13:10:26] Cron 保活已设置
[13:10:26] === STEP 8: 验证 ===
[13:10:26] --- API (localhost:8450) ---
 OK
[13:10:26] --- cloudflared 进程 ---
root     2524118  0.0  1.5 1292804 31988 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2524140  0.0  1.4 1292740 29844 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel list
[13:10:26] --- aishield.tools ---
[13:10:26] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax08     
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[13:10:26] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:10:26] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:10:26] 凭证文件存在
[13:10:26] 创建 config.yml...
[13:10:26] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:10:26] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
 OK
[13:10:27] --- DNS CNAME ---
[13:10:27] --- DNS A ---
172.67.188.44
104.21.81.46
[13:10:27] === 部署汇总 ===
[13:10:27] Tunnel Mode: cert
[13:10:27] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:10:27] API: http://localhost:8450
[13:10:27] 域名: https://aishield.tools
[13:10:27] cloudflared: /usr/local/bin/cloudflared
[13:10:27] PID: 2523823
[13:10:27] Config: /root/.cloudflared/config.yml
[13:10:27] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:10:27] 状态: Named Tunnel (cert 模式) 已配置
[13:10:27] 启动 Named Tunnel (cert 模式)...
[13:10:27] 使用 config: /root/.cloudflared/config.yml
[13:10:27] cloudflared PID: 2524366
[13:10:28] DNS 路由结果: 2026-08-10T05:10:28Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:10:28] === STEP 5: 更新 DNS (API) ===
[13:10:28] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:10:28] 启动 Named Tunnel (cert 模式)...
[13:10:28] 使用 config: /root/.cloudflared/config.yml
[13:10:28] cloudflared PID: 2524509
[13:10:29] Tunnel 连接已建立!
[13:10:29] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T05:10:28Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T05:10:28Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T05:10:28Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T05:10:28Z INF Generated Connector ID: a4c3c682-9e69-4c01-a364-320691f05c1a
2026-08-10T05:10:28Z INF Initial protocol quic
2026-08-10T05:10:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T05:10:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T05:10:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T05:10:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T05:10:29Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-10T05:10:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-10T05:10:29Z INF Registered tunnel connection connIndex=0 connection=1502f407-9c02-485b-af95-6e0082c438a6 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-10T05:10:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-10T05:10:29Z INF Registered tunnel connection connIndex=1 connection=9e7fd39e-9568-41b6-8b0a-849e821d176b event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-10T05:10:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
[13:10:29] === STEP 7: 持久化 ===
[13:10:30] systemd 服务已配置
[13:10:30] Cron 保活已设置
[13:10:30] === STEP 8: 验证 ===
[13:10:30] --- API (localhost:8450) ---
 OK
[13:10:30] --- cloudflared 进程 ---
root     2524366  3.6  1.8 1294100 37472 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2524509  4.0  1.8 1293844 37376 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2524658  0.0  1.3 1292484 27492 ?       Rl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:10:30] --- aishield.tools ---
[13:10:30] Tunnel 连接已建立!
[13:10:30] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T05:10:28Z INF Generated Connector ID: a4c3c682-9e69-4c01-a364-320691f05c1a
2026-08-10T05:10:28Z INF Initial protocol quic
2026-08-10T05:10:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T05:10:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T05:10:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T05:10:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T05:10:29Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-10T05:10:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-10T05:10:29Z INF Registered tunnel connection connIndex=0 connection=1502f407-9c02-485b-af95-6e0082c438a6 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-10T05:10:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-10T05:10:30Z INF Registered tunnel connection connIndex=1 connection=73173256-d5a5-4a1d-a76a-9be80f583959 event=0 ip=198.41.192.37 location=lax05 protocol=quic
2026-08-10T05:10:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7

2026-08-10T05:10:30Z INF Registered tunnel connection connIndex=2 connection=816d89ad-dff5-4d25-a88d-79fc9a03d088 event=0 ip=198.41.192.77 location=lax07 protocol=quic
2026-08-10T05:10:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
[13:10:30] === STEP 7: 持久化 ===
[13:10:31] systemd 服务已配置
[13:10:31] Cron 保活已设置
[13:10:31] === STEP 8: 验证 ===
[13:10:31] --- API (localhost:8450) ---
 OK
[13:10:31] --- cloudflared 进程 ---
root     2524366  3.2  1.9 1294676 39360 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2524509  3.3  1.9 1294420 38368 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2524785  0.0  1.3 1292740 28104 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:10:31] --- aishield.tools ---
 OK
[13:10:31] --- DNS CNAME ---
[13:10:31] --- DNS A ---
104.21.81.46
172.67.188.44
[13:10:31] === 部署汇总 ===
[13:10:31] Tunnel Mode: cert
[13:10:31] Tunnel ID: You
[13:10:31] API: http://localhost:8450
[13:10:31] 域名: https://aishield.tools
[13:10:31] cloudflared: /usr/local/bin/cloudflared
[13:10:31] PID: 2524366
[13:10:31] Config: /root/.cloudflared/config.yml
[13:10:31] CNAME: You.cfargotunnel.com
[13:10:31] 状态: Named Tunnel (cert 模式) 已配置
[13:10:32] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:10:34] 设置 SSL 模式为 Full...
SSL: 跳过
[13:10:34] === STEP 6: 启动 Tunnel ===
 FAIL (DNS 传播中或配置错误)
[13:10:37] --- DNS CNAME ---
[13:10:37] --- DNS A ---
104.21.81.46
172.67.188.44
[13:10:37] === 部署汇总 ===
[13:10:37] Tunnel Mode: cert
[13:10:37] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:10:37] API: http://localhost:8450
[13:10:37] 域名: https://aishield.tools
[13:10:37] cloudflared: /usr/local/bin/cloudflared
[13:10:37] PID: 2524509
[13:10:37] Config: /root/.cloudflared/config.yml
[13:10:37] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:10:37] 状态: Named Tunnel (cert 模式) 已配置
[13:10:37] 启动 Named Tunnel (cert 模式)...
[13:10:37] 使用 config: /root/.cloudflared/config.yml
[13:10:37] cloudflared PID: 2525180
[13:10:39] Tunnel 连接已建立!
[13:10:39] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T05:10:37Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T05:10:37Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T05:10:37Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T05:10:37Z INF Generated Connector ID: 35cff49a-2967-4880-857d-c751023a30c7
2026-08-10T05:10:37Z INF Initial protocol quic
2026-08-10T05:10:37Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T05:10:37Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T05:10:37Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T05:10:37Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T05:10:37Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-10T05:10:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-08-10T05:10:38Z INF Registered tunnel connection connIndex=0 connection=b6b85012-e56e-40d6-9468-931972c78e91 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-10T05:10:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-10T05:10:39Z INF Registered tunnel connection connIndex=1 connection=6b7f48df-b979-463d-b1d4-03d22ea8e0f2 event=0 ip=198.41.192.27 location=lax07 protocol=quic
2026-08-10T05:10:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.37
[13:10:39] === STEP 7: 持久化 ===
[13:10:40] systemd 服务已配置
[13:10:40] Cron 保活已设置
[13:10:40] === STEP 8: 验证 ===
[13:10:40] --- API (localhost:8450) ---
 OK
[13:10:40] --- cloudflared 进程 ---
root     2525180  3.0  1.9 1294420 38932 ?       Sl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2525333  0.0  1.3 1292484 26576 ?       Rl   13:10   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:10:40] --- aishield.tools ---
 OK
[13:10:42] --- DNS CNAME ---
[13:10:42] --- DNS A ---
172.67.188.44
104.21.81.46
[13:10:42] === 部署汇总 ===
[13:10:42] Tunnel Mode: cert
[13:10:42] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:10:42] API: http://localhost:8450
[13:10:42] 域名: https://aishield.tools
[13:10:42] cloudflared: /usr/local/bin/cloudflared
[13:10:42] PID: 2525180
[13:10:42] Config: /root/.cloudflared/config.yml
[13:10:42] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:10:42] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-10 13:10:40 CST; 2min 34s ago
   Main PID: 2525325 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 16.7M
        CPU: 428ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2525325 /bin/bash /opt/start-tunnel.sh
             └─2525333 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 10 05:13:15 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786338795.7681003, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
