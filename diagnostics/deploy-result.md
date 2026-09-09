=== DIAGNOSTIC ===
Time: Wed Sep 9 04:13:22 PM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1788941602.7922642, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "60e78aab40558f06f9e3d1b5279d716fbe8b2afb", "deployed_at": "2026-09-09T08:12:44Z"}OK
=== CLOUDFLARED PROCESS ===
root     1538313  0.8  1.8 1360284 37604 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1538391  1.1  1.7 1294676 35996 ?       Ssl  16:13   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1538460  1.1  1.8 1294676 38092 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-09T08:13:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-09-09T08:13:10Z INF Registered tunnel connection connIndex=3 connection=946e7d27-96b2-49bd-aff6-3c9af51801ff event=0 ip=198.41.192.47 location=lax09 protocol=quic
2026-09-09T08:13:12Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.193
2026-09-09T08:13:12Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.193
2026-09-09T08:13:14Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-09-09T08:13:16Z INF +-----------------------------------------------------------------------------------------------+
2026-09-09T08:13:16Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-09-09T08:13:16Z INF +-----------------------------------------------------------------------------------------------+
2026-09-09T08:13:16Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-09-09T08:13:16Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-09-09T08:13:16Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-09-09T08:13:16Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-09-09T08:13:16Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-09-09T08:13:16Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-09-09T08:13:16Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-09-09T08:13:16Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-09-09T08:13:16Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-09-09T08:13:16Z INF |                                                                                               |
2026-09-09T08:13:16Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-09-09T08:13:16Z INF +-----------------------------------------------------------------------------------------------+
2026-09-09T08:13:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8dd86d8d-9a0a-424e-aa29-f608e6c82fd9 status=pass target=region1.v2.argotunnel.com
2026-09-09T08:13:16Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8dd86d8d-9a0a-424e-aa29-f608e6c82fd9 status=pass target=region2.v2.argotunnel.com
2026-09-09T08:13:16Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8dd86d8d-9a0a-424e-aa29-f608e6c82fd9 status=pass target=region1.v2.argotunnel.com
2026-09-09T08:13:16Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=8dd86d8d-9a0a-424e-aa29-f608e6c82fd9 status=fail target=region2.v2.argotunnel.com
2026-09-09T08:13:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8dd86d8d-9a0a-424e-aa29-f608e6c82fd9 status=pass target=region1.v2.argotunnel.com
2026-09-09T08:13:16Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8dd86d8d-9a0a-424e-aa29-f608e6c82fd9 status=pass target=region2.v2.argotunnel.com
2026-09-09T08:13:16Z INF precheck component="Cloudflare API" details="API is reachable" run_id=8dd86d8d-9a0a-424e-aa29-f608e6c82fd9 status=pass target=api.cloudflare.com:443
2026-09-09T08:13:16Z INF precheck complete hard_fail=false run_id=8dd86d8d-9a0a-424e-aa29-f608e6c82fd9 suggested_protocol=http2
2026-09-09T08:13:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-09-09T08:13:21Z INF Registered tunnel connection connIndex=1 connection=48681222-9f6c-4a73-8917-832c5cab1bc2 event=0 ip=198.41.200.43 location=sjc05 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:12:44] Time: Wed Sep  9 04:12:44 PM CST 2026
[16:12:44] User: root (UID: 0)
[16:12:44] === STEP 1: 启动 API (端口 8450) ===
[16:12:44] 代码由 runner tarball 投递，权威 sha=60e78aab
[16:12:44] commit 对比: 运行进程=b524162ee1da7489148fdd3d643bfa70035512fe / 磁盘=60e78aab40558f06f9e3d1b5279d716fbe8b2afb
[16:12:44] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[16:12:44] 需要重新加载代码 -> 重启 API
[16:12:45] 强制重启 Python API 进程（当前commit=b524162ee1da7489148fdd3d643bfa70035512fe 目标=60e78aab40558f06f9e3d1b5279d716fbe8b2afb）
[16:12:55] API 状态: OK
[16:12:55] === STEP 2: 安装 cloudflared ===
[16:12:55] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:12:55] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:12:55] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:12:55] === STEP 3: 检查认证方式 ===
[16:12:55] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:12:55] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:12:55] 检查现有 tunnel...
[16:12:56] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax07, 2xlax08, 1xlax10, 1xsjc07, 2xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax08, 1xlax12, 1xsjc05, 1xsjc10                   
[16:12:56] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:12:56] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:12:56] 凭证文件存在
[16:12:56] 创建 config.yml...
[16:12:56] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:12:56] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:00] DNS 路由结果: 2026-09-09T08:13:00Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:00] === STEP 5: 更新 DNS (API) ===
[16:13:00] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:01] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:13:03] 设置 SSL 模式为 Full...
SSL: 跳过
[16:13:03] === STEP 6: 启动 Tunnel ===
[16:13:06] 启动 Named Tunnel (cert 模式)...
[16:13:06] 使用 config: /root/.cloudflared/config.yml
[16:13:06] cloudflared PID: 1538313
[16:13:08] Tunnel 连接已建立!
[16:13:08] --- cloudflared 日志 (最后 15 行) ---
2026-09-09T08:13:06Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-09-09T08:13:06Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-09T08:13:06Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-09T08:13:06Z INF Generated Connector ID: 20065d3d-22aa-4c95-8281-e864a22141f9
2026-09-09T08:13:06Z INF Initial protocol quic
2026-09-09T08:13:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-09T08:13:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-09T08:13:07Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-09T08:13:07Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-09T08:13:07Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-09-09T08:13:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-09-09T08:13:07Z INF Registered tunnel connection connIndex=0 connection=f6810776-478a-4af2-b60e-5df303cd0300 event=0 ip=198.41.192.107 location=lax10 protocol=quic
2026-09-09T08:13:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-09-09T08:13:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-09-09T08:13:08Z INF Registered tunnel connection connIndex=2 connection=d03f0164-2003-4fb8-a9e3-c57cdba0681a event=0 ip=198.41.200.113 location=sjc10 protocol=quic
[16:13:08] === STEP 7: 持久化 ===
[16:13:10] systemd 服务已配置
[16:13:10] Cron 保活已设置
[16:13:10] === STEP 8: 验证 ===
[16:13:10] --- API (localhost:8450) ---
 OK
[16:13:10] --- cloudflared 进程 ---
root     1538313  2.2  1.9 1360284 38840 ?       Sl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1538391  0.0  1.8 1293844 36264 ?       Ssl  16:13   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1538460  0.0  1.3 1292484 27588 ?       Rl   16:13   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:13:10] --- aishield.tools ---
 OK
[16:13:12] --- DNS CNAME ---
[16:13:12] --- DNS A ---
172.67.188.44
104.21.81.46
[16:13:12] === 部署汇总 ===
[16:13:12] Tunnel Mode: cert
[16:13:12] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:13:12] API: http://localhost:8450
[16:13:12] 域名: https://aishield.tools
[16:13:12] cloudflared: /usr/local/bin/cloudflared
[16:13:12] PID: 1538313
[16:13:12] Config: /root/.cloudflared/config.yml
[16:13:12] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:13:12] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-09-09 16:13:10 CST; 12s ago
   Main PID: 1538452 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 19.0M
        CPU: 154ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1538452 /bin/bash /opt/start-tunnel.sh
             └─1538460 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=1537942,fd=3))                                                    
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
Time: Wed Sep  9 08:13:35 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1788941615.581773, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "60e78aab40558f06f9e3d1b5279d716fbe8b2afb", "deployed_at": "2026-09-09T08:12:44Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
