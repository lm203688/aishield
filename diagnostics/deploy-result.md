=== DIAGNOSTIC ===
Time: Tue Sep 8 08:44:21 AM CST 2026
=== USER ===
root
=== GIT LOG ===
fatal: detected dubious ownership in repository at '/opt/aishield'
To add an exception for this directory, call:

	git config --global --add safe.directory /opt/aishield
NO GIT REPO
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1788828261.3867404, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "baafcca0e3fad0d32a614316f9ab0d42738eb4f7", "deployed_at": "2026-09-08T00:43:50Z"}OK
=== CLOUDFLARED PROCESS ===
root      324899  1.4  1.5 1294420 31288 ?       Sl   08:44   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      324998  2.1  1.6 1294420 33360 ?       Ssl  08:44   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root      325009  2.0  1.6 1294676 33344 ?       Sl   08:44   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-08T00:44:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-09-08T00:44:10Z INF Registered tunnel connection connIndex=1 connection=d600a6e3-3dbf-4a96-8a2a-8e089973046e event=0 ip=198.41.200.23 location=sjc10 protocol=quic
2026-09-08T00:44:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-09-08T00:44:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.37
2026-09-08T00:44:12Z INF Registered tunnel connection connIndex=3 connection=004ba3a9-35b9-4a76-8fbf-5cb6382a974c event=0 ip=198.41.192.37 location=lax09 protocol=quic
2026-09-08T00:44:16Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.73
2026-09-08T00:44:16Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.73
2026-09-08T00:44:16Z INF +-------------------------------------------------------------------------------------+
2026-09-08T00:44:16Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-09-08T00:44:16Z INF +-------------------------------------------------------------------------------------+
2026-09-08T00:44:16Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-09-08T00:44:16Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-08T00:44:16Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-08T00:44:16Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-08T00:44:16Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-08T00:44:16Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-08T00:44:16Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-08T00:44:16Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-09-08T00:44:16Z INF |                                                                                     |
2026-09-08T00:44:16Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-09-08T00:44:16Z INF +-------------------------------------------------------------------------------------+
2026-09-08T00:44:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=4321c1b0-c02d-467c-bbdd-77306b945750 status=pass target=region1.v2.argotunnel.com
2026-09-08T00:44:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=4321c1b0-c02d-467c-bbdd-77306b945750 status=pass target=region2.v2.argotunnel.com
2026-09-08T00:44:16Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=4321c1b0-c02d-467c-bbdd-77306b945750 status=pass target=region1.v2.argotunnel.com
2026-09-08T00:44:16Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=4321c1b0-c02d-467c-bbdd-77306b945750 status=pass target=region2.v2.argotunnel.com
2026-09-08T00:44:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4321c1b0-c02d-467c-bbdd-77306b945750 status=pass target=region1.v2.argotunnel.com
2026-09-08T00:44:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=4321c1b0-c02d-467c-bbdd-77306b945750 status=pass target=region2.v2.argotunnel.com
2026-09-08T00:44:16Z INF precheck component="Cloudflare API" details="API is reachable" run_id=4321c1b0-c02d-467c-bbdd-77306b945750 status=pass target=api.cloudflare.com:443
2026-09-08T00:44:16Z INF precheck complete hard_fail=false run_id=4321c1b0-c02d-467c-bbdd-77306b945750 suggested_protocol=quic
2026-09-08T00:44:16Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:43:50] Time: Tue Sep  8 08:43:50 AM CST 2026
[08:43:50] User: root (UID: 0)
[08:43:50] === STEP 1: 启动 API (端口 8450) ===
[08:43:50] 代码由 runner tarball 投递，权威 sha=baafcca0
[08:43:50] commit 对比: 运行进程=a8201ff78841125f170eec9464cdd6f7cc608c48 / 磁盘=baafcca0e3fad0d32a614316f9ab0d42738eb4f7
[08:43:50] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[08:43:50] 需要重新加载代码 -> 重启 API
[08:43:51] 强制重启 Python API 进程（当前commit=a8201ff78841125f170eec9464cdd6f7cc608c48 目标=baafcca0e3fad0d32a614316f9ab0d42738eb4f7）
[08:44:01] API 状态: OK
[08:44:01] === STEP 2: 安装 cloudflared ===
[08:44:01] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:44:01] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:44:01] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:44:01] === STEP 3: 检查认证方式 ===
[08:44:01] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:44:01] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:44:01] 检查现有 tunnel...
[08:44:02] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                                            
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax05, 1xlax08, 1xlax10, 1xlax11, 1xsjc07, 1xsjc08, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                                        
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                                        
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax05, 1xlax11, 1xsjc05, 1xsjc11                                     
2026-09-08T00:44:02Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.3
[08:44:02] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:44:02] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:44:02] 凭证文件存在
[08:44:02] 创建 config.yml...
[08:44:02] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:44:02] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:44:04] DNS 路由结果: 2026-09-08T00:44:04Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:44:04] === STEP 5: 更新 DNS (API) ===
[08:44:04] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:44:05] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:44:05] 设置 SSL 模式为 Full...
SSL: 跳过
[08:44:06] === STEP 6: 启动 Tunnel ===
[08:44:09] 启动 Named Tunnel (cert 模式)...
[08:44:09] 使用 config: /root/.cloudflared/config.yml
[08:44:09] cloudflared PID: 324899
[08:44:11] Tunnel 连接已建立!
[08:44:11] --- cloudflared 日志 (最后 15 行) ---
2026-09-08T00:44:09Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-09-08T00:44:09Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-08T00:44:09Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-08T00:44:09Z INF Generated Connector ID: ecc87ed8-f923-42e8-a421-6ecdd94b21f4
2026-09-08T00:44:09Z INF Initial protocol quic
2026-09-08T00:44:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-08T00:44:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-08T00:44:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-08T00:44:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-08T00:44:09Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-09-08T00:44:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.57
2026-09-08T00:44:09Z INF Registered tunnel connection connIndex=0 connection=43b2b3db-8044-4f35-bc83-b93836fd9cfb event=0 ip=198.41.192.57 location=lax10 protocol=quic
2026-09-08T00:44:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-09-08T00:44:10Z INF Registered tunnel connection connIndex=1 connection=d600a6e3-3dbf-4a96-8a2a-8e089973046e event=0 ip=198.41.200.23 location=sjc10 protocol=quic
2026-09-08T00:44:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[08:44:11] === STEP 7: 持久化 ===
[08:44:12] systemd 服务已配置
[08:44:12] Cron 保活已设置
[08:44:12] === STEP 8: 验证 ===
[08:44:12] --- API (localhost:8450) ---
 OK
