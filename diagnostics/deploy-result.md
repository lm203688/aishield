=== AIShield DIAGNOSTIC ===
Time: Thu Jul 30 00:54:31 UTC 2026
=== nginx -t ===
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
=== PORTS ===
LISTEN 0      511          0.0.0.0:80         0.0.0.0:*    users:(("nginx",pid=3648843,fd=8),("nginx",pid=3648842,fd=8),("nginx",pid=3648841,fd=8))
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                    
LISTEN 0      511          0.0.0.0:443        0.0.0.0:*    users:(("nginx",pid=3648843,fd=6),("nginx",pid=3648842,fd=6),("nginx",pid=3648841,fd=6))
LISTEN 0      511             [::]:80            [::]:*    users:(("nginx",pid=3648843,fd=9),("nginx",pid=3648842,fd=9),("nginx",pid=3648841,fd=9))
LISTEN 0      511             [::]:443           [::]:*    users:(("nginx",pid=3648843,fd=7),("nginx",pid=3648842,fd=7),("nginx",pid=3648841,fd=7))
=== NGINX PROCESS ===
root     3648841  0.0  0.0  10936  1696 ?        Ss   08:54   0:00 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
www-data 3648842  0.0  0.3  11736  7388 ?        S    08:54   0:00 nginx: worker process
www-data 3648843  0.0  0.2  11604  4284 ?        S    08:54   0:00 nginx: worker process
=== NGINX ERROR LOG ===
2026/07/30 05:26:20 [emerg] 3509840#3509840: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:20 [emerg] 3509840#3509840: still could not bind()
2026/07/30 05:26:23 [emerg] 3509892#3509892: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:23 [emerg] 3509892#3509892: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:23 [emerg] 3509892#3509892: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:23 [emerg] 3509892#3509892: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:23 [emerg] 3509892#3509892: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:23 [emerg] 3509892#3509892: still could not bind()
2026/07/30 05:26:25 [emerg] 3509898#3509898: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:25 [emerg] 3509898#3509898: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:25 [emerg] 3509898#3509898: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:25 [emerg] 3509898#3509898: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:25 [emerg] 3509898#3509898: bind() to 0.0.0.0:80 failed (98: Unknown error)
2026/07/30 05:26:25 [emerg] 3509898#3509898: still could not bind()
2026/07/30 08:16:19 [notice] 3617749#3617749: signal process started
2026/07/30 08:16:19 [error] 3617749#3617749: open() "/run/nginx.pid" failed (2: No such file or directory)
2026/07/30 08:23:43 [notice] 3623854#3623854: signal process started
2026/07/30 08:23:43 [error] 3623854#3623854: open() "/run/nginx.pid" failed (2: No such file or directory)
2026/07/30 08:28:43 [notice] 3628478#3628478: signal process started
2026/07/30 08:28:43 [error] 3628478#3628478: open() "/run/nginx.pid" failed (2: No such file or directory)
2026/07/30 08:32:42 [notice] 3631977#3631977: signal process started
2026/07/30 08:32:42 [error] 3631977#3631977: open() "/run/nginx.pid" failed (2: No such file or directory)
2026/07/30 08:39:00 [notice] 3636782#3636782: signal process started
2026/07/30 08:39:00 [error] 3636782#3636782: open() "/run/nginx.pid" failed (2: No such file or directory)
2026/07/30 08:43:32 [notice] 3640310#3640310: signal process started
2026/07/30 08:43:32 [error] 3640310#3640310: open() "/run/nginx.pid" failed (2: No such file or directory)
2026/07/30 08:48:43 [notice] 3644305#3644305: signal process started
2026/07/30 08:48:43 [error] 3644305#3644305: open() "/run/nginx.pid" failed (2: No such file or directory)
2026/07/30 08:54:20 [notice] 3648803#3648803: signal process started
2026/07/30 08:54:20 [error] 3648803#3648803: open() "/run/nginx.pid" failed (2: No such file or directory)
=== SSL TEST ===
depth=0 CN = aishield.tools
verify error:num=18:self-signed certificate
verify return:1
depth=0 CN = aishield.tools
verify return:1
CONNECTED(00000003)
---
Certificate chain
 0 s:CN = aishield.tools
   i:CN = aishield.tools
   a:PKEY: rsaEncryption, 2048 (bit); sigalg: RSA-SHA256
   v:NotBefore: Jul 30 00:54:22 2026 GMT; NotAfter: Jul 27 00:54:22 2036 GMT
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDEzCCAfugAwIBAgIUE4zUaaAtMUTUk0cwZ0lpX9hA2E4wDQYJKoZIhvcNAQEL
BQAwGTEXMBUGA1UEAwwOYWlzaGllbGQudG9vbHMwHhcNMjYwNzMwMDA1NDIyWhcN
MzYwNzI3MDA1NDIyWjAZMRcwFQYDVQQDDA5haXNoaWVsZC50b29sczCCASIwDQYJ
KoZIhvcNAQEBBQADggEPADCCAQoCggEBAJZudIpqbAw24Nb2Ui7BaHn/kVp9GCWR
mHl07/2Sqr9/HN/3Rd5ZK6aY6MYpKFTJ9IIDM+3l4vPhliQKkEvqjyBVbrh44y7A
RYDV9StVkotWJB0G9XnhZkzrsvpDhDTVKMaPPGDpgusNH+E0UZJTCGFKwvNigM57
OoNDwJyBVEAyAnXSt6oef3+dydUq0KxhyYVHoEYWwwifc8csrf0TqtNUOGEXfywv
CHJgnfAgACuqt6irxoWvyDiSM+wGA+L8pPqn+GmTf7kgMUicufugkgHuzC3MewRw
3f731J2vLVFNEMUNYT/ryjKgvSt1CoxbQraVH4gDt9A6CSpIe3ascZsCAwEAAaNT
MFEwHQYDVR0OBBYEFP/tHDiZe4o8AziA7EtKCFS1ivkgMB8GA1UdIwQYMBaAFP/t
HDiZe4o8AziA7EtKCFS1ivkgMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQEL
BQADggEBACwYflF5TkhmaL+oV4gZ4D7wh+ho3rJ7jWInWTB1/AwNnVYp4vflAbFF
Bvmgyte56UiGpX95vgHeehMO0dBlMMfdt0YDDQsthgzT8OrcsyqL9/cb6RrVP7OH
JUhd5yXgPegmmYcaZAUlVcbRPYpxAn91so6erBth9FWh3SqMClZWa/PmVshDqodh
C6ZVYj9Bp+3IrIk4kFGtjTkf3zPMyA1yp0YvM4NVuEOK921GEIkGYISuttIGIgvn
=== CERT CHECK ===
subject=CN = aishield.tools
notBefore=Jul 30 00:54:22 2026 GMT
notAfter=Jul 27 00:54:22 2036 GMT
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785372874.0674229, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
=== NGINX CONF ===
user www-data;
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    access_log /var/log/nginx/access.log;
    sendfile      on;
    keepalive_timeout 65;
    client_max_body_size 50m;

    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    # ── 443 端口: Cloudflare Full 模式通过 443 连接，绕过 80 端口备案拦截 ──
    server {
        listen 443 ssl;
        listen [::]:443 ssl;
        server_name aishield.tools www.aishield.tools healthlens.cc www.healthlens.cc _;

        # 自签证书（Cloudflare Full 模式接受自签证书）
        ssl_certificate     /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         HIGH:!aNULL:!MD5;

        proxy_connect_timeout 5s;
        proxy_send_timeout    60s;
        proxy_read_timeout    60s;

        # 所有请求转发到 AIShield API
        location / {
            proxy_pass http://127.0.0.1:8450;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_buffering off;
            proxy_request_buffering off;
        }
    }

    # ── 80 端口: 仅用于 ACME challenge（如需 Let's Encrypt），其他请求重定向到 443 ──
    server {
        listen 80;
        listen [::]:80;
        server_name aishield.tools www.aishield.tools healthlens.cc www.healthlens.cc _;

        # ACME challenge
        location /.well-known/acme-challenge/ {
            root /var/www/html;
        }

        # 其他请求重定向到 HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }
}

