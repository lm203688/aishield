# Agent Computers Need Two Security Planes: Isolation and Content Trust

> Version 1.0 · 2026-08-10 · AIShield Project · https://aishield.tools
> 中文摘要在文末。

## TL;DR

Giving an AI agent its own computer is now a solved infrastructure problem. Cloudflare Sandboxes,
forgevm, E2B, Open Interpreter and Goose all give an agent a shell, a filesystem and a network stack
inside a container or micro-VM.

That solves **blast radius**: what the agent is allowed to touch.

It does not solve **content trust**: whether the MCP servers, skills and tool descriptions the agent
loads *inside* that box should be believed in the first place.

A sandboxed agent that loads a poisoned skill still exfiltrates your data — it just does so from
inside a container, using the credentials you deliberately gave it. Isolation is necessary. It is
not sufficient.

**AIShield is the content-trust plane for agent computers.** It is complementary to every isolation
runtime listed above, not a competitor to any of them.

## The two planes

| | Isolation plane | Content-trust plane |
|---|---|---|
| **Question answered** | What can this agent reach? | Should this agent believe what it just read? |
| **Enforced by** | Container / micro-VM / V8 isolate, egress policy, credential injection | Static analysis of MCP configs, skills, tool descriptions; runtime admission on each call |
| **Typical products** | Cloudflare Sandboxes & Containers, forgevm / agent-forge, E2B, Open Interpreter, Goose | AIShield |
| **Fails against** | Poisoned skill, tool-description injection, hallucinated dependency, rug-pulled MCP server | Kernel escape, resource exhaustion, host compromise |
| **Failure mode if missing** | Agent bug becomes host compromise | Agent behaves "correctly" while executing an attacker's instructions |

Neither plane subsumes the other. An escape-proof sandbox running a malicious skill is a
faithfully-executed attack. A perfectly audited skill running unsandboxed is one dependency bug away
from your home directory.

## Why isolation alone keeps failing

Three properties of agent workloads break the assumption that the sandbox boundary is enough.

**1. The agent has legitimate credentials.** Modern agent runtimes inject secrets at the network
layer so the agent never sees them — Cloudflare's egress proxy does exactly this, and it is good
design. But the requests still go out authenticated. If the instruction to make that request came
from a poisoned tool description, the sandbox happily authenticates the attack.

**2. Markdown is executable.** In the skill ecosystem, `SKILL.md` is not documentation, it is the
program. An LLM reads it and acts. Any security tool that treats `.md` as "just docs" has a blind
spot the size of the entire skill supply chain. (We found this bug in our own scanner while auditing
our own published artifacts — see the postmortem below.)

**3. The trust decision happens before the sandbox starts.** By the time the container boots, the
`.mcp.json` in the workspace has already decided which servers will be spawned and what they can do.
Auditing after startup is auditing after the decision.

## What the content-trust plane actually does

AIShield implements four controls, each mapping to a point in the agent lifecycle.

### 1. Pre-flight workspace scan — before the box starts

Parse everything in the workspace that will influence agent behaviour: `.mcp.json`, forge / Goose /
Open Interpreter configs, and every skill file. Score them. Refuse to boot on high risk.

```bash
python scripts/scan_workspace.py /path/to/workspace --md
```

**Invariant: AIShield never spawns a command found in a scanned configuration.** Reading an MCP
server's `tools/list` requires starting it, and an MCP `command` is arbitrary code — several
config scanners explicitly warn that scanning your config executes it. Auditing a hostile config
must not be the thing that compromises you. The cost of this choice is honest: purely static
analysis does not see tool descriptions that only exist at runtime.

### 2. Sandbox-hardening rules — is the box itself built correctly?

Eleven rules covering the ways teams accidentally hand the host back to the agent: mounted
`docker.sock`, `--privileged`, host network / PID / IPC namespaces, `cap_add: ALL`,
`CAP_SYS_ADMIN`, `seccomp=unconfined`, `--user 0`, Kubernetes `hostPath` mounts.

You can have a sandbox and still have no isolation. These rules check the second part.

### 3. Guardrail-as-harness — admission on every tool call

Between the model ("the brain") and the tools ("the hands") sits an admission check. Every call is
evaluated against policy: kill switch, deny list, allow list, then default-deny. Decisions are
written to a hash-chained append-only audit log, so tampering, deletion and insertion are all
detectable and locatable.

Cloudflare's own framing of Managed Agents separates the brain from the hands. That separation is
exactly where the content-trust plane belongs — it is the seam, and a seam is where you put a gate.

### 4. Continuous attestation — trust decays

A server that scored 95 last month can be rug-pulled tomorrow. Certification without expiry is
marketing. AIShield re-scans on a cycle (default 7 days), detects drift against the recorded
evidence hash, and revokes certification when the score drops below threshold. For live agents it
re-runs the workspace pre-flight, so "was safe at install time" never silently becomes "is safe now".

