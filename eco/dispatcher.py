"""
Eco路由分发器 — 直接内联路由处理，不依赖eco模块的函数签名
"""
from urllib.parse import urlparse, parse_qs

_modules = {}

def init(modules_dict):
    global _modules
    _modules = modules_dict


def dispatch_get(handler):
    """分发GET请求。返回True如果处理了。"""
    parsed = urlparse(handler.path)
    path = parsed.path
    qs = parse_qs(parsed.query)

    # Identity: 列出agents
    if path == "/api/v1/identity/agents":
        mod = _modules.get("identity")
        if mod:
            reg = mod.AgentRegistration()
            agents = reg.list_agents()
            handler._send_json({"success": True, "total": len(agents), "agents": agents})
            return True

    # Identity: 查询agent详情
    if path.startswith("/api/v1/identity/agents/"):
        mod = _modules.get("identity")
        if mod:
            did = path[len("/api/v1/identity/agents/"):]
            reg = mod.AgentRegistration()
            agent = reg.get_agent(did)
            if agent:
                handler._send_json({"success": True, "agent": agent})
            else:
                handler._send_json({"error": "Agent not found", "did": did}, 404)
            return True

    # Payment: 套餐列表
    if path == "/api/v1/billing/plans":
        mod = _modules.get("payment")
        if mod:
            handler._send_json({"success": True, "plans": mod.PLANS})
            return True

    # Badge: SVG徽章
    if path.startswith("/api/v1/badge/"):
        mod = _modules.get("badge")
        if mod:
            tool_name = path[len("/api/v1/badge/"):]
            score = int(qs.get("score", [0])[0])
            level = qs.get("level", ["none"])[0]
            svc = mod.BadgeService()
            svg = svc.generate_badge_svg(tool_name, score, level)
            handler.send_response(200)
            handler.send_header("Content-Type", "image/svg+xml")
            handler.send_header("Content-Length", str(len(svg.encode())))
            handler.end_headers()
            handler.wfile.write(svg.encode())
            return True

    # Badge: 查询认证详情
    if path.startswith("/api/v1/certify/"):
        mod = _modules.get("badge")
        if mod:
            cert_id = path[len("/api/v1/certify/"):]
            svc = mod.CertificationService()
            cert = svc.get_certification(cert_id)
            if cert:
                handler._send_json({"success": True, "certification": cert})
            else:
                handler._send_json({"error": "Certification not found", "cert_id": cert_id}, 404)
            return True

    # Marketplace: 工具列表
    if path == "/api/v1/market/tools":
        mod = _modules.get("marketplace")
        if mod:
            mp = mod.ToolMarketplace()
            page = int(qs.get("page", [1])[0])
            category = qs.get("category", [None])[0]
            tools = mp.list_tools(category=category, page=page)
            handler._send_json({"success": True, "tools": tools})
            return True

    # Marketplace: 查询工具详情
    if path.startswith("/api/v1/market/tools/"):
        mod = _modules.get("marketplace")
        if mod:
            tool_id = path[len("/api/v1/market/tools/"):]
            mp = mod.ToolMarketplace()
            tool = mp.get_tool(tool_id)
            if tool:
                handler._send_json({"success": True, "tool": tool})
            else:
                handler._send_json({"error": "Tool not found", "tool_id": tool_id}, 404)
            return True

    # A2A: 发现agents（支持 skill / name / min_reputation 多参数）
    if path == "/api/v1/a2a/discover":
        mod = _modules.get("a2a_gateway")
        if mod:
            disc = mod.AgentDiscovery()
            skill = qs.get("skill", [None])[0]
            name = qs.get("name", [None])[0]
            min_reputation = int(qs.get("min_reputation", [0])[0])
            agents = disc.discover(skill=skill, name=name, min_reputation=min_reputation)
            handler._send_json({"success": True, "agents": agents})
            return True

    return False


def dispatch_post(handler, data):
    """分发POST请求。返回True如果处理了。"""
    parsed = urlparse(handler.path)
    path = parsed.path

    # Identity: 注册agent
    if path == "/api/v1/identity/register":
        mod = _modules.get("identity")
        if mod:
            name = data.get("name", "").strip()
            if not name:
                handler._send_json({"error": "name is required"}, 400)
                return True
            reg = mod.AgentRegistration()
            result = reg.register(
                name=name,
                owner=data.get("owner", ""),
                capabilities=data.get("capabilities", []),
            )
            handler._send_json({"success": True, **result})
            return True

    # Identity: 更新信誉分
    if path.startswith("/api/v1/identity/reputation/"):
        mod = _modules.get("identity")
        if mod:
            did = path[len("/api/v1/identity/reputation/"):]
            event_type = data.get("event_type")
            try:
                rep = mod.ReputationSystem()
                result = rep.update_score(did, event_type)
                handler._send_json({"success": True, **result})
            except ValueError as e:
                handler._send_json({"error": str(e)}, 400)
            return True

    # Payment: 记录用量
    if path == "/api/v1/billing/usage":
        mod = _modules.get("payment")
        if mod:
            bs = mod.BillingService()
            result = bs.record_usage(
                account_id=data.get("user_id", "anonymous"),
                endpoint=data.get("endpoint", "unknown"),
            )
            handler._send_json({"success": True, **result})
            return True

    # Badge: 认证工具
    if path == "/api/v1/certify":
        mod = _modules.get("badge")
        if mod:
            svc = mod.CertificationService()
            result = svc.certify_tool(
                source_url=data.get("source_url", ""),
                scan_report=data.get("scan_report", {}),
            )
            handler._send_json({"success": True, **result})
            return True

    # Marketplace: Webhook
    if path == "/api/v1/market/webhook":
        mod = _modules.get("marketplace")
        if mod:
            mp = mod.ToolMarketplace()
            result = mp.process_webhook(data)
            handler._send_json({"success": True, **result})
            return True

    # A2A: 注册AgentCard
    if path == "/api/v1/a2a/agent-card":
        mod = _modules.get("a2a_gateway")
        if mod:
            svc = mod.AgentCard()
            result = svc.register(data)
            handler._send_json({"success": True, **result})
            return True

    # A2A: 创建任务
    if path == "/api/v1/a2a/task":
        mod = _modules.get("a2a_gateway")
        if mod:
            router = mod.TaskRouter()
            task = data.get("task", {})
            result = router.create_task(
                task_description=task.get("description", task.get("input", "")),
                task_type=task.get("type", "general"),
                required_skills=task.get("skills"),
                payload=task.get("payload"),
            )
            handler._send_json({"success": True, **result})
            return True

    return False
