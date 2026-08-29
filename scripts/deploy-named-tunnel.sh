#!/bin/bash
# AIShield Named Tunnel 部署脚本
# 使用 cert.pem (cloudflared tunnel login) 创建持久化 Named Tunnel
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
CERT_FILE='/root/.cloudflared/cert.pem'
CONFIG_FILE='/root/.cloudflared/config.yml'
CRED_DIR='/root/.cloudflared'

# ========== STEP 1: 启动 API (端口 8450) ==========
log "=== STEP 1: 启动 API (端口 8450) ==="

cd /opt/aishield 2>/dev/null || cd ~/aishield 2>/dev/null || true
# ── 代码更新 ──────────────────────────────────────────────────────
# 【2026-08-28 修复】旧实现有两个叠加的静默失效：
#   1) `git pull ... || true` 把拉取失败吞掉；
#   2) 拉取之后，只要 API 已在运行就只打一行日志、永不重启 —— 进程
#      一直跑着「启动那一刻」的旧代码。文件更新了，内存里没更新。
# 结果：线上长期停在 4.2.0 / 133 规则，而所有部署门禁都是绿的
# （health 只判断「活着」，从不判断「是不是新代码」）。
# 现改为：以仓库 main 为真相源比对版本哨兵 -> 必要时 raw 兜底覆盖
#         -> 只要代码有变化就必须重启进程。
RAW=https://raw.githubusercontent.com/lm203688/aishield/main
NEED_RESTART=0

before_head=$(git rev-parse HEAD 2>/dev/null || echo "nogit")
git fetch --all 2>/dev/null || true
git reset --hard origin/main 2>/dev/null || git pull origin main 2>/dev/null || true
after_head=$(git rev-parse HEAD 2>/dev/null || echo "nogit")
log "HEAD: ${before_head:0:8} -> ${after_head:0:8}"
[ "$before_head" != "$after_head" ] && NEED_RESTART=1

# ── 真相源：把「磁盘上的 commit」写进 .deploy_meta.json ─────────────────
# 这一步必须在 git reset 之后、进程重启之前，否则 API 永远读不到新值。
# 用 commit SHA 而不是版本字符串做判据：版本字符串只在发版时变，
# 「只新增 12 条规则、不改版本号」这类日常改动会让版本判据完全失明。
python3 - "$after_head" <<'PYMETA' 2>/dev/null || true
import json, sys, datetime
commit = sys.argv[1] if len(sys.argv) > 1 else ""
if commit and commit != "nogit":
    json.dump({"commit": commit,
               "deployed_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")},
              open(".deploy_meta.json", "w"), indent=2)
PYMETA

# 兼容保留：版本字符串哨兵，仅在 git 完全不可用时（after_head=nogit）才用。
card_ver() {
    python3 -c "
import json,sys
try:
    d=json.load(open(sys.argv[1]))
    print(d.get('version') or d.get('serverInfo',{}).get('version',''))
except Exception:
    print('')
" "$1" 2>/dev/null || true
}

disk_ver=$(card_ver api/static/.well-known/mcp/server-card.json)

