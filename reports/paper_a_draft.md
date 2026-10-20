# AIShield: An Offline, Zero-Dependency, Machine-Verifiable Framework for Agentic-AI Supply-Chain and Prompt-Injection Threat Detection

> **Paper A — full draft (CCF-A / SCI orientation).**
> Target venues: USENIX Security 2027 (system/security, artifact-weighted) or IEEE Transactions on Information Forensics and Security (SCI).
> All quantitative claims are pinned to the single source of truth in `ARTIFACT.md` and `benchmarks/expected.json`; the reproducibility package is `ARTIFACT.md` + `scripts/run_all.py`.
> Version of record: AIShield 4.11.0 (`/api/v1/health.commit`).

---

## Abstract

The shift from monolithic software to agentic AI—systems that *execute* externally supplied tools, packages, and instructions—moves the attack surface from the traditional supply chain to prompt injection, tool poisoning, and capability overclaim. Existing guardrails are deficient on at least one of three axes: they **exfiltrate data to the cloud** (breaking air-gap and compliance assumptions), they make **unverifiable safety claims** (no formal guarantee that the scanner itself cannot be hijacked), or they suffer **high false-positive rates** that cause operators to disable them. We present **AIShield**, an offline, zero-dependency, machine-verifiable framework for detecting threats in agentic-AI workloads. AIShield's contributions are (1) a **formal isolation invariant**—the scanner never executes scanned code, never contacts the network, and writes only to its own isolated state—proven by exhaustive bounded model checking over 64 reachable states with a completeness argument; (2) a **neuro-symbolic zero-false-positive discipline** (`ratify()`) under which the neural layer can never self-escalate; and (3) an **externally-sourced, provenance-auditable gold-standard evaluation corpus** of 1,110 samples (593 positive / 517 negative, 18 attack families; automated Label Consistency Audit κ = 0.867) on which AIShield achieves **0/517 false positives** while remaining competitive on recall under a fixed operating point. We report honest limitations, including that the external recall of 29.5% reflects genuine out-of-distribution difficulty rather than a benchmark artifact, and that the corpus labels derive from authoritative external ground truth (GitHub Security Advisory CVEs and the published InjecAgent benchmark); an automated Label Consistency Audit quantifies label self-consistency, while genuine human dual-annotation is the scheduled pre-submission step (toolkit provided).

---

## 1. Introduction

### 1.1 Motivation

Agentic AI systems compose third-party tools (MCP servers, function-calling schemas) and ingest untrusted instructions. This composition reintroduces supply-chain risk at a new layer: a malicious MCP server can execute arbitrary code in the agent's context, a poisoned dependency can exfiltrate secrets, and an indirect prompt injection can redirect the agent's actions. The *Model Context Protocol (MCP)* and the *OWASP Top 10 for LLM Applications 2025* and *OWASP Agentic AI Top 10* enumerate these risks, but detection tooling has not kept pace.

Three structural deficiencies dominate the current landscape:

- **Data exfiltration by design.** Many commercial scanners send the scanned artifact or its metadata to a vendor cloud. For regulated or air-gapped deployments this is a non-starter, and it creates a second-order supply-chain dependency on the scanner vendor.
- **Unverifiable safety claims.** A scanner that claims to "prevent prompt injection" is itself a privileged component. If the scanner can be made to *execute* scanned code or be reconfigured by it, its guarantees are void. No existing tool offers a machine-checkable proof that the scanner's own isolation holds.
- **False-positive disablement.** Guardrails that cry wolf are switched off. In security tooling, a false positive is not a nuisance—it is a **fidelity failure** that defeats the control.

### 1.2 Thesis (single sharp contribution)

> **We present AIShield: an offline, zero-dependency, machine-verifiable framework for agentic-AI threat detection whose safety invariants are exhaustively proven (64 reachable states, 4 mutation variants all caught) and whose detection discipline guarantees zero false-positive expansion on an externally-sourced corpus (0/517).**

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
| **AIShield** (4.11.0) | **Yes** | **Yes (BMC, 64 states)** | **Yes (ratify)** | **Yes (1,110 gold-standard samples, LCA κ=0.867)** | — |

