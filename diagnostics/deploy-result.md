=== DIAGNOSTIC ===
Time: Thu Aug 20 04:14:00 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787213640.2942472, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3674156  0.8  1.7 1294676 34260 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674181  1.0  1.8 1294676 36240 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674282  1.2  1.7 1360028 35980 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674298  1.0  1.8 1294420 37268 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
root     3674767  1.8  1.9 1360284 38664 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-20T08:13:54Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:54Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:54Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:54Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:54Z INF Starting metrics server on 2026-08-20T08:13:55Z INF +-------------------------------------------------------------------------------------+
2026-08-20T08:13:55Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-20T08:13:55Z INF +-------------------------------------------------------------------------------------+
2026-08-20T08:13:55Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-20T08:13:55Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-20T08:13:55Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-20T08:13:55Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-20T08:13:55Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-20T08:13:55Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-20T08:13:55Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-20T08:13:55Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-20T08:13:55Z INF |                                                                                     |
2026-08-20T08:13:55Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-20T08:13:55Z INF +-------------------------------------------------------------------------------------+
2026-08-20T08:13:55Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f836403f-6f4c-446b-a141-78e70c996acc status=pass target=region1.v2.argotunnel.com
2026-08-20T08:13:55Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f836403f-6f4c-446b-a141-78e70c996acc status=pass target=region2.v2.argotunnel.com
2026-08-20T08:13:55Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f836403f-6f4c-446b-a141-78e70c996acc status=pass target=region1.v2.argotunnel.com
2026-08-20T08:13:55Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f836403f-6f4c-446b-a141-78e70c996acc status=pass target=region2.v2.argotunnel.com
2026-08-20T08:13:55Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f836403f-6f4c-446b-a141-78e70c996acc status=pass target=region1.v2.argotunnel.com
2026-08-20T08:13:55Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f836403f-6f4c-446b-a141-78e70c996acc status=pass target=region2.v2.argotunnel.com
2026-08-20T08:13:55Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f836403f-6f4c-446b-a141-78e70c996acc status=pass target=api.cloudflare.com:443
2026-08-20T08:13:55Z INF precheck complete hard_fail=false run_id=f836403f-6f4c-446b-a141-78e70c996acc suggested_protocol=quic
2026-08-20T08:13:56Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-08-20T08:13:56Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.73
2026-08-20T08:13:57Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
ex=2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:13:15] Time: Thu Aug 20 04:13:15 PM CST 2026
[16:13:15] User: root (UID: 0)
[16:13:15] === STEP 1: 启动 API (端口 8450) ===
[16:13:35] API 已在运行
[16:13:35] API 状态: OK
[16:13:35] === STEP 2: 安装 cloudflared ===
[16:13:35] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:13:35] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:13:35] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:13:35] === STEP 3: 检查认证方式 ===
[16:13:35] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:13:35] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:13:35] 检查现有 tunnel...
[16:13:37] API 已在运行
[16:13:37] API 状态: OK
[16:13:37] === STEP 2: 安装 cloudflared ===
[16:13:37] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:13:37] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:13:37] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:13:37] === STEP 3: 检查认证方式 ===
[16:13:37] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:13:37] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:13:37] 检查现有 tunnel...
[16:13:37] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax08, 1xlax09, 1xlax11, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-20T08:13:37Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[16:13:37] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:37] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:13:37] 凭证文件存在
[16:13:37] 创建 config.yml...
[16:13:37] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:13:37] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:38] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax08, 1xlax09, 1xlax11, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-20T08:13:38Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[16:13:38] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:38] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:13:38] 凭证文件存在
[16:13:38] 创建 config.yml...
[16:13:38] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:13:38] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:39] DNS 路由结果: 2026-08-20T08:13:39Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:39] === STEP 5: 更新 DNS (API) ===
[16:13:39] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:39] API 已在运行
[16:13:39] API 状态: OK
[16:13:39] === STEP 2: 安装 cloudflared ===
[16:13:39] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:13:39] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:13:39] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:13:39] === STEP 3: 检查认证方式 ===
[16:13:39] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:13:39] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:13:39] 检查现有 tunnel...
[16:13:40] DNS 路由结果: 2026-08-20T08:13:40Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:40] === STEP 5: 更新 DNS (API) ===
[16:13:40] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:40] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[16:13:40] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[16:13:41] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax08, 1xlax09, 1xlax11, 1xlax12 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-20T08:13:41Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[16:13:41] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:41] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:13:41] 凭证文件存在
[16:13:41] 创建 config.yml...
[16:13:41] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:13:41] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[16:13:42] 设置 SSL 模式为 Full...
[16:13:42] DNS 路由结果: 2026-08-20T08:13:42Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:42] === STEP 5: 更新 DNS (API) ===
[16:13:42] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[16:13:42] 设置 SSL 模式为 Full...
[16:13:43] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
SSL: 跳过
[16:13:43] === STEP 6: 启动 Tunnel ===
[16:13:44] API 已在运行
[16:13:44] API 状态: OK
[16:13:44] === STEP 2: 安装 cloudflared ===
[16:13:44] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:13:44] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:13:44] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:13:44] === STEP 3: 检查认证方式 ===
[16:13:44] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:13:44] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:13:44] 检查现有 tunnel...
SSL: 跳过
[16:13:44] === STEP 6: 启动 Tunnel ===
[16:13:44] 现有 tunnel 列表:

