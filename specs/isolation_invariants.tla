---------------------------- MODULE isolation_invariants ----------------------------
(* FVI v0.1 — AIShield 隔离不变量形式化规格（TLA+ / TLC）
 *
 * 证明三条「永不可被元 agent 改写」的基石不变量在**任意（含恶意）被扫输入**下成立：
 *   INV-1  NoExecNet   : 扫描器绝不执行被扫配置里的命令、绝不因被扫内容发起网络动作。
 *   INV-3  SingleWriter: 任一产物路径的写入者唯一（单一生产者，对应 E13）。
 *
 * 与 scripts/check_isolation_invariants.py（纯 Python 有界模型检查，可离线跑）
 * 是同一模型的两种表述；与 scripts/prove_isolation.py（运行时拦截 spawn 自证）互补。
 *
 * 运行（需 Java + TLC，tla2tools.jar）：
 *   java -cp tla2tools.jar tlc2.TLC -config isolation_invariants.cfg isolation_invariants.tla
 * 期望：Model checking completed. No error has been found.
 *)

EXTENDS Naturals, Sequences, FiniteSets

OPS     == {"exec", "net"}
WRITERS == {"scanner"}

Artifacts == {
    "package.json#postinstall",
    "tool.py#os.system",
    "tool.py#subprocess.call",
    "skill.md#os.system",
    "mcp_config.json#bash -c",
    "benign_readme.md"
}

(* 攻击者在产物里嵌入、试图诱导扫描器执行的 op 集合 —— 这是**被扫内容的数据**，
   不是扫描器自己的动作。正确关系永不把它升级为 performed。 *)
AdversaryRequests(a) ==
    CASE a = "package.json#postinstall"  -> {"exec", "net"}
      [] a = "tool.py#os.system"         -> {"exec"}
      [] a = "tool.py#subprocess.call"   -> {"exec"}
      [] a = "skill.md#os.system"        -> {"exec", "net"}
      [] a = "mcp_config.json#bash -c"   -> {"exec", "net"}
      [] OTHER                           -> {}

FindingPath(a) == "findings/" \o a
FindingPaths == { FindingPath(a) : a \in Artifacts }

VARIABLES pending, performed, writers
vars == <<pending, performed, writers>>

Init ==
    /\ pending  = Artifacts
    /\ performed = {}
    /\ writers  = [p \in FindingPaths |-> {}]

(* 正确扫描器关系：处理产物 = 只读 + 由**唯一**写入者 scanner 写 finding。
   AdversaryRequests(a) 全程只是数据，绝不进入 performed。 *)
Scan(a) ==
    /\ a \in pending
    /\ pending'  = pending \ {a}
    /\ performed' = performed
                       \cup { [kind |-> "read",  target |-> a] }
                       \cup { [kind |-> "write", target |-> FindingPath(a)] }
    /\ writers'  = [writers EXCEPT ![FindingPath(a)] = @ \cup {"scanner"}]

Next == \E a \in Artifacts : Scan(a)

(* ---- 安全不变量（要被证明的性质）---- *)
NoExecNet == \A act \in performed : act.kind \notin {"exec", "net"}
SingleWriter == \A p \in DOMAIN writers : writers[p] \subseteq {"scanner"}
TypeOK ==
    /\ performed \subseteq [kind : {"read", "write"}, target : Artifacts \cup FindingPaths]
    /\ \A p \in DOMAIN writers : writers[p] \subseteq WRITERS

Spec == Init /\ [][Next]_vars

(* ---- 反例规格（错误关系）：把被扫 op 泄漏为扫描器自己的动作 ----
   用于证明"若关系写错，TLC 会在 2 步内报 NoExecNet 反例"（判别力自证）。
   把下面 Next 换成 BuggyNext 后运行，TLC 应报告 Invariant NoExecNet is violated。 *)
BuggyScan(a) ==
    /\ a \in pending
    /\ pending'  = pending \ {a}
    /\ performed' = performed
                       \cup { [kind |-> "read",  target |-> a] }
                       \cup { [kind |-> "write", target |-> FindingPath(a)] }
                       \cup { [kind |-> o, target |-> a] : o \in AdversaryRequests(a) }
    /\ writers'  = [writers EXCEPT ![FindingPath(a)] = @ \cup {"scanner"}]
BuggyNext == \E a \in Artifacts : BuggyScan(a)
BuggySpec == Init /\ [][BuggyNext]_vars

=====================================================================================
