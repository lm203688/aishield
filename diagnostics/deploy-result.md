=== DIAGNOSTIC ===
Time: Thu Jul 30 22:58:18 UTC 2026
=== USER ===
root
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785452302.0552163, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      393575  0.5  1.9 1360284 39068 ?       Sl   06:58   0:00 /usr/local/bin/cloudflared tunnel --url http://localhost:8450
=== CLOUDFLARED BINARY ===
lrwxrwxrwx 1 root root 20 Jul 27 22:46 /usr/local/bin/cloudflared -> /usr/bin/cloudflared
NOT FOUND
=== CLOUDFLARED LOG ===
2026-07-30T22:58:09Z INF Initial protocol quic
2026-07-30T22:58:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T22:58:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T22:58:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T22:58:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T22:58:09Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-07-30T22:58:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-07-30T22:58:10Z INF Registered tunnel connection connIndex=0 connection=8ad017a2-22c1-4de5-9e77-cb8a05ccf29b event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-07-30T22:58:16Z INF +-------------------------------------------------------------------------------------+
2026-07-30T22:58:16Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-07-30T22:58:16Z INF +-------------------------------------------------------------------------------------+
2026-07-30T22:58:16Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-07-30T22:58:16Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-07-30T22:58:16Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-07-30T22:58:16Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-07-30T22:58:16Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-07-30T22:58:16Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-07-30T22:58:16Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-07-30T22:58:16Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-07-30T22:58:16Z INF |                                                                                     |
2026-07-30T22:58:16Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-07-30T22:58:16Z INF +-------------------------------------------------------------------------------------+
2026-07-30T22:58:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9a0c2e41-d25d-4785-8563-2ce6408bdff4 status=pass target=region1.v2.argotunnel.com
2026-07-30T22:58:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9a0c2e41-d25d-4785-8563-2ce6408bdff4 status=pass target=region2.v2.argotunnel.com
2026-07-30T22:58:16Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=9a0c2e41-d25d-4785-8563-2ce6408bdff4 status=pass target=region1.v2.argotunnel.com
2026-07-30T22:58:16Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=9a0c2e41-d25d-4785-8563-2ce6408bdff4 status=pass target=region2.v2.argotunnel.com
2026-07-30T22:58:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9a0c2e41-d25d-4785-8563-2ce6408bdff4 status=pass target=region1.v2.argotunnel.com
2026-07-30T22:58:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9a0c2e41-d25d-4785-8563-2ce6408bdff4 status=pass target=region2.v2.argotunnel.com
2026-07-30T22:58:16Z INF precheck component="Cloudflare API" details="API is reachable" run_id=9a0c2e41-d25d-4785-8563-2ce6408bdff4 status=pass target=api.cloudflare.com:443
2026-07-30T22:58:16Z INF precheck complete hard_fail=false run_id=9a0c2e41-d25d-4785-8563-2ce6408bdff4 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Quick Tunnel Deployment ===
[06:58:02] Time: Fri Jul 31 06:58:02 AM CST 2026
[06:58:02] User: root (UID: 0)
[06:58:02] === STEP 1: 启动 API (端口 8450) ===
[06:58:03] API 已在运行
[06:58:03] API 状态: OK
[06:58:03] === STEP 2: 安装 cloudflared ===
[06:58:03] cloudflared 安装路径: /usr/local/bin/cloudflared
[06:58:03] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:58:03] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[06:58:03] === STEP 3: 启动 Quick Tunnel ===
[06:58:05] 启动 Quick Tunnel...
[06:58:05] cloudflared PID: 393575
[06:58:11] Tunnel URL: https://magnetic-optimum-manufacturers-temporal.trycloudflare.com
[06:58:11] --- cloudflared 日志 (最后 15 行) ---
2026-07-30T22:58:09Z INF |  https://magnetic-optimum-manufacturers-temporal.trycloudflare.com                         |
2026-07-30T22:58:09Z INF +--------------------------------------------------------------------------------------------+
2026-07-30T22:58:09Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-07-30T22:58:09Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-07-30T22:58:09Z INF Settings: map[cred-file:/root/.cloudflared/aa3f86b8-01f4-4ce0-83a8-5512219f9003.json credentials-file:/root/.cloudflared/aa3f86b8-01f4-4ce0-83a8-5512219f9003.json ha-connections:1 protocol:quic url:http://localhost:8450]
2026-07-30T22:58:09Z INF cloudflared will not automatically update if installed by a package manager.
2026-07-30T22:58:09Z INF Generated Connector ID: 08202d63-e86c-4deb-a894-0144140722b7
2026-07-30T22:58:09Z INF Initial protocol quic
2026-07-30T22:58:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T22:58:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T22:58:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T22:58:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T22:58:09Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-07-30T22:58:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-07-30T22:58:10Z INF Registered tunnel connection connIndex=0 connection=8ad017a2-22c1-4de5-9e77-cb8a05ccf29b event=0 ip=198.41.200.43 location=lax01 protocol=quic
[06:58:11] === STEP 4: 更新 DNS ===
[06:58:11] 目标: aishield.tools -> magnetic-optimum-manufacturers-temporal.trycloudflare.com
[06:58:12] 现有 DNS 记录 ID: fdc3eba7fdb90436809fe05358eb0f3a
[06:58:12] 更新为 CNAME -> magnetic-optimum-manufacturers-temporal.trycloudflare.com
DNS 更新: OK
[06:58:13] === STEP 5: 持久化 (crontab) ===
[06:58:13] Cron job 已设置
[06:58:13] === STEP 6: 验证 ===
[06:58:13] --- API (localhost:8450) ---
 OK
[06:58:13] --- Tunnel URL ---
 FAIL
[06:58:14] --- aishield.tools ---
 FAIL (DNS 传播中...)
[06:58:15] === 部署汇总 ===
[06:58:15] Tunnel URL: https://magnetic-optimum-manufacturers-temporal.trycloudflare.com
[06:58:15] API: http://localhost:8450
[06:58:15] 域名: https://aishield.tools
[06:58:15] cloudflared: /usr/local/bin/cloudflared
[06:58:15] PID: 393575
=== TUNNEL URL ===
https://magnetic-optimum-manufacturers-temporal.trycloudflare.com
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                 
=== CRONTAB ===
* * * * * pgrep -f 'cloudflared tunnel' > /dev/null 2>&1 || nohup /usr/local/bin/cloudflared tunnel --url http://localhost:8450 >> /tmp/cloudflared.log 2>&1 &

=== HTTPS Test from Runner ===
Time: Thu Jul 30 22:58:22 UTC 2026

=== curl test (aishield.tools) ===
error code: 1014

=== DNS lookup ===
172.67.188.44
104.21.81.46
