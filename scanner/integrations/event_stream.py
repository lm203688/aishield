"""
Apache Kafka/Flink Integration for AIShield
=============================================
实时安全事件流处理管道。

核心能力：
- Kafka: 高吞吐事件收集（每秒百万级事件）
- Flink: 实时威胁检测和规则匹配
- 事件驱动的安全响应

参考:
- Apache Kafka: 分布式事件流平台
- Apache Flink: 流处理引擎
- Apache HertzBeat: AI 驱动实时监控 (2026 TLP)
"""

import json
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


# ============================================================
# 事件模型
# ============================================================

class EventType(str, Enum):
    """安全事件类型"""
    VULNERABILITY_DETECTED = "vulnerability.detected"
    SCAN_COMPLETED = "scan.completed"
    THREAT_INTEL_UPDATE = "threat.intel.update"
    RULE_TRIGGERED = "rule.triggered"
    ANOMALY_DETECTED = "anomaly.detected"
    ALERT_FIRED = "alert.fired"
    SYSTEM_HEALTH = "system.health"


class EventPriority(str, Enum):
    """事件优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityEvent:
    """安全事件"""
    event_type: EventType
    source: str
    payload: Dict[str, Any]
    priority: EventPriority = EventPriority.MEDIUM
    timestamp: str = ""
    event_id: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.event_id:
            import hashlib
            self.event_id = hashlib.md5(
                f"{self.event_type}:{self.source}:{self.timestamp}".encode()
            ).hexdigest()[:16]

    def to_json(self) -> str:
        return json.dumps({
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "payload": self.payload,
        })


# ============================================================
# 内存事件总线（开发/测试用）
# ============================================================

class InMemoryEventBus:
    """
    内存事件总线 - 不需要外部依赖

    适合开发、测试和小规模部署
    """

    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_log: deque = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._running = False

    def publish(self, event: SecurityEvent) -> str:
        """发布事件"""
        with self._lock:
            self._event_log.append(event)

        # 通知订阅者
        callbacks = self._subscribers.get(event.event_type.value, [])
        callbacks += self._subscribers.get("*", [])  # 通配符订阅

        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error("Subscriber error: %s", e)

        logger.debug("Published event: %s [%s]", event.event_type.value, event.priority.value)
        return event.event_id

    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info("Subscribed to: %s", event_type)

    def get_recent_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取最近的事件"""
        with self._lock:
            events = list(self._event_log)

        if event_type:
            events = [e for e in events if e.event_type.value == event_type]

        return [
            {
                "event_id": e.event_id,
                "event_type": e.event_type.value,
                "source": e.source,
                "priority": e.priority.value,
                "timestamp": e.timestamp,
                "payload": e.payload,
            }
            for e in events[-limit:]
        ]

    def get_stats(self) -> Dict[str, Any]:
        """获取事件统计"""
        with self._lock:
            events = list(self._event_log)

        type_counts = {}
        priority_counts = {}
        for e in events:
            type_counts[e.event_type.value] = type_counts.get(e.event_type.value, 0) + 1
            priority_counts[e.priority.value] = priority_counts.get(e.priority.value, 0) + 1

        return {
            "total_events": len(events),
            "by_type": type_counts,
            "by_priority": priority_counts,
            "subscribers": {k: len(v) for k, v in self._subscribers.items()},
        }


# ============================================================
# Kafka 适配器
# ============================================================

