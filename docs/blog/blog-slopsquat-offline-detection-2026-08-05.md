---
title: "Half of AI-Hallucinated Packages Look Nothing Like Real Ones — Here's How We Detect Them Offline"
date: 2026-08-05
tags: [supply-chain, slopsquatting, mcp, agentic-ai, owasp, offline-security]
canonical: https://aishield.tools/blog/slopsquat-offline-detection-2026-08-05
---

# Half of AI-Hallucinated Packages Look Nothing Like Real Ones

*Why edit-distance typosquat detection structurally misses slopsquatting — and how to catch it with zero network calls.*

## The number that should worry you

USENIX Security 2025 tested 16 models across 576,000 code samples. **19.7% of recommended packages did not exist.** That produced **205,474 unique fabricated package names** — each one a registrable, empty namespace slot.

A 2026 replication study on five frontier models narrowed the range from 5.2%–21.7% down to 4.62%–6.10%. Better. Not zero. And it does not matter much, because the attack economics already flipped:

- **43–58% of hallucinated names recur deterministically.** The attacker's targeting problem is solved by the models themselves.
- Registering a name costs a signup. No maintainer compromise, no malicious commit, no trust-building release history.
- Every increment of agent autonomy removes another human between the hallucination and `npm install`.

## The part most scanners get wrong

Here is the structural problem, stated plainly:

> **Roughly half of hallucinated package names are not misspellings of anything.**

Typosquatting exploits human typing errors, so registries and scanners defend with similarity: edit distance, homoglyph normalization, keyboard-adjacency. Those defenses work because a typo is, by definition, *near* a real name.

Slopsquatting is different. A model does not mistype — it **composes**. It assembles a plausible name out of ecosystem naming conventions. The result is a name that is semantically obvious and lexically novel.

The canonical case is `react-codeshift`, January 2026. It fuses two real tools — `jscodeshift` (a codemod toolkit) and `react-codemod` (React migration scripts) — into a name that never existed. Its edit distance to both parents is large. **No similarity scanner fires.**

Then came the propagation vector that makes this a 2026 problem rather than a 2025 curiosity: `react-codeshift` spread through **237 repositories via AI-generated agent skill files**. An agent wrote a setup instruction referencing it. That file was committed. Other agents read that file as authoritative context and repeated the dependency into their own output.

No human planted it. The fabricated name propagated agent-to-agent as a self-reinforcing artifact. **A hallucination committed once becomes ground truth for every agent that reads it afterward.** The error does not decay; it compounds.

That slot was never weaponized — which is why it is a near-miss and not a breach. 237 repositories were one registry signup away.

## What AIShield ships today (v4.2.0+, released 2026-08-05)

Our previous supply-chain layer did edit-distance typosquat + homoglyph normalization + brand impersonation. Honest assessment: that covered the *other* half.

The new `check_package_name()` adds three offline channels, and a new `check_dependency_hygiene()` covers the manifest level:

### 1. Composite hallucination advisory (the non-similar half)

A name is flagged when it is a multi-segment composite, contains at least one **ecosystem anchor token** (`react`, `langchain`, `mcp`, `openai`, `fastapi`, `huggingface`, …), and is absent from the trusted catalog.

```
react-codeshift        -> suspected_hallucinated_package (info)
langchain-mcp-toolkit  -> suspected_hallucinated_package (info)
huggingface-cli-tools  -> suspected_hallucinated_package (info)

react-router-dom       -> clean
langchain-community    -> clean
pytest-asyncio         -> clean
```

Severity is deliberately **`info` — zero score deduction**. Offline we cannot prove a package does not exist; we can only say *this name has the shape of a fabrication, verify it before install*. Advisories are capped at 5 per manifest so a monorepo does not drown the report. Being loud and wrong is worse than being quiet and right.

### 2. Cross-registry confusion

Research found **8.7% of Python-hallucinated names already exist on npm.** In polyglot repos where agents scaffold Node and Python side by side, a Python-flavored hallucination can resolve against npm — to whatever an attacker registered there.

