#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 通过 Cloudflare API 创建持久化 Named Tunnel
# 解决 Quick Tunnel 的 error 1014 (CNAME Cross-User Banned) 问题
#
# Named Tunnel 的 CNAME 目标是 {tunnel_id}.cfargotunnel.com（同账户内），不会被 Cloudflare 拦截

set +e
LOG_FILE="/tmp/aishield-deploy.log"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "=== AIShield Named Tunnel Deployment ===" | tee "$LOG_FILE"
log "Time: $(date)"
log "User: $(whoami) (UID: $(id -u))"

# ========== 配置 ==========
CF_API_TOKEN=$(echo 'Y2Z1dF9Nb2hJTlhSTFBpaWQ2cHpDZUJuOVZCVUxxZWdvR29sSmVESEFwZDR1YWE1NDM5ZGI=' | base64 -d)
CF_ZONE_ID='7625fc8ab719b3974e12aa2b6bf25489'
TUNNEL_NAME='aishield-tunnel'
TOKEN_FILE='/root/.cloudflared/tunnel-token'
TUNNEL_ID_FILE='/root/.cloudflared/tunnel-id'

# ========== STEP 1: 启动 API (端口 8450) ==========
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

if [ -w /usr/local/bin ]; then
    CF_BIN=/usr/local/bin/cloudflared
elif [ -w /usr/bin ]; then
    CF_BIN=/usr/bin/cloudflared
else
    mkdir -p "$HOME/bin"
    CF_BIN="$HOME/bin/cloudflared"
fi
log "cloudflared 安装路径: $CF_BIN"

if [ -f "$CF_BIN" ] && "$CF_BIN" --version 2>/dev/null; then
    log "cloudflared 已安装: $($CF_BIN --version 2>&1)"
else
    log "下载 cloudflared..."
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
    which cloudflared 2>/dev/null && CF_BIN=$(which cloudflared) || log "系统中未找到 cloudflared"
fi

# ========== STEP 3: 获取 Account ID ==========
log "=== STEP 3: 获取 Account ID ==="

ZONE_INFO=$(curl -s "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID" \
    -H "Authorization: Bearer $CF_API_TOKEN")

ACCOUNT_ID=$(echo "$ZONE_INFO" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['account']['id'] if d.get('result') else '')" 2>/dev/null)

if [ -n "$ACCOUNT_ID" ]; then
    log "Account ID: $ACCOUNT_ID"
else
    log "ERROR: 无法获取 Account ID"
    log "API 响应: $(echo "$ZONE_INFO" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('errors','unknown'))" 2>/dev/null)"
fi

# ========== STEP 4: 创建/获取 Named Tunnel ==========
log "=== STEP 4: 创建/获取 Named Tunnel ==="

TUNNEL_ID=""
TUNNEL_TOKEN=""

