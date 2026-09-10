=== DIAGNOSTIC ===
Time: Thu Sep 10 04:12:07 PM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1789027927.8625586, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "2e12c70baaf961a13ecc3f562b90b8a6df0eeb3e", "deployed_at": "2026-09-10T08:11:32Z"}OK
=== CLOUDFLARED PROCESS ===
root     2483783  1.1  1.8 1294420 36920 ?       Sl   16:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2483914  1.0  1.9 1359708 38220 ?       Ssl  16:11   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     2483916  1.2  1.9 1294676 39504 ?       Sl   16:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-10T08:11:52Z INF Registered tunnel connection connIndex=0 connection=fd4644ca-7cb0-4bf6-8464-f5a7694094f2 event=0 ip=198.41.192.37 location=sjc06 protocol=quic
2026-09-10T08:11:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-09-10T08:11:53Z INF Registered tunnel connection connIndex=1 connection=d4552a7e-f37d-4f54-98a8-c89175ad1afd event=0 ip=198.41.200.33 location=sjc10 protocol=quic
2026-09-10T08:11:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
2026-09-10T08:11:54Z INF Registered tunnel connection connIndex=2 connection=c729e0fd-673e-4230-8c90-247100bb52a0 event=0 ip=198.41.200.13 location=sjc10 protocol=quic
2026-09-10T08:11:54Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.192.67
2026-09-10T08:11:55Z INF Registered tunnel connection connIndex=3 connection=4626e1a2-488c-4506-a49b-be6f8b674963 event=0 ip=198.41.192.67 location=sjc01 protocol=quic
2026-09-10T08:12:02Z INF +-----------------------------------------------------------------------------------------------+
2026-09-10T08:12:02Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-09-10T08:12:02Z INF +-----------------------------------------------------------------------------------------------+
2026-09-10T08:12:02Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-09-10T08:12:02Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-09-10T08:12:02Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-09-10T08:12:02Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-09-10T08:12:02Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-09-10T08:12:02Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-09-10T08:12:02Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-09-10T08:12:02Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-09-10T08:12:02Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-09-10T08:12:02Z INF |                                                                                               |
2026-09-10T08:12:02Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-09-10T08:12:02Z INF +-----------------------------------------------------------------------------------------------+
2026-09-10T08:12:02Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=bd96c9d0-8d5d-4008-8dde-f095703ed282 status=pass target=region1.v2.argotunnel.com
2026-09-10T08:12:02Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=bd96c9d0-8d5d-4008-8dde-f095703ed282 status=pass target=region2.v2.argotunnel.com
2026-09-10T08:12:02Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=bd96c9d0-8d5d-4008-8dde-f095703ed282 status=pass target=region1.v2.argotunnel.com
2026-09-10T08:12:02Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=bd96c9d0-8d5d-4008-8dde-f095703ed282 status=fail target=region2.v2.argotunnel.com
2026-09-10T08:12:02Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bd96c9d0-8d5d-4008-8dde-f095703ed282 status=pass target=region1.v2.argotunnel.com
2026-09-10T08:12:02Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=bd96c9d0-8d5d-4008-8dde-f095703ed282 status=pass target=region2.v2.argotunnel.com
2026-09-10T08:12:02Z INF precheck component="Cloudflare API" details="API is reachable" run_id=bd96c9d0-8d5d-4008-8dde-f095703ed282 status=pass target=api.cloudflare.com:443
2026-09-10T08:12:02Z INF precheck complete hard_fail=false run_id=bd96c9d0-8d5d-4008-8dde-f095703ed282 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[16:11:32] Time: Thu Sep 10 04:11:32 PM CST 2026
[16:11:32] User: root (UID: 0)
[16:11:32] === STEP 1: 启动 API (端口 8450) ===
[16:11:32] 代码由 runner tarball 投递，权威 sha=2e12c70b
[16:11:32] commit 对比: 运行进程=60e78aab40558f06f9e3d1b5279d716fbe8b2afb / 磁盘=2e12c70baaf961a13ecc3f562b90b8a6df0eeb3e
[16:11:32] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[16:11:32] 需要重新加载代码 -> 重启 API
[16:11:33] 强制重启 Python API 进程（当前commit=60e78aab40558f06f9e3d1b5279d716fbe8b2afb 目标=2e12c70baaf961a13ecc3f562b90b8a6df0eeb3e）
[16:11:43] API 状态: OK
[16:11:43] === STEP 2: 安装 cloudflared ===
[16:11:43] cloudflared 安装路径: /usr/local/bin/cloudflared
[16:11:43] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:11:43] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[16:11:43] === STEP 3: 检查认证方式 ===
[16:11:43] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[16:11:43] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[16:11:43] 检查现有 tunnel...
[16:11:44] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                                            
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax08, 1xlax09, 1xlax10, 1xlax11, 1xsjc05, 1xsjc07, 1xsjc10, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                                        
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                                        
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax11, 1xlax12, 1xsjc07, 1xsjc11                                     
[16:11:44] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:11:44] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[16:11:44] 凭证文件存在
[16:11:44] 创建 config.yml...
[16:11:44] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[16:11:44] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:11:45] DNS 路由结果: 2026-09-10T08:11:45Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[16:11:45] === STEP 5: 更新 DNS (API) ===
[16:11:45] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:11:46] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[16:11:48] 设置 SSL 模式为 Full...
SSL: 跳过
[16:11:49] === STEP 6: 启动 Tunnel ===
[16:11:52] 启动 Named Tunnel (cert 模式)...
[16:11:52] 使用 config: /root/.cloudflared/config.yml
[16:11:52] cloudflared PID: 2483783
[16:11:54] Tunnel 连接已建立!
[16:11:54] --- cloudflared 日志 (最后 15 行) ---
2026-09-10T08:11:52Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-09-10T08:11:52Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-10T08:11:52Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-10T08:11:52Z INF Generated Connector ID: 3547de30-00cc-43b6-9908-7cd78ee46d77
2026-09-10T08:11:52Z INF Initial protocol quic
2026-09-10T08:11:52Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-10T08:11:52Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-10T08:11:52Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-10T08:11:52Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-10T08:11:52Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-09-10T08:11:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.37
2026-09-10T08:11:52Z INF Registered tunnel connection connIndex=0 connection=fd4644ca-7cb0-4bf6-8464-f5a7694094f2 event=0 ip=198.41.192.37 location=sjc06 protocol=quic
2026-09-10T08:11:52Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.33
2026-09-10T08:11:53Z INF Registered tunnel connection connIndex=1 connection=d4552a7e-f37d-4f54-98a8-c89175ad1afd event=0 ip=198.41.200.33 location=sjc10 protocol=quic
2026-09-10T08:11:53Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.13
[16:11:54] === STEP 7: 持久化 ===
[16:11:55] systemd 服务已配置
[16:11:55] Cron 保活已设置
[16:11:55] === STEP 8: 验证 ===
[16:11:55] --- API (localhost:8450) ---
 OK
