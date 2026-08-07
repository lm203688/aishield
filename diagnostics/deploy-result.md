=== DIAGNOSTIC ===
Time: Fri Aug 7 09:39:11 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786066751.0905735, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3445705  0.1  1.7 1294676 35816 ?       Sl   07:19   0:13 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3445913  0.1  1.7 1294676 35600 ?       Sl   07:19   0:13 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-06T23:19:13Z INF Registered tunnel connection connIndex=0 connection=90874925-b5d4-4f8f-aaed-de8bacfb53cd event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-06T23:19:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-06T23:19:14Z INF Registered tunnel connection connIndex=1 connection=38fb4c12-52b5-4326-87c8-8a3e69a83fe5 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-06T23:19:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
2026-08-06T23:19:14Z INF Registered tunnel connection connIndex=2 connection=0e74d7ef-3b9b-4a39-879b-7c021dad44b1 event=0 ip=198.41.192.67 location=lax10 protocol=quic
2026-08-06T23:19:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-06T23:19:15Z INF Registered tunnel connection connIndex=3 connection=93910cac-0765-4d61-92e3-4406c8a253cc event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-06T23:19:16Z INF +-----------------------------------------------------------------------------------------------+
2026-08-06T23:19:16Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-06T23:19:16Z INF +-----------------------------------------------------------------------------------------------+
2026-08-06T23:19:16Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-06T23:19:16Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-06T23:19:16Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-06T23:19:16Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-06T23:19:16Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-06T23:19:16Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-06T23:19:16Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-06T23:19:16Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-06T23:19:16Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-06T23:19:16Z INF |                                                                                               |
2026-08-06T23:19:16Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-06T23:19:16Z INF +-----------------------------------------------------------------------------------------------+
2026-08-06T23:19:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=43d1b262-f83a-41fa-b17f-17f7ed82a888 status=pass target=region1.v2.argotunnel.com
2026-08-06T23:19:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=43d1b262-f83a-41fa-b17f-17f7ed82a888 status=pass target=region2.v2.argotunnel.com
2026-08-06T23:19:16Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=43d1b262-f83a-41fa-b17f-17f7ed82a888 status=pass target=region1.v2.argotunnel.com
2026-08-06T23:19:16Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=43d1b262-f83a-41fa-b17f-17f7ed82a888 status=fail target=region2.v2.argotunnel.com
2026-08-06T23:19:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=43d1b262-f83a-41fa-b17f-17f7ed82a888 status=pass target=region1.v2.argotunnel.com
2026-08-06T23:19:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=43d1b262-f83a-41fa-b17f-17f7ed82a888 status=pass target=region2.v2.argotunnel.com
2026-08-06T23:19:16Z INF precheck component="Cloudflare API" details="API is reachable" run_id=43d1b262-f83a-41fa-b17f-17f7ed82a888 status=pass target=api.cloudflare.com:443
2026-08-06T23:19:16Z INF precheck complete hard_fail=false run_id=43d1b262-f83a-41fa-b17f-17f7ed82a888 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[07:16:46] Time: Fri Aug  7 07:16:46 AM CST 2026
[07:16:46] User: root (UID: 0)
[07:16:46] === STEP 1: 启动 API (端口 8450) ===
[07:16:57] API 已在运行
[07:16:57] API 状态: OK
[07:16:57] === STEP 2: 安装 cloudflared ===
[07:16:57] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:16:57] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:16:57] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:16:57] === STEP 3: 检查认证方式 ===
[07:16:57] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[07:16:57] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[07:16:57] 检查现有 tunnel...
[07:16:58] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 3xlax07 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[07:16:58] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:16:58] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[07:16:58] 凭证文件存在
[07:16:58] 创建 config.yml...
[07:16:58] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[07:16:58] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:16:59] DNS 路由结果: 2026-08-06T23:16:59Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[07:16:59] === STEP 5: 更新 DNS (API) ===
[07:16:59] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:00] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[07:17:00] 设置 SSL 模式为 Full...
[07:17:01] API 已在运行
[07:17:01] API 状态: OK
[07:17:01] === STEP 2: 安装 cloudflared ===
[07:17:01] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:17:01] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:17:01] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:17:01] === STEP 3: 检查认证方式 ===
[07:17:01] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[07:17:01] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[07:17:01] 检查现有 tunnel...
SSL: 跳过
[07:17:01] === STEP 6: 启动 Tunnel ===
[07:17:01] 现有 tunnel 列表:

