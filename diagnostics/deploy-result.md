=== DIAGNOSTIC ===
Time: Tue Aug 4 05:59:17 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785794357.2955856, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      261877  0.9  1.9 1294676 39792 ?       Sl   05:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      261986  1.3  1.9 1294676 39648 ?       Sl   05:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-03T21:59:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-03T21:59:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-03T21:59:07Z INF Registered tunnel connection connIndex=2 connection=bb7adf6b-c83e-47d5-8238-4dcd961ba20a event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-03T21:59:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.27
2026-08-03T21:59:08Z INF Registered tunnel connection connIndex=3 connection=d45854dd-9d0b-4c3a-8ade-5f5a210b1fe4 event=0 ip=198.41.192.27 location=lax09 protocol=quic
2026-08-03T21:59:11Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.193
2026-08-03T21:59:11Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.193
2026-08-03T21:59:12Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-03T21:59:12Z INF +-------------------------------------------------------------------------------------+
2026-08-03T21:59:12Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-03T21:59:12Z INF +-------------------------------------------------------------------------------------+
2026-08-03T21:59:12Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-03T21:59:12Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-03T21:59:12Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-03T21:59:12Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-03T21:59:12Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-03T21:59:12Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-03T21:59:12Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-03T21:59:12Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-03T21:59:12Z INF |                                                                                     |
2026-08-03T21:59:12Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-03T21:59:12Z INF +-------------------------------------------------------------------------------------+
2026-08-03T21:59:12Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c5534cc0-c6ca-4914-9e8c-76259858dec9 status=pass target=region1.v2.argotunnel.com
2026-08-03T21:59:12Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c5534cc0-c6ca-4914-9e8c-76259858dec9 status=pass target=region2.v2.argotunnel.com
2026-08-03T21:59:12Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c5534cc0-c6ca-4914-9e8c-76259858dec9 status=pass target=region1.v2.argotunnel.com
2026-08-03T21:59:12Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c5534cc0-c6ca-4914-9e8c-76259858dec9 status=pass target=region2.v2.argotunnel.com
2026-08-03T21:59:12Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c5534cc0-c6ca-4914-9e8c-76259858dec9 status=pass target=region1.v2.argotunnel.com
2026-08-03T21:59:12Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c5534cc0-c6ca-4914-9e8c-76259858dec9 status=pass target=region2.v2.argotunnel.com
2026-08-03T21:59:12Z INF precheck component="Cloudflare API" details="API is reachable" run_id=c5534cc0-c6ca-4914-9e8c-76259858dec9 status=pass target=api.cloudflare.com:443
2026-08-03T21:59:12Z INF precheck complete hard_fail=false run_id=c5534cc0-c6ca-4914-9e8c-76259858dec9 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[05:58:56] Time: Tue Aug  4 05:58:56 AM CST 2026
[05:58:56] User: root (UID: 0)
[05:58:56] === STEP 1: 启动 API (端口 8450) ===
[05:58:58] API 已在运行
[05:58:58] API 状态: OK
[05:58:58] === STEP 2: 安装 cloudflared ===
[05:58:58] cloudflared 安装路径: /usr/local/bin/cloudflared
[05:58:58] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[05:58:58] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[05:58:58] === STEP 3: 检查认证方式 ===
[05:58:58] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[05:58:58] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[05:58:58] 检查现有 tunnel...
[05:58:59] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax09, 2xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[05:58:59] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[05:58:59] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[05:58:59] 凭证文件存在
[05:58:59] 创建 config.yml...
[05:58:59] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[05:58:59] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[05:59:00] DNS 路由结果: 2026-08-03T21:59:00Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[05:59:00] === STEP 5: 更新 DNS (API) ===
[05:59:00] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[05:59:01] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[05:59:02] 设置 SSL 模式为 Full...
SSL: 跳过
[05:59:02] === STEP 6: 启动 Tunnel ===
[05:59:05] 启动 Named Tunnel (cert 模式)...
[05:59:05] 使用 config: /root/.cloudflared/config.yml
[05:59:05] cloudflared PID: 261877
[05:59:07] Tunnel 连接已建立!
[05:59:07] --- cloudflared 日志 (最后 15 行) ---
2026-08-03T21:59:05Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-03T21:59:05Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-03T21:59:05Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-03T21:59:05Z INF Generated Connector ID: 91aae3f2-6b5a-4e2d-b525-2b544dd4bd12
2026-08-03T21:59:05Z INF Initial protocol quic
2026-08-03T21:59:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-03T21:59:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-03T21:59:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-03T21:59:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-03T21:59:06Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-03T21:59:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.57
2026-08-03T21:59:06Z INF Registered tunnel connection connIndex=0 connection=3d3bb468-9335-4327-8bf7-e8872bfa0f79 event=0 ip=198.41.192.57 location=lax10 protocol=quic
2026-08-03T21:59:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-03T21:59:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-03T21:59:07Z INF Registered tunnel connection connIndex=2 connection=bb7adf6b-c83e-47d5-8238-4dcd961ba20a event=0 ip=198.41.200.113 location=lax01 protocol=quic
[05:59:07] === STEP 7: 持久化 ===
[05:59:08] systemd 服务已配置
[05:59:08] Cron 保活已设置
[05:59:08] === STEP 8: 验证 ===
[05:59:08] --- API (localhost:8450) ---
 OK
[05:59:08] --- cloudflared 进程 ---
root      261877  3.3  1.9 1294420 39268 ?       Sl   05:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      261986  0.0  1.3 1292484 27556 ?       Rl   05:59   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[05:59:08] --- aishield.tools ---
 OK
[05:59:10] --- DNS CNAME ---
[05:59:10] --- DNS A ---
172.67.188.44
104.21.81.46
[05:59:10] === 部署汇总 ===
[05:59:10] Tunnel Mode: cert
[05:59:10] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[05:59:10] API: http://localhost:8450
[05:59:10] 域名: https://aishield.tools
[05:59:10] cloudflared: /usr/local/bin/cloudflared
[05:59:10] PID: 261877
[05:59:10] Config: /root/.cloudflared/config.yml
[05:59:10] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[05:59:10] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-08-04 05:59:08 CST; 8s ago
   Main PID: 261978 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.9M
        CPU: 128ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─261978 /bin/bash /opt/start-tunnel.sh
             └─261986 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug  3 21:59:17 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785794358.3282268, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
