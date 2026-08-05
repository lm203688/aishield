=== DIAGNOSTIC ===
Time: Thu Aug 6 04:51:42 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785963102.9889028, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1858935  0.1  1.2 1294676 24868 ?       Sl   Aug05   0:58 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1859040  0.1  1.2 1294676 24324 ?       Sl   Aug05   0:58 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-05T16:03:10Z INF Retrying connection in up to 8s connIndex=2 event=0 ip=198.41.200.53
2026-08-05T16:03:10Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: Application error 0x0 (remote)" connIndex=3 event=0 ip=198.41.192.57
2026-08-05T16:03:10Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=3 event=0 ip=198.41.192.57
2026-08-05T16:03:10Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.57
2026-08-05T16:03:10Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.57
2026-08-05T16:03:10Z INF Retrying connection in up to 8s connIndex=3 event=0 ip=198.41.192.57
2026-08-05T16:03:10Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: Application error 0x0 (remote)" connIndex=1 event=0 ip=198.41.192.107
2026-08-05T16:03:10Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.192.107
2026-08-05T16:03:10Z ERR failed to serve tunnel connection error="control stream encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.107
2026-08-05T16:03:10Z ERR Serve tunnel error error="control stream encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.107
2026-08-05T16:03:10Z INF Retrying connection in up to 8s connIndex=1 event=0 ip=198.41.192.107
2026-08-05T16:03:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-05T16:03:11Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: Application error 0x0 (remote)" connIndex=0 event=0 ip=198.41.200.113
2026-08-05T16:03:11Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.200.113
2026-08-05T16:03:11Z ERR failed to serve tunnel connection error="control stream encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-08-05T16:03:11Z ERR Serve tunnel error error="control stream encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-08-05T16:03:11Z INF Retrying connection in up to 32s connIndex=0 event=0 ip=198.41.200.113
2026-08-05T16:03:14Z ERR Connection terminated error="control stream encountered a failure while serving" connIndex=1
2026-08-05T16:03:14Z ERR Connection terminated error="datagram manager encountered a failure while serving" connIndex=2
2026-08-05T16:03:14Z ERR Connection terminated error="accept stream listener encountered a failure while serving" connIndex=3
2026-08-05T16:03:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-05T16:03:18Z INF Registered tunnel connection connIndex=0 connection=14d73749-5329-44f2-94ad-f47cfb3c13bd event=0 ip=198.41.200.113 location=sjc07 protocol=quic
2026-08-05T16:04:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-05T16:04:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-08-05T16:04:20Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-08-05T16:04:21Z INF Registered tunnel connection connIndex=3 connection=c12a07c8-9159-40a5-8471-bc8e46ee44eb event=0 ip=198.41.192.57 location=sjc01 protocol=quic
2026-08-05T16:04:21Z INF Registered tunnel connection connIndex=2 connection=2acdf4d4-5332-4286-99f5-ed2e522ccc9c event=0 ip=198.41.200.53 location=sjc07 protocol=quic
2026-08-05T16:04:21Z INF Registered tunnel connection connIndex=1 connection=8cb04c65-7f25-409b-954a-411ce5532b65 event=0 ip=198.41.192.107 location=sjc06 protocol=quic
2026-08-05T18:24:13Z ERR  error="stream 21 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-05T18:24:13Z ERR Request failed error="stream 21 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.192.57 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:14:49] Time: Wed Aug  5 06:14:49 PM CST 2026
[18:14:49] User: root (UID: 0)
[18:14:49] === STEP 1: 启动 API (端口 8450) ===
[18:16:19] API 已在运行
[18:16:19] API 状态: OK
[18:16:19] === STEP 2: 安装 cloudflared ===
[18:16:19] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:16:19] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:16:19] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:16:19] === STEP 3: 检查认证方式 ===
[18:16:19] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:16:19] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:16:19] 检查现有 tunnel...
[18:16:20] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax08, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[18:16:20] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:16:20] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:16:20] 凭证文件存在
[18:16:20] 创建 config.yml...
[18:16:20] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:16:20] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:16:24] DNS 路由结果: 2026-08-05T10:16:24Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:16:24] === STEP 5: 更新 DNS (API) ===
[18:16:24] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:16:24] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[18:16:25] 设置 SSL 模式为 Full...
SSL: 跳过
[18:16:26] === STEP 6: 启动 Tunnel ===
[18:16:29] 启动 Named Tunnel (cert 模式)...
[18:16:29] 使用 config: /root/.cloudflared/config.yml
[18:16:29] cloudflared PID: 1858935
[18:16:31] Tunnel 连接已建立!
[18:16:31] --- cloudflared 日志 (最后 15 行) ---
2026-08-05T10:16:29Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-05T10:16:29Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-05T10:16:29Z INF Generated Connector ID: e7dadb20-341a-49a3-aafe-026cbda3c1d6
2026-08-05T10:16:29Z INF Initial protocol quic
2026-08-05T10:16:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T10:16:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T10:16:29Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-05T10:16:29Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-05T10:16:29Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-05T10:16:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-05T10:16:30Z INF Registered tunnel connection connIndex=0 connection=1a3755d6-2b10-43af-a994-53b93d167d15 event=0 ip=198.41.200.63 location=lax01 protocol=quic
2026-08-05T10:16:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-05T10:16:30Z INF Registered tunnel connection connIndex=1 connection=8d999c6b-95ff-4f34-b4c2-0298059b4bd5 event=0 ip=198.41.192.37 location=lax09 protocol=quic
2026-08-05T10:16:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-08-05T10:16:31Z INF Registered tunnel connection connIndex=2 connection=41023622-c730-44de-810b-63083c2e31c3 event=0 ip=198.41.200.43 location=lax01 protocol=quic
[18:16:31] === STEP 7: 持久化 ===
[18:16:32] systemd 服务已配置
[18:16:32] Cron 保活已设置
[18:16:32] === STEP 8: 验证 ===
[18:16:32] --- API (localhost:8450) ---
 OK
[18:16:32] --- cloudflared 进程 ---
root     1858935  3.0  1.9 1294420 39232 ?       Sl   18:16   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1859040  0.0  1.3 1292740 27164 ?       Rl   18:16   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[18:16:32] --- aishield.tools ---
 OK
[18:16:33] --- DNS CNAME ---
[18:16:34] --- DNS A ---
172.67.188.44
104.21.81.46
[18:16:34] === 部署汇总 ===
[18:16:34] Tunnel Mode: cert
[18:16:34] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:16:34] API: http://localhost:8450
[18:16:34] 域名: https://aishield.tools
[18:16:34] cloudflared: /usr/local/bin/cloudflared
[18:16:34] PID: 1858935
[18:16:34] Config: /root/.cloudflared/config.yml
[18:16:34] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:16:34] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-05 18:16:32 CST; 10h ago
   Main PID: 1859039 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 20.6M
        CPU: 58.490s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1859039 /bin/bash /opt/start-tunnel.sh
             └─1859040 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Wed Aug  5 20:51:43 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785963103.496323, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
