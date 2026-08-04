#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield 情报转规则引擎 (Intel → Detection Rules)
=================================================
评估报告指出的关键断点：**情报入库后，没有任何环节把它转成检测能力。**
情报库越攒越大，扫描器的规则却一条没变 —— 数据飞轮缺了最关键的那一齿，
采集到的情报只是躺在 JSON 里的死数据，不产生任何产品价值。

本模块补上这一齿，把权威漏洞情报自动转化为三类可执行检测规则：

  R1 漏洞包黑名单   —— 从 OSV/GHSA 的 affected 字段提取受影响包，
                        扫到依赖即告警（这是命中率最高的一类规则）
  R2 攻击模式规则   —— 从 CVE 描述中提取攻击手法特征，生成正则检测模式
  R3 OWASP 映射     —— 将漏洞归类到 OWASP LLM/Agent Top 10，支撑合规报告

输出：data/generated_rules.json（被 scanner/rules.py 在导入时自动合并）

用法：
    python scripts/intel_to_rules.py
    python scripts/intel_to_rules.py --notify
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

THREAT_DB = REPO_ROOT / "data" / "threat_intel.json"
OUT_RULES = REPO_ROOT / "data" / "generated_rules.json"

# 攻击手法 → 检测特征。key 为情报文本中的触发词，value 为生成的检测规则
ATTACK_PATTERNS = {
    "prompt injection": [
        (r"(?i)(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above)\s+(instruction|prompt|rule)",
         "提示注入: 覆盖历史指令", "critical", "LLM01"),
    ],
    "command injection": [
        (r"(?i)(os\.system|subprocess\.(call|run|Popen)|child_process\.exec)\s*\(\s*[^)]*(\+|%|\$\{|f['\"])",
         "命令注入: 动态拼接系统命令", "critical", "LLM05"),
    ],
    "path traversal": [
        (r"(?i)(\.\./){2,}|(%2e%2e%2f)",
         "路径遍历: 越权访问上级目录", "high", "LLM06"),
    ],
    "ssrf": [
        (r"(?i)(requests\.(get|post)|urllib\.request\.urlopen|fetch)\s*\(\s*[^)]*(user|input|param|req\.)",
         "SSRF: 请求目标来自不可信输入", "high", "LLM06"),
    ],
    "sandbox escape": [
        (r"(?i)(docker\.sock|/proc/self/|privileged\s*[:=]\s*true|--cap-add\s*=?\s*SYS_ADMIN)",
         "沙箱逃逸: 容器高危配置", "critical", "LLM05"),
    ],
    "session": [
        (r"(?i)(session|token)\s*[:=]\s*['\"][^'\"]{0,8}['\"]",
         "会话安全: 会话标识过短或硬编码", "high", "LLM07"),
    ],
    "origin": [
        (r"(?i)(Access-Control-Allow-Origin['\"]?\s*[:,]\s*['\"]\*|cors\s*\(\s*\)\s*)",
         "跨域校验缺失: 允许任意来源", "high", "LLM07"),
    ],
    "authentication": [
        (r"(?i)(auth(entication)?\s*[:=]\s*(False|None|null|0)\b|verify\s*=\s*False)",
         "认证绕过: 显式关闭校验", "critical", "LLM07"),
    ],
    "deserialization": [
        (r"(?i)(pickle\.loads|yaml\.load\s*\((?![^)]*Loader)|node-serialize)",
         "不安全反序列化", "critical", "LLM05"),
    ],
    "tool poisoning": [
        (r"(?i)(tool|function)[_\s]?(description|schema)\s*[:=].{0,80}(ignore|override|system\s+prompt)",
         "工具投毒: 工具描述中夹带指令", "critical", "LLM01"),
    ],
}

