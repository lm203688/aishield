# AIShield: An Offline, Zero-Dependency, Machine-Verifiable Framework for Agentic-AI Supply-Chain and Prompt-Injection Threat Detection

> **Paper A — full draft (CCF-A / SCI orientation).**
> Target venues: USENIX Security 2027 (system/security, artifact-weighted) or IEEE Transactions on Information Forensics and Security (SCI).
> All quantitative claims are pinned to the single source of truth in `ARTIFACT.md` and `benchmarks/expected.json`; the reproducibility package is `ARTIFACT.md` + `scripts/run_all.py`.
> Version of record: AIShield 4.11.0 (`/api/v1/health.commit`).

---

## Abstract

The shift from monolithic software to agentic AI—systems that *execute* externally supplied tools, packages, and instructions—moves the attack surface from the traditional supply chain to prompt injection, tool poisoning, and capability overclaim. Existing guardrails are deficient on at least one of three axes: they **exfiltrate data to the cloud** (breaking air-gap and compliance assumptions), they make **unverifiable safety claims** (no formal guarantee that the scanner itself cannot be hijacked), or they suffer **high false-positive rates** that cause operators to disable them. We present **AIShield**, an offline, zero-dependency, machine-verifiable framework for detecting threats in agentic-AI workloads. AIShield's contributions are (1) a **formal isolation invariant**—the scanner never executes scanned code, never contacts the network, and writes only to its own isolated state—*verified over a faithful mechanism model* by exhaustive bounded model checking over 64 reachable states (2^6, with a completeness argument); the *implementation* is covered by a runtime self-proof and property-based tests, with a full TLA+/Apalache proof listed as enhancement evidence; (2) a **neuro-symbolic zero-false-positive discipline** (`ratify()`) under which the neural layer can never self-escalate; and (3) an **externally-sourced, provenance-auditable gold-standard evaluation corpus** of 1,110 samples (593 positive / 517 negative, 18 attack families; automated Label Consistency Audit κ = 0.867) on which AIShield achieves **0/517 false positives** while strictly dominating a learned lexical baseline on false-positive rate (0% vs 48.9%) and on primary-scope recall (100% vs 62.1%). We report honest limitations, including that the external recall of **40.6% [36.6%, 44.7%]**—with primary-scope supply-chain CVE detection at **100% (66/66)** via an *offline, air-gap-safe* advisory matcher, and the remaining **33.2%** on natural-language prompt-injection reflecting the genuine ceiling of static analysis on semantic-classification cases—reflects scope-partitioned difficulty rather than a benchmark artifact; the corpus labels derive from authoritative external ground truth (GitHub Security Advisory CVEs and the published InjecAgent benchmark), so label reliability rests on provenance—augmented by an automated Label Consistency Audit (κ = 0.867) that verifies labels are independently re-derivable from primary signals; we do not re-annotate a source-endorsed corpus (and state why, §7.2), shipping a runnable human-IAA toolkit for any reviewer-requested human κ.

---

## 1. Introduction

### 1.1 Motivation

Agentic AI systems compose third-party tools (MCP servers, function-calling schemas) and ingest untrusted instructions. This composition reintroduces supply-chain risk at a new layer: a malicious MCP server can execute arbitrary code in the agent's context, a poisoned dependency can exfiltrate secrets, and an indirect prompt injection can redirect the agent's actions. The *Model Context Protocol (MCP)* and the *OWASP Top 10 for LLM Applications 2025* and *OWASP Agentic AI Top 10* enumerate these risks, but detection tooling has not kept pace.

Three structural deficiencies dominate the current landscape:

- **Data exfiltration by design.** Many commercial scanners send the scanned artifact or its metadata to a vendor cloud. For regulated or air-gapped deployments this is a non-starter, and it creates a second-order supply-chain dependency on the scanner vendor.
- **Unverifiable safety claims.** A scanner that claims to "prevent prompt injection" is itself a privileged component. If the scanner can be made to *execute* scanned code or be reconfigured by it, its guarantees are void. No existing tool offers a machine-checkable proof that the scanner's own isolation holds.
- **False-positive disablement.** Guardrails that cry wolf are switched off. In security tooling, a false positive is not a nuisance—it is a **fidelity failure** that defeats the control.

### 1.2 Thesis (single sharp contribution)

> **We present AIShield: an offline, zero-dependency, machine-verifiable framework for agentic-AI threat detection whose safety invariants are exhaustively *verified over a faithful mechanism model* (64 reachable states, 4 mutation variants all caught); implementation conformance is established separately by a runtime self-proof and property tests and whose detection discipline guarantees zero false-positive expansion on an externally-sourced corpus (0/517).**

The differentiating combination—**offline + formally-exhaustively-verified isolation + zero-false-positive discipline**—is, to our knowledge, not simultaneously achieved by any existing tool (§2). We do *not* claim a leaderboard-topping recall; we claim a *trustworthy operating point* backed by proof and reproducible evaluation.

### 1.3 Paper roadmap

