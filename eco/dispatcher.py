"""
Eco路由分发器 — 直接内联路由处理，不依赖eco模块的函数签名
"""
from urllib.parse import urlparse, parse_qs

_modules = {}

def init(modules_dict):
    global _modules
    _modules = modules_dict


# ══════════════════════════════════════════════
#  P0-4: Auth 认证中间件
# ══════════════════════════════════════════════

# 认证豁免路径（生成key的端点和健康检查不需要认证）
_AUTH_EXEMPT_PATHS = {
    "/api/v1/auth/keys",   # 生成 API Key 的端点
    "/api/v1/health",      # 健康检查
}


def _require_auth(handler):
    """
    认证中间件：验证请求的 Authorization header 中的 API Key。

    - 读取 Authorization: Bearer <api_key> header
    - 调用 auth_provider.APIKeyManager().verify_key() 验证
    - 验证失败返回 401（已通过 handler._send_json 发送响应）
    - 验证成功把 agent_id 挂到 handler._auth_agent_id
    - 对 /api/v1/auth/keys（生成 key 的端点）和 /api/v1/health 豁免认证
    - 对其他 /api/v1/* 端点默认启用认证

    Args:
        handler: AIShieldHandler 实例

    Returns:
        bool: True 表示认证通过（或豁免），False 表示认证失败（已发送401响应）
    """
    parsed = urlparse(handler.path)
    path = parsed.path

    # 非 /api/v1/ 路径不启用认证
    if not path.startswith("/api/v1/"):
        return True

    # 豁免路径
    if path in _AUTH_EXEMPT_PATHS:
        return True

    # 获取 auth_provider 模块
    # 如果 auth_provider 未加载，则无法验证 Key，放行避免阻断所有请求
    mod = _modules.get("auth_provider")
    if not mod:
        return True

    # 读取 Authorization header
    auth_header = handler.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        handler._send_json(
            {"error": "Authorization header required (Bearer <api_key>)"}, 401
        )
        return False

    api_key = auth_header[len("Bearer "):].strip()
    if not api_key:
        handler._send_json({"error": "Invalid API key"}, 401)
        return False

    # 验证 API Key
    try:
        mgr = mod.APIKeyManager()
        key_info = mgr.verify_key(api_key)
    except Exception as e:
        handler._send_json({"error": f"Auth service error: {str(e)}"}, 500)
        return False

    if not key_info:
        handler._send_json({"error": "Invalid or expired API key"}, 401)
        return False

    # 验证成功，挂载 agent_id 到 handler
    handler._auth_agent_id = key_info.get("agent_id", "")
    return True


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

    # Collab: 列出频道
    if path == "/api/v1/collab/channels":
        mod = _modules.get("collab")
        if mod:
            bus = mod.MessageBus()
            bus._load()
            channels = bus._data.get("channels", {}) if hasattr(bus, '_data') else {}
            handler._send_json({"success": True, "channels": channels, "total": len(channels)})
            return True

    # Collab: 消费消息
    if path == "/api/v1/collab/messages":
        mod = _modules.get("collab")
        if mod:
            bus = mod.MessageBus()
            agent_id = qs.get("agent_id", [None])[0]
            channel = qs.get("channel", [None])[0]
            # P0-1 修复: consume() 签名为 subscriber_agent_id，而非 agent_id
            result = bus.consume(subscriber_agent_id=agent_id, channel=channel)
            handler._send_json({"success": True, "messages": result if isinstance(result, list) else []})
            return True

    # Collab: 会话消息
    if path.startswith("/api/v1/collab/sessions/") and path.endswith("/messages"):
        mod = _modules.get("collab")
        if mod:
            sid = path[len("/api/v1/collab/sessions/"):-len("/messages")]
            sess = mod.CollaborationSession()
            result = sess.get_session_messages(sid)
            handler._send_json({"success": True, "messages": result if isinstance(result, list) else []})
            return True

    # Collab: 列出委托
    if path == "/api/v1/collab/delegations":
        mod = _modules.get("collab")
        if mod:
            agent_id = qs.get("agent_id", [None])[0]
            status = qs.get("status", [None])[0]
            delg = mod.TaskDelegation()
            result = delg.list_delegations(agent_id=agent_id, status=status)
            handler._send_json({"success": True, "delegations": result if isinstance(result, list) else []})
            return True

    # Skills: 搜索技能（/api/v1/skills/agent/ 前缀必须先于 /api/v1/skills/{skill_id}）
    if path.startswith("/api/v1/skills/agent/"):
        mod = _modules.get("skill_market")
        if mod:
            agent_id = path[len("/api/v1/skills/agent/"):]
            reg = mod.SkillRegistry()
            result = reg.list_by_agent(agent_id)
            handler._send_json({"success": True, **result})
            return True

    # Skills: 技能列表
    if path == "/api/v1/skills":
        mod = _modules.get("skill_market")
        if mod:
            reg = mod.SkillRegistry()
            query = qs.get("q", [None])[0]
            category = qs.get("category", [None])[0]
            result = reg.search(query=query, category=category)
            handler._send_json({"success": True, **result})
            return True

    # Skills: 技能评分
    if path.startswith("/api/v1/skills/") and path.endswith("/ratings"):
        mod = _modules.get("skill_market")
        if mod:
            skill_id = path[len("/api/v1/skills/"):-len("/ratings")]
            rating = mod.SkillRating()
            result = rating.get_ratings(skill_id)
            handler._send_json({"success": True, **result})
            return True

    # Skills: 技能详情
    if path.startswith("/api/v1/skills/"):
        mod = _modules.get("skill_market")
        if mod:
            skill_id = path[len("/api/v1/skills/"):]
            reg = mod.SkillRegistry()
            result = reg.get_skill(skill_id)
            handler._send_json({"success": True, **result})
            return True

    # Sandbox: 列出任务
    if path == "/api/v1/sandbox/tasks":
        mod = _modules.get("sandbox")
        if mod:
            agent_id = qs.get("agent_id", [None])[0]
            status = qs.get("status", [None])[0]
            task = mod.SandboxTask()
            result = task.list_tasks(agent_id=agent_id, status=status)
            handler._send_json({"success": True, **result})
            return True

    # Auth: 列出API Key
    if path == "/api/v1/auth/keys":
        mod = _modules.get("auth_provider")
        if mod:
            auth_header = handler.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                handler._send_json({"error": "Authorization header required"}, 401)
                return True
            agent_id = qs.get("agent_id", [None])[0]
            mgr = mod.APIKeyManager()
            result = mgr.list_keys(agent_id=agent_id)
            handler._send_json({"success": True, **result})
            return True

    # Auth: 作用域列表
    if path == "/api/v1/auth/scopes":
        mod = _modules.get("auth_provider")
        if mod:
            mgr = mod.ScopeManager()
            handler._send_json({"success": True, "scopes": mod.SCOPES})
            return True

    # Auth: 审计日志
    if path == "/api/v1/auth/audit":
        mod = _modules.get("auth_provider")
        if mod:
            agent_id = qs.get("agent_id", [None])[0]
            logger = mod.AuditLogger()
            result = logger.query_events(agent_id=agent_id)
            handler._send_json({"success": True, "events": result if isinstance(result, list) else []})
            return True

    # Account: 查询当前用户信息
    if path == "/api/v1/account/me":
        mod = _modules.get("account")
        if mod:
            account = mod._get_auth_account(handler)
            if not account:
                handler._send_json({"error": "Unauthorized"}, 401)
                return True
            info = mod.UserAccount().get_user_info(account["account_id"])
            handler._send_json({"success": True, "account": info})
            return True

    # Account: 查询余额
    if path == "/api/v1/account/balance":
        mod = _modules.get("account")
        if mod:
            account = mod._get_auth_account(handler)
            if not account:
                handler._send_json({"error": "Unauthorized"}, 401)
                return True
            try:
                balance = mod.UserAccount().get_balance(account["account_id"])
                handler._send_json({"success": True, "account_id": account["account_id"], "balance": balance})
            except ValueError as e:
                handler._send_json({"error": str(e)}, 400)
            return True

    return False


