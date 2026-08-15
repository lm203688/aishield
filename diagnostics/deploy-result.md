=== DIAGNOSTIC ===
Time: Sun Aug 16 02:01:59 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786816919.963214, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3558576  1.0  1.3 1294676 27904 ?       Sl   02:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3558680  1.7  1.4 1294676 29732 ?       Sl   02:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-15T18:01:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-15T18:01:48Z INF Registered tunnel connection connIndex=0 connection=029d3b92-14b3-4537-afba-914828cfd6f0 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-15T18:01:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-15T18:01:48Z INF Registered tunnel connection connIndex=1 connection=eb56cbac-8dc9-41b8-ab29-53d0f3a77ebd event=0 ip=198.41.192.27 location=lax10 protocol=quic
2026-08-15T18:01:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-15T18:01:49Z INF Registered tunnel connection connIndex=2 connection=15e2a522-7872-4460-8b67-3e7d60c04b80 event=0 ip=198.41.192.227 location=lax08 protocol=quic
2026-08-15T18:01:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.113
2026-08-15T18:01:50Z INF Registered tunnel connection connIndex=3 connection=5f617123-7d83-4b00-a0e7-591bdf168542 event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-15T18:01:54Z INF +-------------------------------------------------------------------------------------+
2026-08-15T18:01:54Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-15T18:01:54Z INF +-------------------------------------------------------------------------------------+
2026-08-15T18:01:54Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-15T18:01:54Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-15T18:01:54Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-15T18:01:54Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-15T18:01:54Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-15T18:01:54Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-15T18:01:54Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-15T18:01:54Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-15T18:01:54Z INF |                                                                                     |
2026-08-15T18:01:54Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-15T18:01:54Z INF +-------------------------------------------------------------------------------------+
2026-08-15T18:01:54Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=92d1377c-5a1b-4110-bcd8-861764c728ec status=pass target=region1.v2.argotunnel.com
2026-08-15T18:01:54Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=92d1377c-5a1b-4110-bcd8-861764c728ec status=pass target=region2.v2.argotunnel.com
2026-08-15T18:01:54Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=92d1377c-5a1b-4110-bcd8-861764c728ec status=pass target=region1.v2.argotunnel.com
2026-08-15T18:01:54Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=92d1377c-5a1b-4110-bcd8-861764c728ec status=pass target=region2.v2.argotunnel.com
2026-08-15T18:01:54Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=92d1377c-5a1b-4110-bcd8-861764c728ec status=pass target=region1.v2.argotunnel.com
2026-08-15T18:01:54Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=92d1377c-5a1b-4110-bcd8-861764c728ec status=pass target=region2.v2.argotunnel.com
2026-08-15T18:01:54Z INF precheck component="Cloudflare API" details="API is reachable" run_id=92d1377c-5a1b-4110-bcd8-861764c728ec status=pass target=api.cloudflare.com:443
2026-08-15T18:01:54Z INF precheck complete hard_fail=false run_id=92d1377c-5a1b-4110-bcd8-861764c728ec suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[01:59:28] Time: Sun Aug 16 01:59:28 AM CST 2026
[01:59:28] User: root (UID: 0)
[01:59:28] === STEP 1: 启动 API (端口 8450) ===
[02:01:39] API 已在运行
[02:01:39] API 状态: OK
[02:01:39] === STEP 2: 安装 cloudflared ===
[02:01:39] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:01:39] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:01:39] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:01:39] === STEP 3: 检查认证方式 ===
[02:01:39] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:01:39] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:01:39] 检查现有 tunnel...
[02:01:40] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax07, 1xlax09, 1xsjc01 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-15T18:01:40Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[02:01:40] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:01:40] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:01:40] 凭证文件存在
[02:01:40] 创建 config.yml...
[02:01:40] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:01:40] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:01:42] DNS 路由结果: 2026-08-15T18:01:42Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:01:42] === STEP 5: 更新 DNS (API) ===
[02:01:42] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:01:43] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:01:44] 设置 SSL 模式为 Full...
SSL: 跳过
[02:01:44] === STEP 6: 启动 Tunnel ===
[02:01:47] 启动 Named Tunnel (cert 模式)...
[02:01:47] 使用 config: /root/.cloudflared/config.yml
[02:01:47] cloudflared PID: 3558576
[02:01:49] Tunnel 连接已建立!
[02:01:49] --- cloudflared 日志 (最后 15 行) ---
2026-08-15T18:01:47Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-15T18:01:47Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-15T18:01:47Z INF Generated Connector ID: 6bf11efe-7d43-496f-a332-c8abdba2bd40
2026-08-15T18:01:47Z INF Initial protocol quic
2026-08-15T18:01:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T18:01:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T18:01:47Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-15T18:01:47Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-15T18:01:47Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-15T18:01:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-08-15T18:01:48Z INF Registered tunnel connection connIndex=0 connection=029d3b92-14b3-4537-afba-914828cfd6f0 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-08-15T18:01:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-15T18:01:48Z INF Registered tunnel connection connIndex=1 connection=eb56cbac-8dc9-41b8-ab29-53d0f3a77ebd event=0 ip=198.41.192.27 location=lax10 protocol=quic
2026-08-15T18:01:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-15T18:01:49Z INF Registered tunnel connection connIndex=2 connection=15e2a522-7872-4460-8b67-3e7d60c04b80 event=0 ip=198.41.192.227 location=lax08 protocol=quic
[02:01:49] === STEP 7: 持久化 ===
[02:01:50] systemd 服务已配置
[02:01:50] Cron 保活已设置
[02:01:50] === STEP 8: 验证 ===
[02:01:50] --- API (localhost:8450) ---
 OK
[02:01:50] --- cloudflared 进程 ---
root     3558576  3.0  1.9 1294420 39444 ?       Sl   02:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3558680  0.0  1.3 1292484 27672 ?       Rl   02:01   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:01:50] --- aishield.tools ---
 OK
[02:01:52] --- DNS CNAME ---
[02:01:52] --- DNS A ---
104.21.81.46
172.67.188.44
[02:01:52] === 部署汇总 ===
[02:01:52] Tunnel Mode: cert
[02:01:52] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:01:52] API: http://localhost:8450
[02:01:52] 域名: https://aishield.tools
[02:01:52] cloudflared: /usr/local/bin/cloudflared
[02:01:52] PID: 3558576
[02:01:52] Config: /root/.cloudflared/config.yml
[02:01:52] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:01:52] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-16 02:01:50 CST; 9s ago
   Main PID: 3558679 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 22.7M
        CPU: 173ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3558679 /bin/bash /opt/start-tunnel.sh
             └─3558680 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2342254,fd=3))                                                    
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
Time: Sat Aug 15 18:02:00 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786816921.1501312, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