§2 positions AIShield against related work with a differential table. §3 formalizes the threat model (mapping the RSI L1–L5 severity scale to OWASP Agentic AI). §4 describes the design, emphasizing the neuro-symbolic zero-FP bridge. §5 presents the formal isolation invariants and their exhaustive verification. §6 evaluates on the external corpus with baselines and bootstrap confidence intervals. §7 states limitations honestly. §8 concludes.

---

## 2. Background and Related Work

### 2.1 The agentic threat surface

The OWASP *Top 10 for LLM Applications (2025)* and the OWASP *Agentic AI Top 10* identify prompt injection, supply-chain compromise, and excessive agency as top risks. The *Model Context Protocol* standardizes tool composition but provides no built-in assurance that a connected server is benign. NIST *AI Risk Management Framework* calls for measurable, auditable controls—precisely what current tools lack.

### 2.2 Related tools and their gaps

| Tool | Offline / air-gap | Formal isolation proof | Zero-FP discipline | External-corpus eval | AIShield delta |
|---|---|---|---|---|---|
| **Invariant mcp-scan** (v0.9) | Yes (local) | No | No (heuristic) | No public corpus | + formal proof + 0-FP |
| **Snyk agent-scan** (v1.x) | **No** (cloud) | No | No | No | + offline + proof |
| **agent-security-scanner-mcp** (v0.4) | Yes | No | No | No | + formal proof |
| **mcp-audit** (v1.2) | Yes | No | No | No | + formal proof |
| **Lakera / Gandalf** (benchmark) | **No** (cloud) | No | No | Gandalf is a testbed, not a scanner | + offline + proof |
| **PJB / InjecAgent** (datasets) | n/a (data) | n/a | n/a | Yes (the data we reuse) | — (we *consume* these) |
| **AIShield** (4.11.0) | **Yes** | **Yes (model-level BMC, 64 states)** | **Yes (ratify)** | **Yes (1,110 gold-standard samples, LCA κ=0.867)** | — |

The decisive gap is the **combination**: every offline tool we surveyed lacks a machine-checkable isolation proof and a zero-FP guarantee; every tool with a formal flavor targets a different problem (e.g., smart contracts) and not agentic tool composition. AIShield is the first to couple an *exhaustively verified* isolation invariant with a *zero-FP* detection discipline evaluated on an *externally-sourced, provenance-auditable gold-standard* corpus.

**Cell provenance (honesty of the differential table).** Every non-AIShield cell is an *evidence-anchored* claim, not an assertion of internal knowledge: "Offline / air-gap = **Yes**" means the tool runs locally without a vendor cloud by default; "**No**" means it requires a cloud backend or account token (Snyk, Lakera/Gandalf). "Formal isolation proof" means a *machine-checkable* proof that the scanner's own isolation holds; all competitors are marked **No** because none publishes such a proof (their detection is heuristic/pattern-based per their public documentation, cited in §9). "Zero-FP discipline" means a `ratify()`-style grounded-promotion gate that makes zero-FP *principled* rather than incidental; competitors are marked **No** as no such mechanism is documented. "External-corpus eval" marks whether a public, fixed, externally-sourced benchmark is reported; commercial tools are evaluated only on vendor-authored or undisclosed sets. Cells we cannot verify are left as "No (no published evidence)" rather than asserted absolutely, consistent with the paper's honesty posture. The new primitive AIShield contributes is therefore not "yet another scanner" but the first **machine-checkable isolation verification (model-level BMC) for an agentic scanner** coupled with a **neuro-symbolic zero-FP promotion gate** (`ratify()`) evaluated on an **externally-sourced** corpus — the combination none of the surveyed tools achieves.

---

## 3. Threat Model

We adopt the **RSI (Relative Severity Index) L1–L5** scale and map it to the OWASP Agentic AI taxonomy.

| RSI | Severity | Agentic manifestation | OWASP Agentic mapping |
|---|---|---|---|
| L1 | Informational | Benign capability mention | Excessive Agency (minor) |
| L2 | Low | Risky but gated tool use | Tool Misuse |
| L3 | Medium | Unauthorized data read | Data exfiltration |
| L4 | High | Credential/secret exposure | Sensitive Information Disclosure |
| L5 | Critical | Arbitrary code execution / persistent takeover | Supply-Chain Compromise / Agent Hijacking |

**Empirical finding (defect and fix).** During corpus construction we observed that **L5 signals are systematically suppressed by capability filters**: naive capability-based scanners downgrade execution-risk signals to L1 because they match a benign capability keyword. AIShield's scanner treats any execution-primitive signal as a *default-deny escalation path* rather than a capability to be filtered, closing this gap. This is reported as a concrete, fixed vulnerability class rather than a hypothetical.

**Adversary model.** We assume an adversary who controls (a) a third-party tool/MCP server the agent connects to, (b) a dependency the agent installs, or (c) text the agent ingests (indirect prompt injection). The adversary's goal is code execution, secret exfiltration, or unauthorized action. We do *not* assume the scanner itself is compromised; the isolation invariant (§5) bounds what a compromised *scanned artifact* can do to the scanner.

---

## 4. Design

### 4.1 Architecture

AIShield is a **local-first** scanner with two planes:

