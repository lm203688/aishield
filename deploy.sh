#!/bin/bash
# AIShield 一键部署脚本
# 用法: ./deploy.sh

set -e

echo "🚀 AIShield 部署脚本"
echo "===================="

# 检查是否在项目目录
if [ ! -f "api/server.py" ]; then
    echo "❌ 错误: 请在 AIShield 项目根目录运行此脚本"
    exit 1
fi

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 备份数据
echo "💾 备份数据..."
if [ -d "api/data" ]; then
    cp -r api/data api/data.backup.$(date +%Y%m%d_%H%M%S)
fi

# 语法检查
echo "🔍 语法检查..."
python3 -m py_compile api/server.py eco/*.py scanner/*.py

# 运行测试
echo "🧪 运行测试..."
python3 tests/run_all.py

# 停止旧服务
echo "🛑 停止旧服务..."
pkill -f "api/server.py" || true
sleep 2

# 启动新服务
echo "🚀 启动服务..."
export PORT=8450
nohup python3 api/server.py > server.log 2>&1 &

# 等待服务启动
sleep 3

# 健康检查
echo "🏥 健康检查..."
if curl -sf http://localhost:8450/api/v1/health > /dev/null; then
    echo "✅ 服务启动成功!"
    echo ""
    echo "📍 访问地址:"
    echo "   - 首页: http://$(hostname -I | awk '{print $1}'):8420"
    echo "   - API:  http://$(hostname -I | awk '{print $1}'):8420/api/v1/health"
    echo "   - 日志: tail -f server.log"
else
    echo "❌ 服务启动失败，查看日志:"
    tail -n 20 server.log
    exit 1
fi

echo ""
echo "🎉 部署完成!"