# AIShield 科学性评估与 SCI 可行性报告

> 评估日期：2026-10-18 · 评估方式：实跑验证（非旧结论）+ 代码/资产核查
> 评估口径：以"能否支撑一篇经同行评审的 SCI/CCF-A 级安全论文"为标尺

---

## 0. 一句话结论

AIShield 已经从"架构 + 营销文档"阶段，**实质性地长出了可信的科学资产**——可复现基准（我实跑通过：57/57 召回、0 误报）、机器可检验的隔离不变量（形式化 + 变异测试"判别力自证"）、以及 RSI-L5→ASI 威胁建模（含一个真实被修复的检测缺陷）。

它**还不是一篇可直接投的 SCI 论文**，但内部已经孵化出 **2–3 个可发表的"种子"**，其中「离线 + 形式化可验 + 神经-符号零误报」这一组合在 Agent 安全品类里是**稀缺的**。要达标，最短路径是补三件事：**外部/独立语料、与 ≥3 个基线的公开对比、形式化从"模拟"升级为"穷举或完备性论证"**。

---

## 1. 我实地验证了什么（避免空谈）

| 资产 | 验证命令 | 实跑结果 |
|---|---|---|
| 可复现基准 v1 | `python scripts/benchmark.py` | 57 正样本→57 检出（**召回 100.0%**）；45 负样本→**0 误报（0.0%）**；Agent Memory 面 4/4、0 误报；真实 harness 6 文件、7 findings。**确定性、零网络、零第三方依赖** |
| 形式化隔离不变量门禁 | `python scripts/run_fvi_gate.py` | **PASS**：有界模型检查穷举 64 态、0 反例；**变异测试抓出 step_buggy_leak（EXEC 泄漏）与 step_buggy_multiwriter（单写者破坏）**；B4 隔离自检退出码 0 |
| 基准 v1.md 与实跑一致性 | 比对 | 实跑数字（57/57、45/0）已优于提交的 v1.md（50/46、45/0），语料在 v1.md 生成后被扩充；应以实跑为准 |

> 关键诚信点：形式化门禁自带"判别力自证"——往模型里注入两个缺陷变体，验证器**必须**抓到，否则门禁失败。这排除了"检查器恒真=假绿"这一学术界最警惕的漏洞。

---

## 2. 科学性优势（这是真东西）

1. **可复现性达到论文级**：固定语料（单一真源 `rule_corpus.py`）、确定性扫描、零网络、零依赖、可第三方复跑，且带 CI 门禁（`--fail-under-recall` / `--fail-over-fp`）。这是安全/系统顶会最看重的"artifact"底座。
2. **形式化方法真实落地**：Quint 规格 + Python 有界模型检查（`check_isolation_invariants.py`，语义等价重述）+ Hypothesis 属性测试 + 固定语料回归，三层防线互相兜底；诚实声明边界（随机模拟非穷举，待装 Apalache）。这是"可证明安全"的工程近似，远胜大多数"我们很安全"的口头声明。
3. **基准方法论有巧思**：参数化变体（同一攻击意图换"表面形态"再测，检验规则是否只记单词不识意图）、两套口径（`serious_only` 召回 vs `any_finding` 覆盖）各自内部一致、公开"检出缺口"清单（把"没覆盖哪"变成可核对清单而非藏起来）。
4. **科学诚信罕见**：`docs/benchmark-report.md` **主动撤回**了早期"100%/460"等不可复现数字，指向规范基准。这种 errata 行为在学术评审中是加分项。
5. **威胁建模有真实发现**：`rsi-asi-mapping.md` 把 Theseus RSI 五级自主权映射到 OWASP Agentic，并**发现并修复了一个真实缺陷**——L5 信号（"递归改进护栏机制"）会被 R4-capability 过滤器当成良性能力研究而永久抑制。
6. **神经-符号架构有纪律**：`neuro_symbolic_probe.py` v0.1 落地——符号层当"宪法"（零误报铁律），神经层只产候选、经 `ratify()` 桥接、**永不自升级**为结论。设计上从根上堵住"LLM 误报污染门禁"。

---

## 3. 科学性短板 / 与 SCI 门槛的差距（诚实）

| # | 差距 | 为什么卡 SCI | 现状 |
|---|---|---|---|
| G1 | **语料规模小且自我精选** | 57+45 样本远低于安全/系统论文可接受的下限；且语料与规则**同步迭代调优**（基准脚本注释自承修了评分歧视度、启动器轴重标、剔除描述性样本）。审稿人会质疑"是在测攻击，还是测自己定义的攻击" | 自精选、已调优 |
| G2 | **缺外部基线对比** | 唯一对比（mcp-audit/Sunglasses 78%/65%）已在报告里被**自己撤回**为不可复现。SCI 必须有 ≥3 个基线在**同一固定语料**上的 precision/recall/F1 对照 | 缺失 |
| G3 | **形式化是模拟非穷举** | "200 轨迹×16 步"是随机模拟，不是模型检查（穷举需 Apalache/Java，列为 TODO）。结论缺"覆盖全部可达状态"的完备性论证 | 模拟级 |
| G4 | **无统计显著性与置信区间** | 100%/0% 在 57+45 样本上没有 CI；审稿人必然要求 bootstrap 置信区间，而那会暴露数字并非"绝对" | 无 CI |
| G5 | **缺独立/第三方验证** | "真实项目面"仅 6 个文件；没有外部实验室复现、没有公开数据集被社区采用 | 自测 |
| G6 | **单一贡献不尖锐** | 项目把"离线扫描器 + 双维分类 + 形式化 + 自进化雷达 + 神经符号 + RSI 分类"全打包，读起来像系统介绍，缺一个可被一句话概括的**核心贡献**与清晰的 related-work 站位 | 需聚焦 |

