=== DIAGNOSTIC ===
Time: Sat Sep 12 04:00:24 PM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1789200024.157353, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "81eb016a5fd4f1da0f898b66a6f811e6e41e8cd7", "deployed_at": "2026-09-12T07:59:45Z"}OK
=== CLOUDFLARED PROCESS ===
root      169523  1.0  1.9 1294676 39604 ?       Sl   16:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      169592  1.0  1.9 1294676 40056 ?       Ssl  16:00   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root      169639  1.0  1.9 1294676 40104 ?       Sl   16:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-12T08:00:09Z INF Registered tunnel connection connIndex=0 connection=dfb390c6-873c-48fc-9c00-45086edec605 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-09-12T08:00:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-09-12T08:00:10Z INF Registered tunnel connection connIndex=1 connection=fe95e5af-6965-4a7a-90af-3c780f236816 event=0 ip=198.41.200.33 location=sjc10 protocol=quic
2026-09-12T08:00:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-09-12T08:00:11Z INF Registered tunnel connection connIndex=2 connection=9808c775-0f2d-4dd3-b2fe-339d7d0064c1 event=0 ip=198.41.200.53 location=sjc10 protocol=quic
2026-09-12T08:00:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.167
2026-09-12T08:00:12Z INF Registered tunnel connection connIndex=3 connection=a197c83b-a588-4f20-97ca-f20157128e01 event=0 ip=198.41.192.167 location=lax08 protocol=quic
2026-09-12T08:00:19Z INF +-----------------------------------------------------------------------------------------------+
2026-09-12T08:00:19Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-09-12T08:00:19Z INF +-----------------------------------------------------------------------------------------------+
2026-09-12T08:00:19Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-09-12T08:00:19Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-09-12T08:00:19Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-09-12T08:00:19Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-09-12T08:00:19Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-09-12T08:00:19Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-09-12T08:00:19Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-09-12T08:00:19Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-09-12T08:00:19Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-09-12T08:00:19Z INF |                                                                                               |
2026-09-12T08:00:19Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-09-12T08:00:19Z INF +-----------------------------------------------------------------------------------------------+
2026-09-12T08:00:19Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b0caa332-dd4e-491d-b58c-e61ffd1aff6c status=pass target=region1.v2.argotunnel.com
2026-09-12T08:00:19Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b0caa332-dd4e-491d-b58c-e61ffd1aff6c status=pass target=region2.v2.argotunnel.com
2026-09-12T08:00:19Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b0caa332-dd4e-491d-b58c-e61ffd1aff6c status=pass target=region1.v2.argotunnel.com
2026-09-12T08:00:19Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=b0caa332-dd4e-491d-b58c-e61ffd1aff6c status=fail target=region2.v2.argotunnel.com
2026-09-12T08:00:19Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b0caa332-dd4e-491d-b58c-e61ffd1aff6c status=pass target=region1.v2.argotunnel.com
2026-09-12T08:00:19Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b0caa332-dd4e-491d-b58c-e61ffd1aff6c status=pass target=region2.v2.argotunnel.com
2026-09-12T08:00:19Z INF precheck component="Cloudflare API" details="API is reachable" run_id=b0caa332-dd4e-491d-b58c-e61ffd1aff6c status=pass target=api.cloudflare.com:443
2026-09-12T08:00:19Z INF precheck complete hard_fail=false run_id=b0caa332-dd4e-491d-b58c-e61ffd1aff6c suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[15:59:45] Time: Sat Sep 12 03:59:45 PM CST 2026
[15:59:45] User: root (UID: 0)
[15:59:45] === STEP 1: 启动 API (端口 8450) ===
[15:59:45] 代码由 runner tarball 投递，权威 sha=81eb016a
[15:59:45] commit 对比: 运行进程=85c1f91ccd379f3e6717546eee052040c10caa3d / 磁盘=81eb016a5fd4f1da0f898b66a6f811e6e41e8cd7
[15:59:45] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[15:59:45] 需要重新加载代码 -> 重启 API
[15:59:45] 强制重启 Python API 进程（当前commit=85c1f91ccd379f3e6717546eee052040c10caa3d 目标=81eb016a5fd4f1da0f898b66a6f811e6e41e8cd7）
[15:59:55] API 状态: OK
[15:59:55] === STEP 2: 安装 cloudflared ===
[15:59:55] cloudflared 安装路径: /usr/local/bin/cloudflared
[15:59:56] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[15:59:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[15:59:56] === STEP 3: 检查认证方式 ===
[15:59:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[15:59:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[15:59:56] 检查现有 tunnel...
[15:59:57] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax08, 2xlax09, 1xlax11, 1xsjc08, 2xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax05, 1xlax08, 1xsjc05, 1xsjc07                   
[15:59:57] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[15:59:57] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[15:59:57] 凭证文件存在
[15:59:57] 创建 config.yml...
[15:59:57] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[15:59:57] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:00:00] DNS 路由结果: 2026-09-12T08:00:00Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:00:00] === STEP 5: 更新 DNS (API) ===
[16:00:00] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:00:02] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:00:05] 设置 SSL 模式为 Full...
SSL: 跳过
[16:00:06] === STEP 6: 启动 Tunnel ===
[16:00:09] 启动 Named Tunnel (cert 模式)...
[16:00:09] 使用 config: /root/.cloudflared/config.yml
[16:00:09] cloudflared PID: 169523
[16:00:11] Tunnel 连接已建立!
[16:00:11] --- cloudflared 日志 (最后 15 行) ---
2026-09-12T08:00:09Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-12T08:00:09Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-12T08:00:09Z INF Generated Connector ID: 89214d5f-fbaf-4a2e-bf87-b44d95e41b7f
2026-09-12T08:00:09Z INF Initial protocol quic
2026-09-12T08:00:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-12T08:00:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-12T08:00:09Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-12T08:00:09Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-12T08:00:09Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-09-12T08:00:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.7
2026-09-12T08:00:09Z INF Registered tunnel connection connIndex=0 connection=dfb390c6-873c-48fc-9c00-45086edec605 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-09-12T08:00:09Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-09-12T08:00:10Z INF Registered tunnel connection connIndex=1 connection=fe95e5af-6965-4a7a-90af-3c780f236816 event=0 ip=198.41.200.33 location=sjc10 protocol=quic
2026-09-12T08:00:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-09-12T08:00:11Z INF Registered tunnel connection connIndex=2 connection=9808c775-0f2d-4dd3-b2fe-339d7d0064c1 event=0 ip=198.41.200.53 location=sjc10 protocol=quic
[16:00:11] === STEP 7: 持久化 ===
[16:00:12] systemd 服务已配置
[16:00:12] Cron 保活已设置
[16:00:12] === STEP 8: 验证 ===
[16:00:12] --- API (localhost:8450) ---
 OK
