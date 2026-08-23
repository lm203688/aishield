=== DIAGNOSTIC ===
Time: Sun Aug 23 09:22:53 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787491373.480781, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2008847  0.1  1.0 1294676 22032 ?       Sl   08:43   1:10 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2009070  0.1  1.1 1294676 22244 ?       Sl   08:43   1:12 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-23T00:43:39Z INF Registered tunnel connection connIndex=1 connection=e7364ed7-0fca-4d1d-a71a-b582f683f36b event=0 ip=198.41.200.43 location=sjc10 protocol=quic
2026-08-23T00:43:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-23T00:43:40Z INF Registered tunnel connection connIndex=2 connection=0302ada6-d5e9-4b63-9cca-efd78b5b759c event=0 ip=198.41.200.13 location=sjc07 protocol=quic
2026-08-23T00:43:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-23T00:43:41Z INF Registered tunnel connection connIndex=3 connection=c3b6c663-0214-49d8-9201-47a166447aaf event=0 ip=198.41.192.47 location=sjc01 protocol=quic
2026-08-23T00:43:42Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T00:43:42Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-23T00:43:42Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T00:43:42Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-23T00:43:42Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-23T00:43:42Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-23T00:43:42Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-23T00:43:42Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-23T00:43:42Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-23T00:43:42Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-23T00:43:42Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-23T00:43:42Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-23T00:43:42Z INF |                                                                                               |
2026-08-23T00:43:42Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-23T00:43:42Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T00:43:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region1.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region2.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region1.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=fail target=region2.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region1.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=region2.v2.argotunnel.com
2026-08-23T00:43:42Z INF precheck component="Cloudflare API" details="API is reachable" run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 status=pass target=api.cloudflare.com:443
2026-08-23T00:43:42Z INF precheck complete hard_fail=false run_id=74b103fc-85a6-40c9-abc3-e235a3aa1b06 suggested_protocol=http2
2026-08-23T07:13:32Z ERR  error="Incoming request ended abruptly: context canceled" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-23T07:13:32Z ERR Request failed error="Incoming request ended abruptly: context canceled" connIndex=2 dest=https://aishield.tools/api/v1/mcp event=0 ip=198.41.200.13 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:43:23] Time: Sun Aug 23 08:43:23 AM CST 2026
[08:43:23] User: root (UID: 0)
[08:43:23] === STEP 1: 启动 API (端口 8450) ===
[08:43:24] API 已在运行
[08:43:24] API 状态: OK
[08:43:24] === STEP 2: 安装 cloudflared ===
[08:43:24] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:43:25] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:43:25] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:43:25] === STEP 3: 检查认证方式 ===
[08:43:25] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:43:25] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:43:25] 检查现有 tunnel...
[08:43:25] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xsjc01, 1xsjc05, 2xsjc06, 1xsjc07, 1xsjc08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[08:43:25] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:43:25] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:43:25] 凭证文件存在
[08:43:25] 创建 config.yml...
[08:43:25] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:43:25] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:43:26] DNS 路由结果: 2026-08-23T00:43:26Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:43:26] === STEP 5: 更新 DNS (API) ===
[08:43:26] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:43:27] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:43:28] 设置 SSL 模式为 Full...
SSL: 跳过
[08:43:28] === STEP 6: 启动 Tunnel ===
[08:43:31] 启动 Named Tunnel (cert 模式)...
[08:43:31] 使用 config: /root/.cloudflared/config.yml
[08:43:31] cloudflared PID: 2008847
[08:43:39] Tunnel 连接已建立!
[08:43:39] --- cloudflared 日志 (最后 15 行) ---
2026-08-23T00:43:32Z INF Generated Connector ID: 1407cedc-7924-4da9-8d60-084b635248fc
2026-08-23T00:43:32Z INF Initial protocol quic
2026-08-23T00:43:32Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-23T00:43:32Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-23T00:43:32Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-23T00:43:32Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-23T00:43:32Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-23T00:43:32Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.193
2026-08-23T00:43:37Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.193
2026-08-23T00:43:37Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.193
2026-08-23T00:43:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-23T00:43:38Z INF Registered tunnel connection connIndex=0 connection=eea74186-4a96-4b45-91e9-760da00bb134 event=0 ip=198.41.192.107 location=sjc01 protocol=quic
2026-08-23T00:43:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-23T00:43:39Z INF Registered tunnel connection connIndex=1 connection=e7364ed7-0fca-4d1d-a71a-b582f683f36b event=0 ip=198.41.200.43 location=sjc10 protocol=quic
2026-08-23T00:43:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
[08:43:39] === STEP 7: 持久化 ===
[08:43:40] systemd 服务已配置
[08:43:40] Cron 保活已设置
[08:43:40] === STEP 8: 验证 ===
[08:43:40] --- API (localhost:8450) ---
 OK
[08:43:40] --- cloudflared 进程 ---
root     2008847  1.7  1.9 1294420 39300 ?       Sl   08:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2009070  0.0  1.3 1292740 27344 ?       Rl   08:43   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:43:40] --- aishield.tools ---
 OK
[08:43:41] --- DNS CNAME ---
[08:43:42] --- DNS A ---
104.21.81.46
172.67.188.44
[08:43:42] === 部署汇总 ===
[08:43:42] Tunnel Mode: cert
[08:43:42] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:43:42] API: http://localhost:8450
[08:43:42] 域名: https://aishield.tools
[08:43:42] cloudflared: /usr/local/bin/cloudflared
[08:43:42] PID: 2008847
[08:43:42] Config: /root/.cloudflared/config.yml
[08:43:42] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:43:42] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-23 08:43:40 CST; 12h ago
   Main PID: 2009062 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.8M
        CPU: 1min 12.736s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2009062 /bin/bash /opt/start-tunnel.sh
             └─2009070 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3693189,fd=3))                                                    
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
Time: Sun Aug 23 13:22:53 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787491374.02098, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
