"""
AIShield 策略即代码 (F6)

用声明式治理策略约束扫描结果，落地企业合规门禁：
  - 最低总分 / 各维度最低分
  - 每严重级最多允许数（0 即零容忍）
  - 阻断的 OWASP 类别（如出现即失败）
  - 传输约束（禁止无认证远程 server）
  - server 黑白名单

策略文件支持 YAML（需 pyyaml）或 JSON。仓库内置默认策略 policies/default.json。
"""
from __future__ import annotations

import json
import os

DEFAULT_POLICY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "policies", "default.json")


def load_policy(path: str | None = None) -> dict:
    """加载策略（YAML 优先，降级 JSON）。"""
    path = path or DEFAULT_POLICY_PATH
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    low = path.lower()
    if low.endswith((".yaml", ".yml")):
        try:
            import yaml
            return yaml.safe_load(text)
        except ImportError:
            # 退化为极简 YAML：仅支持本治理 schema 的 key: value 顶层 + 列表
            return _mini_yaml(text)
    return json.loads(text)


def _mini_yaml(text: str) -> dict:
    """无 pyyaml 时的极简策略解析（仅支持顶层 key: value 与 - 列表）。"""
    policy: dict = {}
    list_key = None
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith("- "):
            if list_key:
                policy.setdefault(list_key, [])
                policy[list_key].append(line[2:].strip())
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if v == "":
                list_key = k
                policy[k] = []
            else:
                list_key = None
                policy[k] = _coerce(v)
    return policy


def _coerce(v: str):
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    try:
        return int(v)
    except ValueError:
        return v


def evaluate_policy(scan_result: dict, policy: dict | None = None,
                    policy_path: str | None = None) -> dict:
    """
    评估扫描结果是否满足策略。

    Args:
        scan_result: engine.scan() 的输出（含 scores / findings / risk_level）
        policy: 已加载策略 dict；或传 policy_path 加载
    Returns:
        {passed, score, violations:[{rule, detail, severity}], policy_name}
    """
    if policy is None:
        policy = load_policy(policy_path)

    violations: list[dict] = []
    scores = scan_result.get("scores") or {
        "overall_score": scan_result.get("overall_score", 0),
        "security_score": scan_result.get("security_score", 0),
        "permissions_score": scan_result.get("permissions_score", 0),
        "data_handling_score": scan_result.get("data_handling_score", 0),
        "supply_chain_score": scan_result.get("supply_chain_score", 0),
        "reliability_score": scan_result.get("reliability_score", 0),
    }
    findings = scan_result.get("findings", [])

    # 1) 最低总分
    min_overall = policy.get("min_overall_score")
    if min_overall is not None and scores.get("overall_score", 0) < min_overall:
        violations.append({"rule": "min_overall_score", "detail":
            f"总分 {scores.get('overall_score')} < 要求 {min_overall}", "severity": "high"})

    # 2) 各维度最低分
    for dim in ("security_score", "permissions_score", "data_handling_score",
                "supply_chain_score", "reliability_score"):
        mv = policy.get("min_" + dim)
        if mv is not None and scores.get(dim, 0) < mv:
            violations.append({"rule": "min_" + dim, "detail":
                f"{dim} {scores.get(dim)} < 要求 {mv}", "severity": "high"})

    # 3) 每严重级最多允许数
    max_by_sev = policy.get("max_findings_by_severity", {})
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.get("severity", "info")] = counts.get(f.get("severity", "info"), 0) + 1
    for sev, limit in (max_by_sev or {}).items():
        if counts.get(sev, 0) > limit:
            violations.append({"rule": "max_findings_by_severity",
                "detail": f"{sev} 级漏洞 {counts.get(sev)} > 上限 {limit}", "severity": sev})

    # 4) 阻断的 OWASP 类别
    blocked = policy.get("blocked_owasp_categories", [])
    for f in findings:
        cat = f.get("owasp_category", "")
        if cat in blocked:
            violations.append({"rule": "blocked_owasp_categories",
                "detail": f"出现被阻断类别 {cat}: {f.get('description','')}", "severity": "critical"})

    # 5) 传输约束：禁止无认证远程 server
    if policy.get("disallow_unauthenticated_remote"):
        for f in findings:
            if f.get("type") == "unauthenticated_remote" or "无认证" in f.get("description", ""):
                violations.append({"rule": "disallow_unauthenticated_remote",
                    "detail": f.get("description", ""), "severity": "high"})

    # 6) 黑名单命中
    denylist = policy.get("deny_servers", [])
    names = " ".join(str(f.get("name", "")) for f in [scan_result])
    for d in denylist:
        if d and d in (scan_result.get("name", "") or ""):
            violations.append({"rule": "deny_servers", "detail": f"命中黑名单 server: {d}",
                "severity": "critical"})

    return {
        "passed": len(violations) == 0,
        "score": scores.get("overall_score", 0),
        "violations": violations,
        "policy_name": policy.get("name", "default"),
    }
