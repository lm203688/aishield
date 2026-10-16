# Foresight AI for Science & Safety Nodes — Application

**Applicant:** [Name — pending user confirmation]
**Project:** AIShield — Local-First AI Tool Security Scanner
**Call:** Call II — Coordination and accountability
**Focus area:** 4. AI Insurance & Open Governance
**Deadline:** 2026-10-31 23:59 PDT (= 2026-11-01 14:59 CST; 38 days from 2026-09-23)
**Decisions expected:** January 2027 (stated on the application form)
**Submission URL (single short Airtable form, no login):** https://airtable.com/appyVXc5SMPAvIKpP/pagp7takV26cG6JY1/form

> See [`PLAYBOOK.md`](PLAYBOOK.md) for the verified field-by-field form structure, character limits,
> and the grantee comparison. The form's core pitch field is **350 characters, zero jargon** — this
> document is supporting material, not the submission itself.

---

## 1. Executive Summary

AI agent ecosystems (MCP servers, agent skills, GPTs, tool configs) are proliferating faster than anyone can audit them. Every week, hundreds of new agent skills are published to public marketplaces — most unverified, some malicious, none of them scanned at install time. Developers deploy them the same way they `pip install` from a public index: trust-by-default.

**AIShield** is a local-first, open-source scanner that catches:

- 235 MCP configuration attacks (208 static + 8 generated + 19 radar-discovered, the radar entries already counted inside the 235) covering supply-chain install scripts, tool-shadowing, egress, plaintext credentials, sandbox escape
- 262 Agent Skill attacks (prompt injection, memory poisoning, budget/payment surface, benchmark falsification, desktop-driver hijack)
- Both aligned to OWASP MCP Top 10 and OWASP Agentic AI Top 10 (ASI01–ASI10)
- 1295 automated tests, 22 real open-source harness files scanned with zero critical false positives

**What this funding buys:** we turn AIShield from a defensive scanner into an **independent assessment infrastructure** — the layer that insurance underwriters, procurement teams, and community governance bodies call when they need to decide "can we deploy this AI agent?" independently of the lab that built it.

Specifically, in 6 months we will:

1. Ship a **verifier-based rule promotion pipeline** (candidate rule → real-environment test → promoted only if it reproduces), aligned with the "verifier beats ruleset" thesis from Mano-P 2.0.
2. Publish a **public assessment API** (`aishield.tools/api/v1/trust`) that returns reproducible scan reports + JWKS-signed attestations anyone can call.
3. Build a **continuous-monitoring feed** that reports new AI tool supply-chain incidents as they happen — the incident-reporting infrastructure Foresight asks for.
4. Ship an **open assessment methodology paper** that other labs and governance bodies can adopt or reject on its merits.

---

## 2. Problem Statement

### 2.1 The trust gap in agent infrastructure

The three biggest agent distribution channels — Anthropic's community plugin marketplace, `awesome-mcp-servers` on GitHub, and `npm` for MCP servers — all accept uploads on pull request alone. None of them:

- Execute a security scan at submission time
- Provide a reproducible attestation a third party can verify
- Offer independent assessment separated from the vendor that shipped the tool

The result: **anyone with a GitHub account can publish a "plugin" that installs scripts, exfiltrates tokens, or shadows other tools.** The first wave of malicious MCP servers was documented by OWASP in their MCP Top 10, and the volume keeps growing.

### 2.2 Why self-assessment fails

The lab that builds a tool has three structural conflicts of interest:

1. **Incentive conflict** — the lab gets paid by shipping, not by not-shipping. A scanner inside the lab's CI has permission to skip tests when the product release deadline is close.
2. **Methodology conflict** — the lab's ruleset is shaped by what the lab considers an attack, not by what a downstream consumer would consider an attack.
3. **Disclosure conflict** — the lab controls which findings get public disclosure. A scanner inside the lab can quietly downgrade severity.

Foresight's Call II, focus area 4 (AI Insurance & Open Governance) calls this out explicitly: "Build ways for people **outside a lab** to assess risks." AIShield is designed from day one to be the outside-lab scanner.

### 2.3 What we already have

As of 2026-09-22:

