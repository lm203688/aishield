=== DIAGNOSTIC ===
Time: Mon Oct 12 06:51:21 PM CST 2026
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
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791802281.2764795, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "63186af81eaa315092ab5b4ef43aa82fa4865f39", "deployed_at": "2026-10-12T10:50:49Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}OK
=== CLOUDFLARED PROCESS ===
root     1335051  0.1  1.2 1295188 24712 ?       Sl   Sep18  56:53 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.2 1295188 25532 ?       Ssl  Sep18  57:06 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.3 1294932 26788 ?       Sl   Sep27  36:12 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     3287981  1.4  1.9 1294676 39740 ?       Sl   18:51   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-12T10:51:10Z ERR Connection terminated connIndex=1
2026-10-12T10:51:13Z INF +-------------------------------------------------------------------------------------+
2026-10-12T10:51:13Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-10-12T10:51:13Z INF +-------------------------------------------------------------------------------------+
2026-10-12T10:51:13Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-10-12T10:51:13Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-10-12T10:51:13Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-10-12T10:51:13Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-10-12T10:51:13Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-10-12T10:51:13Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-10-12T10:51:13Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-10-12T10:51:13Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-10-12T10:51:13Z INF |                                                                                     |
2026-10-12T10:51:13Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-10-12T10:51:13Z INF +-------------------------------------------------------------------------------------+
2026-10-12T10:51:13Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=1f64ccff-417a-46ae-8fed-7b2ee4fd3964 status=pass target=region1.v2.argotunnel.com
2026-10-12T10:51:13Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=1f64ccff-417a-46ae-8fed-7b2ee4fd3964 status=pass target=region2.v2.argotunnel.com
2026-10-12T10:51:13Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=1f64ccff-417a-46ae-8fed-7b2ee4fd3964 status=pass target=region1.v2.argotunnel.com
2026-10-12T10:51:13Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=1f64ccff-417a-46ae-8fed-7b2ee4fd3964 status=pass target=region2.v2.argotunnel.com
2026-10-12T10:51:13Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=1f64ccff-417a-46ae-8fed-7b2ee4fd3964 status=pass target=region1.v2.argotunnel.com
2026-10-12T10:51:13Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=1f64ccff-417a-46ae-8fed-7b2ee4fd3964 status=pass target=region2.v2.argotunnel.com
2026-10-12T10:51:13Z INF precheck component="Cloudflare API" details="API is reachable" run_id=1f64ccff-417a-46ae-8fed-7b2ee4fd3964 status=pass target=api.cloudflare.com:443
2026-10-12T10:51:13Z INF precheck complete hard_fail=false run_id=1f64ccff-417a-46ae-8fed-7b2ee4fd3964 suggested_protocol=quic
2026-10-12T10:51:14Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.193
2026-10-12T10:51:14Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.193
2026-10-12T10:51:14Z ERR Connection terminated connIndex=3
2026-10-12T10:51:14Z ERR no more connections active and exiting
2026-10-12T10:51:14Z INF Tunnel server stopped
2026-10-12T10:51:14Z INF Metrics server stopped
2026-10-12T10:51:14Z ERR icmp router terminated error="context canceled"
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[18:50:49] Time: Mon Oct 12 06:50:49 PM CST 2026
[18:50:49] User: root (UID: 0)
[18:50:49] === STEP 1: 启动 API (端口 8450) ===
[18:50:49] 代码由 runner tarball 投递，权威 sha=63186af8
[18:50:49] commit 对比: 运行进程=42094d82be5c3c72fbf49216e022757b5926bb4f / 磁盘=63186af81eaa315092ab5b4ef43aa82fa4865f39
[18:50:49] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[18:50:50] 需要重新加载代码 -> 重启 API
[18:50:52] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[18:50:58] API 状态: OK（第 1 轮验证通过）
[18:50:58] === STEP 2: 安装 cloudflared ===
[18:50:58] cloudflared 安装路径: /usr/local/bin/cloudflared
[18:50:58] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:50:58] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[18:50:58] === STEP 3: 检查认证方式 ===
[18:50:58] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[18:50:58] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[18:50:58] 检查现有 tunnel...
[18:50:59] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                                   
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax05, 1xlax10, 1xsjc01, 3xsjc06, 1xsjc07, 2xsjc10, 3xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                               
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                               
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax05, 1xsjc06, 2xsjc11                                     
[18:50:59] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:50:59] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[18:50:59] 凭证文件存在
[18:50:59] 创建 config.yml...
[18:50:59] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[18:50:59] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:51:00] DNS 路由结果: 2026-10-12T10:51:00Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[18:51:00] === STEP 5: 更新 DNS (API) ===
[18:51:00] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:51:01] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[18:51:02] 设置 SSL 模式为 Full...
SSL: 跳过
[18:51:03] === STEP 6: 启动 Tunnel ===
[18:51:03] systemd 托管中 -> systemctl stop cloudflared-tunnel
[18:51:06] 启动 Named Tunnel (cert 模式)...
[18:51:06] 使用 config: /root/.cloudflared/config.yml
[18:51:06] cloudflared PID: 3287839
[18:51:08] Tunnel 连接已建立!
[18:51:08] --- cloudflared 日志 (最后 15 行) ---
2026-10-12T10:51:06Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-12T10:51:06Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-12T10:51:06Z INF Generated Connector ID: dc6b701a-4e41-48a4-b040-9b8bd4bdcefc
2026-10-12T10:51:06Z INF Initial protocol quic
2026-10-12T10:51:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-12T10:51:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-12T10:51:06Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-12T10:51:06Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-12T10:51:06Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-12T10:51:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-10-12T10:51:07Z INF Registered tunnel connection connIndex=0 connection=97dc1dcb-7dc4-46d1-bd2b-dda341b7c23b event=0 ip=198.41.200.23 location=sjc10 protocol=quic
2026-10-12T10:51:07Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.47
2026-10-12T10:51:07Z INF Registered tunnel connection connIndex=1 connection=3741aeff-d2cb-493b-8c8e-626d11f48bc9 event=0 ip=198.41.192.47 location=sjc06 protocol=quic
2026-10-12T10:51:08Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.27
2026-10-12T10:51:08Z INF Registered tunnel connection connIndex=2 connection=d1b9b9de-c9a4-40a7-9307-c78bf75d48ff event=0 ip=198.41.192.27 location=sjc01 protocol=quic
[18:51:08] === STEP 7: 持久化 ===
[18:51:09] 停止 nohup cloudflared (PID 3287839) -> 交由 systemd 单实例托管
[18:51:11] systemd 服务已配置
[18:51:11] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[18:51:11] === STEP 8: 验证 ===
[18:51:11] --- API (localhost:8450) ---
 OK
