=== DIAGNOSTIC ===
Time: Thu Aug 20 10:08:26 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787191706.3934352, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3376607  0.1  1.5 1294676 31948 ?       Sl   08:35   0:09 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3376750  0.1  1.6 1294932 33552 ?       Sl   08:35   0:09 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-20T00:35:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
2026-08-20T00:35:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.193
2026-08-20T00:35:51Z INF Registered tunnel connection connIndex=2 connection=79629258-0130-4fc4-b6ef-e869f9daf443 event=0 ip=198.41.192.27 location=lax11 protocol=quic
2026-08-20T00:35:55Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-08-20T00:35:55Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-08-20T00:35:55Z INF +-------------------------------------------------------------------------------------+
2026-08-20T00:35:55Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-20T00:35:55Z INF +-------------------------------------------------------------------------------------+
2026-08-20T00:35:55Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-20T00:35:55Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-20T00:35:55Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-20T00:35:55Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-20T00:35:55Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-20T00:35:55Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-20T00:35:55Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-20T00:35:55Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-20T00:35:55Z INF |                                                                                     |
2026-08-20T00:35:55Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-20T00:35:55Z INF +-------------------------------------------------------------------------------------+
2026-08-20T00:35:55Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7ba6a671-de65-4a55-8fdc-1177a36150ee status=pass target=region1.v2.argotunnel.com
2026-08-20T00:35:55Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=7ba6a671-de65-4a55-8fdc-1177a36150ee status=pass target=region2.v2.argotunnel.com
2026-08-20T00:35:55Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=7ba6a671-de65-4a55-8fdc-1177a36150ee status=pass target=region1.v2.argotunnel.com
2026-08-20T00:35:55Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=7ba6a671-de65-4a55-8fdc-1177a36150ee status=pass target=region2.v2.argotunnel.com
2026-08-20T00:35:55Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7ba6a671-de65-4a55-8fdc-1177a36150ee status=pass target=region1.v2.argotunnel.com
2026-08-20T00:35:55Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=7ba6a671-de65-4a55-8fdc-1177a36150ee status=pass target=region2.v2.argotunnel.com
2026-08-20T00:35:55Z INF precheck component="Cloudflare API" details="API is reachable" run_id=7ba6a671-de65-4a55-8fdc-1177a36150ee status=pass target=api.cloudflare.com:443
2026-08-20T00:35:55Z INF precheck complete hard_fail=false run_id=7ba6a671-de65-4a55-8fdc-1177a36150ee suggested_protocol=quic
2026-08-20T00:35:56Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
2026-08-20T00:36:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-08-20T00:36:15Z INF Registered tunnel connection connIndex=3 connection=629d2d26-26af-4081-bdeb-c5d243ae323a event=0 ip=198.41.200.63 location=lax01 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:35:35] Time: Thu Aug 20 08:35:35 AM CST 2026
[08:35:35] User: root (UID: 0)
[08:35:35] === STEP 1: 启动 API (端口 8450) ===
[08:35:37] API 已在运行
[08:35:37] API 状态: OK
[08:35:37] === STEP 2: 安装 cloudflared ===
[08:35:37] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:35:38] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:35:38] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:35:38] === STEP 3: 检查认证方式 ===
[08:35:38] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:35:38] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:35:38] 检查现有 tunnel...
[08:35:39] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax07, 1xlax08, 2xlax09 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-20T00:35:39Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:35:39] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:35:39] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:35:39] 凭证文件存在
[08:35:39] 创建 config.yml...
[08:35:39] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:35:39] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:35:41] DNS 路由结果: 2026-08-20T00:35:41Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:35:41] === STEP 5: 更新 DNS (API) ===
[08:35:41] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:35:42] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:35:43] 设置 SSL 模式为 Full...
SSL: 跳过
[08:35:44] === STEP 6: 启动 Tunnel ===
[08:35:47] 启动 Named Tunnel (cert 模式)...
[08:35:47] 使用 config: /root/.cloudflared/config.yml
[08:35:47] cloudflared PID: 3376607
[08:35:49] Tunnel 连接已建立!
[08:35:49] --- cloudflared 日志 (最后 15 行) ---
2026-08-20T00:35:47Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-20T00:35:47Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-20T00:35:47Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-20T00:35:47Z INF Generated Connector ID: 27d5ba0e-8cb3-4827-97c5-f0769b3f63b7
2026-08-20T00:35:47Z INF Initial protocol quic
2026-08-20T00:35:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T00:35:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T00:35:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-20T00:35:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-20T00:35:47Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-20T00:35:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-20T00:35:48Z INF Registered tunnel connection connIndex=0 connection=a0ade52b-4870-4ae2-bba6-c25c5895f20c event=0 ip=198.41.192.67 location=lax09 protocol=quic
2026-08-20T00:35:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-08-20T00:35:48Z INF Registered tunnel connection connIndex=1 connection=886e7939-ccc1-44d1-abbc-62f62f930863 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-20T00:35:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
[08:35:49] === STEP 7: 持久化 ===
[08:35:50] systemd 服务已配置
[08:35:50] Cron 保活已设置
[08:35:50] === STEP 8: 验证 ===
[08:35:50] --- API (localhost:8450) ---
 OK
[08:35:50] --- cloudflared 进程 ---
root     3376607  3.3  1.8 1294100 37660 ?       Sl   08:35   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3376750  0.0  1.3 1292484 27200 ?       Rl   08:35   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:35:50] --- aishield.tools ---
 OK
[08:35:52] --- DNS CNAME ---
[08:35:53] --- DNS A ---
104.21.81.46
172.67.188.44
[08:35:53] === 部署汇总 ===
[08:35:53] Tunnel Mode: cert
[08:35:53] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:35:53] API: http://localhost:8450
[08:35:53] 域名: https://aishield.tools
[08:35:53] cloudflared: /usr/local/bin/cloudflared
[08:35:53] PID: 3376607
[08:35:53] Config: /root/.cloudflared/config.yml
[08:35:53] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:35:53] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-08-20 08:35:50 CST; 1h 32min ago
   Main PID: 3376747 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.7M
        CPU: 9.461s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3376747 /bin/bash /opt/start-tunnel.sh
             └─3376750 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Thu Aug 20 02:08:26 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787191707.0108438, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
