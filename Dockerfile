FROM python:3.10-slim

LABEL maintainer="AIShield Team"
LABEL description="AIShield - OWASP MCP Top 10 aligned AI Agent security scanner"

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl \
    && rm -rf /var/lib/apt/lists/*

# Python依赖（仅标准库，无外部依赖）
COPY scanner/ /app/scanner/
COPY api/ /app/api/
COPY eco/ /app/eco/
COPY sdk/python/aishield/ /app/sdk/aishield/
COPY data/ /app/data/
COPY sdk/python/ /app/sdk/python/

# 创建数据目录和 SDK init
RUN mkdir -p /app/api/data /app/data
RUN touch /app/sdk/__init__.py

# 可选安装（不阻塞构建）
RUN pip install -e . 2>/dev/null || true

# 环境变量
ENV AISHIELD_PORT=8450
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8450

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8450/api/v1/health')" || exit 1

CMD ["python", "-m", "api.server"]
