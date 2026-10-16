# CocoLoop 上架草稿 + 注册交接（hub.cocoloop.cn）

> **平台事实（2026-09-15 实地核实）**
> - CocoLoop 是 **当贝**推出的 OpenClaw 类 AI Agent **技能商店**，上线于 **2026-03-19**，收录 5000+ Skills，配套「龙虾」社区。
> - 上架强制走 **CLS（平台专属）+ BSS（行业通用）** 安全审核，出具报告并给 **S+/S/A/B/C/D** 评级；另提供 VM 级（Docker）隔离执行环境。
> - **同赛道竞品已在架**：`SkillScan`（`/skills/7590`，评级 A，"Skill 安全准入网关 · 风险智能分级拦截"）。本清单要打的差异化就是下面第 3 条。

---

## 一、注册状态（AI 无法代做，原因明确）

- 平台的登录/投稿入口是**客户端渲染**（`/login`、`/submit`、`/upload` 等直连均 404，页面由 Next.js 在浏览器内构建），**且账号大概率需手机号/微信 OTP**——**AI 无法创建**，必须由你本人在浏览器完成。
- 因此本文件交付的是「**可直接粘贴的上架文案**」+「点击路径」，而不是一个已建好的账号。

**你的操作路径（约 3 分钟）**
1. 打开 <https://hub.cocoloop.cn/> → 右上角登录/注册（手机号或微信扫码，以实际页面为准）。
2. 进入「**社区投稿 / 分享自制 Skill**」入口（平台采用社区投稿 + 人工审核机制；部分新上架技能审核较慢，属已知现象）。
3. 提交公开仓库 **<https://github.com/lm203688/aishield>**，把下面第二节文案粘进对应字段。
4. 等待 CLS/BSS 认证评级——注意：认证流程本身会**扫描并（在其沙箱内）运行**提交的 skill，这与 AIShield「本地不出机」的卖点并不冲突（我们扫别人，不要求别人扫我们）。

## 二、可直接粘贴的文案

**Skill name**: AIShield
**Category**: Security / Supply-chain
**Repository**: https://github.com/lm203688/aishield
**Install**: `npm i -g aishield-mcp-server`（或经 MCP 桥接：在 agent 配置里把 `aishield-mcp-server` 加为 MCP tool provider —— 零安装、零适配）

**Short description**（卡片）:
> 本地、离线、零依赖的 AI 工具安全扫描器，专扫 MCP server / agent skills / GPTs / prompts。在 agent 安装或运行不可信工具前，静态检测供应链投毒、prompt 注入、隐藏命令、越权与数据外传 —— 你的代码永不出本机。双维覆盖 OWASP MCP Top 10 与 Agentic AI Top 10（ASI01–10）。

**Why install it**（详情页）:
- **定位互补**：CocoLoop 的 CLS 认证是「上架门槛」，AIShield 是开发者**自己**给技能/插件做「**安装前**安全门禁」的工具 —— 一个在云端审、一个在本机审。
- **纯静态推断**：绝不执行被扫配置里的任何命令（read-only），避免「为看工具列表先把恶意配置跑一遍」的陷阱；可用 `scripts/prove_isolation.py` 自证 spawn 0 子进程。
- **5 维评分**（安全 / 权限 / 数据处理 / 供应链 / 可靠性）+ 0–100 总分与 `safe/medium/high/critical` 风险级；输出 **SARIF**（进 GitHub Security tab）与 CycloneDX SBOM，可直接当 CI 门禁。
- **235 条规则**，对齐 OWASP MCP Top 10 与 OWASP Agentic AI Top 10（ASI01–ASI10）；含 19 条 Tech-Radar 自动晋升的雷达规则。
- **与 CLS 互补而非替代**：CLS 偏大模型深度检测（依赖外部 API、较慢），AIShield 本地零依赖、可离线、秒级 —— 两者叠加使用。

**Risk-review note**（坦诚声明保证边界）:
> AIShield 本身 MIT、完全本地，扫描目标路径但不运行目标代码。和任何安全工具一样，最终权威仍是源码 —— 请锁定版本、亲自阅读。规则命中是线索，不是判决。

**Tags**: `security`, `supply-chain`, `mcp`, `scanner`, `local`, `offline`

## 三、差异化话术（针对已在架的 SkillScan）
- **在哪跑**：SkillScan 以平台网关形态拦截（安装前/后检测）；AIShield 是**装在开发者本机**、**离线**、**代码不出机**。
- **依赖**：SkillScan/CLS 类需外部服务与大模型；AIShield **零第三方依赖**（纯标准库 urllib）。
- **可验证**：AIShield 把「绝不 spawn 被扫命令」写成一等不变量并**提供自证脚本**；这是最容易打动安全评审的一条。
