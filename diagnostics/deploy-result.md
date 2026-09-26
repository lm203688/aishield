=== DIAGNOSTIC ===
Time: Sat Sep 26 09:17:12 AM CST 2026
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
{"status": "ok", "version": "4.8.3", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 235, "rules_breakdown": {"static": 208, "generated": 8, "radar": 19, "total": 235}, "uptime": 1790385432.2402318, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "96b030f012e14c636fa8af8267e56bccb55ed04d", "deployed_at": "2026-09-26T01:16:44Z"}OK
=== CLOUDFLARED PROCESS ===
root      513042  1.2  1.9 1294420 38844 ?       Sl   09:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  1.0 1294932 21960 ?       Sl   Sep18  17:47 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.1 1294932 22748 ?       Ssl  Sep18  17:54 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-26T01:17:00Z INF Registered tunnel connection connIndex=1 connection=b8bd8ff0-1bd5-4a34-a673-96e5b51d91bd event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-09-26T01:17:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-09-26T01:17:00Z INF Registered tunnel connection connIndex=2 connection=1e3510d9-4487-426c-b8de-1fb68ae1f9cf event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-09-26T01:17:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-09-26T01:17:01Z INF Initiating graceful shutdown due to signal terminated ...
2026-09-26T01:17:01Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.200.43
2026-09-26T01:17:01Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.43
2026-09-26T01:17:01Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.43
2026-09-26T01:17:01Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.200.43
2026-09-26T01:17:01Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.200.53
2026-09-26T01:17:01Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.53
2026-09-26T01:17:01Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.53
2026-09-26T01:17:01Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.53
2026-09-26T01:17:01Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.192.107
2026-09-26T01:17:01Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.107
2026-09-26T01:17:01Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.107
2026-09-26T01:17:01Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.107
2026-09-26T01:17:02Z INF Registered tunnel connection connIndex=3 connection=8b81f279-10f7-4d61-b82c-f378ed66fcfa event=0 ip=198.41.192.47 location=lax09 protocol=quic
2026-09-26T01:17:02Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.192.47
2026-09-26T01:17:02Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.47
2026-09-26T01:17:02Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.47
2026-09-26T01:17:02Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.192.47
2026-09-26T01:17:02Z ERR Connection terminated connIndex=2
2026-09-26T01:17:02Z ERR Connection terminated connIndex=0
2026-09-26T01:17:02Z ERR Connection terminated connIndex=1
2026-09-26T01:17:02Z ERR Connection terminated connIndex=3
2026-09-26T01:17:02Z ERR no more connections active and exiting
2026-09-26T01:17:02Z INF Tunnel server stopped
2026-09-26T01:17:02Z ERR icmp router terminated error="context canceled"
2026-09-26T01:17:02Z INF Metrics server stopped
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[09:16:44] Time: Sat Sep 26 09:16:44 AM CST 2026
[09:16:44] User: root (UID: 0)
[09:16:44] === STEP 1: 启动 API (端口 8450) ===
[09:16:44] 代码由 runner tarball 投递，权威 sha=96b030f0
[09:16:44] commit 对比: 运行进程=65d72a7ba364f234c8330a207590afeed737b1f5 / 磁盘=96b030f012e14c636fa8af8267e56bccb55ed04d
[09:16:44] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[09:16:44] 需要重新加载代码 -> 重启 API
[09:16:45] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[09:16:51] API 状态: OK（第 1 轮验证通过）
[09:16:51] === STEP 2: 安装 cloudflared ===
[09:16:51] cloudflared 安装路径: /usr/local/bin/cloudflared
[09:16:51] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:16:51] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[09:16:51] === STEP 3: 检查认证方式 ===
[09:16:51] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[09:16:51] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[09:16:51] 检查现有 tunnel...
[09:16:52] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 3xlax01, 3xlax08, 1xlax10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                    
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xsjc01, 1xsjc06, 2xsjc11          
2026-09-26T01:16:52Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.9.3
[09:16:52] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:16:52] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[09:16:52] 凭证文件存在
[09:16:52] 创建 config.yml...
[09:16:52] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[09:16:52] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:16:53] DNS 路由结果: 2026-09-26T01:16:53Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[09:16:53] === STEP 5: 更新 DNS (API) ===
[09:16:53] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:16:54] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[09:16:55] 设置 SSL 模式为 Full...
SSL: 跳过
[09:16:55] === STEP 6: 启动 Tunnel ===
[09:16:55] systemd 托管中 -> systemctl stop cloudflared-tunnel
[09:16:59] 启动 Named Tunnel (cert 模式)...
[09:16:59] 使用 config: /root/.cloudflared/config.yml
[09:16:59] cloudflared PID: 512912
[09:17:01] Tunnel 连接已建立!
[09:17:01] --- cloudflared 日志 (最后 15 行) ---
2026-09-26T01:16:59Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-26T01:16:59Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-26T01:16:59Z INF Generated Connector ID: ada81ae0-26bf-442c-b662-e2b1a655fb55
2026-09-26T01:16:59Z INF Initial protocol quic
2026-09-26T01:16:59Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-26T01:16:59Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-26T01:16:59Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-26T01:16:59Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-26T01:16:59Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-09-26T01:16:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-09-26T01:16:59Z INF Registered tunnel connection connIndex=0 connection=e9fdcd57-f6a9-456e-b2f4-baa8c5e536cc event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-09-26T01:16:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-09-26T01:17:00Z INF Registered tunnel connection connIndex=1 connection=b8bd8ff0-1bd5-4a34-a673-96e5b51d91bd event=0 ip=198.41.192.107 location=lax08 protocol=quic
2026-09-26T01:17:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-09-26T01:17:00Z INF Registered tunnel connection connIndex=2 connection=1e3510d9-4487-426c-b8de-1fb68ae1f9cf event=0 ip=198.41.200.43 location=lax01 protocol=quic
[09:17:01] === STEP 7: 持久化 ===
[09:17:01] 停止 nohup cloudflared (PID 512912) -> 交由 systemd 单实例托管
[09:17:03] systemd 服务已配置
[09:17:03] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[09:17:03] === STEP 8: 验证 ===
[09:17:03] --- API (localhost:8450) ---
 OK
