=== DIAGNOSTIC ===
Time: Sun Aug 30 08:36:32 AM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788050192.2680514, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "95c91227797dcfdd5c1987d8f078e698b7ebb512", "deployed_at": "2026-08-29T05:03:39Z"}OK
=== CLOUDFLARED PROCESS ===
root      226074  1.0  1.9 1294676 39160 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      226206  1.3  1.9 1293836 40212 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-30T00:36:23Z INF Registered tunnel connection connIndex=2 connection=dbb4c624-2621-438b-a952-9e441390b7d3 event=0 ip=198.41.200.43 location=sjc10 protocol=quic
2026-08-30T00:36:23Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.7
2026-08-30T00:36:24Z INF Registered tunnel connection connIndex=3 connection=98684ca7-f0a1-465e-bbdc-bdd213968748 event=0 ip=198.41.192.7 location=lax07 protocol=quic
2026-08-30T00:36:26Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.73
2026-08-30T00:36:26Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.73
2026-08-30T00:36:26Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-30T00:36:27Z INF +-------------------------------------------------------------------------------------+
2026-08-30T00:36:27Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-30T00:36:27Z INF +-------------------------------------------------------------------------------------+
2026-08-30T00:36:27Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-30T00:36:27Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-30T00:36:27Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-30T00:36:27Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-30T00:36:27Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-30T00:36:27Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-30T00:36:27Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-30T00:36:27Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-30T00:36:27Z INF |                                                                                     |
2026-08-30T00:36:27Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-30T00:36:27Z INF +-------------------------------------------------------------------------------------+
2026-08-30T00:36:27Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8e835bae-8bbe-4bfe-a7d5-652b8bde34a7 status=pass target=region1.v2.argotunnel.com
2026-08-30T00:36:27Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=8e835bae-8bbe-4bfe-a7d5-652b8bde34a7 status=pass target=region2.v2.argotunnel.com
2026-08-30T00:36:27Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8e835bae-8bbe-4bfe-a7d5-652b8bde34a7 status=pass target=region1.v2.argotunnel.com
2026-08-30T00:36:27Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=8e835bae-8bbe-4bfe-a7d5-652b8bde34a7 status=pass target=region2.v2.argotunnel.com
2026-08-30T00:36:27Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8e835bae-8bbe-4bfe-a7d5-652b8bde34a7 status=pass target=region1.v2.argotunnel.com
2026-08-30T00:36:27Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=8e835bae-8bbe-4bfe-a7d5-652b8bde34a7 status=pass target=region2.v2.argotunnel.com
2026-08-30T00:36:27Z INF precheck component="Cloudflare API" details="API is reachable" run_id=8e835bae-8bbe-4bfe-a7d5-652b8bde34a7 status=pass target=api.cloudflare.com:443
2026-08-30T00:36:27Z INF precheck complete hard_fail=false run_id=8e835bae-8bbe-4bfe-a7d5-652b8bde34a7 suggested_protocol=quic
2026-08-30T00:36:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.233
2026-08-30T00:36:29Z INF Registered tunnel connection connIndex=1 connection=3f96f7e9-a781-4d57-9753-b2641326c84e event=0 ip=198.41.200.233 location=sjc10 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:34:30] Time: Sun Aug 30 08:34:30 AM CST 2026
[08:34:30] User: root (UID: 0)
[08:34:30] === STEP 1: 启动 API (端口 8450) ===
[08:36:07] HEAD: 95c91227 -> 95c91227
[08:36:07] commit 对比: 运行进程=95c91227797dcfdd5c1987d8f078e698b7ebb512 / 磁盘=95c91227797dcfdd5c1987d8f078e698b7ebb512
[08:36:07] 代码已是最新且 API 健康 -> 跳过重启
[08:36:07] API 状态: OK
[08:36:07] === STEP 2: 安装 cloudflared ===
[08:36:07] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:36:07] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:08] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:08] === STEP 3: 检查认证方式 ===
[08:36:08] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:36:08] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:36:08] 检查现有 tunnel...
[08:36:08] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax07, 3xlax09, 2xsjc08, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                             
2026-08-30T00:36:08Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:36:08] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:08] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:36:08] 凭证文件存在
[08:36:08] 创建 config.yml...
[08:36:08] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:36:08] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:11] DNS 路由结果: 2026-08-30T00:36:11Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:11] === STEP 5: 更新 DNS (API) ===
[08:36:11] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:11] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:36:12] 设置 SSL 模式为 Full...
SSL: 跳过
[08:36:13] === STEP 6: 启动 Tunnel ===
[08:36:14] HEAD: 95c91227 -> 95c91227
[08:36:14] commit 对比: 运行进程=95c91227797dcfdd5c1987d8f078e698b7ebb512 / 磁盘=95c91227797dcfdd5c1987d8f078e698b7ebb512
[08:36:14] 代码已是最新且 API 健康 -> 跳过重启
[08:36:14] API 状态: OK
[08:36:14] === STEP 2: 安装 cloudflared ===
[08:36:14] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:36:14] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:14] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:36:14] === STEP 3: 检查认证方式 ===
[08:36:14] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:36:14] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:36:14] 检查现有 tunnel...
[08:36:15] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z             
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[08:36:15] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:15] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:36:15] 凭证文件存在
[08:36:15] 创建 config.yml...
[08:36:15] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:36:15] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:16] 启动 Named Tunnel (cert 模式)...
[08:36:16] 使用 config: /root/.cloudflared/config.yml
[08:36:16] cloudflared PID: 225776
[08:36:16] DNS 路由结果: 2026-08-30T00:36:16Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:16] === STEP 5: 更新 DNS (API) ===
[08:36:16] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:17] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:36:17] 设置 SSL 模式为 Full...
[08:36:18] Tunnel 连接已建立!
[08:36:18] --- cloudflared 日志 (最后 15 行) ---
2026-08-30T00:36:16Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-30T00:36:16Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-30T00:36:16Z INF Generated Connector ID: 7684f659-9e4b-4060-a4a8-c2903f9316ce
2026-08-30T00:36:16Z INF Initial protocol quic
2026-08-30T00:36:16Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:36:16Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:36:16Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:36:16Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:36:16Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-30T00:36:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-08-30T00:36:16Z INF Registered tunnel connection connIndex=0 connection=54dd6a93-d0eb-40f3-a206-e3685b8cd9b2 event=0 ip=198.41.192.37 location=lax12 protocol=quic
2026-08-30T00:36:16Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-08-30T00:36:17Z INF Registered tunnel connection connIndex=1 connection=2147f822-eb45-4073-8b6a-7603d1e267db event=0 ip=198.41.200.33 location=sjc05 protocol=quic
2026-08-30T00:36:17Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-08-30T00:36:17Z INF Registered tunnel connection connIndex=2 connection=ccc516f3-b124-47da-abb6-7a2ce7b58813 event=0 ip=198.41.200.43 location=sjc07 protocol=quic
[08:36:18] === STEP 7: 持久化 ===
SSL: 跳过
[08:36:18] === STEP 6: 启动 Tunnel ===
[08:36:18] systemd 服务已配置
[08:36:18] Cron 保活已设置
[08:36:18] === STEP 8: 验证 ===
[08:36:18] --- API (localhost:8450) ---
 OK
