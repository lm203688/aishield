=== DIAGNOSTIC ===
Time: Mon Aug 10 05:03:10 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786352590.7367191, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2566667  0.1  1.6 1360284 33668 ?       Sl   14:04   0:16 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566693  0.1  1.7 1294932 34660 ?       Sl   14:04   0:16 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566752  0.1  1.7 1294676 34832 ?       Sl   14:04   0:16 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566769  0.1  1.7 1294676 35336 ?       Sl   14:04   0:16 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566788  0.1  1.6 1294676 34132 ?       Sl   14:04   0:16 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2567348  0.1  1.7 1360284 35256 ?       Sl   14:04   0:16 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-10T06:04:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.19322026-08-10T06:04:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-10T06:04:41Z INF Registered tunnel connection connIndex=2 connection=1bccb1a5-08a8-4cbe-a4a8-bd80dda43da2 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-10T06:04:42Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.77
2026-08-10T06:04:43Z INF Registered tunnel connection connIndex=3 connection=6b50c47f-74ca-4907-86d4-e43428dfa301 event=0 ip=198.41.192.77 location=lax09 protocol=quic
2026-08-10T06:04:45Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.2202026-08-10T06:04:46Z INF +-------------------------------------------------------------------------------------+
2026-08-10T06:04:46Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-10T2026-08-10T06:04:49Z INF +-----------------------------------------------------------------------------------------------+
2026-08-10T06:04:49Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-10T06:04:49Z INF +-----------------------------------------------------------------------------------------------+
2026-08-10T06:04:49Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-10T06:04:49Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-10T06:04:49Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-10T06:04:49Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-10T06:04:49Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-10T06:04:49Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-10T06:04:49Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-10T06:04:49Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-10T06:04:49Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-10T06:04:49Z INF |                                                                                               |
2026-08-10T06:04:49Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-10T06:04:49Z INF +-----------------------------------------------------------------------------------------------+
2026-08-10T06:04:49Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ad8ad04d-8cff-4d6d-9c90-1ab47e59ec5b status=pass target=region1.v2.argotunnel.com
2026-08-10T06:04:49Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=ad8ad04d-8cff-4d6d-9c90-1ab47e59ec5b status=pass target=region2.v2.argotunnel.com
2026-08-10T06:04:49Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=ad8ad04d-8cff-4d6d-9c90-1ab47e59ec5b status=pass target=region1.v2.argotunnel.com
2026-08-10T06:04:49Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=ad8ad04d-8cff-4d6d-9c90-1ab47e59ec5b status=fail target=region2.v2.argotunnel.com
2026-08-10T06:04:49Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=ad8ad04d-8cff-4d6d-9c90-1ab47e59ec5b status=pass target=region1.v2.argotunne202026-08-10T06:05:18Z ERR  error="stream 5 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-10T06:05:18Z ERR Request failed error="stream 5 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.192.227 type=http
6-08-10T06:05:16Z ERR  error="stream 5 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-10T06:05:16Z ERR Request failed error="stream 5 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.200.23 type=http
2026-08-10T06:05:03Z INF Registered tunnel connection connIndex=1 connection=97d1639b-dd2f-45b3-ae32-66cccf9bcb9f event=0 ip=198.41.200.13 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[14:04:25] Time: Mon Aug 10 02:04:25 PM CST 2026
[14:04:25] User: root (UID: 0)
[14:04:25] === STEP 1: 启动 API (端口 8450) ===
[14:04:26] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 5xlax01, 1xlax05, 2xlax07, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[14:04:26] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:26] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[14:04:26] 凭证文件存在
[14:04:26] 创建 config.yml...
[14:04:26] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[14:04:26] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:27] API 已在运行
[14:04:27] API 状态: OK
[14:04:27] === STEP 2: 安装 cloudflared ===
[14:04:27] cloudflared 安装路径: /usr/local/bin/cloudflared
[14:04:27] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:04:27] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:04:27] === STEP 3: 检查认证方式 ===
[14:04:27] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[14:04:27] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[14:04:27] 检查现有 tunnel...
[14:04:27] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 5xlax01, 1xlax05, 2xlax07, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[14:04:27] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:27] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[14:04:27] 凭证文件存在
[14:04:27] 创建 config.yml...
[14:04:27] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[14:04:27] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:28] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 1xlax05, 2xlax07, 2xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[14:04:28] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:28] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[14:04:28] 凭证文件存在
[14:04:28] 创建 config.yml...
[14:04:28] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[14:04:28] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:29] DNS 路由结果: 2026-08-10T06:04:29Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:29] === STEP 5: 更新 DNS (API) ===
[14:04:29] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:30] API 已在运行
[14:04:30] API 状态: OK
[14:04:30] === STEP 2: 安装 cloudflared ===
[14:04:30] cloudflared 安装路径: /usr/local/bin/cloudflared
[14:04:30] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:04:30] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:04:30] === STEP 3: 检查认证方式 ===
[14:04:30] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[14:04:30] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[14:04:30] 检查现有 tunnel...
[14:04:30] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[14:04:30] DNS 路由结果: 2026-08-10T06:04:30Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:30] === STEP 5: 更新 DNS (API) ===
[14:04:30] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:31] DNS 路由结果: 2026-08-10T06:04:31Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:31] === STEP 5: 更新 DNS (API) ===
[14:04:31] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:31] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 1xlax05, 2xlax07, 2xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[14:04:31] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:31] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[14:04:31] 凭证文件存在
[14:04:31] 创建 config.yml...
[14:04:31] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[14:04:31] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:31] DNS 路由结果: 2026-08-10T06:04:31Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:31] === STEP 5: 更新 DNS (API) ===
[14:04:31] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:32] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[14:04:32] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[14:04:33] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[14:04:33] DNS 路由结果: 2026-08-10T06:04:33Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:33] === STEP 5: 更新 DNS (API) ===
[14:04:33] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[14:04:33] 设置 SSL 模式为 Full...
DNS 更新: OK
DNS 更新: OK
[14:04:33] 设置 SSL 模式为 Full...
[14:04:33] 设置 SSL 模式为 Full...
[14:04:34] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
SSL: 跳过
[14:04:34] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[14:04:35] === STEP 6: 启动 Tunnel ===
DNS 更新: OK
[14:04:35] 设置 SSL 模式为 Full...
DNS 更新: OK
[14:04:35] 设置 SSL 模式为 Full...
SSL: 跳过
[14:04:36] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[14:04:36] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[14:04:36] === STEP 6: 启动 Tunnel ===
[14:04:37] 启动 Named Tunnel (cert 模式)...
[14:04:37] 使用 config: /root/.cloudflared/config.yml
[14:04:37] cloudflared PID: 2566667
[14:04:38] 启动 Named Tunnel (cert 模式)...
[14:04:38] 使用 config: /root/.cloudflared/config.yml
[14:04:38] cloudflared PID: 2566693
[14:04:39] 启动 Named Tunnel (cert 模式)...
[14:04:39] 使用 config: /root/.cloudflared/config.yml
[14:04:39] cloudflared PID: 2566752
[14:04:39] 启动 Named Tunnel (cert 模式)...
[14:04:39] 使用 config: /root/.cloudflared/config.yml
[14:04:39] cloudflared PID: 2566769
[14:04:39] 启动 Named Tunnel (cert 模式)...
[14:04:39] 使用 config: /root/.cloudflared/config.yml
[14:04:39] cloudflared PID: 2566788
[14:04:39] Tunnel 连接已建立!
[14:04:39] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T06:04:39Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-10T06:04:39Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-10T06:04:39Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T06:04:39Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T06:04:39Z INF Generated Connector ID: 989f6c0b-33c5-4631-9203-2392bcb1bd5a
2026-08-10T06:04:39Z INF Initial protocol quic
2026-08-10T06:04:39Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF Starting metrics server on 127.0.0.1:20245/metrics
2026-08-10T06:04:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
                                                                                                                                                                                                                                                                                                                     2026-08-10T06:04:39Z INF Registered tunnel connection connIndex=1 connection=eef692a9-2c8f-4802-81d7-2fc98497cd3c event=0 ip=198.41.192.57 location=lax11 protocol=quic
