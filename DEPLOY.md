# AIShield 部署文档

## 本地启动

**Windows:**
```bat
start.bat
```

**跨平台:**
```bash
python -m api.server
```

## Docker 部署

```bash
docker-compose up -d
```

## Railway（推荐，免费）

1. Fork 本仓库
2. 登录 [Railway](https://railway.app) → New Project → Deploy from GitHub repo
3. 选择 fork 的仓库，Railway 会自动检测 `railway.json` 和 `Dockerfile`
4. 添加环境变量（见下方说明）
5. 推送到 `main` 分支自动触发部署（已配置 GitHub Actions）

## Render

1. Fork 本仓库
2. 登录 [Render](https://render.com) → New → Web Service
3. 连接 GitHub 仓库，Render 会自动检测 `render.yaml`
4. 添加环境变量 → Deploy

## 华为云 / 阿里云

使用 `Dockerfile` 部署到容器服务（CCE / SAE / ECS + Docker）：

```bash
docker build -t aishield-api:latest .
docker run -d -p 8000:8000 aishield-api:latest
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PORT` / `AISHIELD_PORT` | 服务监听端口 | `8000` |
| `AISHIELD_LLM_URL` | LLM API 地址（用于智能分析） | - |
| `AISHIELD_LLM_KEY` | LLM API 密钥 | - |

## 验证部署

启动后访问健康检查接口确认服务正常运行：

```
GET /api/v1/health
```

返回 `{"status": "ok"}` 即表示部署成功。