[08:44:12] --- cloudflared 进程 ---
root      324899  3.6  1.9 1294420 39476 ?       Sl   08:44   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      324998  0.0  1.3 1292484 27468 ?       Ssl  08:44   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root      325009  0.0  1.3 1292740 27228 ?       Rl   08:44   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:44:12] --- aishield.tools ---
 OK
[08:44:14] --- DNS CNAME ---
[08:44:14] --- DNS A ---
104.21.81.46
172.67.188.44
[08:44:14] === 部署汇总 ===
[08:44:14] Tunnel Mode: cert
[08:44:14] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:44:14] API: http://localhost:8450
[08:44:14] 域名: https://aishield.tools
[08:44:14] cloudflared: /usr/local/bin/cloudflared
[08:44:14] PID: 324899
[08:44:14] Config: /root/.cloudflared/config.yml
[08:44:14] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:44:14] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-09-08 08:44:12 CST; 9s ago
   Main PID: 325005 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 21.1M
        CPU: 190ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─325005 /bin/bash /opt/start-tunnel.sh
             └─325009 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=324581,fd=3))                                                     
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
Time: Tue Sep  8 00:44:29 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1788828270.3766448, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "baafcca0e3fad0d32a614316f9ab0d42738eb4f7", "deployed_at": "2026-09-08T00:43:50Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
