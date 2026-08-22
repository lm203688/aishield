"""
Browser Use Integration for AIShield
====================================
AI 驱动的浏览器安全扫描引擎。

核心能力：
- 自然语言驱动的安全扫描
- DOM 蒸馏降低 67% token 消耗
- 反检测隐身模式
- 循环恢复机制

参考: https://github.com/browser-use/browser-use (MIT License, 103K+ stars)
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ScanTask:
    """浏览器扫描任务定义"""
    task_id: str
    target_url: str
    scan_type: str  # xss, sqli, csrf, recon, full
    description: str
    max_steps: int = 50
    timeout_seconds: int = 300


@dataclass
class ScanResult:
    """扫描结果"""
    task_id: str
    target_url: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    dom_snapshots: List[str] = field(default_factory=list)
    network_requests: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = False
    error: Optional[str] = None


# ============================================================
# 预定义的安全扫描任务模板
# ============================================================

SECURITY_SCAN_TEMPLATES = {
    "xss_scan": {
        "description": "Cross-Site Scripting 漏洞扫描",
        "tasks": [
            "Find all input fields on the page and try injecting <script>alert(1)</script>",
            "Check for reflected parameters in the URL",
            "Test form submissions with XSS payloads",
            "Look for innerHTML or eval usage in page scripts",
        ],
    },
    "sqli_scan": {
        "description": "SQL Injection 漏洞扫描",
        "tasks": [
            "Find all input fields and try SQL injection payloads",
            "Test URL parameters with ' OR 1=1 --",
            "Check for error-based SQL injection",
            "Test blind SQL injection with time delays",
        ],
    },
    "csrf_scan": {
        "description": "Cross-Site Request Forgery 漏洞扫描",
        "tasks": [
            "Identify all state-changing requests",
            "Check for CSRF tokens in forms",
            "Test if actions can be performed without authentication",
            "Check SameSite cookie attributes",
        ],
    },
    "recon": {
        "description": "目标侦察和信息收集",
        "tasks": [
            "Extract all links and endpoints from the page",
            "Find hidden form fields and parameters",
            "Identify JavaScript frameworks and versions",
            "Check for exposed API endpoints",
            "Extract all cookies and their attributes",
        ],
    },
    "auth_test": {
        "description": "认证和授权测试",
        "tasks": [
            "Test login for brute force protection",
            "Check session management",
            "Test privilege escalation",
            "Verify logout invalidates session",
        ],
    },
    "full_scan": {
        "description": "全面安全评估",
        "tasks": [
            "Perform reconnaissance and map all endpoints",
            "Test for XSS, SQLi, CSRF vulnerabilities",
            "Check authentication and authorization",
            "Test for sensitive data exposure",
            "Check security headers",
            "Verify HTTPS configuration",
        ],
    },
}


class BrowserUseScanner:
    """
    Browser Use 安全扫描引擎

    使用方式：
        scanner = BrowserUseScanner()
        # 执行 XSS 扫描
        result = await scanner.scan("https://target.com", scan_type="xss")
        # 全面扫描
        result = await scanner.full_scan("https://target.com")
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o",
        headless: bool = True,
        stealth_mode: bool = True,
        max_concurrent: int = 3,
    ):
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.headless = headless
        self.stealth_mode = stealth_mode
        self.max_concurrent = max_concurrent
        self._check_installation()

    def _check_installation(self):
        """检查 browser-use 是否已安装"""
        try:
            import browser_use
            logger.info("Browser Use installed: v%s", browser_use.__version__)
        except ImportError:
            logger.warning(
                "Browser Use not installed. Install: pip install browser-use"
            )

    async def scan(
        self,
        target_url: str,
        scan_type: str = "recon",
        custom_tasks: Optional[List[str]] = None,
        max_steps: int = 50,
    ) -> ScanResult:
        """
        执行安全扫描

        Args:
            target_url: 目标 URL
            scan_type: 扫描类型 (xss, sqli, csrf, recon, auth_test, full)
            custom_tasks: 自定义扫描任务列表
            max_steps: 最大执行步数
        """
        try:
            from browser_use import Agent, Browser
        except ImportError:
            return ScanResult(
                task_id="",
                target_url=target_url,
                success=False,
                error="browser-use not installed",
            )

        # 构建扫描任务
        template = SECURITY_SCAN_TEMPLATES.get(scan_type, SECURITY_SCAN_TEMPLATES["recon"])
        tasks = custom_tasks or template["tasks"]

        all_findings = []
        all_screenshots = []
        all_network = []

        for i, task_desc in enumerate(tasks):
            full_task = f"Go to {target_url} and {task_desc}"

            logger.info("Executing task %d/%d: %s", i + 1, len(tasks), task_desc)

            try:
                browser = Browser(
                    headless=self.headless,
                    # 反检测配置
                    extra_chromium_args=[
                        "--disable-blink-features=AutomationControlled",
                    ] if self.stealth_mode else [],
                )

                agent = Agent(
                    task=full_task,
                    llm=self._get_llm(),
                    browser=browser,
                    max_actions_per_step=5,
                )

                result = await agent.run(max_steps=max_steps)

                # 提取发现
                if result:
                    all_findings.append({
                        "task": task_desc,
                        "result": str(result),
                        "scan_type": scan_type,
                    })

            except Exception as e:
                logger.error("Task failed: %s - %s", task_desc, e)
                all_findings.append({
                    "task": task_desc,
                    "error": str(e),
                })

        return ScanResult(
            task_id=f"scan_{hash(target_url)}",
            target_url=target_url,
            findings=all_findings,
            screenshots=all_screenshots,
            network_requests=all_network,
            success=True,
        )

    async def full_scan(self, target_url: str) -> ScanResult:
        """执行全面安全扫描"""
        return await self.scan(target_url, scan_type="full")

    async def quick_recon(self, target_url: str) -> ScanResult:
        """快速侦察"""
        return await self.scan(
            target_url,
            scan_type="recon",
            max_steps=20,
        )

    async def test_xss(self, target_url: str, custom_payloads: Optional[List[str]] = None) -> ScanResult:
        """XSS 专项测试"""
        tasks = [
            f"Find all input fields on {target_url} and test each with these payloads: <script>alert('XSS')</script>, <img src=x onerror=alert(1)>, javascript:alert(1)",
            "Check for DOM-based XSS by analyzing JavaScript code",
            "Test URL parameter reflection",
            "Check for stored XSS in comment fields",
        ]
        if custom_payloads:
            tasks.append(f"Test these custom payloads: {', '.join(custom_payloads)}")

        return await self.scan(target_url, custom_tasks=tasks)

    async def enumerate_endpoints(self, target_url: str) -> Dict[str, Any]:
        """枚举所有端点和 API"""
        tasks = [
            f"Navigate to {target_url} and extract ALL links, forms, and API endpoints",
            "Check robots.txt and sitemap.xml",
            "Look for hidden endpoints in JavaScript code",
            "Identify REST/GraphQL API endpoints",
            "Check for common admin paths (/admin, /dashboard, /api/v1)",
        ]

        result = await self.scan(target_url, custom_tasks=tasks, max_steps=30)

        return {
            "target": target_url,
            "endpoints_found": len(result.findings),
            "findings": result.findings,
        }

    def _get_llm(self):
        """获取 LLM 实例"""
        if self.llm_provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=self.llm_model)
        elif self.llm_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=self.llm_model)
        elif self.llm_provider == "ollama":
            from langchain_community.llms import Ollama
            return Ollama(model=self.llm_model)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")