[07:17:01] 创建新 tunnel: aishield-tunnel
[07:17:01] API 已在运行
[07:17:01] API 状态: OK
[07:17:01] === STEP 2: 安装 cloudflared ===
[07:17:01] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:17:02] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:17:02] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:17:02] === STEP 3: 检查认证方式 ===
[07:17:02] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[07:17:02] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[07:17:02] 检查现有 tunnel...
[07:17:02] 创建输出: failed to create tunnel: Create Tunnel API call failed: tunnel with name already exists
[07:17:02] Tunnel 创建失败，尝试其他方法...
[07:17:02] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[07:17:02] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:02] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[07:17:02] 凭证文件存在
[07:17:02] 创建 config.yml...
[07:17:02] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[07:17:02] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:03] 使用第一个可用 tunnel: You
[07:17:03] 凭证文件: /root/.cloudflared/You.json
[07:17:03] 凭证文件不存在，列出 .cloudflared 目录内容:
total 24
drwxr-xr-x 2 root root 4096 Jul 31 07:21 .
drwx------ 8 root root 4096 Jul 28 11:01 ..
-r-------- 1 root root  175 Jul 31 07:21 0c39bcfb-0c96-4858-9025-d54131e062ec.json
-r-------- 1 root root  175 Jul 28 11:03 aa3f86b8-01f4-4ce0-83a8-5512219f9003.json
-rw------- 1 root root  282 Jul 28 11:02 cert.pem
-rw-r--r-- 1 root root  227 Aug  7 07:17 config.yml
[07:17:03] 创建 config.yml...
[07:17:03] config.yml 已创建:
tunnel: You
credentials-file: /root/.cloudflared/You.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[07:17:03] 路由 DNS: aishield.tools -> You.cfargotunnel.com
[07:17:04] DNS 路由结果: 2026-08-06T23:17:04Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:04] === STEP 5: 更新 DNS (API) ===
[07:17:04] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:04] DNS 路由结果: 2026-08-06T23:17:04Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:04] === STEP 5: 更新 DNS (API) ===
[07:17:04] CNAME: aishield.tools -> You.cfargotunnel.com
[07:17:04] 启动 Named Tunnel (cert 模式)...
[07:17:04] 使用 config: /root/.cloudflared/config.yml
[07:17:04] cloudflared PID: 3442383
[07:17:04] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[07:17:05] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[07:17:05] 设置 SSL 模式为 Full...
DNS 更新: OK
[07:17:05] 设置 SSL 模式为 Full...
SSL: 跳过
[07:17:06] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[07:17:06] === STEP 6: 启动 Tunnel ===
[07:17:09] 启动 Named Tunnel (cert 模式)...
[07:17:09] 使用 config: /root/.cloudflared/config.yml
[07:17:09] cloudflared PID: 3442490
[07:17:09] 启动 Named Tunnel (cert 模式)...
[07:17:09] 使用 config: /root/.cloudflared/config.yml
[07:17:09] cloudflared PID: 3442507
[07:17:14] 等待 tunnel 连接... (10s)
[07:17:19] 等待 tunnel 连接... (10s)
[07:17:19] 等待 tunnel 连接... (10s)
[07:17:24] API 已在运行
[07:17:24] API 状态: OK
[07:17:24] === STEP 2: 安装 cloudflared ===
[07:17:24] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:17:24] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:17:24] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:17:24] === STEP 3: 检查认证方式 ===
[07:17:24] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[07:17:24] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[07:17:24] 检查现有 tunnel...
[07:17:24] 等待 tunnel 连接... (20s)
[07:17:25] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[07:17:25] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:25] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[07:17:25] 凭证文件存在
[07:17:25] 创建 config.yml...
[07:17:25] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[07:17:25] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:29] DNS 路由结果: 2026-08-06T23:17:29Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:29] === STEP 5: 更新 DNS (API) ===
[07:17:29] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:29] 等待 tunnel 连接... (20s)
[07:17:29] 等待 tunnel 连接... (20s)
[07:17:29] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[07:17:30] 设置 SSL 模式为 Full...
SSL: 跳过
[07:17:30] === STEP 6: 启动 Tunnel ===
[07:17:33] 启动 Named Tunnel (cert 模式)...
[07:17:33] 使用 config: /root/.cloudflared/config.yml
[07:17:33] cloudflared PID: 3443107
[07:17:34] Tunnel 连接已建立!
[07:17:34] --- cloudflared 日志 (最后 15 行) ---
2026-08-06T23:17:34Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-06T23:17:34Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-06T23:17:34Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-06T23:17:34Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-06T23:17:34Z INF Generated Connector ID: 047fc907-31db-42d4-81c2-2cd2022d7d27
2026-08-06T23:17:34Z INF Initial protocol quic
2026-08-06T23:17:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:17:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:17:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:17:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:17:34Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-06T23:17:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-06T23:17:34Z INF Registered tunnel connection connIndex=0 connection=d8ce8df5-bcc9-47e2-a49d-c40ad2818642 event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-06T23:17:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-06T23:17:34Z INF Registered tunnel connection connIndex=1 connection=baa95e3a-a3a4-4699-a45f-1dcecddf19a3 event=0 ip=198.41.200.63 location=lax01 protocol=quic
[07:17:34] === STEP 7: 持久化 ===
[07:17:35] Tunnel 连接已建立!
[07:17:35] --- cloudflared 日志 (最后 15 行) ---
2026-08-06T23:17:34Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-06T23:17:34Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-06T23:17:34Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-06T23:17:34Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-06T23:17:34Z INF Generated Connector ID: 047fc907-31db-42d4-81c2-2cd2022d7d27
2026-08-06T23:17:34Z INF Initial protocol quic
2026-08-06T23:17:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:17:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:17:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:17:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:17:34Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-06T23:17:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-06T23:17:34Z INF Registered tunnel connection connIndex=0 connection=d8ce8df5-bcc9-47e2-a49d-c40ad2818642 event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-06T23:17:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-06T23:17:34Z INF Registered tunnel connection connIndex=1 connection=baa95e3a-a3a4-4699-a45f-1dcecddf19a3 event=0 ip=198.41.200.63 location=lax01 protocol=quic
[07:17:35] === STEP 7: 持久化 ===
[07:17:35] Tunnel 连接已建立!
[07:17:35] --- cloudflared 日志 (最后 15 行) ---
2026-08-06T23:17:34Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-06T23:17:34Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-06T23:17:34Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-06T23:17:34Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-06T23:17:34Z INF Generated Connector ID: 047fc907-31db-42d4-81c2-2cd2022d7d27
2026-08-06T23:17:34Z INF Initial protocol quic
2026-08-06T23:17:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:17:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:17:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:17:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:17:34Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-06T23:17:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-06T23:17:34Z INF Registered tunnel connection connIndex=0 connection=d8ce8df5-bcc9-47e2-a49d-c40ad2818642 event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-06T23:17:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-06T23:17:34Z INF Registered tunnel connection connIndex=1 connection=baa95e3a-a3a4-4699-a45f-1dcecddf19a3 event=0 ip=198.41.200.63 location=lax01 protocol=quic
[07:17:35] === STEP 7: 持久化 ===
[07:17:35] Tunnel 连接已建立!
[07:17:35] --- cloudflared 日志 (最后 15 行) ---
2026-08-06T23:17:34Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-06T23:17:34Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-06T23:17:34Z INF Generated Connector ID: 047fc907-31db-42d4-81c2-2cd2022d7d27
2026-08-06T23:17:34Z INF Initial protocol quic
2026-08-06T23:17:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:17:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:17:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:17:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:17:34Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-06T23:17:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-06T23:17:34Z INF Registered tunnel connection connIndex=0 connection=d8ce8df5-bcc9-47e2-a49d-c40ad2818642 event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-08-06T23:17:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-06T23:17:34Z INF Registered tunnel connection connIndex=1 connection=baa95e3a-a3a4-4699-a45f-1dcecddf19a3 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-06T23:17:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-06T23:17:35Z INF Registered tunnel connection connIndex=2 connection=36ddca8d-31d7-4b54-be72-235cae97a842 event=0 ip=198.41.200.113 location=lax01 protocol=quic
[07:17:35] === STEP 7: 持久化 ===
[07:17:36] systemd 服务已配置
[07:17:36] systemd 服务已配置
[07:17:36] systemd 服务已配置
[07:17:36] Cron 保活已设置
[07:17:36] Cron 保活已设置
[07:17:36] Cron 保活已设置
[07:17:36] === STEP 8: 验证 ===
[07:17:36] === STEP 8: 验证 ===
[07:17:36] --- API (localhost:8450) ---
[07:17:36] === STEP 8: 验证 ===
[07:17:36] --- API (localhost:8450) ---
[07:17:36] --- API (localhost:8450) ---
 OK
 OK
 OK