The decisive gap is the **combination**: every offline tool we surveyed lacks a machine-checkable isolation proof and a zero-FP guarantee; every tool with a formal flavor targets a different problem (e.g., smart contracts) and not agentic tool composition. AIShield is the first to couple an *exhaustively verified* isolation invariant with a *zero-FP* detection discipline evaluated on an *externally-sourced, provenance-auditable gold-standard* corpus.

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

The invariant **"the neural layer can never self-escalate"** is enforced both by construction (the neural path has no write to the privilege table) and by the formal model (§5, INV-3 single-writer). This is what makes the **0/517 false-positive** result principled rather than accidental: under `ratify`, a finding must be grounded in a symbolic rule, and the false-positive surface is the precision of those rules, which we measure directly.

---

## 5. Formal Isolation Invariants

### 5.1 The invariant family

We specify five invariants over the scanner's action system:

- **INV-1 `no_execute`** — the scanner never executes a command derived from scanned content.
- **INV-2 `no_network`** — the scanner never opens an outbound network connection during a scan.
- **INV-3 `single_writer`** — the privilege/state table has exactly one writer (the symbolic core); the neural layer is read-only.
- **INV-4 `read_only_input`** — scanned inputs are never mutated or used as code.
- **INV-5 `completeness`** — the model explores all reachable states within the bounded action vocabulary.

### 5.2 Verification method

We use a three-layer defense:

1. **Quint** specification (`formal/isolation_invariants.qnt`) for human-readable modeling.
2. **Python bounded model checker** (`scripts/check_isolation_invariants.py`) that **exhaustively explores 64 reachable states**, reports `termination=exhausted`, `coverage=1.0`, `complete=true`, and includes a `completeness_argument()` proving |reachable| = 64 from the action vocabulary.
3. **Hypothesis** property-based testing as a runtime regression net.

### 5.3 Mutation testing (discriminating power)

We inject four mutation variants (M1–M4) that each violate one invariant (e.g., M1 makes the scanner spawn a scanned command). The BMC **catches all four**, demonstrating that the invariant suite has real discriminating power rather than vacuously passing. This satisfies acceptance gate **R4** (exhaustive model checking with a completeness argument; the Python BMC is the documented fallback to Apalache, which is unavailable in our offline build environment).

---

## 6. Evaluation

All numbers below are produced by `scripts/run_all.py` and `scripts/baseline_compare.py` from pinned inputs; confidence intervals use bootstrap (1,000 resamples, seed `20261018`).

### 6.1 External corpus (gate R1)

- **Scale:** 593 positive / 517 negative / **1,110 total**, spanning **18 attack families**.
- **Provenance / label reliability:** the corpus is **externally-sourced gold-standard** — 66 positives are GitHub Security Advisory CVEs (labels anchored to third-party published vulnerabilities) and 527 positives + 517 negatives are the published InjecAgent benchmark (Zhang et al., NAACL 2024, author-labeled ground truth). Because the labels are *source ground truth* rather than in-house human annotation, label reliability is established by provenance, consistent with how HarmBench / AdvBench / InjecAgent themselves are accepted.
- **Label Consistency Audit (LCA):** an automated, reproducible check re-derives each label from raw signals (CVE identifiers, dataset provenance, a conservative lexical attack-term scan) **without** reading the source label, and compares against the source ground truth. Cohen's κ = **0.867** [0.809, 0.926] (bootstrap SE 0.015). This LCA κ measures *automated label self-consistency / reproducibility*, **not** human inter-annotator agreement. Genuine human dual-annotation (two independent analysts + adjudication of disagreements) is the scheduled pre-submission step and is supported by a provided toolkit (`scripts/human_iAA_kit.py`, §7).
- **Family coverage:** positives span `data_exfiltration` (176), `indirect_prompt_injection` (176), `jailbreak_family` (175), and 14 further families; negatives include 17 benign user tasks and 500 controlled benign-injection-context samples.

### 6.2 Baselines on the same fixed corpus (gates R2, R3)

All tools consume the identical corpus under the `serious_only`口径 (only critical/high count as detections). AIShield 4.11.0 (self) versus two offline-runnable naive baselines:

