=== DIAGNOSTIC ===
Time: Sat Oct 24 07:55:10 PM CST 2026
=== USER ===
root
=== GIT LOG ===
fatal: detected dubious ownership in repository at '/opt/aishield'
To add an exception for this directory, call:

	git config --global --add safe.directory /opt/aishield
NO GIT REPO
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1792842910.0378168, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "41d1f189bd9051ab86d693d6fb5565d99f2a7c9a", "deployed_at": "2026-10-24T11:54:34Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}OK
=== CLOUDFLARED PROCESS ===
root     1335162  0.1  0.8 1295188 17760 ?       Ssl  Sep18  85:05 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     2124852  1.2  2.0 1360284 40256 ?       Sl   19:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-24T11:54:52Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-24T11:54:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-10-24T11:54:52Z INF Registered tunnel connection connIndex=0 connection=b596462c-fda4-44ec-86e6-221ade38087c event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-10-24T11:54:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
202026-10-24T11:54:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-10-24T11:54:54Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-24T11:54:54Z INF Registered tunnel connection connIndex=2 connection=8df232026-10-24T11:54:54Z INF Registered tunnel connection connIndex=2 connection=aafa48a1-2026-10-24T11:54:54Z ERR failed to run the datagram handler error="context cancele2026-10-24T11:54:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.73
2026-10-24T11:54:54Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-24T11:54:55Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.200.53
2026-10-24T11:54:55Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.53
2026-10-24T11:54:55Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.53
2026-10-24T11:54:55Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.53
2026-10-24T11:54:55Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.192.77
2026-10-24T11:54:55Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.77
2026-10-24T11:54:55Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.77
2026-10-24T11:54:55Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.192.77
2022026-10-24T11:54:55Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.192.57
2026-10-24T11:54:55Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.57
2026-10-24T11:54:55Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.57
2026-10-24T11:54:55Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.2026-10-24T11:54:55Z ERR Connection terminated connIndex=0
2026-10-24T11:54:55Z ERR Connection terminated connIndex=2
2026-10-24T11:54:55Z ERR Connection terminated connIndex=1
2026-10-24T11:54:59Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-10-24T11:54:59Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.73
2026-10-24T11:54:59Z ERR Connection terminated connIndex=3
2026-10-24T11:54:59Z ERR no more connections active and exiting
2026-10-24T11:54:59Z INF Tunnel server stopped
2026-10-24T11:54:59Z INF Metrics server stopped
rminated error="context canceled"
2026-10-24T11:54:57Z INF Metrics server stopped
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[19:54:34] Time: Sat Oct 24 07:54:34 PM CST 2026
[19:54:34] User: root (UID: 0)
[19:54:34] === STEP 1: 启动 API (端口 8450) ===
[19:54:34] 代码由 runner tarball 投递，权威 sha=41d1f189
[19:54:34] commit 对比: 运行进程=7f7107e2191eb9e7763025f61bd1b78a5a85bf90 / 磁盘=41d1f189bd9051ab86d693d6fb5565d99f2a7c9a
[19:54:34] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[19:54:35] 需要重新加载代码 -> 重启 API
[19:54:36] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[19:54:36] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[19:54:42] API 状态: OK（第 1 轮验证通过）
[19:54:42] API 状态: OK（第 1 轮验证通过）
[19:54:42] === STEP 2: 安装 cloudflared ===
[19:54:42] === STEP 2: 安装 cloudflared ===
[19:54:42] cloudflared 安装路径: /usr/local/bin/cloudflared
[19:54:42] cloudflared 安装路径: /usr/local/bin/cloudflared
[19:54:43] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[19:54:43] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[19:54:43] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[19:54:43] === STEP 3: 检查认证方式 ===
[19:54:43] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[19:54:43] === STEP 3: 检查认证方式 ===
[19:54:43] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[19:54:43] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[19:54:43] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[19:54:43] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[19:54:43] 检查现有 tunnel...
[19:54:43] 检查现有 tunnel...
[19:54:43] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 4xlax01, 2xlax05, 1xlax08, 2xlax10, 1xlax11, 2xlax13 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax01, 1xlax11, 1xlax12                            
[19:54:43] 现有 tunnel 列表:
[19:54:43] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 4xlax01, 2xlax05, 1xlax08, 2xlax10, 1xlax11, 2xlax13 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax01, 1xlax11, 1xlax12                            
[19:54:43] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[19:54:44] 凭证文件存在
[19:54:44] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[19:54:44] 创建 config.yml...
[19:54:44] config.yml 已创建:
[19:54:44] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[19:54:44] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[19:54:44] 凭证文件存在
[19:54:44] 创建 config.yml...
[19:54:44] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[19:54:44] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[19:54:45] DNS 路由结果: 2026-10-24T11:54:45Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[19:54:45] === STEP 5: 更新 DNS (API) ===
[19:54:45] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[19:54:45] DNS 路由结果: 2026-10-24T11:54:45Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[19:54:45] === STEP 5: 更新 DNS (API) ===
[19:54:45] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[19:54:45] 创建新 DNS CNAME 记录...
[19:54:46] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[19:54:47] 设置 SSL 模式为 Full...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[19:54:47] 设置 SSL 模式为 Full...
SSL: 跳过
[19:54:48] === STEP 6: 启动 Tunnel ===
[19:54:48] systemd 托管中 -> systemctl stop cloudflared-tunnel
SSL: 跳过
[19:54:49] === STEP 6: 启动 Tunnel ===
[19:54:51] 启动 Named Tunnel (cert 模式)...
[19:54:51] 使用 config: /root/.cloudflared/config.yml
[19:54:51] cloudflared PID: 2124486
[19:54:52] 启动 Named Tunnel (cert 模式)...
[19:54:52] 使用 config: /root/.cloudflared/config.yml
[19:54:52] cloudflared PID: 2124504
[19:54:53] Tunnel 连接已建立!
[19:54:53] --- cloudflared 日志 (最后 15 行) ---
2026-10-24T11:54:52Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-10-24T11:54:52Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-10-24T11:54:52Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-24T11:54:52Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-24T11:54:52Z INF Generated Connector ID: a222ab8a-525c-44a8-97be-6651500144b8
2026-10-24T11:54:52Z INF Initial protocol quic
2026-10-24T11:54:52Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-24T11:54:52Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-24T11:54:52Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-24T11:54:52Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-24T11:54:52Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-24T11:54:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-10-24T11:54:52Z INF Registered tunnel connection connIndex=0 connection=b596462c-fda4-44ec-86e6-221ade38087c event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-10-24T11:54:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
2026-10-24T11:54:53Z INF Registered tunnel connection connIndex=1 connection=f1208987-f454-49ac-9362-2c9fdacc3f5c event=0 ip=198.41.192.7 location=lax11 protocol=quic
[19:54:53] === STEP 7: 持久化 ===
[19:54:54] 停止 nohup cloudflared (PID 2124486) -> 交由 systemd 单实例托管
[19:54:54] Tunnel 连接已建立!
[19:54:54] --- cloudflared 日志 (最后 15 行) ---
2026-10-24T11:54:52Z INF Initial protocol quic
2026-10-24T11:54:52Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-24T11:54:52Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-24T11:54:52Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-24T11:54:52Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-24T11:54:52Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-24T11:54:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-10-24T11:54:52Z INF Registered tunnel connection connIndex=0 connection=b596462c-fda4-44ec-86e6-221ade38087c event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-10-24T11:54:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.7
202026-10-24T11:54:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.53
2026-10-24T11:54:54Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-24T11:54:54Z INF Registered tunnel connection connIndex=2 connection=8df232026-10-24T11:54:54Z INF Registered tunnel connection connIndex=2 connection=aafa48a1-2026-10-24T11:54:54Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.200.53
2026-10-24T11:54:54Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.53
2026-10-24T11:54:54Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.53
2026-10-24T11:54:54Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.200.53
[19:54:54] === STEP 7: 持久化 ===
[19:54:54] 停止 nohup cloudflared (PID 2124504) -> 交由 systemd 单实例托管
[19:54:56] systemd 服务已配置
[19:54:56] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[19:54:56] === STEP 8: 验证 ===
[19:54:56] --- API (localhost:8450) ---
 OK
