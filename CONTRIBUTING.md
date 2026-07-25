# 贡献指南

感谢你对 AIShield 的兴趣！AIShield 是 AI Agent 安全与信任基础设施，每一个贡献都让 Agent 生态更安全。

## 如何贡献

### 1. 报告问题

- **Bug 报告**：使用 [Bug 报告模板](https://github.com/lm203688/aishield/issues/new?template=01-bug-report.yml)
- **功能建议**：使用 [功能建议模板](https://github.com/lm203688/aishield/issues/new?template=02-feature-request.yml)
- **安全问题**：请通过 [安全页面](https://aishield.tools/security) 私下报告，不要在公开 Issue 中披露
- **使用问题**：前往 [Discussions](https://github.com/lm203688/aishield/discussions) 区交流

### 2. 提交代码

#### 环境准备

```bash
# 克隆仓库
git clone https://github.com/lm203688/aishield.git
cd aishield

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖（本项目零外部依赖，仅标准库）
# 但测试需要 pytest
pip install pytest
```

#### 开发流程

1. **Fork 仓库** 并创建分支：`git checkout -b feature/你的功能`
2. **编写代码**：遵循现有代码风格，保持零外部依赖（标准库 only）
3. **运行测试**：`python tests/run_all.py`
4. **提交 PR**：描述清楚改动内容和测试情况

#### 代码规范

- Python 3.10+ 兼容
- 零外部依赖（`requirements.txt` 为空是设计选择）
- 中文注释，英文变量名
- 每个模块顶部包含功能说明和 API 路由文档
- 线程安全：JSON 文件操作使用 `threading.Lock`

### 3. 贡献安全规则

AIShield 的核心是安全规则库。你可以：

- **新增规则**：在 `scanner/rules/` 下添加规则，遵循 `MCPxx-xxx` 编号格式
- **规则优化**：提升现有规则的检测准确率，减少误报
- **漏洞案例**：提交真实漏洞案例，帮助我们训练更精准的检测

### 4. 文档贡献

- 改进 README、API 文档
- 撰写安全研究博客（发布到 [aishield.tools/blog](https://aishield.tools/blog)）
- 翻译文档（我们计划支持多语言）

### 5. 社区参与

- 加入 [Discord](https://discord.gg/aishield)
- 在社交媒体分享 AIShield
- 在 Awesome MCP Servers 列表中推荐我们

## 贡献者权益

- 高质量贡献者将获得 GitHub 仓库的 Triage 权限
- 核心贡献者将列入 CONTRIBUTORS 文件和官网致谢页
- 安全规则贡献者将在规则库中署名

## 行为准则

请尊重每一位社区成员。我们遵循 [Contributor Covenant](https://www.contributor-covenant.org/) 行为准则。

## 需要帮助？

- 查看 [文档](https://aishield.tools/docs)
- 加入 [Discord](https://discord.gg/aishield)
- 发起 [Discussion](https://github.com/lm203688/aishield/discussions)