```
express       in requirements.txt -> cross_registry_confusion (medium)
beautifulsoup4 in package.json    -> cross_registry_confusion (medium)
```

### 3. Dependency confusion / internal namespace leakage

Internal namespace tokens (`internal`, `corp`, `private`, `intranet`, …) appearing in a public manifest mean the public registry can be squatted with the same name and win resolution.

### 4. Manifest hygiene

- `install_script_execution` (**critical**) — `preinstall`/`postinstall`/`prepare` invoking `curl`, `wget`, `base64 -d`, `chmod +x`, `bash -c`, `powershell`, `certutil`, `eval`.
- `untrusted_dependency_source` (**high**) — `git+`, `http://`, `file:`, `github:`, tarball URLs.
- `unpinned_dependency` (**medium**) — `*`, `latest`, empty spec.
- `missing_lockfile` (**low**) — declared dependencies with no lockfile. A hallucinated name has no lockfile entry, so `npm ci` **fails closed**. This is the single highest-leverage control in the whole class, and it is boring.
- `dependency_confusion` (**medium**) — `--extra-index-url` in `requirements.txt`.

## Measured false-positive rate

Heuristics that cry wolf get switched off, which is a security failure with extra steps. We sampled 40 real, widely-used packages (20 npm, 20 PyPI) including hard composites like `react-router-dom`, `langchain-community`, `@modelcontextprotocol/sdk`, `pytest-cov`, `python-dotenv`:

> **0 / 40 false positives.**

Detection on a malicious/suspicious sample: 6 / 7. The miss is `requesocks` — a historic `requests` typosquat at edit distance 4, which sits outside our distance-2 threshold and has no ecosystem anchor. We would rather miss that one than flag `react-router-dom`.

Test suite: **127 passing** (99 → 127, +28 for this feature).

## Why offline matters here

Competitors solve hallucination detection two ways: ship a **4.3-million-package local database**, or query the live registry at scan time.

Both work. Both also mean your dependency graph — a precise fingerprint of your internal architecture, vendor relationships, and unreleased features — either bloats your install or leaves your machine.

AIShield runs on **pure heuristics: zero network calls, zero third-party dependencies, zero package database.** Registry existence, package age, and download-count verification remain available as an *optional remote* step. Default is offline. That is not a limitation we are apologizing for; it is the product.

## The honest caveat

An offline heuristic cannot prove a package exists. What it does is **reduce an unbounded verification problem to a short, ranked list** a human or a CI gate can actually act on.

The full defense stack is still the boring one, and you should run all of it:

1. Committed lockfiles + `npm ci` / hash-pinned installs (fails closed on any hallucinated name)
2. Existence-and-age gating before a new dependency lands
3. Provenance verification (Sigstore) as an audit layer
4. A merge-blocking human review on every agent-added dependency
5. `--ignore-scripts` by default

AIShield's job is item 2's cheap front half, running in your CI, on your machine, for free.

## The shift underneath all of this

AI-generated code gets reviewed for logic. AI-generated **dependency lists** get executed on trust.

In the agentic era the import statement *is* the attack surface. Treat every package name a model proposes as unverified input from the internet — because the moment an attacker registers it, that is exactly what it becomes.

---

**Try it**

```bash
npx aishield-mcp-server        # MCP server (stdio)
```

- GitHub: https://github.com/lm203688/aishield
- Trust API: https://aishield.tools/api/v1/trust/score/{did}
- SARIF / CycloneDX export for CI gating: `/api/v1/export/sarif`, `/api/v1/export/sbom`

Local-first. MIT. 201 rules across OWASP MCP Top 10 + OWASP Agentic AI Top 10 (ASI01–ASI10).

**Sources:** USENIX Security 2025 package-hallucination study · 2026 five-model replication study · `react-codeshift` incident analysis (Jan 2026) · CoSAI Workstream 4, *MCP Security* & *Agentic Identity and Access Management* (Mar–Apr 2026) · Palo Alto Unit 42 multi-MCP attack-success research · Cisco agent-skills survey (31,000+ skills)
