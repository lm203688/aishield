=== DIAGNOSTIC ===
Time: Thu Aug 13 03:05:10 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786604710.7338703, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1187754  0.1  1.7 1294420 34748 ?       Sl   13:41   0:08 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1187887  0.1  1.6 1294420 33632 ?       Sl   13:41   0:08 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-13T05:41:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-13T05:41:03Z INF Registered tunnel connection connIndex=0 connection=2d810a8d-e4cf-482f-be93-cd71682ea70b event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-13T05:41:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-13T05:41:04Z INF Registered tunnel connection connIndex=1 connection=34250995-9c58-4e9d-a13e-99ebaa85cb66 event=0 ip=198.41.192.67 location=lax07 protocol=quic
2026-08-13T05:41:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-08-13T05:41:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-13T05:41:05Z INF Registered tunnel connection connIndex=2 connection=89d487da-cd80-4f60-bb10-7a5966212962 event=0 ip=198.41.192.7 location=lax09 protocol=quic
2026-08-13T05:41:06Z INF Registered tunnel connection connIndex=3 connection=f3306fc0-863d-4d8a-a89a-eac8b195c6a1 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-13T05:41:09Z INF +-------------------------------------------------------------------------------------+
2026-08-13T05:41:09Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-13T05:41:09Z INF +-------------------------------------------------------------------------------------+
2026-08-13T05:41:09Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-13T05:41:09Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-13T05:41:09Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-13T05:41:09Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-13T05:41:09Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-13T05:41:09Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-13T05:41:09Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-13T05:41:09Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-13T05:41:09Z INF |                                                                                     |
2026-08-13T05:41:09Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-13T05:41:09Z INF +-------------------------------------------------------------------------------------+
2026-08-13T05:41:09Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=52c4a874-79e9-4d04-956a-1c5325fd0729 status=pass target=region1.v2.argotunnel.com
2026-08-13T05:41:09Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=52c4a874-79e9-4d04-956a-1c5325fd0729 status=pass target=region2.v2.argotunnel.com
2026-08-13T05:41:09Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=52c4a874-79e9-4d04-956a-1c5325fd0729 status=pass target=region1.v2.argotunnel.com
2026-08-13T05:41:09Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=52c4a874-79e9-4d04-956a-1c5325fd0729 status=pass target=region2.v2.argotunnel.com
2026-08-13T05:41:09Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=52c4a874-79e9-4d04-956a-1c5325fd0729 status=pass target=region1.v2.argotunnel.com
2026-08-13T05:41:09Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=52c4a874-79e9-4d04-956a-1c5325fd0729 status=pass target=region2.v2.argotunnel.com
2026-08-13T05:41:09Z INF precheck component="Cloudflare API" details="API is reachable" run_id=52c4a874-79e9-4d04-956a-1c5325fd0729 status=pass target=api.cloudflare.com:443
2026-08-13T05:41:09Z INF precheck complete hard_fail=false run_id=52c4a874-79e9-4d04-956a-1c5325fd0729 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[13:26:52] Time: Thu Aug 13 01:26:52 PM CST 2026
[13:26:52] User: root (UID: 0)
[13:26:52] === STEP 1: 启动 API (端口 8450) ===
SSL: 跳过
[13:26:52] === STEP 6: 启动 Tunnel ===
[13:26:54] 等待 tunnel 连接... (20s)
[13:26:55] 启动 Named Tunnel (cert 模式)...
[13:26:55] 使用 config: /root/.cloudflared/config.yml
[13:26:55] cloudflared PID: 1172828
[13:26:59] 等待 tunnel 连接... (10s)
[13:27:00] API 已在运行
[13:27:00] API 状态: OK
[13:27:00] === STEP 2: 安装 cloudflared ===
[13:27:00] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:27:00] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:00] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:00] === STEP 3: 检查认证方式 ===
[13:27:00] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:27:00] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:27:00] 检查现有 tunnel...
[13:27:01] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[13:27:01] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:01] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:27:01] 凭证文件存在
[13:27:01] 创建 config.yml...
[13:27:01] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:27:01] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:02] 等待 tunnel 连接... (20s)
[13:27:02] DNS 路由结果: 2026-08-13T05:27:02Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:02] === STEP 5: 更新 DNS (API) ===
[13:27:03] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:04] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[13:27:04] 等待 tunnel 连接... (30s)
DNS 更新: OK
[13:27:05] 设置 SSL 模式为 Full...
[13:27:05] 等待 tunnel 连接... (10s)
SSL: 跳过
[13:27:06] === STEP 6: 启动 Tunnel ===
[13:27:09] 启动 Named Tunnel (cert 模式)...
[13:27:09] 使用 config: /root/.cloudflared/config.yml
[13:27:09] cloudflared PID: 1173296
[13:27:09] 等待 tunnel 连接... (20s)
[13:27:10] Tunnel 连接已建立!
[13:27:10] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:27:09Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-13T05:27:09Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-13T05:27:09Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:27:09Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:27:09Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:27:09Z INF Generated Connector ID: efa40c7c-807d-4b87-a236-5bb459a914f2
2026-08-13T05:27:09Z INF Initial protocol quic
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-13T05:27:09Z INF Registered tunnel connection connIndex=0 connection=4e78103a-9b84-4288-9b6c-6e591771c1bf event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
[13:27:10] === STEP 7: 持久化 ===
[13:27:10] Tunnel 连接已建立!
[13:27:10] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:27:09Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-13T05:27:09Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-13T05:27:09Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:27:09Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:27:09Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:27:09Z INF Generated Connector ID: efa40c7c-807d-4b87-a236-5bb459a914f2
2026-08-13T05:27:09Z INF Initial protocol quic
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-13T05:27:09Z INF Registered tunnel connection connIndex=0 connection=4e78103a-9b84-4288-9b6c-6e591771c1bf event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
[13:27:10] === STEP 7: 持久化 ===
[13:27:11] Tunnel 连接已建立!
[13:27:11] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:27:09Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:27:09Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:27:09Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:27:09Z INF Generated Connector ID: efa40c7c-807d-4b87-a236-5bb459a914f2
2026-08-13T05:27:09Z INF Initial protocol quic
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-13T05:27:09Z INF Registered tunnel connection connIndex=0 connection=4e78103a-9b84-4288-9b6c-6e591771c1bf event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-13T05:27:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-13T05:27:11Z INF Registered tunnel connection connIndex=2 connection=d3759929-edd5-4fdc-b656-9b71a47e24c0 event=0 ip=198.41.200.113 location=lax01 protocol=quic
[13:27:11] === STEP 7: 持久化 ===
[13:27:11] Tunnel 连接已建立!
[13:27:11] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:27:09Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:27:09Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:27:09Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:27:09Z INF Generated Connector ID: efa40c7c-807d-4b87-a236-5bb459a914f2
2026-08-13T05:27:09Z INF Initial protocol quic
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-13T05:27:09Z INF Registered tunnel connection connIndex=0 connection=4e78103a-9b84-4288-9b6c-6e591771c1bf event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-13T05:27:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-13T05:27:11Z INF Registered tunnel connection connIndex=2 connection=d3759929-edd5-4fdc-b656-9b71a47e24c0 event=0 ip=198.41.200.113 location=lax01 protocol=quic
[13:27:11] === STEP 7: 持久化 ===
[13:27:11] Tunnel 连接已建立!
[13:27:11] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:27:09Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:27:09Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:27:09Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:27:09Z INF Generated Connector ID: efa40c7c-807d-4b87-a236-5bb459a914f2
2026-08-13T05:27:09Z INF Initial protocol quic
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:09Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-13T05:27:09Z INF Registered tunnel connection connIndex=0 connection=4e78103a-9b84-4288-9b6c-6e591771c1bf event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-08-13T05:27:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-13T05:27:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-13T05:27:11Z INF Registered tunnel connection connIndex=2 connection=d3759929-edd5-4fdc-b656-9b71a47e24c0 event=0 ip=198.41.200.113 location=lax01 protocol=quic
[13:27:11] === STEP 7: 持久化 ===
[13:27:13] systemd 服务已配置
[13:27:13] systemd 服务已配置
[13:27:13] systemd 服务已配置
[13:27:13] systemd 服务已配置
[13:27:13] systemd 服务已配置
[13:27:13] Cron 保活已设置
[13:27:13] Cron 保活已设置
[13:27:13] === STEP 8: 验证 ===
[13:27:13] Cron 保活已设置
[13:27:13] Cron 保活已设置
[13:27:13] Cron 保活已设置
[13:27:13] === STEP 8: 验证 ===
[13:27:13] --- API (localhost:8450) ---
[13:27:13] === STEP 8: 验证 ===
[13:27:13] === STEP 8: 验证 ===
[13:27:13] === STEP 8: 验证 ===
[13:27:13] --- API (localhost:8450) ---
[13:27:13] --- API (localhost:8450) ---
[13:27:13] --- API (localhost:8450) ---
[13:27:13] --- API (localhost:8450) ---
 OK
 OK