if [ -n "$ACCOUNT_ID" ]; then
    # 检查是否已有同名 tunnel
    log "检查现有 tunnel: $TUNNEL_NAME"
    LIST_RESULT=$(curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel?name=$TUNNEL_NAME" \
        -H "Authorization: Bearer $CF_API_TOKEN")

    TUNNEL_ID=$(echo "$LIST_RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if d.get('result') and len(d['result']) > 0:
    print(d['result'][0]['id'])
" 2>/dev/null)

    if [ -n "$TUNNEL_ID" ]; then
        log "Tunnel 已存在: $TUNNEL_ID"

        # 检查 tunnel 状态
        TUNNEL_STATUS=$(echo "$LIST_RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if d.get('result') and len(d['result']) > 0:
    print(d['result'][0].get('status','unknown'))
" 2>/dev/null)
        log "Tunnel 状态: $TUNNEL_STATUS"

        # 如果 tunnel 已被删除，需要重新创建
        if [ "$TUNNEL_STATUS" = "deleted" ]; then
            log "Tunnel 已被删除，需要重新创建"
            TUNNEL_ID=""
        fi
    else
        log "API 响应: $(echo "$LIST_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('errors','no tunnel found'))" 2>/dev/null)"
    fi

    # 如果没有现有 tunnel，创建新的
    if [ -z "$TUNNEL_ID" ]; then
        log "创建新 Named Tunnel: $TUNNEL_NAME"

        # 生成 tunnel secret (32 bytes base64)
        TUNNEL_SECRET=$(head -c 32 /dev/urandom | base64)

        CREATE_RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"name\":\"$TUNNEL_NAME\",\"tunnel_secret\":\"$TUNNEL_SECRET\"}")

        TUNNEL_ID=$(echo "$CREATE_RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if d.get('result'):
    print(d['result'].get('id',''))
" 2>/dev/null)

        if [ -n "$TUNNEL_ID" ]; then
            log "Tunnel 创建成功! ID: $TUNNEL_ID"
            # 创建时返回 token
            TUNNEL_TOKEN=$(echo "$CREATE_RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if d.get('result'):
    print(d['result'].get('token',''))
" 2>/dev/null)
        else
            log "Tunnel 创建失败!"
            log "错误: $(echo "$CREATE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('errors','unknown')))" 2>/dev/null)"
            log "完整响应: $CREATE_RESULT"
        fi
    fi

    # 如果有 tunnel 但没有 token，尝试获取
    if [ -n "$TUNNEL_ID" ] && [ -z "$TUNNEL_TOKEN" ]; then
        log "获取 Tunnel token..."
        TOKEN_RESULT=$(curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel/$TUNNEL_ID/token" \
            -H "Authorization: Bearer $CF_API_TOKEN")

        TUNNEL_TOKEN=$(echo "$TOKEN_RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if d.get('result'):
    print(d['result'])
" 2>/dev/null)

        if [ -n "$TUNNEL_TOKEN" ]; then
            log "Token 获取成功"
        else
            log "Token 获取失败: $(echo "$TOKEN_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('errors','unknown')))" 2>/dev/null)"
        fi
    fi
fi

# ========== STEP 5: 配置 Ingress ==========
if [ -n "$TUNNEL_ID" ] && [ -n "$ACCOUNT_ID" ]; then
    log "=== STEP 5: 配置 Ingress ==="

    CONFIG_RESULT=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel/$TUNNEL_ID/configurations" \
        -H "Authorization: Bearer $CF_API_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "config": {
                "ingress": [
                    {
                        "hostname": "aishield.tools",
                        "service": "http://localhost:8450"
                    },
                    {
                        "service": "http_status:404"
                    }
                ]
            }
        }')

    CONFIG_OK=$(echo "$CONFIG_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('success') else 'FAIL')" 2>/dev/null)

    if [ "$CONFIG_OK" = "OK" ]; then
        log "Ingress 配置成功: aishield.tools -> http://localhost:8450"
    else
        log "Ingress 配置失败: $(echo "$CONFIG_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('errors','unknown')))" 2>/dev/null)"
    fi
fi

# ========== STEP 6: 更新 DNS ==========
if [ -n "$TUNNEL_ID" ]; then
    log "=== STEP 6: 更新 DNS ==="

    TUNNEL_CNAME="${TUNNEL_ID}.cfargotunnel.com"
    log "CNAME 目标: aishield.tools -> $TUNNEL_CNAME"

    # 查询现有 DNS 记录
    DNS_RESULT=$(curl -s "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records?name=aishield.tools" \
        -H "Authorization: Bearer $CF_API_TOKEN")

    DNS_RECORD_ID=$(echo "$DNS_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'][0]['id'] if d.get('result') else '')" 2>/dev/null)

    if [ -n "$DNS_RECORD_ID" ]; then
        log "更新现有 DNS 记录 (ID: $DNS_RECORD_ID)"
        UPDATE_RESULT=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$DNS_RECORD_ID" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"type\":\"CNAME\",\"name\":\"aishield.tools\",\"content\":\"$TUNNEL_CNAME\",\"proxied\":true}")

        echo "$UPDATE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('DNS 更新: OK' if d.get('success') else 'DNS 更新失败: '+json.dumps(d.get('errors','')))" 2>/dev/null | tee -a "$LOG_FILE"
    else
        log "创建新 DNS CNAME 记录..."
        CREATE_RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"type\":\"CNAME\",\"name\":\"aishield.tools\",\"content\":\"$TUNNEL_CNAME\",\"proxied\":true}")

        echo "$CREATE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('DNS 创建: OK' if d.get('success') else 'DNS 创建失败: '+json.dumps(d.get('errors','')))" 2>/dev/null | tee -a "$LOG_FILE"
    fi

    # 尝试设置 SSL 模式为 Full（非严格）
    log "设置 SSL 模式为 Full..."
    SSL_RESULT=$(curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/settings/ssl" \
        -H "Authorization: Bearer $CF_API_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"value":"full"}')
    echo "$SSL_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('SSL 设置: OK' if d.get('success') else 'SSL 设置: 跳过 (权限不足)')" 2>/dev/null | tee -a "$LOG_FILE"