[07:17:36] --- cloudflared 进程 ---
[07:17:36] --- cloudflared 进程 ---
[07:17:36] --- cloudflared 进程 ---
root     3443107  3.0  1.9 1294092 38968 ?       Sl   07:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3443364  0.0  1.8 1293836 36292 ?       Sl   07:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3443107  3.0  1.9 1294092 38968 ?       Sl   07:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3443364  0.0  1.8 1293836 36292 ?       Sl   07:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3443107  3.0  1.9 1294092 38968 ?       Sl   07:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3443364  0.0  1.8 1293836 36292 ?       Rl   07:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[07:17:37] --- aishield.tools ---
[07:17:37] --- aishield.tools ---
[07:17:37] --- aishield.tools ---
[07:17:37] systemd 服务已配置
[07:17:37] Cron 保活已设置
[07:17:37] === STEP 8: 验证 ===
[07:17:37] --- API (localhost:8450) ---
 OK
[07:17:37] --- cloudflared 进程 ---
root     3443107  2.2  1.9 1294092 39484 ?       Sl   07:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3443537  0.0  1.3 1292740 27176 ?       Rl   07:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[07:17:37] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[07:17:37] --- DNS CNAME ---
 FAIL (DNS 传播中或配置错误)
[07:17:37] --- DNS CNAME ---
 FAIL (DNS 传播中或配置错误)
