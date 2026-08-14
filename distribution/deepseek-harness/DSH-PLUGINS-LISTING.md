# DSH Plugins 目录投稿草稿（deepbolt.xyz/products/dsh-plugins）

> 提交方式：在 DSH Plugins 站点提交公开 GitHub 插件仓库，经管理员审核（确认仓库公开活跃、安装路径、README 摘要）后上架。本草稿直接复制填写即可。

---

**Plugin name**: AIShield
**Category**: Security / Supply-chain
**Repository**: https://github.com/lm203688/aishield
**Install command**:
```
dsh plugin --profile web add dsh-aishield
```
（或经 MCP 桥接，在 DSH 配置中将 `aishield-mcp-server` 加为 MCP tool provider —— 零安装、零适配）

**Short description** (for the listing card):
> Local, offline security scanner for DeepSeek Harness plugins. Scans any plugin you're about to install for supply-chain poisoning, prompt-injection, hidden commands, and over-privilege — before it touches your agent. Your code never leaves your machine; 227 MCP / 233 Skill rules run locally with zero third-party dependencies.

**Why install it** (for the detail page):
- DSH's own docs warn that third-party plugins are "another layer of trust." AIShield closes that gap.
- Scans static artifacts only — it never executes the plugin being scanned (read-only inference).
- Maps findings to OWASP Agentic AI Top 10 (ASI01–ASI10).
- Optional certified badge (gold/silver/bronze) for plugins that pass.

**Risk-review note** (DSH Plugins asks you to be honest about what review guarantees):
> AIShield itself is MIT-licensed and fully local. The DSH plugin wrapper calls our own scanner against a target plugin path; it does not run the target plugin's code. As with any security tool, the source remains the final authority — pin a version and read it.

**Tags**: `security`, `supply-chain`, `mcp`, `scanner`, `local`
