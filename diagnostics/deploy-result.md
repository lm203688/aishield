=== DIAGNOSTIC ===
Time: Fri Sep 11 04:08:42 PM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1789114122.3454206, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "85c1f91ccd379f3e6717546eee052040c10caa3d", "deployed_at": "2026-09-11T08:08:07Z"}OK
=== CLOUDFLARED PROCESS ===
root     3421259  0.8  1.9 1294420 39360 ?       Sl   16:08   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3421364  1.2  2.0 1294676 40436 ?       Ssl  16:08   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     3421378  1.2  1.9 1360028 40188 ?       Sl   16:08   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-11T08:08:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-09-11T08:08:29Z INF Registered tunnel connection connIndex=1 connection=22ceaa8f-24e1-4641-b449-b43d3ab6cadf event=0 ip=198.41.192.57 location=lax09 protocol=quic
2026-09-11T08:08:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-09-11T08:08:30Z INF Registered tunnel connection connIndex=2 connection=0e3d413e-2b83-4d5e-b645-160ba2e5b4a2 event=0 ip=198.41.192.227 location=lax08 protocol=quic
2026-09-11T08:08:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
2026-09-11T08:08:35Z INF +-------------------------------------------------------------------------------------+
2026-09-11T08:08:35Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-09-11T08:08:35Z INF +-------------------------------------------------------------------------------------+
2026-09-11T08:08:35Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-09-11T08:08:35Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-11T08:08:35Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-11T08:08:35Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-11T08:08:35Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-11T08:08:35Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-11T08:08:35Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-11T08:08:35Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-09-11T08:08:35Z INF |                                                                                     |
2026-09-11T08:08:35Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-09-11T08:08:35Z INF +-------------------------------------------------------------------------------------+
2026-09-11T08:08:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=726faa03-c49c-4bfc-b15e-d44db2d2b3a3 status=pass target=region1.v2.argotunnel.com
2026-09-11T08:08:35Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=726faa03-c49c-4bfc-b15e-d44db2d2b3a3 status=pass target=region2.v2.argotunnel.com
2026-09-11T08:08:35Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=726faa03-c49c-4bfc-b15e-d44db2d2b3a3 status=pass target=region1.v2.argotunnel.com
2026-09-11T08:08:35Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=726faa03-c49c-4bfc-b15e-d44db2d2b3a3 status=pass target=region2.v2.argotunnel.com
2026-09-11T08:08:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=726faa03-c49c-4bfc-b15e-d44db2d2b3a3 status=pass target=region1.v2.argotunnel.com
2026-09-11T08:08:35Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=726faa03-c49c-4bfc-b15e-d44db2d2b3a3 status=pass target=region2.v2.argotunnel.com
2026-09-11T08:08:35Z INF precheck component="Cloudflare API" details="API is reachable" run_id=726faa03-c49c-4bfc-b15e-d44db2d2b3a3 status=pass target=api.cloudflare.com:443
2026-09-11T08:08:35Z INF precheck complete hard_fail=false run_id=726faa03-c49c-4bfc-b15e-d44db2d2b3a3 suggested_protocol=quic
2026-09-11T08:08:36Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-09-11T08:08:36Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.73
2026-09-11T08:08:37Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:08:07] Time: Fri Sep 11 04:08:07 PM CST 2026
[16:08:07] User: root (UID: 0)
[16:08:07] === STEP 1: 启动 API (端口 8450) ===
[16:08:07] 代码由 runner tarball 投递，权威 sha=85c1f91c
[16:08:07] commit 对比: 运行进程=2e12c70baaf961a13ecc3f562b90b8a6df0eeb3e / 磁盘=85c1f91ccd379f3e6717546eee052040c10caa3d
[16:08:07] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[16:08:07] 需要重新加载代码 -> 重启 API
[16:08:07] 强制重启 Python API 进程（当前commit=2e12c70baaf961a13ecc3f562b90b8a6df0eeb3e 目标=85c1f91ccd379f3e6717546eee052040c10caa3d）
[16:08:17] API 状态: OK
[16:08:17] === STEP 2: 安装 cloudflared ===
[16:08:17] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:08:17] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:08:17] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:08:17] === STEP 3: 检查认证方式 ===
[16:08:17] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:08:17] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:08:17] 检查现有 tunnel...
[16:08:19] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax05, 1xlax07, 2xlax08, 1xsjc05, 1xsjc08, 2xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax12, 1xsjc06, 2xsjc11                            
2026-09-11T08:08:19Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.9.0
[16:08:19] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:08:19] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:08:19] 凭证文件存在
[16:08:19] 创建 config.yml...
[16:08:19] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:08:19] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:08:22] DNS 路由结果: 2026-09-11T08:08:22Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:08:22] === STEP 5: 更新 DNS (API) ===
[16:08:22] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:08:24] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:08:24] 设置 SSL 模式为 Full...
SSL: 跳过
[16:08:25] === STEP 6: 启动 Tunnel ===
[16:08:28] 启动 Named Tunnel (cert 模式)...
[16:08:28] 使用 config: /root/.cloudflared/config.yml
[16:08:28] cloudflared PID: 3421259
[16:08:30] Tunnel 连接已建立!
[16:08:30] --- cloudflared 日志 (最后 15 行) ---
2026-09-11T08:08:28Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-09-11T08:08:28Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-11T08:08:28Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-11T08:08:28Z INF Generated Connector ID: 952f0529-35ee-492d-affe-c204b8e880f9
2026-09-11T08:08:28Z INF Initial protocol quic
2026-09-11T08:08:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-11T08:08:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-11T08:08:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-11T08:08:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-11T08:08:28Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-09-11T08:08:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-09-11T08:08:29Z INF Registered tunnel connection connIndex=0 connection=7ddf1c08-ddcc-4fee-8a60-6cbe855fa2f2 event=0 ip=198.41.200.43 location=sjc11 protocol=quic
2026-09-11T08:08:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-09-11T08:08:29Z INF Registered tunnel connection connIndex=1 connection=22ceaa8f-24e1-4641-b449-b43d3ab6cadf event=0 ip=198.41.192.57 location=lax09 protocol=quic
2026-09-11T08:08:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
[16:08:30] === STEP 7: 持久化 ===
[16:08:31] systemd 服务已配置
[16:08:31] Cron 保活已设置
[16:08:31] === STEP 8: 验证 ===
[16:08:31] --- API (localhost:8450) ---
 OK