## Composing with specific runtimes

| Runtime | Where AIShield fits |
|---|---|
| **Cloudflare Sandboxes / Containers** | Pre-flight the workspace before the sandbox is provisioned; run harness admission at the tool boundary. Cloudflare's own guidance suggests detecting Shadow MCP at the gateway — that is a content-trust rule, and content-trust rules are what AIShield ships. |
| **forgevm / agent-forge** | Same pre-flight, plus the sandbox-hardening rules applied to the VM/container definition itself. |
| **Open Interpreter** | Scan its config and any loaded skills before granting shell access. |
| **Goose** | Scan `~/.config/goose` extensions and MCP entries; keep continuous attestation on the ones you keep. |
| **CI / GitHub Actions** | SARIF 2.1.0 output into Code Scanning; CycloneDX SBOM for the supply-chain view. |

## Postmortem: we found this blind spot in our own product

On 2026-08-10 someone downloaded one of our published skills from a third-party marketplace. It was
the first real adoption signal for that channel, and it immediately surfaced a gap: the artifact had
shipped without its source being kept in the repository. We could not re-verify what a stranger was
running.

Fixing that meant building a distribution gate — every published artifact must be registered in a
ledger, keep its source in-repo, and pass our own scanner before release. Running it exposed a
second, worse problem: our engine downgraded every finding inside a `.md` file to "documentation
example", on the reasonable theory that a `curl` snippet in a README is not an attack.

For skills that theory is wrong. A malicious `SKILL.md` containing prompt-injection plus a
`curl | bash` payload scored **98/100 with only low-severity findings**. It would have passed.

The fix distinguishes documentation from instruction payloads: `SKILL.md`, `AGENTS.md`, `CLAUDE.md`,
anything under `skills/` or `prompts/`, and any Markdown carrying a `name` + `description`
frontmatter is treated as executable content. The same malicious sample now scores **61/100 with
critical findings** and is blocked.

The first thing the fixed gate blocked was our own published skill, which hardcoded an internal
address. That is embarrassing in the useful way: a security tool that cannot fail its own audit is
not running an audit.

## FAQ

**Is AIShield a sandbox?**
No. It does not isolate execution. It decides what should be trusted before and during execution.
Use it with a sandbox, not instead of one.

**Does AIShield compete with Cloudflare Sandboxes / forgevm / E2B?**
No. Those are isolation runtimes. AIShield is the content-trust plane above them. Deploying both is
the intended configuration.

**Does it send my code to the cloud?**
No. The rule engine is fully local with zero third-party dependencies. Semantic analysis via an LLM
is optional and off by default.

**Why not just execute the MCP server to enumerate its tools?**
Because an MCP `command` is arbitrary code supplied by the thing you are trying to audit. We accept
reduced runtime visibility in exchange for the guarantee that scanning a hostile artifact is safe.

**What does it cover?**
214 MCP rules / 220 skill rules, aligned to OWASP MCP Top 10, OWASP Agentic AI Top 10 (ASI01–ASI10),
Chinese-language prompt injection, and sandbox escape.

## 中文摘要

给 agent 一台电脑，现在已经是被解决的基础设施问题——Cloudflare Sandboxes、forgevm、E2B、
Open Interpreter、Goose 都能给 agent 一个隔离的 shell、文件系统和网络栈。

但它们解决的是**爆炸半径**（agent 能碰到什么），不是**内容可信**（agent 读进来的 MCP server、
skill、工具描述该不该信）。一个被投毒的 skill 在沙箱里照样能把数据带走——它用的是你主动给它的凭据，
只不过是在容器里做的。隔离是必要条件，不是充分条件。

AIShield 做的是 **agent 计算机的内容安全平面**，与上述所有隔离运行时互补，不是竞品。四个控制点：
① 启动前工作区预扫（绝不执行被扫配置里的命令）② 沙箱硬化规则（有沙箱不等于有隔离）
③ 每次工具调用的准入 harness（哈希链审计）④ 持续鉴证（信任会衰减，认证必须会过期）。

文中「自查发现自家盲点」一节是真实事故复盘：我们的引擎曾把所有 `.md` 命中降级为「文档示例」，
导致一个恶意 `SKILL.md` 拿到 98 分放行。对 skill 来说，Markdown 就是可执行体。修复后同一样本
61 分被拦，而第一个被拦下的是我们自己已发布的 skill。

---

- GitHub: https://github.com/lm203688/aishield
- Install: `npx aishield-mcp-server`
- Benchmark: [agent-security-benchmark-2026](agent-security-benchmark-2026.md)
- Trust Standard: [aishield-trust-standard-v0.1](aishield-trust-standard-v0.1.md)
