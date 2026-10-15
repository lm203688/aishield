=== DIAGNOSTIC ===
Time: Fri Oct 16 01:28:56 AM CST 2026
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
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1792085336.3928463, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "25cabc25f17cb45d2cebd592ba5f14a215736199", "deployed_at": "2026-10-15T17:28:26Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}OK
=== CLOUDFLARED PROCESS ===
root     1335051  0.1  0.9 1295188 18700 ?       Sl   Sep18  64:41 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.0 1295188 21132 ?       Ssl  Sep18  64:56 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
root     1770899  0.1  1.2 1294932 24584 ?       Sl   Sep27  44:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2160984  1.7  1.9 1294420 39628 ?       Sl   01:28   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-10-15T17:28:47Z ERR Connection terminated connIndex=1
2026-10-15T17:28:50Z INF +-------------------------------------------------------------------------------------+
2026-10-15T17:28:50Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-10-15T17:28:50Z INF +-------------------------------------------------------------------------------------+
2026-10-15T17:28:50Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-10-15T17:28:50Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-10-15T17:28:50Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-10-15T17:28:50Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-10-15T17:28:50Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-10-15T17:28:50Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-10-15T17:28:50Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-10-15T17:28:50Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-10-15T17:28:50Z INF |                                                                                     |
2026-10-15T17:28:50Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-10-15T17:28:50Z INF +-------------------------------------------------------------------------------------+
2026-10-15T17:28:50Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=fe03af4e-81d4-4bac-ba7a-db49c5dab795 status=pass target=region1.v2.argotunnel.com
2026-10-15T17:28:50Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=fe03af4e-81d4-4bac-ba7a-db49c5dab795 status=pass target=region2.v2.argotunnel.com
2026-10-15T17:28:50Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=fe03af4e-81d4-4bac-ba7a-db49c5dab795 status=pass target=region1.v2.argotunnel.com
2026-10-15T17:28:50Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=fe03af4e-81d4-4bac-ba7a-db49c5dab795 status=pass target=region2.v2.argotunnel.com
2026-10-15T17:28:50Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=fe03af4e-81d4-4bac-ba7a-db49c5dab795 status=pass target=region1.v2.argotunnel.com
2026-10-15T17:28:50Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=fe03af4e-81d4-4bac-ba7a-db49c5dab795 status=pass target=region2.v2.argotunnel.com
2026-10-15T17:28:50Z INF precheck component="Cloudflare API" details="API is reachable" run_id=fe03af4e-81d4-4bac-ba7a-db49c5dab795 status=pass target=api.cloudflare.com:443
2026-10-15T17:28:50Z INF precheck complete hard_fail=false run_id=fe03af4e-81d4-4bac-ba7a-db49c5dab795 suggested_protocol=quic
2026-10-15T17:28:51Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=3 event=0 ip=198.41.200.73
2026-10-15T17:28:51Z INF Retrying connection in up to 2s connIndex=3 event=0 ip=198.41.200.73
2026-10-15T17:28:51Z ERR Connection terminated connIndex=3
2026-10-15T17:28:51Z ERR no more connections active and exiting
2026-10-15T17:28:51Z INF Tunnel server stopped
2026-10-15T17:28:51Z INF Metrics server stopped
2026-10-15T17:28:51Z ERR icmp router terminated error="context canceled"
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[01:28:26] Time: Fri Oct 16 01:28:26 AM CST 2026
[01:28:26] User: root (UID: 0)
[01:28:26] === STEP 1: 启动 API (端口 8450) ===
[01:28:26] 代码由 runner tarball 投递，权威 sha=25cabc25
[01:28:26] commit 对比: 运行进程=06a95d49467d4de9cd064d0f27dbd28af8be1bc2 / 磁盘=25cabc25f17cb45d2cebd592ba5f14a215736199
[01:28:26] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[01:28:28] 需要重新加载代码 -> 重启 API
[01:28:29] systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=/opt/aishield）
[01:28:35] API 状态: OK（第 1 轮验证通过）
[01:28:35] === STEP 2: 安装 cloudflared ===
[01:28:35] cloudflared 安装路径: /usr/local/bin/cloudflared
[01:28:35] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[01:28:35] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[01:28:35] === STEP 3: 检查认证方式 ===
[01:28:35] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[01:28:35] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[01:28:35] 检查现有 tunnel...
[01:28:36] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                                            
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax01, 1xlax07, 2xlax08, 2xlax09, 1xlax10, 3xlax13, 1xsjc07, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                                        
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                                        
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax01, 1xlax07, 1xlax08, 1xlax13                                     
[01:28:36] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:28:36] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[01:28:36] 凭证文件存在
[01:28:36] 创建 config.yml...
[01:28:36] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[01:28:36] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:28:38] DNS 路由结果: 2026-10-15T17:28:38Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[01:28:38] === STEP 5: 更新 DNS (API) ===
[01:28:38] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:28:39] 创建新 DNS CNAME 记录...
DNS 创建失败: [{"code": 9106, "message": "Missing X-Auth-Key, X-Auth-Email or Authorization headers"}]
[01:28:39] 设置 SSL 模式为 Full...
SSL: 跳过
[01:28:40] === STEP 6: 启动 Tunnel ===
[01:28:40] systemd 托管中 -> systemctl stop cloudflared-tunnel
[01:28:43] 启动 Named Tunnel (cert 模式)...
[01:28:43] 使用 config: /root/.cloudflared/config.yml
[01:28:43] cloudflared PID: 2160805
[01:28:45] Tunnel 连接已建立!
[01:28:45] --- cloudflared 日志 (最后 15 行) ---
2026-10-15T17:28:43Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-10-15T17:28:43Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-10-15T17:28:43Z INF cloudflared will not automatically update if installed by a package manager.
2026-10-15T17:28:43Z INF Generated Connector ID: acf72f37-917e-431b-a09a-e9e5865f36ea
2026-10-15T17:28:43Z INF Initial protocol quic
2026-10-15T17:28:43Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-15T17:28:43Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-15T17:28:43Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-10-15T17:28:43Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-10-15T17:28:43Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-10-15T17:28:43Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.233
2026-10-15T17:28:44Z INF Registered tunnel connection connIndex=0 connection=0618db1e-2396-466f-8bcc-3aab61bed61b event=0 ip=198.41.200.233 location=lax13 protocol=quic
2026-10-15T17:28:44Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-10-15T17:28:44Z INF Registered tunnel connection connIndex=1 connection=6c363042-4147-4a12-babf-8dcac43e6e18 event=0 ip=198.41.192.107 location=lax10 protocol=quic
2026-10-15T17:28:45Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.47
[01:28:45] === STEP 7: 持久化 ===
[01:28:46] 停止 nohup cloudflared (PID 2160805) -> 交由 systemd 单实例托管
[01:28:48] systemd 服务已配置
[01:28:48] Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）
[01:28:48] === STEP 8: 验证 ===
[01:28:48] --- API (localhost:8450) ---
 OK
