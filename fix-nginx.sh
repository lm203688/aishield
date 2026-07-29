#!/bin/bash
# ════════════════════════════════════════════════════════
#  AIShield Nginx 全面修复脚本 v2
#  处理 Docker 占用端口 + 配置正确的反向代理
# ════════════════════════════════════════════════════════

set -e

echo "═══════════════════════════════════════"
echo "  AIShield Nginx 全面修复 v2"
echo "═══════════════════════════════════════"

# 0. 检查 root
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请用 sudo 运行"
    exit 1
fi

# 1. 诊断：查看端口占用和 Docker 容器
echo ""
echo "🔍 诊断端口占用..."
echo "── 所有监听端口 ──"
ss -tlnp | grep -E ':(80|443|8450) ' || echo "  (无匹配)"

echo ""
echo "── Docker 容器 ──"
if command -v docker &> /dev/null; then
    docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Names}}" 2>/dev/null || echo "  Docker 未运行"
else
    echo "  Docker 未安装"
fi

# 2. 检查 API 是否运行
echo ""
echo "🔍 检查 AIShield API (8450)..."
if curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
    echo ""
    echo "✅ API 正常运行"
else
    echo "⚠️  API 未运行，尝试启动..."
    cd /opt/aishield || cd ~/aishield
    
    # 尝试 Docker 启动
    if command -v docker &> /dev/null && [ -f docker-compose.yml ]; then
        echo "尝试通过 Docker Compose 启动..."
        docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null || true
        sleep 5
    fi
    
    # 尝试直接启动
    if ! curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
        pkill -f "api/server.py" 2>/dev/null || true
        sleep 1
        export PORT=8450
        nohup python3 api/server.py > /tmp/aishield-api.log 2>&1 &
        sleep 3
    fi
    
    if curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
        echo "✅ API 已启动"
    else
        echo "❌ API 启动失败"
        tail -20 /tmp/aishield-api.log 2>/dev/null
    fi
fi

# 3. 处理 Docker 容器占用端口 80 的问题
echo ""
echo "🔧 处理端口 80 占用..."

# 查找占用端口 80 的 Docker 容器
DOCKER_80_CONTAINER=""
if command -v docker &> /dev/null; then
    DOCKER_80_CONTAINER=$(docker ps --format '{{.Names}}' 2>/dev/null | head -20 | while read name; do
        if docker port "$name" 2>/dev/null | grep -q '80/tcp'; then
            echo "$name"
            break
        fi
    done)
fi

if [ -n "$DOCKER_80_CONTAINER" ]; then
    echo "⚠️  Docker 容器 '$DOCKER_80_CONTAINER' 占用端口 80"
    echo "   停止该容器以释放端口..."
    docker stop "$DOCKER_80_CONTAINER" 2>/dev/null || true
    sleep 2
    echo "✅ 已停止 $DOCKER_80_CONTAINER"
else
    echo "   没有发现 Docker 容器占用端口 80"
fi

# 也检查端口 443
DOCKER_443_CONTAINER=""
if command -v docker &> /dev/null; then
    DOCKER_443_CONTAINER=$(docker ps --format '{{.Names}}' 2>/dev/null | head -20 | while read name; do
        if docker port "$name" 2>/dev/null | grep -q '443/tcp'; then
            echo "$name"
            break
        fi
    done)
fi

if [ -n "$DOCKER_443_CONTAINER" ]; then
    echo "⚠️  Docker 容器 '$DOCKER_443_CONTAINER' 占用端口 443"
    docker stop "$DOCKER_443_CONTAINER" 2>/dev/null || true
    sleep 2
    echo "✅ 已停止 $DOCKER_443_CONTAINER"
fi

# 4. 确保安装 Nginx
echo ""
echo "📦 确保 Nginx 已安装..."
if ! command -v nginx &> /dev/null; then
    apt-get update -qq && apt-get install -y -qq nginx
fi
echo "✅ Nginx: $(nginx -v 2>&1)"

