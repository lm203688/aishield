=== DIAGNOSTIC ===
Time: Sun Aug 9 04:26:35 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786263995.6329043, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1706265  0.1  1.7 1294932 34224 ?       Sl   16:14   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1706474  0.1  1.7 1294420 35100 ?       Sl   16:14   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1706764  0.1  1.7 1294676 34668 ?       Sl   16:14   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-09T08:14:24Z INF Registered tunnel connection connIndex=0 connection=96763967-68d5-487c-a915-24cf918244d8 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-09T08:14:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-09T08:14:24Z INF Registered tunnel connection connIndex=1 connection=ce053d05-4a17-40dc-a9f9-4970c7d6b69a event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-09T08:14:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
2026-08-09T08:14:25Z INF Registered tunnel connection connIndex=2 connection=2b58eab3-f6f1-4ff5-af42-a69b531793cc event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-08-09T08:14:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-08-09T08:14:26Z INF Registered tunnel connection connIndex=3 connection=a91c5e3d-ed1b-4a2f-858a-23c836dcf9f7 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-09T08:14:33Z INF +-----------------------------------------------------------------------------------------------+
2026-08-09T08:14:33Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-09T08:14:33Z INF +-----------------------------------------------------------------------------------------------+
2026-08-09T08:14:33Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-09T08:14:33Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-09T08:14:33Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-09T08:14:33Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-09T08:14:33Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-09T08:14:33Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-09T08:14:33Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-09T08:14:33Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-09T08:14:33Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-09T08:14:33Z INF |                                                                                               |
2026-08-09T08:14:33Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-09T08:14:33Z INF +-----------------------------------------------------------------------------------------------+
2026-08-09T08:14:33Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=22942d6c-bb1e-4994-a2af-97551cf79555 status=pass target=region1.v2.argotunnel.com
2026-08-09T08:14:33Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=22942d6c-bb1e-4994-a2af-97551cf79555 status=pass target=region2.v2.argotunnel.com
2026-08-09T08:14:33Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=22942d6c-bb1e-4994-a2af-97551cf79555 status=pass target=region1.v2.argotunnel.com
2026-08-09T08:14:33Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=22942d6c-bb1e-4994-a2af-97551cf79555 status=fail target=region2.v2.argotunnel.com
2026-08-09T08:14:33Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=22942d6c-bb1e-4994-a2af-97551cf79555 status=pass target=region1.v2.argotunnel.com
2026-08-09T08:14:33Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=22942d6c-bb1e-4994-a2af-97551cf79555 status=pass target=region2.v2.argotunnel.com
2026-08-09T08:14:33Z INF precheck component="Cloudflare API" details="API is reachable" run_id=22942d6c-bb1e-4994-a2af-97551cf79555 status=pass target=api.cloudflare.com:443
2026-08-09T08:14:33Z INF precheck complete hard_fail=false run_id=22942d6c-bb1e-4994-a2af-97551cf79555 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:13:59] Time: Sun Aug  9 04:13:59 PM CST 2026
[16:13:59] User: root (UID: 0)
[16:13:59] === STEP 1: 启动 API (端口 8450) ===
[16:14:08] API 已在运行
[16:14:08] API 状态: OK
[16:14:08] === STEP 2: 安装 cloudflared ===
[16:14:08] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:14:08] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:14:09] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:14:09] === STEP 3: 检查认证方式 ===
[16:14:09] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:14:09] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:14:09] 检查现有 tunnel...
[16:14:09] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax09, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[16:14:09] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:14:09] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:14:09] 凭证文件存在
[16:14:09] 创建 config.yml...
[16:14:09] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:14:09] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:14:11] DNS 路由结果: 2026-08-09T08:14:11Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:14:11] === STEP 5: 更新 DNS (API) ===
[16:14:11] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:14:11] API 已在运行
[16:14:11] API 状态: OK
[16:14:11] === STEP 2: 安装 cloudflared ===
[16:14:11] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:14:12] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:14:12] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:14:12] === STEP 3: 检查认证方式 ===
[16:14:12] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:14:12] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:14:12] 检查现有 tunnel...
[16:14:12] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax09, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[16:14:12] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:14:12] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:14:12] 凭证文件存在
[16:14:12] 创建 config.yml...
[16:14:12] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:14:12] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:14:12] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[16:14:14] API 已在运行
[16:14:14] API 状态: OK
[16:14:14] === STEP 2: 安装 cloudflared ===
[16:14:14] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:14:14] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:14:14] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:14:14] === STEP 3: 检查认证方式 ===
[16:14:14] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:14:14] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:14:14] 检查现有 tunnel...
[16:14:15] DNS 路由结果: 2026-08-09T08:14:15Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:14:15] === STEP 5: 更新 DNS (API) ===
[16:14:15] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:14:15] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax09, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[16:14:15] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:14:15] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:14:15] 凭证文件存在
[16:14:15] 创建 config.yml...
[16:14:15] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:14:15] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[16:14:15] 设置 SSL 模式为 Full...
[16:14:16] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
SSL: 跳过
[16:14:16] === STEP 6: 启动 Tunnel ===
[16:14:16] DNS 路由结果: 
[16:14:16] === STEP 5: 更新 DNS (API) ===
[16:14:16] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[16:14:17] 设置 SSL 模式为 Full...
[16:14:17] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
SSL: 跳过
[16:14:17] === STEP 6: 启动 Tunnel ===
DNS 更新: OK
[16:14:18] 设置 SSL 模式为 Full...
[16:14:19] 启动 Named Tunnel (cert 模式)...
[16:14:19] 使用 config: /root/.cloudflared/config.yml
[16:14:19] cloudflared PID: 1706238
SSL: 跳过
[16:14:19] === STEP 6: 启动 Tunnel ===
[16:14:20] 启动 Named Tunnel (cert 模式)...
[16:14:20] 使用 config: /root/.cloudflared/config.yml
[16:14:20] cloudflared PID: 1706265
[16:14:21] Tunnel 连接已建立!
[16:14:21] --- cloudflared 日志 (最后 15 行) ---
2026-08-09T08:14:20Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-09T08:14:20Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-09T08:14:20Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-09T08:14:20Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-09T08:14:20Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-09T08:14:20Z INF Generated Connector ID: aa6047d6-aa4b-41e9-98ba-c434c0ec1e86
2026-08-09T08:14:20Z INF Initial protocol quic
2026-08-09T08:14:20Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T08:14:20Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T08:14:20Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T08:14:20Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T08:14:20Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-09T08:14:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-09T08:14:21Z INF Registered tunnel connection connIndex=0 connection=0ab54630-7892-4c27-afb6-492a88fca287 event=0 ip=198.41.192.27 location=lax09 protocol=quic
2026-08-09T08:14:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
[16:14:21] === STEP 7: 持久化 ===
[16:14:22] systemd 服务已配置
[16:14:22] Cron 保活已设置
[16:14:22] === STEP 8: 验证 ===
[16:14:22] --- API (localhost:8450) ---
 OK