[13:27:13] --- cloudflared 进程 ---
[13:27:13] --- cloudflared 进程 ---
 OK
 OK
 OK
[13:27:13] --- cloudflared 进程 ---
[13:27:13] --- cloudflared 进程 ---
[13:27:13] --- cloudflared 进程 ---
root     1173296  2.7  1.9 1360284 39740 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1173727  0.0  1.3 1292484 27332 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1173296  2.7  1.9 1360284 39740 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1173727  0.0  1.3 1292484 27332 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:27:13] --- aishield.tools ---
[13:27:13] --- aishield.tools ---
root     1173296  2.7  1.9 1360284 39740 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1173727  0.0  1.3 1292484 27332 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1173296  2.7  1.9 1360284 39740 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1173727  0.0  1.3 1292484 27332 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:27:13] --- aishield.tools ---
[13:27:13] --- aishield.tools ---
root     1173296  2.7  1.9 1360284 39740 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1173727  0.0  1.3 1292484 27332 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:27:13] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[13:27:14] --- DNS CNAME ---
 FAIL (DNS 传播中或配置错误)
[13:27:14] --- DNS CNAME ---
 FAIL (DNS 传播中或配置错误)
[13:27:14] --- DNS CNAME ---
[13:27:14] --- DNS A ---
[13:27:14] --- DNS A ---
[13:27:14] --- DNS A ---
172.67.188.44
104.21.81.46
[13:27:14] === 部署汇总 ===
[13:27:14] Tunnel Mode: cert
172.67.188.44
104.21.81.46
[13:27:14] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:14] API: http://localhost:8450
[13:27:14] 域名: https://aishield.tools
172.67.188.44
104.21.81.46
[13:27:14] === 部署汇总 ===
[13:27:14] === 部署汇总 ===
[13:27:14] cloudflared: /usr/local/bin/cloudflared
[13:27:14] Tunnel Mode: cert
[13:27:14] Tunnel Mode: cert
[13:27:14] PID: 1172226
[13:27:14] Tunnel ID: You
[13:27:14] Config: /root/.cloudflared/config.yml
[13:27:14] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:14] API: http://localhost:8450
[13:27:14] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:14] API: http://localhost:8450
[13:27:14] 域名: https://aishield.tools
[13:27:14] 域名: https://aishield.tools
[13:27:14] cloudflared: /usr/local/bin/cloudflared
[13:27:14] 状态: Named Tunnel (cert 模式) 已配置
[13:27:14] PID: 1172644
[13:27:14] cloudflared: /usr/local/bin/cloudflared
[13:27:14] Config: /root/.cloudflared/config.yml
[13:27:14] CNAME: You.cfargotunnel.com
[13:27:14] PID: 1171900
[13:27:14] Config: /root/.cloudflared/config.yml
[13:27:14] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:14] 状态: Named Tunnel (cert 模式) 已配置
[13:27:14] 状态: Named Tunnel (cert 模式) 已配置
 FAIL (DNS 传播中或配置错误)
