#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield · Proposed-Candidate Triage
====================================

`scripts/tech_radar.py` drafts a candidate for every high-severity signal it
sees. It matches on keywords only, so it cannot tell an *attack* from a
*defense* -- a paper called "Shielding against Prompt Injection" and a repo
called "prompt-injection-firewall-skill" both get drafted as if they were
threats. The result: `scanner/_proposed/` fills with candidates that can never
become a rule, and the real ones drown in them.

This tool closes the queue. Every candidate gets an explicit disposition:

  reject  -> moved to scanner/_proposed/rejected/ with a machine-readable
             reason. Reversible: nothing is deleted.
  keep    -> stays in the queue as outstanding authoring work.

Reason codes
------------
  R1-defense-side   Defensive tool/paper, or a repo-spam listing. No attack
                    surface to express as a detection pattern.
  R2-benchmark      Evaluation/benchmark methodology. Measures attacks, is not
                    one; yields no indicator of compromise.
  R3-off-scope      Unrelated to MCP config / skill / prompt scanning.
  R4-capability     Self-evolving-agent capability paper mis-labelled as
                    trajectory-poisoning. The capability is the precondition
                    for the attack, not the attack.
  R5-out-of-reach   Real attack, but lives in model weights or a non-text
                    modality. Invisible to a config/text scanner by design.
  R6-covered        Real attack, already covered by live rules. Promoting it
                    would only add a duplicate.

Usage:
  python scripts/triage_proposed.py --plan     # show disposition, change nothing
  python scripts/triage_proposed.py --apply    # move rejects, write index
  python scripts/triage_proposed.py --restore  # undo: move everything back
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROPOSED = os.path.join(ROOT, "scanner", "_proposed")
REJECTED = os.path.join(PROPOSED, "rejected")

REASONS = {
    "R1-defense-side": "防御侧工具/论文或刷仓仓库，无攻击面可提取为检测特征",
    "R2-benchmark": "评测/基准方法学，度量攻击而非攻击本身，无可提取 IOC",
    "R3-off-scope": "与 MCP 配置 / skill / prompt 扫描无关",
    "R4-capability": "自进化 agent 能力论文被误标 trajectory-poisoning（是攻击前提，非攻击）",
    "R5-out-of-reach": "真实攻击，但位于模型权重或非文本模态，文本/配置扫描器天然不可见",
    "R6-covered": "真实攻击，但已被现网规则覆盖，晋升只会产生重复规则",
}

