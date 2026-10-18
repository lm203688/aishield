# 论文 A 大纲（Paper A Outline）

> 对应执行方案 P4 任务 4.2 / 4.3 / 4.4。目标 venue：USENIX Security 2027 或 IEEE TIFS（见 `reports/venue_decision.md`）。
> 篇幅：正文 10–12 页（双栏，ACM/IEEE 模板）。本文档为**骨架 + 每节要点 + 已核实数字占位**，非全文草稿。
> 所有数字均为当前仓库实测，禁止在终稿里手写与下表不一致的数值（单一真值源见 `ARTIFACT.md` / `benchmarks/expected.json`）。

---

## 一句话 Thesis（尖锐单一贡献）

> **我们提出 AIShield：一个离线、零依赖、机器可验证的 Agentic-AI 威胁检测框架，其"永不执行被扫代码"等安全不变量可被形式化穷举证明（64 可达态、4 变异体全抓），且其检测纪律保证在外部公开语料上零误报扩张（0/517 FP）。**

差异点（组合稀缺，须反复强调）：**离线 + 形式化穷举证明 + 零误报纪律** 三者同时成立。现有工具至多占其一（见 §2 差异表）。

---

## §1 Introduction（1.5 页）

- 背景：MCP / Agentic AI 把"执行外部代码/工具"常态化，攻击面从传统软件供应链扩展到 prompt-injection、工具投毒、能力越权。
- 痛点：现有护栏要么上云（数据出域）、要么无形式保证（"声称安全"不可验）、要么误报高（被用户禁用）。
- 我们的回答：AIShield = 264 规则 + 291 技能 + 5 形式化不变量，全部可离线、可复跑、可机器验。
- 贡献三件套（用 bullet 明确，避免"像系统介绍"被拒）：
  1. **形式化穷举证明**：Python BMC 穷举 64 可达态 + 完备性论证 + 4 变异体判别力（R4）。
  2. **零误报纪律的实证**：外部公开语料 593 正 / 517 负，FP = 0/517（0.0%），bootstrap 95% CI 钉死。
  3. **诚实基线对比**：同一固定语料上 ≥3 个可出真实数字的基线（含 2 个朴素离线基线 + 自身），4 个商业基线诚实标注"条件不对等"不伪造（R2/R3）。

---

## §2 Background & Related Work（1.5 页）+ 差异表（R5 硬性要求）

对比对象（按执行方案 R5）：OWASP MCP Top10(2025)、OWASP Agentic AI Top10、Invariant mcp-scan、Snyk agent-scan、Lakera/Gandalf、prompt-injection 基准（PJB / InjecAgent）、NIST AI RMF。

**差异表（终稿放 §2 末，必填，防"系统介绍"拒稿）：**

| 系统 / 基准 | 离线可跑 | 形式化穷举证明 | 零误报纪律 | 固定公开语料+CI | 规则/技能数 |
|---|---|---|---|---|---|
| **AIShield（本文）** | ✓（零依赖） | ✓（64 态穷举+4变异） | ✓（0/517 FP） | ✓（593/517, 18 family） | 264 / 291 |
| Invariant mcp-scan | 部分（docker） | ✗ | 未量化 | ✗（本环境未跑） | ~150 |
| Snyk agent-scan | ✗（须上云+token） | ✗ | 未量化 | ✗ | N/A |
| Lakera / Gandalf | ✗（SaaS） | ✗ | 未量化 | 基准非检测工具 | — |
| PJB / InjecAgent | —（基准） | — | — | ✓（被本文复用为负样本源） | — |
| OWASP Top10 | —（清单） | — | — | — | — |

> 该表直说"条件不对等"那几格不编造数字，正是论文诚实性的卖点。

---

## §3 Threat Model（种子 B 并入，1 页）

- RSI L1–L5 威胁分层 → OWASP Agentic AI Top10 映射（来源 `docs/rsi-asi-mapping.md`，精炼为定量章节）。
- 实证缺陷与修复（种子 B 核心故事）：**"L5 信号被能力过滤器抑制"**——早期版本对高危信号做了过度保守的可用性过滤，导致 L5 级攻击静默放行；修复后纳入 INV 体系并回归。
- 攻击面枚举：prompt-injection / 工具投毒 / 供应链执行 / 越权写 / 信息外泄，对应外部语料 18 个家族。

---

## §4 Design（1.5 页）

- 离线扫描引擎架构：instruction-plane 与 config-plane 双通道（对应语料 `scan_plane` 字段）。
- 神经-符号零误报桥接纪律 `ratify()`：神经层（LLM 辅助）**永不自升级**为执行动作；任何"执行被扫代码"的尝试被 INV-1/INV-2 硬拒（fail-closed）。
- 规则→技能→能力的分层；264 静态/生成/雷达规则与 291 技能的声明面单一真值源（`/api/v1/health.rules_breakdown`）。
- 为什么"零依赖"是安全属性而非工程偏好：攻击面最小化 = 不加载第三方解释器/联网库。

---

## §5 Formal Isolation Invariants（种子 C 并入，2 页 —— 论文最强差异点）

