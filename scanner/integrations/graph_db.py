"""
Graph Database Integration for AIShield
========================================
用图数据库存储和分析威胁情报关系网络。

核心能力：
- 威胁图谱：CVE → 攻击者 → 基础设施 → 受影响资产
- 攻击链推断：从一个 IOC 自动发现关联 TTP
- 7 跳关系查询：< 350ms
- 支持 Neo4j / FalkorDB / ArangoDB

参考:
- Neo4j Cyber Threat Intelligence (Apache 2.0)
- FalkorDB Securin Case Study (0.3s 7-hop queries)
- CrowdStrike Threat Graph (trillions of events/day)
"""

import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================
# 数据模型
# ============================================================

class NodeType(str, Enum):
    """图节点类型"""
    CVE = "CVE"
    ATTACKER = "Attacker"
    MALWARE = "Malware"
    IP = "IP"
    DOMAIN = "Domain"
    URL = "URL"
    VULNERABILITY = "Vulnerability"
    ASSET = "Asset"
    TOOL = "Tool"
    TTP = "TTP"  # Tactics, Techniques, and Procedures
    CAMPAIGN = "Campaign"
    REPORT = "Report"


class EdgeType(str, Enum):
    """图边类型"""
    EXPLOITS = "EXPLOITS"
    USES = "USES"
    TARGETS = "TARGETS"
    ORIGINATES_FROM = "ORIGINATES_FROM"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"
    MITIGATES = "MITIGATES"
    DETECTS = "DETECTS"


@dataclass
class GraphNode:
    """图节点"""
    node_type: NodeType
    properties: Dict[str, Any]
    node_id: Optional[str] = None

    def __post_init__(self):
        if not self.node_id:
            # 自动生成唯一 ID
            key_parts = [self.node_type.value]
            for k in sorted(self.properties.keys()):
                key_parts.append(f"{k}={self.properties[k]}")
            self.node_id = hashlib.md5(
                "|".join(key_parts).encode()
            ).hexdigest()[:12]


@dataclass
class GraphEdge:
    """图边"""
    edge_type: EdgeType
    source_id: str
    target_id: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatPath:
    """威胁路径（查询结果）"""
    path: List[Dict[str, Any]]
    relationships: List[str]
    risk_score: float
    description: str


# ============================================================
# 图数据库适配器
# ============================================================

