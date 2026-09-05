=== DIAGNOSTIC ===
Time: Sat Sep 5 05:40:29 PM CST 2026
=== USER ===
root
=== GIT LOG ===
4c18b94b chore(ci-state): 更新 CI 状态总线
2775ad03 auto: 威胁情报入库 + 检测规则更新 + README计数同步（情报 315 条 / 规则 85 条）[skip ci]
c5554455 auto: 批量扫描入库 [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788601229.2783308, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "4c18b94bcb180aec29357e6a18cfc15bb4a956cc", "deployed_at": "2026-09-05T09:39:48Z"}OK
=== CLOUDFLARED PROCESS ===
root     1988751  0.6  1.8 1294676 36656 ?       Sl   17:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1988779  1.0  1.8 1294420 36936 ?       Ssl  17:40   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1988969  1.7  1.8 1294668 37216 ?       Sl   17:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-05T09:40:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-09-05T09:40:17Z INF +-------------------------------------------------------------------------------------+
2026-09-05T09:40:17Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-09-05T09:40:17Z INF +-------------------------------------------------------------------------------------+
2026-09-05T09:40:17Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-09-05T09:40:17Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-05T09:40:17Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-05T09:40:17Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-05T09:40:17Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-05T09:40:17Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-05T09:40:17Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-05T09:40:17Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-09-05T09:40:17Z INF |                                                                                     |
2026-09-05T09:40:17Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-09-05T09:40:17Z INF +-------------------------------------------------------------------------------------+
2026-09-05T09:40:17Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region1.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region2.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region1.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region2.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region1.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region2.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=api.cloudflare.com:443
2026-09-05T09:40:17Z INF precheck complete hard_fail=false run_id=f617b7db-7f64-42d9-a9cf-b58010022060 suggested_protocol=quic
2026-09-05T09:40:17Z INF Registered tunnel connection connIndex=0 connection=6f9536b3-f315-45df-9fc6-a9f0b45b9712 event=0 ip=198.41.192.27 location=lax07 protocol=quic
2026-09-05T09:40:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-09-05T09:40:18Z INF Registered tunnel connection connIndex=1 connection=082c0c2d-ef8f-42c7-abe8-70cb26c10dcd event=0 ip=198.41.200.63 location=sjc10 protocol=quic
2026-09-05T09:40:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-09-05T09:40:19Z INF Registered tunnel connection connIndex=2 connection=a91d0121-d7c9-49c2-8682-9992cc0d5876 event=0 ip=198.41.200.113 location=sjc10 protocol=quic
2026-09-05T09:40:19Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.107
2026-09-05T09:40:20Z INF Registered tunnel connection connIndex=3 connection=1df130ca-de88-4aef-8318-2e15bfad5c61 event=0 ip=198.41.192.107 location=lax07 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[17:39:47] Time: Sat Sep  5 05:39:47 PM CST 2026
[17:39:47] User: root (UID: 0)
[17:39:47] === STEP 1: 启动 API (端口 8450) ===
[17:39:48] HEAD: 4c18b94b -> 4c18b94b
[17:39:48] commit 对比: 运行进程=93fcd10c5a07cf882e7bfbb7a3ee6da122e3a19c / 磁盘=4c18b94bcb180aec29357e6a18cfc15bb4a956cc
[17:39:48] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[17:39:48] 需要重新加载代码 -> 重启 API
[17:39:48] 强制重启 Python API 进程（当前commit=93fcd10c5a07cf882e7bfbb7a3ee6da122e3a19c 目标=4c18b94bcb180aec29357e6a18cfc15bb4a956cc）
[17:39:58] API 状态: OK
[17:39:58] === STEP 2: 安装 cloudflared ===
[17:39:58] cloudflared 安装路径: /usr/local/bin/cloudflared
[17:39:59] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:39:59] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[17:39:59] === STEP 3: 检查认证方式 ===
[17:39:59] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[17:39:59] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[17:39:59] 检查现有 tunnel...
[17:40:00] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax05, 1xlax08, 1xsjc07, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                    
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax08, 1xlax10, 1xsjc07, 1xsjc08 
[17:40:00] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:40:00] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[17:40:00] 凭证文件存在
[17:40:00] 创建 config.yml...
[17:40:00] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[17:40:00] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:40:01] DNS 路由结果: 2026-09-05T09:40:01Z INF Added CNAME aishield.tools.healthlens.cc which will route to this tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[17:40:01] === STEP 5: 更新 DNS (API) ===
[17:40:01] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:40:05] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[17:40:07] 设置 SSL 模式为 Full...
SSL: 跳过
[17:40:07] === STEP 6: 启动 Tunnel ===
[17:40:10] 启动 Named Tunnel (cert 模式)...
[17:40:10] 使用 config: /root/.cloudflared/config.yml
[17:40:10] cloudflared PID: 1988751
[17:40:18] Tunnel 连接已建立!
[17:40:18] --- cloudflared 日志 (最后 15 行) ---
2026-09-05T09:40:17Z INF |                                                                                     |
2026-09-05T09:40:17Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-09-05T09:40:17Z INF +-------------------------------------------------------------------------------------+
2026-09-05T09:40:17Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region1.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region2.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region1.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region2.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region1.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=region2.v2.argotunnel.com
2026-09-05T09:40:17Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f617b7db-7f64-42d9-a9cf-b58010022060 status=pass target=api.cloudflare.com:443
2026-09-05T09:40:17Z INF precheck complete hard_fail=false run_id=f617b7db-7f64-42d9-a9cf-b58010022060 suggested_protocol=quic
2026-09-05T09:40:17Z INF Registered tunnel connection connIndex=0 connection=6f9536b3-f315-45df-9fc6-a9f0b45b9712 event=0 ip=198.41.192.27 location=lax07 protocol=quic
2026-09-05T09:40:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.63
2026-09-05T09:40:18Z INF Registered tunnel connection connIndex=1 connection=082c0c2d-ef8f-42c7-abe8-70cb26c10dcd event=0 ip=198.41.200.63 location=sjc10 protocol=quic
2026-09-05T09:40:18Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
[17:40:18] === STEP 7: 持久化 ===
[17:40:21] systemd 服务已配置
[17:40:21] Cron 保活已设置
[17:40:21] === STEP 8: 验证 ===
[17:40:21] --- API (localhost:8450) ---
 OK
