=== DIAGNOSTIC ===
Time: Mon Aug 31 08:33:59 AM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788136439.0427434, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "b8a7f720b8b2cd4f089e579d30840006d40b2d94", "deployed_at": "2026-08-30T00:37:59Z"}OK
=== CLOUDFLARED PROCESS ===
root     1143660  1.0  1.8 1294420 38020 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1143848  1.5  1.9 1294092 38416 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-31T00:33:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-31T00:33:50Z INF Registered tunnel connection connIndex=2 connection=cf3c49dd-ec5a-4f97-ac44-4a4e1eff1b5c event=0 ip=198.41.200.23 location=sjc10 protocol=quic
2026-08-31T00:33:51Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.37
2026-08-31T00:33:51Z INF Registered tunnel connection connIndex=3 connection=651447ce-148e-4ca6-99fd-7e85c4db78fc event=0 ip=198.41.192.37 location=lax09 protocol=quic
2026-08-31T00:33:54Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1 event=0 ip=198.41.200.193
2026-08-31T00:33:54Z INF Retrying connection in up to 2s connIndex=1 event=0 ip=198.41.200.193
2026-08-31T00:33:55Z INF +-------------------------------------------------------------------------------------+
2026-08-31T00:33:55Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-31T00:33:55Z INF +-------------------------------------------------------------------------------------+
2026-08-31T00:33:55Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-31T00:33:55Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-31T00:33:55Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-31T00:33:55Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-31T00:33:55Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-31T00:33:55Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-31T00:33:55Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-31T00:33:55Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-31T00:33:55Z INF |                                                                                     |
2026-08-31T00:33:55Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-31T00:33:55Z INF +-------------------------------------------------------------------------------------+
2026-08-31T00:33:55Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e2bab30b-9a3e-431a-9db2-74e6d479d076 status=pass target=region1.v2.argotunnel.com
2026-08-31T00:33:55Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=e2bab30b-9a3e-431a-9db2-74e6d479d076 status=pass target=region2.v2.argotunnel.com
2026-08-31T00:33:55Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e2bab30b-9a3e-431a-9db2-74e6d479d076 status=pass target=region1.v2.argotunnel.com
2026-08-31T00:33:55Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=e2bab30b-9a3e-431a-9db2-74e6d479d076 status=pass target=region2.v2.argotunnel.com
2026-08-31T00:33:55Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e2bab30b-9a3e-431a-9db2-74e6d479d076 status=pass target=region1.v2.argotunnel.com
2026-08-31T00:33:55Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=e2bab30b-9a3e-431a-9db2-74e6d479d076 status=pass target=region2.v2.argotunnel.com
2026-08-31T00:33:55Z INF precheck component="Cloudflare API" details="API is reachable" run_id=e2bab30b-9a3e-431a-9db2-74e6d479d076 status=pass target=api.cloudflare.com:443
2026-08-31T00:33:55Z INF precheck complete hard_fail=false run_id=e2bab30b-9a3e-431a-9db2-74e6d479d076 suggested_protocol=quic
2026-08-31T00:33:55Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=1
2026-08-31T00:33:59Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.73
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[08:33:33] Time: Mon Aug 31 08:33:33 AM CST 2026
[08:33:33] User: root (UID: 0)
[08:33:33] === STEP 1: 启动 API (端口 8450) ===
[08:33:41] HEAD: b8a7f720 -> b8a7f720
[08:33:41] commit 对比: 运行进程=b8a7f720b8b2cd4f089e579d30840006d40b2d94 / 磁盘=b8a7f720b8b2cd4f089e579d30840006d40b2d94
[08:33:41] 代码已是最新且 API 健康 -> 跳过重启
[08:33:41] API 状态: OK
[08:33:41] === STEP 2: 安装 cloudflared ===
[08:33:41] cloudflared 安装路径: /usr/local/bin/cloudflared
[08:33:41] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:33:41] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[08:33:41] === STEP 3: 检查认证方式 ===
[08:33:41] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[08:33:41] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[08:33:41] 检查现有 tunnel...
[08:33:42] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax05, 1xlax12, 1xsjc07, 1xsjc08 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
2026-08-31T00:33:42Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.2
[08:33:42] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:33:42] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[08:33:42] 凭证文件存在
[08:33:42] 创建 config.yml...
[08:33:42] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[08:33:42] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:33:43] DNS 路由结果: 2026-08-31T00:33:43Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[08:33:43] === STEP 5: 更新 DNS (API) ===
[08:33:43] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:33:44] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[08:33:44] 设置 SSL 模式为 Full...
SSL: 跳过
[08:33:45] === STEP 6: 启动 Tunnel ===
[08:33:48] 启动 Named Tunnel (cert 模式)...
[08:33:48] 使用 config: /root/.cloudflared/config.yml
[08:33:48] cloudflared PID: 1143660
[08:33:50] Tunnel 连接已建立!
[08:33:50] --- cloudflared 日志 (最后 15 行) ---
2026-08-31T00:33:48Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-31T00:33:48Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-31T00:33:48Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-31T00:33:48Z INF Generated Connector ID: 4660d3bf-95bd-437c-b8dc-83c3bad7c180
2026-08-31T00:33:48Z INF Initial protocol quic
2026-08-31T00:33:48Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-31T00:33:48Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-31T00:33:48Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-31T00:33:48Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-31T00:33:48Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-08-31T00:33:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-08-31T00:33:49Z INF Registered tunnel connection connIndex=0 connection=9829b80e-a510-42b4-bf83-0e1a3eaa1c5d event=0 ip=198.41.192.167 location=lax10 protocol=quic
2026-08-31T00:33:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.193
2026-08-31T00:33:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.23
2026-08-31T00:33:50Z INF Registered tunnel connection connIndex=2 connection=cf3c49dd-ec5a-4f97-ac44-4a4e1eff1b5c event=0 ip=198.41.200.23 location=sjc10 protocol=quic
[08:33:50] === STEP 7: 持久化 ===
[08:33:51] systemd 服务已配置
[08:33:51] Cron 保活已设置
[08:33:51] === STEP 8: 验证 ===
[08:33:51] --- API (localhost:8450) ---
 OK
[08:33:51] --- cloudflared 进程 ---
root     1143660  3.3  1.8 1294420 38152 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     1143848  0.0  1.3 1292740 27632 ?       Sl   08:33   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[08:33:51] --- aishield.tools ---
 OK
[08:33:53] --- DNS CNAME ---
[08:33:53] --- DNS A ---
172.67.188.44
104.21.81.46
[08:33:53] === 部署汇总 ===
[08:33:53] Tunnel Mode: cert
[08:33:53] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[08:33:53] API: http://localhost:8450
[08:33:53] 域名: https://aishield.tools
[08:33:53] cloudflared: /usr/local/bin/cloudflared
[08:33:53] PID: 1143660
[08:33:53] Config: /root/.cloudflared/config.yml
[08:33:53] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[08:33:53] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-31 08:33:51 CST; 7s ago
   Main PID: 1143847 (start-tunnel.sh)
      Tasks: 8 (limit: 2216)
     Memory: 18.3M
        CPU: 137ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─1143847 /bin/bash /opt/start-tunnel.sh
             └─1143848 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
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
Time: Mon Aug 31 00:34:06 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788136446.8177047, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "b8a7f720b8b2cd4f089e579d30840006d40b2d94", "deployed_at": "2026-08-30T00:37:59Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