[13:27:15] --- DNS CNAME ---
[13:27:15] --- DNS A ---
104.21.81.46
172.67.188.44
[13:27:15] === 部署汇总 ===
[13:27:15] Tunnel Mode: cert
[13:27:15] Tunnel ID: You
[13:27:15] API: http://localhost:8450
[13:27:15] 域名: https://aishield.tools
[13:27:15] cloudflared: /usr/local/bin/cloudflared
[13:27:15] PID: 1172828
[13:27:15] Config: /root/.cloudflared/config.yml
[13:27:15] CNAME: You.cfargotunnel.com
[13:27:15] 状态: Named Tunnel (cert 模式) 已配置
 FAIL (DNS 传播中或配置错误)
[13:27:16] --- DNS CNAME ---
[13:27:16] --- DNS A ---
104.21.81.46
172.67.188.44
[13:27:16] === 部署汇总 ===
[13:27:16] Tunnel Mode: cert
[13:27:16] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:16] API: http://localhost:8450
[13:27:16] 域名: https://aishield.tools
[13:27:16] cloudflared: /usr/local/bin/cloudflared
[13:27:16] PID: 1173296
[13:27:16] Config: /root/.cloudflared/config.yml
[13:27:16] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:16] 状态: Named Tunnel (cert 模式) 已配置
[13:27:22] API 已在运行
[13:27:22] API 已在运行
[13:27:22] API 状态: OK
[13:27:22] === STEP 2: 安装 cloudflared ===
[13:27:22] API 状态: OK
[13:27:22] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:27:22] === STEP 2: 安装 cloudflared ===
[13:27:22] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:27:22] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:22] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:22] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:22] === STEP 3: 检查认证方式 ===
[13:27:22] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:27:22] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:27:22] 检查现有 tunnel...
[13:27:22] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:22] === STEP 3: 检查认证方式 ===
[13:27:22] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:27:22] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:27:22] 检查现有 tunnel...
[13:27:23] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xlax01, 1xlax05, 2xlax07, 1xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[13:27:23] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:23] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:27:23] 凭证文件存在
[13:27:23] 创建 config.yml...
[13:27:23] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:27:23] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:24] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xlax01, 1xlax05, 2xlax07, 1xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[13:27:24] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:24] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:27:24] 凭证文件存在
[13:27:24] 创建 config.yml...
[13:27:24] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:27:24] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:26] DNS 路由结果: 2026-08-13T05:27:26Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:26] === STEP 5: 更新 DNS (API) ===
[13:27:26] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:27] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[13:27:27] DNS 路由结果: 2026-08-13T05:27:27Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:27] === STEP 5: 更新 DNS (API) ===
[13:27:27] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:28] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:27:29] 设置 SSL 模式为 Full...
DNS 更新: OK
[13:27:29] 设置 SSL 模式为 Full...
SSL: 跳过
[13:27:29] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[13:27:31] === STEP 6: 启动 Tunnel ===
[13:27:32] 启动 Named Tunnel (cert 模式)...
[13:27:32] 使用 config: /root/.cloudflared/config.yml
[13:27:32] cloudflared PID: 1175011
[13:27:34] 启动 Named Tunnel (cert 模式)...
[13:27:34] 使用 config: /root/.cloudflared/config.yml
[13:27:34] cloudflared PID: 1175051
[13:27:34] API 已在运行
[13:27:34] API 状态: OK
[13:27:34] === STEP 2: 安装 cloudflared ===
[13:27:34] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:27:34] Tunnel 连接已建立!
[13:27:35] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:27:34Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-13T05:27:34Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:27:34Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:27:34Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:27:34Z INF Generated Connector ID: 2793592d-c852-439a-b914-6b0bafaae914
2026-08-13T05:27:34Z INF Initial protocol quic
2026-08-13T05:27:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:34Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-13T05:27:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-13T05:27:34Z INF Registered tunnel connection connIndex=0 connection=486bf8f0-e404-4d51-8654-c0bbd007990c event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-13T05:27:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
                                                                                                                                                                       2026-08-13T05:27:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
[13:27:35] === STEP 7: 持久化 ===
[13:27:35] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:35] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:35] === STEP 3: 检查认证方式 ===
[13:27:35] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:27:35] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:27:35] 检查现有 tunnel...
[13:27:35] systemd 服务已配置
[13:27:35] Cron 保活已设置
[13:27:35] === STEP 8: 验证 ===
[13:27:35] --- API (localhost:8450) ---
 OK
[13:27:35] --- cloudflared 进程 ---
root     1175011  3.0  1.8 1294100 37984 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1175051  9.0  1.9 1294676 38800 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1175191  0.0  1.7 1293844 34204 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel list
[13:27:35] --- aishield.tools ---
[13:27:35] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xlax01, 1xlax07, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[13:27:35] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:35] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:27:35] 凭证文件存在
[13:27:35] 创建 config.yml...
[13:27:35] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:27:35] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:36] Tunnel 连接已建立!
[13:27:36] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:27:34Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:27:34Z INF Generated Connector ID: 2793592d-c852-439a-b914-6b0bafaae914
2026-08-13T05:27:34Z INF Initial protocol quic
2026-08-13T05:27:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:34Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:34Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:34Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-13T05:27:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-13T05:27:34Z INF Registered tunnel connection connIndex=0 connection=486bf8f0-e404-4d51-8654-c0bbd007990c event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-13T05:27:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-13T05:27:35Z INF Registered tunnel connection connIndex=1 connection=bdec2bd7-3d08-48c8-8154-c0d64f01d0f9 event=0 ip=198.41.192.167 location=lax11 protocol=quic
2026-08-13T05:27:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-13T05:27:36Z INF Registered tunnel connection connIndex=2 connection=ad2a031f-c7ef-4323-b067-ceb1a20cc640 event=0 ip=198.41.200.63 location=lax01 protocol=quic
-08-13T05:27:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
[13:27:36] === STEP 7: 持久化 ===
[13:27:36] systemd 服务已配置
[13:27:36] Cron 保活已设置
[13:27:36] === STEP 8: 验证 ===
[13:27:36] --- API (localhost:8450) ---
 OK
