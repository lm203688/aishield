=== DIAGNOSTIC ===
Time: Tue Aug 11 05:28:47 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786397327.1962757, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2773536  0.1  1.3 1294676 26712 ?       Sl   Aug10   0:58 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2773658  0.1  1.3 1294676 27308 ?       Sl   Aug10   0:59 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-10T11:12:58Z INF Registered tunnel connection connIndex=3 connection=8c54c18e-f473-4852-8a0f-d90c458c42a4 event=0 ip=198.41.192.67 location=lax05 protocol=quic
2026-08-10T11:13:02Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.193
2026-08-10T11:13:02Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.193
2026-08-10T11:13:02Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-10T11:13:03Z INF +-------------------------------------------------------------------------------------+
2026-08-10T11:13:03Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-10T11:13:03Z INF +-------------------------------------------------------------------------------------+
2026-08-10T11:13:03Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-10T11:13:03Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-10T11:13:03Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-10T11:13:03Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-10T11:13:03Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-10T11:13:03Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-10T11:13:03Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-10T11:13:03Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-10T11:13:03Z INF |                                                                                     |
2026-08-10T11:13:03Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-10T11:13:03Z INF +-------------------------------------------------------------------------------------+
2026-08-10T11:13:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9d0f5806-ada4-4f5f-8210-58610b0f99bc status=pass target=region1.v2.argotunnel.com
2026-08-10T11:13:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9d0f5806-ada4-4f5f-8210-58610b0f99bc status=pass target=region2.v2.argotunnel.com
2026-08-10T11:13:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=9d0f5806-ada4-4f5f-8210-58610b0f99bc status=pass target=region1.v2.argotunnel.com
2026-08-10T11:13:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=9d0f5806-ada4-4f5f-8210-58610b0f99bc status=pass target=region2.v2.argotunnel.com
2026-08-10T11:13:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9d0f5806-ada4-4f5f-8210-58610b0f99bc status=pass target=region1.v2.argotunnel.com
2026-08-10T11:13:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9d0f5806-ada4-4f5f-8210-58610b0f99bc status=pass target=region2.v2.argotunnel.com
2026-08-10T11:13:03Z INF precheck component="Cloudflare API" details="API is reachable" run_id=9d0f5806-ada4-4f5f-8210-58610b0f99bc status=pass target=api.cloudflare.com:443
2026-08-10T11:13:03Z INF precheck complete hard_fail=false run_id=9d0f5806-ada4-4f5f-8210-58610b0f99bc suggested_protocol=quic
2026-08-10T11:13:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-10T11:13:19Z INF Registered tunnel connection connIndex=2 connection=b1be4496-b401-4843-bd71-3ccaa4e4cec0 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-10T13:17:42Z ERR  error="stream 13 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-10T13:17:42Z ERR Request failed error="stream 13 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.192.67 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:57:04] Time: Mon Aug 10 06:57:04 PM CST 2026
[18:57:04] User: root (UID: 0)
[18:57:04] === STEP 1: 启动 API (端口 8450) ===
DNS 更新: OK
[18:57:04] 设置 SSL 模式为 Full...
SSL: 跳过
[18:57:04] === STEP 6: 启动 Tunnel ===
[18:57:07] 启动 Named Tunnel (cert 模式)...
[18:57:07] 使用 config: /root/.cloudflared/config.yml
[18:57:07] cloudflared PID: 2761232
[18:57:09] Tunnel 连接已建立!
[18:57:09] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T10:57:08Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T10:57:08Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T10:57:08Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T10:57:08Z INF Generated Connector ID: bf9d3d4b-3f20-4a4b-b05c-860e847d2315
2026-08-10T10:57:08Z INF Initial protocol quic
2026-08-10T10:57:08Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:57:08Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:57:08Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:57:08Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:57:08Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-10T10:57:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-08-10T10:57:08Z INF Registered tunnel connection connIndex=0 connection=644da126-8756-4cb7-a151-b649dd7f65dd event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-10T10:57:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-08-10T10:57:09Z INF Registered tunnel connection connIndex=1 connection=3983578b-4639-4908-9b38-bb47e1dce407 event=0 ip=198.41.192.57 location=lax05 protocol=quic
2026-08-10T10:57:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
[18:57:09] === STEP 7: 持久化 ===
[18:57:10] systemd 服务已配置
[18:57:10] Cron 保活已设置
[18:57:10] === STEP 8: 验证 ===
[18:57:10] --- API (localhost:8450) ---
 OK
[18:57:10] --- cloudflared 进程 ---
root     2761232  3.0  1.9 1294420 39496 ?       Sl   18:57   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2761361  0.0  1.3 1292740 27512 ?       Sl   18:57   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:57:10] --- aishield.tools ---
 OK
