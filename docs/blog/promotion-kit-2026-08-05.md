# Promotion Kit — 2026-08-05

**主题**：离线 slopsquatting 检测 —— 覆盖「与真实包不形近」的那一半 AI 幻觉包
**支撑文章**：`docs/blog/blog-slopsquat-offline-detection-2026-08-05.md`
**核心数据锚点**：205,474 个虚构包名 / ~50% 不形近 / 8.7% 跨注册表命中 / react-codeshift 扩散 237 仓库 / 0-40 误报 / 127 测试通过
**发布状态**：全部为**草稿**（无对应外部连接器已连接，未自动发布）

---

## 1. X / Twitter 线程

**1/**
Everyone's defending against typosquatting.

But ~50% of AI-hallucinated package names aren't misspellings of anything. They're *compositions*. Edit-distance detection structurally cannot see them.

We shipped offline detection for that half. 🧵

**2/**
USENIX Security 2025: 16 models, 576k code samples.

19.7% of recommended packages didn't exist.
205,474 unique fabricated names.
43–58% recur deterministically.

Each one is a registrable, empty namespace slot. Cost to attack: a registry signup.

**3/**
The canonical case: `react-codeshift` (Jan 2026).

Fuses `jscodeshift` + `react-codemod` into a name that never existed. Large edit distance to both parents. No similarity scanner fires.

**4/**
Here's the 2026 part.

It spread to **237 repositories via AI-generated agent skill files**.

An agent wrote it into a skill. Another agent read that skill as authoritative context and repeated it. No human planted it.

A hallucination committed once becomes ground truth for every agent after.

**5/**
So we added three offline channels to AIShield:

→ composite hallucination advisory (the non-similar half)
→ cross-registry confusion (8.7% of Python hallucinations exist on npm)
→ dependency confusion / internal namespace leakage

Plus manifest hygiene: install-script poisoning, untrusted sources, unpinned versions, missing lockfile.

**6/**
The severity choice matters.

Composite hallucination = **`info`, zero score deduction**, capped at 5 per manifest.

Offline we can't prove a package doesn't exist. We can only say "this name has the shape of a fabrication, verify before install."

Loud and wrong is worse than quiet and right.

**7/**
False positives, measured:

40 real widely-used packages (react-router-dom, langchain-community, @modelcontextprotocol/sdk, pytest-cov…)

**0 / 40 false positives.**
6 / 7 detection on the malicious sample.
127 tests passing.

**8/**
Why offline?

Competitors ship a 4.3M-package database or query the live registry.

Both work. Both mean your dependency graph — a fingerprint of your internal architecture — either bloats your install or leaves your machine.

AIShield: pure heuristics. Zero network calls. Zero package DB.

**9/**
The honest caveat: a heuristic can't prove existence. It reduces an unbounded problem to a short ranked list.

Run the boring stack too: lockfiles + `npm ci`, age gating, Sigstore, human review on agent-added deps, `--ignore-scripts`.

**10/**
AI-generated code gets reviewed for logic.
AI-generated dependency lists get executed on trust.

In the agentic era, the import statement is the attack surface.

MIT, local-first, 201 rules (OWASP MCP Top 10 + Agentic AI Top 10):
`npx aishield-mcp-server`
github.com/lm203688/aishield

---

## 2. Hacker News

**Title:**
`Half of AI-hallucinated package names aren't misspellings – detecting them offline`

**Alt titles (A/B):**
- `Slopsquatting: edit-distance detection misses ~50% of hallucinated packages`
- `A hallucinated npm package spread to 237 repos via AI-generated skill files`

**URL:** https://aishield.tools/blog/slopsquat-offline-detection-2026-08-05

**First comment (author context — post immediately):**

> Author here. The thing that pushed me to build this was the propagation vector in the `react-codeshift` case, not the hallucination rate itself.
>
> Typosquat defenses assume a *near-miss*: a human mistyped something, so the fake name sits close to the real one in edit-distance space. Registries are decent at this now. But a model doesn't mistype — it composes a plausible name out of naming conventions. `react-codeshift` is `jscodeshift` + `react-codemod` fused. Edit distance to either parent is large. Similarity detection is structurally blind to it, and roughly half of the 205k fabricated names from the USENIX study fall in that bucket.
>
> Then it spread to 237 repos through **agent-authored skill files** — one agent wrote the dependency into an instruction file, other agents read that file as authoritative context and repeated it. No human deliberately planted it. That's a self-reinforcing artifact in agent context, and it doesn't decay.
>
> Implementation notes, since I expect the obvious objection:
>
> - The composite-hallucination check is deliberately `info` severity with **zero score deduction**, capped at 5 findings per manifest. Offline you cannot prove non-existence. Overclaiming here would get the whole check disabled, which is a security failure with extra steps.
> - Measured 0/40 false positives on real widely-used packages, including hard composites (`react-router-dom`, `langchain-community`, `pytest-cov`). The catalog carries an explicit allowlist of high-frequency legit composites, which is the unglamorous part that makes it usable.
> - It misses `requesocks` (edit distance 4 from `requests`, no ecosystem anchor). I'd rather miss that than flag `react-router-dom`.
> - No network calls, no 4.3M-package database. Competitors do one or the other; both are reasonable, both mean your dependency graph either bloats the install or leaves the machine.
>
> None of this replaces lockfiles + `npm ci`, which fail closed on any hallucinated name and remain the actual fix. This is the cheap front half of the existence-check gate, running in CI.
>
> Happy to go into the heuristic details or argue about the severity choice.

---

## 3. Reddit r/LocalLLaMA

**Title:**
`Open-weight models hallucinate packages at ~4x the rate of frontier APIs — here's an offline detector`

**Body:**

If you run a local coder model for agent work, this is a tax you're paying that's worth knowing about.

USENIX Security 2025 (16 models, 576k samples):
- **Open-weight / open-source models: 21.7%** average package hallucination rate (CodeLlama exceeded 33% in some configs)
- **Commercial / frontier API: 5.2%** (GPT-4 Turbo lowest at 3.59%)

A 2026 replication on newer frontier models compressed the range to 4.62%–6.10%. The floor is not zero on anything tested.

I'm not posting this as an argument against self-hosting — I self-host too, and the cost math is usually right. The point is narrower: **model choice is a risk multiplier, not a control.** Running a local coder to save on API costs means accepting roughly 4x the squattable-name volume, and that trade is only correct if you have downstream gating that catches the difference. Choosing a frontier model doesn't let you skip lockfiles; it just lowers the rate at which the lockfile gate has to fire.

The nastier detail: **~50% of hallucinated names aren't similar to any real package.** They're compositions, not typos. `react-codeshift` = `jscodeshift` + `react-codemod` fused into something that never existed. Edit-distance and homoglyph checks — which is what most scanners and registries actually implement — never trigger on those.

And there's an agent-specific propagation path that should bother anyone running skill-file-driven or multi-agent workflows: `react-codeshift` spread to 237 repos because an agent wrote it into a skill/instruction file, and other agents read that file as authoritative context and repeated the dependency. A hallucination committed once becomes ground truth for every agent that reads it afterward.

So I added offline detection for the non-similar half to AIShield (MIT, local-first MCP/agent security scanner):

- composite hallucination advisory — ecosystem anchor token + multi-segment + not in catalog
- cross-registry confusion — 8.7% of Python-hallucinated names exist on npm, which matters in polyglot repos where agents scaffold both
- dependency confusion / internal namespace leakage
- manifest hygiene: `postinstall` curl|bash, `git+`/`http://` sources, `*`/`latest` specs, missing lockfile

Zero network calls, zero third-party deps, no 4.3M-package database — relevant if you self-host specifically because you don't want your stack phoning home. Registry existence/age checks exist as an *optional* remote step, off by default.

Severity for the composite check is `info` (no score deduction), capped at 5 per manifest. Offline you can't prove a package doesn't exist, so overclaiming would just get the check turned off.

0/40 false positives on real packages, 127 tests passing.

`npx aishield-mcp-server` · https://github.com/lm203688/aishield

Curious what hallucination rates people are seeing on current open-weight coders (Qwen3-coder, GLM, DeepSeek). The published numbers lag the models by a lot.

---

## 4. Reddit r/MCP

**Title:**
`Added offline slopsquat detection to our MCP scanner — the half that edit-distance misses`

**Body:**

Context for anyone running MCP servers from the wild: the supply-chain risk isn't only the server code, it's the dependency list the agent writes for you.

Numbers worth having in your head:
- 19.7% of AI-recommended packages don't exist (USENIX Security 2025, 16 models / 576k samples)
- 205,474 unique fabricated names — each a free namespace slot
- 43–58% recur deterministically, so attackers can pre-register
- **~50% aren't similar to any real package** → typosquat detection is structurally blind

Case that made it concrete: `react-codeshift` (Jan 2026), a fusion of `jscodeshift` and `react-codemod`. It spread to 237 repos through **AI-generated skill files** — agent writes it into an instruction file, next agent reads that as authoritative and repeats it. Directly relevant to MCP/skill ecosystems, where instruction files are the distribution medium.

What's new in AIShield (MIT, local-first, 201 rules across OWASP MCP Top 10 + Agentic AI Top 10):

- **composite hallucination advisory** — the non-similar half, `info` severity, capped at 5/manifest
- **cross-registry confusion** — 8.7% of Python hallucinations exist on npm
- **dependency confusion** — internal namespace tokens in public manifests
- **install-script poisoning** — `preinstall`/`postinstall` running curl/wget/base64/chmod (critical)
- **untrusted sources** — `git+`, `http://`, `file:`, tarball URLs (high)
- **unpinned / missing lockfile** — a hallucinated name has no lockfile entry, so `npm ci` fails closed

All offline. No registry lookups, no package database. Exports SARIF + CycloneDX if you want it as a CI gate.

0/40 false positives measured on real packages; 127 tests passing.

`npx aishield-mcp-server` · https://github.com/lm203688/aishield

Also curious whether people here are seeing CoSAI's *Agentic IAM* paper (Mar 2026) get picked up — the "fail-closed enforcement gateway + immutable decision log" requirement seems like where MCP runtime governance is heading, and almost nothing in the OSS tooling space implements it yet.

---

## 5. Lobsters

**Title:** `Detecting AI-hallucinated package names offline, including the ~50% that aren't typos`
**Tags:** `security`, `ai`, `javascript`, `python`
**URL:** https://aishield.tools/blog/slopsquat-offline-detection-2026-08-05

**Submission comment:**

> Writeup of a heuristic set for the slopsquatting class, with the design tradeoffs made explicit rather than hand-waved.
>
> The interesting constraint is that offline you cannot prove a package does not exist. So the composite-hallucination check ships at `info` severity with zero score deduction and a 5-per-manifest cap — it converts an unbounded verification problem into a short ranked list, and deliberately does not pretend to more certainty than that.
>
> Includes measured false-positive numbers (0/40 on real widely-used packages), the one case it knowingly misses and why, and the allowlist work that makes composite-name heuristics usable at all. Pure stdlib, no package database, no network.

---

## 6. 待发布平台清单

| 平台 | 状态 | 连接器 | 备注 |
|------|------|--------|------|
| X / Twitter | 📝 草稿就绪 | ❌ 未连接 | 10 条线程，需手动发 |
| Hacker News | 📝 草稿就绪 | ❌ 无连接器 | Show HN 或普通提交；首评已备 |
| Reddit r/LocalLLaMA | 📝 草稿就绪 | ❌ 无连接器 | 角度=本地模型幻觉率 4x，社区契合度最高 |
| Reddit r/MCP | 📝 草稿就绪 | ❌ 无连接器 | 角度=MCP 供应链 + skill 文件传播 |
| Lobsters | 📝 草稿就绪 | ❌ 无连接器 | 需邀请码；标签 security/ai |
| GitHub Release Notes | ⏳ 待 npm 发布 | — | 阻塞于 NPM_TOKEN（只读） |
| npm | ⛔ 阻塞 | — | **需用户提供 Automation token** |

### 发布节奏建议
1. 先发 **HN**（周三/周四 UTC 13:00–16:00 命中率最高），首评立即跟上。
2. HN 有热度后 2–4h 内发 **r/LocalLLaMA**（换成本地模型角度，勿复制粘贴同一文案）。
3. 次日发 **r/MCP** + **Lobsters**。
4. X 线程与 HN 同步发，用于回流。

---

## 7. 不变量自查（发布前必过）
- [x] 本地 / 不上云 —— 全文强调零网络调用、零包数据库
- [x] MCP + Agentic 双维覆盖 —— 文案与 llms.txt 均已声明
- [x] 中性信任机构 —— 未与任何厂商结盟，未贬损具体竞品（只做能力对比）
- [x] 不改名，域名 aishield.tools —— 全文一致
- [x] 无 secret / token 泄露
- [x] 数据可溯源 —— 所有数字均附研究出处
- [x] 代码已跑通测试（127 passed）后才提交
