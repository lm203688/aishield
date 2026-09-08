# -*- coding: utf-8 -*-
"""
合规框架映射模块（Compliance Mapping）

借鉴来源（2026-09-07 开源扫描）:
    - Latteflo/mcp-scanner: 每条 finding 自动映射到合规框架控制项
      （ISO/IEC 27001 / NIST CSF / PCI DSS / SOC 2）—— 企业采购决策中
      「能否对接 GRC/审计流程」是关键选型因素，纯报告层实现、不动检测逻辑。

设计哲学（与全库一致）:
    - 纯标准库，零第三方依赖，零网络
    - 映射是**静态知识**（OWASP 类别 → 框架控制项），不判断合规与否、
      不给"合规分数"——那是认证机构的职权，AIShield 保持中性信任机构定位
    - 聚合在报告级而非逐条注入：findings 数组保持轻量，兼容既有消费者

框架与版本锚定:
    - NIST Cybersecurity Framework 2.0 (2024-02): PR.AA / PR.DS / PR.PS /
      DE.CM / ID.AM / ID.RA 等类别码
    - ISO/IEC 27001:2022 Annex A（A.5.x 组织 / A.8.x 技术控制）
    - PCI DSS v4.0 要求编号
"""
from __future__ import annotations

from typing import Any, Dict, List

# OWASP MCP Top 10 / Agentic AI Top 10 → 控制项映射（静态知识）
# 条目取"最相关的 2-3 项"——穷举等于没映射，选型者要的是锚点不是噪音。
CATEGORY_CONTROLS: Dict[str, Dict[str, List[str]]] = {
    "MCP01": {  # 令牌管理不当与密钥暴露
        "nist_csf": ["PR.AA-01", "PR.DS-01"],
        "iso27001": ["A.5.17", "A.8.24"],
        "pci_dss": ["8.2", "3.5"],
    },
    "MCP02": {  # 权限范围蔓延导致提权
        "nist_csf": ["PR.AA-05"],
        "iso27001": ["A.5.15", "A.8.2"],
        "pci_dss": ["7.2"],
    },
    "MCP03": {  # 工具投毒
        "nist_csf": ["PR.PS-06", "DE.CM-09"],
        "iso27001": ["A.8.28", "A.5.37"],
        "pci_dss": ["6.2.4"],
    },
    "MCP04": {  # 软件供应链攻击与依赖篡改
        "nist_csf": ["PR.PS-06", "ID.RA-01"],
        "iso27001": ["A.5.21", "A.8.30"],
        "pci_dss": ["6.3.2"],
    },
    "MCP05": {  # 命令注入与执行
        "nist_csf": ["PR.PS-01", "DE.CM-01"],
        "iso27001": ["A.8.28", "A.8.32"],
        "pci_dss": ["6.2.4"],
    },
    "MCP06": {  # 意图流颠覆/上下文提示注入
        "nist_csf": ["PR.PS-01", "DE.AE-02"],
        "iso27001": ["A.8.28", "A.5.37"],
        "pci_dss": ["6.2.4"],
    },
    "MCP07": {  # 身份认证与授权不足
        "nist_csf": ["PR.AA-03", "PR.AA-05"],
        "iso27001": ["A.5.15", "A.8.5"],
        "pci_dss": ["8.2", "7.2"],
    },
    "MCP08": {  # 审计与可观测性缺失
        "nist_csf": ["PR.PS-04", "DE.CM-09"],
        "iso27001": ["A.8.15", "A.8.16"],
        "pci_dss": ["10.2"],
    },
    "MCP09": {  # 影子 MCP 服务器
        "nist_csf": ["ID.AM-01", "PR.AA-05"],
        "iso27001": ["A.5.9", "A.5.19"],
        "pci_dss": ["12.5.2"],
    },
    "MCP10": {  # 上下文注入与过度共享（含 SSRF）
        "nist_csf": ["DE.CM-01", "PR.DS-02"],
        "iso27001": ["A.8.20", "A.8.22"],
        "pci_dss": ["1.2", "11.5"],
    },
    "ASI01": {  # 目标与指令操纵（提示注入）
        "nist_csf": ["PR.PS-01", "DE.AE-02"],
        "iso27001": ["A.8.28"],
        "pci_dss": ["6.2.4"],
    },
    "ASI02": {  # 工具滥用
        "nist_csf": ["PR.AA-05", "DE.CM-09"],
        "iso27001": ["A.5.15", "A.8.28"],
        "pci_dss": ["7.2"],
    },
    "ASI03": {  # 过度代理 / 凭证外泄
        "nist_csf": ["PR.AA-05", "PR.DS-02"],
        "iso27001": ["A.5.15", "A.8.12"],
        "pci_dss": ["3.5", "7.2"],
    },
    "ASI04": {  # 记忆操纵与投毒
        "nist_csf": ["PR.DS-01", "PR.PS-06"],
        "iso27001": ["A.8.24", "A.8.28"],
        "pci_dss": ["6.2.4"],
    },
    "ASI05": {  # 智能体身份与信任
        "nist_csf": ["PR.AA-01", "PR.AA-03"],
        "iso27001": ["A.5.16", "A.5.17"],
        "pci_dss": ["8.2"],
    },
    "ASI06": {  # 智能体通信与供应链
        "nist_csf": ["PR.PS-06", "PR.IR-01"],
        "iso27001": ["A.5.21", "A.8.22"],
        "pci_dss": ["6.3.2", "1.2"],
    },
    "ASI07": {  # 资源无界消耗
        "nist_csf": ["PR.IR-04"],
        "iso27001": ["A.8.6", "A.8.14"],
        "pci_dss": ["2.2"],
    },
    "ASI08": {  # 可观测性缺口
        "nist_csf": ["PR.PS-04", "DE.CM-09"],
        "iso27001": ["A.8.15", "A.8.16"],
        "pci_dss": ["10.2"],
    },
    "ASI09": {  # 级联失效与多智能体风险
        "nist_csf": ["PR.IR-04", "DE.AE-06"],
        "iso27001": ["A.5.30", "A.8.14"],
        "pci_dss": ["2.2"],
    },
    "ASI10": {  # 流氓智能体 / 人机边界
        "nist_csf": ["GV.PO-02", "PR.AA-05"],
        "iso27001": ["A.5.4", "A.5.15"],
        "pci_dss": ["12.5.2"],
    },
}