[13:27:36] --- cloudflared 进程 ---
root     1175011  2.2  1.9 1294420 39240 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1175051  3.0  1.9 1294676 38800 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1175324  2.5  1.4 1292740 29788 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
[13:27:37] --- aishield.tools ---
 OK
[13:27:37] --- DNS CNAME ---
[13:27:37] --- DNS A ---
104.21.81.46
172.67.188.44
[13:27:37] === 部署汇总 ===
[13:27:37] Tunnel Mode: cert
[13:27:37] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:37] API: http://localhost:8450
[13:27:37] 域名: https://aishield.tools
[13:27:37] cloudflared: /usr/local/bin/cloudflared
[13:27:37] PID: 1175011
[13:27:37] Config: /root/.cloudflared/config.yml
[13:27:37] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:37] 状态: Named Tunnel (cert 模式) 已配置
 FAIL (DNS 传播中或配置错误)
[13:27:37] --- DNS CNAME ---
[13:27:38] --- DNS A ---
104.21.81.46
172.67.188.44
[13:27:38] === 部署汇总 ===
[13:27:38] Tunnel Mode: cert
[13:27:38] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:38] API: http://localhost:8450
[13:27:38] 域名: https://aishield.tools
[13:27:38] cloudflared: /usr/local/bin/cloudflared
[13:27:38] PID: 1175051
[13:27:38] Config: /root/.cloudflared/config.yml
[13:27:38] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:38] 状态: Named Tunnel (cert 模式) 已配置
[13:27:39] API 已在运行
[13:27:39] API 状态: OK
[13:27:39] === STEP 2: 安装 cloudflared ===
[13:27:39] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:27:39] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:39] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:39] === STEP 3: 检查认证方式 ===
[13:27:39] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:27:39] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:27:39] 检查现有 tunnel...
[13:27:39] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 1xlax05, 1xlax07, 1xlax09, 2xlax10, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
[13:27:39] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:39] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:27:39] 凭证文件存在
[13:27:39] 创建 config.yml...
[13:27:39] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:27:39] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:40] DNS 路由结果: 2026-08-13T05:27:40Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:40] === STEP 5: 更新 DNS (API) ===
[13:27:40] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:40] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[13:27:41] DNS 路由结果: 2026-08-13T05:27:41Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:41] === STEP 5: 更新 DNS (API) ===
[13:27:41] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:42] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:27:42] 设置 SSL 模式为 Full...
SSL: 跳过
[13:27:43] === STEP 6: 启动 Tunnel ===
DNS 更新: OK
[13:27:45] 设置 SSL 模式为 Full...
SSL: 跳过
[13:27:46] === STEP 6: 启动 Tunnel ===
[13:27:46] 启动 Named Tunnel (cert 模式)...
[13:27:46] 使用 config: /root/.cloudflared/config.yml
[13:27:46] cloudflared PID: 1175925
[13:27:48] Tunnel 连接已建立!
[13:27:48] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:27:47Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:27:47Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:27:47Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:27:47Z INF Generated Connector ID: b83b36a8-a6d2-4c16-bd03-2392f74e36b0
2026-08-13T05:27:47Z INF Initial protocol quic
2026-08-13T05:27:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:47Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T05:27:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-13T05:27:47Z INF Registered tunnel connection connIndex=0 connection=649c62d3-0fb1-4eff-b61c-500685f4a043 event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-08-13T05:27:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-13T05:27:48Z INF Registered tunnel connection connIndex=1 connection=33caa113-7b16-4061-9b75-ea37db06830f event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-13T05:27:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
[13:27:48] === STEP 7: 持久化 ===
[13:27:49] 启动 Named Tunnel (cert 模式)...
[13:27:49] 使用 config: /root/.cloudflared/config.yml
[13:27:49] cloudflared PID: 1176044
[13:27:49] API 已在运行
[13:27:49] API 状态: OK
[13:27:49] === STEP 2: 安装 cloudflared ===
[13:27:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:27:49] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:49] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:49] === STEP 3: 检查认证方式 ===
[13:27:49] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:27:49] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:27:49] 检查现有 tunnel...
[13:27:49] systemd 服务已配置
[13:27:49] Cron 保活已设置
[13:27:49] === STEP 8: 验证 ===
[13:27:49] --- API (localhost:8450) ---
 OK
[13:27:49] --- cloudflared 进程 ---
root     1175925  3.0  1.9 1294676 39032 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1176044  0.0  1.8 1293844 37768 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1176145  0.0  1.5 1292740 30724 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel list
[13:27:49] --- aishield.tools ---
[13:27:50] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xlax01, 1xlax05, 1xlax08, 1xlax10, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[13:27:50] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:50] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:27:50] 凭证文件存在
[13:27:50] 创建 config.yml...
[13:27:50] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:27:50] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:51] Tunnel 连接已建立!
[13:27:51] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:27:49Z INF Initial protocol quic
2026-08-13T05:27:49Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:49Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:49Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:27:49Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:27:49Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-13T05:27:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.57
2026-08-13T05:27:49Z INF Registered tunnel connection connIndex=0 connection=c081a763-9e1d-4019-b141-442b3f05b7fa event=0 ip=198.41.192.57 location=lax08 protocol=quic
2026-08-13T05:27:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
2026-08-13T05:27:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
                                                                                                                                                                         2026-08-13T05:27:49Z INF Registered tunnel connection connIndex=2 connection=1857054f-dc0b-4d54-91af-3913000e3bbf event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-13T05:27:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.107
