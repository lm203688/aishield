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
2. **Hypothesis 属性测试**（`tests/test_invariant_property.py`）：在**真实
   实现**上跑随机语料，证不变量在输入空间上成立。经验性证明；
   模型可能偏离实现，由它兜底。
3. **固定语料回归**（`tests/test_isolation_invariants.py`）：钉具体攻击
   场景，防止性质测试通过而具体场景失效。

## 已知边界（诚实声明）

- `quint run` 是**模拟**（随机轨迹），不是穷举模型检查。穷举需
  `quint verify`（Apalache 后端，要 Java）——本机未装 Java，列为待办。
- 模型覆盖的是**动作系统**；真实实现还靠属性测试与回归测试把守。
  三层各自能失效，叠加才构成"可证明安全"的工程近似。

## 待办

- [ ] 装 Java + Apalache 后跑 `quint verify --invariants ...`（有界穷举）
- [ ] 单一生产者（E13）不变量进模型
- [ ] CI 集成：node 环境装 quint 后把上面命令挂进验证 job