[18:57:11] --- DNS CNAME ---
[18:57:11] --- DNS A ---
104.21.81.46
172.67.188.44
[18:57:11] === 部署汇总 ===
[18:57:11] Tunnel Mode: cert
[18:57:11] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:57:11] API: http://localhost:8450
[18:57:11] 域名: https://aishield.tools
[18:57:11] cloudflared: /usr/local/bin/cloudflared
[18:57:11] PID: 2761232
[18:57:11] Config: /root/.cloudflared/config.yml
[18:57:11] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:57:12] 状态: Named Tunnel (cert 模式) 已配置
[18:57:56] API 已在运行
[18:57:56] API 状态: OK
[18:57:56] === STEP 2: 安装 cloudflared ===
[18:57:56] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:57:56] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:57:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:57:56] === STEP 3: 检查认证方式 ===
[18:57:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:57:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:57:56] 检查现有 tunnel...
[18:57:57] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax08, 1xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[18:57:57] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:57:57] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:57:57] 凭证文件存在
[18:57:57] 创建 config.yml...
[18:57:57] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:57:57] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:57:58] DNS 路由结果: 2026-08-10T10:57:58Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:57:58] === STEP 5: 更新 DNS (API) ===
[18:57:58] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:58:00] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:58:01] 设置 SSL 模式为 Full...
SSL: 跳过
[18:58:03] === STEP 6: 启动 Tunnel ===
[18:58:06] 启动 Named Tunnel (cert 模式)...
[18:58:06] 使用 config: /root/.cloudflared/config.yml
[18:58:06] cloudflared PID: 2762291
[18:58:08] Tunnel 连接已建立!
[18:58:08] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T10:58:06Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T10:58:06Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T10:58:06Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T10:58:06Z INF Generated Connector ID: 79fd28ff-871e-4df4-92cb-7b96a5d8dd46
2026-08-10T10:58:06Z INF Initial protocol quic
2026-08-10T10:58:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:58:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:58:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:58:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:58:06Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-10T10:58:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-10T10:58:07Z INF Registered tunnel connection connIndex=0 connection=84a3505d-1ffb-452a-83bf-75589e723839 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-10T10:58:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
2026-08-10T10:58:07Z INF Registered tunnel connection connIndex=1 connection=5df626c3-9316-4db4-bbe8-5df82fd3a14b event=0 ip=198.41.192.227 location=lax08 protocol=quic
2026-08-10T10:58:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[18:58:08] === STEP 7: 持久化 ===
[18:58:09] systemd 服务已配置
[18:58:09] Cron 保活已设置
[18:58:09] === STEP 8: 验证 ===
[18:58:09] --- API (localhost:8450) ---
 OK
[18:58:09] --- cloudflared 进程 ---
root     2762291  3.0  1.9 1293836 38372 ?       Sl   18:58   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2762443  0.0  1.3 1292484 26904 ?       Rl   18:58   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:58:09] --- aishield.tools ---
 OK
[18:58:10] --- DNS CNAME ---
[18:58:10] --- DNS A ---
104.21.81.46
172.67.188.44
[18:58:10] === 部署汇总 ===
[18:58:10] Tunnel Mode: cert
[18:58:10] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:58:10] API: http://localhost:8450
[18:58:10] 域名: https://aishield.tools
[18:58:10] cloudflared: /usr/local/bin/cloudflared
[18:58:10] PID: 2762291
[18:58:10] Config: /root/.cloudflared/config.yml
[18:58:10] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:58:11] 状态: Named Tunnel (cert 模式) 已配置
[18:59:02] API 已在运行
[18:59:02] API 状态: OK
[18:59:02] === STEP 2: 安装 cloudflared ===
[18:59:02] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:59:02] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:59:02] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:59:02] === STEP 3: 检查认证方式 ===
[18:59:02] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:59:02] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:59:02] 检查现有 tunnel...
[18:59:02] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 2xlax08, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[18:59:02] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:59:02] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:59:02] 凭证文件存在
[18:59:02] 创建 config.yml...
[18:59:02] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:59:02] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:59:04] DNS 路由结果: 2026-08-10T10:59:04Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:59:04] === STEP 5: 更新 DNS (API) ===
[18:59:04] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:59:05] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:59:06] 设置 SSL 模式为 Full...
SSL: 跳过
[18:59:07] === STEP 6: 启动 Tunnel ===
[18:59:10] 启动 Named Tunnel (cert 模式)...
[18:59:10] 使用 config: /root/.cloudflared/config.yml
[18:59:10] cloudflared PID: 2763441
[18:59:12] Tunnel 连接已建立!
[18:59:12] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T10:59:10Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T10:59:10Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T10:59:10Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T10:59:10Z INF Generated Connector ID: 9f06a994-2344-4614-a9b9-7efc438be7ff
2026-08-10T10:59:10Z INF Initial protocol quic
2026-08-10T10:59:10Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:59:10Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:59:10Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:59:10Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:59:10Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-10T10:59:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.7
2026-08-10T10:59:11Z INF Registered tunnel connection connIndex=0 connection=75029dd9-0491-48b5-a56a-dec7f9ff2718 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-08-10T10:59:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-10T10:59:11Z INF Registered tunnel connection connIndex=1 connection=195b3081-ff3d-481d-a791-8dac9b5e889b event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-10T10:59:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
[18:59:12] === STEP 7: 持久化 ===
[18:59:13] systemd 服务已配置
[18:59:13] Cron 保活已设置
[18:59:13] === STEP 8: 验证 ===
[18:59:13] --- API (localhost:8450) ---
 OK
