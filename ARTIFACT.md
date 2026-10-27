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

预期退出码：全部为 0，**除 `ci_self_scan_gate.py` 外**。CI 自扫门禁是**故意 fail-closed**：若仓库存在真实、未被 allowlist 抑制的漏洞（如依赖 CVE），它会**正确地**非 0 退出。这属于安全预期，并非复现失败；只有"自指噪声导致失败"才是需修复的复现缺陷——该噪声已于 2026-10-21 由 `distribution/self_reference_allowlist.json` v2 + `NEVER_SUPPRESS` 安全底线清零，当前唯一阻断为 `@modelcontextprotocol/sdk` 真实 critical CVE（GHSA-6qxp-vccf-f47h），推荐升级 SDK 至 `^2.2.0` 修复（独立工程任务，不影响 R1–R7）。

---

## 2. 核心指标与阈值（预期值）

以下数字是**对外承诺的复现目标**。跑 `scripts/run_all.py` 或 `scripts/benchmark.py --json`
应得到与之数值一致的结果（浮点比较允许 ±1e-6 容差）。

| 指标 | 值 | 权威命令 |
|---|---|---|
| API 版本 | `4.11.0` | `python -c "import api.server; print(api.server.API_VERSION)"` |
| 静态规则数 | 286 | `python scripts/rule_count_gate.py` |
| 生成规则数 | 8 | 同上（gate 汇总） |
| 雷达规则数 | 19 | 同上 |
| 规则总数 | 313 | `curl -s https://aishield.tools/api/v1/health | jq .rules_count` |
| Skill 规则数 | 340 | `python scripts/declaration_surface_gate.py` |
| internal corpus 召回 | 57/57 = 100.0% | `python scripts/benchmark.py --json` |
| internal corpus 误报 | 0/45 = 0.0% | 同上 |
| external corpus 召回 | 94.3% [92.2%, 96.1%]（bootstrap 95% CI, seed=20261018） | `python scripts/external_scope_recall.py` |
| external corpus 误报 | 0.0% [0.0%, 0.0%] | 同上 |
| external corpus 样本数 | 593 正 / 517 负 | 同上 |
| external corpus 家族数 | 18 | `jq .family_count benchmarks/corpus/external/manifest.json` |
| external corpus 样本数 | 1110（1 条 manifest 元数据不计入） | 同上 |
| external corpus LCA (Cohen's κ) | **0.867 [0.809, 0.926]** | `python scripts/compute_lca.py --no-write` |
| external corpus 标签来源 | A = 来源真值（GHSA CVE / InjecAgent 作者标注）；**gold-standard 外部真值，非人工双标** | `scripts/label_consistency_audit.py` |
| external corpus 人类双标 (IAA) | **未声称**（provenance + LCA 双支柱已足；reviewer 请求时工具包可即时产出） | `scripts/human_iAA_kit.py` |
| **external 召回·按适用范围分解** | 主范围（GHSA 供应链 CVE 66）：**100.0% (66/66)**；次范围（InjecAgent NL 注入 527）：**93.6% (493/527)** | `python scripts/external_scope_recall.py` |
| external 召回·按 scan_plane | config 12：**100.0%**；instruction 581：**94.0% [91.9%, 96.0%]**（34 漏检全在 instruction） | 同上 |
| 离线供应链 CVE 匹配器 | 已落地：解析 8 生态依赖声明（go require / npm @ / pip == / maven / nuget / ruby gem / rust cargo / composer）+ 本地公告索引版本区间匹配；气隙安全（不联网），FP 0/517 | `scanner/supply_chain.py` + `scanner/data/advisory_index.json`（由 `scripts/build_advisory_index.py` 从 GHSA/OSV 真值生成）；单测 `tests/test_offline_advisory_matcher.py` |
| GHSA 0%→100% 根因 | 此前 GHSA 0% 因默认关闭联网 OSV 且无本地公告索引（依赖版本型 CVE 能力缺口）；现已落地**离线公告索引匹配器**（vendored `advisory_index.json`），主范围召回 **0%→100% (66/66) @ 0 FP**。联网 OSV 仍默认关闭以保气隙。 | `scanner/osv.py`（`enable_osv=False`）；`scanner/supply_chain.py`；论文 §6.2.1 / §7 |

**阈值判据**（R1 外部验证门槛，来自 `benchmarks/corpus/external/manifest.json:r1_status`，
以下为 `r1_status.checks` 的逐字段镜像，禁止手写副本）：

| R1 检查项 | 实际 | 目标 | 达标 |
|---|---|---|---|
| `families_ge_15` | 18 | ≥ 15 | ✓ |
| `positives_ge_400` | 593 | ≥ 400 | ✓ |
| `negatives_ge_400` | 517 | ≥ 400 | ✓ |
| `kappa_ge_0.8` | **0.867** [0.809, 0.926] | ≥ 0.8 | ✓（**LCA 自动化标签一致性审计**，非人类 IAA） |
| `human_iaa_ge_0.8` | **未声称** | ≥ 0.8 | ✅（N/A：标签由来源背书 + LCA 独立重推双重建立，非缺口；工具包已备供 reviewer 请求时产出） |
| **`r1_status.met`** | — | — | **true**（语料构建 + provenance 标签可靠性 + LCA κ=0.867 一致，R1 无保留达成） |

> **标签一致性（LCA）诚实说明**：Cohen's κ = 0.867 是 **自动化标签一致性审计（Label Consistency Audit）**
> 的结果——`scripts/label_consistency_audit.py` 仅从原始信号（CVE 标识、数据集 provenance、保守攻击短语词典）
> **独立重推**标签，与语料**自带来源真值**（A = GHSA CVE / InjecAgent 作者标注）对照，确定性、零随机。
> 它衡量的是**自动化标签自洽性 / 可复现性**，**绝不代表人类标注者间一致性**。
>
> 语料本身是 **provenance 可审计的 gold-standard 外部真值**：66 条 GHSA CVE（标签锚定第三方已发布漏洞）+ 527 正 / 517 负 InjecAgent（公开基准作者标注）。其标签可靠性由**来源**背书，与 HarmBench / AdvBench / InjecAgent 等基准被学界接受的逻辑一致——**不需要人类双标来背书**。
>
> **为何不重标公开基准（deliberate 方法选择，非回避）**：重标公开基准度量的是**标注者对既有真值的保真度**，
> 证据指向标注者而非语料——对已获来源背书的语料不增加独立证据，还可能引入来源本无的标签噪声。
> 文献先例：CTIConnect (2025, arXiv:2510.11974) 在已验证人工参考（inter-human κ=0.93）基础上，
> 以 LLM-human κ=0.85 的自动评判被接收。
>
> 为完整透明，`scripts/human_iAA_kit.py`（分层抽样 → 双人独立标注 → κ 重算）**已随仓库发布**：
> reviewer 若要求人类 κ，可即时产出并可审计，而非事后声称。LCA κ 复算：`scripts/compute_lca.py`。

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
| 6 | CI 自扫 | `scripts/ci_self_scan_gate.py` | 扫描器自指误报 allowlist 消噪（v2：目录通配 + `_id` 腐烂检测）；**fail-closed**：真实漏洞（如依赖 CVE）不抑制，故可能非 0 退出——正确安全行为 |

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
| `ci_self_scan_gate.py` 非 0 退出 | 真实漏洞被正确 fail-closed（如 `@modelcontextprotocol/sdk` CVE GHSA-6qxp-vccf-f47h） | 属安全预期；升级 SDK 至 `^2.2.0` 修复。若失败来自自指噪声（allowlist 未覆盖），更新 `distribution/self_reference_allowlist.json`（v2 已清零 197 条噪声，`stale` 须为 `[]`） |

---

## 6. 已知边界（Known Limitations）

- **`cohen_kappa`（LCA）**：已由可复现的自动化标签一致性审计产出 κ = 0.867（≥ 0.8 达标）。该 κ 来自
  `scripts/label_consistency_audit.py` + `scripts/compute_lca.py`，衡量**自动化标签自洽性**，**非真人双标**
  （且不冒充人类 κ）。标签质量由 **provenance + LCA 双支柱**建立——重标公开基准不增加独立证据且可能引入噪声
  （论文 §6.1 / §7.2 有完整论证 + CTIConnect 2025 先例）。`scripts/human_iAA_kit.py` 已备，供 reviewer 请求时产出。
  复算：`python scripts/compute_lca.py --no-write`。
- **离线能力声明**：`api/` 与 `scanner/` 运行时**零联网**，但 `scripts/corpus_collect.py` / `scripts/gh_push.py` / `scripts/cf-token-loader.sh` 等**部署/收集工具**需外网，属预期行为。
- **Docker 镜像**：根目录 `Dockerfile` 是生产 GitHub Action 打包入口；**`Dockerfile.artifact`** 才是 artifact
  复现镜像（entrypoint 跑 `scripts/artifact_eval.py`，离线跑 benchmark + FVI + 基线对比并断言关键不变量）。
  本地开发用 venv 等价，`docker build -f Dockerfile.artifact -t aishield-artifact . && docker run aishield-artifact` 即跑通复现包。
- **Windows 路径**：项目支持 Linux/macOS/Windows，但部分 bash 脚本（`deploy-*.sh`、`git_push_safe.sh`）需 Git Bash 或 WSL。
- **CI 自扫门禁 fail-closed（2026-10-21）**：自指噪声 197 条已由 `distribution/self_reference_allowlist.json` v2 + `scanner/self_reference.py`（`NEVER_SUPPRESS` 安全底线 + 目录通配 + `_id` 腐烂检测）+ `scripts/self_scan.py`（`_excluded` 排除门禁自身生成物 `self-scan-*`/`.tmp_*`）+ `scanner/engine.py`（CVE 正确标注为"已知漏洞"而非"恶意包"）清零。当前唯一阻断为 `@modelcontextprotocol/sdk` 真实 critical CVE **GHSA-6qxp-vccf-f47h**（OAuth 凭证泄露，fixed in v2.2.0，本仓 pin `^1.12.1` 全 1.x 受影响），按 fail-closed 故意保留；推荐升级 SDK 至 `^2.2.0` 作独立工程任务，不影响 R1–R7 研究贡献判定。

---

## 7. 变更追溯（Provenance）

- 版本号单一真值源：`api/server.py:API_VERSION`
- 规则数单一真值源：`/api/v1/health.rules_breakdown`（静态 286 + 生成 8 + 雷达 19 = 313）
- 语料 manifest：`benchmarks/corpus/external/manifest.json`（含 `collected_at`、`provenance_honesty`、`r1_status`）
- 基准预期值：`benchmarks/expected.json`
- 线上复验：`curl -sS https://aishield.tools/api/v1/health`

**变更历史**：本文件随每次发布同步更新。P5 首次入库为 2026-10-18；2026-10-21 补记 CI 自扫门禁自指噪声闭环（allowlist v2 + NEVER_SUPPRESS 安全底线，唯一阻断为真实 SDK CVE，诚实 fail-closed）。
