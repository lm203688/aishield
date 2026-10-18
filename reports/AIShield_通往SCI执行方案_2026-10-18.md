# AIShield 通往 SCI 论文的下一阶段执行方案（直接落地版）

> 产出日期：2026-10-18 · 基于《AIShield_科学性评估与SCI可行性_2026-10-18.md》的差距 G1–G6 与种子 A/B/C
> 主航道：**种子 A**——*An Offline, Zero-Dependency, Machine-Verifiable Framework for Agentic-AI Supply-Chain & Prompt-Injection Threat Detection*
> 配套：种子 B（RSI-L5 威胁分类，并入论文 §3/§6）、种子 C（形式化工具论文，论文 §5 + 独立 tool 稿）

---

## 0. 先定义"什么叫达标"（验收门槛）

不要先写论文，先钉死"可投稿"的客观标准。以下 7 条全部满足，才算 SCI-submissible：

| # | 验收门槛（量化、可测） | 对应差距 |
|---|---|---|
| R1 | **外部独立语料**正样本 ≥400、负样本 ≥400，覆盖 ≥15 个攻击族，且含 ≥2 名标注者的 **Cohen's κ ≥ 0.8** 一致性记录 | G1/G5 |
| R2 | 在**同一固定语料**上与 **≥3 个基线**（mcp-audit / Invariant mcp-scan / agent-security-scanner-mcp / Snyk agent-scan 中任选 ≥3）产出 precision/recall/F1 | G2 |
| R3 | 上述指标附 **bootstrap 95% 置信区间**（≥1000 次重采样） | G4 |
| R4 | 形式化隔离不变量完成 **穷举模型检查（Apalache）或给出有界穷举 + 完备性论证**，并量化状态空间规模 | G3 |
| R5 | 论文含**尖锐单一贡献陈述** + 系统 related-work（对比 Invariant/Snyk/Lakera-Gandalf/OWASP Agentic/NIST AI RMF） | G6 |
| R6 | **可复现性包（artifact）**：Dockerfile + 固定语料 + 一键复跑（benchmark + FVI gate），可过 artifact evaluation | — |
| R7 | 诚实报告局限（外部语料召回不必 100%；贡献在方法论+形式保证，而非榜单第一） | G1 |

> 反目标提醒：**不要再追"100% 召回 / 0% 误报"的自精选叙事**。审稿人第一反应是过拟合。把贡献锚定在「方法可复现 + 形式可验 + 零误报纪律 + 外部语料可比」上。

---

## 1. 总体分阶段路线（时间盒，约 14–18 周）

| Phase | 周期 | 目标 | 关键交付 | 验收 |
|---|---|---|---|---|
| **P0** 工程基线加固 | 1–2 周 | 止血 + 真值源 + CI 固化 | 修死分支、规则数单一真值源、benchmark/FVI 进 CI | P0 任务全绿 |
| **P1** 外部独立语料 | 3–5 周 | 破 G1/G5（最关键） | 外部语料 schema + 采集 + 标注 IAA + 加载器 | R1 达成 |
| **P2** 公开基线对比 | 2–3 周 | 破 G2 | baseline runner + compare（含 CI） | R2/R3 达成 |
| **P3** 形式化升级 | 1–2 周 | 破 G3 | Apalache 穷举 或 完备性论证 + 新不变量 | R4 达成 |
| **P4** 统计严谨 + 撰写 | 4–6 周 | 破 G4 + 主航道稿 | bootstrap CI + 论文 A 10–12 页 + 种子 B/C 章节 | R5 初稿 |
| **P5** 可复现包 + 投稿 | 2–3 周 | 收口 | Dockerfile + artifact + 选 venue 投稿 | R6/R7 达成 |

依赖链：**P0 → P1 → P2 → P4 → P5**；**P3 可与 P1 并行**；**P4 吸收 P2/P3 结果**。

---

## 2. 任务卡（文件级执行要求）

### Phase 0 — 工程基线加固

**任务 0.1｜修 `benchmarks/run_bench.py` 死分支（已知缺陷）**
- 位置：第 82–88 行 `if cfg.get("expect_typosquat"): ... pass` 是空操作，从不校验 typosquat。
- 改法：把 `expected.json` 里 `malicious.expect_typosquat=true` 落为真实断言——
  ```python
  if cfg.get("expect_typosquat"):
      typ = any("typosquat" in t or "hallucinated" in t or "package_name" in t
                for t in types)
      dep_types = " ".join(d.get("type", "") for d in dep.get("findings", []))
      if not (typ or "hallucinated" in dep_types):
          ok = False
          reasons.append("未检出预期 typosquat/hallucinated")
  ```
- 验收：`python benchmarks/run_bench.py` 退出码 0；对恶意样本缺失 typosquat 时 FAIL。

**任务 0.2｜规则数单一真值源**
- 问题：`AGENTS.md` 写 v4.8.3/264，`mcp-server/README.md` 自相矛盾（"静态 235 (113+62+11+22)" 但求和=208≠235）。
- 改法：所有"规则数"文案统一引用 `api/server.py` 的 `/api/v1/health` 的 `rules_breakdown`；删 `scripts/sync_readme_counts()` 的错误引用（真实为 `rule_count_gate.py`）。
- 验收：全仓 grep 规则数只有"实时派生"一种来源；自扫描门禁不报矛盾。

