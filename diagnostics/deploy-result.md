=== DIAGNOSTIC ===
Time: Tue Oct 6 11:46:22 PM CST 2026
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
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791301582.0885046, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "f0309eb836802355afed9da9cae3594440182a19", "deployed_at": "2026-10-06T15:45:40Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}OK
=== CLOUDFLARED PROCESS ===
root     1335051  0.1  1.1 1295188 22304 ?       Sl   Sep18  43:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.1 1294932 23688 ?       Ssl  Sep18  43:16 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.1 1294932 23828 ?       Sl   Sep27  22:25 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2069346  0.7  1.9 1294676 40116 ?       Sl   23:46   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-06T15:45:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-10-06T15:45:59Z INF Registered tunnel connection connIndex=0 connection=c012744b-1ebc-4e11-9b22-8d3923fed6f1 event=0 ip=198.41.192.67 location=lax09 protocol=quic
2026-10-06T15:45:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-10-06T15:46:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-10-06T15:46:01Z INF Registered tunnel connection connIndex=2 connection=def4545f-85eb-428b-a0d3-b3a71b156dae event=0 ip=198.41.200.33 location=lax13 protocol=quic
2026-10-06T15:46:01Z INF Initiating graceful shutdown due to signal terminated ...
2026-10-06T15:46:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.37
2026-10-06T15:46:01Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.192.67
2026-10-06T15:46:01Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.67
2026-10-06T15:46:01Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.67
2026-10-06T15:46:01Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.67
2026-10-06T15:46:01Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=2 event=0 ip=198.41.200.33
2026-10-06T15:46:01Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.33
2026-10-06T15:46:01Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=2 event=0 ip=198.41.200.33
2026-10-06T15:46:01Z INF Retrying connection in up to 1s connIndex=2 event=0 ip=198.41.200.33
2026-10-06T15:46:02Z INF Registered tunnel connection connIndex=3 connection=fe54c02c-de52-48e0-b113-2b9bf0815f6e event=0 ip=198.41.192.37 location=lax10 protocol=quic
2026-10-06T15:46:02Z ERR failed to run the datagram handler error="Application error 0x0 (remote)" connIndex=3 event=0 ip=198.41.192.37
2026-10-06T15:46:02Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.37
2026-10-06T15:46:02Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=3 event=0 ip=198.41.192.37
2026-10-06T15:46:02Z INF Retrying connection in up to 1s connIndex=3 event=0 ip=198.41.192.37
2026-10-06T15:46:02Z ERR Connection terminated connIndex=0
2026-10-06T15:46:02Z ERR Connection terminated connIndex=2
2026-10-06T15:46:02Z ERR Connection terminated connIndex=3
2026-10-06T15:46:04Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.193
2026-10-06T15:46:04Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.193
2026-10-06T15:46:04Z ERR Connection terminated connIndex=1
2026-10-06T15:46:04Z ERR no more connections active and exiting
2026-10-06T15:46:04Z INF Tunnel server stopped
2026-10-06T15:46:04Z INF Metrics server stopped
2026-10-06T15:46:04Z ERR icmp router terminated error="context canceled"
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[23:45:40] Time: Tue Oct  6 11:45:40 PM CST 2026
[23:45:40] User: root (UID: 0)
[23:45:40] === STEP 1: 启动 API (端口 8450) ===
[23:45:40] 代码由 runner tarball 投递，权威 sha=f0309eb8
[23:45:40] commit 对比: 运行进程=6b644de758eaaa73b6629e20e6b6d7d4cb239d64 / 磁盘=f0309eb836802355afed9da9cae3594440182a19
[23:45:40] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[23:45:41] 需要重新加载代码 -> 重启 API
[23:45:42] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[23:45:48] API 状态: OK（第 1 轮验证通过）
[23:45:48] === STEP 2: 安装 cloudflared ===
[23:45:48] cloudflared 安装路径: /usr/local/bin/cloudflared
[23:45:48] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:45:48] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[23:45:48] === STEP 3: 检查认证方式 ===
[23:45:48] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[23:45:48] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[23:45:48] 检查现有 tunnel...
[23:45:51] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 4xlax01, 2xlax07, 2xlax08, 2xlax09, 2xlax13 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                             
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 2xlax01, 1xlax09, 1xlax10                   
2026-10-06T15:45:51Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.10.0
[23:45:51] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:45:51] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[23:45:51] 凭证文件存在
[23:45:51] 创建 config.yml...
[23:45:51] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[23:45:51] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:45:52] DNS 路由结果: 2026-10-06T15:45:52Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[23:45:52] === STEP 5: 更新 DNS (API) ===
[23:45:52] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:45:54] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[23:45:55] 设置 SSL 模式为 Full...
SSL: 跳过
[23:45:56] === STEP 6: 启动 Tunnel ===
[23:45:56] systemd 托管中 -> systemctl stop cloudflared-tunnel
[23:45:59] 启动 Named Tunnel (cert 模式)...
[23:45:59] 使用 config: /root/.cloudflared/config.yml
[23:45:59] cloudflared PID: 2069222
[23:46:01] Tunnel 连接已建立!
[23:46:01] --- cloudflared 日志 (最后 15 行) ---
2026-10-06T15:45:59Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-10-06T15:45:59Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-10-06T15:45:59Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-06T15:45:59Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-06T15:45:59Z INF Generated Connector ID: de8c7e16-7a43-4ba0-ad35-000e66d61c08
2026-10-06T15:45:59Z INF Initial protocol quic
2026-10-06T15:45:59Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-06T15:45:59Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-06T15:45:59Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-06T15:45:59Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-06T15:45:59Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-06T15:45:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-10-06T15:45:59Z INF Registered tunnel connection connIndex=0 connection=c012744b-1ebc-4e11-9b22-8d3923fed6f1 event=0 ip=198.41.192.67 location=lax09 protocol=quic
2026-10-06T15:45:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-10-06T15:46:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
[23:46:01] === STEP 7: 持久化 ===
[23:46:01] 停止 nohup cloudflared (PID 2069222) -> 交由 systemd 单实例托管
[23:46:03] systemd 服务已配置
[23:46:03] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[23:46:03] === STEP 8: 验证 ===
[23:46:03] --- API (localhost:8450) ---
 OK
[23:46:03] --- cloudflared 进程 ---
root     1335051  0.1  1.1 1295188 22304 ?       Sl   Sep18  43:03 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.1 1294932 23688 ?       Ssl  Sep18  43:16 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
[23:46:03] --- aishield.tools ---
 OK
[23:46:07] --- DNS CNAME ---
[23:46:07] --- DNS A ---
104.21.81.46
172.67.188.44
[23:46:07] === 部署汇总 ===
[23:46:07] Tunnel Mode: cert
[23:46:07] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[23:46:07] API: http://localhost:8450
[23:46:07] 域名: https://aishield.tools
[23:46:07] cloudflared: /usr/local/bin/cloudflared
[23:46:07] PID: 2069222
[23:46:07] Config: /root/.cloudflared/config.yml
[23:46:07] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[23:46:07] 状态: Named Tunnel (cert 模式) 已配置
[23:46:07] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-10-06 23:46:03 CST; 18s ago
   Main PID: 2069336 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.4M
        CPU: 161ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2069336 /bin/bash /opt/start-tunnel.sh
             └─2069346 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2068847,fd=3))                                                    
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
Time: Tue Oct  6 15:46:34 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791301594.8744302, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "f0309eb836802355afed9da9cae3594440182a19", "deployed_at": "2026-10-06T15:45:40Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
