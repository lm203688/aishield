=== DIAGNOSTIC ===
Time: Mon Aug 10 02:03:32 PM CST 2026
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
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1786341812.383809, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== CLOUDFLARED PROCESS ===
root     2561480  3.3  1.9 1294676 38996 ?       Sl   14:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== CLOUDFLARED LOG (last 30 lines) ===
2026-08-10T06:03:30Z INF Starting tunnel tunnelID=0c39bcfb-0c96-4858-9025-d54131e062ec
2026-08-10T06:03:30Z INF Version 2026.7.3 (Checksum 9d71c677db00134c1bd4144b7783486b654ad281b1ea62b4972098d19f770f17)
2026-08-10T06:03:30Z INF GOOS: linux, GOVersion: go1.26.4, GoArch: amd64
2026-08-10T06:03:30Z INF Settings: map[config:/root/.cloudflared/config.yml cred-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json credentials-file:/root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json]
2026-08-10T06:03:30Z INF cloudflared will not automatically update if installed by a package manager.
2026-08-10T06:03:30Z INF Generated Connector ID: 46727aec-5095-4cd5-afd8-9ee4a3d93121
2026-08-10T06:03:30Z INF Initial protocol quic
2026-08-10T06:03:30Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:03:30Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:03:30Z INF ICMP proxy will use 10.0.0.11 as source for IPv4
2026-08-10T06:03:30Z INF ICMP proxy will use fe80::5054:ff:fe13:e120 in zone eth0 as source for IPv6
2026-08-10T06:03:30Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-10T06:03:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:30Z INF Registered tunnel connection connIndex=0 connection=9915a21e-b47f-4e86-a750-7a35954498eb event=0 ip=198.41.192.27 location=lax11 protocol=quic
2026-08-10T06:03:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-08-10T06:03:31Z INF Initiating graceful shutdown due to signal terminated ...
2026-08-10T06:03:31Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:31Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:31Z INF Registered tunnel connection connIndex=1 connection=c6527550-3a95-407c-9f79-d2e03e490873 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-10T06:03:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-10T06:03:31Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.200.53
2026-08-10T06:03:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.53
2026-08-10T06:03:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.53
2026-08-10T06:03:31Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.53
=== DEPLOY LOG ===
=== AIShield Named Tunnel Deployment ===
[14:03:22] Time: Mon Aug 10 02:03:22 PM CST 2026
[14:03:22] User: root (UID: 0)
[14:03:22] === STEP 1: 启动 API (端口 8450) ===
[14:03:22] API 已在运行
[14:03:22] API 状态: OK
[14:03:22] === STEP 2: 安装 cloudflared ===
[14:03:22] cloudflared 安装路径: /usr/local/bin/cloudflared
[14:03:22] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:03:22] systemd 服务已配置
[14:03:22] Cron 保活已设置
[14:03:22] === STEP 8: 验证 ===
[14:03:22] --- API (localhost:8450) ---
 OK
[14:03:22] --- cloudflared 进程 ---
[14:03:22] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:03:22] === STEP 3: 检查认证方式 ===
[14:03:22] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
root     2560742  3.6  1.9 1294676 39556 ?       Sl   14:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2560766  4.0  1.9 1294092 38904 ?       Sl   14:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
root     2561086  0.0  1.5 1292812 31576 ?       Rl   14:03   0:00 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
[14:03:22] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[14:03:22] --- aishield.tools ---
[14:03:22] 检查现有 tunnel...
[14:03:23] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[14:03:23] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS                        
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 5xlax01, 1xlax05, 1xlax09, 2xlax11 
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z                                    
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z                                    
[14:03:23] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:03:23] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[14:03:23] 凭证文件存在
[14:03:23] 创建 config.yml...
[14:03:23] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[14:03:23] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
 OK
