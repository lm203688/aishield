# AIShield 多渠道分发包（一能力多上架）

把同一个「AIShield 安全扫描能力」以多种形态分发到不同生态，最大化触达。
所有对外投放的产物**必须在 [`published.json`](published.json) 台账登记，且源留底在本目录下**。

| 渠道 | 形态 | 目录 | 状态 |
|------|------|------|------|
| **MCP Hub** | 官方 MCP registry server.json | [`../registry/server.json`](../registry/server.json) | 已上架（npm `aishield-mcp-server` 4.2.2） |
| **Agensi** | Agent Skill | [`agensi/chinese-seo-compliance/`](agensi/chinese-seo-compliance/) | **已发布 v1.0，有真实下载**；仓库内为规范重建的 v1.1 |
| **Claude Skills** | Claude 可直接调用的 Skill | [`claude-skill/SKILL.md`](claude-skill/SKILL.md) | 源已就绪，待提交 |
| **GPT Store** | 自定义 GPT（Actions 接 AIShield API） | [`gpt-store/gpt-manifest.json`](gpt-store/gpt-manifest.json) | 源已就绪，待提交 |
| **HuggingFace** | 安全基准 + 复现卡 | [`huggingface/README.md`](huggingface/README.md) | 源已就绪，待提交 |

## 发布留底铁律

2026-08-10，Agensi 上有人下载了 `chinese-seo-compliance v1.0`——这是分发渠道的第一个真实下载，
同时暴露一个硬伤：**东西发出去了，仓库里却没有源，无法复核也无法迭代**。
一家做信任的项目不能有这种缺口，所以定下规矩：

1. 任何对外投放，先把源放进 `distribution/<渠道>/<产物名>/`
2. 在 `published.json` 登记（渠道 / 名称 / 版本 / 发布日 / 源路径 / 源状态 / 采纳信号）
3. 发布前必须过自家扫描器：`python scripts/verify_distribution.py`
4. 门禁不过（阻断级发现 / 评分 < 80 / 源缺失）就不许发

## 自检门禁

```bash
python scripts/verify_distribution.py           # 人读报告
python scripts/verify_distribution.py --json    # 机器消费
```

门禁复用主扫描引擎（rules / dependency / secrets / poisoning / taint），
**只读文件，绝不执行发布物里的命令，也不联网**。
测试见 `tests/test_distribution_gate.py`（含"门禁必须能失败"的反例用例）。

## 一次发现的真实盲点

给发布物做自检时发现：引擎早期把所有 `.md` 命中一律降级成「文档示例」，
理由是 README 里的 `curl` 示例不该报 critical。但对 **agent skill** 来说，
`SKILL.md` 本身就是可执行载荷——LLM 读到什么就照做。
恶意 skill 只要把 payload 写进正文，就能拿到「low + 98 分」放行。

修复：`scanner/rules.py::is_agent_instruction_doc()` 区分「给人看的文档」与
「给 agent 执行的指令」（SKILL.md / AGENTS.md / CLAUDE.md、skills 与 prompts 目录、
带 `name` + `description` frontmatter 的 Markdown），后者不降级。
同一份恶意样本从 98 分 low 变成 61 分 critical。
副作用是我们自己的 `claude-skill/SKILL.md` 当场被自家门禁拦下（写死了内网地址），
已改为 `$AISHIELD_API` 参数化。

> 各渠道共用同一套规则库（`scanner/rules.py`）与 Trust API，更新一处、全渠道同步。
