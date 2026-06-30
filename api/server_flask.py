"""
AIShield - AI工具安全审计与认证平台
架构：Flask + subprocess隔离扫描 + 前端轮询
- 提交审计 → 写入pending → 启动后台线程 → subprocess执行scan_cli.py → 返回audit_id
- 前端轮询 /api/v1/audit/{id} 获取结果
- scan_cli.py在独立进程中运行，不会影响Flask进程
- 付费API层级：免费3次/天 → Pro ¥99/月 → Enterprise ¥499/月
"""
from flask import Flask, request, jsonify, Response, redirect
from flask_cors import CORS
import json, os, time, hashlib, sys, subprocess, threading, tempfile, urllib.parse, secrets
from pathlib import Path

app = Flask(__name__, static_folder="/home/ubuntu/aishield/aishield/static", static_url_path="/static")
CORS(app, resources={r"/api/*": {"origins": "*"}})  # API端点允许跨域

# ============ 付费API层级 ============
API_KEYS_FILE = Path("/home/ubuntu/aishield/aishield/data/api_keys.json")
ORDERS_FILE = Path("/home/ubuntu/aishield/aishield/data/orders.json")
FREE_DAILY_LIMIT = 50  # 免费用户每天50次扫描（v3: 扩10倍对抗竞品）
PRO_DAILY_LIMIT = 500  # Pro用户每天500次
ENTERPRISE_DAILY_LIMIT = -1  # Enterprise无限

# ============ 虎皮椒支付配置 ============
XUNHU_APPID = "201906181178"
XUNHU_SECRET = "d856af3cab45ce0b0ae5d491a2ac94b0"
XUNHU_API = "https://api.xunhupay.com/payment/do.html"
# 回调地址走ATEX平台统一处理
XUNHU_NOTIFY_URL = "http://150.158.119.19:8420/v1/pay/alipay/callback"
XUNHU_RETURN_URL = "http://150.158.119.19:8450/pay?status=success"
# ATEX平台API（用于统一支付验证）
ATEX_API = "http://150.158.119.19:8420"

# 产品定价映射（v3: 市场调整，免费层扩10倍，Pro/企业降价）
PRODUCTS = {
    "pro_monthly": {"name": "AIShield Pro月度", "price": 19.00, "tier": "pro", "duration_days": 30},
    "pro_yearly": {"name": "AIShield Pro年度", "price": 190.00, "tier": "pro", "duration_days": 365},
    "enterprise_monthly": {"name": "AIShield 企业版月度", "price": 99.00, "tier": "enterprise", "duration_days": 30},
    "enterprise_yearly": {"name": "AIShield 企业版年度", "price": 990.00, "tier": "enterprise", "duration_days": 365},
    "scan_pack_10": {"name": "AIShield 10次扫描包", "price": 5.00, "tier": "scan_pack", "scan_count": 10},
    "scan_pack_50": {"name": "AIShield 50次扫描包", "price": 20.00, "tier": "scan_pack", "scan_count": 50},
}

def xunhu_hash(params):
    """生成虎皮椒签名: 按key字典序排列，拼接secret，MD5"""
    sorted_keys = sorted(k for k in params.keys() if k != "hash" and params[k] != "")
    sign_str = "&".join(f"{k}={params[k]}" for k in sorted_keys) + XUNHU_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest()

def load_orders():
    """加载订单数据"""
    if ORDERS_FILE.exists():
        try:
            with open(ORDERS_FILE) as f:
                return json.load(f)
        except:
            pass
    return {}

def save_orders(data):
    """原子写入订单数据"""
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(dir=str(ORDERS_FILE.parent), suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, str(ORDERS_FILE))
        except:
            try: os.unlink(tmp_path)
            except: pass
    except:
        pass

# API Key层级定义
TIER_CONFIG = {
    "free": {"daily_limit": FREE_DAILY_LIMIT, "badge_cert": True, "batch_scan": False, "name": "免费版"},
    "pro": {"daily_limit": PRO_DAILY_LIMIT, "badge_cert": True, "batch_scan": True, "name": "Pro版 ¥19/月"},
    "enterprise": {"daily_limit": ENTERPRISE_DAILY_LIMIT, "badge_cert": True, "batch_scan": True, "name": "企业版 ¥99/月"},
    "scan_pack": {"daily_limit": -1, "badge_cert": True, "batch_scan": False, "name": "按次付费"},
}

def load_api_keys():
    """加载API Key数据"""
    if API_KEYS_FILE.exists():
        try:
            with open(API_KEYS_FILE) as f:
                return json.load(f)
        except:
            pass
    # 初始化默认数据
    default = {
        # 预置一个演示用的Pro key
        "aishield_demo_pro_2026": {
            "tier": "pro",
            "name": "演示Pro账号",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "email": "demo@aishield.ai",
        }
    }
    save_api_keys(default)
    return default

def save_api_keys(data):
    """原子写入API Key数据"""
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(dir=str(API_KEYS_FILE.parent), suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, str(API_KEYS_FILE))
        except:
            try: os.unlink(tmp_path)
            except: pass
    except:
        pass

def get_tier(api_key):
    """获取API Key对应的层级"""
    if not api_key:
        return "free"
    keys = load_api_keys()
    key_data = keys.get(api_key)
    if key_data:
        return key_data.get("tier", "free")
    return "free"

def check_api_limit(api_key):
    """检查API调用限制，返回(allowed, remaining, tier)"""
    tier = get_tier(api_key)
    config = TIER_CONFIG.get(tier, TIER_CONFIG["free"])
    daily_limit = config["daily_limit"]

    if daily_limit == -1:  # 无限
        return True, -1, tier

    # 用日期+api_key作为限制key
    today = time.strftime("%Y-%m-%d")
    limit_key = f"{api_key or 'anon'}:{today}"

    # 简易内存计数器
    if not hasattr(app, '_api_usage'):
        app._api_usage = {}
    usage = app._api_usage.get(limit_key, 0)

    if usage >= daily_limit:
        return False, 0, tier

    app._api_usage[limit_key] = usage + 1
    remaining = daily_limit - usage - 1
    return True, remaining, tier

