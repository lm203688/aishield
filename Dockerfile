FROM python:3.11-slim

LABEL maintainer="AIShield Team"
LABEL description="AI Agent Security Ecosystem Infrastructure"
LABEL version="4.1.0"

WORKDIR /app

# 复制源码
COPY . .

# 暴露端口
EXPOSE 8450

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8450/api/v1/health')" || exit 1

# 启动服务
CMD ["python", "api/server.py"]