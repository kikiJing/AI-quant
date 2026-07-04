#!/usr/bin/env python3
"""
测试AI Quant Lab的数据加载
"""

import os
from pathlib import Path

# 项目目录
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

print("=" * 60)
print("AI Quant Lab - 数据文件检查")
print("=" * 60)
print()

# 检查data目录
if not DATA_DIR.exists():
    print(f"❌ 错误: data/ 目录不存在！")
    print(f"   路径: {DATA_DIR}")
    exit(1)

print(f"✅ data/ 目录存在: {DATA_DIR}")
print()

# 列出所有CSV文件
csv_files = list(DATA_DIR.glob("*.csv"))
print(f"找到 {len(csv_files)} 个CSV文件:")
print()

for csv_file in csv_files:
    size = csv_file.stat().st_size
    print(f"  📄 {csv_file.name}")
    print(f"     大小: {size:,} bytes ({size/1024:.1f} KB)")
    
    # 检查文件内容
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
            second_line = f.readline().strip()
        
        print(f"     表头: {first_line[:60]}...")
        print(f"     第一行: {second_line[:60]}...")
        
        # 检查是否有BOM
        with open(csv_file, 'rb') as f:
            bom = f.read(3)
            if bom == b'\xef\xbb\xbf':
                print(f"     ⚠️  文件包含BOM标记（会自动处理）")
        
        print()
    except Exception as e:
        print(f"     ❌ 读取失败: {e}")
        print()

print("=" * 60)
print("建议:")
print("1. 确保通过本地服务器访问HTML文件:")
print("   cd /Users/kikijing/Desktop/AI\\ quant/ai-quant-lab")
print("   python3 -m http.server 8000")
print()
print("2. 在浏览器中访问: http://localhost:8000/index.html")
print()
print("3. 打开浏览器控制台（F12）查看详细日志")
print("=" * 60)