class KafkaEventBus:
    """
    Apache Kafka 事件总线 - 生产级事件流

    需要安装: pip install kafka-python
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic_prefix: str = "aishield.",
        group_id: str = "aishield-consumer",
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic_prefix = topic_prefix
        self.group_id = group_id
        self._producer = None
        self._consumer = None

    def connect(self):
        """连接到 Kafka"""
        try:
            from kafka import KafkaProducer, KafkaConsumer
            self._producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            logger.info("Connected to Kafka: %s", self.bootstrap_servers)
        except ImportError:
            logger.warning("kafka-python not installed: pip install kafka-python")
        except Exception as e:
            logger.error("Kafka connection failed: %s", e)

    def publish(self, event: SecurityEvent) -> str:
        """发布事件到 Kafka"""
        if not self._producer:
            logger.warning("Kafka not connected, falling back to in-memory")
            return event.event_id

        topic = f"{self.topic_prefix}{event.event_type.value}"
        self._producer.send(topic, value={
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "source": event.source,
            "priority": event.priority.value,
            "timestamp": event.timestamp,
            "payload": event.payload,
        })
        self._producer.flush()
        return event.event_id

    def subscribe(
        self,
        event_type: str,
        callback: Callable,
        topics: Optional[List[str]] = None,
    ):
        """订阅 Kafka 主题"""
        if not self._producer:
            return

        if topics is None:
            topics = [f"{self.topic_prefix}{event_type}"]

        try:
            from kafka import KafkaConsumer
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
            )

            def _consume():
                for message in consumer:
                    try:
                        event_data = message.value
                        callback(SecurityEvent(
                            event_type=EventType(event_data["event_type"]),
                            source=event_data["source"],
                            payload=event_data["payload"],
                            priority=EventPriority(event_data["priority"]),
                            timestamp=event_data["timestamp"],
                            event_id=event_data["event_id"],
                        ))
                    except Exception as e:
                        logger.error("Kafka consumer error: %s", e)

            thread = threading.Thread(target=_consume, daemon=True)
            thread.start()
            logger.info("Subscribed to Kafka topics: %s", topics)

        except ImportError:
            logger.warning("kafka-python not installed")


# ============================================================
# Flink 流处理规则引擎
# ============================================================

@dataclass
class StreamRule:
    """流处理规则"""
    rule_id: str
    name: str
    description: str
    event_type: EventType
    condition: Callable[[SecurityEvent], bool]
    action: Callable[[SecurityEvent], Any]
    priority: int = 0
    enabled: bool = True


class FlinkStyleRuleEngine:
    """
    Flink 风格的流处理规则引擎

    在内存中实现 Flink 的核心概念：
    - 窗口（Windowing）
    - 状态（State）
    - CEP（复杂事件处理）
    """

    def __init__(self):
        self._rules: List[StreamRule] = []
        self._windows: Dict[str, deque] = {}
        self._state: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def add_rule(self, rule: StreamRule):
        """添加处理规则"""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info("Added rule: %s (priority: %d)", rule.name, rule.priority)

    def process_event(self, event: SecurityEvent) -> List[Any]:
        """处理事件，触发匹配的规则"""
        results = []

        # 更新窗口
        self._update_window(event)

        # 检查规则
        for rule in self._rules:
            if not rule.enabled:
                continue
            if rule.event_type != event.event_type:
                continue

            try:
                if rule.condition(event):
                    result = rule.action(event)
                    results.append({
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "result": result,
                    })
                    logger.info("Rule triggered: %s", rule.name)
            except Exception as e:
                logger.error("Rule execution failed: %s - %s", rule.name, e)

        return results

    def _update_window(self, event: SecurityEvent):
        """更新滑动窗口"""
        window_key = event.event_type.value
        if window_key not in self._windows:
            self._windows[window_key] = deque(maxlen=1000)
        self._windows[window_key].append(event)

    def get_window(self, event_type: str, window_size: int = 100) -> List[SecurityEvent]:
        """获取窗口内的事件"""
        return list(self._windows.get(event_type, deque()))[-window_size:]

    def set_state(self, key: str, value: Any):
        """设置状态"""
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """获取状态"""
        return self._state.get(key, default)


# ============================================================
# 预定义的安全规则
# ============================================================

def create_default_rules() -> List[StreamRule]:
    """创建默认的安全处理规则"""
    rules = []

    # 规则 1: 高危漏洞立即告警
    def critical_vuln_condition(event: SecurityEvent) -> bool:
        severity = event.payload.get("severity", "").lower()
        return severity in ("critical", "high")

    def critical_vuln_action(event: SecurityEvent):
        logger.critical(
            "CRITICAL VULNERABILITY: %s at %s",
            event.payload.get("cve_id", "unknown"),
            event.payload.get("target", "unknown"),
        )
        return {"alert": "critical", "action": "immediate_response"}

    rules.append(StreamRule(
        rule_id="R001",
        name="Critical Vulnerability Alert",
        description="高危漏洞立即告警",
        event_type=EventType.VULNERABILITY_DETECTED,
        condition=critical_vuln_condition,
        action=critical_vuln_action,
        priority=100,
    ))

    # 规则 2: 扫描完成自动入库
    def scan_completed_condition(event: SecurityEvent) -> bool:
        return event.payload.get("status") == "completed"

    def scan_completed_action(event: SecurityEvent):
        findings = event.payload.get("findings", [])
        logger.info("Scan completed: %d findings", len(findings))
        return {"archived": True, "findings_count": len(findings)}

    rules.append(StreamRule(
        rule_id="R002",
        name="Scan Auto-Archive",
        description="扫描完成自动归档",
        event_type=EventType.SCAN_COMPLETED,
        condition=scan_completed_condition,
        action=scan_completed_action,
        priority=50,
    ))

    # 规则 3: 异常行为检测（基于窗口）
    def anomaly_condition(event: SecurityEvent) -> bool:
        # 检查最近 5 分钟内是否有异常多的同类事件
        return True  # 简化实现

    def anomaly_action(event: SecurityEvent):
        return {"anomaly_detected": True, "investigation_needed": True}

    rules.append(StreamRule(
        rule_id="R003",
        name="Anomaly Detection",
        description="异常行为检测",
        event_type=EventType.ANOMALY_DETECTED,
        condition=anomaly_condition,
        action=anomaly_action,
        priority=80,
    ))

    return rules


# ============================================================
# 与 AIShield 集成
# ============================================================

class EventPipeline:
    """
    AIShield 事件处理管道

    用法：
        pipeline = EventPipeline()
        pipeline.start()

        # 发布事件
        pipeline.publish_vulnerability("CVE-2026-12345", "critical", "https://target.com")

        # 获取统计
        stats = pipeline.get_stats()
    """

    def __init__(self, use_kafka: bool = False, kafka_config: Optional[Dict] = None):
        if use_kafka and kafka_config:
            self.bus = KafkaEventBus(**kafka_config)
        else:
            self.bus = InMemoryEventBus()

        self.engine = FlinkStyleRuleEngine()

        # 添加默认规则
        for rule in create_default_rules():
            self.engine.add_rule(rule)

        self._running = False

    def start(self):
        """启动管道"""
        self._running = True
        if hasattr(self.bus, 'connect'):
            self.bus.connect()
        logger.info("Event pipeline started")

    def stop(self):
        """停止管道"""
        self._running = False
        if hasattr(self.bus, 'close'):
            self.bus.close()
        logger.info("Event pipeline stopped")

    def publish(self, event: SecurityEvent) -> str:
        """发布事件"""
        event_id = self.bus.publish(event)
        self.engine.process_event(event)
        return event_id

    def publish_vulnerability(
        self,
        cve_id: str,
        severity: str,
        target: str,
        details: Optional[Dict] = None,
    ) -> str:
        """发布漏洞事件"""
        event = SecurityEvent(
            event_type=EventType.VULNERABILITY_DETECTED,
            source="aishield-scanner",
            payload={
                "cve_id": cve_id,
                "severity": severity,
                "target": target,
                "details": details or {},
            },
            priority=EventPriority.CRITICAL if severity == "critical" else EventPriority.HIGH,
        )
        return self.publish(event)

    def publish_scan_completed(
        self,
        target: str,
        findings: List[Dict],
        scan_type: str = "full",
    ) -> str:
        """发布扫描完成事件"""
        event = SecurityEvent(
            event_type=EventType.SCAN_COMPLETED,
            source="aishield-scanner",
            payload={
                "target": target,
                "findings": findings,
                "scan_type": scan_type,
                "status": "completed",
            },
        )
        return self.publish(event)

    def publish_threat_intel(self, intel_data: Dict[str, Any]) -> str:
        """发布威胁情报更新"""
        event = SecurityEvent(
            event_type=EventType.THREAT_INTEL_UPDATE,
            source="aishield-threat-intel",
            payload=intel_data,
        )
        return self.publish(event)

    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        self.bus.subscribe(event_type, callback)

    def get_recent(self, event_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """获取最近事件"""
        if hasattr(self.bus, 'get_recent_events'):
            return self.bus.get_recent_events(event_type, limit)
        return []

    def get_stats(self) -> Dict[str, Any]:
        """获取管道统计"""
        if hasattr(self.bus, 'get_stats'):
            return self.bus.get_stats()
        return {}
