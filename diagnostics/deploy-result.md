=== DIAGNOSTIC ===
Time: Tue Oct 6 06:29:34 PM CST 2026
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
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791282574.3618944, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "49012136576c19578573c8df74d0bec811001cf0", "deployed_at": "2026-10-06T10:28:52Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}OK
=== CLOUDFLARED PROCESS ===
root     1335051  0.1  1.1 1295188 22616 ?       Sl   Sep18  42:28 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.3 1294932 27816 ?       Ssl  Sep18  42:41 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.4 1294932 28728 ?       Sl   Sep27  21:50 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1862960  0.7  1.9 1294676 39916 ?       Sl   18:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-06T10:29:12Z INF Registered tunnel connection connIndex=1 connection=934fa692-d0ec-4079-a37b-121c29129235 event=0 ip=198.41.200.43 location=lax13 protocol=quic
2026-10-06T10:29:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-10-06T10:29:12Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-06T10:29:12Z INF Registered tunnel connection connIndex=2 connection=95a9d37c-0baf-406b-8c29-4fcb0ca456f9 event=0 ip=198.41.200.113 location=lax13 protocol=quic
2026-10-06T10:29:13Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.192.77
2026-10-06T10:29:13Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.77
2026-10-06T10:29:13Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.77
2026-10-06T10:29:13Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.77
2026-10-06T10:29:13Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.200.43
2026-10-06T10:29:13Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.43
2026-10-06T10:29:13Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.43
2026-10-06T10:29:13Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.43
2026-10-06T10:29:13Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.200.113
2026-10-06T10:29:13Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.113
2026-10-06T10:29:13Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.113
2026-10-06T10:29:13Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.200.113
2026-10-06T10:29:13Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.57
2026-10-06T10:29:14Z INF Registered tunnel connection connIndex=3 connection=3e06fd21-ae8b-4631-af51-633f4f0a7b0f event=0 ip=198.41.192.57 location=lax11 protocol=quic
2026-10-06T10:29:14Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.192.57
2026-10-06T10:29:14Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.57
2026-10-06T10:29:14Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.57
2026-10-06T10:29:14Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.192.57
2026-10-06T10:29:14Z ERR Connection terminated connIndex=0
2026-10-06T10:29:14Z ERR Connection terminated connIndex=1
2026-10-06T10:29:14Z ERR Connection terminated connIndex=2
2026-10-06T10:29:14Z ERR Connection terminated connIndex=3
2026-10-06T10:29:14Z ERR no more connections active and exiting
2026-10-06T10:29:14Z INF Tunnel server stopped
2026-10-06T10:29:14Z INF Metrics server stopped
2026-10-06T10:29:14Z ERR icmp router terminated error="context canceled"
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:28:51] Time: Tue Oct  6 06:28:51 PM CST 2026
[18:28:51] User: root (UID: 0)
[18:28:51] === STEP 1: 启动 API (端口 8450) ===
[18:28:52] 代码由 runner tarball 投递，权威 sha=49012136
[18:28:52] commit 对比: 运行进程=69f6d59566d97be3923b999babbbde22e4781482 / 磁盘=49012136576c19578573c8df74d0bec811001cf0
[18:28:52] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[18:28:53] 需要重新加载代码 -> 重启 API
[18:28:55] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[18:29:01] API 状态: OK（第 1 轮验证通过）
[18:29:01] === STEP 2: 安装 cloudflared ===
[18:29:01] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:29:01] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:29:01] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:29:01] === STEP 3: 检查认证方式 ===
[18:29:01] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:29:01] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:29:01] 检查现有 tunnel...
[18:29:02] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 2xlax01, 1xlax07, 2xlax08, 1xlax09, 2xlax10, 4xlax13 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax01, 1xlax09, 1xlax10                            
[18:29:02] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:29:02] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:29:02] 凭证文件存在
[18:29:02] 创建 config.yml...
[18:29:02] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:29:02] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:29:04] DNS 路由结果: 2026-10-06T10:29:04Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:29:04] === STEP 5: 更新 DNS (API) ===
[18:29:04] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:29:04] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[18:29:06] 设置 SSL 模式为 Full...
SSL: 跳过
[18:29:07] === STEP 6: 启动 Tunnel ===
[18:29:07] systemd 托管中 -> systemctl stop cloudflared-tunnel
[18:29:10] 启动 Named Tunnel (cert 模式)...
[18:29:10] 使用 config: /root/.cloudflared/config.yml
[18:29:10] cloudflared PID: 1862846
[18:29:12] Tunnel 连接已建立!
[18:29:12] --- cloudflared 日志 (最后 15 行) ---
2026-10-06T10:29:10Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-10-06T10:29:10Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-10-06T10:29:10Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-06T10:29:10Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-06T10:29:10Z INF Generated Connector ID: 3865760b-19e2-48b5-a8ba-bc33dee5584c
2026-10-06T10:29:10Z INF Initial protocol quic
2026-10-06T10:29:10Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-06T10:29:10Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-06T10:29:10Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-06T10:29:10Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-06T10:29:10Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-06T10:29:10Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.77
2026-10-06T10:29:11Z INF Registered tunnel connection connIndex=0 connection=24a7655f-7690-489f-84be-857d4ec80e0d event=0 ip=198.41.192.77 location=lax09 protocol=quic
2026-10-06T10:29:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.43
2026-10-06T10:29:12Z INF Registered tunnel connection connIndex=1 connection=934fa692-d0ec-4079-a37b-121c29129235 event=0 ip=198.41.200.43 location=lax13 protocol=quic
[18:29:12] === STEP 7: 持久化 ===
[18:29:12] 停止 nohup cloudflared (PID 1862846) -> 交由 systemd 单实例托管
[18:29:14] systemd 服务已配置
[18:29:14] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[18:29:14] === STEP 8: 验证 ===
[18:29:14] --- API (localhost:8450) ---
 OK
[18:29:14] --- cloudflared 进程 ---
root     1335051  0.1  1.1 1295188 22620 ?       Sl   Sep18  42:28 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.3 1294932 27820 ?       Ssl  Sep18  42:41 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
[18:29:14] --- aishield.tools ---
 OK
[18:29:19] --- DNS CNAME ---
[18:29:19] --- DNS A ---
172.67.188.44
104.21.81.46
[18:29:19] === 部署汇总 ===
[18:29:19] Tunnel Mode: cert
[18:29:19] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:29:20] API: http://localhost:8450
[18:29:20] 域名: https://aishield.tools
[18:29:20] cloudflared: /usr/local/bin/cloudflared
[18:29:20] PID: 1862846
[18:29:20] Config: /root/.cloudflared/config.yml
[18:29:20] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:29:20] 状态: Named Tunnel (cert 模式) 已配置
[18:29:20] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-10-06 18:29:14 CST; 19s ago
   Main PID: 1862950 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.2M
        CPU: 159ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1862950 /bin/bash /opt/start-tunnel.sh
             └─1862960 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=1862480,fd=3))                                                    
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
Time: Tue Oct  6 10:29:50 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791282591.1844153, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "49012136576c19578573c8df74d0bec811001cf0", "deployed_at": "2026-10-06T10:28:52Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
