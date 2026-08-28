## AIShield Security Scanner

- **Website**: https://aishield.tools
- **Repository**: https://github.com/lm203688/aishield
- **License**: MIT

AIShield is an AI Agent security and trust infrastructure platform. It provides OWASP MCP Top 10-aligned security scanning for MCP servers and AI Agent tools — detecting prompt injection, secret leakage, tool abuse, excessive permissions, and more across 227 security rules.

### Key Features
- **Agent-First**: One-click onboarding — register as an Agent, get DID + API Key + quick start guide in a single API call (`POST /api/v1/agent/setup`)
- **MCP Native**: StreamableHTTP endpoint, directly callable from Claude, Cursor, VS Code, and any MCP-compatible client
- **A2A Discovery**: Agent Card auto-discovery via `/.well-known/agent-card.json`, with inter-agent trust scoring
- **227 Security Rules**: Aligned with OWASP MCP Top 10 (2025 v0.1), covering all 10 risk categories
- **Zero Dependencies**: Pure Python stdlib, no external packages required
- **OpenAPI 3.0.3**: Machine-readable API spec at `/openapi.json` for automatic client generation
- **Trust Ecosystem**: Built-in DID identity, reputation system, skill marketplace, and payment gateway

### MCP Server Configuration

Add to your MCP client config (Claude Desktop, Cursor, VS Code, etc.):

```json
{
  "mcpServers": {
    "aishield": {
      "url": "https://aishield.tools/api/v1/mcp"
    }
  }
}
```

### Quick Start via API

```bash
# 1. Register as an Agent (one call, get everything)
curl -X POST https://aishield.tools/api/v1/agent/setup \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "MyAgent", "capabilities": ["scan", "monitor"]}'

# 2. Scan a tool
curl -X POST https://aishield.tools/api/v1/audit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_api_key>" \
  -d '{"tool_name": "my-mcp-server", "tool_description": "...", "tool_schema": {}}'
```

### MCP Tools Available

| Tool | Description |
|------|-------------|
| `aishield_scan` | Full security audit against OWASP MCP Top 10 |
| `aishield_prompt_check` | Prompt injection detection |
| `aishield_banned_words` | Chinese content compliance check |
| `aishield_rug_pull` | Rug pull / supply chain risk detection |
| `aishield_handshake` | MCP protocol handshake verification |
| `agent_register` | One-click Agent registration |
| `agent_quick_scan` | Quick scan by tool name + description |

### Categories
`security`, `developer-tools`