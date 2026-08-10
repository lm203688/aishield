=== DIAGNOSTIC ===
Time: Mon Aug 10 11:02:57 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786330977.1674724, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     1747768  0.1  1.0 1294932 20804 ?       Sl   Aug09   1:36 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1747907  0.1  1.0 1294676 21932 ?       Sl   Aug09   1:37 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-09T15:29:42Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.192.57
2026-08-09T15:29:42Z WRN Connection terminated error="accept stream listener encountered a failure while serving" connIndex=3
2026-08-09T15:29:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-08-09T15:29:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-09T15:30:06Z INF Registered tunnel connection connIndex=3 connection=e778a4ab-b4d1-4483-86bc-893406028180 event=0 ip=198.41.192.57 location=lax07 protocol=quic
2026-08-09T15:30:08Z INF Registered tunnel connection connIndex=1 connection=f9502f2f-764f-4c7d-b0cf-a8d43745eaea event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-08-09T15:30:15Z ERR failed to accept incoming stream requests error="failed to accept QUIC stream: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.192.37
2026-08-09T15:30:15Z ERR failed to run the datagram handler error="timeout: no recent network activity" connIndex=1 event=0 ip=198.41.192.37
2026-08-09T15:30:15Z WRN failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.37
2026-08-09T15:30:15Z WRN Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.37
2026-08-09T15:30:15Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.37
2026-08-09T15:30:17Z WRN Connection terminated error="accept stream listener encountered a failure while serving" connIndex=1
2026-08-09T15:30:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.37
2026-08-09T15:30:46Z INF Registered tunnel connection connIndex=1 connection=8302d508-aa24-4c1b-86a6-dd442cfa3142 event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-08-09T15:35:42Z ERR  error="stream 5 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-09T15:35:42Z ERR Request failed error="stream 5 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.192.57 type=http
2026-08-09T17:19:37Z ERR  error="stream 121 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-09T17:19:37Z ERR Request failed error="stream 121 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.200.43 type=http
2026-08-09T17:35:04Z ERR  error="stream 25 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-09T17:35:04Z ERR Request failed error="stream 25 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.192.37 type=http
2026-08-09T20:37:13Z ERR  error="stream 205 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-09T20:37:13Z ERR Request failed error="stream 205 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.200.43 type=http
2026-08-09T21:19:09Z ERR  error="stream 101 canceled by remote with error code 0" connIndex=0 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-09T21:19:09Z ERR Request failed error="stream 101 canceled by remote with error code 0" connIndex=0 dest=https://aishield.tools/ event=0 ip=198.41.200.63 type=http
2026-08-09T22:35:33Z ERR  error="stream 93 canceled by remote with error code 0" connIndex=3 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-09T22:35:33Z ERR Request failed error="stream 93 canceled by remote with error code 0" connIndex=3 dest=https://aishield.tools/ event=0 ip=198.41.192.57 type=http
2026-08-09T23:34:57Z ERR  error="stream 281 canceled by remote with error code 0" connIndex=2 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-09T23:34:57Z ERR Request failed error="stream 281 canceled by remote with error code 0" connIndex=2 dest=https://aishield.tools/ event=0 ip=198.41.200.43 type=http
2026-08-10T02:45:58Z ERR  error="stream 57 canceled by remote with error code 0" connIndex=1 event=1 ingressRule=0 originService=http://localhost:8450
2026-08-10T02:45:58Z ERR Request failed error="stream 57 canceled by remote with error code 0" connIndex=1 dest=https://aishield.tools/ event=0 ip=198.41.192.37 type=http
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[17:03:44] Time: Sun Aug  9 05:03:44 PM CST 2026
[17:03:44] User: root (UID: 0)
[17:03:44] === STEP 1: 启动 API (端口 8450) ===
[17:03:46] API 已在运行
[17:03:46] API 状态: OK
[17:03:46] === STEP 2: 安装 cloudflared ===
[17:03:46] cloudflared 安装路径: /usr/local/bin/cloudflared
[17:03:46] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:03:46] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:03:46] === STEP 3: 检查认证方式 ===
[17:03:46] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[17:03:46] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[17:03:46] 检查现有 tunnel...
[17:03:48] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 2xlax08, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[17:03:48] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:03:48] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[17:03:48] 凭证文件存在
[17:03:48] 创建 config.yml...
[17:03:48] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[17:03:48] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:03:50] DNS 路由结果: 2026-08-09T09:03:50Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:03:50] === STEP 5: 更新 DNS (API) ===
[17:03:50] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:03:51] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[17:03:52] 设置 SSL 模式为 Full...
SSL: 跳过
[17:03:54] === STEP 6: 启动 Tunnel ===
[17:03:57] 启动 Named Tunnel (cert 模式)...
[17:03:57] 使用 config: /root/.cloudflared/config.yml
[17:03:57] cloudflared PID: 1747768
[17:03:59] Tunnel 连接已建立!
[17:03:59] --- cloudflared 日志 (最后 15 行) ---
2026-08-09T09:03:58Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-09T09:03:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-09T09:03:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-09T09:03:58Z INF Generated Connector ID: 646675bd-f273-42b6-be3e-32edafd0cc1b
2026-08-09T09:03:58Z INF Initial protocol quic
2026-08-09T09:03:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T09:03:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T09:03:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-09T09:03:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-09T09:03:58Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-09T09:03:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-08-09T09:03:58Z INF Registered tunnel connection connIndex=0 connection=e708403b-f75b-4cab-84be-1d4d1397ff56 event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-08-09T09:03:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-08-09T09:03:58Z INF Registered tunnel connection connIndex=1 connection=797f5fdc-b02f-42dc-a344-279b1dafd439 event=0 ip=198.41.192.167 location=lax08 protocol=quic
2026-08-09T09:03:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
[17:03:59] === STEP 7: 持久化 ===
[17:04:00] systemd 服务已配置
[17:04:00] Cron 保活已设置
[17:04:00] === STEP 8: 验证 ===
[17:04:00] --- API (localhost:8450) ---
 OK
[17:04:00] --- cloudflared 进程 ---
root     1747768  3.3  1.9 1294420 38344 ?       Sl   17:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1747907  0.0  1.3 1292484 27380 ?       Rl   17:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[17:04:00] --- aishield.tools ---
 OK
[17:04:02] --- DNS CNAME ---
[17:04:02] --- DNS A ---
172.67.188.44
104.21.81.46
[17:04:02] === 部署汇总 ===
[17:04:02] Tunnel Mode: cert
[17:04:02] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:04:02] API: http://localhost:8450
[17:04:02] 域名: https://aishield.tools
[17:04:02] cloudflared: /usr/local/bin/cloudflared
[17:04:02] PID: 1747768
[17:04:02] Config: /root/.cloudflared/config.yml
[17:04:02] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:04:02] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-09 17:04:00 CST; 17h ago
   Main PID: 1747903 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 20.1M
        CPU: 1min 37.279s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1747903 /bin/bash /opt/start-tunnel.sh
             └─1747907 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 10 03:02:57 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786330977.6865356, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
