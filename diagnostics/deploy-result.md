=== DIAGNOSTIC ===
Time: Mon Sep 7 10:25:15 PM CST 2026
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
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1788791115.306595, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "a8201ff78841125f170eec9464cdd6f7cc608c48", "deployed_at": "2026-09-07T14:24:39Z"}OK
=== CLOUDFLARED PROCESS ===
root     4112998  0.8  1.7 1294092 36092 ?       Sl   22:24   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4113181  1.2  1.8 1294676 37876 ?       Ssl  22:25   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     4113197  1.1  1.9 1294676 38436 ?       Sl   22:25   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-07T14:25:01Z INF Registered tunnel connection connIndex=0 connection=590a4aed-1770-4a63-b89b-69f33abe3dd6 event=0 ip=198.41.192.167 location=lax05 protocol=quic
2026-09-07T14:25:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-09-07T14:25:01Z INF Registered tunnel connection connIndex=1 connection=10ac8e19-0961-44da-b937-d1ea448c6efb event=0 ip=198.41.200.23 location=sjc10 protocol=quic
2026-09-07T14:25:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
2026-09-07T14:25:02Z INF Registered tunnel connection connIndex=2 connection=0694bb6d-f859-4583-9fdc-136a71b2227f event=0 ip=198.41.192.57 location=lax11 protocol=quic
2026-09-07T14:25:03Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.33
2026-09-07T14:25:03Z INF Registered tunnel connection connIndex=3 connection=b403c38e-ba24-48a5-8ae4-e57ddc8ab351 event=0 ip=198.41.200.33 location=sjc11 protocol=quic
2026-09-07T14:25:10Z INF +-----------------------------------------------------------------------------------------------+
2026-09-07T14:25:10Z INF |                                    CONNECTIVITY PRE-CHECKS                                    |
2026-09-07T14:25:10Z INF +-----------------------------------------------------------------------------------------------+
2026-09-07T14:25:10Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                                 |
2026-09-07T14:25:10Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-09-07T14:25:10Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully               |
2026-09-07T14:25:10Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful              |
2026-09-07T14:25:10Z INF |  UDP Connectivity  region2.v2.argotunnel.com  FAIL    QUIC connection failed                  |
2026-09-07T14:25:10Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-09-07T14:25:10Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful            |
2026-09-07T14:25:10Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable                        |
2026-09-07T14:25:10Z INF |  WARNING: Allow outbound QUIC traffic on port 7844 or use HTTP2.                              |
2026-09-07T14:25:10Z INF |                                                                                               |
2026-09-07T14:25:10Z INF |  SUMMARY: Environment ready with degraded transport. cloudflared will proceed using 'http2'.  |
2026-09-07T14:25:10Z INF +-----------------------------------------------------------------------------------------------+
2026-09-07T14:25:10Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f52c0f39-29a7-407f-8552-9795bc7e1342 status=pass target=region1.v2.argotunnel.com
2026-09-07T14:25:10Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=f52c0f39-29a7-407f-8552-9795bc7e1342 status=pass target=region2.v2.argotunnel.com
2026-09-07T14:25:10Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=f52c0f39-29a7-407f-8552-9795bc7e1342 status=pass target=region1.v2.argotunnel.com
2026-09-07T14:25:10Z INF precheck component="UDP Connectivity" details="QUIC connection failed" run_id=f52c0f39-29a7-407f-8552-9795bc7e1342 status=fail target=region2.v2.argotunnel.com
2026-09-07T14:25:10Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f52c0f39-29a7-407f-8552-9795bc7e1342 status=pass target=region1.v2.argotunnel.com
2026-09-07T14:25:10Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=f52c0f39-29a7-407f-8552-9795bc7e1342 status=pass target=region2.v2.argotunnel.com
2026-09-07T14:25:10Z INF precheck component="Cloudflare API" details="API is reachable" run_id=f52c0f39-29a7-407f-8552-9795bc7e1342 status=pass target=api.cloudflare.com:443
2026-09-07T14:25:10Z INF precheck complete hard_fail=false run_id=f52c0f39-29a7-407f-8552-9795bc7e1342 suggested_protocol=http2
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[22:24:39] Time: Mon Sep  7 10:24:39 PM CST 2026
[22:24:39] User: root (UID: 0)
[22:24:39] === STEP 1: 启动 API (端口 8450) ===
[22:24:39] 代码由 runner tarball 投递，权威 sha=a8201ff7
[22:24:39] commit 对比: 运行进程=08a75eba2c2987e2368f7618a0f6303dac212c0e / 磁盘=a8201ff78841125f170eec9464cdd6f7cc608c48
[22:24:39] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[22:24:39] 需要重新加载代码 -> 重启 API
[22:24:39] 强制重启 Python API 进程（当前commit=08a75eba2c2987e2368f7618a0f6303dac212c0e 目标=a8201ff78841125f170eec9464cdd6f7cc608c48）
[22:24:49] API 状态: OK
[22:24:49] === STEP 2: 安装 cloudflared ===
[22:24:49] cloudflared 安装路径: /usr/local/bin/cloudflared
[22:24:50] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:24:50] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[22:24:50] === STEP 3: 检查认证方式 ===
[22:24:50] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[22:24:50] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[22:24:50] 检查现有 tunnel...
[22:24:51] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME              CREATED              CONNECTIONS                                          
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel   2026-07-30T23:21:20Z 1xlax05, 1xlax09, 1xlax10, 1xlax12, 2xsjc08, 2xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools    2026-06-27T14:20:27Z                                                      
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens        2026-07-28T03:03:32Z                                                      
772e48b6-fec9-4295-9816-92f6479e823d healthlens-tunnel 2026-09-02T00:32:00Z 1xlax08, 1xlax09, 2xsjc05                            
[22:24:51] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[22:24:51] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[22:24:51] 凭证文件存在
[22:24:51] 创建 config.yml...
[22:24:51] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[22:24:51] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:24:53] DNS 路由结果: 2026-09-07T14:24:53Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[22:24:53] === STEP 5: 更新 DNS (API) ===
[22:24:53] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:24:54] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[22:24:56] 设置 SSL 模式为 Full...
SSL: 跳过
[22:24:57] === STEP 6: 启动 Tunnel ===
[22:25:00] 启动 Named Tunnel (cert 模式)...
[22:25:00] 使用 config: /root/.cloudflared/config.yml
[22:25:00] cloudflared PID: 4112998
[22:25:02] Tunnel 连接已建立!
[22:25:02] --- cloudflared 日志 (最后 15 行) ---
2026-09-07T14:25:00Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-09-07T14:25:00Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-07T14:25:00Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-07T14:25:00Z INF Generated Connector ID: 387c7e9c-0623-48e1-96e1-0af8b731a1ef
2026-09-07T14:25:00Z INF Initial protocol quic
2026-09-07T14:25:00Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-07T14:25:00Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-07T14:25:00Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-07T14:25:00Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-07T14:25:00Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-09-07T14:25:00Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.167
2026-09-07T14:25:01Z INF Registered tunnel connection connIndex=0 connection=590a4aed-1770-4a63-b89b-69f33abe3dd6 event=0 ip=198.41.192.167 location=lax05 protocol=quic
2026-09-07T14:25:01Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.23
2026-09-07T14:25:01Z INF Registered tunnel connection connIndex=1 connection=10ac8e19-0961-44da-b937-d1ea448c6efb event=0 ip=198.41.200.23 location=sjc10 protocol=quic
2026-09-07T14:25:02Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.57
[22:25:02] === STEP 7: 持久化 ===
[22:25:03] systemd 服务已配置
[22:25:03] Cron 保活已设置
[22:25:03] === STEP 8: 验证 ===
[22:25:03] --- API (localhost:8450) ---
 OK
