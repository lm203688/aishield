=== AIShield DIAGNOSTIC ===
Time: Thu Jul 30 21:25:57 UTC 2026
=== nginx -t ===
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
=== PORTS ===
LISTEN 0      511          0.0.0.0:80         0.0.0.0:*    users:(("nginx",pid=326084,fd=8),("nginx",pid=326083,fd=8),("nginx",pid=326082,fd=8))
LISTEN 0      5            0.0.0.0:8450       0.0.0.0:*    users:(("python3",pid=2590363,fd=3))                                                 
LISTEN 0      511          0.0.0.0:443        0.0.0.0:*    users:(("nginx",pid=326084,fd=6),("nginx",pid=326083,fd=6),("nginx",pid=326082,fd=6))
LISTEN 0      511             [::]:80            [::]:*    users:(("nginx",pid=326084,fd=9),("nginx",pid=326083,fd=9),("nginx",pid=326082,fd=9))
LISTEN 0      511             [::]:443           [::]:*    users:(("nginx",pid=326084,fd=7),("nginx",pid=326083,fd=7),("nginx",pid=326082,fd=7))
=== NGINX PROCESS ===
root      326082  0.0  0.0  10936  1692 ?        Ss   05:25   0:00 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
www-data  326083  0.0  0.2  11604  4268 ?        S    05:25   0:00 nginx: worker process
www-data  326084  0.1  0.3  11740  7828 ?        S    05:25   0:00 nginx: worker process
=== NGINX ERROR LOG ===
2026/07/31 00:08:48 [crit] 3648842#3648842: *877 SSL_do_handshake() failed (SSL: error:0A00006C:SSL routines::bad key share) while SSL handshaking, client: 165.154.62.35, server: 0.0.0.0:443
2026/07/31 05:25:45 [notice] 325998#325998: signal process started
2026/07/31 05:25:45 [error] 325998#325998: open() "/run/nginx.pid" failed (2: No such file or directory)
=== SSL TEST ===
depth=0 O = "CloudFlare, Inc.", OU = CloudFlare Origin CA, CN = CloudFlare Origin Certificate
verify error:num=20:unable to get local issuer certificate
verify return:1
depth=0 O = "CloudFlare, Inc.", OU = CloudFlare Origin CA, CN = CloudFlare Origin Certificate
verify error:num=21:unable to verify the first certificate
verify return:1
depth=0 O = "CloudFlare, Inc.", OU = CloudFlare Origin CA, CN = CloudFlare Origin Certificate
verify return:1
CONNECTED(00000003)
---
Certificate chain
 0 s:O = "CloudFlare, Inc.", OU = CloudFlare Origin CA, CN = CloudFlare Origin Certificate
   i:C = US, O = "CloudFlare, Inc.", OU = CloudFlare Origin SSL Certificate Authority, L = San Francisco, ST = California
   a:PKEY: rsaEncryption, 2048 (bit); sigalg: RSA-SHA256
   v:NotBefore: Jul 30 21:21:00 2026 GMT; NotAfter: Jul 26 21:21:00 2041 GMT
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIEqDCCA5CgAwIBAgIUaBz+MWoAtsMskUpJGWueRKnBRdQwDQYJKoZIhvcNAQEL
BQAwgYsxCzAJBgNVBAYTAlVTMRkwFwYDVQQKExBDbG91ZEZsYXJlLCBJbmMuMTQw
MgYDVQQLEytDbG91ZEZsYXJlIE9yaWdpbiBTU0wgQ2VydGlmaWNhdGUgQXV0aG9y
aXR5MRYwFAYDVQQHEw1TYW4gRnJhbmNpc2NvMRMwEQYDVQQIEwpDYWxpZm9ybmlh
MB4XDTI2MDczMDIxMjEwMFoXDTQxMDcyNjIxMjEwMFowYjEZMBcGA1UEChMQQ2xv
dWRGbGFyZSwgSW5jLjEdMBsGA1UECxMUQ2xvdWRGbGFyZSBPcmlnaW4gQ0ExJjAk
BgNVBAMTHUNsb3VkRmxhcmUgT3JpZ2luIENlcnRpZmljYXRlMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEAk8Jli3uc15mUjhQ90BVYW4kFY7E5YfE3bQbe
bAVk+a6YYpNECkD5OFOBSuUd2plT7lG/SjbFJ+2FcwnqLjjHtPYMJoTRO1bktLFL
rZr98bV/N4q+Ole9z0DZ1uA7+i0rrvSFfe9CoYhbwxrrF0ggYy1+BqdVPU8xzj1K
p0bQD+aPdvjYT4DiA+V8Su4KdLaLrCrN9n0dh3/E136ZuDkhB2IDec8WuhN/cnOl
iPyLJ7mgW/3BJjAoaAeii48USYKKJ+sRb04wnGzJGXFH5ZhqKP7JfISQ0/eJtw2X
=== CERT CHECK ===
subject=O = "CloudFlare, Inc.", OU = CloudFlare Origin CA, CN = CloudFlare Origin Certificate
notBefore=Jul 30 21:21:00 2026 GMT
notAfter=Jul 26 21:21:00 2041 GMT
=== API STATUS ===
{"status": "ok", "version": "4.2", "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)", "rules_count": 133, "uptime": 1785446759.5780718, "agent_first": true, "openapi": "/openapi.json", "agent_setup": "/api/v1/agent/setup"}OK
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
Time: Thu Jul 30 21:25:59 UTC 2026

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
