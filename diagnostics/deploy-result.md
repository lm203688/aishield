=== DIAGNOSTIC ===
Time: Fri Aug 28 07:15:23 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787872523.3687289, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2439095  0.1  1.7 1360284 35832 ?       Sl   06:39   0:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2439233  0.1  1.7 1294676 35576 ?       Sl   06:39   0:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-27T22:39:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
2026-08-27T22:39:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-27T22:39:33Z INF Registered tunnel connection connIndex=3 connection=c9b2d0fe-53f7-40ea-b858-97b5396fa4cc event=0 ip=198.41.192.47 location=lax12 protocol=quic
2026-08-27T22:39:37Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.193
2026-08-27T22:39:37Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.193
2026-08-27T22:39:37Z INF +-------------------------------------------------------------------------------------+
2026-08-27T22:39:37Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-27T22:39:37Z INF +-------------------------------------------------------------------------------------+
2026-08-27T22:39:37Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-27T22:39:37Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-27T22:39:37Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-27T22:39:37Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-27T22:39:37Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-27T22:39:37Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-27T22:39:37Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-27T22:39:37Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-27T22:39:37Z INF |                                                                                     |
2026-08-27T22:39:37Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-27T22:39:37Z INF +-------------------------------------------------------------------------------------+
2026-08-27T22:39:37Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f2753fb5-7e3e-4835-b986-391f22d0afd2 status=pass target=region1.v2.argotunnel.com
2026-08-27T22:39:37Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f2753fb5-7e3e-4835-b986-391f22d0afd2 status=pass target=region2.v2.argotunnel.com
2026-08-27T22:39:37Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f2753fb5-7e3e-4835-b986-391f22d0afd2 status=pass target=region1.v2.argotunnel.com
2026-08-27T22:39:37Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f2753fb5-7e3e-4835-b986-391f22d0afd2 status=pass target=region2.v2.argotunnel.com
2026-08-27T22:39:37Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f2753fb5-7e3e-4835-b986-391f22d0afd2 status=pass target=region1.v2.argotunnel.com
2026-08-27T22:39:37Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f2753fb5-7e3e-4835-b986-391f22d0afd2 status=pass target=region2.v2.argotunnel.com
2026-08-27T22:39:37Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f2753fb5-7e3e-4835-b986-391f22d0afd2 status=pass target=api.cloudflare.com:443
2026-08-27T22:39:37Z INF precheck complete hard_fail=false run_id=f2753fb5-7e3e-4835-b986-391f22d0afd2 suggested_protocol=quic
2026-08-27T22:39:37Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-27T22:39:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-08-27T22:39:47Z INF Registered tunnel connection connIndex=2 connection=427e22a7-4882-4fdf-9a6b-9f26010d454c event=0 ip=198.41.200.233 location=sjc07 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[06:37:14] Time: Fri Aug 28 06:37:14 AM CST 2026
[06:37:14] User: root (UID: 0)
[06:37:14] === STEP 1: 启动 API (端口 8450) ===
[06:37:27] API 已在运行
[06:37:27] API 状态: OK
[06:37:27] === STEP 2: 安装 cloudflared ===
[06:37:27] cloudflared 安装路径: /usr/local/bin/cloudflared
[06:37:27] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:37:27] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:37:27] === STEP 3: 检查认证方式 ===
[06:37:27] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[06:37:27] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[06:37:27] 检查现有 tunnel...
[06:37:28] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xlax07, 2xlax09, 2xsjc05, 1xsjc07, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-27T22:37:28Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[06:37:28] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:37:28] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[06:37:28] 凭证文件存在
[06:37:28] 创建 config.yml...
[06:37:28] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[06:37:28] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:37:29] DNS 路由结果: 2026-08-27T22:37:29Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[06:37:29] === STEP 5: 更新 DNS (API) ===
[06:37:29] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:37:30] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[06:37:31] 设置 SSL 模式为 Full...
SSL: 跳过
[06:37:31] === STEP 6: 启动 Tunnel ===
[06:37:34] 启动 Named Tunnel (cert 模式)...
[06:37:34] 使用 config: /root/.cloudflared/config.yml
[06:37:34] cloudflared PID: 2435814
[06:37:36] Tunnel 连接已建立!
[06:37:36] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T22:37:34Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-27T22:37:34Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-27T22:37:34Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-27T22:37:34Z INF Generated Connector ID: 79f38ed0-9253-4fac-93a7-3d0ae807a4e9
2026-08-27T22:37:34Z INF Initial protocol quic
2026-08-27T22:37:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:37:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:37:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:37:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:37:35Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-27T22:37:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-27T22:37:35Z INF Registered tunnel connection connIndex=0 connection=fffbfd11-2acd-4310-b77c-e79a76f6c1eb event=0 ip=198.41.200.13 location=sjc05 protocol=quic
2026-08-27T22:37:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-27T22:37:35Z INF Registered tunnel connection connIndex=1 connection=f0c17d65-6df4-45a6-b61e-72cdd732e9b9 event=0 ip=198.41.192.7 location=lax08 protocol=quic
2026-08-27T22:37:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[06:37:36] === STEP 7: 持久化 ===
[06:37:37] systemd 服务已配置
[06:37:37] Cron 保活已设置
[06:37:37] === STEP 8: 验证 ===
[06:37:37] --- API (localhost:8450) ---
 OK
