# AIShield MCP Server

> Agent-native AI tool security scanner. Scan MCP/Skill/GPT/Prompt for security risks via Model Context Protocol.

[![npm version](https://img.shields.io/npm/v/aishield-mcp.svg)](https://www.npmjs.com/package/aishield-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quick Start

### Install & Run (stdio mode)

Add to your MCP client config (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "aishield": {
      "command": "npx",
      "args": ["aishield-mcp"]
    }
  }
}
```

Or with API key for higher limits:

```json
{
  "mcpServers": {
    "aishield": {
      "command": "npx",
      "args": ["aishield-mcp"],
      "env": {
        "AISHIELD_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Remote Mode (no local install)

```json
{
  "mcpServers": {
    "aishield": {
      "command": "npx",
      "args": ["aishield-mcp"],
      "env": {
        "AISHIELD_REMOTE": "1"
      }
    }
  }
}
```

## Tools Provided

| Tool | Description |
|------|-------------|
| `scan_ai_tool` | Full security audit of any AI tool (MCP/GPT/Skill/Prompt) |
| `check_tool_safety` | Quick pass/fail check before installing an MCP tool |
| `get_security_badge` | Get badge info for display in README |
| `batch_scan` | Scan up to 10 tools at once |

## Use Cases

### Before installing a new MCP tool
```
Agent: "I want to install @modelcontextprotocol/server-filesystem"
→ AIShield: "⚠️ Score: 72/100 | 2 medium risks found. See report."
```

### In CI/CD pipeline
```yaml
- uses: aishield/scan@v1
  with:
    api_key: ${{ secrets.AISHIELD_KEY }}
```

### Batch audit your tool registry
```
Agent: "Scan these 5 MCP servers for security"
→ AIShield batch_scan: 5 results in one call
```

## Scoring

4-dimensional scoring (0-100):
- **Security** (40%): Code vulnerabilities, dangerous APIs
- **Privacy** (25%): Data exfiltration, telemetry
- **Quality** (20%): Code quality, documentation
- **Performance** (15%): Resource usage

Badges: 🥇 Gold (≥85) | 🥈 Silver (≥70) | 🥉 Bronze (≥55)

## Pricing

- Free: 5 scans/day
- Pro: ¥29/month, 200 scans/day
- Enterprise: ¥199/month, unlimited
- Pay-per-scan: ¥1/scan

Get API key: https://aishield.ai/pricing

## License

MIT