FRAMEWORKS = ("nist_csf", "iso27001", "pci_dss")

_SEV_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def compliance_summary(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    把 findings 按 owasp_category 聚合为合规控制项视图。

    Returns:
        {
          "frameworks": {fw: {"controls_hit": n, "controls": {code: {...}}}},
          "categories_mapped": n,     # 有 finding 且可映射的 OWASP 类别数
          "findings_unmapped": n,     # 无 owasp_category 或未知类别的条数
          "note": "映射为审计锚点，不构成合规认证",
        }
    """
    out: Dict[str, Any] = {
        "frameworks": {fw: {} for fw in FRAMEWORKS},
        "categories_mapped": 0,
        "findings_unmapped": 0,
        "note": "映射为审计锚点（select-the-control），不构成合规认证结论",
    }

    seen_categories = set()
    for f in findings or []:
        if not isinstance(f, dict):
            continue
        cat = f.get("owasp_category", "")
        mapping = CATEGORY_CONTROLS.get(cat)
        if not mapping:
            out["findings_unmapped"] += 1
            continue
        seen_categories.add(cat)
        sev = str(f.get("severity", "info")).lower()
        for fw in FRAMEWORKS:
            for code in mapping.get(fw, []):
                slot = out["frameworks"][fw].setdefault(
                    code, {"findings_count": 0, "max_severity": "info"}
                )
                slot["findings_count"] += 1
                if _SEV_RANK.get(sev, 0) > _SEV_RANK.get(slot["max_severity"], 0):
                    slot["max_severity"] = sev

    out["categories_mapped"] = len(seen_categories)
    # frameworks[fw] 变回 {code: {...}} → 顶层再包一层计数，方便渲染摘要
    for fw in FRAMEWORKS:
        out["frameworks"][fw] = {
            "controls_hit": len(out["frameworks"][fw]),
            "controls": out["frameworks"][fw],
        }
    return out


def controls_for_category(category: str) -> Dict[str, List[str]]:
    """单类别查询（报告模板 / API 单点查询用）。未知类别返回空映射。"""
    return CATEGORY_CONTROLS.get(category, {fw: [] for fw in FRAMEWORKS})