# ── 关键判据：进程自报的 commit vs 磁盘上的 commit ─────────────────────
# 唯一可靠的「进程是否在跑磁盘代码」信号。head_sha 每次 push 都会变，
# 所以规则新增、脚本修改、文档更新都会被正确捕获。
live_meta=$(curl -s --max-time 10 http://127.0.0.1:8450/api/v1/health 2>/dev/null || true)
live_commit=$(printf '%s' "$live_meta" | python3 -c "import json,sys
try:
    print(json.load(sys.stdin).get('commit') or '')
except Exception:
    print('')" 2>/dev/null || true)
disk_commit=$(python3 -c "import json
try:
    print(json.load(open('.deploy_meta.json')).get('commit') or '')
except Exception:
    print('')" 2>/dev/null || true)
log "commit 对比: 运行进程=${live_commit:-none} / 磁盘=${disk_commit:-none}"

if [ -n "$disk_commit" ] && [ "$live_commit" != "$disk_commit" ]; then
    log "运行进程落后于磁盘代码（commit 不一致）-> 标记重启"
    NEED_RESTART=1
fi

# git 不可用时的兜底：raw 通道覆盖关键文件
if [ "$after_head" = "nogit" ]; then
    if curl -sL --max-time 20 "$RAW/api/static/.well-known/mcp/server-card.json" -o /tmp/_card_main.json 2>/dev/null; then
        expect_ver=$(card_ver /tmp/_card_main.json)
    else
        expect_ver=""
    fi
    rm -f /tmp/_card_main.json
    log "git 不可用 -> 走 raw 兜底 (磁盘=${disk_ver:-none} 仓库=${expect_ver:-unknown})"
    if [ -n "$expect_ver" ] && [ "$disk_ver" != "$expect_ver" ]; then
        curl -sL --max-time 30 "$RAW/api/static/.well-known/mcp/server-card.json" -o api/static/.well-known/mcp/server-card.json 2>/dev/null
        curl -sL --max-time 30 "$RAW/api/static/.well-known/agent-card.json" -o api/static/.well-known/agent-card.json 2>/dev/null
        curl -sL --max-time 30 "$RAW/api/server.py" -o /tmp/aishield-server.py.new 2>/dev/null && mv /tmp/aishield-server.py.new api/server.py
        NEED_RESTART=1
    fi
fi

if ! curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
    NEED_RESTART=1
fi

# ── 启动 / 重启 API ───────────────────────────────────────────────
if [ "$NEED_RESTART" = "1" ]; then
    log "需要重新加载代码 -> 重启 API"
    cname=""
    if command -v docker &>/dev/null; then
        cname=$(docker ps -a --format '{{.Names}}' 2>/dev/null | grep -i aishield | head -1)
    fi

    if [ -n "$cname" ]; then
        log "通过 docker 重启容器: $cname"
        docker restart "$cname" 2>/dev/null || true
        sleep 10
    fi

    # 兜底：用 commit 判断「跑着的进程是否就是磁盘上的代码」。
    # 注意不能写成「API 挂了才重启」—— 陈旧进程恰好是「活着但 commit 不对」，
    # 那种写法会正好跳过重启，问题永远修不掉。
    cur_commit=$(curl -s --max-time 10 http://127.0.0.1:8450/api/v1/health 2>/dev/null | python3 -c "import json,sys
try:
    print(json.load(sys.stdin).get('commit') or '')
except Exception:
    print('')" 2>/dev/null || true)
    if [ "$cur_commit" != "$disk_commit" ] || ! curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
        log "强制重启 Python API 进程（当前commit=${cur_commit:-none} 目标=${disk_commit:-none}）"
        pkill -f "api/server.py" 2>/dev/null || true
        sleep 2
        export PORT=8450
        nohup python3 api/server.py > /tmp/aishield-api.log 2>&1 &
        sleep 8
    else
        log "运行进程 commit 已与磁盘一致（${cur_commit}）-> 无需额外重启"
    fi
else
    log "代码已是最新且 API 健康 -> 跳过重启"
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
    )
    for URL in "${DOWNLOAD_URLS[@]}"; do
        log "尝试下载: $URL"
        curl -L --connect-timeout 10 --max-time 60 -o "$CF_BIN" "$URL" 2>/dev/null
        if [ -s "$CF_BIN" ] && "$CF_BIN" --version 2>/dev/null; then
            log "下载成功!"
            chmod +x "$CF_BIN"
            break
        fi
    done
fi

if "$CF_BIN" --version 2>/dev/null; then
    log "cloudflared 版本: $($CF_BIN --version 2>&1)"
else
    log "ERROR: cloudflared 不可用!"
    which cloudflared 2>/dev/null && CF_BIN=$(which cloudflared) || log "系统中未找到 cloudflared"
fi

# ========== STEP 3: 检查 cert.pem ==========
log "=== STEP 3: 检查认证方式 ==="

TUNNEL_MODE=""  # "cert" or "token" or "quick"
TUNNEL_ID=""
TUNNEL_TOKEN=""

if [ -f "$CERT_FILE" ]; then
    log "cert.pem 存在: $(ls -la $CERT_FILE)"
    TUNNEL_MODE="cert"
else
    log "cert.pem 不存在，尝试 API 方式..."

    # 获取 Account ID
    ZONE_INFO=$(curl -s "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID" \
        -H "Authorization: Bearer $CF_API_TOKEN")
    ACCOUNT_ID=$(echo "$ZONE_INFO" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['account']['id'] if d.get('result') else '')" 2>/dev/null)

    if [ -n "$ACCOUNT_ID" ]; then
        log "Account ID: $ACCOUNT_ID"

        # 尝试创建 Named Tunnel via API
        TUNNEL_SECRET=$(head -c 32 /dev/urandom | base64)
        CREATE_RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"name\":\"$TUNNEL_NAME\",\"tunnel_secret\":\"$TUNNEL_SECRET\"}")

        TUNNEL_ID=$(echo "$CREATE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'].get('id','') if d.get('result') else '')" 2>/dev/null)

        if [ -n "$TUNNEL_ID" ]; then
            log "Tunnel 创建成功 (API): $TUNNEL_ID"
            TUNNEL_TOKEN=$(echo "$CREATE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'].get('token',''))" 2>/dev/null)
            TUNNEL_MODE="token"

            # 配置 ingress via API
            curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel/$TUNNEL_ID/configurations" \
                -H "Authorization: Bearer $CF_API_TOKEN" \
                -H "Content-Type: application/json" \
                -d '{"config":{"ingress":[{"hostname":"aishield.tools","service":"http://localhost:8450"},{"service":"http_status:404"}]}}' \
                | python3 -c "import sys,json; d=json.load(sys.stdin); print('Ingress: OK' if d.get('success') else 'Ingress: FAIL')" 2>/dev/null | tee -a "$LOG_FILE"
        else
            log "API Tunnel 创建失败: $(echo "$CREATE_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('errors','unknown'))" 2>/dev/null)"
        fi
    fi
fi

# ========== STEP 4: 使用 cert.pem 创建/获取 Named Tunnel ==========
if [ "$TUNNEL_MODE" = "cert" ]; then
    log "=== STEP 4: 使用 cert.pem 创建 Named Tunnel ==="

    # 检查是否已有同名 tunnel
    log "检查现有 tunnel..."
    TUNNEL_LIST=$("$CF_BIN" tunnel list 2>&1)
    log "现有 tunnel 列表:"
    echo "$TUNNEL_LIST" | tee -a "$LOG_FILE"

    # 尝试从列表中提取 tunnel ID
    # 格式: ID                                   NAME              ...
    TUNNEL_ID=$(echo "$TUNNEL_LIST" | grep "$TUNNEL_NAME" | awk '{print $1}' | head -1)

    if [ -n "$TUNNEL_ID" ]; then
        log "Tunnel 已存在: $TUNNEL_ID"
    else
        log "创建新 tunnel: $TUNNEL_NAME"
        CREATE_OUTPUT=$("$CF_BIN" tunnel create "$TUNNEL_NAME" 2>&1)
        log "创建输出: $CREATE_OUTPUT"

        # 从创建输出中提取 tunnel ID
        TUNNEL_ID=$(echo "$CREATE_OUTPUT" | grep -oP '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)

        if [ -n "$TUNNEL_ID" ]; then
            log "Tunnel 创建成功! ID: $TUNNEL_ID"
        else
            log "Tunnel 创建失败，尝试其他方法..."
            # 可能 tunnel 已存在但名称不匹配，列出所有
            TUNNEL_ID=$("$CF_BIN" tunnel list 2>&1 | grep -v "ID" | grep -v "^$" | awk '{print $1}' | head -1)
            if [ -n "$TUNNEL_ID" ]; then
                log "使用第一个可用 tunnel: $TUNNEL_ID"
            fi
        fi
    fi

    # 配置 tunnel
    if [ -n "$TUNNEL_ID" ]; then
        CRED_FILE="$CRED_DIR/${TUNNEL_ID}.json"

        log "凭证文件: $CRED_FILE"
        if [ -f "$CRED_FILE" ]; then
            log "凭证文件存在"
        else
            log "凭证文件不存在，列出 .cloudflared 目录内容:"
            ls -la "$CRED_DIR/" 2>/dev/null | tee -a "$LOG_FILE"
        fi

        # 创建 config.yml
        log "创建 config.yml..."
        cat > "$CONFIG_FILE" << CONFIGEOF
tunnel: ${TUNNEL_ID}
credentials-file: ${CRED_FILE}

ingress:
  - hostname: aishield.tools
    service: http://localhost:8450
  - service: http_status:404
CONFIGEOF
        log "config.yml 已创建:"
        cat "$CONFIG_FILE" | tee -a "$LOG_FILE"

        # 路由 DNS
        log "路由 DNS: aishield.tools -> ${TUNNEL_ID}.cfargotunnel.com"
        DNS_ROUTE_OUTPUT=$("$CF_BIN" tunnel route dns "$TUNNEL_NAME" aishield.tools 2>&1)
        log "DNS 路由结果: $DNS_ROUTE_OUTPUT"

        # 如果按名称路由失败，尝试按 ID
        if echo "$DNS_ROUTE_OUTPUT" | grep -qi "error\|fail"; then
            log "按名称路由失败，尝试按 ID..."
            DNS_ROUTE_OUTPUT=$("$CF_BIN" tunnel route dns "$TUNNEL_ID" aishield.tools 2>&1)
            log "DNS 路由结果 (by ID): $DNS_ROUTE_OUTPUT"
        fi
    else
        log "ERROR: 无法获取 Tunnel ID，cert.pem 模式失败"
        TUNNEL_MODE="quick"
    fi
fi

# ========== STEP 5: 更新 DNS (API - 所有模式) ==========
if [ -n "$TUNNEL_ID" ]; then
    log "=== STEP 5: 更新 DNS (API) ==="

    TUNNEL_CNAME="${TUNNEL_ID}.cfargotunnel.com"
    log "CNAME: aishield.tools -> $TUNNEL_CNAME"

    # 使用 API 更新 DNS（cert.pem 的 zone 可能不匹配，API 更可靠）
    DNS_RESULT=$(curl -s "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records?name=aishield.tools" \
        -H "Authorization: Bearer $CF_API_TOKEN")
    DNS_RECORD_ID=$(echo "$DNS_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'][0]['id'] if d.get('result') else '')" 2>/dev/null)

    if [ -n "$DNS_RECORD_ID" ]; then
        log "更新现有 DNS 记录 (ID: $DNS_RECORD_ID)"
        curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$DNS_RECORD_ID" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"type\":\"CNAME\",\"name\":\"aishield.tools\",\"content\":\"$TUNNEL_CNAME\",\"proxied\":true}" \
            | python3 -c "import sys,json; d=json.load(sys.stdin); print('DNS 更新: OK' if d.get('success') else 'DNS 更新失败: '+json.dumps(d.get('errors','')))" 2>/dev/null | tee -a "$LOG_FILE"
    else
        log "创建新 DNS CNAME 记录..."
        curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"type\":\"CNAME\",\"name\":\"aishield.tools\",\"content\":\"$TUNNEL_CNAME\",\"proxied\":true}" \
            | python3 -c "import sys,json; d=json.load(sys.stdin); print('DNS 创建: OK' if d.get('success') else 'DNS 创建失败: '+json.dumps(d.get('errors','')))" 2>/dev/null | tee -a "$LOG_FILE"
    fi

    # 设置 SSL 模式为 Full
    log "设置 SSL 模式为 Full..."
    curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/settings/ssl" \
        -H "Authorization: Bearer $CF_API_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"value":"full"}' \
        | python3 -c "import sys,json; d=json.load(sys.stdin); print('SSL: OK' if d.get('success') else 'SSL: 跳过')" 2>/dev/null | tee -a "$LOG_FILE"
fi

# ========== STEP 6: 启动 Tunnel ==========
log "=== STEP 6: 启动 Tunnel ==="

# 停止现有 cloudflared
pkill -f "cloudflared" 2>/dev/null || true
sleep 3

if [ "$TUNNEL_MODE" = "cert" ] && [ -n "$TUNNEL_ID" ]; then
    log "启动 Named Tunnel (cert 模式)..."
    log "使用 config: $CONFIG_FILE"
    nohup "$CF_BIN" tunnel --config "$CONFIG_FILE" run > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    log "cloudflared PID: $CF_PID"

elif [ "$TUNNEL_MODE" = "token" ] && [ -n "$TUNNEL_TOKEN" ]; then
    log "启动 Named Tunnel (token 模式)..."
    nohup "$CF_BIN" tunnel run --token "$TUNNEL_TOKEN" > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    log "cloudflared PID: $CF_PID"

else
    log "ERROR: 无法启动 Named Tunnel，使用 Quick Tunnel 临时方案"
    TUNNEL_MODE="quick"
    nohup "$CF_BIN" tunnel --url http://localhost:8450 > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    log "Quick Tunnel PID: $CF_PID"
fi

# 等待连接建立
for i in $(seq 1 20); do
    sleep 2
    if grep -q "Registered tunnel connection" /tmp/cloudflared.log 2>/dev/null; then
        log "Tunnel 连接已建立!"
        break
    fi
    if [ $((i % 5)) -eq 0 ]; then
        log "等待 tunnel 连接... ($((i*2))s)"
    fi
done

log "--- cloudflared 日志 (最后 15 行) ---"
tail -15 /tmp/cloudflared.log 2>/dev/null | tee -a "$LOG_FILE"

# ========== STEP 7: 持久化 ==========
log "=== STEP 7: 持久化 ==="

# 创建启动脚本
cat > /opt/start-tunnel.sh << 'STARTEOF'
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
STARTEOF
chmod +x /opt/start-tunnel.sh 2>/dev/null

# systemd 服务
cat > /etc/systemd/system/cloudflared-tunnel.service << 'SVCEOF'
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

# ========== STEP 8: 验证 ==========
log "=== STEP 8: 验证 ==="

log "--- API (localhost:8450) ---"
curl -sf http://127.0.0.1:8450/api/v1/health 2>/dev/null && echo " OK" | tee -a "$LOG_FILE" || echo " FAIL" | tee -a "$LOG_FILE"

log "--- cloudflared 进程 ---"
ps aux | grep cloudflared | grep -v grep | head -3 | tee -a "$LOG_FILE"

log "--- aishield.tools ---"
curl -sf --max-time 15 https://aishield.tools/api/v1/health 2>/dev/null && echo " OK" | tee -a "$LOG_FILE" || echo " FAIL (DNS 传播中或配置错误)" | tee -a "$LOG_FILE"

log "--- DNS CNAME ---"
dig aishield.tools CNAME +short 2>/dev/null | head -3 | tee -a "$LOG_FILE"

log "--- DNS A ---"
dig +short aishield.tools 2>/dev/null | head -3 | tee -a "$LOG_FILE"

# ========== 汇总 ==========
log "=== 部署汇总 ==="
log "Tunnel Mode: $TUNNEL_MODE"
log "Tunnel ID: ${TUNNEL_ID:-未获取}"
log "API: http://localhost:8450"
log "域名: https://aishield.tools"
log "cloudflared: $CF_BIN"
log "PID: ${CF_PID:-N/A}"
log "Config: ${CONFIG_FILE:-N/A}"

if [ "$TUNNEL_MODE" = "cert" ]; then
    log "CNAME: ${TUNNEL_ID}.cfargotunnel.com"
    log "状态: Named Tunnel (cert 模式) 已配置"
elif [ "$TUNNEL_MODE" = "token" ]; then
    log "CNAME: ${TUNNEL_ID}.cfargotunnel.com"
    log "状态: Named Tunnel (token 模式) 已配置"
else
    log "状态: Quick Tunnel 临时方案 (error 1014 未解决)"
    QUICK_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | head -1)
    log "临时 URL: ${QUICK_URL:-未获取}"
fi

unset CF_API_TOKEN TUNNEL_TOKEN TUNNEL_SECRET

echo ""
echo "=== 完整日志 ==="
cat "$LOG_FILE"

exit 0
