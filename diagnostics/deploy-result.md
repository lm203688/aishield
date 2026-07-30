=== DIAGNOSTIC ===
Time: Fri Jul 31 07:21:34 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785453694.0533004, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root      411957  1.4  1.9 1294420 40044 ?       Sl   07:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      412073  1.5  1.9 1294676 39000 ?       Sl   07:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-07-30T23:21:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-07-30T23:21:25Z INF Registered tunnel connection connIndex=0 connection=2b930e28-b314-45ff-8530-20d504500fe1 event=0 ip=198.41.192.77 location=lax05 protocol=quic
2026-07-30T23:21:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-07-30T23:21:25Z INF Registered tunnel connection connIndex=1 connection=bc25bda0-6573-4884-8c9c-5527c3a83058 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-07-30T23:21:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-07-30T23:21:27Z INF Registered tunnel connection connIndex=2 connection=1a0ed3c7-83ce-46dd-9cb9-e5a88e60b204 event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-07-30T23:21:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.27
2026-07-30T23:21:27Z INF Registered tunnel connection connIndex=3 connection=a49f8bde-8391-43b2-9a5b-a33d0f195ec6 event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-07-30T23:21:31Z INF +-------------------------------------------------------------------------------------+
2026-07-30T23:21:31Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-07-30T23:21:31Z INF +-------------------------------------------------------------------------------------+
2026-07-30T23:21:31Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-07-30T23:21:31Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-07-30T23:21:31Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-07-30T23:21:31Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-07-30T23:21:31Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-07-30T23:21:31Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-07-30T23:21:31Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-07-30T23:21:31Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-07-30T23:21:31Z INF |                                                                                     |
2026-07-30T23:21:31Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-07-30T23:21:31Z INF +-------------------------------------------------------------------------------------+
2026-07-30T23:21:31Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=448c8dc3-61bc-400e-8e1a-cf08820c7763 status=pass target=region1.v2.argotunnel.com
2026-07-30T23:21:31Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=448c8dc3-61bc-400e-8e1a-cf08820c7763 status=pass target=region2.v2.argotunnel.com
2026-07-30T23:21:31Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=448c8dc3-61bc-400e-8e1a-cf08820c7763 status=pass target=region1.v2.argotunnel.com
2026-07-30T23:21:31Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=448c8dc3-61bc-400e-8e1a-cf08820c7763 status=pass target=region2.v2.argotunnel.com
2026-07-30T23:21:31Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=448c8dc3-61bc-400e-8e1a-cf08820c7763 status=pass target=region1.v2.argotunnel.com
2026-07-30T23:21:31Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=448c8dc3-61bc-400e-8e1a-cf08820c7763 status=pass target=region2.v2.argotunnel.com
2026-07-30T23:21:31Z INF precheck component="Cloudflare API" details="API is reachable" run_id=448c8dc3-61bc-400e-8e1a-cf08820c7763 status=pass target=api.cloudflare.com:443
2026-07-30T23:21:31Z INF precheck complete hard_fail=false run_id=448c8dc3-61bc-400e-8e1a-cf08820c7763 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[07:21:17] Time: Fri Jul 31 07:21:17 AM CST 2026
[07:21:17] User: root (UID: 0)
[07:21:17] === STEP 1: 启动 API (端口 8450) ===
[07:21:18] API 已在运行
[07:21:18] API 状态: OK
[07:21:18] === STEP 2: 安装 cloudflared ===
[07:21:18] cloudflared 安装路径: /usr/local/bin/cloudflared
[07:21:18] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:21:18] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[07:21:18] === STEP 3: 检查认证方式 ===
[07:21:18] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[07:21:18] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[07:21:18] 检查现有 tunnel...
[07:21:19] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME           CREATED              CONNECTIONS 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools 2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens     2026-07-28T03:03:32Z             
[07:21:19] 创建新 tunnel: aishield-tunnel
[07:21:20] 创建输出: Tunnel credentials written to /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json. cloudflared chose this file based on where your origin certificate was found. Keep this file secret. To revoke these credentials, delete the tunnel.

Created tunnel aishield-tunnel with id 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:21:20] Tunnel 创建成功! ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:21:20] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[07:21:20] 凭证文件存在
[07:21:20] 创建 config.yml...
[07:21:20] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[07:21:20] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:21:22] DNS 路由结果: 2026-07-30T23:21:22Z INF Added CNAME aishield.tools.healthlens.cc which will route to this tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[07:21:22] === STEP 6: 启动 Tunnel ===
[07:21:25] 启动 Named Tunnel (cert 模式)...
[07:21:25] 使用 config: /root/.cloudflared/config.yml
[07:21:25] cloudflared PID: 411957
[07:21:27] Tunnel 连接已建立!
[07:21:27] --- cloudflared 日志 (最后 15 行) ---
2026-07-30T23:21:25Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-07-30T23:21:25Z INF cloudflared will not automatically update if installed by a package manager.
2026-07-30T23:21:25Z INF Generated Connector ID: 7ec4e798-de9f-4f9b-b7bc-29f18604f50c
2026-07-30T23:21:25Z INF Initial protocol quic
2026-07-30T23:21:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T23:21:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T23:21:25Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-07-30T23:21:25Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-07-30T23:21:25Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-07-30T23:21:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-07-30T23:21:25Z INF Registered tunnel connection connIndex=0 connection=2b930e28-b314-45ff-8530-20d504500fe1 event=0 ip=198.41.192.77 location=lax05 protocol=quic
2026-07-30T23:21:25Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-07-30T23:21:25Z INF Registered tunnel connection connIndex=1 connection=bc25bda0-6573-4884-8c9c-5527c3a83058 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-07-30T23:21:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-07-30T23:21:27Z INF Registered tunnel connection connIndex=2 connection=1a0ed3c7-83ce-46dd-9cb9-e5a88e60b204 event=0 ip=198.41.200.33 location=lax01 protocol=quic
[07:21:27] === STEP 7: 持久化 ===
[07:21:27] systemd 服务已配置
[07:21:27] Cron 保活已设置
[07:21:27] === STEP 8: 验证 ===
[07:21:27] --- API (localhost:8450) ---
 OK
[07:21:27] --- cloudflared 进程 ---
root      411957  6.0  1.9 1294420 39396 ?       Sl   07:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      412073  0.0  1.3 1292484 27244 ?       Sl   07:21   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[07:21:27] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[07:21:28] --- DNS CNAME ---
[07:21:28] --- DNS A ---
104.21.81.46
172.67.188.44
[07:21:28] === 部署汇总 ===
[07:21:28] Tunnel Mode: cert
[07:21:28] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[07:21:28] API: http://localhost:8450
[07:21:28] 域名: https://aishield.tools
[07:21:28] cloudflared: /usr/local/bin/cloudflared
[07:21:28] PID: 411957
[07:21:28] Config: /root/.cloudflared/config.yml
[07:21:28] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[07:21:28] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-07-31 07:21:27 CST; 6s ago
   Main PID: 412069 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.4M
        CPU: 120ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─412069 /bin/bash /opt/start-tunnel.sh
             └─412073 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                 
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
Time: Thu Jul 30 23:21:34 UTC 2026

=== curl test (aishield.tools) ===
error code: 1014

=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
