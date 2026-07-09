#!/bin/bash
# 均线策略回测系统 - 一键启动脚本
# 用法: 双击运行，或在终端执行 ./start.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo ""
echo "=================================================="
echo "  均线策略回测系统 - 启动中..."
echo "=================================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.8+"
    echo "   访问: https://www.python.org/downloads/"
    read -p "按回车键退出..."
    exit 1
fi

PYTHON_CMD="python3"
# 也尝试 python 命令
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

# 杀掉已占用的 8000 端口
echo "🧹 清理端口 8000..."
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null
sleep 1

echo "📡 正在启动本地服务器 (http://localhost:8000) ..."
echo "   数据目录: $SCRIPT_DIR/data/json/"
echo ""

# 启动 HTTP 服务器（后台）
$PYTHON_CMD -m http.server 8000 &
SERVER_PID=$!

sleep 2

# 检查服务器是否启动成功
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ 服务器启动失败，请检查端口 8000 是否被占用"
    read -p "按回车键退出..."
    exit 1
fi

echo "✅ 服务器已启动 (PID: $SERVER_PID)"
echo ""
echo "🌐 正在打开浏览器..."
echo ""

# 打开浏览器
open "http://localhost:8000/ma_backtest_local.html" 2>/dev/null || \
echo "   请手动打开浏览器访问: http://localhost:8000/ma_backtest_local.html"

echo "=================================================="
echo "  服务器运行中...  按 Ctrl+C 停止服务器"
echo "=================================================="
echo ""

# 等待用户 Ctrl+C
wait $SERVER_PID