[01:28:48] --- cloudflared 进程 ---
root     1335051  0.1  0.9 1295188 19052 ?       Sl   Sep18  64:41 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1335162  0.1  1.0 1295188 21412 ?       Ssl  Sep18  64:56 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1770833  0.0  0.0   2892   916 ?        Ss   Sep27   0:00 /bin/sh -c curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
[01:28:48] --- aishield.tools ---
 OK
[01:28:49] --- DNS CNAME ---
[01:28:50] --- DNS A ---
172.67.188.44
104.21.81.46
[01:28:50] === 部署汇总 ===
[01:28:50] Tunnel Mode: cert
[01:28:50] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[01:28:50] API: http://localhost:8450
[01:28:50] 域名: https://aishield.tools
[01:28:50] cloudflared: /usr/local/bin/cloudflared
[01:28:50] PID: 2160805
[01:28:50] Config: /root/.cloudflared/config.yml
[01:28:50] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[01:28:50] 状态: Named Tunnel (cert 模式) 已配置
[01:28:50] EXIT 0: API 健康
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2026-10-16 01:28:48 CST; 8s ago
   Main PID: 2160979 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 18.3M
        CPU: 151ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2160979 /bin/bash /opt/start-tunnel.sh
             └─2160984 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2160510,fd=3))                                                    
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
Time: Thu Oct 15 17:29:05 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.11.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 264, "rules_breakdown": {"static": 237, "generated": 8, "radar": 19, "total": 264}, "uptime": 1792085346.7467759, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "25cabc25f17cb45d2cebd592ba5f14a215736199", "deployed_at": "2026-10-15T17:28:26Z", "signing_backend": "ed25519", "identity_ready": true, "identity_reason": null}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