[19:54:56] --- cloudflared 进程 ---
root     1335162  0.1  0.8 1295188 16956 ?       Ssl  Sep18  85:05 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     2124486 13.2  1.9 1294676 38604 ?       Sl   19:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2124504 14.2  1.9 1294676 38888 ?       Sl   19:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[19:54:56] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[19:54:57] --- DNS CNAME ---
[19:54:59] --- DNS A ---
172.67.188.44
104.21.81.46
[19:54:59] === 部署汇总 ===
[19:54:59] Tunnel Mode: cert
[19:54:59] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[19:54:59] API: http://localhost:8450
[19:54:59] 域名: https://aishield.tools
[19:54:59] cloudflared: /usr/local/bin/cloudflared
[19:54:59] PID: 2124486
[19:54:59] Config: /root/.cloudflared/config.yml
[19:54:59] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[19:54:59] 状态: Named Tunnel (cert 模式) 已配置
[19:54:59] EXIT 0: API 健康
[19:54:59] systemd 服务已配置
[19:54:59] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[19:54:59] === STEP 8: 验证 ===
[19:54:59] --- API (localhost:8450) ---
 OK
[19:54:59] --- cloudflared 进程 ---
root     1335162  0.1  0.8 1295188 16956 ?       Ssl  Sep18  85:05 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     2124852  0.0  1.3 1358092 27964 ?       Rl   19:54   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[19:54:59] --- aishield.tools ---
 OK
