=== DIAGNOSTIC ===
Time: Thu Aug 27 08:33:49 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787790829.9588754, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1571307  1.0  1.9 1294676 38216 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1571448  1.5  1.8 1294676 37988 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-27T00:33:39Z INF Registered tunnel connection connIndex=0 connection=8743fdd1-e325-4c0f-953a-0d081cc90b64 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-27T00:33:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-27T00:33:39Z INF Registered tunnel connection connIndex=1 connection=e2b51bc7-6f2a-442f-84f6-d0f5f432c7bf event=0 ip=198.41.192.167 location=lax12 protocol=quic
2026-08-27T00:33:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-27T00:33:40Z INF Registered tunnel connection connIndex=2 connection=d6e1ec13-f931-4e3a-8d43-14178c6b3229 event=0 ip=198.41.192.227 location=lax12 protocol=quic
2026-08-27T00:33:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-27T00:33:41Z INF Registered tunnel connection connIndex=3 connection=29198f88-b7ac-4d64-b83b-654f62ace759 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-27T00:33:48Z INF +-----------------------------------------------------------------------------------------------+
2026-08-27T00:33:48Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-27T00:33:48Z INF +-----------------------------------------------------------------------------------------------+
2026-08-27T00:33:48Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-27T00:33:48Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-27T00:33:48Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-27T00:33:48Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-27T00:33:48Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-27T00:33:48Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-27T00:33:48Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-27T00:33:48Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-27T00:33:48Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-27T00:33:48Z INF |                                                                                               |
2026-08-27T00:33:48Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-27T00:33:48Z INF +-----------------------------------------------------------------------------------------------+
2026-08-27T00:33:48Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f53ea7cc-38af-41a1-8c76-414826b893d5 status=pass target=region1.v2.argotunnel.com
2026-08-27T00:33:48Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f53ea7cc-38af-41a1-8c76-414826b893d5 status=pass target=region2.v2.argotunnel.com
2026-08-27T00:33:48Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f53ea7cc-38af-41a1-8c76-414826b893d5 status=pass target=region1.v2.argotunnel.com
2026-08-27T00:33:48Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=f53ea7cc-38af-41a1-8c76-414826b893d5 status=fail target=region2.v2.argotunnel.com
2026-08-27T00:33:48Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f53ea7cc-38af-41a1-8c76-414826b893d5 status=pass target=region1.v2.argotunnel.com
2026-08-27T00:33:48Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f53ea7cc-38af-41a1-8c76-414826b893d5 status=pass target=region2.v2.argotunnel.com
2026-08-27T00:33:48Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f53ea7cc-38af-41a1-8c76-414826b893d5 status=pass target=api.cloudflare.com:443
2026-08-27T00:33:48Z INF precheck complete hard_fail=false run_id=f53ea7cc-38af-41a1-8c76-414826b893d5 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:33:27] Time: Thu Aug 27 08:33:27 AM CST 2026
[08:33:27] User: root (UID: 0)
[08:33:27] === STEP 1: 启动 API (端口 8450) ===
[08:33:29] API 已在运行
[08:33:29] API 状态: OK
[08:33:29] === STEP 2: 安装 cloudflared ===
[08:33:29] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:33:29] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:33:29] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:33:29] === STEP 3: 检查认证方式 ===
[08:33:29] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:33:29] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:33:29] 检查现有 tunnel...
[08:33:30] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax08, 2xlax09, 1xlax10, 1xsjc07, 2xsjc08, 1xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
[08:33:30] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:33:30] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:33:30] 凭证文件存在
[08:33:30] 创建 config.yml...
[08:33:30] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:33:30] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:33:32] DNS 路由结果: 2026-08-27T00:33:32Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:33:32] === STEP 5: 更新 DNS (API) ===
[08:33:32] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:33:34] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:33:34] 设置 SSL 模式为 Full...
SSL: 跳过
[08:33:35] === STEP 6: 启动 Tunnel ===
[08:33:38] 启动 Named Tunnel (cert 模式)...
[08:33:38] 使用 config: /root/.cloudflared/config.yml
[08:33:38] cloudflared PID: 1571307
[08:33:40] Tunnel 连接已建立!
[08:33:40] --- cloudflared 日志 (最后 15 行) ---
2026-08-27T00:33:38Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-27T00:33:38Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-27T00:33:38Z INF Generated Connector ID: fa2adac7-3372-4749-aa65-cc040b86fa22
2026-08-27T00:33:38Z INF Initial protocol quic
2026-08-27T00:33:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T00:33:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T00:33:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-27T00:33:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-27T00:33:38Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-27T00:33:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.13
2026-08-27T00:33:39Z INF Registered tunnel connection connIndex=0 connection=8743fdd1-e325-4c0f-953a-0d081cc90b64 event=0 ip=198.41.200.13 location=lax01 protocol=quic
2026-08-27T00:33:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-27T00:33:39Z INF Registered tunnel connection connIndex=1 connection=e2b51bc7-6f2a-442f-84f6-d0f5f432c7bf event=0 ip=198.41.192.167 location=lax12 protocol=quic
2026-08-27T00:33:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-27T00:33:40Z INF Registered tunnel connection connIndex=2 connection=d6e1ec13-f931-4e3a-8d43-14178c6b3229 event=0 ip=198.41.192.227 location=lax12 protocol=quic
[08:33:40] === STEP 7: 持久化 ===
[08:33:41] systemd 服务已配置
[08:33:41] Cron 保活已设置
[08:33:41] === STEP 8: 验证 ===
[08:33:41] --- API (localhost:8450) ---
 OK
[08:33:41] --- cloudflared 进程 ---
root     1571307  3.0  1.9 1294420 38952 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1571448  0.0  1.3 1292484 27244 ?       Rl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:33:41] --- aishield.tools ---
 OK
[08:33:42] --- DNS CNAME ---
[08:33:42] --- DNS A ---
172.67.188.44
104.21.81.46
[08:33:42] === 部署汇总 ===
[08:33:42] Tunnel Mode: cert
[08:33:42] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:33:42] API: http://localhost:8450
[08:33:42] 域名: https://aishield.tools
[08:33:42] cloudflared: /usr/local/bin/cloudflared
[08:33:42] PID: 1571307
[08:33:42] Config: /root/.cloudflared/config.yml
[08:33:42] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:33:42] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-27 08:33:41 CST; 8s ago
   Main PID: 1571447 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 18.5M
        CPU: 133ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1571447 /bin/bash /opt/start-tunnel.sh
             └─1571448 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 27 00:33:51 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787790831.889311, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
