# AIShield Guardrail MCP

> 🛡️ Security gate for AI agent tool installation. Blocks unsafe MCP/skill installs automatically.

**This is the killer product.** Agent puts this MCP first in its config. Every time the Agent wants to install a new tool, AIShield scans it first. Unsafe tools get blocked. Safe tools get a badge.

## Why This Matters

AI agents can install MCP servers that:
- Read your files (`filesystem`)
- Execute commands (`bash`)
- Make network requests (`fetch`)
- Access your databases (`postgres`)

**Without AIShield**: Agent installs anything → 💀
**With AIShield**: Agent installs → AIShield scans → blocks if unsafe → ✅

## Install

### Claude Desktop / Cursor config

```json
{
  "mcpServers": {
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

**⚠️ Put `aishield-guardrail` FIRST in your mcpServers list.**

### No API key (free tier)

```json
{
  "mcpServers": {
    "aishield-guardrail": {
      "command": "npx",
      "args": ["aishield-guardrail"]
    }
  }
}
```

## How It Works

```
Agent: "I want to install @some-org/some-mcp-server"

→ Agent calls guardrail.guard_install("https://github.com/some-org/some-mcp-server")

AIShield:
  🛡️ AIShield Guardrail — Install Gate

  📦 Tool: some-mcp-server
  📊 Score: 45/100 | Risk: 🔴 critical
  🚫 VERDICT: BLOCKED

  ⚠️ DO NOT INSTALL. Security issues:
    • [CRITICAL] Command execution via child_process
    • [HIGH] No input validation on SQL queries
    • [HIGH] Hardcoded API key detected

  📄 Full report: https://aishield.ai/report/abc123

Agent: "⚠️ AIShield blocked this tool (score 45/100, critical risks).
       Do you want me to find an alternative?"
```

## Tools

| Tool | When to Call |
|------|--------------|
| `guard_install` | BEFORE installing any MCP/skill/tool |
| `scan_before_use` | BEFORE using a tool you haven't used before |
| `audit_config` | Audit your entire mcpServers config at once |
| `get_policy` | Check current guardrail policy |

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `AISHIELD_API_KEY` | (none) | API key. Free: 5 scans/day, Pro: 200/day |
| `AISHIELD_API_URL` | https://aishield.ai | API endpoint |
| `AISHIELD_MIN_SCORE` | 60 | Minimum score to allow install |
| `AISHIELD_BLOCK_RISK` | critical,high | Risk levels to block |

### Strict mode (enterprise)

```json
{
  "env": {
    "AISHIELD_API_KEY": "your-key",
    "AISHIELD_MIN_SCORE": "75",
    "AISHIELD_BLOCK_RISK": "critical,high,medium"
  }
}
```

### Permissive mode (developer)

```json
{
  "env": {
    "AISHIELD_MIN_SCORE": "40",
    "AISHIELD_BLOCK_RISK": "critical"
  }
}
```

## Use Cases

### 1. Personal Agent Safety
Protect your Claude/Cursor from installing malicious MCP servers.

### 2. Team Policy Enforcement
Set `MIN_SCORE=75` to enforce a security baseline across your team.

### 3. CI/CD Integration
Add to your CI agent config to prevent deploying unsafe tools.

### 4. Audit Existing Tools
```json
Agent: "Audit my current MCP config"
→ calls audit_config with your mcpServers
→ Gets security report for all installed tools
```

## Pricing

- Free: 5 scans/day (no key needed)
- Pro: ¥29/month, 200 scans/day
- Enterprise: ¥199/month, unlimited + custom rules

https://aishield.ai/pricing

## License

MIT
