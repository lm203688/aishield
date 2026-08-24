=== DIAGNOSTIC ===
Time: Mon Aug 24 05:50:03 PM CST 2026
=== USER ===
root
=== GIT LOG ===
dbcf3459 fix: download script from GitHub raw if git reset fails, add script version diagnostics
14ced6b0 chore: update deploy diagnostics [skip ci]
7b4068ba fix: force git reset on server to get latest deploy script
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787565003.1262746, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3299690  3.0  1.8 1294420 37600 ?       Sl   17:49   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3299896  6.5  1.8 1294676 37808 ?       Sl   17:50   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3300023 10.0  1.8 1294092 36656 ?       Sl   17:50   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-24T09:50:01Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-24T09:50:01Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-24T09:50:01Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-24T09:50:01Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-24T09:50:01Z INF Generated Connector ID: 7c33c5e3-d746-4dee-9d9d-287297d6cf12
2026-08-24T09:50:01Z INF Initial protocol quic
2026-08-24T09:50:01Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-24T09:50:01Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T09:50:01Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T09:50:01Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T09:50:01Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T09:50:01Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-24T09:50:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
2026-08-24T09:50:01Z INF Registered tunnel connection connIndex=0 connection=d821fe90-8329-48a9-a9c6-6b4e446b12d0 event=0 ip=198.41.192.47 location=lax07 protocol=quic
2026-08-24T09:50:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-24T09:50:01Z INF Registered tunnel connection connIndex=1 connection=f8e35f77-e9e3-4a2a-9e99-d5961d9f959c event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-24T09:50:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-08-24T09:50:03Z INF Registered tunnel connection connIndex=2 connection=62732e9e-9c1e-4441-9ab6-92b7123630f0 event=0 ip=198.41.200.13 location=lax01 protocol=quic
26-08-24T09:50:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.107
2026-08-24T09:50:02Z INF Registered tunnel connection connIndex=3 connection=591512f5-c366-4060-ac5d-2f8f3e9010bd event=0 ip=198.41.192.107 location=lax08 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[17:49:58] Time: Mon Aug 24 05:49:58 PM CST 2026
[17:49:58] User: root (UID: 0)
[17:49:58] === STEP 1: 启动 API (端口 8450) ===
[17:49:58] 创建输出: failed to create tunnel: Create Tunnel API call failed: tunnel with name already exists
[17:49:58] Tunnel 创建失败，尝试其他方法...
[17:49:59] 启动 Named Tunnel (cert 模式)...
[17:49:59] 使用 config: /root/.cloudflared/config.yml
[17:49:59] cloudflared PID: 3299690
[17:49:59] 使用第一个可用 tunnel: You
[17:49:59] 凭证文件: /root/.cloudflared/You.json
[17:49:59] 凭证文件不存在，列出 .cloudflared 目录内容:
total 24
drwxr-xr-x 2 root root 4096 Jul 31 07:21 .
drwx------ 9 root root 4096 Aug 10 08:42 ..
-r-------- 1 root root  175 Jul 31 07:21 0c39bcfb-0c96-4858-9025-d54131e062ec.json
-r-------- 1 root root  175 Jul 28 11:03 aa3f86b8-01f4-4ce0-83a8-5512219f9003.json
-rw------- 1 root root  282 Jul 28 11:02 cert.pem
-rw-r--r-- 1 root root  227 Aug 24 17:49 config.yml
[17:49:59] 创建 config.yml...
[17:49:59] config.yml 已创建:
tunnel: You
credentials-file: /root/.cloudflared/You.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[17:49:59] 路由 DNS: aishield.tools -> You.cfargotunnel.com
[17:49:59] API 已在运行
[17:49:59] API 状态: OK
[17:49:59] === STEP 2: 安装 cloudflared ===
[17:49:59] cloudflared 安装路径: /usr/local/bin/cloudflared
[17:49:59] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:50:00] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:50:00] === STEP 3: 检查认证方式 ===
[17:50:00] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[17:50:00] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[17:50:00] 检查现有 tunnel...
[17:50:00] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS      
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax01, 1xlax05 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                  
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                  
2026-08-24T09:50:00Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[17:50:00] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:50:00] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[17:50:00] 凭证文件存在
[17:50:00] 创建 config.yml...
[17:50:00] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[17:50:01] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:50:01] 启动 Named Tunnel (cert 模式)...
[17:50:01] 使用 config: /root/.cloudflared/config.yml
[17:50:01] cloudflared PID: 3299896
[17:50:01] Tunnel 连接已建立!
[17:50:01] --- cloudflared 日志 (最后 15 行) ---
2026-08-24T09:50:01Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-24T09:50:01Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-24T09:50:01Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-24T09:50:01Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-24T09:50:01Z INF Generated Connector ID: 7c33c5e3-d746-4dee-9d9d-287297d6cf12
2026-08-24T09:50:01Z INF Initial protocol quic
2026-08-24T09:50:01Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-24T09:50:01Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T09:50:01Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T09:50:01Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-24T09:50:01Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-24T09:50:01Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-24T09:50:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          2026-08-24T09:50:01Z INF Registered tunnel connection connIndex=2 connection=f0b624f5-ee30-4ccc-a299-6f1d5b31ba12 event=0 ip=198.41.200.53 location=lax01 protocol=quic
[17:50:01] === STEP 7: 持久化 ===
[17:50:01] DNS 路由结果: 2026-08-24T09:50:01Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:50:01] === STEP 5: 更新 DNS (API) ===
[17:50:01] CNAME: aishield.tools -> You.cfargotunnel.com
[17:50:02] systemd 服务已配置
[17:50:02] Cron 保活已设置
[17:50:02] === STEP 8: 验证 ===
[17:50:02] --- API (localhost:8450) ---
 OK
[17:50:02] --- cloudflared 进程 ---
root     3299690  3.0  1.9 1293844 38272 ?       Sl   17:49   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3299885  7.0  1.6 1293836 34076 ?       Sl   17:50   0:00 /usr/local/bin/cloudflared tunnel route dns aishield-tunnel aishield.tools
root     3299896 11.0  1.8 1293836 37900 ?       Sl   17:50   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[17:50:02] --- aishield.tools ---
[17:50:02] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[17:50:02] DNS 路由结果: 2026-08-24T09:50:02Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:50:02] === STEP 5: 更新 DNS (API) ===
[17:50:02] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-24 17:50:02 CST; 1s ago
   Main PID: 3300017 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 16.8M
        CPU: 117ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3300017 /bin/bash /opt/start-tunnel.sh
             └─3300023 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2525069,fd=3))                                                    
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
Time: Mon Aug 24 09:50:04 UTC 2026

=== curl test (aishield.tools) ===
error code: 502

=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
