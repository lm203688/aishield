=== DIAGNOSTIC ===
Time: Sat Aug 29 12:44:26 PM CST 2026
=== USER ===
root
=== GIT LOG ===
f0271b32 chore(meta): 体系体检 score=83 level=degraded
47b2a651 fix(ci+deploy): 修掉 CI 全线停摆 + 部署验证门改为真门禁 + 补齐 13 条未落地雷达规则
b6ee2f07 fix(ci+deploy): 修掉 CI 全线停摆 + 部署验证门改为真门禁 + 补齐 13 条未落地雷达规则
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1787978666.3102767, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "f0271b32c130e0765ee76a146c4704aeaf48c6fa", "deployed_at": "2026-08-29T04:44:00Z"}OK
=== CLOUDFLARED PROCESS ===
root     3638921  2.8  1.9 1359444 39648 ?       Sl   12:44   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3638938  3.5  1.9 1360284 39644 ?       Sl   12:44   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3639226  3.0  1.9 1294676 38892 ?       Sl   12:44   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3639669  6.0  1.6 1293844 34140 ?       Sl   12:44   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-29T04:44:24Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.73
2026-08-29T04:44:24Z INF Retrying connection in up to 2s connIndex=0 event=0 ip=198.41.200.73
2026-08-29T04:44:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-29T04:44:24Z INF Registered tunnel connection connIndex=0 connection=a8cf1005-1071-40b4-a012-d93269cf9767 event=0 ip=198.41.192.67 location=lax11 protocol=quic
2026-08-29T04:44:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-08-29T04:44:25Z INF Registered tunnel connection connIndex=1 connection=e9e7c23f-ec25-4bfb-b20c-1abf4898e1dd event=0 ip=198.41.200.23 location=sjc07 protocol=quic
2026-08-29T04:44:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
4a3-c2d01743c69a event=0 ip=198.41.200.13 location=sjc08 protocol=quic
2026-08-29T04:44:25Z INF +-------------------------------------------------------------------------------------+
2026-08-29T04:44:25Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-29T04:44:25Z INF +-------------------------------------------------------------------------------------+
2026-08-29T04:44:25Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-29T04:44:25Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-29T04:44:25Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-29T04:44:25Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-29T04:44:25Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-29T04:44:25Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-29T04:44:25Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-29T04:44:25Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-29T04:44:25Z INF |                                                                                     |
2026-08-29T04:44:25Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-29T04:44:25Z INF +-------------------------------------------------------------------------------------+
2026-08-29T04:44:25Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=6362c584-607f-4536-9d17-2c3d46e318b0 status=pass target=region1.v2.argotunnel.com
2026-08-29T04:44:25Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=6362c584-607f-4536-9d17-2c3d46e318b0 status=pass target=region2.v2.argotunnel.com
2026-08-29T04:44:25Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=6362c584-607f-4536-9d17-2c3d46e318b0 status=pass target=region1.v2.argotunnel.com
2026-08-29T04:44:25Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=6362c584-607f-4536-9d17-2c3d46e318b0 status=pass target=region2.v2.argotunnel.com
2026-08-29T04:44:25Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=6362c584-607f-4536-9d17-2c3d46e318b0 status=pass target=region1.v2.argotunnel.com
2026-08-29T04:44:25Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=6362c584-607f-4536-9d17-2c3d46e318b0 status=pass target=region2.v2.argotunnel.com
2026-08-29T04:44:25Z INF precheck component="Cloudflare API" details="API is reachable" run_id=6362c584-607f-4536-9d17-2c3d46e318b0 status=pass target=api.cloudflare.com:443
2026-08-29T04:44:25Z INF precheck complete hard_fail=false run_id=6362c584-607f-4536-9d17-2c3d46e318b0 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:44:22] Time: Sat Aug 29 12:44:22 PM CST 2026
[12:44:22] User: root (UID: 0)
[12:44:22] === STEP 1: 启动 API (端口 8450) ===
 OK
[12:44:23] --- DNS CNAME ---
[12:44:23] --- DNS A ---
104.21.81.46
172.67.188.44
[12:44:23] === 部署汇总 ===
[12:44:23] Tunnel Mode: cert
[12:44:23] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:44:23] API: http://localhost:8450
[12:44:23] 域名: https://aishield.tools
[12:44:23] cloudflared: /usr/local/bin/cloudflared
[12:44:23] PID: 3638938
[12:44:23] Config: /root/.cloudflared/config.yml
[12:44:23] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:44:23] 状态: Named Tunnel (cert 模式) 已配置
 OK
[12:44:23] --- DNS CNAME ---
[12:44:24] --- DNS A ---
172.67.188.44
104.21.81.46
[12:44:24] === 部署汇总 ===
[12:44:24] Tunnel Mode: cert
[12:44:24] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:44:24] API: http://localhost:8450
[12:44:24] 域名: https://aishield.tools
[12:44:24] cloudflared: /usr/local/bin/cloudflared
[12:44:24] PID: 3638921
[12:44:24] Config: /root/.cloudflared/config.yml
[12:44:24] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:44:24] 状态: Named Tunnel (cert 模式) 已配置
[12:44:24] HEAD: f0271b32 -> f0271b32
[12:44:24] commit 对比: 运行进程=f0271b32c130e0765ee76a146c4704aeaf48c6fa / 磁盘=f0271b32c130e0765ee76a146c4704aeaf48c6fa
[12:44:24] 代码已是最新且 API 健康 -> 跳过重启
[12:44:24] API 状态: OK
[12:44:24] === STEP 2: 安装 cloudflared ===
[12:44:24] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:44:24] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:44:24] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:44:24] === STEP 3: 检查认证方式 ===
[12:44:24] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:44:24] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:44:24] 检查现有 tunnel...
[12:44:25] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                   
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax09, 1xlax10, 1xlax11, 2xsjc07, 1xsjc08, 3xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                               
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                               
2026-08-29T04:44:25Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[12:44:25] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:44:25] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:44:25] 凭证文件存在
[12:44:25] 创建 config.yml...
[12:44:25] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:44:25] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-08-29 12:44:22 CST; 4s ago
   Main PID: 3639213 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.6M
        CPU: 136ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3639213 /bin/bash /opt/start-tunnel.sh
             └─3639226 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3637801,fd=3))                                                    
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
Time: Sat Aug 29 04:44:26 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1787978667.1714199, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "f0271b32c130e0765ee76a146c4704aeaf48c6fa", "deployed_at": "2026-08-29T04:44:00Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