2026-08-13T05:27:50Z INF Registered tunnel connection connIndex=3 connection=beda3e59-9f48-4cbb-adbf-4552fa9a9b8d event=0 ip=198.41.192.107 location=lax11 protocol=quic
2026-08-13T05:27:50Z ERR  error="stream 1 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-13T05:27:50Z ERR Request failed error="stream 1 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.200.113 type=http
[13:27:51] === STEP 7: 持久化 ===
 OK
[13:27:51] --- DNS CNAME ---
[13:27:52] --- DNS A ---
172.67.188.44
104.21.81.46
[13:27:52] === 部署汇总 ===
[13:27:52] Tunnel Mode: cert
[13:27:52] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:52] API: http://localhost:8450
[13:27:52] 域名: https://aishield.tools
[13:27:52] cloudflared: /usr/local/bin/cloudflared
[13:27:52] PID: 1175925
[13:27:52] Config: /root/.cloudflared/config.yml
[13:27:52] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:52] 状态: Named Tunnel (cert 模式) 已配置
[13:27:53] DNS 路由结果: 2026-08-13T05:27:53Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:53] === STEP 5: 更新 DNS (API) ===
[13:27:53] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:53] systemd 服务已配置
[13:27:53] Cron 保活已设置
[13:27:53] === STEP 8: 验证 ===
[13:27:53] --- API (localhost:8450) ---
 OK
[13:27:53] --- cloudflared 进程 ---
root     1175925  1.8  1.9 1294676 39260 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1176044  2.7  1.9 1293844 39352 ?       Sl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1176510  0.0  1.3 1292740 27160 ?       Rl   13:27   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:27:53] --- aishield.tools ---
[13:27:55] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
 OK
[13:27:55] --- DNS CNAME ---
[13:27:55] --- DNS A ---
172.67.188.44
104.21.81.46
[13:27:55] === 部署汇总 ===
[13:27:55] Tunnel Mode: cert
[13:27:55] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:27:55] API: http://localhost:8450
[13:27:55] 域名: https://aishield.tools
[13:27:55] cloudflared: /usr/local/bin/cloudflared
[13:27:55] PID: 1176044
[13:27:55] Config: /root/.cloudflared/config.yml
[13:27:55] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:27:55] 状态: Named Tunnel (cert 模式) 已配置
DNS 更新: OK
[13:27:56] 设置 SSL 模式为 Full...
SSL: 跳过
[13:27:58] === STEP 6: 启动 Tunnel ===
[13:27:59] API 已在运行
[13:27:59] API 状态: OK
[13:27:59] === STEP 2: 安装 cloudflared ===
[13:27:59] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:27:59] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:59] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:27:59] === STEP 3: 检查认证方式 ===
[13:27:59] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:27:59] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:27:59] 检查现有 tunnel...
[13:28:01] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05     
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[13:28:01] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:01] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:28:01] 凭证文件存在
[13:28:01] 创建 config.yml...
[13:28:01] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:28:01] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:01] 启动 Named Tunnel (cert 模式)...
[13:28:01] 使用 config: /root/.cloudflared/config.yml
[13:28:01] cloudflared PID: 1176900
[13:28:02] DNS 路由结果: 2026-08-13T05:28:02Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:02] === STEP 5: 更新 DNS (API) ===
[13:28:02] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:03] Tunnel 连接已建立!
[13:28:03] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:28:01Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:28:01Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:28:01Z INF Generated Connector ID: fe9eb794-7f99-4dee-b00d-a2e46dd5bccf
2026-08-13T05:28:01Z INF Initial protocol quic
2026-08-13T05:28:01Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:28:01Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:28:01Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:28:01Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:28:01Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T05:28:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-13T05:28:02Z INF Registered tunnel connection connIndex=0 connection=fd36fe2a-8b61-4447-8733-f9c43d2b374e event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-13T05:28:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-13T05:28:02Z INF Registered tunnel connection connIndex=1 connection=ed381475-ae8f-4d44-a1a6-58cba3a00fe8 event=0 ip=198.41.192.107 location=lax07 protocol=quic
2026-08-13T05:28:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-13T05:28:03Z INF Registered tunnel connection connIndex=2 connection=d2fa4740-38d3-454b-8767-2959172d9114 event=0 ip=198.41.200.113 location=lax01 protocol=quic
[13:28:03] === STEP 7: 持久化 ===
[13:28:04] systemd 服务已配置
[13:28:04] Cron 保活已设置
[13:28:04] === STEP 8: 验证 ===
[13:28:04] --- API (localhost:8450) ---
 OK
[13:28:04] --- cloudflared 进程 ---
[13:28:04] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
root     1176900  3.6  1.9 1294420 39300 ?       Sl   13:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1177008  0.0  1.4 1292740 29400 ?       Rl   13:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:28:04] --- aishield.tools ---
DNS 更新: OK
[13:28:05] 设置 SSL 模式为 Full...
 OK