[16:08:31] --- cloudflared 进程 ---
root     3421259  3.0  1.9 1294420 39140 ?       Sl   16:08   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3421364  0.0  1.3 1292484 26988 ?       Rsl  16:08   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     3421378  0.0  1.3 1358092 27376 ?       Rl   16:08   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:08:31] --- aishield.tools ---
 OK
[16:08:33] --- DNS CNAME ---
[16:08:33] --- DNS A ---
172.67.188.44
104.21.81.46
[16:08:33] === 部署汇总 ===
[16:08:33] Tunnel Mode: cert
[16:08:33] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:08:33] API: http://localhost:8450
[16:08:33] 域名: https://aishield.tools
[16:08:33] cloudflared: /usr/local/bin/cloudflared
[16:08:33] PID: 3421259
[16:08:33] Config: /root/.cloudflared/config.yml
[16:08:33] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:08:33] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-09-11 16:08:31 CST; 10s ago
   Main PID: 3421375 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.3M
        CPU: 151ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3421375 /bin/bash /opt/start-tunnel.sh
             └─3421378 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3420938,fd=3))                                                    
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
Time: Fri Sep 11 08:08:53 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1789114133.7198157, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "85c1f91ccd379f3e6717546eee052040c10caa3d", "deployed_at": "2026-09-11T08:08:07Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
