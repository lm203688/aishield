=== DIAGNOSTIC ===
Time: Fri Oct 2 12:29:46 PM CST 2026
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
{"status": "ok", "version": "4.10.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 253, "rules_breakdown": {"static": 226, "generated": 8, "radar": 19, "total": 253}, "uptime": 1790915386.7802746, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "323cf4e14b294d7add4156b8aba802ab9c8d50bb", "deployed_at": "2026-10-02T04:29:13Z"}OK
=== CLOUDFLARED PROCESS ===
root     1335051  0.1  1.1 1294932 22816 ?       Sl   Sep18  32:05 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.1 1294932 23560 ?       Ssl  Sep18  31:52 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.1 1294676 22244 ?       Sl   Sep27  11:11 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2070779  1.0  1.9 1294676 39652 ?       Sl   12:29   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-02T04:29:29Z INF Registered tunnel connection connIndex=1 connection=e2405bec-7341-47d7-b55b-a4fc38125e3d event=0 ip=198.41.200.13 location=lax13 protocol=quic
2026-10-02T04:29:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
2026-10-02T04:29:30Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-02T04:29:30Z INF Registered tunnel connection connIndex=2 connection=6ebfbeb7-6c1b-4ecd-9ac2-f63258a9480c event=0 ip=198.41.192.227 location=lax07 protocol=quic
2026-10-02T04:29:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.233
2026-10-02T04:29:30Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.192.27
2026-10-02T04:29:30Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.27
2026-10-02T04:29:30Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.27
2026-10-02T04:29:30Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.27
2026-10-02T04:29:31Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=1 event=0 ip=198.41.200.13
2026-10-02T04:29:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.13
2026-10-02T04:29:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.13
2026-10-02T04:29:31Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.13
2026-10-02T04:29:31Z ERR failed to run the datagram handler error="context canceled" connIndex=2 event=0 ip=198.41.192.227
2026-10-02T04:29:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.227
2026-10-02T04:29:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.192.227
2026-10-02T04:29:31Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.192.227
2026-10-02T04:29:31Z ERR Connection terminated connIndex=0
2026-10-02T04:29:31Z ERR Connection terminated connIndex=1
2026-10-02T04:29:31Z ERR Connection terminated connIndex=2
2026-10-02T04:29:31Z INF Registered tunnel connection connIndex=3 connection=ad6d95dc-bc34-4b99-8119-c06104b20b0f event=0 ip=198.41.200.233 location=lax01 protocol=quic
2026-10-02T04:29:32Z ERR failed to run the datagram handler error="context canceled" connIndex=3 event=0 ip=198.41.200.233
2026-10-02T04:29:32Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.233
2026-10-02T04:29:32Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.200.233
2026-10-02T04:29:32Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.200.233
2026-10-02T04:29:32Z ERR Connection terminated connIndex=3
2026-10-02T04:29:32Z ERR no more connections active and exiting
2026-10-02T04:29:32Z INF Tunnel server stopped
2026-10-02T04:29:32Z ERR icmp router terminated error="context canceled"
2026-10-02T04:29:32Z INF Metrics server stopped
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[12:29:13] Time: Fri Oct  2 12:29:13 PM CST 2026
[12:29:13] User: root (UID: 0)
[12:29:13] === STEP 1: 启动 API (端口 8450) ===
[12:29:13] 代码由 runner tarball 投递，权威 sha=323cf4e1
[12:29:13] commit 对比: 运行进程=a9f4b4636316f0c3020a7596be5f25a2729e4734 / 磁盘=323cf4e14b294d7add4156b8aba802ab9c8d50bb
[12:29:13] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[12:29:13] 需要重新加载代码 -> 重启 API
[12:29:14] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[12:29:20] API 状态: OK（第 1 轮验证通过）
[12:29:20] === STEP 2: 安装 cloudflared ===
[12:29:20] cloudflared 安装路径: /usr/local/bin/cloudflared
[12:29:20] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:29:20] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[12:29:20] === STEP 3: 检查认证方式 ===
[12:29:20] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[12:29:20] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[12:29:20] 检查现有 tunnel...
[12:29:21] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 5xlax01, 3xlax08, 1xlax09, 1xlax10, 1xlax11, 1xlax13 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax01, 1xlax09, 1xsjc06                            
[12:29:21] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:29:21] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[12:29:21] 凭证文件存在
[12:29:21] 创建 config.yml...
[12:29:21] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[12:29:21] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:29:22] DNS 路由结果: 2026-10-02T04:29:22Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[12:29:22] === STEP 5: 更新 DNS (API) ===
[12:29:22] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:29:23] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[12:29:24] 设置 SSL 模式为 Full...
SSL: 跳过
[12:29:24] === STEP 6: 启动 Tunnel ===
[12:29:24] systemd 托管中 -> systemctl stop cloudflared-tunnel
[12:29:27] 启动 Named Tunnel (cert 模式)...
[12:29:27] 使用 config: /root/.cloudflared/config.yml
[12:29:27] cloudflared PID: 2070633
[12:29:30] Tunnel 连接已建立!
[12:29:30] --- cloudflared 日志 (最后 15 行) ---
2026-10-02T04:29:28Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-10-02T04:29:28Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-02T04:29:28Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-02T04:29:28Z INF Generated Connector ID: e708da8a-2f6b-4e85-8a66-27b7bf196cd8
2026-10-02T04:29:28Z INF Initial protocol quic
2026-10-02T04:29:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-02T04:29:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-02T04:29:28Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-02T04:29:28Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-02T04:29:28Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-02T04:29:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-10-02T04:29:28Z INF Registered tunnel connection connIndex=0 connection=6dabebf2-eca3-4166-a095-4ca761dd9890 event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-10-02T04:29:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.13
2026-10-02T04:29:29Z INF Registered tunnel connection connIndex=1 connection=e2405bec-7341-47d7-b55b-a4fc38125e3d event=0 ip=198.41.200.13 location=lax13 protocol=quic
2026-10-02T04:29:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.227
[12:29:30] === STEP 7: 持久化 ===
[12:29:30] 停止 nohup cloudflared (PID 2070633) -> 交由 systemd 单实例托管
[12:29:32] systemd 服务已配置
[12:29:32] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[12:29:32] === STEP 8: 验证 ===
[12:29:32] --- API (localhost:8450) ---
 OK