# basename -> (reason_code, note)
DISPOSITION = {
    # ---- R1 defense-side / repo spam -------------------------------------
    "PROPOSED_20260810_sentry_llm_sentryllm_570fbd.json":
        ("R1-defense-side", "SentryLLM 是注入防护哨兵，防御侧"),
    "PROPOSED_20260811_basis_breach_aware_selective_p_4b3e4c.json":
        ("R1-defense-side", "BASIS 是 Shielding 防护机制，防御侧"),
    "PROPOSED_20260811_the_anatomy_of_a_prompt_inject_bc25ec.json":
        ("R1-defense-side", "结构化分析框架，无具体载荷特征"),
    "PROPOSED_20260812_eskuratov_agent_security_paper_c94e24.json":
        ("R1-defense-side", "论文清单仓，无攻击载荷"),
    "PROPOSED_20260817_maludb_ed_skill_safety_checker_e2ce7a.json":
        ("R1-defense-side", "skill 安全检查器，与 AIShield 同类防御工具"),
    "PROPOSED_20260818_alphaparkinc_genpark_llm_promp_2c4904.json":
        ("R1-defense-side", "genpark-* 刷仓；firewall skill 属防御侧"),
    "PROPOSED_20260824_alphaparkinc_genpark_prompt_in_638ede.json":
        ("R1-defense-side", "genpark-* 刷仓；vulnerability scanner 属防御侧"),
    "PROPOSED_20260825_breaking_the_assumptions_1518ab.json":
        ("R1-defense-side", "审计越狱防御的假设，防御侧"),
    "PROPOSED_20260825_breaking_the_assumptions_audit_1518ab.json":
        ("R1-defense-side", "审计越狱防御的假设，防御侧"),
    "PROPOSED_20260827_pie_script_llm_agent_testbed_bc3012.json":
        ("R1-defense-side", "测试床，无攻击载荷"),
    "PROPOSED_20260901_circuit_discovery_helps_detect_2b15b7.json":
        ("R1-defense-side", "机制可解释性用于检测越狱，防御侧"),
    "PROPOSED_20260901_rope_routed_origin_policy_enfo_58a0a8.json":
        ("R1-defense-side", "ROPE 是来源策略强制执行，防御侧（曾误判 critical）"),
    "PROPOSED_20260902_alphaparkinc_genpark_prompt_in_ca33e6.json":
        ("R1-defense-side", "genpark-* 刷仓；firewall sentinel 属防御侧"),
    "PROPOSED_20260902_alphaparkinc_genpark_distribut_31fc1a.json":
        ("R1-defense-side", "genpark-* 刷仓；混沌延迟压测器被误标 skill-poisoning"),
    # ---- R2 benchmark / methodology --------------------------------------
    "PROPOSED_20260811_measuring_the_wrong_thing_inte_77f8d3.json":
        ("R2-benchmark", "有害性评分度量方法学"),
    "PROPOSED_20260812_redagentbench_executable_red_t_bc74c7.json":
        ("R2-benchmark", "红队基准测试集"),
    "PROPOSED_20260818_security_assessment_of_deepsee_1afad2.json":
        ("R2-benchmark", "安全性评估报告，无载荷特征"),
    "PROPOSED_20260819_fair_asr_re_evaluating_black_b_287671.json":
        ("R2-benchmark", "ASR 指标公平性重评估"),
    "PROPOSED_20260828_redevoagent_automatic_red_team_ccaf13.json":
        ("R2-benchmark", "红队 agent 框架，无配置层可见特征"),
    # ---- R3 off-scope ----------------------------------------------------
    "PROPOSED_20260811_gap_claudeconfig_v2w3x4.json":
        ("R3-off-scope", "普通 claude 配置仓"),
    "PROPOSED_20260811_gap_clinical_fp_e1f2g3.json":
        ("R3-off-scope", "临床研究诚信评估，与 agent 安全无关"),
    "PROPOSED_20260811_gap_cyberforge_b8c9d0.json":
        ("R3-off-scope", "代码仓漏洞注入，非 agent 配置面"),
    "PROPOSED_20260811_gap_llmfuzz_y5z6a7.json":
        ("R3-off-scope", "JS 引擎 fuzzing，非 agent 配置面"),
    "PROPOSED_20260811_gap_mobhunt_s9t0u1.json":
        ("R3-off-scope", "移动端漏洞猎取工具"),
    "PROPOSED_20260811_gap_smartcontract_p6q7r8.json":
        ("R3-off-scope", "智能合约审计器"),
    "PROPOSED_20260818_magian1127_deepseek_harness_zh_e553c8.json":
        ("R3-off-scope", "中文 harness 移植，无攻击面"),
    # ---- R4 capability mis-labelled --------------------------------------
    "PROPOSED_20260810_skillprox_self_evolving_agent__e09b7d.json":
        ("R4-capability", "自进化 skill 优化方法"),
    "PROPOSED_20260812_geoforge_non_parametric_self_e_ee1c69.json":
        ("R4-capability", "对地观测自进化 agent"),
    "PROPOSED_20260812_mega_self_evolving_agent_optim_0c3b10.json":
        ("R4-capability", "自进化 agent 优化基础设施"),
    "PROPOSED_20260812_skillzip_evaluation_free_skill_58eea1.json":
        ("R4-capability", "skill 压缩方法"),
    # ---- R5 out of reach of a text scanner -------------------------------
    "PROPOSED_20260901_fully_unleashing_the_multimoda_07671b.json":
        ("R5-out-of-reach", "视觉语言模型多模态越狱，图像模态"),
    "PROPOSED_20260902_jailbreaking_text_to_image_mod_e6b965.json":
        ("R5-out-of-reach", "文生图模型越狱，与 MCP/skill 配置无关"),
    "PROPOSED_20260902_akrasia_stealthy_backdoor_atta_199ab5.json":
        ("R5-out-of-reach", "权重级推理后门，配置层不可见"),
    # ---- R6 already covered by live rules --------------------------------
    "PROPOSED_20260823_shoebpate1_ai_agent_hacking_wr_291c3b.json":
        ("R6-covered", "writeup 合集；记忆投毒面已有 4 条现网规则覆盖"),
    "PROPOSED_20260824_utility_under_attack_agent_mem_d4c9b0.json":
        ("R6-covered", "记忆投毒；已被雷达『轨迹投毒』+『持久载体』规则覆盖"),
    "PROPOSED_20260825_injecmem_memory_injection_atta_71422a.json":
        ("R6-covered", "记忆注入；同上，且静态规则已覆盖 memory.upsert/insert 写入"),
    "PROPOSED_20260902_transferable_end_to_end_optimi_a0a0d2.json":
        ("R6-covered", "长期记忆投毒；同上，为该类第 4 条重复草稿"),
    # ---- 2026-09-26 第二轮分诊（shadow catch=0 且 regex 不合规） ---------
    "PROPOSED_20260915_agentq_quantization_conditione_37d6b4.json":
        ("R5-out-of-reach", "量化级后门（AgentQ），注入位于模型权重层，配置/文本扫描器天然不可见"),
    "PROPOSED_20260915_monesgoda_offensive_agent_s_3d9082.json":
        ("R3-off-scope", "regex 匹配的是「LLM+红队」话题组合（.* 无界），非攻击 IOC；话题提及≠攻击特征"),
    # ---- 20260904–20260911 批次分诊 ---------------------------------------
    "PROPOSED_20260904_adapting_to_evolving_requireme_836249.json":
        ("R3-off-scope", "零售供应链 agentic AI 运营论文，与 agent 安全无关"),
    "PROPOSED_20260909_closing_the_consistency_gap_se_bf2502.json":
        ("R4-capability", "自进化 agent 能力论文（保持课程），被误标 trajectory-poisoning"),
    "PROPOSED_20260909_vex_bench_benchmarking_llm_age_562d27.json":
        ("R2-benchmark", "VEX-Bench 供应链可利用性基准评测"),
    "PROPOSED_20260911_an_empirical_measurement_of_ja_6e63e0.json":
        ("R2-benchmark", "越狱评估器经验度量方法学"),
    "PROPOSED_20260911_understanding_in_context_multi_21ec74.json":
        ("R1-defense-side", "后验重加权分析多模态越狱，机制可解释性防御侧研究"),
}

