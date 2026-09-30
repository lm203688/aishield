=== DIAGNOSTIC ===
Time: Wed Sep 30 10:40:09 AM CST 2026
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
{"status": "ok", "version": "4.10.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 235, "rules_breakdown": {"static": 208, "generated": 8, "radar": 19, "total": 235}, "uptime": 1790736009.4353173, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "509594ec8d2d3e1ce63bca39a162222462187978", "deployed_at": "2026-09-30T02:39:41Z"}OK
=== CLOUDFLARED PROCESS ===
root      129366  1.5  1.9 1294100 39148 ?       Sl   10:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  1.1 1294932 23252 ?       Sl   Sep18  27:11 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.2 1294932 24436 ?       Ssl  Sep18  26:58 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.0 1294676 20416 ?       Sl   Sep27   6:11 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-30T02:40:00Z ERR Connection terminated connIndex=2
2026-09-30T02:40:03Z INF +-------------------------------------------------------------------------------------+
2026-09-30T02:40:03Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-09-30T02:40:03Z INF +-------------------------------------------------------------------------------------+
2026-09-30T02:40:03Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-09-30T02:40:03Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-30T02:40:03Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-30T02:40:03Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-30T02:40:03Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-30T02:40:03Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-30T02:40:03Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-30T02:40:03Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-09-30T02:40:03Z INF |                                                                                     |
2026-09-30T02:40:03Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-09-30T02:40:03Z INF +-------------------------------------------------------------------------------------+
2026-09-30T02:40:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=73ce1052-c00d-4d87-a412-5639eced2a70 status=pass target=region1.v2.argotunnel.com
2026-09-30T02:40:03Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=73ce1052-c00d-4d87-a412-5639eced2a70 status=pass target=region2.v2.argotunnel.com
2026-09-30T02:40:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=73ce1052-c00d-4d87-a412-5639eced2a70 status=pass target=region1.v2.argotunnel.com
2026-09-30T02:40:03Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=73ce1052-c00d-4d87-a412-5639eced2a70 status=pass target=region2.v2.argotunnel.com
2026-09-30T02:40:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=73ce1052-c00d-4d87-a412-5639eced2a70 status=pass target=region1.v2.argotunnel.com
2026-09-30T02:40:03Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=73ce1052-c00d-4d87-a412-5639eced2a70 status=pass target=region2.v2.argotunnel.com
2026-09-30T02:40:03Z INF precheck component="Cloudflare API" details="API is reachable" run_id=73ce1052-c00d-4d87-a412-5639eced2a70 status=pass target=api.cloudflare.com:443
2026-09-30T02:40:03Z INF precheck complete hard_fail=false run_id=73ce1052-c00d-4d87-a412-5639eced2a70 suggested_protocol=quic
2026-09-30T02:40:04Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-09-30T02:40:04Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.73
2026-09-30T02:40:04Z ERR Connection terminated connIndex=3
2026-09-30T02:40:04Z ERR no more connections active and exiting
2026-09-30T02:40:04Z INF Tunnel server stopped
2026-09-30T02:40:04Z ERR icmp router terminated error="context canceled"
2026-09-30T02:40:04Z INF Metrics server stopped
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[10:39:41] Time: Wed Sep 30 10:39:41 AM CST 2026
[10:39:41] User: root (UID: 0)
[10:39:41] === STEP 1: 启动 API (端口 8450) ===
[10:39:41] 代码由 runner tarball 投递，权威 sha=509594ec
[10:39:41] commit 对比: 运行进程=53bc038b6bf68065c88885fc64b1854e34fe71c7 / 磁盘=509594ec8d2d3e1ce63bca39a162222462187978
[10:39:41] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[10:39:41] 需要重新加载代码 -> 重启 API
[10:39:43] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[10:39:49] API 状态: OK（第 1 轮验证通过）
[10:39:49] === STEP 2: 安装 cloudflared ===
[10:39:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[10:39:49] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:39:49] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[10:39:49] === STEP 3: 检查认证方式 ===
[10:39:49] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[10:39:49] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[10:39:49] 检查现有 tunnel...
[10:39:50] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 6xlax01, 1xlax05, 2xlax08, 1xlax09, 1xlax10, 1xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax01, 1xlax09, 1xsjc06, 1xsjc11                   
[10:39:50] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:39:50] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[10:39:50] 凭证文件存在
[10:39:50] 创建 config.yml...
[10:39:50] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[10:39:50] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:39:51] DNS 路由结果: 2026-09-30T02:39:51Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[10:39:51] === STEP 5: 更新 DNS (API) ===
[10:39:51] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:39:52] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[10:39:53] 设置 SSL 模式为 Full...
SSL: 跳过
[10:39:53] === STEP 6: 启动 Tunnel ===
[10:39:53] systemd 托管中 -> systemctl stop cloudflared-tunnel
[10:39:56] 启动 Named Tunnel (cert 模式)...
[10:39:56] 使用 config: /root/.cloudflared/config.yml
[10:39:56] cloudflared PID: 129236
[10:39:58] Tunnel 连接已建立!
[10:39:58] --- cloudflared 日志 (最后 15 行) ---
2026-09-30T02:39:56Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-09-30T02:39:56Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-09-30T02:39:56Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-30T02:39:56Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-30T02:39:56Z INF Generated Connector ID: b7c713af-ae35-4d52-9aa5-35a09157ba55
2026-09-30T02:39:56Z INF Initial protocol quic
2026-09-30T02:39:56Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-30T02:39:56Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-30T02:39:56Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-30T02:39:56Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-30T02:39:56Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-09-30T02:39:56Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-09-30T02:39:57Z INF Registered tunnel connection connIndex=0 connection=63fd0a5b-5375-4264-b192-b8c0fdc07ac5 event=0 ip=198.41.192.107 location=lax09 protocol=quic
2026-09-30T02:39:57Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.113
2026-09-30T02:39:58Z INF Registered tunnel connection connIndex=1 connection=5404866e-6134-4352-9b63-469547be7d3e event=0 ip=198.41.200.113 location=lax01 protocol=quic
[10:39:58] === STEP 7: 持久化 ===
[10:39:59] 停止 nohup cloudflared (PID 129236) -> 交由 systemd 单实例托管
[10:40:01] systemd 服务已配置
[10:40:01] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[10:40:01] === STEP 8: 验证 ===
[10:40:01] --- API (localhost:8450) ---
 OK
