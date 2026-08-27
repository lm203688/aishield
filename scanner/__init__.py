"""AIShield Scanner - OWASP MCP Top 10 对齐安全扫描引擎"""
from .rules import get_rule_count, get_all_rules, OWASP_MCP_TOP10
from .engine import scan, batch_scan
from .rug_pull import detect_rug_pull
from .handshake import verify_handshake
from .api_scanner import APIScanOrchestrator
from .client_discovery import (
    discover_client_configs,
    scan_client_configs,
    discover_and_scan,
    CLIENT_PROFILES,
)
# 投资人视角战略补齐的能力模块（见 docs/investor-strategy-2026-08.md）
from .osv import check_osv
from .attack_path import solve_minimal_removal, attack_graph_json
from .exporters import to_nucleus, to_splunk, to_attack_graph
from .policy import load_policy, evaluate_policy
from .telemetry import record_scan, get_aggregates, reset as telemetry_reset
from .live_probe import probe_server_metadata
from .registry_discovery import discover_across_registries, search_registry
from .engine import explain_score
# Fleet 中心化聚合 (F5)
from .fleet import FleetService, ingest as fleet_ingest, summary as fleet_summary, list_members as fleet_list_members
from .diff import diff_scans, diff_summary
from .fuzzing import fuzz, FuzzReport

__all__ = [
    "get_rule_count", "get_all_rules", "OWASP_MCP_TOP10",
    "scan", "batch_scan",
    "detect_rug_pull",
    "verify_handshake",
    "APIScanOrchestrator",
    # 多客户端 MCP 配置发现（纯离线，绝不执行被扫命令）
    "discover_client_configs", "scan_client_configs", "discover_and_scan",
    "CLIENT_PROFILES",
    # 新增能力（D1/M3/M4/F2/F3/F6/D3/D4）
    "check_osv", "solve_minimal_removal", "attack_graph_json",
    "to_nucleus", "to_splunk", "to_attack_graph",
    "load_policy", "evaluate_policy",
    "record_scan", "get_aggregates", "telemetry_reset",
    "probe_server_metadata", "discover_across_registries", "search_registry",
    "explain_score",
    # Fleet 中心化聚合 (F5)
    "FleetService", "fleet_ingest", "fleet_summary", "fleet_list_members",
]