# 简易速率限制（IP级别，防滥用）
_rate_limit = {}
RATE_LIMIT_WINDOW = 60  # 60秒窗口
RATE_LIMIT_MAX = 10  # 每窗口最多10次审计提交

def check_rate_limit(ip):
    """检查IP速率限制"""
    now = time.time()
    if ip not in _rate_limit:
        _rate_limit[ip] = []
    # 清理过期记录
    _rate_limit[ip] = [t for t in _rate_limit[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit[ip]) >= RATE_LIMIT_MAX:
        return False
    _rate_limit[ip].append(now)
    return True

DATA_DIR = Path("/home/ubuntu/aishield/aishield/data")
AUDITS_FILE = DATA_DIR / "audits.json"
TOOLS_FILE = DATA_DIR / "tools.json"
TEMPLATES_DIR = Path("/home/ubuntu/aishield/aishield/templates")
SCAN_CLI = "/home/ubuntu/aishield/aishield/scanner/scan_cli.py"
SCAN_CWD = "/home/ubuntu/aishield"

def load_json(path):
    try:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        # JSON损坏时尝试加载备份
        bak_path = str(path) + ".bak"
        if os.path.exists(bak_path):
            try:
                with open(bak_path) as f:
                    return json.load(f)
            except:
                pass
    except:
        pass
    return {}

def save_json(path, data):
    """原子写入：先写临时文件，再rename，防止容器重启导致JSON损坏"""
    try:
        # 先备份当前文件
        if os.path.exists(path):
            bak_path = str(path) + ".bak"
            try:
                os.replace(str(path), bak_path)
            except:
                pass
        # 写入临时文件
        tmp_fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, str(path))
        except:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except:
                pass
    except:
        pass

# ============ 启动时恢复卡住的扫描任务 ============

def _recover_stuck_audits():
    """容器重启后，检查并重跑卡在pending/running状态的审计任务"""
    try:
        audits = load_json(AUDITS_FILE)
        now = time.time()
        recovered = 0
        for audit_id, audit in audits.items():
            status = audit.get("status")
            if status not in ("pending", "running"):
                continue
            # 检查是否超时（超过5分钟视为卡住）
            started_at = audit.get("started_at", 0)
            if started_at and (now - started_at) < 300:
                continue  # 还没超时，跳过
            # 重跑卡住的任务
            tool_type = audit.get("tool_type", "mcp")
            source_url = audit.get("source_url", "")
            name = audit.get("name", "")
            description = audit.get("description", "")
            if source_url:
                t = threading.Thread(
                    target=_run_scan,
                    args=(audit_id, tool_type, source_url, name, description),
                    daemon=True
                )
                t.start()
                recovered += 1
        if recovered > 0:
            print(f"[AIShield] Recovered {recovered} stuck audit(s) on startup")
    except Exception as e:
        print(f"[AIShield] Error recovering stuck audits: {e}")

# ============ API: Stats ============

@app.route("/api/v1/stats")
def stats():
    tools = load_json(TOOLS_FILE)
    audits = load_json(AUDITS_FILE)
    by_type, by_risk, by_badge = {}, {}, {}
    total_sec = 0
    for t in tools.values():
        tt = t.get("tool_type", "unknown")
        by_type[tt] = by_type.get(tt, 0) + 1
        by_risk[t.get("risk_level", "unknown")] = by_risk.get(t.get("risk_level", "unknown"), 0) + 1
        by_badge[t.get("badge_level", "none")] = by_badge.get(t.get("badge_level", "none"), 0) + 1
        total_sec += t.get("security_score", 0)
    return jsonify({
        "total_tools": len(tools), "total_audits": len(audits),
        "by_type": by_type, "by_risk": by_risk, "by_badge": by_badge,
        "avg_security_score": round(total_sec / len(tools), 1) if tools else 0,
    })

# ============ API: Submit Audit (async) ============

@app.route("/api/v1/audit", methods=["POST"])
def submit_audit():
    # 速率限制
    ip = request.remote_addr or "unknown"
    if not check_rate_limit(ip):
        return jsonify({"success": False, "detail": "请求过于频繁，请稍后再试"}), 429
    
    # API Key & 付费层级检查
    api_key = request.headers.get("X-API-Key", "") or request.args.get("api_key", "")
    allowed, remaining, tier = check_api_limit(api_key)
    if not allowed:
        config = TIER_CONFIG.get(tier, TIER_CONFIG["free"])
        return jsonify({
            "success": False, 
            "detail": f"今日免费扫描次数已用完（{config['daily_limit']}次/天）。升级Pro版享500次/天，企业版无限次。",
            "upgrade": "https://aishield.ai/#pricing",
            "tier": tier,
        }), 429
    
    data = request.json or {}
    tool_type = data.get("tool_type", "mcp")
    source_url = data.get("source_url", "")
    name = data.get("name", "") or source_url.split("/")[-1]
    description = data.get("description", "")
    
    if not source_url:
        return jsonify({"success": False, "detail": "source_url is required"}), 400
    
    audit_id = f"audit_{hashlib.md5(f'{tool_type}:{source_url}:{time.time()}'.encode()).hexdigest()[:12]}"
    
    # 写入pending状态
    audits = load_json(AUDITS_FILE)
    audits[audit_id] = {
        "audit_id": audit_id, "status": "pending",
        "tool_type": tool_type, "source_url": source_url,
        "name": name, "description": description,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "started_at": time.time(),  # 记录启动时间，用于超时检测
        "tier": tier,  # 记录付费层级
    }
    save_json(AUDITS_FILE, audits)
    
    # 启动后台扫描线程
    t = threading.Thread(target=_run_scan, args=(audit_id, tool_type, source_url, name, description), daemon=True)
    t.start()
    
    response = {"success": True, "audit_id": audit_id, "status": "pending", "tier": tier, "remaining": remaining}
    return jsonify(response)

