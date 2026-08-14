# AIShield × DeepSeek Harness（DSH）匹配策略

> 2026-08-15 用户问询："DeepSeek Harness 这个有插件市场吗？我们可以匹配吗？"
> 结论：**有分发面，且是我们目前找到的最契合的 agent-native 渠道**——DSH 原生支持 MCP，而 AIShield 本身就是 MCP server；且 DSH 生态的"插件供应链风险"是官方承认的头号隐患，正是 AIShield 的本职。

## 一、DSH 的插件分发面（三层）

| 层级 | 形态 | 我们的切入点 |
|---|---|---|
| 官方预留 Plugin Store | 内置 100+ 官方插件，第三方提交通道在建 | 未来官方上架 |
| **DSH Plugins 目录**（deepbolt.xyz/products/dsh-plugins） | 社区维护、人工审核的独立第三方目录；列安装命令 `dsh plugin --profile web add <npm/github/...>` | **立刻投稿占 security 类目（低代码）** |
| **GitHub `dsh-plugin` topic** | 非官方但事实注册表；打标签即被发现 | 发 `dsh-aishield` 包并打标签 |

## 二、两条匹配路径

### 路径 A（推荐，零适配、稳定）：MCP 桥接
- DSH **原生支持 MCP 协议**（官方文档确认）。
- AIShield 已是标准 MCP server（6 个 `aishield_*` 工具，npm `aishield-mcp-server` 4.2.2）。
- 用户在 DSH 配置里把 AIShield 加为 MCP tool provider 即可，**无需写一行 TypeScript**。
- 优势：绕开 DSH 的 Cordis 插件 API（dev preview，breaking changes 频繁），MCP 是稳定跨语言契约。

### 路径 B（先发窗口，需少量 TS）：原生 `dsh-aishield` 插件
- 写一个 npm 包 `dsh-aishield`，用 `package.json` 的 `dsh.bundle.patch` 指向 `cordis.patch.yml`，`index.js` 注册一个 "scan this plugin for supply-chain risk" 服务，调用我们自己的 `python -m scanner.cli scan` 扫描**待安装的其它 DSH 插件**。
- 价值：DSH 生态**目前没有安全类插件**（已列 12+ 插件全是 UI/视觉/工作流/多 Agent），先发者直接占 "security" 类目。
- 风险：DSH 是 developer preview，Cordis 服务/命令 API 仍在变 → `index.js` 的注册体需等 API 稳定再补全；声明部分（package.json + cordis.patch.yml）已稳定可先发。
- 注意：插件调用的是**我们自己的扫描器**扫**目标插件路径**，不执行目标插件的任何代码 —— 与"绝不 spawn 被扫配置"不变量一致。

## 三、优先级判断（客观）
- **机制真实**：DSH 支持 MCP、supply-chain 是其头号风险、security 类目真空 —— 三件事都成立，不是凑。
- **概率高低**：取决于 DSH  adoption 走势（首日 34k–65k★ 很高，但 dev preview 留失风险也在）。先占低成本入口（目录投稿 + MCP 桥接文档）是稳赚；原生插件等 API 稳再投入。
- **相对其它渠道**：匹配度高于 ClawHub / MCP.so / LobeHub（那些要么被 squat、要么被同名云 SaaS 占）。DSH 是全新生态、无 incumbent 安全插件，是我们"agent 生态位提前占领"的最佳落点之一。

## 四、待办（用户 vs AI）
- **用户**：① 在 deepbolt.xyz DSH Plugins 提交我们的 listing（草稿见 `DSH-PLUGINS-LISTING.md`）；② `npm publish dsh-aishield`（需登录 npm，且等 DSH API 稳定再补 `index.js` 注册体）。
- **AI 已准备**：本目录 `dsh-plugin/`（package.json + cordis.patch.yml + index.js 骨架）、`DSH-PLUGINS-LISTING.md` 投稿草稿；并已更新 `docs/agent-ecosystem-distribution.md` §1 + `competitive-landscape.md` §7.9。