[13:28:06] --- DNS CNAME ---
[13:28:06] --- DNS A ---
104.21.81.46
172.67.188.44
[13:28:06] === 部署汇总 ===
[13:28:06] Tunnel Mode: cert
[13:28:06] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:06] API: http://localhost:8450
[13:28:06] 域名: https://aishield.tools
[13:28:06] cloudflared: /usr/local/bin/cloudflared
[13:28:06] PID: 1176900
[13:28:06] Config: /root/.cloudflared/config.yml
[13:28:06] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:06] 状态: Named Tunnel (cert 模式) 已配置
SSL: 跳过
[13:28:07] === STEP 6: 启动 Tunnel ===
[13:28:09] API 已在运行
[13:28:09] API 状态: OK
[13:28:09] === STEP 2: 安装 cloudflared ===
[13:28:09] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:28:09] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:28:09] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:28:09] === STEP 3: 检查认证方式 ===
[13:28:09] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:28:09] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:28:09] 检查现有 tunnel...
[13:28:10] 启动 Named Tunnel (cert 模式)...
[13:28:10] 使用 config: /root/.cloudflared/config.yml
[13:28:10] cloudflared PID: 1177361
[13:28:10] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05     
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[13:28:10] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:10] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:28:10] 凭证文件存在
[13:28:10] 创建 config.yml...
[13:28:10] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:28:10] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:11] DNS 路由结果: 2026-08-13T05:28:11Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:11] === STEP 5: 更新 DNS (API) ===
[13:28:11] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:12] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:28:13] 设置 SSL 模式为 Full...
SSL: 跳过
[13:28:14] === STEP 6: 启动 Tunnel ===
[13:28:17] 启动 Named Tunnel (cert 模式)...
[13:28:17] 使用 config: /root/.cloudflared/config.yml
[13:28:17] cloudflared PID: 1177551
[13:28:18] Tunnel 连接已建立!
[13:28:18] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:28:17Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-13T05:28:17Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:28:17Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:28:17Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:28:17Z INF Generated Connector ID: 92409219-c076-468f-b032-40eb92e8ab9f
2026-08-13T05:28:17Z INF Initial protocol quic
2026-08-13T05:28:17Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:28:17Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:28:17Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:28:17Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:28:17Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T05:28:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-13T05:28:17Z INF Registered tunnel connection connIndex=0 connection=8832daf3-7619-46bd-9470-89cbae9971ab event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-13T05:28:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-13T05:28:18Z INF Registered tunnel connection connIndex=1 connection=ca980114-36c9-414b-bee7-15d342b698b0 event=0 ip=198.41.192.47 location=lax08 protocol=quic
[13:28:18] === STEP 7: 持久化 ===
[13:28:18] systemd 服务已配置
[13:28:18] Cron 保活已设置
[13:28:18] === STEP 8: 验证 ===
[13:28:18] --- API (localhost:8450) ---
 OK
[13:28:18] --- cloudflared 进程 ---
root     1177551  8.0  1.9 1293844 38340 ?       Sl   13:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1177697  0.0  1.3 1292484 27312 ?       Rl   13:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:28:18] --- aishield.tools ---
[13:28:19] Tunnel 连接已建立!
[13:28:19] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:28:17Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:28:17Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:28:17Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:28:17Z INF Generated Connector ID: 92409219-c076-468f-b032-40eb92e8ab9f
2026-08-13T05:28:17Z INF Initial protocol quic
2026-08-13T05:28:17Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:28:17Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:28:17Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:28:17Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:28:17Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T05:28:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-13T05:28:17Z INF Registered tunnel connection connIndex=0 connection=8832daf3-7619-46bd-9470-89cbae9971ab event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-13T05:28:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-13T05:28:18Z INF Registered tunnel connection connIndex=1 connection=ca980114-36c9-414b-bee7-15d342b698b0 event=0 ip=198.41.192.47 location=lax08 protocol=quic
2026-08-13T05:28:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
[13:28:19] === STEP 7: 持久化 ===
[13:28:19] systemd 服务已配置
[13:28:19] Cron 保活已设置
[13:28:19] === STEP 8: 验证 ===
[13:28:19] --- API (localhost:8450) ---
 OK
[13:28:19] --- cloudflared 进程 ---
root     1177551  5.0  1.9 1294676 39152 ?       Sl   13:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1177818  0.0  1.3 1292484 27276 ?       Rl   13:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:28:19] --- aishield.tools ---
 OK
[13:28:20] --- DNS CNAME ---
[13:28:20] --- DNS A ---
104.21.81.46
172.67.188.44
[13:28:20] === 部署汇总 ===
[13:28:20] Tunnel Mode: cert
[13:28:20] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:20] API: http://localhost:8450
[13:28:20] 域名: https://aishield.tools
[13:28:21] cloudflared: /usr/local/bin/cloudflared
[13:28:21] PID: 1177551
[13:28:21] Config: /root/.cloudflared/config.yml
[13:28:21] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:21] 状态: Named Tunnel (cert 模式) 已配置
 OK
[13:28:21] --- DNS CNAME ---
[13:28:21] --- DNS A ---
104.21.81.46
172.67.188.44
[13:28:21] === 部署汇总 ===
[13:28:21] Tunnel Mode: cert
[13:28:21] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:21] API: http://localhost:8450
[13:28:21] 域名: https://aishield.tools
[13:28:21] cloudflared: /usr/local/bin/cloudflared
[13:28:21] PID: 1177361
[13:28:21] Config: /root/.cloudflared/config.yml
[13:28:21] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:21] 状态: Named Tunnel (cert 模式) 已配置
[13:28:26] API 已在运行
[13:28:26] API 状态: OK
[13:28:26] === STEP 2: 安装 cloudflared ===
[13:28:26] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:28:26] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:28:26] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:28:26] === STEP 3: 检查认证方式 ===
[13:28:26] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:28:26] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:28:26] 检查现有 tunnel...
[13:28:27] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 3xlax01, 1xlax05, 2xlax08, 1xlax09, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[13:28:27] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:27] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:28:27] 凭证文件存在
[13:28:27] 创建 config.yml...
[13:28:27] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:28:27] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:28] DNS 路由结果: 2026-08-13T05:28:28Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:28] === STEP 5: 更新 DNS (API) ===
[13:28:28] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:29] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:28:31] 设置 SSL 模式为 Full...
SSL: 跳过
[13:28:33] === STEP 6: 启动 Tunnel ===
[13:28:36] 启动 Named Tunnel (cert 模式)...
[13:28:36] 使用 config: /root/.cloudflared/config.yml
[13:28:36] cloudflared PID: 1178468
[13:28:38] Tunnel 连接已建立!
[13:28:38] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:28:36Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:28:36Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:28:36Z INF Generated Connector ID: cdd28e77-f739-411a-b89a-06da5764d802
2026-08-13T05:28:36Z INF Initial protocol quic
2026-08-13T05:28:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:28:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:28:36Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:28:36Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:28:36Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T05:28:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-13T05:28:36Z INF Registered tunnel connection connIndex=0 connection=2be6e764-981b-4558-99d1-aca7cec28f35 event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-08-13T05:28:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-13T05:28:37Z INF Registered tunnel connection connIndex=1 connection=7a1c3a56-68d1-4002-931f-be59605ad62e event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-13T05:28:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-08-13T05:28:38Z INF Registered tunnel connection connIndex=2 connection=e8708523-3227-4741-bb25-e0c0e3fde5bc event=0 ip=198.41.192.77 location=lax05 protocol=quic
[13:28:38] === STEP 7: 持久化 ===
[13:28:38] systemd 服务已配置
[13:28:38] Cron 保活已设置
[13:28:38] === STEP 8: 验证 ===
[13:28:38] --- API (localhost:8450) ---
 OK