| Asset | State |
|---|---|
| Codebase (MIT, `lm203688/aishield`) | 235 MCP rules (208 static + 8 generated + 19 radar) + 262 Skill rules |
| Test suite | 1295 tests, 100% pass, runs in <90s locally |
| Live API (`aishield.tools/api/v1`) | 24/7, CF-hosted, no auth required for public endpoints |
| Real-harness scan corpus | 22 files from PenguinHarness, Cua, Mano-P — 0 critical findings, 0 false positives on benign targets |
| Distribution | npm (`aishield-mcp-server`), Glama marketplace, GitHub Actions |
| 24/7 automation | Daily threat-intel radar (02:00 UTC), nightly monitor (08:30), weekly competitor scan, Sunday weekly digest |
| Benchmark methodology | Three-plane benchmark (serious_only / any_finding / harness attack surface), MIN_RECALL=0.85 gate in CI |

What we don't have yet:

- **Verifiable attestation** — no standard format anyone outside the project can verify
- **Independent assessment methodology** documented to a level a governance body would sign off on
- **Incident feed** that publishes findings as new tools get deployed
- **Public dataset** of scanned-tool outcomes over time

This funding closes these four gaps in 6 months.

---

## 3. Proposed Project

### 3.1 The four deliverables

**Deliverable A — Verifier-based rule promotion pipeline (Months 1–2)**

Move from "ruleset grows by human curation" to "candidate rule only promotes after an independent verifier reproduces it in a real environment." Directly addresses the risk that a curated ruleset drifts — becomes stale, over-fits its own test set, or silently regresses when new attack techniques appear.

Concrete milestones:

- Ship `engine/promote_verifier.py` as a first-class module (in progress, 350 LOC, 12 tests passing)
- Integrate with existing 24/7 radar so candidate rules flow through: radar discovers → verifier tests → human approves → CI gate enforces
- Publish the verifier's own benchmark (does it catch attacks a static rule misses? does it reject false positives a static rule accepts?)
- Open-source the entire pipeline so other scanners can adopt

**Deliverable B — Public assessment API with JWKS-signed attestations (Months 2–4)**

`aishield.tools` today returns scan results. Version 4.4+ will also return **signable attestations** — a JWKS endpoint exposes an Ed25519 public key, and every scan result includes an HMAC-SHA256 signature over the canonicalised result. Anyone can call the API and verify they got the same result a governance body got, without trusting the API's uptime.

Concrete milestones:

- `.well-known/jwks.json` endpoint live (prototype already pushed to SwarmLabs sibling project — porting pattern)
- Key rotation workflow (90-day cycle, revocation list at `.well-known/jwks/revoked.json`)
- OpenAPI schema published, SDKs for Python + Node.js
- Rate-limited public endpoint + authenticated tier for governance bodies

**Deliverable C — Incident feed (Months 3–5)**

Turn the existing 24/7 radar into a **public, timestamped, append-only incident feed**. Every new attack technique discovered (whether from a new malicious MCP server, a new skill-marketplace entry, or an arXiv paper describing a new injection vector) becomes a public record with:

- Detection timestamp (UTC, second precision)
- Rule that caught it (with source pointer)
- Sample payload (redacted for safety)
- Whether any active deploy already has this risk

This is the "independent incident reporting" Foresight calls for. It's not another security blog — it's a machine-readable, verified feed with a stable API contract.

**Deliverable D — Assessment methodology paper (Month 6)**

A preprint-length paper (8–12 pages) describing:

- The rule promotion methodology and its empirical accuracy on the harness corpus
- The signature/attestation design and its threat model
- The methodology for calibrating the confidence scores
- Open questions and known limitations

Forkable, critiquable, adoptable. The paper is the durable output — the code changes every quarter, but the methodology has to be something a governance body can pin a policy to.

### 3.2 Alignment with Foresight's mandate

Foresight's Call II focus area 4 says, in their words:

> "Build ways for people outside a lab to assess risks... independent incident reporting... independent technical assessment."

We map each:

| Foresight mandate | AIShield deliverable |
|---|---|
| Independent technical assessment | Deliverable A + B (verifier + signed attestations) |
| Outside-a-lab assessment | Structural — AIShield is a standalone MIT project, not a subsidiary of any model lab |
| Incident reporting | Deliverable C (append-only feed) |
| Open, verifiable, reproducible | Deliverables A, B, D all produce public artifacts |
| Community governance | Methodology paper (D) + open pipeline (A) means any community can adopt |

### 3.3 What makes this different from competitors

| Competitor | What they do | Gap we fill |
|---|---|---|
| Sonatype Nexus Trust | SCA + license check for traditional OSS | Not MCP/agent-specific; no ruleset trained on 2024-2026 agent attack surface |
| OWASP MCP Top 10 | Framework document | Not a scanner; provides rules, not runtime detection |
| Anthropic / OpenAI internal safety | Lab-owned scanners | Structural conflict of interest — see §2.2 |
| Semgrep / CodeQL | General-purpose SAST | Not trained on MCP/agent attack patterns; requires heavy rule authoring |
| VirusTotal | General malware scanning | Doesn't handle JSON config / markdown skill files as first-class artifacts |
| AIsa AgentPay Guard | Payment-focused | Narrow scope — misses the broader 235+262 attack surface |