def dispatch_post(handler, data):
    """分发POST请求。返回True如果处理了。"""
    parsed = urlparse(handler.path)
    path = parsed.path

    # Account: 注册（无需认证）
    if path == "/api/v1/account/register":
        mod = _modules.get("account")
        if mod:
            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "")
            if not name or not email or not password:
                handler._send_json({"error": "name, email, password 均为必填"}, 400)
                return True
            try:
                mgr = mod.UserAccount()
                result = mgr.register(name, email, password)
                handler._send_json({"success": True, **result}, 201)
            except ValueError as e:
                handler._send_json({"error": str(e)}, 409)
            return True

    # Account: 登录（无需认证）
    if path == "/api/v1/account/login":
        mod = _modules.get("account")
        if mod:
            email = data.get("email", "").strip()
            password = data.get("password", "")
            if not email or not password:
                handler._send_json({"error": "email, password 均为必填"}, 400)
                return True
            try:
                mgr = mod.UserAccount()
                result = mgr.login(email, password)
                handler._send_json({"success": True, **result})
            except ValueError as e:
                handler._send_json({"error": str(e)}, 401)
            return True

    # Account: 充值（无需认证，按接口设计直接调用）
    if path == "/api/v1/account/recharge":
        mod = _modules.get("account")
        if mod:
            account_id = data.get("account_id", "").strip()
            amount = float(data.get("amount", 0))
            gateway = data.get("gateway", "alipay")
            if not account_id or amount <= 0:
                handler._send_json({"error": "account_id 和 amount 为必填，且 amount > 0"}, 400)
                return True
            try:
                mgr = mod.UserAccount()
                result = mgr.recharge(account_id, amount, gateway)
                handler._send_json({"success": True, **result})
            except ValueError as e:
                handler._send_json({"error": str(e)}, 400)
            return True

    # P0-4: 认证中间件 — 对 /api/v1/* POST 端点默认启用认证
    if not _require_auth(handler):
        return True

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

    # Collab: 发布消息
    if path == "/api/v1/collab/publish":
        mod = _modules.get("collab")
        if mod:
            bus = mod.MessageBus()
            result = bus.publish(
                channel=data.get("channel", ""),
                sender_agent_id=data.get("sender_agent_id", ""),
                message_type=data.get("message_type", "status"),
                payload=data.get("payload", {}),
            )
            handler._send_json({"success": True, **result})
            return True

    # Collab: 订阅频道
    if path == "/api/v1/collab/subscribe":
        mod = _modules.get("collab")
        if mod:
            bus = mod.MessageBus()
            result = bus.subscribe(
                channel=data.get("channel", ""),
                subscriber_agent_id=data.get("subscriber_agent_id", ""),
            )
            handler._send_json({"success": True, **result})
            return True

    # Collab: 创建协作会话
    if path == "/api/v1/collab/sessions":
        mod = _modules.get("collab")
        if mod:
            sess = mod.CollaborationSession()
            result = sess.create_session(
                initiator_agent_id=data.get("initiator_agent_id", ""),
                task_description=data.get("task_description", ""),
                participant_agent_ids=data.get("participant_agent_ids", []),
            )
            handler._send_json({"success": True, **result})
            return True

    # Collab: 委托任务
    if path == "/api/v1/collab/delegate":
        mod = _modules.get("collab")
        if mod:
            delg = mod.TaskDelegation()
            result = delg.delegate(
                task_description=data.get("task_description", ""),
                from_agent_id=data.get("from_agent_id", ""),
                to_agent_id=data.get("to_agent_id", ""),
            )
            handler._send_json({"success": True, **result})
            return True

    # Collab: 接受委托
    if path.startswith("/api/v1/collab/delegations/") and path.endswith("/accept"):
        mod = _modules.get("collab")
        if mod:
            did = path[len("/api/v1/collab/delegations/"):-len("/accept")]
            delg = mod.TaskDelegation()
            result = delg.accept_delegation(did, agent_id=data.get("agent_id", ""))
            handler._send_json({"success": True, **result})
            return True

    # Collab: 提交委托结果
    if path.startswith("/api/v1/collab/delegations/") and path.endswith("/result"):
        mod = _modules.get("collab")
        if mod:
            did = path[len("/api/v1/collab/delegations/"):-len("/result")]
            delg = mod.TaskDelegation()
            result = delg.submit_result(did, result_data=data.get("result", {}))
            handler._send_json({"success": True, **result})
            return True

    # Skills: 发布技能
    if path == "/api/v1/skills/publish":
        mod = _modules.get("skill_market")
        if mod:
            reg = mod.SkillRegistry()
            result = reg.publish(
                agent_id=data.get("agent_id", ""),
                name=data.get("name", ""),
                description=data.get("description", ""),
                category=data.get("category", "security"),
            )
            handler._send_json({"success": True, **result})
            return True

    # Skills: 调用技能
    if path.startswith("/api/v1/skills/") and path.endswith("/invoke"):
        mod = _modules.get("skill_market")
        if mod:
            skill_id = path[len("/api/v1/skills/"):-len("/invoke")]
            invoker = mod.SkillInvoker()
            result = invoker.invoke(
                skill_id,
                caller_agent_id=data.get("caller_agent_id", ""),
                input_data=data.get("input_data", {}),
                account_id=data.get("account_id"),
            )
            handler._send_json({"success": True, **result})
            return True

    # Sandbox: 提交并执行任务
    if path == "/api/v1/sandbox/execute":
        mod = _modules.get("sandbox")
        if mod:
            task = mod.SandboxTask()
            task_dict = task.submit(
                agent_id=data.get("agent_id", ""),
                code=data.get("code", ""),
                language=data.get("language", "python"),
            )
            if task_dict.get("status") == "rejected":
                handler._send_json({"success": False, **task_dict})
            else:
                result = task.execute_pending(task_dict["task_id"])
                handler._send_json({"success": True, **result})
            return True

    # Auth: 生成API Key
    if path == "/api/v1/auth/keys":
        mod = _modules.get("auth_provider")
        if mod:
            mgr = mod.APIKeyManager()
            result = mgr.generate_key(
                agent_id=data.get("agent_id", ""),
                key_name=data.get("key_name", ""),
            )
            handler._send_json({"success": True, **result})
            return True

    # Auth: 撤销API Key
    if path.startswith("/api/v1/auth/keys/") and path.endswith("/revoke"):
        mod = _modules.get("auth_provider")
        if mod:
            key_id = path[len("/api/v1/auth/keys/"):-len("/revoke")]
            mgr = mod.APIKeyManager()
            # P0-1 修复: revoke_key() 签名为 agent_id，而非 revoked_by
            result = mgr.revoke_key(key_id, agent_id=data.get("revoked_by", ""))
            handler._send_json({"success": True, **result} if isinstance(result, dict) else {"success": bool(result)})
            return True

    # Scan: API扫描
    if path == "/api/v1/scan/api":
        from scanner.api_scanner import APIScanOrchestrator
        url = data.get("url", "")
        if not url:
            handler._send_json({"error": "url is required"}, 400)
            return True
        try:
            orchestrator = APIScanOrchestrator()
            result = orchestrator.scan(spec_source=url)
            handler._send_json({"success": True, **result})
        except Exception as e:
            handler._send_json({"error": str(e)}, 500)
        return True

    return False
