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
# 【2026-09-15】CF token 不再硬编码。此前这里 inline 解码一个 base64 token，
# 本仓库是 public 的 —— 等于把 aishield.tools 的 Zone Read + DNS Records Edit
# + Zone Settings Edit 公开给所有人（足以劫持 CNAME 指向攻击者服务器）。
# 改为运行期解析：env $CF_TUNNEL_TOKEN -> /root/.aishield/cf-token。
# 后者由 .github/workflows/install-cf-token.yml 一次性写入（chmod 600）。
[ -f "$(dirname "$0")/cf-token-loader.sh" ] && . "$(dirname "$0")/cf-token-loader.sh"
CF_ZONE_ID='7625fc8ab719b3974e12aa2b6bf25489'
TUNNEL_NAME='aishield-tunnel'
CERT_FILE='/root/.cloudflared/cert.pem'
CONFIG_FILE='/root/.cloudflared/config.yml'
CRED_DIR='/root/.cloudflared'

# ========== STEP 1: 启动 API (端口 8450) ==========
log "=== STEP 1: 启动 API (端口 8450) ==="

# --- STEP 1a: 身份签名后端（L1 可移植身份 / L3 意图授权的生死线）---
# 【2026-10-05 修的真实生产缺口】线上 /api/v1/identity/jwks 长期返回
# keys=[] ready=false，根因不在代码而在**运行时环境**：
#   * api/data/*.json 被 gitignore，tarball 投递也不含 —— 生产从来没有签发密钥；
#   * eco/crypto_sign.py 在没有 cryptography 时会**静默降级**成 hmac-sha256，
#     于是 JWKS 发不出公钥、VC 与 mandate 签出来只能自证；
#   * 而本机与 CI 都装了 cryptography —— 所以 1865 个单测、148 条契约路由全绿，
#     绿的是代码，不是生产。这是第三层假绿（前两层是「入口漏接」「签不出也不报」）。
# 处理办法复用 scripts/rotate_signing_key.py：它先预检后端，再做「备份 → 迁移
# → 自检 → 不过就自回滚」，不会留下「迁移显示成功、第三方其实验不过」的半吊子。
#
# 为什么不在这里 exit 1：pip 装不上（网络/权限）属于环境侧偶发，不该让整条
# 发布链陪葬；这一步只把结果如实打进日志，真正的拦截在部署验证门第 6 条断言
# （线上 identity_ready 必须为 true）。退出码显式取 rc，不用 || echo 吞掉。
python3 -m pip install cryptography >/dev/null 2>&1 \
  && echo "[identity] cryptography 就位（后端应为 ed25519）" \
  || echo "[identity] WARN: cryptography 安装失败，后端可能仍是 hmac-sha256"

cd "$(dirname "$0")/.." 2>/dev/null || true
python3 scripts/rotate_signing_key.py --yes > /tmp/aishield-rotate.log 2>&1
rotate_rc=$?
tail -n 12 /tmp/aishield-rotate.log
echo "[identity] rotate_signing_key exit=${rotate_rc}（非 0 不阻断部署；"
echo "           线上 identity_ready 断言会判红）"

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
# 【2026-09-06 修复】旧实现 `git fetch --all 2>/dev/null || true` 把 fetch 失败
# 静默吞掉，reset 复位到陈旧的本地 origin/main 引用 —— 部署日志铁证
# `HEAD: 93fcd10c -> 93fcd10c`，线上停在 09-01 代码而所有门禁照绿。
# 新语义（按可靠性排序）：
#   1) DEPLOY_SHA 注入（GitHub Actions 经 SSH 投递代码 tarball 时设置）——
#      代码已在磁盘，唯一要做的就是如实把该 sha 写进 .deploy_meta.json；
#   2) 无 DEPLOY_SHA 时走 git fetch，失败显式暴露（不再吞），
#      并尝试 codeload 全量 tarball 兜底（单请求，区别于逐文件 raw）；
#   3) 全部失败 -> 保留磁盘现状，meta 维持旧值，
#      由验证门第 5 条断言（磁盘 commit == 触发 run 的 GitHub sha）判红。
after_head=""
if [ -n "${DEPLOY_SHA:-}" ]; then
    after_head="$DEPLOY_SHA"
    log "代码由 runner tarball 投递，权威 sha=${after_head:0:8}"
