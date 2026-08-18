=== DIAGNOSTIC ===
Time: Tue Aug 18 08:09:53 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787011793.8219786, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1237795  0.1  1.0 1294676 21644 ?       Sl   01:59   0:29 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1237947  0.1  1.1 1294676 22672 ?       Sl   01:59   0:31 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1238277  0.1  1.1 1294676 22892 ?       Sl   01:59   0:30 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1478548  0.0  1.6 1293844 34180 ?       Sl   08:09   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-17T17:59:29Z INF Registered tunnel connection connIndex=1 connection=b9d0cea5-1e82-4d18-b483-a56aa74a90e0 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-17T17:59:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.233
2026-08-17T17:59:30Z INF Registered tunnel connection connIndex=2 connection=12891a60-88a3-4704-a6bf-66fff90655b5 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-17T17:59:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.7
2026-08-17T17:59:31Z INF Registered tunnel connection connIndex=3 connection=0fc6738d-0ca2-43b2-9e01-f2a1538a94b4 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-08-17T17:59:35Z INF +-------------------------------------------------------------------------------------+
2026-08-17T17:59:35Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-17T17:59:35Z INF +-------------------------------------------------------------------------------------+
2026-08-17T17:59:35Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-17T17:59:35Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-17T17:59:35Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-17T17:59:35Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-17T17:59:35Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-17T17:59:35Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-17T17:59:35Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-17T17:59:35Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-17T17:59:35Z INF |                                                                                     |
2026-08-17T17:59:35Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-17T17:59:35Z INF +-------------------------------------------------------------------------------------+
2026-08-17T17:59:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region1.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region2.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region1.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region2.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region1.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=region2.v2.argotunnel.com
2026-08-17T17:59:35Z INF precheck component="Cloudflare API" details="API is reachable" run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 status=pass target=api.cloudflare.com:443
2026-08-17T17:59:35Z INF precheck complete hard_fail=false run_id=cbc4ed04-807f-409c-be06-3c0a621bed75 suggested_protocol=quic
uic
2026-08-17T22:10:14Z ERR  error="stream 129 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-17T22:10:14Z ERR Request failed error="stream 129 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.200.233 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:09:51] Time: Tue Aug 18 08:09:51 AM CST 2026
[08:09:51] User: root (UID: 0)
[08:09:51] === STEP 1: 启动 API (端口 8450) ===
[08:09:51] DNS 路由结果: 2026-08-18T00:09:51Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:09:51] === STEP 5: 更新 DNS (API) ===
[08:09:52] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:09:52] API 已在运行
[08:09:52] API 状态: OK
[08:09:52] === STEP 2: 安装 cloudflared ===
[08:09:52] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:09:52] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:09:52] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:09:52] === STEP 3: 检查认证方式 ===
[08:09:52] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:09:52] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:09:52] 检查现有 tunnel...
[08:09:52] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[08:09:53] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 6xlax01, 2xlax05, 1xlax07, 1xlax09, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
[08:09:53] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:09:53] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:09:53] 凭证文件存在
[08:09:53] 创建 config.yml...
[08:09:53] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:09:53] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[08:09:53] 设置 SSL 模式为 Full...
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===

=== HTTPS Test from Runner ===
Time: Tue Aug 18 00:09:54 UTC 2026

=== curl test (aishield.tools) ===
error code: 502

=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
