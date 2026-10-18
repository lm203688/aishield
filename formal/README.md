# formal/ — 不变量形式化验证（FVI / Program E）

本目录放 AIShield 核心不变量的**形式化模型**。目标是蓝图 §3 Program E：
把"永不执行被扫代码 / fail-closed / 单一生产者 / 只读输入 / 完备性"从脚本断言
升级为**机器可检验的规格**，并让"证明"成为可复跑、可回归的工程产物。

## 文件

| 文件 | 内容 | 状态 |
|---|---|---|
| `isolation_invariants.qnt` | Quint 模型：no_execute / fail_closed / read_only 三不变量 | ✅ 已验证（200 轨迹 × 16 步零违反，随机模拟） |
| `scripts/check_isolation_invariants.py` | Python 有界模型检查（**穷举可达态 + 完备性论证 + 4 变异体**） | ✅ **已穷举**（64 可达态全枚举，R4 达成） |
| `scripts/run_fvi_gate.py` | FVI 门禁统一驱动（正确性模型 + 变异体判别力） | ✅ CI 入口 |

## 复跑

```bash
# R4 主证明（穷举 + 完备性 + 变异套件）—— 零依赖、离线、确定性
python scripts/run_fvi_gate.py

# Quint 随机模拟（独立交叉验证，非穷举）
node node_modules/@informalsystems/quint/dist/src/cli.js run \
  formal/isolation_invariants.qnt \
  --invariants invNoExecute invFailClosed invReadOnly \
  --max-steps=15 --max-samples=200 --backend=typescript
```

`quint run` 必须显式 `--backend=typescript`：默认 rust 后端会尝试联网下载二进制，
离线环境直接超时（2026-10-15 实测 `UND_ERR_CONNECT_TIMEOUT`）。

## 五不变量分层（INV-1 ~ INV-5）

| 编号 | 不变量 | 含义 | 来源 |
|---|---|---|---|
| INV-1 | `no_execute` | 永不执行被扫代码 | scanner 核心铁律 |
| INV-2 | `no_network` | 扫描过程零网络外联 | 离线能力声明 |
| INV-3 | `single_writer` | 产物单一写入者（E13） | 防并发/越权写 |
| INV-4 | `read_only_input` | 只读被扫输入，绝不写回 | 防污化被扫文件 |
| INV-5 | `completeness` | 每个输入都被处理（无漏处理） | 终态检查兜底 |

## R4 如何被满足（穷举 + 完备性，不依赖 Apalache）

`scripts/check_isolation_invariants.py` 用纯 Python 在干净 checkout 上做**有界模型检查**：

1. **穷举可达态**：`explore_with_report()` 从初始态 BFS 展开动作系统，队列排空即
   `termination="exhausted"`（到达不动点 = 全部可达态已枚举）。实测 `reachable_states=64`、
   `coverage=1.0`、`complete=true` —— 这是"穷举"的硬定义，不是随机采样。
2. **完备性论证**：`completeness_argument()` 给出命题链（命题 1–5），由构造证明
   `|reachable| = 2^6 = 64`；再交叉校验 `explore` 实际枚举数 == 论证上界，二者一致
   才放行。论证与实测双重钉死"没漏掉任何可达态"。
3. **判别力自证（防假绿）**：`mutation_suite()` 注入 4 个缺陷变异体，**全部必须被
   抓到**否则门禁失败——
   - M1 `leak-exec-net`：被扫 op 泄漏为动作（INV-1/2 违反）
   - M2 `secondary-writer`：多写入者（INV-3 / E13 违反）
   - M3 `readonly-violation`：扫描器写回被扫路径（INV-4 违反）
   - M4 `partial-processing`：奇数序号产物静默跳过（INV-5 违反）
4. **不变量判定**：`violated_invariants()` 对 INV-1~INV-4 逐条检查；INV-5（完备性）
   由 `completeness_check()` 单独做终态检查（漏处理在中间态看不出，必须在终态判定）。

> 关键结论：**R4（形式化穷举 + 完备性）已由 Python 层达成**，无需安装 Java/Apalache。
> Quint 仅作为独立随机模拟交叉验证，其"非穷举"现状**不再阻塞 R4**。

## 三层防线的分工

1. **Python 有界模型检查**（`scripts/check_isolation_invariants.py`，由
   `scripts/run_fvi_gate.py` 统一驱动）：**穷举**可达状态空间（64 态），并附完备性
   论证。这是 R4 的主证明，零依赖、离线、确定性。
2. **Quint 模型**（本目录）：随机模拟（200 轨迹 × 16 步）作为**独立交叉验证**。
   任何人往 `step` 里加一个 spawn 动作或拆掉 fail-closed 守卫，模拟立刻红。穷举需
   `quint verify`（Apalache + Java），列为增强项而非阻塞项。
3. **Hypothesis 属性测试**（`tests/test_invariant_property.py`）：在**真实实现**上
   跑随机语料，证不变量在输入空间上成立。经验性证明；模型可能偏离实现，由它兜底。
4. **固定语料回归**（`tests/test_isolation_invariants.py`）：钉具体攻击场景，防止
   性质测试通过而具体场景失效。

## Python ↔ Quint 等价映射

`scripts/check_isolation_invariants.py` 是 Quint 规格的可离线重述，一一对应：

| Quint 概念            | Python 实现                                        |
|----------------------|---------------------------------------------------|
| `var state`          | `class State`（files / spawned / net_calls …）     |
| `action step`        | `step_correct(s, a)`                               |
| 注入 spawn 的缺陷动作 | `step_buggy_leak` / `step_buggy_multiwriter` / `step_buggy_writes_scanned` / `step_buggy_skip` |
| `invariant`          | `violated_invariants(s)` → `["EXEC","NET",…]`      |
| `run` 随机/穷举轨迹  | `explore_with_report()` 穷举可达状态（exhausted 终止）|

判别力自证（防"检查器恒真=假绿"）在两层都做：正确模型零反例，**四个缺陷变异体
（M1–M4）必须被抓到**，否则门禁失败。CI 单一入口：`python scripts/run_fvi_gate.py`。

## 已知边界（诚实声明）

- **R4 已达成**：Python 层已穷举 64 可达态并附完备性论证，不依赖 Apalache/Java。
- Quint `quint run` 是**模拟**（随机轨迹），不是穷举模型检查。穷举需
  `quint verify`（Apalache 后端，要 Java）——列为增强项，非 R4 阻塞。
- 模型覆盖的是**动作系统**；真实实现还靠属性测试与回归测试把守。
  三层各自能失效，叠加才构成"可证明安全"的工程近似。

## 待办（增强项，非阻塞）

- [ ] 装 Java + Apalache 后跑 `quint verify --invariants ...`（与 Python 穷举互为独立证据）
- [ ] CI 集成：node 环境装 quint 后把上面命令挂进验证 job（Python 层已是主门禁）
