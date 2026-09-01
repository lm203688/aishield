=== DIAGNOSTIC ===
Time: Tue Sep 1 01:00:40 PM CST 2026
=== USER ===
root
=== GIT LOG ===
93fcd10c auto: 威胁情报入库 + 检测规则更新 + README计数同步（情报 270 条 / 规则 74 条）[skip ci]
ec65b03f auto: 批量扫描入库 [skip ci]
86030d86 chore: 重生成 task-registry 反映 spine 融合架构（18 workflow / 5 定时 / 13 事件驱动）
=== SCRIPT CHECK ===
#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
=== API STATUS ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788238840.9172647, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "93fcd10c5a07cf882e7bfbb7a3ee6da122e3a19c", "deployed_at": "2026-09-01T05:00:07Z"}OK
=== CLOUDFLARED PROCESS ===
root     2250190  0.9  1.9 1360028 40012 ?       Sl   13:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2250300  1.2  2.0 1294676 40268 ?       Sl   13:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-09-01T05:00:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-09-01T05:00:27Z INF Registered tunnel connection connIndex=0 connection=6d570734-d7a6-4b17-ab29-44c698a19aac event=0 ip=198.41.200.23 location=sjc05 protocol=quic
2026-09-01T05:00:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-09-01T05:00:28Z INF Registered tunnel connection connIndex=1 connection=fafca5c7-b8bd-4bba-9d23-96b0a618b481 event=0 ip=198.41.192.57 location=lax05 protocol=quic
2026-09-01T05:00:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
2026-09-01T05:00:29Z INF Registered tunnel connection connIndex=2 connection=6b59a6e8-7509-4a30-a2a0-0e3ea889efb5 event=0 ip=198.41.192.7 location=lax08 protocol=quic
2026-09-01T05:00:29Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=3 event=0 ip=198.41.200.33
2026-09-01T05:00:30Z INF Registered tunnel connection connIndex=3 connection=48e0f21c-ddb0-4d01-8b10-f8590c6de7c5 event=0 ip=198.41.200.33 location=sjc11 protocol=quic
2026-09-01T05:00:34Z INF +-------------------------------------------------------------------------------------+
2026-09-01T05:00:34Z INF |                               CONNECTIVITY PRE-CHECKS                               |
2026-09-01T05:00:34Z INF +-------------------------------------------------------------------------------------+
2026-09-01T05:00:34Z INF |  COMPONENT         TARGET                     STATUS  DETAILS                       |
2026-09-01T05:00:34Z INF |  DNS Resolution    region1.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-01T05:00:34Z INF |  DNS Resolution    region2.v2.argotunnel.com  PASS    DNS Resolved successfully     |
2026-09-01T05:00:34Z INF |  UDP Connectivity  region1.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-01T05:00:34Z INF |  UDP Connectivity  region2.v2.argotunnel.com  PASS    QUIC connection successful    |
2026-09-01T05:00:34Z INF |  TCP Connectivity  region1.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-01T05:00:34Z INF |  TCP Connectivity  region2.v2.argotunnel.com  PASS    HTTP/2 connection successful  |
2026-09-01T05:00:34Z INF |  Cloudflare API    api.cloudflare.com:443     PASS    API is reachable              |
2026-09-01T05:00:34Z INF |                                                                                     |
2026-09-01T05:00:34Z INF |  SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.  |
2026-09-01T05:00:34Z INF +-------------------------------------------------------------------------------------+
2026-09-01T05:00:34Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=0fa67f45-be0c-4843-ad7a-2e9adc41796d status=pass target=region1.v2.argotunnel.com
2026-09-01T05:00:34Z INF precheck component="DNS Resolution" details="DNS Resolved successfully" run_id=0fa67f45-be0c-4843-ad7a-2e9adc41796d status=pass target=region2.v2.argotunnel.com
2026-09-01T05:00:34Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=0fa67f45-be0c-4843-ad7a-2e9adc41796d status=pass target=region1.v2.argotunnel.com
2026-09-01T05:00:34Z INF precheck component="UDP Connectivity" details="QUIC connection successful" run_id=0fa67f45-be0c-4843-ad7a-2e9adc41796d status=pass target=region2.v2.argotunnel.com
2026-09-01T05:00:34Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=0fa67f45-be0c-4843-ad7a-2e9adc41796d status=pass target=region1.v2.argotunnel.com
2026-09-01T05:00:34Z INF precheck component="TCP Connectivity" details="HTTP/2 connection successful" run_id=0fa67f45-be0c-4843-ad7a-2e9adc41796d status=pass target=region2.v2.argotunnel.com
2026-09-01T05:00:34Z INF precheck component="Cloudflare API" details="API is reachable" run_id=0fa67f45-be0c-4843-ad7a-2e9adc41796d status=pass target=api.cloudflare.com:443
2026-09-01T05:00:34Z INF precheck complete hard_fail=false run_id=0fa67f45-be0c-4843-ad7a-2e9adc41796d suggested_protocol=quic
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[13:00:05] Time: Tue Sep  1 01:00:05 PM CST 2026
[13:00:05] User: root (UID: 0)
[13:00:05] === STEP 1: 启动 API (端口 8450) ===
[13:00:07] HEAD: 93fcd10c -> 93fcd10c
[13:00:07] commit 对比: 运行进程=68a497f5ce491bf1b370f98274cda20eadcc5ae4 / 磁盘=93fcd10c5a07cf882e7bfbb7a3ee6da122e3a19c
[13:00:07] 运行进程落后于磁盘代码（commit 不一致）-> 标记重启
[13:00:07] 需要重新加载代码 -> 重启 API
[13:00:08] 强制重启 Python API 进程（当前commit=68a497f5ce491bf1b370f98274cda20eadcc5ae4 目标=93fcd10c5a07cf882e7bfbb7a3ee6da122e3a19c）
[13:00:18] API 状态: OK
[13:00:18] === STEP 2: 安装 cloudflared ===
[13:00:18] cloudflared 安装路径: /usr/local/bin/cloudflared
[13:00:18] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:00:18] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[13:00:18] === STEP 3: 检查认证方式 ===
[13:00:18] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[13:00:18] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[13:00:18] 检查现有 tunnel...
[13:00:20] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                                                            
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax07, 1xlax08, 1xlax10, 1xlax11, 1xsjc05, 1xsjc07, 1xsjc08, 1xsjc11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                                                        
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                                                        
2026-09-01T05:00:20Z WRN Your version 2026.7.3 is outdated. We recommend upgrading it to 2026.8.3
[13:00:20] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:00:20] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[13:00:20] 凭证文件存在
[13:00:20] 创建 config.yml...
[13:00:20] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[13:00:20] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:00:21] DNS 路由结果: 2026-09-01T05:00:21Z INF aishield.tools.healthlens.cc is already configured to route to your tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
[13:00:21] === STEP 5: 更新 DNS (API) ===
[13:00:21] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:00:22] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
DNS 更新: OK
[13:00:23] 设置 SSL 模式为 Full...
SSL: 跳过
[13:00:24] === STEP 6: 启动 Tunnel ===
[13:00:27] 启动 Named Tunnel (cert 模式)...
[13:00:27] 使用 config: /root/.cloudflared/config.yml
[13:00:27] cloudflared PID: 2250190
[13:00:29] Tunnel 连接已建立!
[13:00:29] --- cloudflared 日志 (最后 15 行) ---
2026-09-01T05:00:27Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-09-01T05:00:27Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-09-01T05:00:27Z INF cloudflared will not automatically update if installed by a package manager.
2026-09-01T05:00:27Z INF Generated Connector ID: aef83e26-e63a-4c9d-a059-e0057410cca4
2026-09-01T05:00:27Z INF Initial protocol quic
2026-09-01T05:00:27Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-01T05:00:27Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-01T05:00:27Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-09-01T05:00:27Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-09-01T05:00:27Z INF Starting metrics server on 127.0.0.1:20241/metrics
2026-09-01T05:00:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.200.23
2026-09-01T05:00:27Z INF Registered tunnel connection connIndex=0 connection=6d570734-d7a6-4b17-ab29-44c698a19aac event=0 ip=198.41.200.23 location=sjc05 protocol=quic
2026-09-01T05:00:27Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.192.57
2026-09-01T05:00:28Z INF Registered tunnel connection connIndex=1 connection=fafca5c7-b8bd-4bba-9d23-96b0a618b481 event=0 ip=198.41.192.57 location=lax05 protocol=quic
2026-09-01T05:00:28Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.192.7
[13:00:29] === STEP 7: 持久化 ===
[13:00:29] systemd 服务已配置
[13:00:29] Cron 保活已设置
[13:00:29] === STEP 8: 验证 ===
[13:00:29] --- API (localhost:8450) ---
 OK
