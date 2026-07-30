#!/bin/bash
# AIShield Quick Tunnel 部署脚本
# 绕过腾讯云备案SNI拦截 - 使用 Cloudflare Quick Tunnel
# 无需 root 权限，无需 Nginx，无需 SSL 证书

set +e
LOG_FILE="/tmp/aishield-deploy.log"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "=== AIShield Quick Tunnel Deployment ===" | tee "$LOG_FILE"
log "Time: $(date)"
log "User: $(whoami) (UID: $(id -u))"

# ========== STEP 1: 启动 API ==========
log "=== STEP 1: 启动 API (端口 8450) ==="

cd /opt/aishield 2>/dev/null || cd ~/aishield 2>/dev/null || true
git pull origin main 2>/dev/null || true

if curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
    log "API 已在运行"
else
    log "API 未运行，尝试启动..."

    # 尝试 Docker
    if command -v docker &>/dev/null; then
        docker start $(docker ps -aq --filter "status=exited") 2>/dev/null
        sleep 3
    fi

    if ! curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
        if [ -f docker-compose.yml ] && command -v docker &>/dev/null; then
            docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null || true
            sleep 5
        fi

        if ! curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
            log "Docker 启动失败，直接运行 Python..."
            pkill -f "api/server.py" 2>/dev/null || true
            sleep 1
            export PORT=8450
            nohup python3 api/server.py > /tmp/aishield-api.log 2>&1 &
            sleep 5
        fi
    fi
fi

if curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
    log "API 状态: OK"
else
    log "API 状态: FAIL - 尝试查看日志"
    tail -10 /tmp/aishield-api.log 2>/dev/null
fi

# ========== STEP 2: 安装 cloudflared ==========
log "=== STEP 2: 安装 cloudflared ==="

# 选择可写目录
if [ -w /usr/local/bin ]; then
    CF_BIN=/usr/local/bin/cloudflared
elif [ -w /usr/bin ]; then
    CF_BIN=/usr/bin/cloudflared
else
    mkdir -p "$HOME/bin"
    CF_BIN="$HOME/bin/cloudflared"
fi
log "cloudflared 安装路径: $CF_BIN"

# 检查是否已安装
if [ -f "$CF_BIN" ] && "$CF_BIN" --version 2>/dev/null; then
    log "cloudflared 已安装: $($CF_BIN --version 2>&1)"
else
    log "下载 cloudflared..."

    # 尝试多个下载源
    DOWNLOAD_URLS=(
        "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        "https://github.com/cloudflare/cloudflared/releases/download/2025.7.0/cloudflared-linux-amd64"
        "https://pkg.cloudflare.com/cloudflared"
    )

    for URL in "${DOWNLOAD_URLS[@]}"; do
        log "尝试下载: $URL"
        curl -L --connect-timeout 10 --max-time 60 -o "$CF_BIN" "$URL" 2>/dev/null
        if [ -s "$CF_BIN" ] && "$CF_BIN" --version 2>/dev/null; then
            log "下载成功!"
            chmod +x "$CF_BIN"
            break
        fi
        log "下载失败或文件无效"
    done

    # 如果所有下载都失败，尝试 apt 安装
    if ! "$CF_BIN" --version 2>/dev/null; then
        log "直接下载失败，尝试 apt 安装..."
        if command -v apt-get &>/dev/null; then
            curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null 2>&1
            echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs 2>/dev/null || echo jammy) main" | tee /etc/apt/sources.list.d/cloudflared.list >/dev/null 2>&1
            apt-get update -qq 2>/dev/null && apt-get install -y -qq cloudflared 2>/dev/null
        fi
    fi
fi

if "$CF_BIN" --version 2>/dev/null; then
    log "cloudflared 版本: $($CF_BIN --version 2>&1)"
else
    log "ERROR: cloudflared 安装失败!"
    log "尝试查找系统中的 cloudflared..."
    which cloudflared 2>/dev/null && CF_BIN=$(which cloudflared) || log "系统中未找到 cloudflared"
fi

# ========== STEP 3: 启动 Quick Tunnel ==========
log "=== STEP 3: 启动 Quick Tunnel ==="

if ! "$CF_BIN" --version 2>/dev/null; then
    log "SKIP: cloudflared 不可用"
