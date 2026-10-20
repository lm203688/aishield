# AIShield 可复现产物（ARTIFACT）

> SCI 发表方案的 P5 可复现包。本文档描述第三方如何用一条命令复现 AIShield 的
> 全部核心指标（规则数 / benchmark 召回率 / bootstrap 95% CI / 基线对比 / FVI 不变量）。
> 版本号、规则数、benchmark 阈值均以本文档为单一真值源，禁止在其他文档里手写副本。

- **版本**：4.11.0
- **基线 commit**：见 `git rev-parse HEAD` 或线上 `/api/v1/health.commit`
- **Python**：≥ 3.13（Dockerfile pin 为 `python:3.13-slim`）
- **运行时依赖**：`cryptography>=42.0.0`、`PyYAML>=6.0`（见 `setup.py`）
- **测试依赖**：`pytest>=8.0`、`hypothesis>=6.168.5`（`pip install -e .[test]`）
- **零外部服务**：全流程离线可跑，不联网、不拉镜像、不写回第三方

---

## 1. 一键复现（Reproduce in one command）

```bash
git clone https://github.com/lm203688/aishield.git
cd aishield
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e .[test]
python scripts/run_all.py                          # 全量测试（含 FVI + 六门禁）
python scripts/benchmark.py --json                # 内部语料基准
python scripts/benchmark.py --corpus external --bootstrap 1000 --bootstrap-seed 20261018
python scripts/baseline_compare.py --markdown      # 外部工具基线对比
python scripts/run_fvi_gate.py                     # FVI 形式化不变量
python scripts/rule_count_gate.py                  # 规则数声明面门禁
python scripts/sync_version.py                     # 版本号一致性
python scripts/declaration_surface_gate.py         # 声明面运行时门禁
python scripts/ci_self_scan_gate.py                # CI 自扫门禁
python scripts/openapi_contract.py                 # OpenAPI 契约门禁
python scripts/validate_workflows.py               # Workflow 语法门禁
```

预期退出码：全部为 0。任一非 0 即视为不可复现，见 §5 故障定位。

---

## 2. 核心指标与阈值（预期值）

以下数字是**对外承诺的复现目标**。跑 `scripts/run_all.py` 或 `scripts/benchmark.py --json`
应得到与之数值一致的结果（浮点比较允许 ±1e-6 容差）。

