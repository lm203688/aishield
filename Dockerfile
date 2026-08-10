FROM python:3.11-slim

LABEL maintainer="AIShield Team"
LABEL description="AIShield MCP/Agent Security Scan — local-first GitHub Action"
LABEL version="4.2.2"

WORKDIR /app

# 复制源码
COPY . .

# GitHub Action 入口：读取 INPUT_* 环境变量，扫描目标仓库并产出 score/report/sarif
# 绝不 spawn 被扫配置里的命令、绝不联网抓取被扫内容
ENTRYPOINT ["python", "/app/action_entrypoint.py"]