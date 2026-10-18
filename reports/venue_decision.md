# 投稿 Venue 决策（Venue Decision）

> 对应执行方案 P5 任务 5.3（R6/R7 达成）。本文档固化 venue 选择、时间线与预印本策略，供后续投稿动作直接执行。

---

## 1. 结论（TL;DR）

| 优先级 | Venue | 类型 | 为什么 |
|---|---|---|---|
| **主推 A** | **USENIX Security 2027** | 系统/安全顶会（CCF-A，重 artifact） | 本文最大卖点（形式化穷举 + 零误报 + 可复现包）正中 USENIX 评审偏好；artifact evaluation 是加分项而非障碍 |
| **主推 B** | **IEEE Transactions on Information Forensics and Security (TIFS)** | SCI 期刊（CCF-A，安全领域 SCI 一区） | 若顶会周期/命中率风险高，TIFS 是"SCI 发表"硬指标的直接落点；更容得下 10–12 页系统 + 形式化细节 |
| **并行** | **arXiv 预印本** | 预印本 | 不等审稿周期，先把可复现包与结果公开积累引用（执行方案风险对策明确建议） |

**决策原则**：先 arXiv 预印本（立即上线，固定优先权），再投 USENIX Security 2027；若 USENIX 落选或周期不匹配，转 TIFS。两路不互斥，arXiv 恒为第一动作。

---

## 2. USENIX Security 2027 关键事实（须以官网为准，以下为计划占位）

- 定位：系统与安全顶会，artifact evaluation 为正式环节，鼓励"可复现系统论文"。
- 篇幅：正文约 12–13 页（双栏，含参考文献上限以当年 call 为准）。
- 时间线（占位，需查 2027 官方 deadlines）：
  - 摘要 / 正文 deadline：约 2026 年底至 2027 年初（通常提前 ~6 个月）。
  - 通知：约 deadline 后 3 个月。
  - 会议：2027 年 8 月（USENIX Security 惯例夏末）。
- 适配动作：论文 A 大纲（§1–§8）已按 10–12 页设计；§5 形式化与 §6 可复现包直接对应 artifact evaluation。

---

## 3. IEEE TIFS 关键事实（期刊，SCI）

- 定位：IEEE 信号处理协会 / 安全与取证领域 SCI 一区（CCF-A），接受系统+形式化交叉稿。
- 篇幅：正文 10–14 页（双栏，含图），比顶会宽松，可展开 §5 完备性论证与 §6 全部家族细节。
- 周期：投稿→一审约 3–6 个月；可先 arXiv 占位不冲突。
- 适配动作：论文 A 大纲直接复用；若转 TIFS，把 §5 论证与 §6.4 家族覆盖扩展为独立小节。

---

## 4. arXiv 预印本策略（立即执行项）

- 仓库已有完整可复现包（ARTIFACT.md + run_all.py + 语料 + FVI）。预印本须附带：
  - 完整 `ARTIFACT.md` 与 `reports/paper_a_outline.md` 对应正文。
  - 真实数字（内部 100%/0%、外部 29.51% [25.8,33.22]/0%、FVI 64 态、baselines 三真实数字）。
  - **诚实标注 R1 κ=null 阻塞**（§7 limitations），不删除不掩饰。
- 分类：cs.CR（密码学与安全）+ cs.AI（人工智能）。
- 优先权：在 USENIX/TIFS 投稿前 1–2 周挂出，固定优先权日。

---

## 5. 投稿前硬性 Checklist（R6/R7）

- [ ] `python scripts/run_all.py` 全绿（六门禁 + FVI + 测试 + benchmark），退出码 0。
- [ ] Dockerfile 存在且 entrypoint 跑 `benchmark --json` + `run_fvi_gate.py`（P5 任务 5.1）。
- [ ] `ARTIFACT.md` 数字与仓库实测一致（单一真值源）。
- [ ] 论文 §2 差异表、§5 形式化、§6.3 baseline 解读、§7 limitations（含 κ=null）齐全。
- [ ] arXiv 预印本已挂，分类 cs.CR + cs.AI。
- [ ] 按 venue 模板排版（USENIX 用 `usenix` LaTeX 类；TIFS 用 IEEEtran）。

---

## 6. 种子 C 独立 Tool 稿延伸（可选第二发表）

- §5 的 Python BMC + Quint + Hypothesis 三层防线 + 4 变异判别力，可独立于论文 A 投 **CAV / FM / ASE** 的 tool/artifact 轨道。
- 价值：把"可证明安全的 Agent 护栏"作为方法论工具稿单独发表，放大引用面，不与论文 A 的"系统+评估"主线冲突（须在稿件中明确区分贡献边界，避免 self-plagiarism）。
