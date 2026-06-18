<div align="center">

# 🛡️ AIShield

### Agent-Native AI Tool Security Scanner

Scan MCP servers, AI skills, GPTs, and prompts for security risks. 4-dimensional scoring. Certified badges. Guardrail MCP for auto-protection.

[![npm: aishield-mcp](https://img.shields.io/npm/v/aishield-mcp.svg)](https://www.npmjs.com/package/aishield-mcp)
[![npm: aishield-guardrail](https://img.shields.io/npm/v/aishield-guardrail.svg)](https://www.npmjs.com/package/aishield-guardrail)
[![pypi: aishield](https://img.shields.io/pypi/v/aishield.svg)](https://pypi.org/project/aishield/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🚀 Quick Start

### 1. MCP Server (Claude Desktop / Cursor)

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

### 2. Python SDK

```bash
pip install aishield
```

```python
from aishield import AIShield

shield = AIShield()
result = shield.scan("https://github.com/modelcontextprotocol/servers")
print(result.overall_score)  # 85
print(result.badge_level)    # "gold"
```

### 3. Guardrail MCP (Auto-protection)

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

**Put `aishield-guardrail` FIRST in your config.** It intercepts all tool installs and blocks unsafe ones.

### 4. GitHub Action

```yaml
- uses: aishield/audit@v1
  with:
    api_key: ${{ secrets.AISHIELD_KEY }}
    fail_on_risk: true
```

---

## 🛡️ What AIShield Scans

| Category | Detection |
|----------|-----------|
| **Tool Poisoning** | Hidden adversarial instructions in tool descriptions |
| **Prompt Injection** | Malicious prompts that hijack agent behavior |
| **Command Execution** | `child_process`, `subprocess`, `os.system` |
| **Data Exfiltration** | Unauthorized network calls, telemetry |
| **Credential Leaks** | Hardcoded API keys, tokens, passwords |
| **Dangerous APIs** | File system, network, shell, database access |
| **Supply Chain** | Malicious dependencies, typosquatting |
| **Code Quality** | Error handling, input validation, docs |

## 📊 Scoring

4-dimensional scoring (0-100):

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Security | 40% | Code vulnerabilities, dangerous APIs |
| Privacy | 25% | Data exfiltration, telemetry |
| Quality | 20% | Code quality, documentation |
| Performance | 15% | Resource usage, efficiency |

**Badges**: 🥇 Gold (≥85) | 🥈 Silver (≥70) | 🥉 Bronze (≥55)

---

## 📦 Packages

| Package | Install | Description |
|---------|---------|-------------|
| [`aishield-mcp`](packages/npm-mcp) | `npx aishield-mcp` | MCP Server for Claude/Cursor |
| [`aishield-guardrail`](packages/npm-guardrail) | `npx aishield-guardrail` | Guardrail MCP (auto-block unsafe tools) |
| [`aishield`](packages/pypi-sdk) | `pip install aishield` | Python SDK |
| [GitHub Action](packages/github-action) | `uses: aishield/audit@v1` | CI/CD integration |
| [Claude Skill](packages/claude-skill) | Plugin install | Claude Code skill |

---

## 🔌 API

### Submit Audit
```bash
curl -X POST https://aishield.ai/api/v1/audit \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "tool_type": "mcp",
    "source_url": "https://github.com/user/repo",
    "name": "my-mcp-server"
  }'
```

### Get Result
```bash
curl https://aishield.ai/api/v1/audit/{audit_id}
```

### Get Badge
```markdown
![AIShield](https://aishield.ai/api/v1/badge-name/your-tool-name)
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/audit` | Submit audit |
| GET | `/api/v1/audit/{id}` | Get audit result |
| GET | `/api/v1/tools` | List scanned tools |
| GET | `/api/v1/stats` | Global statistics |
| GET | `/api/v1/badge-name/{name}` | SVG badge |
| GET | `/api/v1/pricing` | Pricing info |
| POST | `/api/v1/keys` | Create API key |
| GET | `/api/v1/health` | Health check |

---

## 💰 Pricing

| Tier | Price | Scans/Day | Features |
|------|-------|-----------|----------|
| Free | ¥0 | 5 | Basic scanning, badge |
| Pro | ¥29/month | 200 | Priority queue, batch scan |
| Enterprise | ¥199/month | Unlimited | Custom rules, SSO, SLA |
| Pay-per-scan | ¥1/scan | - | One-time |

Get API key: https://aishield.ai/pricing

---

## 🏗️ Architecture

```
Agent (Claude/Cursor/Cline)
    ↓ installs MCP tool
Guardrail MCP intercepts
    ↓ calls AIShield API
AIShield Scanner
    ├── Static Analysis (30+ regex rules)
    ├── Dependency Analysis (npm/PyPI)
    ├── Secrets Detection
    └── Semantic Analysis (AI-powered)
    ↓ returns 4D score + badge
Agent shows result to user
    ✅ Approved → install
    🚫 Blocked → warn user
```

---

## 📈 Roadmap

- [x] MCP Server (stdio)
- [x] Python SDK
- [x] GitHub Action
- [x] Guardrail MCP
- [x] 4-dimensional scoring
- [x] Certified badges
- [ ] OWASP MCP Top 10 alignment
- [ ] Tool Poisoning deep detection
- [ ] Rug Pull detection (git diff monitoring)
- [ ] MCP Trust Framework (MTF) scoring
- [ ] Real-time handshake verification
- [ ] Batch scan 1000+ tools
- [ ] Industry security report

---

## 📄 License

MIT © AIShield
