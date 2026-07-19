"""AIShield Python SDK"""
__version__ = "4.1.0"

import json
import urllib.request
import urllib.error


class AIShieldClient:
    """AIShield API Client — OWASP MCP Top 10 aligned security scanner"""

    def __init__(self, api_url="https://api.aishield.dev", api_key=None):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key

    def _request(self, path, data=None, method="POST"):
        url = f"{self.api_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"AIShield-Python-SDK/{__version__}",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            raise AIShieldError(e.code, error_body)

    # ========== 安全端点 ==========

    def scan(self, source_url, tool_type="mcp", name=""):
        """完整安全扫描 — OWASP MCP Top 10，82+ 条规则，5 维度评分"""
        return self._request("/api/v1/audit", {
            "source_url": source_url,
            "tool_type": tool_type,
            "name": name,
        })

    def guardrail(self, source_url, auto_block=True):
        """安装前安全检查 — 返回 pass/block 判定结果"""
        result = self.scan(source_url, "mcp", "")
        score = result.get("report", {}).get("overall_score", 0)
        result["verdict"] = "pass" if score >= 70 else "block"
        return result

    def prompt_check(self, prompt):
        """提示注入检测 — 支持中英文双语"""
        return self._request("/api/v1/prompt-check", {"prompt": prompt})

    def banned_words(self, text, platform="all"):
        """违禁词检测 — 覆盖 6 大主流内容平台"""
        return self._request("/api/v1/banned-words", {"text": text, "platform": platform})

    def rug_pull(self, source_url):
        """Rug Pull 风险检测 — 识别恶意工具撤回/欺诈行为"""
        return self._request("/api/v1/rug-pull", {"source_url": source_url})

    def handshake(self, source_url):
        """工具握手验证 — 验证远端工具的身份与可达性"""
        return self._request("/api/v1/handshake", {"source_url": source_url})

    def health(self):
        """API 健康检查 — 返回服务运行状态"""
        return self._request("/api/v1/health", method="GET")

    def stats(self):
        """使用统计 — 返回平台调用与扫描统计数据"""
        return self._request("/api/v1/stats", method="GET")

    # ========== 生态端点 ==========

    def identity_register(self, name, owner, capabilities=None):
        """注册 AI Agent 数字身份 — 绑定名称、所有者与能力声明"""
        if capabilities is None:
            capabilities = []
        return self._request("/api/v1/identity/register", {
            "name": name,
            "owner": owner,
            "capabilities": capabilities,
        })

    def identity_list(self):
        """查询已注册的 AI Agent 身份列表"""
        return self._request("/api/v1/identity/agents", method="GET")

    def identity_get(self, did):
        """根据 DID 查询指定 AI Agent 的身份详情"""
        return self._request(f"/api/v1/identity/agents/{did}", method="GET")

    def badge_svg(self, tool_name, score, level="A"):
        """获取安全徽章 SVG — 用于在 README 或网站中嵌入安全评分图标"""
        return self._request(
            f"/api/v1/badge/{tool_name}",
            method="GET",
        )

    def certify(self, source_url, scan_report=None):
        """提交认证申请 — 将扫描报告上链/存证，获取安全证书"""
        return self._request("/api/v1/certify", {
            "source_url": source_url,
            "scan_report": scan_report,
        })

    def billing_plans(self):
        """查询计费方案 — 返回可用套餐与定价信息"""
        return self._request("/api/v1/billing/plans", method="GET")

    def billing_usage(self, user_id, endpoint=None):
        """查询用量记录 — 按用户和端点筛选调用明细"""
        data = {"user_id": user_id}
        if endpoint is not None:
            data["endpoint"] = endpoint
        return self._request("/api/v1/billing/usage", data)

    def market_tools(self, category=None, page=1):
        """浏览工具市场 — 按分类分页查询已上架的安全工具"""
        path = "/api/v1/market/tools"
        query_parts = []
        if category:
            query_parts.append(f"category={category}")
        query_parts.append(f"page={page}")
        if query_parts:
            path += "?" + "&".join(query_parts)
        return self._request(path, method="GET")

    def a2a_discover(self, skill=None):
        """发现 A2A 服务 — 根据技能关键词搜索可用的 Agent 服务"""
        path = "/api/v1/a2a/discover"
        if skill:
            path += f"?skill={skill}"
        return self._request(path, method="GET")

    def a2a_register_card(self, data):
        """注册 Agent Card — 向 A2A 协议注册智能体服务卡片"""
        return self._request("/api/v1/a2a/agent-card", data)

    def a2a_create_task(self, task_description, task_type="general", skills=None, payload=None):
        """创建 A2A 任务 — 向目标 Agent 下发协作任务"""
        if skills is None:
            skills = []
        body = {
            "task_description": task_description,
            "task_type": task_type,
            "skills": skills,
        }
        if payload is not None:
            body["payload"] = payload
        return self._request("/api/v1/a2a/task", body)


class AIShieldError(Exception):
    def __init__(self, status_code, body=""):
        self.status_code = status_code
        self.body = body
        super().__init__(f"AIShield API {status_code}: {body[:200]}")


# ========== 便捷函数 ==========

_default_client = None


def get_client():
    """获取全局默认 AIShield 客户端实例"""
    global _default_client
    if _default_client is None:
        _default_client = AIShieldClient()
    return _default_client


def scan(source_url, tool_type="mcp", name=""):
    """完整安全扫描（便捷函数）"""
    return get_client().scan(source_url, tool_type, name)


def prompt_check(prompt):
    """提示注入检测（便捷函数）"""
    return get_client().prompt_check(prompt)


def banned_words(text, platform="all"):
    """违禁词检测（便捷函数）"""
    return get_client().banned_words(text, platform)


def rug_pull(source_url):
    """Rug Pull 风险检测（便捷函数）"""
    return get_client().rug_pull(source_url)


def handshake(source_url):
    """工具握手验证（便捷函数）"""
    return get_client().handshake(source_url)


def health():
    """API 健康检查（便捷函数）"""
    return get_client().health()


def stats():
    """使用统计（便捷函数）"""
    return get_client().stats()


def identity_register(name, owner, capabilities=None):
    """注册 AI Agent 数字身份（便捷函数）"""
    return get_client().identity_register(name, owner, capabilities)


def identity_list():
    """查询已注册 Agent 列表（便捷函数）"""
    return get_client().identity_list()


def identity_get(did):
    """查询指定 Agent 身份详情（便捷函数）"""
    return get_client().identity_get(did)


def badge_svg(tool_name, score, level="A"):
    """获取安全徽章 SVG（便捷函数）"""
    return get_client().badge_svg(tool_name, score, level)


def certify(source_url, scan_report=None):
    """提交认证申请（便捷函数）"""
    return get_client().certify(source_url, scan_report)


def billing_plans():
    """查询计费方案（便捷函数）"""
    return get_client().billing_plans()


def billing_usage(user_id, endpoint=None):
    """查询用量记录（便捷函数）"""
    return get_client().billing_usage(user_id, endpoint)


def market_tools(category=None, page=1):
    """浏览工具市场（便捷函数）"""
    return get_client().market_tools(category, page)


def a2a_discover(skill=None):
    """发现 A2A 服务（便捷函数）"""
    return get_client().a2a_discover(skill)


def a2a_register_card(data):
    """注册 Agent Card（便捷函数）"""
    return get_client().a2a_register_card(data)


def a2a_create_task(task_description, task_type="general", skills=None, payload=None):
    """创建 A2A 任务（便捷函数）"""
    return get_client().a2a_create_task(task_description, task_type, skills, payload)