[13:00:29] --- cloudflared 进程 ---
root     2250190  4.5  1.9 1359708 38512 ?       Sl   13:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2250300  0.0  1.3 1292484 27492 ?       Sl   13:00   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[13:00:29] --- aishield.tools ---
 OK
[13:00:32] --- DNS CNAME ---
[13:00:32] --- DNS A ---
104.21.81.46
172.67.188.44
[13:00:32] === 部署汇总 ===
[13:00:32] Tunnel Mode: cert
[13:00:32] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[13:00:32] API: http://localhost:8450
[13:00:32] 域名: https://aishield.tools
[13:00:32] cloudflared: /usr/local/bin/cloudflared
[13:00:32] PID: 2250190
[13:00:32] Config: /root/.cloudflared/config.yml
[13:00:32] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[13:00:32] 状态: Named Tunnel (cert 模式) 已配置
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2026-09-01 13:00:29 CST; 11s ago
   Main PID: 2250294 (start-tunnel.sh)
      Tasks: 9 (limit: 2216)
     Memory: 18.4M
        CPU: 148ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2250294 /bin/bash /opt/start-tunnel.sh
             └─2250300 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2249866,fd=3))                                                    
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
Time: Tue Sep  1 05:00:52 UTC 2026

=== curl test (aishield.tools) ===
{"status": "ok", "version": "4.3.0", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 228, "rules_breakdown": {"static": 204, "generated": 9, "radar": 15, "total": 228}, "uptime": 1788238853.2586436, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup", "commit": "93fcd10c5a07cf882e7bfbb7a3ee6da122e3a19c", "deployed_at": "2026-09-01T05:00:07Z"}
=== DNS lookup ===
172.67.188.44
104.21.81.46

=== DNS CNAME check ===