# Candidates deliberately kept in the queue, with why they are worth authoring.
KEEP_NOTES = {
    "PROPOSED_20260811_toward_metacognitive_one_shot__281d17.json":
        "单次间接注入的策略抽象，载荷形态可提取",
    "PROPOSED_20260812_from_prompt_injection_to_web_e_33a86e.json":
        "critical：注入链到 Web 利用，需核对现网外传/端点规则是否已覆盖",
    "PROPOSED_20260814_soulkyu_leandro_40aab1.json":
        "标题无信息量，需实际读仓库后再定去留",
    "PROPOSED_20260815_forbiddengarden_poisonvine_54c4b9.json":
        "mcp-attack，疑 MCP 投毒工具，最高优先级人工核查",
    "PROPOSED_20260816_anonymous_beta_kaiju_625069.json":
        "mcp-attack，需读仓库确认载荷",
    "PROPOSED_20260816_simimasai111_ai_jailbreak_prom_892d9e.json":
        "越狱提示集合，可作为语料提取共性特征",
    "PROPOSED_20260817_ikooky_jailbreak_kit_cd9771.json":
        "越狱工具包，同上",
    "PROPOSED_20260817_xer0_code_universal_ai_jailbre_73d74b.json":
        "通用越狱合集，同上",
    "PROPOSED_20260818_jailbreakskill_scaling_automat_4d95d0.json":
        "以 skill 为载体的可复用越狱，正对 AIShield skill 扫描面",
    "PROPOSED_20260820_selujuju_all_ai_jailbreaks_7c0f0f.json":
        "越狱合集（与 0821 条疑似同源，可合并）",
    "PROPOSED_20260821_buryusu_all_ai_jailbreaks_d7d693.json":
        "越狱合集（与 0820 条疑似同源，可合并）",
    "PROPOSED_20260825_psychjail_exploring_psychologi_51c9e7.json":
        "多轮心理说服越狱，可提取话术特征",
    "PROPOSED_20260825_skillbloat_token_amplification_6aac90.json":
        "已授权真实 regex：skill 注入型 token 放大，现网无同类覆盖",
    # ---- 20260904–20260911 批次保留（真实攻击，需撰写 regex）--------------
    "PROPOSED_20260904_context_inference_attacks_with_ec440e.json":
        "上下文推断攻击（无越狱），非传统越狱路径，需读原文提取载荷特征",
    "PROPOSED_20260907_repeat_after_me_black_box_adap_a653e9.json":
        "视觉提示注入（黑盒自适应），多模态注入新形态，需读原文提取",
    "PROPOSED_20260907_rethinking_indirect_prompt_inj_018b34.json":
        "间接提示注入重思（测试时搜索），注入新攻击面，需核对现网规则覆盖",
    "PROPOSED_20260909_google_attackers_are_using_pro_741530.json":
        "Google 报告：攻击者针对 coding agent 的提示注入，产业级信号",
    "PROPOSED_20260910_an_experimental_evaluation_of__529f3b.json":
        "多模态提示注入在 agentic AI 上的实验评估，攻击面直接对应 MCP/agent",
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def candidates(directory):
    if not os.path.isdir(directory):
        return []
    return sorted(
        os.path.join(directory, n)
        for n in os.listdir(directory)
        if n.startswith("PROPOSED_") and n.endswith(".json")
    )


def cmd_plan(apply_changes=False):
    files = candidates(PROPOSED)
    if not files:
        print("no candidates in scanner/_proposed/")
        return 0

    rejects, keeps, unknown = [], [], []
    for path in files:
        base = os.path.basename(path)
        if base in DISPOSITION:
            rejects.append((path,) + DISPOSITION[base])
        elif base in KEEP_NOTES:
            keeps.append((path, KEEP_NOTES[base]))
        else:
            unknown.append(path)

    print(f"candidates: {len(files)}  reject: {len(rejects)}  "
          f"keep: {len(keeps)}  unclassified: {len(unknown)}")

    by_reason = {}
    for path, code, note in rejects:
        by_reason.setdefault(code, []).append((os.path.basename(path), note))
    for code in sorted(by_reason):
        print(f"\n{code}  ({REASONS[code]})")
        for base, note in by_reason[code]:
            print(f"  - {base}\n      {note}")

    print("\nKEEP (outstanding authoring work):")
    for path, note in keeps:
        print(f"  . {os.path.basename(path)}\n      {note}")

    if unknown:
        print("\nUNCLASSIFIED -- triage map is stale, add these:")
        for path in unknown:
            print(f"  ? {os.path.basename(path)}")

    if not apply_changes:
        print("\n(plan only -- nothing moved; rerun with --apply)")
        return 1 if unknown else 0

    os.makedirs(REJECTED, exist_ok=True)
    moved = 0
    for path, code, note in rejects:
        data = load(path)
        data["status"] = "rejected"
        data["rejected_at"] = "2026-09-03"
        data["reject_reason"] = code
        data["review_notes"] = f"{REASONS[code]}｜{note}"
        dest = os.path.join(REJECTED, os.path.basename(path))
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.remove(path)
        moved += 1

    write_index(rejects, keeps)
    print(f"\nmoved {moved} candidate(s) -> scanner/_proposed/rejected/")
    print(f"queue now holds {len(candidates(PROPOSED))} outstanding candidate(s)")
    return 1 if unknown else 0


def write_index(rejects, keeps):
    lines = [
        "# 被拒候选索引（2026-09-03 分诊）",
        "",
        "`tech_radar.py` 按关键词起草候选，无法区分攻击侧与防御侧，因此队列里长期混入",
        "永远无法成为规则的条目。本次对全部 49 条做了显式处置：拒绝的移入本目录（**未删除，可逆**），",
        "保留的留在 `scanner/_proposed/` 作为待撰写工作。",
        "",
        "还原：`python scripts/triage_proposed.py --restore`",
        "",
        "## 理由码",
        "",
        "| 码 | 含义 |",
        "|----|------|",
    ]
    for code, text in REASONS.items():
        lines.append(f"| `{code}` | {text} |")
    lines += ["", f"## 被拒条目（{len(rejects)}）", "",
              "| 文件 | 理由码 | 说明 |", "|------|--------|------|"]
    for path, code, note in sorted(rejects, key=lambda r: r[1]):
        lines.append(f"| `{os.path.basename(path)}` | `{code}` | {note} |")
    lines += ["", f"## 保留待撰写（{len(keeps)}）", "",
              "| 文件 | 为何值得写 |", "|------|------------|"]
    for path, note in keeps:
        lines.append(f"| `{os.path.basename(path)}` | {note} |")
    lines.append("")
    with open(os.path.join(REJECTED, "REJECTED-INDEX.md"), "w",
               encoding="utf-8") as f:
        f.write("\n".join(lines))


def cmd_restore():
    files = candidates(REJECTED)
    if not files:
        print("nothing to restore")
        return 0
    for path in files:
        shutil.move(path, os.path.join(PROPOSED, os.path.basename(path)))
    print(f"restored {len(files)} candidate(s) -> scanner/_proposed/")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Triage proposed rule candidates")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", action="store_true", help="Show disposition only")
    g.add_argument("--apply", action="store_true", help="Move rejects, write index")
    g.add_argument("--restore", action="store_true", help="Undo --apply")
    args = ap.parse_args()

    if args.plan:
        return cmd_plan(apply_changes=False)
    if args.apply:
        return cmd_plan(apply_changes=True)
    if args.restore:
        return cmd_restore()
    return 0


if __name__ == "__main__":
    sys.exit(main())