[13:28:38] --- cloudflared 进程 ---
root     1178468  6.0  1.9 1294420 39328 ?       Sl   13:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1178610  0.0  1.3 1292740 27000 ?       Rl   13:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:28:38] --- aishield.tools ---
 OK
[13:28:40] --- DNS CNAME ---
[13:28:40] --- DNS A ---
172.67.188.44
104.21.81.46
[13:28:40] === 部署汇总 ===
[13:28:40] Tunnel Mode: cert
[13:28:40] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:28:40] API: http://localhost:8450
[13:28:40] 域名: https://aishield.tools
[13:28:40] cloudflared: /usr/local/bin/cloudflared
[13:28:40] PID: 1178468
[13:28:40] Config: /root/.cloudflared/config.yml
[13:28:40] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:28:40] 状态: Named Tunnel (cert 模式) 已配置
[13:29:00] API 已在运行
[13:29:00] API 状态: OK
[13:29:00] === STEP 2: 安装 cloudflared ===
[13:29:00] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:29:01] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:29:01] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:29:01] === STEP 3: 检查认证方式 ===
[13:29:01] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:29:01] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:29:01] 检查现有 tunnel...
[13:29:02] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax05, 1xlax07, 1xlax09, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[13:29:02] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:29:02] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:29:02] 凭证文件存在
[13:29:02] 创建 config.yml...
[13:29:02] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:29:02] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:29:03] API 已在运行
[13:29:03] API 状态: OK
[13:29:03] === STEP 2: 安装 cloudflared ===
[13:29:03] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:29:03] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:29:03] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:29:03] === STEP 3: 检查认证方式 ===
[13:29:03] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:29:03] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:29:03] 检查现有 tunnel...
[13:29:04] DNS 路由结果: 2026-08-13T05:29:04Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:29:04] === STEP 5: 更新 DNS (API) ===
[13:29:04] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:29:05] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:29:07] 设置 SSL 模式为 Full...
[13:29:07] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax05, 1xlax07, 1xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[13:29:07] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:29:07] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:29:07] 凭证文件存在
[13:29:07] 创建 config.yml...
[13:29:07] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:29:07] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
SSL: 跳过
[13:29:08] === STEP 6: 启动 Tunnel ===
[13:29:08] DNS 路由结果: 
[13:29:08] === STEP 5: 更新 DNS (API) ===
[13:29:08] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:29:09] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:29:10] 设置 SSL 模式为 Full...
SSL: 跳过
[13:29:11] === STEP 6: 启动 Tunnel ===
[13:29:11] 启动 Named Tunnel (cert 模式)...
[13:29:11] 使用 config: /root/.cloudflared/config.yml
[13:29:11] cloudflared PID: 1179411
[13:29:13] Tunnel 连接已建立!
[13:29:13] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:29:11Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:29:11Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:29:11Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:29:11Z INF Generated Connector ID: d187a53d-94e2-47bf-a906-2afbea6298e0
2026-08-13T05:29:11Z INF Initial protocol quic
2026-08-13T05:29:11Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:29:11Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:29:11Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:29:11Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:29:11Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T05:29:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-13T05:29:11Z INF Registered tunnel connection connIndex=0 connection=d358cd76-2612-4b70-b366-2616cd8264b7 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-13T05:29:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-13T05:29:12Z INF Registered tunnel connection connIndex=1 connection=e00e594f-15ef-4f90-acdf-8e0e6e32c37f event=0 ip=198.41.192.107 location=lax09 protocol=quic
2026-08-13T05:29:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
[13:29:13] === STEP 7: 持久化 ===
[13:29:13] systemd 服务已配置
[13:29:13] Cron 保活已设置
[13:29:13] === STEP 8: 验证 ===
[13:29:13] --- API (localhost:8450) ---
 OK
[13:29:13] --- cloudflared 进程 ---
root     1179411  4.5  1.9 1360028 38420 ?       Sl   13:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1179505  0.0  1.3 1292484 27364 ?       Sl   13:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:29:13] --- aishield.tools ---
[13:29:14] 启动 Named Tunnel (cert 模式)...
[13:29:14] 使用 config: /root/.cloudflared/config.yml
[13:29:14] cloudflared PID: 1179554
 FAIL (DNS 传播中或配置错误)
