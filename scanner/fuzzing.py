"""
AIShield Fuzzing 模块 — 发现规则引擎未能覆盖的新攻击面

设计哲学:
    - 不运行被扫代码（绝不 spawn）
    - 对输入样本做结构化变异，观察规则引擎的"漏网"情况
    - 漏网 = 需要新规则的攻击模式
    - 完全本地运行，零网络依赖

用法:
    from scanner.fuzzing import fuzz, FuzzReport
    report = fuzz(mcp_config_text, max_mutations=50)
    print(report.new_vectors)   # 未被现有规则覆盖的新攻击向量
    print(report.coverage)      # 现有规则覆盖率
"""

from __future__ import annotations

import copy
import hashlib
import json
import random
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class FuzzVector:
    """一个变异攻击向量"""
    vector_id: str
    category: str  # encoding_evasion / structure_mutation / semantic_obfuscation
    description: str
    input_variant: str
    detected_by_existing_rules: bool
    findings: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FuzzReport:
    """Fuzzing 结果报告"""
    input_hash: str
    total_mutations: int
    detected_count: int
    undetected_count: int
    coverage_pct: float
    new_vectors: List[FuzzVector] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("new_vectors")
        d["new_vector_count"] = len(self.new_vectors)
        d["new_vector_categories"] = {}
        for v in self.new_vectors:
            cat = v.category
            d["new_vector_categories"][cat] = d["new_vector_categories"].get(cat, 0) + 1
        return d


# ── 变异策略 ──

# 编码逃逸：把已知触发词用不同编码包装
ENCODING_MUTATIONS = [
    (r"(\w+)", lambda m: "\\x" + "%02x" * len(m.group(1)) % tuple(ord(c) for c in m.group(1))),
    (r"(\w{3,})", lambda m: "\\" + " ".join(f"{ord(c):o}" for c in m.group(1))),
    (r"(\w{3,})", lambda m: "🅐" + m.group(1)[1:] if m.group(1)[0].isupper() else m.group(1)),
]

# 结构变异：打散 JSON/配置结构
STRUCTURE_MUTATIONS = [
    "inject_whitespace",
    "inject_comments",
    "reorder_keys",
    "split_value",
]

# 语义混淆：用近义词/缩写替换
SYNONYM_MAP = {
    "eval": ["evaluate", "exec_dynamic", "run_code", "process_expr"],
    "exec": ["execute", "run_dynamic", "process_command"],
    "shell": ["terminal", "console", "cmd_interface"],
    "password": ["passphrase", "secret_token", "credential"],
    "token": ["api_key", "secret", "access_key"],
    "inject": ["embed", "insert", "embed_payload"],
    "bypass": ["skip", "circumvent", "avoid"],
    "admin": ["superuser", "root_user", "privileged"],
}

# 已知触发词（用于编码逃逸）
TRIGGER_WORDS = [
    "eval(", "exec(", "shell(", "password", "token", "inject", "bypass",
    "admin", "rm -rf", "DROP TABLE", "SELECT.*FROM", "curl.*|.*sh",
    "fetch(", "axios(", "requests.get", "child_process", "subprocess",
]


def _hash_input(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]


def _apply_encoding_mutation(text: str, idx: int) -> str:
    """对随机触发词做编码逃逸"""
    word = random.choice(TRIGGER_WORDS)
    if word not in text:
        return None
    mutation = ENCODING_MUTATIONS[idx % len(ENCODING_MUTATIONS)]
    pattern, repl_fn = mutation
    def repl(m):
        if m.group(0).lower() == word.lower():
            return repl_fn(m)
        return m.group(0)
    return re.sub(pattern, repl, text, count=1, flags=re.IGNORECASE)


