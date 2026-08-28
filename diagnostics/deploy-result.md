=== DIAGNOSTIC ===
Time: Fri Aug 28 11:41:00 PM CST 2026
=== USER ===
root
=== GIT LOG ===
435b1220 chore(meta): 体系体检 score=83 level=degraded
177ed4b7 fix(deploy): use git as primary script channel on server (raw.githubusercontent hangs 5min)
fbed2339 auto: 部署验证状态回写 [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787931660.9252324, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3118574  4.5  1.9 1294092 38840 ?       Sl   23:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T15:40:58Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-28T15:40:58Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-28T15:40:58Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-28T15:40:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T15:40:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T15:40:58Z INF Generated Connector ID: 60437ee5-b2c9-4331-b406-c25c060ff538
2026-08-28T15:40:58Z INF Initial protocol quic
2026-08-28T15:40:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:40:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:40:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:40:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:40:58Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T15:40:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-08-28T15:40:59Z INF Registered tunnel connection connIndex=0 connection=a8166326-49cd-4d6e-a376-2cc6e0b397f8 event=0 ip=198.41.200.53 location=sjc10 protocol=quic
2026-08-28T15:40:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-28T15:40:59Z INF Registered tunnel connection connIndex=1 connection=c6c54f72-4f6d-4e36-ad56-a57a7e73a97e event=0 ip=198.41.192.47 location=lax11 protocol=quic
2026-08-28T15:41:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-28T15:41:00Z INF Registered tunnel connection connIndex=2 connection=cf034fe4-e6f2-4629-8c54-a653014dd146 event=0 ip=198.41.200.63 location=sjc08 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:40:24] Time: Fri Aug 28 11:40:24 PM CST 2026
[23:40:24] User: root (UID: 0)
[23:40:24] === STEP 1: 启动 API (端口 8450) ===
[23:40:25] HEAD: 435b1220 -> 435b1220
[23:40:39] server-card 版本: 磁盘=none 仓库=unknown
[23:40:39] 代码已是最新且 API 健康 -> 跳过重启
[23:40:39] API 状态: OK
[23:40:39] === STEP 2: 安装 cloudflared ===
[23:40:39] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:40:39] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:40:39] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:40:39] === STEP 3: 检查认证方式 ===
[23:40:39] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:40:39] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:40:39] 检查现有 tunnel...
[23:40:40] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 3xlax12, 2xsjc05, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[23:40:40] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:40:40] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:40:40] 凭证文件存在
[23:40:40] 创建 config.yml...
[23:40:40] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:40:40] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:40:41] DNS 路由结果: 2026-08-28T15:40:41Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:40:41] === STEP 5: 更新 DNS (API) ===
[23:40:41] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:40:42] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[23:40:43] 设置 SSL 模式为 Full...
SSL: 跳过
[23:40:44] === STEP 6: 启动 Tunnel ===
[23:40:45] server-card 版本: 磁盘=none 仓库=unknown
[23:40:45] 代码已是最新且 API 健康 -> 跳过重启
[23:40:45] API 状态: OK
[23:40:45] === STEP 2: 安装 cloudflared ===
[23:40:45] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:40:45] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:40:45] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:40:45] === STEP 3: 检查认证方式 ===
[23:40:45] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:40:45] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:40:45] 检查现有 tunnel...
[23:40:47] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
2026-08-28T15:40:47Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[23:40:47] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:40:47] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:40:47] 凭证文件存在
[23:40:47] 创建 config.yml...
[23:40:47] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:40:47] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:40:48] 启动 Named Tunnel (cert 模式)...
[23:40:48] 使用 config: /root/.cloudflared/config.yml
[23:40:48] cloudflared PID: 3118205
[23:40:49] DNS 路由结果: 2026-08-28T15:40:49Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:40:49] === STEP 5: 更新 DNS (API) ===
[23:40:49] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:40:50] Tunnel 连接已建立!
[23:40:50] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T15:40:48Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-28T15:40:48Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T15:40:48Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T15:40:48Z INF Generated Connector ID: 7a37eafd-699e-4faa-b99d-940c77c2adf2
2026-08-28T15:40:48Z INF Initial protocol quic
2026-08-28T15:40:48Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:40:48Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:40:48Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:40:48Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:40:48Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T15:40:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.7
2026-08-28T15:40:48Z INF Registered tunnel connection connIndex=0 connection=1b140b50-4883-4200-8cdc-94111bebebc3 event=0 ip=198.41.192.7 location=lax07 protocol=quic
2026-08-28T15:40:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-08-28T15:40:48Z INF Registered tunnel connection connIndex=1 connection=1f212566-9096-4a11-8377-b711407ec20c event=0 ip=198.41.200.113 location=sjc10 protocol=quic
2026-08-28T15:40:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
[23:40:50] === STEP 7: 持久化 ===
[23:40:50] systemd 服务已配置
[23:40:50] Cron 保活已设置
[23:40:50] === STEP 8: 验证 ===
[23:40:50] --- API (localhost:8450) ---
 OK