[16:14:22] --- cloudflared 进程 ---
root     1706265  4.0  1.8 1294100 38048 ?       Sl   16:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1706387  0.0  1.3 1358348 27356 ?       Rl   16:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:14:22] --- aishield.tools ---
[16:14:22] Tunnel 连接已建立!
[16:14:22] --- cloudflared 日志 (最后 15 行) ---
2026-08-09T08:14:20Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-09T08:14:20Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-09T08:14:20Z INF Generated Connector ID: aa6047d6-aa4b-41e9-98ba-c434c0ec1e86
2026-08-09T08:14:20Z INF Initial protocol quic
2026-08-09T08:14:20Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T08:14:20Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T08:14:20Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T08:14:20Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T08:14:20Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-09T08:14:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-09T08:14:21Z INF Registered tunnel connection connIndex=0 connection=0ab54630-7892-4c27-afb6-492a88fca287 event=0 ip=198.41.192.27 location=lax09 protocol=quic
2026-08-09T08:14:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-09T08:14:21Z INF Registered tunnel connection connIndex=1 connection=972241bc-353c-44bf-bb14-1a967cfb6b82 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-09T08:14:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-09T08:14:22Z INF Registered tunnel connection connIndex=2 connection=05fadc49-9071-4c29-85b3-c9cf7a701b3e event=0 ip=198.41.192.167 location=lax07 protocol=quic
[16:14:22] === STEP 7: 持久化 ===
[16:14:22] 启动 Named Tunnel (cert 模式)...
[16:14:22] 使用 config: /root/.cloudflared/config.yml
[16:14:22] cloudflared PID: 1706474
[16:14:23] systemd 服务已配置
[16:14:23] Cron 保活已设置
[16:14:23] === STEP 8: 验证 ===
[16:14:23] --- API (localhost:8450) ---
 OK