**任务 0.3｜benchmark + FVI 进 CI 单一入口**
- 改法：在 `.github/workflows/` 增 `eval-gate.yml`，仅调用 `python scripts/benchmark.py --fail-under-recall 0.9 --fail-over-fp 0` 与 `python scripts/run_fvi_gate.py`，复用既有的 `prepare-tests` 动作（装 pytest/pyyaml/cryptography）。
- 验收：PR 触发 eval-gate，任一数字退化即红。

### Phase 1 — 外部独立语料（破 G1/G5，最关键）

**任务 1.1｜定义外部语料 schema**
- 新建 `benchmarks/corpus/external/positives/<id>.json` 与 `negatives/<id>.json`，单样本字段：
  ```json
  {
    "id": "ext-pos-0001",
    "family": "credential_exposure",
    "source": "github-advisory/GHSA-xxxx",
    "license": "CC0/permissive",
    "text": "<被扫内容原文或指针>",
    "labels": [{"annotator": "A", "positive": true}, {"annotator": "B", "positive": true}],
    "sha256": "<内容指纹>"
  }
  ```
- 新建 `benchmarks/corpus/external/manifest.json`：记录样本数、各 family 计数、**Cohen's κ**、采集日期、来源清单。

**任务 1.2｜数据源清单（一次性采集，运行时仍离线）**
- 来源：① OSV/GitHub Advisory 真实 CVE 依赖；② 公开恶意 MCP server 仓库快照；③ 公开 prompt-injection 数据集（如 PJB）**固定版本快照**（避免"一次性跑"不可复现）；④ agent 安全论文的 artifact/附录样本。
- 纪律：采集是一次性的；`benchmark.py` 运行时不联网。所有外部样本落盘 + sha256。

**任务 1.3｜标注与 IAA**
- ≥2 名标注者对全部样本打正负标签；计算 **Cohen's κ ≥ 0.8** 才入册；分歧样本由第三人仲裁或剔除。
- 验收：manifest 写入 κ 值与分歧处理记录。

**任务 1.4｜扩展加载器**
- 在 `scripts/rule_corpus.py` 增 `EXTERNAL_POSITIVES` / `EXTERNAL_NEGATIVES` 加载器（读 `benchmarks/corpus/external/`）。
- `scripts/benchmark.py` 增 `--corpus {internal,external,all}` 与合并模式；外部语料走与内部**完全相同的** `serious_only`/`any_finding` 口径。
- 验收：`python scripts/benchmark.py --corpus external` 产出外部语料专属 recall/FP + 各 family 覆盖。

**任务 1.5｜规模目标**
- 正 ≥400、负 ≥400、覆盖 ≥15 攻击族（对齐内部 family_coverage 的 19 个族）。
- 验收：**R1** 达标（数量 + κ + 族覆盖）。

### Phase 2 — 公开基线对比（破 G2）

**任务 2.1｜选基线**
- 至少 3 个：mcp-audit、Invariant mcp-scan、agent-security-scanner-mcp（优先）；可选 Snyk agent-scan。

**任务 2.2｜写 `benchmarks/baselines/runner.py`**
- 每个基线用各自 Docker/venv 隔离调用，输入为**同一固定语料**（内部+外部合并集），输出归一化 schema：
  ```json
  {"sample_id": "ext-pos-0001", "detected": true, "severity": "high"}
  ```
- 纪律：每个基线记录**版本号 + 运行日期 + 命令**，确保可复现。

**任务 2.3｜写 `scripts/baseline_compare.py`**
- 在同一语料上算每个工具的 precision / recall / F1，并对 recall/FP 做 **bootstrap 95% CI（1000 次重采样）**。
- 输出 Markdown 对比表，列：工具 / 版本 / recall(95%CI) / FP(95%CI) / F1 / 规则数 / 是否上云。

**任务 2.4｜诚实标注**
- 若某基线须上云，在表内标注"非离线"，并在论文局限节说明对比条件不对等。
- 验收：**R2/R3** 达成（≥3 基线 + CI）。

### Phase 3 — 形式化升级（破 G3，可与 P1 并行）

**任务 3.1｜穷举模型检查**
- 装 Java + Apalache，运行 `quint verify --invariants invNoExecute invFailClosed invReadOnly`（替换现有 `quint run` 模拟）。
- 记录状态空间规模（states explored / diameter）。

**任务 3.2｜退路（Apalache 不可行时）**
- 把 `scripts/check_isolation_invariants.py` 升级为**有界穷举**（扩 `explore` 的 bound，报告可达状态总数与覆盖），并写一段**完备性论证**（为何该 bound 覆盖全部可达行为）。

**任务 3.3｜扩展不变量**
- 把单写者（E13）、声明面门禁盲区等更多不变量补进 `formal/isolation_invariants.qnt` 与 Python BMC。

