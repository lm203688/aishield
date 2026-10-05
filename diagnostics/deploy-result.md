=== DIAGNOSTIC ===
Time: Mon Oct 5 10:55:43 AM CST 2026
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
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791168943.0595782, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "f5c545857d5b32a8d76527c1cd450a7e13df747d", "deployed_at": "2026-10-05T02:55:14Z"}OK
=== CLOUDFLARED PROCESS ===
root      630336  1.2  1.9 1294420 40112 ?       Sl   10:55   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  1.2 1295188 24436 ?       Sl   Sep18  39:17 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.2 1294932 25680 ?       Ssl  Sep18  39:27 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.2 1294932 24424 ?       Sl   Sep27  18:37 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-05T02:55:29Z INF Registered tunnel connection connIndex=1 connection=db9946a8-0a03-4f20-95b5-680a88fc4daf event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-10-05T02:55:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
2026-10-05T02:55:30Z INF Registered tunnel connection connIndex=2 connection=da1b3350-d22f-4274-bf86-59ef3fc5a482 event=0 ip=198.41.192.107 location=lax05 protocol=quic
2026-10-05T02:55:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.53
2026-10-05T02:55:31Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-05T02:55:31Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.192.107
2026-10-05T02:55:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.107
2026-10-05T02:55:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.107
2026-10-05T02:55:31Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.192.107
2026-10-05T02:55:31Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.200.43
2026-10-05T02:55:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.43
2026-10-05T02:55:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.43
2026-10-05T02:55:31Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.43
2026-10-05T02:55:31Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.192.167
2026-10-05T02:55:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.167
2026-10-05T02:55:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.167
2026-10-05T02:55:31Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.167
2026-10-05T02:55:31Z INF Registered tunnel connection connIndex=3 connection=e7b9d22f-de6b-46c8-a900-28b8bbfb5c89 event=0 ip=198.41.200.53 location=lax13 protocol=quic
2026-10-05T02:55:31Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=3 event=0 ip=198.41.200.53
2026-10-05T02:55:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.53
2026-10-05T02:55:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.53
2026-10-05T02:55:31Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.200.53
2026-10-05T02:55:32Z ERR Connection terminated connIndex=2
2026-10-05T02:55:32Z ERR Connection terminated connIndex=0
2026-10-05T02:55:32Z ERR Connection terminated connIndex=1
2026-10-05T02:55:32Z ERR Connection terminated connIndex=3
2026-10-05T02:55:32Z ERR no more connections active and exiting
2026-10-05T02:55:32Z INF Tunnel server stopped
2026-10-05T02:55:32Z INF Metrics server stopped
2026-10-05T02:55:32Z ERR icmp router terminated error="context canceled"
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[10:55:14] Time: Mon Oct  5 10:55:14 AM CST 2026
[10:55:14] User: root (UID: 0)
[10:55:14] === STEP 1: 启动 API (端口 8450) ===
[10:55:14] 代码由 runner tarball 投递，权威 sha=f5c54585
[10:55:14] commit 对比: 运行进程=e9f2944f66df85db585a53aaa858415c80946b54 / 磁盘=f5c545857d5b32a8d76527c1cd450a7e13df747d
[10:55:14] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[10:55:14] 需要重新加载代码 -> 重启 API
[10:55:15] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[10:55:21] API 状态: OK（第 1 轮验证通过）
[10:55:21] === STEP 2: 安装 cloudflared ===
[10:55:21] cloudflared 安装路径: /usr/local/bin/cloudflared
[10:55:21] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:55:21] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:55:21] === STEP 3: 检查认证方式 ===
[10:55:21] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[10:55:21] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[10:55:21] 检查现有 tunnel...
[10:55:22] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 2xlax01, 1xlax05, 1xlax07, 2xlax08, 2xlax09, 4xlax13 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax01, 1xlax05, 1xlax09                            
[10:55:22] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:55:22] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[10:55:22] 凭证文件存在
[10:55:22] 创建 config.yml...
[10:55:22] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[10:55:22] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:55:23] DNS 路由结果: 2026-10-05T02:55:23Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[10:55:23] === STEP 5: 更新 DNS (API) ===
[10:55:23] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:55:24] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[10:55:25] 设置 SSL 模式为 Full...
SSL: 跳过
[10:55:25] === STEP 6: 启动 Tunnel ===
[10:55:25] systemd 托管中 -> systemctl stop cloudflared-tunnel
[10:55:28] 启动 Named Tunnel (cert 模式)...
[10:55:28] 使用 config: /root/.cloudflared/config.yml
[10:55:28] cloudflared PID: 630221
[10:55:30] Tunnel 连接已建立!
[10:55:30] --- cloudflared 日志 (最后 15 行) ---
2026-10-05T02:55:28Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-05T02:55:28Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-05T02:55:28Z INF Generated Connector ID: 4c7c45ad-c7fb-4d69-89e2-a8bcb1c055c1
2026-10-05T02:55:28Z INF Initial protocol quic
2026-10-05T02:55:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-05T02:55:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-05T02:55:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-05T02:55:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-05T02:55:28Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-05T02:55:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-10-05T02:55:29Z INF Registered tunnel connection connIndex=0 connection=8ddf953a-21dc-46fc-8526-be721687f247 event=0 ip=198.41.200.43 location=lax13 protocol=quic
2026-10-05T02:55:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.167
2026-10-05T02:55:29Z INF Registered tunnel connection connIndex=1 connection=db9946a8-0a03-4f20-95b5-680a88fc4daf event=0 ip=198.41.192.167 location=lax09 protocol=quic
2026-10-05T02:55:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
2026-10-05T02:55:30Z INF Registered tunnel connection connIndex=2 connection=da1b3350-d22f-4274-bf86-59ef3fc5a482 event=0 ip=198.41.192.107 location=lax05 protocol=quic
[10:55:30] === STEP 7: 持久化 ===
[10:55:31] 停止 nohup cloudflared (PID 630221) -> 交由 systemd 单实例托管
[10:55:33] systemd 服务已配置
[10:55:33] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[10:55:33] === STEP 8: 验证 ===
[10:55:33] --- API (localhost:8450) ---
 OK
[10:55:33] --- cloudflared 进程 ---
root      630336  0.0  1.3 1292484 27264 ?       Sl   10:55   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  1.2 1295188 24436 ?       Sl   Sep18  39:17 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.2 1294932 25680 ?       Ssl  Sep18  39:27 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
[10:55:33] --- aishield.tools ---
 OK
[10:55:35] --- DNS CNAME ---
[10:55:35] --- DNS A ---
172.67.188.44
104.21.81.46
[10:55:35] === 部署汇总 ===
[10:55:35] Tunnel Mode: cert
[10:55:35] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:55:35] API: http://localhost:8450
[10:55:35] 域名: https://aishield.tools
[10:55:35] cloudflared: /usr/local/bin/cloudflared
[10:55:35] PID: 630221
[10:55:35] Config: /root/.cloudflared/config.yml
[10:55:35] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:55:35] 状态: Named Tunnel (cert 模式) 已配置
[10:55:35] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-10-05 10:55:33 CST; 9s ago
   Main PID: 630326 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.7M
        CPU: 140ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─630326 /bin/bash /opt/start-tunnel.sh
             └─630336 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=629896,fd=3))                                                     
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
Time: Mon Oct  5 02:55:52 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791168952.7077732, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "f5c545857d5b32a8d76527c1cd450a7e13df747d", "deployed_at": "2026-10-05T02:55:14Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
