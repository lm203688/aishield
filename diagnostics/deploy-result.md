=== DIAGNOSTIC ===
Time: Wed Aug 19 02:03:12 AM CST 2026
=== USER ===
root
=== GIT LOG ===
dbcf345 fix: download script from GitHub raw if git reset fails, add script version diagnostics
14ced6b chore: update deploy diagnostics [skip ci]
7b4068b fix: force git reset on server to get latest deploy script
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787076192.2522771, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2181789  1.2  1.8 1294676 36828 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2181808  1.2  1.8 1360284 37932 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2182044  2.1  1.9 1294676 38384 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-18T18:03:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-18T18:03:04Z INF Registered tunnel connection connIndex=0 connection=0d0d6f43-4a9c-4b4e-b6b2-8a02dd81f5c2 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-18T18:03:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-18T18:03:04Z INF Registered tunnel connection connIndex=1 connection=5037414b-d1af-481b-a6e5-17d169724727 event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-08-18T18:03:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-18T18:03:05Z INF Registered tunnel connection connIndex=2 connection=5424237a-1dc1-4ecb-8e81-a6b8e507ed9f event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-18T18:03:06Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.47
2026-08-18T18:03:06Z INF Registered tunnel connection connIndex=3 connection=396fa0d1-dd0c-4548-838b-b4e5df9a4398 event=0 ip=198.41.192.47 location=lax12 protocol=quic
2026-08-18T18:03:10Z INF +-------------------------------------------------------------------------------------+
2026-08-18T18:03:10Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-08-18T18:03:10Z INF +-------------------------------------------------------------------------------------+
2026-08-18T18:03:10Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-08-18T18:03:10Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T18:03:10Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-08-18T18:03:10Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T18:03:10Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-08-18T18:03:10Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T18:03:10Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-08-18T18:03:10Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-08-18T18:03:10Z INF |                                                                                     |
2026-08-18T18:03:10Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-08-18T18:03:10Z INF +-------------------------------------------------------------------------------------+
2026-08-18T18:03:10Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c57b65b5-63d4-4a4e-a4b7-d61e81687653 status=pass target=region1.v2.argotunnel.com
2026-08-18T18:03:10Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=c57b65b5-63d4-4a4e-a4b7-d61e81687653 status=pass target=region2.v2.argotunnel.com
2026-08-18T18:03:10Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c57b65b5-63d4-4a4e-a4b7-d61e81687653 status=pass target=region1.v2.argotunnel.com
2026-08-18T18:03:10Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=c57b65b5-63d4-4a4e-a4b7-d61e81687653 status=pass target=region2.v2.argotunnel.com
2026-08-18T18:03:10Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c57b65b5-63d4-4a4e-a4b7-d61e81687653 status=pass target=region1.v2.argotunnel.com
2026-08-18T18:03:10Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=c57b65b5-63d4-4a4e-a4b7-d61e81687653 status=pass target=region2.v2.argotunnel.com
2026-08-18T18:03:10Z INF precheck component="Cloudflare API" details="API is reachable" run_id=c57b65b5-63d4-4a4e-a4b7-d61e81687653 status=pass target=api.cloudflare.com:443
2026-08-18T18:03:10Z INF precheck complete hard_fail=false run_id=c57b65b5-63d4-4a4e-a4b7-d61e81687653 suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[02:02:54] Time: Wed Aug 19 02:02:54 AM CST 2026
[02:02:54] User: root (UID: 0)
[02:02:54] === STEP 1: 启动 API (端口 8450) ===
[02:02:55] API 已在运行
[02:02:55] API 状态: OK
[02:02:55] === STEP 2: 安装 cloudflared ===
[02:02:55] cloudflared 安装路径: /usr/local/bin/cloudflared
[02:02:55] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:02:56] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[02:02:56] === STEP 3: 检查认证方式 ===
[02:02:56] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[02:02:56] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[02:02:56] 检查现有 tunnel...
[02:02:56] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 4xlax01, 1xlax05, 1xlax08, 2xlax10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[02:02:56] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:02:56] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[02:02:56] 凭证文件存在
[02:02:56] 创建 config.yml...
[02:02:56] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[02:02:56] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:02:57] DNS 路由结果: 2026-08-18T18:02:57Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:02:57] === STEP 5: 更新 DNS (API) ===
[02:02:57] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:02:58] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[02:02:58] DNS 路由结果: 2026-08-18T18:02:58Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[02:02:58] === STEP 5: 更新 DNS (API) ===
[02:02:58] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
DNS 更新: OK
[02:02:59] 设置 SSL 模式为 Full...
[02:02:59] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
SSL: 跳过
[02:02:59] === STEP 6: 启动 Tunnel ===
DNS 更新: OK
[02:03:00] 设置 SSL 模式为 Full...
SSL: 跳过
[02:03:00] === STEP 6: 启动 Tunnel ===
[02:03:02] 启动 Named Tunnel (cert 模式)...
[02:03:02] 使用 config: /root/.cloudflared/config.yml
[02:03:02] cloudflared PID: 2181789
[02:03:03] 启动 Named Tunnel (cert 模式)...
[02:03:03] 使用 config: /root/.cloudflared/config.yml
[02:03:03] cloudflared PID: 2181808
[02:03:04] Tunnel 连接已建立!
[02:03:04] --- cloudflared 日志 (最后 15 行) ---
2026-08-18T18:03:03Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-18T18:03:03Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-18T18:03:03Z INF Generated Connector ID: afe820df-a663-46b9-9628-1abddd53bcaa
2026-08-18T18:03:03Z INF Initial protocol quic
2026-08-18T18:03:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T18:03:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T18:03:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T18:03:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T18:03:03Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-18T18:03:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-18T18:03:04Z INF Registered tunnel connection connIndex=0 connection=0d0d6f43-4a9c-4b4e-b6b2-8a02dd81f5c2 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-18T18:03:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-18T18:03:04Z INF Registered tunnel connection connIndex=1 connection=5037414b-d1af-481b-a6e5-17d169724727 event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-08-18T18:03:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.107
2026-08-18T18:03:04Z INF Registered tunnel connection connIndex=2 connection=c9371b9a-f3de-47dd-9cdf-8a77e9c17db0 event=0 ip=198.41.192.107 location=lax09 protocol=quic
[02:03:04] === STEP 7: 持久化 ===
[02:03:05] systemd 服务已配置
[02:03:05] Cron 保活已设置
[02:03:05] === STEP 8: 验证 ===
[02:03:05] --- API (localhost:8450) ---
 OK
