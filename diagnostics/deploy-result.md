=== DIAGNOSTIC ===
Time: Tue Sep 8 04:12:58 PM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1788855178.6533616, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "b524162ee1da7489148fdd3d643bfa70035512fe", "deployed_at": "2026-09-08T08:12:16Z"}OK
=== CLOUDFLARED PROCESS ===
root      616889  0.5  1.8 1294676 37296 ?       Sl   16:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      616904  0.6  1.8 1294676 37908 ?       Ssl  16:12   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root      617087  1.0  1.9 1294420 39824 ?       Sl   16:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-08T08:12:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.47
2026-09-08T08:12:40Z INF Registered tunnel connection connIndex=0 connection=e92a6937-15e6-42e0-b1e9-52685eb8469c event=0 ip=198.41.192.47 location=lax07 protocol=quic
2026-09-08T08:12:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-09-08T08:12:41Z INF Registered tunnel connection connIndex=1 connection=371308c9-f182-4bf5-95c6-8cab907d3b02 event=0 ip=198.41.200.233 location=sjc10 protocol=quic
2026-09-08T08:12:41Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-09-08T08:12:41Z INF +-------------------------------------------------------------------------------------+
2026-09-08T08:12:41Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-09-08T08:12:41Z INF +-------------------------------------------------------------------------------------+
2026-09-08T08:12:41Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-09-08T08:12:41Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-08T08:12:41Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-08T08:12:41Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-08T08:12:41Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-08T08:12:41Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-08T08:12:41Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-08T08:12:41Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-09-08T08:12:41Z INF |                                                                                     |
2026-09-08T08:12:41Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-09-08T08:12:41Z INF +-------------------------------------------------------------------------------------+
2026-09-08T08:12:41Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region1.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region2.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region1.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region2.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region1.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region2.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="Cloudflare API" details="API is reachable" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=api.cloudflare.com:443
2026-09-08T08:12:41Z INF precheck complete hard_fail=false run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a suggested_protocol=quic
2026-09-08T08:12:42Z INF Registered tunnel connection connIndex=2 connection=ef3253e0-bc61-4f50-bc6e-d766f6f85db2 event=0 ip=198.41.200.113 location=sjc11 protocol=quic
2026-09-08T08:12:42Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.7
2026-09-08T08:12:43Z INF Registered tunnel connection connIndex=3 connection=54aac8b0-d03d-4341-abf3-a2a054fe54eb event=0 ip=198.41.192.7 location=lax08 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:12:16] Time: Tue Sep  8 04:12:16 PM CST 2026
[16:12:16] User: root (UID: 0)
[16:12:16] === STEP 1: 启动 API (端口 8450) ===
[16:12:16] 代码由 runner tarball 投递，权威 sha=b524162e
[16:12:16] commit 对比: 运行进程=baafcca0e3fad0d32a614316f9ab0d42738eb4f7 / 磁盘=b524162ee1da7489148fdd3d643bfa70035512fe
[16:12:16] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[16:12:16] 需要重新加载代码 -> 重启 API
[16:12:16] 强制重启 Python API 进程（当前commit=baafcca0e3fad0d32a614316f9ab0d42738eb4f7 目标=b524162ee1da7489148fdd3d643bfa70035512fe）
[16:12:26] API 状态: OK
[16:12:26] === STEP 2: 安装 cloudflared ===
[16:12:26] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:12:26] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:12:27] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:12:27] === STEP 3: 检查认证方式 ===
[16:12:27] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:12:27] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:12:27] 检查现有 tunnel...
[16:12:28] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax09, 2xlax10, 1xlax11, 1xsjc07, 2xsjc08, 1xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax05, 1xsjc08, 1xsjc10                            
2026-09-08T08:12:28Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.3
[16:12:28] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:12:28] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:12:28] 凭证文件存在
[16:12:28] 创建 config.yml...
[16:12:28] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:12:28] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:12:29] DNS 路由结果: 2026-09-08T08:12:29Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:12:29] === STEP 5: 更新 DNS (API) ===
[16:12:29] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:12:30] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:12:30] 设置 SSL 模式为 Full...
SSL: 跳过
[16:12:31] === STEP 6: 启动 Tunnel ===
[16:12:34] 启动 Named Tunnel (cert 模式)...
[16:12:34] 使用 config: /root/.cloudflared/config.yml
[16:12:34] cloudflared PID: 616889
[16:12:42] Tunnel 连接已建立!
[16:12:42] --- cloudflared 日志 (最后 15 行) ---
2026-09-08T08:12:41Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-08T08:12:41Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-08T08:12:41Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-09-08T08:12:41Z INF |                                                                                     |
2026-09-08T08:12:41Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-09-08T08:12:41Z INF +-------------------------------------------------------------------------------------+
2026-09-08T08:12:41Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region1.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region2.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region1.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region2.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region1.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=region2.v2.argotunnel.com
2026-09-08T08:12:41Z INF precheck component="Cloudflare API" details="API is reachable" run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a status=pass target=api.cloudflare.com:443
2026-09-08T08:12:41Z INF precheck complete hard_fail=false run_id=b676bc17-f619-4a6b-a69c-5dcfd961631a suggested_protocol=quic
2026-09-08T08:12:42Z INF Registered tunnel connection connIndex=2 connection=ef3253e0-bc61-4f50-bc6e-d766f6f85db2 event=0 ip=198.41.200.113 location=sjc11 protocol=quic
[16:12:42] === STEP 7: 持久化 ===
[16:12:45] systemd 服务已配置
[16:12:45] Cron 保活已设置
[16:12:45] === STEP 8: 验证 ===
[16:12:45] --- API (localhost:8450) ---
 OK
[16:12:45] --- cloudflared 进程 ---
root      616889  0.9  1.8 1294676 37824 ?       Sl   16:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      616904  1.3  1.9 1294676 38960 ?       Ssl  16:12   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root      617087  0.0  1.2 1292484 25356 ?       Rl   16:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:12:45] --- aishield.tools ---
 OK
[16:12:47] --- DNS CNAME ---
[16:12:48] --- DNS A ---
172.67.188.44
104.21.81.46
[16:12:48] === 部署汇总 ===
[16:12:48] Tunnel Mode: cert
[16:12:48] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:12:48] API: http://localhost:8450
[16:12:48] 域名: https://aishield.tools
[16:12:48] cloudflared: /usr/local/bin/cloudflared
[16:12:48] PID: 616889
[16:12:48] Config: /root/.cloudflared/config.yml
[16:12:48] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:12:48] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-09-08 16:12:45 CST; 13s ago
   Main PID: 617082 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 19.6M
        CPU: 136ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─617082 /bin/bash /opt/start-tunnel.sh
             └─617087 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=616572,fd=3))                                                     
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
Time: Tue Sep  8 08:13:09 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1788855189.7627258, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "b524162ee1da7489148fdd3d643bfa70035512fe", "deployed_at": "2026-09-08T08:12:16Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