[16:13:44] 创建新 tunnel: aishield-tunnel
DNS 更新: OK
[16:13:45] 设置 SSL 模式为 Full...
[16:13:45] 创建输出: 2026-08-20T08:13:45Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
failed to create tunnel: Create Tunnel API call failed: tunnel with name already exists
[16:13:45] Tunnel 创建失败，尝试其他方法...
SSL: 跳过
[16:13:46] === STEP 6: 启动 Tunnel ===
[16:13:46] ERROR: 无法获取 Tunnel ID，cert.pem 模式失败
[16:13:46] === STEP 6: 启动 Tunnel ===
[16:13:46] 启动 Named Tunnel (cert 模式)...
[16:13:46] 使用 config: /root/.cloudflared/config.yml
[16:13:46] cloudflared PID: 3674156
[16:13:47] 启动 Named Tunnel (cert 模式)...
[16:13:47] 使用 config: /root/.cloudflared/config.yml
[16:13:47] cloudflared PID: 3674181
[16:13:48] Tunnel 连接已建立!
[16:13:48] --- cloudflared 日志 (最后 15 行) ---
2026-08-20T08:13:47Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-20T08:13:47Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-20T08:13:47Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-20T08:13:47Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-20T08:13:47Z INF Generated Connector ID: 7f7db3ad-bef4-4914-8699-db6a3e0bebb8
2026-08-20T08:13:47Z INF Initial protocol quic
2026-08-20T08:13:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:48Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:48Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:48Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-20T08:13:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-20T08:13:48Z INF Registered tunnel connection connIndex=0 connection=f91048fa-a12a-4ee1-8751-0717a7b79887 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-20T08:13:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
                                                                                                                                                                         2026-08-20T08:13:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.193
[16:13:48] === STEP 7: 持久化 ===
[16:13:49] 启动 Named Tunnel (cert 模式)...
[16:13:49] 使用 config: /root/.cloudflared/config.yml
[16:13:49] cloudflared PID: 3674282
[16:13:49] ERROR: 无法启动 Named Tunnel，使用 Quick Tunnel 临时方案
[16:13:49] Quick Tunnel PID: 3674298
[16:13:49] systemd 服务已配置
[16:13:49] Cron 保活已设置
[16:13:49] === STEP 8: 验证 ===
[16:13:49] --- API (localhost:8450) ---
 OK