class GraphDatabaseAdapter:
    """
    图数据库适配器 - 支持多种图数据库后端

    支持的后端：
    - Neo4j: 功能最全，适合复杂查询
    - FalkorDB: 性能最优，7-hop 查询 < 350ms
    - ArangoDB: 多模型，适合混合场景
    """

    def __init__(
        self,
        backend: str = "neo4j",
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "",
        database: str = "aishield",
    ):
        self.backend = backend
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver = None

    def connect(self):
        """连接到图数据库"""
        if self.backend == "neo4j":
            self._connect_neo4j()
        elif self.backend == "falkordb":
            self._connect_falkordb()
        elif self.backend == "arangodb":
            self._connect_arangodb()
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def _connect_neo4j(self):
        """连接 Neo4j"""
        try:
            from neo4j import GraphDatabase as Neo4jDriver
            self._driver = Neo4jDriver.auth(self.uri, self.username, self.password)
            logger.info("Connected to Neo4j: %s", self.uri)
        except ImportError:
            logger.warning("Neo4j driver not installed: pip install neo4j")

    def _connect_falkordb(self):
        """连接 FalkorDB"""
        try:
            import falkordb
            self._driver = falkordb.FalkorDB(
                host=self.uri.split("//")[1].split(":")[0],
                port=int(self.uri.split(":")[-1]),
                password=self.password,
            )
            logger.info("Connected to FalkorDB: %s", self.uri)
        except ImportError:
            logger.warning("FalkorDB driver not installed: pip install falkordb")

    def _connect_arangodb(self):
        """连接 ArangoDB"""
        try:
            from arango import ArangoClient
            client = ArangoClient(hosts=self.uri)
            self._driver = client.db(
                self.database,
                username=self.username,
                password=self.password,
            )
            logger.info("Connected to ArangoDB: %s", self.uri)
        except ImportError:
            logger.warning("ArangoDB driver not installed: pip install python-arango")

    def close(self):
        """关闭连接"""
        if self._driver:
            if hasattr(self._driver, 'close'):
                self._driver.close()
            self._driver = None

    # ============================================================
    # CRUD 操作
    # ============================================================

    def add_node(self, node: GraphNode) -> str:
        """添加节点"""
        if self.backend == "neo4j":
            return self._add_node_neo4j(node)
        elif self.backend == "falkordb":
            return self._add_node_falkordb(node)
        elif self.backend == "arangodb":
            return self._add_node_arangodb(node)
        return node.node_id

    def add_edge(self, edge: GraphEdge) -> bool:
        """添加边"""
        if self.backend == "neo4j":
            return self._add_edge_neo4j(edge)
        elif self.backend == "falkordb":
            return self._add_edge_falkordb(edge)
        elif self.backend == "arangodb":
            return self._add_edge_arangodb(edge)
        return True

    def _add_node_neo4j(self, node: GraphNode) -> str:
        query = (
            f"MERGE (n:{node.node_type.value} {{id: $id}}) "
            f"SET n += $props "
            f"RETURN n.id"
        )
        with self._driver.session(database=self.database) as session:
            result = session.run(query, id=node.node_id, props=node.properties)
            return result.single()[0]

    def _add_node_falkordb(self, node: GraphNode) -> str:
        graph = self._driver.select_graph(self.database)
        graph.merge(
            node.node_type.value,
            node.node_id,
            node.properties,
        )
        return node.node_id

    def _add_node_arangodb(self, node: GraphNode) -> str:
        collection = self._driver.collection(node.node_type.value)
        collection.insert({
            "_key": node.node_id,
            **node.properties,
        })
        return node.node_id

    def _add_edge_neo4j(self, edge: GraphEdge) -> bool:
        query = (
            f"MATCH (a {{id: $src}}), (b {{id: $tgt}}) "
            f"MERGE (a)-[r:{edge.edge_type.value}]->(b) "
            f"SET r += $props"
        )
        with self._driver.session(database=self.database) as session:
            session.run(query, src=edge.source_id, tgt=edge.target_id, props=edge.properties)
            return True

    def _add_edge_falkordb(self, edge: GraphEdge) -> bool:
        graph = self._driver.select_graph(self.database)
        graph.merge_relationship(
            edge.edge_type.value,
            {"_from": edge.source_id, "_to": edge.target_id, **edge.properties},
        )
        return True

    def _add_edge_arangodb(self, edge: GraphEdge) -> bool:
        edge_col = self._driver.edge_collection(edge.edge_type.value)
        edge_col.insert({
            "_from": f"{edge.source_id.split('_')[0]}/{edge.source_id}",
            "_to": f"{edge.target_id.split('_')[0]}/{edge.target_id}",
            **edge.properties,
        })
        return True

    # ============================================================
    # 威胁情报查询
    # ============================================================

    def find_attack_chain(self, cve_id: str, max_depth: int = 5) -> List[ThreatPath]:
        """
        从 CVE 出发，发现完整攻击链

        查询路径：CVE → 攻击者 → 工具 → 基础设施 → 受影响资产
        """
        if self.backend == "neo4j":
            return self._find_chain_neo4j(cve_id, max_depth)
        elif self.backend == "falkordb":
            return self._find_chain_falkordb(cve_id, max_depth)
        return []

    def _find_chain_neo4j(self, cve_id: str, max_depth: int) -> List[ThreatPath]:
        query = f"""
        MATCH path = (c:CVE {{id: $cve_id}})-[*1..{max_depth}]-(target)
        WHERE ALL(r IN relationships(path) WHERE r IS NOT NULL)
        RETURN path,
               [r IN relationships(path) | type(r)] AS rels,
               length(path) AS depth
        ORDER BY depth
        LIMIT 50
        """
        paths = []
        with self._driver.session(database=self.database) as session:
            for record in session.run(query, cve_id=cve_id):
                path_data = []
                for node in record["path"].nodes:
                    path_data.append({
                        "type": list(node.labels)[0],
                        "id": node["id"],
                        "properties": dict(node),
                    })
                paths.append(ThreatPath(
                    path=path_data,
                    relationships=record["rels"],
                    risk_score=self._calculate_risk_score(record["rels"]),
                    description=" → ".join(record["rels"]),
                ))
        return paths

    def _find_chain_falkordb(self, cve_id: str, max_depth: int) -> List[ThreatPath]:
        graph = self._driver.select_graph(self.database)
        query = f"""
        FOR v, e IN 1..{max_depth} ANY 'CVE/{cve_id}' GRAPH '{self.database}'
        RETURN v, e,.depth AS d
        LIMIT 50
        """
        paths = []
        result = graph.aql.execute(query)
        for record in result:
            paths.append(ThreatPath(
                path=[{"type": record["v"].get("type", ""), "properties": record["v"]}],
                relationships=[record["e"].get("type", "")],
                risk_score=0.5,
                description=record["e"].get("type", ""),
            ))
        return paths

    def get_related_cves(self, cve_id: str, max_hops: int = 2) -> List[Dict[str, Any]]:
        """获取相关 CVE"""
        if self.backend == "neo4j":
            query = f"""
            MATCH (c:CVE {{id: $cve_id}})-[*1..{max_hops}]-(related:CVE)
            RETURN DISTINCT related.id, related.description, related.severity
            LIMIT 20
            """
            results = []
            with self._driver.session(database=self.database) as session:
                for record in session.run(query, cve_id=cve_id):
                    results.append({
                        "cve_id": record["related.id"],
                        "description": record.get("related.description", ""),
                        "severity": record.get("related.severity", ""),
                    })
            return results
        return []

    def get_threat_landscape(self) -> Dict[str, Any]:
        """获取整体威胁态势"""
        if self.backend == "neo4j":
            query = """
            MATCH (n)
            RETURN labels(n)[0] AS type, count(n) AS count
            ORDER BY count DESC
            """
            stats = {}
            with self._driver.session(database=self.database) as session:
                for record in session.run(query):
                    stats[record["type"]] = record["count"]
            return stats
        return {}

    def search_iocs(
        self,
        keyword: str,
        node_types: Optional[List[NodeType]] = None,
    ) -> List[Dict[str, Any]]:
        """搜索 IOC（威胁指标）"""
        if self.backend == "neo4j":
            type_filter = ""
            if node_types:
                types = ", ".join(f"'{t.value}'" for t in node_types)
                type_filter = f"WHERE labels(n)[0] IN [{types}]"

            query = f"""
            MATCH (n) {type_filter}
            WHERE ANY(key IN keys(n) WHERE n[key] CONTAINS $keyword)
            RETURN labels(n)[0] AS type, n.id AS id, n
            LIMIT 50
            """
            results = []
            with self._driver.session(database=self.database) as session:
                for record in session.run(query, keyword=keyword):
                    results.append({
                        "type": record["type"],
                        "id": record["id"],
                        "properties": dict(record["n"]),
                    })
            return results
        return []

    # ============================================================
    # 威胁情报入库
    # ============================================================

    def ingest_threat_intel(self, intel_data: Dict[str, Any]) -> Dict[str, int]:
        """
        导入威胁情报数据

        Args:
            intel_data: 情报数据，包含 nodes 和 edges
        """
        stats = {"nodes_added": 0, "edges_added": 0}

        for node_data in intel_data.get("nodes", []):
            node = GraphNode(
                node_type=NodeType(node_data["type"]),
                properties=node_data.get("properties", {}),
                node_id=node_data.get("id"),
            )
            self.add_node(node)
            stats["nodes_added"] += 1

        for edge_data in intel_data.get("edges", []):
            edge = GraphEdge(
                edge_type=EdgeType(edge_data["type"]),
                source_id=edge_data["source"],
                target_id=edge_data["target"],
                properties=edge_data.get("properties", {}),
            )
            self.add_edge(edge)
            stats["edges_added"] += 1

        logger.info("Ingested threat intel: %s", stats)
        return stats

    def ingest_cve_batch(self, cves: List[Dict[str, Any]]) -> Dict[str, int]:
        """批量导入 CVE 数据"""
        nodes = []
        edges = []

        for cve in cves:
            cve_id = cve.get("id", "")
            nodes.append({
                "type": "CVE",
                "id": cve_id,
                "properties": {
                    "description": cve.get("description", ""),
                    "severity": cve.get("severity", "unknown"),
                    "published": cve.get("published", ""),
                    "source": cve.get("source", ""),
                },
            })

            # 关联 CWE
            for cwe in cve.get("cwes", []):
                nodes.append({
                    "type": "Vulnerability",
                    "id": cwe,
                    "properties": {"type": "CWE"},
                })
                edges.append({
                    "type": "RELATED_TO",
                    "source": cve_id,
                    "target": cwe,
                })

            # 关联受影响资产
            for pkg in cve.get("affected_packages", []):
                nodes.append({
                    "type": "ASSET",
                    "id": f"pkg:{pkg}",
                    "properties": {"type": "package", "name": pkg},
                })
                edges.append({
                    "type": "TARGETS",
                    "source": cve_id,
                    "target": f"pkg:{pkg}",
                })

        return self.ingest_threat_intel({"nodes": nodes, "edges": edges})

    def _calculate_risk_score(self, relationships: List[str]) -> float:
        """计算风险评分"""
        risk_weights = {
            "EXPLOITS": 1.0,
            "USES": 0.8,
            "TARGETS": 0.9,
            "ORIGINATES_FROM": 0.7,
            "COMMUNICATES_WITH": 0.6,
        }
        if not relationships:
            return 0.0
        total = sum(risk_weights.get(r, 0.3) for r in relationships)
        return min(total / len(relationships), 1.0)