[07:17:37] --- DNS CNAME ---
[07:17:37] --- DNS A ---
[07:17:37] --- DNS A ---
[07:17:37] --- DNS A ---
104.21.81.46
172.67.188.44
172.67.188.44
104.21.81.46
[07:17:37] === 部署汇总 ===
[07:17:37] Tunnel Mode: cert
[07:17:37] === 部署汇总 ===
[07:17:37] Tunnel ID: You
[07:17:37] API: http://localhost:8450
[07:17:37] Tunnel Mode: cert
[07:17:37] 域名: https://aishield.tools
[07:17:37] cloudflared: /usr/local/bin/cloudflared
[07:17:37] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:37] PID: 3442507
[07:17:37] API: http://localhost:8450
172.67.188.44
104.21.81.46
[07:17:37] Config: /root/.cloudflared/config.yml
[07:17:37] 域名: https://aishield.tools
[07:17:37] CNAME: You.cfargotunnel.com
[07:17:37] === 部署汇总 ===
[07:17:37] cloudflared: /usr/local/bin/cloudflared
[07:17:37] Tunnel Mode: cert
[07:17:37] 状态: Named Tunnel (cert 模式) 已配置
[07:17:37] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:37] PID: 3442383
[07:17:37] API: http://localhost:8450
[07:17:37] Config: /root/.cloudflared/config.yml
[07:17:37] 域名: https://aishield.tools
[07:17:37] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:37] cloudflared: /usr/local/bin/cloudflared
[07:17:37] 状态: Named Tunnel (cert 模式) 已配置
[07:17:37] PID: 3442490
[07:17:37] Config: /root/.cloudflared/config.yml
[07:17:37] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:37] 状态: Named Tunnel (cert 模式) 已配置
 FAIL (DNS 传播中或配置错误)
