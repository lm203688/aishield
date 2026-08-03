=== DIAGNOSTIC ===
Time: Tue Aug 4 05:32:44 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785792764.170476, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2779765  0.1  1.4 1294932 28856 ?       Sl   Aug02   3:34 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2779856  0.1  1.2 1360284 25972 ?       Sl   Aug02   3:33 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-03T16:49:06Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=1 event=0 ip=198.41.192.77
2026-08-03T16:49:06Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: Application error 0x0 (remote)" connIndex=1 event=0 ip=198.41.192.77
2026-08-03T16:49:06Z WRN failed to serve tunnel connection error="datagram manager encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.77
2026-08-03T16:49:06Z WRN Serve tunnel error error="datagram manager encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.77
2026-08-03T16:49:06Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.77
2026-08-03T16:49:07Z WRN Connection terminated error="datagram manager encountered a failure while serving" connIndex=1
2026-08-03T16:49:26Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.77
2026-08-03T16:49:26Z INF Registered tunnel connection connIndex=1 connection=98936902-cdf5-4e07-990f-dfa3c4c26b14 event=0 ip=198.41.192.77 location=lax11 protocol=quic
2026-08-03T17:17:26Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.33
2026-08-03T17:17:26Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=0 event=0 ip=198.41.200.33
2026-08-03T17:17:26Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.33
2026-08-03T17:17:26Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.33
2026-08-03T17:17:26Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.33
2026-08-03T17:17:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-08-03T17:17:29Z INF Registered tunnel connection connIndex=0 connection=fba570ef-3536-42ad-89c2-2e8a702aba9b event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-03T17:20:31Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:31Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:31Z WRN failed to serve tunnel connection error="datagram manager encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:31Z WRN Serve tunnel error error="datagram manager encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:31Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:32Z WRN Connection terminated error="datagram manager encountered a failure while serving" connIndex=2
2026-08-03T17:20:46Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:53Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:53Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:53Z WRN failed to serve tunnel connection error="control stream encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:53Z WRN Serve tunnel error error="control stream encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:53Z INF Retrying connection in up to 4s connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:20:56Z WRN Connection terminated error="control stream encountered a failure while serving" connIndex=2
2026-08-03T17:21:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-03T17:21:14Z INF Registered tunnel connection connIndex=2 connection=6a933062-92da-47c0-b20e-b56d0d6c85f5 event=0 ip=198.41.192.227 location=lax10 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[14:46:51] Time: Sun Aug  2 02:46:51 PM CST 2026
[14:46:51] User: root (UID: 0)
[14:46:51] === STEP 1: 启动 API (端口 8450) ===
[14:47:24] API 已在运行
[14:47:24] API 状态: OK
[14:47:24] === STEP 2: 安装 cloudflared ===
[14:47:24] cloudflared 安装路径: /usr/local/bin/cloudflared
[14:47:24] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:47:24] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:47:24] === STEP 3: 检查认证方式 ===
[14:47:24] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[14:47:24] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[14:47:24] 检查现有 tunnel...
[14:47:25] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 2xlax08, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[14:47:25] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:47:25] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[14:47:25] 凭证文件存在
[14:47:25] 创建 config.yml...
[14:47:25] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[14:47:25] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:47:28] DNS 路由结果: 2026-08-02T06:47:28Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[14:47:28] === STEP 5: 更新 DNS (API) ===
[14:47:28] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:47:28] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[14:47:29] 设置 SSL 模式为 Full...
SSL: 跳过
[14:47:30] === STEP 6: 启动 Tunnel ===
[14:47:33] 启动 Named Tunnel (cert 模式)...
[14:47:33] 使用 config: /root/.cloudflared/config.yml
[14:47:33] cloudflared PID: 2779765
[14:47:35] Tunnel 连接已建立!
[14:47:35] --- cloudflared 日志 (最后 15 行) ---
2026-08-02T06:47:33Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-02T06:47:33Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-02T06:47:33Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-02T06:47:33Z INF Generated Connector ID: 6ccbb49a-5a22-4af8-aec6-f7fa852b258f
2026-08-02T06:47:33Z INF Initial protocol quic
2026-08-02T06:47:33Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-02T06:47:33Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-02T06:47:33Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-02T06:47:33Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-02T06:47:33Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-02T06:47:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-08-02T06:47:33Z INF Registered tunnel connection connIndex=0 connection=dab2d2a7-fd38-4971-99bd-ef317d4460ce event=0 ip=198.41.200.33 location=lax01 protocol=quic
2026-08-02T06:47:33Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.77
2026-08-02T06:47:34Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-08-02T06:47:34Z INF Registered tunnel connection connIndex=1 connection=50cf186e-37dd-476d-bbb7-178cd61c0e15 event=0 ip=198.41.192.77 location=lax11 protocol=quic
[14:47:35] === STEP 7: 持久化 ===
[14:47:35] systemd 服务已配置
[14:47:35] Cron 保活已设置
[14:47:35] === STEP 8: 验证 ===
[14:47:35] --- API (localhost:8450) ---
 OK
[14:47:35] --- cloudflared 进程 ---
root     2779765  4.5  1.9 1294420 38224 ?       Sl   14:47   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2779856  0.0  1.0 1292484 21440 ?       Rl   14:47   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[14:47:35] --- aishield.tools ---
 OK
[14:47:37] --- DNS CNAME ---
[14:47:38] --- DNS A ---
104.21.81.46
172.67.188.44
[14:47:38] === 部署汇总 ===
[14:47:38] Tunnel Mode: cert
[14:47:38] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:47:38] API: http://localhost:8450
[14:47:38] 域名: https://aishield.tools
[14:47:38] cloudflared: /usr/local/bin/cloudflared
[14:47:38] PID: 2779765
[14:47:38] Config: /root/.cloudflared/config.yml
[14:47:38] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:47:38] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-02 14:47:35 CST; 1 day 14h ago
   Main PID: 2779855 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 19.9M
        CPU: 3min 33.150s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2779855 /bin/bash /opt/start-tunnel.sh
             └─2779856 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug  3 21:32:44 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785792764.761538, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