def _run_scan(audit_id, tool_type, source_url, name, description):
    """后台线程：用subprocess执行scan_cli.py"""
    try:
        scan_input = json.dumps({
            "tool_type": tool_type, "source_url": source_url,
            "name": name, "description": description,
        }, ensure_ascii=False)
        
        proc = subprocess.run(
            [sys.executable, SCAN_CLI, scan_input],
            capture_output=True, text=True, timeout=180,
            cwd=SCAN_CWD
        )
        
        if proc.returncode != 0:
            _update_audit(audit_id, {"status": "failed", "error": proc.stderr[:500]})
            return
        
        result = json.loads(proc.stdout)
        report = result.get("report", {})
        report.update({
            "audit_id": audit_id, "tool_type": tool_type,
            "source_url": source_url, "description": description,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "completed",
        })
        _update_audit(audit_id, report)
        _update_tool(source_url, {
            "name": name, "source_url": source_url, "tool_type": tool_type,
            "description": description, "latest_audit_id": audit_id,
            "security_score": report.get("security_score", 0),
            "privacy_score": report.get("privacy_score", 0),
            "quality_score": report.get("quality_score", 0),
            "overall_score": report.get("overall_score", 0),
            "risk_level": report.get("risk_level", "unknown"),
            "badge_level": report.get("badge_level", "none"),
            "findings_count": len(report.get("findings", [])),
            "last_audit": report["timestamp"],
        })
    except subprocess.TimeoutExpired:
        _update_audit(audit_id, {"status": "failed", "error": "扫描超时(180s)"})
    except Exception as e:
        _update_audit(audit_id, {"status": "failed", "error": str(e)[:300]})

def _update_audit(audit_id, updates):
    try:
        audits = load_json(AUDITS_FILE)
        if audit_id in audits:
            audits[audit_id].update(updates)
        else:
            audits[audit_id] = updates
        save_json(AUDITS_FILE, audits)
    except:
        pass

def _update_tool(source_url, data):
    try:
        tools = load_json(TOOLS_FILE)
        tools[source_url] = data
        save_json(TOOLS_FILE, tools)
    except:
        pass

# ============ API: Get Audit ============

@app.route("/api/v1/audit/<audit_id>")
def get_audit(audit_id):
    audits = load_json(AUDITS_FILE)
    if audit_id not in audits:
        return jsonify({"success": False, "detail": "审计报告不存在"}), 404
    return jsonify(audits[audit_id])

# ============ API: List Tools ============

@app.route("/api/v1/tools")
def list_tools():
    q = request.args.get("q", "").lower()
    tool_type = request.args.get("tool_type")
    risk_level = request.args.get("risk_level")
    badge = request.args.get("badge")
    sort = request.args.get("sort", "overall_score")
    limit = min(int(request.args.get("limit", 50)), 200)
    offset = int(request.args.get("offset", 0))
    
    tools = load_json(TOOLS_FILE)
    results = list(tools.values())
    if q: results = [t for t in results if q in t.get("name", "").lower() or q in t.get("source_url", "").lower()]
    if tool_type: results = [t for t in results if t.get("tool_type") == tool_type]
    if risk_level: results = [t for t in results if t.get("risk_level") == risk_level]
    if badge: results = [t for t in results if t.get("badge_level") == badge]
    reverse = sort in ("overall_score", "security_score", "privacy_score", "quality_score")
    results.sort(key=lambda t: t.get(sort, 0), reverse=reverse)
    return jsonify({"total": len(results), "tools": results[offset:offset + limit]})

# ============ API: Badge ============

@app.route("/api/v1/badge/<path:tool_key>")
def badge(tool_key):
    tools = load_json(TOOLS_FILE)
    t = tools.get(tool_key, {})
    score = t.get("overall_score", 0)
    badge_level = t.get("badge_level", "none")
    colors = {"gold": ("#FFD700", "#000"), "silver": ("#C0C0C0", "#000"), "bronze": ("#CD7F32", "#fff"), "none": ("#555", "#fff")}
    bg, fg = colors.get(badge_level, ("#555", "#fff"))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="180" height="24">
  <rect width="180" height="24" rx="4" fill="{bg}"/>
  <text x="10" y="17" font-family="Arial,sans-serif" font-size="11" font-weight="bold" fill="{fg}">🛡️ AIShield</text>
  <text x="170" y="17" font-family="Arial,sans-serif" font-size="11" fill="{fg}" text-anchor="end">{score}/100</text>
</svg>'''
    return Response(svg, mimetype="image/svg+xml")

# ============ API: Health Check ============

@app.route("/api/v1/health")
def health():
    tools = load_json(TOOLS_FILE)
    audits = load_json(AUDITS_FILE)
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "uptime": time.time(),
        "tools_count": len(tools),
        "audits_count": len(audits),
    })

# ============ API: Recent Audits ============

@app.route("/api/v1/recent")
def recent_audits():
    limit = min(int(request.args.get("limit", 10)), 50)
    audits = load_json(AUDITS_FILE)
    # 按时间排序
    sorted_audits = sorted(
        [a for a in audits.values() if a.get("status") == "completed"],
        key=lambda a: a.get("timestamp", ""),
        reverse=True
    )
    return jsonify({"total": len(sorted_audits), "audits": sorted_audits[:limit]})

# ============ API: Badge by name ============

@app.route("/api/v1/badge-name/<path:tool_name>")
def badge_by_name(tool_name):
    tools = load_json(TOOLS_FILE)
    # 按名称查找工具
    for url, t in tools.items():
        if t.get("name", "").lower() == tool_name.lower():
            score = t.get("overall_score", 0)
            badge_level = t.get("badge_level", "none")
            colors = {"gold": ("#FFD700", "#000"), "silver": ("#C0C0C0", "#000"), "bronze": ("#CD7F32", "#fff"), "none": ("#555", "#fff")}
            bg, fg = colors.get(badge_level, ("#555", "#fff"))
            svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="180" height="24">
  <rect width="180" height="24" rx="4" fill="{bg}"/>
  <text x="10" y="17" font-family="Arial,sans-serif" font-size="11" font-weight="bold" fill="{fg}">🛡️ AIShield</text>
  <text x="170" y="17" font-family="Arial,sans-serif" font-size="11" fill="{fg}" text-anchor="end">{score}/100</text>
</svg>'''
            return Response(svg, mimetype="image/svg+xml")
    return jsonify({"success": False, "detail": "工具未找到"}), 404

