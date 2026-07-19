# AIShield Registry 发布指南

## 1. GitHub MCP Registry (官方)
npx @anthropic/mcp-registry publish --from ./mcp-server

## 2. Glama (56K+ Servers, SEO最高)
访问 https://glama.ai/mcp/servers/new 提交
或等自动索引（Glama会自动爬取GitHub仓库中的MCP Server）

## 3. Smithery
npx @smithery/cli publish ./mcp-server

## 4. mcp.so
访问 https://mcp.so/submit 提交

## 5. Docker MCP Registry
# Dockerfile已就绪，推送到Docker Hub:
docker build -t aishield/aishield-api:latest .
docker push aishield/aishield-api:latest

## 6. npm (MCP Server)
cd mcp-server && npm publish

## 7. PyPI (Python SDK)
pip install build && python -m build && twine upload dist/*