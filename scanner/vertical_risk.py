"""
scanner/vertical_risk.py — 垂直场景风险词审查（金融 / 医疗 / 政企）

借鉴赛道一 **FinFlux「金融语义准入与受控演化引擎」** 的垂直场景治理思路：
通用安全规则（OWASP）之外，针对高敏感垂直行业，加一层"语义准入"——
识别金融欺诈诱导、医疗虚假诊断、政企敏感议题等高风险内容模式。

与 banned_words（中文平台内容审核）的区别：
  banned_words 面向"内容平台合规"（赌博/色情等）；
  vertical_risk 面向"Agent 安全语义"——防止 Agent 在垂直场景里
  输出未经授权/高风险的建议，属于 Agentic 安全平面的一部分。

零第三方依赖（仅标准库）。词表为可审计的内置基线，可经 attestation 持续修订。
"""
from __future__ import annotations

import re

# ── 金融：欺诈诱导 / 无牌理财 / 资金盘 / 代客理财 ──
FINANCE_RISK_TERMS = [
    "稳赚不赔", "保本保息", "年化收益", "内部筹码", "庄家拉升", "杀猪盘",
    "资金盘", "传销币", "代客理财", "无风险高回报", "配资杠杆", "原始股内幕",
    "带单老师", "喊单", "拉盘", "割韭菜", "保本理财", "稳赚",
]

# ── 医疗：无资质诊断 / 虚假疗效 / 违禁用药建议 ──
MEDICAL_RISK_TERMS = [
    "包治百病", "根治癌症", "祖传秘方", "百分百治愈", "不用吃药", "停用西药",
    "特效神药", "一针见效", "包你怀上", "保证转阴", "纯中药无副作用",
    "自家偏方治糖尿病", "替代放化疗", "治愈艾滋病",
]

# ── 政企：敏感议题 / 越权披露 / 内部信息外泄 ──
GOV_RISK_TERMS = [
    "内部文件泄露", "涉密资料", "未公开政策", "替你抹掉记录", "篡改档案",
    "绕过审批", "伪造公文", "代写举报信", "攻击政府网站", "煽动聚集",
]

DOMAINS = {
    "finance": FINANCE_RISK_TERMS,
    "medical": MEDICAL_RISK_TERMS,
    "gov": GOV_RISK_TERMS,
}

DOMAIN_LABELS = {
    "finance": "金融语义准入",
    "medical": "医疗安全语义",
    "gov": "政企敏感议题",
}


def scan_vertical_risk(text, domain="finance"):
    """扫描文本在指定垂直场景下的风险词。

    返回：
      {
        "domain": "finance",
        "domain_label": "金融语义准入",
        "safe": bool,
        "risk_level": "high" | "medium" | "low" | "none",
        "found": [{"term", "position", "context"}],
        "recommendation": str,
      }
    """
    if domain not in DOMAINS:
        return {"error": f"未知垂直域: {domain}", "available": list(DOMAINS)}
    text = text or ""
    terms = DOMAINS[domain]
    found = []
    for term in terms:
        idx = text.find(term)
        while idx != -1:
            ctx_start = max(0, idx - 12)
            ctx_end = min(len(text), idx + len(term) + 12)
            found.append({
                "term": term,
                "position": idx,
                "context": text[ctx_start:ctx_end],
            })
            idx = text.find(term, idx + len(term))

    n = len(found)
    if n == 0:
        risk_level = "none"
    elif n >= 3:
        risk_level = "high"
    elif n == 2:
        risk_level = "medium"
    else:
        risk_level = "low"

    recommendation = {
        "high": "高风险：命中多项垂直场景敏感表述，禁止 Agent 直接输出，需人工复核或拒绝。",
        "medium": "中风险：存在垂直场景敏感表述，建议加人工确认环。",
        "low": "低风险：命中单项敏感词，建议记录并提示。",
        "none": "未命中垂直场景风险词。",
    }[risk_level]

    return {
        "domain": domain,
        "domain_label": DOMAIN_LABELS[domain],
        "safe": n == 0,
        "risk_level": risk_level,
        "found_count": n,
        "found": found,
        "recommendation": recommendation,
    }


def scan_all_domains(text):
    """一次性扫描三个垂直域，返回汇总。"""
    out = {}
    for d in DOMAINS:
        out[d] = scan_vertical_risk(text, d)
    blocking = [d for d, r in out.items() if not r.get("safe")]
    return {
        "safe": len(blocking) == 0,
        "blocking_domains": blocking,
        "per_domain": out,
    }


if __name__ == "__main__":
    t = "这个庄家拉升的币稳赚不赔，跟我代客理财保本保息"
    print("finance:", scan_vertical_risk(t, "finance")["risk_level"])
    print("all:", scan_all_domains(t)["blocking_domains"])
