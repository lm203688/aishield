=== DIAGNOSTIC ===
Time: Sat Aug 29 12:59:12 PM CST 2026
=== USER ===
root
=== GIT LOG ===
3bcb0223 chore: update deploy diagnostics [skip ci]
f0271b32 chore(meta): 体系体检 score=83 level=degraded
47b2a651 fix(ci+deploy): 修掉 CI 全线停摆 + 部署验证门改为真门禁 + 补齐 13 条未落地雷达规则
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1787979552.7390127, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "3bcb0223011fd77b4658039e3f219b3984a30e9f", "deployed_at": "2026-08-29T04:44:31Z"}OK
=== CLOUDFLARED PROCESS ===
root     3650503  0.8  1.9 1294676 39684 ?       Sl   12:58   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3650637  1.0  1.9 1360284 40180 ?       Sl   12:58   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-29T04:58:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
2026-08-29T04:58:58Z INF Registered tunnel connection connIndex=0 connection=52297c75-2aea-412f-8d7c-e1d1cacaa0bf event=0 ip=198.41.192.47 location=lax09 protocol=quic
2026-08-29T04:58:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-29T04:58:59Z INF Registered tunnel connection connIndex=1 connection=7b6bcfaa-fcd6-4af2-b451-d0a22b1ba193 event=0 ip=198.41.200.43 location=sjc07 protocol=quic
2026-08-29T04:58:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-29T04:59:00Z INF Registered tunnel connection connIndex=2 connection=2ebe084c-6a41-478c-a42a-f382e81449f6 event=0 ip=198.41.200.113 location=sjc05 protocol=quic
2026-08-29T04:59:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.227
2026-08-29T04:59:01Z INF Registered tunnel connection connIndex=3 connection=f2035e88-9826-454b-807a-8fef21227d18 event=0 ip=198.41.192.227 location=lax09 protocol=quic
2026-08-29T04:59:04Z INF +-------------------------------------------------------------------------------------+
2026-08-29T04:59:04Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-29T04:59:04Z INF +-------------------------------------------------------------------------------------+
2026-08-29T04:59:04Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-29T04:59:04Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-29T04:59:04Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-29T04:59:04Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-29T04:59:04Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-29T04:59:04Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-29T04:59:04Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-29T04:59:04Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-29T04:59:04Z INF |                                                                                     |
2026-08-29T04:59:04Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-29T04:59:04Z INF +-------------------------------------------------------------------------------------+
2026-08-29T04:59:04Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=6854c20c-a869-4424-aea8-94879096e321 status=pass target=region1.v2.argotunnel.com
2026-08-29T04:59:04Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=6854c20c-a869-4424-aea8-94879096e321 status=pass target=region2.v2.argotunnel.com
2026-08-29T04:59:04Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=6854c20c-a869-4424-aea8-94879096e321 status=pass target=region1.v2.argotunnel.com
2026-08-29T04:59:04Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=6854c20c-a869-4424-aea8-94879096e321 status=pass target=region2.v2.argotunnel.com
2026-08-29T04:59:04Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=6854c20c-a869-4424-aea8-94879096e321 status=pass target=region1.v2.argotunnel.com
2026-08-29T04:59:04Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=6854c20c-a869-4424-aea8-94879096e321 status=pass target=region2.v2.argotunnel.com
2026-08-29T04:59:04Z INF precheck component="Cloudflare API" details="API is reachable" run_id=6854c20c-a869-4424-aea8-94879096e321 status=pass target=api.cloudflare.com:443
2026-08-29T04:59:04Z INF precheck complete hard_fail=false run_id=6854c20c-a869-4424-aea8-94879096e321 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:57:18] Time: Sat Aug 29 12:57:18 PM CST 2026
[12:57:18] User: root (UID: 0)
[12:57:18] === STEP 1: 启动 API (端口 8450) ===
[12:58:49] HEAD: 3bcb0223 -> 3bcb0223
[12:58:49] commit 对比: 运行进程=3bcb0223011fd77b4658039e3f219b3984a30e9f / 磁盘=3bcb0223011fd77b4658039e3f219b3984a30e9f
[12:58:49] 代码已是最新且 API 健康 -> 跳过重启
[12:58:49] API 状态: OK
[12:58:49] === STEP 2: 安装 cloudflared ===
[12:58:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:58:49] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:58:49] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:58:49] === STEP 3: 检查认证方式 ===
[12:58:49] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:58:49] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:58:49] 检查现有 tunnel...
[12:58:51] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                            
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax07, 1xlax08, 1xlax09, 1xsjc07, 1xsjc08, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                                        
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                                        
2026-08-29T04:58:51Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[12:58:51] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:58:51] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:58:51] 凭证文件存在
[12:58:51] 创建 config.yml...
[12:58:51] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:58:51] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:58:52] DNS 路由结果: 2026-08-29T04:58:52Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:58:52] === STEP 5: 更新 DNS (API) ===
[12:58:52] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:58:53] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[12:58:54] 设置 SSL 模式为 Full...
SSL: 跳过
[12:58:55] === STEP 6: 启动 Tunnel ===
[12:58:58] 启动 Named Tunnel (cert 模式)...
[12:58:58] 使用 config: /root/.cloudflared/config.yml
[12:58:58] cloudflared PID: 3650503
[12:59:00] Tunnel 连接已建立!
[12:59:00] --- cloudflared 日志 (最后 15 行) ---
2026-08-29T04:58:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-29T04:58:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-29T04:58:58Z INF Generated Connector ID: 185c0e49-d50f-4d78-ac24-2a0943ba1c59
2026-08-29T04:58:58Z INF Initial protocol quic
2026-08-29T04:58:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-29T04:58:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-29T04:58:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-29T04:58:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-29T04:58:58Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-29T04:58:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
2026-08-29T04:58:58Z INF Registered tunnel connection connIndex=0 connection=52297c75-2aea-412f-8d7c-e1d1cacaa0bf event=0 ip=198.41.192.47 location=lax09 protocol=quic
2026-08-29T04:58:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-29T04:58:59Z INF Registered tunnel connection connIndex=1 connection=7b6bcfaa-fcd6-4af2-b451-d0a22b1ba193 event=0 ip=198.41.200.43 location=sjc07 protocol=quic
2026-08-29T04:58:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-29T04:59:00Z INF Registered tunnel connection connIndex=2 connection=2ebe084c-6a41-478c-a42a-f382e81449f6 event=0 ip=198.41.200.113 location=sjc05 protocol=quic
[12:59:00] === STEP 7: 持久化 ===
[12:59:00] systemd 服务已配置
[12:59:00] Cron 保活已设置
[12:59:00] === STEP 8: 验证 ===
[12:59:00] --- API (localhost:8450) ---
 OK
[12:59:00] --- cloudflared 进程 ---
root     3650503  4.5  1.9 1294420 39144 ?       Sl   12:58   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3650637  0.0  1.3 1292740 27332 ?       Sl   12:58   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[12:59:00] --- aishield.tools ---
 OK
[12:59:02] --- DNS CNAME ---
[12:59:02] --- DNS A ---
104.21.81.46
172.67.188.44
[12:59:02] === 部署汇总 ===
[12:59:02] Tunnel Mode: cert
[12:59:02] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:59:02] API: http://localhost:8450
[12:59:02] 域名: https://aishield.tools
[12:59:02] cloudflared: /usr/local/bin/cloudflared
[12:59:02] PID: 3650503
[12:59:02] Config: /root/.cloudflared/config.yml
[12:59:02] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:59:02] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-29 12:59:00 CST; 12s ago
   Main PID: 3650633 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.4M
        CPU: 134ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3650633 /bin/bash /opt/start-tunnel.sh
             └─3650637 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3640203,fd=3))                                                    
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
Time: Sat Aug 29 04:59:20 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1787979561.14526, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "3bcb0223011fd77b4658039e3f219b3984a30e9f", "deployed_at": "2026-08-29T04:44:31Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
