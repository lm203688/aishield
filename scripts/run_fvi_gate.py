# -*- coding: utf-8 -*-
"""
scripts/run_fvi_gate.py — FVI（Program E）CI 门禁单一入口 v0.1
=================================================================

蓝图 §3 Program E「把不变量写成机器可检验证明」。本项目对核心隔离不变量已有
**三层证据**（见 formal/README.md）：

  1. Quint 动作系统模型（formal/isolation_invariants.qnt）
  2. Python 有界模型检查（scripts/check_isolation_invariants.py）
  3. Hypothesis 属性测试 + 固定语料回归（tests/test_invariant_property.py 等）

CI 需要的是"一条命令跑完隔离证明并给退出码"。unittest 那层在 `python
tests/run_all.py` 里已经覆盖，但隔离证明是安全铁律，值得有**独立、可单独调用**
的入口——本脚本就是它：直接 import 有界模型检查器，跑"正确模型零反例 +
两个缺陷变异体必须被抓（判别力自证）"，再顺带跑 B4 经验式自检
（scripts/prove_isolation.py）作为第二道防线。任一不过 → 退出码非 0。

Python ↔ Quint 等价映射（为什么两套都成立）
-------------------------------------------
有界模型检查器是 Quint 规格的**纯 Python 重述**，一一对应：

| Quint 概念            | Python 实现（check_isolation_invariants.py）      |
|----------------------|----------------------------------------------|
| `var state`          | `class State`（files / spawned / net_calls …）|
| `action step`        | `step_correct(s, a)`                         |
| 注入 spawn 的缺陷动作 | `step_buggy_leak(s, a)` / `step_buggy_multiwriter` |
| `invariant`          | `violated_invariants(s)` → ["EXEC","NET",…]  |
| `run` 随机轨迹模拟    | `explore(step, bound)` 穷举可达状态          |

两者语义一致：Quint 用 Apalache/模拟证"无违规轨迹"，Python 用同一套
状态转移 + 不变量判定在干净 checkout 上穷举可达空间。哪套都可能在实现漂移时
先红，互相兜底。
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import Tuple

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _run_model_check() -> Tuple[int, str]:
    """
    跑有界模型检查：正确模型零反例 + 两缺陷变异体必须被抓（判别力自证）。

    返回 (rc, summary)：rc=0 通过，rc=1 失效。
    """
    import scripts.check_isolation_invariants as fvi

    lines = []
    ok = True

    explored, cex, violations = fvi.explore(fvi.step_correct)
    if cex or violations:
        ok = False
        lines.append(f"[FAIL] 正确模型出现反例（探索 {explored} 态）：{violations}")
    else:
        lines.append(f"[PASS] 正确模型：探索 {explored} 态，0 反例 "
                     f"(>= 恶意语料 {len(fvi.HOSTILE_CORPUS)})")

    for name in ("step_buggy_leak", "step_buggy_multiwriter"):
        step = getattr(fvi, name)
        _, cex_m, viol_m = fvi.explore(step)
        caught = bool(cex_m or viol_m)
        if not caught:
            ok = False
            lines.append(f"[FAIL] 判别力缺失：{name} 未被抓到 → 检查器可能恒真（假绿）")
        else:
            lines.append(f"[PASS] 判别力：{name} 被抓到（{viol_m or 'trace 反例'}）")

    return (0 if ok else 1, "\n".join(lines))


def _run_b4_self_check() -> Tuple[int, str]:
    """顺带跑 B4 经验式隔离自检（scripts/prove_isolation.py）作第二道防线。"""
    script = os.path.join(_ROOT, "scripts", "prove_isolation.py")
    if not os.path.exists(script):
        return 0, "[SKIP] prove_isolation.py 不存在"
    r = subprocess.run([sys.executable, script],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return (1, "[FAIL] prove_isolation.py 退出码 %d\n%s"
                % (r.returncode, (r.stdout + r.stderr)[-800:]))
    return (0, "[PASS] B4 隔离自检（prove_isolation.py）退出码 0")


def run_gate() -> int:
    """FVI 门禁总入口。任一证据层失效即非零退出。"""
    print("=" * 60)
    print("FVI (Program E) — 隔离不变量形式化门禁")
    print("=" * 60)

    rc_mc, summary_mc = _run_model_check()
    print("\n--- 有界模型检查 ---")
    print(summary_mc)

    rc_b4, summary_b4 = _run_b4_self_check()
    print("\n--- B4 经验式自检 ---")
    print(summary_b4)

    overall = rc_mc or rc_b4
    print("\n" + "=" * 60)
    if overall == 0:
        print("FVI GATE: PASS — 隔离不变量证明通过（模型检查 + B4 自检）")
    else:
        print("FVI GATE: FAIL — 隔离证明未通过，隔离铁律可能被破坏")
    print("=" * 60)
    return overall


def main() -> int:
    return run_gate()


if __name__ == "__main__":
    sys.exit(main())
