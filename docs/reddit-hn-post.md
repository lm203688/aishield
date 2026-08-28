Title: AIShield — Open-source AI Agent security scanner (OWASP MCP Top 10, 227 rules, MCP native)

I built AIShield, an open-source AI Agent security & trust infrastructure platform. It scans MCP servers and AI Agent tools against 227 security rules aligned with OWASP MCP Top 10.

**The problem**: MCP ecosystem has 10,000+ servers and 97M monthly SDK downloads, but zero built-in security scanning. When an AI agent calls a MCP tool, it gets the same permissions as the user — no sandboxing, no trust verification, no prompt injection protection. One malicious prompt can leak secrets, abuse tools, or execute arbitrary operations.

**What AIShield does**:
- Scans MCP tool descriptions, schemas, and configurations for 227 security risks across all 10 OWASP MCP Top 10 categories
- Detects prompt injection, secret/credential leakage, excessive permissions, tool abuse, schema poisoning, and more
- Provides an MCP Server endpoint — so Claude, Cursor, VS Code, or any MCP-compatible client can call security scans directly in the AI workflow
- Agent-First design: `POST /api/v1/agent/setup` registers an Agent, gets DID + API Key + quick start guide in ONE call
- A2A Agent Card auto-discovery for inter-agent trust scoring
- Built-in trust ecosystem: DID identity, reputation system, skill marketplace, payment gateway

**MCP integration** (add to your MCP config):
```json
{
  "mcpServers": {
    "aishield": {
      "url": "https://aishield.tools/api/v1/mcp"
    }
  }
}
```

**Tech**: Pure Python stdlib (zero dependencies), ThreadingMixIn HTTP server, JSON file storage, 227 security rules.

**Try it**: https://aishield.tools  
**Code**: https://github.com/lm203688/aishield  
**License**: MIT

I'd love to hear feedback — especially from MCP server authors who want to verify their tools are safe before publishing.