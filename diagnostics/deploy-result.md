=== DIAGNOSTIC ===
Time: Sat Aug 15 05:12:46 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786741966.8629842, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2728934  0.1  1.7 1294676 34948 ?       Sl   04:59   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2729346  0.1  1.7 1360284 34760 ?       Sl   04:59   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T20:59:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-14T20:59:58Z INF +-------------------------------------------------------------------------------------+
2026-08-14T20:59:58Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-14T20:59:58Z INF +-------------------------------------------------------------------------------------+
2026-08-14T20:59:58Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-14T20:59:58Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T20:59:58Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T20:59:58Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T20:59:58Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T20:59:58Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T20:59:58Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T20:59:58Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-14T20:59:58Z INF |                                                                                     |
2026-08-14T20:59:58Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-14T20:59:58Z INF +-------------------------------------------------------------------------------------+
2026-08-14T20:59:58Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region1.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region2.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region1.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region2.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region1.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region2.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="Cloudflare API" details="API is reachable" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=api.cloudflare.com:443
2026-08-14T20:59:58Z INF precheck complete hard_fail=false run_id=00793cca-a346-4abf-9796-56b35fcdaa20 suggested_protocol=quic
2026-08-14T20:59:58Z INF Registered tunnel connection connIndex=0 connection=16371958-f244-4368-8b06-2e14078d2bf6 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-14T20:59:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-14T20:59:58Z INF Registered tunnel connection connIndex=1 connection=ea60654c-e4dc-4163-82fa-57e91a0aa596 event=0 ip=198.41.192.47 location=lax09 protocol=quic
2026-08-14T20:59:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-14T20:59:59Z INF Registered tunnel connection connIndex=2 connection=49fc5fa4-3d0b-4072-b159-c10f266f2a63 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-14T21:00:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.27
2026-08-14T21:00:00Z INF Registered tunnel connection connIndex=3 connection=089f1efa-e41f-49dc-838b-29a86594b2cd event=0 ip=198.41.192.27 location=lax08 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[04:59:43] Time: Sat Aug 15 04:59:43 AM CST 2026
[04:59:43] User: root (UID: 0)
[04:59:43] === STEP 1: 启动 API (端口 8450) ===
SSL: 跳过
[04:59:43] === STEP 6: 启动 Tunnel ===
[04:59:44] API 已在运行
[04:59:44] API 状态: OK
[04:59:44] === STEP 2: 安装 cloudflared ===
[04:59:44] cloudflared 安装路径: /usr/local/bin/cloudflared
[04:59:44] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[04:59:45] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[04:59:45] === STEP 3: 检查认证方式 ===
[04:59:45] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[04:59:45] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[04:59:45] 检查现有 tunnel...
[04:59:45] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[04:59:45] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[04:59:45] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[04:59:45] 凭证文件存在
[04:59:45] 创建 config.yml...
[04:59:45] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[04:59:45] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[04:59:45] 启动 Named Tunnel (cert 模式)...
[04:59:45] 使用 config: /root/.cloudflared/config.yml
[04:59:45] cloudflared PID: 2728316
[04:59:46] DNS 路由结果: 2026-08-14T20:59:46Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[04:59:46] === STEP 5: 更新 DNS (API) ===
[04:59:46] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[04:59:46] 启动 Named Tunnel (cert 模式)...
[04:59:46] 使用 config: /root/.cloudflared/config.yml
[04:59:46] cloudflared PID: 2728373
[04:59:47] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[04:59:47] Tunnel 连接已建立!
[04:59:47] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T20:59:46Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-14T20:59:46Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-14T20:59:46Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T20:59:46Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T20:59:46Z INF Generated Connector ID: a801ca80-1e7b-4fbe-885e-7853f82e6fa6
2026-08-14T20:59:46Z INF Initial protocol quic
2026-08-14T20:59:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T20:59:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T20:59:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T20:59:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T20:59:46Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-14T20:59:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-14T20:59:47Z INF Registered tunnel connection connIndex=0 connection=39f3edc2-0d1c-406f-a3e2-db1f9cdd3c19 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-14T20:59:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-14T20:59:47Z INF Registered tunnel connection connIndex=1 connection=8e9cb159-1c1a-4941-97cf-acc8580d3f26 event=0 ip=198.41.192.67 location=lax08 protocol=quic
[04:59:47] === STEP 7: 持久化 ===
[04:59:47] Tunnel 连接已建立!
[04:59:47] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T20:59:46Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-14T20:59:46Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-14T20:59:46Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T20:59:46Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T20:59:46Z INF Generated Connector ID: a801ca80-1e7b-4fbe-885e-7853f82e6fa6
2026-08-14T20:59:46Z INF Initial protocol quic
2026-08-14T20:59:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T20:59:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T20:59:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T20:59:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T20:59:46Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-14T20:59:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-14T20:59:47Z INF Registered tunnel connection connIndex=0 connection=39f3edc2-0d1c-406f-a3e2-db1f9cdd3c19 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-14T20:59:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-14T20:59:47Z INF Registered tunnel connection connIndex=1 connection=8e9cb159-1c1a-4941-97cf-acc8580d3f26 event=0 ip=198.41.192.67 location=lax08 protocol=quic
[04:59:47] === STEP 7: 持久化 ===
DNS 更新: OK
[04:59:48] 设置 SSL 模式为 Full...
SSL: 跳过
[04:59:48] === STEP 6: 启动 Tunnel ===
[04:59:48] Tunnel 连接已建立!
[04:59:48] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T20:59:46Z INF Initial protocol quic
2026-08-14T20:59:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T20:59:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T20:59:46Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T20:59:46Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T20:59:46Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-14T20:59:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.1132026-08-14T20:59:48Z INF Initiating graceful shutdown due to signal terminated ...
2026-08-14T20:59:48Z INF Tunnel server stopped
2026-08-14T20:59:48Z ERR icmp router terminated error="context canceled"
2026-08-14T20:59:48Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: context canceled" connIndex=0 event=0 ip=198.41.200.73
2026-08-14T20:59:48Z INF Metrics server stopped
1-97cf-acc8580d3f26 event=0 ip=198.41.192.67 location=lax08 protocol=quic
2026-08-14T20:59:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-14T20:59:48Z INF Registered tunnel connection connIndex=2 connection=c5850247-c664-4ddb-a8f8-4fda0a5bd2f1 event=0 ip=198.41.192.77 location=lax07 protocol=quic
2026-08-14T20:59:48Z INF Initiating graceful shutdown due to signal terminated ...
[04:59:48] === STEP 7: 持久化 ===
[04:59:49] systemd 服务已配置
[04:59:49] systemd 服务已配置
[04:59:49] systemd 服务已配置
[04:59:49] Cron 保活已设置
[04:59:49] === STEP 8: 验证 ===
[04:59:49] Cron 保活已设置
[04:59:49] Cron 保活已设置
[04:59:49] --- API (localhost:8450) ---
[04:59:49] === STEP 8: 验证 ===
[04:59:49] === STEP 8: 验证 ===
[04:59:49] --- API (localhost:8450) ---
[04:59:49] --- API (localhost:8450) ---
 OK
 OK