def _apply_structure_mutation(text: str, idx: int) -> str:
    """结构变异"""
    strategies = STRUCTURE_MUTATIONS[idx % len(STRUCTURE_MUTATIONS)]
    if strategies == "inject_whitespace":
        # 在关键字前插入不可见空白
        markers = ["\\n", "\\r\\n", "\\t"]
        return text.replace("\n", "\n" + random.choice(markers), 1) if "\n" in text else None
    elif strategies == "inject_comments":
        if "{" in text:
            return text.replace("{", "{ // fuzz-comment", 1)
        if "function" in text:
            return text.replace("function", "// @fuzz\nfunction", 1)
        return None
    elif strategies == "reorder_keys":
        if isinstance(text, str) and "{" in text and "}" in text:
            return None  # 简化：不重排 JSON，避免破坏结构
        return None
    elif strategies == "split_value":
        # 把长字符串拆成多段拼接
        for word in ["password", "token", "secret"]:
            if word in text:
                mid = len(word) // 2
                return text.replace(word, word[:mid] + ' + "' + word[mid:] + '"', 1)
        return None
    return None


def _apply_semantic_mutation(text: str, idx: int) -> str:
    """用近义词替换关键字"""
    words = list(SYNONYM_MAP.keys())
    word = words[idx % len(words)]
    if word not in text:
        return None
    synonyms = SYNONYM_MAP[word]
    alt = synonyms[idx % len(synonyms)]
    return text.replace(word, alt, 1)


def _run_rules(text: str) -> List[Dict[str, Any]]:
    """用现有规则引擎扫描输入"""
    try:
        from scanner.rules import OWASP_MCP_TOP10, SKILL_EXTRA_RULES
        all_rules = OWASP_MCP_TOP10 + SKILL_EXTRA_RULES
        findings = []
        for rule in all_rules:
            pattern = rule.get("pattern", "")
            if pattern and re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                findings.append({
                    "rule_id": rule.get("rule_id", "unknown"),
                    "severity": rule.get("severity", "medium"),
                })
        return findings
    except Exception:
        return []


def fuzz(
    input_text: str,
    max_mutations: int = 50,
    seed: Optional[int] = None,
) -> FuzzReport:
    """
    对输入文本执行 fuzzing。

    Args:
        input_text: 要 fuzz 的输入（MCP config / skill 目录 / prompt 等）
        max_mutations: 最大变异次数
        seed: 随机种子（可重复）

    Returns:
        FuzzReport
    """
    if seed is not None:
        random.seed(seed)

    in_hash = _hash_input(input_text)
    mutations: List[FuzzVector] = []

    for i in range(max_mutations):
        # 随机选一种变异策略
        strategy = random.choice(["encoding", "structure", "semantic"])
        variant = None

        if strategy == "encoding":
            variant = _apply_encoding_mutation(input_text, i)
        elif strategy == "structure":
            variant = _apply_structure_mutation(input_text, i)
        else:
            variant = _apply_semantic_mutation(input_text, i)

        if variant is None or variant == input_text:
            continue

        vector_id = hashlib.md5(variant.encode()).hexdigest()[:8]
        findings = _run_rules(variant)
        detected = len(findings) > 0

        mutations.append(FuzzVector(
            vector_id=vector_id,
            category=strategy,
            description=f"Mutation #{i}: {strategy} evasion",
            input_variant=variant[:500],
            detected_by_existing_rules=detected,
            findings=findings,
        ))

    detected_count = sum(1 for v in mutations if v.detected_by_existing_rules)
    undetected_count = sum(1 for v in mutations if not v.detected_by_existing_rules)
    total = detected_count + undetected_count or 1
    coverage = round(detected_count / total * 100, 1)

    new_vectors = [v for v in mutations if not v.detected_by_existing_rules]

    summary = (
        f"{total} 变异: {detected_count} 已检测 ({coverage}%) / "
        f"{undetected_count} 漏网 → {len(new_vectors)} 个新攻击向量"
    )

    return FuzzReport(
        input_hash=in_hash,
        total_mutations=len(mutations),
        detected_count=detected_count,
        undetected_count=undetected_count,
        coverage_pct=coverage,
        new_vectors=new_vectors,
        summary=summary,
    )