[12:29:32] --- cloudflared 进程 ---
root     1335051  0.1  1.1 1294932 22816 ?       Sl   Sep18  32:05 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.1 1294932 23560 ?       Ssl  Sep18  31:52 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
[12:29:32] --- aishield.tools ---
 OK
[12:29:35] --- DNS CNAME ---
[12:29:35] --- DNS A ---
104.21.81.46
172.67.188.44
[12:29:35] === 部署汇总 ===
[12:29:35] Tunnel Mode: cert
[12:29:35] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[12:29:35] API: http://localhost:8450
[12:29:35] 域名: https://aishield.tools
[12:29:35] cloudflared: /usr/local/bin/cloudflared
[12:29:35] PID: 2070633
[12:29:35] Config: /root/.cloudflared/config.yml
[12:29:35] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[12:29:35] 状态: Named Tunnel (cert 模式) 已配置
[12:29:35] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-10-02 12:29:32 CST; 14s ago
   Main PID: 2070766 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.8M
        CPU: 154ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2070766 /bin/bash /opt/start-tunnel.sh
             └─2070779 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2070323,fd=3))                                                    
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
Time: Fri Oct  2 04:29:58 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.10.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 253, "rules_breakdown": {"static": 226, "generated": 8, "radar": 19, "total": 253}, "uptime": 1790915398.8769214, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "323cf4e14b294d7add4156b8aba802ab9c8d50bb", "deployed_at": "2026-10-02T04:29:13Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
