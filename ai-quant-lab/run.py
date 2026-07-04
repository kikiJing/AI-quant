#!/usr/bin/env python3
"""
AI Quant Lab - 主启动脚本
自动启动本地服务器并在浏览器中打开界面
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# 配置
PORT = 8000
HOST = 'localhost'

def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print("=" * 70)
    print("   AI Quant Lab - 股票技术分析工具")
    print("=" * 70)
    print()
    
    # 检查data目录
    data_dir = script_dir / "data"
    if not data_dir.exists():
        print("❌ 错误: data/ 目录不存在！")
        print(f"   路径: {data_dir}")
        input("按回车键退出...")
        sys.exit(1)
    
    # 检查CSV文件
    csv_files = list(data_dir.glob("*.csv"))
    if len(csv_files) == 0:
        print("⚠️  警告: data/ 目录中没有CSV文件！")
        print("   请先运行 scripts/fetch_stocks.py 获取数据")
    else:
        print(f"✅ 找到 {len(csv_files)} 个CSV数据文件")
    
    print()
    print(f"🚀 正在启动本地服务器...")
    print(f"   地址: http://{HOST}:{PORT}")
    print(f"   目录: {script_dir}")
    print()
    print("=" * 70)
    print()
    print("提示:")
    print("  - 服务器启动后，浏览器会自动打开")
    print("  - 如果浏览器没有自动打开，请手动访问上面的地址")
    print("  - 按 Ctrl+C 停止服务器")
    print()
    print("=" * 70)
    print()
    
    # 创建HTTP服务器
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer((HOST, PORT), handler) as httpd:
            # 在后台打开浏览器
            url = f"http://{HOST}:{PORT}/index.html"
            print(f"🌐 正在打开浏览器: {url}")
            webbrowser.open(url)
            
            print(f"✅ 服务器已启动！访问 {url}")
            print()
            
            # 启动服务器
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n")
        print("=" * 70)
        print("   服务器已停止")
        print("=" * 70)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()