[16:00:12] --- cloudflared 进程 ---
root      169523  3.3  1.9 1294676 39336 ?       Sl   16:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      169592  0.0  1.8 1293844 37836 ?       Ssl  16:00   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root      169639  0.0  1.3 1292484 27256 ?       Rl   16:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:00:12] --- aishield.tools ---
 OK
[16:00:14] --- DNS CNAME ---
[16:00:14] --- DNS A ---
104.21.81.46
172.67.188.44
[16:00:14] === 部署汇总 ===
[16:00:14] Tunnel Mode: cert
[16:00:14] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:00:14] API: http://localhost:8450
[16:00:14] 域名: https://aishield.tools
[16:00:14] cloudflared: /usr/local/bin/cloudflared
[16:00:14] PID: 169523
[16:00:14] Config: /root/.cloudflared/config.yml
[16:00:14] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:00:14] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-09-12 16:00:12 CST; 11s ago
   Main PID: 169631 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.2M
        CPU: 140ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─169631 /bin/bash /opt/start-tunnel.sh
             └─169639 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=169074,fd=3))                                                     
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
Time: Sat Sep 12 08:00:33 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1789200033.6982872, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "81eb016a5fd4f1da0f898b66a6f811e6e41e8cd7", "deployed_at": "2026-09-12T07:59:45Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