[06:37:37] --- cloudflared 进程 ---
root     2435814  3.6  1.9 1294092 38528 ?       Sl   06:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2435952  0.0  1.3 1292740 27468 ?       Sl   06:37   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[06:37:37] --- aishield.tools ---
 OK
[06:37:39] --- DNS CNAME ---
[06:37:39] --- DNS A ---
104.21.81.46
172.67.188.44
[06:37:39] === 部署汇总 ===
[06:37:39] Tunnel Mode: cert
[06:37:39] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:37:39] API: http://localhost:8450
[06:37:39] 域名: https://aishield.tools
[06:37:39] cloudflared: /usr/local/bin/cloudflared
[06:37:39] PID: 2435814
[06:37:39] Config: /root/.cloudflared/config.yml
[06:37:39] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:37:39] 状态: Named Tunnel (cert 模式) 已配置
[06:38:30] API 已在运行
[06:38:30] API 状态: OK
[06:38:30] === STEP 2: 安装 cloudflared ===
[06:38:30] cloudflared 安装路径: /usr/local/bin/cloudflared
[06:38:30] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:38:30] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:38:30] === STEP 3: 检查认证方式 ===
[06:38:30] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[06:38:30] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[06:38:30] 检查现有 tunnel...
[06:38:31] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                            
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax07, 1xlax08, 1xlax10, 1xlax11, 1xsjc05, 1xsjc07, 1xsjc08, 1xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                                        
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                                        
[06:38:31] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:38:31] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[06:38:31] 凭证文件存在
[06:38:31] 创建 config.yml...
[06:38:31] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[06:38:31] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:38:32] DNS 路由结果: 2026-08-27T22:38:32Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[06:38:32] === STEP 5: 更新 DNS (API) ===
[06:38:32] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:38:33] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[06:38:33] API 已在运行
[06:38:33] API 状态: OK
[06:38:33] === STEP 2: 安装 cloudflared ===
[06:38:33] cloudflared 安装路径: /usr/local/bin/cloudflared
[06:38:33] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
DNS 更新: OK
[06:38:33] 设置 SSL 模式为 Full...
[06:38:33] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:38:33] === STEP 3: 检查认证方式 ===
[06:38:33] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[06:38:33] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[06:38:33] 检查现有 tunnel...
[06:38:34] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                            
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax07, 1xlax08, 1xlax10, 1xlax11, 1xsjc05, 1xsjc07, 1xsjc08, 1xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                                        
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                                        
2026-08-27T22:38:34Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[06:38:34] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:38:34] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[06:38:34] 凭证文件存在
[06:38:34] 创建 config.yml...
[06:38:34] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[06:38:34] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
SSL: 跳过
[06:38:34] === STEP 6: 启动 Tunnel ===
[06:38:34] DNS 路由结果: 
[06:38:34] === STEP 5: 更新 DNS (API) ===
[06:38:34] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:38:35] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[06:38:35] 设置 SSL 模式为 Full...
SSL: 跳过
[06:38:36] === STEP 6: 启动 Tunnel ===
[06:38:37] 启动 Named Tunnel (cert 模式)...
[06:38:37] 使用 config: /root/.cloudflared/config.yml
[06:38:37] cloudflared PID: 2437132
[06:38:39] 启动 Named Tunnel (cert 模式)...
[06:38:39] 使用 config: /root/.cloudflared/config.yml
[06:38:39] cloudflared PID: 2437188
[06:38:41] Tunnel 连接已建立!
[06:38:41] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T22:38:39Z INF Generated Connector ID: 8c27c619-239d-4b37-867f-c2464f9a78a5
2026-08-27T22:38:39Z INF Initial protocol quic
2026-08-27T22:38:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:38:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:38:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:38:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:38:39Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-27T22:38:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-27T22:38:40Z INF Registered tunnel connection connIndex=0 connection=2e7e56b4-7c0c-4bdc-9d83-bcef9d73664b event=0 ip=198.41.192.37 location=lax09 protocol=quic
2026-08-27T22:38:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-27T22:38:40Z INF Registered tunnel connection connIndex=1 connection=9bbe8edc-d794-4102-8a7b-8b85bed15b8a event=0 ip=198.41.200.33 location=sjc05 protocol=quic
2026-08-27T22:38:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-27T22:38:41Z INF Registered tunnel connection connIndex=2 connection=74058861-2091-42bd-b6ec-8c9fdf529f17 event=0 ip=198.41.200.63 location=sjc08 protocol=quic
26-08-27T22:38:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-08-27T22:38:40Z INF Registered tunnel connection connIndex=3 connection=3fc7471a-07bc-415a-8ab2-29c48d333091 event=0 ip=198.41.200.63 location=sjc07 protocol=quic
[06:38:41] === STEP 7: 持久化 ===
[06:38:41] Tunnel 连接已建立!
[06:38:41] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T22:38:39Z INF Generated Connector ID: 8c27c619-239d-4b37-867f-c2464f9a78a5
2026-08-27T22:38:39Z INF Initial protocol quic
2026-08-27T22:38:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:38:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:38:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:38:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:38:39Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-27T22:38:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-27T22:38:40Z INF Registered tunnel connection connIndex=0 connection=2e7e56b4-7c0c-4bdc-9d83-bcef9d73664b event=0 ip=198.41.192.37 location=lax09 protocol=quic
2026-08-27T22:38:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-27T22:38:40Z INF Registered tunnel connection connIndex=1 connection=9bbe8edc-d794-4102-8a7b-8b85bed15b8a event=0 ip=198.41.200.33 location=sjc05 protocol=quic
2026-08-27T22:38:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-27T22:38:41Z INF Registered tunnel connection connIndex=2 connection=74058861-2091-42bd-b6ec-8c9fdf529f17 event=0 ip=198.41.200.63 location=sjc08 protocol=quic
26-08-27T22:38:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-08-27T22:38:40Z INF Registered tunnel connection connIndex=3 connection=3fc7471a-07bc-415a-8ab2-29c48d333091 event=0 ip=198.41.200.63 location=sjc07 protocol=quic
[06:38:41] === STEP 7: 持久化 ===
[06:38:42] systemd 服务已配置
[06:38:42] Cron 保活已设置
[06:38:42] === STEP 8: 验证 ===
[06:38:42] systemd 服务已配置
[06:38:42] --- API (localhost:8450) ---
[06:38:42] Cron 保活已设置
[06:38:42] === STEP 8: 验证 ===
[06:38:42] --- API (localhost:8450) ---
 OK
