# AIShield 多渠道分发包（一能力四上架）

把同一个「AIShield 安全扫描能力」以四种形态分发到不同生态，最大化触达：

| 渠道 | 形态 | 目录 | 状态 |
|------|------|------|------|
| **MCP Hub** | 官方 MCP registry server.json | [`../registry/server.json`](../registry/server.json) | 已就绪，待 `git tag v4.2.0` 触发上架 |
| **Claude Skills** | Claude 可直接调用的 Skill | [`claude-skill/SKILL.md`](claude-skill/SKILL.md) | 已就绪 |
| **GPT Store** | 自定义 GPT (Actions 接 AIShield API) | [`gpt-store/gpt-manifest.json`](gpt-store/gpt-manifest.json) | 已就绪 |
| **HuggingFace** | 安全基准 + 复现卡 | [`huggingface/README.md`](huggingface/README.md) | 已就绪 |

## 发布动作（一次性）

```bash
# 1) MCP Hub：打标签触发 npm 发布 → 自动接 MCP registry 上架
git tag v4.2.0 && git push origin v4.2.0

# 2) Claude Skills：将 claude-skill/ 目录作为 Skill 提交到 Claude 技能市场
# 3) GPT Store：用 gpt-manifest.json 创建自定义 GPT
# 4) HuggingFace：将 huggingface/README.md 作为 Dataset/Space 卡发布
```

> 四渠道共用同一套规则库 (scanner/rules.py) 与 Trust API，更新一处、全渠道同步。
