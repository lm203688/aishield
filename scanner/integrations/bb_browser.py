"""
BB Browser Integration for AIShield
====================================
利用真实浏览器登录态进行威胁情报采集和安全侦察。

核心优势：
- 复用真实 Chrome 登录态，对网站来说就是用户本人
- 自带 MCP Server，可直接与 AI Agent 对话
- 36 个平台 103 个命令，覆盖社交媒体/代码仓库/新闻/学术

参考: https://github.com/epiral/bb-browser (MIT License, 6K+ stars)
"""

import json
import subprocess
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BBSiteCommand:
    """BB Browser 站点命令定义"""
    platform: str
    command: str
    category: str  # search, social, news, dev, video, finance, etc.
    description: str
    example_args: List[str] = field(default_factory=list)


# 预定义的威胁情报相关站点命令
THREAT_INTEL_SOURCES = {
    "github_search": BBSiteCommand(
        platform="github",
        command="search",
        category="dev",
        description="搜索 GitHub 仓库/代码中的安全漏洞",
        example_args=["vulnerability", "CVE-2026"],
    ),
    "github_issues": BBSiteCommand(
        platform="github",
        command="issues",
        category="dev",
        description="查看 GitHub Issues 中的安全报告",
        example_args=["security", "vulnerability"],
    ),
    "twitter_search": BBSiteCommand(
        platform="twitter",
        command="search",
        category="social",
        description="搜索 Twitter 上的安全威胁情报",
        example_args=["zero-day", "exploit", "CVE"],
    ),
    "reddit_security": BBSiteCommand(
        platform="reddit",
        command="hot",
        category="social",
        description="获取 Reddit 安全社区热门话题",
        example_args=["netsec", "cybersecurity"],
    ),
    "arxiv_search": BBSiteCommand(
        platform="arxiv",
        command="search",
        category="dev",
        description="搜索学术论文中的安全研究",
        example_args=["adversarial machine learning", "prompt injection"],
    ),
    "stackoverflow_search": BBSiteCommand(
        platform="stackoverflow",
        command="search",
        category="dev",
        description="搜索 StackOverflow 安全问题",
        example_args=["MCP vulnerability", "API security"],
    ),
    "zhihu_hot": BBSiteCommand(
        platform="zhihu",
        command="hot",
        category="knowledge",
        description="获取知乎安全领域热门话题",
        example_args=[],
    ),
    "hackernews_top": BBSiteCommand(
        platform="hackernews",
        command="top",
        category="news",
        description="获取 HackerNews 安全相关热门",
        example_args=[],
    ),
    "36kr_security": BBSiteCommand(
        platform="36kr",
        command="newsflash",
        category="news",
        description="获取 36kr 安全资讯",
        example_args=[],
    ),
    "bilibili_search": BBSiteCommand(
        platform="bilibili",
        command="search",
        category="video",
        description="搜索 Bilibili 安全教程视频",
        example_args=["网络安全", "渗透测试"],
    ),
}


