"""
AIShield API Server — v4.2 Agent-First

Agent-First 改造:
  - POST /api/v1/agent/setup         — Agent 一键入驻（注册+API Key+快速指引）
  - GET  /api/v1/agent/status/{did}  — Agent 状态查询
  - POST /api/v1/agent/scan          — Agent 快速扫描
  - GET  /openapi.json                — OpenAPI 3.0.3 规范（Agent 自动发现）
  - 所有错误响应增加 error_code + error_id
  - MCP 新增 agent_register / agent_quick_scan 工具

端口: 8450
"""

import json
import os
import sys
import time
import uuid
import threading
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone, timedelta

# ── 路径 ──
BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE)
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, ".."))

from scanner.engine import scan, batch_scan
from scanner.rug_pull import detect_rug_pull
from scanner.handshake import verify_handshake
from scanner.vertical_risk import scan_vertical_risk
from scanner.rules import OWASP_MCP_TOP10, get_rule_count
from scanner.monitor import get_monitored_tools, add_monitor as add_tool_monitor, remove_monitor, check_version_change, check_all_monitored
from scanner.api_scanner import APIScanOrchestrator
from proxy import gateway as proxy_gateway

# ── Eco Dispatcher ──
try:
    from eco.dispatcher import init as _eco_init, dispatch_get as _eco_dispatch_get, dispatch_post as _eco_dispatch_post
    _eco_available = True
except ImportError:
    _eco_available = False
    def _eco_dispatch_get(handler): return False
    def _eco_dispatch_post(handler, data): return False
    def _eco_init(modules): pass

# ── 数据存储 ──
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

AUDIT_FILE = os.path.join(DATA_DIR, "audits.json")
USAGE_FILE = os.path.join(DATA_DIR, "usage.json")
WEBHOOK_PROCESSED_FILE = os.path.join(DATA_DIR, "webhook_processed.json")  # 幂等性：已处理的webhook checkout_id
CREDIT_TXN_FILE = os.path.join(DATA_DIR, "credit_transactions.json")  # 积分变动流水

TZ = timezone(timedelta(hours=8))

_lock = threading.Lock()


def _load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def _save_json(path, data):
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _record_usage(endpoint, ip, success=True):
    usage = _load_json(USAGE_FILE, {"daily": {}, "total": 0})
    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if today not in usage["daily"]:
        usage["daily"][today] = {"total": 0, "errors": 0, "by_endpoint": {}}
    usage["daily"][today]["total"] += 1
    if not success:
        usage["daily"][today]["errors"] += 1
    ep = usage["daily"][today].setdefault("by_endpoint", {})
    ep[endpoint] = ep.get(endpoint, 0) + 1
    usage["total"] = usage.get("total", 0) + 1
    # 只保留最近30天
    keys = sorted(usage["daily"].keys())
    if len(keys) > 30:
        for k in keys[:-30]:
            del usage["daily"][k]
    _save_json(USAGE_FILE, usage)


# ── 违禁词检测（简化版，完整版需外部词库）──
def check_banned_words(text, platform="all"):
    """中文违禁词检测"""
    # 基础违禁词库（示例，生产环境需完整词库）
    BASE_WORDS = [
        "赌博", "色情", "暴力", "恐怖", "毒品", "枪支", "弹药",
        "洗钱", "诈骗", "传销", "非法集资", "偷税漏税",
        "反动", "颠覆", "分裂", "邪教",
    ]
    
    platform_extra = {
        "douyin": ["刷粉", "刷赞", "买粉", "互赞", "引流", "私聊"],
        "xiaohongshu": ["引流", "私信", "加v", "加微", "约稿"],
        "wechat": ["砍价", "助力", "红包", "转账", "收款码"],
        "weibo": ["买粉", "刷量", "水军", "控评"],
        "bilibili": ["刷弹幕", "买播放", "刷硬币"],
    }
    
    found = []
    all_words = list(BASE_WORDS)
    if platform != "all" and platform in platform_extra:
        all_words.extend(platform_extra[platform])
    
    for word in all_words:
        if word in text:
            # 查找位置
            idx = text.find(word)
            context_start = max(0, idx - 10)
            context_end = min(len(text), idx + len(word) + 10)
            found.append({
                "word": word,
                "position": idx,
                "context": text[context_start:context_end],
                "platform": platform,
                "severity": "high" if word in BASE_WORDS else "medium",
            })
    
    return {
        "safe": len(found) == 0,
        "total_words": len(all_words),
        "found_count": len(found),
        "words": found,
        "platform": platform,
    }


# ── Prompt注入检测 ──
def check_prompt_injection(prompt):
    """Prompt安全检测"""
    from scanner.rules import MCP06_RULES, SKILL_EXTRA_RULES, ZH_PROMPT_INJECTION_RULES
    
    findings = []
    import re
    
    all_rules = dict(MCP06_RULES)
    all_rules.update(SKILL_EXTRA_RULES)
    all_rules.update(ZH_PROMPT_INJECTION_RULES)
    
    for pattern, (desc, severity) in all_rules.items():
        try:
            matches = list(re.finditer(pattern, prompt, re.IGNORECASE))
        except re.error:
            continue
        if matches:
            for m in matches[:3]:
                findings.append({
                    "type": "prompt_injection",
                    "severity": severity,
                    "description": desc,
                    "evidence": m.group()[:100],
                })
    
    # 零宽字符检测
    zero_width = ['\u200b', '\u200c', '\u200d', '\u2060', '\ufeff']
    for zwc in zero_width:
        if zwc in prompt:
            findings.append({
                "type": "prompt_injection",
                "severity": "critical",
                "description": f"零宽字符 U+{ord(zwc):04X}（可能隐藏指令）",
                "evidence": f"U+{ord(zwc):04X}",
            })
    
    # 评分
    score = 100
    for f in findings:
        score -= {"critical": 30, "high": 15, "medium": 5, "low": 1}.get(f["severity"], 0)
    score = max(0, min(100, score))
    
    risk = "safe" if score >= 80 else "low" if score >= 60 else "medium" if score >= 40 else "high" if score >= 20 else "critical"
    
    summary_parts = []
    critical = [f for f in findings if f["severity"] == "critical"]
    high = [f for f in findings if f["severity"] == "high"]
    if critical:
        summary_parts.append(f"发现{len(critical)}个严重风险")
    if high:
        summary_parts.append(f"发现{len(high)}个高风险")
    if not findings:
        summary_parts.append("未发现安全风险")
    
    return {
        "safe": score >= 80,
        "score": score,
        "risk": risk,
        "findings": findings,
        "total_findings": len(findings),
        "summary": "，".join(summary_parts),
    }


