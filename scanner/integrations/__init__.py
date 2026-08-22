"""
AIShield Scanner Integrations
================================
外部项目集成模块 —— 提升安全扫描和威胁情报能力。

模块列表：
- bb_browser: BB Browser 威胁情报采集（36平台103命令）
- browser_use: Browser Use AI 浏览器安全扫描
- graph_db: 图数据库威胁图谱（Neo4j/FalkorDB/ArangoDB）
- event_stream: Apache Kafka/Flink 实时事件管道
- scan_isolation: vCluster 隔离扫描环境
- persistent_agent: Grok Bot 持久化安全监控

用法：
    from scanner.integrations import (
        BBBrowserAdapter,
        BrowserScanAdapter,
        ThreatGraphIntegration,
        EventPipeline,
        VClusterManager,
        PersistentAgent,
    )
"""

from scanner.integrations.bb_browser import BBBrowserAdapter
from scanner.integrations.browser_use import BrowserScanAdapter
from scanner.integrations.graph_db import ThreatGraphIntegration
from scanner.integrations.event_stream import EventPipeline, SecurityEvent, EventType, EventPriority
from scanner.integrations.scan_isolation import VClusterManager
from scanner.integrations.persistent_agent import PersistentAgent

__all__ = [
    "BBBrowserAdapter",
    "BrowserScanAdapter",
    "ThreatGraphIntegration",
    "EventPipeline",
    "SecurityEvent",
    "EventType",
    "EventPriority",
    "VClusterManager",
    "PersistentAgent",
]
