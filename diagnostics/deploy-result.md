=== DIAGNOSTIC ===
Time: Sun Aug 30 07:57:46 PM CST 2026
=== USER ===
root
=== GIT LOG ===
b8a7f720 chore(meta): 体系体检 score=83 level=degraded
a0eae3aa fix(deploy): 磁盘状态改用 artifact 跨 job 传递，修掉验证门读旧数据的缺陷
b7a69aae auto: 部署验证状态回写 [skip ci]
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788091066.3415163, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "b8a7f720b8b2cd4f089e579d30840006d40b2d94", "deployed_at": "2026-08-30T00:37:59Z"}OK
=== CLOUDFLARED PROCESS ===
root      260027  0.1  1.6 1294676 34000 ?       Sl   09:25   0:59 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-30T00:55:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
2026-08-30T00:55:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.67
2026-08-30T00:55:40Z INF Registered tunnel connection connIndex=3 connection=26f0a092-ad88-4448-b5bc-85a8be07d01f event=0 ip=198.41.192.67 location=lax11 protocol=quic
2026-08-30T00:55:43Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.73
2026-08-30T00:55:43Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.73
2026-08-30T00:55:43Z INF +-------------------------------------------------------------------------------------+
2026-08-30T00:55:43Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-30T00:55:43Z INF +-------------------------------------------------------------------------------------+
2026-08-30T00:55:43Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-30T00:55:43Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-30T00:55:43Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-30T00:55:43Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-30T00:55:43Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-30T00:55:43Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-30T00:55:43Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-30T00:55:43Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-30T00:55:43Z INF |                                                                                     |
2026-08-30T00:55:43Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-30T00:55:43Z INF +-------------------------------------------------------------------------------------+
2026-08-30T00:55:43Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f5322535-5227-4e80-a447-0696b981c5f7 status=pass target=region1.v2.argotunnel.com
2026-08-30T00:55:43Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f5322535-5227-4e80-a447-0696b981c5f7 status=pass target=region2.v2.argotunnel.com
2026-08-30T00:55:43Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f5322535-5227-4e80-a447-0696b981c5f7 status=pass target=region1.v2.argotunnel.com
2026-08-30T00:55:43Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f5322535-5227-4e80-a447-0696b981c5f7 status=pass target=region2.v2.argotunnel.com
2026-08-30T00:55:43Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f5322535-5227-4e80-a447-0696b981c5f7 status=pass target=region1.v2.argotunnel.com
2026-08-30T00:55:43Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f5322535-5227-4e80-a447-0696b981c5f7 status=pass target=region2.v2.argotunnel.com
2026-08-30T00:55:43Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f5322535-5227-4e80-a447-0696b981c5f7 status=pass target=api.cloudflare.com:443
2026-08-30T00:55:43Z INF precheck complete hard_fail=false run_id=f5322535-5227-4e80-a447-0696b981c5f7 suggested_protocol=quic
2026-08-30T00:55:44Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2
2026-08-30T00:55:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-30T00:55:48Z INF Registered tunnel connection connIndex=2 connection=aad55bdf-81a5-404a-b6c9-e7bbc7afdf79 event=0 ip=198.41.200.113 location=sjc07 protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:53:16] Time: Sun Aug 30 08:53:16 AM CST 2026
[08:53:16] User: root (UID: 0)
[08:53:16] === STEP 1: 启动 API (端口 8450) ===
[08:53:28] HEAD: b8a7f720 -> b8a7f720
[08:53:28] commit 对比: 运行进程=b8a7f720b8b2cd4f089e579d30840006d40b2d94 / 磁盘=b8a7f720b8b2cd4f089e579d30840006d40b2d94
[08:53:28] 代码已是最新且 API 健康 -> 跳过重启
[08:53:28] API 状态: OK
[08:53:28] === STEP 2: 安装 cloudflared ===
[08:53:28] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:53:28] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:53:28] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:53:28] === STEP 3: 检查认证方式 ===
[08:53:28] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:53:28] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:53:28] 检查现有 tunnel...
[08:53:29] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax09, 1xlax10, 2xlax12, 1xsjc05, 2xsjc08, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                      
2026-08-30T00:53:29Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:53:29] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:53:29] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:53:29] 凭证文件存在
[08:53:29] 创建 config.yml...
[08:53:29] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:53:29] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:53:32] DNS 路由结果: 2026-08-30T00:53:32Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:53:32] === STEP 5: 更新 DNS (API) ===
[08:53:32] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:53:33] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:53:34] 设置 SSL 模式为 Full...
SSL: 跳过
[08:53:35] === STEP 6: 启动 Tunnel ===
[08:53:38] 启动 Named Tunnel (cert 模式)...
[08:53:38] 使用 config: /root/.cloudflared/config.yml
[08:53:38] cloudflared PID: 238499
[08:53:40] Tunnel 连接已建立!
[08:53:40] --- cloudflared 日志 (最后 15 行) ---
2026-08-30T00:53:38Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-30T00:53:38Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-30T00:53:38Z INF Generated Connector ID: ac5541cd-8f10-40ca-9e80-82c7e61d81f0
2026-08-30T00:53:38Z INF Initial protocol quic
2026-08-30T00:53:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:53:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:53:38Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:53:38Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:53:38Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-30T00:53:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.113
2026-08-30T00:53:38Z INF Registered tunnel connection connIndex=0 connection=ea9c2576-5e16-4cae-a7e0-e7b95aab5648 event=0 ip=198.41.200.113 location=sjc10 protocol=quic
2026-08-30T00:53:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.107
2026-08-30T00:53:39Z INF Registered tunnel connection connIndex=1 connection=8c0a9adc-895e-4a8f-9171-9a184bddf676 event=0 ip=198.41.192.107 location=lax05 protocol=quic
2026-08-30T00:53:39Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-30T00:53:40Z INF Registered tunnel connection connIndex=2 connection=8f2dd0eb-cb3e-41f2-8710-f99a6884d063 event=0 ip=198.41.200.23 location=sjc10 protocol=quic
[08:53:40] === STEP 7: 持久化 ===
[08:53:40] systemd 服务已配置
[08:53:40] Cron 保活已设置
[08:53:40] === STEP 8: 验证 ===
[08:53:40] --- API (localhost:8450) ---
 OK