# ============================================================
# 与 AIShield Scanner 集成
# ============================================================

class ThreatGraphIntegration:
    """
    AIShield 威胁图谱集成

    用法：
        graph = ThreatGraphIntegration()
        graph.connect()

        # 导入情报
        graph.ingest_cves(cve_list)

        # 查询攻击链
        chain = graph.query_attack_chain("CVE-2026-12345")

        # 获取威胁态势
        landscape = graph.get_landscape()
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        self.adapter = GraphDatabaseAdapter(
            backend=config.get("backend", "neo4j"),
            uri=config.get("uri", "bolt://localhost:7687"),
            username=config.get("username", "neo4j"),
            password=config.get("password", ""),
            database=config.get("database", "aishield"),
        )

    def connect(self):
        self.adapter.connect()

    def close(self):
        self.adapter.close()

    def ingest_cves(self, cves: List[Dict[str, Any]]) -> Dict[str, int]:
        return self.adapter.ingest_cve_batch(cves)

    def query_attack_chain(self, cve_id: str) -> List[Dict[str, Any]]:
        paths = self.adapter.find_attack_chain(cve_id)
        return [
            {
                "path": p.path,
                "relationships": p.relationships,
                "risk_score": p.risk_score,
                "description": p.description,
            }
            for p in paths
        ]

    def get_landscape(self) -> Dict[str, Any]:
        return self.adapter.get_threat_landscape()

    def search(self, keyword: str) -> List[Dict[str, Any]]:
        return self.adapter.search_iocs(keyword)

    def to_aishield_finding(self, threat_path: ThreatPath) -> Dict[str, Any]:
        """将威胁路径转换为 AIShield 发现格式"""
        return {
            "type": "threat_graph",
            "description": threat_path.description,
            "risk_score": threat_path.risk_score,
            "path_length": len(threat_path.path),
            "nodes": threat_path.path,
            "owasp_category": "MCP05",
            "severity": "critical" if threat_path.risk_score > 0.8 else "high",
        }