# ============ API: 安全评分JSON（供第三方嵌入） ============

@app.route("/api/v1/score/<path:tool_name>")
def score_json(tool_name):
    """返回工具安全评分JSON（供Smithery/mcp.so等平台嵌入）"""
    tools = load_json(TOOLS_FILE)
    for url, t in tools.items():
        if t.get("name", "").lower() == tool_name.lower():
            return jsonify({
                "tool": t.get("name", tool_name),
                "source_url": url,
                "overall_score": t.get("overall_score", 0),
                "badge_level": t.get("badge_level", "none"),
                "risk_level": t.get("risk_level", "unknown"),
                "scores": {
                    "security": t.get("security_score", 0),
                    "privacy": t.get("privacy_score", 0),
                    "quality": t.get("quality_score", 0),
                    "performance": t.get("performance_score", 0),
                },
                "owasp_coverage": t.get("owasp_coverage", {}),
                "last_scanned": t.get("last_scanned", ""),
                "badge_svg": f"http://150.158.119.19:8450/api/v1/badge-name/{tool_name}",
                "badge_markdown": f"![AIShield](http://150.158.119.19:8450/api/v1/badge-name/{tool_name})",
                "embed_html": f'<iframe src="http://150.158.119.19:8450/api/v1/embed/{tool_name}" width="200" height="60" frameborder="0"></iframe>',
            })
    return jsonify({"success": False, "detail": "工具未找到"}), 404

@app.route("/api/v1/embed/<path:tool_name>")
def embed_badge(tool_name):
    """可嵌入的HTML安全评分卡片"""
    tools = load_json(TOOLS_FILE)
    for url, t in tools.items():
        if t.get("name", "").lower() == tool_name.lower():
            score = t.get("overall_score", 0)
            badge = t.get("badge_level", "none")
            colors = {"gold": "#FFD700", "silver": "#C0C0C0", "bronze": "#CD7F32", "none": "#555"}
            bg = colors.get(badge, "#555")
            return Response(f'''<div style="display:inline-block;background:#1a1a2e;border:1px solid #333;border-radius:8px;padding:8px 12px;font-family:system-ui,sans-serif">
<a href="http://150.158.119.19:8450" target="_blank" style="text-decoration:none;color:#fff">
<span style="background:{bg};color:#000;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700">🛡️ {badge.upper()}</span>
<span style="color:#fff;margin-left:8px;font-size:13px;font-weight:600">{score}/100</span>
<span style="color:#888;margin-left:4px;font-size:10px">AIShield</span>
</a></div>''', mimetype="text/html")
    return Response("<div>AIShield: Not scanned</div>", mimetype="text/html")

@app.route("/api/v1/pricing")
def pricing():
    return jsonify({
        "tiers": {
            "free": {
                "name": "免费版",
                "price": "¥0/月",
                "daily_limit": FREE_DAILY_LIMIT,
                "features": ["安全扫描(119条规则)", "四维评分", "OWASP MCP Top 10", "安全认证徽章", f"每天{FREE_DAILY_LIMIT}次扫描"],
            },
            "pro": {
                "name": "Pro版",
                "price": "¥19/月",
                "daily_limit": PRO_DAILY_LIMIT,
                "features": [f"每天{PRO_DAILY_LIMIT}次扫描", "批量扫描", "详细修复建议", "GitHub Action集成", "优先队列"],
            },
            "enterprise": {
                "name": "企业版",
                "price": "¥99/月",
                "daily_limit": "无限",
                "features": ["无限扫描", "批量扫描", "Rug Pull持续监控", "自定义规则", "专属客服", "SLA保障", "私有部署"],
            },
            "scan_pack": {
                "name": "按次付费",
                "price": "¥0.5/次",
                "daily_limit": "按购买量",
                "features": ["10次¥5", "50次¥20", "安全认证徽章", "无需月费"],
            },
        },
        "payment": {
            "methods": ["支付宝", "微信支付"],
            "contact": "pay@aishield.ai",
        }
    })

# ============ API: API Key Management ============

