# AIShield — Architecture

## Layered design

```
┌─────────────────────────────────────────────────────────────┐
│  MCP server (TS)  │  HTTP API (Python)  │  CLI (Python)    │  ← Entry points
├─────────────────────────────────────────────────────────────┤
│  engine.py ────── loads rules.py + neuro_symbolic_probe.py  │  ← Core
├─────────────────────────────────────────────────────────────┤
│  scanner/*  ───── memory_integrity_scan, identity_scan,     │  ← Detectors
│                   network_scan, policy_pack, red_team_probe │
├─────────────────────────────────────────────────────────────┤
│  eco/*        ───── attestation, evolution_ledger,          │  ← Trust layer
│                   meta_agent, crypto_sign, guardrail_harness│
├─────────────────────────────────────────────────────────────┤
│  api/*        ───── governance_api, ecosystem_support_api   │  ← REST endpoints
├─────────────────────────────────────────────────────────────┤
│  scanner/rules.py  ──── 286 static + 8 intel + 19 radar    │  ← Rule registry
└─────────────────────────────────────────────────────────────┘
```

## Scan pipeline

1. **Discovery** — `scanner/discover.py` walks the workspace, classifying files by extension and structure (MCP config, SKILL.md, agent identity, sandbox manifest).
2. **Static analysis** — `scanner/engine.py` iterates `ALL_RULES` (regex + AST patterns), producing findings with `(rule_id, severity, category, snippet, line)`.
3. **Neuro-symbolic bridge** — `scanner/neuro_symbolic_probe.py` runs a deterministic heuristic backend over the same input. Neural findings are **candidates only**; they never self-escalate to `finding` status without a symbolic rule match. This is the zero-FP guarantee: the symbolic layer is the constitution, the neural layer is a recall enhancer.
4. **Policy overlay** — `scanner/policy_pack.py` applies 5 policy packs (default, strict, relaxed, compliance, audit) that re-score findings per organizational posture.
5. **Report** — scored findings are emitted as SARIF, JSON, or HTML depending on the entry point.

## Rule taxonomy

Rules live in `scanner/rules.py` as a single flat dict keyed by regex pattern. Each value is `(description, severity)`. The taxonomy is:

| Prefix | Meaning | Source |
|---|---|---|
| `MCP01`–`MCP10` | OWASP MCP Top 10 | Official 2025 |
| `ASI01`–`ASI10` | Agentic AI (AIShield internal) | Internal mapping to OWASP 2026 |
| `AST01`–`AST10` | Agentic Skills Top 10 | Official 2026-08 |
| `SANDBOX*` | Container/OS hardening | Heuristic |
| `ZH_PROMPT*` | Chinese-language injection | Market-specific |
| `SKILL_EXTRA*` | Skill-specific execution plane | Heuristic |

The three `01`–`10` families (MCP / ASI / AST) each have 10 categories covering the full standard. The AST rules (added 2026-10-22) are **metadata-plane** rules — they catch "what the skill claims about itself" — while `SKILL_EXTRA_RULES` catch "what the skill tries to do". No double-counting.

## Isolation invariant

The scanner never spawns commands from the configuration it scans. This is proven by `scripts/prove_isolation.py`:

1. Patch `subprocess.Popen`, `os.system`, `subprocess.run` to raise on any call
2. Load the scanner against a hostile-looking config
3. Assert zero spawn invocations

This is not a guideline — it is a runtime assertion that fails the test suite if broken.

## Zero-dependency discipline

- Core scan path: Python stdlib only
- `cryptography` and `PyYAML` are **required** (not optional) for Ed25519 signing and YAML config parsing
- No network calls on the scan path
- No file writes to paths derived from scanned content

## Entry points

| Entry | What it does | Shared core |
|---|---|---|
| `python -m scanner` | CLI scan of a single file or workspace | `engine.py` |
| `npx aishield-mcp-server` | MCP server over stdio | `engine.py` (via HTTP) |
| `api/server.py` | HTTP REST API | `engine.py` |
| `scripts/scan_workspace.py` | Batch workspace scan | `engine.py` |
| `scripts/run_fvi_gate.py` | Formal verification gate | BMC 64-state model |

All five entry points call the same `scanner/engine.py`. There is no duplicate scan logic.

## Formal verification

`formal/isolation_invariants.qnt` defines a 64-state mechanism model (6 artifact booleans → 2⁶ states). `scripts/run_fvi_gate.py` performs BMC exploration of all 64 reachable states, asserting:

- `complete=true` (all states explored)
- INV-1 (no_execute): no state transitions to a spawn action
- INV-2 (no_network): no state transitions to a network call
- INV-3 (single_writer): findings are append-only
- INV-4 (read_only_input): scanned files are never mutated
- INV-5 (completeness): every rule is reachable
- INV-6 (grounded_promotion): neural findings never self-upgrade

Four mutation operators (M1–M4) are applied to the model to prove discriminative power — the model must catch each mutation as a violation.

## Directory layout

```
aishield/
├── scanner/          # Core scan engine + rules + detectors
│   ├── rules.py      # 313 rule registry (flat dict)
│   ├── engine.py     # Scan pipeline orchestrator
│   ├── neuro_symbolic_probe.py  # Zero-FP bridge
│   ├── policy_pack.py           # 5 policy packs
│   ├── red_team_probe.py        # 17 probes
│   └── ...           # 11 detector modules
├── eco/              # Trust layer
│   ├── attestation.py       # Hash-chained attestation
│   ├── evolution_ledger.py  # RSES accountability ledger
│   ├── meta_agent.py        # Bounded meta-agent
│   ├── crypto_sign.py       # Ed25519 signing
│   └── guardrail_harness.py # Tool-call interception
├── api/              # REST endpoints
│   ├── server.py             # FastAPI entry
│   ├── governance_api.py     # /api/v1/guard/*
│   └── ecosystem_support_api.py
├── mcp-server/       # TypeScript MCP server
├── formal/           # TLA+/BMC formal model
├── benchmarks/       # External corpus (593 pos / 517 neg / 18 families)
├── reports/          # Paper drafts, validation reports
├── scripts/          # Gates, benchmarks, utilities
├── tests/            # 2140 test cases (26 skipped)
└── docs/             # Documentation (EN + ZH)
```

## Related documents

- [Overview](./overview.md)
- [Quick Start](./quickstart.md)
- [Deployment](./deployment.md)
- [Benchmark results](./benchmark.md)
- [API reference](./api-reference.md)
- [FAQ](./faq.md)
- [Formal verification](../../formal/README.md)
