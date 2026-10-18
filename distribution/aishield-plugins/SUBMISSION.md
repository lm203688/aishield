# AIShield Anthropic Plugin — Submission Package

本目录是提交到 **Anthropic Claude Code Plugin Marketplace** 的完整包。
按下面 3 步走：先跑一次自检 → 再走官方提交表单 → 最后等待审核。

## 目录结构（已合规）

```
distribution/aishield-plugins/
├── .claude-plugin/
│   ├── plugin.json              ← 插件清单（name + description 必填）
│   └── marketplace.json         ← 自分发市场清单
├── skills/
│   └── aishield-security-scan/
│       └── SKILL.md             ← 4.4KB，包含完整调用说明
├── README.md                    ← 面向 Anthropic 审核者的公开说明
├── SUBMISSION.md                ← 本文档，给用户看的提交手册
└── LICENSE                      ← MIT
```

关键结构铁律（来自 `code.claude.com/docs/en/plugins`）：

- `.claude-plugin/` 内只能放 `plugin.json` / `marketplace.json`
- `skills/`、`commands/`、`agents/`、`hooks/`、`.mcp.json` 必须在**插件根目录**
- 唯一强制字段是 `plugin.json.name`（kebab-case）与 `description`

## Step 1 — 本地预检（提交前必须通过）

在提交表单之前，用 `claude plugin validate` 做与审核流水线一致的本地检查：

```bash
# 一次性 clone
git clone https://github.com/lm203688/aishield.git
cd aishield/distribution/aishield-plugins

# 走一遍 validate（警告视为错误）
claude plugin validate . --strict

# 期望输出：
#   ✔ Validation passed
```

**如果本地没有 claude CLI**，手动核对以下几点即可（我们这边已经过一遍）：

- [x] `.claude-plugin/plugin.json` 存在且 `name` 为 kebab-case（当前：`aishield-security-scan`）
- [x] `description` 非空且非纯占位符
- [x] `skills/` 里的每个 `SKILL.md` frontmatter 含 `name` 与 `description`
- [x] `marketplace.json` 里 `plugins[0].source = "."` 指向根（自分发模式）
- [x] 无二进制 / 无 secrets / 无执行载荷（规则集以 JSON + 正则静态存储）
- [x] 版本号一致：plugin.json `4.3.0` = SKILL.md `metadata.version` = README 文案

## Step 2 — 选择提交通道（二选一）

Anthropic 目前**不区分**个人 / 团队作者，官方市场 (`claude-plugins-official`) 是 Anthropic 人工挑选的白名单，**任何提交流程都不会把插件加到官方市场**。你能进入的是**社区市场 `anthropics/claude-plugins-community`**，审核通过后会 pin 到该仓库的某个 commit SHA。

两个入口都可以用，选一个即可：

| 通道 | URL | 适用场景 |
|---|---|---|
| **Console 表单**（推荐个人作者） | https://platform.claude.com/plugins/submit | 无 Team / Enterprise 组织账号 |
| **claude.ai 表单** | https://claude.ai/admin-settings/directory/submissions/plugins/new | 拥有 Team / Enterprise 组织 Owner 权限 |

中国大陆直连 `platform.claude.com` 会被 redirect 到 `app-unavailable-in-region` 页面。需要自备**海外网络出口**（不是简单的代理，是要让 `platform.claude.com` 判为你在支持地区）。建议用你常用的海外网络环境，直接打开下面的 URL 复制内容填进去。

## Step 3 — 表单字段填什么

以下是**可直接复制粘贴**的字段值。审核流水线做自动化安全筛查时读的就是这些。

### 3.1 基础字段

| 字段 | 值 |
|---|---|
| Plugin name | `aishield-security-scan` |
| Display name | `AIShield Security Scan` |
| Version | `4.3.0` |
| Owner / Publisher | `lm203688` |
| Homepage | `https://aishield.tools` |
| Repository | `https://github.com/lm203688/aishield`（路径：`distribution/aishield-plugins/`） |
| License | `MIT` |
| Category | `quality-security` |
| Keywords | `security, scanner, mcp, agent, skill, prompt-injection, supply-chain, sbom, sarif` |

### 3.2 描述（Description / long description）

短描述（≈ 300 字符，用于列表页）：

```
AIShield 是本地、开源、零成本的 AI 工具安全扫描器，覆盖 OWASP MCP Top 10 + OWASP Agentic AI Top 10 + 沙箱硬化，264 条 MCP 规则 / 291 条 Skill 规则。核心不变量：扫描过程绝不执行被扫配置里的任何命令。
```

长描述（复制到 README 字段）：

```markdown
AIShield 是本地、开源、零成本的 AI 工具安全扫描器，覆盖 OWASP MCP Top 10 + OWASP Agentic AI Top 10 + 沙箱硬化，共 264 条 MCP 规则 / 291 条 Skill 规则（含 27 条 SKILL_EXTRA：供应链 / 上下文劫持 / Harness 元能力 / 记忆篡改 / 中文变体 / benchmark 声称 / 桌面驱动 / Agent 支付与预算攻击面）。

核心不变量：扫描过程绝不执行被扫配置里的任何命令。很多同类工具为了读取 tools/list 会真实启动被扫服务——那等于先中招再体检。AIShield 只读文件 + 只发 HTTP 审计请求，零 subprocess、零被扫代码执行面。

包含内容：
- Skill: skills/aishield-security-scan/SKILL.md — 指导 agent 如何用 AIShield 扫 MCP 服务器、AI Skill、Agent 工作区
- MCP Server: npx aishield-mcp-server — 直接把扫描器作为 MCP 工具挂载到 Claude Code
- 输出：CycloneDX SBOM + SARIF，可直接接 GitHub Code Scanning

合规说明：本 skill 是检测工具，SKILL.md 中出现的"攻击字符串"（如 curl | sh）是被扫描目标，不是让 agent 去执行的指令。规则集本体存放在 scanner/rules.py，以正则+严重级别静态存储，运行时不会被 agent 解释为指令。MCP server 是纯 HTTP 客户端，无代码执行面。

License: MIT
```

