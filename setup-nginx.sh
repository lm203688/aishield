#!/bin/bash
# ════════════════════════════════════════════════════════
#  AIShield Nginx 一键配置脚本
#  用途: 配置 Nginx 反向代理 80 → 8450
#  前提: Cloudflare SSL 已改为 Flexible 模式
#  使用: sudo bash setup-nginx.sh
# ════════════════════════════════════════════════════════

set -e

echo "═══════════════════════════════════════"
echo "  AIShield Nginx 配置脚本"
echo "═══════════════════════════════════════"

# 0. 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请用 sudo 运行: sudo bash setup-nginx.sh"
    exit 1
fi

# 1. 检查 Nginx 是否安装
echo ""
echo "🔍 检查 Nginx..."
if ! command -v nginx &> /dev/null; then
    echo "📦 安装 Nginx..."
    apt-get update -qq && apt-get install -y -qq nginx
else
    echo "✅ Nginx 已安装 ($(nginx -v 2>&1))"
fi

# 2. 检查 AIShield API 是否在运行
echo ""
echo "🔍 检查 AIShield API (端口 8450)..."
if curl -sf http://127.0.0.1:8450/api/v1/health > /dev/null 2>&1; then
    echo "✅ AIShield API 运行中"
else
    echo "⚠️  AIShield API 未运行！请先启动: cd /opt/aishield && PORT=8450 python3 api/server.py &"
    echo "   继续配置 Nginx（API 可稍后启动）..."
fi

# 3. 写入 Nginx 配置
echo ""
echo "📝 写入 Nginx 配置..."
cat > /etc/nginx/sites-available/aishield << 'NGINX_CONF'
# AIShield Nginx 反向代理配置
# Cloudflare SSL: Flexible → Nginx 80 → API 8450

map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    listen [::]:80;
    server_name aishield.tools www.aishield.tools _;

    client_max_body_size 50m;

    proxy_connect_timeout 30s;
    proxy_send_timeout    120s;
    proxy_read_timeout    120s;

    # 信任 Cloudflare IP
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 131.0.72.0/22;
    real_ip_header CF-Connecting-IP;

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
NGINX_CONF
echo "✅ 配置已写入 /etc/nginx/sites-available/aishield"

# 4. 启用站点
echo ""
echo "🔗 启用站点..."
ln -sf /etc/nginx/sites-available/aishield /etc/nginx/sites-enabled/aishield

# 禁用默认站点（避免冲突）
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm -f /etc/nginx/sites-enabled/default
    echo "✅ 已禁用默认站点"
fi

# 5. 测试 Nginx 配置
echo ""
echo "🧪 测试 Nginx 配置..."
if nginx -t 2>&1; then
    echo "✅ Nginx 配置测试通过"
else
    echo "❌ Nginx 配置测试失败！"
    exit 1
fi

# 6. 重载 Nginx
echo ""
echo "🔄 重载 Nginx..."
systemctl reload nginx
systemctl enable nginx
echo "✅ Nginx 已重载并设为开机启动"

# 7. 验证
echo ""
echo "🏥 验证..."
echo ""
echo "── 本地测试 (Nginx → API) ──"
if curl -sf http://127.0.0.1/api/v1/health 2>/dev/null; then
    echo ""
    echo "✅ 本地 Nginx 代理正常！"
else
    echo "⚠️  本地测试失败，请检查 AIShield API 是否运行"
fi

echo ""
echo "── Cloudflare 测试 ──"
if curl -sf https://aishield.tools/api/v1/health 2>/dev/null; then
    echo ""
    echo "✅ Cloudflare → Nginx → API 全链路正常！"
else
    echo "⚠️  Cloudflare 测试失败"
    echo "   请确认:"
    echo "   1. Cloudflare SSL 模式已改为 'Flexible'"
    echo "   2. 等待 1-2 分钟让配置生效"
    echo "   3. 再次测试: curl https://aishield.tools/api/v1/health"
fi

echo ""
echo "═══════════════════════════════════════"
echo "  🎉 配置完成！"
echo "═══════════════════════════════════════"
