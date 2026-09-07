=== DIAGNOSTIC ===
Time: Mon Sep 7 04:17:36 PM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788769056.1762052, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "08a75eba2c2987e2368f7618a0f6303dac212c0e", "deployed_at": "2026-09-06T08:48:34Z"}OK
=== CLOUDFLARED PROCESS ===
root     2962567  0.1  1.0 1294676 20932 ?       Sl   Sep06   2:09 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2962687  0.1  1.0 1360284 21016 ?       Ssl  Sep06   2:09 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     2962692  0.1  1.3 1294676 26684 ?       Sl   Sep06   2:08 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-06T08:48:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-09-06T08:48:54Z INF Registered tunnel connection connIndex=0 connection=4b57ba17-1991-45e4-a6f2-3e2f9b6a1cbd event=0 ip=198.41.200.33 location=sjc11 protocol=quic
2026-09-06T08:48:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
2026-09-06T08:48:55Z INF Registered tunnel connection connIndex=1 connection=203dcfee-c9f6-4239-9ec9-55704dcaae55 event=0 ip=198.41.192.227 location=lax05 protocol=quic
2026-09-06T08:48:55Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
2026-09-06T08:48:56Z INF Registered tunnel connection connIndex=2 connection=a83fe252-2acd-4829-88cd-d6020c1603db event=0 ip=198.41.200.43 location=sjc08 protocol=quic
2026-09-06T08:48:56Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.107
2026-09-06T08:48:57Z INF Registered tunnel connection connIndex=3 connection=543baf74-4c22-42ca-98ae-416555e9eb0f event=0 ip=198.41.192.107 location=lax12 protocol=quic
2026-09-06T08:49:02Z INF +-------------------------------------------------------------------------------------+
2026-09-06T08:49:02Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-09-06T08:49:02Z INF +-------------------------------------------------------------------------------------+
2026-09-06T08:49:02Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-09-06T08:49:02Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-06T08:49:02Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-06T08:49:02Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-06T08:49:02Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-06T08:49:02Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-06T08:49:02Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-06T08:49:02Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-09-06T08:49:02Z INF |                                                                                     |
2026-09-06T08:49:02Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-09-06T08:49:02Z INF +-------------------------------------------------------------------------------------+
2026-09-06T08:49:02Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cd32bc25-1e18-4aa8-99ad-97fcfbe76aed status=pass target=region1.v2.argotunnel.com
2026-09-06T08:49:02Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=cd32bc25-1e18-4aa8-99ad-97fcfbe76aed status=pass target=region2.v2.argotunnel.com
2026-09-06T08:49:02Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cd32bc25-1e18-4aa8-99ad-97fcfbe76aed status=pass target=region1.v2.argotunnel.com
2026-09-06T08:49:02Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=cd32bc25-1e18-4aa8-99ad-97fcfbe76aed status=pass target=region2.v2.argotunnel.com
2026-09-06T08:49:02Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cd32bc25-1e18-4aa8-99ad-97fcfbe76aed status=pass target=region1.v2.argotunnel.com
2026-09-06T08:49:02Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=cd32bc25-1e18-4aa8-99ad-97fcfbe76aed status=pass target=region2.v2.argotunnel.com
2026-09-06T08:49:02Z INF precheck component="Cloudflare API" details="API is reachable" run_id=cd32bc25-1e18-4aa8-99ad-97fcfbe76aed status=pass target=api.cloudflare.com:443
2026-09-06T08:49:02Z INF precheck complete hard_fail=false run_id=cd32bc25-1e18-4aa8-99ad-97fcfbe76aed suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:48:33] Time: Sun Sep  6 04:48:33 PM CST 2026
[16:48:33] User: root (UID: 0)
[16:48:33] === STEP 1: 启动 API (端口 8450) ===
[16:48:33] 代码由 runner tarball 投递，权威 sha=08a75eba
[16:48:34] commit 对比: 运行进程=4c18b94bcb180aec29357e6a18cfc15bb4a956cc / 磁盘=08a75eba2c2987e2368f7618a0f6303dac212c0e
[16:48:34] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[16:48:34] 需要重新加载代码 -> 重启 API
[16:48:34] 强制重启 Python API 进程（当前commit=4c18b94bcb180aec29357e6a18cfc15bb4a956cc 目标=08a75eba2c2987e2368f7618a0f6303dac212c0e）
[16:48:44] API 状态: OK
[16:48:44] === STEP 2: 安装 cloudflared ===
[16:48:44] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:48:44] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:48:44] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:48:44] === STEP 3: 检查认证方式 ===
[16:48:44] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:48:44] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:48:44] 检查现有 tunnel...
[16:48:45] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax05, 2xlax07, 1xlax11, 1xsjc05, 3xsjc10 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                             
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax10, 1xlax11, 1xsjc05, 1xsjc10          
[16:48:45] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:48:45] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:48:45] 凭证文件存在
[16:48:45] 创建 config.yml...
[16:48:45] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:48:45] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:48:48] DNS 路由结果: 2026-09-06T08:48:48Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:48:48] === STEP 5: 更新 DNS (API) ===
[16:48:48] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:48:49] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:48:50] 设置 SSL 模式为 Full...
SSL: 跳过
[16:48:51] === STEP 6: 启动 Tunnel ===
[16:48:54] 启动 Named Tunnel (cert 模式)...
[16:48:54] 使用 config: /root/.cloudflared/config.yml
[16:48:54] cloudflared PID: 2962567
[16:48:56] Tunnel 连接已建立!
[16:48:56] --- cloudflared 日志 (最后 15 行) ---
2026-09-06T08:48:54Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-09-06T08:48:54Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-06T08:48:54Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-06T08:48:54Z INF Generated Connector ID: 127a8b59-24a2-4ba1-962a-c83626f2892c
2026-09-06T08:48:54Z INF Initial protocol quic
2026-09-06T08:48:54Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-06T08:48:54Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-06T08:48:54Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-06T08:48:54Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-06T08:48:54Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-09-06T08:48:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.33
2026-09-06T08:48:54Z INF Registered tunnel connection connIndex=0 connection=4b57ba17-1991-45e4-a6f2-3e2f9b6a1cbd event=0 ip=198.41.200.33 location=sjc11 protocol=quic
2026-09-06T08:48:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.227
2026-09-06T08:48:55Z INF Registered tunnel connection connIndex=1 connection=203dcfee-c9f6-4239-9ec9-55704dcaae55 event=0 ip=198.41.192.227 location=lax05 protocol=quic
2026-09-06T08:48:55Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.43
[16:48:56] === STEP 7: 持久化 ===
[16:48:57] systemd 服务已配置
[16:48:57] Cron 保活已设置
[16:48:57] === STEP 8: 验证 ===
[16:48:57] --- API (localhost:8450) ---
 OK
