# Examples

## Claude Desktop Config

```json
{
  "mcpServers": {
    "aishield": {
      "command": "npx",
      "args": ["aishield-mcp"]
    },
    "aishield-guardrail": {
      "command": "npx",
      "args": ["aishield-guardrail"],
      "env": {
        "AISHIELD_API_KEY": "your-key"
      }
    }
  }
}
```

## Cursor Config

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

## Python SDK

```python
from aishield import AIShield

# Free tier (5 scans/day)
shield = AIShield()

# Scan MCP tool
result = shield.scan(
    "https://github.com/modelcontextprotocol/servers",
    tool_type="mcp"
)
print(f"Score: {result.overall_score}/100")
print(f"Badge: {result.badge_level}")

# Quick safety check
is_safe, score, risk = shield.check_safety("https://github.com/user/repo")
if not is_safe:
    print(f"⚠️ Blocked: {risk} (score {score})")
```

## GitHub Actions

```yaml
name: Security Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: AIShield Audit
        uses: aishield-ai/aishield@v2
        with:
          api_key: ${{ secrets.AISHIELD_API_KEY }}
          fail_on_risk: true
```

## Guardrail MCP (Auto-block unsafe tools)

```json
{
  "mcpServers": {
    "aishield-guardrail": {
      "command": "npx",
      "args": ["aishield-guardrail"],
      "env": {
        "AISHIELD_API_KEY": "your-key",
        "AISHIELD_MIN_SCORE": "60",
        "AISHIELD_BLOCK_RISK": "critical,high"
      }
    }
  }
}
```

Agent behavior:
```
User: "Install the filesystem MCP"
Agent: calls guard_install("https://github.com/.../filesystem")
AIShield: Score 82/100, medium risk
Agent: "✅ Safe to install (Silver badge). Configure with restricted paths."
```
