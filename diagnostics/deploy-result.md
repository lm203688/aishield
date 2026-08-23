=== DIAGNOSTIC ===
Time: Mon Aug 24 06:07:38 AM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787522858.3093033, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2683576  0.1  1.1 1294676 22392 ?       Sl   02:04   0:20 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2683595  0.1  1.1 1294676 22232 ?       Sl   02:04   0:20 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2683788  0.1  1.1 1294420 23252 ?       Sl   02:04   0:20 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-23T18:04:12Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-23T18:04:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.10722026-08-23T18:04:12Z INF Registered tunnel connection connIndex=0 connection=d4dae0a9-f40b-4cfc-b1b1-cec93b55ca2d event=0 ip=198.41.192.107 location=sjc06 protocol=quic
2026-08-23T18:04:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.1322026-08-23T18:04:13Z INF Registered tunnel connection connIndex=1 connection=e4c6d50f-bc04-4402-bb91-8bfbb288739d event=0 ip=198.41.200.13 location=sjc08 protocol=quic
2026-08-23T18:04:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-23T18:04:14Z INF Registered tunnel connection connIndex=2 connection=f3f43b30-1cb3-4633-8ac7-a60e69e0e683 event=0 ip=198.41.192.167 location=sjc06 protocol=quic
2026-08-23T18:04:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.43
2026-08-23T18:04:15Z INF Registered tunnel connection connIndex=3 connection=06791928-9088-4644-9811-2acf355a6f16 event=0 ip=198.41.200.43 location=sjc08 protocol=quic
2026-08-23T18:04:22Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T18:04:22Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-08-23T18:04:22Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T18:04:22Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-08-23T18:04:22Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-23T18:04:22Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-08-23T18:04:22Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-08-23T18:04:22Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-08-23T18:04:22Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-23T18:04:22Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-08-23T18:04:22Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-08-23T18:04:22Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-08-23T18:04:22Z INF |                                                                                               |
2026-08-23T18:04:22Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-08-23T18:04:22Z INF +-----------------------------------------------------------------------------------------------+
2026-08-23T18:04:22Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9fe0ae57-7093-4ec1-8a50-ccfc83fcd6c4 status=pass target=region1.v2.argotunnel.com
2026-08-23T18:04:22Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9fe0ae57-7093-4ec1-8a50-ccfc83fcd6c4 status=pass target=region2.v2.argotunnel.com
2026-08-23T18:04:22Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=9fe0ae57-7093-4ec1-8a50-ccfc83fcd6c4 status=pass target=region1.v2.argotunnel.com
2026-08-23T18:04:22Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=9fe0ae57-7093-4ec1-8a50-ccfc83fcd6c4 status=fail target=region2.v2.argotunnel.com
2026-08-23T18:04:22Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9fe0ae57-7093-4ec1-8a50-ccfc83fcd6c4 status=pass target=region1.v2.argotunnel.com
2026-08-23T18:04:22Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9fe0ae57-7093-4ec1-8a50-ccfc83fcd6c4 status=pass target=region2.v2.argotunnel.com
2026-08-23T18:04:22Z INF precheck component="Cloudflare API" details="API is reachable" run_id=9fe0ae57-7093-4ec1-8a50-ccfc83fcd6c4 status=pass target=api.cloudflare.com:443
2026-08-23T18:04:22Z INF precheck complete hard_fail=false run_id=9fe0ae57-7093-4ec1-8a50-ccfc83fcd6c4 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:04:02] Time: Mon Aug 24 02:04:02 AM CST 2026
[02:04:02] User: root (UID: 0)
[02:04:02] === STEP 1: 启动 API (端口 8450) ===
[02:04:04] API 已在运行
[02:04:04] API 状态: OK
[02:04:04] === STEP 2: 安装 cloudflared ===
[02:04:04] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:04] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:04] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:04] === STEP 3: 检查认证方式 ===
[02:04:04] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:04] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:04] 检查现有 tunnel...
[02:04:05] API 已在运行
[02:04:05] API 状态: OK
[02:04:05] === STEP 2: 安装 cloudflared ===
[02:04:05] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:04:05] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:05] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:04:05] === STEP 3: 检查认证方式 ===
[02:04:05] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:04:05] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:04:05] 检查现有 tunnel...
[02:04:05] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xsjc01, 1xsjc05, 3xsjc06, 1xsjc08, 2xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[02:04:05] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:05] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:05] 凭证文件存在
[02:04:05] 创建 config.yml...
[02:04:05] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:05] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:05] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xsjc01, 1xsjc05, 3xsjc06, 1xsjc08, 2xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
[02:04:05] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:05] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:04:05] 凭证文件存在
[02:04:05] 创建 config.yml...
[02:04:05] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:04:05] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:07] DNS 路由结果: 2026-08-23T18:04:07Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:07] === STEP 5: 更新 DNS (API) ===
[02:04:07] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:07] DNS 路由结果: 2026-08-23T18:04:07Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:07] === STEP 5: 更新 DNS (API) ===
[02:04:07] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:07] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[02:04:08] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[02:04:08] 设置 SSL 模式为 Full...
DNS 更新: OK
[02:04:08] 设置 SSL 模式为 Full...
SSL: 跳过
[02:04:09] === STEP 6: 启动 Tunnel ===
SSL: 跳过
[02:04:09] === STEP 6: 启动 Tunnel ===
[02:04:12] 启动 Named Tunnel (cert 模式)...
[02:04:12] 使用 config: /root/.cloudflared/config.yml
[02:04:12] cloudflared PID: 2683576
[02:04:12] 启动 Named Tunnel (cert 模式)...
[02:04:12] 使用 config: /root/.cloudflared/config.yml
[02:04:12] cloudflared PID: 2683595
[02:04:14] Tunnel 连接已建立!
[02:04:14] --- cloudflared 日志 (最后 15 行) ---
2026-08-23T18:04:12Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-23T18:04:12Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-23T18:04:12Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-23T18:04:12Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-23T18:04:12Z INF Generated Connector ID: f6d1b902-9e72-4cf3-b5aa-81838c29a137
2026-08-23T18:04:12Z INF Initial protocol quic
2026-08-23T18:04:12Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-23T18:04:12Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-23T18:04:12Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-23T18:04:12Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-23T18:04:12Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-23T18:04:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.10722026-08-23T18:04:12Z INF Registered tunnel connection connIndex=0 connection=d4dae0a9-f40b-4cfc-b1b1-cec93b55ca2d event=0 ip=198.41.192.107 location=sjc06 protocol=quic
2026-08-23T18:04:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.1322026-08-23T18:04:13Z INF Registered tunnel connection connIndex=1 connection=e4c6d50f-bc04-4402-bb91-8bfbb288739d event=0 ip=198.41.200.13 location=sjc08 protocol=quic
2026-08-23T18:04:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-23T18:04:13Z INF Registered tunnel connection connIndex=2 connection=b2ebb16a-4fa0-42af-8fc2-bd5df15e92be event=0 ip=198.41.192.227 location=sjc01 protocol=quic
[02:04:14] === STEP 7: 持久化 ===
[02:04:14] Tunnel 连接已建立!
[02:04:14] --- cloudflared 日志 (最后 15 行) ---
2026-08-23T18:04:12Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-23T18:04:12Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-23T18:04:12Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-23T18:04:12Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-23T18:04:12Z INF Generated Connector ID: f6d1b902-9e72-4cf3-b5aa-81838c29a137
2026-08-23T18:04:12Z INF Initial protocol quic
2026-08-23T18:04:12Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-23T18:04:12Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-23T18:04:12Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-23T18:04:12Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-23T18:04:12Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-23T18:04:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.10722026-08-23T18:04:12Z INF Registered tunnel connection connIndex=0 connection=d4dae0a9-f40b-4cfc-b1b1-cec93b55ca2d event=0 ip=198.41.192.107 location=sjc06 protocol=quic
2026-08-23T18:04:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.1322026-08-23T18:04:13Z INF Registered tunnel connection connIndex=1 connection=e4c6d50f-bc04-4402-bb91-8bfbb288739d event=0 ip=198.41.200.13 location=sjc08 protocol=quic
2026-08-23T18:04:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.167
2026-08-23T18:04:14Z INF Registered tunnel connection connIndex=2 connection=f3f43b30-1cb3-4633-8ac7-a60e69e0e683 event=0 ip=198.41.192.167 location=sjc06 protocol=quic
[02:04:14] === STEP 7: 持久化 ===
[02:04:15] systemd 服务已配置
[02:04:15] Cron 保活已设置
[02:04:15] === STEP 8: 验证 ===
[02:04:15] --- API (localhost:8450) ---
[02:04:15] systemd 服务已配置
 OK