[18:59:13] --- cloudflared 进程 ---
root     2763441  3.0  1.9 1293836 38668 ?       Sl   18:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2763572  0.0  1.4 1292484 28612 ?       Rl   18:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:59:13] --- aishield.tools ---
[18:59:14] API 已在运行
[18:59:14] API 状态: OK
[18:59:14] === STEP 2: 安装 cloudflared ===
[18:59:14] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:59:14] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:59:14] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:59:14] === STEP 3: 检查认证方式 ===
[18:59:14] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:59:14] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:59:14] 检查现有 tunnel...
 OK
[18:59:14] --- DNS CNAME ---
[18:59:15] --- DNS A ---
104.21.81.46
172.67.188.44
[18:59:15] === 部署汇总 ===
[18:59:15] Tunnel Mode: cert
[18:59:15] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:59:15] API: http://localhost:8450
[18:59:15] 域名: https://aishield.tools
[18:59:15] cloudflared: /usr/local/bin/cloudflared
[18:59:15] PID: 2763441
[18:59:15] Config: /root/.cloudflared/config.yml
[18:59:15] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:59:15] 状态: Named Tunnel (cert 模式) 已配置
[18:59:15] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xlax01, 1xlax05, 2xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[18:59:15] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:59:15] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:59:15] 凭证文件存在
[18:59:15] 创建 config.yml...
[18:59:15] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:59:15] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:59:17] DNS 路由结果: 2026-08-10T10:59:17Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:59:17] === STEP 5: 更新 DNS (API) ===
[18:59:17] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:59:19] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:59:19] 设置 SSL 模式为 Full...
SSL: 跳过
[18:59:20] === STEP 6: 启动 Tunnel ===
[18:59:23] 启动 Named Tunnel (cert 模式)...
[18:59:23] 使用 config: /root/.cloudflared/config.yml
[18:59:23] cloudflared PID: 2763924
[18:59:25] Tunnel 连接已建立!
[18:59:25] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T10:59:23Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T10:59:23Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T10:59:23Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T10:59:23Z INF Generated Connector ID: a0be40be-cd34-4716-8765-591376bbfcb6
2026-08-10T10:59:23Z INF Initial protocol quic
2026-08-10T10:59:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:59:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:59:23Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T10:59:23Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T10:59:23Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-10T10:59:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-10T10:59:24Z INF Registered tunnel connection connIndex=0 connection=67373865-6b4b-4182-81dd-36cae9e76186 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-10T10:59:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-10T10:59:24Z INF Registered tunnel connection connIndex=1 connection=e182134a-a216-47d3-8e2c-c4c97467cfae event=0 ip=198.41.192.7 location=lax10 protocol=quic
2026-08-10T10:59:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
[18:59:25] === STEP 7: 持久化 ===
[18:59:26] systemd 服务已配置
[18:59:26] Cron 保活已设置
[18:59:26] === STEP 8: 验证 ===
[18:59:26] --- API (localhost:8450) ---
 OK
[18:59:26] --- cloudflared 进程 ---
root     2763924  3.3  1.9 1294420 39240 ?       Sl   18:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2764098  0.0  1.3 1292740 27296 ?       Rl   18:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:59:26] --- aishield.tools ---
 OK
[18:59:27] --- DNS CNAME ---
[18:59:27] --- DNS A ---
172.67.188.44
104.21.81.46
[18:59:27] === 部署汇总 ===
[18:59:27] Tunnel Mode: cert
[18:59:27] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:59:27] API: http://localhost:8450
[18:59:27] 域名: https://aishield.tools
[18:59:27] cloudflared: /usr/local/bin/cloudflared
[18:59:27] PID: 2763924
[18:59:27] Config: /root/.cloudflared/config.yml
[18:59:27] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:59:27] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-10 19:12:58 CST; 10h ago
   Main PID: 2773654 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 20.4M
        CPU: 59.506s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2773654 /bin/bash /opt/start-tunnel.sh
             └─2773658 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2772386,fd=3))                                                    
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
Time: Mon Aug 10 21:28:47 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786397327.7616725, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