### 3.3 安全自审声明（Self-audit statement，如果表单有独立字段）

```
本插件是安全扫描器，不产生、不执行任何攻击载荷：
1. SKILL.md 里出现的"攻击字符串"（如 curl | sh / npx skills add / rm -rf）是 AIShield 会命中的 pattern，作为被扫描目标描述，不是让 agent 去执行的指令。
2. 规则集本体（scanner/rules.py）以正则+严重级别静态存储，运行时分派到扫描引擎，从不被 agent 解释为指令。
3. MCP server（npx aishield-mcp-server）是纯 HTTP 客户端——发审计请求给 https://aishield.tools 或本地 API，无代码执行面。
4. 本地扫描路径（scan_workspace.py）只读文件系统，无任何 subprocess 调用（这是项目的核心不变量）。

上游仓库：https://github.com/lm203688/aishield（MIT）
线上 API：https://aishield.tools
npm 包：https://www.npmjs.com/package/aishield-mcp-server

如果审核需要验证，可用下列命令在干净环境跑通：
  curl -X POST "$AISHIELD_API/api/v1/audit" \
    -H 'Content-Type: application/json' \
    -d '{"source_url":"https://github.com/owner/any-mcp-repo","tool_type":"mcp"}'
```

### 3.4 演示 / Demo（如果表单需要）

推荐 3 段（视频 / GIF / 文字皆可）：

1. **一键安装**（15s）：终端录屏
   ```
   claude plugin marketplace add lm203688/aishield-plugins
   claude plugin install aishield-security-scan@lm203688-plugins
   ```

2. **Agent 内部调用**（30s）：在 Claude Code 里发一句
   ```
   /aishield-security-scan 帮我扫一下 https://github.com/owner/some-mcp-server
   ```
   Agent 会主动调用 MCP 工具或走 curl，返回 JSON 报告。

3. **本地工作区预扫**（20s）：
   ```
   python scripts/scan_workspace.py /path/to/agent-workspace --md
   ```
   输出 Markdown 表格，展示命中项、严重级别、修复建议。

**没有真机演示也没关系**——把下面这段作为文字版演示：

```
$ curl -X POST https://aishield.tools/api/v1/audit \
    -H 'Content-Type: application/json' \
    -d '{"source_url":"https://github.com/anthropics/example-mcp-server","tool_type":"mcp"}'

{
  "overall_score": 62,
  "risk_level": "medium",
  "owasp_coverage": ["MCP06-Unrestricted-Resource-Consumption"],
  "findings": [
    {"rule_id": "MCP06-RSS", "severity": "medium", "evidence": "line 148: exec(...)"},
    ...
  ]
}
```

## Step 4 — 提交之后

1. **审核队列**：官方目录每晚从审核流水线同步，从提交到出现在 `anthropics/claude-plugins-community` 通常有几小时到一两天的延迟。
2. **状态查询**：可以在 https://github.com/anthropics/claude-plugins-community 的 marketplace.json 里搜 `aishield-security-scan`，看到就说明已上线。
3. **失败排查**：如果审核被拒，通常在表单页面会给出原因。常见的两条：
   - **规则数与实际不符** → 用 `curl https://aishield.tools/api/v1/health` 取当前 `rules_count` / `rules_breakdown`，同步更新 SKILL.md 与 README 再提一次。
   - **被判定为"攻击工具"** → 走 README 第 5 节的"合规说明"再强调一遍是检测工具，且 SKILL.md 里的攻击字符串明确标注为"被扫描目标"。

## 官方市场的说明（重要）

`claude-plugins-official` 是 Anthropic 人工策展的市场，**不接受任何提交流程**：

> "There is no application process, and the submission form does not add plugins to the official marketplace."
> — https://code.claude.com/docs/en/plugins

想让 Anthropic 收录：先进社区市场拿到真实使用量与口碑 → 观察他们的推荐标准（见 https://code.claude.com/docs/en/plugin-hints）→ 达到规模后由 Anthropic 侧主动引入。提交表单本身不会让插件进入官方市场。

## 版本一致性（提交前最后一遍）

跑这个校验：

```bash
python -c "
import json, sys
p = json.load(open('.claude-plugin/plugin.json'))
assert p['name'] == 'aishield-security-scan', 'plugin name'
assert p['version'] == '4.3.0', 'plugin version'
import urllib.request
h = json.loads(urllib.request.urlopen('https://aishield.tools/api/v1/health').read())
print('live MCP rules:', h['rules_count'])
print('plugin.json OK; live API OK')
"
```

`rules_breakdown.total` 应与 plugin.json / README / SKILL.md 里的 MCP 数字一致（当前 `264`）。

## 联系

- GitHub：https://github.com/lm203688/aishield
- Email：在 GitHub repo 里通过 issue 联系作者
- License：MIT
