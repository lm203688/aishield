=== DIAGNOSTIC ===
Time: Fri Aug 28 02:04:55 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787853895.8443918, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2258000  1.4  1.7 1360028 35496 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2258094  1.5  1.8 1294676 37212 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-27T18:04:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-27T18:04:44Z INF Registered tunnel connection connIndex=0 connection=541521de-0dae-4944-9d81-c66f1ce4492a event=0 ip=198.41.192.37 location=lax12 protocol=quic
2026-08-27T18:04:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-27T18:04:45Z INF Registered tunnel connection connIndex=1 connection=1cbf8c07-c3eb-4fd2-85d0-4c599476d1c7 event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-27T18:04:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-27T18:04:46Z INF Registered tunnel connection connIndex=2 connection=a3b865c3-1f2d-490b-94fc-dbfbf7fc3a01 event=0 ip=198.41.200.63 location=sjc07 protocol=quic
2026-08-27T18:04:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-27T18:04:47Z INF Registered tunnel connection connIndex=3 connection=2521d6c4-64df-4782-952b-4623e2240ec2 event=0 ip=198.41.192.47 location=lax08 protocol=quic
2026-08-27T18:04:50Z INF +-------------------------------------------------------------------------------------+
2026-08-27T18:04:50Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-27T18:04:50Z INF +-------------------------------------------------------------------------------------+
2026-08-27T18:04:50Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-27T18:04:50Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-27T18:04:50Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-27T18:04:50Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-27T18:04:50Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-27T18:04:50Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-27T18:04:50Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-27T18:04:50Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-27T18:04:50Z INF |                                                                                     |
2026-08-27T18:04:50Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-27T18:04:50Z INF +-------------------------------------------------------------------------------------+
2026-08-27T18:04:50Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=acf45717-6f8d-4a3a-92b4-98ae82bbc6e0 status=pass target=region1.v2.argotunnel.com
2026-08-27T18:04:50Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=acf45717-6f8d-4a3a-92b4-98ae82bbc6e0 status=pass target=region2.v2.argotunnel.com
2026-08-27T18:04:50Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=acf45717-6f8d-4a3a-92b4-98ae82bbc6e0 status=pass target=region1.v2.argotunnel.com
2026-08-27T18:04:50Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=acf45717-6f8d-4a3a-92b4-98ae82bbc6e0 status=pass target=region2.v2.argotunnel.com
2026-08-27T18:04:50Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=acf45717-6f8d-4a3a-92b4-98ae82bbc6e0 status=pass target=region1.v2.argotunnel.com
2026-08-27T18:04:50Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=acf45717-6f8d-4a3a-92b4-98ae82bbc6e0 status=pass target=region2.v2.argotunnel.com
2026-08-27T18:04:50Z INF precheck component="Cloudflare API" details="API is reachable" run_id=acf45717-6f8d-4a3a-92b4-98ae82bbc6e0 status=pass target=api.cloudflare.com:443
2026-08-27T18:04:50Z INF precheck complete hard_fail=false run_id=acf45717-6f8d-4a3a-92b4-98ae82bbc6e0 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:03:53] Time: Fri Aug 28 02:03:53 AM CST 2026
[02:03:53] User: root (UID: 0)
[02:03:53] === STEP 1: 启动 API (端口 8450) ===
[02:04:35] API 已在运行
[02:04:36] API 状态: OK
[02:04:36] === STEP 2: 安装 cloudflared ===
[02:04:36] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:36] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:36] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:36] === STEP 3: 检查认证方式 ===
[02:04:36] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:36] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:36] 检查现有 tunnel...
[02:04:37] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                            
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax07, 1xlax08, 1xlax10, 1xsjc05, 1xsjc08, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                                        
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                                        
[02:04:37] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:37] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:37] 凭证文件存在
[02:04:37] 创建 config.yml...
[02:04:37] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:37] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:38] DNS 路由结果: 2026-08-27T18:04:38Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:38] === STEP 5: 更新 DNS (API) ===
[02:04:38] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:38] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:04:40] 设置 SSL 模式为 Full...
SSL: 跳过
[02:04:41] === STEP 6: 启动 Tunnel ===
[02:04:44] 启动 Named Tunnel (cert 模式)...
[02:04:44] 使用 config: /root/.cloudflared/config.yml
[02:04:44] cloudflared PID: 2258000
[02:04:46] Tunnel 连接已建立!
[02:04:46] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T18:04:44Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-27T18:04:44Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-27T18:04:44Z INF Generated Connector ID: 6b85c99c-e5e2-4e57-ba22-c2b034b9bc94
2026-08-27T18:04:44Z INF Initial protocol quic
2026-08-27T18:04:44Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T18:04:44Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T18:04:44Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T18:04:44Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T18:04:44Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-27T18:04:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-27T18:04:44Z INF Registered tunnel connection connIndex=0 connection=541521de-0dae-4944-9d81-c66f1ce4492a event=0 ip=198.41.192.37 location=lax12 protocol=quic
2026-08-27T18:04:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-27T18:04:45Z INF Registered tunnel connection connIndex=1 connection=1cbf8c07-c3eb-4fd2-85d0-4c599476d1c7 event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-27T18:04:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-27T18:04:46Z INF Registered tunnel connection connIndex=2 connection=a3b865c3-1f2d-490b-94fc-dbfbf7fc3a01 event=0 ip=198.41.200.63 location=sjc07 protocol=quic
[02:04:46] === STEP 7: 持久化 ===
[02:04:46] systemd 服务已配置
[02:04:46] Cron 保活已设置
[02:04:46] === STEP 8: 验证 ===
[02:04:46] --- API (localhost:8450) ---
 OK
[02:04:46] --- cloudflared 进程 ---
root     2258000  5.0  1.9 1360028 39108 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2258094  0.0  1.3 1292484 27256 ?       Rl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:04:46] --- aishield.tools ---
 OK
[02:04:48] --- DNS CNAME ---
[02:04:48] --- DNS A ---
104.21.81.46
172.67.188.44
[02:04:48] === 部署汇总 ===
[02:04:48] Tunnel Mode: cert
[02:04:48] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:48] API: http://localhost:8450
[02:04:48] 域名: https://aishield.tools
[02:04:48] cloudflared: /usr/local/bin/cloudflared
[02:04:48] PID: 2258000
[02:04:48] Config: /root/.cloudflared/config.yml
[02:04:48] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:48] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 02:04:46 CST; 9s ago
   Main PID: 2258093 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 21.6M
        CPU: 153ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2258093 /bin/bash /opt/start-tunnel.sh
             └─2258094 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 27 18:04:56 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787853897.1746266, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