[16:14:23] --- cloudflared 进程 ---
root     1706265  3.6  1.9 1294420 38636 ?       Sl   16:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1706474 10.0  1.8 1294100 36376 ?       Sl   16:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1706532  0.0  1.3 1292484 27420 ?       Rl   16:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:14:23] --- aishield.tools ---
 OK
[16:14:23] --- DNS CNAME ---
[16:14:24] --- DNS A ---
172.67.188.44
104.21.81.46
[16:14:24] === 部署汇总 ===
[16:14:24] Tunnel Mode: cert
[16:14:24] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:14:24] API: http://localhost:8450
[16:14:24] 域名: https://aishield.tools
[16:14:24] cloudflared: /usr/local/bin/cloudflared
[16:14:24] PID: 1706238
[16:14:24] Config: /root/.cloudflared/config.yml
[16:14:24] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:14:24] 状态: Named Tunnel (cert 模式) 已配置
[16:14:24] Tunnel 连接已建立!
[16:14:24] --- cloudflared 日志 (最后 15 行) ---
2026-08-09T08:14:23Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-09T08:14:23Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-09T08:14:23Z INF Generated Connector ID: 9b0c2ccc-0741-4882-a1c9-387c993e921c
2026-08-09T08:14:23Z INF Initial protocol quic
2026-08-09T08:14:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T08:14:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T08:14:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T08:14:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T08:14:23Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-09T08:14:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-09T08:14:24Z INF Registered tunnel connection connIndex=0 connection=96763967-68d5-487c-a915-24cf918244d8 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-09T08:14:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-09T08:14:24Z INF Registered tunnel connection connIndex=1 connection=ce053d05-4a17-40dc-a9f9-4970c7d6b69a event=0 ip=198.41.192.107 location=lax07 protocol=quic
                                                                                                                                                                                                                                                                                                                     2026-08-09T08:14:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.113
2026-08-09T08:14:23Z INF Registered tunnel connection connIndex=3 connection=3cfc1d9e-82b4-4426-94c5-b158b5b3bdeb event=0 ip=198.41.200.113 location=lax01 protocol=quic
[16:14:24] === STEP 7: 持久化 ===
[16:14:25] systemd 服务已配置
[16:14:25] Cron 保活已设置
[16:14:25] === STEP 8: 验证 ===
[16:14:25] --- API (localhost:8450) ---
 OK
[16:14:25] --- cloudflared 进程 ---
root     1706265  2.4  1.8 1294420 36948 ?       Sl   16:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1706474  4.3  1.8 1294100 37056 ?       Sl   16:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1706764  0.0  1.3 1292484 27212 ?       Rl   16:14   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:14:25] --- aishield.tools ---
 OK
[16:14:25] --- DNS CNAME ---
[16:14:25] --- DNS A ---
104.21.81.46
172.67.188.44
[16:14:25] === 部署汇总 ===
[16:14:25] Tunnel Mode: cert
[16:14:25] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:14:25] API: http://localhost:8450
[16:14:25] 域名: https://aishield.tools
[16:14:25] cloudflared: /usr/local/bin/cloudflared
[16:14:25] PID: 1706265
[16:14:25] Config: /root/.cloudflared/config.yml
[16:14:25] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:14:25] 状态: Named Tunnel (cert 模式) 已配置
 OK
[16:14:27] --- DNS CNAME ---
[16:14:27] --- DNS A ---
172.67.188.44
104.21.81.46
[16:14:27] === 部署汇总 ===
[16:14:27] Tunnel Mode: cert
[16:14:27] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:14:27] API: http://localhost:8450
[16:14:27] 域名: https://aishield.tools
[16:14:27] cloudflared: /usr/local/bin/cloudflared
[16:14:27] PID: 1706474
[16:14:27] Config: /root/.cloudflared/config.yml
[16:14:27] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:14:27] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-09 16:14:25 CST; 12min ago
   Main PID: 1706754 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 16.8M
        CPU: 1.263s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1706754 /bin/bash /opt/start-tunnel.sh
             └─1706764 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sun Aug  9 08:26:36 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786263996.202798, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
