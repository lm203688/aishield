# AIShield Security Scan - Claude Code Plugin

> Agent-native security guardrail. Auto-scans AI tools before installation.

## Install

```bash
claude plugin install aishield-security-scan
```

Or add manually to your Claude Code config:

```json
{
  "plugins": ["aishield-security-scan"]
}
```

## What It Does

When Claude Code is about to install an MCP server, import a skill, or use a new AI tool, AIShield automatically:

1. Scans the tool for security risks
2. Checks for: prompt injection, tool poisoning, dangerous APIs, credential leaks, data exfiltration
3. Returns a 4-dimensional score (security/privacy/quality/performance)
4. Blocks or warns based on risk level

## Example

```
You: "Install the filesystem MCP server"

Claude: 🛡️ AIShield Security Check

📦 Tool: @modelcontextprotocol/server-filesystem
📊 Score: 82/100 | Risk: medium
🛡️ Badge: SILVER

⚠️ 2 medium issues found:
  • File system operations (write, delete)
  • No path restrictions

Recommendation: Configure with restricted paths. Safe to install with sandbox.

Proceeding with installation...
```

## Pricing

- Free: 5 scans/day
- Pro: ¥29/month, 200 scans/day
- Enterprise: ¥199/month, unlimited

https://aishield.ai/pricing

## License

MIT