[02:03:05] --- cloudflared 进程 ---
root     2181789  3.0  1.9 1294676 39252 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2181808  4.0  1.9 1359444 38444 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2181905  0.0  1.3 1292484 27524 ?       Rl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:03:05] --- aishield.tools ---
[02:03:05] Tunnel 连接已建立!
[02:03:05] --- cloudflared 日志 (最后 15 行) ---
2026-08-18T18:03:03Z INF Generated Connector ID: afe820df-a663-46b9-9628-1abddd53bcaa
2026-08-18T18:03:03Z INF Initial protocol quic
2026-08-18T18:03:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T18:03:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T18:03:03Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-18T18:03:03Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-18T18:03:03Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-18T18:03:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.43
2026-08-18T18:03:04Z INF Registered tunnel connection connIndex=0 connection=0d0d6f43-4a9c-4b4e-b6b2-8a02dd81f5c2 event=0 ip=198.41.200.43 location=lax01 protocol=quic
2026-08-18T18:03:04Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.27
2026-08-18T18:03:04Z INF Registered tunnel connection connIndex=1 connection=5037414b-d1af-481b-a6e5-17d169724727 event=0 ip=198.41.192.27 location=lax05 protocol=quic
2026-08-18T18:03:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.113
2026-08-18T18:03:05Z INF Registered tunnel connection connIndex=2 connection=5424237a-1dc1-4ecb-8e81-a6b8e507ed9f event=0 ip=198.41.200.113 location=lax01 protocol=quic
2026-08-18T18:03:05Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.13
2026-08-18T18:03:05Z INF Registered tunnel connection connIndex=3 connection=a5505f01-5687-402a-b46b-a1cb41176d63 event=0 ip=198.41.200.13 location=lax01 protocol=quic
[02:03:05] === STEP 7: 持久化 ===
[02:03:06] systemd 服务已配置
[02:03:06] Cron 保活已设置
[02:03:06] === STEP 8: 验证 ===
[02:03:06] --- API (localhost:8450) ---
 OK
[02:03:06] --- cloudflared 进程 ---
root     2181789  2.5  1.9 1294676 39128 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2181808  2.6  1.9 1359444 38520 ?       Sl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2182044  0.0  1.3 1292484 27332 ?       Rl   02:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[02:03:06] --- aishield.tools ---
 OK
[02:03:07] --- DNS CNAME ---
[02:03:07] --- DNS A ---
172.67.188.44
104.21.81.46
[02:03:07] === 部署汇总 ===
[02:03:07] Tunnel Mode: cert
[02:03:07] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:03:07] API: http://localhost:8450
[02:03:07] 域名: https://aishield.tools
[02:03:07] cloudflared: /usr/local/bin/cloudflared
[02:03:07] PID: 2181789
[02:03:07] Config: /root/.cloudflared/config.yml
[02:03:07] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:03:07] 状态: Named Tunnel (cert 模式) 已配置
 FAIL (DNS 传播中或配置错误)
[02:03:11] --- DNS CNAME ---
[02:03:11] --- DNS A ---
104.21.81.46
172.67.188.44
[02:03:11] === 部署汇总 ===
[02:03:11] Tunnel Mode: cert
[02:03:11] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[02:03:11] API: http://localhost:8450
[02:03:11] 域名: https://aishield.tools
[02:03:11] cloudflared: /usr/local/bin/cloudflared
[02:03:11] PID: 2181808
[02:03:11] Config: /root/.cloudflared/config.yml
[02:03:11] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[02:03:11] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-08-19 02:03:06 CST; 5s ago
   Main PID: 2182035 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 20.2M
        CPU: 142ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2182035 /bin/bash /opt/start-tunnel.sh
             └─2182044 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=1897042,fd=3))                                                    
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
Time: Tue Aug 18 18:03:12 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1787076192.913678, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