[14:04:39] === STEP 7: 持久化 ===
[14:04:40] Tunnel 连接已建立!
[14:04:40] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T06:04:39Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-10T06:04:39Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T06:04:39Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T06:04:39Z INF Generated Connector ID: 989f6c0b-33c5-4631-9203-2392bcb1bd5a
2026-08-10T06:04:39Z INF Initial protocol quic
2026-08-10T06:04:39Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF Starting metrics server on 127.0.0.1:20245/metrics
2026-08-10T06:04:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:04:40Z INF Registered tunnel connection connIndex=0 connection=f9e41513-2ceb-469d-86fd-a8cbd280b2bd event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-10T06:04:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
026-08-10T06:04:40Z INF Registered tunnel connection connIndex=1 connection=129d17c5-45ce-46a1-bb5f-726ddde9f147 event=0 ip=198.41.192.37 location=lax05 protocol=quic
[14:04:40] === STEP 7: 持久化 ===
[14:04:40] systemd 服务已配置
[14:04:40] Cron 保活已设置
[14:04:40] systemd 服务已配置
[14:04:40] === STEP 8: 验证 ===
[14:04:40] --- API (localhost:8450) ---
[14:04:40] Cron 保活已设置
 OK
[14:04:40] --- cloudflared 进程 ---
[14:04:40] === STEP 8: 验证 ===
root     2566667  3.3  1.9 1360284 39040 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566693  5.0  1.9 1294420 39084 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566752  9.0  1.9 1294676 39220 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[14:04:40] --- API (localhost:8450) ---
[14:04:41] --- aishield.tools ---
 OK
