# Promotion Kit — 2026-08-05（第二轮：非执行式配置审计）

**主题**：扫描 MCP 配置 ≠ 运行它 —— 14 客户端面自动发现 + 纯静态审计
**支撑文章**：`docs/blog/blog-config-scan-without-execution-2026-08-05.md`
**核心数据锚点**：14 客户端面 / 10 类单 server 风险 / 命名空间遮蔽 + 7 类毒性流 / 20 份良性 0 误报（94 分） / 10 份恶意 10/10 检出（0 分） / 190 测试全绿 / 自查 npm audit 5→0
**发布状态**：全部为**草稿**（外部连接器均未连接，未自动发布）

---

## 1. 一句话钩子（各平台通用）

> 为了确认一份 MCP 配置是不是恶意的，大多数扫描器会**先把它执行一遍**。

这句话是整轮传播的支点。它不需要解释背景，任何用过 MCP 的人看完就懂问题在哪。

---

## 2. X / Twitter 线程

**1/**
To check whether an MCP config is malicious, most scanners start by… running it.

They have to: reading `tools/list` means spawning the server. And an MCP `command` is arbitrary code.

So the audit *is* an execution. 🧵

**2/**
This isn't a strawman. Config scanners say it in their own README:

"Scanning MCP configurations will execute the commands defined in them."

Honest documentation. Also an admission: if the config came from someone else, scanning it is the attack.

**3/**
And configs increasingly *do* come from someone else.

`.mcp.json`, `.vscode/mcp.json`, `.cursor/mcp.json` ship inside repos. `git clone` a stranger's project → you just imported their startup command.

Adversa's TrustFall / CVE-2026-30615 sit exactly on this boundary.

**4/**
OX Security (2026-04, "Mother of All AI Supply Chains"): STDIO-style configs can reach command execution *regardless of whether the server process is properly started*.

Configs are propagating like dependencies — with nothing playing the role of a lockfile.

**5/**
So AIShield made the opposite trade: **we gave up `tools/list`.**

No fork. No spawn. No exec. Ever.

We parse the config and infer capabilities from the *shape* of command/args/env, then score risk from capability + launch posture.

**6/**
The cost is real and we state it plainly: no runtime tool descriptions → we don't see prompt injection hidden in tool descriptions from this path. (AIShield's 201 rules still cover that when you submit a server description directly.)

**7/**
What you get instead: auditing a hostile config can't compromise the machine doing the audit.

For the most common workflow — "cloned an unfamiliar repo, let me scan before I trust it" — that trade is obviously right.

**8/**
Coverage: 14 client surfaces.
Claude Desktop · Claude Code (user+project) · Cursor (user+project) · VS Code (user+project) · Windsurf · Gemini CLI · Copilot CLI · Augment · Zed · Cline · WorkBuddy

User-level and project-level counted separately — different trust levels entirely.

**9/**
Per-server: privileged launch, runtime package fetch (`npx -y`/`uvx`), shell interpreter (`bash -c`), non-registry provenance, inline plaintext credentials, insecure transport, wildcard bind, unauthenticated remote, project-level trust trap.

**10/**
Cross-server is where it gets interesting:

**Namespace shadowing** — two servers exposing the same tool name. Which one the agent calls depends on load order, not your intent. NSA flags this as a confused-deputy entry point.

Every config looks clean alone. Only the combination is dangerous.

**11/**
**Toxic capability flows** — 7 classes. e.g. private-data read + untrusted network egress inside one trust boundary. Credential access + code execution. FS write + network fetch.

Again: individually harmless, jointly exploitable.

**12/**
A failure worth publishing. First benchmark run:

20 benign configs → score 0
10 malicious configs → score 0

**A scorer that always returns 0 is identical to having no scorer.** A gate that treats good and bad alike only protects its own existence.

**13/**
Root cause: no cap on cumulative deductions. "15 servers configured" out-deducted "3 malicious servers." Both bottomed out.

Fix: cap medium/low accumulation (20/5) and rebalance —
critical 20 · high 8 · medium 1.5 · low 0.5 · info 0

**14/**
After the fix:

20 benign official configs → **0 false positives, 94/100**
10 known-malicious configs → **10/10 detected, 0/100**

And a `TestScoringDiscrimination` class now pins "the scorer must separate good from bad" so nobody quietly reverts it.

**15/**
Second same-shaped bug: `secrets` capability was inferred from **env key names** (anything matching `*KEY`). Every normal config got flagged as credential-holding → toxic-flow alerts everywhere.

Now inferred from **inline plaintext values**. A key named `GITHUB_TOKEN` doesn't mean the value is in the file.

**16/**
Also: STDIO command-execution exposure is `info`, **zero deduction**.

Nearly every STDIO config matches it. At `medium`, 20 perfectly normal official configs produce 20 alerts and drown the real ones.

Alerts are only worth anything while they're scarce.

**17/**
Credentials found in a config are recorded as `<redacted:kind>`. The raw value never appears in the report.

A security report shouldn't become a new leak channel.

**18/**
Same sweep, we ran `npm audit` on our own `aishield-mcp-server`: **5 vulns (2 high, 3 moderate)**, including a direct dep (`@modelcontextprotocol/sdk` — SSRF + path traversal classes).

Fixed to 0 in the same pass.

A security tool shipping vulns is the worst look there is. Publishing it beats hiding it.

**19/**
```python
from scanner import discover_and_scan
result = discover_and_scan()
```
```
POST /api/v1/scan/client-config
```
Response carries `"note": "静态分析，未执行任何配置中的命令"` — a product commitment, not a disclaimer.

**20/**
AIShield — local-first, open source, free.
201 rules · OWASP MCP Top 10 + Agentic AI Top 10 · zero third-party deps · 190 tests green

https://github.com/lm203688/aishield
`npx aishield-mcp-server`

---

## 3. Hacker News

**标题**：`Show HN: Auditing MCP configs without executing them`

**正文**：

Most MCP config scanners have to spawn the server to read `tools/list`. But an MCP `command` is arbitrary code, so the audit is itself an execution — one scanner states this outright in its README: "Scanning MCP configurations will execute the commands defined in them."

That's fine when the config is yours. It stops being fine now that `.mcp.json` / `.vscode/mcp.json` / `.cursor/mcp.json` ship inside repositories, so cloning a stranger's project imports their startup command.

We took the other trade: no `tools/list`, ever. Pure static parse, capabilities inferred from the shape of command/args/env. We lose visibility into prompt injection hidden in runtime tool descriptions — stated plainly, not buried — and in exchange, auditing a hostile config can't compromise the auditing machine.

Covers 14 client surfaces (user-level and project-level counted separately, since their trust levels differ). Per-server: privileged launch, runtime package fetch, shell interpreter, non-registry provenance, inline plaintext credentials, insecure transport, wildcard bind, unauthenticated remote endpoints, project-level trust traps. Cross-server: namespace shadowing and 7 classes of toxic capability flow — both invisible when you look at one config at a time.

The part I'd actually like feedback on is a bug we shipped and caught: the first benchmark gave benign configs a score of 0 and malicious configs a score of 0. A scorer that's constant is equivalent to no scorer. Cause was uncapped cumulative deduction — having many servers out-deducted having malicious ones. After capping medium/low accumulation and rebalancing weights: 20 official configs → 0 false positives at 94/100; 10 malicious configs → 10/10 at 0/100. There's now a test class whose only job is to fail if the scorer stops discriminating.

Related: a `secrets` capability inferred from env *key names* made every normal config look credential-bearing and lit up toxic-flow alerts. Now inferred from inline plaintext *values*.

Local-first, MIT, zero third-party dependencies, 190 tests.

https://github.com/lm203688/aishield

---

## 4. Reddit r/mcp

**标题**：`你的 MCP 配置扫描器，可能正在运行你要它检查的东西`

**正文**：

想给本机的 MCP server 做体检，工具的第一步通常是把它启动起来——因为要拿 `tools/list` 就得连上去，要连上去就得跑 `command`。

而 `command` 就是一行任意代码。所以「检查这份配置是否恶意」的动作，本身包含了「执行这份配置」。

这在配置都是自己写的年代无所谓。但现在项目级配置（`.mcp.json`、`.vscode/mcp.json`、`.cursor/mcp.json`）跟着仓库走，clone 一个陌生项目就等于引入了别人的启动命令。

我们做了相反的取舍：**放弃 `tools/list`，一行命令都不执行**，纯静态从 command/args/env 的形状推断能力再判风险。

代价说清楚：看不到运行时工具描述里的提示注入。收益：扫一份来路不明的配置，不会把自己搭进去。

覆盖 14 个客户端面（用户级/项目级分开算，信任等级本来就不同）。除了单 server 的 10 类风险，还看两件单点看不出来的事：

- **命名空间遮蔽**：两个 server 撞了工具名，agent 调哪个取决于加载顺序而非你的意图
- **毒性能力流**：7 类组合，比如「读私有数据 + 向不受信网络出口」同处一个信任边界

顺带说个我们自己犯的错，可能比功能本身更有参考价值：第一版基准跑出来，20 份良性配置 0 分，10 份恶意配置也 0 分。**恒定输出的评分器等于没有评分器。** 根因是低危项累计扣分没上限，「server 配得多」比「配了恶意 server」扣得还狠。加了累计上限重排权重后：良性 0 误报 94 分，恶意 10/10 检出 0 分，并加了个专门测「评分器必须能区分好坏」的测试类钉住它。

同一轮巡检里对我们自己的 npm 包跑 audit，报出 5 个漏洞（2 high），当轮修到 0。

本地运行、MIT、零第三方依赖。https://github.com/lm203688/aishield

---

## 5. 待发布平台清单

| 平台 | 状态 | 备注 |
|---|---|---|
| X / Twitter | 草稿 | 连接器未连接 |
| Hacker News | 草稿 | 手动发，建议工作日 UTC 14:00–16:00 |
| Reddit r/mcp | 草稿 | 主战场，技术受众匹配度最高 |
| Reddit r/LocalLLaMA | 草稿 | 强调「本地 / 无 token」 |
| Lobsters | 草稿 | 需邀请码 |
| Dev.to / 掘金 | 草稿 | 中文版直接用博客正文 |

---

## 6. 不变量自查（发布前必过）

- [x] 未宣称「运行时防护」「网关」等未实现能力
- [x] 未宣称能检出运行时工具描述注入（该局限已在正文明写）
- [x] 「本地 / 不上云」贯穿全部文案
- [x] 双维（MCP Top 10 + Agentic AI Top 10）叙事保留
- [x] 中性信任机构定位未被稀释
- [x] 未改名，统一 aishield.tools
- [x] 无任何 secret / token / PAT 出现在文案
- [x] 所有量化数字均可由 `tests/test_client_discovery.py` 复现
- [x] 竞品引用为公开 README 原文，未做贬损性推断