**任务 3.4｜量化交付**
- 输出：状态空间大小、覆盖百分比、变异测试清单（含已抓到的缺陷变体）。
- 验收：**R4** 达成。

### Phase 4 — 统计严谨 + 论文撰写（破 G4 + 主航道/种子 B/C）

**任务 4.1｜bootstrap CI**
- `scripts/benchmark.py` 增 `--bootstrap 1000`，输出 recall/FP 的 95% CI。
- 验收：**R3** 内部口径也具备 CI。

**任务 4.2｜论文 A 大纲（10–12 页，CCF-A/SCI 取向）**
1. **Introduction**：一句话 thesis——*"我们提出一个离线、零依赖、机器可验的 Agentic AI 威胁检测框架，其安全不变量可被形式化证明、其检测纪律保证零误报扩张。"*
2. **Background & Related Work**：OWASP MCP Top10(2025)、OWASP Agentic AI Top10、Invariant mcp-scan、Snyk agent-scan、Lakera/Gandalf、prompt-injection 基准（PJB）、NIST AI RMF；明确差异化（离线+形式化+零FP纪律的组合稀缺）。
3. **Threat Model**（种子 B 并入）：RSI L1–L5 → OWASP Agentic 映射；实证发现"L5 信号被能力过滤器抑制"的缺陷与修复。
4. **Design**：离线扫描引擎架构；神经-符号零误报桥接（`ratify()` 纪律：神经层永不自升级）。
5. **Formal Isolation Invariants**（种子 C 并入）：Quint + Python BMC + Hypothesis 三层防线；变异测试判别力证明；穷举/完备性结果（P3）。
6. **Evaluation**：外部语料（R1）、基线对比（R2/R3）、各 family 覆盖、真实 harness 面。
7. **Limitations**：外部语料规模、形式化模拟边界、基线条件不对等。
8. **Conclusion**。

**任务 4.3｜种子 B/C 收口**
- B：把 `docs/rsi-asi-mapping.md` 精炼为 §3 的定量章节（加 N 个 agent 仓库的验证实验）。
- C：可作为 §5 的 basis，另起一篇 tool 论文投 CAV/FM/ASE。

**任务 4.4｜related-work 清单落地**
- 明确对比对象与差异表（见 §2 背景），避免"像系统介绍"。
- 验收：**R5** 初稿完整。

### Phase 5 — 可复现包 + 投稿

**任务 5.1｜Dockerfile**
- 固定 python 版本、`formal/` 装 quint（及 Apalache/Java 若 P3 选用）；entrypoint：
  ```dockerfile
  RUN python scripts/benchmark.py --json && python scripts/run_fvi_gate.py
  ```

**任务 5.2｜artifact 说明**
- 写 `ARTIFACT.md`：数据卡片（语料来源/license/κ）、复跑步骤、预期输出。

**任务 5.3｜选 venue 与投稿**
- 主推 **USENIX Security 2027**（系统/安全顶会，重 artifact）或 **IEEE TIFS**（SCI 期刊）。
- 按模板提交，附 artifact。
- 验收：**R6/R7** 达成。

---

## 3. 风险与对策

| 风险 | 对策 |
|---|---|
| 外部语料标注一致性难（κ<0.8） | 先小批量试标校准标注指南；分歧样本仲裁或剔除，不强行入册 |
| 基线工具环境/版本漂移导致不可复现 | 每个基线锁版本 + 录运行命令/日期；上云基线单独标注 |
| Apalache 依赖 Java/网络，离线环境装不上 | P3 任务 3.2 退路：有界穷举 + 完备性论证，仍可达 R4 |
| 论文"像系统介绍"被拒 | P4 任务 4.4 强制 related-work 差异表；thesis 一句可概括 |
| 投稿周期长（顶会 4–6 月） | P1–P4 先产出预印本（arXiv），边投边积累引用 |

---

## 4. 执行纪律（对应本项目 AGENTS.md 不变量）

- **单一真值源**：规则数、口径、语料计数只来自派生源，不手抄（B7/E8/E9/E10/E14 同源）。
- **不吞失败**：eval-gate / FVI gate 失败必须红，禁止 `|| true`（E10）。
- **范围纪律**：本方案只在既有资产上扩语料/加对比/升形式化，**不重构** `api/server.py` god file、**不新增**未请求的功能（B7）。
- **派生门禁**：新增语料/规则后，`rule_count_gate` 与 eval-gate 必须同步复跑。

---

## 5. 一句话启动（P0 + P1 起点）

```bash
# P0 止血
python benchmarks/run_bench.py            # 先确认死分支修复后绿
# P1 起点：建外部语料骨架
mkdir -p benchmarks/corpus/external/positives benchmarks/corpus/external/negatives
# 然后按任务 1.1 schema 落样本 + manifest（κ≥0.8），再扩展 rule_corpus.py 加载器
```

> 本方案所有"现状"均来自 2026-10-18 实跑 `scripts/benchmark.py`（57/57、0 FP）与 `scripts/run_fvi_gate.py`（PASS）的核验结果。执行中每完成一个 Phase，建议回头重扫一次以核对是否引入新漂移。
