# AIShield — AI Agent Security & Compliance Platform

> Security infrastructure for the Agent-native ecosystem. Scan MCP servers, detect banned words, assess compliance, and power AI capabilities.

[![Website](https://img.shields.io/badge/website-aishield.tools-blue)](https://aishield.tools)
[![API](https://img.shields.io/badge/API-MCP%20compatible-green)](https://aishield.tools/mcp)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## What is AIShield?

AIShield provides 4 compliance tools and 8+ AI capabilities for AI agents and developers:

### Compliance Tools
- **Chinese Banned Word Detection** — Detect banned/sensitive words in Chinese content. Supports 6 major platforms (Douyin, Xiaohongshu, WeChat, Weibo, Bilibili, Kuaishou). $0.1/check
- **AI Search Visibility Checker** — Check brand ranking in DeepSeek, Kimi, Doubao AI search engines. $2/check
- **Global Expansion Compliance Assessment** — 7-dimension compliance risk assessment for going global. $8/assessment
- **SEO Compliance Checker** — Detect SEO violations to avoid search engine penalties. $1/check

### AI Capabilities
- TTS, ASR, VLM (Image Understanding), Image Generation/Edit, Video Generation
- Web Search, Web Page Reader
- Book Distillation (RIA-TV++), Vector Search Optimizer, Token Slimmer
- Browser Automation (BrowserAct), Cybersecurity Skill Library

## Quick Start

```bash
# Register and get $5 free credit
curl -X POST https://aishield.tools/v1/register \
  -H "Content-Type: application/json" \
  -d '{"name":"my-agent","email":"optional"}'

# Call any service
curl -X POST https://aishield.tools/api/v1/execute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"service_id":"svc_046","query":"text to check"}'
```

## MCP Integration

AIShield is MCP (Model Context Protocol) compatible:

```json
{
  "mcpServers": {
    "aishield": {
      "url": "https://aishield.tools/mcp"
    }
  }
}
```

## GeneTech Ecosystem — 14 Knowledge Bases

AIShield is part of the GeneTech ecosystem, providing 14 frontier technology knowledge bases:

| # | Knowledge Base | Domain | Entities |
|---|---|---|---|
| 1 | GeneTech Tools | genetech-tools.pages.dev | 640+ |
| 2 | TCM Tools | tcm-tools.pages.dev | 324+ |
| 3 | Agent Ecosystem DB | agentecosystem.pages.dev | 594+ |
| 4 | RobotParts DB | robotparts.pages.dev | 412+ |
| 5 | QuantumDB | quantumcomputing.pages.dev | 450+ |
| 6 | BrainDB | brainscience.pages.dev | 525+ |
| 7 | NuclearDB | nuclearenergy.pages.dev | 423+ |
| 8 | ExoDB | exoscience.pages.dev | 435+ |
| 9 | MineralDB | alienminerals.pages.dev | 382+ |
| 10 | DeepSeaDB | deepseatech.pages.dev | 445+ |
| 11 | EnergyDB | newenergy-nya.pages.dev | 603+ |
| 12 | LifeDB | lifescience-epe.pages.dev | 622+ |
| 13 | BioComputeDB | biocomputedb.pages.dev | 174+ |
| 14 | BionicAI DB | bionicai.pages.dev | 115+ |

**Total: 6,000+ structured entities** across 14 frontier technology domains. All knowledge bases provide:
- Free web UI browsing
- API access ($29/month via AIShield)
- Full database export ($499 one-time)
- AI Plugin manifest for ChatGPT/Claude integration
- Scene-triggered llms.txt for AI agent discovery

## AI Agent Discovery

All sites are configured for AI agent discovery:
- `llms.txt` — Scene-triggered recommendations
- `/.well-known/ai-plugin.json` — ChatGPT/Claude plugin manifest
- `robots.txt` — Explicitly allows GPTBot, CCBot, PerplexityBot, YouBot
- `sitemap.xml` — All indexable URLs
- IndexNow submitted to Bing/Yandex

## Pricing

- **Free**: $5 welcome credit on registration
- **Pay-per-use**: $0.1 — $10 per API call
- **Monthly plans**: API Access $29/mo, Intelligence Pro $49/mo, Daily Brief $19/mo
- **One-time**: Full Database $499, Single Domain $49, Lifetime $99

Visit [creem.io/frontierkb](https://creem.io/frontierkb) to subscribe.

## Links

- **Website**: [aishield.tools](https://aishield.tools)
- **API Docs**: [aishield.tools/api/v1/openapi.json](https://aishield.tools/api/v1/openapi.json)
- **MCP Endpoint**: [aishield.tools/mcp](https://aishield.tools/mcp)
- **AI Plugin**: [aishield.tools/.well-known/ai-plugin.json](https://aishield.tools/.well-known/ai-plugin.json)
- **llms.txt**: [aishield.tools/llms.txt](https://aishield.tools/llms.txt)

## License

MIT
