# -*- coding: utf-8 -*-
"""
scripts/rses_cycle.py — 安全自进化闭环（蓝图 Program B · RSES）v0.1 编排层
============================================================================

蓝图定位（§3 Program B）
------------------------
把 L5 递归自改进「安全地关在笼子里」：元 agent 只能"建议规则"，不能改约束自身
的机制（ASI01/ASI10）。闭环：intel → draft(语义) → test(Hypothesis 留存集) →
promote/demote → reflect(FP/FN 记忆)。

本模块是 **编排层**，站在既有 `eco/meta_agent.py`（有界草拟元 agent）与
`eco/evolution_ledger.py`（哈希链问责账本）之上，提供：
  1. `RSSESCycle.run(signals)` —— 跑完整闭环：每个情报信号起草→自测→（ready 则）
     提交晋升审议；含 NSE 语义候选生成钩子位（蓝图 60 天接入真实 LLM 合成）。
  2. `RSSESCycle.self_audit()` —— 闭环不变量自检：
        * 草拟元 agent 不含任何特权方法（promote/demote/rollback…）；
        * 进化账本哈希链通过 verify_chain()；
        * 账本中无任何 `meta:` actor 执行过特权动作（双保险）。
  3. CLI 演示：用一条示例情报跑一遍闭环并自检。

设计纪律（与既有模块同源）
--------------------------
  * 晋升权永远在 `scripts/promote_rule.py` 的六道闸门 + --approved-by，本模块
    与元 agent 都**没有**晋升能力，结构隔离 + 账本门槛双重保险。
  * 零第三方依赖；情报源/扫描器/账本路径全部可注入，便于离线测试。

用法
----
  python scripts/rses_cycle.py            # 演示闭环
  python scripts/rses_cycle.py --audit    # 仅跑不变量自检
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

# 让脚本可直接运行（与既有 scripts/ 同模式）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eco.meta_agent import DraftingMetaAgent  # noqa: E402
from eco import evolution_ledger as ledger  # noqa: E402


# 示例情报：一条"假设已分析的"信号，带人工/LLM 预合成的候选规则规格。
# 真实链路（60 天）里这步由 NSE 语义探针 + LLM 合成，本 v0.1 用占位规格演示闭环。
SAMPLE_SIGNAL = {
    "signal_id": "intel-demo-001",
    "signal_title": "New prompt-injection variant via markdown link title",
    "signal_url": "https://example.com/advisories/INTEL-DEMO-001",
    "pattern": r'\[[^\]]*\]\([^)]*\)',  # 简化的 markdown 链接识别（演示用，非最终规则）
    "description": "Markdown 链接标题中可能隐藏间接提示注入（待人工复核语义）",
    "severity": "medium",
    "attack_category": "MCP06",
}


class RSSESCycle:
    """安全自进化闭环编排。默认用真实 `DraftingMetaAgent` + 真实账本路径；

    测试可注入 `proposals_dir` / `ledger_path` / `self_scan_fn` / `corpus_fn`
    以隔离真实数据。
    """

    def __init__(self, *, agent: DraftingMetaAgent | None = None,
                 proposals_dir: str | None = None, ledger_path: str | None = None,
                 self_scan_fn=None, corpus_fn=None):
        self.agent = agent or DraftingMetaAgent(
            proposals_dir=proposals_dir, ledger_path=ledger_path,
            self_scan_fn=self_scan_fn, corpus_fn=corpus_fn)
        self.ledger_path = (ledger_path or self.agent.ledger_path
                            or ledger.LEDGER_FILE)

    # ── 闭环主流程 ──
    def run(self, signals: list) -> dict:
        """对每个情报信号跑 propose → test →（ready 则）submit_for_promotion。

        返回 {processed, drafted, ready, submitted, rejected, details}。
        """
        summary = {"processed": 0, "drafted": 0, "ready": 0,
                   "submitted": 0, "rejected": 0, "details": []}
        for sig in signals:
            summary["processed"] += 1
            try:
                d = self.agent.propose_rule(
                    signal_id=sig["signal_id"], signal_title=sig["signal_title"],
                    signal_url=sig["signal_url"], pattern=sig["pattern"],
                    description=sig["description"], severity=sig["severity"],
                    attack_category=sig.get("attack_category"))
                summary["drafted"] += 1
                report = self.agent.test_draft(d["draft_path"])
                if report["verdict"] == "ready":
                    summary["ready"] += 1
                    res = self.agent.submit_for_promotion(d["draft_path"])
                    if res.get("ok"):
                        summary["submitted"] += 1
                        summary["details"].append(
                            {"signal": sig["signal_id"], "verdict": "ready",
                             "submitted": True,
                             "promote_command": res.get("promote_command")})
                    else:
                        summary["details"].append(
                            {"signal": sig["signal_id"], "verdict": "ready",
                             "submitted": False, "reason": res.get("reason")})
                else:
                    summary["rejected"] += 1
                    summary["details"].append(
                        {"signal": sig["signal_id"], "verdict": "rejected",
                         "reasons": report["reasons"]})
            except ValueError as e:
                # 起草期校验不过（模式过短/重复/非法）—— 这是预期内的安全拒绝
                summary["rejected"] += 1
                summary["details"].append(
                    {"signal": sig.get("signal_id"), "verdict": "draft_rejected",
                     "reason": str(e)})
        return summary

    # ── 闭环不变量自检 ──
    def self_audit(self) -> dict:
        """验证 RSES 的三道硬约束：无特权方法 + 账本链完整 + 元 agent 未越权。"""
        agent_cls = type(self.agent)
        forbidden = [m for m in agent_cls.FORBIDDEN_METHODS
                     if hasattr(agent_cls, m)]
        chain = ledger.verify_chain(self.ledger_path)
        # 账本里是否有 meta: actor 执行特权动作
        meta_privileged = []
        for e in ledger.list_entries(self.ledger_path):
            if (str(e.get("actor", "")).startswith(ledger.META_ACTOR_PREFIX)
                    and e.get("action") in ledger.PRIVILEGED_ACTIONS):
                meta_privileged.append(e.get("seq"))
        return {
            "forbidden_methods_absent": not forbidden,
            "forbidden_methods_found": forbidden,
            "ledger_chain_verified": chain["ok"],
            "ledger_entries": chain.get("entries"),
            "meta_agent_privileged_violations": meta_privileged,
            "meta_agent_cannot_promote": not hasattr(agent_cls, "promote")
                                         and not hasattr(agent_cls, "promote_rule"),
            "ok": (not forbidden and chain["ok"] and not meta_privileged),
        }


def _demo():
    tmp = tempfile.mkdtemp(prefix="rses_demo_")
    prop_dir = os.path.join(tmp, "proposed")
    lg_path = os.path.join(tmp, "evolution_ledger.jsonl")
    os.makedirs(prop_dir, exist_ok=True)
    cycle = RSSESCycle(proposals_dir=prop_dir, ledger_path=lg_path)
    print("=== RSES 闭环演示 ===")
    res = cycle.run([SAMPLE_SIGNAL])
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("\n=== 不变量自检 ===")
    audit = cycle.self_audit()
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0 if audit["ok"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AIShield RSES 安全自进化闭环 v0.1")
    ap.add_argument("--audit", action="store_true",
                    help="仅跑闭环不变量自检（不起草）")
    args = ap.parse_args(argv)
    if args.audit:
        cycle = RSSESCycle()
        audit = cycle.self_audit()
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        return 0 if audit["ok"] else 1
    return _demo()


if __name__ == "__main__":
    sys.exit(main())