[13:29:14] --- DNS CNAME ---
[13:29:14] --- DNS A ---
104.21.81.46
172.67.188.44
[13:29:14] === 部署汇总 ===
[13:29:14] Tunnel Mode: cert
[13:29:14] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:29:14] API: http://localhost:8450
[13:29:14] 域名: https://aishield.tools
[13:29:14] cloudflared: /usr/local/bin/cloudflared
[13:29:14] PID: 1179411
[13:29:14] Config: /root/.cloudflared/config.yml
[13:29:14] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:29:14] 状态: Named Tunnel (cert 模式) 已配置
[13:29:16] Tunnel 连接已建立!
[13:29:16] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:29:14Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:29:14Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:29:14Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:29:14Z INF Generated Connector ID: 7d51eb54-a07f-4780-a216-19660f650e21
2026-08-13T05:29:14Z INF Initial protocol quic
2026-08-13T05:29:14Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:29:14Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:29:14Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:29:14Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:29:14Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-13T05:29:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
2026-08-13T05:29:15Z INF Registered tunnel connection connIndex=0 connection=aa81d42d-1929-4c95-be8a-2e0cab23353a event=0 ip=198.41.192.47 location=lax08 protocol=quic
2026-08-13T05:29:15Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-13T05:29:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
                                                                                                                                                                                                                                                                                                                          2026-08-13T05:29:14Z INF Registered tunnel connection connIndex=3 connection=8584105f-f749-46fa-b6ed-e9e6022d20ec event=0 ip=198.41.192.167 location=lax08 protocol=quic
[13:29:16] === STEP 7: 持久化 ===
[13:29:17] systemd 服务已配置
[13:29:17] Cron 保活已设置
[13:29:17] === STEP 8: 验证 ===
[13:29:17] --- API (localhost:8450) ---
 OK
[13:29:17] --- cloudflared 进程 ---
root     1179411  1.6  1.9 1360028 39216 ?       Sl   13:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1179554  3.0  1.9 1294676 39120 ?       Sl   13:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1179715  0.0  1.3 1292484 27656 ?       Rl   13:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:29:17] --- aishield.tools ---
 OK
[13:29:18] --- DNS CNAME ---
[13:29:18] --- DNS A ---
104.21.81.46
172.67.188.44
[13:29:18] === 部署汇总 ===
[13:29:18] Tunnel Mode: cert
[13:29:18] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:29:18] API: http://localhost:8450
[13:29:18] 域名: https://aishield.tools
[13:29:18] cloudflared: /usr/local/bin/cloudflared
[13:29:18] PID: 1179554
[13:29:18] Config: /root/.cloudflared/config.yml
[13:29:18] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:29:18] 状态: Named Tunnel (cert 模式) 已配置
[13:40:53] API 已在运行
[13:40:53] API 状态: OK
[13:40:53] === STEP 2: 安装 cloudflared ===
[13:40:53] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:40:53] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:40:53] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:40:53] === STEP 3: 检查认证方式 ===
[13:40:53] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:40:53] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:40:53] 检查现有 tunnel...
[13:40:55] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 1xlax05, 3xlax08, 1xlax09, 1xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[13:40:55] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:40:55] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:40:55] 凭证文件存在
[13:40:55] 创建 config.yml...
[13:40:55] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:40:55] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:40:57] DNS 路由结果: 2026-08-13T05:40:57Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:40:57] === STEP 5: 更新 DNS (API) ===
[13:40:57] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:40:58] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:40:58] 设置 SSL 模式为 Full...
SSL: 跳过
[13:40:59] === STEP 6: 启动 Tunnel ===
[13:41:02] 启动 Named Tunnel (cert 模式)...
[13:41:02] 使用 config: /root/.cloudflared/config.yml
[13:41:02] cloudflared PID: 1187754
[13:41:04] Tunnel 连接已建立!
[13:41:04] --- cloudflared 日志 (最后 15 行) ---
2026-08-13T05:41:02Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-13T05:41:02Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-13T05:41:02Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-13T05:41:02Z INF Generated Connector ID: 3fefcbcb-5974-4479-b1af-6ca5847359c1
2026-08-13T05:41:02Z INF Initial protocol quic
2026-08-13T05:41:02Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:41:02Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:41:02Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-13T05:41:02Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-13T05:41:02Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-13T05:41:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-13T05:41:03Z INF Registered tunnel connection connIndex=0 connection=2d810a8d-e4cf-482f-be93-cd71682ea70b event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-13T05:41:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.67
2026-08-13T05:41:04Z INF Registered tunnel connection connIndex=1 connection=34250995-9c58-4e9d-a13e-99ebaa85cb66 event=0 ip=198.41.192.67 location=lax07 protocol=quic
2026-08-13T05:41:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
[13:41:04] === STEP 7: 持久化 ===
[13:41:05] systemd 服务已配置
[13:41:05] Cron 保活已设置
[13:41:05] === STEP 8: 验证 ===
[13:41:05] --- API (localhost:8450) ---
 OK
[13:41:05] --- cloudflared 进程 ---
root     1187754  9.0  1.9 1294092 38284 ?       Sl   13:41   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1187887  0.0  1.3 1292484 27660 ?       Sl   13:41   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:41:05] --- aishield.tools ---
 OK
[13:41:07] --- DNS CNAME ---
[13:41:07] --- DNS A ---
172.67.188.44
104.21.81.46
[13:41:07] === 部署汇总 ===
[13:41:07] Tunnel Mode: cert
[13:41:07] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:41:07] API: http://localhost:8450
[13:41:07] 域名: https://aishield.tools
[13:41:07] cloudflared: /usr/local/bin/cloudflared
[13:41:07] PID: 1187754
[13:41:07] Config: /root/.cloudflared/config.yml
[13:41:07] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:41:07] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-13 13:41:05 CST; 1h 24min ago
   Main PID: 1187881 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.3M
        CPU: 8.755s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1187881 /bin/bash /opt/start-tunnel.sh
             └─1187887 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 13 07:05:11 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786604711.6463323, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