[07:17:38] --- DNS CNAME ---
[07:17:38] --- DNS A ---
104.21.81.46
172.67.188.44
[07:17:38] === 部署汇总 ===
[07:17:38] Tunnel Mode: cert
[07:17:38] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:38] API: http://localhost:8450
[07:17:38] 域名: https://aishield.tools
[07:17:38] cloudflared: /usr/local/bin/cloudflared
[07:17:38] PID: 3443107
[07:17:38] Config: /root/.cloudflared/config.yml
[07:17:38] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:38] 状态: Named Tunnel (cert 模式) 已配置
[07:17:53] API 已在运行
[07:17:53] API 状态: OK
[07:17:53] === STEP 2: 安装 cloudflared ===
[07:17:53] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:17:53] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:17:53] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:17:53] === STEP 3: 检查认证方式 ===
[07:17:53] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[07:17:53] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[07:17:53] 检查现有 tunnel...
[07:17:53] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 5xlax01, 1xlax07, 2xlax08, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[07:17:53] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:53] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[07:17:53] 凭证文件存在
[07:17:53] 创建 config.yml...
[07:17:53] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[07:17:53] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:57] DNS 路由结果: 2026-08-06T23:17:57Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[07:17:57] === STEP 5: 更新 DNS (API) ===
[07:17:57] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:17:57] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[07:17:58] 设置 SSL 模式为 Full...
SSL: 跳过
[07:17:58] === STEP 6: 启动 Tunnel ===
[07:18:02] 启动 Named Tunnel (cert 模式)...
[07:18:02] 使用 config: /root/.cloudflared/config.yml
[07:18:02] cloudflared PID: 3444550
[07:18:10] Tunnel 连接已建立!
[07:18:10] --- cloudflared 日志 (最后 15 行) ---
2026-08-06T23:18:08Z INF |                                                                                     |
2026-08-06T23:18:08Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-06T23:18:08Z INF +-------------------------------------------------------------------------------------+
2026-08-06T23:18:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e312f294-9861-4b59-9cf0-0ecf08d3a206 status=pass target=region1.v2.argotunnel.com
2026-08-06T23:18:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e312f294-9861-4b59-9cf0-0ecf08d3a206 status=pass target=region2.v2.argotunnel.com
2026-08-06T23:18:08Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e312f294-9861-4b59-9cf0-0ecf08d3a206 status=pass target=region1.v2.argotunnel.com
2026-08-06T23:18:08Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e312f294-9861-4b59-9cf0-0ecf08d3a206 status=pass target=region2.v2.argotunnel.com
2026-08-06T23:18:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e312f294-9861-4b59-9cf0-0ecf08d3a206 status=pass target=region1.v2.argotunnel.com
2026-08-06T23:18:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e312f294-9861-4b59-9cf0-0ecf08d3a206 status=pass target=region2.v2.argotunnel.com
2026-08-06T23:18:08Z INF precheck component="Cloudflare API" details="API is reachable" run_id=e312f294-9861-4b59-9cf0-0ecf08d3a206 status=pass target=api.cloudflare.com:443
2026-08-06T23:18:08Z INF precheck complete hard_fail=false run_id=e312f294-9861-4b59-9cf0-0ecf08d3a206 suggested_protocol=quic
2026-08-06T23:18:08Z INF Registered tunnel connection connIndex=0 connection=aa04fb48-5f87-46e5-8f79-b6fe8cba91ca event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-06T23:18:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-08-06T23:18:09Z INF Registered tunnel connection connIndex=1 connection=6cccb1b7-816e-4cc0-9e08-857b22a4fb93 event=0 ip=198.41.192.57 location=lax07 protocol=quic
2026-08-06T23:18:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
[07:18:10] === STEP 7: 持久化 ===
[07:18:12] systemd 服务已配置
[07:18:12] Cron 保活已设置
[07:18:12] === STEP 8: 验证 ===
[07:18:12] --- API (localhost:8450) ---
 OK
