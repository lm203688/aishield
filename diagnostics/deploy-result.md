=== DIAGNOSTIC ===
Time: Mon Aug 31 09:57:38 PM CST 2026
=== USER ===
root
=== GIT LOG ===
c82438e8 fix(meta+rule-promoter): M3 改用运行活性判分 + rule-promoter 晋升结果带重试可靠入库（修只进不出）
9fdaa02d chore(ci-state): 更新 CI 状态总线
af0a80cd auto: 自愈闭环状态结算 [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788184658.1101325, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "c82438e8c24b6a9f693aa49adc4a8ae7733324f8", "deployed_at": "2026-08-31T09:51:46Z"}OK
=== CLOUDFLARED PROCESS ===
root     1501698  0.1  1.5 1294932 32108 ?       Sl   17:52   0:23 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1501801  0.1  1.5 1294676 31048 ?       Sl   17:52   0:23 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-31T09:52:07Z INF Registered tunnel connection connIndex=2 connection=52db805a-d86a-4d74-84ee-0ca6bd48bfb9 event=0 ip=198.41.200.53 location=sjc10 protocol=quic
2026-08-31T09:52:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.67
2026-08-31T09:52:08Z INF Registered tunnel connection connIndex=3 connection=1c0dca50-ad1d-4eef-aa04-9e45a1935235 event=0 ip=198.41.192.67 location=lax05 protocol=quic
2026-08-31T09:52:10Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.73
2026-08-31T09:52:10Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.73
2026-08-31T09:52:11Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-31T09:52:11Z INF +-------------------------------------------------------------------------------------+
2026-08-31T09:52:11Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-31T09:52:11Z INF +-------------------------------------------------------------------------------------+
2026-08-31T09:52:11Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-31T09:52:11Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-31T09:52:11Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-31T09:52:11Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-31T09:52:11Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-31T09:52:11Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-31T09:52:11Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-31T09:52:11Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-31T09:52:11Z INF |                                                                                     |
2026-08-31T09:52:11Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-31T09:52:11Z INF +-------------------------------------------------------------------------------------+
2026-08-31T09:52:11Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=912779c6-853f-4343-ba02-4bddcd6cf403 status=pass target=region1.v2.argotunnel.com
2026-08-31T09:52:11Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=912779c6-853f-4343-ba02-4bddcd6cf403 status=pass target=region2.v2.argotunnel.com
2026-08-31T09:52:11Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=912779c6-853f-4343-ba02-4bddcd6cf403 status=pass target=region1.v2.argotunnel.com
2026-08-31T09:52:11Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=912779c6-853f-4343-ba02-4bddcd6cf403 status=pass target=region2.v2.argotunnel.com
2026-08-31T09:52:11Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=912779c6-853f-4343-ba02-4bddcd6cf403 status=pass target=region1.v2.argotunnel.com
2026-08-31T09:52:11Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=912779c6-853f-4343-ba02-4bddcd6cf403 status=pass target=region2.v2.argotunnel.com
2026-08-31T09:52:11Z INF precheck component="Cloudflare API" details="API is reachable" run_id=912779c6-853f-4343-ba02-4bddcd6cf403 status=pass target=api.cloudflare.com:443
2026-08-31T09:52:11Z INF precheck complete hard_fail=false run_id=912779c6-853f-4343-ba02-4bddcd6cf403 suggested_protocol=quic
2026-08-31T09:52:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-08-31T09:52:21Z INF Registered tunnel connection connIndex=1 connection=922519df-c5f2-42a8-ae32-efe30d705eff event=0 ip=198.41.200.63 location=sjc08 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[17:51:45] Time: Mon Aug 31 05:51:45 PM CST 2026
[17:51:45] User: root (UID: 0)
[17:51:45] === STEP 1: 启动 API (端口 8450) ===
[17:51:46] HEAD: c82438e8 -> c82438e8
[17:51:46] commit 对比: 运行进程=b8a7f720b8b2cd4f089e579d30840006d40b2d94 / 磁盘=c82438e8c24b6a9f693aa49adc4a8ae7733324f8
[17:51:46] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[17:51:46] 需要重新加载代码 -> 重启 API
[17:51:46] 强制重启 Python API 进程（当前commit=b8a7f720b8b2cd4f089e579d30840006d40b2d94 目标=c82438e8c24b6a9f693aa49adc4a8ae7733324f8）
[17:51:56] API 状态: OK
[17:51:56] === STEP 2: 安装 cloudflared ===
[17:51:56] cloudflared 安装路径: /usr/local/bin/cloudflared
[17:51:57] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:51:57] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:51:57] === STEP 3: 检查认证方式 ===
[17:51:57] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[17:51:57] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[17:51:57] 检查现有 tunnel...
[17:51:58] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax07, 1xlax08, 1xsjc07, 1xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-31T09:51:58Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[17:51:58] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:51:58] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[17:51:58] 凭证文件存在
[17:51:58] 创建 config.yml...
[17:51:58] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[17:51:58] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:52:00] DNS 路由结果: 2026-08-31T09:52:00Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:52:00] === STEP 5: 更新 DNS (API) ===
[17:52:00] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:52:00] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[17:52:01] 设置 SSL 模式为 Full...
SSL: 跳过
[17:52:02] === STEP 6: 启动 Tunnel ===
[17:52:05] 启动 Named Tunnel (cert 模式)...
[17:52:05] 使用 config: /root/.cloudflared/config.yml
[17:52:05] cloudflared PID: 1501698
[17:52:07] Tunnel 连接已建立!
[17:52:07] --- cloudflared 日志 (最后 15 行) ---
2026-08-31T09:52:05Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-31T09:52:05Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-31T09:52:05Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-31T09:52:05Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-31T09:52:05Z INF Generated Connector ID: d83526d4-f4f3-4743-8295-c56b064bdf94
2026-08-31T09:52:05Z INF Initial protocol quic
2026-08-31T09:52:05Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-31T09:52:05Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-31T09:52:05Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-31T09:52:05Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-31T09:52:05Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-31T09:52:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-31T09:52:05Z INF Registered tunnel connection connIndex=0 connection=59e48fc3-d20d-4913-934e-093180db9b03 event=0 ip=198.41.192.37 location=lax09 protocol=quic
2026-08-31T09:52:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
2026-08-31T09:52:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
[17:52:07] === STEP 7: 持久化 ===
[17:52:07] systemd 服务已配置
[17:52:07] Cron 保活已设置
[17:52:07] === STEP 8: 验证 ===
[17:52:07] --- API (localhost:8450) ---
 OK
[17:52:07] --- cloudflared 进程 ---
root     1501698  4.5  1.9 1294164 38864 ?       Sl   17:52   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1501801  0.0  1.3 1292740 27408 ?       Rl   17:52   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[17:52:07] --- aishield.tools ---
 OK
[17:52:09] --- DNS CNAME ---
[17:52:09] --- DNS A ---
104.21.81.46
172.67.188.44
[17:52:09] === 部署汇总 ===
[17:52:09] Tunnel Mode: cert
[17:52:09] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:52:09] API: http://localhost:8450
[17:52:09] 域名: https://aishield.tools
[17:52:09] cloudflared: /usr/local/bin/cloudflared
[17:52:09] PID: 1501698
[17:52:09] Config: /root/.cloudflared/config.yml
[17:52:09] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:52:09] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-31 17:52:07 CST; 4h 5min ago
   Main PID: 1501793 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 17.8M
        CPU: 23.974s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1501793 /bin/bash /opt/start-tunnel.sh
             └─1501801 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=1501360,fd=3))                                                    
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
Time: Mon Aug 31 13:57:51 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788184671.5973463, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "c82438e8c24b6a9f693aa49adc4a8ae7733324f8", "deployed_at": "2026-08-31T09:51:46Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
