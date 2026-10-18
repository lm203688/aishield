# AIShield — Quick Start (English)

> English mirror of `README.md`. See also `README_EN.md` at repo root for the short version.

## What is AIShield

AIShield is a local-first, zero-dependency security scanner and trust authority for the MCP / Agentic AI economy. It scans MCP servers, AI skills, and AI agent configurations for tool poisoning, prompt injection, secret leakage, sandbox misconfiguration, and supply-chain risk — aligned with **OWASP MCP Top 10** and **all 10 risk categories of the OWASP Agentic AI Top 10 (2026)**.

- Repository: <https://github.com/lm203688/aishield>
- npm package: `aishield-mcp-server` (v4.11.0)
- Live service: <https://aishield.tools>

## Install

```bash
git clone https://github.com/lm203688/aishield.git && cd aishield
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

`cryptography` and `pyyaml` are **required**, not optional. `tests/run_all.py` pre-checks both and aborts cleanly (exit 2) rather than silently skipping tests that would otherwise look green.

## Run the test suite

```bash
python tests/run_all.py
```

## Verify the isolation invariant

The scanner never spawns commands from the configuration it inspects. Self-proof:

```bash
python scripts/prove_isolation.py
```

## Scan something

```bash
# Single file
python -m scanner --file path/to/config.json

# Whole workspace
python scripts/scan_workspace.py .
```

## Wire up the MCP server

### Claude Desktop / Cursor / Windsurf (stdio)

```json
{
  "mcpServers": {
    "aishield": {
      "command": "npx",
      "args": ["-y", "aishield-mcp-server"],
      "env": { "AISHIELD_API_KEY": "your-key" }
    }
  }
}
```

### Remote (StreamableHTTP)

```json
{
  "mcpServers": {
    "aishield": {
      "url": "https://aishield.tools/api/v1/mcp"
    }
  }
}
```

## Health check

```bash
curl https://aishield.tools/api/v1/health
```

Response includes `version`, `rules_count`, `rules_breakdown`, `commit`, `deployed_at`, `signing_backend`, `identity_ready`.

## Further reading

- [Overview](./overview.md)
- [Deployment](./deployment.md)
- [Trust attestation quickstart](../trust-attestation-quickstart.md)
