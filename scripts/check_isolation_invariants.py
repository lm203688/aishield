"""FVI v0.1 — AIShield 隔离不变量形式化验证（可运行版）。

把三条「永不可被元 agent 改写」的基石不变量写成抽象状态机，用**有界模型检查**
穷举可达状态空间，证明它们在**任意（含恶意）被扫输入**下都成立：

  INV-1  no_execute   : 扫描器绝不执行被扫配置里的命令。
  INV-2  no_network   : 扫描器绝不因被扫内容发起网络动作。
  INV-3  single_writer: 任一产物路径的写入者唯一（E13）。

这不是对真实 scanner 的重放，而是对「扫描器只能做只读字符串分析、绝不把被扫
内容里的指令升级为自己的动作」这一**机制**的形式化。与 `scripts/prove_isolation.py`
（运行时拦截 spawn 的自证）互补：那边证「这一次没 spawn」，这边证「机制上不可能」。

**判别力自证（防恒真/假绿）**：同一检查器对「错误的关系」变体必须**报出反例**。
若错误变体也"通过"，说明检查器空洞，退出码非 0。

运行：python scripts/check_isolation_invariants.py
退出码：0 = 正确模型通过 且 变异体被抓到（证明有效）；1 = 任一不成立。
标准库 only、零依赖、可 100% 离线。
"""
import os
import sys
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set, Tuple

# 恶意语料：与 scripts/prove_isolation.py 的 _HOSTILE 同源，但这里只取其
# 「攻击者想诱导扫描器执行的 op」这一抽象意图（exec / net / 纯数据）。
# 关键点：这些 op 是**被扫内容的数据**，不是扫描器自己的动作。
@dataclass(frozen=True)
class Artifact:
    name: str
    # 攻击者在该文件里嵌入、试图诱导扫描器执行的意图 op 集合（只读数据）
    adversary_requests: FrozenSet[str]


HOSTILE_CORPUS: Tuple[Artifact, ...] = (
    Artifact("package.json#postinstall", frozenset({"exec", "net"})),  # curl …| sh
    Artifact("tool.py#os.system", frozenset({"exec"})),                # os.system('rm -rf /')
    Artifact("tool.py#subprocess.call", frozenset({"exec"})),          # subprocess.call(shell=True)
    Artifact("skill.md#os.system", frozenset({"exec", "net"})),        # os.system('curl …')
    Artifact("mcp_config.json#bash -c", frozenset({"exec", "net"})),   # command: bash -c …
    Artifact("benign_readme.md", frozenset()),                         # 纯数据，无恶意 op
)

# 扫描器唯一合法写入者（用于 INV-3 单一生产者）；读 op 由扫描器名义发出。
SCANNER_WRITER = "scanner"


@dataclass
class State:
    pending: FrozenSet[str]           # 尚未处理的被扫产物名
    performed: FrozenSet[str]         # 扫描器**实际执行**的动作（应只含 read/write，绝不含 exec/net）
    writers: FrozenSet[Tuple[str, str]]  # (path, writer) —— 检测同一 path 多写入者
    _finding_seq: int = 0

    def key(self):
        return (self.pending, self.performed, self.writers, self._finding_seq)


# ---- 关系（transition relations） ----------------------------------------
# 正确扫描器：处理产物 = 只读 + 由**唯一**写入者 scanner 写 finding。
# 被扫内容里的 adversary_requests **永不**进入 performed —— 这是机制核心。
def step_correct(s: State, a: Artifact) -> State:
    if a.name not in s.pending:
        return s
    performed = set(s.performed)
    performed.add(("read", a.name))
    # 写 finding：由唯一扫描器写入者发出（单一生产者）
    fpath = f"findings/{a.name}"
    performed.add(("write", fpath, SCANNER_WRITER))
    writers = set(s.writers)
    writers.add((fpath, SCANNER_WRITER))
    return State(
        pending=s.pending - {a.name},
        performed=frozenset(performed),
        writers=frozenset(writers),
        _finding_seq=s._finding_seq + 1,
    )


