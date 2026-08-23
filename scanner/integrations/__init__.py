"""
AIShield Scanner Integrations
================================
澶栭儴椤圭洰闆嗘垚妯″潡 鈥斺€?鎻愬崌瀹夊叏鎵弿鍜屽▉鑳佹儏鎶ヨ兘鍔涖€?
妯″潡鍒楄〃锛?- bb_browser: BB Browser 濞佽儊鎯呮姤閲囬泦锛?6骞冲彴103鍛戒护锛?- browser_use: Browser Use AI 娴忚鍣ㄥ畨鍏ㄦ壂鎻?- graph_db: 鍥炬暟鎹簱濞佽儊鍥捐氨锛圢eo4j/FalkorDB/ArangoDB锛?- event_stream: Apache Kafka/Flink 瀹炴椂浜嬩欢绠￠亾
- scan_isolation: vCluster 闅旂鎵弿鐜
- persistent_agent: Grok Bot 鎸佷箙鍖栧畨鍏ㄧ洃鎺?
鐢ㄦ硶锛?    from scanner.integrations import (
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