# ============================================================
# 与 AIShield Scanner 集成
# ============================================================

class BrowserScanAdapter:
    """
    将 Browser Use 集成到 AIShield 扫描引擎

    用法：
        adapter = BrowserScanAdapter()
        # 在 AIShield 扫描流程中调用
        results = adapter.scan_with_browser("https://target.com")
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        self.scanner = BrowserUseScanner(
            llm_provider=config.get("llm_provider", "openai"),
            llm_model=config.get("llm_model", "gpt-4o"),
            headless=config.get("headless", True),
            stealth_mode=config.get("stealth_mode", True),
        )

    def scan_with_browser(
        self,
        target_url: str,
        scan_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        使用浏览器执行安全扫描

        Args:
            target_url: 目标 URL
            scan_types: 要执行的扫描类型列表
        """
        if scan_types is None:
            scan_types = ["recon", "xss", "sqli"]

        loop = asyncio.new_event_loop()
        results = {}

        for scan_type in scan_types:
            logger.info("Running browser scan: %s on %s", scan_type, target_url)
            result = loop.run_until_complete(
                self.scanner.scan(target_url, scan_type=scan_type)
            )
            results[scan_type] = {
                "success": result.success,
                "findings_count": len(result.findings),
                "findings": result.findings,
                "error": result.error,
            }

        return {
            "target": target_url,
            "scans_executed": len(results),
            "results": results,
        }

    def to_aishield_findings(self, browser_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将浏览器扫描结果转换为 AIShield 发现格式"""
        findings = []

        for scan_type, result in browser_results.get("results", {}).items():
            for item in result.get("findings", []):
                findings.append({
                    "type": "browser_scan",
                    "scan_type": scan_type,
                    "target": browser_results.get("target"),
                    "description": item.get("task", ""),
                    "evidence": item.get("result", item.get("error", "")),
                    "severity": "medium",
                    "owasp_category": _map_scan_to_owasp(scan_type),
                })

        return findings


def _map_scan_to_owasp(scan_type: str) -> str:
    """将扫描类型映射到 OWASP 类别"""
    mapping = {
        "xss": "MCP03",      # Injection
        "sqli": "MCP03",     # Injection
        "csrf": "MCP01",     # Broken Authorization
        "auth_test": "MCP01",# Broken Authorization
        "recon": "MCP05",    # Security Misconfiguration
        "full": "MCP00",     # General
    }
    return mapping.get(scan_type, "MCP00")