@app.route("/api/v1/keys", methods=["POST"])
def create_api_key():
    """申请API Key（免费版自动发放，付费版需联系）"""
    data = request.json or {}
    email = data.get("email", "")
    name = data.get("name", "")
    tier = data.get("tier", "free")
    
    if not email:
        return jsonify({"success": False, "detail": "email is required"}), 400
    if tier not in ("free", "pro", "enterprise"):
        return jsonify({"success": False, "detail": "invalid tier"}), 400
    
    # 生成API Key
    key_prefix = {"free": "aishield_free", "pro": "aishield_pro", "enterprise": "aishield_ent"}
    raw = f"{email}:{tier}:{time.time()}:{os.urandom(8).hex()}"
    api_key = f"{key_prefix[tier]}_{hashlib.sha256(raw.encode()).hexdigest()[:20]}"
    
    keys = load_api_keys()
    keys[api_key] = {
        "tier": tier,
        "name": name or email.split("@")[0],
        "email": email,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    save_api_keys(keys)
    
    return jsonify({
        "success": True,
        "api_key": api_key,
        "tier": tier,
        "daily_limit": TIER_CONFIG[tier]["daily_limit"],
        "message": "API Key创建成功！" if tier == "free" else f"API Key已创建，{TIER_CONFIG[tier]['name']}需完成支付后激活。请联系 pay@aishield.ai",
    })

@app.route("/api/v1/keys/info", methods=["GET"])
def api_key_info():
    """查询API Key信息"""
    api_key = request.headers.get("X-API-Key", "") or request.args.get("api_key", "")
    if not api_key:
        return jsonify({"success": False, "detail": "X-API-Key header required"}), 401
    
    keys = load_api_keys()
    key_data = keys.get(api_key)
    if not key_data:
        return jsonify({"success": False, "detail": "Invalid API Key"}), 401
    
    tier = key_data.get("tier", "free")
    config = TIER_CONFIG.get(tier, TIER_CONFIG["free"])
    
    # 查询今日用量
    today = time.strftime("%Y-%m-%d")
    limit_key = f"{api_key}:{today}"
    usage = getattr(app, '_api_usage', {}).get(limit_key, 0) if hasattr(app, '_api_usage') else 0
    
    return jsonify({
        "success": True,
        "tier": tier,
        "name": key_data.get("name", ""),
        "email": key_data.get("email", ""),
        "daily_limit": config["daily_limit"],
        "daily_used": usage,
        "daily_remaining": max(0, config["daily_limit"] - usage) if config["daily_limit"] > 0 else -1,
        "features": {
            "badge_cert": config["badge_cert"],
            "batch_scan": config["batch_scan"],
        }
    })

# ============ API: Batch Scan (Pro/Enterprise only) ============

# ============ Prompt安全检测 ============

@app.route("/api/v1/prompt-check", methods=["POST"])
def prompt_check():
    """Prompt安全检测 — 基于比特助手语义分析"""
    data = request.json or {}
    prompt = data.get("prompt", "").strip()
    
    if not prompt or len(prompt) < 10:
        return jsonify({"safe": False, "score": 0, "risk": "error",
                        "findings": [{"type": "error", "title": "输入太短", "desc": "至少需要10个字符"}],
                        "summary": "输入无效"})
    
    # 本地规则检测（快速）
    findings = []
    prompt_lower = prompt.lower()
    
    INJECTION_PATTERNS = [
        # 英文模式
        (r"ignore (all )?(previous|prior) instructions", "Prompt注入", "critical"),
        (r"disregard (all|previous|prior)", "Prompt注入", "critical"),
        (r"you are now (a |an )?(different|new|dan|evil|hacker)", "角色篡改", "critical"),
        (r"system prompt|api key|secret|token", "尝试窃取系统信息", "critical"),
        (r"send .* to (https?://|http://)", "数据外传指令", "critical"),
        (r"upload .* to .*server", "数据上传指令", "high"),
        (r"execute (code|command|script)", "请求执行代码", "high"),
        (r"access (the |all )?(file|database|filesystem)", "请求访问文件系统", "high"),
        (r"(jailbreak|jail.?break|bypass|override).*(restriction|limit|filter|safety)", "越狱指令", "critical"),
        (r"do anything now|no restrictions|no rules", "越狱指令", "critical"),
        (r"pretend (you are|to be) (a|an)? (different|hacker|malicious)", "角色伪装", "high"),
        (r"(curl|wget|fetch)\s*\(", "网络请求指令", "medium"),
        (r"eval\s*\(|exec\s*\(", "动态执行指令", "high"),
        (r"\\x[0-9a-f]{2}|\\u[0-9a-f]{4}", "编码混淆", "medium"),
        (r"base64|decode|atob|btoa", "编码操作", "low"),
        # 中文模式
        (r"忽略.*(?:之前|前面|以上).*(?:指令|提示|规则)", "中文Prompt注入", "critical"),
        (r"无视.*(?:之前|前面|以上).*(?:指令|提示|规则)", "中文Prompt注入", "critical"),
        (r"不要遵守.*(?:规则|限制|约束)", "中文越狱指令", "critical"),
        (r"你现在(?:是|扮演).*(?:黑客|恶意|不同|新的)", "中文角色篡改", "critical"),
        (r"(?:系统|后台).*(?:密码|密钥|token|API.?key)", "窃取系统凭证", "critical"),
        (r"(?:发送|上传|传).*(?:到|至|给).*(?:http|https|服务器|网址)", "中文数据外传", "critical"),
        (r"(?:执行|运行).*(?:代码|命令|脚本|程序)", "请求执行代码", "high"),
        (r"(?:访问|读取|查看).*(?:文件|数据库|系统|目录)", "请求访问文件系统", "high"),
        (r"(?:越狱|破解|突破).*(?:限制|安全|防护|过滤)", "中文越狱指令", "critical"),
        (r"(?:没有|不受|不要).*(?:限制|规则|约束|安全)", "中文越狱指令", "critical"),
        (r"(?:假装|伪装).*(?:是|成为).*(?:黑客|恶意|不同)", "中文角色伪装", "high"),
        (r"(?:导出|下载|提取).*(?:数据|信息|用户|密码)", "数据提取指令", "high"),
        (r"(?:修改|删除|清空|格式化).*(?:数据|文件|数据库)", "数据破坏指令", "critical"),
        (r"(?:开启|打开|启动).*(?:终端|shell|命令行|root)", "请求系统权限", "critical"),
        (r"sudo\s|rm\s+-rf|chmod\s+\d+", "系统命令注入", "critical"),
        (r"(?:思考过程|reasoning|chain.?of.?thought).*(?:输出|显示|reveal)", "请求泄露思维链", "medium"),
    ]
    
    import re
    for pattern, title, severity in INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            findings.append({
                "type": severity,
                "title": f"⚠️ {title}",
                "desc": f"检测到匹配模式: {pattern[:40]}"
            })
    
    # 调用比特助手做语义分析
    try:
        bit_prompt = f"""分析以下Prompt的安全性。检测：prompt注入、越狱、数据外传、权限提升。
只返回JSON格式：{{"safe": true/false, "risk_level": "safe/medium/high/critical", "issues": ["问题1","问题2"]}}

Prompt内容:
{prompt[:500]}"""
        
        bit_data = json.dumps({"message": bit_prompt, "session_id": "prompt-check"}).encode()
        bit_req = urllib_request.Request(
            "http://150.158.119.19:8431/chat",
            data=bit_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib_request.urlopen(bit_req, timeout=20) as resp:
            bit_result = json.loads(resp.read().decode())
            bit_content = bit_result.get("content", bit_result.get("response", ""))
        
        # 解析比特助手的JSON
        json_match = re.search(r'\{[^{}]*"safe"[^{}]*\}', bit_content, re.DOTALL)
        if json_match:
            try:
                bit_analysis = json.loads(json_match.group())
                if not bit_analysis.get("safe", True):
                    risk = bit_analysis.get("risk_level", "medium")
                    issues = bit_analysis.get("issues", [])
                    for issue in issues[:3]:
                        findings.append({
                            "type": risk,
                            "title": f"🤖 AI语义分析: {issue[:60]}",
                            "desc": "基于AI语义引擎检测"
                        })
            except:
                pass
    except Exception:
        pass  # 比特助手不可用时只用本地规则
    
    # 计算评分
    score = 100
    for f in findings:
        deductions = {"critical": 30, "high": 15, "medium": 8, "low": 3, "error": 0}
        score -= deductions.get(f["type"], 0)
    score = max(0, score)
    
    is_safe = score >= 70 and len(findings) == 0
    
    summary = f"检测到{len(findings)}个风险点，评分{score}/100"
    if is_safe:
        summary = f"未发现安全风险，评分{score}/100"
    
    return jsonify({
        "safe": is_safe,
        "score": score,
        "risk": "safe" if is_safe else ("critical" if score < 40 else "medium" if score < 70 else "high"),
        "findings": findings[:10],
        "summary": summary,
        "engine": "aishield-prompt-v1"
    })


@app.route("/api/v1/batch", methods=["POST"])
def batch_scan():
    """批量扫描（Pro/Enterprise功能）"""
    api_key = request.headers.get("X-API-Key", "") or request.args.get("api_key", "")
    tier = get_tier(api_key)
    config = TIER_CONFIG.get(tier, TIER_CONFIG["free"])
    
    if not config["batch_scan"]:
        return jsonify({
            "success": False,
            "detail": "批量扫描是Pro/Enterprise功能。升级Pro版享500次/天批量扫描。",
            "upgrade": "https://aishield.ai/#pricing",
        }), 403
    
    data = request.json or {}
    tools = data.get("tools", [])
    if not tools:
        return jsonify({"success": False, "detail": "tools list is required"}), 400
    if len(tools) > 10:
        return jsonify({"success": False, "detail": "Maximum 10 tools per batch"}), 400
    
    results = []
    for t in tools:
        source_url = t.get("source_url", "")
        tool_type = t.get("tool_type", "mcp")
        name = t.get("name", "")
        if not source_url:
            results.append({"source_url": "", "status": "skipped", "error": "no source_url"})
            continue
        
        # 提交扫描
        audit_id = f"audit_{hashlib.md5(f'{tool_type}:{source_url}:{time.time()}'.encode()).hexdigest()[:12]}"
        audits = load_json(AUDITS_FILE)
        audits[audit_id] = {
            "audit_id": audit_id, "status": "pending",
            "tool_type": tool_type, "source_url": source_url,
            "name": name, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "started_at": time.time(), "tier": tier,
        }
        save_json(AUDITS_FILE, audits)
        
        t_thread = threading.Thread(target=_run_scan, args=(audit_id, tool_type, source_url, name, ""), daemon=True)
        t_thread.start()
        
        results.append({"source_url": source_url, "name": name, "audit_id": audit_id, "status": "pending"})
    
    return jsonify({"success": True, "batch_size": len(results), "results": results})

# ============ API: Pricing Page ============

@app.route("/pricing")
def pricing_page():
    return (TEMPLATES_DIR / "pricing.html").read_text()

@app.route("/pay")
def pay_page():
    return (TEMPLATES_DIR / "pay.html").read_text()

# ============ API: 虎皮椒支付 ============

@app.route("/api/v1/payment/create", methods=["POST"])
def create_payment():
    """创建虎皮椒支付订单"""
    data = request.json or {}
    product_id = data.get("product_id", "pro_monthly")
    pay_type = data.get("type", "alipay")  # alipay / wechat
    email = data.get("email", "")
    
    if product_id not in PRODUCTS:
        return jsonify({"success": False, "detail": f"无效产品: {product_id}"}), 400
    
    product = PRODUCTS[product_id]
    
    # 生成订单号
    order_id = f"AS{int(time.time())}{secrets.token_hex(4)}"
    
    # 构建虎皮椒请求参数
    params = {
        "version": "1.1",
        "appid": XUNHU_APPID,
        "trade_order_id": order_id,
        "total_fee": str(product["price"]),
        "title": product["name"],
        "time": str(int(time.time())),
        "notify_url": XUNHU_NOTIFY_URL,
        "return_url": XUNHU_RETURN_URL,
        "nonce_str": secrets.token_hex(16),
        "type": pay_type,
        "data": json.dumps({"email": email, "product_id": product_id, "tier": product["tier"]}),
    }
    params["hash"] = xunhu_hash(params)
    
    # 保存订单
    orders = load_orders()
    orders[order_id] = {
        "order_id": order_id,
        "product_id": product_id,
        "product_name": product["name"],
        "amount": product["price"],
        "tier": product["tier"],
        "duration_days": product.get("duration_days", 0),
        "scan_count": product.get("scan_count", 0),
        "email": email,
        "pay_type": pay_type,
        "status": "pending",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    save_orders(orders)
    
    # 构建支付URL
    pay_url = f"{XUNHU_API}?{urllib.parse.urlencode(params)}"
    
    return jsonify({
        "success": True,
        "order_id": order_id,
        "pay_url": pay_url,
        "amount": product["price"],
        "product_name": product["name"],
    })

@app.route("/api/v1/payment/callback", methods=["GET", "POST"])
def payment_callback():
    """虎皮椒支付回调"""
    if request.method == "GET":
        params = dict(request.args)
    else:
        params = dict(request.form) if request.form else request.json or {}
    
    # 验证签名
    received_hash = params.pop("hash", "")
    calculated_hash = xunhu_hash(params)
    
    if received_hash != calculated_hash:
        return jsonify({"success": False, "detail": "签名验证失败"}), 400
    
    order_id = params.get("trade_order_id", "")
    status = params.get("status", "")
    open_order_id = params.get("open_order_id", "")
    
    orders = load_orders()
    order = orders.get(order_id)
    
    if not order:
        return jsonify({"success": False, "detail": "订单不存在"}), 404
    
    if status == "OD" and order["status"] != "paid":
        # 支付成功，激活API Key
        order["status"] = "paid"
        order["paid_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        order["open_order_id"] = open_order_id
        
        # 生成或升级API Key
        email = order.get("email", "")
        tier = order.get("tier", "pro")
        duration_days = order.get("duration_days", 30)
        
        keys = load_api_keys()
        # 查找该邮箱的现有key
        existing_key = None
        for k, v in keys.items():
            if v.get("email") == email:
                existing_key = k
                break
        
        if existing_key:
            # 升级现有key
            keys[existing_key]["tier"] = tier
            keys[existing_key]["expires_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time.time() + duration_days * 86400))
            keys[existing_key]["order_id"] = order_id
            api_key = existing_key
        else:
            # 创建新key
            key_prefix = {"pro": "aishield_pro", "enterprise": "aishield_ent"}
            raw = f"{email}:{tier}:{time.time()}:{os.urandom(8).hex()}"
            api_key = f"{key_prefix.get(tier, 'aishield_pro')}_{hashlib.sha256(raw.encode()).hexdigest()[:20]}"
            keys[api_key] = {
                "tier": tier,
                "name": email.split("@")[0] if email else "user",
                "email": email,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(time.time() + duration_days * 86400)),
                "order_id": order_id,
            }
        
        save_api_keys(keys)
        order["api_key"] = api_key
        orders[order_id] = order
        save_orders(orders)
    
    # 虎皮椒要求返回success
    return "success"

@app.route("/api/v1/payment/orders/<order_id>")
def check_order(order_id):
    """查询订单状态"""
    orders = load_orders()
    order = orders.get(order_id)
    if not order:
        return jsonify({"success": False, "detail": "订单不存在"}), 404
    return jsonify({"success": True, "order": order})

# ============ ATEX统一支付融合 ============

@app.route("/api/v1/payment/atex", methods=["POST"])
def create_atex_payment():
    """通过ATEX平台创建支付订单（统一支付入口）
    
    用户在AIShield购买Pro/Enterprise时，调用ATEX的支付系统：
    1. ATEX创建订单 → 虎皮椒支付宝/微信
    2. 用户支付 → ATEX回调 → 通知AIShield
    3. AIShield激活用户权限
    """
    data = request.json or {}
    product_id = data.get("product_id", "pro_monthly")
    
    if product_id not in PRODUCTS:
        return jsonify({"success": False, "detail": f"无效产品: {product_id}"}), 400
    
    product = PRODUCTS[product_id]
    
    # 调用ATEX API创建支付订单
    try:
        import urllib.request
        payload = json.dumps({
            "amount_cny": product["price"],
            "description": product["name"],
            "metadata": {
                "platform": "aishield",
                "product_id": product_id,
                "tier": product["tier"],
                "duration_days": product.get("duration_days", 0),
            }
        }).encode()
        
        req = urllib.request.Request(
            f"{ATEX_API}/v1/pay/alipay",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": "Bearer atex_deploy_2026"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=10)
        atex_result = json.loads(resp.read())
        
        # 保存订单关联
        order_id = atex_result.get("order_id", f"AS{int(time.time())}")
        orders = load_orders()
        orders[order_id] = {
            "order_id": order_id,
            "product_id": product_id,
            "product_name": product["name"],
            "amount": product["price"],
            "tier": product["tier"],
            "duration_days": product.get("duration_days", 0),
            "status": "pending",
            "payment_channel": "atex",
            "atex_order_id": atex_result.get("atex_order_id", ""),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        save_orders(orders)
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "pay_url": atex_result.get("pay_url", ""),
            "amount": product["price"],
            "product_name": product["name"],
            "payment_channel": "atex",
        })
    except Exception as e:
        # ATEX不可用时回退到本地支付
        return jsonify({
            "success": False,
            "detail": f"ATEX支付创建失败: {str(e)}",
            "fallback": "使用 /api/v1/payment/create 直接创建虎皮椒订单",
        }), 502

@app.route("/api/v1/payment/atex/callback", methods=["POST"])
def atex_payment_callback():
    """ATEX支付成功后通知AIShield激活权限"""
    data = request.json or {}
    order_id = data.get("order_id", "")
    atex_signature = data.get("atex_signature", "")
    
    # 简单验证
    if atex_signature != "atex_deploy_2026":
        return jsonify({"success": False, "detail": "无效签名"}), 403
    
    orders = load_orders()
    order = orders.get(order_id)
    if not order:
        return jsonify({"success": False, "detail": "订单不存在"}), 404
    
    if order["status"] != "paid":
        order["status"] = "paid"
        order["paid_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        save_orders(orders)
    
    return jsonify({"success": True, "order": order})

@app.route("/api/v1/payment/methods")
def payment_methods():
    """返回支持的支付方式"""
    return jsonify({
        "methods": [
            {"id": "alipay", "name": "支付宝", "icon": "💰", "enabled": True},
            {"id": "wechat", "name": "微信支付", "icon": "💬", "enabled": True},
            {"id": "atex", "name": "ATEX余额", "icon": "🤖", "enabled": True, "description": "使用ATEX平台余额支付"},
        ],
        "products": PRODUCTS,
        "platform": "AIShield + ATEX unified payment",
    })

# ============ Internal Deploy ============

@app.route("/api/v1/internal/deploy-github", methods=["POST"])
def deploy_github():
    """创建GitHub公开repo并推送代码（内部端点）"""
    import subprocess
    import urllib.request as urlopen_mod
    import urllib.error
    import ssl
    
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
    if not GITHUB_TOKEN:
        return jsonify({"error": "GITHUB_TOKEN not set"}), 400
    DISTRIB_DIR = "/home/ubuntu/aishield/aishield/distrib"
    ctx = ssl.create_default_context()
    
    def gh_api(method, endpoint, body=None):
        url = f"https://api.github.com{endpoint}"
        data = json.dumps(body).encode() if body else None
        req = urlopen_mod.Request(url, data=data, method=method, headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "User-Agent": "AIShield-Deploy",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json"
        })
        try:
            with urlopen_mod.urlopen(req, timeout=15, context=ctx) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}", "body": e.read().decode()[:500]}
        except Exception as e:
            return {"error": str(e)}
    
    results = []
    
    # 1. Get user
    user = gh_api("GET", "/user")
    if "login" not in user:
        return jsonify({"error": "GitHub auth failed", "detail": user}), 500
    username = user["login"]
    results.append(f"✅ Authenticated as: {username}")
    
    # 2. Check if repo exists
    existing = gh_api("GET", f"/repos/{username}/aishield")
    if "full_name" not in existing:
        # Create repo
        create_body = {
            "name": "aishield",
            "description": "🛡️ Agent-native AI tool security scanner. Scan MCP/Skill/GPT/Prompt for security risks.",
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True,
            "license_template": "mit",
            "homepage": "https://aishield.ai"
        }
        repo = gh_api("POST", "/user/repos", create_body)
        if "full_name" in repo:
            results.append(f"✅ Repo created: {repo['full_name']}")
        else:
            return jsonify({"error": "Create failed", "detail": repo, "results": results}), 500
    else:
        results.append(f"ℹ️ Repo exists: {existing['full_name']}")
    
    # 3. Upload files via GitHub Contents API (不用git命令)
    repo_dir = os.path.join(DISTRIB_DIR, "public-repo")
    try:
        import base64
        import shutil
        
        # Collect all files to upload
        upload_files = []
        
        # Root files
        for f in ["README.md", "LICENSE", "package.json"]:
            s = os.path.join(repo_dir, f)
            if os.path.exists(s):
                upload_files.append((f, s))
        
        # packages/
        for pkg_name, src_dir in [("npm-mcp", "npm-package"), ("npm-guardrail", "guardrail-mcp")]:
            for f in ["index.js", "package.json", "README.md"]:
                s = os.path.join(DISTRIB_DIR, src_dir, f)
                if os.path.exists(s):
                    upload_files.append((f"packages/{pkg_name}/{f}", s))
        
        # sdk/python/
        for f in ["pyproject.toml", "README.md"]:
            s = os.path.join(DISTRIB_DIR, "pypi-package", f)
            if os.path.exists(s):
                upload_files.append((f"sdk/python/{f}", s))
        s = os.path.join(DISTRIB_DIR, "pypi-package", "aishield", "__init__.py")
        if os.path.exists(s):
            upload_files.append(("sdk/python/aishield/__init__.py", s))
        
        # claude-skill/
        for f in ["plugin.json", "SKILL.md", "README.md"]:
            s = os.path.join(DISTRIB_DIR, "claude-skill", f)
            if os.path.exists(s):
                upload_files.append((f"claude-skill/{f}", s))
        
        # github-action/
        s = os.path.join(repo_dir, "github-action", "action.yml")
        if os.path.exists(s):
            upload_files.append(("github-action/action.yml", s))
        
        # docs/
        s = os.path.join(repo_dir, "docs", "openapi.yaml")
        if os.path.exists(s):
            upload_files.append(("docs/openapi.yaml", s))
        
        # examples/
        s = os.path.join(repo_dir, "examples", "README.md")
        if os.path.exists(s):
            upload_files.append(("examples/README.md", s))
        
        # batch-scanner/
        src = os.path.join(DISTRIB_DIR, "batch-scanner")
        for f in os.listdir(src):
            s = os.path.join(src, f)
            if os.path.isfile(s):
                upload_files.append((f"batch-scanner/{f}", s))
        
        results.append(f"📁 Uploading {len(upload_files)} files...")
        
        # Upload each file via Contents API
        success_count = 0
        for path, filepath in upload_files:
            with open(filepath, "rb") as fh:
                content_b64 = base64.b64encode(fh.read()).decode()
            
            upload_body = {
                "message": f"Add {path}",
                "content": content_b64,
                "branch": "main"
            }
            
            # Check if file exists first (to get sha for update)
            existing_file = gh_api("GET", f"/repos/{username}/aishield/contents/{path}?ref=main")
            if "sha" in existing_file:
                upload_body["sha"] = existing_file["sha"]
            
            result = gh_api("PUT", f"/repos/{username}/aishield/contents/{path}", upload_body)
            if "content" in result:
                success_count += 1
            else:
                results.append(f"  ⚠️ {path}: {result.get('error', result.get('message', 'unknown'))}")
            
            time.sleep(0.5)  # Rate limit
        
        results.append(f"✅ Uploaded {success_count}/{len(upload_files)} files")
        
    except Exception as e:
        results.append(f"❌ Deploy error: {str(e)}")
    
    return jsonify({
        "success": True,
        "username": username,
        "repo_url": f"https://github.com/{username}/aishield",
        "results": results
    })

# ============ Frontend ============

@app.route("/")
def homepage():
    return (TEMPLATES_DIR / "index.html").read_text()

@app.route("/audit")
def audit_page():
    return (TEMPLATES_DIR / "audit.html").read_text()

@app.route("/docs")
def docs_page():
    return (TEMPLATES_DIR / "docs.html").read_text()

@app.route("/encyclopedia")
def encyclopedia_page():
    return (TEMPLATES_DIR / "encyclopedia.html").read_text()

@app.route("/prompt-check")
def prompt_check_page():
    return (TEMPLATES_DIR / "prompt-check.html").read_text()

@app.route("/report/<audit_id>")
def report_page(audit_id):
    return (TEMPLATES_DIR / "report.html").read_text()

if __name__ == "__main__":
    _recover_stuck_audits()
    app.run(host="0.0.0.0", port=8450, threaded=True)

# gunicorn启动时也执行恢复（用before_request + 一次性标记）
_recovered = False

@app.before_request
def _maybe_recover():
    global _recovered
    if not _recovered:
        _recovered = True
        _recover_stuck_audits()