[22:25:04] --- cloudflared 进程 ---
root     4112998  2.2  1.9 1294092 38464 ?       Sl   22:24   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     4113181  1.0  1.3 1292740 27360 ?       Rsl  22:25   0:00 /usr/local/bin/cloudflared --config /etc/cloudflared-healthlens/config.yml tunnel --metrics 127.0.0.1:8099 run
root     4113197  1.0  1.3 1292740 27160 ?       Rl   22:25   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[22:25:04] --- aishield.tools ---
 OK
[22:25:05] --- DNS CNAME ---
[22:25:06] --- DNS A ---
104.21.81.46
172.67.188.44
[22:25:06] === 部署汇总 ===
[22:25:06] Tunnel Mode: cert
[22:25:06] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[22:25:06] API: http://localhost:8450
[22:25:06] 域名: https://aishield.tools
[22:25:06] cloudflared: /usr/local/bin/cloudflared
[22:25:06] PID: 4112998
[22:25:06] Config: /root/.cloudflared/config.yml
[22:25:06] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[22:25:06] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-09-07 22:25:03 CST; 11s ago
   Main PID: 4113185 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 20.8M
        CPU: 158ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─4113185 /bin/bash /opt/start-tunnel.sh
             └─4113197 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=4112643,fd=3))                                                    
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
Time: Mon Sep  7 14:25:25 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 236, "rules_breakdown": {"static": 210, "generated": 9, "radar": 17, "total": 236}, "uptime": 1788791125.6329958, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "a8201ff78841125f170eec9464cdd6f7cc608c48", "deployed_at": "2026-09-07T14:24:39Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
