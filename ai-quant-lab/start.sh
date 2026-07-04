#!/bin/bash

# 启动脚本 for StockAnalyzer
# 使用方法: ./start.sh

echo "================================================"
echo "   StockAnalyzer Pro - 启动脚本"
echo "================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    echo "请先安装Python3：https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python3已安装"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📂 工作目录: $SCRIPT_DIR"
echo ""

# 检查CSV文件是否存在
if [ ! -f "data/ningde_times_300750_daily.csv" ]; then
    echo "⚠️  警告：未找到CSV数据文件"
    echo "请先运行 fetch_stocks.py 获取数据"
    echo ""
fi

# 启动HTTP服务器
echo "🚀 正在启动HTTP服务器..."
echo "   地址: http://localhost:8000"
echo ""
echo "💡 使用说明："
echo "   1. 服务器启动后，浏览器会自动打开"
echo "   2. 如果没有自动打开，请手动访问: http://localhost:8000"
echo "   3. 按 Ctrl+C 停止服务器"
echo ""
echo "================================================"
echo ""

# 启动服务器（尝试不同端口）
PORT=8000
while true; do
    python3 -m http.server $PORT 2>/dev/null &
    SERVER_PID=$!
    
    # 等待2秒检查服务器是否启动成功
    sleep 2
    
    if kill -0 $SERVER_PID 2>/dev/null; then
        echo "✅ 服务器已启动在端口 $PORT"
        break
    else
        echo "⚠️  端口 $PORT 被占用，尝试端口 $((PORT+1))..."
        PORT=$((PORT+1))
    fi
done

# 等待服务器完全启动
sleep 2

# 自动打开浏览器
echo "🌐 正在打开浏览器..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:$PORT/index.html"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:$PORT/index.html"
else
    # Windows (Git Bash)
    start "http://localhost:$PORT/index.html"
fi

echo ""
echo "✅ 浏览器已打开！"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 等待用户按Ctrl+C
wait $SERVER_PID