[02:04:15] Cron 保活已设置
[02:04:15] --- cloudflared 进程 ---
[02:04:15] === STEP 8: 验证 ===
root     2683576  3.3  1.8 1294676 38172 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2683595  3.0  1.9 1294420 39264 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2683788  0.0  1.3 1292484 27560 ?       Rl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:04:15] --- API (localhost:8450) ---
[02:04:15] --- aishield.tools ---
 OK
[02:04:15] --- cloudflared 进程 ---
root     2683576  3.3  1.8 1294676 38172 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2683595  3.0  1.9 1294420 39264 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2683788  0.0  1.3 1292484 27560 ?       Sl   02:04   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:04:15] --- aishield.tools ---
 OK
 OK
[02:04:16] --- DNS CNAME ---
[02:04:16] --- DNS CNAME ---
[02:04:17] --- DNS A ---
[02:04:17] --- DNS A ---
172.67.188.44
104.21.81.46
[02:04:17] === 部署汇总 ===
[02:04:17] Tunnel Mode: cert
[02:04:17] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
104.21.81.46
172.67.188.44
[02:04:17] API: http://localhost:8450
[02:04:17] 域名: https://aishield.tools
[02:04:17] cloudflared: /usr/local/bin/cloudflared
[02:04:17] === 部署汇总 ===
[02:04:17] Tunnel Mode: cert
[02:04:17] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:04:17] API: http://localhost:8450
[02:04:17] PID: 2683576
[02:04:17] 域名: https://aishield.tools
[02:04:17] cloudflared: /usr/local/bin/cloudflared
[02:04:17] Config: /root/.cloudflared/config.yml
[02:04:17] PID: 2683595
[02:04:17] Config: /root/.cloudflared/config.yml
[02:04:17] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:17] 状态: Named Tunnel (cert 模式) 已配置
[02:04:17] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:04:17] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-24 02:04:15 CST; 4h 3min ago
   Main PID: 2683782 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 17.4M
        CPU: 20.401s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2683782 /bin/bash /opt/start-tunnel.sh
             └─2683788 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sun Aug 23 22:07:39 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787522859.1861336, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
