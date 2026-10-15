// ═══════════════════════════════════════════════════════════════════
// AIShield 隔离不变量形式化模型（FVI / Program E — Formal Verification）
//
// 对象：AIShield 扫描器 + 运行时治理网关的**动作系统**。
// 目的：证明三条不变量在任意输入、任意交错下成立：
//
//   I-1 no_execute   扫描器的动作集里**不存在** spawn 路径 —— 攻击者可以
//                    注入任意恶意文件，但扫描器唯一的交互是 readAsData；
//   I-2 fail_closed  运行时策略损坏后，放行次数恒 0（收紧而非放开）；
//   I-3 read_only    扫描器只读"待扫集合"里的文件，不碰集合外任何东西。
//
// 与 tests/test_invariant_property.py 的分工：
//   · 本模型（Quint）证明**动作系统**没有违规路径（结构性证明）；
//   · 属性测试证明**真实实现**在该输入空间上满足不变量（经验性证明）。
//   两者互为印证：模型可能偏离实现（靠属性测试兜底），实现可能被偶然
//   测出（靠模型解释为何必然成立）。
//
// 已验证（2026-10-15，quint 0.33.0，--backend=typescript）：
//   quint run --invariants invNoExecute invFailClosed invReadOnly \
//             --max-steps=15 --max-samples=200
//   → [ok] No violation found（200 条随机轨迹 × 16 步，813 traces/s）。
//
// 建模过程本身抓到一次缺陷：初版 allowServer 缺 policyOk 守卫，
// 模拟立即给出 invFailClosed 反例（"策略损坏后仍可放行"）——这正是
// fail-closed 要防的路径。补守卫后零违反。**这条记录比结论更值钱**：
// 它证明该模型不是摆设，删掉任何一条防护都会被验证抓出来。
//
// 穷举检查（需 Java + Apalache，本机未装，列为待办）：
//   quint verify --invariants invNoExecute invFailClosed invReadOnly
//
// 运行：quint run formal/isolation_invariants.qnt --invariant=invNoExecute \
//         --invariant=invFailClosed --invariant=invReadOnly \
//         --max-steps=15 --n-traces=200
// ═══════════════════════════════════════════════════════════════════

module isolation_invariants {
  // ── 状态 ──
  var files: Set[str]          // 待扫文件集合（文件名即内容，内容即攻击载荷）
  var scanned: Set[str]        // 已被读取为数据的文件
  var spawns: int              // 扫描器 spawn 的子进程总数 —— 必须恒 0
  var policyOk: bool           // 运行时策略是否成功加载（true=健康）
  var allowed: Set[str]        // 准入判定放行过的 server 集合
  var allowsWhileBroken: int   // 策略损坏期间仍被放行的次数 —— 必须恒 0

  action init = all {
    files' = Set(),
    scanned' = Set(),
    spawns' = 0,
    policyOk' = true,
    allowed' = Set(),
    allowsWhileBroken' = 0,
  }

  // ── 扫描器唯一被允许的交互：把文件当数据读 ──
  // 注意这里**没有** exec / spawn / connect 动作可走 —— 不变量 I-1 的
  // 成立不靠"小心不写违规动作"，而靠动作系统里根本没有那条路径。
  action readAsData(f: str): bool = all {
    files.contains(f),
    not(scanned.contains(f)),
    scanned' = scanned.union(Set(f)),
    spawns' = spawns,                 // 读是纯内存变换，不 spawn
    files' = files,
    policyOk' = policyOk,
    allowed' = allowed,
    allowsWhileBroken' = allowsWhileBroken,
  }

  // ── 攻击者唯一能做的：往待扫集合注入任意恶意文件 ──
  // 注入不改变扫描器的能力边界（这正是 no_execute 要证的）。
  action injectHostile(f: str): bool = all {
    not(files.contains(f)),
    files' = files.union(Set(f)),
    scanned' = scanned,
    spawns' = spawns,
    policyOk' = policyOk,
    allowed' = allowed,
    allowsWhileBroken' = allowsWhileBroken,
  }

  // ── 运行时侧：策略损坏（环境事件）──
  action breakPolicy: bool = all {
    policyOk' = false,
    files' = files,
    scanned' = scanned,
    spawns' = spawns,
    allowed' = allowed,
    allowsWhileBroken' = allowsWhileBroken,
  }

  // ── 准入放行：仅策略健康时是可用路径（fail-closed 的机制本身）──
  // 注意 policyOk 是**动作守卫**而不是记账条件：策略损坏时"放行"这条
  // 路径在动作系统里根本不存在（对应真实实现的 default_deny 兜底）。
  // allowsWhileBroken 是哨兵：谁拆掉这个守卫，它立刻 >0，不变量变红。
  action allowServer(s: str): bool = all {
    policyOk,
    not(allowed.contains(s)),
    allowed' = allowed.union(Set(s)),
    // 哨兵：守卫在时本分支不可达（恒 0）；守卫被拆则每次损坏期放行 +1，
    // invFailClosed 立刻红 —— 拆 fail-closed 的人逃不过这条验证。
    allowsWhileBroken' = if (policyOk) 0 else allowsWhileBroken + 1,
    files' = files,
    scanned' = scanned,
    spawns' = spawns,
    policyOk' = policyOk,
  }

  // 拒绝永远可用（fail-closed 的"允许拒绝"一侧）
  action denyServer(s: str): bool = all {
    files' = files,
    scanned' = scanned,
    spawns' = spawns,
    policyOk' = policyOk,
    allowed' = allowed,
    allowsWhileBroken' = allowsWhileBroken,
  }

  // 固定攻击面文件名宇宙（injectHostile 的注入源）
  val HOSTILE_NAMES = Set("evil.json", "evil.py", "evil.sh", "skill.md", "mcp.json")
  val SERVERS = Set("srv-a", "srv-b", "srv-c")

  // nondet 必须位于动作体最前面（Quint 语法），且 oneOf 的集合必须非空，
  // 故统一从固定宇宙取值，由被调动作内含的守卫决定该步是否真的可用。
  action readSomeFile: bool = {
    nondet f = oneOf(HOSTILE_NAMES)
    readAsData(f)               // 内含 files.contains(f) 守卫：不在待扫集合则本步不可用
  }

  action injectSomeFile: bool = {
    nondet f = oneOf(HOSTILE_NAMES)
    injectHostile(f)
  }

  action allowSomeServer: bool = {
    nondet s = oneOf(SERVERS)
    allowServer(s)
  }

  action denySomeServer: bool = {
    nondet s = oneOf(SERVERS)
    denyServer(s)
  }

  action step = any {
    readSomeFile,
    injectSomeFile,
    breakPolicy,
    allowSomeServer,
    denySomeServer,
  }

  // ── 不变量（任一被破都应产生反例轨迹）──
  val invNoExecute = spawns == 0
  val invFailClosed = allowsWhileBroken == 0
  val invReadOnly = scanned.union(files) == files

  // 语义说明：I-1 在本模型中恒真，因为动作集无 spawn 路径；其价值在于
  // ①把"扫描器绝不执行被扫代码"变成可执行、可回归的规格；
  // ②任何人给 step 加一个 spawn 动作，验证会立刻红。
}