> 特别提醒：`benchmarks/run_bench.py`（二级 D2 基准）第 82–88 行 `expect_typosquat` 分支是**死代码**（`pass`，从不校验 typosquat）。它不影响规范基准 `scripts/benchmark.py`，但引用时务必以规范基准为准，并修掉这个死分支。

---

## 4. SCI 可行性：三个可发表的"种子"

### 种子 A（系统/安全，最推荐，最强）★ 主航道
**题目方向**：*An Offline, Zero-Dependency, Machine-Verifiable Framework for Agentic-AI Supply-Chain & Prompt-Injection Threat Detection*
- 贡献组合（稀缺）：可复现双平面基准（含表面形态参数化）+ 形式化隔离不变量（含变异测试判别力证明）+ 神经-符号零误报桥接。
- 目标 venue：USENIX Security / NDSS / ACSAC / IEEE TIFS；或上述会议的 tool/artifact 论文。
- 关键差距：补 G1（外部语料 10–50×）、G2（≥3 基线同语料对比）、G3（形式化升级）、G4（CI）。

### 种子 B（分类/立场，偏框架）
**题目方向**：*From Recursive Self-Improvement to Agentic Threat Modeling: A Five-Level Autonomy Risk Taxonomy (RSI-L5 → OWASP Agentic ASI)*
- 贡献：把 Theseus RSI 五级映射到可分类/可晋升的检测类别，并给出"L5 信号被能力过滤器抑制"这一实证发现。
- 目标 venue：IEEE S&P Workshop / USEC / Computers & Security。
- 短板：实证较轻，需配一个定量实验（如：在 N 篇 agent 论文/仓库上验证该分类的召回）。

### 种子 C（形式化/PL，小众但硬）
**题目方向**：*Machine-Checkable Safety Invariants for Agent Scanners: A Bounded-Model-Checking Approach with Discrimination Proof*
- 贡献：Quint + Python BMC + Hypothesis 三层防线，以及"变异测试证明检查器非恒真"的方法论。
- 目标 venue：CAV/FM/ASE 的 tool 论文，或形式化 workshop。
- 短板：需把"模拟"补成"穷举"或给出完备性论证，否则只能投 tool 类。

**建议**：以**种子 A 为旗舰**（它同时含实证复现 + 形式化 + 神经符号，组合最罕见），把种子 B 的分类贡献作为其中一节。种子 C 可独立投 tool 论文。

---

## 5. 达到"可投稿"的待办清单（按投入产出排序）

1. **外部/独立语料（最高优先级，破 G1/G5）**：引入 GitHub Advisory、真实恶意 MCP server 仓库、公开 prompt-injection 数据集（如 PJB，但需固定语料而非一次性跑），规模扩到数百–数千，并做标注者间一致性（IAA）。这是消除"自精选 100%"红 flags 的唯一办法。
2. **公开基线对比（破 G2）**：在同一固定语料上跑 mcp-audit、Invariant mcp-scan、agent-security-scanner-mcp、Snyk agent-scan，报告 precision/recall/F1 + bootstrap 置信区间。
3. **形式化升级（破 G3）**：装 Java + Apalache 跑 `quint verify` 做有界穷举，或给出状态空间规模与覆盖论证；把单写者（E13）等更多不变量进模型。
4. **尖锐化单一贡献 + related-work（破 G6）**：用一句话定义核心贡献；系统对比 Invariant、Snyk、Lakera/Gandalf、OWASP Agentic Top 10、NIST AI RMF，明确差异化。
5. **可复现性包（artifact）**：Dockerfile + 固定语料 + 一键复跑脚本。多数安全顶会现在强制 artifact evaluation。
6. **修二级基准死分支（G6 备注）**：`benchmarks/run_bench.py` 的 `expect_typosquat` 死代码删除或补真实校验。

---

## 6. 总结判断

- **科学性**：在同类"做工具"的开源项目里属于**第一梯队**——它把"可复现基准 + 形式化验证 + 神经符号零误报纪律 + 威胁建模发现"四个通常分散在多篇论文里的要素，集成进了一个工程系统，且**我实跑验证了核心数字与证明**。
- **SCI 可能性**：**有，但需 1 个主航道论文 + 3–6 个月打磨**。当前最大障碍不是"没东西"，而是"东西还没被外部语料和基线对比撑住"。只要补上外部语料与公开基线对比，种子 A 具备投 USENIX Security / IEEE TIFS 量级的潜力；种子 B/C 可作为配套发表。
- **最危险的自我陷阱**：项目已出现"235/262 条规则、100% 召回、0% 误报"的漂亮数字叙述。审稿人第一反应会是"自精选语料 + 完美数字 = 过拟合"。现有的 errata 与公开缺口清单是正面信号，但**只有外部独立语料能真正打消这个疑虑**——这是通往 SCI 的必经一关。

---

*本报告基于 2026-10-18 实跑 `scripts/benchmark.py` 与 `scripts/run_fvi_gate.py` 的结果，以及 `docs/benchmark/v1.md`、`formal/`、`docs/rsi-asi-mapping.md`、`scanner/neuro_symbolic_probe.py` 的源码核查。*