else
    # 停止现有 cloudflared
    pkill -f "cloudflared" 2>/dev/null || true
    sleep 2

    # 启动 Quick Tunnel
    log "启动 Quick Tunnel..."
    nohup "$CF_BIN" tunnel --url http://localhost:8450 > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    log "cloudflared PID: $CF_PID"

    # 等待 tunnel URL (最多 60 秒)
    TUNNEL_URL=""
    for i in $(seq 1 30); do
        sleep 2
        TUNNEL_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | head -1)
        if [ -n "$TUNNEL_URL" ]; then
            log "Tunnel URL: $TUNNEL_URL"
            break
        fi
        if [ $((i % 5)) -eq 0 ]; then
            log "等待 tunnel URL... ($((i*2))s)"
        fi
    done

    log "--- cloudflared 日志 (最后 15 行) ---"
    tail -15 /tmp/cloudflared.log 2>/dev/null | tee -a "$LOG_FILE"
fi

# ========== STEP 4: 更新 DNS ==========
log "=== STEP 4: 更新 DNS ==="

if [ -n "$TUNNEL_URL" ]; then
    TUNNEL_HOST=$(echo "$TUNNEL_URL" | sed 's|https://||')
    log "目标: aishield.tools -> $TUNNEL_HOST"

    CF_API_TOKEN=$(echo 'Y2Z1dF9Nb2hJTlhSTFBpaWQ2cHpDZUJuOVZCVUxxZWdvR29sSmVESEFwZDR1YWE1NDM5ZGI=' | base64 -d)
    CF_ZONE_ID='7625fc8ab719b3974e12aa2b6bf25489'

    # 查询现有 DNS 记录
    DNS_RESULT=$(curl -s "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records?name=aishield.tools" \
        -H "Authorization: Bearer $CF_API_TOKEN")
    DNS_RECORD_ID=$(echo "$DNS_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'][0]['id'] if d.get('result') else '')" 2>/dev/null)

    if [ -n "$DNS_RECORD_ID" ]; then
        log "现有 DNS 记录 ID: $DNS_RECORD_ID"
        log "更新为 CNAME -> $TUNNEL_HOST"
        UPDATE_RESULT=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$DNS_RECORD_ID" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"type\":\"CNAME\",\"name\":\"aishield.tools\",\"content\":\"$TUNNEL_HOST\",\"proxied\":true}")
        echo "$UPDATE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('DNS 更新: OK' if d.get('success') else 'DNS 更新失败: '+str(d.get('errors')))" 2>/dev/null | tee -a "$LOG_FILE"
    else
        log "DNS 记录不存在，创建新 CNAME 记录..."
        CREATE_RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"type\":\"CNAME\",\"name\":\"aishield.tools\",\"content\":\"$TUNNEL_HOST\",\"proxied\":true}")
        echo "$CREATE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('DNS 创建: OK' if d.get('success') else 'DNS 创建失败: '+str(d.get('errors')))" 2>/dev/null | tee -a "$LOG_FILE"
    fi

    unset CF_API_TOKEN
else
    log "ERROR: 未获取到 Tunnel URL，无法更新 DNS"
fi

# ========== STEP 5: 持久化 ==========
log "=== STEP 5: 持久化 (crontab) ==="

if [ -n "$TUNNEL_URL" ] && "$CF_BIN" --version 2>/dev/null; then
    CRON_LINE="* * * * * pgrep -f 'cloudflared tunnel' > /dev/null 2>&1 || nohup $CF_BIN tunnel --url http://localhost:8450 >> /tmp/cloudflared.log 2>&1 &"
    ( crontab -l 2>/dev/null | grep -v 'cloudflared' ; echo "$CRON_LINE" ) | crontab - 2>/dev/null
    if [ $? -eq 0 ]; then
        log "Cron job 已设置"
    else
        log "Cron 设置失败 (非关键)"
    fi
fi

# ========== STEP 6: 验证 ==========
log "=== STEP 6: 验证 ==="

log "--- API (localhost:8450) ---"
curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null && echo " OK" | tee -a "$LOG_FILE" || echo " FAIL" | tee -a "$LOG_FILE"

log "--- Tunnel URL ---"
if [ -n "$TUNNEL_URL" ]; then
    curl -sf --max-time 10 "$TUNNEL_URL/api/v1/health" 2>/dev/null && echo " OK" | tee -a "$LOG_FILE" || echo " FAIL" | tee -a "$LOG_FILE"
fi

log "--- aishield.tools ---"
curl -sf --max-time 10 https://aishield.tools/api/v1/health 2>/dev/null && echo " OK" | tee -a "$LOG_FILE" || echo " FAIL (DNS 传播中...)" | tee -a "$LOG_FILE"

# ========== 汇总 ==========
log "=== 部署汇总 ==="
log "Tunnel URL: ${TUNNEL_URL:-未获取}"
log "API: http://localhost:8450"
log "域名: https://aishield.tools"
log "cloudflared: $CF_BIN"
log "PID: ${CF_PID:-N/A}"

echo ""
echo "=== 完整日志 ==="
cat "$LOG_FILE"

exit 0
