=== DIAGNOSTIC ===
Time: Tue Aug 4 11:23:50 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785857030.8141568, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1006353  0.9  1.9 1294676 39140 ?       Sl   23:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1006458  1.3  1.9 1360284 39288 ?       Sl   23:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-04T15:23:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-08-04T15:23:41Z INF Registered tunnel connection connIndex=2 connection=e5f3fc6d-fc5e-4d14-883d-25d44be4025c event=0 ip=198.41.192.67 location=lax05 protocol=quic
2026-08-04T15:23:41Z INF Registered tunnel connection connIndex=3 connection=e1d7f3ea-8adb-488b-9b4f-196abb5b5076 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-04T15:23:44Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.193
2026-08-04T15:23:44Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.193
2026-08-04T15:23:44Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-04T15:23:48Z INF +-----------------------------------------------------------------------------------------------+
2026-08-04T15:23:48Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-04T15:23:48Z INF +-----------------------------------------------------------------------------------------------+
2026-08-04T15:23:48Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-04T15:23:48Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-04T15:23:48Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-04T15:23:48Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-04T15:23:48Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-04T15:23:48Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-04T15:23:48Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-04T15:23:48Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-04T15:23:48Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-04T15:23:48Z INF |                                                                                               |
2026-08-04T15:23:48Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-04T15:23:48Z INF +-----------------------------------------------------------------------------------------------+
2026-08-04T15:23:48Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c626ca18-c8be-43f5-8800-77de509d2476 status=pass target=region1.v2.argotunnel.com
2026-08-04T15:23:48Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c626ca18-c8be-43f5-8800-77de509d2476 status=pass target=region2.v2.argotunnel.com
2026-08-04T15:23:48Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c626ca18-c8be-43f5-8800-77de509d2476 status=pass target=region1.v2.argotunnel.com
2026-08-04T15:23:48Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=c626ca18-c8be-43f5-8800-77de509d2476 status=fail target=region2.v2.argotunnel.com
2026-08-04T15:23:48Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c626ca18-c8be-43f5-8800-77de509d2476 status=pass target=region1.v2.argotunnel.com
2026-08-04T15:23:48Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c626ca18-c8be-43f5-8800-77de509d2476 status=pass target=region2.v2.argotunnel.com
2026-08-04T15:23:48Z INF precheck component="Cloudflare API" details="API is reachable" run_id=c626ca18-c8be-43f5-8800-77de509d2476 status=pass target=api.cloudflare.com:443
2026-08-04T15:23:48Z INF precheck complete hard_fail=false run_id=c626ca18-c8be-43f5-8800-77de509d2476 suggested_protocol=http2
2026-08-04T15:23:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:23:26] Time: Tue Aug  4 11:23:26 PM CST 2026
[23:23:26] User: root (UID: 0)
[23:23:26] === STEP 1: 启动 API (端口 8450) ===
[23:23:28] API 已在运行
[23:23:28] API 状态: OK
[23:23:28] === STEP 2: 安装 cloudflared ===
[23:23:28] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:23:28] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:23:28] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:23:28] === STEP 3: 检查认证方式 ===
[23:23:28] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:23:28] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:23:28] 检查现有 tunnel...
[23:23:29] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax08, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                           
[23:23:29] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:23:29] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:23:29] 凭证文件存在
[23:23:29] 创建 config.yml...
[23:23:29] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:23:29] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:23:33] DNS 路由结果: 2026-08-04T15:23:33Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:23:33] === STEP 5: 更新 DNS (API) ===
[23:23:33] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:23:34] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[23:23:34] 设置 SSL 模式为 Full...
SSL: 跳过
[23:23:35] === STEP 6: 启动 Tunnel ===
[23:23:38] 启动 Named Tunnel (cert 模式)...
[23:23:38] 使用 config: /root/.cloudflared/config.yml
[23:23:38] cloudflared PID: 1006353
[23:23:40] Tunnel 连接已建立!
[23:23:40] --- cloudflared 日志 (最后 15 行) ---
2026-08-04T15:23:38Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-04T15:23:38Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-04T15:23:38Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-04T15:23:38Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-04T15:23:38Z INF Generated Connector ID: 81fd319d-dd47-46dc-8672-a109962690c1
2026-08-04T15:23:38Z INF Initial protocol quic
2026-08-04T15:23:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-04T15:23:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-04T15:23:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-04T15:23:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-04T15:23:38Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-04T15:23:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-08-04T15:23:39Z INF Registered tunnel connection connIndex=0 connection=7247906b-b3dd-48c1-afd0-8a624e21cd09 event=0 ip=198.41.192.227 location=lax09 protocol=quic
2026-08-04T15:23:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-04T15:23:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.67
[23:23:40] === STEP 7: 持久化 ===
[23:23:41] systemd 服务已配置
[23:23:41] Cron 保活已设置
[23:23:41] === STEP 8: 验证 ===
[23:23:41] --- API (localhost:8450) ---
 OK
[23:23:41] --- cloudflared 进程 ---
root     1006353  3.0  1.9 1294420 39252 ?       Sl   23:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1006458  0.0  1.3 1358092 27244 ?       Rl   23:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[23:23:41] --- aishield.tools ---
 OK
[23:23:42] --- DNS CNAME ---
[23:23:43] --- DNS A ---
172.67.188.44
104.21.81.46
[23:23:43] === 部署汇总 ===
[23:23:43] Tunnel Mode: cert
[23:23:43] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:23:43] API: http://localhost:8450
[23:23:43] 域名: https://aishield.tools
[23:23:43] cloudflared: /usr/local/bin/cloudflared
[23:23:43] PID: 1006353
[23:23:43] Config: /root/.cloudflared/config.yml
[23:23:43] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:23:43] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-04 23:23:41 CST; 9s ago
   Main PID: 1006454 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.3M
        CPU: 129ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1006454 /bin/bash /opt/start-tunnel.sh
             └─1006458 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                 
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
Time: Tue Aug  4 15:23:51 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785857031.5041187, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