[06:38:42] --- cloudflared 进程 ---
 OK
[06:38:42] --- cloudflared 进程 ---
root     2437132  2.0  1.9 1294420 39516 ?       Sl   06:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2437188  3.3  1.9 1294100 39212 ?       Sl   06:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2437388  0.0  1.3 1292740 27476 ?       Rl   06:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[06:38:42] --- aishield.tools ---
root     2437132  2.0  1.9 1294420 39516 ?       Sl   06:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2437188  3.3  1.9 1294100 39212 ?       Sl   06:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2437388  0.0  1.3 1292740 27476 ?       Rl   06:38   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[06:38:42] --- aishield.tools ---
 OK
[06:38:44] --- DNS CNAME ---
 OK
[06:38:44] --- DNS CNAME ---
[06:38:44] --- DNS A ---
[06:38:44] --- DNS A ---
172.67.188.44
104.21.81.46
[06:38:44] === 部署汇总 ===
[06:38:44] Tunnel Mode: cert
104.21.81.46
172.67.188.44
[06:38:44] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:38:44] API: http://localhost:8450
[06:38:44] === 部署汇总 ===
[06:38:44] 域名: https://aishield.tools
[06:38:44] cloudflared: /usr/local/bin/cloudflared
[06:38:44] Tunnel Mode: cert
[06:38:44] PID: 2437132
[06:38:44] Config: /root/.cloudflared/config.yml
[06:38:44] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:38:44] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:38:44] API: http://localhost:8450
[06:38:44] 域名: https://aishield.tools
[06:38:44] 状态: Named Tunnel (cert 模式) 已配置
[06:38:44] cloudflared: /usr/local/bin/cloudflared
[06:38:44] PID: 2437188
[06:38:44] Config: /root/.cloudflared/config.yml
[06:38:44] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:38:44] 状态: Named Tunnel (cert 模式) 已配置
[06:39:13] API 已在运行
[06:39:13] API 状态: OK
[06:39:13] === STEP 2: 安装 cloudflared ===
[06:39:13] cloudflared 安装路径: /usr/local/bin/cloudflared
[06:39:13] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:39:13] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:39:13] === STEP 3: 检查认证方式 ===
[06:39:13] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[06:39:13] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[06:39:13] 检查现有 tunnel...
[06:39:14] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                                     
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax08, 1xlax09, 1xlax10, 2xlax11, 1xsjc05, 1xsjc07, 3xsjc08, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                                                 
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                                                 
2026-08-27T22:39:14Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[06:39:14] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:39:14] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[06:39:14] 凭证文件存在
[06:39:14] 创建 config.yml...
[06:39:14] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[06:39:14] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:39:15] DNS 路由结果: 2026-08-27T22:39:15Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[06:39:15] === STEP 5: 更新 DNS (API) ===
[06:39:15] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:39:16] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[06:39:17] 设置 SSL 模式为 Full...
SSL: 跳过
[06:39:17] === STEP 6: 启动 Tunnel ===
[06:39:17] API 已在运行
[06:39:17] API 状态: OK
[06:39:17] === STEP 2: 安装 cloudflared ===
[06:39:17] cloudflared 安装路径: /usr/local/bin/cloudflared
[06:39:18] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:39:18] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:39:18] === STEP 3: 检查认证方式 ===
[06:39:18] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[06:39:18] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[06:39:18] 检查现有 tunnel...
[06:39:18] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
2026-08-27T22:39:18Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[06:39:18] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:39:18] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[06:39:18] 凭证文件存在
[06:39:18] 创建 config.yml...
[06:39:18] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[06:39:18] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:39:19] DNS 路由结果: 2026-08-27T22:39:19Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[06:39:19] === STEP 5: 更新 DNS (API) ===
[06:39:19] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:39:20] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[06:39:20] 启动 Named Tunnel (cert 模式)...
[06:39:20] 使用 config: /root/.cloudflared/config.yml
[06:39:20] cloudflared PID: 2438390
DNS 更新: OK
[06:39:20] 设置 SSL 模式为 Full...
SSL: 跳过
[06:39:21] === STEP 6: 启动 Tunnel ===
[06:39:22] Tunnel 连接已建立!
[06:39:22] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T22:39:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-27T22:39:21Z INF Registered tunnel connection connIndex=0 connection=884070d6-a177-4afc-a60c-41829a30a0db event=0 ip=198.41.200.113 location=sjc11 protocol=quic
2026-08-27T22:39:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.77
2026-08-27T22:39:21Z INF Initiating graceful shutdown due to signal terminated ...
2026-08-27T22:39:21Z INF Registered tunnel connection connIndex=1 connection=2a6c4d3d-e9e4-48de-bccd-6130635cfcef event=0 ip=198.41.192.77 location=lax05 protocol=quic
2026-08-27T22:39:21Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.200.113
2026-08-27T22:39:21Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-08-27T22:39:21Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-08-27T22:39:21Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.113
2026-08-27T22:39:21Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.192.77
2026-08-27T22:39:21Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.77
2026-08-27T22:39:21Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.77
2026-08-27T22:39:21Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.77
2026-08-27T22:39:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
2026-08-27T22:39:22Z INF Registered tunnel connection connIndex=2 connection=9c79ce8f-a817-472a-a587-234d9c8247eb event=0 ip=198.41.192.47 location=lax08 protocol=quic
[06:39:22] === STEP 7: 持久化 ===
[06:39:23] systemd 服务已配置
[06:39:23] Cron 保活已设置
[06:39:23] === STEP 8: 验证 ===
[06:39:23] --- API (localhost:8450) ---
 OK
