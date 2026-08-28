=== DIAGNOSTIC ===
Time: Fri Aug 28 11:45:23 PM CST 2026
=== USER ===
root
=== GIT LOG ===
e8f0836f chore(meta): 体系体检 score=83 level=degraded
52ffde67 fix(deploy): detect stale process by comparing running version vs on-disk version
af0fb245 auto: 部署验证状态回写 [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787931923.2710295, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     3121962  1.0  1.9 1294676 39656 ?       Sl   23:45   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3122060  1.5  1.9 1293844 39988 ?       Sl   23:45   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-28T15:45:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-28T15:45:12Z INF Registered tunnel connection connIndex=0 connection=c921b349-78b3-469f-aa9b-14b618cd751d event=0 ip=198.41.192.167 location=lax11 protocol=quic
2026-08-28T15:45:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-28T15:45:13Z INF Registered tunnel connection connIndex=1 connection=e76a1ddd-eda5-4bcf-a9fd-c7677c11a9a0 event=0 ip=198.41.200.43 location=sjc08 protocol=quic
2026-08-28T15:45:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-28T15:45:13Z INF Registered tunnel connection connIndex=2 connection=410b32b3-1b12-48e8-9797-d6a53197e3d8 event=0 ip=198.41.200.33 location=sjc11 protocol=quic
2026-08-28T15:45:14Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.227
2026-08-28T15:45:14Z INF Registered tunnel connection connIndex=3 connection=df0d3403-9c7d-4886-9f39-d3fdd0480af1 event=0 ip=198.41.192.227 location=lax10 protocol=quic
2026-08-28T15:45:18Z INF +-------------------------------------------------------------------------------------+
2026-08-28T15:45:18Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-28T15:45:18Z INF +-------------------------------------------------------------------------------------+
2026-08-28T15:45:18Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-28T15:45:18Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T15:45:18Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-28T15:45:18Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T15:45:18Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-28T15:45:18Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T15:45:18Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-28T15:45:18Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-28T15:45:18Z INF |                                                                                     |
2026-08-28T15:45:18Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-28T15:45:18Z INF +-------------------------------------------------------------------------------------+
2026-08-28T15:45:18Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9af85f04-ae99-4fb2-a320-347947815aea status=pass target=region1.v2.argotunnel.com
2026-08-28T15:45:18Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=9af85f04-ae99-4fb2-a320-347947815aea status=pass target=region2.v2.argotunnel.com
2026-08-28T15:45:18Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=9af85f04-ae99-4fb2-a320-347947815aea status=pass target=region1.v2.argotunnel.com
2026-08-28T15:45:18Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=9af85f04-ae99-4fb2-a320-347947815aea status=pass target=region2.v2.argotunnel.com
2026-08-28T15:45:18Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9af85f04-ae99-4fb2-a320-347947815aea status=pass target=region1.v2.argotunnel.com
2026-08-28T15:45:18Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=9af85f04-ae99-4fb2-a320-347947815aea status=pass target=region2.v2.argotunnel.com
2026-08-28T15:45:18Z INF precheck component="Cloudflare API" details="API is reachable" run_id=9af85f04-ae99-4fb2-a320-347947815aea status=pass target=api.cloudflare.com:443
2026-08-28T15:45:18Z INF precheck complete hard_fail=false run_id=9af85f04-ae99-4fb2-a320-347947815aea suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:44:48] Time: Fri Aug 28 11:44:48 PM CST 2026
[23:44:48] User: root (UID: 0)
[23:44:48] === STEP 1: 启动 API (端口 8450) ===
[23:44:49] HEAD: e8f0836f -> e8f0836f
[23:45:00] server-card 版本: 磁盘=none 仓库=unknown
[23:45:00] 运行进程自报版本=4.2 / 磁盘代码版本=none
[23:45:00] 代码已是最新且 API 健康 -> 跳过重启
[23:45:00] API 状态: OK
[23:45:00] === STEP 2: 安装 cloudflared ===
[23:45:00] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:45:00] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:45:00] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:45:00] === STEP 3: 检查认证方式 ===
[23:45:00] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:45:00] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:45:00] 检查现有 tunnel...
[23:45:02] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 2xlax08, 1xlax11, 1xlax12, 2xsjc08, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
[23:45:02] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:45:02] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:45:02] 凭证文件存在
[23:45:02] 创建 config.yml...
[23:45:02] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:45:02] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:45:04] DNS 路由结果: 2026-08-28T15:45:04Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:45:04] === STEP 5: 更新 DNS (API) ===
[23:45:04] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:45:05] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[23:45:06] 设置 SSL 模式为 Full...
SSL: 跳过
[23:45:08] === STEP 6: 启动 Tunnel ===
[23:45:11] 启动 Named Tunnel (cert 模式)...
[23:45:11] 使用 config: /root/.cloudflared/config.yml
[23:45:11] cloudflared PID: 3121962
[23:45:13] Tunnel 连接已建立!
[23:45:13] --- cloudflared 日志 (最后 15 行) ---
2026-08-28T15:45:11Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-28T15:45:11Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-28T15:45:11Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-28T15:45:11Z INF Generated Connector ID: 17467223-3294-45ff-88dd-a9323878af7c
2026-08-28T15:45:11Z INF Initial protocol quic
2026-08-28T15:45:11Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:45:11Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:45:11Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-28T15:45:11Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-28T15:45:11Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-28T15:45:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-28T15:45:12Z INF Registered tunnel connection connIndex=0 connection=c921b349-78b3-469f-aa9b-14b618cd751d event=0 ip=198.41.192.167 location=lax11 protocol=quic
2026-08-28T15:45:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-08-28T15:45:13Z INF Registered tunnel connection connIndex=1 connection=e76a1ddd-eda5-4bcf-a9fd-c7677c11a9a0 event=0 ip=198.41.200.43 location=sjc08 protocol=quic
2026-08-28T15:45:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
[23:45:13] === STEP 7: 持久化 ===
[23:45:14] systemd 服务已配置
[23:45:14] Cron 保活已设置
[23:45:14] === STEP 8: 验证 ===
[23:45:14] --- API (localhost:8450) ---
 OK
[23:45:14] --- cloudflared 进程 ---
root     3121962  3.3  1.9 1294676 39416 ?       Sl   23:45   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3122060  0.0  1.3 1292484 27780 ?       Rl   23:45   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[23:45:14] --- aishield.tools ---
 OK
[23:45:15] --- DNS CNAME ---
[23:45:16] --- DNS A ---
104.21.81.46
172.67.188.44
[23:45:16] === 部署汇总 ===
[23:45:16] Tunnel Mode: cert
[23:45:16] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:45:16] API: http://localhost:8450
[23:45:16] 域名: https://aishield.tools
[23:45:16] cloudflared: /usr/local/bin/cloudflared
[23:45:16] PID: 3121962
[23:45:16] Config: /root/.cloudflared/config.yml
[23:45:16] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:45:16] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-08-28 23:45:14 CST; 8s ago
   Main PID: 3122056 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.1M
        CPU: 147ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3122056 /bin/bash /opt/start-tunnel.sh
             └─3122060 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Fri Aug 28 15:45:23 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787931923.6933937, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
