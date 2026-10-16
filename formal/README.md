# formal/ — 不变量形式化验证（FVI / Program E）

本目录放 AIShield 核心不变量的**形式化模型**。目标是蓝图 §3 Program E：
把"永不执行被扫代码 / fail-closed / 单一生产者"从脚本断言升级为
**机器可检验的规格**，并让"证明"成为可复跑、可回归的工程产物。

## 文件

| 文件 | 内容 | 状态 |
|---|---|---|
| `isolation_invariants.qnt` | Quint 模型：no_execute / fail_closed / read_only 三不变量 | ✅ 已验证（200 轨迹 × 16 步零违反） |

## 复跑（本机已装 quint 0.33.0）

```bash
node node_modules/@informalsystems/quint/dist/src/cli.js run \
  formal/isolation_invariants.qnt \
  --invariants invNoExecute invFailClosed invReadOnly \
  --max-steps=15 --max-samples=200 --backend=typescript
```

必须显式 `--backend=typescript`：默认的 rust 后端会尝试联网下载二进制，
离线环境直接超时（2026-10-15 实测 UND_ERR_CONNECT_TIMEOUT）。

## 三层防线的分工

1. **Quint 模型**（本目录）：证明动作系统**没有**违规路径。结构性证明；
   任何人往 `step` 里加一个 spawn 动作或拆掉 fail-closed 守卫，验证立刻红。
2. **Python 有界模型检查**（`scripts/check_isolation_invariants.py`，由
   `scripts/run_fvi_gate.py` 统一驱动）：Quint 规格的**纯 Python 重述**，
   在干净 checkout 上穷举可达状态空间。两者语义等价（见下），互相兜底——
   Quint 因环境（Java/Apalache）跑不了时，Python 这层仍能独立证明。
3. **Hypothesis 属性测试**（`tests/test_invariant_property.py`）：在**真实
   实现**上跑随机语料，证不变量在输入空间上成立。经验性证明；
   模型可能偏离实现，由它兜底。
4. **固定语料回归**（`tests/test_isolation_invariants.py`）：钉具体攻击
   场景，防止性质测试通过而具体场景失效。

## Python ↔ Quint 等价映射

`scripts/check_isolation_invariants.py` 是 Quint 规格的可离线重述，一一对应：

| Quint 概念            | Python 实现                                        |
|----------------------|---------------------------------------------------|
| `var state`          | `class State`（files / spawned / net_calls …）     |
| `action step`        | `step_correct(s, a)`                               |
| 注入 spawn 的缺陷动作 | `step_buggy_leak` / `step_buggy_multiwriter`       |
| `invariant`          | `violated_invariants(s)` → `["EXEC","NET",…]`      |
| `run` 随机/穷举轨迹  | `explore(step, bound)` 穷举可达状态                |

判别力自证（防"检查器恒真=假绿"）在两层都做：正确模型零反例，**两个缺陷
变异体必须被抓到**，否则门禁失败。CI 单一入口：`python scripts/run_fvi_gate.py`。

## 已知边界（诚实声明）

- `quint run` 是**模拟**（随机轨迹），不是穷举模型检查。穷举需
  `quint verify`（Apalache 后端，要 Java）——本机未装 Java，列为待办。
- 模型覆盖的是**动作系统**；真实实现还靠属性测试与回归测试把守。
  三层各自能失效，叠加才构成"可证明安全"的工程近似。

## 待办

- [ ] 装 Java + Apalache 后跑 `quint verify --invariants ...`（有界穷举）
- [ ] 单一生产者（E13）不变量进模型
- [ ] CI 集成：node 环境装 quint 后把上面命令挂进验证 job
