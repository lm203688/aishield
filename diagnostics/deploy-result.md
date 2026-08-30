=== DIAGNOSTIC ===
Time: Sun Aug 30 08:24:03 AM CST 2026
=== USER ===
root
=== GIT LOG ===
95c91227 fix(ci): 清掉注释里的空表达式标记 + E8 增加空表达式拦截
3758f68e auto: 部署验证状态回写 [skip ci]
93107ff1 chore: update deploy diagnostics [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788049443.816259, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "95c91227797dcfdd5c1987d8f078e698b7ebb512", "deployed_at": "2026-08-29T05:03:39Z"}OK
=== CLOUDFLARED PROCESS ===
root      215807  1.1  1.9 1294676 39472 ?       Sl   08:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      215947  1.5  1.9 1359708 38608 ?       Sl   08:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-30T00:23:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-30T00:23:52Z INF Registered tunnel connection connIndex=0 connection=07fc2052-0d9a-4108-b3f0-411c2faebcbc event=0 ip=198.41.192.67 location=lax07 protocol=quic
2026-08-30T00:23:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-30T00:23:53Z INF Registered tunnel connection connIndex=1 connection=206a6477-4887-4408-b718-4ae33f5a2696 event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-30T00:23:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-30T00:23:54Z INF Registered tunnel connection connIndex=2 connection=909f405f-f930-4d7c-8557-80e64431c5c1 event=0 ip=198.41.200.33 location=sjc08 protocol=quic
2026-08-30T00:23:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-30T00:23:55Z INF Registered tunnel connection connIndex=3 connection=cf47852c-fea1-417a-bb90-8143c8a41859 event=0 ip=198.41.192.47 location=lax12 protocol=quic
2026-08-30T00:23:59Z INF +-------------------------------------------------------------------------------------+
2026-08-30T00:23:59Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-30T00:23:59Z INF +-------------------------------------------------------------------------------------+
2026-08-30T00:23:59Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-30T00:23:59Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-30T00:23:59Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-30T00:23:59Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-30T00:23:59Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-30T00:23:59Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-30T00:23:59Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-30T00:23:59Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-30T00:23:59Z INF |                                                                                     |
2026-08-30T00:23:59Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-30T00:23:59Z INF +-------------------------------------------------------------------------------------+
2026-08-30T00:23:59Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e1c3a406-bd32-4ac5-925b-f003259ce8a8 status=pass target=region1.v2.argotunnel.com
2026-08-30T00:23:59Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e1c3a406-bd32-4ac5-925b-f003259ce8a8 status=pass target=region2.v2.argotunnel.com
2026-08-30T00:23:59Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e1c3a406-bd32-4ac5-925b-f003259ce8a8 status=pass target=region1.v2.argotunnel.com
2026-08-30T00:23:59Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e1c3a406-bd32-4ac5-925b-f003259ce8a8 status=pass target=region2.v2.argotunnel.com
2026-08-30T00:23:59Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e1c3a406-bd32-4ac5-925b-f003259ce8a8 status=pass target=region1.v2.argotunnel.com
2026-08-30T00:23:59Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e1c3a406-bd32-4ac5-925b-f003259ce8a8 status=pass target=region2.v2.argotunnel.com
2026-08-30T00:23:59Z INF precheck component="Cloudflare API" details="API is reachable" run_id=e1c3a406-bd32-4ac5-925b-f003259ce8a8 status=pass target=api.cloudflare.com:443
2026-08-30T00:23:59Z INF precheck complete hard_fail=false run_id=e1c3a406-bd32-4ac5-925b-f003259ce8a8 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:22:14] Time: Sun Aug 30 08:22:14 AM CST 2026
[08:22:14] User: root (UID: 0)
[08:22:14] === STEP 1: 启动 API (端口 8450) ===
[08:23:45] HEAD: 95c91227 -> 95c91227
[08:23:45] commit 对比: 运行进程=95c91227797dcfdd5c1987d8f078e698b7ebb512 / 磁盘=95c91227797dcfdd5c1987d8f078e698b7ebb512
[08:23:45] 代码已是最新且 API 健康 -> 跳过重启
[08:23:45] API 状态: OK
[08:23:45] === STEP 2: 安装 cloudflared ===
[08:23:45] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:23:45] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:23:45] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:23:45] === STEP 3: 检查认证方式 ===
[08:23:45] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:23:45] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:23:45] 检查现有 tunnel...
[08:23:46] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax07, 1xlax08, 2xlax11, 4xsjc07 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[08:23:46] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:23:46] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:23:46] 凭证文件存在
[08:23:46] 创建 config.yml...
[08:23:46] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:23:46] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:23:47] DNS 路由结果: 2026-08-30T00:23:47Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:23:47] === STEP 5: 更新 DNS (API) ===
[08:23:47] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:23:48] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:23:48] 设置 SSL 模式为 Full...
SSL: 跳过
[08:23:49] === STEP 6: 启动 Tunnel ===
[08:23:52] 启动 Named Tunnel (cert 模式)...
[08:23:52] 使用 config: /root/.cloudflared/config.yml
[08:23:52] cloudflared PID: 215807
[08:23:54] Tunnel 连接已建立!
[08:23:54] --- cloudflared 日志 (最后 15 行) ---
2026-08-30T00:23:52Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-30T00:23:52Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-30T00:23:52Z INF Generated Connector ID: f1e4c85c-ff21-412c-91ef-c7b8c42531c9
2026-08-30T00:23:52Z INF Initial protocol quic
2026-08-30T00:23:52Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:23:52Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:23:52Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:23:52Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:23:52Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-30T00:23:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.67
2026-08-30T00:23:52Z INF Registered tunnel connection connIndex=0 connection=07fc2052-0d9a-4108-b3f0-411c2faebcbc event=0 ip=198.41.192.67 location=lax07 protocol=quic
2026-08-30T00:23:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-30T00:23:53Z INF Registered tunnel connection connIndex=1 connection=206a6477-4887-4408-b718-4ae33f5a2696 event=0 ip=198.41.200.233 location=sjc07 protocol=quic
2026-08-30T00:23:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.33
2026-08-30T00:23:54Z INF Registered tunnel connection connIndex=2 connection=909f405f-f930-4d7c-8557-80e64431c5c1 event=0 ip=198.41.200.33 location=sjc08 protocol=quic
[08:23:54] === STEP 7: 持久化 ===
[08:23:55] systemd 服务已配置
[08:23:55] Cron 保活已设置
[08:23:55] === STEP 8: 验证 ===
[08:23:55] --- API (localhost:8450) ---
 OK
[08:23:55] --- cloudflared 进程 ---
root      215807  3.3  1.9 1294420 39516 ?       Sl   08:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      215947  0.0  1.0 1357836 21564 ?       Rl   08:23   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:23:55] --- aishield.tools ---
 OK
[08:23:56] --- DNS CNAME ---
[08:23:56] --- DNS A ---
104.21.81.46
172.67.188.44
[08:23:56] === 部署汇总 ===
[08:23:56] Tunnel Mode: cert
[08:23:56] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:23:56] API: http://localhost:8450
[08:23:56] 域名: https://aishield.tools
[08:23:56] cloudflared: /usr/local/bin/cloudflared
[08:23:56] PID: 215807
[08:23:56] Config: /root/.cloudflared/config.yml
[08:23:56] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:23:56] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-30 08:23:55 CST; 8s ago
   Main PID: 215939 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.1M
        CPU: 138ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─215939 /bin/bash /opt/start-tunnel.sh
             └─215947 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=3654022,fd=3))                                                    
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
Time: Sun Aug 30 00:24:11 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788049451.856831, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "95c91227797dcfdd5c1987d8f078e698b7ebb512", "deployed_at": "2026-08-29T05:03:39Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
