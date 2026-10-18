# AIShield Security Scan — Anthropic Plugin

AIShield 是本地、开源、零成本的 AI 工具安全扫描器，覆盖 **OWASP MCP Top 10 + OWASP Agentic AI Top 10 + 沙箱硬化**，共 **264 条 MCP 规则 / 291 条 Skill 规则**（含 27 条 SKILL_EXTRA 覆盖供应链 / 上下文劫持 / Harness 元能力 / 记忆篡改 / 中文变体 / benchmark 声称 / 桌面驱动 / Agent 支付与预算攻击面）。

**核心不变量：扫描过程绝不执行被扫配置里的任何命令。**

## 安装

```bash
# 一次性添加 marketplace
claude plugin marketplace add lm203688/aishield-plugins

# 安装本插件
claude plugin install aishield-security-scan@lm203688-plugins
```

## 包含内容

- **Skill**：`skills/aishield-security-scan/SKILL.md` — 指导 agent 如何用 AIShield 扫 MCP 服务器、AI Skill、Agent 工作区
- **MCP Server**：`npx aishield-mcp-server` — 直接把扫描器作为 MCP 工具挂载到 Claude Code
- **分类**：`quality-security`

## 为什么用 Skill + MCP 双形态

Skill 教 agent「何时该扫、怎么解读结果」；MCP 提供可编程的调用面。用户想一键装完两个就一次装完，也可以只用 MCP。

## 合规说明（面向 Anthropic 审核）

这是一个**安全扫描器** skill，不是攻击工具：

1. **SKILL.md 里出现的"攻击字符串"是被扫描目标**，例如 `curl | sh` / `npx skills add` 是 AIShield 会命中的 pattern，不是让 agent 去执行的指令。
2. **规则集本体**（`scanner/rules.py`）以正则+严重级别的形式存，运行时作为检测规则使用，从不被 agent 解释为指令。
3. **MCP server** 是一个纯粹的 HTTP 客户端——发审计请求给 `https://aishield.tools` 或本地 API，没有代码执行面。
4. **本地扫描路径**（`scan_workspace.py`）只读文件系统，无任何 subprocess 调用（这是项目的核心不变量）。

如果审核需要验证，可用下列命令在干净环境跑通：

```bash
curl -X POST "$AISHIELD_API/api/v1/audit" \
  -H 'Content-Type: application/json' \
  -d '{"source_url":"https://github.com/owner/any-mcp-repo","tool_type":"mcp"}'
```

## 上游仓库

- 源码：https://github.com/lm203688/aishield
- 托管 API：https://aishield.tools
- npm 包：https://www.npmjs.com/package/aishield-mcp-server
- License：MIT

## License

MIT — see https://github.com/lm203688/aishield/blob/main/LICENSE
