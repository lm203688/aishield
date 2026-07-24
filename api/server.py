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
                    "serverInfo": {"name": "AIShield", "version": "4.2.0",
                        "description": "AI Agent Security Shield — OWASP MCP Top 10 aligned security scanning. 133 rules covering prompt injection, zero-width characters, Rug Pull, permission audit, and dependency monitoring."},
                    "url": "https://aishield.tools/mcp",
                    "provider": {"name": "AIShield", "url": "https://github.com/lm203688/aishield"},
                    "license": "MIT",
                    "tools": [
                        {"name": "security_scan", "description": "Full security audit for MCP tools/agents with OWASP MCP Top 10 alignment.",
                            "inputSchema": {"type": "object", "properties": {"tool_name": {"type": "string"}}, "required": ["tool_name"]}},
                        {"name": "prompt_injection_check", "description": "Detect prompt injection attacks in Chinese and English. 200+ pattern matching.",
                            "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}},
                        {"name": "banned_words_check", "description": "Detect banned/sensitive words for 6 Chinese platforms.",
                            "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
                        {"name": "rug_pull_detect", "description": "Detect Rug Pull risk in MCP tool repositories.",
                            "inputSchema": {"type": "object", "properties": {"source_url": {"type": "string"}}, "required": ["source_url"]}},
                        {"name": "agent_register", "description": "One-click agent onboarding with API key and DID identity.",
                            "inputSchema": {"type": "object", "properties": {"agent_name": {"type": "string"}}, "required": ["agent_name"]}},
                        {"name": "dependency_monitor", "description": "Monitor MCP tool dependencies for version changes.",
                            "inputSchema": {"type": "object", "properties": {"source_url": {"type": "string"}}, "required": ["source_url"]}}
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
                ],
                "docs": "https://aishield.tools/docs",
                "mcp_install": "npx @aishield/mcp-server",
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

        # Eco模块路由
        if _eco_dispatch_get(self):
            return

        self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            body = self._read_body()
            if body is None:
                self._send_json({"error": "Request body too large (max 100KB)"}, 413)
                return
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
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
                    amount = float(data.get("amount", 0))
                    gateway = data.get("gateway", "alipay")
                    if not account_id or amount <= 0:
                        self._send_json({"error": "account_id 和 amount 为必填，且 amount > 0"}, 400)
                        return
                    mgr = _account_mod.UserAccount()
                    result = mgr.recharge(account_id, amount, gateway)
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
    
    def _handle_audit(self, data):
        source_url = data.get("source_url", "")
        tool_type = data.get("tool_type", "mcp")
        name = data.get("name", "")
        
        if not source_url:
            self._send_json({"error": "source_url is required"}, 400)
            return
        
        # ── Free→Pro 转化层：检查今日调用次数 ──
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        usage = _load_json(USAGE_FILE, {"daily": {}, "total": 0})
        today_usage = usage.get("daily", {}).get(today, {})
        today_audit_count = today_usage.get("by_endpoint", {}).get("audit", 0)
        
        # Free层每日50次限制（对应billing模块PLANS定义）
        FREE_DAILY_LIMIT = 50
        is_limited = today_audit_count >= FREE_DAILY_LIMIT
        
        try:
            result = scan(source_url, tool_type, name)
            
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
            # 只保留最近1000条
            if len(audits) > 1000:
                audits = audits[-500:]
            _save_json(AUDIT_FILE, audits)
            
            # P0-3.1: Badge <-> Scan 联动
            # 扫描评分 >= 80 时，自动调用 CertificationService.certify_tool() 生成认证
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
                # 认证失败不影响扫描结果返回
                pass
            
            # 品牌水印 + 转化提示
            response = {
                "success": True,
                "report": result,
                "powered_by": {
                    "name": "AIShield",
                    "url": "https://aishield.tools",
                    "version": "4.1",
                },
            }
            
            # 附加自动认证结果（Badge <-> Scan 联动）
            if certification:
                response["certification"] = certification
            
            # 超限时添加升级提示（完整结果仍返回，但附带转化引导）
            if is_limited:
                response["upgrade_hint"] = "升级Pro获取无限扫描+CI/CD集成 | npx @aishield/mcp-server"
            
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
                        "version": "4.2.0",
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
                            "description": "OWASP MCP Top 10 aligned security scan — 133 rules, 5-dimension scoring",
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
            })
            print("  Eco modules: identity, payment, badge, marketplace, a2a, collab, sandbox, skill_market, auth_provider, account, agent_gateway")
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