[19:55:03] --- DNS CNAME ---
[19:55:03] --- DNS A ---
104.21.81.46
172.67.188.44
[19:55:03] === 部署汇总 ===
[19:55:03] Tunnel Mode: cert
[19:55:03] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[19:55:03] API: http://localhost:8450
[19:55:03] 域名: https://aishield.tools
[19:55:03] cloudflared: /usr/local/bin/cloudflared
[19:55:03] PID: 2124504
[19:55:03] Config: /root/.cloudflared/config.yml
[19:55:03] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[19:55:03] 状态: Named Tunnel (cert 模式) 已配置
[19:55:03] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-10-24 19:54:59 CST; 10s ago
   Main PID: 2124847 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 19.3M
        CPU: 156ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2124847 /bin/bash /opt/start-tunnel.sh
             └─2124852 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2124035,fd=3))                                                    
=== CRONTAB ===
*/5 * * * * flock -xn /tmp/stargate.lock -c '/usr/local/qcloud/stargate/admin/start.sh > /dev/null 2>&1 &'
0 19 * * * /opt/healthlens/scripts/audit_integrity_cron.sh
* * * * * curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
=== START SCRIPT ===
#!/bin/bash
# AIShield Tunnel 启动脚本
CF_BIN='/usr/local/bin/cloudflared'
CONFIG_FILE='/root/.cloudflared/config.yml'
TOKEN_FILE='/root/.cloudflared/tunnel-token'

cleanup() { kill $CF_PID 2>/dev/null; exit 0; }
trap cleanup SIGTERM SIGINT

# 【2026-09-18】隧道起来不等于 API 在监听。Cloudflare 转发到 localhost:8450，
# 若该端口无进程，域名只会稳定返回 502（09-17~09-18 线上连续失活即此路径：
# cloudflared 存活、API 未监听）。开机/重启后先确保 API 就绪再放行隧道。
if ! curl -sf --max-time 5 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1; then
    if systemctl is-active aishield-api >/dev/null 2>&1; then
        systemctl restart aishield-api 2>/dev/null || true
    elif systemctl is-enabled aishield-api >/dev/null 2>&1; then
        systemctl start aishield-api 2>/dev/null || true
    elif [ -f /opt/aishield/api/server.py ]; then
        # 【2026-09-18】与 install_api_service / api_start_nohup 一致：
        # systemd 以 root 运行，assert_not_root() 会拒绝启动（线上 502 的根因）。
        (cd /opt/aishield && PORT=8450 AISHIELD_ALLOW_ROOT=1 nohup python3 api/server.py >> /tmp/aishield-api.log 2>&1 &)
    elif [ -f "$HOME/aishield/api/server.py" ]; then
        (cd "$HOME/aishield" && PORT=8450 AISHIELD_ALLOW_ROOT=1 nohup python3 api/server.py >> /tmp/aishield-api.log 2>&1 &)
    fi
    for _i in 1 2 3 4 5 6; do
        curl -sf --max-time 5 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 && break
        sleep 3
    done
    if ! curl -sf --max-time 5 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1; then
        echo "[$(date '+%H:%M:%S')] WARN: API 未就绪，隧道仍会启动（域名将返回 502）" >> /tmp/aishield-api.log
    fi
fi

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
Time: Sat Oct 24 11:55:34 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1792842934.7519872, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "41d1f189bd9051ab86d693d6fb5565d99f2a7c9a", "deployed_at": "2026-10-24T11:54:34Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
