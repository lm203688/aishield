=== DIAGNOSTIC ===
Time: Sat Oct 24 08:12:50 PM CST 2026
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
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1792843970.3640258, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "127cf09ffea3de5d0de3ed6758f0856a8d7b1e70", "deployed_at": "2026-10-24T12:12:17Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}OK
=== CLOUDFLARED PROCESS ===
root     1335162  0.1  1.0 1295188 22000 ?       Ssl  Sep18  85:07 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     2137445  1.4  1.9 1294676 39364 ?       Sl   20:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-24T12:12:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-10-24T12:12:36Z INF Registered tunnel connection connIndex=0 connection=d8635d89-34be-4557-9e02-07c45aa515e0 event=0 ip=198.41.200.113 location=lax13 protocol=quic
2026-10-24T12:12:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-10-24T12:12:36Z INF Registered tunnel connection connIndex=1 connection=6960c245-d7cf-4607-aba1-a9114db0b7af event=0 ip=198.41.192.107 location=lax05 protocol=quic
2026-10-24T12:12:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
2026-10-24T12:12:37Z INF Registered tunnel connection connIndex=2 connection=5848d789-6a80-4735-ade6-1ee341d2c716 event=0 ip=198.41.192.47 location=lax09 protocol=quic
2026-10-24T12:12:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.193
2026-10-24T12:12:38Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-24T12:12:38Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=1 event=0 ip=198.41.192.107
2026-10-24T12:12:38Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.107
2026-10-24T12:12:38Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.192.107
2026-10-24T12:12:38Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.192.107
2026-10-24T12:12:38Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.192.47
2026-10-24T12:12:38Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.47
2026-10-24T12:12:38Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.47
2026-10-24T12:12:38Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.192.47
2026-10-24T12:12:38Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=0 event=0 ip=198.41.200.113
2026-10-24T12:12:38Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-10-24T12:12:38Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.200.113
2026-10-24T12:12:38Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.200.113
2026-10-24T12:12:39Z ERR Connection terminated connIndex=1
2026-10-24T12:12:39Z ERR Connection terminated connIndex=2
2026-10-24T12:12:39Z ERR Connection terminated connIndex=0
2026-10-24T12:12:43Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-10-24T12:12:43Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-10-24T12:12:43Z ERR Connection terminated connIndex=3
2026-10-24T12:12:43Z ERR no more connections active and exiting
2026-10-24T12:12:43Z INF Tunnel server stopped
2026-10-24T12:12:43Z ERR icmp router terminated error="context canceled"
2026-10-24T12:12:43Z INF Metrics server stopped
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[20:12:17] Time: Sat Oct 24 08:12:17 PM CST 2026
[20:12:17] User: root (UID: 0)
[20:12:17] === STEP 1: 启动 API (端口 8450) ===
[20:12:17] 代码由 runner tarball 投递，权威 sha=127cf09f
[20:12:17] commit 对比: 运行进程=41d1f189bd9051ab86d693d6fb5565d99f2a7c9a / 磁盘=127cf09ffea3de5d0de3ed6758f0856a8d7b1e70
[20:12:17] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[20:12:18] 需要重新加载代码 -> 重启 API
[20:12:19] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[20:12:25] API 状态: OK（第 1 轮验证通过）
[20:12:25] === STEP 2: 安装 cloudflared ===
[20:12:25] cloudflared 安装路径: /usr/local/bin/cloudflared
[20:12:25] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[20:12:25] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[20:12:25] === STEP 3: 检查认证方式 ===
[20:12:25] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[20:12:25] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[20:12:25] 检查现有 tunnel...
[20:12:26] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS               
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax07, 1xlax11, 2xlax13 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                           
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                           
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax01, 1xlax11, 1xlax12 
[20:12:26] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[20:12:26] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[20:12:26] 凭证文件存在
[20:12:26] 创建 config.yml...
[20:12:26] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[20:12:26] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[20:12:27] DNS 路由结果: 2026-10-24T12:12:27Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[20:12:27] === STEP 5: 更新 DNS (API) ===
[20:12:27] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[20:12:30] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[20:12:31] 设置 SSL 模式为 Full...
SSL: 跳过
[20:12:32] === STEP 6: 启动 Tunnel ===
[20:12:32] systemd 托管中 -> systemctl stop cloudflared-tunnel
[20:12:35] 启动 Named Tunnel (cert 模式)...
[20:12:35] 使用 config: /root/.cloudflared/config.yml
[20:12:35] cloudflared PID: 2137269
[20:12:37] Tunnel 连接已建立!
[20:12:37] --- cloudflared 日志 (最后 15 行) ---
2026-10-24T12:12:35Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-24T12:12:35Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-24T12:12:35Z INF Generated Connector ID: 6487700c-8862-4e08-8def-155c0467513a
2026-10-24T12:12:35Z INF Initial protocol quic
2026-10-24T12:12:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-24T12:12:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-24T12:12:35Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-24T12:12:35Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-24T12:12:35Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-10-24T12:12:35Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-10-24T12:12:36Z INF Registered tunnel connection connIndex=0 connection=d8635d89-34be-4557-9e02-07c45aa515e0 event=0 ip=198.41.200.113 location=lax13 protocol=quic
2026-10-24T12:12:36Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-10-24T12:12:36Z INF Registered tunnel connection connIndex=1 connection=6960c245-d7cf-4607-aba1-a9114db0b7af event=0 ip=198.41.192.107 location=lax05 protocol=quic
2026-10-24T12:12:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
2026-10-24T12:12:37Z INF Registered tunnel connection connIndex=2 connection=5848d789-6a80-4735-ade6-1ee341d2c716 event=0 ip=198.41.192.47 location=lax09 protocol=quic
[20:12:37] === STEP 7: 持久化 ===
[20:12:38] 停止 nohup cloudflared (PID 2137269) -> 交由 systemd 单实例托管
[20:12:40] systemd 服务已配置
[20:12:40] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[20:12:40] === STEP 8: 验证 ===
[20:12:40] --- API (localhost:8450) ---
 OK
[20:12:40] --- cloudflared 进程 ---
root     1335162  0.1  1.1 1295188 22352 ?       Ssl  Sep18  85:07 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     2137269 25.4  1.9 1294420 39480 ?       Sl   20:12   0:01 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2137445  0.0  1.6 1293588 33352 ?       Sl   20:12   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[20:12:40] --- aishield.tools ---
 OK
[20:12:42] --- DNS CNAME ---
[20:12:43] --- DNS A ---
104.21.81.46
172.67.188.44
[20:12:43] === 部署汇总 ===
[20:12:43] Tunnel Mode: cert
[20:12:43] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[20:12:43] API: http://localhost:8450
[20:12:43] 域名: https://aishield.tools
[20:12:43] cloudflared: /usr/local/bin/cloudflared
[20:12:43] PID: 2137269
[20:12:43] Config: /root/.cloudflared/config.yml
[20:12:43] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[20:12:43] 状态: Named Tunnel (cert 模式) 已配置
[20:12:43] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-10-24 20:12:40 CST; 10s ago
   Main PID: 2137435 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.7M
        CPU: 158ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2137435 /bin/bash /opt/start-tunnel.sh
             └─2137445 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2137002,fd=3))                                                    
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
Time: Sat Oct 24 12:12:59 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1792843979.5958998, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "127cf09ffea3de5d0de3ed6758f0856a8d7b1e70", "deployed_at": "2026-10-24T12:12:17Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
