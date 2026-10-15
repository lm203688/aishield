=== DIAGNOSTIC ===
Time: Thu Oct 15 08:20:35 AM CST 2026
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
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1792023635.2491105, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "299e7bc341e7f3af50a4e0730a361e7bb53d179a", "deployed_at": "2026-10-15T00:20:05Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}OK
=== CLOUDFLARED PROCESS ===
root     1335051  0.1  0.8 1295188 17640 ?       Sl   Sep18  62:58 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.0 1295188 20568 ?       Ssl  Sep18  63:13 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1486761  1.3  1.9 1294676 39868 ?       Sl   08:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.0 1294932 20380 ?       Sl   Sep27  42:17 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-15T00:20:23Z INF Registered tunnel connection connIndex=1 connection=779b4077-9734-468b-93e3-f11394aa0faf event=0 ip=198.41.192.57 location=lax09 protocol=quic
2026-10-15T00:20:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
2026-10-15T00:20:24Z INF Registered tunnel connection connIndex=2 connection=972140f8-a223-4496-8992-8f7ad19a7a5a event=0 ip=198.41.192.77 location=lax07 protocol=quic
2026-10-15T00:20:24Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.63
2026-10-15T00:20:25Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-15T00:20:25Z INF Registered tunnel connection connIndex=3 connection=d6434511-c57c-491b-9353-0d0ff42ee4a9 event=0 ip=198.41.200.63 location=lax13 protocol=quic
2026-10-15T00:20:25Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.192.77
2026-10-15T00:20:25Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.77
2026-10-15T00:20:25Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.77
2026-10-15T00:20:25Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.192.77
2026-10-15T00:20:25Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.192.57
2026-10-15T00:20:25Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.57
2026-10-15T00:20:25Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.57
2026-10-15T00:20:25Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.57
2026-10-15T00:20:25Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.200.43
2026-10-15T00:20:25Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.43
2026-10-15T00:20:25Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.43
2026-10-15T00:20:25Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.43
2026-10-15T00:20:25Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.200.63
2026-10-15T00:20:25Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.63
2026-10-15T00:20:25Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.63
2026-10-15T00:20:25Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.200.63
2026-10-15T00:20:25Z ERR Connection terminated connIndex=2
2026-10-15T00:20:25Z ERR Connection terminated connIndex=1
2026-10-15T00:20:25Z ERR Connection terminated connIndex=0
2026-10-15T00:20:25Z ERR Connection terminated connIndex=3
2026-10-15T00:20:25Z ERR no more connections active and exiting
2026-10-15T00:20:25Z INF Tunnel server stopped
2026-10-15T00:20:25Z ERR icmp router terminated error="context canceled"
2026-10-15T00:20:25Z INF Metrics server stopped
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:20:05] Time: Thu Oct 15 08:20:05 AM CST 2026
[08:20:05] User: root (UID: 0)
[08:20:05] === STEP 1: 启动 API (端口 8450) ===
[08:20:05] 代码由 runner tarball 投递，权威 sha=299e7bc3
[08:20:05] commit 对比: 运行进程=b512ae17e63155a98619008aa22e176b2a317a95 / 磁盘=299e7bc341e7f3af50a4e0730a361e7bb53d179a
[08:20:05] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[08:20:06] 需要重新加载代码 -> 重启 API
[08:20:07] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[08:20:14] API 状态: OK（第 1 轮验证通过）
[08:20:14] === STEP 2: 安装 cloudflared ===
[08:20:14] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:20:14] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:20:14] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:20:14] === STEP 3: 检查认证方式 ===
[08:20:14] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:20:14] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:20:14] 检查现有 tunnel...
[08:20:15] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                                            
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax01, 1xlax05, 1xlax07, 2xlax08, 2xlax09, 3xlax13, 1xsjc07, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                                        
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                                        
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax01, 1xlax05, 1xlax07, 1xlax13                                     
[08:20:15] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:20:15] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:20:15] 凭证文件存在
[08:20:15] 创建 config.yml...
[08:20:15] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:20:15] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:20:17] DNS 路由结果: 2026-10-15T00:20:17Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:20:17] === STEP 5: 更新 DNS (API) ===
[08:20:17] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:20:17] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[08:20:18] 设置 SSL 模式为 Full...
SSL: 跳过
[08:20:19] === STEP 6: 启动 Tunnel ===
[08:20:19] systemd 托管中 -> systemctl stop cloudflared-tunnel
[08:20:22] 启动 Named Tunnel (cert 模式)...
[08:20:22] 使用 config: /root/.cloudflared/config.yml
[08:20:22] cloudflared PID: 1486596
[08:20:24] Tunnel 连接已建立!
[08:20:24] --- cloudflared 日志 (最后 15 行) ---
2026-10-15T00:20:22Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-10-15T00:20:22Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-15T00:20:22Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-15T00:20:22Z INF Generated Connector ID: ff296a4a-d1e6-4420-a420-d5c9d0ee5d46
2026-10-15T00:20:22Z INF Initial protocol quic
2026-10-15T00:20:22Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-15T00:20:22Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-15T00:20:22Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-15T00:20:22Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-15T00:20:22Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-15T00:20:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-10-15T00:20:22Z INF Registered tunnel connection connIndex=0 connection=f98c735c-746c-4ad7-b263-d81b7de67e22 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-10-15T00:20:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-10-15T00:20:23Z INF Registered tunnel connection connIndex=1 connection=779b4077-9734-468b-93e3-f11394aa0faf event=0 ip=198.41.192.57 location=lax09 protocol=quic
2026-10-15T00:20:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.77
[08:20:24] === STEP 7: 持久化 ===
[08:20:25] 停止 nohup cloudflared (PID 1486596) -> 交由 systemd 单实例托管
[08:20:27] systemd 服务已配置
[08:20:27] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[08:20:27] === STEP 8: 验证 ===
[08:20:27] --- API (localhost:8450) ---
 OK
[08:20:27] --- cloudflared 进程 ---
root     1335051  0.1  0.8 1295188 17640 ?       Sl   Sep18  62:58 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.0 1295188 20568 ?       Ssl  Sep18  63:13 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1486761  0.0  1.3 1292740 27504 ?       Rl   08:20   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:20:27] --- aishield.tools ---
 OK
[08:20:29] --- DNS CNAME ---
[08:20:29] --- DNS A ---
104.21.81.46
172.67.188.44
[08:20:29] === 部署汇总 ===
[08:20:29] Tunnel Mode: cert
[08:20:29] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:20:29] API: http://localhost:8450
[08:20:29] 域名: https://aishield.tools
[08:20:29] cloudflared: /usr/local/bin/cloudflared
[08:20:29] PID: 1486596
[08:20:29] Config: /root/.cloudflared/config.yml
[08:20:29] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:20:29] 状态: Named Tunnel (cert 模式) 已配置
[08:20:29] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-10-15 08:20:27 CST; 8s ago
   Main PID: 1486740 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.7M
        CPU: 132ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1486740 /bin/bash /opt/start-tunnel.sh
             └─1486761 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=1485861,fd=3))                                                    
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
Time: Thu Oct 15 00:20:44 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1792023644.957882, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "299e7bc341e7f3af50a4e0730a361e7bb53d179a", "deployed_at": "2026-10-15T00:20:05Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
