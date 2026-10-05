=== DIAGNOSTIC ===
Time: Mon Oct 5 11:16:34 AM CST 2026
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
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791170194.2615235, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "b566e2ea840e003be6afc7668a4a80e9c0d757ae", "deployed_at": "2026-10-05T03:16:06Z", "signing_backend": "ed25519", "identity_ready": false, "identity_reason": "无可用签名密钥"}OK
=== CLOUDFLARED PROCESS ===
root      645370  1.5  1.8 1294420 37992 ?       Sl   11:16   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  1.1 1295188 22172 ?       Sl   Sep18  39:19 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.2 1294932 24148 ?       Ssl  Sep18  39:29 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.1 1294932 22844 ?       Sl   Sep27  18:39 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-05T03:16:22Z INF Registered tunnel connection connIndex=1 connection=50546baa-58b9-4f17-a829-0129a4dc097d event=0 ip=198.41.200.53 location=lax13 protocol=quic
2026-10-05T03:16:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.37
2026-10-05T03:16:23Z INF Registered tunnel connection connIndex=2 connection=84653a16-3ced-4da6-9eba-e81bea02c565 event=0 ip=198.41.192.37 location=lax11 protocol=quic
2026-10-05T03:16:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.23
2026-10-05T03:16:24Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-05T03:16:24Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.192.227
2026-10-05T03:16:24Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.227
2026-10-05T03:16:24Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.227
2026-10-05T03:16:24Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.227
2026-10-05T03:16:24Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.200.53
2026-10-05T03:16:24Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.53
2026-10-05T03:16:24Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.53
2026-10-05T03:16:24Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.53
2026-10-05T03:16:24Z INF Registered tunnel connection connIndex=3 connection=727eb200-9304-4459-ba4e-da7e70f759db event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-10-05T03:16:24Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.192.37
2026-10-05T03:16:24Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.37
2026-10-05T03:16:24Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.37
2026-10-05T03:16:24Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.192.37
2026-10-05T03:16:24Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.200.23
2026-10-05T03:16:24Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.23
2026-10-05T03:16:24Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.23
2026-10-05T03:16:24Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.200.23
2026-10-05T03:16:25Z ERR Connection terminated connIndex=0
2026-10-05T03:16:25Z ERR Connection terminated connIndex=1
2026-10-05T03:16:25Z ERR Connection terminated connIndex=2
2026-10-05T03:16:25Z ERR Connection terminated connIndex=3
2026-10-05T03:16:25Z ERR no more connections active and exiting
2026-10-05T03:16:25Z INF Tunnel server stopped
2026-10-05T03:16:25Z INF Metrics server stopped
2026-10-05T03:16:25Z ERR icmp router terminated error="context canceled"
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[11:16:06] Time: Mon Oct  5 11:16:06 AM CST 2026
[11:16:06] User: root (UID: 0)
[11:16:06] === STEP 1: 启动 API (端口 8450) ===
[11:16:06] 代码由 runner tarball 投递，权威 sha=b566e2ea
[11:16:06] commit 对比: 运行进程=afc283fe3937cee92f2acb6d567ef4a1415181a0 / 磁盘=b566e2ea840e003be6afc7668a4a80e9c0d757ae
[11:16:06] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[11:16:07] 需要重新加载代码 -> 重启 API
[11:16:07] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[11:16:13] API 状态: OK（第 1 轮验证通过）
[11:16:13] === STEP 2: 安装 cloudflared ===
[11:16:13] cloudflared 安装路径: /usr/local/bin/cloudflared
[11:16:14] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:16:14] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[11:16:14] === STEP 3: 检查认证方式 ===
[11:16:14] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[11:16:14] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[11:16:14] 检查现有 tunnel...
[11:16:14] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 3xlax01, 2xlax07, 2xlax08, 1xlax09, 1xlax10, 3xlax13 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax01, 1xlax05, 1xlax09                            
[11:16:14] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:16:14] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[11:16:14] 凭证文件存在
[11:16:14] 创建 config.yml...
[11:16:14] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[11:16:14] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:16:16] DNS 路由结果: 2026-10-05T03:16:16Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[11:16:16] === STEP 5: 更新 DNS (API) ===
[11:16:16] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:16:17] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[11:16:18] 设置 SSL 模式为 Full...
SSL: 跳过
[11:16:18] === STEP 6: 启动 Tunnel ===
[11:16:18] systemd 托管中 -> systemctl stop cloudflared-tunnel
[11:16:21] 启动 Named Tunnel (cert 模式)...
[11:16:21] 使用 config: /root/.cloudflared/config.yml
[11:16:21] cloudflared PID: 645215
[11:16:23] Tunnel 连接已建立!
[11:16:23] --- cloudflared 日志 (最后 15 行) ---
2026-10-05T03:16:21Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-05T03:16:21Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-05T03:16:21Z INF Generated Connector ID: 30bbbcd4-6868-4c84-b31b-ddcc9a14fa8c
2026-10-05T03:16:21Z INF Initial protocol quic
2026-10-05T03:16:21Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-05T03:16:21Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-05T03:16:21Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-05T03:16:21Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-05T03:16:21Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-05T03:16:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.227
2026-10-05T03:16:22Z INF Registered tunnel connection connIndex=0 connection=65f6e3da-be50-46a8-883e-fe3dbaa90f83 event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-10-05T03:16:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-10-05T03:16:22Z INF Registered tunnel connection connIndex=1 connection=50546baa-58b9-4f17-a829-0129a4dc097d event=0 ip=198.41.200.53 location=lax13 protocol=quic
2026-10-05T03:16:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.37
2026-10-05T03:16:23Z INF Registered tunnel connection connIndex=2 connection=84653a16-3ced-4da6-9eba-e81bea02c565 event=0 ip=198.41.192.37 location=lax11 protocol=quic
[11:16:23] === STEP 7: 持久化 ===
[11:16:24] 停止 nohup cloudflared (PID 645215) -> 交由 systemd 单实例托管
[11:16:26] systemd 服务已配置
[11:16:26] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[11:16:26] === STEP 8: 验证 ===
[11:16:26] --- API (localhost:8450) ---
 OK
[11:16:26] --- cloudflared 进程 ---
root      645370  0.0  1.3 1292740 27348 ?       Rl   11:16   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  1.1 1295188 22172 ?       Sl   Sep18  39:19 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.2 1294932 24148 ?       Ssl  Sep18  39:29 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
[11:16:26] --- aishield.tools ---
 OK
[11:16:27] --- DNS CNAME ---
[11:16:28] --- DNS A ---
104.21.81.46
172.67.188.44
[11:16:28] === 部署汇总 ===
[11:16:28] Tunnel Mode: cert
[11:16:28] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[11:16:28] API: http://localhost:8450
[11:16:28] 域名: https://aishield.tools
[11:16:28] cloudflared: /usr/local/bin/cloudflared
[11:16:28] PID: 645215
[11:16:28] Config: /root/.cloudflared/config.yml
[11:16:28] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[11:16:28] 状态: Named Tunnel (cert 模式) 已配置
[11:16:28] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-10-05 11:16:26 CST; 7s ago
   Main PID: 645360 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.3M
        CPU: 158ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─645360 /bin/bash /opt/start-tunnel.sh
             └─645370 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=644916,fd=3))                                                     
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
Time: Mon Oct  5 03:16:41 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791170202.0427418, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "b566e2ea840e003be6afc7668a4a80e9c0d757ae", "deployed_at": "2026-10-05T03:16:06Z", "signing_backend": "ed25519", "identity_ready": false, "identity_reason": "无可用签名密钥"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