class BBBrowserAdapter:
    """
    BB Browser 适配器 - AIShield 威胁情报采集引擎

    使用方式：
        adapter = BBBrowserAdapter()
        # 搜索 GitHub 安全漏洞
        results = adapter.search_threats("CVE-2026", platform="github")
        # 获取多平台情报
        intel = adapter.cross_platform_research("AI agent vulnerability")
    """

    def __init__(
        self,
        daemon_host: str = "127.0.0.1",
        daemon_port: int = 19824,
        use_openclaw: bool = False,
    ):
        self.daemon_url = f"http://{daemon_host}:{daemon_port}"
        self.use_openclaw = use_openclaw
        self._check_installation()

    def _check_installation(self):
        """检查 bb-browser 是否已安装"""
        try:
            result = subprocess.run(
                ["bb-browser", "--version"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                logger.info("BB Browser installed: %s", result.stdout.strip())
            else:
                logger.warning("BB Browser not found. Install: npm install -g bb-browser")
        except FileNotFoundError:
            logger.warning("BB Browser not installed. Run: npm install -g bb-browser")
        except Exception as e:
            logger.warning("BB Browser check failed: %s", e)

    def _run_command(self, args: List[str], timeout: int = 30) -> Dict[str, Any]:
        """执行 BB Browser 命令"""
        cmd = ["bb-browser"] + args + ["--json"]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
            )
            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout.strip() else {}
            else:
                logger.error("BB Browser error: %s", result.stderr)
                return {"error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except json.JSONDecodeError:
            return {"raw": result.stdout}
        except Exception as e:
            return {"error": str(e)}

    def search_threats(
        self,
        query: str,
        platform: str = "github",
        command: str = "search",
        extra_args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        在指定平台搜索威胁情报

        Args:
            query: 搜索关键词
            platform: 平台名称 (github, twitter, arxiv, etc.)
            command: 命令名称 (search, hot, top, etc.)
            extra_args: 额外参数
        """
        args = ["site", f"{platform}/{command}"] + [query]
        if extra_args:
            args.extend(extra_args)
        return self._run_command(args)

    def cross_platform_research(
        self,
        topic: str,
        platforms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        跨平台威胁情报研究

        Args:
            topic: 研究主题
            platforms: 要搜索的平台列表
        """
        if platforms is None:
            platforms = ["github", "twitter", "arxiv", "stackoverflow", "zhihu"]

        results = {}
        for platform in platforms:
            source = THREAT_INTEL_SOURCES.get(f"{platform}_search")
            if source:
                logger.info("Searching %s for: %s", platform, topic)
                results[platform] = self.search_threats(topic, platform)
            else:
                # 通用搜索
                results[platform] = self.search_threats(topic, platform)

        return {
            "topic": topic,
            "platforms_searched": len(results),
            "results": results,
        }

    def monitor_security_communities(
        self,
        categories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        监控安全社区动态

        Args:
            categories: 监控类别 (social, dev, news, knowledge)
        """
        if categories is None:
            categories = ["social", "dev", "news"]

        monitored = {}
        for name, source in THREAT_INTEL_SOURCES.items():
            if source.category in categories:
                logger.info("Monitoring: %s/%s", source.platform, source.command)
                monitored[name] = self._run_command(
                    ["site", f"{source.platform}/{source.command}"]
                    + source.example_args
                )

        return {
            "categories": categories,
            "sources_monitored": len(monitored),
            "results": monitored,
        }

    def fetch_cve_details(self, cve_id: str) -> Dict[str, Any]:
        """获取特定 CVE 的详细信息"""
        results = {}

        # GitHub 搜索相关 PoC 和修复
        results["github_poc"] = self.search_threats(
            f"{cve_id} poc exploit", platform="github"
        )

        # Twitter 搜索讨论
        results["twitter_discussion"] = self.search_threats(
            cve_id, platform="twitter"
        )

        # 搜索学术分析
        results["arxiv_analysis"] = self.search_threats(
            cve_id, platform="arxiv"
        )

        return {
            "cve_id": cve_id,
            "sources_checked": len(results),
            "details": results,
        }

    def snapshot_page(self, url: str) -> Dict[str, Any]:
        """对目标页面进行快照（用于安全评估）"""
        return self._run_command(["open", url])

    def get_accessibility_tree(self) -> Dict[str, Any]:
        """获取当前页面的可访问性树（用于漏洞分析）"""
        return self._run_command(["snapshot", "-i"])

    def evaluate_javascript(self, expression: str) -> Dict[str, Any]:
        """在当前页面执行 JS（用于 XSS 检测）"""
        return self._run_command(["eval", expression])

    def capture_network_traffic(self) -> Dict[str, Any]:
        """捕获网络流量（用于 API 安全分析）"""
        return self._run_command(["network", "requests", "--with-body", "--json"])


# ============================================================
# MCP Server 集成接口
# ============================================================

def create_mcp_server_config() -> Dict[str, Any]:
    """
    生成 BB Browser MCP Server 配置

    用法：将此配置添加到 Claude Code / Cursor 的 MCP 配置中
    """
    return {
        "mcpServers": {
            "bb-browser": {
                "command": "npx",
                "args": ["-y", "bb-browser", "--mcp"],
            }
        }
    }


def get_bb_browser_tools() -> List[Dict[str, Any]]:
    """
    返回 BB Browser 暴露给 MCP 的工具列表

    这些工具可以被 AI Agent 直接调用
    """
    return [
        {
            "name": "bb_search_threats",
            "description": "在指定平台搜索安全威胁情报",
            "parameters": {
                "query": {"type": "string", "description": "搜索关键词"},
                "platform": {
                    "type": "string",
                    "enum": ["github", "twitter", "arxiv", "stackoverflow",
                             "zhihu", "reddit", "hackernews", "36kr"],
                    "description": "目标平台",
                },
            },
        },
        {
            "name": "bb_cross_platform_research",
            "description": "跨平台威胁情报研究，一次搜索多个平台",
            "parameters": {
                "topic": {"type": "string", "description": "研究主题"},
                "platforms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要搜索的平台列表",
                },
            },
        },
        {
            "name": "bb_fetch_cve",
            "description": "获取特定 CVE 的详细信息，跨平台搜索",
            "parameters": {
                "cve_id": {"type": "string", "description": "CVE 编号，如 CVE-2026-12345"},
            },
        },
        {
            "name": "bb_snapshot",
            "description": "对目标页面进行快照",
            "parameters": {
                "url": {"type": "string", "description": "目标 URL"},
            },
        },
        {
            "name": "bb_evaluate_js",
            "description": "在当前页面执行 JavaScript（用于安全测试）",
            "parameters": {
                "expression": {"type": "string", "description": "JS 表达式"},
            },
        },
    ]
