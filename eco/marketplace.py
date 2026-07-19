"""
eco/marketplace.py — 工具市场API

功能:
  - ToolMarketplace:
      list_tools(category, sort, page):  列出已认证工具
      get_tool(tool_id):                工具详情（含安全报告摘要）
      search_tools(query):              搜索工具
      register_tool(tool_info):         注册工具
      update_tool(tool_id, updates):    更新工具信息
      Webhook通知: 工具被扫描/认证/降级时通知
  - 数据持久化: data/marketplace.json（从已有的batch_scans.json合并）

API路由:
  GET  /api/v1/market/tools                  — 列出工具
  GET  /api/v1/market/tools/{tool_id}        — 工具详情
  POST /api/v1/market/webhook                — Webhook通知
"""

import json
import os
import uuid
import threading
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs

# ── 路径配置 ──
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")
MARKETPLACE_FILE = os.path.join(_DATA_DIR, "marketplace.json")
BATCH_SCANS_FILE = os.path.join(_BASE_DIR, "data", "batch_scans.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()

# ── Webhook事件类型 ──
WEBHOOK_EVENTS = {
    "tool.scanned":    "工具完成安全扫描",
    "tool.certified":  "工具通过安全认证",
    "tool.downgraded": "工具安全等级降级",
    "tool.updated":    "工具信息更新",
}


# ══════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════

def _load_json(path, default=None):
    """加载JSON文件"""
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    """线程安全保存JSON文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _now_iso():
    """返回当前时间ISO格式"""
    return datetime.now(TZ).isoformat()


def _generate_tool_id():
    """生成工具ID"""
    return f"tool-{uuid.uuid4().hex[:12]}"


# ══════════════════════════════════════════════
#  工具市场
# ══════════════════════════════════════════════

class ToolMarketplace:
    """
    工具市场管理器
    管理已认证工具的注册、搜索和Webhook通知
    """

    def __init__(self):
        self._tools = {}
        self._webhooks = {}  # webhook_url -> config

    def _load(self):
        """从磁盘加载数据"""
        data = _load_json(MARKETPLACE_FILE, {
            "tools": {},
            "webhooks": {},
        })
        self._tools = data.get("tools", {})
        self._webhooks = data.get("webhooks", {})

    def _save(self):
        """持久化到磁盘"""
        _save_json(MARKETPLACE_FILE, {
            "tools": self._tools,
            "webhooks": self._webhooks,
        })

    def _merge_batch_scans(self):
        """
        从已有的batch_scans.json合并工具数据
        将历史扫描结果导入到市场数据中
        """
        batch_data = _load_json(BATCH_SCANS_FILE, {})
        # batch_scans.json可能有多种格式，兼容处理
        scans = []
        if isinstance(batch_data, list):
            scans = batch_data
        elif isinstance(batch_data, dict):
            # 尝试获取scans列表
            scans = batch_data.get("scans", batch_data.get("results", []))

        merged_count = 0
        for scan in scans:
            source_url = scan.get("source_url", "")
            name = scan.get("name", scan.get("tool_name", ""))
            if not name and source_url:
                # 从URL提取名称
                parts = source_url.rstrip("/").split("/")
                name = parts[-1] if parts else "unknown"

            tool_id = _generate_tool_id()
            if source_url and source_url not in [t.get("source_url") for t in self._tools.values()]:
                self._tools[tool_id] = {
                    "tool_id": tool_id,
                    "name": name,
                    "source_url": source_url,
                    "category": scan.get("tool_type", "mcp"),
                    "overall_score": scan.get("overall_score", 0),
                    "badge_level": scan.get("badge_level", "none"),
                    "risk_level": scan.get("risk_level", "unknown"),
                    "findings_count": scan.get("total_findings", 0),
                    "certified": scan.get("overall_score", 0) >= 70,
                    "description": scan.get("description", ""),
                    "registered_at": scan.get("scanned_at", _now_iso()),
                    "updated_at": _now_iso(),
                    "status": "active",
                }
                merged_count += 1

        if merged_count > 0:
            self._save()
        return merged_count

    def register_tool(self, tool_info):
        """
        注册新工具到市场

        Args:
            tool_info (dict): 工具信息 {
                name, source_url, category, description,
                author, version, capabilities
            }

        Returns:
            dict: 注册的工具信息
        """
        self._load()

        tool_id = _generate_tool_id()

        entry = {
            "tool_id": tool_id,
            "name": tool_info.get("name", ""),
            "source_url": tool_info.get("source_url", ""),
            "category": tool_info.get("category", "mcp"),
            "description": tool_info.get("description", ""),
            "author": tool_info.get("author", ""),
            "version": tool_info.get("version", "1.0.0"),
            "capabilities": tool_info.get("capabilities", []),
            "overall_score": 0,
            "badge_level": "none",
            "risk_level": "unknown",
            "findings_count": 0,
            "certified": False,
            "registered_at": _now_iso(),
            "updated_at": _now_iso(),
            "status": "pending_scan",
        }

        self._tools[tool_id] = entry
        self._save()

        # 触发Webhook通知
        self._trigger_webhook("tool.updated", {
            "tool_id": tool_id,
            "name": entry["name"],
            "action": "registered",
        })

        return entry

    def get_tool(self, tool_id):
        """
        获取工具详情

        Args:
            tool_id (str): 工具ID

        Returns:
            dict | None: 工具信息
        """
        self._load()
        return self._tools.get(tool_id)

    def update_tool(self, tool_id, updates):
        """
        更新工具信息

        Args:
            tool_id (str):  工具ID
            updates (dict): 更新字段

        Returns:
            dict | None: 更新后的工具信息
        """
        self._load()
        tool = self._tools.get(tool_id)
        if not tool:
            return None

        for key, value in updates.items():
            if key in tool and key not in ("tool_id", "registered_at"):
                tool[key] = value

        # 如果分数更新了，重新计算认证状态
        if "overall_score" in updates:
            tool["certified"] = tool["overall_score"] >= 70

        tool["updated_at"] = _now_iso()
        self._tools[tool_id] = tool
        self._save()

        return tool

    def list_tools(self, category=None, sort="score", page=1, page_size=20):
        """
        列出工具

        Args:
            category (str):   分类过滤 (mcp/skill/gpt/prompt)
            sort (str):       排序方式 (score/name/updated)
            page (int):       页码
            page_size (int):  每页数量

        Returns:
            dict: 工具列表结果
        """
        self._load()
        tools = list(self._tools.values())

        # 分类过滤
        if category:
            tools = [t for t in tools if t.get("category") == category]

        # 排序
        if sort == "score":
            tools.sort(key=lambda t: t.get("overall_score", 0), reverse=True)
        elif sort == "name":
            tools.sort(key=lambda t: t.get("name", ""))
        elif sort == "updated":
            tools.sort(key=lambda t: t.get("updated_at", ""), reverse=True)

        # 分页
        total = len(tools)
        start = (page - 1) * page_size
        end = start + page_size
        page_tools = tools[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "tools": page_tools,
        }

    def search_tools(self, query, page=1, page_size=20):
        """
        搜索工具

        Args:
            query (str):  搜索关键词
            page (int):   页码
            page_size (int): 每页数量

        Returns:
            dict: 搜索结果
        """
        self._load()
        query_lower = query.lower()
        tools = list(self._tools.values())

        # 模糊搜索（名称、描述、分类、作者）
        matched = []
        for t in tools:
            fields = [
                t.get("name", ""),
                t.get("description", ""),
                t.get("category", ""),
                t.get("author", ""),
                t.get("source_url", ""),
            ]
            if any(query_lower in field.lower() for field in fields):
                matched.append(t)

        total = len(matched)
        start = (page - 1) * page_size
        end = start + page_size
        results = matched[start:end]

        return {
            "query": query,
            "total": total,
            "page": page,
            "page_size": page_size,
            "tools": results,
        }

    def register_webhook(self, url, events=None, secret=""):
        """
        注册Webhook

        Args:
            url (str):       Webhook URL
            events (list):   订阅的事件类型
            secret (str):    签名密钥

        Returns:
            dict: Webhook信息
        """
        self._load()
        webhook_id = f"wh-{uuid.uuid4().hex[:8]}"

        self._webhooks[url] = {
            "webhook_id": webhook_id,
            "url": url,
            "events": events or list(WEBHOOK_EVENTS.keys()),
            "secret": secret,
            "created_at": _now_iso(),
        }
        self._save()

        return self._webhooks[url]

    def _trigger_webhook(self, event, payload):
        """
        触发Webhook通知

        Args:
            event (str):    事件类型
            payload (dict): 事件数据

        注意: 标准库不支持异步HTTP请求，
              此方法仅记录待发送的通知。
              生产环境建议使用 urllib.request 发送。
        """
        self._load()
        notifications = []

        for url, config in self._webhooks.items():
            # 检查是否订阅了此事件
            if event not in config.get("events", []):
                continue

            notification = {
                "url": url,
                "event": event,
                "payload": payload,
                "timestamp": _now_iso(),
                "status": "pending",
            }
            notifications.append(notification)

            # TODO: 生产环境使用 urllib.request 异步发送
            # import urllib.request
            # try:
            #     req_data = json.dumps({
            #         "event": event,
            #         "payload": payload,
            #         "timestamp": _now_iso(),
            #     })
            #     req = urllib.request.Request(
            #         url,
            #         data=req_data.encode("utf-8"),
            #         headers={"Content-Type": "application/json"},
            #     )
            #     urllib.request.urlopen(req, timeout=10)
            #     notification["status"] = "sent"
            # except Exception as e:
            #     notification["status"] = "failed"
            #     notification["error"] = str(e)

        return notifications


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将工具市场模块路由注册到HTTPServer的Handler上

    兼容 api/server.py 的 AIShieldHandler 模式。

    Args:
        handler: AIShieldHandler实例
    """
    original_do_get = handler.do_GET
    original_do_post = handler.do_POST

    def do_get_patched(self):
        """扩展GET路由"""
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path

        # ── GET /api/v1/market/tools — 列出工具 ──
        if path == "/api/v1/market/tools":
            query = parse_qs(parsed.query)
            category = query.get("category", [None])[0]
            sort = query.get("sort", ["score"])[0]
            try:
                page = int(query.get("page", [1])[0])
            except (ValueError, IndexError):
                page = 1
            try:
                page_size = int(query.get("page_size", [20])[0])
            except (ValueError, IndexError):
                page_size = 20

            try:
                market = ToolMarketplace()
                result = market.list_tools(
                    category=category,
                    sort=sort,
                    page=page,
                    page_size=page_size,
                )
                self._send_json({"success": True, "market": result})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── GET /api/v1/market/tools/{tool_id} — 工具详情 ──
        if path.startswith("/api/v1/market/tools/"):
            tool_id = path[len("/api/v1/market/tools/"):]
            market = ToolMarketplace()
            tool = market.get_tool(tool_id)
            if tool:
                self._send_json({"success": True, "tool": tool})
            else:
                self._send_json({"error": "工具不存在", "tool_id": tool_id}, 404)
            return

        # 非本模块路由
        original_do_get(self)

    def do_post_patched(self):
        """扩展POST路由"""
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_body()
            data = json.loads(body) if body else {}
        except (json.JSONDecodeError, TypeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        # ── POST /api/v1/market/webhook — Webhook通知 ──
        if path == "/api/v1/market/webhook":
            url = data.get("url", "")
            events = data.get("events")
            secret = data.get("secret", "")

            if not url:
                self._send_json({"error": "url is required"}, 400)
                return

            try:
                market = ToolMarketplace()
                webhook = market.register_webhook(url, events, secret)
                self._send_json({"success": True, "webhook": webhook}, 201)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 非本模块路由
        original_do_post(self)

    handler.do_GET = do_get_patched.__get__(handler, type(handler))
    handler.do_POST = do_post_patched.__get__(handler, type(handler))


# ══════════════════════════════════════════════
#  独立测试入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("=== 工具市场测试 ===")
    market = ToolMarketplace()

    # 尝试合并历史扫描数据
    print("\n--- 合并batch_scans ---")
    merged = market._merge_batch_scans()
    print(f"  合并了 {merged} 个工具")

    # 注册新工具
    print("\n--- 注册工具 ---")
    tool = market.register_tool({
        "name": "ExampleMCP",
        "source_url": "https://github.com/example/mcp-tool",
        "category": "mcp",
        "description": "示例MCP工具",
        "author": "test_author",
        "version": "1.0.0",
        "capabilities": ["file_read", "web_search"],
    })
    print(f"  注册成功: {tool['tool_id']}")

    # 更新工具（模拟扫描结果）
    print("\n--- 更新扫描结果 ---")
    updated = market.update_tool(tool["tool_id"], {
        "overall_score": 88,
        "badge_level": "gold",
        "risk_level": "low",
        "findings_count": 2,
    })
    print(f"  更新后: score={updated['overall_score']}, certified={updated['certified']}")

    # 列出工具
    print("\n--- 列出工具 ---")
    result = market.list_tools(sort="score", page=1, page_size=10)
    print(f"  总计: {result['total']}个工具")
    for t in result["tools"][:5]:
        print(f"    [{t.get('badge_level', '?')}] {t['name']} — {t.get('overall_score', '?')}分")

    # 搜索工具
    print("\n--- 搜索工具 ---")
    search = market.search_tools("example")
    print(f"  搜索 'example': 找到 {search['total']} 个")
    for t in search["tools"]:
        print(f"    {t['name']}")

    # 注册Webhook
    print("\n--- 注册Webhook ---")
    webhook = market.register_webhook(
        url="https://example.com/webhook",
        events=["tool.certified", "tool.scanned"],
        secret="test_secret",
    )
    print(f"  Webhook: {webhook['webhook_id']}")

    print("\n=== 全部测试通过 ===")