[14:04:41] --- cloudflared 进程 ---
root     2566667  2.5  1.9 1360284 39040 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566693  3.3  1.9 1294420 39084 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566752  4.5  1.9 1294676 39220 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[14:04:41] --- aishield.tools ---
[14:04:41] Tunnel 连接已建立!
[14:04:41] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T06:04:39Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T06:04:39Z INF Generated Connector ID: 989f6c0b-33c5-4631-9203-2392bcb1bd5a
2026-08-10T06:04:39Z INF Initial protocol quic
2026-08-10T06:04:39Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF Starting metrics server on 127.0.0.1:20245/metrics
2026-08-10T06:04:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:04:40Z INF Registered tunnel connection connIndex=0 connection=f9e41513-2ceb-469d-86fd-a8cbd280b2bd event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-10T06:04:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.19322026-08-10T06:04:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
ation=lax01 protocol=quic
202026-08-10T06:04:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.62026-08-10T06:04:41Z INF Registered tunnel connection connIndex=2 connection=65fae7a6-0239-4136-9727-885e6eb67535 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-10T06:04:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.23
[14:04:41] === STEP 7: 持久化 ===
[14:04:41] Tunnel 连接已建立!
[14:04:41] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T06:04:39Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T06:04:39Z INF Generated Connector ID: 989f6c0b-33c5-4631-9203-2392bcb1bd5a
2026-08-10T06:04:39Z INF Initial protocol quic
2026-08-10T06:04:39Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF Starting metrics server on 127.0.0.1:20245/metrics
2026-08-10T06:04:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:04:40Z INF Registered tunnel connection connIndex=0 connection=f9e41513-2ceb-469d-86fd-a8cbd280b2bd event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-10T06:04:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.19322026-08-10T06:04:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
ation=lax01 protocol=quic
202026-08-10T06:04:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.62026-08-10T06:04:41Z INF Registered tunnel connection connIndex=2 connection=65fae7a6-0239-4136-9727-885e6eb67535 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-10T06:04:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.23
[14:04:41] === STEP 7: 持久化 ===
[14:04:41] Tunnel 连接已建立!
[14:04:41] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T06:04:39Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T06:04:39Z INF Generated Connector ID: 989f6c0b-33c5-4631-9203-2392bcb1bd5a
2026-08-10T06:04:39Z INF Initial protocol quic
2026-08-10T06:04:39Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:04:39Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:04:39Z INF Starting metrics server on 127.0.0.1:20245/metrics
2026-08-10T06:04:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:04:40Z INF Registered tunnel connection connIndex=0 connection=f9e41513-2ceb-469d-86fd-a8cbd280b2bd event=0 ip=198.41.192.37 location=lax08 protocol=quic
2026-08-10T06:04:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.19322026-08-10T06:04:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
ation=lax01 protocol=quic
202026-08-10T06:04:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.62026-08-10T06:04:41Z INF Registered tunnel connection connIndex=2 connection=65fae7a6-0239-4136-9727-885e6eb67535 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-10T06:04:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.23
[14:04:41] === STEP 7: 持久化 ===
 OK