[04:59:49] --- cloudflared 进程 ---
 OK
[04:59:49] --- cloudflared 进程 ---
[04:59:49] --- cloudflared 进程 ---
root     2728373  3.6  1.8 1294676 37664 ?       Sl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2728652  0.0  1.3 1292484 26700 ?       Rl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2728373  3.6  1.8 1294676 37664 ?       Sl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2728652  0.0  1.3 1292484 26700 ?       Rl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[04:59:49] --- aishield.tools ---
root     2728373  3.6  1.8 1294676 37664 ?       Sl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2728652  0.0  1.3 1292484 26700 ?       Rl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[04:59:49] --- aishield.tools ---
[04:59:49] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[04:59:50] --- DNS CNAME ---
 FAIL (DNS 传播中或配置错误)
[04:59:50] --- DNS CNAME ---
[04:59:50] --- DNS A ---
104.21.81.46
172.67.188.44
[04:59:50] === 部署汇总 ===
[04:59:50] Tunnel Mode: cert
[04:59:50] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[04:59:50] API: http://localhost:8450
[04:59:50] 域名: https://aishield.tools
[04:59:50] cloudflared: /usr/local/bin/cloudflared
[04:59:50] PID: 2728070
[04:59:50] Config: /root/.cloudflared/config.yml
[04:59:50] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[04:59:50] 状态: Named Tunnel (cert 模式) 已配置
 FAIL (DNS 传播中或配置错误)