[08:53:40] --- cloudflared 进程 ---
root      238499  5.0  1.9 1360284 39044 ?       Sl   08:53   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      238594  0.0  1.3 1292740 27092 ?       Rl   08:53   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:53:40] --- aishield.tools ---
 OK
[08:53:41] --- DNS CNAME ---
[08:53:42] --- DNS A ---
104.21.81.46
172.67.188.44
[08:53:42] === 部署汇总 ===
[08:53:42] Tunnel Mode: cert
[08:53:42] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:53:42] API: http://localhost:8450
[08:53:42] 域名: https://aishield.tools
[08:53:42] cloudflared: /usr/local/bin/cloudflared
[08:53:42] PID: 238499
[08:53:42] Config: /root/.cloudflared/config.yml
[08:53:42] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:53:42] 状态: Named Tunnel (cert 模式) 已配置
[08:55:27] HEAD: b8a7f720 -> b8a7f720
[08:55:27] commit 对比: 运行进程=b8a7f720b8b2cd4f089e579d30840006d40b2d94 / 磁盘=b8a7f720b8b2cd4f089e579d30840006d40b2d94
[08:55:27] 代码已是最新且 API 健康 -> 跳过重启
[08:55:27] API 状态: OK
[08:55:27] === STEP 2: 安装 cloudflared ===
[08:55:27] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:55:27] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:55:27] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:55:27] === STEP 3: 检查认证方式 ===
[08:55:27] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:55:27] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:55:27] 检查现有 tunnel...
[08:55:28] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                   
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax07, 1xlax08, 1xlax11, 1xsjc08, 2xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                               
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                               
2026-08-30T00:55:28Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:55:28] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:55:28] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:55:28] 凭证文件存在
[08:55:28] 创建 config.yml...
[08:55:28] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:55:28] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:55:32] DNS 路由结果: 2026-08-30T00:55:32Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:55:32] === STEP 5: 更新 DNS (API) ===
[08:55:32] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:55:32] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:55:33] 设置 SSL 模式为 Full...
SSL: 跳过
[08:55:34] === STEP 6: 启动 Tunnel ===
[08:55:37] 启动 Named Tunnel (cert 模式)...
[08:55:37] 使用 config: /root/.cloudflared/config.yml
[08:55:37] cloudflared PID: 240262
[08:55:39] Tunnel 连接已建立!
[08:55:39] --- cloudflared 日志 (最后 15 行) ---
2026-08-30T00:55:37Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-30T00:55:37Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-30T00:55:37Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-30T00:55:37Z INF Generated Connector ID: e47d6b37-763e-44ba-be63-e5024da7dfc9
2026-08-30T00:55:37Z INF Initial protocol quic
2026-08-30T00:55:37Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:55:37Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:55:37Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-30T00:55:37Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-30T00:55:37Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-30T00:55:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.63
2026-08-30T00:55:37Z INF Registered tunnel connection connIndex=0 connection=7d93e03a-3db5-4815-b560-6b0ad47ea3cf event=0 ip=198.41.200.63 location=sjc08 protocol=quic
2026-08-30T00:55:37Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-08-30T00:55:38Z INF Registered tunnel connection connIndex=1 connection=2686486b-8940-4b8f-9d97-1b4ebd77e71c event=0 ip=198.41.192.57 location=lax08 protocol=quic
2026-08-30T00:55:38Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.73
[08:55:39] === STEP 7: 持久化 ===
[08:55:39] systemd 服务已配置
[08:55:39] Cron 保活已设置
[08:55:39] === STEP 8: 验证 ===
[08:55:39] --- API (localhost:8450) ---
 OK
[08:55:39] --- cloudflared 进程 ---
root      240262  4.5  1.9 1294420 39112 ?       Sl   08:55   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root      240361  0.0  1.3 1292484 27360 ?       Rl   08:55   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:55:39] --- aishield.tools ---
 OK
[08:55:41] --- DNS CNAME ---
[08:55:41] --- DNS A ---
172.67.188.44
104.21.81.46
[08:55:41] === 部署汇总 ===
[08:55:41] Tunnel Mode: cert
[08:55:41] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:55:41] API: http://localhost:8450
[08:55:41] 域名: https://aishield.tools
[08:55:41] cloudflared: /usr/local/bin/cloudflared
[08:55:41] PID: 240262
[08:55:41] Config: /root/.cloudflared/config.yml
[08:55:41] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:55:41] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-08-30 09:25:11 CST; 10h ago
   Main PID: 260025 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 26.8M
        CPU: 59.969s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─260025 /bin/bash /opt/start-tunnel.sh
             └─260027 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=227766,fd=3))                                                     
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
Time: Sun Aug 30 11:57:55 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788091076.2695446, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "b8a7f720b8b2cd4f089e579d30840006d40b2d94", "deployed_at": "2026-08-30T00:37:59Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