[16:11:55] --- cloudflared 进程 ---
root     2483783  4.6  1.8 1294420 37352 ?       Sl   16:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2483914  0.0  1.3 1292484 27244 ?       Rsl  16:11   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     2483916  0.0  1.3 1292484 27152 ?       Rl   16:11   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[16:11:55] --- aishield.tools ---
 OK
[16:11:56] --- DNS CNAME ---
[16:11:57] --- DNS A ---
104.21.81.46
172.67.188.44
[16:11:57] === 部署汇总 ===
[16:11:57] Tunnel Mode: cert
[16:11:57] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[16:11:57] API: http://localhost:8450
[16:11:57] 域名: https://aishield.tools
[16:11:57] cloudflared: /usr/local/bin/cloudflared
[16:11:57] PID: 2483783
[16:11:57] Config: /root/.cloudflared/config.yml
[16:11:57] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[16:11:57] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-09-10 16:11:55 CST; 12s ago
   Main PID: 2483915 (start-tunnel.sh)
      Tasks: 10 (limit: 2216)
     Memory: 20.0M
        CPU: 154ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2483915 /bin/bash /opt/start-tunnel.sh
             └─2483916 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2483442,fd=3))                                                    
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
Time: Thu Sep 10 08:12:19 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1789027939.4999337, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "2e12c70baaf961a13ecc3f562b90b8a6df0eeb3e", "deployed_at": "2026-09-10T08:11:32Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
