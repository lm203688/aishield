=== DIAGNOSTIC ===
Time: Fri Oct 9 06:39:57 PM CST 2026
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
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791542397.2130814, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "782471428f4c499d069c01f97546bf6fd9609904", "deployed_at": "2026-10-09T10:39:19Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}OK
=== CLOUDFLARED PROCESS ===
root      475515  0.9  1.9 1294420 39828 ?       Sl   18:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  0.9 1295188 19828 ?       Sl   Sep18  49:37 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.1 1294932 22600 ?       Ssl  Sep18  49:50 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.1 1294932 22676 ?       Sl   Sep27  28:59 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-09T10:39:38Z INF Registered tunnel connection connIndex=1 connection=28a45d8f-0c33-4475-8ca0-42e95f02dc79 event=0 ip=198.41.192.107 location=lax10 protocol=quic
2026-10-09T10:39:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-10-09T10:39:39Z INF Registered tunnel connection connIndex=2 connection=8d46168b-e535-4ed5-b1aa-b370f5149250 event=0 ip=198.41.200.23 location=lax01 protocol=quic
2026-10-09T10:39:40Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.77
2026-10-09T10:39:40Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-09T10:39:40Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=0 event=0 ip=198.41.200.53
2026-10-09T10:39:40Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.53
2026-10-09T10:39:40Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.53
2026-10-09T10:39:40Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.53
2026-10-09T10:39:40Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.200.23
2026-10-09T10:39:40Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.23
2026-10-09T10:39:40Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.23
2026-10-09T10:39:40Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.200.23
2026-10-09T10:39:40Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.192.107
2026-10-09T10:39:40Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.107
2026-10-09T10:39:40Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.107
2026-10-09T10:39:40Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.107
2026-10-09T10:39:40Z INF Registered tunnel connection connIndex=3 connection=65c74440-aa5d-48f6-a9da-4d9b568f7013 event=0 ip=198.41.192.77 location=lax10 protocol=quic
2026-10-09T10:39:41Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.192.77
2026-10-09T10:39:41Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.77
2026-10-09T10:39:41Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.77
2026-10-09T10:39:41Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.192.77
2026-10-09T10:39:41Z ERR Connection terminated connIndex=0
2026-10-09T10:39:41Z ERR Connection terminated connIndex=2
2026-10-09T10:39:41Z ERR Connection terminated connIndex=1
2026-10-09T10:39:41Z ERR Connection terminated connIndex=3
2026-10-09T10:39:41Z ERR no more connections active and exiting
2026-10-09T10:39:41Z INF Tunnel server stopped
2026-10-09T10:39:41Z ERR icmp router terminated error="context canceled"
2026-10-09T10:39:41Z INF Metrics server stopped
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:39:19] Time: Fri Oct  9 06:39:19 PM CST 2026
[18:39:19] User: root (UID: 0)
[18:39:19] === STEP 1: 启动 API (端口 8450) ===
[18:39:19] 代码由 runner tarball 投递，权威 sha=78247142
[18:39:19] commit 对比: 运行进程=e352c5f9571446422273d24c00f2300c3fd5155a / 磁盘=782471428f4c499d069c01f97546bf6fd9609904
[18:39:19] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[18:39:21] 需要重新加载代码 -> 重启 API
[18:39:23] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[18:39:29] API 状态: OK（第 1 轮验证通过）
[18:39:29] === STEP 2: 安装 cloudflared ===
[18:39:29] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:39:29] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:39:29] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:39:29] === STEP 3: 检查认证方式 ===
[18:39:29] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:39:29] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:39:29] 检查现有 tunnel...
[18:39:31] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 4xlax01, 4xlax08, 1xlax09, 1xlax10, 2xlax13 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                             
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax01, 1xlax09, 1xlax10                   
2026-10-09T10:39:31Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.10.0
[18:39:31] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:39:31] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:39:31] 凭证文件存在
[18:39:31] 创建 config.yml...
[18:39:31] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:39:31] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:39:32] DNS 路由结果: 2026-10-09T10:39:32Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:39:32] === STEP 5: 更新 DNS (API) ===
[18:39:32] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:39:33] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[18:39:34] 设置 SSL 模式为 Full...
SSL: 跳过
[18:39:34] === STEP 6: 启动 Tunnel ===
[18:39:34] systemd 托管中 -> systemctl stop cloudflared-tunnel
[18:39:38] 启动 Named Tunnel (cert 模式)...
[18:39:38] 使用 config: /root/.cloudflared/config.yml
[18:39:38] cloudflared PID: 475354
[18:39:40] Tunnel 连接已建立!
[18:39:40] --- cloudflared 日志 (最后 15 行) ---
2026-10-09T10:39:38Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-09T10:39:38Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-09T10:39:38Z INF Generated Connector ID: 1c7f0987-4884-4dae-8097-f514cc028ac5
2026-10-09T10:39:38Z INF Initial protocol quic
2026-10-09T10:39:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-09T10:39:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-09T10:39:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-09T10:39:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-09T10:39:38Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-09T10:39:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.53
2026-10-09T10:39:38Z INF Registered tunnel connection connIndex=0 connection=548f5da0-0b39-43c6-8872-6d7c181ae249 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-10-09T10:39:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-10-09T10:39:38Z INF Registered tunnel connection connIndex=1 connection=28a45d8f-0c33-4475-8ca0-42e95f02dc79 event=0 ip=198.41.192.107 location=lax10 protocol=quic
2026-10-09T10:39:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-10-09T10:39:39Z INF Registered tunnel connection connIndex=2 connection=8d46168b-e535-4ed5-b1aa-b370f5149250 event=0 ip=198.41.200.23 location=lax01 protocol=quic
[18:39:40] === STEP 7: 持久化 ===
[18:39:40] 停止 nohup cloudflared (PID 475354) -> 交由 systemd 单实例托管
[18:39:42] systemd 服务已配置
[18:39:42] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[18:39:42] === STEP 8: 验证 ===
[18:39:42] --- API (localhost:8450) ---
 OK
[18:39:42] --- cloudflared 进程 ---
root      475515  0.0  1.0 1292484 21080 ?       Rl   18:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  0.9 1295188 19904 ?       Sl   Sep18  49:37 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.1 1294932 22676 ?       Ssl  Sep18  49:50 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
[18:39:42] --- aishield.tools ---
 OK
[18:39:49] --- DNS CNAME ---
[18:39:49] --- DNS A ---
172.67.188.44
104.21.81.46
[18:39:49] === 部署汇总 ===
[18:39:49] Tunnel Mode: cert
[18:39:49] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:39:49] API: http://localhost:8450
[18:39:49] 域名: https://aishield.tools
[18:39:49] cloudflared: /usr/local/bin/cloudflared
[18:39:49] PID: 475354
[18:39:49] Config: /root/.cloudflared/config.yml
[18:39:49] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:39:49] 状态: Named Tunnel (cert 模式) 已配置
[18:39:49] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-10-09 18:39:42 CST; 14s ago
   Main PID: 475495 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 19.9M
        CPU: 162ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─475495 /bin/bash /opt/start-tunnel.sh
             └─475515 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=475058,fd=3))                                                     
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
Time: Fri Oct  9 10:40:08 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791542408.9589458, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "782471428f4c499d069c01f97546bf6fd9609904", "deployed_at": "2026-10-09T10:39:19Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