# ── HTTP Handler ──
class AIShieldHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """简化日志"""
        pass  # 静默日志，减少噪音
    
    def _send_json(self, data, status=200, rate_limit_remaining=None):
        """发送 JSON 响应，自动为错误响应添加 error_code 和 error_id"""
        try:
            # Agent-First: 自动为错误响应补充结构化错误码
            if status >= 400 and "error" in data and "error_code" not in data:
                error_code_map = {
                    400: "BAD_REQUEST", 401: "AUTH_REQUIRED", 403: "PERMISSION_DENIED",
                    404: "NOT_FOUND", 413: "BODY_TOO_LARGE", 429: "RATE_LIMITED", 500: "INTERNAL_ERROR",
                }
                data["error_code"] = error_code_map.get(status, "UNKNOWN_ERROR")
                data["error_id"] = f"err_{uuid.uuid4().hex[:12]}"
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Request-ID")
            self.send_header("X-Request-ID", f"req_{uuid.uuid4().hex[:12]}")
            # Agent-First: 速率限制标准头
            if rate_limit_remaining is not None:
                self.send_header("X-RateLimit-Remaining", str(rate_limit_remaining))
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionAbortedError, BrokenPipeError, OSError):
            pass
    
    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 100000:  # 100KB limit
            self._send_json({"error": "Request body too large (max 100KB)"}, 413)
            return None
        if length == 0:
            return ""
        try:
            return self.rfile.read(length).decode("utf-8", errors="replace")
        except Exception:
            return None

    def _generate_badge_svg(self, tool_name):
        """生成公开徽章SVG（用于GitHub README嵌入）"""
        # 品牌色
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="220" height="32" viewBox="0 0 220 32">'
            f'<defs>'
            f'<linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="0%">'
            f'<stop offset="0%" style="stop-color:#60a5fa"/>'
            f'<stop offset="100%" style="stop-color:#a78bfa"/>'
            f'</linearGradient>'
            f'</defs>'
            f'<rect width="220" height="32" rx="6" fill="#0f172a"/>'
            f'<rect width="80" height="32" rx="6" fill="url(#g)"/>'
            f'<rect x="74" width="6" height="32" fill="url(#g)"/>'
            f'<text x="40" y="21" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">AIShield</text>'
            f'<text x="88" y="21" font-family="Arial,sans-serif" font-size="11" fill="#e2e8f0">{tool_name[:16]}</text>'
            f'<text x="206" y="21" font-family="Arial,sans-serif" font-size="11" fill="#22c55e" text-anchor="end">&#x2713; Scanned</text>'
            f'</svg>'
        )
    
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Request-ID")
        self.end_headers()
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # ── Trust API (P1): 认证/信任评分/注册中心/Agent Card ──
        if (path.startswith("/api/v1/trust") or path.startswith("/api/v1/registry")
                or path == "/.well-known/agent-card.json"):
            try:
                import trust_api
                payload, status = trust_api.handle_get(path, parsed.query)
                self._send_json(payload, status)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("trust-api", self.client_address[0])
            return

        # Landing Page — Agent SEO
        if path == "/agent.html":
            html_path = os.path.join(BASE, "static", "agent.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("agent-page", self.client_address[0])
                return

        # OWASP MCP Top 10 中文解读博客
        if path == "/owasp-mcp-top10-guide/owasp-mcp-top10-guide.html" or path == "/owasp-mcp-top10-guide":
            html_path = os.path.join(PROJECT_ROOT, "owasp-mcp-top10-guide", "owasp-mcp-top10-guide.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("owasp-guide-page", self.client_address[0])
                return

# Demo: 委托链可视化
        if path == "/demo/delegation-chain":
            html_path = os.path.join(BASE, "static", "demo", "delegation-chain.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("demo-delegation-chain", self.client_address[0])
                return

        # ── 战略补齐前端 (F4 攻击图 / F5 Fleet / Phase3 企业控制台) ──
        _STATIC_PAGES = {
            "/attack-graph": "attack-graph.html",
            "/fleet": "fleet.html",
            "/enterprise": "enterprise.html",
        }
        if path in _STATIC_PAGES:
            html_path = os.path.join(BASE, "static", _STATIC_PAGES[path])
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage(path.lstrip("/"), self.client_address[0])
                return

        # Sitemap XML
        if path == "/sitemap.xml":
            sitemap_path = os.path.join(BASE, "static", "sitemap.xml")
            if os.path.exists(sitemap_path):
                with open(sitemap_path, "r", encoding="utf-8") as f:
                    xml = f.read()
                body = xml.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/xml; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

        # Robots.txt
        if path == "/robots.txt":
            robots_path = os.path.join(BASE, "static", "robots.txt")
            if os.path.exists(robots_path):
                with open(robots_path, "r", encoding="utf-8") as f:
                    txt = f.read()
                body = txt.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

        # Smithery MCP Server Card
        if path == "/.well-known/mcp/server-card.json":
            sc_path = os.path.join(BASE, "static", ".well-known", "mcp", "server-card.json")
            json_data = None
            if os.path.exists(sc_path):
                with open(sc_path, "r", encoding="utf-8") as f:
                    json_data = f.read()
            else:
                # Fallback: inline server card for deployments without the static file
                json_data = json.dumps({
                    "serverInfo": {"name": "AIShield", "version": "4.3.0",
                        "description": "AI Agent Security Shield — OWASP MCP Top 10 aligned security scanning. 227 rules covering prompt injection, zero-width characters, Rug Pull, permission audit, and dependency monitoring."},
                    "url": "https://aishield.tools/mcp",
                    "provider": {"name": "AIShield", "url": "https://github.com/lm203688/aishield"},
                    "license": "MIT",
                    "tools": [
                        {"name": "security_scan", "description": "[DEPRECATED — use aishield_scan] Full security audit for MCP tools/agents with OWASP MCP Top 10 alignment.",
                            "inputSchema": {"type": "object", "properties": {"tool_name": {"type": "string"}}, "required": ["tool_name"]},
                            "deprecated": true, "replacement": "aishield_scan"},
                        {"name": "prompt_injection_check", "description": "[DEPRECATED — use aishield_prompt_check] Detect prompt injection attacks in Chinese and English. 200+ pattern matching.",
                            "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]},
                            "deprecated": true, "replacement": "aishield_prompt_check"},
                        {"name": "banned_words_check", "description": "[DEPRECATED — use aishield_banned_words] Detect banned/sensitive words for 6 Chinese platforms.",
                            "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
                            "deprecated": true, "replacement": "aishield_banned_words"},
                        {"name": "rug_pull_detect", "description": "[DEPRECATED — use aishield_rug_pull] Detect Rug Pull risk in MCP tool repositories.",
                            "inputSchema": {"type": "object", "properties": {"source_url": {"type": "string"}}, "required": ["source_url"]},
                            "deprecated": true, "replacement": "aishield_rug_pull"},
                        {"name": "agent_register", "description": "One-click agent onboarding with API key and DID identity.",
                            "inputSchema": {"type": "object", "properties": {"agent_name": {"type": "string"}}, "required": ["agent_name"]}},
                        {"name": "dependency_monitor", "description": "[DEPRECATED — use aishield_scan with tool_type=monitor] Monitor MCP tool dependencies for version changes.",
                            "inputSchema": {"type": "object", "properties": {"source_url": {"type": "string"}}, "required": ["source_url"]},
                            "deprecated": true, "replacement": "aishield_scan"}
                    ]
                }, ensure_ascii=False, indent=2)
            body = json_data.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            _record_usage("smithery-server-card", self.client_address[0])
            return

        # Agent Card (A2A discovery)
        if path == "/.well-known/agent-card.json":
            agent_card_path = os.path.join(BASE, "static", ".well-known", "agent-card.json")
            if os.path.exists(agent_card_path):
                with open(agent_card_path, "r", encoding="utf-8") as f:
                    json_data = f.read()
                body = json_data.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
                _record_usage("agent-card", self.client_address[0])
                return

        # GEO: Atom Feed
        if path == "/feeds.xml":
            feeds_path = os.path.join(BASE, "static", "feeds.xml")
            if os.path.exists(feeds_path):
                with open(feeds_path, "r", encoding="utf-8") as f:
                    xml = f.read()
                body = xml.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/atom+xml; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(body)
                return

        # GEO: Web App Manifest
        if path == "/manifest.json":
            manifest_path = os.path.join(BASE, "static", "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r", encoding="utf-8") as f:
                    json_data = f.read()
                body = json_data.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/manifest+json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(body)
                return

        # GEO: Security Contact
        if path == "/security.txt":
            security_path = os.path.join(BASE, "static", ".well-known", "security.txt")
            if os.path.exists(security_path):
                with open(security_path, "r", encoding="utf-8") as f:
                    txt = f.read()
                body = txt.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

        # GEO: Humans.txt
        if path == "/humans.txt":
            humans_path = os.path.join(BASE, "static", "humans.txt")
            if os.path.exists(humans_path):
                with open(humans_path, "r", encoding="utf-8") as f:
                    txt = f.read()
                body = txt.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

        # GEO: Service Worker
        if path == "/service-worker.js":
            sw_path = os.path.join(BASE, "static", "service-worker.js")
            if os.path.exists(sw_path):
                with open(sw_path, "r", encoding="utf-8") as f:
                    js = f.read()
                body = js.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/javascript; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(body)
                return

        # 博客列表页 /blog
        if path == "/blog" or path == "/blog/":
            html = self._render_blog_index()
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            _record_usage("blog-index", self.client_address[0])
            return
        
        # 博客详情页 /blog/<slug>
        if path.startswith("/blog/") and len(path) > 6:
            slug = path[6:]
            html = self._render_blog_post(slug)
            if html:
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("blog-post", self.client_address[0])
                return
        
        # Landing Page — 定价页（积分制）
        if path == "/pricing":
            html_path = os.path.join(BASE, "static", "pricing.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("pricing-page", self.client_address[0])
                return

        # Creem 支付成功跳转页
        if path == "/recharge/success" or path == "/recharge/success/":
            html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>充值成功 - AIShield</title><style>body{{font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#0f172a;color:#e2e8f0}}.box{{text-align:center;padding:48px;border-radius:16px;background:#1e293b;max-width:480px}}h1{{color:#22c55e;font-size:28px;margin-bottom:12px}}p{{color:#94a3b8;margin-bottom:24px}}a{{display:inline-block;padding:12px 32px;background:#3b82f6;color:#fff;border-radius:8px;text-decoration:none;font-weight:600}}</style></head><body><div class="box"><h1>支付成功</h1><p>积分将在几分钟内到账，请刷新账户页面查看。<br>如未到账，请携带支付凭证联系客服。</p><a href="/pricing">返回定价页</a></div></body></html>'''
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Creem 支付取消跳转页
        if path == "/recharge/cancel" or path == "/recharge/cancel/":
            html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>支付取消 - AIShield</title><style>body{{font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#0f172a;color:#e2e8f0}}.box{{text-align:center;padding:48px;border-radius:16px;background:#1e293b;max-width:480px}}h1{{color:#f59e0b;font-size:28px;margin-bottom:12px}}p{{color:#94a3b8;margin-bottom:24px}}a{{display:inline-block;padding:12px 32px;background:#3b82f6;color:#fff;border-radius:8px;text-decoration:none;font-weight:600}}</style></head><body><div class="box"><h1>支付已取消</h1><p>您取消了本次支付。如需帮助，请联系客服。</p><a href="/pricing">返回定价页</a></div></body></html>'''
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Landing Page — MCP 安全扫描指南（GEO）
        if path == "/mcp-security-guide":
            html_path = os.path.join(BASE, "static", "mcp-security-guide.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("mcp-security-guide-page", self.client_address[0])
                return

        # Landing Page — 违禁词检测
        if path == "/banned-words":
            html_path = os.path.join(BASE, "static", "banned_words.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("banned-words-page", self.client_address[0])
                return

        # Landing Page — 扫描报告（SEO + 徽章引流）
        if path == "/report":
            html_path = os.path.join(BASE, "static", "scan_report.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("report-page", self.client_address[0])
                return

        # ── 工具安全档案页 ──
        # GET /tool/ → 重定向到 /tool/profile
        if path == "/tool/" or path == "/tool":
            self.send_response(302)
            self.send_header("Location", "/tool/profile")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        # GET /tool/profile → 返回工具安全档案页
        if path == "/tool/profile":
            html_path = os.path.join(BASE, "static", "tool_profile.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("tool-profile", self.client_address[0])
                return

        # 公开徽章页 — /badge/{tool_name} 直接返回SVG
        badge_match = re.match(r"^/badge/([^/]+)$", path)
        if badge_match:
            tool_name = badge_match.group(1)
            svg = self._generate_badge_svg(tool_name)
            body = svg.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(body)
            _record_usage("badge-page", self.client_address[0])
            return
        
        if path == "/api/v1/health":
            self._send_json({
                "status": "ok",
                "version": "4.2",
                "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)",
                "rules_count": get_rule_count("mcp"),
                "uptime": time.time(),
                "agent_first": True,
                "openapi": "/openapi.json",
                "agent_setup": "/api/v1/agent/setup",
            })
            _record_usage("health", self.client_address[0])
            return
        
        if path == "/api/v1/stats":
            usage = _load_json(USAGE_FILE, {"daily": {}, "total": 0})
            audits = _load_json(AUDIT_FILE, [])
            self._send_json({
                "total_scans": len(audits),
                "total_api_calls": usage.get("total", 0),
                "today": usage.get("daily", {}).get(datetime.now(TZ).strftime("%Y-%m-%d"), {}).get("total", 0),
                "owasp_categories": 10,
                "rules_count": get_rule_count("mcp"),
            })
            _record_usage("stats", self.client_address[0])
            return
        
        # ── 代理网关路由：列出可代理工具 ──
        if path == "/api/v1/proxy/tools":
            result = proxy_gateway.list_certified_tools()
            self._send_json(result)
            _record_usage("proxy-tools", self.client_address[0])
            return

        # ── 代理网关路由：调用统计 ──
        if path == "/api/v1/proxy/stats":
            result = proxy_gateway.get_call_stats()
            self._send_json(result)
            _record_usage("proxy-stats", self.client_address[0])
            return

        # ── 监控路由：列出监控中的工具 ──
        if path == "/api/v1/monitor/list":
            tools = get_monitored_tools()
            self._send_json({
                "success": True,
                "total": len(tools),
                "tools": tools,
            })
            _record_usage("monitor-list", self.client_address[0])
            return

        # 产品首页 — HTML Landing Page
        if path == "/":
            html_path = os.path.join(BASE, "static", "index.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html = f.read()
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                _record_usage("landing-page", self.client_address[0])
                return

        # ── Agent-First: OpenAPI 规范（Agent 自动发现）──
        if path == "/openapi.json":
            try:
                from api.openapi_spec import get_openapi_spec
                spec = get_openapi_spec()
                self._send_json(spec)
                _record_usage("openapi", self.client_address[0])
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── Agent-First: Agent 状态查询 ──
        agent_status_match = re.match(r"^/api/v1/agent/status/([^/]+)$", path)
        if agent_status_match:
            did = agent_status_match.group(1)
            try:
                from eco.agent_gateway import agent_status
                result = agent_status(did)
                http_status = 200 if result.get("success") else (result.get("http_status", 404) if "http_status" in result else 404)
                self._send_json(result, http_status)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("agent-status", self.client_address[0])
            return

        # API根节点 — JSON端点列表
        if path == "/api/v1":
            self._send_json({
                "name": "AIShield API",
                "version": "4.2",
                "description": "AI Agent Security & Trust Platform — Agent-First API",
                "openapi": "/openapi.json",
                "agent_setup": "/api/v1/agent/setup",
                "endpoints": [
                    "POST /api/v1/agent/setup — Agent one-click onboarding (register + API key + guide)",
                    "POST /api/v1/agent/scan — Agent quick scan (by name + description)",
                    "GET  /api/v1/agent/status/{did} — Agent status query",
                    "POST /api/v1/audit — Full security scan",
                    "POST /api/v1/prompt-check — Prompt injection detection",
                    "POST /api/v1/banned-words — Chinese banned words check",
                    "POST /api/v1/rug-pull — Rug pull detection",
                    "POST /api/v1/handshake — MCP handshake verification",
                    "POST /api/v1/mcp — MCP StreamableHTTP (JSON-RPC 2.0, 8 tools)",
                    "GET  /openapi.json — OpenAPI 3.0.3 spec (Agent auto-discovery)",
                    "GET  /api/v1/health — Health check",
                    "GET  /api/v1/stats — Usage statistics",
                    "GET  /api/v1/monitor/list — List monitored tools",
                    "POST /api/v1/monitor/add — Add tool to monitor",
                    "POST /api/v1/monitor/check — Check for version changes",
                    "GET  /api/v1/identity/agents — List registered agents",
                    "GET  /api/v1/badge/{tool} — Security badge SVG",
                    "GET  /api/v1/market/tools — Tool marketplace",
                    "GET  /api/v1/billing/plans — Pricing plans",
                    "GET  /api/v1/a2a/discover — Agent discovery",
                    "GET  /report — Public scan report landing page",
                    "GET  /badge/{tool} — Public badge SVG (redirect-ready)",
                    "POST /api/v1/proxy/call — Proxy tool call (certified only)",
                    "GET  /api/v1/proxy/tools — List proxyable certified tools",
                    "GET  /api/v1/proxy/stats — Proxy call statistics",
                    "POST /api/v1/account/register — User registration",
                    "POST /api/v1/account/login — User login",
                    "GET  /api/v1/account/me — Get user info",
                    "POST /api/v1/account/recharge — Recharge balance",
                    "GET  /api/v1/account/balance — Query balance",
                    "POST /api/v1/checkout/create — Create Creem checkout session",
                    "POST /api/v1/webhooks/creem — Creem payment webhook",
                ],
                "docs": "https://aishield.tools/docs",
                "mcp_install": "npx aishield-mcp-server",
            })
            return

        # ── 账户路由（在 eco dispatcher 之前处理）──
        if path == "/api/v1/account/me":
            try:
                from eco import account as _account_mod
                acct = _account_mod._get_auth_account(self)
                if not acct:
                    self._send_json({"error": "Unauthorized"}, 401)
                    return
                info = _account_mod.UserAccount().get_user_info(acct["account_id"])
                self._send_json({"success": True, "account": info})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/v1/account/balance":
            try:
                from eco import account as _account_mod
                acct = _account_mod._get_auth_account(self)
                if not acct:
                    self._send_json({"error": "Unauthorized"}, 401)
                    return
                balance = _account_mod.UserAccount().get_balance(acct["account_id"])
                self._send_json({"success": True, "account_id": acct["account_id"], "balance": balance})
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── Fleet 聚合 (F5) ──
        if path == "/api/v1/fleet":
            try:
                from scanner.fleet import summary as fleet_summary
                self._send_json({"success": True, **fleet_summary()})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("fleet", self.client_address[0])
            return
        if path == "/api/v1/fleet/list":
            try:
                from scanner.fleet import list_members
                self._send_json({"success": True, "members": list_members()})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("fleet-list", self.client_address[0])
            return

        # ── 认证列表 (Phase3 企业控制台) ──
        if path == "/api/v1/certify/list":
            try:
                from eco.badge import CertificationService
                certs = CertificationService().list_certifications()
                self._send_json({"success": True, "certifications": certs})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("certify-list", self.client_address[0])
            return

        # ── 虎皮椒：通道配置状态（脱敏，不含任何明文密钥）──
        if path == "/api/v1/pay/hupijiao/status":
            try:
                from eco.hupijiao import HupijiaoGateway
                self._send_json({"success": True, **HupijiaoGateway().status()})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── 虎皮椒：主动查单（回调丢失时的兜底）──
        if path == "/api/v1/pay/hupijiao/query":
            try:
                from eco.hupijiao import HupijiaoGateway
                q = parse_qs(parsed.query)
                res = HupijiaoGateway().query_order(
                    trade_order_id=(q.get("trade_order_id") or [None])[0],
                    open_order_id=(q.get("open_order_id") or [None])[0],
                )
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("hupijiao-query", self.client_address[0])
            return

        # ── 虎皮椒：本地订单台账 ──
        if path == "/api/v1/pay/hupijiao/orders":
            try:
                from eco.hupijiao import list_orders
                q = parse_qs(parsed.query)
                orders = list_orders(status=(q.get("status") or [None])[0])
                self._send_json({"success": True, "total": len(orders), "orders": orders})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── 运行时治理：策略与熔断状态（含审计链自校验）──
        if path == "/api/v1/governance/status":
            try:
                from eco import runtime_governance as rg
                self._send_json({"success": True, **rg.status()})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── 运行时治理：不可篡改审计日志 ──
        if path == "/api/v1/governance/audit":
            try:
                from eco import runtime_governance as rg
                q = parse_qs(parsed.query)
                limit = int((q.get("limit") or ["100"])[0])
                entries = rg.read_audit(limit=max(1, min(limit, 1000)),
                                        event=(q.get("event") or [None])[0])
                self._send_json({"success": True, "total": len(entries),
                                 "chain": rg.verify_chain(), "entries": entries})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── 支付上限：额度用量 ──
        if path == "/api/v1/spend-cap/usage":
            try:
                from eco import spend_cap
                q = parse_qs(parsed.query)
                self._send_json({"success": True, **spend_cap.usage(
                    (q.get("payer_id") or ["anonymous"])[0],
                    (q.get("currency") or ["CNY"])[0])})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── 持续鉴证：套餐 / 订阅列表 / 到期提醒 / 信任状态 ──
        if path == "/api/v1/attestation/plans":
            try:
                from eco import attestation
                self._send_json({"success": True, "plans": attestation.plans()})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/v1/attestation/list":
            try:
                from eco import attestation
                q = parse_qs(parsed.query)
                subs = attestation.list_subscriptions(
                    status=(q.get("status") or [None])[0],
                    payer_id=(q.get("payer_id") or [None])[0])
                self._send_json({"success": True, "total": len(subs), "subscriptions": subs})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/v1/attestation/expiring":
            try:
                from eco import attestation
                q = parse_qs(parsed.query)
                items = attestation.get_expiring(days=int((q.get("days") or ["7"])[0]))
                self._send_json({"success": True, "total": len(items), "subscriptions": items})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/v1/attestation/trust":
            try:
                from eco import attestation
                q = parse_qs(parsed.query)
                src = (q.get("source_url") or [""])[0]
                if not src:
                    self._send_json({"success": False, "error": "source_url 必填"}, 400)
                    return
                self._send_json({"success": True, **attestation.trust_status(src)})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("attestation-trust", self.client_address[0])
            return

        # Eco模块路由
        if _eco_dispatch_get(self):
            return

        self._send_json({"error": "Not found"}, 404)
    
    def _read_raw_body(self):
        """读取原始请求体（用于 webhook 签名验证）"""
        length = int(self.headers.get("Content-Length", 0))
        if length > 200000:  # 200KB
            return None
        if length == 0:
            return b""
        try:
            return self.rfile.read(length)
        except Exception:
            return None

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # ── Trust API (P1): 自动认证 / 显式认证 ──
        if path.startswith("/api/v1/trust"):
            try:
                body = self._read_body()
                if body is None:
                    return
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                import trust_api
                payload, status = trust_api.handle_post(path, data)
                self._send_json(payload, status)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("trust-api", self.client_address[0])
            return

        # ── SBOM / SARIF 导出 (P2) ──
        if path in ("/api/v1/export/sbom", "/api/v1/export/sarif"):
            try:
                body = self._read_body()
                if body is None:
                    return
                edata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from scanner.sbom import cyclonedx_sbom, sarif_from_scan
                sr = edata.get("scan_result") or edata.get("scan_report") or {}
                tname = edata.get("target_name", "unknown")
                tver = edata.get("target_version", "0.0.0")
                if path.endswith("sbom"):
                    payload = cyclonedx_sbom(sr, tname, tver)
                else:
                    payload = sarif_from_scan(sr, tname)
                self._send_json(payload, 200)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("export", self.client_address[0])
            return

        # ── 多客户端 MCP 配置分析（纯静态；服务端绝不执行配置中的命令）──
        if path == "/api/v1/scan/client-config":
            try:
                body = self._read_body()
                if body is None:
                    return
                cdata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from scanner.client_discovery import scan_client_configs, CLIENT_PROFILES
                configs = cdata.get("configs")
                if not configs:
                    self._send_json({
                        "error": "Missing 'configs'",
                        "hint": "传入 {path: content} 映射或 [{path, content, client, scope}] 列表",
                        "clients_supported": sorted({p["client"] for p in CLIENT_PROFILES}),
                    }, 400)
                    return
                result = scan_client_configs(configs)
                result["note"] = "静态分析，未执行任何配置中的命令"
                if cdata.get("enable_live_probe"):
                    from scanner.live_probe import probe_server_metadata
                    probes = [probe_server_metadata(s, enable=True) for s in result.get("inventory", [])]
                    result["live_probes"] = probes
                    result["note"] += "；已对远程 server 做只读元数据探测（不 spawn 任何命令）"
                self._send_json(result, 200)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("client-config-scan", self.client_address[0])
            return

        # ── 攻击路径求解 (M4) ──
        if path == "/api/v1/scan/attack-path":
            try:
                body = self._read_body()
                if body is None:
                    return
                apdata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from scanner.attack_path import solve_minimal_removal, attack_graph_json
                inv = apdata.get("inventory") or []
                tox = apdata.get("toxic_findings") or []
                self._send_json({
                    "recommendation": solve_minimal_removal(inv, tox),
                    "graph": attack_graph_json(inv, tox),
                }, 200)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("attack-path", self.client_address[0])
            return

        # ── Nucleus / SIEM 导出 (F3) ──
        if path in ("/api/v1/export/nucleus", "/api/v1/export/splunk"):
            try:
                body = self._read_body()
                if body is None:
                    return
                edata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from scanner.exporters import to_nucleus, to_splunk
                findings = edata.get("findings") or []
                if path.endswith("nucleus"):
                    payload = to_nucleus(findings, edata.get("asset_name", "aishield-scan"))
                else:
                    payload = to_splunk(findings)
                self._send_json(payload, 200)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("export", self.client_address[0])
            return

        # ── 策略即代码评估 (F6) ──
        if path == "/api/v1/policy/check":
            try:
                body = self._read_body()
                if body is None:
                    return
                pdata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from scanner.policy import evaluate_policy
                result = evaluate_policy(pdata.get("scan_result", {}), policy_path=pdata.get("policy_path"))
                self._send_json(result, 200)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("policy-check", self.client_address[0])
            return

        # ── 跨注册中心发现 (D3) ──
        if path == "/api/v1/registry/discover":
            try:
                body = self._read_body()
                if body is None:
                    return
                rdata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from scanner.registry_discovery import discover_across_registries
                result = discover_across_registries(rdata.get("query", ""), rdata.get("registries"))
                self._send_json(result, 200)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("registry-discover", self.client_address[0])
            return

        # ── OSV 实时 CVE (D1) ──
        if path == "/api/v1/osv":
            try:
                body = self._read_body()
                if body is None:
                    return
                odata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from scanner.osv import check_osv
                deps = odata.get("dependencies") or []
                self._send_json({"findings": check_osv(deps, use_network=True)}, 200)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("osv", self.client_address[0])
            return

        # ── Fleet 收纳 (F5) ──
        if path == "/api/v1/fleet/ingest":
            try:
                body = self._read_body()
                if body is None:
                    return
                fdata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from scanner.fleet import ingest as fleet_ingest
                res = fleet_ingest(fdata.get("scan_result") or fdata)
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("fleet-ingest", self.client_address[0])
            return

        # ── 付费认证：请求 x402 支付要求 (Phase3) ──
        if path == "/api/v1/certify/request-payment":
            try:
                body = self._read_body()
                if body is None:
                    return
                pdata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from eco.monetization import request_cert_payment
                res = request_cert_payment(pdata.get("source_url"), pdata.get("scan_report"),
                                           pdata.get("amount_usd"), pdata.get("payer_id"))
                code = 200 if res.get("success") else (
                    429 if res.get("status") == "blocked_by_spend_cap" else 400)
                self._send_json(res, code)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("certify-pay-req", self.client_address[0])
            return

        # ── 付费认证：履约签发 (Phase3) ──
        if path == "/api/v1/certify/fulfill":
            try:
                body = self._read_body()
                if body is None:
                    return
                fdata = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
                return
            try:
                from eco.monetization import fulfill_cert
                res = fulfill_cert(fdata.get("order_id"), fdata.get("payment_header"), fdata.get("scan_report"))
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("certify-fulfill", self.client_address[0])
            return

        # ── 虎皮椒回调（form-urlencoded，需 raw body 验签，必须回纯文本 success）──
        if path == "/api/v1/pay/hupijiao/notify":
            self._handle_hupijiao_notify()
            return

        # ── Creem Webhook（最高优先级，需要 raw body 验证签名）──
        if path == "/api/v1/webhooks/creem":
            self._handle_creem_webhook()
            return

        try:
            body = self._read_body()
            if body is None:
                self._send_json({"error": "Request body too large (max 100KB)"}, 413)
                return
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        # ── 虎皮椒：创建人民币支付订单 ──
        if path == "/api/v1/pay/hupijiao/create":
            try:
                from eco.hupijiao import HupijiaoGateway
                gw = HupijiaoGateway()
                res = gw.create_payment(
                    amount=data.get("amount", 0),
                    order_id=data.get("order_id"),
                    description=data.get("description", "AIShield 服务"),
                    payment=data.get("payment", "wechat"),
                    attach=data.get("attach", ""),
                    metadata=data.get("metadata"),
                )
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("hupijiao-create", self.client_address[0])
            return

        # ── 认证付费（人民币轨道 · 微信/支付宝）──
        if path == "/api/v1/certify/request-payment-cny":
            try:
                from eco.monetization import request_cert_payment_cny
                res = request_cert_payment_cny(
                    data.get("source_url", ""),
                    data.get("scan_report"),
                    data.get("payment", "wechat"),
                    data.get("amount_cny"),
                    data.get("payer_id"),
                )
                # 被支付上限拦下时返回 429（配额语义），便于客户端区分"付不起"和"参数错"
                code = 200 if res.get("success") else (
                    429 if res.get("status") == "blocked_by_spend_cap" else 400)
                self._send_json(res, code)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("certify-request-payment-cny", self.client_address[0])
            return

        # ══════════════════════════════════════════
        #  运行时治理（ASI08/10）：决策网关 · kill switch · 事故熔断
        # ══════════════════════════════════════════
        if path == "/api/v1/governance/evaluate":
            try:
                from eco import runtime_governance as rg
                res = rg.evaluate(data.get("server", ""), data.get("tool", ""),
                                  data.get("context"))
                # 拒绝用 403，让调用方无需解析 body 即可 fail-closed
                self._send_json({"success": True, **res}, 200 if res["allowed"] else 403)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("governance-evaluate", self.client_address[0])
            return

        if path == "/api/v1/governance/kill":
            try:
                from eco import runtime_governance as rg
                res = rg.kill(data.get("server", ""), data.get("reason", "manual kill switch"))
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("governance-kill", self.client_address[0])
            return

        if path == "/api/v1/governance/revive":
            try:
                from eco import runtime_governance as rg
                res = rg.revive(data.get("server", ""), data.get("reason", "manual revive"))
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/v1/governance/incident":
            try:
                from eco import runtime_governance as rg
                res = rg.record_incident(data.get("server", ""),
                                         data.get("severity", "high"),
                                         data.get("detail"))
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/v1/governance/policy":
            try:
                from eco import runtime_governance as rg
                action = (data.get("action") or "").strip()
                if action == "allow":
                    res = rg.allow_tool(data.get("server", ""), data.get("tools", "*"))
                elif action == "deny":
                    res = rg.deny_tool(data.get("server", ""), data.get("tools", "*"))
                elif action == "default_deny":
                    res = rg.set_default_deny(bool(data.get("enabled", True)))
                else:
                    res = {"success": False,
                           "error": "action 必须是 allow / deny / default_deny"}
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ══════════════════════════════════════════
        #  支付上限策略
        # ══════════════════════════════════════════
        if path == "/api/v1/spend-cap/policy":
            try:
                from eco import spend_cap
                res = spend_cap.set_policy(
                    data.get("payer_id", ""), data.get("currency", "CNY"),
                    data.get("per_tx"), data.get("daily"), data.get("monthly"),
                    data.get("note", ""))
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ══════════════════════════════════════════
        #  持续鉴证订阅
        # ══════════════════════════════════════════
        if path == "/api/v1/attestation/subscribe":
            try:
                from eco import attestation
                res = attestation.subscribe(
                    data.get("source_url", ""), data.get("plan", "monthly"),
                    data.get("payer_id"), data.get("cert_id"),
                    data.get("attest_interval_days", attestation.DEFAULT_ATTEST_INTERVAL_DAYS))
                self._send_json(res, 201 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("attestation-subscribe", self.client_address[0])
            return

        if path == "/api/v1/attestation/renew":
            try:
                from eco import attestation
                res = attestation.renew_subscription(
                    data.get("subscription_id", ""), data.get("periods", 1),
                    data.get("plan"))
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/v1/attestation/cancel":
            try:
                from eco import attestation
                res = attestation.cancel(data.get("subscription_id", ""),
                                         data.get("reason", ""))
                self._send_json(res, 200 if res.get("success") else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/v1/attestation/run-cycle":
            try:
                from eco import attestation
                sid = data.get("subscription_id")
                force = bool(data.get("force", False))
                if sid:
                    res = attestation.attest_once(sid, force=force)
                else:
                    res = attestation.run_cycle(force=force)
                self._send_json({"success": True, **res} if "success" not in res else res,
                                200 if res.get("success", True) else 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("attestation-run-cycle", self.client_address[0])
            return

        # ── Creem Checkout 创建 ──
        if path == "/api/v1/checkout/create":
            self._handle_creem_checkout(data)
            return

        # ── Agent-First: Agent 一键入驻（最高优先级，无认证）──
        if path == "/api/v1/agent/setup":
            try:
                from eco.agent_gateway import agent_setup
                result = agent_setup(data)
                status = 201 if result.get("success") else 400
                self._send_json(result, status)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("agent-setup", self.client_address[0])
            return

        # ── Agent-First: Agent 快速扫描（无认证）──
        if path == "/api/v1/agent/scan":
            try:
                from eco.agent_gateway import agent_quick_scan
                result = agent_quick_scan(data)
                status = 200 if result.get("success") else 400
                self._send_json(result, status)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            _record_usage("agent-scan", self.client_address[0])
            return

        # ── 账户路由（在 eco dispatcher 之前处理）──
        if path.startswith("/api/v1/account/"):
            try:
                from eco import account as _account_mod
                if path == "/api/v1/account/register":
                    name = data.get("name", "").strip()
                    email = data.get("email", "").strip()
                    password = data.get("password", "")
                    if not name or not email or not password:
                        self._send_json({"error": "name, email, password 均为必填"}, 400)
                        return
                    mgr = _account_mod.UserAccount()
                    result = mgr.register(name, email, password)
                    self._send_json({"success": True, **result}, 201)
                    return
                elif path == "/api/v1/account/login":
                    email = data.get("email", "").strip()
                    password = data.get("password", "")
                    if not email or not password:
                        self._send_json({"error": "email, password 均为必填"}, 400)
                        return
                    mgr = _account_mod.UserAccount()
                    result = mgr.login(email, password)
                    self._send_json({"success": True, **result})
                    return
                elif path == "/api/v1/account/recharge":
                    account_id = data.get("account_id", "").strip()
                    yuan_amount = float(data.get("amount", 0))
                    gateway = data.get("gateway", "alipay")
                    # amount 现在代表人民币金额，转换为积分（1元=100积分）
                    credit_amount = yuan_amount * 100
                    if not account_id or yuan_amount <= 0:
                        self._send_json({"error": "account_id 和 amount(元) 为必填，且 amount > 0。1元=100积分"}, 400)
                        return
                    mgr = _account_mod.UserAccount()
                    result = mgr.recharge(account_id, credit_amount, gateway)
                    result["yuan_amount"] = yuan_amount
                    result["credit_amount"] = credit_amount
                    result["rate"] = "1 CNY = 100 credits"
                    self._send_json({"success": True, **result})
                    return
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
                return
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
                return

        if path == "/api/v1/audit":
            self._handle_audit(data)
        elif path == "/api/v1/prompt-check":
            self._handle_prompt_check(data)
        elif path == "/api/v1/banned-words":
            self._handle_banned_words(data)
        elif path == "/api/v1/rug-pull":
            self._handle_rug_pull(data)
        elif path == "/api/v1/handshake":
            self._handle_handshake(data)
        elif path == "/api/v1/mcp":
            self._handle_mcp(data)
        elif path == "/api/v1/monitor/add":
            # ── 监控路由：添加工具到监控列表 ──
            source_url = data.get("source_url", "")
            name = data.get("name", "")
            if not source_url:
                self._send_json({"error": "source_url is required"}, 400)
                return
            result = add_tool_monitor(source_url, name)
            self._send_json(result)
            _record_usage("monitor-add", self.client_address[0])
        elif path == "/api/v1/monitor/check":
            # ── 监控路由：检查版本变更 ──
            source_url = data.get("source_url", "")
            if source_url:
                # 检查单个工具
                result = check_version_change(source_url)
                self._send_json(result)
            else:
                # 检查所有监控中的工具
                results = check_all_monitored()
                self._send_json({"success": True, "results": results, "total": len(results)})
            _record_usage("monitor-check", self.client_address[0])
        elif path == "/api/v1/proxy/call":
            # ── 代理网关路由：代理调用工具 ──
            target_url = data.get("target_url", "")
            tool_name = data.get("tool_name", "")
            arguments = data.get("arguments", {})
            agent_did = data.get("agent_did")
            if not target_url or not tool_name:
                self._send_json({"error": "target_url and tool_name are required"}, 400)
                return
            result = proxy_gateway.call_tool(target_url, tool_name, arguments, agent_did)
            status_code = 403 if result.get("blocked") else 502 if result.get("proxy_metadata", {}).get("proxy_status") in ("upstream_error", "proxy_error") else 200
            self._send_json(result, status_code)
            _record_usage("proxy-call", self.client_address[0])
        else:
            # Eco模块路由
            if _eco_dispatch_post(self, data):
                return
            self._send_json({"error": "Not found"}, 404)
    
    # ── 积分配置 ──
    CREDIT_COST = {"audit": 1, "prompt_check": 1, "batch_audit": 5, "banned_words": 0.5, "rug_pull": 1, "handshake": 0.5}
    FREE_DAILY_LIMIT = 50
    SIGNUP_BONUS = 100
    CREDIT_PER_YUAN = 100
    AGENT_DISCOUNT = 0.5  # Agent 调用半价
    
    # ── 博客渲染 ──
    def _render_blog_index(self):
        """渲染博客列表页"""
        blog_dir = os.path.join(BASE, "content", "blog")
        posts = []
        if os.path.exists(blog_dir):
            for fname in sorted(os.listdir(blog_dir), reverse=True):
                if fname.endswith(".md"):
                    fpath = os.path.join(blog_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    # 解析 frontmatter
                    title = fname.replace(".md", "").replace("-", " ").title()
                    date_str = ""
                    summary = ""
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            fm = parts[1]
                            body = parts[2]
                            for line in fm.split("\n"):
                                if line.startswith("title:"):
                                    title = line.split(":", 1)[1].strip().strip('"')
                                elif line.startswith("date:"):
                                    date_str = line.split(":", 1)[1].strip()
                            summary = body.strip()[:200].replace("\n", " ") + "..."
                    slug = fname.replace(".md", "")
                    posts.append({"slug": slug, "title": title, "date": date_str, "summary": summary})
        
        posts_html = ""
        for p in posts:
            posts_html += f'''<article style="margin-bottom:32px;padding-bottom:24px;border-bottom:1px solid #334155">
                <h2 style="margin-bottom:8px"><a href="/blog/{p['slug']}" style="color:#60a5fa;text-decoration:none">{p['title']}</a></h2>
                <p style="color:#94a3b8;font-size:14px;margin-bottom:8px">{p['date']}</p>
                <p style="color:#cbd5e1">{p['summary']}</p>
            </article>'''
        
        if not posts_html:
            posts_html = '<p style="color:#94a3b8">暂无博客文章，内容流水线将自动生成。</p>'
        
        return f'''<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>博客 - AIShield</title>
<style>body{{font-family:system-ui,sans-serif;margin:0;background:#0f172a;color:#e2e8f0;line-height:1.6}}
.container{{max-width:800px;margin:0 auto;padding:40px 20px}}
h1{{font-size:32px;margin-bottom:8px}}.subtitle{{color:#94a3b8;margin-bottom:40px}}
a{{color:#60a5fa}}</style></head><body>
<div class="container">
<h1>AIShield 博客</h1>
<p class="subtitle">AI Agent 安全洞察与 MCP 生态观察</p>
{posts_html}
<p style="margin-top:40px"><a href="/">← 返回首页</a></p>
</div></body></html>'''
    
    def _render_blog_post(self, slug):
        """渲染单篇博客"""
        safe_slug = "".join(c for c in slug if c.isalnum() or c in "-_")
        if safe_slug != slug:
            return None
        fpath = os.path.join(BASE, "content", "blog", safe_slug + ".md")
        if not os.path.exists(fpath):
            return None
        
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 简单 Markdown → HTML 转换
        title = safe_slug.replace("-", " ").title()
        date_str = ""
        body = content
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm = parts[1]
                body = parts[2].strip()
                for line in fm.split("\n"):
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("date:"):
                        date_str = line.split(":", 1)[1].strip()
        
        # 简单转换
        html_body = body
        html_body = html_body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # 标题
        for i in range(6, 0, -1):
            html_body = html_body.replace(f"{'#' * i} ", f"<h{i} style=\"margin-top:24px;margin-bottom:12px;color:#f1f5f9\">")
            html_body = html_body.replace(f"\n{'#' * i} ", f"\n<h{i} style=\"margin-top:24px;margin-bottom:12px;color:#f1f5f9\">")
        # 粗体
        html_body = html_body.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
        # 代码块
        import re
        html_body = re.sub(r'```(\w+)?\n(.*?)```', r'<pre style="background:#1e293b;padding:16px;border-radius:8px;overflow-x:auto"><code>\2</code></pre>', html_body, flags=re.DOTALL)
        # 行内代码
        html_body = re.sub(r'`([^`]+)`', r'<code style="background:#1e293b;padding:2px 6px;border-radius:4px">\1</code>', html_body)
        # 段落
        paragraphs = html_body.split("\n\n")
        new_paras = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith("<"):
                p = f'<p style="margin-bottom:16px;color:#cbd5e1">{p}</p>'
            new_paras.append(p)
        html_body = "\n".join(new_paras)
        # 链接
        html_body = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#60a5fa">\1</a>', html_body)
        
        return f'''<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - AIShield Blog</title>
<style>body{{font-family:system-ui,sans-serif;margin:0;background:#0f172a;color:#e2e8f0;line-height:1.6}}
.container{{max-width:800px;margin:0 auto;padding:40px 20px}}
h1{{font-size:28px;margin-bottom:8px;color:#f1f5f9}}.meta{{color:#94a3b8;font-size:14px;margin-bottom:32px}}
a{{color:#60a5fa}}pre{{background:#1e293b;padding:16px;border-radius:8px;overflow-x:auto}}
code{{font-family:monospace}}ul,ol{{color:#cbd5e1}}li{{margin-bottom:8px}}
blockquote{{border-left:4px solid #3b82f6;padding-left:16px;margin-left:0;color:#94a3b8}}</style></head><body>
<div class="container">
<h1>{title}</h1>
<p class="meta">{date_str} | <a href="/blog">← 返回博客列表</a></p>
<div class="content">{html_body}</div>
<p style="margin-top:40px"><a href="/blog">← 返回博客列表</a> | <a href="/">首页</a></p>
</div></body></html>'''
    
    def _build_recharge_cta(self, balance, is_agent=False, is_anonymous=False):
        """
        构建充值/注册引导CTA信息（获客转化核心）
        返回 dict 包含结构化引导信息
        """
        base_url = "https://aishield.tools"
        if is_anonymous:
            return {
                "cta_type": "signup",
                "message": f"注册即送 {self.SIGNUP_BONUS} 积分体验金，解锁更多扫描次数",
                "action_url": f"{base_url}/pricing",
                "action_text": "免费注册",
                "remaining_tier": "anonymous_free",
            }
        # 积分不足或余额低时的引导
        agent_note = "Agent 用户享 5 折优惠" if is_agent else ""
        recommended = "daily_brief" if balance < 50 else "intelligence_pro"
        pkg_name = "Daily Brief (500积分)" if recommended == "daily_brief" else "Intelligence Pro (5000积分)"
        return {
            "cta_type": "recharge",
            "message": f"积分余额较低 ({balance:.0f} 积分)。{agent_note}",
            "action_url": f"{base_url}/pricing",
            "action_text": "立即充值",
            "recommended_package": {
                "key": recommended,
                "name": pkg_name,
                "checkout_url": f"{base_url}/api/v1/checkout/create?product_key={recommended}",
            },
            "remaining_tier": "registered",
        }
    
    def _identify_and_deduct(self, endpoint):
        """
        从 Authorization 头识别用户并扣除积分。
        返回 (account_dict, credits_deducted, is_agent, error_response_or_None)
        """
        auth_header = self.headers.get("Authorization", "")
        has_key = auth_header.startswith("Bearer ")
        api_key = auth_header[7:].strip() if has_key else ""
        
        credit_cost = self.CREDIT_COST.get(endpoint, 1)
        
        if has_key and api_key:
            # 有 API Key → 积分扣减
            try:
                from eco import account as _acct
                mgr = _acct.UserAccount()
                account = mgr.get_by_api_key(api_key)
                if not account:
                    return None, 0, False, ("API Key 无效", 401)
                if account.get("status") != "active":
                    return None, 0, False, ("账户已禁用", 403)
                
                balance = account.get("balance", 0)
                # Agent 身份判断：account_id 以 "agent-" 开头
                is_agent = account["account_id"].startswith("agent-")
                actual_cost = credit_cost * (self.AGENT_DISCOUNT if is_agent else 1)
                
                if balance < actual_cost:
                    # P0: 积分不足 — 强CTA引导充值
                    cta = self._build_recharge_cta(balance, is_agent)
                    error_payload = {
                        "error": f"积分不足: 当前 {balance:.0f} 积分，需要 {actual_cost:.0f} 积分。",
                        "cta": cta,
                        "hint": "注册即送 100 积分体验金，充值 1 元 = 100 积分",
                    }
                    return account, 0, is_agent, (error_payload, 402)
                
                # 扣减积分
                mgr.consume(account["account_id"], actual_cost)
                
                # P1: 余额预警 — 低于20积分时提前引导（不阻断，只提示）
                if balance - actual_cost < 20:
                    cta = self._build_recharge_cta(balance - actual_cost, is_agent)
                    return account, actual_cost, is_agent, ("LOW_BALANCE_WARNING", cta)
                
                return account, actual_cost, is_agent, None
            except ValueError as e:
                return None, 0, False, (str(e), 400)
            except Exception:
                return None, 0, False, ("认证服务异常", 500)
        else:
            # 无 API Key → 匿名免费层
            today = datetime.now(TZ).strftime("%Y-%m-%d")
            usage = _load_json(USAGE_FILE, {"daily": {}, "total": 0})
            today_endpoint_count = usage.get("daily", {}).get(today, {}).get("by_endpoint", {}).get(endpoint, 0)
            remaining = max(0, self.FREE_DAILY_LIMIT - today_endpoint_count)
            
            if today_endpoint_count >= self.FREE_DAILY_LIMIT:
                # 免费额度用完 — 强CTA引导注册
                cta = self._build_recharge_cta(0, is_anonymous=True)
                error_payload = {
                    "error": f"匿名免费额度已用完（{self.FREE_DAILY_LIMIT}次/天）。",
                    "cta": cta,
                    "hint": "注册即送 100 积分体验金，可扫描 100 次",
                }
                return None, 0, False, (error_payload, 429)
            
            # P1: 免费额度快用完预警（剩余<=5次时）
            if remaining <= 5:
                cta = self._build_recharge_cta(0, is_anonymous=True)
                return None, 0, False, ("FREE_LIMIT_WARNING", {"remaining": remaining, "cta": cta})
            
            return None, 0, False, None  # 匿名免费放行
    
    def _handle_audit(self, data):
        source_url = data.get("source_url", "")
        tool_type = data.get("tool_type", "mcp")
        name = data.get("name", "")
        
        if not source_url:
            self._send_json({"error": "source_url is required"}, 400)
            return
        
        # ── 积分扣减 / 免费额度检查 ──
        account, credits_used, is_agent, auth_error = self._identify_and_deduct("audit")
        
        # 处理预警类型（不阻断请求）
        balance_warning = None
        free_limit_warning = None
        if auth_error and auth_error[0] == "LOW_BALANCE_WARNING":
            balance_warning = auth_error[1]  # cta dict
            auth_error = None
        elif auth_error and auth_error[0] == "FREE_LIMIT_WARNING":
            free_limit_warning = auth_error[1]  # {"remaining": N, "cta": {...}}
            auth_error = None
        
        if auth_error:
            # 结构化错误响应（402/429 含 CTA）
            status_code = auth_error[1]
            if isinstance(auth_error[0], dict):
                payload = auth_error[0]
                payload["error_code"] = "INSUFFICIENT_CREDITS" if status_code == 402 else "RATE_LIMIT"
            else:
                payload = {"error": auth_error[0], "error_code": "AUTH_REQUIRED"}
            self._send_json(payload, status_code)
            _record_usage("audit", self.client_address[0], success=False)
            return
        
        try:
            result = scan(source_url, tool_type, name)

            # P2: 生成 CycloneDX SBOM + SARIF, 供 CI / 安全工具链直接消费
            try:
                from scanner.sbom import attach_sbom_sarif
                attach_sbom_sarif(result, name or source_url, result.get("version", "0.0.0"))
            except Exception:
                pass

            # 保存审计记录
            audits = _load_json(AUDIT_FILE, [])
            audits.append({
                "name": result.get("name", ""),
                "source_url": source_url,
                "tool_type": tool_type,
                "overall_score": result.get("overall_score", 0),
                "badge_level": result.get("badge_level", "none"),
                "risk_level": result.get("risk_level", ""),
                "total_findings": result.get("total_findings", 0),
                "scanned_at": result.get("scanned_at", ""),
            })
            if len(audits) > 1000:
                audits = audits[-500:]
            _save_json(AUDIT_FILE, audits)
            
            # P0-3.1: Badge <-> Scan 联动
            certification = None
            try:
                overall_score = result.get("overall_score", 0)
                if overall_score >= 80:
                    from eco import badge as _badge_mod
                    cert_svc = _badge_mod.CertificationService()
                    certification = cert_svc.certify_tool(
                        source_url=source_url,
                        scan_report=result,
                    )
            except Exception:
                pass
            
            # 品牌水印
            response = {
                "success": True,
                # 顶层便捷字段：供 CI 门禁 / Agent 直接读取，避免深路径取值失败静默得 0。
                # 与 report.overall_score 恒等，属附加字段，不破坏既有结构。
                "score": result.get("overall_score", 0),
                "badge_level": result.get("badge_level", "none"),
                "risk_level": result.get("risk_level", ""),
                "report": result,
                "powered_by": {
                    "name": "AIShield",
                    "url": "https://aishield.tools",
                    "version": "4.1",
                },
            }
            
            if certification:
                response["certification"] = certification
            
            # 附加积分信息（有身份时）
            if account:
                from eco import account as _acct
                current_balance = _acct.UserAccount().get_balance(account["account_id"])
                response["credits"] = {
                    "deducted": credits_used,
                    "balance": current_balance,
                    "is_agent": is_agent,
                    "agent_discount": self.AGENT_DISCOUNT if is_agent else None,
                }
                # 余额预警嵌入
                if balance_warning:
                    response["credits"]["warning"] = balance_warning
                    response["upgrade_prompt"] = balance_warning
            else:
                response["credits"] = {"deducted": 0, "tier": "anonymous_free"}
                # 免费额度预警嵌入
                if free_limit_warning:
                    response["credits"]["warning"] = free_limit_warning
                    response["upgrade_prompt"] = free_limit_warning["cta"]
            
            self._send_json(response)
            _record_usage("audit", self.client_address[0])
        
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
            _record_usage("audit", self.client_address[0], success=False)
    
    def _handle_prompt_check(self, data):
        prompt = data.get("prompt", "")
        if len(prompt) < 10:
            self._send_json({"error": "prompt must be at least 10 characters"}, 400)
            return
        
        result = check_prompt_injection(prompt)
        # 品牌水印
        result["powered_by"] = {
            "name": "AIShield",
            "url": "https://aishield.tools",
            "version": "4.1",
        }
        self._send_json(result)
        _record_usage("prompt-check", self.client_address[0])
    
    def _handle_banned_words(self, data):
        text = data.get("text", "")
        platform = data.get("platform", "all")
        if not text:
            self._send_json({"error": "text is required"}, 400)
            return
        
        result = check_banned_words(text, platform)
        # 品牌水印
        result["powered_by"] = {
            "name": "AIShield",
            "url": "https://aishield.tools",
            "version": "4.1",
        }
        self._send_json(result)
        _record_usage("banned-words", self.client_address[0])
    
    def _handle_rug_pull(self, data):
        """Rug Pull检测"""
        source_url = data.get("source_url", "")
        if not source_url:
            self._send_json({"error": "source_url is required"}, 400)
            return
        try:
            result = detect_rug_pull(source_url)
            self._send_json(result)
            _record_usage("rug-pull", self.client_address[0])
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
            _record_usage("rug-pull", self.client_address[0], success=False)
    
    def _handle_handshake(self, data):
        """MCP握手验证"""
        source_url = data.get("source_url", "")
        if not source_url:
            self._send_json({"error": "source_url is required"}, 400)
            return
        try:
            result = verify_handshake(source_url)
            self._send_json(result)
            _record_usage("handshake", self.client_address[0])
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
            _record_usage("handshake", self.client_address[0], success=False)
    
    # ── Creem Checkout 创建 ──
    def _handle_creem_checkout(self, data):
        """创建 Creem Checkout Session"""
        product_key = data.get("product_key", "").strip()
        account_id = data.get("account_id", "").strip()
        customer_email = data.get("customer_email", "").strip()
        success_url = data.get("success_url", "").strip()

        if not product_key:
            self._send_json({"error": "product_key 为必填（可选: daily_brief, intelligence_pro, api_access, lifetime, full_db, single_domain）"}, 400)
            return

        if not account_id:
            self._send_json({"error": "account_id 为必填（传入您的 AIShield 账户 ID）"}, 400)
            return

        try:
            from eco.payment import CreemGateway
            gateway = CreemGateway()
            result = gateway.create_checkout(
                product_key=product_key,
                account_id=account_id,
                customer_email=customer_email or None,
                success_url=success_url or None,
            )

            if "error" in result:
                self._send_json(result, 400)
            else:
                self._send_json({"success": True, **result})
                _record_usage("checkout-create", self.client_address[0])
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
            _record_usage("checkout-create", self.client_address[0], success=False)

    # ── Creem Webhook 处理 ──
    def _handle_hupijiao_notify(self):
        """虎皮椒异步回调（application/x-www-form-urlencoded）。

        协议要求：验签通过必须回**纯文本 `success`**，否则平台会持续重推。
        安全上依赖 eco.hupijiao.verify_notify 的四道校验：
        appid 归属 → 签名（恒定时间比对）→ 支付状态 → 金额未被篡改 + 重放去重。
        """
        raw_body = self._read_raw_body()
        if raw_body is None:
            self._send_text("fail", 413)
            return

        try:
            from eco.hupijiao import HupijiaoGateway
            gw = HupijiaoGateway()
            result = gw.handle_notify(raw_body)
        except Exception as e:
            print(f"❌ 虎皮椒回调处理异常: {e}")
            self._send_text("fail", 500)
            return

        reason = result.get("reason", "")
        order_id = result.get("order_id", "")

        if not result.get("ok"):
            # already_settled 是幂等重推，属正常情况，回 success 让平台停止重试
            if reason == "already_settled":
                print(f"ℹ️  虎皮椒回调重复推送（已结算）: {order_id}")
                self._send_text("success", 200)
                return
            # 其余均为异常/疑似攻击，记录并回 fail（平台会重试，便于观察）
            print(f"⚠️  虎皮椒回调校验失败 [{reason}] order={order_id}")
            self._send_text("fail", 400)
            return

        # 验签通过 → 尝试履约（认证类订单自动签发徽章；其它类型跳过）
        try:
            from eco.monetization import settle_cny_order
            settle = settle_cny_order(order_id, result.get("params"))
            if settle.get("success"):
                cert = (settle.get("certification") or {}).get("cert_id", "")
                print(f"✅ 虎皮椒支付成功并签发认证: order={order_id} cert={cert}")
            else:
                print(f"✅ 虎皮椒支付成功（非认证订单）: order={order_id}")
        except Exception as e:
            # 履约失败不能让平台无限重推——支付本身已确认并落账，履约可后台补偿
            print(f"❌ 虎皮椒履约异常（支付已落账，需人工补偿）: order={order_id} err={e}")

        self._send_text("success", 200)
        _record_usage("hupijiao-notify", self.client_address[0])

    def _send_text(self, text, status=200):
        """发送纯文本响应（支付回调等要求非 JSON 的场景）。"""
        try:
            body = text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionAbortedError, BrokenPipeError, OSError):
            pass

    def _handle_creem_webhook(self):
        """处理 Creem Webhook 事件（checkout.completed 等）"""
        raw_body = self._read_raw_body()
        if raw_body is None:
            self._send_json({"error": "Request body too large (max 200KB)"}, 413)
            return

        signature_header = self.headers.get("creem-signature", "")
        webhook_secret = os.environ.get("CREEM_WEBHOOK_SECRET", "")
        if not webhook_secret:
            print("❌ Creem webhook 未配置: 缺少 CREEM_WEBHOOK_SECRET")
            self._send_json({"error": "Webhook secret not configured"}, 500)
            return

        from eco.payment import CreemGateway
        if not CreemGateway.verify_webhook_signature(raw_body, signature_header, webhook_secret):
            print(f"⚠️  Creem webhook 签名验证失败: signature={signature_header[:16]}...")
            self._send_json({"error": "Invalid signature"}, 401)
            return

        try:
            event = json.loads(raw_body.decode("utf-8", errors="replace"))
        except Exception as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, 400)
            return

        event_type = event.get("eventType", "")
        print(f"🔔 Creem webhook 事件: {event_type}")

        if event_type == "checkout.completed":
            self._handle_checkout_completed(event)
        else:
            print(f"ℹ️  事件类型 {event_type} 暂不处理，直接确认")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"received": True}).encode("utf-8"))
        _record_usage("webhook-creem", self.client_address[0])

    def _handle_checkout_completed(self, event):
        """处理 checkout.completed 事件，增加积分（含幂等性检查）"""
        try:
            checkout_data = event.get("object", {})
            metadata = checkout_data.get("metadata", {})
            account_id = metadata.get("account_id")
            product_key = metadata.get("product_key")
            credits = metadata.get("credits")
            checkout_id = checkout_data.get("id", "")

            if not account_id or not credits:
                print(f"⚠️  webhook metadata 缺少必要字段: account_id={account_id}, credits={credits}")
                return

            # ── 幂等性检查：防止重复处理同一个 checkout ──
            processed = _load_json(WEBHOOK_PROCESSED_FILE, {"checkouts": []})
            processed_checkouts = processed.get("checkouts", [])
            if checkout_id and checkout_id in processed_checkouts:
                print(f"⚠️  重复 webhook 已忽略: checkout_id={checkout_id}（已处理过）")
                return

            # ── 充值积分 ──
            from eco.account import UserAccount
            mgr = UserAccount()
            mgr.recharge(account_id, credits, "creem")

            # ── 记录已处理 checkout_id（幂等性）──
            processed_checkouts.append(checkout_id)
            # 只保留最近 1000 条
            if len(processed_checkouts) > 1000:
                processed_checkouts = processed_checkouts[-500:]
            processed["checkouts"] = processed_checkouts
            _save_json(WEBHOOK_PROCESSED_FILE, processed)

            # ── 记录积分变动流水 ──
            txns = _load_json(CREDIT_TXN_FILE, {"transactions": []})
            txn_list = txns.get("transactions", [])
            txn_list.append({
                "txn_id": f"txn_{uuid.uuid4().hex[:12]}",
                "type": "recharge",
                "account_id": account_id,
                "credits": credits,
                "gateway": "creem",
                "checkout_id": checkout_id,
                "product_key": product_key,
                "timestamp": datetime.now(TZ).isoformat(),
            })
            if len(txn_list) > 10000:
                txn_list = txn_list[-5000:]
            txns["transactions"] = txn_list
            _save_json(CREDIT_TXN_FILE, txns)

            print(f"✅ Creem 支付成功: account_id={account_id}, product_key={product_key}, credits={credits}, checkout_id={checkout_id}")
        except Exception as e:
            print(f"❌ 处理 checkout.completed 失败: {e}")

    def _handle_mcp(self, data):
        """MCP StreamableHTTP endpoint — JSON-RPC 2.0"""
        method = data.get("method", "")
        params = data.get("params", {})
        req_id = data.get("id", 1)
        
        # MCP通知 — 服务端忽略
        if method.startswith("notifications/"):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return
        
        # MCP initialize
        if method == "initialize":
            self._send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "AIShield Security Scanner",
                        "version": "4.2.2",
                    },
                },
            })
            return
        
        # MCP tools/list
        if method == "tools/list":
            self._send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "aishield_scan",
                            "description": "OWASP MCP Top 10 aligned security scan — 227 rules, 5-dimension scoring",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "source_url": {"type": "string", "description": "GitHub repo URL"},
                                    "tool_type": {"type": "string", "enum": ["mcp", "skill", "gpt", "prompt"], "default": "mcp"},
                                    "name": {"type": "string", "description": "Tool name"},
                                },
                                "required": ["source_url"],
                            },
                        },
                        {
                            "name": "aishield_guardrail",
                            "description": "Pre-install safety check — pass/block verdict",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "source_url": {"type": "string", "description": "GitHub repo URL"},
                                    "auto_block": {"type": "boolean", "default": True},
                                },
                                "required": ["source_url"],
                            },
                        },
                        {
                            "name": "aishield_prompt_check",
                            "description": "Prompt injection detection — Chinese + English",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {"type": "string", "description": "Prompt text to check (min 10 chars)"},
                                },
                                "required": ["prompt"],
                            },
                        },
                        {
                            "name": "aishield_banned_words",
                            "description": "Chinese banned words detection — 6 platform rules",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string", "description": "Text to check"},
                                    "platform": {"type": "string", "enum": ["douyin", "xiaohongshu", "wechat", "weibo", "bilibili", "kuaishou", "all"], "default": "all"},
                                },
                                "required": ["text"],
                            },
                        },
                        {
                            "name": "aishield_rug_pull",
                            "description": "Rug pull detection — check if a tool has removed security code or added suspicious changes in recent commits",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "source_url": {"type": "string", "description": "GitHub repo URL"},
                                },
                                "required": ["source_url"],
                            },
                        },
                        {
                            "name": "aishield_handshake",
                            "description": "MCP handshake verification — analyze MCP config, detect npx auto-install, sensitive env vars, oversized tool descriptions, and attempt HTTP handshake",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "source_url": {"type": "string", "description": "GitHub repo URL"},
                                },
                                "required": ["source_url"],
                            },
                        },
                        {
                            "name": "aishield_vertical_risk",
                            "description": "Vertical-industry risk scan — detect high-risk claims for finance/medical/gov sectors (unlicensed diagnosis, illegal medical device, financial over-promise, etc.)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string", "description": "Text content to scan"},
                                    "domain": {"type": "string", "enum": ["finance", "medical", "government"], "default": "finance", "description": "Vertical domain"},
                                },
                                "required": ["text"],
                            },
                        },
                        {
                            "name": "agent_register",
                            "description": "Agent-First one-click onboarding — register as an Agent, get DID + API Key + quick start guide in a single call",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "agent_name": {"type": "string", "description": "Agent name (required)"},
                                    "capabilities": {"type": "array", "items": {"type": "string"}, "description": "Capability list, e.g. [\"scan\", \"monitor\"]"},
                                    "owner": {"type": "string", "description": "Owner identifier"},
                                },
                                "required": ["agent_name"],
                            },
                        },
                        {
                            "name": "agent_quick_scan",
                            "description": "Agent-First quick scan — scan a tool by name and description, no source URL required",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "tool_name": {"type": "string", "description": "Tool name (required)"},
                                    "tool_description": {"type": "string", "description": "Tool description (required)"},
                                    "source_url": {"type": "string", "description": "Optional GitHub repo URL for deep scan"},
                                },
                                "required": ["tool_name", "tool_description"],
                            },
                        },
                    ],
                },
            })
            return
        
        # MCP tools/call
        if method == "tools/call":
            tool_name = params.get("name", "")
            args = params.get("arguments", {})
            
            try:
                # 旧工具名 → 新工具名 alias（兼容老客户端）
                _TOOL_ALIAS = {
                    "security_scan": "aishield_scan",
                    "prompt_injection_check": "aishield_prompt_check",
                    "banned_words_check": "aishield_banned_words",
                    "rug_pull_detect": "aishield_rug_pull",
                    "dependency_monitor": "aishield_scan",
                }
                tool_name = _TOOL_ALIAS.get(tool_name, tool_name)

                if tool_name == "aishield_scan":
                    result_data = scan(args["source_url"], args.get("tool_type", "mcp"), args.get("name", ""))
                    text = json.dumps(result_data, ensure_ascii=False, indent=2)
                elif tool_name == "aishield_guardrail":
                    result_data = scan(args["source_url"], "mcp", "")
                    score = result_data.get("overall_score", 0)
                    auto_block = args.get("auto_block", True)
                    if score >= 70:
                        verdict = "PASS"
                    elif score >= 55 and not auto_block:
                        verdict = "WARN"
                    else:
                        verdict = "BLOCK"
                    text = f"AIShield Guardrail: {verdict}\nScore: {score}/100\nBadge: {result_data.get('badge_level', 'none')}\n\n{json.dumps(result_data, ensure_ascii=False, indent=2)}"
                elif tool_name == "aishield_prompt_check":
                    result_data = check_prompt_injection(args["prompt"])
                    text = json.dumps(result_data, ensure_ascii=False, indent=2)
                elif tool_name == "aishield_banned_words":
                    result_data = check_banned_words(args["text"], args.get("platform", "all"))
                    text = json.dumps(result_data, ensure_ascii=False, indent=2)
                elif tool_name == "aishield_rug_pull":
                    result_data = detect_rug_pull(args["source_url"])
                    text = json.dumps(result_data, ensure_ascii=False, indent=2)
                elif tool_name == "aishield_handshake":
                    result_data = verify_handshake(args["source_url"])
                    text = json.dumps(result_data, ensure_ascii=False, indent=2)
                elif tool_name == "aishield_vertical_risk":
                    result_data = scan_vertical_risk(args["text"], args.get("domain", "finance"))
                    text = json.dumps(result_data, ensure_ascii=False, indent=2)
                elif tool_name == "agent_register":
                    from eco.agent_gateway import agent_setup
                    result_data = agent_setup(args)
                    text = json.dumps(result_data, ensure_ascii=False, indent=2)
                elif tool_name == "agent_quick_scan":
                    from eco.agent_gateway import agent_quick_scan
                    result_data = agent_quick_scan(args)
                    text = json.dumps(result_data, ensure_ascii=False, indent=2)
                else:
                    self._send_json({
                        "jsonrpc": "2.0", "id": req_id,
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                    })
                    return
                
                self._send_json({
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {"content": [{"type": "text", "text": text}]},
                })
                _record_usage(f"mcp:{tool_name}", self.client_address[0])
            except Exception as e:
                self._send_json({
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32000, "message": str(e)},
                })
            return
        
        self._send_json({
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32601, "message": f"Unknown method: {method}"},
        })