[06:39:23] --- cloudflared 进程 ---
root     2438390  3.0  1.9 1294092 38844 ?       Sl   06:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2438505  0.0  1.3 1292740 27496 ?       Rl   06:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[06:39:23] --- aishield.tools ---
[06:39:23] API 已在运行
[06:39:23] API 状态: OK
[06:39:23] === STEP 2: 安装 cloudflared ===
[06:39:23] cloudflared 安装路径: /usr/local/bin/cloudflared
 FAIL (DNS 传播中或配置错误)
[06:39:23] --- DNS CNAME ---
[06:39:24] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:39:24] --- DNS A ---
172.67.188.44
104.21.81.46
[06:39:24] === 部署汇总 ===
[06:39:24] Tunnel Mode: cert
[06:39:24] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:39:24] API: http://localhost:8450
[06:39:24] 域名: https://aishield.tools
[06:39:24] cloudflared: /usr/local/bin/cloudflared
[06:39:24] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:39:24] PID: 2438390
[06:39:24] === STEP 3: 检查认证方式 ===
[06:39:24] Config: /root/.cloudflared/config.yml
[06:39:24] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[06:39:24] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[06:39:24] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:39:24] 检查现有 tunnel...
[06:39:24] 状态: Named Tunnel (cert 模式) 已配置
[06:39:24] 启动 Named Tunnel (cert 模式)...
[06:39:24] 使用 config: /root/.cloudflared/config.yml
[06:39:24] cloudflared PID: 2438690
[06:39:24] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS      
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax11, 1xsjc05 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                  
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                  
[06:39:24] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:39:24] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[06:39:24] 凭证文件存在
[06:39:24] 创建 config.yml...
[06:39:24] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[06:39:24] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:39:25] DNS 路由结果: 2026-08-27T22:39:25Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[06:39:25] === STEP 5: 更新 DNS (API) ===
[06:39:25] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:39:26] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[06:39:26] Tunnel 连接已建立!
[06:39:26] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T22:39:24Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-27T22:39:24Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-27T22:39:24Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-27T22:39:24Z INF Generated Connector ID: 15ece0fa-cb2e-44fc-bad9-e94dddc594cf
2026-08-27T22:39:24Z INF Initial protocol quic
2026-08-27T22:39:24Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:39:24Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:39:24Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:39:24Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:39:24Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-27T22:39:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-27T22:39:25Z INF Registered tunnel connection connIndex=0 connection=89e983a2-5001-4d0c-b482-5440feb359c2 event=0 ip=198.41.200.43 location=sjc07 protocol=quic
2026-08-27T22:39:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
2026-08-27T22:39:25Z INF Registered tunnel connection connIndex=1 connection=2fd64032-355d-4a0b-9056-3b0151eeaa12 event=0 ip=198.41.192.227 location=lax09 protocol=quic
2026-08-27T22:39:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[06:39:26] === STEP 7: 持久化 ===
DNS 更新: OK
[06:39:27] 设置 SSL 模式为 Full...
[06:39:27] systemd 服务已配置
[06:39:27] Cron 保活已设置
[06:39:27] === STEP 8: 验证 ===
[06:39:27] --- API (localhost:8450) ---
 OK