[14:03:24] --- DNS CNAME ---
[14:03:24] --- DNS A ---
104.21.81.46
172.67.188.44
[14:03:24] === 部署汇总 ===
[14:03:24] Tunnel Mode: cert
[14:03:24] Tunnel ID: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:03:24] API: http://localhost:8450
[14:03:24] 域名: https://aishield.tools
[14:03:24] cloudflared: /usr/local/bin/cloudflared
[14:03:24] PID: 2560766
[14:03:24] Config: /root/.cloudflared/config.yml
[14:03:24] CNAME: 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:03:24] 状态: Named Tunnel (cert 模式) 已配置
DNS 更新: OK
[14:03:25] 设置 SSL 模式为 Full...
SSL: 跳过
[14:03:26] === STEP 6: 启动 Tunnel ===
[14:03:26] DNS 路由结果: 
[14:03:26] === STEP 5: 更新 DNS (API) ===
[14:03:27] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:03:28] 更新现有 DNS 记录 (ID: fdc3eba7fdb90436809fe05358eb0f3a)
[14:03:28] API 已在运行
[14:03:28] API 状态: OK
[14:03:28] === STEP 2: 安装 cloudflared ===
[14:03:28] cloudflared 安装路径: /usr/local/bin/cloudflared
[14:03:29] cloudflared 已安装: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:03:29] cloudflared 版本: cloudflared version 2026.7.3 (built 2026-07-23-09:58 UTC)
[14:03:29] === STEP 3: 检查认证方式 ===
[14:03:29] cert.pem 存在: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
[14:03:29] === STEP 4: 使用 cert.pem 创建 Named Tunnel ===
[14:03:29] 检查现有 tunnel...
[14:03:29] 启动 Named Tunnel (cert 模式)...
[14:03:29] 使用 config: /root/.cloudflared/config.yml
[14:03:29] cloudflared PID: 2561480
DNS 更新: OK
[14:03:30] 设置 SSL 模式为 Full...
[14:03:31] 现有 tunnel 列表:
You can obtain more detailed information for each tunnel with `cloudflared tunnel info <name/uuid>`
ID                                   NAME            CREATED              CONNECTIONS 
0c39bcfb-0c96-4858-9025-d54131e062ec aishield-tunnel 2026-07-30T23:21:20Z 1xlax11     
a956a3fe-ad15-4f1e-8499-8dad27859d3d aishield.tools  2026-06-27T14:20:27Z             
aa3f86b8-01f4-4ce0-83a8-5512219f9003 healthlens      2026-07-28T03:03:32Z             
[14:03:31] Tunnel 已存在: 0c39bcfb-0c96-4858-9025-d54131e062ec
[14:03:31] 凭证文件: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json
[14:03:31] 凭证文件存在
[14:03:31] 创建 config.yml...
[14:03:31] config.yml 已创建:
tunnel: 0c39bcfb-0c96-4858-9025-d54131e062ec
credentials-file: /root/.cloudflared/0c39bcfb-0c96-4858-9025-d54131e062ec.json

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
[14:03:31] 路由 DNS: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
SSL: 跳过
[14:03:31] === STEP 6: 启动 Tunnel ===
[14:03:31] DNS 路由结果: 
[14:03:31] === STEP 5: 更新 DNS (API) ===
[14:03:31] CNAME: aishield.tools -> 0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com
[14:03:31] Tunnel 连接已建立!
[14:03:31] --- cloudflared 日志 (最后 15 行) ---
2026-08-10T06:03:30Z INF Starting metrics server on 127.0.0.1:20242/metrics
2026-08-10T06:03:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:30Z INF Registered tunnel connection connIndex=0 connection=9915a21e-b47f-4e86-a750-7a35954498eb event=0 ip=198.41.192.27 location=lax11 protocol=quic
2026-08-10T06:03:30Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=1 event=0 ip=198.41.200.53
2026-08-10T06:03:31Z INF Initiating graceful shutdown due to signal terminated ...
2026-08-10T06:03:31Z ERR failed to run the datagram handler error="context canceled" connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:31Z INF Retrying connection in up to 1s connIndex=0 event=0 ip=198.41.192.27
2026-08-10T06:03:31Z INF Registered tunnel connection connIndex=1 connection=c6527550-3a95-407c-9f79-d2e03e490873 event=0 ip=198.41.200.53 location=lax01 protocol=quic
2026-08-10T06:03:31Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveID(65074) CurveP256] connIndex=2 event=0 ip=198.41.200.63
2026-08-10T06:03:31Z ERR failed to run the datagram handler error="context canceled" connIndex=1 event=0 ip=198.41.200.53
2026-08-10T06:03:31Z ERR failed to serve tunnel connection error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.53
2026-08-10T06:03:31Z ERR Serve tunnel error error="accept stream listener encountered a failure while serving" connIndex=1 event=0 ip=198.41.200.53
2026-08-10T06:03:31Z INF Retrying connection in up to 1s connIndex=1 event=0 ip=198.41.200.53
[14:03:31] === STEP 7: 持久化 ===
=== TUNNEL INFO ===
Tunnel ID: NOT SET
Token File: NOT SET
cert.pem: -rw------- 1 root root 282 Jul 28 11:02 /root/.cloudflared/cert.pem
=== SYSTEMD STATUS ===
● cloudflared-tunnel.service - Cloudflare Named Tunnel for AIShield
     Loaded: loaded (/etc/systemd/system/cloudflared-tunnel.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-08-10 14:03:32 CST; 21ms ago
   Main PID: 2561745 (start-tunnel.sh)
      Tasks: 6 (limit: 2216)
     Memory: 9.5M
        CPU: 10ms
     CGroup: /system.slice/cloudflared-tunnel.service
             ├─2561745 /bin/bash /opt/start-tunnel.sh
             └─2561746 /usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
=== PORTS ===
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                    
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
Time: Mon Aug 10 06:03:32 UTC 2026

=== curl test (aishield.tools) ===
<!DOCTYPE html>



 <html class="no-js" lang="en-US"> 
<head>
<title>Cloudflare Tunnel error | aishield.tools | Cloudflare</title>
<meta charset="UTF-8" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="X-UA-Compatible" content="IE=Edge" />
<meta name="robots" content="noindex, nofollow" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link rel="stylesheet" id="cf_styles-css" href="/cdn-cgi/styles/main.css" />


<script>
(function(){if(document.addEventListener&&window.XMLHttpRequest&&JSON&&JSON.stringify){var e=function(a){var c=document.getElementById("error-feedback-survey"),d=document.getElementById("error-feedback-success"),b=new XMLHttpRequest;a={event:"feedback clicked",properties:{errorCode:1033,helpful:a,version:1}};b.open("POST","https://sparrow.cloudflare.com/api/v1/event");b.setRequestHeader("Content-Type","application/json");b.setRequestHeader("Sparrow-Source-Key","c771f0e4b54944bebf4261d44bd79a1e");
b.send(JSON.stringify(a));c.classList.add("feedback-hidden");d.classList.remove("feedback-hidden")};document.addEventListener("DOMContentLoaded",function(){var a=document.getElementById("error-feedback"),c=document.getElementById("feedback-button-yes"),d=document.getElementById("feedback-button-no");"classList"in a&&(a.classList.remove("feedback-hidden"),c.addEventListener("click",function(){e(!0)}),d.addEventListener("click",function(){e(!1)}))})}})();
</script>

<script defer src="https://performance.radar.cloudflare.com/beacon.js"></script>
</head>
<body>
  <div id="cf-wrapper">
    <div class="cf-alert cf-alert-error cf-cookie-error hidden" id="cookie-alert" data-translate="enable_cookies">Please enable cookies.</div>
    <div id="cf-error-details" class="p-0">
      <header class="mx-auto pt-10 lg:pt-6 lg:px-8 w-240 lg:w-full mb-15 antialiased">
         <h1 class="inline-block md:block mr-2 md:mb-2 font-light text-60 md:text-3xl text-black-dark leading-tight">
           <span data-translate="error">Error</span>
           <span>1033</span>
         </h1>
         <span class="inline-block md:block heading-ray-id font-mono text-15 lg:text-sm lg:leading-relaxed">Ray ID: a28ccc4bca8bcb91-LAX &bull;</span>
         <span class="inline-block md:block heading-ray-id font-mono text-15 lg:text-sm lg:leading-relaxed">2026-08-10 06:03:33 UTC</span>
        <h2 class="text-gray-600 leading-1.3 text-3xl lg:text-2xl font-light">Cloudflare Tunnel error</h2>
      </header>

      <section class="w-240 lg:w-full mx-auto mb-8 lg:px-8">
          <div id="what-happened-section" class="w-1/2 md:w-full">
            <h2 class="text-3xl leading-tight font-normal mb-4 text-black-dark antialiased" data-translate="what_happened">What happened?</h2>
            <p>You've requested a page on a website (aishield.tools) that is on the <a href="https://www.cloudflare.com/5xx-error-landing/" target="_blank">Cloudflare</a> network. The host (aishield.tools) is configured as a Cloudflare Tunnel, and Cloudflare is currently unable to resolve it.
            
          </div>

          
          <div id="resolution-copy-section" class="w-1/2 mt-6 text-15 leading-normal">
            <h2 class="text-3xl leading-tight font-normal mb-4 text-black-dark antialiased" data-translate="what_can_i_do">What can I do?</h2>
            <p><strong>If you are a visitor of this website:</strong><br />Please try again in a few minutes.</p><p><strong>If you are the owner of this website:</strong><br />Ensure that cloudflared is running and can reach the network. You may wish to enable <a rel="noopener noreferrer" href="https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/routing-to-tunnel/lb/">load balancing</a> for your tunnel.</p>
          </div>
          
      </section>

      <div class="feedback-hidden py-8 text-center" id="error-feedback">
    <div id="error-feedback-survey" class="footer-line-wrapper">
        Was this page helpful?
        <button class="border border-solid bg-white cf-button cursor-pointer ml-4 px-4 py-2 rounded" id="feedback-button-yes" type="button">Yes</button>
        <button class="border border-solid bg-white cf-button cursor-pointer ml-4 px-4 py-2 rounded" id="feedback-button-no" type="button">No</button>
    </div>
    <div class="feedback-success feedback-hidden" id="error-feedback-success">
        Thank you for your feedback!
    </div>
</div>


      <div class="cf-error-footer cf-wrapper w-240 lg:w-full py-10 sm:py-4 sm:px-8 mx-auto text-center sm:text-left border-solid border-0 border-t border-gray-300">
  <p class="text-13">
  <span class="cf-footer-item sm:block sm:mb-1">Cloudflare Ray ID: <strong class="font-semibold">a28ccc4bca8bcb91-LAX</strong></span>
    <span class="cf-footer-separator sm:hidden">&bull;</span>
    <span id="cf-footer-item-ip" class="cf-footer-item hidden sm:block sm:mb-1">
      Your IP:
      <button type="button" id="cf-footer-ip-reveal" class="cf-footer-ip-reveal-btn">Click to reveal</button>
      <span class="hidden" id="cf-footer-ip">57.154.4.54</span>
      <span class="cf-footer-separator sm:hidden">&bull;</span>
    </span>
    <span class="cf-footer-item sm:block sm:mb-1"><span>Performance &amp; security by</span> <a rel="noopener noreferrer" href="https://www.cloudflare.com/5xx-error-landing" id="brand_link" target="_blank">Cloudflare</a></span>
    
  </p>
  <script>(function(){function d(){var b=a.getElementById("cf-footer-item-ip"),c=a.getElementById("cf-footer-ip-reveal");b&&"classList"in b&&(b.classList.remove("hidden"),c.addEventListener("click",function(){c.classList.add("hidden");a.getElementById("cf-footer-ip").classList.remove("hidden")}))}var a=document;document.addEventListener&&a.addEventListener("DOMContentLoaded",d)})();</script>
</div>


    </div>
  </div>

  <script>
  window._cf_translation = {};
  
  
</script>

</body>
</html>



=== DNS lookup ===
104.21.81.46
172.67.188.44

=== DNS CNAME check ===