[17:40:21] --- cloudflared 进程 ---
root     1988751  0.9  1.9 1294676 39756 ?       Sl   17:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1988779  1.5  1.9 1294092 39368 ?       Ssl  17:40   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     1988969  0.0  1.3 1292484 27440 ?       Rl   17:40   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[17:40:21] --- aishield.tools ---
 OK
[17:40:22] --- DNS CNAME ---
[17:40:23] --- DNS A ---
172.67.188.44
104.21.81.46
[17:40:23] === 部署汇总 ===
[17:40:23] Tunnel Mode: cert
[17:40:23] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[17:40:23] API: http://localhost:8450
[17:40:23] 域名: https://aishield.tools
[17:40:23] cloudflared: /usr/local/bin/cloudflared
[17:40:23] PID: 1988751
[17:40:23] Config: /root/.cloudflared/config.yml
[17:40:23] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[17:40:23] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2026-09-05 17:40:21 CST; 8s ago
   Main PID: 1988965 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 19.1M
        CPU: 154ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1988965 /bin/bash /opt/start-tunnel.sh
             └─1988969 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=1988254,fd=3))                                                    
=== CRONTAB ===
*/5 * * * * flock -xn /tmp/stargate.lock -c '/usr/local/qcloud/stargate/admin/start.sh > /dev/null 2>&1 &'
* * * * * pgrep -f 'cloudflared tunnel' > /dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1
=== START SCRIPT ===
#!/bin/bash
# AIShield Tunnel 启动脚本
CF_BIN='/usr/local/bin/cloudflared'
CONFIG_FILE='/root/.cloudflared/config.yml'
TOKEN_FILE='/root/.cloudflared/tunnel-token'

cleanup() { kill $CF_PID 2>/dev/null; exit 0; }
trap cleanup SIGTERM SIGINT

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
Time: Sat Sep  5 09:40:37 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788601238.2455547, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "4c18b94bcb180aec29357e6a18cfc15bb4a956cc", "deployed_at": "2026-09-05T09:39:48Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