[06:39:27] --- cloudflared 进程 ---
root     2438690  3.3  1.9 1294420 39396 ?       Sl   06:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2438921  0.0  1.3 1292740 28116 ?       Sl   06:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[06:39:27] --- aishield.tools ---
SSL: 跳过
[06:39:27] === STEP 6: 启动 Tunnel ===
 FAIL (DNS 传播中或配置错误)
[06:39:28] --- DNS CNAME ---
[06:39:28] --- DNS A ---
172.67.188.44
104.21.81.46
[06:39:28] === 部署汇总 ===
[06:39:28] Tunnel Mode: cert
[06:39:28] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:39:28] API: http://localhost:8450
[06:39:28] 域名: https://aishield.tools
[06:39:28] cloudflared: /usr/local/bin/cloudflared
[06:39:28] PID: 2438690
[06:39:28] Config: /root/.cloudflared/config.yml
[06:39:28] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:39:28] 状态: Named Tunnel (cert 模式) 已配置
[06:39:30] 启动 Named Tunnel (cert 模式)...
[06:39:30] 使用 config: /root/.cloudflared/config.yml
[06:39:30] cloudflared PID: 2439095
[06:39:32] Tunnel 连接已建立!
[06:39:32] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T22:39:30Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T22:39:30Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T22:39:30Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-27T22:39:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.7
2026-08-27T22:39:31Z INF Registered tunnel connection connIndex=0 connection=d411c5f9-53ae-413e-94ec-7b3c93e9d264 event=0 ip=198.41.192.7 location=lax10 protocol=quic
2026-08-27T22:39:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-27T22:39:31Z INF Registered tunnel connection connIndex=1 connection=5d7ba47d-bf73-473d-ad37-e8f88dedefd0 event=0 ip=198.41.200.63 location=sjc07 protocol=quic
2026-08-27T22:39:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             2026-08-27T22:39:31Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.73
2026-08-27T22:39:31Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.73
2026-08-27T22:39:31Z ERR Connection terminated connIndex=2
2026-08-27T22:39:31Z ERR no more connections active and exiting
2026-08-27T22:39:31Z INF Tunnel server stopped
2026-08-27T22:39:31Z INF Metrics server stopped
2026-08-27T22:39:31Z ERR icmp router terminated error="context canceled"
[06:39:32] === STEP 7: 持久化 ===
[06:39:33] systemd 服务已配置
[06:39:33] Cron 保活已设置
[06:39:33] === STEP 8: 验证 ===
[06:39:33] --- API (localhost:8450) ---
 OK
[06:39:33] --- cloudflared 进程 ---
root     2439095  3.6  1.9 1359700 39020 ?       Sl   06:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2439233  0.0  1.3 1292740 27604 ?       Rl   06:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[06:39:33] --- aishield.tools ---
 OK
[06:39:34] --- DNS CNAME ---
[06:39:35] --- DNS A ---
172.67.188.44
104.21.81.46
[06:39:35] === 部署汇总 ===
[06:39:35] Tunnel Mode: cert
[06:39:35] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[06:39:35] API: http://localhost:8450
[06:39:35] 域名: https://aishield.tools
[06:39:35] cloudflared: /usr/local/bin/cloudflared
[06:39:35] PID: 2439095
[06:39:35] Config: /root/.cloudflared/config.yml
[06:39:35] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[06:39:35] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 06:39:33 CST; 35min ago
   Main PID: 2439225 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 16.7M
        CPU: 3.609s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2439225 /bin/bash /opt/start-tunnel.sh
             └─2439233 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2525069,fd=3))                                                    
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
Time: Thu Aug 27 23:15:24 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787872524.3896103, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