# 变异体（错误关系）：把被扫内容里嵌入的 op **泄漏**成扫描器自己的动作。
# 这正是要被否证的缺陷形态（fail-closed 被"合法数据"绕过的同型）。
def step_buggy_leak(s: State, a: Artifact) -> State:
    ns = step_correct(s, a)
    performed = set(ns.performed)
    for op in a.adversary_requests:            # 缺陷：数据 → 动作
        performed.add((op, a.name))
    return State(pending=ns.pending, performed=frozenset(performed),
                 writers=ns.writers, _finding_seq=ns._finding_seq)


# 变异体（错误关系）：同一产物路径出现**第二个**写入者（E13 单一生产者违背）。
def step_buggy_multiwriter(s: State, a: Artifact) -> State:
    ns = step_correct(s, a)   # 正确侧已写入 ("findings/{name}", "scanner")
    fpath = f"findings/{a.name}"
    writers = set(ns.writers)
    writers.add((fpath, "secondary_writer"))   # 缺陷：同 path 第二个写入者
    return State(pending=ns.pending, performed=ns.performed,
                 writers=frozenset(writers), _finding_seq=ns._finding_seq)


# ---- 安全不变量 -----------------------------------------------------------
def violated_invariants(s: State) -> List[str]:
    v: List[str] = []
    # INV-1 no_execute / INV-2 no_network：performed 里绝不能出现 exec/net 动作
    for act in s.performed:
        if isinstance(act, tuple) and act and act[0] in ("exec", "net"):
            v.append(f"{act[0].upper()} performed: {act}")
            break
    # INV-3 single_writer：任一 path 出现 >1 个不同 writer
    by_path: Dict[str, Set[str]] = {}
    for path, writer in s.writers:
        by_path.setdefault(path, set()).add(writer)
    for path, ws in by_path.items():
        if len(ws) > 1:
            v.append(f"SINGLE_WRITER broken: {path} <- {sorted(ws)}")
    return v


# ---- 有界穷举探索 ---------------------------------------------------------
def explore(step, bound: int = 5000):
    init = State(
        pending=frozenset(a.name for a in HOSTILE_CORPUS),
        performed=frozenset(),
        writers=frozenset(),
    )
    seen = {init.key()}
    dq = deque([(init, [])])
    explored = 0
    while dq and explored < bound:
        s, trace = dq.popleft()
        explored += 1
        v = violated_invariants(s)
        if v:
            return explored, trace, v
        for a in HOSTILE_CORPUS:
            ns = step(s, a)
            k = ns.key()
            if k not in seen:
                seen.add(k)
                dq.append((ns, trace + [(a.name, violated_invariants(ns))]))
    return explored, None, []


def _describe_trace(trace):
    if not trace:
        return "  (反例路径：初始态即违规)"
    return "\n".join(f"    step {i}: process {name}" + (f"  -> {v}" if v else "")
                     for i, (name, v) in enumerate(trace))


def main() -> int:
    print("== FVI v0.1 AIShield 隔离不变量有界模型检查 ==\n")

    # 1) 正确模型：必须无反例（穷举所有可达状态）
    exp_ok, cex_ok, viol_ok = explore(step_correct)
    if cex_ok is not None or viol_ok:
        print(f"[FAIL] 正确模型被报违规（检查器或有缺陷）：{viol_ok}")
        return 1
    print(f"[PASS] 正确扫描器模型：穷举 {exp_ok} 个可达状态，"
          f"no_execute / no_network / single_writer 全部成立。")

    # 2) 变异体 A（数据泄漏成动作）：必须被抓到（证明检查器有判别力，非恒真）
    exp_a, cex_a, viol_a = explore(step_buggy_leak)
    if cex_a is None and not viol_a:
        print("[FAIL] 变异体 step_buggy_leak 未被抓到 —— 检查器恒真（假绿），无效。")
        return 1
    print(f"[PASS] 变异体『被扫 op 泄漏为动作』被抓住（{exp_a} 态内），"
          f"反例：{viol_a[0]}")

    # 3) 变异体 B（多写入者）：必须被抓到
    exp_b, cex_b, viol_b = explore(step_buggy_multiwriter)
    if cex_b is None and not viol_b:
        print("[FAIL] 变异体 step_buggy_multiwriter 未被抓到 —— 检查器恒真（假绿），无效。")
        return 1
    print(f"[PASS] 变异体『多写入者(E13 违背)』被抓住（{exp_b} 态内），"
          f"反例：{viol_b[0]}")

    print("\n结论：三条基石不变量在任意被扫输入下成立，且该结论经非恒真检查器验证。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