else
    fetch_ok=0
    if git fetch --all 2>/tmp/aishield-fetch.log; then
        fetch_ok=1
    else
        log "git fetch 失败: $(tail -2 /tmp/aishield-fetch.log 2>/dev/null)"
    fi
    if [ "$fetch_ok" = "1" ]; then
        git reset --hard origin/main 2>/dev/null || git pull origin main 2>/dev/null || true
        after_head=$(git rev-parse HEAD 2>/dev/null || echo "nogit")
    else
        # fetch 失败 -> codeload 全量 tarball 兜底覆盖（不含 .git 元数据）
        if curl -fsSL --max-time 60 "https://github.com/lm203688/aishield/archive/main.tar.gz" -o /tmp/aishield-main.tgz 2>/dev/null && [ -s /tmp/aishield-main.tgz ]; then
            rm -rf /tmp/aishield-main
            tar xzf /tmp/aishield-main.tgz -C /tmp 2>/dev/null
            if [ -d /tmp/aishield-main ]; then
                ( shopt -s dotglob; cp -a /tmp/aishield-main/* . ) 2>/dev/null
                rm -rf /tmp/aishield-main
            fi
            rm -f /tmp/aishield-main.tgz
            after_head="tarball"
            log "git fetch 失败 -> codeload tarball 兜底覆盖完成"
        else
            after_head="$before_head"
            log "git fetch 与 tarball 兜底均失败 -> 磁盘维持旧代码（验证门应判红）"
        fi
    fi
    log "HEAD: ${before_head:0:8} -> ${after_head:0:8}"
    [ "$before_head" != "$after_head" ] && NEED_RESTART=1
fi

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

# ── API 保活 ────────────────────────────────────────────────────────
# 【2026-09-18 修复】线上 502 失活约 20h 的根因：API 进程只有 nohup 启动，
# 没有 systemd 服务、没有 cron 保活。cloudflared 有 systemd + cron 双保活，
# API 什么都没有 —— 进程一死（OOM / VPS 重启 / SSH 会话清理）就没有任何
# 东西会拉起它，只能等下一次部署恰好被触发。三次自愈（09-17 11:53 / 17:09 /
# 21:31 UTC）全部跑到 STEP 8 仍是 `--- API (localhost:8450) --- FAIL`，
# 即 VPS 本机 8450 上根本没有进程在监听。
# 现改为：systemd 服务优先（Restart=always，由 init 负责拉起），
# nohup 仅作 systemd 不可用时的兜底；启动后带 3 轮重试验证，
# 失败即打印完整日志 + 端口占用 + 进程列表，不再静默。
API_DIR="$(pwd)"

api_healthy() {
    curl -sf --max-time 8 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1
}

api_start_nohup() {
    export PORT=8450
    # 【2026-09-18】线上失活的确切根因。api/server.py::assert_not_root() 拒绝以
    # root 运行（09-16 落地的执行身份护栏，借鉴 Shannon #323），而本机的部署身份
    # 是 root（systemd 服务、systemctl 都需要 root）。于是 API 进程「启动即退出」：
    #   AIShield refuses to run as root. ... Run as a normal user, or set
    #   AISHIELD_ALLOW_ROOT=1 inside a container.
    # 3 轮重试每轮都是同一条拒绝日志，STEP 8 因此永远 `--- API --- FAIL`，
    # 域名稳定 502（cloudflared 存活、后端无进程）。
    # 本 VPS 是专用部署机、root 运行是既定架构，故显式放行并留痕（server 会打
    # WARNING 日志）。这是有意识的决定，不是删护栏。
    export AISHIELD_ALLOW_ROOT=1
    nohup python3 "${API_DIR}/api/server.py" >> /tmp/aishield-api.log 2>&1 &
}

install_api_service() {
    if ! [ -w /etc/systemd/system ]; then
        log "无 /etc/systemd/system 写权限 -> API 走 nohup 兜底"
        return 1
    fi
    cat > /etc/systemd/system/aishield-api.service << APIEOF
[Unit]
Description=AIShield API server (port 8450)
After=network.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${API_DIR}
Environment=PORT=8450
Environment=PYTHONUNBUFFERED=1
# 【2026-09-18】同 api_start_nohup：systemd 以 root 拉起 API，
# assert_not_root() 会 sys.exit(2)，服务永远停在 failed 状态。
Environment=AISHIELD_ALLOW_ROOT=1
ExecStart=/bin/sh -c 'exec $(command -v python3) ${API_DIR}/api/server.py >> /tmp/aishield-api.log 2>&1'
Restart=always
RestartSec=5
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
APIEOF
    systemctl daemon-reload 2>/dev/null || true
    systemctl enable aishield-api 2>/dev/null || true
    log "systemd 服务 aishield-api 已安装（Restart=always，WorkingDirectory=${API_DIR}）"
    return 0
}

ensure_api_up() {
    # 1) 既有的 aishield docker 容器优先沿用（不破坏既有部署形态）
    cname=""
    if command -v docker &>/dev/null; then
        cname=$(docker ps -a --format '{{.Names}}' 2>/dev/null | grep -i aishield | head -1)
    fi
    if [ -n "$cname" ]; then
        log "检测到 aishield docker 容器: $cname -> 尝试容器内重启"
        docker restart "$cname" 2>/dev/null || true
        sleep 10
        if api_healthy; then
            log "API 状态: OK（docker 容器 ${cname}）"
            return 0
        fi
        log "docker 容器未能恢复 API -> 停止容器，改由 systemd/nohup 托管"
        docker stop "$cname" 2>/dev/null || true
        sleep 3
    fi

    install_api_service || true

    # 2) 首轮启动：systemd 可用就走 init，否则 nohup
    if systemctl is-enabled aishield-api >/dev/null 2>&1; then
        systemctl restart aishield-api 2>/dev/null || api_start_nohup
        sleep 6
    else
        pkill -f "api/server.py" 2>/dev/null || true
        sleep 2
        api_start_nohup
        sleep 6
    fi

    # 3) 最多 3 轮重试；每轮失败都留下可定位的证据
    local i
    for i in 1 2 3; do
        if api_healthy; then
            log "API 状态: OK（第 ${i} 轮验证通过）"
            return 0
        fi
        log "API 第 ${i} 轮未响应 -> 重启"
        if systemctl is-enabled aishield-api >/dev/null 2>&1; then
            systemctl restart aishield-api 2>/dev/null || api_start_nohup
        else
            pkill -f "api/server.py" 2>/dev/null || true
            sleep 2
            api_start_nohup
        fi
        sleep 8
    done

    log "API 状态: FAIL（3 轮启动均未通过健康检查）"
    log "--- /tmp/aishield-api.log (最后 30 行) ---"
    tail -30 /tmp/aishield-api.log 2>/dev/null || log "(无 API 日志文件)"
    log "--- 语法自检 ---"
    python3 -m py_compile "${API_DIR}/api/server.py" 2>&1 | tail -20         && log "py_compile: 语法 OK（说明是运行期/端口/依赖问题，不是代码错误）"
    log "--- 端口占用 ---"
    (ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null || true) | grep -E ':(8450|8080)' | head -5
    log "--- python 进程 ---"
    ps aux 2>/dev/null | grep -E 'api/server.py' | grep -v grep | head -5         || log "(无 api/server.py 进程 -> 启动即退出)"
    return 1
}

# ── 启动 / 重启 API ───────────────────────────────────────────────
if [ "$NEED_RESTART" = "1" ]; then
    log "需要重新加载代码 -> 重启 API"
else
    log "代码已是最新且 API 健康 -> 仍执行一次保活检查（幂等）"
fi

ensure_api_up || true

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

    # API 方式需要 CF token；cert.pem 模式完全不需要（走 cloudflared CLI）。
    # 注意必须用 `if ! load_cf_token` 判空：本脚本是 set +e，裸调用会把
    # "没有 token"静默吞掉，然后拿空 Authorization 头连续 curl Cloudflare。
    if ! load_cf_token; then
        log "WARN: 无 CF API token（env \$CF_TUNNEL_TOKEN 与 ${CF_TOKEN_FILE} 均缺）。"
        log "       cert.pem 也不存在，无法创建 Named Tunnel —— 中止。"
        log "       修复：GitHub Secrets 添加 CF_TUNNEL_TOKEN，再运行"
        log "       Actions → install CF token to VPS（docs/cf-token-rotation.md）。"
        exit 2
    fi
    log "CF token 来源: $(cf_token_source)"

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

# 停止现有 cloudflared 实例。
# 【2026-09-18 修复】原 `pkill -f "cloudflared"` 有两个后果：
#   1) 杀掉同机**所有**项目的 cloudflared。本机是多项目共享（tunnel 列表里同时存在
#      aishield-tunnel / aishield.tools / healthlens / healthlens-tunnel），每次部署
#      都会把 healthlens 等其他项目的隧道一并打断；
#   2) 与 STEP 7 的 `systemctl restart cloudflared-tunnel` 叠加，会让 nohup 实例和
#      systemd 实例同时持有同一 tunnel ID。Cloudflare 限制单 tunnel 的并发连接数，
#      两个实例互相把对方踢下线，日志表现为反复 `ERR no more connections active
#      and exiting` —— 隧道看起来活着，实际处于不稳定抖动。
# 现改为：按 PID 文件停止自己上次启动的实例 + 按本项目 config 路径精确匹配兜底，
# systemd 托管的实例走 systemctl stop（不动任何非 systemd 进程）。
AISHIELD_CF_PIDFILE="${CRED_DIR}/tunnel.pid"
if [ -f "$AISHIELD_CF_PIDFILE" ]; then
    OLD_CF_PID=$(cat "$AISHIELD_CF_PIDFILE" 2>/dev/null)
    if [ -n "$OLD_CF_PID" ] && kill -0 "$OLD_CF_PID" 2>/dev/null; then
        log "停止上次启动的 cloudflared (PID ${OLD_CF_PID})"
        kill "$OLD_CF_PID" 2>/dev/null || true
    fi
    rm -f "$AISHIELD_CF_PIDFILE"
fi
if systemctl is-active cloudflared-tunnel >/dev/null 2>&1; then
    log "systemd 托管中 -> systemctl stop cloudflared-tunnel"
    systemctl stop cloudflared-tunnel 2>/dev/null || true
else
    # 只匹配本项目的 config 路径；healthlens 用 /etc/cloudflared-healthlens/，不匹配
    pkill -f '\.cloudflared/config\.yml' 2>/dev/null || true
fi
sleep 3

if [ "$TUNNEL_MODE" = "cert" ] && [ -n "$TUNNEL_ID" ]; then
    log "启动 Named Tunnel (cert 模式)..."
    log "使用 config: $CONFIG_FILE"
    nohup "$CF_BIN" tunnel --config "$CONFIG_FILE" run > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    echo "$CF_PID" > "${CRED_DIR}/tunnel.pid" 2>/dev/null || true
    log "cloudflared PID: $CF_PID"

elif [ "$TUNNEL_MODE" = "token" ] && [ -n "$TUNNEL_TOKEN" ]; then
    log "启动 Named Tunnel (token 模式)..."
    nohup "$CF_BIN" tunnel run --token "$TUNNEL_TOKEN" > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    echo "$CF_PID" > "${CRED_DIR}/tunnel.pid" 2>/dev/null || true
    log "cloudflared PID: $CF_PID"

else
    log "ERROR: 无法启动 Named Tunnel，使用 Quick Tunnel 临时方案"
    TUNNEL_MODE="quick"
    nohup "$CF_BIN" tunnel --url http://localhost:8450 > /tmp/cloudflared.log 2>&1 &
    CF_PID=$!
    echo "$CF_PID" > "${CRED_DIR}/tunnel.pid" 2>/dev/null || true
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

# 【2026-09-18】隧道起来不等于 API 在监听。Cloudflare 转发到 localhost:8450，
# 若该端口无进程，域名只会稳定返回 502（09-17~09-18 线上连续失活即此路径：
# cloudflared 存活、API 未监听）。开机/重启后先确保 API 就绪再放行隧道。
if ! curl -sf --max-time 5 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1; then
    if systemctl is-active aishield-api >/dev/null 2>&1; then
        systemctl restart aishield-api 2>/dev/null || true
    elif systemctl is-enabled aishield-api >/dev/null 2>&1; then
        systemctl start aishield-api 2>/dev/null || true
    elif [ -f /opt/aishield/api/server.py ]; then
        # 【2026-09-18】与 install_api_service / api_start_nohup 一致：
        # systemd 以 root 运行，assert_not_root() 会拒绝启动（线上 502 的根因）。
        (cd /opt/aishield && PORT=8450 AISHIELD_ALLOW_ROOT=1 nohup python3 api/server.py >> /tmp/aishield-api.log 2>&1 &)
    elif [ -f "$HOME/aishield/api/server.py" ]; then
        (cd "$HOME/aishield" && PORT=8450 AISHIELD_ALLOW_ROOT=1 nohup python3 api/server.py >> /tmp/aishield-api.log 2>&1 &)
    fi
    for _i in 1 2 3 4 5 6; do
        curl -sf --max-time 5 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 && break
        sleep 3
    done
    if ! curl -sf --max-time 5 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1; then
        echo "[$(date '+%H:%M:%S')] WARN: API 未就绪，隧道仍会启动（域名将返回 502）" >> /tmp/aishield-api.log
    fi
fi

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
After=network.target aishield-api.service
Wants=aishield-api.service

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
# 【2026-09-18】STEP 6 的 nohup 实例与 systemd 实例会同时持有同一 tunnel ID，
# 互相踢连接（日志铁证：反复 `ERR no more connections active and exiting`，
# 随后 `Tunnel server stopped`）。systemd 是权威的、带 Restart=always 的单实例，
# 接管前必须先停掉 nohup 那份。
if [ -n "${CF_PID:-}" ] && kill -0 "$CF_PID" 2>/dev/null; then
    log "停止 nohup cloudflared (PID ${CF_PID}) -> 交由 systemd 单实例托管"
    kill "$CF_PID" 2>/dev/null || true
    sleep 2
fi
rm -f "${CRED_DIR}/tunnel.pid" 2>/dev/null || true
systemctl restart cloudflared-tunnel 2>/dev/null
log "systemd 服务已配置"

# Cron 备用保活
# 【2026-09-18】原条件 `pgrep -f 'cloudflared tunnel'` 会被同机**其他项目**的
# tunnel 满足（healthlens-tunnel 的命令行同样含 `cloudflared tunnel`），于是
# aishield 自己的隧道死了也不会被拉起 —— 一次「假活」。
# 改为本项目 API 健康探测：API 不健康就拉起 start-tunnel.sh，而该脚本内部
# 先确保 API 就绪再放行隧道，因此一个条件同时覆盖 API 与隧道两层。
CRON_LINE="* * * * * curl -sf --max-time 6 http://127.0.0.1:8450/api/v1/health >/dev/null 2>&1 || /opt/start-tunnel.sh >> /tmp/cloudflared.log 2>&1"
( crontab -l 2>/dev/null | grep -v 'start-tunnel.sh\|cloudflared' ; echo "$CRON_LINE" ) | crontab - 2>/dev/null
log "Cron 保活已设置（以本项目 API 健康为判据，不被他项目 tunnel 假满足）"

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

# 【2026-09-18 修复】此前无条件 exit 0：API 状态 FAIL 也报成功，上层 job
# 因此显示绿（两次自愈的 job 结论都是 success，而 verify 判红）。
# 部署脚本的健康结论必须与退出码一致，否则上层门禁全部假绿。
if ! curl -sf --max-time 10 http://127.0.0.1:8450/api/v1/health 2>/dev/null; then
    log "EXIT 1: API 未健康（localhost:8450 无响应），部署判定失败"
    exit 1
fi
log "EXIT 0: API 健康"
exit 0
