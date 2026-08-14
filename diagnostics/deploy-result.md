=== DIAGNOSTIC ===
Time: Sat Aug 15 05:52:42 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786744362.3137422, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2763893  1.1  1.8 1360284 37180 ?       Sl   05:52   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2764066  1.8  1.9 1294676 38264 ?       Sl   05:52   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-14T21:52:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
2026-08-14T21:52:33Z INF Registered tunnel connection connIndex=0 connection=abb24a2a-80d5-4800-b96d-b81abc1ffcff event=0 ip=198.41.192.47 location=lax10 protocol=quic
2026-08-14T21:52:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-14T21:52:33Z INF Registered tunnel connection connIndex=1 connection=0352a5ec-b4a4-4b4e-b836-524b71c3d8b3 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-14T21:52:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
2026-08-14T21:52:34Z INF Registered tunnel connection connIndex=2 connection=073d22cf-6ad3-4501-bff1-3ee5d18ae490 event=0 ip=198.41.192.57 location=lax09 protocol=quic
2026-08-14T21:52:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-14T21:52:35Z INF Registered tunnel connection connIndex=3 connection=34677e4a-ee93-4b92-8fae-c34224aaafee event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-14T21:52:39Z INF +-------------------------------------------------------------------------------------+
2026-08-14T21:52:39Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-14T21:52:39Z INF +-------------------------------------------------------------------------------------+
2026-08-14T21:52:39Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-14T21:52:39Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T21:52:39Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-14T21:52:39Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T21:52:39Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-14T21:52:39Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T21:52:39Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-14T21:52:39Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-14T21:52:39Z INF |                                                                                     |
2026-08-14T21:52:39Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-14T21:52:39Z INF +-------------------------------------------------------------------------------------+
2026-08-14T21:52:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c641a6f9-f8fd-4cc0-aa2a-9964682f7182 status=pass target=region1.v2.argotunnel.com
2026-08-14T21:52:39Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c641a6f9-f8fd-4cc0-aa2a-9964682f7182 status=pass target=region2.v2.argotunnel.com
2026-08-14T21:52:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c641a6f9-f8fd-4cc0-aa2a-9964682f7182 status=pass target=region1.v2.argotunnel.com
2026-08-14T21:52:39Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c641a6f9-f8fd-4cc0-aa2a-9964682f7182 status=pass target=region2.v2.argotunnel.com
2026-08-14T21:52:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c641a6f9-f8fd-4cc0-aa2a-9964682f7182 status=pass target=region1.v2.argotunnel.com
2026-08-14T21:52:39Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c641a6f9-f8fd-4cc0-aa2a-9964682f7182 status=pass target=region2.v2.argotunnel.com
2026-08-14T21:52:39Z INF precheck component="Cloudflare API" details="API is reachable" run_id=c641a6f9-f8fd-4cc0-aa2a-9964682f7182 status=pass target=api.cloudflare.com:443
2026-08-14T21:52:39Z INF precheck complete hard_fail=false run_id=c641a6f9-f8fd-4cc0-aa2a-9964682f7182 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[05:52:23] Time: Sat Aug 15 05:52:23 AM CST 2026
[05:52:23] User: root (UID: 0)
[05:52:23] === STEP 1: 启动 API (端口 8450) ===
[05:52:24] API 已在运行
[05:52:25] API 状态: OK
[05:52:25] === STEP 2: 安装 cloudflared ===
[05:52:25] cloudflared 安装路径: /usr/local/bin/cloudflared
[05:52:25] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[05:52:25] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[05:52:25] === STEP 3: 检查认证方式 ===
[05:52:25] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[05:52:25] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[05:52:25] 检查现有 tunnel...
[05:52:26] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax08, 1xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-14T21:52:26Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[05:52:26] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[05:52:26] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[05:52:26] 凭证文件存在
[05:52:26] 创建 config.yml...
[05:52:26] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[05:52:26] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[05:52:27] DNS 路由结果: 2026-08-14T21:52:27Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[05:52:27] === STEP 5: 更新 DNS (API) ===
[05:52:27] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[05:52:28] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[05:52:28] 设置 SSL 模式为 Full...
SSL: 跳过
[05:52:29] === STEP 6: 启动 Tunnel ===
[05:52:32] 启动 Named Tunnel (cert 模式)...
[05:52:32] 使用 config: /root/.cloudflared/config.yml
[05:52:32] cloudflared PID: 2763893
[05:52:34] Tunnel 连接已建立!
[05:52:34] --- cloudflared 日志 (最后 15 行) ---
2026-08-14T21:52:32Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-14T21:52:32Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-14T21:52:32Z INF Generated Connector ID: 5d1295ec-7713-41c6-9210-9fef9dc93efb
2026-08-14T21:52:32Z INF Initial protocol quic
2026-08-14T21:52:32Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T21:52:32Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T21:52:32Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-14T21:52:32Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-14T21:52:32Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-14T21:52:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
2026-08-14T21:52:33Z INF Registered tunnel connection connIndex=0 connection=abb24a2a-80d5-4800-b96d-b81abc1ffcff event=0 ip=198.41.192.47 location=lax10 protocol=quic
2026-08-14T21:52:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-14T21:52:33Z INF Registered tunnel connection connIndex=1 connection=0352a5ec-b4a4-4b4e-b836-524b71c3d8b3 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-14T21:52:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
2026-08-14T21:52:34Z INF Registered tunnel connection connIndex=2 connection=073d22cf-6ad3-4501-bff1-3ee5d18ae490 event=0 ip=198.41.192.57 location=lax09 protocol=quic
[05:52:34] === STEP 7: 持久化 ===
[05:52:35] systemd 服务已配置
[05:52:35] Cron 保活已设置
[05:52:35] === STEP 8: 验证 ===
[05:52:35] --- API (localhost:8450) ---
 OK
[05:52:35] --- cloudflared 进程 ---
root     2763893  3.0  1.9 1360028 38888 ?       Sl   05:52   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2764066  0.0  1.3 1292484 27304 ?       Sl   05:52   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[05:52:35] --- aishield.tools ---
 OK
[05:52:36] --- DNS CNAME ---
[05:52:36] --- DNS A ---
172.67.188.44
104.21.81.46
[05:52:36] === 部署汇总 ===
[05:52:36] Tunnel Mode: cert
[05:52:36] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[05:52:36] API: http://localhost:8450
[05:52:36] 域名: https://aishield.tools
[05:52:36] cloudflared: /usr/local/bin/cloudflared
[05:52:36] PID: 2763893
[05:52:36] Config: /root/.cloudflared/config.yml
[05:52:36] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[05:52:36] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-15 05:52:35 CST; 7s ago
   Main PID: 2764065 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 19.5M
        CPU: 134ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2764065 /bin/bash /opt/start-tunnel.sh
             └─2764066 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 14 21:52:42 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786744362.9599223, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