fi

# ========== STEP 7: 启动 cloudflared ==========
log "=== STEP 7: 启动 Named Tunnel ==="

# 保存 token 到文件（供 cron 使用）
if [ -n "$TUNNEL_TOKEN" ]; then
    mkdir -p /root/.cloudflared
    echo -n "$TUNNEL_TOKEN" > "$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    echo -n "$TUNNEL_ID" > "$TUNNEL_ID_FILE"
    log "Token 已保存到 $TOKEN_FILE"
fi

# 如果没有 token 但文件中有，从文件读取
if [ -z "$TUNNEL_TOKEN" ] && [ -f "$TOKEN_FILE" ]; then
    TUNNEL_TOKEN=$(cat "$TOKEN_FILE")
    log "从文件读取 Token"
fi

if [ -z "$TUNNEL_ID" ] && [ -f "$TUNNEL_ID_FILE" ]; then
    TUNNEL_ID=$(cat "$TUNNEL_ID_FILE")
    log "从文件读取 Tunnel ID: $TUNNEL_ID"
fi

# 停止现有 cloudflared
pkill -f "cloudflared" 2>/dev/null || true
sleep 2

if [ -n "$TUNNEL_TOKEN" ] && "$CF_BIN" --version 2>/dev/null; then
    log "启动 Named Tunnel (token 模式)..."
    nohup "$CF_BIN" tunnel run --token "$TUNNEL_TOKEN" > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    log "cloudflared PID: $CF_PID"

    # 等待连接建立
    for i in $(seq 1 15); do
        sleep 2
        if grep -q "Registered tunnel connection" /tmp/cloudflared.log 2>/dev/null; then
            log "Tunnel 连接已建立!"
            break
        fi
        if [ $((i % 5)) -eq 0 ]; then
            log "等待 tunnel 连接... ($((i*2))s)"
        fi
    done

    log "--- cloudflared 日志 (最后 10 行) ---"
    tail -10 /tmp/cloudflared.log 2>/dev/null | tee -a "$LOG_FILE"
elif [ -n "$TUNNEL_ID" ] && [ -f /root/.cloudflared/cert.pem ]; then
    # 如果有 cert.pem，使用 cert 模式
    log "启动 Named Tunnel (cert 模式)..."
    nohup "$CF_BIN" tunnel run "$TUNNEL_NAME" > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    log "cloudflared PID: $CF_PID"
    sleep 10
    tail -10 /tmp/cloudflared.log 2>/dev/null | tee -a "$LOG_FILE"
else
    log "ERROR: 无法启动 Named Tunnel (缺少 token 或 cert)"
    log "TUNNEL_ID: ${TUNNEL_ID:-空}"
    log "TUNNEL_TOKEN: ${TUNNEL_TOKEN:+已设置}${TUNNEL_TOKEN:-空}"
    log "cert.pem: $([ -f /root/.cloudflared/cert.pem ] && echo '存在' || echo '不存在')"

    # Fallback: 启动 Quick Tunnel（仅用于临时访问）
    log "=== FALLBACK: 启动 Quick Tunnel（临时方案）==="
    nohup "$CF_BIN" tunnel --url http://localhost:8450 > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    log "Quick Tunnel PID: $CF_PID"
    sleep 15

    # 获取 Quick Tunnel URL
    QUICK_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | head -1)
    if [ -n "$QUICK_URL" ]; then
        log "Quick Tunnel URL: $QUICK_URL"
        log "注意: Quick Tunnel URL 无法绑定到 aishield.tools (error 1014)"
        log "请使用此 URL 临时访问: $QUICK_URL"
    fi