[07:18:12] --- cloudflared 进程 ---
root     3444550  1.3  2.0 1294676 40512 ?       Sl   07:18   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3444762  0.0  1.3 1292484 27420 ?       Rl   07:18   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[07:18:12] --- aishield.tools ---
 OK
[07:18:14] --- DNS CNAME ---
[07:18:14] --- DNS A ---
172.67.188.44
104.21.81.46
[07:18:14] === 部署汇总 ===
[07:18:14] Tunnel Mode: cert
[07:18:14] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:18:14] API: http://localhost:8450
[07:18:14] 域名: https://aishield.tools
[07:18:14] cloudflared: /usr/local/bin/cloudflared
[07:18:14] PID: 3444550
[07:18:14] Config: /root/.cloudflared/config.yml
[07:18:14] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:18:14] 状态: Named Tunnel (cert 模式) 已配置
[07:18:56] API 已在运行
[07:18:56] API 状态: OK
[07:18:56] === STEP 2: 安装 cloudflared ===
[07:18:56] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:18:56] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:18:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:18:56] === STEP 3: 检查认证方式 ===
[07:18:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[07:18:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[07:18:56] 检查现有 tunnel...
[07:18:57] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax07, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[07:18:57] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:18:57] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[07:18:57] 凭证文件存在
[07:18:57] 创建 config.yml...
[07:18:57] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[07:18:57] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:19:01] DNS 路由结果: 2026-08-06T23:19:01Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[07:19:01] === STEP 5: 更新 DNS (API) ===
[07:19:01] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:19:02] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[07:19:02] 设置 SSL 模式为 Full...
SSL: 跳过
[07:19:03] === STEP 6: 启动 Tunnel ===
[07:19:06] 启动 Named Tunnel (cert 模式)...
[07:19:06] 使用 config: /root/.cloudflared/config.yml
[07:19:06] cloudflared PID: 3445705
[07:19:14] Tunnel 连接已建立!
[07:19:14] --- cloudflared 日志 (最后 15 行) ---
2026-08-06T23:19:06Z INF Generated Connector ID: dfd47d41-ab35-4912-b56f-0b07bb368209
2026-08-06T23:19:06Z INF Initial protocol quic
2026-08-06T23:19:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:19:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:19:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-06T23:19:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-06T23:19:06Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-06T23:19:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.73
2026-08-06T23:19:11Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.73
2026-08-06T23:19:11Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.73
2026-08-06T23:19:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-06T23:19:13Z INF Registered tunnel connection connIndex=0 connection=90874925-b5d4-4f8f-aaed-de8bacfb53cd event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-06T23:19:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-06T23:19:14Z INF Registered tunnel connection connIndex=1 connection=38fb4c12-52b5-4326-87c8-8a3e69a83fe5 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-06T23:19:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
[07:19:14] === STEP 7: 持久化 ===
[07:19:15] systemd 服务已配置
[07:19:15] Cron 保活已设置
[07:19:15] === STEP 8: 验证 ===
[07:19:15] --- API (localhost:8450) ---
 OK
[07:19:15] --- cloudflared 进程 ---
root     3445705  1.1  1.9 1294420 39020 ?       Sl   07:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3445913  0.0  1.3 1292740 27284 ?       Rl   07:19   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[07:19:15] --- aishield.tools ---
 OK
[07:19:16] --- DNS CNAME ---
[07:19:16] --- DNS A ---
172.67.188.44
104.21.81.46
[07:19:16] === 部署汇总 ===
[07:19:16] Tunnel Mode: cert
[07:19:16] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:19:16] API: http://localhost:8450
[07:19:16] 域名: https://aishield.tools
[07:19:16] cloudflared: /usr/local/bin/cloudflared
[07:19:16] PID: 3445705
[07:19:16] Config: /root/.cloudflared/config.yml
[07:19:16] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:19:16] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-07 07:19:15 CST; 2h 19min ago
   Main PID: 3445905 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.3M
        CPU: 13.033s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3445905 /bin/bash /opt/start-tunnel.sh
             └─3445913 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug  7 01:39:11 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786066752.0003772, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