[14:04:42] --- DNS CNAME ---
[14:04:42] --- DNS A ---
104.21.81.46
172.67.188.44
[14:04:42] === 部署汇总 ===
[14:04:42] Tunnel Mode: cert
[14:04:42] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:42] API: http://localhost:8450
[14:04:42] 域名: https://aishield.tools
[14:04:42] cloudflared: /usr/local/bin/cloudflared
[14:04:42] PID: 2566693
[14:04:42] Config: /root/.cloudflared/config.yml
[14:04:42] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:42] 状态: Named Tunnel (cert 模式) 已配置
[14:04:43] systemd 服务已配置
[14:04:43] systemd 服务已配置
[14:04:43] systemd 服务已配置
[14:04:43] Cron 保活已设置
[14:04:43] === STEP 8: 验证 ===
[14:04:43] Cron 保活已设置
[14:04:43] === STEP 8: 验证 ===
[14:04:43] --- API (localhost:8450) ---
[14:04:43] Cron 保活已设置
[14:04:43] --- API (localhost:8450) ---
[14:04:43] === STEP 8: 验证 ===
 OK
 OK
[14:04:43] --- API (localhost:8450) ---
[14:04:43] --- cloudflared 进程 ---
[14:04:43] --- cloudflared 进程 ---
 OK
root     2566667  2.0  1.9 1360284 39276 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566693  2.2  1.9 1294420 39564 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566752  2.5  1.9 1294676 39452 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566667  2.0  1.9 1360284 39276 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566693  2.2  1.9 1294420 39564 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566752  2.5  1.9 1294676 39452 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[14:04:43] --- aishield.tools ---
[14:04:43] --- aishield.tools ---
[14:04:43] --- cloudflared 进程 ---
root     2566667  2.0  1.9 1360284 39276 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566693  2.2  1.9 1294420 39564 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2566752  2.5  1.9 1294676 39452 ?       Sl   14:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[14:04:43] --- aishield.tools ---
 OK
[14:04:44] --- DNS CNAME ---
 OK
[14:04:44] --- DNS CNAME ---
 OK
[14:04:44] --- DNS CNAME ---
[14:04:44] --- DNS A ---
[14:04:44] --- DNS A ---
[14:04:44] --- DNS A ---
172.67.188.44
104.21.81.46
[14:04:44] === 部署汇总 ===
[14:04:44] Tunnel Mode: cert
[14:04:44] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:44] API: http://localhost:8450
[14:04:44] 域名: https://aishield.tools
[14:04:44] cloudflared: /usr/local/bin/cloudflared
104.21.81.46
172.67.188.44
172.67.188.44
104.21.81.46
[14:04:44] === 部署汇总 ===
[14:04:44] PID: 2566769
[14:04:44] === 部署汇总 ===
[14:04:44] Config: /root/.cloudflared/config.yml
[14:04:44] Tunnel Mode: cert
[14:04:44] Tunnel Mode: cert
[14:04:44] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:44] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:44] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:44] API: http://localhost:8450
[14:04:44] 状态: Named Tunnel (cert 模式) 已配置
[14:04:44] API: http://localhost:8450
[14:04:44] 域名: https://aishield.tools
[14:04:44] cloudflared: /usr/local/bin/cloudflared
[14:04:44] 域名: https://aishield.tools
[14:04:44] PID: 2566788
[14:04:44] cloudflared: /usr/local/bin/cloudflared
[14:04:44] PID: 2566752
[14:04:44] Config: /root/.cloudflared/config.yml
[14:04:44] Config: /root/.cloudflared/config.yml
[14:04:44] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:44] 状态: Named Tunnel (cert 模式) 已配置
[14:04:44] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:44] 状态: Named Tunnel (cert 模式) 已配置
 OK
[14:04:45] --- DNS CNAME ---
[14:04:45] --- DNS A ---
104.21.81.46
172.67.188.44
[14:04:45] === 部署汇总 ===
[14:04:45] Tunnel Mode: cert
[14:04:45] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:04:45] API: http://localhost:8450
[14:04:45] 域名: https://aishield.tools
[14:04:45] cloudflared: /usr/local/bin/cloudflared
[14:04:45] PID: 2566667
[14:04:45] Config: /root/.cloudflared/config.yml
[14:04:45] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:04:45] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-10 14:04:43 CST; 2h 58min ago
   Main PID: 2567344 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 16.3M
        CPU: 16.658s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2567344 /bin/bash /opt/start-tunnel.sh
             └─2567348 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 10 09:03:11 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786352591.5603905, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
