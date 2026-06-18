# AIShield Python SDK

> Agent-native AI tool security scanner. Scan MCP/Skill/GPT/Prompt for security risks.

[![PyPI version](https://img.shields.io/pypi/v/aishield.svg)](https://pypi.org/project/aishield/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Install

```bash
pip install aishield
```

## Quick Start

```python
from aishield import AIShield

# Initialize (free: 5 scans/day, no API key needed)
shield = AIShield()

# Or with API key
shield = AIShield(api_key="your-key")

# Scan any AI tool
result = shield.scan(
    source_url="https://github.com/modelcontextprotocol/servers",
    tool_type="mcp",
    name="mcp-servers"
)

print(result.overall_score)    # 85
print(result.badge_level)      # "gold"
print(result.risk_level)       # "safe"
print(result.is_safe)          # True
print(result.summary())        # Formatted summary

# Quick safety check (pass/fail)
is_safe, score, risk = shield.check_safety("https://github.com/user/repo")

# Get badge info
badge = shield.get_badge(name="mcp-servers")

# Batch scan
results = shield.batch_scan([
    {"source_url": "https://github.com/repo1", "tool_type": "mcp"},
    {"source_url": "https://github.com/repo2", "tool_type": "skill"},
])
```

## Use as Guardrail in Agent Frameworks

### LangGraph
```python
from aishield import AIShield
shield = AIShield()

def install_tool(state):
    safety, score, risk = shield.check_safety(state["tool_url"])
    if not safety:
        return {"error": f"Blocked: score {score}, risk {risk}"}
    # ... proceed with install
```

### CrewAI
```python
from aishield import AIShield
shield = AIShield()

@tool
def safe_install_tool(url: str) -> str:
    """Install an MCP tool after security check."""
    is_safe, score, risk = shield.check_safety(url)
    if not is_safe:
        return f"❌ Blocked by AIShield: score {score}/100, risk {risk}"
    return install(url)
```

## ScanResult Fields

| Field | Type | Description |
|-------|------|-------------|
| `overall_score` | int | 0-100 composite score |
| `security_score` | int | 0-100 security score |
| `privacy_score` | int | 0-100 privacy score |
| `quality_score` | int | 0-100 quality score |
| `performance_score` | int | 0-100 performance score |
| `badge_level` | str | gold/silver/bronze/none |
| `risk_level` | str | safe/medium/high/critical |
| `is_safe` | bool | True if score≥60 and not high/critical |
| `findings` | list | Detailed security findings |
| `recommendations` | list | Actionable recommendations |

## License

MIT
