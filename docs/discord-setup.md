# AIShield Discord 社区配置指南

## 创建 Discord 服务器

1. 访问 https://discord.com/developers/applications
2. 创建新 Application → Bot
3. 记录 Bot Token（存为 GitHub Secret: `DISCORD_BOT_TOKEN`）
4. 启用以下 Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent

## 邀请链接

创建后生成邀请链接，权限建议：
- 管理频道 (Manage Channels)
- 发送消息 (Send Messages)
- 管理消息 (Manage Messages)
- 嵌入链接 (Embed Links)
- 读取消息历史 (Read Message History)

## 频道结构

### 文字频道
```
# welcome — 新人引导（自动发送规则和快速开始链接）
# announcements — 官方公告（仅管理员可发）
# general — 通用讨论
# security-research — 安全研究讨论
# mcp-servers — MCP Server 安全话题
# agent-development — Agent 开发讨论
# show-and-tell — 展示你的 Agent / 集成
# help — 使用问题求助
# feedback — 功能建议和反馈
# rules — 社区规则（置顶）
```

### 机器人功能需求
- **欢迎消息**: 新成员加入时自动发送快速开始指引
- **Issue 同步**: GitHub Issue 自动推送到 #announcements
- **安全扫描命令**: `/scan <mcp-server-url>` 在 Discord 中直接扫描
- **信誉查询**: `/reputation <did>` 查询 Agent 信誉分

## Discord Bot 代码骨架（未来实现）

```python
# eco/discord_bot.py — 未来实现
# 使用 discord.py 或 webhooks 实现
# 功能：
#   1. /scan 命令 — 在 Discord 中直接调用安全扫描
#   2. /reputation — 查询 Agent 信誉
#   3. GitHub Issue 推送
#   4. 新人欢迎消息
```

## 社区增长策略

1. **GitHub README 添加 Discord 链接**
2. **Agent 注册成功后推荐加入 Discord**
3. **安全报告发布时在 Discord 同步讨论**
4. **每月 "This Month in AIShield" 社区更新**
5. **活跃成员获得 "Security Researcher" 角色**