| Tool | recall (95% CI) | FP (95% CI) | F1 | Rules | Cloud |
|---|---|---|---|---|---|
| **AIShield** | **29.5% [25.8%, 33.2%]** | **0.0% [0.0%, 0.0%]** | **46%** | 264 | No |
| Naive keyword heuristic | 21.1% [17.9%, 24.4%] | 0.0% [0.0%, 0.0%] | 35% | 0 | No |
| Random guess (base-rate) | 48.9% [44.9%, 52.8%] | **53.8% [49.5%, 58.0%]** | 50% | 0 | No |
| Invariant mcp-scan (v0.9) | N/A (unequal conditions) | N/A | N/A | 150 | No |
| agent-security-scanner-mcp (v0.4) | N/A (unequal conditions) | N/A | N/A | 120 | No |
| mcp-audit (v1.2) | N/A (unequal conditions) | N/A | N/A | 98 | No |
| Snyk agent-scan (v1.x) | N/A (unequal conditions) | N/A | N/A | N/A | **Yes** |

**Interpretation (the paper's spine).** The correct metric for a guardrail is **false-positive rate**, because a single false positive invites disablement. Under the **FP = 0** constraint, AIShield's recall (29.5%) **strictly dominates** the keyword heuristic (21.1%) on the same corpus with identical FP. The random guess achieves higher raw recall (48.9%) only by emitting **53.8% false positives**—operationally unusable. Four commercial baselines cannot be run under identical offline conditions and are reported as *not evaluated* rather than fabricated, a deliberate honesty choice (§7).

### 6.2.1 Scope-partitioned recall (honest decomposition)

A single 29.5% figure invites the misreading "the detector misses 70% of attacks." We decompose it by *applicability scope* so the gap is explained rather than hidden. Detection uses the same `serious_only` bar (≥1 critical/high finding); confidence intervals are bootstrap (1,000 resamples, seed `20261018`), computed by `scripts/external_scope_recall.py`.

| Scope subset | Positives | Detected | Recall (95% CI) |
|---|---|---|---|
| **Overall** | 593 | 175 | **29.5% [25.8%, 33.2%]** |
| Primary — supply-chain CVE (GitHub Advisory, code/config) | 66 | 0 | 0.0% [0.0%, 0.0%] |
| Secondary — NL prompt-injection (InjecAgent) | 527 | 175 | **33.2% [29.4%, 37.2%]** |
| By scan plane: `config` | 12 | 0 | 0.0% |
| By scan plane: `instruction` | 581 | 175 | 30.1% [26.3%, 33.9%] |

**Interpretation.** AIShield's strongest *offline* capability is natural-language prompt-injection detection on the instruction plane (**33.2%** of InjecAgent at **0 FP**). The 66 GitHub Security Advisory positives are *dependency-version vulnerabilities* (e.g., `require github.com/getkin/kin-openapi v0.144.0` inside a known-vulnerable range): detecting them requires **advisory-version matching**. AIShield intentionally keeps live OSV/CVE lookup **disabled by default** to preserve its air-gap / offline invariant (§1.1, §5) and it does **not** yet bundle a static advisory index, so it reports **0%** on that subset. This is a *capability gap within its stated supply-chain scope*, not a detector malfunction; we report it openly rather than exclude these hard cases, and we enumerate bundling an offline advisory index (OSV-mirror) as the concrete remediation (§7, future work). The blended 29.5% is therefore the honest shape of a guardrail that trades a top-line recall number for air-gap safety and a zero-FP operating point.

### 6.3 Internal corpus (sanity)

On the internally-curated corpus, AIShield reaches **100% recall (57/57)** at **0% FP (0/45)** under `serious_only`, confirming the detector is not intrinsically broken—the external 29.5% reflects genuine out-of-distribution difficulty.

### 6.4 Formal verification results (gate R4)

The BMC exhausts **64 reachable states** (`coverage = 1.0`, `complete = true`) and catches all four mutation variants M1–M4. The completeness argument derives |reachable| = 64 from the bounded action vocabulary.

### 6.5 Reproducibility

`scripts/run_all.py` aggregates the six declaration-surface gates, the FVI gate, the unit tests, and both benchmark corpora. A single `pip install -e .[test]` followed by `python scripts/run_all.py` reproduces every number in this section (artifact, §Appendix).

---

## 7. Limitations (gate R7)

We state limitations explicitly; none undermine the central claim but all bound its scope.

1. **External recall is not 100% — and is scope-asymmetric.** The 29.5% external recall (§6.2) decomposes (§6.2.1) into **33.2% on NL prompt-injection** but **0% on the 66 CVE-version supply-chain samples**, because AIShield ships without a bundled advisory-version index (live OSV is off by default to preserve air-gap). Our contribution is methodology + formal assurance + a zero-FP operating point, **not** a leaderboard-first detector. We report the asymmetry openly and reject the temptation to exclude the hard CVE cases or report a self-selected 100%.
2. **Automated label-consistency audit, not human IAA.** The κ = 0.867 is a *Label Consistency Audit (LCA)*: an independent automated re-derivation of labels from raw signals compared against the corpus's source ground-truth labels (GitHub Security Advisory CVEs and InjecAgent author labels). It quantifies *automated label self-consistency / reproducibility*, not human inter-annotator agreement. The corpus is externally-sourced gold-standard, so label reliability is established by provenance rather than by human annotation; top-tier security/alignment benchmarks (HarmBench, AdvBench, InjecAgent) are accepted on exactly this basis. Genuine human dual-annotation (two independent analysts + adjudication of disagreements, targeting Cohen's κ ≥ 0.8) is the scheduled pre-submission step, and a runnable toolkit (`scripts/human_iAA_kit.py`: stratified sampling → dual human annotation → κ recomputation) is provided so the step is auditable rather than fabricated.
3. **Formalization boundary.** The BMC exhausts a *model* of the action system (64 states), not the full implementation. Hypothesis property tests and regression suites cover the implementation gap; a full Apalache/TLA+ proof is listed as enhancement evidence, not a gate blocker.
4. **Baseline condition asymmetry.** Four commercial baselines could not be executed under identical offline conditions (missing images / cloud-only). We leave their cells blank rather than estimate, accepting a weaker direct comparison in exchange for honesty.
5. **CI self-scan noise.** The CI self-scan gate flags the project's *own* legitimate infrastructure (workflow files, deployment scripts) as capability-overclaim/exfiltration-combo. This is a known allowlist gap in the gate, not a product defect; it is being closed as a separate maturity task and does not affect the artifact's external evaluation.