[23:40:50] --- cloudflared 进程 ---
root     3118205  4.5  1.9 1293844 38736 ?       Sl   23:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3118313  0.0  1.3 1292484 27504 ?       Sl   23:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[23:40:50] --- aishield.tools ---
[23:40:51] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
 OK
[23:40:52] --- DNS CNAME ---
[23:40:52] --- DNS A ---
104.21.81.46
172.67.188.44
[23:40:52] === 部署汇总 ===
[23:40:52] Tunnel Mode: cert
[23:40:52] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:40:52] API: http://localhost:8450
[23:40:52] 域名: https://aishield.tools
[23:40:52] cloudflared: /usr/local/bin/cloudflared
[23:40:52] PID: 3118205
[23:40:52] Config: /root/.cloudflared/config.yml
[23:40:52] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:40:52] 状态: Named Tunnel (cert 模式) 已配置
DNS 更新: OK
[23:40:54] 设置 SSL 模式为 Full...
SSL: 跳过
[23:40:55] === STEP 6: 启动 Tunnel ===
[23:40:58] 启动 Named Tunnel (cert 模式)...
[23:40:58] 使用 config: /root/.cloudflared/config.yml
[23:40:58] cloudflared PID: 3118574
[23:41:00] Tunnel 连接已建立!
[23:41:00] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T15:40:58Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T15:40:58Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T15:40:58Z INF Generated Connector ID: 60437ee5-b2c9-4331-b406-c25c060ff538
2026-08-28T15:40:58Z INF Initial protocol quic
2026-08-28T15:40:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:40:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:40:58Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:40:58Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:40:58Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T15:40:58Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-08-28T15:40:59Z INF Registered tunnel connection connIndex=0 connection=a8166326-49cd-4d6e-a376-2cc6e0b397f8 event=0 ip=198.41.200.53 location=sjc10 protocol=quic
2026-08-28T15:40:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-08-28T15:40:59Z INF Registered tunnel connection connIndex=1 connection=c6c54f72-4f6d-4e36-ad56-a57a7e73a97e event=0 ip=198.41.192.47 location=lax11 protocol=quic
2026-08-28T15:41:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-28T15:41:00Z INF Registered tunnel connection connIndex=2 connection=cf034fe4-e6f2-4629-8c54-a653014dd146 event=0 ip=198.41.200.63 location=sjc08 protocol=quic
[23:41:00] === STEP 7: 持久化 ===
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) since Fri 2026-08-28 23:40:55 CST; 5s ago
   Main PID: 3118312 (code=exited, status=0/SUCCESS)
        CPU: 226ms

Aug 28 23:41:01 VM-0-11-ubuntu systemd[1]: Stopped Cloudflare Named Tunnel for AIShield.
Aug 28 23:41:01 VM-0-11-ubuntu systemd[1]: Started Cloudflare Named Tunnel for AIShield.
Aug 28 23:41:01 VM-0-11-ubuntu start-tunnel.sh[3118749]: 2026-08-28T15:41:01Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
Aug 28 23:41:01 VM-0-11-ubuntu start-tunnel.sh[3118749]: 2026-08-28T15:41:01Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
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
Time: Fri Aug 28 15:41:01 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787931662.2211668, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
