# AIShield MCP Server

OWASP MCP Top 10 aligned security scanner for AI Agent tools.

## Install

```bash
npx @aishield/mcp-server
```

## Claude Desktop / Cursor / Windsurf

```json
{
  "mcpServers": {
    "aishield": {
      "command": "npx",
      "args": ["-y", "@aishield/mcp-server"],
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
| `aishield_scan` | Full security scan — OWASP MCP Top 10, 60+ rules, 5-dimension scoring |
| `aishield_guardrail` | Pre-install safety check — pass/block verdict with score |
| `aishield_prompt_check` | Prompt injection detection — Chinese + English |
| `aishield_banned_words` | Chinese content compliance — 6 platform rules |

## Scoring Dimensions

1. **Security** (40%) — OWASP MCP Top 10 coverage
2. **Permissions** (20%) — Least privilege compliance
3. **Data Handling** (20%) — No secrets/exfiltration
4. **Supply Chain** (10%) — Dependency safety
5. **Reliability** (10%) — Auth/logging/observability

## OWASP MCP Top 10 Coverage

| Category | Rules | Description |
|----------|-------|-------------|
| MCP01 | 14 | Token & Secret Management |
| MCP02 | 12 | Privilege Scope Creep |
| MCP03 | 8 | Tool Poisoning |
| MCP04 | 8 | Supply Chain Attack |
| MCP05 | 8 | Command Injection |
| MCP06 | 8 | Prompt Injection |
| MCP07 | 6 | Insufficient Authentication |
| MCP08 | 6 | Lack of Audit |
| MCP09 | 6 | Shadow MCP Servers |
| MCP10 | 6 | Context Over-Sharing |

**Total: 82 rules** (MCP type) / **88 rules** (Skill type)

## License

MIT