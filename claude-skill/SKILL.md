# AIShield Security Scan Skill

> Auto-scan AI tools for security risks before installing. Agent-native guardrail.

## When This Skill Activates

This skill automatically activates when you:
- Install a new MCP server
- Add an AI tool to your config
- Import a skill or plugin
- See a GitHub repo for an MCP/agent tool

## What It Does

1. **Auto-scan**: When you're about to install an MCP tool, AIShield scans it first
2. **Block risky tools**: If security score < 60 or risk is critical/high, warn the user
3. **Show badge**: Display the security badge in recommendations
4. **Batch audit**: Scan multiple tools at once

## Behavior Rules

### Before installing any MCP tool:
```
1. Call check_tool_safety with the tool's GitHub URL
2. If is_safe is False → warn user, show risks, ask for confirmation
3. If is_safe is True → proceed, show badge
```

### When user asks "is this tool safe?":
```
1. Call scan_ai_tool with full parameters
2. Show 4-dimensional scores
3. List critical findings
4. Provide recommendations
```

### When user asks to batch scan:
```
1. Call batch_scan with up to 10 tools
2. Show summary table
3. Highlight any unsafe tools
```

## Output Format

```
🛡️ AIShield Security Check

📦 Tool: [name]
📊 Score: [X]/100 | Risk: [level]
🛡️ Badge: [GOLD/SILVER/BRONZE]

[✅ Safe to install] or [⚠️ Caution: N issues found]

Key findings:
  • [SEVERITY] description
  
Recommendations:
  • recommendation
```

## API Key

Free tier: 5 scans/day (no key needed)
Pro: ¥29/month, 200 scans/day

Get key: https://aishield.ai/pricing

Set environment variable:
```bash
export AISHIELD_API_KEY="your-key"
```