# 5. 清理所有旧 Nginx 配置
echo ""
echo "🧹 清理旧 Nginx 配置..."
mkdir -p /etc/nginx/sites-backup /etc/nginx/sites-available /etc/nginx/sites-enabled /etc/nginx/conf.d

# 备份并清理 sites-enabled
for f in /etc/nginx/sites-enabled/*; do
    [ -e "$f" ] || continue
    cp "$f" /etc/nginx/sites-backup/$(basename $f).bak.$(date +%s) 2>/dev/null || true
    rm -f "$f"
    echo "  清理: $(basename $f)"
done

# 备份并清理 conf.d
for f in /etc/nginx/conf.d/*.conf; do
    [ -e "$f" ] || continue
    cp "$f" /etc/nginx/sites-backup/$(basename $f).bak.$(date +%s) 2>/dev/null || true
    rm -f "$f"
    echo "  清理: $(basename $f)"
done

# 6. 写入新配置
echo ""
echo "📝 写入新 Nginx 配置..."

cat > /etc/nginx/conf.d/aishield.conf << 'NGINX_CONF'
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

    proxy_connect_timeout 5s;
    proxy_send_timeout    60s;
    proxy_read_timeout    60s;

    # ACME challenge (Let's Encrypt)
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

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
NGINX_CONF

# 也写入 sites-available
cp /etc/nginx/conf.d/aishield.conf /etc/nginx/sites-available/aishield
ln -sf /etc/nginx/sites-available/aishield /etc/nginx/sites-enabled/aishield

echo "✅ 配置已写入"

# 7. 确保 nginx.conf 包含 conf.d
if ! grep -q "conf.d" /etc/nginx/nginx.conf; then
    echo "⚠️  nginx.conf 未包含 conf.d，添加..."
    sed -i '/http {/a\    include /etc/nginx/conf.d/*.conf;' /etc/nginx/nginx.conf
fi

# 8. 测试配置
echo ""
echo "🧪 测试 Nginx 配置..."
if nginx -t 2>&1; then
    echo "✅ 配置测试通过"
else
    echo "❌ 配置测试失败！使用最小配置..."
    cat > /etc/nginx/conf.d/aishield.conf << 'FALLBACK'
server {
    listen 80 default_server;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8450;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
FALLBACK
    nginx -t 2>&1 || { echo "❌ 最小配置也失败"; exit 1; }
fi

# 9. 重启 Nginx
echo ""
echo "🔄 重启 Nginx..."
# 先确保停止旧的 Nginx 进程
pkill -f "nginx: master" 2>/dev/null || true
sleep 1
systemctl restart nginx 2>/dev/null || service nginx restart 2>/dev/null || {
    echo "  systemctl 失败，直接启动..."
    nginx
}
systemctl enable nginx 2>/dev/null || true
sleep 2
echo "✅ Nginx 已重启"

# 10. 验证
echo ""
echo "🏥 验证结果..."
echo ""
echo "── 1. 端口监听状态 ──"
ss -tlnp | grep -E ':(80|8450) '

echo ""
echo "── 2. API 直连 (8450) ──"
curl -sf http://127.0.0.1:8450/api/v1/health && echo " ✅" || echo " ❌"

echo ""
echo "── 3. Nginx 代理 (localhost:80) ──"
curl -sf http://127.0.0.1/api/v1/health && echo " ✅" || echo " ❌"

echo ""
echo "── 4. Nginx 代理 (Host: aishield.tools) ──"
curl -sf -H "Host: aishield.tools" http://127.0.0.1/api/v1/health && echo " ✅" || echo " ❌"

echo ""
echo "── 5. Nginx 进程 ──"
ps aux | grep nginx | grep -v grep | head -5

echo ""
echo "── 6. Docker 容器状态 ──"
if command -v docker &> /dev/null; then
    docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}" 2>/dev/null || echo "  (无)"
fi

echo ""
echo "═══════════════════════════════════════"
echo "  修复完成！"
echo "  下一步："
echo "  1. 确认 Cloudflare SSL = Flexible"  
echo "  2. 等待 1-2 分钟 DNS 传播"
echo "  3. 测试: curl https://aishield.tools/api/v1/health"
echo "═══════════════════════════════════════"