fi

# ========== STEP 8: 持久化 ==========
log "=== STEP 8: 持久化 ==="

# 创建启动脚本
cat > /opt/start-tunnel.sh << 'STARTEOF'
#!/bin/bash
# AIShield Tunnel 启动脚本
TOKEN_FILE='/root/.cloudflared/tunnel-token'
CF_BIN='/usr/local/bin/cloudflared'

cleanup() { kill $CF_PID 2>/dev/null; exit 0; }
trap cleanup SIGTERM SIGINT

if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE")
    $CF_BIN tunnel run --token "$TOKEN" &
    CF_PID=$!
else
    $CF_BIN tunnel --url http://localhost:8450 &
    CF_PID=$!
fi

wait $CF_PID
STARTEOF
chmod +x /opt/start-tunnel.sh 2>/dev/null

# systemd 服务
cat > /etc/systemd/system/cloudflared-tunnel.service << SVCEOF
[Unit]
Description=Cloudflare Named Tunnel for AIShield
After=network.target

[Service]
ExecStart=/opt/start-tunnel.sh
Restart=always
RestartSec=10
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload 2>/dev/null
systemctl enable cloudflared-tunnel 2>/dev/null
systemctl restart cloudflared-tunnel 2>/dev/null
log "systemd 服务已配置"

# Cron 备用保活
CRON_LINE="* * * * * pgrep -f 'cloudflared tunnel' > /dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1"
( crontab -l 2>/dev/null | grep -v 'cloudflared' ; echo "$CRON_LINE" ) | crontab - 2>/dev/null
log "Cron 保活已设置"

# ========== STEP 9: 验证 ==========
log "=== STEP 9: 验证 ==="

log "--- API (localhost:8450) ---"
curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null && echo " OK" | tee -a "$LOG_FILE" || echo " FAIL" | tee -a "$LOG_FILE"

log "--- cloudflared 进程 ---"
ps aux | grep cloudflared | grep -v grep | head -3 | tee -a "$LOG_FILE"

log "--- aishield.tools ---"
curl -sf --max-time 15 https://aishield.tools/api/v1/health 2>/dev/null && echo " OK" | tee -a "$LOG_FILE" || echo " FAIL (DNS 传播中或配置错误)" | tee -a "$LOG_FILE"

log "--- DNS 解析 ---"
dig +short aishield.tools 2>/dev/null | head -3 | tee -a "$LOG_FILE"

# ========== 汇总 ==========
log "=== 部署汇总 ==="
log "Tunnel ID: ${TUNNEL_ID:-未获取}"
log "Tunnel Type: Named Tunnel"
log "CNAME: ${TUNNEL_ID:+${TUNNEL_ID}.cfargotunnel.com}未配置"
log "API: http://localhost:8450"
log "域名: https://aishield.tools"
log "cloudflared: $CF_BIN"
log "PID: ${CF_PID:-N/A}"

if [ -n "$TUNNEL_ID" ] && [ -n "$TUNNEL_TOKEN" ]; then
    log "状态: Named Tunnel 已配置"
    log "Tunnel CNAME: ${TUNNEL_ID}.cfargotunnel.com"
else
    log "状态: Named Tunnel 配置失败，使用 Quick Tunnel 临时方案"
    log "需要手动操作: 创建 API Token with Account:Cloudflare Tunnel:Edit 权限"
fi

unset CF_API_TOKEN TUNNEL_TOKEN TUNNEL_SECRET

echo ""
echo "=== 完整日志 ==="
cat "$LOG_FILE"

exit 0
