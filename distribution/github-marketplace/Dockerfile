FROM python:3.11-slim

LABEL maintainer="AIShield Team"
LABEL description="AIShield MCP/Agent Security Scan — local-first GitHub Action"
LABEL version="4.2.2"

WORKDIR /app

# Copy this action repo's sources (action_entrypoint.py lives at repo root).
COPY . .

# GitHub Action entrypoint: reads INPUT_* env, scans the target repo,
# emits score/report/sarif. Never spawns commands from the scanned config;
# never fetches scanned content over the network.
ENTRYPOINT ["python", "/app/action_entrypoint.py"]