[16:13:49] --- cloudflared 进程 ---
root     3674156  3.0  1.9 1294100 38424 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674181  4.5  1.9 1294420 38712 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674282  0.0  1.7 1359452 35732 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:13:49] --- aishield.tools ---
[16:13:49] Tunnel 连接已建立!
[16:13:49] --- cloudflared 日志 (最后 15 行) ---
2026-08-20T08:13:49Z INF Thank you for trying Cloudflare Tunnel. Doing so, without a Cloudflare account, is a quick way to experiment and try it out. However, be aware that these account-less Tunnels have no uptime guarantee, are subject to the Cloudflare Online Services Terms of Use (https://www.cloudflare.com/website-terms/), and Cloudflare reserves the right to investigate your use of Tunnels for violations of such terms. If you intend to use Tunnels in production you should use a pre-created named tunnel by following: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps
2026-08-20T08:13:49Z INF Requesting new quick Tunnel on trycloudflare.com...
not automatically update if installed by a package manager.
2026-08-20T08:13:49Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:49Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:49Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:49Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:49Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-20T08:13:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-20T08:13:49Z INF Registered tunnel connection connIndex=0 connection=8608ffc6-21ae-4150-a7a0-5a64cddd8fdd event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-20T08:13:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
                                                                                                                                                                           2026-08-20T08:13:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
[16:13:49] === STEP 7: 持久化 ===
[16:13:50] systemd 服务已配置
[16:13:50] Cron 保活已设置
[16:13:50] === STEP 8: 验证 ===
[16:13:50] --- API (localhost:8450) ---
 OK
[16:13:50] --- cloudflared 进程 ---
root     3674156  2.5  1.9 1294420 38556 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674181  3.3  1.8 1294676 38176 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674282 12.0  1.8 1360028 37820 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:13:50] --- aishield.tools ---
[16:13:51] Tunnel 连接已建立!
[16:13:51] --- cloudflared 日志 (最后 15 行) ---
2026-08-20T08:13:49Z INF Requesting new quick Tunnel on trycloudflare.com...
not automatically update if installed by a package manager.
2026-08-20T08:13:49Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:49Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:49Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:49Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:49Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-20T08:13:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-20T08:13:49Z INF Registered tunnel connection connIndex=0 connection=8608ffc6-21ae-4150-a7a0-5a64cddd8fdd event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-20T08:13:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-20T08:13:50Z INF Registered tunnel connection connIndex=1 connection=d97e8451-3784-4bc9-87ea-a7ae683421ab event=0 ip=198.41.192.7 location=lax12 protocol=quic
2026-08-20T08:13:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-20T08:13:51Z INF Registered tunnel connection connIndex=2 connection=dc9e58e9-f1f8-4425-823b-0ab1054b0ee4 event=0 ip=198.41.192.167 location=lax12 protocol=quic
Registered tunnel connection connIndex=3 connection=baea1b8f-fd83-477a-bc95-3ac571381cb9 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-20T08:13:51Z INF Registered tunnel connection connIndex=2 connection=a6511ee0-a665-415e-9551-f72d8add858f event=0 ip=198.41.192.57 location=lax11 protocol=quic
[16:13:51] === STEP 7: 持久化 ===
[16:13:51] Tunnel 连接已建立!
[16:13:51] --- cloudflared 日志 (最后 15 行) ---
2026-08-20T08:13:49Z INF Requesting new quick Tunnel on trycloudflare.com...
not automatically update if installed by a package manager.
2026-08-20T08:13:49Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:49Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:49Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T08:13:49Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T08:13:49Z INF Starting metrics server on 127.0.0.1:20243/metrics
2026-08-20T08:13:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-20T08:13:49Z INF Registered tunnel connection connIndex=0 connection=8608ffc6-21ae-4150-a7a0-5a64cddd8fdd event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-20T08:13:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-08-20T08:13:50Z INF Registered tunnel connection connIndex=1 connection=d97e8451-3784-4bc9-87ea-a7ae683421ab event=0 ip=198.41.192.7 location=lax12 protocol=quic
2026-08-20T08:13:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-20T08:13:51Z INF Registered tunnel connection connIndex=2 connection=dc9e58e9-f1f8-4425-823b-0ab1054b0ee4 event=0 ip=198.41.192.167 location=lax12 protocol=quic
Registered tunnel connection connIndex=3 connection=baea1b8f-fd83-477a-bc95-3ac571381cb9 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-20T08:13:51Z INF Registered tunnel connection connIndex=2 connection=a6511ee0-a665-415e-9551-f72d8add858f event=0 ip=198.41.192.57 location=lax11 protocol=quic
[16:13:51] === STEP 7: 持久化 ===
 OK
