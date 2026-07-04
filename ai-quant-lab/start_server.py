#!/usr/bin/env python3
"""
启动本地Web服务器，用于查看ai-quant-lab的HTML界面
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

def start_server():
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print(f"🚀 服务器已启动！")
        print(f"📍 访问地址: http://localhost:{PORT}/index.html")
        print(f"📁 服务目录: {DIRECTORY}")
        print("=" * 60)
        print("按 Ctrl+C 停止服务器")
        print()
        
        # 自动打开浏览器
        webbrowser.open(f'http://localhost:{PORT}/index.html')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n服务器已停止")

if __name__ == "__main__":
    start_server()
