# AIShield

**Open-source, local-first AI Agent security scanner and trust authority for the MCP / Agentic AI economy.**

AIShield scans MCP servers, AI skills and AI agents for tool poisoning, prompt injection, secret leakage, sandbox misconfiguration and supply-chain risk. It detects **264 MCP rule categories / 291 skill rule categories** aligned with **OWASP MCP Top 10** and **all 10 risk categories of the OWASP Agentic AI Top 10 (2026)**, runs fully offline (zero cost, no code sent to the cloud), and acts as a CI security gate.

## Quick Start

```bash
git clone https://github.com/lm203688/aishield.git && cd aishield
python -m venv .venv && source .venv/bin/activate
pip install -e .
python tests/run_all.py
```

## Key Features

- **Zero dependencies** — Python standard library only
- **Fully offline** — no code or configuration leaves your machine
- **264 MCP / 291 Skill rules** — OWASP-aligned, continuously updated
- **CI gate** — GitHub Actions integration with atomic push
- **MCP server** — 76 tools for AI agent integration

## License

MIT
