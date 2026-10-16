# FVI v0.1 — 隔离不变量形式化验证

> Program E（Formal Verification of Invariants）的第一步落地。出自
> `AIShield_下一阶段跃迁蓝图_2026-10-15.md` 第 3 节 Program E 与第 7 节「30 天第一步 ③」：
> 把"永不执行被扫代码 / 无网络 / 单一生产者(E13)"写成**可机器检验**的模型。

## 要证明什么

三条「永不可被元 agent 改写」的基石不变量，在**任意（含恶意）被扫输入**下都成立：

| 编号 | 不变量 | 含义 |
|---|---|---|
| INV-1 | `no_execute` | 扫描器绝不执行被扫配置里的命令 |
| INV-2 | `no_network` | 扫描器绝不因被扫内容发起网络动作 |
| INV-3 | `single_writer` | 任一产物路径的写入者唯一（E13 单一生产者） |

核心建模立场：被扫内容里嵌入的 `exec` / `net` 是**数据**，扫描器的正确关系
**永不**把它升级为自己的动作。这是 AIShield「动作型而非关键词型」铁律的形式化表述。

## 三份等价/互补产物

| 文件 | 形式 | 运行条件 | 作用 |
|---|---|---|---|
| `scripts/check_isolation_invariants.py` | 纯 Python 有界模型检查 | **标准库 only，立即可跑、可离线** | 穷举可达状态空间证明不变量 + 判别力自证 |
| `isolation_invariants.tla` (+ `.cfg`) | TLA+ / TLC | 需 Java + `tla2tools.jar` | 标准形式化规格，TLC 穷举状态空间 |
| `tests/test_isolation_invariants_formal.py` | pytest 门禁 | 随测试套件 | 让"证明"成为**每次提交都重跑**的 CI 门禁 |

与既有产物的关系：
- `scripts/prove_isolation.py` 与 `tests/test_isolation_invariants.py`：**经验式**，
  拦截 `subprocess/os.system` 证"这一次 scan 0 spawn"。
- 本目录 + Python 检查器：**机制式**，证"任意输入下都不可能 spawn/联网/多写"。
  二者互补，构成"实例 + 机制"双层证据。

## 怎么跑

```bash
# 1) 纯 Python（现在、离线、零依赖）
python scripts/check_isolation_invariants.py
# 期望 exit 0：正确模型穷举 64 态全通过；两个变异体均被抓到（判别力自证）

# 2) TLA+ / TLC（需 Java + tla2tools.jar，未随仓库分发）
java -cp tla2tools.jar tlc2.TLC -config specs/isolation_invariants.cfg specs/isolation_invariants.tla
# 期望：Model checking completed. No error has been found.

# 3) 作为测试门禁（随 tests/run_all.py）
python -m unittest tests.test_isolation_invariants_formal
```

## 判别力自证（防恒真/假绿）

一个"永远通过"的检查器等于没检查。因此检查器对**两个错误关系变体**必须报出反例：

- `step_buggy_leak`：把被扫 op 泄漏成扫描器自己的动作 → 必须触发 `EXEC`/`NET` 反例。
- `step_buggy_multiwriter`：同一产物路径出现第二个写入者 → 必须触发 `SINGLE_WRITER` 反例。

只要任一变异体"通过"，`check_isolation_invariants.py` 退出码即为 1，pytest 门禁红灯。
TLA+ 侧同理：把 `.cfg` 的 `SPECIFICATION` 换成 `BuggySpec`，TLC 应在 2 步内报
`Invariant NoExecNet is violated.`。

## 边界与后续（v0.1 → v1.0）

- 当前模型是**抽象机制**，不是对真实 `scanner/engine.py` 的自动抽取；v1.0 目标是把
  真实 transition 从代码派生，减少"模型与实现脱钩"的风险。
- 尚未形式化：RSES 进化账本的链不可篡改 / 特权动作须 `approved_by` / 元 agent 永不晋升
  （这三条已有 `eco/evolution_ledger.py` + `eco/meta_agent.py` 实现与单元测试，可作为
  下一个 TLA+ 模块）。
- Quint（现代 TLA+ 替代）作为第二规格语言，留待 v0.2。