[09:17:03] --- cloudflared 进程 ---
root      513042  0.0  1.3 1292740 27464 ?       Rl   09:17   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  1.0 1294932 21960 ?       Sl   Sep18  17:47 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.1 1294932 22748 ?       Ssl  Sep18  17:54 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
[09:17:03] --- aishield.tools ---
 OK
[09:17:05] --- DNS CNAME ---
[09:17:05] --- DNS A ---
104.21.81.46
172.67.188.44
[09:17:05] === 部署汇总 ===
[09:17:05] Tunnel Mode: cert
[09:17:05] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[09:17:05] API: http://localhost:8450
[09:17:05] 域名: https://aishield.tools
[09:17:05] cloudflared: /usr/local/bin/cloudflared
[09:17:05] PID: 512912
[09:17:05] Config: /root/.cloudflared/config.yml
[09:17:05] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[09:17:05] 状态: Named Tunnel (cert 模式) 已配置
[09:17:05] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-09-26 09:17:03 CST; 8s ago
   Main PID: 513032 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.5M
        CPU: 131ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─513032 /bin/bash /opt/start-tunnel.sh
             └─513042 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=512595,fd=3))                                                     
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
Time: Sat Sep 26 01:17:20 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.8.3", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 235, "rules_breakdown": {"static": 208, "generated": 8, "radar": 19, "total": 235}, "uptime": 1790385440.625249, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "96b030f012e14c636fa8af8267e56bccb55ed04d", "deployed_at": "2026-09-26T01:16:44Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
