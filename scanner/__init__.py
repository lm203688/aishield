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
# 统一导出面（F3 收口）：目标端注册表 + 配置化；含 OCSF 1.1 / STIX 2.1
from .export_registry import (
    TARGETS as EXPORT_TARGETS, TargetConfig, export as export_findings,
    export_to, batch_export, load_config as load_export_config,
)
# 评分可解释（M3 收口）：扣分账本闭合 + 独立复算回放。
# 注意 explain_score 这个名字留给 engine 的文本版（历史兼容），这里导出的是
# 机器可读版与审计/复算，用不冲突的名字，免得后来的 import 把前面的覆盖掉。
from .score_explain import (
    audit as audit_score, replay as replay_score, explain as explain_score_json,
    attribution_text as score_attribution_text,
)
from .policy import load_policy, evaluate_policy
from .telemetry import record_scan, get_aggregates, reset as telemetry_reset
from .live_probe import probe_server_metadata
from .registry_discovery import discover_across_registries, search_registry
from .engine import explain_score
# Fleet 中心化聚合 (F5)
from .fleet import FleetService, ingest as fleet_ingest, summary as fleet_summary, list_members as fleet_list_members, version_stream as fleet_version_stream
from .diff import diff_scans, diff_summary
from .fuzzing import fuzz, FuzzReport
# 基线漂移扫描（借鉴 agent-audit save-baseline + agentgraph 定义钉扎 + Snyk toxic flow）
from .baseline_scan import (
    build_baseline,
    check_drift,
    detect_toxic_flows,
    baseline_scan,
    definition_fingerprints,
)
# 合规映射（借鉴 Latteflo/mcp-scanner：findings → NIST CSF / ISO 27001 / PCI DSS）
from .compliance import compliance_summary, controls_for_category, CATEGORY_CONTROLS

__all__ = [
    "get_rule_count", "get_all_rules", "OWASP_MCP_TOP10",
    "scan", "batch_scan",
    "detect_rug_pull",
    "build_baseline", "check_drift", "detect_toxic_flows",
    "baseline_scan", "definition_fingerprints",
    "compliance_summary", "controls_for_category", "CATEGORY_CONTROLS",
    "verify_handshake",
    "APIScanOrchestrator",
    # 多客户端 MCP 配置发现（纯离线，绝不执行被扫命令）
    "discover_client_configs", "scan_client_configs", "discover_and_scan",
    "CLIENT_PROFILES",
    # 新增能力（D1/M3/M4/F2/F3/F6/D3/D4）
    "check_osv", "solve_minimal_removal", "attack_graph_json",
    "to_nucleus", "to_splunk", "to_attack_graph",
    # 统一导出面（F3 收口）+ 评分可解释（M3 收口）
    "EXPORT_TARGETS", "TargetConfig", "export_findings", "export_to", "batch_export",
    "load_export_config", "audit_score", "replay_score", "explain_score_json",
    "score_attribution_text",
    "load_policy", "evaluate_policy",
    "record_scan", "get_aggregates", "telemetry_reset",
    "probe_server_metadata", "discover_across_registries", "search_registry",
    "explain_score",
    # Fleet 中心化聚合 (F5)
    "FleetService", "fleet_ingest", "fleet_summary", "fleet_list_members", "fleet_version_stream",
]