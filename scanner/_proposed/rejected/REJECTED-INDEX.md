# 被拒候选索引（2026-09-03 分诊）

`tech_radar.py` 按关键词起草候选，无法区分攻击侧与防御侧，因此队列里长期混入
永远无法成为规则的条目。本次对全部 49 条做了显式处置：拒绝的移入本目录（**未删除，可逆**），
保留的留在 `scanner/_proposed/` 作为待撰写工作。

还原：`python scripts/triage_proposed.py --restore`

## 理由码

| 码 | 含义 |
|----|------|
| `R1-defense-side` | 防御侧工具/论文或刷仓仓库，无攻击面可提取为检测特征 |
| `R2-benchmark` | 评测/基准方法学，度量攻击而非攻击本身，无可提取 IOC |
| `R3-off-scope` | 与 MCP 配置 / skill / prompt 扫描无关 |
| `R4-capability` | 自进化 agent 能力论文被误标 trajectory-poisoning（是攻击前提，非攻击） |
| `R5-out-of-reach` | 真实攻击，但位于模型权重或非文本模态，文本/配置扫描器天然不可见 |
| `R6-covered` | 真实攻击，但已被现网规则覆盖，晋升只会产生重复规则 |

## 被拒条目（7）

| 文件 | 理由码 | 说明 |
|------|--------|------|
| `PROPOSED_20260911_understanding_in_context_multi_21ec74.json` | `R1-defense-side` | 后验重加权分析多模态越狱，机制可解释性防御侧研究 |
| `PROPOSED_20260909_vex_bench_benchmarking_llm_age_562d27.json` | `R2-benchmark` | VEX-Bench 供应链可利用性基准评测 |
| `PROPOSED_20260911_an_empirical_measurement_of_ja_6e63e0.json` | `R2-benchmark` | 越狱评估器经验度量方法学 |
| `PROPOSED_20260904_adapting_to_evolving_requireme_836249.json` | `R3-off-scope` | 零售供应链 agentic AI 运营论文，与 agent 安全无关 |
| `PROPOSED_20260915_monesgoda_offensive_agent_s_3d9082.json` | `R3-off-scope` | regex 匹配的是「LLM+红队」话题组合（.* 无界），非攻击 IOC；话题提及≠攻击特征 |
| `PROPOSED_20260909_closing_the_consistency_gap_se_bf2502.json` | `R4-capability` | 自进化 agent 能力论文（保持课程），被误标 trajectory-poisoning |
| `PROPOSED_20260915_agentq_quantization_conditione_37d6b4.json` | `R5-out-of-reach` | 量化级后门（AgentQ），注入位于模型权重层，配置/文本扫描器天然不可见 |

## 保留待撰写（17）

| 文件 | 为何值得写 |
|------|------------|
| `PROPOSED_20260811_toward_metacognitive_one_shot__281d17.json` | 单次间接注入的策略抽象，载荷形态可提取 |
| `PROPOSED_20260812_from_prompt_injection_to_web_e_33a86e.json` | critical：注入链到 Web 利用，需核对现网外传/端点规则是否已覆盖 |
| `PROPOSED_20260814_soulkyu_leandro_40aab1.json` | 标题无信息量，需实际读仓库后再定去留 |
| `PROPOSED_20260815_forbiddengarden_poisonvine_54c4b9.json` | mcp-attack，疑 MCP 投毒工具，最高优先级人工核查 |
| `PROPOSED_20260816_anonymous_beta_kaiju_625069.json` | mcp-attack，需读仓库确认载荷 |
| `PROPOSED_20260816_simimasai111_ai_jailbreak_prom_892d9e.json` | 越狱提示集合，可作为语料提取共性特征 |
| `PROPOSED_20260817_ikooky_jailbreak_kit_cd9771.json` | 越狱工具包，同上 |
| `PROPOSED_20260817_xer0_code_universal_ai_jailbre_73d74b.json` | 通用越狱合集，同上 |
| `PROPOSED_20260818_jailbreakskill_scaling_automat_4d95d0.json` | 以 skill 为载体的可复用越狱，正对 AIShield skill 扫描面 |
| `PROPOSED_20260820_selujuju_all_ai_jailbreaks_7c0f0f.json` | 越狱合集（与 0821 条疑似同源，可合并） |
| `PROPOSED_20260821_buryusu_all_ai_jailbreaks_d7d693.json` | 越狱合集（与 0820 条疑似同源，可合并） |
| `PROPOSED_20260825_psychjail_exploring_psychologi_51c9e7.json` | 多轮心理说服越狱，可提取话术特征 |
| `PROPOSED_20260904_context_inference_attacks_with_ec440e.json` | 上下文推断攻击（无越狱），非传统越狱路径，需读原文提取载荷特征 |
| `PROPOSED_20260907_repeat_after_me_black_box_adap_a653e9.json` | 视觉提示注入（黑盒自适应），多模态注入新形态，需读原文提取 |
| `PROPOSED_20260907_rethinking_indirect_prompt_inj_018b34.json` | 间接提示注入重思（测试时搜索），注入新攻击面，需核对现网规则覆盖 |
| `PROPOSED_20260909_google_attackers_are_using_pro_741530.json` | Google 报告：攻击者针对 coding agent 的提示注入，产业级信号 |
| `PROPOSED_20260910_an_experimental_evaluation_of__529f3b.json` | 多模态提示注入在 agentic AI 上的实验评估，攻击面直接对应 MCP/agent |