AIShield is the only scanner whose entire ruleset is trained specifically on the 2024–2026 AI agent supply chain.

---

## 4. Timeline

Six months from funding notification (assuming notification by 2027-01-31 based on Foresight's stated review cycle).

| Month | Milestone |
|---|---|
| M1 | Verifier pipeline v1.0 with 5 promoted rules |
| M2 | Verifier + radar integration; CI gate enforcing verifier pass |
| M3 | JWKS endpoint live; signed attestation in public API |
| M4 | Python + Node SDK; OpenAPI schema; rate limiting |
| M5 | Incident feed v1 with 30+ historical backfill entries |
| M6 | Methodology paper preprint + public beta of the entire stack |

Each milestone has:

- A pull request merged to main
- A test suite green across 1295+ tests
- A public changelog entry
- A blog post on `aishield.tools/blog` (existing 12-post archive)

---

## 5. Team

### Principal investigator

[Name — pending user confirmation]

- Maintainer of AIShield (sole developer, MIT license)
- 3+ years building open-source security tooling
- Prior work on supply-chain scanning for Python, npm, and Go ecosystems
- Available full-time for the 6-month project period

### Advisors (soft, not required for funding)

- Community contributors to OWASP MCP Top 10 (potential, contact pending)
- Foresight SF / Berlin Node researchers (potential, contact pending)

### What we're not asking for

- Headcount expansion — this project is designed to be runnable by one senior engineer with 6 months
- Travel budget — see [BUDGET variants] for the in-person participation decision
- Subcontracting — the whole point of "outside a lab" is that the person doing the work is independent

---

## 6. Risk assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Rule promotion gate adds latency to radar → missed real-time incidents | Medium | Cache verifier results; run against known-corpus first, only re-run on new samples |
| JWKS signing key compromised | Low | Rotation workflow every 90 days; public revocation list; HMAC fallback for degraded mode |
| Attenuation: users don't check signatures | High | Provide one-line CLI `aishield verify <report.json>`; bake into CI samples |
| Attackers target the scanner itself (PoisonedAIShield attack) | Medium | Self-scan (`self_scan.py`) runs on every CI commit; ruleset is versioned and content-addressed |
| Foresight requires in-person participation and applicant cannot travel | **Highest** | Two budget variants provided — individual (independent, no travel) vs. corporate (with 2 trips to SF/Berlin) |
| 6-month timeline slips due to solo development | Medium | Milestones are additive (M1 output is still useful even if M6 slips); paper can be preprint-early |

---

## 7. Expected impact

If successful, six months after notification:

- **~500 total rules** (up from 235+262) with verifier-promoted entries marked separately
- **Signed attestation API** consumed by at least 3 external governance bodies
- **Incident feed** with 100+ timestamped entries, adoptable by any downstream consumer
- **Methodology paper** cited or forked by at least one other scanner project
- **Community adoption**: a real, earned usage number. *Correction 2026-09-23: the earlier draft of
  this line claimed "500+ GitHub stars (currently ~100)". The verified figures are **2 stars and 0
  forks** — the claim was inflated by two orders of magnitude and has been removed. The honest target
  for the grant period is to establish a **measurable install/scan count** (npm downloads, Glama
  installs, CI runs) and report that, rather than repositorial popularity.*

Not claimed, but a plausible upside: AIShield becomes the reference implementation for "independent AI tool assessment" that insurance underwriters can point to when a customer asks "who audited this agent?"

---

## 8. Appendix: Existing evidence

- **Code**: https://github.com/lm203688/aishield (public, MIT)
- **Live API**: https://aishield.tools/api/v1/health
- **Benchmark report**: https://aishield.tools/blog/agent-security-benchmark-2026/
- **Rule count verified live**: 235 MCP + 262 Skill (see `/api/v1/health` `rules_breakdown`)
- **Real-harness corpus**: 22 files from PenguinHarness, Cua, Mano-P — 0 critical, 0 false positive
- **Distribution**: `aishield-mcp-server` on npm, `lm203688/aishield` on GitHub, Glama marketplace entry

---

*This document is the master application. Submit via https://foresight.org/grants/ai-science-safety-nodes-rfp/. Attach PROJECT_PLAN.md, the appropriate BUDGET variant, and SUBMISSION_CHECKLIST.md as supporting files.*