[18:51:11] --- cloudflared 进程 ---
root     1335051  0.1  1.2 1295188 24712 ?       Sl   Sep18  56:53 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.2 1295188 25532 ?       Ssl  Sep18  57:06 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
[18:51:11] --- aishield.tools ---
 OK
[18:51:13] --- DNS CNAME ---
[18:51:13] --- DNS A ---
172.67.188.44
104.21.81.46
[18:51:13] === 部署汇总 ===
[18:51:13] Tunnel Mode: cert
[18:51:13] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[18:51:13] API: http://localhost:8450
[18:51:13] 域名: https://aishield.tools
[18:51:13] cloudflared: /usr/local/bin/cloudflared
[18:51:13] PID: 3287839
[18:51:13] Config: /root/.cloudflared/config.yml
[18:51:13] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[18:51:13] 状态: Named Tunnel (cert 模式) 已配置
[18:51:13] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-10-12 18:51:11 CST; 10s ago
   Main PID: 3287975 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 17.9M
        CPU: 154ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─3287975 /bin/bash /opt/start-tunnel.sh
             └─3287981 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3287477,fd=3))                                                    
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
Time: Mon Oct 12 10:51:30 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1791802291.2537165, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "63186af81eaa315092ab5b4ef43aa82fa4865f39", "deployed_at": "2026-10-12T10:50:49Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
