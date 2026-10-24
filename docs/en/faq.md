# AIShield — FAQ

## General

### What is AIShield?

AIShield is a local-first, zero-dependency security scanner and trust authority for the MCP / Agentic AI economy. It scans MCP servers, AI skills, and AI agent configurations for tool poisoning, prompt injection, secret leakage, sandbox misconfiguration, and supply-chain risk.

### Is it free?

Yes. The core scanner is open-source (MIT) and free. The local CLI and MCP server have no usage limits. The hosted API at aishield.tools offers a free tier (1,000 scans/hour) and a Pro tier for higher limits.

### Is it open source?

Yes, MIT license. See <https://github.com/lm203688/aishield>.

## Security

### Does the scanner execute the configuration it scans?

**No.** This is the core invariant. AIShield is purely static — it reads files and analyzes patterns without spawning any processes. This is proven by `scripts/prove_isolation.py`, which patches all spawn functions and asserts zero invocations.

### Does it send my code to the cloud?

**No.** The local scanner runs entirely on your machine. No code, configuration, or scan results leave your environment unless you explicitly use the hosted API.

### What about supply-chain risk from AIShield itself?

AIShield ships via npm with sigstore provenance. The npm package is a thin TypeScript wrapper around the Python scanner. You can also run the Python scanner directly without npm. The published channels are listed in `distribution/published.json` with source-of-truth links.

## Standards

### What standards does AIShield align with?

Three standards in parallel:

1. **OWASP MCP Top 10 (2025 v0.1)** — MCP01–MCP10
2. **OWASP Agentic AI Top 10 (2026)** — ASI01–ASI10 (AIShield internal mapping)
3. **OWASP Agentic Skills Top 10 (2026-08)** — AST01–AST10

Plus sandbox hardening heuristics and Chinese-language prompt injection rules.

### What does the `owasp_category` field mean?

The `owasp_category` field carries **two namespaces**:
- `MCP01`–`MCP10` are official OWASP MCP Top 10 codes
- `ASI01`–`ASI10` are AIShield's **internal** IDs (not official OWASP)
- `AST01`–`AST10` are official OWASP Agentic Skills Top 10 codes

Only `ASI01`/`ASI02`/`ASI03` coincide with the official OWASP Agentic AI Top 10 (2026). The machine-readable crosswalk is the `internal_to_owasp_agentic` field returned by `compliance_summary()`.

## Scanning

### What file types does AIShield scan?

- MCP configuration files (JSON, YAML)
- SKILL.md / AGENTS.md / CLAUDE.md (treated as executable content, not documentation)
- Agent identity files (AgentCard, DID documents)
- Sandbox/container manifests (Dockerfile, docker-compose, k8s)
- Python, JavaScript, TypeScript source code
- Shell scripts
- Markdown with frontmatter

### How does AIShield handle Markdown files?

AIShield treats **Markdown as executable content**. `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, and any Markdown with `name` + `description` frontmatter is the program an LLM will follow. Scanners that downgrade `.md` findings to "documentation example" structurally miss the entire skill supply chain.

### What are the 313 rules?

| Category | Count |
|---|---|
| MCP Top 10 (MCP01–MCP10) | 128 |
| Agentic AI Top 10 (ASI01–ASI10) | 75 |
| Agentic Skills Top 10 (AST01–AST10) | 23 |
| Sandbox hardening | 12 |
| Chinese prompt injection | 22 |
| **Static total** | **286** |
| Threat-intel generated | 8 |
| Radar-promoted | 19 |
| **Total** | **313** |

The authoritative number is always what `GET /api/v1/health` reports.

### What is the difference between AST and SKILL_EXTRA rules?

AST rules (AST01–AST10) are **metadata-plane** rules — they catch "what the skill claims about itself" (e.g. "this skill has no isolation", "this skill targets all platforms"). SKILL_EXTRA rules are **execution-plane** rules — they catch "what the skill tries to do" (e.g. "this skill runs `curl | sh`"). The two are complementary and do not double-count.

## Performance

### How fast is it?

The scanner processes a single file in milliseconds. A full workspace scan of a typical project takes under 5 seconds. The bottleneck is I/O, not computation.

### What is the maximum file size?

There is no hard limit. The scanner streams files line-by-line and does not load entire files into memory. For very large files, consider using `--max-size` to cap per-file processing.

## Trust and Attestation

### What is an attestation?

An attestation is a cryptographically signed statement that an agent or MCP server has passed AIShield's security scan. It includes a trust score (0–100), a certification level (uncertified / verified / certified / trusted), and a validity period.

### How do I verify an attestation?

Every attestation is Ed25519-signed. The public key is published at `https://aishield.tools/.well-known/jwks.json`. You can verify any attestation offline with just the public key — no network call required.

### What is a DID?

AIShield uses `did:key` for agent identity. A `did:key` is a self-contained, portable identifier derived from a public key. It does not require a registry — anyone can verify the identity offline.

## Deployment

### How do I deploy AIShield in CI/CD?

```yaml
# GitHub Actions example
- name: Security scan
  run: |
    npx -y aishield-mcp-server --scan . --format sarif --output results.sarif
    npx @sarif/sarif-tools check results.sarif --fail-on-critical
```

The scanner exits with code 1 if any critical or high findings are found, making it suitable as a CI gate.

### Can I run AIShield in a container?

Yes:
```bash
docker run --rm -v $(pwd):/workspace -w /workspace \
  aishield/scanner scan --file .
```

The scanner never writes to paths derived from scanned content, so it is safe to run in a container with read-only filesystem mounts.

### How do I keep AIShield updated?

For npm: `npm update aishield-mcp-server`
For Python: `pip install -e . && pip install --upgrade .`
The live API at aishield.tools is always on the latest version.

## Related documents

- [Overview](./overview.md)
- [Quick Start](./quickstart.md)
- [Architecture](./architecture.md)
- [Benchmark](./benchmark.md)
- [API reference](./api-reference.md)
- [Trust attestation quickstart](../trust-attestation-quickstart.md)