=== HTTPS Test from GitHub Actions Runner ===
Time: Thu Jul 30 00:54:34 UTC 2026

=== curl test (aishield.tools) ===
error code: 525

=== openssl s_client test ===
depth=2 C = US, O = Google Trust Services LLC, CN = GTS Root R4
verify return:1
depth=1 C = US, O = Google Trust Services, CN = WE1
verify return:1
depth=0 CN = aishield.tools
verify return:1
CONNECTED(00000003)
---
Certificate chain
 0 s:CN = aishield.tools
   i:C = US, O = Google Trust Services, CN = WE1
   a:PKEY: id-ecPublicKey, 256 (bit); sigalg: ecdsa-with-SHA256
   v:NotBefore: Jun 27 03:07:45 2026 GMT; NotAfter: Sep 25 03:49:41 2026 GMT
 1 s:C = US, O = Google Trust Services, CN = WE1
   i:C = US, O = Google Trust Services LLC, CN = GTS Root R4
   a:PKEY: id-ecPublicKey, 256 (bit); sigalg: ecdsa-with-SHA384
   v:NotBefore: Dec 13 09:00:00 2023 GMT; NotAfter: Feb 20 14:00:00 2029 GMT
 2 s:C = US, O = Google Trust Services LLC, CN = GTS Root R4
   i:C = BE, O = GlobalSign nv-sa, OU = Root CA, CN = GlobalSign Root CA
   a:PKEY: id-ecPublicKey, 384 (bit); sigalg: RSA-SHA256
   v:NotBefore: Nov 15 03:43:21 2023 GMT; NotAfter: Jan 28 00:00:42 2028 GMT
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDhjCCAyugAwIBAgIQKXZSWSZoZBkTFOU/QUe7ozAKBggqhkjOPQQDAjA7MQsw
CQYDVQQGEwJVUzEeMBwGA1UEChMVR29vZ2xlIFRydXN0IFNlcnZpY2VzMQwwCgYD
VQQDEwNXRTEwHhcNMjYwNjI3MDMwNzQ1WhcNMjYwOTI1MDM0OTQxWjAZMRcwFQYD
VQQDEw5haXNoaWVsZC50b29sczBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABGCW
mpeRJ8jYq5QM212PRn9laqRm9IchMfgU9dWYvh0XAwy+FqFhMBB3YMhY2Rym85L7
qo6QE1HUJ84uShjSJoujggIxMIICLTAOBgNVHQ8BAf8EBAMCB4AwEwYDVR0lBAww
