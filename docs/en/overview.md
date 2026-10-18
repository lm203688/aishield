# AIShield — Overview

AIShield is an agent-native, local-first security scanner and trust authority for the MCP / Agentic AI economy.

## What problem it solves

Every MCP server is arbitrary code. When an agent loads an MCP server, it reads the server's `tools/list` — which typically requires starting the server process. Any scanner that spawns the config it inspects has already executed arbitrary code under the guise of a "security check." AIShield refuses to do that: **the scanner reads configurations and source statically, and never spawns or executes anything from what it scans.**

This is not a soft guideline. `scripts/prove_isolation.py` patches `subprocess.Popen`, `os.system`, and `subprocess.run` to raise on any call, then loads the scanner against a hostile-looking config and asserts zero spawn invocations. If this invariant ever breaks, the scanner has been compromised.

## Two standards, aligned

AIShield ships with rule sets for both standards in parallel:

| Standard | Coverage | Rules |
|---|---|---|
| **OWASP MCP Top 10 (2025 v0.1)** | MCP01–MCP10 | 128 |
| **OWASP Agentic AI Top 10 (ASI01–ASI10, AIShield internal)** | ASI01–ASI10 | 75 |
| Sandbox / host-escape heuristics | — | 12 |
| Chinese-language prompt injection | — | 22 |
| **Static subtotal** | | **237** |
| Threat-intel generated (daily radar) | — | 8 |
| Radar-promoted (weekly) | — | 19 |
| **MCP-type total** | | **264** |
| Skill-specific extra | — | +27 |
| **Skill-type total** | | **291** |

The authoritative number is always what `GET /api/v1/health` reports as `rules_breakdown`. Every other number in the repo is derived from that.

> **Note on `ASI0x` labels.** The `owasp_category` field carries **two namespaces**: `MCP01`–`MCP10` are official OWASP MCP Top 10 codes; `ASI01`–`ASI10` are AIShield's **internal** IDs. Only `ASI01`/`ASI02`/`ASI03` coincide with the official OWASP Agentic AI Top 10 (2026). Most Agentic scanners emit `MCP0x` and miss the internal `ASI0x` findings. The machine-readable crosswalk is the `internal_to_owasp_agentic` field returned by `compliance_summary()`; source of truth is `scanner/compliance.py`.

## Architecture in one paragraph

`scanner/engine.py` is the entry point. It loads `scanner/rules.py` (237 static + dynamic rule sets from `data/`), runs the neuro-symbolic probe (`scanner/neuro_symbolic_probe.py` — symbolic layer as constitution, semantic layer as recall enhancer only, never self-escalates), and produces a scored report. `api/server.py` wraps this as an HTTP service; `mcp-server/src/index.ts` wraps it as an MCP server; both call the same engine. There is no duplicate logic.

## Zero-cost, offline-first

- **Zero third-party runtime dependencies** — Python standard library only. `cryptography` and `pyyaml` are optional for advanced features (Ed25519 signing, YAML parsing) but not for the core scan path.
- **Fully offline** — no code, no configuration, and no scan results ever leave the machine. The scanner does not phone home.
- **Local SLM optional** — a llama.cpp-based GGUF backend can be plugged into the semantic layer for broader recall, but the default `DeterministicHeuristicBackend` requires nothing and is sufficient for production.

## Trust layer

AIShield signs its own outputs. Every attestation is Ed25519-signed (JWKS published at `/.well-known/jwks.json`), and the identity is a portable `did:key`. Third parties can verify any attestation offline with just the public key.

The scanner also verifies itself: `distribution/published.json` is a public ledger of every channel AIShield is published on, with source-of-truth links back to the repo.

## Where AIShield is published

- npm: <https://www.npmjs.com/package/aishield-mcp-server> (v4.11.0, sigstore-provenance)
- GitHub: <https://github.com/lm203688/aishield> (MIT)
- Smithery: <https://smithery.ai/server/aishield>
- Agensi: chinese-seo-compliance skill
- Live API: <https://aishield.tools>

## Related documents

- [Quick Start](./quickstart.md)
- [Deployment](./deployment.md)
- [Trust attestation quickstart](../trust-attestation-quickstart.md)
- [Agent ecosystem landscape](../agent-ecosystem-2026-landscape.md)
- [Competitive landscape](../competitive-landscape-2026-09.md)