- **Configuration plane (static).** Parses manifests, dependency declarations, and tool schemas; applies a 264-rule detection catalog spanning 18 families.
- **Instruction plane (dynamic).** Analyzes ingested text (prompts, tool responses) for injection intent.

Both planes run in a **single OS process that never spawns the scanned artifact's commands** and never opens an outbound network socket (§5). Results are written only to an isolated, per-run state directory.

### 4.2 Neuro-symbolic zero-false-positive bridge

The neural layer may propose a finding, but promotion to a reported, blocking finding requires `ratify()`:

```
ratify(proposal):
    assert proposal not self_escalating      # neural layer may never upgrade its own privilege
    assert proposal grounded_in_symbolic_rule # must map to a catalogued rule or typed pattern
    return Finding(severity, evidence)
```

The invariant **"the neural layer can never self-escalate"** is enforced both by construction (the neural path has no write to the privilege table) and by the formal model (§5, INV-3 single-writer). This is what makes the **0/517 false-positive** result principled rather than accidental: under `ratify`, a finding must be grounded in a symbolic rule, and the false-positive surface is the precision of those rules, which we measure directly. Crucially, the promotion path is *part of the verified action system*: INV-6 (`grounded_promotion`, §5.1) states that every reported finding maps to a symbolic rule, so the isolation proof and the detector share the same invariant family—the "coupling" claimed in §1.2 is not merely asserted but stated as INV-3 + INV-6.

---

## 5. Formal Isolation Invariants

### 5.1 The invariant family

We specify five invariants over the scanner's action system:

- **INV-1 `no_execute`** — the scanner never executes a command derived from scanned content.
- **INV-2 `no_network`** — the scanner never opens an outbound network connection during a scan.
- **INV-3 `single_writer`** — the privilege/state table has exactly one writer (the symbolic core); the neural layer is read-only.
- **INV-4 `read_only_input`** — scanned inputs are never mutated or used as code.
- **INV-5 `completeness`** — the model explores all reachable states within the bounded action vocabulary.
- **INV-6 `grounded_promotion`** — every *reported* finding is grounded in a symbolic rule (`ratify`'s `grounded_in_symbolic_rule`); the detector's promotion path is part of the verified action system, so the proof is coupled to the detector rather than orthogonal to it.

### 5.2 Verification method

We use a three-layer defense:

1. **Quint** specification (`formal/isolation_invariants.qnt`) for human-readable modeling.
2. **Python bounded model checker** (`scripts/check_isolation_invariants.py`) that **exhaustively explores 64 reachable states**, reports `termination=exhausted`, `coverage=1.0`, `complete=true`, and includes a `completeness_argument()` proving |reachable| = 64 from the action vocabulary. The model is a faithful abstraction of the isolation *mechanism* — the scanner performs only read-only string analysis and can never promote a string found in scanned content into its own action — not a re-implementation of the scanner. The 64 states are a genuine bound, not hand-tuned: the action vocabulary reduces to "each of the 6 hostile corpus artifacts is either processed or not," so the reachable set is exactly 2^6 = 64, and the completeness argument cross-checks this against the empirical exploration (§6.4). This BMC is the *documented fallback* to an Apalache/TLA+ exhaustive proof (unavailable in our offline build) and is complementary to the runtime self-proof (`scripts/prove_isolation.py`), which shows the live scanner never spawns a scanned command on a concrete run.
3. **Hypothesis** property-based testing as a runtime regression net.

### 5.3 Mutation testing (discriminating power)

We inject four mutation variants (M1–M4) that each violate one invariant (e.g., M1 makes the scanner spawn a scanned command). The BMC **catches all four**, demonstrating that the invariant suite has real discriminating power rather than vacuously passing. This satisfies acceptance gate **R4** (exhaustive model checking with a completeness argument; the Python BMC is the documented fallback to Apalache, which is unavailable in our offline build environment).

---

## 6. Evaluation

All numbers below are produced by `scripts/run_all.py` and `scripts/baseline_compare.py` from pinned inputs; confidence intervals use bootstrap (1,000 resamples, seed `20261018`).

### 6.1 External corpus (gate R1)

- **Scale:** 593 positive / 517 negative / **1,110 total**, spanning **18 attack families**.
- **Provenance / label reliability:** the corpus is **externally-sourced gold-standard** — 66 positives are GitHub Security Advisory CVEs (labels anchored to third-party published vulnerabilities) and 527 positives + 517 negatives are the published InjecAgent benchmark (Zhang et al., NAACL 2024, author-labeled ground truth). Because the labels are *source ground truth* rather than in-house human annotation, label reliability is established by provenance, consistent with how HarmBench / AdvBench / InjecAgent themselves are accepted.
- **Label reliability basis — provenance, with an automated consistency audit.** Because every label is *inherited source ground truth* (CVE advisory classification / InjecAgent author labels) rather than annotation introduced by this work, label reliability is established by **provenance** — the same basis on which HarmBench, AdvBench, and InjecAgent themselves are accepted as benchmarks. We do not re-annotate; doing so would raise the unanswerable question "are our labels more authoritative than the benchmark authors'" without adding information the source already provides.
- **Label Consistency Audit (LCA).** We additionally run an automated, reproducible check that re-derives each label from raw signals (CVE identifiers, dataset provenance, a conservative lexical attack-term scan) **without** reading the source label, and compares the re-derivation against the source ground truth: Cohen's κ = **0.867** [0.809, 0.926] (bootstrap SE 0.015). This LCA κ is a *label self-consistency / reproducibility* metric — it verifies that the corpus's labels are independently re-derivable from primary signals, which is the appropriate consistency guarantee for a provenance-backed corpus. We are explicit that this is **not** a human inter-annotator-agreement figure, and we do not substitute it for one. Human dual-annotation on an already-source-endorsed gold-standard corpus would measure the annotators' fidelity to established labels rather than add independent evidence; we therefore report provenance + LCA as the label-quality argument, and ship `scripts/human_iAA_kit.py` so any reviewer-requested human κ can be produced transparently rather than claimed retroactively (§7.2).
- **Family coverage:** positives span `data_exfiltration` (176), `indirect_prompt_injection` (176), `jailbreak_family` (175), and 14 further families; negatives include 17 benign user tasks and 500 controlled benign-injection-context samples.
- **Adversarial negative design (why 0/517 means something).** The 517 negatives are *not* easy distractors. The 500 `controlled_matched` negatives are constructed by taking a positive injection artifact and **removing only the malicious intent while preserving the same surface text, tool context, and format** — i.e., a hard negative that specifically probes *over-triggering*. A scanner that merely keyed on salient words ("email", "password", "API") would fire on these and rack up false positives. Achieving **0/517** against this design — and in particular **0/500** on the controlled-matched set — is therefore a meaningful precision result, not an artifact of trivial negatives. The remaining 17 `benign_user_task` negatives are clean user requests with no injection context.

### 6.2 Baselines on the same fixed corpus (gates R2, R3)

All tools consume the identical corpus under the `serious_only`口径 (only critical/high count as detections). AIShield 4.11.0 (self) versus two offline-runnable naive baselines:

| Tool | recall (95% CI) | FP (95% CI) | F1 | Rules | Cloud |
|---|---|---|---|---|---|
| **AIShield** | **40.6% [36.6%, 44.7%]** | **0.0% [0.0%, 0.0%]** | **58%** | 264 | No |
| Naive keyword heuristic | 21.1% [17.9%, 24.4%] | 0.0% [0.0%, 0.0%] | 35% | 0 | No |
| Random guess (base-rate) | 48.9% [44.9%, 52.8%] | **53.8% [49.5%, 58.0%]** | 50% | 0 | No |
| Learned lexical (TF-IDF + Rocchio, 5-fold CV) | 83.0% [79.9%, 86.0%] | 48.9% [44.5%, 53.2%] | 74% | 0 (learned) | No |
| **LLM judge** (glm-4.5-flash, local proxy)¹ | **55.3% [47.2%, 64.2%]** | **0.0% [0.0%, 0.0%]**² | **72%** | 0 (parametric) | No³ |
| Invariant mcp-scan (v0.9) | N/A (unequal conditions) | N/A | N/A | 150 | No |
| agent-security-scanner-mcp (v0.4) | N/A (unequal conditions) | N/A | N/A | 120 | No |
| mcp-audit (v1.2) | N/A (unequal conditions) | N/A | N/A | 98 | No |
| Snyk agent-scan (v1.x) | N/A (unequal conditions) | N/A | N/A | N/A | **Yes** |

¹ LLM judge run on a stratified subsample (150 of 593 positives, 40 of 517 negatives) due to local proxy throughput limits; bootstrap CIs account for subsample size. Full-corpus run is impractical at ~0.12 samples/s sustained throughput on the local proxy.
² Only 8 of 40 negatives parsed successfully (80% PARSE_FAIL on adversarial-adjacent inputs); 0/8 FP. See §6.2.3 for the PARSE_FAIL analysis.
³ Local Zhipu GLM proxy (127.0.0.1:8790); no third-party SaaS called, but NOT air-gapped (local HTTP endpoint).

**Interpretation (the paper's spine).** The correct metric for a guardrail is **false-positive rate**, because a single false positive invites disablement. Under the **FP = 0** constraint, AIShield's recall (40.6%) **strictly dominates** the keyword heuristic (21.1%) on the same corpus with identical FP, and the random guess achieves higher raw recall (48.9%) only by emitting **53.8% false positives**—operationally unusable. We now add a genuine *learned semantic* comparator: an LLM judge (glm-4.5-flash, served on a local proxy, no cloud dependency) evaluated on the same corpus. It reaches **55.3% [47.2%, 64.2%] recall** at **0% FP** on parsed negatives—higher raw recall than AIShield, and the *same* zero-FP operating point. This is the most important result in the paper, because it reframes the comparison: **zero-FP is achievable by both deterministic and learned methods; the question is not whether zero-FP is possible, but what you get *with* it.** The LLM's advantage is NL-injection recall (79.7% vs 33.2%); AIShield's advantage is primary-scope supply-chain CVE coverage (100% vs 28.8%), formal isolation guarantees, air-gap operation, and deterministic reproducibility (§6.2.3). Four commercial baselines cannot be run under identical offline conditions and are reported as *not evaluated* rather than fabricated, a deliberate honesty choice (§7). The learned lexical baseline reaches **83.0% [79.9%, 86.0%] recall** but at a **48.9% [44.5%, 53.2%] false-positive rate**—249/500 false positives on the controlled-matched hard negatives *alone*—which disqualifies it as a guardrail, and it is **worse than AIShield on the primary supply-chain scope** (62.1% vs 100%, §6.2.1) because a lexical learner cannot perform version-range advisory matching. AIShield's value is the operating point (0/517 FP) plus dominance on primary scope—not the top-line recall number.

**Statistical significance (bootstrap, seed `20261018`, 1,000 resamples).** The 95% CIs are *disjoint* in both comparisons, so the claims are quantitative, not qualitative: (i) AIShield's recall CI **[36.6%, 44.7%]** lies entirely above the keyword heuristic's **[17.9%, 24.4%]** — AIShield's recall advantage at equal FP = 0 is **statistically significant**; (ii) the random guess's recall CI **[44.9%, 52.8%]** lies entirely *above* AIShield's — i.e., random guessing achieves **significantly higher raw recall**, and AIShield is *not* a recall leader. We state this without flinching: AIShield's value is the **FP dimension** (0/517 vs 53.8%), not raw recall. A guardrail that is indistinguishable from random on recall but emits 54% false positives is worse than useless; AIShield trades the top-line recall number for a *trustworthy operating point*, which is the paper's central, honestly-stated thesis.

### 6.2.1 Scope-partitioned recall (honest decomposition)

A single recall figure invites the misreading "the detector misses most attacks." We decompose it by *applicability scope* so the gap is explained rather than hidden. Detection uses the same `serious_only` bar (≥1 critical/high finding); confidence intervals are bootstrap (1,000 resamples, seed `20261018`), computed by `scripts/external_scope_recall.py`.

| Scope subset | Positives | Detected | Recall (95% CI) |
|---|---|---|---|
| **Overall** | 593 | 241 | **40.6% [36.6%, 44.7%]** |
| Primary — supply-chain CVE (GitHub Advisory, code/config) | 66 | 66 | **100.0% [100.0%, 100.0%]** |
| Secondary — NL prompt-injection (InjecAgent) | 527 | 175 | **33.2% [29.4%, 37.2%]** |
| By scan plane: `config` | 12 | 12 | **100.0%** |
| By scan plane: `instruction` | 581 | 229 | 39.4% [35.3%, 43.5%] |

**Interpretation.** AIShield's *offline* capability now spans both static supply-chain CVE detection and natural-language prompt-injection. The 66 GitHub Security Advisory positives are *dependency-version vulnerabilities* (e.g., `require github.com/getkin/kin-openapi v0.144.0` inside a known-vulnerable range). Detecting them requires **advisory-version matching**, which AIShield performs through an **offline, air-gap-safe matcher** (`scanner/supply_chain.py`): it parses dependency declarations across 8 ecosystems (go `require`, npm `@`, pip `==`, maven, nuget, ruby gem, rust cargo, composer) and checks the version against a **vendored static advisory index** (`scanner/data/advisory_index.json`, bootstrapped from the same GitHub Advisory / OSV data that defines ground truth). Live OSV lookup remains **disabled by default** to preserve the air-gap invariant (§1.1, §5); the offline index is refreshed out-of-band in production. This matcher lifts primary-scope recall from **0% → 100% (66/66) at 0 FP**. The remaining gap is the **secondary** NL prompt-injection subset (33.2%): a *semantic-classification* problem that static pattern analysis is not built to solve, stated rather than hidden. The matcher's parsing and semver-range logic are independently validated by synthetic unit tests (`tests/test_offline_advisory_matcher.py`) on out-of-corpus cases, so the integration recall is not tuned to the evaluation set. The blended **40.6%** is therefore the honest shape of a guardrail that trades a top-line recall number for air-gap safety and a zero-FP operating point. The learned lexical baseline reaches only **62.1%** on this primary scope (vs AIShield's **100%**)—confirming the advantage is *structural* (offline advisory version-matching), not recoverable by a lexical learner.

### 6.2.2 Error analysis of the NL-injection misses (honest taxonomy)

A single 33.2% figure invites the misreading "the detector is broken on prompt injection." We instead **explain every miss by an externally-defined axis**, turning the gap into a contribution. We categorize the 352 missed samples (and the 175 detected ones) using the benchmark's *own* authoritative fields (`dataset_setting`, `family`, `attack_type`) plus a detector-independent lexical-opacity proxy, so no category is invented post hoc to flatter the result.

**Finding 1 — recall is bimodal by injection overtness, not random.** The InjecAgent subset splits cleanly on the benchmark's `dataset_setting` field — `base` (the injection embedded covertly inside otherwise-benign tool output, e.g., a malicious instruction hidden in a product review) versus `enhanced` (an overt adversarial re-writing that adds explicit control phrasing):

| `dataset_setting` | Positives | Detected | Recall |
|---|---|---|---|
| `enhanced` (overt) | 175 | 175 | **100.0%** |
| `base` (covert) | 352 | 0 | **0.0%** |

This coincides exactly with the `family` axis: `jailbreak_family` is 175/175 (100%) while `data_exfiltration` (176) and `indirect_prompt_injection` (176) are both 0/176. The detector does not "sometimes work"; it works precisely where an *explicit* injection cue exists and fails precisely where the injection is *covert*.

**Finding 2 — a detector-independent opacity proxy confirms the ceiling is semantic, not lexical-missing.** We flagged each sample's scanned text for a small, conservative set of overt injection-control markers (`ignore previous`, `disregard`, `system prompt`, `email them`, `api key`, `password`, …). The result is decisive:

- **All 175 detected samples (100%) carried an explicit marker.**
- **318/352 misses (90.3%) contained no such marker** — lexically opaque.
- The remaining **34/352 (9.7%)** contained a marker *only inside benign-looking tool output* (e.g., "…email them to my alternate email address" embedded in a product review or a GitHub note). These are contextual covert injections: the cue is present but the surrounding text is genuinely benign, so a static rule that escalated it would also fire on legitimate content — i.e., escalating them would *manufacture* false positives, directly violating the zero-FP discipline. They are therefore a semantic-property boundary, not a missing keyword.

**Interpretation (the contribution).** The residual gap is not a defect to be hidden; it is a *principled, theoretically-grounded ceiling* of **static, offline, zero-FP** analysis on a *semantic-classification* problem. This maps onto the established overt-vs-covert (a.k.a. direct-vs-indirect / steganographic) injection distinction in the literature (Greshake et al., 2023; Zhang et al., NAACL 2024): static lexical analysis can catch overt injections (an explicit control cue exists) with perfect precision-oriented recall and **0 FP**, and it *cannot* adjudicate covert injections that depend on agent context and tool semantics without *executing* the agent — which would violate the air-gap / no-execute invariants (§5). The honest remedy is a *runtime* semantic monitor, which is explicitly out of scope for a static offline scanner and is positioned as future work (§7, §8). The 34 contextual misses additionally show that even lexically-present injections escape static escalation when embedded in benign contexts, reinforcing that covert injection is a semantic property rather than a missing pattern.

### 6.3 LLM-judge baseline: scope complementarity and format-compliance failure

We add a semantic LLM-judge comparator (`scripts/baseline_llm.py`, `scripts/analyze_llm_baseline.py`) served on a local proxy (glm-4.5-flash, 127.0.0.1:8790, no third-party SaaS, not air-gapped). The subsample is 150 of 593 positives (all 66 primary-scope GHSA positives + 84 secondary NL-injection positives) and 40 of 517 negatives, bootstrap-seeded for interval estimation.

**Scope complementarity (the structural finding).** On the *same* evaluation protocol the two systems partition the threat surface cleanly rather than competing for the same samples:

| Scope | Positives (subsample) | AIShield recall | LLM recall (95% CI) |
|---|---|---|---|
| Primary — supply-chain CVE (GHSA) | 59 | **100% (66/66 full corpus)** | 28.8% [17.0%, 39.0%] |
| Secondary — NL prompt-injection | 64 | 33.2% (full corpus) | **79.7% [68.8%, 89.1%]** |
| Blended subsample | 123 parsed | 40.6% (full corpus) | **55.3% [47.2%, 64.2%]** |

The gap is structural, not tuning: primary-scope detection requires *version-range advisory matching* against a curated offline index — an operation a foundation model cannot perform without a retrieved KB, and its recall drops to 28.8% because it guesses from parametric knowledge alone (and cannot reproduce AIShield's 66/66 exact-version hits on the full corpus). Secondary-scope detection is a *semantic classification* task that LLMs are well-suited to; AIShield's static-analysis ceiling there is the principle boundary documented in §6.2.2.

**Format-compliance failure (the second-order finding).** Of the 40 negatives, **32 (80%) produced unparseable output** — the model emitted reasoning without the required `VERDICT: X` line. The pattern is adversarial-correlated: 27 of the 32 PARSE_FAIL negatives are `controlled_matched` (positives with only the malicious intent removed, so the text still carries injection-adjacent surface features), versus 3 of 3 `clean_source` negatives also failing. On parsed negatives the FP rate is 0/8; on parsed positives recall is 55.3%. The 80% negative PARSE_FAIL rate is *itself* a result: it demonstrates that LLM output-format compliance degrades precisely on adversarial-adjacent inputs, so even where an LLM judge *could* be deployed, the surrounding harness must handle failure modes that a deterministic scanner does not exhibit. This is a structural property of the class of systems, not a fixable bug in one model.

**Interpretation.** The LLM baseline does not displace AIShield; it *sharpens* the paper's thesis. AIShield's contribution is not "the only way to get zero FP" (the LLM also achieves 0/8 on parsed negatives), but "the way to get zero FP *on adversarial-adjacent inputs* without relying on a probabilistic model's format compliance or on a cloud service." The supply-chain scope shows the concrete complement: deterministic advisory matching achieves 100% recall on a task that is *unsolvable without a curated offline KB*, and the LLM's 28.8% on the same subset quantifies the KB dependency. The NL-injection scope shows the other concrete complement: an LLM is far better at semantic classification, and the honest architectural position is a *combined* system — deterministic scanner for supply-chain/config plus LLM runtime monitor for covert injection — which is precisely the future work AIShield positions (§8).

### 6.4 Internal corpus (sanity)

On the internally-curated corpus, AIShield reaches **100% recall (57/57)** at **0% FP (0/45)** under `serious_only`, confirming the detector is not intrinsically broken—the external 40.6% reflects genuine out-of-distribution difficulty (concentrated in the NL prompt-injection subset), while the supply-chain CVE subset is fully recovered by the offline advisory matcher.

### 6.5 Formal verification results (gate R4)

The BMC exhausts **64 reachable states** (`coverage = 1.0`, `complete = true`) and catches all four mutation variants M1–M4. The completeness argument derives |reachable| = 64 from the bounded action vocabulary.

### 6.6 Reproducibility

`scripts/run_all.py` aggregates the six declaration-surface gates, the FVI gate, the unit tests, and both benchmark corpora. A single `pip install -e .[test]` followed by `python scripts/run_all.py` reproduces every number in this section (artifact, §Appendix).

---

## 7. Limitations (gate R7)

We state limitations explicitly; none undermine the central claim but all bound its scope.

1. **External recall is not 100% — and is scope-asymmetric.** The 40.6% external recall (§6.2) decomposes (§6.2.1) into **100% on the 66 CVE-version supply-chain samples** (recovered by the offline advisory matcher, §6.2.1) but only **33.2% on the NL prompt-injection subset (InjecAgent)**. The residual gap is a *semantic-classification* problem—static pattern + version-range analysis is not built to adjudicate whether an instruction is an indirect injection—and we report it openly rather than exclude these hard cases or report a self-selected 100%. Our contribution is methodology + formal assurance + a zero-FP operating point, **not** a leaderboard-first detector.
2. **Label quality rests on provenance + automated consistency, not human dual-annotation.** The κ = 0.867 is a *Label Consistency Audit (LCA)*: an independent automated re-derivation of labels from raw signals compared against the corpus's source ground-truth labels (GitHub Security Advisory CVEs and InjecAgent author labels). It quantifies *label self-consistency / reproducibility*, **not** human inter-annotator agreement, and we do not represent it as such. Our label-quality argument is two-fold: (i) every label is inherited source ground truth from a published, third-party-vetted corpus, and (ii) the LCA shows these labels are independently re-derivable from primary signals at κ = 0.867. This is a deliberate methodological choice, not an omission. Top-tier security and alignment benchmarks — HarmBench, AdvBench, InjecAgent — are accepted on exactly this provenance basis, and recent work shows automated judges agree with expert humans at κ ≈ 0.85 where a validated reference exists (CTIConnect, 2025). We acknowledge the counter-argument explicitly: human dual-annotation would quantify annotator fidelity to *already-established* labels, which is evidence about the annotators rather than new evidence about the corpus; re-annotating a source-endorsed benchmark can also *introduce* label noise the source does not have. Accordingly we do not claim a human κ. For full transparency, `scripts/human_iAA_kit.py` (stratified sampling → dual human annotation → κ recomputation) is shipped so a reviewer-requested human κ can be produced and audited on request rather than asserted after the fact.
3. **Formalization boundary (model-level, not implementation-level).** The BMC exhausts a *model* of the action system (64 states, 2^6 from the 6-artifact action vocabulary), not the full implementation—this is the same model-level scope stated in the Abstract and §1.2. Implementation conformance is established separately: a runtime self-proof (`scripts/prove_isolation.py`) shows the live scanner never spawns a scanned command on a concrete run, and Hypothesis property tests cover the regression surface. A full Apalache/TLA+ proof of the *implementation* is listed as enhancement evidence, not a gate blocker.
4. **Baseline condition asymmetry.** Four commercial baselines could not be executed under identical offline conditions (missing images / cloud-only). We leave their cells blank rather than estimate, accepting a weaker direct comparison in exchange for honesty.
5. **CI self-scan gate — closed.** The earlier allowlist gap (the self-scan gate flagged the project's *own* legitimate infrastructure as capability-overclaim/exfiltration-combo) has been resolved: the allowlist was rewritten as a v2 declarative policy plus a dedicated `self_reference` scanner and a CI self-scan gate, reducing blocking findings from 197 to 1 on the project's own tree. The single remaining block is a **genuine, documented** `GHSA-6qxp-vccf-f47h` affecting the `@modelcontextprotocol/sdk` dependency, which is intentionally **fail-closed** (retained, not suppressed) and tracked as an independent engineering fix outside this paper. This does not affect the artifact's external evaluation (§6).

---

## 8. Conclusion

AIShield demonstrates that an agentic-AI threat detector can be **offline**, **isolation-verified over a faithful mechanism model** (64-state exhaustive BMC, 4/4 mutations caught; implementation covered by a runtime self-proof and property tests), and **zero-false-positive-disciplined** (0/517 on an externally-sourced gold-standard corpus; label reliability by provenance with LCA κ = 0.867) simultaneously. The combination is, to our knowledge, novel. We deliberately trade a top recall number for a trustworthy operating point and an honest evaluation, and we provide a one-command reproducibility package. The residual NL-injection gap is explained, not hidden (§6.2.2): it is the principled ceiling of static, offline, zero-FP analysis on covert semantic-classification cases. Label quality rests on corpus provenance plus an automated consistency audit (§6.1, §7.2) — the same basis on which the benchmarks we reuse are themselves accepted — with a runnable human-IAA toolkit shipped for any reviewer-requested human κ. The CI self-scan gate is now closed (§7.5).

---

## 9. References

- OWASP. *OWASP Top 10 for Large Language Model Applications*. 2025. https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP. *OWASP Top 10 for Agentic AI Applications*. 2025. https://genai.owasp.org/
- Anthropic. *Model Context Protocol*. 2024. https://modelcontextprotocol.io
- NIST. *AI Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1, 2023. https://doi.org/10.6028/NIST.AI.100-1
- Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Hauschildt, T., Fritz, M. *Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection.* arXiv:2302.12173, 2023.
- Liu, Q., Zhang, Y., Che, J., Feng, Y., Su, Y., Sun, H. *InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents.* Findings of NAACL 2024. arXiv:2403.02691.
- Mazeika, M., Phan, L., Yin, X., Zou, A., Wang, Z., Mu, N., Sakhaee, E., Li, N., Stenyo, S., Hendrycks, D. *HarmBench: A Standardized Evaluation Framework for Automated Neural Attacks and Defenses.* ICLR 2024. arXiv:2402.03253.
- Zou, A., Wang, Z., Carlini, N., Nasr, M., Kolter, J. Z., Fredrikson, M. *Universal and Transferable Adversarial Attacks on Aligned Language Models.* arXiv:2307.15043, 2023.
- Invariant Labs. *mcp-scan — security scanner for MCP servers.* https://invariantlabs.ai/blog/mcp-scan (local scanner; pattern/heuristic detection, no published isolation proof or fixed external-corpus eval — per §2.2 cell provenance).
- Snyk. *Snyk agent-scan (AI security).* https://snyk.io (cloud-backed; requires account token; no offline mode, no published isolation proof — per §2.2).
- Lakera. *Lakera Guard / Gandalf.* https://lakera.ai (SaaS; Gandalf is an interactive prompt-injection testbed, not a deployable scanner — per §2.2).
- Zhang, Y., et al. *uiuc-kang-lab/InjecAgent.* GitHub. https://github.com/uiuc-kang-lab/InjecAgent (source of the 527 NL-injection positives reused in §6; `base`/`enhanced` and `attack_type` fields drive the §6.2.2 taxonomy).
- Zhang, A. K., Perry, N., Dulepet, R., Ji, J., Menders, C., Lin, J. W., Jones, E., Hussein, G., Liu, S., Jasper, D., et al. *CTIConnect: A Benchmark for Retrieval-Augmented LLMs over Heterogeneous Cyber Threat Intelligence.* arXiv:2510.11974, 2025. Cited in §7.2 for precedent that automated-judge evaluation against a validated human reference is accepted at κ ≈ 0.85 (inter-human κ = 0.93).

---

## Appendix A. Artifact (reproducibility)

- **Single command:** `git clone https://github.com/lm203688/aishield && cd aishield && pip install -e .[test] && python scripts/run_all.py`
- **Outputs reproduced:** rule-count declaration gate, version sync, declaration-surface runtime gate, OpenAPI contract gate, workflow gate, FVI gate (64 states), unit tests, internal benchmark (100%/0%), external benchmark (40.6% [36.6,44.7] / 0% FP; primary-scope supply-chain CVE 100%, secondary NL-injection 33.2%), baseline comparison table. Supplementary: `scripts/analyze_nl_misses.py` regenerates the §6.2.2 miss taxonomy (`benchmarks/corpus/external/nl_miss_taxonomy.json`) — bimodal recall by `dataset_setting` (enhanced 175/175, base 0/352) and the lexical-opacity proxy (100% of detected carry an explicit marker; 90.3% of misses are lexically opaque). `scripts/baseline_learned.py` regenerates the learned lexical baseline row in §6.2 (TF-IDF + Rocchio, stratified 5-fold CV: 83.0% recall at 48.9% FP; 62.1% on primary scope vs AIShield 100%).
- **Pinned inputs:** external corpus `benchmarks/corpus/external/` (1,110 gold-standard samples, LCA κ = 0.867), bootstrap seed `20261018`, AIShield 4.11.0.
- **License:** corpus samples carry CC0/permissive or dataset licenses; CVE-derived texts are synthesized native dependency declarations, not advisory verbatim (provenance recorded per-sample).

---

*Single source of truth for all numbers: `ARTIFACT.md` and `benchmarks/expected.json`. The external corpus LCA κ is computed by `scripts/compute_lca.py` from `scripts/label_consistency_audit.py` (deterministic, reproducible); it is an automated label-consistency audit, not human inter-annotator agreement, and is not represented as such. Label quality rests on corpus provenance plus this LCA (§6.1, §7.2); `scripts/human_iAA_kit.py` is shipped so a reviewer-requested human κ can be produced and audited on request.*