[16:48:57] --- cloudflared 进程 ---
root     2962567  2.5  1.9 1294420 39208 ?       Sl   16:48   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2962687  0.0  1.3 1358348 27544 ?       Rsl  16:48   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     2962692  1.0  1.3 1292740 27100 ?       Rl   16:48   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:48:58] --- aishield.tools ---
 OK
[16:48:59] --- DNS CNAME ---
[16:49:00] --- DNS A ---
104.21.81.46
172.67.188.44
[16:49:00] === 部署汇总 ===
[16:49:00] Tunnel Mode: cert
[16:49:00] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:49:00] API: http://localhost:8450
[16:49:00] 域名: https://aishield.tools
[16:49:00] cloudflared: /usr/local/bin/cloudflared
[16:49:00] PID: 2962567
[16:49:00] Config: /root/.cloudflared/config.yml
[16:49:00] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:49:00] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-09-06 16:48:57 CST; 23h ago
   Main PID: 2962691 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 26.7M
        CPU: 2min 8.651s
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2962691 /bin/bash /opt/start-tunnel.sh
             └─2962692 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2962223,fd=3))                                                    
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
Time: Mon Sep  7 08:17:46 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788769066.6679187, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "08a75eba2c2987e2368f7618a0f6303dac212c0e", "deployed_at": "2026-09-06T08:48:34Z"}
=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
