#!/bin/bash

# AI Quant Lab - 快速启动脚本

echo "============================================================"
echo "   AI Quant Lab - 股票技术分析工具"
echo "============================================================"
echo ""

cd "$(dirname "$0")"

echo "🚀 正在启动服务器..."
echo "📍 访问地址: http://localhost:8000/index.html"
echo ""
echo "提示："
echo "  - 服务器启动后，浏览器会自动打开"
echo "  - 按 Ctrl+C 停止服务器"
echo "  - 确保 data/ 目录下有CSV数据文件"
echo ""
echo "============================================================"
echo ""

# 启动Python HTTP服务器
python3 -m http.server 8000 --bind 127.0.0.1 &

# 等待2秒让服务器启动
sleep 2

# 打开浏览器
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:8000/index.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:8000/index.html
else
    # Windows
    start http://localhost:8000/index.html
fi

# 等待服务器进程
wait