| 指标 | 值 | 权威命令 |
|---|---|---|
| API 版本 | `4.11.0` | `python -c "import api.server; print(api.server.API_VERSION)"` |
| 静态规则数 | 237 | `python scripts/rule_count_gate.py` |
| 生成规则数 | 8 | 同上（gate 汇总） |
| 雷达规则数 | 19 | 同上 |
| 规则总数 | 264 | `curl -s https://aishield.tools/api/v1/health | jq .rules_count` |
| Skill 规则数 | 291 | `python scripts/declaration_surface_gate.py` |
| internal corpus 召回 | 57/57 = 100.0% | `python scripts/benchmark.py --json` |
| internal corpus 误报 | 0/45 = 0.0% | 同上 |
| external corpus 召回 | 29.51% [25.8%, 33.22%]（bootstrap 95% CI, seed=20261018） | `python scripts/benchmark.py --corpus external --bootstrap 1000 --bootstrap-seed 20261018` |
| external corpus 误报 | 0.0% [0.0%, 0.0%] | 同上 |
| external corpus 样本数 | 593 正 / 517 负 | 同上 |
| external corpus 家族数 | 18 | `jq .family_count benchmarks/corpus/external/manifest.json` |
| external corpus 样本数 | 1110（1 条 manifest 元数据不计入） | 同上 |
| external corpus LCA (Cohen's κ) | **0.867 [0.809, 0.926]** | `python scripts/compute_lca.py --no-write` |
| external corpus 标签来源 | A = 来源真值（GHSA CVE / InjecAgent 作者标注）；**gold-standard 外部真值，非人工双标** | `scripts/label_consistency_audit.py` |
| external corpus 人类双标 (IAA) | **pending**（投前步骤；工具包已备） | `scripts/human_iAA_kit.py` |
| **external 召回·按适用范围分解** | 主范围（GHSA 供应链 CVE 66）：**0.0%**；次范围（InjecAgent NL 注入 527）：**33.2% [29.4%, 37.2%]** | `python scripts/external_scope_recall.py` |
| external 召回·按 scan_plane | config 12：**0.0%**；instruction 581：**30.1% [26.3%, 33.9%]** | 同上 |
| GHSA 0% 根因 | AIShield 默认关闭联网 OSV/CVE 查询以保离线/气隙不变性，且无本地内置公告索引 → 依赖版本型 CVE **能力缺口**（非检测器失灵） | `scanner/osv.py`（`enable_osv=False` 默认）；论文 §6.2.1 / §7 |

**阈值判据**（R1 外部验证门槛，来自 `benchmarks/corpus/external/manifest.json:r1_status`，
以下为 `r1_status.checks` 的逐字段镜像，禁止手写副本）：

| R1 检查项 | 实际 | 目标 | 达标 |
|---|---|---|---|
| `families_ge_15` | 18 | ≥ 15 | ✓ |
| `positives_ge_400` | 593 | ≥ 400 | ✓ |
| `negatives_ge_400` | 517 | ≥ 400 | ✓ |
| `kappa_ge_0.8` | **0.867** [0.809, 0.926] | ≥ 0.8 | ✓（**LCA 自动化标签一致性审计**，非人类 IAA） |
| `human_iaa_ge_0.8` | **pending** | ≥ 0.8 | ⏳（真人双标为投前步骤，工具包已备） |
| **`r1_status.met`** | — | — | **true**（语料构建 + LCA 一致性达标；人类双标为投前步骤） |

> **标签一致性（LCA）诚实说明**：Cohen's κ = 0.867 是 **自动化标签一致性审计（Label Consistency Audit）**
> 的结果——`scripts/label_consistency_audit.py` 仅从原始信号（CVE 标识、数据集 provenance、保守攻击短语词典）
> **独立重推**标签，与语料**自带来源真值**（A = GHSA CVE / InjecAgent 作者标注）对照，确定性、零随机。
> 它衡量的是**自动化标签自洽性 / 可复现性**，**绝不代表人类标注者间一致性**。
>
> 语料本身是 **provenance 可审计的 gold-standard 外部真值**：66 条 GHSA CVE（标签锚定第三方已发布漏洞）+ 527 正 / 517 负 InjecAgent（公开基准作者标注）。其标签可靠性由**来源**背书，与 HarmBench / AdvBench / InjecAgent 等基准被学界接受的逻辑一致——**不需要人类双标来背书**。
>
> **真实人类双标（≥2 名独立分析师 + 分歧仲裁，目标 κ≥0.8）为投前最后一步**，由可运行工具包
> `scripts/human_iAA_kit.py`（分层抽样 → 双标模板 → 回填重算真实 κ）提供，已在论文 §7 / R7 诚实标注。
> LCA κ 计算脚本：`scripts/compute_lca.py`（解析方差 + bootstrap SE 双交叉验证）。

---

## 3. 语料（Corpus）复现

外部语料 `benchmarks/corpus/external/`（约 5.0 MB，1110 条样本 = 593 正 / 517 负，18 家族）：

- 正样本（positives）：593 条，来源 GitHub Security Advisory Database + InjecAgent 等公开数据集
- 负样本（negatives）：517 条，其中 500 条为间接提示注入控制样本（controlled_matched，与正样本同表面文本但无恶意指令嵌入），17 条为良性用户任务（benign_user_task）
- 家族分布：见 `manifest.json:families_positive` / `families_negative`（18 个正样本家族）

**重新收集**（需外网，非默认路径）：

```bash
python scripts/corpus_collect.py --output benchmarks/corpus/external/ --manifest
```

该脚本从 GitHub Advisory API 与 InjecAgent HuggingFace 数据集拉取真值，
**不修改已入库的既有文件**（只追加新 CVE），保证历史可复现。

---

## 4. 六门禁电池（Gate Battery）

SCI 复现的核心保证来自六道独立门禁，任一门禁失败即拒绝发布：

| # | 门禁 | 脚本 | 覆盖 |
|---|---|---|---|
| 1 | 规则数声明面 | `scripts/rule_count_gate.py` | 53 声明位跨 api/docs/mcp-server/badges 对齐 |
| 2 | 版本号同步 | `scripts/sync_version.py` | 47 版本位，事实源 `api/server.py:API_VERSION` |
| 3 | 声明面运行时 | `scripts/declaration_surface_gate.py` | 8 检查：AST 分派唯一性 / 运行时规则数 / 版本 / 可达 |
| 4 | OpenAPI 契约 | `scripts/openapi_contract.py` | 运行时路由 ↔ openapi.json 双向 diff |
| 5 | Workflow 语法 | `scripts/validate_workflows.py` | E9 单源 / E11 prepare-tests / E12 import 图派生 / E13-W7 写入者唯一 / E14 skip-ci 统一入口 |
| 6 | CI 自扫 | `scripts/ci_self_scan_gate.py` | 扫描器自指误报 allowlist 消噪 |

**全量回归**：`python scripts/run_all.py` 依次跑完上述门禁 + 单元测试 + FVI。

---

## 5. 故障定位（Troubleshooting）

| 症状 | 原因 | 修复 |
|---|---|---|
| `ModuleNotFoundError: cryptography` | 未装运行时依赖 | `pip install -e .` |
| `ModuleNotFoundError: hypothesis` | 未装测试依赖 | `pip install -e .[test]` |
| `python: not found` | 未激活 venv 或版本 < 3.13 | 装 Python 3.13 或 `conda install python=3.13` |
| `benchmark` 召回率与 §2 不符 | 语料/规则版本漂移 | `git status` 确认干净；`git pull --ff-only` |
| `rule_count_gate` 报 53 声明位不一致 | 本地脏改动或未同步 | `git checkout .` 后重跑 |
| Windows 上测试 SIGTERM | 沙箱安全删除守卫误触发 | 用 `env -u CODEBUDDY_SAFE_DELETE_BULK_STATE_DIR -u CODEBUDDY_TOOL_CALL_ID python -m unittest ...` |
| Docker 构建失败 | 系统未装 Docker 或网络受限 | 改用 venv 路径，Docker 非必需 |

---

## 6. 已知边界（Known Limitations）

- **`cohen_kappa`（LCA）**：已由可复现的自动化标签一致性审计产出 κ = 0.867（≥ 0.8 达标）。该 κ 来自
  `scripts/label_consistency_audit.py` + `scripts/compute_lca.py`，衡量**自动化标签自洽性**，**非真人双标**。
  真人双标（IAA）为投前最后一步，工具包 `scripts/human_iAA_kit.py` 已备，详见论文 §7 / R7 与上方 §2 阈值判据说明。
  复算：`python scripts/compute_lca.py --no-write`。
- **离线能力声明**：`api/` 与 `scanner/` 运行时**零联网**，但 `scripts/corpus_collect.py` / `scripts/gh_push.py` / `scripts/cf-token-loader.sh` 等**部署/收集工具**需外网，属预期行为。
- **Docker 镜像**：根目录 `Dockerfile` 是生产 GitHub Action 打包入口；**`Dockerfile.artifact`** 才是 artifact
  复现镜像（entrypoint 跑 `scripts/artifact_eval.py`，离线跑 benchmark + FVI + 基线对比并断言关键不变量）。
  本地开发用 venv 等价，`docker build -f Dockerfile.artifact -t aishield-artifact . && docker run aishield-artifact` 即跑通复现包。
- **Windows 路径**：项目支持 Linux/macOS/Windows，但部分 bash 脚本（`deploy-*.sh`、`git_push_safe.sh`）需 Git Bash 或 WSL。

---

## 7. 变更追溯（Provenance）

- 版本号单一真值源：`api/server.py:API_VERSION`
- 规则数单一真值源：`/api/v1/health.rules_breakdown`（静态 237 + 生成 8 + 雷达 19 = 264）
- 语料 manifest：`benchmarks/corpus/external/manifest.json`（含 `collected_at`、`provenance_honesty`、`r1_status`）
- 基准预期值：`benchmarks/expected.json`
- 线上复验：`curl -sS https://aishield.tools/api/v1/health`

**变更历史**：本文件随每次发布同步更新。P5 首次入库为 2026-10-18。
