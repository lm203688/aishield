#!/bin/bash
# ════════════════════════════════════════════════════════
#  AIShield Nginx 全面修复脚本
#  清理所有旧配置，设置正确的反向代理
# ════════════════════════════════════════════════════════

set -e

echo "═══════════════════════════════════════"
echo "  AIShield Nginx 全面修复"
echo "═══════════════════════════════════════"

# 0. 检查 root
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请用 sudo 运行: sudo bash fix-nginx.sh"
    exit 1
fi

# 1. 诊断：查看当前端口占用
echo ""
echo "🔍 诊断端口占用..."
echo "── 端口 80 ──"
ss -tlnp | grep ':80 ' || echo "  (无监听)"
echo "── 端口 443 ──"
ss -tlnp | grep ':443 ' || echo "  (无监听)"
echo "── 端口 8450 ──"
ss -tlnp | grep ':8450 ' || echo "  (无监听)"

# 2. 诊断：检查 API 是否运行
echo ""
echo "🔍 检查 AIShield API (8450)..."
if curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
    echo ""
    echo "✅ API 正常运行"
else
    echo "⚠️  API 未运行，尝试启动..."
    cd /opt/aishield || cd ~/aishield
    pkill -f "api/server.py" 2>/dev/null || true
    sleep 1
    export PORT=8450
    nohup python3 api/server.py > /tmp/aishield-api.log 2>&1 &
    sleep 3
    if curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
        echo "✅ API 已启动"
    else
        echo "❌ API 启动失败！查看日志："
        tail -20 /tmp/aishield-api.log 2>/dev/null
        echo "尝试通过 Docker 启动..."
        if command -v docker &> /dev/null; then
            cd /opt/aishield || cd ~/aishield
            docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null || true
            sleep 5
            if curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
                echo "✅ API 通过 Docker 启动成功"
            else
                echo "❌ API 仍然无法启动"
            fi
        fi
    fi
fi

# 3. 清理所有旧的 Nginx 配置
echo ""
echo "🧹 清理旧 Nginx 配置..."

# 列出当前所有配置
echo "── 当前 sites-enabled ──"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "  (目录不存在)"
echo "── 当前 conf.d ──"
ls -la /etc/nginx/conf.d/ 2>/dev/null || echo "  (目录不存在)"

# 备份并清理
mkdir -p /etc/nginx/sites-backup
if [ -d /etc/nginx/sites-enabled ]; then
    for f in /etc/nginx/sites-enabled/*; do
        [ -e "$f" ] || continue
        mv "$f" /etc/nginx/sites-backup/ 2>/dev/null || rm -f "$f"
        echo "  已备份: $(basename $f)"
    done
fi
if [ -d /etc/nginx/conf.d ]; then
    for f in /etc/nginx/conf.d/*.conf; do
        [ -e "$f" ] || continue
        mv "$f" /etc/nginx/sites-backup/ 2>/dev/null || rm -f "$f"
        echo "  已备份: $(basename $f)"
    done
fi

# 4. 写入新的干净配置
echo ""
echo "📝 写入新 Nginx 配置..."

# 确保目录存在
mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled /etc/nginx/conf.d

cat > /etc/nginx/sites-available/aishield << 'NGINX_CONF'
# AIShield 反向代理 - 唯一配置
# Cloudflare Flexible: HTTP 80 → API 8450

map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name aishield.tools www.aishield.tools healthlens.cc www.healthlens.cc _;

    client_max_body_size 50m;

    proxy_connect_timeout 10s;
    proxy_send_timeout    60s;
    proxy_read_timeout    60s;

    # ACME challenge (Let's Encrypt)
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # API 健康检查
    location /api/v1/health {
        proxy_pass http://127.0.0.1:8450;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 所有其他请求
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

# 启用
ln -sf /etc/nginx/sites-available/aishield /etc/nginx/sites-enabled/aishield

# 确保 nginx.conf 包含 sites-enabled
if ! grep -q "sites-enabled" /etc/nginx/nginx.conf; then
    echo "⚠️  nginx.conf 未包含 sites-enabled，直接写入 conf.d..."
    cp /etc/nginx/sites-available/aishield /etc/nginx/conf.d/aishield.conf
fi

# 确保 conf.d 为空（避免冲突）
rm -f /etc/nginx/conf.d/*.conf 2>/dev/null
cp /etc/nginx/sites-available/aishield /etc/nginx/conf.d/aishield.conf

echo "✅ 配置已写入"

# 5. 测试配置
echo ""
echo "🧪 测试 Nginx 配置..."
if nginx -t 2>&1; then
    echo "✅ 配置测试通过"
else
    echo "❌ 配置测试失败！尝试回退..."
    # 如果失败，恢复最小配置
    cat > /etc/nginx/conf.d/aishield.conf << 'FALLBACK'
server {
    listen 80 default_server;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8450;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
FALLBACK
    nginx -t 2>&1 && echo "✅ 回退配置通过" || { echo "❌ 回退也失败"; exit 1; }
fi

# 6. 重载 Nginx
echo ""
echo "🔄 重载 Nginx..."
systemctl restart nginx 2>/dev/null || service nginx restart 2>/dev/null || nginx -s reload
systemctl enable nginx 2>/dev/null || true
echo "✅ Nginx 已重启"

# 7. 验证
echo ""
echo "🏥 验证结果..."
echo ""
echo "── 1. API 直连 (8450) ──"
curl -sf http://127.0.0.1:8450/api/v1/health && echo " ✅" || echo " ❌"

echo ""
echo "── 2. Nginx 代理 (localhost:80) ──"
curl -sf http://127.0.0.1/api/v1/health && echo " ✅" || echo " ❌"

echo ""
echo "── 3. Nginx 代理 (localhost:80, Host: aishield.tools) ──"
curl -sf -H "Host: aishield.tools" http://127.0.0.1/api/v1/health && echo " ✅" || echo " ❌"

echo ""
echo "── 4. Nginx 配置文件 ──"
cat /etc/nginx/conf.d/aishield.conf | head -5

echo ""
echo "── 5. Nginx 进程 ──"
ps aux | grep nginx | grep -v grep | head -3

echo ""
echo "═══════════════════════════════════════"
echo "  修复完成！"
echo "  下一步："
echo "  1. 确认 Cloudflare SSL = Flexible"
echo "  2. 等待 1-2 分钟 DNS 传播"
echo "  3. 测试: curl https://aishield.tools/api/v1/health"
echo "═══════════════════════════════════════"