[16:13:51] --- DNS CNAME ---
[16:13:51] --- DNS A ---
104.21.81.46
172.67.188.44
[16:13:51] === 部署汇总 ===
[16:13:51] Tunnel Mode: cert
[16:13:51] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:51] API: http://localhost:8450
[16:13:51] 域名: https://aishield.tools
[16:13:51] cloudflared: /usr/local/bin/cloudflared
[16:13:51] PID: 3674181
[16:13:51] Config: /root/.cloudflared/config.yml
[16:13:51] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:51] 状态: Named Tunnel (cert 模式) 已配置
 OK
[16:13:52] --- DNS CNAME ---
[16:13:52] systemd 服务已配置
[16:13:52] systemd 服务已配置
[16:13:52] --- DNS A ---
[16:13:52] Cron 保活已设置
[16:13:52] === STEP 8: 验证 ===
[16:13:52] --- API (localhost:8450) ---
[16:13:52] Cron 保活已设置
[16:13:52] === STEP 8: 验证 ===
[16:13:52] --- API (localhost:8450) ---
104.21.81.46
172.67.188.44
[16:13:52] === 部署汇总 ===
 OK
[16:13:52] Tunnel Mode: cert
 OK
[16:13:52] --- cloudflared 进程 ---
[16:13:52] --- cloudflared 进程 ---
[16:13:52] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:52] API: http://localhost:8450
root     3674156  1.8  1.7 1294420 34504 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674181  2.4  1.7 1294676 35968 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674282  4.3  1.7 1360028 34820 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:13:52] 域名: https://aishield.tools
root     3674156  1.8  1.7 1294420 34504 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674181  2.4  1.7 1294676 35968 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3674282  4.3  1.7 1360028 34820 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:13:52] --- aishield.tools ---
[16:13:52] cloudflared: /usr/local/bin/cloudflared
[16:13:52] --- aishield.tools ---
[16:13:52] PID: 3674156
[16:13:52] Config: /root/.cloudflared/config.yml
[16:13:52] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:52] 状态: Named Tunnel (cert 模式) 已配置
 OK
[16:13:54] --- DNS CNAME ---
[16:13:54] --- DNS A ---
104.21.81.46
172.67.188.44
[16:13:54] === 部署汇总 ===
[16:13:54] Tunnel Mode: cert
[16:13:54] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:54] API: http://localhost:8450
[16:13:54] 域名: https://aishield.tools
 OK
[16:13:54] cloudflared: /usr/local/bin/cloudflared
[16:13:54] --- DNS CNAME ---
[16:13:54] PID: 3674282
[16:13:54] Config: /root/.cloudflared/config.yml
[16:13:54] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:54] 状态: Named Tunnel (cert 模式) 已配置
[16:13:54] --- DNS A ---
104.21.81.46
172.67.188.44
[16:13:54] === 部署汇总 ===
[16:13:54] Tunnel Mode: quick
[16:13:54] Tunnel ID: 未获取
[16:13:54] API: http://localhost:8450
[16:13:54] 域名: https://aishield.tools
[16:13:54] cloudflared: /usr/local/bin/cloudflared
[16:13:54] PID: 3674298
[16:13:54] Config: /root/.cloudflared/config.yml
[16:13:54] 状态: Quick Tunnel 临时方案 (error 1014 未解决)
[16:13:54] 临时 URL: 未获取
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-20 16:13:52 CST; 7s ago
   Main PID: 3674754 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 23.1M
        CPU: 162ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3674754 /bin/bash /opt/start-tunnel.sh
             └─3674767 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=1897042,fd=3))                                                    
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
Time: Thu Aug 20 08:14:01 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787213641.9458613, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