- 五不变量分层 INV-1~INV-5（no_execute / no_network / single_writer / read_only_input / completeness）。
- 三层防线：Python 有界模型检查（**主证明，穷举 64 态**）+ Quint 随机模拟（交叉验证）+ Hypothesis 属性测试（真实实现）。
- **R4 达成证据**：`explore_with_report()` 以 `termination=exhausted` 枚举 64 可达态，`coverage=1.0`，`complete=true`；`completeness_argument()` 由构造证 |reachable|=64 并与实测交叉校验。
- **判别力自证（防假绿）**：M1 leak-exec-net / M2 secondary-writer / M3 readonly-violation / M4 partial-processing 四个缺陷变异体**全部被抓到**，否则门禁失败。
- 种子 C 延伸：本 § 可作为独立 tool 论文 basis 投 CAV / FM / ASE（见 `venue_decision.md`）。

---

## §6 Evaluation（2.5 页 —— 对应 R1/R2/R3）

### 6.1 内部语料（自身回归）
- 召回 57/57 = **100.0%**，误报 0/45 = **0.0%**（serious_only 口径，与 Plane E 一致）。

### 6.2 外部公开语料（R1）
- 规模：**593 正 / 517 负 / 1110 总 / 18 家族**（GitHub Advisory + InjecAgent 等公开数据集，非自造）。
- 召回 **29.51% [25.8%, 33.22%]**（bootstrap 95% CI，seed=20261018，1000 重采样）；FP **0.0% [0.0%, 0.0%]**。
- **诚实 R1 阻塞项**：Cohen's κ = null（仅 1 标注来源，自动化无法补齐，需 ≥2 名独立人类标注者）。`r1_status.met=false`，不伪造 κ。这是局限性章节（§7）的直接引用素材。

### 6.3 基线对比（R2/R3）
同一固定语料、serious_only 口径、bootstrap 种子固定。

| 工具 | recall(95%CI) | FP(95%CI) | F1 | 规则数 | 上云 |
|---|---|---|---|---|---|
| **AIShield** | **29.5% [25.8%, 33.2%]** | **0.0% [0.0%, 0.0%]** | 46% | 264 | 否 |
| Naive keyword heuristic | 21.1% [17.9%, 24.4%] | 0.0% [0.0%, 0.0%] | 35% | 0 | 否 |
| Random guess (base-rate) | 48.9% [44.9%, 52.8%] | 53.8% [49.5%, 58.0%] | 50% | 0 | 否 |
| Invariant / agent-security-scanner / mcp-audit / Snyk | N/A（条件不对等，未运行） | — | — | — | — |

**尖锐解读（关键，避免被误读为"不如随机"）**：对**护栏**而言 FP 必须近零（误报被禁用即失效）。在 **FP=0 约束下**，AIShield recall 29.5% **严格优于** keyword 21.1%（同 FP 下更高召回），并**碾压** random（后者 54% FP 在实际部署中不可用）。Random 的更高原始 recall 恰恰说明：原始召回率不是护栏的正确指标，零误报纪律才是本工作的立身之本。

### 6.4 家族覆盖
18 个正样本家族覆盖情况（indirect_prompt_injection 176 / data_exfiltration 176 / jailbreak 175 为三大主力；技术漏洞类长尾各 1–7）。讨论分布偏斜对外部召回的影响。

---

## §7 Limitations（R7 硬性要求，1 页）

- **外部召回非 100%**：AIShield 规则针对自身内部模式，外部语料以文本注入为主，29.5% 召回是**分布外（OOD）**下的诚实结果；贡献在方法论 + 形式保证，不在榜单第一。
- **R1 的 κ 阻塞**：单标注源导致 κ 未定义，已诚实留空；补第二标注者即可解锁（流程已支持）。
- **形式化边界**：Python BMC 穷举的是**动作系统模型**（64 态），真实实现由 Hypothesis + 回归兜底；模型-实现偏差是已知近似。Quint 的穷举（Apalache）列为增强证据未阻塞 R4。
- **基线条件不对等**：4 个商业基线本环境不可跑，对比表留白不伪造；论文明确标注此为对比公平性边界。

---

## §8 Conclusion（0.5 页）

- 回扣 thesis：离线 + 形式化穷举 + 零误报纪律三者兼得的框架是可行且可机器验的。
- 展望：双标注解锁 κ、Quint 穷举独立证据、种子 C 独立 tool 稿、更多 harness 面覆盖。

---

## 附录 / Artifact（R6）

- Dockerfile（固定 python:3.13-slim + 离线 entrypoint 跑 benchmark + FVI gate）。
- `ARTIFACT.md` 一键复现：`python scripts/run_all.py` 聚合六门禁 + FVI + 测试 + benchmark。
- 预期退出码全 0；任一直言非 0 即不可复现。

---

## 验收映射（R5）

- [x] 尖锐单一贡献陈述（§1 thesis + §6.3 解读）
- [x] 系统 related-work + 差异表（§2 表）
- [x] 种子 B 并入（§3 RSI→OWASP + L5 缺陷故事）
- [x] 种子 C 并入（§5 形式化穷举 + 变异判别力，可作独立 tool 稿）
- [x] 真实数字全部入位（内部 100%/0%、外部 29.51%/0%、FVI 64 态、baselines 三真实数字）
