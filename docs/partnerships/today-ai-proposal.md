# Today AI × AIShield 预集成提案（邮件草稿）

> **状态**：草稿，待齐俊元团队联系渠道确认。齐俊元是前 Teambition CEO，Today AI 目前 waiting-list 阶段（尚未公开发布）。**waiting list 阶段是最佳预集成时机**——架构决定一旦定型很难改。
> **发送方式**：通过 today.ai 官网联系表单、齐俊元 X/Weibo/LinkedIn 私信、或共同熟人。本文件只放邮件正文，不包含渠道调研。
> **建议发送时机**：Today AI 公开发布前 2-4 周。

---

## 邮件正文（可直接复制发送）

**Subject**：为 Today AI 接入本地 agent 安全扫描层（1 页说明）

**收件人**：齐俊元 / Today AI 团队

俊元，

看过 Today AI 的定位（个人级 AI Agent 操作系统，接入电脑/本地文件/短信/日历/邮箱/Notion/GitHub），有个技术协同点想聊——**在等待列表阶段就能锁定的架构决定**。

## 场景（Today AI 明天会遇到）

Today AI 的核心动作是让个人 agent 自主接入各类云服务和 tool。这里有个**结构性安全 gap**：

1. **接入面越广，风险越大**。GitHub、Notion、邮箱是 agent 权限最高、数据最敏感的几个表面。Today AI 帮用户接入越多，被 prompt injection / tool poisoning 影响的爆炸半径越大。
2. **skill 供应链问题**。用户可能通过社区安装 skill（比如 ClawHub、CocoLoop），本地 agent 需要有能力验证"这个 skill 该不该被信任"——尤其是"Markdown as executable content"（`SKILL.md`、`AGENTS.md`、`CLAUDE.md` 里藏指令）的攻击面。
3. **信任层缺失**。个人 agent 没有企业 IT 部门把关，用户无法判断"我这个 agent 装的 skill 是不是有毒"。

## AIShield 的定位

不是 Today AI 的竞品，是**它的 agent 安全扫描层**。

- **本地零依赖**（urllib only，无 Docker、无 venv、无 API key），跑在用户机器上，不上传任何代码。这对"个人级 agent OS"的定位是硬匹配。
- **静态审计**：审计 MCP 配置时**不 spawn 任何被扫描的命令**——用户让 agent 装的恶意 MCP server 不会在扫描过程被执行。这条不变量 `scripts/prove_isolation.py` 有自证。
- **235 条 MCP 规则 + 241 条 skill 规则**，覆盖 OWASP MCP Top 10 与 OWASP Agentic AI Top 10（ASI01-10）。
- **`aishield-trust/v1` 中立信任凭证**：可嵌 MCP Server Card / Agent Card，作为 Today AI 展示给用户的信任标志。

## 3 个具体建议

1. **接入层 hook**：Today AI 在用户点"接入 GitHub / Notion / 邮箱"时，先让 AIShield 扫一遍 agent 会调到的 tool 描述（tool description poisoning 检测）+ 生成的 MCP 配置。零成本前置检查。
2. **Skill 安装门禁**：Today AI 接入 ClawHub / CocoLoop 类社区时，安装前跑 AIShield 的 skill 扫描（Markdown as executable content 语义解析）。
3. **Agent 简报里的信任信号**：Today AI 主打"主动简报"作为核心交互——把 AIShield 的日级 digest 嵌到简报里（"你今天有 3 个 skill 通过扫描 / 1 个被拦下"）。这个是把安全扫描包装成用户体验的方式，不添负担。

## 下一步

- 如果方向对，我可以发一份 `aishield-trust/v1` 的 spec（已经公开：https://aishield.tools/trust-attestation-spec），你们可以拿来决定要不要嵌。
- 也可以直接跑一次 `npx aishield-mcp-server`（10 秒起来），接一个 tool 边界做 PoC。
- Today AI 未公开发布是**最好的预集成窗口**——之后要接就得走完整 SDK / 后台 / 计费链路。

项目本身：https://github.com/lm203688/aishield （MIT，4.8.3，2026-09 已 235 规则稳定运行）。

—— 厉兴（AIShield maintainer）

---

## 备选简短版（如果 1 页太冗）

**Subject**：为个人 Agent OS 提供本地安全扫描层

俊元，

看到 Today AI 的定位是"个人级 AI Agent 操作系统"，我这边有个 open-source 的 agent 安全扫描器想聊接入。

核心：AIShield 是本地零依赖的 agent 安全扫描层，覆盖 OWASP MCP Top 10 + Agentic AI Top 10（235 条规则）。静态审计、不 spawn 被扫描命令、不上传代码。MIT 许可。

匹配点：Today AI 接入 GitHub/Notion/邮箱时的高风险 tool 边界、skill 供应链、用户信任信号展示——AIShield 都能在本地静态扫描层解决。

waiting list 阶段是最佳预集成窗口。想聊聊？

项目：https://github.com/lm203688/aishield

—— 厉兴

---

## 待用户拍板

1. **发送渠道**：邮件 / X 私信 / LinkedIn / 熟人介绍——需用户确认有哪一个可用渠道。
2. **发送时机**：现在发 vs 等 Today AI 公开发布前 2-4 周发。前者能占早鸟位置，后者更精准命中。
3. **署名**：`厉兴` vs `AIShield maintainer` vs 英文署名——用户拍板。

---

*本文件是沟通草稿，不代表 AIShield 团队已联系 Today AI。用户确认发送后请同步更新本文件的"发送状态"字段。*