def main():
    port = int(os.environ.get("AISHIELD_PORT", os.environ.get("PORT", 8450)))
    
    # 注册生态路由
    if _eco_available:
        try:
            from eco import identity, payment, badge, marketplace, a2a_gateway
            from eco import collab, sandbox, skill_market, auth_provider, account
            from eco import agent_gateway
            from eco import observability
            from eco import blackboard, agent_security_gateway
            from eco import trust_protocol, replay
            from scanner import vertical_risk
            _eco_init({
                "identity": identity,
                "payment": payment,
                "badge": badge,
                "marketplace": marketplace,
                "a2a_gateway": a2a_gateway,
                "collab": collab,
                "sandbox": sandbox,
                "skill_market": skill_market,
                "auth_provider": auth_provider,
                "account": account,
                "agent_gateway": agent_gateway,
                "observability": observability,
                "blackboard": blackboard,
                "agent_security_gateway": agent_security_gateway,
                "trust_protocol": trust_protocol,
                "replay": replay,
                "vertical_risk": vertical_risk,
            })
            print("  Eco modules: identity, payment, badge, marketplace, a2a, collab, sandbox, skill_market, auth_provider, account, agent_gateway, observability, blackboard, agent_security_gateway, trust_protocol, replay, vertical_risk")
        except Exception as e:
            print(f"  Eco modules: init failed ({e})")
    else:
        print("  Eco modules: not loaded (dispatcher unavailable)")
    
    class ThreadedServer(ThreadingMixIn, HTTPServer):
        daemon_threads = True

    server = ThreadedServer(("0.0.0.0", port), AIShieldHandler)
    print(f"AIShield API v4.2 — Agent-First + OWASP MCP Top 10")
    print(f"  Port: {port}")
    print(f"  Rules: {get_rule_count('mcp')}")
    print(f"  Standard: OWASP MCP Top 10 (2025 v0.1)")
    print(f"  MCP endpoint: /api/v1/mcp")
    print(f"  Agent setup: /api/v1/agent/setup")
    print(f"  OpenAPI spec: /openapi.json")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()