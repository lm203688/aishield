=== DIAGNOSTIC ===
Time: Fri Aug 28 11:50:42 PM CST 2026
=== USER ===
root
=== GIT LOG ===
438464b1 chore(meta): 体系体检 score=83 level=degraded
7732d15e fix(deploy): read nested serverInfo.version, and force restart on version mismatch
d895572d auto: 部署验证状态回写 [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 215, "uptime": 1787932242.402942, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3125929  0.8  1.9 1294420 40004 ?       Sl   23:50   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3126029  0.8  1.9 1360284 39396 ?       Sl   23:50   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T15:50:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-08-28T15:50:25Z INF Registered tunnel connection connIndex=0 connection=0a63cfc7-43de-4bcd-99d2-977d157648ed event=0 ip=198.41.192.77 location=lax10 protocol=quic
2026-08-28T15:50:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-28T15:50:26Z INF Registered tunnel connection connIndex=1 connection=cd0ab427-4a5f-4340-9c32-77e44a6eb027 event=0 ip=198.41.200.13 location=sjc05 protocol=quic
2026-08-28T15:50:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-28T15:50:27Z INF Registered tunnel connection connIndex=2 connection=3e77ed8b-0890-4bbf-bf90-54dab8a0dacb event=0 ip=198.41.200.53 location=sjc07 protocol=quic
2026-08-28T15:50:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.7
2026-08-28T15:50:28Z INF Registered tunnel connection connIndex=3 connection=eb27c989-81ad-413f-ab53-0fc77b401207 event=0 ip=198.41.192.7 location=lax05 protocol=quic
2026-08-28T15:50:31Z INF +-------------------------------------------------------------------------------------+
2026-08-28T15:50:31Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-28T15:50:31Z INF +-------------------------------------------------------------------------------------+
2026-08-28T15:50:31Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-28T15:50:31Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T15:50:31Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T15:50:31Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T15:50:31Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T15:50:31Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T15:50:31Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T15:50:31Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-28T15:50:31Z INF |                                                                                     |
2026-08-28T15:50:31Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-28T15:50:31Z INF +-------------------------------------------------------------------------------------+
2026-08-28T15:50:31Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=829368ec-1457-47b2-9fc3-117de932f240 status=pass target=region1.v2.argotunnel.com
2026-08-28T15:50:31Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=829368ec-1457-47b2-9fc3-117de932f240 status=pass target=region2.v2.argotunnel.com
2026-08-28T15:50:31Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=829368ec-1457-47b2-9fc3-117de932f240 status=pass target=region1.v2.argotunnel.com
2026-08-28T15:50:31Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=829368ec-1457-47b2-9fc3-117de932f240 status=pass target=region2.v2.argotunnel.com
2026-08-28T15:50:31Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=829368ec-1457-47b2-9fc3-117de932f240 status=pass target=region1.v2.argotunnel.com
2026-08-28T15:50:31Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=829368ec-1457-47b2-9fc3-117de932f240 status=pass target=region2.v2.argotunnel.com
2026-08-28T15:50:31Z INF precheck component="Cloudflare API" details="API is reachable" run_id=829368ec-1457-47b2-9fc3-117de932f240 status=pass target=api.cloudflare.com:443
2026-08-28T15:50:31Z INF precheck complete hard_fail=false run_id=829368ec-1457-47b2-9fc3-117de932f240 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:50:01] Time: Fri Aug 28 11:50:01 PM CST 2026
[23:50:01] User: root (UID: 0)
[23:50:01] === STEP 1: 启动 API (端口 8450) ===
[23:50:02] HEAD: 438464b1 -> 438464b1
[23:50:04] server-card 版本: 磁盘=4.3.0 仓库=4.3.0
[23:50:04] 运行进程自报版本=4.2 / 磁盘代码版本=4.3.0
[23:50:04] 运行进程落后于磁盘代码 -> 标记重启
[23:50:04] 需要重新加载代码 -> 重启 API
[23:50:04] 强制重启 Python API 进程（当前=4.2 目标=4.3.0）
[23:50:14] API 状态: OK
[23:50:14] === STEP 2: 安装 cloudflared ===
[23:50:14] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:50:14] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:50:14] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:50:14] === STEP 3: 检查认证方式 ===
[23:50:14] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:50:14] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:50:14] 检查现有 tunnel...
[23:50:16] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                   
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax10, 1xlax11, 1xlax12, 1xsjc05, 1xsjc08, 2xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                               
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                               
2026-08-28T15:50:16Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[23:50:16] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:50:16] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:50:16] 凭证文件存在
[23:50:16] 创建 config.yml...
[23:50:16] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:50:16] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:50:19] DNS 路由结果: 2026-08-28T15:50:19Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:50:19] === STEP 5: 更新 DNS (API) ===
[23:50:19] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:50:20] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[23:50:21] 设置 SSL 模式为 Full...
SSL: 跳过
[23:50:21] === STEP 6: 启动 Tunnel ===
[23:50:24] 启动 Named Tunnel (cert 模式)...
[23:50:24] 使用 config: /root/.cloudflared/config.yml
[23:50:25] cloudflared PID: 3125929
[23:50:27] Tunnel 连接已建立!
[23:50:27] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T15:50:25Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-28T15:50:25Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T15:50:25Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T15:50:25Z INF Generated Connector ID: 8659da44-8d9f-45e3-97c1-ad440f25055d
2026-08-28T15:50:25Z INF Initial protocol quic
2026-08-28T15:50:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:50:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:50:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:50:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:50:25Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T15:50:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-08-28T15:50:25Z INF Registered tunnel connection connIndex=0 connection=0a63cfc7-43de-4bcd-99d2-977d157648ed event=0 ip=198.41.192.77 location=lax10 protocol=quic
2026-08-28T15:50:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-08-28T15:50:26Z INF Registered tunnel connection connIndex=1 connection=cd0ab427-4a5f-4340-9c32-77e44a6eb027 event=0 ip=198.41.200.13 location=sjc05 protocol=quic
2026-08-28T15:50:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
[23:50:27] === STEP 7: 持久化 ===
[23:50:27] systemd 服务已配置
[23:50:27] Cron 保活已设置
[23:50:27] === STEP 8: 验证 ===
[23:50:27] --- API (localhost:8450) ---
 OK
[23:50:27] --- cloudflared 进程 ---
root     3125929  5.0  1.9 1294420 39728 ?       Sl   23:50   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3126029  0.0  1.3 1292740 27196 ?       Rl   23:50   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[23:50:27] --- aishield.tools ---
 OK
[23:50:29] --- DNS CNAME ---
[23:50:29] --- DNS A ---
172.67.188.44
104.21.81.46
[23:50:29] === 部署汇总 ===
[23:50:29] Tunnel Mode: cert
[23:50:29] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:50:29] API: http://localhost:8450
[23:50:29] 域名: https://aishield.tools
[23:50:29] cloudflared: /usr/local/bin/cloudflared
[23:50:29] PID: 3125929
[23:50:29] Config: /root/.cloudflared/config.yml
[23:50:29] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:50:29] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 23:50:27 CST; 14s ago
   Main PID: 3126028 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.8M
        CPU: 146ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3126028 /bin/bash /opt/start-tunnel.sh
             └─3126029 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3125577,fd=3))                                                    
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
Time: Fri Aug 28 15:50:42 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 215, "uptime": 1787932243.1272197, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