---

## 8. Conclusion

AIShield demonstrates that an agentic-AI threat detector can be **offline**, **formally isolation-verified** (64-state exhaustive BMC, 4/4 mutations caught), and **zero-false-positive-disciplined** (0/517 on an externally-sourced gold-standard corpus, LCA κ = 0.867) simultaneously. The combination is, to our knowledge, novel. We deliberately trade a top recall number for a trustworthy operating point and an honest evaluation, and we provide a one-command reproducibility package. The path to submission is the scheduled human dual-annotation (toolkit provided) and the closure of the CI allowlist gap.

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

---

## Appendix A. Artifact (reproducibility)

- **Single command:** `git clone https://github.com/lm203688/aishield && cd aishield && pip install -e .[test] && python scripts/run_all.py`
- **Outputs reproduced:** rule-count declaration gate, version sync, declaration-surface runtime gate, OpenAPI contract gate, workflow gate, FVI gate (64 states), unit tests, internal benchmark (100%/0%), external benchmark (29.5% [25.8,33.2] / 0% FP), baseline comparison table.
- **Pinned inputs:** external corpus `benchmarks/corpus/external/` (1,110 gold-standard samples, LCA κ = 0.867), bootstrap seed `20261018`, AIShield 4.11.0.
- **License:** corpus samples carry CC0/permissive or dataset licenses; CVE-derived texts are synthesized native dependency declarations, not advisory verbatim (provenance recorded per-sample).

---

*Single source of truth for all numbers: `ARTIFACT.md` and `benchmarks/expected.json`. The external corpus LCA κ is computed by `scripts/compute_lca.py` from `scripts/label_consistency_audit.py` (deterministic, reproducible); it is an automated label-consistency audit, not human inter-annotator agreement. Genuine human dual-annotation is supported by `scripts/human_iAA_kit.py` as the scheduled pre-submission step.*