[08:36:18] --- cloudflared 进程 ---
root      225776  4.5  1.9 1293844 38372 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      225913  0.0  1.3 1292740 27544 ?       Rl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:36:18] --- aishield.tools ---
 FAIL (DNS 传播中或配置错误)
[08:36:19] --- DNS CNAME ---
[08:36:19] --- DNS A ---
172.67.188.44
104.21.81.46
[08:36:19] === 部署汇总 ===
[08:36:19] Tunnel Mode: cert
[08:36:19] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:19] API: http://localhost:8450
[08:36:19] 域名: https://aishield.tools
[08:36:19] cloudflared: /usr/local/bin/cloudflared
[08:36:19] PID: 225776
[08:36:19] Config: /root/.cloudflared/config.yml
[08:36:19] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:19] 状态: Named Tunnel (cert 模式) 已配置
[08:36:21] 启动 Named Tunnel (cert 模式)...
[08:36:21] 使用 config: /root/.cloudflared/config.yml
[08:36:21] cloudflared PID: 226074
[08:36:23] Tunnel 连接已建立!
[08:36:23] --- cloudflared 日志 (最后 15 行) ---
2026-08-30T00:36:21Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-30T00:36:21Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-30T00:36:21Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-30T00:36:21Z INF Generated Connector ID: 9c9b53be-0f5f-43e6-82e2-630573e10e6c
2026-08-30T00:36:21Z INF Initial protocol quic
2026-08-30T00:36:21Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:36:21Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:36:21Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:36:21Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:36:21Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-30T00:36:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.107
2026-08-30T00:36:21Z INF Registered tunnel connection connIndex=0 connection=c137d562-9cd5-426d-9548-dcd179be96d8 event=0 ip=198.41.192.107 location=lax12 protocol=quic
2026-08-30T00:36:21Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
2026-08-30T00:36:22Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-08-30T00:36:23Z INF Registered tunnel connection connIndex=2 connection=dbb4c624-2621-438b-a952-9e441390b7d3 event=0 ip=198.41.200.43 location=sjc10 protocol=quic
[08:36:23] === STEP 7: 持久化 ===
[08:36:24] systemd 服务已配置
[08:36:24] Cron 保活已设置
[08:36:24] === STEP 8: 验证 ===
[08:36:24] --- API (localhost:8450) ---
 OK
[08:36:24] --- cloudflared 进程 ---
root      226074  3.3  1.9 1294420 38692 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      226206  0.0  1.6 1293068 33512 ?       Sl   08:36   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:36:24] --- aishield.tools ---
 OK
[08:36:25] --- DNS CNAME ---
[08:36:25] --- DNS A ---
104.21.81.46
172.67.188.44
[08:36:25] === 部署汇总 ===
[08:36:25] Tunnel Mode: cert
[08:36:25] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:36:25] API: http://localhost:8450
[08:36:25] 域名: https://aishield.tools
[08:36:25] cloudflared: /usr/local/bin/cloudflared
[08:36:25] PID: 226074
[08:36:25] Config: /root/.cloudflared/config.yml
[08:36:25] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:36:25] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-30 08:36:24 CST; 8s ago
   Main PID: 226205 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 17.8M
        CPU: 126ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─226205 /bin/bash /opt/start-tunnel.sh
             └─226206 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Sun Aug 30 00:36:39 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788050199.9828022, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "95c91227797dcfdd5c1987d8f078e698b7ebb512", "deployed_at": "2026-08-29T05:03:39Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