[10:40:01] --- cloudflared 进程 ---
root      129236 14.8  1.9 1294676 38780 ?       Sl   10:39   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      129366  0.0  1.3 1292484 26300 ?       Rl   10:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335051  0.1  1.1 1294932 23656 ?       Sl   Sep18  27:11 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[10:40:01] --- aishield.tools ---
 OK
[10:40:02] --- DNS CNAME ---
[10:40:03] --- DNS A ---
104.21.81.46
172.67.188.44
[10:40:03] === 部署汇总 ===
[10:40:03] Tunnel Mode: cert
[10:40:03] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[10:40:03] API: http://localhost:8450
[10:40:03] 域名: https://aishield.tools
[10:40:03] cloudflared: /usr/local/bin/cloudflared
[10:40:03] PID: 129236
[10:40:03] Config: /root/.cloudflared/config.yml
[10:40:03] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[10:40:03] 状态: Named Tunnel (cert 模式) 已配置
[10:40:03] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-09-30 10:40:01 CST; 8s ago
   Main PID: 129356 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 18.9M
        CPU: 144ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─129356 /bin/bash /opt/start-tunnel.sh
             └─129366 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=128887,fd=3))                                                     
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
Time: Wed Sep 30 02:40:17 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.10.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 235, "rules_breakdown": {"static": 208, "generated": 8, "radar": 19, "total": 235}, "uptime": 1790736017.9693663, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "509594ec8d2d3e1ce63bca39a162222462187978", "deployed_at": "2026-09-30T02:39:41Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