OWASP_MAP = {
    "LLM01": "提示注入 (Prompt Injection)",
    "LLM02": "敏感信息泄露 (Sensitive Information Disclosure)",
    "LLM03": "供应链漏洞 (Supply Chain)",
    "LLM04": "数据与模型投毒 (Data and Model Poisoning)",
    "LLM05": "不当输出处理 (Improper Output Handling)",
    "LLM06": "过度代理权限 (Excessive Agency)",
    "LLM07": "系统提示泄露 (System Prompt Leakage)",
    "LLM08": "向量与嵌入弱点 (Vector and Embedding Weaknesses)",
    "LLM09": "错误信息 (Misinformation)",
    "LLM10": "无限制消耗 (Unbounded Consumption)",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_intel() -> List[Dict[str, Any]]:
    if not THREAT_DB.exists():
        return []
    try:
        d = json.loads(THREAT_DB.read_text(encoding="utf-8"))
        return d.get("intel", []) if isinstance(d, dict) else d
    except Exception:
        return []


# --------------------------------------------------------------------------
# R1 漏洞包黑名单
# --------------------------------------------------------------------------
def build_package_blacklist(intel: List[Dict[str, Any]]) -> Dict[str, Any]:
    pkgs: Dict[str, Dict[str, Any]] = {}
    for i in intel:
        sev = (i.get("severity") or "").lower()
        if sev not in ("critical", "high"):
            continue
        aff = i.get("affected") or ""
        for token in re.split(r"[,\s]+", aff):
            if ":" not in token:
                continue
            eco, name = token.split(":", 1)
            eco, name = eco.strip().lower(), name.strip()
            if not name or len(name) > 120:
                continue
            key = f"{eco}:{name}"
            entry = pkgs.setdefault(
                key, {"ecosystem": eco, "package": name, "severity": sev, "advisories": []}
            )
            if i.get("id") and i["id"] not in entry["advisories"]:
                entry["advisories"].append(i["id"])
            if sev == "critical":
                entry["severity"] = "critical"
    return pkgs


# --------------------------------------------------------------------------
# R2 攻击模式规则
# --------------------------------------------------------------------------
def build_pattern_rules(intel: List[Dict[str, Any]]) -> Dict[str, Any]:
    hits: Dict[str, int] = defaultdict(int)
    evidence: Dict[str, List[str]] = defaultdict(list)

    for i in intel:
        text = ((i.get("title") or "") + " " + (i.get("summary") or "")).lower()
        for trigger in ATTACK_PATTERNS:
            if trigger in text:
                hits[trigger] += 1
                if i.get("id") and len(evidence[trigger]) < 5:
                    evidence[trigger].append(i["id"])

    rules: Dict[str, Any] = {}
    for trigger, count in hits.items():
        for pattern, desc, sev, owasp in ATTACK_PATTERNS[trigger]:
            rules[pattern] = {
                "description": desc,
                "severity": sev,
                "owasp": owasp,
                "owasp_name": OWASP_MAP.get(owasp, ""),
                "derived_from": trigger,
                "intel_hits": count,
                "evidence": evidence[trigger],
            }
    return rules


# --------------------------------------------------------------------------
# R3 OWASP 分布
# --------------------------------------------------------------------------
def build_owasp_distribution(rules: Dict[str, Any]) -> Dict[str, int]:
    dist: Dict[str, int] = defaultdict(int)
    for r in rules.values():
        dist[r["owasp"]] += 1
    return dict(dist)


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield 情报转规则引擎")
    ap.add_argument("--notify", action="store_true")
    args = ap.parse_args()

    intel = load_intel()
    if not intel:
        print("情报库为空，请先运行 scripts/fetch_vuln_feeds.py")
        return 0

    print(f"读取情报 {len(intel)} 条\n" + "=" * 60)

    blacklist = build_package_blacklist(intel)
    patterns = build_pattern_rules(intel)
    owasp_dist = build_owasp_distribution(patterns)

    prev_count = 0
    if OUT_RULES.exists():
        try:
            prev = json.loads(OUT_RULES.read_text(encoding="utf-8"))
            prev_count = len(prev.get("pattern_rules", {})) + len(prev.get("package_blacklist", {}))
        except Exception:
            pass

    out = {
        "generated_at": _now(),
        "source_intel_count": len(intel),
        "package_blacklist": blacklist,
        "pattern_rules": patterns,
        "owasp_distribution": owasp_dist,
        "total_rules": len(blacklist) + len(patterns),
    }
    OUT_RULES.parent.mkdir(parents=True, exist_ok=True)
    OUT_RULES.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"R1 漏洞包黑名单：{len(blacklist)} 个高危包")
    for k, v in list(blacklist.items())[:8]:
        print(f"   [{v['severity'].upper()}] {k}  ← {', '.join(v['advisories'][:2])}")
    print(f"\nR2 攻击模式规则：{len(patterns)} 条")
    for p, r in list(patterns.items())[:8]:
        print(f"   [{r['severity'].upper()}] {r['description']}  (情报命中 {r['intel_hits']} 次, {r['owasp']})")
    print(f"\nR3 OWASP 覆盖分布：{json.dumps(owasp_dist, ensure_ascii=False)}")
    print("=" * 60)
    delta = out["total_rules"] - prev_count
    print(f"规则总数 {out['total_rules']}（较上轮 {'+' if delta >= 0 else ''}{delta}）")
    print(f"已写出 {OUT_RULES.relative_to(REPO_ROOT)}，scanner 下次扫描即生效")

    try:
        from scripts.state_bus import StateBus

        StateBus().set(
            "rules",
            {
                "total": out["total_rules"],
                "package_blacklist": len(blacklist),
                "pattern_rules": len(patterns),
                "owasp_distribution": owasp_dist,
                "delta": delta,
                "last_run": _now(),
            },
            source="intel_to_rules",
        )
    except Exception as e:
        print(f"[warn] 状态回写失败: {e}")

    if args.notify and delta > 0:
        try:
            from scripts.notify import notify

            body = (
                f"情报转规则引擎本轮新增 **{delta}** 条检测规则（总计 {out['total_rules']} 条）。\n\n"
                f"- 漏洞包黑名单：{len(blacklist)} 个\n"
                f"- 攻击模式规则：{len(patterns)} 条\n"
                f"- OWASP 覆盖：{json.dumps(owasp_dist, ensure_ascii=False)}\n\n"
                f"> 数据飞轮闭合：情报采集 → 规则生成 → 检测能力提升 → 扫描结果更准。"
            )
            notify("P2", f"检测规则库更新 +{delta} 条", body, "rules-updated", cooldown_hours=48)
        except Exception as e:
            print(f"[warn] 通知失败: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