[04:59:50] --- DNS CNAME ---
[04:59:50] --- DNS A ---
[04:59:50] --- DNS A ---
104.21.81.46
172.67.188.44
[04:59:50] === 部署汇总 ===
[04:59:50] Tunnel Mode: cert
104.21.81.46
172.67.188.44
[04:59:50] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[04:59:50] API: http://localhost:8450
[04:59:50] === 部署汇总 ===
[04:59:50] 域名: https://aishield.tools
[04:59:50] cloudflared: /usr/local/bin/cloudflared
[04:59:50] Tunnel Mode: cert
[04:59:50] PID: 2728373
[04:59:50] Config: /root/.cloudflared/config.yml
[04:59:50] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[04:59:50] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[04:59:50] 状态: Named Tunnel (cert 模式) 已配置
[04:59:50] API: http://localhost:8450
[04:59:50] 域名: https://aishield.tools
[04:59:50] cloudflared: /usr/local/bin/cloudflared
[04:59:50] PID: 2728316
[04:59:50] Config: /root/.cloudflared/config.yml
[04:59:50] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[04:59:50] 状态: Named Tunnel (cert 模式) 已配置
[04:59:51] 启动 Named Tunnel (cert 模式)...
[04:59:51] 使用 config: /root/.cloudflared/config.yml
[04:59:51] cloudflared PID: 2728934
[04:59:59] Tunnel 连接已建立!
[04:59:59] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T20:59:58Z INF |                                                                                     |
2026-08-14T20:59:58Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-14T20:59:58Z INF +-------------------------------------------------------------------------------------+
2026-08-14T20:59:58Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region1.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region2.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region1.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region2.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region1.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=region2.v2.argotunnel.com
2026-08-14T20:59:58Z INF precheck component="Cloudflare API" details="API is reachable" run_id=00793cca-a346-4abf-9796-56b35fcdaa20 status=pass target=api.cloudflare.com:443
2026-08-14T20:59:58Z INF precheck complete hard_fail=false run_id=00793cca-a346-4abf-9796-56b35fcdaa20 suggested_protocol=quic
2026-08-14T20:59:58Z INF Registered tunnel connection connIndex=0 connection=16371958-f244-4368-8b06-2e14078d2bf6 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-14T20:59:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-14T20:59:58Z INF Registered tunnel connection connIndex=1 connection=ea60654c-e4dc-4163-82fa-57e91a0aa596 event=0 ip=198.41.192.47 location=lax09 protocol=quic
2026-08-14T20:59:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
[04:59:59] === STEP 7: 持久化 ===
[05:00:00] systemd 服务已配置
[05:00:00] Cron 保活已设置
[05:00:00] === STEP 8: 验证 ===
[05:00:00] --- API (localhost:8450) ---
 OK
[05:00:00] --- cloudflared 进程 ---
root     2728934  1.1  1.9 1294676 39044 ?       Sl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2729346  0.0  1.3 1292484 27588 ?       Sl   04:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[05:00:00] --- aishield.tools ---
 OK
[05:00:01] --- DNS CNAME ---
[05:00:01] --- DNS A ---
172.67.188.44
104.21.81.46
[05:00:01] === 部署汇总 ===
[05:00:01] Tunnel Mode: cert
[05:00:01] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[05:00:01] API: http://localhost:8450
[05:00:01] 域名: https://aishield.tools
[05:00:01] cloudflared: /usr/local/bin/cloudflared
[05:00:01] PID: 2728934
[05:00:01] Config: /root/.cloudflared/config.yml
[05:00:01] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[05:00:01] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-15 05:00:00 CST; 12min ago
   Main PID: 2729338 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 15.7M
        CPU: 1.172s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2729338 /bin/bash /opt/start-tunnel.sh
             └─2729346 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 21:12:47 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786741967.528013, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
