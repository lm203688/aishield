=== DIAGNOSTIC ===
Time: Mon Aug 17 04:27:42 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786955262.9697585, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      576377  0.1  1.2 1360284 24520 ?       Sl   08:58   0:43 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      576509  0.1  1.2 1294676 24384 ?       Sl   08:58   0:43 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-17T00:58:51Z INF Registered tunnel connection connIndex=0 connection=485fe87d-9580-4a4c-aef0-887ac611e231 event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-08-17T00:58:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-17T00:58:51Z INF Registered tunnel connection connIndex=1 connection=a5707c15-73ea-4ea4-99e1-451338db47d2 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-17T00:58:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
2026-08-17T00:58:53Z INF Registered tunnel connection connIndex=2 connection=0ea38787-e38a-4bc2-bcc3-e8ae0a7481ee event=0 ip=198.41.192.67 location=lax07 protocol=quic
2026-08-17T00:58:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.33
2026-08-17T00:58:54Z INF Registered tunnel connection connIndex=3 connection=4a894523-2b63-4441-a870-9cbc29cfd103 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-17T00:59:01Z INF +-----------------------------------------------------------------------------------------------+
2026-08-17T00:59:01Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-17T00:59:01Z INF +-----------------------------------------------------------------------------------------------+
2026-08-17T00:59:01Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-17T00:59:01Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-17T00:59:01Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-17T00:59:01Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-17T00:59:01Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-17T00:59:01Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-17T00:59:01Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-17T00:59:01Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-17T00:59:01Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-17T00:59:01Z INF |                                                                                               |
2026-08-17T00:59:01Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-17T00:59:01Z INF +-----------------------------------------------------------------------------------------------+
2026-08-17T00:59:01Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=90a9737e-d486-4953-b23c-a480ee928499 status=pass target=region1.v2.argotunnel.com
2026-08-17T00:59:01Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=90a9737e-d486-4953-b23c-a480ee928499 status=pass target=region2.v2.argotunnel.com
2026-08-17T00:59:01Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=90a9737e-d486-4953-b23c-a480ee928499 status=pass target=region1.v2.argotunnel.com
2026-08-17T00:59:01Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=90a9737e-d486-4953-b23c-a480ee928499 status=fail target=region2.v2.argotunnel.com
2026-08-17T00:59:01Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=90a9737e-d486-4953-b23c-a480ee928499 status=pass target=region1.v2.argotunnel.com
2026-08-17T00:59:01Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=90a9737e-d486-4953-b23c-a480ee928499 status=pass target=region2.v2.argotunnel.com
2026-08-17T00:59:01Z INF precheck component="Cloudflare API" details="API is reachable" run_id=90a9737e-d486-4953-b23c-a480ee928499 status=pass target=api.cloudflare.com:443
2026-08-17T00:59:01Z INF precheck complete hard_fail=false run_id=90a9737e-d486-4953-b23c-a480ee928499 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:58:40] Time: Mon Aug 17 08:58:40 AM CST 2026
[08:58:41] User: root (UID: 0)
[08:58:41] === STEP 1: 启动 API (端口 8450) ===
[08:58:42] API 已在运行
[08:58:42] API 状态: OK
[08:58:42] === STEP 2: 安装 cloudflared ===
[08:58:42] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:58:42] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:58:42] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:58:42] === STEP 3: 检查认证方式 ===
[08:58:42] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:58:42] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:58:42] 检查现有 tunnel...
[08:58:43] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax08, 2xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[08:58:43] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:58:43] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:58:43] 凭证文件存在
[08:58:43] 创建 config.yml...
[08:58:43] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:58:43] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:58:45] DNS 路由结果: 2026-08-17T00:58:45Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:58:45] === STEP 5: 更新 DNS (API) ===
[08:58:45] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:58:45] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:58:46] 设置 SSL 模式为 Full...
SSL: 跳过
[08:58:47] === STEP 6: 启动 Tunnel ===
[08:58:50] 启动 Named Tunnel (cert 模式)...
[08:58:50] 使用 config: /root/.cloudflared/config.yml
[08:58:50] cloudflared PID: 576377
[08:58:53] Tunnel 连接已建立!
[08:58:53] --- cloudflared 日志 (最后 15 行) ---
2026-08-17T00:58:51Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-17T00:58:51Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-17T00:58:51Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-17T00:58:51Z INF Generated Connector ID: d256a2f2-637a-47a9-9803-62597e4273c8
2026-08-17T00:58:51Z INF Initial protocol quic
2026-08-17T00:58:51Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-17T00:58:51Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-17T00:58:51Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-17T00:58:51Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-17T00:58:51Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-17T00:58:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-17T00:58:51Z INF Registered tunnel connection connIndex=0 connection=485fe87d-9580-4a4c-aef0-887ac611e231 event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-08-17T00:58:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-17T00:58:51Z INF Registered tunnel connection connIndex=1 connection=a5707c15-73ea-4ea4-99e1-451338db47d2 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-17T00:58:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
[08:58:53] === STEP 7: 持久化 ===
[08:58:53] systemd 服务已配置
[08:58:53] Cron 保活已设置
[08:58:53] === STEP 8: 验证 ===
[08:58:53] --- API (localhost:8450) ---
 OK
[08:58:53] --- cloudflared 进程 ---
root      576377  2.6  1.9 1359700 38936 ?       Sl   08:58   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      576509  0.0  1.3 1292740 27320 ?       Rl   08:58   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:58:53] --- aishield.tools ---
 OK
[08:58:54] --- DNS CNAME ---
[08:58:55] --- DNS A ---
104.21.81.46
172.67.188.44
[08:58:55] === 部署汇总 ===
[08:58:55] Tunnel Mode: cert
[08:58:55] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:58:55] API: http://localhost:8450
[08:58:55] 域名: https://aishield.tools
[08:58:55] cloudflared: /usr/local/bin/cloudflared
[08:58:55] PID: 576377
[08:58:55] Config: /root/.cloudflared/config.yml
[08:58:55] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:58:55] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-17 08:58:53 CST; 7h ago
   Main PID: 576508 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 18.1M
        CPU: 43.355s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─576508 /bin/bash /opt/start-tunnel.sh
             └─576509 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 17 08:27:43 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786955263.427662, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
