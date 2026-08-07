# AIShield MCP Server

Security scanner for AI Agent tools, aligned with **OWASP MCP Top 10** and
**OWASP Agentic AI Top 10 (ASI)**. 201 local rules, 5-dimension scoring.

Scans never execute the code under review — AIShield reads configuration and
source statically, and never spawns commands from the config it is inspecting.

## Install

```bash
npx aishield-mcp-server
```

## Claude Desktop / Cursor / Windsurf

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

## Remote Mode (StreamableHTTP)

```json
{
  "mcpServers": {
    "aishield": {
      "url": "https://api.aishield.tools/mcp"
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `aishield_scan` | Full security scan — OWASP MCP Top 10 + Agentic AI Top 10, 201 rules, 5-dimension scoring |
| `aishield_guardrail` | Pre-install safety check — pass/block verdict with score |
| `aishield_prompt_check` | Prompt injection detection — Chinese + English |
| `aishield_banned_words` | Chinese content compliance — 6 platform rules |
| `aishield_rug_pull` | Rug pull detection — security code removed or new exfil paths across commits |
| `aishield_handshake` | MCP config review — `npx -y` risk, sensitive env vars, over-long tool descriptions |

## Scoring Dimensions

1. **Security** (40%) — OWASP MCP Top 10 coverage
2. **Permissions** (20%) — Least privilege compliance
3. **Data Handling** (20%) — No secrets/exfiltration
4. **Supply Chain** (10%) — Dependency safety
5. **Reliability** (10%) — Auth/logging/observability

## OWASP MCP Top 10 Coverage

| Category | Rules | Description |
|----------|-------|-------------|
| MCP01 | 16 | Improper Token & Secret Management |
| MCP02 | 12 | Privilege Scope Creep |
| MCP03 | 8 | Tool Poisoning |
| MCP04 | 9 | Supply Chain Attack & Dependency Tampering |
| MCP05 | 24 | Command Injection & Execution |
| MCP06 | 14 | Intent Flow Subversion / Prompt Injection |
| MCP07 | 8 | Insufficient Authentication & Authorization |
| MCP08 | 6 | Lack of Audit & Observability |
| MCP09 | 6 | Shadow MCP Servers |
| MCP10 | 7 | Context Injection & Over-Sharing |

Subtotal: **110 rules**

## OWASP Agentic AI Top 10 (ASI) Coverage

| Category | Rules | Description |
|----------|-------|-------------|
| ASI01 | 6 | Goal and Instruction Manipulation |
| ASI02 | 6 | Tool Misuse |
| ASI03 | 6 | Excessive Agency |
| ASI04 | 6 | Memory Manipulation |
| ASI05 | 6 | Agent Identity and Trust |
| ASI06 | 6 | Agent Communication and Supply Chain |
| ASI07 | 6 | Unbounded Resource Consumption |
| ASI08 | 6 | Observability and Monitoring Gaps |
| ASI09 | 6 | Cascading Failures & Multi-Agent Risks |
| ASI10 | 6 | Rogue Agent & Human-Autonomy Boundary |

Subtotal: **60 rules**

Plus 23 Chinese-language prompt-injection rules and 8 generated rules.

**Total: 201 rules** (MCP type) / **207 rules** (Skill type)

## License

MIT