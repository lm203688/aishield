=== DIAGNOSTIC ===
Time: Sat Aug 29 08:43:02 PM CST 2026
=== USER ===
root
=== GIT LOG ===
95c91227 fix(ci): 清掉注释里的空表达式标记 + E8 增加空表达式拦截
3758f68e auto: 部署验证状态回写 [skip ci]
93107ff1 chore: update deploy diagnostics [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788007382.1270714, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "95c91227797dcfdd5c1987d8f078e698b7ebb512", "deployed_at": "2026-08-29T05:03:39Z"}OK
=== CLOUDFLARED PROCESS ===
root     3654316  0.1  1.4 1294676 29892 ?       Sl   13:03   0:42 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3654471  0.1  1.5 1294676 30980 ?       Sl   13:04   0:42 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-29T05:03:59Z INF Registered tunnel connection connIndex=0 connection=a87a1c96-95ea-4205-bcc6-4f03de776cab event=0 ip=198.41.192.167 location=lax11 protocol=quic
2026-08-29T05:03:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-29T05:03:59Z INF Registered tunnel connection connIndex=1 connection=1d1b7208-f77f-4a7f-9b9b-4639a10f86f4 event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-29T05:04:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-08-29T05:04:01Z INF Registered tunnel connection connIndex=2 connection=b0794b78-4cbf-4692-83af-a146ca8677f6 event=0 ip=198.41.192.7 location=lax07 protocol=quic
2026-08-29T05:04:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-08-29T05:04:01Z INF Registered tunnel connection connIndex=3 connection=7999285d-9cdd-468b-aabe-edc3a08ceebc event=0 ip=198.41.200.63 location=sjc07 protocol=quic
2026-08-29T05:04:08Z INF +-----------------------------------------------------------------------------------------------+
2026-08-29T05:04:08Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-29T05:04:08Z INF +-----------------------------------------------------------------------------------------------+
2026-08-29T05:04:08Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-29T05:04:08Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-29T05:04:08Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-29T05:04:08Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-29T05:04:08Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-29T05:04:08Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-29T05:04:08Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-29T05:04:08Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-29T05:04:08Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-29T05:04:08Z INF |                                                                                               |
2026-08-29T05:04:08Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-29T05:04:08Z INF +-----------------------------------------------------------------------------------------------+
2026-08-29T05:04:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=3b248e60-49a4-4cec-805c-b2b37a4f05e6 status=pass target=region1.v2.argotunnel.com
2026-08-29T05:04:08Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=3b248e60-49a4-4cec-805c-b2b37a4f05e6 status=pass target=region2.v2.argotunnel.com
2026-08-29T05:04:08Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=3b248e60-49a4-4cec-805c-b2b37a4f05e6 status=pass target=region1.v2.argotunnel.com
2026-08-29T05:04:08Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=3b248e60-49a4-4cec-805c-b2b37a4f05e6 status=fail target=region2.v2.argotunnel.com
2026-08-29T05:04:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=3b248e60-49a4-4cec-805c-b2b37a4f05e6 status=pass target=region1.v2.argotunnel.com
2026-08-29T05:04:08Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=3b248e60-49a4-4cec-805c-b2b37a4f05e6 status=pass target=region2.v2.argotunnel.com
2026-08-29T05:04:08Z INF precheck component="Cloudflare API" details="API is reachable" run_id=3b248e60-49a4-4cec-805c-b2b37a4f05e6 status=pass target=api.cloudflare.com:443
2026-08-29T05:04:08Z INF precheck complete hard_fail=false run_id=3b248e60-49a4-4cec-805c-b2b37a4f05e6 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[13:03:37] Time: Sat Aug 29 01:03:37 PM CST 2026
[13:03:37] User: root (UID: 0)
[13:03:37] === STEP 1: 启动 API (端口 8450) ===
[13:03:39] HEAD: 95c91227 -> 95c91227
[13:03:39] commit 对比: 运行进程=3bcb0223011fd77b4658039e3f219b3984a30e9f / 磁盘=95c91227797dcfdd5c1987d8f078e698b7ebb512
[13:03:39] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[13:03:39] 需要重新加载代码 -> 重启 API
[13:03:40] 强制重启 Python API 进程（当前commit=3bcb0223011fd77b4658039e3f219b3984a30e9f 目标=95c91227797dcfdd5c1987d8f078e698b7ebb512）
[13:03:50] API 状态: OK
[13:03:50] === STEP 2: 安装 cloudflared ===
[13:03:50] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:03:50] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:03:50] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:03:50] === STEP 3: 检查认证方式 ===
[13:03:50] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:03:50] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:03:50] 检查现有 tunnel...
[13:03:50] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                   
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax07, 2xlax09, 1xlax10, 1xsjc05, 1xsjc07, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                               
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                               
[13:03:50] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:03:50] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:03:50] 凭证文件存在
[13:03:50] 创建 config.yml...
[13:03:50] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:03:50] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:03:53] DNS 路由结果: 2026-08-29T05:03:53Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:03:53] === STEP 5: 更新 DNS (API) ===
[13:03:53] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:03:54] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:03:54] 设置 SSL 模式为 Full...
SSL: 跳过
[13:03:55] === STEP 6: 启动 Tunnel ===
[13:03:58] 启动 Named Tunnel (cert 模式)...
[13:03:58] 使用 config: /root/.cloudflared/config.yml
[13:03:58] cloudflared PID: 3654316
[13:04:00] Tunnel 连接已建立!
[13:04:00] --- cloudflared 日志 (最后 15 行) ---
2026-08-29T05:03:58Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-29T05:03:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-29T05:03:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-29T05:03:58Z INF Generated Connector ID: 804b6eaf-8659-41b2-b6bb-3ff08399bf80
2026-08-29T05:03:58Z INF Initial protocol quic
2026-08-29T05:03:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-29T05:03:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-29T05:03:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-29T05:03:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-29T05:03:58Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-29T05:03:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-29T05:03:59Z INF Registered tunnel connection connIndex=0 connection=a87a1c96-95ea-4205-bcc6-4f03de776cab event=0 ip=198.41.192.167 location=lax11 protocol=quic
2026-08-29T05:03:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-29T05:03:59Z INF Registered tunnel connection connIndex=1 connection=1d1b7208-f77f-4a7f-9b9b-4639a10f86f4 event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-29T05:04:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
[13:04:00] === STEP 7: 持久化 ===
[13:04:01] systemd 服务已配置
[13:04:01] Cron 保活已设置
[13:04:01] === STEP 8: 验证 ===
[13:04:01] --- API (localhost:8450) ---
 OK
[13:04:01] --- cloudflared 进程 ---
root     3654316  3.0  1.9 1294668 38760 ?       Sl   13:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3654471  0.0  1.3 1292484 26560 ?       Rl   13:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:04:01] --- aishield.tools ---
 OK
[13:04:02] --- DNS CNAME ---
[13:04:02] --- DNS A ---
104.21.81.46
172.67.188.44
[13:04:02] === 部署汇总 ===
[13:04:02] Tunnel Mode: cert
[13:04:02] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:04:02] API: http://localhost:8450
[13:04:02] 域名: https://aishield.tools
[13:04:02] cloudflared: /usr/local/bin/cloudflared
[13:04:02] PID: 3654316
[13:04:02] Config: /root/.cloudflared/config.yml
[13:04:02] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:04:02] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-29 13:04:01 CST; 7h ago
   Main PID: 3654467 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 20.6M
        CPU: 42.586s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3654467 /bin/bash /opt/start-tunnel.sh
             └─3654471 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3654022,fd=3))                                                    
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
Time: Sat Aug 29 12:43:14 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788007394.8763585, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "95c91227797dcfdd5c1987d8f078e698b7ebb512", "deployed_at": "2026-08-29T05:03:39Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
