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

__all__ = [
    "get_rule_count", "get_all_rules", "OWASP_MCP_TOP10",
    "scan", "batch_scan",
    "detect_rug_pull",
    "verify_handshake",
    "APIScanOrchestrator",
    # 多客户端 MCP 配置发现（纯离线，绝不执行被扫命令）
    "discover_client_configs", "scan_client_configs", "discover_and_scan",
    "CLIENT_PROFILES",
]