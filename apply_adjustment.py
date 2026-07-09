#!/usr/bin/env python3
"""
apply_adjustment.py — 使用已保存的复权因子对数据进行复权处理
用法: python3 apply_adjustment.py
"""

import sys
from pathlib import Path

import pandas as pd

# 股票列表
STOCKS = [
    ("300750.SZ", "ningde_times"),
    ("601318.SH", "ping_an"),
    ("600519.SH", "moutai"),
    ("601857.SH", "petro_china"),
    ("002594.SZ", "byd"),
]

# 目录
DATA_DIR = Path(__file__).parent / "data"
ADJ_DIR = DATA_DIR / "adj_factors"
OUTPUT_DIR = DATA_DIR / "adjusted"


def apply_adjustment(ts_code: str, name: str) -> bool:
    """使用保存的复权因子对数据进行复权处理"""
    code_simple = ts_code.split(".")[0]
    
    # 加载原始数据
    data_file = DATA_DIR / f"{name}_{code_simple}_daily.csv"
    if not data_file.exists():
        print(f"  ⚠️  数据文件不存在：{data_file}")
        return False
    
    # 加载复权因子
    adj_file = ADJ_DIR / f"{name}_{code_simple}_adj_factor.csv"
    if not adj_file.exists():
        print(f"  ⚠️  复权因子文件不存在：{adj_file}")
        print(f"       请先运行 fetch_adj_factors.py 获取复权因子")
        return False
    
    print(f"  ✓ 已加载数据和复权因子")
    
    # 读取数据
    df = pd.read_csv(data_file, encoding="utf-8-sig")
    adj_df = pd.read_csv(adj_file, encoding="utf-8-sig")
    
    # 转换日期
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    adj_df['trade_date'] = pd.to_datetime(adj_df['trade_date'], format='%Y%m%d')
    
    # 合并数据
    merged = pd.merge(df, adj_df[['trade_date', 'adj_factor']], on='trade_date', how='left')
    
    # 检查复权因子
    missing_adj = merged['adj_factor'].isnull().sum()
    if missing_adj > 0:
        print(f"  ⚠️  {missing_adj} 条记录缺少复权因子，将向前填充")
        merged['adj_factor'] = merged['adj_factor'].ffill()
    
    # 前复权处理
    latest_adj_factor = merged['adj_factor'].iloc[-1]
    print(f"  - 最新复权因子：{latest_adj_factor:.4f}")
    print("  - 正在进行前复权处理...")
    
    # 计算前复权价格
    price_cols = ['open', 'high', 'low', 'close', 'pre_close']
    price_cols = [col for col in price_cols if col in merged.columns]
    
    for col in price_cols:
        merged[f'{col}_adj'] = merged[col] * (merged['adj_factor'] / latest_adj_factor)
    
    # 替换原始价格
    for col in price_cols:
        merged[col] = merged[f'{col}_adj']
        merged = merged.drop(columns=[f'{col}_adj'])
    
    # 重新计算涨跌幅
    merged['change'] = merged['close'] - merged['pre_close']
    merged['pct_chg'] = (merged['change'] / merged['pre_close'] * 100).round(2)
    
    # 删除复权因子列
    if 'adj_factor' in merged.columns:
        merged = merged.drop(columns=['adj_factor'])
    
    # 保存
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / f"{name}_{code_simple}_daily_adjusted.csv"
    merged.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"  ✓ 复权数据已保存至：{output_file}")
    
    return True


def main():
    print("="*60)
    print("应用复权处理")
    print("="*60)
    print()
    
    # 检查哪些股票有复权因子
    print("检查复权因子文件...")
    print()
    
    stocks_with_adj = []
    stocks_without_adj = []
    
    for ts_code, name in STOCKS:
        code_simple = ts_code.split(".")[0]
        adj_file = ADJ_DIR / f"{name}_{code_simple}_adj_factor.csv"
        
        if adj_file.exists():
            print(f"  ✓ {name} ({ts_code}) — 有复权因子")
            stocks_with_adj.append((ts_code, name))
        else:
            print(f"  ✗ {name} ({ts_code}) — 缺少复权因子")
            stocks_without_adj.append((ts_code, name))
    
    print()
    
    if not stocks_with_adj:
        print("⚠️  没有找到任何复权因子文件。")
        print(f"请先运行 fetch_adj_factors.py 获取复权因子。")
        print(f"复权因子应保存在：{ADJ_DIR}")
        return
    
    # 处理有复权因子的股票
    print("="*60)
    print(f"开始处理 {len(stocks_with_adj)} 只股票...")
    print("="*60)
    print()
    
    success_count = 0
    for ts_code, name in stocks_with_adj:
        print(f"处理 {name} ({ts_code})...")
        if apply_adjustment(ts_code, name):
            success_count += 1
            print(f"✅ {name} ({ts_code}) 处理完成\n")
        else:
            print(f"❌ {name} ({ts_code}) 处理失败\n")
    
    # 打印汇总
    print("="*60)
    print("汇总")
    print("="*60)
    print(f"成功处理：{success_count}/{len(stocks_with_adj)} 只股票")
    print()
    
    if stocks_without_adj:
        print("以下股票缺少复权因子，请运行 fetch_adj_factors.py 获取：")
        for ts_code, name in stocks_without_adj:
            print(f"  - {name} ({ts_code})")
        print()
    
    print(f"复权后数据保存至：{OUTPUT_DIR}")
    print()


if __name__ == "__main__":
    main()
